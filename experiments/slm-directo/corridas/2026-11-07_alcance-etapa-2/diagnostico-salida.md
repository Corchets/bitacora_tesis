# #143, etapa 2: diagnóstico fuera del criterio (escrito después de ver los resultados)

v4 con «riesgo ≥ 0.4 o alerta» (su regla adoptada) y C con «riesgo ≥ 0.3 o alerta» (la que eligió analizar.py con FA ≤ 42). Primera corrida de cada una, salvo donde se dice.

## 1. Estafas: de dónde sale la diferencia

Por tipo del primer pedido crítico de la referencia. «antes / en / después» es la línea del primer aviso contra la del pedido (T_R).

| pedido | estafas | v4 avisa | C avisa | v4 antes / en / después | C antes / en / después |
|---|---|---|---|---|---|
| sin pedido | 10 | 1 | 9 | — | — |
| REQUEST_AUTH_CODE | 10 | 9 | 7 | 3 / 5 / 1 | 5 / 2 / 0 |
| REQUEST_SECRET | 7 | 4 | 5 | 1 / 3 / 0 | 4 / 0 / 1 |
| REQUEST_TRANSFER | 9 | 6 | 6 | 3 / 3 / 0 | 3 / 3 / 0 |
| REQUEST_PERSONAL_DATA | 6 | 4 | 5 | 0 / 3 / 1 | 3 / 2 / 0 |
| REQUEST_SECURITY_ACTION | 2 | 2 | 2 | 2 / 0 / 0 | 2 / 0 / 0 |
| REQUEST_REMOTE_ACCESS | 2 | 2 | 2 | 1 / 1 / 0 | 0 / 1 / 1 |

Estafas con pedido (36): momento del aviso de v4 (filas) contra el de C (columnas).

|  | C antes | C en | C después | C – | total |
|---|---|---|---|---|---|
| v4 antes | 9 | 1 | 0 | 0 | 10 |
| v4 en | 4 | 7 | 2 | 2 | 15 |
| v4 después | 1 | 0 | 0 | 1 | 2 |
| v4 – | 3 | 0 | 0 | 6 | 9 |

- v4: adelanto T_R − T_A en sus avisos a tiempo, mediana 0 líneas (n = 25; 3 o más líneas antes: 9).
- C: adelanto T_R − T_A en sus avisos a tiempo, mediana 4 líneas (n = 25; 3 o más líneas antes: 13).

Pares discordantes en los mismos casos (McNemar exacto, dos colas; solo para mirar: el umbral de C se eligió sobre estos mismos casos, así que el p es optimista):

| cifra | solo C | solo v4 | p |
|---|---|---|---|
| estafas avisadas (/46) | 11 | 3 | 0.057 |
| avisos antes del pedido (/36) | 8 | 1 | 0.039 |
| detección útil, antes o en el pedido (/36) | 4 | 4 | 1.000 |
| FA (/94) | 7 | 22 | 0.008 |

Estafas en que v4 y C difieren (L = línea del primer aviso; – sin aviso):

