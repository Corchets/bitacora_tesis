# Prompt v5: maniobras, pedidos indirectos y excepción de datos

**Fecha:** 2026-11-05. **Issue:** [#51](https://github.com/Corchets/bitacora_tesis/issues/51), sigue abierto.

> **Estado: propuesta sin discutir.** Diagnóstico sobre los 150 casos de desarrollo, ya vistos, con referencias y roles sin revisión
> humana. No es una evaluación final. No toca la reserva, no decide
> [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) ni
> [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental) y no cambia el
> [ADR 0001](../../../../docs/ingenieria/adr/0001-parakeet-filtro-y-gemma4-e2b-con-tito-viejo.md).

## Conclusión

**Ninguna variante cumple la meta** (60–64 estafas con 8–11 falsas alarmas). La mejor llega a 57/13, dos estafas más que v4, dentro de lo que
cambia entre variantes cercanas.

1. **La regla de maniobras no sirvió para lo que se escribió.** Ninguna de las 10 estafas sin pedido del corpus v2 avisa con ella, salvo
   BANCO-011, que ya avisaba. En v5, con los tres cambios juntos, se suma solo `TR-12`.
2. **Y agrega falsas alarmas del tipo que el tutor pidió evitar:** toma como táctica consejos como «no abras ningun sitio del mensaje».
3. **Las reglas de pedidos indirectos y de la excepción no recuperaron lo que apuntaban.** En la línea del pedido, las 8 estafas que nadie
   avisa siguen con riesgo de 0,1 a 0,4, salvo PREMIO-001, donde Tito no activa. Cambiar la redacción no mueve eso.
4. **Sacar la excepción de datos suma poco:** recupera SOPORTE-003 y SOPORTE-006, dos pedidos de credenciales, y pierde PREMIO-002.
5. **Exigir dos alertas no lo arregla:** sin la excepción da 53/8 y entra en la franja de falsas alarmas, pero vuelve a perder esos dos pedidos de credenciales.

Ninguna variante le gana a v4 con una diferencia que se pueda defender.

## Resultados

Colab con GPU T4, Tito sin indicio, umbral 0,5, roles y 150 casos. Todas siguen tras el aviso, así que el primer aviso y las demás políticas
salen de la misma corrida. v4 es la repetición de la [tanda de roles](../2026-11-04_tanda-roles-tito-sin-indicio/). Ninguna corrida tuvo fallos técnicos.

| Condición | Primer aviso | 2 en la llamada | 2 seguidas | 3 en la llamada | 3 seguidas |
|---|---:|---:|---:|---:|---:|
| v4 | 55/13 | 51/11 | 49/8 | 48/6 | 47/4 |
| v4 con maniobras (`v5-maniobras`) | 57/16 | 53/12 | 53/11 | 52/8 | 51/7 |
| v4 con pedidos indirectos (`v5-indirectos`) | 55/12 | 50/8 | 49/7 | 47/5 | 47/4 |
| v4 sin la excepción (`v5-sin-excepcion`) | 56/13 | **53/8** | 51/7 | 51/4 | 47/3 |
| Los tres juntos (`v5`) | 57/13 | 54/10 | 54/9 | 53/5 | 51/5 |

| Condición, primer aviso | Corpus v2: estafas de 46 | Con pedido de 36 | Falsas alarmas de 51 | Antes / en / después del pedido | Cita el pedido | Cita solo a la víctima |
|---|---:|---:|---:|---:|---:|---:|
| v4 | 27 | 26 | 6 | 18 / 34 / 2 | **36** | 2 |
| `v5-maniobras` | 29 | 28 | 6 | 29 / 23 / 4 | 25 | 3 |
| `v5-indirectos` | 27 | 26 | 6 | 18 / 32 / 4 | 34 | 2 |
| `v5-sin-excepcion` | 28 | 27 | 7 | 21 / 30 / 4 | 32 | 2 |
| `v5` | 28 | 27 | 4 | 26 / 24 / 5 | 27 | 2 |

Las reglas nuevas adelantan avisos: `v5-maniobras` tiene 11 más antes del pedido y cita el pedido en 11 casos menos. Es un costo que el número de
estafas no muestra.

### Qué cambia cada una contra v4

| Condición | Gana | Pierde | Falsas alarmas que agrega | Que saca |
|---|---|---|---|---|
| `v5-maniobras` | SOPORTE-003, SOPORTE-006 | — | `LAB-arca-canal-oficial`, `LAB-banco-gasto-sin-pedido`, `TR-05` | — |
| `v5-indirectos` | — | — | — | `LG-BANK-VERIF-01-e01` |
| `v5-sin-excepcion` | SOPORTE-003, SOPORTE-006 | PREMIO-002 | ESCUELA-004 | `LG-BANK-VERIF-01-e01` |
| `v5` | SOPORTE-003, SOPORTE-006, `TR-12` | PREMIO-002 | `LAB-arca-canal-oficial`, `LAB-banco-gasto-sin-pedido` | BANCO-005, BANCO-006 |

SOPORTE-003 y SOPORTE-006 también vuelven con la regla de maniobras, aunque esa regla no habla de credenciales. Puede ser sensibilidad a cualquier cambio
del prompt y no efecto de la regla: una sola corrida no lo separa.

### Las hipótesis que no se cumplieron

| Hipótesis | Resultado |
|---|---|
| La regla de maniobras avisa las estafas sin pedido | No. WHATSAPP-007 sigue con riesgo 0,3 y sin alerta en «No lo comentes en el grupo todavía» |
| Ampliar los pedidos indirectos recupera FAMILIAR y SOPORTE-005 | No: ni una estafa de más |
| Sacar la excepción recupera PREMIO-003 y ORGANISMO_PREVISIONAL-004 | No: siguen en 0,1 y 0,4 |
| Sacar la excepción dispara las alarmas por dato de identificación | Agrega una sola, ESCUELA-004, y saca `LG-BANK-VERIF-01-e01`. Las de dato ya estaban con la excepción |

### Controles de maniobras

[18 casos aparte](../../casos/controles-maniobras.json), que no se suman a los 150. Con Tito → SLM:

| Prompt | Estafas (de 6) | Legítimas con aviso (de 12) |
|---|---:|---|
| v4 | 1 | `CTRL-L-BANCO-AVISO-CORREO` |
| `v5-maniobras` | 4 | `CTRL-L-BANCO-AVISO-CORREO` |
| `v5` | 2 | `CTRL-L-BANCO-AVISO-CORREO` |

**Ninguna legítima con un «no cortes» genuino salta,** ni siquiera con el SLM sin Tito. La única falsa alarma es el consejo de no abrir un correo, que también
tiene v4. Esto no valida la regla, por tres razones:

- **Los controles son más fáciles que el corpus.** Los escribió quien escribió la regla, y sus estafas amenazan de forma mucho más explícita. Dan 4/6 con la regla, cuando en el corpus da 0.
- **Dos de esos cuatro avisos no son por la maniobra:** `CTRL-V-BANCO-QUEDATE-EN-LINEA` avisa en la línea 1 y `CTRL-V-TECNICO-COMPU` en la 4, antes de que aparezca.
- **Tito decide primero:** en `CTRL-V-CAUSA-JUDICIAL` y `CTRL-V-SORTEO-RESERVA` no activa, y ningún prompt puede avisarlas.

## Próximo paso

> **Estado: propuesta sin discutir.** Depende de lo que decida el equipo. Adoptar cualquiera implica reabrir el ADR 0001.

- **Dejar afuera la regla de maniobras.** No avisa su objetivo y confunde consejos con tácticas. Coincide con lo que planteó Luciano el 2026-11-05: en esas llamadas, hasta donde
  cortan, no hay evidencia suficiente para avisar.
- **No seguir tocando la redacción para los pedidos que fallan.** El riesgo en esas líneas no se mueve con cuatro prompts distintos.
- **Candidata: v4 con roles, sin indicio y primer aviso (55/13).** Es la más simple, la única repetida (avisó en los mismos 68 casos) y la que más cita el pedido real. En el corpus v2 da 27/46 y 6/51 (12 %, en
  la franja), con 0/25 en cotidianas.
- **Alternativa a un caso de distancia:** `v5-sin-excepcion` con primer aviso (56/13; 28/46 y 7/51 en el corpus v2). Recupera SOPORTE-003 y SOPORTE-006, pero suma una alarma en una cotidiana, y cita menos el pedido.
- **Persistencia, por ahora no.** Con el corpus v2 como número principal, las falsas alarmas ya están en la franja, y lo que falta es detección. `v5-sin-excepcion` con 2 en la llamada pasa de 28/7 a 25/3
  en ese corpus: saca 4 alarmas y pierde 3 estafas, entre ellas los dos pedidos de credenciales. Además, hoy solo está simulada.

## Límites

- Prompts, políticas y controles salen de casos ya vistos: elegir acá no estima el rendimiento. Eso sale de la reserva.
- Diferencias de 1 o 2 casos no se leen como efecto. v4 es la única de estas que se corrió dos veces, y las dos veces avisó en los mismos casos.
- La persistencia se simula sin avisarle al modelo que ya alertó, y no mide cuánto tarda en llegar el aviso a la persona.
- La reserva puede cambiar: hay una corrección en curso de sus llamadas cortadas, en otra sesión (rama `reserva-sin-cortes`). Por eso acá no se proyecta a la reserva.

## Cómo se corrió

| Dato | Valor |
|---|---|
| Entorno | Google Colab con GPU T4, Ollama 0.40.14 |
| Modelo | `gemma4:e2b-it-q4_K_M`, digest `b37049369adf…` |
| Parámetros | `num_ctx` 4096, seed 42, temperatura 0, `--seguir-tras-aviso`, sin reglas |
| Prompts | `v5-maniobras` `4d46ccb9c881e37e`, `v5-indirectos` `0535596c8b517b10`, `v5-sin-excepcion` `8ed94066e673fac4`, `v5` `e6f62043d0d95cd1` |
| Código | Rama [`prompt-v5-colab`](https://github.com/Corchets/bitacora_tesis/tree/prompt-v5-colab), commit `26e1b17`, script fijado en `f3f9a78` (SHA-256 `0374a355…`), [procedimiento](../../colab/README-PROMPT-V5.md) |
| Duración | Maniobras 21,9 min; `v5` 18,4; indirectos 17,2; sin excepción 16,8; controles 6,9 |

Las cifras salen de los CSV de esta carpeta, sin correr modelos: `python -I analizar_v5.py`, desde `experiments/slm-directo`. Las de citas y de posición del aviso usan las
definiciones de [`comparar_con_v1_colab.py`](../2026-11-04_193946_prompt-v3-a-solo-y-con-indicio/comparar_con_v1_colab.py).
