# Inventario inicial de fuentes y canales

**Fecha de comprobación:** 13 de noviembre de 2026.  
**Estado:** inventario documental revisado el 13 de noviembre de 2026. La localización de un endpoint, su funcionamiento técnico y la autorización para tratar sus contenidos son tres validaciones distintas. La matriz operativa está en [Matriz de pruebas de ingesta](07-matriz-pruebas-ingesta.md).

Este documento separa tres cosas que no deben confundirse:

1. **Fuente editorial:** institución, revista o medio que publica la información.
2. **Canal técnico:** RSS/Atom, API u otro mecanismo por el que se detectan novedades.
3. **Utilidad editorial:** si el canal aporta noticias, agenda, novedades bibliográficas o simplemente registros de catálogo.

Un canal oficial no es necesariamente una fuente de noticias adecuada para el boletín. Algunos se proponen como fuentes de descubrimiento y requerirán filtrado.

## 1. Fuentes con canal RSS oficial localizado

### 1.1 Library of Congress (Estados Unidos)

La página oficial de suscripciones agrupa los canales por temática y confirma expresamente dos blogs relacionados con música:

| Fuente | Canal RSS | Utilidad prevista | Evaluación inicial |
|---|---|---|---|
| In the Muse Blog | https://blogs.loc.gov/music/feed/ | Colecciones de música, teatro y danza; patrimonio, adquisiciones, actividades y conciertos | **Prioridad alta** |
| NLS Music Notes Blog | https://blogs.loc.gov/nls-music-notes/feed/ | Música en braille, audio y formatos accesibles | Especializada; incluir si interesa accesibilidad musical |
| Concerts & Performing Arts Events | https://www.loc.gov/rss/music/concerts.xml | Agenda de conciertos, conferencias y actividades escénicas | Útil para agenda; separar de noticias |
| Latest News | https://www.loc.gov/rss/pao/news.xml | Noticias generales de la institución | Baja prioridad; necesita filtrado musical |

La página de suscripciones permite localizar los enlaces RSS y describe el ámbito de cada canal. El blog *In the Muse* está dedicado específicamente a las colecciones de música, teatro y danza, por lo que es un candidato especialmente adecuado.

Fuentes oficiales:
- https://www.loc.gov/subscribe/
- https://www.loc.gov/rss/faq.html

### 1.2 Bibliothèque nationale de France (BnF)

La BnF mantiene una página institucional de canales RSS para actualidad, prensa y agenda:

- Página de canales: https://www.bnf.fr/fr/flux-rss-site-bnffr
- Actualidad: https://www.bnf.fr/fr/actualites/rss

Además, la Bibliographie nationale française publica feeds específicos por sección. Hay un canal dedicado a **Partitions** (partituras) y otro a **Son**:

- Índice de feeds: https://bibliographienationale.bnf.fr/content/rss
- Partitions: https://bibliographienationale.bnf.fr/rss/mus
- Son: https://bibliographienationale.bnf.fr/rss/son

**Interpretación:** los feeds de la Bibliographie nationale son novedades bibliográficas/catalográficas, no noticias periodísticas. Pueden detectar nuevas publicaciones musicales y registros de sonido, pero conviene almacenarlos con un tipo de contenido distinto (por ejemplo, novedad bibliográfica) para que no se mezclen sin criterio con noticias de actualidad.

La BnF también documenta que Gallica permite suscribirse a un RSS asociado a una búsqueda de su catálogo. Es un mecanismo de seguimiento de resultados y actualizaciones documentales, no un feed general de noticias de Gallica. Se podría usar más adelante para búsquedas temáticas concretas (partituras, manuscritos musicales, compositores), si se comprueba que el mecanismo sigue disponible y que el resultado es útil.

Fuentes oficiales:
- https://www.bnf.fr/fr/flux-rss-site-bnffr
- https://bibliographienationale.bnf.fr/content/rss
- https://api.bnf.fr/fr/blog