| estafa | pedido | T_R | líneas | v4 | C | C (repetición) |
|---|---|---|---|---|---|---|
| BANCO-001 | REQUEST_AUTH_CODE | 32 | 38 | L32 | L2 | L2 |
| BANCO-009 | REQUEST_SECRET | 13 | 20 | L13 | L4 | L4 |
| BANCO-012 | sin pedido | – | 21 | – | L1 | L1 |
| ORGANISMO_PREVISIONAL-001 | REQUEST_PERSONAL_DATA | 12 | 27 | L12 | L10 | L10 |
| ORGANISMO_PREVISIONAL-003 | REQUEST_PERSONAL_DATA | 11 | 20 | L13 | L1 | L1 |
| ORGANISMO_PREVISIONAL-004 | REQUEST_PERSONAL_DATA | 14 | 21 | – | L5 | L5 |
| ORGANISMO_PREVISIONAL-005 | sin pedido | – | 23 | – | L2 | L2 |
| ORGANISMO_PREVISIONAL-006 | sin pedido | – | 22 | – | L1 | L1 |
| PREMIO-004 | REQUEST_SECRET | 14 | 21 | L14 | L12 | L12 |
| PREMIO-005 | sin pedido | – | 23 | – | L9 | L9 |
| SOPORTE-001 | REQUEST_SECRET | 14 | 21 | L14 | L15 | L15 |
| SOPORTE-002 | REQUEST_REMOTE_ACCESS | 13 | 24 | L10 | L13 | L13 |
| SOPORTE-004 | REQUEST_REMOTE_ACCESS | 14 | 30 | L14 | L18 | L18 |
| SOPORTE-006 | REQUEST_SECRET | 15 | 20 | – | L14 | L14 |
| SOPORTE-007 | sin pedido | – | 21 | – | L2 | L2 |
| SOPORTE-008 | sin pedido | – | 22 | – | L1 | L1 |
| WHATSAPP-003 | REQUEST_AUTH_CODE | 12 | 21 | L12 | – | – |
| WHATSAPP-004 | REQUEST_AUTH_CODE | 13 | 21 | – | L1 | L1 |
| WHATSAPP-005 | REQUEST_AUTH_CODE | 14 | 21 | L14 | – | – |
| WHATSAPP-006 | REQUEST_AUTH_CODE | 25 | 36 | L28 | – | – |
| WHATSAPP-007 | sin pedido | – | 21 | – | L3 | L3 |
| WHATSAPP-008 | sin pedido | – | 20 | – | L6 | L6 |

## 2. Legítimas entrantes: dónde baja la FA

De las 94: FA con las dos 20; solo v4 22; solo C 7; ninguna 45.

| lote | FA v4 | FA C | solo v4 | solo C |
|---|---|---|---|---|
| LEG (21) | 3 | 5 | 0 | 2 |
| LEG2 (28) | 15 | 8 | 9 | 2 |
| ENT-L (42) | 23 | 14 | 12 | 3 |
| selección (3) | 1 | 0 | 1 | 0 |

Cuándo cae la FA, según los eventos de la referencia de cada legítima:

| la FA cae… | v4 | C |
|---|---|---|
| antes de cualquier pedido | 4 | 14 |
| en la línea de un pedido de datos personales | 35 | 6 |
| después de un pedido de datos personales | 3 | 7 |
| después de otro pedido | 0 | 0 |
| total | 42 | 27 |

Legítimas con algún pedido de datos personales en la referencia: 64/94. FA en ellas: v4 39, C 21; en las otras 30: v4 3, C 6.

## 3. Cómo usa cada prompt el riesgo escrito (dentro del alcance, todas las líneas)

| prompt | líneas de | n | 0 | 0.1 | 0.2 | 0.3 | 0.4 | 0.5 | 0.6 | 0.7 | 0.8 | 0.9 | 1 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| v4 | estafas | 1069 | 2 | 23 | 23 | 26 | 1 | 10 | 5 | 3 | 5 | 1 | · |
| v4 | legítimas | 1552 | 2 | 43 | 23 | 14 | 0 | 9 | 1 | 1 | 6 | 2 | · |
| C | estafas | 1069 | 1 | 17 | 37 | 33 | 1 | 1 | 7 | 1 | 0 | 1 | · |
| C | legítimas | 1552 | 2 | 55 | 30 | 8 | 0 | 0 | 2 | 2 | 1 | · | · |
| v4-premisa | estafas | 1069 | 2 | 23 | 28 | 24 | 0 | 11 | 3 | 2 | 5 | 1 | · |
| v4-premisa | legítimas | 1552 | 2 | 44 | 24 | 13 | 0 | 8 | 1 | 1 | 6 | 2 | · |

Cada celda: % de líneas con ese riesgo escrito, al decimal de abajo (0,85 cuenta como 0,8; · = ninguna).

