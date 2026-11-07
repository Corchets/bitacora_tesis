# ADR 0005 — Elegimos con reglas escritas antes de correr y miramos la reserva una sola vez

- **Fecha:** 2026-11-06
- **Estado:** propuesta sin discutir
- **Participantes de la discusión:** Mateo Antenucci, durante la segunda vuelta de
  [#143](https://github.com/Corchets/bitacora_tesis/issues/143). Reúne prácticas que el equipo ya aplicaba, como aislar
  cada cambio (Luciano Grosso, 2026-11-04). Lo redactó un agente a pedido de Mateo y falta la revisión del equipo.
- **Ámbito:** metodología

> **Estado: propuesta sin discutir.** Las reglas estaban repartidas en #143, en los `analizar.py` de las dos vueltas
> y en el método del corpus; este ADR las junta. Sirve de insumo para el protocolo de
> [D08](../../gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental)
> ([#33](https://github.com/Corchets/bitacora_tesis/issues/33)), pero no lo cierra. La política de aviso y el límite de
> falsas alarmas se fijan en el ADR 0002.

## Contexto

- Elegimos sobre 150 conversaciones sintéticas de desarrollo, sin revisión humana. El número que vale sale de la
  reserva ([#52](https://github.com/Corchets/bitacora_tesis/issues/52)), y hay una sola.
- Cada decisión tomada mirando los resultados de desarrollo infla esas mismas cifras. Usar el test para decidir
  invalida sus garantías (Dwork et al., 2015). Los autores de Open-Jev reconocen que eligieron su receta después de
  mirar el test.
- El prompt mueve mucho el resultado. Formatos equivalentes cambian hasta 76 puntos (Sclar et al., 2024), y las
  paráfrasis cambian el ranking (Mizrahi et al., 2024).
- Con 46 estafas, cada estafa vale 2,2 puntos, y una corrida y su repetición no dan exactamente lo mismo.
- La primera vuelta de #143 no fue justa con el token: la pregunta era literal y estaba antes de la transcripción
  ([análisis](../../../experiments/slm-directo/corridas/2026-11-05_puntaje-token-150/analisis.md)).

Las fuentes de este contexto están en
[`FUENTES.md`, §2 y §5](../../../experiments/slm-directo/corridas/2026-11-06_puntaje-token-2/FUENTES.md#5-sensibilidad-al-prompt-y-sobreajuste).

## Decisión

Para comparar y elegir configuraciones, aplicamos estas nueve reglas.

1. **Desarrollo y reserva van separados, y la reserva se mira una sola vez.** Se elige sobre desarrollo. La reserva se
   corre una vez, con la configuración congelada en el ADR 0002, y después no se ajusta nada. El runner rechaza los
   casos reservados salvo con `--particion test_reservado`
   ([diseño de corpus_v2](../../../experiments/slm-directo/casos/DISENO-CORPUS-V2.md#semillas-parentesco-y-reserva)).
   *Por qué:* decidir mirando el test invalida sus garantías, y no hay otra reserva.
2. **Las reglas se escriben antes de correr.** Antes de ver resultados quedan escritos, en el issue o en el
   `analizar.py` de la corrida:
   - la vista y el límite de falsas alarmas;
   - las políticas, la grilla y los desempates;
   - la línea base y la regla de adopción.

   Lo que no estaba escrito se informa como exploración, fuera de la regla. *Por qué:* elegir la regla después de ver
   los números es elegir el número.
3. **Una diferencia de ±2 casos es ruido.** Para preferir una configuración hacen falta 3 estafas más, o 3 avisos más
   antes del pedido. Dentro de ±2 decide otro criterio escrito antes, como la latencia
   ([#141](https://github.com/Corchets/bitacora_tesis/issues/141)). *Por qué:* en la primera vuelta, las repeticiones
   quedaron a ±1 caso del punto elegido. Por ejemplo, A1 v4 dio 26/4/7 en la corrida y 26/4/6 en la repetición.
4. **Lo que no se repite no cuenta.** Cada configuración candidata se corre dos veces, con el mismo commit y la misma
   seed. Un resultado cuenta solo si la repetición lo confirma en el mismo punto, el que se eligió en la primera
   corrida. *Por qué:* las corridas no salen idénticas. Elegir el punto en una y comprobarlo en la otra separa el
   hallazgo de la suerte.
5. **Un cambio por vez.** Cada comparación cambia una sola cosa: la forma de leer con el mismo prompt (v4-L contra v4
   JSON) o el prompt con la misma lectura. Si una alternativa necesita su propio prompt para que la prueba sea justa,
   se le escribe uno y se lo mide también en JSON. *Por qué:* si cambian dos cosas, no se sabe cuál movió el
   resultado. Luciano pidió aislar cada cambio el 2026-11-04 (D08), y una alternativa no debe heredar parámetros
   pensados para otra.
6. **Los controles se escriben a ciegas.** Los casos que se agregan para mirar un problema y las anotaciones nuevas los
   hace alguien que no vio los prompts ni los resultados, con fuentes externas cuando las hay. Se informan aparte y
   no entran en la regla. *Por qué:* quien conoce el prompt puede escribir, sin querer, casos que el prompt resuelve.
   Así se hicieron los 6 [controles de ventas](../../../experiments/slm-directo/casos/controles-ventas.json) y la
   [anotación del alcance](../../../experiments/slm-directo/casos/alcance-desarrollo.json). La revisión de
   [#145](https://github.com/Corchets/bitacora_tesis/issues/145) sigue la misma idea: la planilla no dice cuáles detectó
   el sistema, y no revisa quien escribió los casos o analizó sus resultados.
7. **Las reglas del prompt salen de fuentes externas, no de los fallos.** Lo que el prompt considera estafa, y lo que
   no, se apoya en fuentes de bancos, organismos y denuncias. No se agregan reglas, excepciones ni ejemplos escritos
   para arreglar casos del corpus con el que se mide. *Por qué:* una regla escrita mirando los fallos sube las cifras
   de desarrollo y no dice nada del resto. Por eso no se vuelve a proponer la opción (b), una excepción que se escribió
   después de mirar casos. En cambio, la lista de acciones de los prompts S y C coincide con lo que los bancos dicen
   que nunca piden
   ([`FUENTES.md`, §1](../../../experiments/slm-directo/corridas/2026-11-06_puntaje-token-2/FUENTES.md#1-estafas-y-llamadas-legítimas-en-argentina)).
8. **Los casos manuales no filtran.** Laboratorio, piloto y trampa (los 53 casos anteriores a corpus_v2) se informan
   aparte, como chequeo: no descartan configuraciones ni sirven para elegir. El único filtro antes de correr es la
   prueba de humo de formato. *Por qué:* no anticipan el orden de los detectores en corpus_v2. Con el primer aviso, v1
   y v4 detectan todas las estafas de laboratorio y del piloto. En falsas alarmas, los manuales prefieren v4 (11
   contra 15 sobre 24 legítimas), mientras que corpus_v2 prefiere v1 (4 contra 6 sobre 51). Los dos prompts siguen en
   análisis: la comparación muestra que los dos conjuntos no coinciden, no cuál prompt es mejor.
9. **La pregunta va al final y el comienzo queda estable.** En las lecturas de token, la pregunta va al final del
   mensaje del usuario, después de la transcripción, y nada que cambie entre pedidos va al comienzo. *Por qué:*
   - **Es más justo.** En la primera vuelta, la pregunta antes de la transcripción fue uno de los motivos por los que
     la prueba no se consideró justa. En contextos largos, poner la consulta al final mejoró los resultados hasta un
     30 % en las pruebas de Anthropic con Claude.
   - **Es más barato.** Ollama reutiliza la parte inicial que se repite de una línea a la otra
     ([nota sobre Gemma 4 y la caché](../../../experiments/slm-directo/corridas/2026-11-06_puntaje-token-2/NOTA-GEMMA4-Y-CACHE.md);
     [`FUENTES.md`, §4](../../../experiments/slm-directo/corridas/2026-11-06_puntaje-token-2/FUENTES.md#4-prompts-y-formato)).

## Alternativas consideradas

| Alternativa | A favor | En contra | Por qué se descartó |
|---|---|---|---|
| Ajustar el prompt sobre los fallos del corpus hasta que pasen | Sube rápido las cifras de desarrollo | El modelo se adapta al generador, y el sesgo de dirección muestra que el corpus tiene atajos ([ADR 0004](0004-legitimas-entrantes-nuevas-y-test-aparte.md)) | Es forzar que las pruebas pasen |
| Decidir por cualquier diferencia, sin margen | Es más simple | Una corrida y su repetición difieren en un caso | Se fija el margen de ±2 |
| Una sola corrida por configuración | Cuesta la mitad en Colab | No se sabe si el punto elegido se sostiene | Se repite cada candidata |
| Filtrar con los casos manuales antes de correr los 150 | Son 53 casos y la corrida es corta | Ordenan los detectores distinto que corpus_v2 | Solo filtra la prueba de humo de formato |
| Comparar configuraciones que cambian varias cosas a la vez | Hacen falta menos corridas | No se sabe qué causó la diferencia | Un cambio por vez |
| Usar la reserva, o una parte, para validar | Hay más datos para elegir | Invalida el único número que vale, y no hay otra reserva | Se mira una sola vez |

## Consecuencias

- Cada candidata cuesta dos corridas en Colab T4. La etapa 1 de la segunda vuelta lleva unos 35 minutos.
- Con 46 estafas no se ven efectos de 1 o 2 casos. Queda como limitación declarada.
- El margen de ±2 se midió en corpus_v2. Dentro del alcance hay otras legítimas
  ([ADR 0004](0004-legitimas-entrantes-nuevas-y-test-aparte.md)), así que hay que confirmarlo con la repetición de esa
  vista antes de usarlo para decidir.
- La exploración se permite, pero se rotula y no decide.
- Si la configuración falla en la reserva, se informa tal cual. Para otra vuelta harían falta datos nuevos, como los de
  [#144](https://github.com/Corchets/bitacora_tesis/issues/144).

**Para reconsiderarla:** que dos repeticiones de la misma configuración difieran en más de 2 casos. En ese caso, el
margen se agranda antes de la comparación siguiente.

## Referencias

- [#143](https://github.com/Corchets/bitacora_tesis/issues/143): regla de elección y de adopción, escrita antes de
  correr.
- Primera vuelta: [`analizar.py`](../../../experiments/slm-directo/corridas/2026-11-05_puntaje-token-150/analizar.py) y
  [análisis](../../../experiments/slm-directo/corridas/2026-11-05_puntaje-token-150/analisis.md), con las repeticiones.
- Segunda vuelta: [`analizar.py`](../../../experiments/slm-directo/corridas/2026-11-06_puntaje-token-2/analizar.py),
  con las decisiones en el docstring.
- [`FUENTES.md`](../../../experiments/slm-directo/corridas/2026-11-06_puntaje-token-2/FUENTES.md): §2 (Open-Jev), §4
  (prompts y formato) y §5 (Dwork; Sclar; Mizrahi; Husain y Shankar).
- [Nota sobre Gemma 4 y la caché](../../../experiments/slm-directo/corridas/2026-11-06_puntaje-token-2/NOTA-GEMMA4-Y-CACHE.md).
- [Método del corpus, §9](../../corpus/METODO-CREACION-CORPUS.md#9-división-de-datos) y
  [D08](../../gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental) (pedido de Luciano del 2026-11-04).
- Comparación de los manuales: corridas JSON
  [`2026-11-04_sin-indicio-150/a`](../../../experiments/slm-directo/corridas/2026-11-04_sin-indicio-150/) (v1) y
  [`2026-11-05_tito-2-v4/b`](../../../experiments/slm-directo/corridas/2026-11-05_tito-2-v4/) (v4), con el primer aviso.
