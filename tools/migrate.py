"""Apply the versioned SQL migrations using the local osap.toml connection."""
from __future__ import annotations

from pathlib import Path
import sys

from mysql_support import MysqlClient, ROOT, load_db_config


MIGRATIONS = [
    ROOT / "database" / "migrations" / "001_initial_schema.sql",
    ROOT / "database" / "migrations" / "002_seed_content_types.sql",
    ROOT / "database" / "migrations" / "003_initial_source_candidates.sql",
    ROOT / "database" / "migrations" / "004_source_content_type_hints.sql",
    ROOT / "database" / "migrations" / "005_description_identity.sql",
    ROOT / "database" / "migrations" / "006_taxonomy_seed.sql",
    ROOT / "database" / "migrations" / "007_free_music_sources.sql",
    ROOT / "database" / "migrations" / "008_noticias_module.sql",
    ROOT / "database" / "migrations" / "009_user_profiles.sql",
    ROOT / "database" / "migrations" / "010_topic_terms_i18n.sql",
    ROOT / "database" / "migrations" / "011_delivery_modes.sql",
    ROOT / "database" / "migrations" / "012_corpus_musical.sql",
    ROOT / "database" / "migrations" / "013_outbound_queue.sql",
    ROOT / "database" / "migrations" / "014_fuente_es.sql",
    ROOT / "database" / "migrations" / "015_outbound_userref.sql",
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
