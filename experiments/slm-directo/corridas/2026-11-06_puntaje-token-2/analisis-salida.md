# #143, segunda vuelta: alcance, prompt C, v4-L y token al final — análisis offline

## Líneas base JSON

Primer aviso (`alerta_sugerida`), como corrieron. Tiene que reproducir la tabla de referencia de #143.

| corpus_v2 | estafas | antes/en/después de T_R | L_R mediana / media / ≥ 3 | falsas alarmas | FA por tipo |
|---|---|---|---|---|---|
| v1 solo (2026-11-04, a) | 28/46 | 13/11/3 (de 36) | 0 / 2.4 / 9 | 4/51 | cotidiana 1, mencion_sin_pedido 1, pedido_razonable 2 |
| v1 + Tito sin indicio (2026-11-04, b) | 27/46 | 12/10/4 (de 36) | 0 / 2.1 / 8 | 4/51 | cotidiana 1, mencion_sin_pedido 1, pedido_razonable 2 |
| v1 solo, repetición (2026-11-04, c) | 27/46 | 12/11/3 (de 36) | 0 / 2.3 / 8 | 4/51 | cotidiana 1, mencion_sin_pedido 1, pedido_razonable 2 |
| v4 solo (2026-11-05, b) | 28/46 | 9/16/2 (de 36) | 0 / 1.9 / 7 | 6/51 | mencion_sin_pedido 2, pedido_razonable 4 |
| v4 + Tito sin indicio (tanda de roles, d) | 27/46 | 7/17/2 (de 36) | 0 / 1.3 / 5 | 6/51 | mencion_sin_pedido 2, pedido_razonable 4 |

La tabla de referencia se reproduce: v1 solo 28/13/4, v1 + Tito 27/12/4, v4 solo 28/9/6.

Umbral sobre el riesgo escrito: avisa en la primera línea con riesgo ≥ u o `alerta_sugerida`. Las corridas operativas cortan en el aviso, así que esta regla está observada entera.

| corpus_v2 | riesgo | estafas | antes/en/después de T_R | L_R mediana / media / ≥ 3 | falsas alarmas | FA por tipo |
|---|---|---|---|---|---|---|
| v1 solo (2026-11-04, a) | ≥ 0.3 | 42/46 | 25/6/2 (de 36) | 5 / 7.1 / 19 | 21/51 | cotidiana 4, mencion_sin_pedido 7, pedido_razonable 10 |
| v1 solo (2026-11-04, a) | ≥ 0.4 | 30/46 | 14/11/4 (de 36) | 0 / 2.6 / 11 | 7/51 | cotidiana 1, mencion_sin_pedido 3, pedido_razonable 3 |
| v1 solo (2026-11-04, a) | ≥ 0.5 | 30/46 | 14/11/4 (de 36) | 0 / 2.6 / 11 | 7/51 | cotidiana 1, mencion_sin_pedido 3, pedido_razonable 3 |
| v1 + Tito sin indicio (2026-11-04, b) | ≥ 0.3 | 41/46 | 23/7/2 (de 36) | 2 / 4.4 / 15 | 16/51 | cotidiana 3, mencion_sin_pedido 5, pedido_razonable 8 |
| v1 + Tito sin indicio (2026-11-04, b) | ≥ 0.4 | 28/46 | 13/9/5 (de 36) | 0 / 2.3 / 10 | 6/51 | cotidiana 1, mencion_sin_pedido 2, pedido_razonable 3 |
| v1 + Tito sin indicio (2026-11-04, b) | ≥ 0.5 | 28/46 | 13/9/5 (de 36) | 0 / 2.2 / 10 | 6/51 | cotidiana 1, mencion_sin_pedido 2, pedido_razonable 3 |
| v1 solo, repetición (2026-11-04, c) | ≥ 0.3 | 42/46 | 25/6/2 (de 36) | 5 / 7.1 / 19 | 21/51 | cotidiana 3, mencion_sin_pedido 7, pedido_razonable 11 |
| v1 solo, repetición (2026-11-04, c) | ≥ 0.4 | 30/46 | 13/11/5 (de 36) | 0 / 2.3 / 10 | 7/51 | cotidiana 1, mencion_sin_pedido 3, pedido_razonable 3 |
| v1 solo, repetición (2026-11-04, c) | ≥ 0.5 | 30/46 | 13/11/5 (de 36) | 0 / 2.3 / 10 | 7/51 | cotidiana 1, mencion_sin_pedido 3, pedido_razonable 3 |
| v4 solo (2026-11-05, b) | ≥ 0.3 | 41/46 | 23/8/2 (de 36) | 8 / 7.2 / 19 | 21/51 | cotidiana 8, mencion_sin_pedido 3, pedido_razonable 10 |
| v4 solo (2026-11-05, b) | ≥ 0.4 | 29/46 | 11/15/2 (de 36) | 0 / 2.9 / 9 | 7/51 | mencion_sin_pedido 3, pedido_razonable 4 |
| v4 solo (2026-11-05, b) | ≥ 0.5 | 28/46 | 11/14/2 (de 36) | 0 / 2.5 / 9 | 7/51 | mencion_sin_pedido 3, pedido_razonable 4 |
| v4 + Tito sin indicio (tanda de roles, d) | ≥ 0.3 | 38/46 | 20/8/3 (de 36) | 2 / 4.3 / 14 | 14/51 | cotidiana 5, mencion_sin_pedido 2, pedido_razonable 7 |
| v4 + Tito sin indicio (tanda de roles, d) | ≥ 0.4 | 28/46 | 8/17/2 (de 36) | 0 / 1.8 / 7 | 6/51 | mencion_sin_pedido 2, pedido_razonable 4 |
| v4 + Tito sin indicio (tanda de roles, d) | ≥ 0.5 | 27/46 | 8/16/2 (de 36) | 0 / 1.7 / 7 | 6/51 | mencion_sin_pedido 2, pedido_razonable 4 |

