# #143, etapa 2: exploración para decidir cómo seguir (escrita después de ver los resultados)

C con «riesgo ≥ 0.3 o alerta», primera corrida, dentro del alcance (46 estafas y 94 legítimas), salvo donde se dice.

## 1. alerta_sugerida en C y lo que cuesta generar después del riesgo

| corrida | líneas con alerta escrita | llamadas | riesgo mínimo | con riesgo < 0,3 | con riesgo < 0,4 |
|---|---|---|---|---|---|
| c-json-corte | 110 | 19 | 0.6 | 0 | 0 |
| c-json-corte-rep | 110 | 21 | 0.6 | 0 | 0 |
| v4-corte | 507 | 70 | 0.2 | 2 | 10 |

- c-json-corte: con «riesgo ≥ 0,3» sola cambia la línea de aviso en 0 de 140 llamadas.
- c-json-corte-rep: con «riesgo ≥ 0,3» sola cambia la línea de aviso en 0 de 140 llamadas.

Cómo empieza la salida de C (hasta alerta_sugerida), lo más común:

- 1032 líneas: `'{\n  "riesgo": 0.1,\n  '`
- 857 líneas: `'{\n  "riesgo": 0.2,\n  '`
- 482 líneas: `'{\n  "riesgo": 0.3,\n  '`
- 107 líneas: `'{\n  "riesgo": 0.6,\n  '`

En T4, medianas por línea: 276 ms en total, 96 ms de lectura del prompt y 6.9 ms por token generado (24 tokens).

## 2. ¿El riesgo de C sube y baja?

Cambio del riesgo respecto de la línea anterior, según quién habla en la línea.

| clase | línea de | líneas | sube | baja | cambio medio |
|---|---|---|---|---|---|
| estafas | OTRA | 505 | 91 (18 %) | 46 (9 %) | +0.014 |
| estafas | PROTEGIDA | 518 | 57 (11 %) | 66 (13 %) | -0.003 |
| legítimas | OTRA | 742 | 116 (16 %) | 80 (11 %) | +0.006 |
| legítimas | PROTEGIDA | 716 | 59 (8 %) | 82 (11 %) | -0.003 |

| clase | llegan a 0,3 | después bajan de 0,3 | y vuelven a 0,3 | terminan debajo de 0,3 |
|---|---|---|---|---|
| estafas | 36 | 23 | 18 | 12 |
| legítimas | 27 | 21 | 9 | 19 |

Bajadas de 0,2 o más en una línea, por quién habla:

### estafa, línea de OTRA: 14

- CV2-D-V-BANCO-004 L22 0.6→0.3 (T_R 16): Bien, ya quedó asociado el teléfono al reclamo.
- CV2-D-V-BANCO-007 L7 0.6→0.3 (T_R 17): Ese es el registro viejo que estamos retirando.
- CV2-D-V-BANCO-007 L9 0.6→0.3 (T_R 17): Es el número temporal que usa el área de recuperación durante el cambio.
- CV2-D-V-BANCO-007 L11 0.6→0.3 (T_R 17): Van a pasar por ahí mientras el sistema libera el anterior.
- CV2-D-V-BANCO-007 L23 0.5→0.3 (T_R 17): Si vence la solicitud, queda una revisión manual y durante ese tiempo podés perder los avisos.
- CV2-D-V-BANCO-008 L18 0.5→0.3 (T_R 16): La cantidad completa, unos doscientos mil según el registro.
- CV2-D-V-BANCO-009 L15 0.7→0.3 (T_R 13): Sí el sistema los compara con el registro y después te deja crear uno nuevo
- CV2-D-V-BANCO-010 L13 0.6→0.3 (T_R 13): Para esta gestión usás esa misma serie como comprobante de voluntad.
- CV2-D-V-BANCO-011 L6 0.5→0.3 (T_R –): Todavía no está confirmada, por eso te llamo antes del cierre.
- CV2-D-V-ORGANISMO_PREVISIONAL-001 L14 0.5→0.3 (T_R 12): Ese mismo. Abra la ficha de actualización de domicilio.
- CV2-D-V-ORGANISMO_PREVISIONAL-001 L16 0.5→0.3 (T_R 12): Es el título general. Lo que ponemos abajo es la dirección nueva.
- CV2-D-V-ORGANISMO_PREVISIONAL-001 L22 0.5→0.3 (T_R 12): Es quien valida administrativamente, no quien va a cobrar.
- CV2-D-V-SOPORTE-002 L21 0.6→0.3 (T_R 13): Perfecto, ya estoy viendo la pantalla.
- CV2-D-V-SOPORTE-002 L23 0.6→0.2 (T_R 13): Sí, la semana ya se mueve correctamente.

