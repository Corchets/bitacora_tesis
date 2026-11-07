# Ideas pendientes y trabajo futuro (#143, 2026-11-06)

> **Estado: propuesta sin discutir.** Son ideas que salieron de esta vuelta y no se prueban antes de congelar el
> ADR 0002. Quedan anotadas para el capítulo de trabajo futuro y para la defensa. Fuentes en [`FUENTES.md`](FUENTES.md).

## 0. Lo primero: legítimas entrantes de números desconocidos

**El problema.** El equipo fijó el alcance el 2026-11-06: el detector corre solo en llamadas entrantes de números no
agendados. Pero el corpus no permite medir ese caso:

- En corpus_v2, las 46 estafas de desarrollo son entrantes, y 44 de las 51 legítimas las inicia la persona: son las
  «consultas» que se armaron como par de cada estafa ([`casos/alcance-desarrollo.json`](../../casos/alcance-desarrollo.json)).
- Las 7 legítimas entrantes son familiares y compañeros de trabajo, que en un teléfono real estarían agendados.
- La reserva sale del mismo generador; lo más probable es que tenga el mismo sesgo.

Así, quién llamó predice la clase casi a la perfección, y dentro del alcance no quedan legítimas para medir falsas
alarmas. Por ejemplo, v4 JSON con «riesgo ≥ 0,3 o alerta» avisa 41 de 46 estafas, 23 antes del pedido, con 1 falsa
alarma sobre apenas 7 legítimas. Los números suben, pero no se pueden defender.

**Qué hace falta.** Legítimas entrantes de números desconocidos, que son las negativas difíciles que el producto sí va
a escuchar:
- el banco real que avisa un movimiento;
- ventas de telefonía, seguros o tarjetas;
- el correo o un delivery que confirma una entrega;
- un consultorio que confirma un turno;
- encuestas, selección de personal y empresas de servicios que avisan un corte.

Hacen falta en desarrollo, para elegir, y en un test aparte, escrito sin mirar resultados. **Evaristo las está
generando desde el 2026-11-06.** Cuando estén, la etapa 2 de #143 prueba el prompt C y `v4-premisa`, que dicen el
alcance. Los 4 controles de ventas que están dentro del alcance son un comienzo, pero solo sirven para mirar.

## 0 bis. El estafador que te hace llamar a vos

**El caso** (lo planteó Mateo el 2026-11-06). El estafador llama, corta, o te dice «llamame a este número», «te paso
con el área de seguridad, llamá al 0800…». También pasa que el primer contacto es un SMS o un WhatsApp que te pide
llamar. Cuando la persona llama, la llamada es **saliente**, queda fuera del alcance y el detector no la escucha. Es el
mismo agujero que el soporte falso que aparece en un buscador.

**Qué se puede hacer, de menor a mayor costo:**
1. **Avisar en la llamada entrante.** Que te pidan cortar y llamar a otro número que te dictan es una señal, sobre todo si
   viene con un problema urgente. C ya habla de «seguir pasos en el celular»; si hace falta, se puede nombrar
   explícitamente, apoyado en las fuentes de los bancos: el banco te dice que llames al número de atrás de tu tarjeta,
   no a uno que te dictan.
2. **Seguir el número.** Si una llamada entrante fue sospechosa, o en ella se dictó un número, y después la persona llama
   a ese número o a otro desconocido en los minutos siguientes, el detector también escucha esa llamada saliente y el
   prompt dice que es una devolución. Es una regla de la app, no del modelo. Necesita guardar un dato entre llamadas,
   algo que hoy D03 deja afuera.
3. **Ampliar el alcance a las salientes a números desconocidos,** con la dirección como dato de cada llamada. Es lo más
   completo, pero vuelve a meter las consultas legítimas que inicia la persona, que son las que más falsas alarmas daban.

