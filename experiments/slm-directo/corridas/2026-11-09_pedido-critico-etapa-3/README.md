# #143, segunda vuelta, etapa 3: C con campo contra C sin alerta, una consulta por línea

> **Estado: propuesta sin discutir.** Desarrollo; la reserva no se corre. Preparada el 2026-11-09, sin correr. La regla
> de abajo está escrita antes de correr, en código en [`analizar.py`](analizar.py), con las decisiones de Mateo del
> 2026-11-09. El Colab está en
> [`colab/README-PUNTAJE-TOKEN.md` §6](../../colab/README-PUNTAJE-TOKEN.md#6-segunda-vuelta-etapa-3-tag-colab143-etapa-3).

## Qué pregunta

¿Un campo de pedido crítico en el JSON de C le suma avisos a C dentro del alcance, sin sumar más de 5 FA?

- **C** ([`tarea_c.txt`](../../prompts/tarea_c.txt)) se adoptó en la etapa 2, provisorio hasta la reserva: 36/46
  estafas, 17/36 avisos antes del pedido y 27/94 FA, con «riesgo ≥ 0,3 o alerta»
  ([análisis](../2026-11-07_alcance-etapa-2/analisis.md)).
- **Lo que más le falta:** 7 de sus 12 errores son pedidos explícitos de un código o una clave en contextos amables,
  donde escribe 0,1–0,2.
- **Las dos versiones** usan el mismo texto de tarea de C y una sola consulta por línea. Solo cambia el JSON:
  - **C sin alerta (la base):** pide solo el riesgo ([`salida_json_c_sin_alerta.txt`](../../prompts/salida_json_c_sin_alerta.txt)).
    En la etapa 2, las 110 alertas escritas de C tenían riesgo ≥ 0,6, así que con 0,3 no sumaban avisos;
  - **C con campo:** pide `pedido_critico` y después el riesgo
    ([`salida_json_c_con_campo.txt`](../../prompts/salida_json_c_con_campo.txt)). El riesgo se define igual en los
    tres JSON.
- **La lista sale de fuentes externas,** no de los fallos del corpus (ADR 0005, regla 7): ver [`FUENTES.md`](FUENTES.md).
- **Vista:** los 140 dentro del alcance ([`alcance-140`](../../casos/listas/alcance-140.txt)), con las 46 estafas de
  corpus_v2 (36 con pedido) y las 94 legítimas entrantes de #155.

## Decisiones de Mateo (2026-11-09), antes de escribir

1. **Va la etapa 3** (opción B de [`PROPUESTA-SIGUIENTE.md`](../2026-11-07_alcance-etapa-2/PROPUESTA-SIGUIENTE.md),
   §3.1), con C con campo contra C sin alerta. El plan llegó desde la sesión de la etapa 2, y Mateo lo confirmó acá.
   - Quedan afuera la pregunta de pedido crítico como consulta aparte, que duplica las consultas, y la lista como
     párrafo dentro de C.
2. **Definición de pedido crítico** (Mateo):
   - se define por el propósito, y la lista son ejemplos, no un límite;
   - quedan afuera el número de DNI, la fecha de nacimiento, el nombre y la dirección;
   - cuenta lo que PROTEGIDA da o hace porque OTRA la llevó a eso, diga quien diga la frase;
   - las advertencias no cuentan;
   - «entregar la tarjeta» es pasar sus números, no el plástico.

   Mateo aprobó el texto del campo:
   > "pedido_critico": true si OTRA ya está llevando a PROTEGIDA a dar o hacer algo que le permita a alguien sacarle
   > plata, tomar sus cuentas o hacerse pasar por ella; si no, false. Por ejemplo: dictar un código que le llegó, decir
   > una clave o un PIN, dar los datos completos de la tarjeta, mandar una foto del DNI o de su cara, transferir, pagar
   > o entregar plata o la tarjeta, instalar un programa o compartir la pantalla, seguir pasos en el cajero o en la app,
   > o cortar y llamar a otro número. Dar el número de DNI, la fecha de nacimiento, el nombre o la dirección no cuenta.
   > Cuenta también si la frase la dice PROTEGIDA porque OTRA la llevó a eso, como «¿te leo el código?». No cuentan las
   > advertencias, como «nunca te vamos a pedir el código».
3. **Dos señales:**
   - «cualquier aviso» decide: riesgo ≥ 0,3 en la base, y riesgo ≥ 0,3 o `pedido_critico` en C con campo;
   - la alerta fuerte (`pedido_critico`) se informa aparte;
   - la política del test se elige antes del test.
4. **Tope de FA:** C con campo puede sumar hasta 5 FA respecto de la base.
5. **Lectura:**
   - la regla usa todas las líneas;
   - «solo OTRA» se simula con las mismas salidas, y se adopta si no empeora ninguna cifra en más de 2, en las dos
     corridas.
6. **`alcance-91`:** si el resultado se invierte ahí, decide el equipo. Es una propuesta de la sesión del corpus.
7. **El primer aviso muestra un texto fijo** en la app, sin consultar nada más. El motivo propio de C
   ([`motivo_c_corte.txt`](../../prompts/motivo_c_corte.txt)) se pide solo en la primera alerta fuerte (`pedido_critico`
   en true), una vez por llamada. C sin alerta nunca lo pide. Texto aprobado:
   > Se va a avisar a PROTEGIDA que esta llamada puede ser una estafa. Respondé solo con un objeto JSON con estos campos,
   > en este orden:
   > - "evidencia": copiá textualmente la frase de OTRA que más muestra que puede ser una estafa.
   > - "motivo": una frase breve dirigida a la persona que diga por qué puede ser una estafa. Nombrá un pedido solo si
   >   ya ocurrió en la llamada.
8. **Política a simular, para el costo por llamada:**
   - solo las líneas de OTRA, si se confirma;
   - el aviso no se apaga;
   - el detector corta después de la alerta fuerte, que lleva el motivo.

## Configuraciones

| corrida | prompt | casos | papel |
|---|---|---|---|
| `c-sin-alerta` | C sin alerta | los 244 | base |
| `c-con-campo` | C con campo | los 244 | candidata |
| `c-sin-alerta-rep` | C sin alerta | los 140 | repetición (ADR 0005) |
| `c-con-campo-rep` | C con campo | los 140 | repetición |

Además, los 6 controles de ventas y préstamos con las dos, solo para mirar.

**Condiciones comunes:**
- todas corren en todas las líneas (`--seguir-tras-aviso`), con roles y `--sin-reglas`;
- Ollama 0.40.14, el digest `b37049369adf…`, `num_ctx` 4096, seed 42 y temperatura 0;
- el JSON es corto y el modelo lo cierra solo. `num_predict` 48 es solo un tope (`MAXIMO_TOKENS_C_CORTO`);
- llegar al tope cuenta como fallo.

## Humo de formato, antes de correr

En los 3 casos de siempre (48 líneas), en una sola corrida con `c-json-corte` (C como corrió en la etapa 2),
`c-sin-alerta` y `c-con-campo`.

**Pasa** la versión que lee el JSON en las 48 líneas sin llegar al tope.

Se informan, sin criterio, varios datos:
- los tokens generados;
- el riesgo contra el de `c-json-corte`;
- cuántas veces escribe `pedido_critico` en true;
- el motivo de las alertas fuertes.

**Si una versión no pasa:**
- la que no pasa no corre;
- si es la base, la base pasa a ser C de la etapa 2 (regla 1);
- si no pasa ninguna, no corre nada.

No se ajusta nada en esa sesión.

## Regla, escrita antes de correr

**Cifras,** dentro del alcance y en todas las líneas:
- estafas avisadas (/46);
- avisos antes del pedido (T_A < T_R, /36);
- avisos a tiempo, antes o en el pedido (T_A ≤ T_R, /36);
- FA (/94).

Las líneas inválidas no avisan.

1. **La base contra C de la etapa 2.**
   - Se compara C sin alerta («riesgo ≥ 0,3») con `c-json-corte` de la etapa 2 («riesgo ≥ 0,3 o alerta»).
   - Si alguna de las cuatro cifras se mueve más de ±2, la base pasa a ser el prompt de la etapa 2, cortado tras el
     riesgo. Se lee de `c-json-corte` y `c-json-corte-rep` con «riesgo ≥ 0,3», sin la alerta.
2. **C con campo contra la base, en «cualquier aviso».** Se adopta si cumple todo esto:
   - suma 3 o más en estafas, antes del pedido o a tiempo;
   - no pierde 3 o más en ninguna;
   - tiene FA ≤ FA(base) + 5;
   - su repetición, contra la repetición de la base, cumple lo mismo: +3 en una cifra en que ganó la primera corrida,
     sin perder 3 o más y con FA ≤ FA(base) + 5.

   Si gana en una cifra y pierde 3 o más en otra, en la corrida o en la repetición, decide el equipo. En cualquier otro
   caso, queda la base.
3. **`alcance-91`:** se aplica la regla 2 a las 46 estafas y a una legítima por escenario, sin dudosas. Si el resultado
   se invierte, decide el equipo.
4. **«Solo OTRA»:** se adopta para la configuración que queda si, en la corrida y en la repetición, ninguna cifra de
   detección baja más de 2 y las FA no suben más de 2, contra la lectura en todas las líneas.
   - Con las corridas de C de la etapa 2 da −1 estafa, −2 avisos antes del pedido y −3 FA, así que pasaría.

Lo que se adopta es provisorio hasta la reserva. La meta 80/15 no es criterio.

## Solo para mirar (no decide)

- **La alerta fuerte:**
  - estafas con pedido crítico en la referencia, avisadas a tiempo o tarde;
  - estafas sin pedido crítico;
  - legítimas, en los 140 y en `alcance-91`.
- las estafas sin pedido;
- la curva con u = 0,1…1,0, con las dos lecturas (`curva.csv`);
- los intervalos de Wilson;
- las estafas por primer pedido de la referencia, y los pares discordantes entre la base y C con campo;
- las FA:
  - por lote;
  - según el pedido de datos personales;
  - por escenario sin dudosas;
  - en L1–L3;
- otros grupos: corpus_v2 entero, los manuales y las reglas v1 y v2 del laboratorio;
- **la repetición de cada versión:** los casos con otra línea de aviso y cuántos mueven una cifra. Sirve para la
  lectura de «más de 2 casos» del ADR 0005, que fija la sesión principal;
- C sin alerta contra C de la etapa 2, línea por línea;
- **la latencia por tipo de consulta** (C y el motivo de la alerta fuerte), en todas las líneas y solo en las de OTRA,
  junto a la de la etapa 2;
- **el costo por llamada de la política:** consultas y ms, con las dos lecturas;
- los controles de ventas, con el primer aviso y la primera alerta fuerte.

**Motivo de C, con la medición escrita antes de correr.** En cada alerta fuerte en que se pidió el motivo, dentro del
alcance:
- JSON válido con motivo;
- la evidencia es una frase textual de OTRA hasta esa línea;
- la evidencia es textual en cualquier voz;
- el motivo nombra un pedido antes de que ocurra. Se marca cuando la referencia todavía no tiene un pedido crítico y el
  motivo usa alguna palabra de una lista fija (código, clave, tarjeta, transferencia, cajero, foto…). Los marcados se
  leen a mano.

## Duración

Alrededor de 1 h en T4:
- **`c-sin-alerta` sobre los 244 (4.325 líneas): unos 14 minutos.** C de la etapa 2 tardó 21,8, con 24 tokens por
  línea, y esta escribe unos 13;
- **`c-con-campo`: unos 20,** con unos 25 tokens;
- **las repeticiones sobre los 140 (2.621 líneas):** unos 9 y 12;
- **la instalación, la humo y los controles:** unos 8.

## Después de correr

1. Descomprimir cada ZIP en un directorio vacío nuevo, y correr todo Python con `-I`.
2. Verificar los ZIP con el procedimiento de [`2026-11-07_json-cortado/README.md`](../2026-11-07_json-cortado/README.md):
   - los parciales coinciden con el final;
   - el commit es el del tag, sin cambios sin commitear;
   - el sha256 de `colab/probar_etapa_3.py` y el digest coinciden;
   - la segunda consulta es `motivo_c_corte.txt`, y no hay casos de la reserva.
3. Copiar las carpetas acá y correr `python -I analizar.py`. Usa las corridas `c-json-corte/` y `c-json-corte-rep/`
   de la etapa 2, en `../2026-11-07_alcance-etapa-2/`, o en la carpeta que diga `--etapa-2`.

## Archivos

| Archivo | Qué es |
|---|---|
| [`analizar.py`](analizar.py) | La regla de arriba en código, escrita antes de correr. Tests en [`tests/test_etapa3_143.py`](../../tests/test_etapa3_143.py). |
| [`FUENTES.md`](FUENTES.md) | Fuentes externas de cada ejemplo de la definición, y de la exclusión del DNI. |
| [`alcance-91`](../../casos/listas/alcance-91.txt) y [`legitimas-escenarios-45`](../../casos/listas/legitimas-escenarios-45.txt) | La vista sin escenarios repetidos ni dudosas. Copiadas tal cual de la rama `corpus/escenarios-y-dudosas` (commit `45e3037`), donde están el manifiesto y el criterio. |
