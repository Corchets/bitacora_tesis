# Fuentes de la segunda vuelta de #143

> **Estado: propuesta sin discutir.** Bibliografía reunida el 2026-11-06 para #143 y la defensa. Todo parafraseado.
> «Verificada» = abrimos la fuente y comprobamos lo que se dice acá. «Relevada» = la trajo una búsqueda con agentes
> y no la volvimos a abrir. La lectura de Google Scam Detection está aparte, en
> [`docs/investigacion/lecturas/2026-google-scam-detection.md`](../../../../docs/investigacion/lecturas/2026-google-scam-detection.md).

## 1. Estafas y llamadas legítimas en Argentina

Sirven para justificar las listas del prompt sin sacarlas del corpus y para escribir los controles de ventas.

| Fuente | Qué dice | Cómo la usamos | Estado |
|---|---|---|---|
| [MPF, UFECI: fotos del DNI y selfies (2022-07-08)](https://www.fiscales.gob.ar/ciberdelincuencia/pedidos-de-selfies-y-de-fotos-del-dni-aumentan-los-fraudes-vinculados-con-los-servicios-puerta-a-puerta-del-correo-argentino/) | Un falso Correo Argentino, por mensajes, pedía fotos del DNI (frente y dorso) y dos selfies. Con eso pasaban la validación de identidad de las fintech y abrían cuentas a nombre de la víctima. 160 víctimas. | La foto del documento o de la cara entra en la lista de lo que busca una estafa. | Verificada |
| [UFECI, informe anual 2024](https://www.mpf.gob.ar/ufeci/files/2025/06/UFECI_informe_anual_2024-1.pdf), pp. 12–24 | 34.468 reportes, 5.509 de ellos ataques a WhatsApp con código. Describe falsos proveedores de telefonía y préstamos sacados a nombre de la víctima después de instalar acceso remoto. No menciona pedidos del DNI. | Las estafas por código son mucho más frecuentes que las por datos; pedir solo el DNI es una señal débil. | Relevada |
| [ANSES: nunca pide datos personales, claves ni información bancaria](https://www.anses.gob.ar/noticias/anses-nunca-solicita-datos-personales-claves-o-informacion-bancaria-0) | ANSES no llama para pedir esos datos. | Fuente de la semilla `SC-ORG-BENEFICIO-01`. | Ya estaba en el catálogo |
| [BCRA, cómo prevenir estafas](https://www.bcra.gob.ar/como-prevenir-estafas-virtuales/) | Advierte por llamadas falsas en nombre de bancos y por pedidos de códigos. | Fuente de varias semillas. | Ya estaba en el catálogo |
| [BCRA, Com. A 7319 (2021-07-01)](https://www.bcra.gob.ar/noticias/se-refuerza-la-responsabilidad-de-los-bancos-por-los-creditos-que-otorgan-a-traves-de-canales-electronicos/) | Los préstamos preaprobados por canales electrónicos exigen identificación positiva y se acreditan a las 48 h hábiles. | Control `CTRL-L-BANCO-OFRECE-PRESTAMO`. | Relevada |
| Listas de «nunca te vamos a pedir»: [BNA](https://www.bna.com.ar/Personas/TarjetasDeCredito/ProtejaSusDatos), [Banco Provincia](https://www.bancoprovincia.com.ar/web/PREGUNTAS_FRECUENTES_TOKEN_DE_SEGURIDAD), [BBVA](https://www.bbva.com/es/ar/innovacion/clave-token-y-sms-como-funcionan-estos-factores-de-autenticacion/), [Mercado Pago](https://www.mercadopago.com.ar/seguridad) y [la campaña de ABA, Adeba, Abapra y ABE en La Nación (2020)](https://www.lanacion.com.ar/economia/estafa-virtual-los-bancos-lanzan-campana-prevenir-nid2472909) | Ninguna entidad pide por teléfono claves, token, códigos, datos completos de la tarjeta ni que instales programas. Banco Provincia agrega que, si te piden generar un código para compartirlo, es una estafa. | Coinciden con la lista de acciones de los prompts S y C: esa lista sale de fuentes externas, no del corpus. | Relevada |
| [Claro, portabilidad](https://www.claro.com.ar/personas/servicios/servicios-moviles/portabilidad/) | Alcanza con el DNI, mandan el chip al domicilio y el cliente ingresa el código que le llega por SMS. | Control `CTRL-L-VENTA-PORTABILIDAD`. No pudimos verificar si un vendedor pide ese código por teléfono. | Relevada |
| [Res. ENACOM 263/2023, resumida por Marval](https://www.marval.com/Publicacion/el-enacom-aprueba-un-nuevo-reglamento-para-combatir-maniobras-delictivas-15423?lang=es) | Las telefónicas validan la identidad con el número de trámite, el sexo y la fecha de nacimiento. | Una venta legítima puede pedir el número de trámite. | Relevada |
| [Ley 26.951, Registro «No Llame»](https://www.argentina.gob.ar/normativa/nacional/norma-233066/texto); [Decreto 2501/2014](https://www.argentina.gob.ar/normativa/nacional/240407/texto) | Prohíbe llamar a quien está inscripto, salvo por un contrato vigente. Obliga a llamar desde un número visible, pero no a que el vendedor diga su nombre. | Contexto de las ventas en frío. | Relevada |
| [La Gaceta (2026-07-01)](https://www.lagaceta.com.ar/nota/1143580/sociedad/cuidado-esta-llamada-asi-funciona-fraude-telefonico-busca-quedarse-tu-whatsapp.html) | Falsos empleados de telefonía inventan un problema de titularidad y piden reenviar un SMS. | Control `CTRL-V-OPERADOR-SMS`. | Relevada |
| [La Nación (2025-01-16)](https://www.lanacion.com.ar/tecnologia/crecen-las-denuncias-de-estafas-con-apps-que-ofrecen-prestamos-truchos-nid16012025/) | Préstamos falsos que cobran una comisión por adelantado a una billetera virtual. | Control `CTRL-V-PRESTAMO-REDES`. | Relevada |
| [Manual Cibercuidados, argentina.gob.ar](https://www.argentina.gob.ar/sites/default/files/manual_talleres_ti_cibercuidados_fraudes_y_estafas.pdf) | Los datos personales suelen pedirse cuando es el cliente quien inicia el contacto. | Apoya el alcance: quién llamó cambia lo que es normal pedir. | Relevada |

## 2. Detectores de estafas telefónicas

| Fuente | Qué dice | Qué tomamos | Estado |
|---|---|---|---|
| [Open-Jev / CallScreenBench, arXiv 2609.23959 (2026)](https://arxiv.org/abs/2609.23959) | Qwen3-4B, una decisión por turno. Sin ajuste fino, leer los logits de la etiqueta da AUROC 0,69 y una confianza muy mal calibrada (ECE 0,17). Con LoRA llega a ~0,97 y es 4,9 veces más rápido que generar la respuesta. En el modelo ajustado, leer la probabilidad de la etiqueta dentro del JSON da 0,95, contra 0,875 de la etiqueta escrita. Avisa con dos turnos seguidos sobre el umbral. Los autores admiten que eligieron la receta después de mirar el test. | Sin ajuste fino, el token no tiene por qué ganarle al JSON: el ajuste fino queda como trabajo futuro. De acá sale v4-L. Es también un ejemplo de por qué no se elige mirando el test. | Verificada |
| [Shen et al. 2025, «It Warned Me Just at the Right Moment», arXiv 2502.03964](https://arxiv.org/abs/2502.03964) | Detección en tiempo real con un LLM que evalúa con lo dicho hasta cada momento. Estudia el compromiso entre recall y avisar a tiempo. Según el cuerpo del artículo, una salida «UNCERTAIN» sube la precisión pero atrasa el aviso. | Es el mismo dilema que nuestras políticas de persistencia. | Resumen verificado; el detalle, relevado |
| [Shen et al. 2024, arXiv 2409.11643](https://arxiv.org/abs/2409.11643) | Pasa la transcripción completa a LLM comerciales: precisión alta y recall de hasta 0,72. No es incremental. | Antecedente. | Relevada |
| [TeleAntiFraud-28k, arXiv 2503.24115](https://arxiv.org/abs/2503.24115) | 28.511 pares de audio y texto, con llamadas normales del mismo tipo de servicio que las de fraude. Un modelo de audio ajustado le gana con mucha diferencia a un LLM grande sin ajustar. | Otra vez, el ajuste fino es lo que más mueve el resultado. | Relevada |
| [SentinelEdge, EMNLP 2026 demos](https://aclanthology.org/2026.emnlp-demos.60/) | Puntúa cada oración, suaviza con una media móvil exponencial y avisa al cruzar un umbral. Código abierto. | Es nuestra política EMA. | Verificada |
| Servicios coreanos: Samsung (2025), [SK Telecom](https://news.sktelecom.com/221425), KT y [LG U+ (estudio de caso de la GSMA)](https://www.gsma.com/solutions-and-impact/technologies/security/scams/wp-content/uploads/2025/08/Case-Study_Real-time-On-device-Vishing-Detection-and-Anti-DeepVoice-Protection-v2.pdf) | Detectan en el teléfono y con dos niveles de alerta. Samsung solo lo hace con números que no están agendados. No publican prompts ni tasas de falsas alarmas. | Apoya el alcance de llamadas entrantes de números no agendados. | Relevada |
| [Ayuda de Google Scam Detection](https://support.google.com/phoneapp/answer/15654065) | No se usa en llamadas con contactos y no está disponible en Argentina. | Apoya el alcance (ver también la lectura del repo). | Relevada |

## 3. Leer puntajes de la probabilidad de los tokens

| Fuente | Qué dice | Qué tomamos | Estado |
|---|---|---|---|
| [Kadavath et al. 2022, «Language Models (Mostly) Know What They Know»](https://arxiv.org/abs/2207.05221) (Anthropic) | P(True) es la probabilidad de «verdadero» frente a una respuesta propuesta. Los modelos post-entrenados parecen muy descalibrados porque el entrenamiento concentra la probabilidad, y una sola temperatura lo corrige en buena parte. | Explica por qué P(SÍ) salió casi siempre 0 o 1. | Relevada |
| [Informe técnico de GPT-4](https://arxiv.org/abs/2303.08774) | El post-entrenamiento empeora la calibración. | Lo mismo. | Relevada |
| [G-Eval, EMNLP 2023](https://aclanthology.org/2023.emnlp-main.153/) | Pondera la escala con la probabilidad de cada valor para que el puntaje sea continuo. La mejora es chica. | La idea del dígito esperado (S y C dígito, v4-L). | Relevada |
| [Wang, Zhang y Choi 2025, arXiv 2503.03064](https://arxiv.org/abs/2503.03064) | La media de la distribución de puntajes rinde mejor que el valor más probable, y razonar antes concentra la distribución. | Sin razonar antes del dígito, y conviene medir cuánto se reparte. | Relevada |
| [Wang et al. 2024, «My Answer is C», arXiv 2402.14499](https://arxiv.org/abs/2402.14499) | En modelos instruidos, el primer token no siempre coincide con la respuesta escrita. | Un motivo más para controlar la lectura en la humo. | Relevada |
| [Tian et al. 2023, EMNLP](https://arxiv.org/abs/2305.14975); [Xiong et al., ICLR 2024](https://arxiv.org/abs/2306.13063) | En modelos grandes, la confianza escrita suele calibrar mejor que la probabilidad del token, aunque también sobreestima. | El riesgo escrito del JSON no es un mal puntaje de por sí. | Relevada |
| [Zhao et al. 2021, calibración contextual](https://proceedings.mlr.press/v139/zhao21c.html) | Corrige el sesgo hacia una respuesta con entradas vacías. No se probó en modelos instruidos. | Idea, sin usar. | Relevada |
| [ShieldGemma](https://ai.google.dev/gemma/docs/shieldgemma/model_card) | Gemma ajustado para clasificar leyendo P(Yes), con la pregunta al final. | El token funciona cuando el modelo se ajusta para eso. | Relevada |
| [OpenAI Cookbook, «Using logprobs»](https://developers.openai.com/cookbook/examples/using_logprobs) | Clasificar con `top_logprobs`; la etiqueta puede quedar partida en varios tokens. | Lo mismo que vimos con «S» + «Í». | Relevada |
| [Ollama PR 12899](https://github.com/ollama/ollama/pull/12899) | Los logprobs se calculan sobre los logits crudos, antes de la temperatura. | La saturación no viene de usar temperatura 0. | Relevada |

## 4. Prompts y formato

| Fuente | Qué dice | Qué tomamos | Estado |
|---|---|---|---|
| [Anthropic, buenas prácticas de prompts](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices) | En contextos largos, poner los datos arriba y la consulta al final mejoró hasta un 30 % en sus pruebas. Está medido en Claude. | La pregunta del token va al final del mensaje del usuario. | Relevada |
| [Anthropic, criterios de éxito y pruebas](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests) | Criterios medibles, casos borde y volumen antes que perfección. | Método. | Relevada |
| [Gemma, estructura de prompts](https://ai.google.dev/gemma/docs/core/prompt-structure) y [formato de Gemma 4](https://ai.google.dev/gemma/docs/core/prompt-formatting-gemma4) | Gemma 3 tiene solo los turnos de usuario y modelo. Gemma 4 agrega un turno de sistema propio. | Ver [`NOTA-GEMMA4-Y-CACHE.md`](NOTA-GEMMA4-Y-CACHE.md). | Relevada |
| [Renderer de gemma4 en Ollama](https://github.com/ollama/ollama/blob/main/model/renderers/gemma4.go) | Arma el turno de sistema y deja el razonamiento apagado por defecto. | Lo mismo. | Relevada |
| [Tam et al. 2024, arXiv 2408.02442](https://arxiv.org/abs/2408.02442) | Forzar JSON empeora el razonamiento, pero en clasificación rinde igual o mejor. | El JSON no nos está perjudicando por ser JSON. | Relevada |

## 5. Sensibilidad al prompt y sobreajuste

| Fuente | Qué dice | Qué tomamos | Estado |
|---|---|---|---|
| [Sclar et al., ICLR 2024](https://arxiv.org/abs/2310.11324) | Formatos equivalentes cambian el resultado hasta en 76 puntos. Recomiendan informar el rango sobre varios formatos. | Para saber el ruido de un prompt, probar paráfrasis. | Relevada |
| [Mizrahi et al., TACL 2024](https://aclanthology.org/2024.tacl-1.52/) | Las paráfrasis cambian puntajes y rankings. Para una aplicación, elegir el mejor prompt en datos apartados. | Lo mismo; es lo que hacemos con la reserva. | Relevada |
| [Voronov et al. 2024](https://arxiv.org/abs/2401.06766) | El mejor prompt de un modelo no sirve necesariamente para otro, y promediar varios prompts estabiliza. | Idea para después. | Relevada |
| [Dwork et al., Science 2015](https://doi.org/10.1126/science.aaa9375) | Usar el conjunto de prueba para decidir invalida sus garantías. | La reserva se mira una sola vez. | Relevada |
| [Husain y Shankar, preguntas frecuentes sobre evals](https://hamel.dev/blog/posts/evals-faq/) | Analizar los errores por categoría, medir aciertos en positivos y en negativos, y usar el test una sola vez. | Método. | Relevada |
