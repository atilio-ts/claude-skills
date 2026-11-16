---
name: personal:reporte-proyecto
version: 1.5.0
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
  - Bash
  - Write
  - Edit
  - mcp__claude_ai_Atlassian_Rovo__search
  - mcp__claude_ai_Atlassian_Rovo__searchJiraIssuesUsingJql
  - mcp__claude_ai_Atlassian_Rovo__getJiraIssue
  - mcp__claude_ai_Atlassian_Rovo__getVisibleJiraProjects
  - mcp__claude_ai_Atlassian_Rovo__getAccessibleAtlassianResources
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

- `old/` contiene todos los reportes ya enviados, en PDF, uno por semana,
  llamados `AAAA-MM-DD Actualización semanal de estado del proyecto.pdf`, así
  que ordenarlos por nombre ya los ordena por fecha. Puede haber subcarpetas con
  reportes de otras herramientas más viejos. Esos PDFs son la fuente de
  continuidad: se leen con `pdftotext`.
- El borrador de la semana lo deja el usuario en `current-report.md` en la raíz.
  Cuando el reporte queda final, el usuario lo exporta a PDF y lo mueve a `old/`.
  Por eso la raíz queda vacía entre semanas y el reporte anterior siempre está
  en `old/`.
- Si no hay borrador, redactar desde las tareas y comentarios que el usuario
  pegue, siguiendo los mismos pasos.
- Dónde escribir el resultado:
  - si el usuario nombra un archivo, usar ese;
  - si `current-report.md` no existe o está vacío, escribir ahí;
  - si `current-report.md` tiene un borrador, no pisarlo y crear
    `AAAA-MM-DD Actualización semanal de estado del proyecto.md` en la raíz.
- Aplicar las correcciones que pida el usuario con ediciones puntuales, sin
  reescribir el archivo entero. Si pide cambiar un punto, cambiar solo ese punto
  y no retocar el resto.
- Si el usuario pega una versión editada por él, esa pasa a ser la versión
  vigente: partir de ella para los cambios siguientes y no reintroducir lo que
  sacó.

---

## Step 0 — Datos del proyecto

Esta skill no contiene datos de ningún cliente. Antes de buscar nada, obtené:

- `<PROYECTO>`: clave del proyecto Jira.
- `<CLOUD_ID>`: id del sitio Atlassian.
- `<PREFIJO_SESIONES>`: prefijo de las carpetas de sesiones de Claude Code del
  cliente en `~/.claude/projects/`. Solo en modo local.

Orden de resolución:

1. **Memoria del usuario.** Buscá una nota sobre el alcance del reporte de
   proyecto que tenga esos valores. Si existe, usala sin preguntar. Si el
   entorno no tiene memoria (por ejemplo Rovo), pasá al punto 2.
2. **Resolverlos con Atlassian**, sin pedir lo que se pueda deducir:
   - `<CLOUD_ID>`: llamá a `getAccessibleAtlassianResources`. Si devuelve un solo
     sitio, usá su `id`. Si devuelve varios, preguntá cuál.
   - `<PROYECTO>`: llamá a `getVisibleJiraProjects` con ese `cloudId`. Si el
     usuario dio un nombre o una clave, buscala en el resultado. Si no dio nada o
     hay más de una coincidencia, mostrá la lista corta (clave y nombre) y
     preguntá cuál.
3. **`<PREFIJO_SESIONES>`** (solo modo local): listá `~/.claude/projects/` y
   proponé las carpetas que coincidan con el nombre del cliente o del proyecto;
   si hay dudas, preguntá el prefijo. Es el nombre de carpeta codificado, por
   ejemplo `-Users-<usuario>-Projects-<cliente>`.

Pedí los valores faltantes una sola vez, todos juntos. Cuando los tengas,
ofrecé guardarlos en la memoria del usuario para no volver a preguntarlos. Si
acepta, guardalos solo ahí: nunca en esta skill, en el README ni en ningún
archivo del repositorio. Si la memoria ya tenía valores y el usuario da otros,
preguntá si reemplazar los guardados.

---

## Step 1 — Reunir la información

Hay dos fuentes obligatorias:

1. **El reporte de la semana anterior** (y en modo local, los 2 o 3 más
   recientes de `old/`). Siempre revisarlo antes de redactar. Sirve para
   mantener el hilo de cómo vienen las tareas: qué bloqueos siguen abiertos, qué
   ya se resolvió, en qué estado quedó cada frente (en revisión, en QA,
   esperando producción) y qué formulaciones no repetir textualmente. También
   marca el alcance: ver "Qué entra en el reporte" más abajo.
