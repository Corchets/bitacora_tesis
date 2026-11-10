# Escenarios de las 94 legítimas de desarrollo

Fecha: 2026-11-09. Lo preparó un agente a pedido de Mateo Antenucci, para decidir antes de la próxima corrida de
[#143](https://github.com/Corchets/bitacora_tesis/issues/143) cómo se cuentan las legítimas repetidas
([`PROPUESTA-SIGUIENTE.md`](../corridas/2026-11-07_alcance-etapa-2/PROPUESTA-SIGUIENTE.md) §3.5, sin commitear).

> **Estado: propuesta sin discutir.** El agrupamiento lo decide el método de #45. Las legítimas las generaron agentes,
> así que no hay un autor que lo confirme: el control es un subagente que no vio resultados (sección «Control a
> ciegas»). Nada de esto cambia `texto/` ni `referencia/`.

## Qué es

Las 94 legítimas de desarrollo (`listas/legitimas-91.txt` y `listas/legitimas-seleccion-3.txt`) no son 94 situaciones
distintas. Hay guiones que vuelven entre lotes: una `LEG2` reescribe una `LEG`, y una `ENT-L` alarga la misma
situación. Si se cuentan como independientes, un mismo guion pesa dos o tres veces en las falsas alarmas.

Un **escenario** es un grupo de llamadas que cuentan la misma situación con otras palabras. Se arma solo con el texto:
nadie miró resultados de detectores para armarlo.

## Método

Es el de #45 ([`TEST-ALCANCE.md`](https://github.com/Corchets/bitacora_tesis/blob/laboratorio-luciano/experiments/slm-directo/casos/TEST-ALCANCE.md)
§2, `test_alcance.py` en `laboratorio-luciano`), copiado sin cambios en
[`corpus_desarrollo.py`](../corpus_desarrollo.py):

- **Dos medidas.** El coseno TF-IDF de palabras sueltas y pares de palabras, y la **cobertura**: la parte de los
  bigramas de una llamada, pesados por IDF, que reaparece en otra. La cobertura detecta una reescritura alargada aunque
  el coseno baje.
- **Umbrales calibrados** con las 15 `LEG2` que, según sus notas, reescriben una `LEG`: el mínimo de esas 15 parejas.
  Dan coseno **0,347** y cobertura **0,246**, los mismos de #45.
- **Enlace:** dos llamadas se enlazan si superan cualquiera de los dos umbrales (la cobertura, en cualquier sentido).
- **Escenario:** cada componente conexa de esos enlaces. Es un agrupamiento por cadena: si A se parece a B y B a C,
  A y C quedan juntas aunque no se parezcan entre sí. Esos grupos van marcados como **encadenados**.

Se reproduce con `python -I corpus_desarrollo.py escenarios`, que reescribe la tabla de abajo y
[`escenarios-legitimas.json`](escenarios-legitimas.json). Los textos son los mismos que usó #45 (revisión `ac8a81f`);
su huella está en el JSON.

## Resultado

**47 escenarios:** 15 tríos, 17 pares y 15 llamadas sueltas.

- **Las 15 reescrituras declaradas quedan cada una en su escenario**, como debe ser con umbrales mínimos.
- **Los 15 tríos son todos una `LEG`, una `LEG2` y una `ENT-L`.** Casi siempre llevan el mismo número
  (`LEG-BA-02`, `LEG2-BA-02`, `ENT-L-BANCO-002`), aunque solo la `LEG2` lo declara.
- **Los 17 pares:** 11 son una `ENT-L` con una `LEG2`, 5 una `ENT-L` con una `LEG` y uno es `LEG-CO-01` con su
  reescritura declarada.
- **Sueltas:** 14 `ENT-L` (incluidas las 3 de selección de personal) y `LEG2-ST-05`.
- **Las 21 `LEG` y 27 de las 28 `LEG2` tienen una `ENT-L` o una `LEG2` en su escenario.** De las 45 `ENT-L`, 31
  están en un grupo. #45 había visto lo mismo: 31 de las 42 `ENT-L` se parecen a una `LEG` o `LEG2` tanto como las
  reescrituras declaradas.
- **El guion de TecnoFix es el escenario E11**: `LEG-ST-03`, `LEG2-ST-03` y `ENT-L-SOPORTE-003`.

**Los grupos están bien separados.** Entre llamadas de escenarios distintos, solo dos pares llegan al 75 % de algún
umbral: `LEG2-TU-06` con `LEG2-VE-04` (coseno 0,235; cobertura 0,216) y `ENT-L-DELIVERY-001` con `LEG2-CO-01`
(0,155; 0,188). Por eso el número casi no depende del umbral:

<!-- sensibilidad:inicio -->
| Umbrales | Coseno | Cobertura | Escenarios |
|---|---:|---:|---:|
| calibrados (mínimo de las reescrituras) | 0,347 | 0,246 | 47 |
| solo coseno | 0,347 | — | 55 |
| solo cobertura | — | 0,246 | 47 |
| percentil 25 de las reescrituras | 0,472 | 0,388 | 56 |
| mediana de las reescrituras | 0,523 | 0,450 | 59 |
<!-- sensibilidad:fin -->

Con umbrales más exigentes, los tríos encadenados se parten y aparecen más escenarios. La exploración de la etapa 2
(`exploracion-salida.md` §6, sin commitear) había dado «unos 56, entre 45 y 75» con otra medida, más gruesa.

**Por familia** (un escenario que mezcla familias cuenta en las dos):

| Familia | Llamadas | Escenarios |
|---|---:|---:|
| banco | 13 | 6 |
| comercial | 26 | 12 |
| delivery | 13 | 7 |
| encuesta | 13 | 6 |
| médico | 11 | 5 |
| soporte | 13 | 7 |
| trámite | 2 | 2 |
| trabajo (selección de personal) | 3 | 3 |

