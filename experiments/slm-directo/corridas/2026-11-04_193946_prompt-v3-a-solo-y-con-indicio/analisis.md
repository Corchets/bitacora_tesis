# Prompt v3 en Colab: SLM solo y Tito con y sin indicio

> **Estado: propuesta sin discutir.** Diagnóstico de desarrollo para
> [#51](https://github.com/Corchets/bitacora_tesis/issues/51) sobre los 150 casos ya vistos, con
> referencias sin revisión humana. No toca la reserva, no decide D07/D08 ni reemplaza el
> [ADR 0001](../../../../docs/ingenieria/adr/0001-parakeet-filtro-y-gemma4-e2b-con-tito-viejo.md).

Corridas del 2026-11-04 en Colab con T4: esta carpeta (SLM solo y Tito con indicio) y
[`2026-11-04_201116_prompt-v3-b-tito-sin-indicio`](../2026-11-04_201116_prompt-v3-b-tito-sin-indicio/),
commit `a42e1b5`, prompt `a944aadc550480b3`. Sin fallos técnicos. Detalle en
[`comparacion-tres-condiciones.md`](comparacion-tres-condiciones.md); cifras con
[`comparar_con_v1.py`](comparar_con_v1.py).

| Medida | v1 solo (Windows) | v1 Tito con indicio (Windows) | v3 solo | v3 Tito con indicio | v3 Tito sin indicio |
|---|---:|---:|---:|---:|---:|
| Estafas con aviso | 55/75 | 51/75 | 65/75 | 63/75 | 64/75 |
| Con pedido de referencia | 54/64 | 51/64 | 64/64 | 62/64 | 63/64 |
| Falsas alarmas | 18/75 | 13/75 | 47/75 | 30/75 | 35/75 |
| · comunes | 3/51 | 5/51 | 28/51 | 17/51 | 20/51 |
| · difíciles | 15/24 | 8/24 | 19/24 | 13/24 | 15/24 |
| Aviso antes / en / después de T_R | 25/25/4 | 17/29/5 | 43/20/1 | 36/23/3 | 42/18/3 |
| Consultas al SLM | 2.218 | 1.179 | 1.680 | 867 | 791 |

**Observación.** Ninguna condición alcanza 80–85 % de estafas con 10–15 % de falsas alarmas. Contra v1,
v3 no pierde ninguna estafa ni elimina ninguna falsa alarma en las dos comparaciones con par: es un
corrimiento hacia alertar más. TR-13 y TR-08 siguen alertando.

**Respuestas.** El SLM solo copia evidencia en 1.003 de 1.568 líneas sin alerta, aunque el prompt pide
`""`. Hay motivos con atribución inventada: en `CV2-D-L-BANCO-009` cita a quien relata su PIN y responde
que se lo están pidiendo. 60 de los 112 avisos del SLM solo usan «podría».

**Límites.** v1 corrió en Windows y v3 en Colab, sin control v1 ni repetición en la misma sesión: el
tamaño de la diferencia no separa prompt y máquina, y tampoco se comparan tiempos. v3 reúne varios
cambios: ninguna diferencia se atribuye a una frase. Las causas siguen siendo hipótesis.