2. **Las tareas del proyecto Jira indicado por el usuario** creadas
   o actualizadas en la última semana, junto con sus comentarios y
   bitácoras.

Cómo conseguirlas:

- **Tareas y comentarios**: con `<PROYECTO>` y `<CLOUD_ID>` del Step 0, buscá
  las issues actualizadas desde la fecha del reporte anterior con
  `searchJiraIssuesUsingJql`:
  `project = <PROYECTO> AND updated >= "AAAA-MM-DD" ORDER BY updated DESC`,
  pidiendo solo `summary`, `status` y `updated`. Después traé los comentarios de
  cada issue con `getJiraIssue` (`fields: ["summary","status","comment","updated"]`).
  No pedir `comment` ni `description` en la búsqueda JQL: con muchas issues la
  llamada se cuelga y falla por timeout a los 300 s. Para el estado general,
  listar también las abiertas con `project = <PROYECTO> AND statusCategory != Done`.
  Las issues de QA son las que empiezan con "QA -"; si no tienen comentarios
  nuevos en la semana, preguntar al usuario si hubo novedades en lugar de
  repetir el estado anterior.
- **Conversaciones de la semana (modo local)**: revisar las sesiones de Claude
  Code en `~/.claude/projects/` cuyas carpetas empiecen con `<PREFIJO_SESIONES>`
  (Step 0), excluyendo `Projects-Personal`.
  Leer solo los mensajes del usuario con un script (no volcar las sesiones
  enteras) y descartar lo que es herramientas de desarrollo, plugins, skills y
  configuración personal: no es contenido del reporte. Filtrar por la fecha de
  cada mensaje, no por la fecha de modificación del archivo (muchas sesiones se
  modifican a la vez). Lo trabajado el mismo día del reporte anterior suele
  estar cubierto por él.
- **Reporte de la semana anterior**: buscalo en Confluence con
  `searchConfluenceUsingCql` (por ejemplo `space = "<espacio del proyecto>"
  AND title ~ "actualización de estado"` o similar) y traé la página más
  reciente con `getConfluencePage`.
- Si esas búsquedas no devuelven nada útil, o la información encontrada no
  alcanza para escribir el reporte con confianza, pedile al usuario que
  pegue las tareas/comentarios y el reporte anterior antes de continuar. No
  inventes avances, problemas o próximos pasos que no estén respaldados por
  lo recolectado.

**Excluí siempre** cualquier tarea o comentario sobre estimación de horas o
presupuestos de trabajo futuro — es información interna que nunca se
reporta al cliente.

### Qué entra en el reporte

- Entran los frentes que ya venían en el reporte anterior y los frentes nuevos
  con trabajo real en la semana (por ejemplo, un incidente en producción).
- Una tarea de Jira que solo cambió de estado, sin comentarios ni trabajo en las
  conversaciones de la semana, y que no figura en el reporte anterior, no entra.
  Omitirla sin preguntar.
- Un estado esperado no es un problema: un servicio que todavía no acepta
  procesamientos, o que espera una ventana de despliegue, no se reporta como
  caído ni como bloqueo.
- Los cambios menores de pantalla (íconos, filtros, textos) no se reportan por
  separado: o se omiten o se mencionan dentro del frente al que pertenecen.

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

**Nombrar la etapa exacta.** Cada frente dice qué terminó y qué falta, sin
palabras que suenen a más avance del real. "Se completó la validación" se lee
como listo para producción; si lo que terminó es el código, escribir "se
completó la implementación de la consulta de validación de cuentas, que queda
pendiente de revisión y de pruebas en los ambientes". Si la implementación está
terminada pero no se probó, decir "la implementación quedó terminada y resta su
validación y pruebas en el entorno local".

**Dudas al usuario.** Si hay varias dudas antes de redactar (estado de una
tarea, si algo es un bloqueo, si un tema entra), preguntarlas juntas en una
lista numerada, para que el usuario conteste por número.

---

## Step 3 — Redactar las cuatro secciones

El reporte tiene **exactamente cuatro secciones, en este orden**: Resumen,
Avances Realizados, Problemas Encontrados, Próximos Pasos.

Cada sección sigue la misma estructura obligatoria:

1. Una frase introductoria (1 a 3 oraciones) que resume el contenido de la
   sección, usando la fórmula de apertura correspondiente (ver abajo).
2. La frase conectora fija: **"Los puntos clave incluyen:"**
3. Una lista de 2 a 5 bullets, cada uno terminado en punto. Excepción:
   Problemas Encontrados puede tener un solo bullet cuando lo único vigente es
   un bloqueo que persiste.

