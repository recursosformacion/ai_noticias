# Idioma original, traducciones y presentación multilingüe

**Estado:** diseño funcional para la primera fase de ingesta y persistencia. La selección de idioma por usuario y la presentación de noticias pertenecen a una fase posterior, pero el corpus debe almacenar desde el principio la información necesaria para ofrecer ambas posibilidades.

## 1. Principio general

Cada noticia tiene un idioma original, que debe conservarse y no sustituirse por una traducción. El sistema podrá disponer, además, de versiones traducidas de sus campos editoriales.

En una fase posterior, el usuario podrá elegir entre:

- **Idioma original:** mostrar el título y el resumen en el idioma en que se publicó la noticia, y abrir la fuente original.
- **Idioma preferido:** mostrar una traducción disponible en el idioma elegido.
- **Versión de la fuente:** si el medio ofrece una edición oficial en otro idioma, utilizar su URL y contenido como una versión publicada por el propio medio, no como traducción de ai_noticias.

No se debe asumir que una noticia está traducida porque la web de la fuente tenga selector de idioma. Hay que comprobar que exista una versión real del artículo, con su propia URL o identificador, y que corresponda al mismo contenido.

## 2. Qué significa traducir una noticia

Conviene distinguir tres niveles:

1. **Contenido original capturado:** título, descripción, fragmento y metadatos que proporciona el feed/API. Se conserva tal cual y se identifica su idioma.
2. **Texto editorial de ai_noticias:** título y resumen propios, redactados a partir de la información disponible. No equivalen al artículo completo.
3. **Traducciones editoriales:** versiones del título y resumen de ai_noticias a otros idiomas. Se almacenan separadas del original y vinculadas a la versión que se tradujo.

No se copiará ni traducirá íntegramente un artículo protegido para almacenarlo o redistribuirlo, salvo que exista una autorización o licencia que lo permita. La traducción de un resumen propio y breve es un caso distinto de reproducir el artículo original.

## 3. Detección y normalización del idioma

Para cada aparición de una noticia se conservarán, cuando existan:

- Idioma declarado en RSS/Atom/API (por ejemplo, idioma del canal o del elemento).
- Idioma detectado a partir del título y la descripción.
- Código normalizado del idioma, preferiblemente BCP 47 (por ejemplo, es, ca, en, fr, de, pt-BR).
- Fuente de la información lingüística: declarado, detectado o inferido.
- Confianza de la detección cuando no haya una declaración fiable.

El idioma del canal no debe aplicarse ciegamente a todos sus elementos: una fuente puede publicar contenido en varios idiomas. Si el texto es demasiado corto o mezcla idiomas, se marcará como incierto en lugar de asignar un idioma con falsa seguridad.

En una noticia consolidada que aparezca en varios medios o ediciones lingüísticas, cada aparición debe conservar su propio idioma. El registro consolidado puede tener un idioma original principal, pero no debe perder las variantes de procedencia.

## 4. Estrategia: versión oficial de la fuente y traducción propia

Son dos mecanismos complementarios, no excluyentes.

### 4.1 Versión publicada por la fuente

Si el medio dispone de una versión oficial de la misma noticia en el idioma solicitado:

- Preferir esa versión para enlazar al artículo.
- Conservar su URL, idioma e identificador como otra aparición o variante de la noticia.
- Mantener la atribución al medio.
- No traducir automáticamente el contenido de esa página ni asumir que ambas versiones son idénticas; pueden diferir en extensión o actualización.

La búsqueda de versiones oficiales debe hacerse durante la ingesta o mediante metadatos/API documentados, no depender de que la interfaz de la fuente permita cambiar de idioma en el momento de mostrar la noticia.

### 4.2 Traducción realizada por ai_noticias

Si no hay una versión oficial disponible:

- Utilizar el título y resumen editorial de ai_noticias como material traducible.
- Generar traducciones bajo demanda cuando una fase posterior conozca los idiomas que se necesitan, o en lotes si se decide que resulta más eficiente.
- Guardar cada traducción en la base de datos para reutilizarla, no repetir la llamada a IA cada vez que alguien consulte la noticia.
- Registrar idioma origen, idioma destino, modelo/proveedor, fecha, versión de instrucciones y versión del texto fuente.
- Si el contenido original cambia de forma sustancial, marcar las traducciones afectadas como desactualizadas y regenerarlas cuando se soliciten.

La traducción debe ser fiel y no añadir información. Nombres propios, títulos de obras, instituciones, citas y terminología musical requieren especial cuidado. Los títulos oficiales de obras y nombres de personas no se traducirán salvo que exista una forma reconocida en el idioma destino.

## 5. Qué se traduce en la primera fase

La primera fase debe dejar los datos preparados y cargar los siguientes elementos:

- Título original.
- Descripción o fragmento original disponible.
- Idioma original y evidencia de detección.
- Título editorial en español.
- Resumen editorial en español.
- Si una fuente ofrece una versión lingüística oficial identificable, su URL e idioma.

No es necesario generar ahora traducciones a todos los idiomas posibles. Hacerlo sin conocer todavía las preferencias de los usuarios produciría traducciones que quizá nunca se utilicen y elevaría innecesariamente el coste de IA.

El modelo de persistencia sí debe permitir añadir traducciones en otros idiomas sin modificar ni sobrescribir el original ni el resumen español. En una fase posterior se decidirá si se generan bajo demanda, anticipadamente para los idiomas más utilizados o combinando ambos métodos.

## 6. Ejemplo de funcionamiento futuro

Una noticia se publica en inglés:

- Original: título y descripción en inglés, idioma en.
- ai_noticias: título editorial y resumen en español, idioma es.
- La fuente no ofrece versión en español.
- En una fase posterior, una persona que elija catalán solicita esa noticia:
  - Si existe versión oficial en catalán, se ofrece esa versión y su enlace.
  - Si no existe, se traduce el resumen editorial al catalán (ca) y se guarda en la tabla de traducciones.
  - El usuario que elija idioma original seguirá viendo el texto inglés y el enlace original.

La traducción catalana no reemplaza ni altera el registro inglés ni el resumen español.

## 7. Datos que debe conservar el modelo

Sin fijar todavía columnas SQL, el modelo conceptual debe contemplar:

- Idioma declarado por la fuente.
- Idioma detectado y código normalizado.
- Evidencia y confianza de la detección.
- Idioma de cada aparición o versión publicada por una fuente.
- Idioma del texto editorial base.
- Traducciones por idioma destino.
- Versión del contenido que se tradujo.
- Proveedor/modelo, versión de prompt, fecha y estado de la traducción.
- Relación entre traducción generada y noticia original.

La traducción debe tener estados independientes (pendiente, completada, error o desactualizada). Un fallo de traducción nunca debe bloquear la captura, clasificación ni almacenamiento de la noticia original.

## 8. Criterio de aceptación para la primera fase

La primera fase estará preparada para la futura consulta multilingüe cuando:

1. Cada noticia conserve su título y descripción originales.
2. El idioma se registre con un código normalizado y una indicación de cómo se obtuvo.
3. Las fuentes con varios idiomas no asignen automáticamente el idioma del canal a todas las noticias.
4. Cada aparición en una fuente conserve su propio idioma y URL.
5. El título y resumen editorial en español se almacenen como contenido separado.
6. El modelo admita traducciones adicionales sin sobrescribir el original.
7. Los fallos o cambios de traducción no afecten al estado de captura ni al análisis editorial.
8. Se pueda determinar qué versión original se utilizó para generar cada traducción.

La preferencia de idioma de cada usuario, la interfaz para alternar entre original y traducción y la generación bajo demanda se implementarán en una fase posterior.
