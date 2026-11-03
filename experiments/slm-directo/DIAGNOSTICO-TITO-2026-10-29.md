# Diagnóstico del Tito histórico sobre la partición de diagnóstico (#98)

Fecha: 2026-10-29. Semilla: 42. Código: `84435777e2d78e7d9d096d5e7af96681268b09d1`.

> Referencias sin revisión humana: marcas provisionales. Diagnóstico exploratorio de desarrollo; no evaluación independiente, no cierra D07/D08/D09.

## Artefacto histórico (sin modificar)

- Ruta: `/home/chato/orca/workspaces/bitacora_tesis/searobin/experiments/slm-directo/tito_logreg.json`; sha256: `fb601eaa8ecb8d51e0d37f1d5af00ec4ca41706ef638fe2780ae276e5098eccd` (idéntico antes/después).
- Encoder: `pysentimiento/robertuito-base-uncased` revisión `20cb399e4b93f270c0cd6b6f533bcb0ada3cb658` congelado, promedio_enmascarado_ultima_capa, hidden 768.
- Tokenizador límite 128 tokens, truncados en ajuste: 0.
- Clasificador: regresión logística {'tipo': 'regresion_logistica', 'semilla': 42, 'C': 1.0, 'solver': 'lbfgs', 'max_iter': 1000}.
- Entrada: frase_actual_aislada. Umbral de derivación: 0.5 (igualdad incluida).

## Partición usada

- Diagnóstico: 10 conversaciones (CV2-D-L-BANCO-008, CV2-D-L-DELIVERY-002, CV2-D-L-ESCUELA-002, CV2-D-L-ESCUELA-003, CV2-D-L-FAMILIAR-004, CV2-D-L-MEDICO-003, CV2-D-L-TRABAJO-002, CV2-D-L-TRABAJO-005, CV2-D-V-BANCO-003, CV2-D-V-BANCO-008).
- Reserva final rechazada sin leer; veinte de comparación excluidas; grupos verificados sin partir.
- Exposición histórica: ajuste con 5520 frases aceptadas del banco (inventario 6000, excluidas 480) commit `bb542e1` (ejemplos `fc1fe13cfba1…`, exclusiones `2b7f88b39f10…`); ninguna conversación entera estuvo en el ajuste.
- Fuentes: particiones `210b58e7ba0a…`, configuración `b7a87c927c9a…`, selección `012080dfdd8d…` (verificadas contra archivos y entre sí, sin deriva).
- Solapamiento léxico banco↔diagnóstico: Jaccard máximo 0.318, mediano 0.15 sobre 246 líneas; 0 líneas ≥ 0,7.

## Recorrido por conversación

| Conversación | Clase | Líneas | T_R | T_C | Derivación | Oportunidad |
|---|---|---:|---|---|---|---|
| CV2-D-L-BANCO-008 | legitima | 21 | None | None | None | sin_derivacion |
| CV2-D-L-DELIVERY-002 | legitima | 25 | None | None | None | sin_derivacion |
| CV2-D-L-ESCUELA-002 | legitima | 26 | None | None | 3 | sin_marca_T_R |
| CV2-D-L-ESCUELA-003 | legitima | 24 | None | None | None | sin_derivacion |
| CV2-D-L-FAMILIAR-004 | legitima | 24 | None | None | 17 | sin_marca_T_R |
| CV2-D-L-MEDICO-003 | legitima | 25 | None | None | None | sin_derivacion |
| CV2-D-L-TRABAJO-002 | legitima | 25 | None | None | 5 | sin_marca_T_R |
| CV2-D-L-TRABAJO-005 | legitima | 27 | None | None | 1 | sin_marca_T_R |
| CV2-D-V-BANCO-003 | vishing | 26 | 19 | 26 | 5 | antes_del_pedido |
| CV2-D-V-BANCO-008 | vishing | 23 | 16 | None | 16 | en_el_pedido |

Posiciones en líneas, no en segundos: el texto no trae timestamps.

### Detalle por conversación (fragmento que deriva o puntajes máximos)

