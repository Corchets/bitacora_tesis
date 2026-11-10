# #143 después de la etapa 2: propuesta para seguir (2026-11-09)

> **Estado: propuesta sin discutir.** La escribió la sesión de la etapa 2 a pedido de Mateo, que preguntó cómo seguir:
> pasos, sesiones, alternativas, decisiones pendientes y trabajo para repartir en el equipo. Las cifras nuevas salen de
> [`exploracion.py`](exploracion.py) ([salida](exploracion-salida.md)), escrito después de ver los resultados: son
> hipótesis y no deciden nada (ADR 0005). El resultado de la etapa 2 está en [`analisis.md`](analisis.md).

## Decisiones de Mateo (2026-11-09, después de leer esta propuesta)

- **Etapa 3: va** (opción B de §3.1). La preparan las sesiones `etapa3-143` (la corrida) y `corpus-escenarios` (la
  limpieza).
- **Una sola consulta por línea (cambio de Mateo, más tarde el mismo día).** Se descarta la variante 1 de §3.1, la
  pregunta de pedido crítico como consulta aparte: duplica las consultas y el teléfono no lo aguanta. Las versiones
  son tres, todas con una consulta por línea:
  1. **C sin alerta (base):** el JSON pide solo `"riesgo"`, y el primer aviso sale con 0,3.
  2. **C con mención** (la variante 2 de §3.1):
     - el texto de C dice que esos pedidos son una señal fuerte, sin ordenar que suba el riesgo;
     - el JSON pide solo `"riesgo"`;
     - la alerta fuerte sale de un segundo umbral, elegido con una regla escrita antes.
  3. **C con campo:**
     - el JSON pide `{"pedido_critico": true/false, "riesgo": x}`, en ese orden, y se corta después del riesgo;
     - el primer aviso sale con riesgo ≥ 0,3, y la alerta fuerte, con `pedido_critico`;
     - es la señal de la variante 1, pero dentro de la misma consulta.
- **No se agregan otras versiones.**
- **Plan final (Mateo, más tarde):** Mateo quiere probar «C con campo». La etapa 3 prueba dos versiones: C sin alerta
  (base) y C con campo.
  - «C con mención» queda afuera: su alerta fuerte depende de un segundo umbral de riesgo, frágil en el teléfono, y el
    campo da la misma información de forma más robusta.
  - Se le pasó el plan completo a la sesión `etapa3-143`.
