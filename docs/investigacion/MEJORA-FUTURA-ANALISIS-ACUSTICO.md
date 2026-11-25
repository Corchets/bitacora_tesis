# Mejora futura: análisis acústico de la llamada

> **Estado: propuesta sin discutir.** Es trabajo futuro: no se implementó ni se midió nada de lo que sigue. El detector
> actual trabaja solo sobre la transcripción, y la decisión de sumar rasgos acústicos sigue abierta en
> [D11](../gestion/MAPA-DECISIONES.md#d11--análisis-lingüístico-o-también-acústico). Documenta una mejora futura y
> cómo se aplicaría; la tesis la resume en el [§11.4](../tesis/CAP-11-CONCLUSIONES.md#114-trabajo-futuro-acotado).
> Redactado el 2026-11-23.

## 1. La pregunta

¿Analizar cómo habla quien llama (`OTRA`) y cómo se reparten los tiempos de la conversación le da al detector
información que la transcripción no tiene?

**Objetivo.** Evaluar si los rasgos prosódicos de `OTRA` y los tiempos de interacción, medidos turno a turno a lo largo
de la llamada, permiten al detector avisar antes del primer pedido de alto riesgo (`T_R`,
[métricas](../evaluacion/METRICAS.md#1-marcas-temporales)) o avisar estafas que el texto solo no avisa, con un margen de
falsas alarmas fijado antes de evaluar. El piloto usa conversaciones recreadas por personas, en español argentino y con
los dos canales separados. Los métodos se comparan sobre las mismas llamadas y con la información disponible en cada
instante. El aviso se fecha cuando el sistema lo emite efectivamente (`T_A`).

**Por qué interesa.** Ninguno de los candidatos probados en
[H12](../hallazgos/H12-cambiar-el-prompt-mueve-el-corte-no-la-separacion.md) mejoró claramente la separación entre
estafas y legítimas reales: los que bajaron las falsas alarmas perdieron detección o avisos a tiempo. Eso no prueba
que el texto haya llegado a un techo, pero sugiere buscar información que el detector no tiene, en vez de otra forma de
pedirle lo mismo. La voz es información que el sistema ya captura y hoy descarta: un operador y un estafador pueden
decir lo mismo, y lo que cambia es cómo lo dicen y cómo llevan la conversación.

**Hipótesis.** En algunas estafas, la forma de hablar de quien llama y la manera en que lleva la conversación cambian
de un modo que el texto no registra, y esos cambios aportan información una vez considerado el texto. No pasa en todas:
hay estafadores tranquilos, llamadas legítimas insistentes y emergencias reales con voces agitadas. Por eso el piloto
incluye esos casos, para poner a prueba la hipótesis.

**Qué no se afirma.** No se anticipa una ganancia. Si el piloto da negativo, la conclusión defendible es acotada: estos
rasgos, en estas condiciones y con esta política de aviso, no mostraron un aporte medible. Eso también responde la
pregunta.

## 2. Qué se analiza

### 2.1. Dos fuentes de señal

- **La voz de `OTRA`.** Cómo suena cada turno: altura, intensidad, ritmo y pausas, comparados con cómo hablaba esa
  persona al comienzo de la llamada.
- **Los tiempos de la conversación.** Quién habla cuánto, cuánto tarda cada uno en contestar, cuándo hablan a la vez y
  cómo cambia el largo de los turnos de `PROTEGIDA`.

Las dos se calculan por turno y están disponibles recién cuando el turno termina y se procesa.

### 2.2. Patrones a observar

Son hipótesis sobre qué podría distinguir una estafa, no supuestos:

1. **Escalada.** Quien llama se agita, acelera o sube la intensidad a medida que avanza la llamada.
2. **Cambio de registro.** Empieza con la calma de un operador y pasa a la urgencia al acercarse al pedido.
3. **Reacción ante una duda.** Cuando `PROTEGIDA` duda o se niega («prefiero llamar al banco»), la respuesta de quien
   llama se endurece en vez de aflojar.
4. **Dominio de la conversación.** Quien llama habla mucho más, interrumpe, contesta enseguida, y los turnos de
   `PROTEGIDA` se acortan hasta quedar en «sí» y «ajá».

Ninguno es exclusivo de las estafas: un vendedor insistente puede escalar, un familiar en una emergencia habla agitado
desde el primer segundo, y un estafador profesional puede mantener la calma toda la llamada. El patrón 3 depende de un
hecho del texto (la duda); para saber si la voz agrega algo sobre ese hecho, la comparación incluye un control (§3.1).

### 2.3. Definiciones para el piloto

- **Referencia de la propia voz:** cada turno de `OTRA` se compara con sus turnos anteriores en la misma llamada. Hay
  que definir cuánta voz previa hace falta (en segundos) y qué pasa si falta: en ese caso no hay señal prosódica y
  decide el texto solo. La referencia puede fallar en llamadas cortas, cuando la presión empieza desde el saludo o
  cuando cambia la ganancia del micrófono.
- **Tiempos:** no todo solapamiento es una interrupción. Hay asentimientos («ajá»), eco y retrasos del canal. Se
  define qué cuenta como interrupción y se revisa a mano una muestra.
- **Duda u objeción** (para el patrón 3): un turno de `PROTEGIDA` que duda, se niega, pide verificar o posterga. Los
  ejemplos y los casos dudosos se fijan en una guía de anotación antes de grabar, y se anotan a mano en el piloto.
- **Ventana útil:** lo que aparece antes de `T_R` sirve para anticipar el aviso; lo que aparece después puede aportar a
  la detección, pero ya no adelanta nada. Se informan por separado. `T_R` marca el inicio del pedido, aunque caiga
  dentro de un turno, así que un turno puede empezar antes de `T_R` y terminar después: sus rasgos solo contribuyen
  cuando están disponibles, y el aviso se fecha entonces.

### 2.4. Rasgos

| Rasgo | Qué es | Resistencia al canal telefónico |
| --- | --- | --- |
| Altura ($F_0$) relativa | Nivel y rango de la altura de la voz frente a la referencia | Por verificar. En voz por VoIP, $F_0$ estuvo entre las medidas más estables (Xu et al., 2024) |
| Intensidad relativa | Volumen frente a la referencia | Por verificar. Depende de la ganancia y del control automático del canal |
| Ritmo | Tasa de regiones sonoras por segundo. Es una aproximación, no un conteo de sílabas | Por verificar |
| Pausas | Proporción de silencio dentro del turno. eGeMAPS da la duración de las regiones no sonoras; la proporción se define y se calcula aparte | Por verificar |
| Proporción de habla | Qué parte del tiempo habla cada canal hasta el momento | Por verificar |
| Demora de respuesta | Tiempo entre el fin de un turno y el inicio del siguiente | Por verificar. Le suma el retraso del canal |
| Solapamiento | Habla simultánea de los dos canales, según la definición de §2.3 | Por verificar. El eco puede simular solapamientos |
| Largo de los turnos de `PROTEGIDA` | Duración de cada turno frente a sus turnos anteriores | Por verificar |

Altura, intensidad y ritmo salen del conjunto eGeMAPS (Eyben et al., 2016) con openSMILE; las pausas, de las regiones
no sonoras con un cálculo propio; el resto, de la actividad de voz de cada canal. Ninguno de estos rasgos indica estafa
por sí mismo: también cambian por el contenido de lo que se dice, el ruido, el canal y la dinámica normal de una
conversación. Qué dirección se espera en una estafa es parte de lo que el piloto tiene que observar, no un supuesto.

### 2.5. De dónde sale cada cosa

```mermaid
flowchart LR
    C["Captura por canal<br/>(PROTEGIDA / OTRA)"] --> S["Silero: actividad de voz<br/>por bloque, en cada canal"]
    S --> T["Tiempos de la<br/>conversación"]
    S --> P["Parakeet: texto"] --> G["Gemma 4 E2B: riesgo"]
    C --> O["openSMILE sobre el audio<br/>de OTRA: rasgos prosódicos"]
    T --> R["Regla de combinación"]
    O --> R
    G --> R
    R --> AV["Aviso, fechado al emitirse"]
```

La atribución de cada turno a una persona viene de la captura por canal, no de Silero. Por eso el canal objetivo (la
forma real de capturar la llamada) se prueba desde el piloto.

## 3. La comparación

### 3.1. Métodos

Todos sobre los mismos prefijos de conversación y con la información disponible en cada instante:

| Método | Qué ve | Qué aísla |
| --- | --- | --- |
| 0. Texto actual | La configuración congelada ([ADR 0002](../ingenieria/adr/0002-detector-gemma4-e2b-solo-con-prompt-c-premisa.md) y [ADR 0008](../ingenieria/adr/0008-prompt-del-detector-c-consejos.md)) | La base |
| 1. Texto con tiempos | 0, más los tiempos de la conversación | Si los tiempos suman sobre el texto |
| 2. Texto con tiempos y voz | 1, más los rasgos prosódicos de `OTRA` | Si la voz suma sobre todo lo anterior |
| Control. Texto con la duda marcada | 0, más la marca de que `PROTEGIDA` dudó u objetó | Si para el patrón 3 alcanza con señalar la duda, sin escuchar la respuesta |

Los métodos comparten la misma transcripción incremental, el mismo calendario de consultas y una única ejecución del
detector base. Cada método conserva los disparos del anterior y puede emitir un aviso adicional con la señal que
incorpora. El aviso base sale sin esperar el cálculo adicional. Los tiempos y los rasgos de un turno entran al cerrarse
el turno y terminar su cálculo. Si faltan rasgos prosódicos, el método 2 conserva la decisión del método 1. Compartir
la ejecución importa: la misma configuración, corrida de otro modo, pasó de 37 a 43 avisos antes del pedido
([H13](../hallazgos/H13-la-misma-configuracion-corrida-de-otro-modo.md)).

En el piloto las dudas se anotan a mano. Si el control resulta necesario en el teléfono, aparte se mide cuánto se
pierde cuando hay que detectarlas automáticamente.

### 3.2. La regla de combinación del piloto

El riesgo que escribe Gemma no es un puntaje continuo ([H04](../hallazgos/H04-riesgo-escrito-no-es-puntaje.md)): se
concentra en pocos valores. En desarrollo, con `c-premisa`, 57 de 66 avisos salieron de exactamente 0,3
([ADR 0002](../ingenieria/adr/0002-detector-gemma4-e2b-solo-con-prompt-c-premisa.md),
[corrida de sensibilidad](../../experiments/slm-directo/corridas/2026-11-10_sensibilidad-c/analisis.md)). Una
regresión logística común sobre ese puntaje tampoco garantiza conservar la decisión del texto. Para el piloto conviene
una regla explícita:

- **Conserva los avisos existentes.** Cada llamada que el texto solo avisa sigue avisando, en el mismo turno o antes.
- **Puede agregar o adelantar avisos** cuando los tiempos o la voz cumplen una condición escrita antes de evaluar.
- **Vuelve al texto solo cuando falta señal:** sin voz previa suficiente o con el canal degradado.

Con esta regla las falsas alarmas quedan iguales o aumentan; no pueden bajar. «Avisar antes con las mismas falsas
alarmas» es un resultado que hay que demostrar, no una propiedad de la regla. Por eso se miden las dos cosas: cuántos
avisos agrega y cuánto los adelanta, y cuántos de los agregados caen en legítimas. Usar la voz para bajar falsas
alarmas, por ejemplo subiendo el umbral común, sería otro experimento, porque puede eliminar avisos que hoy sí salen.

Qué tan fuerte es el aviso (suave o fuerte) es otra pregunta: si cambiar la intensidad mejora lo que hace la persona
frente a la alerta. Se responde con usuarios, no con este piloto.

### 3.3. Qué se informa

Cada método se compara con el anterior (1 contra 0, 2 contra 1, y el control contra 0), sobre llamadas pareadas y con
denominadores explícitos:

- cuántas estafas pasan a recibir un aviso antes de `T_R` (`T_A < T_R`);
- cuántas estafas que el método anterior no avisaba pasan a avisarse;
- cuánto cambia el margen `L_R` en las estafas que ya avisaban con los dos métodos;
- cuántas legítimas reciben un aviso nuevo, con un horizonte común;
- la incertidumbre de cada cifra, teniendo en cuenta que las llamadas de una misma persona o familia de guiones no son
  independientes.

Además:

- Todo separado por tipo de llamada (§4.1). Un método que mejora el total pero empeora un tipo se informa así.
- Por llamada, un gráfico con el riesgo de cada método turno a turno, los rasgos de la voz y los tiempos, las dudas,
  `T_R` y `T_A`, y **cuándo estuvo disponible cada señal**: los rasgos de un turno llegan después de que el turno
  termina.
- Entre llamadas, comparaciones con un horizonte común (por ejemplo, hasta `T_R` o las primeras N consultas), no con el
  máximo de la llamada entera, que favorece a las más largas.

## 4. El piloto

### 4.1. Cómo grabar

- **Las dos clases recreadas, en las mismas condiciones.** «Voz humana» y «llamada real» son cosas distintas. Si las
  estafas se actúan y las legítimas son naturales, el modelo puede aprender la actuación aunque se use el mismo
  micrófono. En el piloto, estafas y legítimas se recrean por igual; la validación con llamadas naturales va después,
  por separado.
- **Participantes en las dos clases** cuando se pueda, para que la voz de una persona no delate la clase.
- **Reserva agrupada por personas y por familias de guiones:** se asigna antes de ajustar la regla, y cada
  participante y cada familia completa de guiones queda en un solo conjunto, el que se usa para definir la regla o el
  que se usa para evaluarla.
- **Los tipos que pueden refutar la idea**, además de los típicos: estafas que escalan, estafas con tono tranquilo,
  estafas con presión desde el saludo, emergencias legítimas con un familiar agitado, vendedores y cobradores
  insistentes, legítimas tranquilas, y llamadas con y sin dudas antes del pedido.
- **El canal real.** Si se prueba banda telefónica, se codifica y decodifica con AMR-NB o G.711. Remuestrear a 8 kHz no
  equivale a pasar por el códec.

### 4.2. Lo que se puede mirar sin audio

Los conjuntos reales de la evaluación final son texto traducido, sin audio: no sirven para la voz ni para los tiempos.
Sí permiten contar con qué frecuencia la persona duda antes del pedido en llamadas que no se escribieron para esto, que
es lo que necesita el patrón 3. En las 27 estafas reales con pedido de alto riesgo registrado se cuenta cuántas tienen
una duda antes del primer pedido; las seis sin pedido se describen aparte. En las 33 legítimas reales, no solo las 21
que avisaron, se cuentan hasta un horizonte común. Las marcas requieren revisión y los roles de las legítimas se
infirieron sobre una transcripción sin hablantes
([procedencia](FUENTES-LEGITIMAS-REALES.md#85-límites-para-informar)); alcanzan para un recuento exploratorio.

### 4.3. Para qué sirve el piloto

No fija un tamaño de muestra: lo estima. Sirve para saber:

- si los rasgos son estables: la misma persona, en las mismas condiciones, ¿da valores parecidos?;
- si los patrones de §2.2 aparecen, y en qué tipos de llamada;
- cuántas llamadas cambian de decisión entre un método y el siguiente;
- para el patrón 3, cuántas de las dudas grabadas dejan una respuesta aprovechable antes de `T_R`. Cuántas llamadas
  tienen dudas lo fija el diseño de los guiones, así que esa frecuencia sale de §4.2, no del piloto.

Con eso se dimensiona una evaluación posterior: cuántas estafas y cuántas legítimas hacen falta, teniendo en cuenta
cuántas llamadas comparten participantes y qué precisión se quiere.

## 5. Criterio para avanzar

> **Estado: propuesta sin discutir.** Los valores concretos se fijan por escrito antes de grabar.

Antes de abrir la reserva se fijan una mejora mínima que justifique seguir y un máximo de falsas alarmas adicionales.
El piloto justifica una evaluación más grande si se cumplen las tres condiciones:

1. **Los rasgos son estables** en la misma persona y las mismas condiciones, dentro de un margen fijado.
2. **Algún patrón aparece.** En los datos usados para definir la regla, no en la reserva, al menos uno de los patrones
   de §2.2 es más frecuente en estafas que en legítimas del mismo tipo.
3. **Un método supera al anterior por la mejora mínima** (1 a 0, o 2 a 1) en estafas que pasan a avisarse antes de
   `T_R`, en estafas nuevas avisadas o en margen ganado, sin pasar el máximo de falsas alarmas adicionales, con la
   incertidumbre informada.

Si falla 1 o 2, se escribe por qué y se cierra. Si 1 supera a 0 y 2 no supera a 1, aportan los tiempos y no la voz. Si
el control explica la mejora del patrón 3, aporta notar la duda en el texto, no cómo se respondió.

## 6. Límites

- **Recreado no es natural.** Un resultado positivo en el piloto no prueba nada sobre llamadas reales; hace falta una
  validación aparte.
- **Que aprenda la grabación y no la estafa.** Un modelo de audio puede apoyarse en diferencias de grabación: en
  detección de voces falsas, modelos entrenados en ASVspoof 2019 se apoyaban en cuánto silencio había al principio
  (Müller et al., 2021). Grabar las dos clases igual y agrupar la reserva por personas apunta a eso.
- **Sesgo por grupos.** Las falsas alarmas se informan por región o tonada, género y edad, con márgenes fijados antes e
  incertidumbre. Con grupos chicos, una diferencia puede ser ruido, y no observar diferencias tampoco demuestra que no
  haya sesgo.
- **Qué no se mide.** Ni acento, región o nivel socioeconómico: no son pertinentes para la finalidad, penalizarían a
  hablantes legítimos por cómo hablan, y la Ley 25.326 exige que los datos sean pertinentes y no excesivos para la
  finalidad
  ([privacidad del sistema](../corpus/PRIVACIDAD-DEL-SISTEMA.md#2-marco-legal-argentino-ley-25326-de-protección-de-datos-personales)).
  Ni si alguien miente: los analizadores de estrés vocal rinden cerca del azar (Horvath, 1982; National Research
  Council, 2003), y Eriksson y Lacerda (2007) califican de charlatanería a dos de esos detectores. Ni si la voz es
  sintética, que es otra línea con otros datos (por ejemplo AASIST, Jung et al., 2022).
- **Privacidad en el producto.** La comparación con la propia voz necesita conservar en memoria un resumen de los
  rasgos de `OTRA` hasta el final de la llamada, no solo durante el turno. Ese resumen se descarta al cortar y nunca se
  guarda.
- **Privacidad en la investigación.** Las grabaciones del piloto requieren consentimiento informado, acceso restringido
  y un plazo de retención explícito, y quedan fuera de Git ([invariantes](../../AGENTS.md#invariantes)).
- **Costo en el teléfono, sin medir.** En el Samsung A56 se midió el detector con un prompt anterior
  ([§8.6](../tesis/CAP-08-RESULTADOS-EXPERIMENTALES.md#86-rendimiento-y-límites-del-hardware)). Falta medir el
  recorrido con ASR y el costo adicional de extraer los rasgos.

## 7. Alternativas posteriores

Quedan fuera del piloto y solo tienen sentido si el método 2 muestra algo:

- **Dimensiones de tono preentrenadas.** El modelo de audEERING estima activación, dominancia y valencia a partir de la
  onda de audio (Wagner et al., 2023). Dos cuidados: «dominancia» no equivale a dar órdenes, y los mismos autores
  muestran que el modelo capta información léxica al estimar la valencia. Si mejora la clasificación, es más difícil
  atribuir la mejora al tono y no a las palabras.
- **Una red propia sobre el espectrograma.** Necesita mucho audio y es la más expuesta a aprender la grabación.
- **Que E2B escuche el turno.** Quedó afuera sin medir en la
  [corrida de #152](../../experiments/asr-local/corridas/2026-11-10_152-opcion-b-e2b-transcribe/resumen.md#por-qué-la-opción-c-queda-afuera-sin-medirla).

VISHGUARD ([estado del arte](SINTESIS-ESTADO-DEL-ARTE.md#23-datasets-y-límites-de-reutilización-recuperación-de-43))
sirve como antecedente de anotación de persuasión y emoción en llamadas sintéticas, no como datos para este piloto: no
tiene español.

## 8. Fuentes

- Eriksson, A. y Lacerda, F. (2007). Charlatanry in forensic speech science: A problem to be taken seriously.
  *International Journal of Speech, Language and the Law*, 14(2), 169–193.
- Eyben, F. et al. (2016). The Geneva Minimalistic Acoustic Parameter Set (GeMAPS) for Voice Research and Affective
  Computing. *IEEE Transactions on Affective Computing*, 7(2), 190–202.
  [doi:10.1109/TAFFC.2015.2457417](https://doi.org/10.1109/TAFFC.2015.2457417).
- Horvath, F. (1982). Detecting deception: the promise and the reality of voice stress analysis. *Journal of Forensic
  Sciences*, 27(2), 340–351.
- Jung, J. et al. (2022). AASIST: Audio Anti-Spoofing using Integrated Spectro-Temporal Graph Attention Networks.
  *ICASSP 2022*.
- Müller, N. M. et al. (2021). Speech is Silver, Silence is Golden: What do ASVspoof-trained Models Really Learn?
  *ASVspoof 2021 Workshop*.
- National Research Council (2003). *The Polygraph and Lie Detection*. Washington, DC: The National Academies Press.
- Wagner, J. et al. (2023). Dawn of the Transformer Era in Speech Emotion Recognition: Closing the Valence Gap. *IEEE
  Transactions on Pattern Analysis and Machine Intelligence*, 45(9), 10745–10759.
  [arXiv:2203.07378](https://arxiv.org/abs/2203.07378).
- Xu, C. et al. (2024). Voice quality in telephone speech: Comparing acoustic measures between VoIP telephone and
  high-quality recordings. *Interspeech 2024*, 1570–1574.
  [doi:10.21437/Interspeech.2024-2240](https://www.isca-archive.org/interspeech_2024/xu24j_interspeech.html).
