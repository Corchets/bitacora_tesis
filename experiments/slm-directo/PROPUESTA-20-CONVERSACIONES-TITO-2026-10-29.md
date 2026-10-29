# Selección aprobada de 20 conversaciones para comparar Tito viejo y nuevo

Fecha: 2026-10-29. Registrada en: [#101](https://github.com/Corchets/bitacora_tesis/issues/101); consolidación posterior en [#102](https://github.com/Corchets/bitacora_tesis/issues/102).

> **Estado: selección aprobada por el usuario el 2026-10-29.** Confirmación: «si estan bien». IDs registrados en [#101](https://github.com/Corchets/bitacora_tesis/issues/101), fuente del compromiso de prueba. No cierra [D08](../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental). Se conserva el nombre de archivo para mantener los enlaces de revisión.

Se seleccionaron 10 conversaciones de clase autoral `estafa` y 10 de clase autoral `legitima`. La proporción 10/10 fue aprobada junto con la lista. Abrir cada ID para leer su diálogo completo en la fuente original. Son textos sintéticos de desarrollo, no grabaciones de llamadas reales.

Las mismas 20 se recorrerán con SLM directo, Tito viejo→SLM y Tito nuevo→SLM para cada uno de los diez modelos acordados: 600 recorridos en #101. Esta selección no fija los tamaños de entrenamiento, validación ni del diagnóstico #98.

Criterio de propuesta: diversidad de situaciones, solicitudes de códigos, permisos de acceso, dinero y documentación; contexto prolongado, evidencia repartida, negativas y solicitudes legítimas. No se ejecutaron modelos para elegir estos casos ni se seleccionó por su rendimiento. Las clases y resúmenes orientan esta revisión; no son una anotación ciega.

## Conversaciones aprobadas

| N.º | Texto completo | Situación | Líneas | Curación aprobada en #96 |
|---|---|---|---:|---|
| 1 | [CV2-D-V-BANCO-001](casos/texto/CV2-D-V-BANCO-001.txt) | Reclamo de cochera que deriva en pedido de código; negativa y contexto largo. | 38 | Conservada |
| 2 | [CV2-D-V-BANCO-002](casos/texto/CV2-D-V-BANCO-002.txt) | Supuesto banco pide autorizar un dispositivo ajeno; la persona acepta. | 31 | Conservada |
| 3 | [CV2-D-V-BANCO-007](casos/texto/CV2-D-V-BANCO-007.txt) | Cambio del teléfono receptor de verificaciones hacia un número ajeno. | 30 | Conservada |
| 4 | [CV2-D-V-WHATSAPP-002](casos/texto/CV2-D-V-WHATSAPP-002.txt) | Supuesto soporte de internet pide un código de WhatsApp; negativa. | 22 | Conservada |
| 5 | [CV2-D-V-WHATSAPP-006](casos/texto/CV2-D-V-WHATSAPP-006.txt) | Inscripción a cerámica: pedido indirecto repartido entre líneas tras charla larga. | 36 | Conservada con observaciones |
| 6 | [CV2-D-V-SOPORTE-003](casos/texto/CV2-D-V-SOPORTE-003.txt) | Supuesto soporte educativo solicita usuario y contraseña en una ficha. | 21 | Conservada |
| 7 | [CV2-D-V-SOPORTE-004](casos/texto/CV2-D-V-SOPORTE-004.txt) | Asistencia de facturación intenta obtener control remoto con el banco abierto. | 30 | Conservada con observaciones |
| 8 | [CV2-D-V-FAMILIAR-002](casos/texto/CV2-D-V-FAMILIAR-002.txt) | Supuesto hijo accidentado pide una transferencia urgente a una cuenta de terceros. | 29 | Conservada con observaciones |
| 9 | [CV2-D-V-ORGANISMO_PREVISIONAL-001](casos/texto/CV2-D-V-ORGANISMO_PREVISIONAL-001.txt) | Trámite de domicilio deriva en documentos y cambio de representante. | 27 | Conservada con observaciones |
| 10 | [CV2-D-V-PREMIO-004](casos/texto/CV2-D-V-PREMIO-004.txt) | Supuesto premio exige datos de tarjeta y código de seguridad; negativa. | 21 | Conservada |
| 11 | [CV2-D-L-BANCO-001](casos/texto/CV2-D-L-BANCO-001.txt) | Consulta por débito desconocido: gestión sin compartir credenciales. | 22 | Conservada |
| 12 | [CV2-D-L-BANCO-007](casos/texto/CV2-D-L-BANCO-007.txt) | La palabra «clave» describe un comercio; explicación del resumen. | 23 | Conservada |
| 13 | [CV2-D-L-DELIVERY-001](casos/texto/CV2-D-L-DELIVERY-001.txt) | Cambio de entrega, domicilio y contacto autorizado. | 24 | Conservada |
| 14 | [CV2-D-L-ESCUELA-001](casos/texto/CV2-D-L-ESCUELA-001.txt) | Coordinación de reunión escolar y autorización de retiro. | 24 | Conservada |
| 15 | [CV2-D-L-FAMILIAR-001](casos/texto/CV2-D-L-FAMILIAR-001.txt) | Organización de visita familiar, compras y cuidado de la abuela. | 24 | Conservada |
| 16 | [CV2-D-L-MEDICO-001](casos/texto/CV2-D-L-MEDICO-001.txt) | Reprogramación de turno y consulta de copago sin pago anticipado. | 25 | Conservada |
| 17 | [CV2-D-L-ORGANISMO_PREVISIONAL-001](casos/texto/CV2-D-L-ORGANISMO_PREVISIONAL-001.txt) | Consulta de trámite y documentación para presentar en oficina. | 24 | Conservada |
| 18 | [CV2-D-L-PREMIO-001](casos/texto/CV2-D-L-PREMIO-001.txt) | Consulta de rifa ya pagada, sin pedir otro pago ni credenciales. | 24 | Conservada |
| 19 | [CV2-D-L-SOPORTE-002](casos/texto/CV2-D-L-SOPORTE-002.txt) | Recuperación de acceso desde la página habitual sin revelar contraseña. | 26 | Conservada |
| 20 | [CV2-D-L-WHATSAPP-001](casos/texto/CV2-D-L-WHATSAPP-001.txt) | Orientación para ingresar un código en la aplicación oficial, sin dictarlo. | 23 | Conservada |

## Antes de ejecutar

Los veinte IDs están conservados en la [selección de #96](SELECCION-TITO-2026-10-28.json). Cuatro tienen observaciones de curación: WhatsApp-006, soporte-004, familiar-002 y organismo previsional-001 (todos `CV2-D-V-*`); sus detalles y ajustes propuestos se consultan en la [curación](CURACION-TITO-2026-10-28.md). La aprobación no cambia los textos ni las referencias.

El manifiesto los identifica como `desarrollo_sin_independencia_acreditada`. Antes de habilitarlos como evaluación independiente, auditar exposición histórica y relaciones con entrenamiento/validación/diagnóstico, mantener juntos los grupos relacionados y separar estos casos de los usados para ajustar o seleccionar al Tito nuevo. La aprobación visual de esta lista no acredita por sí sola independencia ni nuevas anotaciones. No se accedió a la reserva final.

La selección aprobada está registrada en #101 y referenciada en #102. Antes de ejecutar, completar el manifiesto de ejecución con hashes, partición y procedencia; cualquier sustitución debe quedar explícita.
