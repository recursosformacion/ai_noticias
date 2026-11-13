# Inventario inicial de fuentes y canales

**Fecha de comprobación:** 13 de noviembre de 2026.  
**Estado:** investigación documental inicial. Los endpoints se han localizado en páginas institucionales; antes de incorporarlos a una ejecución automática habrá que comprobar periódicamente que siguen respondiendo y revisar el contenido que entregan.

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

**Pendiente:** localizar las URL actuales exactas de los cinco feeds y comprobar que siguen activos. La página de referencia es antigua, por lo que no se incorporan endpoints deducidos ni se da por garantizada su vigencia. La web actual de la BNE mantiene secciones diferenciadas de noticias, agenda y blog, pero la consulta automatizada de las páginas institucionales devuelve acceso restringido (403) en esta investigación; los resultados públicos consultados no exponen los enlaces RSS concretos. Por tanto, no se declara resuelto el endpoint.

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
| DOAJ | API/OAI-PMH y metadatos documentados | Descubrimiento académico, no feed de noticias |

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
- Musicology Now: divulgación e investigación musicológica, con RSS localizado.
- Google News RSS: descubrimiento transversal en español e inglés, manteniendo separado el medio original.
- BnF – Actualités: canal institucional general que requiere filtrado por contenido musical.
- BnF – Bibliographie nationale / Partitions: novedades bibliográficas musicales, almacenadas con tipo BIBLIO y no como noticia periodística.

### Tanda de ampliación
- LOC – NLS Music Notes, por su especialización en accesibilidad.
- LOC – Concerts & Performing Arts, como agenda.
- BnF – Son, como novedad bibliográfica/catalográfica.
- RILM – Bibliolore, cuando se confirme su feed.
- BNE, cuando se recuperen y prueben las URL oficiales.
- DOAJ y feeds de revistas/editoriales concretas, con tratamiento académico diferenciado.

La prioridad es probar una fuente de cada comportamiento relevante (noticia editorial, agregador, agenda y novedad bibliográfica), no activar muchos feeds de golpe.

## 7. Próxima investigación

1. Localizar los cinco endpoints actuales de la BNE y comprobar sus respuestas.
2. Comprobar directamente los feeds de LOC y BnF con un lector RSS, inspeccionando fechas, campos y volumen.
3. Probar funcionalmente el RSS localizado de Bibliolore y corregir el endpoint AMS anunciado que devuelve 404.
4. Preparar una muestra de entradas reales para evaluar relevancia, duplicados y separación entre noticia, agenda y novedad bibliográfica.
5. Revisar las condiciones de uso de cada canal antes de fijar qué metadatos o fragmentos se almacenarán.
