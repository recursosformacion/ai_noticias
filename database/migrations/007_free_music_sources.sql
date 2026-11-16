-- ai_noticias — catálogo de fuentes de libre difusión
-- Revisado y comprobado técnicamente el 15-11-2026 con petición HTTP real.
--
-- Criterio de esta migración: solo se activan (ACTIVE) canales cuyo contenido se
-- publica bajo dominio público, CC0, CC BY, licencia abierta equivalente o Open
-- Access explícito. Los canales cuya reutilización no está autorizada
-- (Scherzo, Beckmesser, Bachtrack, Musicology Now, MBW, NPR) se registran en
-- PAUSED y NO se activan: localizar un RSS no equivale a tener permiso.
--
-- Compatible con ejecuciones repetidas sobre MariaDB 10.4.
USE osap_noticias;
-- ---------- Editoriales ----------
INSERT INTO publishers (
        name,
        website_url,
        domain,
        country_code,
        description
    )
SELECT 'Library of Congress',
    'https://www.loc.gov/',
    'loc.gov',
    'US',
    'Biblioteca del Congreso de Estados Unidos. Textos de blogs del personal reutilizables con atribución (dominio público US).'
WHERE NOT EXISTS (
        SELECT 1
        FROM publishers
        WHERE domain = 'loc.gov'
    );
INSERT INTO publishers (
        name,
        website_url,
        domain,
        country_code,
        description
    )
SELECT 'Bibliothèque nationale de France',
    'https://www.bnf.fr/',
    'bnf.fr',
    'FR',
    'Biblioteca nacional francesa. Metadatos bajo Licence Ouverte 2.0 (Etalab).'
WHERE NOT EXISTS (
        SELECT 1
        FROM publishers
        WHERE domain = 'bnf.fr'
    );
INSERT INTO publishers (
        name,
        website_url,
        domain,
        country_code,
        description
    )
SELECT 'Wikimedia Foundation',
    'https://wikimediafoundation.org/',
    'wikimedia.org',
    'US',
    'Proyectos Wikimedia: Wikipedia y Wikisource bajo CC BY-SA (texto disponible también bajo CC0 en fuentes primarias).'
WHERE NOT EXISTS (
        SELECT 1
        FROM publishers
        WHERE domain = 'wikimedia.org'
    );
INSERT INTO publishers (
        name,
        website_url,
        domain,
        country_code,
        description
    )
SELECT 'Wikimedia Foundation',
    'https://wikimediafoundation.org/',
    'wikisource.org',
    'US',
    'Wikisource: textos y partituras libres con licencia CC BY-SA o dominio público.'
WHERE NOT EXISTS (
        SELECT 1
        FROM publishers
        WHERE domain = 'wikisource.org'
    );
INSERT INTO publishers (
        name,
        website_url,
        domain,
        country_code,
        description
    )
SELECT 'Internet Archive',
    'https://archive.org/',
    'archive.org',
    'US',
    'Biblioteca digital sin ánimo de lucro; fondos de audio de dominio público y Open Library.'
WHERE NOT EXISTS (
        SELECT 1
        FROM publishers
        WHERE domain = 'archive.org'
    );
INSERT INTO publishers (
        name,
        website_url,
        domain,
        country_code,
        description
    )
SELECT 'MetaBrainz Foundation',
    'https://metabrainz.org/',
    'metabrainz.org',
    'US',
    'Fundación sin ánimo de lucro: MusicBrainz, ListenBrainz y AcousticBrainz. Datos y blog CC0/CC BY-NC-SA.'
WHERE NOT EXISTS (
        SELECT 1
        FROM publishers
        WHERE domain = 'metabrainz.org'
    );
INSERT INTO publishers (
        name,
        website_url,
        domain,
        country_code,
        description
    )
SELECT 'MetaBrainz Foundation',
    'https://metabrainz.org/',
    'musicbrainz.org',
    'US',
    'Base de datos musical abierta, datos bajo CC0 y contenido extra bajo CC BY-NC-SA.'
WHERE NOT EXISTS (
        SELECT 1
        FROM publishers
        WHERE domain = 'musicbrainz.org'
    );
INSERT INTO publishers (
        name,
        website_url,
        domain,
        country_code,
        description
    )
