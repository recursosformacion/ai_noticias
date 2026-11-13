# Diseño físico propuesto para MySQL/MariaDB

**Estado:** borrador técnico acompañado por una primera migración SQL, aún no ejecutada ni validada contra el servidor. Traduce el modelo conceptual del documento 08 a tablas, claves e índices.

**Base de datos:** `osap_noticias`.

## 1. Criterios físicos

- Motor transaccional InnoDB para todas las tablas.
- Codificación `utf8mb4`; collation explícita y uniforme, inicialmente `utf8mb4_unicode_ci` si está disponible en la versión elegida. Las comparaciones de URL, GUID, hashes y códigos técnicos serán binarias o con collation sensible a mayúsculas cuando corresponda.
- Claves primarias internas `BIGINT UNSIGNED AUTO_INCREMENT`. Las relaciones usarán esos IDs, no nombres ni URLs.
- Fechas almacenadas en UTC. La aplicación convierte a la zona horaria de presentación. Para fechas de publicación se conserva también el texto/valor recibido cuando su interpretación sea dudosa.
- Nombres de tablas y columnas en `snake_case`, singular/plural coherente y sin prefijos innecesarios.
- Campos de estado con valores controlados por la aplicación; no usar ENUM para estados que previsiblemente evolucionen.
- No guardar artículos completos ni payloads sin límite. Los fragmentos y respuestas originales se limitan a lo permitido por cada fuente.
- Las credenciales y parámetros de conexión se obtienen de configuración externa. No se versionan en Git.
- La base se crea como `osap_noticias`; este diseño no crea ni modifica ninguna base de datos.

## 2. Tablas propuestas

### 2.1 Catálogo de fuentes

#### `publishers`
Identidad editorial del medio o institución.

- `id` BIGINT PK.
- `name` VARCHAR(255) NOT NULL.
- `website_url` VARCHAR(2048) NULL.
- `domain` VARCHAR(255) NULL.
- `country_code` CHAR(2) NULL.
- `description` TEXT NULL.
- `created_at`, `updated_at` DATETIME NOT NULL.
- Índices: UNIQUE opcional sobre `domain` solo cuando esté normalizado y no sea NULL; índice por `name`.

No se debe identificar un publisher únicamente por el nombre: los dominios y las fusiones/cambios editoriales requieren revisión.

#### `source_channels`
Cada feed, API, endpoint OAI-PMH o consulta de agregador.

- `id` BIGINT PK.
- `publisher_id` BIGINT NULL FK → publishers.
- `provider_name` VARCHAR(255) NOT NULL: proveedor técnico del canal (por ejemplo, Google News), distinto del publisher del artículo.
- `name` VARCHAR(255) NOT NULL.
- `url` VARCHAR(2048) NOT NULL.
- `protocol` VARCHAR(30) NOT NULL: RSS, ATOM, API, OAI_PMH u otro código controlado.
- `format` VARCHAR(30) NULL.
- `declared_language` VARCHAR(35) NULL.
- `topic_hint` VARCHAR(500) NULL.
- `poll_interval_minutes` INT UNSIGNED NULL.
- `status` VARCHAR(20) NOT NULL.
- `terms_url` VARCHAR(2048) NULL.
- `terms_reviewed_at` DATETIME NULL.
- `usage_policy` TEXT NULL: notas y restricciones operativas, no sustituyen la URL de términos.
- `etag` VARCHAR(500) NULL; `last_modified` VARCHAR(500) NULL.
- `last_checked_at` DATETIME NULL; `created_at`, `updated_at` DATETIME NOT NULL.
- Índices: UNIQUE(`url`(longitud indexable compatible) o hash de URL completa); INDEX(`status`, `last_checked_at`); INDEX(`publisher_id`).

Para evitar límites de índice sobre URL larga, se recomienda almacenar además `url_sha256` BINARY(32) NOT NULL y aplicar UNIQUE(`url_sha256`). La aplicación calcula el hash de la URL normalizada y comprueba igualdad completa ante cualquier colisión.

### 2.2 Captura y observaciones

#### `fetch_runs`
Una ejecución de consulta de un canal.

