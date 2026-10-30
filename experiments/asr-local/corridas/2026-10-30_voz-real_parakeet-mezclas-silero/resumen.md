# Resumen de la medición del ASR con voz real

> **ADVERTENCIA: son una o dos voces del equipo, sin piloto: no es evidencia de rendimiento general ni cierra D09** (ver [MAPA-DECISIONES.md](../../../../docs/gestion/MAPA-DECISIONES.md#d09--elegir-asr-y-detector)). Plan: [PLAN-VOZ-REAL.md](../../PLAN-VOZ-REAL.md). Issue #94.

> **Nota de esta corrida:** Silero VAD (sherpa-onnx, umbral 0,5) mezclado con el RMS 0,8 s / 0,008 de «Probar el ASR»: «filtro» (el RMS corta, Silero decide qué cuenta como voz) e «y» (voz si lo dicen los dos). Mismo audio, modelo, preaudio, tope y MIN_VOZ_S. Una voz (Luciano), micrófono de la Mac. Referencias del guion por bloque. Demora offline en la M1.

> **Estado: propuesta sin discutir.** Las listas de términos y jerga se usan como instrumento; D07 sigue abierta.

## 1. Datos

- Toma 1, `luciano-microfono`: 5 pruebas (5 con el bloque tal cual el guion). Bloques: 1, 2, 3, 4, 5.
- Toma 1, `luciano-pausas`: 1 pruebas (1 con el bloque tal cual el guion). Bloques: 3.
- Toma 1, `luciano-ruido-tv`: 1 pruebas (1 con el bloque tal cual el guion). Bloques: 2.
- Toma 1, `luciano-voz-baja`: 1 pruebas (1 con el bloque tal cual el guion). Bloques: 1.
- Toma 2, `luciano-microfono`: 6 pruebas (6 con el bloque tal cual el guion). Bloques: 1, 2, 3, 4, 5, 6.
- Toma 3, `luciano-microfono`: 6 pruebas (6 con el bloque tal cual el guion). Bloques: 1, 2, 3, 4, 5, 6.
- Omitidas: 0.
- Carpeta de pruebas: `/Users/lucianogrosso/bitacora_tesis-voip-asr/experiments/voip/llamadas` | CSV: `/Users/lucianogrosso/orca/workspaces/bitacora_tesis/silero-vs-rms-94/experiments/asr-local/voz-real/pruebas.csv` | audio medido: 587.4 s.

## 2. Resultado por variante (toma 2, todas las condiciones juntas)

| Variante | Frases OK | Etiquetas nuevas en negativas | Recall críticos | Recall bancos y apps | Recall jerga* | WER | CER | Segmentos finales | Demora final mediana (s) | p95 (s) | Proceso (s) | RTF | p95 / máx. por bloque (ms) | Memoria pico (MB) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `parakeet-0.8-rms-0.008` | 28/30 | 0 | 88.9% | 88.9% | 46.7% | 13.3% | 5.5% | 30 | 1.06 | 1.16 | 35.13 | 0.192 | 77.5 / 448.7 | 887 |
| `parakeet-0.8-rms-0.008-filtro-silero-0.5` | 28/30 | 0 | 88.9% | 88.9% | 46.7% | 13.3% | 5.5% | 30 | 1.06 | 1.16 | 35.18 | 0.192 | 76.0 / 437.0 | 1052 |
| `parakeet-0.8-rms-0.008-y-silero-0.5` | 28/30 | 0 | 88.9% | 88.9% | 46.7% | 14.3% | 6.2% | 31 | 1.06 | 1.16 | 36.65 | 0.201 | 97.0 / 461.3 | 984 |

\* La jerga es informativa, sin umbral. «Frases OK» = frases cuyas etiquetas de `reglas.py` sobre la transcripción son iguales a las de la referencia. La demora es offline (ver sección 6).

## 3. Regla del plan §2 (toma 2)

Cada corte y umbral contra `parakeet-0.8-rms-0.008` (la referencia de esta corrida), en la toma 2, con las cuatro condiciones de la regla. No se elige sola: «pasa» quiere decir que cumple las cuatro.

| Variante | Frases más | Etiquetas nuevas en negativas | Demora extra (s) | WER extra (puntos) | ¿Pasa? |
|---|---|---|---|---|---|
| `parakeet-0.8-rms-0.008-filtro-silero-0.5` | +0 ✗ | +0 | 0.00 | +0.0 | no |
| `parakeet-0.8-rms-0.008-y-silero-0.5` | +0 ✗ | +0 | -0.00 | +1.0 | no |

## 4. Por toma y condición

### toma1/luciano-microfono

| Variante | Frases OK | Etiquetas nuevas en negativas | Recall críticos | WER | Segmentos | Demora mediana (s) |
|---|---|---|---|---|---|---|
| `parakeet-0.8-rms-0.008` | 23/25 | 0 | 85.0% | 18.5% | 22 | 1.06 |
| `parakeet-0.8-rms-0.008-filtro-silero-0.5` | 23/25 | 0 | 85.0% | 18.5% | 22 | 1.06 |
| `parakeet-0.8-rms-0.008-y-silero-0.5` | 22/25 | 0 | 83.3% | 19.1% | 22 | 1.05 |

### toma1/luciano-pausas

| Variante | Frases OK | Etiquetas nuevas en negativas | Recall críticos | WER | Segmentos | Demora mediana (s) |
|---|---|---|---|---|---|---|
| `parakeet-0.8-rms-0.008` | 5/5 | 0 | 93.3% | 20.3% | 11 | 0.96 |
| `parakeet-0.8-rms-0.008-filtro-silero-0.5` | 5/5 | 0 | 93.3% | 20.3% | 11 | 0.96 |
| `parakeet-0.8-rms-0.008-y-silero-0.5` | 5/5 | 0 | 93.3% | 23.4% | 11 | 0.96 |

### toma1/luciano-ruido-tv

| Variante | Frases OK | Etiquetas nuevas en negativas | Recall críticos | WER | Segmentos | Demora mediana (s) |
|---|---|---|---|---|---|---|
| `parakeet-0.8-rms-0.008` | 5/5 | 0 | 85.7% | 22.7% | 3 | 0.49 |
| `parakeet-0.8-rms-0.008-filtro-silero-0.5` | 5/5 | 0 | 85.7% | 22.7% | 3 | 0.53 |
| `parakeet-0.8-rms-0.008-y-silero-0.5` | 5/5 | 0 | 92.9% | 19.7% | 4 | 0.26 |

### toma1/luciano-voz-baja

| Variante | Frases OK | Etiquetas nuevas en negativas | Recall críticos | WER | Segmentos | Demora mediana (s) |
|---|---|---|---|---|---|---|
| `parakeet-0.8-rms-0.008` | 5/5 | 0 | 87.5% | 4.7% | 5 | 1.03 |
| `parakeet-0.8-rms-0.008-filtro-silero-0.5` | 5/5 | 0 | 87.5% | 4.7% | 5 | 1.03 |
| `parakeet-0.8-rms-0.008-y-silero-0.5` | 5/5 | 0 | 87.5% | 4.7% | 5 | 1.03 |

### toma2/luciano-microfono

| Variante | Frases OK | Etiquetas nuevas en negativas | Recall críticos | WER | Segmentos | Demora mediana (s) |
|---|---|---|---|---|---|---|
| `parakeet-0.8-rms-0.008` | 28/30 | 0 | 88.9% | 13.3% | 30 | 1.06 |
| `parakeet-0.8-rms-0.008-filtro-silero-0.5` | 28/30 | 0 | 88.9% | 13.3% | 30 | 1.06 |
| `parakeet-0.8-rms-0.008-y-silero-0.5` | 28/30 | 0 | 88.9% | 14.3% | 31 | 1.06 |

### toma3/luciano-microfono

| Variante | Frases OK | Etiquetas nuevas en negativas | Recall críticos | WER | Segmentos | Demora mediana (s) |
|---|---|---|---|---|---|---|
| `parakeet-0.8-rms-0.008` | 28/30 | 0 | 90.3% | 13.0% | 28 | 1.05 |
| `parakeet-0.8-rms-0.008-filtro-silero-0.5` | 28/30 | 0 | 90.3% | 13.0% | 28 | 1.04 |
| `parakeet-0.8-rms-0.008-y-silero-0.5` | 28/30 | 0 | 90.3% | 14.8% | 28 | 1.05 |

## 5. Recall por término crítico (toma 2)

| Término | En la referencia | `parakeet-0.8-rms-0.008` |
|---|---|---|
| `abri el enlace` | 1 | 1/1 |
| `acceso remoto` | 1 | 1/1 |
| `alias` | 2 | 2/2 |
| `anydesk` | 1 | 0/1 |
| `autoriz` | 2 | 2/2 |
| `autoriza` | 2 | 2/2 |
| `cbu` | 2 | 2/2 |
| `clave` | 3 | 3/3 |
| `codigo` | 4 | 4/4 |
| `compart` | 1 | 0/1 |
| `comparti pantalla` | 1 | 0/1 |
| `configuracion` | 1 | 1/1 |
| `confirmame` | 1 | 1/1 |
| `cvv` | 1 | 0/1 |
| `dame` | 5 | 5/5 |
| `decime` | 2 | 1/2 |
| `dni` | 2 | 1/2 |
| `domicilio` | 1 | 1/1 |
| `efectivo` | 2 | 2/2 |
| `instal` | 2 | 2/2 |
| `instala` | 2 | 2/2 |
| `link` | 2 | 2/2 |
| `luca` | 2 | 2/2 |
| `mandame` | 3 | 3/3 |
| `mango` | 1 | 1/1 |
| `necesito que` | 1 | 1/1 |
| `numeros` | 1 | 1/1 |
| `otp` | 1 | 1/1 |
| `paga` | 2 | 2/2 |
| `pago` | 2 | 2/2 |
| `pasame` | 6 | 6/6 |
| `pin` | 2 | 2/2 |
| `plata` | 2 | 2/2 |
| `seis digitos` | 1 | 1/1 |
| `tenes que` | 2 | 1/2 |
| `token` | 1 | 0/1 |
| `transferencia` | 1 | 1/1 |
| `transferi` | 2 | 2/2 |
| `verificacion` | 1 | 1/1 |

## 5b. Sustituciones frecuentes de la toma 1 (candidatas al diccionario)

Lo que salió con `parakeet-0.8-rms-0.008` → lo que se dijo. Revisá cada una antes de pasarla a `voz-real/diccionario.csv`.

| Salió | Se dijo | Veces |
|---|---|---|
| `el` | `al` | 3 |
| `hacer` | `hacé` | 2 |
| `la` | `le` | 2 |
| `se` | `seas` | 2 |
| `safa` | `zafás` | 2 |
| `abre` | `abrí` | 2 |
| `pedo` | `ñudo` | 2 |
| `hace` | `hacés` | 2 |
| `llevo` | `llegó` | 2 |
| `transferir` | `y` | 1 |
| `45` | `cinco` | 1 |
| `servicio` | `cbu` | 1 |
| `matro` | `macro` | 1 |
| `confirmen` | `confirmes` | 1 |
| `avisan` | `avises` | 1 |
| `dar` | `duele` | 1 |
| `jugo` | `jugué` | 1 |
| `sean` | `sea` | 1 |
| `ni` | `instalá` | 1 |
| `desk` | `anydesk` | 1 |
| `autorizar` | `autorizá` | 1 |
| `juazo` | `guaso` | 1 |
| `3` | `tres` | 1 |
| `4` | `cuatro` | 1 |
| `1` | `uno` | 1 |
| `9` | `nueve` | 1 |
| `2` | `dos` | 1 |
| `7` | `siete` | 1 |
| `abrir` | `abrí` | 1 |
| `seguridad` | `cvv` | 1 |

## 6. Cómo se midió

- El audio guardado (canal protegida del estéreo) se pasa por cada variante en bloques de 40 ms con 2 hilos, igual que el servidor del panel.
- **Demora de la frase final** = `disponible_s − fin de la voz`, con el reloj simulado de `asr_local.py` (`disponible_s` suma el tiempo de proceso de cada bloque) y el fin de la voz en el último bloque con RMS sobre el umbral. No incluye red ni pantalla. La final que sale al cerrar la prueba cuenta como segmento pero no entra en la demora. Whisper va por lotes y no tiene demora comparable.
- **Proceso, p95 por bloque y memoria pico**: el proceso suma el tiempo de todos los bloques; el p95 es el máximo entre pruebas de los p95 por bloque; la memoria pico es la del subproceso de esa variante (incluye la carga del modelo) y no se puede separar por condición.
- La ganancia y el umbral RMS **de captura** ya quedaron en el audio: offline solo se rehacen el umbral del motor (`rms-*`) y una normalización de nivel (`norm`).
- Los hotwords usan un `bpe.vocab` sintético con puntaje `-(ln(id+2)+3)`; `beam+hotwords-id` repite el `-id` del plan. Ver `hotwords.py`.
- Whisper con ayudas: `hotwords` = términos críticos, bancos y apps; `initial_prompt` = la jerga.

## 7. Reproducir

```bash
python experiments/asr-local/medir_voz_real.py --solo-parakeet --contra-parakeet parakeet-0.8-rms-0.008 --variantes parakeet-0.8-rms-0.008-filtro-silero-0.5,parakeet-0.8-rms-0.008-y-silero-0.5 --pruebas /Users/lucianogrosso/bitacora_tesis-voip-asr/experiments/voip/llamadas --etiqueta parakeet-mezclas-silero --nota 'Silero VAD (sherpa-onnx, umbral 0,5) mezclado con el RMS 0,8 s / 0,008 de «Probar el ASR»: «filtro» (el RMS corta, Silero decide qué cuenta como voz) e «y» (voz si lo dicen los dos). Mismo audio, modelo, preaudio, tope y MIN_VOZ_S. Una voz (Luciano), micrófono de la Mac. Referencias del guion por bloque. Demora offline en la M1.'
```

Código: `9c4deb621414f053ac35c059efa31988e1d44a15` (LucianoGrosso13/silero-vs-rms-94, limpio). Detalle completo en `manifiesto.json`; textos por frase en `frases.jsonl`.
