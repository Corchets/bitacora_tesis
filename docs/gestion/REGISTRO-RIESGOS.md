# Registro de riesgos

Escala: probabilidad e impacto de 1 (bajo) a 5 (crítico). Revisar semanalmente.
Los IDs se conservan para que las referencias históricas sigan identificando el mismo riesgo;
los IDs retirados no se reutilizan.

| ID | Riesgo | P | I | Señal temprana | Mitigación | Contingencia | Dueño | Estado |
|---|---|---:|---:|---|---|---|---|---|
| R04 | Corpus pequeño o artificial | 4 | 4 | pocas familias/hablantes, diálogos leídos o solo pedidos directos en conversaciones breves | [catálogo](../corpus/CATALOGO-ESCENARIOS.csv), piloto y fichas semi-estructuradas; comprobar diversidad antes de ampliar; revisar pedidos indirectos y contexto prolongado, sin tomar el [ejemplo conceptual de #20](../ingenieria/ARQUITECTURA.md#4-primer-par-escrito-del-escenario-al-aviso) como prueba de cobertura; la [matriz de fuentes externas](../investigacion/SINTESIS-ESTADO-DEL-ARTE.md#23-datasets-y-límites-de-reutilización-recuperación-de-43) registra diferencias de dominio y anotación que revisar antes de reutilizar datos | revisar casos y reportar límites del corpus | equipo / #39 | abierto; límite de casos directos señalado por Mateo el 2026-10-07; sin validación empírica |
| R05 | Fuga de información entre entrenamiento y test | 4 | 5 | variantes de una semilla aparecen en splits distintos o se ajusta mirando el test | agrupar por semilla; reservar test y separar datos usados para ajustar | rehacer splits y resultados afectados | por autoasignar | abierto |
| R06 | ASR falla con español argentino y ruido | 4 | 4 | pierde códigos, pedidos u otros términos críticos | medir con audio propio y comparar transcripción manual frente a ASR | probar otro ASR y reportar la degradación | por autoasignar | abierto; sin benchmark del corpus propio |
| R07 | Falsas alarmas inutilizan el sistema | 4 | 4 | alertas en llamadas legítimas o un solo pico sostiene la alerta | negativos difíciles; calibrar con datos de desarrollo y revisar la persistencia en [D08](MAPA-DECISIONES.md#d08--congelar-protocolo-experimental) | priorizar pedidos críticos y reportar el límite | equipo / evaluación | abierto; la [corrida exploratoria del 2026-09-28](../investigacion/CONTRASTE-NLP-TEORIA-Y-LABORATORIO.md#3-cifras-del-marco-contra-cifras-medidas) reporta 5/10 falsas alarmas de goteo; no es evaluación final |
| R08 | Modelo demasiado pesado para móvil | 3 | 3 | no sigue el ritmo de la llamada o supera el presupuesto de memoria | medir pipeline completo contra [criterios de prefactibilidad](../investigacion/PREFACTIBILIDAD-TECNICA.md); la [corrida del 2026-09-28](../investigacion/CONTRASTE-NLP-TEORIA-Y-LABORATORIO.md#3-cifras-del-marco-contra-cifras-medidas) ocupa ~1,7 GB en encoder + SLM, sin ASR, frente a 1024 MB de presupuesto | probar un detector más liviano; declarar que medir en PC no prueba viabilidad Android | equipo / [#51](https://github.com/Corchets/bitacora_tesis/issues/51) | abierto; esa configuración excede el presupuesto, otras siguen pendientes |
| R09 | Integración ocurre demasiado tarde | 4 | 4 | módulos aislados o corrida que solo reproduce su autor | obtener una primera ejecución audio→ASR→reglas→aviso después de probar el procedimiento del piloto; otra persona la reproduce y se comprueba el flujo en cada hito | priorizar replay reproducible como demo base | por autoasignar | abierto |
| R14 | El aviso por regla crítica infla `Preventive@δ` | 3 | 4 | se confunde un pedido detectado con una anotación humana o se mezclan las fuentes de alerta | anotar el pedido real y reportar alertas por reglas y por acumulación temporal por separado, según [METRICAS.md](../evaluacion/METRICAS.md) | recalcular resultados con las marcas y fuentes correctas | por autoasignar | abierto |

## Reglas

- P×I igual o mayor a 15 requiere acción en el ciclo actual.
- Un riesgo materializado pasa al seguimiento como bloqueo con fecha y dueño.
- La ausencia de novedad no elimina el riesgo; solo evidencia nueva permite bajar
  probabilidad o impacto.
- Toda ampliación de alcance agrega o actualiza al menos un riesgo.