## Puntos débiles del agrupamiento

1. **Tres tríos encadenados:** E01 (`ENT-L-BANCO-001`), E10 (`ENT-L-SOPORTE-002`) y E13 (`ENT-L-VENTAS-004`). En los
   tres, la `ENT-L` se une por su parecido con la `LEG2` y no llega a ningún umbral con la `LEG` (coseno 0,20 a 0,24).
   En E13, además, la `LEG2` llega a la `LEG` solo por la cobertura (0,266) y llevan números distintos
   (`LEG-CC-02` y `LEG2-CC-04`).
2. **E25 mezcla familias:** `ENT-L-TRAMITE-002` (trámite) y `LEG2-TU-06` (médico), con coseno 0,503 y cobertura 0,655.
   Por el texto es el mismo guion; la familia distinta puede ser un error de la referencia.
3. **Los dos pares cercanos** de arriba, que el método deja separados.

## Control a ciegas

Un subagente que no vio `case_id`, referencia, dudosas ni resultados leyó las 94 llamadas agrupadas como las deja el
método, con nombres neutros. Respondió, para cada grupo, si es la misma situación y qué escenarios uniría. Su
respuesta, con los `case_id` ya repuestos, está en [`escenarios-control.json`](escenarios-control.json).

- **En los 32 grupos reconoce el mismo guion:** la misma entidad, el mismo motivo y el mismo desenlace.
- **Separaría 15, casi todos por la misma razón: la reescritura agrega un pedido de datos que el original no tiene.**
  En 11 grupos, la `LEG` no pide nada y la `LEG2` o la `ENT-L` piden el DNI, el domicilio, el número de afiliado o el mail (E01,
  E02, E03, E08, E10, E12, E14, E15, E21, E23 y E27). En E11, el guion de TecnoFix, separa las tres: la `LEG` no pide
  datos, la `LEG2` pide el DNI y la `ENT-L` además vende un cargador. En E06 y E20 la versión larga agrega un reclamo,
  y en E28 una seña por transferencia.
- **Uniría E32 con E35:** `LEG-CO-01` y `LEG2-CO-01` con `ENT-L-DELIVERY-001`, el correo que llama antes de llegar. Es
  uno de los dos pares cercanos que el método deja afuera.

**Qué se hace con esto.** El agrupamiento sigue siendo el del método: la tabla y las vistas por escenario usan los 47.
El control confirma que lo que el método junta es el mismo guion. Además muestra que **el generador, al reescribir,
agrega pedidos de datos**: es el mismo sesgo del DNI que ya marcaba #45, ahora caso por caso. Con la división del
control salen 62 escenarios. Están en el JSON (`escenario_control`) y se usan solo como sensibilidad en las
[cifras](CIFRAS-LIMPIEZA-DESARROLLO.md).

## Cómo se usa

**Decidido por Mateo el 2026-11-09:** para la etapa 3 de #143 cuenta **una legítima por escenario**, sin las 7
dudosas. Por defecto es la `ENT-L`. La regla y la lista de 45 están en
[`MANIFIESTO-DESARROLLO.md`](MANIFIESTO-DESARROLLO.md) y en `listas/legitimas-escenarios-45.txt`. No se borra ningún
caso.

- Las cifras de la etapa 2 por escenario están en [`CIFRAS-LIMPIEZA-DESARROLLO.md`](CIFRAS-LIMPIEZA-DESARROLLO.md), como
  exploración.
- **Para generar legítimas nuevas:** un escenario no se reescribe en otro lote. #45 ya lo controla para el test.

## Tabla caso → escenario

La columna «Más parecido» da el vecino con mayor coseno y, si es otro, el de mayor cobertura. «Situación» es el campo
`situacion` de la referencia. «Control» es lo que dijo el subagente del grupo de esa fila.