| prompt | líneas con riesgo ≥ 0,4 | de esas, con alerta escrita | líneas con alerta escrita | de esas, con riesgo < 0,4 |
|---|---|---|---|---|
| v4 | 567 | 497 | 507 | 10 |
| C | 199 | 110 | 110 | 0 |
| v4-premisa | 507 | 441 | 468 | 27 |

Máximo riesgo escrito por llamada (cuántas llamadas llegan a cada valor como máximo):

| prompt | llamadas | 0 | 0.1 | 0.2 | 0.3 | 0.4 | 0.5 | 0.6 | 0.7 | 0.8 | 0.9 | 1 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| v4 | estafas | · | · | 7 | 13 | · | 5 | 4 | 2 | 12 | 3 | · |
| v4 | legítimas | · | 17 | 25 | 12 | · | 14 | 5 | 1 | 15 | 5 | · |
| C | estafas | · | · | 10 | 21 | · | 1 | 8 | 1 | 4 | 1 | · |
| C | legítimas | · | 22 | 45 | 18 | · | · | 3 | 2 | 4 | · | · |
| v4-premisa | estafas | · | · | 8 | 13 | · | 5 | 1 | 3 | 14 | 2 | · |
| v4-premisa | legítimas | · | 19 | 29 | 8 | · | 14 | 4 | 2 | 13 | 5 | · |

## 4. Lo que le queda a C con «riesgo ≥ 0.3 o alerta»

### En qué línea cae el primer aviso

| prompt | avisos a | L1–2 | L3–5 | L6–10 | L11+ | total |
|---|---|---|---|---|---|---|
| v4 | estafas | 1 | 2 | 10 | 15 | 28 |
| v4 | legítimas (FA) | 1 | 21 | 15 | 5 | 42 |
| C | estafas | 12 | 6 | 9 | 9 | 36 |
| C | legítimas (FA) | 9 | 8 | 6 | 4 | 27 |

### Estafas sin aviso o con aviso después del pedido

| estafa | pedido | T_R | líneas | C avisa | riesgo máx. de C | riesgo de C en T_R | v4 avisa |
|---|---|---|---|---|---|---|---|
| FAMILIAR-004 | REQUEST_TRANSFER | 22 | 29 | – | 0.2 | 0.2 | – |
| FAMILIAR-005 | REQUEST_TRANSFER | 20 | 21 | – | 0.2 | 0.2 | – |
| FAMILIAR-006 | REQUEST_TRANSFER | 22 | 23 | – | 0.2 | 0.2 | – |
| PREMIO-003 | REQUEST_PERSONAL_DATA | 13 | 28 | – | 0.2 | 0.1 | – |
| PREMIO-006 | sin pedido | – | 22 | – | 0.2 | – | – |
| SOPORTE-001 | REQUEST_SECRET | 14 | 21 | L15 | 0.3 | 0.2 | L14 |
| SOPORTE-003 | REQUEST_SECRET | 11 | 21 | – | 0.2 | 0.1 | – |
| SOPORTE-004 | REQUEST_REMOTE_ACCESS | 14 | 30 | L18 | 0.3 | 0.2 | L14 |
| SOPORTE-005 | REQUEST_SECRET | 16 | 21 | – | 0.2 | 0.2 | – |
| WHATSAPP-003 | REQUEST_AUTH_CODE | 12 | 21 | – | 0.2 | 0.2 | L12 |
| WHATSAPP-005 | REQUEST_AUTH_CODE | 14 | 21 | – | 0.2 | 0.2 | L14 |
| WHATSAPP-006 | REQUEST_AUTH_CODE | 25 | 36 | – | 0.2 | 0.1 | L28 |

### Las FA de C, con la última línea de OTRA hasta el aviso

