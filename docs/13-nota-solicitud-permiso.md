# Nota de solicitud de permiso a entidades y editores

**Uso:** enviar a los editores cuyo RSS está localizado pero cuya reutilización no está
autorizada. Se personaliza lo marcado entre corchetes.

---

**Asunto:** Solicitud de autorización para la inclusión de sus contenidos musicales en el servicio de noticias de OSAP

Estimados señores:

Me dirijo a ustedes en nombre de **[NOMBRE DE LA ENTIDAD/ASOCIACIÓN]**, responsable del
proyecto **OSAP** —Open Source Academic Platform, una plataforma de acceso libre dedicada a
la documentación y difusión de la música académica—.

Estamos poniendo en marcha un **servicio gratuito de actualidad musical** que reúne noticias
de fuentes especializadas y las ofrece a los usuarios registrados de la plataforma en su
idioma de preferencia. El servicio **no tiene ánimo de lucro**, no incluye publicidad y no
redistribuye los textos completos: únicamente muestra el **titular, un breve extracto y un
enlace directo** a la noticia original en su web.

Hemos localizado el canal RSS de **[NOMBRE DEL MEDIO]**, que consideramos una referencia de
primer nivel para nuestros usuarios. Antes de incorporarlo les escribimos porque sus
condiciones de uso **[requieren autorización previa / reservan todos los derechos]** y
queremos actuar con el máximo respeto a su labor editorial.

**Qué le solicitamos concretamente**

1. Autorización para **consultar periódicamente** su canal RSS y detectar las noticias
   publicadas.
2. Autorización para **almacenar el titular, la descripción y los metadatos** (autor, fecha
   y URL) de cada noticia, junto con un enlace a su página original.
3. Autorización para **mencionar su medio como fuente** en los resúmenes enviados a nuestros
   usuarios, con la atribución y el enlace que ustedes indiquen.

**Qué no haremos sin su consentimiento expreso**

- No publicaremos ni redistribuiremos el texto completo de sus artículos.
- No reproduciremos sus imágenes, vídeos ni material gráfico.
- No utilizaremos sus contenidos para entrenar modelos de inteligencia artificial.
- No permitiremos la reventa ni el uso comercial de la información.

**Modalidad de atribución propuesta** (pueden modificarla a su criterio):

> _Titular de la noticia_ — [nombre del medio], [fecha]. Enlace: [URL original].

Quedamos a su disposición para firmar cualquier acuerdo de licencia, aceptar sus condiciones
técnicas (frecuencia de consulta, identificación del robot, límites de peticiones) o adaptar
la modalidad de cita a lo que estimen oportuno. Igualmente, si prefieren que limitemos la
presencia a un enlace sin extracto, lo haremos así.

Les agradeceríamos una respuesta antes del **[FECHA]**, indicándonos si podemos incorporar su
canal a partir de ese momento.

Gracias por su tiempo y por el trabajo que hacen en favor de la música.

Atentamente,

**[NOMBRE Y APELLIDOS]**
[Topo] — [Entidad]
[Correo electrónico] · [Teléfono]
[Web del proyecto]

---

## Anexo: entidades a las que enviar esta nota

| Medio                    | Sitio                                    | Contacto / vía          | Estado                                     |
| ------------------------ | ---------------------------------------- | ----------------------- | ------------------------------------------ |
| Scherzo                  | https://scherzo.es/                      | Aviso legal / redacción | Pendiente                                  |
| Beckmesser               | https://www.beckmesser.com/              | Aviso legal             | Pendiente                                  |
| Bachtrack                | https://bachtrack.com/                   | Conditions of use       | Pendiente                                  |
| Musicology Now (AMS)     | https://musicologynow.org/               | Junta editorial de AMS  | Pendiente                                  |
| Music Business Worldwide | https://www.musicbusinessworldwide.com/  | Terms of use            | Pendiente                                  |
| NPR Music                | https://www.npr.org/                     | Permissions desk        | Pendiente (prohíbe IA sin permiso escrito) |
| Ópera Actual             | https://www.operaactual.com/             | Redacción               | Pendiente (feed sin validar)               |
| Doce Notas               | https://www.docenotas.com/               | Aviso legal             | Pendiente                                  |
| Platea Magazine          | https://www.plateamagazine.com/          | Redacción               | Pendiente (feed no válido)                 |
| Melómano Digital         | https://www.melomanodigital.com/         | Redacción               | Pendiente (feed no válido)                 |
| Codalario                | https://www.codalario.com/               | Redacción               | Pendiente (feed no válido)                 |
| Revista Musical Chilena  | https://revistamusicalchilena.uchile.cl/ | Dirección editorial     | Pendiente (feed no válido)                 |
| Anuario Musical (CSIC)   | https://anuariomusical.revistas.csic.es/ | CSIC                    | Pendiente (feed no válido)                 |

**Nota sobre la BNE:** además del permiso editorial, la Biblioteca Nacional de España no
permite el acceso automatizado (HTTP 403). Conviene consultarles expresamente por el uso de
sus canales RSS.

## Seguimiento

| Fecha | Medio | Respuesta | Autoriza | Condiciones | Incorporado al catálogo |
| ----- | ----- | --------- | -------- | ----------- | ----------------------- |
|       |       |           |          |             |                         |

Cuando un medio responda afirmativamente:

1. Guardar la respuesta en `docs/permisos/` con el nombre `AAAA-MM-DD_medio.pdf`.
2. Activar el canal con `python -m app.cli activate --source-id ID --confirm-terms-reviewed`
   una vez revisadas las condiciones.
3. Anotar en `source_channels.usage_policy` la referencia del permiso concedido.
