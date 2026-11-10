> **Estado: borrador parcial del 2026-11-03.** Las conclusiones finales dependen del test reservado (#52). Lo que sigue no adelanta ese resultado.

# Capítulo 11: Conclusiones

## 11.1. Aportes y resultados principales

**Ya disponibles:**

- Un recorrido local y reproducible, desde el audio de una llamada hasta un aviso explicado, con voz real por Meet en una notebook de 8 GB.
- Una evaluación centrada en el tiempo de intervención, con una separación estricta entre lo que el detector puede ver y la referencia.
- Una comparación de detectores que incluye resultados negativos: reglas, cascadas, cross-encoders, prompts que no generalizaron y una compuerta entrenada como clasificador, que no ve lo sensible ([H09](../hallazgos/H09-tito-clasificador-en-vez-de-compuerta.md)).
- Un corpus controlado en español, con contexto argentino y legítimas difíciles, todavía sin revisión humana.
- Una configuración justificada con alternativas descartadas: Parakeet con filtro Silero, y Tito viejo con Gemma 4 E2B.

> **Corregir (#51):** la configuración del detector la fija el ADR 0002.

**[Completar con el resultado del test reservado.]**

## 11.2. Hipótesis respaldadas o no

**[Completar con #52.]** Provisionalmente, en desarrollo:

- Un filtro liviano reduce las consultas a la mitad, pero no las falsas alarmas de E2B. En #101, la única que desaparece está en una llamada que Tito ya había derivado; en los 150 casos de desarrollo, las que desaparecen son un punto ciego del filtro. En los 150 casos, además, pierde una estafa ([H08](../hallazgos/H08-tito-evita-falsas-alarmas-por-punto-ciego.md)).
- La calidad medida con TTS no anticipa la calidad con voz real.
- Los márgenes observados con voz real son más ajustados de lo deseable: el aviso suele llegar después de empezado el pedido.

## 11.3. Limitaciones

- Sin medición en teléfono, y con la latencia y la memoria por encima de los criterios de prefactibilidad.
- Corpus simulado, de redacción asistida y sin referencia humana validada.
- Las métricas de detección salen de conversaciones escritas, no de audio transcripto. El ASR se midió aparte, con voz real y ruido de fondo, sin comparar el mismo detector sobre las dos entradas.
- Voz real limitada a 4 guiones y 2 voces, con el audio original perdido.
- El contenido de una llamada no permite verificar la identidad de quien habla.
- Sin prueba con usuarios: no se sabe si el aviso cambia la conducta de una persona.
- La captura universal de llamadas telefónicas queda fuera de alcance por restricción de plataforma.

## 11.4. Trabajo futuro acotado

- Medir la configuración en un teléfono de gama alta: latencia, memoria, batería y temperatura.
- Si esa medición muestra que hace falta ahorrar consultas, rediseñar la compuerta como detector de lo sensible. Se entrenaría con líneas de conversación de las dos voces, incluidas las cortas, y se mediría por cobertura antes que por ahorro ([H09](../hallazgos/H09-tito-clasificador-en-vez-de-compuerta.md), [#149](https://github.com/Corchets/bitacora_tesis/issues/149)).
- Bajar la demora por consulta, con caché de prefijo o respuestas más cortas.
- Ampliar el reconocimiento de términos críticos, como «token» y «CVV».
- Probar la comprensión del aviso con voluntarios, especialmente adultos mayores.
- Evaluar con más voces, ruido real y códecs telefónicos.
- Explorar rasgos acústicos, hoy excluidos ([D11](../gestion/MAPA-DECISIONES.md#d11--análisis-lingüístico-o-también-acústico)).
- Que el SLM escuche el audio del turno, con lo anterior como texto, en vez de leer la transcripción. Antes hay que resolver cómo se arma el contexto, porque la llamada entera no entra, y evaluar con audio de todos los casos ([corrida de #152](../../experiments/asr-local/corridas/2026-11-10_152-opcion-b-e2b-transcribe/resumen.md#por-qué-la-opción-c-queda-afuera-sin-medirla)).
