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
| `alta` | `1g` | 4 / 2 | se corre |
| `media` | `512m` | 3 / 1 | prevista, no correr |
| `baja` | `256m` | 1 / 1 | prevista; Moonshine es solo id, no motor |

Sin GPU a propósito. Los hilos son config del proceso, no `cpus` de Compose.

## Límites (leer antes de citar un número)

- PC x86 con techo, **no** teléfono ARM: el número dice “con esta memoria y estos
  hilos, ¿entra?”, nada más.
- Candidato LLM de arranque: Llama 3.2 1B Instruct; umbral 0.5, silencio 400 ms y
  pedazos de 300 ms son parámetros de spike, no decisiones congeladas.
- Las reglas de incendio son lista de trabajo; D07 sigue abierta.
- El oracle (`chequear_casos.py`) hoy fija **incendio**; el goteo LLM se fija cuando
  haya corridas con servidor levantado.
