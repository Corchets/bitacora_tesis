# Por qué falla el detector: casos uno por uno y problemas del corpus

**Fecha:** 2026-11-05. **Issue:** [#51](https://github.com/Corchets/bitacora_tesis/issues/51). **Autor:** Luciano Grosso,
con análisis de Claude Opus 5.5.

> **Estado: propuesta sin discutir.** Lectura propia de los 150 casos de desarrollo, ya vistos, sin revisión humana. No
> cambia ninguna etiqueta, no toca la reserva y no decide
> [D07](../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) ni
> [D08](../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

## En dos minutos

Venimos probando prompts (v1, v3, v4), roles, con y sin indicio de Tito, y ninguna combinación llega a la meta del tutor:
**60–64 estafas avisadas de 75, con 8–11 falsas alarmas de 75**. La mejor es v4 con roles: **55/75 estafas y 13/75 falsas
alarmas**.

Leímos uno por uno los casos que fallan. La conclusión es que **la mayor parte de los errores ya no se arregla tocando el
prompt**:

- De las **20 estafas** que v4 no avisa, **15** dependen del corpus o de qué contamos como acierto, y **5** son errores limpios
  del modelo o de Tito.
- De las **13 falsas alarmas** de v4, **9** dependen del corpus o de la métrica, y **4** son errores limpios del modelo.
- Sobre las estafas que **llegan a pedir algo**, v4 avisa **54 de 64 (84 %)**, pero ese número se apoya en los casos viejos: en el
  corpus v2 es **26 de 36 (72 %)**. No alcanza con decir que la brecha es de definición: las indirectas también fallan (10 de 18).

**Actualización del mismo día, con la [tanda de roles](../corridas/2026-11-04_193946_prompt-v3-a-solo-y-con-indicio/analisis.md#tanda-de-roles-qué-dejó).**
Cuatro condiciones más confirman que el prompt ya casi no mueve el resultado: entre las 10 con Tito sin indicio, el caso explica el 80 %
de la variación y la condición, el 3 %. También corrigen cuatro cosas de la primera versión de este documento:

1. **`TR-08` no es solo culpa del corte en el primer aviso:** siguiendo la llamada, el modelo tampoco corrige. Pasa a los errores del modelo.
2. **SOPORTE-003 no se pierde por la regla de citar a OTRA:** sin esa regla tampoco vuelve.
3. **Pasarle al detector quién inició la llamada choca con D03,** que deja esa entrada fuera del alcance. Ver el [problema 3](#problema-3-falta-en-el-corpus-quién-inició-la-llamada).
4. **Separar por origen no ayuda a llegar a la meta: baja el número.** Lo que más falta es detección en el corpus v2, que es lo que tiene la reserva.

## Los resultados que estamos mirando

Todas las condiciones corrieron entre el 2026-11-04 y el 2026-11-05 en Colab con GPU T4, Gemma 4 E2B, Tito sin indicio (umbral 0,5), corte al primer
aviso y los 150 casos de desarrollo. El detalle está en el
[análisis de v3 y v4](../corridas/2026-11-04_193946_prompt-v3-a-solo-y-con-indicio/analisis.md).

| Condición | Estafas (de 75) | Con pedido (de 64) | Falsas alarmas (de 75) |
|---|---:|---:|---:|
| v1 de Evaristo | 54 | 53 | 14 |
| v1 control | 53 | 52 | 14 |
| v3 | 64 | 63 | 35 |
| v3 con el orden de v1 | 57 | 56 | 18 |
| v3 con roles | 67 | 63 | 34 |
| **v4 con roles** | **55** | **54** | **13** |
| v1 con roles | 53 | 52 | 12 |
| **v4 con cita libre** | **55** | **54** | **12** |
| v3 con el orden de v1 y roles | 55 | 54 | 19 |
| v4 con roles, repetida | 55 | 54 | 13 |

«Con pedido» son las estafas que tienen una línea `T_R` en la referencia: el momento en que el atacante pide el código, la
clave, el dato o la plata. Las otras 11 cortan antes.

## Problema 1: el porcentaje general mezcla dos corpus distintos

Los 150 casos vienen de cuatro orígenes. Separados, con v4:

| Origen | Qué son | Estafas con aviso | Falsas alarmas |
|---|---|---:|---:|
| `LAB` | Fragmentos de 2 a 7 líneas, sin saludo ni contexto | 16/16 | 2/10 |
| `SC` y `LG` | Pares escritos del piloto | 7/7 | 1/7 |
| `TR` | Trampas puntuales | 5/6 | 4/7 |
| `CV2` directas | Corpus v2, llamadas de 20 a 38 líneas, pedido explícito | 16/18 | — |
| `CV2` indirectas | Corpus v2, pedido disfrazado | 10/18 | — |
| `CV2` sin pedido | Corpus v2, cortan antes de pedir | 1/10 | — |
| `CV2` legítimas | Corpus v2: cotidianas, menciones y pedidos razonables | — | 6/51 |

En los casos viejos, el detector avisa **28 de 29** estafas. En el corpus v2, que es el realista, **27 de 46 (59 %)**. El
73 % general depende más de cuántos casos de cada tipo hay que de lo bien que detecta. Además, los 26 casos `LAB` pesan lo
mismo que una llamada de 25 líneas, aunque sean de cinco líneas.

**Esta mezcla juega a favor, no en contra.** Sacar los casos viejos no acerca a la meta: baja las estafas a 59 %, con 12 % de falsas alarmas. Y la
[reserva](DISENO-CORPUS-V2.md) es toda corpus v2. Con las tasas de v4, daría
[cerca de 60 estafas y 14 falsas alarmas de cada 100](../corridas/2026-11-04_193946_prompt-v3-a-solo-y-con-indicio/analisis.md#el-número-depende-de-la-mezcla-y-la-reserva-no-tiene-casos-viejos),
no 73. Es una cuenta, no una medición: la reserva no se corrió ni se leyó.

## Problema 2: las estafas sin pedido no se pueden aprobar con la definición actual

Son 11: BANCO-011, BANCO-012, ORGANISMO_PREVISIONAL-005 y 006, PREMIO-005 y 006, SOPORTE-007 y 008, WHATSAPP-007 y 008 (todas
`CV2-D-V-`) y `TR-12-corta-antes-del-pedido`. v4 avisa solo BANCO-011. En estos casos chocan tres cosas a la vez:

1. **Su propia referencia** dice que «la clase vishing es una hipótesis de escenario… no un acierto exigible frente a
   evidencia invisible».
2. **El [prompt v4](../prompts/tarea_v4.txt)** dice que apurar, decir ser de una entidad o hablar de un problema «no alcanza por
   sí solo para alertar».
3. **El tutor**, en la [reunión del 2026-10-28](../../../docs/gestion/seguimientos/2026-10-28.md), pidió medir la meta sobre
   **todas** las estafas, también las que cortan antes del pedido.

Con un detector que avisa por pedidos, llegar a 60 exige avisar 60 de las 64 estafas con pedido: un 94 %. En la reserva, con 20 estafas
sin pedido de cada 100, el techo de ese detector es 80/100, ni acertando todas.

**Pero no son estafas invisibles.** 8 de las 11 tienen maniobras explícitas de aislamiento o de retención, y **ninguna de las
75 legítimas tiene una frase así**:

| Caso | Maniobra |
|---|---|
| ORGANISMO_PREVISIONAL-005 | «Guardalo y no lo reenvíes a nadie», «No cortes, así no se pierde el turno» |
| ORGANISMO_PREVISIONAL-006 | «no conviene decirlo», «No cierres esta llamada, la marca se puede vencer» |
| PREMIO-005 | «no te conviene entrar todavía», «Esperá todavía no cortes» |
| SOPORTE-007 | «no cierres la pantalla del medidor por ahora» |
| WHATSAPP-007 | «no lo abras mientras la llamada siga activa», «No lo comentes en el grupo» |
| WHATSAPP-008 | «no salgas de la pantalla de chats», «No respondas a mensajes nuevos» |
| `TR-12` | «no cortes y no le cuentes a nadie, ni al abuelo», «¡No, abu, no cortes!» |
| BANCO-011 | «no cierres la sesión», «No cortes, porque si vuelve a entrar la validación queda autorizada» |

Las otras tres solo apuran (BANCO-012, SOPORTE-008) o postergan sin dar datos (PREMIO-006).

El modelo puede verlas: **BANCO-011 salta en 15 de 17 condiciones** por «no cierres la sesión» o «No cortes», aunque el prompt
le dice que eso no alcanza.

**La contracara también es un problema.** Como el corpus no tiene ninguna legítima con un «no cortes» genuino (un operador real
que te pasa con el área de fraudes, un soporte que te pide no cerrar la sesión mientras resetea), cualquier regla de maniobras
que agreguemos va a dar perfecto acá y no va a estar probada.

## Problema 3: falta en el corpus quién inició la llamada

Seis de las falsas alarmas de v4 son el mismo caso: **la persona llamó al banco o al centro de salud y le piden un dato para
identificarla**. Son BANCO-001, BANCO-002, BANCO-004, BANCO-005 y BANCO-010 (todas `CV2-D-L-`), y
`TR-13-turno-medico-pide-dni`. Por ejemplo, BANCO-002: «Para identificar la cuenta, decime los últimos cuatro dígitos». Saltan
en 9 a 17 de las 17 condiciones.

Hay tres problemas de corpus:

- **La dirección de la llamada no es un campo.** Solo aparece como frase: «llamo yo» (BANCO-001, 004 y 005) o «Atención del
  banco, buen día» (BANCO-002). En BANCO-010 ni siquiera eso: arranca con «no se si eso se saca acá».
- **La propia referencia marca esas líneas como pedido** (`REQUEST_PERSONAL_DATA`) en un caso legítimo.
- **No hay contraejemplos.** Casi ninguna estafa tiene a la víctima llamando a un número falso, como el soporte trucho que
  aparece en redes o en un buscador. La única pista es `SC-PREMIO-01-e01`, sin revisar. La excepción de v4 («si PROTEGIDA
  inició la gestión, un dato común no alcanza») no se puede validar sin esos casos, y el modelo tampoco la cumple.

**Límite de alcance.** [D03](../../../docs/gestion/MAPA-DECISIONES.md#d03--congelar-alcance-y-contribución), el
[Plan de Trabajo](../../../docs/propuesta/PLAN-DE-TRABAJO.md) y la [arquitectura](../../../docs/ingenieria/ARQUITECTURA.md) dejan la dirección
entrante o saliente **fuera de las entradas del detector**. Por eso, anotar el dato en el corpus sirve para separar resultados, pero pasárselo al modelo
exige reabrir esa decisión. Además, la demo captura por Meet, donde «quién llamó» no es lo mismo que en un celular.

## Problema 4: el corte en el primer aviso no deja medir correcciones

`TR-08-frase-cortada-candado` **falla en las 17 condiciones**:

```text
A: Pasame el código
A: del candado de la valija que me prestaste. La cerré sin pensar...
```

El caso se escribió para ver si el detector **corrige** el aviso al leer la línea siguiente. La primera versión de este documento decía que el
protocolo no dejaba aprobarlo. La corrida que sigue después del aviso muestra que eso no alcanza: **el modelo mantiene la alerta en esa línea y en todas
las que siguen**, hasta el final. Es un error del modelo.

Distinto es cuando la propia persona ofrece algo y el otro lo rechaza en la línea siguiente. `LG-BANK-VERIF-01-e01` y `TR-06-banco-alerta-legitima`
alertan una sola línea y se apagan. Ahí sí pesa lo que mide el protocolo: con [exigir dos alertas](../corridas/2026-11-04_193946_prompt-v3-a-solo-y-con-indicio/analisis.md#las-falsas-alarmas-se-apagan-solas-pero-exigir-persistencia-pierde-estafas)
salen las dos, a cambio de perder 4 estafas. Es una decisión de D08.

## Problema 5: fragmentos de laboratorio sin contexto

`LAB-banco-app-parafrasis` (falsa alarma en v4 y v1) tiene cinco líneas en minúscula:

```text
A: corta aca y fijate vos en la app del banco
B: dale a ver
A: entra con tu huella y revisa los movimientos
B: no hay nada raro
A: buenisimo era mentira entonces
```

No dice quién llama ni a quién, y la última línea supone una conversación anterior que no está. Lo mismo pasa con
`LAB-banco-revisa-app` (falsa alarma en v4 y v1), `LAB-arca-canal-oficial` y `LAB-no-bajes-nada` (falsas alarmas en v1).
`LAB-no-bajes-nada` es alguien que cuenta una estafa que recibió («me llamaron para que baje un programa»): avisar ahí no
perjudica a nadie.

## Problema 6: el límite entre estafa y pedido legítimo de plata o de clave

**Plata en familia.** FAMILIAR-004, 005 y 006 (`CV2-D-V-`) piden en condicional, en la penúltima línea y con la negativa en la
siguiente:

> «Si podés cubrir la seña ahora, te la devuelvo cuando salga de la veterinaria.»

`TR-11-familiar-real-pide-plata`, que es **legítima**, pide de forma más directa:

> «¿Me podrás transferir veinte mil pesos?»

Lo único que separa unas de otra es la historia incoherente: una prima que antes era hermana, un número prestado, una
veterinaria sin nombre. Justo eso es lo que el prompt le dice al modelo que ignore. Si avisar ante «hijo pide plata» es un
error es una pregunta de D07, no del prompt. En v1 caen además `TR-05-asado-con-transferencia` y FAMILIAR-005 legítima (aportes
entre hermanos).

**«Ingresala vos en la pantalla».** En SOPORTE-005 y SOPORTE-006, el atacante dice explícitamente que no le digan la clave,
sino que la escriban en el campo de recuperación. Que esa pantalla sea falsa no aparece antes del pedido: en SOPORTE-005 nunca,
y en SOPORTE-006 el enlace se menciona recién en la línea 16. Del lado legítimo, «entrá con tu huella y revisá los movimientos»
tiene la misma forma y cuenta como falsa alarma.

## Los errores que sí son del modelo

Con el corpus bien, estos fallan igual:

| Caso | Clase | Qué pasa |
|---|---|---|
| WHATSAPP-004 | Estafa | «No, pasámelo por acá», justo después de que la víctima lee el código de registro. Nadie lo detecta en v4 ni en v1 |
| PREMIO-001 | Estafa | Tito nunca activa, así que el SLM no se consulta. El pedido es «El DNI completo y una foto del frente» |
| PREMIO-003 | Estafa | «El número de documento. Si queda vacío, el kit vuelve al listado de suplentes» |
| ORGANISMO_PREVISIONAL-004 | Estafa | «Decime los últimos cuatro y la fecha de emisión» del trámite del DNI |
| SOPORTE-003 | Estafa | «necesito que me confirmes ambos datos» (usuario y clave). v1 sin roles avisaba antes, citando a la víctima («Me pide usuario y contraseña»). En el pedido, el riesgo queda en 0,2–0,3 también sin la regla de citar a OTRA |
| `LG-BANK-VERIF-01-e01` | Legítima | La persona ofrece «¿Querés que te diga los últimos números de la tarjeta?». El modelo ve `PROTEGIDA:` y avisa igual |
| `TR-06-banco-alerta-legitima` | Legítima | La persona ofrece «¿Te lo paso así lo verificás?», y el banco le dice que no |
| BANCO-006 | Legítima | Avisa por un consejo: «Podés cerrar esa sesión desde el menú de seguridad» |
| `TR-08-frase-cortada-candado` | Legítima | Mantiene la alerta después de leer que el código es del candado de una valija |

## Todos los casos, clasificados

Los nombres sin prefijo son `CV2-D-V-` (estafas) o `CV2-D-L-` (legítimas). «Condiciones» cuenta cuántas de las 17
configuraciones del 2026-11-04 y el 2026-11-05 avisan en ese caso; v4 está dos veces, porque se repitió.

### Estafas que v4 no avisa (20)

| Caso | `T_R` | Condiciones | v1 control | Clase de problema |
|---|---:|---:|---|---|
| BANCO-012 | — | 1/17 | sin aviso | Sin pedido, solo apuro |
| ORGANISMO_PREVISIONAL-005 | — | 0/17 | sin aviso | Sin pedido, con maniobra |
| ORGANISMO_PREVISIONAL-006 | — | 0/17 | sin aviso | Sin pedido, con maniobra |
| PREMIO-005 | — | 0/17 | sin aviso | Sin pedido, con maniobra |
| PREMIO-006 | — | 1/17 | sin aviso | Sin pedido, sin maniobra clara |
| SOPORTE-007 | — | 0/17 | sin aviso | Sin pedido, con maniobra |
| SOPORTE-008 | — | 0/17 | sin aviso | Sin pedido, solo apuro |
| WHATSAPP-007 | — | 0/17 | sin aviso | Sin pedido, con maniobra |
| WHATSAPP-008 | — | 1/17 | sin aviso | Sin pedido, con maniobra |
| `TR-12-corta-antes-del-pedido` | — | 0/17 | sin aviso | Sin pedido, con maniobra |
| FAMILIAR-004 | 22 | 4/17 | sin aviso | Plata en familia, pedido en condicional |
| FAMILIAR-005 | 20 | 4/17 | sin aviso | Plata en familia, pedido en la penúltima línea |
| FAMILIAR-006 | 22 | 3/17 | sin aviso | Plata en familia, pedido en la penúltima línea |
| SOPORTE-005 | 16 | 4/17 | sin aviso | «Ingresala vos», pantalla sin indicio de ser falsa |
| SOPORTE-006 | 15 | 13/17 | con aviso | «Ingresala vos»; v1 sin roles y v4 con cita libre avisan antes del pedido |
| SOPORTE-003 | 11 | 11/17 | con aviso | Modelo: no reacciona en el pedido |
| WHATSAPP-004 | 13 | 6/17 | sin aviso | Modelo |
| PREMIO-001 | 10 | 4/17 | sin aviso | Tito no activa |
| PREMIO-003 | 13 | 4/17 | sin aviso | Modelo |
| ORGANISMO_PREVISIONAL-004 | 14 | 6/17 | sin aviso | Modelo |

v1 control, además, no avisa BANCO-003, ORGANISMO_PREVISIONAL-003, SOPORTE-001 y `TR-04-pedido-tras-charla-larga`, que v4 sí
avisa.

### Falsas alarmas de v4 (13)

| Caso | Condiciones | v1 control | Clase de problema |
|---|---:|---|---|
| BANCO-001 | 15/17 | falsa alarma | Dato de identificación, llamó la persona |
| BANCO-002 | 17/17 | falsa alarma | Dato de identificación, llamó la persona |
| BANCO-004 | 9/17 | sin aviso | Dato de identificación, llamó la persona |
| BANCO-005 | 11/17 | sin aviso | Dato de identificación, llamó la persona |
| BANCO-010 | 17/17 | falsa alarma | Dato de identificación; no queda claro quién llamó |
| `TR-13-turno-medico-pide-dni` | 17/17 | falsa alarma | Dato de identificación, llamó la persona |
| `TR-08-frase-cortada-candado` | 17/17 | falsa alarma | Modelo: no corrige al leer la aclaración |
| `LAB-banco-app-parafrasis` | 15/17 | falsa alarma | Fragmento de laboratorio sin contexto |
| `LAB-banco-revisa-app` | 17/17 | falsa alarma | Fragmento de laboratorio sin contexto |
| `TR-11-familiar-real-pide-plata` | 17/17 | falsa alarma | Plata en familia: límite de la etiqueta |
| `LG-BANK-VERIF-01-e01` | 16/17 | falsa alarma | Modelo: la propia persona ofrece |
| `TR-06-banco-alerta-legitima` | 17/17 | falsa alarma | Modelo: la propia persona ofrece |
| BANCO-006 | 8/17 | sin aviso | Modelo: avisa por un consejo |

v1 control suma además FAMILIAR-005 legítima, `TR-05-asado-con-transferencia`, `LAB-arca-canal-oficial` y `LAB-no-bajes-nada`.

## Qué proponemos

> **Estado: propuesta sin discutir.** Las decisiones de qué cuenta como acierto son de
> [D07](../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y cómo se mide es de
> [D08](../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

**No conviene reescribir los casos que fallan para que pasen.** Ya los vimos: sería ajustar el corpus al modelo. Lo que sí
proponemos, en orden:

1. **Avisar las maniobras de aislamiento** («no cortes», «no le cuentes», «no lo abras»). Se probó en el [prompt v5](../corridas/2026-11-05_prompt-v5-tito-sin-indicio/analisis.md), y **no funcionó**: no avisa esas estafas del corpus y
   confunde consejos con tácticas. Queda como antecedente. Luciano planteó que, hasta donde cortan esas llamadas, no hay evidencia suficiente para avisar.
2. **Anotar `inicia_llamada` en los 150 casos, solo para separar resultados.** Como entrada del detector, primero hay que reabrir D03.
3. **Escribir los casos nuevos que hoy faltan, solo en desarrollo y sin tocar la reserva:** legítimas con un «no cortes» genuino y
   estafas donde la víctima llama a un número falso.
4. **Informar por separado `LAB`, `TR` y `CV2`,** con el corpus v2 como número principal, como indicó Luciano. No acerca a la meta: lo baja a 59 %, pero es
   lo que más se parece a la reserva.
5. **Decidir en D08 entre primer aviso y persistencia,** con [la simulación](../corridas/2026-11-04_193946_prompt-v3-a-solo-y-con-indicio/analisis.md#las-falsas-alarmas-se-apagan-solas-pero-exigir-persistencia-pierde-estafas): 55/13, 51/11 o 49/8.
6. **No seguir tocando la redacción para estos errores.** En [v5](../corridas/2026-11-05_prompt-v5-tito-sin-indicio/analisis.md), cuatro prompts distintos dejan igual el riesgo de 0,1 a 0,4 en la línea del pedido de las estafas que nadie avisa.

## Límites

- La clasificación es lectura nuestra, sin revisión humana, y las clases salen de casos ya vistos.
- Las referencias (`T_R`, clase, roles) tampoco tienen revisión humana.
- Salvo v4 repetida, las corridas cortan en el primer aviso. La persistencia se simuló solo sobre esa condición.
- La proyección a la reserva usa tasas de desarrollo y la composición declarada; no es una medición.
- Diferencias de 1 o 2 casos entre condiciones están dentro del ruido: repetir v1 movió 1 estafa.

## Cómo reproducir

Desde `experiments/slm-directo`, sin correr modelos:

```bash
python -I analizar_fallas_corpus.py
```

Da la tabla por origen, la lista de casos que fallan en v4 o v1 control, la activación de Tito y las maniobras de aislamiento. Las cifras de
persistencia, caso contra condición y grupos salen de `python -I comparar_con_v1_colab.py`, en la
[carpeta del análisis](../corridas/2026-11-04_193946_prompt-v3-a-solo-y-con-indicio/).
Para ver el texto de un caso y lo que citó cada condición:

```bash
python -I analizar_fallas_corpus.py --casos CV2-D-V-FAMILIAR-006 TR-08-frase-cortada-candado
```

El [script](../analizar_fallas_corpus.py) lee los CSV de las carpetas de corrida `2026-11-04*` y los archivos de [`texto/`](texto/) y
[`referencia/`](referencia/).
