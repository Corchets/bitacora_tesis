# Análisis — Tito viejo → Gemma 4 E2B sobre las 150 conversaciones de desarrollo

- **Fecha del análisis:** 2026-11-04
- **Corrida:** `2026-11-04_003715_e2b-tito-viejo-150` (inicio 2026-11-04T00:37:15, fin 00:46:04, sin interrupciones). Tablas caso por caso en [`resumen.md`](resumen.md); datos crudos en [`actualizaciones.csv`](actualizaciones.csv) y [`manifiesto.json`](manifiesto.json).
- **Configuración:** la del [ADR 0001](../../../../docs/ingenieria/adr/0001-parakeet-filtro-y-gemma4-e2b-con-tito-viejo.md). Tito viejo (RoBERTuito congelado + `tito_logreg.json`, frase aislada, umbral 0,5) como compuerta de `gemma4:e2b-it-q4_K_M`, prompt `tarea`, hablantes `ab`, `num_ctx` 4096, seed 42, temperatura 0, timeout 120 s, aviso único (`operativo-hasta-aviso`). Ollama 0.40.14.
- **Datos:** partición `desarrollo`, 150 conversaciones escritas: 75 vishing, 51 legítimas y 24 legítimas difíciles, 2.773 líneas. Las 150 están **sin revisión humana**: tanto los casos como `T_R` y `T_C` son referencias de trabajo.
- **Código:** commit `833a3fb` de `laboratorio-main`.

> **Límites de esta medición.** Son datos de desarrollo, sin revisión humana, y no estiman el rendimiento en el test reservado ([D08](../../../../docs/gestion/MAPA-DECISIONES.md)). Este análisis no ajusta umbrales ni prompt: solo describe.

## Cómo se corrió (dejar constancia)

1. **Solo Tito→E2B y reglas.** La corrida se lanzó con un wrapper externo, `solo_tito_slm.py`, guardado fuera del repo. El wrapper llama a `correr.main` con el comando base y reemplaza en memoria `correr.procesar_caso` para que el detector SLM directo (`slm|gemma4:e2b-it-q4_K_M|tarea|ab`) no procese ninguna línea. Al terminar, saca esa configuración del manifiesto y agrega el campo `nota_wrapper`. **No se modificó código del repo.** El campo `comando` del manifiesto muestra `python correr.py …` porque así lo registra `correr.main`.
2. **Máquina:** la PC Windows del equipo (Windows 11, AMD Ryzen familia 25 modelo 33 con 12 núcleos lógicos, 31,9 GB de RAM, Python 3.12.10). Ollama informa el modelo entero en VRAM (`size_vram_bytes = size_bytes`), así que **muy probablemente corrió en GPU**. El manifiesto no registra qué placa. **No es el teléfono de referencia ni la M1 de 8 GB, y tampoco la CPU de un contenedor:** las latencias de abajo no se trasladan al teléfono.
3. **Finales de línea de Windows.** El manifiesto marca `cambios_sin_commit_en_la_carpeta: true` y el SHA-256 del artefacto (`2fcf65d7…`) difiere del de `tito_logreg.json` en el repo (`fb601eaa…`). Se verificó que la única diferencia es CRLF: el SHA del archivo del repo convertido a CRLF es exactamente `2fcf65d7…`. Las huellas de los 150 casos y del prompt `tarea` (`bf4284996898c45d`) coinciden con el repo, y antes de correr se restauraron los casos con LF para que pasara el control SHA-256 de la reserva.
4. Cargar E2B tardó 86,2 s, y preparar el encoder de Tito 65,5 s (descarga incluida). Las dos cosas pasan una sola vez por proceso y no entran en las latencias por consulta.

## Resultado principal

| Configuración | Estafas con aviso (sobre 75) | Falsas alarmas (sobre 75) | Legítimas | Legítimas difíciles | Fallos |
|---|---|---|---|---|---|
| **Tito viejo → E2B** | **51/75 (68,0 %)** | **13/75 (17,3 %)** | 5/51 (9,8 %) | 8/24 (33,3 %) | 0/2.318 |
| Reglas v1 | 65/75 (86,7 %) | 51/75 (68,0 %) | 37/51 (72,5 %) | 14/24 (58,3 %) | 0/1.319 |
| Meta del tutor | 80–85 % | 10–15 % | | | |

