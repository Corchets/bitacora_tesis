# Propuesta de configuración del detector para el ADR 0002

**Fecha:** 2026-11-05. **Issue:** [#51](https://github.com/Corchets/bitacora_tesis/issues/51).

> **Nota del 2026-11-11:** superada por el [ADR 0002](../ingenieria/adr/0002-detector-gemma4-e2b-solo-con-prompt-c-premisa.md). El equipo sacó a Tito
> el 2026-11-06 y la segunda vuelta de [#143](https://github.com/Corchets/bitacora_tesis/issues/143) eligió el prompt C
> con la premisa del alcance en lugar de `v4`. Lo de abajo queda como estaba.

> **Estado: propuesta sin discutir.** La propone Luciano para que el equipo decida si vamos con esta configuración u
> otra. Todos los números son de los 150 casos de desarrollo, ya vistos y con referencias sin revisión humana: sirven
> para elegir, no estiman el rendimiento final. No decide
> [D07](../gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) ni
> [D08](../gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental). El ASR no cambia: sigue el
> [ADR 0001](../ingenieria/adr/0001-parakeet-filtro-y-gemma4-e2b-con-tito-viejo.md).

## Qué proponemos

| Pieza | Propuesta | Lo que dice hoy el ADR 0001 |
|---|---|---|
| Filtro | **Tito viejo**, umbral 0,5, **sin indicio**: solo decide cuándo consultar al modelo | Tito viejo con indicio |
| Modelo | **Gemma 4 E2B** (`gemma4:e2b-it-q4_K_M`), `num_ctx` 4096, temperatura 0, seed 42 | Igual |
| Prompt | **[v4](../../experiments/slm-directo/prompts/tarea_v4.txt)**, con cada línea marcada como PROTEGIDA u OTRA | [v1 (`tarea`)](../../experiments/slm-directo/prompts/tarea.txt), con A y B |
| Aviso | **Uno por llamada, en la primera alerta** | Igual |

**Resultado: 55 de 75 estafas avisadas y 13 de 75 falsas alarmas.** Salió igual, caso por caso, en tres corridas (una con Tito viejo 2.0, que no cambia nada).
Lo que dice hoy el ADR 0001 da 50–51 estafas y 12–13 falsas alarmas: la propuesta avisa 4 o 5 estafas más con, como
mucho, una falsa alarma más, y cita mejor lo que se pidió. La demo con ASR ya arranca así desde el 2026-11-05.

**No llega a la meta de referencia** (80–85 % de estafas con 10–15 % de falsas alarmas, o sea 60–64 y 8–11 de 75). Ninguna
de las condiciones probadas llega. Más abajo está [por qué](#qué-no-arregla-ninguna-configuración).

## Cómo leer las tablas

- **Casos:** 75 estafas y 75 legítimas de desarrollo. Las legítimas son 51 comunes y 24 difíciles, hechas para parecerse a una estafa.
- **Ruido:** repetir la misma corrida mueve 1 o 2 casos. Una diferencia así no se lee como mejora. Con 75 casos, 55/75
  es en realidad algo entre 62 % y 82 %, y 13/75, entre 10 % y 27 % (intervalo de Wilson del 95 %).
- **Cita el pedido:** cuántas veces el aviso copia la línea donde realmente se pide algo, sobre las 64 estafas que tienen pedido. Mide si el aviso es útil para la persona.
- **Consultas:** cuántas veces se le pregunta al modelo en los 150 casos. En el teléfono, cada consulta es tiempo y batería.
- Todas las corridas son con Gemma 4 E2B en Google Colab (GPU T4), salvo donde se dice otra cosa.

## Decisión 1: el filtro (Tito)

Todas con prompt v4 y roles, salvo donde se aclara.

| Opción | Estafas | Falsas alarmas | Consultas | Qué mejora frente a la propuesta | Qué empeora |
|---|---:|---:|---:|---|---|
| **Tito viejo sin indicio (propuesta)** | **55** | **13** | 1.132 | — | — |
| Tito viejo 2.0 (frases de Ignacio, sin indicio) | 55 | 13 | 1.133 | Nada: mismos casos y mismas líneas | Una pieza más que mantener |
| Sin Tito: el modelo lee todas las líneas | 56 | 17 | 2.225 | Avisa `PREMIO-001`, la única estafa donde Tito no se activa | 5 falsas alarmas más (y 1 menos) y casi el doble de consultas |
| Tito viejo con indicio (con v1) | 50 | 12 | 1.189 | 2 falsas alarmas menos que v1 sin indicio | 4 estafas menos que v1 sin indicio: el modelo se apoya en la frase que marcó Tito |
| Tito nuevo (solo en los 20 casos de #101) | 2 de 10 | 0 de 10 | — | Ninguna falsa alarma | Pierde casi todas las estafas; no se probó en los 150 |

**Por qué Tito viejo sin indicio.** Tito ya se activa en 74 de las 75 estafas, y en las que tienen pedido se activa
antes o justo en el pedido en 62 de 64. Lo que aporta es no activarse en las legítimas: ahorra la mitad de las consultas
y 4 falsas alarmas netas a cambio de una estafa. Las frases de Tito viejo 2.0 no cambian nada porque aparecen cuando
Tito ya está casi en cero; habría que multiplicar sus pesos por más de 10 para que muevan algo. Detalle en la
[corrida del 2026-11-05](../../experiments/slm-directo/corridas/2026-11-05_tito-2-v4/analisis.md).

> **Nota del 2026-11-06 (Mateo):** que Tito no se active en las legítimas no es un acierto. Cuando aparece la primera
> línea sensible, el SLM está despierto en 62 de 64 estafas, pero solo en 14 de 43 legítimas. Las 5 legítimas que dejan
> de dar falsa alarma con Tito son casos en que el SLM avisaba en una línea sensible que Tito no vio, y suma una
> (`BANCO-006`); en corpus_v2 no cambia ninguna. El aporte que queda es la mitad de las consultas, a cambio de
> `PREMIO-001`. Ver
> [H08](../hallazgos/H08-tito-evita-falsas-alarmas-por-punto-ciego.md).

## Decisión 2: el prompt del modelo

Todas con Tito viejo sin indicio y primer aviso. «v4» es la versión que proponemos; las demás son las que se probaron antes o después.

| Prompt | Qué cambia | Estafas | Falsas alarmas | Cita el pedido | Cita solo a la víctima | Qué mejora frente a v4 | Qué empeora |
|---|---|---:|---:|---:|---:|---|---|
| **v4 con roles (propuesta)** | Ver la lista de abajo | **55** | **13** | 34–36 | 1–2 | — | — |
| v1 (`tarea`), A y B | El original, del 2026-10-13 | 53–54 | 14 | 27 | 7–8 | Más corto: unos 700 tokens por consulta contra 1.100 | Avisa peor: cita menos el pedido y más veces solo a la víctima |
| v1 con roles | v1 sabiendo quién es quién | 53 | 12 | 30 | 5 | 1 falsa alarma menos | 2 estafas menos y cita peor |
| v3, A y B | La cita va primero y hay más reglas de contexto | 64 | 35 | 20 | 8 | 9 estafas más | 22 falsas alarmas más |
| v3 con roles | v3 sabiendo quién es quién | 67 | 34 | 22 | 7 | 12 estafas más | 21 falsas alarmas más |
| v3 con el orden de v1 | v3 con la cita al final | 57 | 18 | 31 | 5 | 2 estafas más | 5 falsas alarmas más |
| v4 con cita libre | v4 sin exigir que la cita sea de OTRA | 55 | 12 | 36 | 4 | 1 falsa alarma menos, dentro del ruido | Cita más veces solo a la víctima |
| v5, maniobras | v4 + avisar si OTRA intenta aislar a la persona | 57 | 16 | 25 | 3 | 2 estafas más | 3 falsas alarmas más, toma consejos por tácticas y avisa antes del pedido |
| v5, indirectos | v4 + más formas de pedido indirecto | 55 | 12 | 34 | 2 | 1 falsa alarma menos, dentro del ruido | No recupera lo que buscaba |
| v5, sin excepción | v4 sin la excepción de datos comunes | 56 | 13 | 32 | 2 | Recupera dos pedidos de credenciales | Pierde otra estafa y cita menos el pedido |
| v5, los tres juntos | Las tres reglas de v5 | 57 | 13 | 27 | 2 | 2 estafas más | Adelanta 8 avisos antes del pedido y cita mucho menos |

**Qué tiene v4 frente a v1:** cada línea dice si habla PROTEGIDA u OTRA y solo alerta si OTRA pide; la lista de
acciones es más amplia (reenviar un mensaje, foto de la cara, dejar que otro maneje el celular, seguir instrucciones en
el cajero); cuentan los pedidos indirectos aunque la razón parezca válida; no alerta por consejos de entrar por la
aplicación oficial ni por relatos de otra llamada; no alerta si PROTEGIDA inició la gestión y le piden un dato común
(nunca claves, códigos ni pagos); y la cita tiene que ser de OTRA. El orden de los campos es el de v1.

**Por qué v4.** Entre las que no suben las falsas alarmas, es la que mejor avisa: cita el pedido real en 34–36 casos,
contra 27 de v1, y casi nunca cita solo lo que dijo la víctima. v3 detecta más, pero con 34–35 falsas alarmas, muy lejos
de la meta. v5 no supera a v4 con una diferencia que se pueda defender. Historial completo en el
[README de prompts](../../experiments/slm-directo/prompts/README.md) y resultados en el
[análisis de v3, v4 y v5](../../experiments/slm-directo/corridas/2026-11-04_193946_prompt-v3-a-solo-y-con-indicio/analisis.md).

**Qué cuesta:** v4 es más largo (unos 1.100 tokens de entrada por consulta contra 700). En la T4 no cambia el tiempo
(0,41 s por consulta en las dos), pero en el teléfono no se midió.

## Decisión 3: el modelo

| Modelo | Calidad | Costo | Situación |
|---|---|---|---|
| **Gemma 4 E2B (propuesta)** | Los 150 resultados de arriba | Archivo de 4,59 GB. En la Mac M1 de 8 GB, 3,74 s por consulta (mediana) | El único corrido en los 150 |
| Gemma 4 E4B | En los 20 casos de #101: 10/10 estafas y 1/10 falsas alarmas, contra 10/10 y 0/10 de E2B | En la M1 entra en swap: 16 y 46 s en sus dos evaluaciones, y avisó 49 s tarde | Nunca se corrió en los 150 |
| Qwen3.5 9B, reglas, cross-encoders y riesgo primero | Ver el ADR 0001 | Ver el ADR 0001 | Descartados en el [ADR 0001](../ingenieria/adr/0001-parakeet-filtro-y-gemma4-e2b-con-tito-viejo.md#alternativas-consideradas) |

**Capacidad, lo que sabemos y lo que no:** E2B (4,59 GB), Tito (unos 0,48 GB) y el ASR (hasta 1 GB) quedan muy por
encima del techo de 512 MB de la prefactibilidad. En la M1, E2B no cumple los 2 s por consulta de #84, aunque el aviso
llegó entre −0,45 y +0,40 s del fin del pedido. **En un teléfono no se midió nada todavía**: eso es
[#141](https://github.com/Corchets/bitacora_tesis/issues/141).

**Por qué E2B.** E4B no mostró mejor calidad y en la Mac ya no corre a tiempo. Para cambiar, habría que correr E4B en
los 150, y aun ganando un par de casos seguiría el problema de memoria.

## Decisión 4: cuándo se avisa

Simulado sobre una corrida de v4 que siguió leyendo después del primer aviso, sin que el modelo supiera que ya había alertado.

| Política | Estafas | Falsas alarmas | Qué mejora frente al primer aviso | Qué empeora |
|---|---:|---:|---|---|
| **Primera alerta (propuesta)** | **55** | **13** | — | — |
| 2 alertas en la llamada | 51 | 11 | 2 falsas alarmas menos | 4 estafas menos |
| 2 alertas seguidas | 49 | 8 | 5 falsas alarmas menos: entra en la franja de la meta | 6 estafas menos |
| 3 alertas en la llamada | 48 | 6 | 7 falsas alarmas menos | 7 estafas menos |
| 3 alertas seguidas | 47 | 4 | 9 falsas alarmas menos | 8 estafas menos |

**Por qué la primera alerta.** Esperar más alertas baja las falsas alarmas, pero pierde estafas al mismo ritmo, y lo
que más falta para la meta es detectar estafas. Además, solo está simulada. La política es parte de D08, así que el
equipo puede elegir otra sin cambiar el resto.

## Qué no arregla ninguna configuración

De las 20 estafas que la propuesta no avisa:

- **10 no llegan a pedir nada.** Ningún prompt avisó ninguna, y v5 solo una. Que cuenten o no como acierto es una
  decisión de D07. Si no cuentan, la propuesta avisa 54 de 64 (84 %), dentro de la meta. Pero en el corpus v2, que es lo
  que más se parece a la reserva, esas mismas cuentas dan 26 de 36 (72 %).
- **10 tienen un pedido que el modelo no ve.** v3 sin Tito las detecta todas, pero con 47 falsas alarmas: el modelo
  puede verlas, el problema es el costo. Cuatro prompts distintos no movieron su riesgo en la línea del pedido.

De las 13 falsas alarmas, 7 son pedidos de un dato de identificación en llamadas que inició la persona. El sistema no
sabe quién inició la llamada (D03 lo deja fuera), y la excepción de v4 no alcanzó a evitarlas. El detalle caso por caso
está en [FALLAS-Y-CORPUS-2026-11-05.md](../../experiments/slm-directo/casos/FALLAS-Y-CORPUS-2026-11-05.md).

**Qué esperar en la reserva:** las 100 estafas reservadas son todas del corpus v2, donde la propuesta avisa 27 de 46
(59 %) con 6 de 51 falsas alarmas (12 %). Con esas tasas daría alrededor de 60 de 100. Hay 20 estafas sin pedido en
la reserva, así que un detector que solo avisa por pedidos no puede pasar de 80.

## Qué tiene que decidir el equipo

Siguiendo lo que pide el [#51](https://github.com/Corchets/bitacora_tesis/issues/51):

- [ ] **Regla de decisión, antes de mirar la reserva:** diferencias de ±2 casos en los 150 son ruido.
- [ ] **Filtro:** Tito viejo sin indicio, sin Tito u otro.
- [ ] **Prompt:** v4 con roles o v1 (`tarea`) con A y B.
- [ ] **Modelo:** E2B, o correr antes E4B en los 150.
- [ ] **Política de aviso:** primera alerta o alguna persistencia (D08).
- [ ] **Estafas sin pedido:** si cuentan como acierto (D07), para llevar a la reunión con el tutor del 2026-11-11.

**Si no vamos con esta**, las alternativas razonables son:

- Dejar el ADR 0001 como está (v1 con indicio, 50–51/12–13).
- `v5-sin-excepcion` (56/13), a un caso de distancia.
- La propuesta con dos alertas en la llamada (51/11).

Con lo que se decida se escribe el ADR 0002 y se congela la configuración antes de correr la reserva (#33).

## Fuentes

- **Corridas de Tito 2.0 y sin Tito:** [análisis del 2026-11-05](../../experiments/slm-directo/corridas/2026-11-05_tito-2-v4/analisis.md), con un [script](../../experiments/slm-directo/corridas/2026-11-05_tito-2-v4/analizar.py) que reproduce las tablas de filtro y costo.
- **Prompts v1, v3, v4 y v5, indicio y persistencia:** [análisis general](../../experiments/slm-directo/corridas/2026-11-04_193946_prompt-v3-a-solo-y-con-indicio/analisis.md), reproducible con [`comparar_con_v1_colab.py`](../../experiments/slm-directo/corridas/2026-11-04_193946_prompt-v3-a-solo-y-con-indicio/comparar_con_v1_colab.py), y [análisis de v5](../../experiments/slm-directo/corridas/2026-11-05_prompt-v5-tito-sin-indicio/analisis.md).
- **Tito viejo 2.0 con v1:** [comparación de Ignacio](../../experiments/slm-directo/analisis/2026-11-05-TITO-VIEJO-2-COMPARACION.md).
- **Tito nuevo, E4B, memoria y tiempos en la M1:** [comparación de candidatos](COMPARACION-CANDIDATOS-DESARROLLO.md#comparación-que-sostiene-la-elección-2026-10-30-a-2026-11-02) y [ADR 0001](../ingenieria/adr/0001-parakeet-filtro-y-gemma4-e2b-con-tito-viejo.md#consecuencias).
- **Tokens y tiempo por consulta en la T4:** medianas de `tokens_prompt` y `slm_ms` en los `actualizaciones.csv` de las corridas de v1 y v4 con Tito sin indicio.
