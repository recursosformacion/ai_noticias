# Módulo de boletín por correo (histórico; no es la integración vigente)

> **Aviso:** este documento describe el diseño antiguo. OSAP ya no usa `digest`,
> `mailbox`, `outbound_messages` ni la lista `/api/v1/admin/users`. La vía vigente es
> la API de consulta con sesión OSAP: [16-integracion-osap.md](16-integracion-osap.md).

## 1. Qué hace

Un proceso periódico que, en cada ejecución:

1. **Actualiza las noticias** consultando los canales RSS activos.
2. **Recorre los usuarios de OSAP** que han aceptado recibir noticias.
3. **Prepara un boletín personalizado** por usuario: en su idioma y con sus temas.
4. **Deja el mensaje en la cola** `outbound_messages`.

El envío del correo **no lo hace este módulo**: corresponde a OSAP, que es el propietario de
las comunicaciones.

```
cron → app.cli digest
         ├─ 1. ingest_active_channels()        (fuentes RSS/Atom)
         ├─ 2. GET osap-auth /api/v1/admin/users
         ├─ 3. process_request()  por usuario  (filtra por idioma y temas)
         └─ 4. INSERT outbound_messages (user_ref, asunto, texto, HTML)
                                      ↓
                           OSAP (osap-support) envía
```

## 2. Regla de aislamiento entre servicios

**`ai_noticias` solo lee su propia base de datos (`osap_noticias`).**

Todo lo demás se consulta por API:

| Necesidad               | Origen      | Endpoint                   |
| ----------------------- | ----------- | -------------------------- |
| Usuarios y preferencias | `osap-auth` | `GET /api/v1/admin/users`  |
| Catálogo de géneros     | `osap-api`  | `GET /api/v1/genres`       |
| Búsqueda de obras       | `osap-api`  | `GET /api/v1/search/works` |

No hay ninguna conexión a `osap_auth` ni a `osap_storage`: ni credenciales de esas bases en
`osap.toml` ni driver que las abra. Esto evita acoplarse a su esquema interno y permite que
esos servicios evolucionen sin romper el boletín.

## 3. Configuración (`osap.toml`)

```toml
[db]
host = "127.0.0.1"
name = "osap_noticias"
user = "..."
password = "..."

[apis]
enabled = true
service_email = "servicio@osap.local"   # cuenta de servicio para el login
service_password = ""                   # mejor en OSAP_NEWS_SERVICE_PASSWORD
timeout = 10

[apis.identity]        # osap-auth
url = "http://127.0.0.1:8001"
# token = ""           # alternativa al login: token de larga duración

[apis.catalog]         # osap-api
url = "http://127.0.0.1:8000"

[noticias]
default_language = "es"
max_items = 20
window_days = 365

[mail]
from_address = "noticias@osap.local"
from_name = "OSAP Noticias"
delivery = "QUEUE"
outbound_dir = "var/outbound"
```

Variables de entorno equivalentes (preferibles para secretos):

- `OSAP_NEWS_SERVICE_EMAIL`, `OSAP_NEWS_SERVICE_PASSWORD`
- `OSAP_NEWS_IDENTITY_API_URL`, `OSAP_NEWS_IDENTITY_TOKEN`
- `OSAP_NEWS_CATALOG_API_URL`, `OSAP_NEWS_CATALOG_TOKEN`
- `OSAP_NEWS_DELIVERY`, `OSAP_NEWS_MAIL_FROM`

## 4. Uso

```bash
# Ciclo completo (lo que ejecuta el cron)
py -3 -m app.cli digest

# Sin capturar fuentes (solo enviar lo ya almacenado)
py -3 -m app.cli digest --no-ingest

# Simulación: calcula sin escribir en la cola
py -3 -m app.cli digest --dry-run

# Un solo usuario
py -3 -m app.cli digest --user 3f2b1c…

# Prueba manual a una dirección concreta y todos los temas
py -3 -m app.cli digest --to alguien@example.org --all-topics --lang fr

# Ver el último mensaje generado
py -3 -m tools.ver_mensaje
```

## 5. Programación (cron)

```cron
# Todos los días a las 07:00, hora local del servidor
0 7 * * *  cd /opt/ai_noticias && /usr/bin/python3 -m app.cli digest >> var/log/digest.log 2>&1
```

En Windows, Programador de tareas:

```
Programa:      py.exe
Argumentos:    -m app.cli digest
Directorio:    D:\Proyectos\AI_OSAP\ai_noticias
```

