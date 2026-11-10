# Prompts del ensayo #50

> **Estado: propuesta sin discutir.** Primera versión (v1, 2026-10-13). Cualquier
> cambio se registra abajo con fecha y motivo; las corridas guardan el texto
> completo y su hash en `manifiesto.json`, así que una corrida vieja siempre
> dice con qué prompt se hizo.

| Variante (`--prompts`) | Mensaje de sistema |
|---|---|
| `tarea` | [`tarea.txt`](tarea.txt) |
| `tarea+base` | [`tarea.txt`](tarea.txt) + una línea en blanco + [`base_institucional.txt`](base_institucional.txt) |
| `v2` | [`tarea_v2.txt`](tarea_v2.txt), con los campos en otro orden (`ESQUEMA_SALIDA_V2` en `detectores.py`) |
| `v3` | [`tarea_v3.txt`](tarea_v3.txt), con el orden de campos de v2 |
| `v3-orden-v1` | [`tarea_v3_orden_v1.txt`](tarea_v3_orden_v1.txt): v3 con los campos en el orden de v1 |
| `v4` | [`tarea_v4.txt`](tarea_v4.txt), pensada para `--hablantes rol` |
| `v5-maniobras`, `v5-indirectos`, `v5-sin-excepcion`, `v5` | Un cambio cada una sobre v4, y `v5` con los tres. Probadas, no adoptadas: ver el [análisis](../corridas/2026-11-05_prompt-v5-tito-sin-indicio/analisis.md) |
| `v4-cita-libre` | [`tarea_v4_cita_libre.txt`](tarea_v4_cita_libre.txt): v4 con la instrucción de evidencia de v1, sin exigir citar a OTRA. Probada, no adoptada: 55/75 y 12/75 en el [análisis](../corridas/2026-11-04_193946_prompt-v3-a-solo-y-con-indicio/analisis.md) |
| `v4-a1`, `tarea-a1`, `v4-a2` | [`tarea_v4_a1.txt`](tarea_v4_a1.txt), [`tarea_a1.txt`](tarea_a1.txt) y [`tarea_v4_a2.txt`](tarea_v4_a2.txt): A1 (solo formato) y A2 (intención) de #143. Pregunta SÍ/NO en lugar del JSON, leída por la probabilidad del primer token (`DetectorSLMSiNo`). Ver «Pregunta SÍ/NO» abajo |
| `tarea-sino`, `v4-sino`, `v4-sin-reglas-sino` | [`tarea_sino.txt`](tarea_sino.txt), [`tarea_v4_sino.txt`](tarea_v4_sino.txt) y [`tarea_v4_sin_reglas_sino.txt`](tarea_v4_sin_reglas_sino.txt): primer intento SÍ/NO de #143, descartado en la prueba de humo 1 |
| `riesgo` | [`riesgo.txt`](riesgo.txt) en la etapa 1 (solo `{"riesgo": x}`); si x > umbral, [`riesgo_motivo.txt`](riesgo_motivo.txt) como pedido de la etapa 2 (`DetectorSLMDosEtapas`) |

El mensaje del usuario lo arma `detectores.py` en cada actualización: la
transcripción disponible numerada por línea y una aclaración sobre hablantes
según `--hablantes` (`ab`: cada línea con A o B; `rol`: con PROTEGIDA u OTRA, según
[`roles-protegida.json`](../casos/roles-protegida.json); `sin`: sin indicar quién habla).

## Versiones del system prompt

Los textos completos se conservan en archivos separados. El número de versión
identifica el historial; **P0/P1 identifica el control y el candidato de una
comparación concreta**, no el orden histórico.

