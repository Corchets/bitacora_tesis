# ADR 0002 — El detector es Gemma 4 E2B solo, con el prompt `c-premisa-corte-riesgo` y aviso con riesgo ≥ 0,3

- **Fecha:** 2026-11-11
- **Estado:** Aceptada
- **Participantes de la discusión:** el equipo. El filtro, el modelo y el alcance los decidió el equipo el 2026-11-06
  ([#51](https://github.com/Corchets/bitacora_tesis/issues/51)). Prompt, lectura, umbral y cuándo consultar salen de la
  segunda vuelta de [#143](https://github.com/Corchets/bitacora_tesis/issues/143), con reglas escritas antes de correr
  (Mateo Antenucci, cerrada el 2026-11-10). Que Tito quede afuera también como ablación es la decisión del 2026-11-09
  registrada en [#52](https://github.com/Corchets/bitacora_tesis/issues/52). Lo registra Luciano Grosso.
- **Ámbito:** arquitectura

## Contexto

[D09](../../gestion/MAPA-DECISIONES.md#d09--elegir-asr-y-detector) pedía elegir ASR y detector antes de correr la
reserva. El [ADR 0001](0001-parakeet-filtro-y-gemma4-e2b-con-tito-viejo.md) fijó el ASR y, hasta el 2026-11-07, también
un detector: Tito viejo como compuerta de Gemma 4 E2B, con el prompt `tarea` y el indicio de Tito. Esa elección salió
de 20 casos de [#101](../../../experiments/slm-directo/corridas/2026-10-30_112956_101_informe_101.md). Lo que vino
después la desarmó:

- la baja de falsas alarmas que se le atribuía a Tito era casi toda punto ciego del filtro
  ([H08](../../hallazgos/H08-tito-evita-falsas-alarmas-por-punto-ciego.md)), porque se entrenó como clasificador de
  estafas y no como compuerta de lo sensible ([H09](../../hallazgos/H09-tito-clasificador-en-vez-de-compuerta.md));
- el indicio de Tito en el prompt le hacía perder estafas al SLM
  ([H07](../../hallazgos/H07-indicio-de-tito-pierde-estafas.md));
- con los prompts que preguntan por el pedido, el aviso caía en la línea del pedido y no antes, y las estafas sin
  pedido no se avisaban ([H05](../../hallazgos/H05-estafas-sin-pedido.md),
  [H10](../../hallazgos/H10-c-avisa-antes-del-pedido.md)).

El detector corre solo en llamadas entrantes de números no agendados
([ADR 0003](0003-detector-solo-en-entrantes-de-no-agendados.md)), y la elección se hizo sobre los 244 casos de
desarrollo con las reglas del [ADR 0005](0005-reglas-de-evaluacion-escritas-antes-de-correr.md): reglas escritas antes
de correr, ±2 casos es ruido, cada candidata repetida y la reserva sin tocar.

## Decisión

Usamos Gemma 4 E2B solo, sin Tito ni reglas delante, con esta configuración:

| Qué | Valor |
|---|---|
| Modelo | `gemma4:e2b-it-q4_K_M`, digest `b37049369adf…` |
| Prompt | `c-premisa-corte-riesgo`: [`tarea_c_premisa.txt`](../../../experiments/slm-directo/prompts/tarea_c_premisa.txt) (sha256 `0e527f70…`) y [`salida_json_c.txt`](../../../experiments/slm-directo/prompts/salida_json_c.txt) (`db9301de…`) |
| Hablantes | Por rol: `PROTEGIDA` y `OTRA`, según el canal capturado |
| Cuándo consulta | Solo en las líneas de OTRA, con toda la transcripción hasta ahí. En vivo, al cerrar cada turno de OTRA ([ADR 0007](0007-consulta-al-cerrar-cada-turno-de-otra.md)) |
| Lectura | La salida se corta después del riesgo, el primer campo del JSON (`num_predict` 14, [ADR 0006](0006-salida-cortada-tras-el-campo-que-decide-y-motivo-al-avisar.md)) |
| Aviso | Uno solo por llamada, en la primera consulta con riesgo ≥ 0,3. Después no se consulta más |
| Motivo | Una segunda consulta, solo en ese aviso, con [`motivo_c_corte.txt`](../../../experiments/slm-directo/prompts/motivo_c_corte.txt) (`e30e8feb…`). Si falla, el aviso sale con un texto fijo |
| Parámetros | Temperatura 0, seed 42, `num_ctx` 4096. No se envía `think` ni se piden logprobs |
| Código | `DetectorSLMCorteRiesgo` en [`detectores.py`](../../../experiments/slm-directo/detectores.py). Los tres prompts no cambiaron desde `ca4fab0`, el commit del tag `colab/143-sensibilidad` |

Las reglas léxicas quedan como línea base y como respaldo de la demo sin modelo. El ASR sigue siendo el del ADR 0001.

## Alternativas consideradas

Las cifras son de desarrollo dentro del alcance (`alcance-140`: 46 estafas, 36 con pedido, y 94 legítimas), salvo
donde se indica otra cosa.

| Alternativa | A favor | En contra | Por qué se descartó |
|---|---|---|---|
| Tito viejo como compuerta de E2B (la del ADR 0001) | La mitad de las consultas | Las falsas alarmas que «evita» son punto ciego (H08). Pierde `CV2-D-V-PREMIO-001` y atrasa avisos | El equipo lo sacó el 2026-11-06. Desde el 2026-11-09 tampoco va como ablación. El rediseño es trabajo futuro ([#149](https://github.com/Corchets/bitacora_tesis/issues/149)) |
| El indicio de Tito dentro del prompt | Le da al modelo una pista de dónde mirar | Le hace perder estafas al SLM (H07) | La demo dejó de usarlo el 2026-11-05 |
| `v4` con roles, cortado tras la alerta (propuesta del 2026-11-05) | Cita mejor que `tarea` (H06) | Contra C, 8 estafas menos, 7 avisos menos antes del pedido y 42/94 FA contra 27/94 ([etapa 2](../../../experiments/slm-directo/corridas/2026-11-07_alcance-etapa-2/analisis.md)) | Pierde por más de ±2 en las tres cifras |
| `v4-premisa` | El mismo párrafo del alcance, sobre v4 | Queda dentro del ruido contra v4 (etapa 2) | No mejora a v4 |
| C sin el párrafo de la premisa (`c-json-corte-riesgo`, la base de la prueba de sensibilidad) | Era la configuración congelada hasta el 2026-11-10 | 37/46 estafas, 15/36 antes del pedido y 25/36 a tiempo, contra 40, 19 y 29. Mismas FA: 26/94 ([sensibilidad](../../../experiments/slm-directo/corridas/2026-11-10_sensibilidad-c/analisis.md)) | La regla elige `c-premisa`, y la repetición lo sostiene |
| `c-ancla` y `c-sin-freno` | También pasan la regla | Suman +5 entre estafas y a tiempo, contra +7 de `c-premisa`. `c-sin-freno` agrega 8 a 10 FA en las legítimas dudosas | La regla elige la que más suma |
| C con un campo `pedido_critico` antes del riesgo | 17–18/94 FA | Pierde 4 avisos a tiempo, y 3 en la repetición ([etapa 3](../../../experiments/slm-directo/corridas/2026-11-09_pedido-critico-etapa-3/analisis.md)) | Pierde 3 o más |
| Leer la probabilidad del token (P(SÍ) o el riesgo de v4-L) | Es lo más rápido y da un puntaje continuo | Empata con el riesgo escrito y pierde las estafas de `alerta_sugerida` ([etapa 1](../../../experiments/slm-directo/corridas/2026-11-06_puntaje-token-2/analisis.md)) | Sin ajuste fino no sirve. Trabajo futuro con LoRA ([#176](https://github.com/Corchets/bitacora_tesis/issues/176)) |
| Umbral 0,2 | Avisa 46/46 | 69/94 FA, 14 de ellas en cotidianas ([humo](../../../experiments/slm-directo/corridas/2026-11-10_config-congelada-humo/analisis.md)) | Las FA se disparan |
| Una capa de reglas sobre C | Suma estafas con pedido explícito | v1: +5 estafas y +32 FA; v2: +1 y +9 (humo) | El costo en FA es mayor que la ganancia |
| Gemma 4 E4B | Modelo más grande de la misma familia | No se corrió sobre los 244. En la M1 de 8 GB avisó a +49 s del pedido | Sin evidencia para preferirlo. Se compara en la PC en [#173](https://github.com/Corchets/bitacora_tesis/issues/173), como referencia |
| Consultar en todas las líneas, de los dos lados | Avisa antes si la frase de PROTEGIDA alcanza | El doble de consultas, sin mejorar ninguna cifra en más de 2 | ADR 0007 |
| Un modelo de frontera por API | Probablemente detecta más | La transcripción sale del teléfono, depende de la red y cuesta por consulta | Lo descartó el tutor por privacidad. Se mide como techo en [#174](https://github.com/Corchets/bitacora_tesis/issues/174), solo en desarrollo |
| Gemma 4 escuchando el audio directo ([#152](https://github.com/Corchets/bitacora_tesis/issues/152)) | Sin transcripción intermedia | La llamada no entra en el contexto, y sin texto no hay motivo ni registro | ADR 0001. Trabajo futuro |

## Consecuencias

- **Cifras de desarrollo, que no estiman el rendimiento final:** 40/46 estafas avisadas, 19/36 antes del pedido,
  29/36 a tiempo y 26/94 FA; en la repetición, 39, 18, 28 y 28/94
  ([sensibilidad](../../../experiments/slm-directo/corridas/2026-11-10_sensibilidad-c/analisis.md)). Lo que significan
  está en [H10](../../hallazgos/H10-c-avisa-antes-del-pedido.md).
- **Las FA quedan lejos de la meta de referencia:** 26/94 es cerca del 28 %, contra el 10–15 % de RNF-06. Cómo se lee
  ese límite en la reserva lo fija el protocolo en [#33](https://github.com/Corchets/bitacora_tesis/issues/33).
- **El aviso sale casi siempre de un 0,3 exacto** (57 de 66 avisos), así que un cambio chico de prompt mueve varias
  cifras ([H04](../../hallazgos/H04-riesgo-escrito-no-es-puntaje.md)).
- **Queda un punto ciego:** ninguna variante avisa `WHATSAPP-003`, `SOPORTE-003` ni `PREMIO-003`, que tienen pedido
  explícito. Algunos motivos dicen lo contrario de lo que pasó (`ENT-L-SELECCION-002`): la explicación hay que revisarla.
- **La elección es una búsqueda a mano sobre los mismos casos de desarrollo,** sin revisión humana de `T_R` ni de `T_C`
  ([D07](../../gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico)). El número honesto lo da la corrida
  única de [#52](https://github.com/Corchets/bitacora_tesis/issues/52) sobre la reserva y el set externo de
  [#144](https://github.com/Corchets/bitacora_tesis/issues/144).
- **Sin Tito no hay componente entrenado:** el detector es un modelo general con un prompt, sin datos propios de ajuste.
  La memoria y la latencia de Tito (0,48 GB y unos 30 ms por frase) salen de las cuentas.
- **Costo:** en T4, 206 ms de mediana por consulta y 678 ms el motivo, con la base sin la premisa
  ([humo](../../../experiments/slm-directo/corridas/2026-11-10_config-congelada-humo/analisis.md)). En el Samsung A56,
  3,60 s de mediana por línea de OTRA y unos 11 s el motivo, también con la base
  ([a56-congelada-latencia](../../../experiments/slm-directo/corridas/2026-11-10_a56-congelada-latencia/README.md)).
  Falta repetirlo con `c-premisa` ([#141](https://github.com/Corchets/bitacora_tesis/issues/141)), y bajarlo es
  [#172](https://github.com/Corchets/bitacora_tesis/issues/172).
- **No se midió el efecto del ASR** sobre estas cifras ([#54](https://github.com/Corchets/bitacora_tesis/issues/54)):
  todas suponen texto limpio y turnos perfectos.
- `servidor.py`, el panel y `medir.py` ya arrancan con esta configuración (PR #167 y #171). Tito viejo sigue disponible
  por línea de comandos, solo como antecedente.

**Para reconsiderarla:** que en el teléfono una consulta tarde más que un turno típico de OTRA aun con las mejoras de
#172, o que la ventana real del ASR mueva las cifras más de ±2 frente a los turnos perfectos. Lo que se cambie después de
correr la reserva se informa como exploración, no como resultado.

## Referencias

- [Etapa 2 de #143](../../../experiments/slm-directo/corridas/2026-11-07_alcance-etapa-2/analisis.md): C contra v4.
- [Etapa 3 de #143](../../../experiments/slm-directo/corridas/2026-11-09_pedido-critico-etapa-3/analisis.md): corte
  tras el riesgo, umbral 0,3 y solo OTRA.
- [Humo de la configuración congelada](../../../experiments/slm-directo/corridas/2026-11-10_config-congelada-humo/analisis.md).
- [Prueba de sensibilidad](../../../experiments/slm-directo/corridas/2026-11-10_sensibilidad-c/analisis.md): elige
  `c-premisa`. Las fuentes externas del párrafo están en el
  [`FUENTES.md` de la etapa 3](../../../experiments/slm-directo/corridas/2026-11-09_pedido-critico-etapa-3/FUENTES.md).
- [Propuesta del 2026-11-05](../../evaluacion/PROPUESTA-CONFIGURACION-DETECTOR.md), superada por este ADR.
