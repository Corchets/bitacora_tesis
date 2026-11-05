# Cierre de #97 — Primer aviso operativo, preparación e instrumentación del ensayo Tito

Fecha: 2026-10-27. Alcance: #97 implementado; #96 explícitamente PARCIAL.
No cierra decisiones (D07/D08/D09 abiertas), no crea ADR, no toca
[MAPA-DECISIONES.md](../../docs/gestion/MAPA-DECISIONES.md) ni
[ARQUITECTURA.md](../../docs/ingenieria/ARQUITECTURA.md) ni código en este documento.
Bitácora: [2026-10-semana-04.md](../../docs/gestion/bitacora/2026-10-semana-04.md).
Riesgos: [REGISTRO-RIESGOS.md](../../docs/gestion/REGISTRO-RIESGOS.md) (R05, R25).

> **Nota de alcance confirmada por el usuario el 2026-10-27:** #96 queda PARCIAL
> (validación de datos implementada; habilitación bloqueada sin revisión humana
> ni acuerdos) y #98–#100 no están implementados (fases bloqueadas). No se afirma
> #96 completo. Los dobles deterministas no se presentan como calidad aprendida
> ni la revisión automática como revisión humana. Revisiones terminadas:
> Standards 0 violaciones duras / 2 smells menores opcionales; Spec #97
> conforme / #96 parcial; últimos hallazgos (1 redacción histórica, 2 campo
> muerto) corregidos y revisados por el coordinador con 31
> `tests.test_primer_aviso` verdes. Campo fecha explícita documentado, no
> requiere cambio. Workers Muse usaron muse-spark-1.3-contributor:
> implementación y revisiones en high; correcciones de otros workers en
> medium/low. Codex coordinó y revisó la integración.
> Sin decisiones cerradas ni calidad aprendida.

## Qué se implementó (#97)

- Modo operativo en `correr.py`: cada llamada termina en su primer aviso válido;
  `--seguir-tras-aviso` conserva el recorrido completo solo como diagnóstico,
  separado del costo operativo hasta el aviso.
- Preparación separada del costo operativo; `resumen.py`/`comparar.py` reportan
  costos Tito+SLM por componentes, con fallos y ausencias, más trayectorias.
- `tito_real.py` reutiliza el artefacto `tito_logreg.json` sin reentrenar;
  corrección de puntajes históricos (43 puntajes hasta activación, no 105).
- Documentación operativa en [README.md](README.md#verificación-sin-modelos-ni-corridas-históricas-97),
  preparación de datos en [DATOS-TITO.md](DATOS-TITO.md) / [datos_tito.py](datos_tito.py).

## Evidencia observable

- Commits: `057f388`, `00b0f58`, `566c6f9`, `b9a154c`, `a60b898`, `8e3caa7`
  (`057f388` y `566c6f9` corresponden a #96 parcial; `8e3caa7` es posterior a
  `a60b898` y aclara el alcance descriptivo de costos históricos).
  Workers Muse usaron muse-spark-1.3-contributor: implementación y
  revisiones en high; correcciones de otros workers en medium/low. Codex
  coordinó y revisó la integración.
- Suite del coordinador desde `experiments/slm-directo`:
  `python3 -m unittest discover -s tests -v` → 161 tests OK, 1 skipped
  (reserva fuera del repo en copia pública); 50 pruebas de datos en
  [tests/test_datos_tito.py](tests/test_datos_tito.py); luego 31 dirigidas
  `tests.test_primer_aviso` verdes tras la última corrección; compilación
  Python verificada. Sin modelos ni descargas.
- Verificación dirigida sin modelos:
  `python -m unittest tests.test_primer_aviso tests.test_ensayo tests.test_filtro_tito -v`.
- Revisiones terminadas: Standards 0 violaciones duras / 2 smells menores
  opcionales; Spec #97 conforme / #96 parcial.

## Decisiones abiertas y próxima acción

- D07/D08/D09 siguen abiertas; procedencia, revisión humana y acuerdos pendientes.
- Próxima acción: revisión humana y acuerdos de habilitación (#96), después #98
  según dependencias nativas de #95.

## Bloque Markdown listo para copiar en GitHub

```markdown
Closes #97.

Resumen: primer aviso operativo implementado (corte por llamada + diagnóstico
separado con `--seguir-tras-aviso`), preparación separada del costo operativo,
reportes con costos Tito+SLM por componentes/fallos/ausencias y corrección de
puntajes históricos; `tito_real.py` reutiliza el artefacto sin reentrenar.

Evidencia observable: commits 057f388, 00b0f58, 566c6f9, b9a154c, a60b898,
8e3caa7 (este último posterior a a60b898: alcance descriptivo de costos
históricos); `python3 -m unittest discover -s tests -v` desde
`experiments/slm-directo`: 161 tests OK (1 skipped: reserva fuera del repo),
50 pruebas de datos en `tests/test_datos_tito.py`; 31 dirigidas
`tests.test_primer_aviso` verdes tras la última corrección; compilación
Python verificada; sin modelos ni descargas. Los dobles son
deterministas y no miden calidad aprendida. Workers Muse usaron
muse-spark-1.3-contributor: implementación y revisiones en high;
correcciones de otros workers en medium/low. Codex coordinó y revisó la
integración.

Decisiones abiertas: D07/D08/D09 sin cerrar; sin ADR en este cierre.
Revisiones terminadas: Standards 0 violaciones duras / 2 smells menores
opcionales; Spec #97 conforme / #96 parcial.

Próxima acción: completar revisión humana y acuerdos de #96 (PARCIAL) y luego
#98 según dependencias nativas de #95.

Nota: #96 queda explícitamente PARCIAL y #98–#100 no están implementados
(fases bloqueadas, confirmado por el usuario el 2026-10-27).
```
