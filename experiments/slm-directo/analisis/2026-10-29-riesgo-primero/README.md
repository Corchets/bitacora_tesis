# «Riesgo primero»: ¿baja la latencia si el SLM escribe solo el riesgo?

> **Estado: propuesta sin discutir.** Ensayo de desarrollo de Evaristo sobre
> [#50](https://github.com/Corchets/bitacora_tesis/issues/50). No elige modelo
> ([D09](../../../../docs/gestion/MAPA-DECISIONES.md#d09--elegir-asr-y-detector)) ni cierra la
> política de alerta ([D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental)).

## Pregunta

Con los prompts `tarea` y `v2`, el SLM escribe en cada línea un JSON de ~40 tokens
(evidencia, alerta, riesgo, motivo). Con la caché del prefijo funcionando, escribir es lo
que domina el tiempo ([caché de prefijo](../2026-10-21-cache-prefijo/README.md)). Las
preguntas:

1. Si el modelo escribe **primero y solamente el riesgo** (`{"riesgo": 0.35}`, ~8 tokens) y
   sigue escribiendo solo cuando el riesgo supera 0,6, ¿cuánto baja el tiempo por línea y por
   llamada?
2. ¿Cuánta calidad se pierde frente al `v2`, que pide la cita **antes** de decidir?
3. ¿Ayuda **acumular el puntaje** entre líneas (idea de Mateo)? Una línea sola puede no ser
   riesgosa y dos o tres juntas sí. El contexto ya se acumula: el modelo recibe toda la
   transcripción en cada línea. Lo que se prueba acá es la acumulación en la política de aviso.

## Cómo funciona

- **Etapa 1:** prompt [`riesgo.txt`](../../prompts/riesgo.txt) con la escala anclada (0–0,3
  charla normal; 0,31–0,6 señales sin pedido; > 0,6 pedido) y esquema `{"riesgo"}`, con
  `num_predict` 24. Si riesgo ≤ 0,6, la línea termina ahí.
- **Etapa 2** (solo si riesgo > 0,6): los mismos mensajes, más la respuesta de la etapa 1
  como `assistant` y el pedido [`riesgo_motivo.txt`](../../prompts/riesgo_motivo.txt) con
  esquema `{evidencia, motivo}`. Como el comienzo es idéntico, Ollama no vuelve a leer la
  transcripción. Si la etapa 2 falla, la alerta se mantiene y el error queda como `etapa2_*`.
- `actualizaciones.csv` agrega `ms_etapa1`, `ms_etapa2`, `tokens_prompt_etapa2`,
  `tokens_salida_etapa2` y `crudo_etapa2`; `ms` es la suma de las dos etapas.

## Cómo correrlo (notebook Windows, solo CPU)

Desde `experiments/slm-directo`:

```
ollama pull gemma3n:e2b
python correr.py --modelos gemma3n:e2b --prompts riesgo --solo-cpu --num-batch 32 --sin-reglas --casos SC-WA-CODE-01-e01,LG-WA-CONSULTA-01-e01 --detalle
python correr.py --modelos gemma3n:e2b --prompts riesgo --solo-cpu --num-batch 32 --sin-reglas --etiqueta win-gemma3n-e2b-riesgo-cpu
python correr.py --modelos gemma3n:e2b --prompts v2 --solo-cpu --num-batch 32 --sin-reglas --etiqueta win-gemma3n-e2b-v2-cpu
python analisis/2026-10-29-riesgo-primero/acumular.py corridas/<carpeta-riesgo> corridas/<carpeta-v2>
```

1. **Prueba rápida** (2 casos, `--detalle`): la etapa 1 tiene que tardar poco, y la etapa 2
   tiene que aparecer solo en la línea donde piden el código.
2. **Corridas completas:** 150 casos de desarrollo, primero `riesgo` y después la línea base
   `v2`, en la misma máquina. En CPU puede tardar varias horas; si se corta con Ctrl+C, lo procesado queda
   guardado y `acumular.py` usa los casos completos.
3. **`acumular.py`** escribe `acumular.md` con dos cosas:
   - **latencia por config:** ms por línea p50/p95, etapa 1, etapa 2, tokens y ms por llamada;
   - **políticas:** umbral simple, k líneas seguidas, media de las últimas w y EMA (suma con
     olvido), con τ de 0,5 a 0,9, contra la meta del tutor (≥ 80 % de estafas con aviso sobre
     todas, ≤ 15 % de falsas alarmas).

   La mejor política se elige en la mitad A y se informa en la B.

Otros modelos para después: `qwen3.5:4b`, `qwen3.5:2b`, `gemma2:2b`, `gemma3:270m`,
`gemma3:1b`, `gemma3:4b`, `gemma3n:e4b`. Se usan los mismos comandos, siempre en la misma máquina.

## Resultados

Pendiente: corrida de `gemma3n:e2b` en la notebook de Evaristo.

## Límites

- `riesgo` no está calibrado: es el número que escribe el modelo, no una probabilidad.
- Todo es desarrollo: elegir la política mirando estos 150 casos es optimista. La
  evaluación final va sobre el test reservado, después de D08.
- La etapa 2 corre una sola vez por llamada, en la primera línea con riesgo > 0,6. Si una política
  avisa en otra línea (o con τ < 0,6), la demora del aviso usa la mediana de la etapa 2.
