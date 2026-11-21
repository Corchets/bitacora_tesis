# #143, segunda vuelta, etapa 2: C y v4-premisa contra v4 dentro del alcance

> **Estado: propuesta sin discutir.** Prueba de desarrollo; la reserva no se tocó. El criterio está en
> [`README.md`](README.md) y en [`analizar.py`](analizar.py), escritos antes de correr y confirmados por Mateo
> (`python -I analizar.py`). La salida completa está en [`analisis-salida.md`](analisis-salida.md). Las secciones
> «Qué mejoró», «Lo que le queda a C» y «Para seguir» salen de [`diagnostico.py`](diagnostico.py), que se escribió el
> 2026-11-09 después de ver los resultados y no cambia el criterio ([`diagnostico-salida.md`](diagnostico-salida.md)).

## Resumen

- **Según la regla, se adopta C con «riesgo ≥ 0,3 o alerta», provisorio hasta la reserva.** Contra `v4-corte` avisa
  8 estafas más y 7 avisos más antes del pedido, con 15 FA menos (27 contra 42 de las 94 legítimas entrantes). La
  repetición lo sostiene.
- **`v4-premisa` queda dentro del ruido:** la oración del alcance sola no cambia a v4.
- **Dónde gana C:**
  - las 8 estafas de más son todas estafas sin pedido;
  - en las que tienen pedido, detecta las mismas, pero antes;
  - las FA bajan porque deja de alertar cuando una legítima pide el DNI.
- **Lo que le queda:**
  - FA al comienzo de llamadas legítimas de seguridad bancaria o de soporte, que empiezan igual que una estafa;
  - pedidos explícitos de un código o una contraseña en contextos que no parecen estafa, donde escribe 0,1–0,2.
- **La próxima mejora con más techo:** sumarle a C un detector literal de pedidos críticos (códigos, claves, plata,
  control del celular; sin datos personales). Con la referencia como oráculo, el techo es de 44/46 estafas y 35/36
  avisos a tiempo, con las mismas FA.

## Qué se corrió

- **Colab T4, el 2026-11-07 de 23:31 a 01:15 UTC** (20:31 a 22:15 en Argentina), 1 h 44 min:
  1. la humo de formato de los dos prompts nuevos en los 3 casos de siempre (48 líneas);
  2. `v4-corte` sobre los 244 casos de desarrollo, en 23,5 min;
  3. `c-json-corte` sobre los 244, en 21,8 min, y su repetición sobre los 140 dentro del alcance, en 13,0 min;
  4. `v4-premisa-corte` sobre los 244, en 23,4 min, y su repetición sobre los 140, en 14,0 min;
  5. los 6 controles de ventas y préstamos con los tres prompts, en 1,5 min.
- **Las tres configuraciones** usan el JSON cortado después de `alerta_sugerida` (`num_predict` 24) y piden el motivo
  aparte, en la primera línea en que dispara «riesgo ≥ 0,4 o alerta» (ADR 0006). Cada prompt es su base tal cual
  (`CORTE_DE`). Todas corren en todas las líneas (`--seguir-tras-aviso`), con roles y `--sin-reglas`.
- **Mismo setup que las etapas anteriores:** commit `d127953` (tag `colab/143-etapa-2`), Ollama 0.40.14, digest
  `b37049369adf…`, `num_ctx` 4096, seed 42 y temperatura 0.
- **Los ZIP están verificados** (2026-11-09), con el procedimiento de
  [`2026-11-07_json-cortado/README.md`](../2026-11-07_json-cortado/README.md):
  - cada uno de los 8 se descomprimió en un directorio vacío nuevo, y los 7 parciales coinciden byte a byte con su
    carpeta en el final;
  - `commit.txt`, los 6 `TERMINADA.txt` y los 7 manifiestos dan `d127953`, sin cambios sin commitear;
  - el sha256 de `colab/probar_etapa_2.py` en el tag coincide con `script-sha256.txt` (`3966e0ac…`);
  - el digest del modelo coincide en los 7 manifiestos y en `digest.txt`;
  - el texto de la segunda consulta es el de `motivo_v4_corte.txt` en todas;
  - no hay casos de la reserva.
