"""Rango de fechas por canal activo: sirve para ajustar la ventana de las consultas."""
from __future__ import annotations

import sys

from app.db import connect


def main() -> int:
    connection = connect()
    try:
        with connection.cursor() as cur:
            cur.execute(
                """SELECT s.name, s.delivery_mode m,
                DATE(MIN(COALESCE(p.published_at, p.first_seen_at))) d_min,
                DATE(MAX(COALESCE(p.published_at, p.first_seen_at))) d_max,
                COUNT(*) n
                FROM source_observations o
                JOIN news_publications p ON p.id = o.news_publication_id
                JOIN source_channels s ON s.id = o.source_channel_id
                WHERE s.status = 'ACTIVE'
                GROUP BY s.name, s.delivery_mode
                ORDER BY d_max DESC"""
            )
            print(f"{'desde':10} {'hasta':10} {'n':>5} {'modo':7} canal")
            for r in cur.fetchall():
                print(f"{str(r['d_min']):10} {str(r['d_max']):10} {r['n']:>5} "
                      f"{r['m']:7} {r['name']}")
        return 0
    finally:
        connection.close()


if __name__ == "__main__":
    sys.exit(main())