| legítima | lote | aviso / líneas | riesgo | alerta escrita | v4 | eventos hasta el aviso | última línea de OTRA |
|---|---|---|---|---|---|---|---|
| ENT-L-BANCO-001 | ENT-L | L1/24 | 0.3 | no | L3 | — | L1: buenas tardes te llamo del área de de prevención fraudes del banco me llamo veronica |
| ENT-L-BANCO-002 | ENT-L | L2/23 | 0.3 | no | L4 | — | L2: Hola, buen día. Te llamo del banco, del sector de seguridad. |
| ENT-L-BANCO-004 | ENT-L | L5/35 | 0.3 | no | L4 | L4 pedido DATOS | L4: valeria valeria para validar su identidad me dice su dni |
| ENT-L-BANCO-005 | ENT-L | L1/22 | 0.3 | no | L3 | — | L1: Buen día, le hablo de prevención de fraudes del banco. |
| ENT-L-BANCO-006 | ENT-L | L2/21 | 0.3 | no | L4 | — | L2: Hola, buenas tardes. Te hablo del banco, por tu app. |
| ENT-L-DELIVERY-004 | ENT-L | L8/21 | 0.3 | no | L8 | L8 pedido DATOS | L8: ¿Me confirmás tu número de documento para dejarlo asentado a tu nombre? |
| ENT-L-ENCUESTA-006 | ENT-L | L3/21 | 0.3 | no | – | — | L2: hola buenas tardes te habla martina del banco del área de experiencia de clientes |
| ENT-L-SOPORTE-001 | ENT-L | L3/26 | 0.3 | no | L3 | L3 pedido DATOS | L3: para validar que hablo con la titular me confirmás tu dni |
| ENT-L-SOPORTE-003 | ENT-L | L1/23 | 0.3 | no | L18 | — | L1: Hola, ¿Tobías? Te hablo de TecnoFix, el local de la calle Muñecas. Dejaste una notebook la semana pasada. |
| ENT-L-SOPORTE-005 | ENT-L | L11/32 | 0.3 | no | L5 | L5 pedido DATOS | L11: Abajo hay un botón que dice Asistencia remota. Descargá ese programa, solo desde ahí. |
| ENT-L-VENTAS-001 | ENT-L | L10/27 | 0.3 | no | L13 | — | L9: el de diez no entra en la promo pero dejame ver te lo puedo dejar mismo precio precio por cuatro meses |
| ENT-L-VENTAS-002 | ENT-L | L16/23 | 0.3 | no | L14 | L8 pedido DATOS, L10 pedido DATOS, L14 pedido DATOS | L16: te entiendo igual sin el dni no puedo cargar la solicitud porque la verificación de identidad es obligatoria |
| ENT-L-VENTAS-003 | ENT-L | L18/29 | 0.3 | no | – | L5 pedido DATOS | L17: hay una versión básica de ocho mil que cubre incendio y daños por agua sin robo |
| ENT-L-VENTAS-009 | ENT-L | L21/32 | 0.3 | no | – | L3 pedido DATOS, L17 pedido PLATA | L21: La seña se devuelve si no se aprueba el crédito. Si te arrepentís por otro motivo, se pierde. |
| LEG-BA-01 | LEG | L5/13 | 0.3 | no | L5 | L3 mención | L5: Detectamos un intento de compra con tu tarjeta de crédito terminada en cuatro cuatro uno siete, por ciento oc… |
| LEG-BA-02 | LEG | L3/9 | 0.5 | no | L3 | — | L3: Carla, te llamo de Banco Andino, de seguridad. Registramos dos inicios de sesión en tu home banking desde un … |
| LEG-BA-03 | LEG | L3/9 | 0.3 | no | L3 | L3 mención | L3: Juan Pablo, te llamo de Banco Andino, de prevención de fraudes. Tenemos una compra en el exterior con tu tarj… |
| LEG-CC-03 | LEG | L8/12 | 0.3 | no | – | L7 mención | L7: No, está perfecto que preguntes. Hacé una cosa: llamá al cero ochocientos que figura en tu factura, pedí por … |
| LEG-ST-03 | LEG | L1/8 | 0.3 | no | – | — | L1: Hola, ¿Matías? Te hablo de TecnoFix, el local de la calle Muñecas. Dejaste una notebook la semana pasada. |
| LEG2-BA-01 | LEG2 | L4/12 | 0.7 | sí | L4 | L4 pedido DATOS | L4: Gonzalo, necesito validar tu identidad antes de darte información. ¿Me decís tu DNI y tu fecha de nacimiento? |
| LEG2-BA-02 | LEG2 | L4/10 | 0.3 | no | L4 | L4 pedido DATOS | L4: Carla, registramos dos ingresos a tu homebanking desde un dispositivo nuevo esta madrugada. Antes de seguir, … |
| LEG2-BA-03 | LEG2 | L2/12 | 0.3 | no | L2 | L2 pedido DATOS | L2: Buenas tardes, te habla Lorena, de prevención de fraudes de Banco Andino. ¿Me decís tu nombre completo, por f… |
| LEG2-BA-05 | LEG2 | L6/12 | 0.3 | no | L4 | L4 pedido DATOS | L6: Gracias. Tu tarjeta de débito se usó ayer a la noche en un cajero de Córdoba. ¿Estuviste allá? |
| LEG2-CC-05 | LEG2 | L6/12 | 0.3 | no | L6 | L6 pedido DATOS | L6: Por eso te llamaba. Te faltó validar la identidad. ¿Me confirmás tu DNI? |
| LEG2-CC-06 | LEG2 | L9/12 | 0.3 | no | – | L6 mención, L8 pedido DATOS | L8: Sí, va un técnico. ¿Sigue siendo en Las Piedras al dos mil cien? |
| LEG2-ST-03 | LEG2 | L2/10 | 0.3 | no | L4 | — | L2: Hola, ¿Matías? Te hablo de TecnoFix, el local de la calle Muñecas. Dejaste una notebook la semana pasada. |
| LEG2-ST-05 | LEG2 | L2/9 | 0.3 | no | – | — | L2: Hola, buenas tardes, te habla Julieta, de soporte de Tiendita Online. Te llamo por el ticket que abriste porq… |