| Versión | Fecha | Texto completo | Cambio y estado |
|---|---|---|---|
| **Versión 1 — original** | 2026-10-13 | [`tarea.txt`](tarea.txt) | Criterio de alerta, seis acciones, exclusión breve de menciones y JSON con riesgo primero. Es `tarea` en el ejecutor y **P0 de las dos corridas de 150**. Commit `d9173b6`. |
| **Versión 2 — modificación previa** | 2026-10-21 | [`tarea_v2.txt`](tarea_v2.txt) | Reformula las acciones, explicita relatos/hipótesis y razones creíbles, quita el ejemplo de código, pone la evidencia primero y exige riesgo ≥ 0,5 con alerta. Es `v2` en el ejecutor; no fue el prompt de esas corridas de 150. Commit `886cff0`. |
| **Versión 3 — probada, no adoptada** | 2026-11-04 | [`tarea_v3.txt`](tarea_v3.txt) | Parte de v2: quita el mínimo de riesgo 0,5, conserva el orden de campos de v2 y agrega reglas de contexto. [Resultados en Colab](../corridas/2026-11-04_193946_prompt-v3-a-solo-y-con-indicio/analisis.md): más estafas con aviso y muchas más falsas alarmas. No se usa en la demo. |
| **Versión 4 — por defecto en la demo desde el 2026-11-05, ADR 0001 sin reabrir** | 2026-11-04 | [`tarea_v4.txt`](tarea_v4.txt) | Parte de v3: vuelve al orden de campos de v1, nombra a PROTEGIDA y OTRA, y agrega las reglas de canal propio y de datos comunes. [Resultados](../corridas/2026-11-04_193946_prompt-v3-a-solo-y-con-indicio/analisis.md): 55/75 estafas y 13/75 falsas alarmas con Tito sin indicio (55/75 y 13/75 repetido). |
| **Versión 5 — probada, no adoptada** | 2026-11-05 | [`tarea_v5_maniobras.txt`](tarea_v5_maniobras.txt), [`tarea_v5_indirectos.txt`](tarea_v5_indirectos.txt), [`tarea_v5_sin_excepcion.txt`](tarea_v5_sin_excepcion.txt), [`tarea_v5.txt`](tarea_v5.txt) | Tres cambios probados de a uno sobre v4 (maniobras sin pedido explícito, pedidos indirectos de dinero o cobro, y retiro de la excepción de datos comunes) y los tres juntos (`v5`), más 18 controles sintéticos de maniobras. [Resultados](../corridas/2026-11-05_prompt-v5-tito-sin-indicio/analisis.md): `v5-maniobras` 57/75 y 16/75, `v5-indirectos` 55/75 y 12/75, `v5-sin-excepcion` 56/75 y 13/75, y `v5` 57/75 y 13/75. Ninguna supera a v4 de forma consistente ni avisa las estafas sin pedido del corpus. No se adopta. |

## Pregunta SÍ/NO (#143) — 2026-11-05

