# Flujo de ingesta, estados y deduplicación

**Estado:** especificación funcional con una primera implementación de captura RSS/Atom y persistencia. El comportamiento descrito es el objetivo; las limitaciones de esta primera iteración se detallan al final.

## 1. Separar el estado de la fuente del estado de cada noticia

Una consulta a una fuente y el procesamiento de una noticia son operaciones distintas. Deben poder fallar y reanudarse de forma independiente.

### Ejecución de una fuente

Cada intento de consulta debe dejar constancia de:

- Fuente consultada.
- Inicio y fin.
- Resultado HTTP o del mecanismo API.
- Número de elementos recibidos, nuevos, ya conocidos y con error.
- Estado: iniciada, correcta, parcial o fallida.
- Mensaje de error, si existe.
- Datos de control HTTP disponibles, como ETag y Last-Modified.

Un fallo de una fuente no debe impedir consultar las demás. Si una fuente no ha cambiado, el recolector debe poder registrar el resultado sin volver a procesar todos sus elementos.

### Estado de procesamiento de una noticia

El estado de análisis debe ser independiente de la consulta de origen. Estados funcionales propuestos:

| Estado | Significado |
|---|---|
| CAPTURED | Elemento recibido y conservado, pendiente de normalización o análisis |
| NORMALIZED | Datos convertidos al formato común |
| PENDING_ANALYSIS | Pendiente de clasificación con IA |
| ANALYZED | Clasificación completada y resultado válido |
| REJECTED | No cumple los criterios de relevancia; se conserva el motivo |
| REVIEW | Información ambigua o insuficiente; requiere revisión o nuevo análisis |
| ERROR | Error técnico recuperable; conserva el punto de fallo |

El estado no debe borrar la información previa. Un error de IA, por ejemplo, no convierte en fallida la captura que ya se realizó correctamente.

## 2. Captura y normalización

Por cada elemento recibido se conservará, siempre que el canal lo proporcione:

- Identificador externo del elemento.
- URL original y URL canónica calculada.
- Título y descripción originales.
- Autor o editor.
- Fecha de publicación y fecha de actualización, si existen.
- Idioma declarado por el feed o elemento, si existe.
- Idioma detectado del título y descripción, código normalizado (preferiblemente BCP 47), evidencia y confianza.
- Idioma y URL de cada versión lingüística de la misma noticia, si la fuente las publica.
- Fecha de primera captura y última observación.
- Metadatos adicionales útiles del feed/API.
- Referencia a la fuente y a la ejecución que lo detectó.

No se debe inventar una fecha cuando el feed no la proporciona. Se distinguirán la fecha publicada por la fuente, la fecha de actualización y la fecha de captura.

Los datos originales se conservarán separados de los campos normalizados y de los textos generados por IA. La normalización no debe destruir el valor original. El idioma declarado por el canal no se aplicará automáticamente a todos sus elementos si la fuente puede publicar en varios idiomas.

## 3. Deduplicación en varios niveles

La deduplicación debe evitar tanto duplicados evidentes como fusiones incorrectas de noticias diferentes.

Orden de decisión:

1. **Identificador externo dentro de la misma fuente:** si el identificador coincide, se trata del mismo elemento de esa fuente.
2. **URL canónica:** si dos fuentes apuntan al mismo artículo original, se consideran apariciones de una misma noticia, conservando ambas procedencias.
3. **URL de redirección o agregador:** intentar resolver o normalizar parámetros de seguimiento cuando sea seguro. No eliminar parámetros que formen parte real de la identidad del recurso.
4. **Similitud de título y fecha:** utilizarla para detectar posibles duplicados, no para fusionarlos automáticamente sin evidencia suficiente.

La misma noticia puede aparecer en un feed institucional, en Google News y en otro agregador. El corpus debe mantener una noticia consolidada y varias relaciones de procedencia.

No deben fusionarse automáticamente:
- Dos artículos distintos sobre el mismo acontecimiento.
- Una noticia original y una actualización posterior con información sustancial nueva.
- Dos eventos diferentes con títulos parecidos.
- Una reseña y el lanzamiento al que hace referencia.

Cuando no haya certeza, es preferible conservar dos registros candidatos y marcarlos para revisión antes que perder información por una fusión errónea.

## 4. Actualizaciones de una noticia

Cuando una fuente vuelva a entregar un elemento conocido:

- Actualizar la fecha de última observación y los metadatos de esa aparición.
- Detectar si el título, descripción, URL o fecha de actualización han cambiado.
- No sobrescribir silenciosamente el contenido original ya almacenado.
- Si hay cambios sustanciales, conservar una nueva versión o una evidencia de cambio y permitir repetir el análisis.
- Si solo cambia el formato o un dato técnico irrelevante, no consumir otra llamada de IA.

La política exacta de versionado se concretará al diseñar la base de datos, pero el sistema debe poder distinguir una nueva captura de una noticia realmente nueva.

## 5. Clasificación y reintentos

- Solo se envía a IA el material necesario: título, descripción, metadatos y contexto permitido.
- La respuesta se valida contra los tipos de contenido y categorías controlados.
- Una respuesta inválida se marca como error de análisis, no como noticia descartada.
- Un error temporal puede reintentarse con espera progresiva y un límite configurable.
- Si se agota el límite, la noticia permanece pendiente para una ejecución posterior.
- Cambiar el prompt o la versión de taxonomía puede justificar un nuevo análisis, sin volver a descargar el feed.
- Cada resultado debe conservar proveedor, modelo, versión de prompt, versión de taxonomía, fecha y respuesta estructurada.
- El título y resumen editorial en español se almacenan separados del título y descripción originales.
- Las traducciones adicionales se guardan por idioma destino y vinculadas a la versión de contenido traducida; un error de traducción no cambia el estado de la captura ni de la clasificación.

