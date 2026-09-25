# Tipología de maniobras de vishing en Argentina

**Fecha:** 2026-09-25 (borrador v0)
**Issue:** [#26](https://github.com/Corchets/bitacora_tesis/issues/26). Alimenta
[#17](https://github.com/Corchets/bitacora_tesis/issues/17) (catálogo de escenarios) y
[D07](../gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) ([#32](https://github.com/Corchets/bitacora_tesis/issues/32)).
**Estado:** borrador de trabajo. **No cierra D07.** No es un ADR.

> **Estado: propuesta sin discutir.** La tipología de §3 y §4 sistematiza lo que ya está verificado
> en el [catálogo de escenarios](../datos-etica/CATALOGO-ESCENARIOS.csv); no agrega fuentes nuevas.
> Las secciones marcadas **PENDIENTE** no tienen respaldo todavía y no deben citarse.

Este archivo es la fuente de verdad de la tipología. Las fuentes por escenario siguen viviendo en el
catálogo (una fila, una fuente, una fecha de consulta); acá solo se agregan y se comparan.

## 1. Qué responde este documento

1. ¿Qué modalidades de engaño telefónico documentan organismos oficiales argentinos?
2. ¿Qué maniobras de manipulación (capa 1) y qué pedidos (capa 2) aparecen en cada una?
3. ¿Qué fundamento conceptual tienen esas maniobras en la literatura de ingeniería social?
4. ¿Las modalidades argentinas son etiquetas nuevas o instancias de las 6+6 del
   [manual de anotación](../datos-etica/MANUAL-ANOTACION.md)? (pregunta abierta de D07)

**Qué no responde:** prevalencia ni frecuencia de cada modalidad. Las fuentes son advertencias
públicas, no estadísticas; que una modalidad aparezca documentada no dice cuán común es.

## 2. Método

- Revisión dirigida, no exhaustiva, según el [protocolo de revisión](PROTOCOLO-REVISION.md)
  (fuentes primarias no académicas: organismos argentinos).
- Cada búsqueda se registra en la tabla de registro del protocolo con fecha, base y cadena.
- Una modalidad entra a la tipología solo si hay una fuente oficial o académica abierta y leída que
  la describa **como llamada telefónica** (no solo como mensaje o sitio falso).
- Las maniobras se codifican con las etiquetas de trabajo del manual; la asignación por modalidad
  es del equipo, no de la fuente.

## 3. Modalidades documentadas

Síntesis de las filas `vishing` del catálogo con estado `revisado`. La columna _Fuente_ remite al
catálogo, donde está la URL y la fecha de consulta.

| Modalidad | Se presenta como | Qué busca | Pedido crítico (capa 2) | Fuente (ver catálogo) |
|---|---|---|---|---|
| Compra sospechosa y pedido de código | banco | código de verificación | `REQUEST_AUTH_CODE` | BCRA — `SC-BANK-OTP-01` |
| Verificación falsa de WhatsApp | soporte o conocido | código de activación de la cuenta | `REQUEST_AUTH_CODE` | Min. Seguridad, UFECI — `SC-WA-CODE-01` |
| Falso soporte que pide la clave | mesa de ayuda | usuario y contraseña | `REQUEST_SECRET` | BCRA — `SC-SOPORTE-CLAVE-01` |
| Beneficio previsional falso | ANSES / organismo previsional | datos personales | `REQUEST_PERSONAL_DATA` | ANSES, UFECRI-MPF — `SC-ORG-BENEFICIO-01` |
| Premio o sorteo | empresa u organizador | datos de cuenta o tarjeta | `REQUEST_PERSONAL_DATA` | BCRA, Min. Seguridad — `SC-PREMIO-01` |
| Cambio de clave por teléfono | banco u organismo público | que la persona cambie o entregue la clave | `REQUEST_SECURITY_ACTION` | Min. Seguridad — `SC-CLAVE-CAMBIO-01` |
| Familiar en apuros | familiar | dinero | `REQUEST_TRANSFER` | UFECRI-MPF — `SC-FAMILIAR-DINERO-01` |
| Canje de billetes | entidad bancaria | efectivo o transferencia | `REQUEST_TRANSFER` | UFECRI-MPF — `SC-BANK-BILLETES-01` |
| Pantalla compartida | banco, empresa de servicios o soporte | acceso al dispositivo | `REQUEST_REMOTE_ACCESS` | Banco Galicia, UFECI — `SC-SOPORTE-REMOTO-01` |

**Descartada por falta de fuente:** _resguardo de fondos por causa judicial_ (policía o fiscalía,
`SC-POLICIA-RESGUARDO-01`). La propuso el modelo; UFECRI enumera familiar, entidad bancaria y
empleado público, no policía. El 2026-09-25 se revisaron además el informe anual 2024 de la UFECI,
la Policía de la Ciudad y el Ministerio de Seguridad (§6.1 y §6.2): ninguna fuente describe un
falso policía o fiscal **por teléfono**. Sigue descartada.

**Documentada, sin semilla en el catálogo:** _secuestro virtual_ (§6.2). Si entra al catálogo es
decisión del equipo; hasta entonces no se diseña semilla.

## 4. Maniobras por modalidad

Asignación de trabajo del catálogo (capa 1). `X` = la semilla declara esa maniobra.

| Escenario | `AUTHORITY_CLAIM` | `URGENCY_PRESSURE` | `THREAT_FEAR` | `ISOLATION_SECRECY` | `TRUST_BUILDING` | `PERSISTENCE_DISTRACTION` |
|---|:-:|:-:|:-:|:-:|:-:|:-:|
| `SC-BANK-OTP-01` | X | X | | X | | |
| `SC-WA-CODE-01` | | X | | | X | |
| `SC-SOPORTE-CLAVE-01` | X | | | | X | X |
| `SC-ORG-BENEFICIO-01` | X | X | | | X | |
| `SC-PREMIO-01` | | X | | | X | X |
| `SC-CLAVE-CAMBIO-01` | X | X | | X | | |
| `SC-FAMILIAR-DINERO-01` | | X | X | X | X | |
| `SC-BANK-BILLETES-01` | X | X | | | X | |
| `SC-SOPORTE-REMOTO-01` | X | X | X | X | | |
| **Total (9 semillas)** | **6** | **8** | **2** | **4** | **6** | **2** |

Lectura preliminar (sin valor estadístico, son 9 semillas diseñadas por el equipo):

- La urgencia aparece en casi todas las modalidades: es la maniobra más transversal.
- `THREAT_FEAR` y `PERSISTENCE_DISTRACTION` tienen dos semillas cada una. Si el corpus las
  reproduce en esa proporción, quedan en riesgo de ser clases raras (Manual §1).
- `REQUEST_REMOTE_ACCESS` y `REQUEST_SECURITY_ACTION` tienen una sola semilla cada una. La de
  acceso remoto tiene ahora dos fuentes oficiales (Banco Galicia y UFECI 2024); el problema es la
  cantidad de semillas, no el respaldo.

## 5. Fundamento en la literatura de ingeniería social

> **Parcialmente verificado.** Solo entra acá lo que alguien del equipo leyó en el texto de la
> fuente. Un intento de completar esta sección con deep research (2026-09-25) produjo citas y
> fuentes que no resistieron el cotejo: quedan registradas en §5.3 para que nadie las reutilice.

### 5.1 Fuentes verificadas

| Fuente | Qué se verificó | Cómo |
|---|---|---|
| Ferreira, A., Coventry, L. y Lenzini, G. (2015). *Principles of persuasion in social engineering and their use in phishing*. HAS 2015, LNCS 9190, Springer. [PDF abierto](https://orbilu.uni.lu/bitstream/10993/20301/1/FerreiraAna-CameraReady.pdf) | Definiciones literales de *Authority* y *Social Proof*, y la figura que integra las taxonomías de Cialdini, Gragg y Stajano | Corchets leyó el PDF el 2026-09-25 |
| Stajano, F. y Wilson, P. (2011). *Understanding scam victims: seven principles for systems security*. *Communications of the ACM*, 54(3). | Texto literal del *Time Principle* | Corchets leyó el artículo el 2026-09-25 |

Citas literales cotejadas:

- Ferreira et al., *Authority (AUTH)*: _"Society trains people not to question authority so they are
  conditioned to respond to it. People usually follow an expert or pretense of authority and do a
  great deal for someone they think is an authority."_
- Ferreira et al., *Social Proof (SP)*: _"People tend to mimic what the majority of people do or
  seem to be doing. People let their guard and suspicion down when everyone else appears to share
  the same behaviours and risks. In this way, they will not be held solely responsible for their
  actions."_
- Stajano y Wilson, *Time Principle*: _"When under time pressure to make an important decision, we
  use a different decision strategy, and hustlers steer us toward one involving less reasoning."_

**Sobre las páginas:** el PDF abierto de Ferreira et al. no tiene la paginación del volumen LNCS, y
del artículo de Stajano y Wilson se leyó el recuadro del principio sin registrar el número de
página. Hasta resolverlo, estas citas se referencian **por nombre de principio**, no por página. El
número de página se completa contra la versión publicada antes de que las citas entren al informe.

**Nombre correcto del principio de Stajano y Wilson:** la figura de Ferreira et al. lo identifica
como **Social compliance** (y el que se corresponde con *Social Proof*, como **Herd**). No es
"Conformity": ese nombre apareció en el deep research y no está en las fuentes.

### 5.2 Correspondencia con nuestras etiquetas

Asignación del equipo, no de las fuentes. Solo filas con cita cotejada.

| Etiqueta | Principio | Fuente | Solidez |
|---|---|---|---|
| `AUTHORITY_CLAIM` | *Authority (AUTH)* | Ferreira et al. (2015) | directa |
| `AUTHORITY_CLAIM` | *Social compliance* | Stajano y Wilson (2011), vía la figura de Ferreira et al. | indirecta: el nombre se leyó en Ferreira, no en Stajano |
| `URGENCY_PRESSURE` | *Time Principle* | Stajano y Wilson (2011) | directa |
| `THREAT_FEAR` | — | — | **sin respaldo verificado** |
| `ISOLATION_SECRECY` | — | — | **sin respaldo verificado** (ver §5.4) |
| `TRUST_BUILDING` | — | — | **sin respaldo verificado** |
| `PERSISTENCE_DISTRACTION` | — | — | **sin respaldo verificado** |

Pendiente de leer, en este orden: Jones, K. S., Armstrong, M. E., Tornblad, M. K. y Siami Namin, A.
(2021), *How social engineers use persuasion principles during vishing attacks*, *Information and
Computer Security* 29(2) — es el único sobre vishing y el que más puede aportar; el resto de la
lista de principios de Stajano y Wilson (cubriría `PERSISTENCE_DISTRACTION`); la definición de
*Distraction* y *Liking, Similarity & Deception* de Ferreira et al. (cubriría `TRUST_BUILDING`);
y Cialdini para `THREAT_FEAR` (aversión a la pérdida).

### 5.3 Fuentes descartadas del deep research

Un deep research del 2026-09-25 devolvió siete fuentes. Al cotejarlas:

| Fuente propuesta | Resultado del cotejo |
|---|---|
| Rodríguez-Gómez, H. D. y Cárdenas-Sánchez, F. (2021), *Revista Criminalidad* 63(2) | **No se encontró.** No aparece en búsquedas y el informe no daba enlace. Se descarta |
| Luong, H. T. y Nguyen, T. (2024), *Trends in Organized Crime* | **No se encontró** con ese título y esos autores. Se descarta |
| Miramirkhani, N., Starov, O. y Nikiforakis, N. (2017), *Dial One for Scam*, NDSS | **El paper existe**, pero las frases que el informe le atribuía (*"stay on the line"*, *"tier-2"*) no aparecen en el texto. Las citas se descartan; el paper puede volver si alguien lo lee de verdad |
| Citas atribuidas a Stajano y Wilson | **No coinciden con el texto.** El informe daba _"When you are under pressure to make a decision, you sacrifice full and proper assessment, reasoning and rationality"_; el original dice otra cosa (§5.1). Paráfrasis presentada como cita literal |
| Nombre *Conformity Principle* | **Incorrecto**: es *Social compliance* |
| Números de página de todas las fuentes | Sin verificar; al menos los de Ferreira et al. no pueden salir del PDF abierto, que no los tiene |

Las tres fuentes que el informe marcaba como respaldo "directo" de las seis etiquetas son
justamente las dos inexistentes y la que no dice lo que se le atribuía. **Lección metodológica:**
cuando un deep research devuelve exactamente lo que se le pidió encontrar, ese es el motivo para
desconfiar, no para celebrar.

### 5.4 Hallazgo: `ISOLATION_SECRECY` no está en las taxonomías clásicas

Ni Ferreira et al. (2015) ni la lista de Stajano y Wilson (2011) incluyen el aislamiento de la
víctima o la imposición de secreto como principio de persuasión. Es coherente: esas taxonomías se
construyeron sobre estafas presenciales y phishing por correo, donde no existe un canal abierto que
el atacante deba monopolizar. La orden de no cortar solo tiene sentido operativo por teléfono.

> **Estado: propuesta sin discutir.** Si se confirma al leer Jones et al. (2021), `ISOLATION_SECRECY`
> quedaría como una etiqueta que **no** se hereda de la literatura de persuasión sino del canal, y
> su respaldo serían las fuentes de vishing: el informe anual 2024 de la UFECI y la Policía de la
> Ciudad, que describe que los delincuentes "intentarán todo el tiempo tener el control de la
> comunicación" (§6.1 y §6.2). Eso es defendible y además es una contribución, pero hay que
> **decirlo**, no disimularlo con una cita forzada.

## 6. Huecos conocidos

| Hueco | Por qué importa | Estado |
|---|---|---|
| UFECI (ciberdelincuencia) | El issue la pide; el catálogo cita UFECRI (criminal compleja), que es otra unidad | Resuelto (§6.1): cotejada e incorporada al catálogo |
| Policía Federal / Policía de la Ciudad | El issue las pide; podrían respaldar la modalidad policial descartada | Policía de la Ciudad revisada (§6.2); Policía Federal pendiente |
| Circulares o comunicaciones del BCRA | Solo se citan páginas de prevención, no normativa | PENDIENTE |
| Compras en Marketplace | El issue la menciona; no hay semilla ni fuente | PENDIENTE |
| Secuestro virtual | El issue la menciona; solo está cubierto en parte por "familiar en apuros" | Documentado (§6.2); falta decidir si entra al catálogo |
| Llamada policial o judicial | Semilla descartada por falta de fuente | Sin fuente tras revisar UFECI, Policía de la Ciudad y Min. Seguridad; falta Policía Federal |

### 6.1 Fuentes de la UFECI

Abiertas, extraídas y cotejadas literalmente por Corchets el 2026-09-25 (frase y página).

| Fuente | Publicación | ¿Por llamada? | Suplanta a | Pide | Presión | Página |
|---|---|---|---|---|---|---|
| [Informe anual 2024](https://www.mpf.gob.ar/ufeci/files/2025/06/UFECI_informe_anual_2024-1.pdf) | junio 2025 | sí | bancos, billeteras digitales, tarjetas, empresas de servicios; soporte de WhatsApp | acceso remoto (vía link); código de WhatsApp | excusa de autorizar una compra o verificación de seguridad | 18, 19, 24 |
| [Capacitación UFECI–WhatsApp](https://www.fiscales.gob.ar/ciberdelincuencia/la-ufeci-y-whatsapp-capacitaron-a-personal-judicial-y-del-mpf-frente-a-las-maniobras-fraudulentas-para-tomar-control-de-las-cuentas-de-mensajeria/) | 2021-11-24 | sí, y también mensajes | centro de vacunación; amigo o familiar | código de WhatsApp o captura de la verificación | familiar "con alguna urgencia" | web |
| [Informe de pandemia](https://www.mpf.gob.ar/ufeci/files/2021/09/UFECI_informe-pandemia.pdf) | septiembre 2021 (datos 2020) | sí (275 casos de vishing, p. 17) | bancos / homebanking; ANSES y programas de ayuda | credenciales de homebanking; luego transferencias | no dice | 16–18 |
| [Alerta de obtención de datos bajo engaño](https://www.fiscales.gob.ar/fiscalias/ufeci-alerta-sobre-una-nueva-campana-de-obtencion-de-datos-personales-bajo-engano/) | 2019-12-13 | **no** (WhatsApp + sitio web) | Ministerio de Trabajo | edad y teléfono | no dice | web |

Frases cotejadas:

- Informe 2024: _"las víctimas reciben llamados de supuestos representantes de bancos, billeteras
  digitales, administradoras de tarjetas de crédito o empresas de servicios, usualmente con la
  excusa de autorizar una compra o realizar una verificación de seguridad. Luego, [...] envían
  links a las víctimas, logrando instalar algún software de acceso remoto"_.
- Informe 2024: _"las víctimas reciben llamados con diversas excusas (turnos por campañas de
  vacunación, beneficios de algún organismo oficial, premios o descuentos de una empresa privada y
  del supuesto servicio técnico de la misma aplicación de WhatsApp, etc.). Luego le solicitan a la
  víctima que remita un código desde su teléfono"_.
- Capacitación 2021: _"Un ardid frecuente para convencer a las personas a entregar el código son
  llamados falsos para confirmar turnos en centros de vacunación contra la Covid-19. [...] o
  incluso simulaciones en las que el estafador se hace pasar por algún amigo o familiar con alguna
  urgencia"_.

**Qué cambia en la tipología:**

| Hallazgo | Efecto |
|---|---|
| El informe 2024 describe acceso remoto pedido en una llamada de falso banco o empresa | Segunda fuente oficial para `REQUEST_REMOTE_ACCESS` (antes solo Banco Galicia). Refuerza `SC-SOPORTE-REMOTO-01` |
| El informe 2024 y la capacitación 2021 describen el pedido del código de WhatsApp por llamada | Refuerza `SC-WA-CODE-01` con fuente de la UFECI; la modalidad aparece en 2021 y en 2024 (persiste) |
| Las excusas del código incluyen beneficio de organismo, premio y soporte de WhatsApp | Un mismo pedido (`REQUEST_AUTH_CODE`) con varios pretextos: el pretexto no define la modalidad, el pedido sí |
| El informe de pandemia describe credenciales de homebanking seguidas de transferencia | Apoya `REQUEST_SECRET` → `REQUEST_TRANSFER` como secuencia; persistencia desde 2020 |
| La alerta de 2019 no es por llamada | Queda fuera de la tipología (criterio de §2) |
| El informe 2024 menciona PFA, AFIP/ARCA y Correo Argentino suplantados con falsas multas o citaciones, pero **por correo electrónico** | **No** recupera `SC-POLICIA-RESGUARDO-01`: sigue faltando una fuente de falso policía **por teléfono** |

**Cifra:** el informe de pandemia registra **275 casos** de phishing telefónico o vishing (p. 17).
Es una cantidad de casos reportados a la UFECI en el período del informe, no una medida de
prevalencia. El porcentaje atribuido por prensa al informe 2024 sigue sin usarse.

### 6.2 Policía de la Ciudad y Ministerio de Seguridad

Abiertas por Corchets el 2026-09-25. La extracción agrupa las tres fuentes; la única frase literal
registrada es _"intentarán todo el tiempo tener el control de la comunicación"_ (Policía de la
Ciudad). Antes de citar una fuente en particular en el informe, anotar qué frase sale de cuál.

| Fuente | Publicación | ¿Por llamada? |
|---|---|---|
| [Consejos de protección de la Policía de la Ciudad ante estafas telefónicas](https://buenosaires.gob.ar/noticias/consejos-de-proteccion-de-la-policia-de-la-ciudad-ante-estafas-telefonicas) | 2020-10-08 | sí |
| [Consejos para evitar estafas virtuales y telefónicas](https://buenosaires.gob.ar/gcaba_historico/seguridad/consejos-para-evitar-estafas-virtuales-y-telefonicas) (GCBA, archivo histórico) | sin fecha visible | sí |
| [Seguridad y fiscales evaluaron medidas contra los "secuestros virtuales"](https://www.argentina.gob.ar/noticias/gseguridad-y-fiscales-evaluaron-medidas-contra-fraudes-conocidos-popularmente-como-%E2%80%9Csecuestros) (Min. Seguridad) | 2014-06-23 | sí |

**Secuestro virtual, según las tres fuentes:**

- Quien llama se hace pasar por un hijo, nieto o familiar cercano, a veces distorsionando la voz.
  No hay secuestrado real: es una simulación.
- Piden dinero o joyas como rescate, o los ahorros guardados en el domicilio.
- Presión: los delincuentes buscan tener el control de la comunicación. Las recomendaciones insisten
  en cortar y verificar con el familiar o el 911. Ninguna cita una frase textual del tipo "no cortes".

**Falso policía o fiscal:** ninguna de las tres lo menciona. La única mención a fiscales es la
reunión institucional entre el Ministerio y la Procuración.

**Codificación candidata** (asignación del equipo, no de la fuente):
`TRUST_BUILDING` (se hace pasar por familiar), `THREAT_FEAR` (secuestro), `ISOLATION_SECRECY`
(control de la comunicación) → `REQUEST_TRANSFER`. La urgencia no aparece explícita en lo extraído.

**Antigüedad:** las tres son de 2014 a 2020 (una sin fecha). Muestran que la modalidad está
documentada hace años, no que siga vigente. Para vigencia hace falta una fuente de 2024 o posterior.

## 7. Aporte a D07

> **Estado: propuesta sin discutir.** Insumo para
> [D07](../gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico); la decisión es
> del equipo.

Con lo relevado hasta acá, las modalidades argentinas (código de WhatsApp, beneficio de ANSES,
falso soporte, canje de billetes) se describen como **combinaciones** de las 6+6 etiquetas: ninguna
necesitó una etiqueta nueva para codificarse. Eso sugiere tratarlas como instancias, no como
etiquetas, pero dos puntos quedan abiertos:

- `REQUEST_TRANSFER` agrupa transferencia y entrega de efectivo (canje de billetes). Hay que decidir
  si la entrega presencial se distingue.
- El secuestro virtual (§6.2) entra en las 6+6 salvo por un detalle: se piden **joyas**, y la
  definición de `REQUEST_TRANSFER` habla de mover dinero o entregar efectivo. Decidir si la entrega
  de bienes de valor entra en esa etiqueta.
- Si §6 agrega Marketplace, hay que volver a verificar que entre en las 6+6.

## 8. Terminado cuando

- [ ] §5 tiene una fuente verificada por fila (hoy: 2 de 6 etiquetas con respaldo cotejado).
- [ ] Leído Jones et al. (2021), el único trabajo sobre vishing de la lista.
- [ ] §6 sin PENDIENTE, o con el motivo por el que el hueco queda abierto.
- [ ] Búsquedas nuevas registradas en el [protocolo](PROTOCOLO-REVISION.md#registro-de-búsquedas).
- [ ] Filas nuevas del catálogo con fuente y fecha de consulta.
- [ ] Revisión cruzada por otra persona del equipo (familia "Dominio, escenarios argentinos y ética").
