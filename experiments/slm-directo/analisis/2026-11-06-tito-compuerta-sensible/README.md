# Tito como compuerta: ¿las falsas alarmas que «evita» son aciertos?

**Fecha:** 2026-11-06. **Hecho por:** Mateo Antenucci, con análisis de Claude Opus 5.5. **Issues:** [#51](https://github.com/Corchets/bitacora_tesis/issues/51) y [#143](https://github.com/Corchets/bitacora_tesis/issues/143).
**Hallazgos que salen de acá:** [H08](../../../../docs/hallazgos/H08-tito-evita-falsas-alarmas-por-punto-ciego.md) y [H09](../../../../docs/hallazgos/H09-tito-clasificador-en-vez-de-compuerta.md).

> **Estado: propuesta sin discutir.** Diagnóstico sobre los 150 casos de desarrollo, ya vistos, con referencias sin
> revisión humana. No toca la reserva y no decide [#51](https://github.com/Corchets/bitacora_tesis/issues/51).

## Pregunta y criterio

Con Tito las falsas alarmas bajaban: de 19 a 14 con v1 y de 17 a 13 con v4. ¿Es porque Tito reconoce que esas llamadas no tienen riesgo, o porque no vio lo que el SLM sí vio?

El criterio es el de Mateo para una compuerta. Tito no decide: solo despierta al SLM. Tiene que despertarlo ante cualquier cosa posiblemente sospechosa (un código de WhatsApp, una clave, un dato personal) y solo puede dejar sin consulta lo que no tiene nada sensible. Una falsa alarma que desaparece porque Tito no vio la línea sensible no es un mérito.

## Datos y definiciones

- **Corridas** (todas en `laboratorio-main`, lista exacta en [cargar.py](cargar.py)):
  - v1 y v4, cada uno solo y con Tito sin indicio;
  - v4 con Tito viejo 2.0;
  - reglas v1;
  - la [matriz #101](../../corridas/2026-10-30_112956_101_informe_101.md);
  - las seis corridas por token de #143 (por ahora solo en la rama `exp/143-puntaje-token`).
- **Activación de Tito:** sale de la corrida `2026-11-04_tanda-roles-tito-sin-indicio/d`, que sigue después del aviso. Es la misma con v1 y con v4, y el script lo comprueba.
- **Línea sensible:** la primera que la referencia marca como `mencion` o `pedido`, o `T_R`. Es una aproximación: las marcas no tienen revisión humana y no cubren todo lo sensible. Por ejemplo, `MEDICO-004` pide la fecha de nacimiento sin marca.
- **Veredicto de cada falsa alarma que desaparece:**
  - **no filtró:** Tito ya había activado en la línea del aviso. El SLM cambió de respuesta, pero no por la compuerta.
  - **punto ciego:** la compuerta le tapó al SLM una línea sensible.
  - **filtrado honesto:** antes del aviso no había nada sensible.

## Resultados

### 1. Lectura JSON en los 150 casos: 7 de 7 son punto ciego

| Caso | Aviso sin Tito | Lo sensible que Tito no vio | Puntaje | Tito activa |
|---|---|---|---:|---|
| `LG-WA-CONSULTA-01-e01` | L1 (v1), L2 (v4) | «Me llegó por SMS un código para activar WhatsApp» | 0,234 | nunca |
| `LAB-anses-canal-oficial` | L1 | «me ofrecieron un bono si les doy datos del organismo» | 0,009 | L5, con «gracias» (0,792) |
| `LAB-no-bajes-nada` | L1 (v4) | «me llamaron para que baje un programa y les muestre el celular» | 0,000 | L4, con «bien» (0,961) |
| `TR-03-negacion-y-consejo` | L5 | la clave del banco, el código por mensaje, el PIN, transferir | 0,000–0,006 | nunca |
| `LG-ORG-TURNO-01-e01` | L4 (v1) | «una foto con el documento en la mano» | 0,000 | nunca |
| `LG-SUPPORT-INFO-01-e01` | L4 (v1) | «no me digas ni tu usuario ni tu contraseña» | 0,035 | L7 |
| `CV2-D-L-BANCO-009` | L8 (v4) | «marqué el PIN» | 0,006 | nunca |

Con v4, Tito además suma una falsa alarma: `CV2-D-L-BANCO-006`, en la línea 6. En las siete, la persona protegida inició la llamada o hablaba con alguien de confianza. En corpus_v2, que se parece a la reserva, Tito no cambia las falsas alarmas: 4 = 4 con v1 y 6 = 6 con v4.

### 2. Lectura por token (#143): 2 son punto ciego, 1 es dudosa y 2 están bien filtradas

La compuerta simulada de #143 saca cinco legítimas más. Veredicto a mano, mirando el texto:

| Caso | Aviso sin Tito | Línea | Puntaje | Veredicto |
|---|---|---|---:|---|
| `CV2-D-L-BANCO-003` | L6 | «¿me confirmás tu nombre completo y el mes de vencimiento de esa tarjeta?» | 0,140 | Punto ciego |
| `CV2-D-L-SOPORTE-002` | L6 | «¿me confirmás el nombre del consultorio y las primeras letras del correo registrado?» | 0,003 | Punto ciego |
| `CV2-D-L-MEDICO-004` | L4 | «me confirmás tu fecha de nacimiento», sin marca en la referencia | 0,144 | Dudoso |
| `CV2-D-L-MEDICO-001` | L2 | «¿Me decís tu nombre y la fecha del turno?» | 0,000 | Bien filtrada |
| `CV2-D-L-MEDICO-005` | L3 | nombre y hora del turno; solo es falsa alarma con umbral 0,07 | — | Bien filtrada |

Para ver cuánto queda de la ventaja de Tito en #143, se simuló un Tito sin punto ciego: el real, más una activación en la primera mención o pedido marcados. Es un oráculo, porque usa la referencia, así que da un techo. El cuadro muestra el mejor punto con 7 falsas alarmas o menos en corpus_v2, con estafas sobre 46 y avisos antes del pedido.

| Corrida | SLM solo | Tito → SLM | Tito sin punto ciego → SLM |
|---|---|---|---|
| A1 v4 | 26, 4 antes | 26, 8 antes | 27, 4 antes |
| A1 v4 rep | 26, 4 antes | 28, 9 antes | 27, 7 antes |
| A2 v4 | 25, 2 antes | 29, 7 antes | 29, 4 antes |
| A2 v4 rep | 24, 2 antes | 28, 7 antes | 27, 4 antes |
| A1 tarea | 27, 9 antes | 26, 8 antes | 27, 8 antes |
| A1 tarea rep | 27, 14 antes | 26, 12 antes | 27, 12 antes |

La ventaja que sobrevive aparece solo en A2 v4 y sale de dos llamadas médicas, `MEDICO-001` y `MEDICO-004`. Además es con la lectura por token, que #143 no adoptó.

### 3. Cobertura de la compuerta y ahorro de consultas

¿Está despierto el SLM en la primera línea sensible? Recorriendo las llamadas completas (2.773 líneas):

| Compuerta | Estafas | Legítimas | Líneas sin consultar |
|---|---:|---:|---:|
| Tito viejo | 62/64 | 14/43 | 1.139 (41 %) |
| Tito viejo 2.0 | 62/64 | 14/43 | 1.138 (41 %) |
| Reglas v1 | 52/64 | 26/43 | 1.203 (43 %) |
| Tito o reglas v1, sin ajustar nada | 63/64 | 30/43 | 642 (23 %) |
| Tito sin punto ciego (oráculo) | 64/64 | 43/43 | 900 (32 %) |

- De las 1.139 líneas que Tito deja sin consultar, 239 están en o después de la primera línea sensible; 225 de ellas, en legítimas.
- Las reglas v1 se escribieron mirando los 53 casos cortos. En corpus_v2, Tito o reglas cubre 35/36 y 17/23 y deja sin consultar el 24 %.
- Las estafas que paga el punto ciego:
  - `CV2-D-V-PREMIO-001` se pierde: «El DNI completo y una foto del frente» saca 0,024.
  - El aviso de `CV2-D-V-BANCO-007` se atrasa de L6 a L16 con v1: «quieren cambiar el teléfono que recibe los avisos de acceso» saca 0,128.

### 4. Matriz #101: la ventaja de E2B con Tito tampoco es filtrado

E2B dio 10/10 · 1/10 solo y 10/10 · 0/10 con Tito, y eso sostuvo el [ADR 0001](../../../../docs/ingenieria/adr/0001-parakeet-filtro-y-gemma4-e2b-con-tito-viejo.md). Pero en esa legítima (`CV2-D-L-BANCO-001`, aviso en L12) Tito activó en la línea 1: el SLM leyó la llamada entera en las dos condiciones.

En los 10 modelos, las falsas alarmas bajan de 48 a 27: Tito saca 24 y suma 3.

- **13 son filtrado honesto.** 9 son de `gemma:2b` y `gemma3:1b`, que avisan en llamadas sin nada sensible, casi siempre en las dos primeras líneas.
- **6 son punto ciego.**
- **En 5, Tito ya había activado.**

En #101, E2B solo avisó antes del pedido en 4 de 10 estafas, contra 1 con Tito. #101 prueba la activación y el indicio juntos, así que no separa cuál de los dos atrasó el aviso.

### 5. Por qué: Tito se entrenó para otra cosa

El [banco de entrenamiento](https://github.com/Corchets/bitacora_tesis/tree/archivo/tito-banco/experiments/laboratorio/entrenamiento_tito) tiene 5.520 textos sintéticos.

| | Estafas (2.620) | Legítimas (2.900) |
|---|---:|---:|
| Largo | 18 a 39 palabras (mediana 27) | 10 a 38 (mediana 24) |
| Mencionan clave, código, contraseña, PIN, token, CVV, DNI, documento o tarjeta | 1.180 | 319 |
| La víctima cuenta lo que le pasó («me llamaron», «me llegó»…) | 0 | 42 |
| Contienen «gracias» | 0 | 115 |

- **El objetivo era clasificar estafa o legítima.** Las legítimas incluyen a propósito usos inocentes de códigos y claves, así que Tito aprende a no reaccionar a esas palabras solas. Una compuerta necesita lo contrario.
- **Los textos no se parecen a una línea de llamada.** Son monólogos del estafador con presentación y pedido juntos. En una llamada, la maniobra se reparte en varias líneas, la mitad las dice la persona protegida y muchas son cortas. Por eso Tito reacciona sobre todo a «te llamo del banco» (33 de 56 presentaciones en estafas pasan de 0,5) y no al contenido sensible.
- **«bien», «gracias» y «corta» no vienen del banco.** De 38 líneas de una o dos palabras, solo esas tres pasan de 0,5: palabras sueltas sin puntuación. «Perfecto, gracias.» saca 0,000. La hipótesis es que con una sola palabra el promedio enmascarado queda dominado por los tokens especiales de inicio y fin, y la regresión nunca vio nada de menos de 10 palabras. **Sin verificar:** hace falta puntuar «gracias», «gracias.» y «Perfecto, gracias.» con el modelo.

## Límites

- Tito deja de puntuar cuando activa: no sabemos qué puntaje habrían sacado las líneas posteriores.
- La línea sensible depende de marcas sin revisión humana; el oráculo es un techo, no una compuerta posible.
- Todo es material de desarrollo ya visto. No dice nada del rendimiento final.

## Reproducir

Desde esta carpeta, con Python 3 y sin dependencias:

```bash
python3 revisar.py                          # tablas 1, 3, 4 y 5, con controles de los números
python3 revisar.py LG-WA-CONSULTA-01-e01    # detalle línea por línea de uno o más casos
python3 compuerta_honesta_143.py            # tabla 2; necesita la rama exp/143-puntaje-token
```

`revisar.py` termina en error si los números principales de las tablas 1, 3, 4 y 5 dejan de coincidir con las corridas. Lee solo los 150 casos de desarrollo y nunca la reserva.
