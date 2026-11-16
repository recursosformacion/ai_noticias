-- ai_noticias — modo de entrega editorial por canal
--
-- El corpus mezcla canales útiles para noticias con otros que son referencias o
-- fondos documentales. `delivery_mode` decide si un canal puede aparecer en las
-- respuestas del módulo de correo:
--
--   DAILY   → se incluye en las respuestas (noticias, agenda, novedades).
--   MANUAL  → se conserva en la base, pero no se ofrece en los correos.
--   ALERT   → además puede generar avisos inmediatos (reservado).
--
-- JUSTIFICACIÓN (revisada el 15-11-2026 sobre el corpus real):
--   - Wikipedia (artículo «Music»): es un historial de ediciones, no noticias.
--   - Wikisource: son textos literarios de dominio público, no actualidad.
--   - BnF Agenda: 200 entradas de toda la agenda cultural, sin filtro musical;
--     se degrada a MANUAL hasta que exista filtrado temático.
--   - NARA: noticias de archivo general, sin relación musical verificada.
--
-- Compatible con ejecuciones repetidas sobre MariaDB 10.4.
USE osap_noticias;
UPDATE source_channels
SET delivery_mode = 'MANUAL'
WHERE url IN (
    'https://en.wikipedia.org/w/index.php?title=Music&action=history&feed=atom',
    'https://es.wikisource.org/w/index.php?title=Especial:CambiosRecientes&feed=atom&namespace=0',
    'https://www.bnf.fr/fr/agenda/rss',
    'https://www.archives.gov/rss.xml'
  );
-- Los canales musicales especializados se incluyen en las respuestas diarias.
UPDATE source_channels
SET delivery_mode = 'DAILY'
WHERE url IN (
    'https://blogs.loc.gov/nls-music-notes/feed/',
    'https://www.loc.gov/rss/music/concerts.xml',
    'https://www.bnf.fr/fr/actualites/rss',
    'https://bibliographienationale.bnf.fr/rss/mus',
    'https://bibliographienationale.bnf.fr/rss/son',
    'https://archive.org/services/collection-rss.php?collection=opensource_audio',
    'https://blog.openlibrary.org/feed/',
    'https://blog.metabrainz.org/feed/',
    'https://bibliolore.org/feed/',
    'https://doaj.org/feed',
    'https://journals.plos.org/plosone/feed/atom',
    'https://www.frontiersin.org/journals/psychology/rss'
  );
INSERT INTO schema_migrations (version, description)
VALUES (
    '011_delivery_modes',
    'Modo de entrega editorial por canal (DAILY/MANUAL)'
  ) ON DUPLICATE KEY
UPDATE description =
VALUES(description);