- **Control de `analizar.py`:** sin problemas. Son 4.325 líneas por corrida sobre los 244 y 2.621 sobre los 140, sin
  inválidas.
- **La humo pasa en los dos prompts, y no se ajustó nada:** la alerta termina en el token 23 en las 48 líneas, y el
  cortado lee riesgo y alerta en las 48. Como dato, el cortado escribe el mismo riesgo y la misma alerta que el JSON
  completo en 43 de las 48.

## Resultado según el criterio

**Punto de comparación:** `v4-corte` con su regla adoptada («riesgo ≥ 0,4 o alerta») da **F = 42/94 FA**. Cada
configuración usa su regla con FA ≤ 42 que avisa más estafas.

| configuración | regla | estafas | antes del pedido | antes o en el pedido | FA | contra `v4-corte` | veredicto |
|---|---|---|---|---|---|---|---|
| `v4-corte` (referencia) | riesgo ≥ 0,4 o alerta | 28/46 | 10/36 | 25/36 | 42/94 | — | — |
| C (`c-json-corte`) | riesgo ≥ 0,3 o alerta | 36/46 | 17/36 | 25/36 | 27/94 | +8 estafas, +7 antes | gana en las dos; la repetición lo sostiene (+8, +6, FA 26): **cuenta** |
| `v4-premisa-corte` | riesgo ≥ 0,4 o alerta | 27/46 | 11/36 | 25/36 | 41/94 | −1, +1 | dentro de ±2: queda `v4-corte` |

**Se adopta C con «riesgo ≥ 0,3 o alerta», provisorio hasta la reserva.** Lo que sigue en esta sección es solo para
mirar.

- **La curva de C queda por encima de la de v4 por debajo de 52/94 FA.**
  - Con FA ≤ 9 y ≤ 14, solo C tiene un punto: con «riesgo ≥ 0,4 o alerta» da 15/46, 6/36 y 9/94. v4 y `v4-premisa`
    no bajan de 41 FA con ninguna regla.
  - Recién con 52 FA, v4 con 0,3 avisa más estafas (39/46).
  - Así que la ventaja no depende de haber elegido 0,3 para C y 0,4 para v4.
- **Pares discordantes** en los mismos casos, con McNemar exacto. El p es optimista, porque el umbral de C se eligió
  sobre estos casos.

  | cifra | solo C | solo v4 | p |
  |---|---|---|---|
  | estafas avisadas | 11 | 3 | 0,057 |
  | avisos antes del pedido | 8 | 1 | 0,039 |
  | detección útil (antes o en el pedido) | 4 | 4 | 1 |
  | FA | 7 | 22 | 0,008 |

- **Intervalos de Wilson en el punto de comparación:**

  | | estafas | antes del pedido | detección útil | FA |
  |---|---|---|---|---|
  | `v4-corte` | 61 % [46–74] | 28 % [16–44] | 69 % [53–82] | 45 % [35–55] |
  | C | 78 % [64–88] | 47 % [32–63] | 69 % [53–82] | 29 % [21–39] |

- **Con las legítimas entrantes, v4 da 45 % de FA.**
  - En corpus_v2 daba 7/51 (14 %): 44 de esas 51 las inicia la persona, y ahí la excepción de v4 deja pasar el pedido
    de datos.
  - Las 94 nuevas son entrantes y piden datos personales en 64.
- **La repetición de C** avisa en otra línea en 3 casos, y 2 de ellos cambian una cifra:
  - `CV2-D-V-FAMILIAR-003` pasa de antes del pedido a la línea del pedido;
  - `LEG-CC-03` deja de dar FA;
  - `CV2-D-V-BANCO-003` pasa de L3 a L1.

  El riesgo escrito coincide en el 95,9 % de las líneas, y en `v4-premisa`, en el 98,7 %. El ADR 0005 se reconsidera
  si dos repeticiones «difieren en más de 2 casos»: por cifras, no se llega; por línea de aviso, son 3. Cómo se lee lo
  decide quien lleva los ADR.

