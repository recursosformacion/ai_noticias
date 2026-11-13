# Modelo conceptual de persistencia

**Estado:** propuesta conceptual consolidada para revisión antes de diseñar el esquema MySQL/MariaDB.  
**Base de datos de destino acordada:** `osap_noticias` (MySQL/MariaDB).

**No es SQL ni una autorización para crear tablas.**

## 1. Principios del modelo

El modelo debe representar por separado:

1. El editor o institución que publica.
2. El canal técnico por el que se descubre contenido.
3. Cada observación recibida en una consulta.
4. La publicación concreta y su edición/idioma.
5. La noticia o historia lógica a la que pueden corresponder varias publicaciones.
6. El análisis editorial y sus sucesivas versiones.
7. Las traducciones del texto editorial.
8. La taxonomía y las asignaciones temáticas.

La distinción esencial es:

- **Noticia (news item):** historia o acontecimiento lógico consolidado.
- **Publicación (news publication):** artículo, anuncio, entrada o edición concreta publicada por un editor, con su URL, idioma y texto propios.
- **Observación (source observation):** registro tal como lo entregó un canal RSS/API en una ejecución determinada.

Una noticia puede tener varias publicaciones: por ejemplo, una edición en inglés y otra en español, o artículos de dos medios sobre el mismo hecho. Una publicación puede ser descubierta por varios canales. No se deben fusionar publicaciones solo porque compartan tema o acontecimiento.

## 2. Entidades conceptuales

### 2.1 Editoriales y canales

**Publisher (editor/fuente editorial)**
- Identidad del medio, biblioteca, universidad, revista o institución que publica.
- Nombre, dominio, país/ámbito, sitio principal, idioma(s) habituales y datos de atribución.
- Condiciones de uso, licencia, restricciones de IA, política de caché y URL de referencia a sus términos, con fecha de revisión.
- No representa un endpoint de descarga.

**Source channel (canal técnico)**
- Un feed RSS/Atom, endpoint API, OAI-PMH o consulta de agregador.
- Pertenece a un publisher cuando el canal es propio; para agregadores se identifica el proveedor del canal y se resuelve por separado el publisher del artículo.
- URL, protocolo/formato, tipo de contenido esperado, idioma declarado, ámbito temático orientativo, frecuencia, estado, configuración de consulta y última comprobación.
- Cabeceras de control como ETag y Last-Modified, cuando proceda.
- Puede haber varios canales por publisher y varios canales de descubrimiento que conduzcan al mismo publisher.

**Fetch run (ejecución de captura)**
- Una ejecución concreta de un canal.
- Inicio/fin, URL solicitada/final, HTTP/API status, latencia, cabeceras relevantes, número recibido/nuevo/conocido/error, resultado y mensaje técnico.
- Estados diferenciados: RUNNING, SUCCESS, PARTIAL, FAILED, NOT_MODIFIED.
- Permite medir salud y reanudar sin confundir el fallo de un canal con el estado de una noticia.

### 2.2 Observaciones y publicaciones

**Source observation (observación de origen)**
- Cada elemento recibido desde un canal durante una ejecución.
- Identificador externo, GUID, URL tal como llegó, título/fragmento originales, autor, fechas, idioma declarado, metadatos y payload bruto permitido.
- Referencia a canal y ejecución.
- Se conserva el dato original y se registra su primera y última observación.
- Restricción de unicidad preferente: canal + identificador externo; si no existe, una huella técnica documentada, sin asumir que la URL es siempre estable.
- Si el contenido del elemento cambia, se conserva una revisión/evidencia de cambio, no se sobrescribe silenciosamente.

**Observation revision (revisión de observación)**
- Instantánea de campos relevantes cuando el elemento cambia de forma significativa.
- Fecha de observación, huella del contenido y campos originales.
- Evita perder la evidencia de actualizaciones y permite decidir si hace falta repetir análisis.
- No es necesario guardar cada consulta idéntica; sí los cambios y los eventos de primera/última observación.

**News publication (publicación/edición)**
- Una publicación concreta del editor: URL canónica, URL original, identificador del editor, título y descripción/fragmento originales, autor, fecha de publicación y actualización, idioma y metadatos propios.
- Relación con un publisher.
- Puede vincularse a varias source observations que la descubrieron.
- Puede estar asociada a una news item consolidada.
- Una edición lingüística oficial es otra publicación, aunque se relacione con la misma noticia.
- Se registra la fuente de la identificación del idioma y la confianza cuando no es declarada fiable.

