# ADR 0003 — El detector corre solo en llamadas entrantes de números no agendados

- **Fecha:** 2026-11-06
- **Estado:** propuesta sin discutir
- **Participantes de la discusión:** el equipo, con Mateo Antenucci, en la segunda vuelta de
  [#143](https://github.com/Corchets/bitacora_tesis/issues/143). Al tutor se le explica el 2026-11-11, sin pedirle que
  lo confirme. Se registra en [#151](https://github.com/Corchets/bitacora_tesis/issues/151).
- **Ámbito:** alcance

## Contexto

Hasta ahora el detector escuchaba cualquier llamada, sin saber quién llamó
([D03](../../gestion/MAPA-DECISIONES.md#d03--congelar-alcance-y-contribución)). Los productos comparables no lo hacen.
Scam Detection de Google no se usa en llamadas con contactos
([lectura, §5.1](../../investigacion/lecturas/2026-google-scam-detection.md#51-scam-detection-en-llamadas--análisis-del-contenido)),
y Samsung detecta solo en números no agendados
([`FUENTES.md`, §2](../../../experiments/slm-directo/corridas/2026-11-06_puntaje-token-2/FUENTES.md#2-detectores-de-estafas-telefónicas)).

Cuando la persona llama al banco o pide un turno, es normal que le pidan datos
([`FUENTES.md`, §1](../../../experiments/slm-directo/corridas/2026-11-06_puntaje-token-2/FUENTES.md#1-estafas-y-llamadas-legítimas-en-argentina)).
En una corrida de desarrollo, la persona inició 8 de las 13 llamadas legítimas con falsa alarma. En 7, el aviso salta
cuando la otra parte pide o confirma un dato de la persona
([`alcance-desarrollo.json`](../../../experiments/slm-directo/casos/alcance-desarrollo.json)).

## Decisión

El detector corre solo en llamadas entrantes de números que no están en la agenda. La app decide si lo activa. El
modelo sigue recibiendo solo la transcripción, y el prompt dice el alcance como un dato fijo.

## Alternativas consideradas

| Alternativa | A favor | En contra | Por qué se descartó |
|---|---|---|---|
| Todas las llamadas (D03 del 2026-10-04) | Cubre la devolución de llamada y el contacto robado | Escucha las consultas que inicia la persona, que dan la mayoría de las falsas alarmas | El producto no necesita escucharlas |
| Todas, con la dirección como dato para el modelo | Cubre la devolución de llamada | Vuelve a escuchar esas consultas, y el corpus no tiene estafas salientes para medirlo | No se puede medir. Queda como trabajo futuro |
| Entrantes de cualquier número | Cubre el contacto robado | Escucha a familiares y compañeros, que Google y Samsung excluyen | Google cubre ese caso con otra técnica ([§5.2](../../investigacion/lecturas/2026-google-scam-detection.md#52-fake-call-detection--verificación-de-identidad-del-llamante)) |

## Consecuencias

- Cambia D03: la app usa la agenda y la dirección de la llamada, aunque no como entradas del modelo.
- Hacen falta legítimas entrantes de números desconocidos y hay que rehacer la reserva
  ([ADR 0004](0004-legitimas-entrantes-nuevas-y-test-aparte.md)).
- La cifra principal sale de las llamadas dentro del alcance. El resto se informa aparte.
- **Agujeros declarados:**
  - la devolución de llamada, cuando el estafador hace que la persona llame a otro número;
  - el contacto robado;
  - el número de un banco agendado que se falsifica.

  Las mitigaciones propuestas están en
  [ideas pendientes, §0 bis](../../../experiments/slm-directo/corridas/2026-11-06_puntaje-token-2/IDEAS-PENDIENTES.md#0-bis-el-estafador-que-te-hace-llamar-a-vos).
- La demo por Meet no tiene número ni agenda. Falta decidir cómo se declara ahí el alcance.

**Para reconsiderarla:** que dentro del alcance haya tantas falsas alarmas como afuera, o que una fuente muestre que la
devolución de llamada es frecuente en Argentina.

## Referencias

- [Lectura de Google Scam Detection](../../investigacion/lecturas/2026-google-scam-detection.md), §5.1 y §5.2.
- [`FUENTES.md`](../../../experiments/slm-directo/corridas/2026-11-06_puntaje-token-2/FUENTES.md), §1 y §2.
- [`alcance-desarrollo.json`](../../../experiments/slm-directo/casos/alcance-desarrollo.json), cruzado con la corrida
  [`2026-11-04_tanda-roles-tito-sin-indicio/d`](../../../experiments/slm-directo/corridas/2026-11-04_tanda-roles-tito-sin-indicio/).
