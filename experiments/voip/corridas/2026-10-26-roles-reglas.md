# Registro por roles y replay — #76

Verificación local del 2026-10-26 sobre `luciano/voip-76`, base
`78b18693e8e194d94040cda6f8ea5497ed9860dc` más el cambio de #76 todavía sin
commit durante la corrida (así consta en el manifiesto). No evalúa rendimiento
ni cambia D08/D09. Solo se usó `SC-WA-CODE-01-tts-estereo.wav`; sin reserva.

## Configuración y reproducción

macOS arm64, 8 núcleos lógicos, 8 GB RAM; Python 3.13.15, sherpa-onnx 1.13.8.
Zipformer español kroko 2025-08-06 local, dos motores, dos hilos por motor,
PCM16 a 16 kHz, bloques de 40 ms, corte de silencio 0,8 s. Detector `reglas`,
disparo `final`, hablantes `ab`, seed no aplica. Es una prueba de integración
con una llamada TTS, sin partición de entrenamiento/evaluación ni métricas de
clasificación.

Desde la raíz del repositorio, con los modelos locales disponibles en
`experiments/asr-local/modelos/` (symlink ignorado en esta copia):

```bash
/Users/lucianogrosso/bitacora_tesis-voip/.venv/bin/python experiments/voip/servidor.py \
  --host 127.0.0.1 --puerto 8876 --detector reglas --salida /tmp/voip-76-demo-llamadas

# En dos terminales, iniciados juntos:
/Users/lucianogrosso/bitacora_tesis-voip/.venv/bin/python experiments/voip/cliente.py \
  --servidor ws://127.0.0.1:8876 --rol otra --canal izq \
  --wav /Users/lucianogrosso/bitacora_tesis-voip/experiments/asr-local/audio/SC-WA-CODE-01-tts-estereo.wav
/Users/lucianogrosso/bitacora_tesis-voip/.venv/bin/python experiments/voip/cliente.py \
  --servidor ws://127.0.0.1:8876 --rol protegida --canal der \
  --wav /Users/lucianogrosso/bitacora_tesis-voip/experiments/asr-local/audio/SC-WA-CODE-01-tts-estereo.wav

/Users/lucianogrosso/bitacora_tesis-voip/.venv/bin/python experiments/replay/replay.py \
  --actualizaciones /tmp/voip-76-demo-llamadas/2026-10-26_171252/actualizaciones.jsonl \
  --detector reglas --salida /tmp/voip-76-replay
```

## Resultado observable

| Medida | En vivo | Replay |
|---|---:|---:|
| Actualización que emite el aviso | 16 | 16 |
| `T_A` (s) | 18,455 | 18,4491 |
| Tiempo del detector en ese aviso (ms) | 10,6 | 4,1 |

Diferencia absoluta: **5,9 ms**. Tolerancia: **15,7 ms**, suma de ambos tiempos
del detector más 1 ms por el redondeo del registro. Ambos avisos corresponden a
`REQUEST_AUTH_CODE` y citan «decime el código de activación que recibiste por sms».
Todas las actualizaciones guardadas tienen `canal` igual a `protegida` u `otra`
y ninguna tiene el campo `rol` duplicado. La configuración de replay conserva `ab`.

El JSONL, el manifiesto, `detector.jsonl` y el estéreo quedaron en la carpeta de
`/tmp` indicada; el replay produjo `eventos.csv`, `manifiesto.json` y `resumen.md`
en `/tmp/voip-76-replay`. No se incorpora audio a Git. Servidor y clientes detenidos.

## Compatibilidad y pruebas

- `experiments/voip/tests/`: 4 tests, OK. `MotorFalso` y reloj controlado comprueban
  ambos órdenes de roles, el parcial anterior al primer final, puntuación ignorada,
  las fotos exactas recibidas por el detector y su igualdad con replay.
- `experiments/replay/tests/`: 14 tests, OK. Incluyen reinicio de letras por llamada,
  A/B históricos conservados aunque B aparezca primero y CLI con roles sin caída a `sin`.
- Replay con reglas sobre
  `experiments/asr-local/corridas/2026-10-17_estereo_SC-WA-CODE-01_zipformer_mezcla/actualizaciones.jsonl`:
  22 filas, A/B conservados y aviso emitido; salida `/tmp/voip-76-replay-anterior`.
- Replay del corpus `experiments/slm-directo/casos/texto/SC-WA-CODE-01-e01.txt`:
  5 filas, A/B conservados y aviso emitido; salida `/tmp/voip-76-replay-corpus`.
- El panel conserva los eventos ASR anteriores (`canal` A/B, `rol` con la persona);
  `panel.html` no cambia. El formato nuevo corresponde al archivo persistido.

No se probaron voces reales, Meet, BlackHole ni otra notebook: son verificaciones
humanas de la demo completa, no necesarias para el contrato de registro de #76.
