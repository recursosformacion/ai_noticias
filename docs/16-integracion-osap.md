# Integración de ai_noticias en OSAP

## Decisión

`ai_noticias` deja de ser un servicio de correo y pasa a ser el **corpus de noticias**
que OSAP consulta en nombre de un usuario autenticado.

La corrección afecta a dos puntos:

1. **Forma de acceso**: el usuario entra en OSAP (`/noticias`) con su sesión. No se
   accede por correo, ni se pide al usuario que escriba a un buzón.
2. **Filosofía de comunicaciones**: OSAP es el propietario de la identidad, el
   consentimiento y cualquier envío. `ai_noticias` no lee la lista de usuarios, no
   guarda direcciones y no encola correos.

## Flujo correcto

```
usuario autenticado
  → OSAP /noticias
  → OSAP lee idioma/temas de osap-auth
  → GET ai_noticias /api/v1/news?language=…&topics=…
  → tarjetas en la web
```

Si en el futuro se activa un resumen por correo:

```
OSAP worker (propietario)
  → lee usuarios con consentimiento explícito
  → pide el resumen a ai_noticias (solo idioma/temas)
  → crea CommunicationEvent
  → EmailSender de osap-support
```

`ai_noticias` **no** crea `CommunicationEvent`, no habla SMTP y no escribe
`outbound_messages`.

## Contrato interno

Cabecera obligatoria: `X-OSAP-News-Token` (comparada con `OSAP_NEWS_API_TOKEN`;
sin token configurado la API falla cerrada).

### `GET /api/v1/news/topics`

Devuelve el catálogo temático:

```json
{"items": [{"code": "coral", "name": "Música coral", "description": "…"}], "count": 1}
```

### `GET /api/v1/news`

Parámetros: `language` (es, ca, fr, en, de, it, pt), `topics` (códigos separados por
coma), `limit` (1–100) y `days` (1–3650).

```json
{
  "items": [
    {
      "news_item_id": 1,
      "title": "…",
      "summary": "…",
      "url": "https://fuente.example/…",
      "published_at": "2026-11-15T00:00:00",
      "publisher": "…",
      "language": "en",
      "matched": ["opera"]
    }
  ],
  "count": 1,
  "language": "en",
  "topics": ["opera"]
}
```

La API no recibe `user_ref`, `email` ni nombres. No escribe en la base: es solo lectura.

## Qué queda obsoleto

Estos caminos siguen en el repositorio como herramientas históricas, pero **no son la
integración de OSAP** y no deben usarse en producción:

- `app.cli mailbox`: responder correos entrantes.
- `app.cli digest`: recorrer usuarios y encolar boletines.
- `app.subscribers`: pedir `/api/v1/admin/users` con credenciales de servicio.
- `outbound_messages`: cola de correo propia.

Conservan valor para pruebas del corpus y para entender el histórico, pero la
autoridad de usuarios y comunicaciones es OSAP.

## Configuración de desarrollo

`ai_noticias`:

```bash
$env:OSAP_NEWS_API_TOKEN = "osap-dev-news-token"
python -m uvicorn app.api:app --host 127.0.0.1 --port 8400
```

`osap-api`:

```bash
$env:OSAP_NEWS_API_BASE = "http://127.0.0.1:8400"
$env:OSAP_NEWS_API_TOKEN = "osap-dev-news-token"
```

El script `osap-api/script/restart-dev.ps1` incluye ambos servicios y variables.
En producción, el token debe venir del gestor de secretos y la API no debe exponerse
fuera de la red interna.