- **Ninguna configuración cumple la meta.** Tito→E2B queda 12–17 puntos por debajo en estafas y 2,3 puntos por encima del techo de falsas alarmas. Reglas detecta más estafas pero dispara en dos de cada tres legítimas.
- **11 de las 75 estafas no tienen pedido crítico** (`T_R` vacío, dificultad `sin_pedido`): la llamada se corta antes del pedido. E2B no avisó en ninguna (0/11). Contando solo las 64 estafas con pedido, avisó en **51/64 (79,7 %)**, justo debajo del piso de 80 %. Qué se exige en las estafas sin pedido es una decisión abierta de D08, y este análisis no la resuelve.
- **Fallos de JSON y timeouts:** ninguno. Las 1.179 consultas al SLM devolvieron JSON válido, sin timeouts y sin fallos técnicos de Tito. El prompt más largo tuvo 1.287 tokens, lejos del `num_ctx` de 4.096.
- **Evidencia textual:** 62 de los 64 avisos citan texto presente en la conversación disponible.

## Momento del aviso respecto del pedido peligroso

Avisos en estafas con `T_R` de referencia (`casos/referencia/`):

| Momento | Tito→E2B | Reglas |
|---|---|---|
| Antes del pedido (`< T_R`) | 17 | 32 |
| En la línea del pedido (`= T_R`) | 29 | 20 |
| Después del pedido, antes del cumplimiento | 4 | 5 |
| En o después del cumplimiento (`≥ T_C`) | 1 | 0 |
| Estafa sin `T_R` con aviso | 0 | 8 |
| **Total** | **51** | **65** |

- 46 de los 51 avisos de E2B (90 %) llegan antes del pedido o en la misma línea.
- Los cuatro tardíos llegan entre 1 y 3 líneas después del pedido: `CV2-D-V-FAMILIAR-001` (L16, T_R 15), `CV2-D-V-FAMILIAR-003` (L17, T_R 15), `CV2-D-V-SOPORTE-003` (L14, T_R 11) y `CV2-D-V-SOPORTE-004` (L17, T_R 14). Ninguno llega al cumplimiento.
- El único aviso en el cumplimiento es `TR-04-pedido-tras-charla-larga`: aviso en L27 con T_R 26 y T_C 27.
- Los avisos «antes» se apoyan en presión, amenaza o suplantación («te vacian la cuenta», «te llamo del área de seguridad del banco»), no en un pedido. En `LAB-*`, `SC-*` y `TR-09/10` llegan 1 a 2 líneas antes del pedido. En `CV2-D-V-BANCO-010` (L1, T_R 13) y `CV2-D-V-BANCO-005` (L5, T_R 19) llegan mucho antes.

## Compuerta de Tito

Mecánica: Tito puntúa cada línea hasta superar 0,5. Desde ahí el SLM queda activo en todas las líneas siguientes (activación persistente, `filtro_tito.py`) y Tito deja de puntuar.

- **Conversaciones donde Tito activó al SLM:** 128/150. Por clase: 74/75 vishing, 33/51 legítimas y 21/24 legítimas difíciles. En 35 conversaciones activó ya en la línea 1. La mediana de activación cae al 25 % de la conversación.
- **Líneas:** con aviso único se procesaron 2.318 de las 2.773 líneas. Tito puntuó 1.267, y **1.179 pasaron al SLM (50,9 % de las procesadas)**; 1.139 se resolvieron sin consultar. Por clase, el SLM se consultó en 580 de 966 líneas de vishing, 521 de 1.170 de legítimas y 78 de 182 de legítimas difíciles.
- **Tito como causa de pérdida:** de las 64 estafas con pedido, Tito activó al SLM antes del pedido o en el pedido en 62.
  - `CV2-D-V-PREMIO-001`: Tito nunca activó (máximo 0,23 en L6; el pedido de L10, «El DNI completo y una foto del frente…», puntuó 0,024). Es la **única estafa perdida por la compuerta**.
  - `CV2-D-V-ORGANISMO_PREVISIONAL-003`: Tito activó en L13, dos líneas después del pedido (L11, puntaje 0,128), y E2B tampoco avisó después.
  - Las otras 22 estafas perdidas **sí pasaron la compuerta**: el que no avisó fue el SLM.
