# Propuesta funcional y arquitectura inicial

**Estado:** borrador de trabajo. No es todavía una especificación de implementación.

## 1. Objetivo del paquete

Recopilar automáticamente noticias y novedades de **todos los ámbitos musicales**, tanto de interés general como especializado. El sistema no limitará la recolección a un único género o comunidad: cubrirá, entre otros, música clásica, coral, jazz, rock, pop, música urbana, electrónica, música tradicional, industria musical, educación, musicología, partituras y patrimonio. Las noticias se normalizarán, deduplicarán, clasificarán y almacenarán en MySQL/MariaDB. **El límite funcional de esta primera fase es disponer de ese corpus de noticias correctamente cargado en la base de datos.**

El sistema debe mantener la trazabilidad hasta la fuente original y distinguir claramente entre los datos publicados por la fuente y el texto redactado por la IA. La consulta personalizada, las preferencias de usuarios, la integración con OSAP y el envío de boletines quedan expresamente fuera del alcance de esta fase.

## 2. Flujo general

1. **Fuentes:** mantener un catálogo de fuentes RSS/Atom y APIs, con URL, tipo, idioma, temática, frecuencia, estado y última consulta.
2. **Recolección:** consultar las fuentes periódicamente, respetando sus condiciones de uso, límites y cabeceras HTTP cuando proceda.
3. **Normalización:** convertir cada elemento a un formato común: fuente, identificador externo, URL canónica, título, descripción disponible, autor, idioma original detectado, idioma declarado por la fuente, fecha de publicación y fecha de captura.
4. **Deduplicación:** detectar repetidos mediante identificador de origen, URL normalizada y, como apoyo, huella del título. Una misma noticia puede aparecer en varias fuentes; conviene conservar esas relaciones en lugar de perder la procedencia.
5. **Preclasificación:** aplicar reglas sencillas de términos y categorías para descartar ruido evidente y reducir llamadas innecesarias a la IA.
6. **Clasificación con IA:** decidir si la entrada es pertinente y asignar una o varias categorías. La respuesta debe ajustarse a un esquema JSON validable.
7. **Redacción editorial y traducción:** conservar siempre título y descripción originales. Generar un título y resumen editorial en español como idioma editorial inicial, sin añadir hechos. Mantener el diseño preparado para almacenar traducciones adicionales por idioma, separadas del original.
8. **Persistencia:** guardar la noticia normalizada, su procedencia, el resultado de clasificación y los textos generados, junto con los estados y datos necesarios para reanudar procesos fallidos.

La primera fase comprende desde la consulta de fuentes hasta la carga verificable en MySQL/MariaDB. La recolección, el análisis y la persistencia deben poder ejecutarse de forma independiente: un fallo de IA no debe provocar una nueva descarga innecesaria ni perder los datos ya capturados. No se implementarán todavía vistas de usuario, boletines ni envío de correo.

## 3. Fuentes iniciales propuestas

### 3.1 Google News RSS

Ejemplo de consulta en español:

https://news.google.com/rss/search?q=choral+music+OR+partituras&hl=es&gl=ES&ceid=ES:es

Se podrán crear consultas separadas por ámbito e idioma, por ejemplo:

- Música coral y actividad de coros.
- Música clásica y acontecimientos musicales.
- Musicología e investigación.
- Partituras, manuscritos y ediciones musicales.
- Digitalización y patrimonio musical.
- Bibliotecas, archivos y colecciones musicales.

La consulta exacta, los operadores admitidos y la estabilidad del feed deberán probarse. Google News es un agregador, no la fuente editorial original: se debe conservar, cuando esté disponible, el medio que publicó la noticia y enlazar a la publicación original.

### 3.2 Bibliotecas, archivos e instituciones

Fuentes a investigar:

- Biblioteca Nacional de España (BNE): noticias, novedades de colecciones y digitalización de fondos musicales.
- Gallica / Bibliothèque nationale de France: novedades, blog y colecciones digitalizadas.
- Library of Congress: colecciones de música notada, novedades y publicaciones.
- Otras bibliotecas nacionales, archivos, universidades, conservatorios y centros de investigación.