### estafa, línea de PROTEGIDA: 15

- CV2-D-V-BANCO-001 L37 0.7→0.3 (T_R 32): Dejá constancia también de que voy a consultar yo. Corto acá.
- CV2-D-V-BANCO-002 L21 0.6→0.3 (T_R 18): Me preocupa dejar entrar otra máquina a mi cuenta.
- CV2-D-V-BANCO-004 L11 0.6→0.3 (T_R 16): ¿Un código al celular?
- CV2-D-V-BANCO-004 L15 0.6→0.4 (T_R 16): ¿Te leo el número?
- CV2-D-V-BANCO-005 L2 0.3→0.1 (T_R 19): Sí pagué una cuota el viernes
- CV2-D-V-BANCO-006 L11 0.6→0.3 (T_R 14): ¿Confirmar cómo?
- CV2-D-V-BANCO-006 L21 0.6→0.3 (T_R 14): Lo reviso yo desde la app y corto.
- CV2-D-V-BANCO-007 L4 0.5→0.3 (T_R 17): Veo uno, pero no lo abrí todavía.
- CV2-D-V-BANCO-008 L21 0.6→0.3 (T_R 16): No voy a preparar efectivo para alguien que todavía no conozco.
- CV2-D-V-BANCO-008 L23 0.6→0.3 (T_R 16): Prefiero terminar la llamada y consultar en la sucursal.
- CV2-D-V-BANCO-009 L20 0.8→0.6 (T_R 13): Voy a cortar y revisar con el banco
- CV2-D-V-BANCO-010 L10 0.6→0.4 (T_R 13): ¿Me llega por la aplicación?
- CV2-D-V-FAMILIAR-001 L18 0.6→0.3 (T_R 15): El importe era ciento treinta y ocho
- CV2-D-V-FAMILIAR-003 L18 0.6→0.3 (T_R 15): No voy a transferir sin confirmar la reserva con el salón.
- CV2-D-V-SOPORTE-002 L14 0.8→0.6 (T_R 13): No conozco ese programa.

### legítima, línea de OTRA: 16

- ENT-L-BANCO-001 L9 0.7→0.3 (T_R –): bien la operación quedó rechazada no se te cobró nada
- ENT-L-BANCO-001 L17 0.6→0.3 (T_R –): listo ya está bloqueada por precaución también cerré las sesiones abiertas de la app
- ENT-L-BANCO-001 L23 0.7→0.3 (T_R –): tu número de gestión es cinco ocho dos dos uno cero por si tenés que reclamar algo
- ENT-L-BANCO-004 L8 0.7→0.3 (T_R –): entiendo como es un monto alto a un destino nuevo nuevo queda en revisión hasta que titular la confirme
- ENT-L-BANCO-005 L11 0.7→0.3 (T_R –): No. Se inicia el desconocimiento y, si se confirma que no fue usted, se le reintegra.
- ENT-L-BANCO-005 L13 0.6→0.3 (T_R –): Normalmente entre diez y quince días hábiles.
- ENT-L-BANCO-005 L19 0.6→0.3 (T_R –): Bien. También le recomiendo cambiar el PIN cuando le llegue la nueva, en el cajero. Ese PIN no se lo diga a nadie.
- ENT-L-BANCO-005 L21 0.6→0.3 (T_R –): El número de reclamo le llega por mail. Si no le llega, vaya a cualquier sucursal con el documento.
- ENT-L-BANCO-006 L10 0.6→0.3 (T_R –): No, nunca. Ni yo ni nadie del banco te lo va a pedir. Si alguien te lo pide, cortá.
- ENT-L-ENCUESTA-006 L4 0.3→0.1 (T_R –): no nada ayer estuviste en la sucursal centro y te queremos hacer una encuesta de tres preguntas
- ENT-L-SOPORTE-003 L3 0.3→0.1 (T_R –): Casi. Le cambiamos el disco por uno sólido, como habíamos quedado, y reinstalamos el sistema.
- LEG-BA-02 L7 0.6→0.3 (T_R –): Mientras tanto, por precaución, el acceso desde ese dispositivo nuevo ya quedó suspendido. No tenés que darme ni hacer …
- LEG-ST-03 L3 0.3→0.1 (T_R –): Sí, ya está lista. Le cambiamos el disco por uno sólido, como habíamos quedado, y le reinstalamos el sistema. Tus archi…
- LEG2-BA-01 L8 0.8→0.2 (T_R –): Ok. La operación quedó rechazada, no se te cobró. Voy a bloquear la tarjeta y te mandamos una nueva a tu domicilio en s…
- LEG2-BA-02 L8 0.8→0.3 (T_R –): Exacto. Mientras tanto, el acceso desde ese dispositivo ya quedó suspendido por precaución.
- LEG2-BA-02 L10 0.7→0.2 (T_R –): Perfecto, Carla. Gracias.

