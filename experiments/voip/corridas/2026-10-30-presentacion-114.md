# Resultado conservado y escena reconstruida ante fallas — #114

## Pregunta y alcance

Comprobar que al terminar o reconectar el panel la Presentación conserva una
escena coherente con texto y detecciones, y que las fallas de captura, conexión
o detector se ven sin anunciar una llamada segura. Cuarta entrega de
[#110](https://github.com/Corchets/bitacora_tesis/issues/110), verificada contra
[#114](https://github.com/Corchets/bitacora_tesis/issues/114).

Código: `2381e37` más el ajuste de pruebas descripto abajo. Se verificó el HTML
real de [`panel.html`](../panel.html) con Chrome headless y CDP. Como en las
entregas anteriores ([#111](2026-10-30-presentacion-111.md),
[#112](2026-10-30-presentacion-112.md), [#113](2026-10-30-presentacion-113.md)),
el servidor de prueba envía eventos WebSocket sintéticos; no ejecuta captura,
ASR ni detector reales. La reconexión se simula cerrando el WebSocket del panel
y reenviando los eventos de la misma llamada, como hace el servidor con su
historial al conectarse un panel en medio de una llamada.

## Reproducción

Mismo [driver portable](../tests/presentacion_ui.py) y entorno que #111. En esta
Mac se usó `/Users/lucianogrosso/bitacora_tesis-voip/.venv/bin/python`.

```sh
python experiments/voip/tests/presentacion_ui.py --outdir /tmp/presentacion-114 --report /tmp/presentacion-114.md
node --test experiments/voip/tests/*.test.mjs
python -m unittest discover -s experiments/voip/tests -p 'test_*.py' -q
```

## Resultado observado el 2026-10-30

- **36 comprobaciones de UI aprobadas**, repetidas por Claude después de la
  entrega de Gemini 3.8 Flash. El script devuelve un código distinto de cero si
  falla una.
- Reconectar después de un aviso ya cerrado reconstruye las 7 frases sin
  duplicarlas, en Presentación y en la consola; no emite otro inicio, la
  tarjeta sigue cerrada, «Posible estafa» queda sólo en la frase del código y,
  con el sonido activo, **0 tonos** nuevos.
- Terminar con un borrador pendiente incorpora el último final, marca «No
  evaluado» lo que ya no se va a evaluar y conserva la escena con «Análisis
  finalizado». El borrador sin confirmar no queda en la escena final.
- Un permiso de micrófono denegado se muestra en los controles y en
  Presentación; la interrupción de la fuente y el error del detector quedan
  visibles y conservados tras el fin, sin ninguna frase marcada «Sin aviso».
- Volver a la consola permite operar sin crear otra llamada, y una nueva
  llamada empieza sin texto, aviso, puntuación ni borrador anteriores.
- La revisión agregó dos comprobaciones a la reconexión. Una mide el tono: sin
  el resguardo de la entrega sonaba 1 tono al reconectar. La otra verifica la
  atribución del aviso: los eventos ASR reenviados no traían su número de orden,
  como sí lo trae el servidor real, y la captura mostraba el aviso en otra frase.
- **0 errores de consola**, **6/6 pruebas Node** y **73/73 pruebas Python**.

Capturas con datos sintéticos:

- [Escena final conservada tras reconectar, 1920 × 1080](2026-10-30-presentacion-114-fin-conservado-1920x1080.png).
- [Falla de fuente y error del detector, 1920 × 1080](2026-10-30-presentacion-114-fallo-1920x1080.png).
- [Notebook, 1366 × 768](2026-10-30-presentacion-114-notebook-1366x768.png).

## Límites

No se probó una reconexión real contra `servidor.py` ni la pérdida de una
fuente externa: la recuperación usa las capacidades existentes del panel y no
recaptura automáticamente una fuente perdida. La ruta real de ASR y detector y
el ensayo en notebook y proyección siguen en #115. Esta entrega no resuelve
D08, D09 ni el aviso final de D10.
