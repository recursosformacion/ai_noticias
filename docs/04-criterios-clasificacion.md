# Criterios editoriales y de clasificación

**Estado:** propuesta operativa para la primera fase. Debe validarse con noticias reales, pero permite comenzar las pruebas de clasificación sin confundir tipos de contenido con temas musicales.

## 1. Qué debe entrar en el corpus

El objetivo es recopilar información nueva y verificable relacionada con la música en sentido amplio. La relevancia no depende de que el contenido trate música clásica o coral: se incluyen todos los géneros, actividades e industrias musicales.

Una entrada es candidata cuando cumple al menos una de estas condiciones:

- Informa de un hecho, decisión, acontecimiento, lanzamiento, descubrimiento o cambio relacionado de forma sustancial con la música.
- Anuncia una actividad musical concreta: concierto, festival, curso, convocatoria, concurso, estreno o temporada.
- Comunica una publicación académica o resultado de investigación musical identificable.
- Registra una novedad bibliográfica, documental o de catálogo relevante para partituras, grabaciones, manuscritos, archivos o patrimonio musical.
- Describe una iniciativa, política, herramienta o avance tecnológico cuyo objeto o impacto musical sea sustancial.

No es necesario que la publicación se denomine a sí misma «noticia». El sistema debe identificar qué clase de contenido es y conservar esa distinción.

## 2. Qué debe excluirse o quedar en espera

Excluir, salvo que exista un contexto musical claro:

- Contenido donde términos musicales aparezcan solo como coincidencia, etiqueta incidental o expresión ambigua.
- Publicidad, publirreportajes o páginas comerciales sin información nueva verificable. Una noticia sobre una operación empresarial o un producto relevante sí puede entrar, etiquetada como industria o tecnología.
- Páginas de navegación, categorías, páginas de autor, resultados de búsqueda vacíos y avisos técnicos.
- Contenido duplicado sin información nueva.
- Opinión genérica o promoción de un artista sin novedad, acontecimiento o aportación informativa identificable.
- Contenido sin título o descripción suficiente para determinar su pertinencia: no descartarlo definitivamente; marcarlo como pendiente de análisis.
- Información cuyo único vínculo musical sea una mención secundaria que no aporte valor informativo.

La falta de resumen en un feed no implica por sí sola exclusión. Se podrá clasificar con título, metadatos y contexto de la fuente, marcando una confianza menor cuando proceda.

## 3. Dos ejes independientes: tipo de contenido y tema

Cada registro debe poder describirse mediante dos clasificaciones distintas.

### 3.1 Tipo de contenido

Se propone un catálogo controlado inicial:

| Código | Tipo | Uso |
|---|---|---|
| NEWS | Noticia | Hecho, anuncio, decisión o acontecimiento de actualidad |
| EVENT | Agenda / evento | Concierto, festival, curso, convocatoria o actividad futura |
| RELEASE | Lanzamiento | Publicación de disco, vídeo, grabación, edición o nueva obra |
| RESEARCH | Investigación / publicación académica | Artículo, tesis, proyecto o resultado de investigación |
| BIBLIO | Novedad bibliográfica | Nueva partitura, libro, edición o registro bibliográfico |
| COLLECTION | Colección / catálogo / archivo | Incorporación, digitalización o actualización de fondos y registros |
| INTERVIEW | Entrevista / perfil | Entrevista o perfil con contenido informativo propio |
| OPINION | Opinión / crítica | Reseña, crítica o artículo de opinión; conservar separado de la noticia |
| OTHER | Otro contenido pertinente | Contenido musical útil que no encaja todavía en los tipos anteriores |
| REVIEW | Pendiente de revisión | Información insuficiente, ambigua o contradictoria |

El tipo de contenido no sustituye a las categorías temáticas. Un concierto de música coral puede ser EVENT y recibir las categorías «Música coral y vocal», «Conciertos, giras y temporadas» y, si procede, «Música religiosa y litúrgica».

### 3.2 Tema musical

Se asignan una o varias categorías del árbol temático de la propuesta funcional (sección 5). La clasificación se basa en el contenido concreto, no solo en la fuente ni en el nombre del medio.

Ejemplos:
- Una noticia sobre una nueva ley de derechos de autor para plataformas musicales: NEWS + «Derechos de autor, licencias y legislación» + «Plataformas digitales, streaming y distribución».
- La convocatoria de un concurso internacional de dirección coral: EVENT + «Premios, concursos y convocatorias» + «Música coral y vocal» + «Dirección coral y práctica de conjunto».
- El hallazgo de un manuscrito de una ópera: NEWS + «Manuscritos y fuentes históricas» + «Ópera y música escénica» + «Patrimonio material e inmaterial».
- Una tesis sobre jazz en comunidades migrantes: RESEARCH + «Investigación, musicología y etnomusicología» + «Jazz y blues» + «Música y sociedad».
- La publicación de una nueva edición crítica de una partitura: BIBLIO + «Partituras y publicaciones musicales» + «Música clásica y académica»; añadir «Música antigua y prácticas históricas» si el contenido lo justifica.

## 4. Reglas para asignar categorías