## 6. Garantías

| Garantía                       | Cómo se cumple                                       |
| ------------------------------ | ---------------------------------------------------- |
| No duplicar noticias           | Identidad por SHA-256 de la descripción normalizada  |
| No repetir el boletín del día  | `outbound_messages(user_ref, digest_date)`           |
| Un fallo no detiene el lote    | Cada usuario se procesa en su propio `try`           |
| La captura no bloquea el envío | Si falla la red, se envía lo ya almacenado           |
| No enviar correos vacíos       | Si no hay noticias, no se encola nada                |
| Sin correos en claro           | La cola guarda `user_ref`; el buzón lo resuelve OSAP |

## 7. Lo que se necesita de los otros módulos

### 7.1 Obligatorio: `osap-auth` — endpoint de usuarios (ya existe)

`GET /api/v1/admin/users` devuelve por usuario: `id`, `email`, `status`, `news_opt_in`,
`news_language`, `news_topics`. **Falta una credencial con permiso para llamarlo.**

Estado comprobado el 15-11-2026:

- Los clientes de servicio de `osap-auth` existen, pero **ninguno tiene el scope necesario**.
- Hay un usuario `OSAP Admin`, pero su contraseña no está disponible para este servicio.

**Necesitamos:** una cuenta de servicio (o un token de larga duración) con permiso de lectura
sobre el endpoint de usuarios. Basta un cliente de servicio con scope `users:read`. Sin eso,
el boletín no puede saber a quién enviar.

### 7.2 Obligatorio: `osap-support` — envío desde la cola

`ai_noticias` deja los mensajes en `outbound_messages`. Falta el consumidor que los envíe:

1. `SELECT ... FROM outbound_messages WHERE status='PENDING' FOR UPDATE SKIP LOCKED`
2. Resolver el buzón a partir de `user_ref` (o usar `recipient_address` si no hay `user_ref`).
3. Enviar con el `EmailSender` de `osap-support` usando `subject`, `body_text` y `body_html`.
4. Marcar `status='SENT'` y `sent_at`, o `'FAILED'` incrementando `attempts`.

**Por qué así:** el correo es una responsabilidad de OSAP (ADR-006). Duplicar aquí el envío
implicaría dos propietarios de la misma función, dos juegos de credenciales SMTP y dos
políticas de rebotes.

### 7.3 Recomendado: `osap-api` — más vocabulario

Hoy el catálogo aporta los 12 géneros. Sería útil un endpoint de **personas e instrumentos**
filtrable (`GET /api/v1/persons?q=…`) para enriquecer los temas con compositores e
intérpretes sin descargar miles de registros.

### 7.4 Para la web de OSAP

Una página donde el usuario marque «recibir noticias musicales», elija idioma y temas.
Con eso, `ai_noticias` no necesita ninguna gestión de preferencias propia.

## 8. Estado de la prueba del 15-11-2026

| Aspecto           | Resultado                                              |
| ----------------- | ------------------------------------------------------ |
| Captura           | 46 noticias nuevas incorporadas                        |
| Cola de salida    | Mensaje generado para `migarcia@recursosformacion.com` |
| Idiomas           | `en` 106 noticias, `fr` 50, **`es` 0**                 |
| Temas             | Los 12 del catálogo, traducidos al idioma del envío    |
| Lista de usuarios | **No disponible**: falta credencial de servicio        |

### Limitación conocida: no hay corpus en español

Las tres fuentes en español comprobadas (Scherzo, Doce Notas, Platea, Melómano, Codalario)
prohíben la reproducción sin autorización escrita, y la BNE bloquea el acceso automatizado.
TRANS (SIBE) tiene licencia CC BY-NC-ND, pero su RSS no incluye descripción y, sin ella, no
se puede calcular la identidad de la noticia conforme al criterio del documento 05.

**Consecuencia:** un usuario cuyo idioma sea `es` recibe hoy un boletín vacío. Hay dos salidas,
y ambas requieren decidir:

- **A.** Obtener autorización de algún medio en español (ver `13-nota-solicitud-permiso.md`).
- **B.** Aceptar una **identidad alternativa basada en el GUID** para fuentes sin descripción.
  Es un cambio de criterio editorial: permitiría usar TRANS y cualquier feed «solo titulares»,
  a cambio de renunciar a consolidar noticias por texto entre fuentes.