**Decisión: pendiente.** Mateo, el 2026-11-06: las tres quedan anotadas para decidir más adelante cuál se implementa.
Por ahora:
- **(1) sí, en el prompt.** Agregada a C el 2026-11-07, con el OK de Mateo y antes de correr C sobre las legítimas
  nuevas. La lista de pedidos de C ahora termina en «…, o cortar y llamar enseguida a otro número que le dictan».
  - **El «enseguida»** apunta a la urgencia: un banco o el correo de verdad pueden dar un 0800 para consultas, pero no
    piden cortar y llamar ya.
  - **De dónde sale:** del caso que planteó Mateo y de los consejos de los bancos (llamar al número oficial, el de la
    tarjeta), no del corpus.
  - **Consecuencia:** C cambió después del tag `colab/143-ronda-2`, así que la etapa 2 repite la humo de formato de
    `c-sino` y `c-digito`.
- **(2) como diseño propuesto,** sin implementar.
- **(3) no, por ahora.** En el corpus no hay estafas salientes para medirla.

Si el estafador corta sin decir nada, no hay nada que detectar, pero tampoco hay daño hasta que alguien devuelva la
llamada.

## 1. Varias preguntas cortas y una regla fija

**Qué es.** Hoy le hacemos al modelo una sola pregunta grande: «¿es una estafa?». La idea es hacerle, en cada línea,
varias preguntas chicas y literales, cada una respondida con un solo token:

- ¿OTRA pidió un código, una clave o un PIN?
- ¿OTRA pidió plata o una transferencia?
- ¿OTRA dice ser de un banco, un organismo o una empresa?
- ¿OTRA apura o amenaza?

El aviso no lo decide el modelo sino una regla escrita de antemano. Por ejemplo: avisar si la primera o la segunda
pregunta dan SÍ, o si la tercera y la cuarta dan SÍ juntas.

**Por qué podría andar.**
- Un modelo chico responde bien preguntas literales. En la primera vuelta, A1 respondió al pie de la letra «¿le pide algo
  de la lista?», y eso lo perjudicó porque esa no era la pregunta correcta. Si cada pregunta es literal a propósito,
  esa misma conducta pasa a ser una ventaja.
- La regla es transparente y explica sola el aviso: dice qué pregunta dio SÍ.

**Cuánto cuesta.** Con la pregunta al final, la transcripción es el comienzo común de todos los pedidos, así que
Ollama la procesa una vez y cada pregunta más agrega pocos tokens (ver
[`NOTA-GEMMA4-Y-CACHE.md`](NOTA-GEMMA4-Y-CACHE.md)). Cuatro preguntas costarían bastante menos que un JSON entero.

**Riesgos.**
- Vuelve a mirar los pedidos y las tácticas, justo lo contrario del prompt C, que mira la intención.
- La regla no puede salir de mirar los fallos del corpus: tiene que escribirse antes.

## 2. Sondeo activo

**Qué es.** Cuando el detector duda, en lugar de esperar más evidencia, la app le sugiere a la persona una pregunta que
la genera. Por ejemplo: «Pedile el número de la sucursal y decile que lo llamás vos». Un banco real acepta sin
problema; un estafador evade o presiona. La respuesta sube o baja el riesgo.

**De dónde sale.** De la patente de Google sobre Scam Detection. Está en
[la lectura del repo](../../../../docs/investigacion/lecturas/2026-google-scam-detection.md), sección 3.4, idea 1.

**Por qué importa.** Un detector que solo escucha está obligado a elegir entre avisar temprano, con poca evidencia, o
tarde, con más. El sondeo rompe ese compromiso porque genera la evidencia en vez de esperarla.

**Qué haría falta.** Es interacción con la persona, no solo un modelo. Medirlo exige llamadas simuladas en las que el
estafador «responde» a la pregunta, o un estudio con voluntarios.

## 3. Ajuste fino para leer el token (trabajo futuro)

**Qué dice la literatura.**
- Sin ajuste fino, leer la probabilidad de la etiqueta en un modelo instruido da un puntaje casi binario y mal
  calibrado.
- Con un ajuste chico (LoRA) sobre datos de la tarea, la misma lectura llega a un AUROC de ~0,97 con un solo paso del
  modelo, 4,9 veces más rápido que generar la respuesta (Open-Jev, 2026).
