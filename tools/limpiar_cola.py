"""Vacía la cola de salida (mensajes de prueba pendientes).

Uso:
    py -3 -m tools.limpiar_cola            # ver qué hay
    py -3 -m tools.limpiar_cola --apply    # borrar los PENDING/FAILED
"""
from __future__ import annotations

import argparse
import sys

from app.db import connect


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--all", action="store_true", help="Incluye los ya enviados.")
    args = parser.parse_args()

    connection = connect()
    try:
        with connection.cursor() as cur:
            cur.execute(
                """SELECT id, user_ref, recipient_address, status, digest_date,
                language_code, items_count, subject
                FROM outbound_messages ORDER BY id"""
            )
            rows = cur.fetchall()
            for r in rows:
                print(f"#{r['id']:>3} {r['status']:8} {r['language_code'] or '-':2} "
                      f"items={r['items_count']:>2} {(r['user_ref'] or r['recipient_address'] or '?'):38} "
                      f"{(r['subject'] or '')[:40]}")

            condition = "" if args.all else " WHERE status <> 'SENT'"
            cur.execute(f"SELECT COUNT(*) n FROM outbound_messages{condition}")
            total = cur.fetchone()["n"]
            print(f"\na borrar: {total}")

            if not args.apply:
                print("Simulación. Añade --apply para borrar.")
                return 0
            if total:
                cur.execute(f"DELETE FROM outbound_messages{condition}")
                print(f"Borrados {total} mensajes.")
        connection.commit()
        return 0
    finally:
        connection.close()


if __name__ == "__main__":
    sys.exit(main())
