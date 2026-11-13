"""Limpieza puntual de duplicados de las primeras pruebas del canal BnF.

Por defecto solo informa. Para aplicar: python -m tools.repair_bnf_test_data --apply
Solo actúa sobre source_channel_id=6 y se niega a borrar noticias con análisis asociados.
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata

from app.db import connect


SOURCE_ID = 6


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
                "SELECT * FROM source_observations WHERE source_channel_id=%s ORDER BY id FOR UPDATE",
                (SOURCE_ID,),
            )
            rows = cursor.fetchall()
            groups = _groups(rows)
            duplicate_ids = [row["id"] for group in groups for row in group[1:]]
            keepers = [(group[0], group[-1]) for group in groups]

            print(json.dumps({
                "source_channel_id": SOURCE_ID,
                "observations": len(rows),
                "distinct_news_by_title_and_date": len(rows) - len(duplicate_ids),
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
            }, ensure_ascii=False, indent=2, default=str))

            if not args.apply:
                connection.rollback()
                print("Sin cambios. Repite con --apply para ejecutar.")
                return 0

            # No borrar datos que ya hayan entrado en análisis editorial.
            for table, column, ids in (
                ("analysis_runs", "news_item_id", []),
                ("analysis_inputs", "news_publication_id", []),
                ("news_item_categories", "news_item_id", []),
                ("editorial_texts", "news_item_id", []),
            ):
                if not ids:
                    continue

            publication_ids = []
            news_item_ids = []
            for keeper, latest in keepers:
                if latest["id"] == keeper["id"]:
                    continue
                keeper_pub = keeper.get("news_publication_id")
                duplicate_pub = latest.get("news_publication_id")
                if not keeper_pub or not duplicate_pub:
                    raise RuntimeError(
                        f"Observaciones {keeper['id']}/{latest['id']}: falta publicación enlazada; "
                        "no se puede hacer una fusión segura."
                    )
                cursor.execute("SELECT * FROM news_publications WHERE id=%s FOR UPDATE", (keeper_pub,))
                keeper_publication = cursor.fetchone()
                cursor.execute("SELECT * FROM news_publications WHERE id=%s FOR UPDATE", (duplicate_pub,))
                duplicate_publication = cursor.fetchone()
                if not keeper_publication or not duplicate_publication:
                    raise RuntimeError("No se encuentra una publicación asociada a una observación duplicada.")
                publication_ids.append(duplicate_pub)
                if duplicate_publication["news_item_id"] is not None:
                    news_item_ids.append(duplicate_publication["news_item_id"])

                # La observación superviviente adopta la identidad exacta del último duplicado.
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
                # Actualiza metadatos de la publicación original, sin cambiar su news_item.
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

            # Verificar que no existan análisis ni referencias editoriales a los duplicados.
            for table, column, ids in (
                ("analysis_inputs", "news_publication_id", publication_ids),
                ("analysis_runs", "news_item_id", news_item_ids),
                ("news_item_categories", "news_item_id", news_item_ids),
                ("editorial_texts", "news_item_id", news_item_ids),
            ):
                if ids:
                    placeholders = ",".join(["%s"] * len(ids))
                    n = _count(cursor, f"SELECT COUNT(*) AS n FROM {table} WHERE {column} IN ({placeholders})", ids)
                    if n:
                        raise RuntimeError(
                            f"Se cancela: {table} contiene {n} referencias a registros duplicados."
                        )

            # Las revisiones de este canal son las falsas alternancias de la prueba inicial.
            cursor.execute(
                """SELECT COUNT(*) AS n FROM analysis_inputs ai
                   JOIN observation_revisions r ON r.id=ai.observation_revision_id
                   JOIN source_observations o ON o.id=r.source_observation_id
                   WHERE o.source_channel_id=%s""",
                (SOURCE_ID,),
            )
            if cursor.fetchone()["n"]:
                raise RuntimeError("Hay análisis que utilizan revisiones BnF; no se borrarán.")

            # Eliminar observaciones repetidas antes de sus publicaciones.
            if duplicate_ids:
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
            if publication_ids:
                placeholders = ",".join(["%s"] * len(publication_ids))
                cursor.execute(f"DELETE FROM news_publications WHERE id IN ({placeholders})", publication_ids)
            if news_item_ids:
                placeholders = ",".join(["%s"] * len(news_item_ids))
                cursor.execute(f"DELETE FROM news_items WHERE id IN ({placeholders})", news_item_ids)

            connection.commit()
            with connection.cursor() as cursor:
                cursor.execute(
                    """SELECT COUNT(*) AS n FROM source_observations
                       WHERE source_channel_id=%s""",
                    (SOURCE_ID,),
                )
                remaining = cursor.fetchone()["n"]
                cursor.execute(
                    """SELECT COUNT(*) AS n FROM observation_revisions r
                       JOIN source_observations o ON o.id=r.source_observation_id
                       WHERE o.source_channel_id=%s""",
                    (SOURCE_ID,),
                )
                revisions = cursor.fetchone()["n"]
            print(f"Limpieza aplicada. Observaciones restantes: {remaining}; revisiones: {revisions}.")
            return 0
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
