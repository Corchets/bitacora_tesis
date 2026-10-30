# Reporte #99 — frase y contexto con RoBERTuito congelado

Fecha: 2026-10-30. Encoder `pysentimiento/robertuito-base-uncased` revision `20cb399e4b93` congelado. Seed 42.

## Auditoria semantica (otro worker)

Artefacto validado con umbral 0.876 (conservador:min_par (solapa con azar; se excluye de más)). Familias excluidas del ajuste: 0.
Supervision: `SUPERVISION-CONTEXTUAL-TITO-99-2026-10-29.jsonl` modelos ['gemma4:e4b'].
Cota lexica propia solo auxiliar, sin valor semantico.

## Criterio operativo de oportunidad

Criterio operativo de desarrollo (exploratorio, vinculado a D08): derivacion <= T_R sobre referencias sin revision humana (#98). Sin T_R el caso es no evaluable y se informa aparte con ambos margenes T_R/T_C. No cierra arquitectura ni margen final.

## Entrenamiento

4246 ejemplos (ver artefacto 3843 banco + prefijos unos). 6 clasificadores, 18 configuraciones.

## Clasificacion por prefijo (elegida, solo revisados)

Revisados: 114, inciertos: 8, sin registro: 0. F1 (solo revisados): 0.6286.
Recarga verificada sin ajuste: artefactos recargados desde disco y puntaje lineal+sigmoide reverificado con suma independiente en los primeros 5 prefijos de cada configuracion; sin ajuste en evaluar.

## Seleccion (solo validacion)

Elegida: `historial_acumulado/C=1.0/u=0.5`. Frontera historial: ['historial_acumulado/C=0.1/u=0.3', 'historial_acumulado/C=0.1/u=0.5', 'historial_acumulado/C=0.1/u=0.7', 'historial_acumulado/C=1.0/u=0.3', 'historial_acumulado/C=1.0/u=0.5', 'historial_acumulado/C=1.0/u=0.7', 'historial_acumulado/C=10.0/u=0.5', 'historial_acumulado/C=10.0/u=0.7']. Controles frase: ['frase_actual_control/C=0.1/u=0.3', 'frase_actual_control/C=0.1/u=0.5', 'frase_actual_control/C=0.1/u=0.7', 'frase_actual_control/C=1.0/u=0.3', 'frase_actual_control/C=1.0/u=0.5', 'frase_actual_control/C=1.0/u=0.7', 'frase_actual_control/C=10.0/u=0.3', 'frase_actual_control/C=10.0/u=0.5', 'frase_actual_control/C=10.0/u=0.7'].

| config | omisiones | legit_deriv | consultas_media |
|---|---|---|---|
| `frase_actual_control/C=0.1/u=0.3` | 1/4 | 3/6 | 10.4 |
| `frase_actual_control/C=0.1/u=0.5` | 1/4 | 2/6 | 10.8 |
| `frase_actual_control/C=0.1/u=0.7` | 1/4 | 1/6 | 11.2 |
| `frase_actual_control/C=1.0/u=0.3` | 1/4 | 3/6 | 10.9 |
| `frase_actual_control/C=1.0/u=0.5` | 1/4 | 3/6 | 11.1 |
| `frase_actual_control/C=1.0/u=0.7` | 1/4 | 1/6 | 11.2 |
| `frase_actual_control/C=10.0/u=0.3` | 1/4 | 2/6 | 11.0 |
| `frase_actual_control/C=10.0/u=0.5` | 1/4 | 2/6 | 11.1 |
| `frase_actual_control/C=10.0/u=0.7` | 1/4 | 2/6 | 11.1 |
| `historial_acumulado/C=0.1/u=0.3` | 1/4 | 2/6 | 10.1 |
| `historial_acumulado/C=0.1/u=0.5` | 1/4 | 2/6 | 10.4 |
| `historial_acumulado/C=0.1/u=0.7` | 2/4 | 1/6 | 11.3 |
| `historial_acumulado/C=1.0/u=0.3` | 1/4 | 2/6 | 10.1 |
| `historial_acumulado/C=1.0/u=0.5` | 1/4 | 2/6 | 10.3 |
| `historial_acumulado/C=1.0/u=0.7` | 1/4 | 2/6 | 10.3 |
| `historial_acumulado/C=10.0/u=0.3` | 1/4 | 3/6 | 7.7 |
| `historial_acumulado/C=10.0/u=0.5` | 1/4 | 2/6 | 10.3 |
| `historial_acumulado/C=10.0/u=0.7` | 1/4 | 2/6 | 10.3 |

## Criterio de fine-tuning (#100)

Baseline viejo (frase, u=0.5): 0/4 omisiones, 3/6 legitimas derivadas.
Elegido: 1 omisiones, 2 legitimas derivadas.
evaluar fine-tuning en #100: ningun candidato congelado conserva ambas fallas frente al viejo en validacion y hay errores observables que lo justifican.

## Limites

- Seleccion solo con validacion de desarrollo.
- Criterio oportuna operativo exploratorio (D08); sin T_R no evaluable, con ambos margenes.
- F1 solo sobre prefijos revisados; inciertos en cobertura.
- Cota lexica auxiliar; no es evidencia semantica suficiente.
- Nulos fuera de perdida y metricas, con cobertura.
- Sin revision humana inventada; puerta formal intacta.
- Reserva no leida; veinte de comparacion sin usar.
