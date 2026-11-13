# Propuesta funcional y arquitectura inicial

**Estado:** borrador de trabajo. No es todavía una especificación de implementación.

## 1. Objetivo del paquete

Recopilar automáticamente noticias y novedades relacionadas con la música, con especial interés inicial en música clásica, coral, musicología, partituras, archivos y patrimonio musical. Las entradas relevantes se conservarán en MySQL/MariaDB y podrán utilizarse posteriormente para elaborar un boletín en español.

El sistema debe mantener la trazabilidad hasta la fuente original y distinguir claramente entre los datos publicados por la fuente y el texto redactado por la IA.

## 2. Flujo general

1. **Fuentes:** mantener un catálogo de fuentes RSS/Atom y APIs, con URL, tipo, idioma, temática, frecuencia, estado y última consulta.
2. **Recolección:** consultar las fuentes periódicamente, respetando sus condiciones de uso, límites y cabeceras HTTP cuando proceda.
3. **Normalización:** convertir cada elemento a un formato común: fuente, identificador externo, URL canónica, título, descripción disponible, autor, idioma, fecha de publicación y fecha de captura.
4. **Deduplicación:** detectar repetidos mediante identificador de origen, URL normalizada y, como apoyo, huella del título. Una misma noticia puede aparecer en varias fuentes; conviene conservar esas relaciones en lugar de perder la procedencia.
5. **Preclasificación:** aplicar reglas sencillas de términos y categorías para descartar ruido evidente y reducir llamadas innecesarias a la IA.
6. **Clasificación con IA:** decidir si la entrada es pertinente y asignar una o varias categorías. La respuesta debe ajustarse a un esquema JSON validable.
7. **Redacción:** para las entradas aceptadas, generar un título editorial y un resumen breve en español, sin añadir hechos que no estén respaldados por el material recibido.
8. **Revisión y publicación:** dejar las noticias clasificadas disponibles para revisión, selección o inclusión automática según una política que se decidirá más adelante.
9. **Boletín:** preparar una edición con las noticias seleccionadas y enviarla a los suscriptores que hayan dado consentimiento.

La recolección, el análisis y el envío serán tareas independientes. Un fallo del proveedor de IA o del SMTP no debe obligar a descargar de nuevo los feeds ni perder las noticias ya almacenadas.

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

## 4. Clasificación temática inicial

Categorías candidatas:

- Música clásica.
- Música coral y vocal.
- Musicología e investigación.
- Partituras, edición y publicaciones musicales.
- Manuscritos y fuentes históricas.
- Patrimonio musical, archivos y bibliotecas.
- Interpretación, conciertos y festivales.
- Compositores, intérpretes, agrupaciones e instituciones.
- Educación y formación musical.

La clasificación deberá permitir varias categorías por noticia y conservar una explicación breve de por qué se considera pertinente. Las categorías definitivas y sus límites se acordarán con ejemplos reales.

## 5. Uso de IA

El sistema no dependerá directamente de un proveedor concreto. Se definirá una interfaz común para poder utilizar Gemini, Groq u otro servicio compatible.

La IA recibirá únicamente los metadatos y fragmentos necesarios para clasificar la noticia. No se enviará el contenido completo de una página salvo que exista una justificación y permiso adecuados.

### Resultado estructurado propuesto

- relevant: booleano.
- categories: lista de categorías controladas.
- language: idioma detectado.
- relevance_reason: explicación breve basada en el contenido recibido.
- editorial_title_es: título en español, si procede.
- summary_es: resumen divulgativo en español, si procede.
- confidence: confianza estimada, si el proveedor la ofrece de forma útil.
- needs_review: indicador de revisión humana.

La aplicación validará el JSON y los campos. Una respuesta inválida, incompleta o contradictoria se marcará como error de análisis y podrá reintentarse; no se guardará como noticia aprobada.

La IA no debe inventar fechas, lugares, participantes ni resultados. Si el fragmento no contiene información suficiente, debe indicarlo y solicitar revisión, no completar los huecos mediante suposiciones.

