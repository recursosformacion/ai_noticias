# Matriz de pruebas de ingesta

**Estado:** protocolo funcional previo a la implementación.  
**Alcance:** comprobar fuentes, captura, normalización, deduplicación, clasificación y persistencia. No contiene código ni autoriza escrituras en bases de datos.

## 1. Objetivo y criterio de ejecución

La matriz permite decidir, con evidencia repetible, qué canales pueden activarse en la primera versión. Cada prueba debe registrar fecha, canal, URL consultada, resultado HTTP/API, versión del recolector o herramienta de prueba, muestra examinada y conclusión.

No se considerará validado un canal solo porque devuelva HTTP 200 o un XML. Debe entregar elementos utilizables, con estabilidad suficiente, y su uso debe ser compatible con las condiciones del editor.

## 2. Ficha de prueba por canal

| Área | Comprobación | Evidencia que se registra | Criterio de aceptación |
|---|---|---|---|
| Identidad | El endpoint corresponde al editor y canal documentados | URL de documentación y URL final | Procedencia verificable |
| Transporte | DNS, TLS, conexión, redirecciones y código HTTP | Código, URL final, latencia, error | Respuesta válida; redirecciones justificadas |
| Tipo de contenido | RSS 2.0, Atom, XML/API u otro formato declarado | Content-Type y formato detectado | Formato coherente y parseable |
| Parseo | Documento completo, namespaces, encoding y caracteres | Resultado del parser y errores | Sin errores que impidan leer elementos |
| Actividad | Fechas de los últimos elementos y frecuencia observada | Últimas fechas, intervalo y número de elementos | Actividad acorde con el tipo de canal; inactividad se evalúa, no se confunde con fallo |
| Identidad de elemento | GUID/ID, permalink, DOI u otro identificador | Campos presentes y estabilidad | Identificador estable o estrategia alternativa documentada |
| URL | URL del artículo, URL de redirección y canonical si existe | URL original, final y canonical | Se puede conservar un enlace útil a la publicación |
| Contenido | Título, resumen/fragmento, autor, categorías | Porcentaje de elementos con cada campo | Suficiente para preclasificación; los campos ausentes quedan explícitos |
| Fechas | Publicación, modificación, evento y captura | Valores originales y parseados, zona horaria | No se inventan fechas ni se confunden tipos |
| Idioma | Idioma del canal y del elemento | Declaración, detección, código BCP 47 y confianza | Se detectan correctamente casos multilingües o se marcan inciertos |
| Clasificación | Pertinencia, tipo y temas | Muestra etiquetada y desacuerdos | Precisión suficiente para el uso previsto; dudas pasan a revisión |
| Duplicados | Repetición en el mismo feed y entre fuentes | Coincidencias por ID, URL y similitud | No duplica apariciones; no fusiona artículos distintos |
| Cambios | Elemento ya visto que cambia título, resumen o fecha | Antes/después y detección de cambio | Se conserva evidencia y se reanaliza solo si el cambio es sustancial |
| Condiciones | Términos, licencia, restricciones de IA, caché y redistribución | URL, fecha de revisión y decisión | Uso concreto autorizado o limitado de forma explícita |
| Operación | ETag, Last-Modified, límites, errores y reintentos | Cabeceras, latencia, fallos y frecuencia recomendada | Consulta respetuosa, reanudable y sin carga innecesaria |

## 3. Tamaño y composición de la muestra

Para la primera validación de cada canal:

- Capturar hasta 50 elementos recientes, o todos los disponibles si el canal ofrece menos.
- Examinar manualmente al menos 20 elementos cuando existan; si el canal ofrece menos, examinarlos todos.
- Para canales de agenda o bibliografía, comprobar al menos 10 registros y su semántica específica.
- Repetir la consulta al menos una vez sin cambios y una tercera vez después de que aparezca una novedad, si el canal tiene actividad suficiente.
- Probar al menos dos idiomas cuando la fuente sea multilingüe.
- Mantener una muestra de referencia con etiquetas editoriales humanas para medir la clasificación de IA.

Estos tamaños son umbrales de prueba inicial, no estimaciones estadísticas de calidad ni límites permanentes de descarga.

## 4. Matriz de pruebas funcionales del sistema