### Las FA que C saca y v4 tiene (muestra de las primeras 12), con la línea que dispara a v4

| legítima | v4 avisa | eventos hasta el aviso | riesgo máx. de C | última línea de OTRA |
|---|---|---|---|---|
| ENT-L-BANCO-003 | L5 | L3 pedido DATOS, L5 pedido DATOS | 0.2 | L5: Gracias, señor Sosa. ¿Me confirma los últimos tres números de su documento? |
| ENT-L-DELIVERY-001 | L15 | L5 pedido DATOS | 0.2 | L15: Sí, me firmás en el celular y me decís el documento de quien recibe. |
| ENT-L-DELIVERY-002 | L8 | L8 pedido DATOS | 0.2 | L8: para el remito necesito el nombre y el dni de quien lo recibe |
| ENT-L-ENCUESTA-004 | L6 | L6 pedido DATOS | 0.2 | L6: Para validar que sos afiliada, ¿me confirmás tu número de documento? |
| ENT-L-MEDICO-001 | L5 | L5 pedido DATOS | 0.2 | L5: Sí, diez y media. Para dejar cargada la admisión, ¿me confirmás tu DNI? |
| ENT-L-MEDICO-003 | L3 | L3 pedido DATOS | 0.2 | L3: Santiago, tenés turno mañana a las siete y media para extracción. Para confirmarlo, ¿me decís tu número de do… |
| ENT-L-SELECCION-003 | L10 | L8 pedido DATOS, L10 pedido DATOS | 0.2 | L10: Perfecto. ¿Y su número de CUIL? |
| ENT-L-SOPORTE-002 | L6 | L6 pedido DATOS | 0.2 | L6: me imagino para validar la garantía necesito el dni del titular de la factura |
| ENT-L-SOPORTE-006 | L8 | L8 pedido DATOS | 0.2 | L8: Para el envío, ¿me confirmás tu número de documento? |
| ENT-L-TRAMITE-002 | L4 | L4 pedido DATOS | 0.2 | L4: Lourdes, sacaste un turno para la renovación de la licencia. ¿Me confirmás tu DNI y tu fecha de nacimiento? |
| ENT-L-VENTAS-005 | L5 | L5 pedido DATOS | 0.2 | L5: Por eso te llamo, te quedó a mitad de camino. Faltaba validar la identidad. ¿Me confirmás tu DNI? |
| ENT-L-VENTAS-007 | L11 | L11 pedido DATOS | 0.2 | L11: tu nombre completo el dni y más o menos cuánto ganás por mes en blanco |

