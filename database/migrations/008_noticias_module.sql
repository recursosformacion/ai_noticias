-- ai_noticias — soporte para el módulo de respuesta por correo
-- Añade: modos de entrega por correo, historial de consultas por correo y temas
-- de interés reutilizables. No toca las tablas de captura.
-- Compatible con ejecuciones repetidas sobre MariaDB 10.4.
USE osap_noticias;
-- ---------- Preferencias de entrega en source_channels ----------
-- MANUAL: no se incluye en los correos automáticos.
-- DAILY: se incluye en el resumen diario.
-- ALERT: se incluye y puede generar avisos inmediatos.
ALTER TABLE source_channels
ADD COLUMN IF NOT EXISTS delivery_mode VARCHAR(16) NOT NULL DEFAULT 'DAILY'
AFTER status;
CREATE INDEX IF NOT EXISTS ix_source_channels_delivery ON source_channels (delivery_mode, status);
-- ---------- Historial de consultas por correo ----------
-- Registra cada petición recibida: quién pregunta, desde qué dirección, qué temas,
-- qué idioma y cuántas noticias se le devolvieron. Permite auditoría, límites de uso
-- y evitar respuestas duplicadas al mismo mensaje.
CREATE TABLE IF NOT EXISTS email_requests (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  message_id VARCHAR(255) NULL,
  sender_hash CHAR(64) NULL,
  sender_domain VARCHAR(255) NULL,
  subject VARCHAR(500) NULL,
  topics_json JSON NULL,
  languages_json JSON NULL,
  limit_requested INT UNSIGNED NULL,
  window_days INT UNSIGNED NULL,
  result_status VARCHAR(20) NOT NULL DEFAULT 'RECEIVED',
  items_sent INT UNSIGNED NOT NULL DEFAULT 0,
  response_subject VARCHAR(500) NULL,
  error_code VARCHAR(100) NULL,
  error_message TEXT NULL,
  received_at DATETIME(6) NOT NULL,
  processed_at DATETIME(6) NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_email_requests_message (message_id),
  KEY ix_email_requests_sender (sender_hash, received_at),
  KEY ix_email_requests_status (result_status, received_at)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
-- Detalle de lo devuelto en cada consulta (permite repetir o auditar un envío).
CREATE TABLE IF NOT EXISTS email_request_items (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  email_request_id BIGINT UNSIGNED NOT NULL,
  news_item_id BIGINT UNSIGNED NOT NULL,
  publication_id BIGINT UNSIGNED NULL,
  rank_position INT UNSIGNED NOT NULL DEFAULT 0,
  score DECIMAL(8, 4) NULL,
  matched_terms VARCHAR(1000) NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_email_request_items (email_request_id, news_item_id),
  KEY ix_email_request_items_news (news_item_id),
  CONSTRAINT fk_email_request_items_request FOREIGN KEY (email_request_id) REFERENCES email_requests(id) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT fk_email_request_items_news FOREIGN KEY (news_item_id) REFERENCES news_items(id) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT fk_email_request_items_publication FOREIGN KEY (publication_id) REFERENCES news_publications(id) ON DELETE
  SET NULL ON UPDATE RESTRICT
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
-- ---------- Temas de interés reutilizables ----------
-- Un tema agrupa sinónimos y se vincula a categorías de la taxonomía y a géneros
-- del catálogo OSAP (osap_storage.genres) para enriquecer la consulta.
CREATE TABLE IF NOT EXISTS interest_topics (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  code VARCHAR(64) NOT NULL,
  name VARCHAR(255) NOT NULL,
  description TEXT NULL,
  keywords_json JSON NULL,
  osap_genre_ids_json JSON NULL,
  category_codes_json JSON NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
  created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  UNIQUE KEY uq_interest_topics_code (code),
  KEY ix_interest_topics_status (status)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
-- ---------- Semilla de temas ----------
-- Los códigos de género proceden de osap_storage.genres:
-- 1 Clásica/Docta, 2 Sacra/Himnología, 3 Tradición Folclórica y Etnomusicología,
-- 4 Jazz y Blues, 5 Rock y Metal, 6 Pop, 7 Urbana y Hip Hop, 8 Electrónica y Dance,
-- 9 Latina y Caribeña, 10 Country, Folk y Americana, 11 Soul, Funk y Disco,
-- 12 Música Escénica y Aplicada.
INSERT INTO interest_topics (
    code,
    name,
    description,
    keywords_json,
    osap_genre_ids_json,
    category_codes_json
  )
VALUES (
    'clasica',
    'Música clásica y docta',
    'Conciertos, orquestas, ópera, composición académica e intérpretes de música clásica.',
    JSON_ARRAY(
      'música clásica',
      'clásica',
      'orquesta',
      'sinfónica',
      'ópera',
      'concierto',
      'compositor',
      'director',
      'cuarteto',
      'solista',
      'recital',
      'partitura'
    ),
    JSON_ARRAY(1, 12),
    JSON_ARRAY('B1', 'B3', 'C1', 'C8', 'D1', 'D2')
  ),
  (
    'sacra',
    'Música sacra y coral',
    'Música litúrgica, coral, himnología, órganos y repertorio religioso.',
    JSON_ARRAY(
      'música sacra',
      'coral',
      'coro',
      'litúrgica',
      'himno',
      'himnología',
      'órgano',
      'misas',
      'motete',
      'réquiem',
      'canto gregoriano'
    ),
    JSON_ARRAY(2),
    JSON_ARRAY('B2', 'B15', 'D3')
  ),
  (
    'patrimonio',
    'Patrimonio, archivos y partituras',
    'Fondos documentales, digitalización, manuscritos, bibliotecas y colecciones musicales.',
    JSON_ARRAY(
      'patrimonio',
      'archivo',
      'manuscrito',
      'partitura',
      'digitalización',
      'biblioteca',
      'colección',
      'fondo',
      'catálogo',
      'incunable',
      'legado'
    ),
    JSON_ARRAY(1, 3),
    JSON_ARRAY('E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7')
  ),
  (
    'investigacion',
    'Musicología e investigación',
    'Artículos académicos, estudios, tesis y proyectos de investigación musical.',
    JSON_ARRAY(
      'musicología',
      'investigación',
      'estudio',
      'tesis',
      'etnomusicología',
      'académico',
      'universidad',
      'artículo científico'
    ),
    JSON_ARRAY(3),
    JSON_ARRAY('D6', 'A5')
  ),
  (
    'jazz',
    'Jazz y blues',
    'Actualidad de jazz, blues, escenas improvisadas y festivales.',
    JSON_ARRAY(
      'jazz',
      'blues',
      'swing',
      'bebop',
      'improvisación',
      'big band',
      'standard'
    ),
    JSON_ARRAY(4),
    JSON_ARRAY('B8')
  ),
  (
    'popular',
    'Música popular, rock y pop',
    'Rock, pop, metal, indie y escenas de música popular contemporánea.',
    JSON_ARRAY(
      'rock',
      'pop',
      'metal',
      'indie',
      'grupo',
      'banda',
      'gira',
      'disco',
      'sencillo',
      'álbum'
    ),
    JSON_ARRAY(5, 6),
    JSON_ARRAY('B4', 'C1', 'C2', 'C4')
  ),
  (
    'urbana',
    'Música urbana y latina',
    'Hip hop, reguetón, música latina, caribeña y escenas urbanas.',
    JSON_ARRAY(
      'urbana',
      'hip hop',
      'rap',
      'reguetón',
      'latina',
      'caribeña',
      'trap',
      'reggaeton'
    ),
    JSON_ARRAY(7, 9),
    JSON_ARRAY('B5', 'B6', 'B10')
  ),
  (
    'electronica',
    'Música electrónica y experimental',
    'Electrónica, dance, música experimental y nuevas tecnologías sonoras.',
    JSON_ARRAY(
      'electrónica',
      'dance',
      'techno',
      'experimental',
      'sintetizador',
      'DJ',
      'ambient'
    ),
    JSON_ARRAY(8),
    JSON_ARRAY('B7', 'A5')
  ),
  (
    'tradicional',
    'Músicas tradicionales y del mundo',
    'Folk, músicas del mundo, tradiciones orales, folklor y etnomusicología aplicada.',
    JSON_ARRAY(
      'folk',
      'tradicional',
      'folclore',
      'etnomusicología',
      'músicas del mundo',
      'popular tradicional'
    ),
    JSON_ARRAY(3, 10),
    JSON_ARRAY('B11', 'B16', 'E5')
  ),
  (
    'industria',
    'Industria musical y derechos',
    'Sellos, streaming, giras, mercado, derechos de autor, licencias y legislación.',
    JSON_ARRAY(
      'industria',
      'sello',
      'discográfica',
      'streaming',
      'derechos',
      'licencia',
      'copyright',
      'mercado',
      'promotora',
      'gestión'
    ),
    JSON_ARRAY(6, 7, 8),
    JSON_ARRAY('A2', 'A3', 'A4', 'A6', 'A7', 'A8')
  ),
  (
    'educacion',
    'Educación musical',
    'Conservatorios, escuelas, didáctica, cursos y formación musical.',
    JSON_ARRAY(
      'educación',
      'conservatorio',
      'escuela',
      'didáctica',
      'enseñanza',
      'formación',
      'curso',
      'taller',
      'alumnado'
    ),
    JSON_ARRAY(1),
    JSON_ARRAY('D4', 'D5', 'F5')
  ),
  (
    'agenda',
    'Agenda y eventos',
    'Conciertos, festivales, ciclos, temporadas y actividades programadas.',
    JSON_ARRAY(
      'concierto',
      'festival',
      'ciclo',
      'temporada',
      'gira',
      'agenda',
      'programación',
      'entrada',
      'estreno'
    ),
    JSON_ARRAY(1, 5, 6, 4),
    JSON_ARRAY('C1', 'C2', 'C3', 'C9')
  ) ON DUPLICATE KEY
UPDATE name =
VALUES(name),
  description =
VALUES(description),
  keywords_json =
VALUES(keywords_json),
  osap_genre_ids_json =
VALUES(osap_genre_ids_json),
  category_codes_json =
VALUES(category_codes_json);
INSERT INTO schema_migrations (version, description)
VALUES (
    '008_noticias_module',
    'Soporte del módulo de correo: entrega por canal, consultas por correo y temas de interés'
  ) ON DUPLICATE KEY
UPDATE description =
VALUES(description);