# Detecciones y aviso en el teléfono protegido — #113

## Pregunta y alcance

Comprobar que cada evaluación del detector se adjunta a la frase que la
disparó, que la vista distingue «Analizando», «Sin aviso», «Posible estafa»,
«No evaluado» y «Error», y que el primer aviso real aparece en el teléfono de la
persona protegida con motivo y evidencia, sin repetirse al alternar vistas.
Tercera entrega de [#110](https://github.com/Corchets/bitacora_tesis/issues/110),
verificada contra [#113](https://github.com/Corchets/bitacora_tesis/issues/113).

Código: `33f2c9d` más la corrección de revisión descripta abajo. Se verificó el
HTML real de [`panel.html`](../panel.html) con Chrome headless y CDP. Como en
[#111](2026-10-30-presentacion-111.md) y [#112](2026-10-30-presentacion-112.md),
el servidor de prueba envía eventos WebSocket sintéticos con la forma de los del
detector; no ejecuta captura, ASR ni detector reales. No cambia modelos,
prompts, umbrales, registros ni política de alerta.

## Reproducción

Mismo [driver portable](../tests/presentacion_ui.py) y entorno que #111. En esta
Mac se usó `/Users/lucianogrosso/bitacora_tesis-voip/.venv/bin/python`.

```sh
python experiments/voip/tests/presentacion_ui.py --outdir /tmp/presentacion-113 --report /tmp/presentacion-113.md
node --test experiments/voip/tests/*.test.mjs
python -m unittest discover -s experiments/voip/tests -p 'test_*.py' -q
```

El driver suma una segunda llamada con una evaluación sin aviso, una evaluación
tardía que llega después de otra intervención, una frase salteada, una
respuesta inválida, un aviso con evidencia ubicable, una evaluación sin
puntuación, frases posteriores al aviso, cierre del aviso, silenciado del tono y
alternancia de vistas.

## Resultado observado el 2026-10-30

- **29 comprobaciones de UI aprobadas**, repetidas por Claude después de la
  entrega de Gemini. El script devuelve un código distinto de cero si falla una.
- La evaluación tardía queda en su frase y no en la última visible. La frase
  salteada se muestra «No evaluado» y la respuesta inválida «Error»; ninguna
  aparece como «Sin aviso».
- El aviso aparece en el teléfono protegido con motivo, momento y cita; la cita
  se resalta en la frase que lo disparó. El otro teléfono sigue diciendo «Otra
  persona». Las frases posteriores quedan «No evaluado» con el motivo «Detector
  detenido tras el primer aviso».
- Los detalles técnicos muestran puntuación como «no calibrada» cuando existe,
  «No entregada por el detector» cuando falta, demoras e identificación del
  detector.
- Cerrar el aviso no borra el registro ni cambia el estado de la llamada; el
  tono se silencia desde el teléfono y alternar vistas no vuelve a mostrarlo.
- La revisión detectó que la tarjeta «Posible estafa» y el botón «Volver al
  vivo» tenían un `display` propio que anulaba el atributo `hidden`: la tarjeta
  se veía en **toda** llamada, aun sin aviso, y el botón quedaba siempre
  visible (la observación pendiente de #112). Una regla de Presentación hace
  respetar `hidden`, y el driver ahora comprueba la visibilidad real: tres
  comprobaciones de aviso y una de «Volver al vivo» fallaban sin la corrección.
- **0 errores de consola**, **6/6 pruebas Node** y **73/73 pruebas Python**.

Capturas con datos sintéticos:

- [Aviso activo, 1920 × 1080](2026-10-30-presentacion-113-aviso-1920x1080.png).
- [Notebook, 1366 × 768](2026-10-30-presentacion-113-notebook-1366x768.png) y
  [proyección, 1920 × 1080](2026-10-30-presentacion-113-proyeccion-1920x1080.png):
  escena final de una llamada sin aviso, sin tarjeta.
- [Movimiento reducido, 1920 × 1080](2026-10-30-presentacion-113-reducido-1920x1080.png).

## Límites

Las capturas verifican UI; no acreditan desempeño del detector, un ensayo
físico en sala ni la ruta real de ASR y detector, que sigue en #115. La cita se
resalta sólo si aparece literal en la frase que disparó el aviso; si no se
ubica, se conserva el motivo sin mostrar cita. Al terminar, las frases sin
evaluación quedan «No evaluado»; la reconstrucción ante fallas y reconexión
sigue en #114. Esta entrega no resuelve D08, D09 ni el aviso final de D10.