### legítima, línea de PROTEGIDA: 7

- ENT-L-BANCO-001 L6 0.7→0.3 (T_R –): bueno bueno cuarenta millones ciento cinco mil tressientos veintidós nací el catorce de marzo del noventa y siete
- ENT-L-BANCO-001 L20 0.6→0.3 (T_R –): ok y la compra esa no me la van a cobrar en el resumen
- ENT-L-BANCO-004 L19 0.6→0.3 (T_R –): ok entonces ya se manda
- ENT-L-BANCO-004 L35 0.5→0.3 (T_R –): ok eso no lo havía pensado
- ENT-L-BANCO-005 L6 0.6→0.3 (T_R –): No, estoy en Tucumán. Y la tarjeta la tengo acá.
- LEG2-BA-01 L5 0.7→0.2 (T_R –): Cuarenta, ciento cinco, trescientos veintidós. Y nací el catorce de marzo del noventa y siete.
- LEG2-ST-03 L5 0.6→0.3 (T_R –): Treinta y nueve, setecientos dos, ciento quince.

## 3. Frases tranquilizadoras de OTRA

Búsqueda por expresión regular: `tranquil|no (es|se trata de) (una|ninguna) estafa|no te preocup|no se preocup|no (te|le) (voy|vamos) a pedir|nunca (te|le) (vamos a |va a )?pedi|no compart|no (le|se lo|te lo) (des|dé|digas|diga)|por (tu|su) seguridad|para (tu|su) (seguridad|tranquilidad)|es (todo )?(seguro|oficial)|no soy (un |ningún )?estafador|cuento|verso`.

- **estafas:** 4 líneas de OTRA; sube 0, baja 0, igual 4 (cambio medio +0.000; resto de las líneas de OTRA +0.015).
  - CV2-D-V-FAMILIAR-002 L6 0.1→0.1 (T_R 16): La retiré esta mañana, después te cuento eso.
  - CV2-D-V-ORGANISMO_PREVISIONAL-004 L10 0.3→0.3 (T_R 14): No hace falta foto Podés mirar el reverso donde está impreso el número de trámite
  - CV2-D-V-WHATSAPP-002 L8 0.2→0.2 (T_R 10): No te preocupes, primero revisamos si la cuenta sigue asociada a tu número.
  - CV2-D-V-WHATSAPP-002 L12 0.2→0.2 (T_R 10): Sí, el que aparece con el aviso de no compartir. Es automático, no es una clave bancaria.
