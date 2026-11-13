"""Comandos locales para la captura de noticias."""
from __future__ import annotations

import argparse
import json
import sys

from .db import connect
from .collector import ingest_active_channels


def main() -> int:
    parser = argparse.ArgumentParser(prog="ai-noticias")
    sub = parser.add_subparsers(dest="command", required=True)
    ingest = sub.add_parser("ingest", help="Consultar fuentes RSS/Atom activas.")
    ingest.add_argument("--source-id", type=int, help="Limitar la ejecución a un canal.")
    args = parser.parse_args()

    connection = None
    try:
        connection = connect()
        if args.command == "ingest":
            results = ingest_active_channels(connection, args.source_id)
            print(json.dumps(results, ensure_ascii=False, indent=2, default=str))
            if not results:
                print("No hay canales ACTIVE registrados.")
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
