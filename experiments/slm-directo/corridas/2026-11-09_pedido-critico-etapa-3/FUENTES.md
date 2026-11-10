# Fuentes de la lista de pedidos críticos (etapa 3 de #143)

> **Estado: propuesta sin discutir.** Relevamiento del 2026-11-09, para la definición del campo `pedido_critico` de C
> con campo ([`salida_json_c_con_campo.txt`](../../prompts/salida_json_c_con_campo.txt)). Mateo escribió la definición y
> los ejemplos ese día, a partir de fuentes externas. Este relevamiento busca una fuente para cada ejemplo, sin mirar el
> corpus ni resultados (ADR 0005, regla 7). **Falta que Mateo lo verifique.**

## Cómo se verificó

- **Texto completo:** se leyó la página en un navegador, o el texto extraído del PDF.
- **WebFetch:** se leyó un resumen automático de la página. Conviene abrirla una vez a mano antes de citarla en la tesis.

## Cada ejemplo, con sus fuentes

| ejemplo del párrafo | fuentes | estado |
|---|---|---|
| dictar un código que le llegó | S01, S03, S04, S05, S08, S09, S10, S11, S12, S15, S16, S20, S26, S27, S29, S31, S37 | cubierto, con WhatsApp (S09, S10) |
| decir una clave o un PIN | S01, S02, S04, S05, S12, S13, S15, S16, S20, S21, S26, S31, S36 | cubierto |
| dar los datos completos de la tarjeta, o «entregar la tarjeta» | S02, S05, S12, S13, S14, S18, S21, S26, S34, S36, S37 | cubierto, con Visa y Mastercard. Ninguna fuente nombra el vencimiento, que entra en «datos de la tarjeta». «Entregar la tarjeta» es pasar sus números, no el plástico (Mateo, 2026-11-09) |
| mandar una foto del DNI o de su cara | S01, S07, S16, S24 | cubierto |
| transferir, pagar o entregar plata | S08, S19, S20, S21, S22, S23, S25, S26, S34, S35 | cubierto |
| instalar un programa o compartir la pantalla | S01, S05, S08, S26, S28, S29, S34 | cubierto |
| seguir pasos en el cajero o en la app | cajero o app durante el llamado: S01, S15, S16, S19, S21, S23, S25, S27. Token: S03, S04, S36. Préstamo: S15, S34, S35 | cubierto |
| cortar y llamar a otro número | S22 (único pedido por llamado, de 2015). Por mensaje: S17, S32, S33. El consejo contrario, llamar vos al número oficial: S12, S14, S16, S18, S21, S26 | **con poca base** |

**Procesadoras de tarjetas (Prisma, Payway, Fiserv):** no hay nada dirigido al tarjetahabiente. Por las tarjetas están
las marcas: Visa (S12, S13) y Mastercard (S14).

## La exclusión: DNI, fecha de nacimiento, nombre y dirección

- **A favor:**
  - las listas oficiales de «nunca te vamos a pedir» nombran credenciales (claves, PIN, token, códigos, datos de la
    tarjeta), y ninguna nombra el número de DNI ni la fecha de nacimiento (S01, S02, S03, S26, S37);
  - la banca telefónica legítima de Banco Provincia identifica al cliente con el número de documento, más una clave
    aparte (S30);
  - el manual del Gobierno nacional dice que los datos personales se piden cuando llama el cliente (S11, p. 6).
- **En contra:**
  - el MPF de Río Negro recomienda no decirle a un desconocido el DNI, el nombre completo ni la fecha de nacimiento
    (S25);
  - BNA, BBVA, Mastercard, Banco Provincia y la UFECRI hablan de «datos personales» en general (S14, S23, S26, S31, S32).
- **Lectura:** las fuentes no dicen que dar el DNI sea inocuo. Sí sostienen que con el DNI solo no se saca plata ni se
  toma una cuenta. La exclusión es una decisión de diseño, y C ya la tenía. S25 es la voz oficial que va más lejos.

## Fuentes