- `id` BIGINT PK.
- `source_channel_id` BIGINT NOT NULL FK → source_channels.
- `started_at` DATETIME NOT NULL; `finished_at` DATETIME NULL.
- `requested_url` VARCHAR(2048) NOT NULL; `final_url` VARCHAR(2048) NULL.
- `http_status` SMALLINT UNSIGNED NULL.
- `result_status` VARCHAR(20) NOT NULL: RUNNING, SUCCESS, PARTIAL, FAILED, NOT_MODIFIED.
- `items_received`, `items_new`, `items_known`, `items_error` INT UNSIGNED NOT NULL DEFAULT 0.
- `duration_ms` INT UNSIGNED NULL.
- `error_code` VARCHAR(100) NULL; `error_message` TEXT NULL.
- Índices: INDEX(`source_channel_id`, `started_at`); INDEX(`result_status`, `started_at`).

#### `source_observations`
Un elemento recibido desde un canal. Conserva los datos originales y enlaza la publicación normalizada cuando se identifica.

- `id` BIGINT PK.
- `source_channel_id` BIGINT NOT NULL FK → source_channels.
- `fetch_run_id` BIGINT NOT NULL FK → fetch_runs.
- `external_id` VARCHAR(1000) NULL.
- `external_id_hash` BINARY(32) NULL.
- `url_original` VARCHAR(2048) NULL.
- `title_original` TEXT NULL; `description_original` MEDIUMTEXT NULL.
- `author_original` VARCHAR(500) NULL.
- `published_at_raw` VARCHAR(100) NULL; `published_at` DATETIME NULL.
- `updated_at_raw` VARCHAR(100) NULL; `updated_at` DATETIME NULL.
- `declared_language` VARCHAR(35) NULL.
- `payload_metadata` JSON/TEXT NULL: solo metadatos permitidos, con tamaño acotado.
- `content_hash` BINARY(32) NOT NULL.
- `first_seen_at`, `last_seen_at` DATETIME NOT NULL.
- `news_publication_id` BIGINT NULL FK → news_publications.
- `processing_status` VARCHAR(20) NOT NULL.
- Índices: UNIQUE(`source_channel_id`, `external_id_hash`) cuando exista ID; INDEX(`fetch_run_id`); INDEX(`news_publication_id`); INDEX(`content_hash`); INDEX(`last_seen_at`).

La unicidad con ID externo se implementará mediante una columna hash nullable y una estrategia compatible con el motor elegido; las filas sin ID no deben colisionar por NULL. La aplicación verifica el identificador original tras encontrar el hash.

#### `observation_revisions`
Historial solo cuando cambian campos sustanciales de una observación.

- `id` BIGINT PK.
- `source_observation_id` BIGINT NOT NULL FK → source_observations.
- `revision_number` INT UNSIGNED NOT NULL.
- `observed_at` DATETIME NOT NULL.
- `content_hash` BINARY(32) NOT NULL.
- `title_original` TEXT NULL; `description_original` MEDIUMTEXT NULL.
- `url_original` VARCHAR(2048) NULL.
- `published_at_raw` VARCHAR(100) NULL; `updated_at_raw` VARCHAR(100) NULL.
- `metadata` JSON/TEXT NULL.
- UNIQUE(`source_observation_id`, `revision_number`); INDEX(`content_hash`).

No se crea una revisión en cada sondeo idéntico; solo ante cambios relevantes.

### 2.3 Publicaciones y noticias consolidadas

#### `news_items`
Historia lógica común a una o varias publicaciones.

- `id` BIGINT PK.
- `status` VARCHAR(20) NOT NULL: ACTIVE, MERGED, DISMISSED, REVIEW.
- `primary_publication_id` BIGINT NULL FK → news_publications.
- `first_detected_at`, `last_detected_at` DATETIME NOT NULL.
- `created_at`, `updated_at` DATETIME NOT NULL.
- Índices: INDEX(`status`, `last_detected_at`); INDEX(`first_detected_at`).

#### `news_publications`
Artículo, anuncio o edición concreta publicada por un editor.

