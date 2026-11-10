# #143, etapa 3: diagnóstico fuera de la regla (escrito después de ver los resultados)

## 1. El riesgo escrito y el valor que dispara el primer aviso

Dentro del alcance, todas las líneas. «0,3 exacto»: el primer aviso de la llamada sale de un riesgo de 0,3, el escalón de la regla.

| serie | llamadas | valores del riesgo (≥ 1 % de las líneas) | avisos con 0,3 exacto | avisos con > 0,3 | solo por pedido_critico | avisos |
|---|---|---|---|---|---|---|
| base: C de la etapa 2, cortado tras el riesgo | estafas | 0.05: 1 %, 0.1: 17 %, 0.2: 37 %, 0.3: 33 %, 0.5: 1 %, 0.6: 7 % | 31 | 5 | 0 | 36 |
| base: C de la etapa 2, cortado tras el riesgo | legítimas | 0.05: 1 %, 0.1: 55 %, 0.2: 30 %, 0.3: 8 %, 0.6: 2 %, 0.7: 2 % | 25 | 2 | 0 | 27 |
| C sin alerta | estafas | 0.05: 1 %, 0.1: 16 %, 0.2: 36 %, 0.3: 36 %, 0.4: 1 %, 0.5: 2 %, 0.6: 5 % | 37 | 2 | 0 | 39 |
| C sin alerta | legítimas | 0: 1 %, 0.05: 1 %, 0.1: 52 %, 0.2: 33 %, 0.3: 9 %, 0.6: 1 %, 0.7: 1 % | 31 | 1 | 0 | 32 |
| C con campo | estafas | 0.1: 26 %, 0.2: 43 %, 0.3: 22 %, 0.6: 1 %, 0.7: 3 %, 0.8: 3 % | 29 | 8 | 0 | 37 |
| C con campo | legítimas | 0.05: 1 %, 0.1: 63 %, 0.2: 26 %, 0.3: 9 % | 16 | 2 | 0 | 18 |

## 2. Pares discordantes de la regla, con McNemar exacto

| corrida | cifra | solo la base | solo C con campo | p (McNemar exacto) |
|---|---|---|---|---|
| corrida | estafas avisadas | 2 | 3 | 1.000 |
| corrida | avisos a tiempo | 5 | 1 | 0.219 |
| corrida | FA | 10 | 1 | 0.012 |
| repetición | estafas avisadas | 3 | 3 | 1.000 |
| repetición | avisos a tiempo | 5 | 2 | 0.453 |
| repetición | FA | 9 | 0 | 0.004 |

## 3. Los avisos a tiempo que pierde C con campo

Riesgo en la línea del pedido de la referencia (y la línea en que cada versión avisa). «pc»: primera línea con `pedido_critico` en true.

| caso | línea del pedido | texto de esa línea | base | C con campo | pc |
|---|---|---|---|---|---|
| CV2-D-V-FAMILIAR-001 | 15 | No hace falta efectivo haceme una transferencia y te lo devuelvo cuando cobre el viernes | 0.3 (aviso L15) | 0.2 (aviso L17) | L19 |
| CV2-D-V-ORGANISMO_PREVISIONAL-003 | 11 | Del titular de la consulta. Para que el sistema abra el detalle, me faltan los dígitos de… | 0.2 (aviso L1) | 0.2 (aviso L13) | — |
| CV2-D-V-PREMIO-002 | 13 | Dos mil setecientos se abona por transferencia a la cuenta de producción | 0.3 (aviso L13) | 0.2 (aviso —) | — |
| CV2-D-V-PREMIO-004 | 14 | El nombre, la fecha de vencimiento y los tres números de seguridad que están atrás. | 0.2 (aviso L12) | 0.2 (aviso L15) | L15 |
| CV2-D-V-WHATSAPP-001 | 9 | Cuando te llegue el código decime los seis números para asociar tu contacto con la lista | 0.3 (aviso L9) | 0.2 (aviso L10) | — |

## 4. La alerta fuerte en las legítimas

