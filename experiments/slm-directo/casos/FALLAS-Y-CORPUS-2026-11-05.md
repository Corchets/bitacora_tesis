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
- De las **13 falsas alarmas** de v4, **10** dependen del corpus o de la métrica, y **3** son errores limpios del modelo.
- Sobre las estafas que **llegan a pedir algo**, v4 ya avisa **54 de 64 (84 %)**, dentro de la franja que pidió el tutor.
  La brecha la ponen las estafas que cortan antes del pedido y la mezcla de casos fáciles con casos realistas.

## Los resultados que estamos mirando

Todas las condiciones corrieron el 2026-11-04 en Colab con GPU T4, Gemma 4 E2B, Tito sin indicio (umbral 0,5), corte al primer
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

## Problema 2: las estafas sin pedido no se pueden aprobar con la definición actual

Son 11: BANCO-011, BANCO-012, ORGANISMO_PREVISIONAL-005 y 006, PREMIO-005 y 006, SOPORTE-007 y 008, WHATSAPP-007 y 008 (todas
`CV2-D-V-`) y `TR-12-corta-antes-del-pedido`. v4 avisa solo BANCO-011. En estos casos chocan tres cosas a la vez:

1. **Su propia referencia** dice que «la clase vishing es una hipótesis de escenario… no un acierto exigible frente a
   evidencia invisible».
2. **El [prompt v4](../prompts/tarea_v4.txt)** dice que apurar, decir ser de una entidad o hablar de un problema «no alcanza por
   sí solo para alertar».
3. **El tutor**, en la [reunión del 2026-10-28](../../../docs/gestion/seguimientos/2026-10-28.md), pidió medir la meta sobre
   **todas** las estafas, también las que cortan antes del pedido.

Con un detector que avisa por pedidos, llegar a 60 exige avisar 60 de las 64 estafas con pedido: un 94 %.

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

El modelo puede verlas: **BANCO-011 salta en 11 de 13 condiciones** por «no cierres la sesión» o «No cortes», aunque el prompt
le dice que eso no alcanza.

**La contracara también es un problema.** Como el corpus no tiene ninguna legítima con un «no cortes» genuino (un operador real
que te pasa con el área de fraudes, un soporte que te pide no cerrar la sesión mientras resetea), cualquier regla de maniobras
que agreguemos va a dar perfecto acá y no va a estar probada.

## Problema 3: falta en el corpus quién inició la llamada

Seis de las falsas alarmas de v4 son el mismo caso: **la persona llamó al banco o al centro de salud y le piden un dato para
identificarla**. Son BANCO-001, BANCO-002, BANCO-004, BANCO-005 y BANCO-010 (todas `CV2-D-L-`), y
`TR-13-turno-medico-pide-dni`. Por ejemplo, BANCO-002: «Para identificar la cuenta, decime los últimos cuatro dígitos». Saltan
en todas o casi todas las condiciones.

Hay tres problemas de corpus:

- **La dirección de la llamada no es un campo.** Solo aparece como frase: «llamo yo» (BANCO-001, 004 y 005) o «Atención del
  banco, buen día» (BANCO-002). En BANCO-010 ni siquiera eso: arranca con «no se si eso se saca acá». El celular real sí sabe si
  la llamada es entrante o saliente.
- **La propia referencia marca esas líneas como pedido** (`REQUEST_PERSONAL_DATA`) en un caso legítimo.
- **No hay contraejemplos.** Casi ninguna estafa tiene a la víctima llamando a un número falso, como el soporte trucho que
  aparece en redes o en un buscador. La única pista es `SC-PREMIO-01-e01`, sin revisar. La excepción de v4 («si PROTEGIDA
  inició la gestión, un dato común no alcanza») no se puede validar sin esos casos, y el modelo tampoco la cumple.

## Problema 4: casos que el protocolo no deja aprobar

`TR-08-frase-cortada-candado` **falla en las 13 condiciones**:

```text
A: Pasame el código
A: del candado de la valija que me prestaste. La cerré sin pensar...
```