El título del documento es `# AAAA-MM-DD Actualización semanal de estado del
proyecto` (por ejemplo `# 2026-11-13 ...`), con la fecha de envío, igual que el
nombre de archivo. Los reportes viejos de `old/` pueden traer otro formato en
el título; no copiarlo.

### Resumen

- Apertura: "Durante esta semana se [verbo en pasado]...", combinando en una
  sola frase los temas de avances, problemas y próximos pasos.
- Bullets: alto nivel, una línea por item, sin detalle técnico profundo. Es
  la síntesis de las novedades más relevantes de la semana — no repite el
  detalle que va en Avances Realizados.

### Avances Realizados

- Apertura: "Se lograron avances en [tema principal] y en [tema
  secundario]." Opcionalmente, una segunda oración: "El trabajo de la semana se
  concentró en [a], [b] y [c]."
- Bullets: detallados, con contexto funcional, causa raíz cuando aplica,
  métricas o decisiones tomadas. Pueden extenderse 2 a 4 líneas por item.
- Preferir pocos bullets con lo relevante: cuando el usuario edita el reporte
  final suele sacar los bullets secundarios o especulativos, no agregarlos.

### Problemas Encontrados

- Apertura: indicar el estado del problema principal (resuelto o en curso)
  y si persisten bloqueos.
- Bullets: incluir tanto problemas resueltos durante la semana como
  bloqueantes persistentes. Si un bloqueo lleva varias semanas activo,
  igual mencionarlo, aclarando que persiste — nunca omitirlo solo porque ya
  se reportó antes. Si no tuvo novedades, se puede repetir el mismo texto de
  la semana anterior.
- Si no hubo bloqueos nuevos, decirlo y nombrar igual lo que persiste: "No se
  presentaron nuevos bloqueos durante la semana; se mantiene el bloqueo de
  infraestructura del servicio de auditoría y las dependencias pendientes para
  la integración con la API de cuentas." Nunca afirmar que no hay bloqueos si
  alguno sigue abierto.
- Cuando el bloqueo es un componente interno poco conocido, explicar la
  consecuencia concreta: "sin este directorio los proyectos no pueden iniciar,
  ya que no cuentan con las configuraciones necesarias, que se encuentran en
  ese proyecto".
- No inventar dependencias o riesgos a futuro como problemas: van solo los que
  hoy frenan algo.

### Próximos Pasos

- Apertura: "Para la próxima semana, el equipo se enfocará en [tema A] y en
  [tema B]." (los reportes recientes también usan "Durante la próxima semana
  se deberá continuar con ..."; ambas son válidas).
- Bullets: acciones concretas, cada una empezando con un verbo de acción
  (Completar, Realizar, Coordinar, Continuar, Evaluar, Monitorear,
  Implementar, Dar seguimiento). Para un bloqueo que persiste se usa la
  fórmula fija "Seguimiento del bloqueo de [tema] hasta que exista una
  definición concreta."
- Lo que ya pasó QA y espera ventana sigue apareciendo cada semana como
  "Coordinar el pase a producción de [cambios] validados por el equipo de QA"
  hasta que se haga el pase.

### Ejemplo de una sección completa

