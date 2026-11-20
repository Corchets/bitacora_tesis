> **Estado: borrador del 2026-11-20, propuesta de redacción sin discutir.** Incorpora la evaluación final del 2026-11-19 ([§8.3.4](CAP-08-RESULTADOS-EXPERIMENTALES.md#834-evaluación-final)). Falta revisarlo entre los cuatro.

# Capítulo 11: Conclusiones

## 11.1. Aportes y resultados principales

**Ya disponibles:**

- Un recorrido local y reproducible, desde el audio de una llamada hasta un aviso explicado, con voz real por Meet en una notebook de 8 GB.
- Una evaluación centrada en el tiempo de intervención, con una separación estricta entre lo que el detector puede ver y la referencia.
- Una comparación de detectores que incluye resultados negativos: reglas, cascadas, cross-encoders, prompts que no generalizaron y una compuerta entrenada como clasificador, que no ve lo sensible ([H09](../hallazgos/H09-tito-clasificador-en-vez-de-compuerta.md)).
- Un corpus controlado en español, con contexto argentino y legítimas difíciles, todavía sin revisión humana.
- Una configuración justificada con alternativas descartadas: Parakeet con filtro Silero ([ADR 0001](../ingenieria/adr/0001-parakeet-filtro-y-gemma4-e2b-con-tito-viejo.md)) y Gemma 4 E2B solo, con un prompt que pregunta por la intención de quien llama ([ADR 0002](../ingenieria/adr/0002-detector-gemma4-e2b-solo-con-prompt-c-premisa.md)) y lleva los consejos oficiales ([ADR 0008](../ingenieria/adr/0008-prompt-del-detector-c-consejos.md)).
- Un registro de hallazgos, de [H01 a H13](../hallazgos/README.md), que deja a la vista qué se creía, qué se midió y qué se cambió.

**De la evaluación final:**

- Sobre 100 estafas generadas que no intervinieron en ninguna elección, el detector avisó 73 y llegó a tiempo en 53 de las 80 que tienen pedido, con 15 falsas alarmas en 56 legítimas.
- Avisó las 33 estafas reales de un conjunto externo, y también 21 de 33 llamadas reales legítimas de call center.
- Siete prompts probados después no bajaron esa falsa alarma sin perder estafas: no se corrige cambiando el prompt ([H12](../hallazgos/H12-cambiar-el-prompt-mueve-el-corte-no-la-separacion.md)).

## 11.2. Hipótesis respaldadas o no

Con la evaluación final:

- **Respaldada:** un modelo pequeño que corre en el equipo detecta de forma incremental. Avisó el 73 % de las estafas del test y todas las reales.
- **Respaldada:** preguntar por la intención de quien llama adelanta el aviso. Llegó antes del pedido en 37 de 80 estafas, contra 15 con el prompt de pedidos.
- **No respaldada:** que el modelo detecte más que las reglas léxicas. Las reglas avisaron 87 de 100 estafas; lo que aporta el modelo es avisar en el 27 % de las legítimas y no en el 86 %.
- **No respaldada:** que la especificidad se sostenga en llamadas reales. Avisó en el 64 % de las legítimas reales de call center.
- **Sin responder:** el margen en segundos, con marcas humanas.

En desarrollo:

- Un filtro liviano reduce las consultas a la mitad, pero no las falsas alarmas de E2B. En #101, la única que desaparece está en una llamada que Tito ya había derivado; en los 150 casos de desarrollo, las que desaparecen son un punto ciego del filtro. En los 150 casos, además, pierde una estafa ([H08](../hallazgos/H08-tito-evita-falsas-alarmas-por-punto-ciego.md)).
- La calidad medida con TTS no anticipa la calidad con voz real.
- Los márgenes observados con voz real son más ajustados de lo deseable: el aviso suele llegar después de empezado el pedido.

## 11.3. Limitaciones

- Sin medición del recorrido completo en teléfono: en un Samsung A56 se midió solo el detector, y la latencia y la memoria quedan por encima de los criterios de prefactibilidad.
- Corpus simulado, de redacción asistida y sin referencia humana validada.
- Sin estafas reales argentinas: los dos conjuntos reales tienen 33 llamadas cada uno, están traducidos y son de otros países.
- La evaluación final es una sola corrida. Al repetirla, la misma configuración movió hasta 6 casos de una cifra ([H13](../hallazgos/H13-la-misma-configuracion-corrida-de-otro-modo.md)).
- Las métricas de detección salen de conversaciones escritas, no de audio transcripto. El ASR se midió aparte, con voz real y ruido de fondo, sin comparar el mismo detector sobre las dos entradas.
- Voz real limitada a 4 guiones y 2 voces, con el audio original perdido.
- El contenido de una llamada no permite verificar la identidad de quien habla.
- Sin prueba con usuarios: no se sabe si el aviso cambia la conducta de una persona.
- La captura universal de llamadas telefónicas queda fuera de alcance por restricción de plataforma.

## 11.4. Trabajo futuro acotado

- Medir la configuración en un teléfono de gama alta: latencia, memoria, batería y temperatura.
- Si esa medición muestra que hace falta ahorrar consultas, rediseñar la compuerta como detector de lo sensible. Se entrenaría con líneas de conversación de las dos voces, incluidas las cortas, y se mediría por cobertura antes que por ahorro ([H09](../hallazgos/H09-tito-clasificador-en-vez-de-compuerta.md), [#149](https://github.com/Corchets/bitacora_tesis/issues/149)).
- Bajar la demora por consulta, con caché de prefijo o respuestas más cortas.
- Ajustar el modelo para las llamadas reales, en vez de seguir cambiando el prompt ([H12](../hallazgos/H12-cambiar-el-prompt-mueve-el-corte-no-la-separacion.md), [#176](https://github.com/Corchets/bitacora_tesis/issues/176)).
- Un aviso en dos niveles, uno suave y uno fuerte según el riesgo, para que una llamada comercial no reciba el mismo aviso que una estafa clara.
- Conseguir estafas y llamadas legítimas reales de Argentina, y etiquetarlas a ciegas con la política de producto.
- Ampliar el reconocimiento de términos críticos, como «token» y «CVV».
- Probar la comprensión del aviso con voluntarios, especialmente adultos mayores.
- Evaluar con más voces, ruido real y códecs telefónicos.
- Explorar rasgos acústicos, hoy excluidos ([D11](../gestion/MAPA-DECISIONES.md#d11--análisis-lingüístico-o-también-acústico)).
- Que el SLM escuche el audio del turno, con lo anterior como texto, en vez de leer la transcripción. Antes hay que resolver cómo se arma el contexto, porque la llamada entera no entra, y evaluar con audio de todos los casos ([corrida de #152](../../experiments/asr-local/corridas/2026-11-10_152-opcion-b-e2b-transcribe/resumen.md#por-qué-la-opción-c-queda-afuera-sin-medirla)).
