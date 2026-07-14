# Tipo: Bug fix

Aplica cuando algo no se comporta como debería y hay que corregirlo. Antes de
escribir una sola línea, hay un paso obligatorio.

## Paso obligatorio antes de redactar

No des por sentado que se trata de un "bug" en el sentido de un error de
implementación. Preguntale al usuario:

> ¿Esto fue siempre un error, o la funcionalidad se diseñó de una manera en
> su momento y el proyecto/uso evolucionó hasta dejar ese diseño
> desactualizado?

Esta distinción importa porque cambia el tono de toda la historia:

- **Error de implementación real** (ej. una comparación mal hecha, un guard
  que falta): se describe como comportamiento incorrecto de forma directa,
  causa raíz técnica incluida.
- **Diseño que quedó desactualizado** (ej. un campo que servía para un solo
  propósito y ahora se usa para dos cosas distintas porque el flujo creció):
  se describe como una limitación que el diseño original no contemplaba, no
  como una falla de quien lo escribió. Evitá lenguaje acusatorio tipo "esto
  está roto" o "quedó mal hecho" — es más preciso y más justo decir "el
  campo X se pensó para un solo caso y ahora tiene que cubrir dos, lo cual
  genera este conflicto".

Si el usuario no tiene claro cuál de los dos es, avanzá con la hipótesis más
razonable según la evidencia técnica, pero aclaralo al final junto con el
resto de las inferencias (ver Paso 5 del `SKILL.md`).

## Campos

1. **Título** — una línea que describa el síntoma, no la causa (ej. "Bugfix:
   tarjeta actualizada por ABU se borra antes de llegar a PayStudio").
2. **Contexto** — cómo se detectó y quién lo reportó (cliente, monitoreo,
   otro desarrollador, code review propio).
3. **Descripción del problema** — comportamiento actual vs. esperado, y la
   causa raíz. Cada afirmación técnica relevante se acompaña de una frase que
   traduzca el impacto (ver `tono-y-estilo.md`) — quien lee no tiene por qué
   entender el código para entender qué se rompe.
4. **Definición de hecho** — criterios verificables, idealmente incluyendo
   tests si aplica.
5. **Story Points** — solo si la plataforma es Jira (ver `plataforma-jira.md`).

## Estilo

- El detalle técnico (nombres de clases, fragmentos de código, condiciones)
  se mantiene tal cual — no hay que "simplificarlo" quitando información,
  sino sumarle una capa de traducción a impacto.
- Evitá el tono de reporte de incidente formal ("se ha detectado una
  anomalía..."); escribí como se lo contarías a un compañero.

## Ejemplo real — humanizando sin perder precisión técnica

**Antes (solo el detalle técnico, difícil de seguir para un Scrum Master):**

```
Comportamiento actual: Al hacer login con NBK por primera vez, internamente
se intenta recuperar el usuario existente. Como el usuario es nuevo y no
existe en la base de datos, se lanza IllegalStateException: Invalid handle,
lo que resulta en un error 500.

Causa raíz: la integración con Sherlog convirtió silenciosamente a la
función utilizada saveSGBUser en un método de solo actualización (requiere
existencia previa del usuario), rompiendo el flujo de creación que antes
funcionaba como upsert.
```

**Después (mismo detalle técnico, con la traducción de impacto agregada):**

```
Comportamiento actual: cuando un usuario nuevo inicia sesión con NBK por
primera vez, el login falla con un error 500 en vez de crearle la cuenta —
en la práctica, ningún usuario nuevo puede entrar al sistema por esta vía.

Causa raíz: internamente se intenta recuperar el usuario en la base de
datos con saveSGBUser, pero al integrar Sherlog esa función pasó a exigir
que el usuario ya exista (dejó de crear usuarios nuevos, solo actualiza los
existentes). Como es la primera vez que este usuario inicia sesión, la
búsqueda no encuentra nada y el sistema lanza
IllegalStateException: Invalid handle.
```

Notá que no se quitó ningún nombre técnico (`saveSGBUser`,
`IllegalStateException: Invalid handle`) — se agregó la frase inicial que
explica qué significa esto para alguien que usa el sistema.
