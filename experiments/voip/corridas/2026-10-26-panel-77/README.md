# Verificación del panel de ejemplo — #77 (2026-10-26)

Objetivo: comprobar la ruta real `/panel` → audio estéreo por bloques → Zipformer → detector,
y contrastar el aviso de la estafa con `reglas-final` (18,457 s, tolerancia ±0,1 s).
Son dos ejemplos TTS de desarrollo para la demo; no es una evaluación del rendimiento del
detector ni usa una partición de reserva. No se accedió a CV2-T-*.

## Configuración y datos

Se midió el commit `3dc9269` con árbol limpio; cada manifiesto conserva el hash completo,
la máquina, versiones, ASR, modelo/prompt del detector, seed (42 para SLM; no aplica a reglas),
y el mensaje de inicio. Zipformer local, 2 hilos por canal, corte 0,8 s, disparo `final`.
Los WAV de `experiments/asr-local/audio/` son estéreo a 16 kHz: izquierdo = otra persona,
derecho = protegida. No se guardan WAV en Git.

| Archivo de entrada | SHA-256 |
|---|---|
| `SC-WA-CODE-01-tts-estereo.wav` | `4e6be5e30a962cd9ed15790759342ababf39b79811635ac8e5ae24b6a9868344` |
| `LG-WA-CONSULTA-01-tts-estereo.wav` | `58d228ba5a08b20f92ceb9661537460d3451576b7ee95238344c3f95ec4d2e07` |

## Resultados observados

Cada enlace contiene `actualizaciones.jsonl`, `detector.jsonl` y `manifiesto.json`
originales de la llamada; el estéreo grabado permanece en `/tmp/voip-demo-llamadas/`.

| Corrida | Escenario | Aviso (`T_A`) | Evaluaciones |
|---|---|---|---|
| [reglas-estafa](reglas-estafa/manifiesto.json) | `SC-WA-CODE-01` | 18.455 s | 4 |
| [reglas-legitima](reglas-legitima/manifiesto.json) | `LG-WA-CONSULTA-01` | 5.214 s | 1 |
| [slm-legitima](slm-legitima/manifiesto.json) | `LG-WA-CONSULTA-01` | Sin aviso | 3 |

La estafa con reglas cumple la tolerancia de ±0,1 s frente a 18,457 s. La legítima
con Qwen3.5 0.8B local no avisa y sus evaluaciones son válidas, sin fallos.
Con el respaldo de reglas la legítima da una falsa alarma por «Me llegó por ese MS
un código para activar WhatsApp y yo no lo pedí»: mencionar un código basta para esa
regla. El coordinador indicó conservar esta limitación y verificar la legítima con el
detector de la demo; no se cambian reglas ni se suprimen avisos según el escenario.

## Cómo repetir

Desde `experiments/voip/`, arrancá el servidor y abrí `http://127.0.0.1:8767/`:

```bash
../../.venv/bin/python servidor.py --host 127.0.0.1 --puerto 8767 --salida /tmp/voip-demo-llamadas --detector reglas
```

Elegí la estafa y tocá «Iniciar llamada»; al finalizar, repetí con la legítima.
Para el detector de la demo, detené el servidor y arrancalo así antes de repetir la legítima:

```bash
../../.venv/bin/python servidor.py --host 127.0.0.1 --puerto 8767 --salida /tmp/voip-demo-llamadas --detector slm --modelo qwen3.5:0.8b-q8_0 --ollama-url http://127.0.0.1:11434
```

Esta verificación envió por WebSocket el mismo `iniciar` que manda el panel
(ver [contrato y controles](../../README.md#ejemplo-desde-el-panel-sin-terminales-de-clientes))
y esperó `fin`; leyó el aviso y los manifiestos guardados. El servidor produjo sus propias
marcas con reloj real; no se simuló ASR ni detector en estas tres llamadas.

## Pruebas y revisión

- `../../.venv/bin/python -m unittest discover -s tests`: **11 tests, OK** (0,553 s).
  Incluyen MotorFalso/reloj controlado, inicio/fin explícitos, fin por desconexión,
  carpetas independientes, alineación de ambos canales, bloque final corto, interrupción
  del ejemplo y rechazo de clientes que llegan durante la precarga del ejemplo.
- JS extraído de `panel.html`: `tsc --allowJs --checkJs --noEmit --target ES2022 --lib ES2022,DOM`: **OK**.
- `cliente.py` no tiene cambios frente a `78b18693`; los tests usan su mismo protocolo PCM16.
- No se tocaron documentos de gestión, detector ni corpus; no se subieron WAV.

## Standards

La revisión independiente observó falta de trazabilidad de las cifras nuevas: no estaban
versionados sus manifiestos ni salidas. Se corrigió conservando estas tres corridas con
árbol limpio, datos identificados por hash, configuración y revisión de código.
No encontró otras violaciones manuales ni heurísticas con impacto concreto.

## Spec

La revisión independiente encontró una carrera al admitir clientes durante la precarga
del ejemplo. Se corrigió serializando la admisión con el inicio/cierre y se agregó una prueba
que falla con el código anterior y pasa con el cambio. El resultado de la legítima con SLM
ya está conservado aquí; el respaldo de reglas mantiene su falsa alarma documentada.

Resumen de revisión: Standards, 1 hallazgo corregido (trazabilidad); Spec, 1 hallazgo
corregido (carrera), y verificación con SLM incorporada.

## Verificación humana pendiente

El entorno no ofrece navegador disponible (CUA devolvió inventario vacío), por lo que
queda comprobar en la notebook de demo: seleccionar fuente, iniciar, ver la transcripción
y aviso, terminar antes de EOF, tocar «Nueva llamada», comprobar panel limpio y volver a
iniciar. También quedan los ensayos con voz real, Meet y otra notebook, propios de la
integración y de los tickets siguientes; #77 no agrega captura del navegador.
