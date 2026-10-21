# Qué grabar para probar ASR — corpus v2

Fecha: 2026-10-21. Lista de preparación para Luciano Grosso. Todos los diálogos son ficticios.

> **Estado: propuesta sin discutir.** La selección es una primera prueba exploratoria de ASR,
> no un tamaño mínimo validado ni la evaluación final. Se vincula con
> [D08](../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).
> La habilitación de tomas, consentimiento y resguardo siguen en
> [D06](../../../docs/gestion/MAPA-DECISIONES.md#d06--definir-corpus-y-piloto).

## 1. Grabá primero estos 24

Son 12 vishing y 12 legítimas de **desarrollo**, con dos casos por cada una de las seis
acciones críticas y situaciones legítimas con datos, transferencias y charla cotidiana.
Hay 23 casos nuevos y un antecedente de 12 líneas que ya ofrece un pedido legítimo de DNI.
Los textos elegidos son limpios: no hay que leer errores artificiales de transcripción.

| ID y guion | Clase | Líneas | Qué interesa escuchar en el ASR |
|---|---|---:|---|
| [CV2-D-V-BANCO-001](texto/CV2-D-V-BANCO-001.txt) | vishing | 38 | Pedido tardío en una charla extensa; el atacante es B. Retención de contexto y cifras del aviso. |
| [CV2-D-V-WHATSAPP-006](texto/CV2-D-V-WHATSAPP-006.txt) | vishing | 36 | Pedido indirecto partido en dos líneas; dictado de seis cifras con ceros después de una charla larga. |
| [CV2-D-V-SOPORTE-001](texto/CV2-D-V-SOPORTE-001.txt) | vishing | 20 | Credenciales dentro de instrucciones de soporte; distinguir el campo de ingreso de un relato. |
| [CV2-D-V-PREMIO-004](texto/CV2-D-V-PREMIO-004.txt) | vishing | 20 | Datos de tarjeta y CVV solicitados de forma indirecta; preservar negaciones y preguntas de aclaración. |
| [CV2-D-V-ORGANISMO_PREVISIONAL-001](texto/CV2-D-V-ORGANISMO_PREVISIONAL-001.txt) | vishing | 20 | DNI y fecha de nacimiento; dictado de números y parentesco del titular. |
| [CV2-D-V-PREMIO-003](texto/CV2-D-V-PREMIO-003.txt) | vishing | 20 | Solicitud indirecta de documento; distinguir descripción del formulario e instrucción de completarlo. |
| [CV2-D-V-BANCO-008](texto/CV2-D-V-BANCO-008.txt) | vishing | 22 | Entrega de efectivo solicitada sin empezar por nombrar una transferencia; objeción y cuantificadores. |
| [CV2-D-V-FAMILIAR-002](texto/CV2-D-V-FAMILIAR-002.txt) | vishing | 20 | Transferencia bajo suplantación familiar; importe y confirmación de ejecución. |
| [CV2-D-V-SOPORTE-002](texto/CV2-D-V-SOPORTE-002.txt) | vishing | 24 | Instalación y acceso remoto: secuencia de pasos, número de sesión y cumplimiento. |
| [CV2-D-V-SOPORTE-004](texto/CV2-D-V-SOPORTE-004.txt) | vishing | 20 | Permiso de control remoto expresado con eufemismos; distinguirlo de mirar la propia pantalla. |
| [CV2-D-V-BANCO-002](texto/CV2-D-V-BANCO-002.txt) | vishing | 20 | Autorización de dispositivo presentada como gestión bancaria; conservar el sentido de alta/baja. |
| [CV2-D-V-BANCO-007](texto/CV2-D-V-BANCO-007.txt) | vishing | 20 | Cambio de dispositivo inducido; referencia de una acción a lo dicho en turnos previos. |
| [CV2-D-L-BANCO-002](texto/CV2-D-L-BANCO-002.txt) | legítima | 24 | La persona llama al banco; pide comprobante de una transferencia ya realizada y confirma referencias limitadas. |
| [CV2-D-L-BANCO-007](texto/CV2-D-L-BANCO-007.txt) | legítima | 23 | La palabra clave describe el resumen; cambios de tema y autocorrección farmacia/ferretería. |
| [CV2-D-L-FAMILIAR-002](texto/CV2-D-L-FAMILIAR-002.txt) | legítima | 25 | Transferencia familiar normal, con pedido y ejecución; contraste con suplantación sin depender de la palabra transferir. |
| [CV2-D-L-FAMILIAR-005](texto/CV2-D-L-FAMILIAR-005.txt) | legítima | 27 | Otro gasto compartido con transferencia legítima; importe, acuerdo y recepción. |
| [CV2-D-L-DELIVERY-004](texto/CV2-D-L-DELIVERY-004.txt) | legítima | 24 | Reprogramación de entrega: horarios, número de pedido y acceso al edificio. |
| [TR-13-turno-medico-pide-dni](texto/TR-13-turno-medico-pide-dni.txt) | legítima | 12 | Antecedente útil: la persona llama por un turno y dicta DNI y nacimiento. Caso limpio de pedido legítimo de datos. |
| [CV2-D-L-ESCUELA-001](texto/CV2-D-L-ESCUELA-001.txt) | legítima | 24 | Llamada escolar cotidiana, horarios y coordinación de personas; voz sin vocabulario deliberado de fraude. |
| [CV2-D-L-TRABAJO-003](texto/CV2-D-L-TRABAJO-003.txt) | legítima | 25 | Coordinación laboral: nombres de objetos, referencias y aclaraciones en habla cotidiana. |
| [CV2-D-L-WHATSAPP-004](texto/CV2-D-L-WHATSAPP-004.txt) | legítima | 25 | Relato de un código recibido en otra ocasión; menciones y acciones de notificación sin solicitar el OTP. |
| [CV2-D-L-SOPORTE-001](texto/CV2-D-L-SOPORTE-001.txt) | legítima | 25 | La persona llama por un corte de internet: domicilio, teléfono parcial y visita técnica legítima. |
| [CV2-D-L-ORGANISMO_PREVISIONAL-001](texto/CV2-D-L-ORGANISMO_PREVISIONAL-001.txt) | legítima | 24 | Consulta iniciada sobre una prestación y confirmación razonable de datos; contraste con falso beneficio. |
| [CV2-D-L-PREMIO-001](texto/CV2-D-L-PREMIO-001.txt) | legítima | 24 | Consulta legítima de promoción: datos de participación y aclaración de condiciones. |

Interpretá con otra persona adulta, usando A/B para distribuir las intervenciones; no leas
los prefijos ni los metadatos. Una clase no determina el tono: también hay urgencias
y pedidos de dinero legítimos. Conservá el ID del caso para vincular cada toma con el guion.

El audio, los consentimientos y cualquier dato identificable quedan fuera de Git. El
[kit del primer par](../../../docs/corpus/KIT-PRIMER-PAR.md) y el
[método del corpus](../../../docs/corpus/METODO-CREACION-CORPUS.md) contienen el procedimiento.
Si improvisás o cambiás una frase, la referencia para ASR debe transcribir lo realmente
grabado: no se compara contra el guion como si fuera una transcripción exacta.
Las marcas por línea no se convierten a segundos; los tiempos se anotan sobre el audio.

## 2. No hace falta grabar estos 126 para la primera prueba

Alcanza con probarlos como texto en esta etapa. No se descartan: si el ASR muestra
un error que esta selección no cubre, se revisa qué toma adicional aporta información.
Las variantes `variante_asr:true` prueban robustez del detector ante texto alterado,
pero no prueban el ASR y no se deben leer literalmente para simular sus fallos.

| ID y guion | Motivo para postergar |
|---|---|
| [CV2-D-L-BANCO-001](texto/CV2-D-L-BANCO-001.txt) | Variante escrita de ASR: probar como texto; requiere referencia limpia si se selecciona después. |
| [CV2-D-L-BANCO-003](texto/CV2-D-L-BANCO-003.txt) | Caso de desarrollo adicional; la primera selección ya cubre la acción o el contexto general. |
| [CV2-D-L-BANCO-004](texto/CV2-D-L-BANCO-004.txt) | Caso de desarrollo adicional; la primera selección ya cubre la acción o el contexto general. |
| [CV2-D-L-BANCO-005](texto/CV2-D-L-BANCO-005.txt) | Caso de desarrollo adicional; la primera selección ya cubre la acción o el contexto general. |
| [CV2-D-L-BANCO-006](texto/CV2-D-L-BANCO-006.txt) | Caso de desarrollo adicional; la primera selección ya cubre la acción o el contexto general. |
| [CV2-D-L-BANCO-008](texto/CV2-D-L-BANCO-008.txt) | Caso de desarrollo adicional; la primera selección ya cubre la acción o el contexto general. |
| [CV2-D-L-BANCO-009](texto/CV2-D-L-BANCO-009.txt) | Caso de desarrollo adicional; la primera selección ya cubre la acción o el contexto general. |
| [CV2-D-L-BANCO-010](texto/CV2-D-L-BANCO-010.txt) | Variante escrita de ASR: probar como texto; requiere referencia limpia si se selecciona después. |
| [CV2-D-L-DELIVERY-001](texto/CV2-D-L-DELIVERY-001.txt) | Variante escrita de ASR: probar como texto; requiere referencia limpia si se selecciona después. |
| [CV2-D-L-DELIVERY-002](texto/CV2-D-L-DELIVERY-002.txt) | Caso de desarrollo adicional; la primera selección ya cubre la acción o el contexto general. |
| [CV2-D-L-DELIVERY-003](texto/CV2-D-L-DELIVERY-003.txt) | Variante escrita de ASR: probar como texto; requiere referencia limpia si se selecciona después. |
| [CV2-D-L-DELIVERY-005](texto/CV2-D-L-DELIVERY-005.txt) | Caso de desarrollo adicional; la primera selección ya cubre la acción o el contexto general. |
| [CV2-D-L-ESCUELA-002](texto/CV2-D-L-ESCUELA-002.txt) | Variante escrita de ASR: probar como texto; requiere referencia limpia si se selecciona después. |
| [CV2-D-L-ESCUELA-003](texto/CV2-D-L-ESCUELA-003.txt) | Caso de desarrollo adicional; la primera selección ya cubre la acción o el contexto general. |
| [CV2-D-L-ESCUELA-004](texto/CV2-D-L-ESCUELA-004.txt) | Caso de desarrollo adicional; la primera selección ya cubre la acción o el contexto general. |
| [CV2-D-L-ESCUELA-005](texto/CV2-D-L-ESCUELA-005.txt) | Variante escrita de ASR: probar como texto; requiere referencia limpia si se selecciona después. |
| [CV2-D-L-FAMILIAR-001](texto/CV2-D-L-FAMILIAR-001.txt) | Caso de desarrollo adicional; la primera selección ya cubre la acción o el contexto general. |
| [CV2-D-L-FAMILIAR-003](texto/CV2-D-L-FAMILIAR-003.txt) | Caso de desarrollo adicional; la primera selección ya cubre la acción o el contexto general. |
| [CV2-D-L-FAMILIAR-004](texto/CV2-D-L-FAMILIAR-004.txt) | Caso de desarrollo adicional; la primera selección ya cubre la acción o el contexto general. |
| [CV2-D-L-MEDICO-001](texto/CV2-D-L-MEDICO-001.txt) | Caso de desarrollo adicional; la primera selección ya cubre la acción o el contexto general. |
| [CV2-D-L-MEDICO-002](texto/CV2-D-L-MEDICO-002.txt) | Variante escrita de ASR: probar como texto; requiere referencia limpia si se selecciona después. |
| [CV2-D-L-MEDICO-003](texto/CV2-D-L-MEDICO-003.txt) | Caso de desarrollo adicional; la primera selección ya cubre la acción o el contexto general. |
| [CV2-D-L-MEDICO-004](texto/CV2-D-L-MEDICO-004.txt) | Variante escrita de ASR: probar como texto; requiere referencia limpia si se selecciona después. |
| [CV2-D-L-MEDICO-005](texto/CV2-D-L-MEDICO-005.txt) | Caso de desarrollo adicional; la primera selección ya cubre la acción o el contexto general. |
| [CV2-D-L-ORGANISMO_PREVISIONAL-002](texto/CV2-D-L-ORGANISMO_PREVISIONAL-002.txt) | Caso de desarrollo adicional; la primera selección ya cubre la acción o el contexto general. |
| [CV2-D-L-ORGANISMO_PREVISIONAL-003](texto/CV2-D-L-ORGANISMO_PREVISIONAL-003.txt) | Variante escrita de ASR: probar como texto; requiere referencia limpia si se selecciona después. |
| [CV2-D-L-PREMIO-002](texto/CV2-D-L-PREMIO-002.txt) | Caso de desarrollo adicional; la primera selección ya cubre la acción o el contexto general. |
| [CV2-D-L-PREMIO-003](texto/CV2-D-L-PREMIO-003.txt) | Caso de desarrollo adicional; la primera selección ya cubre la acción o el contexto general. |
| [CV2-D-L-SOPORTE-002](texto/CV2-D-L-SOPORTE-002.txt) | Caso de desarrollo adicional; la primera selección ya cubre la acción o el contexto general. |
| [CV2-D-L-SOPORTE-003](texto/CV2-D-L-SOPORTE-003.txt) | Caso de desarrollo adicional; la primera selección ya cubre la acción o el contexto general. |
| [CV2-D-L-SOPORTE-004](texto/CV2-D-L-SOPORTE-004.txt) | Caso de desarrollo adicional; la primera selección ya cubre la acción o el contexto general. |
| [CV2-D-L-SOPORTE-005](texto/CV2-D-L-SOPORTE-005.txt) | Caso de desarrollo adicional; la primera selección ya cubre la acción o el contexto general. |
| [CV2-D-L-TRABAJO-001](texto/CV2-D-L-TRABAJO-001.txt) | Variante escrita de ASR: probar como texto; requiere referencia limpia si se selecciona después. |
| [CV2-D-L-TRABAJO-002](texto/CV2-D-L-TRABAJO-002.txt) | Variante escrita de ASR: probar como texto; requiere referencia limpia si se selecciona después. |
| [CV2-D-L-TRABAJO-004](texto/CV2-D-L-TRABAJO-004.txt) | Caso de desarrollo adicional; la primera selección ya cubre la acción o el contexto general. |
| [CV2-D-L-TRABAJO-005](texto/CV2-D-L-TRABAJO-005.txt) | Caso de desarrollo adicional; la primera selección ya cubre la acción o el contexto general. |
| [CV2-D-L-WHATSAPP-001](texto/CV2-D-L-WHATSAPP-001.txt) | Caso de desarrollo adicional; la primera selección ya cubre la acción o el contexto general. |
| [CV2-D-L-WHATSAPP-002](texto/CV2-D-L-WHATSAPP-002.txt) | Caso de desarrollo adicional; la primera selección ya cubre la acción o el contexto general. |
| [CV2-D-L-WHATSAPP-003](texto/CV2-D-L-WHATSAPP-003.txt) | Caso de desarrollo adicional; la primera selección ya cubre la acción o el contexto general. |
| [CV2-D-L-WHATSAPP-005](texto/CV2-D-L-WHATSAPP-005.txt) | Variante escrita de ASR: probar como texto; requiere referencia limpia si se selecciona después. |
| [CV2-D-V-BANCO-003](texto/CV2-D-V-BANCO-003.txt) | Variante escrita de ASR: probar como texto; requiere referencia limpia si se selecciona después. |
| [CV2-D-V-BANCO-004](texto/CV2-D-V-BANCO-004.txt) | Caso de desarrollo adicional; la primera selección ya cubre la acción o el contexto general. |
| [CV2-D-V-BANCO-005](texto/CV2-D-V-BANCO-005.txt) | Variante escrita de ASR: probar como texto; requiere referencia limpia si se selecciona después. |
| [CV2-D-V-BANCO-006](texto/CV2-D-V-BANCO-006.txt) | Caso de desarrollo adicional; la primera selección ya cubre la acción o el contexto general. |
| [CV2-D-V-BANCO-009](texto/CV2-D-V-BANCO-009.txt) | Variante escrita de ASR: probar como texto; requiere referencia limpia si se selecciona después. |
| [CV2-D-V-BANCO-010](texto/CV2-D-V-BANCO-010.txt) | Caso de desarrollo adicional; la primera selección ya cubre la acción o el contexto general. |
| [CV2-D-V-BANCO-011](texto/CV2-D-V-BANCO-011.txt) | Caso de desarrollo adicional; la primera selección ya cubre la acción o el contexto general. |
| [CV2-D-V-BANCO-012](texto/CV2-D-V-BANCO-012.txt) | Caso de desarrollo adicional; la primera selección ya cubre la acción o el contexto general. |
| [CV2-D-V-FAMILIAR-001](texto/CV2-D-V-FAMILIAR-001.txt) | Variante escrita de ASR: probar como texto; requiere referencia limpia si se selecciona después. |
| [CV2-D-V-FAMILIAR-003](texto/CV2-D-V-FAMILIAR-003.txt) | Caso de desarrollo adicional; la primera selección ya cubre la acción o el contexto general. |
| [CV2-D-V-FAMILIAR-004](texto/CV2-D-V-FAMILIAR-004.txt) | Caso de desarrollo adicional; la primera selección ya cubre la acción o el contexto general. |
| [CV2-D-V-FAMILIAR-005](texto/CV2-D-V-FAMILIAR-005.txt) | Caso de desarrollo adicional; la primera selección ya cubre la acción o el contexto general. |
| [CV2-D-V-FAMILIAR-006](texto/CV2-D-V-FAMILIAR-006.txt) | Caso de desarrollo adicional; la primera selección ya cubre la acción o el contexto general. |
| [CV2-D-V-ORGANISMO_PREVISIONAL-002](texto/CV2-D-V-ORGANISMO_PREVISIONAL-002.txt) | Variante escrita de ASR: probar como texto; requiere referencia limpia si se selecciona después. |
| [CV2-D-V-ORGANISMO_PREVISIONAL-003](texto/CV2-D-V-ORGANISMO_PREVISIONAL-003.txt) | Caso de desarrollo adicional; la primera selección ya cubre la acción o el contexto general. |
| [CV2-D-V-ORGANISMO_PREVISIONAL-004](texto/CV2-D-V-ORGANISMO_PREVISIONAL-004.txt) | Variante escrita de ASR: probar como texto; requiere referencia limpia si se selecciona después. |
| [CV2-D-V-ORGANISMO_PREVISIONAL-005](texto/CV2-D-V-ORGANISMO_PREVISIONAL-005.txt) | Caso de desarrollo adicional; la primera selección ya cubre la acción o el contexto general. |
| [CV2-D-V-ORGANISMO_PREVISIONAL-006](texto/CV2-D-V-ORGANISMO_PREVISIONAL-006.txt) | Caso de desarrollo adicional; la primera selección ya cubre la acción o el contexto general. |
| [CV2-D-V-PREMIO-001](texto/CV2-D-V-PREMIO-001.txt) | Caso de desarrollo adicional; la primera selección ya cubre la acción o el contexto general. |
| [CV2-D-V-PREMIO-002](texto/CV2-D-V-PREMIO-002.txt) | Variante escrita de ASR: probar como texto; requiere referencia limpia si se selecciona después. |
| [CV2-D-V-PREMIO-005](texto/CV2-D-V-PREMIO-005.txt) | Variante escrita de ASR: probar como texto; requiere referencia limpia si se selecciona después. |
| [CV2-D-V-PREMIO-006](texto/CV2-D-V-PREMIO-006.txt) | Caso de desarrollo adicional; la primera selección ya cubre la acción o el contexto general. |
| [CV2-D-V-SOPORTE-003](texto/CV2-D-V-SOPORTE-003.txt) | Variante escrita de ASR: probar como texto; requiere referencia limpia si se selecciona después. |
| [CV2-D-V-SOPORTE-005](texto/CV2-D-V-SOPORTE-005.txt) | Caso de desarrollo adicional; la primera selección ya cubre la acción o el contexto general. |
| [CV2-D-V-SOPORTE-006](texto/CV2-D-V-SOPORTE-006.txt) | Variante escrita de ASR: probar como texto; requiere referencia limpia si se selecciona después. |
| [CV2-D-V-SOPORTE-007](texto/CV2-D-V-SOPORTE-007.txt) | Caso de desarrollo adicional; la primera selección ya cubre la acción o el contexto general. |
| [CV2-D-V-SOPORTE-008](texto/CV2-D-V-SOPORTE-008.txt) | Caso de desarrollo adicional; la primera selección ya cubre la acción o el contexto general. |
| [CV2-D-V-WHATSAPP-001](texto/CV2-D-V-WHATSAPP-001.txt) | Variante escrita de ASR: probar como texto; requiere referencia limpia si se selecciona después. |
| [CV2-D-V-WHATSAPP-002](texto/CV2-D-V-WHATSAPP-002.txt) | Caso de desarrollo adicional; la primera selección ya cubre la acción o el contexto general. |
| [CV2-D-V-WHATSAPP-003](texto/CV2-D-V-WHATSAPP-003.txt) | Variante escrita de ASR: probar como texto; requiere referencia limpia si se selecciona después. |
| [CV2-D-V-WHATSAPP-004](texto/CV2-D-V-WHATSAPP-004.txt) | Caso de desarrollo adicional; la primera selección ya cubre la acción o el contexto general. |
| [CV2-D-V-WHATSAPP-005](texto/CV2-D-V-WHATSAPP-005.txt) | Caso de desarrollo adicional; la primera selección ya cubre la acción o el contexto general. |
| [CV2-D-V-WHATSAPP-007](texto/CV2-D-V-WHATSAPP-007.txt) | Caso de desarrollo adicional; la primera selección ya cubre la acción o el contexto general. |
| [CV2-D-V-WHATSAPP-008](texto/CV2-D-V-WHATSAPP-008.txt) | Caso de desarrollo adicional; la primera selección ya cubre la acción o el contexto general. |
| [LAB-acceso-remoto](texto/LAB-acceso-remoto.txt) | Antecedente conservado para reproducir corridas; no prioritario para ampliar la primera muestra de voz. |
| [LAB-acceso-remoto-parafrasis](texto/LAB-acceso-remoto-parafrasis.txt) | Antecedente conservado para reproducir corridas; no prioritario para ampliar la primera muestra de voz. |
| [LAB-anses-beneficio](texto/LAB-anses-beneficio.txt) | Antecedente conservado para reproducir corridas; no prioritario para ampliar la primera muestra de voz. |
| [LAB-anses-beneficio-parafrasis](texto/LAB-anses-beneficio-parafrasis.txt) | Antecedente conservado para reproducir corridas; no prioritario para ampliar la primera muestra de voz. |
| [LAB-anses-canal-oficial](texto/LAB-anses-canal-oficial.txt) | Antecedente conservado para reproducir corridas; no prioritario para ampliar la primera muestra de voz. |
| [LAB-arca-canal-oficial](texto/LAB-arca-canal-oficial.txt) | Antecedente conservado para reproducir corridas; no prioritario para ampliar la primera muestra de voz. |
| [LAB-arca-deuda](texto/LAB-arca-deuda.txt) | Antecedente conservado para reproducir corridas; no prioritario para ampliar la primera muestra de voz. |
| [LAB-arca-deuda-parafrasis](texto/LAB-arca-deuda-parafrasis.txt) | Antecedente conservado para reproducir corridas; no prioritario para ampliar la primera muestra de voz. |
| [LAB-banco-app-parafrasis](texto/LAB-banco-app-parafrasis.txt) | Antecedente conservado para reproducir corridas; no prioritario para ampliar la primera muestra de voz. |
| [LAB-banco-codigo](texto/LAB-banco-codigo.txt) | Antecedente conservado para reproducir corridas; no prioritario para ampliar la primera muestra de voz. |
| [LAB-banco-codigo-parafrasis](texto/LAB-banco-codigo-parafrasis.txt) | Antecedente conservado para reproducir corridas; no prioritario para ampliar la primera muestra de voz. |
| [LAB-banco-gasto-sin-pedido](texto/LAB-banco-gasto-sin-pedido.txt) | Antecedente conservado para reproducir corridas; no prioritario para ampliar la primera muestra de voz. |
| [LAB-banco-niega-el-codigo](texto/LAB-banco-niega-el-codigo.txt) | Antecedente conservado para reproducir corridas; no prioritario para ampliar la primera muestra de voz. |
| [LAB-banco-numeros-sin-clave](texto/LAB-banco-numeros-sin-clave.txt) | Antecedente conservado para reproducir corridas; no prioritario para ampliar la primera muestra de voz. |
| [LAB-banco-revisa-app](texto/LAB-banco-revisa-app.txt) | Antecedente conservado para reproducir corridas; no prioritario para ampliar la primera muestra de voz. |
| [LAB-digitos-sin-palabra](texto/LAB-digitos-sin-palabra.txt) | Antecedente conservado para reproducir corridas; no prioritario para ampliar la primera muestra de voz. |
| [LAB-familiar-llama-vos](texto/LAB-familiar-llama-vos.txt) | Antecedente conservado para reproducir corridas; no prioritario para ampliar la primera muestra de voz. |
| [LAB-familiar-peligro](texto/LAB-familiar-peligro.txt) | Antecedente conservado para reproducir corridas; no prioritario para ampliar la primera muestra de voz. |
| [LAB-familiar-peligro-parafrasis](texto/LAB-familiar-peligro-parafrasis.txt) | Antecedente conservado para reproducir corridas; no prioritario para ampliar la primera muestra de voz. |
| [LAB-giro-sin-plata](texto/LAB-giro-sin-plata.txt) | Antecedente conservado para reproducir corridas; no prioritario para ampliar la primera muestra de voz. |
| [LAB-mensajeria-no-pases-nada](texto/LAB-mensajeria-no-pases-nada.txt) | Antecedente conservado para reproducir corridas; no prioritario para ampliar la primera muestra de voz. |
| [LAB-no-bajes-nada](texto/LAB-no-bajes-nada.txt) | Antecedente conservado para reproducir corridas; no prioritario para ampliar la primera muestra de voz. |
| [LAB-pantalla-sin-programa](texto/LAB-pantalla-sin-programa.txt) | Antecedente conservado para reproducir corridas; no prioritario para ampliar la primera muestra de voz. |
| [LAB-portero-codigo-puerta](texto/LAB-portero-codigo-puerta.txt) | Antecedente conservado para reproducir corridas; no prioritario para ampliar la primera muestra de voz. |
| [LAB-whatsapp-codigo](texto/LAB-whatsapp-codigo.txt) | Antecedente conservado para reproducir corridas; no prioritario para ampliar la primera muestra de voz. |
| [LAB-whatsapp-codigo-parafrasis](texto/LAB-whatsapp-codigo-parafrasis.txt) | Antecedente conservado para reproducir corridas; no prioritario para ampliar la primera muestra de voz. |
| [LG-BANK-VERIF-01-e01](texto/LG-BANK-VERIF-01-e01.txt) | Antecedente conservado para reproducir corridas; no prioritario para ampliar la primera muestra de voz. |
| [LG-FAMILIAR-LLAMADO-01-e01](texto/LG-FAMILIAR-LLAMADO-01-e01.txt) | Antecedente conservado para reproducir corridas; no prioritario para ampliar la primera muestra de voz. |
| [LG-ORG-TURNO-01-e01](texto/LG-ORG-TURNO-01-e01.txt) | Antecedente conservado para reproducir corridas; no prioritario para ampliar la primera muestra de voz. |
| [LG-PREMIO-CONSULTA-01-e01](texto/LG-PREMIO-CONSULTA-01-e01.txt) | Antecedente conservado para reproducir corridas; no prioritario para ampliar la primera muestra de voz. |
| [LG-SUPPORT-INFO-01-e01](texto/LG-SUPPORT-INFO-01-e01.txt) | Antecedente conservado para reproducir corridas; no prioritario para ampliar la primera muestra de voz. |
| [LG-SUPPORT-INFO-01-e02](texto/LG-SUPPORT-INFO-01-e02.txt) | Antecedente conservado para reproducir corridas; no prioritario para ampliar la primera muestra de voz. |
| [LG-WA-CONSULTA-01-e01](texto/LG-WA-CONSULTA-01-e01.txt) | Antecedente conservado para reproducir corridas; no prioritario para ampliar la primera muestra de voz. |
| [SC-CLAVE-CAMBIO-01-e01](texto/SC-CLAVE-CAMBIO-01-e01.txt) | Antecedente conservado para reproducir corridas; no prioritario para ampliar la primera muestra de voz. |
| [SC-FAMILIAR-DINERO-01-e01](texto/SC-FAMILIAR-DINERO-01-e01.txt) | Antecedente conservado para reproducir corridas; no prioritario para ampliar la primera muestra de voz. |
| [SC-ORG-BENEFICIO-01-e01](texto/SC-ORG-BENEFICIO-01-e01.txt) | Antecedente conservado para reproducir corridas; no prioritario para ampliar la primera muestra de voz. |
| [SC-PREMIO-01-e01](texto/SC-PREMIO-01-e01.txt) | Antecedente conservado para reproducir corridas; no prioritario para ampliar la primera muestra de voz. |
| [SC-SOPORTE-CLAVE-01-e01](texto/SC-SOPORTE-CLAVE-01-e01.txt) | Antecedente conservado para reproducir corridas; no prioritario para ampliar la primera muestra de voz. |
| [SC-SOPORTE-REMOTO-01-e01](texto/SC-SOPORTE-REMOTO-01-e01.txt) | Antecedente conservado para reproducir corridas; no prioritario para ampliar la primera muestra de voz. |
| [SC-WA-CODE-01-e01](texto/SC-WA-CODE-01-e01.txt) | Antecedente conservado para reproducir corridas; no prioritario para ampliar la primera muestra de voz. |
| [TR-01-pedido-indirecto-digitos](texto/TR-01-pedido-indirecto-digitos.txt) | Antecedente conservado para reproducir corridas; no prioritario para ampliar la primera muestra de voz. |
| [TR-02-codigo-del-candado](texto/TR-02-codigo-del-candado.txt) | Antecedente conservado para reproducir corridas; no prioritario para ampliar la primera muestra de voz. |
| [TR-03-negacion-y-consejo](texto/TR-03-negacion-y-consejo.txt) | Antecedente conservado para reproducir corridas; no prioritario para ampliar la primera muestra de voz. |
| [TR-04-pedido-tras-charla-larga](texto/TR-04-pedido-tras-charla-larga.txt) | Antecedente conservado para reproducir corridas; no prioritario para ampliar la primera muestra de voz. |
| [TR-05-asado-con-transferencia](texto/TR-05-asado-con-transferencia.txt) | Antecedente conservado para reproducir corridas; no prioritario para ampliar la primera muestra de voz. |
| [TR-06-banco-alerta-legitima](texto/TR-06-banco-alerta-legitima.txt) | Antecedente conservado para reproducir corridas; no prioritario para ampliar la primera muestra de voz. |
| [TR-07-pedido-partido-en-dos-lineas](texto/TR-07-pedido-partido-en-dos-lineas.txt) | Antecedente conservado para reproducir corridas; no prioritario para ampliar la primera muestra de voz. |
| [TR-08-frase-cortada-candado](texto/TR-08-frase-cortada-candado.txt) | Antecedente conservado para reproducir corridas; no prioritario para ampliar la primera muestra de voz. |
| [TR-09-victima-se-niega](texto/TR-09-victima-se-niega.txt) | Antecedente conservado para reproducir corridas; no prioritario para ampliar la primera muestra de voz. |
| [TR-10-ofrecimiento-inducido](texto/TR-10-ofrecimiento-inducido.txt) | Antecedente conservado para reproducir corridas; no prioritario para ampliar la primera muestra de voz. |
| [TR-11-familiar-real-pide-plata](texto/TR-11-familiar-real-pide-plata.txt) | Antecedente conservado para reproducir corridas; no prioritario para ampliar la primera muestra de voz. |
| [TR-12-corta-antes-del-pedido](texto/TR-12-corta-antes-del-pedido.txt) | Antecedente conservado para reproducir corridas; no prioritario para ampliar la primera muestra de voz. |

## 3. Estos 200 quedan reservados: no grabarlos para afinar ahora

No hace falta grabarlos para desarrollar el detector o comparar ASR sobre el lote inicial.
Pueden necesitar audio para una evaluación final independiente del sistema completo:
eso se acuerda en D08 antes de medir, con las referencias revisadas en D07.
Las 24 grabaciones de desarrollo no demuestran una meta 95/5 del flujo con ASR.
Los IDs siguientes solo identifican la reserva; sus textos y referencias no se incorporan
al panel de desarrollo. No se eligen modelos, prompts, reglas ni umbrales con ellos.

| ID reservado | Uso en esta etapa |
|---|---|
| `CV2-T-L-BANCO-001` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-BANCO-002` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-BANCO-003` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-BANCO-004` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-BANCO-005` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-BANCO-006` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-BANCO-007` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-BANCO-008` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-BANCO-009` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-BANCO-010` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-BANCO-011` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-BANCO-012` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-BANCO-013` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-BANCO-014` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-BANCO-015` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-BANCO-016` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-BANCO-017` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-BANCO-018` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-BANCO-019` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-BANCO-020` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-DELIVERY-001` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-DELIVERY-002` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-DELIVERY-003` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-DELIVERY-004` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-DELIVERY-005` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-DELIVERY-006` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-DELIVERY-007` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-DELIVERY-008` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-ESCUELA-001` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-ESCUELA-002` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-ESCUELA-003` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-ESCUELA-004` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-ESCUELA-005` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-ESCUELA-006` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-ESCUELA-007` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-ESCUELA-008` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-FAMILIAR-001` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-FAMILIAR-002` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-FAMILIAR-003` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-FAMILIAR-004` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-FAMILIAR-005` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-FAMILIAR-006` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-FAMILIAR-007` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-FAMILIAR-008` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-FAMILIAR-009` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-FAMILIAR-010` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-FAMILIAR-011` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-FAMILIAR-012` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-FAMILIAR-013` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-FAMILIAR-014` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-FAMILIAR-015` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-FAMILIAR-016` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-FAMILIAR-017` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-FAMILIAR-018` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-MEDICO-001` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-MEDICO-002` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-MEDICO-003` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-MEDICO-004` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-MEDICO-005` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-MEDICO-006` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-MEDICO-007` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-MEDICO-008` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-ORGANISMO_PREVISIONAL-001` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-ORGANISMO_PREVISIONAL-002` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-ORGANISMO_PREVISIONAL-003` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-ORGANISMO_PREVISIONAL-004` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-ORGANISMO_PREVISIONAL-005` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-ORGANISMO_PREVISIONAL-006` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-PREMIO-001` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-PREMIO-002` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-PREMIO-003` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-PREMIO-004` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-PREMIO-005` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-PREMIO-006` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-SOPORTE-001` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-SOPORTE-002` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-SOPORTE-003` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-SOPORTE-004` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-SOPORTE-005` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-SOPORTE-006` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-SOPORTE-007` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-SOPORTE-008` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-SOPORTE-009` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-SOPORTE-010` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-TRABAJO-001` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-TRABAJO-002` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-TRABAJO-003` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-TRABAJO-004` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-TRABAJO-005` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-TRABAJO-006` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-TRABAJO-007` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-TRABAJO-008` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-WHATSAPP-001` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-WHATSAPP-002` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-WHATSAPP-003` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-WHATSAPP-004` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-WHATSAPP-005` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-WHATSAPP-006` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-WHATSAPP-007` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-L-WHATSAPP-008` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-BANCO-001` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-BANCO-002` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-BANCO-003` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-BANCO-004` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-BANCO-005` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-BANCO-006` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-BANCO-007` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-BANCO-008` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-BANCO-009` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-BANCO-010` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-BANCO-011` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-BANCO-012` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-BANCO-013` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-BANCO-014` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-BANCO-015` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-BANCO-016` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-BANCO-017` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-BANCO-018` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-BANCO-019` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-BANCO-020` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-BANCO-021` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-BANCO-022` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-BANCO-023` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-BANCO-024` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-BANCO-025` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-FAMILIAR-001` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-FAMILIAR-002` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-FAMILIAR-003` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-FAMILIAR-004` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-FAMILIAR-005` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-FAMILIAR-006` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-FAMILIAR-007` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-FAMILIAR-008` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-FAMILIAR-009` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-FAMILIAR-010` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-FAMILIAR-011` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-FAMILIAR-012` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-FAMILIAR-013` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-FAMILIAR-014` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-FAMILIAR-015` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-ORGANISMO_PREVISIONAL-001` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-ORGANISMO_PREVISIONAL-002` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-ORGANISMO_PREVISIONAL-003` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-ORGANISMO_PREVISIONAL-004` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-ORGANISMO_PREVISIONAL-005` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-ORGANISMO_PREVISIONAL-006` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-ORGANISMO_PREVISIONAL-007` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-ORGANISMO_PREVISIONAL-008` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-ORGANISMO_PREVISIONAL-009` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-ORGANISMO_PREVISIONAL-010` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-PREMIO-001` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-PREMIO-002` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-PREMIO-003` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-PREMIO-004` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-PREMIO-005` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-PREMIO-006` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-PREMIO-007` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-PREMIO-008` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-PREMIO-009` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-PREMIO-010` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-PREMIO-011` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-PREMIO-012` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-PREMIO-013` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-PREMIO-014` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-PREMIO-015` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-SOPORTE-001` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-SOPORTE-002` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-SOPORTE-003` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-SOPORTE-004` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-SOPORTE-005` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-SOPORTE-006` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-SOPORTE-007` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-SOPORTE-008` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-SOPORTE-009` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-SOPORTE-010` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-SOPORTE-011` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-SOPORTE-012` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-SOPORTE-013` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-SOPORTE-014` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-SOPORTE-015` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-SOPORTE-016` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-SOPORTE-017` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-SOPORTE-018` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-SOPORTE-019` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-SOPORTE-020` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-WHATSAPP-001` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-WHATSAPP-002` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-WHATSAPP-003` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-WHATSAPP-004` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-WHATSAPP-005` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-WHATSAPP-006` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-WHATSAPP-007` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-WHATSAPP-008` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-WHATSAPP-009` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-WHATSAPP-010` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-WHATSAPP-011` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-WHATSAPP-012` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-WHATSAPP-013` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-WHATSAPP-014` | Reserva; postergar grabación hasta definir evaluación final. |
| `CV2-T-V-WHATSAPP-015` | Reserva; postergar grabación hasta definir evaluación final. |

Selección de trabajo: **24 grabar primero + 126 texto por ahora + 200 reserva = 350 casos**.
La revisión técnica y sus límites se registran en [REVISION-CORPUS-V2.md](REVISION-CORPUS-V2.md).
