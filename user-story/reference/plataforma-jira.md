# Plataforma: Jira

Jira sí renderiza markdown en sus campos de descripción, así que acá el
formato es **markdown completo**.

## Reglas de formato

- **Encabezados**: `##` para cada sección.
- **Identificadores técnicos**: backticks (nombres de clases, campos,
  endpoints, condiciones de código).
- **Listas**: `-` para viñetas.
- **Título**: como encabezado `#` al inicio, o como primera línea en negrita
  si el título ya va en el campo "Summary" nativo de Jira y esta redacción es
  solo para la descripción — preguntá si no está claro dónde va a pegarse.
- **Nunca incluye el campo Link a Jira** — la historia ya vive en Jira, no
  hace falta linkearse a sí misma.
- **Siempre incluye Story Points**, salvo que el tipo sea Reunión.
- **Sin saltos de línea manuales dentro de un párrafo**: cada párrafo va en
  una sola línea continua. Jira reformatea el texto dinámicamente según el
  ancho de pantalla, así que cortar líneas a mano para que se vean prolijas
  en el editor termina en cortes irregulares dentro de la app. Los `##` y
  `---` marcan la estructura; dentro de cada sección, el texto corrido no
  lleva saltos manuales.

## Story Points

Usa la escala de Fibonacci estándar: **1, 2, 3, 5, 8, 13**.

| Story Points | Significado |
|:---:|---|
| 1 | Cambio trivial, menos de una hora de trabajo. |
| 2 | Tarea pequeña y bien definida, sin incertidumbre. |
| 3 | Tarea de tamaño moderado con alguna investigación menor. |
| 5 | Tarea con cierta complejidad o que involucra varios componentes. |
| 8 | Tarea compleja o con dependencias externas importantes. |
| 13 | Tarea muy grande; debería considerarse dividirla en subtareas. |

Justificá brevemente la estimación en una línea. Si la información no
alcanza para estimar con confianza, indicá un rango (ej. **5–8**) y explicá
qué información reduciría la incertidumbre.

## Estructura final para Jira

```
## Contexto

[...]

---

## Descripción [del problema / de la tarea]

[...]

---

## Definición de hecho

- Criterio 1
- Criterio 2

---

## Story Points

**X** — [Justificación en una línea.]
```