## Qué mejoró, dónde y por qué (diagnóstico, fuera del criterio)

### Las 8 estafas de más son todas estafas sin pedido

| primer pedido crítico | estafas | v4 avisa | C avisa | v4 antes / en / después | C antes / en / después |
|---|---|---|---|---|---|
| sin pedido | 10 | 1 | 9 | — | — |
| código (`AUTH_CODE`) | 10 | 9 | 7 | 3 / 5 / 1 | 5 / 2 / 0 |
| clave (`SECRET`) | 7 | 4 | 5 | 1 / 3 / 0 | 4 / 0 / 1 |
| plata (`TRANSFER`) | 9 | 6 | 6 | 3 / 3 / 0 | 3 / 3 / 0 |
| datos personales | 6 | 4 | 5 | 0 / 3 / 1 | 3 / 2 / 0 |
| acción de seguridad | 2 | 2 | 2 | 2 / 0 / 0 | 2 / 0 / 0 |
| acceso remoto | 2 | 2 | 2 | 1 / 1 / 0 | 0 / 1 / 1 |

- **Sin pedido, v4 avisa 1 de 10 y C 9 de 10.** Es lo que predecía H05: v4 es un detector de pedidos, y C no.
- **Con pedido, los dos detectan 27 de 36, pero C avisa antes:**
  - antes del pedido, 17 contra 10;
  - la mediana del adelanto en los avisos a tiempo es de 4 líneas contra 0;
  - con 3 líneas o más de adelanto, 13 contra 9.

  Confirma la causa que daba H03: el SLM avisaba en el pedido porque el prompt definía el aviso como «hay un pedido».
- **La detección útil (antes o en el pedido) queda igual, 25 de 36, pero no son las mismas:**
  - C avisa a tiempo 4 que v4 no: `ORGANISMO_PREVISIONAL-003`, `ORGANISMO_PREVISIONAL-004`, `SOPORTE-006` y
    `WHATSAPP-004`;
  - v4 avisa a tiempo 4 que C no: `WHATSAPP-003`, `WHATSAPP-005`, `SOPORTE-001` y `SOPORTE-004`. Las 4 son pedidos
    explícitos de un código, una clave o el control del celular.

### La FA baja porque C deja de alertar por el DNI

- **De las 94:** FA con los dos, 20; solo v4, 22; solo C, 7; con ninguno, 45.
- **Por lote, las FA bajan donde se pide el DNI:**

  | lote | FA v4 | FA C |
  |---|---|---|
  | LEG (21) | 3 | 5 |
  | LEG2 (28) | 15 | 8 |
  | ENT-L (42) | 23 | 14 |
  | selección (3) | 1 | 0 |

- **Cuándo cae la FA, según los eventos de la referencia:**

  | la FA cae… | v4 | C |
  |---|---|---|
  | en la línea en que la legítima pide un dato personal | 35 | 6 |
  | después de un pedido de datos | 3 | 7 |
  | antes de cualquier pedido | 4 | 14 |

  - 35 de las 42 FA de v4 caen justo en la línea en que la legítima pide el DNI, la fecha de nacimiento o el nombre
    completo.
  - En las 64 legítimas que piden datos, v4 da 39 FA y C 21.

### Por qué: lo que cambia es la pregunta del prompt, no la oración del alcance

- **v4 pregunta «¿hay un pedido peligroso?»**, y su lista incluye «dar datos personales (DNI, CUIL, fecha de
  nacimiento…)». La única excepción es que la persona haya iniciado la gestión, y dentro del alcance eso nunca pasa.
  Por eso, toda legítima entrante que pide el DNI para identificar a la persona le parece una estafa.
- **`v4-premisa` no cambia nada** porque la oración del alcance no toca esa lista: 27/46, 11/36 y 41/94, casi lo mismo
  que v4.