SELECT 'Répertoire International de Littérature Musicale',
    'https://www.rilm.org/',
    'bibliolore.org',
    'US',
    'RILM. Blog Bibliolore de investigación musical; contenidos divulgativos académicos.'
WHERE NOT EXISTS (
        SELECT 1
        FROM publishers
        WHERE domain = 'bibliolore.org'
    );
INSERT INTO publishers (
        name,
        website_url,
        domain,
        country_code,
        description
    )
SELECT 'Directory of Open Access Journals',
    'https://doaj.org/',
    'doaj.org',
    'SE',
    'Índice de revistas de acceso abierto. Metadatos publicados bajo CC0.'
WHERE NOT EXISTS (
        SELECT 1
        FROM publishers
        WHERE domain = 'doaj.org'
    );
INSERT INTO publishers (
        name,
        website_url,
        domain,
        country_code,
        description
    )
SELECT 'Public Library of Science',
    'https://plos.org/',
    'plos.org',
    'US',
    'Editorial científica Open Access; artículos bajo CC BY 4.0.'
WHERE NOT EXISTS (
        SELECT 1
        FROM publishers
        WHERE domain = 'plos.org'
    );
INSERT INTO publishers (
        name,
        website_url,
        domain,
        country_code,
        description
    )
SELECT 'Frontiers Media',
    'https://www.frontiersin.org/',
    'frontiersin.org',
    'CH',
    'Editorial científica Open Access; artículos bajo CC BY 4.0.'
WHERE NOT EXISTS (
        SELECT 1
        FROM publishers
        WHERE domain = 'frontiersin.org'
    );
INSERT INTO publishers (
        name,
        website_url,
        domain,
        country_code,
        description
    )
SELECT 'National Archives and Records Administration',
    'https://www.archives.gov/',
    'archives.gov',
    'US',
    'Archivo Nacional de Estados Unidos. Contenido del Gobierno federal, dominio público.'
WHERE NOT EXISTS (
        SELECT 1
        FROM publishers
        WHERE domain = 'archives.gov'
    );
-- Canales cuya reutilización está restringida: se registran para no perder el
-- inventario, pero permanecen PAUSED y no se capturan.
INSERT INTO publishers (
        name,
        website_url,
        domain,
        country_code,
        description
    )
SELECT 'Scherzo',
    'https://scherzo.es/',
    'scherzo.es',
    'ES',
    'Revista española de música clásica. Requiere autorización escrita.'
WHERE NOT EXISTS (
        SELECT 1
        FROM publishers
        WHERE domain = 'scherzo.es'
    );
INSERT INTO publishers (
        name,
        website_url,
        domain,
        country_code,
        description
    )
SELECT 'Beckmesser',
    'https://www.beckmesser.com/',
    'beckmesser.com',
    'ES',
    'Publicación española de música clásica y ópera. Todos los derechos reservados.'
WHERE NOT EXISTS (
        SELECT 1
        FROM publishers
        WHERE domain = 'beckmesser.com'
    );
INSERT INTO publishers (
        name,
        website_url,
        domain,
        country_code,
        description
    )
SELECT 'Bachtrack',
    'https://bachtrack.com/',
    'bachtrack.com',
    'GB',
    'Publicación internacional de música clásica, ópera y danza. Uso personal; automatización restringida.'
WHERE NOT EXISTS (
        SELECT 1
        FROM publishers
        WHERE domain = 'bachtrack.com'
    );
INSERT INTO publishers (
        name,
        website_url,
        domain,
        country_code,
        description
    )
SELECT 'Musicology Now',
    'https://musicologynow.org/',
    'musicologynow.org',
    'US',
    'Publicación digital de la American Musicological Society. Sin licencia general de reutilización.'
WHERE NOT EXISTS (
        SELECT 1
        FROM publishers
        WHERE domain = 'musicologynow.org'
    );
INSERT INTO publishers (
        name,
        website_url,
        domain,
        country_code,
        description
    )
SELECT 'Music Business Worldwide',
    'https://www.musicbusinessworldwide.com/',
    'musicbusinessworldwide.com',
    'GB',
    'Industria musical internacional. Uso personal no comercial.'
