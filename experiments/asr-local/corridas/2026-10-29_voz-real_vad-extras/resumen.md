# Silero contra RMS: lo que el WER no muestra

> Una voz (Luciano), micrófono de la Mac, demora y costo medidos offline en la M1 (2 hilos para el ASR, 1 para Silero). No cierra D09. Plan: [PLAN-VOZ-REAL.md §12](../../PLAN-VOZ-REAL.md). Issue #94.

WER, CER y etiquetas de las mismas variantes: [2026-10-29_voz-real_parakeet-silero-vs-rms](../2026-10-29_voz-real_parakeet-silero-vs-rms/resumen.md).

## 1. Grabaciones sin texto (todo lo que sale es inventado)

| Grabación | Variante | Voz según el detector | Segmentos abiertos | Al ASR | Llamadas al ASR | Audio al ASR (s) | Finales con texto | Palabras inventadas (finales / borradores) | Lo que salió |
|---|---|---|---|---|---|---|---|---|---|
| G10 30 s sin hablar, tele apagada | `parakeet-0.8-rms-0.008` | 31.3 % | 10 | 9 | 28 | 79.12 | 2 | 4 / 4 | «Shh. Uh-uh.» · «He» |
| G10 30 s sin hablar, tele apagada | `parakeet-0.8-silero-0.5` | 1.5 % | 2 | 1 | 1 | 1.68 | 1 | 2 / 0 | «Uh uh.» |
| G10 30 s sin hablar, tele apagada | `parakeet-0.5-silero-0.5` | 1.5 % | 2 | 1 | 1 | 1.36 | 1 | 2 / 0 | «Uh uh.» |
| G10 30 s sin hablar, tele apagada | `parakeet-0.3-silero-0.5` | 1.5 % | 2 | 1 | 1 | 1.16 | 1 | 2 / 0 | «Uh uh.» |
| G10 30 s sin hablar, tele apagada | `parakeet-0.5-silero-0.9` | 0.0 % | 0 | 0 | 0 | 0 | 0 | 0 / 0 | — |
| G10 30 s sin hablar, tele apagada | `parakeet-0.3-silero-0.9` | 0.0 % | 0 | 0 | 0 | 0 | 0 | 0 / 0 | — |
| serie de fondo sin hablar | `parakeet-0.8-rms-0.008` | 10.7 % | 24 | 10 | 40 | 165.32 | 6 | 17 / 14 | «Hello» · «Well then.» · «Creo que tú tampoco. No quiero que te desmida.» · «No sé, nada.» · «Mm.» · «Okay,» |
| serie de fondo sin hablar | `parakeet-0.8-silero-0.5` | 12.1 % | 19 | 12 | 36 | 88.36 | 7 | 19 / 33 | «Okay.» · «Otro intento.» · «Very good.» · «Hola.» · «No quiero que es una vez.» · «Você não.» · «Esta idea de sus misión.» |
| serie de fondo sin hablar | `parakeet-0.5-silero-0.5` | 12.1 % | 19 | 12 | 36 | 85.48 | 6 | 19 / 37 | «Mm.» · «Otro intento.» · «Very good.» · «Hija, no quiero que te despedida.» · «Não sei, não.» · «Hay que parar las condiciones.» |
| serie de fondo sin hablar | `parakeet-0.3-silero-0.5` | 12.1 % | 20 | 12 | 35 | 80.4 | 9 | 25 / 34 | «Mm.» · «Otro intento.» · «Th.» · «Oh, this is like.» · «Hija, no quiero que te despedida.» · «Não sei, não.» · «Mm-hmm.» · «E' stupido.» · «Esta idea de misiones.» |
| serie de fondo sin hablar | `parakeet-0.5-silero-0.9` | 5.5 % | 10 | 9 | 17 | 32.28 | 5 | 16 / 13 | «Very committee.» · «It is like» · «Hija, no quiero que te desmabecas.» · «Não sei, nada.» · «Mm-hmm.» |
| serie de fondo sin hablar | `parakeet-0.3-silero-0.9` | 5.5 % | 11 | 10 | 17 | 27.76 | 6 | 16 / 1 | «Very good.» · «It is funky.» · «Yeah, no.» · «Yeah, this one.» · «No sé, nada.» · «Something like that.» |

