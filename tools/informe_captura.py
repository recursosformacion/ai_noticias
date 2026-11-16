"""Informe de captura en texto: por canal, por ejecución y duplicados.

Uso:
    py -3 -m tools.informe_captura
"""
from __future__ import annotations

import sys

from app.db import connect


def main() -> int:
    connection = connect()
    try:
        with connection.cursor() as cur:
            cur.execute("SELECT COUNT(*) n FROM news_items")
            total_noticias = cur.fetchone()["n"]
            cur.execute("SELECT COUNT(*) n FROM news_publications")
            total_pubs = cur.fetchone()["n"]
            cur.execute("SELECT COUNT(*) n FROM source_observations")
            total_obs = cur.fetchone()["n"]
            cur.execute("SELECT COUNT(*) n FROM fetch_runs")
            total_runs = cur.fetchone()["n"]

            print("== Totales ==")
            print(f"noticias={total_noticias} publicaciones={total_pubs} "
                  f"observaciones={total_obs} ejecuciones={total_runs}")

            print("\n== Canales activos ==")
            cur.execute(
                """SELECT s.id, p.name editor, s.name canal, s.declared_language,
                ct.code tipo, (SELECT COUNT(*) FROM fetch_runs r WHERE r.source_channel_id=s.id) runs,
                (SELECT SUM(r.items_new) FROM fetch_runs r WHERE r.source_channel_id=s.id) nuevos,
                (SELECT SUM(r.items_known) FROM fetch_runs r WHERE r.source_channel_id=s.id) conocidos,
                (SELECT SUM(r.items_error) FROM fetch_runs r WHERE r.source_channel_id=s.id) errores
                FROM source_channels s JOIN publishers p ON p.id=s.publisher_id
                LEFT JOIN content_types ct ON ct.id=s.default_content_type_id
                WHERE s.status='ACTIVE' ORDER BY s.id"""
            )
            print(f"{'id':>2} {'canal':44} {'idi':3} {'tipo':11} {'runs':>4} {'nuevos':>6} {'cono':>5} {'err':>4}")
            for r in cur.fetchall():
                print(f"{r['id']:>2} {r['canal'][:44]:44} {r['declared_language'] or '':3} "
                      f"{r['tipo'] or '':11} {r['runs'] or 0:>4} {r['nuevos'] or 0:>6} "
                      f"{r['conocidos'] or 0:>5} {r['errores'] or 0:>4}")

            print("\n== Canales en pausa ==")
            cur.execute(
                """SELECT s.id, p.name editor, s.name canal
                FROM source_channels s JOIN publishers p ON p.id=s.publisher_id
                WHERE s.status<>'ACTIVE' ORDER BY s.id"""
            )
            for r in cur.fetchall():
                print(f"{r['id']:>2} {r['canal'][:44]:44} {r['editor']}")

            print("\n== Última ejecución por canal ==")
            cur.execute(
                """SELECT s.id, s.name canal, r.id run, r.started_at, r.http_status,
                r.result_status, r.items_received recibidos, r.items_new nuevos,
                r.items_known conocidos, r.items_error errores
                FROM source_channels s
                JOIN fetch_runs r ON r.id=(SELECT MAX(id) FROM fetch_runs WHERE source_channel_id=s.id)
                ORDER BY s.id"""
            )
            for r in cur.fetchall():
                print(f"{r['id']:>2} {r['canal'][:36]:36} run={r['run']:>2} {r['started_at']} "
                      f"HTTP {r['http_status']} {r['result_status']:8} rec={r['recibidos']:>3} "
                      f"nuevos={r['nuevos']:>3} conocidos={r['conocidos']:>3} err={r['errores']}")

            print("\n== Noticias compartidas entre fuentes (misma huella de descripción) ==")
            cur.execute(
                """SELECT p.news_item_id, COUNT(DISTINCT p.publisher_id) editores,
                GROUP_CONCAT(DISTINCT pv.name ORDER BY pv.name SEPARATOR ' | ') medios,
                LEFT(MIN(p.title_original), 70) titulo
                FROM news_publications p JOIN publishers pv ON pv.id=p.publisher_id
                GROUP BY p.news_item_id HAVING editores > 1
                ORDER BY editores DESC, p.news_item_id"""
            )
            compartidas = cur.fetchall()
            for r in compartidas:
                print(f"item {r['news_item_id']:>4} ({r['editores']} editores): {r['titulo']}")
                print(f"          -> {r['medios']}")
            print(f"total noticias consolidadas entre fuentes: {len(compartidas)}")

            print("\n== Noticias por idioma declarado del canal ==")
            cur.execute(
                """SELECT s.declared_language idi, COUNT(DISTINCT p.news_item_id) n
                FROM news_publications p
                JOIN source_observations o ON o.news_publication_id=p.id
                JOIN source_channels s ON s.id=o.source_channel_id
                GROUP BY s.declared_language ORDER BY n DESC"""
            )
            for r in cur.fetchall():
                print(f"{r['idi'] or 'sin declarar':13} {r['n']:>5}")
        return 0
    finally:
        connection.close()


if __name__ == "__main__":
    sys.exit(main())
