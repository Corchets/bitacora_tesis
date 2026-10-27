# Comentario listo para GitHub — #74 (copiar y cerrar con `Closes #74`)

```markdown
Closes #74.

Consolidado Tito→SLM verificado: 6 artefactos × 8 conversaciones × 2 variantes = 96 evaluaciones.

- Cobertura: `consolidar.py` confirma 96/96 desde las salidas crudas (105 filas por variante y corrida; directa 105 consultas, filtrada 70 + 35 evitadas). Los 5 digests Qwen coinciden con #68; sin alias duplicados y con los dos 0.8B separados. Llama registra digest recuperado `22bc6b92…` sin afirmar identidad histórica (#73). Discrepancia menor: #68 trae truncado a 62 hex el digest del 2B; vale el de 64 hex del manifiesto (`…ade63a3c3…`). La corrida `…_132916_qwen4b` queda excluida y declarada (Tito falló con `ModuleNotFoundError` y derivó todo por fail-open); la canónica es `…_133838`.
- Regeneración sin nueva inferencia: `regenerar.sh` re-ejecuta `comparar.py` × 6 y `consolidar.py`, idéntico byte a byte. Comandos y requisitos del experimento real en el script y en cada `manifiesto.json`.
- Resultados (denominadores 4 vishing + 4 legítimas por variante): Qwen 4/4 en directo y filtrado en los cinco (el filtro no pierde vishing); FA 4b 3→4, 0.8B 2→2, 2B 0→1, 9B 3→2. Llama directo 0/4 con 5 fallos `salida_cortada`, filtrado 2/4 con 3 FA. Derivación idéntica en los seis modelos; costo filtrado con Tito+fallos incluido. Sensibilidad TR-04/TR-07: mismos avisos, solo cambian márgenes en líneas; sin adjudicar. Motivos/citas revisados (avisos previos al pedido, una cita no textual en 4b/TR-07, FA con motivo asertivo); pierde/retrasa/agrega documentados; activación e indicio evaluados juntos, sin atribución causal separada.
- Límites: 8 sintéticas de desarrollo, referencias provisorias, umbral 0,5 exploratorio, runtimes históricos, sin segundos/RTF/móvil. Sin afirmaciones de rendimiento móvil, generalización ni ahorro por contar consultas.
- Auditoría: 79 regresiones OK (1 salteada); manifiestos, `tito_logreg.json` (sha `fb601eaa…`, seed 42, 5520 textos, RoBERTuito congelado), hashes, hardware, versiones y trazas por línea conservados.
- Revisión por otra persona: **pendiente** (`REVISION.md` con lista de verificación). No se declara reproducción de inferencia ajena.
- Barrido: bitácora semanal, D09 (evidencia nueva, sin cerrar D07/D08/D09 ni #51) y R23 (mitigado en desarrollo, con residual) actualizados. No se cierra #68.

Evidencia: `experiments/slm-directo/analisis/2026-10-26-tito-slm-consolidado/` (CONSOLIDADO, TABLAS, cobertura.json, consolidar.py, regenerar.sh, REVISION.md).
Próxima acción: revisión cruzada y, con su resultado, decidir en #68 si conviene otra iteración.
```
