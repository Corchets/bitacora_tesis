# #143, etapa 3: análisis

> **Estado: propuesta sin discutir.** Desarrollo; la reserva no se corrió. Se corrió en Colab T4 el 2026-11-09 y se
> analizó el mismo día.

**Resultado de la regla escrita antes de correr:** queda la base, **C de la etapa 2 cortado tras el riesgo, con «riesgo
≥ 0,3»**. Es provisoria hasta la reserva, y consulta **solo en las líneas de OTRA**. C con campo no se adopta: pierde 4
avisos a tiempo, y 3 en la repetición.

La salida completa está en [`analisis-salida.md`](analisis-salida.md). El diagnóstico, escrito después de ver los
resultados, está en [`diagnostico-salida.md`](diagnostico-salida.md).

## Verificación de los ZIP

- Cada ZIP se descomprimió en un directorio vacío nuevo, y los 6 parciales coinciden archivo por archivo con su
  carpeta en el final.
- `commit.txt`, los 5 `TERMINADA.txt` y los 6 manifiestos dan `c3c1ffa`, sin cambios sin commitear.
- El sha256 de `colab/probar_etapa_3.py` en el tag coincide con `script-sha256.txt` (`e2c2dd4f…`).
- El digest del modelo coincide en los manifiestos y en `digest.txt` (`b37049369adf…`), con Ollama 0.40.14.
- La segunda consulta es la de `motivo_c_corte.txt`, y no hay casos de la reserva.
- **Humo:** pasa en las dos versiones, con 48/48 líneas leídas y ninguna en el tope.
- Las cuatro corridas tienen 0 líneas inválidas.

## La regla, paso a paso

Dentro del alcance: 46 estafas (36 con pedido) y 94 legítimas.

| configuración | estafas | antes del pedido | a tiempo | FA |
|---|---|---|---|---|
| C de la etapa 2, cortado tras el riesgo (**la base**) | 36/46 | 17/36 | 25/36 | 27/94 |
| la base, repetición | 36/46 | 16/36 | 25/36 | 26/94 |
| C sin alerta | 39/46 | 18/36 | 25/36 | 32/94 |
| C con campo | 37/46 | 15/36 | 21/36 | 18/94 |
| C con campo, repetición | 36/46 | 16/36 | 22/36 | 17/94 |

1. **La base contra la etapa 2:** C sin alerta se aparta en +3 estafas y +5 FA, más de ±2. Por eso la base pasa a ser
   el prompt de la etapa 2 cortado tras el riesgo.
   - En ese JSON el riesgo es el primer campo, así que el riesgo leído de `c-json-corte` es el que daría el corte.
2. **C con campo contra la base:** suma 1 estafa, pero pierde 2 avisos antes del pedido y 4 a tiempo. Pierde 3 o más,
   así que no se adopta.
   - Contra C sin alerta también pierde 4 a tiempo.
3. **`alcance-91`:** el resultado no se invierte.
4. **«Solo OTRA»:** no empeora ninguna cifra en más de 2. La corrida da −1, −2, 0 y −3 FA; la repetición, 0, −1, 0 y
   −1 FA. **Se adopta.**

## Qué se aprende (diagnóstico, después de ver los resultados)

**1. El aviso de C es, casi siempre, «el modelo escribió 0,3 una vez».** El riesgo toma casi solo los valores 0,1, 0,2,
0,3 y 0,6.
- En la base, 31 de los 36 avisos en estafas y 25 de las 27 FA salen de un 0,3 exacto.
- Con 0,4, la base avisa 15/46 estafas, con 9/94 FA.
- Por eso un cambio chico de prompt mueve varias cifras. C sin alerta solo saca la descripción de los campos que no se
  escriben, y coincide con la etapa 2 en el 77 % de las líneas. Dos corridas iguales coinciden en el 96 %.
- El ±2 del ADR 0005 mide bien el ruido entre corridas, pero queda chico para un cambio de prompt.

**2. C con campo baja las FA de 27 a 18, y esa baja es sólida.**
- Las legítimas que avisan solo con la base son 10, contra 1 solo con C con campo (McNemar exacto, p = 0,012). En la
  repetición son 9 contra 0 (p = 0,004).
- La pérdida a tiempo es de 5 pares contra 1 (p = 0,22).
- En los 5 casos que pierde, la base avisó con 0,3 y C con campo escribió 0,2.
- La regla cuenta la pérdida igual. Cambiarla ahora sería decidir después de mirar los resultados.

**3. La alerta fuerte (`pedido_critico`) avisa pocas veces, y cuando avisa suele acertar.**
- Salta a tiempo en 12 de las 30 estafas con pedido crítico, y tarde en 3. Salta en 2 de las 16 sin pedido crítico, y
  en 5 de las 94 legítimas.
- Se le escapan pedidos explícitos. En `CV2-D-V-WHATSAPP-001`, «decime los seis números» deja `pedido_critico` en false
  toda la llamada, incluso cuando PROTEGIDA dicta el código.
- **Las 5 legítimas:**
  - **2 son el consejo seguro** «cortá y llamá al número del dorso de tu tarjeta», que choca con el ejemplo «cortar y
    llamar a otro número» de la definición;
  - **2 son pedidos reales de una llamada legítima:** el soporte remoto (`ENT-L-SOPORTE-005`) y la seña por
    transferencia (`ENT-L-VENTAS-009`);
  - **en la otra, PROTEGIDA empieza a dictar un código sin que nadie se lo pida** (`ENT-L-BANCO-006`), y el banco la
    frena.
- **En los controles de ventas,** salta en los 3 vishing y en ninguna de las 3 legítimas.

**4. El motivo de C funciona.** Dio 22/22 con JSON válido y 21/22 con evidencia de OTRA.
- Se leyeron a mano los 6 que la búsqueda por palabras marcó como «pedido antes de que ocurra»:
  - los 5 de estafas nombran un pedido que ya está en curso. La referencia lo marca más tarde, o como dato personal
    (la foto del DNI);
  - el único mal es el de `ENT-L-BANCO-006`, que dice «te están pidiendo un código» cuando nadie lo pidió.
- El de `ENT-L-BANCO-002` dice «un número que te dictan», cuando es el del dorso de la tarjeta.

**5. Latencia en T4:**
- C sin alerta: 239 ms (p50), con 14 tokens.
- C con campo: 288 ms, con 24.
- El motivo: unos 800 ms, una vez por llamada.

## Lo que queda abierto

- **La base no pide motivo nunca.** No tiene alerta fuerte, y el primer aviso muestra un texto fijo. Hay que decidir si
  el producto queda así o si vuelve el motivo en el primer aviso. En la etapa 2 se midieron 24 motivos de
  `c-json-corte`, pero solo los de la alerta escrita.
- **«Cortado tras el riesgo» nunca corrió como tal:** se leyó de `c-json-corte`. Para la reserva hace falta una
  configuración real, o correr `c-json-corte` y leer solo el riesgo.
- **El escalón del 0,3:** cualquier comparación con «riesgo ≥ 0,3» depende de cuántas veces el modelo escribe 0,3 en
  vez de 0,2. Conviene tenerlo en cuenta al leer la reserva y al escribir el informe.
- **La alerta fuerte como segundo nivel** (precaución con riesgo y alerta con `pedido_critico`) queda como hipótesis.
  Para probarla hace falta una regla nueva, escrita antes, y casos que no se hayan mirado.
