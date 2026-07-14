# Tono y estilo

## Quién lee esto

Scrum Masters y otras personas del equipo que no necesariamente tienen
conocimiento técnico profundo. Lo que les importa es entender **qué cambia y
por qué es necesario**, no el mecanismo interno paso a paso. Está bien
mencionar archivos, clases, nombres de servicios o fragmentos de código —
son identificadores necesarios para que un desarrollador pueda ubicar el
cambio — pero cada mención técnica relevante tiene que venir acompañada de
una traducción a impacto, en una frase, para quien no lee código.

Ejemplo de la traducción que hay que hacer siempre:

> Solo lo técnico: "credentialUpdate se sobrescribe entre el driver de ABU y
> el de Cybersource."

> Con impacto agregado: "El campo que indica si la tarjeta fue actualizada
> se pisa entre dos pasos del proceso, lo que hace que el comercio no reciba
> el aviso de la actualización aunque el sistema sí tenga la tarjeta nueva."

Ver `tipo-bugfix.md` para el ejemplo completo antes/después de un caso real.

## Reglas de redacción

- **Idioma**: español, a menos que el usuario indique lo contrario.
- **Tono**: natural y directo, como lo escribiría un integrante del equipo,
  no un documento corporativo. Usar primera persona del plural cuando
  corresponda ("se nos compartieron los documentos", "nos indicaron que",
  "tenemos el requerimiento de"). Evitar frases como "cabe destacar que",
  "en el marco de", "a los efectos de".
- **Contexto**: describir de dónde viene la tarea en términos concretos —
  qué se recibió, quién lo solicitó, qué documento o evento lo desencadenó.
  Evitar aperturas impersonales tipo "El documento X introduce Y"; preferir
  "Se nos compartió el documento X, en el cual se menciona Y".
- **Vocabulario técnico**: los nombres de código, clases, servicios, rutas o
  campos técnicos se mantienen en su formato original — son identificadores,
  no prosa. No hay que "traducirlos" ni sacarlos, solo explicar qué significan
  para el negocio cuando sea relevante.
- **Longitud**: lo suficientemente detallado para que un tercero entienda el
  alcance, sin repetir información ni agregar relleno.
- **Viñetas**: usar listas cuando hay más de dos elementos enumerables.
  Evitar párrafos densos con enumeraciones en prosa.

## No asumas que es un bug

Antes de redactar una historia de tipo bug fix, seguí el paso obligatorio de
`tipo-bugfix.md`: preguntale al usuario si el comportamiento fue siempre un
error, o si es una funcionalidad que se diseñó de una manera y el proyecto
evolucionó hasta dejar ese diseño desactualizado. La redacción cambia según
la respuesta — no es lo mismo un error de implementación que una limitación
de un diseño que en su momento fue válido.

## Checklist rápido antes de entregar

- ¿Cada mención técnica importante tiene su frase de impacto al lado?
- ¿Se evitó el lenguaje acusatorio o de reporte formal de incidente?
- ¿Un Scrum Master que no programa podría explicarle a un stakeholder qué
  cambió y por qué, solo leyendo esto?
