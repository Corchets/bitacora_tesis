# Ventana de contexto y lógica de alerta

**Fecha:** 2026-09-16 (consolidación v3; secciones 11 y 12 agregadas el 2026-09-18)
**Sobre:** el primer pedido del profesor —si el contexto acumulado degrada la performance en una
llamada larga— y el margen de falsas alarmas de
[D08](../gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).
Issue: [#23](https://github.com/Corchets/bitacora_tesis/issues/23).
**Estado:** propuesta técnica de diseño e investigación para el issue #23. **No cierra D08.** No es un ADR. A ratificar por los cuatro.

Consolidación de lo trabajado sobre el primer pedido del profesor. Este archivo es la fuente de
verdad de esta investigación; los documentos principales solo enlazan acá.

Convertido del documento de trabajo `Ventana de contexto - consolidacion v3 2026-09-16.docx`
sin cambios de contenido: solo se reemplazó la portada por este encabezado.

> **Estado de este documento**
> **Borrador de trabajo del 16 de septiembre de 2026.** Todo lo que se propone acá es **propuesta sin discutir**: no fue validado por el grupo completo ni por el profesor.
> Los resultados numéricos salen de **llamadas sintéticas construidas a mano**. Sirven para probar si un diseño falla y por qué; **no miden rendimiento**.
> No se usa como fuente bibliográfica: el informe de Gemini citado es un insumo a verificar, no una referencia.

## Resumen: por dónde vamos

El profesor pidió averiguar si, en una conversación larga con procesamiento incremental, **el contexto acumulado degrada la performance**, con el ejemplo de que "pasame el código" dicho en un contexto legítimo no debería disparar una alerta.

Tomamos el informe de deep research de Gemini, recuperamos sus fórmulas (se habían perdido en la exportación a Markdown), revisamos los cuatro métodos que propone, encontramos errores verificables, armamos un diseño corregido y lo probamos sobre llamadas sintéticas.

#### Lo que sale en limpio

| **Hallazgo** | **Qué significa** |
|---|---|
| **Sí, el contexto acumulado degrada la performance** | En una llamada de prueba de 19 minutos, limitar cuánto hacia atrás se mira hace que el sistema pase de avisar tarde a avisar antes. **El mecanismo se sostiene; los segundos exactos no**, porque la llamada y los coeficientes son inventados. |
| **Las falsas alarmas se acumulan** | Un detector que acierta el 99% por actualización, actualizando cada 15 s, mete al menos una falsa alarma en el **55%** de las llamadas legítimas de 20 minutos. |
| **Eso da el margen de aceptación** | Se fija primero el máximo de llamadas legítimas con alerta y se deriva cuán bueno tiene que ser el detector. Es el método que pide D08. |
| **El informe de Gemini tiene tres errores** | Un rango de parámetro que no cumple lo que promete, una sigmoide sin sesgo, y una fórmula que hace imposible anticipar el pedido (rompe PI2). |
| **El registro conjunto de eventos es el aporte propio** | Guardar hechos del atacante y de la víctima, ordenados y con tiempo, es lo que separa una estafa de una llamada legítima del banco con los mismos marcadores. |
| **Con el diseño corregido, anticipar es posible** | La fórmula corregida puede avisar antes del pedido del código. Que lo haga bien en llamadas reales **todavía no está medido**: los coeficientes se eligieron a mano. |

#### Lo que falta

- **Armar el entorno de pruebas de llamadas.** Es lo que más falta: sin él, nada de esto está medido con conversaciones reales. Hoy todo sale de llamadas inventadas.
- **Quién detecta los eventos.** Todo el diseño supone que un turno ya viene etiquetado como `AISLAMIENTO` o `SOLICITUD_CRITICA`. Ese detector no existe todavía.
- **El presupuesto de tokens del modelo**, que depende de la elección de modelo (tema del compañero que está viendo modelos).
- **Ratificar decisiones con el grupo** (lista en la sección 9).

## Explicado en simple

*Versión para contarla en cinco minutos, sin fórmulas.*

#### 1. El problema

Una estafa telefónica puede durar veinte minutos. Si el sistema lee **toda** la conversación cada vez, se vuelve lento y se confunde con cosas viejas que no importan. Si lee **solo lo último**, se olvida de lo importante: que al principio el tipo dijo ser del banco.

#### 2. La idea: un anotador

Mientras la llamada avanza, un anotador apunta **solo los hechos importantes, con la hora**. No guarda la charla. Ocupa casi nada, así que puede durar toda la llamada.

`00:14  el que llama   dijo ser del banco`

`00:35  la víctima     preguntó quién era`

`00:42  el que llama   apuró ("hay que hacerlo ya")`

`01:30  el que llama   dijo "no cortes"`

`02:10  el que llama   pidió abrir la app del banco`

#### 3. Tres preguntas que se le hacen al anotador

| **Pregunta** | **Por qué sirve** |
|---|---|
| **¿Cuántas partes del guion de estafa aparecieron?** (presentarse como el banco, apurar, aislar, hacer abrir la app, pedir el código) | Mientras más partes, más se parece a una estafa. |
| **¿Aparecieron en el orden del guion?** | Una estafa sigue un libreto: primero se presenta, después apura, después aísla, al final pide. Una charla normal puede tocar algunas cosas pero desordenadas. |
| **Cuando la víctima desconfió, ¿el otro dio datos o apretó más?** | Si le preguntás al banco de verdad quién es, te da un legajo y te dice que llames al 0800. Un estafador apura más. **Es lo que más separa una estafa de una llamada real del banco.** |

#### 4. Los hechos se olvidan a distinta velocidad

Un apuro de hace diez minutos ya no importa. Que dijo ser del banco importa toda la llamada. Cada tipo de hecho se va borrando a su ritmo. Así lo viejo e irrelevante no confunde, y lo importante no se pierde.

#### 5. Hace falta presión y pedido, juntos

Presión sola (una llamada urgente del banco real) **no alcanza**. Pedido solo ("pasame el código" entre compañeros de trabajo) **no alcanza**. Las dos cosas juntas, sí. Por eso "pasame el código" en un contexto normal no dispara nada.

#### 6. No alertar por un pico

La alerta salta solo si el riesgo se mantiene alto dos revisiones seguidas, y no se repite: se muestra una vez por nivel.

#### 7. El problema de revisar muy seguido

El sistema revisa la llamada cada tantos segundos. Aunque se equivoque solo 1 vez de cada 100, en veinte minutos revisa ochenta veces: es como tirar ochenta veces un dado de 100 caras. **La chance de que alguna vez salga el error es 55%.** Por eso hay que decidir antes cuántas falsas alarmas se toleran y ajustar el sistema a eso.

#### 8. Lo que falta

Todo esto está probado con **llamadas inventadas por nosotros**. Muestra que la lógica tiene sentido, no que funcione. Para saberlo hace falta **armar un entorno de pruebas con llamadas VoIP** simuladas y medir con ellas.

## 1. Punto de partida

### 1.1 Los cinco pedidos del profesor

| **#** | **Pedido** | **Tipo de trabajo** |
|---|---|---|
| 1 | **Ventana de contexto:** si la conversación es larga y el procesamiento es incremental, el contexto acumulado puede degradar la performance. "Pasame el código" en contexto legítimo no debería alertar. | **Investigación propia. Es el que se desarrolla en este documento.** |
| 2 | Prefactibilidad técnica y legal: criterios, gama de dispositivos, modelos, márgenes de aceptación, velocidad. | Depende de 1, 3 y 5. |
| 3 | Umbrales: con qué comparar en otras investigaciones. | Bibliográfico. Sin bloqueos. |
| 4 | Papers sobre manipulación o tipos de manipulación; quién puede saber de esto (policía). | Bibliográfico. Alimenta la taxonomía (D07). |
| 5 | Entrenar, hacer fine-tuning o usar un modelo existente; métodos para recortar el modelo. | Lo está viendo un compañero. Depende de 1. |

### 1.2 Por qué empezar por la ventana de contexto

Se pensaba que la ventana de contexto estaba bloqueada por la elección del modelo. **Es al revés.** La política de ventana es un **requisito** que restringe qué modelo sirve: quien elija modelo necesita saber "el detector tiene que mirar hasta X de contexto y responder en Y milisegundos". Sin eso, elige a ciegas.

## 2. La pregunta, bien planteada

### 2.1 Tres problemas distintos

|  | **Subproblema** | **¿Depende del modelo?** |
|---|---|---|
| a | **Qué texto entra al detector** en cada actualización: todo lo acumulado, una ventana de los últimos turnos, o un estado resumido. | No. Es diseño del algoritmo. |
| b | **Cómo se acumula la evidencia** entre actualizaciones: memoria, decaimiento, histéresis. | No. |
| c | **El límite duro de tokens** del modelo concreto. | Sí, pero es un dato que se consulta. |

### 2.2 El ejemplo del profesor es sobre la unidad de anotación

"Pasame el código" es un indicador de estafa o no según **lo que vino antes**. Eso obliga a decidir si se etiqueta el turno aislado o el prefijo de conversación hasta ese turno (decisión D07). Y apunta **en contra** de recortar contexto: lo que distingue el caso legítimo del fraudulento es justamente la historia previa.

> **La tensión central**
> **Más contexto** desambigua mejor, pero diluye la señal, cuesta latencia y —como se muestra en la sección 7— acumula ruido que envenena las variables.
> **Menos contexto** es rápido y no diluye, pero no puede distinguir el pedido legítimo del fraudulento.

### 2.3 Relación con PI1

PI1 plantea evaluar con prefijos sucesivos (25%, 50%, 75%, 100% de la llamada). Eso mide **cuánta conversación transcurrió**, no **cuánta mira el detector**. Son dos ejes independientes y hoy están colapsados en uno. La pregunta del profesor es exactamente el eje que falta.

## 3. El informe de Gemini

Informe de deep research titulado «Análisis Técnico-Jurídico y Estrategia de Modelado para la Detección Incremental de Vishing en Dispositivos Móviles». Cubre los cinco pedidos del profesor, uno por sección. La sección 1 corresponde a la ventana de contexto.

### 3.1 Problemas del informe como fuente

| **Problema** | **Detalle** |
|---|---|
| **Las fórmulas se perdieron en el .md** | Estaban como imágenes PNG. Se recuperaron del .docx original leyéndolas una por una. |
| **Las URLs están corruptas** | Las 32 referencias dicen "htps://", los guiones pasaron a espacios y se perdieron ligaduras ("fnancieros", "fle.aspx"). Ninguna es copiable tal cual. |
| **La lista no está curada** | La referencia 32 es un repositorio de GitHub de un plugin de Obsidian, sin relación con el tema. Las otras 31 son sospechosas hasta abrirlas. |
| **No es corroboración independiente** | Coincide con el otro deep research del repo en la taxonomía de seis etiquetas. Que dos informes generados por modelos coincidan no prueba nada: pueden venir de las mismas fuentes o del mismo encuadre. |

### 3.2 Los cuatro métodos que propone

| **#** | **Método** | **Qué busca** | **Matemática recuperada** |
|---|---|---|---|
| 1 | **Ventana doble** | Separar el pedido explícito del contexto que lo vuelve sospechoso. | `W_loc` = 2–3 turnos del interlocutor externo · `W_ctx` = cola FIFO de 6–10 turnos, paso 1 · turnos cortados por VAD con silencio de 500–800 ms |
| 2 | **Leaky integrator** | Que un indicio viejo se desvanezca si nadie lo corrobora. | `R_t = α·R_t−1 + (1−α)·s_t · τ = −1/ln α · α ∈ [0,70; 0,85]` |
| 3 | **Acoplamiento multiplicativo** | Que un pedido legítimo no alerte si no hubo manipulación previa. | `S_t = C_t · σ(λ_1·M_t + λ_2·Σ w_i·M_t−i)` · `M` = manipulación, `C` = solicitud crítica |
| 4 | **Schmitt trigger** | Que la alerta no parpadee. | `θ_high` ≈ 0,75 para encender · `θ_low` ≈ 0,40 para apagar |

## 4. Revisión crítica de los cuatro métodos

### 4.1 Método 1 — Ventana doble

**La idea es buena.** Hay dos preguntas que necesitan cantidades de contexto opuestas: "¿qué me piden ahora?" necesita poco; "¿este pedido es raro?" necesita mucho. En vez de elegir una ventana, se corren dos en paralelo. La ventana local detecta el pedido de código **en los dos casos**; distinguir legítimo de fraudulento es trabajo de la ventana contextual.

#### Cómo funciona la cola FIFO

Es una **cola, no una pila**. Cada turno nuevo entra y expulsa al más viejo. No hay varias ventanas que se van gastando: hay una sola que se arrastra, y **el turno que sale desaparece**.

`turno 11 →  [ 2  3  4  5  6  7  8  9 10 11 ]  → se cae el turno 1`

`turno 12 →  [ 3  4  5  6  7  8  9 10 11 12 ]  → se cae el turno 2`

#### Debilidades

- Ve muy poco de una llamada larga. Con `W_ctx` = 10 turnos, en una llamada de 20 minutos se ve entre el 4% y el 12% (según dure un turno promedio, a medir en el corpus).

| **Turno promedio** | **Turnos en 20 min** | `Qué abarca W_ctx=10` | **% visible** |
|---|---|---|---|
| 5 s | ~240 | ~50 s | ~4% |
| 10 s | ~120 | ~100 s | ~8% |
| 15 s | ~80 | ~150 s | ~12% |

- **Olvida el pretexto.** "Le hablo del área de fraude del banco" se dice una vez, al principio. Con FIFO de 10 turnos desaparece al turno 12 — al minuto y medio — y el resto de la llamada el detector no sabe que el interlocutor dijo ser del banco.
- **Se mide en turnos, pero el límite real es en tokens.** Diez turnos pueden ser 30 palabras o 900.
- **No tiene formalización matemática.** Se resuelve en la sección 5.

### 4.2 Método 2 — Leaky integrator

#### Explicación sin matemática

Es **un balde con un agujero en el fondo**. Cada turno sospechoso echa agua; entre turno y turno se escurre un poco; la alerta salta cuando el agua pasa cierta altura. α es el tamaño del agujero: α alto → agujero chico → memoria larga; α bajo → se vacía rápido.

`R_t = α · R_t−1 + (1 − α) · s_t`

| **Variable** | **Qué significa** |
|---|---|
| `R_t` | Riesgo acumulado en el turno t (el agua del balde). |
| `R_t−1` | Riesgo acumulado en el turno anterior. |
| `s_t` | Sospecha del turno actual, entre 0 y 1 (el agua que se echa). |
| α | Retención, entre 0 y 1: qué parte del riesgo anterior se conserva (tamaño del agujero al revés). |
| τ = −1 / ln α | Constante de tiempo: turnos neutros para que el riesgo caiga al 37%. |

**Ejemplo con α = 0,8:**

| **Turno** | **1** | **2** | **3** | **4** | **5** | **6** | **7** | **8** |
|---|---|---|---|---|---|---|---|---|
| Presión sostenida · sospecha | 0,60 | 0,70 | 0,80 | 0,90 | 0,80 | 0,90 | 0,90 | 0,80 |
| Presión sostenida · **balde** | 0,12 | 0,24 | 0,35 | 0,46 | 0,53 | 0,60 | 0,66 | **0,69** |
| Pico aislado · sospecha | 0,00 | 0,00 | 0,90 | 0,00 | 0,00 | 0,00 | 0,00 | 0,00 |
| Pico aislado · **balde** | 0,00 | 0,00 | 0,18 | 0,14 | 0,12 | 0,09 | 0,07 | **0,06** |

**Una frase sospechosa suelta no alcanza; hace falta insistencia.** El costo: tarda en llenarse tanto como en vaciarse. No se puede tener memoria larga y reacción rápida con el mismo α.

#### Error verificado

El informe afirma que α ∈ [0,70; 0,85] "garantiza que la sospecha decaiga más del 80% al cabo de tres o cuatro turnos neutros". Con turnos neutros el riesgo se multiplica por α en cada turno:

| **α** | **τ (turnos)** | **Decae a los 3 turnos** | **Decae a los 4 turnos** | **Turnos para −80%** |
|---|---|---|---|---|
| 0,70 | 2,8 | 65,7% | 76,0% | **4,5** |
| 0,75 | 3,5 | 57,8% | 68,4% | **5,6** |
| 0,80 | 4,5 | 48,8% | 59,0% | **7,2** |
| 0,85 | 6,2 | 38,6% | 47,8% | **9,9** |

> **No se cumple en ningún punto del rango.** Para caer 80% en 4 turnos hace falta α ≤ 0,669; en 3 turnos, α ≤ 0,585. Lo correcto es decidir cuántos turnos de memoria se quieren y derivar α, o calibrarlo con el corpus.

**Además se pisa con el método 3:** los dos implementan memoria sobre la misma cantidad, y el informe no dice cómo se relacionan. Se resuelve en la sección 5.5.

### 4.3 Método 3 — Acoplamiento multiplicativo

`S_t = C_t · σ( λ_1·M_t + λ_2·Σ w_i·M_t−i )`

| **Variable** | **Qué significa** |
|---|---|
| `S_t` | Riesgo compuesto en el instante t. |
| `C_t` | Solicitud crítica: si hay un pedido de código, transferencia o instalación. |
| `M_t` | Manipulación contextual: suplantación, urgencia, aislamiento. |
| `M_t−i` | Manipulación de i turnos atrás. |
| `w_i` | Peso de cada turno pasado. |
| `λ_1`, `λ_2` | Pesos de la manipulación actual y de la pasada. |
| σ | Sigmoide: convierte cualquier número en uno entre 0 y 1. |

**Es la mejor idea de las cuatro.** Multiplicar en vez de sumar exige que estén las dos cosas: manipulación **y** pedido crítico. Responde de frente al ejemplo del profesor, y explica por qué una llamada legítima del banco —que tiene suplantación y urgencia pero nunca pide el código— no debería alertar.

#### Error 1: la sigmoide no tiene sesgo

`M_t = 0  →  σ(0) = 0,5  →  S_t = 0,5 · C_t`

Con un pedido de código explícito y cero manipulación, el riesgo da **0,50**. El informe dice que en ese caso queda "en niveles insignificantes". Medio punto de escala no es insignificante.

#### Error 2 (el más grave): `C_t` funciona como compuerta

`C_t = 0  →  S_t = 0, sin importar cuánta manipulación haya`

Mientras no haya un pedido crítico, el riesgo es exactamente cero: el sistema no puede alertar antes del primer pedido. PI2 mide `L_R` = `T_R` − `T_A`, la anticipación respecto del primer pedido riesgoso. Con esta fórmula `T_A` ≥ `T_R`, así que `L_R` ≤ 0 siempre, por construcción.

> La fórmula del informe hace que la métrica central de PI2 sea **estructuralmente imposible de dar positiva**. No es un problema de calibración: es la forma de la ecuación. La sección 6 lo confirma con una traza.

### 4.4 Método 4 — Schmitt trigger

Dos umbrales: se enciende al cruzar `θ_high` hacia arriba y se apaga al cruzar `θ_low` hacia abajo; en el medio mantiene el estado. Evita que la alerta prenda y apague en turnos seguidos, que para una persona mayor bajo presión es peor que no alertar.

#### Choque con lo que ya está en el repositorio

|  | **METRICAS.md** | **Informe de Gemini** |
|---|---|---|
| Mecanismo | Persistencia temporal: `T_A` es la primera predicción que se sostiene dos actualizaciones | Doble umbral: `θ_high` para encender, `θ_low` para apagar |
| Qué evita | Alertar por un pico transitorio | Que la alerta parpadee una vez encendida |

No son lo mismo, se pueden combinar y probablemente convenga. Pero hay que decidirlo: hoy circulan dos definiciones de `T_A`. Los valores 0,75 y 0,40 no tienen justificación en el informe; son valores iniciales a calibrar.

## 5. Diseño propuesto

> **Estado**
> **Propuesta sin discutir.** Casi todo lo de esta sección es elaboración propia, no sale del informe. Requiere validación del grupo.

### 5.1 Fuente de audio: VoIP

La inclinación del equipo es usar **VoIP** para la demostración final, porque permite simular una llamada real y capturar sin problemas al atacante y a la víctima. Eso corresponde a D05 y **debe ratificarse entre los cuatro**.

**Argumento técnico a favor:** en VoIP la app es el cliente de la llamada y cada hablante llega por su propio canal. Eso **elimina la diarización** (separar quién habla) del pipeline. Con altavoz, separar dos voces de un audio monofónico con reverberación y en tiempo real es un problema serio.

#### Sobre la sugerencia del profesor (micrófono vs. parlante)

El profesor sugirió investigar si desde el teléfono se puede saber qué componente está activo para identificar quién habla. **En lo conceptual tiene razón:** el teléfono tiene las dos señales por separado. Pero el mecanismo, tal como se planteó, tiene dos obstáculos:

- **El micrófono está activo toda la llamada.** Una llamada es full-duplex: no se apaga cuando habla el otro. Desde una app se puede leer el estado de ruteo de audio, no quién habla en cada instante.
- **El obstáculo real es de permiso.** El audio entrante de una llamada celular está reservado a componentes privilegiados (ya registrado como decisión cerrada en el mapa de decisiones).

Una vía que sí vale investigar es la **cancelación de eco acústico**, que por diseño separa la señal cercana de la lejana en modo altavoz. **Pendiente de verificar con documentación oficial de Android, con fuente y fecha de consulta.**

### 5.2 Tres estructuras en vez de dos ventanas

`W_loc     deslizante, corta         →  qué me piden ahora`

`W_ctx     deslizante, media         →  cómo viene la presión en los últimos turnos`

`REGISTRO  crece, no se desliza      →  qué quedó establecido en esta llamada`

#### Regla para medir `W_ctx`: tokens, turnos y tiempo

`W_ctx = los turnos más recientes que cumplan:`

| **Restricción** | **Valor inicial** | **Tipo** |
|---|---|---|
| Tokens | ≤ presupuesto del modelo | **Dura:** nunca se viola. Si no entran ni los turnos mínimos, se trunca el más viejo. |
| Turnos | mínimo 4, máximo ~12 | Blanda. El mínimo le gana al tope de tiempo. |
| Tiempo | span ≤ ~180 s | Blanda. Descarta lo viejo aunque sobren tokens. |

### 5.3 El registro de eventos

Es una lista que solo crece. **No guarda texto: guarda hechos tipados con marca de tiempo.** Por eso cuesta prácticamente cero tokens y puede durar la llamada entera.

`e_k = ( k , τ_k , ρ_k , γ_k , c_k )`

| **Campo** | **Significado** |
|---|---|
| k | Índice de orden: 1, 2, 3… |
| `τ_k` | Segundo de la llamada en que ocurrió. |
| `ρ_k` | Rol: **A** = atacante / interlocutor externo, **V** = víctima. |
| `γ_k` | Tipo de evento (SUPLANTACION, URGENCIA, AISLAMIENTO, DESVIO, SOLICITUD_CRITICA, RESISTENCIA, CUMPLIMIENTO, ACLARACION…). |
| `c_k` | Confianza del detector, entre 0 y 1. |

**Ejemplo de registro:**

`00:14   A   SUPLANTACION        "banco, área de fraude"`

`00:35   V   RESISTENCIA         "¿quién habla?"`

`00:42   A   URGENCIA            "hay que resolverlo ahora"`

`01:30   A   AISLAMIENTO         "no cortes"`

`04:10   A   SOLICITUD_CRITICA   "dictame el código"`

#### Los eventos de la víctima se parten en dos

| **Clase** | **Ejemplos** | **Uso** |
|---|---|---|
| **Resistencia** | "¿quién sos?", "¿de dónde me hablás?", "¿por qué querés esto?" | **Entra al modelo.** Es señal útil y ocurre antes del desenlace. |
| **Cumplimiento** | "mi código es 4-8-2…" | No entra al score de riesgo. Es `T_C`, el evento que el sistema busca prevenir. Si alimenta el score, el sistema alerta cuando la víctima ya está cumpliendo y `L_C` da cero por construcción. Sirve como marca de anotación y como freno de emergencia por una vía aparte, reportada por separado. |

### 5.4 Tres indicadores calculados sobre el registro

Los tres son **números entre 0 y 1** que se recalculan en cada revisión mirando el registro. Responden tres preguntas distintas.

#### (a) κ — Cobertura de fases

**Pregunta:** ¿cuántas partes del guion de estafa aparecieron? Guion canónico:

`1 suplantación → 2 urgencia → 3 aislamiento → 4 desvío → 5 solicitud crítica`

κ = fases del guion presentes / 5

| **Variable** | **Qué significa** |
|---|---|
| κ (kappa) | Cobertura del guion, entre 0 y 1. |
| fases presentes | Cuántas de las 5 fases tienen al menos un evento vigente en el registro. |

**Ejemplo:** hubo suplantación, urgencia y aislamiento → κ = 3/5 = 0,60. **Limitación:** no dice nada del orden. Para eso está Ω.

#### (b) Ω — Orden de la escalada

**Pregunta:** ¿los hechos aparecieron en el orden en que se arma una estafa?

**Paso a paso:**

1. Se toman los eventos del atacante **en el orden en que ocurrieron** (índice k) y se reemplaza cada uno por su número de fase. Suplantación, urgencia, aislamiento, solicitud → **[1, 2, 3, 5]**.
2. Se arman **todos los pares** (uno anterior, uno posterior). Con 4 eventos hay 6: (1,2) (1,3) (1,5) (2,3) (2,5) (3,5).
3. Un par está **en orden** si el anterior tiene número de fase menor que el posterior. Dos eventos de la misma fase (dos urgencias) no forman par.
4. Se divide: pares en orden sobre pares totales.

`Ω_crudo = pares en orden / pares totales`

| **Variable** | **Qué significa** |
|---|---|
| Ω (omega) | Orden de la escalada, entre 0 y 1. |
| pares totales | Todas las combinaciones anterior–posterior de eventos de fases distintas. |
| pares en orden | Los pares donde la fase del anterior es menor que la del posterior. |

| **Secuencia de fases** | **Qué es** | **Pares** | **En orden** | **Ω crudo** | **Ω suavizado** |
|---|---|---|---|---|---|
| [1, 2, 3, 5] | Guion completo, en orden | 6 | 6 | 1,00 | 0,83 |
| [2, 4, 1, 3] | Mezclado | 6 | 3 | 0,50 | 0,50 |
| [4, 1, 2] | Empieza por el desvío | 3 | 1 | 0,33 | 0,42 |
| [5, 4, 3, 2, 1] | Al revés | 10 | 0 | 0,00 | 0,12 |
| [1, 2] | Solo dos eventos | 1 | 1 | **1,00** | **0,62** |

**Cómo se lee:** 1 = escalada perfecta; 0,5 = sin patrón, como si los eventos cayeran al azar; cerca de 0 = al revés del guion.

**Suavizado.** Con solo dos eventos, Ω crudo ya vale 1,00: "orden perfecto" con casi nada de evidencia. Se suman **m pares imaginarios** que cuentan como "medio en orden", para que con poca evidencia el número quede cerca de 0,5 ("no sé") y con mucha evidencia pese lo real:

Ω = (pares en orden + m · 0,5) / (pares totales + m)

| **Variable** | **Qué significa** |
|---|---|
| m | Cantidad de pares imaginarios. Valor inicial 3, sin calibrar. |
| 0,5 | Valor de "no sé": la mitad de un par en orden. |

#### (c) δ — Respuesta a la resistencia

**Pregunta:** cuando la víctima desconfió, ¿el otro respondió con datos o apretó más?

**Paso a paso:**

1. Se buscan en el registro los eventos **RESISTENCIA** de la víctima.
2. Para cada uno se mira **el siguiente evento del atacante**: el primero que ocurre después.
3. Si ese evento es de **presión** (URGENCIA, AISLAMIENTO o DESVIO), cuenta como "respondió con presión". Si es **ACLARACION** u otra cosa, no.
4. Se divide: resistencias respondidas con presión sobre resistencias totales.

δ = resistencias respondidas con presión / resistencias totales

| **Variable** | **Qué significa** |
|---|---|
| δ (delta) | Respuesta a la resistencia, entre 0 y 1. |
| RESISTENCIA | La víctima desconfía: "¿quién sos?", "¿de dónde me hablás?", "¿por qué querés esto?". |
| presión | Eventos URGENCIA, AISLAMIENTO o DESVIO del atacante. |
| ACLARACION | El otro da datos verificables: legajo, "cortá y llamá al 0800 del dorso". |

| **Llamada** | **Resistencia de la víctima** | **Siguiente evento del otro** | **¿Presión?** |
|---|---|---|---|
| Estafa | t=35 "¿quién habla?" | t=42 URGENCIA | Sí |
| Estafa | t=90 "¿por qué no llamo yo?" | t=98 AISLAMIENTO | Sí |
|  |  | **δ = 2 / 2 = 1,00** |  |
| Legítima | t=40 "¿cómo sé que es el banco?" | t=48 ACLARACION | No |
|  |  | **δ = 0 / 1 = 0,00** |  |

**Limitaciones:**

- **Si la víctima nunca desconfía, δ vale 0 y no aporta nada.** Justo la víctima más vulnerable, la que no pregunta, es la que menos ayuda recibe de este indicador. Los otros dos siguen funcionando, pero hay que decirlo en la tesis.
- **"El siguiente evento" puede no ser una respuesta.** Si pasaron varios turnos, la relación es dudosa. Ajuste posible: contarlo solo si ocurre dentro de unos 30 segundos.
- **Depende del detector de eventos**: tiene que distinguir bien presión de aclaración.
- **Notación:** METRICAS.md ya usa δ en Preventive@δ (segundos). Si se adopta este indicador conviene renombrarlo.

### 5.5 Memoria del registro: cada hecho pierde peso a su ritmo

En vez de que un evento cuente entero hasta que se corta de golpe, cada evento tiene un **peso** que empieza en su confianza y baja con el tiempo. Se expresa con la **vida media** —el tiempo en que el peso cae a la mitad— porque se entiende mejor que α.

`peso_k(t) = c_k × 0,5 elevado a [ (t − τ_k) / h_γ ]`

| **Variable** | **Qué significa** |
|---|---|
| `peso_k(t`) | Cuánto cuenta el evento k en el instante t, entre 0 y 1. |
| `c_k` | Confianza del detector en ese evento. |
| t − `τ_k` | Edad del evento, en segundos. |
| `h_γ` | Vida media del tipo de evento γ, en segundos: a esa edad el peso vale la mitad. |

