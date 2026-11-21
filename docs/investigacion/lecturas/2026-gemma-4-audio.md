# Gemma 4 con entrada de audio

- **Qué es:** la familia de modelos abiertos Gemma 4, de Google DeepMind, con licencia Apache 2.0. Los tamaños E2B, E4B y 12B aceptan audio, además de texto e imagen.
- **Para qué la miramos:** [#152](https://github.com/Corchets/bitacora_tesis/issues/152), la alternativa de que E2B escuche el audio de la llamada y se simplifique o se saque el ASR.
- **Fecha de consulta de todas las fuentes:** 2026-11-06.
- **Estado:** fuentes candidatas. No se citan en la tesis hasta que #152 decida si la alternativa sigue. Si queda afuera, sirven para el capítulo 11 (trabajo futuro).

> **Advertencia de método.** Las afirmaciones salen de fuentes primarias: la ficha del modelo, la documentación de LiteRT-LM, la página del modelo en Ollama y la documentación de llama.cpp. Están parafraseadas, no copiadas. Las fuentes secundarias van aparte y no se citan. Nada de esto lo medimos nosotros.

## 1. Qué dice la ficha del modelo [F1]

| Dato | Valor | Nota |
|---|---|---|
| Tamaños con audio | E2B, E4B y 12B | 26B A4B y 31B aceptan solo texto e imagen |
| Parámetros de E2B | 2,3 B efectivos; 5,1 B contando los embeddings por capa | La «E» del nombre es de «efectivos» |
| Contexto de E2B y E4B | 128K tokens | |
| Largo máximo de audio | 30 s por entrada | Una llamada se procesa por tramos |
| Tareas de audio | Reconocimiento de voz y traducción de voz a texto | La ficha también habla de analizar e interpretar audio |
| Resultados de voz de E2B | FLEURS 0,09 (menor es mejor); CoVoST 33,47 | Los resultados de voz excluyen el chino. No hay cifra para español ni para rioplatense |
| Idiomas | Más de 35 listos para usar; preentrenado en más de 140 | No hay una lista de idiomas para audio |
| Licencia | Apache 2.0 | |

## 2. Dónde corre con audio

| Runtime | Qué dice la fuente | Para nosotros |
|---|---|---|
| LiteRT-LM [F2] | Corre en Android, iOS, web, escritorio e IoT, y soporta modelos multimodales con visión y audio. Lista Gemma 4 E2B y E4B como modelos de chat, pero no dice explícitamente que acepte su audio | Candidato para el teléfono. Hay que confirmarlo en la ficha del modelo para LiteRT-LM |
| Ollama [F3] | La información del modelo dice que E2B y E4B aceptan audio, pero la tabla de tags muestra solo texto e imagen | Es lo que usamos hoy. Probarlo en la versión instalada antes de contar con eso |
| llama.cpp [F4] | Lista Gemma 4 E2B y E4B entre los modelos con audio y visión | Sirve para probar en PC o Colab con un GGUF |
| Transformers | No se consultó | Opción mínima para una prueba en Colab |

## 3. Qué no dicen las fuentes y hay que medir en #152

- Calidad del reconocimiento en español rioplatense, con voz de teléfono.
- Demora por tramo y memoria con audio, en PC y en el teléfono.
- Si conviene que E2B transcriba y después lea (opción B de #152) o que escuche directo (opción C).
- Cómo se le indica quién habla cuando el audio llega por dos canales ([D05](../../gestion/MAPA-DECISIONES.md#d05--elegir-la-fuente-de-audio-demostrable)).

## 4. Fuentes secundarias, no citables

Aparecieron en la búsqueda y no se usan como evidencia:

- MindStudio, [el codificador de audio de E2B y E4B](https://www.mindstudio.ai/blog/gemma-4-audio-encoder-e2b-e4b-speech-recognition). Dice que el codificador es alrededor de un 50 % más chico que el de Gemma 3n, sin fuente primaria.
- DEV Community, [llama.cpp suma el audio de Gemma 4](https://dev.to/soytuber/llamacpp-adds-gemma-4-audio-speculative-decoding-ollama-agent-boost-local-ai-33no). Es un resumen de segunda mano; lo confirma [F4].

## 5. Fuentes

- **[F1]** Gemma Team, Google DeepMind. *Gemma 4 model card.* https://ai.google.dev/gemma/docs/core/model_card_4
- **[F2]** Google. *LiteRT-LM overview.* https://developers.google.com/edge/litert-lm/overview
- **[F3]** Ollama. *gemma4.* https://ollama.com/library/gemma4
- **[F4]** ggml-org. *llama.cpp: Multimodal.* https://github.com/ggml-org/llama.cpp/blob/master/docs/multimodal.md
- **Informe técnico que cita la ficha, sin leer:** Gemma Team. *Gemma 4 Technical Report.* arXiv:2607.02770, 2026. https://arxiv.org/abs/2607.02770

Las cuatro primeras son fuentes web: van como `@misc` con `urldate`. El informe técnico se cita como preprint solo si se lee.

```bibtex
@misc{gemma4_modelcard,
  author  = {{Gemma Team}},
  title   = {Gemma 4 model card},
  howpublished = {Google AI for Developers},
  url     = {https://ai.google.dev/gemma/docs/core/model_card_4},
  urldate = {2026-11-06}
}
@misc{litertlm_overview,
  author  = {{Google}},
  title   = {{LiteRT-LM} overview},
  howpublished = {Google for Developers},
  url     = {https://developers.google.com/edge/litert-lm/overview},
  urldate = {2026-11-06}
}
@misc{ollama_gemma4,
  author  = {{Ollama}},
  title   = {gemma4},
  url     = {https://ollama.com/library/gemma4},
  urldate = {2026-11-06}
}
@misc{llamacpp_multimodal,
  author  = {{ggml-org}},
  title   = {llama.cpp: Multimodal},
  url     = {https://github.com/ggml-org/llama.cpp/blob/master/docs/multimodal.md},
  urldate = {2026-11-06}
}
@misc{gemma4_report,
  author        = {{Gemma Team}},
  title         = {Gemma 4 Technical Report},
  year          = {2026},
  eprint        = {2607.02770},
  archivePrefix = {arXiv},
  primaryClass  = {cs.CL},
  url           = {https://arxiv.org/abs/2607.02770}
}
```
