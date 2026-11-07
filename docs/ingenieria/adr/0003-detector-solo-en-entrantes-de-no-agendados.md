# ADR 0003 — El detector corre solo en llamadas entrantes de números no agendados

- **Fecha:** 2026-11-06
- **Estado:** propuesta sin discutir
- **Participantes de la discusión:** el equipo, con Mateo Antenucci, durante la segunda vuelta de
  [#143](https://github.com/Corchets/bitacora_tesis/issues/143). Al tutor se le explica el porqué el 2026-11-11; no se
  le pide que lo confirme. Se registra en [#151](https://github.com/Corchets/bitacora_tesis/issues/151).
- **Ámbito:** alcance

> **Estado: propuesta sin discutir.** El equipo tomó la decisión el 2026-11-06; lo que falta revisar es este texto.
> Contradice la precisión de alcance del 2026-10-04 en
> [D03](../../gestion/MAPA-DECISIONES.md#d03--congelar-alcance-y-contribución), que todavía no se actualizó.

## Contexto

Hasta ahora el detector escuchaba cualquier llamada. La precisión de D03 del 2026-10-04 deja la agenda y la dirección
de la llamada (entrante o saliente) fuera de sus entradas: el detector ve solo la transcripción.

Los productos comparables no escuchan todo:
- **Google:** Scam Detection no se usa nunca en llamadas con contactos
  ([lectura del repo, §5.1](../../investigacion/lecturas/2026-google-scam-detection.md#51-scam-detection-en-llamadas--análisis-del-contenido)).
- **Samsung:** detecta solo en llamadas de números no agendados
  ([`FUENTES.md`, §2](../../../experiments/slm-directo/corridas/2026-11-06_puntaje-token-2/FUENTES.md#2-detectores-de-estafas-telefónicas);
  fuente relevada, no verificada).

Quién llamó también cambia qué datos es normal que te pidan. Según el manual de Cibercuidados del Gobierno nacional,
los datos personales suelen pedirse cuando es el cliente el que inicia el contacto
([`FUENTES.md`, §1](../../../experiments/slm-directo/corridas/2026-11-06_puntaje-token-2/FUENTES.md#1-estafas-y-llamadas-legítimas-en-argentina);
relevada).

En nuestras corridas se ve lo mismo. Luciano lo notó el 2026-11-05 en v4 con roles, Tito viejo sin indicio y primer
aviso, que da 13 falsas alarmas sobre las 75 legítimas de desarrollo. Según la anotación a ciegas de
[`alcance-desarrollo.json`](../../../experiments/slm-directo/casos/alcance-desarrollo.json), **la persona inició 8 de
esas 13 llamadas**. En 7, el aviso salta cuando la otra parte pide o confirma un dato que identifica a la persona o a
su cuenta: el titular, los últimos cuatro dígitos o el DNI. Seis son consultas al banco y una es para sacar un turno
médico. En la octava, es la persona la que ofrece los últimos números de su tarjeta. En el producto, esas llamadas no
se escuchan. Son corridas de desarrollo, con prompts que todavía están en análisis: muestran dónde caen las falsas
alarmas, no cuánto rinde el detector.

## Decisión

El detector corre solo en **llamadas entrantes de números que no están en la agenda** del teléfono. La app decide si
lo activa según la dirección de la llamada y la agenda. El modelo sigue recibiendo solo la transcripción. Como toda llamada
que escucha cumple la misma condición, el prompt la dice como un dato fijo: «PROTEGIDA recibió esta llamada de un
número que no tiene agendado».

Se mantiene el supuesto de [D05](../../gestion/MAPA-DECISIONES.md#d05--elegir-la-fuente-de-audio-demostrable): el
detector sabe quién habla de cada lado, porque cada canal se captura por separado. El altavoz mezcla las dos voces y
queda como límite.

## Alternativas consideradas

| Alternativa | A favor | En contra | Por qué se descartó |
|---|---|---|---|
| Todas las llamadas, sin agenda ni dirección (D03 del 2026-10-04) | No depende de la agenda ni de la dirección. También escucha la devolución de llamada y al contacto robado | Escucha las consultas que inicia la persona, donde es normal que pidan datos. De ahí salen 8 de las 13 falsas alarmas de v4 con Tito | Las falsas alarmas que más pesan salen de llamadas que el producto no necesita escuchar |
| Todas las llamadas, con la dirección como dato de cada una | El modelo sabe quién llamó y se cubre la devolución de llamada ([ideas pendientes, §0 bis](../../../experiments/slm-directo/corridas/2026-11-06_puntaje-token-2/IDEAS-PENDIENTES.md#0-bis-el-estafador-que-te-hace-llamar-a-vos), opción 3) | Vuelve a meter las consultas legítimas que inicia la persona. En el corpus no hay ninguna estafa saliente (0 de 75) para medirlo | Trae de vuelta las falsas alarmas que el alcance saca, y con este corpus no se puede medir. Queda como trabajo futuro |
| Entrantes de cualquier número, incluidos los agendados | Escucharía al familiar al que le robaron la cuenta de WhatsApp | Escucha a familiares y compañeros, que Google y Samsung excluyen. Contra la suplantación de un contacto, Google usa otra técnica: comprueba que el teléfono del contacto esté llamando ([Fake Call Detection, §5.2](../../investigacion/lecturas/2026-google-scam-detection.md#52-fake-call-detection--verificación-de-identidad-del-llamante)) | Queda fuera del producto de referencia. El contacto robado queda como agujero declarado |

## Consecuencias

- **Cambia D03.** La app pasa a usar la agenda y la dirección, aunque no como entradas del modelo. El historial, la
  memoria entre llamadas y la reputación del número siguen afuera. Hay que actualizar la ficha de D03 en el mapa.
- **El prompt dice el alcance.** El prompt C y `v4-premisa` ya lo hacen
  ([`prompts/README.md`](../../../experiments/slm-directo/prompts/README.md#segunda-vuelta-2026-11-06-alcance-prompt-c-pregunta-al-final-y-lectura-del-token)).
  Decirlo no vuelve sospechoso cualquier pedido de datos. C mantiene la opción (a): que pidan el nombre, el DNI, la
  fecha de nacimiento, una dirección o un correo no vuelve estafa una llamada.
- **Hacen falta legítimas entrantes de números desconocidos, y hay que rehacer la reserva.** El corpus casi no las
  tiene; ver el [ADR 0004](0004-legitimas-entrantes-nuevas-y-test-aparte.md) y
  [#45](https://github.com/Corchets/bitacora_tesis/issues/45).
- **La evaluación principal se hace dentro del alcance.** La cifra principal sale de las llamadas dentro del alcance;
  las que inició la persona se informan aparte.
- **Agujeros declarados,** para el capítulo de limitaciones:
  - **La devolución de llamada.** El estafador corta, o dice «llamame a este número» o «te paso con seguridad, llamá
    al 0800…». A veces el primer contacto es un SMS o un WhatsApp que pide llamar. Cuando la persona llama, la llamada
    es saliente y no se escucha. Pasa lo mismo con el soporte falso que aparece en un buscador.
  - **El contacto robado.** Si le roban la cuenta de WhatsApp a un familiar, la llamada llega como de un contacto
    agendado.
  - **El número del banco falsificado.** Si el estafador falsifica el número de un banco que la persona tiene
    agendado, la llamada aparece como de un contacto.
- **Mitigaciones propuestas, sin implementar**
  ([ideas pendientes, §0 bis](../../../experiments/slm-directo/corridas/2026-11-06_puntaje-token-2/IDEAS-PENDIENTES.md#0-bis-el-estafador-que-te-hace-llamar-a-vos)):
  1. **Avisar en la llamada entrante** cuando piden cortar y llamar a otro número que se dicta, sobre todo si viene con
     un problema urgente. Esto va en el prompt.
  2. **Seguir el número.** Si, en los minutos siguientes a una llamada sospechosa, la persona llama al número que le
     dictaron o a otro desconocido, la app también escucha esa llamada saliente. Es una regla de la app, no del modelo,
     y necesita guardar un dato entre llamadas, algo que D03 deja afuera. Queda como diseño propuesto.
- **Demo:** la llamada por Meet no tiene número ni agenda. Falta decidir cómo se declara el alcance en el panel.

**Para reconsiderarla:** que, con las legítimas entrantes nuevas, el detector dé dentro del alcance tantas falsas
alarmas como afuera, o que una fuente muestre que la devolución de llamada es una modalidad frecuente en Argentina.

## Referencias

- [Lectura de Google Scam Detection](../../investigacion/lecturas/2026-google-scam-detection.md), §5.1 y §5.2.
- [`FUENTES.md` de la segunda vuelta de #143](../../../experiments/slm-directo/corridas/2026-11-06_puntaje-token-2/FUENTES.md),
  §1 y §2.
- [`alcance-desarrollo.json`](../../../experiments/slm-directo/casos/alcance-desarrollo.json): regla, método y conteo de
  la anotación a ciegas. Las 8 de 13 salen de cruzarla con la corrida
  [`2026-11-04_tanda-roles-tito-sin-indicio/d`](../../../experiments/slm-directo/corridas/2026-11-04_tanda-roles-tito-sin-indicio/).
- [Ideas pendientes](../../../experiments/slm-directo/corridas/2026-11-06_puntaje-token-2/IDEAS-PENDIENTES.md), §0 bis
  y §4.
- [ADR 0001](0001-parakeet-filtro-y-gemma4-e2b-con-tito-viejo.md): este ADR no cambia el ASR ni el modelo.
- [#151](https://github.com/Corchets/bitacora_tesis/issues/151): registro de esta decisión y de los sesgos del corpus.