### Los casos en que la repetición de C avisa en otra línea

| caso | clase | T_R | C | C (repetición) |
|---|---|---|---|---|
| CV2-D-V-BANCO-003 | vishing | 19 | L3 | L1 |
| CV2-D-V-FAMILIAR-003 | vishing | 15 | L14 | L15 |
| LEG-CC-03 | legitima | – | L8 | – |

## 5. La segunda consulta (motivo) con la regla de C

En Colab la segunda consulta se pidió con la regla de la corrida («riesgo ≥ 0,4 o alerta», `UMBRAL_CORTE`), no con «riesgo ≥ 0.3 o alerta».

- C avisa en 63 llamadas de la vista; la segunda consulta corrió en la línea de ese aviso en 7, y en 39 no corrió nunca (el riesgo no llegó a 0,4 ni hubo alerta escrita).
- En 59 de esos 63 avisos el modelo no escribió alerta: avisa solo el riesgo. Con v4, en la corrida del JSON cortado, 19 de 78 avisos eran solo por riesgo, y ahí estaban los 4 fallos de la segunda consulta.
- 26 avisos de C a estafas llegan antes del pedido o en llamadas sin pedido. `motivo_v4_corte.txt` pide «lo que le están pidiendo»: en esas líneas todavía no hay pedido.

Motivos que escribió la segunda consulta en las estafas de la vista, cuando corrió antes del pedido o sin pedido (primeros 8):

| estafa | línea | T_R | motivo | evidencia en el texto |
|---|---|---|---|---|
| BANCO-001 | L29 | 32 | Tené cuidado, te están diciendo que alguien intenta acceder a tu cuenta, es una táctica c… | true |
| BANCO-004 | L10 | 16 | Cuidado, te están pidiendo un código para confirmar tu titularidad, lo cual es una táctic… | true |
| BANCO-005 | L11 | 19 | Cuidado, te están pidiendo tu clave de seis dígitos, lo cual es una señal de alerta en es… | true |
| BANCO-006 | L10 | 14 | Desconfía de que le pidan confirmar datos o acciones a través de una llamada inesperada. | true |
| BANCO-007 | L3 | 17 | Desconfiá, te están pidiendo información sobre un cambio en tu cuenta que no iniciaste. | true |
| BANCO-010 | L1 | 13 | Desconfía de la urgencia y la mención de una retención para verificar la legitimidad de l… | true |
| BANCO-011 | L4 | – | Desconfía de la transferencia y no debe proporcionar ninguna información personal o de cu… | true |

## 6. Exploración: riesgo sostenido en líneas seguidas (no decide; genera hipótesis)

Avisa con alerta escrita, o con riesgo ≥ u en k líneas seguidas. Elegir u y k mirando esta tabla sería ajustar sobre desarrollo: si se quiere usar, se escribe antes y se prueba en otros casos.

