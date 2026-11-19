# Política de producto: cuándo sirve un aviso (#143)

> **Estado: propuesta sin discutir.** Escrita el 2026-11-10, a pedido de Mateo. Las secciones 1 y 2 y la posición sobre
> el DNI y los códigos son de **antes de abrir corridas, análisis y casos**; las secciones 3 y 4 se cerraron después,
> con las fuentes nuevas, y lo dicen. Sale de principios y de fuentes públicas ([`FUENTES.md` de la etapa 3](../2026-11-09_pedido-critico-etapa-3/FUENTES.md),
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

## 3. El DNI

> **Orden en que se escribió.** La posición quedó anotada antes de leer los casos y antes del relevamiento nuevo
> (commit `c638eda`): el número solo no dispara ni tranquiliza, y se juzga por el pretexto. Las fuentes nuevas llegaron
> después de leer los casos y de ver los resultados. No cambiaron la posición; agregaron el **número de trámite** y
> mostraron qué parte de ella es inferencia.

### ¿Hay legítimas entrantes que piden el DNI?

**Sí, pero las fuentes no dicen cuántas ni cuáles.** Lo que está documentado:

- **El DNI se pide cuando llama la persona:** Banco Provincia (S30), Galicia (P10), el 147 del GCBA para turnos (P35) y
  Macro (P37).
- **Hay llamadas legítimas de números no agendados:** la venta telefónica es legal (Ley 26.951, P19) y la cobranza por
  estudios externos existe (Santander, P09; AAIP, P31). Ninguna fuente dice qué datos piden.
- **El alta de una línea, que puede ser remota, pide el DNI, el sexo y el número de trámite** (ENACOM, Res. 263/2023,
  art. 7, P16), y Claro vende la portabilidad por teléfono con el DNI como requisito (P14).
- **El DNI se muestra al recibir un envío, en persona** (OCA, P36). Nada dice que el correo lo pida por teléfono.

**No se encontró ninguna fuente** que diga que al confirmar un turno, cobrar una deuda, hacer una encuesta o
seleccionar personal se pide el DNI por teléfono, ni una medición de qué tan común es. Que esas llamadas lo pidan es
experiencia común, no un dato relevado: queda como **límite declarado**.

**Del otro lado,** ANSES, PAMI, ARCA, Santander, Naranja X, la UFECI y Con Vos en la Web dicen que no llaman para pedir
«datos personales» o «información personal» (P02–P07, P11, P30, P33). **Ninguna nombra el número de DNI:** nombran
credenciales y, a lo sumo, la foto del DNI (P07, S07, S16, S24). La única voz oficial que nombra el número sigue siendo
el MPF de Río Negro (S25).

### ¿Qué puede hacer un estafador con el número solo?

**Ninguna fuente oficial lo responde, ni dice que sea inocuo.** Lo que sigue es una inferencia desde dos hechos:

- **El número circula:** la Ley 25.326 permite listados con nombre, DNI, fecha de nacimiento y domicilio sin
  consentimiento (art. 5, P18); la Central de Deudores del BCRA se consulta con el CUIL (P26); y RENAPER admitió en 2021
  que un servicio devolvía todos los datos del DNI con el número y el sexo (P20).
- **Cada trámite que mueve plata o una cuenta pide algo más:** el número de trámite (alta de una línea, Clave de la
  Seguridad Social; P16, P24), biometría con prueba de vida (cambio de SIM, clave fiscal, Mi Argentina; P16, P05, P22),
  una foto del DNI con una selfie (S07) o identificación positiva (créditos preaprobados, BCRA A 7319, P25).

De ahí: **con el número solo no se saca plata ni se toma una cuenta, y el estafador muchas veces ya lo tiene.** El
segundo dato que más puertas abre es el **número de trámite**. El uso del DNI para hacer creíble la llamada siguiente
aparece solo en opiniones de especialistas en la prensa (P39).

### Qué conviene: juzgarlo según el pretexto

| opción | qué pasa | veredicto |
|---|---|---|
| **Excluirlo** («pedir el DNI no vuelve estafa una llamada») | Trata igual al turno médico y al premio que nadie esperaba | Es lo que hay hoy. Sirve como freno, pero no dice cuándo sí pesa |
| **Endurecerlo** («el DNI no se le da a quien llamó») | Avisa en las ventas, los reclamos y los turnos que lo piden. El aviso no evita ninguna pérdida, y ninguna lista oficial de «nunca te pedimos» nombra el número | No |
| **Juzgarlo según el pretexto** | No dispara solo. Pesa si el motivo es un premio, un beneficio, una deuda o un bloqueo que la persona no esperaba, o si viene con el número de trámite, una foto del documento u otro pedido de la lista | **Sí** |

Tres reglas quedan de esto:

1. **El número de DNI solo no dispara el aviso.**
2. **El número de trámite y la foto del documento sí:** van con las credenciales.
3. **Que OTRA ya sepa el nombre, el DNI o la dirección no prueba quién es.** Es una inferencia de que el dato circula
   (P18, P20), no una frase de una fuente.

**La duda de Mateo, «¿dejamos pasar estafas reales que piden el DNI para que los números se vean mejor?»,** tiene dos
partes. Por las fuentes, una llamada que pide solo el número no produce la pérdida en esa llamada: la produce el paso
siguiente, y ese paso sí está en la lista. Por el corpus, la pregunta se responde en [`HALLAZGOS.md`](HALLAZGOS.md),
con una advertencia: en desarrollo hay 6 estafas cuyo pedido es de datos personales, y el sesgo R29 sigue (la sigla DNI
aparece en el 37 % de las legítimas y en el 7 % de las estafas).

## 4. Los códigos y las claves

**No hay un caso legítimo documentado en que quien llamó pida que le dicten un código que acaba de llegar.**

- **«Nadie te pide el código», sin excepciones:** Santander (P07), PAMI (P02), Naranja X (P11), Mercado Libre (P12, aun
  cuando la llamada la pidió el usuario), la UFECI (P29), Con Vos en la Web (P33) y WhatsApp (S09), además de las ya
  relevadas (S01, S03–S05, S26, S37).
- **La excepción «salvo que hayas llamado vos» no aparece para los códigos.** Aparece para los datos de la tarjeta
  (Naranja X, P11) y para los datos personales (S11).
- **Los códigos legítimos se ingresan o se muestran, no se dictan por teléfono:** se cargan en la web o en la app (P14,
  P37), se aprueban en la app del banco (Santander, P08) o se le dicen al repartidor en la puerta (Mercado Libre, P13).
- **El único candidato es el PIN de portabilidad.** La norma hace que le llegue por SMS al titular a pedido de la
  operadora que lo recibe (Res. 203/2018, P15), y no dice por qué canal se lo pasa. La única evidencia de que se dicta
  en una venta telefónica es un blog con comentarios (P40, no oficial), donde el mismo pedido aparece en trámites reales
  y en un fraude.

**Política:** un código que le llegó a PROTEGIDA, una clave o un PIN **no se le dictan a quien llamó**, se presente como
se presente y lo pida con las palabras que lo pida. Si una venta de portabilidad real lo pide por teléfono, el aviso
igual es un buen consejo: el PIN se carga en la web o en un local, y con una línea ajena se reciben los códigos de todo
lo demás (UFECI, P28).

Lo que **no** es un pedido:
- que OTRA **dé** un número: de reclamo, de turno, de seguimiento, de visita;
- que OTRA **diga que no se comparte**, o que PROTEGIDA empiece a dictarlo y OTRA la frene.

## 5. Lo que esta política no resuelve

- **No hay medición de frecuencia** de ningún tipo de llamada. La política ordena por lo que se pierde, no por lo
  común.
- **Las cobranzas** son llamadas legítimas, insistentes y de números no agendados (P09, P31), piden plata y no están
  en el corpus. Con esta política, un pago pedido por teléfono merece el aviso; cuánto molestaría no se puede medir
  acá.
- **«Tolerable» es una categoría de evaluación, no de producto.** La persona recibe el mismo aviso. Si el texto del
  aviso debería ser distinto cuando no hay pedido («así empiezan muchas estafas; no dictes códigos») queda para
  después de congelar.