## 2. G08, serie de fondo mientras habla: ¿se sigue cerrando por el tope?

| Variante | Voz según el detector | Segmentos | Cierres por silencio / tope / fin | Duración de los segmentos (s) |
|---|---|---|---|---|
| `parakeet-0.8-rms-0.008` | 90.0 % | 3 | 0 / 2 / 1 | 10.0, 10.0, 7.7 |
| `parakeet-0.8-silero-0.5` | 80.9 % | 4 | 2 / 1 / 1 | 5.6, 5.5, 10.0, 5.2 |
| `parakeet-0.5-silero-0.5` | 80.9 % | 4 | 3 / 1 / 0 | 5.2, 5.2, 10.0, 5.0 |
| `parakeet-0.3-silero-0.5` | 80.9 % | 5 | 4 / 1 / 0 | 5.0, 2.2, 2.8, 10.0, 4.8 |
| `parakeet-0.5-silero-0.9` | 71.1 % | 5 | 4 / 1 / 0 | 5.2, 5.2, 3.5, 10.0, 0.7 |
| `parakeet-0.3-silero-0.9` | 71.1 % | 6 | 6 / 0 / 0 | 5.0, 2.1, 2.8, 3.3, 5.2, 5.3 |

## 3. Todas las grabaciones con texto (20)

| Variante | Segmentos abiertos | Descartados sin ASR (< 0,3 s de voz) | Cierres por tope | Llamadas al ASR (borradores + finales) | Audio al ASR (s) | Tiempo de ASR (s) |
|---|---|---|---|---|---|---|
| `parakeet-0.8-rms-0.008` | 103 | 2 | 6 | 734 | 2583 | 123.8 |
| `parakeet-0.8-silero-0.5` | 75 | 1 | 33 | 941 | 4655 | 219.0 |
| `parakeet-0.5-silero-0.5` | 79 | 0 | 29 | 937 | 4436 | 209.4 |
| `parakeet-0.3-silero-0.5` | 86 | 0 | 26 | 929 | 4275 | 202.7 |
| `parakeet-0.5-silero-0.9` | 107 | 2 | 5 | 787 | 2715 | 131.7 |
| `parakeet-0.3-silero-0.9` | 125 | 1 | 1 | 770 | 2275 | 114.2 |

## 4. Demora del detector contra el RMS 0,008 y costo por bloque

Desfase = flanco del detector − flanco RMS más cercano (± 0,6 s), en las 20 grabaciones con texto; positivo es que el detector llega después. El costo es solo la decisión voz/silencio de cada bloque de 40 ms, sin el ASR.

| Variante | Desfase al empezar la voz: mediana (p10–p90) s | Desfase al terminar: mediana (p10–p90) s | Decisión por bloque: mediana / p95 / máx. (ms) | % de los 40 ms (mediana) |
|---|---|---|---|---|
| `parakeet-0.8-rms-0.008` | +0.00 (+0.00 a +0.00), n=475 | +0.00 (+0.00 a +0.00), n=475 | 0.004 / 0.037 / 1.68 | 0.01 % |
| `parakeet-0.8-silero-0.5` | +0.04 (+0.00 a +0.08), n=86 | +0.06 (-0.34 a +0.52), n=44 | 0.112 / 0.248 / 5.93 | 0.28 % |
| `parakeet-0.5-silero-0.5` | +0.04 (+0.00 a +0.08), n=86 | +0.06 (-0.34 a +0.52), n=44 | 0.112 / 0.251 / 26.54 | 0.28 % |
| `parakeet-0.3-silero-0.5` | +0.04 (+0.00 a +0.08), n=86 | +0.06 (-0.34 a +0.52), n=44 | 0.111 / 0.237 / 32.22 | 0.28 % |
| `parakeet-0.5-silero-0.9` | +0.04 (+0.04 a +0.08), n=157 | +0.12 (+0.00 a +0.40), n=141 | 0.110 / 0.228 / 7.41 | 0.27 % |
| `parakeet-0.3-silero-0.9` | +0.04 (+0.04 a +0.08), n=157 | +0.12 (+0.00 a +0.40), n=141 | 0.111 / 0.268 / 22.28 | 0.28 % |