- ShieldGemma es Gemma ajustado justamente para eso.

**Qué haría falta.**
- Datos de entrenamiento separados del desarrollo y de la reserva. Los 150 casos alcanzan para elegir, no para entrenar.
- Un conjunto aparte para ajustar el umbral.
- Volver a evaluar en la reserva, una sola vez.

**¿Cuánto cuesta probarlo?**
- **Lo técnico es posible en días.** QLoRA de un modelo de este tamaño entra en una T4 o una L4 con Unsloth o PEFT.
  Entrenar unos miles de ejemplos lleva horas, no días.
- **Lo difícil está alrededor:**
  1. **Datos.** Hacen falta cientos o miles de llamadas etiquetadas por línea, aparte del desarrollo y de la reserva. Si
     salen del mismo generador, el modelo aprende su estilo. El sesgo de la dirección de la llamada es justo eso.
  2. **Llevarlo a Ollama.** Hay que fusionar el LoRA, convertirlo a GGUF y cuantizarlo a q4_K_M. Falta confirmar que las
     herramientas soporten la arquitectura de Gemma 4 E2B.
  3. **Evaluarlo** en datos que no se usaron para entrenar ni para elegir.
- **Propuesta:** un sondeo de 1 o 2 días, después del ADR 0002. Ajustar con pocos datos sintéticos, solo para comprobar
  que el camino entero funciona (entrenar, fusionar, convertir y leer el token en Ollama), sin sacar conclusiones de
  rendimiento. Si funciona, queda como experimento acotado; si no, trabajo futuro, con el motivo escrito.

**Para la defensa.** Si en esta vuelta el token no iguala al JSON, la conclusión es que leer el token sin ajuste fino no
alcanza con este modelo, y se informa el ajuste fino como la mejora con mejor respaldo.

## 4. Otras

- **Paráfrasis del prompt.** Correr 2 o 3 redacciones equivalentes del prompt elegido y reportar el rango, para saber
  cuánto ruido mete la redacción (Sclar 2024; Mizrahi 2024). También se pueden promediar.
- **EMA sobre el logaritmo de las chances en vez de sobre la probabilidad.** Con P(SÍ) pegada a 0 o a 1, promediar
  probabilidades se parece a votar; promediar log-chances acumula evidencia.
- **Altavoz y llamadas sin hablantes (`--hablantes sin`).** Queda como límite: la tesis supone que se sabe quién habla
  de cada lado, porque se captura cada canal por separado (D05).
- **Agujeros del alcance.** Números de bancos falsificados, la cuenta de WhatsApp robada a un familiar y las estafas que
  te hacen llamar a vos, como un soporte falso que aparece en un buscador. Quedan afuera por diseño.

## 5. ADR que faltan

Las decisiones de esta semana están repartidas en issues, análisis y handoffs. Para que alimenten las corridas y la
defensa, conviene escribirlas como ADR, en `docs/ingenieria/adr/`:

- **Alcance del detector:** llamadas entrantes de números no agendados. Incluye por qué (Google, Samsung y las falsas
  alarmas de v4), los agujeros (devolución de llamada, contactos robados) y las consecuencias: cambia D03, se agrega la
  oración en el prompt y se generan legítimas entrantes.
- **Corpus:** el sesgo de dirección de corpus_v2, la decisión de generar legítimas entrantes y cómo se congela el test.
- **Método de evaluación:**
  - desarrollo y reserva separados, y la reserva se mira una sola vez;
  - las reglas se escriben antes de correr;
  - una diferencia de ±2 casos es ruido;
  - lo que no se repite no cuenta;
  - controles escritos a ciegas;
  - las reglas del prompt salen de fuentes externas y no de los fallos del corpus;
  - un cambio por vez;
  - la pregunta al final y el comienzo estable para la caché.
- **ADR 0002** (configuración del detector, ya planeado): token o JSON, prompt y política, con el resultado de esta vuelta.

