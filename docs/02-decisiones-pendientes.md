# Decisiones y cuestiones pendientes

Este documento registra asuntos que requieren investigación o acuerdo. No se consideran decisiones cerradas.

## Fuentes

- [x] Localizar fuentes oficiales y documentar los primeros endpoints RSS de LOC y BnF (véase [inventario de fuentes](03-inventario-fuentes.md)).
- [ ] Localizar y comprobar las URL actuales de los cinco feeds de la BNE.
- [ ] Comprobar técnicamente la respuesta, campos, fechas y volumen de los feeds identificados de LOC y BnF.
- [ ] Validar las consultas de Google News RSS y la extracción de la URL del medio original.
- [ ] Investigar feeds propios de revistas, universidades y centros de musicología.
- [ ] Revisar las condiciones de uso específicas de cada fuente antes de activarla.
- [ ] Identificar APIs oficiales disponibles para instituciones que no tengan RSS.
- [ ] Definir idiomas y territorios que cubrirá la primera versión.
- [ ] Establecer frecuencia y límites de consulta por fuente.

## Criterios editoriales

- [ ] Precisar qué significa «noticia musical» para este proyecto.
- [x] Definir cobertura general y especializada: el recolector abarcará todos los ámbitos musicales; cada usuario elegirá los temas que desea seguir.
- [ ] Diseñar una taxonomía de ámbitos generales y especialidades, con categorías jerárquicas y ejemplos positivos/negativos.
- [ ] Definir cómo podrá el usuario seleccionar temas: ámbitos completos, categorías concretas y posibles exclusiones.
- [ ] Decidir si las preferencias se aplican solo al boletín o también a una futura vista personal de noticias.
- [ ] Decidir si las noticias se publican automáticamente o pasan por revisión.
- [ ] Definir el tratamiento de noticias repetidas, actualizaciones y artículos sindicados.
- [ ] Decidir la longitud y el tono del resumen en español.

## IA

- [ ] Comparar Gemini y Groq con un conjunto de noticias reales y una evaluación común.
- [ ] Confirmar límites, condiciones de uso y política de datos de cada nivel gratuito.
- [ ] Definir proveedor principal, alternativa y comportamiento cuando se agoten las cuotas.
- [ ] Versionar los prompts y conservar el modelo utilizado para cada análisis.
- [ ] Decidir umbrales de confianza y casos que requieren revisión humana.

## Base de datos e integración

- [ ] Confirmar versión y configuración objetivo de MySQL/MariaDB.
- [ ] Definir conexión y gestión de credenciales mediante configuración externa, nunca en Git.
- [ ] Determinar cómo se vincularán las preferencias temáticas y las suscripciones con los usuarios de OSAP.
- [ ] Definir el modelo de persistencia para preferencias de usuario sin duplicar el corpus común de noticias.
- [ ] Acordar retención de registros de captura, errores, análisis y envíos.
- [ ] Definir si el paquete expondrá API propia o será consumido directamente por otro servicio.

## Boletín y correo

- [ ] Decidir periodicidad del boletín y zona horaria.
- [ ] Determinar si habrá una edición única o boletines por preferencias temáticas/idioma.
- [ ] Comparar SMTP del alojamiento con proveedores externos y verificar límites vigentes.
- [ ] Diseñar confirmación de alta, baja, rebotes y prevención de envíos duplicados.
- [ ] Confirmar requisitos legales y de protección de datos aplicables a los destinatarios.

## Operación

- [ ] Elegir cron, programador del sistema o worker persistente.
- [ ] Definir métricas mínimas: fuentes consultadas, elementos nuevos, duplicados, aceptados, descartados, errores y coste/cuota de IA.
- [ ] Establecer política de reintentos y alertas para fuentes que fallen repetidamente.
- [ ] Preparar un conjunto de pruebas con RSS reales y respuestas simuladas de IA y SMTP.

## Decisiones que conviene mantener desde el principio

1. Una noticia no se pierde porque falle la IA o el correo.
2. Recolectar, analizar y enviar son procesos independientes.
3. Toda noticia conserva la referencia a su fuente original.
4. Los resúmenes generados no sustituyen ni se confunden con el texto original.
5. La IA y el proveedor de correo son sustituibles.
6. La suscripción al boletín requiere consentimiento explícito.
7. Ninguna cuota gratuita ni endpoint de terceros se considerará estable sin verificación periódica.
