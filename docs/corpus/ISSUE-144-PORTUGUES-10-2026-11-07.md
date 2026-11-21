# Issue #144 — portugués: 10 grupos más de PIX Scam BR

Fecha: 2026-11-07. Archivo local, fuera de Git.

**Para qué es.** Igual que en inglés: lo que se lee y se marca con ficha va al **test** de #144 (decisión de Luciano del 2026-11-07). No hay observaciones de IA sobre pedidos ni sobre la clase.

**Fuente.** [ai-safety-brazil/pix-scam-challenge-br-synthetic](https://huggingface.co/datasets/ai-safety-brazil/pix-scam-challenge-br-synthetic), revisión `acdc964b67fea50300fa82033af2ca9db86fbe4d`, v1.0.0. Licencia CC BY 4.0, atribución a AI Safety Brazil; esta traducción es un cambio sobre el original. Es **100 % sintético** (lo generó Qwen y lo filtró otro modelo, sin revisión humana).

**Cómo se eligieron.** Cada grupo de la fuente es un mismo diálogo corto (4 a 6 turnos) con tres evidencias externas distintas, y según la evidencia cambia la clase. Solo 22 de los 1.000 grupos describen una **llamada telefónica** en su contexto; el resto son chats. Se tomaron esos 22, sin contar los dos que ya están en `ISSUE-144-PORTUGUES-2026-11-06.md`, y se sortearon 10 con `random.Random(144)`, alternando familias. Por eso salieron 8 de contacto bancario, 1 familiar y 1 de intermediario de venta. Los diálogos de banco se parecen mucho entre sí: la fuente los generó con el mismo molde.

**Cómo está traducido.** Traducción fiel al español, sin argentinizar, hecha por Claude (Opus 5.5) el 2026-11-07, sin revisión bilingüe humana. `A` = quien llama o pide (*pessoa_a*), `B` = quien atiende (*pessoa_b*). Se dejan como están los identificadores ficticios (`CONTA_LUA`, `CONTA_SOL`…), Pix y CPF.

**La clase está oculta.** Las tres evidencias de cada grupo aparecen como V1, V2 y V3, ordenadas por su identificador en la fuente y no por clase. La clase de la fuente está aparte, en `ISSUE-144-PORTUGUES-10-CLAVE-2026-11-07.json`: no abrirla hasta haber llenado las fichas. El detector solo va a escuchar la conversación, sin la evidencia; por eso la ficha pregunta las dos cosas.

| Caso | Familia en la fuente | Grupo | Turnos |
|---|---|---|---|
| PT-01 | contacto bancario | `bc83da504309cb30101a6eef` | 6 |
| PT-02 | identidad familiar | `42d44eeaa8a98fb26c207b43` | 6 |
| PT-03 | intermediario de venta | `03cd8c1826520cd63fe24152` | 5 |
| PT-04 | contacto bancario | `1a5c27287a27dcee1ac30849` | 6 |
| PT-05 | contacto bancario | `ff00032f9de0fdced31ec1c0` | 5 |
| PT-06 | contacto bancario | `234608bb717a87524bf79240` | 6 |
| PT-07 | contacto bancario | `46db3b007d1678bab0d6a9ab` | 6 |
| PT-08 | contacto bancario | `971f3fde14907d0ef6a65abb` | 6 |
| PT-09 | contacto bancario | `5763e6a6bfaa31ea5b3f31b2` | 6 |
| PT-10 | contacto bancario | `fe11f507646a5ee749f57779` | 6 |

---

## PT-01 · Contacto bancario

**Contexto de la fuente:** B recibió una llamada de A, que dijo ser empleado del banco por una transacción Pix sospechosa de R$ 4.500,00. B negó haberla autorizado. A le indicó bloquearla desde la app oficial y le dio el protocolo. La conversación fue por teléfono. No consta que B haya verificado el teléfono oficial del banco ni el perfil de A en la plataforma digital del banco antes o durante la llamada.

1. **A:** Hola, le hablo de la central de riesgos del Banco Nova. Detectamos un intento de Pix de 4.500 a CONTA_LUA hace un momento. ¿Usted lo autorizó?
2. **B:** ¡No! Si hoy ni compré nada. Tengo el saldo completo. ¿Qué está pasando? Tengo que bloquear esto ya, si no pierdo el dinero.
3. **A:** Entendido. Para evitar el débito necesito validar su identidad. Por favor, entre a la app oficial y confirme el bloqueo en la pestaña de seguridad. Yo no lo puedo hacer por el chat.
4. **B:** Bien, ya abrí la app. ¿Pero usted qué hizo? ¿Cómo supo que era CONTA_LUA? Páseme el protocolo para verificarlo después.
5. **A:** El protocolo es 99887. La operación está en estado «pendiente» en el sistema. Si usted confirma el bloqueo en la app, la transacción se revierte automáticamente.
6. **B:** Ya hice el bloqueo. El saldo no salió. Pero usted dijo que la transacción iba a CONTA_LUA. ¿Cómo sé que no es una estafa? Dígame el nombre completo del beneficiario.

**Evidencias externas (cada una por separado):**

- **V1:** B no hizo ninguna consulta externa al banco (teléfono oficial, app o sucursal) para verificar la autenticidad del protocolo 99887 ni la existencia de la transacción pendiente; dependió solo de lo que dijo A.
- **V2:** La consulta en el canal oficial de reclamos del banco confirma que existe el protocolo 99887, registrado a la hora de la llamada y vinculado a un intento de transacción bloqueado con éxito en la cuenta de B.
- **V3:** El sistema interno del banco, consultado por B después de la llamada, no registra ningún pedido de soporte de riesgos abierto con el protocolo 99887 ni ningún intento de transacción pendiente en la cuenta de B a la hora indicada.

### Ficha PT-01

- Conservar / descartar / revisar:
- ¿Es creíble como llamada? (sí / dudosa / no) y por qué:
- Con solo la conversación, sin evidencia, ¿es estafa? (sí / no / dudoso):
- Clase con cada evidencia (estafa / legítima / no alcanza) — V1: · V2: · V3:
- ¿En qué turno una persona atenta ya sospecharía?:
- Primer pedido de alto riesgo (turno, `T_R`):
- Primer cumplimiento (turno, `T_C`):
- ¿Se distinguen bien los hablantes?:
- Equivalente local (familia del catálogo):
- Dudas o ambigüedades:
- Decisión y motivo:

---

## PT-02 · Identidad familiar

**Contexto de la fuente:** B recibió una llamada de A, que dice ser su nieta Clara. Clara le pide un pago inmediato por Pix a un proveedor de servicios de limpieza, alegando urgencia y una falla en el sistema de la empresa. B duda y pide datos concretos para validar la identidad y la transacción.

1. **A:** ¡Hola, tía! ¿Me escuchas? Necesito un favor urgente: se colgó el sistema de la empresa y tengo que pagarle a un proveedor ahora.
2. **B:** ¿Clara? ¡Qué susto! ¿Está todo bien? Dime, pero explícame rápido qué pasó, que estoy algo preocupada.
3. **A:** ¡Sí, soy yo! Es el proveedor de limpieza: la cuenta venció y no liberan el servicio si no se paga antes de las 14. ¿Me haces el Pix?
4. **B:** Espera, mi nieta. Tú nunca me llamas a esta hora. Dime el nombre completo del proveedor y el monto exacto.
5. **A:** Es Limpeza Rápida, CNPJ 12.345, por R$ 850,00. Tía, por favor, tarda en llegar al banco, mándame la clave ahora.
6. **B:** Bueno, lo voy a revisar en mi agenda. ¿Me confirmas si la clave Pix es la de siempre o si cambió este mes?

`[en la fuente: B llama «tía» a quien dice ser su nieta; se deja como está]`

**Evidencias externas (cada una por separado):**

- **V1:** La clave Pix que dio A coincide exactamente con los datos registrados de la empresa Limpeza Rápida, que figura como habilitada hace años en la agenda de B.
- **V2:** B no reconoce de inmediato la clave Pix que dio A y no puede cruzar los datos con sus registros sin conexión durante la llamada.
- **V3:** La clave Pix que dio A corresponde a una cuenta bancaria vinculada a un nombre desconocido, distinto del CNPJ de la empresa de limpieza y de cualquier contacto conocido de B.

### Ficha PT-02

- Conservar / descartar / revisar:
- ¿Es creíble como llamada? (sí / dudosa / no) y por qué:
- Con solo la conversación, sin evidencia, ¿es estafa? (sí / no / dudoso):
- Clase con cada evidencia (estafa / legítima / no alcanza) — V1: · V2: · V3:
- ¿En qué turno una persona atenta ya sospecharía?:
- Primer pedido de alto riesgo (turno, `T_R`):
- Primer cumplimiento (turno, `T_C`):
- ¿Se distinguen bien los hablantes?:
- Equivalente local (familia del catálogo):
- Dudas o ambigüedades:
- Decisión y motivo:

---

## PT-03 · Intermediario de venta

**Contexto de la fuente:** Intermediario de venta de equipos industriales. El comprador (B) y el vendedor (A) cerraron la negociación por teléfono. El contrato inicial preveía el pago por clave Pix vinculada directamente al CPF/CNPJ del vendedor (CONTA_SOL). Al momento del pago, el vendedor pide desviarlo a una cuenta de terceros (CONTA_LUA), alegando un bloqueo técnico. El comprador exige identificar la cuenta nueva para validar el desvío, pero el vendedor se niega a dar datos formales y solo afirma de palabra que la cuenta es de su «socia».

`[no queda claro si la conversación misma es por teléfono: el contexto dice que la negociación se cerró por teléfono]`

1. **A:** Hola, gracias por la confianza. El lote está reservado. Para liberar la entrega urgente, necesito que el Pix caiga en la cuenta de mi socia, la CONTA_LUA. Es la misma estructura que la venta anterior.
2. **B:** Bien, ¿pero por qué cambió la clave? En la conversación anterior fue directo a CONTA_SOL, que es tuya. Quiero evitar trámites, mándame la clave de la CONTA_LUA ya.
3. **A:** La CONTA_SOL está hoy en bloqueo administrativo, no hay forma. La CONTA_LUA es para cobros operativos del equipo. Es la misma empresa, solo cambió el destino del flujo. Confía, el producto sale hoy.
4. **B:** Me cuesta confiar en este cambio de último momento. Confírmame el CNPJ o el nombre completo de la dueña de la CONTA_LUA para cotejarlo con el contrato antes de darle a enviar.
5. **A:** No tengo tiempo para trámites ahora, el camión está esperando. Es solo una cuenta intermediaria de mi socia. Si no lo mandas ahora, pierdo el flete. Es la misma persona jurídica.

**Evidencias externas (cada una por separado):**

- **V1:** La consulta al registro público no devuelve datos actualizados sobre la CONTA_LUA, y el vendedor se niega a mandar el contrato firmado o un comprobante del vínculo societario, así que la titularidad sigue siendo ambigua.
- **V2:** La consulta al registro público muestra que la CONTA_LUA está vinculada al mismo CNPJ del vendedor, con la socia registrada como titular autorizada en las reglas de pago de la empresa.
- **V3:** La consulta al registro público muestra que la CONTA_LUA está vinculada a un CNPJ inactivo y sin relación societaria comprobada con el vendedor, y que el titular de la cuenta es ajeno al negocio.

### Ficha PT-03

- Conservar / descartar / revisar:
- ¿Es creíble como llamada? (sí / dudosa / no) y por qué:
- Con solo la conversación, sin evidencia, ¿es estafa? (sí / no / dudoso):
- Clase con cada evidencia (estafa / legítima / no alcanza) — V1: · V2: · V3:
- ¿En qué turno una persona atenta ya sospecharía?:
- Primer pedido de alto riesgo (turno, `T_R`):
- Primer cumplimiento (turno, `T_C`):
- ¿Se distinguen bien los hablantes?:
- Equivalente local (familia del catálogo):
- Dudas o ambigüedades:
- Decisión y motivo:

---

## PT-04 · Contacto bancario

**Contexto de la fuente:** B recibió una llamada de un número desconocido que se identificó como seguridad del banco. Quien llamaba alegó fraude en una transacción Pix y pidió acceso por un enlace externo. B revisó la app oficial del banco y no encontró ninguna notificación de alerta ni transacción pendiente que coincidiera con lo que describía quien llamaba. El enlace enviado por SMS pedía volver a autenticarse por completo.

1. **A:** Hola, le hablo del sector de seguridad del Banco Nova. Detectamos una transacción sospechosa de R$ 1.200 a CONTASOL. ¿La confirmamos?
2. **B:** ¡Ay, no hice esa compra! Tengo que cancelarla ya o me dejan el saldo en cero. Es Pix, ¿no?
3. **A:** Sí, es Pix. Para revertirla necesito que entre a la app y valide su identidad en el enlace seguro que le acabo de enviar.
4. **B:** Bien, ya estoy en la app, pero no aparece ninguna alerta de seguridad. Solo está la pantalla de transferencias.
5. **A:** Puede ser la caché. Haga clic en el enlace que le mandé por SMS. Es obligatorio para bloquear el pago.
6. **B:** Voy a hacer clic... pero el enlace me pide que vuelva a cargar mi contraseña de acceso. Qué raro.

**Evidencias externas (cada una por separado):**

- **V1:** No se pudo verificar la autenticidad del dominio del enlace enviado, ni confirmar si la falta de alerta en la app se debió a una demora de sincronización o a notificaciones bloqueadas por el usuario; faltan datos para distinguir entre error técnico y fraude.
- **V2:** El enlace enviado es del dominio oficial del banco, y el pedido de volver a autenticarse solo ocurre cuando el sistema de seguridad detecta una falla de sesión durante un intento de bloqueo de emergencia por un canal alternativo.
- **V3:** El enlace enviado por SMS lleva a un dominio externo que no pertenece al banco y pide ingresar la contraseña de acceso principal, una práctica incompatible con los protocolos oficiales de seguridad, que solo usan notificaciones *push* en la app.

### Ficha PT-04

- Conservar / descartar / revisar:
- ¿Es creíble como llamada? (sí / dudosa / no) y por qué:
- Con solo la conversación, sin evidencia, ¿es estafa? (sí / no / dudoso):
- Clase con cada evidencia (estafa / legítima / no alcanza) — V1: · V2: · V3:
- ¿En qué turno una persona atenta ya sospecharía?:
- Primer pedido de alto riesgo (turno, `T_R`):
- Primer cumplimiento (turno, `T_C`):
- ¿Se distinguen bien los hablantes?:
- Equivalente local (familia del catálogo):
- Dudas o ambigüedades:
- Decisión y motivo:

---

## PT-05 · Contacto bancario

**Contexto de la fuente:** B recibió una llamada de un número registrado como «+55 11 9XXXX-XXXX», que A identificó como del «Banco Delta». A tiene un tono urgente y presionante. B se mostró escéptica y pidió verificar internamente antes de dar cualquier dato. B no verificó durante la conversación que el número fuera oficial. Hasta el momento de la verificación no hay intentos de extracción registrados en la app de B.

1. **A:** Hola, le hablo de soporte del Banco Delta. Detectamos un intento de retiro no autorizado en su cuenta CONTA_ZEBRA. Para bloquearlo necesito que me confirme el código que le acabo de enviar por SMS.
2. **B:** ¡Ay, qué susto! Estaba por pagar el alquiler. ¿De cuánto fue el intento? Quiero estar segura antes de pasarle el código.
3. **A:** Fue de R$ 2.500,00 a una cuenta en la CONTA_FURACAO. El código es 8842. La rapidez es clave, si no el dinero sale. ¿Me confirma el código ahora mismo?
4. **B:** Espere, nunca oí hablar de esa CONTA_FURACAO. Primero lo voy a revisar en la app del banco. Deme un minutito para mirar mis movimientos.
5. **A:** No hay tiempo, el sistema se va a bloquear si tarda. Escriba el código 8842 ahora o autorice el bloqueo manual por el chat oficial. Elija rápido, ¿sí?

**Evidencias externas (cada una por separado):**

- **V1:** Al revisar la app oficial del banco, el número «+55 11 9XXXX-XXXX» aparece entre los contactos autorizados de atención al cliente del Banco Delta, y hay una alerta de seguridad pendiente justo por R$ 2.500,00 asociada a la CONTA_FURACAO.
- **V2:** Al revisar la app oficial del banco, B ve que el origen de la llamada no corresponde a ningún canal oficial registrado, y el número «+55 11 9XXXX-XXXX» está en una lista de denuncias recientes de suplantación (*spoofing*) de entidades financieras.
- **V3:** B intenta llamar al número oficial del Banco Delta, pero la línea está ocupada o fuera de servicio. La app del banco no muestra alertas de seguridad, pero tampoco confirma que el número de la llamada sea oficial, así que el origen de la llamada sigue sin conocerse.

### Ficha PT-05

- Conservar / descartar / revisar:
- ¿Es creíble como llamada? (sí / dudosa / no) y por qué:
- Con solo la conversación, sin evidencia, ¿es estafa? (sí / no / dudoso):
- Clase con cada evidencia (estafa / legítima / no alcanza) — V1: · V2: · V3:
- ¿En qué turno una persona atenta ya sospecharía?:
- Primer pedido de alto riesgo (turno, `T_R`):
- Primer cumplimiento (turno, `T_C`):
- ¿Se distinguen bien los hablantes?:
- Equivalente local (familia del catálogo):
- Dudas o ambigüedades:
- Decisión y motivo:

---

## PT-06 · Contacto bancario

**Contexto de la fuente:** B recibió una llamada de A, que dice ser del Banco Nova. A alega fraude en la cuenta CONTA_LUA y pide un Pix inmediato a CONTA_SOL. B no ve alertas en la app oficial y cuestiona la lógica del pedido. La conversación es por teléfono, sin envío de enlaces ni adjuntos. No hay ningún ticket abierto por B antes de la llamada. El monto pedido es R$ 1.500,00.

1. **A:** Hola, le hablo de soporte del Banco Nova. Vi que su cuenta CONTA_LUA tuvo una operación sospechosa de R$ 1.500,00. Necesito que haga el Pix a CONTA_SOL ahora para congelar el saldo.
2. **B:** Eh, yo no hice ese Pix. En la app está todo tranquilo. ¿Por qué tengo que mover el dinero otra vez? No tiene sentido.
3. **A:** Es un procedimiento de seguridad, amigo. El sistema lo bloqueó porque parece fraude. Si no transfiere ahora, pierde la protección. Es urgente.
4. **B:** Entiendo... pero la app no muestra ninguna alerta de bloqueo. Solo vi el débito ya hecho. Voy a ver si hay algún mensaje ahí.
5. **A:** La app a veces tarda en actualizarse. Confíe en mí, es el nuevo estándar de seguridad. Haga el Pix a CONTA_SOL y me avisa.
6. **B:** Bueno, voy a tratar de ver el número de referencia que piden. Pero si da error, lo vuelvo a llamar.

**Evidencias externas (cada una por separado):**

- **V1:** B no pudo entrar a la app durante la llamada por problemas de conexión y, al terminar, no verificó si había alguna alerta de seguridad o instrucción oficial en la app sobre transferencias por seguridad.
- **V2:** Al consultar la app oficial del Banco Nova, B verifica que no hay ningún pedido de activación de seguridad que exija transferir fondos a otra cuenta, y que el número de la llamada no corresponde a la central de atención registrada en el banco.
- **V3:** Al consultar la app oficial del Banco Nova, B encuentra una alerta activa de «Verificación de seguridad pendiente» que indica explícitamente hacer una transferencia de prueba a una cuenta designada por el sistema, y el número de la llamada figura como canal oficial de atención.

### Ficha PT-06

- Conservar / descartar / revisar:
- ¿Es creíble como llamada? (sí / dudosa / no) y por qué:
- Con solo la conversación, sin evidencia, ¿es estafa? (sí / no / dudoso):
- Clase con cada evidencia (estafa / legítima / no alcanza) — V1: · V2: · V3:
- ¿En qué turno una persona atenta ya sospecharía?:
- Primer pedido de alto riesgo (turno, `T_R`):
- Primer cumplimiento (turno, `T_C`):
- ¿Se distinguen bien los hablantes?:
- Equivalente local (familia del catálogo):
- Dudas o ambigüedades:
- Decisión y motivo:

---

## PT-07 · Contacto bancario

**Contexto de la fuente:** B recibió una llamada de un número no agendado, que A identificó como soporte del banco. A pidió una transferencia Pix inmediata a CONTA_SOL como condición para bloquear un supuesto fraude en la CONTA_LUA. B hizo la transferencia sin verificar la identidad del supuesto operador por canales oficiales.

1. **A:** Hola, le hablo de soporte de su banco. Detectamos un intento de retiro no autorizado en su CONTA_LUA. Tenemos que bloquearlo ahora para evitar perjuicios.
2. **B:** ¡Qué miedo! Si ni estaba usando la app. ¿Qué tengo que hacer? Dígame rápido que lo hago aquí.
3. **A:** Rápido, por favor. Para revertirlo tiene que confirmar una transferencia de reversión de R$ 1.500,00 a la CONTA_SOL. Es el mismo monto del intento sospechoso.
4. **B:** Bueno, tranquilo. ¿Abro la app y hago la transferencia a esa CONTA_SOL ahora mismo?
5. **A:** Exacto. Solo confirme el pago por Pix. Apenas se acredite, nuestro sistema libera el bloqueo de su cuenta automáticamente.
6. **B:** Listo. Ya la mandé. La transferencia se aprobó. ¿Y ahora qué pasa?

**Evidencias externas (cada una por separado):**

- **V1:** La transferencia se hizo a la CONTA_SOL, pero en el contexto no hay información verificable sobre la titularidad o el vínculo institucional de esa cuenta, así que no se puede confirmar si es una cuenta oficial o de terceros.
- **V2:** La transferencia que hizo B fue a la CONTA_SOL, que no tiene vínculo oficial con la CONTA_LUA ni con entidades financieras conocidas: es un desvío de fondos a una cuenta de terceros no vinculada.
- **V3:** La transferencia que hizo B fue a la CONTA_SOL, que es una cuenta interna de conciliación financiera registrada oficialmente a nombre de la misma entidad bancaria que administra la CONTA_LUA, según el sistema de pagos.

### Ficha PT-07

- Conservar / descartar / revisar:
- ¿Es creíble como llamada? (sí / dudosa / no) y por qué:
- Con solo la conversación, sin evidencia, ¿es estafa? (sí / no / dudoso):
- Clase con cada evidencia (estafa / legítima / no alcanza) — V1: · V2: · V3:
- ¿En qué turno una persona atenta ya sospecharía?:
- Primer pedido de alto riesgo (turno, `T_R`):
- Primer cumplimiento (turno, `T_C`):
- ¿Se distinguen bien los hablantes?:
- Equivalente local (familia del catálogo):
- Dudas o ambigüedades:
- Decisión y motivo:

---

## PT-08 · Contacto bancario

**Contexto de la fuente:** La conversación fue por llamada de voz. Quien llamaba se identificó como soporte técnico del Banco Neon. El tono fue urgente y pidió datos vinculados a la clave Pix. El usuario dudó al principio, pero al final pidió verificar por canales oficiales. No se mencionaron contraseñas numéricas ni tokens de la app.

1. **A:** Hola, le hablo de soporte del Banco Neon. Detectamos una transacción sospechosa en su cuenta. Para bloquear el retiro no autorizado necesito que me confirme los últimos dígitos de su clave Pix.
2. **B:** ¡Ah, qué bueno que llamaron! Estaba por hacer un pago grande. ¿De cuánto es la transacción sospechosa? Quiero saber si es la que hice hace un rato.
3. **A:** El monto no importa ahora, lo importante es la seguridad. Por favor, escriba la clave Pix de destino que registró en la última compra, así valido el origen.
4. **B:** Bueno, pero no puedo pasar datos sensibles por teléfono. ¿Cómo sé que usted es realmente del banco? ¿Tienen un número de protocolo?
5. **A:** El protocolo se está generando ahora. Pero la urgencia es esta: si no confirma, la transacción puede aprobarse y vamos a perder el plazo para revertirla. Escriba la clave ahora.
6. **B:** Entiendo. Voy a revisar la app del banco a ver si está esa notificación. Espéreme un minuto que miro el historial oficial.

**Evidencias externas (cada una por separado):**

- **V1:** Al consultar el historial de atención en la app oficial del Banco Neon, el usuario no encuentra ningún registro de atención reciente, y la clave Pix pedida corresponde a una cuenta extranjera que no está entre sus destinatarios frecuentes.
- **V2:** La app oficial del Banco Neon muestra un caso activo con el mismo número de protocolo que dio el operador, y la transacción sospechosa del historial coincide exactamente con el monto y la hora de la compra que el usuario estaba por hacer.
- **V3:** La app del banco muestra una notificación de intento de transacción, pero no hay ningún registro de atención telefónica asociado, y el usuario todavía no confirmó si la clave pedida es la misma de la transacción pendiente.

### Ficha PT-08

- Conservar / descartar / revisar:
- ¿Es creíble como llamada? (sí / dudosa / no) y por qué:
- Con solo la conversación, sin evidencia, ¿es estafa? (sí / no / dudoso):
- Clase con cada evidencia (estafa / legítima / no alcanza) — V1: · V2: · V3:
- ¿En qué turno una persona atenta ya sospecharía?:
- Primer pedido de alto riesgo (turno, `T_R`):
- Primer cumplimiento (turno, `T_C`):
- ¿Se distinguen bien los hablantes?:
- Equivalente local (familia del catálogo):
- Dudas o ambigüedades:
- Decisión y motivo:

---

## PT-09 · Contacto bancario

**Contexto de la fuente:** B recibió una llamada de un número no agendado que decía ser del banco. El pedido es confirmar un Pix de R$ 2.500,00 a CONTA_LUA con el argumento de bloquear un fraude. B duda y pide una verificación independiente. El usuario no verificó antes de la conversación que el número de origen fuera oficial.

1. **A:** Hola, le hablo de la central del banco. Detectamos una transacción sospechosa en su cuenta. Para bloquear el retiro no autorizado necesito que confirme ahora mismo el Pix de R$ 2.500,00 a la cuenta CONTA_LUA. Es urgente.
2. **B:** ¡Ay, qué susto! Yo no hice ese retiro. Pero espere, ¿por qué tiene que ir a la CONTA_LUA? ¿Por qué no a una cuenta del propio banco o del cliente?
3. **A:** Es el procedimiento estándar de recuperación de activos. La CONTA_LUA es una cuenta de custodia temporal segura. Si no confirma ahora, el dinero sale al exterior y no hay vuelta atrás. Ingrese el código 8821.
4. **B:** Espere, un amigo me dijo que las cuentas de custodia tienen otros nombres. Primero lo voy a revisar en la app oficial. ¿Cuál es el nombre exacto del beneficiario en el comprobante?
5. **A:** Por seguridad no tengo acceso al nombre completo. Solo ingrese el código en la app, aparece como «Transferencia Bancaria Segura». No pierda tiempo, se está acabando el plazo.
6. **B:** Lo voy a consultar con el gerente. Si es real, lo vuelvo a llamar. Pero no voy a ingresar nada sin ver el destinatario en mi aplicación.

**Evidencias externas (cada una por separado):**

- **V1:** La verificación en la app oficial muestra que CONTA_LUA es una cuenta personal de un tercero desconocido, con un historial reciente de transferencias sospechosas, y el banco no usa cuentas de personas físicas para custodiar fondos en casos de fraude.
- **V2:** La verificación en la app oficial confirma que CONTA_LUA es una cuenta institucional interna del banco, rotulada correctamente como «Custodia de Activos Recuperación», y el número de la llamada coincide con la central oficial registrada.
- **V3:** B todavía no entró a la app oficial para verificar el destinatario CONTA_LUA, y la identidad de quien llamó no se confirmó por canales oficiales secundarios antes de decidir.

### Ficha PT-09

- Conservar / descartar / revisar:
- ¿Es creíble como llamada? (sí / dudosa / no) y por qué:
- Con solo la conversación, sin evidencia, ¿es estafa? (sí / no / dudoso):
- Clase con cada evidencia (estafa / legítima / no alcanza) — V1: · V2: · V3:
- ¿En qué turno una persona atenta ya sospecharía?:
- Primer pedido de alto riesgo (turno, `T_R`):
- Primer cumplimiento (turno, `T_C`):
- ¿Se distinguen bien los hablantes?:
- Equivalente local (familia del catálogo):
- Dudas o ambigüedades:
- Decisión y motivo:

---

## PT-10 · Contacto bancario

**Contexto de la fuente:** B recibió una llamada de una «Central de Riesgos». El monto del Pix no coincide con el pago que B quería hacer. Quien llama pide una acción inmediata por un enlace externo y la contraseña.

1. **A:** Hola, le hablo de la Central de Riesgos del Banco Nova. Detectamos un intento de Pix de R$ 1.200,00 a CONTA_LUA. ¿Usted lo autorizó?
2. **B:** ¡Uy, no! Estaba pagando la luz, pero ese monto está mal. ¿Qué pasó?
3. **A:** El sistema falló y lo redirigió a una cuenta externa. Para revertirlo necesito que confirme si el beneficiario es desconocido. Si es así, lo bloqueo de inmediato.
4. **B:** ¡Sí, es desconocido! Necesito que lo detengan ya, si no el dinero desaparece. ¿Cómo hago el bloqueo?
5. **A:** Le voy a generar un enlace de seguridad en su app. Haga clic ahí y escriba su contraseña de 6 dígitos para activar el bloqueo.
6. **B:** Bueno, lo hago. ¿Pero por qué piden la contraseña? ¿No tenía que ser solo en la app?

**Evidencias externas (cada una por separado):**

- **V1:** Quien llamaba informó que el bloqueo lo haría directamente el sistema interno de la aplicación, sin necesidad de compartir contraseñas ni hacer clic en enlaces externos.
- **V2:** Quien llamaba pidió ingresar la contraseña de acceso en un enlace enviado por mensaje, en contra de la política habitual de que las contraseñas nunca se comparten por canales externos.
- **V3:** Quien llamaba mencionó que el bloqueo se haría desde la aplicación oficial, pero no especificó si haría falta alguna acción fuera de la app, así que el método queda ambiguo.

### Ficha PT-10

- Conservar / descartar / revisar:
- ¿Es creíble como llamada? (sí / dudosa / no) y por qué:
- Con solo la conversación, sin evidencia, ¿es estafa? (sí / no / dudoso):
- Clase con cada evidencia (estafa / legítima / no alcanza) — V1: · V2: · V3:
- ¿En qué turno una persona atenta ya sospecharía?:
- Primer pedido de alto riesgo (turno, `T_R`):
- Primer cumplimiento (turno, `T_C`):
- ¿Se distinguen bien los hablantes?:
- Equivalente local (familia del catálogo):
- Dudas o ambigüedades:
- Decisión y motivo:
