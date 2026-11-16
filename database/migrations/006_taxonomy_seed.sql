-- Carga de la taxonomía inicial para ai_noticias
-- Basado en el documento de propuesta funcional (Doc 01 §5)
-- Insertar una versión nueva con las categorías iniciales

SET NAMES utf8mb4;
SET time_zone = '+00:00';

USE osap_noticias;

-- Agregamos una nueva versión de taxonomía
INSERT INTO taxonomy_versions (version_code, description, status)
VALUES ('2026.11-A', 'Taxonomía inicial para noticias musicales (propuesta funcional)', 'ACTIVE')
ON DUPLICATE KEY UPDATE description = VALUES(description), status = VALUES(status);

-- Recuperamos el ID de la versión de taxonomía recién creada
SET @taxonomy_version_id = (SELECT id FROM taxonomy_versions WHERE version_code = '2026.11-A');

-- Función para insertar categorías y manejar árboles
CREATE TEMPORARY TABLE IF NOT EXISTS temporary_categories (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    taxonomy_version_id BIGINT UNSIGNED NOT NULL,
    parent_id BIGINT UNSIGNED,
    code VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL
);

-- Ramas superiores: nivel A–F
INSERT IGNORE INTO temporary_categories (taxonomy_version_id, code, name) VALUES
(@taxonomy_version_id, 'A', 'Actualidad musical general'),
(@taxonomy_version_id, 'B', 'Géneros y tradiciones musicales'),
(@taxonomy_version_id, 'C', 'Actividad y actualidad artística'),
(@taxonomy_version_id, 'D', 'Creación, interpretación y formación'),
(@taxonomy_version_id, 'E', 'Partituras, archivos y patrimonio'),
(@taxonomy_version_id, 'F', 'Sociedad y música');

-- Subcategorías para cada rama principal
-- Actualidad musical general
INSERT IGNORE INTO temporary_categories (taxonomy_version_id, parent_id, code, name) VALUES
(@taxonomy_version_id, 1, 'A1', 'Noticias generales de música'),
(@taxonomy_version_id, 1, 'A2', 'Industria musical y mercado'),
(@taxonomy_version_id, 1, 'A3', 'Sellos, editoriales, promotores y salas'),
(@taxonomy_version_id, 1, 'A4', 'Plataformas digitales, streaming y distribución'),
(@taxonomy_version_id, 1, 'A5', 'Tecnología, IA y herramientas musicales'),
(@taxonomy_version_id, 1, 'A6', 'Derechos de autor, licencias y legislación'),
(@taxonomy_version_id, 1, 'A7', 'Políticas culturales, financiación y ayudas'),
(@taxonomy_version_id, 1, 'A8', 'Trabajo, asociaciones y organizaciones profesionales');

-- Géneros y tradiciones musicales
INSERT IGNORE INTO temporary_categories (taxonomy_version_id, parent_id, code, name) VALUES
(@taxonomy_version_id, 2, 'B1', 'Música clásica y académica'),
(@taxonomy_version_id, 2, 'B2', 'Música coral y vocal'),
(@taxonomy_version_id, 2, 'B3', 'Ópera y música escénica'),
(@taxonomy_version_id, 2, 'B4', 'Rock y pop'),
(@taxonomy_version_id, 2, 'B5', 'Música urbana'),
(@taxonomy_version_id, 2, 'B6', 'Reguetón y músicas urbanas latinoamericanas'),
(@taxonomy_version_id, 2, 'B7', 'Música electrónica y experimental'),
(@taxonomy_version_id, 2, 'B8', 'Jazz y blues'),
(@taxonomy_version_id, 2, 'B9', 'Flamenco y músicas ibéricas'),
(@taxonomy_version_id, 2, 'B10', 'Músicas latinoamericanas y caribeñas'),
(@taxonomy_version_id, 2, 'B11', 'Folk, country, bluegrass y músicas tradicionales y del mundo'),
(@taxonomy_version_id, 2, 'B12', 'Reggae, ska y músicas jamaicanas'),
(@taxonomy_version_id, 2, 'B13', 'Música antigua y prácticas históricas'),
(@taxonomy_version_id, 2, 'B14', 'Bandas de viento y música para conjuntos'),
(@taxonomy_version_id, 2, 'B15', 'Música religiosa y litúrgica'),
(@taxonomy_version_id, 2, 'B16', 'Otros géneros, fusiones y escenas locales');

