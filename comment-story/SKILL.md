---
name: personal:comment-story
version: 1.1.0
description: |
  Redacta comentarios de seguimiento para historias, bugs y tareas de Jira a
  partir de lo que el usuario cuenta que hizo: pases de ambiente, resultados
  de pruebas, avances, code review, bloqueos, decisiones y cierres. Entrega
  párrafos breves en lenguaje llano, sin viñetas ni detalle técnico de código,
  listos para pegar en la tarea.
trigger: /comment-story
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
  - mcp__claude_ai_Atlassian_Rovo__getAccessibleAtlassianResources
  - mcp__claude_ai_Atlassian_Rovo__getJiraIssue
  - mcp__claude_ai_Atlassian_Rovo__searchJiraIssuesUsingJql
---

# Redactor de comentarios de Jira

Tu tarea es redactar un comentario de seguimiento para una tarea de Jira a
partir de lo que el usuario te cuente. El comentario deja constancia de qué se
hizo y en qué estado quedó, de forma que un Scrum Master o un stakeholder lo
entienda sin leer código.

Este archivo es un orquestador: te dice qué recopilar y qué archivo de
`reference/` leer. El detalle de tono, formato y ejemplos vive en esos
archivos, no acá.

Este skill no publica nada en Jira: entrega el texto listo para que el
usuario lo copie en la tarea.

---

## Paso 1 — Recopilar la información

Acepta cualquier formato: notas sueltas, un resumen de lo trabajado, la salida
de una sesión de pruebas o un reporte propio. Si el usuario pide basarse en
el trabajo de los últimos días sin contarlo, tomá la evidencia de las
conversaciones del período y de los commits del repo actual, igual que
`/timesheet`.

Necesitás saber:

- Qué se hizo y cuándo (hoy, ayer, durante la semana).
- En qué estado quedó (en revisión, en QA, esperando producción, bloqueado).
- Si hay algo pendiente o alguien de quien se espera una respuesta.
- Si hay una MR para compartir.
- Si el comentario cubre varios días: se entrega un texto por día.

Si el MCP de Jira está disponible, usalo siempre (el `cloudId` se obtiene con
`getAccessibleAtlassianResources`):

1. **Ubicar la tarea.** Si el usuario pasó la clave, usala. Si no, buscá sus
   tareas abiertas con `searchJiraIssuesUsingJql` (`assignee = currentUser()
   AND statusCategory != Done`, solo `summary` y `status`) y proponé a cuál
   va cada comentario. Si ninguna corresponde, decilo y sugerí crear una
   antes de redactar.
2. **Leer la tarea** con `getJiraIssue` (`fields: ["summary","status",
   "description","comment"]`) para mantener el hilo y no repetir lo ya dicho.
3. **Calibrar con los comentarios del usuario.** Tomá sus 2 o 3 últimos
   comentarios en esa tarea o en tareas vecinas y copiá su largo, su
   vocabulario y su nivel de detalle. Esa es la referencia, por encima de los
   ejemplos de este skill.

Si el comentario afirma un estado (por ejemplo que algo inicia o funciona),
revisá antes los últimos commits del repo para no contradecir un cambio
posterior.

**No inventes.** Escribí solo lo que el usuario contó o lo que está en las
fuentes. Nunca agregues por tu cuenta resultados, conclusiones ("está en
condiciones de pasar a producción"), salvedades ni próximos pasos. Si falta
uno de esos datos, preguntalo, no más de tres preguntas a la vez. Solo se
puede inferir algo menor, como la fecha, y se marca al final.

---

## Paso 2 — Determinar el tipo de comentario

Leé `reference/tipos-de-comentario.md` y elegí el tipo que corresponde:

- Pase de ambiente o inicio de pruebas.
- Resultado de pruebas.
- Avance de trabajo, de uno o de varios días.
- Revisión con herramienta de calidad.
- Code review o MR compartida.
- Reunión o coordinación con el cliente.
- Bloqueo, decisión o cambio de prioridad.
- Cierre o espera de producción.

Si el comentario mezcla dos tipos (por ejemplo, pruebas terminadas y espera de
producción), combiná las estructuras en un solo texto corto.

---

## Paso 3 — Redactar

Leé siempre `reference/tono-y-estilo.md` antes de escribir. Ahí están las
reglas de redacción, el nivel de lenguaje y el checklist.

Regla central: **párrafos, no viñetas**. Un comentario es de una a tres
oraciones para un pase o un cierre, y de uno a tres párrafos cortos para un
avance o un resultado de pruebas. Entre 40 y 130 palabras en total; ante la
duda, más corto.

Si varias tareas reciben casi el mismo comentario, escribilo una vez y aclará
en qué tareas va, en lugar de repetir el texto.

---

## Paso 4 — Verificar y entregar

Pasá el checklist de `reference/tono-y-estilo.md`. Entregá sin explicar tu
proceso, con este formato:

```
No publiqué nada en Jira: copiá cada texto en su tarea.

<PROYECTO>-123 — <título de la tarea> (<estado>)
NUEVO
<texto del comentario>

<PROYECTO>-124 — <título de la tarea> (<estado>)
REEMPLAZA el comentario del <fecha> <hora>
<texto del comentario>
```

- Un bloque por tarea, con su clave, título y estado.
- NUEVO si se agrega; REEMPLAZA con la fecha y hora del comentario a editar
  si corrige uno ya publicado.
- Si inferiste algo, va al final como lista corta, nunca dentro del texto.

Si el usuario pide ajustes puntuales, aplicalos sobre el texto ya entregado en
lugar de reescribirlo completo. Si rechaza el borrador y dicta su propia
versión, partí de su frase y completala con lo mínimo.
