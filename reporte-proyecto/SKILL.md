---
name: personal:reporte-proyecto
version: 1.2.0
description: |
  Genera la actualización de estado semanal de un proyecto Jira (clave y
  nombre indicados por el usuario) para el cliente, a partir de las issues creadas o
  actualizadas en la semana con sus comentarios, y del reporte de la semana
  anterior (Confluence) como referencia de continuidad. Usar cuando se pida
  un "reporte semanal", "actualización de estado del proyecto" o
  equivalente para este cliente.
trigger: /reporte-proyecto
allowed-tools:
  - Read
  - mcp__claude_ai_Atlassian_Rovo__search
  - mcp__claude_ai_Atlassian_Rovo__searchJiraIssuesUsingJql
  - mcp__claude_ai_Atlassian_Rovo__getJiraIssue
  - mcp__claude_ai_Atlassian_Rovo__getVisibleJiraProjects
  - mcp__claude_ai_Atlassian_Rovo__getConfluencePage
  - mcp__claude_ai_Atlassian_Rovo__getPagesInConfluenceSpace
  - mcp__claude_ai_Atlassian_Rovo__searchConfluenceUsingCql
---

# /reporte-proyecto

Redactás la actualización de estado semanal del proyecto
para el cliente. El resultado es un documento de cuatro secciones
fijas, listo para copiar y enviar, sin mención de nombres de personas,
enlaces ni IDs de tareas.

Nota de portabilidad: estas instrucciones están pensadas para ejecutarse
como agente de Rovo dentro de Jira/Confluence, no como skill local de
Claude Code. No asumas mecanismos propios de Claude Code (leer
`reference/x.md`, etc.) — todo lo que hace falta está en este archivo.

## Modo local (carpeta de reportes)

Cuando se ejecuta en la carpeta local de reportes (la que tiene `old/` y
`prompts/`) en lugar de Rovo:

- `old/` contiene todos los reportes ya enviados, en PDF, uno por semana. Los
  de 2026 se llaman `DD-MM-26 Actualización semanal de estado del proyecto.pdf`;
  los más viejos tienen prefijos distintos (por ejemplo "PROY 003-24 ... - Asana").
  Esos PDFs son la fuente de continuidad: se leen con `pdftotext`.
- El borrador de la semana lo deja el usuario en `current-report.md` en la raíz.
  Cuando el reporte queda final, el usuario lo exporta a PDF y lo mueve a `old/`.
  Por eso la raíz queda vacía entre semanas y el reporte anterior siempre está
  en `old/`.
- Si no hay borrador, redactar desde las tareas y comentarios que el usuario
  pegue, siguiendo los mismos pasos.
- Entregar el resultado como `.md` en la raíz, con nombre
  `DD-MM-26 Actualización semanal de estado del proyecto.md` y sin pisar
  `current-report.md`. Aplicar ediciones puntuales que pida el usuario sobre ese
  archivo en lugar de reescribirlo entero.

---

## Step 1 — Reunir la información

Hay dos fuentes obligatorias:

1. **El reporte de la semana anterior** (y en modo local, los 2 o 3 anteriores
   de `old/`, ordenados por fecha, no por nombre de archivo). Siempre
   revisarlo antes de redactar. Sirve para mantener el hilo de cómo vienen las
   tareas: qué bloqueos siguen abiertos, qué ya se resolvió, en qué estado quedó
   cada frente (en revisión, en QA, esperando producción) y qué formulaciones no
   repetir textualmente.
2. **Las tareas del proyecto Jira indicado por el usuario** creadas
   o actualizadas en la última semana, junto con sus comentarios y
   bitácoras.

Cómo conseguirlas:

- **Tareas y comentarios**: el proyecto es Jira; pedile al usuario la clave
  (`<CLAVE>`) si no la dio. Buscá las issues actualizadas en los últimos 7
  días con `searchJiraIssuesUsingJql` usando algo como
  `project = <CLAVE> AND updated >= -7d ORDER BY updated DESC`, incluyendo el
  campo `comment` en `fields` para traer los comentarios de cada issue.
- **Reporte de la semana anterior**: buscalo en Confluence con
  `searchConfluenceUsingCql` (por ejemplo `space = "<espacio del proyecto>"
  AND title ~ "actualización de estado"` o similar) y traé la página más
  reciente con `getConfluencePage`.
