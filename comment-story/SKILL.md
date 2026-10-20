---
name: personal:comment-story
version: 1.0.0
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

Si el usuario te pasa la clave de la tarea y el MCP de Jira está disponible,
leé la descripción y los últimos comentarios con `getJiraIssue` (pidiendo
`comment` en `fields`) para mantener el hilo y no repetir lo ya dicho. El
`cloudId` se obtiene con `getAccessibleAtlassianResources`.

Si falta lo esencial para escribir algo coherente, preguntá lo mínimo, no más
de tres preguntas. Si podés inferir, inferí y marcalo al final.

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
avance o un resultado de pruebas.

---

## Paso 4 — Verificar y entregar

Pasá el checklist de `reference/tono-y-estilo.md`. Mostrá el comentario listo
para copiar, sin explicar tu proceso. Si inferiste algo (una fecha, un
estado), indicalo al final, fuera del texto del comentario, para que el
usuario lo confirme o corrija.

Si el usuario pide ajustes puntuales, aplicalos sobre el texto ya entregado en
lugar de reescribirlo completo.
