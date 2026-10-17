# Replay incremental: integración de ASR, contexto y detector (#28)

Herramienta de simulación de streaming para evaluar el pipeline completo de detección
incremental de vishing: consume actualizaciones de ASR (o casos de texto), mantiene el
contexto acumulado de la llamada, invoca el detector (reglas de laboratorio o SLM local)
y aplica la política de aviso único, midiendo el instante efectivo de aviso (`T_A`) en el reloj
de la llamada.

---

## 1. Recorrido del flujo (Arquitectura)

```mermaid
flowchart TD
    Audio["Audio de llamada (streaming)"] --> ASR["ASR local (actualizaciones.jsonl)"]
    ASR -->|"Actualización (parcial / final)"| Replay["Motor Replay (replay.py)"]
    Replay --> Contexto["Contexto incremental<br/>- Parcial: reemplaza borrador abierto<br/>- Final: acumula línea cerrada"]
    Contexto -->|"Disparo (final / parcial)"| Detector["Detector<br/>- Reglas (comparador)<br/>- SLM directo (Ollama)"]
    Detector -->|"Respuesta (riesgo, alerta_sugerida, motivo, evidencia)"| Politica["Política de aviso único"]
    Politica -->|"Primer alerta válida = true"| Aviso["Emisión de aviso (T_A)<br/>T_A = disponible_s + t_detector"]
    Politica -->|"Sin alerta o alertas posteriores"| Registro["Registro de evento (eventos.csv)"]
    Aviso --> Registro
```

---

## 2. Cómo correrlo

El script principal es `replay.py`. Acepta dos modos de entrada mutuamente excluyentes:
streaming de audio ASR (`--actualizaciones`) y casos de texto sin audio (`--texto`).

### A. Simulación de audio ASR (JSONL)

Con detector de reglas de laboratorio:
```bash
python replay.py \
  --actualizaciones tests/datos/ejemplo_actualizaciones.jsonl \
  --detector reglas \
  --salida corridas/demo_reglas
```

Con SLM local (requiere Ollama activo con el modelo descargado):
```bash
python replay.py \
  --actualizaciones tests/datos/ejemplo_actualizaciones.jsonl \
  --detector slm \
  --modelo qwen3.5:2b \
  --prompt tarea \
  --hablantes ab \
  --disparo final \
  --salida corridas/demo_slm
```

### B. Modo texto sin audio

Reproduce un caso de `experiments/slm-directo/casos/texto/`:
```bash
python replay.py \
  --texto ../slm-directo/casos/texto/LAB-whatsapp-codigo.txt \
  --detector reglas \
  --salida corridas/demo_texto
```

### Parámetros principales

| Parámetro | Valores | Por defecto | Descripción |
|---|---|---|---|
| `--actualizaciones` | ruta `.jsonl` | — | Flujo de actualizaciones del contrato ASR. |
| `--texto` | ruta `.txt` | — | Caso de texto de diálogo directo. |
| `--detector` | `reglas`, `slm` | Obligatorio | Detector a evaluar. |
| `--modelo` | texto | `qwen3.5:2b` | Modelo SLM para Ollama. |
| `--prompt` | `tarea`, `tarea+base` | `tarea` | Variante del prompt del sistema. |
| `--hablantes` | `ab`, `sin` | `ab` | Con etiquetas de canal (A/B) o texto ciego. Si el audio no tiene canal, conmuta automáticamente a `sin`. |
| `--disparo` | `final`, `parcial` | `final` | Invoca el detector solo en segmentos cerrados (`final`) o en cada actualización (`parcial`). |
| `--salida` | ruta directorio | Obligatorio | Carpeta donde se guardan los artefactos. |
| `--seed` | entero | `42` | Semilla para SLM (`no-aplica` para reglas). |

---

## 3. Política de aviso único

> **Estado: propuesta sin discutir.** Ver [D08](../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

En este ensayo se aplica la política `aviso_unico_primer_true_valido`:
1. El detector evalúa lo disponible hasta el instante actual `disponible_s`.
2. El primer resultado válido con `alerta_sugerida = True` emite el aviso de la llamada.
3. Respuestas inválidas (error de JSON, recorte de contexto o timeout) cuentan como **fallos**, nunca como predicción, y no impiden que una actualización posterior válida genere el aviso.
4. Una vez emitido el aviso, las actualizaciones posteriores se siguen registrando pero tienen `aviso = false`.
5. En audio, el instante del aviso se calcula como:
   $$T_A = \text{disponible\_s} + \frac{\text{ms\_detector}}{1000}$$
   representando el segundo real del reloj de audio en que el usuario recibiría la notificación.
6. En modo texto, no hay reloj de audio: las columnas de tiempo quedan vacías y el aviso informa el turno/línea correspondiente.

---

## 4. Qué registra cada corrida

Cada ejecución en `--salida <dir>` produce tres archivos:

1. **`eventos.csv`**: traza fila a fila de cada actualización:
   - `llamada_id`, `n`, `tipo` (`parcial`/`final`), `segmento`, `canal`, `texto`.
   - `texto_disponible_resumido`: texto acumulado disponible en ese instante exacto.
   - `inicio_audio_s`, `fin_audio_s`, `disponible_s`.
   - `ms_detector`, `riesgo`, `alerta_sugerida`, `motivo`, `evidencia`, `valida`, `error`.
   - `aviso` (`true`/`false`), `t_a` (segundos del audio si emite aviso).
2. **`manifiesto.json`**: procedencia técnica completa:
   - Hash SHA-256 del archivo de entrada y tamaño en bytes.
   - Configuración completa (detector, modelo, prompt, hablantes, disparo, seed o no-aplica).
   - Metadatos de ASR (`asr_meta`) si venían en la cabecera del JSONL.
   - Hash de commit git y estado de cambios en el repositorio.
   - Datos de hardware de la máquina de ejecución (SO, CPU, núcleos, RAM, versión de Python).
3. **`resumen.md`**: reporte sintetizado:
   - Si hubo aviso, instante `T_A`, motivo, evidencia y actualización desencadenante.
   - Transcripción completa disponible al momento exacto del aviso (permite auditar qué información provocó la alerta).
   - Total de actualizaciones, evaluaciones, fallos y tiempos de respuesta.

---

## 5. Límites y alcance metodológico

- **Sin etiquetas de referencia en runtime:** el runner jamás recibe clases (`vishing`/`legítima`), escenarios, roles ni marcas humanas (`T_R`/`T_C`). La evaluación contra referencia humana se realiza en etapas posteriores de análisis.
- **Sin segundos inventados en texto:** en modo `--texto` los tiempos quedan en blanco; no se asumen duraciones artificiales por palabra ni silencios.
- **Garantía temporal incremental:** el contexto disponible solo contiene segmentos entregados hasta `disponible_s`.