**Ejemplo con vidas medias ilustrativas (no calibradas), peso según la edad del evento:**

| **Tipo** | **Vida media** | **0 s** | **1 min** | **2 min** | **5 min** | **10 min** | **15 min** |
|---|---|---|---|---|---|---|---|
| URGENCIA | 60 s | 1,00 | 0,50 | 0,25 | 0,03 | 0,00 | 0,00 |
| AISLAMIENTO | 180 s | 1,00 | 0,79 | 0,63 | 0,31 | 0,10 | 0,03 |
| SUPLANTACION | 600 s | 1,00 | 0,93 | 0,87 | 0,71 | 0,50 | 0,35 |

**Cómo entra en los indicadores:** la presencia de una fase pasa a ser el mayor peso vigente de sus eventos, y κ = suma de presencias / 5 (ya no salta de 0 a 1: baja de a poco). Para Ω y δ se cuentan los eventos cuyo peso sigue por encima de un mínimo, por ejemplo 0,2.

**Relación con el leaky integrator:** es la misma idea —decaimiento exponencial— aplicada a cada hecho del registro y no al riesgo final. Así hay una sola memoria.

#### Cómo se mide

1. Punto de partida desde los datos. En las llamadas de fraude anotadas, medir cuántos segundos pasan entre cada tipo de evento y el pedido crítico (`T_R`). Si la suplantación ocurre típicamente 4 minutos antes del pedido, su vida media no puede ser de 1 minuto: cuando llegue el pedido ya no pesaría nada.
2. **Calibración en validación.** Probar una grilla de vidas medias por tipo (30, 60, 120, 300, 600 s y sin decaimiento) y quedarse con la combinación que da más anticipación (Preventive@δ) respetando el tope de falsas alarmas fijado antes. Siempre en el split de validación, nunca en test (D08).
3. **Comparación en test.** Correr el mismo detector en tres versiones: sin olvido, ventana dura de 300 s y decaimiento por tipo. Si el decaimiento no mejora, no se justifica y se reporta así.
4. **Sensibilidad.** Repetir con cada vida media a la mitad y al doble. Si el resultado se derrumba con cambios chicos, el mecanismo es frágil y hay que decirlo.

