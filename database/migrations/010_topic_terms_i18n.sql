-- ai_noticias — términos multilingües de los temas semilla
--
-- Sin esto, un tema como «ópera» solo encontraba noticias escritas en español:
-- las fuentes en inglés y francés usan otras palabras. Cada fila es un término
-- y su idioma; el buscador los aplica según el idioma de la respuesta.
--
-- Compatible con ejecuciones repetidas sobre MariaDB 10.4.
USE osap_noticias;
CREATE TABLE IF NOT EXISTS interest_topic_terms (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  interest_topic_id BIGINT UNSIGNED NOT NULL,
  language_code VARCHAR(8) NOT NULL,
  term VARCHAR(160) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_interest_topic_terms (interest_topic_id, language_code, term),
  KEY ix_interest_topic_terms_lang (language_code, term),
  CONSTRAINT fk_interest_topic_terms_topic FOREIGN KEY (interest_topic_id) REFERENCES interest_topics(id) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
-- Términos por tema e idioma. Solo en y fr: el español ya está en keywords_json.
INSERT INTO interest_topic_terms (interest_topic_id, language_code, term)
SELECT t.id,
  v.lang,
  v.term
FROM interest_topics t
  JOIN (
    SELECT 'clasica' code,
      'en' lang,
      'classical music' term
    UNION ALL
    SELECT 'clasica',
      'en',
      'orchestra'
    UNION ALL
    SELECT 'clasica',
      'en',
      'symphony'
    UNION ALL
    SELECT 'clasica',
      'en',
      'opera'
    UNION ALL
    SELECT 'clasica',
      'en',
      'composer'
    UNION ALL
    SELECT 'clasica',
      'en',
      'conductor'
    UNION ALL
    SELECT 'clasica',
      'en',
      'recital'
    UNION ALL
    SELECT 'clasica',
      'en',
      'concert hall'
    UNION ALL
    SELECT 'clasica',
      'fr',
      'musique classique'
    UNION ALL
    SELECT 'clasica',
      'fr',
      'orchestre'
    UNION ALL
    SELECT 'clasica',
      'fr',
      'symphonique'
    UNION ALL
    SELECT 'clasica',
      'fr',
      'opéra'
    UNION ALL
    SELECT 'clasica',
      'fr',
      'compositeur'
    UNION ALL
    SELECT 'clasica',
      'fr',
      'chef d''orchestre'
    UNION ALL
    SELECT 'clasica',
      'fr',
      'concert'
    UNION ALL
    SELECT 'sacra',
      'en',
      'sacred music'
    UNION ALL
    SELECT 'sacra',
      'en',
      'choral'
    UNION ALL
    SELECT 'sacra',
      'en',
      'choir'
    UNION ALL
    SELECT 'sacra',
      'en',
      'organ'
    UNION ALL
    SELECT 'sacra',
      'en',
      'hymn'
    UNION ALL
    SELECT 'sacra',
      'en',
      'requiem'
    UNION ALL
    SELECT 'sacra',
      'fr',
      'musique sacrée'
    UNION ALL
    SELECT 'sacra',
      'fr',
      'chœur'
    UNION ALL
    SELECT 'sacra',
      'fr',
      'choral'
    UNION ALL
    SELECT 'sacra',
      'fr',
      'orgue'
    UNION ALL
    SELECT 'sacra',
      'fr',
      'hymne'
    UNION ALL
    SELECT 'patrimonio',
      'en',
      'heritage'
    UNION ALL
    SELECT 'patrimonio',
      'en',
      'archive'
    UNION ALL
    SELECT 'patrimonio',
      'en',
      'manuscript'
    UNION ALL
    SELECT 'patrimonio',
      'en',
      'score'
    UNION ALL
    SELECT 'patrimonio',
      'en',
      'sheet music'
    UNION ALL
    SELECT 'patrimonio',
      'en',
      'digitization'
    UNION ALL
    SELECT 'patrimonio',
      'en',
      'library'
    UNION ALL
    SELECT 'patrimonio',
      'en',
      'collection'
    UNION ALL
    SELECT 'patrimonio',
      'fr',
      'patrimoine'
    UNION ALL
    SELECT 'patrimonio',
      'fr',
      'archives'
    UNION ALL
    SELECT 'patrimonio',
      'fr',
      'manuscrit'
    UNION ALL
    SELECT 'patrimonio',
      'fr',
      'partition'
    UNION ALL
    SELECT 'patrimonio',
      'fr',
      'numérisation'
    UNION ALL
    SELECT 'patrimonio',
      'fr',
      'bibliothèque'
    UNION ALL
    SELECT 'patrimonio',
      'fr',
      'collection'
    UNION ALL
    SELECT 'investigacion',
      'en',
      'musicology'
    UNION ALL
    SELECT 'investigacion',
      'en',
      'research'
    UNION ALL
    SELECT 'investigacion',
      'en',
      'study'
    UNION ALL
    SELECT 'investigacion',
      'en',
      'ethnomusicology'
    UNION ALL
    SELECT 'investigacion',
      'en',
      'journal article'
    UNION ALL
    SELECT 'investigacion',
      'en',
      'scholarship'
    UNION ALL
    SELECT 'investigacion',
      'fr',
      'musicologie'
    UNION ALL
    SELECT 'investigacion',
      'fr',
      'recherche'
    UNION ALL
    SELECT 'investigacion',
      'fr',
      'étude'
    UNION ALL
    SELECT 'investigacion',
      'fr',
      'ethnomusicologie'
    UNION ALL
    SELECT 'jazz',
      'en',
      'jazz'
    UNION ALL
    SELECT 'jazz',
      'en',
      'blues'
    UNION ALL
    SELECT 'jazz',
      'en',
      'swing'
    UNION ALL
    SELECT 'jazz',
      'en',
      'improvisation'
    UNION ALL
    SELECT 'jazz',
      'en',
      'big band'
    UNION ALL
    SELECT 'jazz',
      'fr',
      'jazz'
    UNION ALL
    SELECT 'jazz',
      'fr',
      'blues'
    UNION ALL
    SELECT 'jazz',
      'fr',
      'improvisation'
    UNION ALL
    SELECT 'popular',
      'en',
      'rock'
    UNION ALL
    SELECT 'popular',
      'en',
      'pop music'
    UNION ALL
    SELECT 'popular',
      'en',
      'metal'
    UNION ALL
    SELECT 'popular',
      'en',
      'indie'
    UNION ALL
    SELECT 'popular',
      'en',
      'band'
    UNION ALL
    SELECT 'popular',
      'en',
      'album'
    UNION ALL
    SELECT 'popular',
      'en',
      'tour'
    UNION ALL
    SELECT 'popular',
      'fr',
      'rock'
    UNION ALL
    SELECT 'popular',
      'fr',
      'pop'
    UNION ALL
    SELECT 'popular',
      'fr',
      'groupe'
    UNION ALL
    SELECT 'popular',
      'fr',
      'album'
    UNION ALL
    SELECT 'popular',
      'fr',
      'tournée'
    UNION ALL
    SELECT 'urbana',
      'en',
      'hip hop'
    UNION ALL
    SELECT 'urbana',
      'en',
      'rap'
    UNION ALL
    SELECT 'urbana',
      'en',
      'reggaeton'
    UNION ALL
    SELECT 'urbana',
      'en',
      'latin music'
    UNION ALL
    SELECT 'urbana',
      'fr',
      'hip hop'
    UNION ALL
    SELECT 'urbana',
      'fr',
      'rap'
    UNION ALL
    SELECT 'electronica',
      'en',
      'electronic music'
    UNION ALL
    SELECT 'electronica',
      'en',
      'techno'
    UNION ALL
    SELECT 'electronica',
      'en',
      'experimental'
    UNION ALL
    SELECT 'electronica',
      'en',
      'synthesizer'
    UNION ALL
    SELECT 'electronica',
      'fr',
      'musique électronique'
    UNION ALL
    SELECT 'electronica',
      'fr',
      'expérimental'
    UNION ALL
    SELECT 'tradicional',
      'en',
      'folk'
    UNION ALL
    SELECT 'tradicional',
      'en',
      'traditional music'
    UNION ALL
    SELECT 'tradicional',
      'en',
      'world music'
    UNION ALL
    SELECT 'tradicional',
      'en',
      'folklore'
    UNION ALL
    SELECT 'tradicional',
      'fr',
      'musique traditionnelle'
    UNION ALL
    SELECT 'tradicional',
      'fr',
      'folklore'
    UNION ALL
    SELECT 'tradicional',
      'fr',
      'musiques du monde'
    UNION ALL
    SELECT 'industria',
      'en',
      'music industry'
    UNION ALL
    SELECT 'industria',
      'en',
      'record label'
    UNION ALL
    SELECT 'industria',
      'en',
      'streaming'
    UNION ALL
    SELECT 'industria',
      'en',
      'copyright'
    UNION ALL
    SELECT 'industria',
      'en',
      'licensing'
    UNION ALL
    SELECT 'industria',
      'en',
      'royalties'
    UNION ALL
    SELECT 'industria',
      'fr',
      'industrie musicale'
    UNION ALL
    SELECT 'industria',
      'fr',
      'label'
    UNION ALL
    SELECT 'industria',
      'fr',
      'streaming'
    UNION ALL
    SELECT 'industria',
      'fr',
      'droit d''auteur'
    UNION ALL
    SELECT 'educacion',
      'en',
      'music education'
    UNION ALL
    SELECT 'educacion',
      'en',
      'conservatory'
    UNION ALL
    SELECT 'educacion',
      'en',
      'teaching'
    UNION ALL
    SELECT 'educacion',
      'en',
      'workshop'
    UNION ALL
    SELECT 'educacion',
      'fr',
      'éducation musicale'
    UNION ALL
    SELECT 'educacion',
      'fr',
      'conservatoire'
    UNION ALL
    SELECT 'educacion',
      'fr',
      'enseignement'
    UNION ALL
    SELECT 'agenda',
      'en',
      'festival'
    UNION ALL
    SELECT 'agenda',
      'en',
      'season'
    UNION ALL
    SELECT 'agenda',
      'en',
      'concert'
    UNION ALL
    SELECT 'agenda',
      'en',
      'performance'
    UNION ALL
    SELECT 'agenda',
      'fr',
      'festival'
    UNION ALL
    SELECT 'agenda',
      'fr',
      'saison'
    UNION ALL
    SELECT 'agenda',
      'fr',
      'concert'
    UNION ALL
    SELECT 'agenda',
      'fr',
      'spectacle'
  ) v ON v.code = t.code ON DUPLICATE KEY
UPDATE term =
VALUES(term);
INSERT INTO schema_migrations (version, description)
VALUES (
    '010_topic_terms_i18n',
    'Términos multilingües (en/fr) de los temas semilla'
  ) ON DUPLICATE KEY
UPDATE description =
VALUES(description);