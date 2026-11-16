-- ai_noticias — perfiles de usuario y temas de interés por usuario
--
-- Los temas dejan de ser solo parámetros del correo: pasan a ser una preferencia
-- propiedad del usuario. El módulo resuelve el usuario por el remitente y usa sus
-- temas; si no hay perfil, cae al contenido del propio correo (modo anónimo).
--
-- Enlace con identidad: ``user_ref`` guarda el ``osap-auth.users.id`` (UUID de 36
-- caracteres) cuando el usuario proviene del servicio de identidad. No se crea clave
-- foránea porque las bases son independientes (osap-auth vive en otro esquema).
--
-- Compatible con ejecuciones repetidas sobre MariaDB 10.4.
USE osap_noticias;
-- ---------- Perfiles ----------
CREATE TABLE IF NOT EXISTS user_profiles (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  -- Identidad en OSAP (osap-auth.users.id). NULL para perfiles locales.
  user_ref CHAR(36) NULL,
  -- Identidad en este módulo: SHA-256 del correo normalizado (en minúsculas y sin espacios).
  email_lookup CHAR(64) NOT NULL,
  -- Correo de respuesta. Se guarda cifrado o vacío si no se desea almacenar en claro.
  reply_address VARCHAR(320) NULL,
  display_name VARCHAR(160) NULL,
  -- Preferencias de entrega.
  preferred_language VARCHAR(8) NOT NULL DEFAULT 'es',
  secondary_languages_json JSON NULL,
  max_items INT UNSIGNED NOT NULL DEFAULT 20,
  window_days INT UNSIGNED NOT NULL DEFAULT 30,
  delivery_frequency VARCHAR(16) NOT NULL DEFAULT 'ON_DEMAND',
  status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
  consent_at DATETIME(6) NULL,
  last_request_at DATETIME(6) NULL,
  created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  UNIQUE KEY uq_user_profiles_email (email_lookup),
  UNIQUE KEY uq_user_profiles_user_ref (user_ref),
  KEY ix_user_profiles_status (status),
  KEY ix_user_profiles_delivery (status, delivery_frequency)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
-- ---------- Temas de interés del usuario ----------
-- Cada fila es un tema que el usuario ha elegido. Puede apuntar a un tema semilla
-- (interest_topics) o ser texto libre; ``weight`` permite ordenar prioridades.
CREATE TABLE IF NOT EXISTS user_topics (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  profile_id BIGINT UNSIGNED NOT NULL,
  interest_topic_id BIGINT UNSIGNED NULL,
  label VARCHAR(160) NOT NULL,
  keywords_json JSON NULL,
  weight DECIMAL(4, 2) NOT NULL DEFAULT 1.00,
  active BOOLEAN NOT NULL DEFAULT TRUE,
  source VARCHAR(16) NOT NULL DEFAULT 'USER',
  created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  UNIQUE KEY uq_user_topics_label (profile_id, label),
  KEY ix_user_topics_profile_active (profile_id, active),
  CONSTRAINT fk_user_topics_profile FOREIGN KEY (profile_id) REFERENCES user_profiles(id) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT fk_user_topics_seed FOREIGN KEY (interest_topic_id) REFERENCES interest_topics(id) ON DELETE
  SET NULL ON UPDATE RESTRICT
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
-- ---------- Idioma y origen de cada tema ----------
-- Un tema puede tener términos propios por idioma (p. ej. «ópera»/«opera»/«opéra»).
CREATE TABLE IF NOT EXISTS user_topic_terms (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_topic_id BIGINT UNSIGNED NOT NULL,
  language_code VARCHAR(8) NOT NULL DEFAULT 'es',
  term VARCHAR(160) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_user_topic_terms (user_topic_id, language_code, term),
  KEY ix_user_topic_terms_language (language_code, term),
  CONSTRAINT fk_user_topic_terms_topic FOREIGN KEY (user_topic_id) REFERENCES user_topics(id) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
-- ---------- Trazabilidad de la consulta por correo ----------
-- Indica de dónde salieron los temas de una petición: perfil del usuario o el propio correo.
ALTER TABLE email_requests
ADD COLUMN IF NOT EXISTS profile_id BIGINT UNSIGNED NULL
AFTER id;
ALTER TABLE email_requests
ADD COLUMN IF NOT EXISTS topic_source VARCHAR(16) NOT NULL DEFAULT 'EMAIL'
AFTER topics_json;
SET @fk_exists = (
    SELECT COUNT(*)
    FROM information_schema.TABLE_CONSTRAINTS
    WHERE CONSTRAINT_SCHEMA = DATABASE()
      AND TABLE_NAME = 'email_requests'
      AND CONSTRAINT_NAME = 'fk_email_requests_profile'
      AND CONSTRAINT_TYPE = 'FOREIGN KEY'
  );
SET @ddl = IF(
    @fk_exists = 0,
    'ALTER TABLE email_requests ADD CONSTRAINT fk_email_requests_profile FOREIGN KEY (profile_id) REFERENCES user_profiles(id) ON DELETE SET NULL ON UPDATE RESTRICT',
    'SELECT 1'
  );
PREPARE migration_stmt
FROM @ddl;
EXECUTE migration_stmt;
DEALLOCATE PREPARE migration_stmt;
CREATE INDEX IF NOT EXISTS ix_email_requests_profile ON email_requests (profile_id, received_at);
INSERT INTO schema_migrations (version, description)
VALUES (
    '009_user_profiles',
    'Perfiles de usuario, temas de interés por usuario y trazabilidad de la consulta'
  ) ON DUPLICATE KEY
UPDATE description =
VALUES(description);