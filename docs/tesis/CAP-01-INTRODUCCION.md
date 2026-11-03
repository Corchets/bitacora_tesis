> **Estado: borrador del 2026-11-03.** Requiere revisión del equipo.

# Capítulo 1: Introducción

## 1.1. Contexto y motivación

El vishing es una modalidad de ingeniería social realizada por llamada de voz. Quien llama intenta obtener información sensible, inducir una transferencia o provocar otra acción riesgosa. En Argentina, fuentes oficiales documentan modalidades de suplantación bancaria, familiar y previsional ([UFECRI](https://www.fiscales.gob.ar/procuracion-general/la-unidad-fiscal-especializada-en-investigacion-criminal-compleja-advierte-sobre-estafas-telefonicas-a-personas-mayores/)), pedidos de códigos y secretos ([BCRA](https://www.bcra.gob.ar/como-prevenir-estafas-virtuales/)) y falsos beneficios ([ANSES](https://www.anses.gob.ar/noticias/anses-nunca-solicita-datos-personales-claves-o-informacion-bancaria-0)). Estas fuentes respaldan la existencia de las modalidades; no miden su prevalencia.

Un número puede parecer normal, y el peligro hacerse visible solo en el contenido de la conversación y en cómo evoluciona. La reputación del número no ve lo que se dice, y las recomendaciones de BCRA y ANSES dependen de que la persona las recuerde en pocos minutos de presión, sin poder verificar a su interlocutor.

## 1.2. Problema y beneficiarios

El problema de ingeniería es detectar evidencia suficiente de manipulación y de un pedido riesgoso **mientras la llamada todavía está en curso**, con una tasa de falsas alarmas aceptable y una advertencia que permita actuar antes de compartir información o de hacer una operación.

La persona beneficiaria es alguien en Argentina que conversa por teléfono con quien dice llamar de su banco, de un organismo como ANSES, de una mesa de soporte o de parte de un familiar. El daño que se quiere evitar es que dicte un código o una clave, transfiera dinero o comparta la pantalla. Por eso la advertencia sirve solo si llega antes de que cumpla el pedido.

El proyecto conserva el foco en personas adultas mayores, por la gravedad potencial de las pérdidas y su exposición a la suplantación. Ese encuadre es parcial ([D12](../gestion/MAPA-DECISIONES.md#d12--encuadre-del-foco-en-adultos-mayores)): no es un requisito del corpus ni permite prometer rendimiento para ese grupo.

## 1.3. Objetivos

**Objetivo general.** Diseñar, implementar y evaluar un prototipo capaz de analizar incrementalmente un flujo de audio de una conversación de voz en español, mediante inferencia local, para estimar el riesgo de vishing, identificar maniobras de ingeniería social y emitir una advertencia contextual antes de una acción crítica, cuantificando su desempeño, falsas alarmas, latencia y margen temporal de intervención.

**Objetivos específicos.**

1. Relevar el estado del arte, las modalidades relevantes de vishing y las restricciones técnicas, éticas y legales del problema.
2. Definir una taxonomía operacional de maniobras y solicitudes riesgosas.
3. Construir un corpus controlado y documentado de conversaciones simuladas de vishing y llamadas legítimas en español.
4. Comparar alternativas de reconocimiento de voz local sobre audio representativo.
5. Evaluar reglas solas como línea base para comparar los detectores candidatos.
6. Desarrollar un detector incremental que acumule evidencia a lo largo del tiempo.
7. Diseñar advertencias explicables derivadas de las señales detectadas.
8. Integrar la cadena audio→ASR→detección→advertencia en un entorno controlado.
9. Evaluar clasificación, falsas alarmas, robustez al ASR, anticipación, latencia y consumo de recursos.
10. Documentar arquitectura, decisiones, implementación, pruebas, resultados, limitaciones y trabajo futuro.

## 1.4. Preguntas de investigación

- **PI1, detección incremental:** ¿con qué desempeño y tasa de falsas alarmas puede detectarse vishing utilizando solo la parte de la conversación disponible hasta cada instante?
- **PI2, utilidad temporal:** ¿con cuánto margen respecto del primer pedido riesgoso y de la primera acción de cumplimiento puede emitirse una alerta estable?

Se suman dos evaluaciones que no son preguntas centrales: **E1**, el efecto del ASR, que compara el mismo detector con texto manual y con texto reconocido, y **E2**, la revisión de si el motivo mostrado corresponde a la evidencia disponible. El tutor consideró adecuada esta formulación el 2026-09-09 ([minuta](../gestion/seguimientos/2026-09-09.md)). Las preguntas no presuponen un resultado favorable.

## 1.5. Alcance, exclusiones y contribuciones

**Dentro del alcance:** español, con prioridad de la variedad argentina y sin afirmar representatividad nacional; corpus de llamadas simuladas y legítimas difíciles; transcripción local; detector sobre texto con contexto de la llamada actual; evento crítico y medición de anticipación; advertencia explicable; reproducción de audio como streaming; y demo en entorno controlado.

**Fuera del alcance:** captura universal de llamadas PSTN desde una app Android ordinaria; biometría y detección de voces clonadas; agenda, historial, memoria entre sesiones, reputación de números y detección de spoofing; rasgos acústicos para detectar fraude; app iOS, múltiples idiomas y análisis de mensajes; backend de producción y publicación comercial; y estudio poblacional con víctimas reales.

El contenido de la llamada permite evaluar señales de riesgo, pero no verificar la identidad del interlocutor. Si dos llamadas tienen el mismo contenido observable, el detector dispone de la misma evidencia aunque una sea legítima y la otra no.

**Contribución.** No es una primicia: el análisis durante la llamada ya existe, comercial y académicamente. El aporte es la combinación de vishing en español, contexto argentino, procesamiento incremental, intervención explicable, evento crítico anotado, evaluación temporal, ejecución local y reproducibilidad.

## 1.6. Organización del informe

El [capítulo 2](CAP-02-MARCO-CONCEPTUAL-Y-ANTECEDENTES.md) presenta conceptos y antecedentes. El [3](CAP-03-REQUISITOS-Y-ANALISIS.md) define requisitos y restricciones, y el [4](CAP-04-METODOLOGIA.md), la metodología. Los capítulos [5](CAP-05-DISENO-Y-ARQUITECTURA.md) y [6](CAP-06-IMPLEMENTACION.md) describen diseño e implementación; el [7](CAP-07-VERIFICACION-Y-PRUEBAS.md), las pruebas de software; y el [8](CAP-08-RESULTADOS-EXPERIMENTALES.md), los resultados. El [9](CAP-09-DISCUSION.md) los discute, el [10](CAP-10-GESTION-DEL-PROYECTO.md) repasa la gestión y el [11](CAP-11-CONCLUSIONES.md) concluye.
