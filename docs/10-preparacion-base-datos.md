# Estado de conexión y preparación de la base de datos

**Base prevista:** `osap_noticias`.

## Configuración local

`osap.toml` es configuración de desarrollo/local y no debe distribuirse con el repositorio público.

- Está incluido en `.gitignore`.
- Se ha eliminado del seguimiento de Git; el repositorio ya no contiene ese fichero.
- La configuración local del equipo de desarrollo debe conservarse fuera del repositorio.
- La plantilla pública es `osap.example.toml`, sin credenciales.
- La base configurada para este proyecto debe ser `osap_noticias`, no `osap_api`.

El fichero local puede contener credenciales de desarrollo. No se copian sus valores a documentación, commits ni registros. El uso de esa conexión queda limitado al entorno de desarrollo y a la base prevista para este proyecto; no se debe ejecutar ninguna migración contra una base de producción ni contra `osap_api`.

**Historial Git:** el fichero `osap.toml` estuvo versionado anteriormente. Aunque ya no está en la rama actual, sus versiones históricas pueden seguir accesibles en el historial del repositorio. Si alguna credencial histórica deja de ser válida o se considera expuesta, debe rotarse. No se ha reescrito el historial Git.

## Preparación disponible

- `database/migrations/001_initial_schema.sql`: crea `osap_noticias` si no existe y define las tablas iniciales.
- `database/migrations/002_seed_content_types.sql`: carga el catálogo inicial de tipos de contenido.
- `schema_migrations`: registra las migraciones aplicadas.
- `osap.example.toml`: plantilla sin credenciales.

## Compatibilidad y ejecución

La migración 001 está redactada para **MySQL 8.0.16 o posterior**. No se declara todavía compatibilidad validada con MariaDB. Antes de ejecutarla se debe comprobar la versión del servidor y que la cuenta de desarrollo tenga permisos limitados a la base `osap_noticias`.

Las migraciones se aplican en orden y el ejecutor consulta `schema_migrations` antes de cada versión. Las tablas de la primera migración usan `IF NOT EXISTS`; la referencia a publicación principal se valida en la aplicación para evitar una dependencia circular. El catálogo de tipos también usa una inserción idempotente.

No se ha ejecutado ninguna migración ni se ha realizado ninguna escritura en la base de datos.