El caso se escribió para ver si el detector **corrige** el aviso al leer la línea siguiente. Pero las corridas cortan en el
primer aviso, así que la corrección nunca se mide. Con esta métrica, el único detector que lo aprueba es uno que no avise
nunca por «pasame el código».

Algo parecido pasa cuando la propia persona ofrece algo y el otro lo rechaza en la línea siguiente (`LG-BANK-VERIF-01-e01`,
`TR-06-banco-alerta-legitima`): la negativa queda fuera de lo que se evalúa.

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
| SOPORTE-003 | Estafa | «necesito que me confirmes ambos datos» (usuario y clave). v1 avisaba citando a la víctima («Me pide usuario y contraseña»); v4 exige citar a la otra persona y no avisa |
| `LG-BANK-VERIF-01-e01` | Legítima | La persona ofrece «¿Querés que te diga los últimos números de la tarjeta?». El modelo ve `PROTEGIDA:` y avisa igual |
| `TR-06-banco-alerta-legitima` | Legítima | La persona ofrece «¿Te lo paso así lo verificás?», y el banco le dice que no |
| BANCO-006 | Legítima | Avisa por un consejo: «Podés cerrar esa sesión desde el menú de seguridad» |

## Todos los casos, clasificados

Los nombres sin prefijo son `CV2-D-V-` (estafas) o `CV2-D-L-` (legítimas). «Condiciones» cuenta cuántas de las 13
configuraciones del 2026-11-04 avisan en ese caso.

### Estafas que v4 no avisa (20)

| Caso | `T_R` | Condiciones | v1 control | Clase de problema |
|---|---:|---:|---|---|
| BANCO-012 | — | 1/13 | sin aviso | Sin pedido, solo apuro |
| ORGANISMO_PREVISIONAL-005 | — | 0/13 | sin aviso | Sin pedido, con maniobra |
| ORGANISMO_PREVISIONAL-006 | — | 0/13 | sin aviso | Sin pedido, con maniobra |
| PREMIO-005 | — | 0/13 | sin aviso | Sin pedido, con maniobra |
| PREMIO-006 | — | 1/13 | sin aviso | Sin pedido, sin maniobra clara |
| SOPORTE-007 | — | 0/13 | sin aviso | Sin pedido, con maniobra |
| SOPORTE-008 | — | 0/13 | sin aviso | Sin pedido, solo apuro |
| WHATSAPP-007 | — | 0/13 | sin aviso | Sin pedido, con maniobra |
| WHATSAPP-008 | — | 1/13 | sin aviso | Sin pedido, con maniobra |
| `TR-12-corta-antes-del-pedido` | — | 0/13 | sin aviso | Sin pedido, con maniobra |
| FAMILIAR-004 | 22 | 4/13 | sin aviso | Plata en familia, pedido en condicional |
| FAMILIAR-005 | 20 | 4/13 | sin aviso | Plata en familia, pedido en la penúltima línea |
| FAMILIAR-006 | 22 | 3/13 | sin aviso | Plata en familia, pedido en la penúltima línea |
| SOPORTE-005 | 16 | 4/13 | sin aviso | «Ingresala vos», pantalla sin indicio de ser falsa |
| SOPORTE-006 | 15 | 12/13 | con aviso | «Ingresala vos»; v1 avisa |
| SOPORTE-003 | 11 | 11/13 | con aviso | Modelo: la regla de citar a la otra persona |
| WHATSAPP-004 | 13 | 5/13 | sin aviso | Modelo |
| PREMIO-001 | 10 | 4/13 | sin aviso | Tito no activa |
| PREMIO-003 | 13 | 4/13 | sin aviso | Modelo |
| ORGANISMO_PREVISIONAL-004 | 14 | 5/13 | sin aviso | Modelo |

v1 control, además, no avisa BANCO-003, ORGANISMO_PREVISIONAL-003, SOPORTE-001 y `TR-04-pedido-tras-charla-larga`, que v4 sí
avisa.

### Falsas alarmas de v4 (13)

