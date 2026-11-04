# v1 y v3 con Tito sin indicio, en Colab: comparación y cómo bajar las falsas alarmas

**Fecha:** 2026-11-04. **Issue:** [#51](https://github.com/Corchets/bitacora_tesis/issues/51), sigue abierto.

> **Estado: propuesta sin discutir.** Diagnóstico sobre los 150 de desarrollo, ya vistos y sin revisión
> humana. No toca la reserva, no decide
> [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) ni
> [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental) y no cambia el
> [ADR 0001](../../../../docs/ingenieria/adr/0001-parakeet-filtro-y-gemma4-e2b-con-tito-viejo.md). No se corrió
> ningún modelo: todo sale de los CSV, con `python -I comparar_con_v1_colab.py`.

## Conclusión

**Conviene partir de v1, no de v3.** Con Tito sin indicio, v1 queda a 3 falsas alarmas y 6 estafas de la
meta; v3 queda a 24 falsas alarmas. Las alarmas y las estafas de v1 están contenidas en las de v3: v3
funciona como un detector más sensible, no como uno que distinga mejor. Bajar v3 con un umbral de riesgo
tampoco sirve, porque a igual detección que v1 da 10 falsas alarmas más.

| Tito sin indicio | Estafas con aviso | Falsas alarmas | Comunes | Difíciles | Cita el pedido | Consultas |
|---|---:|---:|---:|---:|---:|---:|
| **v1** (corrida `sin-indicio-150`) | 54/75 (72 %) | 14/75 (19 %) | 4/51 | 10/24 | 27/53 | 1.140 |
| **v3** (corrida de Luciano) | 64/75 (85 %) | 35/75 (47 %) | 20/51 | 15/24 | 20/63 | 791 |
| **Meta del tutor** | 60–64 | 8–11 | | | | |

«Cita el pedido»: la cita del primer aviso incluye la línea `T_R` u otra marcada como pedido, entre las
estafas con pedido que tuvieron aviso. No cuenta pasos previos reales, así que es un piso.

## Las corridas

La de v1 es [`2026-11-04_sin-indicio-150`](../2026-11-04_sin-indicio-150/conclusiones.md), de la rama
`claude/clever-fermi-fxgrx4`. Se confirmó lo que pedía el handoff: commit `4916ead`, prompt `tarea`
(`bf4284996898c45d`), `--sin-indicio`, y el mensaje al SLM es igual al del SLM solo. Comparte con la de v3 los
150 casos, GPU T4, Ollama 0.40.14, digest del modelo, artefacto de Tito, umbral 0,5 y seed 42. Los commits figuran
con autor «Claude», así que el repositorio no muestra quién la corrió: la atribución a Evaristo es de Luciano.

**Esto levanta el límite de las máquinas distintas.** v1 da casi lo mismo en Windows y en Colab: SLM solo 55/18
y 55/19; Tito con indicio 51/13 y 50/12. Repetida en Colab, varía 1 estafa y 1 falsa alarma. El salto de v3 no se
explica por la máquina ni por ese ruido, aunque cada prompt se corrió en una sesión de Colab distinta.

| | Estafas v1 → v3 | Falsas alarmas v1 → v3 |
|---|---:|---:|
| SLM solo | 55 → 65 | 19 → 47 |
| Tito con indicio | 50 → 63 | 12 → 30 |
| Tito sin indicio | 54 → 64 | 14 → 35 |

En las tres condiciones v3 no pierde ninguna estafa ni elimina ninguna falsa alarma.

**Sacar el indicio:** con v1 suma 4 estafas y 2 falsas alarmas; con v3, 1 y 5. No apunta siempre para el mismo
lado, y con repetición el ruido ronda 1 o 2 casos.

## Qué compran las 10 estafas que gana v3

Lectura propia del primer aviso, sin revisión humana:

| Lectura | Casos |
|---|---|
| Cita el pedido (2) | ORGANISMO_PREVISIONAL-003, PREMIO-003 |
| Cita un paso previo real (5) | ORGANISMO_PREVISIONAL-004, SOPORTE-001, SOPORTE-005, WHATSAPP-004, `TR-04` |
| Cita a la víctima, sin base (3) | FAMILIAR-004, FAMILIAR-005, FAMILIAR-006 |

Por esas 10 paga 21 falsas alarmas nuevas. Las 11 estafas que no detecta ninguna son 10 sin pedido de referencia
y PREMIO-001, donde Tito nunca activa. Como la meta se mide sobre
[todas las estafas](../../../../docs/gestion/seguimientos/2026-10-28.md), llegar a 60 con un detector que avisa por
pedidos exige casi todas las 64 que lo tienen.

## De qué están hechas las falsas alarmas

Lectura propia, sin revisión humana; la lista está en el script.

| Clase | v1 | v3 | Ejemplo | Vía |
|---|---:|---:|---|---|
| Consejo seguro, explicación o negación | 3 | 10 | «Cortá y entrá vos a la aplicación oficial» | Regla de prompt |
| Quien ofrece, pregunta o relata es la propia persona | 3 | 9 | «¿Querés que te diga los últimos números?» | Decirle quién es la persona protegida |
| Dato de identificación en una gestión legítima | 4 | 7 | «Decime los últimos cuatro dígitos» | Difícil: una estafa pide igual |
| Dinero o encargo cotidiano entre conocidos | 3 | 7 | «Mandame el alias» | Difícil sin verificar identidad |
| Frase ambigua o pedido inexistente | 1 | 2 | «Pasame el código» (candado) | Persistencia, a medir |

Las dos primeras clases suman 6 de las 14 de v1: alcanzarían para entrar en la meta si se eliminaran y no se
perdiera ninguna estafa. Eso es un techo, no una predicción.

**Un hallazgo que no se había probado:** el SLM nunca sabe a quién protege. El mensaje le dice que «las letras no
indican quién llamó ni quién es sospechoso» ([`detectores.py`](../../detectores.py)), pero el servidor de la demo
ya distingue `protegida` y `otra`. **Hipótesis, sin probar:** por eso escribe «te están pidiendo» sobre lo que la persona misma ofrece, y la
regla de ofrecimiento de v3 no frenó esos casos. En el corpus ese rol no está anotado: en las estafas con pedido
se deduce de `T_R`, en el resto hay que anotarlo.

## Lo que no conviene hacer

| Idea | Resultado | Lectura |
|---|---|---|
| Exigir más riesgo a v1 | ≥ 0,6: de 54/14 a 31/6 | Pierde 23 estafas para sacar 8 alarmas |
| Exigir más riesgo a v3 | ≥ 0,7: de 64/35 a 54/24 | Igual detección que v1, con 10 alarmas más |
| Combinar v1 y v3 | Unión 64/35, intersección 54/14 | Solo reproduce a v3 o a v1 |
| Vetar citas de la propia víctima | Saca hasta 3 alarmas en v1; 8 estafas citan solo a la víctima | Se pierde más de lo que se gana |
| Subir el umbral de Tito por su puntaje | Mediana al activar: 0,98 en estafas, 0,99 en alarmas | No las separa en ese punto. Tito no puntúa después de activar, así que no se puede simular |

Los vetos están censurados: las corridas cortan en el primer aviso y no se sabe qué pasaría después. Con
diferencias así de grandes no cambia la lectura, pero son cotas.

## Próxima prueba propuesta

> **Estado: propuesta sin discutir.** Requiere acuerdo: parte de v1, cuando la decisión del 2026-11-04 era conservar
> el orden de v2. No cambia demo, Tito, umbrales ni espera. Todo va en Colab, sobre Tito sin indicio, en la misma
> sesión. Cada condición tarda unos 11 minutos.

| # | Condición | Qué responde | Riesgo a mirar |
|---|---|---|---|
| 0 | v1, control | Línea de base y ruido en la sesión | |
| 1 | v3 con los campos en el orden de v1 | Si la evidencia primero causa el salto: cita en 509 de 692 líneas sin alerta contra 0 de 1.072 en v1 | |
| 2 | v1 + regla de canal propio | Si cae la clase de consejos | `LAB-arca-deuda-parafrasis` y BANCO-002 también mandan a la aplicación |
| 3 | v1 + persona protegida en el mensaje | Si cae la clase de ofrecimientos | Exige anotar el rol; `TR-10` es un ofrecimiento inducido |
| 4 | v1 + lista ampliada y pedidos indirectos de v3 | Si gana estafas sin el resto de v3 | Puede traer de vuelta las alarmas |
| 5 | Combinación de lo que sirva de 2, 3 y 4 | Si llega a la meta | |

Texto tentativo de la regla de la condición 2, a continuación de «No alcanza con mencionar…»:

> Tampoco alcanza con aconsejar que corte y entre por su cuenta a la aplicación o a la página oficial, o que llame a
> un número que ya tiene, si no le dan un plazo, una amenaza, un enlace ni pasos a seguir.

**Aparte, una corrida de diagnóstico:** v1 con Tito sin indicio y `--seguir-tras-aviso`. Sin tocar el prompt, muestra
si las alarmas se sostienen y permite simular persistencia y vetos sin censura. Solo se simula: la política de
espera sigue en D08.

## Límites

- Las clases y las reglas salen de estos 150 casos, ya vistos. Una mejora acá puede ser ajuste a ellos y hay que
  validarla fuera del desarrollo cuando D08 lo defina. Las reglas evitan frases de los casos por eso mismo.
- `T_R` y las referencias no tienen revisión humana. Algunas legítimas, como `TR-11`, no se distinguen de una estafa
  con el texto solo: conviene decidir en D07 si deben contar igual.
- Las corridas de v1 y v3 son de la misma configuración, pero no de la misma sesión.
