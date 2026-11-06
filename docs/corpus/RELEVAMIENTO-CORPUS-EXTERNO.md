# Relevamiento de fuentes para el corpus externo

Pasos 1 y 2 de [#144](https://github.com/Corchets/bitacora_tesis/issues/144): qué conversaciones
externas sirven para probar si el sistema generaliza fuera de nuestro generador. Relevado el
**2026-11-06**. No arma el set (paso 3), no marca referencias (paso 4) y no corre detectores.

> **Estado: propuesta sin discutir.** La elección y los descartes de este documento son una
> recomendación para el equipo. El tamaño y la composición del set siguen abiertos en
> [D08](../gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

## 1. Resultado en breve

- **Ninguna fuente trae a la vez estafas y legítimas parecidas a una estafa en llamadas reales.**
  Las dos fuentes elegidas aportan solo estafas. Faltan legítimas difíciles (ver §5.1); sin
  ellas no se puede armar el set balanceado del paso 3.
- **Elegidas (propuesta):** las estafas reales de KorCCVi v2 (coreano, publicadas por el FSS de
  Corea) y un subconjunto de las 20 llamadas de *scambaiters* de YouTube. El filtro de KorCCVi
  (§3.1.1) deja 16 llamadas con comienzo y pedido, y 10 más con pedido pero sin comienzo.
- **Descartadas:** PIX Scam BR, porque la conversación no define la clase, y el multi-agente de
  BothBosu y sus parientes sintéticos, porque son demasiado fáciles. También tres fuentes sin
  procedencia o sin ficha.
- **Pendientes, sin muestra:** el honeypot de Traister et al., ES-Port (legítimas reales en
  español) y TeleAntiFraud. No se pudieron abrir desde esta sesión (§4).
- **Formato del set:** todas van como conversaciones con identificador neutro y en la misma
  carpeta. La clase y las marcas quedan en una referencia aparte que el detector no ve (§5.4).

## 2. Qué se miró y cómo

Para cada fuente se leyó la ficha y se registraron idioma, tamaño, origen real o sintético,
licencia, presencia de legítimas y tipos de estafa. Después se leyó una muestra de unos 10
diálogos con cuatro preguntas del issue:

1. ¿Es creíble como llamada?
2. ¿Las legítimas son realistas o triviales?
3. ¿La estafa se construye distinto que en nuestro corpus (más lenta, más sutil)?
4. ¿Los tipos de estafa tienen equivalente en Argentina? Se compara con las familias del
   [catálogo](CATALOGO-ESCENARIOS.csv): banco, organismo previsional, premio, soporte,
   familiar, WhatsApp y policial/judicial.

Se agregó una pregunta propia del proyecto: **¿se puede marcar `T_R`?** La conversación tiene
que contener el pedido de alto riesgo y algo de construcción antes de él. Si la estafa ya
empezó cuando arranca la transcripción, no hay margen para medir el aviso anticipado
([`METRICAS.md`](../evaluacion/METRICAS.md)).

Muestreo: semilla 144 en Python (`random.sample`). Los datos crudos se bajaron al espacio
temporal de la sesión, fuera de Git. Este documento no copia diálogos.

## 3. Fuentes revisadas con muestra

### 3.1. KorCCVi v2: estafas reales del FSS coreano (elegida, solo estafas)

| Campo | Dato |
|---|---|
| Fuente | [selfcontrol7/Korean_Voice_Phishing_Detection](https://github.com/selfcontrol7/Korean_Voice_Phishing_Detection), commit `93b5b07a9a73b20d2e686f82e5115ba850e21b9c`, `Multimodal/data/transcripts/` |
| Idioma | Coreano |
| Tamaño | 706 llamadas de vishing y 711 legítimas. Transcripción automática (Naver CLOVA) con hablante por segmento |
| Origen | **Real.** Grabaciones que víctimas compartieron con el regulador financiero coreano (FSS) y que este publica como material de prevención |
| Licencia | **No redistribuible.** [`DATA.md`](https://github.com/selfcontrol7/Korean_Voice_Phishing_Detection/blob/93b5b07a9a73b20d2e686f82e5115ba850e21b9c/DATA.md) §2 y §5: los autores no pueden licenciar los datos, las transcripciones son obra derivada y piden no redistribuir el original ni derivados. El uso permitido se confirma con el FSS |
| Legítimas | Llamadas de AI Hub (educación, servicios públicos, comercio) elegidas a propósito **lejos de lo financiero**. Exigen aprobación individual y no se pueden redistribuir. El propio `DATA.md` §4 avisa que la fuente predice la clase |
| Tipos | Por palabras clave sobre las 706: 351 suplantan a fiscalía o policía, 154 son de préstamo o refinanciación y 201 son otras |

Duración de las estafas: mediana 92 s; el 10 % de las más largas pasa los 543 s. Hay **141 llamadas
de 4 minutos o más, con 2 hablantes o más y 20 turnos o más** (101 de fiscalía o policía, 33 de
préstamo, 7 otras). En 232 llamadas el reconocimiento detectó un solo hablante.

Muestra (10 estafas y 4 legítimas): `vishing_512`, `vishing_131`, `vishing_518`, `vishing_174`,
`vishing_255`, `vishing_465`, `vishing_180`, `vishing_75`, `vishing_477`, `vishing_557`; legítimas
`d04j18s004207`, `d02j05s001066`, `d02j10s006589`, `d04j18s021884`.

- **Creíble como llamada:** sí; es la única fuente revisada con estafas reales entre estafador y
  víctima. Pero muchas son **recortes**: el FSS publica fragmentos y varios arrancan en medio de
  la maniobra (`vishing_131`, `vishing_477`, `vishing_518`). La atribución de hablantes falla en
  algunos turnos (`vishing_180` mezcla tres).
- **Legítimas:** triviales para esta prueba (consultas de envíos o de trámites). No se proponen.
- **Construcción:** en las llamadas largas, **más lenta que en nuestro corpus,** que es lo que
  busca el issue. El falso fiscal o policía arma un expediente (una cuenta a nombre de la
  víctima, la banda detenida, el número de causa), aísla a la persona (la llamada «se graba» y
  no puede haber otra voz, no se corta, `vishing_174`, `vishing_180`, `vishing_557`) y amenaza
  con congelar todas sus cuentas. En `vishing_512` (208 s) y `vishing_557` (730 s) **no aparece
  todavía un pedido explícito** de dinero o credenciales: las grabaciones terminan antes. Que
  una llamada sea larga no garantiza que tenga `T_R`.
- **Equivalente local:** la suplantación de fiscalía o policía corresponde a
  `SC-POLICIA-RESGUARDO-01` («resguardo de fondos por una causa judicial»). El préstamo
  preaprobado o la refinanciación no tiene fila en el catálogo; habría que decidir si se acepta
  sin semilla local.
- **`T_R`:** marcable solo en las llamadas que contienen el pedido. En los recortes cortos suele
  faltar la construcción; en algunas largas falta el pedido. El filtro de §3.1.1 revisa las 141.

**Propuesta:** tomar las estafas del grupo A del filtro y, si hacen falta más, del grupo B. Como
no se puede redistribuir, versionar solo los identificadores (`vishing_N.json` y el commit) y
el procedimiento, como indica el issue. Adaptar del coreano al rioplatense es el cambio más
grande de todas las fuentes (ver §5.2).

#### 3.1.1. Filtro de las 141 llamadas largas (2026-11-06)

Resultado por llamada: [`FILTRO-KORCCVI.csv`](FILTRO-KORCCVI.csv). Solo trae identificadores,
duración, grupo, etiqueta y tiempo aproximado del primer pedido y una nota breve; no copia texto.

**Cómo se hizo.** [`filtrar_korccvi.py`](../../experiments/laboratorio/filtrar_korccvi.py) toma las
llamadas de 4 minutos o más, con 2 hablantes o más y 20 turnos o más. Busca pedidos candidatos
por palabra clave, agrupados por las etiquetas del [manual](MANUAL-ANOTACION.md#2-cómo-ubicar-las-marcas-y-resolver-dudas),
y descarta las advertencias del tipo «no le vamos a pedir la clave». Marca 91 con algún candidato
del hablante que más habla. Después se leyó cada llamada: el comienzo, el contexto de los
primeros candidatos y, si no había ninguno, el final. En las dudosas hubo una segunda búsqueda
(cuentas virtuales, «cuentas seguras», visitas, archivos para descargar).

| Grupo | Criterio | Llamadas |
|---|---|---:|
| **A** | Incluye el comienzo de la llamada (o de esta llamada de la serie) y un pedido de alto riesgo del llamante | 16 |
| **B** | Tiene pedido, pero la transcripción arranca en medio de la maniobra | 10 |
| Dudosa | Puede haber pedido, pero no está claro en el texto | 19 |
| C | Sin pedido observable, pedido sin construcción previa, víctima que se burla o corta, o cumplimiento anterior al fragmento | 96 |

Lo que muestra el grupo A:

- **Tipos:** 7 de fiscalía o policía, 5 de préstamo, 1 de falso banco (`vishing_540`), 1 de app
  de «seguridad» (`vishing_281`) y 2 de empleo o alquiler de cuentas, donde la víctima termina
  como intermediaria (`vishing_298`, `vishing_538`). Estas dos últimas no tienen fila en el
  catálogo.
- **Pedido:** en 9 de 16 el primer pedido es `REQUEST_SECURITY_ACTION`. En las de fiscalía casi
  siempre es entrar a un sitio falso del organismo y cargar datos. En el catálogo,
  `SC-POLICIA-RESGUARDO-01` usa la misma suplantación pero termina en mover el dinero: es
  parecida, no igual.
- **Margen antes del pedido:** en 12 el primer pedido llega a los 2 minutos o más (hasta unos
  37 minutos en `vishing_637`). En 4 llega antes del minuto (`vishing_448`, `vishing_540`,
  `vishing_577`, `vishing_657`); varias son la segunda llamada de una serie y la construcción
  quedó en la primera.

Con 16 del grupo A y unas 7 de YouTube hay 23 estafas, la mitad de un set de 46 diálogos.
Para llegar al mínimo de 50 del issue hacen falta algunas del grupo B; con las 10 se llega a
33 estafas, la mitad de un set de 66.

Límites del filtro: el tiempo es el comienzo del turno que contiene el pedido según la
diarización automática, no `T_R`. `T_R` se marca a mano en el paso 4 con la [guía de #32](MANUAL-ANOTACION.md).
Lo leyó una sola persona (asistente de IA); las 19 dudosas y los grupos A y B necesitan una
segunda lectura humana, idealmente de alguien que lea coreano.

### 3.2. YouTube scam conversations, BothBosu (elegida en parte, solo estafas)

| Campo | Dato |
|---|---|
| Fuente | [BothBosu/youtube-scam-conversations](https://huggingface.co/datasets/BothBosu/youtube-scam-conversations), commit `d0b94f1e2a9522af4703154c805d02d5c596110d` |
| Idioma | Inglés (EE. UU.) |
| Tamaño | 20 conversaciones, 208 a 1301 palabras (media 482) |
| Origen | **Real** del lado del estafador; transcripción de videos de *scambaiters* (13 de Scammer Jammer, 3 de Rinoa Poison, 2 de scambait tv, 1 de Scammer Payback, 1 de Lewis's Tech) |
| Licencia | La ficha solo declara Apache 2.0, sin texto ni procedencia. Quien subió el dataset no es dueño de los videos: **los derechos de redistribución no están claros** |
| Legítimas | Ninguna (las 20 tienen `labels = 1`) |
| Tipos | 7 premio, 5 soporte técnico, 4 reintegro, 4 seguridad social (`ssn`) |

Muestra: se leyó el comienzo de las 20 (hasta unos 1600 caracteres cada una).

- **Creíble como llamada:** a medias. El estafador es real, pero la «víctima» actúa: se hace la
  confundida, inventa historias o confronta (`#10`, `#17`, `#19`). 18 de 20 son llamadas
  `outgoing`: el *scambaiter* devuelve la llamada y el estafador atiende «gracias por llamar a…».
  En nuestro corpus llama el estafador. En 11 diálogos hay 87 cambios de hablante pegados en la
  misma línea, y en `#0` hay turnos atribuidos al hablante equivocado.
- **Construcción:** más larga y con más rodeos que en nuestro corpus. El pedido llega tarde
  (soporte: guiar paso a paso hasta instalar AnyDesk o TeamViewer).
- **Equivalente local:** soporte y reintegro → soporte (`SC-SOPORTE-REMOTO-01`); premio → premio
  (`SC-PREMIO-01`); seguridad social → organismo previsional (`SC-ORG-BENEFICIO-01`), con la
  diferencia de que en EE. UU. el número de seguridad social es el dato pedido.
- **`T_R`:** marcable en las que la víctima colabora hasta el pedido.

**Propuesta:** quedarse con las que no se vuelven parodia y donde el pedido aparece; a primera
lectura, `#3`, `#4`, `#7`, `#11`, `#13`, `#14` y `#15`. Corregir la atribución de hablantes
antes de adaptar. Por los derechos dudosos, tratarla como no redistribuible: versionar índice
de fila y commit. Los nombres y teléfonos que aparecen los inventaron los *scambaiters*, pero se
tratan como datos identificables y no van al repo.

### 3.3. PIX Scam Challenge BR (descartada)

| Campo | Dato |
|---|---|
| Fuente | [ai-safety-brazil/pix-scam-challenge-br-synthetic](https://huggingface.co/datasets/ai-safety-brazil/pix-scam-challenge-br-synthetic), commit `acdc964b67fea50300fa82033af2ca9db86fbe4d`, versión 1.0.0 (2026-10-28) |
| Idioma | Portugués de Brasil |
| Tamaño | 3000 casos en 1000 grupos de tres; conversaciones de 4 a 6 turnos (media 124 palabras) |
| Origen | Sintético (`Qwen3.6-35B-A3B`), filtrado por otro modelo; sin revisión humana según la ficha |
| Licencia | CC BY 4.0 (datos) y MIT (código), con atribución obligatoria |
| Legítimas | Sí: 1000 `legitimate` y 1000 `insufficient_evidence` |
| Tipos | 10 familias: identidad familiar, factura de proveedor, origen de un reintegro, comprobante, QR, intermediario de marketplace, colecta, seña de un servicio, reserva de alquiler, contacto del banco |

Muestra: un grupo por familia (30 casos), por ejemplo `b87dcd6c3c30c83372dd7a21` (contacto del
banco) y `e24a2dc7241413744ff93451` (identidad familiar); la lista completa está en §6.

- **La conversación no define la clase.** Se verificó en los 1000 grupos: los tres casos de un
  grupo tienen **la misma conversación** y solo cambia un párrafo de «evidencia» externo (lo que
  dice el sistema del banco, el comprobante o la verificación de la clave). La ficha lo dice: un
  clasificador que solo mira la conversación no supera 1/3 de aciertos. Nuestro detector solo ve
  la conversación, así que cualquier resultado mediría la evidencia inventada y no la llamada.
- **No son llamadas.** Casi todos son chats (`mensagem` aparece en 127 contextos y `chat` en 97,
  frente a 35 `ligação`). Solo la familia de contacto del banco se parece a una llamada.
- Seis turnos no dejan construcción antes del pedido; no se puede medir anticipación.

### 3.4. Multi-agent scam conversation y parientes sintéticos de BothBosu (descartadas)

| Campo | Dato |
|---|---|
| Fuente | [BothBosu/multi-agent-scam-conversation](https://huggingface.co/datasets/BothBosu/multi-agent-scam-conversation), commit `709db2b6c37f424c3070f29138abb33971e21ab9` |
| Idioma | Inglés (EE. UU.) |
| Tamaño | 1600 diálogos (800 y 800), 3 a 20 turnos (media 12), 527 palabras de media |
| Origen | Sintético: dos agentes (Autogen y Together), con 8 personalidades de receptor |
| Licencia | Apache 2.0 |
| Legítimas | Sí: entrega, venta de seguro, turno, número equivocado (200 de cada uno) |
| Tipos | Seguridad social, reintegro, soporte técnico, premio (200 de cada uno) |

Muestra (filas de `agent_conversation_all.csv`): estafas 459, 36, 465, 83, 739; legítimas 973,
1206, 890, 1479, 1219.

- **Demasiado fácil.** «social security» aparece en el 60,8 % de las estafas y en el 0,3 % de las
  legítimas; «suspicious», en el 32,8 % y el 0,7 %. En 193 de las 200 estafas de seguridad
  social, el primer turno del llamante ya nombra o pide el número.
- **Legítimas triviales:** entregas y números equivocados; ninguna se parece a una estafa. Las de
  seguros son lo más cercano.
- Tanto el issue como [S006 en la síntesis](../investigacion/SINTESIS-ESTADO-DEL-ARTE.md) anticipan
  el problema: modelos que dan F1 = 1 sobre BothBosu caen a 0,02–0,40 en llamadas reales.

Por diseño y por ficha se descartan también, **sin leer muestra**,
[scam-dialogue](https://huggingface.co/datasets/BothBosu/scam-dialogue) y
[single-agent-scam-conversations](https://huggingface.co/datasets/BothBosu/single-agent-scam-conversations)
(mismas clases, generadas con Llama 3), [Scammer-Conversation](https://huggingface.co/datasets/BothBosu/Scammer-Conversation)
(tabular, generada con Gretel) y
[shakeleoatmeal/phone-scam-detection-synthetic](https://huggingface.co/datasets/shakeleoatmeal/phone-scam-detection-synthetic)
(Llama 8B; soporte, seguridad social y reintegro).

## 4. Otras fuentes encontradas

Búsqueda en el buscador de Hugging Face (`scam`, `vishing`, `fraud-call`, `phone-scam`, `estafa`,
`golpe`, `fraude`, `scambait`, `voice-phishing`, `telecom-fraud`) y en la literatura ya
registrada en la [síntesis §2.3](../investigacion/SINTESIS-ESTADO-DEL-ARTE.md#23-datasets-y-límites-de-reutilización-recuperación-de-43).

| Fuente | Qué es | Situación |
|---|---|---|
| Honeypot de voz, [Traister et al. 2026](https://arxiv.org/abs/2609.29528) | 1000 llamadas reales de estafa y spam, largas (mediana 19,8 min), en inglés; responde un agente LLM; CC BY-NC | **Pendiente, alto interés.** Se distribuye por `scam.ai/research`, que no está habilitado en esta sesión. Limitación: la «víctima» es un agente, no una persona. Sin legítimas |
| [ES-Port](https://github.com/Vicomtech/esport-corpus) | 1170 llamadas reales a soporte técnico de una operadora española, anonimizadas; CC BY-SA 3.0 ES | **Pendiente.** Única fuente de **legítimas reales en español** del relevamiento, cercana a la familia soporte. La descarga (`datasets.vicomtech.org`) no está habilitada en esta sesión |
| [TeleAntiFraud-28k](https://huggingface.co/datasets/JimmyMa99/TeleAntiFraud) y [TeleAntiFraud 2.0](https://arxiv.org/abs/2609.18748) | Chino. 28k mezcla llamadas reales regeneradas con TTS y sintéticas. 2.0 publica sets mensuales congelados con legítimas del mismo dominio | **Pendiente.** En Hugging Face pide cuenta y aceptar condiciones. Lo interesante son las legítimas cercanas de 2.0, aunque son sintéticas |
| [HyaDoo/ko-voicephishing-binary-classification](https://huggingface.co/datasets/HyaDoo/ko-voicephishing-binary-classification) | 8725 fragmentos en coreano, sin turnos ni hablantes | Descartada: parece derivada del FSS sin procedencia; conviene ir al original (§3.1) |
| [BaekRok/vishing_data_3](https://huggingface.co/datasets/BaekRok/vishing_data_3) | Unos 80 GB de audio coreano con segmentos | Descartada: sin ficha ni procedencia |
| [sumitkant/scam-nonscam-youtube-calls](https://huggingface.co/datasets/sumitkant/scam-nonscam-youtube-calls) | Dos `.tar.gz` (1,3 GB) | Descartada por ahora: sin ficha ni licencia; no se abrió |
| [menaattia/phone-scam-dataset](https://huggingface.co/datasets/menaattia/phone-scam-dataset) | 4000 diálogos en inglés de 2 o 3 turnos | Descartada: sin procedencia ni licencia (ya registrado en la síntesis) y demasiado cortos |
| [ScamBench](https://huggingface.co/datasets/Shouninger/ScamBench) y [AmSpotNot1221/scam-call](https://huggingface.co/datasets/AmSpotNot1221/scam-call) | Sin ficha pública | No inspeccionadas: acceso restringido |

## 5. Lo que bloquea el paso 3

### 5.1. Faltan legítimas difíciles

El paso 3 pide 50 a 80 diálogos balanceados, con legítimas parecidas a una estafa. Ninguna
fuente revisada las trae en llamadas: KorCCVi y AI Hub son triviales y no redistribuibles, y las
de BothBosu y PIX son triviales o no son llamadas. Opciones, para decidir en equipo:

1. **ES-Port** para legítimas de soporte, reales y en español. Cubre una sola familia y hay que
   bajarla y revisarla.
2. **Set solo de estafas** para medir detección y adelanto `L_R`, y medir falsas alarmas aparte
   con legítimas propias. Pierde la comparación en igualdad de condiciones.
3. **Legítimas escritas por el equipo** sobre los mismos temas. Dejan de ser «externas»: tendría
   que hacerlas alguien que no desarrolló el detector y habría que declararlo como límite.

### 5.2. Traducción y adaptación

Las estafas elegidas están en coreano e inglés. El issue pide adaptarlas sin cambiar la
estructura. Con KorCCVi hay que decidir qué se hace con las instituciones (fiscalía de Seúl →
¿fiscalía federal?), los montos y los procedimientos que no existen acá (cuentas «seguras» del
FSS), sin volverlas más explícitas. Conviene probar el prompt de traducción en 2 o 3 llamadas y
revisarlas a mano antes de traducir el resto.

### 5.3. Derechos

KorCCVi no se puede redistribuir y la fuente de YouTube tiene derechos dudosos. En los dos casos
al repo van solo identificadores, commit y procedimiento; el texto adaptado tampoco se versiona
mientras no esté claro que el derivado está permitido. Esto es más estricto que lo que pide el
issue («al repo sube solo el texto adaptado»), porque el `DATA.md` de KorCCVi pide no distribuir
derivados.

### 5.4. Formato: todas son conversaciones

Pedido del equipo (2026-11-06): el detector tiene que recibir solo la conversación, como si
fuera una llamada cualquiera que está llegando, sin nada que se pueda relacionar con si es o no
una estafa.

**Lo que ya está resuelto.** El circuito de `experiments/slm-directo` ya separa las dos cosas: el
detector recibe, en cada paso, solo las líneas de una llamada que llegaron hasta ese momento. No
recibe el `case_id`, la clase, el escenario ni las marcas ([`detectores.py`](../../experiments/slm-directo/detectores.py),
encabezado). La referencia la lee el resto del circuito, no el detector. Si el set externo usa el
mismo formato (`casos/texto/` y `casos/referencia/`), se corre igual que la reserva sin tocar el
código.

```mermaid
flowchart LR
    subgraph custodia["Solo quien custodia el set · fuera de Git"]
        F["Fuentes originales<br/>KorCCVi, YouTube, legítimas"]
        M["Correspondencia<br/>original → EXT-NNN"]
        R["Referencia por EXT-NNN<br/>clase, T_R, T_C, fuente"]
    end
    subgraph congelado["Set congelado · hashes SHA-256"]
        T["texto/EXT-NNN.txt<br/>solo turnos A: / B:"]
    end
    F -- "misma adaptación y limpieza para todas<br/>IDs por sorteo" --> T
    F --> M
    T -- "marcado a mano con la guía de #32" --> R
    T --> C["correr.py<br/>entrega línea por línea"]
    C -- "solo las líneas hasta ahora" --> D(["Detector"])
    D -- "aviso o sin aviso" --> C
    C --> A["Registro de avisos<br/>por EXT-NNN"]
    A --> S["Métricas"]
    R --> S
```

**Reglas del set:**

- **Una carpeta y un formato para todas.** Nada de carpetas por clase como `vishing/`,
  `legitima/` y `dificiles/` en [`experiments/laboratorio/casos`](../../experiments/laboratorio/casos).
- **Identificadores neutros**: `EXT-001`, `EXT-002`, …, asignados por sorteo con semilla
  registrada. Sin prefijos que delaten clase, fuente o tipo. Los del corpus propio sí los tienen
  (`CV2-D-L-…` para legítimas y `CV2-D-V-…` para estafas). Hoy no llegan al detector, pero se ven
  en los registros y en las carpetas: para el set externo conviene que ni eso sugiera la clase.
- **El archivo de cada conversación tiene solo los turnos**, `A:` y `B:`, una línea por turno.
  Sin encabezados, comentarios ni metadatos. Quién es la persona protegida va en
  `roles-protegida.json`, que usa el circuito y no el detector.
- **La referencia, la correspondencia con el original y este documento quedan del lado de la
  custodia.** [`FILTRO-KORCCVI.csv`](FILTRO-KORCCVI.csv) es material de curaduría y no entra al set.

**Lo que puede seguir delatando la clase está en el texto mismo**, no en los archivos. Separar
los archivos no alcanza si las estafas y las legítimas se distinguen por su forma:

| Indicio | Cómo reducirlo |
|---|---|
| Rótulos de la fuente: YouTube usa `Suspect` e `Innocent` | Reemplazarlos por `A` y `B` y revisar que no queden dentro de las líneas |
| Huellas de cada fuente: errores de diarización de KorCCVi, frases cortadas | La misma limpieza para todas; corregir la atribución antes de adaptar |
| Estilo de la traducción: si solo se traducen las estafas, «suenan traducidas» | Pasar las legítimas por el mismo proceso, idealmente desde otro idioma también |
| Largo: las estafas de KorCCVi duran minutos | Elegir legítimas de largo parecido y comparar la distribución por clase |
| Cómo empieza: las estafas arrancan en medio de la maniobra, las legítimas con el saludo | Que todas arranquen igual, o que en las dos clases haya de las dos formas |
| Orden: todas las estafas juntas, o la estafa siempre en el mismo lugar | Sorteo de IDs y de orden de corrida |

**Prueba de fuga antes de congelar.** Quien custodia el set entrena clasificadores triviales que
no entienden de estafas: uno solo con el largo y el número de turnos, y otro con TF-IDF y
regresión logística, con validación dejando una conversación afuera. Si alguno acierta la clase
bastante más que el azar, hay un atajo de forma: se busca y se corrige antes de congelar. Es lo
mismo que hizo PIX Scam BR con sus líneas de base (§3.3). Con 50 a 80 conversaciones la prueba
detecta solo atajos gruesos, y conviene declararla como límite.

**Quién ve qué.** Quien desarrolló el detector no ve las conversaciones ni la referencia antes
de la corrida ([protocolo, ceguera previa](../evaluacion/PROTOCOLO-EXPERIMENTAL.md)). La custodia
adapta, marca, prueba la fuga, congela y corre.

## 6. Reproducibilidad

| Fuente | Revisión | Cómo se obtuvo |
|---|---|---|
| KorCCVi v2 | `93b5b07a9a73b20d2e686f82e5115ba850e21b9c` | `git clone --sparse`, carpeta `Multimodal/data` |
| YouTube scam conversations | `d0b94f1e2a9522af4703154c805d02d5c596110d` | `youtube_scam_conversations.csv` |
| Multi-agent scam conversation | `709db2b6c37f424c3070f29138abb33971e21ab9` | `agent_conversation_all.csv` |
| PIX Scam Challenge BR | `acdc964b67fea50300fa82033af2ca9db86fbe4d` | API de filas de Hugging Face (`datasets-server`), splits `development` y `test` |

Grupos de PIX leídos, uno por familia: `b87dcd6c3c30c83372dd7a21`, `e24a2dc7241413744ff93451`,
`0308cae0b082b846d4a240ad`, `451ea20c17d71a1eed595778`, `64240fb870a4bc4eebee0f05`,
`c41f9f8d146df4ff6719215c`, `1ffe1cc7176b9ba7e2328c66`, `fe0388a91d3cc551419a883d`,
`808eee95db323ac22a12d518`, `d587a4ea65fe008f50090893`.

Los conteos por palabra clave (tipos de KorCCVi, atajos léxicos de BothBosu) son una búsqueda
de cadenas sobre el texto, no una anotación; sirven para describir la fuente, no como referencia.