WHERE NOT EXISTS (
        SELECT 1
        FROM publishers
        WHERE domain = 'musicbusinessworldwide.com'
    );
INSERT INTO publishers (
        name,
        website_url,
        domain,
        country_code,
        description
    )
SELECT 'NPR',
    'https://www.npr.org/',
    'npr.org',
    'US',
    'NPR Music. Prohíbe el uso de sus contenidos para sistemas de IA sin permiso escrito.'
WHERE NOT EXISTS (
        SELECT 1
        FROM publishers
        WHERE domain = 'npr.org'
    );
-- ---------- Canales de libre difusión (ACTIVE) ----------
-- Formato: (dominio, nombre, url, idioma, tipo_contenido, pista_temática, política)
-- Library of Congress
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
        terms_url,
        usage_policy,
        terms_reviewed_at
    )
SELECT p.id,
    'RSS',
    'LOC - In the Muse',
    'https://blogs.loc.gov/music/feed/',
    UNHEX(SHA2('https://blogs.loc.gov/music/feed/', 256)),
    'RSS',
    'RSS2',
    'en',
    'Colecciones musicales, patrimonio, adquisiciones y actividades',
    (
        SELECT id
        FROM content_types
        WHERE code = 'NEWS'
        LIMIT 1
    ), 'ACTIVE', 'https://blogs.loc.gov/about/', 'Blogs de personal LOC: reutilización permitida con atribución al autor y a la institución (dominio público US). No reutilizar imágenes.', UTC_TIMESTAMP(6)
FROM publishers p
WHERE p.domain = 'loc.gov'
    AND NOT EXISTS (
        SELECT 1
        FROM source_channels s
        WHERE s.url_sha256 = UNHEX(SHA2('https://blogs.loc.gov/music/feed/', 256))
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
        terms_url,
        usage_policy,
        terms_reviewed_at
    )
SELECT p.id,
    'RSS',
    'LOC - NLS Music Notes',
    'https://blogs.loc.gov/nls-music-notes/feed/',
    UNHEX(
        SHA2(
            'https://blogs.loc.gov/nls-music-notes/feed/',
            256
        )
    ),
    'RSS',
    'RSS2',
    'en',
    'Música accesible: braille, audio y formatos alternativos',
    (
        SELECT id
        FROM content_types
        WHERE code = 'NEWS'
        LIMIT 1
    ), 'ACTIVE', 'https://blogs.loc.gov/about/', 'Blog de personal LOC; atribución obligatoria. No reutilizar imágenes.', UTC_TIMESTAMP(6)
FROM publishers p
WHERE p.domain = 'loc.gov'
    AND NOT EXISTS (
        SELECT 1
        FROM source_channels s
        WHERE s.url_sha256 = UNHEX(
                SHA2(
                    'https://blogs.loc.gov/nls-music-notes/feed/',
                    256
                )
            )
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
        terms_url,
        usage_policy,
        terms_reviewed_at
    )
SELECT p.id,
    'RSS',
    'LOC - Concerts & Performing Arts',
    'https://www.loc.gov/rss/music/concerts.xml',
    UNHEX(
        SHA2('https://www.loc.gov/rss/music/concerts.xml', 256)
    ),
    'RSS',
    'RSS2',
    'en',
    'Agenda de conciertos, conferencias y actividades escénicas',
    (
        SELECT id
        FROM content_types
        WHERE code = 'EVENT'
        LIMIT 1
    ), 'ACTIVE', 'https://www.loc.gov/legal/', 'Contenido del Gobierno federal de EE. UU. en dominio público. Canal de agenda, no de noticias.', UTC_TIMESTAMP(6)
FROM publishers p
WHERE p.domain = 'loc.gov'
    AND NOT EXISTS (
        SELECT 1
        FROM source_channels s
        WHERE s.url_sha256 = UNHEX(
                SHA2('https://www.loc.gov/rss/music/concerts.xml', 256)
            )
    );
-- Bibliothèque nationale de France
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
        terms_url,
        usage_policy,
        terms_reviewed_at
    )
