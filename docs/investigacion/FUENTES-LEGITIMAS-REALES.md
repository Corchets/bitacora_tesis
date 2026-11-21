# Legítimas reales para medir falsas alarmas

Consulta: **2026-11-10**. Pregunta: ¿se puede armar, antes del 2026-11-30, un set de llamadas **entrantes,
legítimas y reales** para medir falsas alarmas (FA) como test externo? Este documento no baja datos, no arma el set
y no corre detectores.

> **Estado: propuesta sin discutir.** La fuente, la composición y la custodia del set son parte de
> [D08](../gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental). Nada de esto cambia la configuración
> congelada ni el test de [#45](https://github.com/Corchets/bitacora_tesis/issues/45).

> **Actualización del 2026-11-18:** el set está armado (§8). Son **33 legítimas reales de telecomunicaciones** y
> **42 llamadas de zona gris**, que no cuentan como falsas alarmas. Lo que cambió respecto de este relevamiento: las
> salientes de seguros y de equipamiento médico de CallCenterEN **no son legítimas**. Son captación de Medicare y
> esquemas que el OIG de EE. UU. describe como fraude. Solo las de telecomunicaciones sirven.

## 1. Resultado en breve

- **Vale la pena, acotado a ventas y telemarketing.** Hoy todas las FA salen de legítimas generadas: la configuración
  congelada da 25/94 en desarrollo ([humo del 2026-11-10](../../experiments/slm-directo/corridas/2026-11-10_config-congelada-humo/README.md)).
  Con 50 a 60 llamadas reales se ve si la cifra real está muy por debajo o muy por encima de esa. Si la real fuera
  10 % o 50 %, la diferencia se nota. Si fuera 15 % o 40 %, no (§5).
- **Fuente recomendada: las llamadas salientes de [CallCenterEN](#32-callcenteren-aixblock-la-recomendada).** Son
  llamadas reales de call center a clientes, en inglés, solo texto, con los datos personales tapados. Tienen licencia
  CC BY-NC 4.0, son gratis y no piden registro. Son unas 4.700 de seguros y equipamiento médico, más una parte de
  telecomunicaciones. Hay que traducirlas.
- **Ninguna fuente real y abierta cubre las demás legítimas.** No aparecen entregas, correo, turnos médicos, bancos
  que llaman de verdad ni cobranzas reales en abierto, en ningún idioma. De encuestas hay tres a cinco grabaciones
  sueltas y un proveedor pago (§3). La cifra diría «FA en ventas reales», no «FA en legítimas reales» a secas.
- **Complemento en español, opcional.** En YouTube hay llamadas en vivo que suben los propios vendedores, por ejemplo
  dos agentes inmobiliarios de Lima con unas 100 a 200 llamadas (§3.3). Hay que bajar el audio, transcribir y separar
  roles, y eso duplica el trabajo. Solo vale si sobra tiempo.
- **Tiempo:** unas 40 horas-persona, repartidas en una semana de calendario, entre un custodio y dos anotadores que no
  ajustaron el detector. Si arranca el 2026-11-16, termina antes del 30.
- **Primero hace falta el OK de Mateo** para bajar tres archivos de CallCenterEN, de unos 128 MB en total (§6).

## 2. Qué se buscó

**Qué encaja.** Una llamada que la persona **recibe** de un número desconocido, que no es estafa y que se grabó de
verdad, no actuada ni generada. Es el alcance del
[ADR 0003](../ingenieria/adr/0003-detector-solo-en-entrantes-de-no-agendados.md). Los tipos pedidos son ventas y
telemarketing, correo o entregas, turnos médicos y obras sociales, cobranzas, encuestas, selección laboral y bancos.

**Qué queda como contraste:** las llamadas que inicia la persona, como las de ES-Port, las de familia o amigos, como
CALLHOME, y las actuadas.

**Cómo se sabe que es legítima.** Es el punto débil de toda fuente real. Hay tres niveles, de más a menos firme:

1. el dataset viene de los registros de una empresa real (CallCenterEN);
2. la sube quien llama, con nombre y empresa (vendedores en YouTube);
3. la sube quien la recibe, y entonces no se puede comprobar que no sea una estafa.

**Antecedentes.** El relevamiento del 2026-11-04 (CABNC, CALLHOME Spanish y Fisher) se retiró el 2026-11-10, cuando se
descartó CABNC ([PR #175](https://github.com/Corchets/bitacora_tesis/pull/175)). ES-Port y las fuentes de estafas de
#144 están en el [relevamiento del corpus externo](../corpus/RELEVAMIENTO-CORPUS-EXTERNO.md).

**Cómo.** Se buscó en tres frentes en paralelo: datasets abiertos (Hugging Face, GitHub, arXiv, ACL Anthology),
catálogos con licencia (LDC, ELRA, TalkBank) y grabaciones públicas (YouTube, radio). Se leyeron fichas, README,
papers y páginas. No se bajó ni se escuchó ningún dato. Marcas: **V**, verificado en la página primaria; **I**,
inferido; **NV**, no verificado.

## 3. Fuentes

### 3.1. Resumen

| Fuente | Idioma | ¿Real? | Cuántas encajan y de qué tipo | Licencia | Acceso y costo | Veredicto |
|---|---|---|---|---|---|---|
| [CallCenterEN](#32-callcenteren-aixblock-la-recomendada) | inglés | sí | ~4.700 salientes de seguros y equipamiento médico, más telecomunicaciones | CC BY-NC 4.0, sin redistribuir | abierto, gratis, ~128 MB | **recomendada** |
| [YouTube, vendedores en vivo](#33-grabaciones-públicas-en-youtube) | inglés, español y portugués | sí (I) | 150–250 en español de particulares, casi todas inmobiliarias; 250–700 en inglés | licencia estándar de YouTube | bajar audio y transcribir | complemento opcional |
| [Honeypot de Traister et al.](#34-honeypot-de-traister-et-al-2026) | inglés | sí, pero atiende una IA | 380 legítimas, solo con acuerdo de uso; 500 spam en lo público | CC BY-NC | créditos pagos o acuerdo de uso | no llega al 30 |
| [TeleAntiFraud-28k](#35-teleantifraud-28k) | chino | mezcla con TTS y LLM | 14.864 normales, sin saber cuántas son reales | Apache-2.0 | aceptar condiciones en HF | no sirve |
| [LDC, ELRA, TalkBank y corpus orales](#36-ldc-elra-talkbank-y-corpus-orales-del-español) | español e inglés | sí | 0 de empresa a persona | acuerdo LDC; CC BY-NC-SA en TalkBank | Fisher Spanish, US$ 1.500 el texto; C-ORAL-ROM, 3.000 € | no encaja |
| [Proveedores comerciales](#37-proveedores-comerciales) | español, también de Argentina | según el vendedor; FutureBeeAI parece actuada | salientes, sin conteo publicado | contrato | cotización; Nexdata, desde US$ 20.000 | no llega al 30 |
| [Inaccesibles o fuera de alcance](#38-descartadas) | varios | — | 0 | — | — | contraste |

### 3.2. CallCenterEN (AIxBlock): la recomendada

- **Qué es.** 91.706 transcripciones de llamadas reales de unos 10 centros BPO, grabadas hacia 2020. Son unas 10.448 h
  de audio original, que no se publica. Ficha:
  [AIxBlock/92k-real-world-call-center-scripts-english](https://huggingface.co/datasets/AIxBlock/92k-real-world-call-center-scripts-english);
  paper: [Dao et al. 2025](https://arxiv.org/abs/2507.02958). La ficha dice que hay entrantes y salientes (V).
- **Salientes.** Según la tabla 3 del paper son 7.982, el 8,7 %. El paper las define como llamadas «initiated by
  agents, often for cold-calling or upselling purposes». Están en tres archivos:

  | Archivo | Llamadas | Dirección | Tamaño |
  |---|---:|---|---:|
  | Insurance_outbound | 4.005 | saliente | 55,3 MB |
  | Medical_equipment_outbound | 738 | saliente | 13,5 MB |
  | Home_service_inbound & telecom_outbound | 3.239 | mezcla | 59,1 MB |

  El conteo por archivo lo leyó el relevamiento de datasets en el paper y en el listado de archivos. Yo solo pude
  confirmar la ficha: el texto del PDF no se pudo extraer en esta sesión (NV).
- **Tipo para nosotros.** Ventas y retención de seguros, equipamiento médico para jubilados y telecomunicaciones. El
  equipamiento médico es lo más parecido a «la obra social te llama». No hay entregas, bancos ni cobranzas.
- **Licencia (V).** CC BY-NC 4.0, con una cláusula extra de la ficha: «Commercial use, resale, or redistribution is
  prohibited». La licencia permite traducir con fines no comerciales, con atribución y marcando los cambios (I). Por
  la cláusula, el original y la traducción quedan fuera de Git, como en #144. Al repo van identificadores, hashes y
  procedimiento.
- **Privacidad (V).** Datos personales tapados con detección automática y revisión manual, en 44 categorías (nombres,
  teléfonos, cuentas, tarjetas, montos, fechas, lugares). Quedan como marcadores. El paper pide no intentar
  reidentificar.
- **Legitimidad.** Viene de los registros de BPO con los que AIxBlock tenía convenio, sin etiqueta de legitimidad ni de
  resultado. Parte de las salientes puede ser telemarketing agresivo. En EE. UU., por ejemplo, está prohibido llamar en
  frío a jubilados de Medicare para venderles equipamiento médico (I). Agresivo no es estafa, pero hay que anotarlo.
  **Lo que mostró la anotación (2026-11-18, §8):** en seguros y equipamiento médico ningún anotador marcó legítima
  ninguna de las 42 llamadas. Solo las de telecomunicaciones son legítimas.
- **Formato.** JSON con el texto, la duración y marcas de tiempo por palabra, salido del ASR de AssemblyAI, sin
  muletillas y con los números en cifras. La ficha no habla de hablantes. **Confirmado el 2026-11-18:** el campo
  `speaker` viene vacío en todas las palabras de los tres archivos, así que hay que separar turnos y roles.
- **Esfuerzo:** medio-alto.
  1. Separar turnos y asignar roles: el agente es `OTRA` y el cliente, `PROTEGIDA`.
  2. En el archivo mezclado, separar telecomunicaciones salientes de servicios para el hogar entrantes.
  3. Traducir a rioplatense y adaptar lo que no existe acá, por ejemplo Medicare por PAMI.
  4. Anotar tipo y legitimidad (§4).

### 3.3. Grabaciones públicas en YouTube

Existen, pero casi todas las sube **quien llama**: vendedores que se graban llamando en vivo. Eso da el nivel 2 de
legitimidad. Las que sube quien recibe son pocas, cortas y sesgadas: se viralizan las peleas y los chistes.

| Fuente | Idioma | Tipo | Llamadas (I) | Quién sube |
|---|---|---|---:|---|
| Gonzalo Cavero Noya y Erickson Villafane, agentes inmobiliarios ([ej. 1](https://www.youtube.com/watch?v=pPqBwVQznKk), [ej. 2](https://www.youtube.com/watch?v=UsNrBE1Z4xw)) | es-PE | llaman a particulares que pusieron un cartel de «se vende»; ~30 videos, ~22 h | 100–200 | quien llama |
| Flab \| Sin Filtros ([ej.](https://www.youtube.com/watch?v=sjRbiF1R2h4)) | es-UY | venta de páginas web a comercios (B2B) | 40–80, cortas | quien llama |
| Telemarketing viral (Fibertel, Movistar y otros) | es-AR y otros | portabilidad, retención | 15–30, <10 de Argentina | quien recibe o terceros |
| Cobranzas grabadas (México, Colombia, Argentina) | es | cobranza | 10–25 | quien recibe; legitimidad dudosa |
| Inmobiliarias de EE. UU. (Brandon Mulrenin, Loida Velasquez, Maximilian Dier y otros) | en-US | llaman a propietarios | 200–600 | quien llama |
| Seguros a *leads* (Cody Askins, Peter Roberts y otros) | en-US | piden fecha de nacimiento, salud y cuenta bancaria | 30–60, largas | quien llama |
| Randall Reilly, «Listening In» ([ej.](https://www.youtube.com/watch?v=6pYVd6yUw7A)) | en-US | selección: reclutadores llaman a choferes | 20–40, con comentarios | la empresa |

- **Lo que falta:** turnos médicos, correo o entregas y bancos. Bancos y organismos solo publican ejemplos de estafas.
  Encuestas hay 3 a 5 en todo el español. Selección laboral real, solo en inglés.
- **Derechos (V):** licencia estándar de YouTube, salvo un par de videos CC BY. Es la misma zona gris que los
  *scambaiters* de #144: transcribir para investigación y guardar el texto fuera de Git.
- **Privacidad:** peor que con los *scambaiters*. Quien atiende es un particular que no aceptó que lo publiquen, y se
  oyen su nombre, la zona y el precio. Hay que seudonimizar y no guardar el audio.
- **Esfuerzo: alto.** Hay que bajar audio (con OK), transcribir en Colab porque acá no hay ffmpeg, cortar llamada por
  llamada, sacar los comentarios del vendedor y separar roles en un solo canal. No se verificó cuántas llamadas por hora
  están completas ni si se oye bien a quien atiende.
- **Excluir:** bromas (Tangalanga, Anda Ya) y actuadas o de práctica (Cognism «mock», Kwestyon, Mente Comercial).

El detalle canal por canal, con todos los enlaces, quedó en las notas compartidas de las sesiones, fuera del repo
(`fuentes-grabaciones-publicas.md`).

### 3.4. Honeypot de Traister et al. (2026)

[Traister et al.](https://arxiv.org/abs/2609.29528) cargaron números en formularios de captación de clientes y
atendieron lo que llegó con un agente de IA con persona de viuda jubilada. Sobre 6.374 llamadas resueltas, separan
949 estafas, 3.949 de *spam* (venta o captación «predatoria pero legal») y 380 legítimas (V).

- **Las legítimas no se publican (V):** «Legitimate calls are excluded entirely». Las 1.000 públicas son 500 estafas y
  500 spam, elegidas por largo, con las empresas reemplazadas por marcadores.
- **Acceso (V):** la parte pública pide comprar créditos en [scam.ai/research](https://scam.ai/research), sin precio a
  la vista; el corpus completo pide un acuerdo de uso. Licencia CC BY-NC; la versión no coincide entre el paper y arXiv.
- **Para nosotros:** las 3.949 de spam serían negativos difíciles reales. Pero quien atiende es una máquina, el llamador
  compró un *lead* «caliente» y hay que pagar o firmar. No llega al 30.

### 3.5. TeleAntiFraud-28k

En chino, Apache-2.0, en Hugging Face con aceptación de condiciones (V). Tiene 14.864 llamadas normales con escenarios
de reparto, viajes y turnos. Las grabaciones reales se pasaron por ASR y se **resintetizaron con TTS**, y se mezclan
con texto generado por LLM. Lo real va solo en test, sin conteo ([paper](https://arxiv.org/abs/2503.24115), V). No hay
manera de aislar llamadas reales y entrantes. La versión 2.0 es enteramente sintética.

### 3.6. LDC, ELRA, TalkBank y corpus orales del español

Ninguno trae llamadas de una empresa a una persona.

- **[Fisher Spanish](https://catalog.ldc.upenn.edu/LDC2010T04) (LDC).** 819 llamadas de 10 a 12 minutos. La
  plataforma llama a la persona y la junta con alguien que «typically do not know», con un tema asignado (V). Es lo
  más parecido a «me llama un desconocido», y 20 de los 136 hablantes se criaron en Argentina (V). Pero no hay empresa
  ni pedido. Cuesta US$ 1.500 las transcripciones y US$ 2.500 el audio para no miembros, según la tabla de aranceles
  que vio el relevamiento; el catálogo muestra el monto solo al iniciar sesión.
- **CALLHOME y CALLFRIEND Spanish (LDC).** Familia y amigos. CALLHOME, segunda edición, US$ 3.000.
- **C-ORAL-ROM (ELRA).** La parte telefónica de servicios del español es persona-máquina. Cuesta 3.000 € para uso
  académico, por las cuatro lenguas, y llega en DVD.
- **TalkBank (CABank).** CallHome y CallFriend en español, gratis con registro y CC BY-NC-SA. El corpus *Business*
  son llamadas B2B en inglés de 1987 a 1991. Ninguno encaja.
- **Corpus orales del español** (CORLEC, CREA oral, CORPES XXI oral, Val.Es.Co, ESLORA, Ameresco, PRESEEA): no se
  encontraron llamadas con empresas.

### 3.7. Proveedores comerciales

Todos piden cotización y contrato, y ninguno publica cuántas llamadas son salientes ni el plazo de entrega. Con el
trámite, no llegan al 30 (I).

| Proveedor | Qué ofrece | ¿Real? | Precio |
|---|---|---|---|
| [FutureBeeAI](https://www.futurebeeai.com/dataset/speech-dataset/healthcare-call-center-conversation-spanish-argentina) | **Español de Argentina**, 7 dominios de 30 h. Tiene salientes por escenario: recordatorios de turnos y de cuotas, entregas, encuestas, ofertas de crédito (V) | Dice «unscripted», pero la graban 60 personas reclutadas, sin ruido: parece actuada (I) | cotización |
| Shaip | Call center de México y España, «real inbound and outbound» (V) | según el vendedor | por hora, sin publicar |
| Nexdata | 20.000 h multilingües con salientes de ventas (V) | no lo dice | desde US$ 20.000 (V) |
| AxonData | más de 1.000 h en español, con salientes (V) | «real-world» (V) | cotización; muestra de una llamada |
| GeoPoll | entrevistas telefónicas reales en Latinoamérica, sin Argentina (V) | sí, con cuestionario | cotización |

FutureBeeAI es la única que cubre los tipos que faltan, y en rioplatense. Pero si es actuada, mide lo mismo que las
legítimas generadas, con otra mano. Su licencia prohíbe publicar el dataset, incluso modificado (V).

### 3.8. Descartadas

| Fuente | Por qué |
|---|---|
| ES-Port, DECODA (francés), LUNA (italiano), CallSurf y AlloSat (francés), CMCC (chino) | Las inicia el cliente: soporte entrante |
| HarperValleyBank, SpokenWOZ, DiaBiz (polaco, con cobranzas), TeleSalesCorpus | Actuadas o generadas |
| AI Hub (Corea) | Las fichas dicen que solo pueden pedirlo ciudadanos coreanos (V) |
| NCSU Robocall Audio Dataset | Robollamadas de la FTC, la mayoría ilegales (V) |
| OSWE Telephone Interviews | 43 entrevistas pactadas de antemano, con fin lingüístico (V) |
| Gong call-playbook, liva-ai/real-sales | Fragmentos B2B o 7 llamadas |
| Cobranzas, selección y turnos de papers | Datos privados, sin publicar (V) |

## 4. Protocolo propuesto: solo test

> **Estado: propuesta sin discutir.** Reúne reglas que ya están en
> [PROTOCOLO-EXPERIMENTAL.md §3.2 y §3.3](../evaluacion/PROTOCOLO-EXPERIMENTAL.md#32-criterios-anti-fuga-propuestos-callerseed-disjoint),
> en el [ADR 0005](../ingenieria/adr/0005-reglas-de-evaluacion-escritas-antes-de-correr.md) y en
> [#145](../corpus/REVISION-CIEGA-145.md). Quién custodia el set lo decide el equipo.

### 4.1. Antes de abrir una sola llamada

1. **La configuración**, por commit: la congelada el 2026-11-09, con C cortado tras el riesgo, riesgo ≥ 0,3, solo
   `OTRA` y primer aviso. El set no sirve para elegirla ni para retocarla.
2. **La regla de selección**, commiteada:
   - archivos de origen y versión del dataset;
   - cuotas por archivo;
   - duración mínima de 60 s, para sacar buzones y cortes;
   - semilla del sorteo.

   Se elige por metadatos (archivo, duración), sin leer el diálogo. Sin tope de duración: las llamadas reales son
   largas, y cortarlas bajaría las FA. Si el tiempo no alcanza, el tope se fija antes y se declara.
3. **La regla de lectura, en código.** Una FA es una legítima con al menos un aviso
   ([METRICAS.md §4](../evaluacion/METRICAS.md#4-qué-se-mide)). Se informa con Wilson al 95 %. Solo permite repetir una
   llamada un fallo técnico, como una salida ilegible o una caída del servidor. Nunca un aviso raro.
4. **Revisar el formato sin leer.** Un script que informe solo la estructura: campos, si `speaker` viene vacío y
   cuántas llamadas y qué duración hay por archivo. No imprime texto. Así se confirman los conteos de §3.2 sin romper
   la ceguera.

### 4.2. Custodia y armado

- Arma el set alguien que no ajustó el detector. Quien desarrolló la configuración congelada no lee las llamadas hasta
  publicar el resultado.
- Los datos quedan en `data/private/`, que Git ignora, o fuera del repo. Al repo van el identificador neutro, el
  archivo y el nombre de origen, los SHA-256 del texto y de la referencia, y el procedimiento.
- Queda afuera toda llamada que alguien del equipo haya leído antes de sellar, como las diez de ES-Port
  ([relevamiento §7.3](../corpus/RELEVAMIENTO-CORPUS-EXTERNO.md#73-exclusión-de-exploración-y-trabajo-que-sigue-pendiente)).
- Se sortean unas 80 candidatas para llegar a 60 dentro del alcance. Se espera perder alrededor de una de cada cuatro
  por buzón, transferencia, llamada que pidió el cliente o legitimidad dudosa (I).

### 4.3. Turnos, roles y traducción

- Si `speaker` viene vacío, el custodio separa turnos y roles con un modelo y los revisa a mano. `OTRA` es el agente y
  `PROTEGIDA`, el cliente. Importa porque la configuración consulta solo en las líneas de `OTRA`.
- Se traduce con los criterios de #144
  ([relevamiento §5.2](../corpus/RELEVAMIENTO-CORPUS-EXTERNO.md#52-traducción-y-adaptación)): mismos turnos y orden,
  sin agregar ni sacar información, rioplatense oral, «usted» si el original es formal. **Cambio aplicado en §8:**
  como en el set coreano ([relevamiento §8.2](../corpus/RELEVAMIENTO-CORPUS-EXTERNO.md#82-cómo-se-hizo)), la traducción
  es fiel, en español neutro, y sin adaptar el contexto de EE. UU.
- Lo propio de las legítimas: **no hacerlas más ni menos parecidas a una estafa.** Si el vendedor pide la tarjeta, la
  traducción pide la tarjeta. Las instituciones se cambian solo cuando no existen acá. Los marcadores de datos tapados
  se reemplazan por datos ficticios con una tabla fija.
- Si traduce un modelo, se registran el modelo y el prompt. No puede ser Gemma, la familia del detector. El custodio
  revisa la fidelidad contra el original.
- El formato es el de `slm-directo`: ID neutro, líneas `PROTEGIDA`/`OTRA` y la referencia aparte, que el detector no
  ve ([relevamiento §5.4](../corpus/RELEVAMIENTO-CORPUS-EXTERNO.md#54-formato-todas-son-conversaciones)).

### 4.4. Anotación a ciegas

Dos personas anotan por separado, **antes** de correr el detector y sin ver resultados:

| Campo | Valores |
|---|---|
| Alcance | entrante de desconocido / entrante de conocido / la pidió el cliente / no se sabe |
| Legitimidad | legítima / legítima pero agresiva / dudosa / estafa |
| Tipo | ventas · salud u obra social · telecomunicaciones · entrega · cobranza · encuesta · selección · banco · otra |
| Tipo de desarrollo | `cotidiana` / `pedido_razonable` / `mencion_sin_pedido` |
| Pedido sensible | ninguno / datos personales / datos de pago / código o clave / plata |
| Completa | sí / falta el comienzo / falta el final |

- Antes de adjudicar se mide el acuerdo, en porcentaje y con kappa de Cohen, en alcance, legitimidad y tipo.
- Las dudosas y las que quedan fuera del alcance no entran en la cifra principal: se cuentan y se informan aparte.
- La clave que une alias y origen va a `data/private/`, como la de #145. Sirve su formulario ciego cambiando las
  preguntas.
- Se anota sobre el original o sobre la traducción, pero siempre igual para todas.

### 4.5. Corrida y lectura

- Una sola corrida desatendida, con el manifiesto sellado antes. El resultado va al informe tal como sale.
- Se informa `FA = k/n` con Wilson al 95 %, desglosada por archivo de origen, por pedido sensible y por largo. El largo
  importa porque las legítimas generadas son más cortas que las estafas
  ([#151](https://github.com/Corchets/bitacora_tesis/issues/151)).
- Un aviso en una legítima que pide la tarjeta sigue siendo FA. Se informa aparte para que se lea bien.
- Se compara con las legítimas generadas, las 94 de desarrollo y las 56 de test, con el intervalo de Newcombe para
  la diferencia. No se ajusta nada con lo que salga.

## 5. Cuántas llamadas hacen falta

Wilson al 95 %, calculado con [`intervalo_wilson`](../../experiments/metricas/metricas.py) del repo:

| n | Si da 10 % | Si da 25 % | Si da 0 |
|---:|---|---|---|
| 40 | 4/40: 4,0–23,1 % | 10/40: 14,2–40,2 % | ≤ 8,8 % |
| 50 | 5/50: 4,3–21,4 % | 12/50: 14,3–37,4 % | ≤ 7,1 % |
| 60 | 6/60: 4,7–20,1 % | 15/60: 15,8–37,2 % | ≤ 6,0 % |
| 80 | 8/80: 5,2–18,5 % | 20/80: 16,8–35,5 % | ≤ 4,6 % |
| 100 | 10/100: 5,5–17,4 % | 25/100: 17,5–34,3 % | ≤ 3,7 % |

La referencia es 25/94 en desarrollo, con Wilson de 18,7 a 36,3 %. Con el intervalo de Newcombe para la diferencia:

| Si la FA real fuera | ¿Se distingue de 25/94? |
|---|---|
| 5 % | sí, desde n = 30 |
| 10 % | sí, desde n = 40 |
| 15 % | recién con n ≈ 100 |
| 40 % | recién con n ≈ 100 |
| 50 % | sí, desde n = 30 |

**Propuesta: 60 dentro del alcance,** con un mínimo de 40. Detecta una diferencia grande y da ±11 puntos si la FA
ronda 25 %. Una diferencia moderada pide unas 100, que no llegan al 30. Por tipo o por archivo, con 20 por grupo, solo
se informan conteos, sin conclusiones.

## 6. Recomendación y plan

**Sí, con CallCenterEN, para medir FA en ventas reales.** No reemplaza a las legítimas generadas: las complementa en
el único tipo que existe real y abierto. El límite se declara: no hay entregas, turnos, bancos ni cobranzas reales.

| Paso | Quién | Horas |
|---|---|---:|
| OK de Mateo para bajar los tres archivos salientes (~128 MB, Hugging Face, CC BY-NC 4.0) | Mateo | — |
| El equipo elige custodio y dos anotadores que no ajustaron el detector | equipo | — |
| Regla de selección y de lectura commiteadas; script de estructura | custodio | 3 |
| Sorteo de 80 candidatas y filtro de alcance | custodio | 3 |
| Turnos y roles, si no vienen (≈ 8 min por llamada) | custodio | 10 |
| Traducción con modelo y revisión de fidelidad (≈ 10 min por llamada) | custodio | 12 |
| Anotación a ciegas (≈ 5 min por llamada y persona) | dos anotadores | 2 × 5 |
| Acuerdo, adjudicación, sellado con SHA-256 | custodio | 3 |
| Corrida en Colab y lectura según la regla | otro integrante | 2 |
| **Total** | | **≈ 43** |

Las horas por llamada son estimaciones (I): las llamadas reales son más largas que las generadas.

Son unos 6 a 8 días de calendario. Conviene arrancar después del 90 % del 2026-11-15 y cerrar el 2026-11-25, con
margen. Si el script de estructura muestra que faltan roles y turnos, o que las salientes no llegan a 80 usables, se
vuelve a decidir antes de traducir.

**El complemento de YouTube en español** sumaría unas 20 a 25 horas más para 20 llamadas de Lima (I). Lo dejaría para
después del 30 o como trabajo futuro.

## 7. Qué no se verificó

- **CallCenterEN:** si el JSON trae hablantes; cuántas de las 3.239 del archivo mezclado son salientes; cuántas
  salientes son en frío y cuántas a clientes existentes. Lo responde el script de estructura de §4.1.
- **YouTube:** cuántas llamadas completas hay por hora y si se oye bien a quien atiende.
- **Traister:** el precio de los créditos y si el acuerdo de uso incluye las 380 legítimas.
- **TeleAntiFraud:** cuántas normales salen de grabaciones reales.
- **LDC y ELRA:** los plazos de entrega, y el resto del catálogo de ELRA, porque el buscador devolvió errores.
- **Proveedores:** cuántas salientes tiene cada uno y si FutureBeeAI es real o actuada.

## 8. Set armado el 2026-11-18

> **Estado: propuesta sin discutir.** Mateo delegó el armado el 2026-11-18. Si y cómo se informa en
> [#52](https://github.com/Corchets/bitacora_tesis/issues/52) lo decide el equipo. Ningún detector corrió sobre estas
> llamadas.

### 8.1. Qué quedó

| Set | Llamadas | Qué son | Cómo se lee |
|---|---:|---|---|
| **Legítimas reales** | 33 | Telecomunicaciones salientes a negocios que ya son clientes o habían pedido algo: instalaciones, visitas técnicas, mejoras de plan | Falsas alarmas: `k/33` con Wilson |
| **Zona gris de Medicare** | 42 | 24 de seguros y 18 de equipamiento médico | Aparte: ni falsa alarma ni estafa |

De las 33 legítimas, 19 son `cotidiana`, 10 `mencion_sin_pedido` y 4 `pedido_razonable`. Cuatro tienen un pedido
sensible de datos personales. Tienen de 13 a 38 líneas, con mediana de 22, parecido a las estafas de desarrollo.
26 están completas, a 5 les falta el final y a 2 el comienzo.

Quedaron afuera tres llamadas de telecomunicaciones: dos entrantes (`CAND-49` y `CAND-60`) y una que inicia la
persona (`CAND-51`).

Con n = 33, el intervalo de Wilson al 95 % es ancho:

| FA | Intervalo |
|---|---|
| 0/33 | 0–10,4 % |
| 3/33 | 3,1–23,6 % |
| 8/33 | 12,8–41,0 % |

Alcanza para ver una diferencia grande con las 25/94 de desarrollo, no una chica (§5).

### 8.2. Por qué hay una zona gris

En seguros y equipamiento médico ningún anotador marcó legítima ninguna de las 42 llamadas:

- el anotador `a1` marcó las 42 como estafa;
- `a2` marcó 30 dudosas y 12 estafas.

Lo que describe `a2` coincide con dos esquemas documentados en EE. UU.:

- **Seguros:** prometen una «mejora» de Medicare con reembolso, confirman fecha de nacimiento y domicilio, y
  transfieren a otro agente que va a pedir el número de Medicare. Las aseguradoras de Medicare Advantage no pueden
  llamar en frío ([42 CFR 422.2264(a)(2)(iv)](https://www.law.cornell.edu/cfr/text/42/422.2264)).
- **Equipamiento médico:** ofrecen una prueba genética o rodilleras «gratis» a cambio del número de Medicare o del
  Seguro Social, y arman una «contraseña de verificación». En una llamada el agente le dice a la persona que mienta
  en las preguntas que siguen. Es el esquema de la
  [alerta de fraude del OIG](https://oig.hhs.gov/fraud/consumer-alerts/fraud-alert-genetic-testing-scam).

Contarlas como legítimas inflaría las falsas alarmas. Tampoco son estafas con referencia: no hay marcas ni se sabe
cómo terminó cada una. Por eso van aparte. Si el detector avisa ahí, probablemente avisa bien.

Lo que esto le cambia al relevamiento: «viene de un BPO real» no es verdad de base de legitimidad (§2). Sirvió el
tercer criterio, la anotación.

### 8.3. Cómo se hizo

1. **Descarga.** Tres archivos de la revisión `9d40ca13f3e1` de CallCenterEN, 128 MB, con el SHA-256 de Hugging
   Face. Se revisó la estructura con un script que no imprime texto. El campo `speaker` viene vacío.
2. **Sorteo.** [`seleccionar_legitimas_reales.py`](../../experiments/slm-directo/seleccionar_legitimas_reales.py)
   se commiteó antes de abrir ninguna llamada. Elige por nombre de archivo y duración, de 60 a 900 s, con
   `Random(20261118)`: 24 de seguros, 18 de equipamiento médico y 8 de telecomunicaciones. Parte el texto en cada
   pausa de 600 ms o más. La segunda tanda, de 28 llamadas de telecomunicaciones con `Random(20261119)`, se decidió
   después de anotar la primera y antes de correr ningún detector, y también se commiteó antes de traducir.
3. **Turnos y traducción.** Doce subagentes Claude Sonnet 5.5 en paralelo, con el prompt de
   [PROMPTS-LEGITIMAS-REALES-2026-11-18.md §1](../corpus/PROMPTS-LEGITIMAS-REALES-2026-11-18.md#1-turnos-roles-y-traducción).
   La traducción es fiel, en español neutro, con el contexto de EE. UU., como el set coreano. Se comprobó con
   script que cada traducción cubre todos los segmentos de su fuente y entre 84 y 98 % de su vocabulario.
4. **Texto final.** [`armar_set_legitimas_reales.py`](../../experiments/slm-directo/armar_set_legitimas_reales.py)
   arma una línea por turno, con `A` como quien habla primero. Los marcadores de datos tapados se reemplazan por un
   valor ficticio fijo por tipo y por llamada.
5. **Anotación a ciegas.** Dos subagentes Sonnet por tanda, sin ver el inglés, el estrato ni al otro anotador (§2 de
   los prompts). Los desacuerdos de las llamadas que algún anotador marcó legítimas los resolvió un tercero (§3).
6. **Congelado.** IDs `EXT-NNNN` de cuatro cifras, para no chocar con los de tres del set coreano. Los manifiestos
   tienen el SHA-256 de cada archivo:
   - [`MANIFIESTO-LEGITIMAS-REALES-2026-11-18.json`](../corpus/MANIFIESTO-LEGITIMAS-REALES-2026-11-18.json): su
     SHA-256 es `f1f6631a968321b5d897adcb9ff1a58109efb077b75460efcb51d05a0e91e0de`;
   - [`MANIFIESTO-ZONA-GRIS-MEDICARE-2026-11-18.json`](../corpus/MANIFIESTO-ZONA-GRIS-MEDICARE-2026-11-18.json): su
     SHA-256 es `3f2d79370ca472a7e27d75a9cf2007242e4c32b3b1caa666204cdc9f20261d2d`.

**Acuerdo entre anotadores** (76 llamadas, las dos tandas juntas):

| Campo | Acuerdo | Kappa |
|---|---:|---:|
| Quién inicia | 76/76 | 1,00 |
| Legítima sí o no | 76/76 | 1,00 |
| Hay pedido sensible | 75/76 | 0,97 |
| `completa` | 70/76 | 0,86 |
| `tipo_legitima` | 68/76 | 0,83 |
| Legitimidad, con sus cuatro valores | 43/76 | 0,42 |
| Motivo | 30/76 | 0,32 |

Lo que decide qué entra al set tiene acuerdo total. Los desacuerdos de legitimidad son entre `estafa` y `dudosa` en
la zona gris, y entre `legitima` y `legitima_agresiva` en las legítimas.

### 8.4. Custodia y cómo se corre

- Los textos no se versionan: la ficha prohíbe redistribuir. Todo queda en `data/private/legitimas-reales/` del
  checkout principal, que Git ignora: las zip, la carpeta de trabajo y `sets/set-legitimas` y
  `sets/set-zona-gris`. `correspondencia.json` lleva el nombre de archivo de la fuente, que es el teléfono de la
  persona, así que no sale de ahí.
- Los dos sets tienen el formato del set coreano. Se comprobó que cargan sin errores con el código de #52: primero
  con `conjuntos.preparar_externo(carpeta, destino, manifiesto=…)` de la rama local de entonces, y después con
  `conjuntos.preparar_legitimas_reales`: 33 legítimas y 42 `legitima_dificil`.
- **Sumados a #52 el 2026-11-18** (Mateo: «sumalos»), en la rama `exp/52-legitimas-reales`.
  `conjuntos.preparar_legitimas_reales` arma un conjunto `legitimas_reales`, con las 33 en la vista principal y la zona
  gris en una vista aparte. El Colab lo corre si se sube la carpeta `sets/` y se pone su ruta en `LEGITIMAS_REALES`.
  En la zona gris, `legitima_dificil` es solo para que el formato valide: no se cuenta como falsa alarma.

> **Nota del 2026-11-20:** por decisión de Mateo, los dos sets se publican en
> [`casos/externo/legitimas-reales/`](../../experiments/slm-directo/casos/externo/legitimas-reales/), aunque la ficha
> prohíbe redistribuir, para que el equipo los vea y las corridas no dependan de subirlos a mano. Se publican texto,
> referencia y roles; `correspondencia.json` sigue fuera de Git por los teléfonos. El resto de esta sección queda
> como estaba.

### 8.5. Límites para informar

- **Todo es B2B y de un solo rubro.** Quien atiende es el dueño o un empleado de un negocio, y en general ya es
  cliente o había pedido algo. Por la regla de alcance entra, porque llama la empresa a un número que no está
  agendado, pero no es un particular al que lo llama un desconocido. No hay entregas, turnos, bancos ni cobranzas.
- **Español neutro y contexto de EE. UU.,** como el set coreano. El detector se ajustó sobre rioplatense.
- **Roles inseguros.** La fuente no trae hablantes. Los traductores marcaron con duda 530 turnos de las dos tandas,
  sobre todo en telecomunicaciones, donde hay pocas pausas. Un error de rol importa porque la configuración consulta
  solo en las líneas de `OTRA`.
- **Ningún humano leyó las llamadas.** Traducción, anotación y adjudicación son de IA. La sesión que coordinó no
  leyó llamadas: vio conteos y las justificaciones de una línea. `a1` repitió la misma justificación en 42 llamadas,
  así que esa anotación es de baja calidad. No cambia el set, porque la otra anotación también deja esas 42 fuera de
  las legítimas.
- **Duración acotada:** se dejaron afuera las llamadas de más de 15 minutos. En telecomunicaciones la mediana es de 19
  minutos, así que el set queda sesgado hacia las cortas.
- **Datos ficticios:** hay un valor por tipo de marcador y por llamada. Si se nombra al agente y al cliente, los dos
  pueden quedar con el mismo nombre.
