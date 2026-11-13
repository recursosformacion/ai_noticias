# Decisiones y cuestiones pendientes

Este documento registra asuntos que requieren investigación o acuerdo. No se consideran decisiones cerradas.

## Fuentes

- [ ] Confirmar la URL y el formato real de cada feed de Google News que se vaya a utilizar.
- [ ] Verificar si BNE, Gallica y Library of Congress ofrecen feeds oficiales adecuados para novedades musicales.
- [ ] Identificar APIs oficiales disponibles para las instituciones que no tengan RSS.
- [ ] Localizar feeds de revistas, universidades y centros de musicología de acceso abierto.
- [ ] Definir idiomas y territorios que cubrirá la primera versión.
- [ ] Establecer frecuencia y límites de consulta por fuente.

## Criterios editoriales

- [ ] Precisar qué significa «noticia musical» para este proyecto.
- [ ] Decidir si el alcance inicial se limita a música clásica, coral, musicología y patrimonio o incluye también otros ámbitos musicales.
- [ ] Definir categorías y ejemplos positivos/negativos para evaluar la clasificación.
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
- [ ] Determinar cómo se vincularán las suscripciones con los usuarios de OSAP.
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