| ID | Escenario | Resultado esperado |
|---|---|---|
| ING-01 | Feed RSS válido | Se captura y normaliza cada elemento |
| ING-02 | Feed Atom válido | Se procesa sin depender de RSS 2.0 |
| ING-03 | API JSON documentada | Se adapta al mismo modelo normalizado |
| ING-04 | HTTP 304 / contenido sin cambios | Se registra la consulta sin reprocesar elementos |
| ING-05 | HTTP 404, 410, 429 o 5xx | Se registra el fallo y se aplica la política adecuada; no se marca como captura correcta |
| ING-06 | Timeout o XML truncado | Se conserva el error y se reintenta sin duplicar |
| ING-07 | Feed vacío o sin novedades | La ejecución queda correcta si el canal respondió válidamente |
| ING-08 | Elemento sin GUID | Se usa URL/huella como alternativa, sin asumir unicidad absoluta |
| ING-09 | Dos GUID distintos con la misma URL canónica | Se detecta una posible misma publicación y se conserva la evidencia de ambas observaciones |
| ING-10 | Mismo artículo en dos canales | Una publicación puede enlazarse a dos observaciones; se conservan ambos canales |
| ING-11 | Dos artículos sobre el mismo acontecimiento | No se fusionan solo por título o tema |
| ING-12 | Google News apunta a medio externo | Se conserva el agregador como canal de descubrimiento y el medio como editor de la publicación |
| ING-13 | Artículo actualizado | Se registra nueva evidencia/versionado y se decide si requiere nuevo análisis |
| ING-14 | Fecha ausente o inválida | Se conserva el valor bruto y se deja fecha normalizada nula; no se inventa |
| ING-15 | Fecha con zona horaria | Se almacena el instante normalizado y, cuando sea útil, el valor original |
| ING-16 | Canal declarado en inglés con elemento en español | El idioma del elemento prevalece si la detección es fiable |
| ING-17 | Texto corto o idioma ambiguo | Se marca incertidumbre y no se fuerza una traducción |
| ING-18 | Noticia pertinente de varias categorías | Se permiten varias categorías válidas |
| ING-19 | Elemento no musical | Se conserva como descartado con motivo, si la política de retención lo permite |
| ING-20 | Respuesta IA inválida o proveedor caído | La captura permanece; análisis queda en error/reintento |
| ING-21 | Repetición de análisis con nuevo prompt | Se conserva el análisis anterior y se identifica el nuevo |
| ING-22 | Categoría inexistente en la taxonomía activa | Se rechaza esa asignación o se manda a revisión; nunca se crea silenciosamente |
| ING-23 | Traducción falla | No cambia el estado de captura ni clasificación |
| ING-24 | Repetir toda la ejecución | No crea noticias, publicaciones u observaciones duplicadas |
| ING-25 | Interrupción durante persistencia | La transacción deja un estado íntegro y la siguiente ejecución puede continuar |
| ING-26 | Dos workers procesan el mismo elemento | Restricciones de unicidad y transacciones evitan duplicados |
| ING-27 | Fuente retirada o URL cambia | Se conserva historial del canal y se registra sustitución/retirada |
| ING-28 | Elemento desaparece del feed | No se borra automáticamente del corpus |
| ING-29 | Versión oficial en otro idioma | Se registra como publicación/edición relacionada, no como traducción propia |
| ING-30 | Revisión manual corrige clasificación | Se conserva quién/cuándo y el resultado anterior, si se habilita revisión en esta fase |

## 5. Evaluación editorial de la muestra

Cada elemento de la muestra debe recibir una etiqueta humana:

- Pertinente / no pertinente / insuficiente.
- Tipo: NEWS, EVENT, RELEASE, RESEARCH, BIBLIO, COLLECTION, INTERVIEW, OPINION, OTHER o REVIEW.
- Categorías temáticas justificadas.
- Idioma original.
- Publicación original identificada o no.
- Duplicado exacto, publicación relacionada o noticia distinta.
- Necesidad de revisión.

La comparación con IA debe separar:
- Falsos positivos: contenido no musical aceptado.
- Falsos negativos: contenido musical descartado.
- Errores de tipo: noticia confundida con crítica, agenda o bibliografía.
- Errores de categoría: tema principal omitido o categoría incidental añadida.
- Errores de idioma.
- Datos inventados o inferencias no respaldadas.