| corrida | u | k | estafas | antes del pedido | antes o en el pedido | FA |
|---|---|---|---|---|---|---|
| v4-corte | 0.3 | 1 | 39/46 | 22/36 | 28/36 | 52/94 |
| v4-corte | 0.3 | 2 | 37/46 | 20/36 | 27/36 | 46/94 |
| v4-corte | 0.3 | 3 | 37/46 | 16/36 | 27/36 | 43/94 |
| v4-corte | 0.4 | 1 | 28/46 | 10/36 | 25/36 | 42/94 |
| v4-corte | 0.4 | 2 | 28/46 | 10/36 | 25/36 | 42/94 |
| v4-corte | 0.4 | 3 | 28/46 | 10/36 | 25/36 | 42/94 |
| c-json-corte | 0.3 | 1 | 36/46 | 17/36 | 25/36 | 27/94 |
| c-json-corte | 0.3 | 2 | 32/46 | 12/36 | 16/36 | 18/94 |
| c-json-corte | 0.3 | 3 | 30/46 | 12/36 | 14/36 | 14/94 |
| c-json-corte | 0.4 | 1 | 15/46 | 6/36 | 10/36 | 9/94 |
| c-json-corte | 0.4 | 2 | 12/46 | 6/36 | 8/36 | 9/94 |
| c-json-corte | 0.4 | 3 | 12/46 | 4/36 | 8/36 | 9/94 |
| c-json-corte-rep | 0.3 | 1 | 36/46 | 16/36 | 25/36 | 26/94 |
| c-json-corte-rep | 0.3 | 2 | 34/46 | 12/36 | 16/36 | 18/94 |
| c-json-corte-rep | 0.3 | 3 | 31/46 | 12/36 | 15/36 | 13/94 |
| c-json-corte-rep | 0.4 | 1 | 15/46 | 6/36 | 11/36 | 9/94 |
| c-json-corte-rep | 0.4 | 2 | 13/46 | 6/36 | 9/36 | 9/94 |
| c-json-corte-rep | 0.4 | 3 | 13/46 | 5/36 | 9/36 | 9/94 |

### Techo de sumarle a C un detector literal de pedidos críticos (la referencia hace de oráculo)

Pedido crítico: el primer evento `pedido` de la referencia con código, clave, plata, acceso remoto o acción de seguridad; los datos personales no cuentan. Es un techo: supone un detector que nunca falla, y las marcas de la referencia no tienen revisión humana.

| regla | estafas | antes del pedido | antes o en el pedido | FA |
|---|---|---|---|---|
| v4 «riesgo ≥ 0.4 o alerta» | 28/46 | 10/36 | 25/36 | 42/94 |
| C «riesgo ≥ 0.3 o alerta» | 36/46 | 17/36 | 25/36 | 27/94 |
| pedido crítico (oráculo) solo | 30/46 | 0/36 | 30/36 | 2/94 |
| C «riesgo ≥ 0.3 o alerta» o pedido crítico (oráculo) | 44/46 | 17/36 | 35/36 | 27/94 |

Legítimas con un pedido crítico en la referencia: ENT-L-SOPORTE-005, ENT-L-VENTAS-009.

## 7. Controles de ventas, línea por línea

