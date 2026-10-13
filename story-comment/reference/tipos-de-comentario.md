# Tipos de comentario

Elegí el tipo según lo que el usuario contó. Todos siguen las reglas de
`tono-y-estilo.md`: párrafos, voz impersonal, sin identificadores de código.

## Pase de ambiente o inicio de pruebas

Una o dos oraciones: qué ambiente, qué se hizo y que se iniciaron las pruebas.
Si viene de un ambiente anterior, mencionar cómo salió.

> Luego de las pruebas exitosas en el ambiente DEV, el día de hoy se hizo el
> pase al ambiente QA y se iniciaron las pruebas.

> El día de ayer se aprobaron los cambios y se realizó el pase al ambiente DEV.
> Se estarán realizando las pruebas correspondientes antes de pedir el pase a
> QA.

## Resultado de pruebas

Primero el resultado general, después qué se cubrió y, al final, hallazgos y
estado. Sin viñetas: lo cubierto se enumera dentro de la oración.

> Durante la semana se completaron las pruebas en QA del cambio, sin fallas.
> Se verificaron la descarga de archivos nuevos y la de archivos que ya
> existían en la carpeta de destino, y en todos los casos se obtuvo el
> resultado esperado.
>
> Quedo atento al pase a los siguientes ambientes.

Si se encontró algo, se explica por su efecto y se indica el estado: "Se
detectó un problema de visualización menor en la pantalla de lotes anteriores
a los cambios, ya corregido y en revisión."

## Avance de trabajo

Qué problema se atendió, por qué importa y qué se hizo, en uno a tres
párrafos. La causa se cuenta por su efecto, y los cambios por lo que logran.

> Esta semana se trabajó en los lotes que quedaban sin terminar al procesar
> la respuesta del servicio de actualización de tarjetas. Ocurría cuando un
> comercio subía dos veces el mismo archivo y ambos lotes se bloqueaban entre
> sí.
>
> Se corrigió para que ese conflicto no frene el procesamiento y quede
> registrado para su seguimiento, y se agregaron pruebas automáticas que
> reproducen el caso.

## Code review o MR compartida

Qué se pidió en la revisión, qué se corrigió y que se compartió la MR. La MR
va en una línea aparte, al final, solo si el usuario la pasó.

> El día de hoy se hizo la code review, en la cual se pidió bajar el nivel de
> detalle de los registros de los servicios que envían mensajes al Core. Ya se
> corrigió lo solicitado y se compartió la MR con el equipo. Quedo atento.

## Bloqueo, decisión o cambio de prioridad

Qué pasó, qué se decidió y qué queda en espera. Sin nombres de personas ni
equipos concretos: "con el equipo de infraestructura", "con las personas
responsables".

> Se coordinó con infraestructura la actualización del entorno de despliegue
> para estos proyectos. Debido al esfuerzo que implica y a la prioridad que
> hoy tiene otra modernización, se decidió pausar esta tarea y retomarla más
> adelante. Quedamos atentos a novedades para continuar.

## Cierre o espera de producción

Qué quedó terminado y qué falta para producción. Si el pase a producción es
incierto, indicar que se cierra la tarea y que se abrirá otra para su
seguimiento.

> El día de hoy se hizo la code review de las últimas correcciones, que ya
> fueron aprobadas, y luego se aprobó el pase a QA. Como es incierto cuándo se
> realizará el pase a producción, se da la tarea por terminada y se abrirá otra
> para ese seguimiento.

## Combinar tipos

Si una misma novedad abarca dos tipos, un solo texto corto con el orden más
natural: primero lo que pasó (pruebas o pase) y al final el estado o la espera.
Ejemplo: resultado de pruebas más espera de producción termina con "Quedo
atento al pase a producción".
