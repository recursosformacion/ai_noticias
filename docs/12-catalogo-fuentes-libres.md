# Catálogo de fuentes musicales de libre difusión

**Fecha de comprobación:** 15 de noviembre de 2026.
**Estado:** base `osap_noticias` vaciada y re-sembrada desde la migración `007_free_music_sources.sql`.

Este documento recoge las fuentes registradas tras vaciar los datos de prueba, con el criterio
aplicado, el resultado técnico de cada canal y el estado de su licencia.

## 1. Criterio de selección

Solo se activan (`ACTIVE`) canales cuyo contenido tenga una base clara de reutilización:

- **Dominio público** (obras del Gobierno de EE. UU., fondos sin derechos).
- **Licencias abiertas** explícitas: CC0, CC BY, CC BY-SA, Licence Ouverte (Etalab).
- **Open Access** con licencia CC BY declarada por el editor.

Los canales con RSS localizado pero **sin autorización de reutilización** se registran en `PAUSED`,
para conservar el inventario sin capturarlos. Localizar un RSS no equivale a tener permiso.

## 2. Canales activos (15)

|  id | Canal                                       | Editor                | Idioma | Tipo       | Licencia / base                          | Elementos |
| --: | ------------------------------------------- | --------------------- | ------ | ---------- | ---------------------------------------- | --------: |
|   7 | LOC – NLS Music Notes                       | Library of Congress   | en     | NEWS       | Dominio público US (autoría de personal) |        10 |
|   8 | LOC – Concerts & Performing Arts            | Library of Congress   | en     | EVENT      | Dominio público US                       |        25 |
|   9 | BnF – Actualités                            | BnF                   | fr     | NEWS       | Licence Ouverte 2.0                      |        30 |
|  10 | BnF – Bibliographie nationale / Son         | BnF                   | fr     | BIBLIO     | Licence Ouverte 2.0 (metadatos)          |        26 |
|  11 | BnF – Agenda                                | BnF                   | fr     | EVENT      | Licence Ouverte 2.0                      |       200 |
|  12 | Wikisource ES – Cambios recientes           | Wikimedia             | es     | COLLECTION | CC BY-SA 4.0 / dominio público           |        50 |
|  13 | Wikipedia EN – Artículo _Music_ (historial) | Wikimedia             | en     | OTHER      | CC BY-SA 4.0                             |        10 |
|  14 | Internet Archive – Audio de dominio público | Internet Archive      | en     | COLLECTION | Dominio público / licencias abiertas     |        50 |
|  15 | Open Library Blog                           | Internet Archive      | en     | BIBLIO     | Proyecto abierto (licencia por entrada)  |        10 |
|  16 | MetaBrainz Blog                             | MetaBrainz Foundation | en     | NEWS       | Fundación sin ánimo de lucro; datos CC0  |        10 |
|  17 | RILM – Bibliolore                           | RILM                  | en     | RESEARCH   | Blog académico, licencia de compartición |        10 |
|  18 | DOAJ – Nuevas revistas                      | DOAJ                  | en     | RESEARCH   | Metadatos CC0                            |       100 |
|  19 | PLOS ONE                                    | PLOS                  | en     | RESEARCH   | CC BY 4.0                                |        30 |
|  20 | Frontiers in Psychology                     | Frontiers             | en     | RESEARCH   | CC BY 4.0                                |        20 |
|  21 | NARA – Noticias                             | NARA (EE. UU.)        | en     | NEWS       | Dominio público US                       |        10 |

**Cobertura por idioma (noticias distintas):** en = 274, fr = 233, es = 45.

## 3. Canales registrados pero en pausa (8)

|  id | Canal                                      | Motivo                                                                                                         |
| --: | ------------------------------------------ | -------------------------------------------------------------------------------------------------------------- |
|   1 | LOC – In the Muse                          | Mismo contenido que el blog de LOC; reactivar solo tras verificar autoría por entrada (personal vs. invitado). |
|   6 | BnF – Bibliographie nationale / Partitions | Duplicado del canal 10 (misma base bibliográfica; el _Son_ cubre registros sonoros).                           |
|   3 | Scherzo                                    | El aviso legal exige autorización escrita previa.                                                              |
|   4 | Beckmesser                                 | Todos los derechos reservados; prohíbe almacenamiento permanente.                                              |
|   5 | Bachtrack – News                           | Uso personal/privado; prohíbe otros usos automatizados e IA.                                                   |
|  22 | Musicology Now                             | Sin licencia general de reutilización; pendiente de autorización.                                              |
|  23 | Music Business Worldwide                   | Uso personal no comercial; prohíbe copia y publicación.                                                        |
|  24 | NPR Music                                  | Prohíbe usar sus contenidos para sistemas de IA sin permiso escrito.                                           |