- **legítimas:** 18 líneas de OTRA; sube 4, baja 2, igual 12 (cambio medio +0.011; resto de las líneas de OTRA +0.006).
  - ENT-L-BANCO-001 L19 0.3→0.6 (T_R –): te va a llegar un sms con un código para reactivarla ese código lo ponés vos en la app no se lo digas a nadie tampoco a…
  - ENT-L-BANCO-004 L18 0.6→0.6 (T_R –): bien le aclaro una cosa nosotros nunca le vamos a pedir el token ni ningún código para liberar una operación si alguien…
  - ENT-L-BANCO-005 L19 0.6→0.3 (T_R –): Bien. También le recomiendo cambiar el PIN cuando le llegue la nueva, en el cajero. Ese PIN no se lo diga a nadie.
  - ENT-L-ENCUESTA-001 L11 0.1→0.1 (T_R –): Sí, se suma al descuento de los días sin servicio.
  - ENT-L-SOPORTE-006 L16 0.2→0.1 (T_R –): El chip viene en una tarjeta con un PUK impreso. Guardalo vos, no se lo des a nadie.
  - ENT-L-VENTAS-002 L20 0.3→0.3 (T_R –): hasta fin de mes seguro después no te lo puedo asegurar
  - ENT-L-VENTAS-003 L3 0.2→0.2 (T_R –): te llamo porque como clienta tenés un seguro de hogar con el primer mes bonificado cubre incendio robo y daños por agua…
  - ENT-L-VENTAS-006 L4 0.2→0.2 (T_R –): Carolina, te llamo para ofrecerte el pack de deportes con cuarenta por ciento de descuento por tres meses. Entra todo e…
  - ENT-L-VENTAS-006 L16 0.2→0.2 (T_R –): Sí, la referencia es para eso. Igual no te preocupes por mí.
  - ENT-L-VENTAS-006 L22 0.2→0.2 (T_R –): Se pierde el descuento. Pero no te voy a apurar.
  - ENT-L-VENTAS-008 L6 0.1→0.2 (T_R –): Le cuento igual. Este mes hay cupos en el plan setenta treinta con la primera cuota bonificada.
  - LEG-BA-01 L3 0.1→0.2 (T_R –): Gonzalo, te llamo del área de prevención de fraudes de Banco Andino, mi nombre es Verónica. Antes que nada te aclaro: e…
  - LEG-CC-03 L3 0.1→0.1 (T_R –): Gonzalo, ¿cómo andás? Te habla Rodrigo de VisiónNorte, de atención a clientes. Te llamo porque tenés el pack básico y t…
  - LEG-CC-03 L7 0.2→0.2 (T_R –): No, está perfecto que preguntes. Hacé una cosa: llamá al cero ochocientos que figura en tu factura, pedí por la promo d…
  - LEG-VE-01 L5 0.1→0.1 (T_R –): Perfecto, te cuento rápido. Este mes tenemos financiación a tasa cero en doce cuotas para una parte del valor, y el res…
  - LEG-VE-02 L5 0.2→0.2 (T_R –): Te cuento igual en treinta segundos: es un plan setenta treinta, pagás cuotas en pesos y podés adjudicar por sorteo o p…
  - LEG2-CC-06 L4 0.2→0.2 (T_R –): Sofía, te ofrezco el pack de deportes con cuarenta por ciento de descuento por tres meses. Entra todo el fútbol y la pr…
  - LEG2-VE-01 L4 0.1→0.2 (T_R –): Te cuento: este mes hay tasa cero en doce cuotas para una parte, y el resto en sesenta cuotas fijas. Si querés, te prec…

## 4. Consultar solo en las líneas de OTRA

Cada consulta lleva la transcripción entera hasta esa línea, con las dos voces. Si no se consulta en las líneas de PROTEGIDA, la salida en las de OTRA no cambia: el aviso pasa a la primera línea de OTRA que dispara.

- c-json-corte: estafa: se atrasa 1 ×6; estafa: se atrasa 3 ×1; estafa: se pierde ×1; legítima: se atrasa 1 ×2; legítima: se atrasa 3 ×1; legítima: se pierde ×3
- c-json-corte-rep: estafa: se atrasa 1 ×5; estafa: se atrasa 13 ×1; estafa: se atrasa 3 ×1; legítima: se atrasa 1 ×2; legítima: se atrasa 3 ×1; legítima: se atrasa 9 ×1; legítima: se pierde ×1

