# Manual de anotación

> **Estado: propuesta sin discutir.** La taxonomía deriva del
> [deep research](../../deep-research-report.md), no de un relevamiento propio. Se congela al cerrar
> [D07](../gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico).

Protocolo que siguen los anotadores. Las secciones 1 y 2 son la propuesta de etiquetas; la sección 4
es el esqueleto que se completa **después** del piloto, cuando aparezcan las ambigüedades reales.

## 1. Principio de diseño

**No hacer 30 etiquetas.** En cuatro meses las clases raras destruyen el análisis estadístico: si una
etiqueta aparece cuatro veces en todo el corpus, no se puede reportar nada sobre ella.

La propuesta son **dos capas multi-label** de ~6 etiquetas cada una. Un turno puede tener varias
etiquetas de ambas capas, o ninguna.

### Capa 1 — Técnicas de manipulación

| Etiqueta | Qué debe observar el anotador |
|---|---|
| `IMPERSONATION_AUTHORITY` | Se presenta como entidad/persona con autoridad o confianza |
| `URGENCY_PRESSURE` | Impone tiempo, rapidez o consecuencias por demorar |
| `THREAT_FEAR` | Plantea pérdida, bloqueo, delito, sanción o peligro |
| `ISOLATION_SECRECY` | Pide no cortar, no consultar, no hablar con terceros |
| `TRUST_BUILDING` | Utiliza datos o procedimientos para parecer legítimo |
| `PERSISTENCE_DISTRACTION` | Insiste, redirige objeciones o mantiene al usuario cognitivamente ocupado |

Se corresponden con las maniobras permitidas que el
[método de creación del corpus](METODO-CREACION-CORPUS.md) declara en cada semilla fraudulenta.

### Capa 2 — Acciones solicitadas

Más directamente protectoras: son las que definen el momento crítico y marcan `T_R`.

| Etiqueta | Ejemplos |
|---|---|
| `REQUEST_AUTH_CODE` | OTP, token, código de WhatsApp |
| `REQUEST_SECRET` | clave, PIN, CVV, contraseña |
| `REQUEST_PERSONAL_DATA` | DNI, domicilio, identificación |
| `REQUEST_TRANSFER` | transferencia, pago, cripto, efectivo |
| `REQUEST_REMOTE_ACCESS` | instalar acceso remoto, compartir pantalla |
| `REQUEST_SECURITY_ACTION` | abrir enlace, cambiar configuración, autorizar dispositivo |

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

**El acuerdo entre anotadores no es un trámite.** El anteproyecto se compromete a validar la
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
  (UFECI, ANSES, PAMI, BCRA, prensa)?
- Las modalidades argentinas concretas — código de WhatsApp, "premio de ANSES", falso soporte de
  billetera virtual — ¿son etiquetas nuevas o instancias de las existentes?
- ¿Quién valida la taxonomía además del equipo? El anteproyecto menciona "personas con experiencia
  en prevención de fraude".
