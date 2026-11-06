# H03 — El SLM avisa en la línea del pedido, no antes

- **Fecha:** 2026-11-05
- **Tipo:** resultado
- **Estado:** vigente. La segunda vuelta de [#143](https://github.com/Corchets/bitacora_tesis/issues/143) prueba un prompt que mira la intención.
- **Evidencia:**
  - [Descripción de #143](https://github.com/Corchets/bitacora_tesis/issues/143), sección «Variantes».
  - Líneas base de `corridas/2026-11-05_puntaje-token-150/analisis-salida.md`, en la rama `exp/143-puntaje-token` hasta su merge.
- **Afecta a:** PI2 (margen temporal) en el [capítulo 9](../tesis/CAP-09-DISCUSION.md#91-respuesta-a-las-preguntas-de-investigación).

## Qué encontramos

- En corpus_v2, la mediana del adelanto `L_R` es 0: el aviso cae en la línea del pedido.
- De las 36 estafas de corpus_v2 con `T_R`, el aviso llega 3 líneas o más antes del pedido en 9 con v1 solo y en 7 con v4 solo.
- La sospecha aparece antes en el riesgo escrito, pero no llega al aviso. Con v4, el riesgo ronda 0,3 en las 6 líneas anteriores al pedido y salta a 0,53 en el pedido.
- **Causa:** todos los prompts definen el aviso como «hay un pedido».
  - v1 dice «solo si… alguien pide».
  - v3 a v5 dicen que «alguien apure o diga ser de una entidad… no alcanza por sí solo para alertar».

## Qué tan seguro es

Las marcas de `T_R` son provisionales, sin revisión humana. Las posiciones están en líneas, no en segundos.

## Qué cambia

El margen preventivo está limitado por cómo definimos el aviso, no solo por la latencia. Hay que contarlo así al responder PI2.