No se dará por hecho que cada sección dispone de RSS. Para cada institución habrá que localizar y verificar el feed o API oficial; si no existe, se anotará como fuente pendiente y se estudiará una alternativa permitida.

### 3.3 Revistas y repositorios académicos

Fuentes a investigar:

- DOAJ y sus mecanismos de búsqueda/API.
- Revistas de musicología de acceso abierto.
- Blogs universitarios y centros de investigación musical.
- Repositorios académicos que publiquen novedades mediante RSS, Atom o API.

Conviene distinguir noticias divulgativas de artículos académicos. Estos últimos pueden requerir metadatos bibliográficos específicos y no siempre son adecuados para un boletín diario.

## 4. Modelo editorial: cobertura general y especializada

La recolección tendrá una cobertura amplia y común para todos los usuarios. Se recogerán noticias de los ámbitos musicales generales y de los especializados; no se crearán recolectores separados ni se limitará la consulta de fuentes en función de las preferencias individuales.

La separación entre «general» y «especializado» será una **clasificación editorial**, no dos sistemas aislados:

- **Ámbito general:** actualidad de la música en conjunto, industria, mercado, tecnología, plataformas, derechos, festivales, giras y noticias de interés transversal.
- **Ámbitos especializados:** música clásica, coral y vocal, jazz, rock, pop, electrónica, músicas tradicionales, musicología, educación, partituras, instrumentos, interpretación, patrimonio y otros campos que se incorporen al catálogo.

Una noticia podrá pertenecer a más de un ámbito. Por ejemplo, una noticia sobre digitalización de manuscritos de una compositora puede ser a la vez patrimonio, musicología y música clásica.

### Alcance de esta primera fase

La clasificación temática se aplica a cada noticia y se almacena en el corpus común. No se implementarán todavía preferencias individuales, vistas personalizadas ni filtros asociados a cuentas de usuario. La taxonomía se diseña para que pueda reutilizarse en fases posteriores, pero en esta fase su función es organizar y consultar el conjunto de noticias recopiladas.


## 5. Taxonomía temática inicial

La taxonomía se plantea como un árbol de temas para clasificar el corpus. En una fase posterior podrá servir también para preferencias personales. Una noticia podrá recibir varias etiquetas; no se forzará a encajar en una única sección.

Esta es una propuesta de partida, no un catálogo cerrado:

### A. Actualidad musical general
- Noticias generales de música.
- Industria musical y mercado.
- Sellos, editoriales, promotores y salas.
- Plataformas digitales, streaming y distribución.
- Tecnología, inteligencia artificial y herramientas musicales.
- Derechos de autor, licencias y legislación.
- Políticas culturales, financiación y ayudas.
- Trabajo, asociaciones y organizaciones profesionales.

### B. Géneros y tradiciones musicales
- Música clásica y académica.
- Música coral y vocal.
- Ópera y música escénica.
- Rock y pop (incluidos indie, metal y otras escenas derivadas).
- Música urbana, hip-hop, rap y R&B.
- Reguetón y músicas urbanas latinoamericanas.
- Música electrónica y experimental.
- Jazz y blues.
- Flamenco y músicas de raíz ibérica.
- Músicas latinoamericanas y caribeñas.
- Folk, country, bluegrass y otras músicas tradicionales y del mundo.
- Reggae, ska y músicas jamaicanas.
- Música antigua y prácticas históricas.
- Bandas, música de viento y música para conjuntos.
- Música religiosa y litúrgica.
- Otros géneros, fusiones y escenas locales.

### C. Actividad y actualidad artística
- Conciertos, giras y temporadas.
- Festivales y ciclos.
- Estrenos y nuevas obras.
- Lanzamientos discográficos y audiovisuales.
- Premios, concursos y convocatorias.
- Entrevistas y perfiles.
- Fallecimientos, homenajes y aniversarios.
- Noticias de orquestas, coros, bandas y otros conjuntos.
- Noticias de teatros, auditorios y salas.

