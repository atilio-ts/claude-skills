# Plataforma: Jira

Jira sí renderiza markdown en sus campos de descripción, así que acá el
formato es **markdown completo**.

## Reglas de formato

- **Encabezados**: `##` para cada sección.
- **Identificadores técnicos**: backticks (nombres de clases, campos,
  endpoints, condiciones de código).
- **Listas**: `-` para viñetas.
- **Separadores**: una línea `---` entre secciones.
- **Título**: va en el campo "Summary" nativo de Jira, así que se entrega
  aparte, como primera línea fuera del bloque de la descripción. Copiá el
  formato de las historias recientes del proyecto: si usan un prefijo de
  proyecto y un separador ("<PREFIJO> - <Iniciativa>: <tarea>"), repetilo; los
  bugs suelen empezar con "Bugfix: <síntoma>". Las tareas de soporte llevan un
  título simple ("Soporte para creación de …").
- **Nunca incluye el campo Link a Jira** — la historia ya vive en Jira, no
  hace falta linkearse a sí misma.
- **Historias relacionadas**: si la tarea continúa o depende de otra, nombrala
  por su clave en el Contexto (`<PROYECTO>-123`) en lugar de volver a contar su
  contenido.
- **Story Points nunca van en la descripción.** Si corresponde estimar,
  sugerilos fuera del bloque para el campo nativo de Jira (ver abajo). No
  aplica a Reunión.
- **Sin saltos de línea manuales dentro de un párrafo**: cada párrafo va en
  una sola línea continua. Jira reformatea el texto dinámicamente según el
  ancho de pantalla, así que cortar líneas a mano para que se vean prolijas
  en el editor termina en cortes irregulares dentro de la app. Los `##` y
  `---` marcan la estructura; dentro de cada sección, el texto corrido no
  lleva saltos manuales.

## Story Points (sugerencia aparte)

Se cargan en el campo nativo de Jira, no en la descripción. Después del bloque
de la historia, agregá una línea como "Story Points sugeridos: **3** — tarea
moderada con una integración nueva." Usa la escala de Fibonacci estándar: **1, 2, 3, 5, 8, 13**.

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

Título (campo Summary, fuera del bloque):
`<PREFIJO> - <Iniciativa>: <tarea>`

Descripción:

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
```

Una sección `## Repositorio` solo se agrega si el usuario pasa los links.
