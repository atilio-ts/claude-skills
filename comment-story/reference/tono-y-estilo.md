# Tono y estilo

## Quién lee esto

Scrum Masters y otras personas del equipo que no necesariamente leen código.
Lo que les importa es saber qué se hizo, en qué estado quedó y qué se espera
a continuación. Un comentario de Jira es un registro de avance, no un informe
técnico.

## Reglas de redacción

- **Idioma**: español, con tildes y ñ.
- **Párrafos, no viñetas.** El comentario se escribe en párrafos breves que
  resumen lo hecho. Solo se usan viñetas si el usuario las pide
  explícitamente. Si hay varios elementos, se enumeran dentro de la oración
  ("las pruebas cubrieron A, B y C").
- **Voz impersonal en pasado.** "Se realizó el pase", "se completaron las
  pruebas", "se detectó un problema". Nunca sujeto explícito ni nombres de
  personas.
- **Apertura natural.** Según el caso: "El día de hoy se…", "El día de ayer
  se…", "Durante la semana se…", "Luego de las pruebas en DEV se…". No variar
  por variar: son las aperturas habituales del equipo.
- **Cierre opcional.** Cuando el usuario lo indica o el estado lo pide, la
  última oración dice qué se espera ("Quedo atento a los resultados", "Queda
  en espera de la definición para el pase a producción"). Es el único lugar
  donde se admite la primera persona singular. Si no hay nada que esperar, el
  comentario termina con el último hecho.
- **Resultado explícito.** Decir cómo salió: "sin fallas", "con el resultado
  esperado", "ya corregido y en revisión". Si algo falló, decirlo con su
  impacto y su estado.
- **Largo.** Pase de ambiente o cierre: una o dos oraciones. Avance o
  resultado de pruebas: uno a tres párrafos cortos. Entre 40 y 130 palabras.
  Sin repetir información ni agregar relleno. Un avance se resume en qué se
  hizo y para qué sirve, no en la lista de piezas tocadas.
- **MR.** Si solo se comparte una MR, alcanza con una línea: "Comparto la MR
  para verificación: <link>".
- **Un párrafo es una única línea continua.** No cortar oraciones con saltos
  de línea manuales: Jira reformatea el texto según el ancho de pantalla. El
  salto de línea se usa solo entre párrafos.
- **Sin formato.** Sin negritas, sin encabezados, sin tablas y sin emojis.

## Nivel de lenguaje

- Se nombran sistemas, funcionalidades, procesos y ambientes (el servicio de
  pagos, el bus de archivos, DEV, QA, producción, la pantalla de lotes).
- Nunca se nombran tablas, columnas, índices, clases, métodos, campos ni
  nombres de variables. Nada entre backticks. Pregunta de control: si el
  término solo existe dentro del código, no va.
- La causa se explica por su efecto funcional ("un archivo subido dos veces
  dejaba lotes sin terminar") y la solución por lo que logra ("evita que ese
  conflicto frene el procesamiento"), no por cómo está implementada.
- Se puede mencionar que se agregaron pruebas automáticas, sin detallarlas.
- Evitar jerga de desarrollo ("refactor", "deadlock", "endpoint", "query"):
  preferir "reorganización", "bloqueo entre procesos", "servicio", "consulta".
- Se pueden incluir fechas ("el 10/11") y números de versión ("versión
  2.3.0") cuando aportan al seguimiento.
- Sin nombres de personas, de comercios ni de clientes, y sin identificadores
  de lotes o de tareas, salvo que el usuario pida nombrar a alguien (por
  ejemplo, quien debe revisar): en ese caso se usa el nombre tal como lo dio.
  Un nombre que el usuario aceptó no se marca como error al revisar
  comentarios ya publicados; las faltas de ortografía se avisan aparte.
  Los links no van, salvo la MR cuando el usuario la pasa: en ese caso va en
  una línea aparte al final.
- Se pueden nombrar las herramientas de calidad del equipo (Sonar, la code
  review) y las capas de la arquitectura (aplicación, infraestructura, acceso)
  por su responsabilidad, sin nombrar clases ni módulos de código.
- Si el usuario da una frase o un ejemplo del texto que quiere, se conserva su
  redacción y se completa con el mismo tono; no se reescribe desde cero.

## Qué no incluir

- Nada que el usuario no haya contado: resultados, conclusiones, salvedades
  ni próximos pasos agregados por cuenta propia.
- Temas que el usuario pidió dejar fuera, ni caídas o problemas de sistemas
  de terceros que no sean el tema del comentario.
- La code review o la revisión de calidad, salvo que el usuario la mencione.
- Pasos del proceso de trabajo ni descripciones de cómo se probó,
  más allá de qué se cubrió.
- Justificaciones largas ni disculpas.
- Menciones a herramientas de asistencia ni a la forma en que se redactó el
  comentario.

## Ejemplo antes y después

Antes (técnico, con viñetas):

> Se ejecutó la batería completa de pruebas (217 tests) y se cargaron 10 lotes
> por los tres formatos.
> - El campo `credentialUpdate` y el campo `tokenizationStatus` quedan
>   independientes.
> - Los endpoints de filtros devuelven `invalid.argument` ante un valor no
>   válido.

Después (párrafos, lenguaje llano):

> Durante la semana se completaron las pruebas en QA de la separación entre la
> actualización de tarjetas y la tokenización, sin fallas en los cambios. Se
> cargaron y siguieron hasta el final 10 lotes de prueba con los tres formatos
> y se ejecutaron los tests automáticos, confirmando que cada estado se informa
> por separado y que ninguna presentación queda sin estado.
>
> Se probaron además el archivo de resultado para el comercio, las
> devoluciones, los filtros de la API y la carga simultánea de lotes, sin
> bloqueos. Se detectó un problema de visualización menor en la pantalla de
> lotes anteriores a los cambios, ya corregido y en revisión.

## Checklist rápido antes de entregar

- ¿Es texto en párrafos, sin viñetas, negritas ni encabezados?
- ¿Cada párrafo está en una sola línea continua?
- ¿Está en voz impersonal, con la primera persona solo en el cierre?
- ¿Dice cómo salió y en qué estado quedó?
- ¿Se evitó todo identificador de código, backtick, nombre de persona o ID?
- ¿Un Scrum Master que no programa entendería qué se hizo y qué sigue?
- ¿Respeta tildes y ñ, y no repite lo que ya decía un comentario anterior?
- ¿Tiene un largo parecido a los últimos comentarios del usuario?
- ¿Todo lo que afirma lo contó el usuario o sale de las fuentes?
- ¿Cada comentario indica en qué tarea va y si es nuevo o reemplaza otro?
