# Presentación de una misma llamada — #111

## Pregunta y alcance

Comprobar que una llamada iniciada desde la consola abre una escena con dos
teléfonos y permite volver al panel conservando la llamada. Esta es la primera
entrega de [#110](https://github.com/Corchets/bitacora_tesis/issues/110), verificada
contra [#111](https://github.com/Corchets/bitacora_tesis/issues/111).

Código de la escena: `275707b`. Se verificó el HTML real de
[`panel.html`](../panel.html) y sus módulos mediante Chrome headless y CDP. El
servidor de prueba reutiliza la función de serving del panel y envía eventos
WebSocket sintéticos; no ejecuta captura, ASR ni detector reales. La secuencia
es fija, sin aleatoriedad, corpus ni split de evaluación.

## Reproducción

El [driver portable](../tests/presentacion_ui.py) localiza el repositorio desde
su archivo y acepta `--repo`, `--outdir`, `--report` y `CHROME_BIN`. Requiere Chrome
o Chromium y el entorno Python con las dependencias existentes de VoIP. En esta
Mac se usó `/Users/lucianogrosso/bitacora_tesis-voip/.venv/bin/python`.

```sh
python experiments/voip/tests/presentacion_ui.py --outdir /tmp/presentacion-111 --report /tmp/presentacion-111.md
node --test experiments/voip/tests/*.test.mjs
python -m unittest discover -s experiments/voip/tests -p 'test_*.py' -q
```

El driver sirve esta copia en puertos efímeros y conserva el servidor de la demo
en `8765`. Abre su propio Chrome y cierra sus procesos al terminar. El comando de
inicio se observa antes de confirmar la llamada; los eventos siguientes incluyen
inicio de prueba ASR, inicio de llamada, niveles alternados, dos frases finales
con roles, navegación y fin.

## Resultado observado el 2026-10-30

- **12 comprobaciones de UI aprobadas**, repetidas por Codex después de la
  entrega de Gemini. El script devuelve un código distinto de cero si falla una.
- Presentación abre tras el inicio confirmado del modo llamada. El modo ASR
  continúa aparte. Los roles conservan su lado y los niveles actualizan el
  estado de voz y los medidores.
- La alternancia entre consola y Presentación emite **0 comandos adicionales**
  de inicio o fin. El cierre conserva las dos intervenciones y muestra
  «Análisis finalizado».
- Ambos nombres son visibles sobre fondo oscuro. La primera inspección detectó
  que el estilo global de `header` los dejaba blancos sobre blanco; se corrigió
  el alcance del CSS y la prueba comprueba su visibilidad y contraste efectivo.
- **0 errores de consola**, **6/6 pruebas Node** y **73/73 pruebas Python**.

Capturas con datos sintéticos de la escena final:

- [Notebook, 1366 × 768](2026-10-30-presentacion-111-notebook-1366x768.png).
- [Proyección, 1920 × 1080](2026-10-30-presentacion-111-proyeccion-1920x1080.png).

## Límites

Las capturas verifican UI; no acreditan un ensayo físico en sala ni desempeño de
ASR o detector. La verificación integrada con un ejemplo real del pipeline sigue
en #115. Parciales y revisión del diálogo (#112), detecciones y aviso (#113), y
reconstrucción ante fallas (#114) mantienen su propio alcance. El video continúa
en #53. Esta entrega no resuelve D08, D09 ni el aviso final de D10.
