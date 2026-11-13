-- ai_noticias — catálogo inicial de tipos de contenido
-- Requiere haber aplicado 001_initial_schema.sql.

USE osap_noticias;

INSERT INTO content_types (code, name, description, status) VALUES
('NEWS', 'Noticia', 'Información de actualidad sobre un hecho o desarrollo.', 'ACTIVE'),
('EVENT', 'Evento', 'Concierto, festival, ciclo, convocatoria con fecha o actividad programada.', 'ACTIVE'),
('RELEASE', 'Lanzamiento', 'Publicación o estreno discográfico, audiovisual o editorial.', 'ACTIVE'),
('RESEARCH', 'Investigación', 'Artículo académico, investigación, estudio o comunicación científica.', 'ACTIVE'),
('BIBLIO', 'Novedad bibliográfica', 'Libro, edición, catálogo o publicación bibliográfica.', 'ACTIVE'),
('COLLECTION', 'Colección o patrimonio', 'Novedad sobre fondos, archivos, colecciones o patrimonio musical.', 'ACTIVE'),
('INTERVIEW', 'Entrevista', 'Entrevista o conversación con músicos, investigadores o agentes del sector.', 'ACTIVE'),
('OPINION', 'Opinión', 'Columna, análisis o comentario editorial.', 'ACTIVE'),
('OTHER', 'Otro', 'Contenido pertinente que no encaja todavía en otro tipo.', 'ACTIVE'),
('REVIEW', 'Crítica o reseña', 'Crítica de concierto, grabación, espectáculo o publicación.', 'ACTIVE')
ON DUPLICATE KEY UPDATE
  name = VALUES(name),
  description = VALUES(description),
  status = VALUES(status);

INSERT INTO schema_migrations (version, description)
VALUES ('002_seed_content_types', 'Catálogo inicial de tipos de contenido')
ON DUPLICATE KEY UPDATE description = VALUES(description);