Línea base de la regla de adopción: mejor punto JSON del SLM solo con falsas alarmas ≤ 7/51 en corpus_v2, por prompt. Como dato, también `alerta_sugerida` sola:

- v1: v1 solo (2026-11-04, a), riesgo ≥ 0.4 o alerta: 30/46 estafas, 14 antes del pedido, 7/51 FA (`alerta_sugerida` sola: 28/46, 13 antes, 4/51).
- v4: v4 solo (2026-11-05, b), riesgo ≥ 0.4 o alerta: 29/46 estafas, 11 antes del pedido, 7/51 FA (`alerta_sugerida` sola: 28/46, 9 antes, 6/51).

Activaciones de Tito viejo sin indicio: 128 de 150 casos (iguales con v1 y v4); Tito por línea antes de activar: mediana 111 ms.

## Alcance

| grupo | clase | casos | dentro | dudoso | fuera |
|---|---|---|---|---|---|
| corpus_v2 | vishing | 46 | 46 | 0 | 0 |
| corpus_v2 | legitima | 51 | 7 | 0 | 44 |
| laboratorio | vishing | 16 | 16 | 0 | 0 |
| laboratorio | legitima | 10 | 2 | 8 | 0 |
| piloto_escrito | vishing | 7 | 7 | 0 | 0 |
| piloto_escrito | legitima | 7 | 1 | 1 | 5 |
| trampa | vishing | 6 | 6 | 0 | 0 |
| trampa | legitima | 7 | 5 | 0 | 2 |

## Humo de formato

| prompt | masa ≥ 0,9 | masa mínima | respuesta limpia | resultado |
|---|---|---|---|---|
| `v4-lectura` | 48/48 | 1.0000 | 48/48 | PASA |
| `c-sino` | 48/48 | 1.0000 | 48/48 | PASA |
| `c-digito` | 48/48 | 0.9997 | 48/48 | PASA |

> Falta c-json/: se omite «C JSON».

> Falta c-sino/: se omite «C SÍ/NO».

> Falta c-sino-rep/: se omite «C SÍ/NO, repetición».

> Falta c-digito/: se omite «C dígito».

> Falta c-digito-rep/: se omite «C dígito, repetición».

## Control de las corridas

