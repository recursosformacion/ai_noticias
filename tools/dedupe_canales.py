"""Elimina canales duplicados (misma URL) conservando el registro más reciente.

Los canales antiguos 1-6 de la migración 003 quedaron duplicados por la 007
(misma URL). Como están en PAUSED y sin datos de captura, se pueden borrar.

Uso: py -3 -m tools.dedupe_canales [--apply]
"""
from __future__ import annotations

import argparse
import sys

from app.db import connect


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    connection = connect()
    try:
        with connection.cursor() as cur:
            # La URL se compara normalizada (sin espacios ni barra final).
            cur.execute(
                """SELECT TRIM(TRAILING '/' FROM TRIM(url)) url_norm,
                COUNT(*) n, GROUP_CONCAT(id ORDER BY id) ids,
                GROUP_CONCAT(status ORDER BY id) estados,
                GROUP_CONCAT(url ORDER BY id SEPARATOR ' || ') urls
                FROM source_channels GROUP BY url_norm HAVING n > 1"""
            )
            dupes = cur.fetchall()

            borrar = []
            for row in dupes:
                ids = [int(x) for x in row["ids"].split(",")]
                estados = row["estados"].split(",")
                conservar = ids[-1]
                print(f"URL duplicada ({len(ids)}): {row['url_norm']}")
                print(f"  valores: {row['urls']}")
                print(f"  ids={ids} estados={estados} -> se conserva {conservar}")
                for cid, estado in zip(ids, estados):
                    if cid == conservar:
                        continue
                    if estado != "PAUSED":
                        raise RuntimeError(
                            f"El canal {cid} está en {estado}: no se borra automáticamente."
                        )
                    borrar.append(cid)

            if not borrar:
                print("No hay canales duplicados que borrar.")
                return 0
            if not args.apply:
                connection.rollback()
                print(f"Simulación: se borrarían {len(borrar)} canales: {borrar}")
                return 0

            marks = ",".join(["%s"] * len(borrar))
            cur.execute(
                f"""SELECT COUNT(*) n FROM source_observations WHERE source_channel_id IN ({marks})""",
                borrar,
            )
            if cur.fetchone()["n"]:
                raise RuntimeError("Los canales duplicados tienen observaciones; abortado.")
            cur.execute(f"DELETE FROM source_channels WHERE id IN ({marks})", borrar)
            connection.commit()
            print(f"Canales borrados: {borrar}")
        return 0
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


if __name__ == "__main__":
    sys.exit(main())