> Hoy **no se puede medir**: hacen falta el entorno de pruebas de llamadas y un corpus anotado con marcas de tiempo.

### 5.6 Combinación: de los indicadores a un riesgo

Se hace en tres pasos.

#### Paso 1 — Manipulación acumulada

`M_t = 0,40·κ + 0,30·Ω + 0,30·δ`

| **Variable** | **Qué significa** |
|---|---|
| `M_t` | Manipulación acumulada en el instante t, entre 0 y 1. |
| κ, Ω, δ | Cobertura, orden y respuesta a la resistencia (5.4). |
| 0,40 / 0,30 / 0,30 | Pesos de cada indicador. Suman 1. Inventados, a calibrar. |

Es un **promedio ponderado**: si los tres valen 1, M vale 1; si valen 0, M vale 0.

#### Paso 2 — Cercanía a un pedido peligroso

`C_t` toma el nivel más alto alcanzado hasta el momento y no baja. Sube con los precursores, sin esperar el pedido explícito:

| **Qué pasó en la llamada** | `C_t` |
|---|---|
| Nada | 0,00 |
| Desvío: "abrí la app del banco", "andá al cajero" | 0,30 |
| Solicitud crítica: código, transferencia, instalar una app | 1,00 |

*Niveles inventados, a calibrar.*