### D. Creación, interpretación y formación
- Compositores y creación musical.
- Intérpretes, directores y solistas.
- Dirección coral y práctica de conjunto.
- Instrumentos, técnica e interpretación.
- Educación, conservatorios y universidades.
- Cursos, talleres y formación.
- Investigación, musicología y etnomusicología.
- Composición, arreglos, edición y transcripción.

### E. Partituras, archivos y patrimonio
- Partituras y publicaciones musicales.
- Manuscritos y fuentes históricas.
- Bibliotecas, archivos y colecciones.
- Digitalización y acceso abierto.
- Patrimonio material e inmaterial.
- Instrumentos históricos y organología.
- Restauración, catalogación y conservación.

### F. Sociedad y música
- Música y sociedad.
- Música y salud, cuando la noticia sea informativa y esté respaldada por fuentes.
- Inclusión, accesibilidad y participación.
- Música en medios, cine, videojuegos y publicidad.
- Educación comunitaria y proyectos sociales.

### Reglas de clasificación

- Las ramas superiores agruparán sus subcategorías. La asignación de una categoría padre se podrá deducir de sus descendientes, evitando guardar etiquetas redundantes.
- Las categorías podrán combinarse; por ejemplo, una noticia de IA aplicada a la restauración de partituras podrá etiquetarse como tecnología, IA y patrimonio musical.
- Se distinguirá el **tema** de las entidades mencionadas (personas, obras, agrupaciones, instituciones, lugares). Las entidades se podrán normalizar más adelante, pero no se convertirán en categorías temáticas.
- La clasificación debe guardar tanto las etiquetas asignadas como la versión de la taxonomía utilizada, para que los cambios futuros no alteren silenciosamente el significado del histórico.
- La fuente de procedencia orientará el análisis, pero no determinará por sí sola la categoría: cada noticia se clasificará por su contenido.
- Se admitirán etiquetas «otros» y «pendiente de clasificación» para no descartar noticias solo porque el árbol todavía no contemple su tema.

La taxonomía se validará con una muestra de noticias reales de ámbitos distintos antes de cerrar el catálogo definitivo. Los criterios operativos de inclusión, exclusión y asignación múltiple se detallan en [Criterios editoriales y de clasificación](04-criterios-clasificacion.md).

## 6. Uso de IA

El sistema no dependerá directamente de un proveedor concreto. Se definirá una interfaz común para poder utilizar Gemini, Groq u otro servicio compatible.

La IA recibirá únicamente los metadatos y fragmentos necesarios para clasificar la noticia. No se enviará el contenido completo de una página salvo que exista una justificación y permiso adecuados.

### Resultado estructurado propuesto

- relevant: booleano.
- categories: lista de categorías controladas.
- original_language: idioma original detectado, preferiblemente con código BCP 47.
- language_evidence: idioma declarado por la fuente, detectado en el texto o inferido con confianza.
- relevance_reason: explicación breve basada en el contenido recibido.
- editorial_title_es: título editorial en español, si procede.
- summary_es: resumen divulgativo en español, si procede.
- translations: traducciones adicionales, cada una identificada por idioma destino y vinculada a la versión del contenido original que se tradujo.
- confidence: confianza estimada, si el proveedor la ofrece de forma útil.
- needs_review: indicador de revisión humana.

La aplicación validará el JSON y los campos. Una respuesta inválida, incompleta o contradictoria se marcará como error de análisis y podrá reintentarse; no se guardará como noticia aprobada.

La IA no debe inventar fechas, lugares, participantes ni resultados. Si el fragmento no contiene información suficiente, debe indicarlo y solicitar revisión, no completar los huecos mediante suposiciones.

## 7. Persistencia MySQL/MariaDB: modelo conceptual

