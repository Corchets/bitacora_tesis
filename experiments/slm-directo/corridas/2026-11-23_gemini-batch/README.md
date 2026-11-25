# #174 — Gemini 3.8 Flash Batch sobre desarrollo-150

Comparación exploratoria para la tesis. ¿Cómo cambian los avisos y su anticipación si se puntúan los mismos prefijos con Gemini 3.8 Flash Batch y con Gemma 4 E2B? El objetivo es describir los resultados para estas configuraciones sobre material de desarrollo. La evaluación principal es la [corrida del 2026-11-19](../2026-11-12_evaluacion-final/README.md). La decisión sobre la inferencia local está en [D03](../../../../docs/gestion/MAPA-DECISIONES.md#d03--congelar-alcance-y-contribución).

## Configuración fijada el 2026-11-23

- Los 150 casos sintéticos y los 1.392 prefijos de [«Solo el número»](../2026-11-21_solo-el-numero/README.md). Se reutilizan las salidas de `d150-numero` de Gemma. Cada prefijo acumula el texto por roles hasta una línea de OTRA.
- Mismo prompt íntegro `c-consejos-corte-riesgo`, mismo mensaje de usuario y mismo corte de decisión en riesgo ≥ 0,3. Gemma usa el prellenado y Gemini genera el JSON completo. Solo se lee el riesgo para decidir el aviso.
- OpenRouter Batch, modelo `google/gemini-3.8-flash`, Google Vertex, razonamiento `low`, seed solicitada 42 y temperatura del proveedor. La [ficha del endpoint](https://openrouter.ai/api/v1/models/google/gemini-3.8-flash%3Abatch/endpoints) declara seed y omite temperatura. La ficha no garantiza repetibilidad. El cliente omite el razonamiento de la respuesta.
- Tope de 336 tokens de salida por consulta, escogido con la estimación conservadora para un presupuesto total de USD 2. Las 83 consultas de `s6` forman el primer lote. Si el lote completa y devuelve puntajes válidos, cuentan para el conjunto completo y se habilita el segundo lote con la misma configuración.
- Sin reintentos. Una conversación con una consulta sin puntaje se excluye de la comparación pareada para ambos modelos y se informa. Un aviso después de un error podría ocultar un aviso anterior.
- Métricas de la [evaluación](../../../../docs/evaluacion/METRICAS.md): estafas avisadas, falsas alarmas, aviso antes del pedido, a tiempo y antes del cumplimiento donde exista la marca. Se informan pares discordantes y costo real de OpenRouter. La anticipación se mide en líneas. Las marcas son las del corpus y la comparación usa una pasada de desarrollo.

## Reproducción

Desde esta carpeta, con Python 3.10 o superior. El cliente lee `CLAVE_OPENROUTER` del archivo `.env` de la raíz, ignorado por Git. Usar una clave con límite de USD 2. Guardar recibos y resultados crudos en un directorio de salida fuera del repositorio. El cliente local arma los pedidos y calcula las métricas. La inferencia corre en infraestructura administrada de Google Vertex mediante OpenRouter.

```sh
python3 -I correr.py plan --salida /tmp/tesis-174-gemini
python3 -I correr.py enviar --lote piloto --salida /tmp/tesis-174-gemini
python3 -I correr.py consultar --lote piloto --salida /tmp/tesis-174-gemini
python3 -I correr.py enviar --lote resto --salida /tmp/tesis-174-gemini
python3 -I correr.py consultar --lote resto --salida /tmp/tesis-174-gemini
python3 -I correr.py analizar --salida /tmp/tesis-174-gemini > /tmp/tesis-174-gemini/analisis.md
```

Consultar el mismo lote hasta alcanzar un estado terminal. El envío del segundo lote comprueba el piloto, el saldo de la clave y que el costo ya informado más el estimado del resto estén dentro del presupuesto. El recibo se escribe antes del envío para poder distinguir un envío de estado incierto y evitar duplicarlo. El análisis genera `manifiesto.json` y `puntajes.csv` además de su salida Markdown.

## Resultados

El [análisis pareado](analisis.md) se regenera con el comando anterior. El [CSV](puntajes.csv) conserva ambos puntajes por línea y el fin de la respuesta de Gemini, y el [manifiesto](manifiesto.json) registra ambos lotes, huellas, proveedor y consumo. OpenRouter reportó ambas tandas como completadas. Tres salidas se cortaron por el límite de tokens y quedaron sin un JSON completo.