1. **Clasificar por contenido:** la temática habitual de una fuente es una pista, nunca una asignación automática.
2. **Asignación múltiple, pero limitada:** asignar todas las categorías sustanciales, no cada categoría que aparezca mencionada de pasada.
3. **Preferir la categoría específica:** si una noticia trata principalmente de ópera, asignar «Ópera y música escénica»; no añadir géneros no relacionados.
4. **Categorías transversales:** añadir industria, derechos, tecnología, educación, patrimonio o sociedad cuando sean parte real del asunto.
5. **No confundir protagonista y tema:** que una noticia mencione a un compositor no significa que deba clasificarse como «Compositores y creación musical» si trata, por ejemplo, de una exposición bibliográfica.
6. **No inventar subcategorías:** si ninguna categoría encaja, marcar la clasificación temática como pendiente y proponer una nueva categoría para revisión del catálogo.
7. **No forzar una etiqueta:** si la información no permite decidir entre dos categorías, conservar la duda mediante needs_review y una confianza baja.
8. **Jerarquía:** las categorías padre agrupan subcategorías. La aplicación podrá consultar una rama incluyendo sus descendientes; no es necesario asignar automáticamente todos los padres como etiquetas explícitas.
9. **Versionado:** cada análisis debe registrar la versión de taxonomía y del criterio/prompt que se utilizó.

## 5. Ejemplos de inclusión y exclusión

| Entrada hipotética | Decisión | Motivo / clasificación |
|---|---|---|
| Una orquesta anuncia su próxima temporada | Incluir | EVENT; actividad artística y orquesta |
| Una sala publica su programación de conciertos | Incluir | EVENT; conservar fechas y lugar si el feed los aporta |
| Una empresa compra un sello discográfico | Incluir | NEWS; industria musical y mercado |
| Una plataforma cambia el sistema de remuneración de artistas | Incluir | NEWS; plataformas e industria; derechos si procede |
| Un artículo analiza una nueva técnica de restauración de partituras | Incluir | RESEARCH; tecnología y patrimonio |
| Una biblioteca digitaliza manuscritos musicales | Incluir | COLLECTION o NEWS, según sea un aviso de catálogo o un hecho noticioso |
| Una revista publica una nueva edición de una partitura | Incluir | BIBLIO o RELEASE, según el objeto anunciado |
| Un blog publica una lista genérica de canciones sin novedad ni análisis relevante | Excluir o OPINION | No es noticia; conservar solo si se decide incluir crítica editorial |
| Un resultado menciona una banda musical en una noticia sobre bandas de transporte | Excluir | Coincidencia léxica, no contenido musical |
| Una página contiene solo publicidad de clases particulares | Excluir | Promoción comercial sin novedad informativa |
| Una noticia general menciona brevemente una canción como ejemplo | Excluir | La música no es el asunto de la noticia |

## 6. Tratamiento de eventos y contenido académico

- Las agendas y convocatorias son contenido válido, pero deben poder distinguirse de las noticias de hechos ya ocurridos.
- Cuando un evento tenga fecha futura, conservar la fecha original y no confundirla con la fecha de publicación o captura.
- Un evento pasado puede seguir siendo una noticia si informa de un resultado, estreno, premio o acontecimiento ya sucedido.
- Los artículos científicos, tesis y libros pueden tener valor para el corpus, aunque no sean noticias de actualidad. Se deben identificar como investigación o novedad bibliográfica.
- Los feeds de catálogos bibliográficos pueden generar muchos registros de baja actualidad. No deben mezclarse con NEWS ni descartarse automáticamente: su tipo específico permitirá decidir más adelante cómo consultarlos.

## 7. Datos mínimos que debe producir la clasificación

Para cada elemento analizado:

- is_relevant: si pertenece al ámbito musical definido.
- content_type: uno de los tipos controlados anteriores.
- categories: cero o más identificadores del catálogo temático.
- original_language: idioma del contenido original, normalizado preferiblemente según BCP 47.
- language_source: origen de la identificación (declarado por el feed, detectado o inferido).
- language_confidence: confianza de la detección cuando no exista un idioma declarado fiable.
- relevance_reason: justificación breve basada en el contenido recibido.
- confidence: confianza estimada, con escala definida por la aplicación.
- needs_review: indica si la información requiere revisión.
- editorial_title_es: título editorial en español, si se genera.
- summary_es: resumen breve en español, si se genera.
- translations: traducciones editoriales adicionales, separadas del original y vinculadas a la versión traducida.
- taxonomy_version y prompt_version: versiones usadas para que el resultado sea reproducible.

Una entrada no pertinente puede permanecer registrada como descartada, junto con el motivo, para evitar analizarla repetidamente. Una entrada pendiente no debe confundirse con una entrada rechazada.

## 8. Principio de conservación

La clasificación no debe destruir ni sustituir los datos originales. Se conservarán por separado:

- Título, descripción, idioma y fecha tal como los entrega cada fuente.
- Versiones lingüísticas oficiales publicadas por una misma fuente, conservando su URL e idioma.
- URL y datos de procedencia.
- Tipo y categorías asignadas por el sistema.
- Texto editorial generado por IA y sus traducciones, cada uno con su idioma identificado.
- Estado, motivo de exclusión o revisión y metadatos del análisis.

Así será posible corregir una clasificación o cambiar la taxonomía sin tener que volver a descargar el contenido original.
