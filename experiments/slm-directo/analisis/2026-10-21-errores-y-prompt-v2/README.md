# Errores del prompt v1 y primer prompt v2

> **Estado: propuesta sin discutir.** Análisis de desarrollo del ensayo
> [#50](https://github.com/Corchets/bitacora_tesis/issues/50) sobre los 53 casos escritos,
> sin revisión humana. El prompt v2 sale de mirar estos mismos casos: está ajustado a
> ellos y solo se evalúa de forma justa con casos reservados
> ([#55](https://github.com/Corchets/bitacora_tesis/issues/55)). No usar el test del
> corpus v2 para afinarlo. No elige modelo (D09) ni política (D08).

```bash
python analisis/2026-10-21-errores-y-prompt-v2/errores.py   # tabla y errores.json
```

## 1. Qué falla con el v1

Siete configuraciones ya corridas (Windows con GPU y M1), prompt `tarea`, hablantes `ab`.
Política del ensayo: primer `alerta_sugerida` verdadero.

| Configuración | Estafas con aviso | Falsas alarmas | Con cita verificada: estafas · FA | Riesgo ≥ 0,6 sin alerta | Alerta con riesgo < 0,5 |
|---|---|---|---|---|---|
| 0.8B · Windows | 26/29 | 8/24 | 24/29 · 7/24 | 0 de 464 | 0 de 95 |
| 2B · Windows (1) | 20/29 | 2/24 | 20/29 · 2/24 | 49 de 464 | 0 de 53 |
| 2B · Windows (2) | 21/29 | 2/24 | 21/29 · 2/24 | 49 de 464 | 0 de 55 |
| 4B · Windows | 29/29 | 15/24 | 29/29 · 15/24 | 6 de 464 | 0 de 220 |
| 0.8B · M1 | 27/29 | 9/24 | 26/29 · 8/24 | 0 de 464 | 0 de 100 |
| 2B · M1 | 20/29 | 2/24 | 19/29 · 2/24 | 49 de 464 | 0 de 56 |
| 4B · M1 (42/53) | 24/24 | 9/18 | 24/24 · 9/18 | 7 de 310 | 0 de 151 |
| 0.8B · M1, `num_batch` 32 | 26/29 | 9/24 | 26/29 · 8/24 | 0 de 464 | 0 de 97 |

### Las estafas que pierde el 2B

Son las mismas en las tres corridas (salvo `LAB-pantalla-sin-programa`, que en una
avisa):

| Caso | Pedido | Riesgo en el pedido | Qué pasa |
|---|---|---|---|
| `LAB-arca-deuda` y su paráfrasis | transferencia o clave fiscal | 0,1 | «tiene que autorizar con su clave fiscal o transferir hoy»: lo trata como un trámite de deuda. |
| `LAB-giro-sin-plata` | transferencia | 0,1 | «necesito que me gires ya a la cuenta que te dicto», sin la palabra «transferencia». |
| `LAB-familiar-peligro-parafrasis` | efectivo, después alias | 0,8 | Riesgo alto, pero `alerta_sugerida` falso en las dos líneas del pedido. |
| `LAB-pantalla-sin-programa` | acceso remoto | 0,8 | Igual: riesgo alto, sin alerta, y hasta copia la línea como evidencia. |
| `LAB-digitos-sin-palabra` | código, sin nombrarlo | 0,3 | «leeme lo que te acaba de llegar, de a uno». |
| `TR-01-pedido-indirecto-digitos` | código, sin nombrarlo | 0,65 | Misma maniobra, versión larga. |
| `SC-ORG-BENEFICIO-01-e01` | datos personales y foto con el documento | 0,35 (llega a 0,85) | «confirmame tu fecha de nacimiento y domicilio» para cobrar un beneficio. |
| `TR-12-corta-antes-del-pedido` | ninguno | máx. 0,2 | Sin pedido no hay alerta: es lo que pide el v1. |

Tres patrones:

1. **Pedidos de dinero con una razón creíble** (una deuda, un accidente) o sin la
   palabra clave: 4 de las 8 estafas que pierde.
2. **Pedidos indirectos** de código: 2 de 8.
3. **Riesgo y alerta no concuerdan.** El 2B deja 49 líneas con riesgo ≥ 0,6 y sin
   alerta, contra 53–56 alertas. Responde primero `riesgo` y `alerta_sugerida`, y la cita
   después: decide sin haber señalado la frase. Por eso subir el umbral de riesgo lo
   mejora (ver «Afinar» en el panel).

### Lo que ya se sabía de 0.8B y 4B

Del [análisis del 2026-10-14](../2026-10-14-fundamento-de-avisos/README.md): el 0.8B
inventa pedidos (12 de 34 avisos dicen «te están pidiendo un código» cuando nadie lo
pidió) y el 4B avisa por sospecha o por pedidos relatados (28 de 44). El ejemplo de la v1
(«Te están pidiendo un código…») se repite en los motivos aunque se pida dinero o la
pantalla.

### Verificar la cita no alcanza

Exigir que la cita del aviso aparezca en lo dicho (`evidencia_en_texto`) casi no cambia
nada: saca 1 o 2 avisos del 0.8B y ninguno del 4B. Los modelos copian texto real aunque
el pedido que describen no exista: la cita es verdadera, la interpretación no.

## 2. Prompt v2

[`prompts/tarea_v2.txt`](../../prompts/tarea_v2.txt), variante `--prompts v2`. Los criterios
están en [prompts/README.md](../../prompts/README.md#criterios-de-la-v2). En corto: la cita va
primero en el esquema y la alerta se ata a ella; el pedido cuenta sin palabras clave y
aunque la razón suene válida; mencionar, negar, relatar o plantear no es pedir; la
sospecha sube el riesgo, pero no alerta; sin el ejemplo del «código». Los cambios se
prueban juntos.

## 3. Primeros resultados del v2

Corrida [`2026-10-21_182201_m1-0.8b-v1v2-nb32`](../../corridas/2026-10-21_182201_m1-0.8b-v1v2-nb32/resumen.md),
`qwen3.5:0.8b-q8_0` en M1 con `--num-batch 32`. El v1 está completo; el **v2 quedó en
los 24 casos del laboratorio** (120 líneas) porque la corrida se cortó por memoria, con
Docker abierto. Comparación sobre esos 24 casos:

| 0.8B, 24 casos del laboratorio | Estafas con aviso | Falsas alarmas | Motivos que dicen «código» sin que se pida |
|---|---|---|---|
| v1 | 13/14 | 4/10 | 10 de 17 avisos (pedían dinero, otra cosa o todavía nada) |
| v2 | 11/14 | 2/10 | 0 de 13 |

- El v2 pierde `LAB-arca-deuda-parafrasis` y `LAB-digitos-sin-palabra` y saca las falsas
  alarmas de banco (`LAB-banco-app-parafrasis`, `LAB-banco-gasto-sin-pedido`,
  `LAB-banco-revisa-app`). Suma una nueva en `LAB-no-bajes-nada` y mantiene
  `LAB-familiar-llama-vos`, donde inventa un pedido de «DNI, CUIL».
- Los motivos ya no repiten «código», pero el 0.8B los escribe en tercera persona («El
  solicitante pide…») aunque el prompt pide hablarle a la persona.
- Son 24 casos cortos, un modelo y una corrida: **no alcanza para decir que el v2 es
  mejor.** Falta el v2 completo con 0.8B, 2B y 4B.

### 2B sobre los 150 de desarrollo

Corrida [`2026-10-21_201039_m1-2b-v1v2-nb32`](../../corridas/2026-10-21_201039_m1-2b-v1v2-nb32/),
`qwen3.5:2b-q8_0` en M1 con `--num-batch 32`, v1 y v2 completos, 0 fallos. Intervalos de
Wilson del 95 % (`errores.py`). El v2 se escribió mirando los 53 históricos: los 97 de
corpus_v2 son su primera prueba.

| 2B | Casos | Estafas con aviso | Falsas alarmas |
|---|---|---|---|
| v1 | 53 históricos | 20/29 (51–83 %) | 2/24 (2–26 %) |
| v2 | 53 históricos | 24/29 (65–92 %) | 4/24 (7–36 %) |
| v1 | corpus_v2 | 22/46 (34–62 %) | 6/51 (6–23 %) |
| v2 | corpus_v2 | 23/46 (36–64 %) | 11/51 (12–35 %) |

- **En los 53 históricos el v1 repite exactamente** los números del 2026-10-17 (tercera
  repetición): `--num-batch 32` no cambió la calidad.
- **En los históricos el v2 gana lo que se buscaba:** detecta 4 pedidos de dinero o datos
  que el v1 perdía (`LAB-arca-deuda`, `LAB-familiar-peligro-parafrasis`, `LAB-giro-sin-plata`,
  `SC-ORG-BENEFICIO-01-e01`). A cambio, suma 2 falsas alarmas en legítimas que piden un dato
  (`LG-BANK-VERIF-01-e01`, `TR-13-turno-medico-pide-dni`).
- **En corpus_v2 el v2 no mejora al 2B:** gana 3 estafas y pierde 2 (neto +1), y casi
  duplica las falsas alarmas (de 6 a 11). Las 5 nuevas son una transferencia entre
  familiares, un médico que confirma nombre y fecha de nacimiento, y tres de soporte
  donde una pregunta o un relato («¿Me vas a pedir que te pase la clave…?», «¿Ayer te
  pidieron cambiar la contraseña…?») cuenta como pedido. La instrucción «cuenta aunque la
  excusa parezca válida» choca con las legítimas que piden algo razonable, y «lo relatado
  no cuenta» no le alcanza al 2B.
- **Las estafas que cortan antes del pedido** (10 de las 46 de corpus_v2) quedan en 0/10
  con los dos prompts: un detector de pedidos no las puede ver. Con ellas en el
  denominador, el máximo posible en desarrollo es 65/75 (87 %). Si la meta de 95 % se
  mide sobre todas las estafas o solo sobre las que tienen pedido es parte de
  [D07](../../../../docs/gestion/MAPA-DECISIONES.md)/D08. **Estado: propuesta sin discutir.**
- Por tipo, el v1 en corpus_v2 avisa en 14/18 pedidos directos y en 8/18 indirectos o partidos.
- Latencia por línea: p50 1,9 s y p95 4,5 s con el v1, prácticamente igual con el v2.

**Lectura:** para el 2B, el v2 corre el punto de operación (más avisos en todo) en lugar
de separar mejor. Lo que distingue una legítima con pedido razonable de una estafa no
está en la forma del pedido sino en quién llama, quién inició y si el pedido encaja con
el motivo de la llamada. Falta ver 0.8B y 4B antes de decidir.

## 4. Pendiente

La cola del 2026-10-21 sigue con v1 y v2 del 0.8B y del 4B sobre los 150 de desarrollo;
el 9B queda para la PC con Windows (etiqueta `win-`). Con esas corridas se completa esta
sección y se vuelve a correr `errores.py`.
