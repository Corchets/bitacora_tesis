# #143, segunda vuelta, etapa 2: C y v4-premisa contra v4 dentro del alcance

> **Estado: propuesta sin discutir.** Desarrollo; la reserva no se corre. Se preparó y se corrió en Colab el
> 2026-11-07, y se analizó el 2026-11-09. **Según la regla, se adopta C con «riesgo ≥ 0,3 o alerta», provisorio hasta
> la reserva.**
> - Contra `v4-corte`: +8 estafas y +7 avisos antes del pedido, con 27/94 FA contra 42/94.
> - La repetición lo sostiene.
> - `v4-premisa` queda dentro de ±2.
>
> Ver [`analisis.md`](analisis.md), y para seguir, [`PROPUESTA-SIGUIENTE.md`](PROPUESTA-SIGUIENTE.md). El criterio
> de abajo se escribió antes de correr, y está en código en
> [`analizar.py`](analizar.py). El Colab está en
> [`colab/README-PUNTAJE-TOKEN.md` §5](../../colab/README-PUNTAJE-TOKEN.md#5-segunda-vuelta-etapa-2-tag-colab143-etapa-2).

## Qué pregunta

¿El prompt C o `v4-premisa` le ganan a v4 dentro del alcance?

- **Alcance** (decisión del equipo, 2026-11-06; ADR 0003): llamadas entrantes de números no agendados.
- **C** ([`tarea_c.txt`](../../prompts/tarea_c.txt) + [`salida_json_c.txt`](../../prompts/salida_json_c.txt)): mira la
  intención y hacia dónde va la llamada, y permite avisar antes del pedido.
- **`v4-premisa`** ([`tarea_v4_premisa.txt`](../../prompts/tarea_v4_premisa.txt)): v4 con una sola oración más:
  «PROTEGIDA recibió esta llamada de un número que no tiene agendado: la llamó OTRA.»
- **Vista dentro del alcance:** 140 casos ([`alcance-140`](../../casos/listas/alcance-140.txt)):
  - las 46 estafas de corpus_v2, 36 de ellas con pedido;
  - las 94 legítimas entrantes de #155.

## Configuraciones (decisión de Mateo, 2026-11-07)

Todas usan el JSON cortado después de `alerta_sugerida`, y piden el motivo aparte, solo al avisar (ADR 0006). Ningún
prompt cambió: cada una es su prompt base tal cual (`CORTE_DE` en `detectores.py`).

| corrida | prompt | casos | papel |
|---|---|---|---|
| `v4-corte` | v4 | los 244 | referencia |
| `c-json-corte` | C | los 244 | candidata |
| `c-json-corte-rep` | C | los 140 | repetición (ADR 0005) |
| `v4-premisa-corte` | v4-premisa | los 244 | candidata |
| `v4-premisa-corte-rep` | v4-premisa | los 140 | repetición |

Además, los 6 controles de ventas y préstamos con los tres prompts, solo para mirar.

Antes de correr, filtra solo la humo de formato de los dos prompts nuevos, en los 3 casos de siempre (48 líneas):
- con el JSON completo y logprobs, la alerta termina a más tardar en el token 24;
- el cortado lee riesgo y alerta en las 48 líneas.

El prompt que no pasa no corre, y no se ajusta nada en esa sesión.

## Criterio, escrito antes de correr

> **Confirmado por Mateo el 2026-11-07, antes de correr.** Pidió «solo la curva», sin un límite fijo de FA. Se le
> propuso esta forma de decidir con la curva, la confirmó y aclaró cómo se lee la repetición.

**La curva.**
- Cada configuración se mira con las mismas reglas, sobre el riesgo y la alerta que escribe el modelo:
  - «alerta sola»;
  - «riesgo ≥ u o alerta», con u = 0,1…1,0.
- Cada regla da estafas avisadas (/46), avisos antes del pedido (T_A < T_R, /36) y FA (/94).
- Se informa entera, en la tabla y en `curva.csv`. Las reglas v1 y v2 del laboratorio van como puntos sueltos.

**Punto de comparación: las FA del detector de hoy.**
1. **F** son las FA de `v4-corte` en las 94, con su regla adoptada: «riesgo ≥ 0,4 o alerta».
2. **Regla de cada configuración** (`v4-corte` incluida): la que tenga FA ≤ F y avise más estafas.
   - Desempates: más avisos antes del pedido, menos FA y el umbral más cercano a 0,4.

**Regla de #143** (ADR 0005), contra `v4-corte` en ese punto:
- **Se prefiere la candidata** si tiene 3 estafas más, o 3 avisos más antes del pedido, sin perder 3 o más en la otra
  cifra.
- **Si gana en una y pierde 3 o más en la otra,** no se adopta, y decide el equipo.
- **Dentro de ±2 en las dos,** se queda `v4-corte`. La latencia se informa.
- **La repetición no vuelve a elegir el umbral** (aclaraciones de Mateo, 2026-11-07). Usa la misma regla (el mismo u)
  que eligió la candidata en su primera corrida, porque el punto elegido tiene que sostenerse (ADR 0005). Con esa
  regla, tiene que cumplir la misma condición completa que la primera corrida:
  - +3 contra `v4-corte` en una cifra en que ganó la primera; si ganó en las dos, alcanza con una;
  - sin perder 3 o más en la otra cifra;
  - con FA ≤ F + 2.

  Si gana en una cifra y pierde 3 o más en la otra, no se adopta, y decide el equipo. En cualquier otro caso, no
  cuenta.
- **Si cuentan las dos:**
  - gana la de más estafas, después la de más avisos antes y después la de menos FA;
  - si entre ellas quedan dentro de ±2 en las dos cifras, se elige `v4-premisa`, que es el cambio más chico.
- Lo que se adopta es provisorio hasta la reserva.

**Solo para mirar (no decide):**
- la misma comparación con FA = 0, 4, 9 y 14 (0 %, 5 %, 10 % y 15 % de las 94);
- los intervalos de Wilson en el punto de comparación, con la detección útil (T_A ≤ T_R);
- las estafas sin pedido y las 6 que piden un dato de identificación;
- corpus_v2 entero, sin el alcance;
- las 7 legítimas de corpus_v2 que están dentro del alcance;
- los manuales;
- las legítimas por lote (LEG, LEG2, ENT-L y selección), por el sesgo del DNI (R29, #154);
- las reglas v1 y v2;
- los controles de ventas;
- la diferencia entre corrida y repetición;
- la latencia.

La meta 80/15 no es criterio.

## Humo de formato y verificación de los ZIP

**Humo:** se corrió en Colab T4 el 2026-11-07 a las 23:33 UTC, con el commit `d127953`, sobre los 3 casos de siempre
(48 líneas). **Pasa en los dos prompts, así que no se ajustó nada.**

| prompt | tokens hasta la alerta (mín / mediana / máx) | líneas que alcanzan | cortado, líneas leídas | resultado |
|---|---|---|---|---|
| `c-json-corte` | 23 / 23 / 23 | 48/48 | 48/48 | PASA |
| `v4-premisa-corte` | 23 / 23 / 23 | 48/48 | 48/48 | PASA |

El detalle está en [`humo/humo.md`](humo/humo.md).

**Verificación de los ZIP (2026-11-09):**
- cada uno de los 8 se descomprimió en un directorio vacío nuevo, y los 7 parciales coinciden byte a byte con su
  carpeta en el final;
- `commit.txt`, los 6 `TERMINADA.txt` y los 7 manifiestos dan `d127953`, sin cambios sin commitear;
- el sha256 de `colab/probar_etapa_2.py` en el tag coincide con `script-sha256.txt` (`3966e0ac…`);
- el digest del modelo coincide en los manifiestos y en `digest.txt` (`b37049369adf…`), con Ollama 0.40.14;
- el texto de la segunda consulta es el de `motivo_v4_corte.txt`, y no hay casos de la reserva.

## Archivos

| Archivo | Qué es |
|---|---|
| [`analizar.py`](analizar.py) | El criterio de arriba en código, escrito antes de correr: `python -I analizar.py` desde esta carpeta, con los ZIP descomprimidos acá. Tests en [`tests/test_etapa2_143.py`](../../tests/test_etapa2_143.py). |
| [`analisis.md`](analisis.md) | Resultado: el veredicto, qué mejoró, dónde y por qué, lo que le queda a C y una propuesta para seguir. |
| [`analisis-salida.md`](analisis-salida.md), `curva.csv` | Salida completa de `python -I analizar.py` y la curva de cada corrida. |
| [`diagnostico.py`](diagnostico.py), [`diagnostico-salida.md`](diagnostico-salida.md) | Diagnóstico fuera del criterio, escrito el 2026-11-09 después de ver los resultados. Cubre: estafas por tipo de pedido, FA por lote y por momento, uso del riesgo escrito, errores de C, la segunda consulta, la exploración del riesgo sostenido y del pedido crítico con oráculo, y los controles línea por línea. |
| [`exploracion.py`](exploracion.py), [`exploracion-salida.md`](exploracion-salida.md) | Exploración del 2026-11-09, después de ver los resultados, para decidir cómo seguir: `alerta_sugerida` y el corte tras el riesgo, subidas y bajadas del riesgo, frases tranquilizadoras, consultar solo en las líneas de OTRA, aperturas, y FA según el pedido de datos y por escenario. |
| [`PROPUESTA-SIGUIENTE.md`](PROPUESTA-SIGUIENTE.md) | Propuesta para seguir: qué se concluye, respuestas a las preguntas de Mateo, decisiones pendientes, pasos, sesiones y trabajo para repartir. |
| `humo/`, `v4-corte/`, `c-json-corte/`, `c-json-corte-rep/`, `v4-premisa-corte/`, `v4-premisa-corte-rep/`, `controles-ventas/` | Corridas de Colab, una carpeta por corrida, tal como bajaron. |
| `commit.txt`, `script-sha256.txt`, `ollama-version.txt`, `digest.txt`, `pip-freeze.txt`, `gpu.txt` | Registro de la corrida. |
