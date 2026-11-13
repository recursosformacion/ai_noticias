-- ai_noticias — tipo de contenido predeterminado por canal
-- BnF Partitions es un canal bibliográfico: sus observaciones reciben BIBLIO
-- como pista de clasificación, sin convertir automáticamente la noticia en
-- una clasificación editorial validada por IA.

USE osap_noticias;

ALTER TABLE source_channels
  ADD COLUMN default_content_type_id BIGINT UNSIGNED NULL AFTER topic_hint,
  ADD KEY ix_source_channels_default_content_type (default_content_type_id),
  ADD CONSTRAINT fk_source_channels_default_content_type
    FOREIGN KEY (default_content_type_id) REFERENCES content_types(id)
    ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE source_observations
  ADD COLUMN content_type_hint_id BIGINT UNSIGNED NULL AFTER declared_language,
  ADD KEY ix_source_observations_content_type_hint (content_type_hint_id),
  ADD CONSTRAINT fk_source_observations_content_type_hint
    FOREIGN KEY (content_type_hint_id) REFERENCES content_types(id)
    ON DELETE RESTRICT ON UPDATE RESTRICT;

UPDATE source_channels
SET default_content_type_id = (
  SELECT id FROM content_types WHERE code = 'BIBLIO' AND status = 'ACTIVE' LIMIT 1
)
WHERE id = 6
  AND url = 'https://bibliographienationale.bnf.fr/rss/mus';

INSERT INTO schema_migrations (version, description)
VALUES ('004_source_content_type_hints', 'Pistas de tipo de contenido por canal y observación')
ON DUPLICATE KEY UPDATE description = VALUES(description);
