# #143, prueba de sensibilidad: análisis

> **Estado: propuesta sin discutir.** Desarrollo; no se tocó la reserva, las legítimas de test ni #144. Mateo la corrió
> en Colab T4 el 2026-11-10, y se analizó el mismo día.

**Resultado de la regla escrita antes de correr: queda `c-premisa`.** Las tres variantes pasan. Según la regla se elige
la que más suma en estafas y a tiempo juntas, y esa es `c-premisa` (+3 y +4). `c-ancla` y `c-sin-freno` suman +5 cada
una. Ninguna cae en «decide Mateo».

La salida completa está en [`analisis-salida.md`](analisis-salida.md).

## Verificación de los ZIP

- Cada ZIP se descomprimió en un directorio vacío nuevo. Los nueve parciales (la humo y las ocho corridas) coinciden
  archivo por archivo con su carpeta en el final.
- `commit.txt`, los `TERMINADA.txt` y los ocho manifiestos dan `ca4fab0`, el commit del tag `colab/143-sensibilidad`,
  sin cambios sin commitear.
- El sha256 de `colab/probar_sensibilidad.py` en el tag coincide con `script-sha256.txt` (`4cb0d9f6…`).
- El digest coincide en los manifiestos y en `digest.txt` (`b37049369adf…`), con Ollama 0.40.14 en una Tesla T4.
- No hay casos de la reserva ni de test. Cada corrida sobre los 244 tardó 9,7 minutos, y cada repetición, 5,6 a 5,7.

## La regla, paso a paso

**Humo de formato:** pasan las cuatro. Todas leen el riesgo, con su coma, en 48/48 líneas.

**Control:** las ocho corridas sin problemas, y 0 líneas inválidas. En las de los 244 consultaron 2.177 líneas de OTRA,
y en las repeticiones, 1.313. Las líneas de PROTEGIDA no consultaron, y el motivo se pidió solo en el aviso.

**Cifras (alcance-140):**

| corrida | estafas | antes del pedido | a tiempo | antes del cumplimiento | FA cotidianas | FA dudosas | FA |
|---|---|---|---|---|---|---|---|
| base | 37/46 | 15/36 | 25/36 | 12/15 | 1/29 | 25/65 | 26/94 |
| `c-ancla` | 39/46 | 15/36 | **28/36** | 13/15 | 3/29 | 24/65 | 27/94 |
| `c-premisa` | **40/46** | **19/36** | **29/36** | 12/15 | 2/29 | 24/65 | 26/94 |
| `c-sin-freno` | **40/46** | **20/36** | 27/36 | 12/15 | 3/29 | 33/65 | 36/94 |
| base, repetición | 36/46 | 14/36 | 25/36 | 12/15 | 1/29 | 25/65 | 26/94 |
| `c-ancla`, repetición | 40/46 | 18/36 | 29/36 | 14/15 | 3/29 | 24/65 | 27/94 |
| `c-premisa`, repetición | 39/46 | 18/36 | 28/36 | 12/15 | 2/29 | 26/65 | 28/94 |
| `c-sin-freno`, repetición | 41/46 | 20/36 | 28/36 | 13/15 | 3/29 | 35/65 | 38/94 |

En negrita, lo que gana 3 o más contra la base.

**Veredicto por variante:**
- **`c-ancla`: pasa.** Suma +3 a tiempo, y la repetición lo sostiene (+4). Llega justo al tope de FA en cotidianas
  (+2).
- **`c-premisa`: pasa.** Suma +3 estafas, +4 antes del pedido y +4 a tiempo. La repetición da +3, +4 y +3. Suma 1 FA en
  cotidianas y ninguna en total.
- **`c-sin-freno`: pasa.** Suma +3 estafas y +5 antes del pedido, y la repetición da +5 y +6. Llega justo al tope en
  cotidianas (+2), y en las dudosas suma +8 en la corrida y +10 en la repetición. Por eso no cae en «decide Mateo»,
  que es con más de 10.

**Elección:** `c-premisa` (+7 entre estafas y a tiempo), contra +5 de `c-ancla` y +5 de `c-sin-freno`.

## Lectura, después de ver los resultados (no decide)

**La base es estable:** 37/46 acá, 36/46 en la repetición y 36/46 en la humo. La variación entre corridas es de ±1, y
las ganancias de `c-premisa` (+3 a +4, sostenidas en la repetición) están por encima de eso, aunque no por mucho.