## 6. Persistencia MySQL/MariaDB: entidades conceptuales

El esquema físico se diseñará después de validar el flujo. Como punto de partida se identifican estas entidades:

- **news_sources:** catálogo de feeds, APIs e instituciones.
- **source_fetches:** ejecuciones de consulta, fecha, resultado, estado y errores.
- **news_items:** noticia normalizada, fechas, título original, descripción disponible, URL y estado de procesamiento.
- **news_item_sources:** relación entre una noticia consolidada y las apariciones en distintas fuentes.
- **news_ai_analysis:** proveedor/modelo, versión de prompt, clasificación, JSON recibido, resumen generado, fecha y estado.
- **news_categories:** catálogo controlado de categorías.
- **news_item_categories:** relación entre noticias y categorías.
- **newsletter_editions:** ediciones del boletín y su estado.
- **newsletter_edition_items:** noticias incluidas en cada edición y orden de presentación.
- **newsletter_subscriptions:** suscripciones, consentimiento, fecha de alta/baja y estado.
- **newsletter_delivery_log:** registro de envíos, destinatario, edición, fecha y resultado, con retención limitada.

La vinculación de suscriptores con cuentas de OSAP deberá hacerse mediante el identificador de usuario acordado con el sistema de autenticación, sin duplicar innecesariamente datos personales. No se presupone todavía el nombre ni la estructura de las tablas de usuarios existentes.

## 7. Boletín por correo

El envío será una fase posterior a la recolección y clasificación. El sistema deberá:

- Permitir que el usuario active voluntariamente la suscripción.
- Registrar el consentimiento y permitir darse de baja fácilmente.
- Evitar envíos duplicados de una misma edición al mismo destinatario.
- Generar HTML y una alternativa de texto plano.
- Registrar resultados y errores sin almacenar más datos personales de los necesarios.
- Respetar límites del proveedor, rebotes y requisitos de autenticación del dominio (SPF, DKIM y DMARC).

Se estudiarán el SMTP del alojamiento y servicios externos como Brevo. Las cuotas gratuitas, límites y condiciones comerciales pueden cambiar y deberán verificarse antes de elegir proveedor. No se fijará una cuota concreta en el diseño.

## 8. Derechos, atribución y uso responsable

- Priorizar feeds y APIs oficiales y respetar sus condiciones de uso.
- Guardar título, metadatos, fragmentos suministrados por el feed, enlace y atribución de la fuente.
- No copiar ni redistribuir artículos completos.
- El resumen generado debe ser original, breve y basado en la información disponible.
- Mostrar claramente el medio o institución de origen y enlazar a la noticia original.
- Respetar las condiciones de cada API, robots/limitaciones aplicables y las solicitudes de retirada cuando proceda.

## 9. Ejecución y operación

Se prevé una ejecución programada (por ejemplo, diaria al inicio), pero la frecuencia se configurará por fuente. Las tareas deberán ser idempotentes y reanudables:

- Repetir una consulta no debe duplicar noticias.
- Un fallo de una fuente no debe detener las demás.
- Los errores y tiempos de respuesta deben quedar registrados.
- La clasificación pendiente debe poder retomarse sin volver a recolectar.
- El envío de una edición debe poder reintentarse sin duplicar entregas ya confirmadas.

No se ha decidido aún si la programación se realizará mediante cron, el programador del sistema o un worker persistente propio.

## 10. Fases propuestas

1. Inventariar y verificar fuentes RSS/APIs.
2. Acordar categorías, criterios de inclusión y exclusión con ejemplos.
3. Diseñar el esquema MySQL y los estados de procesamiento.
4. Construir y probar la recolección y deduplicación sin IA.
5. Incorporar clasificación y resumen mediante IA intercambiable.
6. Añadir revisión y gestión editorial.
7. Integrar suscripciones y boletines.
8. Programar ejecución, observabilidad, recuperación y mantenimiento.

No se debe iniciar el envío de correos ni una recolección masiva antes de validar las fases anteriores.
