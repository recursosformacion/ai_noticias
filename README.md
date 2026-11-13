# ai_noticias

Paquete independiente para recopilar, clasificar y almacenar en MySQL/MariaDB noticias de todos los ámbitos musicales, tanto generales como especializados. Los boletines y las funciones para usuarios quedan para una fase posterior.

## Estado

**Fase actual: diseño de la recopilación, clasificación y carga en MySQL/MariaDB.**

El objetivo de esta primera fase es terminar con las noticias recopiladas, normalizadas, deduplicadas, clasificadas y cargadas correctamente en MySQL/MariaDB. Las preferencias personales, las vistas personalizadas, la integración con OSAP y los boletines por correo quedan fuera de esta fase. Este repositorio recoge ideas, fuentes potenciales, decisiones de arquitectura y cuestiones pendientes; todavía no contiene una aplicación funcional ni debe interpretarse como una especificación cerrada.

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
- feedparser para feeds RSS/Atom.
- MySQL/MariaDB para persistencia; nombre acordado de la base de datos: `osap_noticias`.
- API de IA con adaptador intercambiable (por ejemplo, Gemini o Groq).


Las migraciones iniciales están preparadas como borrador en `database/migrations/`. No se ejecutarán hasta verificar la versión y los permisos del servidor y aprobar la conexión de la cuenta específica de ai_noticias.
