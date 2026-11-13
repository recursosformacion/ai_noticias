"""Captura RSS/Atom y persistencia idempotente en MariaDB."""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
import time
import unicodedata
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, urlunsplit
from urllib.request import Request, urlopen

from .db import transaction
from .feed_parser import parse_feed


USER_AGENT = "ai_noticias/0.1 (+https://github.com/recursosformacion/ai_noticias)"


def _utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _hash(value: str) -> bytes:
    return sha256(value.encode("utf-8", errors="replace")).digest()


def _identity_text(value: str | None) -> str:
    """Normaliza texto para identidad: minúsculas, sin acentos ni puntuación."""
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(char for char in value if not unicodedata.combining(char))
    value = value.casefold()
    value = "".join(char if char.isalnum() else " " for char in value)
    return " ".join(value.split())


def _observation_identity(item: dict) -> str:
    """Huella independiente de URL y GUID: título normalizado + fecha de publicación."""
    title = _identity_text(item.get("title"))
    published = item.get("published_at")
    if isinstance(published, datetime):
        published_key = (published.astimezone(timezone.utc).replace(tzinfo=None) if published.tzinfo else published).isoformat(timespec="seconds")
    else:
        published_key = _identity_text(item.get("published_raw"))
    if not title or not published_key:
        raise ValueError("No se puede crear la huella: la noticia necesita título y fecha de publicación.")
    digest = sha256((title + "|" + published_key).encode("utf-8")).hexdigest()
    return digest


def canonical_url(value: str | None) -> str | None:
    if not value:
        return None
    parts = urlsplit(value.strip())
    if parts.scheme.lower() not in {"http", "https"} or not parts.netloc:
        return value.strip()
    host = parts.netloc.lower()
    path = parts.path or "/"
    # Remove common tracking parameters only; preserve all other query parameters.
    tracking = {"fbclid", "gclid", "mc_cid", "mc_eid"}
    query_parts = []
    for pair in parts.query.split("&") if parts.query else []:
        key = pair.split("=", 1)[0].lower()
        if key.startswith("utm_") or key in tracking:
            continue
        query_parts.append(pair)
    return urlunsplit((parts.scheme.lower(), host, path, "&".join(query_parts), ""))


def _fetch(channel: dict) -> tuple[int, bytes, dict, str]:
    headers = {"User-Agent": USER_AGENT, "Accept": "application/atom+xml, application/rss+xml, application/xml, text/xml;q=0.9, */*;q=0.5"}
    if channel.get("etag"):
        headers["If-None-Match"] = channel["etag"]
    if channel.get("last_modified"):
        headers["If-Modified-Since"] = channel["last_modified"]
    request = Request(channel["url"], headers=headers)
    try:
        with urlopen(request, timeout=25) as response:
            return response.status, response.read(8 * 1024 * 1024 + 1), dict(response.headers.items()), response.geturl()
    except HTTPError as exc:
        if exc.code == 304:
            return 304, b"", dict(exc.headers.items()), exc.geturl()
        raise
    except URLError as exc:
        raise RuntimeError(f"Error de conexión: {exc.reason}") from exc