| código | fuente | fecha | verificación |
|---|---|---|---|
| S01 | [BCRA, ¿Cómo prevenir estafas virtuales?](https://www.bcra.gob.ar/como-prevenir-estafas-virtuales/) | sin fecha | WebFetch |
| S02 | [Banco Nación, Proteja sus datos](https://www.bna.com.ar/Personas/TarjetasDeCredito/ProtejaSusDatos) | sin fecha | WebFetch |
| S03 | [Banco Provincia, preguntas frecuentes del Token de Seguridad](https://www.bancoprovincia.com.ar/web/PREGUNTAS_FRECUENTES_TOKEN_DE_SEGURIDAD) | sin fecha | WebFetch |
| S04 | [BBVA, Clave Token y SMS](https://www.bbva.com/es/ar/innovacion/clave-token-y-sms-como-funcionan-estos-factores-de-autenticacion/) | sin fecha | WebFetch |
| S05 | [Mercado Pago, Seguridad](https://www.mercadopago.com.ar/seguridad) | sin fecha | WebFetch |
| S07 | [MPF, UFECI: fotos del DNI y selfies](https://www.fiscales.gob.ar/ciberdelincuencia/pedidos-de-selfies-y-de-fotos-del-dni-aumentan-los-fraudes-vinculados-con-los-servicios-puerta-a-puerta-del-correo-argentino/) | 2022-07-08 | WebFetch |
| S08 | [UFECI, informe anual 2024](https://www.mpf.gob.ar/ufeci/files/2025/06/UFECI_informe_anual_2024-1.pdf), pp. 17–20 | 2025-06 | texto completo |
| S09 | [WhatsApp, Recibí un código de verificación que no había solicitado](https://faq.whatsapp.com/479314433984258/) | sin fecha | texto completo |
| S10 | [WhatsApp, Cómo recuperar una cuenta comprometida](https://faq.whatsapp.com/1131652977717250/?locale=es_LA) | sin fecha | WebFetch |
| S11 | [Gobierno nacional, Cibercuidados: fraudes y estafas](https://www.argentina.gob.ar/sites/default/files/manual_talleres_ti_cibercuidados_fraudes_y_estafas.pdf) | sin fecha | texto completo |
| S12 | [Visa Argentina, Prevención de fraude digital](https://www.visa.com.ar/support/consumer/security/prevencion-fraude-digital.html) | sin fecha | texto completo |
| S13 | [Visa Argentina, Prevención de fraude](https://www.visa.com.ar/la-diferencia-visa/seguridad/prevencion-fraude.html) | sin fecha | WebFetch |
| S14 | [Mastercard Argentina, preguntas frecuentes, «Denuncia de fraude»](https://www.mastercard.com/ar/es/personal/get-support/frequently-asked-questions.html) | sin fecha | texto completo |
| S15 | [BCRA, Recomendaciones para evitar estafas virtuales](https://www.bcra.gob.ar/archivos/Pdfs/Noticias/recomendaciones-bcra-estafas-virtuales.pdf) | 2025-08-05 | texto completo |
| S16 | [Comercio Interior y BCRA, Consejos para evitar estafas y fraudes bancarios](https://www.argentina.gob.ar/noticias/consejos-para-evitar-estafas-y-fraudes-bancarios) | 2021-06-29 | WebFetch |
| S17 | [BCRA, caso de smishing a nombre del BCRA](https://www.bcra.gob.ar/noticias/caso-de-smishing-mensaje-de-texto-o-de-chat-falso-a-nombre-del-bcra/) | 2019-07-26 | WebFetch |
| S18 | [Con Vos en la Web, ¿Qué hago si me piden datos personales por teléfono?](https://www.argentina.gob.ar/justicia/convosenlaweb/situaciones/que-hago-si-me-piden-datos-personales-por-telefono) | 2026-10 | WebFetch |
| S19 | [GCBA, Estafas virtuales](https://buenosaires.gob.ar/noticias/estafas-virtuales) | 2024-06-07 | WebFetch |
| S20 | [IPS de la Provincia de Buenos Aires, aviso de estafa a jubilados](https://www.ips.gba.gob.ar/node/736) | 2026-10-05 | WebFetch |
| S21 | [Defensoría del Pueblo de Río Negro, Estafas telefónicas](https://defensoriarionegro.gov.ar/drn/estafas-telefonicas-ante-la-duda-corta-la-llamada/) | 2021-05-17 | WebFetch |
| S22 | [MPF, Fiscalía de Instrucción N.º 43, nueva modalidad de estafa telefónica](https://www.fiscales.gob.ar/fiscalias/alertan-sobre-una-nueva-modalidad-de-estafa-telefonica/) | 2015-03-26 | texto completo |
| S23 | [MPF, UFECRI, estafas telefónicas a personas mayores](https://www.fiscales.gob.ar/procuracion-general/la-unidad-fiscal-especializada-en-investigacion-criminal-compleja-advierte-sobre-estafas-telefonicas-a-personas-mayores/) | 2020-08-28 | WebFetch |
| S24 | [MPF, UFECI, medida cautelar a favor de una jubilada](https://www.fiscales.gob.ar/ciberdelincuencia/dictaron-una-medida-cautelar-a-favor-de-una-jubilada-que-fue-victima-de-una-estafa-bancaria-virtual/) | 2026-03-19 | WebFetch |
| S25 | [MPF de Río Negro, nuevas estafas telefónicas a dos mujeres mayores](https://ministeriopublico.jusrionegro.gov.ar/nota/4840/nuevas-estafas-telefonicas-perjudican-a-dos-mujeres-de-mas-de-80-anos) | 2021-08-12 | texto completo |
| S26 | [Banco Provincia, Llamados y mensajes](https://www.bancoprovincia.com.ar/web/cs_llamados_y_mensajes) | sin fecha | texto completo |
| S27 | [Banco Provincia, Cajeros automáticos](https://www.bancoprovincia.com.ar/web/cs_cajeros_automaticos) | sin fecha | WebFetch |
| S28 | [Banco Provincia, Accesos remotos](https://www.bancoprovincia.com.ar/web/cs_accesos_remotos) | sin fecha | WebFetch |
| S29 | [Banco Provincia, Hackeo de WhatsApp](https://www.bancoprovincia.com.ar/web/cs_hackeo_whatsapp) | sin fecha | WebFetch |
| S30 | [Banco Provincia, Medidas de seguridad del Banco](https://www.bancoprovincia.com.ar/web/medidas_de_seguridad_del_banco) | sin fecha | WebFetch |
| S31 | [Banco Nación, Información de seguridad](https://www.bna.com.ar/Home/home/InformacionDeSeguridad) | sin fecha | WebFetch |
| S32 | [BBVA Argentina, Recomendaciones de seguridad](https://www.bbva.com.ar/personas/recomendaciones-de-seguridad.html) | sin fecha | texto completo |
| S33 | [BBVA, qrishing, vishing y smishing](https://www.bbva.com/es/ar/innovacion/estafas-virtuales-como-evitar-el-qrishing-el-vishing-y-el-smishing/) | sin fecha | WebFetch |
| S34 | [Mercado Pago, ¿Cómo prevenir estafas telefónicas?](https://www.mercadopago.com.ar/ayuda/como-prevenir-estafas-telefonicas_36408) | sin fecha | texto completo |
| S35 | [Naranja X, si te llaman para darte algo en su nombre](https://www.naranjax.com/blog/que-hacer-si-te-llaman-para-darte-algo-en-nombre-de-naranja-x) | sin fecha | texto completo |
| S36 | [ICBC Argentina, Seguridad en canales](https://www.icbc.com.ar/personas/seguridad-canales) | sin fecha | WebFetch |
| S37 | [Banco Patagonia, Evitá los fraudes](https://www.bancopatagonia.com.ar/ebank/personas/seguridad/evitar-fraudes.php) | sin fecha | WebFetch |

Quedaron afuera:
- **Notas periodísticas, solo como complemento:** La Nación sobre la campaña de las asociaciones de bancos (2020-10-07,
  ya citada en [`FUENTES.md` de la etapa 1](../2026-11-06_puntaje-token-2/FUENTES.md)), Diario Uno sobre un 0800 falso
  (2018) y Diario de Cuyo sobre un cadete que retira plata (2021).
- **Sin verificar:** las notas de ANSES («La ANSES no llama para requerir datos…»), que cargan vacías.
