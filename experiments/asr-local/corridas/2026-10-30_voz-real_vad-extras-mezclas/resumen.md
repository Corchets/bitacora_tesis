# Silero contra RMS: lo que el WER no muestra

> Una voz (Luciano), micrófono de la Mac, demora y costo medidos offline en la M1 (2 hilos para el ASR, 1 para Silero). No cierra D09. Plan: [PLAN-VOZ-REAL.md §12](../../PLAN-VOZ-REAL.md). Issue #94.

WER, CER y etiquetas de las mismas variantes: [2026-10-30_voz-real_parakeet-mezclas-silero](../2026-10-30_voz-real_parakeet-mezclas-silero/resumen.md).

## 1. Grabaciones sin texto (todo lo que sale es inventado)

| Grabación | Variante | Voz según el detector | Segmentos abiertos | Al ASR | Llamadas al ASR | Audio al ASR (s) | Finales con texto | Palabras inventadas (finales / borradores) | Lo que salió |
|---|---|---|---|---|---|---|---|---|---|
| G10 30 s sin hablar, tele apagada | `parakeet-0.8-rms-0.008` | 31.3 % | 10 | 9 | 28 | 79.12 | 2 | 4 / 4 | «Shh. Uh-uh.» · «He» |
| G10 30 s sin hablar, tele apagada | `parakeet-0.8-rms-0.008-filtro-silero-0.5` | 31.3 % | 10 | 1 | 1 | 2.4 | 1 | 3 / 0 | «Shh. Uh-uh.» |
| G10 30 s sin hablar, tele apagada | `parakeet-0.8-rms-0.008-y-silero-0.5` | 1.4 % | 2 | 1 | 1 | 1.56 | 1 | 2 / 0 | «Uh uh.» |
| serie de fondo sin hablar | `parakeet-0.8-rms-0.008` | 10.7 % | 24 | 10 | 40 | 165.32 | 6 | 17 / 14 | «Hello» · «Well then.» · «Creo que tú tampoco. No quiero que te desmida.» · «No sé, nada.» · «Mm.» · «Okay,» |
| serie de fondo sin hablar | `parakeet-0.8-rms-0.008-filtro-silero-0.5` | 10.7 % | 24 | 6 | 10 | 34.32 | 4 | 14 / 13 | «Hello» · «Creo que tú tampoco. No quiero que te desmida.» · «No sé, nada.» · «Okay,» |
| serie de fondo sin hablar | `parakeet-0.8-rms-0.008-y-silero-0.5` | 3.6 % | 15 | 7 | 10 | 20.4 | 4 | 10 / 6 | «Very good.» · «No quiero que después.» · «Não sei, não.» · «Okay.» |

## 2. G08, serie de fondo mientras habla: ¿se sigue cerrando por el tope?

| Variante | Voz según el detector | Segmentos | Cierres por silencio / tope / fin | Duración de los segmentos (s) |
|---|---|---|---|---|
| `parakeet-0.8-rms-0.008` | 90.0 % | 3 | 0 / 2 / 1 | 10.0, 10.0, 7.7 |
| `parakeet-0.8-rms-0.008-filtro-silero-0.5` | 90.0 % | 3 | 0 / 2 / 1 | 10.0, 10.0, 7.7 |
| `parakeet-0.8-rms-0.008-y-silero-0.5` | 77.5 % | 4 | 2 / 1 / 1 | 5.6, 5.5, 10.0, 5.2 |

## 3. Todas las grabaciones con texto (20)

| Variante | Segmentos abiertos | Descartados sin ASR (< 0,3 s de voz) | Cierres por tope | Llamadas al ASR (borradores + finales) | Audio al ASR (s) | Tiempo de ASR (s) |
|---|---|---|---|---|---|---|
| `parakeet-0.8-rms-0.008` | 103 | 2 | 6 | 734 | 2583 | 129.9 |
| `parakeet-0.8-rms-0.008-filtro-silero-0.5` | 103 | 2 | 6 | 718 | 2540 | 122.7 |
| `parakeet-0.8-rms-0.008-y-silero-0.5` | 105 | 2 | 5 | 716 | 2441 | 118.7 |

## 4. Demora del detector contra el RMS 0,008 y costo por bloque

Desfase = flanco del detector − flanco RMS más cercano (± 0,6 s), en las 20 grabaciones con texto; positivo es que el detector llega después. El costo es solo la decisión voz/silencio de cada bloque de 40 ms, sin el ASR.

