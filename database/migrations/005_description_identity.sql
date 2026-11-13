-- ai_noticias — huella de descripción para consolidar noticias entre fuentes
-- La huella se calcula en la aplicación sobre la descripción normalizada.
-- Los registros existentes quedan NULL hasta que vuelvan a capturarse.
-- Compatible con MariaDB 10.4; migración repetible.

USE osap_noticias;

ALTER TABLE news_publications
  ADD COLUMN IF NOT EXISTS description_sha256 BINARY(32) NULL AFTER description_original;

ALTER TABLE news_publications
  ADD INDEX IF NOT EXISTS ix_news_publications_description_hash (description_sha256);

INSERT INTO schema_migrations (version, description)
VALUES ('005_description_identity', 'Huella de descripción normalizada para identidad y consolidación entre fuentes')
ON DUPLICATE KEY UPDATE description = VALUES(description);