- `id` BIGINT PK.
- `publisher_id` BIGINT NULL FK → publishers.
- `news_item_id` BIGINT NULL FK → news_items.
- `external_id` VARCHAR(1000) NULL.
- `canonical_url` VARCHAR(2048) NULL; `original_url` VARCHAR(2048) NULL.
- `url_sha256` BINARY(32) NULL.
- `title_original` TEXT NOT NULL; `description_original` MEDIUMTEXT NULL.
- `author_original` VARCHAR(500) NULL.
- `published_at` DATETIME NULL; `updated_at` DATETIME NULL.
- `published_at_raw` VARCHAR(100) NULL; `updated_at_raw` VARCHAR(100) NULL.
- `language_declared` VARCHAR(35) NULL; `language_detected` VARCHAR(35) NULL.
- `language_evidence` VARCHAR(30) NULL; `language_confidence` DECIMAL(5,4) NULL.
- `first_seen_at`, `last_seen_at` DATETIME NOT NULL.
- `created_at`, `updated_at` DATETIME NOT NULL.
- Índices: INDEX(`publisher_id`, `published_at`); INDEX(`news_item_id`); INDEX(`language_detected`, `published_at`); INDEX(`url_sha256`).

La identidad de publicación no debe imponerse con UNIQUE sobre URL sin estudiar redirecciones, parámetros significativos y reutilización de URL. La aplicación normaliza, busca candidatos y confirma identidad. `news_item_id` puede quedar NULL mientras la relación entre publicaciones sea dudosa.

La relación `news_items.primary_publication_id` es una referencia de conveniencia. Debe validarse en la aplicación que la publicación principal pertenece a esa misma noticia.

### 2.4 Análisis editorial

#### `analysis_runs`
Cada ejecución del proveedor de IA o análisis equivalente.

- `id` BIGINT PK.
- `news_item_id` BIGINT NOT NULL FK → news_items.
- `provider` VARCHAR(50) NOT NULL; `model` VARCHAR(150) NOT NULL.
- `prompt_version` VARCHAR(80) NOT NULL; `taxonomy_version_id` BIGINT NULL FK → taxonomy_versions.
- `status` VARCHAR(20) NOT NULL: PENDING, RUNNING, COMPLETED, INVALID, ERROR.
- `started_at` DATETIME NULL; `finished_at` DATETIME NULL.
- `input_language` VARCHAR(35) NULL.
- `usage_input_tokens`, `usage_output_tokens` BIGINT UNSIGNED NULL.
- `cost_amount` DECIMAL(12,6) NULL; `cost_currency` CHAR(3) NULL.
- `error_code` VARCHAR(100) NULL; `error_message` TEXT NULL.
- `raw_response` MEDIUMTEXT NULL, sujeto a límites y política de retención.
- `created_at` DATETIME NOT NULL.
- Índices: INDEX(`news_item_id`, `created_at`); INDEX(`status`, `created_at`).

#### `analysis_inputs`
Entradas exactas utilizadas en un análisis; resuelve la trazabilidad publicación/revisión.

- `id` BIGINT PK.
- `analysis_run_id` BIGINT NOT NULL FK → analysis_runs.
- `news_publication_id` BIGINT NOT NULL FK → news_publications.
- `observation_revision_id` BIGINT NULL FK → observation_revisions.
- `content_hash` BINARY(32) NOT NULL.
- `input_role` VARCHAR(20) NOT NULL.
- UNIQUE(`analysis_run_id`, `news_publication_id`, `content_hash`); INDEX(`news_publication_id`).

#### `editorial_analyses`
Resultado estructurado validado de un análisis.

- `id` BIGINT PK.
- `analysis_run_id` BIGINT NOT NULL UNIQUE FK → analysis_runs.
- `is_relevant` BOOLEAN NOT NULL.
- `content_type_id` BIGINT NULL FK → content_types.
- `language_detected` VARCHAR(35) NULL; `language_evidence` VARCHAR(30) NULL.
- `language_confidence` DECIMAL(5,4) NULL.
- `relevance_reason` TEXT NULL.
- `confidence` DECIMAL(5,4) NULL.
- `needs_review` BOOLEAN NOT NULL DEFAULT FALSE.
- `created_at` DATETIME NOT NULL.

Un intento inválido o fallido no genera editorial_analysis; permanece registrado en analysis_runs.

### 2.5 Taxonomía y tipos

#### `taxonomy_versions`
- `id` BIGINT PK.
- `version_code` VARCHAR(40) NOT NULL UNIQUE.
- `description` TEXT NULL.
- `status` VARCHAR(20) NOT NULL: DRAFT, ACTIVE, RETIRED.
- `effective_at` DATETIME NULL; `created_at` DATETIME NOT NULL.