SELECT p.id,
    'RSS',
    'BnF - Actualités',
    'https://www.bnf.fr/fr/actualites/rss',
    UNHEX(SHA2('https://www.bnf.fr/fr/actualites/rss', 256)),
    'RSS',
    'RSS2',
    'fr',
    'Actualidad institucional de la BnF; requiere filtrado temático musical',
    (
        SELECT id
        FROM content_types
        WHERE code = 'NEWS'
        LIMIT 1
    ), 'ACTIVE', 'https://www.bnf.fr/fr/conditions-de-reutilisations-des-donnees-de-la-bnf', 'Metadatos y contenidos institucionales bajo Licence Ouverte 2.0; conservar fuente y fecha de recuperación.', UTC_TIMESTAMP(6)
FROM publishers p
WHERE p.domain = 'bnf.fr'
    AND NOT EXISTS (
        SELECT 1
        FROM source_channels s
        WHERE s.url_sha256 = UNHEX(SHA2('https://www.bnf.fr/fr/actualites/rss', 256))
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
        terms_url,
        usage_policy,
        terms_reviewed_at
    )
SELECT p.id,
    'RSS',
    'BnF - Bibliographie nationale / Partitions',
    'https://bibliographienationale.bnf.fr/rss/mus',
    UNHEX(
        SHA2(
            'https://bibliographienationale.bnf.fr/rss/mus',
            256
        )
    ),
    'RSS',
    'RSS2',
    'fr',
    'Novedades bibliográficas y registros de partituras',
    (
        SELECT id
        FROM content_types
        WHERE code = 'BIBLIO'
        LIMIT 1
    ), 'ACTIVE', 'https://bibliographienationale.bnf.fr/content/rss', 'Metadatos bibliográficos bajo Licence Ouverte. Registros de catálogo, no noticias periodísticas.', UTC_TIMESTAMP(6)
FROM publishers p
WHERE p.domain = 'bnf.fr'
    AND NOT EXISTS (
        SELECT 1
        FROM source_channels s
        WHERE s.url_sha256 = UNHEX(
                SHA2(
                    'https://bibliographienationale.bnf.fr/rss/mus',
                    256
                )
            )
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
        terms_url,
        usage_policy,
        terms_reviewed_at
    )
SELECT p.id,
    'RSS',
    'BnF - Bibliographie nationale / Son',
    'https://bibliographienationale.bnf.fr/rss/son',
    UNHEX(
        SHA2(
            'https://bibliographienationale.bnf.fr/rss/son',
            256
        )
    ),
    'RSS',
    'RSS2',
    'fr',
    'Novedades bibliográficas de registros sonoros',
    (
        SELECT id
        FROM content_types
        WHERE code = 'BIBLIO'
        LIMIT 1
    ), 'ACTIVE', 'https://bibliographienationale.bnf.fr/content/rss', 'Metadatos bibliográficos bajo Licence Ouverte. Registros de catálogo, no noticias periodísticas.', UTC_TIMESTAMP(6)
FROM publishers p
WHERE p.domain = 'bnf.fr'
    AND NOT EXISTS (
        SELECT 1
        FROM source_channels s
        WHERE s.url_sha256 = UNHEX(
                SHA2(
                    'https://bibliographienationale.bnf.fr/rss/son',
                    256
                )
            )
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
        terms_url,
        usage_policy,
        terms_reviewed_at
    )
SELECT p.id,
    'RSS',
    'BnF - Agenda',
    'https://www.bnf.fr/fr/agenda/rss',
    UNHEX(SHA2('https://www.bnf.fr/fr/agenda/rss', 256)),
    'RSS',
    'RSS2',
    'fr',
    'Agenda cultural y musical de la BnF (feed completo, sin filtro temático)',
    (
        SELECT id
        FROM content_types
        WHERE code = 'EVENT'
        LIMIT 1
    ), 'ACTIVE', 'https://www.bnf.fr/fr/conditions-de-reutilisations-des-donnees-de-la-bnf', 'Licence Ouverte 2.0. El feed devuelve hasta 200 entradas de toda la agenda: exige filtrado musical.', UTC_TIMESTAMP(6)
FROM publishers p
WHERE p.domain = 'bnf.fr'
    AND NOT EXISTS (
        SELECT 1
        FROM source_channels s
        WHERE s.url_sha256 = UNHEX(SHA2('https://www.bnf.fr/fr/agenda/rss', 256))
    );