| Caso | Condiciones | v1 control | Clase de problema |
|---|---:|---|---|
| BANCO-001 | 11/13 | falsa alarma | Dato de identificación, llamó la persona |
| BANCO-002 | 13/13 | falsa alarma | Dato de identificación, llamó la persona |
| BANCO-004 | 6/13 | sin aviso | Dato de identificación, llamó la persona |
| BANCO-005 | 8/13 | sin aviso | Dato de identificación, llamó la persona |
| BANCO-010 | 13/13 | falsa alarma | Dato de identificación; no queda claro quién llamó |
| `TR-13-turno-medico-pide-dni` | 13/13 | falsa alarma | Dato de identificación, llamó la persona |
| `TR-08-frase-cortada-candado` | 13/13 | falsa alarma | El protocolo no deja aprobarlo |
| `LAB-banco-app-parafrasis` | 11/13 | falsa alarma | Fragmento de laboratorio sin contexto |
| `LAB-banco-revisa-app` | 13/13 | falsa alarma | Fragmento de laboratorio sin contexto |
| `TR-11-familiar-real-pide-plata` | 13/13 | falsa alarma | Plata en familia: límite de la etiqueta |
| `LG-BANK-VERIF-01-e01` | 13/13 | falsa alarma | Modelo: la propia persona ofrece |
| `TR-06-banco-alerta-legitima` | 13/13 | falsa alarma | Modelo: la propia persona ofrece |
| BANCO-006 | 6/13 | sin aviso | Modelo: avisa por un consejo |

v1 control suma además FAMILIAR-005 legítima, `TR-05-asado-con-transferencia`, `LAB-arca-canal-oficial` y `LAB-no-bajes-nada`.

## Qué proponemos

> **Estado: propuesta sin discutir.** Las decisiones de qué cuenta como acierto son de
> [D07](../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y cómo se mide es de
> [D08](../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

**No conviene reescribir los casos que fallan para que pasen.** Ya los vimos: sería ajustar el corpus al modelo. Lo que sí
proponemos, en orden:

1. **Llevarle al tutor la contradicción de las estafas sin pedido, con estos ejemplos.** Hay dos salidas: ampliar la definición
   de alerta a maniobras de aislamiento («no cortes», «no le cuentes», «no lo abras») o informar esas estafas aparte.
2. **Agregar el campo `inicia_llamada` a los 150 casos.** El sistema real lo conoce, igual que el canal de cada voz.
3. **Escribir casos nuevos que hoy faltan**, también para la reserva: legítimas con un «no cortes» genuino y estafas donde la
   víctima llama a un número falso.
4. **Informar por separado `LAB`, `TR` y `CV2`**, o sacar los fragmentos de laboratorio de la métrica principal.
5. **Correr `TR-08` y los casos de autoofrecimiento con `--seguir-tras-aviso`**, o sacarlos de las falsas alarmas mientras se
   mida solo el primer aviso.
6. **Seguir con el modelo solo en los 8 errores limpios.** Son los únicos donde un prompt mejor debería notarse.

## Límites

- La clasificación es lectura nuestra, sin revisión humana, y las clases salen de casos ya vistos.
- Las referencias (`T_R`, clase, roles) tampoco tienen revisión humana.
- Las corridas cortan en el primer aviso: no sabemos si la alerta se sostendría ni si se corregiría.
- Diferencias de 1 o 2 casos entre condiciones están dentro del ruido: repetir v1 movió 1 estafa.

## Cómo reproducir

Desde `experiments/slm-directo`, sin correr modelos:

```bash
python -I analizar_fallas_corpus.py
```

Da la tabla por origen, la lista de casos que fallan en v4 o v1 control, la activación de Tito y las maniobras de aislamiento.
Para ver el texto de un caso y lo que citó cada condición:

```bash
python -I analizar_fallas_corpus.py --casos CV2-D-V-FAMILIAR-006 TR-08-frase-cortada-candado
```

El [script](../analizar_fallas_corpus.py) lee los CSV de las corridas `2026-11-04*` y los archivos de [`texto/`](texto/) y
[`referencia/`](referencia/).
