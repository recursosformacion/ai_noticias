"""Captura RSS/Atom y persistencia idempotente en MariaDB."""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
import time
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
        cursor.execute(
            "SELECT id, news_item_id FROM news_publications WHERE url_sha256=%s ORDER BY id LIMIT 1 FOR UPDATE",
            (url_hash,),
        )
        publication = cursor.fetchone()

    if publication:
        pub_id = publication["id"]
        news_id = publication["news_item_id"]
        cursor.execute(
            "UPDATE news_publications SET last_seen_at=%s, "
            "title_original=IF(title_original='',%s,title_original), "
            "description_original=COALESCE(description_original,%s) WHERE id=%s",
            (now, item["title"], item["description"], pub_id),
        )
        if news_id is None:
            cursor.execute(
                "INSERT INTO news_items (status, first_detected_at, last_detected_at) VALUES ('ACTIVE',%s,%s)",
                (now, now),
            )
            news_id = cursor.lastrowid
            cursor.execute("UPDATE news_publications SET news_item_id=%s WHERE id=%s", (news_id, pub_id))
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
    return cursor.lastrowid, news_id


def _persist_item(cursor, channel, run_id, item, now):
    external_id = item["external_id"] or item["url"] or (
        item["title"] + "|" + (item["published_raw"] or "")
    )
    external_hash = _hash(external_id)
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
                (run_id, item["external_id"], item["url"], item["title"], item["description"],
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
        (channel["id"], run_id, item["external_id"], external_hash, item["url"],
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
            _, items = parse_feed(body)
            counts["received"] = len(items)
            for item in items:
                try:
                    with connection.cursor() as cursor:
                        with transaction(connection):
                            result = _persist_item(cursor, channel, run_id, item, _utcnow())
                    counts[result] += 1
                except Exception:
                    connection.rollback()
                    counts["error"] += 1
            if counts["error"]:
                status = "PARTIAL" if counts["new"] + counts["known"] + counts["updated"] else "FAILED"
    except Exception as exc:
        status = "FAILED"
        error_message = str(exc)[:6000]
    else:
        error_message = None

    finished = _utcnow()
    etag = headers.get("ETag") or headers.get("Etag")
    last_modified = headers.get("Last-Modified")
    with connection.cursor() as cursor:
        cursor.execute(
            """UPDATE fetch_runs SET finished_at=%s, final_url=%s, http_status=%s,
            result_status=%s, items_received=%s, items_new=%s, items_known=%s,
            items_error=%s, duration_ms=%s, error_message=%s WHERE id=%s""",
            (finished, final_url, http_status, status, counts["received"],
             counts["new"] + counts["updated"], counts["known"], counts["error"],
             int((time.monotonic() - started_clock) * 1000), error_message, run_id),
        )
        cursor.execute(
            """UPDATE source_channels SET last_checked_at=%s,
            etag=COALESCE(%s,etag), last_modified=COALESCE(%s,last_modified)
            WHERE id=%s""",
            (finished, etag, last_modified, channel["id"]),
        )
    connection.commit()
    return {"run_id": run_id, "status": status, **counts, "http_status": http_status}


def ingest_active_channels(connection, source_id: int | None = None) -> list[dict]:
    with connection.cursor() as cursor:
        sql = """SELECT id, publisher_id, provider_name, name, url, etag, last_modified
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