- **C pregunta «¿qué tan probable es que sea una estafa, mirando hacia dónde va la llamada?»**, permite avisar antes
  del pedido y dice que una llamada legítima también puede pedir el nombre, el DNI o la fecha de nacimiento.
  - Con eso desaparece el disparador del DNI: 35 FA de v4 en esa línea contra 6 de C.
  - Y el riesgo pasa a ser un puntaje con un escalón de sospecha: C escribe 0,3 cuando la llamada se parece a una
    estafa, aunque no haya pedido.
- **Cómo usa cada prompt el riesgo escrito:**
  - En v4, el riesgo ≥ 0,4 es casi lo mismo que la alerta: 497 de sus 567 líneas con riesgo ≥ 0,4 tienen la alerta en
    true. Por eso su curva es plana de 0,4 a 1.
  - C escribe la alerta mucho menos (10/46 estafas con «alerta sola») y usa el 0,3 como nivel intermedio.

  | máximo riesgo de la llamada | 0,1 | 0,2 | 0,3 | 0,5 o más |
  |---|---|---|---|---|
  | C, estafas (46) | 0 | 10 | 21 | 15 |
  | C, legítimas (94) | 22 | 45 | 18 | 9 |
  | v4, estafas (46) | 0 | 7 | 13 | 26 |
  | v4, legítimas (94) | 17 | 25 | 12 | 40 |

  - En C, el 0,3 junta 21 estafas y 18 legítimas, y entre 0,3 y 0,4 no hay nada.
  - En v4, 40 de las 94 legítimas llegan a 0,5 o más.

### Lo que C empeora o deja igual

- **Fuera del alcance avisa más:**
  - en corpus_v2 entero, 13/51 FA contra 7/51. Las 13 son llamadas que inicia la persona: en las 7 legítimas de
    corpus_v2 dentro del alcance, C no da ninguna;
  - en los manuales del laboratorio, 8/10 contra 5/10.

  No pesa si el detector corre solo en llamadas entrantes de números no agendados (ADR 0003), pero C con 0,3 no
  debería correr fuera de ahí.
- **En el lote LEG suma 2 FA** (5 contra 3).
- **Los controles de ventas no cambian en la regla:** los tres prompts avisan en las 3 legítimas difíciles en L3–L4.
  Mirando el riesgo línea por línea:
  - v4 escribe 0,5–0,9 en las tres y la alerta escrita desde L3, L4 u L8;
  - C escribe 0,1–0,3 en las dos de préstamos, y 0,6 con alerta en dos líneas de la portabilidad.
- **Latencia (T4, p50 / p95, dentro del alcance):**
  - C es un poco más rápido: 276 / 335 ms por línea contra 290 / 350 de v4, porque su prompt es más corto (777 tokens
    contra 1.052);
  - la segunda consulta tarda lo mismo (690 / 847 ms).

## Lo que le queda a C (dónde está la próxima mejora)

**Estafas: 10 sin aviso y 2 con aviso después del pedido.** En todas, C escribe como máximo 0,2 (0,3 en las dos
tardías).

| grupo | estafas | v4 |
|---|---|---|
| pedido explícito de un código en un contexto que no parece estafa (un taller de la biblioteca, el grupo de un club) | `WHATSAPP-003`, `WHATSAPP-005`, `WHATSAPP-006` | avisa las 3: dos en el pedido y una 3 líneas después |
| pedido de usuario y contraseña de una plataforma (un curso, la cuenta) | `SOPORTE-003`, `SOPORTE-005` | no avisa |
| aviso de C después del pedido | `SOPORTE-001` (clave), `SOPORTE-004` (acceso remoto) | avisa en el pedido |
| un familiar que sugiere la transferencia sin pedirla («si apareciera esa diferencia en mi cuenta…») | `FAMILIAR-004`, `FAMILIAR-005`, `FAMILIAR-006` | no avisa |
| un premio que pide el DNI, y uno sin pedido | `PREMIO-003`, `PREMIO-006` | no avisa |