-- Wikimedia: Wikisource
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
        terms_url,
        usage_policy,
        terms_reviewed_at
    )
SELECT p.id,
    'Atom',
    'Wikisource ES - Cambios recientes',
    'https://es.wikisource.org/w/index.php?title=Especial:CambiosRecientes&feed=atom&namespace=0',
    UNHEX(
        SHA2(
            'https://es.wikisource.org/w/index.php?title=Especial:CambiosRecientes&feed=atom&namespace=0',
            256
        )
    ),
    'ATOM',
    'Atom',
    'es',
    'Textos y partituras libres en español (incluye dominio público)',
    (
        SELECT id
        FROM content_types
        WHERE code = 'COLLECTION'
        LIMIT 1
    ), 'ACTIVE', 'https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use/es', 'Contenido bajo CC BY-SA 4.0 o dominio público. Requiere atribución y compartir igual. Canal de cambios, exige filtrado musical.', UTC_TIMESTAMP(6)
FROM publishers p
WHERE p.domain = 'wikisource.org'
    AND NOT EXISTS (
        SELECT 1
        FROM source_channels s
        WHERE s.url_sha256 = UNHEX(
                SHA2(
                    'https://es.wikisource.org/w/index.php?title=Especial:CambiosRecientes&feed=atom&namespace=0',
                    256
                )
            )
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
        terms_url,
        usage_policy,
        terms_reviewed_at
    )
SELECT p.id,
    'Atom',
    'Wikipedia EN - Revisión del artículo Music',
    'https://en.wikipedia.org/w/index.php?title=Music&action=history&feed=atom',
    UNHEX(
        SHA2(
            'https://en.wikipedia.org/w/index.php?title=Music&action=history&feed=atom',
            256
        )
    ),
    'ATOM',
    'Atom',
    'en',
    'Historial de ediciones del artículo Music (referencia enciclopédica)',
    (
        SELECT id
        FROM content_types
        WHERE code = 'OTHER'
        LIMIT 1
    ), 'ACTIVE', 'https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use', 'CC BY-SA 4.0. Canal de cambios de una única página: úsese como referencia, no como noticia.', UTC_TIMESTAMP(6)
FROM publishers p
WHERE p.domain = 'wikimedia.org'
    AND NOT EXISTS (
        SELECT 1
        FROM source_channels s
        WHERE s.url_sha256 = UNHEX(
                SHA2(
                    'https://en.wikipedia.org/w/index.php?title=Music&action=history&feed=atom',
                    256
                )
            )
    );
-- Internet Archive
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
        terms_url,
        usage_policy,
        terms_reviewed_at
    )
SELECT p.id,
    'RSS',
    'Internet Archive - Audio de dominio público',
    'https://archive.org/services/collection-rss.php?collection=opensource_audio',
    UNHEX(
        SHA2(
            'https://archive.org/services/collection-rss.php?collection=opensource_audio',
            256
        )
    ),
    'RSS',
    'RSS2',
    'en',
    'Nuevos audios subidos a la colección opensource_audio',
    (
        SELECT id
        FROM content_types
        WHERE code = 'COLLECTION'
        LIMIT 1
    ), 'ACTIVE', 'https://archive.org/about/terms.php', 'Fondos de dominio público y licencias abiertas. Comprobar licencia por ítem antes de reutilizar.', UTC_TIMESTAMP(6)
FROM publishers p
WHERE p.domain = 'archive.org'
    AND NOT EXISTS (
        SELECT 1
        FROM source_channels s
        WHERE s.url_sha256 = UNHEX(
                SHA2(
                    'https://archive.org/services/collection-rss.php?collection=opensource_audio',
                    256
                )
            )
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
        terms_url,
        usage_policy,
        terms_reviewed_at
    )
SELECT p.id,
    'RSS',
    'Open Library Blog',
    'https://blog.openlibrary.org/feed/',
    UNHEX(SHA2('https://blog.openlibrary.org/feed/', 256)),
    'RSS',
    'RSS2',
    'en',
    'Blog del catálogo abierto de libros de Internet Archive',
    (
        SELECT id
        FROM content_types
        WHERE code = 'BIBLIO'
        LIMIT 1
    ), 'ACTIVE', 'https://archive.org/about/terms.php', 'Blog de proyecto abierto de Internet Archive; revisar licencia por entrada.', UTC_TIMESTAMP(6)