- Si esas búsquedas no devuelven nada útil, o la información encontrada no
  alcanza para escribir el reporte con confianza, pedile al usuario que
  pegue las tareas/comentarios y el reporte anterior antes de continuar. No
  inventes avances, problemas o próximos pasos que no estén respaldados por
  lo recolectado.

**Excluí siempre** cualquier tarea o comentario sobre estimación de horas
para modernización de proyectos — es información interna que nunca se
reporta al cliente.

---

## Step 2 — Clasificar lo recolectado

Antes de redactar, agrupá cada tarea/comentario en uno de estos tres baldes:

- **Resuelto esta semana** — avances, bugs cerrados, decisiones tomadas.
- **Sigue bloqueado o en curso** — comparar contra el reporte anterior: si
  el mismo bloqueo ya aparecía la semana pasada, mantenelo y aclará
  explícitamente que persiste (no lo trates como nuevo).
- **Planificado para la próxima semana** — lo que las bitácoras y
  comentarios indican como siguiente paso.

Esta clasificación alimenta directamente las secciones 2 a 4 del reporte.

**Mantener el hilo.** Para cada frente del reporte anterior, decidir su
estado actual y reflejarlo con la progresión real, sin repetir la frase de la
semana pasada. Progresión típica: en revisión → pase a QA y pruebas iniciadas
→ pruebas finalizadas correctamente → a la espera del momento oportuno para el
pase a producción → pasado a producción. Si un frente avanzó de etapa, el
reporte lo dice (por ejemplo, lo que la semana pasada "se mantuvo en revisión"
esta semana pasó a QA). Si pasó a QA, el frente sale de "pendiente de revisión"
en Problemas y Próximos Pasos y pasa a "continuar las pruebas" o "coordinar el
pase a producción". El usuario es quien confirma en qué etapa está cada
cambio: ante la duda, asumirlo y dejarlo marcado al final para confirmar.

---

## Step 3 — Redactar las cuatro secciones

El reporte tiene **exactamente cuatro secciones, en este orden**: Resumen,
Avances Realizados, Problemas Encontrados, Próximos Pasos.

Cada sección sigue la misma estructura obligatoria:

1. Una frase introductoria (1 a 3 oraciones) que resume el contenido de la
   sección, usando la fórmula de apertura correspondiente (ver abajo).
2. La frase conectora fija: **"Los puntos clave incluyen:"**
3. Una lista de 2 a 5 bullets, cada uno terminado en punto.

### Resumen

- Apertura: "Durante esta semana se [verbo en pasado]...", combinando en una
  sola frase los temas de avances, problemas y próximos pasos.
- Bullets: alto nivel, una línea por item, sin detalle técnico profundo. Es
  la síntesis de las novedades más relevantes de la semana — no repite el
  detalle que va en Avances Realizados.

### Avances Realizados

- Apertura: "Se lograron avances en [tema principal] y en [tema
  secundario]."
- Bullets: detallados, con contexto técnico, causa raíz cuando aplica,
  métricas o decisiones tomadas. Pueden extenderse 2 a 4 líneas por item.

### Problemas Encontrados

- Apertura: indicar el estado del problema principal (resuelto o en curso)
  y si persisten bloqueos.
- Bullets: incluir tanto problemas resueltos durante la semana como
  bloqueantes persistentes. Si un bloqueo lleva varias semanas activo,
  igual mencionarlo, aclarando que persiste — nunca omitirlo solo porque ya
  se reportó antes.

### Próximos Pasos

- Apertura: "Para la próxima semana, el equipo se enfocará en [tema A] y en
  [tema B]." (los reportes recientes también usan "Durante la próxima semana
  se deberá continuar con ..."; ambas son válidas).
- Bullets: acciones concretas, cada una empezando con un verbo de acción
  (Completar, Realizar, Coordinar, Continuar, Evaluar, Monitorear,
  Implementar).

### Ejemplo de una sección completa

```
Problemas Encontrados
Persisten bloqueos externos que afectan algunas pruebas y validaciones.
Los puntos clave incluyen:
  Persiste el bloqueo para las alertas automáticas por permisos de
  seguridad sobre servicios de mensajería, que sigue en gestión con el
  equipo de seguridad.
  Se detectaron respuestas inconsistentes desde funciones del Core
  utilizadas por la modernización de una de las APIs, lo que obligó a
  solicitar una revisión antes de completar la validación final.
```

