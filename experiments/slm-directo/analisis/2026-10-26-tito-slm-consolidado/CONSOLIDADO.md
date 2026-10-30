# Consolidado Tito→SLM: verificación de la reproducción (#74, parte de #68)

2026-10-26. Seis artefactos × ocho conversaciones × dos variantes =
**96 evaluaciones de conversación** (1260 filas de actualización), ejecutadas
el 2026-10-26 en la PC Linux de Ignacio (Ollama 0.40.8, GPU RTX 3060 12 GB).
Tito real único (`tito_logreg.json`, sha256
`fb601eaa…5098eccd`, umbral 0,5) para las seis comparaciones.

Tablas cruzadas generadas desde las salidas crudas: [TABLAS.md](TABLAS.md).
Vista interactiva por modelo, conversación y ticket: [informe visual](graficos/index.html)
([regeneración](graficos/README.md)). Usa las salidas guardadas, sin nueva inferencia.
Manifiesto auditable: [cobertura.json](cobertura.json).
Procedimiento: [consolidar.py](consolidar.py) (solo lee CSV, sin inferencia) y
[regenerar.sh](regenerar.sh) (re-ejecuta `comparar.py` × 6 y verifica
identidad byte a byte). Detalle por modelo y conversación en cada
`corridas/<fecha>_<modelo>-comparacion/comparacion.md`.

## 1. Cobertura verificada

