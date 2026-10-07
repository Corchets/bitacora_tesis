# Banco, billeteras y pagos

## Estado de producción

La etapa de banco del Issue #41 está materializada en [familias_banco.json](familias_banco.json): **100 familias/marcos** (banco_001–banco_100), distribuidas en **50 estafa y 50 legitima**, con 20 realizaciones combinatorias por familia: **2.000 textos** en total. Son 100 marcos con variaciones construidas al combinar cinco contextos de enunciación y cuatro expresiones/pedidos o respuestas por familia; no son 2.000 escenarios independientes ni conversaciones grabadas. Los textos están redactados como turnos de voz telefónica ficticios, no como narración explicativa.

Las primeras 25 familias positivas (banco_001–banco_025) cubren suplantación de soporte bancario o de billetera, pedidos de claves/tokens, transferencias y devoluciones inducidas, tarjetas, préstamos, inversiones y acceso remoto. Las 25 nuevas (banco_051–banco_075) amplían el repertorio con pedidos de los números visibles en SMS, acceso por pantalla compartida, autorización de dispositivo y QR, refinanciaciones, cuotas, impuestos, tasas, seguros y beneficios. Las familias legítimas previas (banco_026–banco_050) recorren compras, pagos, consultas, reclamos, deudas y movimientos ordinarios; las nuevas (banco_076–banco_100) agregan códigos de reserva, puerta y operación propia, transferencias a conocidos previamente verificados, recuperación de clave desde la aplicación propia, devoluciones documentadas, pagos según contrato, reclamos por fraude pasado y charlas cotidianas de gastos, negocios y trabajo. Los ejemplos no incorporan datos personales, teléfonos, enlaces ni credenciales reales.

## Fuentes consultadas

Se revisaron las páginas completas de siete fuentes institucionales argentinas el 2026-10-02; sus hallazgos y alcance se registran en [fuentes_banco.json](fuentes_banco.json):

- [BCRA: Cómo prevenir estafas virtuales](https://www.bcra.gob.ar/como-prevenir-estafas-virtuales/) describe llamados que solicitan datos/códigos, falsos reintegros o errores de transferencias y pedidos de asistencia remota.
- [Policía Federal Argentina, comunicado en Argentina.gob.ar](https://www.argentina.gob.ar/noticias/desarticulamos-una-banda-dedicada-estafas-por-home-banking-en-cordoba-y-buenos-aires) documenta una causa particular con control remoto, credenciales/tokens y transferencia de fondos.
- [UFECI: Informe 2024](https://www.mpf.gob.ar/ufeci/files/2025/06/UFECI_informe_anual_2024-1.pdf) describe patrones reportados de llamadas de supuestos representantes financieros y acceso remoto.
- [BCRA: Reclamar por fraude o estafa](https://www.bcra.gob.ar/realizar-un-reclamo-ante-el-banco-central-por-fraude-o-estafa/) informa la secuencia de reclamo por operaciones no reconocidas, usada como contexto para turnos de consulta y autogestión.
- [Con Vos en la Web: protección al utilizar un código QR](https://www.argentina.gob.ar/justicia/convosenlaweb/situaciones/como-me-protejo-al-utilizar-un-codigo-qr) describe riesgos de sitios falsos, accesos y acciones iniciadas por QR, y recomienda revisar destino e identidad antes de confirmar.
- [Superintendencia de Seguros de la Nación: intentos de contacto fraudulentos](https://www.argentina.gob.ar/noticias/la-ssn-advierte-sobre-intentos-de-contacto-fraudulentos) informa suplantaciones y pedidos de datos por canales no oficiales.
- [Comisión Nacional de Valores: advertencia al público inversor](https://www.argentina.gob.ar/noticias/advertencia-al-publico-inversor-sobre-nuevas-estafas-virtuales) describe pedidos sucesivos de transferencias bajo pretextos de impuestos, tasas o derechos.

Las fuentes fundamentan patrones y vocabulario de contexto; no son transcripciones de los textos sintéticos ni prueban que las interacciones comerciales incluidas sean protocolos oficiales. Los ejemplos son originales y sintéticos (licencia_textos: no importados). El informe UFECI cuenta reportes recibidos y una causa policial documenta un caso; ninguno justifica inferir prevalencia o representatividad para estas 100 familias.

## Límites de uso

La cantidad de textos no debe confundirse con diversidad independiente: cada familia comparte un núcleo semántico y cada realización surge de composición controlada. Este lote sirve como material sintético de entrenamiento y exploración; no es evidencia de rendimiento, no simula salida de ASR y no cierra decisiones D07, D08 ni D09. Para evaluar generalización habrá que separar por familia y contrastar con conversaciones independientes; los ejemplos negativos tampoco certifican la legitimidad de un interlocutor real.