FROM publishers p
WHERE p.domain = 'archive.org'
    AND NOT EXISTS (
        SELECT 1
        FROM source_channels s
        WHERE s.url_sha256 = UNHEX(SHA2('https://blog.openlibrary.org/feed/', 256))
    );
-- MetaBrainz
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
        terms_url,
        usage_policy,
        terms_reviewed_at
    )
SELECT p.id,
    'RSS',
    'MetaBrainz Blog',
    'https://blog.metabrainz.org/feed/',
    UNHEX(SHA2('https://blog.metabrainz.org/feed/', 256)),
    'RSS',
    'RSS2',
    'en',
    'Desarrollo de MusicBrainz, ListenBrainz y datos musicales abiertos',
    (
        SELECT id
        FROM content_types
        WHERE code = 'NEWS'
        LIMIT 1
    ), 'ACTIVE', 'https://metabrainz.org/social-contract', 'Publicación de fundación sin ánimo de lucro; datos musicales CC0. Blog bajo licencia abierta.', UTC_TIMESTAMP(6)
FROM publishers p
WHERE p.domain = 'metabrainz.org'
    AND NOT EXISTS (
        SELECT 1
        FROM source_channels s
        WHERE s.url_sha256 = UNHEX(SHA2('https://blog.metabrainz.org/feed/', 256))
    );
-- RILM
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
        terms_url,
        usage_policy,
        terms_reviewed_at
    )
SELECT p.id,
    'RSS',
    'RILM - Bibliolore',
    'https://bibliolore.org/feed/',
    UNHEX(SHA2('https://bibliolore.org/feed/', 256)),
    'RSS',
    'RSS2',
    'en',
    'Investigación musical, musicología y etnomusicología (RILM)',
    (
        SELECT id
        FROM content_types
        WHERE code = 'RESEARCH'
        LIMIT 1
    ), 'ACTIVE', 'https://bibliolore.org/about/', 'Blog académico de RILM con licencia de compartición; citar y enlazar al original.', UTC_TIMESTAMP(6)
FROM publishers p
WHERE p.domain = 'bibliolore.org'
    AND NOT EXISTS (
        SELECT 1
        FROM source_channels s
        WHERE s.url_sha256 = UNHEX(SHA2('https://bibliolore.org/feed/', 256))
    );
-- DOAJ
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
        terms_url,
        usage_policy,
        terms_reviewed_at
    )
SELECT p.id,
    'RSS',
    'DOAJ - Nuevas revistas',
    'https://doaj.org/feed',
    UNHEX(SHA2('https://doaj.org/feed', 256)),
    'RSS',
    'RSS2',
    'en',
    'Revistas de acceso abierto recién incorporadas al directorio DOAJ',
    (
        SELECT id
        FROM content_types
        WHERE code = 'RESEARCH'
        LIMIT 1
    ), 'ACTIVE', 'https://doaj.org/terms/', 'Metadatos bajo CC0. La licencia de los metadatos no altera los derechos del artículo. Volumen alto (100 entradas).', UTC_TIMESTAMP(6)
FROM publishers p
WHERE p.domain = 'doaj.org'
    AND NOT EXISTS (
        SELECT 1
        FROM source_channels s
        WHERE s.url_sha256 = UNHEX(SHA2('https://doaj.org/feed', 256))
    );
-- PLOS / Frontiers
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
        terms_url,
        usage_policy,
        terms_reviewed_at
    )
SELECT p.id,
    'Atom',
    'PLOS ONE',
    'https://journals.plos.org/plosone/feed/atom',
    UNHEX(
        SHA2(
            'https://journals.plos.org/plosone/feed/atom',
            256
        )
    ),
    'ATOM',
    'Atom',
    'en',
    'Artículos científicos multidisciplinares de acceso abierto (incluye música y acústica)',
    (
        SELECT id
        FROM content_types
        WHERE code = 'RESEARCH'
        LIMIT 1
    ), 'ACTIVE', 'https://plos.org/publishing-with-plos/licenses-and-copyright/', 'Artículos bajo CC BY 4.0: reutilización permitida con atribución. Exige filtrado temático fuerte.', UTC_TIMESTAMP(6)
