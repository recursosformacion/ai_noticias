-- ai_noticias — la cola de salida identifica al destinatario por su cuenta de OSAP
--
-- Motivo de privacidad: en `osap-auth` el correo no se guarda en claro (solo
-- `email_lookup` y `email_cipher` con clave de osap-auth). `ai_noticias` no puede
-- ni debe descifrarlo, así que la cola no almacena direcciones: guarda el
-- `user_ref` (UUID de osap-auth) y OSAP resuelve el buzón al enviar.
--
-- `recipient_address` queda para dos casos legítimos: pruebas manuales y envíos a
-- direcciones que no son cuentas de OSAP (por ejemplo, buzones de contacto).
--
-- Compatible con ejecuciones repetidas sobre MariaDB 10.4.
USE osap_noticias;
ALTER TABLE outbound_messages
ADD COLUMN IF NOT EXISTS user_ref CHAR(36) NULL
AFTER id;
ALTER TABLE outbound_messages
MODIFY COLUMN recipient VARCHAR(320) NULL;
ALTER TABLE outbound_messages
ADD COLUMN IF NOT EXISTS recipient_address VARCHAR(320) NULL
AFTER recipient;
CREATE INDEX IF NOT EXISTS ix_outbound_user_ref ON outbound_messages (user_ref, sent_at);
-- Registro del envío por usuario (evita reenviar el mismo boletín dos veces al día).
ALTER TABLE outbound_messages
ADD COLUMN IF NOT EXISTS digest_date DATE NULL
AFTER kind;
ALTER TABLE outbound_messages
ADD COLUMN IF NOT EXISTS digest_window_days INT UNSIGNED NULL
AFTER digest_date;
CREATE INDEX IF NOT EXISTS ix_outbound_digest ON outbound_messages (user_ref, digest_date);
INSERT INTO schema_migrations (version, description)
VALUES (
    '015_outbound_userref',
    'Cola de salida por user_ref (sin correos en claro) y control de boletín diario'
  ) ON DUPLICATE KEY
UPDATE description =
VALUES(description);