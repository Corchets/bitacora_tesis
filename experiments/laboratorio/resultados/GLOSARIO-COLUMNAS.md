# Glosario de columnas

Corrida de texto del 2026-09-24. Los CSV están en [2026-09-24/](2026-09-24/). Una fila por guion, más `ejemplo.txt` y una fila `_suite` con el resumen.

`T_A` es el turno en que dispara el goteo (la alerta con histéresis). `T_R` es el primer turno de incendio (el pedido). En modo texto no hay segundos ni marca de cumplimiento, así que `T_C`, `L_C` y `Preventive@δ` quedan vacíos. Las fórmulas de margen están en [METRICAS.md](../../../docs/evaluacion/METRICAS.md).

| Columna | Qué es |
|---|---|
| `fecha` | Fecha y hora local de esta corrida. |
| `commit` | Commit de la rama en el momento de correr (`git rev-parse HEAD`). |
| `detector_incendio` | Quién marca el pedido. En esta corrida vale `reglas`: una lista escrita a mano. Si el turno dice algo como «pasame el código» o «decime la clave», hay incendio. |
| `detector_goteo` | Quién pone el puntaje de 0 a 1. En `2026-09-24/resultados-2026-09-24.csv` vale `tfidf-stub-semillas`: cuenta palabras de los textos inventados de `semillas.json` y puntúa cada turno. Si el turno tiene menos de 2 palabras que esa lista conoce, no opina. En los CSV de encoders, el valor es el id de Hugging Face: el modelo lee la frase, se queda congelado, y una regresión logística entrenada con esas mismas 24 frases inventadas pone el número. Ahí hay opinión en todo turno que no esté vacío. En los dos casos, goteo es el puntaje alto dos turnos seguidos. |
| `duracion_s` | Segundos de reloj de toda la suite (21 casos, ejemplo, typos y robustez). El mismo valor en cada fila. |
| `caso` | Ruta del guion. `_suite` es la fila de resumen. |
| `clase` | `V` vishing, `L` legítima, `ejemplo` el guion de muestra, `resumen` la fila de totales. |
| `n_turnos` | Cantidad de turnos del guion. En `_suite`, cantidad de casos (21). |
| `incendio` | 1 si las reglas marcaron un pedido. En `_suite`, cuántos vishing incendiaron. |
| `T_R_turno` | Turno del primer incendio. Vacío si no hubo pedido. |
| `etiquetas_incendio` | Etiquetas que disparó el incendio, separadas por `\|`. |
| `etiquetas_esperadas` | Etiquetas que el oracle espera en ese guion. |
| `cobertura_etiquetas` | 1 si las esperadas están todas entre las observadas. En `_suite`, cuántos vishing cubren. |
| `goteo` | 1 si la histéresis disparó la alerta. En `_suite`, cuántos vishing gotearon. |
| `T_A_turno` | Turno del goteo. Vacío si no alertó. |
| `umbral_goteo` | Umbral de puntaje usado para el goteo (0,5). |
| `L_R_turnos` | `T_R − T_A`, en turnos. Positivo: la alerta llegó antes del pedido. En `_suite`, la mediana. |
| `latencia_decision_turno` | El primero entre incendio y goteo. |
| `T_C_turno` | Turno en que la víctima empieza a cumplir. Vacío: estos guiones no lo anotan. |
| `L_C_turnos` | `T_C − T_A`. Vacío por la misma razón. |
| `puntaje_max` | Puntaje más alto del caso. En `_suite`, el máximo entre las legítimas (el margen). |
| `puntajes` | Puntaje de cada turno con opinión (`t3=0.411`). En `_suite`, cuartiles de `L_R`. |
| `falsa_alarma` | 1 si una legítima incendió o goteó. En `_suite`, cuántas legítimas lo hicieron. |
| `terminos_criticos` | Cuáles de `codigo`, `token`, `transferencia` aparecen en el texto. En `_suite`, precisión, recall y F1 del goteo (vishing = positivo) y AUROC/AUPRC del puntaje máximo. |
| `memoria_pico_mb` | Pico de RAM del proceso durante la corrida. |
| `typo_ok` | 1 si un swap de letras por turno (semilla 42) conserva el incendio esperado. En `_suite`, el total. |
| `robusto_upper` | 1 si en mayúsculas el resultado no cambia. En `_suite`, el total. |
| `robusto_tildes` | 1 si con tildes el resultado no cambia. En `_suite`, el total. |
| `robusto_muletilla` | 1 si con muletillas el resultado no cambia. En `_suite`, el total. |
| `nota` | Aclaración de la fila: qué no se mide en modo texto, o cómo leer el resumen. |

## Encoders (misma fecha, otro archivo)

El transcriptor no corre. El incendio sigue siendo `reglas`. Solo cambia quién puntúa el goteo. Pesos en la caché de Hugging Face, fuera del repositorio. No cierra D09.

| Archivo | `detector_goteo` |
|---|---|
| [resultados-2026-09-24-bert-base-spanish-wwm-cased.csv](2026-09-24/resultados-2026-09-24-bert-base-spanish-wwm-cased.csv) | `dccuchile/bert-base-spanish-wwm-cased` (BETO) |
| [resultados-2026-09-24-robertuito-base-uncased.csv](2026-09-24/resultados-2026-09-24-robertuito-base-uncased.csv) | `pysentimiento/robertuito-base-uncased` (RoBERTuito) |
| [resultados-2026-09-24-distilbert-base-spanish-uncased.csv](2026-09-24/resultados-2026-09-24-distilbert-base-spanish-uncased.csv) | `dccuchile/distilbert-base-spanish-uncased` (DistilBETO) |
| [resultados-2026-09-24-albert-tiny-spanish.csv](2026-09-24/resultados-2026-09-24-albert-tiny-spanish.csv) | `dccuchile/albert-tiny-spanish` (ALBETO chico) |