FROM publishers p
WHERE p.domain = 'plos.org'
    AND NOT EXISTS (
        SELECT 1
        FROM source_channels s
        WHERE s.url_sha256 = UNHEX(
                SHA2(
                    'https://journals.plos.org/plosone/feed/atom',
                    256
                )
            )
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
        terms_url,
        usage_policy,
        terms_reviewed_at
    )
SELECT p.id,
    'RSS',
    'Frontiers in Psychology - Música',
    'https://www.frontiersin.org/journals/psychology/rss',
    UNHEX(
        SHA2(
            'https://www.frontiersin.org/journals/psychology/rss',
            256
        )
    ),
    'RSS',
    'RSS2',
    'en',
    'Psicología de la música, cognición y percepción auditiva',
    (
        SELECT id
        FROM content_types
        WHERE code = 'RESEARCH'
        LIMIT 1
    ), 'ACTIVE', 'https://www.frontiersin.org/about/terms', 'Artículos bajo CC BY 4.0. Feed general de la revista; requiere filtrado temático musical.', UTC_TIMESTAMP(6)
FROM publishers p
WHERE p.domain = 'frontiersin.org'
    AND NOT EXISTS (
        SELECT 1
        FROM source_channels s
        WHERE s.url_sha256 = UNHEX(
                SHA2(
                    'https://www.frontiersin.org/journals/psychology/rss',
                    256
                )
            )
    );
-- NARA
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
        terms_url,
        usage_policy,
        terms_reviewed_at
    )
SELECT p.id,
    'RSS',
    'NARA - Noticias',
    'https://www.archives.gov/rss.xml',
    UNHEX(SHA2('https://www.archives.gov/rss.xml', 256)),
    'RSS',
    'RSS2',
    'en',
    'Noticias del Archivo Nacional de EE. UU. (patrimonio sonoro y documental)',
    (
        SELECT id
        FROM content_types
        WHERE code = 'NEWS'
        LIMIT 1
    ), 'ACTIVE', 'https://www.archives.gov/global-pages/privacy-policy', 'Contenido del Gobierno federal de EE. UU. en dominio público. Requiere filtrado musical.', UTC_TIMESTAMP(6)
FROM publishers p
WHERE p.domain = 'archives.gov'
    AND NOT EXISTS (
        SELECT 1
        FROM source_channels s
        WHERE s.url_sha256 = UNHEX(SHA2('https://www.archives.gov/rss.xml', 256))
    );
-- ---------- Canales con reutilización no autorizada (PAUSED) ----------
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
        terms_url,
        usage_policy
    )
SELECT p.id,
    'RSS',
    'Scherzo',
    'https://scherzo.es/feed',
    UNHEX(SHA2('https://scherzo.es/feed', 256)),
    'RSS',
    'RSS2',
    'es',
    'Música clásica, ópera y actualidad musical',
    (
        SELECT id
        FROM content_types
        WHERE code = 'NEWS'
        LIMIT 1
    ), 'PAUSED', 'https://scherzo.es/aviso-legal/', 'El aviso legal exige autorización escrita previa. No activar sin permiso. Solo enlace directo.'
FROM publishers p
WHERE p.domain = 'scherzo.es'
    AND NOT EXISTS (
        SELECT 1
        FROM source_channels s
        WHERE s.url_sha256 = UNHEX(SHA2('https://scherzo.es/feed', 256))
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
        terms_url,
        usage_policy
    )
SELECT p.id,
    'RSS',
    'Beckmesser',
    'https://www.beckmesser.com/feed',
    UNHEX(SHA2('https://www.beckmesser.com/feed', 256)),
    'RSS',
    'RSS2',
    'es',
    'Música clásica, ópera y crítica musical',
    (
        SELECT id
        FROM content_types
        WHERE code = 'NEWS'
        LIMIT 1
    ), 'PAUSED', 'https://www.beckmesser.com/aviso-legal/', 'Todos los derechos reservados; prohíbe almacenamiento permanente sin consentimiento escrito.'
