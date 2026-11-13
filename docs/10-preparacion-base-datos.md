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

El script `crear_bbdd_osap_noticias.bat` ejecuta `tools/migrate.py`, que lee host, puerto, base, usuario y contraseña de `osap.toml` (la contraseña también puede venir de `OSAP_DB_PASSWORD`). No solicita credenciales por consola ni las imprime. Para conectar usa un fichero temporal de opciones que elimina al terminar. La cuenta necesita permisos para crear la base `osap_noticias`, tablas e índices. El script se detiene si falla una migración.

Para comprobar una instalación ya creada, ejecutar `verificar_bbdd_osap_noticias.bat`. Este llama a `tools/verify_database.py` y comprueba las 17 tablas, las dos migraciones registradas y los diez tipos de contenido. No modifica datos.

La migración 001 crea las tablas con `IF NOT EXISTS`; la referencia a publicación principal se valida en la aplicación para evitar una dependencia circular. El catálogo de tipos usa una inserción idempotente. `schema_migrations` permite comprobar qué versiones se han aplicado.

El usuario ha confirmado que la base de datos ya está creada en su entorno local. La verificación de tablas, claves foráneas y catálogo semilla queda pendiente de ejecutar desde ese equipo mediante `verificar_bbdd_osap_noticias.bat`.