- **10 de esos 12 tienen un pedido crítico según la referencia** (código, clave, plata o acceso remoto):
  - 7 son explícitos: los 3 de WhatsApp y los 4 de soporte;
  - 3 son la transferencia que los familiares sugieren sin pedirla.
- **C no ve los explícitos porque el contexto no se parece a su descripción de una estafa** (alguien de confianza, un problema,
  urgencia). Por ejemplo, en `WHATSAPP-003` la llamada es por un taller de huerta, y C escribe 0,2 cuando OTRA dice
  «Leeme los seis dígitos y te incorporo al grupo».
- **v4 los ve en parte por su lista literal,** pero no las dos contraseñas de `SOPORTE`: el modelo no aplica la lista
  siempre cuando el contexto es amable.

**FA: 27 de 94.** 25 de ellas son riesgo 0,3 sin alerta escrita.

- **14 caen antes de cualquier pedido:**
  - 7 al comienzo de llamadas legítimas del banco («te llamo del área de prevención de fraudes», «del sector de
    seguridad»);
  - 4 de soporte técnico o de un local que llama por un equipo. El mismo guion de TecnoFix aparece en tres lotes
    (`LEG-ST-03`, `LEG2-ST-03` y `ENT-L-SOPORTE-003`) y da las 3 FA;
  - 1 encuesta del banco, 1 oferta de venta y 1 empresa que manda a llamar al 0800.
- **13 caen en o después de un pedido de datos personales,** o en un pedido real de la legítima: la seña de un
  crédito, o descargar la asistencia remota.
- **Al comienzo de la llamada, el texto todavía no las distingue:** en L1–L2, C avisa 12 estafas y 9 legítimas, con
  la misma clase de frase.

**Techo de sumarle a C un detector literal de pedidos críticos.** Exploración: la referencia hace de oráculo, así que
supone un detector que nunca falla, y las marcas no tienen revisión humana.

| regla | estafas | antes del pedido | antes o en el pedido | FA |
|---|---|---|---|---|
| C, «riesgo ≥ 0,3 o alerta» | 36/46 | 17/36 | 25/36 | 27/94 |
| pedido crítico (oráculo), solo | 30/46 | 0/36 | 30/36 | 2/94 |
| C o pedido crítico (oráculo) | 44/46 | 17/36 | 35/36 | 27/94 |

- **Un detector de pedidos críticos que no cuente los datos personales casi no da FA** en las legítimas entrantes:
  solo 2 tienen un pedido así (la seña de un crédito y una asistencia remota), y C ya las avisa.
- **Juntado con C, recupera 8 estafas y pone a tiempo los 2 avisos tardíos:** 10 de los 12 errores.
- **En la práctica, una pregunta literal tiene chances con los 7 pedidos explícitos.** Con las 3 transferencias
  sugeridas de los familiares, menos.

**Lo que no ayuda: exigir el riesgo en líneas seguidas.** Con C, exigir 0,3 en 2 líneas seguidas baja las FA de 27 a
18, pero la detección útil cae de 25/36 a 16/36. La primera subida a 0,3 dura muchas veces una sola línea: en 14 de
36 estafas y en 13 de 27 legítimas. Así que el aviso se atrasa más allá del pedido, y no se separan las estafas de las
legítimas.

**La segunda consulta (motivo) no se midió con la regla de C.**
- En Colab corrió con «riesgo ≥ 0,4 o alerta», así que en 39 de las 63 llamadas en que avisa C nunca corrió.
- En 59 de los 63 avisos de C, el modelo no escribió la alerta: avisa solo el riesgo. En la corrida del JSON cortado,
  los 4 fallos de la segunda consulta de v4 estaban todos en ese tipo de aviso (19 de 78).
- `motivo_v4_corte.txt` pide «lo que le están pidiendo». Cuando corrió antes del pedido y había algo concreto, los
  motivos están bien. Por ejemplo, en `BANCO-004`: «te están pidiendo un código para confirmar tu titularidad»,
  después de «Te mando un código para confirmar que sos titular».
