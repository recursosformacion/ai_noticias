# Estado de conexión y preparación de la base de datos

**Base prevista:** `osap_noticias`.

## Configuración encontrada

El repositorio incluye `osap.toml`, siguiendo la estructura de configuración de OSAP. La configuración consultada apunta a una conexión local MySQL (`127.0.0.1:3306)) y a la base `osap_api`, no a `osap_noticias`. Por tanto, esa conexión no debe reutilizarse automáticamente: hay que comprobar permisos y separar la cuenta de servicio de noticias de la cuenta de OSAP API.

La contraseña no se documenta aquí. El fichero versionado se ha saneado y el valor se ha vaciado; se ha añadido `.gitignore` para evitar volver a incorporar `osap.toml`, ficheros `.env` y datos locales. La plantilla pública es `osap.example.toml`.

**Importante:** el repositorio es público y Git conserva el historial de commits. Vaciar el valor en el último commit no elimina el secreto de commits anteriores. La contraseña anterior debe considerarse expuesta y rotarse en el servidor MySQL. No se ha intentado conectar con esa cuenta ni crear la base de datos.

## Preparación disponible

- `database/migrations/001_initial_schema.sql`: crea `osap_noticias` si no existe y define las tablas iniciales.
- `database/migrations/002_seed_content_types.sql`: carga el catálogo inicial de tipos de contenido.
- `schema_migrations`: registra las migraciones aplicadas.
- `osap.example.toml`: plantilla sin credenciales.

## Compatibilidad y ejecución

La migración 001 está redactada para **MySQL 8.0.16 o posterior**. No se declara todavía compatibilidad validada con MariaDB. Antes de ejecutarla se debe comprobar la versión real del servidor y revisar los permisos de la cuenta específica de ai_noticias.

La migración debe ejecutarse una sola vez y en orden. Aunque varias tablas usan `IF NOT EXISTS`, el alta de la clave foránea circular de publicación principal no es una operación repetible sin control de migraciones. El ejecutor debe consultar `schema_migrations` y no volver a lanzar una versión ya aplicada.

No se ha ejecutado ninguna migración ni se ha realizado ninguna escritura en la base de datos.
