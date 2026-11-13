"""Apply the versioned SQL migrations using the local osap.toml connection."""
from __future__ import annotations

from pathlib import Path
import sys

from mysql_support import MysqlClient, ROOT, load_db_config


MIGRATIONS = [
    ROOT / "database" / "migrations" / "001_initial_schema.sql",
    ROOT / "database" / "migrations" / "002_seed_content_types.sql",
]


def main() -> int:
    try:
        config = load_db_config()
        print(f"Conectando a MariaDB en {config['host']}:{config['port']} / {config['name']}...")
        with MysqlClient(config) as client:
            for migration in MIGRATIONS:
                if not migration.is_file():
                    raise RuntimeError(f"No se encuentra la migración: {migration}")
                print(f"Aplicando {migration.name}...")
                client.run(migration.read_text(encoding="utf-8"), stdin=True)
                print(f"  OK: {migration.name}")
        print("Migraciones finalizadas correctamente.")
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