**Las tres estafas que recupera `c-premisa` avisan por la razón correcta.** Ninguno de sus motivos se apoya en el
número desconocido:

| caso | aviso | T_R | motivo |
|---|---|---|---|
| CV2-D-V-FAMILIAR-004 | L10 | 22 | «el contexto de una urgencia económica y la necesidad de una transferencia o acción inmediata es una táctica común en estafas» |
| CV2-D-V-FAMILIAR-006 | L14 | 22 | «Tu prima te pide dinero de forma urgente para un gasto inesperado, lo cual es una táctica común de estafa.» |
| CV2-D-V-SOPORTE-005 | L14 | 16 | «Te están pidiendo que salgas de tu sesión y accedas a una recuperación de cuenta, lo cual es una táctica común para robar tus credenciales.» |

Las tres avisan antes del pedido. `c-premisa` no pierde ninguna de las estafas que la base avisa. En la repetición
recupera cuatro (las mismas tres y PREMIO-005) y pierde una sin pedido (PREMIO-006).

**Siguen sin aviso seis estafas.** Cinco tienen pedido explícito:
- el código de WhatsApp (WHATSAPP-003 y 006);
- la clave (SOPORTE-003);
- la plata para un familiar (FAMILIAR-005);
- los datos para un premio (PREMIO-003).

La sexta, PREMIO-006, no tiene pedido. Ninguna variante avisa WHATSAPP-003, SOPORTE-003 ni PREMIO-003. Es el punto ciego
que queda, y conviene nombrarlo en la tesis.

**Las FA:** `c-premisa` suma 4 FA nuevas y deja 4 de la base. El total queda igual, 26/94.
- Las que deja son las de mención o pedido razonable de la base, como LEG2-ST-05, uno de los tres motivos engañosos de
  la humo.
- **ENT-L-ENCUESTA-003 (cotidiana):** OTRA nombra a PROTEGIDA antes de que se presente, y después lo explica con un
  panel de encuestas. Avisan las tres variantes. Es una cotidiana en el borde. Su motivo es uno de los
  dos (sobre 26 FA) que nombran el número desconocido. Por la premisa del alcance, ese motivo vale para todas las
  llamadas.
- **ENT-L-SELECCION-002 (mención):** OTRA le dice «ese código no me lo pases ni a mí ni a nadie», y el motivo dice lo
  contrario («te están pidiendo que les des un código»). **Es un motivo engañoso**, como los tres de la humo.
- **ENT-L-ENCUESTA-006 y ENT-L-VENTAS-003:** son una mención de una tarjeta clonada y una oferta de seguro. Los motivos
  son genéricos.

**Las tres variantes avisan sobre todo con un 0,3 exacto.** Igual que la base (56/63), en `c-premisa` el 0,3 exacto da
57 de los 66 avisos, y las tres estafas recuperadas también avisan con 0,3. La ganancia viene de pasar líneas de 0,2 a
0,3, no de subir el riesgo de golpe. El escalón sigue siendo frágil, como ya se sabía.

**Lo que dice cada hipótesis:**
- *`c-ancla`:* el ancla de 0,7 no ancló la punta alta. En la humo, los riesgos ≥ 0,6 bajan de 13 a 3. Con u = 0,4 avisa
  23 estafas, contra 15 de la base. El cambio movió el medio, no la punta.
- *`c-premisa`:* tenerlo en cuenta, sin números, alcanza para pasar de 0,2 a 0,3 en las estafas de familiar y de
  recuperación de cuenta. No mueve las FA totales.
- *`c-sin-freno`:* el párrafo que frena sí le cuesta algo de detección al prompt (+3 estafas y +5 antes del pedido al
  sacarlo). Pero sacarlo suma 8 a 10 FA en las dudosas. La duda de Mateo tenía base. La regla elige `c-premisa`, que
  gana parecido sin ese costo.

**No se probó** combinar `c-premisa` y `c-sin-freno`. Sería otra prueba con regla nueva. Cada prueba más sobre
desarrollo agranda el riesgo de sobreajuste. Como es una búsqueda a mano, el número honesto lo dan la reserva y #144.

## Qué sigue

Según la regla, `c-premisa-corte-riesgo` reemplaza a `c-json-corte-riesgo` en la evaluación final, con todo lo demás
igual: corte tras el riesgo, «≥ 0,3», el motivo de C en el primer aviso y solo OTRA. El panel VoIP también tendría que
pasar a usarla por defecto.