- **Lo que corre la etapa 3 (Mateo, en la sesión `etapa3-143`, 2026-11-09).** Reemplaza lo que había contestado ahí
  antes («solo V2», C más un párrafo, con una sola señal).
  - «C con campo» contra la base «C sin alerta».
  - **`pedido_critico`, definición de Mateo:**
    - se define por el propósito: OTRA lleva a PROTEGIDA a dar o hacer algo que le permita a alguien sacarle plata,
      tomar sus cuentas o hacerse pasar por ella;
    - 8 ejemplos:
      - un código;
      - una clave o un PIN;
      - los datos completos de la tarjeta;
      - una foto del DNI o de la cara;
      - transferir, pagar o entregar plata o la tarjeta;
      - instalar un programa o compartir la pantalla;
      - seguir pasos en el cajero o en la app;
      - cortar y llamar a otro número;
    - no cuentan el número de DNI, la fecha de nacimiento, el nombre ni la dirección;
    - cuenta aunque la frase la diga PROTEGIDA;
    - las advertencias no cuentan.
  - **Tope de FA:** FA(base) + 5. Reemplaza el «sin más de 2 FA» del borrador de regla de §3.1.
  - **Solo OTRA:** se adopta si queda dentro de ±2 en todas las cifras y en las dos corridas.
  - **`alcance-91` va como vista,** con la propuesta de la sesión del corpus (PR #161): si el veredicto se invierte,
    decide el equipo. **Falta que Mateo lo confirme.**
- **Dos señales:** desde la etapa 3 se informan «cualquier aviso» y «alerta por pedido crítico», y la política se elige
  antes del test (§3.2).
- **La base es «C sin alerta»:**
  - la primera consulta pide solo `"riesgo"`;
  - se mide en la misma corrida de la etapa 3, no en una aparte (reemplaza la propuesta de §2.5);
  - las versiones 2 y 3 se arman sobre esa base;
  - **propuesta:** una regla escrita antes que la compare con C de la etapa 2; si alguna cifra se aparta más de ±2, la
    base queda C sin tocar el prompt, cortada tras el riesgo.
- **Consultar solo en las líneas de OTRA:** se vuelve a medir en la etapa 3, como lectura preregistrada. Si se confirma
  dentro de ±2, se adopta desde el comienzo de la llamada.
- **Política de consultas a preregistrar:**
  - la misma consulta en cada línea, o solo en las de OTRA si se confirma;
  - después del primer aviso sigue la misma consulta, y el aviso no se apaga;
  - **después de la alerta fuerte, el detector corta** (Mateo);
  - el motivo se pide una vez por llamada: en la primera alerta fuerte (`pedido_critico` en true). El aviso de
    precaución, con riesgo ≥ 0,3, usa un texto fijo y no consulta nada más. Motivo y evidencia van separados, como en
    `motivo_c_corte.txt`. Reemplaza el motivo pedido con 0,3 de §2.6 (así quedó en la sesión `etapa3-143`).
- **La limpieza del corpus es necesaria.**
  - Las legítimas de desarrollo se generaron todas con agentes: Evaristo no escribió ninguna a mano. Los escenarios y
    las dudosas los revisa un agente en la sesión `corpus-escenarios`.
  - La credibilidad de #145 sigue siendo trabajo humano.
- **Las coreanas:** Evaristo (`Corchets`) subió las traducidas del grupo A (§5.2 del relevamiento). Faltan las demás.
- **Teléfono (#141):** Nacho mide ya lo que no depende de la configuración final (§6). Mide un solo tipo de consulta:
  el riesgo, con unos 10 tokens de salida, o unos pocos más con el campo. Aparte, el motivo.
- **Revisiones de Luciano:** ya están en `laboratorio-main` (PR #160, 2026-11-07), con un solo revisor.
  - #144: sus fichas de las 20 llamadas de inglés, 16 conservadas y 4 descartadas. Las conversaciones siguen fuera de
    Git.
  - #145: 20 de las 42 fichas de la muestra, 17 confirmadas y 3 sin confirmar.
  - Quien haga la segunda revisión no tiene que mirarlas antes de anotar.

## 1. Qué se puede concluir y qué no

**Sí:** el planteo de C («mirá hacia dónde va la llamada») le gana al de v4 («buscá el pedido»). Como pregunta
principal del detector, el estilo de v4 queda descartado.

**Con tres matices:**
- **Se compararon prompts enteros.** C también cambia otras cosas, como la oración del DNI y la lista de maniobras. El
  planteo es la mejor explicación, pero no se aisló.
- **La lista literal de v4 todavía sirve para algo.** De los 7 pedidos explícitos de un código o una clave que C no
  avisa a tiempo, v4 avisa 5. Eso es lo que propone retomar la etapa 3, como canal aparte y angosto (§3.1).
- **La ventaja en FA depende del lote de legítimas.** La ventaja en detección no.

  | legítimas | llamadas | FA v4 | FA C |
  |---|---|---|---|
  | piden datos personales | 64 | 39 | 21 |
  | no piden datos personales | 30 | 3 | 6 |

  Si las legítimas que piden el DNI de entrada no son realistas, la ventaja de C en FA se achica. Además, las 94
  legítimas no son 94 escenarios: una medida gruesa da entre 45 y 75 grupos, según el umbral, y unos 56 en el medio
  (§6 de la salida). #45 ya lo había visto en las `ENT-L`.

**No:**
- **Que C sea el mejor prompt.** Con 46 estafas solo se ven efectos de 3 casos o más.
- **Cuál es el techo.** Con un oráculo hecho con la referencia, C más un detector de pedidos críticos llega a 44/46 y
  35/36 a tiempo. Es una cota, no una medición.

## 2. Respuestas a las preguntas de Mateo

### 2.1. ¿El riesgo sube y baja? ¿Qué lo hace bajar?

**Sube y baja, y lo que dice la persona puede bajarlo.**
- **En las líneas de OTRA sube más de lo que baja:** en las estafas sube en el 18 % y baja en el 9 %.
- **En las de PROTEGIDA baja un poco más de lo que sube:** en las estafas sube en el 11 % y baja en el 13 %.

**Después de llegar a 0,3:**

| | llegan a 0,3 | después bajan de 0,3 | y vuelven a 0,3 | terminan debajo de 0,3 |
|---|---|---|---|---|
| estafas | 36 | 23 | 18 | 12 |
| legítimas | 27 | 21 | 9 | 19 |

**Lo que lo baja** (bajadas de 0,2 o más en una línea):
- **En estafas, cuando PROTEGIDA duda o se resiste.** Por ejemplo, «No voy a transferir sin confirmar la reserva con
  el salón» o «Prefiero terminar la llamada y consultar en la sucursal».
- **En estafas, cuando PROTEGIDA pregunta.** Con «¿Te leo el número?», una línea antes del pedido, pasa de 0,6 a 0,4.
- **En estafas, cuando OTRA habla en tono de trámite.** Con «Perfecto, ya estoy viendo la pantalla», con el acceso
  remoto ya dado, pasa de 0,6 a 0,3.
- **En legítimas, cuando se resuelve el problema** («La operación quedó rechazada, no se te cobró») **y cuando
  PROTEGIDA da el DNI** (de 0,7 a 0,2).

En las estafas, 15 de las 29 bajadas grandes caen en líneas de PROTEGIDA.

**Lectura:** el modelo parece puntuar «qué tan peligrosa está la llamada ahora» más que «qué tan probable es que sea
una estafa».
- No cambia el primer aviso, porque ya saltó.
- Pesa si la app muestra el riesgo actual o si un segundo aviso depende de él. Por eso el aviso no debería apagarse
  cuando baja el riesgo (§3.3).

### 2.2. ¿Y si el estafador dice «tranquilo, no es una estafa»?

En las 46 estafas de desarrollo casi no pasa: 4 líneas de OTRA con frases así, y en las 4 C no se movió. Una es «Es
automático, no es una clave bancaria», dos líneas después del pedido.
- **No hay evidencia de que suba, como querría Mateo.** Tampoco de que baje.
- **El corpus no tiene ese patrón,** y las estafas reales sí lo usan. Hay que mirarlo en el set externo (#144).
- Si se quiere que suba, tiene que entrar como regla con una fuente externa (ADR 0005, regla 7), no como ajuste.

### 2.3. ¿Escuchar solo las líneas de OTRA?

Se puede simular con las salidas de la etapa 2. Cada consulta lleva la transcripción entera con las dos voces, así
que no consultar en las líneas de PROTEGIDA no cambia las salidas en las de OTRA.

| corrida | consultas en | estafas | antes del pedido | antes o en el pedido | FA | consultas |
|---|---|---|---|---|---|---|
| C | todas las líneas | 36/46 | 17/36 | 25/36 | 27/94 | 2.621 |
| C | solo OTRA | 35/46 | 15/36 | 25/36 | 24/94 | 1.313 (50 %) |
| C, repetición | todas las líneas | 36/46 | 16/36 | 25/36 | 26/94 | 2.621 |
| C, repetición | solo OTRA | 36/46 | 15/36 | 25/36 | 25/94 | 1.313 (50 %) |

- **Las consultas bajan a la mitad y todo queda dentro de ±2.** Casi siempre el aviso se atrasa una línea.
- **No se pierde contexto:** lo que dice la persona sigue entrando en la consulta siguiente.
- **Hace falta saber quién habla.** Las corridas ya lo suponen (`--hablantes rol`).

### 2.4. ¿Salta por cualquier «soy de…»?

No por cualquiera, pero sí por las presentaciones del banco o de soporte.

**Riesgo de C en la primera línea de OTRA:**
- **0,3 en 5 de las 13 legítimas del banco y en 4 de las 13 de soporte.**
- **En las otras 68 legítimas, nunca:** ventas, delivery, encuestas, turnos médicos, selección de personal y trámites
  quedan en 0,1 o 0,2.
- **En las estafas:** 6 de las 12 del banco tienen 0,3 o más, y 3 de las 6 del organismo previsional.

**Avisos en L1–L3:** 13 de las 27 FA de C y 14 de las 36 estafas que avisa.

**Lo que se puede hacer:**
- **Al comienzo, una llamada real del banco y una falsa dicen lo mismo.** «Te llamo de prevención de fraudes del
  banco» no se puede separar con un prompt. Es una decisión de política: qué tan fuerte es el primer aviso. Va en los
  dos niveles de #33.
- **El caso claramente mal es TecnoFix.** Es el mismo guion 3 veces: «Te hablo de TecnoFix, el local de la calle
  Muñecas. Dejaste una notebook…». Da 0,3 al presentarse, y en las dos versiones sin DNI baja a 0,1 cuando dice que
  la notebook está lista.
- **No se arregla con texto en el prompt sacado de estos casos** (ADR 0005, regla 7).

### 2.5. ¿Se saca `alerta_sugerida` de C?

**No le suma nada con 0,3.**
- En cada corrida de C hay 110 líneas con la alerta escrita dentro del alcance, todas con riesgo de 0,6 o más.
- Leer solo «riesgo ≥ 0,3» no cambia la línea de aviso en ninguna de las 140 llamadas, en ninguna de las dos corridas.

**Propuesta: no tocar el prompt y cortar la generación después del riesgo.**
- **El riesgo sale primero**, así que queda igual que ahora, como en una repetición, y no hay que validar una
  configuración nueva.
- **Sacar el campo de `salida_json_c.txt` cambia el prompt.** Pediría sus dos corridas (ADR 0005, regla 5).
- **Ahorro:** en T4 cada línea tarda 276 ms (mediana), con 6,9 ms por token generado. El riesgo termina hacia la mitad
  de los 24 tokens (`{\n  "riesgo": 0.3,`), así que el ahorro ronda los 80 ms por línea (≈ 30 %). En el teléfono debería
  ser más, porque generar es más lento (#141).
- **Cómo cortar:** el número de tokens lo fija la humo. Un `stop` en la coma falla si el modelo escribe «0,3», así que
  la humo tiene que comprobar que el riesgo llegue entero en todas las líneas.
- **Registro:** es una enmienda del ADR 0006, que lleva la sesión principal.

### 2.6. Motivo propio de C

**De acuerdo con lo que propone Mateo:**
- `motivo_c_corte.txt`, según la definición del JSON de C: por qué puede ser una estafa, con la frase de OTRA que más
  lo muestra;
- que nombre el pedido solo si ya ocurrió;
- que se pida en la primera línea con riesgo ≥ 0,3;
- que se mida en la próxima corrida.

**Sugerencias:**
- **El mismo orden que `motivo_v4_corte.txt`:** primero la evidencia y después el motivo. Con v4 dio motivo en 74 de
  78 avisos.
- **La medición, escrita antes de correr:**
  - JSON válido y motivo no vacío;
  - la evidencia es una frase textual de OTRA hasta esa línea (`evidencia_en_texto`);
  - en los avisos antes de T_R, el motivo no habla de un pedido que todavía no ocurrió.

## 3. Decisiones pendientes

### 3.1. ¿Etapa 3 o congelar ya? (Mateo)

**A. Congelar C ya y pasar al test.**
- C entra con el corte tras el riesgo, la lectura solo en OTRA y el motivo.
- Igual hace falta una corrida corta de desarrollo (~25 min) para la humo del corte y el motivo.

**B. Una sola corrida más de desarrollo, la etapa 3 (recomendada si está lista el 2026-11-12).**

Las dos variantes atacan lo que más le falta a C: 7 de sus 12 errores son pedidos explícitos.
- **C sin cambios**, cortado tras el riesgo y con su motivo. Es una medición, no decide.
- **Variante 1, «C + pedido crítico»:**
  - C sin cambios, más una pregunta literal y angosta, solo en las líneas de OTRA, con SÍ/NO en un token;
  - la pregunta cubre un código que le llegó, una clave o PIN, los datos completos de la tarjeta, transferir o pagar,
    e instalar un programa o compartir la pantalla. El DNI y la fecha de nacimiento quedan afuera;
  - avisa si dispara cualquiera de las dos. **Solo puede sumar avisos y nunca le saca uno a C, así que no vuelve al
    sesgo de v4.** En dos niveles, es la alerta fuerte;
  - el riesgo es el contrario: FA por menciones legítimas, como «nunca te vamos a pedir el código».
- **Variante 2, «C-nunca»:**
  - la misma lista dentro del texto de C, como una oración: nadie legítimo te pide eso por teléfono, aunque el resto
    suene normal;
  - es una sola consulta, pero cambia el prompt de C y puede mover el resto.
- **Comparar 1 contra 2** responde la duda de Mateo: pregunta aparte o dentro de C.
- **Condiciones:**
  - la lista sale de fuentes externas: BCRA, bancos, WhatsApp, procesadoras de tarjetas;
  - la regla se escribe antes de correr, y cada variante va dos veces (ADR 0005);
  - en Colab, unas 1,5 h.

**Borrador de regla:** se adopta una variante si suma 3 o más avisos antes o en el pedido, sin más de 2 FA de
cualquier aviso respecto de C. Si pasan las dos, se elige la de más avisos a tiempo. Dentro de ±2, la de menos
consultas.

**C. Más variantes de C.** Cada una necesita una fuente, su regla y dos corridas, y con 46 estafas no se ven efectos
chicos. Las dejaría para después del test, como exploración declarada.

### 3.2. Qué se cuenta como FA (Mateo, antes del test)

Los dos niveles quedan para #33 y la UI. Pero el ADR 0005 (regla 2) pide escribir la política antes de correr el test.

**Propuesta:**
- desde la etapa 3, informar las dos señales de la misma corrida: «cualquier aviso» y «alerta por pedido crítico»;
- elegir la política antes del test.

No cuesta corridas extra.

### 3.3. ¿Sigue escuchando después de avisar? (Mateo)

**Propuesta:**
- **Seguir escuchando, y consultar solo en las líneas de OTRA desde el comienzo** (§2.3).
- **El aviso no se apaga** cuando baja el riesgo (§2.1).
- **Si la persona descarta el aviso,** el detector sigue solo por los pedidos críticos.

Se escribe como lectura de la etapa 3 y sale de las mismas salidas.

### 3.4. ¿Para qué se usan las estafas reales traducidas? (Mateo y Luciano)

**Lo que hay hoy (#144):**
- **16 llamadas de inglés** (`EXT-*`), armadas por Luciano fuera de Git.
  - 18 de las 20 originales son salientes: el *scambaiter* le devuelve la llamada al estafador, que atiende «gracias
    por llamar a…». Quedan fuera del alcance.
  - La «víctima» actúa, la traducción no está argentinizada y los comienzos ya se leyeron (§7.3 del relevamiento).
- **Las coreanas (KorCCVi)** son llamadas entrantes reales, lo más parecido al alcance. Evaristo subió traducidas las
  del grupo A: según §5.2 del relevamiento, son las 13 con comienzo y pedido. Faltan las 12 del grupo B y los derechos.
  (Corrección de Mateo, 2026-11-09: antes decía que no se encontraban.)
- **Todas son estafas:** miden detección, no FA.

**Opciones:**
- **Como desarrollo.** Con 16 casos, uno vale 6 puntos: no alcanza para elegir entre configuraciones. Además dejan de
  servir como test.
- **Como test, una sola vez.** Es lo que propone Luciano (§7.4) y es la única evidencia externa. Se informa aparte, como
  «salientes, fuera del alcance».
- **Mixta (recomendada si alguien puede traducir las coreanas a tiempo):**
  - las de inglés, como exploración externa: ver cómo se porta C con el lenguaje real (tranquilizar, rodeos largos),
    sin ajustar prompts;
  - las coreanas (13 con comienzo y pedido), como test.

**Sobre la preocupación de Mateo:** no se ajustaron prompts sobre fallos del corpus (ADR 0005). Pero sí se eligió con
este corpus, y la parte de FA de esa elección depende de las legítimas que piden datos (§1). Eso lo resuelve la
limpieza (§3.5), y no hace falta cambiar de casos de desarrollo.

### 3.5. Limpieza del corpus de desarrollo (equipo, antes de la próxima corrida)

**FA por escenario,** además de por llamada:
- los grupos los arma un agente con el método de #45;
- los confirma Evaristo, que escribió las legítimas.

**Legítimas dudosas:**
- se marcan con un criterio escrito antes de mirar cuáles tuvieron FA, por ejemplo «seguridad bancaria que pide el DNI
  y la fecha de nacimiento antes de decir para qué llama»;
- el criterio necesita una fuente citable sobre qué hace una llamada real; si no la hay, es un juicio del equipo y se
  aplica a ciegas;
- no se borran: se informan aparte.

**Las 10 estafas sin pedido:**
- entran a #145 con el campo a/b/c: cortada, primer contacto, incoherente;
- se informan los dos denominadores (D07, reunión del 2026-11-11);
- **si salen de la cifra principal, C sigue ganando** en avisos antes del pedido (17 contra 10) y en FA, pero pierde
  las +8 estafas.

### 3.6. Repetición del ADR 0005 (sesión principal, antes de la próxima corrida)

En la repetición de C, el aviso cambió de línea en 3 casos, y 2 cambiaron una cifra. «Más de 2 casos» hay que
interpretarlo antes de la etapa 3.

**Propuesta:** contar solo los cambios que mueven una cifra de la regla. Con 2, no se dispara.

## 4. Pasos y fechas

| cuándo | qué | quién |
|---|---|---|
| 2026-11-09/10 | Decisiones 3.1–3.4. OK al commit de la etapa 2 y al comentario de #143 | Mateo |
| 2026-11-09/10 | Guía de #145 con a/b/c; grupos de escenarios; criterio de dudosas | Luciano, Evaristo, sesión A |
| 2026-11-10/11 | Etapa 3 preparada: fuentes, prompts, regla escrita, Colab, humo en seco y tag | sesión B, con los OK de Mateo |
| 2026-11-11 | Reunión: D07 (sin pedido), plan de #45, #152 (audio) | equipo |
| 2026-11-11/12 | Colab de la etapa 3, unas 1,5 h | Mateo |
| 2026-11-12/13 | Análisis y ADR 0002 congelado, con la política | sesión B y principal |
| 2026-11-13/15 | #45 congelado y test, una sola vez: reserva, legítimas de test y set externo | equipo |
| 2026-11-16/30 | Teléfono (#141), escritura y presentación (#142) | equipo |

**Si la etapa 3 no está lista el 2026-11-12, opción A:** se congela C y la etapa 3 corre después del test, como
exploración declarada.

## 5. Sesiones

**A. Corpus de desarrollo: escenarios y legítimas dudosas.**
- Agrupa las 94 legítimas con el método de #45.
- Propone el criterio de dudosas, con fuentes.
- Arma para #145 la hoja de las 10 sin pedido.
- Recién después recalcula, como exploración, las cifras de la etapa 2 por escenario y sin dudosas.
- Prepara, no juzga: el juicio es humano (#145). No toca la reserva ni el test.

**B. #143, etapa 3.**
- Confirma las decisiones de §3 con Mateo.
- Prepara la corrida: fuentes, prompts, regla escrita, Colab fijado a un tag y humo en seco.
- No corre nada.

**Sesión principal:**
- la enmienda del ADR 0006 (corte tras el riesgo en C);
- la lectura de «más de 2 casos» del ADR 0005;
- el ADR 0002 cuando se congele;
- los hallazgos.

## 6. Trabajo humano para repartir

| quién | qué | por qué una persona |
|---|---|---|
| Luciano | Guía de #145 hoy, con el campo a/b/c para las sin pedido. Decidir con Mateo el papel del set de inglés y los derechos de KorCCVi | Tiene la custodia de #144 y lleva #145 |
| Nacho | #141, ya: en el teléfono, comparar el riesgo de C con el de T4 en las mismas líneas (¿0,3 sigue siendo 0,3?) y medir la latencia de una consulta según el largo del contexto y los tokens generados (24, solo el riesgo, 1 de SÍ/NO). El costo de cada política sale de ahí por cuenta. Con la configuración congelada, una corrida de confirmación | Todo C cuelga de ese escalón: con 0,4 baja a 15/46 |
| Evaristo | Las 14 `LEG2` de test (#45) | Corrección de Mateo (2026-11-09): las legítimas se generaron con agentes, así que los escenarios los arma la sesión `corpus-escenarios` |
| Luciano o Evaristo | Comprobar que el lote de test de #45 no repita escenarios ni comparta escenarios con desarrollo, sin correr nada | Tiene que ser alguien que no ajusta el detector |
| Mateo | Las decisiones de §3, correr los Colab y verificar las fuentes de la lista de pedidos críticos | No revisa #145, porque ya vio los resultados |
| Opcional | Traducir y revisar las 13 llamadas coreanas con comienzo y pedido, si los derechos lo permiten | Darían el único test externo dentro del alcance |

## 7. Lo que no haría

- **Reglas de riesgo sostenido:** la detección útil cae de 25 a 16.
- **Más variantes de C sobre desarrollo antes del test.**
- **Corregir las aperturas del banco o de TecnoFix con texto sacado de esos casos.**
- **Ajustar nada mirando el set externo.**
- **Volver a v4 con 0,3:** da 52/94 FA.