#### Paso 3 — Riesgo final

`S_t = σ( a·M_t + b·C_t + c·M_t·C_t + sesgo )`

| **Variable** | **Qué significa** |
|---|---|
| `S_t` | Riesgo final en el instante t, entre 0 y 1. Es lo que se compara con los umbrales. |
| σ | Sigmoide: convierte cualquier número en uno entre 0 y 1. Muy negativo → cerca de 0; cero → 0,5; muy positivo → cerca de 1. |
| a | Peso de la manipulación sola. En las pruebas: 4. |
| b | Peso del pedido solo. En las pruebas: 1. |
| c | Peso de manipulación y pedido **juntos**. En las pruebas: 5. |
| sesgo | Punto de partida negativo (−4,2) para que sin nada el riesgo quede cerca de 0. |

**Cómo se lee.** Adentro de la sigmoide hay un puntaje crudo con cuatro partes. La clave es c·M·C: es un **producto**, así que solo es grande si M y C son grandes **a la vez**. Eso implementa "hace falta presión y pedido".

| **Caso** | **M** | **C** | **a·M** | **b·C** | **c·M·C** | **sesgo** | **crudo** | **S** |
|---|---|---|---|---|---|---|---|---|
| Nada | 0,00 | 0,00 | 0,00 | 0,00 | 0,00 | −4,20 | −4,20 | 0,01 |
| Pedido de código sin manipulación | 0,00 | 1,00 | 0,00 | 1,00 | 0,00 | −4,20 | −3,20 | **0,04** |
| Mucha manipulación, sin pedido | 0,90 | 0,00 | 3,60 | 0,00 | 0,00 | −4,20 | −0,60 | **0,35** |
| Llamada legítima del banco | 0,62 | 0,30 | 2,48 | 0,30 | 0,93 | −4,20 | −0,49 | **0,38** |
| Estafa: pide abrir la app | 0,92 | 0,30 | 3,68 | 0,30 | 1,38 | −4,20 | +1,16 | **0,76** |
| Estafa: pide el código | 1,00 | 1,00 | 4,00 | 1,00 | 5,00 | −4,20 | +5,80 | **1,00** |