#### `categories`
- `id` BIGINT PK.
- `taxonomy_version_id` BIGINT NOT NULL FK → taxonomy_versions.
- `parent_id` BIGINT NULL FK → categories.
- `code` VARCHAR(100) NOT NULL.
- `name` VARCHAR(255) NOT NULL.
- `description` TEXT NULL.
- `status` VARCHAR(20) NOT NULL.
- UNIQUE(`taxonomy_version_id`, `code`); INDEX(`parent_id`).

La aplicación debe impedir ciclos y comprobar que padre e hijo pertenecen a la misma versión de taxonomía.

#### `content_types`
- `id` BIGINT PK.
- `code` VARCHAR(40) NOT NULL UNIQUE.
- `name` VARCHAR(100) NOT NULL.
- `description` TEXT NULL.
- `status` VARCHAR(20) NOT NULL.

#### `news_item_categories`
Asignaciones temáticas aceptadas para una noticia.

- `id` BIGINT PK.
- `news_item_id` BIGINT NOT NULL FK → news_items.
- `category_id` BIGINT NOT NULL FK → categories.
- `editorial_analysis_id` BIGINT NULL FK → editorial_analyses.
- `confidence` DECIMAL(5,4) NULL.
- `assignment_status` VARCHAR(20) NOT NULL: PROPOSED, ACCEPTED, REJECTED.
- `assigned_at` DATETIME NOT NULL.
- UNIQUE(`news_item_id`, `category_id`); INDEX(`category_id`, `news_item_id`).

La categoría ya identifica su versión de taxonomía. Si se necesita conservar asignaciones históricas de distintas versiones simultáneamente, se retirará la unicidad simple y se añadirá historial explícito antes de la implementación.

### 2.6 Textos editoriales y traducciones

#### `editorial_texts`
Título y resumen propios, no copiados de la publicación original.

- `id` BIGINT PK.
- `news_item_id` BIGINT NOT NULL FK → news_items.
- `editorial_analysis_id` BIGINT NOT NULL FK → editorial_analyses.
- `language_code` VARCHAR(35) NOT NULL DEFAULT 'es'.
- `title` VARCHAR(500) NOT NULL.
- `summary` TEXT NOT NULL.
- `status` VARCHAR(20) NOT NULL: DRAFT, ACCEPTED, SUPERSEDED.
- `created_at` DATETIME NOT NULL.
- INDEX(`news_item_id`, `language_code`, `created_at`).

Se conserva cada versión. La aplicación determina cuál es la vigente; no se sobrescribe una redacción anterior.

#### `editorial_translations`
Traducciones del texto editorial propio, no ediciones oficiales del editor.

- `id` BIGINT PK.
- `editorial_text_id` BIGINT NOT NULL FK → editorial_texts.
- `target_language_code` VARCHAR(35) NOT NULL.
- `title` VARCHAR(500) NOT NULL; `summary` TEXT NOT NULL.
- `provider` VARCHAR(50) NOT NULL; `model` VARCHAR(150) NOT NULL.
- `prompt_version` VARCHAR(80) NOT NULL.
- `source_content_hash` BINARY(32) NOT NULL.
- `status` VARCHAR(20) NOT NULL: PENDING, COMPLETED, ERROR, STALE.
- `created_at` DATETIME NOT NULL; `completed_at` DATETIME NULL.
- UNIQUE(`editorial_text_id`, `target_language_code`, `source_content_hash`); INDEX(`status`, `target_language_code`).

## 3. Relaciones y reglas de integridad

- Publisher 1:N source_channels y news_publications.
- Source_channel 1:N fetch_runs y source_observations.
- Fetch_run 1:N source_observations.
- Source_observation 1:N observation_revisions y N:1 news_publication.
- News_item 1:N news_publications; una publicación pertenece como máximo a una noticia consolidada.
- News_item 1:N analysis_runs; cada análisis identifica sus entradas concretas en analysis_inputs.
- Analysis_run 1:0..1 editorial_analysis.
- Taxonomy_version 1:N categories; category puede tener padre en la misma versión.
- News_item N:M categories mediante news_item_categories.
- News_item 1:N editorial_texts; editorial_text 1:N editorial_translations.

