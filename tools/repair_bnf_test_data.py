"""Limpieza puntual de duplicados de las primeras pruebas del canal BnF.

Por defecto solo informa. Para aplicar: python -m tools.repair_bnf_test_data --apply
Solo actúa sobre el canal BnF de pruebas (ID 6), valida el estado esperado y
se niega a borrar noticias que ya tengan análisis o referencias editoriales.
"""
from __future__ import annotations

import argparse
import json
import unicodedata

from app.db import connect


SOURCE_ID = 6
SOURCE_URL = "https://bibliographienationale.bnf.fr/rss/mus"


def _key(row: dict) -> tuple[str, str]:
    title = unicodedata.normalize("NFKC", row.get("title_original") or "")
    title = " ".join(title.split()).casefold()
    published = " ".join((row.get("published_at_raw") or "").split()).casefold()
    return title, published


def _groups(rows: list[dict]) -> list[list[dict]]:
    grouped: dict[tuple[str, str], list[dict]] = {}
    for row in rows:
        grouped.setdefault(_key(row), []).append(row)
    return [sorted(group, key=lambda x: x["id"]) for group in grouped.values() if len(group) > 1]


def _count(cursor, sql: str, params=()) -> int:
    cursor.execute(sql, params)
    return int(cursor.fetchone()["n"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Aplicar la limpieza dentro de una transacción.")
    args = parser.parse_args()

    connection = connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, url FROM source_channels WHERE id=%s FOR UPDATE",
                (SOURCE_ID,),
            )
            channel = cursor.fetchone()
            if not channel or channel["url"] != SOURCE_URL:
                raise RuntimeError("El canal 6 no coincide con el RSS BnF esperado. No se modifica nada.")

            cursor.execute(
                "SELECT * FROM source_observations WHERE source_channel_id=%s ORDER BY id FOR UPDATE",
                (SOURCE_ID,),
            )
            rows = cursor.fetchall()
            groups = _groups(rows)
            duplicate_ids = [row["id"] for group in groups for row in group[1:]]
            keepers = [(group[0], group[-1]) for group in groups]
            distinct_count = len(rows) - len(duplicate_ids)

            report = {
                "source_channel_id": SOURCE_ID,
                "observations": len(rows),
                "distinct_news_by_title_and_date": distinct_count,
                "duplicate_observation_ids": duplicate_ids,
                "duplicate_groups": [
                    {"keep": group[0]["id"], "remove": [r["id"] for r in group[1:]],
                     "title": group[0]["title_original"],
                     "published_at_raw": group[0]["published_at_raw"]}
                    for group in groups
                ],
                "false_revision_count": _count(
                    cursor,
                    """SELECT COUNT(*) AS n FROM observation_revisions r
                       JOIN source_observations o ON o.id=r.source_observation_id
                       WHERE o.source_channel_id=%s""",
                    (SOURCE_ID,),
                ),
                "mode": "APPLY" if args.apply else "DRY RUN",
            }
            print(json.dumps(report, ensure_ascii=False, indent=2, default=str))

            if not args.apply:
                connection.rollback()
                print("Sin cambios. Repite con --apply para ejecutar.")
                return 0

            # Esta limpieza es deliberadamente específica para el estado observado.
            # Si hay nuevos datos o grupos ambiguos, se detiene para revisión.
            if len(rows) != 12 or distinct_count != 7 or len(groups) != 5:
                raise RuntimeError(
                    "El estado ya no coincide con las primeras pruebas (esperadas: "
                    "12 observaciones, 7 noticias y 5 duplicados). No se modifica nada."
                )
            if any(len(group) != 2 for group in groups):
                raise RuntimeError("Hay grupos con más de dos filas; se requiere revisión manual.")

            publication_ids = []
            news_item_ids = []
            for keeper, latest in keepers:
                keeper_pub = keeper.get("news_publication_id")
                duplicate_pub = latest.get("news_publication_id")
                if not keeper_pub or not duplicate_pub:
                    raise RuntimeError(
                        f"Observaciones {keeper['id']}/{latest['id']}: falta publicación enlazada."
                    )
                cursor.execute("SELECT * FROM news_publications WHERE id=%s FOR UPDATE", (keeper_pub,))
                if not cursor.fetchone():
                    raise RuntimeError(f"No existe la publicación {keeper_pub} de la observación superviviente.")
                cursor.execute("SELECT * FROM news_publications WHERE id=%s FOR UPDATE", (duplicate_pub,))
                duplicate_publication = cursor.fetchone()
                if not duplicate_publication:
                    raise RuntimeError(f"No existe la publicación duplicada {duplicate_pub}.")
                publication_ids.append(duplicate_pub)
                if duplicate_publication["news_item_id"] is not None:
                    news_item_ids.append(duplicate_publication["news_item_id"])

                # La observación superviviente adopta la identidad exacta de la fila duplicada más reciente.
                cursor.execute(
                    """UPDATE source_observations SET fetch_run_id=%s, external_id=%s,
                       external_id_hash=%s, url_original=%s, title_original=%s,
                       description_original=%s, author_original=%s, published_at_raw=%s,
                       published_at=%s, updated_at_raw=%s, updated_at=%s,
                       declared_language=%s, payload_metadata=%s, content_hash=%s,
                       last_seen_at=%s, processing_status=%s
                       WHERE id=%s""",
                    (latest["fetch_run_id"], latest["external_id"], latest["external_id_hash"],
                     latest["url_original"], latest["title_original"], latest["description_original"],
                     latest["author_original"], latest["published_at_raw"], latest["published_at"],
                     latest["updated_at_raw"], latest["updated_at"], latest["declared_language"],
                     latest["payload_metadata"], latest["content_hash"], latest["last_seen_at"],
                     latest["processing_status"], keeper["id"]),
                )
                # Conserva la publicación/noticia original y actualiza sus datos de fuente.
                cursor.execute(
                    """UPDATE news_publications SET external_id=%s, canonical_url=%s,
                       original_url=%s, url_sha256=%s, title_original=%s,
                       description_original=%s, author_original=%s, published_at=%s,
                       updated_at=%s, published_at_raw=%s, updated_at_raw=%s,
                       language_declared=%s, last_seen_at=%s
                       WHERE id=%s""",
                    (duplicate_publication["external_id"], duplicate_publication["canonical_url"],
                     duplicate_publication["original_url"], duplicate_publication["url_sha256"],
                     duplicate_publication["title_original"], duplicate_publication["description_original"],
                     duplicate_publication["author_original"], duplicate_publication["published_at"],
                     duplicate_publication["updated_at"], duplicate_publication["published_at_raw"],
                     duplicate_publication["updated_at_raw"], duplicate_publication["language_declared"],
                     duplicate_publication["last_seen_at"], keeper_pub),
                )

            # No eliminar publicaciones/noticias si ya se usan en análisis o textos editoriales.
            checks = (
                ("analysis_inputs", "news_publication_id", publication_ids),
                ("analysis_runs", "news_item_id", news_item_ids),
                ("news_item_categories", "news_item_id", news_item_ids),
                ("editorial_texts", "news_item_id", news_item_ids),
            )
            for table, column, ids in checks:
                if ids:
                    placeholders = ",".join(["%s"] * len(ids))
                    n = _count(cursor, f"SELECT COUNT(*) AS n FROM {table} WHERE {column} IN ({placeholders})", ids)
                    if n:
                        raise RuntimeError(f"Se cancela: {table} contiene {n} referencias a duplicados.")

            # Cada noticia duplicada debe estar enlazada solo a su publicación duplicada.
            if news_item_ids:
                placeholders = ",".join(["%s"] * len(news_item_ids))
                n = _count(
                    cursor,
                    f"""SELECT COUNT(*) AS n FROM news_publications
                        WHERE news_item_id IN ({placeholders})
                          AND id NOT IN ({",".join(["%s"] * len(publication_ids))})""",
                    (*news_item_ids, *publication_ids),
                )
                if n:
                    raise RuntimeError("Una noticia duplicada tiene otras publicaciones asociadas; no se borra.")

            # Las revisiones BnF son las alternancias falsas de estas primeras pruebas.
            n = _count(
                cursor,
                """SELECT COUNT(*) AS n FROM analysis_inputs ai
                   JOIN observation_revisions r ON r.id=ai.observation_revision_id
                   JOIN source_observations o ON o.id=r.source_observation_id
                   WHERE o.source_channel_id=%s""",
                (SOURCE_ID,),
            )
            if n:
                raise RuntimeError("Hay análisis que utilizan revisiones BnF; no se borrarán.")

            placeholders = ",".join(["%s"] * len(duplicate_ids))
            cursor.execute(
                f"DELETE FROM source_observations WHERE id IN ({placeholders}) AND source_channel_id=%s",
                (*duplicate_ids, SOURCE_ID),
            )
            cursor.execute(
                """DELETE r FROM observation_revisions r
                   JOIN source_observations o ON o.id=r.source_observation_id
                   WHERE o.source_channel_id=%s""",
                (SOURCE_ID,),
            )
            placeholders = ",".join(["%s"] * len(publication_ids))
            cursor.execute(f"DELETE FROM news_publications WHERE id IN ({placeholders})", publication_ids)
            if news_item_ids:
                placeholders = ",".join(["%s"] * len(news_item_ids))
                cursor.execute(f"DELETE FROM news_items WHERE id IN ({placeholders})", news_item_ids)

            connection.commit()
            with connection.cursor() as cursor:
                remaining = _count(
                    cursor, "SELECT COUNT(*) AS n FROM source_observations WHERE source_channel_id=%s",
                    (SOURCE_ID,),
                )
                revisions = _count(
                    cursor,
                    """SELECT COUNT(*) AS n FROM observation_revisions r
                       JOIN source_observations o ON o.id=r.source_observation_id
                       WHERE o.source_channel_id=%s""",
                    (SOURCE_ID,),
                )
            print(f"Limpieza aplicada. Observaciones restantes: {remaining}; revisiones: {revisions}.")
            return 0
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
