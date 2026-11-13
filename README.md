# ai_noticias

Paquete independiente para recopilar, clasificar y almacenar en MySQL/MariaDB noticias de todos los ámbitos musicales, tanto generales como especializados. Los boletines y las funciones para usuarios quedan para una fase posterior.

## Estado

**Fase actual: diseño de la recopilación, clasificación y carga en MySQL/MariaDB.**

El objetivo de esta primera fase es terminar con las noticias recopiladas, normalizadas, deduplicadas, clasificadas y cargadas correctamente en MySQL/MariaDB. Las preferencias personales, las vistas personalizadas, la integración con OSAP y los boletines por correo quedan fuera de esta fase. Este repositorio recoge ideas, fuentes potenciales, decisiones de arquitectura y cuestiones pendientes; todavía no contiene una aplicación funcional ni debe interpretarse como una especificación cerrada.

## Objetivo

Construir un recolector que:

1. Consulte periódicamente fuentes RSS y APIs públicas.
2. Detecte novedades y evite registrar repetidamente la misma noticia.
3. Clasifique las entradas según su interés musical mediante reglas y un proveedor de IA intercambiable.
4. Genere resúmenes divulgativos en español cuando proceda.
5. Guarde las noticias, su procedencia y el resultado del análisis en MySQL/MariaDB.
6. Permita preparar y enviar boletines a usuarios que hayan solicitado expresamente recibirlos.

## Documentación

- [Propuesta funcional y arquitectura inicial](docs/01-propuesta-funcional.md)
- [Decisiones y cuestiones pendientes](docs/02-decisiones-pendientes.md)
- [Inventario inicial de fuentes y canales](docs/03-inventario-fuentes.md)

## Principios iniciales

- Priorizar RSS y APIs oficiales frente al scraping de páginas.
- Conservar la URL y los metadatos de la fuente original.
- No confundir el texto original con el resumen generado por IA.
- No publicar ni redistribuir artículos completos protegidos por derechos de autor.
- Mantener separados recolección, clasificación, almacenamiento y envío.
- Diseñar el proveedor de IA y el servicio de correo como componentes sustituibles.
- No enviar correos sin consentimiento explícito y mecanismo de baja.
- No incorporar credenciales, claves API ni datos personales al repositorio.

## Tecnologías propuestas (no definitivas)

- Python.
- feedparser para feeds RSS/Atom.
- MySQL/MariaDB para persistencia.
- API de IA con adaptador intercambiable (por ejemplo, Gemini o Groq).
- SMTP para el envío, sujeto a elección y validación del proveedor.

Las decisiones definitivas se documentarán antes de iniciar la implementación.
