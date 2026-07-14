---
name: personal:user-story
version: 2.0.0
description: |
  Redacta historias de usuario, bugs, análisis o minutas de reunión para Jira
  y Asana a partir de información proporcionada por el usuario. Determina el
  tipo de tarea y la plataforma, y aplica la guía correspondiente desde
  reference/ para producir una descripción clara y profesional.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
---

# Redactor de Historias de Usuario

Tu tarea es redactar una historia, bug, análisis o minuta de reunión a partir
de la información que el usuario te proporcione. El objetivo es una
descripción clara y completa que cualquier integrante del equipo — técnico o
no — pueda entender sin contexto adicional.

Este archivo es un orquestador: determina tipo y plataforma, y te dice qué
archivo de `reference/` leer en cada caso. El contenido detallado (campos,
ejemplos, reglas de formato) vive en esos archivos, no acá.

---

## Paso 1 — Recopilar la información

Acepta cualquier formato: estructurado o notas sueltas.

Si falta alguna sección obligatoria, infiere lo que puedas a partir de lo que
sí te dieron y señalá al final qué completaste por inferencia para que el
usuario lo confirme o corrija.

Si la información es muy escasa para escribir algo coherente, formulá
preguntas puntuales antes de continuar — no más de tres preguntas a la vez.

---

## Paso 2 — Determinar el tipo de tarea

Hay cuatro tipos posibles. Si no es obvio cuál corresponde, preguntale al
usuario explicándole brevemente la diferencia:

- **Reunión** — minuta o resumen de una reunión, no un pedido de trabajo.
  → Leer `reference/tipo-reunion.md`.
- **Historia** — funcionalidad nueva, mejora o tarea técnica/chore que no
  parte de un comportamiento incorrecto reportado.
  → Leer `reference/tipo-historia.md`.
- **Bug fix** — algo no se comporta como debería.
  → Leer `reference/tipo-bugfix.md`.
- **Análisis / Estimación** — el entregable es una decisión, documento o
  número, no código productivo.
  → Leer `reference/tipo-analisis.md`.

**Si el tipo es Bug fix**, antes de seguir hay un paso obligatorio: preguntar
si el problema es un error de implementación real o si es una funcionalidad
que se diseñó de una manera y el proyecto evolucionó hasta dejar ese diseño
desactualizado. El detalle de por qué importa esta distinción y cómo cambia
la redacción está en `reference/tipo-bugfix.md` — leelo antes de preguntar.

---

## Paso 3 — Determinar la plataforma

Si el usuario no indicó si esto es para **Asana** o **Jira**, preguntaselo
siempre — incluso si el tipo es Reunión — explicando la diferencia central:

- **Asana**: texto plano, sin markdown, y siempre cierra con el campo
  "Link a JIRA de OCA".
- **Jira**: markdown completo, e incluye Story Points.

Según la respuesta, leé:
- `reference/plataforma-asana.md`, o
- `reference/plataforma-jira.md`.

---

## Paso 4 — Redactar

Combiná las tres fuentes que ya leíste:

1. El archivo de **tipo** (Paso 2) — qué campos van y en qué orden.
2. El archivo de **plataforma** (Paso 3) — formato (markdown o texto plano),
   Story Points o Link a Jira.
3. `reference/tono-y-estilo.md` — leelo siempre, sin importar tipo o
   plataforma. Ahí está la guía de humanización, las reglas de redacción y
   el checklist de "no asumas que es un bug".

---

## Paso 5 — Verificar y entregar

Antes de mostrar el resultado final:

1. Revisá que cada sección responda exactamente a su propósito según el
   archivo de tipo correspondiente.
2. Asegurate de que la Definición de hecho sea verificable (sin criterios
   vagos como "funciona correctamente" sin especificar qué significa eso).
   No aplica a Reunión, que no tiene esta sección.
3. Si la plataforma es Jira, verificá que los Story Points sean coherentes
   con la complejidad descrita.
4. Si la plataforma es Asana, verificá que el campo Título esté presente y
   que el cierre "Link a JIRA de OCA" no haya quedado afuera (con el link
   real o `[Pendiente]`).
5. Pasá el checklist de `reference/tono-y-estilo.md`.

Mostrá el resultado completo listo para copiar. Si completaste alguna
sección con inferencias, indicá qué inferiste al final, fuera del bloque de
la historia, para que el usuario confirme o corrija.

No expliques tu proceso a menos que el usuario lo pida.