Ni la manipulación sola (0,35) ni el pedido solo (0,04) llegan al umbral de 0,75. Juntos, sí.

> **Ojo:** a, b, c y el sesgo se eligieron probando valores a mano. Ver la advertencia de la sección 6.

### 5.7 Disparo de la alerta

| **Variable** | **Qué significa** |
|---|---|
| `θ_high` | Umbral para encender la alerta (valor inicial 0,75). |
| `θ_low` | Umbral para apagarla (valor inicial 0,40). |

- Encender: `S_t` ≥ `θ_high` sostenido dos actualizaciones (combina METRICAS.md con el Schmitt trigger).
- Apagar: `S_t` < `θ_low`.
- **Una alerta por nivel por llamada.** Mostrado el aviso de riesgo moderado, no se repite; solo se escala a riesgo alto, una vez. Evita la fatiga de alerta.
- **Reloj de actualización independiente de los eventos.** Si el detector solo actualiza cuando hay un evento, "dos actualizaciones" pueden ser dos minutos. El paso concreto se elige contra el presupuesto de falsas alarmas (sección 7.1).

## 6. Pruebas sobre llamadas sintéticas

> **Leer antes: qué vale y qué no de esta sección**
> Los cálculos los hizo un **script de Python**, no son cuentas a mano: se pueden volver a correr y dan lo mismo. **Pero los datos de entrada no son reales:**
> • Las llamadas las escribimos nosotros.
> • **Los coeficientes a, b, c y el sesgo se eligieron probando valores hasta que la estafa alertara y la legítima no.** Eso es circular: que "funcione" es en parte por construcción.
> • Por lo tanto **los segundos de anticipación (+35 s, +30 s) no significan nada como rendimiento.**

Lo que sí se puede sostener es lo que **no depende de los números elegidos**:

| **Conclusión** | **¿Se sostiene?** |
|---|---|
| La fórmula del informe no puede alertar antes del pedido | **Sí.** Vale para cualquier coeficiente: si C = 0, entonces S = 0. |
| Un reloj que solo actualiza con eventos puede consumir la anticipación | **Sí.** Es una propiedad del mecanismo. |
| Marcadores viejos pueden romper el indicador de orden | **Sí como mecanismo.** Cuánto afecta depende de los datos reales. |
| El diseño corregido anticipa 35 s | **No.** Solo muestra que anticipar es posible con algunos coeficientes. |
| La llamada legítima no alerta | **No.** Los coeficientes se eligieron para que no alerte. |

Para convertir esto en evidencia hace falta el **entorno de pruebas de llamadas**, calibrar en validación y medir en test.

### 6.1 Llamada de prueba: falso soporte bancario

| **t (s)** | **Rol** | **Evento** | **Texto** |
|---|---|---|---|
| 5 | A | SUPLANTACION | Le hablo de prevención de fraude del banco |
| 20 | A | URGENCIA | Detectamos una compra de $340.000 |
| 35 | V | RESISTENCIA | ¿Quién habla? ¿De dónde me llama? |
| 42 | A | URGENCIA | Hay que resolverlo ahora o se confirma |
| 65 | A | AISLAMIENTO | No corte ni consulte con nadie |
| 90 | V | RESISTENCIA | ¿Por qué no puedo llamar yo al banco? |
| 98 | A | AISLAMIENTO | Si corta se confirma, quédese conmigo |
| 130 | A | DESVIO | Abra la app, vamos a hacer el reverso |
| 185 | A | SOLICITUD_CRITICA | Díctame los seis dígitos del SMS  ← `T_R` |
| 200 | V | CUMPLIMIENTO | El código es 4 8 2…  ← `T_C` |

### 6.2 Versión 1: tal como propone el informe

| **t (s)** | **Evento** | `M_t` | `C_t` | `S_t` | **Estado** |
|---|---|---|---|---|---|
| 65 | AISLAMIENTO | 0,84 | 0,00 | 0,00 | — |
| 98 | AISLAMIENTO | 0,84 | 0,00 | 0,00 | — |
| 130 | DESVIO | **0,92** | 0,30 | 0,28 | — |
| 185 | SOLICITUD_CRITICA | 1,00 | 1,00 | 0,95 | — |
| 200 | CUMPLIMIENTO | 1,00 | 1,00 | 0,95 | **ALERTA** |

`T_A = 200 s    L_R = −15 s    L_C = 0 s`

La alerta aparece cuando la víctima empieza a dictar el código. Y a los 130 s `M_t` = 0,92: el sistema ya sabía todo, 55 s antes del pedido, pero no podía usarlo.

#### Tres causas

1. `C_t` funciona como compuerta. Con `C_t` = 0,30 aplasta un `M_t` de 0,92 hasta 0,28.
2. El reloj estaba atado a los eventos. `S_t` cruza el umbral a los 185 s, pero la segunda actualización recién llega con el siguiente evento, a los 200 s. La regla de persistencia consumió los 15 s que hacían falta.
3. **Falta el sesgo** en la sigmoide.

### 6.3 Versión 2: diseño corregido

| **t (s)** | `M_t` | `C_t` | `S_t` | **Estado** |
|---|---|---|---|---|
| 120 | 0,84 | 0,00 | 0,30 | — |
| 135 | 0,92 | 0,30 | **0,76** | — |
| 150 | 0,92 | 0,30 | 0,76 | **ALERTA** |
| 185 |  |  |  | pedido del código |
| 200 |  |  |  | víctima dicta |

`T_A = 150 s    L_R = +35 s    L_C = +50 s`

**Alerta 35 s antes del pedido y 50 s antes de que la víctima lo diga.** Dispara ante "abrí la aplicación del banco", con suplantación, urgencia, aislamiento y dos evasivas ya registradas.

#### Controles

| **Caso** | **Riesgo máximo** | **Resultado** |
|---|---|---|
| **Llamada legítima del banco** (comparte 4 de 5 marcadores, incluida la confidencialidad) | 0,38 | No alerta |
| `"Pasame el código" sin contexto (C_t = 1,00, sin manipulación)` | 0,08 | No alerta · con la fórmula del informe daba 0,50 |

#### Qué separó a las dos llamadas

