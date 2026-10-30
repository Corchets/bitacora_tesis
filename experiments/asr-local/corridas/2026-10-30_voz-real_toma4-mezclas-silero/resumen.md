# Resumen de la medición del ASR con voz real

> **ADVERTENCIA: son una o dos voces del equipo, sin piloto: no es evidencia de rendimiento general ni cierra D09** (ver [MAPA-DECISIONES.md](../../../../docs/gestion/MAPA-DECISIONES.md#d09--elegir-asr-y-detector)). Plan: [PLAN-VOZ-REAL.md](../../PLAN-VOZ-REAL.md). Issue #94.

> **Nota de esta corrida:** Toma 4 (2026-10-30): G01-G06 leídos tres veces seguidas con parakeet-filtro, parakeet-y y parakeet-silero a la vista en el panel, más G08b con la serie de fondo. Una voz (Luciano), micrófono de la Mac. Referencias del guion por bloque. Demora offline en la M1.

> **Estado: propuesta sin discutir.** Las listas de términos y jerga se usan como instrumento; D07 sigue abierta.

## 1. Datos

- Toma 4, `luciano-microfono`: 18 pruebas (18 con el bloque tal cual el guion). Bloques: 1, 2, 3, 4, 5, 6, 1, 2, 3, 4, 5, 6, 1, 2, 3, 4, 5, 6.
- Toma 4, `luciano-ruido-tv`: 1 pruebas (1 con el bloque tal cual el guion). Bloques: 2.
- Omitidas: 20: `2026-10-29_194923-902062` (no existe la carpeta o no tiene manifiesto legible); `2026-10-29_195020-082746` (no existe la carpeta o no tiene manifiesto legible); `2026-10-29_195202-772508` (no existe la carpeta o no tiene manifiesto legible); `2026-10-29_195256-042759` (no existe la carpeta o no tiene manifiesto legible); `2026-10-29_195409-306210` (no existe la carpeta o no tiene manifiesto legible); `2026-10-29_200653-308143` (no existe la carpeta o no tiene manifiesto legible); `2026-10-29_200832-553834` (no existe la carpeta o no tiene manifiesto legible); `2026-10-29_200926-056710` (no existe la carpeta o no tiene manifiesto legible); `2026-10-29_201653-688897` (no existe la carpeta o no tiene manifiesto legible); `2026-10-29_201733-924805` (no existe la carpeta o no tiene manifiesto legible); `2026-10-29_201814-367007` (no existe la carpeta o no tiene manifiesto legible); `2026-10-29_202351-657853` (no existe la carpeta o no tiene manifiesto legible); `2026-10-29_201921-145948` (no existe la carpeta o no tiene manifiesto legible); `2026-10-29_201959-768452` (no existe la carpeta o no tiene manifiesto legible); `2026-10-29_204534-495909` (no existe la carpeta o no tiene manifiesto legible); `2026-10-29_204616-642444` (no existe la carpeta o no tiene manifiesto legible); `2026-10-29_205011-705316` (no existe la carpeta o no tiene manifiesto legible); `2026-10-29_205052-595235` (no existe la carpeta o no tiene manifiesto legible); `2026-10-29_205127-026460` (no existe la carpeta o no tiene manifiesto legible); `2026-10-29_205159-170084` (no existe la carpeta o no tiene manifiesto legible)
- Carpeta de pruebas: `../voip/llamadas` | CSV: `/Users/lucianogrosso/orca/workspaces/bitacora_tesis/silero-vs-rms-94/experiments/asr-local/voz-real/pruebas.csv` | audio medido: 483.0 s.

## 2. Resultado por variante (toma 4, todas las condiciones juntas)

| Variante | Frases OK | Etiquetas nuevas en negativas | Recall críticos | Recall bancos y apps | Recall jerga* | WER | CER | Segmentos finales | Demora final mediana (s) | p95 (s) | Proceso (s) | RTF | p95 / máx. por bloque (ms) | Memoria pico (MB) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `parakeet-0.8-rms-0.008` | 93/95 | 0 | 94.3% | 85.2% | 50.0% | 17.0% | 11.2% | 78 | 1.04 | 1.25 | 126.79 | 0.263 | 160.0 / 474.9 | 1166 |
| `parakeet-0.3-silero-0.9` | 93/95 | 0 | 93.9% | 85.2% | 50.0% | 13.4% | 6.8% | 110 | 0.55 | 1.07 | 93.90 | 0.194 | 102.3 / 455.4 | 987 |
| `parakeet-0.8-rms-0.008-filtro-silero-0.5` | 93/95 | 0 | 94.3% | 85.2% | 50.0% | 17.0% | 11.2% | 78 | 1.05 | 1.26 | 128.76 | 0.267 | 156.2 / 468.3 | 1246 |
| `parakeet-0.8-rms-0.008-y-silero-0.5` | 93/95 | 0 | 94.3% | 85.2% | 46.0% | 14.6% | 8.8% | 82 | 1.04 | 1.24 | 120.45 | 0.249 | 125.0 / 469.0 | 1057 |

\* La jerga es informativa, sin umbral. «Frases OK» = frases cuyas etiquetas de `reglas.py` sobre la transcripción son iguales a las de la referencia. La demora es offline (ver sección 6).

## 3. Regla del plan §2 (toma 4)

Cada corte y umbral contra `parakeet-0.8-rms-0.008` (la referencia de esta corrida), en la toma 4, con las cuatro condiciones de la regla. No se elige sola: «pasa» quiere decir que cumple las cuatro.

| Variante | Frases más | Etiquetas nuevas en negativas | Demora extra (s) | WER extra (puntos) | ¿Pasa? |
|---|---|---|---|---|---|
| `parakeet-0.3-silero-0.9` | +0 ✗ | +0 | -0.49 | -3.6 | no |
| `parakeet-0.8-rms-0.008-filtro-silero-0.5` | +0 ✗ | +0 | 0.01 | +0.0 | no |
| `parakeet-0.8-rms-0.008-y-silero-0.5` | +0 ✗ | +0 | -0.00 | -2.4 | no |

## 4. Por toma y condición

### toma4/luciano-microfono

| Variante | Frases OK | Etiquetas nuevas en negativas | Recall críticos | WER | Segmentos | Demora mediana (s) |
|---|---|---|---|---|---|---|
| `parakeet-0.8-rms-0.008` | 88/90 | 0 | 94.0% | 17.1% | 75 | 1.04 |
| `parakeet-0.3-silero-0.9` | 88/90 | 0 | 93.5% | 13.1% | 106 | 0.55 |
| `parakeet-0.8-rms-0.008-filtro-silero-0.5` | 88/90 | 0 | 94.0% | 17.1% | 75 | 1.05 |
| `parakeet-0.8-rms-0.008-y-silero-0.5` | 88/90 | 0 | 94.4% | 14.4% | 79 | 1.04 |

### toma4/luciano-ruido-tv

| Variante | Frases OK | Etiquetas nuevas en negativas | Recall críticos | WER | Segmentos | Demora mediana (s) |
|---|---|---|---|---|---|---|
| `parakeet-0.8-rms-0.008` | 5/5 | 0 | 100.0% | 15.2% | 3 | 0.81 |
| `parakeet-0.3-silero-0.9` | 5/5 | 0 | 100.0% | 18.2% | 4 | 0.22 |
| `parakeet-0.8-rms-0.008-filtro-silero-0.5` | 5/5 | 0 | 100.0% | 15.2% | 3 | 0.83 |
| `parakeet-0.8-rms-0.008-y-silero-0.5` | 5/5 | 0 | 92.9% | 19.7% | 3 | 0.69 |

## 5. Recall por término crítico (toma 4)

| Término | En la referencia | `parakeet-0.8-rms-0.008` |
|---|---|---|
| `abri el enlace` | 3 | 2/3 |
| `acceso remoto` | 4 | 4/4 |
| `alias` | 7 | 7/7 |
| `anydesk` | 4 | 4/4 |
| `autoriz` | 6 | 5/6 |
| `autoriza` | 6 | 5/6 |
| `cbu` | 6 | 5/6 |
| `clave` | 10 | 10/10 |
| `codigo` | 12 | 12/12 |
| `compart` | 3 | 2/3 |
| `comparti pantalla` | 3 | 2/3 |
| `configuracion` | 3 | 2/3 |
| `confirmame` | 3 | 3/3 |
| `cvv` | 3 | 0/3 |
| `dame` | 16 | 16/16 |
| `decime` | 6 | 6/6 |
| `dni` | 6 | 6/6 |
| `domicilio` | 3 | 3/3 |
| `efectivo` | 7 | 6/7 |
| `instal` | 7 | 7/7 |
| `instala` | 7 | 7/7 |
| `link` | 6 | 6/6 |
| `luca` | 7 | 7/7 |
| `mandame` | 9 | 9/9 |
| `mango` | 3 | 3/3 |
| `necesito que` | 3 | 3/3 |
| `numeros` | 3 | 3/3 |
| `otp` | 3 | 3/3 |
| `paga` | 6 | 6/6 |
| `pago` | 6 | 6/6 |
| `pasame` | 20 | 20/20 |
| `pin` | 6 | 6/6 |
| `plata` | 7 | 7/7 |
| `seis digitos` | 3 | 2/3 |
| `tenes que` | 6 | 6/6 |
| `token` | 3 | 2/3 |
| `transferencia` | 4 | 4/4 |
| `transferi` | 7 | 7/7 |
| `verificacion` | 3 | 3/3 |

## 5b. Sustituciones frecuentes de la toma 1 (candidatas al diccionario)

_Sin pruebas de la toma 1 o sin sustituciones._

## 6. Cómo se midió

- El audio guardado (canal protegida del estéreo) se pasa por cada variante en bloques de 40 ms con 2 hilos, igual que el servidor del panel.
- **Demora de la frase final** = `disponible_s − fin de la voz`, con el reloj simulado de `asr_local.py` (`disponible_s` suma el tiempo de proceso de cada bloque) y el fin de la voz en el último bloque con RMS sobre el umbral. No incluye red ni pantalla. La final que sale al cerrar la prueba cuenta como segmento pero no entra en la demora. Whisper va por lotes y no tiene demora comparable.
- **Proceso, p95 por bloque y memoria pico**: el proceso suma el tiempo de todos los bloques; el p95 es el máximo entre pruebas de los p95 por bloque; la memoria pico es la del subproceso de esa variante (incluye la carga del modelo) y no se puede separar por condición.
- La ganancia y el umbral RMS **de captura** ya quedaron en el audio: offline solo se rehacen el umbral del motor (`rms-*`) y una normalización de nivel (`norm`).
- Los hotwords usan un `bpe.vocab` sintético con puntaje `-(ln(id+2)+3)`; `beam+hotwords-id` repite el `-id` del plan. Ver `hotwords.py`.
- Whisper con ayudas: `hotwords` = términos críticos, bancos y apps; `initial_prompt` = la jerga.

## 7. Reproducir

```bash
python experiments/asr-local/medir_voz_real.py --pruebas ../voip/llamadas --toma-decision 4 --solo-parakeet --contra-parakeet parakeet-0.8-rms-0.008 --variantes parakeet-0.8-rms-0.008-filtro-silero-0.5,parakeet-0.8-rms-0.008-y-silero-0.5,parakeet-0.3-silero-0.9 --etiqueta toma4-mezclas-silero --nota 'Toma 4 (2026-10-30): G01-G06 leídos tres veces seguidas con parakeet-filtro, parakeet-y y parakeet-silero a la vista en el panel, más G08b con la serie de fondo. Una voz (Luciano), micrófono de la Mac. Referencias del guion por bloque. Demora offline en la M1.'
```

Código: `734988d9814ca20cfbc9e3e0e0662a7a469eb012` (LucianoGrosso13/silero-vs-rms-94, limpio). Detalle completo en `manifiesto.json`; textos por frase en `frases.jsonl`.