- Como filtro de costo, la compuerta ahorra poco en este corpus: activa en el 44 % de las conversaciones legítimas y en el 88 % de las legítimas difíciles, en general temprano.

## Latencia

PC Windows con GPU probable; no es el teléfono ni la M1. Tiempos en milisegundos por actualización.

| Medida | n | Mediana | p90 | p95 | Máximo |
|---|---|---|---|---|---|
| Consulta a E2B (`slm_ms`) | 1.179 | 309 | 390 | 512 | 913 |
| Línea con consulta (Tito + SLM) | 1.179 | 309 | 416 | | |
| Tito por línea puntuada (`tito_ms`) | 1.267 | 26,9 | 31,3 | | 41,8 |
| Reglas por línea | 1.319 | 7 | | 14 (p95) | |

Como referencia, el ADR registra una mediana de 3,74 s por consulta de E2B en la M1 de 8 GB: unas 12 veces más que acá. El criterio de 2 s de #84 no se puede evaluar con esta máquina.

## Desglose por grupo

| Grupo | Estafas Tito→E2B | FA Tito→E2B | Estafas reglas | FA reglas |
|---|---|---|---|---|
| corpus_v2 (97) | 24/46 (52,2 %) | 5/51 (9,8 %) | 42/46 (91,3 %) | 37/51 (72,5 %) |
| laboratorio (26) | 16/16 (100 %) | 3/10 (30,0 %) | 13/16 (81,2 %) | 1/10 (10,0 %) |
| piloto_escrito (14) | 7/7 (100 %) | 1/7 (14,3 %) | 6/7 (85,7 %) | 7/7 (100 %) |
| trampa (13) | 4/6 (66,7 %) | 4/7 (57,1 %) | 4/6 (66,7 %) | 6/7 (85,7 %) |

