# Módulo de métricas de evaluación

Herramienta de cálculo y reporte de métricas de evaluación para los detectores de vishing,
siguiendo estrictamente las definiciones de [`docs/evaluacion/METRICAS.md`](../../docs/evaluacion/METRICAS.md).

> **Estado: propuesta sin discutir.**
> La definición de las marcas de referencia mínimas ($T_R$, $T_C$) se encuentra abierta en
> [D07](../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico).
> La política de alerta ($T_A$), los valores del parámetro $\delta$ (5, 10 y 20 s en audio / 0, 1 y 2 líneas en texto son candidatos sin aprobar),
> la composición de legítimas y el protocolo del test reservado (#52) permanecen abiertos en
> [D08](../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).
> Esta herramienta no ejecuta la evaluación final sobre test reservado ni fija decisiones abiertas: deja el módulo listo y probado.

---

## 1. Qué calcula y de dónde sale cada fórmula

Todas las métricas implementadas provienen de [`docs/evaluacion/METRICAS.md`](../../docs/evaluacion/METRICAS.md):

| Métrica / Medición | Fórmula / Definición | Sección canónica |
|---|---|---|
| **Marcas temporales / de posición** | `T_A` (primer aviso emitido), `T_R` (primer pedido de alto riesgo), `T_C` (primer cumplimiento observable de la víctima). | [METRICAS.md §1](../../docs/evaluacion/METRICAS.md#1-marcas-temporales) |
| **Márgenes de alerta** | `L_R = T_R − T_A` (margen respecto al pedido); `L_C = T_C − T_A` (margen respecto al cumplimiento). Sin alerta → llamada no detectada y margen sin dato (`None`). Sin $T_C$ → $L_C$ sin dato (`None`), sin inferir prevención. | [METRICAS.md §2](../../docs/evaluacion/METRICAS.md#2-margen-de-la-alerta) |
| **Distribución de márgenes** | Mediana, cuartiles (Q1, Q3) y rango intercuartil (`IQR = Q3 − Q1`) informando la cantidad $n$ de llamadas que permitieron calcularlos. | [METRICAS.md §2](../../docs/evaluacion/METRICAS.md#2-margen-de-la-alerta) |
| **Alertas con margen suficiente** | `Preventive@δ(X) = (vishing con T_A ≤ X − δ) / (vishing evaluables para X)` con $X \in \{T_R, T_C\}$. Llamadas sin alerta permanecen en el denominador. Casos sin marca $X$ en la referencia quedan excluidos, informando cantidad y motivo. | [METRICAS.md §3](../../docs/evaluacion/METRICAS.md#3-alertas-con-margen-suficiente) |
| **Falsas alarmas en legítimas** | Llamadas legítimas con al menos una alerta / total de legítimas evaluadas. | [METRICAS.md §4](../../docs/evaluacion/METRICAS.md#4-qué-se-mide) |
| **Decisión por conversación** | Precision, recall y F1 sobre la decisión binaria por llamada completa o prefijo, informando conteos ($TP$, $FP$, $FN$, $TN$) y denominadores. | [METRICAS.md §4](../../docs/evaluacion/METRICAS.md#4-qué-se-mide) |
| **Incertidumbre de proporciones** | Intervalo de Wilson al 95 % para proporciones binomiales (robusto en muestras acotadas y proporciones cercanas a 0 o 1). | [METRICAS.md §4](../../docs/evaluacion/METRICAS.md#4-qué-se-mide) |
| **Sensibilidad a prevalencia** | `precision(p) = (p × r) / (p × r + (1 − p) × f)`. Si el denominador es cero no se calcula (`None`). Demuestra el impacto del balance del conjunto (Williams, 2021). | [METRICAS.md §4](../../docs/evaluacion/METRICAS.md#balance-y-precisión-de-las-alertas) |
| **Factor de tiempo real (RTF)** | `RTF = tiempo_computo_s / duracion_audio_s`. Solo aplica cuando existe audio; en texto sin timestamps no aplica (`None`). | [METRICAS.md §4](../../docs/evaluacion/METRICAS.md#4-qué-se-mide) |

### Regla de unidades
- **En audio:** Todas las marcas y márgenes se miden en **segundos**.
- **En texto:** Diálogos sin timestamps miden posiciones y márgenes en **LÍNEAS**. **Nunca** se convierten líneas a segundos usando duraciones supuestas.

---

## 2. Estructura del módulo

- `metricas.py`: Funciones puras con cobertura completa de pruebas:
  - `calcular_margen_lr(t_r, t_a)` y `calcular_margen_lc(t_c, t_a)`
  - `intervalo_wilson(k, n, confianza=0.95)`
  - `resumen_distribucion(valores)`
  - `preventive_at(delta, referencia, casos_vishing)`
  - `tasa_falsas_alarmas(casos_legitimos)`
  - `metricas_clasificacion_conversacion(casos)`
  - `precision_con_prevalencia(p, r, f)`
  - `calcular_rtf(tiempo_computo_s, duracion_audio_s)`
- `evaluar.py`: CLI y adaptadores de ingesta:
  - Carga corridas de `experiments/slm-directo/` (`actualizaciones.csv` + `casos/referencia/*.json`).
  - Carga salidas de `experiments/replay/` (`eventos.csv` + referencia humana).
  - Genera `metricas.json` y `metricas.md` con tablas desglosadas por configuración, grupo (`piloto_escrito`, `trampa`, `laboratorio`) y tipo de legítima (negativos difíciles vs cotidianas).
- `tests/test_metricas.py`: Pruebas unitarias con `unittest` (TDD, casos borde, denominador cero, ejemplos canónicos de METRICAS.md y adaptador replay).
- `salidas/2026-10-17-desarrollo/`: Salidas de evaluación generadas sobre las corridas existentes de desarrollo de `qwen3.5` (0.8B, 2B, 4B) y línea base de reglas.

---

## 3. Adaptador para `experiments/replay/`

Para evaluar corridas sobre streaming de audio, `evaluar.py` acepta `--replay-eventos` y `--replay-referencia`.

### Formato esperado en `eventos.csv`
- `case_id`: Identificador de la conversación/llamada (texto).
- `aviso`: Booleano (`true`/`false`) que indica si la actualización disparó una alerta.
- `disponible_s` (o `t_a` / `T_A`): Timestamp en **segundos** desde el inicio de la llamada.
- `config`: Nombre de la configuración evaluada (opcional, por defecto `replay`).
- `ms` o `tiempo_computo_s`: Tiempo de cómputo insumido (opcional, para RTF).
- `duracion_audio_s`: Duración total del audio (opcional, para RTF).

### Formato esperado en la referencia humana de replay
Archivo JSON o carpeta de JSONs con:
- `case_id`: Identificador coincidente.
- `clase`: `"vishing"` o `"legitima"` (o `"legitima_dificil"`, `"legitima_cotidiana"`).
- `t_r` (o `t_r_s`): Segundo donde inicia el primer pedido de alto riesgo (o `null`).
- `t_c` (o `t_c_s`): Segundo donde inicia el primer cumplimiento observable (o `null`).
- `duracion_s`: Duración del audio en segundos (opcional).

---

## 4. Cómo correrlo

### Ejecutar las pruebas unitarias
```bash
python3 -m unittest discover -s experiments/metricas/tests
```

### Evaluar corridas existentes de `slm-directo`
```bash
python3 experiments/metricas/evaluar.py \
    experiments/slm-directo/corridas/2026-10-13_224418_linea-base-reglas \
    experiments/slm-directo/corridas/2026-10-14_173532_demo-qwen3.5-0.8b \
    experiments/slm-directo/corridas/2026-10-14_172930_demo-qwen3.5-2b \
    experiments/slm-directo/corridas/2026-10-14_175451_demo-qwen3.5-2b \
    experiments/slm-directo/corridas/2026-10-14_174602_demo-qwen3.5-4b \
    --salida-dir experiments/metricas/salidas/2026-10-17-desarrollo
```

### Evaluar una corrida de `experiments/replay`
```bash
python3 experiments/metricas/evaluar.py \
    --replay-eventos experiments/replay/salidas/eventos.csv \
    --replay-referencia experiments/replay/referencia.json \
    --salida-dir experiments/metricas/salidas/replay-demo
```
