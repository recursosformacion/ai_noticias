uito, musical....y todo e"""Prueba de extremo a extremo del buzón: correo en carpeta -> respuesta en cola.

Crea dos correos de ejemplo, los procesa con `app.mailbox` y muestra el resultado
junto con el estado de la cola de salida.

Uso: py -3 -m tools.probar_buzon [--delivery QUEUE|FILE]
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from app.db import connect
from app.mailbox import process_directory
from app.settings import load_settings

INBOX = Path("var/inbox")

CORREOS = {
    "001_jazz_sin_perfil.eml": """From: Carlos Ruiz <carlos@example.org>
To: noticias@osap.local
Subject: Noticias de jazz e investigacion
Message-ID: <test-001@example.org>
Date: Sun, 15 Nov 2026 09:00:00 +0100
MIME-Version: 1.0
Content-Type: text/plain; charset=utf-8

Hola, me interesan las noticias sobre jazz y musicologia.
""",
    "002_perfil_ana.eml": """From: Ana Perez <ana.perez@example.org>
To: noticias@osap.local
Subject: Consulta mensual
Message-ID: <test-002@example.org>
Date: Sun, 15 Nov 2026 09:05:00 +0100
MIME-Version: 1.0
Content-Type: text/plain; charset=utf-8

Quiero mis noticias habituales.
""",
    "003_invalido.eml": """From: sin-arroba
To: noticias@osap.local
Subject: roto
Message-ID: <test-003@example.org>

hola
""",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--delivery", choices=["QUEUE", "FILE", "NONE"], default="QUEUE")
    args = parser.parse_args()

    settings = load_settings()
    if INBOX.exists():
        shutil.rmtree(INBOX)
    (INBOX / "processed").mkdir(parents=True)
    for name, content in CORREOS.items():
        (INBOX / name).write_text(content, encoding="utf-8")

    print(f"Correos creados en {INBOX.resolve()}")
    print(f"Entrega: {args.delivery}")

    connection = connect()
    try:
        result = process_directory(str(INBOX), connection, settings, args.delivery)
        print("\n=== Resultado del buzón ===")
        print(json.dumps(result.as_dict(), ensure_ascii=False, indent=2, default=str))

        with connection.cursor() as cur:
            cur.execute(
                """SELECT id, recipient, subject, kind, status, language_code,
                items_count, CHAR_LENGTH(body_text) len
                FROM outbound_messages ORDER BY id DESC LIMIT 5"""
            )
            print("\n=== Cola de salida ===")
            for r in cur.fetchall():
                print(f"#{r['id']} {r['status']} {r['language_code']} "
                      f"items={r['items_count']} len={r['len']} -> {r['recipient']}")
                print(f"    {r['subject']}")

            cur.execute(
                """SELECT id, sender_domain, topic_source, result_status, items_sent,
                LEFT(topics_json, 90) topics
                FROM email_requests ORDER BY id DESC LIMIT 5"""
            )
            print("\n=== Peticiones registradas ===")
            for r in cur.fetchall():
                print(f"#{r['id']} {r['result_status']:8} {r['topic_source']:7} "
                      f"items={r['items_sent']} dom={r['sender_domain']} {r['topics']}")
    finally:
        connection.close()

    print(f"\nArchivados en {INBOX / 'processed'}")
    return 0 if result.failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
