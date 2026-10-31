# Meet y BlackHole con personas reales — cierre de #80 y #88 (2026-10-28)

Llamadas hechas por Luciano el 2026-10-28 desde el panel, con el micrófono como «Persona protegida» y la
pestaña de Meet o BlackHole como «Otra persona». Luciano informó el 2026-10-31 que la prueba con dos
personas (#80) y el ensayo siguiendo solo la guía `/guia` (#88) quedaron hechos; este informe agrega lo
que dicen los manifiestos. No es una medición de calidad de ASR ni del detector.

Audio y manifiestos fuera de Git, en la copia `bitacora_tesis-voip-asr`, `experiments/voip/llamadas/`.
Se leyeron solo los `manifiesto.json`: `inicio_panel.fuentes` dice la fuente de cada canal y
`canales.*.inicio_s` / `desfase_llegada_s` el desfase. Máquina: M1 8 GB.

| Llamada | Otra persona | Duración | Diferencia de inicio entre canales | Diferencia de la mediana de llegada | ASR | Código |
|---|---|---|---|---|---|---|
| `2026-10-28_144435-816207` | Meet | 224,2 s | 0,009 s | 0,007 s | Zipformer | `a37b47e` |
| `2026-10-28_154037-310058` | BlackHole | 59,2 s | 0,012 s | 0,004 s | Zipformer | `a37b47e` |
| `2026-10-28_154150-316810` | BlackHole | 492,8 s | 0,007 s | 0,024 s | Zipformer | `a37b47e` |
| `2026-10-28_155008-022263` | BlackHole | 25,0 s | 0,000 s | 0,000 s | Zipformer | `a37b47e` |
| `2026-10-28_155049-573149` | BlackHole | 5,1 s | 0,014 s | 0,013 s | Zipformer | `a37b47e` |
| `2026-10-28_155059-103695` | BlackHole | 112,3 s | 0,009 s | 0,041 s | Zipformer | `a37b47e` |
| `2026-10-28_155256-834885` | BlackHole | 5,6 s | 0,001 s | 0,001 s | Zipformer | `a37b47e` |
| `2026-10-28_160149-290124` | BlackHole | 228,1 s | 0,007 s | 0,020 s | Zipformer | `a37b47e` |
| `2026-10-28_160836-713154` | BlackHole | 52,5 s | 0,015 s | 0,001 s | Zipformer | `a37b47e` |
| `2026-10-28_160952-234120` | BlackHole | 117,0 s | 0,012 s | 0,012 s | Zipformer | `a37b47e` |
| `2026-10-28_162435-706172` | Meet (eco cancelado) | 95,8 s | 0,030 s | 0,007 s | Zipformer | `22ebc3b` |
| `2026-10-28_202237-600773` | Meet (eco cancelado) | 60,0 s | 0,008 s | 0,003 s | Parakeet | `52129ef` |

- **El desfase entre canales queda en ≤ 0,03 s en las 12**, contra el límite de 0,3 s de #80.
- En `154150`, `155059` y `160149` los dos canales llegan con ~0,4–0,8 s de atraso de mediana respecto del
  reloj, pero el atraso es igual en los dos, así que no desalinea a las personas entre sí.
- El manifiesto dice «BlackHole», no qué aplicación sonaba detrás (WhatsApp Desktop o Meet de escritorio);
  eso sale del informe de Luciano.
