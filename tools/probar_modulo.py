"""Prueba del módulo de correo sin servidor SMTP.

Simula correos entrantes y muestra la respuesta (temas, idioma, noticias y avisos).

Uso:
    py -3 -m tools.probar_modulo
    py -3 -m tools.probar_modulo --raw correo.eml --save salida.eml
"""
from __future__ import annotations

import argparse
import json
import sys

import pymysql
from pymysql.cursors import DictCursor

from app.db import connect
from app.news_service import describe_vocabulary, handle_raw_message, handle_topics
from app.settings import load_settings


CORREOS = [
    ("anónimo, español, temas libres", """From: Ana Pérez <ana.perez@example.org>
Subject: Noticias sobre ópera y patrimonio
Message-ID: <demo-1@example.org>
MIME-Version: 1.0
Content-Type: text/plain; charset=utf-8

Hola, me interesan noticias sobre ópera, patrimonio y archivística.
Responde en español, 5 noticias como máximo.
"""),
    ("anónimo, inglés, temas libres", """From: John Smith <john@example.org>
Subject: Orchestras and research news in English
Message-ID: <demo-2@example.org>
MIME-Version: 1.0
Content-Type: text/plain; charset=utf-8

Please send me news about jazz, orchestras and musicology in English.
"""),
]


def _preparar_conexion():
    settings = load_settings()
    return settings, connect()


def _mostrar(titulo: str, response) -> None:
    print(f"\n=== {titulo} ===")
    data = response.as_dict()
    print(json.dumps({k: data[k] for k in ("status", "topics", "language", "topic_source",
                                            "count", "warnings")},
                     ensure_ascii=False, indent=2))
    for res in data["resolutions"]:
        print(f"  tema «{res['query']}» -> semilla={res['matched_topic']} "
              f"gen={res['genres']} osap={res['osap_terms']} "
              f"kw={res['keywords'][:5]}")
    for item in data["items"][:6]:
        print(f"  [{item['score']:>6.2f}] {item['title'][:70]}  ({item['publisher']}, {item['published_at']})")
        print(f"           coincide: {item['matched'][:4]}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", help="Fichero .eml a procesar")
    parser.add_argument("--save", help="Guardar el correo de respuesta en este fichero")
    args = parser.parse_args()

    settings = load_settings()
    print("Configuración del módulo:")
    print(json.dumps({
        "idioma_por_defecto": settings.default_language,
        "max_items": settings.max_items,
        "ventana_dias": settings.default_window_days,
        "remitentes_permitidos": settings.allowed_senders,
        "dominios_permitidos": settings.allowed_domains,
        "osap_habilitado": settings.osap_enabled,
        "smtp": f"{settings.mail.host}:{settings.mail.port}",
    }, ensure_ascii=False, indent=2))

    print("\nCatálogo OSAP:")
    print(json.dumps(describe_vocabulary(settings), ensure_ascii=False, indent=2)[:800])

    if args.raw:
        raw = open(args.raw, "r", encoding="utf-8", errors="replace").read()
        connection = connect()
        try:
            response = handle_raw_message(raw, connection, settings, persist=True)
        finally:
            connection.close()
        _mostrar(f"correo {args.raw}", response)
        if args.save and response.message:
            with open(args.save, "w", encoding="utf-8") as handle:
                handle.write(response.message.as_string())
            print(f"\nRespuesta guardada en {args.save}")
        return 0

    connection = connect()
    try:
        for titulo, raw in CORREOS:
            response = handle_raw_message(raw, connection, settings, persist=False)
            _mostrar(titulo, response)

        print("\n=== consulta directa ===")
        direct = handle_topics("api@osap.local", ["jazz", "investigación"], language="en",
                               limit=3, connection=connection, settings=settings)
        _mostrar("API directa", direct)
    finally:
        connection.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
