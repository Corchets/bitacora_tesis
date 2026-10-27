# Datos revisados y particiones verificables para evaluar a Tito (#96)

> **Estado: propuesta sin discutir.** Paquete preparado, uso no habilitado.
> Decisiones abiertas: [D07](../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico)
> y [D08](../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

## Qué hay

- [datos_tito.py](datos_tito.py): recorrido público conversaciones → prefijos →
  particiones → manifiesto → informe. Solo stdlib, sin descargas ni modelos.
  Nunca lee la reserva: la rechaza por identificador/partición.
- [tests/test_datos_tito.py](tests/test_datos_tito.py): 20 pruebas de
  comportamiento con dobles. Se corren sin red ni GPU:
  `python -m unittest tests.test_datos_tito` desde este directorio.

## Contratos reutilizados (no modificados)

`casos.py` (`Linea`, clases, eventos), `correr.procesar_caso` (recorrido
incremental), `filtro_tito`/`tito_real` (interfaz `puntuar`, umbral 0,5 en el
flujo) y las constantes de procedencia de `entrenar_tito.py`
(`BANCO_COMMIT`, hashes declarados). La familia de variantes del banco
(`banco_001`, 276 familias) se distingue de la modalidad amplia del corpus
(`banco`, `whatsapp`, `soporte`, ...): solo la primera agrupa variantes
relacionadas que no pueden cruzar particiones.

## Antecedente auditado (solo lectura, sin sobrescribir)

Banco histórico del commit `bb542e1` (`entrenar_tito.py`): 6.000 registros,
5.520 aceptados en 276 familias, 480 apartados en 24 exclusiones con motivo.
Verificado por `auditar_banco_historico()` contra los hashes declarados.
Ese banco ya ajustó el artefacto actual (`tito_logreg.json`): separarlo
retrospectivamente no lo vuelve evaluación independiente; el módulo lo
rechaza (`familias_artefacto`). Las ocho conversaciones de la demo
(`demo.sh`, `CASOS_DEMO`) se conservan como regresión, no como evaluación.

## Estado real al 2026-10-27

- 150 casos de desarrollo válidos (`python casos.py`), **0 con
  `revision_humana: true`**. La revisión del equipo y el acuerdo de
  composición/tamaño/reglas/proporciones no existen todavía.
- La reserva (200 `CV2-T-*`) sigue fuera de esta rama y no se leyó.

## Criterios de #96: qué se cumple y qué falta

- Cumple: inventario con procedencia y exclusiones; rechazo de cruces,
  duplicados incompatibles y referencias faltantes/ambiguas; prefijos con
  etiquetas solo del texto visible (sin copiar la clase final); manifiesto e
  informe reproducibles; reserva rechazada sin leerla.
- Pendiente (bloquea habilitar el uso): revisión humana efectiva con
  originales, desacuerdos y adjudicaciones; acuerdo de composición, tamaño,
  reglas de referencia y proporciones (coordinar con #32/#55); cobertura
  real de la muestra; diagnóstico con material revisado. El módulo informa
  cada bloqueo exacto (`puede_habilitarse`, `informe_validacion`) en vez de
  completar artificialmente. No se inventan revisores, acuerdos, cuotas ni
  etiquetas revisadas.

## Propuestas sin discutir

- Tamaño y proporciones entrenamiento/validación/evaluación, ventanas
  candidatas y criterio de insuficiencia para fine-tuning: se proponen y
  acuerdan antes de producir material dependiente, con
  [D07](../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico)
  y [D08](../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).
  Esta entrega no cierra ninguna de las dos ni fija cuotas.