| corrida | líneas | inválidas | masa mínima | líneas con masa < 0,9 | ms SLM p50 / p95 | commit |
|---|---|---|---|---|---|---|
| v4-L | 2773 | 0 | 1.0000 | 0 | 237 / 326 | b9fd09ab23 |
| v4-L, repetición | 2773 | 2 | 0.0000 | 2 | 237 / 323 | b9fd09ab23 |

v4-L escribe el mismo riesgo que la línea base v4 en 2034 de 2225 líneas comparables. Si no coinciden casi todas, el pedido no es el mismo: revisar antes de concluir.

## Vista principal: todos los casos, como en la primera vuelta

corpus_v2 en esta vista: 46 estafas y 51 legítimas; FA permitidas: 7 (15 %).

| JSON | regla | estafas | antes/en/después de T_R | L_R mediana / media / ≥ 3 | falsas alarmas | FA por tipo |
|---|---|---|---|---|---|---|
| v4 JSON | alerta_sugerida | 28/46 | 9/16/2 (de 36) | 0 / 1.9 / 7 | 6/51 | mencion_sin_pedido 2, pedido_razonable 4 |
| v4 JSON | riesgo ≥ 0.3 o alerta | 41/46 | 23/8/2 (de 36) | 8 / 7.2 / 19 | 21/51 | cotidiana 8, mencion_sin_pedido 3, pedido_razonable 10 |
| v4 JSON | riesgo ≥ 0.4 o alerta | 29/46 | 11/15/2 (de 36) | 0 / 2.9 / 9 | 7/51 | mencion_sin_pedido 3, pedido_razonable 4 |
| v4 JSON | riesgo ≥ 0.5 o alerta | 28/46 | 11/14/2 (de 36) | 0 / 2.5 / 9 | 7/51 | mencion_sin_pedido 3, pedido_razonable 4 |

- v4 JSON: riesgo ≥ 0.4 o alerta: 29/46 estafas, 11 antes del pedido, 7/51 FA.

**Línea base de la regla de adopción: v4 JSON, riesgo ≥ 0.4 o alerta (29/46 estafas, 11 antes del pedido, 7/51 FA).**

Curva completa de esta vista en `curva.csv`.

### Mejor punto por política con FA ≤ 7