<!-- tabla:inicio -->
| Escenario | Caso | Familia | Tipo | Líneas | Más parecido (coseno · cobertura) | Marcas | Situación (referencia) | Control |
|---|---|---|---|---:|---|---|---|---|
| E01 (3) | `ENT-L-BANCO-001` | banco | pedido_razonable | 24 | `LEG2-BA-01` 0,412 · 0,490 | mismo número que `LEG-BA-01`, `LEG2-BA-01`; **grupo encadenado** | Prevención de fraudes llama por un intento de compra online que el cliente no hizo, valida identidad con DNI y fecha de nacimiento, bloquea la tarjeta y avisa de un SMS para reactivar la app. | separar: `LEG-BA-01` / `ENT-L-BANCO-001`, `LEG2-BA-01` |
| E01 (3) | `LEG-BA-01` | banco | mencion_sin_pedido | 13 | `LEG2-BA-01` 0,383 · 0,387 | reescritura declarada de/por `LEG2-BA-01`; mismo número que `ENT-L-BANCO-001`, `LEG2-BA-01`; **grupo encadenado** | Prevención de fraudes del banco consulta por una compra que el cliente no reconoce y bloquea la tarjeta. | separar: `LEG-BA-01` / `ENT-L-BANCO-001`, `LEG2-BA-01` |
| E01 (3) | `LEG2-BA-01` | banco | mencion_sin_pedido | 12 | `ENT-L-BANCO-001` 0,412 · 0,490 | reescritura declarada de/por `LEG-BA-01`; mismo número que `ENT-L-BANCO-001`, `LEG-BA-01`; **grupo encadenado** | Prevención de fraudes valida identidad con DNI y fecha de nacimiento y bloquea la tarjeta. | separar: `LEG-BA-01` / `ENT-L-BANCO-001`, `LEG2-BA-01` |
| E02 (3) | `ENT-L-BANCO-002` | banco | pedido_razonable | 23 | `LEG2-BA-02` 0,447 · 0,497 | mismo número que `LEG-BA-02`, `LEG2-BA-02` | Seguridad del banco llama por accesos desde un dispositivo nuevo; la clienta se niega a dar el DNI y la operadora le pide que corte y llame al número oficial. | separar: `LEG2-BA-02`, `ENT-L-BANCO-002` / `LEG-BA-02` |
| E02 (3) | `LEG-BA-02` | banco | mencion_sin_pedido | 9 | `LEG2-BA-02` 0,593 · 0,564 | reescritura declarada de/por `LEG2-BA-02`; mismo número que `ENT-L-BANCO-002`, `LEG2-BA-02` | El banco llama por movimientos raros; el cliente desconfía y la operadora le pide que corte y llame al número oficial. | separar: `LEG2-BA-02`, `ENT-L-BANCO-002` / `LEG-BA-02` |
| E02 (3) | `LEG2-BA-02` | banco | mencion_sin_pedido | 10 | `LEG-BA-02` 0,593 · 0,564 | reescritura declarada de/por `LEG-BA-02`; mismo número que `ENT-L-BANCO-002`, `LEG-BA-02` | El banco pide el DNI, el cliente desconfía y la operadora le pide que corte y llame al número oficial. | separar: `LEG2-BA-02`, `ENT-L-BANCO-002` / `LEG-BA-02` |
| E03 (3) | `ENT-L-BANCO-003` | banco | pedido_razonable | 21 | `LEG2-BA-03` 0,303 · 0,341 | mismo número que `LEG-BA-03`, `LEG2-BA-03` | El banco consulta a un cliente mayor por una compra en el exterior que sí hizo; pide nombre completo y los últimos números del DNI y le explica cómo avisar viajes. | separar: `LEG-BA-03` / `ENT-L-BANCO-003`, `LEG2-BA-03` |
| E03 (3) | `LEG-BA-03` | banco | mencion_sin_pedido | 9 | `LEG2-BA-03` 0,580 · 0,507 | reescritura declarada de/por `LEG2-BA-03`; mismo número que `ENT-L-BANCO-003`, `LEG2-BA-03` | El banco consulta por una compra en el exterior que el cliente sí reconoce. | separar: `LEG-BA-03` / `ENT-L-BANCO-003`, `LEG2-BA-03` |
| E03 (3) | `LEG2-BA-03` | banco | pedido_razonable | 12 | `LEG-BA-03` 0,580 · 0,507 | reescritura declarada de/por `LEG-BA-03`; mismo número que `ENT-L-BANCO-003`, `LEG-BA-03` | El banco consulta por una compra en el exterior que el cliente reconoce, con validación de nombre y DNI. | separar: `LEG-BA-03` / `ENT-L-BANCO-003`, `LEG2-BA-03` |
| E04 (3) | `ENT-L-DELIVERY-002` | delivery | pedido_razonable | 20 | `LEG2-CO-02` 0,469 · 0,545 | mismo número que `LEG-CO-02`, `LEG2-CO-02` | Nadie atiende en el edificio y el repartidor coordina dejar el paquete con el encargado; pide nombre y DNI de quien lo recibe. | misma situación |
| E04 (3) | `LEG-CO-02` | delivery | cotidiana | 9 | `LEG2-CO-02` 0,523 · 0,465 | reescritura declarada de/por `LEG2-CO-02`; mismo número que `ENT-L-DELIVERY-002`, `LEG2-CO-02` | Repartidor llama, el destinatario no está y coordina dejarlo con el portero. | misma situación |
| E04 (3) | `LEG2-CO-02` | delivery | pedido_razonable | 10 | `LEG-CO-02` 0,523 · `ENT-L-DELIVERY-002` 0,545 | reescritura declarada de/por `LEG-CO-02`; mismo número que `ENT-L-DELIVERY-002`, `LEG-CO-02` | El destinatario no está y el repartidor pide nombre y DNI de quien va a recibir. | misma situación |
| E05 (3) | `ENT-L-DELIVERY-003` | delivery | cotidiana | 21 | `LEG2-CO-03` 0,346 · 0,458 | mismo número que `LEG-CO-03`, `LEG2-CO-03` | El repartidor no encuentra el número de la casa y pide referencias; la destinataria le explica el pasillo y pregunta si hay algo que pagar. | misma situación |
| E05 (3) | `LEG-CO-03` | delivery | cotidiana | 7 | `LEG2-CO-03` 0,603 · 0,569 | reescritura declarada de/por `LEG2-CO-03`; mismo número que `ENT-L-DELIVERY-003`, `LEG2-CO-03` | Repartidor no encuentra la dirección y pide referencias. | misma situación |
| E05 (3) | `LEG2-CO-03` | delivery | pedido_razonable | 10 | `LEG-CO-03` 0,603 · 0,569 | reescritura declarada de/por `LEG-CO-03`; mismo número que `ENT-L-DELIVERY-003`, `LEG-CO-03` | Repartidor no encuentra la dirección y pide referencias. | misma situación |
| E06 (3) | `ENT-L-ENCUESTA-001` | encuesta | cotidiana | 21 | `LEG2-EN-01` 0,442 · 0,585 | mismo número que `LEG-EN-01`, `LEG2-EN-01` | Una encuesta de satisfacción después de una visita técnica; el cliente califica la atención, se queja de la demora y pide que no lo vuelvan a encuestar. | separar: `LEG-EN-01`, `LEG2-EN-01` / `ENT-L-ENCUESTA-001` |
| E06 (3) | `LEG-EN-01` | encuesta | cotidiana | 11 | `LEG2-EN-01` 0,633 · 0,656 | reescritura declarada de/por `LEG2-EN-01`; mismo número que `ENT-L-ENCUESTA-001`, `LEG2-EN-01` | Encuesta de satisfacción después de una visita técnica. | separar: `LEG-EN-01`, `LEG2-EN-01` / `ENT-L-ENCUESTA-001` |
| E06 (3) | `LEG2-EN-01` | encuesta | cotidiana | 12 | `LEG-EN-01` 0,633 · 0,656 | reescritura declarada de/por `LEG-EN-01`; mismo número que `ENT-L-ENCUESTA-001`, `LEG-EN-01` | Encuesta de satisfacción después de una visita técnica, confirmando el nombre del cliente. | separar: `LEG-EN-01`, `LEG2-EN-01` / `ENT-L-ENCUESTA-001` |
| E07 (3) | `ENT-L-ENCUESTA-003` | encuesta | cotidiana | 14 | `LEG2-EN-03` 0,342 · 0,491 | mismo número que `LEG-EN-03`, `LEG2-EN-03` | Una encuestadora de consumo llama a un conductor que no puede hablar; él le pregunta de dónde sacaron su número y ella ofrece no volver a llamarlo. | misma situación |
| E07 (3) | `LEG-EN-03` | encuesta | cotidiana | 5 | `LEG2-EN-03` 0,666 · 0,677 | reescritura declarada de/por `LEG2-EN-03`; mismo número que `ENT-L-ENCUESTA-003`, `LEG2-EN-03` | Encuesta de consumo; el receptor no quiere participar. | misma situación |
| E07 (3) | `LEG2-EN-03` | encuesta | cotidiana | 8 | `LEG-EN-03` 0,666 · 0,677 | reescritura declarada de/por `LEG-EN-03`; mismo número que `ENT-L-ENCUESTA-003`, `LEG-EN-03` | Encuesta de consumo; el receptor no puede y pide que no lo llamen. | misma situación |
| E08 (3) | `ENT-L-MEDICO-001` | medico | pedido_razonable | 21 | `LEG2-TU-01` 0,457 · 0,643 | mismo número que `LEG-TU-01`, `LEG2-TU-01` | El centro médico confirma un turno con dermatología y pide DNI, obra social y número de afiliado para la admisión. | separar: `LEG2-TU-01`, `ENT-L-MEDICO-001` / `LEG-TU-01` |
| E08 (3) | `LEG-TU-01` | medico | cotidiana | 9 | `LEG2-TU-01` 0,508 · `ENT-L-MEDICO-001` 0,483 | reescritura declarada de/por `LEG2-TU-01`; mismo número que `ENT-L-MEDICO-001`, `LEG2-TU-01` | Centro médico confirma un turno con especialista. | separar: `LEG2-TU-01`, `ENT-L-MEDICO-001` / `LEG-TU-01` |
| E08 (3) | `LEG2-TU-01` | medico | pedido_razonable | 10 | `LEG-TU-01` 0,508 · `ENT-L-MEDICO-001` 0,643 | reescritura declarada de/por `LEG-TU-01`; mismo número que `ENT-L-MEDICO-001`, `LEG-TU-01` | Centro médico confirma un turno y valida DNI y obra social. | separar: `LEG2-TU-01`, `ENT-L-MEDICO-001` / `LEG-TU-01` |
| E09 (3) | `ENT-L-MEDICO-002` | medico | cotidiana | 22 | `LEG2-TU-02` 0,424 · 0,639 | mismo número que `LEG-TU-02`, `LEG2-TU-02` | El consultorio odontológico llama para reprogramar un turno por un imprevisto de la doctora y negocia un nuevo horario con la paciente. | misma situación |
| E09 (3) | `LEG-TU-02` | medico | cotidiana | 10 | `LEG2-TU-02` 0,749 · 0,753 | reescritura declarada de/por `LEG2-TU-02`; mismo número que `ENT-L-MEDICO-002`, `LEG2-TU-02` | Consultorio odontológico necesita reprogramar un turno. | misma situación |
| E09 (3) | `LEG2-TU-02` | medico | cotidiana | 10 | `LEG-TU-02` 0,749 · 0,753 | reescritura declarada de/por `LEG-TU-02`; mismo número que `ENT-L-MEDICO-002`, `LEG-TU-02` | Consultorio odontológico reprograma un turno. | misma situación |
| E10 (3) | `ENT-L-SOPORTE-002` | soporte | pedido_razonable | 22 | `LEG2-ST-02` 0,445 · 0,542 | mismo número que `LEG-ST-02`, `LEG2-ST-02`; **grupo encadenado** | El service oficial de electrodomésticos llama por una orden de lavarropas en garantía, pide el DNI que figura en la factura, confirma el domicilio y negocia el horario de la visita. | separar: `LEG2-ST-02`, `ENT-L-SOPORTE-002` / `LEG-ST-02` |
| E10 (3) | `LEG-ST-02` | soporte | pedido_razonable | 11 | `LEG2-ST-02` 0,498 · 0,454 | reescritura declarada de/por `LEG2-ST-02`; mismo número que `ENT-L-SOPORTE-002`, `LEG2-ST-02`; **grupo encadenado** | Service oficial de electrodomésticos coordina visita por un lavarropas en garantía. | separar: `LEG2-ST-02`, `ENT-L-SOPORTE-002` / `LEG-ST-02` |
| E10 (3) | `LEG2-ST-02` | soporte | pedido_razonable | 12 | `LEG-ST-02` 0,498 · `ENT-L-SOPORTE-002` 0,542 | reescritura declarada de/por `LEG-ST-02`; mismo número que `ENT-L-SOPORTE-002`, `LEG-ST-02`; **grupo encadenado** | Service oficial de electrodomésticos valida la garantía con DNI y dirección. | separar: `LEG2-ST-02`, `ENT-L-SOPORTE-002` / `LEG-ST-02` |
| E11 (3) | `ENT-L-SOPORTE-003` | soporte | pedido_razonable | 23 | `LEG2-ST-03` 0,379 · 0,545 | mismo número que `LEG-ST-03`, `LEG2-ST-03` | El local de reparación avisa que la notebook está lista, confirma el documento de quien la dejó y pide autorización para cambiar un cargador que también falla, con un costo extra. | separar: `LEG-ST-03` / `LEG2-ST-03` / `ENT-L-SOPORTE-003` |
| E11 (3) | `LEG-ST-03` | soporte | mencion_sin_pedido | 8 | `LEG2-ST-03` 0,472 · `ENT-L-SOPORTE-003` 0,506 | reescritura declarada de/por `LEG2-ST-03`; mismo número que `ENT-L-SOPORTE-003`, `LEG2-ST-03` | Local de reparación avisa que la notebook que el cliente dejó ya está lista. | separar: `LEG-ST-03` / `LEG2-ST-03` / `ENT-L-SOPORTE-003` |
| E11 (3) | `LEG2-ST-03` | soporte | mencion_sin_pedido | 10 | `LEG-ST-03` 0,472 · `ENT-L-SOPORTE-003` 0,545 | reescritura declarada de/por `LEG-ST-03`; mismo número que `ENT-L-SOPORTE-003`, `LEG-ST-03` | Local de reparación avisa que la notebook está lista y pide el DNI para retirarla. | separar: `LEG-ST-03` / `LEG2-ST-03` / `ENT-L-SOPORTE-003` |
| E12 (3) | `ENT-L-VENTAS-001` | comercial | pedido_razonable | 27 | `LEG2-CC-01` 0,446 · 0,491 | mismo número que `LEG-CC-01`, `LEG2-CC-01` | Una operadora móvil ofrece a una clienta pasar a un plan más grande y lo da de alta en la llamada, validando DNI y mail; la clienta negocia el precio y el alta se acepta con un SMS que ella carga en la app. | separar: `ENT-L-VENTAS-001`, `LEG2-CC-01` / `LEG-CC-01` |
| E12 (3) | `LEG-CC-01` | comercial | cotidiana | 12 | `LEG2-CC-01` 0,351 · 0,298 | reescritura declarada de/por `LEG2-CC-01`; mismo número que `ENT-L-VENTAS-001`, `LEG2-CC-01` | Operadora de telefonía móvil ofrece upgrade de plan a cliente existente. | separar: `ENT-L-VENTAS-001`, `LEG2-CC-01` / `LEG-CC-01` |
| E12 (3) | `LEG2-CC-01` | comercial | mencion_sin_pedido | 14 | `ENT-L-VENTAS-001` 0,446 · 0,491 | reescritura declarada de/por `LEG-CC-01`; mismo número que `ENT-L-VENTAS-001`, `LEG-CC-01` | Operadora móvil ofrece upgrade de plan y lo da de alta en la llamada, validando DNI. | separar: `ENT-L-VENTAS-001`, `LEG2-CC-01` / `LEG-CC-01` |
| E13 (3) | `ENT-L-VENTAS-004` | comercial | cotidiana | 23 | `LEG2-CC-04` 0,326 · 0,421 | mismo número que `LEG2-CC-04`; **grupo encadenado** | Un agente de telefonía confirma el nombre del titular para ofrecerle internet; el titular corta la oferta y pide salir de la base. | misma situación |
| E13 (3) | `LEG-CC-02` | comercial | cotidiana | 9 | `LEG2-CC-04` 0,332 · 0,318 | **grupo encadenado** | Empresa de fibra óptica ofrece servicio nuevo en el barrio; el receptor rechaza y pide no ser llamado. | misma situación |
| E13 (3) | `LEG2-CC-04` | comercial | cotidiana | 10 | `LEG-CC-02` 0,332 · `ENT-L-VENTAS-004` 0,421 | mismo número que `ENT-L-VENTAS-004`; **grupo encadenado** | Agente de telefonía confirma titular y el receptor pide que no lo llamen más. | misma situación |
| E14 (3) | `ENT-L-VENTAS-006` | comercial | mencion_sin_pedido | 24 | `LEG2-CC-06` 0,466 · 0,582 | mismo número que `LEG2-CC-06` | Un vendedor de TV por cable ofrece un pack con descuento, insiste con que vence el viernes, la clienta desconfía y él le da un código de referencia y la manda al 0800. | separar: `LEG2-CC-06`, `ENT-L-VENTAS-006` / `LEG-CC-03` |
| E14 (3) | `LEG-CC-03` | comercial | cotidiana | 12 | `LEG2-CC-06` 0,378 · 0,371 | reescritura declarada de/por `LEG2-CC-06` | Vendedor de TV por cable algo insistente; el receptor desconfía y el vendedor lo deriva al canal oficial. | separar: `LEG2-CC-06`, `ENT-L-VENTAS-006` / `LEG-CC-03` |
| E14 (3) | `LEG2-CC-06` | comercial | mencion_sin_pedido | 12 | `ENT-L-VENTAS-006` 0,466 · 0,582 | reescritura declarada de/por `LEG-CC-03`; mismo número que `ENT-L-VENTAS-006` | Vendedor de TV insistente; el receptor desconfía y el vendedor da número de referencia y lo deriva al 0800. | separar: `LEG2-CC-06`, `ENT-L-VENTAS-006` / `LEG-CC-03` |
| E15 (3) | `ENT-L-VENTAS-007` | comercial | pedido_razonable | 27 | `LEG2-VE-01` 0,449 · 0,593 |  | Una concesionaria hace el seguimiento de una consulta web por una pick-up, precalifica el crédito con DNI e ingresos aproximados y manda la cotización por mail. | separar: `ENT-L-VENTAS-007`, `LEG2-VE-01` / `LEG-VE-01` |
| E15 (3) | `LEG-VE-01` | comercial | cotidiana | 12 | `LEG2-VE-01` 0,347 · 0,323 | reescritura declarada de/por `LEG2-VE-01`; mismo número que `LEG2-VE-01` | Concesionaria hace seguimiento a una consulta que el cliente dejó en la web. | separar: `ENT-L-VENTAS-007`, `LEG2-VE-01` / `LEG-VE-01` |
| E15 (3) | `LEG2-VE-01` | comercial | pedido_razonable | 12 | `ENT-L-VENTAS-007` 0,449 · 0,593 | reescritura declarada de/por `LEG-VE-01`; mismo número que `LEG-VE-01` | Concesionaria hace seguimiento de una consulta web y ofrece precalificar el crédito con el DNI. | separar: `ENT-L-VENTAS-007`, `LEG2-VE-01` / `LEG-VE-01` |
| E16 (2) | `ENT-L-BANCO-005` | banco | pedido_razonable | 22 | `LEG2-BA-05` 0,355 · 0,437 | mismo número que `LEG2-BA-05` | La tarjeta de débito de un cliente se usó en un cajero de otra provincia; el banco valida documento, la bloquea y confirma la dirección para mandar la reposición. | misma situación |
| E16 (2) | `LEG2-BA-05` | banco | pedido_razonable | 12 | `ENT-L-BANCO-005` 0,355 · 0,437 | mismo número que `ENT-L-BANCO-005` | El banco detecta uso de la tarjeta en otra provincia y confirma la dirección para enviar la reposición. | misma situación |
| E17 (2) | `ENT-L-DELIVERY-006` | delivery | pedido_razonable | 26 | `LEG2-CO-06` 0,372 · 0,496 | mismo número que `LEG2-CO-06` | El flete de una mueblería coordina la entrega de un placard, confirma dirección, piso y ascensor, y pide nombre y DNI del hermano que lo va a recibir. | misma situación |
| E17 (2) | `LEG2-CO-06` | delivery | pedido_razonable | 12 | `ENT-L-DELIVERY-006` 0,372 · 0,496 | mismo número que `ENT-L-DELIVERY-006` | Flete de una mueblería coordina la entrega y pide datos de quien recibe. | misma situación |
| E18 (2) | `ENT-L-ENCUESTA-002` | encuesta | pedido_razonable | 36 | `LEG-EN-02` 0,469 · 0,531 | mismo número que `LEG-EN-02` | Una consultora hace una encuesta anónima sobre transporte público; pide rango de edad, barrio y ocupación, y la persona pregunta para qué son los datos. | misma situación |
| E18 (2) | `LEG-EN-02` | encuesta | pedido_razonable | 16 | `ENT-L-ENCUESTA-002` 0,469 · 0,531 | mismo número que `ENT-L-ENCUESTA-002` | Consultora hace una encuesta anónima sobre transporte público. | misma situación |
| E19 (2) | `ENT-L-ENCUESTA-004` | encuesta | mencion_sin_pedido | 21 | `LEG2-EN-04` 0,619 · 0,720 | mismo número que `LEG2-EN-04` | La obra social hace una encuesta de atención a una afiliada, valida con el documento y le menciona un código para completar una encuesta más larga en la web. | misma situación |
| E19 (2) | `LEG2-EN-04` | encuesta | mencion_sin_pedido | 12 | `ENT-L-ENCUESTA-004` 0,619 · 0,720 | mismo número que `ENT-L-ENCUESTA-004` | Obra social hace una encuesta de atención y valida al afiliado con el DNI. | misma situación |
| E20 (2) | `ENT-L-ENCUESTA-005` | encuesta | pedido_razonable | 21 | `LEG2-EN-05` 0,535 · 0,691 | mismo número que `LEG2-EN-05` | La municipalidad hace una encuesta sobre la recolección de residuos, pide calle y altura para ubicar la zona y anota un reclamo por bolsas rotas. | separar: `LEG2-EN-05` / `ENT-L-ENCUESTA-005` |
| E20 (2) | `LEG2-EN-05` | encuesta | pedido_razonable | 12 | `ENT-L-ENCUESTA-005` 0,535 · 0,691 | mismo número que `ENT-L-ENCUESTA-005` | La municipalidad encuesta sobre la recolección de residuos y pide la calle y altura. | separar: `LEG2-EN-05` / `ENT-L-ENCUESTA-005` |
| E21 (2) | `ENT-L-MEDICO-003` | medico | mencion_sin_pedido | 20 | `LEG-TU-03` 0,430 · 0,435 | mismo número que `LEG-TU-03` | El laboratorio confirma un turno de extracción, valida el documento, recuerda el ayuno y le dice al paciente su número de turno. | separar: `LEG-TU-03` / `ENT-L-MEDICO-003` |
| E21 (2) | `LEG-TU-03` | medico | cotidiana | 9 | `ENT-L-MEDICO-003` 0,430 · 0,435 | mismo número que `ENT-L-MEDICO-003` | Laboratorio de análisis clínicos confirma turno y recuerda el ayuno. | separar: `LEG-TU-03` / `ENT-L-MEDICO-003` |
| E22 (2) | `ENT-L-MEDICO-004` | medico | cotidiana | 20 | `LEG2-TU-05` 0,447 · 0,729 |  | La veterinaria recuerda el turno de la vacuna antirrábica del perro y la dueña pregunta por el costo y el ayuno. | misma situación |
| E22 (2) | `LEG2-TU-05` | medico | cotidiana | 8 | `ENT-L-MEDICO-004` 0,447 · 0,729 |  | Veterinaria recuerda el turno de vacunación de la mascota. | misma situación |
| E23 (2) | `ENT-L-SOPORTE-001` | soporte | mencion_sin_pedido | 26 | `LEG-ST-01` 0,332 · 0,339 | mismo número que `LEG-ST-01` | El soporte del proveedor de internet llama por un reclamo de falta de servicio, valida al titular, diagnostica el módem por teléfono, agenda un técnico y da un código de visita para reconocerlo. | separar: `LEG-ST-01` / `ENT-L-SOPORTE-001` |
| E23 (2) | `LEG-ST-01` | soporte | cotidiana | 13 | `ENT-L-SOPORTE-001` 0,332 · 0,339 | mismo número que `ENT-L-SOPORTE-001` | Soporte del proveedor de internet llama por un reclamo que el cliente hizo y agenda un técnico. | separar: `LEG-ST-01` / `ENT-L-SOPORTE-001` |
| E24 (2) | `ENT-L-SOPORTE-004` | soporte | pedido_razonable | 20 | `LEG2-ST-04` 0,575 · 0,742 | mismo número que `LEG2-ST-04` | La empresa de aire acondicionado coordina la instalación de un split comprado, pide dirección completa, piso, entre calles y si hay balcón. | misma situación |
| E24 (2) | `LEG2-ST-04` | soporte | pedido_razonable | 12 | `ENT-L-SOPORTE-004` 0,575 · 0,742 | mismo número que `ENT-L-SOPORTE-004` | Empresa de aire acondicionado confirma dirección, piso y entre calles para la instalación. | misma situación |
| E25 (2) | `ENT-L-TRAMITE-002` | tramite | pedido_razonable | 20 | `LEG2-TU-06` 0,503 · 0,655 | **mezcla familias** | El centro de licencias de conducir confirma un turno de renovación, valida DNI y fecha de nacimiento y le recuerda los requisitos y el pago en el centro. | misma situación |
| E25 (2) | `LEG2-TU-06` | medico | pedido_razonable | 10 | `ENT-L-TRAMITE-002` 0,503 · 0,655 | **mezcla familias** | Centro de licencias de conducir confirma el turno con DNI y fecha de nacimiento. | misma situación |
| E26 (2) | `ENT-L-VENTAS-005` | comercial | mencion_sin_pedido | 25 | `LEG2-CC-05` 0,430 · 0,561 | mismo número que `LEG2-CC-05` | Una nueva operadora llama para terminar una portabilidad que el cliente empezó en la web; valida DNI y mail y le explica que el PIN de portabilidad lo carga él, no se lo dicta al agente. | misma situación |
| E26 (2) | `LEG2-CC-05` | comercial | mencion_sin_pedido | 12 | `ENT-L-VENTAS-005` 0,430 · 0,561 | mismo número que `ENT-L-VENTAS-005` | Nueva operadora ofrece portabilidad y explica que el PIN lo carga el cliente en la web. | misma situación |
| E27 (2) | `ENT-L-VENTAS-008` | comercial | pedido_razonable | 20 | `LEG-VE-02` 0,325 · 0,319 |  | Una vendedora de planes de ahorro llama en frío, insiste dos veces con los cupos del mes y pide nombre y DNI para reservar uno; la persona se niega y la vendedora la invita a la oficina. | separar: `LEG-VE-02` / `ENT-L-VENTAS-008` |
| E27 (2) | `LEG-VE-02` | comercial | cotidiana | 9 | `ENT-L-VENTAS-008` 0,325 · 0,319 |  | Vendedor de plan de ahorro llama en frío; el receptor no está interesado. | separar: `LEG-VE-02` / `ENT-L-VENTAS-008` |
| E28 (2) | `ENT-L-VENTAS-009` | comercial | pedido_razonable | 32 | `LEG-VE-03` 0,269 · 0,305 |  | El vendedor llama con la tasación del usado de un cliente, confirma patente y kilometraje, negocia el valor y le ofrece congelar el precio con una seña transferida a la cuenta de la concesionaria contra factura. | separar: `LEG-VE-03` / `ENT-L-VENTAS-009` |
| E28 (2) | `LEG-VE-03` | comercial | mencion_sin_pedido | 9 | `ENT-L-VENTAS-009` 0,269 · 0,305 |  | Vendedor llama para pasar la tasación del usado y la cotización del auto que el cliente fue a ver. | separar: `LEG-VE-03` / `ENT-L-VENTAS-009` |
| E29 (2) | `ENT-L-VENTAS-010` | comercial | mencion_sin_pedido | 26 | `LEG2-VE-04` 0,439 · 0,528 |  | Una concesionaria de motos avisa que llegó la moto reservada, confirma DNI y domicilio para el patentamiento y le recuerda el código de reserva que ya le mandaron. | misma situación |
| E29 (2) | `LEG2-VE-04` | comercial | mencion_sin_pedido | 12 | `ENT-L-VENTAS-010` 0,439 · 0,528 |  | Concesionaria de motos confirma datos para el patentamiento y la entrega de la moto reservada. | misma situación |
| E30 (2) | `ENT-L-VENTAS-011` | comercial | cotidiana | 21 | `LEG2-VE-05` 0,491 · 0,613 |  | Una agencia de usados avisa a un cliente que entró un sedán parecido al que buscaba, le pregunta la zona y le ofrece llevárselo para probar. | misma situación |
| E30 (2) | `LEG2-VE-05` | comercial | pedido_razonable | 10 | `ENT-L-VENTAS-011` 0,491 · 0,613 |  | Agencia de usados avisa que entró un auto parecido al que el cliente buscaba. | misma situación |
| E31 (2) | `ENT-L-VENTAS-012` | comercial | cotidiana | 16 | `LEG2-VE-06` 0,599 · 0,798 |  | Una vendedora llama a un cliente que pidió el folleto de un SUV en un stand del shopping y confirma el mail; el cliente está en una reunión y la corta enseguida. | misma situación |
| E31 (2) | `LEG2-VE-06` | comercial | pedido_razonable | 7 | `ENT-L-VENTAS-012` 0,599 · 0,798 |  | El vendedor confirma el mail para mandar el folleto y el receptor está apurado. | misma situación |
| E32 (2) | `LEG-CO-01` | delivery | cotidiana | 8 | `LEG2-CO-01` 0,573 · 0,533 | reescritura declarada de/por `LEG2-CO-01`; mismo número que `LEG2-CO-01` | Repartidor avisa que está llegando con un paquete y dice el nombre del destinatario. | misma situación; unir con E35 |
| E32 (2) | `LEG2-CO-01` | delivery | pedido_razonable | 9 | `LEG-CO-01` 0,573 · 0,533 | reescritura declarada de/por `LEG-CO-01`; mismo número que `LEG-CO-01` | Repartidor confirma nombre y dirección y avisa que está llegando. | misma situación; unir con E35 |
| E33 (1) | `ENT-L-BANCO-004` | banco | pedido_razonable | 35 | `ENT-L-BANCO-006` 0,129 · 0,104 |  | El banco retiene una transferencia grande a un CBU nuevo; la clienta la hizo para pagar la seña de un departamento y el banco pide DNI, nombre del destinatario y motivo antes de liberarla. | — |
| E34 (1) | `ENT-L-BANCO-006` | banco | mencion_sin_pedido | 21 | `ENT-L-BANCO-004` 0,129 · 0,104 |  | El banco detecta que la app se vinculó a un celular nuevo; el cliente sí cambió de teléfono y empieza a leer el código de vinculación, pero la operadora lo frena. | — |
| E35 (1) | `ENT-L-DELIVERY-001` | delivery | cotidiana | 18 | `LEG2-CO-01` 0,155 · 0,188 |  | El repartidor confirma nombre y dirección, pregunta por el perro y por quién va a recibir, y avisa que está llegando. | unir con E32 |
| E36 (1) | `ENT-L-DELIVERY-004` | delivery | mencion_sin_pedido | 21 | `ENT-L-ENCUESTA-006` 0,098 · `LEG2-EN-01` 0,084 |  | La sucursal del correo avisa que un paquete quedó retenido después de dos intentos de entrega, confirma el documento del destinatario y le da el número de seguimiento. | — |
| E37 (1) | `ENT-L-DELIVERY-005` | delivery | mencion_sin_pedido | 20 | `ENT-L-DELIVERY-001` 0,105 · 0,075 |  | El repartidor avisa que sale con un pedido que tiene código de entrega; el comprador intenta decírselo por teléfono y el repartidor le pide mostrarlo en la puerta. | — |
| E38 (1) | `ENT-L-ENCUESTA-006` | encuesta | mencion_sin_pedido | 21 | `LEG2-EN-01` 0,129 · 0,152 |  | El banco hace una encuesta de satisfacción a un cliente que fue a la sucursal; el cliente desconfía y el banco aclara que no pide datos de cuentas ni claves. | — |
| E39 (1) | `ENT-L-SELECCION-001` | trabajo | cotidiana | 18 | `ENT-L-MEDICO-002` 0,094 · `LEG-TU-01` 0,103 |  | Una agencia de personal eventual llama a una postulante a auxiliar de depósito para la temporada de fiestas, le describe el puesto y la cita a una entrevista grupal el martes 10 a las 9, con el pedido de que confirme la asistencia en el día. | — |
| E40 (1) | `ENT-L-SELECCION-002` | trabajo | mencion_sin_pedido | 23 | `ENT-L-BANCO-006` 0,100 · `LEG2-ST-05` 0,112 |  | Una consultora de recursos humanos llama a un postulante a analista contable semi senior para coordinar una entrevista por videollamada el jueves 12 a las 11 y avisarle que el mail que le mandó trae el link y el acceso a una evaluación online; cuando él ofrece leerle el código de acceso, ella lo frena. | — |
| E41 (1) | `ENT-L-SELECCION-003` | trabajo | pedido_razonable | 32 | `ENT-L-BANCO-003` 0,104 · `LEG2-TU-06` 0,114 |  | La responsable de Recursos Humanos de una distribuidora llama a un chofer de reparto recién contratado para avisarle que el preocupacional dio apto y confirmar sus datos para el alta antes de que empiece el lunes 16; él duda al dar el CUIL y ella le ofrece verificar llamando al conmutador de la empresa. | — |
| E42 (1) | `ENT-L-SOPORTE-005` | soporte | pedido_razonable | 32 | `LEG2-ST-05` 0,109 · 0,136 |  | Un técnico de soporte del sistema de facturación que el cliente contrató responde un ticket, le pide instalar el programa de asistencia remota desde la página oficial y dictarle el número de conexión para revisar el error. | — |
| E43 (1) | `ENT-L-SOPORTE-006` | soporte | mencion_sin_pedido | 22 | `ENT-L-VENTAS-005` 0,123 · `LEG2-VE-06` 0,088 |  | Soporte de telefonía coordina el envío de un chip nuevo por una falla, pide documento y dirección y le explica que el PUK viene impreso con el chip. | — |
| E44 (1) | `ENT-L-TRAMITE-001` | tramite | mencion_sin_pedido | 21 | `ENT-L-TRAMITE-002` 0,101 · `LEG2-TU-01` 0,095 |  | La planta de revisión técnica confirma el turno de un auto, verifica la patente y le recuerda el código de turno que llegó por mail. | — |
| E45 (1) | `ENT-L-VENTAS-002` | comercial | pedido_razonable | 23 | `LEG-CC-02` 0,123 · 0,135 |  | Una empresa de fibra óptica ofrece instalación y pide dirección exacta y DNI para ver factibilidad; el vecino duda de dar el DNI y le ofrecen cargarlo él por la web. | — |
| E46 (1) | `ENT-L-VENTAS-003` | comercial | pedido_razonable | 29 | `LEG2-CO-01` 0,104 · 0,177 |  | La aseguradora del banco ofrece un seguro de hogar, confirma el domicilio, el tipo de vivienda y la cuenta donde se pagarían los reintegros. | — |
| E47 (1) | `LEG2-ST-05` | soporte | mencion_sin_pedido | 9 | `ENT-L-SOPORTE-005` 0,109 · 0,136 |  | Soporte de una tienda online responde un ticket y menciona el link para cambiar la contraseña. | — |
<!-- tabla:fin -->