## 5. Inicios de palabra

Frases (de las 100 con texto) cuya primera palabra no aparece entre las dos primeras de la transcripción, según el reparto por frases de `medir_voz_real.py`. Incluye errores del modelo, no solo cortes.

| Variante | Frases con la primera palabra perdida | «Compartí pantalla» (toma: lo que salió) |
|---|---|---|
| `parakeet-0.8-rms-0.008` | 10/100 | t2: «la pantalla y entra a la configuración de la cuenta Yot.» · t3: «la pantalla y entra a la configuración de la cuenta Yot.» |
| `parakeet-0.8-silero-0.5` | 15/100 | t2: «la pantalla y entra a la configuración de la cuenta yo te llevo You can do it.» · t3: «la pantalla y entra a la configuración de la cuenta YoteGio.» |
| `parakeet-0.5-silero-0.5` | 14/100 | t2: «la pantalla y entrar la configuración de la cuenta. Yo te g» · t3: «la pantalla y entra a la configuración de la cuenta YoteGio.» |
| `parakeet-0.3-silero-0.5` | 11/100 | t2: «la pantalla y entra a la configuración de la cuenta Yote» · t3: «la pantalla y entra a la configuración de la cuenta YoteGio.» |
| `parakeet-0.5-silero-0.9` | 9/100 | t2: «la pantalla y entra a la configuración de la cuenta Yote» · t3: «la pantalla y entra la configuración de la cuenta Yotg.» |
| `parakeet-0.3-silero-0.9` | 12/100 | t2: «la pantalla y entrar a la configuración de la cuenta Yote G» · t3: «la pantalla y entra a la configuración de la cuenta YTGU.» |

El segmento de «pantalla» transcripto otra vez con más audio previo (mismo reconocedor, sin el corte):