```markdown
## Problemas Encontrados

Persiste la definición pendiente sobre el directorio de configuración y el bloqueo de infraestructura del servicio de auditoría. No se identifican bloqueos nuevos en la implementación.

Los puntos clave incluyen:

- Para la modernización del servicio de pagos, todavía no se definió cómo incorporar el directorio de configuración al proceso de construcción del proyecto. Este directorio es un repositorio donde se encuentra la configuración que necesitan los servicios para funcionar, como los datos de conexión y los mensajes de error que se devuelven al usuario. Durante la semana se mantuvieron conversaciones con el equipo responsable y se espera concretar una reunión en los próximos días.

- Para el servicio de auditoría, persiste el bloqueo de infraestructura para proyectos de la nueva versión de Java. La tarea depende de la configuración necesaria para ejecutar runners o mover el despliegue a Jenkins, por lo que no es posible planificar un cierre mientras no exista una decisión concreta.
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
- Redacción natural: cada oración con un sujeto claro y un verbo principal.
  Evitar construcciones como "debido a una actualización en el servidor le
  impidió enviar archivos"; escribir "El servidor dejó de enviar y recibir
  archivos por una actualización automática y se normalizó al reiniciarlo al
  día siguiente."

### Nivel de lenguaje

El público incluye gente no técnica, y aunque lo sea no conoce el detalle del
código. Patrón observado en todos los reportes anteriores:

- Se nombran sistemas, APIs, funcionalidades, procesos y ambientes (el
  sistema de pagos, el panel de administración, el servicio de archivos, DEV, QA).
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
  "lote", "nueva arquitectura". Lo mismo con la jerga interna del equipo: en
  lugar de "paridad con el original", escribir "que su comportamiento coincida
  con el del servicio original".
- Términos de infraestructura (runner, pipeline, Jenkins, AWS) se pueden usar
  tal cual, sin explicar la implementación. Herramientas o componentes internos
  poco conocidos se aclaran la primera vez que aparecen, con qué son o qué
  contienen: "el directorio de aplicación (app directory), que contiene las
  configuraciones de los proyectos".
- Cuando hay varios componentes del mismo tipo (varios servicios, middlewares
  o APIs en paralelo), nombrar siempre cuál: "el servicio de pagos" o "los
  servicios de pagos y cuentas", nunca solo "el servicio" o "el middleware".
- Incidentes: en el Resumen, contar qué pasó de forma breve (una actualización
  que dejó al servicio sin poder enviar archivos) en lugar de poner al frente un
  sistema o equipo como culpable. El detalle de la causa va en Avances
  Realizados y en Problemas Encontrados.
- Largo: Resumen, una o dos líneas por bullet. Avances Realizados, dos a
  cuatro líneas por bullet, centradas en qué se hizo y para qué.

### Agrupar por frente

- Un bullet por frente, no uno por tarea de Jira. Si varias tareas del mismo
  frente están en la misma etapa (por ejemplo, todas pasaron QA), van en un solo
  bullet que enumera los cambios.
- "Para <frente>, se ..." solo abre el primer bullet de cada frente. Los
  bullets siguientes del mismo frente empiezan directo con el hecho ("Se
  completó la integración con ...").
- No repetir el mismo estado en bullets consecutivos ("con pruebas en QA" en
  cada uno): decirlo una vez para el grupo.

### Formato de salida

Markdown: título `#` con la fecha en formato `AAAA-MM-DD`, secciones `##`, bullets con `-`, línea en
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
- ¿Se excluyó todo lo relacionado a estimación de horas o presupuestos?
- ¿Hay nombres de personas, links o IDs de tareas colados en el texto? Si
  los hay, sacalos.
- ¿Se usó "avances significativos" en algún lado? Si sí, corregilo a
  "avances".
- ¿Quedó algún identificador de código, nombre de tabla o campo, o backtick?
  Si sí, reemplazalo por su efecto funcional.
- ¿Cada frente conserva su hilo respecto al reporte anterior (misma
  progresión de etapas, sin retroceder ni repetir el estado de la semana
  pasada)?
- ¿Cada sección tiene entre 2 y 5 bullets (Problemas puede tener uno)?
  Fusionar bullets afines si hay más.
- ¿Algún frente tiene varios bullets seguidos abriendo con "Para <frente>," o
  repitiendo el mismo estado? Agruparlos.
- ¿Alguna etapa suena más avanzada de lo real ("se completó la validación"
  cuando solo terminó el código)?
- ¿Quedó algún componente ambiguo cuando hay varios del mismo tipo, o un
  término interno sin aclarar la primera vez?
- ¿Entró alguna tarea que solo cambió de estado y no estaba en el reporte
  anterior, o algo que es un estado esperado reportado como problema?
- Si el usuario editó el archivo a mano, revisar de nuevo sus cambios contra
  estas reglas (nombres de personas, saltos de línea faltantes, tildes) y
  avisarle en vez de revertirlos.

Mostrá el resultado completo listo para copiar. Si tuviste que asumir algo
por falta de información (por ejemplo, el estado de un bloqueo que no
quedó claro en las fuentes), indicalo al final, fuera del bloque del
reporte, para que el usuario lo confirme o corrija.

---

## Step 6 — Verificar las horas en Clockify

Solo en modo local y si el MCP de Clockify está disponible (buscarlo con
ToolSearch). Si no está, avisar al usuario y omitir este paso sin inventar
horas.

1. Traer las entradas de tiempo de la semana del reporte (mismo rango que las
   issues de Jira).
2. Cruzarlas contra lo reportado: cada frente del reporte debería tener horas
   cargadas, y cada bloque grande de horas debería corresponder a algo del
   reporte o a una tarea de Jira.
3. Marcar al usuario, en una lista corta fuera del reporte:
   - horas cargadas a un frente que no aparece en el reporte;
   - frentes del reporte sin horas;
   - entradas con descripción vaga, repetida o que no se entiende (por ejemplo
     "varios", "ajustes");
   - entradas de más de 3 horas seguidas, o días sin carga;
   - proyecto o tarea de Clockify distinto del que corresponde al trabajo.
4. No modificar ni borrar entradas: solo reportar las observaciones.

El detalle de horas nunca va dentro del reporte al cliente.

No expliques tu proceso a menos que el usuario lo pida.
