# Resumen de la medición del ASR con voz real

> **ADVERTENCIA: son una o dos voces del equipo, sin piloto: no es evidencia de rendimiento general ni cierra D09** (ver [MAPA-DECISIONES.md](../../../../docs/gestion/MAPA-DECISIONES.md#d09--elegir-asr-y-detector)). Plan: [PLAN-VOZ-REAL.md](../../PLAN-VOZ-REAL.md). Issue #94.

> **Nota de esta corrida:** Confirmación: la toma 3 (G11–G16 de nuevo) se grabó en vivo con 0,8 s / 0,008, elegido mirando la toma 2 de 2026-10-29_voz-real_parakeet-cortes. Una voz (Luciano), micrófono de la Mac. Referencias del guion por bloque.

> **Estado: propuesta sin discutir.** Las listas de términos y jerga se usan como instrumento; D07 sigue abierta.

## 1. Datos

- Toma 1, `luciano-microfono`: 5 pruebas (5 con el bloque tal cual el guion). Bloques: 1, 2, 3, 4, 5.
- Toma 1, `luciano-pausas`: 1 pruebas (1 con el bloque tal cual el guion). Bloques: 3.
- Toma 1, `luciano-ruido-tv`: 1 pruebas (1 con el bloque tal cual el guion). Bloques: 2.
- Toma 1, `luciano-voz-baja`: 1 pruebas (1 con el bloque tal cual el guion). Bloques: 1.
- Toma 2, `luciano-microfono`: 6 pruebas (6 con el bloque tal cual el guion). Bloques: 1, 2, 3, 4, 5, 6.
- Toma 3, `luciano-microfono`: 6 pruebas (6 con el bloque tal cual el guion). Bloques: 1, 2, 3, 4, 5, 6.
- Omitidas: 0.
- Carpeta de pruebas: `/Users/lucianogrosso/bitacora_tesis-voip-asr/experiments/voip/llamadas` | CSV: `/Users/lucianogrosso/bitacora_tesis-laboratorio-luciano/experiments/asr-local/voz-real/pruebas.csv` | audio medido: 587.4 s.

## 2. Resultado por variante (toma 3, todas las condiciones juntas)

| Variante | Frases OK | Etiquetas nuevas en negativas | Recall críticos | Recall bancos y apps | Recall jerga* | WER | CER | Segmentos finales | Demora final mediana (s) | p95 (s) | Proceso (s) | RTF | p95 / máx. por bloque (ms) | Memoria pico (MB) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `parakeet-0.9-rms-0.003` | 28/30 | 0 | 88.9% | 77.8% | 33.3% | 18.3% | 10.6% | 21 | 0.95 | 1.33 | 57.32 | 0.347 | 165.3 / 470.0 | 1086 |
| `parakeet-0.5-rms-0.008` | 27/30 | 0 | 88.9% | 77.8% | 40.0% | 16.8% | 7.5% | 34 | 0.73 | 0.78 | 29.61 | 0.179 | 76.3 / 271.3 | 979 |
| `parakeet-0.8-rms-0.008` | 28/30 | 0 | 90.3% | 88.9% | 33.3% | 13.0% | 5.2% | 28 | 1.03 | 1.10 | 36.52 | 0.221 | 84.2 / 451.9 | 1078 |

\* La jerga es informativa, sin umbral. «Frases OK» = frases cuyas etiquetas de `reglas.py` sobre la transcripción son iguales a las de la referencia. La demora es offline (ver sección 6).

## 3. Regla del plan §2 (toma 3)

Cada corte y umbral contra `parakeet-0.9-rms-0.003` (el del panel), en la toma 3, con las cuatro condiciones de la regla. No se elige sola: «pasa» quiere decir que cumple las cuatro.

| Variante | Frases más | Etiquetas nuevas en negativas | Demora extra (s) | WER extra (puntos) | ¿Pasa? |
|---|---|---|---|---|---|
| `parakeet-0.5-rms-0.008` | -1 ✗ | +0 | -0.22 | -1.5 | no |
| `parakeet-0.8-rms-0.008` | +0 ✗ | +0 | 0.09 | -5.3 | no |

## 4. Por toma y condición

### toma1/luciano-microfono

| Variante | Frases OK | Etiquetas nuevas en negativas | Recall críticos | WER | Segmentos | Demora mediana (s) |
|---|---|---|---|---|---|---|
| `parakeet-0.9-rms-0.003` | 23/25 | 0 | 85.0% | 18.8% | 20 | 1.15 |
| `parakeet-0.5-rms-0.008` | 23/25 | 0 | 86.7% | 18.2% | 25 | 0.74 |
| `parakeet-0.8-rms-0.008` | 23/25 | 0 | 85.0% | 18.5% | 22 | 1.05 |

### toma1/luciano-pausas

| Variante | Frases OK | Etiquetas nuevas en negativas | Recall críticos | WER | Segmentos | Demora mediana (s) |
|---|---|---|---|---|---|---|
| `parakeet-0.9-rms-0.003` | 5/5 | 0 | 93.3% | 21.9% | 8 | 1.07 |
| `parakeet-0.5-rms-0.008` | 5/5 | 0 | 100.0% | 17.2% | 11 | 0.64 |
| `parakeet-0.8-rms-0.008` | 5/5 | 0 | 93.3% | 20.3% | 11 | 0.95 |

### toma1/luciano-ruido-tv

| Variante | Frases OK | Etiquetas nuevas en negativas | Recall críticos | WER | Segmentos | Demora mediana (s) |
|---|---|---|---|---|---|---|
| `parakeet-0.9-rms-0.003` | 5/5 | 0 | 85.7% | 22.7% | 3 | 0.74 |
| `parakeet-0.5-rms-0.008` | 5/5 | 0 | 85.7% | 24.2% | 3 | 0.56 |
| `parakeet-0.8-rms-0.008` | 5/5 | 0 | 85.7% | 22.7% | 3 | 0.48 |

### toma1/luciano-voz-baja

| Variante | Frases OK | Etiquetas nuevas en negativas | Recall críticos | WER | Segmentos | Demora mediana (s) |
|---|---|---|---|---|---|---|
| `parakeet-0.9-rms-0.003` | 5/5 | 0 | 87.5% | 4.7% | 4 | 1.14 |
| `parakeet-0.5-rms-0.008` | 5/5 | 0 | 87.5% | 4.7% | 5 | 0.74 |
| `parakeet-0.8-rms-0.008` | 5/5 | 0 | 87.5% | 4.7% | 5 | 1.03 |

### toma2/luciano-microfono

| Variante | Frases OK | Etiquetas nuevas en negativas | Recall críticos | WER | Segmentos | Demora mediana (s) |
|---|---|---|---|---|---|---|
| `parakeet-0.9-rms-0.003` | 27/30 | 0 | 84.7% | 20.8% | 24 | 1.15 |
| `parakeet-0.5-rms-0.008` | 28/30 | 0 | 86.1% | 13.8% | 36 | 0.73 |
| `parakeet-0.8-rms-0.008` | 28/30 | 0 | 88.9% | 13.3% | 30 | 1.06 |

### toma3/luciano-microfono

| Variante | Frases OK | Etiquetas nuevas en negativas | Recall críticos | WER | Segmentos | Demora mediana (s) |
|---|---|---|---|---|---|---|
| `parakeet-0.9-rms-0.003` | 28/30 | 0 | 88.9% | 18.3% | 21 | 0.95 |
| `parakeet-0.5-rms-0.008` | 27/30 | 0 | 88.9% | 16.8% | 34 | 0.73 |
| `parakeet-0.8-rms-0.008` | 28/30 | 0 | 90.3% | 13.0% | 28 | 1.03 |

## 5. Recall por término crítico (toma 3)

| Término | En la referencia | `parakeet-0.9-rms-0.003` |
|---|---|---|
| `abri el enlace` | 1 | 1/1 |
| `acceso remoto` | 1 | 1/1 |
| `alias` | 2 | 2/2 |
| `anydesk` | 1 | 0/1 |
| `autoriz` | 2 | 1/2 |
| `autoriza` | 2 | 1/2 |
| `cbu` | 2 | 2/2 |
| `clave` | 3 | 3/3 |
| `codigo` | 4 | 4/4 |
| `compart` | 1 | 0/1 |
| `comparti pantalla` | 1 | 0/1 |
| `configuracion` | 1 | 1/1 |
| `confirmame` | 1 | 1/1 |
| `cvv` | 1 | 0/1 |
| `dame` | 5 | 5/5 |
| `decime` | 2 | 2/2 |
| `dni` | 2 | 2/2 |
| `domicilio` | 1 | 1/1 |
| `efectivo` | 2 | 2/2 |
| `instal` | 2 | 2/2 |
| `instala` | 2 | 2/2 |
| `link` | 2 | 2/2 |
| `luca` | 2 | 2/2 |
| `mandame` | 3 | 3/3 |
| `mango` | 1 | 0/1 |
| `necesito que` | 1 | 1/1 |
| `numeros` | 1 | 1/1 |
| `otp` | 1 | 1/1 |
| `paga` | 2 | 2/2 |
| `pago` | 2 | 2/2 |
| `pasame` | 6 | 6/6 |
| `pin` | 2 | 1/2 |
| `plata` | 2 | 2/2 |
| `seis digitos` | 1 | 1/1 |
| `tenes que` | 2 | 2/2 |
| `token` | 1 | 1/1 |
| `transferencia` | 1 | 1/1 |
| `transferi` | 2 | 2/2 |
| `verificacion` | 1 | 1/1 |

## 5b. Sustituciones frecuentes de la toma 1 (candidatas al diccionario)

Lo que salió con `parakeet-0.9-rms-0.003` → lo que se dijo. Revisá cada una antes de pasarla a `voz-real/diccionario.csv`.

| Salió | Se dijo | Veces |
|---|---|---|
| `el` | `al` | 4 |
| `hacer` | `hacé` | 2 |
| `la` | `le` | 2 |
| `safa` | `zafás` | 2 |
| `30` | `treinta` | 2 |
| `abre` | `abrí` | 2 |
| `pedo` | `ñudo` | 2 |
| `hace` | `hacés` | 2 |
| `llevo` | `llegó` | 2 |
| `transferir` | `y` | 1 |
| `45` | `cinco` | 1 |
| `servicio` | `cbu` | 1 |
| `maatro` | `macro` | 1 |
| `confirmen` | `confirmes` | 1 |
| `avise` | `avises` | 1 |
| `se` | `seas` | 1 |
| `da` | `duele` | 1 |
| `jugo` | `jugué` | 1 |
| `sean` | `sea` | 1 |
| `ni` | `instalá` | 1 |
| `desk` | `anydesk` | 1 |
| `a` | `y` | 1 |
| `autorizar` | `autorizá` | 1 |
| `juazo` | `guaso` | 1 |
| `3` | `cuatro` | 1 |
| `4` | `uno` | 1 |
| `1` | `nueve` | 1 |
| `9` | `dos` | 1 |
| `2` | `siete` | 1 |
| `7` | `abrí` | 1 |

## 6. Cómo se midió

- El audio guardado (canal protegida del estéreo) se pasa por cada variante en bloques de 40 ms con 2 hilos, igual que el servidor del panel.
- **Demora de la frase final** = `disponible_s − fin de la voz`, con el reloj simulado de `asr_local.py` (`disponible_s` suma el tiempo de proceso de cada bloque) y el fin de la voz en el último bloque con RMS sobre el umbral. No incluye red ni pantalla. La final que sale al cerrar la prueba cuenta como segmento pero no entra en la demora. Whisper va por lotes y no tiene demora comparable.
- **Proceso, p95 por bloque y memoria pico**: el proceso suma el tiempo de todos los bloques; el p95 es el máximo entre pruebas de los p95 por bloque; la memoria pico es la del subproceso de esa variante (incluye la carga del modelo) y no se puede separar por condición.
- La ganancia y el umbral RMS **de captura** ya quedaron en el audio: offline solo se rehacen el umbral del motor (`rms-*`) y una normalización de nivel (`norm`).
- Los hotwords usan un `bpe.vocab` sintético con puntaje `-(ln(id+2)+3)`; `beam+hotwords-id` repite el `-id` del plan. Ver `hotwords.py`.
- Whisper con ayudas: `hotwords` = términos críticos, bancos y apps; `initial_prompt` = la jerga.

## 7. Reproducir

```bash
python experiments/asr-local/medir_voz_real.py --solo-parakeet --variantes parakeet-0.5-rms-0.008,parakeet-0.8-rms-0.008 --toma-decision 3 --pruebas /Users/lucianogrosso/bitacora_tesis-voip-asr/experiments/voip/llamadas --etiqueta parakeet-confirmacion --nota 'Confirmación: la toma 3 (G11–G16 de nuevo) se grabó en vivo con 0,8 s / 0,008, elegido mirando la toma 2 de 2026-10-29_voz-real_parakeet-cortes. Una voz (Luciano), micrófono de la Mac. Referencias del guion por bloque.'
```

Código: `e08e409cf17379bcc01c08be36426755b22dfa6d` (laboratorio-luciano, con cambios sin commit). Detalle completo en `manifiesto.json`; textos por frase en `frases.jsonl`.