| control | clase | prompt | riesgo escrito por línea (! = alerta escrita) |
|---|---|---|---|
| CTRL-L-VENTA-PORTABILIDAD | legitima_dificil | v4 | 0.1 0.2 0.2 0.5 0.4 0.3 0.3 0.9! 0.8! 0.8! 0.8! 0.8! 0.8! 0.8! 0.8! 0.9! |
| CTRL-L-VENTA-PORTABILIDAD | legitima_dificil | C | 0.1 0.2 0.2 0.6! 0.3 0.3 0.3 0.6! 0.6 0.3 0.3 0.4 0.3 0.3 0.3 0.3 |
| CTRL-L-VENTA-PORTABILIDAD | legitima_dificil | v4-premisa | 0.1 0.2 0.2 0.4 0.3 0.3 0.3 0.8! 0.7! 0.7! 0.8! 0.8! 0.8! 0.8! 0.8! 0.8! |
| CTRL-V-OPERADOR-SMS | vishing | v4 | 0.1 0.2 0.2 0.2 0.3 0.8! 0.8! 0.8! 0.8! 0.9! 0.8! 0.9! 0.9! 0.9! |
| CTRL-V-OPERADOR-SMS | vishing | C | 0.1 0.1 0.2 0.3 0.3 0.6! 0.6! 0.3 0.3 0.6! 0.3 0.6! 0.6 0.6! |
| CTRL-V-OPERADOR-SMS | vishing | v4-premisa | 0.1 0.2 0.2 0.2 0.2 0.8! 0.8! 0.8! 0.8! 0.8! 0.8! 0.9! 0.8! 0.9! |
| CTRL-L-BANCO-OFRECE-PRESTAMO | legitima_dificil | v4 | 0.1 0.3 0.2 0.7! 0.6! 0.6! 0.5! 0.6! 0.6! 0.6! 0.5 0.3 0.3 0.3 0.3 0.3 |
| CTRL-L-BANCO-OFRECE-PRESTAMO | legitima_dificil | C | 0.1 0.2 0.2 0.3 0.3 0.3 0.2 0.3 0.3 0.3 0.3 0.2 0.3 0.2 0.3 0.2 |
| CTRL-L-BANCO-OFRECE-PRESTAMO | legitima_dificil | v4-premisa | 0.1 0.2 0.2 0.6! 0.5! 0.5! 0.5! 0.5! 0.6! 0.5 0.5 0.3 0.3 0.3 0.3 0.3 |
| CTRL-V-BANCO-PRESTAMO-TOKEN | vishing | v4 | 0.1 0.3 0.3 0.8! 0.8! 0.8! 0.8! 0.8! 0.8! 0.9! 0.9! 0.9! 0.9! 0.9! |
| CTRL-V-BANCO-PRESTAMO-TOKEN | vishing | C | 0.1 0.2 0.2 0.3 0.2 0.3 0.3 0.6 0.3 0.85! 0.7! 0.85! 0.7! 0.8! |
| CTRL-V-BANCO-PRESTAMO-TOKEN | vishing | v4-premisa | 0.1 0.3 0.3 0.8! 0.8! 0.8! 0.8! 0.8! 0.8! 0.9! 0.9! 0.9! 0.9! 0.9! |
| CTRL-L-PIDE-PRESTAMO | legitima_dificil | v4 | 0.2 0.2 0.9! 0.8! 0.8! 0.8! 0.8! 0.8! 0.8! 0.8! 0.8! 0.8! 0.8! 0.8! 0.7! 0.7! |
| CTRL-L-PIDE-PRESTAMO | legitima_dificil | C | 0.1 0.1 0.3 0.2 0.1 0.2 0.2 0.2 0.2 0.2 0.3 0.3 0.3 0.3 0.2 0.2 |
| CTRL-L-PIDE-PRESTAMO | legitima_dificil | v4-premisa | 0.2 0.2 0.9! 0.8! 0.8! 0.8! 0.8! 0.8! 0.8! 0.8! 0.8! 0.8! 0.8! 0.8! 0.8! 0.8! |
| CTRL-V-PRESTAMO-REDES | vishing | v4 | 0.2 0.2 0.3 0.3 0.9! 0.8! 0.9! 0.9! 0.9! 0.9! 0.9! 0.9! 0.9! 0.9! 0.9! |
| CTRL-V-PRESTAMO-REDES | vishing | C | 0.2 0.2 0.2 0.3 0.3 0.3 0.6! 0.6 0.7! 0.6 0.6 0.7! 0.7! 0.7! 0.7! |
| CTRL-V-PRESTAMO-REDES | vishing | v4-premisa | 0.2 0.2 0.3 0.3 0.9! 0.8! 0.9! 0.9! 0.9! 0.9! 0.9! 0.9! 0.9! 0.9! 0.9! |