La clasificación automática puede aceptar, rechazar o marcar para revisión. No debe inventar datos que no aparezcan en el material disponible.

## 6. Persistencia segura e idempotente

La carga debe ser repetible:

- Ejecutar dos veces la misma consulta no crea dos noticias ni dos apariciones idénticas de una misma fuente.
- Si el proceso se interrumpe, la siguiente ejecución continúa desde los estados pendientes.
- La captura se confirma en la base de datos antes de iniciar tareas costosas de IA.
- Si la IA falla, los datos capturados permanecen disponibles.
- Si falla la escritura de una noticia, no se debe dejar una relación de procedencia huérfana ni un estado que indique éxito.
- Los reintentos no deben multiplicar registros de error ni análisis idénticos sin necesidad.

Las operaciones de escritura relacionadas (noticia, procedencia y estado) deberán ser transaccionales cuando corresponda.

## 7. Verificaciones para dar por terminada la primera fase

La carga en MySQL/MariaDB se considerará funcional cuando se compruebe que:

1. Las fuentes activas se consultan y sus ejecuciones quedan registradas.
2. Los elementos recibidos se conservan con su procedencia y datos originales disponibles.
3. La misma noticia detectada por varias fuentes no se duplica, pero conserva todas sus procedencias.
4. Las noticias distintas no se fusionan solo por tener títulos parecidos.
5. La clasificación asigna tipo de contenido y categorías temáticas válidas.
6. Las entradas no pertinentes conservan el motivo de descarte.
7. Los errores de IA no hacen perder la captura ni obligan a descargar de nuevo.
8. Las ejecuciones repetidas no crean duplicados.
9. Los procesos interrumpidos pueden reanudarse.
10. Se puede consultar qué fuente aportó cada noticia y qué análisis produjo su clasificación.
11. Se conserva el idioma original con la evidencia de detección y el idioma de cada aparición.
12. El modelo admite traducciones adicionales sin sobrescribir el contenido original.

## 8. Implementación disponible (primera iteración)

La primera implementación está en `app/`:

- `feed_parser.py`: lectura RSS 2.0, Atom y RDF/RSS 1.0 con la biblioteca estándar.
- `collector.py`: consulta HTTP con timeout, ETag y Last-Modified; límite de 8 MiB por respuesta; normalización básica; hashes de identidad/contenido; persistencia de ejecuciones, publicaciones, observaciones y revisiones.
- `db.py` y `config.py`: conexión MariaDB mediante PyMySQL y lectura de `osap.toml`; se rechaza cualquier base distinta de `osap_noticias`.
- `cli.py`: listado de canales, activación explícita tras revisar términos y captura de canales activos.
- `tests/`: pruebas unitarias de parser y normalización de URL.

La migración 003 registra seis canales candidatos en estado `PAUSED`. No se consulta ningún canal hasta que se active expresamente. NPR y Music Business Worldwide no se incluyen en esta tanda por las restricciones ya documentadas.

### Límites conocidos de esta iteración

- No se ha ejecutado todavía una captura real contra los feeds desde el equipo local.
- No se descargan artículos completos ni se sigue el enlace de cada noticia; se conserva lo que entrega el feed.
- La consolidación por URL canónica es conservadora y no fusiona por similitud de título.
- Los feeds que no proporcionan URL ni identificador estable requieren una política adicional antes de considerarlos fiables.
- No hay todavía clasificación IA, detección avanzada de idioma ni resumen editorial.
- La política de retención se limita por ahora a metadatos y textos proporcionados por el feed; debe ajustarse a las condiciones de cada editor.

La implementación no modifica ni borra registros existentes y no inicia captura de fuentes en estado `PAUSED`.


## 9. Sondeo técnico sin persistencia

El comando `py -3 -m app.cli probe` permite comprobar los feeds de LOC – In the Muse y BnF – Partitions antes de activar la ingesta. Consulta únicamente las URLs exactas incluidas en una lista permitida y comprueba que las redirecciones permanezcan dentro del dominio institucional esperado. Resume el número de elementos y la presencia de URL, autor, fecha e identificador, sin imprimir títulos ni descripciones.

El sondeo no inserta ni actualiza filas, no crea `fetch_runs`, no guarda el cuerpo XML y no cambia el estado PAUSED de los canales. Se puede limitar con `--source-id ID`. No debe utilizarse para probar canales cuya política de uso sigue pendiente o prohíbe el uso automatizado previsto.

## 8. Tipo de contenido predeterminado por canal

Un canal puede declarar un tipo de contenido predeterminado como pista de clasificación. La migración 004 incorpora `source_channels.default_content_type_id`, relacionado con `content_types`.

El canal **Bibliographie nationale - Partitions (BnF, ID 6)** queda configurado con `BIBLIO` (Novedad bibliográfica). El recolector carga esta configuración al seleccionar los canales activos. La pista no equivale a una clasificación editorial validada: no se asigna automáticamente a `editorial_analyses`, no ejecuta IA y no convierte por sí sola una observación en noticia. Cuando se implemente el análisis, deberá utilizarse como valor inicial contextual y validarse frente al contenido real.

La separación permite que BnF se procese como fuente de registros bibliográficos, sin mezclar sus novedades con noticias periodísticas. Otros canales pueden dejar el valor nulo y clasificarse sin sesgo por tipo de fuente.