| caso | línea | texto | evidencia | motivo |
|---|---|---|---|---|
| ENT-L-BANCO-002 | L12 OTRA | Cortá y llamá vos al número que está en el dorso de tu tarjeta. Pedí por seguridad y dales el número de caso … | Cortá y llamá vos al número que está en el dorso de tu tarjeta. Pedí por seguri… | Te están pidiendo que cortes la llamada y llames a un número que te dictan, lo cual es una táctica común para… |
| ENT-L-BANCO-006 | L7 PROTEGIDA | Sí, cambié el celu ayer. Ahora que lo decís, me llegó un mensaje con un código, es el cuatro siete... | me llegó un mensaje con un código, es el cuatro siete... | Te están pidiendo un código que te llegó por mensaje, lo cual es una táctica común de estafa. |
| ENT-L-SOPORTE-005 | L13 OTRA | Sí. Te va a mostrar un número de conexión de nueve cifras. ¿Me lo leés? | Sí. Te va a mostrar un número de conexión de nueve cifras. ¿Me lo leés? | Te están pidiendo que leas un número de conexión, lo cual es una táctica común para obtener acceso remoto a t… |
| ENT-L-VENTAS-009 | L20 PROTEGIDA | ¿Y si después me arrepiento? | Quinientos mil pesos. Podés venir y pagarla en caja, o transferirla a la cuenta… | La solicitud de un pago mediante transferencia a una cuenta de empresa, especialmente cuando se menciona la p… |
| LEG2-BA-02 | L7 PROTEGIDA | Siete, tres, cuatro, cuatro, cero. | Hagamos así: cortá y llamá vos al número del dorso de tu tarjeta. Pedí por segu… | La llamada te pide que cortes y llames a un número, lo cual es una táctica común para robar tus datos o acced… |

## 5. Los motivos de C con campo, dentro del alcance

«Pedido crítico de la referencia»: la primera línea con código, clave, plata, acceso remoto o acción de seguridad (sin datos personales); «pedido»: el primero de cualquier tipo.