**News item (noticia consolidada)**
- Agrupación lógica de publicaciones que informan de la misma noticia o acontecimiento.
- Identificador interno estable, estado editorial, primera/última detección y referencia a la publicación principal cuando proceda.
- No contiene como único original un texto copiado de una publicación arbitraria: los originales y sus idiomas permanecen en cada news publication.
- La relación publication–news item debe poder quedar pendiente o ser revisada si la deduplicación no es concluyente.
- No fusionar automáticamente artículos distintos sobre el mismo tema, ni una actualización sustancial con el artículo inicial, ni una crítica con el evento reseñado.

### 2.3 Análisis y contenido editorial

**Analysis run (ejecución de análisis)**
- Cada intento de clasificación/redacción de una publicación o noticia.
- Proveedor, modelo, versión de prompt, versión de taxonomía, fecha, idioma(s) de entrada, campos enviados, estado, coste/uso si está disponible y error.
- Debe identificar exactamente qué publicación(es) y qué revisión(es) de contenido se usaron como evidencia de entrada; un resultado no puede quedar asociado solo a una noticia abstracta sin trazabilidad del material analizado.
- Puede analizar una publicación individual o varias publicaciones relacionadas, pero debe registrar la selección concreta de entradas.
- Debe distinguir análisis completado, respuesta inválida, fallo temporal y pendiente.
- La captura no depende del éxito del análisis.

**Editorial analysis (resultado editorial)**
- Resultado estructurado de una ejecución válida: pertinencia, tipo de contenido, categorías propuestas, idioma detectado, evidencia, confianza, motivo y necesidad de revisión.
- El idioma se detecta por publicación/revisión; la pertinencia, el tipo y los temas se consolidan en la noticia cuando la evidencia permite afirmar que varias publicaciones tratan del mismo hecho.
- Debe conservarse el histórico; un nuevo prompt o modelo genera otro resultado, no reemplaza silenciosamente el anterior.
- El estado editorial vigente se puede derivar del último resultado aceptado, conservando la trazabilidad.
- Las asignaciones de categorías se guardan como relaciones controladas y versionadas, no solo como texto JSON.

**Editorial text (texto editorial base)**
- Título y resumen originales redactados por ai_noticias, en español en la primera fase.
- Identifica la publicación/noticia de referencia, el idioma, la versión del análisis que lo produjo, fecha y estado.
- No sustituye ni modifica título y descripción de la publicación original.
- El resumen se basa únicamente en la información permitida y disponible; no reproduce el artículo completo.

**Editorial translation (traducción editorial)**
- Traducción de un texto editorial propio a un idioma destino.
- Relación con el texto editorial exacto que se tradujo, no solo con la noticia abstracta.
- Idioma destino, contenido traducido, proveedor/modelo, prompt, fecha, estado y huella/versión de origen.
- Estados: PENDING, COMPLETED, ERROR, STALE.
- No se generan traducciones masivas en esta fase; el modelo solo deja preparada su persistencia.
- Una versión oficial del editor no se almacena como traducción editorial: se representa como otra news publication relacionada con la misma news item.

### 2.4 Taxonomía

**Taxonomy version**
- Versión publicada del árbol temático y de los tipos de contenido.
- Fecha de vigencia, descripción y estado.

**Category**
- Nodo de la jerarquía temática, con código estable, nombre, descripción, padre y estado.
- No se confunde con personas, obras, instituciones, lugares ni otras entidades mencionadas.

**News item category**
- Relación entre noticia y categoría, vinculada al análisis que la justificó y a la versión de taxonomía.
- Puede registrar confianza, justificación breve y si fue aceptada automáticamente o revisada.
- Se permiten varias categorías por noticia; los padres pueden deducirse de sus descendientes y no tienen por qué duplicarse como etiquetas explícitas.

**Content type**
- Catálogo controlado separado de la taxonomía temática: NEWS, EVENT, RELEASE, RESEARCH, BIBLIO, COLLECTION, INTERVIEW, OPINION, OTHER y REVIEW.
- Se versiona o conserva su historial si cambian sus definiciones.

## 3. Relaciones principales

- Un publisher tiene uno o varios source channels.
- Un source channel tiene muchas fetch runs.
- Una fetch run recibe muchas source observations.
- Una source observation puede enlazarse con una news publication.
- Una news publication puede ser detectada por muchas source observations.
- Un publisher publica muchas news publications.
- Una news item agrupa una o varias news publications.
- Una news item puede tener varias ejecuciones/resultados de análisis a lo largo del tiempo.
- Una news item puede tener varias categorías mediante news item categories.
- Una news item puede disponer de uno o varios textos editoriales versionados.
- Un texto editorial puede tener traducciones a distintos idiomas.
- Una news item puede tener varias publicaciones oficiales en distintos idiomas.

## 4. Estados: separar procesos independientes

No se debe crear un único estado que mezcle captura, clasificación, traducción y autorización.