> **Estado: propuesta sin discutir.** En prueba en
> [#143](https://github.com/Corchets/bitacora_tesis/issues/143); no reemplaza a v1 ni a v4.

En vez de pedir el JSON, el prompt termina con una pregunta cerrada y se lee P(SÍ) de los
`logprobs` del primer token (`num_predict` 1, temperatura 0, sin razonamiento, sin esquema).
El mensaje del usuario es el mismo de siempre.

### A1 y A2 (tabla «Variantes» de #143, actualizada el 2026-11-05)

- **A1, solo formato (`v4-a1` con `rol`; `tarea-a1` con `ab` porque #51 sigue abierto):** el cuerpo
  de `tarea_v4.txt` (o `tarea.txt`) sin cambios, salvo la oración que definía `alerta_sugerida`:
  «Marcá "alerta_sugerida": true solo si,» pasa a «Lo que importa es si,» y el resto de la
  oración queda igual. El «solo si» pasa a la pregunta, que pide exactamente eso. El párrafo del
  JSON se reemplaza por la pregunta:
  - `v4-a1`: «¿OTRA le está pidiendo o induciendo a PROTEGIDA algo de la lista? Respondé solo SÍ o NO.»
    (literal del issue);
  - `tarea-a1`: «¿Alguien le está pidiendo o induciendo a la otra persona algo de la lista? Respondé
    solo SÍ o NO.» Con hablantes A/B no hay OTRA ni PROTEGIDA: usa las palabras del cuerpo de
    `tarea.txt`. Aprobada por Mateo el 2026-11-05.

  Se compara contra su línea base JSON: mide el efecto de leer el token con la misma definición de aviso.
- **A2, intención (`v4-a2` con `rol`):** el cuerpo de `v4-a1` sin el párrafo de las dos reglas que
  bloquean la anticipación: «Si para explicar el peligro tenés que suponer algo que no se dijo, no
  alertes. Que alguien apure, diga ser de una entidad o hable de un problema puede aumentar el
  riesgo, pero no alcanza por sí solo para alertar.» Las exclusiones de «No alcanza para alertar»
  quedan iguales. Pregunta: «Hasta acá, ¿OTRA está intentando estafar a PROTEGIDA, aunque todavía no
  haya pedido nada? Respondé solo SÍ o NO.» Se compara contra `v4-a1`.
- `tests/test_puntaje_token.py` comprueba que los tres textos salen de `tarea_v4.txt` y `tarea.txt`
  solo con estos cambios.

### Prueba de humo 1 (descartada): `tarea-sino`, `v4-sino`, `v4-sin-reglas-sino`

Se escribieron con la versión anterior de #143 («mismo prompt, lo único que cambia es el final»),
antes de que el issue sumara la tabla A1/A2 (21:18 del 2026-11-05, antes de correr la humo). El
cuerpo quedaba igual byte a byte, incluido «Marcá "alerta_sugerida": true solo si…», y el JSON se
reemplazaba por «Con lo disponible hasta ahora, ¿corresponde marcar la alerta según estas reglas?
Respondé solo SÍ o NO.» `v4-sin-reglas-sino` además quitaba el párrafo de las dos reglas.

[Resultado](../corridas/2026-11-05_humo-puntaje-token-1/humo.md) (Colab T4, commit `9a2692e`, 3
casos de desarrollo): `masa_si_no` ≥ 0,9 en 35, 31 y 38 de 48 líneas. **No pasa.** Casi toda la masa
que falta va al token «al» (y «alert», «AL»), justo en las líneas donde el JSON de las líneas
base avisaba (SC-WA-CODE-01-e01 L3, CV2-D-L-BANCO-001 L12). Cuando el modelo quiere avisar, empieza
a escribir «al…» en vez de «SÍ». Así P(SÍ)/(P(SÍ)+P(NO)) descarta justo la señal de aviso. A1
y A2 sacan «alerta_sugerida» del cuerpo y «alerta» de la pregunta. La humo 2 genera unos tokens
más en dos de esas líneas para dejar escrita la palabra.

Criterio de la humo 2, fijado antes de correrla (Mateo, 2026-11-05): `masa_si_no` ≥ 0,9 en al menos
44 de 48 líneas (≥ 90 %) por variante. Si no se cumple, se ajusta solo la pregunta final y se repite.

### Prueba de humo 2: A1 y A2 pasan

[Resultado](../corridas/2026-11-05_humo-puntaje-token-2/humo.md) (Colab T4, commit `fc254af`, tag
`colab/143-humo-2`, mismos 3 casos): `tarea-a1`, `v4-a1` y `v4-a2` dan `masa_si_no` ≥ 0,9 en **48 de 48**
líneas (mínimo 0,999998). Los tokens elegidos son solo «NO» y «S» (con «SI» y «Sí» como alternativas
lejanas). No hizo falta tocar la pregunta. El diagnóstico confirma la causa de la humo 1: con el prompt
viejo, en SC-WA-CODE-01-e01 L3 y CV2-D-L-BANCO-001 L12 el modelo escribe «alerta_sugerida: true»
(`al`, `erta`, `_`, `s`, `uger`, `ida`, `:`, ` true`).

### Segunda vuelta (2026-11-06): alcance, prompt C, pregunta al final y lectura del token

> **Estado: propuesta sin discutir.** Lista cerrada el 2026-11-06, antes de correr. Regla y análisis en
> [`corridas/2026-11-06_puntaje-token-2/analizar.py`](../corridas/2026-11-06_puntaje-token-2/analizar.py).

La primera vuelta no fue una prueba justa para el token, por dos motivos:
- A1 preguntaba algo literal («¿le pide algo de la lista?»), y la lista incluye el nombre y el DNI.
- La pregunta quedaba antes de la transcripción.

En esta vuelta, las preguntas de token van **al final del mensaje del usuario**. Reemplazan «Evaluá la llamada con lo
disponible hasta la línea n.» y son lo último que lee el modelo; el resto del mensaje no cambia
(`detectores.PREGUNTAS_FINALES`).

**Alcance, decidido por el equipo el 2026-11-06.** El detector corre solo en **llamadas entrantes de números no
agendados**, como Scam Detection de Google y el detector de Samsung. Quién inició cada caso de desarrollo quedó
anotado a ciegas en [`casos/alcance-desarrollo.json`](../casos/alcance-desarrollo.json).
- **Problema del corpus.** En corpus_v2, las 46 estafas son entrantes y 44 de las 51 legítimas las inicia la persona.
  Dentro del alcance quedan 7 legítimas, y son familiares y compañeros de trabajo que en un teléfono real estarían
  agendados.
- **Dos etapas.** Evaristo genera legítimas entrantes de números desconocidos: ventas, el banco que avisa un
  movimiento, el correo, turnos y encuestas.
  - **Etapa 1 (ya):** v4-L contra v4 sobre los 150. Es la prueba de la forma de leer: el mismo prompt y los mismos casos.
  - **Etapa 2 (con las legítimas nuevas):** el prompt C y `v4-premisa` ([`tarea_v4_premisa.txt`](tarea_v4_premisa.txt):
    v4 con la oración del alcance), que dicen el alcance como un dato fijo. Se deciden dentro del alcance.
- **Cambio en C el 2026-11-07, antes de correrlo sobre las legítimas nuevas:** la lista de pedidos termina en «…, o
  cortar y llamar enseguida a otro número que le dictan». Es la opción 1 del estafador que te hace llamar a vos
  ([ideas pendientes, §0 bis](../corridas/2026-11-06_puntaje-token-2/IDEAS-PENDIENTES.md#0-bis-el-estafador-que-te-hace-llamar-a-vos)).
  No sale del corpus. El tag `colab/143-ronda-2` tiene la versión anterior, y la etapa 1 solo la usó para la humo de
  formato. La etapa 2 la repite.

| Variante | Mensaje de sistema | Pregunta final (mensaje del usuario) | Se lee con | Compara con |
|---|---|---|---|---|
| `v4-lectura` (v4-L), etapa 1 | [`tarea_v4.txt`](tarea_v4.txt), el mismo de v4 | la de siempre; mismo esquema JSON, cortado después del primer decimal del riesgo | riesgo esperado (entero y primer decimal) | v4 JSON |
| `v4-premisa`, etapa 2 | [`tarea_v4_premisa.txt`](tarea_v4_premisa.txt): v4 con una sola oración más, la del alcance | la de siempre | JSON | v4 JSON |
| `c-json`, etapa 2 | [`tarea_c.txt`](tarea_c.txt) + [`salida_json_c.txt`](salida_json_c.txt) | la de siempre | JSON | v4 JSON |
| `c-sino`, etapa 2 | [`tarea_c.txt`](tarea_c.txt) | [`pregunta_c_sino.txt`](pregunta_c_sino.txt): «¿conviene avisarle ya a PROTEGIDA que esta llamada puede ser una estafa? Respondé solo SÍ o NO.» | P(SÍ) | `c-json` |
| `c-digito`, etapa 2 | [`tarea_c.txt`](tarea_c.txt) | [`pregunta_c_digito.txt`](pregunta_c_digito.txt): «¿qué tan probable es que esta llamada sea una estafa? Respondé solo con un número del 0 (nada probable) al 9 (casi seguro).» | dígito esperado / 9 | `c-json` |
| `c-sin-alerta`, etapa 3 | [`tarea_c.txt`](tarea_c.txt) + [`salida_json_c_sin_alerta.txt`](salida_json_c_sin_alerta.txt): el JSON pide solo el riesgo | la de siempre | riesgo escrito, «≥ 0,3» | `c-json-corte` (etapa 2) |
| `c-con-campo`, etapa 3 | [`tarea_c.txt`](tarea_c.txt) + [`salida_json_c_con_campo.txt`](salida_json_c_con_campo.txt): `pedido_critico` y después el riesgo | la de siempre | «riesgo ≥ 0,3 o `pedido_critico`»; el campo es la alerta fuerte | `c-sin-alerta` |
| `c-json-corte-riesgo`, configuración congelada | el mismo de `c-json` | la de siempre; mismo esquema JSON, cortado justo después de la coma del riesgo (`num_predict` 14) | riesgo escrito, «≥ 0,3»; el motivo de C ([`motivo_c_corte.txt`](motivo_c_corte.txt)) en el primer aviso | la lectura de `c-json-corte` solo en las líneas de OTRA (etapa 3) |

- **C** es un prompt nuevo, pedido por Mateo:
  - Dice el alcance: PROTEGIDA recibió la llamada de un número que no tiene agendado.
  - Describe cómo se arma una estafa: quien llama se presenta como alguien de confianza, plantea algo que preocupa,
    apura o entusiasma, y lleva a la persona a entregar o hacer algo.
  - Pide mirar la llamada entera y hacia dónde va, y **avisar aunque todavía no haya un pedido**.
  - Ya no dice «Marcá "alerta_sugerida": true solo si OTRA le pide…», ni ata el motivo al pedido.
  - Mantiene la opción (a): pedir el nombre, el DNI, la fecha de nacimiento, una dirección o un correo, o avisar un
    problema u ofrecer un producto, no vuelve estafa una llamada.
  - La lista de acciones coincide con las listas de «nunca te vamos a pedir» de los bancos
    ([fuentes](../corridas/2026-11-06_puntaje-token-2/FUENTES.md)); no sale del corpus.
- **Antecedentes:** A2 en la primera vuelta y `v5-maniobras` ya buscaron la intención sin pedido y sumaron falsas
  alarmas. C cambia más cosas a la vez: el encuadre entero, no una regla agregada.
- **v4-L** no cambia nada del pedido de v4: el mismo prompt, el mismo mensaje y el mismo esquema.
  - Deja generar solo 12 tokens con `logprobs` y lee la distribución del entero y del primer decimal del riesgo
    dentro del JSON (`detectores.leer_riesgo_json`). Es la comparación más limpia.
  - El JSON de v4 escribe el riesgo con un solo decimal: en la línea base, de 0,0 a 0,9, con el 94 % de las líneas entre
    0,0 y 0,3. v4-L lee la distribución completa (valor esperado), como G-Eval.
  - Antecedente: en Open-Jev (arXiv 2609.23959, 2026), con un modelo ajustado, leer la probabilidad de la etiqueta en el
    comienzo del JSON da AUROC 0,95, contra 0,875 de la etiqueta escrita. Sin ajuste fino, leer los logits dio 0,69.
- **Dígito:** se suman las probabilidades de los dígitos 0–9 entre las 20 alternativas del primer token
  (`detectores.leer_digito`). Gemma parte los números en dígitos sueltos; la humo controla que el modelo no quiera
  escribir «10».
- **Preparadas y reemplazadas antes de correr:**
  - S ([`tarea_s.txt`](tarea_s.txt): `s-json`, `s-sino`, `s-digito`): C la reemplaza porque mira la intención.
  - v4-D ([`tarea_v4_d.txt`](tarea_v4_d.txt): `v4-digito`): v4-L la reemplaza como prueba de la lectura con el prompt de
    v4.
  - (`v4-premisa` y C no fueron reemplazadas: corren en la etapa 2.)

## Versión 3 — 2026-11-04

> **Estado: propuesta sin discutir.** [Resultados](../corridas/2026-11-04_193946_prompt-v3-a-solo-y-con-indicio/analisis.md) y [ficha](V3-ATRIBUCION.md), avance de #51
> vinculado a [D07](../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y
> [D08](../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

La v3 parte de la v2 y reúne varios cambios, así que un efecto no se atribuye a una frase. Usa
`ESQUEMA_SALIDA_V2` (`v3`) o el esquema de v1 (`v3-orden-v1`). El borrador anterior, derivado de v1,
se conserva en el commit `8a718fe`.

## Criterios de la v1

- **`tarea`** define qué es una alerta con las seis acciones solicitadas del
  [manual](../../../docs/corpus/MANUAL-ANOTACION.md#acciones-solicitadas) y su
  regla central: mencionar, aconsejar o negar no es pedir. No incluye ejemplos de
  los casos de prueba, para no ajustar el prompt a las respuestas.
- **`base_institucional.txt`** es el texto del laboratorio sin cambios
  (`experiments/laboratorio/detector.py`, rama `laboratorio-main`), que a su vez
  viene del marco #27 de Luciano. Se conserva igual para poder comparar con la
  hipótesis H5 del [contraste](../../../docs/investigacion/CONTRASTE-NLP-TEORIA-Y-LABORATORIO.md).
  Sus afirmaciones **no fueron cotejadas con fuentes** en este ensayo; la regla 4,
  por ejemplo, es más absoluta que lo que respaldan las fuentes del catálogo.

## Criterios de la v2

> **Estado: propuesta sin discutir.** Sale del
> [análisis de errores del 2026-10-21](../analisis/2026-10-21-errores-y-prompt-v2/README.md)
> sobre los mismos 53 casos de desarrollo: está ajustada a ellos y solo se puede evaluar
> de forma justa con casos reservados (#55). No usar el test del corpus v2 para afinarla.

- **Sin el ejemplo del «código».** El motivo tiene que nombrar lo que se pidió. El
  ejemplo de la v1 hacía que 0.8B y 2B dijeran «código» ante pedidos de dinero, fotos
  o pantalla.
- **La cita va primero.** El esquema pide `evidencia`, después `alerta_sugerida`,
  `riesgo` y `motivo`, y la alerta se ata a haber copiado un pedido. En la v1 el
  modelo decidía la alerta antes de escribir la cita, y el 2B dejó 49 líneas con riesgo
  ≥ 0,6 sin alerta.
- **Pedido sin palabras clave o con una razón creíble.** Se aclara que cuenta aunque no
  nombre el código o la transferencia y aunque la razón parezca válida: es el error más
  repetido del 2B (deudas, accidentes, «girame a la cuenta que te dicto»).
- **Lo que no es pedido**, en una lista: mencionar, aconsejar, negar, negarse, relatar
  un pedido de otra llamada o plantearlo como hipótesis. Apunta a los avisos del 4B
  por pedidos relatados y por sospecha.
- **La sospecha sube el riesgo, pero no alerta.** Repite la regla de la v1 (alerta solo
  por pedido) de forma explícita. Si el equipo decide en D08 que la sospecha también
  avise, esto cambia.
- Riesgo de al menos 0,5 cuando hay alerta, para que `riesgo` y `alerta_sugerida` no se
  contradigan.

Los cambios se prueban juntos: no se midió el aporte de cada uno por separado.

## Historial

| Fecha | Cambio | Motivo |
|---|---|---|
| 2026-10-13 | v1 | Primera versión para el ensayo #50. |
| 2026-10-21 | v2 (`tarea_v2.txt`, variante `v2`); la v1 queda igual | Errores de la v1 en las corridas del 2026-10-14 y 2026-10-17 (ver «Criterios de la v2»). |
| 2026-10-29 | `riesgo` (`riesgo.txt` + `riesgo_motivo.txt`), en dos etapas; v1 y v2 quedan igual | Bajar la latencia por línea: escribir el JSON completo domina el tiempo ([caché de prefijo](../analisis/2026-10-21-cache-prefijo/README.md)). Escala del riesgo anclada y «una palabra suelta no es pedido» por la minuta del 2026-10-28 (R07). Ver [análisis](../analisis/2026-10-29-riesgo-primero/README.md). |
| 2026-11-04 | v3, borrador P1 (`tarea_v3.txt`), sin integrar al ejecutor; v1/P0 y v2 intactas | Una hipótesis: atribuir el pedido dentro de la llamada frente a relato, hipótesis, ofrecimiento y consejo. [Ficha y controles](V3-ATRIBUCION.md); sin inferencia nueva. |
| 2026-11-04 | v3 reemplazada por un texto basado en v2; v1 y v2 intactas | Decisiones del grill con Luciano. [Probada en Colab sobre los 150 de desarrollo](../corridas/2026-11-04_193946_prompt-v3-a-solo-y-con-indicio/analisis.md): no se adopta. |
| 2026-11-04 | v4 (`tarea_v4.txt`) y `v3-orden-v1`; v1, v2 y v3 intactas | Bajar las falsas alarmas de v3 y darle al SLM el rol que en la llamada da el canal. [Probadas en Colab](../corridas/2026-11-04_193946_prompt-v3-a-solo-y-con-indicio/analisis.md): 55/75 estafas y 13/75 falsas alarmas con Tito sin indicio. |
| 2026-11-05 | `v4-cita-libre` (`tarea_v4_cita_libre.txt`) y tanda de roles; v1–v4 intactas | Medir si exigir citar a `OTRA` en `evidencia` frena avisos y separar el efecto de `--hablantes rol` en v1 y `v3-orden-v1`. [Resultados en Colab](../corridas/2026-11-04_193946_prompt-v3-a-solo-y-con-indicio/analisis.md#tanda-de-roles-qué-dejó): `v4-cita-libre` 55/75 y 12/75, `v4` repetida 55/75 y 13/75; no se adopta `v4-cita-libre`. |
| 2026-11-05 | v5 (`v5-maniobras`, `v5-indirectos`, `v5-sin-excepcion`, `v5`); v1–v4 intactas | Probar sobre v4 la regla de maniobras sin pedido explícito, los pedidos indirectos y quitar la excepción de datos comunes, por separado y juntos, más 18 controles sintéticos. [Resultados en Colab](../corridas/2026-11-05_prompt-v5-tito-sin-indicio/analisis.md): ninguna mejora a v4 de forma consistente (maniobras 57/16, indirectos 55/12, sin excepción 56/13, las tres 57/13) ni detecta las estafas sin pedido del corpus. No se adopta v5. |
| 2026-11-05 | `tarea-sino`, `v4-sino` y `v4-sin-reglas-sino`; v1–v5 intactas | #143: leer P(SÍ) del primer token en vez del riesgo escrito, que solo toma 0,1/0,2/0,3/0,5 y da dos puntos de operación. Ver «Pregunta SÍ/NO». |
| 2026-11-05 | `tarea-a1`, `v4-a1` y `v4-a2` (A1 y A2 de #143); los tres `*-sino` quedan como humo 1, descartados | El issue pasó a definir A1 (sin «Marcá "alerta_sugerida"…», pregunta por el pedido) y A2 (pregunta por la intención). La [humo 1](../corridas/2026-11-05_humo-puntaje-token-1/humo.md) no pasó: masa SÍ+NO ≥ 0,9 en solo 31–38 de 48 líneas, porque el modelo responde «al…» («alerta_sugerida: true») cuando quiere avisar. La [humo 2](../corridas/2026-11-05_humo-puntaje-token-2/humo.md) pasa: 48 de 48 en las tres variantes. |
| 2026-11-05 | `v4` como valor por defecto de la demo en vivo (`servidor.py`, `medir.py`) con `--hablantes rol` y `--sin-indicio` | Por pedido de Luciano tras comparar v1, v3, v4 y v5 sobre los 150 de desarrollo; ADR 0001 sigue pendiente de reabrir con el equipo. |
| 2026-11-06 | `v4-lectura` (etapa 1), `v4-premisa`, `c-json`, `c-sino` y `c-digito` (etapa 2, con legítimas entrantes) de la segunda vuelta de #143; `s-*` y `v4-digito` quedan preparados pero no corren; los prompts anteriores quedan intactos | La primera vuelta no fue justa con el token: hacía otra pregunta y la ponía antes de la transcripción. C dice el alcance (llamadas entrantes de números no agendados), mira la intención y hacia dónde va la llamada, no el pedido, y mantiene la opción (a). Se evalúa con las legítimas entrantes nuevas, porque corpus_v2 casi no las tiene. Ver [la segunda vuelta](#segunda-vuelta-2026-11-06-alcance-prompt-c-pregunta-al-final-y-lectura-del-token). |
| 2026-11-09 | `c-sin-alerta` y `c-con-campo` (el texto de tarea de C con un JSON más corto), y el motivo propio de C ([`motivo_c_corte.txt`](motivo_c_corte.txt)), que se pide solo en la alerta fuerte; C y los demás intactos | Etapa 3 de #143: 7 de los 12 errores de C son pedidos explícitos de un código o una clave en contextos amables. La definición del campo la escribió Mateo, por el propósito y con ejemplos de fuentes externas ([`FUENTES.md`](../corridas/2026-11-09_pedido-critico-etapa-3/FUENTES.md)), no de los fallos. Regla en [`corridas/2026-11-09_pedido-critico-etapa-3/`](../corridas/2026-11-09_pedido-critico-etapa-3/README.md). |
| 2026-11-10 | `c-json-corte-riesgo`: el prompt de `c-json` sin cambios, cortado tras el riesgo, con el motivo de C en el primer aviso | La configuración que congeló Mateo el 2026-11-09, para correrla como tal: hasta acá el corte tras el riesgo se leía de `c-json-corte`. Prueba de humo en [`corridas/2026-11-10_config-congelada-humo/`](../corridas/2026-11-10_config-congelada-humo/README.md). |