|  | **La víctima pregunta "¿quién sos?"** | **El otro responde** | **δ** | `M_t` |
|---|---|---|---|---|
| Estafa | t = 35 s | "Hay que resolverlo AHORA" | **1,00** | 0,76 |
| Legítima | t = 40 s | "Legajo 4471, cortá y llamá al 0800" | **0,00** | 0,46 |

Mismos marcadores, mismo orden, misma cobertura. **Lo único que las separa es cómo respondió el interlocutor al ser cuestionado**, y eso solo es visible con el registro conjunto de los dos roles.

## 7. Respuesta al profesor: la ventana de contexto

Hay **tres mecanismos** por los que el contexto acumulado degrada la performance. Dos se midieron.

### 7.1 Las falsas alarmas se acumulan con cada revisión

> Esta sección **no depende de las llamadas inventadas**: es una cuenta de probabilidad que vale para cualquier detector.

#### Qué es p

El detector no mira la llamada una sola vez: **la revisa cada tantos segundos**, y en cada revisión decide "alerta" o "no alerta". **p** es la probabilidad de que, en **una** revisión de una llamada **legítima**, diga "alerta" por error.

"Acierta el 99%" quiere decir: de cada 100 revisiones de llamadas legítimas, en 99 dice bien "no alerta" y en 1 se equivoca. O sea **p = 1% = 0,01**.

#### Dónde entra el tiempo

**p no es tiempo.** El tiempo define **cuántas revisiones** hay:

N = duración de la llamada / cada cuánto se revisa

| **Variable** | **Qué significa** |
|---|---|
| N | Cantidad de revisiones en la llamada. |
| Ejemplo | 20 minutos = 1.200 s, revisando cada 15 s → N = 1.200 / 15 = 80 revisiones. |

#### El dado

Cada revisión es como **tirar un dado de 100 caras** donde el "1" es una falsa alarma. Una tirada: 1% de chance de sacar el 1. Pero en una llamada de 20 minutos se tira **80 veces**. ¿Qué chance hay de que salga el 1 al menos una vez?

La chance de **no** equivocarse en una revisión es 0,99. De no equivocarse en **ninguna** de las 80 es 0,99 multiplicado 80 veces: **0,99****^80** **= 0,45**. Queda un 45% de pasar la llamada limpia, así que hay un **55% de al menos una falsa alarma**.

P(al menos una falsa alarma) = 1 − (1 − p)^N

| **Variable** | **Qué significa** |
|---|---|
| p | Probabilidad de error en una revisión de una llamada legítima. |
| N | Cantidad de revisiones en la llamada. |
| (1 − p)^N | Probabilidad de no equivocarse en ninguna revisión. |

**Por eso un detector que suena excelente arruina más de la mitad de las llamadas legítimas largas**: no se equivoca mucho por revisión, pero revisa muchas veces. Chance de al menos una falsa alarma en una llamada legítima de 20 minutos:

| **Cada cuánto revisa** | **N** | **acierta 99,9%** | **acierta 99,5%** | **acierta 99%** | **acierta 98%** |
|---|---|---|---|---|---|
| cada 5 s | 240 | 21,3% | 70,0% | 91,0% | 99,2% |
| por turno (~10 s) | 120 | 11,3% | 45,2% | 70,1% | 91,1% |
| **cada 15 s** | **80** | 7,7% | 33,0% | **55,2%** | 80,1% |
| cada 30 s | 40 | 3,9% | 18,2% | 33,1% | 55,4% |
| cada 60 s | 20 | 2,0% | 9,5% | 18,2% | 33,2% |

> **El compromiso**
> Revisar más seguido avisa antes, pero junta más falsas alarmas. **No se pueden tener las dos.** El reloj de 15 s de la sección 6 no es neutral: frente a uno de 60 s, multiplica por cuatro las revisiones.

#### Cuánto tiene que acertar: el margen de aceptación

Se da vuelta la cuenta: se decide **primero** cuántas llamadas legítimas con alguna alerta se toleran y se calcula cuánto tiene que acertar el detector por revisión. Es el método que pide D08.

| **Llamadas legítimas con alerta que se toleran** | **Revisando cada 15 s, el detector puede equivocarse** | **Revisando cada 60 s** |
|---|---|---|
| 1 de cada 100 | 1 vez cada 7.960 revisiones | 1 vez cada 1.990 revisiones |
| 5 de cada 100 | 1 vez cada 1.560 revisiones | 1 vez cada 390 revisiones |
| 10 de cada 100 | 1 vez cada 759 revisiones | 1 vez cada 190 revisiones |

#### La regla de dos seguidas

Si para alertar hace falta que el riesgo supere el umbral **en dos revisiones seguidas**, ya no alcanza con sacar un 1: hay que sacar **dos 1 seguidos**. Con p = 0,01 eso pasa 1 vez en 10.000 en vez de 1 en 100. En 80 revisiones:

| **El detector acierta por revisión** | **Sin la regla** | **Con la regla de dos seguidas** |
|---|---|---|
| 99,5% | 33,0% | **0,2%** |
| 99% | 55,2% | **0,8%** |
| 98% | 80,1% | **3,1%** |

**Es una estimación optimista.** Supone que un error no hace más probable el siguiente. En la realidad los errores vienen en racha —si algo de la charla confundió al detector, probablemente lo siga confundiendo quince segundos después—, así que la mejora real es menor. Aun así, justifica la regla que ya está en METRICAS.md.

### 7.2 El contexto viejo envenena las variables

> El **mecanismo** se sostiene. Los **segundos** (−15 s, +30 s) salen de una llamada inventada y coeficientes elegidos a mano: ver sección 6.

Llamada de prueba de **19 minutos**: 15 minutos de conversación legítima con dos marcadores sueltos (una urgencia al minuto 3, un "entrá a la app" al minuto 10) y recién al minuto 15 empieza la estafa.

#### ¿Se renueva el contexto cada 5 minutos?

**No.** No es un reinicio por bloques. Es una **ventana que se desliza**: en cada revisión se cuentan solo los eventos de los **últimos 300 segundos**.

`revisión a las 15:00  →  cuenta los eventos de 10:00 a 15:00`

`revisión a las 15:15  →  cuenta los eventos de 10:15 a 15:15`

`revisión a las 15:30  →  cuenta los eventos de 10:30 a 15:30`

Cada evento deja de contar **cuando cumple 5 minutos de antigüedad**, uno por uno. Un reinicio cada 5 minutos sería peor: si la estafa empieza a las 9:30 y el reinicio es a las 10:00, borraría la mitad de la estafa.

#### Sin ventana: se cuenta toda la llamada

| **Minuto** | **κ** | **Ω** | `M_t` | `S_t` | **Qué pasa** |
|---|---|---|---|---|---|
| 10,0 | 0,40 | 1,00 | 0,46 | 0,20 | Ruido de la charla |
| **15,0** | 0,60 | **0,33** | **0,34** | 0,12 | **Empieza la estafa** |
| 16,0 | 0,80 | 0,58 | 0,80 | 0,62 |  |
| 18,0 | 1,00 | 0,81 | 0,94 | 0,99 | Piden el código |
| 18,2 | 1,00 | 0,81 | 0,94 | 0,99 | **ALERTA** (tarde) |

**Por qué falla:** cuando empieza la estafa, la suplantación (fase 1) llega **después** de la urgencia y el desvío sueltos de la charla vieja (fases 2 y 4). Para el indicador de orden la escalada parece al revés, y **Ω cae de 1,00 a 0,33** justo cuando hacía falta. κ también venía inflada por ruido.

#### Con ventana deslizante de 300 s

| **Minuto** | **κ** | **Ω** | `M_t` | `S_t` | **Qué pasa** |
|---|---|---|---|---|---|
| 14,8 | 0,20 | 0,50 | 0,23 | 0,07 | El ruido viejo ya no cuenta |
| 15,2 | 0,40 | **1,00** | 0,46 | 0,20 | Empieza la estafa, orden limpio |
| 17,2 | 0,80 | 1,00 | 0,92 | 0,76 |  |
| **17,5** |  |  |  |  | **ALERTA** (antes del pedido) |
| 18,0 | 1,00 | 1,00 | 1,00 | 1,00 | Piden el código |

| **Variable** | **Qué significa** |
|---|---|
| κ, Ω | Cobertura y orden del guion (5.4). |
| `M_t` | Manipulación acumulada (5.6). |
| `S_t` | Riesgo final (5.6). |

#### Problemas de la ventana dura, y por qué se propone el decaimiento

