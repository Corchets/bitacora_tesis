# Manual de anotación

> **Estado: propuesta sin discutir.** La taxonomía deriva del
> [deep research](../investigacion/deep-research-report-00.md), no de un relevamiento propio. Se congela al cerrar
> [D07](../gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico).

Protocolo que siguen los anotadores. Las secciones 1 y 2 son la propuesta de etiquetas; la sección 4
es el esqueleto que se completa **después** del piloto, cuando aparezcan las ambigüedades reales.

## 1. Principio de diseño

**No hacer 30 etiquetas.** En cuatro meses las clases raras destruyen el análisis estadístico: si una
etiqueta aparece cuatro veces en todo el corpus, no se puede reportar nada sobre ella.

La propuesta son **dos capas multi-label** de ~6 etiquetas cada una. Un turno puede tener varias
etiquetas de ambas capas, o ninguna.

### Capa 1 — Técnicas de manipulación

| Etiqueta | Qué la dispara | Qué **no** la dispara |
|---|---|---|
| `AUTHORITY_CLAIM` | Quien llama se presenta como una entidad o persona con autoridad o confianza: un banco, un organismo, un soporte técnico, un familiar | Que la persona *suponga* con quién habla. La etiqueta necesita que el llamante lo afirme |
| `URGENCY_PRESSURE` | Impone tiempo, rapidez o consecuencias por demorar: "tenés dos minutos", "si cortás se bloquea" | Que el tema sea urgente en sí mismo. Lo que se anota es la presión que ejerce el llamante, no la gravedad del asunto |
| `THREAT_FEAR` | Plantea pérdida, bloqueo, delito, sanción o peligro dirigidos a la persona | Informar un hecho negativo sin atribuirle consecuencias a la persona ("se registró una compra") |
| `ISOLATION_SECRECY` | Pide no cortar, no consultar, no hablar con terceros, o desalienta verificar por otro canal | Pedir silencio por ruido o pedir que no se interrumpa para poder explicar |
| `TRUST_BUILDING` | Usa datos, procedimientos o jerga para parecer legítimo: menciona el DNI, dice un número de trámite, recita pasos | El solo hecho de ser legítimo. Un banco real que dice su nombre no construye confianza artificialmente |
| `PERSISTENCE_DISTRACTION` | Insiste tras una objeción, redirige la duda o mantiene a la persona cognitivamente ocupada | Repreguntar una vez porque no se escuchó |

> **Aprobación parcial para el catálogo v0 (Mateo, 2026-09-23):** esta capa tenía la etiqueta
> `IMPERSONATION_AUTHORITY`. Los negativos muestran por qué era equívoca: una entidad legítima no
> suplanta a nadie, pero puede presentarse como autoridad. `AUTHORITY_CLAIM` nombra esa señal
> observable sin presuponer fraude. El cambio queda adoptado como etiqueta de trabajo del catálogo;
> la taxonomía completa y el marcado temporal siguen abiertos en
> [D07](../gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico).

Se corresponden con las maniobras permitidas que el
[método de creación del corpus](METODO-CREACION-CORPUS.md) declara en cada semilla fraudulenta.

### Capa 2 — Acciones solicitadas

Más directamente protectoras: son las que definen el momento crítico y marcan `T_R`.

| Etiqueta | Qué la dispara (ejemplos) | Qué **no** la dispara |
|---|---|---|
| `REQUEST_AUTH_CODE` | Pide un código de un solo uso: OTP, token, código de WhatsApp | Mencionar que un código existe o que va a llegar, sin pedir que se lo dicte |
| `REQUEST_SECRET` | Pide una credencial permanente: clave, PIN, CVV, contraseña, usuario | Pedir confirmar datos que la entidad ya tiene, como los últimos cuatro dígitos |
| `REQUEST_PERSONAL_DATA` | Pide datos identificatorios: DNI, CUIL, domicilio, o una foto de identificación | Que la persona los diga por su cuenta sin que se los pidan |
| `REQUEST_TRANSFER` | Pide mover dinero: transferencia, pago, cripto, entrega de efectivo, operar un cajero | Hablar de un movimiento de dinero ya ocurrido |
| `REQUEST_REMOTE_ACCESS` | Pide instalar acceso remoto o compartir pantalla | Pedir que se abra una app para mirar algo uno mismo |
| `REQUEST_SECURITY_ACTION` | Pide ejecutar una acción de seguridad: abrir un enlace, cambiar una clave, autorizar un dispositivo | Recomendar cambiar la clave por el canal oficial, que es conducta segura |

