> **Estado: borrador del 2026-11-03.** Requisitos reconstruidos a partir del plan, la prefactibilidad y la matriz de pruebas; requieren revisión del equipo.

# Capítulo 3: Requisitos y análisis del problema

## 3.1. Interesados y escenarios

| Interesado | Qué necesita |
|---|---|
| Persona protegida | Un aviso comprensible, a tiempo, que no interrumpa la llamada ni exponga datos. |
| Equipo y tutor | Un experimento reproducible y una demo que se pueda repetir. |
| Tribunal | Decisiones trazables y límites declarados. |

Los escenarios salen del [catálogo](../corpus/CATALOGO-ESCENARIOS.csv): falso empleado del banco, falso soporte técnico, código de WhatsApp, falso organismo previsional, falso premio y falso familiar. Cada uno tiene una contraparte legítima con vocabulario parecido, para comprobar si el detector distingue un pedido peligroso de la mera mención de un banco, un código o dinero.

## 3.2. Requisitos funcionales

| ID | Requisito | Verificación |
|---|---|---|
| RF-01 | Procesar el audio en streaming, sin depender del fin de la llamada. | Matriz de trazabilidad, [§7.6](CAP-07-VERIFICACION-Y-PRUEBAS.md) |
| RF-02 | Reemplazar los borradores de transcripción sin duplicar líneas. | Ídem |
| RF-03 | Consolidar los segmentos cerrados en el contexto de la llamada. | Ídem |
| RF-04 | Respetar la causalidad: el detector nunca ve texto futuro. | Ídem |
| RF-05 | Emitir como máximo un aviso por llamada. | Ídem |
| RF-06 | Reiniciar todo el estado entre llamadas. | Ídem |
| RF-07 | Tratar las respuestas inválidas como fallo, no como voto negativo. | Ídem |
| RF-08 | Comprobar que la evidencia citada exista en lo transcripto. | Ídem |
| RF-09 | Exigir salida estructurada con riesgo, alerta, motivo y evidencia. | Ídem |
| RF-10 | Separar los dos canales de la llamada, sin suponer quién habla primero. | Pruebas de `experiments/voip/` |
| RF-11 | Mostrar el aviso con el motivo y la cita, identificando a cada persona por su rol. | #104 y pruebas de la vista de presentación |

## 3.3. Requisitos no funcionales

Los umbrales de latencia y memoria son criterios internos del proyecto ([prefactibilidad](../investigacion/PREFACTIBILIDAD-TECNICA.md)), no límites universales.