- CV2-D-L-BANCO-008 (legitima): sin derivación; máximos L9=0.1962: «Me queda lejos. ¿Hay algún cajero que acepte más billetes por vez?»; L18=0.093: «Entonces no hay un movimiento que reclamar. Probá con los billetes en mejor estado o consultá en caja.».
- CV2-D-L-DELIVERY-002 (legitima): sin derivación; máximos L16=0.1396: «Dejo anotado: reemplazo solo de tomate, no de rúcula.»; L8=0.0132: «Podemos anotarlo, pero necesitamos que vos confirmes que lo acepta.».
- CV2-D-L-ESCUELA-002 (legitima): deriva en línea 3 con puntaje 0.5919: «segundo año se llama milena paz ensaya con el grupo de la tarde».
- CV2-D-L-ESCUELA-003 (legitima): sin derivación; máximos L21=0.0073: «Es él. Gracias por orientarme.»; L20=0.0046: «Sí, Tomás Varela, segundo B.».
- CV2-D-L-FAMILIAR-004 (legitima): deriva en línea 17 con puntaje 0.5712: «Comprá cuatro nada más, que las otras siguen en la canasta.».
- CV2-D-L-MEDICO-003 (legitima): sin derivación; máximos L3=0.0271: «Ah, justo ese día le toca el control de crecimiento.»; L16=0.0046: «¿Querés conservar el turno original si aparece otro profesional el miércoles?».
- CV2-D-L-TRABAJO-002 (legitima): deriva en línea 5 con puntaje 0.6636: «sí pero en el mensaje que mandó antes aparece 62 capaz copié mal el dato».
- CV2-D-L-TRABAJO-005 (legitima): deriva en línea 1 con puntaje 0.6088: «¿Tenés la notebook gris? La necesita el equipo de sonido para la prueba.».
- CV2-D-V-BANCO-003 (vishing): deriva en línea 5 con puntaje 0.9806: «No es una denuncia Es un recambio preventivo para que no te queden unidades fuera de circulación».
- CV2-D-V-BANCO-008 (vishing): deriva en línea 16 con puntaje 0.7464: «Poné en un sobre todo el efectivo que retiraste, así lo cuenta el operador sin mezclarlo.».

Dificultad: las 8 legítimas son comunes (ninguna `legitima_dificil`); los 2 vishing pertenecen al mismo grupo de escenario (CV2-D-V-BANCO-003). Muestra pequeña: describe, no generaliza.

## Resumen

- Vishing con derivación: 2/2 (con T_R: 2, con T_C: 1).
- Sin derivación: ninguno.
- Omisiones oportunas vs T_R: ninguna.
- Legítimas derivadas: ['CV2-D-L-ESCUELA-002', 'CV2-D-L-FAMILIAR-004', 'CV2-D-L-TRABAJO-002', 'CV2-D-L-TRABAJO-005'] (tasa 0.5).
- Derivación ≠ alerta; omisión ≠ legitimidad: Tito solo deriva al SLM.

## Costos (ms, separados)

- Arranque: artefacto 0.2 ms, encoder 3830.0 ms, calentamiento 67.7 ms.
- Ejecución: 246 actualizaciones, p50 14.9 ms, p95 19.0 ms, máx 23.1 ms; fallos: 0; truncadas >128 tokens: 0.
- Sin latencia de audio ni RTF: no hubo audio en este diagnóstico.

## Interpretación

- Falta de validación: sin revisión humana no hay verdad de referencia formal; los conteos son descriptivos de desarrollo.
- Errores observados: ver tabla y JSON por línea (puntaje, derivación, oportunidad, legítimas derivadas).
- Causas no aisladas: puntajes altos o banco grande no prueban por sí solos buen o mal ajuste; el ajuste se juzga en #99 contra validación.

## Comparador recargable para #101

- Recarga: `tito_real.cargar_artefacto` + `TitoReal` + `puntuar(n, frase)` con umbral 0.5; reproduce puntajes: True (246/246 válidas, fallos 0, distintos 0, tolerancia 5e-05).
- Diagnóstico no sustituye la corrida Tito viejo→SLM con los diez modelos de #101.

## Reproducir

- Corrida: `../../.venv/bin/python diagnosticar_tito.py --salida DIAGNOSTICO-TITO-2026-10-29.json` desde `experiments/slm-directo/`.
- Solo MD (sin inferencia): `../../.venv/bin/python diagnosticar_tito.py --regenerar-md DIAGNOSTICO-TITO-2026-10-29.json`.
- Hardware/runtime en el JSON (`runtime`, `librerias`, `codigo`): AMD Ryzen 7 7700X 8-Core Processor con 30.5 GB RAM.
