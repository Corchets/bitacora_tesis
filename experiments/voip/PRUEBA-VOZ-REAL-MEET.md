# Prueba con voz real por Meet: checklist

Para Luciano y otra persona. Cubre [#84](https://github.com/Corchets/bitacora_tesis/issues/84),
[#85](https://github.com/Corchets/bitacora_tesis/issues/85),
[#86](https://github.com/Corchets/bitacora_tesis/issues/86) y
[#94](https://github.com/Corchets/bitacora_tesis/issues/94). El paso a paso de cada llamada está en la
[hoja de diálogos](../asr-local/voz-real/HOJA-DIALOGOS.md); el de Meet, en la [guía](GUIA-MEET-WHATSAPP.md).

> Lo que salga son unas pocas llamadas guionadas en una notebook: sirve para ver si el recorrido anda
> con voz real. No es rendimiento del detector ni resuelve [D09](../../docs/gestion/MAPA-DECISIONES.md#d09--elegir-asr-y-detector).

## Antes de citar a la otra persona

- [ ] **Consentimiento ([D06](../../docs/gestion/MAPA-DECISIONES.md#d06--definir-corpus-y-piloto)):** persona adulta, consentimiento firmado **antes** de grabar, con domicilio y contacto reales completados fuera de Git.
- [ ] **Si no es del equipo, Luciano lo confirma antes:** el tutor aprobó el 2026-10-28 el esquema para [adultos del equipo](../../docs/gestion/seguimientos/2026-10-28.md); D06 menciona familiares, pero esa aprobación no.
- [ ] **Anotado en [#94](https://github.com/Corchets/bitacora_tesis/issues/94):** solo que hay consentimiento y la fecha, sin nombre ni datos de contacto.
- [ ] **Queda claro con la otra persona:** el audio queda local bajo resguardo de Mateo, fuera de Git, y no se publica su voz.

## Antes de la primera llamada

- [ ] Los dos con **auriculares**. En la notebook, todo cerrado salvo Chrome, Meet y el panel.
- [ ] El servidor anda: `curl http://localhost:8765/detector` dice `tito-slm` y `gemma4:e2b-it-q4_K_M`. **Con el tag completo:** `gemma4:e2b` a secas es otro artefacto.
- [ ] `ollama list` muestra para ese tag el digest `b37049369adf…`, el de la matriz #101.
- [ ] La copia del servidor tiene la marca de Tito en Presentación (commit `feat(voip): marcar en Presentación…`) y recargaste la página.
- [ ] Panel: **Detector** = «Gemma 4 E2B con Tito viejo»; **ASR** = Parakeet con filtro o con Silero, el mismo toda la sesión. **Otra persona** = pestaña de Meet con audio compartido; **Persona protegida** = micrófono.
- [ ] **Una llamada de ensayo con D3, antes de grabar en serio.** E2B se probó en esta Mac solo con Zipformer; Parakeet con E2B y Meet no se midió. Si la Mac entra en swap o crecen las salteadas, pará y anotalo: no cambies de ASR a mitad de sesión.
- [ ] **Si pasaron más de 10 minutos sin consultas, correr antes el ejemplo `SC-WA-CODE-01`:** Ollama descarga el modelo a los 10 min y el panel no lo recalienta al iniciar. Sin esto, la primera consulta sale en frío, justo cuando Tito activa.

## Las llamadas

Una sola toma por llamada. D1, D2 y D4 son estafa; D3 es legítima.

- [ ] D1 · [ ] D2 · [ ] D3 · [ ] D4 · [ ] D1 con la tele de fondo (`dialogo-tv`)
- [ ] Si se puede, cambiar de lugar y repetir D1 a D4 (cambia la columna `voz`).
- [ ] **Plan B de #86:** la llamada de ejemplo, en la misma notebook y sin red.

## Qué registrar en cada llamada

**En [`pruebas.csv`](../asr-local/voz-real/pruebas.csv), dos filas por llamada** (una por canal), como indica la hoja:

```text
<id>,5,<voz>,dialogo,D1,protegida,<nota sin comas>
<id>,5,<voz>,dialogo,D1,otra,<nota sin comas>
```

**En la tabla de la corrida**, la que se arma al terminar. Casi todo sale del Historial o de `detector.jsonl`:

| Dato | De dónde sale |
|---|---|
| `id`, diálogo, condición (`dialogo` o `dialogo-tv`) | Historial y lo que hicieron |
| ¿Hubo aviso? `T_A` y frase citada | Presentación / `manifiesto.json` |
| Frase donde se marcó «Tito activó al modelo» y puntaje | Presentación / `indicio_linea` e `indicio_puntaje` |
| Frases «Sin consulta» | `consulta` = `omitida` |
| Consultas al modelo: cantidad, primera, mediana y máximo, **sin contar las «Sin consulta»** | `ms_detector` donde `consulta` ≠ `omitida` |
| Salteadas y fallos | `manifiesto.json` |
| Lo que se vio raro: eco, cortes, aviso en D3, swap, palabras cambiadas | A mano, en una línea |

En D3, un aviso es una **falsa alarma**: anotala tal cual. En D1, D2 y D4, la falta de aviso también se anota.

## Al terminar

- [ ] `llamadas/` no se sube. A `corridas/` van solo `manifiesto.json`, `actualizaciones.jsonl` y `detector.jsonl`, sin el WAV. Comprobá con `git status` que no entre audio.
- [ ] Por #85, repetí una llamada con `python replay.py --actualizaciones <llamada>/actualizaciones.jsonl --detector tito-slm --modelo gemma4:e2b-it-q4_K_M`.
- [ ] Sacá una captura de Presentación con la marca de Tito y una frase «Sin consulta», sin datos personales en pantalla.
- [ ] Problemas nuevos, a riesgos o a un issue (#86). Después, completá y publicá el [comentario de cierre de #85](corridas/2026-11-02-pendientes-tito-gemma.md#borrador-comentario-de-cierre-de-85).