-- Actividad y actualidad artística
INSERT IGNORE INTO temporary_categories (taxonomy_version_id, parent_id, code, name) VALUES
(@taxonomy_version_id, 3, 'C1', 'Conciertos, giras y temporadas'),
(@taxonomy_version_id, 3, 'C2', 'Festivales y ciclos'),
(@taxonomy_version_id, 3, 'C3', 'Estrenos y nuevas obras'),
(@taxonomy_version_id, 3, 'C4', 'Lanzamientos discográficos y audiovisuales'),
(@taxonomy_version_id, 3, 'C5', 'Premios, concursos y convocatorias'),
(@taxonomy_version_id, 3, 'C6', 'Entrevistas y perfiles'),
(@taxonomy_version_id, 3, 'C7', 'Fallecimientos, homenajes y aniversarios'),
(@taxonomy_version_id, 3, 'C8', 'Noticias de orquestas y conjuntos'),
(@taxonomy_version_id, 3, 'C9', 'Noticias de auditorios, salas y teatros');

-- Creación, interpretación y formación
INSERT IGNORE INTO temporary_categories (taxonomy_version_id, parent_id, code, name) VALUES
(@taxonomy_version_id, 4, 'D1', 'Composición musical'),
(@taxonomy_version_id, 4, 'D2', 'Instrumentos y técnica de interpretación'),
(@taxonomy_version_id, 4, 'D3', 'Director de orquesta y práctica coral'),
(@taxonomy_version_id, 4, 'D4', 'Educación musical, conservatorios y universidades'),
(@taxonomy_version_id, 4, 'D5', 'Cursos, talleres y formación profesional'),
(@taxonomy_version_id, 4, 'D6', 'Investigación musicológica'),
(@taxonomy_version_id, 4, 'D7', 'Composición, arreglos y edición');

-- Partituras, archivos y patrimonio
INSERT IGNORE INTO temporary_categories (taxonomy_version_id, parent_id, code, name) VALUES
(@taxonomy_version_id, 5, 'E1', 'Partituras e impresos musicales'),
(@taxonomy_version_id, 5, 'E2', 'Manuscritos y fuentes históricas'),
(@taxonomy_version_id, 5, 'E3', 'Bibliotecas, archivos y colecciones'),
(@taxonomy_version_id, 5, 'E4', 'Digitalización y acceso libre'),
(@taxonomy_version_id, 5, 'E5', 'Patrimonio material e inmaterial'),
(@taxonomy_version_id, 5, 'E6', 'Instrumentos históricos y organología'),
(@taxonomy_version_id, 5, 'E7', 'Restauración y conservación de documentos');

-- Sociedad y música
INSERT IGNORE INTO temporary_categories (taxonomy_version_id, parent_id, code, name) VALUES
(@taxonomy_version_id, 6, 'F1', 'Música y sociedad'),
(@taxonomy_version_id, 6, 'F2', 'Música y salud*'),
(@taxonomy_version_id, 6, 'F3', 'Inclusión y participación cultural'),
(@taxonomy_version_id, 6, 'F4', 'Música en cine, videojuegos y publicidad'),
(@taxonomy_version_id, 6, 'F5', 'Educación comunitaria y proyectos sociales');

-- Ejecutar migración cruzando detalles reales a la tabla oficial
INSERT IGNORE INTO categories (taxonomy_version_id, parent_id, code, name)
SELECT taxonomy_version_id, parent_id, code, name FROM temporary_categories;

DROP TEMPORARY TABLE IF EXISTS temporary_categories;

-- Asegurar consistencia y permanencia a nivel de escritura
COMMIT;
-- Registro de la migración (requerido por tools/verify_database.py).
INSERT INTO schema_migrations (version, description)
VALUES ('006_taxonomy_seed', 'Taxonomía temática inicial 2026.11-A')
ON DUPLICATE KEY UPDATE description = VALUES(description);
