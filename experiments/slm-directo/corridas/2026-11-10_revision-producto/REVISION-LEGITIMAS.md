# Las 94 legítimas de desarrollo, con la política de producto

> **Estado: propuesta sin discutir.** Es una propuesta para Mateo: **falta que la acepte, la corrija o la descarte.**
> Si la acepta, la regla de la prueba la usa y se informan las dos versiones ([README](README.md#regla-escrita-antes-de-correr)).
> No cambia `texto/` ni `referencia/`.

## Cómo se hizo

- **Qué se leyó:** las 94 legítimas de [`alcance-140`](../../casos/listas/alcance-140.txt), enteras, con los roles
  PROTEGIDA y OTRA. Son también las 45 legítimas de `alcance-91`, que es un subconjunto.
- **Qué no se leyó antes de etiquetar:** `referencia/` (ni `tipo_legitima` ni `que_prueba`), prompts, corridas y
  análisis. Las etiquetas están en el commit `6c1fca0`, anterior a abrir los resultados.
- **Con qué criterio:** la [política](POLITICA.md), escrita antes. La pregunta para cada llamada es qué le pide OTRA a
  PROTEGIDA y qué pierde si OTRA mentía sobre quién es.
- **Las etiquetas,** en [`etiquetas-producto.json`](etiquetas-producto.json), con la intención, lo que pide OTRA y la
  línea que lo muestra:

| etiqueta | qué quiere decir | cómo cuenta un aviso |
|---|---|---|
| **No debería avisar** | La llamada no le pide a PROTEGIDA nada que se pueda perder | Falsa alarma |
| **Está bien que avise** (tolerable) | El aviso coincide con un consejo oficial aunque la llamada sea legítima | No es falsa alarma, y tampoco se exige |
| **Debería avisar** | La llamada pide un acto que las fuentes dicen no aceptar de quien llamó | Es un acierto; como legítima está mal anotada para medir falsas alarmas |

## Resultado

| | llamadas (/94) | en `alcance-91` (/45) | escenarios (/47) |
|---|---|---|---|
| No debería avisar | **75** | 36 | 36 |
| Está bien que avise | **18** | 9 | 8 |
| Debería avisar | **1** | 0 | 1 |
| Escenarios con las dos primeras | | | 2 |

Los escenarios son los de [`ESCENARIOS-LEGITIMAS-DESARROLLO.md`](../../casos/ESCENARIOS-LEGITIMAS-DESARROLLO.md): las 94
llamadas cuentan 47 situaciones, y la misma situación vuelve hasta tres veces.

### Debería avisar (1)

| caso | escenario | intención | razón, tomada de la conversación |
|---|---|---|---|
| `ENT-L-SOPORTE-005` | E42 | pedir un acto de riesgo | Soporte por un ticket de PROTEGIDA: le hace descargar un programa de asistencia remota (l. 11) y leerle el número de conexión (l. 13), y con la sesión abierta ella escribe su clave fiscal (l. 23). Es el pedido que las fuentes dicen no aceptar de quien llamó (S28). |

Es la llamada más difícil del lote y está bien escrita: un soporte real hace eso. Pero dentro de la llamada es igual a
la estafa del acceso remoto, y la persona escribe su clave fiscal con la sesión abierta. Avisar ahí es lo correcto.

### Está bien que avise (18)

**Trece son «el banco» que llama por un problema de seguridad.** Es el disfraz de la estafa más común, y el consejo
oficial ante esa llamada es cortar y llamar al número de la tarjeta (S12, S14, S16, S18, S21, S26). Si el detector
avisa, repite ese consejo, y hacerle caso cuesta unos minutos. Las otras cinco piden datos con un pretexto flojo o
proponen una transferencia.

| caso | escenario | intención | razón, tomada de la conversación |
|---|---|---|---|
| `ENT-L-BANCO-001` | E01 | advertir | A nombre del banco por un consumo; pide el DNI y la fecha de nacimiento antes de decir el motivo (l. 3). No pide credenciales ni actos. |
| `ENT-L-BANCO-002` | E02 | advertir | A nombre del banco por ingresos desde otro celular; pide el DNI (l. 6). PROTEGIDA se niega y OTRA le dice que corte y llame (l. 12). |
| `ENT-L-BANCO-003` | E03 | advertir | A nombre del banco; pide el nombre completo y los últimos tres números del documento (l. 3 y 5). Libera una compra que PROTEGIDA reconoce. |
| `ENT-L-BANCO-004` | E33 | advertir | A nombre del banco; pide el DNI (l. 4), el destinatario y el motivo de una transferencia que PROTEGIDA ya había hecho (l. 10–12), y la libera. |
| `ENT-L-BANCO-005` | E16 | advertir | A nombre del banco por una extracción; pide el documento (l. 3). Bloquea la tarjeta y confirma el domicilio que ya tiene. |
| `ENT-L-BANCO-006` | E34 | advertir | A nombre del banco por una vinculación nueva; pide el DNI (l. 4). PROTEGIDA empieza a dictar un código y OTRA la frena (l. 8). |
| `ENT-L-ENCUESTA-004` | E19 | preguntar una opinión | Encuesta de la obra social que pide el documento «para validar que sos afiliada» (l. 6). PROTEGIDA lo cuestiona (l. 7): una encuesta no necesita el DNI. |
| `ENT-L-SELECCION-003` | E41 | tomar datos | Alta laboral: nombre completo, CUIL, fecha de nacimiento y domicilio (l. 8–20). PROTEGIDA reconoce la entrevista, pero duda (l. 11); es el perfil completo de identidad, dictado a quien llamó. |
| `ENT-L-VENTAS-008` | E27 | ofrecer o vender | Venta en frío de un plan de ahorro, con «cupos pocos» (l. 10); pide nombre y DNI para «reservar» (l. 12). PROTEGIDA no lo da. |
| `ENT-L-VENTAS-009` | E28 | ofrecer o vender | La concesionaria ofrece asegurar el precio con una seña de 500 mil pesos, en caja o por transferencia (l. 15–19). No apura y PROTEGIDA no transfiere, pero es plata que se le pide a quien atendió. |
| `LEG-BA-01` | E01 | advertir | A nombre del banco por un consumo; no pide nada y bloquea la tarjeta (l. 5–7). |
| `LEG-BA-02` | E02 | advertir | A nombre del banco por inicios de sesión; no pide nada. PROTEGIDA desconfía y OTRA le dice que corte y llame (l. 5). |
| `LEG-BA-03` | E03 | advertir | A nombre del banco; solo pregunta si reconoce una compra (l. 3). |
| `LEG2-BA-01` | E01 | advertir | A nombre del banco; pide el DNI y la fecha de nacimiento antes de decir el motivo (l. 4). |
| `LEG2-BA-02` | E02 | advertir | A nombre del banco por ingresos desde un dispositivo nuevo; pide el DNI (l. 4). PROTEGIDA se niega y OTRA le dice que corte y llame (l. 6). |
| `LEG2-BA-03` | E03 | advertir | A nombre del banco; pide el nombre completo y los últimos tres números del DNI (l. 2 y 4). |
| `LEG2-BA-05` | E16 | advertir | A nombre del banco por una extracción; pide el DNI (l. 4) y confirma el domicilio que ya tiene. |
| `LEG2-EN-04` | E19 | preguntar una opinión | Encuesta de la obra social que pide el DNI «para validar que sos afiliada» (l. 4): una encuesta no necesita el DNI. |

### No debería avisar (75)

| caso | escenario | intención | razón, tomada de la conversación |
|---|---|---|---|
| `ENT-L-DELIVERY-001` | E35 | informar o coordinar | El repartidor coordina la entrega. El documento se dice al firmar, en la puerta (l. 15). |
| `ENT-L-DELIVERY-002` | E04 | informar o coordinar | El repartidor busca a quién dejarle el pedido. El DNI de quien recibe lo pide en mano (l. 8–10). |
| `ENT-L-DELIVERY-003` | E05 | informar o coordinar | El repartidor pide referencias para encontrar la casa. Nada para pagar (l. 18). |
| `ENT-L-DELIVERY-004` | E36 | informar o coordinar | La sucursal del correo avisa que hay un paquete para retirar. Pide el documento por teléfono (l. 8); no cobra nada (l. 14). |
| `ENT-L-DELIVERY-005` | E37 | informar o coordinar | El repartidor avisa que sale. PROTEGIDA quiere dictarle el código de entrega y él no la deja (l. 7). |
| `ENT-L-DELIVERY-006` | E17 | informar o coordinar | El flete coordina la entrega de un mueble. Pide el DNI del hermano para el remito (l. 18); el recargo se paga al entregar, contra recibo (l. 12). |
| `ENT-L-ENCUESTA-001` | E06 | preguntar una opinión | Encuesta de satisfacción tras una visita técnica. Confirma un mail que ya tiene (l. 13–15). |
| `ENT-L-ENCUESTA-002` | E18 | preguntar una opinión | Encuesta anónima de transporte: rango de edad, barrio, ocupación. El mail es opcional (l. 34). |
| `ENT-L-ENCUESTA-003` | E07 | preguntar una opinión | Encuesta de mercado. PROTEGIDA pide que la saquen del panel (l. 11–12). |
| `ENT-L-ENCUESTA-005` | E20 | preguntar una opinión | Encuesta municipal de residuos: calle y altura, y un nombre de pila para un reclamo (l. 19). |
| `ENT-L-ENCUESTA-006` | E38 | preguntar una opinión | Encuesta del banco tras una visita a la sucursal. Solo pide una opinión (l. 6). |
| `ENT-L-MEDICO-001` | E08 | informar o coordinar | Confirma un turno. Pide el DNI y el número de afiliado para la admisión (l. 5 y 9). |
| `ENT-L-MEDICO-002` | E09 | informar o coordinar | Reprograma un turno que suspendió la odontóloga. |
| `ENT-L-MEDICO-003` | E21 | informar o coordinar | Confirma un turno de laboratorio. Pide el documento (l. 3). |
| `ENT-L-MEDICO-004` | E22 | informar o coordinar | Recuerda el turno de una vacuna en la veterinaria. |
| `ENT-L-SELECCION-001` | E39 | informar o coordinar | Una agencia cita a una entrevista por una postulación que PROTEGIDA reconoce (l. 5–7). |
| `ENT-L-SELECCION-002` | E40 | informar o coordinar | Una consultora coordina una entrevista. PROTEGIDA ofrece leer un código de acceso y OTRA no la deja (l. 13). |
| `ENT-L-SOPORTE-001` | E23 | seguir una gestión de PROTEGIDA | Soporte por un reclamo de PROTEGIDA. Pide el DNI (l. 3) y da un código de visita (l. 19): darlo no es pedirlo. |
| `ENT-L-SOPORTE-002` | E10 | seguir una gestión de PROTEGIDA | Service por una orden de PROTEGIDA. Pide el DNI del titular de la factura (l. 6). |
| `ENT-L-SOPORTE-003` | E11 | seguir una gestión de PROTEGIDA | El local avisa que la notebook está lista y ofrece un cargador. Pide el documento que dejó (l. 15); se paga en el mostrador (l. 17). |
| `ENT-L-SOPORTE-004` | E24 | seguir una gestión de PROTEGIDA | Coordina la instalación de un aire: dirección y balcón. |
| `ENT-L-SOPORTE-006` | E43 | seguir una gestión de PROTEGIDA | Soporte por un reclamo de PROTEGIDA; le mandan un chip nuevo a su domicilio. Pide el documento (l. 8). |
| `ENT-L-TRAMITE-001` | E44 | informar o coordinar | La planta de revisión técnica confirma un turno. No se paga nada antes (l. 17). |
| `ENT-L-TRAMITE-002` | E25 | informar o coordinar | La municipalidad confirma un turno de licencia. Pide el DNI y la fecha de nacimiento (l. 4); PROTEGIDA duda (l. 5) y OTRA ofrece confirmarlo por la web. |
| `ENT-L-VENTAS-001` | E12 | ofrecer o vender | Oferta de un plan. Pide el DNI para cargar el cambio (l. 13); el código lo carga PROTEGIDA en la app (l. 17). |
| `ENT-L-VENTAS-002` | E45 | ofrecer o vender | Oferta de fibra. Pide nombre y DNI para la solicitud (l. 14); PROTEGIDA no da el DNI y OTRA la manda a la web. |
| `ENT-L-VENTAS-003` | E46 | ofrecer o vender | Oferta de un seguro. Confirma datos que ya tiene; no pide tarjeta (l. 21) y la alta la hace PROTEGIDA en el home banking (l. 25). |
| `ENT-L-VENTAS-004` | E13 | ofrecer o vender | Oferta que PROTEGIDA corta; pide que lo saquen de la base. |
| `ENT-L-VENTAS-005` | E26 | ofrecer o vender | Portabilidad que PROTEGIDA empezó en la web. Pide el DNI (l. 5); PROTEGIDA ofrece el PIN y OTRA no la deja (l. 15). |
| `ENT-L-VENTAS-006` | E14 | ofrecer o vender | Oferta de un pack. Ante la duda, OTRA la manda al 0800 de la factura (l. 14). |
| `ENT-L-VENTAS-007` | E15 | ofrecer o vender | La concesionaria, por una consulta de PROTEGIDA, precalifica un crédito: nombre, DNI e ingreso (l. 11). Se firma en el salón (l. 27). |
| `ENT-L-VENTAS-010` | E29 | ofrecer o vender | La moto que PROTEGIDA reservó llegó. Pide el DNI y el domicilio para el patentamiento (l. 8–10); el saldo se paga en caja. |
| `ENT-L-VENTAS-011` | E30 | ofrecer o vender | Una agencia ofrece un usado por una búsqueda de PROTEGIDA; coordinan una visita. |
| `ENT-L-VENTAS-012` | E31 | ofrecer o vender | Manda un folleto que PROTEGIDA pidió. |
| `LEG-CC-01` | E12 | ofrecer o vender | Oferta de un plan; manda las condiciones por mail. |
| `LEG-CC-02` | E13 | ofrecer o vender | Oferta que PROTEGIDA rechaza. |
| `LEG-CC-03` | E14 | ofrecer o vender | Oferta de un pack; ante la duda, la manda al 0800. |
| `LEG-CO-01` | E32 | informar o coordinar | El repartidor avisa que está a dos cuadras. |
| `LEG-CO-02` | E04 | informar o coordinar | El repartidor deja el pedido al encargado. |
| `LEG-CO-03` | E05 | informar o coordinar | El repartidor pide una referencia para llegar. |
| `LEG-EN-01` | E06 | preguntar una opinión | Encuesta de satisfacción de tres preguntas. |
| `LEG-EN-02` | E18 | preguntar una opinión | Encuesta anónima de transporte. |
| `LEG-EN-03` | E07 | preguntar una opinión | Encuesta que PROTEGIDA rechaza porque maneja. |
| `LEG-ST-01` | E23 | seguir una gestión de PROTEGIDA | Soporte por un reclamo de PROTEGIDA; agenda un técnico. |
| `LEG-ST-02` | E10 | seguir una gestión de PROTEGIDA | Service por una orden de PROTEGIDA; coordina la visita. |
| `LEG-ST-03` | E11 | seguir una gestión de PROTEGIDA | El local avisa que la notebook está lista; se paga en el mostrador. |
| `LEG-TU-01` | E08 | informar o coordinar | Confirma un turno médico. |
| `LEG-TU-02` | E09 | informar o coordinar | Reprograma un turno. |
| `LEG-TU-03` | E21 | informar o coordinar | Confirma un turno de laboratorio y recuerda el ayuno. |
| `LEG-VE-01` | E15 | ofrecer o vender | La concesionaria cuenta la financiación por una consulta de PROTEGIDA. |
| `LEG-VE-02` | E27 | ofrecer o vender | Oferta de un plan de ahorro que PROTEGIDA rechaza; la suscripción es en la oficina. |
| `LEG-VE-03` | E28 | ofrecer o vender | Tasación de un usado; la seña se hace en el salón. |
| `LEG2-CC-01` | E12 | ofrecer o vender | Oferta de un plan. Pide el DNI para cargarlo (l. 8); el código lo carga PROTEGIDA (l. 12). |
| `LEG2-CC-04` | E13 | ofrecer o vender | Oferta que PROTEGIDA corta; pide que lo saquen de la base. |
| `LEG2-CC-05` | E26 | ofrecer o vender | Portabilidad que PROTEGIDA empezó en la web. Pide el DNI (l. 6); el PIN lo carga ella (l. 10). |
| `LEG2-CC-06` | E14 | ofrecer o vender | Oferta de un pack; la manda al 0800. |
| `LEG2-CO-01` | E32 | informar o coordinar | El repartidor confirma la dirección y avisa que llega. |
| `LEG2-CO-02` | E04 | informar o coordinar | El repartidor deja el pedido al encargado; el DNI se lo pide a él (l. 6–8). |
| `LEG2-CO-03` | E05 | informar o coordinar | El repartidor pide una referencia para llegar. |
| `LEG2-CO-06` | E17 | informar o coordinar | El flete coordina la entrega. Pide el DNI del hermano para el remito (l. 10). |
| `LEG2-EN-01` | E06 | preguntar una opinión | Encuesta de satisfacción de tres preguntas. |
| `LEG2-EN-03` | E07 | preguntar una opinión | Encuesta que PROTEGIDA rechaza porque maneja. |
| `LEG2-EN-05` | E20 | preguntar una opinión | Encuesta municipal de residuos: calle y altura. |
| `LEG2-ST-02` | E10 | seguir una gestión de PROTEGIDA | Service por una orden de PROTEGIDA. Pide el DNI del titular de la factura (l. 6). |
| `LEG2-ST-03` | E11 | seguir una gestión de PROTEGIDA | El local avisa que la notebook está lista. Pide el DNI que dejó (l. 4). |
| `LEG2-ST-04` | E24 | seguir una gestión de PROTEGIDA | Coordina la instalación de un aire: dirección. |
| `LEG2-ST-05` | E47 | seguir una gestión de PROTEGIDA | Soporte por un ticket de PROTEGIDA: le manda un link para crear la contraseña. |
| `LEG2-TU-01` | E08 | informar o coordinar | Confirma un turno. Pide el DNI para la admisión (l. 6). |
| `LEG2-TU-02` | E09 | informar o coordinar | Reprograma un turno. |
| `LEG2-TU-05` | E22 | informar o coordinar | Recuerda el turno de una vacuna en la veterinaria. |
| `LEG2-TU-06` | E25 | informar o coordinar | La municipalidad confirma un turno de licencia. Pide el DNI y la fecha de nacimiento (l. 4): pide de más, pero con eso solo no se pierde nada. |
| `LEG2-VE-01` | E15 | ofrecer o vender | La concesionaria precalifica un crédito por una consulta de PROTEGIDA: nombre y DNI (l. 6). |
| `LEG2-VE-04` | E29 | ofrecer o vender | La moto que PROTEGIDA reservó llegó. Pide el DNI y confirma el domicilio (l. 6–8). |
| `LEG2-VE-05` | E30 | ofrecer o vender | Una agencia ofrece un usado por una búsqueda de PROTEGIDA. |
| `LEG2-VE-06` | E31 | ofrecer o vender | Manda un folleto que PROTEGIDA pidió. |

## Las que no representan bien llamadas reales

Ninguna es imposible. El problema es del conjunto: **son legítimas ejemplares.**

- **En 27 de las 94, OTRA hace seguridad por su cuenta.**
  - En 4, PROTEGIDA empieza a dictar un código y OTRA la frena: `ENT-L-BANCO-006`, `ENT-L-DELIVERY-005`, `ENT-L-SELECCION-002`, `ENT-L-VENTAS-005`.
  - En 16, OTRA aclara sin que nadie pregunte que un código o una clave no se comparten, o que no se paga
    por transferencia.
  - En 7, propone cortar y llamar al número oficial.

  Un banco puede abrir así. Un repartidor, una consultora o un vendedor, casi nunca. El riesgo es doble: el corpus no
  tiene **ninguna legítima que se porte mal** (que cobre con la tarjeta por teléfono, que pida el PIN de portabilidad),
  y enseña un atajo, «nombra un código y dice que no lo des: es legítima», que un estafador usa igual.
- **«El banco» pide el DNI en 10 de las 13 llamadas de banco** (entero en 8), y en 2 también la fecha de
  nacimiento antes de decir el motivo (`ENT-L-BANCO-001`, `LEG2-BA-01`). No se encontró ningún banco que diga que
  valida así cuando llama él; lo publicado es de cuando llama el cliente (S30, P08, P10), y Santander, Naranja X, BNA y
  BBVA dicen que no llaman para pedir «datos personales» (P07, P11, S31, S32). Son las llamadas legítimas más parecidas
  a una estafa, y por eso quedaron como tolerables.
- **El DNI aparece en 35 de las 94** (10 de advertir, 10 de ofrecer o vender, 6 de informar o coordinar, 6 de seguir una gestión de PROTEGIDA, 2 de preguntar una opinión, 1 de tomar datos). Que un
  turno, un reclamo o una venta lo pidan es verosímil, pero ninguna fuente lo documenta ni lo mide
  ([política, §3](POLITICA.md#3-el-dni)). El sesgo R29 sigue.
- **Las 94 son 47 situaciones.** Un mismo guion pesa hasta tres veces en las falsas alarmas.
- **Faltan llamadas enteras:**
  - las **cobranzas**, que son legítimas, insistentes, de números no agendados y piden plata (P09, P31);
  - una venta que **cierra por teléfono** con los datos de la tarjeta;
  - organismos (PAMI, ANSES, una obra social por un trámite), la escuela, un número equivocado y un familiar que llama
    desde otro teléfono.

  Las de otra intención, que son las que nunca deberían avisar, sí están: 28 de informar o coordinar, 26 de venta y 13
  encuestas.

## Las estafas, en una muestra

Se leyeron 8 de las 46: las 6 cuyo pedido es de datos personales y 2 sin pedido. No se leyeron las de código o clave,
para que los textos de las variantes no salgan de su redacción.

- **Las 6 de datos personales piden más que el número.** Dos piden el DNI con una foto (`PREMIO-001` y `-003`), una el
  DNI, la fecha de nacimiento y fotos del frente y el dorso (`ORGANISMO_PREVISIONAL-001`), una el **número de trámite**
  (`-004`), una los dígitos que faltan del DNI (`-003`) y una sola pide solo datos de identidad: el CUIL y la fecha de
  nacimiento (`-002`).
- **En las 6, el pretexto es plata o un trámite que la persona no pidió:** un ajuste a favor, una devolución de
  aportes, un premio. Es lo que separa a `ORGANISMO_PREVISIONAL-002` de `ENT-L-SELECCION-003`, que pide lo mismo para
  un alta laboral que la persona reconoce. Va con «juzgarlo según el pretexto».
- **Las dos sin pedido** (`BANCO-011` y `ORGANISMO_PREVISIONAL-005`) no piden nada: insisten en que no corte. Avisar ahí
  es avisar por la maniobra, y está bien.
- **Son realistas en el arco y raras en el detalle:** nombres de organismos inventados y genéricos («sector de
  actualización de beneficiarios»), y una PROTEGIDA que casi siempre termina cortando para verificar. De las 36 con
  pedido, solo 15 tienen cumplimiento.