La regresión de arriba se entrenó con las 24 frases inventadas de `semillas.json`. Con tan pocos ejemplos el puntaje se separa de memoria: en los cuatro, el goteo marca 13/13 vishing de la suite original y también 8/8 legítimas. Esos números no sustituyen al corpus ni al piloto.

Los pesos no están en el caché suelto: se copiaron a `experiments/laboratorio/modelos/` (BETO, RoBERTuito, DistilBETO y ALBETO chico, una carpeta por modelo). Esa carpeta está en `.gitignore`.

## Casos difíciles (sumados a los mismos CSV)

Cinco guiones en `casos/dificiles/`, fuera del oracle de los 21. La fila `_suite` se recalculó con la suite original más estos cinco. `duracion_s` de las filas nuevas es el tiempo de esta pasada, no el de la primera.

| Guion | Qué busca |
|---|---|
| `dificiles/vishing/digitos-sin-palabra.txt` | Pide los dígitos del mensaje sin decir código, token ni números. |
| `dificiles/vishing/pantalla-sin-programa.txt` | Pide ver la pantalla sin TeamViewer, AnyDesk ni «instala». |
| `dificiles/vishing/giro-sin-plata.txt` | Pide girar dinero sin plata, alias, CBU ni transferencia. |
| `dificiles/legitima/portero-codigo-puerta.txt` | Dice «código» y es el de la puerta. |
| `dificiles/legitima/banco-gasto-sin-pedido.txt` | Habla de un gasto del banco y no pide nada. |

## Cascada encoder → SLM (2026-09-28)

CSV en [2026-09-28/](2026-09-28/). Mismas columnas que arriba, más dos al final. La fila `_suite` resume los 21 casos más los 5 difíciles, en una sola pasada. Esta vez los difíciles no se sumaron después. `ejemplo.txt` va aparte.

| Archivo | `detector_goteo` |
|---|---|
| `resultados-2026-09-28-robertuito-base-uncased.csv` | RoBERTuito + regresión logística, sin SLM. |
| `resultados-2026-09-28-cascada-robertuito-llama3.2-1b-instruct-q4_K_M.csv` | El mismo encoder. Si el puntaje cae entre 0,35 y 0,75, puntúa `llama3.2:1b-instruct-q4_K_M` (Ollama) con el historial y la base institucional del PR #40. |
| `resultados-2026-09-28-transcripciones.csv` | Las 4 grabaciones AR de YouTube como **texto plano**, sin audio, partidas en bloques. Una fila por grabación y detector. |

La regresión ya no usa las 24 frases inventadas. Usa semillas provisorias que arma `armar_semillas.py` desde `semillas_manifiesto.json`. El texto queda fuera de Git.

- **Estafa:** turnos del estafador en 8 grabaciones AR distintas de las de evaluación.
- **Legítima:** turnos AR sin maniobra más turnos de ES-Port.

No es corpus ni piloto. El reemplazo real se investiga en [#41](https://github.com/Corchets/bitacora_tesis/issues/41). Los 0,35 / 0,75 son el ejemplo del PR #40, sin calibrar.

| Columna extra | Qué es |
|---|---|
| `turnos_zona_gris` | Turnos que el encoder mandó al SLM sobre turnos puntuados. En `_suite` incluye las pasadas de robustez. Vacío sin cascada. |
| `memoria_slm_mb` | RAM del modelo cargado según Ollama (`/api/ps`). Va aparte de `memoria_pico_mb`: el SLM corre en otro contenedor y el techo de gama es la suma. |

### Transcripciones en bloques

No se corre audio. El texto es el `texto_final` que Zipformer Kroko dejó el 2026-09-25 en `artifacts/corrida-<caso>.json`. El cortador de turnos no está definido, así que el texto se parte en **bloques fijos de 25 palabras, sin solapamiento**: unos 10 segundos de habla. Cada bloque cuenta como un turno. `T_A_turno`, `T_R_turno` y `L_R_turnos` se miden en bloques. Los bloques quedan en `artifacts/transcripciones/`, fuera de Git porque son voces de terceros.

> **Estado: propuesta sin discutir.** Los 25 palabras son un parámetro de laboratorio, no la definición del cortador (D08).

En estas filas, `clase` es siempre `V`: son estafas editadas por medios, con narración. `falsa_alarma` y `cobertura_etiquetas` quedan vacías. `duracion_s` es el tiempo de puntuar esa grabación.

| Columna extra | Qué es |
|---|---|
| `video_url` | Grabación de origen en YouTube. |
| `duracion_audio_s` | Duración del audio original. Solo como referencia: no se procesa audio. |
| `texto_fuente` | Artifact del que sale el texto, con su sha256 (12 caracteres). |
| `asr_texto_fuente` | Modelo ASR y fecha en que se generó ese texto. |
| `recorte` | Cómo se partió el texto. |
| `archivo_bloques` | Archivo con un bloque por línea, con su sha256. |
| `palabras` | Palabras del texto completo. |
