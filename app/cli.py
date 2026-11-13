"""Comandos locales para la captura de noticias."""
from __future__ import annotations

import argparse
import json
import sys

from .db import connect
from .collector import ingest_active_channels, probe_candidate_channels


def main() -> int:
    parser = argparse.ArgumentParser(prog="ai-noticias")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("sources", help="Mostrar los canales registrados y su estado.")

    probe = sub.add_parser(
        "probe", help="Comprobar LOC y BnF sin guardar elementos ni modificar la base."
    )
    probe.add_argument("--source-id", type=int, help="Limitar la prueba a un canal permitido.")

    ingest = sub.add_parser("ingest", help="Consultar fuentes RSS/Atom activas.")
    ingest.add_argument("--source-id", type=int, help="Limitar la ejecución a un canal.")

    activate = sub.add_parser("activate", help="Activar un canal tras revisar sus condiciones.")
    activate.add_argument("--source-id", type=int, required=True)
    activate.add_argument(
        "--confirm-terms-reviewed", action="store_true",
        help="Confirma que se han revisado los términos y el uso previsto."
    )

    args = parser.parse_args()
    connection = None
    try:
        connection = connect()
        if args.command == "sources":
            with connection.cursor() as cursor:
                cursor.execute(
                    """SELECT id, name, url, status, declared_language, topic_hint,
                    terms_url, terms_reviewed_at FROM source_channels ORDER BY id"""
                )
                rows = cursor.fetchall()
            print(json.dumps(rows, ensure_ascii=False, indent=2, default=str))
            if not rows:
                print("No hay canales registrados. Aplica las migraciones.")
        elif args.command == "probe":
            results = probe_candidate_channels(connection, args.source_id)
            print(json.dumps(results, ensure_ascii=False, indent=2, default=str))
            if not results:
                print("No hay canales permitidos para la prueba. Comprueba la migración 003.")
        elif args.command == "ingest":
            results = ingest_active_channels(connection, args.source_id)
            print(json.dumps(results, ensure_ascii=False, indent=2, default=str))
            if not results:
                print("No hay canales ACTIVE registrados.")
        elif args.command == "activate":
            if not args.confirm_terms_reviewed:
                raise RuntimeError(
                    "No se activa el canal sin --confirm-terms-reviewed. "
                    "La existencia de un RSS no implica permiso de reutilización."
                )
            with connection.cursor() as cursor:
                cursor.execute(
                    """UPDATE source_channels SET status='ACTIVE',
                    terms_reviewed_at=UTC_TIMESTAMP(6)
                    WHERE id=%s AND status='PAUSED'""",
                    (args.source_id,),
                )
                changed = cursor.rowcount
            connection.commit()
            if changed != 1:
                raise RuntimeError(
                    "No se activó ningún canal: comprueba el ID y que su estado sea PAUSED."
                )
            print(f"Canal {args.source_id} activado. Ya puede incluirse en la captura.")
        return 0
    except Exception as exc:
        if connection:
            connection.rollback()
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
