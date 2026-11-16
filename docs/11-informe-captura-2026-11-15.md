# Informe de captura — 15-11-2026

## 1. Resumen

| Concepto                               | 13-11-2026 (captura anterior) | 15-11-2026 (captura nueva) |
| -------------------------------------- | ----------------------------- | -------------------------- |
| Ejecuciones registradas (`fetch_runs`) | 1                             | 2                          |
| Canales consultados                    | 1                             | 1                          |
| Elementos recibidos del feed           | 12                            | 12                         |
| Elementos nuevos                       | 3                             | **0**                      |
| Elementos ya conocidos                 | 9                             | 12                         |
| Errores                                | 0                             | 0                          |
| Noticias distintas (`news_items`)      | 3                             | **3**                      |
| Publicaciones (`news_publications`)    | 3                             | **3**                      |
| Observaciones (`source_observations`)  | 3                             | **3**                      |

**Conclusión sobre duplicados:** la nueva petición **no ha duplicado nada**. Tras la ejecución
`run_id = 5`, los tres totales permanecen iguales (3 / 3 / 3). El canal devolvió los mismos 12
elementos del feed y los 12 se han reconocido como conocidos: la identidad de cada noticia se
calcula con SHA-256 de la descripción normalizada, por lo que un mismo ítem no genera una nueva
observación ni una nueva publicación. Lo único que se actualizó es `last_seen_at` / `last_detected_at`.

## 2. Ejecuciones

| run_id | Fecha                   | Canal            | HTTP | Resultado | Recibidos | Nuevos | Conocidos | Errores |
| ------ | ----------------------- | ---------------- | ---- | --------- | --------- | ------ | --------- | ------- |
| 4      | 13-11-2026 19:42:35 UTC | BnF – Partitions | 200  | SUCCESS   | 12        | 3      | 9         | 0       |
| 5      | 15-11-2026 08:25:16 UTC | BnF – Partitions | 200  | SUCCESS   | 12        | 0      | 12        | 0       |

Diferencia en el recuento: la ejecución 4 decía 9 «conocidos» por los 9 elementos del feed ya
existentes en la base de datos de pruebas previas; la 5 reconoce los 12 porque los 3 nuevos de
la primera captura ya forman parte del corpus.

## 3. Noticias almacenadas

Las tres noticias corresponden al canal **BnF – Bibliographie nationale, série Partitions** y están
en francés (`declared_language = fr`, `language_declared` por publicación sin rellenar).

| news_item | Título                                                                                                        | Publicada  | Idiomas / estado |
| --------- | ------------------------------------------------------------------------------------------------------------- | ---------- | ---------------- |
| 13        | Le numéro Partitions 03/2019 est paru (491 Notices)                                                           | 2020-02-20 | fr (canal)       |
| 14        | Suspension des activités de dépôt légal et de la parution des numéros de la Bibliographie nationale française | 2020-05-04 | fr (canal)       |
| 15        | Le numéro Partitions 01/2019 est paru (338 Notices)                                                           | 2019-06-17 | fr (canal)       |

Cada noticia tiene 1 publicación y 1 editor, lo que confirma que no hay consolidaciones cruzadas
entre fuentes en esta muestra (solo hay una fuente activa). No hay clasificación con IA aplicada
todavía: la fase `analyze` sigue pendiente y el CLI la invoca sin cliente LLM.

Observación editorial: el contenido disponible es antiguo (2019-2020) porque el feed de la BnF
sobre «Partitions» publica volcados de números atrasados, no actualidad diaria. Conviene tenerlo en
cuenta al valorar la utilidad del canal como fuente de noticias.

## 4. Fuentes utilizadas

Canales registrados (6), según `source_channels`:

| id  | Editor                           | Canal                                | Idioma | Estado     | Última consulta      |
| --- | -------------------------------- | ------------------------------------ | ------ | ---------- | -------------------- |
| 1   | Library of Congress              | In the Muse                          | en     | PAUSED     | —                    |
| 2   | Musicology Now                   | Musicology Now                       | en     | PAUSED     | —                    |
| 3   | Scherzo                          | Scherzo                              | es     | PAUSED     | —                    |
| 4   | Beckmesser                       | Beckmesser                           | es     | PAUSED     | —                    |
| 5   | Bachtrack                        | Bachtrack – News                     | en     | PAUSED     | —                    |
| 6   | Bibliothèque nationale de France | Bibliographie nationale – Partitions | fr     | **ACTIVE** | 15-11-2026 08:25 UTC |

**Solo un canal está en estado ACTIVE**, por lo que es la única fuente de la que proceden las
noticias descargadas. Los cinco restantes siguen en `PAUSED` a la espera de revisar sus condiciones
de uso (`activate --confirm-terms-reviewed`).

## 5. Incidencias y cambios técnicos

- Al ejecutar el informe se detectó que `osap.toml` no era TOML válido: `GROQ_API` y `GEMINI_API`
  estaban sin comillas y fuera de la sección `[db]`, lo que bloqueaba cualquier conexión
  (`TOMLDecodeError`). Se han comentado; las claves de IA deben ir como variables de entorno, no en
  el archivo de configuración.
- Se añadió `tools/informe_dia.py` para obtener este informe de forma reproducible:
  `py -3 -m tools.informe_dia --days 5`.

## 6. Recomendaciones

1. **Ampliar la muestra**: con una sola fuente activa el estudio de duplicados es trivial. Activar
   al menos un canal adicional (p. ej. Bachtrack) permitiría comprobar la deduplicación entre
   fuentes distintas, que es el caso de uso real.
2. **Renovar el contenido**: el feed de la BnF devuelve números de 2019-2020; si se busca
   actualidad musical, este canal no la aporta.
3. **Revisar credenciales**: trasladar las claves de IA a variables de entorno antes de poner en
   marcha la clasificación (`analyze`).
