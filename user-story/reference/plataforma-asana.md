# Plataforma: Asana

Las notas de Asana no renderizan markdown — todo lo que se escriba con `##`,
`**`, backticks o listas con `- ` se ve tal cual, con los símbolos incluidos.
Por eso el formato es **texto plano**.

## Reglas de formato

- **Nada de markdown**: sin encabezados `##`, sin negrita `**texto**`, sin
  backticks para nombres técnicos, sin `- item` como viñeta.
- **Nombres de sección**: como texto simple en su propia línea (ej.
  `Contexto`, no `## Contexto`).
- **Listas**: como líneas separadas, sin guion ni ningún otro prefijo de
  viñeta — así aparecen en las notas reales del equipo. Cada ítem va en su
  propia línea y se distingue por el salto de línea, no por un símbolo.
- **Título**: va como primera línea del cuerpo de la nota.
- **Cierre obligatorio**: siempre termina con el campo `Link a JIRA de OCA`,
  incluso si en el momento no se tiene el link. Si el usuario no lo dio,
  dejar `[Pendiente]` como placeholder para que lo complete después.
- **Nunca incluye Story Points** — ese campo es exclusivo de Jira.
- **Sin saltos de línea manuales dentro de un párrafo**: cada párrafo va en
  una sola línea continua. Asana reformatea el texto dinámicamente según el
  ancho de pantalla, así que cortar líneas a mano para que se vean prolijas
  en el editor termina en cortes irregulares dentro de la app. Solo hay
  salto de línea entre secciones o entre ítems de una lista.

## Estructura final para Asana

```
[Título]

Contexto
[...]

Descripción del problema
[...]

Definición de hecho
[...]

Link a JIRA de OCA
[link o [Pendiente]]
```

(Para el tipo Reunión, la estructura es la de `tipo-reunion.md` — no lleva
Contexto/Descripción/Definición de hecho ni el cierre de Link a Jira.)

## Ejemplo real de referencia

```
[OPC-2326] Diseño de botón, formulario de devolución, modal de confirmación

Contexto
Esta tarea surge de la reunión de refinamiento y como parte del proyecto de sobres y cupones.

Descripción
El objetivo de esta tarea es crear los diseños para los siguientes elementos:
Botón "Anular Presentación", debe ir en la vista de una presentación
El botón debe estar disponible solo para archivos anulables
Al hacer clic, debe aparecer un modal de confirmación

Definición de hecho
Vistas para el botón de anular, modal de confirmación y formulario de devolución creadas
```

Notá cómo no hay ningún símbolo de markdown ni siquiera en la lista de
elementos a diseñar — son líneas simples.
