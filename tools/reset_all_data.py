"""Vacía los datos de captura de osap_noticias conservando el esquema y los catálogos.

Borra: ejecuciones, observaciones, revisiones, publicaciones, noticias, análisis,
textos editoriales y traducciones. Y vacía también los editores y canales
(``--keep-channels`` los conserva), para poder re-sembrar el catálogo de fuentes.

Conserva: esquema, registro de migraciones, tipos de contenido y taxonomía.

Primero simula:  py -3 -m tools.reset_all_data
Después aplica:  py -3 -m tools.reset_all_data --apply
"""
from __future__ import annotations

import argparse
import json
import sys

from app.db import connect

# Orden inverso a las dependencias (hijos antes que padres).
TABLAS_CAPTURA = [
    "editorial_translations",
    "editorial_texts",
    "news_item_categories",
    "editorial_analyses",
    "analysis_inputs",
    "analysis_runs",
    "observation_revisions",
    "source_observations",
    "fetch_runs",
    "news_publications",
    "news_items",
]

TABLAS_CATALOGO = ["source_channels", "publishers"]


def _count(cur, table: str) -> int:
    cur.execute(f"SELECT COUNT(*) AS n FROM {table}")
    return int(cur.fetchone()["n"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Ejecuta el borrado.")
    parser.add_argument(
        "--keep-channels", action="store_true",
        help="Conserva editores y canales registrados.",
    )
    args = parser.parse_args()

    tables = list(TABLAS_CAPTURA)
    if not args.keep_channels:
        tables += TABLAS_CATALOGO

    connection = connect()
    try:
        with connection.cursor() as cur:
            antes = {t: _count(cur, t) for t in tables}

        print(json.dumps(
            {"modo": "APPLY" if args.apply else "SIMULACIÓN", "filas_antes": antes,
             "conserva_catalogos": True, "conserva_canales": args.keep_channels},
            ensure_ascii=False, indent=2,
        ))

        if not args.apply:
            connection.rollback()
            print("Simulación: no se ha borrado nada. Añade --apply para ejecutar.")
            return 0

        with connection.cursor() as cur:
            for table in tables:
                cur.execute(f"DELETE FROM {table}")
            # Reinicia los AUTO_INCREMENT de las tablas de captura para dejar
            # la base como recién instalada.
            for table in TABLAS_CAPTURA:
                cur.execute(f"ALTER TABLE {table} AUTO_INCREMENT = 1")
            if not args.keep_channels:
                cur.execute("ALTER TABLE publishers AUTO_INCREMENT = 1")
                cur.execute("ALTER TABLE source_channels AUTO_INCREMENT = 1")
        connection.commit()

        with connection.cursor() as cur:
            despues = {t: _count(cur, t) for t in tables}
        print(json.dumps({"filas_despues": despues}, ensure_ascii=False, indent=2))
        print("Datos de captura eliminados. Esquema, catálogos y taxonomía conservados.")
        return 0
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


if __name__ == "__main__":
    sys.exit(main())
