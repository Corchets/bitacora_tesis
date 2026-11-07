# ADR 0005 — Elegimos con reglas escritas antes de correr y miramos la reserva una sola vez

- **Fecha:** 2026-11-06
- **Estado:** propuesta sin discutir
- **Participantes de la discusión:** Mateo Antenucci, en la segunda vuelta de
  [#143](https://github.com/Corchets/bitacora_tesis/issues/143). Junta prácticas que el equipo ya aplicaba, como aislar
  cada cambio (Luciano Grosso, 2026-11-04).
- **Ámbito:** metodología

## Contexto

Elegimos sobre casos sintéticos de desarrollo, y hay una sola reserva. Decidir mirando el test invalida sus garantías
(Dwork et al., 2015). El prompt mueve mucho el resultado (Sclar et al., 2024; Mizrahi et al., 2024). Además, con las
46 estafas de corpus_v2, cada una vale 2,2 puntos. Las fuentes están en
[`FUENTES.md`, §5](../../../experiments/slm-directo/corridas/2026-11-06_puntaje-token-2/FUENTES.md#5-sensibilidad-al-prompt-y-sobreajuste).

## Decisión

Para comparar y elegir configuraciones aplicamos estas reglas:

1. **La reserva se mira una sola vez,** con la configuración congelada en el ADR 0002. Todo lo demás se elige sobre
   desarrollo.
2. **Las reglas se escriben antes de correr:** la vista, el límite de falsas alarmas, la política, los desempates y la
   regla de adopción. Lo que no estaba escrito se informa como exploración y no decide.
3. **Una diferencia de ±2 casos es ruido.** Para preferir una configuración hacen falta 3 estafas más, o 3 avisos más
   antes del pedido. Dentro de ±2 decide un criterio escrito antes, como la latencia.
4. **Lo que no se repite no cuenta.** Cada candidata se corre dos veces, con el mismo commit y la misma seed. El punto
   elegido en la primera corrida tiene que sostenerse en la segunda.
5. **Se cambia una cosa por vez:** el prompt o la forma de leer la salida, nunca las dos juntas. Si una alternativa
   necesita su propio prompt, ese prompt se mide también con la lectura JSON.
6. **Los controles se escriben a ciegas,** sin ver prompts ni resultados, y se informan aparte.
7. **Las reglas del prompt salen de fuentes externas,** como bancos, organismos y denuncias, y no de los fallos del
   corpus.
8. **Los casos manuales no filtran.** Los 53 anteriores a corpus_v2 se informan aparte. Antes de correr, solo filtra la
   prueba de humo de formato.
9. **La pregunta va al final y el comienzo del prompt no cambia.** Así la prueba es justa y Ollama puede reutilizar la
   caché ([nota sobre Gemma 4 y la caché](../../../experiments/slm-directo/corridas/2026-11-06_puntaje-token-2/NOTA-GEMMA4-Y-CACHE.md)).

## Alternativas consideradas

| Alternativa | A favor | En contra | Por qué se descartó |
|---|---|---|---|
| Ajustar el prompt sobre los fallos del corpus | Sube rápido las cifras de desarrollo | El modelo aprende los atajos del generador ([ADR 0004](0004-legitimas-entrantes-nuevas-y-test-aparte.md)) | Es forzar que las pruebas pasen |
| Decidir por cualquier diferencia | Es más simple | Una corrida y su repetición difieren en un caso | Se fija el margen de ±2 |
| Una sola corrida por candidata | Cuesta la mitad en Colab | No se sabe si el punto elegido se sostiene | Se repite cada candidata |
| Filtrar con los casos manuales | Son 53 casos y la corrida es corta | Ordenan los detectores distinto que corpus_v2 | Solo filtra la prueba de humo |
| Usar parte de la reserva para validar | Más datos para elegir | Invalida el único número que vale | Se mira una sola vez |

## Consecuencias

- Cada candidata cuesta dos corridas en Colab.
- Con 46 estafas no se ven efectos de 1 o 2 casos. Queda como limitación declarada.
- Si la configuración falla en la reserva, se informa tal cual.
- Es insumo para el protocolo de [D08](../../gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental), pero no
  lo cierra.

**Para reconsiderarla:** que dos repeticiones de la misma configuración difieran en más de 2 casos.

## Referencias

- [#143](https://github.com/Corchets/bitacora_tesis/issues/143): reglas de elección y de adopción, escritas antes de
  correr.
- [`FUENTES.md`](../../../experiments/slm-directo/corridas/2026-11-06_puntaje-token-2/FUENTES.md), §2, §4 y §5.
- [Método del corpus, §9](../../corpus/METODO-CREACION-CORPUS.md#9-división-de-datos).