def _get_or_create_publication(cursor, channel, item, now, existing_publication_id=None):
    canonical = canonical_url(item["url"])
    url_hash = _hash(canonical) if canonical else None
    publication = None
    # Reuse the publication already linked to this source observation, including
    # Atom entries that expose an ID but no URL.
    if existing_publication_id:
        cursor.execute(
            "SELECT id, news_item_id FROM news_publications WHERE id=%s FOR UPDATE",
            (existing_publication_id,),
        )
        publication = cursor.fetchone()
    if publication is None and url_hash:
        # A URL can be a shared search/results page. Only reuse a publication
        # when both its canonical URL and title match (conservative deduplication).
        cursor.execute(
            """SELECT id, news_item_id FROM news_publications
            WHERE url_sha256=%s AND title_original=%s ORDER BY id LIMIT 1 FOR UPDATE""",
            (url_hash, item["title"]),
        )
        publication = cursor.fetchone()

    if publication:
        pub_id = publication["id"]
        news_id = publication["news_item_id"]
        cursor.execute(
            """UPDATE news_publications SET last_seen_at=%s, title_original=%s,
            description_original=COALESCE(%s,description_original),
            author_original=COALESCE(%s,author_original),
            canonical_url=COALESCE(%s,canonical_url),
            original_url=COALESCE(%s,original_url),
            url_sha256=COALESCE(%s,url_sha256),
            published_at=COALESCE(%s,published_at),
            updated_at=COALESCE(%s,updated_at),
            published_at_raw=COALESCE(%s,published_at_raw),
            updated_at_raw=COALESCE(%s,updated_at_raw),
            language_declared=COALESCE(%s,language_declared)
            WHERE id=%s""",
            (now, item["title"], item["description"], item["author"], canonical,
             item["url"], url_hash, item["published_at"], item["updated_at"],
             item["published_raw"], item["updated_raw"], item["language"], pub_id),
        )
        if news_id is None:
            cursor.execute(
                "INSERT INTO news_items (status, first_detected_at, last_detected_at) VALUES ('ACTIVE',%s,%s)",
                (now, now),
            )
            news_id = cursor.lastrowid
            cursor.execute("UPDATE news_publications SET news_item_id=%s WHERE id=%s", (news_id, pub_id))
        cursor.execute(
            "UPDATE news_items SET primary_publication_id=COALESCE(primary_publication_id,%s) WHERE id=%s",
            (pub_id, news_id),
        )
        return pub_id, news_id

    cursor.execute(
        "INSERT INTO news_items (status, first_detected_at, last_detected_at) VALUES ('ACTIVE',%s,%s)",
        (now, now),
    )
    news_id = cursor.lastrowid
    cursor.execute(
        """INSERT INTO news_publications
        (publisher_id, news_item_id, external_id, canonical_url, original_url, url_sha256,
         title_original, description_original, author_original, published_at, updated_at,
         published_at_raw, updated_at_raw, language_declared, first_seen_at, last_seen_at)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        (
            channel["publisher_id"], news_id, item["external_id"], canonical, item["url"],
            url_hash, item["title"], item["description"], item["author"],
            item["published_at"], item["updated_at"], item["published_raw"],
            item["updated_raw"], item["language"], now, now,
        ),
    )
    pub_id = cursor.lastrowid
    cursor.execute("UPDATE news_items SET primary_publication_id=%s WHERE id=%s", (pub_id, news_id))
    return pub_id, news_id


def _persist_item(cursor, channel, run_id, item, now):
    if item["url"] and len(item["url"]) > 2048:
        raise ValueError("La URL del elemento supera los 2048 caracteres admitidos.")
    if item["external_id"] and len(item["external_id"]) > 1000:
        raise ValueError("El identificador externo supera los 1000 caracteres admitidos.")
    identity_digest = _observation_identity(item)
    external_id = "fingerprint:v2:" + identity_digest
    external_hash = bytes.fromhex(identity_digest)
    content_hash = _hash(json.dumps(
        {k: item.get(k).isoformat() if isinstance(item.get(k), datetime) else item.get(k)
         for k in ("title", "url", "description", "author", "published_raw", "updated_raw", "language")},
        ensure_ascii=False, sort_keys=True,
    ))
    cursor.execute(
        """SELECT id, content_hash, news_publication_id FROM source_observations
        WHERE source_channel_id=%s AND external_id_hash=%s FOR UPDATE""",
        (channel["id"], external_hash),
    )
    observation = cursor.fetchone()

    # Upgrade an existing observation created by the old URL-based fallback.
    # Match its current title/date before changing its unique identity hash;
    # this preserves its row, publication link and accumulated revision history.
    if observation is None and not item.get("external_id"):
        cursor.execute(
            """SELECT id, content_hash, news_publication_id
            FROM source_observations
            WHERE source_channel_id=%s AND title_original=%s
              AND published_at_raw <=> %s
            ORDER BY id LIMIT 1 FOR UPDATE""",
            (channel["id"], item["title"], item.get("published_raw")),
        )
        legacy = cursor.fetchone()
        if legacy:
            cursor.execute(
                """UPDATE source_observations
                SET external_id=%s, external_id_hash=%s
                WHERE id=%s""",
                (external_id, external_hash, legacy["id"]),
            )
            observation = legacy

    existing_pub_id = observation["news_publication_id"] if observation else None
    pub_id, news_id = _get_or_create_publication(
        cursor, channel, item, now, existing_publication_id=existing_pub_id
    )

    if observation:
        obs_id = observation["id"]
        if observation["content_hash"] != content_hash:
            cursor.execute(
                "SELECT COALESCE(MAX(revision_number),0)+1 AS next_revision "
                "FROM observation_revisions WHERE source_observation_id=%s",
                (obs_id,),
            )
            revision = cursor.fetchone()["next_revision"]
            cursor.execute(
                """INSERT INTO observation_revisions
                (source_observation_id, revision_number, observed_at, content_hash,
                 title_original, description_original, url_original, published_at_raw,
                 updated_at_raw, metadata)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (obs_id, revision, now, content_hash, item["title"], item["description"],
                 item["url"], item["published_raw"], item["updated_raw"],
                 json.dumps({"author": item["author"], "language": item["language"]}, ensure_ascii=False)),
            )
            cursor.execute(
                """UPDATE source_observations SET fetch_run_id=%s, external_id=%s,
                url_original=%s, title_original=%s, description_original=%s,
                author_original=%s, published_at_raw=%s, published_at=%s,
                updated_at_raw=%s, updated_at=%s, declared_language=%s,
                payload_metadata=%s, content_hash=%s, last_seen_at=%s,
                news_publication_id=%s, processing_status='CAPTURED' WHERE id=%s""",
                (run_id, external_id, item["url"], item["title"], item["description"],
                 item["author"], item["published_raw"], item["published_at"],
                 item["updated_raw"], item["updated_at"], item["language"],
                 json.dumps({"canonical_url": canonical_url(item["url"])}, ensure_ascii=False),
                 content_hash, now, pub_id, obs_id),
            )
            cursor.execute("UPDATE news_items SET last_detected_at=%s WHERE id=%s", (now, news_id))
            return "updated"
        cursor.execute(
            "UPDATE source_observations SET fetch_run_id=%s, last_seen_at=%s, "
            "news_publication_id=%s WHERE id=%s",
            (run_id, now, pub_id, obs_id),
        )
        cursor.execute("UPDATE news_items SET last_detected_at=%s WHERE id=%s", (now, news_id))
        return "known"

    cursor.execute(
        """INSERT INTO source_observations
        (source_channel_id, fetch_run_id, external_id, external_id_hash, url_original,
         title_original, description_original, author_original, published_at_raw,
         published_at, updated_at_raw, updated_at, declared_language, payload_metadata,
         content_hash, first_seen_at, last_seen_at, news_publication_id, processing_status)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'CAPTURED')""",
        (channel["id"], run_id, external_id, external_hash, item["url"],
         item["title"], item["description"], item["author"], item["published_raw"],
         item["published_at"], item["updated_raw"], item["updated_at"], item["language"],
         json.dumps({"canonical_url": canonical_url(item["url"])}, ensure_ascii=False),
         content_hash, now, now, pub_id),
    )
    cursor.execute("UPDATE news_items SET last_detected_at=%s WHERE id=%s", (now, news_id))
    return "new"