- No se sabe qué escribe cuando C avisa al comienzo de la llamada y todavía no hay nada que nombrar.

## Cuidados antes de congelar el ADR 0002

- **El punto de C está en un solo escalón.**
  - Con 0,3, 36/46 y 27/94; con 0,4, 15/46 y 9/94.
  - La repetición se sostuvo en la misma sesión de Colab, pero si el teléfono escribe el decimal un poco distinto, el
    punto se mueve mucho. Conviene mirar en el teléfono la distribución del riesgo de C (#141), además de la latencia.
- **Avisar con 0,3 es avisar sin que el modelo haya sugerido la alerta** en 59 de 63 avisos. El motivo de esos avisos
  no está medido (ver arriba).
- **C con 0,3 no debería correr fuera del alcance** (13/51 FA en corpus_v2 entero).
- **R29 (#154):** C dice que pedir el DNI no vuelve estafa una llamada.
  - Las legítimas nuevas piden datos en 64 de 94, y solo 6 de las 46 estafas tienen los datos personales como primer
    pedido. C avisa 5 de esas 6, mejor que v4 (4).
  - Con 6 casos no se puede descartar que C aprenda «DNI → legítima». Hacen falta las estafas que piden el DNI del #154.

## Para seguir (propuesta; lo decide el equipo)

> **Actualizado el 2026-11-09:** Mateo dejó los dos niveles de aviso para #33 y la UI, y preguntó cómo seguir. La
> propuesta nueva, con las decisiones pendientes, los pasos y el trabajo para repartir, está en
> [`PROPUESTA-SIGUIENTE.md`](PROPUESTA-SIGUIENTE.md). Lo de abajo queda como estaba.

1. **Decidir cómo avisa la app con C (#33), antes del ADR 0002.** Hay dos caminos:
   - **Un nivel:** avisar con «riesgo ≥ 0,3 o alerta» como alerta. Hace falta un motivo pensado para C («por qué puede
     ser una estafa», como en `salida_json_c.txt`), medido en las líneas de aviso de C: unos 15 min de Colab sobre
     los 140.
   - **Dos niveles (recomendado):**
     - «precaución» con C ≥ 0,3, con un texto fijo del estilo «no compartas códigos ni claves ni transfieras; si
       dudás, cortá y llamá vos al número oficial»;
     - «alerta» cuando hay un pedido crítico o C escribe la alerta, con el motivo de hoy, que nombra el pedido.

     Al comienzo de una llamada del banco el texto no distingue la legítima de la estafa (12 contra 9 en L1–L2), y esa
     precaución es lo mismo que aconsejan los bancos. Así, las FA de C al comienzo pasan a ser un consejo, no una
     alarma. El nivel de precaución no necesita correr nada nuevo.
2. **La próxima prueba de detección: C más una pregunta literal de pedidos críticos.**
   - **Qué es:** al final de la misma transcripción, una pregunta corta de un token: «¿OTRA le pidió a PROTEGIDA un
     código, una clave, una contraseña o un usuario, plata, o instalar algo o dejarle manejar el celular?».
     - Sin datos personales.
     - Con una regla fija escrita antes: avisar si C ≥ u o si la pregunta da SÍ.
     - Es la idea 1 de `IDEAS-PENDIENTES.md`, reducida a una pregunta.
   - **Por qué:**
     - 10 de los 12 errores de detección de C tienen un pedido crítico, y 7 son explícitos;
     - el techo con oráculo es de 44/46 y 35/36 avisos a tiempo, sin FA nuevas;
     - el detector de pedidos críticos solo, con oráculo, da 2/94 FA.
   - **Cómo, según el ADR 0005:**
     - la lista sale de fuentes externas: bancos, el BCRA y WhatsApp («nunca compartas el código»). No sale de los
       fallos;
     - el prompt de C no cambia, así que es un cambio por vez;
     - va la humo, los 244 con la repetición (cerca de 1 h de Colab) y la latencia de la pregunta de más, que reutiliza
       la caché de la transcripción;
     - los controles deberían incluir menciones («no compartas el código») y pedidos de DNI, que tienen que dar NO.
   - **Riesgos:**
     - el problema de A1 en la primera vuelta: el SÍ literal ante un DNI o una mención;
     - v4 tiene esa lista y aun así no avisó las dos contraseñas de `SOPORTE`. Lo que no se sabe es qué tan bien
       contesta E2B una pregunta literal cuando el contexto es amable;
     - como la idea sale de este diagnóstico, la cifra de desarrollo es optimista. Hay que confirmarla en #144
       (detección) y en la reserva.
3. **Datos para confiar en C,** en paralelo y sin Colab:
   - las estafas que piden el DNI del #154 (R29);
   - más llamadas legítimas de seguridad bancaria y estafas con el mismo comienzo, que es la principal fuente de FA
     de C;
   - revisar guiones repetidos entre lotes, como el de TecnoFix: 3 FA salen de un guion;
   - ver si #144 tiene estafas de códigos en contextos amables, el punto ciego de C.
4. **Teléfono (#141):** la latencia y la distribución del riesgo de C. Su ventaja vive en el 0,3.
5. **Lo que no conviene probar, según estos datos:**
   - exigir el riesgo en líneas seguidas, porque atrasa los avisos;
   - la oración del alcance en v4, porque no hace nada;
   - bajar v4 a 0,3, que da 39/46 con 52/94 FA.
6. **Más adelante:**
   - **El sondeo de LoRA** que ya está planeado. Los errores que quedan son semánticos (pedidos en contextos amables,
     comienzos legítimos iguales a los de una estafa), que es lo que corrige un ajuste fino. Necesita datos aparte del
     desarrollo y de la reserva.
   - **Leer el token con C (`c-digito`),** solo si el equipo quiere un punto entre 9 y 27 FA. C no escribe nada entre
     0,3 y 0,4, y en el 0,3 hay 21 estafas y 18 legítimas.

**Para la capa de hallazgos** (la lleva la sesión principal):
- un hallazgo nuevo: con un prompt que mira la intención, el SLM avisa antes y avisa estafas sin pedido, y la FA se
  muda al comienzo de las llamadas legítimas de seguridad;
- otro: dentro del alcance, las FA de v4 son pedidos de DNI (45 % de FA);
- revisar H03 y H05 a la luz de esto.

## Otras cifras (solo para mirar)

- **Reglas del laboratorio, sin modelo, dentro del alcance:**
  - v1: 42/46, 27/36 y 69/94 FA;
  - v2: 11/46, 3/36 y 36/94.
- **Estafas sin pedido avisadas en el punto de comparación:** v4 1/10, C 9/10, reglas v1 8/10 y v2 0/10.
- **Las 6 estafas que piden un dato de identificación:** C avisa 5 (3 antes del pedido) y v4 4 (una después del
  pedido). `PREMIO-003` no la avisa nadie.
- **Las 7 legítimas de corpus_v2 dentro del alcance:** 0 FA con los tres prompts.
- **Manuales:**

  | | v4 | C |
  |---|---|---|
  | laboratorio | 16/16, 8/16 antes y 5/10 FA | 16/16, 15/16 antes y 8/10 FA |
  | piloto escrito | 7/7, 4/7 y 3/7 | 7/7, 6/7 y 3/7 |
  | trampa | 5/6, 3/5 y 5/7 | 5/6, 4/5 y 4/7 |

- **Segunda consulta en T4:**
  - v4, 704 / 909 ms en 70 líneas, con 2 fallos;
  - C, 690 / 847 ms en 24 líneas, sin fallos;
  - `v4-premisa`, 718 / 934 ms en 68 líneas, con 1 fallo.
- **La curva entera** está en `curva.csv` y en `analisis-salida.md`.
