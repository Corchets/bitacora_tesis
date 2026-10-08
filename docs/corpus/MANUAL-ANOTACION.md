# Manual de anotación

**Versión de trabajo para el piloto.** El 2026-10-04 se acordó una referencia mínima
por conversación: clase, marcas críticas cuando correspondan y fragmentos que las
justifican. La validación con el piloto y las ambigüedades siguen abiertas en
[D07](../gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico).

Las personas anotan lo que ocurrió; el sistema registra sus predicciones y avisos.
Un programa compara ambas salidas y calcula las [métricas](../evaluacion/METRICAS.md).
La referencia humana se guarda separada: el detector recibe texto y contexto de la
llamada, sin clase, roles de atacante/víctima, etiquetas ni marcas de referencia.

## 1. Qué registramos por conversación

| Dato | Cómo se obtiene |
|---|---|
| ID y semilla | Vinculan conversación, audio y transcripción con el escenario representado. |
| Clase: vishing o legítima | Se registra según la situación simulada y se revisa contra lo efectivamente representado. No se deduce de una palabra ni se copia sin revisar el catálogo. |
| `T_R` y `T_C`, cuando correspondan | Se ubican escuchando el audio, según [METRICAS.md](../evaluacion/METRICAS.md#1-marcas-temporales). Un evento ausente o no observable queda sin dato. |
| Evidencia seleccionada | Fragmentos que contienen el pedido, el cumplimiento o el contexto necesario para interpretarlos, con ubicación en la transcripción o el audio. |
| Notas | Ambigüedades, diferencias respecto de la ficha o problemas de grabación/anotación. |

No se exige etiquetar cada turno con las doce etiquetas candidatas. Se usan
etiquetas en los fragmentos relevantes cuando ayudan a describir un caso o revisar
una explicación. La ausencia de una etiqueta en esta anotación parcial no significa
que la maniobra esté ausente de toda la conversación.

La transcripción conserva la conversación completa y puede dividirse en segmentos
para procesarla. Esa división no obliga a crear una ficha manual por segmento.
`T_A` sale de la ejecución del sistema y no pertenece a esta referencia.

## 2. Cómo ubicar las marcas y resolver dudas

- Revisar el pedido en su contexto: mencionar un código no es pedirlo; pedir algo
  sensible tampoco prueba por sí solo un fraude. Registrar la evidencia que permite
  interpretar el evento o la ambigüedad que impide hacerlo.
- Para los márgenes de una llamada fraudulenta, localizar el primer pedido de alto
  riesgo y el primer cumplimiento observable. La marca puede caer dentro de una
  intervención; no se toma automáticamente su comienzo ni la salida de una regla.
- Si hay varios pedidos, conservar el fragmento que justifica la primera marca;
  anotar otros cuando sean necesarios para explicar un desacuerdo o una alerta.
- Si no se observa cumplimiento, `T_C` queda sin dato. Una solicitud legítima puede
  describirse como evidencia sin convertirla en evento crítico de un fraude.
- Si no hay evidencia en el diálogo para distinguir identidades auténticas de
  suplantadas, registrar ese límite. No excluir un caso solo porque el detector falle.

En ejemplos escritos sin audio se marca la posición del evento en el texto o el
turno. Los segundos se anotan sobre grabaciones, no con duraciones inventadas.
La precisión alcanzable y los casos límite se revisan en el piloto.

## 3. Ejemplo de referencia de una conversación

**Ilustrativo:** las marcas siguientes muestran el formato, no una grabación medida.
El contexto ficticio es una suplantación de soporte que busca el código de activación
de la cuenta. El JSON representa la referencia de la conversación completa; los
fragmentos seleccionados no reemplazan su transcripción.

```json
{
  "call_id": "C001",
  "scenario_id": "SC-WA-CODE-01",
  "class": "vishing",
  "t_r_s": 58,
  "t_c_s": 64,
  "evidence": [
    {
      "time_s": 58,
      "event": "pedido",
      "text": "Decime el código de seis dígitos que te llegó por SMS.",
      "labels": ["REQUEST_AUTH_CODE"]
    },
    {
      "time_s": 64,
      "event": "cumplimiento",
      "text": "El código es..."
    }
  ],
  "notes": "Solicitud dentro de una simulación de suplantación de soporte."
}
```

En una legítima sin pedido crítico, `t_r_s` y `t_c_s` quedan en `null`. El formato es
un ejemplo de exportación; no obliga a escribir JSON ni congela una interfaz de
código. La ficha puede completarse con una herramienta o planilla y exportarse.

## 4. Trabajo asistido y revisión compartida

1. Obtener una transcripción inicial, por ejemplo con ASR local, y revisar el texto
   contra el audio. El borrador automático no es la referencia final.
2. Completar la ficha mínima y seleccionar los fragmentos necesarios. Una herramienta
   puede ayudar a localizar y exportar tiempos; las personas verifican las marcas.
3. Los cuatro integrantes anotan independientemente las mismas conversaciones de
   una muestra común, sin ver las respuestas de los demás. Se acuerda esa muestra
   antes de anotar; no implica que los cuatro deban anotar todo el corpus.
4. Comparar las versiones originales, describir desacuerdos y acordar una referencia
   final. Conservar los originales y medir el esfuerzo antes de ampliar.

El acuerdo se analiza antes de la adjudicación. No se exige un Kappa sobre doce
etiquetas para empezar: el análisis debe corresponder a lo realmente anotado
(clase, presencia de eventos y ubicación de marcas). La muestra, herramienta,
procedimiento de revisión del resto y medidas de acuerdo se precisan en D07.

## 5. Vocabulario candidato para evidencia

> **Estado: propuesta sin discutir.** Estas etiquetas orientan fichas y revisión de
> fragmentos; no son doce salidas obligatorias del detector ni una taxonomía validada.
> Sus definiciones se contrastan con el catálogo, las fuentes y el piloto en D07.

Una etiqueta describe lo dicho; por sí sola no determina la clase de la llamada.
Por ejemplo, una presentación como banco o un pedido de transferencia también
pueden aparecer en conversaciones legítimas.

### Técnicas de manipulación o construcción de confianza

| Etiqueta                  | Qué la dispara                                                                                                                        | Qué **no** la dispara                                                                                                |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `AUTHORITY_CLAIM`         | Quien llama se presenta como una entidad o persona con autoridad o confianza: un banco, un organismo, un soporte técnico, un familiar | Que la persona _suponga_ con quién habla. La etiqueta necesita que el llamante lo afirme                             |
| `URGENCY_PRESSURE`        | Impone tiempo, rapidez o consecuencias por demorar: "tenés dos minutos", "si cortás se bloquea"                                       | Que el tema sea urgente en sí mismo. Lo que se anota es la presión que ejerce el llamante, no la gravedad del asunto |
| `THREAT_FEAR`             | Plantea pérdida, bloqueo, delito, sanción o peligro dirigidos a la persona                                                            | Informar un hecho negativo sin atribuirle consecuencias a la persona ("se registró una compra")                      |
| `ISOLATION_SECRECY`       | Pide no cortar, no consultar, no hablar con terceros, o desalienta verificar por otro canal                                           | Pedir silencio por ruido o pedir que no se interrumpa para poder explicar                                            |
| `TRUST_BUILDING`          | Usa datos o procedimientos para sostener su identidad o generar confianza: menciona datos conocidos, un trámite o pasos de verificación                     | Presentarse por su nombre sin aportar ese tipo de respaldo; la etiqueta no permite decidir si la identidad es auténtica               |
| `PERSISTENCE_DISTRACTION` | Insiste tras una objeción, redirige la duda o mantiene a la persona cognitivamente ocupada                                            | Repreguntar una vez porque no se escuchó                                                                             |

### Acciones solicitadas

| Etiqueta                  | Qué la dispara (ejemplos)                                                                           | Qué **no** la dispara                                                          |
| ------------------------- | --------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| `REQUEST_AUTH_CODE`       | Pide un código de un solo uso: OTP, token, código de WhatsApp                                       | Mencionar que un código existe o que va a llegar, sin pedir que se lo dicte    |
| `REQUEST_SECRET`          | Pide una credencial permanente: clave, PIN, CVV, contraseña, usuario                                | Pedir confirmar datos que la entidad ya tiene, como los últimos cuatro dígitos |
| `REQUEST_PERSONAL_DATA`   | Pide datos identificatorios: DNI, CUIL, domicilio, o una foto de identificación                     | Que la persona los diga por su cuenta sin que se los pidan                     |
| `REQUEST_TRANSFER`        | Pide mover dinero: transferencia, pago, cripto, entrega de efectivo, operar un cajero               | Hablar de un movimiento de dinero ya ocurrido                                  |
| `REQUEST_REMOTE_ACCESS`   | Pide instalar acceso remoto o compartir pantalla                                                    | Pedir que se abra una app para mirar algo uno mismo                            |
| `REQUEST_SECURITY_ACTION` | Pide ejecutar una acción de seguridad: abrir un enlace, cambiar una clave, autorizar un dispositivo | Recomendar cambiar la clave por el canal oficial, que es conducta segura       |

### Fundamentos y límites del vocabulario

Recuperación selectiva del [relevamiento del PR #38](https://github.com/Corchets/bitacora_tesis/pull/38),
cotejada el 2026-10-04. Las fuentes respaldan situaciones observadas; la correspondencia
con nuestras etiquetas es una interpretación de trabajo del equipo, pendiente de
validación en [D07](../gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico).

- El [informe UFECI 2024](https://www.mpf.gob.ar/ufeci/files/2025/06/UFECI_informe_anual_2024-1.pdf)
  describe llamadas de falsos bancos o empresas que conducen a instalar acceso remoto,
  y otra variante que obtiene credenciales o induce transferencias (p. 18). Esto fundamenta
  pedidos candidatos `REQUEST_REMOTE_ACCESS`, `REQUEST_SECRET` y `REQUEST_TRANSFER`;
  no convierte cualquier pedido de esas acciones en fraude. El mismo informe describe
  llamadas que obtienen el código de WhatsApp con distintos pretextos (p. 20): un pedido
  `REQUEST_AUTH_CODE` puede aparecer bajo identidades y motivos diferentes. Son reportes
  recibidos por la UFECI, no una muestra representativa de todas las llamadas argentinas.
- La [capacitación UFECI–WhatsApp del 2021-11-24](https://www.fiscales.gob.ar/ciberdelincuencia/la-ufeci-y-whatsapp-capacitaron-a-personal-judicial-y-del-mpf-frente-a-las-maniobras-fraudulentas-para-tomar-control-de-las-cuentas-de-mensajeria/)
  documenta pedidos de código mediante llamadas falsas sobre vacunación. Aporta otro
  antecedente de la modalidad; la identidad declarada y el pedido se describen por
  separado. No fija cómo debe redactarse una conversación simulada.
- Los [consejos de la Policía de la Ciudad del 2020-10-08](https://buenosaires.gob.ar/gcaba_historico/noticias/consejos-de-proteccion-de-la-policia-de-la-ciudad-ante-estafas-telefonicas)
  describen suplantación de familiares o entidades, pretextos de secuestro o accidentes
  y control de la comunicación. Ese control motiva revisar `ISOLATION_SECRECY`, pero la
  fuente no prueba cada conducta incluida en su definición: hay que observar en el
  diálogo el pedido de no cortar, de guardar secreto o de no verificar. Tampoco prueba
  que el aislamiento sea exclusivo del teléfono ni justifica agregar una nueva semilla
  al catálogo sin acordarla.

- [Stajano y Wilson (2011)](https://www.cl.cam.ac.uk/~fms27/papers/2011-StajanoWil-scam.pdf)
  analizan estafas y presentan principios de distracción (p. 71), obediencia a la
  autoridad (p. 72) y presión temporal (p. 73). Son antecedentes conceptuales para
  `PERSISTENCE_DISTRACTION`, `AUTHORITY_CLAIM` y `URGENCY_PRESSURE`, con correspondencia
  parcial: distracción no define la insistencia tras una objeción. Su ejemplo de
  credibilidad mediante jerga y procedimientos (p. 72) también informa `TRUST_BUILDING`.
  El material parte de estafas recreadas para televisión, no de una evaluación
  controlada de nuestro detector ni de llamadas argentinas.

Las modalidades del [catálogo](CATALOGO-ESCENARIOS.csv) aportan contextos para probar
las reglas; no se transforman automáticamente en clases nuevas. Las definiciones de
evidencia tampoco equivalen a principios psicológicos validados. El borrador del PR
proponía otras correspondencias con Ferreira et al. (2015) y Jones et al. (2021):
sus textos no pudieron cotejarse al preparar esta sección y esas correspondencias
no se adoptan aquí como fundamento confirmado. Las referencias y citas no
verificadas quedan fuera del manual, sin concluir que las fuentes no existan.

## 6. Qué falta para cerrar D07

- Probar el marcado de pedidos y cumplimiento con audio y resolver casos ambiguos.
- Acordar la muestra común, la revisión del resto y cómo informar desacuerdos de clase
  y marcas; registrar la precisión temporal que permite el material.
- Elegir una herramienta por facilidad y costo observado, no por exigir un formato.
- Revisar las etiquetas que se usen para explicaciones, con ejemplos observables y
  respaldo verificable. Una evaluación exhaustiva por etiqueta requeriría anotación
  adicional y un protocolo acordado antes de medirla.