def ingest_channel(connection, channel: dict) -> dict:
    started = _utcnow()
    with connection.cursor() as cursor:
        cursor.execute(
            """INSERT INTO fetch_runs
            (source_channel_id, started_at, requested_url, result_status)
            VALUES (%s,%s,%s,'RUNNING')""",
            (channel["id"], started, channel["url"]),
        )
        run_id = cursor.lastrowid
    connection.commit()

    counts = {"received": 0, "new": 0, "known": 0, "updated": 0, "error": 0}
    item_errors = []
    status = "SUCCESS"
    http_status = None
    final_url = channel["url"]
    headers = {}
    started_clock = time.monotonic()
    try:
        http_status, body, headers, final_url = _fetch(channel)
        if http_status == 304:
            pass
        else:
            if len(body) > 8 * 1024 * 1024:
                raise RuntimeError("El feed supera el límite de 8 MiB.")
            _, items = parse_feed(body, base_url=final_url)
            counts["received"] = len(items)
            for item in items:
                try:
                    with connection.cursor() as cursor:
                        with transaction(connection):
                            result = _persist_item(cursor, channel, run_id, item, _utcnow())
                    counts[result] += 1
                except Exception as item_exc:
                    connection.rollback()
                    counts["error"] += 1
                    if len(item_errors) < 10:
                        item_errors.append(str(item_exc)[:500])
            if counts["error"]:
                status = "PARTIAL" if counts["new"] + counts["known"] + counts["updated"] else "FAILED"
    except Exception as exc:
        status = "FAILED"
        error_message = str(exc)[:6000]
    else:
        error_message = "; ".join(item_errors)[:6000] if item_errors else None

    finished = _utcnow()
    etag = headers.get("ETag") or headers.get("Etag")
    last_modified = headers.get("Last-Modified")
    with connection.cursor() as cursor:
        cursor.execute(
            """UPDATE fetch_runs SET finished_at=%s, final_url=%s, http_status=%s,
            result_status=%s, items_received=%s, items_new=%s, items_known=%s,
            items_error=%s, duration_ms=%s, error_code=%s, error_message=%s WHERE id=%s""",
            (finished, final_url, http_status, status, counts["received"],
             counts["new"], counts["known"] + counts["updated"], counts["error"],
             int((time.monotonic() - started_clock) * 1000),
             "ITEM_ERRORS" if item_errors else ("FETCH_ERROR" if status == "FAILED" else None),
             error_message, run_id),
        )
        cursor.execute(
            """UPDATE source_channels SET last_checked_at=%s,
            etag=COALESCE(%s,etag), last_modified=COALESCE(%s,last_modified)
            WHERE id=%s""",
            (finished, etag, last_modified, channel["id"]),
        )
    connection.commit()
    return {"run_id": run_id, "status": status, **counts, "http_status": http_status}



