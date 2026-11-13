-- ai_noticias — tipo de contenido predeterminado por canal
-- BnF Partitions es un canal bibliográfico. El valor es una pista de clasificación,
-- no una clasificación editorial validada ni una orden para ejecutar IA.

USE osap_noticias;

ALTER TABLE source_channels
  ADD COLUMN default_content_type_id BIGINT UNSIGNED NULL AFTER topic_hint,
  ADD KEY ix_source_channels_default_content_type (default_content_type_id),
  ADD CONSTRAINT fk_source_channels_default_content_type
    FOREIGN KEY (default_content_type_id) REFERENCES content_types(id)
    ON DELETE RESTRICT ON UPDATE RESTRICT;

UPDATE source_channels
SET default_content_type_id = (
  SELECT id FROM content_types WHERE code = 'BIBLIO' AND status = 'ACTIVE' LIMIT 1
)
WHERE id = 6
  AND url = 'https://bibliographienationale.bnf.fr/rss/mus';

INSERT INTO schema_migrations (version, description)
VALUES ('004_source_content_type_hints', 'Tipo de contenido predeterminado por canal')
ON DUPLICATE KEY UPDATE description = VALUES(description);
