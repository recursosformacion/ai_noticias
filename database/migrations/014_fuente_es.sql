-- ai_noticias — primera fuente musical en español bajo licencia abierta
--
-- El corpus no tenía ninguna noticia en español: las editoriales comerciales
-- consultadas (Scherzo, Doce Notas, Platea, Melómano, Codalario) prohíben
-- expresamente la reproducción sin autorización escrita, y la BNE bloquea el
-- acceso automatizado con HTTP 403.
--
-- TRANS - Revista Transcultural de Música (SIBE) publica sus artículos bajo
-- CC BY-NC-ND 2.5 España: permite copiar, distribuir y comunicar públicamente
-- citando autor y fuente, sin fines comerciales y sin obra derivada.
-- Verificado el 15-11-2026: feed válido con 10 elementos, en español.
--
-- Compatible con ejecuciones repetidas sobre MariaDB 10.4.
USE osap_noticias;
INSERT INTO publishers (
    name,
    website_url,
    domain,
    country_code,
    description
  )
SELECT 'SIBE - Sociedad de Etnomusicología',
  'https://www.sibetrans.com/',
  'sibetrans.com',
  'ES',
  'Sociedad Ibérica de Etnomusicología; edita TRANS, revista de musicología en acceso abierto.'
WHERE NOT EXISTS (
    SELECT 1
    FROM publishers
    WHERE domain = 'sibetrans.com'
  );
INSERT INTO source_channels (
    publisher_id,
    provider_name,
    name,
    url,
    url_sha256,
    protocol,
    format,
    declared_language,
    topic_hint,
    default_content_type_id,
    status,
    delivery_mode,
    terms_url,
    usage_policy,
    terms_reviewed_at
  )
SELECT p.id,
  'RSS',
  'TRANS - Revista Transcultural de Música',
  'https://www.sibetrans.com/trans/rss',
  UNHEX(SHA2('https://www.sibetrans.com/trans/rss', 256)),
  'RSS',
  'RSS2',
  'es',
  'Musicología, etnomusicología y músicas del mundo (SIBE)',
  (
    SELECT id
    FROM content_types
    WHERE code = 'RESEARCH'
    LIMIT 1
  ), 'ACTIVE', 'DAILY', 'https://www.sibetrans.com/trans/', 'CC BY-NC-ND 2.5 España: copia y distribución con atribución a autor y a TRANS; sin uso comercial ni obra derivada.', UTC_TIMESTAMP(6)
FROM publishers p
WHERE p.domain = 'sibetrans.com'
  AND NOT EXISTS (
    SELECT 1
    FROM source_channels s
    WHERE s.url_sha256 = UNHEX(SHA2('https://www.sibetrans.com/trans/rss', 256))
  );
-- LIMITACIÓN TÉCNICA VERIFICADA (15-11-2026): el feed de TRANS solo publica
-- <title>, <link>, <guid> y un <pubDate /> vacío. No trae descripción, y la
-- identidad de noticia se calcula con SHA-256 de la descripción normalizada;
-- sin ella el ítem no se puede registrar (regla del documento 05: no se inventa
-- una identidad alternativa). Se deja en MANUAL hasta que el editor publique
-- descripción o se decida una identidad basada en GUID para fuentes sin texto.
UPDATE source_channels
SET delivery_mode = 'MANUAL',
  usage_policy = 'CC BY-NC-ND 2.5 ES, pero el feed no incluye descripción: no se puede calcular la identidad de noticia. Pendiente de decisión de identidad por GUID.'
WHERE url = 'https://www.sibetrans.com/trans/rss';
INSERT INTO schema_migrations (version, description)
VALUES (
    '014_fuente_es',
    'TRANS (SIBE): registrada con licencia abierta, pendiente de identidad por falta de descripción'
  ) ON DUPLICATE KEY
UPDATE description =
VALUES(description);