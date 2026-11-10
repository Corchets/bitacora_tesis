# Muestras Exploratorias de Corpus Externo en Portugués (Issue #144)

**Fecha de elaboración:** 2026-11-06  
**Idioma analizado:** Portugués de Brasil  
**Investigador destinatario:** Luciano Grosso  
**Entrega local exclusiva:** `/Users/lucianogrosso/Downloads/ISSUE-144-PORTUGUES-2026-11-06.md`  
**Registro de procedencia:** `/Users/lucianogrosso/Downloads/ISSUE-144-PORTUGUES-2026-11-06-PROCEDENCIA.json`  

---

## 1. Encuadre Metodológico y Datos de la Fuente

### 1.1. Propósito y Carácter Exploratorio

El presente documento reúne dos casos traducidos íntegramente al español a partir del conjunto de datos sintético *ai-safety-brazil/pix-scam-challenge-br-synthetic* para permitir la lectura cualitativa de Luciano Grosso.

> **ESTADO METODOLÓGICO:**  
>
> - **Estado: propuesta sin discutir.** La recomendación de selección corresponde a [D08](https://github.com/Corchets/bitacora_tesis/blob/e467c7c/docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental). Esta entrega es una exploración previa. No declara aprobada ninguna fuente ni resuelve D03, D07 o D08. D09 ya figura resuelta en el mapa; esta entrega no la modifica.  
> - **Exclusión del test futuro:** Estas dos conversaciones leídas quedan excluidas del conjunto de prueba futuro para evitar contaminación por exposición previa de estos casos específicos.  
> - **Sin validación humana bilingüe:** La traducción fue realizada mediante asistencia de IA y no cuenta con validación humana bilingüe.

### 1.2. Datos de la Fuente y Licencia (CC BY 4.0)

- **Repositorio primario:** [ai-safety-brazil/pix-scam-challenge-br-synthetic en Hugging Face](https://huggingface.co/datasets/ai-safety-brazil/pix-scam-challenge-br-synthetic)
- **Revisión / Commit Git:** `acdc964b67fea50300fa82033af2ca9db86fbe4d` (versión 1.0.0, 2026-10-28)
- **Licencia:** CC BY 4.0 (datos) y MIT (código).
- **Atribución CC BY 4.0:** AI Safety Brazil, 2026. *PIX Scam Challenge BR — Synthetic* (v1.0.0). Se seleccionaron dos grupos emparejados para traducción y evaluación técnica de viabilidad.
- **Naturaleza:** Sintética (*silver synthetic*). Generado con `Qwen/Qwen3.6-35B-A3B` y clasificado por `nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16`. El registro de metadatos declara `human_reviewed: false` (sin revisión humana declarada por el registro de origen).
- **Límites de uso:** No contiene datos bancarios reales ni grabaciones sonoras reales. Texto traducido de uso local privado exclusivo fuera de Git.

### 1.3. Comprobación sobre los Dos Grupos Seleccionados

- **Diseño documentado en la fuente:** La ficha técnica describe 1.000 grupos de tres casos con diálogos compartidos y variantes de evidencia externa.
- **Comprobación en estos dos casos:** Se verificó directamente en los archivos provistos que en el grupo `b87dcd6c3c30c83372dd7a21` (6 turnos) y en el grupo `e24a2dc7241413744ff93451` (5 turnos), el campo `conversation` es estrictamente invariante entre sus tres filas (`scam_like`, `legitimate`, `insufficient_evidence`).
- **Consecuencia para un detector de solo conversación:** Como el diálogo es idéntico y las etiquetas difieren según la evidencia externa, un detector que procese exclusivamente la conversación recibe la misma entrada ante tres clasificaciones contradictorias. La recomendación de descartar esta fuente para evaluar un detector conversacional se mantiene como propuesta sin discutir para el equipo.

### 1.4. Alcance Operativo (Issue #151)

El alcance aprobado por el equipo comprende llamadas entrantes de números no agendados. En los casos analizados:

- **Caso 1:** El contexto describe una llamada de número desconocido atribuido al banco (dirección entrante compatible con el alcance).
- **Caso 2:** La evidencia externa alude a un contacto previo en red social y la brevedad se asemeja a mensajería de chat. El diálogo no demuestra el medio, la dirección ni si el número estaba agendado, por lo que su correspondencia con el alcance de #151 permanece incierta, sin descarte automático en esta fase exploratoria.

---

## 2. Caso 1: Grupo `b87dcd6c3c30c83372dd7a21` — Familia: `bank_contact`

### 2.1. Metadatos Primarios

- **Identificador de grupo:** `b87dcd6c3c30c83372dd7a21`
- **Partición (Split):** `test`
- **Familia técnica:** `bank_contact`
- **Turnos:** 6 turnos conversacionales
- **Contexto compartido de la situación:**  
Persona B recibió una llamada de un número desconocido atribuido al banco. El interlocutor alega una transacción Pix pendiente de 2.500 reales hacia CONTA_LUA y solicita confirmación verbal inmediata para el bloqueo. No hubo envío de enlaces ni solicitud de contraseñas, solo presión temporal y confirmación del destinatario.

### 2.2. Variantes de Evidencia Externa (Fuera del Diálogo)

Las tres variantes comparten el diálogo de §2.3. La etiqueta de la fuente depende de la información externa disponible para un auditor o sistema:


| Fila / Índice en Split | Identificador (Row ID)     | Etiqueta                | Confianza del Juez | Evidencia Externa Traducida                                                                                                                                                                                                                                                                                     | Motivo Registrado en Fuente                                                                                                                                         |
| ---------------------- | -------------------------- | ----------------------- | :------------------: | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Fila 1505              | `d9b35e80071c28a002c1dba6` | `scam_like`             | 0.90               | La verificación independiente en la aplicación oficial del banco revela que no hay ninguna transacción pendiente hacia CONTA\_LUA en la cuenta de Persona B, y el número de teléfono de la llamada no figura en el registro de canales oficiales del banco.                                                     | La verificación independiente contradice directamente la afirmación del interlocutor sobre una transacción Pix pendiente. El número no consta en canales oficiales. |
| Fila 694               | `504e0f2f8dbba0694ddfeac8` | `legitimate`            | 0.85               | La verificación independiente en la aplicación oficial del banco confirma la existencia de una transacción Pix pendiente de 2.500 reales hacia CONTA\_LUA, y el número de teléfono de la llamada corresponde a una central de atención autorizada registrada por el banco.                                      | La información disponible sustenta la transacción Pix pendiente y la legitimidad del número telefónico según registro oficial.                                      |
| Fila 1924              | `fe9745f31eb95b5cadcdd7ac` | `insufficient_evidence` | 0.75               | La verificación independiente en la aplicación oficial del banco indica que hay una transacción Pix pendiente, pero el número de teléfono de la llamada no puede ser cruzado con la lista de canales oficiales disponibles públicamente, permaneciendo el origen de la llamada sin confirmación de legitimidad. | Se confirma la transacción Pix pendiente, pero no es posible validar la legitimidad del contacto telefónico al no cruzarse con canales oficiales.                   |


### 2.3. Conversación Completa en Español

**Turno 1 (Hablante A):** Hola, le hablo del soporte de Banco Neon. Detectamos una transacción sospechosa en su cuenta. Para bloquear el Pix de 2.500 reales en curso, necesito validar su identidad ahora.  
**Turno 2 (Hablante B):** Qué extraño, yo no hice nada. Va demasiado rápido. Dígame la clave Pix que le paso la confirmación, pero solo si tengo la certeza de que es oficial.  
**Turno 3 (Hablante A):** No necesita enviar clave. El sistema ya tiene sus datos. Solo necesito que usted confirme si el beneficiario es CONTA_LUA. Si no lo es, el dinero va a la basura. ¿Confirma o cancelo?  
**Turno 4 (Hablante B):** Espere, ¿mi cuenta tiene dinero para CONTA_LUA? Yo tengo una factura pendiente allí, pero no envié Pix hoy. ¿Esto es urgente de verdad?  
**Turno 5 (Hablante A):** Sí, la transacción ya fue aprobada por el sistema. Si usted no confirma en 2 minutos, el bloqueo no entra y el dinero sale. Escriba SÍ para bloquear.  
**Turno 6 (Hablante B):** Voy a verificar mi aplicación antes. Si es real, vuelvo. Envíeme el código de seguridad de su interno para que lo verifique en la lista oficial.  

### 2.4. Notas Técnicas y Candidatos Observables

- **Dirección y alcance:** Compatible con llamada entrante de número desconocido según el contexto.
- **Estructura:** Breve (6 turnos), sin fase de rapport gradual; el aviso de transacción y la solicitud de validación se introducen en el primer turno.
- **Acciones y solicitudes en el diálogo:** En Turno 1 se plantea validar identidad; en Turno 3 se pide confirmar beneficiario bajo advertencia de pérdida de fondos; en Turno 5 se pide escribir SÍ con plazo de 2 minutos. Si estos enunciados constituyen o no un pedido de alto riesgo es una duda abierta de taxonomía (D07) que debe evaluar la persona revisora en la plantilla.
- **Traducción:** En Turno 4, la mención a factura traduce la referencia comercial usual a comprobante pendiente; en Turno 5, la indicación de escribir SÍ refleja un estilo híbrido entre telefonía y chat; en Turno 6, interno traduce la extensión telefónica corporativa.

### 2.5. Plantilla de Revisión Humana (Campos Vacíos para Luciano Grosso)

- Conservar / descartar / revisar: `[ si ] Conservar   [ ] Descartar   [ ] Revisar`
- Credibilidad: si
- Comienzo y final completos o recorte:completa
- Hablantes claros:si
- Pedido de alto riesgo observable (turno):1
- Cumplimiento observable (turno): no
- Equivalente local sin reescribirlo: nose
- Ambigüedades: no
- Diferencias respecto del corpus propio: no mucha 
- Decisión y motivo: es medio corto el caso pero esta bien igual, no me encanto pero es un 6/10
- ¿Es estafa leyendo la conversación entera? (sí / no / dudoso) — agregado el 2026-11-07, de #145:
- ¿En qué turno una persona atenta ya sospecharía? (o «ninguno») — agregado el 2026-11-07, de #145:

---

## 3. Caso 2: Grupo `e24a2dc7241413744ff93451` — Familia: `family_identity`

### 3.1. Metadatos Primarios

- **Identificador de grupo:** `e24a2dc7241413744ff93451`
- **Partición (Split):** `development`
- **Familia técnica:** `family_identity`
- **Turnos:** 5 turnos conversacionales
- **Contexto compartido de la situación:**  
Persona A solicita una transferencia urgente mediante Pix para saldar una deuda con un proveedor, alegando el bloqueo temporal de su aplicación bancaria. Persona B cuestiona el cambio de clave, pero Persona A insiste en que es la misma clave de siempre y demuestra impaciencia ante la verificación detallada. No hay mención a contraseñas ni tokens.

### 3.2. Variantes de Evidencia Externa (Fuera del Diálogo)

Las tres variantes comparten el diálogo de §3.3. La etiqueta de la fuente depende de la información externa disponible para un auditor o sistema:


| Fila / Índice en Split | Identificador (Row ID)     | Etiqueta                | Confianza del Juez | Evidencia Externa Traducida                                                                                                                                                                                                                                                            | Motivo Registrado en Fuente                                                                                        |
| ---------------------- | -------------------------- | ----------------------- | :------------------: | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| Fila 507               | `22bda30be723ecfb8ec8250f` | `scam_like`             | 0.95               | La verificación del destinatario en la operación revela que la clave Pix informada corresponde a CONTA\_FANTASMA, vinculada a un CPF diferente del CPF real de Persona A presente en el registro antiguo de la red social donde conversan.                                             | La clave Pix informada corresponde a una cuenta no vinculada al titular legítimo, indicando desvío de pago.        |
| Fila 28                | `2e638c0b85ffb6a796bad809` | `legitimate`            | 0.90               | La verificación del destinatario en la operación confirma que la clave Pix informada corresponde exactamente a CONTA\_PRINCIPAL, vinculada al CPF de Persona A, quien posee historial de transacciones con el mismo proveedor mencionado.                                              | La clave Pix corresponde a la cuenta principal de Persona A y existe historial con el proveedor.                   |
| Fila 9                 | `312021bce5a2f5b046dff3e9` | `insufficient_evidence` | 0.60               | La verificación del destinatario en la operación indica que la clave Pix informada pertenece a una cuenta activa, pero el nombre del titular mostrado en el sistema interno y el CPF asociado no se visualizan con claridad para una comparación inmediata con el perfil de Persona A. | No hay confirmación clara de titularidad; la falta de datos concluyentes impide clasificar como legítima o estafa. |


### 3.3. Conversación Completa en Español

**Turno 1 (Hablante A):** ¡Hola! ¿Todo bien? Estoy necesitando un favor urgente. Necesito transferir un dinero para saldar una deuda aquí afuera y no puedo acceder a mi aplicación ahora.  
**Turno 2 (Hablante B):** Claro, envía la clave Pix y el monto. Pero dime, ¿cuál es la urgencia? Sé que no sueles pedir dinero así de repente.  
**Turno 3 (Hablante A):** Es que el sistema del banco se cayó y tengo que pagarle al proveedor en 10 minutos o si no pierdo el contrato. Es urgente de verdad, amigo. La clave es la misma de siempre.  
**Turno 4 (Hablante B):** Está bien, pero antes de que lo envíe, ¿me puedes confirmar si es para la cuenta de la empresa o para tu CPF personal? Me parece que cambió la clave en el último contacto.  
**Turno 5 (Hablante A):** No cambia nada, es mi cuenta principal misma. [pasaje de traducción incierta] y hazlo ya, por favor. No tengo tiempo para burocracia ahora.  

### 3.4. Nota sobre el Pasaje de Traducción Incierta

- En el Turno 5, la expresión señalada como `[pasaje de traducción incierta]` corresponde a una locución verbal de la fuente que la lectura asistida por IA no pudo resolver en un sentido contextual unívoco en español.
- No se cuenta con validación humana bilingüe para este pasaje. Siguiendo las directivas del proyecto, se marca la incertidumbre en el diálogo sin conjeturar intenciones de redacción ni reescribir el texto.

### 3.5. Notas Técnicas y Candidatos Observables

- **Dirección y medio:** La mención externa a redes sociales y la estructura breve sugieren un intercambio similar a mensajería de texto. El diálogo no acredita si se trató de una llamada de voz ni el estado del número en la agenda; su inclusión en el alcance de #151 permanece incierta.
- **Acciones y solicitudes en el diálogo:** En Turno 1 se formula un pedido urgente de transferencia; en Turno 3 se introduce presión temporal de 10 minutos; en Turno 5 se insiste en realizar el envío evitando demoras. La delimitación de si constituye un evento crítico formal corresponde a la revisión en plantilla.
- **Cumplimiento:** No se observa resolución ni envío de fondos en el diálogo disponible, que concluye en el Turno 5.

### 3.6. Plantilla de Revisión Humana (Campos Vacíos para Luciano Grosso)

- Conservar / descartar / revisar: `[ ] Conservar   [ si] Descartar   [ ] Revisar`
- Credibilidad: si
- Comienzo y final completos o recorte: completa
- Hablantes claros: si
- Pedido de alto riesgo observable (turno):1 
- Cumplimiento observable (turno):no cumple
- Equivalente local sin reescribirlo: 
- Ambigüedades: 
- Diferencias respecto del corpus propio: 
- Decisión y motivo: muy corta la conversacion 
- ¿Es estafa leyendo la conversación entera? (sí / no / dudoso) — agregado el 2026-11-07, de #145:
- ¿En qué turno una persona atenta ya sospecharía? (o «ninguno») — agregado el 2026-11-07, de #145:

---

## 4. Notas Técnicas del Ejercicio Exploratorio

1. **Invariancia conversacional observada:** En los dos grupos analizados, el contenido de la conversación es idéntico entre las tres clases y la etiqueta depende de verificaciones externas fuera de banda.
2. **Propuesta técnica sin discutir (D08):** La recomendación de descartar esta fuente para evaluar un detector que procesa únicamente transcripciones de llamadas telefónicas permanece como propuesta abierta para el equipo, sin constituir una decisión cerrada ni conclusiones definitivas de informe.
3. **Ceguera de evaluación:** Las dos conversaciones analizadas en este documento quedan excluidas del conjunto de evaluación futuro para evitar contaminación por exposición previa de estos ejemplos particulares.

---

*Fin del informe exploratorio de muestras en portugués — Issue #144 (2026-11-06).*