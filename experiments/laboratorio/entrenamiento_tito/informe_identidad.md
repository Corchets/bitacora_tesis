# Lote identidad para entrenamiento de Tito

## Estado del Issue #41

El lote contiene **100 familias (50 `estafa`, 50 `legitima`) y 2.000 realizaciones**. Las 50 familias `identidad_001`–`identidad_050` originales fueron recuperadas y conservadas; solo recibieron ajustes puntuales de léxico y puntuación en frases preexistentes. La etapa 2 agrega `identidad_051`–`identidad_075` (25 positivas) y `identidad_076`–`identidad_100` (25 negativas), con 20 textos por familia. [`familias_identidad.json`](familias_identidad.json) es la fuente de verdad del lote.

La ampliación positiva incluye solicitudes indirectas de dígitos recibidos, vinculación de sesiones con QR, accesos desde otros equipos, claves de cuentas y desbloqueo de dispositivos. Los pretextos cubren programas sociales, promociones locales, telefonía, servicios y consultas. Se evitaron los pedidos de códigos genéricos atribuidos solamente a un turno o a un beneficio. Los negativos incluyen consultas y confirmaciones de turnos, pedidos, transferencias por prestaciones acordadas, urgencias médicas y de servicios reales, coordinación familiar y laboral, autogestión de PIN/códigos dentro de la aplicación que abrió quien llama y ayuda técnica solicitada a personas conocidas.

Las 50 familias nuevas se materializaron con cinco enunciados contextuales propios y cuatro acciones o respuestas compatibles por familia. Se usaron aperturas variadas y se revisaron las combinaciones de bloques a nivel de familia, junto con la primera y última realización de cada familia nueva. No se hizo revisión humana exhaustiva de las 1.000 realizaciones nuevas.

La verificación estructural del JSON completo encontró: IDs `identidad_001`–`identidad_100` únicos, 20 textos por familia, distribución 50/50, 2.000 textos únicos tras normalizar tildes, mayúsculas y puntuación, longitudes entre 14 y 35 palabras, fuentes existentes y ausencia de URLs, correos o números largos. Estas comprobaciones no prueban calidad semántica exhaustiva ni rendimiento del detector. `preparar.py` se consultó como contrato de validación; no se ejecutó porque valida también los lotes `banco` y `cotidiano` fuera del alcance de este trabajo.

## Fuentes y límites

[`fuentes_identidad.json`](fuentes_identidad.json) conserva ocho referencias oficiales verificadas, consultadas el 2026-10-02: seguridad de WhatsApp (F01), alertas sobre programas sociales (F02), trámites de salud y soporte (F03), páginas falsas y trámites suplantados (F04), concursos y promociones (F05), SIM swapping (F06), riesgos de QR (F07) y vishing/solicitud telefónica de datos (F08). Sustentan patrones generales y contexto; los diálogos son sintéticos originales, no citas ni transcripciones, y no atribuyen procedimientos particulares a organismos o empresas.

No se incorporaron fuentes nuevas porque los patrones cubiertos corresponden a las referencias existentes. No se importaron transcripciones ni datasets. No se entrenó ni evaluó un modelo; no hay split ni métricas del detector. D07, D08 y D09 continúan abiertas.

## Filtro del coordinador posterior a la entrega

El 2026-10-02 la inspección final apartó las familias `identidad_062`, `078`, `085`, `089`, `090` y `096` por contexto insuficiente o voces incompatibles. Los motivos completos están en [exclusiones.json](exclusiones.json). La generación conserva 100 familias y 2.000 textos; la exportación de desarrollo incluye 1.880 (980 `estafa`, 900 `legitima`). Los otros 120 se guardan para reescritura y no alimentan a Tito. El éxito estructural de la generación no acredita revisión semántica exhaustiva.