El modelo se ha desarrollado en [Modelo conceptual de persistencia](08-modelo-conceptual-persistencia.md). Se distinguen publisher/editor, canal técnico, ejecución de captura, observación recibida, publicación concreta y noticia consolidada. Las publicaciones oficiales en distintos idiomas permanecen separadas y pueden relacionarse con una misma noticia; una publicación puede descubrirse mediante varios canales.

El modelo incluye análisis versionados, taxonomía y asignaciones, textos editoriales en español y traducciones preparadas para una fase posterior. Los estados de captura, análisis y traducción son independientes. No se incorporan usuarios, preferencias ni boletines.

El documento 08 define entidades, relaciones, estados, identidad, versionado y cuestiones técnicas pendientes. Todavía no fija tablas ni columnas SQL.

## 8. Boletín por correo: fase posterior

El boletín no forma parte de la primera fase ni debe generar trabajo de implementación ahora. Cuando se aborde, el sistema deberá:

- Permitir que el usuario active voluntariamente la suscripción.
- Registrar el consentimiento y permitir darse de baja fácilmente.
- Evitar envíos duplicados de una misma edición al mismo destinatario.
- Generar HTML y una alternativa de texto plano.
- Registrar resultados y errores sin almacenar más datos personales de los necesarios.
- Respetar límites del proveedor, rebotes y requisitos de autenticación del dominio (SPF, DKIM y DMARC).

Se estudiarán el SMTP del alojamiento y servicios externos como Brevo. Las cuotas gratuitas, límites y condiciones comerciales pueden cambiar y deberán verificarse antes de elegir proveedor. No se fijará una cuota concreta en el diseño.

## 9. Derechos, atribución y uso responsable

- Priorizar feeds y APIs oficiales y respetar sus condiciones de uso.
- Guardar título, metadatos, fragmentos suministrados por el feed, enlace y atribución de la fuente.
- No copiar ni redistribuir artículos completos.
- El resumen generado debe ser original, breve y basado en la información disponible.
- Mostrar claramente el medio o institución de origen y enlazar a la noticia original.
- Respetar las condiciones de cada API, robots/limitaciones aplicables y las solicitudes de retirada cuando proceda.

## 10. Ejecución y operación

Se prevé una ejecución programada (por ejemplo, diaria al inicio), pero la frecuencia se configurará por fuente. Las tareas deberán ser idempotentes y reanudables:

- Repetir una consulta no debe duplicar noticias.
- Un fallo de una fuente no debe detener las demás.
- Los errores y tiempos de respuesta deben quedar registrados.
- La clasificación pendiente debe poder retomarse sin volver a recolectar.
- Los procesos deben registrar sus intentos y errores para permitir reintentos controlados.

No se ha decidido aún si la programación se realizará mediante cron, el programador del sistema o un worker persistente propio.

## 11. Fases propuestas

### Fase 1: recopilación y carga en base de datos (alcance actual)

1. Inventariar y verificar fuentes RSS/APIs.
2. Acordar categorías y criterios de clasificación con ejemplos reales.
3. Diseñar el esquema MySQL/MariaDB y los estados de procesamiento.
4. Construir y probar la recolección, normalización y deduplicación.
5. Incorporar clasificación y resumen mediante una IA intercambiable.
6. Persistir noticias, procedencia, categorías y análisis en la base de datos.
7. Verificar integridad, ausencia de duplicados y posibilidad de reanudar capturas y análisis pendientes.

**Criterio de finalización:** las fuentes previstas se consultan de forma repetible y las noticias quedan cargadas en MySQL/MariaDB con sus metadatos, procedencia, clasificación y estado de procesamiento. La carga debe poder repetirse sin duplicar registros.

### Fases posteriores (fuera del alcance actual)

- Herramientas de revisión y gestión editorial, si se consideran necesarias.
- Preferencias temáticas por usuario y vistas personalizadas.
- Integración con cuentas y servicios de OSAP.
- Suscripciones, generación de boletines y envío de correo.

La programación, observabilidad, recuperación y mantenimiento se resolverán en la medida necesaria para que la primera fase funcione de forma fiable; no se pospondrán los controles técnicos imprescindibles para una carga correcta.