| corrida | consultas en | estafas | antes del pedido | antes o en el pedido | FA | consultas |
|---|---|---|---|---|---|---|
| c-json-corte | todas las líneas | 36/46 | 17/36 | 25/36 | 27/94 | 2621 (100 %) |
| c-json-corte | solo OTRA | 35/46 | 15/36 | 25/36 | 24/94 | 1313 (50 %) |
| c-json-corte-rep | todas las líneas | 36/46 | 16/36 | 25/36 | 26/94 | 2621 (100 %) |
| c-json-corte-rep | solo OTRA | 36/46 | 15/36 | 25/36 | 25/94 | 1313 (50 %) |

## 5. Aperturas

### Legítimas con FA: 13 de 27 avisan en L1–L3

- ENT-L-BANCO-001 (ENT-L (42)), aviso en L1, riesgo L1–L6 0.3 0.3 0.5 0.8 0.7 0.3: buenas tardes te llamo del área de de prevención fraudes del banco me llamo veronica
- ENT-L-BANCO-002 (ENT-L (42)), aviso en L2, riesgo L1–L6 0.1 0.3 0.3 0.6 0.5 0.7: Hola, buen día. Te llamo del banco, del sector de seguridad.
- ENT-L-BANCO-005 (ENT-L (42)), aviso en L1, riesgo L1–L6 0.3 0.3 0.3 0.5 0.6 0.3: Buen día, le hablo de prevención de fraudes del banco.
- ENT-L-BANCO-006 (ENT-L (42)), aviso en L2, riesgo L1–L6 0.1 0.3 0.3 0.3 0.3 0.3: Hola, buenas tardes. Te hablo del banco, por tu app.
- ENT-L-ENCUESTA-006 (ENT-L (42)), aviso en L3, riesgo L1–L6 0.1 0.2 0.3 0.1 0.2 0.2: hola buenas tardes te habla martina del banco del área de experiencia de clientes
- ENT-L-SOPORTE-001 (ENT-L (42)), aviso en L3, riesgo L1–L6 0.2 0.2 0.3 0.3 0.2 0.2: hola buen día te habla leonel de soporte técnico de fibrasur te llamo por el reclamo 3349 de falta de serbicio
- ENT-L-SOPORTE-003 (ENT-L (42)), aviso en L1, riesgo L1–L6 0.3 0.3 0.1 0.1 0.1 0.1: Hola, ¿Tobías? Te hablo de TecnoFix, el local de la calle Muñecas. Dejaste una notebook la semana pasada.
- LEG-BA-02 (LEG (21)), aviso en L3, riesgo L1–L6 0.1 0.1 0.5 0.6 0.6 0.6: Hola, buen día, ¿me comunico con Carla Benítez?
- LEG-BA-03 (LEG (21)), aviso en L3, riesgo L1–L6 0.1 0.1 0.3 0.2 0.1 0.2: Buenas tardes, ¿hablo con Juan Pablo Sosa?
- LEG-ST-03 (LEG (21)), aviso en L1, riesgo L1–L6 0.3 0.3 0.1 0.1 0.1 0.1: Hola, ¿Matías? Te hablo de TecnoFix, el local de la calle Muñecas. Dejaste una notebook la semana pasada.
- LEG2-BA-03 (LEG2 (28)), aviso en L2, riesgo L1–L6 0.1 0.3 0.2 0.3 0.2 0.2: Buenas tardes, te habla Lorena, de prevención de fraudes de Banco Andino. ¿Me decís tu nombre completo, por favor?
- LEG2-ST-03 (LEG2 (28)), aviso en L2, riesgo L1–L6 0.1 0.3 0.3 0.6 0.3 0.2: Hola, ¿Matías? Te hablo de TecnoFix, el local de la calle Muñecas. Dejaste una notebook la semana pasada.
- LEG2-ST-05 (LEG2 (28)), aviso en L2, riesgo L1–L6 0.1 0.3 0.2 0.2 0.2 0.2: Hola, buenas tardes, te habla Julieta, de soporte de Tiendita Online. Te llamo por el ticket que abriste porque no podías entrar a tu cuenta. ¿Hablo …

### Estafas avisadas: 14 de 36 avisan en L1–L3

