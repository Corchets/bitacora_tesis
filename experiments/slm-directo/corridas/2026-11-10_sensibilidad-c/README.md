# #143, prueba de sensibilidad: tres cambios chicos a C para avisar más estafas

> **Estado: propuesta sin discutir.** Desarrollo; la reserva, las legítimas de test y #144 no se tocan. Preparada el
> 2026-11-10, a pedido de Mateo, después de la [humo de la configuración congelada](../2026-11-10_config-congelada-humo/analisis.md).
> La regla de abajo está escrita antes de correr. El Colab está en
> [`colab/README-PUNTAJE-TOKEN.md` §8](../../colab/README-PUNTAJE-TOKEN.md#8-prueba-de-sensibilidad-tag-colab143-sensibilidad).

## Por qué

La humo mostró dónde flaquea el detector ([diagnóstico](../2026-11-10_config-congelada-humo/analisis.md#diagnóstico-dónde-flaquea-el-detector-después-de-ver-los-resultados-no-decide)):
- las 10 estafas que no avisan escriben como máximo 0,2;
- en 7 de ellas hay un pedido explícito, y el riesgo no sube ni en esa línea. Son el código de WhatsApp, la contraseña y
  la plata para un supuesto familiar, que están entre las estafas reales más comunes;
- las FA no caen en llamadas cotidianas (0/29). Caen en legítimas que piden un dato o mencionan algo sensible.

Mateo (2026-11-10) prefiere avisar más estafas aunque avise en algunas legítimas dudosas, y no en las cotidianas. Le
preocupa que el prompt se haya ajustado para bajar FA a costa de la detección.

**El riesgo es de sobreajuste:** el problema se vio en desarrollo. Por eso cada variante cambia una sola cosa, sale de
fuentes externas y de la premisa del alcance (ADR 0003), no de los casos, y el número honesto lo dan después la reserva y
#144.

## Las tres variantes

Cada una es C con un solo cambio. El resto es igual a la configuración congelada: corte tras el riesgo
(`num_predict` 14), «riesgo ≥ 0,3», el motivo de C en el primer aviso y solo OTRA.

| variante | qué cambia | hipótesis |
|---|---|---|
| `c-ancla` | [`salida_json_c_ancla.txt`](../../prompts/salida_json_c_ancla.txt): la definición del riesgo agrega «si OTRA ya está llevando a PROTEGIDA a hacer o entregar alguna de las cosas de la lista de arriba, el riesgo es 0.7 o más, aunque la charla sea amable o OTRA diga ser un familiar o un conocido». | El modelo reconoce el pedido, pero escribe un número bajo: le falta calibración. Ancla solo la punta alta, para no mover el medio. |
| `c-premisa` | [`tarea_c_premisa.txt`](../../prompts/tarea_c_premisa.txt): un párrafo más, sin números, sobre el número no agendado. Un banco, una empresa o un organismo no pide por teléfono el código ni las claves, y un familiar que llama desde un número desconocido para pedir plata es una estafa común. «Tenelo en cuenta en el riesgo, aunque la charla sea amable.» | Es la idea de Mateo: que lo tenga en cuenta, sin forzar un número. |
| `c-sin-freno` | [`tarea_c_sin_freno.txt`](../../prompts/tarea_c_sin_freno.txt): saca el párrafo «Una llamada legítima también puede pedir el nombre, el DNI… Eso solo no la vuelve una estafa». | Ese párrafo baja las FA, y puede bajar también el riesgo de las estafas. Es la duda de Mateo puesta a prueba. |

**Fuentes:**
- el código y las claves: S01, S02, S05, S09 y S26;
- el falso familiar: S23 y S25.

Están en [`FUENTES.md` de la etapa 3](../2026-11-09_pedido-critico-etapa-3/FUENTES.md). La lista de pedidos es la de la
tarea de C, sin cambios.

**Lo que quedó afuera, y por qué:**
- **Bajar el umbral a 0,2:** avisa 46/46, pero con FA 69/94, 14 de ellas cotidianas. Se midió en la humo.
- **Una capa de reglas:** la v1 suma 5 estafas y 32 FA, y la v2 suma 1 y 9. También se midió en la humo.
- **Una pregunta literal aparte** («¿OTRA pidió un código?»): duplica las consultas, y el campo `pedido_critico` de la
  etapa 3 dejó pasar pedidos explícitos.
- **Leer la probabilidad del token del riesgo, o el ajuste fino:** obligan a elegir un umbral en una curva o a
  entrenar. No entran antes del 2026-11-15, y quedan como trabajo futuro.

## Qué corre

En Colab T4, con Ollama 0.40.14, el digest `b37049369adf…`, `num_ctx` 4096, seed 42, temperatura 0, roles,
`--sin-reglas` y `--solo-otra`. Corre todas las líneas de OTRA (`--seguir-tras-aviso`), así se puede mirar la curva. El
aviso es la primera línea de OTRA con «riesgo ≥ 0,3».

1. **Humo de formato** en los 3 casos de siempre (48 líneas), con las cuatro: la base (`c-json-corte-riesgo`) y las
   tres variantes. Pasa la que lee el riesgo, con su coma, en las 48. La que no pasa no corre; si no pasa la base, no
   corre nada.
2. **Sobre los 244:** la base, `c-ancla`, `c-premisa` y `c-sin-freno`, en ese orden.
3. **Repeticiones sobre [`alcance-140`](../../casos/listas/alcance-140.txt),** en el mismo orden.

Dura alrededor de 1 h 10.

## Regla, escrita antes de correr

**Vista:** dentro del alcance, `alcance-140`. Son 46 estafas (36 con pedido y 15 con cumplimiento) y 94 legítimas: 29
cotidianas, 38 con un pedido razonable y 27 que mencionan algo sensible (`tipo_legitima`, anotado antes).

**Cifras de detección:**
- estafas avisadas (/46);
- avisos antes del pedido (T_A < T_R, /36);
- avisos a tiempo (T_A ≤ T_R, /36);
- avisos antes del cumplimiento (T_A < T_C, /15).

**FA:** en las cotidianas (/29) y en total (/94). Las líneas inválidas no avisan.

Cada variante se compara con la base de la misma sesión. **Pasa** si cumple las cuatro condiciones:
1. suma 3 o más en al menos una cifra de detección;
2. no pierde 3 o más en ninguna cifra de detección;
3. FA en cotidianas ≤ las de la base + 2;
4. en la repetición, contra la repetición de la base, suma 3 o más en una cifra en que ganó la primera corrida, sin
   perder 3 o más en ninguna, y con FA en cotidianas ≤ las de la base + 2.

**Las FA en las legítimas dudosas no tienen tope** (Mateo, 2026-11-10). Pero si una variante que pasa suma más de 10 FA
en las legítimas con pedido o mención (en la corrida o en la repetición), no se adopta sola: decide Mateo, leyendo una
a una las FA nuevas.

**Si pasan varias,** se elige la que más suma en estafas y a tiempo, juntas, en la primera corrida. Si empatan, la de
menos FA en total. **Si no pasa ninguna,** queda la base.

Lo que se adopte reemplaza a la base en la evaluación final, con todo lo demás igual. Es provisorio, como siempre, hasta
la reserva y #144.

## Solo para mirar (no decide)

- las FA por tipo de legítima, y el motivo de cada FA nueva, para leer a mano;
- qué estafas de las que pierde la base recupera cada variante, y en qué línea;
- la curva con u = 0,1…0,9 en todas las líneas de OTRA;
- cuántos avisos salen de un 0,3 exacto;
- la latencia y el motivo, con la medición de la humo;
- `alcance-91`.

## Después de correr

1. Descomprimir cada ZIP en un directorio vacío nuevo, y correr todo Python con `-I`.
2. Verificar: los parciales coinciden con el final; el commit es el del tag, sin cambios sin commitear; el sha256 de
   `colab/probar_sensibilidad.py` y el digest coinciden; no hay casos de la reserva.
3. Copiar las carpetas acá y correr `python -I analizar.py`.

`analizar.py` se escribe mientras corre la prueba, antes de bajar los resultados, y tiene que aplicar esta regla tal
cual. La regla que vale es la de este README, que está en el tag.
