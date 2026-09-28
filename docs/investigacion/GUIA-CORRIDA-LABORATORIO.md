# Guía: corrida del laboratorio (spike #29)

Corrida repetible de la config `alta` (Zipformer Kroko + reglas de incendio + **LLM/SLM local**)
en PC con techo. Evidencia del [issue #29](https://github.com/Corchets/bitacora_tesis/issues/29)
(hijo de #28). **No cierra D09.** El contrato vive en
[PRIMERA-INVESTIGACION-MODELOS.md](PRIMERA-INVESTIGACION-MODELOS.md).

> **Pivote 2026-09-25:** TF–IDF eliminado. Detector = LLM local (`LLM_BASE_URL`);
> `DETECTOR_MODO=clasificador|agente`.

El código está en `experiments/laboratorio/`, sin Markdown adentro.

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
