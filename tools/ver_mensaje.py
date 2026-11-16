"""Muestra el contenido de un mensaje de la cola de salida.

Uso: py -3 -m tools.ver_mensaje [--id N] [--html]
"""
from __future__ import annotations

import argparse
import sys

from app.db import connect


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", type=int)
    parser.add_argument("--html", action="store_true")
    args = parser.parse_args()

    connection = connect()
    try:
        with connection.cursor() as cur:
            if args.id:
                cur.execute("SELECT * FROM outbound_messages WHERE id=%s", (args.id,))
            else:
                cur.execute("SELECT * FROM outbound_messages ORDER BY id DESC LIMIT 1")
            row = cur.fetchone()
            if not row:
                print("No hay mensajes en la cola.")
                return 1

            print("=" * 74)
            print("ID:", row["id"], "| estado:", row["status"])
            print("user_ref:", row["user_ref"])
            print("dirección:", row["recipient_address"])
            print("idioma:", row["language_code"], "| noticias:", row["items_count"])
            print("asunto:", row["subject"])
            print("fecha boletín:", row["digest_date"], "| ventana:", row["digest_window_days"], "días")
            print("=" * 74)
            body = row["body_html"] if args.html else row["body_text"]
            print(body)
        return 0
    finally:
        connection.close()


if __name__ == "__main__":
    sys.exit(main())