| Variante | Grabación | Audio previo extra (s) | Lo que salió |
|---|---|---|---|
| `parakeet-0.8-rms-0.008` | G16 tele apagada (toma 2) | 0.0 | «compartir la pantalla y entra la configuración de la cuenta Yot.» |
| `parakeet-0.8-rms-0.008` | G16 tele apagada (toma 2) | 0.3 | «compartir la pantalla y entra la configuración de la cuenta yo te gui» |
| `parakeet-0.8-rms-0.008` | G16 tele apagada (toma 2) | 0.6 | «compartir la pantalla y entrar a la configuración de la cuenta yo te g» |
| `parakeet-0.8-rms-0.008` | G16 conf. panel 0.8/0.008 (toma 3) | 0.0 | «Compartir la pantalla y entra a la configuración de la cuenta Yot.» |
| `parakeet-0.8-rms-0.008` | G16 conf. panel 0.8/0.008 (toma 3) | 0.3 | «Compartir la pantalla y entrar a la configuración de la cuenta Yotgio.» |
| `parakeet-0.8-rms-0.008` | G16 conf. panel 0.8/0.008 (toma 3) | 0.6 | «Compartir la pantalla y entra a la configuración de la cuenta Yotg.» |
| `parakeet-0.8-silero-0.5` | G16 tele apagada (toma 2) | 0.0 | «te mando la foto de mi cumple de mi sobrino cuando llega a casa compartir la pantalla y entra a la configuración de la cuenta yo te llevo» |
| `parakeet-0.8-silero-0.5` | G16 tele apagada (toma 2) | 0.3 | «te mando la foto de mi cumple de mi sobrino cuando llega a casa compartir la pantalla y entra la configuración de la cuenta yo te» |
| `parakeet-0.8-silero-0.5` | G16 tele apagada (toma 2) | 0.6 | «Te mando la foto de mi cumple de mi sobrino cuando llega a casa. Compartir la pantalla y entra a la configuración de la cuenta.» |
| `parakeet-0.8-silero-0.5` | G16 conf. panel 0.8/0.008 (toma 3) | 0.0 | «cuando llega a casa. Compartir la pantalla y entra a la configuración de la cuenta YoteGio.» |
| `parakeet-0.8-silero-0.5` | G16 conf. panel 0.8/0.008 (toma 3) | 0.3 | «sobrino cuando llega a casa compartir la pantalla y entra a la configuración de la cuenta Yot.» |
| `parakeet-0.8-silero-0.5` | G16 conf. panel 0.8/0.008 (toma 3) | 0.6 | «mi sobrino cuando llega a casa. Compartir la pantalla y entra a la configuración de la cuenta Yot.» |
| `parakeet-0.5-silero-0.5` | G16 tele apagada (toma 2) | 0.0 | «Compartir la pantalla y entrar la configuración de la cuenta. Yo te g» |
| `parakeet-0.5-silero-0.5` | G16 tele apagada (toma 2) | 0.3 | «compartir la pantalla y entra a la configuración de la cuenta yo te gui» |
| `parakeet-0.5-silero-0.5` | G16 tele apagada (toma 2) | 0.6 | «compartir la pantalla y entra a la configuración de la cuenta yo te gui» |
| `parakeet-0.5-silero-0.5` | G16 conf. panel 0.8/0.008 (toma 3) | 0.0 | «cuando llega a casa. Compartir la pantalla y entra a la configuración de la cuenta YoteGio.» |
| `parakeet-0.5-silero-0.5` | G16 conf. panel 0.8/0.008 (toma 3) | 0.3 | «sobrino cuando llega a casa compartir la pantalla y entra a la configuración de la cuenta Yot.» |
| `parakeet-0.5-silero-0.5` | G16 conf. panel 0.8/0.008 (toma 3) | 0.6 | «mi sobrino cuando llega a casa. Compartir la pantalla y entra a la configuración de la cuenta Yot.» |
| `parakeet-0.3-silero-0.5` | G16 tele apagada (toma 2) | 0.0 | «compartir la pantalla y entra a la configuración de la cuenta Yote» |
| `parakeet-0.3-silero-0.5` | G16 tele apagada (toma 2) | 0.3 | «compartir la pantalla y entrar a la configuración de la cuenta yo te gui» |
| `parakeet-0.3-silero-0.5` | G16 tele apagada (toma 2) | 0.6 | «compartir la pantalla y entra la configuración de la cuenta yo te g» |
| `parakeet-0.3-silero-0.5` | G16 conf. panel 0.8/0.008 (toma 3) | 0.0 | «cuando llega a casa. Compartir la pantalla y entra a la configuración de la cuenta YoteGio.» |
| `parakeet-0.3-silero-0.5` | G16 conf. panel 0.8/0.008 (toma 3) | 0.3 | «sobrino cuando llega a casa compartir la pantalla y entra a la configuración de la cuenta Yot.» |
| `parakeet-0.3-silero-0.5` | G16 conf. panel 0.8/0.008 (toma 3) | 0.6 | «mi sobrino cuando llega a casa. Compartir la pantalla y entra a la configuración de la cuenta Yot.» |
| `parakeet-0.5-silero-0.9` | G16 tele apagada (toma 2) | 0.0 | «compartir la pantalla y entra a la configuración de la cuenta Yote» |
| `parakeet-0.5-silero-0.9` | G16 tele apagada (toma 2) | 0.3 | «compartir la pantalla y entrar a la configuración de la cuenta yo te g» |
| `parakeet-0.5-silero-0.9` | G16 tele apagada (toma 2) | 0.6 | «compartir la pantalla y entra la configuración de la cuenta yo te g» |
| `parakeet-0.5-silero-0.9` | G16 conf. panel 0.8/0.008 (toma 3) | 0.0 | «Compartir la pantalla y entra la configuración de la cuenta Yotg.» |
| `parakeet-0.5-silero-0.9` | G16 conf. panel 0.8/0.008 (toma 3) | 0.3 | «Compartir la pantalla y entra a la configuración de la cuenta Yotg.» |
| `parakeet-0.5-silero-0.9` | G16 conf. panel 0.8/0.008 (toma 3) | 0.6 | «Compartir la pantalla y entra a la configuración de la cuenta Yot.» |
| `parakeet-0.3-silero-0.9` | G16 tele apagada (toma 2) | 0.0 | «compartir la pantalla y entrar a la configuración de la cuenta Yote G» |
| `parakeet-0.3-silero-0.9` | G16 tele apagada (toma 2) | 0.3 | «compartir la pantalla y entrar a la configuración de la cuenta yo te g» |
| `parakeet-0.3-silero-0.9` | G16 tele apagada (toma 2) | 0.6 | «compartir la pantalla y entra la configuración de la cuenta yo te g» |
| `parakeet-0.3-silero-0.9` | G16 conf. panel 0.8/0.008 (toma 3) | 0.0 | «Compartir la pantalla y entra a la configuración de la cuenta YTGU.» |
| `parakeet-0.3-silero-0.9` | G16 conf. panel 0.8/0.008 (toma 3) | 0.3 | «Compartir la pantalla y entra a la configuración de la cuenta Yot.» |
| `parakeet-0.3-silero-0.9` | G16 conf. panel 0.8/0.008 (toma 3) | 0.6 | «Compartir la pantalla y entra a la configuración de la cuenta YoteGui.» |