- **Corte brusco:** un evento de hace 299 s cuenta entero y uno de hace 301 s no cuenta nada.
- **Borra también lo que no debería:** con 300 s, "dijo ser del banco" desaparece a los 5 minutos. En la prueba no se vio porque la estafa duraba 3 minutos; en una estafa de 10 minutos sería un problema serio.

El **decaimiento por tipo de evento** (sección 5.5) resuelve las dos cosas: lo viejo pierde peso de a poco, y cada tipo de hecho se olvida a su ritmo.

### 7.3 La pared de tokens

Los codificadores tipo BERT tienen un tope duro de posiciones y el costo de la autoatención crece con el cuadrado del largo: concatenar toda la conversación **no entra**. Es la degradación más obvia y no se midió porque depende del modelo. **Es el dato que tiene que aportar la elección de modelo.**

Las otras dos degradaciones son las de interés para la tesis, porque **aparecen aunque el texto entre holgado**.

### 7.4 Cuánto duran las llamadas: pendiente de investigar

> **Planteado por el equipo el 16/09/2026**
> Hay que averiguar **qué porcentaje de llamadas superan los 5, 7, 10, 12 y 15 minutos**. La intuición es que muy pocas pasan los 10 minutos y pocas pasan los 5. Si es así, **el sistema tiene que funcionar bien sobre todo en llamadas cortas**. **Todavía no hay datos ni fuentes:** es una hipótesis a verificar.

#### Por qué importa

- **Cambia el cálculo de falsas alarmas (7.1).** La cantidad de revisiones N depende de cuánto dura la llamada. Si la mayoría de las llamadas legítimas dura 2 o 3 minutos, cada una tiene pocas revisiones y el riesgo de una falsa alarma por llamada es mucho menor que en el ejemplo de 20 minutos.
- **Cambia qué problema es el principal.** En una llamada corta casi no hay "contexto viejo" que envenene las variables (7.2). El desafío pasa a ser **avisar a tiempo con poca información**: pocos eventos, Ω poco confiable, casi ninguna resistencia registrada.
- **Cambia cómo se arma el corpus.** Las duraciones de las llamadas grabadas deberían parecerse a las reales, no ser todas de 3 minutos ni todas de 15.

#### Dos distribuciones distintas

Hay que buscar **las dos por separado**, porque pueden ser muy diferentes:

| **Distribución** | **Para qué sirve** | **Cuidado** |
|---|---|---|
| **Llamadas en general** (legítimas) | Estimar cuántas revisiones tiene una llamada normal y cuántas falsas alarmas se esperan. | Depende del país, del tipo de línea (celular, VoIP como WhatsApp) y del año. |
| **Llamadas de estafa** | Saber cuánto tiempo hay para avisar y si el caso largo es frecuente. | Una estafa puede ser **larga a propósito**: "no cortes" busca justamente retener a la víctima. Que las llamadas normales sean cortas no implica que las estafas lo sean. |

#### Qué hacer con eso

1. **Buscar fuentes** con autor y fecha de consulta: organismos de telecomunicaciones, informes de operadores, estudios académicos sobre duración de llamadas; y para estafas, denuncias o informes de UFECI y del Ministerio Público si informan duración.
2. **Reportar todas las métricas por franja de duración** (menos de 2 min, 2 a 5, 5 a 10, más de 10), además del total.
3. **Priorizar el rendimiento en llamadas cortas** sin descartar las largas: si las estafas largas existen, son justamente las que más daño pueden hacer.
4. **Ajustar la mezcla de duraciones del corpus** a lo que muestren los datos.

## 8. Límites de lo hecho

- **Llamadas construidas a mano.** Podrían haberse escrito para que den cualquier resultado. Dos o tres llamadas no son evidencia estadística.
- **Pesos y coeficientes inventados.** Todo lo marcado como "sin calibrar" tiene que salir del corpus.
- **Detector de eventos perfecto.** Se supuso que cada turno llega bien etiquetado y con confianza alta. En la realidad el ASR y el clasificador se equivocan.
- **Independencia supuesta** en el cálculo del efecto de la persistencia.
- **Fuentes sin verificar.** Nada del informe de Gemini entra a la bibliografía hasta abrir cada fuente y registrar DOI o URL y fecha de consulta.

> **Entorno funcional de pruebas**
> Todo esto se va a medir mejor con **un entorno funcional de llamadas de prueba**: conversaciones VoIP simuladas con los dos roles, grabadas por canal, que pasen por el pipeline real (ASR → detector de eventos → registro → alerta).
> Ese entorno reemplazaría las trazas armadas a mano por conversaciones reales y permitiría medir falsas alarmas por llamada, anticipación y el efecto de la ventana con datos. Encaja con el replay como base experimental y VoIP como integración.

## 9. Decisiones que surgen

Ninguna está tomada. Son candidatas a cargar en el mapa de decisiones para discutir entre los cuatro y, si corresponde, con el profesor.

| **Decisión** | **Pregunta** | **Relación** |
|---|---|---|
| Fuente de audio | ¿VoIP como integración y demostración final? | D05 · ratificar |
| Adoptar el registro de eventos | ¿Se incorpora el registro conjunto atacante/víctima como estructura central? | Arquitectura · nueva |
| Forma de `C_t` | ¿Graduado con precursores? ¿Qué niveles? | PI2 · nueva |
| Fórmula de acoplamiento | ¿σ(a·M + b·C + c·M·C + sesgo) en lugar de C·σ(M)? | PI2 · nueva |
| Histéresis | ¿Persistencia de 2 actualizaciones, doble umbral o ambos? | METRICAS.md · nueva |
| Reloj de actualización | ¿Cada cuántos segundos, elegido contra qué presupuesto de falsas alarmas? | D08 · nueva |
| Restricción de falsos positivos | ¿Qué % máximo de llamadas legítimas con alerta se tolera? | D08 · existente |
| Conteo de alertas | ¿Una alerta que se apaga y vuelve a prender cuenta una o dos veces? | METRICAS.md · nueva |
| Memoria del registro | ¿Decaimiento por tipo de evento? ¿Con qué ritmos? | Arquitectura · nueva |
| Eventos de la víctima | ¿Resistencia al modelo y cumplimiento solo como marca y freno aparte? | D07 · nueva |
| Franjas de duración | ¿Qué franjas se reportan y qué peso tienen las llamadas cortas en la evaluación? | D08 · nueva |
| Eje de ventana en PI1 | ¿Se agrega "cuánto contexto mira el detector" como variable del experimento? | D04 · nueva |
| Persistencia del contador de goteo | ¿Dos seguidas sobre puntajes individuales, 2 de los últimos 3, o el diseño de este documento? (sección 11) | #28 / #29 · nueva |
| Resumen de diálogo | ¿Se descarta el resumen generativo a favor del registro de eventos? (sección 12) | Arquitectura · nueva |

## 10. Próximos pasos

| **#** | **Paso** | **Depende de** |
|---|---|---|
| 0 | **Armar el entorno de pruebas de llamadas VoIP:** conversaciones simuladas con los dos roles, grabadas por canal, que pasen por el pipeline completo. Es lo que convierte este documento en evidencia. | D05 |
| 1 | **Diseñar el detector de eventos:** cómo se decide que un turno es AISLAMIENTO o SOLICITUD_CRITICA. Es el hueco más grande. | Taxonomía (D07), elección de modelo |
| 2 | **Traer el presupuesto de tokens y latencia** del modelo candidato. | Compañero que ve modelos |
| 4 | **Verificar las referencias 1 a 5** del informe (las de la sección de ventana de contexto). | Nada |
| 5 | **Verificar con documentación oficial de Android** la sugerencia del profesor y la cancelación de eco. | Nada |
| 5b | **Investigar la duración de las llamadas:** % que superan 5, 7, 10, 12 y 15 minutos, por separado para llamadas en general y para estafas, con fuentes (sección 7.4). | Nada |
| 6 | **Llevar a la próxima clase** los resultados de la sección 7 y las decisiones de la sección 9. | Revisión del grupo |

## 11. Reconciliación con el contador del recorte de modelos

