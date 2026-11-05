# Transcripción en vivo y revisión del diálogo — #112

## Pregunta y alcance

Comprobar que el diálogo central de Presentación muestra los parciales del ASR
como texto provisorio, los corrige sin duplicar intervenciones, confirma los
finales con rol y cronología correctos, y deja revisar frases anteriores sin
perder los teléfonos ni la llamada. Segunda entrega de
[#110](https://github.com/Corchets/bitacora_tesis/issues/110), verificada contra
[#112](https://github.com/Corchets/bitacora_tesis/issues/112).

Código: `74cb4b7` más la corrección de revisión descripta abajo. Se verificó el
HTML real de [`panel.html`](../panel.html) con Chrome headless y CDP. Igual que
en [#111](2026-10-30-presentacion-111.md), el servidor de prueba envía eventos
WebSocket sintéticos; no ejecuta captura, ASR ni detector reales. La secuencia
es fija, sin aleatoriedad, corpus ni split de evaluación.

## Reproducción

Mismo [driver portable](../tests/presentacion_ui.py) y entorno que #111. En esta
Mac se usó `/Users/lucianogrosso/bitacora_tesis-voip/.venv/bin/python`.

```sh
python experiments/voip/tests/presentacion_ui.py --outdir /tmp/presentacion-112 --report /tmp/presentacion-112.md
node --test experiments/voip/tests/*.test.mjs
python -m unittest discover -s experiments/voip/tests -p 'test_*.py' -q
```

El driver suma a la secuencia de #111 un parcial con su revisión, dos finales
intercalados de ambos roles, una conversación larga, la revisión manual de una
frase anterior con «Volver al vivo», una nueva llamada y la emulación de
movimiento reducido.

## Resultado observado el 2026-10-30

- **20 comprobaciones de UI aprobadas**, repetidas por Claude después de la
  entrega de Gemini. El script devuelve un código distinto de cero si falla una.
- El parcial aparece como «Texto provisorio» y su revisión reemplaza la misma
  intervención: una sola línea. Los finales se ordenan por segmento con su rol.
- Con diez intervenciones se desplaza sólo el diálogo central; los teléfonos
  siguen visibles sin scroll de la ventana.
- Subir a revisar pausa el seguimiento y muestra «Volver al vivo»; el botón
  vuelve al final sin alterar la llamada. La alternancia con la consola emite
  **0 comandos adicionales** y conserva las 11 líneas; una nueva llamada empieza
  con el diálogo vacío.
- Con movimiento reducido el desplazamiento es inmediato.
- La revisión detectó que la entrega borraba la línea que escribe el texto de
  cada frase en la consola: las 11 frases quedaban vacías. Se restituyó y el
  driver ahora comprueba que la consola conserve el texto de las frases finales.
- **0 errores de consola**, **6/6 pruebas Node** y **73/73 pruebas Python**.

Capturas con datos sintéticos de la escena final, con «Volver al vivo» visible:

- [Notebook, 1366 × 768](2026-10-30-presentacion-112-notebook-1366x768.png).
- [Proyección, 1920 × 1080](2026-10-30-presentacion-112-proyeccion-1920x1080.png).
- [Movimiento reducido, 1920 × 1080](2026-10-30-presentacion-112-reducido-1920x1080.png).

## Límites

Las capturas verifican UI; no acreditan calidad del ASR, un ensayo físico en
sala ni el ritmo de parciales de Parakeet o Zipformer reales, que sigue en #115.
Detecciones y aviso (#113) y reconstrucción ante fallas (#114) mantienen su
alcance. Observación no bloqueante: «Volver al vivo» puede quedar visible con
el análisis ya finalizado.
