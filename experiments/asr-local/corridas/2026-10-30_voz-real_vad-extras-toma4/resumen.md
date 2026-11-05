# Silero contra RMS: lo que el WER no muestra

> Una voz (Luciano), micrófono de la Mac, demora y costo medidos offline en la M1 (2 hilos para el ASR, 1 para Silero). No cierra D09. Plan: [PLAN-VOZ-REAL.md §12](../../PLAN-VOZ-REAL.md). Issue #94.

WER, CER y etiquetas de las mismas variantes: [2026-10-30_voz-real_toma4-mezclas-silero](../2026-10-30_voz-real_toma4-mezclas-silero/resumen.md).

## 1. Grabaciones sin texto (todo lo que sale es inventado)

| Grabación | Variante | Voz según el detector | Segmentos abiertos | Al ASR | Llamadas al ASR | Audio al ASR (s) | Finales con texto | Palabras inventadas (finales / borradores) | Lo que salió |
|---|---|---|---|---|---|---|---|---|---|
| G10b 30 s sin hablar, ruidos de la pieza | `parakeet-0.8-rms-0.008` | 39.9 % | 4 | 4 | 24 | 116.44 | 1 | 1 / 2 | «Sh» |
| G10b 30 s sin hablar, ruidos de la pieza | `parakeet-0.8-rms-0.008-filtro-silero-0.5` | 39.9 % | 4 | 0 | 0 | 0 | 0 | 0 / 0 | — |
| G10b 30 s sin hablar, ruidos de la pieza | `parakeet-0.8-rms-0.008-y-silero-0.5` | 1.1 % | 2 | 0 | 0 | 0 | 0 | 0 / 0 | — |
| G10b 30 s sin hablar, ruidos de la pieza | `parakeet-0.3-silero-0.9` | 0.0 % | 0 | 0 | 0 | 0 | 0 | 0 / 0 | — |
| G10c 30 s sin hablar, con la tele | `parakeet-0.8-rms-0.008` | 99.9 % | 5 | 5 | 82 | 444.37 | 0 | 0 / 0 | — |
| G10c 30 s sin hablar, con la tele | `parakeet-0.8-rms-0.008-filtro-silero-0.5` | 99.9 % | 5 | 1 | 2 | 11.12 | 0 | 0 / 0 | — |
| G10c 30 s sin hablar, con la tele | `parakeet-0.8-rms-0.008-y-silero-0.5` | 2.5 % | 1 | 1 | 2 | 3.12 | 0 | 0 / 0 | — |
| G10c 30 s sin hablar, con la tele | `parakeet-0.3-silero-0.9` | 0.0 % | 0 | 0 | 0 | 0 | 0 | 0 / 0 | — |

## 2. Serie de fondo mientras habla (G08): ¿se sigue cerrando por el tope?

| Grabación | Variante | Voz según el detector | Segmentos | Cierres por silencio / tope / fin | Duración de los segmentos (s) |
|---|---|---|---|---|---|
| G08b serie de fondo panel parakeet 0.8/0.008 (toma 4) | `parakeet-0.8-rms-0.008` | 99.3 % | 3 | 0 / 2 / 1 | 10.0, 10.0, 4.4 |
| G08b serie de fondo panel parakeet 0.8/0.008 (toma 4) | `parakeet-0.8-rms-0.008-filtro-silero-0.5` | 99.3 % | 3 | 0 / 2 / 1 | 10.0, 10.0, 4.4 |
| G08b serie de fondo panel parakeet 0.8/0.008 (toma 4) | `parakeet-0.8-rms-0.008-y-silero-0.5` | 91.3 % | 3 | 0 / 2 / 1 | 10.0, 10.0, 3.7 |
| G08b serie de fondo panel parakeet 0.8/0.008 (toma 4) | `parakeet-0.3-silero-0.9` | 81.8 % | 4 | 4 / 0 / 0 | 4.7, 4.3, 3.6, 10.0 |