| corrida | compuerta | política | papel | umbral (rango empatado) | estafas | antes/en/después de T_R | L_R mediana / media / ≥ 3 | falsas alarmas | FA por tipo |
|---|---|---|---|---|---|---|---|---|---|
| v4-L | SLM solo | umbral | regla | 0.4 (0.4–0.4) | 27/46 | 11/13/2 (de 36) | 0 / 2.8 / 9 | 7/51 | mencion_sin_pedido 3, pedido_razonable 4 |
| v4-L | SLM solo | dos seguidas | regla | 0.37 (0.35–0.38) | 25/46 | 10/2/12 (de 36) | -0.5 / 1.9 / 8 | 7/51 | mencion_sin_pedido 3, pedido_razonable 4 |
| v4-L | SLM solo | EMA α=0.5 | regla | 0.35 (0.35–0.35) | 27/46 | 11/13/2 (de 36) | 0 / 2.7 / 9 | 7/51 | mencion_sin_pedido 3, pedido_razonable 4 |
| v4-L | SLM solo | EMA α=0.3 | exploración | 0.32 (0.32–0.32) | 28/46 | 11/10/6 (de 36) | 0 / 2.2 / 9 | 7/51 | mencion_sin_pedido 3, pedido_razonable 4 |
| v4-L | SLM solo | EMA α=0.7 | exploración | 0.37 (0.37–0.37) | 27/46 | 12/12/2 (de 36) | 0 / 2.9 / 9 | 7/51 | mencion_sin_pedido 3, pedido_razonable 4 |
| v4-L | Tito→SLM | umbral | informativo | 0.33 (0.33–0.33) | 30/46 | 16/9/4 (de 36) | 1 / 2.5 / 9 | 7/51 | cotidiana 1, mencion_sin_pedido 2, pedido_razonable 4 |
| v4-L | Tito→SLM | dos seguidas | informativo | 0.31 (0.31–0.31) | 28/46 | 15/3/9 (de 36) | 1 / 1.7 / 9 | 7/51 | cotidiana 1, mencion_sin_pedido 2, pedido_razonable 4 |
| v4-L | Tito→SLM | EMA α=0.5 | informativo | 0.3 (0.3–0.3) | 27/46 | 14/8/4 (de 36) | 1 / 2.5 / 9 | 7/51 | cotidiana 1, mencion_sin_pedido 2, pedido_razonable 4 |
| v4-L | Tito→SLM | EMA α=0.3 | informativo | 0.27 (0.27–0.27) | 30/46 | 13/5/8 (de 36) | 0.5 / 1.9 / 9 | 7/51 | cotidiana 1, mencion_sin_pedido 2, pedido_razonable 4 |
| v4-L | Tito→SLM | EMA α=0.7 | informativo | 0.31 (0.31–0.31) | 28/46 | 16/8/3 (de 36) | 1 / 2.7 / 9 | 7/51 | cotidiana 1, mencion_sin_pedido 2, pedido_razonable 4 |
| v4-L, repetición | SLM solo | umbral | regla | 0.41 (0.41–0.41) | 26/46 | 11/12/2 (de 36) | 0 / 2.9 / 9 | 7/51 | mencion_sin_pedido 3, pedido_razonable 4 |
| v4-L, repetición | SLM solo | dos seguidas | regla | 0.34 (0.34–0.34) | 27/46 | 10/3/13 (de 36) | -0.5 / 1.9 / 9 | 7/51 | mencion_sin_pedido 3, pedido_razonable 4 |
| v4-L, repetición | SLM solo | EMA α=0.5 | regla | 0.37 (0.37–0.37) | 26/46 | 10/11/4 (de 36) | 0 / 2.4 / 9 | 7/51 | mencion_sin_pedido 3, pedido_razonable 4 |
| v4-L, repetición | SLM solo | EMA α=0.3 | exploración | 0.33 (0.33–0.33) | 25/46 | 11/9/4 (de 36) | 0 / 2.5 / 9 | 7/51 | mencion_sin_pedido 3, pedido_razonable 4 |
| v4-L, repetición | SLM solo | EMA α=0.7 | exploración | 0.39 (0.38–0.39) | 26/46 | 11/12/2 (de 36) | 0 / 2.8 / 9 | 7/51 | mencion_sin_pedido 3, pedido_razonable 4 |
| v4-L, repetición | Tito→SLM | umbral | informativo | 0.32 (0.32–0.32) | 30/46 | 17/8/4 (de 36) | 2 / 2.7 / 9 | 7/51 | cotidiana 1, mencion_sin_pedido 2, pedido_razonable 4 |
| v4-L, repetición | Tito→SLM | dos seguidas | informativo | 0.31 (0.3–0.31) | 28/46 | 15/3/9 (de 36) | 1 / 1.7 / 9 | 7/51 | cotidiana 1, mencion_sin_pedido 2, pedido_razonable 4 |
| v4-L, repetición | Tito→SLM | EMA α=0.5 | informativo | 0.29 (0.29–0.29) | 31/46 | 14/8/5 (de 36) | 1 / 2.4 / 10 | 7/51 | cotidiana 1, mencion_sin_pedido 2, pedido_razonable 4 |
| v4-L, repetición | Tito→SLM | EMA α=0.3 | informativo | 0.27 (0.27–0.27) | 30/46 | 13/5/8 (de 36) | 0.5 / 1.9 / 9 | 7/51 | cotidiana 1, mencion_sin_pedido 2, pedido_razonable 4 |
| v4-L, repetición | Tito→SLM | EMA α=0.7 | informativo | 0.31 (0.31–0.31) | 28/46 | 16/8/3 (de 36) | 1 / 2.7 / 9 | 7/51 | cotidiana 1, mencion_sin_pedido 2, pedido_razonable 4 |

### Punto elegido y regla de adopción

