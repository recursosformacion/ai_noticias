# Decisiones y cuestiones pendientes

Este documento registra asuntos que requieren investigación o acuerdo. No se consideran decisiones cerradas.

## Alcance acordado de la primera fase

- [x] La primera fase termina con la recopilación, normalización, deduplicación, clasificación y carga verificable de noticias en MySQL/MariaDB.
- [x] La cobertura incluye todos los ámbitos musicales; la clasificación temática se realiza por noticia.
- [x] Preferencias personales, vistas personalizadas, integración con usuarios de OSAP, suscripciones y boletines quedan para fases posteriores.
- [x] No diseñar ni crear tablas de usuarios, preferencias o correo en el esquema inicial.


## Fuentes

- [x] Localizar fuentes oficiales y documentar los primeros endpoints RSS de LOC y BnF (véase [inventario de fuentes](03-inventario-fuentes.md)).
- [ ] Localizar y comprobar las URL actuales de los cinco feeds de la BNE.
- [ ] Ejecutar la matriz de pruebas de ingesta sobre los feeds priorizados y registrar los resultados reales de parser, campos, fechas, idioma y volumen.
- [ ] Validar Google News RSS, la resolución de URL y la identificación del editor original.
- [ ] Localizar los endpoints actuales de la BNE; la existencia histórica de cinco canales no basta para configurarlos.
- [x] Ampliar inventario con Bachtrack, Music Business Worldwide, NPR Music, Scherzo y Beckmesser; sus endpoints están localizados y pendientes de validación de contenido.
- [x] Registrar Ópera Actual como fuente editorial relevante, pero no activar el endpoint candidato porque la comprobación devolvió HTML en lugar de RSS.
- [ ] Resolver autorización para NPR (uso de IA expresamente restringido sin consentimiento escrito) y Music Business Worldwide (uso limitado y restricciones de copia/traducción) antes de activarlas.
- [ ] Revisar las condiciones de uso específicas de cada fuente antes de activarla.
- [ ] Identificar APIs oficiales disponibles para instituciones que no tengan RSS.
- [ ] Definir idiomas y territorios que cubrirá la primera versión.
- [x] Conservar el idioma original detectado y el idioma de cada aparición de la noticia.
- [x] Separar versiones oficiales de la fuente y traducciones generadas por ai_noticias; documentado en [idiomas y traducciones](06-idiomas-y-traducciones.md).
- [x] Preparar el modelo para traducciones editoriales adicionales sin generarlas masivamente antes de conocer las preferencias de idioma.
- [ ] Establecer frecuencia y límites de consulta por fuente.

## Criterios editoriales

- [x] Definir criterios iniciales de inclusión, exclusión y clasificación por tipo de contenido y tema (véase [criterios editoriales](04-criterios-clasificacion.md)); falta validarlos con una muestra real.
- [x] Definir cobertura general y especializada: el recolector abarcará todos los ámbitos musicales y clasificará cada noticia; las preferencias personales quedan para una fase posterior.
- [x] Preparar una primera taxonomía jerárquica de ámbitos generales y especialidades (propuesta en la sección 5 de la propuesta funcional); pendiente validarla con noticias reales.
- [x] Separar el tipo de contenido (noticia, evento, publicación académica, novedad bibliográfica, etc.) del tema musical; criterios en el documento 04.
- [ ] Decidir si las noticias se publican automáticamente o pasan por revisión.
- [ ] Definir el tratamiento de noticias repetidas, actualizaciones y artículos sindicados.
- [ ] Decidir la longitud y el tono del resumen editorial en español.
- [ ] Validar la detección de idioma con feeds multilingües y textos breves.

## Matriz de pruebas y modelo conceptual

- [x] Definir protocolo y matriz de pruebas técnicas, editoriales, de duplicación, idioma, reintentos y persistencia (véase [07-matriz-pruebas-ingesta](07-matriz-pruebas-ingesta.md)); pendiente ejecutar pruebas con parser real.
- [x] Consolidar modelo conceptual separando publisher, canal, ejecución, observación, publicación, noticia consolidada, análisis, textos editoriales y traducciones (véase [08-modelo-conceptual-persistencia](08-modelo-conceptual-persistencia.md)).
- [ ] Revisar y aprobar el modelo conceptual antes de traducirlo a tablas y relaciones SQL.

## IA

- [ ] Comparar Gemini y Groq con un conjunto de noticias reales y una evaluación común.
- [ ] Confirmar límites, condiciones de uso y política de datos de cada nivel gratuito.
- [ ] Definir proveedor principal, alternativa y comportamiento cuando se agoten las cuotas.
- [ ] Versionar los prompts y conservar el modelo utilizado para cada análisis.
- [ ] Decidir umbrales de confianza y casos que requieren revisión humana.

## Base de datos e integración

- [x] Nombre acordado para la base de datos MySQL/MariaDB: `osap_noticias`.\n- [ ] Confirmar versión y configuración objetivo de MySQL/MariaDB.
- [ ] Definir conexión y gestión de credenciales mediante configuración externa, nunca en Git.
- [ ] Acordar retención de registros de captura, errores, análisis y envíos.
- [ ] Definir si el paquete expondrá API propia o será consumido directamente por otro servicio.

## Boletín y correo (fase posterior; no bloquea la primera versión)

- [ ] Decidir periodicidad del boletín y zona horaria.
- [ ] Determinar si habrá una edición única o boletines por preferencias temáticas/idioma.
- [ ] Comparar SMTP del alojamiento con proveedores externos y verificar límites vigentes.
- [ ] Diseñar confirmación de alta, baja, rebotes y prevención de envíos duplicados.
- [ ] Confirmar requisitos legales y de protección de datos aplicables a los destinatarios.

## Operación de la primera fase

- [ ] Elegir cron, programador del sistema o worker persistente.
- [ ] Definir métricas mínimas: fuentes consultadas, elementos nuevos, duplicados, aceptados, descartados, errores y coste/cuota de IA.
- [ ] Establecer política de reintentos y alertas para fuentes que fallen repetidamente.
- [x] Preparar un conjunto de escenarios y una matriz de pruebas con RSS reales y respuestas simuladas de IA.
- [ ] Ejecutar la matriz con muestras reales y guardar evidencias por fuente.

## Decisiones que conviene mantener desde el principio

1. Una noticia no se pierde porque falle la IA.
2. Recolectar, analizar y persistir son procesos independientes y reanudables.
3. Toda noticia conserva la referencia a su fuente original y las apariciones en otras fuentes.
4. Los resúmenes generados no sustituyen ni se confunden con el texto original.
5. La IA es sustituible y sus resultados deben conservar el modelo y las versiones de instrucciones utilizadas.
6. Ninguna cuota gratuita ni endpoint de terceros se considerará estable sin verificación periódica.
