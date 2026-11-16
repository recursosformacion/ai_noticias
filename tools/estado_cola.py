"""Estado de la cola de salida y de la cobertura por idioma del corpus."""
from __future__ import annotations

import sys

from app.db import connect


def main() -> int:
    connection = connect()
    try:
        with connection.cursor() as cur:
            print("== Cola de salida (outbound_messages) ==")
            cur.execute(
                """SELECT id, recipient, subject, kind, status, language_code,
                items_count, CHAR_LENGTH(body_text) body_len, created_at
                FROM outbound_messages ORDER BY id DESC LIMIT 5"""
            )
            rows = cur.fetchall()
            if not rows:
                print("  (vacía)")
            for r in rows:
                print(f"  #{r['id']} {r['status']:8} {r['kind']:12} "
                      f"{r['language_code'] or '-':2} items={r['items_count']} "
                      f"len={r['body_len']} -> {r['recipient']}")
                print(f"      {r['subject']}")

            print("\n== Noticias por idioma (solo canales DAILY) ==")
            cur.execute(
                """SELECT COALESCE(p.language_detected, s.declared_language) lang,
                COUNT(*) n
                FROM news_publications p
                JOIN source_observations o ON o.news_publication_id = p.id
                JOIN source_channels s ON s.id = o.source_channel_id
                WHERE s.status='ACTIVE' AND s.delivery_mode='DAILY'
                GROUP BY lang ORDER BY n DESC"""
            )
            for r in cur.fetchall():
                print(f"  {r['lang'] or 'sin idioma':12} {r['n']}")

            print("\n== Noticias por canal DAILY ==")
            cur.execute(
                """SELECT s.name, COUNT(*) n
                FROM news_publications p
                JOIN source_observations o ON o.news_publication_id = p.id
                JOIN source_channels s ON s.id = o.source_channel_id
                WHERE s.status='ACTIVE' AND s.delivery_mode='DAILY'
                GROUP BY s.name ORDER BY n DESC"""
            )
            for r in cur.fetchall():
                print(f"  {r['n']:>4}  {r['name']}")
        return 0
    finally:
        connection.close()


if __name__ == "__main__":
    sys.exit(main())
