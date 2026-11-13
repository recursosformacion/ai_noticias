# ai_noticias

Paquete independiente para recopilar, clasificar y almacenar en MySQL/MariaDB noticias de todos los ámbitos musicales, tanto generales como especializados. Los boletines y las funciones para usuarios quedan para una fase posterior.

## Estado

**Fase actual: primera implementación del recolector RSS/Atom y persistencia.**

La base `osap_noticias` ya está creada y verificada en el entorno local MariaDB 10.4.32. El repositorio contiene ahora un parser RSS/Atom, captura HTTP condicional (ETag/Last-Modified), registro de ejecuciones, persistencia transaccional e idempotente de observaciones/publicaciones y registro inicial de seis canales candidatos. Los canales se cargan en estado `PAUSED` hasta revisar sus condiciones de uso. La clasificación con IA será una fase posterior de esta primera entrega; usuarios, preferencias y boletines siguen fuera de alcance.

## Objetivo

Construir un recolector que:

1. Consulte periódicamente fuentes RSS y APIs públicas.
2. Detecte novedades y evite registrar repetidamente la misma noticia.
3. Clasifique las entradas según su interés musical e identifique su idioma original mediante reglas y un proveedor de IA intercambiable.
4. Genere resúmenes divulgativos en español y deje preparado el almacenamiento de traducciones adicionales.
5. Guarde las noticias, su procedencia y el resultado del análisis en MySQL/MariaDB.
6. Deje preparada una base documental reutilizable para fases posteriores, sin implementar todavía funciones de usuario ni boletines.

## Documentación

- [Propuesta funcional y arquitectura inicial](docs/01-propuesta-funcional.md)
- [Decisiones y cuestiones pendientes](docs/02-decisiones-pendientes.md)
- [Inventario inicial de fuentes y canales](docs/03-inventario-fuentes.md)
- [Criterios editoriales y de clasificación](docs/04-criterios-clasificacion.md)
- [Flujo de ingesta, estados y deduplicación](docs/05-flujo-ingesta-y-estados.md)
- [Idioma original, traducciones y presentación multilingüe](docs/06-idiomas-y-traducciones.md)
- [Matriz de pruebas de ingesta](docs/07-matriz-pruebas-ingesta.md)
- [Modelo conceptual de persistencia](docs/08-modelo-conceptual-persistencia.md)
- [Diseño físico propuesto para MySQL/MariaDB](docs/09-diseno-fisico-mysql.md)
- [Preparación de la base de datos y configuración](docs/10-preparacion-base-datos.md)

Para verificar la instalación local de MariaDB, ejecutar `verificar_bbdd_osap_noticias.bat`. Tras actualizar el repositorio, aplicar las nuevas migraciones con `crear_bbdd_osap_noticias.bat`. Los scripts de base de datos leen la configuración local de `osap.toml`, que no se versiona.

## Principios iniciales

- Priorizar RSS y APIs oficiales frente al scraping de páginas.
- Conservar la URL y los metadatos de la fuente original.
- Conservar el idioma y el texto original, separados del resumen editorial y de sus traducciones.
- No publicar ni redistribuir artículos completos protegidos por derechos de autor.
- Mantener separados recolección, clasificación y almacenamiento.
- Diseñar el proveedor de IA como componente sustituible.
- Reservar preferencias personales, integración con OSAP y boletines para fases posteriores.
- No incorporar credenciales, claves API ni datos personales al repositorio.

## Tecnologías propuestas (no definitivas)

- Python.
- Parser RSS/Atom basado inicialmente en la biblioteca estándar de Python.
- MySQL/MariaDB para persistencia; nombre acordado de la base de datos: `osap_noticias`.
- API de IA con adaptador intercambiable (por ejemplo, Gemini o Groq).


Las migraciones `001` a `003` están en `database/migrations/`. Se aplican desde `crear_bbdd_osap_noticias.bat`, leyendo la configuración local `osap.toml`. Para listar fuentes: ejecutar `ver_fuentes.bat` o `py -3 -m app.cli sources`. Para activar un canal tras revisar sus condiciones: `py -3 -m app.cli activate --source-id ID --confirm-terms-reviewed`. Para capturar canales activos: `py -3 -m app.cli ingest` o `capturar_noticias.bat`. Las dependencias están en `requirements.txt`; las pruebas unitarias se ejecutan con `py -3 -m unittest discover -s tests -v`.


### Sondeo técnico previo (sin persistencia)

Antes de activar una fuente se puede comprobar la estructura del feed de los dos candidatos autorizados para esta prueba:

```powershell
py -3 -m app.cli probe
```

En Windows también se puede iniciar con `probar_fuentes.bat`.

El comando solo consulta LOC – In the Muse y BnF – Partitions, muestra el número de elementos y la disponibilidad de campos (URL, autor, fecha e identificador), y **no guarda noticias ni crea ejecuciones en la base de datos**. Admite `--source-id ID` para limitar la consulta a uno de esos canales. No es un mecanismo para probar fuentes con permisos pendientes.
