-- ai_noticias — fuentes iniciales candidatas
-- Se registran en PAUSED: localizar un RSS no equivale a tener permiso de reutilización.
-- Activar cada canal solo después de revisar sus condiciones de uso.

USE osap_noticias;

INSERT INTO publishers (name, website_url, domain, country_code, description)
SELECT 'Library of Congress', 'https://www.loc.gov/', 'loc.gov', 'US',
       'Biblioteca del Congreso de Estados Unidos'
WHERE NOT EXISTS (SELECT 1 FROM publishers WHERE domain='loc.gov');

INSERT INTO publishers (name, website_url, domain, country_code, description)
SELECT 'Musicology Now', 'https://musicologynow.org/', 'musicologynow.org', 'US',
       'Publicación digital de la American Musicological Society'
WHERE NOT EXISTS (SELECT 1 FROM publishers WHERE domain='musicologynow.org');

INSERT INTO publishers (name, website_url, domain, country_code, description)
SELECT 'Scherzo', 'https://scherzo.es/', 'scherzo.es', 'ES',
       'Revista española de música clásica'
WHERE NOT EXISTS (SELECT 1 FROM publishers WHERE domain='scherzo.es');

INSERT INTO publishers (name, website_url, domain, country_code, description)
SELECT 'Beckmesser', 'https://www.beckmesser.com/', 'beckmesser.com', 'ES',
       'Publicación española de música clásica y ópera'
WHERE NOT EXISTS (SELECT 1 FROM publishers WHERE domain='beckmesser.com');

INSERT INTO publishers (name, website_url, domain, country_code, description)
SELECT 'Bachtrack', 'https://bachtrack.com/', 'bachtrack.com', 'GB',
       'Publicación internacional de música clásica, ópera y danza'
WHERE NOT EXISTS (SELECT 1 FROM publishers WHERE domain='bachtrack.com');

INSERT INTO publishers (name, website_url, domain, country_code, description)
SELECT 'Bibliothèque nationale de France', 'https://www.bnf.fr/', 'bnf.fr', 'FR',
       'Biblioteca nacional francesa; canal bibliográfico de partituras'
WHERE NOT EXISTS (SELECT 1 FROM publishers WHERE domain='bnf.fr');

INSERT INTO source_channels
(publisher_id, provider_name, name, url, url_sha256, protocol, format,
 declared_language, topic_hint, status, terms_url, usage_policy)
SELECT p.id, 'RSS', 'In the Muse', 'https://blogs.loc.gov/music/feed/',
       UNHEX(SHA2('https://blogs.loc.gov/music/feed/',256)), 'RSS', 'RSS2',
       'en', 'Colecciones musicales, patrimonio, adquisiciones y actividades',
       'PAUSED', 'https://www.loc.gov/subscribe/',
       'Pendiente de revisión de condiciones de uso y alcance de reutilización.'
FROM publishers p WHERE p.domain='loc.gov'
AND NOT EXISTS (SELECT 1 FROM source_channels s WHERE s.url_sha256=UNHEX(SHA2('https://blogs.loc.gov/music/feed/',256)));

INSERT INTO source_channels
(publisher_id, provider_name, name, url, url_sha256, protocol, format,
 declared_language, topic_hint, status, terms_url, usage_policy)
SELECT p.id, 'RSS', 'Musicology Now', 'https://musicologynow.org/feed/',
       UNHEX(SHA2('https://musicologynow.org/feed/',256)), 'RSS', 'RSS2',
       'en', 'Divulgación e investigación musicológica',
       'PAUSED', 'https://musicologynow.org/about-musicology-now/',
       'Pendiente de revisión de condiciones de uso y alcance de reutilización.'
FROM publishers p WHERE p.domain='musicologynow.org'
AND NOT EXISTS (SELECT 1 FROM source_channels s WHERE s.url_sha256=UNHEX(SHA2('https://musicologynow.org/feed/',256)));

INSERT INTO source_channels
(publisher_id, provider_name, name, url, url_sha256, protocol, format,
 declared_language, topic_hint, status, terms_url, usage_policy)
SELECT p.id, 'RSS', 'Scherzo', 'https://scherzo.es/feed',
       UNHEX(SHA2('https://scherzo.es/feed',256)), 'RSS', 'RSS2',
       'es', 'Música clásica, ópera y actualidad musical',
       'PAUSED', 'https://scherzo.es/',
       'Endpoint localizado; revisar términos del editor antes de activar.'
FROM publishers p WHERE p.domain='scherzo.es'
AND NOT EXISTS (SELECT 1 FROM source_channels s WHERE s.url_sha256=UNHEX(SHA2('https://scherzo.es/feed',256)));

INSERT INTO source_channels
(publisher_id, provider_name, name, url, url_sha256, protocol, format,
 declared_language, topic_hint, status, terms_url, usage_policy)
SELECT p.id, 'RSS', 'Beckmesser', 'https://www.beckmesser.com/feed',
       UNHEX(SHA2('https://www.beckmesser.com/feed',256)), 'RSS', 'RSS2',
       'es', 'Música clásica, ópera y crítica musical',
       'PAUSED', 'https://www.beckmesser.com/',
       'Endpoint localizado; revisar términos del editor antes de activar.'
FROM publishers p WHERE p.domain='beckmesser.com'
AND NOT EXISTS (SELECT 1 FROM source_channels s WHERE s.url_sha256=UNHEX(SHA2('https://www.beckmesser.com/feed',256)));

INSERT INTO source_channels
(publisher_id, provider_name, name, url, url_sha256, protocol, format,
 declared_language, topic_hint, status, terms_url, usage_policy)
SELECT p.id, 'RSS', 'Bachtrack - News', 'https://bachtrack.com/news.rss.xml',
       UNHEX(SHA2('https://bachtrack.com/news.rss.xml',256)), 'RSS', 'RSS2',
       'en', 'Noticias de música clásica, ópera, danza y actividad artística',
       'PAUSED', 'https://bachtrack.com/fr_FR/handler/documentation/view/ug-rss-feeds',
       'Feed oficial documentado; revisar términos de reutilización antes de activar.'
FROM publishers p WHERE p.domain='bachtrack.com'
AND NOT EXISTS (SELECT 1 FROM source_channels s WHERE s.url_sha256=UNHEX(SHA2('https://bachtrack.com/news.rss.xml',256)));

INSERT INTO source_channels
(publisher_id, provider_name, name, url, url_sha256, protocol, format,
 declared_language, topic_hint, status, terms_url, usage_policy)
SELECT p.id, 'RSS', 'Bibliographie nationale - Partitions', 'https://bibliographienationale.bnf.fr/rss/mus',
       UNHEX(SHA2('https://bibliographienationale.bnf.fr/rss/mus',256)), 'RSS', 'RSS2',
       'fr', 'Novedades bibliográficas y registros de partituras',
       'PAUSED', 'https://bibliographienationale.bnf.fr/content/rss',
       'Canal bibliográfico, no periodístico; revisar condiciones y uso de metadatos.'
FROM publishers p WHERE p.domain='bnf.fr'
AND NOT EXISTS (SELECT 1 FROM source_channels s WHERE s.url_sha256=UNHEX(SHA2('https://bibliographienationale.bnf.fr/rss/mus',256)));

INSERT INTO schema_migrations (version, description)
VALUES ('003_initial_source_candidates', 'Registro de seis canales RSS candidatos en estado PAUSED')
ON DUPLICATE KEY UPDATE description = VALUES(description);
