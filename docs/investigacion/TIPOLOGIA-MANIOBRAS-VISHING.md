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
| Verificación falsa de WhatsApp | soporte o conocido | código de activación de la cuenta | `REQUEST_AUTH_CODE` | Min. Seguridad — `SC-WA-CODE-01` |
| Falso soporte que pide la clave | mesa de ayuda | usuario y contraseña | `REQUEST_SECRET` | BCRA — `SC-SOPORTE-CLAVE-01` |
| Beneficio previsional falso | ANSES / organismo previsional | datos personales | `REQUEST_PERSONAL_DATA` | ANSES, UFECRI-MPF — `SC-ORG-BENEFICIO-01` |
| Premio o sorteo | empresa u organizador | datos de cuenta o tarjeta | `REQUEST_PERSONAL_DATA` | BCRA, Min. Seguridad — `SC-PREMIO-01` |
| Cambio de clave por teléfono | banco u organismo público | que la persona cambie o entregue la clave | `REQUEST_SECURITY_ACTION` | Min. Seguridad — `SC-CLAVE-CAMBIO-01` |
| Familiar en apuros | familiar | dinero | `REQUEST_TRANSFER` | UFECRI-MPF — `SC-FAMILIAR-DINERO-01` |
| Canje de billetes | entidad bancaria | efectivo o transferencia | `REQUEST_TRANSFER` | UFECRI-MPF — `SC-BANK-BILLETES-01` |
| Pantalla compartida | banco, empresa de servicios o soporte | acceso al dispositivo | `REQUEST_REMOTE_ACCESS` | Banco Galicia — `SC-SOPORTE-REMOTO-01` |

**Descartada por falta de fuente:** _resguardo de fondos por causa judicial_ (policía o fiscalía,
`SC-POLICIA-RESGUARDO-01`). La propuso el modelo; UFECRI enumera familiar, entidad bancaria y
empleado público, no policía. Vuelve si esta investigación encuentra una fuente (ver §6).

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
- `REQUEST_REMOTE_ACCESS` y `REQUEST_SECURITY_ACTION` tienen una sola semilla cada una.

## 5. Fundamento en la literatura de ingeniería social

> **PENDIENTE.** Sin fuentes verificadas todavía. No completar con citas del
> [deep research](deep-research-report-00.md) (sus marcadores no son referencias).

Tabla a llenar: cada maniobra de la capa 1 con el mecanismo psicológico que la explica y **una
fuente que alguien del equipo abrió** (DOI, autores, año copiados de la fuente).

| Etiqueta | Mecanismo candidato | Fuente verificada |
|---|---|---|
| `AUTHORITY_CLAIM` | obediencia a la autoridad | PENDIENTE |
| `URGENCY_PRESSURE` | escasez de tiempo / decisión bajo presión | PENDIENTE |
| `THREAT_FEAR` | apelación al miedo / aversión a la pérdida | PENDIENTE |
| `ISOLATION_SECRECY` | aislamiento de la víctima de sus fuentes de verificación | PENDIENTE |
| `TRUST_BUILDING` | construcción de credibilidad / pretexting | PENDIENTE |
| `PERSISTENCE_DISTRACTION` | sobrecarga cognitiva / compromiso escalonado | PENDIENTE |

## 6. Huecos conocidos

| Hueco | Por qué importa | Estado |
|---|---|---|
| UFECI (ciberdelincuencia) | El issue la pide; el catálogo cita UFECRI (criminal compleja), que es otra unidad | En curso: cuatro fuentes con canal telefónico confirmado (§6.1) |
| Policía Federal / Policía de la Ciudad | El issue las pide; podrían respaldar la modalidad policial descartada | PENDIENTE |
| Circulares o comunicaciones del BCRA | Solo se citan páginas de prevención, no normativa | PENDIENTE |
| Compras en Marketplace | El issue la menciona; no hay semilla ni fuente | PENDIENTE |
| Secuestro virtual | El issue la menciona; solo está cubierto en parte por "familiar en apuros" | PENDIENTE |
| Llamada policial o judicial | Semilla descartada por falta de fuente | PENDIENTE |

### 6.1 Fuentes de la UFECI en revisión

Abiertas por Corchets el 2026-09-25: las cuatro mencionan la llamada telefónica como canal. Todavía
**no** se extrajo qué entidad suplantan ni qué piden, así que no se usan para §3 ni para el
catálogo hasta completar esas columnas con la frase y la página de la fuente.

| Fuente | Publicación | Canal telefónico | Suplanta a | Pide | Página / frase |
|---|---|---|---|---|---|
| [Informe anual 2024](https://www.mpf.gob.ar/ufeci/files/2025/06/UFECI_informe_anual_2024-1.pdf) | 2025-06 (según URL) | sí | PENDIENTE | PENDIENTE | PENDIENTE |
| [Capacitación UFECI–WhatsApp](https://www.fiscales.gob.ar/ciberdelincuencia/la-ufeci-y-whatsapp-capacitaron-a-personal-judicial-y-del-mpf-frente-a-las-maniobras-fraudulentas-para-tomar-control-de-las-cuentas-de-mensajeria/) | PENDIENTE | sí | PENDIENTE | PENDIENTE | PENDIENTE |
| [Alerta de obtención de datos bajo engaño](https://www.fiscales.gob.ar/fiscalias/ufeci-alerta-sobre-una-nueva-campana-de-obtencion-de-datos-personales-bajo-engano/) | PENDIENTE | sí | PENDIENTE | PENDIENTE | PENDIENTE |
| [Informe de pandemia](https://www.mpf.gob.ar/ufeci/files/2021/09/UFECI_informe-pandemia.pdf) | 2021-09, datos de 2020 | sí | PENDIENTE | PENDIENTE | PENDIENTE |

El informe de pandemia no describe el presente: sirve para mostrar que una modalidad **persiste**
desde 2020 si también aparece en el informe 2024, no como evidencia independiente de su vigencia.

**Cifra no usada:** notas de prensa atribuyen a la UFECI un porcentaje de vishing sobre el total
de reportes. No entra hasta verlo en el informe con su página y cómo se calculó.

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
- Si §6 agrega secuestro virtual o Marketplace, hay que volver a verificar que entren en las 6+6.

## 8. Terminado cuando

- [ ] §5 tiene una fuente verificada por fila.
- [ ] §6 sin PENDIENTE, o con el motivo por el que el hueco queda abierto.
- [ ] Búsquedas nuevas registradas en el [protocolo](PROTOCOLO-REVISION.md#registro-de-búsquedas).
- [ ] Filas nuevas del catálogo con fuente y fecha de consulta.
- [ ] Revisión cruzada por otra persona del equipo (familia "Dominio, escenarios argentinos y ética").