## 4. Candidatos descartados por no tener canal válido

Comprobados el 15-11-2026 con petición HTTP real; **no se registran** porque no existe feed utilizable:

| Fuente                                            | Resultado                                                |
| ------------------------------------------------- | -------------------------------------------------------- |
| UNESCO – Patrimonio Cultural Inmaterial           | Devuelve HTML pese a pedir RSS; API JSON no disponible.  |
| UNESCO – Noticias de cultura                      | HTTP 403 (bloqueo a clientes automatizados).             |
| Europeana (blog y API sin clave)                  | 404 / 401; requiere clave de API.                        |
| Ópera Actual                                      | Devuelve HTML, no RSS válido.                            |
| IMSLP                                             | El feed Atom anunciado redirige a HTML; requiere sesión. |
| Wikinews ES/EN                                    | El feed de cambios recientes llega vacío.                |
| MDPI Arts, Smithsonian Folkways, Open Library API | 403 / 404.                                               |
| OpenEdition Journals, CORE, Zenodo                | 404 en los endpoints RSS indicados.                      |

## 5. Incidencias técnicas corregidas

1. **Certificados TLS.** El almacén de certificados de Windows del equipo está desactualizado y
   rechazaba certificados válidos (Wikipedia, Bibliolore, Internet Archive, MusicBrainz…). Se ha
   añadido `certifi` a `requirements.txt` y el colector (`app/collector.py`) crea el contexto SSL a
   partir de su CA bundle. Antes de este cambio, 8 canales perfectamente operativos fallaban con
   `CERTIFICATE_VERIFY_FAILED`.
2. **Parser Atom genérico.** PLOS ONE publica el resumen en `<content>`, no en `<summary>`: el parser
   solo leía `summary`, `description` y `encoded`, por lo que los 30 elementos se rechazaban por
   «falta una descripción con contenido». Se añadió `content` a la lista de etiquetas
   (`app/feed_parser.py`).
3. **Migración 006.** No registraba su versión en `schema_migrations`; se ha añadido el registro y
   ahora `verify_database.py` la reconoce.

## 6. Resultado de la captura

| Concepto                                 | Valor   |
| ---------------------------------------- | ------- |
| Ejecuciones registradas                  | 46      |
| Noticias distintas (`news_items`)        | **552** |
| Publicaciones (`news_publications`)      | 552     |
| Observaciones (`source_observations`)    | 552     |
| Noticias consolidadas entre fuentes      | 0       |
| Errores de elementos en la última pasada | 0       |

**Duplicados:** la segunda pasada completa devolvió **0 elementos nuevos** en los 15 canales. Cinco
canales respondieron `304 Not Modified`; el resto entregó los mismos ítems y todos se identificaron
como conocidos (`known`/`updated`). La idempotencia se confirma también con el nuevo catálogo.

**Consolidación entre fuentes:** 0 casos. Es lo esperado: la identidad se calcula con SHA-256 de la
descripción normalizada, y fuentes tan distintas (bibliográficas, académicas, patrimoniales) no
repiten descripciones literales. El mecanismo funcionará cuando dos medios reproduzcan el mismo
texto de agencia.

## 7. Herramientas nuevas

| Comando                                 | Uso                                                                               |
| --------------------------------------- | --------------------------------------------------------------------------------- |
| `py -3 -m tools.reset_all_data`         | Simula el vaciado de datos de captura.                                            |
| `py -3 -m tools.reset_all_data --apply` | Vacía datos de captura, editores y canales (conserva esquema, tipos y taxonomía). |
| `py -3 -m tools.dedupe_canales`         | Detecta canales duplicados por URL normalizada.                                   |
| `py -3 -m tools.informe_captura`        | Informe por canal, ejecuciones, idiomas y consolidaciones.                        |
| `py -3 -m tools.errores_captura`        | Muestra ejecuciones fallidas y sus mensajes.                                      |

## 8. Advertencias de uso

- **Volumen y ruido:** BnF – Agenda devuelve 200 entradas de toda la agenda cultural (no solo música)
  y DOAJ, PLOS ONE y Frontiers son corpora académicos generalistas. Requieren filtrado temático
  antes de alimentar cualquier boletín o análisis con IA.
- **Atribución:** CC BY, CC BY-SA y Licence Ouverte exigen citar la fuente, el autor y la fecha de
  recuperación. CC BY-SA obliga a compartir igual cualquier obra derivada.
- **Contenido antiguo:** los feeds bibliográficos (BnF _Son_, Internet Archive, DOAJ) muestran
  registros y volcados, no actualidad diaria.
