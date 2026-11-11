# Catálogo de conversaciones

> Generado por [`catalogo.py`](../catalogo.py); no editar a mano. Para actualizarlo, después de sumar casos,
> listas o corridas: `python catalogo.py` desde `experiments/slm-directo`.

Qué conversaciones hay, dónde están, con qué lista se corre cada conjunto y qué usó cada corrida. Las reglas de
formato y de cada grupo están en [README.md](README.md); qué casos cuentan en desarrollo, en
[MANIFIESTO-DESARROLLO.md](MANIFIESTO-DESARROLLO.md).

## 1. Qué conversaciones hay

Desarrollo, en esta rama (`casos/texto/` y `casos/referencia/`). `correr.py` usa todo el desarrollo por defecto;
`--grupo` elige uno.

| Grupo | Conversaciones | Estafas | Legítimas |
|---|---:|---:|---:|
| `corpus_v2` | 97 | 46 | 51 |
| `laboratorio` | 26 | 16 | 10 |
| `legitimas_cotidianas` | 94 | 0 | 94 |
| `piloto_escrito` | 14 | 7 | 7 |
| `trampa` | 13 | 6 | 7 |
| **Total** | **244** | **75** | **169** |

Fuera de desarrollo. La reserva y las legítimas de test se miran una sola vez, con la configuración
congelada ([ADR 0005](../../../docs/ingenieria/adr/0005-reglas-de-evaluacion-escritas-antes-de-correr.md)): no
se cuentan por clase acá.