### 1.3 Biblioteca Nacional de España (BNE)

La BNE declara disponer de cinco canales RSS para:
- Noticias.
- Actividades.
- Blog de la BNE.
- Exposiciones virtuales.
- Noticias bibliotecarias.

La referencia localizada es una entrada del propio Blog de la BNE que confirma esos cinco canales:
https://www.bne.es/es/blog/blog-bne/las-10-preguntas-mas-frecuentes-sobre-la-bne

**Pendiente:** localizar las URL actuales exactas de los cinco feeds y comprobar que siguen activos. La página de referencia es antigua, por lo que no se incorporan endpoints deducidos ni se da por garantizada su vigencia. La web actual de la BNE mantiene secciones diferenciadas de noticias, agenda y blog, pero la consulta automatizada de la página institucional devolvió acceso restringido (403) en esta investigación; los resultados públicos no exponen los enlaces RSS concretos. Por tanto, no se declara resuelto el endpoint.

**Vía técnica complementaria:** el portal [datos.bne.es](https://datos.bne.es/) publica registros bibliográficos enlazados y ofrece descargas en RDF/XML, JSON-LD y Turtle para registros individuales. Es una fuente de datos de catálogo, no un sustituto de los cinco feeds de actualidad ni una API de noticias confirmada. Puede investigarse más adelante para novedades bibliográficas musicales, con su propio tipo de contenido.

### 1.6 Bachtrack

Bachtrack publica contenidos internacionales sobre música clásica, ópera, danza y eventos. Su propia documentación declara tres feeds principales:

- Noticias: https://bachtrack.com/news.rss.xml
- Artículos: https://bachtrack.com/articles.rss.xml
- Críticas: https://bachtrack.com/rss.xml

También ofrece feeds de críticas por categoría (conciertos, ópera y danza). La web tiene edición en español, además de inglés, francés y alemán.

**Evaluación:** candidato prioritario para la cobertura de música clásica. Los tres tipos deben conservarse separados: noticias, artículos/entrevistas y críticas. La documentación oficial describe expresamente los feeds; la petición al feed de noticias respondió con content-type application/rss+xml en esta comprobación. Queda pendiente probar la lectura de los elementos con feedparser y revisar las condiciones de uso.

Fuentes:
- https://bachtrack.com/fr_FR/handler/documentation/view/ug-rss-feeds
- https://bachtrack.com/es_ES/

### 1.7 Music Business Worldwide

Publicación especializada en noticias, empleo y análisis de la industria musical internacional.

- RSS localizado: https://www.musicbusinessworldwide.com/feed/

**Evaluación técnica:** endpoint localizado y registrado como RSS activo por un directorio externo; falta validar el contenido con un parser real. **Restricción de uso:** las condiciones oficiales limitan el sitio a uso personal no comercial y prohíben copiar, traducir, publicar, licenciar o vender materiales sin consentimiento. No activar el envío de títulos/descripciones a IA ni el almacenamiento sistemático de contenidos hasta obtener autorización o determinar una base de uso compatible. Mantener como candidato documental, no como fuente autorizada para la primera tanda. [Condiciones oficiales](https://www.musicbusinessworldwide.com/terms-of-use/).

Fuente de descubrimiento:
- https://www.musicbusinessworldwide.com/

### 1.8 NPR Music

Canal de NPR dedicado a noticias, reportajes, actuaciones y contenidos musicales.

- RSS localizado: https://feeds.npr.org/1039/rss.xml

**Evaluación técnica:** endpoint localizado; falta validar elementos y actividad con un parser real. **Restricción de uso decisiva:** las condiciones de NPR limitan sus feeds a usos personales no comerciales o a determinadas entidades 501(c)(3), exigen atribución y enlace, restringen redistribución/modificación y prohíben usar sus contenidos para construir o entrenar sistemas de IA sin consentimiento escrito. Por tanto, no enviar titulares ni fragmentos a un proveedor de IA ni incorporar el canal al flujo automatizado hasta obtener permiso escrito y aclarar el alcance de almacenamiento. [Condiciones de uso de NPR](https://www.npr.org/about-npr/179876898/terms-of-use).

Fuente:
- https://www.npr.org/sections/music/

### 1.9 Revistas musicales en español: Scherzo y Beckmesser

Se han localizado dos canales especializados en música clásica y ópera:

- **Scherzo:** https://scherzo.es/feed
- **Beckmesser:** https://www.beckmesser.com/feed

Las direcciones se han localizado mediante un directorio de feeds, no mediante documentación técnica del editor. La herramienta web identifica que son endpoints RSS, pero no puede interpretar el MIME application/rss+xml; por tanto, siguen pendientes de parseo real, frecuencia, campos y condiciones directamente con un lector RSS y en las páginas de cada publicación.

**Evaluación:** candidatos de alta pertinencia para noticias, críticas y actualidad de música clásica y ópera en español. Se deben separar las críticas/opiniones de las noticias, siguiendo los tipos de contenido definidos en el documento 04.

Fuentes editoriales:
- https://scherzo.es/
- https://www.beckmesser.com/

### 1.10 Ópera Actual

ÓPERA ACTUAL es una revista especializada en ópera en español y mantiene secciones diferenciadas de actualidad, críticas y entrevistas. Se ha localizado una URL con parámetros de formato RSS:

- URL candidata: https://www.operaactual.com/?format=feed&type=rss

Sin embargo, la comprobación anterior devolvió contenido HTML, no un documento RSS identificable. Se registra como **endpoint pendiente de validación**, no como feed listo para activar. La sección de actualidad muestra publicaciones recientes y distingue noticias y breves, de modo que sigue siendo una fuente editorial relevante si se localiza un canal válido. [Actualidad](https://www.operaactual.com/actualidad/). La página editorial sí confirma actividad reciente y una cobertura especializada de actualidad operística.

Fuente:
- https://www.operaactual.com/

## 2. Agregadores y consultas temáticas

### 2.1 Google News RSS

Se mantiene como mecanismo de descubrimiento transversal, no como fuente editorial primaria. Ejemplo de consulta inicial:

https://news.google.com/rss/search?q=choral+music+OR+partituras&hl=es&gl=ES&ceid=ES:es

Cada consulta debe tener un objetivo temático claro. Se propone mantener consultas separadas, al menos, para:
- Música coral y vocal.
- Música clásica e interpretación.
- Musicología e investigación.
- Partituras, manuscritos y edición musical.
- Patrimonio, archivos y bibliotecas musicales.
- Educación musical.

Al normalizar una entrada procedente de Google News hay que intentar identificar el medio original y conservarlo por separado del agregador. La noticia no debe atribuirse a Google News si el artículo fue publicado por otro medio.

**Pendiente de prueba técnica:** validar el comportamiento de las consultas, los operadores, los idiomas, la paginación/ventana temporal y la forma de recuperar la URL del editor original. No se presupone que todos los resultados incluyan siempre un enlace directo utilizable.

## 3. DOAJ y fuentes académicas

DOAJ es un directorio e índice de revistas de acceso abierto, no una fuente general de noticias musicales. Puede ayudar a descubrir revistas de musicología y publicaciones académicas, pero no debe tratarse como un feed periodístico.

Canales y servicios documentados:
- API: https://doaj.org/docs/api
- OAI-PMH: https://doaj.org/docs/oai-pmh/
- Condiciones de uso y metadatos: https://doaj.org/terms/

DOAJ declara que los metadatos de revistas y artículos están disponibles bajo una renuncia CC0. El servicio OAI-PMH público puede llevar un retraso de hasta 30 días; el acceso premium se actualiza con mayor rapidez. La documentación también describe un CSV público de revistas, actualizado dentro de un margen de 30 días.

**Uso recomendado:** localizar revistas y artículos académicos relevantes y obtener metadatos, no incorporar indiscriminadamente el catálogo completo como si fueran noticias recientes. Para la actualidad de una revista concreta será preferible utilizar el RSS/Atom del propio editor cuando exista. Debe revisarse la licencia del texto completo en la publicación original; la licencia de los metadatos de DOAJ no convierte automáticamente los artículos en contenido reutilizable.

Fuentes oficiales:
- https://doaj.org/terms/
- https://doaj.org/docs/oai-pmh/
- https://doaj.org/docs/journal-csv

### 1.4 American Musicological Society (AMS) y Musicology Now

Se han localizado dos vías especialmente relevantes para el ámbito musicológico:

- **Musicology Now**, publicación digital de la American Musicological Society orientada al público general, con artículos breves que acercan investigación e ideas sobre música. Su RSS está enlazado desde la propia web: https://musicologynow.org/feed
- **AMS – Musicology in the news**, feed que la AMS describe como noticias de interés para la comunidad musicológica. La página institucional lo sigue enumerando, pero el endpoint enlazado (https://www.ams-net.org/feeds/news/index.php) devolvió un 404 al comprobarlo. Se registra como canal anunciado pero actualmente no verificado; no debe activarse hasta localizar el endpoint vigente.

La AMS también enumera feeds de libros nuevos en musicología, tesis doctorales y anuncios académicos. Son útiles para descubrimiento de publicaciones y actividad académica, pero deben clasificarse como tales y no mezclarse automáticamente con noticias de actualidad.

Fuentes:
- https://www.ams-net.org/feeds/
- https://musicologynow.org/about-musicology-now/

### 1.5 RILM – Bibliolore

**Bibliolore** es el blog del Répertoire International de Littérature Musicale (RILM). La organización confirma que publica entradas nuevas semanalmente y que trata investigación musical global, musicología, etnomusicología, música popular, educación y patrimonio. La página principal estaba actualizada el 11 de noviembre de 2026, por lo que es un candidato editorial activo y de alta pertinencia.

- Página: https://bibliolore.org/
- Información institucional sobre actividad del blog: https://www.rilm.org/aboutus/history/2025-report/

**Endpoint RSS localizado:** https://bibliolore.org/feed/ . La solicitud directa devuelve el tipo de contenido application/rss+xml; el visor de páginas utilizado en esta investigación no interpreta ese formato, por lo que la lectura real de elementos, fechas y campos queda pendiente de una prueba con un lector RSS. El endpoint se considera localizado, pero todavía no validado funcionalmente.

## 4. Estado del inventario

| Institución/canal | Estado | Tratamiento propuesto |
|---|---|---|
| LOC – In the Muse | RSS oficial localizado | Candidato prioritario para noticias de música y patrimonio |
| LOC – NLS Music Notes | RSS oficial localizado | Fuente temática especializada |
| LOC – Concerts & Performing Arts | RSS oficial localizado | Agenda, no mezclar con noticias |
| LOC – Latest News | RSS oficial localizado | Filtrado temático estricto |
| BnF – Actualités | RSS oficial localizado | Revisar relevancia musical de cada entrada |
| BnF – Bibliographie nationale / Partitions | RSS oficial localizado | Novedades bibliográficas musicales |
| BnF – Bibliographie nationale / Son | RSS oficial localizado | Novedades bibliográficas de sonido |
| Gallica – RSS de búsquedas | Mecanismo documentado; endpoint dinámico | Investigar búsquedas temáticas, no es feed general |
| BNE – cinco RSS | Existencia declarada; URL actual pendiente; página institucional con acceso 403 durante esta consulta | No configurar hasta localizar y probar endpoints |
| Google News RSS | Plantilla de consulta documentada | Descubrimiento; identificar siempre el medio original |
| AMS – Musicology Now | RSS oficial localizado | Publicación divulgativa de musicología; candidato prioritario |
| AMS – Musicology in the news | Endpoint anunciado, pero 404 en comprobación | No activar hasta localizar URL vigente |
| RILM – Bibliolore | Blog activo; endpoint /feed/ localizado y responde como application/rss+xml; lectura funcional pendiente | Candidato prioritario; probar con feedparser |
| Bachtrack – News / Articles / Reviews | Tres feeds documentados oficialmente; feed de noticias responde como application/rss+xml | Candidato prioritario para clásica, ópera, artículos y críticas; separar tipos |
| Music Business Worldwide | Endpoint /feed/ localizado; validación funcional pendiente | Restricción de uso personal/no comercial y limitación de copia/traducción: permiso necesario antes de IA o almacenamiento sistemático |
| NPR Music | Endpoint RSS localizado; validación funcional pendiente | Condiciones restringen uso a determinados fines no comerciales y prohíben uso de contenido para IA sin consentimiento escrito; no activar en análisis automatizado |
| Scherzo | Endpoint /feed responde como application/rss+xml; origen de URL por directorio RSS | Candidato de alta pertinencia en español para clásica y ópera |
| Beckmesser | Endpoint /feed responde como application/rss+xml; origen de URL por directorio RSS | Candidato de alta pertinencia en español para clásica y ópera |
| Ópera Actual | URL candidata con parámetros RSS, pero la comprobación devolvió HTML | No activar hasta verificar un endpoint RSS real |
| DOAJ | API/OAI-PMH y metadatos documentados | Descubrimiento académico; metadatos CC0, no implica licencia del texto completo |

## 5. Criterios para dar de alta una fuente

Antes de activar cualquier fuente en producción, registrar:

- Institución/editor y nombre exacto del canal.
- URL oficial de la página que documenta el canal.
- URL del endpoint y formato detectado (RSS, Atom, XML, JSON, OAI-PMH).
- Tipo de contenido: noticia, agenda, publicación académica, novedad bibliográfica o actualización de catálogo.
- Idioma y cobertura temática.
- Frecuencia observada y número aproximado de elementos.
- Presencia de fecha, autor, resumen, identificador y enlace original.
- Condiciones de uso y límites técnicos aplicables.
- Fecha de última comprobación y resultado de la prueba.

No se debe inventar ni inferir una URL RSS a partir de la dirección de una web. Si no se localiza un canal oficial o una API documentada, la fuente permanece como pendiente y no se automatiza mediante scraping por defecto.

## 6. Priorización para la primera fase

Para evitar que la primera implementación dependa de una lista excesiva de canales, se propone incorporar fuentes en tandas:

### Tanda inicial de pruebas
- LOC – In the Muse: contenido musical editorial y patrimonial, con RSS institucional localizado.
- Scherzo y Beckmesser: fuentes en español para música clásica y ópera; comprobar campos y distinguir noticias de críticas.
- Bachtrack – News: noticias internacionales de música clásica, ópera y actividad artística.
- Music Business Worldwide: actualidad de la industria musical.
- NPR Music: reportajes y actualidad musical de interés general.
- Musicology Now: divulgación e investigación musicológica, con RSS localizado.
- Google News RSS: descubrimiento transversal en español e inglés, manteniendo separado el medio original.
- BnF – Actualités: canal institucional general que requiere filtrado por contenido musical.
- BnF – Bibliographie nationale / Partitions: novedades bibliográficas musicales, almacenadas con tipo BIBLIO y no como noticia periodística.

### Tanda de ampliación
- Ópera Actual: incorporar solo cuando se localice un endpoint RSS válido.
- Bachtrack – Articles y Reviews: artículos, entrevistas y críticas, diferenciados de las noticias.
- NPR Music: mantener como candidato hasta verificar la frecuencia y la calidad de metadatos.
- LOC – NLS Music Notes, por su especialización en accesibilidad.
- LOC – Concerts & Performing Arts, como agenda.
- BnF – Son, como novedad bibliográfica/catalográfica.
- RILM – Bibliolore, cuando se confirme su feed.
- BNE, cuando se recuperen y prueben las URL oficiales.
- DOAJ y feeds de revistas/editoriales concretas, con tratamiento académico diferenciado.

La prioridad es probar una fuente de cada comportamiento relevante (noticia editorial, agregador, agenda y novedad bibliográfica), no activar muchos feeds de golpe.

## 7. Resultado de la revisión de uso y prioridad

- **NPR:** técnicamente puede ser un feed útil, pero queda bloqueado para análisis IA y reutilización automatizada hasta obtener consentimiento escrito. Las condiciones vigentes prohíben expresamente el uso de contenidos para construir o entrenar IA sin permiso y restringen los usos de los feeds.
- **Music Business Worldwide:** no se presume autorización por la existencia del RSS. Sus términos limitan el uso a fines personales no comerciales y restringen copia, traducción y publicación. Requiere autorización antes de integrarlo en el procesamiento previsto.
- **DOAJ:** sus metadatos de revistas y artículos están disponibles bajo CC0, pero el propio DOAJ advierte que la licencia de los metadatos no altera los derechos del artículo descrito. El OAI-PMH público puede llevar hasta 30 días de retraso; no es un canal de noticias en tiempo real. [Términos DOAJ](https://doaj.org/terms/) · [OAI-PMH](https://doaj.org/docs/oai-pmh/).
- **Bachtrack:** documentación oficial confirma tres feeds distintos (news, articles, reviews) y feeds de críticas por categoría. Deben tratarse como tipos editoriales separados. [Documentación RSS](https://bachtrack.com/fr_FR/handler/documentation/view/ug-rss-feeds).
- **Library of Congress:** la página oficial confirma los canales de música, música accesible y agenda, con descripciones diferenciadas. [Suscripciones oficiales](https://www.loc.gov/subscribe/).
- **BnF:** confirma feeds institucionales para actualidad, prensa y agenda; los feeds bibliográficos de partituras/sonido deben seguir separados de actualidad. [Índice oficial](https://www.bnf.fr/fr/flux-rss-site-bnffr).
- **BNE:** se confirma documentalmente que existen cinco canales, pero no se han localizado sus URLs actuales. No se inventarán endpoints.

La clasificación técnica/permiso por canal se completa con la matriz de pruebas. Ningún estado «RSS localizado» significa autorización automática para almacenar o procesar textos.

## 8. Límite de esta validación documental

Las respuestas de RSS/Atom se han localizado, pero el visor web empleado no interpreta directamente algunos tipos MIME XML de los feeds. Por ello, no se afirma que el parser los haya leído ni que se hayan inspeccionado los elementos de cada canal. La validación funcional corresponde a la ejecución de la matriz 07 con feedparser o un cliente de API, que deberá registrar muestras y resultados reproducibles.

## 9. Próxima investigación

1. Localizar los cinco endpoints actuales de la BNE y comprobar sus respuestas.
2. Validar técnicamente con un parser real los feeds de LOC, BnF, Bachtrack, Scherzo, Beckmesser, Musicology Now y Bibliolore.
3. Resolver el permiso de NPR y Music Business Worldwide antes de cualquier análisis automatizado.
4. Probar Google News para identificar editor original y resolver URL.
5. Preparar una muestra etiquetada para medir relevancia, tipos, idiomas y duplicados.
6. Revisar las condiciones de cada fuente antes de decidir retención y tratamiento IA.


## 10. Revisión de condiciones de uso: decisión operativa (13-11-2026)

Esta sección prevalece sobre las propuestas preliminares de las secciones 6 y 7 cuando exista contradicción. La disponibilidad pública de RSS solo acredita que el editor ofrece un mecanismo de suscripción; no equivale a una licencia para almacenar de forma permanente, reutilizar, traducir o enviar el contenido a un servicio de IA.

| Canal | Lo que dicen las condiciones oficiales | Decisión para esta implementación |
|---|---|---|
| LOC – In the Muse | La Library of Congress permite reutilizar el texto de los blogs escritos por personal propio, con crédito al autor y a la institución. Algunas imágenes pueden estar restringidas; los artículos de autores invitados deben revisarse por separado. | **Primer candidato para prueba**, limitando la captura al contenido textual del feed, guardando autor, URL, atribución y fecha. No reutilizar imágenes. Revisar cada pieza si el autor no es personal LOC. |
| BnF – Bibliographie nationale / Partitions | Las metadatos descriptivos de la BnF están bajo Licence Ouverte, con obligación de conservar fuente y fecha de recuperación. La sección Partitions contiene registros bibliográficos de música impresa. | **Candidato para prueba independiente**, como novedad bibliográfica, no noticia. Guardar fuente BnF y fecha de recuperación. La licencia de metadatos no se extiende a imágenes, cubiertas ni documentos enlazados. |
| Scherzo | El aviso legal exige autorización escrita previa para reproducción, uso o explotación de los contenidos, cualquiera que sea la finalidad. | **No activar** para captura persistente o análisis IA sin autorización escrita. El enlace directo a la página original sí está expresamente permitido. |
| Beckmesser | El aviso legal reserva todos los derechos y prohíbe reproducción, almacenamiento permanente y difusión con finalidad pública o comercial sin consentimiento previo expreso y escrito. | **No activar** para la ingesta prevista sin autorización escrita. |
| Bachtrack – News / Articles / Reviews | La documentación ofrece RSS oficiales, pero las condiciones de uso (actualizadas el 23-03-2026) restringen el uso ordinario a fines personales y privados. Para robots solo permiten rastreo/lectura/almacenamiento/indexación con el fin de mostrar resultados de búsqueda, bajo límites (máximo 100 palabras por URL, enlace destacado, ritmo no excesivo, User-Agent identificable y respeto de robots.txt). Prohíben expresamente otros usos automatizados, incluido entrenamiento de IA y extracción de contenido. | **No activar en el recolector ni enviar a IA** con el diseño actual. El RSS documentado no anula estas restricciones. Requerir permiso escrito que cubra captura, persistencia y análisis automatizado. |
| Musicology Now | La publicación identifica a los autores como responsables de las opiniones y contenidos; la página informativa y el RSS no ofrecen una licencia general de reutilización de los artículos. | **Pendiente de autorización/aclaración** antes de persistir textos o enviarlos a IA. No inferir licencia abierta por su carácter académico o divulgativo. |
| Music Business Worldwide | Sus condiciones limitan el uso a fines personales no comerciales y restringen reproducción, traducción y redistribución sin autorización. | **No activar** sin permiso escrito. |
| NPR Music | Las condiciones limitan el uso del feed y prohíben utilizar sus contenidos para construir o entrenar sistemas de IA sin consentimiento escrito. | **No activar** en el flujo automatizado sin permiso escrito. |

Fuentes oficiales consultadas:
- LOC, reutilización de blogs: https://blogs.loc.gov/about/
- LOC, guía de derechos de los materiales del sitio: https://www.loc.gov/legal/security-copyright-and-privacy/understanding-copyright/
- BnF, condiciones de reutilización: https://www.bnf.fr/fr/conditions-de-reutilisations-des-donnees-de-la-bnf
- BnF, contenido y secciones de la Bibliographie nationale: https://bibliographienationale.bnf.fr/content/bibliographie
- Scherzo, aviso legal: https://scherzo.es/aviso-legal/
- Beckmesser, aviso legal: https://www.beckmesser.com/aviso-legal/
- Bachtrack, RSS: https://bachtrack.com/fr_FR/handler/documentation/view/ug-rss-feeds
- Bachtrack, condiciones de uso (23-03-2026): https://bachtrack.com/fr_FR/conditions-of-use
- Musicology Now, información editorial: https://musicologynow.org/about-musicology-now/

### Orden de trabajo corregido

1. Probar primero **LOC – In the Muse**, aplicando la atribución indicada y sin reutilizar imágenes. Antes de pasar contenido a IA, comprobar si cada entrada es de personal LOC o de autor invitado.
2. Probar **BnF – Partitions** como flujo separado de novedades bibliográficas y validar que el parser interpreta el RSS y que se conservan fuente y fecha de recuperación.
3. Mantener los demás canales en PAUSED hasta obtener permisos o aclaraciones suficientes. No activar Scherzo, Beckmesser, Bachtrack, Musicology Now, MBW ni NPR solo porque sus RSS respondan.
4. Una prueba técnica de RSS debe limitarse a comprobar conectividad, estructura y campos necesarios; no debe convertirse en almacenamiento de textos editoriales sujetos a restricciones.

La primera captura de LOC debe ser pequeña y verificable. La autorización de reutilización de los textos de blogs del personal no debe extenderse automáticamente a colaboradores invitados, fotografías, material enlazado ni contenidos de terceros.


## 11. Resultado de la prueba técnica de feeds (13-11-2026)

La ejecución local de `probar_fuentes.bat` el 13-11-2026, contra los dos canales incluidos en la lista permitida de sondeo, obtuvo:

| Canal | HTTP | Elementos | Con URL | Con autor | Con fecha | Con identificador | Validadores HTTP |
|---|---:|---:|---:|---:|---:|---:|---|
| LOC – In the Muse (ID 1) | 200 | 10 | 10 | 10 | 10 | 10 | ETag y Last-Modified |
| BnF – Bibliographie nationale / Partitions (ID 6) | 200 | 12 | 12 | 0 | 12 | 0 | Ninguno |

Ambos feeds proporcionaron título de canal y fueron parseados correctamente. El dominio final coincidió con el esperado. El sondeo informó `persisted: false` en los dos casos: no se guardaron publicaciones, observaciones ni ejecuciones de captura, y no se modificó el estado de los canales.

### Interpretación y límites

- **LOC – In the Muse:** resultado técnico satisfactorio y metadatos completos en los diez elementos examinados. La presencia de autor en el feed no acredita que sea empleado de LOC. La propia Library of Congress explica que sus blogs son escritos por personal y, ocasionalmente, por autores invitados; el texto de blogs del personal se puede reutilizar con atribución al autor y a LOC. Por tanto, antes de enviar una entrada a IA o persistir su texto debe identificarse si el autor actúa como personal LOC o como invitado. La categoría «Guest bloggers» del sitio es una señal útil, pero no debe inferirse que todos los autores que aparecen en esa categoría sean invitados: algunas entradas están allí por su temática y son escritas por personal. Fuentes: https://blogs.loc.gov/about/ y https://blogs.loc.gov/music/category/guest-bloggers/.
- **BnF – Partitions:** resultado técnico satisfactorio. La falta de GUID/identificador no impide una identidad técnica inicial porque los doce elementos tienen URL; la URL se puede usar como alternativa de identidad, conservando el valor bruto. Al no ofrecer ETag ni Last-Modified, las consultas posteriores no podrán depender de validadores HTTP y deberán respetar una frecuencia prudente. Es un feed de novedades bibliográficas, no de noticias periodísticas: debe tratarse como `BIBLIO` y mantenerse separado del corpus de actualidad.
- La prueba solo acredita conectividad, parseo y presencia de campos. No constituye una revisión de los doce contenidos, no demuestra relevancia editorial ni amplía los permisos de uso.
- No se ha probado todavía la captura persistente ni la idempotencia de estos dos canales en la base de datos local.

### Decisión operativa tras el sondeo

1. Mantener ambos canales en `PAUSED`.
2. LOC queda como candidato editorial, pendiente de poder distinguir de forma fiable las entradas de personal y las de invitados antes del tratamiento automatizado.
3. BnF queda como candidato técnico para una prueba independiente de novedades bibliográficas. Su activación requiere que se decida expresamente iniciar esa prueba como contenido `BIBLIO`.
4. No ejecutar `activate` ni `ingest` como consecuencia automática de esta prueba. La activación requiere revisión y confirmación explícita de las condiciones y del uso concreto.