## 3. Todas las grabaciones con texto (19)

| Variante | Segmentos abiertos | Descartados sin ASR (< 0,3 s de voz) | Cierres por tope | Llamadas al ASR (borradores + finales) | Audio al ASR (s) | Tiempo de ASR (s) |
|---|---|---|---|---|---|---|
| `parakeet-0.8-rms-0.008` | 79 | 1 | 6 | 679 | 2608 | 126.7 |
| `parakeet-0.8-rms-0.008-filtro-silero-0.5` | 79 | 1 | 6 | 669 | 2583 | 124.3 |
| `parakeet-0.8-rms-0.008-y-silero-0.5` | 83 | 1 | 5 | 664 | 2393 | 117.9 |
| `parakeet-0.3-silero-0.9` | 111 | 0 | 0 | 651 | 1820 | 90.3 |

## 4. Demora del detector contra el RMS 0,008 y costo por bloque

Desfase = flanco del detector − flanco RMS más cercano (± 0,6 s), en las 19 grabaciones con texto; positivo es que el detector llega después. El costo es solo la decisión voz/silencio de cada bloque de 40 ms, sin el ASR.

| Variante | Desfase al empezar la voz: mediana (p10–p90) s | Desfase al terminar: mediana (p10–p90) s | Decisión por bloque: mediana / p95 / máx. (ms) | % de los 40 ms (mediana) |
|---|---|---|---|---|
| `parakeet-0.8-rms-0.008` | +0.00 (+0.00 a +0.00), n=297 | +0.00 (+0.00 a +0.00), n=296 | 0.004 / 0.041 / 0.22 | 0.01 % |
| `parakeet-0.8-rms-0.008-filtro-silero-0.5` | +0.00 (+0.00 a +0.00), n=297 | +0.00 (+0.00 a +0.00), n=296 | 0.116 / 0.240 / 8.70 | 0.29 % |
| `parakeet-0.8-rms-0.008-y-silero-0.5` | +0.00 (+0.00 a +0.04), n=298 | +0.00 (+0.00 a +0.00), n=298 | 0.116 / 0.245 / 4.57 | 0.29 % |
| `parakeet-0.3-silero-0.9` | +0.04 (+0.00 a +0.10), n=165 | +0.04 (-0.04 a +0.16), n=165 | 0.110 / 0.233 / 23.47 | 0.28 % |

## 5. Inicios de palabra

Frases con texto cuya primera palabra no aparece entre las dos primeras de la transcripción, según el reparto por frases de `medir_voz_real.py`. Incluye errores del modelo, no solo cortes.

| Variante | Frases con la primera palabra perdida | «Compartí pantalla» (toma: lo que salió) |
|---|---|---|
| `parakeet-0.8-rms-0.008` | 11/95 | t4: «Compartir pantalla y entra a la configuración de la cuenta. Yo te guío.» · t4: «Compartir pantalla y entrar a la configuración de la cuenta. Yote guío.» · t4: «pantalla y entrar a la ubicación de la cuenta. Yo te guío.» |
| `parakeet-0.8-rms-0.008-filtro-silero-0.5` | 11/95 | t4: «Compartir pantalla y entra a la configuración de la cuenta. Yo te guío.» · t4: «Compartir pantalla y entrar a la configuración de la cuenta. Yote guío.» · t4: «pantalla y entrar a la ubicación de la cuenta. Yo te guío.» |
| `parakeet-0.8-rms-0.008-y-silero-0.5` | 10/95 | t4: «Compartir pantalla y entrar a la configuración de la cuenta. Yo te guío.» · t4: «Compartir pantalla y entrar a la configuración de la cuenta. YoTIO.» · t4: «la pantalla y entrar a la ubicación de la cuenta. Yo te guío.» |
| `parakeet-0.3-silero-0.9` | 7/95 | t4: «Compartir pantalla y entrar a la configuración de la cuenta. Yo te guío.» · t4: «Compartir pantalla y entrar a la configuración de la cuenta. YTIU.» · t4: «la pantalla y entrar a la ubicación de la cuenta. Yo te guío.» |

