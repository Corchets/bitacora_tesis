# Resultados del prompt v3 con Gemma 4 E2B: SLM solo, Tito con indicio y Tito sin indicio

**Fecha:** 2026-11-04. **Issue:** [#51](https://github.com/Corchets/bitacora_tesis/issues/51), sigue abierto.

> **Estado: propuesta sin discutir.** Diagnóstico sobre los 150 casos de desarrollo, ya vistos y con
> referencias sin revisión humana. No es una evaluación final. No toca la reserva, no decide
> [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) ni
> [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental) y no cambia el
> [ADR 0001](../../../../docs/ingenieria/adr/0001-parakeet-filtro-y-gemma4-e2b-con-tito-viejo.md).

## Conclusión

**El prompt v3 no sirve para adoptarlo como está.** Avisa en más estafas que v1, pero las falsas alarmas
se disparan y muchos avisos llegan antes del pedido o se apoyan en un pedido inventado. Ninguna de las
tres condiciones cumple la meta del tutor: 80–85 % de estafas con 10–15 % de falsas alarmas. La
configuración vigente sigue siendo Tito viejo con indicio y el prompt v1 (`tarea`).

La hipótesis previa era que v3 podía perder estafas por ser más estricto. Ocurrió lo contrario.

## Qué se probó

Las tres condiciones usan el mismo prompt, [`tarea_v3.txt`](../../prompts/tarea_v3.txt). Es v2 sin el
mínimo de riesgo 0,5, con reglas de contexto, y conserva el orden de campos de v2 (la evidencia va
primero).

| Condición | Cuándo se consulta al SLM | Qué recibe el SLM |
|---|---|---|
| **SLM solo** | En cada línea | La conversación |
| **Tito con indicio** | Desde que Tito activa | La conversación, más la línea marcada por Tito y su puntaje |
| **Tito sin indicio** | Desde que Tito activa | La misma conversación que el SLM solo |

Tito es siempre el mismo clasificador, con umbral 0,5. Una vez que activa, queda activo hasta el final
de la llamada.

## Resultados

| Medida | v1 solo (Windows) | v1 Tito con indicio (Windows) | **v3 solo** | **v3 Tito con indicio** | **v3 Tito sin indicio** |
|---|---:|---:|---:|---:|---:|
| Estafas con aviso | 55/75 (73 %) | 51/75 (68 %) | **65/75 (87 %)** | **63/75 (84 %)** | **64/75 (85 %)** |
| Estafas con pedido que tuvieron aviso | 54/64 | 51/64 | **64/64** | **62/64** | **63/64** |
| Falsas alarmas | 18/75 (24 %) | 13/75 (17 %) | **47/75 (63 %)** | **30/75 (40 %)** | **35/75 (47 %)** |
| Falsas alarmas en legítimas comunes | 3/51 | 5/51 | **28/51** | **17/51** | **20/51** |
| Falsas alarmas en legítimas difíciles | 15/24 | 8/24 | **19/24** | **13/24** | **15/24** |
| Aviso antes del pedido | 25 | 17 | **43** | **36** | **42** |
| Aviso en el pedido | 25 | 29 | **20** | **23** | **18** |
| Aviso después del pedido | 4 | 5 | **1** | **3** | **3** |
| Consultas al SLM | 2.218 | 1.179 | **1.680** | **867** | **791** |
| Fallos técnicos | 0 | 0 | **0** | **0** | **0** |

Las corridas cortan en el primer aviso. Por eso v3 hace menos consultas que v1: avisa antes, no es más
eficiente. «Pedido» es la línea `T_R` de la referencia, que existe en 64 de las 75 estafas.

## Qué significan

### 1. v3 alerta más, no discrimina mejor

Contra v1, en las dos comparaciones con par, v3 no pierde ninguna estafa y tampoco elimina ninguna falsa
alarma: solo agrega avisos.

| Comparación | Estafas ganadas | Falsas alarmas nuevas |
|---|---:|---:|
| v1 solo → v3 solo | 10 | 29 |
| v1 Tito con indicio → v3 Tito con indicio | 12 | 17 |

### 2. Lo que más se quería corregir sigue fallando

Las decisiones del prompt pedían no alertar por un dato solo cuando el contexto lo explica. TR-13 (turno
médico con DNI) y TR-08 («pasame el código» ambiguo) siguen alertando en las tres condiciones, y aparecen
falsas alarmas nuevas en gestiones comunes:

| Caso legítimo | Línea que cita el modelo | Lo que le dice a la persona |
|---|---|---|
| `CV2-D-L-BANCO-009` | «Me acuerdo que marqué el PIN y después quedó cargando.» | Le están pidiendo que confirme el PIN. Es falso: el cliente relata lo que hizo. |
| `CV2-D-L-MEDICO-001` | «¿Y el copago lo pago ahí o por transferencia?» | Le están pidiendo si va a pagar. Es la persona quien pregunta. |
| `CV2-D-L-ESCUELA-004` | «¿Querés actualizar el correo en la ficha de estudiante?» | Podría ser para acceder a sus cuentas. |
| `TR-03-negacion-y-consejo` | «¿Y si me dicen que tengo que transferir…?» | La están presionando. Es una pregunta hipotética. |

Los ejemplos son del SLM solo.

### 3. Las estafas ganadas valen menos de lo que parece

Contar un aviso no prueba que sea por la razón correcta: **de las 64 estafas con pedido, el SLM solo avisa
antes del pedido en 43** (25 con v1). Los tres casos que Luciano pidió mirar muestran esa diferencia:

| Caso | Pedido | v3 solo | v3 Tito con indicio | Lectura |
|---|---:|---:|---:|---|
| `BANCO-003` | L19 | L14, cita L13 | **L19, cita el pedido** | Con indicio acierta. El solo avisa antes, por una frase previa sobre el mensajero. |
| `PREMIO-003` | L13 | L15, cita L13 | L16, cita L13 | Razonable: cita el pedido de documento, con demora. |
| `SOPORTE-005` | L16 | L11, cita L10 | L10, cita L10 | Avisa por «salí de la sesión», antes de pedirse la contraseña. |

Otro ejemplo: en `FAMILIAR-006`, Tito sin indicio avisa en L23, después del pedido, citando a la persona
que dice «No transfiero hasta confirmar con tu mamá».

### 4. El modelo no respeta el formato de evidencia

El prompt pide evidencia vacía si no hay base para alertar. El SLM solo copia una cita en **1.003 de 1.568
líneas sin alerta** (64 %); con v1 no ocurre en ninguna. Además, 60 de sus 112 avisos usan «podría» para
justificar el peligro.

**Hipótesis, sin probar:** pedir la cita primero y nombrar «el peligro concreto» empuja al modelo a buscar
un pedido en cualquier línea y a justificarlo después. v3 reúne varios cambios, así que estos resultados
no permiten atribuir el efecto a ninguno.

### 5. Tito sigue ayudando, y sacar el indicio no mejora

| Comparación con v3 | Estafas | Falsas alarmas | Consultas |
|---|---:|---:|---:|
| SLM solo → Tito con indicio | −2 | −17 | −813 |
| SLM solo → Tito sin indicio | −1 | −12 (elimina 13, agrega 1) | −889 |
| Tito con indicio → Tito sin indicio | +1 | +5 | −76 |

Tito con indicio es la mejor de las tres condiciones v3 por falsas alarmas. Sus 30 aparecen también en las
otras dos. Esto vale para v3: el efecto de sacar el indicio con v1 se sabrá con la corrida que hace otra
persona del equipo.

## Límites

- **Máquinas distintas:** v1 corrió en Windows y v3 en Colab, sin control v1 en la misma sesión. La
  diferencia es grande, pero esta prueba no separa el efecto del prompt del de la máquina. Por eso
  tampoco se comparan tiempos.
- **Sin repetición:** no se midió el ruido entre corridas iguales, así que las diferencias de 1 a 3 casos
  entre condiciones v3 no se leen como efecto.
- **Datos ya vistos:** el prompt se diseñó mirando estos 150 casos. Las referencias, incluidas las líneas
  `T_R`, no tienen revisión humana.
- **Solo primer aviso:** no se sabe si la alerta se sostendría después.
- **Muestras:** los ejemplos ilustran fallos y no reemplazan una revisión de todos los avisos.

## Casos

Los nombres omiten el prefijo `CV2-D-V-` o `CV2-D-L-`.

**Estafas sin aviso en las tres condiciones (10), ninguna con pedido de referencia:**
BANCO-012, ORGANISMO_PREVISIONAL-005, ORGANISMO_PREVISIONAL-006, PREMIO-005, PREMIO-006, SOPORTE-007,
SOPORTE-008, WHATSAPP-007, WHATSAPP-008 y `TR-12-corta-antes-del-pedido`.

**Estafas con pedido que pierde Tito:** con indicio, FAMILIAR-006 y PREMIO-001; sin indicio, PREMIO-001.

**Estafas que gana el SLM solo contra v1:** BANCO-003, FAMILIAR-004, FAMILIAR-005, FAMILIAR-006,
ORGANISMO_PREVISIONAL-003, ORGANISMO_PREVISIONAL-004, PREMIO-003, SOPORTE-005, WHATSAPP-004 y
`TR-04-pedido-tras-charla-larga`.

**Estafas que gana Tito con indicio contra v1:** BANCO-003, BANCO-011, FAMILIAR-004, FAMILIAR-005,
ORGANISMO_PREVISIONAL-003, ORGANISMO_PREVISIONAL-004, PREMIO-002, PREMIO-003, SOPORTE-001, SOPORTE-005,
WHATSAPP-004 y `TR-01-pedido-indirecto-digitos`.

**Falsas alarmas en las tres condiciones (30):** BANCO-001, BANCO-002, BANCO-004, BANCO-005, BANCO-006,
BANCO-010, ESCUELA-004, FAMILIAR-002, FAMILIAR-005, MEDICO-002, ORGANISMO_PREVISIONAL-001, PREMIO-002,
SOPORTE-004, SOPORTE-005, TRABAJO-001, TRABAJO-003, WHATSAPP-001, `LAB-anses-canal-oficial`,
`LAB-arca-canal-oficial`, `LAB-banco-app-parafrasis`, `LAB-banco-revisa-app`, `LAB-familiar-llama-vos`,
`LAB-no-bajes-nada`, `LG-BANK-VERIF-01-e01`, `LG-SUPPORT-INFO-01-e01`, `TR-05-asado-con-transferencia`,
`TR-06-banco-alerta-legitima`, `TR-08-frase-cortada-candado`, `TR-11-familiar-real-pide-plata` y
`TR-13-turno-medico-pide-dni`.

El detalle línea por línea está en los CSV y en la
[comparación generada en Colab](comparacion-tres-condiciones.md).

## Cómo se corrió

| Dato | Valor |
|---|---|
| Entorno | Google Colab con GPU T4, Ollama 0.40.14 |
| Modelo | `gemma4:e2b-it-q4_K_M`, digest `b37049369adfe3d2b653af0ab301a062ca5cbe96ace6aa0d3f2559ee9b563fc2` |
| Parámetros | Hablantes `ab`, `num_ctx` 4096, seed 42, temperatura 0, corte al primer aviso, sin reglas |
| Prompt | Variante `v3`, huella `a944aadc550480b3` |
| Tito | RoBERTuito con regresión logística, umbral 0,5. El SHA-256 del artefacto es `fb601eaa…` en Colab y `2fcf65d7…` en Windows: difieren solo por los saltos de línea |
| Datos | Los 150 de desarrollo. La rama usada no contiene la reserva |
| Código | Rama [`prompt-v3-colab`](https://github.com/Corchets/bitacora_tesis/tree/prompt-v3-colab), corridas en el commit `a42e1b5`, [notebook y procedimiento](https://github.com/Corchets/bitacora_tesis/blob/prompt-v3-colab/experiments/slm-directo/colab/README-PROMPT-V3.md) |
| Duración | SLM solo y Tito con indicio, 31,8 min; Tito sin indicio, 11,3 min, sin instalación |
| Salidas | Esta carpeta y [`2026-11-04_201116_prompt-v3-b-tito-sin-indicio`](../2026-11-04_201116_prompt-v3-b-tito-sin-indicio/) |

`--prompts v3` solo existe en `prompt-v3-colab`. En `laboratorio-luciano` el ejecutor no la tiene
registrada y la demo sigue igual.

Las cifras de v1 y v3 se recalculan, desde esta carpeta, con
`python -I comparar_con_v1.py`, sin correr modelos.

## Decisiones pendientes

> **Estado: propuesta sin discutir.** Depende de lo que decida el equipo.

1. **Próxima prueba:** usar el texto de v3 con los campos en el orden de v1, con v1 como control en la
   misma sesión de Colab. Cambia un solo factor y pone a prueba la hipótesis de la evidencia primero.
   Contradice la decisión del 2026-11-04 de conservar el orden de v2, así que requiere acuerdo.
2. **Efecto de quitar el indicio con v1:** comparar con la corrida de la otra persona, tras confirmar que
   usa la misma modificación (`slm-sin-indicio`, commit `4916ead`).
3. **Integrar `prompt-v3-colab`:** decidir si se integra a `laboratorio-main` o queda solo como registro.