| Variante | Desfase al empezar la voz: mediana (p10–p90) s | Desfase al terminar: mediana (p10–p90) s | Decisión por bloque: mediana / p95 / máx. (ms) | % de los 40 ms (mediana) |
|---|---|---|---|---|
| `parakeet-0.8-rms-0.008` | +0.00 (+0.00 a +0.00), n=475 | +0.00 (+0.00 a +0.00), n=475 | 0.004 / 0.027 / 0.84 | 0.01 % |
| `parakeet-0.8-rms-0.008-filtro-silero-0.5` | +0.00 (+0.00 a +0.00), n=475 | +0.00 (+0.00 a +0.00), n=475 | 0.118 / 0.235 / 35.09 | 0.30 % |
| `parakeet-0.8-rms-0.008-y-silero-0.5` | +0.00 (+0.00 a +0.04), n=464 | +0.00 (+0.00 a +0.00), n=464 | 0.118 / 0.238 / 36.85 | 0.30 % |

## 5. Inicios de palabra

Frases (de las 100 con texto) cuya primera palabra no aparece entre las dos primeras de la transcripción, según el reparto por frases de `medir_voz_real.py`. Incluye errores del modelo, no solo cortes.

| Variante | Frases con la primera palabra perdida | «Compartí pantalla» (toma: lo que salió) |
|---|---|---|
| `parakeet-0.8-rms-0.008` | 10/100 | t2: «la pantalla y entra a la configuración de la cuenta Yot.» · t3: «la pantalla y entra a la configuración de la cuenta Yot.» |
| `parakeet-0.8-rms-0.008-filtro-silero-0.5` | 10/100 | t2: «la pantalla y entra a la configuración de la cuenta Yot.» · t3: «la pantalla y entra a la configuración de la cuenta Yot.» |
| `parakeet-0.8-rms-0.008-y-silero-0.5` | 12/100 | t2: «la pantalla y entra a la configuración de la cuenta Yote» · t3: «la pantalla y entra a la configuración de la cuenta Yot.» |

El segmento de «pantalla» transcripto otra vez con más audio previo (mismo reconocedor, sin el corte):

| Variante | Grabación | Audio previo extra (s) | Lo que salió |
|---|---|---|---|
| `parakeet-0.8-rms-0.008` | G16 tele apagada (toma 2) | 0.0 | «compartir la pantalla y entra la configuración de la cuenta Yot.» |
| `parakeet-0.8-rms-0.008` | G16 tele apagada (toma 2) | 0.3 | «compartir la pantalla y entra la configuración de la cuenta yo te gui» |
| `parakeet-0.8-rms-0.008` | G16 tele apagada (toma 2) | 0.6 | «compartir la pantalla y entrar a la configuración de la cuenta yo te g» |
| `parakeet-0.8-rms-0.008` | G16 conf. panel 0.8/0.008 (toma 3) | 0.0 | «Compartir la pantalla y entra a la configuración de la cuenta Yot.» |
| `parakeet-0.8-rms-0.008` | G16 conf. panel 0.8/0.008 (toma 3) | 0.3 | «Compartir la pantalla y entrar a la configuración de la cuenta Yotgio.» |
| `parakeet-0.8-rms-0.008` | G16 conf. panel 0.8/0.008 (toma 3) | 0.6 | «Compartir la pantalla y entra a la configuración de la cuenta Yotg.» |
| `parakeet-0.8-rms-0.008-filtro-silero-0.5` | G16 tele apagada (toma 2) | 0.0 | «compartir la pantalla y entra la configuración de la cuenta Yot.» |
| `parakeet-0.8-rms-0.008-filtro-silero-0.5` | G16 tele apagada (toma 2) | 0.3 | «compartir la pantalla y entra la configuración de la cuenta yo te gui» |
| `parakeet-0.8-rms-0.008-filtro-silero-0.5` | G16 tele apagada (toma 2) | 0.6 | «compartir la pantalla y entrar a la configuración de la cuenta yo te g» |
| `parakeet-0.8-rms-0.008-filtro-silero-0.5` | G16 conf. panel 0.8/0.008 (toma 3) | 0.0 | «Compartir la pantalla y entra a la configuración de la cuenta Yot.» |
| `parakeet-0.8-rms-0.008-filtro-silero-0.5` | G16 conf. panel 0.8/0.008 (toma 3) | 0.3 | «Compartir la pantalla y entrar a la configuración de la cuenta Yotgio.» |
| `parakeet-0.8-rms-0.008-filtro-silero-0.5` | G16 conf. panel 0.8/0.008 (toma 3) | 0.6 | «Compartir la pantalla y entra a la configuración de la cuenta Yotg.» |
| `parakeet-0.8-rms-0.008-y-silero-0.5` | G16 tele apagada (toma 2) | 0.0 | «compartir la pantalla y entra a la configuración de la cuenta Yote» |
| `parakeet-0.8-rms-0.008-y-silero-0.5` | G16 tele apagada (toma 2) | 0.3 | «compartir la pantalla y entrar a la configuración de la cuenta yo te g» |
| `parakeet-0.8-rms-0.008-y-silero-0.5` | G16 tele apagada (toma 2) | 0.6 | «compartir la pantalla y entra la configuración de la cuenta yo te g» |
| `parakeet-0.8-rms-0.008-y-silero-0.5` | G16 conf. panel 0.8/0.008 (toma 3) | 0.0 | «Compartir la pantalla y entra a la configuración de la cuenta Yot.» |
| `parakeet-0.8-rms-0.008-y-silero-0.5` | G16 conf. panel 0.8/0.008 (toma 3) | 0.3 | «Compartir la pantalla y entrar a la configuración de la cuenta Yotgio.» |
| `parakeet-0.8-rms-0.008-y-silero-0.5` | G16 conf. panel 0.8/0.008 (toma 3) | 0.6 | «Compartir la pantalla y entra a la configuración de la cuenta Yotg.» |

