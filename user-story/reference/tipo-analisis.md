# Tipo: Análisis / Estimación

Aplica cuando el entregable es una decisión, un documento revisado o un
número (horas, complejidad), no código productivo. Ejemplos típicos:
estimar el esfuerzo de un proyecto, revisar si una propuesta es viable,
validar un documento antes de que se convierta en trabajo real.

Se diferencia de `tipo-historia.md` en que acá no se implementa nada — el
resultado de la tarea es información para que otros decidan, no una
funcionalidad terminada.

## Campos

1. **Título** — qué se está analizando o estimando.
2. **Contexto** — el documento, propuesta o pedido que originó el análisis
   (link a la fuente si existe).
3. **Descripción de la tarea** — qué hay que analizar o estimar
   específicamente, y bajo qué restricciones o prioridades (si el que pide el
   análisis marcó algo como prioritario, decirlo).
4. **Definición de hecho** — el entregable concreto: documento corregido,
   estimación verificada, decisión tomada y comunicada. Nunca "código
   funcionando", porque no es ese tipo de tarea.
5. **Story Points** — solo si la plataforma es Jira. Si hay mucha
   incertidumbre sobre el esfuerzo del análisis en sí, es válido dar un rango
   (ver `plataforma-jira.md`).

## Estilo

- Es la sección más corta de las cuatro en general — no hay que inventar
  pasos de implementación donde no los hay.
- Si el análisis tiene varios frentes (por ejemplo, estimar distintos
  componentes por separado), listalos.

## Ejemplos reales

```
Contexto
https://docs.google.com/spreadsheets/d/.../edit
https://docs.google.com/document/d/.../edit

Descripción de la tarea
Se debe analizar y revisar si la propuesta para el proyecto es correcta y si
la estimación de horas es apropiada.

Definición de hecho
Documento de propuesta corregido en caso de ser necesario y estimación de
horas verificada.
```

```
Contexto
https://app.asana.com/1/1206625192650364/task/1213716667976418

Descripción de la tarea
Se solicitó estimar el esfuerzo en horas de agregar alertas a RPO en los
distintos puntos de falla del flujo: ABU, Pay Studio, Integrity, generación
de resultados y liquidación. Se pidió priorizar ABU y Pay Studio.

Definición de hecho
Estimación de esfuerzo, en horas y en complejidad, para agregar esta
funcionalidad a RPO.
```
