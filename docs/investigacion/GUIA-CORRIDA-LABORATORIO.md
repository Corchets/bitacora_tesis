# Guía: corrida del laboratorio (spike #29)

Corrida repetible de la config `alta` (Zipformer Kroko + reglas de incendio + **LLM/SLM local**)
en PC con techo. Evidencia del [issue #29](https://github.com/Corchets/bitacora_tesis/issues/29)
(hijo de #28). **No cierra D09.** El contrato vive en
[PRIMERA-INVESTIGACION-MODELOS.md](PRIMERA-INVESTIGACION-MODELOS.md).

> **Pivote 2026-09-25:** TF–IDF eliminado. Detector = LLM local (`LLM_BASE_URL`);
> `DETECTOR_MODO=clasificador|agente`.

El código está en `experiments/laboratorio/`, sin Markdown adentro.

## UI local para texto y resultados (#44)

Implementación del [issue #44](https://github.com/Corchets/bitacora_tesis/issues/44) en
[ui_laboratorio.py](../../experiments/laboratorio/ui_laboratorio.py) y
[ui_resultados.py](../../experiments/laboratorio/ui_resultados.py). Permite explorar y
contrastar visualmente los CSV de corridas existentes en `experiments/laboratorio/resultados/`,
probar la lógica del pipeline sobre secuencias de texto y entrenar un clasificador lineal en memoria
para experimentación rápida.

La interfaz base no necesita Docker, ASR ni modelos neuronales pesados para visualizar datos o
probar **reglas solas**. El alcance actual se enfoca prioritariamente en texto; la integración de
audio y streaming se aborda en el [issue #42](https://github.com/Corchets/bitacora_tesis/issues/42).

---

### Índice de la sección

1. [Inicio rápido y entorno virtual](#inicio-rápido-y-entorno-virtual)
2. [Estructura y navegación](#estructura-y-navegación)
3. [Resultados: Comparación de ejemplos](#resultados-comparación-de-ejemplos)
   - [Filtros compactos y ejes de análisis](#filtros-compactos-y-ejes-de-análisis)
   - [Panorama general (matricial)](#panorama-general-matricial)
   - [Paneles de curvas por ejemplo y paginación](#paneles-de-curvas-por-ejemplo-y-paginación)
   - [Superposición enfocada opcional](#superposición-enfocada-opcional)
   - [Procedencia de corridas y tabla de alertas](#procedencia-de-corridas-y-tabla-de-alertas)
   - [Pautas de interpretación (sin declarar ganadores)](#pautas-de-interpretación-sin-declarar-ganadores)
4. [Resultados: Detalle de un ejemplo](#resultados-detalle-de-un-ejemplo)
5. [Probar texto (reglas, encoder y cascada)](#probar-texto-reglas-encoder-y-cascada)
6. [Entrenar clasificador LR en sesión](#entrenar-clasificador-lr-en-sesión)
7. [Exportación, trazabilidad y persistencia sin sobrescritura](#exportación-trazabilidad-y-persistencia-sin-sobrescritura)
8. [Solución de problemas (Troubleshooting)](#solución-de-problemas-troubleshooting)
9. [Límites metodológicos y decisiones abiertas](#límites-metodológicos-y-decisiones-abiertas)

---

### Inicio rápido y entorno virtual

Para ejecutar la interfaz de forma aislada sin modificar el entorno global ni el repositorio, se utiliza
un entorno virtual gestionado con `uv` y Python 3.12 ubicado en `/tmp/bitacora-ui-feat-ui-venv`.

Desde la raíz del repositorio, sin cambiar de rama:

```bash
# 1. Crear el entorno virtual reproducible fuera de Git
uv venv --python python3.12 /tmp/bitacora-ui-feat-ui-venv

# 2. Instalar dependencias mínimas para visualizador y reglas solas
uv pip install --python /tmp/bitacora-ui-feat-ui-venv/bin/python -r experiments/laboratorio/requirements-ui.txt

# 3. Iniciar la aplicación local
PYTHONDONTWRITEBYTECODE=1 /tmp/bitacora-ui-feat-ui-venv/bin/python -m streamlit run experiments/laboratorio/ui_laboratorio.py \
  --server.address 127.0.0.1 \
  --server.fileWatcherType poll \
  --server.runOnSave true \
  --browser.gatherUsageStats false
```

Abrí en tu navegador `http://127.0.0.1:8501`.

Si vas a entrenar el clasificador o ejecutar detectores basados en embeddings (`DetectorEncoder`)
o cascada (`DetectorCascada`), instalá las dependencias complementarias en el mismo entorno:

```bash
uv pip install --python /tmp/bitacora-ui-feat-ui-venv/bin/python -r experiments/laboratorio/requirements-ui-encoder.txt
```

> **Nota de higiene:** Tanto el entorno `/tmp/bitacora-ui-feat-ui-venv` como las memorias caché de
> modelos (`~/.cache/huggingface`) residen fuera del árbol de Git. La aplicación se limita a un
> ancho de pantalla acotado (máximo 1240 px) para facilitar su visualización en notebooks sin
> desplazamiento horizontal excesivo.

---

### Estructura y navegación

La aplicación se organiza a través de un menú lateral (`sidebar`) bajo la sección **Laboratorio local**:

- **Resultados:** Exploración de corridas previas. Ofrece dos modalidades mediante un selector radial:
  - `Comparar ejemplos`: Vista panorámica matricial, paneles por caso y superposición enfocada opcional.
  - `Detalle de un ejemplo`: Inspección turno a turno de un caso particular, con acceso a su guion y metadatos originales.
- **Probar texto:** Consola interactiva para someter turnos de texto (escritos libremente o tomados de guiones)
  al detector seleccionado (Reglas solas, Encoder o Cascada).
- **Entrenar:** Entrenador en sesión de una cabeza de regresión logística sobre representaciones congeladas de un encoder local o del Hub.
- **Ayuda:** Consulta integrada de esta misma sección de la guía, leída dinámicamente desde la fuente de verdad.

---

### Resultados: Comparación de ejemplos

Esta pantalla está pensada para responder interrogantes comparativos entre detectores y corridas
sin saturar la pantalla ni generar confusión visual.

#### Filtros compactos y ejes de análisis

En la parte superior, dentro del panel desplegable **Filtros y configuración de vista** (colapsado por defecto para facilitar el acceso visual directo al panorama), podés acotar:
1. **Corridas a comparar:** Selección de archivos CSV ubicados en `experiments/laboratorio/resultados/`.
2. **Origen de los ejemplos:** Filtra entre `Grabaciones transcritas` (audios reales pasados por ASR),
   `Guiones del laboratorio` (textos sintéticos o estructurados) y `Pruebas de UI` (salidas generadas desde la consola de prueba).
3. **Clases a comparar:** `V` (Vishing/Fraude), `L` (Llamada legítima) o `sin_etiquetar`.
4. **Detectores a comparar:** Detectores de goteo presentes en los CSV cargados con etiquetas legibles y normalizadas (ej. `RoBERTuito`, `DistilBETO`, `BETO`, `ALBETO tiny`, `TF-IDF histórico`, `Reglas solas`, `RoBERTuito → Llama 3.2 1B`). Si coexisten múltiples series con el mismo nombre normalizado, la interfaz desambigua automáticamente incorporando el identificador crudo (`RoBERTuito (id_crudo)`).
5. **Ejemplos a comparar:** Selección de casos específicos.
6. **Eje horizontal:**
   - `Turno`: Turnos enteros cronológicos (1, 2, 3...). Representa orden secuencial de diálogo. **No son segundos de audio**.
   - `Avance por cantidad de turnos (%)`: Normalización relativa dada por `(turno / n_turnos) * 100`.
     Permite comparar llamadas cortas y largas en una escala común [0, 100%]. **No convierte turnos en tiempo físico ni calcula métricas preventivas en segundos**.
7. **Controles de visualización:**
   - `Paneles por página`: Controla cuántos paneles individuales se grafican por página (opciones: `4`, `6`, `8`, `12` o `Todos`; por defecto `4`).
   - `Límite de curvas por panel`: Restringe la cantidad de series mostradas simultáneamente dentro de un mismo caso para no sobrecargar el gráfico (opciones: `4`, `6`, `8`, `12` o `Todas`; por defecto `6`).

#### Panorama general (matricial)

Antes de la matriz se expone un resumen compacto con tres métricas en línea (`Ejemplos`, `Series`, `Archivos CSV`). Las advertencias metodológicas extensas se agrupan en el desplegable **Metodología y cautelas de la comparación** (colapsado por defecto) junto con una línea sintética de aviso.

El **Panorama general** es un mapa térmico (con título `Panorama · puntajes máx`) que sitúa los ejemplos seleccionados en el eje vertical y las series en el eje horizontal mediante códigos visuales breves y horizontales (`S1`, `S2`, …). Estos códigos son alias de selección dinámicos de la vista comparativa (no identificadores permanentes) orientados a garantizar una lectura horizontal inequívoca y sin rotaciones que crucen el título, incluso con múltiples series.

- **Mapeo visible y trazabilidad:** Directamente sobre el gráfico se exhibe una línea de correspondencia sintética (`Series en columnas: S1: Detector [C1] · …`) y debajo se incluye el panel desplegable **Mapeo de series del panorama (S1, S2, …)** con la tabla detallada que asocia cada código con su etiqueta completa, corrida visual, detector, identidad cruda y archivo CSV.
- **Contenido y desambiguación:** Cada celda reporta el **puntaje máximo de goteo registrado** en ese ejemplo (`puntaje_max`). Al posar el cursor (hover), el tooltip reporta la serie completa (`Código · Etiqueta`), el detector legible, la identidad cruda exacta (`detector_goteo`), el puntaje máximo, las marcas de alerta (`T_R` y `T_A`), la cantidad de turnos, el archivo CSV y el commit de Git. Si coexisten diferentes detectores crudos bajo una misma etiqueta o múltiples ocurrencias en el mismo caso/ID/CSV, la matriz desambigua automáticamente las columnas (agregando `#1`, `#2`) para que cada una tenga identidad única y ninguna observación se colapse ni se sobrescriba.
- **Tratamiento estricto de faltantes (No imputación):**
  - Si un detector corrió pero no emitió opinión de goteo (por ejemplo, en corridas de reglas solas),
    la celda se rotula explícitamente como **"Sin opinión"**.
  - Si un ejemplo no formó parte de un CSV determinado, la celda se rotula como **"Sin datos"**.
  - **Bajo ninguna circunstancia la falta de opinión se reemplaza por 0.0**. La ausencia de evidencia
    no equivale a certeza de legitimidad ni a riesgo nulo.
- **Alcance completo:** El panorama matricial refleja **todos los ejemplos seleccionados**, sin verse
  afectado por la paginación de los paneles individuales.

#### Paneles de curvas por ejemplo y paginación

Debajo del panorama, la sección **Curvas por ejemplo** organiza los resultados en paneles pequeños
independientes distribuidos en dos columnas (con comportamiento responsivo que se apila a una columna en anchos menores para evitar comprimir los gráficos):

- **Alineación:** Cada panel contiene todas las curvas asociadas a un mismo caso sobre una escala vertical uniforme `[0, 1]`.
- **Colores estables por detector:** Los colores se asignan de forma fija y determinista según el detector:
  - RoBERTuito: Azul (`#1f77b4`).
  - Cascada RoBERTuito → Llama 3.2 1B: Violeta (`#7c3aed`).
  - DistilBETO: Verde esmeralda (`#059669`).
  - BETO: Celeste / Cyan (`#0891b2`).
  - ALBETO tiny: Ámbar (`#d97706`).
  - TF-IDF histórico: Marrón (`#8c564b`).
  - Reglas solas: Rojo (`#dc2626`).
  - Sin goteo: Gris pizarra (`#64748b`).
  - Nuevos modelos: Asignación determinista respaldada por paleta de reserva vía hash.
- **Trazos por corrida visual:** Cuando un mismo detector se evalúa en diferentes CSVs, el trazo de la línea
  cambia según la corrida visual asignada (`C1` continuo, `C2` discontinuo/dash, `C3` punteado/dot, etc.).
  - **Aclaración:** Las referencias `C1`, `C2`, etc., son etiquetas dinámicas dentro de la sesión visual
    para distinguir archivos; **no constituyen identificadores estables ni permanentes en el repositorio**.
- **Líneas de alerta sin encimamiento:**
  - Línea vertical punteada roja: `T_R_turno` (primer disparo de reglas).
  - Línea vertical punteada violeta: `T_A_turno` (primera alerta sostenida del detector de goteo).
  - Si varias corridas disparan en el mismo turno o porcentaje de avance, las marcas se agrupan en una única línea vertical con etiqueta combinada (ej. `Reglas [C1, C2]`), evitando textos encimados. El detalle individual se conserva en el hover y en la tabla de alertas inferior.
  - Línea horizontal gris: Umbral de goteo registrado en la corrida.
- **Paginación explícita:** Si la selección comprende más ejemplos que los configurados en `Paneles por página`,
  se activa el control numérico `Página de paneles (1–N)`. Un mensaje informativo aclara cuántos ejemplos se están visualizando
  y recuerda que el panorama y las tablas conservan la totalidad de la selección.
- **Tope de series visibles:** Si un ejemplo tiene más curvas que el límite establecido, el panel muestra las
  primeras N y exhibe un aviso aclaratorio para ampliar el tope si se desea.

#### Superposición enfocada opcional

Para situaciones donde se requiere contrastar directamente curvas en una única gráfica de gran detalle,
se incluye el expander **Superposición enfocada (opcional — comparar curvas superpuestas)** (colapsado por defecto):
- Requiere activación manual mediante la casilla `Activar superposición enfocada` (desactivada por defecto).
- Permite seleccionar un subconjunto restringido (hasta 6 ejemplos).
- **Selección explícita de series:** una vez elegidos los casos, se habilita el multiselect `Series a superponer (máximo 10)` (con hasta 10 preseleccionadas por defecto para visualización inmediata). Podés intercambiar o elegir libremente cualquier combinación de series hasta el tope de 10. La interfaz informa de forma transparente cuántas series están disponibles y cuántas están seleccionadas, sin recortes silenciosos.
- Al posar el cursor (hover), detalla: caso, turno, puntaje, detector, corrida visual, CSV de origen y commit de git.

#### Procedencia de corridas y tabla de alertas

Debajo de las gráficas, la interfaz expone la trazabilidad completa de los datos:
1. **Procedencia de las corridas:** Tabla que asocia cada serie (`Serie` con su alias `S1`, `S2`, …, `Etiqueta`, `Corrida visual`, `Detector`, `Identidad completa (detector_goteo)`)
   con su archivo CSV real, cantidad de ejemplos con datos, commit de Git y fecha UTC de ejecución. La columna `Serie` vincula directamente la fila con la columna correspondiente del panorama superior, mientras que la columna de identidad completa conserva el identificador crudo exacto del detector registrado en el CSV.
2. **Alertas de todos los ejemplos seleccionados:** Tabla unificada con las columnas:
   `caso`, `detector_goteo`, `corrida_visual`, `archivo_resultado`, `n_turnos`, `puntaje_max`,
   `umbral_goteo`, `T_R_turno`, `T_A_turno`, `falsa_alarma` y `clase`.
3. **Filas originales y resúmenes `_suite`:** Desplegables con los datos crudos para inspección y verificación.
   Los resúmenes `_suite` de las suites de prueba se mantienen separados de los casos individuales
   y nunca se recalculan al filtrar.
4. **Descarga unificada:** El botón `Descargar filas de la comparación (selección completa)` exporta
   un CSV (`comparacion-laboratorio.csv`) con todas las filas seleccionadas, incluyendo procedencia y sin omisiones por paginación.

#### Pautas de interpretación (sin declarar ganadores)

Al analizar las comparaciones, tené presentes las siguientes pautas metodológicas:
- **Ausencia de calibración:** Modelos entrenados sobre distintos conjuntos o con semillas provisorias
  no comparten calibración probabilística. Un puntaje de 0.60 en un modelo no equivale al mismo nivel de
  riesgo en otro. Los valores de salida no son probabilidades calibradas.
- **No concluir ganadores:** Las curvas permiten analizar tendencias temporales y sensibilidad de turnos,
  pero **no permiten decretar qué detector es "mejor"** ni calcular métricas preventivas concluyentes.
- **Semántica de las marcas temporales:**
  - `T_R_turno` en los CSV históricos del laboratorio corresponde al **primer disparo del módulo de reglas**
    (capa léxica/incendio), **no a la anotación humana del momento en que el atacante solicita la acción crítica**.
  - `T_A_turno` indica el turno donde el detector de goteo superó el umbral bajo la política de histéresis vigente.
  - No hay registro de `T_C` (tiempo de cumplimiento de la víctima), tiempos de audio en segundos,
    márgenes `L_C`, WER, RTF ni tasa preventiva `Preventive@δ` en estas pruebas sobre texto.
- **Histéresis del spike:** El detector del laboratorio utiliza una ventana móvil de 3 opiniones y alerta
  cuando el máximo supera el umbral y se sostiene durante dos actualizaciones. Un único pico seguido de
  una opinión baja puede gatillar la alerta. Esta formulación es una propuesta exploratoria y mantiene
  abierta la discusión de [D08](../gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

---

### Resultados: Detalle de un ejemplo

La vista `Detalle de un ejemplo` permite inspeccionar minuciosamente el comportamiento de una corrida sobre un caso individual:
- **Selección:** Se elige el archivo CSV de la corrida, el filtro de clases y el caso a examinar.
- **Métricas principales:** Tarjetas con el primer disparo de reglas (`T_R_turno`), la primera alerta de goteo (`T_A_turno`)
  y el registro de `T_C` (indicando "Sin dato" en los experimentos de texto).
- **Gráfico de evolución:** Curva individual turno a turno con el umbral registrado y líneas verticales de disparo.
  Si un turno no tuvo evaluación, se grafica con salto de línea (`connectgaps=False`).
- **Guion asociado:** Si el guion existe en el repositorio (dentro de `experiments/laboratorio/casos/`),
  se visualiza en un bloque de código. Por seguridad, la lectura de archivos está confinada estrictamente al laboratorio.
- **Reglas disparadas:** Lista de etiquetas léxicas encendidas (`etiquetas_incendio`).
- **Exportación:** Permite descargar el CSV original sin alteraciones.

---

### Probar texto (reglas, encoder y cascada)

La pestaña **Probar texto** permite correr el pipeline incremental sobre secuencias arbitrarias de diálogo:
1. **Entrada de texto:**
   - Escribir en el área de texto o seleccionar un guion precargado desde `casos/`.
   - **Formato:** Cada línea representa un **turno de conversación**.
   - Las líneas en blanco y aquellas que comiencen con `#` se descartan automáticamente.
   - Usá siempre datos inventados o ficticios; no ingreses información personal ni sensible (Ley 25.326).
2. **Modos de detección:**
   - `Reglas solas`: Aplica exclusivamente las expresiones de capa 2 (`rules.py`). No requiere dependencias
     de PyTorch ni servidores externos.
   - `Encoder entrenado`: Utiliza el clasificador lineal entrenado previamente en la pestaña *Entrenar* sobre
     los embeddings generados por el modelo de lenguaje (ej. RoBERTuito).
   - `Cascada con encoder entrenado`: Evalúa primero con el encoder; si el puntaje cae en la zona de incertidumbre
     (zona gris configurada en 0,35–0,75 según el spike), remite el turno al SLM local.
3. **Parámetros configurables:**
   - `Umbral de goteo`: Valor de decisión para emitir alerta (por defecto 0.50). Inhabilitado en modo reglas solas.
   - `Clase declarada`: Permite catalogar la prueba como `Sin etiquetar`, `Legítima` o `Vishing`. Es una
     etiqueta asignada por el operador para trazabilidad; no constituye una verdad de terreno contrastada.
   - `Servidor SLM local`: URL compatible con OpenAI (restringida por diseño a loopback: `http://localhost:11434/v1`,
     `127.0.0.1` o `::1`). La UI no acepta conexiones a servidores remotos.
   - `Modelo SLM`: Nombre del modelo a consultar (ej. `llama3.2:1b-instruct-q4_K_M`).
   - **Comportamiento del servidor SLM:** **La UI no levanta ni gestiona el proceso del SLM**. Este debe ser ejecutado
     previamente por el usuario (mediante Ollama, vLLM o Docker). Si el servidor no responde o rechaza la conexión,
     la cascada degrada ordenadamente conservando el puntaje emitido por el encoder.
4. **Resultados de la prueba:**
   - Métricas inmediatas de incendio y goteo.
   - Gráfico de la evolución de puntajes turno a turno.
   - Tabla con el desglose de cada turno y JSON detallado de los eventos de reglas.

---

### Entrenar clasificador LR en sesión

La pestaña **Entrenar** implementa el mecanismo exploratorio del spike para entrenar una cabeza de Regresión
Logística sobre representaciones vectoriales congeladas:

1. **Datos de entrenamiento:**
   - Se cargan mediante un archivo JSON externo desde el explorador de archivos.
   - **Esquema requerido:**
     ```json
     {
       "estafa": [
         "Hola, somos del banco, necesitamos verificar una transferencia urgente.",
         "Le solicitamos el código de seis dígitos que acaba de recibir por SMS."
       ],
       "legitima": [
         "Buenos días, llamo para coordinar la entrega del paquete de compras.",
         "Perfecto, nos vemos mañana por la mañana en el domicilio indicado."
       ]
     }
     ```
   - **Validaciones automáticas:**
     - Ambas claves (`estafa` y `legitima`) deben estar presentes.
     - Deben ser listas no vacías compuestas exclusivamente por textos con contenido real (no vacíos).
     - No puede haber contradicciones: ningún texto idéntico puede coexistir en ambas categorías.
2. **Configuración del modelo:**
   - Identificador del encoder en Hugging Face (por defecto `pysentimiento/robertuito-base-uncased`) o ruta
     a un directorio local con pesos compatibles con Hugging Face Transformers.
   - Hilos de cómputo CPU (por defecto 2 hilos, adecuado al presupuesto de gama alta del spike).
3. **Ejecución y ciclo de vida en sesión:**
   - El clasificador lineal se ajusta en memoria mediante `scikit-learn` utilizando `LogisticRegression(max_iter=1000)`
     con semilla pseudoaleatoria fija `seed=42`.
   - **Persistencia en sesión:** El clasificador reside en el estado de la sesión de Streamlit (`st.session_state["encoder"]`).
     Si se refresca la página, se pierde la conexión o se reinicia el servidor, **es necesario volver a entrenar**.
4. **Registro de procedencia (`entrenamiento-lab.json`):**
   - La interfaz genera un registro detallado que puede descargarse en formato JSON.
   - Contiene: modelo base, semilla (42), hilos, hash SHA-256 del JSON de entrada, cantidad de ejemplos por clase,
     duración del entrenamiento, especificación de hardware, versiones de librerías instaladas, commit de Git,
     indicador de cambios pendientes en el árbol y hashes SHA-256 de los scripts del laboratorio.
5. **Advertencia de alcance:**
   - Este procedimiento no conforma un protocolo de validación científica: no divide en train/dev/test,
     no realiza validación cruzada ni reporta métricas de generalización ([issue #41](https://github.com/Corchets/bitacora_tesis/issues/41)).
     Cumple el único fin de permitir la prueba del circuito de inferencia en la interfaz.

---

### Exportación, trazabilidad y persistencia sin sobrescritura

La herramienta cuenta con mecanismos para preservar la trazabilidad y la privacidad:

- **Descarga de pruebas de texto:**
  - `Descargar puntajes CSV (sin texto)`: Exporta una fila tabular con turnos, puntajes numéricos, etiquetas léxicas
    y procedencia, **omitiendo deliberadamente el texto transcripto**. Esto permite compartir evidencia numérica
    sin almacenar conversaciones sensibles.
  - `Descargar detalle JSON (incluye texto)`: Permite al investigador resguardar localmente el objeto completo con
    los textos procesados para análisis puntual privado.
- **Persistencia en `experiments/laboratorio/resultados/`:**
  - El botón `Guardar puntajes en resultados/` escribe un archivo con nombre único basado en marca temporal UTC:
    `resultados-ui-AAAA-MM-DDTHHMMSS-fZ.csv`.
  - El archivo se guarda en modo exclusivo (`'x'`), imposibilitando la sobrescritura accidental de resultados anteriores.
  - No guarda textos de transcripciones; solo registra métricas, puntajes, etiquetas y procedencia.
  - Una vez guardado, el nuevo archivo se incorpora de manera inmediata a la lista de corridas disponibles
    en la pestaña *Resultados*.

---

### Solución de problemas (Troubleshooting)

- **Error de importación tras actualización de código (`ImportError: cannot import name ...`):**
  - *Causa:* Streamlit conserva módulos cacheados en memoria de Python entre reejecuciones.
  - *Mitigación:* La UI verifica automáticamente la marca de tiempo (`st_mtime_ns`) de `ui_resultados.py` y
    fuerza un `importlib.reload`. Si la discrepancia persiste, detené el servidor (Ctrl+C) y relanzalo
    con `--server.fileWatcherType poll`.
- **Faltan librerías al intentar entrenar o probar cascada (`No module named 'torch'`, `'transformers'` o `'sklearn'`):**
  - *Solución:* Verificá que instalaste `requirements-ui-encoder.txt` dentro del entorno `/tmp/bitacora-ui-feat-ui-venv`:
    ```bash
    uv pip install --python /tmp/bitacora-ui-feat-ui-venv/bin/python -r experiments/laboratorio/requirements-ui-encoder.txt
    ```
- **"No hay ejemplos con esta selección" o filtros vacíos:**
  - *Solución:* Abrí el panel desplegable de filtros y asegurate de tener seleccionada al menos una corrida,
    un origen de datos, una clase y un detector. Si borraste todos los elementos de un selector múltiple,
    volvé a seleccionar los valores deseados.
- **Error al cargar JSON de entrenamiento (`ValueError`):**
  - *Causa:* El archivo no cumple el esquema estricto.
  - *Solución:* Revisá que el archivo contenga un objeto JSON con las claves `"estafa"` y `"legitima"`,
    que ambas contengan listas con textos no vacíos y que ningún texto coincida de forma idéntica en ambas listas.
- **Error de conexión con el SLM local en cascada:**
  - *Causa:* El servicio de LLM no está corriendo en la URL indicada, o no se encuentra el modelo solicitado.
  - *Solución:* Asegurate de que Ollama o el motor elegido esté activo en `http://localhost:11434/v1`
    (o la dirección loopback indicada) y que el modelo (`llama3.2:1b-instruct-q4_K_M`) haya sido descargado
    previamente (`ollama pull llama3.2:1b-instruct-q4_K_M`). Recordá que la UI no conecta a hosts externos.
- **El gráfico muestra curvas discontinuas o celdas "Sin opinión":**
  - *Explicación:* Ocurre por diseño cuando una corrida evaluó turnos pero el detector no generó puntaje
    (ej. reglas solas). La interfaz no une los puntos artificialmente ni los dibuja en cero para evitar
    asumir niveles de riesgo que no fueron calculados.

---

### Límites metodológicos y decisiones abiertas

La UI expone el instrumental del laboratorio para exploración visual, pero **no sustituye ni da por cerradas
las decisiones metodológicas clave del proyecto**:

- **[D07 — Aprobar taxonomía y evento crítico](../gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico):**
  Las reglas de incendio activas en `rules.py` son heurísticas preliminares de trabajo. La taxonomía de pedidos,
  la definición formal de eventos críticos y las marcas temporales definitivas permanecen abiertas.
- **[D08 — Congelar protocolo experimental](../gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental):**
  Los umbrales (ej. 0.50) y la ventana móvil de 3 opiniones provienen del spike #29 y no constituyen la política
  temporal congelada. La UI no reemplaza la evaluación con particiones sin fuga de información
  ([METODO-CREACION-CORPUS.md §9](../datos-etica/METODO-CREACION-CORPUS.md#9-división-de-datos)).
- **[D09 — Elegir ASR y detector](../gestion/MAPA-DECISIONES.md#d09--elegir-asr-y-detector):**
  Ni RoBERTuito ni la cascada con Llama 3.2 1B representan la selección final de la tesis. En los ensayos provisorios
  la cascada no mejoró al encoder solo ([CONTRASTE-NLP-TEORIA-Y-LABORATORIO.md](CONTRASTE-NLP-TEORIA-Y-LABORATORIO.md)).
  La decisión final depende del benchmark formal sobre el corpus piloto.
- **[Issue #41 (Datos y entrenamiento formal)](https://github.com/Corchets/bitacora_tesis/issues/41):**
  El entrenamiento en sesión con semillas provisorias carece de validez estadística y no genera particiones de test.
- **[Issue #42 (Pruebas con audio)](https://github.com/Corchets/bitacora_tesis/issues/42):**
  La interfaz actual procesa exclusivamente texto turno a turno. Las métricas de tiempo real en segundos,
  latencia de ASR y RTF requieren las corridas de audio completas.

> **Trazabilidad previa de pruebas:** El conjunto de 25 pruebas automatizadas vigentes (nueve de interfaz en
> `test_ui_laboratorio.py` y dieciséis de procesamiento y soporte en `test_ui_resultados.py`) verifica el correcto funcionamiento
> de los componentes, la carga de datos sin imputación, la desambiguación de series, la normalización de anclas en Ayuda
> y la navegación de la interfaz. El test de entrenamiento utiliza un modelo BERT ficticio con pesos aleatorios para verificar
> el circuito de sesión sin incurrir en descargas pesadas ni validar rendimiento sobre un corpus real.
>
> **Validación visual (2026-10-03):** Comprobada en el navegador integrado de Orca: título completo bajo
> la barra superior, matriz con etiquetas horizontales `S1` y `S2`, filtros plegados y paneles de 320 px
> de alto. En una ventana de 793×789 px los paneles se apilan; el contenedor tiene un máximo de 1240 px.
> El índice de Ayuda conserva sus enlaces internos. La suite final pasó 25 pruebas; el entrenamiento
> se verificó con el modelo ficticio, sin evaluar la calidad del detector.

Referencias de la UI: [Streamlit, carga de archivos](https://docs.streamlit.io/develop/api-reference/widgets/st.file_uploader)
y [gráficos](https://docs.streamlit.io/develop/api-reference/charts). Estas dependencias implementan
la interfaz local; no agregan un backend de producción.

## Requisitos

- Docker + Docker Compose.
- Un WAV **inventado** (sin datos reales), 16 kHz mono 16-bit, **fuera de Git**:
  `ffmpeg -i entrada.m4a -ac 1 -ar 16000 llamada.wav`
- Para el **goteo** LLM: un servidor OpenAI-compatible local (ollama, llama.cpp, etc.) y
  `LLM_BASE_URL` (ej. `http://host.docker.internal:11434/v1`). Sin eso, los turnos quedan
  sin opinión y solo corre el incendio por reglas.

## Corridas

```bash
cd experiments/laboratorio
# Audio: replay en streaming con el ASR real
WAV=/ruta/a/llamada.wav docker compose run --rm corrida
# Texto: reglas + LLM + contador sobre transcripto, sin ASR (brazo manual de E1)
WAV=/tmp/nada.wav LLM_BASE_URL=http://host.docker.internal:11434/v1 \
  docker compose run --rm -e LLM_BASE_URL -e DETECTOR_MODO=clasificador \
  corrida --texto /app/ejemplo.txt
```

La primera corrida de audio baja ~155 MB del Hub al volumen `hf-cache`.

### Cascada encoder → SLM (2026-09-28)

> **Estado: propuesta sin discutir.** Implementa la cascada de #27
> ([PR #40](https://github.com/Corchets/bitacora_tesis/pull/40)): RoBERTuito puntúa cada turno y solo
> la zona gris (0,35–0,75, ejemplo del PR, sin calibrar) va al SLM, con la base institucional del PR.
> No cierra D09.

```bash
cd experiments/laboratorio
E=/ruta/fuera-de-git/entrenamiento-lab     # esport/ + semillas.json
# 1. SLM en su contenedor (el techo de alta es corrida + slm)
WAV=/tmp/nada.wav docker compose --profile cascada up -d slm
WAV=/tmp/nada.wav docker compose exec slm ollama pull llama3.2:1b-instruct-q4_K_M
# 2. Semillas provisorias (texto fuera de Git; el manifiesto sí va en Git)
python armar_semillas.py --entrenamiento $E
# 3. Suite de texto (encoder solo y cascada) -> resultados/2026-09-28/ (mismas columnas que 2026-09-24)
L="-e DETECTOR_MODO=base -e LLM_BASE_URL=http://slm:11434/v1 -e LLM_MODEL=llama3.2:1b-instruct-q4_K_M"
WAV=/tmp/nada.wav ENTRENAMIENTO=$E docker compose run --rm -e COMMIT="$(git rev-parse HEAD)" $L \
  -v "$PWD/resultados:/app/resultados" --entrypoint python corrida correr_cascada.py texto
# 4. Las 4 grabaciones como texto plano (ASR guardado), en bloques de 25 palabras, sin audio
WAV=/tmp/nada.wav ENTRENAMIENTO=$E docker compose run --rm -e COMMIT="$(git rev-parse HEAD)" $L \
  -v "$PWD/resultados:/app/resultados" --entrypoint python corrida correr_cascada.py transcripciones \
  artifacts/corrida-anses-yague-73BxIYoh7Rw.json artifacts/corrida-yapa-salta-HqR-vcondGk.json \
  artifacts/corrida-jujuy-2016-eSJTfa5WQMM.json artifacts/corrida-ancasti-WZNk9yf5DMw.json
```

`armar_semillas.py` espera los ASR de las 8 grabaciones de entrenamiento en
`artifacts/asr-ent-<id>.json` (`WAV=.../ent-<id>-16k.wav docker compose run --rm corrida --salida
/app/artifacts/asr-ent-<id>.json`, sin servidor LLM). Ids y turnos etiquetados: `semillas_manifiesto.json`.

## Salida

JSON por stdout y en `artifacts/` (gitignored): `corrida.json` (audio) o
`corrida-texto.json`. Trae `RTF`, memoria Pico vs techo, texto por turnos,
incendio y goteo **por separado**, hardware, commit y versiones.
Definiciones de `T_A` y márgenes: [METRICAS.md](../evaluacion/METRICAS.md).

## Gamas y techos

Una sola lógica, tres configs (`GAMA` + `mem_limit` en
[docker-compose.yml](../../experiments/laboratorio/docker-compose.yml)):

| `GAMA` | `mem_limit` | Hilos ASR/detector | Estado en #29 |
|---|---|---|---|
| `alta` | `2g` | 4 / 2 | se corre |
| `media` | `512m` | 3 / 1 | prevista, no correr |
| `baja` | `256m` | 1 / 1 | prevista; Moonshine es solo id, no motor |

Sin GPU a propósito. Los hilos son config del proceso, no `cpus` de Compose.

> **Estado: propuesta sin discutir (2026-09-28).** El techo de `alta` pasa de 1024 a
> **2048 MB** para que entren ASR + encoder + SLM de la cascada (#27 / PR #40). Cambia el
> presupuesto que #24 aprobó en [PREFACTIBILIDAD-TECNICA.md](PREFACTIBILIDAD-TECNICA.md) el
> 2026-09-22; hay que avisar a Mateo y revalidarlo con el equipo.

## Límites (leer antes de citar un número)

- PC x86 con techo, **no** teléfono ARM: el número dice “con esta memoria y estos
  hilos, ¿entra?”, nada más.
- Candidato LLM de arranque: Llama 3.2 1B Instruct; umbral 0.5, silencio 400 ms y
  pedazos de 300 ms son parámetros de spike, no decisiones congeladas.
- Las reglas de incendio son lista de trabajo; D07 sigue abierta.
- El oracle (`chequear_casos.py`) hoy fija **incendio**; el goteo LLM se fija cuando
  haya corridas con servidor levantado.