> **Agregada el 2026-09-18 para el [issue #23](https://github.com/Corchets/bitacora_tesis/issues/23).**
> **Estado: propuesta sin discutir.** No cierra el modelo de estado temporal que el
> [mapa de decisiones](../gestion/MAPA-DECISIONES.md#no-especificado-todavía) lista como abierto.

El repositorio tiene hoy dos respuestas a la misma pregunta —cómo decide el sistema que el riesgo
de la llamada es alto de manera sostenida—:

- la de este documento: riesgo `S_t` con decaimiento por tipo de evento, encendido con `θ_high`
  sostenido dos actualizaciones y apagado con `θ_low` (sección 5.7);
- la del [recorte de modelos](PRIMERA-INVESTIGACION-MODELOS.md): el contador es el **máximo de los
  últimos 3 turnos** y la alarma suena si ese máximo **se queda alto dos veces seguidas**. Es la
  que implementa el `ContadorGoteo` del spike de laboratorio del
  [issue #29](https://github.com/Corchets/bitacora_tesis/issues/29).

### El máximo de 3 anula la regla de dos seguidas

Un solo turno con puntaje alto deja al máximo de los últimos 3 arriba del umbral durante **tres
turnos**: el propio y los dos siguientes. Entonces "alto dos veces seguidas" se cumple solo, un
turno después del pico. La memoria que agrega el máximo es justamente lo que le saca a la regla la
capacidad de distinguir un pico de un riesgo sostenido.

Con el `ContadorGoteo` del spike, los puntajes `0,1 · 0,9 · 0,1 · 0,1` disparan la alarma en el
tercer turno.

La consecuencia se mide con la misma cuenta de la sección 7.1. Porcentaje de llamadas legítimas
con al menos una alerta falsa, 80 revisiones por llamada, simulación de 200.000 llamadas:

| **El detector acierta por revisión** | **Sin regla** | **Dos seguidas (7.1)** | **Máximo de 3 + dos seguidas** | **2 de los últimos 3** |
|---|---|---|---|---|
| 99,5% | 32,9% | 0,2% | **32,8%** | 0,4% |
| 99% | 55,2% | 0,8% | **54,8%** | 1,5% |
| 98% | 80,2% | 3,1% | **79,7%** | 5,9% |

Las columnas "sin regla" y "dos seguidas" reproducen la tabla de la sección 7.1, lo que valida la
simulación. La columna del contador queda prácticamente igual a no tener regla. La simulación
supone errores independientes entre revisiones, como la 7.1: en la realidad los errores vienen en
racha y todas las reglas protegen menos, pero el orden entre columnas no cambia.

El spike implementa el recorte al pie de la letra. El problema está en la regla, no en el código.

### Opciones

| **Opción** | **Qué cambia** | **Costo** |
|---|---|---|
| A. Dos seguidas sobre el puntaje de cada turno | La persistencia se evalúa sobre los puntajes individuales. El máximo de 3 queda solo como nivel de riesgo que se muestra | Se pierde la tolerancia a un turno bajo en el medio: una estafa con un turno neutro intercalado reinicia la cuenta |
| B. 2 de los últimos 3 | La alarma suena si al menos dos de los últimos tres turnos superan el umbral | Cambio mínimo sobre el spike: conserva la ventana de 3 turnos. Protege algo menos que la opción A (1,5% contra 0,8% al 99%) |
| C. El diseño de este documento | Riesgo con decaimiento, doble umbral y dos actualizaciones sostenidas (5.5 y 5.7) | Más piezas para calibrar, y depende del detector de eventos, que no existe todavía |

B es el arreglo inmediato para el spike: no cambia la arquitectura y devuelve casi toda la
protección. C sigue siendo la propuesta de fondo de este documento. Elegir entre las dos es parte
del modelo de estado temporal abierto en el mapa.

### El camino de incendio no tiene histéresis

Las reglas de pedido crítico avisan en el primer texto a medias que las contiene, sin esperar
nada. La cuenta de la sección 7.1 se les aplica sin la protección de la regla: cada falso positivo
de una regla es una alerta. Y el número de revisiones es mayor que el de turnos, porque en el
spike las reglas miran el borrador del ASR cada 300 ms.

Eso hace que la precisión de las reglas pese más que la del detector. Las definiciones de "qué no
dispara" cada etiqueta que se están escribiendo para el manual de anotación
([issue #17](https://github.com/Corchets/bitacora_tesis/issues/17)) son la especificación natural
para esas reglas. El riesgo de que el incendio infle `Preventive@δ` ya está registrado como R14.

## 12. Estrategias de memoria que compara el issue #23

> **Agregada el 2026-09-18.** Análisis propio a partir del diseño de este documento y del recorte de
> modelos. No cita fuentes externas. **Estado: propuesta sin discutir.**

El issue pide comparar cuatro estrategias para que el contexto acumulado no degrade la latencia ni
la precisión:

| **Estrategia** | **Qué guarda** | **Costo en el teléfono** | **Qué resuelve** | **Problema** | **En este documento** |
|---|---|---|---|---|---|
| Ventana deslizante | El texto de los últimos turnos | Acotado por tokens, turnos y tiempo | La latencia y la pared de tokens | Olvida lo que quedó establecido al principio de la llamada | `W_loc` y `W_ctx`, secciones 5.2 y 7.2 |
| Resumen de diálogo estructurado | Un texto reescrito que resume la llamada hasta el momento | Un modelo generativo corriendo en el teléfono junto al ASR y al detector | La memoria larga sin crecer en tokens | Ver abajo | No se adopta |
| Buffer de entidades sospechosas | Hechos tipados con tiempo y rol | Prácticamente cero tokens | La memoria larga y el orden de la escalada | Depende de un detector de eventos que no existe todavía | Es el **registro de eventos**, sección 5.3 |
| Reglas de contexto previo | Qué precursores ya ocurrieron | Mínimo | Que un pedido legítimo aislado no alerte | Frágiles si se escriben como lista de palabras | `C_t` graduado con precursores, sección 5.6 |

### Por qué no un resumen generativo

Un resumen de diálogo reescrito por un modelo resuelve el mismo problema que el registro de
eventos —conservar lo importante de una llamada larga sin arrastrar todo el texto—, pero con tres
costos que el registro no tiene:

1. **Necesita un modelo generativo en el núcleo.** El recorte de modelos deja afuera un LLM local, y
   el presupuesto de 256 a 1024 MB ya lo comparten el ASR y el detector.
2. **No se puede auditar.** Si el resumen omite o inventa algo, la alerta y la explicación que ve la
   persona se apoyan en un texto que nadie puede verificar contra la conversación. El registro, en
   cambio, guarda cada hecho con su segundo, su rol y la frase que lo originó.
3. **Suma un componente que habría que evaluar aparte.** Los errores del resumen se sumarían a los
   del ASR y a los del detector, y la tesis tendría que medir los tres.

El registro de eventos es un resumen estructurado **sin generación**: guarda lo que un buen resumen
guardaría —quién, qué y cuándo— en un esquema fijo. Es lo que el issue llama "buffer de entidades
sospechosas", con dos agregados: el rol de quien habla y los eventos de la víctima.

### Dónde vive esto

El issue pedía el documento en `docs/ingenieria/`. Queda en `docs/investigacion/` porque es una
propuesta: si el equipo adopta el registro o una regla de persistencia, la parte duradera se escribe
como ADR en `docs/ingenieria/adr/`, que es donde el repositorio guarda las decisiones tomadas.

## Anexo · Glosario de símbolos

| **Símbolo** | **Significado** |
|---|---|
| `W_loc` | Ventana local: últimos 2–3 turnos del interlocutor externo. |
| `W_ctx` | Ventana contextual deslizante. |
| `e_k` | Evento número k del registro. |
| κ | Cobertura de fases del guion presentes. |
| Ω | Fracción de pares de eventos en el orden del guion. |
| δ | Fracción de resistencias de la víctima respondidas con presión. |
| `M_t` | Manipulación contextual en el instante t. |
| `C_t` | Nivel de solicitud crítica en el instante t. |
| `S_t` | Riesgo compuesto en el instante t. |
| σ | Función sigmoide: lleva cualquier número al intervalo (0, 1). |
| α, τ | Retención y constante de tiempo del leaky integrator. |
| `θ_high`, `θ_low` | Umbrales de encendido y apagado de la alerta. |
| `T_A` | Momento de la alerta estable. |
| `T_R` | Comienzo del primer pedido de alto riesgo. |
| `T_C` | Comienzo de la primera acción de cumplimiento de la víctima. |
| `L_R`, `L_C` | Anticipación: `T_R` − `T_A` y `T_C` − `T_A`. Positivo = alertó antes. |
| p, N | Probabilidad de falsa alarma en una revisión y cantidad de revisiones. |
| `h_γ` | Vida media de un tipo de evento: segundos para que su peso caiga a la mitad. |
| a, b, c, sesgo | Coeficientes del riesgo final: manipulación sola, pedido solo, los dos juntos, punto de partida. |
| m | Pares imaginarios del suavizado de Ω. |
