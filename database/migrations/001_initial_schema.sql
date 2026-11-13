-- ai_noticias — migración inicial de esquema
-- Destino: osap_noticias
-- Compatibilidad objetivo: MySQL 8.0.16+ (InnoDB, utf8mb4).
-- NO ejecutar en producción sin backup, verificación de versión y revisión previa.
-- La conexión y los permisos de creación de base/esquema se gestionan fuera de este archivo.

CREATE DATABASE IF NOT EXISTS osap_noticias
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE osap_noticias;

SET NAMES utf8mb4;
SET time_zone = '+00:00';

CREATE TABLE IF NOT EXISTS schema_migrations (
  version VARCHAR(100) NOT NULL,
  applied_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  description VARCHAR(255) NOT NULL,
  PRIMARY KEY (version)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS publishers (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  name VARCHAR(255) NOT NULL,
  website_url VARCHAR(2048) NULL,
  domain VARCHAR(255) NULL,
  country_code CHAR(2) NULL,
  description TEXT NULL,
  created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  KEY ix_publishers_name (name),
  KEY ix_publishers_domain (domain)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS source_channels (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  publisher_id BIGINT UNSIGNED NULL,
  provider_name VARCHAR(255) NOT NULL,
  name VARCHAR(255) NOT NULL,
  url VARCHAR(2048) NOT NULL,
  url_sha256 BINARY(32) NOT NULL,
  protocol VARCHAR(30) NOT NULL,
  format VARCHAR(30) NULL,
  declared_language VARCHAR(35) NULL,
  topic_hint VARCHAR(500) NULL,
  poll_interval_minutes INT UNSIGNED NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
  terms_url VARCHAR(2048) NULL,
  terms_reviewed_at DATETIME(6) NULL,
  usage_policy TEXT NULL,
  etag VARCHAR(500) NULL,
  last_modified VARCHAR(500) NULL,
  last_checked_at DATETIME(6) NULL,
  created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  UNIQUE KEY uq_source_channels_url_hash (url_sha256),
  KEY ix_source_channels_status_checked (status, last_checked_at),
  KEY ix_source_channels_publisher (publisher_id),
  CONSTRAINT fk_source_channels_publisher FOREIGN KEY (publisher_id) REFERENCES publishers(id) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS fetch_runs (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  source_channel_id BIGINT UNSIGNED NOT NULL,
  started_at DATETIME(6) NOT NULL,
  finished_at DATETIME(6) NULL,
  requested_url VARCHAR(2048) NOT NULL,
  final_url VARCHAR(2048) NULL,
  http_status SMALLINT UNSIGNED NULL,
  result_status VARCHAR(20) NOT NULL DEFAULT 'RUNNING',
  items_received INT UNSIGNED NOT NULL DEFAULT 0,
  items_new INT UNSIGNED NOT NULL DEFAULT 0,
  items_known INT UNSIGNED NOT NULL DEFAULT 0,
  items_error INT UNSIGNED NOT NULL DEFAULT 0,
  duration_ms INT UNSIGNED NULL,
  error_code VARCHAR(100) NULL,
  error_message TEXT NULL,
  PRIMARY KEY (id),
  KEY ix_fetch_runs_channel_started (source_channel_id, started_at),
  KEY ix_fetch_runs_status_started (result_status, started_at),
  CONSTRAINT fk_fetch_runs_channel FOREIGN KEY (source_channel_id) REFERENCES source_channels(id) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS news_items (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
  primary_publication_id BIGINT UNSIGNED NULL,
  first_detected_at DATETIME(6) NOT NULL,
  last_detected_at DATETIME(6) NOT NULL,
  created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  KEY ix_news_items_status_last_detected (status, last_detected_at),
  KEY ix_news_items_first_detected (first_detected_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS news_publications (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  publisher_id BIGINT UNSIGNED NULL,
  news_item_id BIGINT UNSIGNED NULL,
  external_id VARCHAR(1000) NULL,
  canonical_url VARCHAR(2048) NULL,
  original_url VARCHAR(2048) NULL,
  url_sha256 BINARY(32) NULL,
  title_original TEXT NOT NULL,
  description_original MEDIUMTEXT NULL,
  author_original VARCHAR(500) NULL,
  published_at DATETIME(6) NULL,
  updated_at DATETIME(6) NULL,
  published_at_raw VARCHAR(100) NULL,
  updated_at_raw VARCHAR(100) NULL,
  language_declared VARCHAR(35) NULL,
  language_detected VARCHAR(35) NULL,
  language_evidence VARCHAR(30) NULL,
  language_confidence DECIMAL(5,4) NULL,
  first_seen_at DATETIME(6) NOT NULL,
  last_seen_at DATETIME(6) NOT NULL,
  created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  updated_at_record DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  KEY ix_news_publications_publisher_date (publisher_id, published_at),
  KEY ix_news_publications_news_item (news_item_id),
  KEY ix_news_publications_language_date (language_detected, published_at),
  KEY ix_news_publications_url_hash (url_sha256),
  CONSTRAINT fk_news_publications_publisher FOREIGN KEY (publisher_id) REFERENCES publishers(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_news_publications_item FOREIGN KEY (news_item_id) REFERENCES news_items(id) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

ALTER TABLE news_items
  ADD CONSTRAINT fk_news_items_primary_publication
  FOREIGN KEY (primary_publication_id) REFERENCES news_publications(id)
  ON DELETE RESTRICT ON UPDATE RESTRICT;

CREATE TABLE IF NOT EXISTS source_observations (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  source_channel_id BIGINT UNSIGNED NOT NULL,
  fetch_run_id BIGINT UNSIGNED NOT NULL,
  external_id VARCHAR(1000) NULL,
  external_id_hash BINARY(32) NULL,
  url_original VARCHAR(2048) NULL,
  title_original TEXT NULL,
  description_original MEDIUMTEXT NULL,
  author_original VARCHAR(500) NULL,
  published_at_raw VARCHAR(100) NULL,
  published_at DATETIME(6) NULL,
  updated_at_raw VARCHAR(100) NULL,
  updated_at DATETIME(6) NULL,
  declared_language VARCHAR(35) NULL,
  payload_metadata JSON NULL,
  content_hash BINARY(32) NOT NULL,
  first_seen_at DATETIME(6) NOT NULL,
  last_seen_at DATETIME(6) NOT NULL,
  news_publication_id BIGINT UNSIGNED NULL,
  processing_status VARCHAR(20) NOT NULL DEFAULT 'CAPTURED',
  PRIMARY KEY (id),
  UNIQUE KEY uq_observations_channel_external_hash (source_channel_id, external_id_hash),
  KEY ix_observations_fetch_run (fetch_run_id),
  KEY ix_observations_publication (news_publication_id),
  KEY ix_observations_content_hash (content_hash),
  KEY ix_observations_last_seen (last_seen_at),
  CONSTRAINT fk_observations_channel FOREIGN KEY (source_channel_id) REFERENCES source_channels(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_observations_fetch_run FOREIGN KEY (fetch_run_id) REFERENCES fetch_runs(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_observations_publication FOREIGN KEY (news_publication_id) REFERENCES news_publications(id) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS observation_revisions (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  source_observation_id BIGINT UNSIGNED NOT NULL,
  revision_number INT UNSIGNED NOT NULL,
  observed_at DATETIME(6) NOT NULL,
  content_hash BINARY(32) NOT NULL,
  title_original TEXT NULL,
  description_original MEDIUMTEXT NULL,
  url_original VARCHAR(2048) NULL,
  published_at_raw VARCHAR(100) NULL,
  updated_at_raw VARCHAR(100) NULL,
  metadata JSON NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_observation_revision_number (source_observation_id, revision_number),
  KEY ix_observation_revisions_hash (content_hash),
  CONSTRAINT fk_observation_revisions_observation FOREIGN KEY (source_observation_id) REFERENCES source_observations(id) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS taxonomy_versions (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  version_code VARCHAR(40) NOT NULL,
  description TEXT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'DRAFT',
  effective_at DATETIME(6) NULL,
  created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  UNIQUE KEY uq_taxonomy_versions_code (version_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS categories (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  taxonomy_version_id BIGINT UNSIGNED NOT NULL,
  parent_id BIGINT UNSIGNED NULL,
  code VARCHAR(100) NOT NULL,
  name VARCHAR(255) NOT NULL,
  description TEXT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
  PRIMARY KEY (id),
  UNIQUE KEY uq_categories_version_code (taxonomy_version_id, code),
  KEY ix_categories_parent (parent_id),
  CONSTRAINT fk_categories_taxonomy FOREIGN KEY (taxonomy_version_id) REFERENCES taxonomy_versions(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_categories_parent FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS content_types (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  code VARCHAR(40) NOT NULL,
  name VARCHAR(100) NOT NULL,
  description TEXT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
  PRIMARY KEY (id),
  UNIQUE KEY uq_content_types_code (code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS analysis_runs (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  news_item_id BIGINT UNSIGNED NOT NULL,
  provider VARCHAR(50) NOT NULL,
  model VARCHAR(150) NOT NULL,
  prompt_version VARCHAR(80) NOT NULL,
  taxonomy_version_id BIGINT UNSIGNED NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
  started_at DATETIME(6) NULL,
  finished_at DATETIME(6) NULL,
  input_language VARCHAR(35) NULL,
  usage_input_tokens BIGINT UNSIGNED NULL,
  usage_output_tokens BIGINT UNSIGNED NULL,
  cost_amount DECIMAL(12,6) NULL,
  cost_currency CHAR(3) NULL,
  error_code VARCHAR(100) NULL,
  error_message TEXT NULL,
  raw_response MEDIUMTEXT NULL,
  created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  KEY ix_analysis_runs_item_created (news_item_id, created_at),
  KEY ix_analysis_runs_status_created (status, created_at),
  CONSTRAINT fk_analysis_runs_item FOREIGN KEY (news_item_id) REFERENCES news_items(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_analysis_runs_taxonomy FOREIGN KEY (taxonomy_version_id) REFERENCES taxonomy_versions(id) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS analysis_inputs (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  analysis_run_id BIGINT UNSIGNED NOT NULL,
  news_publication_id BIGINT UNSIGNED NOT NULL,
  observation_revision_id BIGINT UNSIGNED NULL,
  content_hash BINARY(32) NOT NULL,
  input_role VARCHAR(20) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_analysis_input_identity (analysis_run_id, news_publication_id, content_hash),
  KEY ix_analysis_inputs_publication (news_publication_id),
  CONSTRAINT fk_analysis_inputs_run FOREIGN KEY (analysis_run_id) REFERENCES analysis_runs(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_analysis_inputs_publication FOREIGN KEY (news_publication_id) REFERENCES news_publications(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_analysis_inputs_revision FOREIGN KEY (observation_revision_id) REFERENCES observation_revisions(id) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS editorial_analyses (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  analysis_run_id BIGINT UNSIGNED NOT NULL,
  is_relevant BOOLEAN NOT NULL,
  content_type_id BIGINT UNSIGNED NULL,
  language_detected VARCHAR(35) NULL,
  language_evidence VARCHAR(30) NULL,
  language_confidence DECIMAL(5,4) NULL,
  relevance_reason TEXT NULL,
  confidence DECIMAL(5,4) NULL,
  needs_review BOOLEAN NOT NULL DEFAULT FALSE,
  created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  UNIQUE KEY uq_editorial_analyses_run (analysis_run_id),
  KEY ix_editorial_analyses_content_type (content_type_id),
  CONSTRAINT fk_editorial_analyses_run FOREIGN KEY (analysis_run_id) REFERENCES analysis_runs(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_editorial_analyses_content_type FOREIGN KEY (content_type_id) REFERENCES content_types(id) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS news_item_categories (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  news_item_id BIGINT UNSIGNED NOT NULL,
  category_id BIGINT UNSIGNED NOT NULL,
  editorial_analysis_id BIGINT UNSIGNED NULL,
  confidence DECIMAL(5,4) NULL,
  assignment_status VARCHAR(20) NOT NULL DEFAULT 'PROPOSED',
  assigned_at DATETIME(6) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_news_item_category (news_item_id, category_id),
  KEY ix_news_item_categories_category_item (category_id, news_item_id),
  CONSTRAINT fk_news_item_categories_item FOREIGN KEY (news_item_id) REFERENCES news_items(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_news_item_categories_category FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_news_item_categories_analysis FOREIGN KEY (editorial_analysis_id) REFERENCES editorial_analyses(id) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS editorial_texts (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  news_item_id BIGINT UNSIGNED NOT NULL,
  editorial_analysis_id BIGINT UNSIGNED NOT NULL,
  language_code VARCHAR(35) NOT NULL DEFAULT 'es',
  title VARCHAR(500) NOT NULL,
  summary TEXT NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'DRAFT',
  created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  KEY ix_editorial_texts_item_language_created (news_item_id, language_code, created_at),
  CONSTRAINT fk_editorial_texts_item FOREIGN KEY (news_item_id) REFERENCES news_items(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_editorial_texts_analysis FOREIGN KEY (editorial_analysis_id) REFERENCES editorial_analyses(id) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS editorial_translations (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  editorial_text_id BIGINT UNSIGNED NOT NULL,
  target_language_code VARCHAR(35) NOT NULL,
  title VARCHAR(500) NOT NULL,
  summary TEXT NOT NULL,
  provider VARCHAR(50) NOT NULL,
  model VARCHAR(150) NOT NULL,
  prompt_version VARCHAR(80) NOT NULL,
  source_content_hash BINARY(32) NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
  created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  completed_at DATETIME(6) NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_editorial_translation_version (editorial_text_id, target_language_code, source_content_hash),
  KEY ix_editorial_translations_status_language (status, target_language_code),
  CONSTRAINT fk_editorial_translations_text FOREIGN KEY (editorial_text_id) REFERENCES editorial_texts(id) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO schema_migrations (version, description)
VALUES ('001_initial_schema', 'Esquema inicial de captura, publicaciones, análisis y textos editoriales')
ON DUPLICATE KEY UPDATE description = VALUES(description);

-- Fin de la migración inicial. Los catálogos semilla se incorporarán en una migración separada.
