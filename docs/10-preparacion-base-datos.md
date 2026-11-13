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

La versión del servidor de desarrollo comunicada es **MariaDB 10.4.32**. Se ha revisado estáticamente la sintaxis de las dos migraciones para este motor; todavía no se ha comprobado mediante ejecución real.

El script `crear_bbdd_osap_noticias.bat` ejecuta las migraciones en orden con el cliente `mysql` de MariaDB. Solicita usuario y contraseña en la consola, sin escribirlos en el fichero ni pasarlos como texto en la línea de comandos. La cuenta necesita permisos para crear la base `osap_noticias`, tablas e índices. El script se detiene si falla una migración.

La migración 001 crea las tablas con `IF NOT EXISTS`; la referencia a publicación principal se valida en la aplicación para evitar una dependencia circular. El catálogo de tipos usa una inserción idempotente. `schema_migrations` permite comprobar qué versiones se han aplicado.

No se ha ejecutado ninguna migración ni se ha realizado ninguna escritura en la base de datos.