### Estado del canal
ACTIVE, PAUSED, DEGRADED, RETIRED.

### Estado de la ejecución de captura
RUNNING, SUCCESS, PARTIAL, FAILED, NOT_MODIFIED.

### Estado de observación/publicación
CAPTURED, NORMALIZED, LINKED, UNMATCHED, ERROR.

### Estado de análisis
PENDING, RUNNING, COMPLETED, REJECTED, REVIEW, ERROR.

REJECTED significa que el contenido no es pertinente; no equivale a ERROR. REVIEW significa que hay incertidumbre editorial.

### Estado de traducción
PENDING, COMPLETED, ERROR, STALE.

Los estados se acompañan de marcas temporales, intentos y errores. Una publicación capturada permanece disponible aunque la IA o una traducción fallen.

## 5. Identidad, deduplicación y versionado

La identidad se resuelve en niveles:

1. Observación: canal + GUID/ID externo, si es estable.
2. Publicación: publisher + identificador editorial, DOI o URL canónica, según disponibilidad.
3. Noticia: agrupación de publicaciones que corresponden al mismo hecho.

Una URL coincidente es evidencia fuerte, pero debe normalizarse con cuidado: no se eliminan parámetros que formen parte de la identidad real. Una similitud de título/fecha solo genera candidatos. Los casos dudosos quedan separados o pendientes de revisión.

Se conservarán:
- La primera captura y la última observación.
- Los cambios sustanciales del título, descripción, URL, idioma o fechas.
- Los análisis previos y sus versiones de modelo/prompt/taxonomía.
- El texto editorial de cada versión y las traducciones vinculadas a su texto de origen.
- La relación entre ediciones oficiales en diferentes idiomas.

No es necesario guardar un duplicado completo del mismo payload en cada ejecución sin cambios. La estrategia de historial debe conservar cambios relevantes y permitir auditar el origen.

## 6. Campos temporales y lingüísticos

Se distinguen, como mínimo:
- Fecha de publicación declarada por el editor.
- Fecha de actualización declarada.
- Fecha/hora de captura.
- Fecha/hora de primera y última observación.
- Fecha de evento, cuando exista, separada de la publicación.
- Zona horaria original si está disponible y representación temporal normalizada.

Para idiomas:
- Idioma declarado por canal.
- Idioma declarado por elemento/publicación.
- Idioma detectado, código BCP 47, evidencia y confianza.
- Idioma de cada publicación oficial.
- Idioma del texto editorial base y de cada traducción.

No se hereda automáticamente el idioma del canal a cada elemento.

## 7. Retención, privacidad y derechos

La captura debe almacenar únicamente los metadatos y fragmentos permitidos por cada fuente. La existencia de un feed público no supone permiso para conservar el contenido completo, redistribuirlo, traducirlo o enviarlo a IA.

Por canal se documentarán las restricciones aplicables: uso personal/no comercial, límites de caché, atribución, enlaces, prohibiciones de minería o IA, permisos y fecha de revisión. Cuando las condiciones prohíban o no aclaren el procesamiento, el canal no se activará para esa operación hasta resolverlo.

No se incorporan usuarios, preferencias, suscripciones, listas personales ni boletines al modelo de esta fase. Tampoco se almacena información personal innecesaria de autores o lectores.

## 8. Alcance mínimo de la primera versión

El esquema físico debe cubrir solamente:

1. Publishers y source channels.
2. Fetch runs.
3. Source observations y revisiones necesarias.
4. News publications y su relación con news items.
5. Análisis y resultados editoriales versionados.
6. Taxonomía, tipos de contenido y asignaciones.
7. Textos editoriales en español y estructura de traducciones, sin generación masiva.

Quedan fuera: cuentas de usuario, preferencias, personalización, boletines, suscripciones, campañas, métricas de lectura y API pública de consulta.

## 9. Decisiones técnicas que se resolverán al diseñar MySQL

- Versión mínima de MySQL/MariaDB y charset/collation UTF-8.
- Tipos y precisión para fechas, zonas horarias, URL, JSON y textos.
- Claves primarias, claves externas e índices de unicidad.
- Política de normalización de URL y huellas.
- Nivel de versionado de observaciones y contenido editorial.
- Transacciones y concurrencia entre workers.
- Retención de payloads brutos y errores según condiciones de cada fuente.
- Índices de consulta por estado, fecha, fuente, idioma y categoría.
- Estrategia de migración/backup si se integra más adelante con otros sistemas (no forma parte de esta fase).

El diseño SQL solo comenzará cuando se haya revisado este modelo conceptual y se hayan resuelto las restricciones de uso de las fuentes que vayan a alimentar el corpus.
