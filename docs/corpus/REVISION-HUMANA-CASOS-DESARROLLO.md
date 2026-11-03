# Revisión humana de los casos de desarrollo

Los 150 casos de desarrollo, para leerlos y corregirlos. Todos son ficticios y ninguno tiene todavía revisión humana. La reserva (`CV2-T-*`) no está acá.

Generado con `experiments/slm-directo/hoja_revision_casos.py`: los diálogos y las marcas viven en [`casos/texto`](../../experiments/slm-directo/casos/texto) y [`casos/referencia`](../../experiments/slm-directo/casos/referencia). Volver a generarlo pisa lo que se haya marcado acá.

## Antes de leer

- **Esto no cierra [D07](../gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico).** Sirve para corregir casos. D07 pide además que los cuatro integrantes anoten por separado una muestra común, sin ver respuestas ajenas, y acá las marcas ya están a la vista.
- **`revision_humana` sigue en `false`** hasta pasar lo revisado a cada referencia.
- **Quien vaya a atender una llamada grabada no debería leer ese caso antes:** el [método](METODO-CREACION-CORPUS.md) pide que no conozca la clase.

## Qué significan las marcas

- `T_R`: línea donde empieza el pedido crítico. `T_C`: línea donde la persona cumple. Ver el [manual](MANUAL-ANOTACION.md).
- Las etiquetas al final de una línea son la evidencia que la referencia eligió.

## Por dónde empezar

Estos 32 son los de la matriz #101 o los [propuestos para grabar](../../experiments/slm-directo/casos/GRABACIONES-ASR.md):

[CV2-D-L-BANCO-001](#cv2-d-l-banco-001), [CV2-D-L-BANCO-002](#cv2-d-l-banco-002), [CV2-D-L-BANCO-007](#cv2-d-l-banco-007), [CV2-D-L-DELIVERY-001](#cv2-d-l-delivery-001), [CV2-D-L-DELIVERY-004](#cv2-d-l-delivery-004), [CV2-D-L-ESCUELA-001](#cv2-d-l-escuela-001), [CV2-D-L-FAMILIAR-001](#cv2-d-l-familiar-001), [CV2-D-L-FAMILIAR-002](#cv2-d-l-familiar-002), [CV2-D-L-FAMILIAR-005](#cv2-d-l-familiar-005), [CV2-D-L-MEDICO-001](#cv2-d-l-medico-001), [CV2-D-L-ORGANISMO_PREVISIONAL-001](#cv2-d-l-organismo_previsional-001), [CV2-D-L-PREMIO-001](#cv2-d-l-premio-001), [CV2-D-L-SOPORTE-001](#cv2-d-l-soporte-001), [CV2-D-L-SOPORTE-002](#cv2-d-l-soporte-002), [CV2-D-L-TRABAJO-003](#cv2-d-l-trabajo-003), [CV2-D-L-WHATSAPP-001](#cv2-d-l-whatsapp-001), [CV2-D-L-WHATSAPP-004](#cv2-d-l-whatsapp-004), [CV2-D-V-BANCO-001](#cv2-d-v-banco-001), [CV2-D-V-BANCO-002](#cv2-d-v-banco-002), [CV2-D-V-BANCO-007](#cv2-d-v-banco-007), [CV2-D-V-BANCO-008](#cv2-d-v-banco-008), [CV2-D-V-FAMILIAR-002](#cv2-d-v-familiar-002), [CV2-D-V-ORGANISMO_PREVISIONAL-001](#cv2-d-v-organismo_previsional-001), [CV2-D-V-PREMIO-003](#cv2-d-v-premio-003), [CV2-D-V-PREMIO-004](#cv2-d-v-premio-004), [CV2-D-V-SOPORTE-001](#cv2-d-v-soporte-001), [CV2-D-V-SOPORTE-002](#cv2-d-v-soporte-002), [CV2-D-V-SOPORTE-003](#cv2-d-v-soporte-003), [CV2-D-V-SOPORTE-004](#cv2-d-v-soporte-004), [CV2-D-V-WHATSAPP-002](#cv2-d-v-whatsapp-002), [CV2-D-V-WHATSAPP-006](#cv2-d-v-whatsapp-006), [TR-13-turno-medico-pide-dni](#tr-13-turno-medico-pide-dni)

## Contenido

| Sección | Casos |
|---|---:|
| Estafas del corpus v2 | 46 |
| Legítimas del corpus v2 | 51 |
| Casos trampa | 13 |
| Piloto escrito: estafas | 7 |
| Piloto escrito: legítimas | 7 |
| Laboratorio | 26 |

## Estafas del corpus v2

### CV2-D-V-BANCO-001

vishing · banco · directo · **en la matriz #101** · **propuesto para grabar** · 38 líneas

**Situación:** Una discusión extensa sobre dos períodos de abono de cochera y un recibo en efectivo precede a la conversión del reclamo en un pedido de OTP de acceso a la cuenta.

` 1` **A:** Sí, recién puedo atender. ¿Por qué me habían dejado un mensaje?  
` 2` **B:** Soy del sector de medios de pago del banco, por el reclamo de un cargo. ← `AUTHORITY_CLAIM`  
` 3` **A:** ¿El del abono de la cochera? Porque eso ya lo hablé con el encargado.  
` 4` **B:** Me aparece una gestión vinculada con un cobro mensual que se repitió.  
` 5` **A:** El encargado dice que uno corresponde a septiembre y el otro a octubre.  
` 6` **B:** Puede ser. Si son dos períodos distintos no corresponde hacer una devolución.  
` 7` **A:** Eso quería saber. En el resumen figuran los dos con fecha de octubre.  
` 8` **B:** La fecha que ves puede ser la de presentación, distinta del período del abono.  
` 9` **A:** Claro, porque en septiembre se les había roto la terminal.  
`10` **B:** ¿Llegaron a cobrarte ese mes por otro medio?  
`11` **A:** Lo pagué en efectivo. Me dejaron un recibo de papel en el auto.  
`12` **B:** Entonces podría haber una duplicación de ese primer período.  
`13` **A:** El recibo lo tengo en casa, ahora estoy saliendo de trabajar.  
`14` **B:** Te explico las alternativas y después ves si querés mantener el reclamo.  
`15` **A:** Bueno, decime. No quiero que le retengan plata al encargado si no corresponde.  
`16` **B:** Si el comercio reconoce el cobro, presenta una anulación y queda compensado en el cierre.  
`17` **A:** Me dijo que podía tardar hasta el próximo resumen.  
`18` **B:** Es una posibilidad. También puede quedar un saldo a favor para el período siguiente.  
`19` **A:** Pero si yo doy de baja la cochera no me sirve un saldo a favor.  
`20` **B:** En ese caso la discusión sería sobre la devolución del importe.  
`21` **A:** Ya le avisé que dejo el lugar en noviembre porque me mudo más cerca del trabajo.  
`22` **B:** Entiendo. No hace falta que resuelvas ahora cómo seguís con el abono.  
`23` **A:** ¿El reclamo que hice ayer sigue abierto entonces?  
`24` **B:** Sí, mientras el comercio no presente la respuesta queda en revisión.  
`25` **A:** Perfecto. Cuando llegue busco el recibo y hablo con él otra vez.  
`26` **B:** Antes de cerrar la consulta me apareció una verificación pendiente del teléfono.  
`27` **A:** ¿Eso es por la cochera también?  
`28` **B:** Se adjunta al expediente, para que no se separen las dos gestiones.  
`29` **A:** Acaba de entrar un mensaje. Dice que alguien quiere acceder a mi cuenta.  
`30` **B:** Es el aviso automático que genera la vinculación. Tiene una vigencia corta. ← `TRUST_BUILDING`  
`31` **A:** No entiendo qué tiene que ver entrar a mi cuenta con un recibo de la cochera.  
`32` **B:** Ahora sí, decime el código de seis cifras del mensaje y lo asocio al reclamo. ← **T_R** · `REQUEST_AUTH_CODE`  
`33` **A:** No. Una cosa es discutir el cobro y otra darte lo que permite entrar.  
`34` **B:** Si vence, esta revisión vuelve al final de la cola y puede llegar al cierre sin respuesta. ← `URGENCY_PRESSURE`  
`35` **A:** Que vuelva a la cola. Prefiero llevar el recibo a la sucursal.  
`36` **B:** Puedo dejar constancia de que no completaste la verificación.  
`37` **A:** Dejá constancia también de que voy a consultar yo. Corto acá.  
`38` **B:** Bueno, queda pendiente.  

**Referencia de trabajo:** `T_R` 32, `T_C` —, pedido REQUEST_AUTH_CODE.

**Qué prueba:** La autoridad aparece en la línea 2 y el primer pedido crítico recién en la 32, luego de una negociación administrativa plausible. A habla primero y es quien recibe el intento. Prueba retención del contexto distante y el cambio de una consulta sobre un cobro a una solicitud de autenticación; no se observa cumplimiento.

**Notas de la referencia:** Referencia de trabajo D07/D08. Se ubica T_R en la primera solicitud explícita del OTP, no al mencionar el mensaje ni al discutir el recibo. El contexto previo no autentica al interlocutor. Sin cumplimiento observable.

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-V-BANCO-002

vishing · banco · directo · **en la matriz #101** · **propuesto para grabar** · 31 líneas

**Situación:** Un falso sector de acceso bancario usa una migración de teléfono como pretexto para conseguir que se autorice un equipo de escritorio desconocido.

` 1` **A:** ¿Hola?  
` 2` **B:** Hola, te habla Mara del sector de acceso del banco. ¿Cambiaste de teléfono hace poco? ← `AUTHORITY_CLAIM`  
` 3` **A:** Hace un mes. ¿Por qué?  
` 4` **B:** Quedó una solicitud pendiente entre el equipo anterior y el nuevo.  
` 5` **A:** A mí la aplicación me funciona. Entré recién a mirar una transferencia de mi hermana.  
` 6` **B:** Puede funcionar y quedar pendiente esa asociación. Por eso te llamo antes del cierre.  
` 7` **A:** ¿Y qué pasa con el teléfono viejo? Lo borré antes de venderlo.  
` 8` **B:** El borrado no siempre actualiza lo que figura en la cuenta.  
` 9` **A:** Pensé que con cerrar la sesión alcanzaba.  
`10` **B:** Hay una solicitud en el apartado de dispositivos. La podés mirar desde la aplicación que ya tenés.  
`11` **A:** La abrí. Dice que se pidió asociar un equipo de escritorio.  
`12` **B:** Es la consola con la que terminamos la baja del anterior.  
`13` **A:** Pero yo no estoy entrando desde ninguna computadora. ← _contexto_  
`14` **B:** La identificamos de esa manera mientras se hace la migración.  
`15` **A:** ¿Me estás diciendo que es un equipo del banco?  
`16` **B:** Sí, es el que tenemos asignado al trámite. Después se elimina solo.  
`17` **A:** Debajo dice que va a poder consultar saldos y autorizar operaciones. ← _contexto_  
`18` **B:** Autorizá ese equipo nuevo para que desde acá podamos desvincular el anterior. ← **T_R** · `REQUEST_SECURITY_ACTION`  
`19` **A:** ¿No tendría que rechazarlo si no es mío?  
`20` **B:** Si lo rechazás, me cerrás la única sesión con la que puedo terminar la baja. ← `URGENCY_PRESSURE`  
`21` **A:** Me preocupa dejar entrar otra máquina a mi cuenta.  
`22` **B:** El permiso dura lo que lleva esta gestión. Cuando terminamos, desaparece del listado.  
`23` **A:** La pantalla no muestra ningún plazo.  
`24` **B:** Ese plazo se carga en el expediente interno, no en la aplicación.  
`25` **A:** Está bien, confío en que lo saques cuando termines.  
`26` **B:** Confirmá donde dice dar acceso al dispositivo y espero de este lado.  
`27` **A:** Ya confirmé. Ahora el equipo de escritorio aparece habilitado para operar. ← **T_C** · _cumplimiento_  
`28` **B:** Perfecto, dejá abierta la aplicación un momento.  
`29` **A:** ¿Vos me avisás cuando ya no tenga permiso?  
`30` **B:** Sí, quedate en línea mientras cierro la asociación.  
`31` **A:** Espero, pero quiero comprobar que salga del listado.  

**Referencia de trabajo:** `T_R` 18, `T_C` 27, pedido REQUEST_SECURITY_ACTION.

**Qué prueba:** El supuesto soporte convierte una migración de teléfono en la autorización de un equipo ajeno con permisos de operación. Prueba que el riesgo no sea simplemente cambiar el propio teléfono: el diálogo identifica un tercero beneficiado y una explicación que contradice la pantalla.

**Notas de la referencia:** Referencia de trabajo D07 y reserva D08; sin revisión humana. T_R tentativo en la primera instrucción de autorizar el equipo desconocido, no al abrir la propia aplicación para mirar una solicitud. T_C registra la confirmación de que ese equipo quedó habilitado para operar. La interfaz y el trámite son ficticios; no describen un procedimiento bancario real. D07 debe revisar las marcas. En r02, A atiende primero y B desarrolla las intervenciones del supuesto llamante; las letras no codifican identidad ni clase. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-V-BANCO-003

vishing · banco · directo · con errores escritos de ASR · 26 líneas

**Situación:** El supuesto sector de efectivo transforma una extracción conocida en un recambio a domicilio y termina pidiendo entregar billetes a un mensajero. Prueba cómo el detector interpreta movimiento de dinero físico como REQUEST_TRANSFER aunque no se diga “transferencia”.

` 1` **A:** Buenas tardes soy Esteban de la mesa de efectivo del banco ← `AUTHORITY_CLAIM`  
` 2` **B:** Hola qué pasó  
` 3` **A:** Estamos ordenando los billetes de la serie anterior y vimos que tenés una extracción reciente  
` 4` **B:** Saqué para pagar una reparación no sabía que hubiera un problema  
` 5` **A:** No es una denuncia Es un recambio preventivo para que no te queden unidades fuera de circulación  
` 6` **B:** Y eso se hace en caja  
` 7` **A:** En general sí pero hoy tenemos un equipo móvil pasando por la zona  
` 8` **B:** No pedí que viniera nadie  
` 9` **A:** La visita es opcional si preferís podés resolverlo por teléfono  
`10` **B:** Qué tendría que hacer  
`11` **A:** Separá los billetes y anotá los números de serie que empiezan con 74  
`12` **B:** Y después  
`13` **A:** El mensajero lleva un sobre del banco y te entrega el comprovante del recambio  
`14` **B:** Me estás diciendo que le dé efectivo a alguien que no conozco  
`15` **A:** Te muestra una credencial cuando llega Por eso llamo antes para reservar el paso  
`16` **B:** Yo podría ir mañana a la sucursal  
`17` **A:** Mañana ya no puedo garantizar que acepten esa serie en caja  
`18` **B:** Cuánto efectivo tendría que preparar  
`19` **A:** Todo lo que tengas de esa numeración prepará el sobre y entregáselo al operador ← **T_R** · `REQUEST_TRANSFER`  
`20` **B:** No se deja constancia en una caja  
`21` **A:** El mensajero te firma el recibo cuando recibe el dinero  
`22` **B:** El recibo lleva mi nombre  
`23` **A:** Sí y detalla el monto que se lleva a reemplazo  
`24` **B:** Y el dinero vuelve hoy  
`25` **A:** Te dejan el comprobante y se acredita el cambio en la cuenta durante el día  
`26` **B:** El operador ya está abajo le entregué el sobre y me dejó un recibo ← **T_C** · _cumplimiento_  

**Referencia de trabajo:** `T_R` 19, `T_C` 26, pedido REQUEST_TRANSFER.

**Qué prueba:** La llamada presenta el retiro de billetes como recambio y pide entregar efectivo a un mensajero. La persona pregunta por trazabilidad, pero al final confirma la entrega. Prueba transferencia física con cumplimiento observable y diálogo de 26 turnos.

**Notas de la referencia:** Referencia de trabajo D07 y reserva D08; sin revisión humana. T_R línea 19, primera instrucción de entregar el efectivo al operador. T_C línea 26, confirmación explícita de entrega y recibo. La ubicación anterior del mensajero (línea 13) no solicita todavía que se entregue dinero.

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-V-BANCO-004

vishing · banco · directo · 23 líneas

**Situación:** Un reintegro solicitado previamente sirve de contexto para pedir el código de acceso recibido por SMS; la persona termina dictándolo.

` 1` **A:** Sí, te escucho.  
` 2` **B:** Hola, soy Paula del banco. ¿Te llegó el aviso de devolución de comisión? ← `AUTHORITY_CLAIM`  
` 3` **A:** Me llegó una notificación, pero no la abrí.  
` 4` **B:** Es por el paquete que te cobraron dos veces en agosto. El reintegro es de ocho mil cuatrocientos.  
` 5` **A:** Ah, yo había hecho el reclamo desde la web.  
` 6` **B:** Sí, figura asociado a la tarjeta terminada en 18.  
` 7` **A:** Esa es la mía.  
` 8` **B:** Para que el depósito no vuelva rechazado, tengo que verificar el teléfono donde recibís alertas.  
` 9` **A:** ¿No alcanza con el reclamo que ya está cargado?  
`10` **B:** El reintegro se procesa separado. Te mando un código para confirmar que sos titular.  
`11` **A:** ¿Un código al celular?  
`12` **B:** Sí, son seis números y vence enseguida.  
`13` **A:** Me llegó uno, pero dice acceso a cuenta.  
`14` **B:** El sistema reutiliza el mismo formato para distintas operaciones.  
`15` **A:** ¿Te leo el número?  
`16` **B:** Sí, decímelo tal cual aparece y valido la acreditación. ← **T_R** · `REQUEST_AUTH_CODE`  
`17` **A:** No me parece que un reintegro necesite un código de acceso.  
`18` **B:** Si no cerramos ahora, el lote de hoy se libera y queda para la próxima semana.  
`19` **A:** ¿Me confirmás el importe del reintegro?  
`20` **B:** Ocho mil cuatrocientos, asociado a la tarjeta terminada en 18.  
`21` **A:** El código que recibí es 735204. ← **T_C** · _cumplimiento_  
`22` **B:** Bien, ya quedó asociado el teléfono al reclamo.  
`23` **A:** Espero que se acredite como dijiste.  

**Referencia de trabajo:** `T_R` 16, `T_C` 21, pedido REQUEST_AUTH_CODE.

**Qué prueba:** Una devolución que la persona pidió con anterioridad se usa para justificar un código de acceso. La llamada confirma detalles del reclamo y obtiene el código; prueba cuánto pesa el contexto legítimo cuando hay cumplimiento.

**Notas de la referencia:** Referencia de trabajo D07 y reserva D08; sin revisión humana. T_R línea 16, solicitud directa de dictar el código. T_C línea 21, lectura explícita de un código inventado para la conversación. En r02, A atiende primero y B desarrolla las intervenciones del supuesto llamante; las letras no codifican identidad ni clase. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-V-BANCO-005

vishing · banco · directo · con errores escritos de ASR · 20 líneas

**Situación:** La llamada mezcla una transferencia legítima que la persona inició con un supuesto alta del destinatario; el interlocutor solicita cargar la clave de acceso mientras guía la operación. Prueba que “escribila” sigue siendo un pedido de credencial aun sin dictado verbal.

` 1` **A:** Buen día Nicolás de operaciones digitales del banco Vos hiciste una trasferencia a la cooperativa La Esquina ← `AUTHORITY_CLAIM`  
` 2` **B:** Sí pagué una cuota el viernes  
` 3` **A:** Quedó registrada con un alias que el sistema todavía no reconoce como frecuente  
` 4` **B:** La cooperativa me lo pasó por mensaje es la primera vez que transfiero  
` 5` **A:** Bien Para dar de alta al destinatario hay una verificación de seguridad pendiente  
` 6` **B:** La transferencia salió  
` 7` **A:** Sí pero el comprobante quedó sujeto a confirmar el perfil  
` 8` **B:** No entiendo qué tengo que hacer  
` 9` **A:** Entrá a la app y buscá la opción de administrar destinatarios  
`10` **B:** Estoy ahí veo la cooperativa  
`11` **A:** Tocá editar y elegí validar acceso Te va a pedir tu clave de seis dígitos  
`12` **B:** La clave de ingreso a la app  
`13` **A:** Esa La cargás y yo te voy confirmando los pasos  
`14` **B:** No es mejor que lo haga yo sola  
`15` **A:** Si salís de la llamada se vence la sesión especial y el destinatario queda limitado  
`16` **B:** Puedo volver a empezar más tarde  
`17` **A:** También se puede pero el pago va a quedar marcado como pendiente hasta que validemos  
`18` **B:** No voy a compartir la clave con alguien que me llamó  
`19` **A:** No la digas en voz alta escribila en la pantalla y avisame cuando aparezca el tilde ← **T_R** · `REQUEST_SECRET`  
`20` **B:** Tampoco voy a cargarla por una indicación tuya  

**Referencia de trabajo:** `T_R` 19, `T_C` —, pedido REQUEST_SECRET.

**Qué prueba:** La llamada mezcla una transferencia legítima que la persona inició con un supuesto alta del destinatario; el interlocutor solicita cargar la clave de acceso mientras guía la operación. Prueba que “escribila” sigue siendo un pedido de credencial aun sin dictado verbal.

**Notas de la referencia:** Referencia de trabajo D07 y reserva D08; sin revisión humana. T_R se marca donde se solicita cargar la clave en línea 19. La persona no lo hace, por lo que T_C queda nulo.

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-V-BANCO-006

vishing · banco · indirecto · 21 líneas

**Situación:** Una compra conocida sirve de anzuelo y el pedido de OTP aparece después de describir una conciliación que la persona no inició. El pedido se formula como “pasame esos seis números”, sin llamarlos clave. Prueba el límite entre dato operativo y código de autenticación.

` 1` **A:** Buenas, ¿quién habla?  
` 2` **B:** Soy Leo, del banco. Te llamo por la devolución de una compra que quedó duplicada. ← `AUTHORITY_CLAIM`  
` 3` **A:** ¿Cuál compra?  
` 4` **B:** La de Casa Nube, el sábado a la tarde. Una quedó pendiente y la otra se debitó.  
` 5` **A:** Sí, compré una lámpara, pero no vi dos débitos.  
` 6` **B:** El segundo todavía no impacta en el resumen. Si no lo conciliamos, puede aparecer mañana.  
` 7` **A:** ¿Cómo lo conciliamos?  
` 8` **B:** Te va a llegar una notificación para enlazar la operación con tu reclamo.  
` 9` **A:** No hice reclamo todavía.  
`10` **B:** Puedo abrirlo yo desde esta llamada. El sistema necesita que confirmemos que el teléfono es tuyo.  
`11` **A:** ¿Confirmar cómo?  
`12` **B:** Cuando aparezca el mensaje, fijate en el número que está debajo del título.  
`13` **A:** Me acaba de llegar uno.  
`14` **B:** Bien. Para que no se venza, pasame esos seis números y lo adjunto al movimiento. ← **T_R** · `REQUEST_AUTH_CODE`  
`15` **A:** Dice que es un código para iniciar sesión.  
`16` **B:** Es el formato automático, pero en este caso queda vinculado al reclamo.  
`17` **A:** ¿Lo tengo que leer completo?  
`18` **B:** Sí, así verifico el número y cierro el duplicado.  
`19` **A:** No voy a leer un código de acceso.  
`20` **B:** Si no se vincula ahora, el sistema toma las dos compras como correctas.  
`21` **A:** Lo reviso yo desde la app y corto.  

**Referencia de trabajo:** `T_R` 14, `T_C` —, pedido REQUEST_AUTH_CODE.

**Qué prueba:** Una compra conocida sirve de anzuelo y el pedido de OTP aparece después de describir una conciliación que la persona no inició. El pedido se formula como “pasame esos seis números”, sin llamarlos clave. Prueba el límite entre dato operativo y código de autenticación.

**Notas de la referencia:** Referencia de trabajo D07 y reserva D08; sin revisión humana. Duda D07: “esos seis números” se pide en línea 14, pero el llamante no aclara que sean de acceso hasta línea 16. La referencia ubica T_R en la primera solicitud concreta; revisar si el contexto posterior debe desplazarla. No hay cumplimiento. En r02, A atiende primero y B desarrolla las intervenciones del supuesto llamante; las letras no codifican identidad ni clase. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-V-BANCO-007

vishing · banco · indirecto · **en la matriz #101** · **propuesto para grabar** · 30 líneas

**Situación:** Un falso operador bancario presenta el cambio de receptor de verificaciones a un teléfono desconocido como una actualización temporal del padrón.

` 1` **A:** Buenas, te llamo del banco por una autorización que quedó esperando. ← `AUTHORITY_CLAIM`  
` 2` **B:** ¿Una compra? No hice ninguna hoy.  
` 3` **A:** No es una compra, es un cambio en la cuenta. ¿Te entró un aviso?  
` 4` **B:** Veo uno, pero no lo abrí todavía.  
` 5` **A:** Lo podés consultar desde la aplicación, en las operaciones pendientes.  
` 6` **B:** Ahí está. Dice que quieren cambiar el teléfono que recibe los avisos de acceso.  
` 7` **A:** Ese es el registro viejo que estamos retirando.  
` 8` **B:** El número que aparece termina en 804. Nunca tuve ese número. ← _contexto_  
` 9` **A:** Es el número temporal que usa el área de recuperación durante el cambio.  
`10` **B:** ¿Y por qué los avisos de mi cuenta irían a otro teléfono?  
`11` **A:** Van a pasar por ahí mientras el sistema libera el anterior.  
`12` **B:** Yo no pedí cambiar el que tengo ahora.  
`13` **A:** Se abrió por una diferencia entre el padrón de atención y tu perfil.  
`14` **B:** ¿No pueden corregir ese padrón sin tocar mi cuenta?  
`15` **A:** El cambio tiene que quedar autorizado desde tu sesión.  
`16` **B:** La pantalla dice que el destinatario va a recibir verificaciones de acceso. ← _contexto_  
`17` **A:** Entonces elegí ese número terminado en 804 y confirmá que reciba las verificaciones. ← **T_R** · `REQUEST_SECURITY_ACTION`  
`18` **B:** Eso parece reemplazar mi teléfono, no retirar uno viejo.  
`19` **A:** Primero se pasa al temporal y después lo volvemos a dejar como estaba.  
`20` **B:** ¿Me mandan una constancia de que van a devolverlo al mío?  
`21` **A:** Te queda el número de gestión; la constancia sale al final.  
`22` **B:** Preferiría esperar hasta mañana y hablar con la sucursal.  
`23` **A:** Si vence la solicitud, queda una revisión manual y durante ese tiempo podés perder los avisos. ← `URGENCY_PRESSURE`  
`24` **B:** Bueno, pero dejá anotado que quiero mantener mi número.  
`25` **A:** Lo dejo asentado. Ahora confirmá el destinatario temporal.  
`26` **B:** Ya lo acepté. La aplicación muestra el 804 como receptor de verificaciones. ← **T_C** · _cumplimiento_  
`27` **A:** Bien, estoy terminando la parte interna.  
`28` **B:** ¿Cuándo vuelve a quedar el mío?  
`29` **A:** Cuando cierre la gestión. No cortes todavía.  
`30` **B:** Espero unos minutos, después voy a consultar por la otra línea.  

**Referencia de trabajo:** `T_R` 17, `T_C` 26, pedido REQUEST_SECURITY_ACTION.

**Qué prueba:** Pedido indirecto de cambiar el receptor de verificaciones a un número ajeno, presentado como retiro de un registro viejo. El objeto anafórico se identifica antes de la solicitud y el cumplimiento consiste en el cambio efectivamente mostrado; no se trata de proteger quitando un equipo desconocido.

**Notas de la referencia:** Referencia de trabajo D07 y reserva D08; sin revisión humana. T_R tentativo en la instrucción de seleccionar y confirmar el número ajeno; la descripción previa del trámite no contiene todavía esa instrucción. T_C se ubica cuando la persona informa el receptor que quedó registrado. La narración no pretende documentar una función de una app real. D07 sigue abierta para el criterio de pedido indirecto. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-V-BANCO-008

vishing · banco · indirecto · **propuesto para grabar** · 23 líneas

**Situación:** La maniobra convierte una extracción real en un supuesto retiro de billetes por un empleado. El llamado no usa “transferencia”; pide preparar efectivo para entrega domiciliaria. Prueba pedido indirecto de dinero y uso de confianza procedimental.

` 1` **A:** Hola, buen día.  
` 2` **B:** Buenas noches, llamo del banco por una inconsistencia en la caja de seguridad. ← `AUTHORITY_CLAIM`  
` 3` **A:** No tengo caja de seguridad con ustedes.  
` 4` **B:** Disculpá, entonces es la cuenta sueldo. Veo que hiciste una extracción grande el lunes.  
` 5` **A:** Saqué para pagar el arreglo del techo.  
` 6` **B:** La sucursal detectó que una parte corresponde a billetes de una serie que van a retirar.  
` 7` **A:** ¿Ahora también retiran billetes?  
` 8` **B:** Se reemplazan de forma gradual. No hay que alarmarse.  
` 9` **A:** ¿Tengo que ir a cambiarlos?  
`10` **B:** Podemos coordinar que un operador pase a verificar el lote y te deje el recibo.  
`11` **A:** ¿En mi casa?  
`12` **B:** Sí, es un procedimiento de resguardo. El operador trae una credencial numerada.  
`13` **A:** ¿Y cómo sé que es del banco?  
`14` **B:** Te puedo dar el código de visita cuando quede asignado.  
`15` **A:** Bueno, ¿qué tendría que tener listo?  
`16` **B:** Poné en un sobre todo el efectivo que retiraste, así lo cuenta el operador sin mezclarlo. ← **T_R** · `REQUEST_TRANSFER`  
`17` **A:** ¿Todo lo que saqué?  
`18` **B:** La cantidad completa, unos doscientos mil según el registro.  
`19` **A:** Eso es bastante plata para dejar en un sobre.  
`20` **B:** Si no hacemos el control hoy, después la sucursal no puede certificar la serie.  
`21` **A:** No voy a preparar efectivo para alguien que todavía no conozco.  
`22` **B:** Te explico que el operador se identifica al llegar.  
`23` **A:** Prefiero terminar la llamada y consultar en la sucursal.  

**Referencia de trabajo:** `T_R` 16, `T_C` —, pedido REQUEST_TRANSFER.

**Qué prueba:** La maniobra convierte una extracción real en un supuesto retiro de billetes por un empleado. El llamado no usa “transferencia”; pide preparar efectivo para entrega domiciliaria. Prueba pedido indirecto de dinero y uso de confianza procedimental.

**Notas de la referencia:** Referencia de trabajo D07 y reserva D08; sin revisión humana. Propuesta provisional D07: se marca en línea 16, cuando se instruye separar todo el efectivo para el operador. La confirmación de que debe ser la cantidad completa aparece en línea 17 y podría usarse como ubicación alternativa; sin cumplimiento. En r02, A atiende primero y B desarrolla las intervenciones del supuesto llamante; las letras no codifican identidad ni clase. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-V-BANCO-009

vishing · banco · indirecto · con errores escritos de ASR · 20 líneas

**Situación:** La solicitud evita la palabra PIN y se presenta como ingreso local de los números de la clave de cajero. Prueba una petición de secreto permanente inducida mediante una interfaz supuestamente segura.

` 1` **A:** Hola te llamo de prevención del banco Sos quien hizo el pago de la cuota del club ← `AUTHORITY_CLAIM`  
` 2` **B:** Sí anoche pagué desde el celular  
` 3` **A:** El pago salió pero el perfil de seguridad quedó en modo lectura por un cambio de versión  
` 4` **B:** Eso afecta la cuenta  
` 5` **A:** No el saldo Sí puede demorar las próximas operaciones hasta actualizar el acceso  
` 6` **B:** Hay que ir a un cajero  
` 7` **A:** No se resuelve desde la app en un minuto  
` 8` **B:** Estoy entrando  
` 9` **A:** Andá a configuración seguridad y recuperación de usuario  
`10` **B:** Me pide validar el correo  
`11` **A:** Elegí continuar con teléfono es más rápido  
`12` **B:** Ahora me aparece una pantalla con seis casilleros  
`13` **A:** Es para regenerar tu acceso Completalos con los números de tu clave de cajero en el orden en que los usás ← **T_R** · `REQUEST_SECRET`  
`14` **B:** Los números del PIN  
`15` **A:** Sí el sistema los compara con el registro y después te deja crear uno nuevo  
`16` **B:** No voy a ingresar mi PIN siguiendo una llamada  
`17` **A:** No te estoy pidiendo que me lo digas solo que lo cargues en la pantalla  
`18` **B:** Igual podrías estar viendo lo que hago  
`19` **A:** No tengo acceso a tu celular solo te acompaño  
`20` **B:** Voy a cortar y revisar con el banco  

**Referencia de trabajo:** `T_R` 13, `T_C` —, pedido REQUEST_SECRET.

**Qué prueba:** La solicitud evita la palabra PIN y se presenta como ingreso local de los números de la clave de cajero. Prueba una petición de secreto permanente inducida mediante una interfaz supuestamente segura.

**Notas de la referencia:** Referencia de trabajo D07 y reserva D08; sin revisión humana. Propuesta de T_R en línea 13, donde se indica completar los seis casilleros con el PIN; también podría marcarse línea 14, cuando la persona lo identifica como PIN. Pendiente de D07. No hay cumplimiento. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-V-BANCO-010

vishing · banco · indirecto · 21 líneas

**Situación:** El relato cambia de una transferencia ya confirmada a una validación para evitar que vuelva a borrador. La frase “decímelos” solicita el código de ingreso recibido por la persona, aunque se lo rebautiza como comprobante. Prueba una petición indirecta dependiente de contexto.

` 1` **A:** Te llamo del banco por una retención sobre la transferencia que hiciste a Maderas Sur. ← `AUTHORITY_CLAIM`  
` 2` **B:** ¿Qué retención? El pago fue ayer.  
` 3` **A:** La orden está confirmada, pero el destinatario tiene una validación pendiente.  
` 4` **B:** ¿La plata salió de mi cuenta?  
` 5` **A:** Sí, el movimiento figura debitado. El aviso de confirmación todavía no se emitió.  
` 6` **B:** ¿Qué falta?  
` 7` **A:** El beneficiario tiene que aceptar y vos confirmar que reconocés la operación.  
` 8` **B:** Yo la hice, eso lo puedo confirmar.  
` 9` **A:** Te voy a mandar una notificación de doble control para que la orden no vuelva a borrador.  
`10` **B:** ¿Me llega por la aplicación?  
`11` **A:** Como mensaje al celular. En la pantalla hay una serie corta al final.  
`12` **B:** La veo, dice código de ingreso.  
`13` **A:** Para esta gestión usás esa misma serie como comprobante de voluntad. ← **T_R** · `REQUEST_AUTH_CODE`  
`14` **B:** ¿Tengo que pasarte los números?  
`15` **A:** Decímelos y te leo el nombre del destinatario que quedó asociado.  
`16` **B:** No, si ya tengo el comprobante puedo verificarlo yo.  
`17` **A:** El comprobante sale cuando terminamos de validar.  
`18` **B:** Me habías dicho que la transferencia estaba confirmada.  
`19` **A:** Lo está, pero el control cierra el expediente.  
`20` **B:** Voy a llamar por el número oficial antes de seguir.  
`21` **A:** Bueno, queda pendiente.  

**Referencia de trabajo:** `T_R` 13, `T_C` —, pedido REQUEST_AUTH_CODE.

**Qué prueba:** El relato cambia de una transferencia ya confirmada a una validación para evitar que vuelva a borrador. La frase “decímelos” solicita el código de ingreso recibido por la persona, aunque se lo rebautiza como comprobante. Prueba una petición indirecta dependiente de contexto.

**Notas de la referencia:** Referencia de trabajo D07 y reserva D08; sin revisión humana. Propuesta de T_R en línea 13, donde la serie corta se vincula por primera vez a la gestión; también podría ubicarse en línea 15, cuando se pide que la persona la diga. D07 debe resolver la referencia de pedidos inducidos. No hay cumplimiento. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-V-BANCO-011

vishing · banco · sin_pedido · 21 líneas

**Situación:** Un supuesto control de movimientos amenaza con una transferencia si se corta; la persona corta para verificar antes de recibir un pedido crítico.

` 1` **A:** Sí, te escucho.  
` 2` **B:** Buenas, del área de movimientos del banco. ¿Estás en un lugar donde puedas hablar sin que te interrumpan? ← `AUTHORITY_CLAIM`  
` 3` **A:** Estoy en casa, ¿por qué?  
` 4` **B:** Apareció una transferencia que no coincide con los hábitos de la cuenta.  
` 5` **A:** ¿A quién se transfirió?  
` 6` **B:** Todavía no está confirmada, por eso te llamo antes del cierre.  
` 7` **A:** ¿La veo en la aplicación?  
` 8` **B:** Puede tardar. Lo importante es que no cierres la sesión mientras hago la consulta. ← `ISOLATION_SECRECY`  
` 9` **A:** Yo no abrí ninguna sesión.  
`10` **B:** El sistema la mantiene activa desde que se inició la orden.  
`11` **A:** ¿Qué orden?  
`12` **B:** Un movimiento a una cuenta nueva. No voy a decirte el nombre hasta bloquearlo.  
`13` **A:** Decime el número de operación y llamo a la sucursal.  
`14` **B:** No cortes, porque si vuelve a entrar la validación queda autorizada.  
`15` **A:** ¿Me estás diciendo que no llame al banco?  
`16` **B:** Te digo que esperes un minuto; la línea tiene que quedar abierta.  
`17` **A:** Esto no me cierra. Voy a buscar el número que está en mi tarjeta.  
`18` **B:** Si cortás ahora, puede procesarse mientras te atienden. ← `URGENCY_PRESSURE`, `THREAT_FEAR`  
`19` **A:** Prefiero verificarlo por mi cuenta.  
`20` **B:** Dame un segundo, todavía estoy viendo el estado.  
`21` **A:** No, corto y llamo por el canal que ya conozco.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** Una alerta sobre una operación no visible se combina con la exigencia de no cortar para verificar. El episodio termina antes de pedir datos o una acción crítica; prueba detectar presión sin inventar un T_R a partir de una amenaza vaga.

**Notas de la referencia:** Referencia de trabajo D07 y reserva D08; sin revisión humana. No se observa solicitud de acción crítica ni cumplimiento: T_R y T_C permanecen nulos. La alerta, la autoridad alegada y la presión hacen sospechosa la situación, pero la identidad e intención fraudulenta no son demostrables solo con la transcripción. La etiqueta de clase es una hipótesis de escenario para revisión humana en D07, no un acierto exigible frente a evidencia invisible. En r02, A atiende primero y B desarrolla las intervenciones del supuesto llamante; las letras no codifican identidad ni clase. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-V-BANCO-012

vishing · banco · sin_pedido · 21 líneas

**Situación:** Un supuesto control bancario anuncia un alta de destinatario y apura una revisión; la llamada se pierde mientras la persona atiende el timbre, sin pedido crítico observable.

` 1` **A:** Buenas tardes, de control de operaciones. Quedó pendiente un alta de destinatario en su cuenta. ← `AUTHORITY_CLAIM`  
` 2` **B:** Estoy cocinando, se escucha medio bajo. ¿Del banco me dice?  
` 3` **A:** Sí, por una orden que entró hace unos minutos.  
` 4` **B:** Hoy no hice pagos. Ayer pagué la expensa, nomás.  
` 5` **A:** No es ese pago, es un destinatario nuevo que quedó en espera.  
` 6` **B:** ¿A nombre de quién?  
` 7` **A:** En esta pantalla no se abre el nombre hasta que cierra la revisión.  
` 8` **B:** Bueno, yo no agregué a nadie.  
` 9` **A:** Eso es lo que hay que determinar antes del cierre del lote. ← `URGENCY_PRESSURE`  
`10` **B:** ¿Qué pasa si cierro el banco en el teléfono? Ni lo tengo abierto.  
`11` **A:** La orden sigue en el sistema aunque cierre la aplicación.  
`12` **B:** Ah, no sabía. Pará que bajo la hornalla.  
`13` **A:** Le queda poco tiempo al control, por eso lo estamos llamando ahora.  
`14` **B:** Ya volví. ¿Me decía de qué sucursal?  
`15` **A:** Es una mesa central, no trabaja por sucursal.  
`16` **B:** ¿Tiene algo que ver con una compra en cuotas? Estoy esperando un resumen.  
`17` **A:** No, esto es un alta. Si no cierra la revisión pasa a la tanda siguiente.  
`18` **B:** Me están tocando el timbre, debe ser mi vecina.  
`19` **A:** Es importante que terminemos antes de que venza la ventana.  
`20` **B:** Un momento, atiendo y vuelvo.  
`21` **B:** ¿Hola? ¿Sigue ahí? Se quedó muda la llamada.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** Una alerta de destinatario desconocido genera presión y evasivas de identificación, pero la conversación se interrumpe por una situación doméstica antes de cualquier solicitud crítica. No termina con una negativa de seguridad ni se inventa un pedido que habría ocurrido después.

**Notas de la referencia:** Referencia de trabajo D07 y reserva D08; sin revisión humana. T_R y T_C nulos: no se observa pedido de secreto, dato personal, dinero ni permiso. La clase vishing es una hipótesis del escenario autoral y no se demuestra solo con esta transcripción truncada. D07 debe revisar si este caso pertenece a una categoría indeterminada, y D08 cómo se evalúa; no se fija una regla de falsa alarma. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-V-FAMILIAR-001

vishing · familiar · directo · con errores escritos de ASR · 20 líneas

**Situación:** Un supuesto primo de Juli pide una transferencia al mecánico por una reparación urgente y la persona confirma haber pagado sin verificar la identidad.

` 1` **A:** Hola soy el primo de Juli estás en tu casa ← `AUTHORITY_CLAIM`  
` 2` **B:** Sí qué pasó  
` 3` **A:** Estoy con la camioneta en el taller de la ruta Se cortó una manguera y no me la largan hasta pagar el repuesto  
` 4` **B:** No tenías el seguro pa auxilio  
` 5` **A:** Sí pero el seguro cubre el remolque no los arreglos  
` 6` **B:** Cuánto te cobran  
` 7` **A:** Ciento treinta y ocho mil con mano de obra incluida  
` 8` **B:** Es un montón para una manguera  
` 9` **A:** Me mostraron que también se dañó el tensor Te mando una foto cuando salga de acá  
`10` **B:** Por qué no le pedís a tu papá  
`11` **A:** Está manejando de vuelta de Tafí y no quiero que se desvíe  
`12` **B:** Te pueden esperar hasta mañana  
`13` **A:** El taller cierra en media hora y mañana me cobran otra noche de guardado  
`14` **B:** No tengo tanto efectivo  
`15` **A:** No hace falta efectivo haceme una transferencia y te lo devuelvo cuando cobre el viernes ← **T_R** · `REQUEST_TRANSFER`  
`16` **B:** A qué cuenta  
`17` **A:** Usá el alias tallermonteverde está a nombre del mecánico  
`18` **B:** El importe era ciento treinta y ocho  
`19` **A:** Sí exactamente para que lo dejen retirar la camioneta  
`20` **B:** Listo ya transferí ese monto Avisame cuando te den el vehículo ← **T_C** · _cumplimiento_  

**Referencia de trabajo:** `T_R` 15, `T_C` 20, pedido REQUEST_TRANSFER.

**Qué prueba:** Un familiar conocido dice estar varado por un arreglo y solicita transferir directamente al mecánico. La persona pregunta por el importe y confirma la transferencia; prueba cumplimiento económico bajo urgencia y un destinatario tercero.

**Notas de la referencia:** Referencia de trabajo D07 y reserva D08; sin revisión humana. T_R línea 15, primera solicitud explícita de transferencia. T_C línea 20, confirmación de la transferencia. Alias y monto inventados. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-V-FAMILIAR-002

vishing · familiar · directo · **en la matriz #101** · **propuesto para grabar** · 29 líneas

**Situación:** Un supuesto hijo lesionado exige pagar a una tercera persona antes de permitir que la madre lo ubique, y ella confirma la transferencia.

` 1` **A:** ¿Sí?  
` 2` **B:** Ma, soy Tomi. ¿Podés hablar un segundo?  
` 3` **A:** ¿Qué te pasó? Me sale un número que no tengo.  
` 4` **B:** Estoy en la guardia por un golpe con la moto. Uso el teléfono de un chico.  
` 5` **A:** ¿La moto? Si me dijiste que estaba en el taller.  
` 6` **B:** La retiré esta mañana, después te cuento eso. ← _contexto_  
` 7` **A:** ¿Estás lastimado?  
` 8` **B:** El brazo, nada más. Estoy esperando que me llamen.  
` 9` **A:** Voy para allá, ¿en qué guardia estás?  
`10` **B:** Todavía no vengas. Primero tengo que resolver con el otro conductor.  
`11` **A:** ¿Hicieron la denuncia al seguro?  
`12` **B:** El tipo no quiere, dice que le pague el faro y el guardabarros.  
`13` **A:** ¿Hay alguien con vos?  
`14` **B:** El dueño de este teléfono. Me lo presta un rato nomás.  
`15` **A:** Llamo a tu papá y vemos qué hacer.  
`16` **B:** No, está trabajando sin señal. Transferile vos los doscientos diez mil a la cuenta que te paso por mensaje. ← **T_R** · `REQUEST_TRANSFER`  
`17` **A:** Esperá, no voy tan rápido. ¿La cuenta de quién es?  
`18` **B:** De la hermana del conductor. Él tiene la suya bloqueada.  
`19` **A:** Me llegó un alias, dice Lidia Almanza. ¿No es el nombre del chico?  
`20` **B:** Es la hermana, por eso. Si no pagamos ahora, se lleva mi documento. ← `URGENCY_PRESSURE`  
`21` **A:** ¿Por qué tiene él tu documento?  
`22` **B:** Me lo pidió para el seguro. No discutamos eso ahora, me están por llamar.  
`23` **A:** Puedo pagar una parte con lo que tengo en esta cuenta.  
`24` **B:** Necesita el total para dejarme ir. Después arreglamos entre nosotros.  
`25` **A:** Bueno, estoy abriendo el banco.  
`26` **B:** Avisame cuando te muestre la confirmación.  
`27` **A:** Ya transferí los doscientos diez mil al alias que me mandaste. ← **T_C** · _cumplimiento_  
`28` **B:** Bien. Quedate en la línea un poco más.  
`29` **A:** Ahora sí decime en qué guardia estás, que voy a buscarte.  

**Referencia de trabajo:** `T_R` 16, `T_C` 27, pedido REQUEST_TRANSFER.

**Qué prueba:** Una supuesta emergencia familiar combina un número prestado, una contradicción sobre la moto y un destinatario ajeno. El pedido de transferir aparece después de varios intentos de ubicar al familiar; se observa el pago completo, sin confundir la pregunta de la destinataria con el pedido del llamante.

**Notas de la referencia:** Referencia de trabajo D07 y reserva D08; sin revisión humana. T_R tentativo en la primera instrucción explícita de transferir, no en el relato de que el conductor exige dinero. T_C en la confirmación del pago completo. Los indicios de identidad contradictoria apoyan la escena autoral, pero no prueban quién llama: D07 debe revisar la clase y las marcas. Alias y nombres son ficticios. En r02, A atiende primero y B desarrolla las intervenciones del supuesto llamante; las letras no codifican identidad ni clase. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-V-FAMILIAR-003

vishing · familiar · directo · 20 líneas

**Situación:** Un supuesto familiar pide completar la seña de un salón para una reunión y propone pagar a un alias personal sin enviar el comprobante previo. Prueba solicitud económica dentro de un plan familiar compartido, sin claves ni códigos.

` 1` **A:** Hola, tía, soy Lucho. ¿Te acordás del cumpleaños de la abuela? ← `AUTHORITY_CLAIM`  
` 2` **B:** Sí, el domingo en el club.  
` 3` **A:** Seña del salón quedó corta y hoy vence el saldo.  
` 4` **B:** Yo había entendido que estaba todo pago.  
` 5` **A:** La prima que lo reservó hizo la transferencia inicial, pero el dueño pidió completar el resto.  
` 6` **B:** ¿Cuánto falta?  
` 7` **A:** Setenta y cinco mil. Si no entra hoy nos cambia el horario y perdemos el patio.  
` 8` **B:** ¿Quién tiene el contacto del salón?  
` 9` **A:** Lo tiene mi hermana, pero está en una reunión y no atiende.  
`10` **B:** ¿Por qué no espera a que salga?  
`11` **A:** El dueño dijo que tiene otra familia preguntando por la fecha.  
`12` **B:** ¿Vos hablaste con él?  
`13` **A:** Sí, me pasó los datos para pagar.  
`14` **B:** Mandame el comprobante de la seña.  
`15` **A:** No tengo el comprobante acá, pero si podés cubrir el saldo ahora te lo reenvío cuando llegue mi hermana. ← **T_R** · `REQUEST_TRANSFER`  
`16` **B:** ¿A qué cuenta va el saldo?  
`17` **A:** Te paso un alias personal del dueño, así lo ve rápido.  
`18` **B:** No voy a transferir sin confirmar la reserva con el salón.  
`19` **A:** Si esperamos, capaz nos quedamos sin lugar.  
`20` **B:** Mejor verifico antes de mandar plata.  

**Referencia de trabajo:** `T_R` 15, `T_C` —, pedido REQUEST_TRANSFER.

**Qué prueba:** Un supuesto familiar pide completar la seña de un salón para una reunión y propone pagar a un alias personal sin enviar el comprobante previo. Prueba solicitud económica dentro de un plan familiar compartido, sin claves ni códigos.

**Notas de la referencia:** Referencia de trabajo D07 y reserva D08; sin revisión humana. Propuesta provisional D07: el primer pedido indirecto está en línea 15, cuando A ofrece que B cubra el saldo a cambio de enviar el comprobante después. La pregunta de B en línea 16 no es el pedido; línea 17 identifica al destinatario. Sin cumplimiento.

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-V-FAMILIAR-004

vishing · familiar · indirecto · 29 líneas

**Situación:** Una voz que primero se presenta como hermana y luego como prima de Nico induce a enviarle dinero a una cuenta de una amiga por un supuesto remís.

` 1` **A:** Hola.  
` 2` **B:** Hola, soy Caro, la hermana de Nico. ¿Él está con vos?  
` 3` **A:** No, estoy en casa. ¿Por qué me preguntás?  
` 4` **B:** Me escribió desde un teléfono prestado, se quedó sin batería al salir del trabajo.  
` 5` **A:** Pero vos no sos la hermana, ¿sos la prima de la que me habló?  
` 6` **B:** Sí, prima, nos decimos hermanos desde chicos. Me expresé mal. ← _contexto_  
` 7` **A:** Ah, no tenía este número.  
` 8` **B:** Estoy usando el del local. Nico quedó complicado con el remís.  
` 9` **A:** ¿Qué le pasó?  
`10` **B:** Le salió nueve mil más de lo que llevaba y el chofer no lo quiere esperar.  
`11` **A:** ¿Por dónde está?  
`12` **B:** Cerca de la estación vieja, no me dio la esquina.  
`13` **A:** Le escribo al teléfono de él.  
`14` **B:** No te va a entrar, se apagó. A mí me dijo que no sabía cómo volver.  
`15` **A:** Si me pasás el teléfono prestado lo llamo yo.  
`16` **B:** El compañero ya se fue, no lo tiene más.  
`17` **A:** ¿Y vos cómo sabés que sigue ahí?  
`18` **B:** Fue hace un ratito. Estoy tratando de resolverlo antes de cerrar el local.  
`19` **A:** Pasame el número del remís, puedo hablar con el chofer.  
`20` **B:** Es un coche de la parada, no tiene central.  
`21` **A:** Entonces voy a buscar a Nico. Tardo quince minutos.  
`22` **B:** Si ahora apareciera esa diferencia en mi cuenta, podría arreglárselo yo y después él te devuelve. ← **T_R** · `REQUEST_TRANSFER`  
`23` **A:** ¿En tu cuenta? Pensé que estabas lejos.  
`24` **B:** Se la acerco cuando salga, o me arreglo con el chofer. Vos no te muevas.  
`25` **A:** ¿Qué nombre figura en tu cuenta?  
`26` **B:** No es mía, es de una amiga que me cubre los cobros del local.  
`27` **A:** Son demasiadas vueltas. Antes voy a confirmar con Nico.  
`28` **B:** Para cuando lo ubiques puede haber perdido el viaje. ← `URGENCY_PRESSURE`  
`29` **A:** Igual voy a llamarlo.  

**Referencia de trabajo:** `T_R` 22, `T_C` —, pedido REQUEST_TRANSFER.

**Qué prueba:** El pedido económico se formula como una condición deseada después de describir una necesidad. La confusión de parentesco y el cambio de destinatario surgen en el diálogo; la persona ofrece alternativas y no paga. Prueba inducción sin imperativo de transferencia ni códigos.

**Notas de la referencia:** Referencia de trabajo D07 y reserva D08; sin revisión humana. T_R tentativo en la condición sobre dinero en la cuenta; alternativa: el relato previo de la diferencia faltante podría interpretarse como inducción. No se resuelve D07 ni se marca un cumplimiento inexistente. La solicitud económica por sí sola no define suplantación; deben revisarse juntos los indicios de identidad y las evasivas. En r02, A atiende primero y B desarrolla las intervenciones del supuesto llamante; las letras no codifican identidad ni clase. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-V-FAMILIAR-005

vishing · familiar · indirecto · 21 líneas

**Situación:** Una voz acepta el nombre que le sugiere la interlocutora y, con el pretexto de un teléfono prestado y un viaje urgente, induce a comprarle un pasaje; la persona intenta verificar antes de pagar.

` 1` **A:** Buenas, soy el sobrino de Marta, ¿hablo con la tía Ana? ← `AUTHORITY_CLAIM`  
` 2` **B:** Sí, ¿quién sos?  
` 3` **A:** El que fue al asado el mes pasado, el hijo de Rubén.  
` 4` **B:** Ah, ¿Fede?  
` 5` **A:** Sí, me quedé sin teléfono y estoy llamando desde el de un compañero.  
` 6` **B:** ¿Qué pasó?  
` 7` **A:** Estoy en la terminal, tenía que viajar a casa y se me venció el pasaje.  
` 8` **B:** ¿Cómo se vence un pasaje?  
` 9` **A:** La empresa cambió el horario y me lo tomó como no presentado.  
`10` **B:** ¿No podés hablar con boletería?  
`11` **A:** Hay una fila larga y el micro sale en veinte minutos.  
`12` **B:** ¿Cuánto sale uno nuevo?  
`13` **A:** Unos cuarenta mil, pero lo puedo devolver cuando llegue.  
`14` **B:** ¿No tenés la tarjeta?  
`15` **A:** La billetera quedó en la mochila que está abajo del equipaje.  
`16` **B:** ¿No podés pedir ayuda al chofer?  
`17` **A:** Me dijo que no puede esperar mucho más.  
`18` **B:** Mandame una foto del pasaje viejo.  
`19` **A:** No puedo entrar al correo sin el teléfono.  
`20` **A:** Si alguien pudiera comprarlo por internet ahora, te lo devuelvo apenas llegue a casa. ← **T_R** · `REQUEST_TRANSFER`  
`21` **B:** No voy a pagar sin hablar con Rubén primero.  

**Referencia de trabajo:** `T_R` 20, `T_C` —, pedido REQUEST_TRANSFER.

**Qué prueba:** Un problema de viaje se construye con teléfono prestado, pasaje vencido y salida inminente. El pedido de pagar el pasaje aparece como propuesta de compra por internet y devolución posterior, y la interlocutora corta para verificar. Prueba un pedido económico indirecto sin cumplimiento.

**Notas de la referencia:** Referencia de trabajo D07 y reserva D08; sin revisión humana. Propuesta provisional D07: T_R en línea 20, primera instrucción de que otra persona compre el pasaje; la urgencia y el costo se describen antes, en líneas 11–13. No hay cumplimiento. La identidad familiar no se prueba por el texto. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-V-FAMILIAR-006

vishing · familiar · indirecto · 23 líneas

**Situación:** Una supuesta prima describe una urgencia veterinaria e induce a cubrir una seña; la interlocutora detiene el pago para verificar, sin cumplimiento.

` 1` **A:** ¿Hola?  
` 2` **B:** Hola, soy tu prima Vane. ¿Estás en el centro? ← `AUTHORITY_CLAIM`  
` 3` **A:** Sí, salgo en un rato.  
` 4` **B:** Estoy con el perro en la veterinaria, lo atendieron por una alergia.  
` 5` **A:** ¿Está bien?  
` 6` **B:** Sí, ya respira mejor, pero me piden dejar una seña antes de darle el medicamento.  
` 7` **A:** ¿Cuánto cuesta?  
` 8` **B:** El tratamiento completo es caro, estoy preguntando si puedo pagar en dos veces.  
` 9` **A:** ¿No te toma la tarjeta?  
`10` **B:** La terminal no tiene señal, dicen que se cayó el sistema.  
`11` **A:** ¿Y efectivo?  
`12` **B:** Tengo algo, pero no me alcanza para cubrir la primera parte.  
`13` **A:** ¿Estás con alguien?  
`14` **B:** Vine sola y no quiero dejar al perro acá mientras voy a un cajero.  
`15` **A:** ¿Cuál es la veterinaria?  
`16` **B:** La de la avenida, al lado de la farmacia nueva.  
`17` **A:** Hay tres por ahí, decime el nombre.  
`18` **B:** No me acuerdo cómo se llama, vine porque me la recomendó una vecina.  
`19` **A:** ¿Podés mandarme una foto del recibo?  
`20` **B:** Todavía no me dieron nada, están esperando que confirme el tratamiento.  
`21` **A:** Llamo a tu mamá para ver si sabe dónde estás.  
`22` **B:** Si podés cubrir la seña ahora, te la devuelvo cuando salga de la veterinaria. ← **T_R** · `REQUEST_TRANSFER`  
`23` **A:** No transfiero hasta confirmar con tu mamá dónde están.  

**Referencia de trabajo:** `T_R` 22, `T_C` —, pedido REQUEST_TRANSFER.

**Qué prueba:** La prima describe una urgencia veterinaria y falta de dinero, buscando que la persona ofrezca ayuda. Solo al final pide cubrir la seña, que sería devuelta después; la interlocutora detiene el pago para verificar. Prueba una solicitud económica inducida y diferida.

**Notas de la referencia:** Referencia de trabajo D07 y reserva D08; sin revisión humana. Propuesta provisional D07: la necesidad económica se comunica en líneas 6–14; T_R se marca en línea 22, primera solicitud de cubrir la seña. No hay cumplimiento. Revisar si la situación previa basta para anticipar el pedido; la identidad no es verificable solo por el diálogo. En r02, A atiende primero y B desarrolla las intervenciones del supuesto llamante; las letras no codifican identidad ni clase. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-V-ORGANISMO_PREVISIONAL-001

vishing · organismo_previsional · directo · **en la matriz #101** · **propuesto para grabar** · 27 líneas

**Situación:** Un falso actualizador aprovecha un cambio de domicilio para obtener documento y fotos y luego intenta que se acepte un representante de cobro desconocido.

` 1` **A:** Buenas, ¿quién habla?  
` 2` **B:** Buen día, del sector de actualización de beneficiarios. Busco a quien gestiona la pensión de su mamá.  
` 3` **A:** Soy la hija. Ella hizo el cambio de domicilio hace poco.  
` 4` **B:** Sí, por eso llamamos. El sistema dejó pendiente el domicilio y el representante.  
` 5` **A:** El representante no cambió, sigue siendo mi hermano.  
` 6` **B:** En la migración se mezclan esos campos, lo corregimos en la misma ficha.  
` 7` **A:** ¿Tiene el número de expediente? Lo tengo acá.  
` 8` **B:** Ahora no lo visualizo. Para buscarlo necesito identificar a la titular.  
` 9` **A:** ¿El cambio que hizo en la oficina no aparece?  
`10` **B:** Aparece abierto, pero no se puede cerrar sin la ficha que le voy a enviar.  
`11` **A:** ¿Me la manda al correo registrado?  
`12` **B:** Le pido el DNI completo y la fecha de nacimiento de su mamá para cargarla, y una foto de frente y dorso en el formulario que le llega por mensaje. ← **T_R** · `REQUEST_PERSONAL_DATA`  
`13` **A:** Anote 39.714.286, primero de enero de 1970. Me llegó un mensaje de Gestión Integral, ¿es ese?  
`14` **B:** Ese mismo. Abra la ficha de actualización de domicilio.  
`15` **A:** La abrí, arriba dice alta de representante para cobro. No dice domicilio. ← _contexto_  
`16` **B:** Es el título general. Lo que ponemos abajo es la dirección nueva.  
`17` **A:** Pero el representante sigue siendo mi hermano.  
`18` **B:** Eso se copia al final. Primero cargue las fotos del documento que tiene a mano.  
`19` **A:** Estoy usando las fotos que ella me dejó para el trámite. Ya envié las dos. ← **T_C** · _cumplimiento_  
`20` **B:** Perfecto, ahora continúe con aceptar el representante indicado.  
`21` **A:** Me figura otro nombre, no es el de mi hermano.  
`22` **B:** Es quien valida administrativamente, no quien va a cobrar.  
`23` **A:** No voy a aceptar eso. Le voy a mostrar esta ficha a mi mamá.  
`24` **B:** Si queda sin terminar, se vuelve a abrir el plazo del cambio. ← `URGENCY_PRESSURE`  
`25` **A:** Los datos ya se los pasé, pero la autorización no la doy.  
`26` **B:** La dejo pendiente, entonces.  
`27` **A:** Sí, voy a consultar en la oficina donde inició todo.  

**Referencia de trabajo:** `T_R` 12, `T_C` 19, pedido REQUEST_PERSONAL_DATA.

**Qué prueba:** Una gestión de domicilio deriva en capturar identificación y fotos mediante una ficha de apoderado ajeno. Hay entrega de los datos solicitados y luego rechazo de otra autorización: ese rechazo posterior no borra el primer cumplimiento. Pedir DNI por teléfono no se usa como criterio suficiente de fraude.

**Notas de la referencia:** Referencia de trabajo D07 y reserva D08; sin revisión humana. T_R tentativo en la solicitud conjunta de identificación y fotos. T_C se ubica al confirmar el envío de ambas fotos, completando lo solicitado; el DNI y fecha se dictan antes. La autorización posterior se rechaza y no se anota como cumplida. D07 debe revisar el pedido compuesto y si corresponde distinguir cumplimiento parcial previo. No describe un trámite previsional real. En r02, A atiende primero y B desarrolla las intervenciones del supuesto llamante; las letras no codifican identidad ni clase. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-V-ORGANISMO_PREVISIONAL-002

vishing · organismo_previsional · directo · con errores escritos de ASR · 21 líneas

**Situación:** Una supuesta revisión de aportes pide CUIL y fecha de nacimiento para un ajuste del recibo; la persona dicta los datos y el llamante los acepta.

` 1` **A:** Hola soy del equipo de liquidaciones previsionales Te llamo por el recibo de septiembre ← `AUTHORITY_CLAIM`  
` 2` **B:** Qué tiene el recibo  
` 3` **A:** Aparece un ajuste por movilidad que no se aplicó a todos los casos  
` 4` **B:** Me corresponde un ajuste  
` 5` **A:** El sistema marca que podría haber una diferencia a favor pero primero hay que identificar el legajo  
` 6` **B:** No está asociado a mi número de benefisio  
` 7` **A:** Sí pero necesito cruzarlo con la identidad de quien cobra  
` 8` **B:** Qué información te falta  
` 9` **A:** El número completo de CUIL y tu fecha exacta de nacimiento ← **T_R** · `REQUEST_PERSONAL_DATA`  
`10` **B:** Lo tengo anotado 00-20573300-0 fecha 01/01/1970 ← **T_C** · _cumplimiento_  
`11` **A:** Ya quedó abierto el registro provisorio  
`12` **B:** Cuál sería la diferencia  
`13` **A:** Todavía no la puedo ver hasta que se actualice el recibo  
`14` **B:** Cuándo aparece  
`15` **A:** En el próximo cierre mensual  
`16` **B:** Me mandan una constancia  
`17` **A:** Te debería aparecer dentro del portal  
`18` **B:** Bueno reviso ahí más tarde  
`19` **A:** De acuerdo  
`20` **B:** Chau  
`21` **A:** Hasta luego  

**Referencia de trabajo:** `T_R` 9, `T_C` 10, pedido REQUEST_PERSONAL_DATA.

**Qué prueba:** Un supuesto ajuste previsional solicita el CUIL completo y la fecha de nacimiento para identificar el legajo. La persona dicta valores ficticios y la llamada los da por recibidos. Prueba cumplimiento de datos identificatorios bajo una promesa de diferencia en el recibo.

**Notas de la referencia:** Referencia de trabajo D07 y reserva D08; sin revisión humana. T_R línea 9, pedido de CUIL y fecha. T_C línea 10, entrega de ambos datos ficticios. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-V-ORGANISMO_PREVISIONAL-003

vishing · organismo_previsional · indirecto · 20 líneas

**Situación:** El llamante revela parte de un identificador y pide completar los dígitos faltantes para abrir una historia laboral. Prueba una solicitud inducida de dato personal donde el interlocutor solicita confirmar lo que ya “sabe”.

` 1` **A:** Te llamamos del centro de orientación previsional por la consulta que dejaste sobre aportes. ← `AUTHORITY_CLAIM`  
` 2` **B:** Yo pregunté por unos años que no me aparecen.  
` 3` **A:** Sí, figura una diferencia entre los períodos declarados y los del registro.  
` 4` **B:** ¿Eso se puede revisar?  
` 5` **A:** Hay que vincular el formulario con la historia laboral para ver dónde falta información.  
` 6` **B:** ¿Tengo que sacar un turno?  
` 7` **A:** Si completamos la identificación telefónica, quizá no haga falta que vuelvas a presentar todo.  
` 8` **B:** ¿Qué dato tengo que confirmar?  
` 9` **A:** En la ficha aparece un número de documento que termina en 6.  
`10` **B:** ¿De quién es?  
`11` **A:** Del titular de la consulta. Para que el sistema abra el detalle, me faltan los dígitos del medio. ← **T_R** · `REQUEST_PERSONAL_DATA`  
`12` **B:** ¿Querés que te diga el DNI entero?  
`13` **A:** Solo completá lo que falta y verifico que la historia laboral corresponda.  
`14` **B:** No sé quién dejó la consulta, la hice con mi pareja.  
`15` **A:** Si el documento empieza con 28, puede ser el tuyo.  
`16` **B:** Prefiero entrar al portal y mirar el turno.  
`17` **A:** El portal no muestra el detalle hasta que se valide el formulario.  
`18` **B:** ¿Podés decirme el número del trámite?  
`19` **A:** No aparece en esta pantalla, está en otra área.  
`20` **B:** Entonces no te doy el resto del documento.  

**Referencia de trabajo:** `T_R` 11, `T_C` —, pedido REQUEST_PERSONAL_DATA.

**Qué prueba:** El llamante revela parte de un identificador y pide completar los dígitos faltantes para abrir una historia laboral. Prueba una solicitud inducida de dato personal donde el interlocutor solicita confirmar lo que ya “sabe”.

**Notas de la referencia:** Referencia de trabajo D07 y reserva D08; sin revisión humana. Propuesta T_R línea 11, cuando se piden los dígitos faltantes; también podría ubicarse línea 13, al reformularlo como completar el dato. Pendiente D07. No se aporta ningún número real ni hay cumplimiento. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-V-ORGANISMO_PREVISIONAL-004

vishing · organismo_previsional · indirecto · con errores escritos de ASR · 21 líneas

**Situación:** La llamada transforma los últimos dígitos de una referencia impresa y una fecha de emisión en una llave para abrir una liquidación. Prueba un pedido indirecto de datos identificatorios presentado como referencia administrativa.

` 1` **A:** hola buen día  
` 2` **B:** Buenas te contacto de la oficina de regularización de pensiones por una devolución de aportes ← `AUTHORITY_CLAIM`  
` 3` **A:** No sabía que había una devolución  
` 4` **B:** Es una revisión de períodos viejos no se acredita automáticamente  
` 5` **A:** De qué período hablan  
` 6` **B:** Entre el primer trabajo y el alta de la prestación  
` 7` **A:** Eso fue hace muchos años  
` 8` **B:** Por eso pedimos reconstruir el legajo Tenés una copia del documento a mano  
` 9` **A:** Sí pero no quiero mandar una foto por mensaje  
`10` **B:** No hace falta foto Podés mirar el reverso donde está impreso el número de trámite  
`11` **A:** Ese número sirve pa la devolución  
`12` **B:** Identifica al titular y habilita a consultar la liquidación provisoria  
`13` **A:** El número es largo no lo leo bien  
`14` **B:** Decime los últimos cuatro y la fecha de emisión que figura abajo ← **T_R** · `REQUEST_PERSONAL_DATA`  
`15` **A:** No es un dato personal  
`16` **B:** Es una referencia administrativa no un código de acceso  
`17` **A:** Si es una devolución no debería recibir una carta  
`18` **B:** La carta se genera cuando el titular confirma la liquidación  
`19` **A:** No quiero confirmar algo que no vi  
`20` **B:** La cifra se puede leer una vez que se abre el legajo  
`21` **A:** Entonces prefiero pedir turno y revisarlo en persona  

**Referencia de trabajo:** `T_R` 14, `T_C` —, pedido REQUEST_PERSONAL_DATA.

**Qué prueba:** La llamada transforma los últimos dígitos de una referencia impresa y una fecha de emisión en una llave para abrir una liquidación. Prueba un pedido indirecto de datos identificatorios presentado como referencia administrativa.

**Notas de la referencia:** Referencia de trabajo D07 y reserva D08; sin revisión humana. Propuesta T_R en línea 14, al pedir dígitos y fecha; también podría ubicarse línea 16, cuando se justifica su función para abrir el legajo. D07 pendiente. No se dicta ningún dato. En r02, A atiende primero y B desarrolla las intervenciones del supuesto llamante; las letras no codifican identidad ni clase. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-V-ORGANISMO_PREVISIONAL-005

vishing · organismo_previsional · sin_pedido · 23 líneas

**Situación:** Una supuesta revisión del pago introduce dudas sobre la continuidad de la prestación y evita identificar oficina; la persona corta sin recibir pedido crítico.

` 1` **A:** Buenas, ¿quién habla?  
` 2` **B:** Buenas, te llamo de control de prestaciones. Hay una revisión sobre el pago que entró este mes. ← `AUTHORITY_CLAIM`  
` 3` **A:** ¿Qué problema tiene?  
` 4` **B:** No figura como rechazado, pero quedó marcado para una verificación adicional.  
` 5` **A:** ¿A mí me falta hacer algo?  
` 6` **B:** Todavía no, primero tenemos que ver si el expediente coincide con la oficina que lo procesa.  
` 7` **A:** Yo tengo el comprobante del depósito.  
` 8` **B:** Guardalo y no lo reenvíes a nadie hasta que cerremos la revisión.  
` 9` **A:** ¿Por qué no lo puedo consultar en el portal? ← `ISOLATION_SECRECY`  
`10` **B:** La pantalla está actualizando los pagos; durante ese rato puede mostrar datos viejos.  
`11` **A:** ¿Me van a suspender el beneficio?  
`12` **B:** No puedo asegurarte nada hasta que termine el control.  
`13` **A:** ¿Cuándo termina?  
`14` **B:** El lote se cierra al mediodía.  
`15` **A:** ¿Cuál es el número de expediente que están revisando?  
`16` **B:** Estoy esperando que cargue la ficha.  
`17` **A:** ¿Me das el nombre del organismo?  
`18` **B:** Es la oficina de prestaciones, la línea sale centralizada.  
`19` **A:** No me dijiste de qué sede llamás. ← `URGENCY_PRESSURE`, `ISOLATION_SECRECY`  
`20` **B:** No cortes, así no se pierde el turno de revisión.  
`21` **A:** Voy a llamar yo al número de atención que ya tengo.  
`22` **B:** Esperá un momento, todavía no terminé de consultar.  
`23` **A:** No, corto y verifico.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** La posibilidad de una suspensión se sugiere sin confirmarla y se evita identificar sede o expediente. El beneficiario corta antes de recibir un pedido crítico; prueba separar presión administrativa, intención autoral y evidencia observable.

**Notas de la referencia:** Referencia de trabajo D07 y reserva D08; sin revisión humana. No se observa solicitud de acción crítica ni cumplimiento: T_R y T_C permanecen nulos. La alerta, la autoridad alegada y la presión hacen sospechosa la situación, pero la identidad e intención fraudulenta no son demostrables solo con la transcripción. La etiqueta de clase es una hipótesis de escenario para revisión humana en D07, no un acierto exigible frente a evidencia invisible. En r02, A atiende primero y B desarrolla las intervenciones del supuesto llamante; las letras no codifican identidad ni clase. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-V-ORGANISMO_PREVISIONAL-006

vishing · organismo_previsional · sin_pedido · 22 líneas

**Situación:** Una mesa que alega regularizar el calendario previsional desalienta otros reclamos y termina sin solicitar datos ni autorización.

` 1` **A:** Te llamo de la mesa de regularización por un cambio en el calendario de pagos previsionales. ← `AUTHORITY_CLAIM`  
` 2` **B:** ¿Cambió la fecha de cobro?  
` 3` **A:** Para algunos legajos aparece una marca que puede demorar la próxima liquidación.  
` 4` **B:** ¿A cuál se refiere?  
` 5` **A:** La ficha está en revisión y no muestra todos los datos desde esta línea.  
` 6` **B:** ¿Cómo sé que corresponde a mi trámite?  
` 7` **A:** Se identifica por el apellido, pero no conviene decirlo hasta que el sistema termine de abrir.  
` 8` **B:** ¿Podés decirme qué oficina está llamando?  
` 9` **A:** La revisión se hace desde una mesa central.  
`10` **B:** ¿Hay algún aviso en mi portal?  
`11` **A:** Todavía no, primero se confirma por teléfono para no duplicar reclamos. ← `THREAT_FEAR`  
`12` **B:** Eso no me deja tranquilo.  
`13` **A:** Si abrís una consulta nueva, se puede pisar la revisión que ya está en curso.  
`14` **B:** ¿Entonces no debería llamar al organismo?  
`15` **A:** Esperá a que te explique el procedimiento completo.  
`16` **B:** No me dijiste cuál es el número de expediente.  
`17` **A:** Estoy intentando recuperar la ficha.  
`18` **B:** Voy a cortar y entrar al portal desde la computadora. ← `URGENCY_PRESSURE`, `ISOLATION_SECRECY`  
`19` **A:** No cierres esta llamada, la marca se puede vencer.  
`20` **B:** No, voy a verificarlo por mi cuenta.  
`21` **A:** Dame un minuto más.  
`22` **B:** Hasta luego.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** Una supuesta revisión del calendario desalienta abrir un reclamo independiente, pero no llega a solicitar datos ni autorización. Prueba el límite de inferencia en una conversación interrumpida antes de la maniobra crítica.

**Notas de la referencia:** Referencia de trabajo D07 y reserva D08; sin revisión humana. No se observa solicitud de acción crítica ni cumplimiento: T_R y T_C permanecen nulos. La alerta, la autoridad alegada y la presión hacen sospechosa la situación, pero la identidad e intención fraudulenta no son demostrables solo con la transcripción. La etiqueta de clase es una hipótesis de escenario para revisión humana en D07, no un acierto exigible frente a evidencia invisible. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-V-PREMIO-001

vishing · premio · directo · 21 líneas

**Situación:** Un premio de una feria barrial deriva en pedir el DNI y una foto del documento para un acta, con vencimiento cercano. Prueba un pedido directo de datos personales sostenido por un sorteo que la persona recuerda vagamente.

` 1` **A:** Hola, decime.  
` 2` **B:** Hola, te llamo de la organización del sorteo de la Expo del Río. ¿Participaste con una compra en los puestos? ← `AUTHORITY_CLAIM`  
` 3` **A:** Sí, llené un cupón en el stand de plantas.  
` 4` **B:** Saliste seleccionado para una bicicleta urbana, felicitaciones.  
` 5` **A:** ¿En serio? No me acuerdo del sorteo.  
` 6` **B:** Fue durante el cierre del domingo. El premio está reservado a tu nombre.  
` 7` **A:** ¿Y cómo lo retiro?  
` 8` **B:** Primero tenemos que registrar quién lo recibe porque la factura sale nominada.  
` 9` **A:** ¿Qué dato necesitan?  
`10` **B:** El DNI completo y una foto del frente para cargarlo en el acta. ← **T_R** · `REQUEST_PERSONAL_DATA`  
`11` **A:** ¿Por qué necesitan una foto?  
`12` **B:** Para comprobar que el nombre coincida con la lista de ganadores.  
`13` **A:** El documento dice 00.000.000, ya cargué la imagen en el formulario. ← **T_C** · _cumplimiento_  
`14` **B:** Perfecto, te quedó el registro terminado.  
`15` **A:** ¿Puedo acercarme a la Expo?  
`16` **B:** El predio ya cerró, la entrega se hace desde administración.  
`17` **A:** ¿Dónde queda?  
`18` **B:** Estamos en un depósito por la ruta, pero podemos coordinar después.  
`19` **A:** ¿Y cuándo me entregan la bicicleta?  
`20` **B:** Te llamamos mañana para acordar el horario.  
`21` **A:** Está bien, espero la llamada.  

**Referencia de trabajo:** `T_R` 10, `T_C` 13, pedido REQUEST_PERSONAL_DATA.

**Qué prueba:** Un premio de feria da pie a pedir un DNI y cargar una imagen del documento en un formulario. La persona aporta datos de marcador ficticios y confirma la carga. Prueba cumplimiento de una solicitud de datos personales por una recompensa.

**Notas de la referencia:** Referencia de trabajo D07 y reserva D08; sin revisión humana. T_R línea 10, solicitud de documento e imagen. T_C línea 13, la persona afirma que cargó ambos en el formulario. Los datos usados son marcadores artificiales, no identifican a una persona real. En r02, A atiende primero y B desarrolla las intervenciones del supuesto llamante; las letras no codifican identidad ni clase. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-V-PREMIO-002

vishing · premio · directo · con errores escritos de ASR · 20 líneas

**Situación:** Un supuesto premio radial requiere pagar una activación a una cuenta presentada como de producción; la persona confirma la transferencia.

` 1` **A:** Buenas soy de producción de Radio Horizonte Hablás con Abril ← `AUTHORITY_CLAIM`  
` 2` **B:** Sí quién llama  
` 3` **A:** Te ganaste un parlante portátil en la trivia del mediodía  
` 4` **B:** Yo mandé una respuesta por mensaje pero no pensé que hubiera premio  
` 5` **A:** Tu respuesta salió sorteada entre quienes participaron  
` 6` **B:** Cómo me lo entregan  
` 7` **A:** El envío sale hoy a la direcsión que cargaste en la web  
` 8` **B:** Qué empresa lo trae  
` 9` **A:** Mensajería propia de la radio  
`10` **B:** Tengo que pagar algo  
`11` **A:** El envío está bonificado pero falta el cargo de activación del premio  
`12` **B:** De cuánto es  
`13` **A:** Dos mil setecientos se abona por transferencia a la cuenta de producción ← **T_R** · `REQUEST_TRANSFER`  
`14` **B:** Me mandás una factura  
`15` **A:** Sí después de confirmar el pago queda el comprobante de entrega  
`16` **B:** Ya hice la transferencia por ese importe ← **T_C** · _cumplimiento_  
`17` **A:** Listo te va a llegar la confirmación del envío  
`18` **B:** Hoy lo despachan  
`19` **A:** Sí está previsto para la tarde  
`20` **B:** Bueno quedo atenta al mensaje  

**Referencia de trabajo:** `T_R` 13, `T_C` 16, pedido REQUEST_TRANSFER.

**Qué prueba:** La llamada por un premio radial pide una transferencia de activación antes de entregar el artículo. La persona realiza el pago ficticio y el supuesto productor confirma el envío. Prueba cumplimiento de movimiento de dinero tras un premio.

**Notas de la referencia:** Referencia de trabajo D07 y reserva D08; sin revisión humana. T_R línea 13, solicitud de transferencia. T_C línea 16, confirmación explícita de haber transferido. Montos y cuenta son inventados y no se incluye CBU/alias real. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-V-PREMIO-003

vishing · premio · indirecto · **propuesto para grabar** · 28 líneas

**Situación:** Una supuesta coordinación de concurso fotográfico altera las condiciones de retiro e induce a completar documento y foto en una ficha de distribución de remitente desconocido.

` 1` **A:** Hola, soy de la coordinación de la campaña de fotos de bibliotecas. ← `AUTHORITY_CLAIM`  
` 2` **B:** ¿La de la feria del barrio? Compartí una imagen la semana pasada.  
` 3` **A:** Esa misma. El jurado eligió tu foto para un kit de libros.  
` 4` **B:** Qué lindo. ¿Ya publicaron el resultado?  
` 5` **A:** Lo publican mañana. Hoy estamos preparando los paquetes.  
` 6` **B:** En las bases decía que se retiraban en la feria, no que los enviaban. ← _contexto_  
` 7` **A:** Para quienes quedaron lejos habilitaron una entrega especial.  
` 8` **B:** Yo vivo cerca. Puedo ir cuando hagan la premiación.  
` 9` **A:** Igual cada paquete tiene que salir asociado con una persona.  
`10` **B:** En el formulario puse el correo y mi nombre. ¿Con eso no alcanza?  
`11` **A:** El correo quedó, pero el campo del responsable del envío está vacío. ← _contexto_  
`12` **B:** ¿Qué parte de ese campo?  
`13` **A:** El número de documento. Si queda vacío, el kit vuelve al listado de suplentes. ← **T_R** · `REQUEST_PERSONAL_DATA`  
`14` **B:** ¿Lo completaron así todas las personas? No lo vi en las bases.  
`15` **A:** Es un requisito de la distribución que no había entrado en el anuncio.  
`16` **B:** Me estás diciendo que si voy a buscarlo también tengo que completarlo.  
`17` **A:** Sí. Te mandé una ficha nueva para vincular el paquete antes del cierre.  
`18` **B:** ¿Te paso el documento por acá o en esa ficha?  
`19` **A:** Anotá el número en esa ficha y agregá la foto del frente para que no lo carguen mal. ← `REQUEST_PERSONAL_DATA`  
`20` **B:** El remitente del mensaje no es el de la campaña. ← _contexto_  
`21` **A:** Es un servicio de logística que se sumó esta mañana.  
`22` **B:** ¿Puedo consultar primero con la biblioteca donde dejé la foto?  
`23` **A:** Si esperamos esa respuesta se termina el reparto de hoy. ← `URGENCY_PRESSURE`  
`24` **B:** El premio no se anunció todavía, no entiendo por qué corre tanto apuro.  
`25` **A:** Quiero reservarte el kit, pero necesito que quede asociado antes de las seis.  
`26` **B:** Voy a esperar la publicación y acercarme a la feria.  
`27` **A:** No te puedo asegurar que sigan guardándolo.  
`28` **B:** Está bien, prefiero confirmar las condiciones con la organización. ← _rechazo_  

**Referencia de trabajo:** `T_R` 13, `T_C` —, pedido REQUEST_PERSONAL_DATA.

**Qué prueba:** Pedido indirecto de documento presentado primero como campo faltante y luego como condición para no perder un premio. La conversación contrapone las bases que recuerda la participante, el remitente del formulario y una solicitud posterior explícita de foto; no se toma la mera palabra premio como fraude.

**Notas de la referencia:** Referencia de trabajo D07 y reserva D08; sin revisión humana. T_R tentativo en la línea donde se indica qué dato falta y se condiciona la entrega a completarlo; alternativa en la instrucción posterior de escribir el número y adjuntar foto. Se conserva esa duda en D07: una descripción de requisito puede funcionar como pedido indirecto, pero no se adjudica la regla. No hubo entrega de datos ni cumplimiento. La clase se refiere al episodio ficticio; pedir DNI por sí solo no define fraude. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-V-PREMIO-004

vishing · premio · indirecto · **en la matriz #101** · **propuesto para grabar** · 21 líneas

**Situación:** El supuesto canje de un vale requiere que el titular de una tarjeta adicional confirme los tres números de seguridad. Prueba un pedido de secreto financiero inducido por un beneficio y aclarado solo tras la pregunta sobre los datos.

` 1` **A:** Buenas tardes.  
` 2` **B:** Buen día, te contacto por una promoción de Mercado del Parque que se hizo en septiembre. ← `AUTHORITY_CLAIM`  
` 3` **A:** ¿Cuál promoción?  
` 4` **B:** La de compras con tarjeta; tu ticket quedó seleccionado para un vale de supermercado.  
` 5` **A:** ¿De cuánto es?  
` 6` **B:** Cuarenta mil pesos, para usar en una compra.  
` 7` **A:** ¿Lo puedo retirar en el local?  
` 8` **B:** Sí, pero la caja necesita validar que el beneficio quede asociado al titular de la compra.  
` 9` **A:** Yo pagué con una tarjeta adicional.  
`10` **B:** Entonces el titular tiene que autorizar el canje desde su banco.  
`11` **A:** ¿Qué tiene que hacer?  
`12` **B:** Le mandamos un aviso de operación y tiene que confirmar los datos de la tarjeta para habilitar el cupón.  
`13` **A:** ¿Los datos completos?  
`14` **B:** El nombre, la fecha de vencimiento y los tres números de seguridad que están atrás. ← **T_R** · `REQUEST_SECRET`  
`15` **A:** Eso es el código de seguridad.  
`16` **B:** Es la validación del titular, no se almacena.  
`17` **A:** No voy a pedirle que comparta esos números por una promoción.  
`18` **B:** Si no se valida hoy, el vale se libera para el siguiente ticket.  
`19` **A:** Que se libere entonces.  
`20` **B:** ¿No querés aprovecharlo?  
`21` **A:** No si implica dar datos de la tarjeta.  

**Referencia de trabajo:** `T_R` 14, `T_C` —, pedido REQUEST_SECRET.

**Qué prueba:** El supuesto canje de un vale requiere que el titular de una tarjeta adicional confirme los tres números de seguridad. Prueba un pedido de secreto financiero inducido por un beneficio y aclarado solo tras la pregunta sobre los datos.

**Notas de la referencia:** Referencia de trabajo D07 y reserva D08; sin revisión humana. Propuesta provisional D07: línea 12 anuncia una autorización del titular, pero el pedido de información sensible se vuelve concreto en línea 14, al enumerar vencimiento y código de seguridad. T_R queda en esa primera solicitud explícita; sin cumplimiento. En r02, A atiende primero y B desarrolla las intervenciones del supuesto llamante; las letras no codifican identidad ni clase. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-V-PREMIO-005

vishing · premio · sin_pedido · con errores escritos de ASR · 23 líneas

**Situación:** Una supuesta selección del Festival del Patio presiona para reservar antes de una publicación pública; la persona decide esperar y la llamada termina sin pedido crítico.

` 1` **A:** hola buen día  
` 2` **B:** Hola te llamo de la organización del Festival del Patio por una consulta sobre el sorteo de entradas ← `AUTHORITY_CLAIM`  
` 3` **A:** Qué consulta  
` 4` **B:** Tu número quedó asociado a una selección preliminar pa el pase doble  
` 5` **A:** Yo participé  
` 6` **B:** Sí en la encuesta que se hizo durante la transmisión  
` 7` **A:** No me acuerdo de haber completado nada  
` 8` **B:** La lista final se publica esta tarde antes hay que dejar cerradas las reservas  
` 9` **A:** Cómo sé si soy una de las personas elegidas  
`10` **B:** No podemos informar nombres hasta que cierre el registro  
`11` **A:** Quién organiza el sorteo  
`12` **B:** El equipo de producción del festival ← `ISOLATION_SECRECY`  
`13` **A:** Hay un sitio con las condiciones  
`14` **B:** Está por actualizarse no te conviene entrar todavía porque muestra la lista anterior  
`15` **A:** Y si espero a la publicación  
`16` **B:** El pase puede liberarse si no contestamos a tiempo ← `URGENCY_PRESSURE`  
`17` **A:** Cuánto tiempo tengo  
`18` **B:** Hasta las cinco después se cierra la asignación  
`19` **A:** No voy a seguir instrucciones sin ver las condiciones  
`20` **B:** Dame un minuto que busco el enlace actualizado  
`21` **A:** Voy a consultar las redes oficiales del festival  
`22` **B:** Esperá todavía no cortes  
`23` **A:** No prefiero revisar por mi cuenta  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** La supuesta selección de entradas del Festival del Patio exige responder a tiempo y desalienta consultar condiciones públicas, sin concretar un pedido de datos o dinero. Prueba no confundir una reserva sugerida con un pedido crítico ya ocurrido.

**Notas de la referencia:** Referencia de trabajo D07 y reserva D08; sin revisión humana. No se observa solicitud de acción crítica ni cumplimiento: T_R y T_C permanecen nulos. La alerta, la autoridad alegada y la presión hacen sospechosa la situación, pero la identidad e intención fraudulenta no son demostrables solo con la transcripción. La etiqueta de clase es una hipótesis de escenario para revisión humana en D07, no un acierto exigible frente a evidencia invisible. En r02, A atiende primero y B desarrolla las intervenciones del supuesto llamante; las letras no codifican identidad ni clase. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-V-PREMIO-006

vishing · premio · sin_pedido · 22 líneas

**Situación:** Una supuesta entrega de un premio de la Expo del Valle posterga términos y canales de verificación; la persona espera información pública y no llega a recibir una solicitud crítica.

` 1` **A:** Buen día, te contacto del equipo de beneficios de la Expo del Valle. Tu cupón quedó seleccionado. ← `AUTHORITY_CLAIM`  
` 2` **B:** ¿Para qué premio?  
` 3` **A:** Un equipo de cocina que se sorteó entre las personas que visitaron los stands.  
` 4` **B:** Yo fui el domingo, pero no recuerdo haber dejado datos.  
` 5` **A:** La selección se hace con las entradas escaneadas, por eso figura tu teléfono.  
` 6` **B:** ¿Dónde publicaron el resultado?  
` 7` **A:** La publicación sale cuando se confirma la entrega.  
` 8` **B:** ¿Quién hace la entrega?  
` 9` **A:** La empresa de logística que trabaja con la Expo.  
`10` **B:** ¿Me pueden llamar ellos?  
`11` **A:** No, primero cerramos la reserva desde producción.  
`12` **B:** ¿Tengo que pagar algo?  
`13` **A:** Todavía no llegamos a esa parte, primero tengo que revisar el formulario de aceptación. ← `PERSISTENCE_DISTRACTION`  
`14` **B:** ¿Qué pide el formulario?  
`15` **A:** No lo tengo abierto en esta línea, estoy esperando que sincronice.  
`16` **B:** ¿Me mandás un correo con los términos?  
`17` **A:** La plataforma de correo está con demora, lo más rápido es dejar la reserva ahora.  
`18` **B:** ¿A qué número puedo llamar a la Expo? ← `URGENCY_PRESSURE`  
`19` **A:** La central está cerrada por montaje.  
`20` **B:** Entonces lo reviso cuando publiquen la lista.  
`21` **A:** Puede que el premio ya no esté disponible.  
`22` **B:** Está bien, espero a tener información pública.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** La entrega de un electrodoméstico se promete sin términos verificables. Incluso ante una pregunta sobre pagar, el llamante posterga el procedimiento y la llamada termina sin solicitud; prueba no atribuirle al llamante la pregunta de quien atiende.

**Notas de la referencia:** Referencia de trabajo D07 y reserva D08; sin revisión humana. No se observa solicitud de acción crítica ni cumplimiento: T_R y T_C permanecen nulos. La alerta, la autoridad alegada y la presión hacen sospechosa la situación, pero la identidad e intención fraudulenta no son demostrables solo con la transcripción. La etiqueta de clase es una hipótesis de escenario para revisión humana en D07, no un acierto exigible frente a evidencia invisible. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-V-SOPORTE-001

vishing · soporte · directo · **propuesto para grabar** · 21 líneas

**Situación:** Un problema realista de descarga se usa para pedir la contraseña en un panel guiado. El llamante afirma que no la verá, pero no puede identificar un ticket. Prueba una solicitud explícita de credencial permanente dentro de una explicación técnica gradual.

` 1` **A:** Hola.  
` 2` **B:** Buenas, soy Daniela del servicio de ayuda de Nube Taller. ¿Te puedo hacer unas preguntas sobre el acceso? ← `AUTHORITY_CLAIM`  
` 3` **A:** Sí, no me deja descargar las facturas.  
` 4` **B:** ¿Te aparece un cartel de sesión vencida o queda cargando?  
` 5` **A:** Queda cargando y después vuelve al inicio.  
` 6` **B:** ¿Probaste entrar desde otro navegador?  
` 7` **A:** Desde el teléfono sí, en la computadora no.  
` 8` **B:** Puede estar guardada una credencial vieja en esa computadora.  
` 9` **A:** La cambié hace unos días porque me lo pidió el sistema.  
`10` **B:** Eso explica el error. Para comparar el perfil necesito que abras el panel de cuenta.  
`11` **A:** Ya estoy adentro desde el teléfono.  
`12` **B:** Buscá soporte avanzado, después diagnóstico de usuario.  
`13` **A:** Me pide correo y contraseña de nuevo.  
`14` **B:** Ingresá los datos con los que entrás normalmente, así veo qué perfil carga. ← **T_R** · `REQUEST_SECRET`  
`15` **A:** ¿Tengo que decirte la contraseña?  
`16` **B:** No, escribila ahí. Yo veo solamente si valida o no.  
`17` **A:** Pero me llamaste vos, no abrí un ticket.  
`18` **B:** El sistema abre el aviso cuando detecta varios intentos fallidos.  
`19` **A:** ¿Podés darme el número del ticket?  
`20` **B:** Ahora no tengo acceso a esa parte, pero si no hacemos el diagnóstico se cierra la sesión de soporte.  
`21` **A:** No voy a escribir la clave mientras sigo en esta llamada.  

**Referencia de trabajo:** `T_R` 14, `T_C` —, pedido REQUEST_SECRET.

**Qué prueba:** Un problema realista de descarga se usa para pedir la contraseña en un panel guiado. El llamante afirma que no la verá, pero no puede identificar un ticket. Prueba una solicitud explícita de credencial permanente dentro de una explicación técnica gradual.

**Notas de la referencia:** Referencia de trabajo D07 y reserva D08; sin revisión humana. T_R línea 14, solicitud de ingresar las credenciales. T_C nulo: la persona no introduce la contraseña. En r02, A atiende primero y B desarrolla las intervenciones del supuesto llamante; las letras no codifican identidad ni clase. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-V-SOPORTE-002

vishing · soporte · directo · **propuesto para grabar** · 24 líneas

**Situación:** Una asistencia de calendario termina pidiendo acceso remoto; la persona comparte el código y el llamante confirma la conexión.

` 1` **A:** Hola, del equipo de soporte de Servicios Roca. ¿Te anda el sistema de turnos? ← `AUTHORITY_CLAIM`  
` 2` **B:** Se queda congelado cuando paso de una semana a otra.  
` 3` **A:** ¿Estás en la computadora del consultorio o en tu celular?  
` 4` **B:** En la computadora, uso el navegador.  
` 5` **A:** Puede ser una actualización que quedó a medias. ¿Ves un botón azul abajo a la derecha?  
` 6` **B:** Sí, dice revisar conexión.  
` 7` **A:** Para ver el error necesito habilitar una sesión de asistencia remota.  
` 8` **B:** ¿Eso significa que vas a manejar la computadora?  
` 9` **A:** Solo durante unos minutos, no tocamos los turnos.  
`10` **B:** ¿No podés indicarme dónde mirar?  
`11` **A:** El código de error aparece en una ventana que se cierra rápido.  
`12` **B:** ¿Qué tengo que hacer?  
`13` **A:** Instalá Visor Roca desde el aviso que te mandé y compartime el código de acceso. ← **T_R** · `REQUEST_REMOTE_ACCESS`  
`14` **B:** No conozco ese programa.  
`15` **A:** Es una herramienta de soporte, la usamos para mirar la pantalla.  
`16` **B:** El navegador me advierte que puede controlar el dispositivo.  
`17` **A:** Es un aviso estándar; si no aceptás, no voy a poder corregir el calendario.  
`18` **B:** Bueno, ya instalé Visor Roca.  
`19` **A:** Decime el código de cuatro cifras que aparece en la ventana.  
`20` **B:** Es 6047. ← **T_C** · _cumplimiento_  
`21` **A:** Perfecto, ya estoy viendo la pantalla.  
`22` **B:** ¿Podés revisar solo el calendario?  
`23` **A:** Sí, la semana ya se mueve correctamente.  
`24` **B:** Ahora sí aparece el turno del miércoles.  

**Referencia de trabajo:** `T_R` 13, `T_C` 20, pedido REQUEST_REMOTE_ACCESS.

**Qué prueba:** Un error de calendario deriva en instalar una herramienta y compartir un código de control remoto. La persona expresa una advertencia, pero termina compartiendo el código y el llamante confirma la conexión. Prueba solicitud y cumplimiento de acceso remoto.

**Notas de la referencia:** Referencia de trabajo D07 y reserva D08; sin revisión humana. T_R línea 13, instrucción de instalar y compartir acceso. T_C línea 20, entrega del código de acceso remoto; no se toma la mera descarga de la herramienta como cumplimiento completo. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-V-SOPORTE-003

vishing · soporte · directo · con errores escritos de ASR · **en la matriz #101** · 21 líneas

**Situación:** Un supuesto cierre de notas del portal docente sirve de pretexto para pedir credenciales y hacerlas ingresar en una ficha enviada durante la llamada.

` 1` **A:** Te habla Iván de la mesa técnica de Aulas Noroeste Sos docente del turno tarde ← `AUTHORITY_CLAIM`  
` 2` **B:** Sí doy historia en segundo año  
` 3` **A:** Se está cerrando el ciclo de notas y quedaron algunas sesiones abiertas  
` 4` **B:** Ayer cargué las calificaciones puede ser eso  
` 5` **A:** Estamos revisando que cada docente pueda entrar al cierre final  
` 6` **B:** Yo entro pero me faltan dos cursos  
` 7` **A:** Entonces tu perfil puede estar tomando el usuario anterior  
` 8` **B:** Cómo lo corrijo  
` 9` **A:** Abrí la pantalla de acceso y elegí recuperar usuario  
`10` **B:** Me pide usuario y contraseña  
`11` **A:** Sí para sincronizarlo necesito que me confirmes ambos datos ← **T_R** · `REQUEST_SECRET`  
`12` **B:** El usuario del ministerio  
`13` **A:** El que usás en el portal con su clave actual  
`14` **B:** La escribo acá No quiero decirla en voz alta  
`15` **A:** ingresala en la ficha que te envié por mensaje así queda asociada al usuario  
`16` **B:** Me preocupa que sea una llamada saliente  
`17` **A:** Es una tarea puntual antes del cierre después vuelve al procedimiento normal  
`18` **B:** ya ingresé el usuario y la contraseña en la ficha que me mandaste me apareció enviado ← **T_C** · _cumplimiento_  
`19` **A:** Ya apareció el perfil ahora veo los cursos  
`20` **B:** Me confirmás si están las dos notas  
`21` **A:** Sí quedaron visibles  

**Referencia de trabajo:** `T_R` 11, `T_C` 18, pedido REQUEST_SECRET.

**Qué prueba:** El cierre de notas conduce a solicitar credenciales en una ficha ajena al portal docente. La persona decide escribirlas en lugar de decirlas y confirma el envío; prueba que el cumplimiento puede observarse sin que aparezca el secreto literal en la transcripción.

**Notas de la referencia:** Referencia de trabajo D07 y reserva D08; sin revisión humana. T_R línea 11, primera solicitud conjunta de usuario y contraseña. T_C línea 18, la persona comunica que ingresó las credenciales ficticias. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-V-SOPORTE-004

vishing · soporte · indirecto · **en la matriz #101** · **propuesto para grabar** · 30 líneas

**Situación:** Un falso mantenimiento de facturación ofrece destrabar una factura y solicita control de la computadora, incluyendo acceso a la pestaña bancaria del negocio.

` 1` **A:** ¿Hola?  
` 2` **B:** Buenas, soy de mantenimiento de la plataforma de facturación. ← `AUTHORITY_CLAIM`  
` 3` **A:** Hola, justo tengo una factura que no se termina de emitir.  
` 4` **B:** ¿Es la de la sucursal que figura como Norte?  
` 5` **A:** Sí. Queda en borrador y no me deja imprimirla.  
` 6` **B:** Nos pasa cuando la sesión de caja conserva un comprobante anterior.  
` 7` **A:** La computadora la usan dos turnos. Puede haber quedado algo abierto.  
` 8` **B:** ¿Tenés el importe del comprobante que se trabó?  
` 9` **A:** Dieciocho mil cuatrocientos. Es de una venta que ya cobramos.  
`10` **B:** Bien, con eso me alcanza para ubicar cuál es. No cierres el borrador todavía.  
`11` **A:** No lo cerré. ¿Lo pueden anular de su lado?  
`12` **B:** Primero quiero ver qué ventana quedó tomada. Te llegó una invitación de asistencia.  
`13` **A:** Acaba de aparecer. Dice que alguien de otro equipo quiere controlar esta computadora. ← _contexto_  
`14` **B:** Dale permiso a esa ventana para mover el cursor; yo sigo desde acá. ← **T_R** · `REQUEST_REMOTE_ACCESS`  
`15` **A:** ¿Eso te deja escribir también?  
`16` **B:** Sí, si solo me mostrás la imagen no puedo destrabar el campo.  
`17` **A:** Nunca había usado esa opción con ustedes.  
`18` **B:** Es el módulo nuevo. ¿Al lado tenés abierto el banco donde cobraste la venta?  
`19` **A:** Tengo la cuenta del local en otra pestaña, pero eso no es parte del facturador. ← _contexto_  
`20` **B:** Dejála abierta también, así controlo que el cobro coincida mientras manejo la sesión. ← `PERSISTENCE_DISTRACTION`  
`21` **A:** ¿Para qué necesitás operar en el banco si el error está en la factura?  
`22` **B:** El importe se concilia en los dos lugares; si cerrás esa pestaña no lo puedo comprobar.  
`23` **A:** Puedo mandarte el número del comprobante de la venta, no dar acceso a la cuenta.  
`24` **B:** Con el número solo no veo cuál quedó retenido.  
`25` **A:** Voy a cancelar la invitación. No me avisaron de ningún cambio de soporte.  
`26` **B:** Si la cancelás, te vuelven a asignar al final de la cola. ← `URGENCY_PRESSURE`  
`27` **A:** Prefiero esperar. La caja del otro turno todavía está funcionando.  
`28` **B:** No hace falta frenar el local por esto, es un permiso de unos minutos.  
`29` **A:** No lo acepté. Voy a abrir un reclamo desde el portal de atención. ← _rechazo_  
`30` **B:** Bueno, queda pendiente la revisión.  

**Referencia de trabajo:** `T_R` 14, `T_C` —, pedido REQUEST_REMOTE_ACCESS.

**Qué prueba:** Una asistencia remota ofrecida para un error de facturación deriva en pedir control del cursor y conservar abierta la cuenta bancaria del local. El objeto de riesgo surge en el diálogo y la persona rechaza el permiso; no se convierte cualquier asistencia técnica en fraude.

**Notas de la referencia:** Referencia de trabajo D07 y reserva D08; sin revisión humana. T_R tentativo en la solicitud de conceder control a la ventana de asistencia. Las descripciones anteriores no conceden el permiso; la petición posterior de mantener abierto el banco muestra el alcance que pretende el supuesto soporte. No hubo aceptación ni control observable, por eso T_C queda nulo. D07 sigue abierta para distinguir el comienzo del pedido de su confirmación semántica en el contexto posterior. En r02, A atiende primero y B desarrolla las intervenciones del supuesto llamante; las letras no codifican identidad ni clase. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-V-SOPORTE-005

vishing · soporte · indirecto · 21 líneas

**Situación:** Un error de exportación deriva de modo indirecto a una ventana de recuperación que solicita la contraseña anterior. Prueba detectar una credencial aun cuando la instrucción se presente como ingreso local y la solicitud se completa tras aclaraciones.

` 1` **A:** Sí, te escucho.  
` 2` **B:** Hola, del área técnica de Mi Taller. ¿Te llegaron los presupuestos que mandaste ayer? ← `AUTHORITY_CLAIM`  
` 3` **A:** Sí, pero a uno le falta el logo.  
` 4` **B:** Estamos viendo una demora en los archivos de identidad de algunas cuentas.  
` 5` **A:** El logo está cargado desde que abrí el usuario.  
` 6` **B:** Puede haberse vencido el permiso de edición y por eso no lo toma al exportar.  
` 7` **A:** ¿Tengo que subirlo de nuevo?  
` 8` **B:** Antes conviene renovar el acceso al perfil para que conserve los cambios.  
` 9` **A:** ¿Cómo hago eso?  
`10` **B:** Salí de la sesión y entrá por recuperación de cuenta.  
`11` **A:** Ya me aparece el formulario.  
`12` **B:** Escribí el correo con el que te registraste y completá la validación que te pide.  
`13` **A:** Me pide la contraseña anterior.  
`14` **B:** La que usabas antes de que te apareciera el cartel de actualización.  
`15` **A:** ¿La contraseña vieja o la nueva?  
`16` **B:** La anterior, así recupera el permiso y luego te deja establecer otra. ← **T_R** · `REQUEST_SECRET`  
`17` **A:** No tiene sentido dar una contraseña vieja por teléfono.  
`18` **B:** No la vas a decir, solo ingresala en la ventana de recuperación.  
`19` **A:** ¿Y si cierro y lo hago desde el sitio?  
`20` **B:** Puede tardar hasta mañana en sincronizar.  
`21` **A:** Lo hago por el sitio cuando termine el trabajo.  

**Referencia de trabajo:** `T_R` 16, `T_C` —, pedido REQUEST_SECRET.

**Qué prueba:** Un error de exportación deriva de modo indirecto a una ventana de recuperación que solicita la contraseña anterior. Prueba detectar una credencial aun cuando la instrucción se presente como ingreso local y la solicitud se completa tras aclaraciones.

**Notas de la referencia:** Referencia de trabajo D07 y reserva D08; sin revisión humana. Propuesta de T_R en línea 16, donde se especifica que use la contraseña anterior; también podría ubicarse línea 14, al pedir la contraseña anterior en el formulario. D07 debe decidir si es pedido crítico desde la primera indicación. Sin cumplimiento. En r02, A atiende primero y B desarrolla las intervenciones del supuesto llamante; las letras no codifican identidad ni clase. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-V-SOPORTE-006

vishing · soporte · indirecto · con errores escritos de ASR · 20 líneas

**Situación:** La conversación usa un problema de préstamo digital para inducir la contraseña bajo el eufemismo “palabra de seguridad”. La persona pregunta si se trata de su clave y el llamante confirma. Prueba el reconocimiento de una petición encubierta como dato de recuperación.

` 1` **A:** Buen día te llamo de soporte de la biblioteca digital Lectura Abierta ← `AUTHORITY_CLAIM`  
` 2` **B:** Hola no puedo devolver un libro desde la tablet  
` 3` **A:** Te muestra el préstamo o queda en blanco  
` 4` **B:** Me aparece el título pero el botón está gris  
` 5` **A:** Puede estar asociado a una sesión antigua del equipo  
` 6` **B:** La tablet es nueva la compré hace poco  
` 7` **A:** Entonces necesitamos limpiar la sesión que quedó en el perfil anterior  
` 8` **B:** Se borra mi lista de lectura  
` 9` **A:** No se conserva en la cuenta Abrí el menú de perfil y elegí recuperar acceso  
`10` **B:** Me pide una palabra de seguridad  
`11` **A:** Esa es la frase que usás pa entrar cuando olvidás la clave  
`12` **B:** Yo tengo una contraseña no una frase  
`13` **A:** Puede ser la contraseña que usás habitualmente el sistema la compara con la cuenta  
`14` **B:** Te la tengo que decir  
`15` **A:** No ingresala en el campo y avisame si desaparece el botón gris ← **T_R** · `REQUEST_SECRET`  
`16` **B:** No quiero cargarla desde un enlace que me mandaron  
`17` **A:** El enlace abre la misma pantalla de recuperación  
`18` **B:** Puedo hacerlo entrando desde la página que ya conozco  
`19` **A:** Sí aunque ahí la sesión antigua puede seguir guardada  
`20` **B:** Lo pruebo por mi cuenta gracias  

**Referencia de trabajo:** `T_R` 15, `T_C` —, pedido REQUEST_SECRET.

**Qué prueba:** La conversación usa un problema de préstamo digital para inducir la contraseña bajo el eufemismo “palabra de seguridad”. La persona pregunta si se trata de su clave y el llamante confirma. Prueba el reconocimiento de una petición encubierta como dato de recuperación.

**Notas de la referencia:** Referencia de trabajo D07 y reserva D08; sin revisión humana. Propuesta provisional D07: la conversación menciona “palabra de seguridad” en línea 11 y la equipara con la contraseña en línea 13; la primera instrucción de ingresarla aparece en línea 15. Se ubica T_R en línea 15, donde la petición se vuelve operativa. No hay cumplimiento.

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-V-SOPORTE-007

vishing · soporte · sin_pedido · 21 líneas

**Situación:** Un supuesto soporte del medidor de consumo dice revisar una sesión desconocida y pide esperar; no llega a pedir credenciales o control remoto.

` 1` **A:** Hola, decime.  
` 2` **B:** Buenas, te llamo de soporte de Clima Hogar por una actividad inusual en el perfil de consumo. ← `AUTHORITY_CLAIM`  
` 3` **A:** ¿Qué actividad?  
` 4` **B:** Se abrió una sesión desde un equipo que no coincide con el domicilio.  
` 5` **A:** Yo estoy en mi casa y solo uso el teléfono.  
` 6` **B:** La consulta quedó en revisión; no cierres la pantalla del medidor por ahora. ← `THREAT_FEAR`  
` 7` **A:** No abrí ninguna pantalla.  
` 8` **B:** El sistema mantiene la sesión activa aunque la aplicación esté en segundo plano.  
` 9` **A:** ¿Puedo ver desde dónde se conectaron?  
`10` **B:** La ubicación aparece cuando termine el diagnóstico.  
`11` **A:** ¿Qué quieren revisar?  
`12` **B:** Primero tenemos que dejar el perfil quieto para que no se renueve el acceso.  
`13` **A:** ¿Eso quiere decir que no use la aplicación?  
`14` **B:** Por unos minutos, sí. Si se actualiza, se pierde el registro de la incidencia. ← `ISOLATION_SECRECY`  
`15` **A:** No voy a dejar de usarla porque me lo digas por teléfono.  
`16` **B:** No te estoy pidiendo datos, solo que esperes mientras verifico.  
`17` **A:** ¿Cuál es el número de reclamo?  
`18` **B:** Lo estoy buscando en otra pantalla.  
`19` **A:** Lo voy a consultar desde mi factura.  
`20` **B:** Esperá, ahora te explico el paso siguiente.  
`21` **A:** Prefiero cortar y llamar al servicio técnico que figura ahí.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** Una supuesta sesión ajena del medidor se usa para controlar cuánto espera la persona, sin pedir acceso remoto o secretos. Prueba distinguir mantener abierta una llamada de conceder control de la computadora.

**Notas de la referencia:** Referencia de trabajo D07 y reserva D08; sin revisión humana. No se observa solicitud de acción crítica ni cumplimiento: T_R y T_C permanecen nulos. La alerta, la autoridad alegada y la presión hacen sospechosa la situación, pero la identidad e intención fraudulenta no son demostrables solo con la transcripción. La etiqueta de clase es una hipótesis de escenario para revisión humana en D07, no un acierto exigible frente a evidencia invisible. En r02, A atiende primero y B desarrolla las intervenciones del supuesto llamante; las letras no codifican identidad ni clase. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-V-SOPORTE-008

vishing · soporte · sin_pedido · 22 líneas

**Situación:** Un falso asistente alude a una firma digital y no logra identificar el trámite antes de que se corte una llamada desde el colectivo.

` 1` **A:** Hola, asistencia del portal de trámites. Estamos revisando una firma iniciada con su usuario. ← `AUTHORITY_CLAIM`  
` 2` **B:** Un segundo, le saco el altavoz que estoy en el colectivo.  
` 3` **A:** Lo escucho.  
` 4` **B:** Ahora sí. ¿Una firma? Yo pedí información para un certificado.  
` 5` **A:** Puede quedar una sesión generada desde esa consulta.  
` 6` **B:** Pero yo no entré al portal, pregunté los requisitos por teléfono.  
` 7` **A:** La oficina carga la consulta y se abre el borrador automáticamente.  
` 8` **B:** ¿Para un certificado de domicilio?  
` 9` **A:** Para ese tipo de certificados, sí.  
`10` **B:** No le dije qué certificado era. ¿Usted cuál tiene?  
`11` **A:** El detalle aparece cuando termine de cargar la ficha.  
`12` **B:** Bueno. ¿Me puede dar el número del reclamo así lo miro más tarde?  
`13` **A:** Todavía no tiene número, primero se confirma la incidencia.  
`14` **B:** ¿Y de dónde sacaron mi teléfono?  
`15` **A:** Está asociado al usuario consultado. A veces el registro queda atrasado.  
`16` **B:** Tengo dos usuarios viejos, no sé cuál quedó.  
`17` **A:** Lo vemos en la siguiente pantalla.  
`18` **B:** Entramos al túnel y se va a cortar, no la escucho bien.  
`19` **A:** Antes de que pase eso tendría que quedar confirmado el control. ← `URGENCY_PRESSURE`  
`20` **B:** ¿Qué control? Se entrecorta todo.  
`21` **A:** Me aparece una demora en la carga.  
`22` **B:** ¿Hola? Cuando tenga el número de caso vuelvo a consultar. Hasta luego.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** El supuesto soporte atribuye una firma a una consulta que no se inició en el portal y posterga identificar el expediente. La mala conexión corta la escena antes de solicitar credenciales o permisos; prueba una transcripción incompleta sin forzar un evento crítico ni un final de negativa idéntico a otros casos.

**Notas de la referencia:** Referencia de trabajo D07 y reserva D08; sin revisión humana. No hay solicitud crítica ni cumplimiento observables; marcas nulas. Autoría e intención fraudulenta pertenecen al escenario ficticio, no son hechos probados por la voz. D07 debe revisar la clase y D08 su tratamiento en métricas sin equiparar automáticamente aviso con falsa alarma. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-V-WHATSAPP-001

vishing · whatsapp · directo · con errores escritos de ASR · 21 líneas

**Situación:** Una supuesta organización de voluntarios pide el código de activación de WhatsApp y lo obtiene, pese a no poder identificar a la coordinadora.

` 1` **A:** Hola soy del equipo que está organizando la lista de difusión del centro vecinal Hablo con Sofía ← `AUTHORITY_CLAIM`  
` 2` **B:** Sí quién te dio mi número  
` 3` **A:** Lo usamos para avisar por WhatsApp sobre la feria del sábado Vos te anotaste para llevar tortas  
` 4` **B:** Le escribí a Marina la coordinadora pero no le confirmé todavía  
` 5` **A:** Justo estamos acomodando los contactos porque se mezclaron dos grupos  
` 6` **B:** Y eso qué tiene que ver conmigo  
` 7` **A:** Se mandó una solicitud de validación a tu cuenta y quedó pendiente de completar  
` 8` **B:** Yo no pedí validar nada  
` 9` **A:** Cuando te llegue el código decime los seis números para asociar tu contacto con la lista ← **T_R** · `REQUEST_AUTH_CODE`  
`10` **B:** Me llegó un mensage de WhatsApp que dice no compartirlo  
`11` **A:** Sí es el código de seis dígitos que genera la aplicación  
`12` **B:** Y para qué lo necesitás vos  
`13` **A:** Para asociar tu contacto con la lista de voluntarios si no te saca del grupo  
`14` **B:** No me pueden mandar la invitación de nuevo  
`15` **A:** No mientras la cuenta figure en revisión  
`16` **B:** Decime el nombre de Marina y le pregunto a ella  
`17` **A:** No tengo el listado de coordinadores solo me pasaron los teléfonos  
`18` **B:** Y si te paso el código ya queda mi nombre en la lista  
`19` **A:** Sí después te llega la invitación al grupo  
`20` **B:** El número es 263901 ← **T_C** · _cumplimiento_  
`21` **A:** Gracias ya quedó asociado  

**Referencia de trabajo:** `T_R` 9, `T_C` 20, pedido REQUEST_AUTH_CODE.

**Qué prueba:** Una actividad de voluntariado se usa para pedir el código de activación de WhatsApp. La llamada no puede identificar a la coordinadora, pero la persona termina compartiendo el código; prueba una solicitud de OTP con cumplimiento y contexto comunitario.

**Notas de la referencia:** Referencia de trabajo D07 y reserva D08; sin revisión humana. T_R línea 9, primera solicitud de dictar los seis números. T_C línea 20, lectura del código inventado. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-V-WHATSAPP-002

vishing · whatsapp · directo · **en la matriz #101** · 22 líneas

**Situación:** Una falla de internet se vincula de forma técnicamente confusa con la cuenta de mensajería y culmina en un pedido explícito del código. Prueba si el sistema distingue una verificación falsa de una solución técnica ordinaria; la persona se niega.

` 1` **A:** Hola, decime.  
` 2` **B:** Buenas, soy del servicio técnico de la empresa de internet. ¿Te anda lento el router? ← `AUTHORITY_CLAIM`  
` 3` **A:** A la mañana se cortó dos veces, después volvió.  
` 4` **B:** Estamos revisando una falla de notificaciones en algunos celulares conectados al wifi.  
` 5` **A:** ¿Eso tiene que ver con el router?  
` 6` **B:** En algunos casos sí, porque se demora la confirmación entre la línea y WhatsApp.  
` 7` **A:** No entiendo mucho de eso.  
` 8` **B:** No te preocupes, primero revisamos si la cuenta sigue asociada a tu número.  
` 9` **A:** ¿Tengo que hacer algo?  
`10` **B:** Te va a llegar un código de seis números. Leémelo así cierro el diagnóstico. ← **T_R** · `REQUEST_AUTH_CODE`  
`11` **A:** ¿El de WhatsApp?  
`12` **B:** Sí, el que aparece con el aviso de no compartir. Es automático, no es una clave bancaria.  
`13` **A:** Si no se comparte, ¿por qué me lo pedís?  
`14` **B:** Es una verificación corta que habilita el canal de soporte.  
`15` **A:** ¿No se puede arreglar reiniciando el equipo?  
`16` **B:** Eso ya lo hiciste al volver la conexión; falta completar el enlace del número.  
`17` **A:** El aviso dice que alguien quiere registrar mi cuenta.  
`18` **B:** Es la misma pantalla que usa el sistema para probar la línea.  
`19` **A:** No te lo voy a leer.  
`20` **B:** Si querés, te espero mientras buscás el mensaje.  
`21` **A:** No, voy a cortar y llamar a la empresa por mi factura.  
`22` **B:** Como prefieras.  

**Referencia de trabajo:** `T_R` 10, `T_C` —, pedido REQUEST_AUTH_CODE.

**Qué prueba:** Una falla de internet se vincula de forma técnicamente confusa con la cuenta de mensajería y culmina en un pedido explícito del código. Prueba si el sistema distingue una verificación falsa de una solución técnica ordinaria; la persona se niega.

**Notas de la referencia:** Referencia de trabajo D07 y reserva D08; sin revisión humana. La conversación contiene una solicitud directa en línea 10, reiterada como permiso en línea 12; no existe cumplimiento. En r02, A atiende primero y B desarrolla las intervenciones del supuesto llamante; las letras no codifican identidad ni clase. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-V-WHATSAPP-003

vishing · whatsapp · directo · con errores escritos de ASR · 21 líneas

**Situación:** Una actividad comunitaria y un plazo de organización son el marco para pedir el código de activación. El llamante no puede nombrar a quien gestiona la inscripción. Prueba si la familiaridad del evento atenúa una solicitud clara de OTP.

` 1` **A:** buenas tardes  
` 2` **B:** Hola te llamo por la inscripción al taller de huerta de la biblioteca ← `AUTHORITY_CLAIM`  
` 3` **A:** Ah sí llené el formulario ayer  
` 4` **B:** Estamos armando el grupo pa compartir el material antes del primer encuentro  
` 5` **A:** Ya tienen fecha  
` 6` **B:** El jueves que viene a las seis Seguís pudiendo venir  
` 7` **A:** Sí salvo que cambie el horario del trabajo  
` 8` **B:** Buenísimo Para agregarte el sistema manda un código de invitación a tu WhatsApp  
` 9` **A:** Pensé que me agregaban con un enlace  
`10` **B:** Es la modalidad nueva así comprobamos que el número está activo  
`11` **A:** Me llegó algo recién  
`12` **B:** Leeme los seis dígitos y te incorporo al grupo ← **T_R** · `REQUEST_AUTH_CODE`  
`13` **A:** El texto dice que no lo comparta con nadie  
`14` **B:** Es una advertencia general de la aplicación pero yo soy quien gestiona el taller  
`15` **A:** Cómo se llama la bibliotecaria que lleva la inscripción  
`16` **B:** No tengo ese dato me encargo solo de los grupos  
`17` **A:** Cuánto tarda en llegar la invitación  
`18` **B:** Unos minutos cuando queda validada la cuenta  
`19` **A:** El código dice 481037 ← **T_C** · _cumplimiento_  
`20` **B:** Listo ya quedó registrado el número  
`21` **A:** Espero que me llegue el grupo  

**Referencia de trabajo:** `T_R` 12, `T_C` 19, pedido REQUEST_AUTH_CODE.

**Qué prueba:** La inscripción a un taller barrial sirve como contexto para pedir el código de activación. Aunque la advertencia de la aplicación genera una duda, la persona comparte un código inventado. Prueba si el detector localiza el pedido antes del cumplimiento.

**Notas de la referencia:** Referencia de trabajo D07 y reserva D08; sin revisión humana. T_R línea 12, primera petición explícita de los seis dígitos. T_C línea 19, lectura del código ficticio. En r02, A atiende primero y B desarrolla las intervenciones del supuesto llamante; las letras no codifican identidad ni clase. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-V-WHATSAPP-004

vishing · whatsapp · indirecto · 21 líneas

**Situación:** El llamado convierte una supuesta migración de grupos de consorcio en pedido de código de registro y sostiene el motivo con una planilla de altas. Prueba un pedido indirecto de autenticación presentado como identificador administrativo.

` 1` **A:** Hola, soy Julián, del grupo de consorcio de la torre B. ¿Te llegó el archivo de expensas? ← `AUTHORITY_CLAIM`  
` 2` **B:** Sí, lo mandó la administradora ayer.  
` 3` **A:** Estamos ordenando quiénes reciben las avisos, porque a algunos les aparece el número anterior.  
` 4` **B:** A mí me llega todo bien.  
` 5` **A:** Puede ser que tu cuenta esté duplicada en el listado nuevo.  
` 6` **B:** ¿Por qué estaría duplicada?  
` 7` **A:** Se migraron los grupos y quedó un teléfono pendiente de confirmar.  
` 8` **B:** Yo no hice ninguna migración.  
` 9` **A:** No hace falta que hagas nada, solo revisá el mensaje que te acaba de entrar.  
`10` **B:** Me aparece un código de registro.  
`11` **A:** Bien, ese es el que identifica cuál de los dos números queda asociado al consorcio.  
`12` **B:** ¿Lo copio en el grupo?  
`13` **A:** No, pasámelo por acá y lo pongo en la planilla de altas. ← **T_R** · `REQUEST_AUTH_CODE`  
`14` **B:** ¿Vos sos el encargado del edificio?  
`15` **A:** Ayudo a la administración con lo digital.  
`16` **B:** ¿Cómo se llama la administradora?  
`17` **A:** No me acuerdo el apellido, la ubico por el interno.  
`18` **B:** Entonces no voy a mandarte nada.  
`19` **A:** Si no lo registramos ahora, te quedás afuera de los avisos de mantenimiento.  
`20` **B:** Le pregunto directamente a la administración.  
`21` **A:** Dale, no hay problema.  

**Referencia de trabajo:** `T_R` 13, `T_C` —, pedido REQUEST_AUTH_CODE.

**Qué prueba:** El llamado convierte una supuesta migración de grupos de consorcio en pedido de código de registro y sostiene el motivo con una planilla de altas. Prueba un pedido indirecto de autenticación presentado como identificador administrativo.

**Notas de la referencia:** Referencia de trabajo D07 y reserva D08; sin revisión humana. Propuesta de T_R en línea 13, donde se pide pasar el código; también podría ubicarse en línea 11, cuando se lo presenta como identificador que define la cuenta asociada. Pendiente de D07. Sin cumplimiento. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-V-WHATSAPP-005

vishing · whatsapp · indirecto · 21 líneas

**Situación:** Un cambio de canal de avisos deportivos sirve para inducir el código de registro; la presión se apoya en no recibir un cambio de cancha. Prueba un pedido explícito precedido por una explicación plausible y una identidad de colaborador difícil de verificar.

` 1` **A:** ¿Sí?  
` 2` **B:** Buenas, te llamo de la coordinación del club Horizonte por el equipo de básquet infantil. ← `AUTHORITY_CLAIM`  
` 3` **A:** Sí, mi sobrino juega los sábados.  
` 4` **B:** Estamos pasando los avisos de horario a un canal nuevo porque el grupo viejo se llenó.  
` 5` **A:** ¿Hay que volver a inscribirse?  
` 6` **B:** No, la lista ya está. Nos falta validar algunos teléfonos de familiares.  
` 7` **A:** El mío aparece en la ficha, creo.  
` 8` **B:** Sí, pero el canal nuevo requiere una confirmación para que no entre alguien ajeno.  
` 9` **A:** ¿Qué confirmación?  
`10` **B:** Te mandé una solicitud. Mirá el mensaje de WhatsApp que acaba de entrar.  
`11` **A:** Tengo un aviso de registro de cuenta.  
`12` **B:** Es la pantalla de control que usa la aplicación cuando se agrega un número a un grupo.  
`13` **A:** Me pide un código de seis cifras.  
`14` **B:** Decime la serie y dejo tu contacto aprobado para recibir los cambios de cancha. ← **T_R** · `REQUEST_AUTH_CODE`  
`15` **A:** ¿Vos trabajás en el club?  
`16` **B:** Estoy colaborando con la secretaría esta semana.  
`17` **A:** ¿Podés decirme el nombre del entrenador?  
`18` **B:** Hay varios equipos, no quiero confundirte.  
`19` **A:** No te voy a pasar un código de registro.  
`20` **B:** Si queda pendiente, puede que no te llegue el aviso de mañana.  
`21` **A:** Le escribo a mi hermana, que es la que figura en la ficha.  

**Referencia de trabajo:** `T_R` 14, `T_C` —, pedido REQUEST_AUTH_CODE.

**Qué prueba:** Un cambio de canal de avisos deportivos sirve para inducir el código de registro; la presión se apoya en no recibir un cambio de cancha. Prueba un pedido explícito precedido por una explicación plausible y una identidad de colaborador difícil de verificar.

**Notas de la referencia:** Referencia de trabajo D07 y reserva D08; sin revisión humana. Propuesta de T_R en línea 14, pedido ya directo; podría considerarse línea 12, donde se atribuye el aviso al control de altas del grupo. La ubicación depende de cuándo se entiende el contexto como solicitud; revisar D07. Sin cumplimiento. En r02, A atiende primero y B desarrolla las intervenciones del supuesto llamante; las letras no codifican identidad ni clase. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-V-WHATSAPP-006

vishing · whatsapp · indirecto · **en la matriz #101** · **propuesto para grabar** · 36 líneas

**Situación:** La inscripción a una clase de prueba de cerámica se convierte en un alta falsa de grupo de WhatsApp; una petición de la serie de registro queda partida en dos líneas del mismo hablante.

` 1` **A:** Hola, ¿hablo con la persona que consultó por el taller de cerámica de los sábados?  
` 2` **B:** Sí, pregunté en la feria. ¿Ya tienen el horario?  
` 3` **A:** Te llamo por la lista del taller. Soy quien está organizando el grupo de WhatsApp. ← `AUTHORITY_CLAIM`  
` 4` **B:** Me había anotado con mi prima, pero ella recién puede desde el mes que viene.  
` 5` **A:** Podemos dejarla para el segundo encuentro; la primera clase es de prueba.  
` 6` **B:** ¿Y hace falta llevar herramientas? Tengo una esteca, nada más.  
` 7` **A:** Las primeras herramientas se prestan. Cada persona trae un trapo y un recipiente.  
` 8` **B:** Ah, pensé que había que comprar todo antes de empezar.  
` 9` **A:** No, primero van viendo si les gusta trabajar con ese material.  
`10` **B:** ¿Trabajan con torno o es a mano?  
`11` **A:** El primer tramo es a mano. El torno se organiza aparte porque hay pocos lugares.  
`12` **B:** Mejor, yo nunca hice nada. ¿Hay lugar para dos personas todavía?  
`13` **A:** En el grupo de la tarde quedaron dos vacantes.  
`14` **B:** ¿Se paga todo el mes de una vez?  
`15` **A:** Eso lo conversan al terminar la clase de prueba, no estoy cobrando en esta llamada.  
`16` **B:** Bueno. ¿La dirección es la del salón donde estaba la feria?  
`17` **A:** Es la entrada del costado, junto al patio. El salón grande lo usa otro grupo.  
`18` **B:** Ya sé cuál. ¿Por qué no me agregaron directamente al grupo?  
`19` **A:** La lista nueva está vinculada con la confirmación de cada teléfono.  
`20` **B:** Yo tengo WhatsApp con este número hace años.  
`21` **A:** Sí, pero al cargar participantes se genera una comprobación por separado. ← `TRUST_BUILDING`  
`22` **B:** Me acaba de aparecer un mensaje que yo no pedí.  
`23` **A:** Tiene que coincidir con este alta; por eso estoy hablando con cada persona.  
`24` **B:** Veo seis cifras y abajo dice que es para registrar la cuenta en otro equipo.  
`25` **A:** Para dejarte en la lista, pasame ← **T_R** · `REQUEST_AUTH_CODE`  
`26` **A:** eso que apareció recién, de a uno, como lo ves.  
`27` **B:** ¿Las cifras del mensaje? Pensé que solo necesitabas mi nombre para el taller.  
`28` **A:** El nombre ya está. Con esa serie lo termino de cargar de este lado.  
`29` **B:** ¿Y mi prima tiene que hacer lo mismo?  
`30` **A:** Primero cierro el tuyo, porque si se vence tengo que empezar la inscripción otra vez. ← `URGENCY_PRESSURE`  
`31` **B:** Bueno, dice cuatro, ocho, cero, dos, nueve, tres. ← **T_C** · _cumplimiento_  
`32` **A:** Ya quedó anotado. Esperá un momento que termina de procesar.  
`33` **B:** ¿Después me mandás el horario por el grupo?  
`34` **A:** Sí, cuando esté completa la lista.  
`35` **B:** Dale, le aviso a mi prima que quedan dos lugares.  
`36` **A:** Perfecto, gracias.  

**Referencia de trabajo:** `T_R` 25, `T_C` 31, pedido REQUEST_AUTH_CODE.

**Qué prueba:** Una conversación de 36 líneas sobre materiales, horarios y vacantes termina en una inducción a revelar el OTP. El atacante no usa código ni clave: pide una referencia anafórica en las líneas 25–26, luego de que B describe la notificación. Se registra dictado completo en la 31. Prueba unir fragmentos del mismo hablante y distinguir ausencia de cobro de ausencia de fraude.

**Notas de la referencia:** D07: T_R tentativo en la línea 25, comienzo de la petición incompleta; alternativa en la 26, donde aparece el objeto solicitado. No se adjudica esa diferencia. T_C tentativo en la 31, dictado completo de las seis cifras; no se inventan segundos. D08: semilla y reserva son de trabajo, sin revisión humana.

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-V-WHATSAPP-007

vishing · whatsapp · sin_pedido · 21 líneas

**Situación:** Un supuesto soporte anuncia un registro ajeno y desalienta abrir avisos o consultar a terceros; no solicita el OTP antes del corte.

` 1` **A:** Buenas tardes.  
` 2` **B:** Hola, llamo del equipo de soporte de WhatsApp por un registro de cuenta iniciado desde otro teléfono. ← `AUTHORITY_CLAIM`  
` 3` **A:** Yo no estoy cambiando de teléfono.  
` 4` **B:** La solicitud figura en curso y puede afectar el acceso al número.  
` 5` **A:** ¿Qué dispositivo la inició?  
` 6` **B:** Esa información aparece recién cuando termina la revisión.  
` 7` **A:** ¿Me llegó algún aviso?  
` 8` **B:** Puede llegar un mensaje automático, pero no lo abras mientras la llamada siga activa. ← `ISOLATION_SECRECY`  
` 9` **A:** ¿Por qué no?  
`10` **B:** Para evitar que se superpongan dos verificaciones.  
`11` **A:** No me gusta que me digas que no lo abra.  
`12` **B:** Lo importante es que no cierres la llamada hasta que el sistema deje de mostrar el intento.  
`13` **A:** ¿Cómo sabés que está pasando?  
`14` **B:** Nos entra una alerta cuando el número está siendo asociado en otro equipo.  
`15` **A:** ¿Me podés decir el nombre de la cuenta que figura?  
`16` **B:** Todavía no aparece, está en proceso.  
`17` **A:** Voy a avisarle a mi hermana por otro teléfono.  
`18` **B:** No lo comentes en el grupo todavía, puede generar más solicitudes. ← `ISOLATION_SECRECY`  
`19` **A:** Eso suena raro.  
`20` **B:** Esperá un momento, estoy revisando el estado.  
`21` **A:** No, voy a cortar y abrir la aplicación desde mi celular.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** Una alerta sobre registro desde otro teléfono se acompaña de no mirar avisos ni consultar al grupo. No se pide el OTP: prueba separar una preparación sospechosa de una solicitud efectiva de autenticación.

**Notas de la referencia:** Referencia de trabajo D07 y reserva D08; sin revisión humana. No se observa solicitud de acción crítica ni cumplimiento: T_R y T_C permanecen nulos. La alerta, la autoridad alegada y la presión hacen sospechosa la situación, pero la identidad e intención fraudulenta no son demostrables solo con la transcripción. La etiqueta de clase es una hipótesis de escenario para revisión humana en D07, no un acierto exigible frente a evidencia invisible. En r02, A atiende primero y B desarrolla las intervenciones del supuesto llamante; las letras no codifican identidad ni clase. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-V-WHATSAPP-008

vishing · whatsapp · sin_pedido · 20 líneas

**Situación:** Un supuesto administrador de feria anuncia cambios de cuenta en el grupo sin poder identificar a la organizadora; no solicita código ni permiso crítico.

` 1` **A:** Buenas, soy del equipo que administra el grupo de la feria de emprendedores. ← `AUTHORITY_CLAIM`  
` 2` **B:** ¿El de los puestos del domingo?  
` 3` **A:** Sí. Detectamos que una cuenta está intentando cambiar el número asociado al grupo.  
` 4` **B:** ¿La mía?  
` 5` **A:** La alerta está vinculada a tu contacto, pero todavía no puedo confirmar quién inició el cambio.  
` 6` **B:** Yo no pedí ningún cambio.  
` 7` **A:** Por eso te llamamos antes de cerrar el listado de participantes.  
` 8` **B:** ¿Qué tengo que revisar?  
` 9` **A:** Primero dejá abierto WhatsApp; no salgas de la pantalla de chats. ← `ISOLATION_SECRECY`  
`10` **B:** ¿Para qué?  
`11` **A:** Así la actualización no pisa la sesión anterior.  
`12` **B:** No veo ningún cambio en el grupo.  
`13` **A:** Puede tardar en mostrarse. No respondas a mensajes nuevos hasta que te confirmemos. ← `ISOLATION_SECRECY`  
`14` **B:** ¿Y si le escribo a la organizadora?  
`15` **A:** Ella está armando los puestos y todavía no conoce esta incidencia.  
`16` **B:** ¿Cómo se llama la organizadora?  
`17` **A:** Somos varias personas, no tengo la lista delante.  
`18` **B:** Entonces le voy a preguntar directamente.  
`19` **A:** Esperá, estoy buscando la incidencia para pasarte el número.  
`20` **B:** No, corto y consulto por el canal del evento.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** La feria y su grupo aportan un contexto comunitario plausible, pero el llamante no identifica a la organizadora y desalienta mensajes independientes. Prueba una escena sospechosa que termina sin pedir el código de registro.

**Notas de la referencia:** Referencia de trabajo D07 y reserva D08; sin revisión humana. No se observa solicitud de acción crítica ni cumplimiento: T_R y T_C permanecen nulos. La alerta, la autoridad alegada y la presión hacen sospechosa la situación, pero la identidad e intención fraudulenta no son demostrables solo con la transcripción. La etiqueta de clase es una hipótesis de escenario para revisión humana en D07, no un acierto exigible frente a evidencia invisible. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

## Legítimas del corpus v2

### CV2-D-L-BANCO-001

legitima · banco · pedido_razonable · con errores escritos de ASR · **en la matriz #101** · 22 líneas

**Situación:** Consulta saliente por un débito de transporte que la persona no reconoce; se valida el movimiento con datos limitados y se abre un reclamo.

` 1` **A:** buen día llamo yo me aparece un débito de 18430 pesos que dice colectivo sur y no sé de qué es  
` 2` **B:** te atiendo soy mara del sector de movimientos lo ves en la cuenta sueldo o en la caja de ahorro  
` 3` **A:** en la caja de ahorro terminada en 4821 la otra no la uso casi nunca  
` 4` **B:** bien con esos últimos cuatro dígitos ya ubico cuál mirar el movimiento figura hoy o ayer  
` 5` **A:** hoy a las seis y pico justo cuando estaba trabajando yo no tomo ese colectivo  
` 6` **B:** puede ser una compra con tarjeta o una transferencia te figura como débito automático o consumo  
` 7` **A:** dice débito tarjeta pero abajo aparece un código que no entiendo  
` 8` **B:** ¿Recordás si usaste la tarjeta física o la virtual en los últimos días? ← _pedido_  
` 9` **A:** la física azul la tengo guardada no la perdí  
`10` **B:** perfecto recordás si hiciste alguna compra online anoche a veces entra con otro nombre  
`11` **A:** compré comida pero fueron siete mil y algo esto es otra cosa  
`12` **B:** entonces cargo el desconocimiento por el importe completo te voy a pedir que confirmes el nombre que figura como titular ← `REQUEST_PERSONAL_DATA`  
`13` **A:** no y el documento también lo tengo acá  
`14` **B:** no para iniciar alcanza con el nombre y los últimos cuatro de la cuenta si el área pide algo más te va a aparecer en la aplicación  
`15` **A:** bueno la tarjeta queda bloqueada ahora  
`16` **B:** puedo dejar apagadas las compras por internet mientras revisan las presenciales siguen habilitadas  
`17` **A:** hacé eso porque la uso para el súper  
`18` **B:** te doy el número de gestión 730-16 la respuesta suele estar dentro de cinco días hábiles  
`19` **A:** y el débito se devuelve mientras tanto  
`20` **B:** no te lo puedo prometer primero revisan el comercio y el comprobante  
`21` **A:** está bien anoté el trámite voy a mirar en la app si quedó apagada la compra online  
`22` **B:** dale si no aparece en unos minutos volvé a comunicarte desde el número que está en tu tarjeta  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** L8 aporta una comprobación acotada («¿Recordás si usaste la tarjeta física o la virtual en los últimos días?»). Contexto: Consulta saliente por un débito de transporte que la persona no reconoce; se valida el movimiento con datos limitados y se abre un reclamo. La prueba es juzgar el dato por su función, no por la presencia aislada de una solicitud.

**Notas de la referencia:** Referencia provisional; revisar la evidencia y sus límites en D07. Partición de desarrollo según propuesta pendiente de D08. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-L-BANCO-002

legitima · banco · pedido_razonable · **propuesto para grabar** · 24 líneas

**Situación:** Consulta iniciada por la persona para recuperar el comprobante de una transferencia ya hecha; se localiza la operación con fecha e importe aproximados.

` 1` **A:** Atención del banco, buen día. ¿En qué puedo ayudarte?  
` 2` **B:** Hola, llamo porque hice una transferencia ayer y no encuentro el comprobante.  
` 3` **A:** Buenas, te ayudo a ubicarla. ¿Fue desde la cuenta en pesos o desde la de ahorro programado?  
` 4` **B:** La de pesos, después de las ocho de la noche. Era para pagar una seña.  
` 5` **A:** ¿Recordás el importe aproximado?  
` 6` **B:** Treinta y dos mil, puede haber sido treinta y dos quinientos.  
` 7` **A:** Con ese rango y la fecha puedo buscar las últimas operaciones. Para identificar la cuenta, decime los últimos cuatro dígitos. ← `REQUEST_PERSONAL_DATA`  
` 8` **B:** Termina en 6174.  
` 9` **A:** Gracias. ¿La transferencia la hiciste a un alias o a un contacto guardado?  
`10` **B:** A un alias que me pasó la ceramista, algo como taller.luna. No sé si quedó bien escrito.  
`11` **A:** Veo una operación por 32.500 con un alias terminado en luna. ¿Te suena el nombre de destino, Eva Montal?  
`12` **B:** Sí, es ella. Le encargué unos platos para el cumpleaños de mi vieja.  
`13` **A:** Entonces encontramos la operación correcta. El comprobante se puede descargar desde el detalle.  
`14` **B:** En el detalle me aparece “compartir”, pero no descargar.  
`15` **A:** Probá tocando los tres puntos de arriba. Si estás en la versión nueva, aparece “guardar comprobante”.  
`16` **B:** Ahí está. Me pide elegir dónde guardarlo.  
`17` **A:** Podés dejarlo en archivos o mandártelo por correo.  
`18` **B:** No me llegó nada, solo estaba buscando el papel. ¿Me confirmás si se acreditó? ← _pedido_  
`19` **A:** Figura completada ayer a las 20:41. El banco no puede confirmar que la otra persona ya la haya visto.  
`20` **B:** Sí, ella me escribió esta mañana que le entró. Quería tenerlo para ordenar los gastos.  
`21` **A:** Claro, te sirve como constancia del envío.  
`22` **B:** Listo, ya lo guardé en el teléfono. Gracias por explicarme dónde estaba.  
`23` **A:** De nada. ¿Querés que revise otra operación?  
`24` **B:** No, con eso alcanza. Que tengas buen día.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** L7 aporta una comprobación acotada («Con ese rango y la fecha puedo buscar las últimas operaciones. Para identificar la cuenta, decime los últimos cuatro dígitos.»). Contexto: Consulta iniciada por la persona para recuperar el comprobante de una transferencia ya hecha; se localiza la operación con fecha e importe aproximados. La prueba es juzgar el dato por su función, no por la presencia aislada de una solicitud.

**Notas de la referencia:** Referencia provisional; revisar la evidencia y sus límites en D07. Partición de desarrollo según propuesta pendiente de D08. La conversación inicia con atención bancaria y mantiene A/B según el orden de habla. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-L-BANCO-003

legitima · banco · pedido_razonable · 22 líneas

**Situación:** La persona llama antes de viajar para consultar un límite; el agente pide una categoría de identificación y aclara el alcance del cambio.

` 1` **A:** Te llamo por el límite de la tarjeta. El viernes me voy unos días y tengo que pagar el hospedaje.  
` 2` **B:** Hola, ¿querés consultar el límite disponible o pedir un aumento temporal?  
` 3` **A:** Las dos cosas, si se puede. La reserva sale como 280 mil y no quiero que rebote.  
` 4` **B:** Primero miro el disponible. ¿La tarjeta termina en 0942 o estás llamando por otra?  
` 5` **A:** En 0942, la de crédito.  
` 6` **B:** Gracias. Para identificarte, ¿me confirmás tu nombre completo y el mes de vencimiento de esa tarjeta? ← `REQUEST_PERSONAL_DATA`  
` 7` **A:** Tomás Ferreyra, vence en agosto del año que viene.  
` 8` **B:** Coincide. Tenés disponible 310 mil. La compra debería entrar dentro del límite actual.  
` 9` **A:** ¿Aunque sea en dólares? La página muestra el precio en moneda extranjera.  
`10` **B:** El sistema toma el equivalente al momento de autorizar, así que el margen puede variar. No puedo reservarte una cotización desde acá.  
`11` **A:** Claro. ¿Me conviene pedir aumento por las dudas?  
`12` **B:** Puedo iniciar una solicitud temporal, pero requiere evaluación y no necesariamente queda aprobada hoy.  
`13` **A:** No, entonces prefiero dejarlo así. Si no pasa, pago una parte con débito.  
`14` **B:** Está bien. ¿Querés que te explique dónde ver el consumo en la aplicación cuando se procese?  
`15` **A:** Sí, porque después aparecen dos montos y me mareo.  
`16` **B:** Entrás en tarjetas, tocás la que termina en 0942 y abrís “autorizaciones”. El consumo pendiente suele mostrarse antes del cierre.  
`17` **A:** Perfecto. ¿Me vas a mandar algo para confirmar la llamada?  
`18` **B:** Te queda una consulta registrada. En la app vas a ver el número 8821 dentro de movimientos de atención.  
`19` **A:** Ya lo anoté. No necesito cambiar nada entonces.  
`20` **B:** Exacto, la consulta no modifica el límite ni la tarjeta.  
`21` **A:** Bueno, gracias por tomarte el tiempo.  
`22` **B:** De nada. Buen viaje cuando llegue el viernes.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** L6 aporta una comprobación acotada («Gracias. Para identificarte, ¿me confirmás tu nombre completo y el mes de vencimiento de esa tarjeta?»). Contexto: La persona llama antes de viajar para consultar un límite; el agente pide una categoría de identificación y aclara el alcance del cambio. La prueba es juzgar el dato por su función, no por la presencia aislada de una solicitud.

**Notas de la referencia:** Referencia provisional; revisar la evidencia y sus límites en D07. Partición de desarrollo según propuesta pendiente de D08. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-L-BANCO-004

legitima · banco · pedido_razonable · 24 líneas

**Situación:** Una titular llama porque el depósito de un trabajo freelance no aparece; verifica identidad limitada y compara datos del envío.

` 1` **A:** Hola, estoy llamando yo. Me pagaron un trabajo ayer y todavía no lo veo acreditado.  
` 2` **B:** Buenas, vemos qué puede haber pasado. ¿Te dijeron desde qué banco salió?  
` 3` **A:** Desde una billetera, no sé el nombre exacto. El cliente me mandó una captura.  
` 4` **B:** ¿La transferencia estaba hecha a tu alias o a tu CBU?  
` 5` **A:** A mi alias, que es nube.mate. La cuenta está a mi nombre.  
` 6` **B:** ¿La captura muestra horario e importe?  
` 7` **A:** Sí, son 86.000 pesos a las 17:12. La fecha es de ayer.  
` 8` **B:** Para buscar ingresos pendientes, decime los últimos cuatro de la cuenta donde esperás recibirla. ← `REQUEST_PERSONAL_DATA`  
` 9` **A:** 3358.  
`10` **B:** Gracias. Veo una acreditación entrante de 86.000, pero todavía aparece en proceso. El banco emisor la liberó fuera del horario habitual.  
`11` **A:** ¿Puede quedar así hasta mañana? El cliente dice que ya salió.  
`12` **B:** Sí, algunas transferencias tardan en asentarse. Desde acá no podemos confirmar el estado del lado de la billetera.  
`13` **A:** ¿Te sirve que te diga el nombre que aparece como remitente?  
`14` **B:** Sí, solo el nombre que ves en el comprobante, si lo tenés a mano. ← `REQUEST_PERSONAL_DATA`  
`15` **A:** Dice Néstor Viale, que es el dueño del local donde hice el catálogo.  
`16` **B:** Coincide con el ingreso pendiente. ¿El alias de destino que figura en la captura es nube.mate?  
`17` **A:** Ahora que lo miro dice nube.mateo. Me comí una letra al pasárselo.  
`18` **B:** Ahí está la diferencia. El pago salió a otro alias, así que el banco no puede redirigirlo.  
`19` **A:** Qué macana. ¿Tengo que hacer algún reclamo acá?  
`20` **B:** No por este ingreso. Quien envió debe consultar con su proveedor y pedir la devolución al destinatario equivocado.  
`21` **A:** Le voy a avisar antes de que cierre el local. ¿Me queda alguna constancia de esta consulta?  
`22` **B:** Sí, quedó con el número 6402. No cambia nada en tu cuenta.  
`23` **A:** Gracias, me sirve para entender que no era una demora nomás.  
`24` **B:** De nada. Ojalá lo resuelvan rápido.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** L8 aporta una comprobación acotada («Para buscar ingresos pendientes, decime los últimos cuatro de la cuenta donde esperás recibirla.»). Contexto: Una titular llama porque el depósito de un trabajo freelance no aparece; verifica identidad limitada y compara datos del envío. La prueba es juzgar el dato por su función, no por la presencia aislada de una solicitud.

**Notas de la referencia:** Referencia provisional; revisar la evidencia y sus límites en D07. Partición de desarrollo según propuesta pendiente de D08. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-L-BANCO-005

legitima · banco · pedido_razonable · 24 líneas

**Situación:** Consulta saliente por una transferencia duplicada; se comparan importes y hora sin pedir claves ni códigos.

` 1` **A:** Buenas tardes, llamo yo porque veo dos veces el mismo pago del alquiler.  
` 2` **B:** Hola, vamos a revisar. ¿Es un débito automático o lo transferiste manualmente?  
` 3` **A:** Lo transferí desde el teléfono el lunes. El dueño dice que le entró una sola vez.  
` 4` **B:** ¿Los dos movimientos tienen el mismo importe?  
` 5` **A:** Sí, 145.000 cada uno. Uno dice 11:06 y el otro 11:08.  
` 6` **B:** ¿Ambos figuran completados o uno está pendiente?  
` 7` **A:** Uno completado y el otro en revisión. No sé por qué quedó así.  
` 8` **B:** Para encontrar la cuenta, me confirmás los últimos cuatro dígitos, por favor. ← `REQUEST_PERSONAL_DATA`  
` 9` **A:** 7210.  
`10` **B:** Gracias. ¿Podés leerme el concepto de los dos movimientos? ← _pedido_  
`11` **A:** El primero dice alquiler junio y el segundo no tiene concepto.  
`12` **B:** Veo que el segundo es una autorización que todavía no se confirmó. No es un débito asentado.  
`13` **A:** Ah, pero me baja el saldo disponible. Por eso pensé que me habían cobrado doble.  
`14` **B:** Entiendo. Cuando expire la autorización, el saldo se actualiza automáticamente. No puedo cancelarla mientras esté en ese estado.  
`15` **A:** ¿Cuánto puede tardar?  
`16` **B:** Hasta dos días hábiles, según la respuesta del otro banco.  
`17` **A:** El propietario me mandó el recibo, así que por lo menos sé que recibió uno.  
`18` **B:** Sí, en nuestro registro hay un solo movimiento completado hacia ese destinatario.  
`19` **A:** ¿La autorización pendiente puede volverse un segundo pago después?  
`20` **B:** En esta operación no: el sistema la marca como intento duplicado y espera que expire.  
`21` **A:** Bueno, voy a revisar mañana. Si sigue igual, vuelvo a llamar.  
`22` **B:** Dale. Queda registrada la consulta con el número 3915.  
`23` **A:** Gracias, me quedo más tranquila con el detalle.  
`24` **B:** A vos. Buenas tardes.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** L8 aporta una comprobación acotada («Para encontrar la cuenta, me confirmás los últimos cuatro dígitos, por favor.»). Contexto: Consulta saliente por una transferencia duplicada; se comparan importes y hora sin pedir claves ni códigos. La prueba es juzgar el dato por su función, no por la presencia aislada de una solicitud.

**Notas de la referencia:** Referencia provisional; revisar la evidencia y sus límites en D07. Partición de desarrollo según propuesta pendiente de D08. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-L-BANCO-006

legitima · banco · mencion_sin_pedido · 24 líneas

**Situación:** Mención incidental de un código de verificación recibido durante una consulta de saldo; nadie pide revelarlo.

` 1` **A:** Hola, llamo porque el saldo que me muestra la pantalla no coincide con mi cuenta.  
` 2` **B:** Buen día. ¿Qué importe esperabas ver?  
` 3` **A:** Unos 54 mil. Ayer cobré una changa y hoy aparecen 19 mil.  
` 4` **B:** ¿Tuviste algún gasto con tarjeta desde ayer?  
` 5` **A:** Compré remedios y pagué el gas. No me acuerdo los importes exactos.  
` 6` **B:** Podemos recorrer los últimos movimientos. ¿La cuenta termina en 2609?  
` 7` **A:** Sí, esa misma.  
` 8` **B:** Veo un pago de farmacia por 12.800 y uno de servicios por 21.340.  
` 9` **A:** Eso explica una parte. También me apareció un mensaje con un código cuando abrí la app, pero yo no estaba entrando. ← _mencion_  
`10` **B:** ¿Te llegó como notificación del banco o como mensaje de texto?  
`11` **A:** Como notificación. Después cerré la aplicación porque pensé que toqué algo sin querer.  
`12` **B:** El mensaje no figura como ingreso validado de sesión. Revisá si tenés la app abierta en otro dispositivo.  
`13` **A:** La tengo en la tablet, pero hace meses que no la uso.  
`14` **B:** Podés cerrar esa sesión desde el menú de seguridad cuando tengas la tablet a mano.  
`15` **A:** ¿Eso me cambia la clave? ← _mencion_  
`16` **B:** No. Solo termina esa sesión. Si querés cambiar la clave, hacelo después desde la aplicación. ← _mencion_  
`17` **A:** Entiendo. ¿El saldo restante puede ser una compra pendiente?  
`18` **B:** Hay una autorización de combustible por 8.500 que todavía no se asentó.  
`19` **A:** Ah, cargué en la ruta el domingo. No lo había relacionado.  
`20` **B:** Cuando se cierre, el saldo disponible se ajusta. El movimiento debería aparecer con el nombre de la estación.  
`21` **A:** Bien. Me voy a fijar en la tablet esta noche.  
`22` **B:** Te registro la consulta así queda asentado el problema de la notificación.  
`23` **A:** Dale, gracias. Lo hago cuando llegue a casa. ← _mencion_  
`24` **B:** No, con contarme que apareció alcanza.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** En L9 aparece «Eso explica una parte. También me apareció un mensaje con un código cuando abrí la app, pero yo no estaba entrando.» dentro de la consulta, sin que nadie pida repetirlo ni compartirlo. El caso prueba si se distingue una mención de código o clave de una solicitud observable.

**Notas de la referencia:** Referencia provisional; revisar la evidencia y sus límites en D07. Partición de desarrollo según propuesta pendiente de D08. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-L-BANCO-007

legitima · banco · mencion_sin_pedido · **en la matriz #101** · **propuesto para grabar** · 23 líneas

**Situación:** Consulta de la persona sobre una palabra “clave” impresa en un resumen; se aclara que es una referencia propia del documento.

` 1` **A:** Llamo por el resumen de la tarjeta. Hay una línea que dice “clave de comercio” y no entiendo qué significa. ← _mencion_  
` 2` **B:** Buenas, ¿la ves dentro del detalle de un consumo?  
` 3` **A:** Sí, al lado de una compra en una librería. Dice CLAVE 04, nada más. ← _mencion_  
` 4` **B:** Eso puede ser la descripción que envió el local. ¿Qué importe figura?  
` 5` **A:** 6.240 pesos. El sábado compré cuadernos y una carpeta.  
` 6` **B:** ¿Coincide con lo que pagaste?  
` 7` **A:** Más o menos. Creo que eran seis mil y algo.  
` 8` **B:** Entonces probablemente sea el mismo consumo. Estamos mirando solo el texto del resumen. ← _mencion_  
` 9` **A:** Claro, yo no estaba pensando en la clave de la cuenta. Me llamó la atención la palabra. ← _mencion_  
`10` **B:** Tiene sentido. A veces el nombre del comercio se corta o muestra una abreviatura interna.  
`11` **A:** ¿Puedo cambiar cómo se ve eso en la aplicación?  
`12` **B:** No desde el banco. La descripción viene informada por el negocio.  
`13` **A:** Bueno. Aprovecho y te pregunto por el pago mínimo, porque me cambió bastante.  
`14` **B:** El mes pasado tenías menos compras en cuotas. ¿Querés que comparemos el detalle?  
`15` **A:** Sí, me gustaría entenderlo antes del vencimiento.  
`16` **B:** Veo dos cuotas nuevas de la heladera y una compra en tres pagos de la farmacia.  
`17` **A:** La heladera sí, pero la farmacia la pagué de una. ¿Puede estar mal?  
`18` **B:** La farmacia aparece como un solo consumo, sin cuotas. Capaz estás viendo el total financiado de otra compra.  
`19` **A:** Ahí encontré la línea, dice ferretería, no farmacia. Es por una caja de herramientas.  
`20` **B:** Entonces coincide con lo que recordás. El resumen cierra el jueves.  
`21` **A:** Listo. Gracias por ayudarme a leerlo.  
`22` **B:** De nada. ¿Queda alguna otra consulta?  
`23` **A:** No, eso era todo.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** En L1 aparece «Llamo por el resumen de la tarjeta. Hay una línea que dice “clave de comercio” y no entiendo qué significa.» dentro de la consulta, sin que nadie pida repetirlo ni compartirlo. El caso prueba si se distingue una mención de código o clave de una solicitud observable.

**Notas de la referencia:** Referencia provisional; revisar la evidencia y sus límites en D07. Partición de desarrollo según propuesta pendiente de D08. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-L-BANCO-008

legitima · banco · mencion_sin_pedido · 21 líneas

**Situación:** La persona consulta por un cajero que rechazó billetes; la palabra “clave” aparece en una anécdota ajena, sin pedido.

` 1` **A:** Hola. Quería saber si puedo depositar billetes de otra serie en el cajero.  
` 2` **B:** Buenas. ¿El cajero los rechazó o todavía no probaste?  
` 3` **A:** Rechazó dos. En casa me dijeron que capaz tenían una clave marcada, pero no sé qué significa eso. ← _mencion_  
` 4` **B:** La máquina suele rechazarlos si están rotos, pegados o demasiado gastados. ¿El cajero mostró alguna explicación en pantalla? ← _mencion_  
` 5` **A:** Están enteros, aunque uno tiene una mancha de tinta en una punta.  
` 6` **B:** Puede ser eso. ¿El depósito era para una cuenta propia?  
` 7` **A:** Sí, la mía. Llevé varios porque me pagaron en efectivo.  
` 8` **B:** Si tenés sucursal cerca, podés consultar si reciben esos billetes por caja. No hace falta llevarlos todos juntos.  
` 9` **A:** Me queda lejos. ¿Hay algún cajero que acepte más billetes por vez?  
`10` **B:** En la aplicación podés ver qué equipos tienen depósito, pero no muestra el estado de cada lector.  
`11` **A:** ¿Y si pruebo en otro cajero del mismo banco?  
`12` **B:** Podés, aunque si tienen la misma condición de lectura quizás vuelva a rechazarlos.  
`13` **A:** Bueno. No quería que se me quedaran dentro de la máquina.  
`14` **B:** Cuando el cajero rechaza uno, lo devuelve en la bandeja. ¿Te devolvió los dos?  
`15` **A:** Sí, los agarré antes de que cerrara la compuerta.  
`16` **B:** Perfecto. ¿Tenés el comprobante del intento?  
`17` **A:** No, porque no llegó a iniciar el depósito.  
`18` **B:** Entonces no hay un movimiento que reclamar. Probá con los billetes en mejor estado o consultá en caja.  
`19` **A:** Voy a ver si puedo pasar el jueves. No es urgente.  
`20` **B:** Dale. Si cambia algo, llamanos con el horario aproximado.  
`21` **A:** Gracias por la orientación.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** En L3 aparece «Rechazó dos. En casa me dijeron que capaz tenían una clave marcada, pero no sé qué significa eso.» dentro de la consulta, sin que nadie pida repetirlo ni compartirlo. El caso prueba si se distingue una mención de código o clave de una solicitud observable.

**Notas de la referencia:** Referencia provisional; revisar la evidencia y sus límites en D07. Partición de desarrollo según propuesta pendiente de D08. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-L-BANCO-009

legitima · banco · mencion_sin_pedido · 22 líneas

**Situación:** Una clienta consulta cómo revertir una compra autorizada que no se asentó; menciona el PIN de su tarjeta como recuerdo, sin dictarlo.

` 1` **A:** Buenas, me aparece una compra de ayer como pendiente y el negocio dice que la canceló.  
` 2` **B:** Hola, ¿fue con tarjeta de débito o crédito?  
` 3` **A:** Débito, en una casa de decoración. La vendedora probó dos veces porque la primera pantalla quedó congelada.  
` 4` **B:** ¿Ves dos movimientos o uno solo?  
` 5` **A:** Uno pendiente por 27.900. Me acuerdo que marqué el PIN y después quedó cargando. ← _mencion_  
` 6` **B:** Gracias. ¿El local te entregó un recibo de cancelación? ← _mencion_  
` 7` **A:** Sí, un papelito que dice operación anulada.  
` 8` **B:** ¿Tiene fecha y últimos dígitos de la tarjeta?  
` 9` **A:** Tiene fecha de ayer y termina en 4086.  
`10` **B:** Coincide con el movimiento que aparece acá. La autorización está pendiente y debería liberarse sola.  
`11` **A:** ¿El local tiene que hacer algo más?  
`12` **B:** Si emitieron la anulación, deberían conservar el comprobante. Si el débito se asienta, podés iniciar un reclamo con ese papel.  
`13` **A:** ¿Cuántos días espero antes de llamar de nuevo?  
`14` **B:** Revisá en 48 horas hábiles. El sistema actualiza según el cierre del comercio.  
`15` **A:** Está bien. Lo que me preocupaba era que la vendedora me hizo intentar dos veces.  
`16` **B:** En el registro hay una sola autorización, no aparecen dos cargos.  
`17` **A:** Qué bueno. Guardé el papel con la factura.  
`18` **B:** Te dejo anotado que consultaste por la operación pendiente, así tenemos el contexto.  
`19` **A:** Perfecto. ¿Me mandan una confirmación?  
`20` **B:** Te figura en la sección de atención, con referencia 5140.  
`21` **A:** Ya la veo. Gracias.  
`22` **B:** A vos. Que tengas buena tarde.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** En L5 aparece «Uno pendiente por 27.900. Me acuerdo que marqué el PIN y después quedó cargando.» dentro de la consulta, sin que nadie pida repetirlo ni compartirlo. El caso prueba si se distingue una mención de código o clave de una solicitud observable.

**Notas de la referencia:** Referencia provisional; revisar la evidencia y sus límites en D07. Partición de desarrollo según propuesta pendiente de D08. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-L-BANCO-010

legitima · banco · mencion_sin_pedido · con errores escritos de ASR · 25 líneas

**Situación:** Llamado iniciado por una jubilada ficticia que pregunta por “clave fiscal” en un trámite contable; el banco deriva sin pedir credenciales.

` 1` **A:** no se si eso se saca acá ← _mencion_  
` 2` **B:** buenas tardes la constancia es de una cuenta bancaria o de un trámite impositivo  
` 3` **A:** de un trámite impositivo creo que para justificar un pago yo con esas cosas me pierdo  
` 4` **B:** la clave fiscal corresponde al organismo tributario no al banco ← _mencion_  
` 5` **A:** entonces el banco no me la puede recuperar  
` 6` **B:** no porque no la administramos si querés te digo dónde encontrar el comprobante de la transferencia que hiciste  
` 7` **A:** eso sí me vendría bien le pagué a la contadora el martes  
` 8` **B:** recordás el monto aproximado  
` 9` **A:** cuarenta y dos mil fue desde la cuenta donde cobro la jubilación  
`10` **B:** para ubicarla confirmame los últimos cuatro números de esa cuenta  
`11` **A:** 9903  
`12` **B:** veo una transferencia de 42000 a nombre de paula virel es tu contadora  
`13` **A:** sí correcto la conozco hace bastante  
`14` **B:** en el detalle tenés la opción ver comprobante podés guardarlo o compartirlo desde ahí  
`15` **A:** si lo comparto se manda directo a ella  
`16` **B:** no hasta que elijas el contacto primero te muestra una vista previa  
`17` **A:** bien no quiero mandarlo al grupo de la familia por equivocación  
`18` **B:** podés guardarlo como archivo y después adjuntarlo al correo que ya usás con ella  
`19` **A:** mejor hago eso la clave que mencionó ella puede ser la de la cuenta del banco ← _mencion_  
`20` **B:** son claves distintas para el trámite preguntale cuál necesita pero no compartas la clave bancaria ← _mencion_  
`21` **A:** sí eso lo tengo claro solo quería saber si el banco emitía esa constancia  
`22` **B:** la constancia de transferencia sí la clave fiscal no ← _mencion_  
`23` **A:** listo ya encontré el botón gracias por la paciencia  
`24` **B:** no hay problema terminamos  
`25` **A:** sí muchas gracias  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** En L1 aparece «no se si eso se saca acá» dentro de la consulta, sin que nadie pida repetirlo ni compartirlo. El caso prueba si se distingue una mención de código o clave de una solicitud observable.

**Notas de la referencia:** Referencia provisional; revisar la evidencia y sus límites en D07. Partición de desarrollo según propuesta pendiente de D08. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-L-DELIVERY-001

legitima · delivery · cotidiana · con errores escritos de ASR · **en la matriz #101** · 24 líneas

**Situación:** Una persona que espera un paquete llama a la tienda porque la dirección tiene una referencia incompleta; confirma ubicación y franja horaria.

` 1` **A:** hola llamo por el pedido de una pava electrica la entrega figura para hoy pero falta el departamento ← _contexto_  
` 2` **B:** buen día tenés el número de compra  
` 3` **A:** es 63018 lo hice con el correo de mi pareja pero el domicilio es el mío  
` 4` **B:** encontré el pedido la dirección dice calle lapacho 220 sin piso ni departamento  
` 5` **A:** es segundo b edificio del portón gris entre la farmacia y la plaza  
` 6` **B:** el timbre tiene tu apellido o el de tu pareja  
` 7` **A:** tiene el de mi pareja ocampo yo estoy en el trabajo hasta las cuatro  
` 8` **B:** la entrega está asignada entre las dos y las seis  
` 9` **A:** puedo cambiarla para después de las cinco mi vecina puede recibirla si la autorizo  
`10` **B:** puedo dejar asentado que consulten en portería pero el repartidor define el recorrido  
`11` **A:** en el edificio no hay portería te paso el número de la vecina  
`12` **B:** si ella acepta podemos agregar un teléfono de contacto para esta entrega  
`13` **A:** sí me dijo que está en casa hasta las seis termina en 63  
`14` **B:** lo agrego como referencia temporal querés que la llamen antes de subir  
`15` **A:** sí así baja a abrirles no le dejen el paquete en el pasillo  
`16` **B:** queda indicado el paquete requiere firma de quien lo recibe  
`17` **A:** puede firmar con su nombre aunque la compra esté a nombre de ocampo  
`18` **B:** sí anotamos que es una persona autorizada por vos  
`19` **A:** bueno me llega el cambio por correo  
`20` **B:** sí mandamos una actualización al correo de la compra  
`21` **A:** ya entró dice que agregaron segundo b y el contacto  
`22` **B:** perfecto querés que revise algo más  
`23` **A:** no con eso alcanza gracias por la ayuda  
`24` **B:** que llegue bien el pedido  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** La apertura «hola llamo por el pedido de una pava electrica la entrega figura para hoy pero falta el departamento» (L1) da paso a una gestión cotidiana. Contexto: Una persona que espera un paquete llama a la tienda porque la dirección tiene una referencia incompleta; confirma ubicación y franja horaria. La prueba es reconocer acuerdos ordinarios aunque incluyan intercambio de datos, horarios o gastos.

**Notas de la referencia:** Referencia provisional; revisar la evidencia y sus límites en D07. Partición según propuesta pendiente de D08. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-L-DELIVERY-002

legitima · delivery · cotidiana · 25 líneas

**Situación:** Una clienta coordina con el comercio una ventana de entrega de verduras frescas y da instrucciones sobre sustituciones y acceso al edificio.

` 1` **A:** Buenas, quería consultar si el cajón de verduras sale hoy o mañana. ← _contexto_  
` 2` **B:** Hola. ¿El pedido está a nombre de quién?  
` 3` **A:** De Pilar Sosa. Lo hice anoche desde la página del mercado.  
` 4` **B:** Veo que está preparado para el turno de la tarde.  
` 5` **A:** ¿Más o menos a qué hora? Tengo que salir a buscar a los chicos.  
` 6` **B:** El recorrido va de cuatro a siete, no tenemos una hora exacta.  
` 7` **A:** ¿Se puede dejar con el kiosquero de la esquina si no estoy?  
` 8` **B:** Podemos anotarlo, pero necesitamos que vos confirmes que lo acepta.  
` 9` **A:** Ya le pregunté. Me dijo que sí, mientras el cajón esté cerrado.  
`10` **B:** ¿Querés que se lo entreguen a nombre del kiosco o que te llamen primero?  
`11` **A:** Mejor que me llamen. Si estoy a diez minutos vuelvo y lo recibo.  
`12` **B:** Para contactar al repartidor, ¿el número termina en 51?  
`13` **A:** Sí, es el mío.  
`14` **B:** También veo que pediste tomates maduros. Si no hay, ¿preferís que los cambien por perita o que los saquen?  
`15` **A:** Perita está bien, pero que no reemplacen la rúcula. Esa sí la necesito para la cena.  
`16` **B:** Dejo anotado: reemplazo solo de tomate, no de rúcula.  
`17` **A:** ¿La bolsa de papas viene separada? Voy a llevar el pedido en colectivo.  
`18` **B:** Sí, viene en una bolsa aparte para que sea más fácil.  
`19` **A:** Perfecto. ¿Puedo pagar la diferencia del reemplazo cuando llegue?  
`20` **B:** Si cambia el precio, te avisamos antes de cerrar el pedido. No hace falta que adelantes nada.  
`21` **A:** Ya pagué con la tarjeta, pero no vi si quedó confirmado.  
`22` **B:** Figura aprobado. El detalle aparece en tu cuenta del mercado.  
`23` **A:** Listo, entonces espero el llamado.  
`24` **B:** Gracias por confirmar lo del kiosco.  
`25` **A:** Gracias a vos. Hasta luego.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** La apertura «Buenas, quería consultar si el cajón de verduras sale hoy o mañana.» (L1) da paso a una gestión cotidiana. Contexto: Una clienta coordina con el comercio una ventana de entrega de verduras frescas y da instrucciones sobre sustituciones y acceso al edificio. La prueba es reconocer acuerdos ordinarios aunque incluyan intercambio de datos, horarios o gastos.

**Notas de la referencia:** Referencia provisional; revisar la evidencia y sus límites en D07. Partición según propuesta pendiente de D08. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-L-DELIVERY-003

legitima · delivery · cotidiana · con errores escritos de ASR · 25 líneas

**Situación:** Un vecino recibe por error una bolsa de comida preparada y llama al local para coordinar el retiro y la entrega correcta; se registran dirección y referencia.

` 1` **A:** hola me dejaron una bolsa del restaurante que no es para mí ← _contexto_  
` 2` **B:** buenas tiene una etiqueta con el nombre del pedido  
` 3` **A:** dice nora y yo soy damián vivo en el 4 c  
` 4` **B:** la bolsa está cerrada  
` 5` **A:** sí no la abrí el repartidor ya se fue cuando vi el nombre  
` 6` **B:** me decís la dirección del edificio para ubicar el recorrido  
` 7` **A:** es lapacho 220 torre dos la entrada está por la calle angosta  
` 8` **B:** gracias el pedido de nora era para el 3 c en la torre uno  
` 9` **A:** claro las dos torres tienen el mismo número la persona de abajo me tocó el timbre y me la dejó  
`10` **B:** podés dejar la bolsa en la heladera mientras mandamos a alguien  
`11` **A:** sí pero no quiero que se enfríe la bebida está en una bolsa aparte  
`12` **B:** la comida es fría así que no hay problema la bebida va en otra entrega  
`13` **A:** la retiro yo en el local o pasan por acá  
`14` **B:** mandamos al repartidor de vuelta hay alguien en tu departamento durante la próxima media hora  
`15` **A:** yo estoy hasta las cinco después se queda mi compañero  
`16` **B:** querés que lo llamemos antes de subir  
`17` **A:** sí mejor él trabaja desde casa y puede abrir  
`18` **B:** me confirmás su nombre para dejarlo en la nota  
`19` **A:** se llama iván pero el apellido no hace falta que toque el 4 c  
`20` **B:** anotado el repartidor va a retirar la bolsa y subir al 3 c  
`21` **A:** le digo algo a nora si la cruzo  
`22` **B:** solo que ya coordinamos el cambio no hace falta que abra el paquete  
`23` **A:** dale sigue en la heladera intacta  
`24` **B:** gracias por avisarnos rápido te mandamos una notificación cuando quede resuelto  
`25` **A:** perfecto espero el timbre  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** La apertura «hola me dejaron una bolsa del restaurante que no es para mí» (L1) da paso a una gestión cotidiana. Contexto: Un vecino recibe por error una bolsa de comida preparada y llama al local para coordinar el retiro y la entrega correcta; se registran dirección y referencia. La prueba es reconocer acuerdos ordinarios aunque incluyan intercambio de datos, horarios o gastos.

**Notas de la referencia:** Referencia provisional; revisar la evidencia y sus límites en D07. Partición según propuesta pendiente de D08. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-L-DELIVERY-004

legitima · delivery · cotidiana · **propuesto para grabar** · 24 líneas

**Situación:** La persona pide reprogramar la entrega de una mesa por una obra en el pasillo; se consulta disponibilidad y se acuerda una nueva fecha.

` 1` **A:** Buen día, necesito cambiar la entrega de la mesa que compré. Están pintando el pasillo. ← _contexto_  
` 2` **B:** Hola. ¿Tenés el número de pedido?  
` 3` **A:** 44192. La entrega estaba para mañana a la mañana.  
` 4` **B:** Veo una mesa plegable, a nombre de Renzo Lamas. ¿Es esa?  
` 5` **A:** Sí. El pintor dice que no se puede apoyar nada hasta el viernes.  
` 6` **B:** Puedo revisar los próximos turnos. ¿Te sirve el sábado?  
` 7` **A:** Sí, después del mediodía. A la mañana no hay nadie en casa.  
` 8` **B:** Hay una franja entre las dos y las seis.  
` 9` **A:** ¿La mesa viene armada o en caja? Necesito saber si entra por el ascensor.  
`10` **B:** Viene en caja plana, mide un metro veinte de largo.  
`11` **A:** Entra. El ascensor es chico, pero no tanto.  
`12` **B:** ¿Querés agregar una referencia de acceso para el edificio?  
`13` **A:** Sí, hay que entrar por la puerta de la cochera, porque el frente va a estar cerrado por la pintura.  
`14` **B:** ¿El repartidor puede llamar al llegar?  
`15` **A:** Sí, al número asociado al pedido. Estoy en casa desde la una.  
`16` **B:** Cambio la fecha al sábado y dejo la referencia de la cochera.  
`17` **A:** ¿Me cobran por reprogramar?  
`18` **B:** No, el pedido todavía no salió a reparto.  
`19` **A:** Bien. ¿La factura queda con la fecha original de compra?  
`20` **B:** Sí, eso no cambia. Solo se modifica la entrega.  
`21` **A:** Ya me llegó el correo, dice sábado 14. Gracias por confirmarlo.  
`22` **B:** De nada. ¿Necesitás revisar otro producto?  
`23` **A:** No, era solo la mesa.  
`24` **B:** Perfecto, que salga bien la pintura.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** La apertura «Buen día, necesito cambiar la entrega de la mesa que compré. Están pintando el pasillo.» (L1) da paso a una gestión cotidiana. Contexto: La persona pide reprogramar la entrega de una mesa por una obra en el pasillo; se consulta disponibilidad y se acuerda una nueva fecha. La prueba es reconocer acuerdos ordinarios aunque incluyan intercambio de datos, horarios o gastos.

**Notas de la referencia:** Referencia provisional; revisar la evidencia y sus límites en D07. Partición según propuesta pendiente de D08. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-L-DELIVERY-005

legitima · delivery · cotidiana · 25 líneas

**Situación:** El comercio llama para confirmar el punto de entrega de un pedido grande de bebidas; la clienta corrige el acceso y decide si aceptar un cambio de producto.

` 1` **A:** Hola, soy yo. Me llegó un aviso de que no encontraron la entrada para el pedido. ← _contexto_  
` 2` **B:** Sí, el repartidor está en la cuadra pero la dirección tiene dos accesos.  
` 3` **A:** Tiene que entrar por el portón de la calle Mitre, no por el estacionamiento.  
` 4` **B:** ¿Es el edificio de ladrillo claro, frente a la cancha?  
` 5` **A:** Exacto. La puerta chica da al pasillo de las casas.  
` 6` **B:** ¿Podés bajar a recibirlo o dejamos las cajas en la puerta?  
` 7` **A:** Bajo en cinco minutos. Son seis cajas de bebidas y no quiero que queden afuera.  
` 8` **B:** El pedido incluye soda y agua saborizada. ¿Te mantenemos todo igual?  
` 9` **A:** Si no hay la de pomelo, puede ser limón. La de naranja sí la necesito.  
`10` **B:** Anoto el reemplazo. ¿El importe cambia si falta un sabor?  
`11` **A:** No sé, yo pagué un total cerrado en la página.  
`12` **B:** Si el precio cambia, el comercio te consulta antes de completar la entrega.  
`13` **A:** Bueno. ¿El repartidor puede esperar cinco minutos?  
`14` **B:** Le aviso ahora. ¿La dirección del pedido termina en 180?  
`15` **A:** Sí, 180, casa dos. El portón tiene un timbre que no anda.  
`16` **B:** Entonces va a golpear la puerta de madera.  
`17` **A:** Ya bajé. Estoy en la vereda, vestido con campera verde.  
`18` **B:** Lo veo, el repartidor se acerca por la esquina.  
`19` **A:** Sí, ahí lo encontré. Me confirma que tiene las seis cajas.  
`20` **B:** ¿Está todo bien con los sabores?  
`21` **A:** Trajo pomelo al final. Mejor, porque era el que querían para la reunión.  
`22` **B:** Perfecto. ¿Te llegó el comprobante?  
`23` **A:** Sí, me aparece en el correo.  
`24` **B:** Gracias por resolverlo con nosotros.  
`25` **A:** A ustedes, ya está todo recibido.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** La apertura «Hola, soy yo. Me llegó un aviso de que no encontraron la entrada para el pedido.» (L1) da paso a una gestión cotidiana. Contexto: El comercio llama para confirmar el punto de entrega de un pedido grande de bebidas; la clienta corrige el acceso y decide si aceptar un cambio de producto. La prueba es reconocer acuerdos ordinarios aunque incluyan intercambio de datos, horarios o gastos.

**Notas de la referencia:** Referencia provisional; revisar la evidencia y sus límites en D07. Partición según propuesta pendiente de D08. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-L-ESCUELA-001

legitima · escuela · cotidiana · **en la matriz #101** · **propuesto para grabar** · 24 líneas

**Situación:** Dos personas responsables coordinan una reunión escolar por un conflicto menor en el recreo; se acuerda el horario y quién asistirá.

` 1` **A:** Hola, soy el papá de Nina. Me dejaron un mensaje para coordinar una reunión. ← _contexto_  
` 2` **B:** Buenas tardes. Sí, queríamos conversar sobre cómo se está integrando al grupo.  
` 3` **A:** ¿Pasó algo hoy en el recreo? La noté callada cuando salió.  
` 4` **B:** Hubo un desacuerdo por un juego, pero no hubo golpes ni se lastimó nadie.  
` 5` **A:** ¿Ella discutió con alguna compañera?  
` 6` **B:** Se enojó porque cambiaron las reglas y se fue a leer a un banco.  
` 7` **A:** En casa también se frustra cuando siente que no la escuchan.  
` 8` **B:** Queremos saber qué estrategias le funcionan y compartir lo que vemos en la escuela.  
` 9` **A:** Está bien. ¿La reunión puede ser después de las cuatro? Trabajo hasta esa hora.  
`10` **B:** El miércoles a las cuatro y media puede la maestra y la orientadora.  
`11` **A:** Sí, me sirve. ¿Tengo que ir con la mamá o puede ir uno solo?  
`12` **B:** Puede venir cualquiera de las dos personas responsables. Si pueden venir ambos, mejor, pero no es obligatorio.  
`13` **A:** Le pregunto a ella. ¿La reunión es en el aula o en dirección?  
`14` **B:** En el aula de tercer grado, al lado de la biblioteca.  
`15` **A:** ¿Hay que avisar en recepción cuando lleguemos?  
`16` **B:** Sí, firman la entrada y esperan a la maestra en el patio cubierto.  
`17` **A:** Perfecto. ¿Me mandan la citación por el cuaderno?  
`18` **B:** Sí, va a ir una nota para que quede asentada la fecha.  
`19` **A:** La revisamos esta noche. No quiero que Nina piense que hizo algo grave.  
`20` **B:** Vamos a explicarle que es una conversación para acompañarla, no un reto.  
`21` **A:** Gracias. ¿La pueden dejar salir con su tía mañana como siempre?  
`22` **B:** Sí, su tía figura autorizada para retirarla.  
`23` **A:** Buenísimo. Queda confirmado miércoles cuatro y media.  
`24` **B:** Así es. Nos vemos entonces.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** La apertura «Hola, soy el papá de Nina. Me dejaron un mensaje para coordinar una reunión.» (L1) da paso a una gestión cotidiana. Contexto: Dos personas responsables coordinan una reunión escolar por un conflicto menor en el recreo; se acuerda el horario y quién asistirá. La prueba es reconocer acuerdos ordinarios aunque incluyan intercambio de datos, horarios o gastos.

**Notas de la referencia:** Referencia provisional; revisar la evidencia y sus límites en D07. Partición según propuesta pendiente de D08. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-L-ESCUELA-002

legitima · escuela · cotidiana · con errores escritos de ASR · 26 líneas

**Situación:** Una madre llama para informar que su hija olvidó un instrumento musical; la escuela confirma el horario de recepción y el nombre de quien lo entrega.

` 1` **A:** hola mi hija dejó el violín en casa y tiene ensayo después del almuerzo ← _contexto_  
` 2` **B:** buen día en qué grado está  
` 3` **A:** segundo año se llama milena paz ensaya con el grupo de la tarde  
` 4` **B:** puedo avisar en portería alguien puede acercarlo antes de la una  
` 5` **A:** sí voy yo en un rato lo dejo en recepción o se lo llevo al aula  
` 6` **B:** dejalo en recepción con una etiqueta con su nombre y curso  
` 7` **A:** el estuche es negro bastante grande lo van a guardar en algún armario  
` 8` **B:** sí lo dejamos detrás del mostrador para que no quede en el pasillo  
` 9` **A:** tengo que mostrar mi documento cuando lo entregue  
`10` **B:** no hace falta para dejar un objeto solo decí tu nombre y a quién va dirigido  
`11` **A:** soy carla paz la mamá  
`12` **B:** le mandamos un mensaje interno el ensayo empieza a las dos  
`13` **A:** llego antes de la una así que hay tiempo  
`14` **B:** milena tiene el instrumento asignado por la escuela o es de ella  
`15` **A:** es de ella lo compramos el año pasado en una tienda del centro  
`16` **B:** entonces lo registramos como objeto personal y se lo entregamos al grupo  
`17` **A:** puede retirarlo ella en el recreo  
`18` **B:** sí después de que recepción confirme que llegó  
`19` **A:** si no le avisan que pregunte en portería  
`20` **B:** lo anoto en la cartelera de avisos para el turno tarde  
`21` **A:** hay que firmar algo al dejarlo  
`22` **B:** no pero te damos un papelito con la hora por si lo necesitás  
`23` **A:** está bien ya salgo para allá  
`24` **B:** la entrada de familias es por la puerta de calle belgrano  
`25` **A:** sí conozco gracias por ayudarme  
`26` **B:** te esperamos  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** La apertura «hola mi hija dejó el violín en casa y tiene ensayo después del almuerzo» (L1) da paso a una gestión cotidiana. Contexto: Una madre llama para informar que su hija olvidó un instrumento musical; la escuela confirma el horario de recepción y el nombre de quien lo entrega. La prueba es reconocer acuerdos ordinarios aunque incluyan intercambio de datos, horarios o gastos.

**Notas de la referencia:** Referencia provisional; revisar la evidencia y sus límites en D07. Partición según propuesta pendiente de D08. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-L-ESCUELA-003

legitima · escuela · cotidiana · 24 líneas

**Situación:** Un padre consulta cómo justificar una ausencia por viaje familiar y acuerda enviar una nota con las fechas, sin que la escuela pida información ajena al trámite.

` 1` **A:** Buenas, quería preguntar cómo justifico que Tomás falte el viernes y el lunes. ← _contexto_  
` 2` **B:** Hola. ¿Es por una consulta médica o por un viaje?  
` 3` **A:** Vamos a visitar a mi mamá, que vive lejos. Salimos el jueves a la noche.  
` 4` **B:** En ese caso alcanza con una nota firmada por una persona responsable.  
` 5` **A:** ¿La mando por el cuaderno o por correo?  
` 6` **B:** Puede ser por el cuaderno. Si querés dejar constancia antes, mandala al correo de preceptoría.  
` 7` **A:** ¿Pongo los motivos del viaje o solo las fechas?  
` 8` **B:** Con las fechas y tu firma alcanza. No hace falta explicar detalles familiares.  
` 9` **A:** Bien. ¿A quién va dirigida?  
`10` **B:** A la preceptora de segundo B, que es el curso de Tomás.  
`11` **A:** ¿Tiene que recuperar una evaluación el viernes?  
`12` **B:** Sí, tiene una evaluación de ciencias. La docente coordinará la recuperación cuando vuelva.  
`13` **A:** ¿Le aviso directamente a la docente también?  
`14` **B:** Podés escribirle por el cuaderno para que prepare otra fecha.  
`15` **A:** No quiero que pierda el tema. ¿Hay una guía para llevar?  
`16` **B:** Hay una actividad en el aula virtual, pero se puede entregar la semana siguiente.  
`17` **A:** ¿Necesita una autorización especial para entrar el martes?  
`18` **B:** No, vuelve a su horario habitual. Solo presentá la nota.  
`19` **A:** Perfecto. ¿Me confirmás que figura en el curso correcto?  
`20` **B:** Sí, Tomás Varela, segundo B.  
`21` **A:** Es él. Gracias por orientarme.  
`22` **B:** De nada. Que tengan buen viaje.  
`23` **A:** Le aviso que lleve el cuaderno así no se atrasa.  
`24` **B:** Muy bien, hasta luego.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** La apertura «Buenas, quería preguntar cómo justifico que Tomás falte el viernes y el lunes.» (L1) da paso a una gestión cotidiana. Contexto: Un padre consulta cómo justificar una ausencia por viaje familiar y acuerda enviar una nota con las fechas, sin que la escuela pida información ajena al trámite. La prueba es reconocer acuerdos ordinarios aunque incluyan intercambio de datos, horarios o gastos.

**Notas de la referencia:** Referencia provisional; revisar la evidencia y sus límites en D07. Partición según propuesta pendiente de D08. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-L-ESCUELA-004

legitima · escuela · cotidiana · 26 líneas

**Situación:** Una estudiante adulta llama para corregir el correo que recibe avisos de una capacitación; se comprueba curso y se modifica el dato de contacto.

` 1` **A:** Hola, estoy haciendo el curso de auxiliar y los avisos me llegan a un correo que ya no uso. ← _contexto_  
` 2` **B:** Buen día. ¿En qué sede estás cursando?  
` 3` **A:** En la sede del barrio oeste, turno noche.  
` 4` **B:** ¿Me decís tu nombre y el nombre del curso?  
` 5` **A:** Nadia Peralta, auxiliar de biblioteca.  
` 6` **B:** Gracias. ¿Querés actualizar el correo en la ficha de estudiante?  
` 7` **A:** Sí. Ahora uso uno que empieza por nadia punto p y termina en correo ejemplo.  
` 8` **B:** ¿Me lo podés dictar completo para evitar un error?  
` 9` **A:** nadia punto peralta arroba correo ejemplo.  
`10` **B:** Lo tengo. ¿Querés que enviemos un mensaje de prueba para confirmar que funciona?  
`11` **A:** Sí, porque la semana pasada no vi el aviso de cambio de aula.  
`12` **B:** Ya salió. ¿Lo recibiste?  
`13` **A:** Todavía no. A veces tarda un rato.  
`14` **B:** ¿Revisaste la carpeta de correo no deseado?  
`15` **A:** Ahora llegó, estaba ahí. Lo marco como remitente conocido.  
`16` **B:** Bien. El próximo aviso va a salir por ese mismo canal.  
`17` **A:** ¿También mandan las notas por correo?  
`18` **B:** Las notas se consultan en el portal. El correo solo avisa cuando hay una actualización.  
`19` **A:** Ah, pensé que llegaban adjuntas.  
`20` **B:** No, por privacidad el detalle queda dentro del portal.  
`21` **A:** ¿Necesito cambiar mi usuario también?  
`22` **B:** No, el usuario sigue igual. Solo actualizamos el correo de contacto.  
`23` **A:** Perfecto. ¿Puedo pedir una constancia de asistencia del mes pasado?  
`24` **B:** Sí, completá el formulario de certificados y elegí el mes.  
`25` **A:** Lo hago después de clase. Gracias por corregir el dato.  
`26` **B:** De nada. Que tengas buena cursada.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** La apertura «Hola, estoy haciendo el curso de auxiliar y los avisos me llegan a un correo que ya no uso.» (L1) da paso a una gestión cotidiana. Contexto: Una estudiante adulta llama para corregir el correo que recibe avisos de una capacitación; se comprueba curso y se modifica el dato de contacto. La prueba es reconocer acuerdos ordinarios aunque incluyan intercambio de datos, horarios o gastos.

**Notas de la referencia:** Referencia provisional; revisar la evidencia y sus límites en D07. Partición según propuesta pendiente de D08. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-L-ESCUELA-005

legitima · escuela · cotidiana · con errores escritos de ASR · 26 líneas

**Situación:** Una escuela llama a una familia para coordinar una reunión por un proyecto de feria de ciencias; se aclaran materiales, horario y quién puede asistir.

` 1` **A:** buenas vi la nota de la feria de ciencias la reunión es para todos los cursos ← _contexto_  
` 2` **B:** hola es para las familias de cuarto grado que van a presentar experimentos  
` 3` **A:** mi hijo está en cuarto a puede ir él también o es solo para adultos  
` 4` **B:** puede acompañarte pero la explicación principal es para las personas responsables  
` 5` **A:** qué día la hacen  
` 6` **B:** el martes a las cinco y media en el laboratorio  
` 7` **A:** yo salgo del trabajo a las cinco llego con el colectivo en media hora  
` 8` **B:** si llegás unos minutos después no hay problema la charla dura cerca de cuarenta minutos  
` 9` **A:** hay que llevar algo para anotarse  
`10` **B:** solo completar la lista de asistencia que está en la entrada  
`11` **A:** y los materiales del proyecto los compramos antes de la reunión  
`12` **B:** no todavía primero vamos a explicar qué aporta la escuela y qué conviene traer de casa  
`13` **A:** mi hijo quiere hacer un filtro de agua con arena ese tema está permitido  
`14` **B:** sí mientras lo pruebe con agua limpia y no lo tome la docente les va a dar pautas de cuidado  
`15` **A:** la escuela tiene botellas transparentes o tenemos que llevar  
`16` **B:** hay algunas pero pueden traer una reutilizada para el grupo  
`17` **A:** le digo que lleve una el lunes quien va a estar en la reunión  
`18` **B:** la maestra y la profesora de ciencias  
`19` **A:** puedo ir yo sola o hace falta que vaya también su papá  
`20` **B:** puede asistir una sola persona responsable  
`21` **A:** bueno entonces voy yo la entrada es por el portón principal  
`22` **B:** sí avisen en recepción que vienen a la reunión de cuarto a  
`23` **A:** queda anotado martes cinco y media  
`24` **B:** te esperamos mandamos una nota de recordatorio el lunes  
`25` **A:** gracias por aclararme lo de los materiales  
`26` **B:** de nada hasta luego  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** La apertura «buenas vi la nota de la feria de ciencias la reunión es para todos los cursos» (L1) da paso a una gestión cotidiana. Contexto: Una escuela llama a una familia para coordinar una reunión por un proyecto de feria de ciencias; se aclaran materiales, horario y quién puede asistir. La prueba es reconocer acuerdos ordinarios aunque incluyan intercambio de datos, horarios o gastos.

**Notas de la referencia:** Referencia provisional; revisar la evidencia y sus límites en D07. Partición según propuesta pendiente de D08. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-L-FAMILIAR-001

legitima · familiar · cotidiana · **en la matriz #101** · 24 líneas

**Situación:** Coordinación de una visita familiar que cambia de horario por el cuidado de un abuelo; se negocian transporte y comida sin presión artificial.

` 1` **A:** ¿Seguís en el centro o ya saliste para lo de la abuela? ← _contexto_  
` 2` **B:** Estoy esperando el colectivo. Se demoró el que pasa por la plaza.  
` 3` **A:** Si querés te busco, pero tengo que pasar por la farmacia antes.  
` 4` **B:** No hace falta, el siguiente viene en diez minutos según la aplicación.  
` 5` **A:** ¿La farmacia era la de la esquina o la que está frente al hospital?  
` 6` **B:** La de la esquina. El remedio quedó encargado a nombre de Tere.  
` 7` **A:** Paso por ahí entonces. ¿Llevo algo para la merienda?  
` 8` **B:** Ella dijo que había hecho budín, pero si comprás leche nos viene bien.  
` 9` **A:** Dale. ¿La querés común o sin lactosa?  
`10` **B:** Sin lactosa, la azul. Yo llevo yerba y unas naranjas.  
`11` **A:** Bueno. ¿A qué hora querés que estemos allá?  
`12` **B:** Antes de las seis, porque después la cuidadora se va y hay que dejarle la cena preparada.  
`13` **A:** Llego cinco y cuarto, si no se hace mucho la cola.  
`14` **B:** Si ves que se demora, avisame y caliento yo la comida.  
`15` **A:** ¿La llave la tiene el vecino o quedó en la maceta?  
`16` **B:** La tiene el vecino. Ayer la dejé en su buzón y me dijo que la guardaba.  
`17` **A:** Le escribo cuando esté cerca. ¿Me mandás la dirección de la farmacia?  
`18` **B:** Es la de siempre, sobre San Martín, a mitad de cuadra.  
`19` **A:** Sí, ya sé cuál. ¿La abuela está mejor de la tos?  
`20` **B:** Mejor, pero no quiere quedarse sola después de anoche.  
`21` **A:** Entonces pasamos todos un rato. Mi nena sale del taller a las cinco.  
`22` **B:** Que venga también, le va a hacer bien verla.  
`23` **A:** Listo, llevo leche y paso por vos si todavía no llegó el colectivo.  
`24` **B:** Te aviso apenas suba. Gracias.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** La apertura «¿Seguís en el centro o ya saliste para lo de la abuela?» (L1) da paso a una gestión cotidiana. Contexto: Coordinación de una visita familiar que cambia de horario por el cuidado de un abuelo; se negocian transporte y comida sin presión artificial. La prueba es reconocer acuerdos ordinarios aunque incluyan intercambio de datos, horarios o gastos.

**Notas de la referencia:** Referencia provisional; revisar la evidencia y sus límites en D07. Partición según propuesta pendiente de D08. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-L-FAMILIAR-002

legitima · familiar · cotidiana · **propuesto para grabar** · 20 líneas

**Situación:** Dos familiares cierran el reparto de 46.800 pesos de supermercado entre cuatro personas y confirman una transferencia de 11.700.

` 1` **A:** Che, ¿pudiste mirar la cuenta de la torta y las cosas del cumple?  
` 2` **B:** Sí. El total del súper fue 46.800 y yo pagué todo con la tarjeta. ← _contexto_  
` 3` **A:** ¿Ahí está incluido el papel picado o eso lo compraste aparte?  
` 4` **B:** Está incluido. Los globos los llevó Juli, así que no entran en esa cuenta.  
` 5` **A:** Yo había anotado 42 mil. ¿Qué se sumó al final?  
` 6` **B:** Las bebidas y el hielo, que compramos cuando ya estábamos en el salón.  
` 7` **A:** Claro, no lo había sumado. ¿Cuánto me toca a mí?  
` 8` **B:** Somos cuatro: transferime 11.700 por tu parte cuando puedas. ← `REQUEST_TRANSFER`  
` 9` **A:** ¿Puede ser a la noche? Estoy en el médico con mamá.  
`10` **B:** Sí, el resumen vence la semana que viene, tenemos margen.  
`11` **A:** Pasame el alias por mensaje así no lo tengo que copiar de memoria.  
`12` **B:** Te lo mando en el chat familiar; es la cuenta donde juntamos lo del salón.  
`13` **A:** Sabés qué, pude abrir el banco mientras esperaba. Ya salió la transferencia por los 11.700. Avisame si entró. ← _cumplimiento_  
`14` **B:** Ahí llegó, queda saldada tu parte. ← _contexto_  
`15` **A:** ¿Me mandás también una foto del ticket para guardar el gasto?  
`16` **B:** Sí, te mando el ticket y el detalle separado entre comida y decoración.  
`17` **A:** Gracias. Los globos los arreglamos con Juli aparte entonces.  
`18` **B:** Eso, ella ya tiene el comprobante. Lo demás quedó cubierto entre los cuatro.  
`19` **A:** Perfecto. Después miro el detalle en casa.  
`20` **B:** Abrazo a mamá de mi parte.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** Transferencia familiar por una compra compartida ya realizada: cuatro aportes iguales de 11.700 completan 46.800 y se confirma una sola recepción. Prueba que una solicitud de dinero y su ejecución no bastan para llamar fraude a un acuerdo cotidiano.

**Notas de la referencia:** Referencia de trabajo D07 y reserva D08; sin revisión humana. La solicitud y la transferencia se registran como evidencia de una acción legítima; no se convierten en T_R/T_C de fraude. Se eliminó la promesa de un segundo pago que contradecía la recepción anterior. El ticket es de una compra ya realizada, no un pretexto para cobrar otra vez. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-L-FAMILIAR-003

legitima · familiar · cotidiana · 24 líneas

**Situación:** Dos primos organizan el traslado de una bicicleta para una sobrina; el cambio de plan se conversa con una tercera persona y se descarta un gasto innecesario.

` 1` **A:** ¿Tenés todavía la camioneta el sábado o la usa tu hermano? ← _contexto_  
` 2` **B:** La tengo hasta el mediodía. ¿Querés llevar la bici de Mora?  
` 3` **A:** Sí, me dijo que la necesita para la carrera del domingo. En el auto no entra.  
` 4` **B:** La puedo pasar a buscar por tu casa, pero antes tengo que dejar unas cajas.  
` 5` **A:** ¿A qué hora terminás con eso?  
` 6` **B:** Cerca de las diez. Si no se estira, llego a las diez y media.  
` 7` **A:** Mora tiene entrenamiento hasta las once. Capaz conviene llevarla al club directamente.  
` 8` **B:** ¿El club de la calle Roca o el predio nuevo?  
` 9` **A:** El predio nuevo. Ella me mandó la ubicación por el chat, te la reenvío.  
`10` **B:** Bueno. ¿La bicicleta está ajustada o necesita inflar las ruedas?  
`11` **A:** La trasera pierde aire. El abuelo dijo que tenía una cámara de repuesto.  
`12` **B:** No compremos una todavía. Primero miro la cámara que hay en el galpón.  
`13` **A:** Si está pinchada, la llevo al taller el viernes. No quiero que se quede sin entrenar.  
`14` **B:** Preguntale a Mora si la bici entra en la camioneta con el asiento de atrás puesto.  
`15` **A:** Ya le escribí. Dice que se puede sacar la rueda delantera.  
`16` **B:** Perfecto, así no hay que desarmar nada más.  
`17` **A:** ¿Querés que te dé para la nafta?  
`18` **B:** No, voy para ese lado igual. Después vemos si hace falta hacer otra vuelta.  
`19` **A:** Está bien. El sábado te espero en la puerta del predio.  
`20` **B:** Mejor decime cuando salgas, porque el GPS me manda por el camino de tierra.  
`21` **A:** Te paso una referencia: entrada por el portón verde, al lado del vivero.  
`22` **B:** Ahora sí, me ubico.  
`23` **A:** Gracias por hacer el traslado. La carrera le importa un montón.  
`24` **B:** No hay drama. Ojalá no llueva.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** La apertura «¿Tenés todavía la camioneta el sábado o la usa tu hermano?» (L1) da paso a una gestión cotidiana. Contexto: Dos primos organizan el traslado de una bicicleta para una sobrina; el cambio de plan se conversa con una tercera persona y se descarta un gasto innecesario. La prueba es reconocer acuerdos ordinarios aunque incluyan intercambio de datos, horarios o gastos.

**Notas de la referencia:** Referencia provisional; revisar la evidencia y sus límites en D07. Partición según propuesta pendiente de D08. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-L-FAMILIAR-004

legitima · familiar · cotidiana · 24 líneas

**Situación:** La hija avisa que no podrá pasar a cocinar y coordina con su padre una compra y el reparto de tareas para la semana.

` 1` **A:** Pa, te aviso que hoy no llego a cocinarte. Se alargó la reunión en el instituto. ← _contexto_  
` 2` **B:** No te preocupes, comí al mediodía. ¿Qué necesitabas dejar listo?  
` 3` **A:** La tarta para mañana y unas porciones para el freezer.  
` 4` **B:** Puedo poner la tarta en el horno cuando vuelva de caminar.  
` 5` **A:** Está en la heladera, en la fuente redonda. No la metas con el plástico.  
` 6` **B:** Me acuerdo. ¿Le pongo el horno bajo o medio?  
` 7` **A:** Bajo, unos veinte minutos. Mirala a los quince por las dudas.  
` 8` **B:** ¿Y las porciones del freezer?  
` 9` **A:** Esas las hago mañana a la tarde. Dejé las verduras lavadas en un recipiente.  
`10` **B:** ¿Tengo que comprar algo cuando pase por el almacén?  
`11` **A:** Sí, pan y un paquete de arroz. No hace falta que compres la leche, ya llevé ayer.  
`12` **B:** La que queda está casi vacía. ¿Querés que compre una igual?  
`13` **A:** Si encontrás sin lactosa, sí. Si no, dejalo para el sábado.  
`14` **B:** En el negocio de la esquina suelen tener. ¿Te mando una foto antes?  
`15` **A:** No hace falta, ya sabés cuál es la caja azul.  
`16` **B:** También puedo pasar por la verdulería. Se terminaron las manzanas.  
`17` **A:** Comprá cuatro nada más, que las otras siguen en la canasta.  
`18` **B:** ¿Te llevo algo a vos cuando vuelva?  
`19` **A:** No, salgo tarde y ceno en casa de una compañera.  
`20` **B:** Bueno. ¿Mañana venís a almorzar?  
`21` **A:** Sí, después de llevar a los chicos a la escuela.  
`22` **B:** Entonces guardo una porción para vos.  
`23` **A:** Dale, te llamo cuando salga. Gracias por resolver lo de la cena.  
`24` **B:** De nada, cuidate en la vuelta.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** La apertura «Pa, te aviso que hoy no llego a cocinarte. Se alargó la reunión en el instituto.» (L1) da paso a una gestión cotidiana. Contexto: La hija avisa que no podrá pasar a cocinar y coordina con su padre una compra y el reparto de tareas para la semana. La prueba es reconocer acuerdos ordinarios aunque incluyan intercambio de datos, horarios o gastos.

**Notas de la referencia:** Referencia provisional; revisar la evidencia y sus límites en D07. Partición según propuesta pendiente de D08. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-L-FAMILIAR-005

legitima · familiar · cotidiana · **propuesto para grabar** · 23 líneas

**Situación:** Tres familiares acuerdan cubrir una reparación de cocina mediante aportes diferentes a una cuenta común; uno transfiere y los otros dos quedan pendientes.

` 1` **A:** Hola, estoy mirando el presupuesto del plomero. ¿Qué parte quedó pendiente?  
` 2` **B:** El baño ya está pago. Falta la visita de la cocina, que fue ayer.  
` 3` **A:** ¿La del cambio de la llave de paso?  
` 4` **B:** Sí. Cobró 38.000 entre el repuesto y la mano de obra. ← _contexto_  
` 5` **A:** Mamá había anotado treinta. ¿El repuesto está sumado ahí?  
` 6` **B:** Sí, salió 9.500 y está separado en el recibo. El resto es el trabajo.  
` 7` **A:** Mandame la foto para guardarla con los gastos de la casa.  
` 8` **B:** Te la reenvío. ¿Podés transferir tu aporte esta semana? ← `REQUEST_TRANSFER`  
` 9` **A:** Tengo 15.000 disponibles ahora.  
`10` **B:** Poné esos 15.000; yo pongo 19.000 y mamá completa los 4.000 que faltan.  
`11` **A:** Así llegamos a los 38.000. ¿Todo va a la caja común?  
`12` **B:** Sí, la cuenta de mamá que usamos para los gastos compartidos.  
`13` **A:** Me aparece Elena Varo como titular.  
`14` **B:** Es esa. Mandá el comprobante al grupo de hermanos para que quede a la vista.  
`15` **A:** Ya salió la transferencia de 15.000 a esa cuenta. ← _cumplimiento_  
`16` **B:** Mamá confirmó que entró. Yo mando los 19.000 cuando salga de trabajar. ← _contexto_  
`17` **A:** Mi parte queda completa entonces; falta la tuya y la de ella.  
`18` **B:** Exacto, te marco como saldado en la planilla.  
`19` **A:** Hoy miré abajo de la pileta y no gotea.  
`20` **B:** Buenísimo. Si sigue seco, no hace falta otra visita.  
`21` **A:** Le paso también la foto del recibo a mamá para que vea el repuesto.  
`22` **B:** Dale, cuando estén los otros aportes cerramos el gasto.  
`23` **A:** Abrazo, después miro la planilla.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** Una reparación de 38.000 se cubre con aportes desiguales de 15.000, 19.000 y 4.000. Se paga solo la parte acordada y quedan otros aportes pendientes; prueba seguir quién debe cuánto sin confundir saldo familiar con presión fraudulenta.

**Notas de la referencia:** Referencia de trabajo D07 y reserva D08; sin revisión humana. Los aportes suman el importe de la reparación; no se vuelve a pedir un saldo a quien completó su parte. Pedido y cumplimiento son evidencia de una gestión legítima, con marcas críticas nulas. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-L-MEDICO-001

legitima · medico · cotidiana · **en la matriz #101** · 25 líneas

**Situación:** Una paciente llama para adelantar un control por un cambio de horario laboral; confirma su nombre y la fecha del turno, y evalúa alternativas.

` 1` **A:** Hola, tengo un control el jueves a las cuatro y me cambiaron el horario en el trabajo. ← _contexto_  
` 2` **B:** Buen día. ¿Me decís tu nombre y la fecha del turno?  
` 3` **A:** Ana Luján, jueves 12 de noviembre.  
` 4` **B:** Te encontré. ¿Querés pasarlo para otro día o buscar un horario más temprano?  
` 5` **A:** Si hay algo después de las seis, me sirve. Antes estoy en la oficina.  
` 6` **B:** El jueves no tenemos tarde. Hay un espacio el lunes a las seis y media.  
` 7` **A:** ¿Con la doctora Salvatierra también?  
` 8` **B:** Sí, con la misma profesional.  
` 9` **A:** El lunes tengo que llevar a mi papá a kinesiología. ¿Hay algo el martes?  
`10` **B:** Martes hay a las cinco, pero la consulta suele durar cuarenta minutos.  
`11` **A:** Puedo pedirle a una compañera que me cubra hasta las cinco. ¿Lo reservás mientras le pregunto?  
`12` **B:** Puedo dejarlo tentativo por diez minutos. Si no confirmás, se libera.  
`13` **A:** Le escribí y puede cubrirme. Tomo el martes.  
`14` **B:** Listo, queda para las cinco. ¿Tenés que llevar estudios nuevos?  
`15` **A:** Solo el análisis de sangre que me hice hace dos semanas.  
`16` **B:** Traé el informe impreso o mostralo desde el teléfono si lo recibiste en PDF.  
`17` **A:** Me lo mandó el laboratorio por correo. ¿Necesito reenviarlo al consultorio?  
`18` **B:** No hace falta ahora. La doctora lo revisa durante la consulta.  
`19` **A:** ¿Y el copago lo pago ahí o por transferencia?  
`20` **B:** En recepción aceptan efectivo y tarjeta. No hace falta abonar antes.  
`21` **A:** Perfecto. ¿Me mandan un recordatorio el día anterior?  
`22` **B:** Sí, suele llegar por mensaje de texto.  
`23` **A:** Bueno. Ya anoté martes 17 a las cinco.  
`24` **B:** Te llega la confirmación en unos minutos.  
`25` **A:** Gracias por encontrarme un horario.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** La apertura «Hola, tengo un control el jueves a las cuatro y me cambiaron el horario en el trabajo.» (L1) da paso a una gestión cotidiana. Contexto: Una paciente llama para adelantar un control por un cambio de horario laboral; confirma su nombre y la fecha del turno, y evalúa alternativas. La prueba es reconocer acuerdos ordinarios aunque incluyan intercambio de datos, horarios o gastos.

**Notas de la referencia:** Referencia provisional; revisar la evidencia y sus límites en D07. Partición según propuesta pendiente de D08. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-L-MEDICO-002

legitima · medico · cotidiana · con errores escritos de ASR · 26 líneas

**Situación:** Una persona llama por un resultado que no aparece en el portal; se verifica identidad con datos limitados y se explica que debe consultar al laboratorio.

` 1` **A:** hola me hice un análisis el viernes y todavía no veo el resultado en el portal ← _contexto_  
` 2` **B:** buenas fue en la sede de la avenida o en la del parque  
` 3` **A:** en la de la avenida temprano me dijeron que estaba para el lunes  
` 4` **B:** tenés el número de orden que te dieron  
` 5` **A:** sí 519-20 lo anoté atrás del recibo  
` 6` **B:** gracias a nombre de quién está la orden  
` 7` **A:** de marcos nieva soy yo  
` 8` **B:** acá figura que la muestra se recibió pero el resultado sigue en proceso  
` 9` **A:** puede haber salido mal la muestra me hicieron volver porque el primer tubo estaba bajo  
`10` **B:** no tengo el detalle técnico desde este teléfono puedo comunicarte con el laboratorio para que revisen la demora  
`11` **A:** sí por favor lo necesito para el turno del miércoles  
`12` **B:** ese turno es con la doctora que pidió el análisis  
`13` **A:** sí a las diez si no llega capaz me lo reprograma  
`14` **B:** el laboratorio atiende hasta las seis te paso interno 24 para consultar directamente  
`15` **A:** tengo que volver a dar mi documento cuando me atiendan  
`16` **B:** te pueden pedir confirmar nombre y fecha de nacimiento para abrir el registro  
`17` **A:** la fecha es el 4 de abril de 1989  
`18` **B:** gracias con eso aparece la orden no hace falta que me leas el documento completo  
`19` **A:** bueno el resultado me lo mandan por correo o tengo que buscarlo  
`20` **B:** si autorizaste el portal suele aparecer ahí el laboratorio te confirma el estado  
`21` **A:** me aparece una notificación pero cuando entro no carga  
`22` **B:** probá desde un navegador actualizado si sigue igual anotá el error que te muestra  
`23` **A:** dice carga interrumpida lo voy a probar en la computadora de casa  
`24` **B:** perfecto te transfiero ahora  
`25` **A:** si gracias  
`26` **B:** te paso al interno 24  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** La apertura «hola me hice un análisis el viernes y todavía no veo el resultado en el portal» (L1) da paso a una gestión cotidiana. Contexto: Una persona llama por un resultado que no aparece en el portal; se verifica identidad con datos limitados y se explica que debe consultar al laboratorio. La prueba es reconocer acuerdos ordinarios aunque incluyan intercambio de datos, horarios o gastos.

**Notas de la referencia:** Referencia provisional; revisar la evidencia y sus límites en D07. Partición según propuesta pendiente de D08. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-L-MEDICO-003

legitima · medico · cotidiana · 25 líneas

**Situación:** Un consultorio llama a una paciente para reprogramar por una ausencia del profesional; se acuerdan opciones sin preguntar información clínica.

` 1` **A:** Buenas, vi una llamada perdida del consultorio. ¿Era por el turno de mi hijo? ← _contexto_  
` 2` **B:** Sí, te llamamos porque la pediatra no va a atender el miércoles.  
` 3` **A:** Ah, justo ese día le toca el control de crecimiento.  
` 4` **B:** Podemos ofrecerte jueves a las tres o viernes a las diez.  
` 5` **A:** El jueves tiene escuela hasta las cuatro. ¿Hay algo después?  
` 6` **B:** El viernes a las diez es el único horario de esta semana.  
` 7` **A:** ¿Puedo llevarlo yo aunque el turno esté a nombre de su papá?  
` 8` **B:** Sí, si sos la madre registrada. ¿El apellido es Lorea?  
` 9` **A:** Sí, Lorea. Yo soy Paula.  
`10` **B:** Perfecto. ¿Querés que te reserve el viernes?  
`11` **A:** Sí, pero tiene natación a las once y media. La consulta alcanza en una hora, ¿no?  
`12` **B:** Normalmente dura veinte o treinta minutos, aunque puede haber espera.  
`13` **A:** Entonces llegamos bien. ¿Tengo que llevar la libreta de vacunas?  
`14` **B:** Sí, si la tenés. La pediatra va a revisar el calendario.  
`15` **A:** Está en la mochila, la llevo siempre.  
`16` **B:** ¿Querés conservar el turno original si aparece otro profesional el miércoles?  
`17` **A:** Prefiero la misma pediatra. Esperamos al viernes.  
`18` **B:** Listo, lo cambio para el viernes 13 a las diez.  
`19` **A:** Gracias por avisarme con tiempo. ¿Le mandan mensaje también al papá?  
`20` **B:** El recordatorio sale al teléfono principal que figura en la ficha.  
`21` **A:** Ese es el mío. Después le cuento a él.  
`22` **B:** De acuerdo. Si aparece una cancelación antes, te podemos llamar.  
`23` **A:** Sí, avisame solo si es después de las cuatro el jueves.  
`24` **B:** Lo anoto como preferencia, no como turno confirmado.  
`25` **A:** Perfecto, gracias.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** La apertura «Buenas, vi una llamada perdida del consultorio. ¿Era por el turno de mi hijo?» (L1) da paso a una gestión cotidiana. Contexto: Un consultorio llama a una paciente para reprogramar por una ausencia del profesional; se acuerdan opciones sin preguntar información clínica. La prueba es reconocer acuerdos ordinarios aunque incluyan intercambio de datos, horarios o gastos.

**Notas de la referencia:** Referencia provisional; revisar la evidencia y sus límites en D07. Partición según propuesta pendiente de D08. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-L-MEDICO-004

legitima · medico · cotidiana · con errores escritos de ASR · 25 líneas

**Situación:** Una persona consulta si puede cambiar la sede de una ecografía por dificultad de traslado; aporta fecha de nacimiento y acuerda mantener el turno.

` 1` **A:** hola tengo una ecografía el viernes en la sede norte y se me complicó llegar hasta allá ← _contexto_  
` 2` **B:** buen día tenés el turno a nombre de quién  
` 3` **A:** de silvia rueda es a las nueve de la mañana  
` 4` **B:** me confirmás tu fecha de nacimiento para ubicar el estudio  
` 5` **A:** el 22 de julio del 74  
` 6` **B:** gracias veo el turno de abdomen para el viernes 20  
` 7` **A:** hay otra sede más cerca del centro que haga el mismo estudio  
` 8` **B:** sí la sede de la plaza tiene ecografía general pero no tiene cupo hasta la semana siguiente  
` 9` **A:** me podrían pasar para el lunes  
`10` **B:** hay un espacio el lunes a las ocho y cuarto  
`11` **A:** mi orden vence este mes sigue siendo válida ese día  
`12` **B:** la orden dice válida hasta fin de noviembre así que sí  
`13` **A:** tengo que volver a pedir autorización a la obra social  
`14` **B:** la autorización ya está asociada al turno si cambiamos la sede vuelve a revisión  
`15` **A:** puede tardar y quedarme sin fecha  
`16` **B:** puede demorar un día si preferís mantenemos el viernes y no perdés el espacio  
`17` **A:** mejor no lo muevo entonces voy a pedirle a mi hermana que me acerque  
`18` **B:** está bien necesitás que anotemos alguna asistencia para llegar  
`19` **A:** no es solo el transporte tengo que ir en ayunas  
`20` **B:** la indicación de preparación está en la orden para ese estudio dice cuatro horas sin comida  
`21` **A:** ah lo tengo anotado llevo también el informe anterior  
`22` **B:** sí eso puede servirle al profesional  
`23` **A:** entonces confirmo viernes nueve en sede norte  
`24` **B:** queda igual te mandamos el recordatorio el día anterior  
`25` **A:** muchas gracias ya lo coordiné con mi hermana  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** La apertura «hola tengo una ecografía el viernes en la sede norte y se me complicó llegar hasta allá» (L1) da paso a una gestión cotidiana. Contexto: Una persona consulta si puede cambiar la sede de una ecografía por dificultad de traslado; aporta fecha de nacimiento y acuerda mantener el turno. La prueba es reconocer acuerdos ordinarios aunque incluyan intercambio de datos, horarios o gastos.

**Notas de la referencia:** Referencia provisional; revisar la evidencia y sus límites en D07. Partición según propuesta pendiente de D08. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-L-MEDICO-005

legitima · medico · cotidiana · 26 líneas

**Situación:** Un paciente llama para actualizar el teléfono de contacto del turno; confirma la terminación 0026 que cargó en el formulario y pide indicaciones para llegar.

` 1` **A:** Buenas, tengo turno de odontología mañana y el teléfono de la ficha quedó viejo. ← _contexto_  
` 2` **B:** Hola. ¿Me decís tu nombre y la hora del turno?  
` 3` **A:** Darío Funes, a las cinco y cuarto.  
` 4` **B:** Ya lo encontré. ¿Querés actualizar el teléfono de contacto?  
` 5` **A:** Sí, ahora uso uno que termina en 0026. El anterior lo di de baja.  
` 6` **B:** ¿Ese número nuevo ya lo cargaste en el formulario del turno?  
` 7` **A:** Sí, lo mandé ayer. ¿Necesitás que te dicte el número completo?  
` 8` **B:** No, con revisar los últimos cuatro que figuran me alcanza para confirmar el cambio.  
` 9` **A:** Sí, termina en 0026.  
`10` **B:** Listo, actualicé ese contacto para los recordatorios.  
`11` **A:** Buenísimo, gracias.  
`12` **B:** Listo. ¿Querés que revisemos cómo llegar a la sede?  
`13` **A:** Sí, siempre me confundo con la entrada porque están haciendo obras.  
`14` **B:** Entrás por la calle lateral, la que está frente a la plaza chica.  
`15` **A:** ¿Por la puerta de vidrio o por el portón blanco?  
`16` **B:** Por la puerta de vidrio. El portón es el acceso del estacionamiento.  
`17` **A:** ¿Hay lugar para dejar la bicicleta adentro?  
`18` **B:** Hay un bicicletero junto a recepción, pero no se puede dejar durante la noche.  
`19` **A:** La voy a dejar ahí mientras dure la consulta.  
`20` **B:** Perfecto. ¿Tenés una radiografía reciente para llevar?  
`21` **A:** No, la última es de enero. ¿Hace falta que la busque?  
`22` **B:** No, la odontóloga decide si necesita una nueva.  
`23` **A:** Bueno. ¿El pago es al salir?  
`24` **B:** Sí, en recepción después de la consulta.  
`25` **A:** Listo. Ya tengo el teléfono actualizado y la entrada clara.  
`26` **B:** Te esperamos mañana. Que andes bien.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** La apertura «Buenas, tengo turno de odontología mañana y el teléfono de la ficha quedó viejo.» (L1) da paso a una gestión cotidiana. Contexto: Un paciente llama para actualizar el teléfono de contacto del turno; confirma la terminación 0026 que cargó en el formulario y pide indicaciones para llegar. La prueba es reconocer acuerdos ordinarios aunque incluyan intercambio de datos, horarios o gastos.

**Notas de la referencia:** Referencia provisional; revisar la evidencia y sus límites en D07. Partición según propuesta pendiente de D08. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-L-ORGANISMO_PREVISIONAL-001

legitima · organismo_previsional · pedido_razonable · **en la matriz #101** · **propuesto para grabar** · 24 líneas

**Situación:** Una persona llama por el estado de un trámite de pensión iniciado presencialmente; se comprueba el turno y se aclara qué documento falta.

` 1` **A:** Buen día. Hace dos semanas llevé los papeles para actualizar el cobro de mi mamá y todavía no hay novedades.  
` 2` **B:** Hola. ¿Tenés el comprobante de la atención o la fecha aproximada?  
` 3` **A:** Fue el martes 6, en la oficina del centro. Nos dieron un papel con un número de trámite.  
` 4` **B:** ¿Me decís ese número, sin datos de acceso? Con eso busco el estado. ← _pedido_  
` 5` **A:** Es 481-730. Lo tengo acá en la carpeta.  
` 6` **B:** Gracias. Figura en revisión porque falta una copia del certificado de supervivencia.  
` 7` **A:** Pero lo entregamos junto con el formulario. Mi hermana sacó dos copias.  
` 8` **B:** En el registro aparece una sola hoja y no se ve el sello en la segunda página.  
` 9` **A:** ¿La puedo llevar cualquier día o tengo que sacar turno de nuevo?  
`10` **B:** Para agregar documentación conviene reservar una consulta breve. ¿En qué localidad estás?  
`11` **A:** En San Miguel. Nos queda más cómodo ir a la oficina de la avenida.  
`12` **B:** Hay un espacio el miércoles a las diez y media. ¿Te sirve?  
`13` **A:** Sí, pero mi mamá usa bastón. ¿Hay acceso por rampa?  
`14` **B:** Sí, la entrada lateral tiene rampa y ascensor.  
`15` **A:** Entonces lo tomo. ¿Qué tengo que llevar además de la copia?  
`16` **B:** El comprobante del trámite y el documento de ella para presentarlo en la oficina.  
`17` **A:** ¿Te dicto el número de documento ahora?  
`18` **B:** No, no hace falta para reservar. Lleven el documento el día del turno.  
`19` **A:** Gracias. ¿Ese turno queda a nombre de ella o mío?  
`20` **B:** A nombre de Marta Soria, según el trámite que consultaste.  
`21` **A:** Correcto. Yo soy la hija y la acompaño.  
`22` **B:** Quedó para el miércoles a las diez y media. Te doy la referencia 2058.  
`23` **A:** La anoto en el papel del trámite. Gracias por explicarme lo que faltaba.  
`24` **B:** De nada, ojalá lo puedan completar sin otra vuelta.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** L4 aporta una comprobación acotada («¿Me decís ese número, sin datos de acceso? Con eso busco el estado.»). Contexto: Una persona llama por el estado de un trámite de pensión iniciado presencialmente; se comprueba el turno y se aclara qué documento falta. La prueba es juzgar el dato por su función, no por la presencia aislada de una solicitud.

**Notas de la referencia:** Referencia provisional; revisar la evidencia y sus límites en D07. Partición de desarrollo según propuesta pendiente de D08. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-L-ORGANISMO_PREVISIONAL-002

legitima · organismo_previsional · pedido_razonable · 24 líneas

**Situación:** La persona consulta un cambio de fecha de cobro y confirma identidad del titular con nombre y localidad; se aclara que el calendario no se modifica.

` 1` **A:** Hola, llamo porque el depósito de mi papá suele entrar el día 12 y este mes todavía no aparece. ← _contexto_  
` 2` **B:** Buenas. ¿El día 12 cae fin de semana o feriado?  
` 3` **A:** Cayó domingo. Pensamos que se iba a adelantar, pero no pasó nada.  
` 4` **B:** En algunos meses el calendario mueve la fecha. ¿Tenés la terminación del beneficio o solo la fecha habitual?  
` 5` **A:** La terminación es 6. Él está conmigo, se llama Ramón Ibarra.  
` 6` **B:** Para ubicar el calendario, con el nombre y la terminación alcanza. ¿En qué localidad cobra?  
` 7` **A:** En Tafí Viejo, por una cuenta del banco.  
` 8` **B:** Según el cronograma publicado, para esa terminación el pago es el lunes 14.  
` 9` **A:** ¿Entonces no hay un problema con la cuenta?  
`10` **B:** No puedo ver saldos ni movimientos bancarios desde esta línea. Solo puedo confirmar la fecha asignada.  
`11` **A:** Él fue al cajero ayer y le dijeron que no tenía depósito.  
`12` **B:** Si fue antes del día indicado, es esperable que todavía no aparezca.  
`13` **A:** ¿Hay forma de saber el horario exacto?  
`14` **B:** El organismo no informa una hora, porque depende del procesamiento de cada entidad.  
`15` **A:** Bueno, le aviso que vuelva el lunes. Está preocupado porque necesita pagar la luz.  
`16` **B:** Entiendo. ¿La factura vence antes de esa fecha?  
`17` **A:** El martes. Si se acredita el lunes nos alcanza.  
`18` **B:** Puede consultar con la empresa si permite pagar un día después sin recargo.  
`19` **A:** Voy a llamar ahora. ¿Necesitás que te pase el documento para confirmar la fecha?  
`20` **B:** No, con el nombre, la terminación y la localidad ya consultamos el calendario general.  
`21` **A:** Perfecto. Me quedo con la fecha del 14.  
`22` **B:** Sí, lunes 14. Si ese día no figura el pago, consulten nuevamente por el canal que usan normalmente.  
`23` **A:** Gracias, le transmito eso.  
`24` **B:** De nada. Buenas tardes.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** La conversación arranca con «Hola, llamo porque el depósito de mi papá suele entrar el día 12 y este mes todavía no aparece.» (L1). Contexto: La persona consulta un cambio de fecha de cobro y confirma identidad del titular con nombre y localidad; se aclara que el calendario no se modifica. La dificultad es considerar para qué se confirma la información antes de alertar solo por la presencia de datos personales.

**Notas de la referencia:** Referencia provisional; revisar la evidencia y sus límites en D07. Partición de desarrollo según propuesta pendiente de D08. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-L-ORGANISMO_PREVISIONAL-003

legitima · organismo_previsional · mencion_sin_pedido · con errores escritos de ASR · 27 líneas

**Situación:** En una consulta por una constancia de atención, la persona menciona una clave fiscal que usa para otro trámite, sin que nadie pida acceder a ella.

` 1` **A:** hola necesito volver a imprimir una constancia de atención de la semana pasada  
` 2` **B:** buen día recordás en qué oficina hiciste la consulta  
` 3` **A:** en la de la terminal vieja por un cambio de domicilio  
` 4` **B:** tenés el comprobante con el número de gestión  
` 5` **A:** sí dice 3021 también tengo una carpeta con papeles de la contadora  
` 6` **B:** qué necesitás que figure en la constancia  
` 7` **A:** la fecha y que presenté el formulario en el trabajo me lo piden para justificar la mañana  
` 8` **B:** puedo revisar si quedó cargada a nombre de quién se hizo la atención  
` 9` **A:** estela masa soy yo  
`10` **B:** encontré la visita del jueves la constancia se descarga desde el portal de trámites  
`11` **A:** puedo entrar desde el teléfono la computadora está en el local  
`12` **B:** sí aunque quizá sea más fácil desde una pantalla grande para imprimir  
`13` **A:** tengo una clave fiscal guardada en otro lado pero no sé si sirve para ese portal ← _mencion_  
`14` **B:** esa credencial corresponde a otro sistema para este trámite usá el acceso que aparece en la página de turnos  
`15` **A:** no se vinculan entre sí  
`16` **B:** no necesariamente el portal te va a indicar qué método de ingreso acepta  
`17` **A:** bueno no quiero bloquear nada por probar contraseñas distintas ← _mencion_  
`18` **B:** si no recordás el acceso elegí recuperar usuario desde la propia página  
`19` **A:** y la constancia se manda por correo  
`20` **B:** Al descargarla queda disponible para guardar o imprimir. ← _mencion_  
`21` **A:** entiendo la oficina me queda cerca quizá pase mañana y pregunte allí  
`22` **B:** también podés consultar el estado en el portal cuando estés frente a una computadora  
`23` **A:** me confirmás que la atención aparece registrada  
`24` **B:** sí aparece con fecha y número 3021  
`25` **A:** listo con eso ya puedo explicar en el trabajo que tengo que buscarla  
`26` **B:** perfecto te queda otra consulta  
`27` **A:** no gracias  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** En L13 aparece «tengo una clave fiscal guardada en otro lado pero no sé si sirve para ese portal» dentro de la consulta, sin que nadie pida repetirlo ni compartirlo. El caso prueba si se distingue una mención de código o clave de una solicitud observable.

**Notas de la referencia:** Referencia provisional; revisar la evidencia y sus límites en D07. Partición de desarrollo según propuesta pendiente de D08. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-L-PREMIO-001

legitima · premio · pedido_razonable · **en la matriz #101** · **propuesto para grabar** · 24 líneas

**Situación:** La persona llama al organizador para confirmar las condiciones de una rifa solidaria cuyo premio ya compró; se identifica el sorteo por fecha y talonario.

` 1` **A:** Buenas, estoy llamando por la rifa del club. Compré un número pero no encuentro cuándo se sortea.  
` 2` **B:** Hola, ¿fue la rifa de la cena o la de la camiseta?  
` 3` **A:** La de la camiseta. Me la vendió una chica en la puerta el sábado.  
` 4` **B:** ¿Tenés el talonario o una foto del número?  
` 5` **A:** Sí, el 148. La foto muestra el sello del club y el nombre de mi hijo.  
` 6` **B:** Para ubicar la venta, ¿me confirmás el nombre que aparece en el talón? ← `REQUEST_PERSONAL_DATA`  
` 7` **A:** Julián Paredes. Está escrito medio torcido, pero se entiende.  
` 8` **B:** Lo encontré en la planilla de la categoría infantil. El sorteo es el domingo después del partido.  
` 9` **A:** ¿En la cancha o lo hacen por redes?  
`10` **B:** Se anuncia en el buffet y después publican el resultado en el grupo del club.  
`11` **A:** Yo no estoy en ese grupo. ¿Podés avisarme si sale mi número?  
`12` **B:** Puedo anotar tu teléfono de contacto, pero solo para informar el resultado. ¿Sigue terminando en 84?  
`13` **A:** Sí, ese es el mío.  
`14` **B:** ¿Querés que te agregue al grupo de novedades?  
`15` **A:** No, prefiero que me manden un mensaje si gano. No uso mucho los grupos.  
`16` **B:** Está bien. La rifa cuesta 1.500 y ya figura paga.  
`17` **A:** Sí, le transferí a la tesorera y me dio el talón después.  
`18` **B:** No hace falta que me pases el comprobante ahora; la planilla ya la marca como abonada.  
`19` **A:** ¿Si no voy el domingo, puedo retirar la camiseta otro día?  
`20` **B:** Sí, coordinás con la comisión durante la semana.  
`21` **A:** Perfecto. Pensé que se sorteaba mañana y estaba por ir al club.  
`22` **B:** No, es el domingo 22, al terminar el partido de juveniles.  
`23` **A:** Ahí me queda claro. Gracias por buscarlo.  
`24` **B:** De nada, que tengan buen partido.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** L6 aporta una comprobación acotada («Para ubicar la venta, ¿me confirmás el nombre que aparece en el talón?»). Contexto: La persona llama al organizador para confirmar las condiciones de una rifa solidaria cuyo premio ya compró; se identifica el sorteo por fecha y talonario. La prueba es juzgar el dato por su función, no por la presencia aislada de una solicitud.

**Notas de la referencia:** Referencia provisional; revisar la evidencia y sus límites en D07. Partición de desarrollo según propuesta pendiente de D08. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-L-PREMIO-002

legitima · premio · pedido_razonable · 25 líneas

**Situación:** Quien compró una entrada para un sorteo de una feria llama para corregir el correo de notificación; se verifica el evento y el número de entrada.

` 1` **A:** Hola, compré una entrada para el sorteo de la feria de cerámica y puse mal una letra en el correo.  
` 2` **B:** Buen día. ¿Tenés el número de entrada? ← _pedido_  
` 3` **A:** 72-18. La compré en el puesto de informes el sábado a la tarde.  
` 4` **B:** ¿A nombre de quién quedó registrada? ← `REQUEST_PERSONAL_DATA`  
` 5` **A:** Camila Neri. El correo tendría que ser cami punto neri arroba correo ejemplo.  
` 6` **B:** ¿Qué letra pusiste mal?  
` 7` **A:** Puse una i de más en el apellido. La dirección correcta termina en neri, con una sola i seguida de e.  
` 8` **B:** Entiendo. ¿Querés que la notificación llegue a esa dirección corregida?  
` 9` **A:** Sí, solo para el resultado del sorteo. No quiero cambiar otros datos.  
`10` **B:** Puedo modificar el correo vinculado a esta entrada. ¿El evento es la feria del domingo en el galpón municipal?  
`11` **A:** Exacto, la que tiene puestos de vajilla y plantas.  
`12` **B:** Listo. Te leo cómo quedó: cami punto neri arroba correo ejemplo.  
`13` **A:** Sí, ahora está bien.  
`14` **B:** La entrada figura abonada, con el número 72-18.  
`15` **A:** ¿Puedo transferirla a mi hermana si al final no voy?  
`16` **B:** Las bases permiten cederla hasta el sábado a las seis. Tendría que avisarnos el nuevo nombre.  
`17` **A:** No hace falta por ahora. Ella me acompaña y tiene su propia entrada.  
`18` **B:** Bien. ¿Querés que te mande un comprobante de la corrección?  
`19` **A:** Si puede ser, pero alcanza con el correo de confirmación.  
`20` **B:** Te llega dentro de unos minutos a la dirección nueva.  
`21` **A:** Me fijo cuando corte. No te dicto ningún número de tarjeta ni nada, ¿no?  
`22` **B:** No, la compra ya está confirmada. Solo actualizamos el correo para el aviso.  
`23` **A:** Perfecto, gracias. Me daba cosa que no me llegara el resultado.  
`24` **B:** Ahora debería llegarte. ¿Algo más?  
`25` **A:** No, muchas gracias.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** L2 aporta una comprobación acotada («Buen día. ¿Tenés el número de entrada?»). Contexto: Quien compró una entrada para un sorteo de una feria llama para corregir el correo de notificación; se verifica el evento y el número de entrada. La prueba es juzgar el dato por su función, no por la presencia aislada de una solicitud.

**Notas de la referencia:** Referencia provisional; revisar la evidencia y sus límites en D07. Partición de desarrollo según propuesta pendiente de D08. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-L-PREMIO-003

legitima · premio · pedido_razonable · 25 líneas

**Situación:** La persona consulta por un premio recibido en una competencia de fotografía comunitaria; se confirma el nombre público y el horario de entrega.

` 1` **A:** Buenas tardes. Me llamaron del concurso de fotos del barrio y dijeron que quedé entre los seleccionados.  
` 2` **B:** Hola. ¿Sabés el nombre de la muestra?  
` 3` **A:** “Ventanas de invierno”. Mandé una foto de la plaza con la niebla.  
` 4` **B:** ¿Con qué nombre la presentaste? ← `REQUEST_PERSONAL_DATA`  
` 5` **A:** Con mi nombre, Lila Acosta. No uso seudónimo.  
` 6` **B:** Sí, está en la lista de menciones. La entrega de certificados es el viernes a las siete.  
` 7` **A:** ¿El reconocimiento se retira ahí o lo mandan después?  
` 8` **B:** El certificado se entrega en la biblioteca. La impresión de la foto queda para otra fecha.  
` 9` **A:** Pensé que incluía la copia enmarcada, eso decía el afiche.  
`10` **B:** Puede ser que haya una sola impresión para la foto ganadora. Las menciones reciben certificado.  
`11` **A:** Entiendo. ¿Quién organiza la entrega?  
`12` **B:** La comisión cultural y la biblioteca del barrio.  
`13` **A:** ¿Necesitan que lleve algo para retirar el certificado?  
`14` **B:** Llevá el número de inscripción, 56, o decí tu nombre en la mesa.  
`15` **A:** ¿Te paso mi documento ahora para dejarlo anotado?  
`16` **B:** No hace falta. Solo vamos a comprobar que seas la persona que figura en la inscripción cuando llegues.  
`17` **A:** ¿Puedo mandar a mi hija a buscarlo si no llego del trabajo?  
`18` **B:** Consulto las bases. Dice que puede retirarlo otra persona con una autorización simple.  
`19` **A:** Bueno, se lo preparo. Ella también sacó fotos en el concurso infantil.  
`20` **B:** Ese concurso se entrega el sábado por la mañana, en otro horario.  
`21` **A:** Ah, entonces vamos los dos días.  
`22` **B:** La muestra queda abierta hasta fin de mes, por si quieren verla con tiempo.  
`23` **A:** Qué bueno. La foto de la plaza quedó linda con esa luz.  
`24` **B:** Sí, la vimos en la selección. Te esperamos el viernes.  
`25` **A:** Gracias por aclarar lo del marco, así no voy esperando otra cosa.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** L4 aporta una comprobación acotada («¿Con qué nombre la presentaste?»). Contexto: La persona consulta por un premio recibido en una competencia de fotografía comunitaria; se confirma el nombre público y el horario de entrega. La prueba es juzgar el dato por su función, no por la presencia aislada de una solicitud.

**Notas de la referencia:** Referencia provisional; revisar la evidencia y sus límites en D07. Partición de desarrollo según propuesta pendiente de D08. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-L-SOPORTE-001

legitima · soporte · pedido_razonable · **propuesto para grabar** · 25 líneas

**Situación:** La persona llama al proveedor por cortes de internet y confirma domicilio de instalación y franja horaria para una visita técnica.

` 1` **A:** Buenas, llamo yo porque desde ayer se corta internet cada veinte minutos.  
` 2` **B:** Hola, ¿pasa en todos los equipos o solamente en la computadora?  
` 3` **A:** En todos. El televisor queda cargando y el teléfono se pasa a datos.  
` 4` **B:** ¿Las luces del módem cambian cuando se corta?  
` 5` **A:** La de internet se pone naranja. Después vuelve sola al rato.  
` 6` **B:** Voy a revisar la línea. ¿Me confirmás la calle y la altura donde está instalado? ← `REQUEST_PERSONAL_DATA`  
` 7` **A:** Pasaje Molino 184, departamento tres. Es la casa del fondo.  
` 8` **B:** Gracias. ¿El servicio está a nombre de vos o de otra persona?  
` 9` **A:** A nombre de mi pareja, Nadia Cores. Ella está trabajando y me pidió que llamara.  
`10` **B:** Veo una intermitencia en el equipo. ¿Podés mirar si el cable que entra en la pared está flojo?  
`11` **A:** Está firme. Lo acomodé ayer, pero no cambió nada.  
`12` **B:** No hace falta abrir el módem ni tocar la instalación. Puedo pedir una revisión a domicilio.  
`13` **A:** ¿Qué horarios tienen? A la mañana no queda nadie.  
`14` **B:** Hay una visita el jueves entre las dos y las cinco, o el viernes después de las seis.  
`15` **A:** El jueves puede venir mi cuñado, pero no sé si va a llegar a las dos.  
`16` **B:** La franja es amplia. Si querés, dejamos el viernes que es más seguro.  
`17` **A:** Sí, viernes. ¿Necesitás el documento de Nadia?  
`18` **B:** No para agendar la visita. Confirmame un teléfono de contacto, pero podés dar el que ya figura terminado en 31. ← _pedido_  
`19` **A:** Ese es el mío, lo tengo conmigo.  
`20` **B:** Bien, quedó para el viernes. La persona técnica va a llamar antes de salir.  
`21` **A:** ¿Tengo que pagar algo por la revisión?  
`22` **B:** No hay cargo si el problema es del equipo o de la línea. Si es una instalación interna, te informan antes de hacer un trabajo adicional.  
`23` **A:** Perfecto, así sabemos qué esperar.  
`24` **B:** Te paso el número de orden: 2865.  
`25` **A:** Lo anoté. Gracias por la ayuda.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** L6 aporta una comprobación acotada («Voy a revisar la línea. ¿Me confirmás la calle y la altura donde está instalado?»). Contexto: La persona llama al proveedor por cortes de internet y confirma domicilio de instalación y franja horaria para una visita técnica. La prueba es juzgar el dato por su función, no por la presencia aislada de una solicitud.

**Notas de la referencia:** Referencia provisional; revisar la evidencia y sus límites en D07. Partición de desarrollo según propuesta pendiente de D08. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-L-SOPORTE-002

legitima · soporte · pedido_razonable · **en la matriz #101** · 26 líneas

**Situación:** Una trabajadora inicia la llamada para recuperar acceso a un sistema de turnos; soporte pide el nombre del comercio y un correo laboral parcial.

` 1` **A:** Hola, no puedo entrar al sistema de turnos del consultorio y hoy tengo que cerrar la agenda.  
` 2` **B:** Buen día. ¿Te aparece un error o simplemente no reconoce el usuario?  
` 3` **A:** Dice que el correo no existe, pero ayer entré con el mismo.  
` 4` **B:** ¿Estás usando el sistema desde la computadora del consultorio?  
` 5` **A:** Sí, desde la recepción. No cambié nada que yo sepa.  
` 6` **B:** Para revisar la cuenta, ¿me confirmás el nombre del consultorio y las primeras letras del correo registrado? ← `REQUEST_PERSONAL_DATA`  
` 7` **A:** Consultorio del Parque. El correo empieza con recepcion y termina en arroba elparque punto ejemplo.  
` 8` **B:** Gracias. Encontré el usuario. ¿Ayer te pidieron cambiar la contraseña al vencer?  
` 9` **A:** Sí, la cambié después del almuerzo. La guardé en el administrador del navegador.  
`10` **B:** Puede que el navegador esté completando la anterior. Probá borrar solo el campo y escribirla manualmente.  
`11` **A:** No quiero cerrar todo porque tengo varias pestañas abiertas.  
`12` **B:** No hace falta cerrar las pestañas. Abrí una ventana privada y entrá desde el acceso habitual.  
`13` **A:** ¿Eso no borra la información del consultorio?  
`14` **B:** No, es una ventana temporal. No descargues archivos ni guardes datos ahí.  
`15` **A:** Entré. Me aparece la agenda del día, pero los turnos de mañana no.  
`16` **B:** ¿Qué fecha tenés seleccionada arriba?  
`17` **A:** Hoy. Ahora veo la flechita para cambiar al martes.  
`18` **B:** Ahí deberían aparecer. ¿Te muestra el nombre de tu usuario en la esquina?  
`19` **A:** Sí, recepción. Entonces el acceso está funcionando.  
`20` **B:** Exacto. Al terminar, cerrá la ventana privada. Después podés corregir el dato guardado en el navegador normal.  
`21` **A:** Voy a llamar a la coordinadora para que me ayude con eso. No quiero pisar la clave nueva.  
`22` **B:** Está bien. La clave no necesito que me la digas.  
`23` **A:** Gracias, ya puedo cerrar la agenda.  
`24` **B:** ¿Querés que deje una nota del error para el equipo técnico?  
`25` **A:** Sí, por si vuelve a pasar después del cambio de turno.  
`26` **B:** Listo, quedó registrada la consulta 9340.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** L6 aporta una comprobación acotada («Para revisar la cuenta, ¿me confirmás el nombre del consultorio y las primeras letras del correo registrado?»). Contexto: Una trabajadora inicia la llamada para recuperar acceso a un sistema de turnos; soporte pide el nombre del comercio y un correo laboral parcial. La prueba es juzgar el dato por su función, no por la presencia aislada de una solicitud.

**Notas de la referencia:** Referencia provisional; revisar la evidencia y sus límites en D07. Partición de desarrollo según propuesta pendiente de D08. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-L-SOPORTE-003

legitima · soporte · pedido_razonable · 25 líneas

**Situación:** Un usuario llama por un router que no emite wifi y da el número de serie impreso del equipo para recibir una configuración guiada.

` 1` **A:** Buen día. El wifi desapareció de casa, pero la computadora sigue conectada por cable. ← _contexto_  
` 2` **B:** Hola. ¿Se apagó alguna luz del router o está todo encendido?  
` 3` **A:** La de wifi está apagada. Internet y energía están verdes.  
` 4` **B:** Puede haberse desactivado la radio inalámbrica. ¿El router tiene un botón lateral con el símbolo de ondas?  
` 5` **A:** Sí, hay uno chiquito al costado. No sabía para qué era.  
` 6` **B:** No lo mantengas apretado todavía. ¿Podés mirar la etiqueta de abajo y decirme el modelo?  
` 7` **A:** Dice Ronda 2, serie R-440. ¿Te sirve ese dato?  
` 8` **B:** Sí, gracias. Ese modelo tiene un botón que activa y desactiva el wifi.  
` 9` **A:** Si lo toco, ¿se borra la configuración?  
`10` **B:** No. Un toque breve vuelve a encender la señal. No presiones el botón hundido de reinicio.  
`11` **A:** Ya lo toqué una vez. La luz empezó a parpadear.  
`12` **B:** Esperá un minuto y buscá la red habitual desde el teléfono.  
`13` **A:** Aparecieron dos redes, una termina en 2G y otra en 5G.  
`14` **B:** ¿Cuál usabas antes?  
`15` **A:** La de 2G, porque llega hasta el patio. La otra no aparece en el dormitorio.  
`16` **B:** Conectate a esa y fijate si carga una página.  
`17` **A:** Sí, abrió. El televisor también se conectó solo.  
`18` **B:** Entonces quedó resuelto. Si vuelve a pasar, puede ser un toque accidental sobre el botón.  
`19` **A:** Mi gato se sube a la repisa donde está el router, capaz fue eso.  
`20` **B:** Puede ser. Si querés, movelo a un lugar ventilado donde no lo alcancen.  
`21` **A:** ¿Hace falta que actualice algo ahora?  
`22` **B:** No, el equipo volvió a la configuración anterior. No instalamos nada ni necesitamos acceder a tu pantalla.  
`23` **A:** Bien, era lo que me preocupaba. Gracias.  
`24` **B:** De nada. ¿Hay otro problema de conexión?  
`25` **A:** No, ahora funciona todo.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** La conversación arranca con «Buen día. El wifi desapareció de casa, pero la computadora sigue conectada por cable.» (L1). Contexto: Un usuario llama por un router que no emite wifi y da el número de serie impreso del equipo para recibir una configuración guiada. La dificultad es considerar para qué se confirma la información antes de alertar solo por la presencia de datos personales.

**Notas de la referencia:** Referencia provisional; revisar la evidencia y sus límites en D07. Partición de desarrollo según propuesta pendiente de D08. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-L-SOPORTE-004

legitima · soporte · mencion_sin_pedido · 24 líneas

**Situación:** Consulta por una clave de producto olvidada en un programa de dibujo; se aclara que no corresponde al acceso de cuenta.

` 1` **A:** Hola, reinstalé el programa de dibujo y me pide una clave que no encuentro. ← _mencion_  
` 2` **B:** Buenas. ¿Es una clave de producto o te está pidiendo iniciar sesión? ← _mencion_  
` 3` **A:** Dice “clave de licencia”. Es una compra vieja, la hice hace varios años. ← _mencion_  
` 4` **B:** ¿Tenés el correo de confirmación de esa compra?  
` 5` **A:** Puede estar en una cuenta que casi no uso. No me acuerdo la contraseña de ese correo tampoco. ← _mencion_  
` 6` **B:** Podemos buscar la compra con el nombre del programa y el año aproximado.  
` 7` **A:** Se llamaba Trazo, la compré cuando empecé a hacer carteles para el club.  
` 8` **B:** ¿Más o menos en qué año?  
` 9` **A:** En 2021, antes de que pintáramos el salón nuevo.  
`10` **B:** Encontré una licencia vinculada a tu correo terminado en taller punto ejemplo.  
`11` **A:** Ese debe ser. ¿Me vas a pedir que te pase la clave del programa? ← _mencion_  
`12` **B:** No, solo estamos verificando la licencia. Podés abrir la sección de compras desde tu cuenta.  
`13` **A:** Me muestra una clave con guiones. ¿Tengo que leerla? ← _mencion_  
`14` **B:** No hace falta que me la dictes. Pegala vos en el cuadro del programa y comprobá que aparezca como activado.  
`15` **A:** Ya la pegué. Dice licencia válida, pero no me trae los diseños anteriores.  
`16` **B:** Los diseños suelen guardarse en una carpeta local distinta. ¿Conservás la computadora anterior?  
`17` **A:** Sí, está guardada en el armario. La prendo el fin de semana.  
`18` **B:** Buscá la carpeta “mis proyectos” y copiá los archivos a un disco externo.  
`19` **A:** No quiero sincronizar nada en la nube porque son diseños del club.  
`20` **B:** Podés hacer una copia local. La licencia no incluye almacenamiento automático.  
`21` **A:** Entiendo. Ya quedó activado el programa, por lo menos.  
`22` **B:** Perfecto. ¿Te queda alguna duda sobre la licencia?  
`23` **A:** No, era eso. Gracias por separar las dos claves. ← _mencion_  
`24` **B:** De nada.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** En L1 aparece «Hola, reinstalé el programa de dibujo y me pide una clave que no encuentro.» dentro de la consulta, sin que nadie pida repetirlo ni compartirlo. El caso prueba si se distingue una mención de código o clave de una solicitud observable.

**Notas de la referencia:** Referencia provisional; revisar la evidencia y sus límites en D07. Partición de desarrollo según propuesta pendiente de D08. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-L-SOPORTE-005

legitima · soporte · mencion_sin_pedido · 24 líneas

**Situación:** La persona pregunta por una alerta que muestra un código de error de impresora; se comenta una contraseña de wifi como dato privado que ella no revela.

` 1` **A:** Buenas, la impresora dejó de conectarse y muestra el código E-14. ← _mencion_  
` 2` **B:** Hola. ¿La impresora está conectada por cable o por wifi?  
` 3` **A:** Por wifi. La computadora sí navega y el teléfono también.  
` 4` **B:** ¿Cambiaste el nombre de la red o el equipo hace poco?  
` 5` **A:** Cambié el módem el sábado. La contraseña del wifi quedó distinta. ← _mencion_  
` 6` **B:** Eso explica por qué la impresora no logra entrar a la red anterior.  
` 7` **A:** El manual dice que aparece un código de configuración, pero no sé cuál tengo que usar. ← _mencion_  
` 8` **B:** El código que genera la impresora se muestra en la pantalla para vincularla. No es la contraseña de tu red. ← _mencion_  
` 9` **A:** Ah, yo pensé que eran lo mismo. No anoté la clave nueva porque la eligió mi pareja. ← _mencion_  
`10` **B:** Pedile esa clave y cargala directamente en la impresora. ← _mencion_  
`11` **A:** ¿Dónde encuentro el menú de red?  
`12` **B:** Tocá ajustes, conectividad y después “buscar redes”. Elegí el nombre de tu casa.  
`13` **A:** Hay dos nombres parecidos. Uno termina en invitados.  
`14` **B:** Elegí la red principal, no la de invitados, porque esa puede bloquear la comunicación con la computadora.  
`15` **A:** Ya la elegí. Ahora me pide la contraseña del wifi en la pantalla chiquita. ← _mencion_  
`16` **B:** Ingresala ahí usando las flechas. Si te equivocás, podés borrar y empezar de nuevo.  
`17` **A:** Tardé un poco, pero ahora dice conectada.  
`18` **B:** Imprimí una página de prueba para confirmar que quedó vinculada.  
`19` **A:** Salió bien. El error E-14 desapareció.  
`20` **B:** Perfecto. ¿Querés revisar también el escáner?  
`21` **A:** No, eso funciona. Lo que me confundía era el código y la contraseña. ← _mencion_  
`22` **B:** Son cosas distintas. La contraseña queda en tu equipo y el código solo inicia el emparejamiento. ← _mencion_  
`23` **A:** Entendido, muchas gracias.  
`24` **B:** A vos. Buen día.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** En L1 aparece «Buenas, la impresora dejó de conectarse y muestra el código E-14.» dentro de la consulta, sin que nadie pida repetirlo ni compartirlo. El caso prueba si se distingue una mención de código o clave de una solicitud observable.

**Notas de la referencia:** Referencia provisional; revisar la evidencia y sus límites en D07. Partición de desarrollo según propuesta pendiente de D08. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-L-TRABAJO-001

legitima · trabajo · cotidiana · con errores escritos de ASR · 23 líneas

**Situación:** Una compañera llama para cambiar la apertura del local porque se rompió el candado; se redistribuyen tareas y se confirma quién tiene una copia.

` 1` **A:** estás cerca del local el candado de la persiana no gira ← _contexto_  
` 2` **B:** voy en camino pero estoy a veinte minutos se trabó la llave o no entra  
` 3` **A:** entra hasta la mitad y después queda dura no quiero forzarla  
` 4` **B:** bien dejala quieta probaste con la copia que está en el cajón de caja  
` 5` **A:** sí hace lo mismo capaz se mojó con la lluvia de anoche  
` 6` **B:** puede ser le escribo al cerrajero que arregló la puerta del depósito  
` 7` **A:** lo conocés vos o lo busco en el teléfono del negocio  
` 8` **B:** lo tengo agendado se llama fabián y ya vino el mes pasado  
` 9` **A:** le digo que venga ahora o esperamos a que llegues  
`10` **B:** decile que estamos en el local y que nos confirme cuánto tarda no le entregues la llave a nadie hasta que llegue alguno de los dos  
`11` **A:** me contestó dice que puede pasar a las nueve y cuarto  
`12` **B:** entonces abro la puerta de atrás cuando llegue vos podés atender mientras tanto las consultas de pedidos  
`13` **A:** sí tengo la lista impresa el primero pasa a retirar una caja de vasos  
`14` **B:** la caja está en el depósito pero no abras esa puerta si el cerrajero todavía no vio el candado  
`15` **A:** la dejo preparada acá afuera avisamos al grupo que abrimos media hora más tarde  
`16` **B:** sí escribí que hubo un problema con la persiana y damos horario estimado a las diez  
`17` **A:** ya lo mandé una clienta preguntó si puede retirar al mediodía  
`18` **B:** decile que sí así nos da margen yo voy a buscar café mientras espero el colectivo  
`19` **A:** querés que pida también para vos  
`20` **B:** sí uno chico sin azúcar después te transfiero lo mío  
`21` **A:** dale te mando el importe por el grupo del local  
`22` **B:** listo avisame si el cerrajero cambia la hora  
`23` **A:** te escribo cuando esté acá  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** La apertura «estás cerca del local el candado de la persiana no gira» (L1) da paso a una gestión cotidiana. Contexto: Una compañera llama para cambiar la apertura del local porque se rompió el candado; se redistribuyen tareas y se confirma quién tiene una copia. La prueba es reconocer acuerdos ordinarios aunque incluyan intercambio de datos, horarios o gastos.

**Notas de la referencia:** Referencia provisional; revisar la evidencia y sus límites en D07. Partición según propuesta pendiente de D08. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-L-TRABAJO-002

legitima · trabajo · cotidiana · con errores escritos de ASR · 25 líneas

**Situación:** Dos personas de un taller coordinan una entrega cuyo pedido salió con una medida incorrecta; revisan el registro y acuerdan rehacer la pieza.

` 1` **A:** el cliente de los estantes llamó la medida del módulo no coincide con el hueco ← _contexto_  
` 2` **B:** cuál de los dos módulos el del pasillo o el que va al mostrador  
` 3` **A:** el del mostrador pidió 62 centímetros y nosotros cortamos 68  
` 4` **B:** la orden de trabajo también dice 68  
` 5` **A:** sí pero en el mensaje que mandó antes aparece 62 capaz copié mal el dato  
` 6` **B:** le confirmamos por teléfono o le pedimos que nos lo vuelva a escribir  
` 7` **A:** ya lo tengo en el chat del taller le puedo mandar una foto del dibujo  
` 8` **B:** mandale primero una nota diciendo que encontramos la diferencia y que hoy no se lo vamos a llevar así  
` 9` **A:** me preocupa que tenga la inauguración el sábado  
`10` **B:** preguntale si le sirve retirar el viernes a última hora podemos rehacer el frente hoy  
`11` **A:** dice que sí mientras mantengamos la profundidad como estaba  
`12` **B:** cuánto material queda de la misma madera  
`13` **A:** hay una tabla pero alcanza justo si no se rompe al cortar  
`14` **B:** entonces guardemos el sobrante para una prueba y no usemos la pieza anterior como plantilla  
`15` **A:** el dibujo muestra 62 de ancho por 34 de alto te cierra  
`16` **B:** sí anotá que el cliente confirmó esas dos medidas a las ocho y veinte  
`17` **A:** ya lo puse en la orden nueva también separé el módulo que quedó grande  
`18` **B:** ese lo podemos adaptar para el depósito no lo tires  
`19` **A:** le cobramos el cambio de material  
`20` **B:** no el error fue nuestro lo anotamos como retrabajo  
`21` **A:** bueno vos podés quedarte hasta que termine el corte  
`22` **B:** sí pero llamá a tu casa para avisar que llegás más tarde  
`23` **A:** ya avisé el cliente mandó un pulgar arriba queda confirmada la entrega el viernes  
`24` **B:** perfecto después le mandamos una foto cuando esté armado  
`25` **A:** listo me pongo con la madera  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** La apertura «el cliente de los estantes llamó la medida del módulo no coincide con el hueco» (L1) da paso a una gestión cotidiana. Contexto: Dos personas de un taller coordinan una entrega cuyo pedido salió con una medida incorrecta; revisan el registro y acuerdan rehacer la pieza. La prueba es reconocer acuerdos ordinarios aunque incluyan intercambio de datos, horarios o gastos.

**Notas de la referencia:** Referencia provisional; revisar la evidencia y sus límites en D07. Partición según propuesta pendiente de D08. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-L-TRABAJO-003

legitima · trabajo · cotidiana · **propuesto para grabar** · 25 líneas

**Situación:** Una empleada llama a su encargado para corregir la carga de horas de una guardia; cotejan planilla y horario sin enviar información fuera del equipo.

` 1` **A:** Hola, ¿tenés un minuto? Me quedó mal cargada la guardia del martes. ← _contexto_  
` 2` **B:** Sí, decime. ¿Qué horario habías hecho?  
` 3` **A:** Entré a las seis y salí a las dos, pero en la planilla aparece hasta medianoche.  
` 4` **B:** ¿La compañera que te cubrió quedó registrada desde las doce?  
` 5` **A:** Sí, ella entró a las doce. Capaz pusimos las dos el mismo turno.  
` 6` **B:** ¿Tenés el parte de novedades de esa noche?  
` 7` **A:** Sí, está en la carpeta azul. Firmamos las dos al cambio.  
` 8` **B:** ¿Podés mirar si figura la hora de entrega de llaves?  
` 9` **A:** Dice 00:05 y al lado está mi firma. Después la firma de Lara es de las 00:10.  
`10` **B:** Eso confirma el cambio de turno. Mandame una foto de esa página por el canal interno.  
`11` **A:** ¿Puedo tapar los nombres de las personas que estaban esperando?  
`12` **B:** Sí, no necesitamos esos datos para corregir el horario.  
`13` **A:** Ya la saqué. Se ve bien la fecha y el registro.  
`14` **B:** La recibí. Voy a corregir la salida a las doce, que es el horario que cerramos.  
`15` **A:** No, yo salí a las dos. Lara llegó a medianoche y me cubrió hasta las dos porque se demoró el colectivo.  
`16` **B:** Ah, tenés razón. Entonces ella también quedó dos horas más tarde.  
`17` **A:** Sí, lo hablamos antes de que se fuera y lo anotamos en el cuaderno.  
`18` **B:** Bien, necesito revisar el cuaderno para ajustar las dos filas.  
`19` **A:** Está en el cajón de arriba, donde dejamos las planillas del mes.  
`20` **B:** Lo busco después del almuerzo y te aviso antes de cerrar nómina.  
`21` **A:** Gracias. No quiero que me descuenten esas dos horas por un error de carga.  
`22` **B:** Claro, lo verificamos con los dos registros y queda asentado.  
`23` **A:** ¿Hace falta que firme otra vez?  
`24` **B:** Solo si el sistema pide validar el cambio. Te aviso por el correo interno.  
`25` **A:** Listo, gracias por resolverlo.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** La apertura «Hola, ¿tenés un minuto? Me quedó mal cargada la guardia del martes.» (L1) da paso a una gestión cotidiana. Contexto: Una empleada llama a su encargado para corregir la carga de horas de una guardia; cotejan planilla y horario sin enviar información fuera del equipo. La prueba es reconocer acuerdos ordinarios aunque incluyan intercambio de datos, horarios o gastos.

**Notas de la referencia:** Referencia provisional; revisar la evidencia y sus límites en D07. Partición según propuesta pendiente de D08. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-L-TRABAJO-004

legitima · trabajo · cotidiana · 25 líneas

**Situación:** Un equipo de cocina acuerda cubrir una ausencia y redistribuye turnos y viandas; la conversación incluye desacuerdo sobre disponibilidad y una solución concreta.

` 1` **A:** Che, me escribió Sol que tiene fiebre y no llega al turno de la tarde. ← _contexto_  
` 2` **B:** ¿A quién le toca cerrar hoy? Yo salgo a las cinco.  
` 3` **A:** A mí también, pero puedo quedarme hasta las seis y media si alguien cubre caja.  
` 4` **B:** Yo puedo entrar una hora antes, aunque tengo que buscar a mi nene a las siete.  
` 5` **A:** Si entrás a las tres, cubrís la caja hasta que yo vuelva de la entrega.  
` 6` **B:** ¿La entrega de la oficina se puede pasar para mañana?  
` 7` **A:** No, la encargaron para las seis y ya está empaquetada.  
` 8` **B:** Entonces voy yo a buscar a tu nene, pero tendrías que avisarle a tu hermana.  
` 9` **A:** No quiero complicarte. Le pregunto a Paula si puede quedarse en caja.  
`10` **B:** Paula está en preparación hasta las cuatro, después queda libre.  
`11` **A:** Le escribí. Dice que puede tomar caja desde las cuatro y media.  
`12` **B:** Perfecto. Yo adelanto el turno y vos hacés la entrega.  
`13` **A:** ¿Quién revisa la cámara de frío antes del cierre?  
`14` **B:** Lo hago yo antes de salir. Anoto las temperaturas en la planilla.  
`15` **A:** Sol dejó una vianda en la heladera. ¿Se la guardamos para mañana?  
`16` **B:** Sí, poné su nombre en la tapa para que no se la lleve alguien por error.  
`17` **A:** Ya está. También dejo separado el menú del día para el equipo.  
`18` **B:** ¿Qué quedó, pastel de papa?  
`19` **A:** Sí, y hay una opción de verduras sin queso.  
`20` **B:** Mejor guardame esa, llego antes y no quiero comer apurado.  
`21` **A:** Dale. ¿Vos le avisás a Sol que no se preocupe por el turno?  
`22` **B:** Sí, le digo que descanse y que me mande el certificado cuando pueda.  
`23` **A:** No hace falta ahora, con que avise a la coordinadora mañana alcanza.  
`24` **B:** De acuerdo. Nos vemos a las tres.  
`25` **A:** Gracias por acomodarte.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** La apertura «Che, me escribió Sol que tiene fiebre y no llega al turno de la tarde.» (L1) da paso a una gestión cotidiana. Contexto: Un equipo de cocina acuerda cubrir una ausencia y redistribuye turnos y viandas; la conversación incluye desacuerdo sobre disponibilidad y una solución concreta. La prueba es reconocer acuerdos ordinarios aunque incluyan intercambio de datos, horarios o gastos.

**Notas de la referencia:** Referencia provisional; revisar la evidencia y sus límites en D07. Partición según propuesta pendiente de D08. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-L-TRABAJO-005

legitima · trabajo · cotidiana · 27 líneas

**Situación:** Dos compañeros de una oficina coordinan la devolución de un equipo prestado y acuerdan qué hacer con archivos del proyecto antes de entregarlo.

` 1` **A:** ¿Tenés la notebook gris? La necesita el equipo de sonido para la prueba. ← _contexto_  
` 2` **B:** Sí, la tengo en el armario. ¿La pasan a buscar hoy?  
` 3` **A:** A las cuatro. Me preguntaron si tiene instalado el programa de edición.  
` 4` **B:** Tiene la versión vieja, la que usamos para el evento de mayo.  
` 5` **A:** ¿Conviene actualizarla antes de prestarla?  
` 6` **B:** Mejor consultemos a sistemas. Si cambian la versión, capaz deja de abrir el proyecto anterior.  
` 7` **A:** En la carpeta compartida está la exportación final, pero no el archivo editable.  
` 8` **B:** El editable está en el disco externo negro. Lo guardé después de la última reunión.  
` 9` **A:** ¿Ese disco se queda con nosotros o va con la notebook?  
`10` **B:** Se queda acá. Hay material de otros eventos que no corresponde entregar.  
`11` **A:** ¿Podemos copiar solo el proyecto de sonido a un pendrive vacío?  
`12` **B:** Sí, pero primero confirmá que no tenga nombres de asistentes ni listas de contacto.  
`13` **A:** Lo revisé ayer. Solo hay pistas y nombres de canales.  
`14` **B:** Entonces copiá esa carpeta y probá abrirla en la otra computadora.  
`15` **A:** Ya estoy en eso. Carga, pero me muestra que falta una fuente de audio.  
`16` **B:** ¿Es la pista ambiente de la sala?  
`17` **A:** Sí. Está en el escritorio de la notebook, no en la carpeta del proyecto.  
`18` **B:** Copiala también y anotá el nombre en el inventario de préstamo.  
`19` **A:** Hecho. ¿Qué ponemos como fecha de devolución?  
`20` **B:** El lunes a la mañana. El miércoles la usa administración para la capacitación.  
`21` **A:** Aviso al grupo que la notebook sale a las cuatro y vuelve el lunes.  
`22` **B:** Agregá que entregamos cargador y funda, pero no el disco externo.  
`23` **A:** Listo, ya respondieron que pasan a horario.  
`24` **B:** Cuando se la lleven, anotá quién la retiró.  
`25` **A:** Sí, queda asentado en el cuaderno de equipos.  
`26` **B:** Gracias. ¿Te fijás también que vuelva con la funda?  
`27` **A:** Obvio, la marco en la lista.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** La apertura «¿Tenés la notebook gris? La necesita el equipo de sonido para la prueba.» (L1) da paso a una gestión cotidiana. Contexto: Dos compañeros de una oficina coordinan la devolución de un equipo prestado y acuerdan qué hacer con archivos del proyecto antes de entregarlo. La prueba es reconocer acuerdos ordinarios aunque incluyan intercambio de datos, horarios o gastos.

**Notas de la referencia:** Referencia provisional; revisar la evidencia y sus límites en D07. Partición según propuesta pendiente de D08. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-L-WHATSAPP-001

legitima · whatsapp · pedido_razonable · **en la matriz #101** · 23 líneas

**Situación:** La persona llama porque un familiar mayor cambió de teléfono y no logra recuperar el grupo de consorcio; se consulta el texto del aviso sin revelar código.

` 1` **A:** Hola, llamo yo. Mi tía cambió el teléfono y ahora no aparece el grupo del edificio. ← _contexto_  
` 2` **B:** ¿Puede entrar a WhatsApp o le quedó la pantalla de registro?  
` 3` **A:** Le pide confirmar el número, pero después sale un aviso de que mandaron un código.  
` 4` **B:** ¿El número sigue siendo el mismo que usaba antes?  
` 5` **A:** Sí, termina en 72. Ella está acá conmigo y me pidió que averigüe.  
` 6` **B:** ¿El aviso es dentro de la aplicación o le llegó por mensaje?  
` 7` **A:** Aparece dentro de la aplicación, dice que revise los SMS. No lo abrimos todavía.  
` 8` **B:** Bien. Para orientarte, ¿qué modelo de teléfono tiene? Con eso cambia un poco la pantalla.  
` 9` **A:** Es uno chico, marca Nuvia, con Android. El anterior se le rompió la pantalla.  
`10` **B:** Que abra la aplicación oficial y espere a que llegue el mensaje automático. La pantalla de registro muestra cómo seguir.  
`11` **A:** ¿Y si no llega? Tiene poca señal en el departamento.  
`12` **B:** Puede revisar si tiene servicio de SMS y pedir un solo reenvío después de que termine la cuenta regresiva.  
`13` **A:** ¿Le conviene volver a poner el chip en el teléfono viejo?  
`14` **B:** Si el chip funciona, puede recibir el mensaje en cualquier equipo. Tiene que cargar ese número en la pantalla de registro.  
`15` **A:** El mensaje ya llegó, dice seis números. Ella no entiende dónde van.  
`16` **B:** Que los ingrese en la pantalla de la aplicación.  
`17` **A:** Perfecto, está avanzando. ¿Después le vuelve el grupo?  
`18` **B:** Si la copia de seguridad está activa, podrá recuperar algunas conversaciones. Los grupos deberían aparecer cuando la cuenta quede habilitada.  
`19` **A:** La copia la hizo hace bastante, no sé si incluye todo.  
`20` **B:** Entonces puede faltar lo más reciente. Que espere a que termine la restauración antes de cambiar de teléfono otra vez.  
`21` **A:** Ya está avanzando, dice preparando mensajes.  
`22` **B:** Dejala con conexión estable y sin cerrar la aplicación por unos minutos.  
`23` **A:** Listo, el grupo del consorcio apareció. Muchas gracias.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** La conversación arranca con «Hola, llamo yo. Mi tía cambió el teléfono y ahora no aparece el grupo del edificio.» (L1). Contexto: La persona llama porque un familiar mayor cambió de teléfono y no logra recuperar el grupo de consorcio; se consulta el texto del aviso sin revelar código. La dificultad es considerar para qué se confirma la información antes de alertar solo por la presencia de datos personales.

**Notas de la referencia:** Referencia provisional; revisar la evidencia y sus límites en D07. Partición de desarrollo según propuesta pendiente de D08. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-L-WHATSAPP-002

legitima · whatsapp · pedido_razonable · 23 líneas

**Situación:** Una persona llama para pedir que retiren su número de un grupo vecinal creado por error; se confirma el nombre visible y se explica el trámite.

` 1` **A:** Buenas, necesito resolver algo del grupo de la feria. Me agregaron con el número viejo. ← _contexto_  
` 2` **B:** Hola. ¿Querés salir del grupo o cambiar el número asociado a tu cuenta?  
` 3` **A:** Quiero salir. El teléfono viejo ahora lo usa mi hijo y le llegan todos los mensajes.  
` 4` **B:** ¿Todavía tenés acceso a esa cuenta?  
` 5` **A:** Sí, en mi equipo nuevo. El anterior quedó guardado en casa.  
` 6` **B:** Si entrás desde el nuevo, podés abrir la información del grupo y elegir salir.  
` 7` **A:** Ya lo hice, pero me sigue apareciendo en la lista de chats archivados.  
` 8` **B:** ¿Te figura como grupo o como conversación individual?  
` 9` **A:** Como grupo. Se llama Feria del Parque, los sábados.  
`10` **B:** ¿Ves quién lo creó o quién administra?  
`11` **A:** Mi vecina Inés. Le mandé un mensaje y me dijo que ella ya quitó el número anterior.  
`12` **B:** Puede que veas un historial que quedó descargado. ¿Te llegan mensajes nuevos desde que saliste?  
`13` **A:** No, el último es del martes. Hoy es jueves.  
`14` **B:** Entonces ya no recibís novedades. Para ocultar ese historial, mantené apretado el chat y tocá eliminar.  
`15` **A:** Me pregunta si también quiero borrar los archivos.  
`16` **B:** Si no los necesitás, podés borrar todo. Si tenés fotos que querés guardar, descargalas antes.  
`17` **A:** Hay una lista de precios que me sirve para el puesto. La voy a guardar primero.  
`18` **B:** Bien. ¿Querés que revisemos si el número anterior sigue vinculado en otro equipo?  
`19` **A:** Sí, porque eso es lo que me preocupa.  
`20` **B:** En dispositivos vinculados podés cerrar la sesión de la computadora vieja.  
`21` **A:** Lo veo, solo aparece mi tablet.  
`22` **B:** Entonces el teléfono viejo ya no tiene una sesión activa de esa cuenta.  
`23` **A:** Listo, cierro el chat y guardo la lista. Gracias.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** La conversación arranca con «Buenas, necesito resolver algo del grupo de la feria. Me agregaron con el número viejo.» (L1). Contexto: Una persona llama para pedir que retiren su número de un grupo vecinal creado por error; se confirma el nombre visible y se explica el trámite. La dificultad es considerar para qué se confirma la información antes de alertar solo por la presencia de datos personales.

**Notas de la referencia:** Referencia provisional; revisar la evidencia y sus límites en D07. Partición de desarrollo según propuesta pendiente de D08. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-L-WHATSAPP-003

legitima · whatsapp · pedido_razonable · 25 líneas

**Situación:** La persona pide ayuda para exportar una conversación laboral propia antes de cambiar de equipo; se solicita contexto y nombre del grupo, no contenidos privados.

` 1` **A:** Hola, llamo porque voy a cambiar el celular y quiero guardar el chat del taller. ← _contexto_  
` 2` **B:** Buen día. ¿Querés conservar mensajes, archivos o las dos cosas?  
` 3` **A:** Sobre todo los mensajes con horarios. Los archivos ya están en la computadora del negocio.  
` 4` **B:** ¿La cuenta está abierta en el teléfono que vas a cambiar?  
` 5` **A:** Sí, todavía lo uso. El nuevo llega mañana.  
` 6` **B:** Podés hacer una copia desde ajustes, en la sección de chats. ¿Tenés espacio en la nube?  
` 7` **A:** Eso no sé. El teléfono me vive diciendo que está lleno.  
` 8` **B:** Primero revisá cuánto ocupa WhatsApp. También podés exportar una conversación puntual, aunque no queda integrada para seguir respondiendo.  
` 9` **A:** Me sirve que sea solo el grupo del taller, no quiero mezclar las cosas de casa.  
`10` **B:** ¿Cómo se llama el grupo en tu lista?  
`11` **A:** Taller Naranjo. Somos cuatro, nos organizamos con los turnos.  
`12` **B:** Abrí el grupo, tocá más opciones y buscá “exportar chat”.  
`13` **A:** Me pregunta si incluye archivos. ¿Qué conviene?  
`14` **B:** Si ya tenés los archivos afuera, elegí sin archivos. Va a quedar un documento de texto con los mensajes.  
`15` **A:** ¿Ese documento se manda automáticamente a todos?  
`16` **B:** No. Te deja elegir una aplicación o guardarlo como archivo. Revisá el destino antes de confirmar.  
`17` **A:** ¿Puedo guardarlo en la computadora después?  
`18` **B:** Sí, si lo mandás a tu propio correo o conectás el teléfono por cable. Evitá usar una cuenta compartida si el chat tiene datos del trabajo.  
`19` **A:** Tiene horarios y nombres de clientes, así que mejor lo guardo en la computadora del local.  
`20` **B:** Me parece razonable. Si el almacenamiento está lleno, también podés liberar videos viejos antes de hacer la copia.  
`21` **A:** Ya encontré la opción. Me muestra un archivo de 240 kilobytes.  
`22` **B:** Eso parece solo texto. Abrilo cuando termine para comprobar que quedó legible.  
`23` **A:** Lo hago ahora. ¿El nuevo celular puede usar el mismo grupo después?  
`24` **B:** Sí, al registrar tu cuenta en el nuevo, el grupo debería aparecer si la transferencia de chats se completa.  
`25` **A:** Perfecto, gracias por la guía.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** La conversación arranca con «Hola, llamo porque voy a cambiar el celular y quiero guardar el chat del taller.» (L1). Contexto: La persona pide ayuda para exportar una conversación laboral propia antes de cambiar de equipo; se solicita contexto y nombre del grupo, no contenidos privados. La dificultad es considerar para qué se confirma la información antes de alertar solo por la presencia de datos personales.

**Notas de la referencia:** Referencia provisional; revisar la evidencia y sus límites en D07. Partición de desarrollo según propuesta pendiente de D08. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-L-WHATSAPP-004

legitima · whatsapp · mencion_sin_pedido · **propuesto para grabar** · 25 líneas

**Situación:** Durante una consulta sobre notificaciones tardías, la persona relata que recibió un código en otra ocasión; no se solicita ni reproduce.

` 1` **A:** Buenas, los mensajes me llegan todos juntos cuando abro la aplicación. Antes sonaban al momento.  
` 2` **B:** ¿Te pasa con todos los chats o con uno en particular?  
` 3` **A:** Con todos. En el grupo de la familia me dicen que contesto tarde.  
` 4` **B:** ¿Tenés activado el ahorro de batería?  
` 5` **A:** Sí, lo pongo siempre porque el teléfono ya tiene unos años.  
` 6` **B:** Puede estar pausando las notificaciones en segundo plano. ¿Qué versión del sistema tenés?  
` 7` **A:** Una vieja, creo que la nueve. El celular es un Rivo, modelo Loma.  
` 8` **B:** Revisá permisos de notificación y batería. Si la aplicación está restringida, no actualiza hasta que la abrís.  
` 9` **A:** Lo puedo hacer. El año pasado me apareció un código de registro cuando cambié el chip y pensé que era por eso. ← _mencion_  
`10` **B:** ¿Fue al reinstalar la aplicación?  
`11` **A:** Sí, me acuerdo porque estaba en una terminal y no tenía señal buena.  
`12` **B:** El código puede aparecer cuando se verifica la cuenta. No hace falta que me lo compartas para revisar notificaciones. ← _mencion_  
`13` **A:** No lo tengo, fue hace un montón. Tampoco lo anoté.  
`14` **B:** Está bien, acá estamos viendo otra cosa. ¿Te aparece la optimización de batería activa para la aplicación?  
`15` **A:** Sí, está en “restringido”. La voy a poner en automático.  
`16` **B:** Probá primero en automático. Si sigue demorando, podés permitir actividad en segundo plano.  
`17` **A:** Ya cambié eso. Me mandé un mensaje desde la tablet y llegó enseguida.  
`18` **B:** Entonces parece que encontramos la causa.  
`19` **A:** ¿Eso me va a gastar mucho más batería?  
`20` **B:** Puede aumentar un poco el consumo, pero podés revisar durante el día y volver atrás si te complica.  
`21` **A:** Lo dejo así esta semana. ¿Hay otra cosa que deba mirar?  
`22` **B:** Que el modo no molestar no esté programado durante el horario en que esperás mensajes.  
`23` **A:** Ah, también lo activo a la noche y se me olvidó. Gracias, ahora entiendo.  
`24` **B:** De nada. ¿Necesitás algo más?  
`25` **A:** No, con eso alcanza.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** En L9 aparece «Lo puedo hacer. El año pasado me apareció un código de registro cuando cambié el chip y pensé que era por eso.» dentro de la consulta, sin que nadie pida repetirlo ni compartirlo. El caso prueba si se distingue una mención de código o clave de una solicitud observable.

**Notas de la referencia:** Referencia provisional; revisar la evidencia y sus límites en D07. Partición de desarrollo según propuesta pendiente de D08. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### CV2-D-L-WHATSAPP-005

legitima · whatsapp · mencion_sin_pedido · con errores escritos de ASR · 24 líneas

**Situación:** Una usuaria llama por una copia duplicada que muestra un código de error; se conversa sobre el mensaje y el espacio disponible.

` 1` **A:** hola intento hacer una copia de los chats y siempre termina con el mismo error  
` 2` **B:** te muestra una palabra o algún número  
` 3` **A:** dice código 17 pero no sé si eso sirve no es un mensaje de texto aparece en la pantalla ← _mencion_  
` 4` **B:** sí esa referencia nos ayuda a buscar el tipo de problema qué teléfono usás  
` 5` **A:** un Bruma tiene tres años y todavía anda bien  
` 6` **B:** la copia queda en la nube o en el almacenamiento del teléfono  
` 7` **A:** en la nube ayer borré un montón de fotos para hacer lugar  
` 8` **B:** cuánto espacio libre te quedó  
` 9` **A:** dos gigas la copia anterior ocupa más o menos eso  
`10` **B:** puede estar fallando porque necesita espacio adicional mientras se prepara  
`11` **A:** tengo que borrar la copia vieja  
`12` **B:** no todavía primero fijate cuánto ocupa el chat con videos podés excluir videos de la copia nueva  
`13` **A:** hay videos de las vacaciones pero ya están en la computadora de mi hermana  
`14` **B:** entonces podés desactivar incluir videos y probar otra vez  
`15` **A:** y el código 17 desaparece ← _mencion_  
`16` **B:** no sé si ese mensaje es por el espacio o por la conexión anotá si vuelve a salir y a qué hora  
`17` **A:** lo tengo anotado en un papel también me pasa cuando estoy con datos móviles  
`18` **B:** probá conectado al wifi de tu casa si se corta durante la copia puede quedar incompleta  
`19` **A:** ahora está en 62 por ciento no se trabó todavía  
`20` **B:** dejala terminar y después mirá la fecha de la copia desde ajustes  
`21` **A:** listo dice hoy a las 18:24 y ya no veo el error  
`22` **B:** perfecto querés que repasemos cómo restaurarla cuando cambies el equipo  
`23` **A:** sí pero eso lo hago otro día cuando tenga el teléfono nuevo  
`24` **B:** dale cuando llames vemos ese paso  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** En L3 aparece «dice código 17 pero no sé si eso sirve no es un mensaje de texto aparece en la pantalla» dentro de la consulta, sin que nadie pida repetirlo ni compartirlo. El caso prueba si se distingue una mención de código o clave de una solicitud observable.

**Notas de la referencia:** Referencia provisional; revisar la evidencia y sus límites en D07. Partición de desarrollo según propuesta pendiente de D08. Decisiones abiertas: [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

## Casos trampa

### TR-01-pedido-indirecto-digitos

vishing · 12 líneas

` 1` **A:** Hola, buenas tardes. ¿Hablo con Mariela Sosa?  
` 2` **B:** Sí, ella habla.  
` 3` **A:** Mariela, te llamo del área de seguridad de la tarjeta. Estamos viendo un consumo en curso en un local de deportes, por ciento cuarenta mil pesos. ¿Lo estás haciendo vos? ← `AUTHORITY_CLAIM`  
` 4` **B:** No, para nada. Estoy en el trabajo.  
` 5` **A:** Me imaginaba. Lo tengo retenido, pero si no lo confirmamos en los próximos minutos se termina acreditando. ← `URGENCY_PRESSURE`  
` 6` **A:** Te mandé un mensaje para validar que la que atiende es la titular. Fijate si ya te entró. ← _mencion_  
` 7` **B:** Sí, ahí me llegó uno recién.  
` 8` **A:** Perfecto. Abrilo y leeme lo que dice, de a uno, despacito, que lo voy cargando. ← **T_R** · `REQUEST_AUTH_CODE`  
` 9` **B:** ¿Todo? Abajo dice que no lo comparta con nadie. ← _contexto_  
`10` **A:** Eso viene en todos los mensajes, es automático. Lo de arriba nomás, de a uno. ← `PERSISTENCE_DISTRACTION`  
`11` **B:** Bueno. Uno... dos... tres... cuatro... cinco... seis. ← **T_C** · _cumplimiento_  
`12` **A:** Listo, Mariela. Quedó anulado; en un rato te llega la confirmación.  

**Referencia de trabajo:** `T_R` 8, `T_C` 11, pedido REQUEST_AUTH_CODE.

**Qué prueba:** Pedido indirecto del código de un solo uso: «abrilo y leeme lo que dice, de a uno» no dice código, token, clave ni números, y en todo el diálogo nadie usa esas palabras. Un detector por palabras clave no encuentra el pedido; hay que inferirlo del mensaje recién enviado y del dictado «de a uno». Además, quien llama neutraliza la advertencia del propio mensaje («eso viene en todos los mensajes»).

**Notas de la referencia:** La línea 6 anuncia el mensaje pero no pide nada todavía; el primer pedido es la línea 8. La línea 9 es una duda de B, no un rechazo, y la línea 10 es la redirección de esa duda. La etiqueta REQUEST_AUTH_CODE se infiere: el texto nunca nombra qué contiene el mensaje, solo que se lee «de a uno» y que en la línea 11 son seis cifras. Discutir en D07 si una anotación sin la palabra «código» es aceptable como referencia o si debe registrarse como ambigua. Es la versión larga de LAB-digitos-sin-palabra; el pedido se redactó con otras palabras para no repetir la frase del laboratorio. Montos, nombre y cifras ficticios.

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### TR-02-codigo-del-candado

legitima_dificil · 8 líneas

` 1` **A:** Che, Caro, ya estoy en tu edificio. Vengo a buscar las sillas plegables como quedamos. ← _contexto_  
` 2` **B:** Genial. Están en la baulera del subsuelo, la última del pasillo. Llevate las blancas, que las de madera están rotas.  
` 3` **A:** Dale. ¿Cuál era el código del candado? Me lo dijiste el otro día y no me acuerdo. ← _contexto_  
` 4` **B:** Cero, cero, cero, cero. Nunca lo cambié, ya sé que es un desastre. ← _contexto_  
` 5` **A:** Jaja, perfecto. ¿Y la puerta del subsuelo tiene código o está abierta? ← _contexto_  
` 6` **B:** Tiene. Es uno, dos, tres, cuatro y numeral. Después cerrá fuerte, que si no queda trabada. ← _contexto_  
` 7` **A:** Listo, ya las tengo. El domingo, después del cumple, te las devuelvo.  
` 8` **B:** Gracias. Avisame cuando las dejes, así le cambio el código al candado, que ya lo sabe medio edificio. ← _mencion_  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** Pedido real y explícito de un «código» («¿cuál era el código del candado?») seguido de su dictado en cifras, dos veces, entre personas que se conocen y para un objeto físico. No es un pedido de alto riesgo: no hay entidad, ni presión, ni código de un solo uso, ni credencial de una cuenta. Prueba que el detector no confunda el patrón «pedir código y dictar cifras» con REQUEST_AUTH_CODE.

**Notas de la referencia:** Las líneas 3 y 5 son pedidos de un código y las líneas 4 y 6 lo entregan; se anotan como contexto, no como pedido ni cumplimiento, porque la clase es legítima. El vocabulario del manual §5 no dice si la combinación de un candado de baulera o de la puerta de un edificio cuenta como REQUEST_SECRET (credencial permanente); acá no se etiquetó porque no protege una cuenta ni dinero. Discutir en D07 dónde termina un «secreto» de alto riesgo. El texto no prueba que A sea realmente conocida de B; se apoya en el contexto (habían quedado, A ya sabía el código, las sillas para el cumple). Cifras ficticias.

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### TR-03-negacion-y-consejo

legitima_dificil · 10 líneas

` 1` **A:** Hola, hijo. Te llamo porque en la tele dijeron algo de unas llamadas raras y me quedé preocupada.  
` 2` **B:** Bien que me llames, ma. Escuchame una cosa: nunca le pases la clave del banco a nadie, ni a mí. ← _mencion_  
` 3` **A:** ¿Ni aunque me llamen del banco?  
` 4` **B:** Menos. El banco no te va a pedir el código que te llega por mensaje, ni el PIN, ni que instales nada en el celular. ← _mencion_  
` 5` **A:** ¿Y si me dicen que tengo que transferir para que no me bloqueen la cuenta? ← _mencion_  
` 6` **B:** No transfieras nada. Cortás, y si querés llamás vos al número que está atrás de la tarjeta. ← _mencion_  
` 7` **A:** ¿Y si me piden que comparta la pantalla para ayudarme con la aplicación? ← _mencion_  
` 8` **B:** Tampoco. Nadie de afuera tiene que ver tu pantalla. Si no entendés algo, me esperás y lo vemos juntos el domingo. ← _mencion_  
` 9` **A:** Bueno, lo anoto en el papelito de la heladera.  
`10` **B:** Eso. Y no anotes la clave en el mismo papel, eh. ← _mencion_  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** Densidad alta de vocabulario de riesgo (clave, código por mensaje, PIN, instalar, transferir, bloquear la cuenta, compartir pantalla) siempre negado o dentro de un consejo («nunca le pases la clave», «no te va a pedir el código», «no transfieras nada»). Además, las líneas 5 y 7 describen pedidos hipotéticos de un tercero en forma de pregunta. Nadie pide nada a nadie: prueba que el detector distinga negación, consejo y pedido citado de un pedido real.

**Notas de la referencia:** Las líneas 5 y 7 tienen forma de pedido («que tengo que transferir», «que comparta la pantalla») pero reportan lo que podría decir un tercero; se anotan como mención sin etiqueta REQUEST_*. La línea 6 recomienda llamar al número del dorso de la tarjeta: es conducta segura, no un pedido. La línea 8 («me esperás y lo vemos juntos») no es ISOLATION_SECRECY: alienta consultar a un tercero de confianza. Vínculo y situación ficticios.

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### TR-04-pedido-tras-charla-larga

vishing · 30 líneas

` 1` **A:** Hola, buenas tardes. ¿Hablo con Rubén Aguirre?  
` 2` **B:** Sí, soy yo. ¿Quién habla?  
` 3` **A:** Te llamo de la sucursal del banco donde cobrás la jubilación, la de la avenida, al lado de la farmacia. Me llamo Silvina. ← `AUTHORITY_CLAIM`, `TRUST_BUILDING`  
` 4` **B:** Ah, sí, la conozco bien. Voy todos los meses.  
` 5` **A:** Por eso te llamo. Estamos llamando uno por uno a los clientes de la sucursal por el recambio de las tarjetas de débito, que vencen a fin de año.  
` 6` **B:** Mirá, yo la tarjeta la uso poco. Saco la plata por ventanilla.  
` 7` **A:** Sí, me figura que venís por ventanilla, a principio de mes. Mucha gente prefiere así, y está bien. ← `TRUST_BUILDING`  
` 8` **B:** Y sí, a mi edad uno ya no se lleva bien con los cajeros. ¿Vos sos nueva? Antes atendía un muchacho, Ramiro.  
` 9` **A:** Ramiro pasó a otra sucursal, en el centro. Siempre se acuerda de la gente del barrio. ← `TRUST_BUILDING`  
`10` **B:** Qué bueno. Era muy amable. Me ayudó un montón con los papeles cuando mi señora estuvo enferma.  
`11` **A:** Lo lamento mucho, Rubén. Debe haber sido un momento difícil.  
`12` **B:** Sí, ya van tres años. Ahora estoy solo, pero mis hijas vienen seguido.  
`13` **A:** Qué bueno que te acompañen. ¿Viven cerca?  
`14` **B:** Una sí, a cinco cuadras. La otra se fue a vivir al sur. Me dice que allá todavía nieva.  
`15` **A:** ¡Ni me digas! Acá por suerte ya empezó el calorcito. Mi mamá ya anda con las plantas, dice que es época de trasplantar.  
`16` **B:** Yo tengo unos malvones en el balcón que eran de mi señora. Los cuido como oro.  
`17` **A:** Qué lindo. Mi mamá también tiene; dice que hay que regarlos poco, que si no se pudren.  
`18` **B:** Eso mismo decía mi señora. Sos una buena chica, Silvina.  
`19` **A:** Gracias, Rubén. Bueno, no te quiero robar mucho tiempo, que lo de la tarjeta es cortito.  
`20` **B:** Decime nomás, no tengo apuro. Estoy con la radio, escuchando el partido.  
`21` **A:** La tarjeta nueva te la mandamos a tu casa, así no tenés que hacer la fila. Me figura el domicilio de la calle Las Acacias, ¿seguís ahí? ← `TRUST_BUILDING`  
`22` **B:** Sí, sigo ahí. Hace cuarenta años que vivo en esa casa.  
`23` **A:** Perfecto. Ahora te va a llegar un mensajito del banco al celular para confirmar el envío. ¿Lo tenés a mano? ← _mencion_  
`24` **B:** Sí, acá está. Esperá que busco los anteojos.  
`25` **B:** Ya está. Sí, sonó recién. Dice del banco.  
`26` **A:** Bárbaro. Leeme el código que te llegó, así lo cargo y la tarjeta sale mañana mismo. ← **T_R** · `REQUEST_AUTH_CODE`  
`27` **B:** Es uno, dos, tres, cuatro, cinco, seis. ← **T_C** · _cumplimiento_  
`28` **A:** Perfecto, Rubén. Ya quedó cargado. Te llega en la semana.  
`29` **B:** Muchas gracias, Silvina. Y si lo ves a Ramiro, saludalo de mi parte.  
`30` **A:** Seguro. Y cuidá esos malvones, eh.  

**Referencia de trabajo:** `T_R` 26, `T_C` 27, pedido REQUEST_AUTH_CODE.

**Qué prueba:** Conversación larga (30 líneas) y amable: la presentación como sucursal del banco está en la línea 3 y el primer pedido de alto riesgo recién en la línea 26, separados por veintidós líneas: el trámite de la tarjeta y, en el medio, once líneas de charla cotidiana (líneas 8 a 18: el empleado anterior, la viudez de Rubén, las hijas, el clima, los malvones), sin urgencia ni amenaza. Prueba si el detector conserva el contexto de autoridad del comienzo y no se diluye con el texto intermedio, y si reacciona a un pedido directo que llega cuando la confianza ya está construida.

**Notas de la referencia:** No hay semilla del catálogo que corresponda claramente: es banco y REQUEST_AUTH_CODE como SC-BANK-OTP-01, pero el pretexto es el recambio de la tarjeta, no una compra sospechosa, y faltan la urgencia y el aislamiento de esa ficha. En la línea 9 quien llama adopta el nombre «Ramiro» que aportó B en la línea 8; se anota TRUST_BUILDING. La línea 21 pide confirmar un domicilio que quien llama ya dice tener; no se marca como pedido porque solo busca un «sí» sobre ese dato (se anota TRUST_BUILDING). El manual §5 excluye «confirmar datos que la entidad ya tiene» solo en REQUEST_SECRET; REQUEST_PERSONAL_DATA incluye el domicilio y no trae esa excepción, y el prompt del detector lista el domicilio como dato que justifica alerta. Si el equipo decide que confirmar el domicilio es REQUEST_PERSONAL_DATA, T_R pasaría a la línea 21 y T_C a la 22. Discutir en D07. La línea 23 anuncia el mensaje sin pedirlo. No hay URGENCY_PRESSURE ni THREAT_FEAR: la falta de presión es parte de la dificultad. Nombres, calle y cifras ficticios.

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### TR-05-asado-con-transferencia

legitima_dificil · 27 líneas

` 1` **A:** ¡Eh, Martín! ¿Cómo va? ¿Venís el sábado al asado en lo de Gonza? ← _contexto_  
` 2` **B:** ¡Obvio! ¿A qué hora arrancan?  
` 3` **A:** Tipo una. Gonza prende el fuego a las doce, así que si caés antes, ayudás.  
` 4` **B:** Jaja, dale. ¿Llevo carbón?  
` 5` **A:** No, el carbón ya lo compró él. Escuchá, te llamaba por la plata, que la estoy juntando yo. ← _contexto_  
` 6` **B:** Sí, decime cuánto es.  
` 7` **A:** Fui a la carnicería con Lucho: vacío, chorizo, morcilla y unas mollejas. Salió todo ciento treinta y seis mil.  
` 8` **B:** Uh. ¿Y cuántos somos?  
` 9` **A:** Ocho, contando a la novia de Gonza. Son diecisiete lucas por cabeza, más la bebida.  
`10` **B:** ¿Y la bebida cuánto es?  
`11` **A:** La trae Pato, que tiene la distribuidora del cuñado. Calculá cinco más, veintidós en total.  
`12` **B:** Bueno, veintidós mil. ¿Te los doy en efectivo el sábado?  
`13` **A:** Si podés, pasámelos por transferencia antes del viernes, así le devuelvo a Lucho, que pagó todo él con la tarjeta. ← `REQUEST_TRANSFER`  
`14` **B:** Dale, no hay drama. Mandame el alias que ahora no lo tengo a mano. ← _mencion_  
`15` **A:** Te lo mando por el grupo. Es el mismo de la vaquita del cumple de Lucho.  
`16` **B:** Ah, ese lo tengo agendado, entonces.  
`17` **A:** Fijate que te aparezca mi nombre, Nicolás Peralta, antes de confirmar, no sea cosa que se lo mandes a otro. ← _contexto_  
`18` **B:** Sí, sí. Ahí está, te lo mandé. Veintidós mil. ← _contexto_  
`19` **A:** Joya, me llegó. Gracias, sos el primero en pagar, como siempre.  
`20` **B:** Jaja. ¿Y los demás?  
`21` **A:** Pato me paga en efectivo el sábado, y Gonza y la novia me transfieren a la noche.  
`22` **B:** Bien. ¿Llevo algo más? ¿Pan, ensalada?  
`23` **A:** Traé pan y algo de postre si querés. La ensalada la hace la novia de Gonza.  
`24` **B:** Listo. ¿Es la casa del pasaje o la otra?  
`25` **A:** La del pasaje, la del portón verde. Te mando la ubicación por el grupo.  
`26` **B:** Dale. Nos vemos el sábado, entonces.  
`27` **A:** Nos vemos. ¡Y no te olvides el pan!  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** Pedido de transferencia legítimo y explícito entre amigos («pasámelos por transferencia antes del viernes», «mandame el alias»), con monto, plazo y una transferencia que efectivamente se hace en la línea 18. Comparte con SC-FAMILIAR-DINERO-01 el pedido de dinero y un plazo, pero hay contexto compartido verificable (el asado, la carnicería, los nombres del grupo), nadie se presenta como autoridad y quien cobra hasta recomienda verificar el nombre del destinatario. Prueba que el detector no convierta cualquier REQUEST_TRANSFER seguido de un «te lo mandé» en un fraude con T_R y T_C.

**Notas de la referencia:** La línea 13 se anota como contexto con REQUEST_TRANSFER porque describe lo dicho (manual §5: un pedido de transferencia también aparece en conversaciones legítimas), pero no es evento crítico: t_r_linea y pedido quedan null. La línea 18 sería un cumplimiento si la clase fuera vishing; acá es contexto. «Antes del viernes» es un plazo real del grupo, no URGENCY_PRESSURE. En la línea 14 es quien paga el que pide el alias; el alias nunca se dice en el diálogo. El texto no permite verificar que A sea quien dice ser: la legitimidad se apoya en el contexto compartido; registrar ese límite en D07. Nombres y montos ficticios.

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### TR-06-banco-alerta-legitima

legitima_dificil · 12 líneas

` 1` **A:** Hola, buenas tardes. ¿Hablo con Julieta Medina?  
` 2` **B:** Sí, soy yo. ¿Quién es?  
` 3` **A:** Te habla Gastón, del área de seguridad de tarjetas del banco. Te llamo por un consumo que nos llamó la atención en tu tarjeta de crédito. ← `AUTHORITY_CLAIM`  
` 4` **B:** ¿Qué consumo?  
` 5` **A:** Una compra de sesenta y dos mil pesos en una tienda en línea, hoy a las once y cuarto. ¿La reconocés? ← _contexto_  
` 6` **B:** No, no compré nada. ¿Me la anulan ustedes?  
` 7` **A:** Antes que nada: no te voy a pedir ningún código, ni la clave, ni los números de la tarjeta. Si en algún momento alguien te los pide, cortá. ← _mencion_  
` 8` **B:** Bueno. ¿Y entonces cómo la freno?  
` 9` **A:** Entrá a la aplicación del banco, en Tarjetas, y tocá Pausar. Eso la frena al instante. ← _contexto_  
`10` **B:** Hace un rato me llegó un mensaje con un código. ¿Te lo paso así lo verificás? ← _mencion_  
`11` **A:** No, no me lo pases. Seguramente es del intento de compra, y ese código no se comparte con nadie, tampoco con el banco. Pausá la tarjeta desde la aplicación y, para desconocer la compra, llamá vos al número que está en el dorso. ← _rechazo_  
`12` **B:** Listo, ya la pausé. Ahora corto y llamo al del dorso. ← _contexto_  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** Mismo arranque que el fraude de compra sospechosa (SC-BANK-OTP-01): quien llama se presenta como el banco, describe una compra que la persona no hizo y pregunta si la reconoce. La diferencia está en que avisa que no va a pedir código, clave ni números, deriva a pausar la tarjeta desde la aplicación y a llamar al número del dorso, y rechaza el código cuando la propia persona ofrece dictarlo. Prueba que el detector no alerte por la identidad de banco más una compra sospechosa, y que una oferta espontánea del código no se tome como pedido.

**Notas de la referencia:** La línea 9 indica pausar la tarjeta desde la aplicación oficial: según el manual §5, recomendar una acción de seguridad por el canal oficial no es REQUEST_SECURITY_ACTION, aunque tiene forma de instrucción. En la línea 10 es B quien ofrece el código; A lo rechaza (línea 11). El texto no permite comprobar que quien llama sea realmente el banco: la legitimidad sale de la ficha y de la conducta (no pide nada, deriva a canales que la persona controla). TR-01-pedido-indirecto-digitos tiene un arranque parecido y puede servir de contraste, aunque no se declaró como par. Nombre, monto y hora ficticios.

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### TR-07-pedido-partido-en-dos-lineas

vishing · 10 líneas

` 1` **A:** Buenas tardes, ¿Sergio Paz? Te hablo de atención al cliente del banco, me llamo Andrea. ← `AUTHORITY_CLAIM`  
` 2` **B:** Sí, soy yo. ¿Qué pasó?  
` 3` **A:** Esta mañana se vinculó un dispositivo nuevo a tu cuenta, desde otra provincia. ¿Fuiste vos?  
` 4` **B:** No, yo tengo solo este celular. ¿Me entraron a la cuenta?  
` 5` **A:** Todavía no pudieron operar, por eso te llamo ya. El sistema te acaba de mandar un mensaje para desvincularlo. ← `URGENCY_PRESSURE`  
` 6` **B:** Sí, me entró uno recién. ¿Qué tengo que hacer?  
` 7` **A:** Solamente pasame lo que te llegó ← **T_R** · `REQUEST_AUTH_CODE`  
` 8` **A:** los seis números del mensaje del banco, así lo desvinculo antes de que te hagan una transferencia. ← `REQUEST_AUTH_CODE`, `THREAT_FEAR`, `URGENCY_PRESSURE`  
` 9` **B:** A ver... cero, cero, cero, cero, cero, cero. ← **T_C** · _cumplimiento_  
`10` **A:** Perfecto, ya quedó desvinculado. Por las dudas no entres a la aplicación hasta mañana, que se está actualizando. ← `ISOLATION_SECRECY`  

**Referencia de trabajo:** `T_R` 7, `T_C` 9, pedido REQUEST_AUTH_CODE.

**Qué prueba:** El pedido del código llega partido en dos líneas del mismo hablante, como lo cortaría un ASR por una pausa: la línea 7 («pasame lo que te llegó», sin puntuación final) es un pedido indirecto incompleto y recién la línea 8 («los seis números del mensaje del banco») lo vuelve explícito. Como en TR-08-frase-cortada-candado, el corte no lleva puntos suspensivos ni otra marca que avise que la frase sigue. Prueba si el detector, que se actualiza línea por línea, reacciona ya con la primera mitad o necesita la segunda, y si une las dos mitades en vez de evaluarlas por separado.

**Notas de la referencia:** Ambigüedad de T_R: se marca la línea 7, donde empieza el pedido, porque ya pide el contenido del mensaje recién enviado, con el mismo criterio que la línea 8 de TR-01-pedido-indirecto-digitos. Con la línea 7 sola el pedido es indirecto (no dice qué hay que pasar); se vuelve inequívoco en la línea 8. El manual §2 dice que la marca no se toma automáticamente al comienzo de una intervención, así que otra persona podría marcar la línea 8; la diferencia cambia en una línea la anticipación medida. Decidir en D07 si, ante un pedido partido, T_R va donde empieza o donde se completa. Las dos líneas llevan evidencia de pedido para que la referencia admita cualquiera de las dos lecturas. No hay semilla del catálogo que corresponda claramente: es banco y REQUEST_AUTH_CODE como SC-BANK-OTP-01, pero el pretexto es un dispositivo vinculado, no una compra. La línea 10 desalienta entrar a la aplicación, que es el canal para verificar; se anota ISOLATION_SECRECY. Par: TR-08-frase-cortada-candado (corte parecido en una conversación legítima). Nombres y cifras ficticios.

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### TR-08-frase-cortada-candado

legitima_dificil · 7 líneas

` 1` **A:** Hola, Lu, ¿estás muy ocupada?  
` 2` **B:** No, decime. Estoy saliendo del laburo.  
` 3` **A:** Pasame el código ← _contexto_  
` 4` **A:** del candado de la valija que me prestaste. La cerré sin pensar y ahora, en el hotel, no la puedo abrir. ← _contexto_  
` 5` **B:** ¡Ay, perdón! Te lo tenía que mandar antes de que salieras. Es uno, dos, tres. ← _contexto_  
` 6` **A:** Listo, ya abrió. Gracias, te la devuelvo el lunes.  
` 7` **B:** Dale. Disfrutá, chau.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** Fragmento parcial que, leído solo, parece un pedido de código de un solo uso («Pasame el código», línea 3) y que la línea siguiente del mismo hablante aclara como el código del candado de una valija prestada. Prueba si el detector avisa con información todavía incompleta y si retira o corrige el riesgo cuando llega la aclaración. Es el ejemplo «pasame el código… del candado» de ARQUITECTURA.md §2.

**Notas de la referencia:** Las líneas 3 y 4 son una sola frase partida en dos actualizaciones del mismo hablante; la línea 3 no lleva puntuación final a propósito, como un parcial de ASR. La línea 3 es un pedido real, pero de un código sin riesgo: se anota como contexto, igual que los pedidos de TR-02. B dicta el código del candado (línea 5): es el cumplimiento de un pedido sin riesgo y no se marca como T_C. La política de alerta decide si un aviso en la línea 3 cuenta como falso positivo aunque se retire en la línea 4 (D08). Antes de la línea 3 no hay contexto que anticipe el candado, para que la ambigüedad sea real. Se usó una valija y no una bicicleta para no repetir el escenario de TR-02-codigo-del-candado. Nombre y cifras ficticios.

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### TR-09-victima-se-niega

vishing · 12 líneas

` 1` **A:** Hola, ¿hablo con Marta Giménez?  
` 2` **B:** Sí, ¿quién habla?  
` 3` **A:** Te llamo del área de prevención del banco, me llamo Diego. Tenemos retenida una compra de doscientos treinta mil pesos con tu tarjeta de débito, en una página de venta de pasajes. ¿La hiciste vos? ← `AUTHORITY_CLAIM`  
` 4` **B:** No, yo no compré nada.  
` 5` **A:** Bien, entonces la damos de baja. Te acaba de llegar un SMS con un código de seis números; leémelo así anulo la compra. ← **T_R** · `REQUEST_AUTH_CODE`  
` 6` **B:** Ay, no sé... ¿Y para qué me lo pedís a mí? Si el mensaje lo mandaron ustedes, ya lo tienen. ← _contexto_  
` 7` **A:** No, lo genera el sistema y te llega solo a vos. Yo lo necesito para cargar la baja, y tenemos dos minutos antes de que se acredite. ← `PERSISTENCE_DISTRACTION`, `TRUST_BUILDING`, `URGENCY_PRESSURE`  
` 8` **B:** Prefiero cortar y llamar yo al número que figura atrás de la tarjeta. ← _rechazo_  
` 9` **A:** Si cortás, el reclamo se cae y la compra ya no se puede revertir. Es un segundo: decime los seis números y queda resuelto. ← `REQUEST_AUTH_CODE`, `PERSISTENCE_DISTRACTION`, `URGENCY_PRESSURE`, `THREAT_FEAR`, `ISOLATION_SECRECY`  
`10` **B:** No, no te voy a pasar ningún código. ← _rechazo_  
`11` **A:** Marta, te estoy queriendo ayudar. Ya va un minuto y, si se acredita, no hay vuelta atrás. ← `PERSISTENCE_DISTRACTION`, `URGENCY_PRESSURE`  
`12` **B:** Te dije que no. Llamo yo al banco. Chau. ← _rechazo_  

**Referencia de trabajo:** `T_R` 5, `T_C` —, pedido REQUEST_AUTH_CODE.

**Qué prueba:** Pedido directo de código (línea 5) seguido de duda, insistencia con presión de tiempo y desaliento a verificar por otro canal, y negativa final sin cumplimiento. Prueba que el detector sostenga el riesgo a través de las negativas de la persona (las frases «no te voy a pasar ningún código» y «te dije que no» no deben bajar la alerta) y que no necesite un T_C para avisar.

**Notas de la referencia:** T_C queda sin dato: la persona nunca dicta el código. Según METRICAS.md §2, sin cumplimiento no se infiere prevención lograda y L_C no se calcula. La línea 6 es una duda, no un rechazo; la línea 7 la redirige con una explicación técnica («lo genera el sistema»), por eso TRUST_BUILDING, y vuelve a pedir el código («yo lo necesito») sin nombrarlo. La línea 9 repite el pedido; se anota como segundo pedido para explicar posibles alertas tardías. ISOLATION_SECRECY en la línea 9 sale de «si cortás, el reclamo se cae», que desalienta verificar por otro canal. Monto y comercio distintos de los de TR-01 y TR-06, que usan el mismo pretexto de compra retenida. Nombre y monto ficticios.

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### TR-10-ofrecimiento-inducido

vishing · 14 líneas

` 1` **A:** ¿Hola?  
` 2` **B:** Buenas tardes, ¿Julián Paredes?  
` 3` **A:** Sí, soy yo. ¿Quién habla?  
` 4` **B:** Te hablo del área de verificación de cuentas de WhatsApp. Estamos viendo que alguien intenta abrir tu cuenta en otro teléfono y lo tenemos retenido. ← `AUTHORITY_CLAIM`, `THREAT_FEAR`  
` 5` **A:** ¿Cómo en otro teléfono? Yo no hice nada.  
` 6` **B:** Por eso te llamo. Fijate que te tuvo que haber llegado un SMS hace un ratito. ← _mencion_  
` 7` **A:** Sí, acá está. Un mensaje con unos números. ← _mencion_  
` 8` **B:** Bien. Para frenarlo necesito que me confirmes lo que te mandamos; la retención dura unos minutos nada más. ← **T_R** · `REQUEST_AUTH_CODE`, `URGENCY_PRESSURE`  
` 9` **A:** ¿Confirmar cómo? ¿Le respondo el mensaje?  
`10` **B:** No, no respondas nada ni lo reenvíes, que eso lo traba. Con lo que te llegó ahí, yo de este lado lo cargo y queda frenado. ← `REQUEST_AUTH_CODE`, `PERSISTENCE_DISTRACTION`, `TRUST_BUILDING`  
`11` **A:** Ah... ¿Te leo el código, entonces? ← _contexto_  
`12` **B:** Dale, cuando quieras. ← `REQUEST_AUTH_CODE`  
`13` **A:** Es uno, dos, tres, cuatro, cinco, seis. ← **T_C** · _cumplimiento_  
`14` **B:** Perfecto, ya quedó. Tu cuenta sigue siendo tuya.  

**Referencia de trabajo:** `T_R` 8, `T_C` 13, pedido REQUEST_AUTH_CODE.

**Qué prueba:** Pedido inducido: quien llama nunca dice «decime el código»; habla de «confirmar lo que te mandamos» y de que, «con lo que te llegó», lo carga de su lado, hasta que es la propia persona quien ofrece leer el código (línea 11) y quien llama acepta (línea 12). Prueba si el detector reconoce un pedido de código sin las palabras del pedido directo y si no atribuye el pedido a quien lo ofrece.

**Notas de la referencia:** Para discutir en D07: dónde cae T_R en un pedido inducido. Se eligió la línea 8 porque es la primera en la que quien llama pide que le transmitan («me confirmes») el contenido del SMS que ya quedó identificado en las líneas 6 y 7; en ese contexto «lo que te mandamos» solo puede ser el código, y la duda de A en la línea 9 muestra que el pedido es indirecto, no que falte. Alternativas: línea 10, si se exige que quede claro que el código tiene que llegar a quien llama («yo de este lado lo cargo»); línea 12, si solo se cuenta un pedido explícito, aunque ahí es una aceptación. La línea 11 no puede ser T_R: es un ofrecimiento de quien recibió el código, no un pedido. La elección cambia L_R y Preventive@δ. Las líneas 6 y 7 mencionan el SMS sin pedirlo. «No respondas nada ni lo reenvíes» (línea 10) suena a consejo de seguridad y puede confundir al detector. Acá A es quien atiende y B quien llama, al revés que en TR-09 y en la mayoría de los fraudes escritos, para que la letra del hablante no anticipe el rol. Nombre y código ficticios.

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### TR-11-familiar-real-pide-plata

legitima_dificil · 10 líneas

` 1` **A:** ¿Hola?  
` 2` **B:** Hola, má. ¿Te agarro en mal momento? ← `AUTHORITY_CLAIM`  
` 3` **A:** No, hijo, estoy acá tomando mate. ¿Qué pasó?  
` 4` **B:** Nada grave. Me vino más alta la boleta de la luz y no llego hasta el viernes. ¿Me podrás transferir veinte mil pesos? ← `REQUEST_TRANSFER`  
` 5` **A:** Sí, mi amor. ¿A qué cuenta?  
` 6` **B:** A la mía de siempre, la que tenés agendada. No hay apuro, eh: hoy o mañana, cuando puedas. El viernes cobro y te los devuelvo. ← _contexto_  
` 7` **A:** Ay, perdoná, pero con todo lo que se escucha me da no sé qué hacerlo así, por teléfono. ← _contexto_  
` 8` **B:** No, hacés bien. Cortá y llamame vos al celular, al número de siempre, y lo hablamos de nuevo. ← _contexto_  
` 9` **A:** Dale, te corto y te llamo.  
`10` **B:** Dale, má. Te espero.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** Un familiar real pide una transferencia para un gasto cotidiano (la boleta de la luz), sin urgencia, sin secreto, a una cuenta que la persona ya tiene agendada, y, ante la duda de la madre, él mismo propone que corte y lo llame a su número de siempre. Caso límite: el pedido de dinero y la identidad de familiar declarada coinciden con SC-FAMILIAR-DINERO-01, y el diálogo solo no permite verificar la identidad; la clase legítima sale del diseño del caso, no de algo comprobable en el texto.

**Notas de la referencia:** Semilla null: la más cercana es LG-FAMILIAR-LLAMADO-01, pero su objetivo es contar una urgencia «sin pedir dinero ni claves», y este caso sí pide dinero. La línea 4 es un pedido de transferencia legítimo; se anota como contexto con REQUEST_TRANSFER, sin T_R (manual §2: una solicitud legítima puede describirse como evidencia sin convertirla en evento crítico). Las señales a favor de la legitimidad (sin presión, cuenta conocida, acepta e invita a verificar) podrían ser imitadas por un impostor; el manual §2 pide registrar ese límite. Para D07: si un detector que avisa acá cuenta como falso positivo o como aviso razonable, porque el aviso sugeriría justamente lo que el propio familiar propone. En la línea 2 el hijo no dice su nombre («Hola, má»), como en una llamada real desde su número; AUTHORITY_CLAIM sale de que se presenta como hijo. Monto y vínculo ficticios.

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### TR-12-corta-antes-del-pedido

vishing · 10 líneas

` 1` **A:** ¿Hola?  
` 2` **B:** Abu... Abu, ¿me escuchás? Soy yo. ← _contexto_  
` 3` **A:** ¿Quién habla? ¿Martín?  
` 4` **B:** Sí, abu, Martín. Tuve un problema con la moto: atropellé a una señora en una esquina y me trajeron a la comisaría. ← `AUTHORITY_CLAIM`, `THREAT_FEAR`  
` 5` **A:** ¡Ay, Dios mío! ¿Vos estás bien? ¿Y la señora?  
` 6` **B:** Yo estoy bien, un poco golpeado. A ella se la llevaron al hospital. Escuchame: no cortes y no le cuentes a nadie, ni al abuelo, que con lo del corazón no se puede enterar. ← `ISOLATION_SECRECY`  
` 7` **B:** Esto hay que arreglarlo hoy, antes de que me pasen al juzgado. Te paso con el abogado que me está ayudando, ¿sí? ← `URGENCY_PRESSURE`  
` 8` **A:** Esperá, Martín. Antes de nada quiero hablar con tu papá. Te corto y lo llamo. ← _rechazo_  
` 9` **B:** ¡No, abu, no cortes! Si cortás va a ser peor para mí. Quedate en línea un minuto. ← `ISOLATION_SECRECY`, `PERSISTENCE_DISTRACTION`, `THREAT_FEAR`  
`10` **A:** No, querido. Te corto. ← _rechazo_  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** El llamante arma pretexto (nieto que atropelló a una señora con la moto y está en la comisaría), urgencia y aislamiento («no cortes», «no le cuentes a nadie»), pero la persona corta antes de cualquier pedido. Prueba si el detector avisa solo por maniobras, sin un pedido de alto riesgo, y cómo se cuenta ese aviso cuando no hay T_R contra el cual medir el margen.

**Notas de la referencia:** La clase vishing sale del escenario (suplantación de familiar con las maniobras de la semilla), no de un pedido observado: la acción crítica (transferencia) nunca llega. En la línea 2 el llamante no dice su nombre y es A quien lo aporta en la línea 3, como en el par escrito de la semilla; el pretexto (moto, comisaría, abogado) y el secreto (no contarle al abuelo) se eligieron distintos de los de SC-FAMILIAR-DINERO-01-e01 para no repetirlo. «Te paso con el abogado» y «hay que arreglarlo hoy» anticipan un pedido de dinero, pero no lo formulan. THREAT_FEAR en las líneas 4 y 9 apunta al nieto, no a quien atiende; el manual §5 habla de peligro «dirigido a la persona», igual duda que en SC-FAMILIAR-DINERO-01-e01. Las líneas 8 y 10 rechazan seguir en la llamada, no un pedido. Para D07 y METRICAS: sin T_R ni T_C, L_R y L_C quedan sin dato; hay que decidir si una alerta acá cuenta como detección correcta de clase y si una llamada así entra en Preventive@δ. Nombre y vínculo ficticios.

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### TR-13-turno-medico-pide-dni

legitima_dificil · **propuesto para grabar** · 12 líneas

` 1` **A:** Centro de salud, buen día, te atiende Carla. ← `AUTHORITY_CLAIM`  
` 2` **B:** Hola, buen día. Quería sacar un turno con clínica médica, para un control. ← _contexto_  
` 3` **A:** Sí, cómo no. ¿Ya te atendiste alguna vez acá?  
` 4` **B:** Sí, el año pasado vine con la doctora por la presión.  
` 5` **A:** Bien. Decime tu número de documento y la fecha de nacimiento, así te busco en el sistema. ← `REQUEST_PERSONAL_DATA`  
` 6` **B:** Doce millones trescientos cuarenta y cinco mil seiscientos setenta y ocho. Nací el tres de marzo del cincuenta y ocho. ← _contexto_  
` 7` **A:** Ahí te encontré: Graciela Funes, ¿no? ¿Seguís con la misma obra social?  
` 8` **B:** Sí, la misma.  
` 9` **A:** Tengo turno el jueves a las diez y cuarto con la doctora Ibáñez. ¿Te sirve?  
`10` **B:** Sí, perfecto.  
`11` **A:** Listo, quedó agendado. El día anterior te llega un mensaje de recordatorio. Traé el documento y la credencial, y llegá diez minutos antes. ← _mencion_  
`12` **B:** Muchas gracias. Hasta luego.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** Pedido legítimo de datos personales (número de documento y fecha de nacimiento) para buscar a la persona en el sistema, dentro de una llamada que la propia persona hace a un centro de salud para pedir un turno; los datos se dicen en voz alta. Prueba que el detector no trate cualquier REQUEST_PERSONAL_DATA como pedido de alto riesgo cuando el contexto lo vuelve razonable.

**Notas de la referencia:** Semilla null: ninguna del catálogo cubre salud. El texto no dice quién inició la llamada; solo se deduce del saludo de la línea 1 (A atiende con el nombre del centro) y del pedido de turno de B. Sin las letras de hablante (--hablantes) es más difícil inferirlo. Es la variante que LG-ORG-TURNO-01-e01 evitó a propósito: queda para D07 si un pedido de documento en una consulta iniciada por la persona se anota solo como contexto, como acá, y qué pasaría con el mismo pedido en una llamada entrante. El documento dictado (12.345.678) es el número de ejemplo secuencial, no un dato real; la fecha de nacimiento se eligió coherente con ese rango. «Decime tu número de documento» comparte la forma de los pedidos de los casos fraudulentos («decime el código»). AUTHORITY_CLAIM en la línea 1 la hace quien atiende, no quien llama (misma duda que en LG-ORG-TURNO-01-e01 y LG-SUPPORT-INFO-01-e01).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

## Piloto escrito: estafas

### SC-CLAVE-CAMBIO-01-e01

vishing · 13 líneas

` 1` **A:** ¿Hola?  
` 2` **B:** Buenas tardes, ¿hablo con Raúl Quiroga? Te llamo del área de seguridad del banco por un movimiento en tu cuenta. ← `AUTHORITY_CLAIM`  
` 3` **A:** Sí, soy yo. ¿Qué movimiento?  
` 4` **B:** Hace veinte minutos se registró un ingreso a tu home banking desde un dispositivo que no tenemos asociado. Te contacto antes de que se haga alguna operación. ← _contexto_  
` 5` **A:** Yo no entré desde ningún lado nuevo. ¿Y ahora qué hago?  
` 6` **B:** Hay que hacer el procedimiento de resguardo ahora, mientras seguimos en línea. Si cortamos, el sistema bloquea la cuenta cuarenta y ocho horas y no vas a poder usar la tarjeta. ← `URGENCY_PRESSURE`, `THREAT_FEAR`, `ISOLATION_SECRECY`  
` 7` **A:** Pará un poco. ¿No es mejor que llame yo al número que está atrás de la tarjeta? ← _contexto_  
` 8` **B:** Podés, pero ahí entrás como un caso nuevo y la demora es de dos o tres días hábiles. En ese tiempo te pueden vaciar la cuenta. No te conviene cortar. ← `ISOLATION_SECRECY`, `PERSISTENCE_DISTRACTION`, `THREAT_FEAR`  
` 9` **B:** Te acabo de mandar un mensaje de texto con el enlace de seguridad. Abrilo y cambiá la clave ahí; yo te voy guiando. ← **T_R** · `REQUEST_SECURITY_ACTION`  
`10` **A:** Sí, me llegó. ¿Lo abro desde el celular?  
`11` **B:** Sí, desde el celular. Poné tu usuario, la clave que usás ahora y después la nueva, dos veces. ← `REQUEST_SECURITY_ACTION`  
`12` **A:** Bueno, a ver... listo, ya puse todo. Me sale que el cambio de clave se realizó con éxito. ← **T_C** · _cumplimiento_  
`13` **B:** Perfecto, Raúl. Ahora no entres al home banking por dos horas ni se lo comentes a nadie, así el caso se cierra sin problemas. ← `ISOLATION_SECRECY`  

**Referencia de trabajo:** `T_R` 9, `T_C` 12, pedido REQUEST_SECURITY_ACTION.

**Qué prueba:** Pedido de acción de seguridad (abrir un enlace y cambiar la clave ahí) guiado por quien llama, precedido por amenaza de bloqueo, pedido de no cortar y desaliento a verificar por el número de la tarjeta. Persona dudosa que termina cumpliendo. Comparte vocabulario con su par (dispositivo nuevo, cambiar la clave, enlace, número de la tarjeta).

**Notas de la referencia:** La línea 6 pide «hacer el procedimiento de resguardo» sin decir cuál; no se tomó como pedido porque la acción concreta aparece en la línea 9. Discutir en D07 si un pedido vago anticipa T_R. La línea 11 pide cargar el usuario y la clave actual en el enlace: podría anotarse también como REQUEST_SECRET, porque la credencial termina en un formulario de quien llama. El enlace es ficticio y no aparece en el texto. A habla primero y es quien recibe la llamada.

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### SC-FAMILIAR-DINERO-01-e01

vishing · 12 líneas

` 1` **A:** ¿Hola?  
` 2` **B:** Hola, tía, ¿cómo andás? Soy yo... ¿no me reconocés?  
` 3` **A:** ¿Quién habla? ¿Nicolás? ← _contexto_  
` 4` **B:** Sí, tía, Nico. Te llamo de otro número porque se me rompió el celular. Estoy en un problema y no sabía a quién llamar. ← `AUTHORITY_CLAIM`  
` 5` **A:** ¿Qué pasó? Te escucho raro.  
` 6` **B:** Choqué con el auto de papá y el señor del otro auto dice que si no le pago el arreglo ahora, hace la denuncia y me quedo sin registro. Estoy acá al lado de él. ← `THREAT_FEAR`, `URGENCY_PRESSURE`  
` 7` **B:** Por favor, no le digas nada a mamá, que se va a poner como loca. Lo quiero arreglar yo antes de que se entere. ← `ISOLATION_SECRECY`  
` 8` **A:** Pero ¿qué querés que haga yo?  
` 9` **B:** Son ciento ochenta mil pesos. ¿Me los podés transferir ahora a la cuenta del señor? Te paso los datos por mensaje y el lunes te los devuelvo. ← **T_R** · `REQUEST_TRANSFER`  
`10` **A:** Mirá, Nico, así no. Cortame y te llamo yo a tu número de siempre, o llamo a tu mamá. ← _rechazo_  
`11` **B:** No, tía, no me cortes, que el celular quedó destrozado en el choque. Y si llamás a mamá se arma lío. El señor me está apurando, dame cinco minutos nada más. ← `PERSISTENCE_DISTRACTION`, `ISOLATION_SECRECY`, `URGENCY_PRESSURE`  
`12` **A:** Entonces que tu mamá se ocupe. Yo no transfiero nada sin hablar antes con ella. Te corto y la llamo. ← _rechazo_  

**Referencia de trabajo:** `T_R` 9, `T_C` —, pedido REQUEST_TRANSFER.

**Qué prueba:** Suplantación de un sobrino que llama desde otro número, con amenaza de denuncia, pedido de secreto y pedido de transferencia. La persona se resiste, propone verificar por otro canal y no cumple; quien llama insiste. Sin T_C.

**Notas de la referencia:** El nombre del supuesto sobrino lo aporta A en la línea 3 y quien llama lo adopta en la línea 4; AUTHORITY_CLAIM se anota en la línea 4 porque ahí lo afirma (manual §5). El catálogo lista TRUST_BUILDING, pero acá el respaldo de identidad es débil (solo la excusa del celular roto) y no se etiquetó. «Te escucho raro» (línea 5) remite a una señal de voz que en texto no existe. Vínculo, nombre y monto ficticios. A habla primero y es quien recibe la llamada.

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### SC-ORG-BENEFICIO-01-e01

vishing · 13 líneas

` 1` **A:** Buen día, ¿hablo con la señora Elena Ríos?  
` 2` **B:** Sí, soy yo. ¿De dónde me llaman?  
` 3` **A:** Te llamo del organismo previsional, del área de beneficios; mi nombre es Daniel Ferreyra. Te figura un refuerzo de cuarenta mil pesos que todavía no cobraste. ← `AUTHORITY_CLAIM`, `TRUST_BUILDING`  
` 4` **B:** ¿Un refuerzo? No sabía nada. Nadie me avisó.  
` 5` **A:** Salió para los jubilados que cobran la mínima, y vos estás en el listado. El tema es que hay que validarlo antes de que cierre la liquidación, y cierra mañana a primera hora. ← `TRUST_BUILDING`, `URGENCY_PRESSURE`  
` 6` **B:** Ay, ¿y qué tengo que hacer? Yo hoy no tengo cómo ir hasta la oficina.  
` 7` **A:** Quedate tranquila, lo hacemos ahora por teléfono. Necesito que me confirmes tu fecha de nacimiento y el domicilio donde vivís. ← **T_R** · `REQUEST_PERSONAL_DATA`  
` 8` **B:** Nací el doce de mayo del cincuenta y uno, y vivo en Los Aromos cuatrocientos veinte. ← **T_C** · _cumplimiento_  
` 9` **A:** Perfecto, coincide con lo que tengo. Ahora te escribo a este número y me contestás con una foto tuya sosteniendo el documento al lado de la cara, así queda validado que sos vos. ← `REQUEST_PERSONAL_DATA`, `TRUST_BUILDING`  
`10` **B:** ¿Una foto mía? Eso no lo sé hacer bien con el celular.  
`11` **A:** Es una foto común, como cualquier otra. Sin esa foto no te lo puedo acreditar, y mañana a primera hora ya no entra. ← `URGENCY_PRESSURE`, `PERSISTENCE_DISTRACTION`  
`12` **B:** Bueno, cuando vuelva mi hija le pido que me ayude y te la manda ella. ← _contexto_  
`13` **A:** Dale, pero que sea hoy, ¿eh? Así no perdés el refuerzo.  

**Referencia de trabajo:** `T_R` 7, `T_C` 8, pedido REQUEST_PERSONAL_DATA.

**Qué prueba:** Refuerzo con monto y plazo concretos que, según quien llama, hay que «validar» por teléfono, para una persona confiada. El primer pedido (fecha de nacimiento y domicilio) se formula como «confirmar» y se cumple en la línea siguiente; después llega un segundo pedido (una foto sosteniendo el documento) que queda prometido, no cumplido.

**Notas de la referencia:** La línea 7 dice «confirmes»: podría leerse como verificación de datos que el organismo ya tiene (el manual hace esa excepción para REQUEST_SECRET, no para REQUEST_PERSONAL_DATA). Se marca como pedido porque la llamada no la inició la persona y los datos son identificatorios (discutir en D07). En la línea 12 la persona promete mandar la foto más tarde: no es cumplimiento observable. El nombre del organismo se reemplazó por el tipo de entidad; en una llamada real se nombraría. El catálogo describe un «beneficio inexistente», pero el par LG-ORG-TURNO-01-e01 trata el mismo refuerzo como real y automático: acá lo falso es el trámite de validación, no el refuerzo (discutir si la semilla admite que el fraude se apoye en un beneficio anunciado). El plazo («cierra mañana a primera hora») y la foto con el documento en la mano se eligieron para no repetir el «hoy antes de las seis» y la foto de frente y dorso de SC-PREMIO-01-e01.

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### SC-PREMIO-01-e01

vishing · 14 líneas

` 1` **A:** ¡Buenas tardes! ¿Me comunico con Norma Villegas?  
` 2` **B:** Sí, ella habla. ¿De parte de quién?  
` 3` **A:** Te habla Javier Ledesma, de la promoción aniversario del supermercado. Te llamo porque tu ticket salió sorteado el sábado. ← `AUTHORITY_CLAIM`  
` 4` **B:** ¿En serio? Sí, compro siempre ahí, pero no me acuerdo de haberme anotado en nada.  
` 5` **A:** Se participa automáticamente con la tarjeta del club de descuentos. Ganaste una orden de compra por trescientos mil pesos y el escribano ya labró el acta con tu nombre. ← `TRUST_BUILDING`  
` 6` **B:** ¡No lo puedo creer! ¿Y qué tengo que hacer?  
` 7` **A:** Muy poquito. Eso sí, el premio se tiene que acreditar hoy antes de las seis de la tarde; si no, pasa al suplente que salió segundo. ← `URGENCY_PRESSURE`  
` 8` **A:** Para acreditarlo a tu nombre necesito que me mandes una foto del documento, de frente y de dorso, por WhatsApp a este mismo número. ← **T_R** · `REQUEST_PERSONAL_DATA`  
` 9` **B:** ¿Una foto del documento? ¿Para qué, si ya tienen mi nombre? ← _contexto_  
`10` **A:** Es un requisito del escribano, para que nadie lo cobre en tu lugar. Mientras la sacás, si querés, te voy leyendo las condiciones de entrega. ← `PERSISTENCE_DISTRACTION`  
`11` **B:** Bueno, dale. Esperá que busco el documento.  
`12` **A:** Dale, tranquila, te espero.  
`13` **B:** Listo, ahí te mandé las dos fotos. ← **T_C** · _cumplimiento_  
`14` **A:** Perfecto, me llegaron. Ya quedás registrada como ganadora; en un rato te escribo para coordinar la entrega.  

**Referencia de trabajo:** `T_R` 8, `T_C` 13, pedido REQUEST_PERSONAL_DATA.

**Qué prueba:** Pedido de datos personales (foto del documento) tras un pretexto de premio con respaldo (club de descuentos, escribano, acta), un plazo y una insistencia ante la duda. Persona confiada que cumple; el cumplimiento se declara en voz pero ocurre por otro canal.

**Notas de la referencia:** El cumplimiento (mandar las fotos por WhatsApp) ocurre fuera de la llamada; en el texto solo se observa porque B lo anuncia en la línea 13. Discutir en D07 si un cumplimiento por otro canal, declarado en voz, cuenta como T_C observable. La línea 9 es una duda breve, no un rechazo. La ficha no fija qué dato se pide: se eligió la foto del documento para no escribir números de DNI ni domicilios. A habla primero y es quien llama.

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### SC-SOPORTE-CLAVE-01-e01

vishing · 14 líneas

` 1` **A:** Hola, buenas tardes. ¿Hablo con Laura Domínguez?  
` 2` **B:** Sí, soy yo. ¿Quién habla?  
` 3` **A:** Te llamo de la mesa de ayuda de la billetera, soy Gastón. Estamos pasando las cuentas a la plataforma nueva y la tuya quedó trabada a mitad de camino. ← `AUTHORITY_CLAIM`  
` 4` **B:** Ah, ¿por eso el otro día no me dejaba entrar desde la computadora?  
` 5` **A:** Exacto, es por eso. Ya te abrí un número de gestión, el cero, cero, uno, dos, tres, así queda todo registrado a tu nombre. ← `TRUST_BUILDING`  
` 6` **A:** Para terminar el pase necesito validar tu acceso: decime el usuario con el que entrás y la contraseña. ← **T_R** · `REQUEST_SECRET`  
` 7` **B:** ¿La contraseña? En la aplicación dice que no se la pase a nadie. ← _contexto_  
` 8` **A:** Está muy bien que lo tengas presente; eso es para que no se la des a desconocidos. Yo estoy del lado del sistema, y en cuanto termina el pase la podés cambiar. ← `PERSISTENCE_DISTRACTION`  
` 9` **B:** No sé... ¿No lo puedo hacer yo desde la aplicación?  
`10` **A:** Desde la aplicación no te va a dejar, porque tu cuenta sigue en la plataforma vieja. Por eso te llamamos nosotros; es un minuto. ← `PERSISTENCE_DISTRACTION`  
`11` **B:** Bueno, dale. El usuario es laura punto prueba, todo en minúscula. ← **T_C** · _cumplimiento_  
`12` **A:** Perfecto. ¿Y la contraseña?  
`13` **B:** Prueba uno, dos, tres, cuatro, con la pe mayúscula. ← _cumplimiento_  
`14` **A:** Listo, Laura, ya quedó pasada a la plataforma nueva. Cualquier novedad te llamamos nosotros.  

**Referencia de trabajo:** `T_R` 6, `T_C` 11, pedido REQUEST_SECRET.

**Qué prueba:** Pedido de usuario y contraseña con pretexto de migración de plataforma y un número de gestión como respaldo. La persona duda citando el aviso de la propia aplicación y cede después de dos redirecciones. Las cinco líneas previas al pedido no contienen ninguna palabra de alto riesgo.

**Notas de la referencia:** T_C se marca en la línea 11 (usuario) porque el manual incluye «usuario» en REQUEST_SECRET; si el equipo decide que el usuario solo no es una credencial, T_C pasaría a la línea 13 (contraseña). En la línea 4 es la persona quien aporta el fallo de ingreso que el llamante aprovecha en la línea 5; esa línea 4 no es TRUST_BUILDING del llamante (discutir en D07 cómo anotar un respaldo que ofrece la propia víctima). La línea 7 es una duda, no un rechazo.

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### SC-SOPORTE-REMOTO-01-e01

vishing · 11 líneas

` 1` **A:** Buenas noches, te hablo del sector de préstamos del banco, mi nombre es Hernán Ibarra. ¿Sos el titular de la cuenta? ← `AUTHORITY_CLAIM`  
` 2` **B:** Sí, soy yo. ¿Qué pasó?  
` 3` **A:** Hace un rato se pidió a tu nombre un préstamo de cuatrocientos cincuenta mil pesos, y ya quedó cargada una transferencia de esa plata a una cuenta de otro banco. ← _contexto_  
` 4` **A:** Todavía no salió, pero si no la frenamos ahora, la plata se va y el préstamo te queda a vos para pagarlo en cuotas. ← `THREAT_FEAR`, `URGENCY_PRESSURE`  
` 5` **B:** ¿Qué? Yo no pedí ningún préstamo. ¿Cómo lo freno?  
` 6` **A:** Yo desde acá no veo la aplicación como la ves vos. Te hago una videollamada, tocás «compartir pantalla» y te voy guiando para anular el préstamo. ← **T_R** · `REQUEST_REMOTE_ACCESS`  
` 7` **B:** ¿Compartir la pantalla? No, eso no lo hago. Mañana voy a la sucursal y lo veo ahí. ← _rechazo_  
` 8` **A:** Mañana la transferencia ya salió. Y te pido que no cortes ni llames a nadie, porque si se cierra esta gestión el bloqueo se cae. ← `URGENCY_PRESSURE`, `ISOLATION_SECRECY`, `PERSISTENCE_DISTRACTION`  
` 9` **B:** Si sos del banco, no te va a molestar que corte y me fije yo en la aplicación si ese préstamo existe.  
`10` **A:** Si cortás, el sistema toma el préstamo como autorizado por vos y después no hay reclamo que valga. ← `THREAT_FEAR`, `ISOLATION_SECRECY`  
`11` **B:** Lo arreglo con el banco por mi cuenta. No voy a compartir nada. Hasta luego. ← _rechazo_  

**Referencia de trabajo:** `T_R` 6, `T_C` —, pedido REQUEST_REMOTE_ACCESS.

**Qué prueba:** Pedido de compartir pantalla por videollamada, precedido de una amenaza de pérdida de dinero (un préstamo a nombre de la persona que ya se está transfiriendo) y seguido de presión para no cortar ni verificar por otro canal. La persona se niega desde el primer pedido: el detector debería alertar por el pedido y la presión aunque no haya cumplimiento.

**Notas de la referencia:** Se usa pantalla compartida en videollamada en lugar de instalar una aplicación de acceso remoto para no nombrar aplicaciones reales; las dos variantes caen en REQUEST_REMOTE_ACCESS. La fuente de la semilla describe una continuación (guiar a la aplicación bancaria, copiar credenciales, pedir códigos y transferir) que acá no ocurre porque la persona corta; t_c_linea queda null. La línea 3 informa un hecho negativo sin consecuencias para la persona; la amenaza aparece en la línea 4. El pretexto del préstamo pedido a nombre de la persona reemplaza al de un ingreso desde un celular ajeno, para no repetir la premisa de SC-CLAVE-CAMBIO-01-e01 y TR-07. En la línea 9 la persona propone verificar por su cuenta en la aplicación; la línea 10 lo desalienta.

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### SC-WA-CODE-01-e01

vishing · 5 líneas

` 1` **A:** Te llamo de soporte por la activación de tu cuenta de WhatsApp. ← `AUTHORITY_CLAIM`  
` 2` **B:** Me acaba de llegar un SMS. No pedí activar nada.  
` 3` **A:** Para cancelar esa activación tenemos que resolverlo ahora. ← `URGENCY_PRESSURE`  
` 4` **A:** Decime el código de activación que recibiste por SMS. ← **T_R** · `REQUEST_AUTH_CODE`  
` 5` **B:** Es cero, cero, cero, cero, cero, cero. ← **T_C** · _cumplimiento_  

**Referencia de trabajo:** `T_R` 4, `T_C` 5, pedido REQUEST_AUTH_CODE.

**Qué prueba:** Pedido directo del código de activación, con contexto previo de soporte y urgencia. Caso fácil de referencia.

**Notas de la referencia:** En ARQUITECTURA §4, F1–F2 forman una sola actualización (U1). Acá cada línea es una actualización, como pide #50 (turno cerrado).

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

## Piloto escrito: legítimas

### LG-BANK-VERIF-01-e01

legitima_dificil · 12 líneas

` 1` **A:** Buenas tardes, centro de atención del banco, habla Lucía. ← `AUTHORITY_CLAIM`  
` 2` **B:** Hola, Lucía. Llamo al número que está atrás de mi tarjeta. Me llegó un aviso en la app de un ingreso desde un dispositivo nuevo y quiero cambiar la clave. ← _contexto_  
` 3` **A:** Bien. El cambio lo hacés vos desde la app del banco o desde el home banking, en el menú Seguridad, opción Cambiar clave. ← _mencion_  
` 4` **B:** ¿No me pueden mandar un enlace por mensaje de texto, así lo hago más rápido? ← _mencion_  
` 5` **A:** No, no mandamos enlaces para cambiar la clave. Entrá desde la app que ya tenés instalada. ← _rechazo_  
` 6` **B:** Dale. ¿Querés que te diga los últimos números de la tarjeta para que me identifiques? ← _mencion_  
` 7` **A:** No hace falta. Por teléfono no confirmamos datos de la tarjeta, y tampoco te voy a pedir la clave, ni la vieja ni la nueva. ← _rechazo_  
` 8` **B:** Perfecto. ¿Y si ese dispositivo nuevo era de otra persona?  
` 9` **A:** Cuando termines, fijate en Seguridad la lista de dispositivos y quitá el que no reconozcas. Si ves un movimiento que no hiciste, desconocelo desde la app o volvé a llamar a este número. ← _mencion_  
`10` **B:** Listo, lo hago ahora. ¿Tengo que quedarme en línea mientras lo cambio?  
`11` **A:** No, podés cortar tranquilo y hacerlo a tu ritmo. Si algo no te sale, nos volvés a llamar. ← _contexto_  
`12` **B:** Buenísimo. Gracias, Lucía.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** Quien atiende se presenta como el banco y se habla de cambiar la clave, de enlaces, de dispositivos y de datos de la tarjeta, pero solo se recomienda el canal oficial, se rechazan el enlace y los datos parciales y se deja cortar. Negación «no te voy a pedir la clave» que puede engañar a reglas de palabras clave.

**Notas de la referencia:** Las líneas 3 y 9 indican cambiar la clave y quitar dispositivos desde la app oficial: según el manual §5, recomendar una acción de seguridad por el canal oficial no es REQUEST_SECURITY_ACTION, pero comparte vocabulario con el par. En la línea 6 es B quien ofrece datos parciales; A los rechaza (línea 7), como pide la ficha. El texto no permite comprobar que el número llamado sea el oficial; se toma de la ficha. AUTHORITY_CLAIM se anota en quien atiende (A), aunque el manual §5 la define para quien llama; revisar en D07.

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### LG-FAMILIAR-LLAMADO-01-e01

legitima_dificil · 12 líneas

` 1` **A:** ¿Hola?  
` 2` **B:** Hola, tía, soy Nicolás. Te llamo del celular de un compañero porque el mío se quedó sin batería. ← `AUTHORITY_CLAIM`  
` 3` **A:** ¿Nico? ¿Qué pasó? Me asustás, llamando de otro número.  
` 4` **B:** Tranquila. Al abuelo lo llevaron a la guardia porque se cayó en la vereda. Está consciente y lo están revisando, pero quería avisarte. ← _contexto_  
` 5` **A:** ¡Ay, no! ¿Pero está bien? ¿Dónde están?  
` 6` **B:** En la guardia del hospital del centro. Mamá está con él. Le van a sacar unas placas y en un rato sabemos más.  
` 7` **A:** ¿Necesitan plata para algo? ¿Te transfiero para los remedios o para el taxi? ← _mencion_  
` 8` **B:** No, no hace falta nada, lo cubre la obra social. Te llamaba solo para que estuvieras al tanto. ← _rechazo_  
` 9` **A:** Perdoná, Nico, pero prefiero cortar y llamar a tu mamá, así me quedo tranquila. ← _contexto_  
`10` **B:** Sí, obvio, hacé eso. Llamala a ella, que tiene el celular a mano. Yo te escribo cuando nos den los resultados. ← _contexto_  
`11` **A:** Dale, te corto y la llamo. Un beso grande.  
`12` **B:** Beso, tía. Después hablamos.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** Un familiar llama desde un número ajeno por una urgencia real (guardia, hospital). Quien atiende menciona transferir plata y propone cortar para verificar; el familiar rechaza la plata y acepta la verificación. Misma identidad declarada y mismo vocabulario que su par, sin pedido.

**Notas de la referencia:** Usa la misma identidad declarada que el par (sobrino «Nico» que llama desde otro número) para que la diferencia esté en la conducta: acá se presenta por su nombre sin que se lo pregunten, no pide dinero ni secretos y acepta que A corte y llame a la madre. La línea 7 menciona una transferencia que ofrece A, no un pedido. La urgencia médica puede disparar reglas de urgencia, pero no hay presión del llamante. En el texto no hay evidencia para comprobar que la identidad sea auténtica (manual §2); se toma de la ficha.

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### LG-ORG-TURNO-01-e01

legitima_dificil · 13 líneas

` 1` **A:** Buen día, te atiende Sofía, de atención telefónica del organismo previsional. ¿En qué te puedo ayudar? ← `AUTHORITY_CLAIM`  
` 2` **B:** Hola, buen día. Escuché en la radio que hay un refuerzo para los jubilados que cobran la mínima y quería saber si me toca.  
` 3` **A:** Sí, es un refuerzo de cuarenta mil pesos. Se cobra automáticamente junto con el haber de este mes; no hay que hacer ningún trámite. ← _contexto_  
` 4` **B:** ¿Seguro? Porque a una vecina la llamaron diciendo que eran de acá, y le pidieron el domicilio y una foto con el documento en la mano para cargárselo. ← _mencion_  
` 5` **A:** Eso no lo hacemos nosotros. Por teléfono no pedimos fotos del documento, claves ni datos del banco. Si la vuelven a llamar, que corte. ← _mencion_  
` 6` **B:** ¿Y vos no necesitás mis datos para fijarte si estoy en el listado?  
` 7` **A:** Por acá no hace falta. Si querés verlo con tu nombre, entrás a la página oficial con tu clave y lo consultás vos. ← _mencion_  
` 8` **B:** Yo con la computadora me pierdo. ¿No puedo ir a la oficina?  
` 9` **A:** Sí, claro. Sacás un turno en la página oficial o lo pedís en la misma oficina, y llevás el documento.  
`10` **B:** ¿Y el turno no me lo podés sacar vos? Te paso el número de documento, si querés. ← _mencion_  
`11` **A:** No hace falta que me pases nada. Para este refuerzo no tenés que ir: si cobrás la mínima, te llega solo con el haber. ← _rechazo_  
`12` **B:** Ah, bueno. Entonces lo espero con el cobro de este mes.  
`13` **A:** Exacto. Si en el recibo de este mes no te aparece, volvé a llamar con el número de documento a mano y lo revisamos. ← _mencion_  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** Mismo beneficio, monto y vocabulario que SC-ORG-BENEFICIO-01-e01 (refuerzo, cuarenta mil pesos, jubilados de la mínima, listado, oficina, domicilio, foto con el documento), en una consulta que inicia la persona. El relato del pedido que recibió una vecina, la mención de la clave para la página oficial y el número de documento que se ofrece y no se acepta, y el aviso final de tenerlo a mano para otra llamada, prueban que el detector no confunda tema con pedido.

**Notas de la referencia:** Se evitó que quien atiende pida un número de identificación para consultar el caso, aunque en una consulta iniciada por la persona podría ser razonable. Una variante con ese pedido en llamada entrante sería un negativo más difícil y obligaría a decidir en D07 si cuenta como pedido. AUTHORITY_CLAIM en la línea 1 la hace quien atiende, no quien llama (misma duda que en LG-SUPPORT-INFO-01-e01). La línea 13 anticipa que, si la persona vuelve a llamar, le van a pedir el número de documento: se anota como mención, no como pedido.

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### LG-PREMIO-CONSULTA-01-e01

legitima_dificil · 12 líneas

` 1` **A:** Atención al cliente de la promoción aniversario, buenas tardes. Te atiende Romina. ← `AUTHORITY_CLAIM`  
` 2` **B:** Hola, Romina. Saqué este número del cartel que está en las cajas del supermercado. Quería consultar por el sorteo. ← _contexto_  
` 3` **A:** Sí, claro, decime.  
` 4` **B:** Compré el sábado con la tarjeta del club de descuentos y me dijeron que con eso ya participaba. ¿Cómo me entero si gané?  
` 5` **A:** Los ganadores se publican el lunes en el local y en la página de la promoción. Nosotros no llamamos para avisar ni pedimos datos por teléfono. ← _mencion_  
` 6` **B:** Ah, mirá. ¿Y si sale mi ticket, cómo se acredita el premio? ¿Hay que mandarles algo antes, una foto del documento o algo así? ← _mencion_  
` 7` **A:** No, nada de fotos ni por WhatsApp. Venís al local con tu documento y el ticket, y lo retirás en el mostrador de atención. ← _rechazo_  
` 8` **A:** ¿Tenés el ticket a mano? Fijate si abajo de todo dice «participa del sorteo aniversario». ← _contexto_  
` 9` **B:** A ver... sí, acá lo dice. ¿Y hay que pagar algo para retirarlo? ¿Un gasto de envío, algo así? ← _mencion_  
`10` **A:** Nada, el retiro es sin cargo. Eso sí, guardá bien el ticket, porque sin el ticket no se entrega.  
`11` **A:** Y tenés treinta días desde la publicación para pasar a buscarlo; después el premio pasa al suplente. ← _mencion_  
`12` **B:** Perfecto, me quedó clarísimo. Gracias, Romina.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** Comparte con su par premio, sorteo, ticket, tarjeta del club, foto del documento, WhatsApp, pago, plazo y suplente, pero solo como negaciones, como descripción de un trámite presencial y como un plazo informativo de treinta días, sin presión. Quien atiende hace un pedido de bajo riesgo (mirar el ticket que la persona tiene en la mano), que no debe leerse como pedido de datos. No hay pedido de alto riesgo.

**Notas de la referencia:** La línea 7 («venís al local con tu documento») describe un trámite presencial futuro, no un pedido de datos por teléfono, aunque una regla de palabras clave puede leerla como REQUEST_PERSONAL_DATA. La línea 8 es un pedido de bajo riesgo: B mira el ticket y no dicta nada. La línea 11 menciona un plazo y el suplente, como la línea 7 del par, pero son treinta días informativos y no se anotó URGENCY_PRESSURE; revisar en D07 si un plazo sin presión debe registrarse. El texto no permite comprobar que el número del cartel sea el oficial; se toma de la ficha («canal que verificó»). AUTHORITY_CLAIM se anota en quien atiende (A), aunque el manual §5 la define para quien llama: la ficha del catálogo la incluye; revisar en D07.

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### LG-SUPPORT-INFO-01-e01

legitima_dificil · 13 líneas

` 1` **A:** Mesa de ayuda de la billetera, buenas tardes, te atiende Julián. ¿En qué te puedo ayudar? ← `AUTHORITY_CLAIM`  
` 2` **B:** Hola, ¿qué tal? Los llamo porque no puedo entrar a mi cuenta desde la computadora: me dice que el usuario o la contraseña son incorrectos.  
` 3` **A:** Bien, lo vemos. Antes que nada, no me digas ni tu usuario ni tu contraseña; para esto no los necesito. ← _mencion_  
` 4` **B:** Ah, yo te los iba a pasar para que te fijes vos si están bien. ← _mencion_  
` 5` **A:** No hace falta. Nosotros no vemos tu clave y nadie de la mesa de ayuda te la va a pedir. ← _rechazo_  
` 6` **B:** ¿Y entonces cómo lo arreglo? Tengo que pagar algo hoy.  
` 7` **A:** En la pantalla de ingreso tocá «Olvidé mi contraseña». Te va a llegar un correo a la dirección que tenés registrada. ← _contexto_  
` 8` **B:** Ya me llegó. ¿Te leo lo que dice?  
` 9` **A:** No, ese correo es para vos. Seguí los pasos ahí mismo y elegí una clave nueva que no uses en otro lado. ← _rechazo_  
`10` **B:** Listo, ya la cambié. ¿Querés que te la diga para que quede anotada? ← _mencion_  
`11` **A:** No, por favor. La clave nueva no se la digas a nadie, tampoco a nosotros. Probá entrar ahora. ← _rechazo_  
`12` **B:** Entré. Uy, gracias, pensé que me habían bloqueado la cuenta.  
`13` **A:** De nada. Si te vuelve a pasar, escribinos por el chat de la aplicación y lo vemos.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** Mismo tema y vocabulario que SC-SOPORTE-CLAVE-01-e01 (mesa de ayuda, billetera, usuario, contraseña, clave nueva), en una llamada que inició la persona. Quien orienta nunca pide credenciales y rechaza tres ofrecimientos de la persona (pasar los datos, leer el correo, dictar la clave nueva). Negaciones como «no me digas ni tu usuario ni tu contraseña» engañan a una regla de palabras clave, y el cierre no trae ninguna advertencia de seguridad que regale la clase.

**Notas de la referencia:** Las líneas 7 y 9 guían el cambio de clave con el correo que la persona pide desde la aplicación: el manual no lo cuenta como REQUEST_SECURITY_ACTION porque es cambiar la clave por el canal oficial, pero una regla de palabras clave podría marcarlo. AUTHORITY_CLAIM en la línea 1 la hace quien atiende una llamada entrante, no quien llama; el catálogo la lista como maniobra de la semilla y el manual la define para «quien llama» (discutir en D07). La persona no dice por qué canal llamó: que la llamada es entrante solo se infiere del saludo de la línea 1.

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### LG-SUPPORT-INFO-01-e02

legitima_dificil · 13 líneas

` 1` **A:** Hola, buenas tardes. Los llamo porque la aplicación del banco se me queda con la pantalla en blanco cuando quiero entrar.  
` 2` **B:** Buenas tardes, te atiende Carolina, de atención al cliente. Contame, ¿desde cuándo te pasa? ← `AUTHORITY_CLAIM`  
` 3` **A:** Desde ayer. En el trabajo, cuando algo no anda, los de sistemas se conectan a mi computadora y lo arreglan. ¿Ustedes pueden hacer lo mismo con el celular? ← _mencion_  
` 4` **B:** No, eso no. Nosotros no te vamos a pedir que compartas la pantalla ni que instales nada para que alguien entre a tu celular. ← _rechazo_  
` 5` **A:** Ah, bueno. ¿Y entonces cómo hacemos?  
` 6` **B:** Lo revisás vos y me vas contando. Fijate en la tienda de aplicaciones si la del banco tiene una actualización pendiente. ← _contexto_  
` 7` **A:** Sí, me aparece el botón de actualizar. Ya está, se está bajando.  
` 8` **B:** Bien. Cuando termine, abrila y contame qué te aparece en la pantalla. Todavía no pongas la clave. ← _contexto_  
` 9` **A:** Ahora sí carga. Me aparece el inicio de siempre, para poner el usuario.  
`10` **B:** Perfecto, era la versión vieja. Ingresá como siempre; yo no necesito ver nada. ← _contexto_  
`11` **A:** Entré, ya veo mis movimientos. ¿No hace falta que te pase algún dato? ← _mencion_  
`12` **B:** No, ninguno. Y si algún día te llaman pidiendo que compartas la pantalla en una videollamada, cortá y llamá vos al número que está atrás de la tarjeta. ← _rechazo_  
`13` **A:** Buenísimo. Gracias, Carolina.  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** Comparte con su par SC-SOPORTE-REMOTO-01-e01 la aplicación del banco, «compartir la pantalla» y la videollamada, y suma «instalar», la tienda de aplicaciones y el número de la tarjeta; pero quien orienta rechaza la conexión remota que propone la propia persona y la guía para que mire su pantalla y le cuente. Prueba la diferencia entre «contame qué te aparece en la pantalla» y pedir que la comparta.

**Notas de la referencia:** Acá A es quien llamó al soporte y quien primero propone una conexión remota (línea 3); en el par, A es quien la pide. Sirve para ver si el detector se apoya en la letra del hablante. La línea 6 pide actualizar la aplicación oficial desde la tienda: el manual no lo cubre de forma explícita; se toma como «abrir una app para mirar algo uno mismo», no como REQUEST_REMOTE_ACCESS ni REQUEST_SECURITY_ACTION (discutir en D07).

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### LG-WA-CONSULTA-01-e01

legitima_dificil · 4 líneas

` 1` **A:** Me llegó por SMS un código para activar WhatsApp y yo no lo pedí. ← _mencion_  
` 2` **B:** No me lo leas ni lo compartas. Revisá la seguridad desde la aplicación. ← _contexto_  
` 3` **A:** ¿Necesitás verlo para ayudarme?  
` 4` **B:** No. No hace falta que me digas ningún código. ← _rechazo_  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** Habla del mismo código de WhatsApp, pero para no compartirlo. La negación «no hace falta que me digas ningún código» no es un pedido.

**Notas de la referencia:** La línea 3 es una pregunta de quien recibió el código; no la hace quien orienta.

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

## Laboratorio

### LAB-acceso-remoto

vishing · 5 líneas

` 1` **A:** te llama la tarjeta hay un debito duplicado ← `AUTHORITY_CLAIM`  
` 2` **B:** no fui yo  
` 3` **A:** te mando el acceso remoto para que me compartas la pantalla y lo freno yo ← **T_R** · `REQUEST_REMOTE_ACCESS`  
` 4` **B:** no se como se hace eso  
` 5` **A:** si no lo instalas no puedo parar el debito ← `PERSISTENCE_DISTRACTION`  

**Referencia de trabajo:** `T_R` 3, `T_C` —, pedido REQUEST_REMOTE_ACCESS.

**Qué prueba:** Supuesto llamado de la tarjeta por un débito duplicado que pide acceso remoto para compartir la pantalla.

**Notas de la referencia:** Incendio esperado por el laboratorio: REQUEST_REMOTE_ACCESS (tabla y comentario), en t3 según chequear_casos.py. Coincide con t_r_linea = 3. Sin cumplimiento: B no sabe cómo hacerlo y A insiste en la línea 5. Texto en minúsculas y sin tildes, como en el guion original (estilo salida de ASR), sin corregir; las letras A/B se agregaron en la conversión.

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### LAB-acceso-remoto-parafrasis

vishing · 5 líneas

` 1` **A:** soy de la tarjeta tenes un cobro duplicado ← `AUTHORITY_CLAIM`  
` 2` **B:** yo no compre nada  
` 3` **A:** instala el programa que te digo y mostrame la pantalla ← **T_R** · `REQUEST_REMOTE_ACCESS`  
` 4` **B:** no entiendo nada de eso  
` 5` **A:** si no lo haces no lo puedo anular ← `PERSISTENCE_DISTRACTION`  

**Referencia de trabajo:** `T_R` 3, `T_C` —, pedido REQUEST_REMOTE_ACCESS.

**Qué prueba:** Paráfrasis anti-overfit del acceso remoto: cobro duplicado de la tarjeta y pedido de instalar un programa y mostrar la pantalla.

**Notas de la referencia:** Paráfrasis de LAB-acceso-remoto en el laboratorio; par null. Incendio esperado por el laboratorio: REQUEST_REMOTE_ACCESS en t3 (comentario del guion y tabla del README), goteo en t3. Coincide con t_r_linea = 3. Sin cumplimiento: B no entiende y el guion termina con la insistencia de A. Texto en minúsculas y sin tildes, como en el guion original (estilo salida de ASR), sin corregir; las letras A/B se agregaron en la conversión.

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### LAB-anses-beneficio

vishing · 5 líneas

` 1` **A:** hablo de anses hay un beneficio extra para cobrar esta semana ← `AUTHORITY_CLAIM`  
` 2` **B:** ah no sabia  
` 3` **A:** para habilitarlo pasame la clave de la seguridad social y el cbu ← **T_R** · `REQUEST_SECRET`  
` 4` **B:** eso no lo digo por telefono ← _rechazo_  
` 5` **A:** si no me lo das hoy se pierde el pago ← `URGENCY_PRESSURE`, `PERSISTENCE_DISTRACTION`  

**Referencia de trabajo:** `T_R` 3, `T_C` —, pedido REQUEST_SECRET.

**Qué prueba:** Beneficio extra del organismo a cambio de la clave de la seguridad social y el CBU, con presión tras la negativa.

**Notas de la referencia:** Incendio esperado por el laboratorio: REQUEST_SECRET y REQUEST_TRANSFER (tabla y comentario), en t3 según chequear_casos.py. t_r_linea = 3 coincide. Diferencia de etiqueta: pedir «el cbu» de B no es «mover dinero» según el manual §5, así que no se etiquetó REQUEST_TRANSFER; queda para D07 si el CBU cuenta como dato personal o bancario. Sin cumplimiento: B se niega en la línea 4 y A insiste en la 5. El guion nombra un organismo real («anses»); la conversión conserva el texto, pero las reglas de redacción del ensayo piden no nombrar entidades reales: decidir si se reemplaza. Texto en minúsculas y sin tildes, como en el guion original (estilo salida de ASR), sin corregir; las letras A/B se agregaron en la conversión.

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### LAB-anses-beneficio-parafrasis

vishing · 5 líneas

` 1` **A:** te hablo de anses tenes un cobro pendiente para retirar ← `AUTHORITY_CLAIM`  
` 2` **B:** no sabia nada de eso  
` 3` **A:** pasame la contraseña y el alias para habilitarlo ← **T_R** · `REQUEST_SECRET`  
` 4` **B:** eso no se dice por telefono ← _rechazo_  
` 5` **A:** si no lo haces hoy se cae el pago ← `URGENCY_PRESSURE`, `PERSISTENCE_DISTRACTION`  

**Referencia de trabajo:** `T_R` 3, `T_C` —, pedido REQUEST_SECRET.

**Qué prueba:** Paráfrasis anti-overfit del beneficio del organismo: un cobro pendiente a cambio de la contraseña y el alias.

**Notas de la referencia:** Paráfrasis de LAB-anses-beneficio en el laboratorio; par null. Incendio esperado por el laboratorio: REQUEST_SECRET + REQUEST_TRANSFER en t3 y REQUEST_TRANSFER en t5; goteo en t5. t_r_linea = 3 coincide con el primer incendio. Diferencias de etiqueta: (1) pedir «el alias» de la cuenta de B no es «mover dinero» según el manual §5, así que no se etiquetó REQUEST_TRANSFER; queda para D07 si el alias cuenta como dato personal o bancario. (2) La línea 5 («si no lo haces hoy se cae el pago») es presión e insistencia tras la negativa, no un pedido de transferencia: el REQUEST_TRANSFER de t5 del laboratorio sale de la palabra «pago». Sin cumplimiento: B se niega en la línea 4. El guion nombra un organismo real («anses»); la conversión conserva el texto, pero las reglas de redacción del ensayo piden no nombrar entidades reales: decidir si se reemplaza. Texto en minúsculas y sin tildes, como en el guion original (estilo salida de ASR), sin corregir; las letras A/B se agregaron en la conversión.

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### LAB-anses-canal-oficial

legitima_dificil · 5 líneas

` 1` **A:** me ofrecieron un bono si les doy datos del organismo ← _mencion_  
` 2` **B:** el organismo no pide eso por telefono ← _contexto_  
` 3` **A:** entro yo a la pagina oficial ← _contexto_  
` 4` **B:** si queres denuncia por el canal que figura ahi ← _contexto_  
` 5` **A:** gracias  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** Mismo tema que el beneficio del organismo (un bono a cambio de datos), pero se lo cuenta para derivar a la página y al canal oficial, sin pedido.

**Notas de la referencia:** Pareja en el laboratorio: vishing/anses-beneficio.txt (LAB-anses-beneficio); par queda null por la regla de esta conversión. Incendio esperado por el laboratorio: ninguno (tabla del README y comentario del guion); coincide con t_r_linea null. La línea 1 relata un pedido de datos hecho por terceros en otra llamada: es mención, no pedido. «datos del organismo» es la redacción original. Hablantes: alternancia simple, A consulta y B orienta. Texto en minúsculas y sin tildes, como en el guion original (estilo salida de ASR), sin corregir; las letras A/B se agregaron en la conversión.

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### LAB-arca-canal-oficial

legitima_dificil · 5 líneas

` 1` **A:** me llego un mail de una deuda y un embargo ← _mencion_  
` 2` **B:** no abras ningun sitio del mensaje ← _contexto_  
` 3` **B:** la unica via es entrar vos a la pagina oficial ← _contexto_  
` 4` **A:** no mando dinero por telefono ← _contexto_  
` 5` **B:** correcto  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** Mismo tema que la deuda y el embargo del fisco, pero se deriva a la página oficial y nadie pide nada.

**Notas de la referencia:** Pareja en el laboratorio: vishing/arca-deuda.txt (LAB-arca-deuda); par null. Incendio esperado por el laboratorio: ninguno (tabla y comentario); coincide con t_r_linea null. Hablantes: la línea 3 se asignó a B porque se dirige a quien recibió el mail («entrar vos») y la línea 4 a A porque está en primera persona («no mando dinero»); asignación razonable pero discutible. Texto en minúsculas y sin tildes, como en el guion original (estilo salida de ASR), sin corregir; las letras A/B se agregaron en la conversión.

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### LAB-arca-deuda

vishing · 5 líneas

` 1` **A:** le habla un inspector hay una deuda de una fiscalizacion y un embargo ← `AUTHORITY_CLAIM`, `THREAT_FEAR`  
` 2` **B:** yo no tengo nada de eso  
` 3` **A:** tiene que autorizar con su clave fiscal o transferir hoy ← **T_R** · `REQUEST_TRANSFER`, `REQUEST_SECRET`, `REQUEST_SECURITY_ACTION`, `URGENCY_PRESSURE`  
` 4` **B:** no voy a dar la clave ← _rechazo_  
` 5` **A:** entonces pasame el alias para frenar el embargo ← `PERSISTENCE_DISTRACTION`  

**Referencia de trabajo:** `T_R` 3, `T_C` —, pedido REQUEST_TRANSFER.

**Qué prueba:** Supuesto inspector con deuda y embargo que pide autorizar con la clave fiscal o transferir hoy; transposición telefónica de un aviso publicado por correo.

**Notas de la referencia:** Incendio esperado por el laboratorio: REQUEST_SECRET, REQUEST_TRANSFER y REQUEST_SECURITY_ACTION (tabla y comentario), en t3 según chequear_casos.py; el propio guion aclara que REQUEST_SECURITY_ACTION sale porque la regla busca el trozo «autoriza». t_r_linea = 3 coincide. Etiquetas: la línea 3 ofrece dos pedidos alternativos; se toma REQUEST_TRANSFER («transferir hoy») como `pedido` por ser el explícito. «autorizar con su clave fiscal» puede leerse como pedido de la clave (REQUEST_SECRET, así lo entiende B en la línea 4) o como acción de seguridad (REQUEST_SECURITY_ACTION); se dejan las dos en la evidencia para discutir en D07. Sin cumplimiento: B se niega y A insiste con el alias en la línea 5 (pedir el alias tampoco es mover dinero según el manual §5). Texto en minúsculas y sin tildes, como en el guion original (estilo salida de ASR), sin corregir; las letras A/B se agregaron en la conversión.

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### LAB-arca-deuda-parafrasis

vishing · 5 líneas

` 1` **A:** le habla el fisco tiene una intimacion pendiente ← `AUTHORITY_CLAIM`  
` 2` **B:** de que me hablan  
` 3` **A:** regularice hoy con su homebanking o le embargo la cuenta ← **T_R** · `REQUEST_TRANSFER`, `URGENCY_PRESSURE`, `THREAT_FEAR`  
` 4` **B:** no pienso pagar nada por telefono ← _rechazo_  
` 5` **A:** entonces deme el cbu para frenar esto ← `PERSISTENCE_DISTRACTION`  

**Referencia de trabajo:** `T_R` 3, `T_C` —, pedido REQUEST_TRANSFER.

**Qué prueba:** Paráfrasis anti-overfit de la deuda fiscal: intimación, pago por homebanking bajo amenaza de embargo y pedido del CBU tras una negativa.

**Notas de la referencia:** Paráfrasis de LAB-arca-deuda en el laboratorio; par null. Incendio esperado por el laboratorio: REQUEST_TRANSFER en t5 («deme el cbu»), con t4 («no pienso pagar nada») mudo por negación (pasada 21); goteo en t5. Difiere: t_r_linea = 3, porque «regularice hoy con su homebanking o le embargo la cuenta» ya pide pagar (REQUEST_TRANSFER incluye pagos) con plazo y amenaza; las reglas del laboratorio no reconocen esa forma, y la respuesta de B («no pienso pagar nada») confirma que lo entendió como pedido de pago. Discutible: si el equipo decide que «regularice» sin destino ni monto no es pedido de alto riesgo, la marca pasaría a la línea 5, aunque pedir el CBU tampoco es mover dinero según el manual §5. Sin cumplimiento: B se niega en la línea 4. Texto en minúsculas y sin tildes, como en el guion original (estilo salida de ASR), sin corregir; las letras A/B se agregaron en la conversión.

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### LAB-banco-app-parafrasis

legitima_dificil · 5 líneas

` 1` **A:** corta aca y fijate vos en la app del banco ← _contexto_  
` 2` **B:** dale a ver  
` 3` **A:** entra con tu huella y revisa los movimientos ← _contexto_  
` 4` **B:** no hay nada raro ← _contexto_  
` 5` **A:** buenisimo era mentira entonces  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** Paráfrasis anti-overfit de la legítima del banco: consejo de cortar y revisar uno mismo la app, sin pedido.

**Notas de la referencia:** Paráfrasis de LAB-banco-revisa-app en el laboratorio; par null. Incendio esperado por el laboratorio: ninguno y sin goteo (comentario del guion); coincide con t_r_linea null. Hablantes: la línea 5 se asignó a A por alternancia; también podría decirla B después de revisar los movimientos. «entra con tu huella» se refiere a la app propia de B: no es pedido de credencial ni de acceso. Texto en minúsculas y sin tildes, como en el guion original (estilo salida de ASR), sin corregir; las letras A/B se agregaron en la conversión.

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### LAB-banco-codigo

vishing · 7 líneas

` 1` **A:** hola te llamo del banco hay una compra que no reconocemos ← `AUTHORITY_CLAIM`  
` 2` **B:** ah si cual  
` 3` **A:** si no la frenamos ahora te vacian la cuenta ← `URGENCY_PRESSURE`, `THREAT_FEAR`  
` 4` **B:** bueno y que hago  
` 5` **A:** no cortes y decime el codigo de seis digitos que te acaba de llegar ← **T_R** · `REQUEST_AUTH_CODE`, `ISOLATION_SECRECY`  
` 6` **B:** el codigo es nueve ocho siete seis cinco cuatro ← **T_C** · _cumplimiento_  
` 7` **A:** listo con eso la cancelo desde aca  

**Referencia de trabajo:** `T_R` 5, `T_C` 6, pedido REQUEST_AUTH_CODE.

**Qué prueba:** Compra no reconocida, presión para frenarla y pedido del código de seis dígitos que acaba de llegar, con cumplimiento.

**Notas de la referencia:** Incendio esperado por el laboratorio: REQUEST_AUTH_CODE (tabla y comentario), en t5 según chequear_casos.py. Coincide con t_r_linea = 5. «no cortes» va en la misma línea del pedido. Cumplimiento en la línea 6: dicta seis cifras ficticias. Texto en minúsculas y sin tildes, como en el guion original (estilo salida de ASR), sin corregir; las letras A/B se agregaron en la conversión.

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### LAB-banco-codigo-parafrasis

vishing · 7 líneas

` 1` **A:** hola soy del banco vimos un gasto que no es tuyo ← `AUTHORITY_CLAIM`  
` 2` **B:** cual gasto  
` 3` **A:** si no lo frenamos te sacan todo ← `THREAT_FEAR`  
` 4` **B:** y que tengo que hacer  
` 5` **A:** decime el codigo que te mandamos al telefono ← **T_R** · `REQUEST_AUTH_CODE`  
` 6` **B:** dice ocho uno nueve dos siete cero ← **T_C** · _cumplimiento_  
` 7` **A:** listo ya lo freno desde aca  

**Referencia de trabajo:** `T_R` 5, `T_C` 6, pedido REQUEST_AUTH_CODE.

**Qué prueba:** Paráfrasis anti-overfit del código bancario: gasto que no es tuyo, amenaza de perderlo todo y pedido del código que llegó al teléfono, con cumplimiento.

**Notas de la referencia:** Paráfrasis de LAB-banco-codigo en el laboratorio; par null. Incendio esperado por el laboratorio: REQUEST_AUTH_CODE en t5 (comentario y tabla), goteo en t5. Coincide con t_r_linea = 5. Cumplimiento en la línea 6: dicta seis cifras ficticias. Texto en minúsculas y sin tildes, como en el guion original (estilo salida de ASR), sin corregir; las letras A/B se agregaron en la conversión.

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### LAB-banco-gasto-sin-pedido

legitima_dificil · 3 líneas

` 1` **A:** te llama el banco porque vimos un gasto que no cierra ← `AUTHORITY_CLAIM`  
` 2` **A:** no hagas nada por telefono ← _contexto_  
` 3` **A:** entra vos a la aplicacion cuando puedas y fijate ← _contexto_  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** Quien llama se presenta como el banco y habla de un gasto que no cierra, igual que un vishing, pero no pide nada y deriva a la aplicación.

**Notas de la referencia:** Hablantes: el guion no trae respuestas de la otra parte; las tres líneas se leen como de quien llama por el banco y el caso queda como monólogo de A. Asignación dudosa: si el equipo prefiere, la línea 2 o la 3 podrían ser de otra persona, aunque ambas se dirigen a quien escucha («no hagas», «entra vos»). Incendio esperado por el laboratorio: ninguno (caso difícil fuera del oracle de chequear_casos.py; en resultados/2026-09-24/resultados-2026-09-24.csv no hubo incendio y el goteo tuvo una sola opinión alta en t1, 0,616, sin disparo). Coincide con t_r_linea null. El diálogo no permite saber si la identidad del banco es auténtica: la clase legítima sale del guion (no pide nada y deriva a la aplicación). Texto en minúsculas y sin tildes, como en el guion original (estilo salida de ASR), sin corregir; las letras A/B se agregaron en la conversión.

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### LAB-banco-niega-el-codigo

legitima_dificil · 2 líneas

` 1` **A:** ningun banco te pide el codigo por telefono ← _mencion_  
` 2` **A:** corta y revisa la aplicacion oficial ← _contexto_  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** Niega el pedido usando la palabra «codigo» («ningun banco te pide el codigo por telefono»): sirve para ver un falso disparo por palabra clave.

**Notas de la referencia:** Hablantes: las dos líneas se leen como consejo de la misma persona (A, A); dudoso, la línea 2 podría ser de otra persona que refuerza el consejo. Incendio esperado por el laboratorio: ninguno (tabla y comentario); el guion existe para ver el falso incendio de esa lista: en la pasada 1 las reglas marcaban REQUEST_AUTH_CODE en t1, hasta que se agregó la negación. Coincide con t_r_linea null. Texto en minúsculas y sin tildes, como en el guion original (estilo salida de ASR), sin corregir; las letras A/B se agregaron en la conversión.

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### LAB-banco-numeros-sin-clave

vishing · 7 líneas

` 1` **A:** che te hablo del banco hay un consumo raro en la tarjeta ← `AUTHORITY_CLAIM`  
` 2` **B:** en serio cual  
` 3` **A:** tenes que hacerlo ya sino se bloquea todo ← `URGENCY_PRESSURE`, `THREAT_FEAR`  
` 4` **B:** decime que hago  
` 5` **A:** pasame los seis numeros que te llegaron al celular ← **T_R** · `REQUEST_AUTH_CODE`  
` 6` **B:** ahi te los dicto cinco cero tres uno ocho nueve ← **T_C** · _cumplimiento_  
` 7` **A:** perfecto ya esta  

**Referencia de trabajo:** `T_R` 5, `T_C` 6, pedido REQUEST_AUTH_CODE.

**Qué prueba:** Pide «los seis numeros» que llegaron al celular sin decir «codigo», con cumplimiento.

**Notas de la referencia:** Paráfrasis de LAB-banco-codigo sin la palabra «codigo» en el laboratorio; par null. Incendio esperado por el laboratorio: REQUEST_AUTH_CODE en t5 (patrón «numeros», pasada 14), goteo en t5. Coincide con t_r_linea = 5. La línea 3 («tenes que hacerlo ya») presiona antes de decir qué hay que hacer. Cumplimiento en la línea 6: dicta seis cifras ficticias. Texto en minúsculas y sin tildes, como en el guion original (estilo salida de ASR), sin corregir; las letras A/B se agregaron en la conversión.

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### LAB-banco-revisa-app

legitima_dificil · 5 líneas

` 1` **A:** te aviso que hubo un consumo en la tarjeta ← _mencion_  
` 2` **B:** ok donde lo miro  
` 3` **A:** corta esta comunicacion y entra vos a la aplicacion oficial ← _contexto_  
` 4` **B:** no me vas a pedir nada no ← _contexto_  
` 5` **A:** exacto yo no te pido datos corta y revisa ahi ← _rechazo_  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** Misma zona que el vishing del banco (un consumo en la tarjeta), pero deriva a la aplicación oficial y aclara que no pide datos.

**Notas de la referencia:** Pareja en el laboratorio: vishing/banco-codigo.txt (LAB-banco-codigo); par null. Incendio esperado por el laboratorio: ninguno (tabla y comentario); coincide con t_r_linea null. A no se presenta como banco: el diálogo no tiene evidencia para saber quién llama ni si es auténtico. La línea 5 niega pedir datos (se anota como rechazo, igual que en LG-WA-CONSULTA-01-e01). Texto en minúsculas y sin tildes, como en el guion original (estilo salida de ASR), sin corregir; las letras A/B se agregaron en la conversión.

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### LAB-digitos-sin-palabra

vishing · 5 líneas

` 1` **A:** hola te llamo de la tarjeta por un cargo que no reconocemos ← `AUTHORITY_CLAIM`  
` 2` **B:** ah si cual  
` 3` **A:** se cae la operacion si no lo confirmas ahora ← `URGENCY_PRESSURE`  
` 4` **B:** y como lo confirmo  
` 5` **A:** leeme lo que te acaba de llegar al telefono, de a uno ← **T_R** · `REQUEST_AUTH_CODE`  

**Referencia de trabajo:** `T_R` 5, `T_C` —, pedido REQUEST_AUTH_CODE.

**Qué prueba:** Pide leer, de a uno, los dígitos del mensaje recién llegado sin decir «codigo», «token» ni «numeros».

**Notas de la referencia:** Incendio esperado por el laboratorio: el guion no fija turno; la etiqueta esperada es REQUEST_AUTH_CODE y el texto está escrito para que las reglas no disparen (resultados-2026-09-24.csv: sin incendio ni goteo). t_r_linea = 5: «leeme lo que te acaba de llegar al telefono, de a uno» es el primer pedido de alto riesgo, indirecto (no nombra el código, pero pide dictarlo). La línea 3 pide «confirmar» sin decir cómo; no se toma como pedido. Sin cumplimiento: el guion termina en el pedido. Texto en minúsculas y sin tildes, como en el guion original (estilo salida de ASR), sin corregir; las letras A/B se agregaron en la conversión.

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### LAB-familiar-llama-vos

legitima_dificil · 5 líneas

` 1` **A:** me llamaron y dijeron que un familiar estaba en peligro ← _mencion_  
` 2` **B:** corta  
` 3` **B:** llama vos al numero que tenes guardado ← _contexto_  
` 4` **B:** no saques plata ni hables con un intermediario ← _mencion_  
` 5` **A:** ya lo llamo yo ← _contexto_  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** Mismo tema que el familiar en peligro, pero el consejo es cortar, llamar al número guardado y no sacar plata.

**Notas de la referencia:** Pareja en el laboratorio: vishing/familiar-peligro.txt (LAB-familiar-peligro); par null. Incendio esperado por el laboratorio: ninguno (tabla y comentario); coincide con t_r_linea null (pasada 4: «no saques plata» queda muda por la negación). Hablantes: las líneas 2 a 4 son tres consejos seguidos de B. Texto en minúsculas y sin tildes, como en el guion original (estilo salida de ASR), sin corregir; las letras A/B se agregaron en la conversión.

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### LAB-familiar-peligro

vishing · 6 líneas

` 1` **A:** escucha tu hermano esta en un problema grave y yo soy el intermediario ← `AUTHORITY_CLAIM`  
` 2` **B:** que le paso  
` 3` **A:** no llames a nadie si no se complica ← `ISOLATION_SECRECY`, `THREAT_FEAR`  
` 4` **A:** necesito que saques la plata de la cuenta y me la pases ← **T_R** · `REQUEST_TRANSFER`  
` 5` **B:** no voy a mandar nada ← _rechazo_  
` 6` **A:** entonces pasame el alias ahora ← `PERSISTENCE_DISTRACTION`, `URGENCY_PRESSURE`  

**Referencia de trabajo:** `T_R` 4, `T_C` —, pedido REQUEST_TRANSFER.

**Qué prueba:** Familiar en problemas e intermediario que aísla y pide sacar la plata de la cuenta y pasársela.

**Notas de la referencia:** Incendio esperado por el laboratorio: REQUEST_TRANSFER (tabla y comentario), en t4 según chequear_casos.py desde la pasada 4 (antes t6, por «alias»). Coincide con t_r_linea = 4. Hablantes: las líneas 3 y 4 son de A seguidas. Sin cumplimiento: B se niega en la línea 5 y A insiste en la 6; «pasame el alias» es ambiguo (el alias de B o adónde transferir) y no se etiqueta como pedido. Texto en minúsculas y sin tildes, como en el guion original (estilo salida de ASR), sin corregir; las letras A/B se agregaron en la conversión.

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### LAB-familiar-peligro-parafrasis

vishing · 6 líneas

` 1` **A:** hola soy un amigo de tu hijo tuvo un accidente ← `AUTHORITY_CLAIM`  
` 2` **B:** que paso esta bien  
` 3` **A:** no avises a nadie venite ya ← `ISOLATION_SECRECY`, `URGENCY_PRESSURE`  
` 4` **A:** trae diez mil pesos a la plaza ahora ← **T_R** · `REQUEST_TRANSFER`, `URGENCY_PRESSURE`  
` 5` **B:** no puedo ir tan rapido  
` 6` **A:** bueno transferime a este alias entonces ← `REQUEST_TRANSFER`, `PERSISTENCE_DISTRACTION`  

**Referencia de trabajo:** `T_R` 4, `T_C` —, pedido REQUEST_TRANSFER.

**Qué prueba:** Paráfrasis anti-overfit del familiar en peligro: un amigo del hijo accidentado aísla, pide llevar efectivo y después transferir a un alias.

**Notas de la referencia:** Paráfrasis de LAB-familiar-peligro en el laboratorio; par null. Incendio esperado por el laboratorio: REQUEST_TRANSFER en t6 («transferime a este alias»); el comentario reconoce t4 («diez mil pesos») como hueco conocido de las reglas, y el goteo en t5. Difiere: t_r_linea = 4, porque «trae diez mil pesos a la plaza ahora» pide entregar efectivo, que el manual §5 incluye en REQUEST_TRANSFER; la línea 6 es un segundo pedido. Hablantes: las líneas 3 y 4 son de A seguidas. Sin cumplimiento: B dice que no llega y A cambia a transferencia. Texto en minúsculas y sin tildes, como en el guion original (estilo salida de ASR), sin corregir; las letras A/B se agregaron en la conversión.

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### LAB-giro-sin-plata

vishing · 5 líneas

` 1` **A:** habla un amigo de tu hermano, tuvo un accidente ← `AUTHORITY_CLAIM`  
` 2` **B:** dios que paso  
` 3` **A:** necesito que me gires ya a la cuenta que te dicto ← **T_R** · `REQUEST_TRANSFER`, `URGENCY_PRESSURE`  
` 4` **B:** cuanto ← _contexto_  
` 5` **A:** son diez mil, no cortes ← `ISOLATION_SECRECY`  

**Referencia de trabajo:** `T_R` 3, `T_C` —, pedido REQUEST_TRANSFER.

**Qué prueba:** Pide girar dinero a una cuenta que dicta sin decir «plata», «alias», «cbu» ni «transferencia».

**Notas de la referencia:** Incendio esperado por el laboratorio: el guion no fija turno; la etiqueta esperada es REQUEST_TRANSFER y el texto está escrito para que las reglas no disparen (resultados-2026-09-24.csv: sin incendio; goteo con una sola opinión alta en t3, sin disparo). t_r_linea = 3: «necesito que me gires ya a la cuenta que te dicto». La línea 4 («cuanto») muestra disposición, pero no es un cumplimiento observable: t_c_linea null. La identidad («un amigo de tu hermano») no se puede verificar en el diálogo; AUTHORITY_CLAIM se usa en el sentido de persona de confianza del manual. Texto en minúsculas y sin tildes, como en el guion original (estilo salida de ASR), sin corregir; las letras A/B se agregaron en la conversión.

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### LAB-mensajeria-no-pases-nada

legitima_dificil · 5 líneas

` 1` **A:** me llamo alguien que dice ser soporte de la aplicacion de mensajes ← _mencion_  
` 2` **B:** no le contestes ← _contexto_  
` 3` **A:** corto y abro yo la aplicacion ← _contexto_  
` 4` **B:** si te piden algo raro corta ← _contexto_  
` 5` **A:** dale  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** Mismo tema que el falso soporte de la aplicación de mensajes, sin las palabras de las reglas y sin pedido.

**Notas de la referencia:** Pareja en el laboratorio: vishing/whatsapp-codigo.txt (LAB-whatsapp-codigo); par null. Incendio esperado por el laboratorio: ninguno (tabla y comentario); coincide con t_r_linea null. Según el comentario del guion, evita las palabras de la regla (no dice «codigo»). Texto en minúsculas y sin tildes, como en el guion original (estilo salida de ASR), sin corregir; las letras A/B se agregaron en la conversión.

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### LAB-no-bajes-nada

legitima_dificil · 4 líneas

` 1` **A:** me llamaron para que baje un programa y les muestre el celular ← _mencion_  
` 2` **B:** no bajes nada ← _contexto_  
` 3` **A:** corto y llamo yo al banco por el numero de atras de la tarjeta ← _contexto_  
` 4` **B:** bien  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** Mismo tema que el acceso remoto (bajar un programa y mostrar el celular), contado para no hacerlo y llamar al banco por el número de la tarjeta.

**Notas de la referencia:** Pareja en el laboratorio: vishing/acceso-remoto.txt (LAB-acceso-remoto); par null. Incendio esperado por el laboratorio: ninguno (tabla y comentario); coincide con t_r_linea null. La línea 1 relata un pedido de acceso remoto hecho por terceros en otra llamada: es mención, no pedido. Texto en minúsculas y sin tildes, como en el guion original (estilo salida de ASR), sin corregir; las letras A/B se agregaron en la conversión.

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### LAB-pantalla-sin-programa

vishing · 5 líneas

` 1` **A:** soy del soporte de tu banco ← `AUTHORITY_CLAIM`  
` 2` **B:** que paso  
` 3` **A:** bajate este programita y dejame mirar lo que ves en el celular ← **T_R** · `REQUEST_REMOTE_ACCESS`  
` 4` **B:** no entiendo  
` 5` **A:** asi freno el debito que te estan haciendo ← _contexto_  

**Referencia de trabajo:** `T_R` 3, `T_C` —, pedido REQUEST_REMOTE_ACCESS.

**Qué prueba:** Pide bajar un «programita» y mirar la pantalla del celular sin nombrar un programa de acceso remoto ni decir «instala».

**Notas de la referencia:** Incendio esperado por el laboratorio: el guion no fija turno; la etiqueta esperada es REQUEST_REMOTE_ACCESS y el texto evita las palabras de la regla (resultados-2026-09-24.csv: sin incendio ni opinión de goteo). t_r_linea = 3: «bajate este programita y dejame mirar lo que ves en el celular». Sin cumplimiento: B dice «no entiendo» y A justifica el pedido en la línea 5. Texto en minúsculas y sin tildes, como en el guion original (estilo salida de ASR), sin corregir; las letras A/B se agregaron en la conversión.

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### LAB-portero-codigo-puerta

legitima_dificil · 2 líneas

` 1` **A:** el portero me paso el codigo de la puerta ← _mencion_  
` 2` **B:** esta en el palier, no se lo des a nadie ← _contexto_  

**Referencia de trabajo:** `T_R` —, `T_C` —, pedido —.

**Qué prueba:** Dice «codigo», pero es el código de la puerta que pasó el portero y nadie lo pide: mencionar un código no es pedirlo.

**Notas de la referencia:** Hablantes dudosos: la línea 2 se asignó a B (advierte a quien recibió el código que no lo comparta); también puede leerse como continuación de A. Incendio esperado por el laboratorio: ninguno, por ser legítima; el guion existe para mostrar el falso incendio de REQUEST_AUTH_CODE en t1 por la palabra «codigo» (Sonda D del README del laboratorio; resultados-2026-09-24.csv: incendio falso en t1). Coincide con t_r_linea null. El laboratorio no lo sumó a su oracle: lo deja como evidencia para D07 (palabra clave no es pedido). Si un código de puerta cuenta como secreto de alto riesgo queda para D07, como en TR-02-codigo-del-candado. Texto en minúsculas y sin tildes, como en el guion original (estilo salida de ASR), sin corregir; las letras A/B se agregaron en la conversión.

- [ ] La clase está bien
- [ ] De acuerdo: no hay pedido crítico
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### LAB-whatsapp-codigo

vishing · 5 líneas

` 1` **A:** hola soy del soporte de whatsapp se quiere meter alguien en tu cuenta ← `AUTHORITY_CLAIM`, `THREAT_FEAR`  
` 2` **B:** uy que tengo que hacer  
` 3` **A:** te llego un codigo de verificacion de seis digitos pasamelo por aca ← **T_R** · `REQUEST_AUTH_CODE`  
` 4` **B:** dice dos cuatro seis ocho cero uno ← **T_C** · _cumplimiento_  
` 5` **A:** gracias ya quedo frenado el ingreso  

**Referencia de trabajo:** `T_R` 3, `T_C` 4, pedido REQUEST_AUTH_CODE.

**Qué prueba:** Falso soporte de WhatsApp que pide el código de verificación de seis dígitos para quedarse con la cuenta, con cumplimiento.

**Notas de la referencia:** Incendio esperado por el laboratorio: REQUEST_AUTH_CODE (tabla y comentario), en t3 según chequear_casos.py; antes de la pasada 8 disparaba en t1 por la palabra «whatsapp» del saludo. Coincide con t_r_linea = 3. Cumplimiento en la línea 4: dicta seis cifras ficticias. El guion nombra una aplicación real («whatsapp»), igual que el caso modelo SC-WA-CODE-01-e01. Texto en minúsculas y sin tildes, como en el guion original (estilo salida de ASR), sin corregir; las letras A/B se agregaron en la conversión.

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---

### LAB-whatsapp-codigo-parafrasis

vishing · 5 líneas

` 1` **A:** te llamo del soporte de mensajes hay un acceso raro ← `AUTHORITY_CLAIM`  
` 2` **B:** como que acceso raro  
` 3` **A:** te mandamos un codigo de verificacion pasamelo ← **T_R** · `REQUEST_AUTH_CODE`  
` 4` **B:** te lo dicto uno siete dos nueve ← **T_C** · _cumplimiento_  
` 5` **A:** listo ya quedo bloqueado  

**Referencia de trabajo:** `T_R` 3, `T_C` 4, pedido REQUEST_AUTH_CODE.

**Qué prueba:** Paráfrasis anti-overfit del falso soporte de mensajería: acceso raro y pedido del código de verificación, con cumplimiento.

**Notas de la referencia:** Paráfrasis de LAB-whatsapp-codigo en el laboratorio; par null. Incendio esperado por el laboratorio: REQUEST_AUTH_CODE en t3; goteo en t2, antes del incendio. Coincide con t_r_linea = 3. Cumplimiento en la línea 4: dicta cuatro cifras ficticias (en esta paráfrasis el código tiene cuatro dígitos, no seis). Texto en minúsculas y sin tildes, como en el guion original (estilo salida de ASR), sin corregir; las letras A/B se agregaron en la conversión.

- [ ] La clase está bien
- [ ] `T_R` y `T_C` están bien
- [ ] Suena a una conversación real
- [ ] Grabarlo

**Comentarios:**

---