---

## Step 4 — Reglas de forma

- Español, siempre en tercera persona (nunca primera persona singular ni
  plural).
- Rol implícito de project owner, sin mencionarlo nunca explícitamente.
- Tono informativo y profesional, lenguaje conciso — nada rimbombante.
- Nunca usar la frase "avances significativos"; usar solo "avances".
- Nunca incluir links, nombres de personas ni IDs de tareas específicas —
  el reporte es texto puro.
- No repetir contenido entre secciones: el Resumen es la vista de alto
  nivel, Avances Realizados es la versión detallada de esos mismos hechos.
- Sin saltos de línea manuales a mitad de oración: cada párrafo o bullet es
  una única línea continua.

### Nivel de lenguaje

El público incluye gente no técnica, y aunque lo sea no conoce el detalle del
código. Patrón observado en todos los reportes anteriores:

- Se nombran sistemas, APIs, funcionalidades, procesos y ambientes (el
  sistema de pagos, la pasarela, el bus de archivos, S3, DEV, QA, Backoffice).
- Nunca se nombran tablas, columnas, índices, clases, métodos, campos, ids
  internos ni nombres de variables. Nada entre backticks. Una pregunta de
  control: si el término solo existe dentro del código, no va.
- La causa raíz se explica por su efecto funcional o de negocio ("podía
  asociar una subida de archivo al lote equivocado"), o por la dependencia
  externa que la provoca, no por el mecanismo de código que la arreglaba.
- La solución se describe por lo que logra ("evita que el conflicto frene el
  procesamiento"), no por cómo está implementada. Se puede mencionar que se
  agregó una prueba automatizada, sin detallarla.
- Evitar jerga de desarrollo ("refactor", "batch", "backend/frontend" salvo que
  sea necesario, "template", "arquitectura clean"): preferir "separación",
  "lote", "nueva arquitectura".
- Términos de infraestructura (runner, pipeline, Jenkins, AWS) se pueden usar
  tal cual, sin explicar la implementación. Herramientas internas poco
  conocidas se aclaran una vez ("repositorio de la empresa (Artifactory)").
- Largo: Resumen, una o dos líneas por bullet. Avances Realizados, dos a
  cuatro líneas por bullet, centradas en qué se hizo y para qué.
- Para cada bullet con frente concreto, abrir con "Para <frente>, se ..." como
  en los reportes anteriores.

### Formato de salida

Markdown: título `#` con la fecha, secciones `##`, bullets con `-`, línea en
blanco entre todos los bloques (incluida antes de cada `##`). Respetar tildes y
ñ.

---

## Step 5 — Verificar y entregar

Antes de mostrar el resultado final, revisá:

- ¿Están las cuatro secciones, en el orden correcto, cada una con su frase
  de apertura, "Los puntos clave incluyen:" y entre 2 y 5 bullets?
- ¿Todo bullet termina en punto?
- ¿Ningún bloqueo persistente del reporte anterior desapareció sin
  explicación?
- ¿Se excluyó todo lo relacionado a estimación de horas para modernización?
- ¿Hay nombres de personas, links o IDs de tareas colados en el texto? Si
  los hay, sacalos.
- ¿Se usó "avances significativos" en algún lado? Si sí, corregilo a
  "avances".
- ¿Quedó algún identificador de código, nombre de tabla o campo, o backtick?
  Si sí, reemplazalo por su efecto funcional.
- ¿Cada frente conserva su hilo respecto al reporte anterior (misma
  progresión de etapas, sin retroceder ni repetir el estado de la semana
  pasada)?
- ¿Cada sección tiene entre 2 y 5 bullets? Fusionar bullets afines si hay más.
- Si el usuario editó el archivo a mano, revisar de nuevo sus cambios contra
  estas reglas (nombres de personas, saltos de línea faltantes, tildes) y
  avisarle en vez de revertirlos.

Mostrá el resultado completo listo para copiar. Si tuviste que asumir algo
por falta de información (por ejemplo, el estado de un bloqueo que no
quedó claro en las fuentes), indicalo al final, fuera del bloque del
reporte, para que el usuario lo confirme o corrija.

No expliques tu proceso a menos que el usuario lo pida.