| ID | Requisito | Situación de la configuración final (ADR 0001 y ADR 0002) |
|---|---|---|
| RNF-01 | Seguir el ritmo del audio: `RTF` < 1. | ASR: cumple, 0,088. Falta el `RTF` conjunto del recorrido. |
| RNF-02 | Memoria del recorrido acotada. | **No cumple el techo original de 512–1024 MB.** En la M1 de 8 GB, el ASR usa 1,0 GB y el archivo de E2B pesa 4,59 GB. En el Samsung A56, E2B solo llegó a 3,39 GiB de pico ([a56-congelada-latencia](../../experiments/slm-directo/corridas/2026-11-10_a56-congelada-latencia/README.md)); el ASR no se midió en el teléfono. El tutor reorientó la referencia a la gama más alta disponible; falta citar su RAM desde el fabricante. |
| RNF-03 | Respuesta por turno: p95 ≤ 1,5 s (degradado hasta 2 s). | **No cumple.** En el Samsung A56, E2B tarda 3,60 s de mediana y 4,90 s de p95 por línea de OTRA, y el motivo suma unos 11 s en el primer aviso ([a56-congelada-latencia](../../experiments/slm-directo/corridas/2026-11-10_a56-congelada-latencia/README.md)). Se midió con el prompt base, sin la premisa. Bajarlo es [#172](https://github.com/Corchets/bitacora_tesis/issues/172). |
| RNF-04 | Procesamiento local: ni audio ni texto salen del equipo. | Cumple por diseño. El tutor descartó por completo el uso de un modelo por API. |
| RNF-05 | Reproducibilidad: cada corrida registra datos, configuración, seed, código, hardware y salidas. | Cumple con manifiestos. Excepción declarada: #101 corrió con cambios sin commit en la carpeta. |
| RNF-06 | Calidad objetivo: 80–85 % de estafas avisadas con 10–15 % de falsas alarmas, sobre todas las estafas. | Meta de referencia del equipo, con el visto bueno del tutor; no es criterio de aprobación. Se mide en el test reservado. |

## 3.4. Restricciones de plataforma, privacidad y ética

**Android.** Una app ordinaria no puede acceder a los flujos `VOICE_UPLINK` y `VOICE_DOWNLINK` de una llamada convencional; ese permiso está reservado a apps del sistema. Por eso la captura universal PSTN queda fuera del alcance ([D05](../gestion/MAPA-DECISIONES.md#d05--elegir-la-fuente-de-audio-demostrable)).

**Privacidad.** La inferencia es estrictamente local. El diseño del producto prevé descartar audio y transcripción al terminar la llamada, y conservar solo metadatos de seguridad ([privacidad del sistema](../corpus/PRIVACIDAD-DEL-SISTEMA.md)). El prototipo de laboratorio sí guarda las llamadas para poder medirlas, en una carpeta fuera de Git y con consentimiento.

**Ética.** La UNSTA no exige comité formal de ética para este proyecto ([minuta del 2026-09-09](../gestion/seguimientos/2026-09-09.md)). Se trabaja con participantes adultos del equipo o familiares, con consentimiento previo, datos ficticios y sin permiso de publicar las voces. El tutor aprobó grabar con este esquema el 2026-10-28.

## 3.5. Criterios de aceptación

El proyecto es exitoso si responde las preguntas con un procedimiento honesto y reproducible, entrega un recorrido demostrable y documenta sus límites. Un resultado que muestre baja anticipación, degradación por ASR o superioridad de un método simple sigue siendo válido si el experimento está bien diseñado. La meta de RNF-06 es una referencia, no un umbral para aprobar: se busca el mayor porcentaje posible sin ajustar el sistema solo para alcanzarla, y se informa aunque no se alcance.

## 3.6. Alternativas consideradas

| Tema | Alternativas | Elección | Dónde se fundamenta |
|---|---|---|---|
| Fuente de audio | Replay; altavoz; VoIP propia; captura por canal en notebook; integración privilegiada | Replay para experimentar y captura por canal con Meet para la demo | [§5.5.2](CAP-05-DISENO-Y-ARQUITECTURA.md#552-captura-de-audio) y [alternativas](../ingenieria/ALTERNATIVAS-CAPTURA-AUDIO.md) |
| Entrada del detector | Texto; texto y rasgos acústicos | Texto ([D11](../gestion/MAPA-DECISIONES.md#d11--análisis-lingüístico-o-también-acústico), a ratificar) | [§5.5.4](CAP-05-DISENO-Y-ARQUITECTURA.md#554-enfoque-lingüístico-frente-a-acústico-d11-abierta) |
| Inferencia | Local; API | Local | Minuta del 2026-10-28 |
| ASR y detector | Ver [ADR 0001](../ingenieria/adr/0001-parakeet-filtro-y-gemma4-e2b-con-tito-viejo.md) y [ADR 0002](../ingenieria/adr/0002-detector-gemma4-e2b-solo-con-prompt-c-premisa.md) | Parakeet con filtro Silero, y Gemma 4 E2B solo con `c-premisa-corte-riesgo` | [§5.5.1](CAP-05-DISENO-Y-ARQUITECTURA.md#551-detector) y [§5.5.3](CAP-05-DISENO-Y-ARQUITECTURA.md#553-reconocimiento-de-voz) |