- CV2-D-V-BANCO-001 (corpus_v2), aviso en L2, riesgo L1–L6 0.2 0.3 0.2 0.3 0.3 0.2: Soy del sector de medios de pago del banco, por el reclamo de un cargo.
- CV2-D-V-BANCO-003 (corpus_v2), aviso en L3, riesgo L1–L6 0.2 0.2 0.3 0.3 0.2 0.2: Buenas tardes soy Esteban de la mesa de efectivo del banco
- CV2-D-V-BANCO-005 (corpus_v2), aviso en L1, riesgo L1–L6 0.3 0.1 0.3 0.3 0.3 0.3: Buen día Nicolás de operaciones digitales del banco Vos hiciste una trasferencia a la cooperativa La Esquina
- CV2-D-V-BANCO-007 (corpus_v2), aviso en L1, riesgo L1–L6 0.3 0.3 0.5 0.3 0.3 0.6: Buenas, te llamo del banco por una autorización que quedó esperando.
- CV2-D-V-BANCO-008 (corpus_v2), aviso en L2, riesgo L1–L6 0.1 0.3 0.3 0.3 0.3 0.3: Buenas noches, llamo del banco por una inconsistencia en la caja de seguridad.
- CV2-D-V-BANCO-010 (corpus_v2), aviso en L1, riesgo L1–L6 0.5 0.5 0.6 0.6 0.6 0.6: Te llamo del banco por una retención sobre la transferencia que hiciste a Maderas Sur.
- CV2-D-V-BANCO-012 (corpus_v2), aviso en L1, riesgo L1–L6 0.3 0.3 0.3 0.2 0.3 0.3: Buenas tardes, de control de operaciones. Quedó pendiente un alta de destinatario en su cuenta.
- CV2-D-V-ORGANISMO_PREVISIONAL-003 (corpus_v2), aviso en L1, riesgo L1–L6 0.3 0.2 0.2 0.2 0.2 0.2: Te llamamos del centro de orientación previsional por la consulta que dejaste sobre aportes.
- CV2-D-V-ORGANISMO_PREVISIONAL-005 (corpus_v2), aviso en L2, riesgo L1–L6 0.1 0.3 0.3 0.3 0.3 0.3: Buenas, te llamo de control de prestaciones. Hay una revisión sobre el pago que entró este mes.
- CV2-D-V-ORGANISMO_PREVISIONAL-006 (corpus_v2), aviso en L1, riesgo L1–L6 0.3 0.2 0.2 0.3 0.3 0.3: Te llamo de la mesa de regularización por un cambio en el calendario de pagos previsionales.
- CV2-D-V-SOPORTE-007 (corpus_v2), aviso en L2, riesgo L1–L6 0.1 0.3 0.3 0.3 0.3 0.3: Buenas, te llamo de soporte de Clima Hogar por una actividad inusual en el perfil de consumo.
- CV2-D-V-SOPORTE-008 (corpus_v2), aviso en L1, riesgo L1–L6 0.3 0.3 0.2 0.2 0.2 0.2: Hola, asistencia del portal de trámites. Estamos revisando una firma iniciada con su usuario.
- CV2-D-V-WHATSAPP-004 (corpus_v2), aviso en L1, riesgo L1–L6 0.3 0.2 0.1 0.1 0.3 0.3: Hola, soy Julián, del grupo de consorcio de la torre B. ¿Te llegó el archivo de expensas?
- CV2-D-V-WHATSAPP-007 (corpus_v2), aviso en L3, riesgo L1–L6 0.1 0.2 0.3 0.3 0.3 0.3: Hola, llamo del equipo de soporte de WhatsApp por un registro de cuenta iniciado desde otro teléfono.

Riesgo de C en la primera línea de OTRA, por familia (cantidad de llamadas por valor):