FROM publishers p
WHERE p.domain = 'beckmesser.com'
    AND NOT EXISTS (
        SELECT 1
        FROM source_channels s
        WHERE s.url_sha256 = UNHEX(SHA2('https://www.beckmesser.com/feed', 256))
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
        terms_url,
        usage_policy
    )
SELECT p.id,
    'RSS',
    'Bachtrack - News',
    'https://bachtrack.com/news.rss.xml',
    UNHEX(SHA2('https://bachtrack.com/news.rss.xml', 256)),
    'RSS',
    'RSS2',
    'en',
    'Noticias de música clásica, ópera, danza y actividad artística',
    (
        SELECT id
        FROM content_types
        WHERE code = 'NEWS'
        LIMIT 1
    ), 'PAUSED', 'https://bachtrack.com/fr_FR/conditions-of-use', 'Uso personal/privado; robots limitados a mostrar resultados. Prohíbe otros usos automatizados e IA.'
FROM publishers p
WHERE p.domain = 'bachtrack.com'
    AND NOT EXISTS (
        SELECT 1
        FROM source_channels s
        WHERE s.url_sha256 = UNHEX(SHA2('https://bachtrack.com/news.rss.xml', 256))
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
        terms_url,
        usage_policy
    )
SELECT p.id,
    'RSS',
    'Musicology Now',
    'https://musicologynow.org/feed',
    UNHEX(SHA2('https://musicologynow.org/feed', 256)),
    'RSS',
    'RSS2',
    'en',
    'Divulgación e investigación musicológica',
    (
        SELECT id
        FROM content_types
        WHERE code = 'RESEARCH'
        LIMIT 1
    ), 'PAUSED', 'https://musicologynow.org/about-musicology-now/', 'Sin licencia general de reutilización. Pendiente de autorización antes de persistir o enviar a IA.'
FROM publishers p
WHERE p.domain = 'musicologynow.org'
    AND NOT EXISTS (
        SELECT 1
        FROM source_channels s
        WHERE s.url_sha256 = UNHEX(SHA2('https://musicologynow.org/feed', 256))
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
        terms_url,
        usage_policy
    )
SELECT p.id,
    'RSS',
    'Music Business Worldwide',
    'https://www.musicbusinessworldwide.com/feed/',
    UNHEX(
        SHA2(
            'https://www.musicbusinessworldwide.com/feed/',
            256
        )
    ),
    'RSS',
    'RSS2',
    'en',
    'Industria musical, mercado y derechos',
    (
        SELECT id
        FROM content_types
        WHERE code = 'NEWS'
        LIMIT 1
    ), 'PAUSED', 'https://www.musicbusinessworldwide.com/terms-of-use/', 'Uso personal no comercial; prohíbe copia, traducción y publicación sin consentimiento.'
FROM publishers p
WHERE p.domain = 'musicbusinessworldwide.com'
    AND NOT EXISTS (
        SELECT 1
        FROM source_channels s
        WHERE s.url_sha256 = UNHEX(
                SHA2(
                    'https://www.musicbusinessworldwide.com/feed/',
                    256
                )
            )
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
        terms_url,
        usage_policy
    )
SELECT p.id,
    'RSS',
    'NPR Music',
    'https://feeds.npr.org/1039/rss.xml',
    UNHEX(SHA2('https://feeds.npr.org/1039/rss.xml', 256)),
    'RSS',
    'RSS2',
    'en',
    'Actualidad musical de interés general (NPR)',
    (
        SELECT id
        FROM content_types
        WHERE code = 'NEWS'
        LIMIT 1
    ), 'PAUSED', 'https://www.npr.org/about-npr/179876898/terms-of-use', 'Prohíbe usar sus contenidos para entrenar o construir sistemas de IA sin permiso escrito.'
FROM publishers p
WHERE p.domain = 'npr.org'
    AND NOT EXISTS (
        SELECT 1
        FROM source_channels s
        WHERE s.url_sha256 = UNHEX(SHA2('https://feeds.npr.org/1039/rss.xml', 256))
    );
INSERT INTO schema_migrations (version, description)
VALUES (
        '007_free_music_sources',
        'Catálogo de fuentes musicales de libre difusión (15 activas) y canales restringidos en pausa'
    ) ON DUPLICATE KEY
UPDATE description =
VALUES(description);