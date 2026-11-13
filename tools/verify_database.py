"""Verify the expected ai_noticias schema and seed data."""
from __future__ import annotations

import sys

from mysql_support import MysqlClient, load_db_config


EXPECTED_TABLES = {
    "schema_migrations", "publishers", "source_channels", "fetch_runs",
    "news_items", "news_publications", "source_observations",
    "observation_revisions", "taxonomy_versions", "categories",
    "content_types", "analysis_runs", "analysis_inputs",
    "editorial_analyses", "news_item_categories", "editorial_texts",
    "editorial_translations",
}
EXPECTED_MIGRATIONS = {"001_initial_schema", "002_seed_content_types"}
EXPECTED_CONTENT_TYPES = {
    "NEWS", "EVENT", "RELEASE", "RESEARCH", "BIBLIO",
    "COLLECTION", "INTERVIEW", "OPINION", "OTHER", "REVIEW",
}


def main() -> int:
    try:
        config = load_db_config()
        print(f"Verificando {config['name']} en {config['host']}:{config['port']}...")
        with MysqlClient(config) as client:
            tables = set(filter(None, client.run(
                "SELECT TABLE_NAME FROM information_schema.TABLES "
                "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_TYPE = 'BASE TABLE' "
                "ORDER BY TABLE_NAME"
            ).splitlines()))
            migrations = set(filter(None, client.run(
                "SELECT version FROM schema_migrations ORDER BY version"
            ).splitlines()))
            content_types = set(filter(None, client.run(
                "SELECT code FROM content_types ORDER BY code"
            ).splitlines()))
            fk_count = int(client.run(
                "SELECT COUNT(*) FROM information_schema.KEY_COLUMN_USAGE "
                "WHERE TABLE_SCHEMA = DATABASE() AND REFERENCED_TABLE_NAME IS NOT NULL"
            ) or "0")
            engines = client.run(
                "SELECT COUNT(*) FROM information_schema.TABLES "
                "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_TYPE = 'BASE TABLE' "
                "AND ENGINE = 'InnoDB'"
            )
            engine_count = int(engines or "0")

        missing_tables = EXPECTED_TABLES - tables
        missing_migrations = EXPECTED_MIGRATIONS - migrations
        missing_types = EXPECTED_CONTENT_TYPES - content_types

        print(f"Tablas detectadas: {len(tables)} (esperadas: {len(EXPECTED_TABLES)})")
        print(f"Claves foráneas: {fk_count}")
        print(f"Tablas InnoDB: {engine_count}")
        print(f"Migraciones registradas: {', '.join(sorted(migrations)) or 'ninguna'}")
        print(f"Tipos de contenido: {len(content_types)} (esperados: {len(EXPECTED_CONTENT_TYPES)})")

        if missing_tables:
            print("FALTAN TABLAS: " + ", ".join(sorted(missing_tables)))
        if missing_migrations:
            print("FALTAN MIGRACIONES: " + ", ".join(sorted(missing_migrations)))
        if missing_types:
            print("FALTAN TIPOS: " + ", ".join(sorted(missing_types)))
        if engine_count != len(EXPECTED_TABLES):
            print("AVISO: el número de tablas InnoDB no coincide con el esquema esperado.")

        if missing_tables or missing_migrations or missing_types or engine_count != len(EXPECTED_TABLES):
            print("RESULTADO: revisión incompleta; hay que corregir lo indicado.")
            return 2

        print("RESULTADO: esquema y datos semilla verificados.")
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
