"""Muestra las ejecuciones fallidas/parciales y sus mensajes de error."""
from __future__ import annotations

import json
import sys

from app.db import connect


def main() -> int:
    connection = connect()
    try:
        with connection.cursor() as cur:
            cur.execute(
                """SELECT id, source_channel_id, result_status, items_received,
                items_new, items_known, items_error, error_code, error_message
                FROM fetch_runs WHERE result_status <> 'SUCCESS' ORDER BY id"""
            )
            rows = cur.fetchall()
        print(json.dumps(rows, ensure_ascii=False, indent=2, default=str))
        return 0
    finally:
        connection.close()


if __name__ == "__main__":
    sys.exit(main())
