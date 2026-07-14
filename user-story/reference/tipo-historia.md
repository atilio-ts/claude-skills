# Tipo: Historia (feature / mejora / chore técnico)

Aplica cuando hay que implementar algo nuevo, mejorar algo existente, o hacer
una tarea técnica (infraestructura, configuración, deuda técnica, refactor)
que **no** parte de un comportamiento incorrecto reportado. Si el punto de
partida es "esto no funciona como debería", es `tipo-bugfix.md`, no este.

Caso límite frecuente: una tarea que dice "fix" en el título pero en realidad
es "probar el endpoint y arreglarlo si hace falta" — sin un comportamiento
actual vs. esperado ya identificado ni una causa raíz. Eso es historia, no
bug: la diferencia es si ya sabés qué está mal (bug) o si todavía hay que
averiguarlo como parte del trabajo (historia).

## Campos

1. **Título** — una línea que resuma la funcionalidad o tarea.
2. **Contexto** — de dónde viene el pedido: qué proyecto, quién lo solicitó,
   qué documento o evento lo desencadenó.
3. **Descripción del problema/tarea** — objetivo concreto y, si corresponde,
   los pasos o el enfoque propuesto de implementación.
4. **Definición de hecho** — criterios verificables de cuándo se considera
   terminada.
5. **Story Points** — solo si la plataforma es Jira (ver `plataforma-jira.md`).

## Estilo

- La descripción explica el **qué** y el **por qué**, no un tutorial paso a
  paso de cómo programarlo.
- Si la tarea involucra varios repos o componentes, listalos explícitamente
  (ver ejemplo de Cognito abajo) — ayuda a quien lee a dimensionar el alcance
  sin tener que adivinar.
- Aplicá igual las reglas de `tono-y-estilo.md`: los nombres técnicos se
  mantienen, pero el impacto se explica en palabras simples.

## Ejemplos reales

**Ejemplo simple (historia chica, bien acotada):**

```
Contexto
Como parte del proyecto de modernización de APIs para comercios se solicitó
la implementación de un endpoint para el proyecto AgreementSys.

Descripción del problema
Se debe implementar la función de ConsTasas en el API moderna AgreementSys
utilizando el servicio CoreAdapter para la comunicación con el Core.

Definición de hecho
Endpoint implementado y funcionando correctamente.
```

**Ejemplo con más contexto técnico (varios pasos, riesgo a resolver):**

```
Contexto
Actualmente la API MerchantIdP no puede acceder a la instancia de Cognito
donde están los usuarios, porque ambos recursos están en cuentas distintas
de AWS: MerchantIdP vive en la cuenta de EOP y el User Pool de Cognito en la
cuenta de Comercios. Sin esta conexión, la API no puede completar el login,
lo que bloquea el avance de la modernización.

Descripción del problema
Como alternativa proponemos una configuración basada en roles de IAM entre
cuentas, sin credenciales estáticas:
1. Crear un rol en la cuenta de Comercios con permisos sobre el User Pool.
2. Crear un rol en la cuenta de EOP que pueda asumir el anterior.
3. La API usa ese segundo rol para operar sobre Cognito sin guardar claves.

Definición de hecho
API conectada a Cognito y funcionando correctamente.

Repositorio
BFF: https://okgitdesl001.oca.uy.corp.itaubank.com/oca-apis-v2/oca.merchantidp
Contrato: https://okgitdesl001.oca.uy.corp.itaubank.com/oca-aws-api-gateway/oca-merchantidp
```

**Ejemplo de tarea técnica/chore (no hay "problema", hay una tarea a validar):**

```
Contexto
https://app.asana.com/1/1206625192650364/task/1213312916378343

Descripción del problema
El objetivo de esta tarea es realizar las pruebas del endpoint de cambio de
contraseña e implementar un fix en caso de ser necesario, ya que actualmente
devuelve un error al intentar hacer la operación.

Definición de hecho
Endpoint de cambio de contraseña funcionando correctamente.
```