No se fijará un porcentaje de aceptación universal antes de ver la muestra. Para una fuente de alta prioridad, los falsos negativos y la pérdida de procedencia se consideran especialmente graves.

## 6. Registro de resultado por fuente

Cada canal terminará con una ficha:

| Campo | Valores |
|---|---|
| Estado técnico | VALIDADO / PARCIAL / FALLIDO / PENDIENTE |
| Estado de uso | APTO / APTO CON LIMITACIONES / PERMISO NECESARIO / NO APTO |
| Calidad editorial | ALTA / MEDIA / BAJA / SIN MUESTRA |
| Tipo de contenido dominante | NEWS / EVENT / BIBLIO / RESEARCH / OPINION / MIXTO |
| Idiomas observados | Códigos BCP 47 |
| Frecuencia recomendada | Basada en observación y límites publicados |
| Identificadores | GUID / URL / DOI / otros / ninguno |
| Retención permitida | Según condiciones revisadas; nunca presumida |
| Decisión | ACTIVAR / ACTIVAR CON RESTRICCIONES / POSPONER / DESCARTAR |
| Próxima revisión | Fecha o evento que la desencadena |

## 7. Reglas para activar una fuente

Una fuente solo pasa a activa cuando:

1. El canal y su editor están identificados.
2. El endpoint se ha probado con un parser real.
3. Se ha comprobado una muestra suficiente de elementos.
4. Se ha definido qué datos se pueden almacenar y enviar al proveedor de IA.
5. La política de atribución y enlace está documentada.
6. La frecuencia y el mecanismo de reintento son razonables.
7. La fuente tiene un tipo editorial claro y no introduce duplicación sistemática sin valor.

Una fuente puede ser técnicamente válida y, aun así, quedar bloqueada por sus condiciones de uso. El estado técnico y el estado de autorización son independientes.

## 8. Orden recomendado de pruebas

1. LOC In the Muse, Bachtrack News y Scherzo/Beckmesser: feeds editoriales especializados.
2. BnF Actualités y BnF Partitions: canal institucional y catálogo bibliográfico.
3. Musicology Now y Bibliolore: investigación y divulgación musicológica.
4. Google News: agregación y resolución del editor original.
5. BNE: cuando se localicen endpoints actuales.
6. NPR y Music Business Worldwide: solo evaluación técnica/documental; no enviar contenido a IA ni activar tratamiento automatizado sujeto a permisos pendientes.
7. Canales de agenda, crítica y bibliografía: validar el tratamiento diferenciado antes de ampliar volumen.

La tanda inicial debe medir calidad y variedad, no maximizar el número de feeds.


## 9. Resultado del sondeo técnico no persistente (13-11-2026)

El comando local `probar_fuentes.bat` comprobó los dos endpoints incluidos en la lista de sondeo:

| Canal | HTTP | Elementos | URL | Autor | Fecha | Identificador | ETag / Last-Modified |
|---|---:|---:|---:|---:|---:|---:|---|
| LOC – In the Muse | 200 | 10 | 10/10 | 10/10 | 10/10 | 10/10 | Sí / Sí |
| BnF – Partitions | 200 | 12 | 12/12 | 0/12 | 12/12 | 0/12 | No / No |

**Estado técnico preliminar:** ambos feeds responden y se parsean. La prueba no guarda datos (`persisted: false`) y no sustituye las pruebas de muestra editorial, condiciones de uso, captura persistente, repetición/idempotencia ni tratamiento de errores.

- LOC: comprobar autoría institucional o invitada para cada elemento antes de tratar el texto. El campo author por sí solo no resuelve esa condición.
- BnF: puede usarse la URL como identidad alternativa al no haber identificador externo. Clasificar las entradas como `BIBLIO`, no como noticias.
- No se activa ninguno de los canales con este resultado. Ambos permanecen en `PAUSED` hasta una decisión explícita de activación.

La salida de esta prueba fue facilitada por el operador local; no se ha ejecutado desde el entorno de GitHub ni se afirma que haya habido una captura persistente en la base de datos.