Primeras palabras perdidas, por variante:

- `parakeet-0.8-rms-0.008`: t1 «Ñaño,» → «Al pedo te…»; t1 «Dejá» → «Deje el miso…»; t1 «Mandame» → «Máme el código…»; t1 «Ñaño,» → «Al pedo te…»; t2 «Ñaño,» → «Al pedo te…»; t2 «Abrí» → «abre el enlace…»; t2 «Te» → «Que llevo un…»; t3 «Ñaño,» → «Al pedo te…»; t3 «Te» → «Testorivo del Galicia,…»; t3 «Mandame» → «Máme el código…»
- `parakeet-0.8-rms-0.008-filtro-silero-0.5`: t1 «Ñaño,» → «Al pedo te…»; t1 «Dejá» → «Deje el miso…»; t1 «Mandame» → «Máme el código…»; t1 «Ñaño,» → «Al pedo te…»; t2 «Ñaño,» → «Al pedo te…»; t2 «Abrí» → «abre el enlace…»; t2 «Te» → «Que llevo un…»; t3 «Ñaño,» → «Al pedo te…»; t3 «Te» → «Testorivo del Galicia,…»; t3 «Mandame» → «Máme el código…»
- `parakeet-0.8-rms-0.008-y-silero-0.5`: t1 «Ñaño,» → «Al pedo te…»; t1 «Dejá» → «Deje el miso…»; t1 «Mandame» → «Máme el código…»; t1 «Ñaño,» → «Al pedo ta…»; t2 «Ñaño,» → «Al pedo te…»; t2 «Abrí» → «abre el enlace…»; t2 «Te» → «Que llevo un…»; t2 «Te» → «Escribo del Galicia,…»; t3 «Ñaño,» → «Al pedo te…»; t3 «Tu» → «Pásame el pin…»; t3 «Te» → «Destrivo del Galicia,…»; t3 «Mandame» → «Máme el código…»

## 7. Reproducir

```bash
python experiments/asr-local/comparar_vad.py --pruebas /Users/lucianogrosso/bitacora_tesis-voip-asr/experiments/voip/llamadas --variantes parakeet-0.8-rms-0.008,parakeet-0.8-rms-0.008-filtro-silero-0.5,parakeet-0.8-rms-0.008-y-silero-0.5 --corrida experiments/asr-local/corridas/2026-10-30_voz-real_parakeet-mezclas-silero --salida experiments/asr-local/corridas/2026-10-30_voz-real_vad-extras-mezclas
```

Código: `9c4deb621414f053ac35c059efa31988e1d44a15` (LucianoGrosso13/silero-vs-rms-94, limpio). Detalle por segmento en `extras.json`.
