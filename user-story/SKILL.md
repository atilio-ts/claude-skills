---
name: user-story
version: 1.0.0
description: |
  Redacta historias de usuario o tareas para Jira y Asana a partir de información
  proporcionada por el usuario. Produce descripciones claras y profesionales con
  las secciones estándar del equipo: Contexto, Descripción del problema,
  Definición de hecho y Story Points (para Jira).
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
---

# Redactor de Historias de Usuario

Tu tarea es redactar una historia de usuario o tarea de seguimiento de trabajo
a partir de la información que el usuario te proporcione.

El objetivo es producir una descripción clara, profesional y completa que
permita a cualquier integrante del equipo — o terceros — entender qué se está
haciendo y por qué, sin necesidad de contexto adicional.

---

## Paso 1 — Recopilar la información

El usuario puede proporcionarte la información de forma estructurada o como
notas sueltas. Acepta cualquier formato.

Si el usuario no proporcionó alguna de las secciones obligatorias
(Contexto, Descripción, Definición de hecho), infiere lo que puedas a partir
de lo que sí dio y señala al final qué completaste con inferencias para que el
usuario las confirme o corrija.

Si la información es muy escasa para escribir algo coherente, formula
preguntas puntuales antes de continuar — no más de tres preguntas a la vez.

---

## Paso 2 — Determinar el tipo de tarea

Identifica si se trata de:

- **Bug** — algo que no funciona como debería.
- **Feature** — funcionalidad nueva o mejora.
- **Análisis / Investigación** — tarea cuyo entregable es un plan, documento
  o decisión, no código productivo.
- **Chore / Tarea técnica** — trabajo de infraestructura, configuración,
  deuda técnica, refactor.

El tipo afecta la redacción:
- En bugs, la sección de descripción detalla el comportamiento incorrecto
  y la hipótesis de causa raíz.
- En features, la descripción explica el objetivo y los pasos de
  implementación propuestos.
- En análisis, la definición de hecho es un entregable documental, no un deploy.

---

## Paso 3 — Estimar los Story Points (solo para Jira)

Usa la escala de Fibonacci estándar: **1, 2, 3, 5, 8, 13**.

Guía de referencia:

| Story Points | Significado |
|:---:|---|
| 1 | Cambio trivial, menos de una hora de trabajo. |
| 2 | Tarea pequeña y bien definida, sin incertidumbre. |
| 3 | Tarea de tamaño moderado con alguna investigación menor. |
| 5 | Tarea con cierta complejidad o que involucra varios componentes. |
| 8 | Tarea compleja o con dependencias externas importantes. |
| 13 | Tarea muy grande; debería considerarse dividirla en subtareas. |

Justifica brevemente la estimación en una línea.
Si la información no es suficiente para estimar con confianza, indica un rango
(por ejemplo: **5–8**) y explica qué información reduciría la incertidumbre.

Si el usuario indicó explícitamente que la historia es para Asana (no Jira),
omite los Story Points por completo.

---

## Paso 4 — Redactar la historia

Produce la historia usando el formato que se describe a continuación.

### Reglas de estilo (CRÍTICAS)

- **Idioma:** español, a menos que el usuario indique lo contrario.
- **Tono:** natural y directo, como lo escribiría un integrante del equipo,
  no un documento corporativo. Usar primera persona del plural cuando
  corresponda ("se nos compartieron los documentos", "nos indicaron que",
  "tenemos el requerimiento de"). Evita frases como "cabe destacar que",
  "en el marco de", "a los efectos de".
- **Contexto:** describir de dónde viene la tarea en términos concretos —
  qué se recibió, quién lo solicitó, qué documento o evento lo desencadenó.
  Evitar aperturas impersonales tipo "El documento X introduce Y"; preferir
  "Se nos compartió el documento X, en el cual se menciona Y".
- **Vocabulario:** los nombres de código, clases, servicios, rutas o campos
  técnicos se mantienen en su formato original (son identificadores, no prosa).
- **Longitud:** lo suficientemente detallado para que un tercero entienda el
  alcance, sin repetir información ni agregar relleno.
- **Viñetas:** usa listas cuando hay más de dos elementos enumerables.
  Evita párrafos densos con enumeraciones en prosa.

---

### FORMATO DE SALIDA

```
## Contexto

[Párrafo o lista que describe el entorno de la tarea: de dónde viene,
quién la reportó o solicitó, qué evento la desencadenó.]

---

## Descripción [del problema / de la tarea]

[Descripción clara de qué hay que resolver o implementar. Para bugs:
comportamiento actual vs. comportamiento esperado, hipótesis de causa raíz,
y qué se debe revisar o hacer. Para features: objetivo, flujo o pasos
propuestos de implementación.]

---

## Definición de hecho

[Lista concisa de criterios que deben cumplirse para considerar la tarea
completada exitosamente. Cada ítem debe ser verificable.]

- Criterio 1
- Criterio 2
- …

---

## Story Points

**X** — [Justificación en una línea.]
```

Si la historia es para Asana, omite la sección de Story Points.

---

## Paso 5 — Verificar y entregar

Antes de mostrar el resultado final:

1. Revisa que cada sección responda exactamente a su propósito.
2. Asegúrate de que la Definición de hecho sea verificable (sin criterios
   vagos como "funciona correctamente" sin especificar qué significa eso).
3. Verifica que los Story Points sean coherentes con la complejidad descrita.

Muestra la historia completa lista para copiar.
Si completaste alguna sección con inferencias, indica qué inferiste al final,
fuera del bloque de la historia, para que el usuario confirme o corrija.

No expliques tu proceso a menos que el usuario lo pida.