Las definiciones de "qué no la dispara" son una **primera pasada**. El esqueleto de la sección 4
pide completarlas con dos ejemplos positivos y dos negativos por etiqueta **después** del piloto,
cuando aparezcan las ambigüedades reales.

### Por qué estas etiquetas y no las de Cialdini

La literatura de persuasión (autoridad, escasez, prueba social) fundamenta **conceptualmente** la
capa 1, pero copiarla literalmente como etiqueta del detector es un error: "autoridad" es útil;
"está pidiendo tu código de verificación mientras te presiona para que no cortes" es mucho más útil
para una persona que está siendo estafada.

Las etiquetas están diseñadas para que **el sistema pueda explicarlas al usuario**, no para
clasificar académicamente la persuasión.

## 2. Formato de anotación por turno

```json
{
  "call_id": "SCAM_BANK_037",
  "turn_id": 11,
  "speaker": "attacker",
  "start_ms": 70200,
  "end_ms": 75400,
  "text": "No cortes porque se bloquea el procedimiento. Decime el código de seis dígitos.",
  "labels": ["URGENCY_PRESSURE", "ISOLATION_SECRECY", "REQUEST_AUTH_CODE"],
  "critical_request": true
}
```

El esquema definitivo de estos campos vive en `ESQUEMA-DATASET.md` cuando se cree.

## 3. Lo que ya conviene tener claro

**El equipo entero anota el piloto.** Si las cuatro personas anotan los mismos 12–20 diálogos al
principio, aparecen rápido las frases ambiguas y las definiciones defectuosas. Después se anota por
duplicado una fracción del corpus y se adjudican las discrepancias. Esto ya está previsto en el
paso 3 del piloto del [método de creación del corpus](METODO-CREACION-CORPUS.md#6-piloto).

**El acuerdo entre anotadores no es un trámite.** El plan de trabajo exige validar la
taxonomía "mediante acuerdo entre anotadores independientes". Si el kappa da bajo, la conclusión no
es maquillar el número: es que la taxonomía está mal definida y hay que arreglarla.

## 4. Esqueleto a completar después del piloto

1. **Unidad de anotación** — ¿el turno conversacional? ¿cómo se define un turno cuando hay
   solapamiento?
2. **Reglas por etiqueta** — para cada una: qué la dispara, qué NO la dispara, dos ejemplos
   positivos y dos negativos. Los negativos son los que evitan el desacuerdo.
3. **Casos límite** — un banco real que pide verificar identidad, una urgencia genuina, una llamada
   legítima que menciona un código. Son exactamente los negativos difíciles del corpus.
4. **Marcado temporal** — cómo se determinan `T_R` y `T_C` con precisión de milisegundos y qué hacer
   si el pedido se extiende varios turnos. Ver [métricas](../evaluacion/METRICAS.md).
5. **Métrica de acuerdo** — ¿Kappa de Cohen (dos anotadores) o Fleiss (más de dos)? Multi-label
   complica el cálculo: hay que decidir si se mide por etiqueta o global.
6. **Umbral aceptable** — fijarlo **antes** de medir.
7. **Procedimiento de adjudicación** — quién resuelve las discrepancias y cómo se registra.
8. **Herramienta** — ¿Label Studio, ELAN, planilla? Condiciona el formato de salida.

## 5. Preguntas abiertas para el equipo

- ¿Adoptamos las 6+6 tal cual, o las derivamos de un relevamiento propio de modalidades argentinas
  (UFECI, ANSES, PAMI, BCRA, prensa)? **Primer dato empírico (2026-09-17):** el relevamiento del
  [catálogo](CATALOGO-ESCENARIOS.csv) sobre fuentes oficiales no identificó una modalidad que
  documente `REQUEST_REMOTE_ACCESS` por teléfono. La alerta de Banco Galicia sí describe la
  pantalla compartida en una llamada; Mateo aprobó el 2026-09-23 usarla como fuente de una entidad
  financiera regulada. El 2026-09-25 se sumó una segunda fuente oficial: el informe anual 2024 de la
  UFECI describe llamados de falsos bancos o empresas que terminan instalando acceso remoto
  ([tipología §6.1](../investigacion/TIPOLOGIA-MANIOBRAS-VISHING.md#61-fuentes-de-la-ufeci)). La
  etiqueta sigue con **una sola semilla en el catálogo**: conviene mirarla de nuevo al cerrar D07.
- Las modalidades argentinas concretas — código de WhatsApp, "premio de ANSES", falso soporte de
  billetera virtual — ¿son etiquetas nuevas o instancias de las existentes?
- ¿Quién valida la taxonomía además del equipo? Evaluar si se consulta a personal con experiencia
  en prevención de fraude institucional o bancario.