Lo más importante de la corrida: **en los grupos viejos (laboratorio y piloto), E2B detecta 23/23 estafas, pero en `corpus_v2` cae a 24/46.** Las 20 conversaciones con las que se eligió la configuración (#101, 10/10 estafas y 1/10 falsas alarmas) se parecen a los grupos viejos. `corpus_v2` es más largo (20–38 líneas), con pedidos indirectos o condicionales y 10 estafas sin pedido. Es la señal de que la evidencia del ADR era optimista, como el propio ADR advierte.

## Desglose por escenario (familias de `corpus_v2`)

| Escenario | Estafas Tito→E2B | FA Tito→E2B | Estafas reglas | FA reglas |
|---|---|---|---|---|
| banco | 9/12 | 3/10 | 12/12 | 10/10 |
| whatsapp | 5/8 | 0/5 | 7/8 | 4/5 |
| soporte | 4/8 | 0/5 | 8/8 | 5/5 |
| familiar | 3/6 | 2/5 | 5/6 | 3/5 |
| organismo_previsional | 2/6 | 0/3 | 6/6 | 2/3 |
| premio | 1/6 | 0/3 | 4/6 | 3/3 |
| delivery | — | 0/5 | — | 3/5 |
| escuela | — | 0/5 | — | 2/5 |
| medico | — | 0/5 | — | 4/5 |
| trabajo | — | 0/5 | — | 1/5 |

En las legítimas de `corpus_v2`, E2B tiene **0 falsas alarmas fuera de banco y familiar**. Las peores familias en estafas son premio (1/6) y organismo previsional (2/6). Ahí el pedido es de datos de identidad (DNI, documento, «últimos cuatro y la fecha de emisión») o de un pago presentado como trámite, y E2B lo trata como administrativo.

## Estafas perdidas (24)

Ninguna de las 24 tuvo `alerta_sugerida` en alguna consulta, así que el modelo no dejó motivo de aviso. Se informa el riesgo máximo que devolvió E2B en la conversación; el riesgo no está calibrado.

**Con pedido (13):**

| Caso | T_R | Texto del pedido (recortado) | Tito | Riesgo máx. E2B |
|---|---|---|---|---|
| `CV2-D-V-BANCO-003` | L19 | «Todo lo que tengas de esa numeración prepará el sobre y entregáselo al operador» | activó L5 | 0,5 (L14) |
| `CV2-D-V-FAMILIAR-004` | L22 | «Si ahora apareciera esa diferencia en mi cuenta, podría arreglárselo yo…» | activó L14 | 0,3 |
| `CV2-D-V-FAMILIAR-005` | L20 | «Si alguien pudiera comprarlo por internet ahora, te lo devuelvo…» | activó L18 | 0,3 |
| `CV2-D-V-FAMILIAR-006` | L22 | «Si podés cubrir la seña ahora, te la devuelvo…» | activó L17 | 0,2 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-003` | L11 | «…me faltan los dígitos del…» | **activó L13, tarde** (0,128 en T_R) | 0,5 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-004` | L14 | «Decime los últimos cuatro y la fecha de emisión que figura abajo» | activó L2 | 0,5 |
| `CV2-D-V-PREMIO-001` | L10 | «El DNI completo y una foto del frente para cargarlo en el acta.» | **nunca activó** (máx. 0,23) | — |
| `CV2-D-V-PREMIO-002` | L13 | «Dos mil setecientos se abona por transferencia a la cuenta de producción» | activó L3 | 0,3 |
| `CV2-D-V-PREMIO-003` | L13 | «El número de documento. Si queda vacío, el kit vuelve al listado…» | activó L3 | 0,1 |
| `CV2-D-V-SOPORTE-001` | L14 | «Ingresá los datos con los que entrás normalmente…» | activó L12 | 0,5 |
| `CV2-D-V-SOPORTE-005` | L16 | «La anterior, así recupera el permiso…» (contraseña anterior) | activó L10 | 0,3 |
| `CV2-D-V-WHATSAPP-004` | L13 | «No, pasámelo por acá y lo pongo en la planilla de altas.» | activó L5 | 0,5 |
| `TR-01-pedido-indirecto-digitos` | L8 | «Abrilo y leeme lo que dice, de a uno, despacito…» | activó L3 | 0,5 |

Patrón: son pedidos **indirectos o condicionales** («si alguien pudiera…», «leeme lo que dice», «pasámelo por acá»), pedidos de datos de identidad o pagos presentados como trámite. El riesgo de E2B se queda en 0,1–0,5 sin sugerir alerta. Todos los avisos de la corrida tuvieron riesgo ≥ 0,5 salvo dos (0,3 y 0,4), y en las consultas sin alerta hubo 146 respuestas con riesgo 0,5.

**Sin pedido (11):** `CV2-D-V-BANCO-011`, `-BANCO-012`, `-ORGANISMO_PREVISIONAL-005`, `-ORGANISMO_PREVISIONAL-006`, `-PREMIO-005`, `-PREMIO-006`, `-SOPORTE-007`, `-SOPORTE-008`, `-WHATSAPP-007`, `-WHATSAPP-008` y `TR-12-corta-antes-del-pedido`. Tienen presión, aislamiento o suplantación, pero la llamada termina antes de cualquier pedido crítico. E2B dio riesgo máximo de 0,3 a 0,6 y no avisó. Que esto cuente como pérdida depende de la política de alerta de D08.

## Falsas alarmas (13)

| Caso | Clase | Grupo | Línea | Texto | Motivo del modelo |
|---|---|---|---|---|---|
| `CV2-D-L-BANCO-002` | legítima | corpus_v2 | L7 | «…decime los últimos cuatro dígitos» | «Te están pidiendo los últimos cuatro dígitos de tu cuenta para identificarla.» |
| `CV2-D-L-BANCO-005` | legítima | corpus_v2 | L8 | «…me confirmás los últimos cuatro dígitos, por favor.» | «No compartas los últimos cuatro dígitos de tu cuenta…» |
| `CV2-D-L-BANCO-010` | legítima | corpus_v2 | L10 | «para ubicarla confirmame los últimos cuatro números de esa cuenta» | «Te están pidiendo los últimos cuatro números de una cuenta bancaria…» |
| `CV2-D-L-FAMILIAR-002` | legítima | corpus_v2 | L11 | «Pasame el alias por mensaje…» | «…puede ser una forma de obtener acceso a alguna cuenta o servicio.» |
| `CV2-D-L-FAMILIAR-005` | legítima | corpus_v2 | L10 | «Poné esos 15.000; yo pongo 19.000…» | «Te están pidiendo que transfieras dinero.» |
| `LAB-arca-canal-oficial` | difícil | laboratorio | L3 | «la unica via es entrar vos a la pagina oficial» | «…ingresar a una página web para resolver un supuesto embargo.» |
| `LAB-banco-revisa-app` | difícil | laboratorio | L3 | «corta esta comunicacion y entra vos a la aplicacion oficial» | «…cortes la comunicación y accedas a una aplicación oficial, … táctica común para engañarte.» |
| `LAB-no-bajes-nada` | difícil | laboratorio | L4 | «bien» (cita L: «me llamaron para que baje un programa…») | «Te están pidiendo que descargues un programa…» |
| `LG-BANK-VERIF-01-e01` | difícil | piloto_escrito | L6 | «¿Querés que te diga los últimos números de la tarjeta…?» | «No le des los números de tu tarjeta a nadie por teléfono.» |
| `TR-06-banco-alerta-legitima` | difícil | trampa | L10 | «Hace un rato me llegó un mensaje con un código. ¿Te lo paso…?» | «Te están pidiendo que compartas un código…» |
| `TR-08-frase-cortada-candado` | difícil | trampa | L3 | «Pasame el código» | «Te están pidiendo un código que te pertenece.» |
| `TR-11-familiar-real-pide-plata` | difícil | trampa | L9 | «Dale, te corto y te llamo.» (cita el pedido de transferencia previo) | «Te están pidiendo realizar una transferencia de dinero…» |
| `TR-13-turno-medico-pide-dni` | difícil | trampa | L5 | «Decime tu número de documento y la fecha de nacimiento…» | «Te están pidiendo tu número de documento y fecha de nacimiento.» |

Patrones:
1. **Datos parciales de identificación en el banco** (últimos cuatro dígitos): tres legítimas de `corpus_v2` y una difícil.
2. **Consejos de seguridad leídos como ataque:** «entrá vos a la app oficial», «no bajes nada». Son los tres `LAB-*`, que justamente prueban eso.
3. **Frases sueltas** («Pasame el código», que pide el propio usuario o un familiar), de las que la meta del tutor pide no saltar.
4. **Pedidos de plata entre familiares.**

Hay una tensión directa con las pérdidas: E2B avisa por «últimos cuatro dígitos» en legítimas de banco y no avisa por «últimos cuatro y la fecha de emisión» en `ORGANISMO_PREVISIONAL-004`. No usa el contexto de forma consistente.

## Comparación con la evidencia previa y con la meta

| Fuente | Estafas | Falsas alarmas |
|---|---|---|
| #101, 20 conversaciones (ADR 0001) | 10/10 | 1/10 |
| Esta corrida, 150 conversaciones | 51/75 (68,0 %); 51/64 con pedido (79,7 %) | 13/75 (17,3 %) |
| Meta del tutor | 80–85 % | 10–15 % |

La configuración elegida **no alcanza la meta en el conjunto de desarrollo ampliado**. Si las estafas sin pedido no se exigen, queda al borde en detección (79,7 %) pero sigue arriba en falsas alarmas (17,3 %). El problema principal no es la compuerta, que solo perdió 1 estafa de 64, sino la decisión de E2B ante pedidos indirectos y su sensibilidad a frases de identificación de rutina. El ADR dice que se reconsidera si el test reservado queda lejos de la meta. Esto no es el test reservado, pero adelanta ese riesgo.

## Qué no dice este análisis

- No es el test reservado y no congela política (D08) ni detector (D09).
- No hay revisión humana de casos ni de `T_R`/`T_C`. Una pérdida puede deberse a una referencia discutible: por ejemplo, en `FAMILIAR-004/005/006` los «pedidos» son condicionales.
- No mide la condición SLM directo: se salteó a propósito, por costo, con el wrapper descripto arriba.
- Las latencias son de una PC de escritorio con GPU probable, no del teléfono ni de la M1.
- No se probó ningún ajuste de prompt ni de umbral. Ajustar sobre estos mismos 150 casos contaminaría la selección.