| caso | clase | línea | pedido | pedido crítico | evidencia | motivo |
|---|---|---|---|---|---|---|
| CV2-D-V-BANCO-001 | vishing | L32 | 32 | 32 | Ahora sí, decime el código de seis cifras del mensaje y lo asocio al reclamo. | Te están pidiendo un código de seis cifras que te llegó por mensaje para asociarlo a un reclamo, lo cual es una táctica… |
| CV2-D-V-BANCO-002 | vishing | L18 | 18 | 18 | Autorizá ese equipo nuevo para que desde acá podamos desvincular el anterior. | La llamada está llevando a PROTEGIDA a autorizar una acción sobre un equipo, lo cual es un punto de riesgo en estafas. |
| CV2-D-V-BANCO-004 | vishing | L10 | 16 | 16 | Te mando un código para confirmar que sos titular. | Te están pidiendo que confirmes algo enviándote un código, lo cual es una táctica común para robar tus datos. |
| CV2-D-V-BANCO-005 | vishing | L11 | 19 | 19 | Tocá editar y elegí validar acceso Te va a pedir tu clave de seis dígitos | Te están pidiendo que ingreses tu clave de seis dígitos, lo cual es una táctica común para robar tus credenciales. |
| CV2-D-V-BANCO-006 | vishing | L14 | 14 | 14 | Para que no se venza, pasame esos seis números y lo adjunto al movimiento. | Te están pidiendo que les des seis números para adjuntarlos a un movimiento, lo cual es una táctica común para obtener … |
| CV2-D-V-BANCO-007 | vishing | L17 | 17 | 17 | Entonces elegí ese número terminado en 804 y confirmá que reciba las verificaci… | Te están pidiendo que confirmes un número específico para recibir verificaciones de acceso, lo cual es una táctica comú… |
| CV2-D-V-BANCO-009 | vishing | L13 | 13 | 13 | Completalos con los números de tu clave de cajero en el orden en que los usás | Te están pidiendo que completes casilleros con claves de cajero, lo cual es una táctica común para robar tus credencial… |
| CV2-D-V-BANCO-010 | vishing | L13 | 13 | 13 | Para esta gestión usás esa misma serie como comprobante de voluntad. | Te están pidiendo que uses un código que te llega por mensaje para confirmar una operación, lo cual es una táctica comú… |
| CV2-D-V-FAMILIAR-001 | vishing | L19 | 15 | 15 | No hace falta efectivo haceme una transferencia y te lo devuelvo cuando cobre e… | La solicitud de realizar una transferencia bancaria para resolver un problema de terceros es una táctica común en estaf… |
| CV2-D-V-FAMILIAR-002 | vishing | L16 | 16 | 16 | No, está trabajando sin señal. Transferile vos los doscientos diez mil a la cue… | Te están pidiendo que transfieras dinero a una cuenta, lo cual es una táctica común en estafas. |
| CV2-D-V-ORGANISMO_PREVISIONAL-001 | vishing | L12 | 12 | — | Le pido el DNI completo y la fecha de nacimiento de su mamá para cargarla, y un… | Te están pidiendo datos sensibles como DNI y fotos de documentos, lo cual es una táctica común de estafa. |
| CV2-D-V-PREMIO-001 | vishing | L10 | 10 | — | El DNI completo y una foto del frente para cargarlo en el acta. | Te están pidiendo datos personales sensibles como tu DNI y una foto, lo cual es una táctica común para robar tu identid… |
| CV2-D-V-PREMIO-004 | vishing | L15 | 14 | 14 | Le mandamos un aviso de operación y tiene que confirmar los datos de la tarjeta… | Te están pidiendo los datos completos de tu tarjeta, lo cual es una señal de alerta en este tipo de llamadas. |
| CV2-D-V-SOPORTE-002 | vishing | L13 | 13 | 13 | Instalá Visor Roca desde el aviso que te mandé y compartime el código de acceso. | Te están pidiendo instalar un programa y compartir un código de acceso, lo cual es una táctica común para obtener contr… |
| CV2-D-V-WHATSAPP-002 | vishing | L10 | 10 | 10 | Te va a llegar un código de seis números. Leémelo así cierro el diagnóstico. | Te están pidiendo que leas un código que te llega, lo cual es una táctica común para robar contraseñas o acceder a cuen… |
| CV2-D-V-WHATSAPP-003 | vishing | L13 | 12 | 12 | Leeme los seis dígitos y te incorporo al grupo | Te están pidiendo que leas un código de invitación para que te incorporen a un grupo de WhatsApp, lo cual es una táctic… |
| CV2-D-V-WHATSAPP-005 | vishing | L13 | 14 | 14 | Te mandé una solicitud. Mirá el mensaje de WhatsApp que acaba de entrar. | Te están pidiendo un código de seis cifras que te enviaron por WhatsApp, lo cual es una táctica común para robar contra… |
| ENT-L-BANCO-002 | legitima | L12 | — | — | Cortá y llamá vos al número que está en el dorso de tu tarjeta. Pedí por seguri… | Te están pidiendo que cortes la llamada y llames a un número que te dictan, lo cual es una táctica común para robar tus… |
| ENT-L-BANCO-006 | legitima | L7 | — | — | me llegó un mensaje con un código, es el cuatro siete... | Te están pidiendo un código que te llegó por mensaje, lo cual es una táctica común de estafa. |
| ENT-L-SOPORTE-005 | legitima | L13 | — | 13 | Sí. Te va a mostrar un número de conexión de nueve cifras. ¿Me lo leés? | Te están pidiendo que leas un número de conexión, lo cual es una táctica común para obtener acceso remoto a tu disposit… |
| ENT-L-VENTAS-009 | legitima | L20 | — | 17 | Quinientos mil pesos. Podés venir y pagarla en caja, o transferirla a la cuenta… | La solicitud de un pago mediante transferencia a una cuenta de empresa, especialmente cuando se menciona la posibilidad… |
| LEG2-BA-02 | legitima | L7 | — | — | Hagamos así: cortá y llamá vos al número del dorso de tu tarjeta. Pedí por segu… | La llamada te pide que cortes y llames a un número, lo cual es una táctica común para robar tus datos o acceder a tu cu… |

