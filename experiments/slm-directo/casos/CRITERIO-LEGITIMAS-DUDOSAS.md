# Criterio de «legítima dudosa» para el corpus de desarrollo

Fecha: 2026-11-09. Lo preparó un agente a pedido de Mateo Antenucci, para decidir antes de la próxima corrida de
[#143](https://github.com/Corchets/bitacora_tesis/issues/143) cómo se cuentan las legítimas poco creíbles
([`PROPUESTA-SIGUIENTE.md`](../corridas/2026-11-07_alcance-etapa-2/PROPUESTA-SIGUIENTE.md) §3.5, sin commitear).

> **Estado: propuesta sin discutir.** El criterio lo adopta o lo cambia el equipo. La credibilidad de una llamada es un
> juicio humano ([#145](https://github.com/Corchets/bitacora_tesis/issues/145)): esto solo marca lo que las fuentes
> externas dicen que una entidad real no hace por teléfono. **No se borra ningún caso:** las dudosas se informan aparte.

## Para qué

Las 94 legítimas de desarrollo las escribió un generador. Si alguna hace algo que un banco o un organismo real no hace
por teléfono, enseña al detector que eso es normal y le cobra una falsa alarma por avisar bien. Una **legítima dudosa**
es una llamada marcada como legítima en la que quien habla por una entidad hace algo que, según las fuentes de abajo,
una entidad real no hace en una llamada.

## Orden en que se escribió

1. **Este criterio se escribió el 2026-11-09, antes de mirar qué legítimas tuvieron falsa alarma** en la etapa 2 o en
   cualquier corrida. Quien lo escribió no abrió ninguna salida de detector por caso antes de aplicarlo.
2. **Lo que sí sabía:** las cifras agregadas de la etapa 2 que trae la propuesta (las 64 legítimas que piden datos
   personales tienen 39 FA con v4 y 21 con C; las 30 que no piden datos, 3 y 6), que el guion de TecnoFix aparece tres
   veces y da tres FA, y que C da 0,3 en la primera línea de 5 de 13 legítimas de banco y de 4 de 13 de soporte. También
   leyó el campo `situacion` de las 94 referencias al armar los [escenarios](ESCENARIOS-LEGITIMAS-DESARROLLO.md).
3. **Por eso no lo aplicó él.** Lo aplicaron dos agentes nuevos que solo recibieron este criterio y las 94
   transcripciones renombradas y mezcladas (sección «Cómo se aplicó»).

## Fuentes

Consultadas el 2026-11-09. Las citas son textuales.

| Id | Fuente | Fecha | Qué dice |
|---|---|---|---|
| F1 | BCRA, [Recomendaciones del BCRA para evitar estafas virtuales](https://www.bcra.gob.ar/noticias/recomendaciones-del-bcra-para-evitar-estafas-virtuales/) | 2025-08-06 | «Los bancos y organismos públicos nunca solicitan la modificación de datos personales o claves, ni la entrega de códigos de verificación recibidos por ningún medio». Si alguien llama y dice ser del banco, no operar con el cajero, la app ni el home banking mientras dure la llamada: cortar y verificar por los canales oficiales. El BCRA mismo «nunca se comunica directamente con clientes bancarios para solicitar datos personales o bancarios». |
| F2 | BCRA, [El Banco Central recuerda 10 recomendaciones para prevenir estafas virtuales](https://www.bcra.gob.ar/noticias/el-banco-central-recuerda-10-recomendaciones-para-prevenir-estafas-virtuales/) | 2021-03-21 | Ante una llamada que dice ser del banco, «nunca se debe acudir a un cajero automático, abrir la app o acceder al home banking». No brindar datos personales, entre ellos «usuarios, claves, contraseñas, pin, Clave de la Seguridad Social, Clave Token». |
| F3 | Banco de la Nación Argentina, [Información de seguridad](https://www.bna.com.ar/Home/InformacionDeSeguridad) | sin fecha | «Nunca te contactaremos por redes sociales, mensajes o llamadas para pedirte datos personales», ni para guiarte a hacer acciones en tu cuenta. No informar la clave «incluso si quien lo solicita se identifica como personal del banco». |
| F4 | Banco de la Nación Argentina, [Proteja sus datos (tarjetas)](https://www.bna.com.ar/Personas/TarjetasDeCredito/ProtejaSusDatos) | sin fecha | El banco «nunca le solicitará información relacionada con sus tarjetas (débito/crédito), códigos de seguridad y/o claves». «Sea precavido con las llamadas o correos no solicitados.» |
| F5 | Banco Provincia, [Llamados y mensajes](https://www.bancoprovincia.com.ar/web/cs_llamados_y_mensajes) | sin fecha | El banco no pide «usuarios, claves, token, códigos de seguridad, datos de tarjetas» ni transferencias por teléfono, mensajes, llamadas o videollamadas, y «nunca te va a solicitar instalar aplicaciones distintas a Cuenta DNI o BIP Móvil». |
| F6 | Banco Provincia, [Ventas telefónicas](https://www.bancoprovincia.com.ar/web/cs_ventas_telefonicas) | sin fecha | El banco «nunca te solicitará datos sensibles ni te pedirá que realices operaciones inusuales». |
| F7 | BBVA Argentina, [Cómo detectar y protegerse de los ciberdelincuentes y las estafas telefónicas](https://www.bbva.com/es/ar/innovacion/como-detectar-y-protegerse-de-los-ciberdelincuentes-y-las-estafas-telefonicas) | 2020-09-10 | «Ni el banco ni otras empresas solicitarán datos confidenciales por teléfono.» Señales de estafa: urgencia, pago previo, transferencia a un CBU desconocido, ingresar un PIN en el cajero. |
| F8 | UK Finance, campaña Take Five to Stop Fraud, [Protect yourself](https://www.takefive-stopfraud.org.uk/advice/general-advice/) | sin fecha | Señales de alerta: «Are you being asked to share a one-time passcode, password or PIN?» y «Have you been asked to move money to a new or "safe" account?». «Only criminals will try to rush or panic you.» |
| F9 | GSA SmartPay (programa de tarjetas del gobierno de EE. UU.), [Smart Bulletin No. 003, Phone Fraud Scams](https://smartpay.gsa.gov/guidance-and-audits/smart-bulletins/003/) | 2007-03-09 | Los bancos o las asociaciones de tarjetas «will never ask for personal information via phone or email» «unless the call was initiated by the cardholder». |
| F10 | Microsoft, [Protect yourself from online scams and attacks](https://support.microsoft.com/en-us/windows/protect-yourself-from-tech-support-scams-2ebf91bd-f94c-2a8a-e541-f5c800d18435) | sin fecha | «Unless you contact us first, Microsoft won't call you to offer tech support.» El acceso remoto al equipo es una maniobra de los estafadores. |

**Huecos.** No se encontró:
- una fuente primaria de Visa, Mastercard o Prisma en Argentina. F4 y F5 hablan de tarjetas desde el banco emisor, y
  F9 es de un programa de tarjetas de EE. UU.;
- **ninguna fuente que describa qué hace una llamada real** de un banco, por ejemplo qué verifica una alerta de
  fraude. Las fuentes solo dicen lo que una entidad no hace. Por eso el criterio usa solo esas listas: es angosto a
  propósito;
- fuentes sobre lo que hacen por teléfono un consultorio, un correo, una encuestadora o una empresa de selección. Para
  esas familias, el criterio solo aplica las señales generales (S1 y S3).

## Criterio

Se mira solo lo que hace **quien habla por una entidad** (en estas llamadas, quien llama). Cuenta aunque la persona no
lo haga, y aunque quien llama se corrija después. Si es la persona la que ofrece algo y quien llama la frena, no cuenta.

| Señal | Qué hace quien llama | Para qué entidades | Fuentes |
|---|---|---|---|
| **S1. Credenciales o códigos** | Pide que la persona diga, dicte, lea o tipee una clave, contraseña, PIN, token, usuario de home banking, un código de verificación o de vinculación recibido por SMS, app o correo, el código de seguridad de la tarjeta o su número completo. | Todas | F1, F2, F3, F4, F5, F8 |
| **S2. Operar durante la llamada** | Pide que la persona opere en el cajero, el home banking o la app mientras sigue en la llamada, o la guía para hacerlo; que transfiera o pague a una cuenta o enlace que da quien llama, o que mueva dinero a otra cuenta para protegerlo. | Banco, tarjeta o billetera, organismo público | F1, F2, F3, F5, F6, F7, F8 |
| **S3. Instalar o dar acceso** | Pide instalar una aplicación o dar acceso remoto al equipo o al celular. | Banco, tarjeta o billetera, organismo público: siempre. Cualquier otra empresa: solo si la persona no pidió el contacto. | F5, F10 |
| **S4. Datos personales sin que la persona haya pedido el contacto** | Pide que la persona diga datos de identidad o de cuenta (DNI, fecha de nacimiento, CUIL o CUIT, número de cuenta o CBU, datos de la tarjeta) en una llamada que la persona no pidió. | Banco, tarjeta o billetera, organismo público | F3, F4, F7, F9 |

- **«La persona pidió el contacto»** quiere decir que en la llamada consta que responde a algo que la persona hizo:
  una solicitud, un reclamo, un turno, un ticket, una compra o un trámite suyo, y la persona lo reconoce. Un aviso de
  fraude por una operación que la persona no hizo **no** es un contacto pedido.
- **Dudosa:** tiene al menos una señal. **Sin marca:** no tiene ninguna. **A revisar:** quienes la aplicaron no
  coinciden, o alguno no pudo decidir.
- **Variante estricta de S4**, por F3, que no tiene la excepción de F9: cuenta también cuando la persona pidió el
  contacto. Se informa aparte, como sensibilidad.
- Se anota además si en S4 el pedido llega **antes de que quien llama diga el motivo** de la llamada, el ejemplo de la
  propuesta. Es informativo: no cambia la marca.

**Lo que este criterio no cubre.** Que la llamada sea rara, incoherente, apurada o poco natural; que una empresa que
no es un banco pida el DNI; el tono. Eso es la pregunta de credibilidad de #145 y la responden personas.

## Cómo se aplicó

> El resultado de la aplicación está en [`LEGITIMAS-DUDOSAS.md`](LEGITIMAS-DUDOSAS.md).

- `python -I corpus_desarrollo.py ciego-dudosas` arma un paquete con las 94 transcripciones, las líneas numeradas, los
  roles PROTEGIDA y OTRA de `roles-protegida.json` y este criterio. Las llamadas van renombradas `llamada-001…094` y
  mezcladas con semilla fija. No llevan `case_id`, familia, referencia, lote ni resultados. La clave queda fuera del
  paquete.
- **Dos agentes nuevos** (Claude, sesiones aparte) anotaron cada uno las 94, sin ver la anotación del otro, este
  repositorio, prompts ni corridas. Por llamada devuelven el tipo de entidad, si la persona pidió el contacto, la línea
  de cada señal (o nada) y un motivo corto.
- `python -I corpus_desarrollo.py unir-dudosas` une las dos anotaciones con la clave. **La marca la calcula el script
  desde los campos**, no desde la opinión del agente: dudosa si las dos anotaciones tienen alguna señal, a revisar si
  difieren.