El segmento de «pantalla» transcripto otra vez con más audio previo (mismo reconocedor, sin el corte):

| Variante | Grabación | Audio previo extra (s) | Lo que salió |
|---|---|---|---|
| `parakeet-0.8-rms-0.008` | G06 panel parakeet-filtro 0.8/0.008 (toma 4) | 0.0 | «Compartir pantalla y entra a la configuración de la cuenta. Yo te guío.» |
| `parakeet-0.8-rms-0.008` | G06 panel parakeet-filtro 0.8/0.008 (toma 4) | 0.3 | «compartir pantalla y entra a la configuración de la cuenta yo te guío» |
| `parakeet-0.8-rms-0.008` | G06 panel parakeet-filtro 0.8/0.008 (toma 4) | 0.6 | «compartir pantalla y entra a la configuración de la cuenta yo te guío» |
| `parakeet-0.8-rms-0.008` | G06 panel parakeet-y 0.8/0.008 (toma 4) | 0.0 | «Compartir pantalla y entrar a la configuración de la cuenta. Yote guío.» |
| `parakeet-0.8-rms-0.008` | G06 panel parakeet-y 0.8/0.008 (toma 4) | 0.3 | «Compartir pantalla y entrar la configuración de la cuenta. Yo te io.» |
| `parakeet-0.8-rms-0.008` | G06 panel parakeet-y 0.8/0.008 (toma 4) | 0.6 | «compartir pantalla y entrar a la configuración de la cuenta jot» |
| `parakeet-0.8-rms-0.008` | G06 panel parakeet-silero 0.3 (toma 4) | 0.0 | «Compartir la pantalla y entrar a la ubicación de la cuenta. Yo te guío.» |
| `parakeet-0.8-rms-0.008` | G06 panel parakeet-silero 0.3 (toma 4) | 0.3 | «compartir la pantalla y entrar a la ubicación de la cuenta. Yo te gui.» |
| `parakeet-0.8-rms-0.008` | G06 panel parakeet-silero 0.3 (toma 4) | 0.6 | «Compartir la pantalla y entrar a la ubicación de la cuenta. Yo te guió.» |
| `parakeet-0.8-rms-0.008-filtro-silero-0.5` | G06 panel parakeet-filtro 0.8/0.008 (toma 4) | 0.0 | «Compartir pantalla y entra a la configuración de la cuenta. Yo te guío.» |
| `parakeet-0.8-rms-0.008-filtro-silero-0.5` | G06 panel parakeet-filtro 0.8/0.008 (toma 4) | 0.3 | «compartir pantalla y entra a la configuración de la cuenta yo te guío» |
| `parakeet-0.8-rms-0.008-filtro-silero-0.5` | G06 panel parakeet-filtro 0.8/0.008 (toma 4) | 0.6 | «compartir pantalla y entra a la configuración de la cuenta yo te guío» |
| `parakeet-0.8-rms-0.008-filtro-silero-0.5` | G06 panel parakeet-y 0.8/0.008 (toma 4) | 0.0 | «Compartir pantalla y entrar a la configuración de la cuenta. Yote guío.» |
| `parakeet-0.8-rms-0.008-filtro-silero-0.5` | G06 panel parakeet-y 0.8/0.008 (toma 4) | 0.3 | «Compartir pantalla y entrar la configuración de la cuenta. Yo te io.» |
| `parakeet-0.8-rms-0.008-filtro-silero-0.5` | G06 panel parakeet-y 0.8/0.008 (toma 4) | 0.6 | «compartir pantalla y entrar a la configuración de la cuenta jot» |
| `parakeet-0.8-rms-0.008-filtro-silero-0.5` | G06 panel parakeet-silero 0.3 (toma 4) | 0.0 | «Compartir la pantalla y entrar a la ubicación de la cuenta. Yo te guío.» |
| `parakeet-0.8-rms-0.008-filtro-silero-0.5` | G06 panel parakeet-silero 0.3 (toma 4) | 0.3 | «compartir la pantalla y entrar a la ubicación de la cuenta. Yo te gui.» |
| `parakeet-0.8-rms-0.008-filtro-silero-0.5` | G06 panel parakeet-silero 0.3 (toma 4) | 0.6 | «Compartir la pantalla y entrar a la ubicación de la cuenta. Yo te guió.» |
| `parakeet-0.8-rms-0.008-y-silero-0.5` | G06 panel parakeet-filtro 0.8/0.008 (toma 4) | 0.0 | «Compartir pantalla y entrar a la configuración de la cuenta. Yo te guío.» |
| `parakeet-0.8-rms-0.008-y-silero-0.5` | G06 panel parakeet-filtro 0.8/0.008 (toma 4) | 0.3 | «Compartir pantalla y entra a la configuración de la cuenta. Yo te guío.» |
| `parakeet-0.8-rms-0.008-y-silero-0.5` | G06 panel parakeet-filtro 0.8/0.008 (toma 4) | 0.6 | «compartir pantalla y entra a la configuración de la cuenta yo te guío» |
| `parakeet-0.8-rms-0.008-y-silero-0.5` | G06 panel parakeet-y 0.8/0.008 (toma 4) | 0.0 | «Compartir pantalla y entrar a la configuración de la cuenta. YoTIO.» |
| `parakeet-0.8-rms-0.008-y-silero-0.5` | G06 panel parakeet-y 0.8/0.008 (toma 4) | 0.3 | «Compartir pantalla y entrar la configuración de la cuenta. Yo te guío.» |
| `parakeet-0.8-rms-0.008-y-silero-0.5` | G06 panel parakeet-y 0.8/0.008 (toma 4) | 0.6 | «compartir pantalla y entrar la configuración de la cuenta yo te guío» |
| `parakeet-0.8-rms-0.008-y-silero-0.5` | G06 panel parakeet-silero 0.3 (toma 4) | 0.0 | «Compartir la pantalla y entrar a la ubicación de la cuenta. Yo te guío.» |
| `parakeet-0.8-rms-0.008-y-silero-0.5` | G06 panel parakeet-silero 0.3 (toma 4) | 0.3 | «compartir la pantalla y entrar a la ubicación de la cuenta. Yo te gui.» |
| `parakeet-0.8-rms-0.008-y-silero-0.5` | G06 panel parakeet-silero 0.3 (toma 4) | 0.6 | «Compartir la pantalla y entrar a la ubicación de la cuenta. Yo te guió.» |
| `parakeet-0.3-silero-0.9` | G06 panel parakeet-filtro 0.8/0.008 (toma 4) | 0.0 | «Compartir pantalla y entrar a la configuración de la cuenta. Yo te guío.» |
| `parakeet-0.3-silero-0.9` | G06 panel parakeet-filtro 0.8/0.008 (toma 4) | 0.3 | «Compartir pantalla y entra a la configuración de la cuenta. Yo te guío.» |
| `parakeet-0.3-silero-0.9` | G06 panel parakeet-filtro 0.8/0.008 (toma 4) | 0.6 | «compartir pantalla y entra a la configuración de la cuenta yo te guío» |
| `parakeet-0.3-silero-0.9` | G06 panel parakeet-y 0.8/0.008 (toma 4) | 0.0 | «Compartir pantalla y entrar a la configuración de la cuenta. YTIU.» |
| `parakeet-0.3-silero-0.9` | G06 panel parakeet-y 0.8/0.008 (toma 4) | 0.3 | «Compartir pantalla y entrar la configuración de la cuenta. Yo te guio.» |
| `parakeet-0.3-silero-0.9` | G06 panel parakeet-y 0.8/0.008 (toma 4) | 0.6 | «compartir pantalla y entrar la configuración de la cuenta yo te guío» |
| `parakeet-0.3-silero-0.9` | G06 panel parakeet-silero 0.3 (toma 4) | 0.0 | «Compartir la pantalla y entrar a la ubicación de la cuenta. Yo te guío.» |
| `parakeet-0.3-silero-0.9` | G06 panel parakeet-silero 0.3 (toma 4) | 0.3 | «compartir la pantalla y entrar a la ubicación de la cuenta Yote Gio.» |
| `parakeet-0.3-silero-0.9` | G06 panel parakeet-silero 0.3 (toma 4) | 0.6 | «compartir la pantalla y entrar a la ubicación de la cuenta. Yo te guío.» |

Primeras palabras perdidas, por variante:

- `parakeet-0.8-rms-0.008`: t4 «Ñaño,» → «Al pedo te…»; t4 «Te» → «Testrigo del Galicia,…»; t4 «Ñaño,» → «Al pedo te…»; t4 «El» → «The número de…»; t4 «Tu» → «12. Pásame el…»; t4 «Mi» → «Así que está…»; t4 «Ñaño,» → «Al pedo te…»; t4 «Abrí» → «341927. el enlace…»; t4 «Esta» → «Me salió de…»; t4 «Te» → «Compartir la…»; t4 «Compartí» → «pantalla y entrar…»
- `parakeet-0.8-rms-0.008-filtro-silero-0.5`: t4 «Ñaño,» → «Al pedo te…»; t4 «Te» → «Testrigo del Galicia,…»; t4 «Ñaño,» → «Al pedo te…»; t4 «El» → «The número de…»; t4 «Tu» → «12. Pásame el…»; t4 «Mi» → «Así que está…»; t4 «Ñaño,» → «Al pedo te…»; t4 «Abrí» → «341927. el enlace…»; t4 «Esta» → «Me salió de…»; t4 «Te» → «Compartir la…»; t4 «Compartí» → «pantalla y entrar…»
- `parakeet-0.8-rms-0.008-y-silero-0.5`: t4 «Ñaño,» → «Al pedo te…»; t4 «Te» → «Testrigo del Galicia,…»; t4 «Ñaño,» → «Al pedo te…»; t4 «Tu» → «tarjeta quedó bloqueada.…»; t4 «Te» → «estrivo del Galicia,…»; t4 «Ñaño,» → «Al pedo te…»; t4 «Abrí» → «341927. Abre enlace…»; t4 «Te» → «Que llegue un…»; t4 «Esta» → «me salió de…»; t4 «Hacé» → «Haz la transferencia…»
- `parakeet-0.3-silero-0.9`: t4 «Ñaño,» → «Al pedo te…»; t4 «Ñaño,» → «Al pedo te…»; t4 «Abrí» → «abre el enlace…»; t4 «Mandame» → «Máme el código…»; t4 «Ñaño,» → «Al pedo te…»; t4 «Abrí» → «abre el enlace…»; t4 «Te» → «Que llega un…»

## 7. Reproducir

```bash
python experiments/asr-local/comparar_vad.py --pruebas ../voip/llamadas --variantes parakeet-0.8-rms-0.008,parakeet-0.8-rms-0.008-filtro-silero-0.5,parakeet-0.8-rms-0.008-y-silero-0.5,parakeet-0.3-silero-0.9 --corrida corridas/2026-10-30_voz-real_toma4-mezclas-silero --salida corridas/2026-10-30_voz-real_vad-extras-toma4
```

Código: `734988d9814ca20cfbc9e3e0e0662a7a469eb012` (LucianoGrosso13/silero-vs-rms-94, limpio). Detalle por segmento en `extras.json`.
