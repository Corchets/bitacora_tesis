# #143, revisión de producto: análisis

> **Estado: propuesta sin discutir.** Desarrollo; no se tocó la reserva, las legítimas de test ni #144. Mateo la corrió
> en Colab T4 el 2026-11-18, y se analizó el mismo día. El resultado sale de la [regla](README.md#regla-escrita-antes-de-correr)
> del tag `colab/143-revision-producto`; la lectura de más abajo es posterior y no decide.

**Resultado de la regla escrita antes de correr: no pasa ninguna, queda `c-premisa-corte-riesgo`.**

- `c-codigo` pierde detección: −5 antes del pedido y −3 a tiempo.
- `c-consejos` queda igual en detección (ninguna cifra se mueve más de 1) y no suma 3 en ninguna.
- `c-freno` suma +4 antes del pedido, pero suma +9 falsas alarmas estrictas.

**Las dos versiones de la regla no coinciden.** Con la anotación original, que no decide, `c-freno` pasaría: el tope de
esa versión mira solo las 29 cotidianas (+1), y las FA totales suben de 24 a 36. Decide «producto» porque Mateo aceptó
las etiquetas el 2026-11-18, antes de correr.

La salida completa está en [`analisis-salida.md`](analisis-salida.md).

## Verificación de los ZIP

- Cada ZIP se descomprimió en un directorio vacío nuevo. Los nueve parciales (la humo y las ocho corridas) coinciden
  archivo por archivo con su carpeta en el final.
- `commit.txt`, los `TERMINADA.txt` y los ocho manifiestos dan `30746d3`, el commit del tag
  `colab/143-revision-producto`, sin cambios sin commitear.
- El sha256 de `colab/probar_revision_producto.py` en el tag coincide con `script-sha256.txt` (`2444a974…`).
- El digest coincide en los manifiestos y en `digest.txt` (`b37049369adf…`), con Ollama 0.40.14 en una Tesla T4.
- No hay casos de la reserva ni de test. Cada corrida sobre los 244 tardó 9,7 a 10,4 minutos, y cada repetición, 5,8
  a 6,0.

## La regla, paso a paso

**Humo de formato:** pasan las cuatro. Todas leen el riesgo, con su coma, en 48/48 líneas.

**Control:** las ocho corridas sin problemas, y 0 líneas inválidas. En las de los 244 consultaron 2.177 líneas de OTRA,
y en las repeticiones, 1.313.

**Cifras (alcance-140):**

| corrida | estafas | antes del pedido | a tiempo | antes del cumplimiento | **FA estrictas** (/75) | tolerables (/18) | FA cotidianas (/29) | FA (/94) |
|---|---|---|---|---|---|---|---|---|
| base | 41/46 | 20/36 | 29/36 | 13/15 | 11 | 12 | 2 | 24 |
| `c-codigo` | 39/46 | 15/36 | 26/36 | 13/15 | 10 | 12 | 2 | 23 |
| `c-consejos` | 41/46 | 19/36 | 28/36 | 14/15 | 10 | 11 | 1 | 22 |
| `c-freno` | 42/46 | **24/36** | 30/36 | 13/15 | 20 | 15 | 3 | 36 |
| base, repetición | 40/46 | 20/36 | 29/36 | 12/15 | 13 | 11 | 2 | 25 |
| `c-codigo`, repetición | 41/46 | 15/36 | 27/36 | **15/15** | 7 | 12 | 2 | 20 |
| `c-consejos`, repetición | 42/46 | 18/36 | 28/36 | 14/15 | 7 | 10 | 0 | 18 |
| `c-freno`, repetición | 42/46 | **24/36** | 30/36 | 13/15 | 19 | 15 | 3 | 35 |

En negrita, lo que gana 3 o más contra la base de su tanda. `ENT-L-SOPORTE-005`, la que debería avisar, avisa en las
ocho.

**Veredicto por variante, versión «producto»:**
- **`c-codigo`: no pasa.** No suma 3 en ninguna cifra y pierde 3 o más en dos: −5 antes del pedido y −3 a tiempo. La
  repetición repite el −5.
- **`c-consejos`: no pasa.** No suma 3 en ninguna cifra: +0 estafas, −1 antes del pedido, −1 a tiempo y +1 antes del
  cumplimiento.
- **`c-freno`: no pasa.** Suma +4 antes del pedido, y la repetición lo sostiene (+4). Pero suma +9 FA estrictas (+6 en
  la repetición), contra un tope de menos de 3.

**Con la vía por FA que se sacó,** el resultado sería el mismo: pedía bajar 3 o más las FA estrictas en la corrida y en
la repetición, y `c-codigo` y `c-consejos` bajan 1 en la corrida (6 en la repetición).

## Lectura, después de ver los resultados (no decide)

**El ruido entre tandas es del tamaño de casi todo lo que se ve.** La base es el mismo prompt que `c-premisa` en la
[sensibilidad](../2026-11-10_sensibilidad-c/analisis.md), con la misma semilla, y da otros números: 41/46 y 24 FA acá
contra 40/46 y 26 allá. Entre esas dos corridas cambia avisar o no avisar en 5 de los 140 casos; entre la base y su
repetición, en 4. Un −1 o un +1 no dice nada.

**`c-codigo`: las restricciones mueven casos de lugar y no suman.** Era la sospecha de Mateo antes de correr.
- Recupera las dos de código o clave que la base no avisa (`SOPORTE-003` y `WHATSAPP-003`), las dos **después** del
  pedido. Pierde otras dos (`SOPORTE-005` y `WHATSAPP-006`). Queda en 15/17, igual que la base, con una menos a tiempo.
- Fuera de código y clave pierde tres que la base avisa: `FAMILIAR-006`, `PREMIO-002` y `PREMIO-005`.
- La oración «decir que un código no se comparte no es pedirlo» no hizo lo suyo: `ENT-L-SELECCION-002`, la legítima en
  que OTRA nombra un código para cuidarla, sigue avisando en las dos corridas.

**`c-consejos`: la mejor de las tres, y no alcanza.**
- Es la única que no pierde ninguna de código o clave: 16/17, con `WHATSAPP-003` avisada en la línea del pedido.
- Fuera de eso pierde dos de familiar (`FAMILIAR-004` y `FAMILIAR-006`) y recupera una sin pedido (`PREMIO-006`).
- En FA estrictas baja 1 en la corrida y 6 en la repetición (de 13 a 7). Deja de avisar en dos encuestas, en
  `ENT-L-SELECCION-002` y en una venta, en las dos corridas. Suma una venta, también en las dos (`ENT-L-VENTAS-006`).
- «Cortar y llamar uno mismo al número oficial» no sacó las dos FA de «llamá al 0800 de tu factura»: `LEG2-CC-06`
  avisa en las dos corridas y `LEG-CC-03` en una.
- **La baja de FA no está firme:** −1 y −6 con un ruido de ±2. Para afirmarla haría falta otra tanda, y la regla de
  esta prueba no deja pasar por FA.

**`c-freno`: reescribir el freno lo debilitó.** La hipótesis era la contraria.
- Avisa en 12 de las 21 legítimas «no debería avisar» que piden el DNI, contra 6 de la base. Seis de sus diez FA
  estrictas nuevas son un pedido de DNI en una garantía, un envío o una venta, con motivos como «te están pidiendo tu
  DNI para validar una garantía».
- Queda en 36/94 FA, lo mismo que dio `c-sin-freno`, la variante sin el párrafo. Decirle al modelo cuándo el DNI sí
  pesa funcionó como sacarle el freno.
- Lo que gana es anticipación: avisa las estafas previsionales en las primeras líneas. No recupera `PREMIO-003`.
- **La duda del DNI queda como estaba:** el párrafo parejo de `c-premisa` frena mejor que el párrafo por intención, y
  las FA por DNI en soporte y ventas no las mueve ninguna variante: `ENT-L-SOPORTE-001`, `ENT-L-VENTAS-001` y
  `LEG2-ST-03` avisan en las ocho corridas, y `LEG2-CC-05`, en siete.

**Lo que sigue sin aviso en la base:** `WHATSAPP-003` y `SOPORTE-003` (código y clave), `FAMILIAR-005`, `PREMIO-003` y
`PREMIO-006`. `PREMIO-003` no la avisa ninguna de las cuatro.

**Todo sigue pasando en el escalón del 0,3.** Con «riesgo ≥ 0,4» ninguna de las cuatro deja más de 1 FA estricta, y
las estafas avisadas caen a 14–17. La latencia no cambia: alrededor de 220 ms la consulta.

## Qué queda

- **La configuración de la evaluación final es `c-premisa-corte-riesgo`,** sin cambios. Con esto no queda ninguna
  prueba de prompt pendiente en #143.
- **Para la tesis:** con las etiquetas de producto, la congelada da 11 a 13 FA sobre 75 llamadas que no deberían
  avisar, y avisa en 11 o 12 de las 18 donde el aviso coincide con un consejo oficial. Es más informativo que «24 a 26
  de 94».
- **Límite:** es la segunda búsqueda a mano sobre los mismos 140 casos, y no encontró mejora. El número honesto lo dan
  la reserva y #144.