Primeras palabras perdidas, por variante:

- `parakeet-0.8-rms-0.008`: t1 «Ñaño,» → «Al pedo te…»; t1 «Dejá» → «Deje el miso…»; t1 «Mandame» → «Máme el código…»; t1 «Ñaño,» → «Al pedo te…»; t2 «Ñaño,» → «Al pedo te…»; t2 «Abrí» → «abre el enlace…»; t2 «Te» → «Que llevo un…»; t3 «Ñaño,» → «Al pedo te…»; t3 «Te» → «Testorivo del Galicia,…»; t3 «Mandame» → «Máme el código…»
- `parakeet-0.8-silero-0.5`: t1 «Me» → «el codo desde…»; t1 «Instalá» → «Intalánides Y dame…»; t1 «Ñaño,» → «Al pedo te…»; t1 «Abrí» → «Y el enlace…»; t1 «Dejá» → «Deje el miso…»; t1 «Ñaño,» → «Al pedo te…»; t1 «Abrí» → «abre el enlace…»; t2 «Ñaño,» → «Al pedo te…»; t2 «Abrí» → «Abre el enlace…»; t2 «Tu» → «…»; t2 «Te» → «Que llevo un…»; t3 «Ñaño,» → «Al pedo te…»; t3 «Tu» → «Pásame el pin…»; t3 «Te» → «Destrivo del Galicia,…»; t3 «Con» → «5 lucas no…»
- `parakeet-0.5-silero-0.5`: t1 «Me» → «el codo desde…»; t1 «Instalá» → «Intalánides Y dame…»; t1 «Ñaño,» → «Al pedo te…»; t1 «Abrí» → «Y el enlace…»; t1 «Dejá» → «Deje el miso…»; t1 «Ñaño,» → «Al pedo te…»; t1 «Abrí» → «abre el enlace…»; t2 «Ñaño,» → «Al pedo te…»; t2 «Abrí» → «Abre el enlace…»; t2 «Te» → «Que llevo un…»; t3 «Ñaño,» → «Al pedo te…»; t3 «Tu» → «Pásame el pin…»; t3 «Te» → «Destrivo del Galicia,…»; t3 «Con» → «5 lucas no…»
- `parakeet-0.3-silero-0.5`: t1 «Instalá» → «ni des y…»; t1 «Ñaño,» → «Al pedo te…»; t1 «Abrí» → «Y el enlace…»; t1 «Dejá» → «Deje el miso…»; t1 «Ñaño,» → «Al pedo te…»; t2 «Ñaño,» → «Al pedo te…»; t2 «Abrí» → «Abre el enlace…»; t2 «Te» → «Que llegó un…»; t3 «Ñaño,» → «Al pedo te…»; t3 «Tu» → «Pásame el pin…»; t3 «Te» → «Destrivo del Galicia,…»
- `parakeet-0.5-silero-0.9`: t1 «Ñaño,» → «Al pedo te…»; t1 «Te» → «Le llevo un…»; t1 «Dejá» → «Deje el miso…»; t1 «Ñaño,» → «Al pedo ta…»; t1 «Abrí» → «abre el enlace…»; t2 «Ñaño,» → «Al pedo te…»; t2 «Abrí» → «abre el enlace…»; t2 «Te» → «que llevo un…»; t3 «Ñaño,» → «Al pedo te…»
- `parakeet-0.3-silero-0.9`: t1 «Instalá» → «ni desk y…»; t1 «Ñaño,» → «Al pedo te…»; t1 «Dejá» → «Deje el miso…»; t1 «Te» → «…»; t1 «Ñaño,» → «Al pedotas es…»; t1 «Abrí» → «abre el enlace…»; t2 «Ñaño,» → «Al pedo te…»; t2 «Abrí» → «Abre el enlace…»; t2 «Te» → «que llevo un…»; t2 «Mandame» → «Máme el código…»; t3 «Ñaño,» → «Al pedo te…»; t3 «Te» → «Destrivo del Galicia,…»

