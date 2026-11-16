-- ai_noticias — corpus musical real para el módulo de correo
--
-- La prueba del módulo reveló que el corpus no contenía noticias musicales:
--   * PLOS ONE y Frontiers son repositorios generalistas (estudios médicos).
--   * DOAJ entrega metadatos de revistas, no noticias.
--   * No había ninguna fuente en español activa.
--   * El canal más rico (BnF - Bibliographie Partitions) seguía en PAUSED y la
--     migración 007 creó un «Musicology Now» duplicado (id 25).
--
-- Esta migración:
--   1. Elimina el duplicado de Musicology Now (id 25, sin datos).
--   2. Reactiva BnF - Partitions como canal de novedades musicales.
--   3. Degrada a MANUAL los canales generalistas que solo aportaban ruido.
--   4. Mantiene el criterio de licencia: solo se activa lo que puede reutilizarse.
--
-- Compatible con ejecuciones repetidas sobre MariaDB 10.4.
USE osap_noticias;
-- 1) Duplicado creado por la 007 (misma URL que el canal 22, sin capturas).
DELETE s
FROM source_channels s
WHERE s.id = 25
  AND s.status = 'PAUSED'
  AND NOT EXISTS (
    SELECT 1
    FROM source_observations o
    WHERE o.source_channel_id = s.id
  );
-- 2) BnF - Bibliographie nationale / Partitions: metadatos bajo Licence Ouverte,
--    contenido estrictamente musical. Vuelve a estar disponible para entrega.
UPDATE source_channels
SET status = 'ACTIVE',
  delivery_mode = 'DAILY',
  terms_reviewed_at = COALESCE(terms_reviewed_at, UTC_TIMESTAMP(6)),
  usage_policy = 'Metadatos bibliográficos bajo Licence Ouverte 2.0. Contenido musical especializado; conservar fuente y fecha de recuperación.'
WHERE url = 'https://bibliographienationale.bnf.fr/rss/mus';
-- 3) Generalistas con poco valor musical: se conservan pero no se envían.
UPDATE source_channels
SET delivery_mode = 'MANUAL'
WHERE url IN (
    'https://journals.plos.org/plosone/feed/atom',
    'https://www.frontiersin.org/journals/psychology/rss',
    'https://doaj.org/feed'
  );
-- 4) Fuentes musicales que sí aportan actualidad musical.
UPDATE source_channels
SET delivery_mode = 'DAILY'
WHERE url IN (
    'https://bibliographienationale.bnf.fr/rss/mus',
    'https://www.bnf.fr/fr/actualites/rss',
    'https://blogs.loc.gov/music/feed/',
    'https://bibliolore.org/feed/'
  );

-- 5) Blog académico de musicología digital (OpenEdition/Hypothèses): contenido
--    especializado y feed verificado el 15-11-2026.
INSERT INTO publishers (name, website_url, domain, country_code, description)
SELECT 'Consortium Musica*', 'https://musica.hypotheses.org/', 'hypotheses.org', 'FR',
       'Blog de musicología digital alojado en OpenEdition (Hypothèses).'
WHERE NOT EXISTS (SELECT 1 FROM publishers WHERE domain='hypotheses.org');

INSERT INTO source_channels
(publisher_id, provider_name, name, url, url_sha256, protocol, format,
 declared_language, topic_hint, default_content_type_id, status, delivery_mode,
 terms_url, usage_policy, terms_reviewed_at)
SELECT p.id, 'RSS', 'Musica* - Musicología digital', 'https://musica.hypotheses.org/feed',
       UNHEX(SHA2('https://musica.hypotheses.org/feed',256)), 'RSS', 'RSS2',
       'fr', 'Musicología digital, congresos, jornadas y proyectos de investigación',
       (SELECT id FROM content_types WHERE code='RESEARCH' LIMIT 1),
       'ACTIVE', 'DAILY', 'https://musica.hypotheses.org/',
       'Blog académico en plataforma abierta; citar autor, título y enlace original.',
       UTC_TIMESTAMP(6)
FROM publishers p WHERE p.domain='hypotheses.org'
AND NOT EXISTS (SELECT 1 FROM source_channels s WHERE s.url_sha256=UNHEX(SHA2('https://musica.hypotheses.org/feed',256)));

INSERT INTO schema_migrations (version, description)
VALUES (
    '012_corpus_musical',
    'Corrige el corpus del módulo: duplicado, BnF Partitions activo y generalistas en MANUAL'
  ) ON DUPLICATE KEY
UPDATE description =
VALUES(description);