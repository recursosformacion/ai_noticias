"""Borra los datos de captura de prueba del canal BnF ID 6.

Primero simula: py -3 -m tools.reset_bnf_test_data
Después aplica: py -3 -m tools.reset_bnf_test_data --apply
Conserva canal, publisher, permisos, catálogos y taxonomía.
"""
from __future__ import annotations
import argparse, json
from app.db import connect

SOURCE_ID = 6
SOURCE_URL = "https://bibliographienationale.bnf.fr/rss/mus"

def count(cur, sql, params=()):
    cur.execute(sql, params)
    return int(cur.fetchone()["n"])

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    conn = connect()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id,url FROM source_channels WHERE id=%s FOR UPDATE", (SOURCE_ID,))
            channel = cur.fetchone()
            if not channel or channel["url"] != SOURCE_URL:
                raise RuntimeError("El canal 6 no es el RSS BnF esperado. Abortado.")
            cur.execute("SELECT id,news_publication_id FROM source_observations WHERE source_channel_id=%s ORDER BY id FOR UPDATE", (SOURCE_ID,))
            observations = cur.fetchall()
            obs_ids = [r["id"] for r in observations]
            pub_ids = sorted({r["news_publication_id"] for r in observations if r["news_publication_id"]})
            publications = []
            if pub_ids:
                marks = ",".join(["%s"]*len(pub_ids))
                cur.execute(f"SELECT id,news_item_id FROM news_publications WHERE id IN ({marks}) FOR UPDATE", pub_ids)
                publications = cur.fetchall()
                if len(publications) != len(pub_ids):
                    raise RuntimeError("Faltan publicaciones enlazadas. Abortado.")
                if count(cur, f"SELECT COUNT(*) n FROM source_observations WHERE news_publication_id IN ({marks}) AND source_channel_id<>%s", (*pub_ids,SOURCE_ID)):
                    raise RuntimeError("Otras fuentes usan estas publicaciones. Abortado.")
            item_ids = sorted({r["news_item_id"] for r in publications if r["news_item_id"]})
            if item_ids:
                imarks = ",".join(["%s"]*len(item_ids))
                pmarks = ",".join(["%s"]*len(pub_ids))
                if count(cur, f"SELECT COUNT(*) n FROM news_publications WHERE news_item_id IN ({imarks}) AND id NOT IN ({pmarks})", (*item_ids,*pub_ids)):
                    raise RuntimeError("Las noticias tienen publicaciones de otras fuentes. Abortado.")
                for table in ("analysis_runs","news_item_categories","editorial_texts"):
                    if count(cur, f"SELECT COUNT(*) n FROM {table} WHERE news_item_id IN ({imarks})", item_ids):
                        raise RuntimeError(f"Hay datos derivados en {table}; abortado.")
            if pub_ids:
                pmarks=",".join(["%s"]*len(pub_ids))
                if count(cur, f"SELECT COUNT(*) n FROM analysis_inputs WHERE news_publication_id IN ({pmarks})", pub_ids):
                    raise RuntimeError("Hay entradas de análisis asociadas; abortado.")
            if count(cur, """SELECT COUNT(*) n FROM analysis_inputs ai JOIN observation_revisions r ON r.id=ai.observation_revision_id JOIN source_observations o ON o.id=r.source_observation_id WHERE o.source_channel_id=%s""",(SOURCE_ID,)):
                raise RuntimeError("Hay análisis que usan revisiones BnF; abortado.")
            revisions=count(cur,"SELECT COUNT(*) n FROM observation_revisions r JOIN source_observations o ON o.id=r.source_observation_id WHERE o.source_channel_id=%s",(SOURCE_ID,))
            runs=count(cur,"SELECT COUNT(*) n FROM fetch_runs WHERE source_channel_id=%s",(SOURCE_ID,))
            print(json.dumps({"channel_id":SOURCE_ID,"observations":len(obs_ids),"revisions":revisions,"publications":len(pub_ids),"news_items":len(item_ids),"fetch_runs":runs,"mode":"APPLY" if args.apply else "DRY RUN"},indent=2))
            if not args.apply:
                conn.rollback()
                print("Simulación: no se ha borrado nada.")
                return 0
            cur.execute("DELETE r FROM observation_revisions r JOIN source_observations o ON o.id=r.source_observation_id WHERE o.source_channel_id=%s",(SOURCE_ID,))
            cur.execute("DELETE FROM source_observations WHERE source_channel_id=%s",(SOURCE_ID,))
            cur.execute("DELETE FROM fetch_runs WHERE source_channel_id=%s",(SOURCE_ID,))
            if item_ids:
                imarks=",".join(["%s"]*len(item_ids))
                cur.execute(f"UPDATE news_items SET primary_publication_id=NULL WHERE id IN ({imarks})",item_ids)
            if pub_ids:
                pmarks=",".join(["%s"]*len(pub_ids))
                cur.execute(f"DELETE FROM news_publications WHERE id IN ({pmarks})",pub_ids)
            if item_ids:
                imarks=",".join(["%s"]*len(item_ids))
                cur.execute(f"DELETE FROM news_items WHERE id IN ({imarks})",item_ids)
            cur.execute("UPDATE source_channels SET etag=NULL,last_modified=NULL,last_checked_at=NULL WHERE id=%s",(SOURCE_ID,))
        conn.commit()
        print("Datos de captura BnF eliminados; configuración y canal conservados.")
        return 0
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    raise SystemExit(main())