| clase | familia | llamadas | 0,1 | 0,2 | 0,3 | 0,4 o más |
|---|---|---|---|---|---|---|
| legítima | BA | 7 | 3 | 3 | 1 |  |
| legítima | BANCO | 6 |  | 2 | 4 |  |
| legítima | CC | 7 | 4 | 3 |  |  |
| legítima | CO | 7 | 6 | 1 |  |  |
| legítima | DELIVERY | 6 | 6 |  |  |  |
| legítima | EN | 7 | 6 | 1 |  |  |
| legítima | ENCUESTA | 6 | 3 | 3 |  |  |
| legítima | MEDICO | 4 | 2 | 2 |  |  |
| legítima | SELECCION | 3 | 3 |  |  |  |
| legítima | SOPORTE | 6 |  | 5 | 1 |  |
| legítima | ST | 7 | 4 |  | 3 |  |
| legítima | TRAMITE | 2 |  | 2 |  |  |
| legítima | TU | 7 | 7 |  |  |  |
| legítima | VE | 7 | 7 |  |  |  |
| legítima | VENTAS | 12 | 8 | 4 |  |  |
| estafa | BANCO | 12 |  | 6 | 5 | 1 |
| estafa | FAMILIAR | 6 | 3 | 3 |  |  |
| estafa | ORGANISMO_PREVISIONAL | 6 |  | 3 | 3 |  |
| estafa | PREMIO | 6 | 2 | 4 |  |  |
| estafa | SOPORTE | 8 | 1 | 5 | 2 |  |
| estafa | WHATSAPP | 8 | 4 | 3 | 1 |  |

## 6. Legítimas: FA según el pedido de datos y escenarios repetidos

| legítimas | llamadas | FA v4 (≥ 0,4 o alerta) | FA C (≥ 0,3 o alerta) |
|---|---|---|---|
| piden datos personales | 64 | 39 | 21 |
| no piden datos personales | 30 | 3 | 6 |

Escenarios: las legítimas se agrupan por parecido de palabras (coseno de bolsa de palabras sin palabras vacías, enlace simple). Es una aproximación: el umbral no está calibrado con reescrituras declaradas, como en #45.

| coseno | grupos | tamaños (cantidad × tamaño) | grupos con FA de v4 | grupos con FA de C |
|---|---|---|---|---|
| ≥ 0.6 | 75 | 57×1, 17×2, 1×3 | 36 | 24 |
| ≥ 0.5 | 56 | 31×1, 13×2, 11×3, 1×4 | 26 | 21 |
| ≥ 0.4 | 45 | 15×1, 13×2, 15×3, 2×4 | 24 | 18 |

Grupos de más de una llamada con coseno ≥ 0,5 (* = FA de C):

- ENT-L-TRAMITE-002, ENT-L-VENTAS-010, LEG2-TU-06, LEG2-VE-04
- ENT-L-BANCO-001*, LEG-BA-01*, LEG2-BA-01*
- ENT-L-BANCO-002*, LEG-BA-02*, LEG2-BA-02*
- ENT-L-BANCO-003, LEG-BA-03*, LEG2-BA-03*
- ENT-L-DELIVERY-002, LEG-CO-02, LEG2-CO-02
- ENT-L-DELIVERY-003, LEG-CO-03, LEG2-CO-03
- ENT-L-ENCUESTA-001, LEG-EN-01, LEG2-EN-01
- ENT-L-MEDICO-001, LEG-TU-01, LEG2-TU-01
- ENT-L-MEDICO-002, LEG-TU-02, LEG2-TU-02
- ENT-L-SOPORTE-002, LEG-ST-02, LEG2-ST-02
- ENT-L-VENTAS-001*, LEG-CC-01, LEG2-CC-01
- ENT-L-VENTAS-007, LEG-VE-01, LEG2-VE-01
- ENT-L-ENCUESTA-002, LEG-EN-02
- ENT-L-ENCUESTA-004, LEG2-EN-04
- ENT-L-ENCUESTA-005, LEG2-EN-05
- ENT-L-MEDICO-003, LEG-TU-03
- ENT-L-SOPORTE-001*, LEG-ST-01
- ENT-L-SOPORTE-004, LEG2-ST-04
- ENT-L-VENTAS-005, LEG2-CC-05*
- ENT-L-VENTAS-006, LEG2-CC-06*
- ENT-L-VENTAS-011, LEG2-VE-05
- ENT-L-VENTAS-012, LEG2-VE-06
- LEG-CO-01, LEG2-CO-01
- LEG-EN-03, LEG2-EN-03
- LEG-ST-03*, LEG2-ST-03*

