# Datos revisados y particiones verificables para evaluar a Tito (#96)

> **Estado: propuesta sin discutir.** Paquete preparado, uso no habilitado.
> Decisiones abiertas: [D07](../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico)
> y [D08](../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

## Qué hay

- [datos_tito.py](datos_tito.py): recorrido público conversaciones → prefijos →
  particiones → manifiesto → informe. Solo stdlib, sin descargas ni modelos.
  Nunca lee la reserva: la rechaza por identificador/partición.
- [tests/test_datos_tito.py](tests/test_datos_tito.py): pruebas de
  comportamiento con dobles (incluyen regresiones de cada fallo
  corregido). Se corren sin red ni GPU:
  `python -m unittest tests.test_datos_tito` desde este directorio.

## Contratos reutilizados (no modificados)

`casos.py` (`Linea` —reutilizada directamente, sin dataclass duplicada—,
`CLASES`, `PEDIDOS`, `ETIQUETAS`, `EVENTOS`), `correr.procesar_caso` (recorrido
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

- Cumple: inventario con procedencia y exclusiones; rechazo de cruces
  (semilla, familia, par, grupos semánticos), conversaciones completas
  duplicadas entre particiones aun con la misma clase, conflictos de
  referencia para diálogos duplicados, identificadores duplicados y
  referencias inválidas (vocabulario de clase/pedido/evento/etiqueta,
  rangos y tipos de líneas, coherencia pedido–`T_R`–`T_C`–evidencia);
  las ocho históricas solo entran como regresión; el diagnóstico es una
  partición disjunta verificada dentro del recorrido (no en un helper
  desconectado); prefijos con supervisión solo del texto visible y
  `clase_conversacion` como metadato final nunca usado como etiqueta del
  prefijo; manifiesto reproducible con fecha inyectable; reserva rechazada
  sin leerla. Una línea suelta repetida (un saludo común en llamadas
  distintas) no cuenta como duplicado. Una legítima sin pedido crítico no
  inventa evidencia (admite lista vacía; lo presente se valida igual).
  Coherencia pedido–`T_R`–`T_C`: se reutiliza el contrato vigente de
  `casos.py` sin modificarlo (`T_C` posterior estricto a `T_R`, rechaza
  `T_C <= T_R`).
  Las entradas inválidas (etiquetas o eventos mal formados, evidencia no
  lista, referencia con otra estructura) vuelven informe no evaluable en
  vez de romper el recorrido. La referencia acepta `Referencia` o dict
  con los mismos campos.
- Pendiente (bloquea habilitar el uso): revisión humana efectiva con
  originales, desacuerdos y adjudicaciones; acuerdo de composición, tamaño,
  reglas de referencia y proporciones (coordinar con #32/#55); cobertura
  real de la muestra; diagnóstico con material revisado. El módulo informa
  cada bloqueo exacto (`puede_habilitarse`, `informe_validacion`) en vez de
  completar artificialmente. No se inventan revisores, acuerdos, cuotas ni
  etiquetas revisadas. La puerta es fail-closed: exige revisión trazable
  (lista no vacía de revisores identificables, originales conservados con
  su ruta o identificador, desacuerdos y adjudicaciones relacionados por
  caso o id, conteo de revisadas cruzado con el manifiesto) y acuerdo con
  contenido (composición, tamaño, reglas de referencia, proporciones
  presentes y no vacíos); ningún dict o lista vacío, ningún faltante y
  ninguna discrepancia con el manifiesto habilita. El software no
  autentica personas ni fija cuotas o metodología nueva: solo verifica la
  estructura que el equipo aporta fuera del módulo.
  El `informe_validacion` conserva el conteo y las huellas del manifiesto;
  la puerta rechaza lo declarado cuando discrepa del manifiesto o la
  revisión está incompleta.

> **Estado: propuesta sin discutir.** Los criterios estructurales de la
> puerta (sin cuotas de revisores ni longitudes mínimas) se proponen
> enlazados a
> [D07](../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico)
> y [D08](../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

## Propuestas sin discutir

- Tamaño y proporciones entrenamiento/validación/evaluación, ventanas
  candidatas y criterio de insuficiencia para fine-tuning: se proponen y
  acuerdan antes de producir material dependiente, con
  [D07](../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico)
  y [D08](../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).
  Esta entrega no cierra ninguna de las dos ni fija cuotas.