# Only these two channels have a sufficiently clear reuse basis for a metadata-only
# technical probe. The probe never writes feed entries to the database.
PROBE_CANDIDATES = {
    "https://blogs.loc.gov/music/feed/": "loc.gov",
    "https://bibliographienationale.bnf.fr/rss/mus": "bnf.fr",
}


def probe_candidate_channels(connection, source_id: int | None = None) -> list[dict]:
    with connection.cursor() as cursor:
        sql = """SELECT s.id, s.publisher_id, s.provider_name, s.name, s.url,
                        p.domain
                 FROM source_channels s
                 JOIN publishers p ON p.id=s.publisher_id
                 WHERE s.url IN (%s, %s)"""
        params = tuple(PROBE_CANDIDATES)
        if source_id is not None:
            sql += " AND s.id=%s"
            params += (source_id,)
        sql += " ORDER BY s.id"
        cursor.execute(sql, params)
        channels = cursor.fetchall()

    results = []
    for channel in channels:
        expected_domain = PROBE_CANDIDATES.get(channel["url"])
        if not expected_domain or channel["domain"] != expected_domain:
            results.append({"source_id": channel["id"], "name": channel["name"],
                            "status": "BLOCKED", "reason": "Canal fuera de la lista permitida."})
            continue
        try:
            status, body, headers, final_url = _fetch(channel)
            if status == 304:
                raise RuntimeError("Respuesta 304 inesperada en una prueba sin validadores.")
            if len(body) > 8 * 1024 * 1024:
                raise RuntimeError("El feed supera el límite de 8 MiB.")
            final_host = (urlsplit(final_url).hostname or "").lower()
            if final_host != expected_domain and not final_host.endswith("." + expected_domain):
                raise RuntimeError("La redirección sale del dominio autorizado.")
            metadata, items = parse_feed(body, base_url=final_url)
            results.append({
                "source_id": channel["id"],
                "name": channel["name"],
                "status": "OK",
                "http_status": status,
                "feed_title_present": bool(metadata.get("title")),
                "items": len(items),
                "items_with_url": sum(bool(x.get("url")) for x in items),
                "items_with_author": sum(bool(x.get("author")) for x in items),
                "items_with_date": sum(bool(x.get("published_raw") or x.get("updated_raw")) for x in items),
                "items_with_identifier": sum(bool(x.get("external_id")) for x in items),
                "final_domain": urlsplit(final_url).hostname,
                "etag_present": bool(headers.get("ETag") or headers.get("Etag")),
                "last_modified_present": bool(headers.get("Last-Modified")),
                "persisted": False,
            })
        except Exception as exc:
            results.append({"source_id": channel["id"], "name": channel["name"],
                            "status": "ERROR", "reason": str(exc)[:500], "persisted": False})
    return results

def ingest_active_channels(connection, source_id: int | None = None) -> list[dict]:
    with connection.cursor() as cursor:
        sql = """SELECT id, publisher_id, provider_name, name, url, etag, last_modified,
                        default_content_type_id
                 FROM source_channels WHERE status='ACTIVE'"""
        params = ()
        if source_id is not None:
            sql += " AND id=%s"
            params = (source_id,)
        sql += " ORDER BY id"
        cursor.execute(sql, params)
        channels = cursor.fetchall()

    results = []
    for channel in channels:
        results.append({"source_id": channel["id"], "name": channel["name"], **ingest_channel(connection, channel)})
    return results