- `consolidar.py` confirma 96/96: cada corrida canónica trae 8 casos con 105
  filas por variante (directa: 105 consultas SLM; filtrada: 70 consultas SLM
  + 35 evitadas). Tito puntuó solo hasta la activación de cada caso: 43
  puntajes por modelo (no 105; corrección #97), y las 35 evitadas son las
  líneas previas a cada activación. Toda conversación filtrada derivó al
  menos una vez, así que ninguna cayó en el caso «nunca derivada»; el
  evaluador igual conserva ese estado con su denominador (`resumen.py:212`).
- Los cinco digests Qwen coinciden con la tabla de #68; no se usaron los alias
  históricos sin sufijo (bare `2b`/`4b`) ni se repitió ningún artefacto.
  Los dos 0.8B tienen digests distintos y se mantuvieron separados.
- **Discrepancia detectada en #68:** su tabla trae el digest de
  `qwen3.5:2b-q8_0` truncado a 62 hex
  (`…ade63c3dbdb…`); el digest completo informado por Ollama y guardado en el
  manifiesto es de 64 hex
  (`0689d440…ade63a3c3dbdb48ab54b130a`). Se adopta el del manifiesto como
  válido y se deja constancia aquí; #68 no se edita desde este ticket.
- **Llama 1B:** digest recuperado
  `22bc6b92…4fbafa02`, declarado sin afirmar identidad con el artefacto de la
  cascada histórica (#73). Salida estructurada verificada (`think: false`,
  `num_ctx` 4096 aceptados); 5 fallos `salida_cortada` en la variante directa
  (TR-04 L10/L12/L14/L17, TR-11 L8) conservados como fallos, no como
  predicciones de legitimidad.
- **Corrida superada excluida:** `2026-10-26_132916_qwen4b-comparacion`
  (mismo comando que la canónica `…_133838`) falló con
  `tito_error: ModuleNotFoundError` en el primer puntaje de cada caso
  (8 intentos, 0 puntajes; corrección #97: no fueron 105 ejecuciones de Tito)
  y derivó todo por fail-open (105 consultas SLM, 0 evitadas). No integra la
  matriz; se conserva como evidencia del camino de fallo técnico de Tito en
  código real.

## 2. Qué muestran las seis comparaciones

Lectura conjunta (activación selectiva + indicio falible evaluados juntos;
sin atribuir el efecto a uno de ellos por separado):

- **Vishing (4/4 por variante):** los cinco Qwen detectan 4/4 en directo y 4/4
  en filtrado: el filtro no pierde ningún vishing. Llama directo no avisa
  nunca (0/4, con 5 fallos intermedios); filtrado detecta 2/4 (TR-04 L10,
  TR-07 L5) y omite SC-SOPORTE y SC-FAMILIAR.
- **Falsas alarmas (denominador 4 legítimas):** 4b 3→4 (agrega LG-SUPPORT
  L10); 0.8B y 0.8B-q8 2→2 (quita TR-08, agrega TR-06); 2B 0→1 (agrega
  LG-SUPPORT L12); 9B 3→2 (quita TR-11); Llama 0→3 (agrega LG-SUPPORT L9,
  TR-06 L5, TR-11 L9).
- **Derivación idéntica en los seis modelos** (mismo Tito): L8, L9, L1, L5,
  L3, L5, L3, L9 según el caso; 35 consultas evitadas por modelo (las previas
  a cada activación; Tito ejecutó 43 puntajes, corrección #97). El costo en
  ms del filtrado incluye Tito hasta la activación más SLM válido y fallido:
  baja en 2B (55037→46954) y 9B (153222→141504), sube en 4b, 0.8B y Llama
  (p. ej. 4b 97969→113314). Los tokens del filtrado bajan en los seis
  (p. ej. 4b 78900→66127). No se afirma ahorro móvil ni generalización: son
  8 conversaciones sintéticas y ms de laboratorio, no presupuesto de teléfono.

## 3. Sensibilidad TR-04 y TR-07 (mismas predicciones, sin nueva inferencia)

Cada `comparacion.md` calcula ambas lecturas sobre los mismos avisos; la
referencia original no cambia:

- **TR-04** (ref T_R=26/T_C=27, alt 21/22): los avisos caen muy antes del
  pedido en ambas lecturas. P. ej. 4b directo L3: −23 líneas (ref) vs −18
  (alt); filtrado L5: −21 vs −16. Ningún modelo cambia su resultado de
  detección entre lecturas.
- **TR-07** (ref T_R=7/T_C=9, alt 8/9): p. ej. 4b directo L3: −4 vs −5;
  filtrado L5: −2 vs −3. Tampoco cambia ningún resultado.

Conclusión: la lectura alternativa mueve los márgenes en unas pocas líneas
pero no adjudica ni revierte ninguna detección u omisión. Las marcas siguen
provisorias y pendientes de D07.

## 4. Motivos, citas y casos donde el filtro pierde, retrasa o agrega

Revisión de motivos/citas por modelo en la sección «Motivos y citas» de cada
`comparacion.md` (las lecturas de pedido inventado o sospecha reforzada son
del autor del reporte, no del manual; ningún caso tiene revisión humana):

- **Avisos anteriores al pedido:** frecuentes en ambas variantes. SC-SOPORTE
  (T_R L6) avisa en L1–L6 según modelo; TR-04 (T_R L26) avisa entre L3 y L26;
  TR-07 (T_R L7) entre L3 y L9. El motivo suele describir captación («simulan
  ser del banco») más que el pedido mismo.
- **Cita no textual:** 4b filtrado TR-07 L5 concatena dos líneas en la
  evidencia y queda marcada como NO textual en su reporte.
- **Falsas alarmas con motivo asertivo:** TR-06, TR-08 y TR-11 reciben motivos
  de suplantación o pedido («pasame el código», «transferí ahora») en casos
  legítimos; el filtro quita algunas (TR-08 en 0.8B, TR-11 en 9B) y agrega
  otras (LG-SUPPORT en 4b/2B/Llama, TR-06 en 0.8B/Llama).
- **Pierde:** ningún vishing detectado en directo se pierde en filtrado en
  ningún modelo (Qwen 4/4→4/4; Llama 0/4→2/4).
- **Retrasa:** 4b TR-04 L3→L5 y TR-07 L3→L5; 4b TR-11 L4→L9; 9B TR-07 L4→L5;
  0.8B SC-FAMILIAR L8→L9. Todos los avisos retrasados siguen anteriores al
  pedido o al cumplimiento salvo TR-04/TR-07, que ya avisaban antes en directo.
- **Adelanta:** 0.8B TR-04 L20→L6 y TR-07 L9→L5; SC-SOPORTE L6→L4.
- **Agrega:** detecciones en Llama (TR-04, TR-07) y falsas alarmas listadas
  arriba. Activación e indicio se evaluaron juntos: no se puede decir si el
  cambio lo produce el momento de consulta o el texto del indicio.

## 5. Límites de interpretación

- 8 conversaciones sintéticas de desarrollo, 105 líneas; sin test reservado.
- Referencias provisorias sin revisión humana; doble lectura sin adjudicar.
- Umbral 0,5 de Tito: convención exploratoria fijada antes de mirar resultados,
  no probabilidad de fraude ni umbral validado.
- Runtimes históricos heterogéneos entre corridas; posiciones en líneas, sin
  segundos, RTF ni rendimiento móvil.
- Digest de Llama histórico ausente: esta ejecución no prueba identidad con la
  cascada del 2026-09-28 ni se compara contra sus cifras.
- No se cierra D07/D08/D09 ni #51; no se adopta arquitectura ni se demuestra
  generalización.

## 6. Regresiones y auditoría

- `python -m unittest discover -s tests` en `experiments/slm-directo/`:
  79 pruebas OK (1 salteada) el 2026-10-26, incluyendo `test_comparar.py`,
  `test_filtro_tito.py` y `test_tito_real.py` (recorrido completo, umbral
  exacto, persistencia, fail-open, reinicio entre llamadas, denominadores).
- Auditables por corrida: `manifiesto.json` (comando, commit
  `d53bbc1`, parámetros, digests, hardware, librerías Tito), `hardware.json`,
  `chequeo-contrato.json`, `actualizaciones.csv` (traza por línea con
  `consulta`, `tito_puntaje`, `indicio_*`, `ms`, tokens y crudo),
  `resumen.md` y `comparacion.md` regenerables.
- Clasificador único: ajuste seed 42 sobre 5520 textos aceptados
  (banco `bb542e1`, 276 familias; 480 apartados excluidos); RoBERTuito
  congelado rev `20cb399e`; límite 128 tokens, 0 truncamientos.

## 7. Revisión por otra persona

Pendiente al cierre de este reporte: ver [REVISION.md](REVISION.md) (lista de
verificación y alcance declarado). No se atribuye ninguna reproducción de
inferencia no realizada.
