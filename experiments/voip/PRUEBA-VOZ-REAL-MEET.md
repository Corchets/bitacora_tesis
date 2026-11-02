# Prueba con voz real por Meet: checklist

Para Luciano y otra persona. Cubre [#84](https://github.com/Corchets/bitacora_tesis/issues/84),
[#85](https://github.com/Corchets/bitacora_tesis/issues/85),
[#86](https://github.com/Corchets/bitacora_tesis/issues/86) y
[#94](https://github.com/Corchets/bitacora_tesis/issues/94). El paso a paso de cada llamada está en la
[hoja de diálogos](../asr-local/voz-real/HOJA-DIALOGOS.md); el de Meet, en la [guía](GUIA-MEET-WHATSAPP.md).

> Lo que salga son unas pocas llamadas guionadas en una notebook: sirve para ver si el recorrido anda
> con voz real. No es rendimiento del detector ni resuelve [D09](../../docs/gestion/MAPA-DECISIONES.md#d09--elegir-asr-y-detector).

## Qué se prueba

> **Decisión de Luciano (2026-11-02):** una sola corrida con otra persona para cerrar lo que necesita una
> llamada: Gemma 4 E2B como detector y las dos opciones de silencio de
> [PLAN-VOZ-REAL §12.9](../asr-local/PLAN-VOZ-REAL.md#129-dos-candidatos-para-comparar-en-diálogos-reales-2026-10-30).

**Lo que queda fijo:** **Detector** = «Gemma 4 E2B con Tito viejo» (`gemma4:e2b-it-q4_K_M`, Tito con umbral 0,5,
prompt `tarea`, `num_ctx` 4096, seed 42); ASR Parakeet TDT 0.6B v3; **Otra persona** = pestaña de Meet con
audio compartido; **Persona protegida** = micrófono; «Cancelar eco» igual toda la corrida.

**Lo que cambia, la opción de silencio:**

| Opción | «Modelo de ASR» en el panel | «Corte de silencio» en el panel | Umbral RMS | Silero |
|---|---|---|---|---|
| **B** | Parakeet · RMS con filtro Silero | 0,8 s | 0,008, lo pone el servidor | 0,5, solo filtra lo que se transcribe |
| **A** | Parakeet · solo Silero | 0,3 s | No se usa; el registro muestra 0,003 | 0,9, decide cuándo corta |

**Orden:**

| Paso | Diálogo | Condición | Opción | Sirve para |
|---|---|---|---|---|
| Antes, sin red | Ejemplo `SC-SOPORTE-CLAVE-01` (decisión de Luciano, 2026-11-02; antes `SC-WA-CODE-01`) | Sin Wi-Fi | B | #86 (plan B) |
| Ensayo, no se anota | D3 | `dialogo` | B | Ver swap y salteadas |
| 1 a 4 | D1, D2, D3, D4 | `dialogo` | B | #85, #86, #94 |
| 5 | D1 con la tele | `dialogo-tv` | B | #94 |
| 6 a 9 | D1, D2, D3, D4, cambiando de lugar si se puede | `dialogo` | A | #94, y A en vivo con Gemma |

**Después, sin personas:** cada audio se vuelve a pasar a ritmo real por la otra opción, con el mismo Gemma:
así A y B se comparan sobre el mismo audio y sin efecto de orden. `resumen_llamada.py` arma la tabla.

```bash
# Otro servidor, con la opción que la llamada no usó; izquierdo = protegida, derecho = otra
python servidor.py --host 127.0.0.1 --puerto 8771 --detector tito-slm --modelo gemma4:e2b-it-q4_K_M \
  --asr parakeet-silero --corte-silencio 0.3 --salida <carpeta fuera de Git>
python cliente.py --servidor ws://localhost:8771 --rol protegida --wav <llamada>/estereo.wav --canal izq &
python cliente.py --servidor ws://localhost:8771 --rol otra --wav <llamada>/estereo.wav --canal der
```

## Antes de citar a la otra persona

- [ ] **Consentimiento ([D06](../../docs/gestion/MAPA-DECISIONES.md#d06--definir-corpus-y-piloto)):** persona adulta, consentimiento firmado **antes** de grabar, con domicilio y contacto reales completados fuera de Git.
- [ ] **Si no es del equipo, Luciano lo confirma antes:** el tutor aprobó el 2026-10-28 el esquema para [adultos del equipo](../../docs/gestion/seguimientos/2026-10-28.md); D06 menciona familiares, pero esa aprobación no.
- [ ] **Anotado en [#94](https://github.com/Corchets/bitacora_tesis/issues/94):** solo que hay consentimiento y la fecha, sin nombre ni datos de contacto.
- [ ] **Queda claro con la otra persona:** el audio queda local bajo resguardo de Mateo, fuera de Git, y no se publica su voz.

## Antes de la primera llamada

- [ ] Los dos con **auriculares** y el **micrófono encendido en Meet**: con otra persona, a diferencia de la [guía](GUIA-MEET-WHATSAPP.md) para probar solo, tiene que escucharte. En la notebook, todo cerrado salvo Chrome, Meet y el panel.
- [ ] El servidor anda: `curl http://localhost:8765/detector` dice `tito-slm` y `gemma4:e2b-it-q4_K_M`. **Con el tag completo:** `gemma4:e2b` a secas es otro artefacto.
- [ ] `ollama list` muestra para ese tag el digest `b37049369adf…`, el de la matriz #101.
- [ ] La copia del servidor tiene la marca de Tito en Presentación (commit `feat(voip): marcar en Presentación…`) y recargaste la página.
- [ ] Panel: lo de [Qué se prueba](#qué-se-prueba), con la opción de esa ronda. El corte arranca en 0,9 s: **hay que escribirlo a mano** al empezar cada ronda.
- [ ] **Una llamada de ensayo con D3, antes de grabar en serio.** Parakeet con E2B anduvo con un ejemplo TTS el 2026-11-02, pero con voz por Meet no se midió. Si la Mac entra en swap o crecen las salteadas, pará y anotalo: no cambies de opción dentro de una ronda.
- [ ] **Si pasaron más de 10 minutos sin consultas, correr antes el ejemplo `SC-WA-CODE-01`:** Ollama descarga el modelo a los 10 min y el panel no lo recalienta al iniciar. Sin esto, la primera consulta sale en frío, justo cuando Tito activa.

## Las llamadas

Una sola toma por llamada. D1, D2 y D4 son estafa; D3 es legítima.

- [ ] **Plan B de #86:** el ejemplo del soporte, en la misma notebook y sin red. Resultado en la [corrida](corridas/2026-11-02-voz-real-meet.md#plan-b-sin-red-86).
- [ ] **Opción B:** D1 · D2 · D3 · D4 · D1 con la tele de fondo (`dialogo-tv`)
- [ ] **Opción A:** D1 · D2 · D3 · D4. Si se puede, cambiando de lugar (cambia la columna `voz`).

## Qué registrar en cada llamada

Durante la llamada solo se anota lo que no queda en los registros: palabras cambiadas y lo raro (eco, cortes, swap).
Lo demás sale de `python resumen_llamada.py --desde <id> --voz-protegida <voz> --voz-otra <voz> --tele <id>`.

**En [`pruebas.csv`](../asr-local/voz-real/pruebas.csv), dos filas por llamada** (una por canal), que imprime ese comando:

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
