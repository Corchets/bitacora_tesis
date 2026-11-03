> **Estado: borrador parcial del 2026-11-03.** Las conclusiones finales dependen del test reservado (#52). Lo que sigue no adelanta ese resultado.

# Capítulo 11: Conclusiones

## 11.1. Aportes y resultados principales

**Ya disponibles:**

- Un recorrido local y reproducible, desde el audio de una llamada hasta un aviso explicado, con voz real por Meet en una notebook de 8 GB.
- Una evaluación centrada en el tiempo de intervención, con una separación estricta entre lo que el detector puede ver y la referencia.
- Una comparación de detectores que incluye resultados negativos: reglas, cascadas, cross-encoders y prompts que no generalizaron.
- Un corpus controlado en español, con contexto argentino y legítimas difíciles, todavía sin revisión humana.
- Una configuración justificada con alternativas descartadas: Parakeet con filtro Silero, y Tito viejo con Gemma 4 E2B.

**[Completar con el resultado del test reservado.]**

## 11.2. Hipótesis respaldadas o no

**[Completar con #52.]** Provisionalmente, en desarrollo:

- Un filtro liviano reduce consultas y falsas alarmas sin perder estafas en estos 20 casos, aunque la muestra no permite generalizar.
- La calidad medida con TTS no anticipa la calidad con voz real.
- Los márgenes observados con voz real son más ajustados de lo deseable: el aviso suele llegar después de empezado el pedido.

## 11.3. Limitaciones

- Sin medición en teléfono, y con la latencia y la memoria por encima de los criterios de prefactibilidad.
- Corpus simulado, de redacción asistida y sin referencia humana validada.
- Voz real limitada a 4 guiones y 2 voces, con el audio original perdido.
- El contenido de una llamada no permite verificar la identidad de quien habla.
- Sin prueba con usuarios: no se sabe si el aviso cambia la conducta de una persona.
- La captura universal de llamadas telefónicas queda fuera de alcance por restricción de plataforma.

## 11.4. Trabajo futuro acotado

- Medir la configuración en un teléfono de gama alta: latencia, memoria, batería y temperatura.
- Bajar la demora por consulta, con caché de prefijo o respuestas más cortas.
- Ampliar el reconocimiento de términos críticos, como «token» y «CVV».
- Probar la comprensión del aviso con voluntarios, especialmente adultos mayores.
- Evaluar con más voces, ruido real y códecs telefónicos.
- Explorar rasgos acústicos, hoy excluidos ([D11](../gestion/MAPA-DECISIONES.md#d11--análisis-lingüístico-o-también-acústico)).
