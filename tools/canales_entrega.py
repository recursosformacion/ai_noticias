"""Distribución de noticias por canal y modo de entrega."""
from __future__ import annotations

import sys

from app.db import connect


def main() -> int:
    connection = connect()
    try:
        with connection.cursor() as cur:
            cur.execute(
                """SELECT s.id, s.name, s.status, s.delivery_mode, s.declared_language l,
                COUNT(DISTINCT o.news_publication_id) n
                FROM source_channels s
                LEFT JOIN source_observations o ON o.source_channel_id = s.id
                GROUP BY s.id, s.name, s.status, s.delivery_mode, s.declared_language
                ORDER BY n DESC, s.id"""
            )
            print(f"{'id':>3} {'estado':8} {'entrega':7} {'idi':3} {'n':>5}  canal")
            for r in cur.fetchall():
                print(f"{r['id']:>3} {r['status']:8} {r['delivery_mode']:7} "
                      f"{r['l'] or '':3} {r['n']:>5}  {r['name']}")
        return 0
    finally:
        connection.close()


if __name__ == "__main__":
    sys.exit(main())
