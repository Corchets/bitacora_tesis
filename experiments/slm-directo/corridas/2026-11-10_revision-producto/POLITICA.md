# Política de producto: cuándo sirve un aviso (#143)

> **Estado: propuesta sin discutir.** Escrita el 2026-11-10, a pedido de Mateo, **antes de abrir corridas, análisis y
> casos**. Sale de principios y de fuentes públicas ([`FUENTES.md` de la etapa 3](../2026-11-09_pedido-critico-etapa-3/FUENTES.md),
> S01–S37, y las nuevas de [`FUENTES-PRODUCTO.md`](FUENTES-PRODUCTO.md), P01…). No cierra
> [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) ni
> [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

## 1. Qué es el aviso para la persona

El detector acompaña a PROTEGIDA en una llamada entrante de un número no agendado
([ADR 0003](../../../../docs/ingenieria/adr/0003-detector-solo-en-entrantes-de-no-agendados.md)). El aviso la interrumpe
en medio de la llamada y le dice, en el fondo, una sola cosa: **frená y verificá por otro canal**.

- **Sirve** cuando frenar cuesta poco y seguir puede costar mucho: plata, una cuenta o el control del teléfono, sin
  vuelta atrás. Tiene que llegar antes de que PROTEGIDA cumpla.
- **Molesta** cuando frenar no evita nada: la llamada no le pide nada que se pueda perder. Además gasta la confianza:
  quien recibe avisos en el turno médico y en la entrega del correo deja de mirarlos, y el aviso de la estafa llega
  tarde a una persona que ya no lo lee.

De ahí salen dos preguntas para cualquier llamada. Ninguna depende de quién dice ser OTRA, porque dentro de la llamada
eso no se puede comprobar: el estafador se presenta como alguien confiable (el banco, un organismo) o inocente (un
taller, un curso, un familiar).

1. **¿Qué le pide OTRA a PROTEGIDA que haga o que diga?**
2. **Si lo hace y OTRA mentía sobre quién es, ¿qué pierde, y se puede deshacer?**

## 2. La intención de la llamada

| Intención de OTRA | Ejemplos | Qué pierde PROTEGIDA si OTRA mentía | ¿Aviso? |
|---|---|---|---|
| **Informar o coordinar** | El correo avisa que pasa; confirmar o mover un turno; un recordatorio; la escuela; el resultado de una entrevista. A lo sumo «¿habla Juan Pérez?» | Nada | **Nunca** |
| **Ofrecer o vender** | Un plan, un seguro, un auto, una tarjeta, mientras ofrece, informa o agenda una visita | Nada: decir que no, o que sí, no mueve plata | **Nunca** |
| **Preguntar una opinión** | Encuestas, satisfacción con un servicio | Nada | **Nunca** |
| **Seguir una gestión que PROTEGIDA reconoce como suya** | El soporte por un reclamo que ella hizo; la concesionaria por una consulta que dejó | Nada, mientras los pedidos sean operativos (reiniciar el módem, un horario de visita) | **No** |
| **Advertir** | El banco por un consumo que no reconoce, sin pedirle nada: «entre usted a la app», «le mandamos una tarjeta nueva» | Nada | **No hace falta.** Si avisa, coincide con el consejo oficial de cortar y llamar al número oficial (S12, S14, S16, S18, S21, S26): es tolerable |
| **Tomar datos que identifican** | Nombre, DNI, fecha de nacimiento, domicilio, mail, obra social | Depende del pretexto: ver [§3](#3-el-dni) | Según el pretexto |
| **Obtener una credencial o un acto sin vuelta atrás** | Dictar un código que llegó, una clave o un PIN; los datos de la tarjeta; una foto del DNI o de la cara; transferir o pagar; instalar un programa o compartir la pantalla; operar en el cajero o en la app con instrucciones | La cuenta o la plata | **Siempre**, sea quien sea OTRA y dé el motivo que dé |

Dos consecuencias:

- **Una llamada legítima también puede merecer el aviso.** Si una empresa real llama y cobra por teléfono con los datos
  de la tarjeta, o un soporte real pide acceso remoto, el aviso dice lo mismo que las fuentes oficiales: eso no se hace
  con quien llamó. Hacerle caso cuesta unos minutos (cortar y llamar al número oficial). En la evaluación esas
  llamadas no deberían contar como falsas alarmas.
- **Lo que OTRA promete no cuenta; cuenta lo que pide.** «Nunca le vamos a pedir la clave» lo dice el banco y lo dice
  el estafador un minuto antes de pedirla. Y que OTRA nombre un código o una clave para decir «no la comparta» no es
  un pedido.

## 3. El DNI y los códigos: posición previa a las fuentes nuevas

> Anotada antes de leer los casos y antes de recibir el relevamiento nuevo, para que quede el orden. Las secciones
> definitivas la reemplazan y dicen qué cambió.

- **DNI:** el número solo no dispara el aviso y tampoco tranquiliza. Se juzga por el pretexto: si el motivo de la
  llamada explica para qué hace falta, y si con ese dato solo se pierde algo. Sube cuando viene con otra cosa: el
  número de trámite, una foto, una seguidilla de datos (fecha de nacimiento, CBU, mail) o un pretexto de premio,
  deuda o bloqueo. Que OTRA ya sepa el nombre o el DNI no prueba quién es.
- **Códigos:** un código que le llegó a PROTEGIDA no se le dicta a quien llamó, con ningún pretexto. Que OTRA dé un
  código (de reclamo, de turno, de seguimiento) no es un pedido.
