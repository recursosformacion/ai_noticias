"""Estado de una fuente concreta: canal, última ejecución y errores."""
import sys

from app.db import connect

PATTERN = sys.argv[1] if len(sys.argv) > 1 else "sibetrans"

connection = connect()
try:
    with connection.cursor() as cur:
        cur.execute(
            "SELECT id, name, status, delivery_mode, url FROM source_channels "
            "WHERE url LIKE %s",
            (f"%{PATTERN}%",),
        )
        channels = cur.fetchall()
        for ch in channels:
            print(f"#{ch['id']} {ch['name']} [{ch['status']}/{ch['delivery_mode']}]")
            print(f"   {ch['url']}")
            cur.execute(
                """SELECT id, result_status, items_received, items_new, items_error,
                error_code, LEFT(error_message, 200) m
                FROM fetch_runs WHERE source_channel_id=%s ORDER BY id DESC LIMIT 3""",
                (ch["id"],),
            )
            for run in cur.fetchall():
                print(f"   run {run['id']}: {run['result_status']} rec={run['items_received']} "
                      f"new={run['items_new']} err={run['items_error']} {run['error_code'] or ''}")
                if run["m"]:
                    print(f"      {run['m']}")
finally:
    connection.close()
