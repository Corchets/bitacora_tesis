# Ensayar Presentación completa en notebook y formato de proyección — #115

## Pregunta y alcance

Verificación integrada de las historias 1–31 y los 10 criterios de aceptación de [#110](https://github.com/Corchets/bitacora_tesis/issues/110) en formato de notebook (1366 × 768) y proyección horizontal (1920 × 1080), asegurando continuidad de la llamada, legibilidad tipográfica, teléfonos visibles sin scroll de ventana y controles alcanzables. Quinta y última entrega del frente de Presentación contra [#115](https://github.com/Corchets/bitacora_tesis/issues/115).

Código evaluado: base `4574df6` más ajuste responsivo en `conversacion.mjs` (`@media (max-height: 820px)`) para compactar marco, avatar y paddings de los iPhone ante avisos activos en pantallas notebook.

## Reproducción

Suite automatizada UI con Chrome headless y CDP:
```sh
/Users/lucianogrosso/bitacora_tesis-voip/.venv/bin/python experiments/voip/tests/presentacion_ui.py --outdir /tmp/tesis-presentacion-115 --report /tmp/tesis-presentacion-115-report.md
node --test experiments/voip/tests/*.test.mjs
/Users/lucianogrosso/bitacora_tesis-voip/.venv/bin/python -m unittest discover -s experiments/voip/tests -p 'test_*.py' -q
```

Comprobación por la ruta real de ASR y detector con ejemplo existente:
```sh
# Servidor en puerto efímero aislado (puerto 8765 ajeno conservado intacto)
/Users/lucianogrosso/bitacora_tesis-voip/.venv/bin/python servidor.py --host 127.0.0.1 --puerto 51122 --detector reglas --asr zipformer
# En otra terminal:
curl --fail --silent http://127.0.0.1:51122/ | cmp - experiments/voip/panel.html
```

## Resultado observado el 2026-10-30

- **41 comprobaciones de UI aprobadas (41/41)** en `presentacion_ui.py`.
- **Navegación por teclado y foco visible**: verificado foco en `volver-panel`, `pres-terminar`, `pres-aviso-btn-sonido`, `pres-aviso-btn-cerrar` y `.pres-detalles-summary` con contorno `2px solid` visible. Despliegue y colapso de detalles técnicos operable mediante teclado.
- **Inspección notebook (1366 × 768)**: con 7 líneas de diálogo, detalle técnico desplegado y tarjeta de aviso en el teléfono protegido, ambos teléfonos (`pres-telefono-otra` y `pres-telefono-protegida`) permanecen visibles dentro del viewport (`top >= 0 && bottom <= 768px`), sin scroll de ventana (`scrollY === 0`), texto legible con contraste ≥ 4.5:1 y todos los controles de acción alcanzables.
- **Inspección proyección (1920 × 1080)**: tipografía de conversación escalada a `1.25rem` (20px), teléfonos fijos en laterales, diálogo central desplazable sin desborde horizontal.
- **Escena final conservada**: verificado estado «Análisis finalizado», 8 líneas conservadas, subtítulo explicativo, teléfonos en reposo y botón «Nueva llamada» habilitado y alcanzable en ambas resoluciones.
- **Ruta real de ASR y detector**: ejecutado ejemplo `SC-WA-CODE-01` (22 s) contra `servidor.py` real (PID 51601, commit `4574df6`, puerto 51122). HTML verificado con `cmp` contra `panel.html` (coincidencia idéntica de 82988 bytes). Zipformer streaming emitió parciales y finales por canal; detector por reglas evaluó 4 segmentos y emitió aviso en `t_a = 18.456 s` con motivo `REQUEST_AUTH_CODE` y cita exacta. Carpeta de llamada cerrada y guardada con `manifiesto.json`, `detector.jsonl`, `actualizaciones.jsonl` y `estereo.wav`.
- **Pruebas de regresión**: 6/6 pruebas Node y 73/73 pruebas Python unittest pasando sin fallos.

Capturas generadas:
- [Notebook con aviso y detalles desplegados, 1366 × 768](2026-10-30-presentacion-115-notebook-1366x768.png).
- [Proyección horizontal con aviso y detalles desplegados, 1920 × 1080](2026-10-30-presentacion-115-proyeccion-1920x1080.png).
- [Escena final conservada en notebook, 1366 × 768](2026-10-30-presentacion-115-notebook-fin-1366x768.png).
- [Escena final conservada en proyección, 1920 × 1080](2026-10-30-presentacion-115-fin-conservado-1920x1080.png).

## Límites

Una captura en resolución de proyector es una validación de maquetación y legibilidad digital, no un ensayo físico en sala con público real ni acústica ambiental. El video hardcodeado sigue pendiente para el cierre en #53. Los ensayos con personas o en sala mantienen sus propios alcances (D05, D08, D09, D10). No se modificaron modelos, prompts, umbrales ni se ejecutó la reserva.
