# Cierre documental #98 — bloque listo para copiar a GitHub

> NO enviar por API ni push. Pegar manualmente en
> [issue #98](https://github.com/Corchets/bitacora_tesis/issues/98) y cerrar
> desde la UI. No cierra D07/D08/D09 ni #51.

```markdown
Closes #98

## Resumen

Diagnóstico real del Tito histórico sobre la partición de diagnóstico
(commits `b7b9d22`, `464480a`): 10 conversaciones no usadas en el ajuste
(2 vishing / 8 legítimas comunes), 246 líneas/prefijos con entrada aislada
y umbral 0,5, artefacto sin modificar. 2/2 vishing derivan en o antes de
`T_R` (L5 con `T_R`=19; L16 con `T_R`=16); 4/8 legítimas derivadas
—derivación al SLM, NO alarmas— (tasa 0,5). Comparador recargable para
#101: 246/246 puntajes reproducidos (tolerancia absoluta 5e-05).
Marcas provisionales sin revisión humana: describe el desarrollo, no
generaliza a producción.

## Evidencia observable

- [DIAGNOSTICO-TITO-2026-10-29.md](../../experiments/slm-directo/DIAGNOSTICO-TITO-2026-10-29.md)
  y [JSON](../../experiments/slm-directo/DIAGNOSTICO-TITO-2026-10-29.json)
  (`experiments/slm-directo/`): puntajes por línea, derivaciones,
  oportunidad vs `T_R`/`T_C`, costos de arranque/ejecución en ms, huellas.
- Artefacto intacto: `tito_logreg.json`, sha256
  `fb601eaa8ecb8d51e0d37f1d5af00ec4ca41706ef638fe2780ae276e5098eccd`
  (idéntico antes/después). Banco: 5520 aceptadas vistas en ajuste de
  inventario 6000 (480 excluidas). Jaccard máx. banco↔diagnóstico 0,318
  (cota inferior, no prueba de independencia).
- Tests: 14/14 en `tests/test_diagnosticar_tito.py` OK
  (`../../.venv/bin/python -m unittest tests.test_diagnosticar_tito -v`
  desde `experiments/slm-directo/`); suite completa 418 OK (1 skipped:
  reserva fuera del repo). MD regenerable sin inferencia (`--regenerar-md`).
- Fuente de verdad: sección #98 en `experiments/slm-directo/README.md`;
  fila ☑ y artefacto en `docs/gestion/bitacora/2026-10-semana-04.md`;
  evidencia R05/R07 en `docs/gestion/REGISTRO-RIESGOS.md` (sin baja de
  probabilidad, sin mitigación inventada).

## Decisiones

Ninguna decisión abierta se cierra. D07/D08/D09 siguen abiertas; la
auditoría semántica completa es ownership de #99. Derivación ≠ alerta y
omisión ≠ legitimidad quedan como criterio explícito del reporte.

## Próxima acción

#99 (entrenamiento/candidato nuevo con supervisión por prefijo sobre
validación, sin tocar la reserva ni las veinte de comparación).
```

## Verificación ejecutada (2026-10-29, worker #98)

- `tests.test_diagnosticar_tito`: 14/14 OK.
- Suite completa `experiments/slm-directo`: 418 OK, 1 skipped (reserva).
  Ejecución puntual durante el cierre; otros workers siguen editando código,
  así que la validación final de la suite se hará cuando terminen todos los
  cambios. El cierre de #98 se sostiene en las 14 pruebas de diagnóstico,
  los enlaces y los documentos verificados.
- JSON verificado: `resumen` (2/2 vishing, 4/8 legítimas, tasa 0,5),
  `recarga_comparador` (246/246, tolerancia 5e-05), `exposicion_historica`
  (5520/6000/480), `artefacto_historico.sha256` = `fb601eaa…5098eccd`,
  10 recorridos / 246 líneas.
- Enlaces relativos comprobados (bitácora→`experiments/slm-directo/`,
  README→archivos del diagnóstico).
