-- ai_noticias — cola de mensajes de salida (puerto de entrega)
--
-- ADR-006 de OSAP: el correo lo envía `osap-support`, que es el propietario de las
-- comunicaciones (EmailSender, CommunicationEvent, plantillas y proveedor SMTP).
-- `ai_noticias` no debe abrir conexiones SMTP ni tener credenciales de correo.
--
-- Por eso este módulo *deja* el mensaje en esta tabla y OSAP lo recoge. El
-- responsable de esta tabla es ai_noticias; el consumidor es osap-support.
--
-- CONTRATO PARA OSAP (a implementar en osap-support, fuera de este repositorio):
--   1. Leer `outbound_messages` con status='PENDING' por `next_attempt_at`.
--   2. Bloquear la fila (SELECT ... FOR UPDATE SKIP LOCKED) y marcarla 'SENDING'.
--   3. Enviar con EmailSender usando `recipient`, `subject`, `body_text`, `body_html`.
--   4. Marcar 'SENT' con `sent_at`, o 'FAILED' incrementando `attempts` y
--      reprogramando `next_attempt_at`. Tras N intentos, 'DEAD'.
--
-- Compatible con ejecuciones repetidas sobre MariaDB 10.4.
USE osap_noticias;
CREATE TABLE IF NOT EXISTS outbound_messages (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  -- Destinatario y contenido final: OSAP no necesita consultar otras tablas.
  recipient VARCHAR(320) NOT NULL,
  subject VARCHAR(500) NOT NULL,
  body_text MEDIUMTEXT NOT NULL,
  body_html MEDIUMTEXT NULL,
  -- Trazabilidad.
  origin VARCHAR(32) NOT NULL DEFAULT 'AI_NOTICIAS',
  kind VARCHAR(32) NOT NULL DEFAULT 'NEWS_DIGEST',
  reference_id VARCHAR(64) NULL,
  language_code VARCHAR(8) NULL,
  items_count INT UNSIGNED NOT NULL DEFAULT 0,
  -- Ciclo de vida.
  status VARCHAR(16) NOT NULL DEFAULT 'PENDING',
  attempts INT UNSIGNED NOT NULL DEFAULT 0,
  last_error VARCHAR(1000) NULL,
  next_attempt_at DATETIME(6) NULL,
  created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  claimed_at DATETIME(6) NULL,
  sent_at DATETIME(6) NULL,
  PRIMARY KEY (id),
  KEY ix_outbound_pending (status, next_attempt_at),
  KEY ix_outbound_recipient (recipient, created_at),
  KEY ix_outbound_reference (reference_id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
INSERT INTO schema_migrations (version, description)
VALUES (
    '013_outbound_queue',
    'Cola de salida: ai_noticias construye el mensaje y OSAP lo envía'
  ) ON DUPLICATE KEY
UPDATE description =
VALUES(description);