# Tipo: Reunión

Aplica cuando la tarea es en realidad la minuta o el resumen de una reunión
(interna o con cliente), no un pedido de trabajo. Se nota porque el usuario te
da algo como "tuvimos una reunión sobre X", una lista de asistentes, o notas
sueltas de una conversación en vez de un problema a resolver.

Este tipo no comparte estructura con historia/bug/análisis — no tiene
Contexto + Descripción + Definición de hecho, y nunca lleva Story Points ni
Link a Jira, sin importar qué plataforma se haya elegido en el Paso 3 del
skill. En la práctica casi siempre termina siendo para Asana en texto plano,
pero la plataforma se pregunta igual por consistencia con el resto del flujo.

## Campos

En este orden:

1. **Título** — fecha + tema en una línea (ej. "2026-02-05 Reunión - Code
   review, actualización template Java").
2. **Participantes** — lista de quiénes estuvieron. Omitir si todos los
   asistentes ya están implícitos en el título o si el usuario no los dio.
3. **Contexto** — opcional. Solo si el motivo de la reunión no es obvio a
   partir del título (por ejemplo, si viene de un pedido previo o de un
   problema reportado). Si el motivo ya está claro en el título, se omite.
4. **Breve resumen** — párrafo(s) narrando qué se conversó, qué se acordó y
   qué información nueva surgió. Es el corazón de la minuta.
5. **Tareas identificadas** — lista de próximos pasos, cada uno con quién
   quedó a cargo. Si no surgió ninguna tarea concreta, se deja un guion solo.

## Estilo

- Narrativo y en primera persona ("me reuní con...", "conversamos acerca
  de...", "acordamos que..."), no un acta formal de actas corporativas.
- No hace falta "Definición de hecho" — una reunión no tiene criterios de
  aceptación, tiene conclusiones y próximos pasos.
- Si algo quedó pendiente de decidir, decilo explícitamente en vez de omitirlo
  ("queda pendiente definir X").

## Ejemplos reales (tono de referencia)

**Ejemplo 1 — con Participantes explícitos:**

```
Participantes:
- Rodrigo Mori
- Diego Petrella
- Pablo Benitez

Breve resumen:
El día de hoy se llevó a cabo la code review de los últimos cambios introducidos al template Java para actualizarlo a la última versión estable (Java 25) con el equipo de integraciones.

Se realizó una revisión de los cambios y demostraciones de funcionamiento con pruebas de flujo completo de la aplicación, y además se mostraron los nuevos ejemplos y herramientas incluidos dentro del template.

El equipo quedó conforme y se integraron los cambios, por lo cual esta pasa a ser la versión más reciente del template y la que será utilizada como punto de partida para nuevos proyectos de APIs en Java.

Tareas identificadas
-
```

**Ejemplo 2 — con Contexto porque el motivo no era obvio del título:**

```
Contexto
Se desea realizar un pase a producción de los últimos cambios implementados a Pagos Recurrentes RPO y al Backoffice. Entre estos cambios, los principales son:
- Fix para actualización de credenciales.
- Tokenización Mastercard
- Fix para login con NBK
- Fix para tokenización

Breve resumen
Durante esta reunión conversamos con Miguel acerca de los últimos cambios que estuvimos implementando al proyecto y sobre la posibilidad de incluirlos en el próximo pase a producción.

Acordamos que se estará implementando la tokenización por marca (Mastercard-VISA), para lo cual estaremos agregando una bandera dentro de RPO para poder controlar esto. Este cambio será testeado durante lo que queda de la semana y será desplegado el miércoles de la semana que viene.

Tareas identificadas
- Atilio Villalba implementará las banderas para tokenización por marca en RPO.
- Una vez implementados los cambios, los mismos serán testeados antes del pase a producción.
```

Nota: estos ejemplos muestran viñetas con "-" solo para legibilidad en este
documento de referencia. Al redactar para Asana, seguí las reglas de
`plataforma-asana.md` (sin viñetas markdown literales).