## 6. Simulación del corte sin ASR: ¿es el umbral de Silero?

Solo el corte de `MotorPorFrases` (sin Parakeet) sobre las 20 grabaciones con texto, que tienen 100 frases. Con Silero, ya en voz sigue en voz mientras la probabilidad no baje de umbral − 0,15. No mide WER ni etiquetas.

| Detector | Umbral | Corte (s) | Voz según el detector | Segmentos | Cierres por silencio | Cierres por tope |
|---|---|---|---|---|---|---|
| rms | 0.008 | 0.3 | 63.7 % | 138 | 135 | 2 |
| rms | 0.008 | 0.5 | 63.7 % | 117 | 114 | 2 |
| rms | 0.008 | 0.8 | 63.7 % | 103 | 95 | 6 |
| silero | 0.5 | 0.3 | 84.8 % | 86 | 53 | 26 |
| silero | 0.5 | 0.5 | 84.8 % | 79 | 41 | 29 |
| silero | 0.5 | 0.8 | 84.8 % | 75 | 29 | 33 |
| silero | 0.7 | 0.3 | 80.0 % | 99 | 75 | 18 |
| silero | 0.7 | 0.5 | 80.0 % | 85 | 55 | 23 |
| silero | 0.7 | 0.8 | 80.0 % | 81 | 42 | 31 |
| silero | 0.85 | 0.3 | 74.3 % | 119 | 113 | 4 |
| silero | 0.85 | 0.5 | 74.3 % | 100 | 83 | 15 |
| silero | 0.85 | 0.8 | 74.3 % | 87 | 60 | 23 |
| silero | 0.9 | 0.3 | 71.9 % | 125 | 123 | 1 |
| silero | 0.9 | 0.5 | 71.9 % | 107 | 100 | 5 |
| silero | 0.9 | 0.8 | 71.9 % | 87 | 65 | 19 |

## 7. Reproducir

```bash
python experiments/asr-local/comparar_vad.py --pruebas /Users/lucianogrosso/bitacora_tesis-voip-asr/experiments/voip/llamadas --corrida experiments/asr-local/corridas/2026-10-29_voz-real_parakeet-silero-vs-rms
python experiments/asr-local/comparar_vad.py --rehacer-resumen --salida experiments/asr-local/corridas/2026-10-29_voz-real_vad-extras --pruebas /Users/lucianogrosso/bitacora_tesis-voip-asr/experiments/voip/llamadas --corrida experiments/asr-local/corridas/2026-10-29_voz-real_parakeet-silero-vs-rms --simular-umbrales 0.5,0.7,0.85,0.9
```

Código: `38bb680e9e82c331fe9307f3b7046493e730ef6e` (LucianoGrosso13/silero-vs-rms-94, con cambios sin commit). Detalle por segmento en `extras.json`.