Las claves foráneas usarán inicialmente `ON DELETE RESTRICT`. No se borrará en cascada el historial editorial ni de captura. Las bajas lógicas se resolverán mediante estados; una política de purga física requerirá decisión específica y comprobación de obligaciones de retención.

## 4. Transacciones, concurrencia e idempotencia

1. Cada fetch_run se crea antes de consultar el canal y se cierra con su resultado, incluso si hay error.
2. Cada observación se inserta o actualiza mediante la clave de identidad del canal; las colisiones se verifican comparando el identificador original.
3. La creación/enlace de una publicación y la actualización de la observación se realizan en una transacción.
4. La consolidación de publicaciones en news_items es una operación separada y conservadora; no se fusionan automáticamente candidatos dudosos.
5. Cada análisis se registra antes de llamar al proveedor. Su resultado validado y las asignaciones/editorial_texts se guardan en una transacción.
6. Un fallo de IA deja intactas la captura y la publicación.
7. Los workers reclaman trabajo mediante actualización atómica de estado y marca temporal/lease; no se mantiene una transacción SQL abierta durante una llamada HTTP o IA.
8. Los reintentos generan nuevos fetch_runs o analysis_runs; no borran los fallidos.

## 5. Índices y consultas prioritarias

El diseño prioriza:
- Canales activos que ya deben consultarse.
- Historial de ejecuciones por canal y fallos recientes.
- Observaciones de una ejecución y observaciones no vinculadas.
- Publicaciones por fecha, publisher, idioma y noticia consolidada.
- Noticias pendientes de análisis, revisión o clasificación.
- Noticias por categoría y fecha.
- Traducciones pendientes o desactualizadas.

No se crearán índices sobre cada campo por anticipado. Se validarán con consultas reales y `EXPLAIN`; se evitarán índices redundantes y prefijos sobre textos largos salvo necesidad demostrada.

## 6. Decisiones que deben cerrarse antes del SQL ejecutable

1. Versión real del servidor y compatibilidad MySQL/MariaDB.
2. Política exacta de collation y sensibilidad a mayúsculas para dominios, URL e identificadores.
3. Estrategia de unicidad portable para URL e identificadores externos largos (hash binario + verificación).
4. Retención de payload_metadata, raw_response, errores y revisiones, según las condiciones de cada fuente.
5. Si la clasificación vigente debe conservar simultáneamente asignaciones de varias versiones de taxonomía o solo las aceptadas en la versión activa.
6. Política de consolidación/reversión de news_items y selección de publicación principal.
7. Valores iniciales de estados, tipos de contenido y categorías; deben cargarse mediante datos semilla versionados.
8. Política de borrado/anonimización y copias de seguridad operativas.

## 7. Fuera de alcance

No se incluyen usuarios, preferencias, suscripciones, boletines, campañas, métricas de lectura, endpoints públicos ni integración de cuentas OSAP. Tampoco se crea aquí ningún fichero de credenciales, migración SQL ni conexión real al servidor.

## 8. Compatibilidad y migraciones

La versión de desarrollo comunicada es **MariaDB 10.4.32**. La migración inicial y el catálogo semilla se han revisado a nivel de sintaxis para ese motor: `database/migrations/001_initial_schema.sql` y `002_seed_content_types.sql`. Se utilizan InnoDB, `utf8mb4`, `DATETIME(6)`, JSON (tipo compatible en MariaDB), claves foráneas e inserciones `ON DUPLICATE KEY UPDATE`.

Esta revisión estática no sustituye una ejecución real. La creación de `osap_noticias` y sus tablas queda pendiente de lanzar el inicializador desde el entorno local y comprobar el resultado. Las migraciones se ejecutan en orden; `schema_migrations` registra las aplicadas y las operaciones de creación/semilla están preparadas para repetirse sin duplicar objetos o tipos.

## 9. Próximo paso

Ejecutar `crear_bbdd_osap_noticias.bat` desde la carpeta del proyecto o mediante un acceso directo del escritorio. El script utiliza el cliente `mysql` de MariaDB y solicita el usuario y la contraseña de desarrollo de forma interactiva; no guarda credenciales.