| Conjunto | Conversaciones | Dónde | Cómo se usa |
|---|---:|---|---|
| Reserva del corpus v2 (`CV2-T-*`) | 200 | rama `reserva/test`: `casos/texto/` y `casos/referencia/` | `--particion test_reservado` en esa rama, solo en la evaluación final |
| Legítimas de test de #45 | 56 | rama `reserva/test`: `casos/legitimas-entrantes-test.jsonl` | todavía no está en el formato de casos: hay que convertirla antes de la evaluación final |
| Corpus externo real de #144 | — | `docs/corpus/ISSUE-144-*` y `docs/corpus/FICHAS-144-*` ([relevamiento](../../../docs/corpus/RELEVAMIENTO-CORPUS-EXTERNO.md)) | lecturas y fichas, no casos: test externo previsto |
| Ejemplos del panel VoIP | 4 | `experiments/asr-local/audio/*-tts-estereo.wav`, fuera de Git (`asr-local/sintetizar_par.py`) | desde el panel; son audio sintético, sin valor de evaluación |
| Llamadas con voz real (#94) | — | `experiments/voip/llamadas/` de la copia que corrió el servidor, fuera de Git | `replay.py --actualizaciones <llamada>/actualizaciones.jsonl` |

## 2. Listas para correr

`python correr.py --lista <nombre>` corre una lista de `casos/listas/`; varias, separadas por coma. Para una
lista nueva, un archivo con un `case_id` por línea y un comentario `#` arriba que diga qué es.

| Lista | Casos | Estafas | Legítimas | Qué es |
|---|---:|---:|---:|---|
| `alcance-140` | 140 | 46 | 94 | Los 140 casos de desarrollo dentro del alcance de la etapa 2 de #143 (llamadas entrantes de números no agendados): las 46 estafas de corpus_v2 (todas «dentro» en alcance-desarrollo.json) y las 94 … |
| `alcance-91` | 91 | 46 | 45 | Vista principal de desarrollo para la etapa 3 de #143: las 46 estafas de corpus_v2 (todas dentro del alcance) y las 45 legítimas representativas de legitimas-escenarios-45. Ver … |
| `desarrollo-150` | 150 | 75 | 75 | Los 150 casos de desarrollo anteriores al 2026-11-06, sin legitimas_cotidianas. Para repetir corridas históricas: python correr.py --lista desarrollo-150 ... |
| `legitimas-91` | 91 | 0 | 91 | Las 91 legítimas de desarrollo de Evaristo (grupo legitimas_cotidianas, 2026-11-06): 21 LEG, 28 LEG2 y 42 ENT-L. No incluye las 3 ENT-L-SELECCION, que van en legitimas-seleccion-3. Para la etapa 2 de … |
| `legitimas-ent-l-42` | 42 | 0 | 42 | Lote ENT-L de legitimas_cotidianas (tanda 3, 2026-11-06): 42 entrantes de 14 a 36 líneas. No incluye las 3 ENT-L-SELECCION, que van en legitimas-seleccion-3. Uso: python correr.py --lista … |
| `legitimas-escenarios-45` | 45 | 0 | 45 | Una legítima por escenario (corpus_desarrollo.py manifiesto, 45 de 94), para la etapa 3 de #143. Regla de Mateo (2026-11-09), fijada antes de correr: la ENT-L del escenario (método de #45, 47 … |
| `legitimas-leg-21` | 21 | 0 | 21 | Lote LEG de legitimas_cotidianas (tanda 1, 2026-11-06): 21 llamadas de 5 a 16 líneas. Uso: python correr.py --lista legitimas-leg-21 ... |
| `legitimas-leg2-28` | 28 | 0 | 28 | Lote LEG2 de legitimas_cotidianas (tanda 2, split dev, 2026-11-06): 28 llamadas entrantes. Uso: python correr.py --lista legitimas-leg2-28 ... |
| `legitimas-seleccion-3` | 3 | 0 | 3 | Las 3 ENT-L de selección de personal (legitimas_cotidianas), agregadas el 2026-11-06 para completar las familias del lote 3. Formato de ENT-L, pero las escribió otro agente después: van aparte de … |
| `rapida-20` | 20 | 10 | 10 | Set rápido para iterar con «riesgo primero» (analisis/2026-10-29-riesgo-primero). Armado por Evaristo el 2026-10-29: 10 estafas y 10 legítimas de corpus_v2, partición desarrollo (~524 líneas). Sirve … |
| `seleccion-57` | 57 | 19 | 38 | Casos para ELEGIR políticas y umbrales (rama reranker-prueba, 2026-10-30). Son las particiones entrenamiento + validacion + diagnostico + regresion de PARTICIONES-TITO-2026-10-29.json (sha256 … |

## 3. Qué usó cada corrida

Sale del `manifiesto.json` de cada carpeta de `corridas/`. «Sin lista» quiere decir que el conjunto no coincide
con ninguna lista, grupo o estado del manifiesto de hoy: se eligió con `--casos` o con una lista que después
cambió.

| Corrida | Fecha | Casos | Conjunto | Prompts o detectores |
|---|---|---:|---|---|
| [`2026-10-13_224418_linea-base-reglas`](../corridas/2026-10-13_224418_linea-base-reglas/) | 2026-10-13 | 53 | estado `historico` del manifiesto | `reglas` |
| [`2026-10-14_172248_demo-qwen3.5-2b`](../corridas/2026-10-14_172248_demo-qwen3.5-2b/) | 2026-10-14 | 8 | 8 casos sin lista | `tarea` |
| [`2026-10-14_172930_demo-qwen3.5-2b`](../corridas/2026-10-14_172930_demo-qwen3.5-2b/) | 2026-10-14 | 53 | estado `historico` del manifiesto | `tarea` |
| [`2026-10-14_173532_demo-qwen3.5-0.8b`](../corridas/2026-10-14_173532_demo-qwen3.5-0.8b/) | 2026-10-14 | 53 | estado `historico` del manifiesto | `tarea` |
| [`2026-10-14_174602_demo-qwen3.5-4b`](../corridas/2026-10-14_174602_demo-qwen3.5-4b/) | 2026-10-14 | 53 | estado `historico` del manifiesto | `tarea` |
| [`2026-10-14_175451_demo-qwen3.5-2b`](../corridas/2026-10-14_175451_demo-qwen3.5-2b/) | 2026-10-14 | 53 | estado `historico` del manifiesto | `tarea` |
| [`2026-10-14_182137_demo-qwen3.5-4b`](../corridas/2026-10-14_182137_demo-qwen3.5-4b/) | 2026-10-14 | 8 | 8 casos sin lista | `tarea` |
| [`2026-10-14_191429_cpu-2hilos`](../corridas/2026-10-14_191429_cpu-2hilos/) | 2026-10-14 | 14 | grupo piloto_escrito | `reglas`, `tarea` |
| [`2026-10-17_145806_demo-qwen3.5-2b-q8_0`](../corridas/2026-10-17_145806_demo-qwen3.5-2b-q8_0/) | 2026-10-17 | 8 | 8 casos sin lista | `tarea` |
| [`2026-10-17_150455_m1-reglas`](../corridas/2026-10-17_150455_m1-reglas/) | 2026-10-17 | 53 | estado `historico` del manifiesto | `reglas` |
| [`2026-10-17_150516_m1-gguf`](../corridas/2026-10-17_150516_m1-gguf/) | 2026-10-17 | 53 | estado `historico` del manifiesto | `tarea` |
| [`2026-10-21_182201_m1-0.8b-v1v2-nb32`](../corridas/2026-10-21_182201_m1-0.8b-v1v2-nb32/) | 2026-10-21 | 53 | estado `historico` del manifiesto | `tarea`, `v2` |
| [`2026-10-21_200147_m1-reglas-150`](../corridas/2026-10-21_200147_m1-reglas-150/) | 2026-10-21 | 150 | lista desarrollo-150 | `reglas` |
| [`2026-10-21_201039_m1-2b-v1v2-nb32`](../corridas/2026-10-21_201039_m1-2b-v1v2-nb32/) | 2026-10-21 | 150 | lista desarrollo-150 | `tarea`, `v2` |
| [`2026-10-21_201914_m1-reglas-v2-150`](../corridas/2026-10-21_201914_m1-reglas-v2-150/) | 2026-10-21 | 150 | lista desarrollo-150 | `reglas` |
| [`2026-10-22_102514_win-9b-piloto-nb32`](../corridas/2026-10-22_102514_win-9b-piloto-nb32/) | 2026-10-22 | 14 | grupo piloto_escrito | `tarea`, `v2` |
| [`2026-10-22_103341_win-4b-v1v2-nb32`](../corridas/2026-10-22_103341_win-4b-v1v2-nb32/) | 2026-10-22 | 53 | estado `historico` del manifiesto | `tarea`, `v2` |
| [`2026-10-22_111736_win-0.8b-v1v2-nb32`](../corridas/2026-10-22_111736_win-0.8b-v1v2-nb32/) | 2026-10-22 | 53 | estado `historico` del manifiesto | `tarea`, `v2` |
| [`2026-10-22_112250_win-9b-v1v2-nb32`](../corridas/2026-10-22_112250_win-9b-v1v2-nb32/) | 2026-10-22 | 53 | estado `historico` del manifiesto | `tarea`, `v2` |
| [`2026-10-23_115920_linux-9b-v1v2-cv2-nb32`](../corridas/2026-10-23_115920_linux-9b-v1v2-cv2-nb32/) | 2026-10-23 | 97 | grupo corpus_v2 | `tarea`, `v2` |
| [`2026-10-23_144554_linux-4b-v1v2-cv2-nb32`](../corridas/2026-10-23_144554_linux-4b-v1v2-cv2-nb32/) | 2026-10-23 | 97 | grupo corpus_v2 | `tarea`, `v2` |
| [`2026-10-23_153722_linux-0.8b-v1v2-nb32`](../corridas/2026-10-23_153722_linux-0.8b-v1v2-nb32/) | 2026-10-23 | 150 | lista desarrollo-150 | `tarea`, `v2` |
| [`2026-10-26_125526_demo-tito-slm-simulado`](../corridas/2026-10-26_125526_demo-tito-slm-simulado/) | 2026-10-26 | 2 | 2 casos sin lista | `reglas`, `tarea`, `tito-slm tarea` |
| [`2026-10-26_132027_tito-real-8casos`](../corridas/2026-10-26_132027_tito-real-8casos/) | 2026-10-26 | 8 | 8 casos sin lista | `reglas`, `tarea`, `tito-slm tarea` |
| [`2026-10-26_132916_qwen4b-comparacion`](../corridas/2026-10-26_132916_qwen4b-comparacion/) | 2026-10-26 | 8 | 8 casos sin lista | `tarea`, `tito-slm tarea` |
| [`2026-10-26_133838_qwen4b-comparacion`](../corridas/2026-10-26_133838_qwen4b-comparacion/) | 2026-10-26 | 8 | 8 casos sin lista | `tarea`, `tito-slm tarea` |
| [`2026-10-26_135518_qwen08b-q8-comparacion`](../corridas/2026-10-26_135518_qwen08b-q8-comparacion/) | 2026-10-26 | 8 | 8 casos sin lista | `tarea`, `tito-slm tarea` |
| [`2026-10-26_135640_qwen08b-comparacion`](../corridas/2026-10-26_135640_qwen08b-comparacion/) | 2026-10-26 | 8 | 8 casos sin lista | `tarea`, `tito-slm tarea` |
| [`2026-10-26_135746_qwen2b-q8-comparacion`](../corridas/2026-10-26_135746_qwen2b-q8-comparacion/) | 2026-10-26 | 8 | 8 casos sin lista | `tarea`, `tito-slm tarea` |
| [`2026-10-26_135930_qwen9b-comparacion`](../corridas/2026-10-26_135930_qwen9b-comparacion/) | 2026-10-26 | 8 | 8 casos sin lista | `tarea`, `tito-slm tarea` |
| [`2026-10-26_141023_llama1b-comparacion`](../corridas/2026-10-26_141023_llama1b-comparacion/) | 2026-10-26 | 8 | 8 casos sin lista | `tarea`, `tito-slm tarea` |
| [`2026-10-29_170921`](../corridas/2026-10-29_170921/) | 2026-10-29 | 2 | 2 casos sin lista | `riesgo` |
| [`2026-10-29_171810_win-gemma3n-e2b-riesgo-cpu`](../corridas/2026-10-29_171810_win-gemma3n-e2b-riesgo-cpu/) | 2026-10-29 | 150 | lista desarrollo-150 | `riesgo` |
| [`2026-10-29_173937_win-gemma3n-e2b-riesgo-cv2-cpu`](../corridas/2026-10-29_173937_win-gemma3n-e2b-riesgo-cv2-cpu/) | 2026-10-29 | 97 | grupo corpus_v2 | `riesgo` |
| [`2026-10-29_182016_rapida-gemma3n-e2b`](../corridas/2026-10-29_182016_rapida-gemma3n-e2b/) | 2026-10-29 | 20 | lista rapida-20 | `riesgo`, `v2` |
| [`2026-10-30_192609`](../corridas/2026-10-30_192609/) | 2026-10-30 | 2 | 2 casos sin lista | `reranker pedidos` |
| [`2026-10-30_193159`](../corridas/2026-10-30_193159/) | 2026-10-30 | 2 | 2 casos sin lista | `reranker pedidos` |
| [`2026-10-30_200421_r1-bge`](../corridas/2026-10-30_200421_r1-bge/) | 2026-10-30 | 77 | 77 casos sin lista | `reranker pedidos` |
| [`2026-10-31_021253_r1-bge-resto`](../corridas/2026-10-31_021253_r1-bge-resto/) | 2026-10-31 | 57 | 57 casos sin lista | `reranker pedidos` |
| [`2026-10-31_105542_r3-riesgo-seleccion`](../corridas/2026-10-31_105542_r3-riesgo-seleccion/) | 2026-10-31 | 57 | lista seleccion-57 | `riesgo` |
| [`2026-11-04_003715_e2b-tito-viejo-150`](../corridas/2026-11-04_003715_e2b-tito-viejo-150/) | 2026-11-04 | 150 | lista desarrollo-150 | `reglas`, `tito-slm tarea` |
| [`2026-11-04_132229_e2b-directo-150`](../corridas/2026-11-04_132229_e2b-directo-150/) | 2026-11-04 | 150 | lista desarrollo-150 | `tarea` |
| [`2026-11-04_193946_prompt-v3-a-solo-y-con-indicio`](../corridas/2026-11-04_193946_prompt-v3-a-solo-y-con-indicio/) | 2026-11-04 | 150 | lista desarrollo-150 | `v3`, `tito-slm v3` |
| [`2026-11-04_201116_prompt-v3-b-tito-sin-indicio`](../corridas/2026-11-04_201116_prompt-v3-b-tito-sin-indicio/) | 2026-11-04 | 150 | lista desarrollo-150 | `tito-slm-sin-indicio v3` |
| [`2026-11-04_prompt-v4-tito-sin-indicio/a/2026-11-04_215231_prompt-v4-a-v4-rol`](../corridas/2026-11-04_prompt-v4-tito-sin-indicio/a/2026-11-04_215231_prompt-v4-a-v4-rol/) | 2026-11-04 | 150 | lista desarrollo-150 | `tito-slm-sin-indicio v4` |
| [`2026-11-04_prompt-v4-tito-sin-indicio/b/2026-11-04_220639_prompt-v4-b-v3-rol`](../corridas/2026-11-04_prompt-v4-tito-sin-indicio/b/2026-11-04_220639_prompt-v4-b-v3-rol/) | 2026-11-04 | 150 | lista desarrollo-150 | `tito-slm-sin-indicio v3` |
| [`2026-11-04_prompt-v4-tito-sin-indicio/c/2026-11-04_221708_prompt-v4-c-v3-orden-v1-ab`](../corridas/2026-11-04_prompt-v4-tito-sin-indicio/c/2026-11-04_221708_prompt-v4-c-v3-orden-v1-ab/) | 2026-11-04 | 150 | lista desarrollo-150 | `tito-slm-sin-indicio v3-orden-v1` |
| [`2026-11-04_prompt-v4-tito-sin-indicio/d/2026-11-04_222802_prompt-v4-d-tarea-ab`](../corridas/2026-11-04_prompt-v4-tito-sin-indicio/d/2026-11-04_222802_prompt-v4-d-tarea-ab/) | 2026-11-04 | 150 | lista desarrollo-150 | `tito-slm-sin-indicio tarea` |
| [`2026-11-04_sin-indicio-150/a/2026-11-04_194015_sin-indicio-a-solo-y-con-indicio`](../corridas/2026-11-04_sin-indicio-150/a/2026-11-04_194015_sin-indicio-a-solo-y-con-indicio/) | 2026-11-04 | 150 | lista desarrollo-150 | `reglas`, `tarea`, `tito-slm tarea` |
| [`2026-11-04_sin-indicio-150/b/2026-11-04_201218_sin-indicio-b-tito-sin-indicio`](../corridas/2026-11-04_sin-indicio-150/b/2026-11-04_201218_sin-indicio-b-tito-sin-indicio/) | 2026-11-04 | 150 | lista desarrollo-150 | `tito-slm-sin-indicio tarea` |
| [`2026-11-04_sin-indicio-150/c/2026-11-04_202259_sin-indicio-c-solo-repeticion`](../corridas/2026-11-04_sin-indicio-150/c/2026-11-04_202259_sin-indicio-c-solo-repeticion/) | 2026-11-04 | 150 | lista desarrollo-150 | `tarea` |
| [`2026-11-04_tanda-roles-tito-sin-indicio/a/2026-11-04_233513_tanda-roles-a-tarea-rol`](../corridas/2026-11-04_tanda-roles-tito-sin-indicio/a/2026-11-04_233513_tanda-roles-a-tarea-rol/) | 2026-11-04 | 150 | lista desarrollo-150 | `tito-slm-sin-indicio tarea` |
| [`2026-11-04_tanda-roles-tito-sin-indicio/b/2026-11-04_234950_tanda-roles-b-v4-cita-libre-rol`](../corridas/2026-11-04_tanda-roles-tito-sin-indicio/b/2026-11-04_234950_tanda-roles-b-v4-cita-libre-rol/) | 2026-11-04 | 150 | lista desarrollo-150 | `tito-slm-sin-indicio v4-cita-libre` |
| [`2026-11-04_tanda-roles-tito-sin-indicio/c/2026-11-05_000133_tanda-roles-c-v3-orden-v1-rol`](../corridas/2026-11-04_tanda-roles-tito-sin-indicio/c/2026-11-05_000133_tanda-roles-c-v3-orden-v1-rol/) | 2026-11-05 | 150 | lista desarrollo-150 | `tito-slm-sin-indicio v3-orden-v1` |
| [`2026-11-04_tanda-roles-tito-sin-indicio/d/2026-11-05_001227_tanda-roles-d-v4-rol`](../corridas/2026-11-04_tanda-roles-tito-sin-indicio/d/2026-11-05_001227_tanda-roles-d-v4-rol/) | 2026-11-05 | 150 | lista desarrollo-150 | `tito-slm-sin-indicio v4` |
| [`2026-11-05_humo-puntaje-token-1/tarea-sino/2026-11-06_014335_humo-tarea-sino`](../corridas/2026-11-05_humo-puntaje-token-1/tarea-sino/2026-11-06_014335_humo-tarea-sino/) | 2026-11-06 | 3 | 3 casos sin lista | `tarea-sino` |
| [`2026-11-05_humo-puntaje-token-1/v4-sin-reglas-sino/2026-11-06_014401_humo-v4-sin-reglas-sino`](../corridas/2026-11-05_humo-puntaje-token-1/v4-sin-reglas-sino/2026-11-06_014401_humo-v4-sin-reglas-sino/) | 2026-11-06 | 3 | 3 casos sin lista | `v4-sin-reglas-sino` |
| [`2026-11-05_humo-puntaje-token-1/v4-sino/2026-11-06_014342_humo-v4-sino`](../corridas/2026-11-05_humo-puntaje-token-1/v4-sino/2026-11-06_014342_humo-v4-sino/) | 2026-11-06 | 3 | 3 casos sin lista | `v4-sino` |
| [`2026-11-05_humo-puntaje-token-2/tarea-a1/2026-11-06_022053_humo-tarea-a1`](../corridas/2026-11-05_humo-puntaje-token-2/tarea-a1/2026-11-06_022053_humo-tarea-a1/) | 2026-11-06 | 3 | 3 casos sin lista | `tarea-a1` |
| [`2026-11-05_humo-puntaje-token-2/v4-a1/2026-11-06_022101_humo-v4-a1`](../corridas/2026-11-05_humo-puntaje-token-2/v4-a1/2026-11-06_022101_humo-v4-a1/) | 2026-11-06 | 3 | 3 casos sin lista | `v4-a1` |
| [`2026-11-05_humo-puntaje-token-2/v4-a2/2026-11-06_022120_humo-v4-a2`](../corridas/2026-11-05_humo-puntaje-token-2/v4-a2/2026-11-06_022120_humo-v4-a2/) | 2026-11-06 | 3 | 3 casos sin lista | `v4-a2` |
| [`2026-11-05_prompt-v5-tito-sin-indicio/a/2026-11-05_140022_prompt-v5-a-v5-maniobras-rol`](../corridas/2026-11-05_prompt-v5-tito-sin-indicio/a/2026-11-05_140022_prompt-v5-a-v5-maniobras-rol/) | 2026-11-05 | 150 | lista desarrollo-150 | `tito-slm-sin-indicio v5-maniobras` |
| [`2026-11-05_prompt-v5-tito-sin-indicio/b/2026-11-05_142148_prompt-v5-b-v5-rol`](../corridas/2026-11-05_prompt-v5-tito-sin-indicio/b/2026-11-05_142148_prompt-v5-b-v5-rol/) | 2026-11-05 | 150 | lista desarrollo-150 | `tito-slm-sin-indicio v5` |
| [`2026-11-05_prompt-v5-tito-sin-indicio/c/2026-11-05_144005_prompt-v5-c-v5-indirectos-rol`](../corridas/2026-11-05_prompt-v5-tito-sin-indicio/c/2026-11-05_144005_prompt-v5-c-v5-indirectos-rol/) | 2026-11-05 | 150 | lista desarrollo-150 | `tito-slm-sin-indicio v5-indirectos` |
| [`2026-11-05_prompt-v5-tito-sin-indicio/controles/2026-11-05_151405_prompt-v5-controles`](../corridas/2026-11-05_prompt-v5-tito-sin-indicio/controles/2026-11-05_151405_prompt-v5-controles/) | 2026-11-05 | 18 | 18 casos sin lista (18 ya no están en desarrollo) | `v4`, `tito-slm-sin-indicio v4`, `v5-maniobras`, `tito-slm-sin-indicio v5-maniobras` … |
| [`2026-11-05_prompt-v5-tito-sin-indicio/d/2026-11-05_145716_prompt-v5-d-v5-sin-excepcion-rol`](../corridas/2026-11-05_prompt-v5-tito-sin-indicio/d/2026-11-05_145716_prompt-v5-d-v5-sin-excepcion-rol/) | 2026-11-05 | 150 | lista desarrollo-150 | `tito-slm-sin-indicio v5-sin-excepcion` |
| [`2026-11-05_puntaje-token-150/tarea-a1/2026-11-06_025249_puntaje-token-tarea-a1`](../corridas/2026-11-05_puntaje-token-150/tarea-a1/2026-11-06_025249_puntaje-token-tarea-a1/) | 2026-11-06 | 150 | lista desarrollo-150 | `tarea-a1` |
| [`2026-11-05_puntaje-token-150/tarea-a1-rep/2026-11-06_030239_puntaje-token-tarea-a1-rep`](../corridas/2026-11-05_puntaje-token-150/tarea-a1-rep/2026-11-06_030239_puntaje-token-tarea-a1-rep/) | 2026-11-06 | 150 | lista desarrollo-150 | `tarea-a1` |
| [`2026-11-05_puntaje-token-150/v4-a1/2026-11-06_024157_puntaje-token-v4-a1`](../corridas/2026-11-05_puntaje-token-150/v4-a1/2026-11-06_024157_puntaje-token-v4-a1/) | 2026-11-06 | 150 | lista desarrollo-150 | `v4-a1` |
| [`2026-11-05_puntaje-token-150/v4-a1-rep/2026-11-06_024916_puntaje-token-v4-a1-rep`](../corridas/2026-11-05_puntaje-token-150/v4-a1-rep/2026-11-06_024916_puntaje-token-v4-a1-rep/) | 2026-11-06 | 150 | lista desarrollo-150 | `v4-a1` |
| [`2026-11-05_puntaje-token-150/v4-a2/2026-11-06_024532_puntaje-token-v4-a2`](../corridas/2026-11-05_puntaje-token-150/v4-a2/2026-11-06_024532_puntaje-token-v4-a2/) | 2026-11-06 | 150 | lista desarrollo-150 | `v4-a2` |
| [`2026-11-05_puntaje-token-150/v4-a2-rep/2026-11-06_025904_puntaje-token-v4-a2-rep`](../corridas/2026-11-05_puntaje-token-150/v4-a2-rep/2026-11-06_025904_puntaje-token-v4-a2-rep/) | 2026-11-06 | 150 | lista desarrollo-150 | `v4-a2` |
| [`2026-11-05_tito-2-v4/a/2026-11-05_185205_tito-2-v4-a-tito-viejo-2`](../corridas/2026-11-05_tito-2-v4/a/2026-11-05_185205_tito-2-v4-a-tito-viejo-2/) | 2026-11-05 | 150 | lista desarrollo-150 | `tito-viejo-2 v4` |
| [`2026-11-05_tito-2-v4/b/2026-11-05_190735_tito-2-v4-b-slm`](../corridas/2026-11-05_tito-2-v4/b/2026-11-05_190735_tito-2-v4-b-slm/) | 2026-11-05 | 150 | lista desarrollo-150 | `v4` |
| [`2026-11-06_puntaje-token-2/controles-ventas/2026-11-06_234847_puntaje-token-2-controles-ventas`](../corridas/2026-11-06_puntaje-token-2/controles-ventas/2026-11-06_234847_puntaje-token-2-controles-ventas/) | 2026-11-06 | 6 | 6 casos sin lista (6 ya no están en desarrollo) | `v4`, `v4-lectura` |
| [`2026-11-06_puntaje-token-2/humo/corrida/2026-11-06_232123_puntaje-token-2-humo`](../corridas/2026-11-06_puntaje-token-2/humo/corrida/2026-11-06_232123_puntaje-token-2-humo/) | 2026-11-06 | 3 | 3 casos sin lista | `v4-lectura`, `c-sino`, `c-digito` |
| [`2026-11-06_puntaje-token-2/v4-lectura/2026-11-06_232456_puntaje-token-2-v4-lectura`](../corridas/2026-11-06_puntaje-token-2/v4-lectura/2026-11-06_232456_puntaje-token-2-v4-lectura/) | 2026-11-06 | 150 | lista desarrollo-150 | `v4-lectura` |
| [`2026-11-06_puntaje-token-2/v4-lectura-rep/2026-11-06_233653_puntaje-token-2-v4-lectura-rep`](../corridas/2026-11-06_puntaje-token-2/v4-lectura-rep/2026-11-06_233653_puntaje-token-2-v4-lectura-rep/) | 2026-11-06 | 150 | lista desarrollo-150 | `v4-lectura` |
| [`2026-11-07_alcance-etapa-2/c-json-corte/2026-11-08_000115_etapa-2-c-json-corte`](../corridas/2026-11-07_alcance-etapa-2/c-json-corte/2026-11-08_000115_etapa-2-c-json-corte/) | 2026-11-08 | 244 | todo el desarrollo (244) | `c-json-corte` |
| [`2026-11-07_alcance-etapa-2/c-json-corte-rep/2026-11-08_002305_etapa-2-c-json-corte-rep`](../corridas/2026-11-07_alcance-etapa-2/c-json-corte-rep/2026-11-08_002305_etapa-2-c-json-corte-rep/) | 2026-11-08 | 140 | lista alcance-140 | `c-json-corte` |
| [`2026-11-07_alcance-etapa-2/controles-ventas/2026-11-08_011328_etapa-2-controles-ventas`](../corridas/2026-11-07_alcance-etapa-2/controles-ventas/2026-11-08_011328_etapa-2-controles-ventas/) | 2026-11-08 | 6 | 6 casos sin lista (6 ya no están en desarrollo) | `v4-corte`, `c-json-corte`, `v4-premisa-corte` |
| [`2026-11-07_alcance-etapa-2/humo/corrida/2026-11-07_233328_etapa-2-humo`](../corridas/2026-11-07_alcance-etapa-2/humo/corrida/2026-11-07_233328_etapa-2-humo/) | 2026-11-07 | 3 | 3 casos sin lista | `c-json-corte`, `v4-premisa-corte` |
| [`2026-11-07_alcance-etapa-2/v4-corte/2026-11-07_233745_etapa-2-v4-corte`](../corridas/2026-11-07_alcance-etapa-2/v4-corte/2026-11-07_233745_etapa-2-v4-corte/) | 2026-11-07 | 244 | todo el desarrollo (244) | `v4-corte` |
| [`2026-11-07_alcance-etapa-2/v4-premisa-corte/2026-11-08_003603_etapa-2-v4-premisa-corte`](../corridas/2026-11-07_alcance-etapa-2/v4-premisa-corte/2026-11-08_003603_etapa-2-v4-premisa-corte/) | 2026-11-08 | 244 | todo el desarrollo (244) | `v4-premisa-corte` |
| [`2026-11-07_alcance-etapa-2/v4-premisa-corte-rep/2026-11-08_005925_etapa-2-v4-premisa-corte-rep`](../corridas/2026-11-07_alcance-etapa-2/v4-premisa-corte-rep/2026-11-08_005925_etapa-2-v4-premisa-corte-rep/) | 2026-11-08 | 140 | lista alcance-140 | `v4-premisa-corte` |
| [`2026-11-07_json-cortado/humo/corrida/2026-11-07_200956_json-cortado-humo`](../corridas/2026-11-07_json-cortado/humo/corrida/2026-11-07_200956_json-cortado-humo/) | 2026-11-07 | 3 | 3 casos sin lista | `v4-corte` |
| [`2026-11-07_json-cortado/v4/2026-11-07_202509_json-cortado-v4`](../corridas/2026-11-07_json-cortado/v4/2026-11-07_202509_json-cortado-v4/) | 2026-11-07 | 150 | lista desarrollo-150 | `v4` |
| [`2026-11-07_json-cortado/v4-corte/2026-11-07_201028_json-cortado-v4-corte`](../corridas/2026-11-07_json-cortado/v4-corte/2026-11-07_201028_json-cortado-v4-corte/) | 2026-11-07 | 150 | lista desarrollo-150 | `v4-corte` |
| [`2026-11-09_pedido-critico-etapa-3/c-con-campo/2026-11-10_003427_etapa-3-c-con-campo`](../corridas/2026-11-09_pedido-critico-etapa-3/c-con-campo/2026-11-10_003427_etapa-3-c-con-campo/) | 2026-11-10 | 244 | todo el desarrollo (244) | `c-con-campo` |
| [`2026-11-09_pedido-critico-etapa-3/c-con-campo-rep/2026-11-10_010800_etapa-3-c-con-campo-rep`](../corridas/2026-11-09_pedido-critico-etapa-3/c-con-campo-rep/2026-11-10_010800_etapa-3-c-con-campo-rep/) | 2026-11-10 | 140 | lista alcance-140 | `c-con-campo` |
| [`2026-11-09_pedido-critico-etapa-3/c-sin-alerta/2026-11-10_001612_etapa-3-c-sin-alerta`](../corridas/2026-11-09_pedido-critico-etapa-3/c-sin-alerta/2026-11-10_001612_etapa-3-c-sin-alerta/) | 2026-11-10 | 244 | todo el desarrollo (244) | `c-sin-alerta` |
| [`2026-11-09_pedido-critico-etapa-3/c-sin-alerta-rep/2026-11-10_005705_etapa-3-c-sin-alerta-rep`](../corridas/2026-11-09_pedido-critico-etapa-3/c-sin-alerta-rep/2026-11-10_005705_etapa-3-c-sin-alerta-rep/) | 2026-11-10 | 140 | lista alcance-140 | `c-sin-alerta` |
| [`2026-11-09_pedido-critico-etapa-3/controles-ventas/2026-11-10_012122_etapa-3-controles-ventas`](../corridas/2026-11-09_pedido-critico-etapa-3/controles-ventas/2026-11-10_012122_etapa-3-controles-ventas/) | 2026-11-10 | 6 | 6 casos sin lista (6 ya no están en desarrollo) | `c-sin-alerta`, `c-con-campo` |
| [`2026-11-09_pedido-critico-etapa-3/humo/corrida/2026-11-10_001236_etapa-3-humo`](../corridas/2026-11-09_pedido-critico-etapa-3/humo/corrida/2026-11-10_001236_etapa-3-humo/) | 2026-11-10 | 3 | 3 casos sin lista | `c-json-corte`, `c-sin-alerta`, `c-con-campo` |
| [`2026-11-10_a56-congelada-latencia/intento-1-esquema-ignorado`](../corridas/2026-11-10_a56-congelada-latencia/intento-1-esquema-ignorado/) | 2026-11-10 | 3 | 3 casos sin lista (3 ya no están en desarrollo) |  |
| [`2026-11-10_a56-congelada-latencia`](../corridas/2026-11-10_a56-congelada-latencia/) | 2026-11-10 | 3 | 3 casos sin lista (3 ya no están en desarrollo) |  |
| [`2026-11-10_config-congelada-humo/desarrollo/2026-11-10_152954_config-congelada-desarrollo`](../corridas/2026-11-10_config-congelada-humo/desarrollo/2026-11-10_152954_config-congelada-desarrollo/) | 2026-11-10 | 244 | todo el desarrollo (244) | `c-json-corte-riesgo` |
| [`2026-11-10_config-congelada-humo/humo/corrida/2026-11-10_152633_config-congelada-humo`](../corridas/2026-11-10_config-congelada-humo/humo/corrida/2026-11-10_152633_config-congelada-humo/) | 2026-11-10 | 3 | 3 casos sin lista | `c-json-corte`, `c-json-corte-riesgo` |
| [`2026-11-10_sensibilidad-c/base/2026-11-10_191406_sensibilidad-base`](../corridas/2026-11-10_sensibilidad-c/base/2026-11-10_191406_sensibilidad-base/) | 2026-11-10 | 244 | todo el desarrollo (244) | `c-json-corte-riesgo` |
| [`2026-11-10_sensibilidad-c/base-rep/2026-11-10_195308_sensibilidad-base-rep`](../corridas/2026-11-10_sensibilidad-c/base-rep/2026-11-10_195308_sensibilidad-base-rep/) | 2026-11-10 | 140 | lista alcance-140 | `c-json-corte-riesgo` |
| [`2026-11-10_sensibilidad-c/c-ancla/2026-11-10_192350_sensibilidad-c-ancla`](../corridas/2026-11-10_sensibilidad-c/c-ancla/2026-11-10_192350_sensibilidad-c-ancla/) | 2026-11-10 | 244 | todo el desarrollo (244) | `c-ancla-corte-riesgo` |
| [`2026-11-10_sensibilidad-c/c-ancla-rep/2026-11-10_195844_sensibilidad-c-ancla-rep`](../corridas/2026-11-10_sensibilidad-c/c-ancla-rep/2026-11-10_195844_sensibilidad-c-ancla-rep/) | 2026-11-10 | 140 | lista alcance-140 | `c-ancla-corte-riesgo` |
| [`2026-11-10_sensibilidad-c/c-premisa/2026-11-10_193330_sensibilidad-c-premisa`](../corridas/2026-11-10_sensibilidad-c/c-premisa/2026-11-10_193330_sensibilidad-c-premisa/) | 2026-11-10 | 244 | todo el desarrollo (244) | `c-premisa-corte-riesgo` |
| [`2026-11-10_sensibilidad-c/c-premisa-rep/2026-11-10_200424_sensibilidad-c-premisa-rep`](../corridas/2026-11-10_sensibilidad-c/c-premisa-rep/2026-11-10_200424_sensibilidad-c-premisa-rep/) | 2026-11-10 | 140 | lista alcance-140 | `c-premisa-corte-riesgo` |
| [`2026-11-10_sensibilidad-c/c-sin-freno/2026-11-10_194311_sensibilidad-c-sin-freno`](../corridas/2026-11-10_sensibilidad-c/c-sin-freno/2026-11-10_194311_sensibilidad-c-sin-freno/) | 2026-11-10 | 244 | todo el desarrollo (244) | `c-sin-freno-corte-riesgo` |
| [`2026-11-10_sensibilidad-c/c-sin-freno-rep/2026-11-10_201007_sensibilidad-c-sin-freno-rep`](../corridas/2026-11-10_sensibilidad-c/c-sin-freno-rep/2026-11-10_201007_sensibilidad-c-sin-freno-rep/) | 2026-11-10 | 140 | lista alcance-140 | `c-sin-freno-corte-riesgo` |
| [`2026-11-10_sensibilidad-c/humo/corrida/2026-11-10_191012_sensibilidad-humo`](../corridas/2026-11-10_sensibilidad-c/humo/corrida/2026-11-10_191012_sensibilidad-humo/) | 2026-11-10 | 3 | 3 casos sin lista | `c-json-corte-riesgo`, `c-ancla-corte-riesgo`, `c-premisa-corte-riesgo`, `c-sin-freno-corte-riesgo` |
| [`2026-11-11_a56-latencia-172/contaminadas/s6-kv-q8`](../corridas/2026-11-11_a56-latencia-172/contaminadas/s6-kv-q8/) | 2026-11-11 | 6 | 6 casos sin lista |  |
| [`2026-11-11_a56-latencia-172/contaminadas/s6-ub128`](../corridas/2026-11-11_a56-latencia-172/contaminadas/s6-ub128/) | 2026-11-11 | 6 | 6 casos sin lista |  |
| [`2026-11-11_a56-latencia-172/s6-base-t4`](../corridas/2026-11-11_a56-latencia-172/s6-base-t4/) | 2026-11-11 | 6 | 6 casos sin lista |  |
| [`2026-11-11_a56-latencia-172/s6-i8mm`](../corridas/2026-11-11_a56-latencia-172/s6-i8mm/) | 2026-11-11 | 6 | 6 casos sin lista |  |
| [`2026-11-11_a56-latencia-172/s6-kv-q8`](../corridas/2026-11-11_a56-latencia-172/s6-kv-q8/) | 2026-11-11 | 6 | 6 casos sin lista |  |
| [`2026-11-11_a56-latencia-172/s6-numero`](../corridas/2026-11-11_a56-latencia-172/s6-numero/) | 2026-11-11 | 6 | 6 casos sin lista |  |
| [`2026-11-11_a56-latencia-172/s6-rendimiento`](../corridas/2026-11-11_a56-latencia-172/s6-rendimiento/) | 2026-11-11 | 6 | 6 casos sin lista |  |
| [`2026-11-11_a56-latencia-172/s6-t6`](../corridas/2026-11-11_a56-latencia-172/s6-t6/) | 2026-11-11 | 6 | 6 casos sin lista |  |
| [`2026-11-11_a56-latencia-172/s6-t8`](../corridas/2026-11-11_a56-latencia-172/s6-t8/) | 2026-11-11 | 6 | 6 casos sin lista |  |
| [`2026-11-11_a56-latencia-172/s6-ub128`](../corridas/2026-11-11_a56-latencia-172/s6-ub128/) | 2026-11-11 | 6 | 6 casos sin lista |  |
| [`2026-11-11_a56-latencia-172/s6-vk`](../corridas/2026-11-11_a56-latencia-172/s6-vk/) | 2026-11-11 | 6 | 6 casos sin lista |  |