- **v4-L:** umbral, umbral 0.4 (empata entre 0.4 y 0.4): 27/46 estafas, 11 antes del pedido, 7/51 FA. Repetición en el mismo punto: 27/46 estafas, 11 antes del pedido, 8/51 FA.
  Contra la línea base (v4 JSON, riesgo ≥ 0.4 o alerta: 29/46): -2 estafas → dentro de ±2: decide la latencia (#141).
  Con el mismo prompt (v4 JSON, riesgo ≥ 0.4 o alerta: 29/46, 11 antes, 7/51): -2 estafas, +0 avisos antes del pedido (dato).

**Entre las de token que cuentan, la de más estafas es v4-L** (27/46 estafas, 11 antes del pedido, 7/51 FA). Ver la latencia arriba.

Estafas sin pedido de corpus_v2 (sin T_R) que avisa cada configuración, en su punto: v4 JSON (riesgo ≥ 0.4 o alerta) 1/10; v4-L 1/10.

## Dato: dentro del alcance (en corpus_v2 quedan casi solo estafas; no sirve para decidir)

corpus_v2 en esta vista: 46 estafas y 7 legítimas; FA permitidas: 1 (15 %).

| JSON | regla | estafas | antes/en/después de T_R | L_R mediana / media / ≥ 3 | falsas alarmas | FA por tipo |
|---|---|---|---|---|---|---|
| v4 JSON | alerta_sugerida | 28/46 | 9/16/2 (de 36) | 0 / 1.9 / 7 | 0/7 | – |
| v4 JSON | riesgo ≥ 0.3 o alerta | 41/46 | 23/8/2 (de 36) | 8 / 7.2 / 19 | 1/7 | cotidiana 1 |
| v4 JSON | riesgo ≥ 0.4 o alerta | 29/46 | 11/15/2 (de 36) | 0 / 2.9 / 9 | 0/7 | – |
| v4 JSON | riesgo ≥ 0.5 o alerta | 28/46 | 11/14/2 (de 36) | 0 / 2.5 / 9 | 0/7 | – |

- v4 JSON: riesgo ≥ 0.3 o alerta: 41/46 estafas, 23 antes del pedido, 1/7 FA.

**Línea base de la regla de adopción: v4 JSON, riesgo ≥ 0.3 o alerta (41/46 estafas, 23 antes del pedido, 1/7 FA).**

### Punto elegido y regla de adopción

- **v4-L:** dos seguidas, umbral 0.11 (empata entre 0.11 y 0.11): 46/46 estafas, 33 antes del pedido, 1/7 FA. Repetición en el mismo punto: 46/46 estafas, 33 antes del pedido, 1/7 FA.
  Contra la línea base (v4 JSON, riesgo ≥ 0.3 o alerta: 41/46): +5 estafas → se adopta, provisorio hasta la reserva (3 o más estafas más).
  Con el mismo prompt (v4 JSON, riesgo ≥ 0.3 o alerta: 41/46, 23 antes, 1/7): +5 estafas, +10 avisos antes del pedido (dato).

**Entre las de token que cuentan, la de más estafas es v4-L** (46/46 estafas, 33 antes del pedido, 1/7 FA). Ver la latencia arriba.

Estafas sin pedido de corpus_v2 (sin T_R) que avisa cada configuración, en su punto: v4 JSON (riesgo ≥ 0.3 o alerta) 8/10; v4-L 10/10.

## Aparte, solo para mirar (vista principal)

Las 6 estafas que piden un dato de identificación y las 6 legítimas en que v4 avisaba por un dato pedido en una llamada que inició la persona. «L» es la línea del primer aviso (– sin aviso, «fuera» si queda fuera del alcance).

| caso | clase | alcance | v4 JSON (riesgo ≥ 0.4 o alerta) | v4-L |
|---|---|---|---|---|
| CV2-D-V-ORGANISMO_PREVISIONAL-001 | vishing (T_R 12) | dentro | L12 | L12 |
| CV2-D-V-ORGANISMO_PREVISIONAL-002 | vishing (T_R 9) | dentro | L9 | L9 |
| CV2-D-V-ORGANISMO_PREVISIONAL-003 | vishing (T_R 11) | dentro | L13 | L13 |
| CV2-D-V-ORGANISMO_PREVISIONAL-004 | vishing (T_R 14) | dentro | L14 | – |
| CV2-D-V-PREMIO-001 | vishing (T_R 10) | dentro | L10 | L10 |
| CV2-D-V-PREMIO-003 | vishing (T_R 13) | dentro | – | – |
| CV2-D-L-BANCO-001 | legitima | fuera | fuera | fuera |
| CV2-D-L-BANCO-002 | legitima | fuera | fuera | fuera |
| CV2-D-L-BANCO-004 | legitima | fuera | fuera | fuera |
| CV2-D-L-BANCO-005 | legitima | fuera | fuera | fuera |
| CV2-D-L-BANCO-010 | legitima | fuera | fuera | fuera |
| TR-13-turno-medico-pide-dni | legitima_dificil | fuera | fuera | fuera |

Manuales en el punto elegido (vista principal):

| configuración | grupo | estafas | antes/en/después de T_R | L_R mediana / media / ≥ 3 | falsas alarmas | FA por tipo |
|---|---|---|---|---|---|---|
| v4 JSON (riesgo ≥ 0.4 o alerta) | laboratorio | 16/16 | 8/8/0 (de 16) | 1 / 1.1 / 1 | 6/10 | legitima_dificil 6 |
| v4 JSON (riesgo ≥ 0.4 o alerta) | piloto_escrito | 7/7 | 4/3/0 (de 7) | 1 / 2.1 / 2 | 3/7 | legitima_dificil 3 |
| v4 JSON (riesgo ≥ 0.4 o alerta) | trampa | 5/6 | 4/1/0 (de 5) | 2 / 2.0 / 2 | 5/7 | legitima_dificil 5 |
| v4-L | laboratorio | 16/16 | 8/8/0 (de 16) | 1 / 1.1 / 1 | 6/10 | legitima_dificil 6 |
| v4-L | piloto_escrito | 7/7 | 4/3/0 (de 7) | 1 / 2.1 / 2 | 3/7 | legitima_dificil 3 |
| v4-L | trampa | 5/6 | 4/1/0 (de 5) | 2 / 1.6 / 0 | 5/7 | legitima_dificil 5 |

## Controles de ventas y préstamos (solo para mirar)

| control | clase | alcance | qué prueba | v4 JSON (riesgo ≥ 0.4 o alerta) | v4-L (umbral, 0.4) |
|---|---|---|---|---|---|
| CTRL-L-VENTA-PORTABILIDAD | legitima_dificil | dentro | Venta telefónica de portabilidad que pide DNI, número de trámite, fecha de nacimiento, domicilio y correo, y anuncia un código por SMS que la persona carga sola, sin dictarlo. | L4 | L4 |
| CTRL-V-OPERADOR-SMS | vishing | dentro | Falso operador de telefonía que inventa un problema de titularidad, suma un descuento para jubilados y pide leer o reenviar el código del SMS para quedarse con el WhatsApp. | L6 | L6 |
| CTRL-L-BANCO-OFRECE-PRESTAMO | legitima_dificil | dentro | El banco llama con un préstamo preaprobado, confirma nombre y DNI y deja la aceptación en la app o el home banking, con acreditación a las 48 horas hábiles y sin pedir token ni claves. | L4 | L4 |
| CTRL-V-BANCO-PRESTAMO-TOKEN | vishing | dentro | Falso empleado del banco que ofrece un préstamo preaprobado con acreditación inmediata y, para «confirmarlo», pide generar el código del token y dictarlo. | L4 | L4 |
| CTRL-L-PIDE-PRESTAMO | legitima_dificil | fuera | La persona llama a su banco a pedir un préstamo y el operador le pide DNI, fecha de nacimiento, ingresos, empleador, domicilio y correo, pero deja la confirmación en el home banking y no pide códigos. | L3 | L3 |
| CTRL-V-PRESTAMO-REDES | vishing | fuera | La persona llama a un número de préstamos visto en redes, se lo aprueban al instante y le piden transferir por adelantado una comisión a una billetera virtual. | L5 | L5 |

