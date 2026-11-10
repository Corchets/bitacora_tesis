# Gemma 4: turnos y caché del prefijo

> **Estado: propuesta sin discutir.** Nota técnica para la defensa, escrita el 2026-11-06. Fuentes en
> [`FUENTES.md`](FUENTES.md); mediciones propias en [`analisis/2026-10-21-cache-prefijo`](../../analisis/2026-10-21-cache-prefijo/README.md)
> y [#141](https://github.com/Corchets/bitacora_tesis/issues/141).

## 1. Los turnos de Gemma 4

Un modelo de chat no recibe texto suelto. Recibe una conversación dividida en **turnos**, cada uno con un rol y
encerrado entre marcas especiales que el modelo aprendió en su entrenamiento.

- **Gemma 3 y 3n** tienen solo dos roles: usuario y modelo. Las instrucciones «de sistema» se pegan al comienzo del primer
  turno del usuario. Así corrían los ensayos viejos con `gemma3n:e2b`.
- **Gemma 4** agrega un **turno de sistema propio**, según la documentación de Google. En Ollama, el modelo
  `gemma4:e2b-it-q4_K_M` no trae plantilla: los mensajes los arma un componente en Go (*renderer*) que pone las
  instrucciones en ese turno y deja el razonamiento apagado por defecto.
- **Nuestro detector ya usa ese formato.** Manda el prompt con el rol `system` y la transcripción, con la pregunta final,
  con el rol `user`. Con Gemma 4, las instrucciones van en su turno de sistema y la llamada en el turno del usuario. Es
  la estructura que recomiendan Google y Anthropic: instrucciones aparte, datos después y la pregunta al final.
- **Razonamiento:**
  - en las lecturas de token se manda `think: false`;
  - en las JSON no se manda nada y queda el valor por defecto, apagado.

  Ninguna configuración «piensa» antes de responder.
- **Límite:** no medimos si el turno de sistema rinde mejor que pegar las instrucciones en el turno del usuario.

## 2. La caché del prefijo

**Qué es.** Para responder, el modelo primero **lee** todo el prompt (*prefill*) y guarda un estado por cada token
(la caché KV). Después **escribe** la respuesta, de a un token por vez. Si el pedido siguiente empieza con exactamente
los mismos tokens, el servidor reutiliza el estado de ese comienzo común y solo lee lo nuevo.

**Por qué nos sirve.** En cada actualización la transcripción crece en una línea; todo lo anterior queda igual: el
prompt de sistema y las líneas 1 a n−1. Si se reutiliza, cada línea nueva cuesta poco aunque la llamada sea larga.

**Ollama lo hace solo, pero hay que ayudarlo:**

1. **El comienzo tiene que ser idéntico.** Nada que cambie entre pedidos puede ir al principio: ni la hora, ni un
   contador, ni otro prompt. Por eso `armar_mensaje_usuario` deja «hasta la línea n» para el final.
2. **Lo que cambia va al final:** la línea nueva y la pregunta. Por eso las preguntas de token van al final del mensaje
   del usuario.
3. **No intercalar prompts distintos en el mismo servidor.** Cada cambio de prompt invalida lo guardado. `correr.py`
   corre cada configuración entera antes de pasar a la siguiente.
4. **No cambiar `num_ctx` ni otras opciones entre pedidos,** porque recargan el modelo.
5. **En modelos que solo retoman desde puntos guardados,** como Qwen 3.5, que es híbrido, conviene bajar `num_batch`
   para que el último punto quede más cerca del final.

**Qué medimos.**
- **M1 con Qwen 3.5 0.8B:** un pedido idéntico tarda 30 ms. El de la línea siguiente relee los últimos ~512 tokens y
  tarda 480 a 1.150 ms. Con `num_batch` 32 baja a 100–175 ms.
- **Colab T4 con Gemma 4 E2B (#141):** desde el turno 6, la lectura tarda unos 98 ms y no crece aunque el contexto pase
  de 500 a 920 tokens. Es coherente con que se reutilice, pero todavía no lo comparamos con la caché apagada.

**Para comprobarlo,** se repite `medir_cache.py`: el mismo pedido en secuencia, repetido y «en frío» (con una marca
distinta al comienzo), comparando `prompt_eval_duration`. Además se lee en el registro de Ollama desde qué posición
retoma cada pedido.

**Por qué importa más con el token.** Si se responde con un solo token, casi todo el tiempo es la lectura. Con la caché,
cada línea lee pocos tokens. Sin ella, relee la llamada entera, y el tiempo crece a medida que avanza.

**En el teléfono no está garantizado.** Depende del motor (llama.cpp, LiteRT/MediaPipe o MLC). Es lo que tiene que
medir #141.
