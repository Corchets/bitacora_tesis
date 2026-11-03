# Resumen de la medición del ASR con voz real

> **ADVERTENCIA: son una o dos voces del equipo, sin piloto: no es evidencia de rendimiento general ni cierra D09** (ver [MAPA-DECISIONES.md](../../../../docs/gestion/MAPA-DECISIONES.md#d09--elegir-asr-y-detector)). Plan: [PLAN-VOZ-REAL.md](../../PLAN-VOZ-REAL.md). Issue #94.

> **Estado: propuesta sin discutir.** Las listas de términos y jerga se usan como instrumento; D07 sigue abierta.

> **Audio original perdido el 2026-11-02.** La carpeta de pruebas citada abajo ya no existe y esta medición no se puede repetir con esos archivos; los resultados quedan como se midieron ([detalle y regrabaciones](../../../voip/corridas/2026-11-02-voz-real-meet.md#audio-original-perdido)).

## 1. Datos

- Toma 5, `luciano-dialogo`: 7 pruebas (7 con el bloque tal cual el guion). Bloques: D1, D2, D3, D4, D2, D3, D4.
- Toma 5, `luciano-dialogo-tv`: 2 pruebas (2 con el bloque tal cual el guion). Bloques: D1, D1.
- Toma 5, `otra-dialogo`: 7 pruebas (7 con el bloque tal cual el guion). Bloques: D1, D2, D3, D4, D2, D3, D4.
- Toma 5, `otra-dialogo-tv`: 2 pruebas (2 con el bloque tal cual el guion). Bloques: D1, D1.
- Omitidas: 39: `2026-10-29_194923-902062` (no existe la carpeta o no tiene manifiesto legible); `2026-10-29_195020-082746` (no existe la carpeta o no tiene manifiesto legible); `2026-10-29_195202-772508` (no existe la carpeta o no tiene manifiesto legible); `2026-10-29_195256-042759` (no existe la carpeta o no tiene manifiesto legible); `2026-10-29_195409-306210` (no existe la carpeta o no tiene manifiesto legible); `2026-10-29_200653-308143` (no existe la carpeta o no tiene manifiesto legible); `2026-10-29_200832-553834` (no existe la carpeta o no tiene manifiesto legible); `2026-10-29_200926-056710` (no existe la carpeta o no tiene manifiesto legible); `2026-10-29_201653-688897` (no existe la carpeta o no tiene manifiesto legible); `2026-10-29_201733-924805` (no existe la carpeta o no tiene manifiesto legible); `2026-10-29_201814-367007` (no existe la carpeta o no tiene manifiesto legible); `2026-10-29_202351-657853` (no existe la carpeta o no tiene manifiesto legible); `2026-10-29_201921-145948` (no existe la carpeta o no tiene manifiesto legible); `2026-10-29_201959-768452` (no existe la carpeta o no tiene manifiesto legible); `2026-10-29_204534-495909` (no existe la carpeta o no tiene manifiesto legible); `2026-10-29_204616-642444` (no existe la carpeta o no tiene manifiesto legible); `2026-10-29_205011-705316` (no existe la carpeta o no tiene manifiesto legible); `2026-10-29_205052-595235` (no existe la carpeta o no tiene manifiesto legible); `2026-10-29_205127-026460` (no existe la carpeta o no tiene manifiesto legible); `2026-10-29_205159-170084` (no existe la carpeta o no tiene manifiesto legible); `2026-10-30_152838-034658` (no existe la carpeta o no tiene manifiesto legible); `2026-10-30_152914-598219` (no existe la carpeta o no tiene manifiesto legible); `2026-10-30_152947-712308` (no existe la carpeta o no tiene manifiesto legible); `2026-10-30_153026-522559` (no existe la carpeta o no tiene manifiesto legible); `2026-10-30_153102-946340` (no existe la carpeta o no tiene manifiesto legible); `2026-10-30_153138-212776` (no existe la carpeta o no tiene manifiesto legible); `2026-10-30_153304-448017` (no existe la carpeta o no tiene manifiesto legible); `2026-10-30_153335-495862` (no existe la carpeta o no tiene manifiesto legible); `2026-10-30_153409-995865` (no existe la carpeta o no tiene manifiesto legible); `2026-10-30_153442-452741` (no existe la carpeta o no tiene manifiesto legible); `2026-10-30_153528-099127` (no existe la carpeta o no tiene manifiesto legible); `2026-10-30_153603-648473` (no existe la carpeta o no tiene manifiesto legible); `2026-10-30_153725-703882` (no existe la carpeta o no tiene manifiesto legible); `2026-10-30_153759-275232` (no existe la carpeta o no tiene manifiesto legible); `2026-10-30_153829-326020` (no existe la carpeta o no tiene manifiesto legible); `2026-10-30_153908-775592` (no existe la carpeta o no tiene manifiesto legible); `2026-10-30_153944-081407` (no existe la carpeta o no tiene manifiesto legible); `2026-10-30_154018-708912` (no existe la carpeta o no tiene manifiesto legible); `2026-10-30_154331-950817` (no existe la carpeta o no tiene manifiesto legible)
- Carpeta de pruebas: `/Users/lucianogrosso/orca/workspaces/bitacora_tesis/tito-gemma-pendientes/experiments/voip/llamadas` | CSV: `/Users/lucianogrosso/orca/workspaces/bitacora_tesis/tito-gemma-pendientes/experiments/asr-local/voz-real/pruebas.csv` | audio medido: 1202.7 s.

## 2. Resultado por variante (toma 5, todas las condiciones juntas)

| Variante | Frases OK | Etiquetas nuevas en negativas | Recall críticos | Recall bancos y apps | Recall jerga* | WER | CER | Segmentos finales | Demora final mediana (s) | p95 (s) | Proceso (s) | RTF | p95 / máx. por bloque (ms) | Memoria pico (MB) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `parakeet-0.8-rms-0.008-filtro-silero-0.5` | 121/129 | 0 | 70.9% | 58.3% | 10.0% | 25.6% | 15.5% | 127 | 1.01 | 1.10 | 105.93 | 0.088 | 0.3 / 487.5 | 1036 |
| `parakeet-0.3-silero-0.9` | 120/129 | 0 | 76.4% | 50.0% | 10.0% | 32.8% | 20.0% | 205 | 0.26 | 0.52 | 51.35 | 0.043 | 0.3 / 221.1 | 998 |

\* La jerga es informativa, sin umbral. «Frases OK» = frases cuyas etiquetas de `reglas.py` sobre la transcripción son iguales a las de la referencia. La demora es offline (ver sección 6).

## 3. Regla del plan §2 (toma 5)

Cada corte y umbral contra `parakeet-0.8-rms-0.008-filtro-silero-0.5` (la referencia de esta corrida), en la toma 5, con las cuatro condiciones de la regla. No se elige sola: «pasa» quiere decir que cumple las cuatro.

| Variante | Frases más | Etiquetas nuevas en negativas | Demora extra (s) | WER extra (puntos) | ¿Pasa? |
|---|---|---|---|---|---|
| `parakeet-0.3-silero-0.9` | -1 ✗ | +0 | -0.75 | +7.3 ✗ | no |

## 4. Por toma y condición

### toma5/luciano-dialogo

| Variante | Frases OK | Etiquetas nuevas en negativas | Recall críticos | WER | Segmentos | Demora mediana (s) |
|---|---|---|---|---|---|---|
| `parakeet-0.8-rms-0.008-filtro-silero-0.5` | 47/49 | 0 | 0.0% | 21.4% | 47 | 0.98 |
| `parakeet-0.3-silero-0.9` | 49/49 | 0 | 100.0% | 23.2% | 56 | 0.42 |

### toma5/luciano-dialogo-tv

| Variante | Frases OK | Etiquetas nuevas en negativas | Recall críticos | WER | Segmentos | Demora mediana (s) |
|---|---|---|---|---|---|---|
| `parakeet-0.8-rms-0.008-filtro-silero-0.5` | 14/14 | 0 | — | 19.2% | 12 | 0.43 |
| `parakeet-0.3-silero-0.9` | 14/14 | 0 | — | 18.3% | 17 | 0.10 |

### toma5/otra-dialogo

| Variante | Frases OK | Etiquetas nuevas en negativas | Recall críticos | WER | Segmentos | Demora mediana (s) |
|---|---|---|---|---|---|---|
| `parakeet-0.8-rms-0.008-filtro-silero-0.5` | 44/50 | 0 | 67.4% | 32.9% | 51 | 1.04 |
| `parakeet-0.3-silero-0.9` | 44/50 | 0 | 79.1% | 41.0% | 105 | 0.24 |

### toma5/otra-dialogo-tv

| Variante | Frases OK | Etiquetas nuevas en negativas | Recall críticos | WER | Segmentos | Demora mediana (s) |
|---|---|---|---|---|---|---|
| `parakeet-0.8-rms-0.008-filtro-silero-0.5` | 16/16 | 0 | 100.0% | 12.0% | 17 | 1.04 |
| `parakeet-0.3-silero-0.9` | 13/16 | 0 | 60.0% | 31.0% | 27 | 0.19 |

## 5. Recall por término crítico (toma 5)

| Término | En la referencia | `parakeet-0.8-rms-0.008-filtro-silero-0.5` |
|---|---|---|
| `acceso remoto` | 2 | 2/2 |
| `alias` | 2 | 1/2 |
| `anydesk` | 2 | 1/2 |
| `cbu` | 2 | 1/2 |
| `clave` | 3 | 3/3 |
| `codigo` | 3 | 3/3 |
| `compart` | 2 | 1/2 |
| `comparti pantalla` | 2 | 1/2 |
| `configuracion` | 2 | 2/2 |
| `confirmame` | 3 | 3/3 |
| `cvv` | 2 | 0/2 |
| `dame` | 2 | 2/2 |
| `instal` | 2 | 1/2 |
| `instala` | 2 | 1/2 |
| `luca` | 2 | 1/2 |
| `numeros` | 5 | 5/5 |
| `pago` | 2 | 1/2 |
| `pasame` | 5 | 4/5 |
| `token` | 4 | 2/4 |
| `transferencia` | 2 | 1/2 |
| `transferi` | 4 | 3/4 |

## 5b. Sustituciones frecuentes de la toma 1 (candidatas al diccionario)

_Sin pruebas de la toma 1 o sin sustituciones._

## 6. Cómo se midió

- El audio guardado (canal otra, protegida del estéreo) se pasa por cada variante en bloques de 40 ms con 2 hilos, igual que el servidor del panel.
- **Demora de la frase final** = `disponible_s − fin de la voz`, con el reloj simulado de `asr_local.py` (`disponible_s` suma el tiempo de proceso de cada bloque) y el fin de la voz en el último bloque con RMS sobre el umbral. No incluye red ni pantalla. La final que sale al cerrar la prueba cuenta como segmento pero no entra en la demora. Whisper va por lotes y no tiene demora comparable.
- **Proceso, p95 por bloque y memoria pico**: el proceso suma el tiempo de todos los bloques; el p95 es el máximo entre pruebas de los p95 por bloque; la memoria pico es la del subproceso de esa variante (incluye la carga del modelo) y no se puede separar por condición.
- La ganancia y el umbral RMS **de captura** ya quedaron en el audio: offline solo se rehacen el umbral del motor (`rms-*`) y una normalización de nivel (`norm`).
- Los hotwords usan un `bpe.vocab` sintético con puntaje `-(ln(id+2)+3)`; `beam+hotwords-id` repite el `-id` del plan. Ver `hotwords.py`.
- Whisper con ayudas: `hotwords` = términos críticos, bancos y apps; `initial_prompt` = la jerga.

## 7. Reproducir

```bash
python experiments/asr-local/medir_voz_real.py --solo-parakeet --toma-decision 5 --contra-parakeet parakeet-0.8-rms-0.008-filtro-silero-0.5 --variantes parakeet-0.3-silero-0.9 --etiqueta dialogos-a-contra-b
```

Código: `abe825ecd802e0b49db47f486bafb019989bde3a` (LucianoGrosso13/tito-gemma-pendientes, limpio). Detalle completo en `manifiesto.json`; textos por frase en `frases.jsonl`.
