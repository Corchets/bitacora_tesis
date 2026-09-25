# Casos de prueba del spike (texto)

Guiones **inventados** para correr el modo `--texto` del laboratorio. Una línea es un turno. Las líneas `#` se ignoran.

No son el corpus, no son fichas de rol y no entran en [CATALOGO-ESCENARIOS.csv](../../../docs/datos-etica/CATALOGO-ESCENARIOS.csv). Las fuentes oficiales justifican la modalidad; el diálogo lo escribimos nosotros, con datos ficticios. Consulta de las páginas: **2026-09-23**.

> **Estado: propuesta sin discutir.** No cierra D09 ni D07.
>
> **Pivote 2026-09-25:** el detector activo es LLM/SLM local. Las pasadas 1–23 abajo
> documentan el stub TF–IDF **histórico** (ya eliminado); no son el camino actual.

## Cómo correr uno

Desde `experiments/laboratorio`, con la imagen ya construida después de este cambio:

```bash
WAV=/tmp/nada.wav docker compose run --rm corrida --texto /app/casos/vishing/banco-codigo.txt
```

`nada.wav` tiene que existir como archivo vacío. El contenedor copia esta carpeta al construir la imagen: si el guion es nuevo, `docker compose build` antes.

## Chequeo completo (oracle)

[chequear_casos.py](../chequear_casos.py) corre los 21 guiones + `ejemplo.txt` y falla (exit 1) si el **incendio** (reglas) no coincide. Tras el pivote LLM (2026-09-25), el **goteo** no se fija en el oracle hasta tener `LLM_BASE_URL` y corridas documentadas en #29.

## Qué hay

| Archivo | Clase | Modalidad publicada | Incendio que busca el guion |
|---|---|---|---|
| [vishing/banco-codigo.txt](vishing/banco-codigo.txt) | vishing | Compra o verificación y pedido de código | `REQUEST_AUTH_CODE` |
| [vishing/whatsapp-codigo.txt](vishing/whatsapp-codigo.txt) | vishing | Código para activar WhatsApp en otro teléfono | `REQUEST_AUTH_CODE` |
| [vishing/acceso-remoto.txt](vishing/acceso-remoto.txt) | vishing | Llamado de un supuesto banco y programa de acceso remoto | `REQUEST_REMOTE_ACCESS` |
| [vishing/anses-beneficio.txt](vishing/anses-beneficio.txt) | vishing | Beneficio a cambio de clave o dato bancario | `REQUEST_SECRET`, `REQUEST_TRANSFER` |
| [vishing/arca-deuda.txt](vishing/arca-deuda.txt) | vishing | Deuda o embargo. El aviso oficial es por correo; el teléfono es transposición de prueba | `REQUEST_SECRET`, `REQUEST_TRANSFER` |
| [vishing/familiar-peligro.txt](vishing/familiar-peligro.txt) | vishing | Familiar en peligro y pedido de sacar dinero | `REQUEST_TRANSFER` |
| [legitima/banco-revisa-app.txt](legitima/banco-revisa-app.txt) | legítima difícil | Mismo tema banco, sin pedido | ninguno |
| [legitima/mensajeria-no-pases-nada.txt](legitima/mensajeria-no-pases-nada.txt) | legítima difícil | Mismo tema mensajería, sin pedido | ninguno |
| [legitima/no-bajes-nada.txt](legitima/no-bajes-nada.txt) | legítima difícil | Mismo tema celular, sin pedido | ninguno |
| [legitima/anses-canal-oficial.txt](legitima/anses-canal-oficial.txt) | legítima difícil | Mismo tema organismo, sin pedido | ninguno |
| [legitima/arca-canal-oficial.txt](legitima/arca-canal-oficial.txt) | legítima difícil | Mismo tema deuda, sin pedido | ninguno |
| [legitima/familiar-llama-vos.txt](legitima/familiar-llama-vos.txt) | legítima difícil | Mismo tema familiar, sin pedido | ninguno |
| [legitima/banco-niega-el-codigo.txt](legitima/banco-niega-el-codigo.txt) | legítima difícil | Niega el pedido y usa la palabra «codigo» | ninguno |
| [vishing/banco-codigo-parafrasis.txt](vishing/banco-codigo-parafrasis.txt) | vishing (paráfrasis) | Misma modalidad, otra redacción | `REQUEST_AUTH_CODE` t5 + goteo t5 (semilla P16) |
| [vishing/banco-numeros-sin-clave.txt](vishing/banco-numeros-sin-clave.txt) | vishing (paráfrasis) | Pide «seis números», evita «código» | `REQUEST_AUTH_CODE` t5 (patrón P14) + goteo t5 |
| [vishing/acceso-remoto-parafrasis.txt](vishing/acceso-remoto-parafrasis.txt) | vishing (paráfrasis) | Misma modalidad, otra redacción | `REQUEST_REMOTE_ACCESS` t3 + goteo t3 (semilla P15) |
| [vishing/anses-beneficio-parafrasis.txt](vishing/anses-beneficio-parafrasis.txt) | vishing (paráfrasis) | Beneficio por contraseña+alias | `SECRET`+`TRANSFER` t3, `TRANSFER` t5; goteo t5 |
| [vishing/arca-deuda-parafrasis.txt](vishing/arca-deuda-parafrasis.txt) | vishing (paráfrasis) | Intimación y CBU (t4 negado P21) | `TRANSFER` t5 + goteo t5 |
| [vishing/familiar-peligro-parafrasis.txt](vishing/familiar-peligro-parafrasis.txt) | vishing (paráfrasis) | Intermediario y alias (t4 pesos: hueco conservador) | `TRANSFER` t6, goteo t5 |
| [vishing/whatsapp-codigo-parafrasis.txt](vishing/whatsapp-codigo-parafrasis.txt) | vishing (paráfrasis) | Soporte falso y código (t3 con opinión desde P24) | `AUTH_CODE` t3, goteo t2 |
| [legitima/banco-app-parafrasis.txt](legitima/banco-app-parafrasis.txt) | legítima (paráfrasis) | Consejo de cortar y revisar la app | ninguno |

Las legítimas evitan las palabras de [rules.py](../rules.py), salvo `banco-niega-el-codigo.txt`, que existe para ver el falso incendio de esa lista.

## Corrida de texto del 2026-09-23

Modo `--texto`, stub con sin opinión. El incendio marcó lo que dice la tabla de arriba.

Pasada 1 de 5. Antes de la negación, 12 de 13 guiones coincidían con la tabla y `banco-niega-el-codigo.txt` marcaba `REQUEST_AUTH_CODE` en «ningún banco te pide el código». La regla ahora deja ese turno vacío si el texto niega el pedido y no hay imperativo. `no voy a dar la clave` en `arca-deuda.txt` también deja de marcar; el pedido sigue en el turno anterior. El goteo no disparó en ninguno: casi todos los turnos quedan sin opinión (menos de 4 palabras del vocabulario de las semillas) y los tres que puntúan están aislados (`banco-codigo` 0,606, `whatsapp-codigo` 0,585, y la legítima `no-bajes-nada` 0,570).

Pasada 2 de 5. El incendio sigue en 13 de 13. El piso de palabras conocidas pasó de 4 a 2: con 4 el goteo no disparaba; con 1 disparaba en 5 de 7 legítimas. Con 2 dispara en `arca-deuda`, `banco-codigo`, `familiar-peligro` y `whatsapp-codigo`, y en ninguna legítima. Siguen quietos `acceso-remoto` y `anses-beneficio` (un solo turno con opinión). Tres legítimas puntúan alto una sola vez y no llegan a goteo: `banco-niega-el-codigo` 0,562, `mensajeria-no-pases-nada` 0,534, `no-bajes-nada` 0,570. `ejemplo.txt` sigue goteando en el turno 3.

Pasada 3. Dos semillas inventadas de estafa en `semillas.json` (archivo eliminado 2026-09-25 con el stub TF–IDF) («si no instalas el programa…», «si no me pasas el dato…») para dar opinión a los turnos mudos de `acceso-remoto` y `anses-beneficio`. Goteo vishing 6 de 6, legítima 0 de 7, incendio 13 de 13. Efecto lateral: las tres legítimas aisladas subieron (0,582, 0,610, 0,625). `ejemplo.txt` igual (goteo turno 3, incendio 5–6).

Pasada 4. `plata` entra a `REQUEST_TRANSFER` y `no saques` a las negaciones de [rules.py](../rules.py). `familiar-peligro` anticipa el incendio al turno 4 («necesito que saques la plata…», antes turno 6 por `alias`); la legítima pareja («no saques plata ni hables…») sigue muda por la negación. 13 de 13, 6 de 6, 0 de 7. `ejemplo.txt` igual.

Pasada 5. Intento (a), revertido: una semilla legítima con vocabulario nuevo («corto y llamo yo al numero oficial…») dio opinión a turnos legítimos antes mudos y el goteo subió a 3 de 7 legítimas. Intento (b), kept: semilla legítima solo con palabras que ya estaban en el vocabulario («llamo al banco por la tarjeta y el codigo de la aplicacion»). Repondera sin abrir opiniones nuevas: las legítimas bajan a 0,482, 0,531 y 0,503; vishing sigue 6 de 6 (`banco-codigo` t1 cae a 0,484 bajo el umbral, el goteo lo sostienen t3/t5). 13 de 13, 6 de 6, 0 de 7. `ejemplo.txt` igual.

Pasada 6. `banco` pasa a [palabras vacías](../detector.py): aparece en ambas clases (saludo del estafador y consejo legítimo de llamar al banco) y no discrimina. `banco-niega-el-codigo` t1 queda sin opinión (era 0,503); ningún otro caso cambia de estado. 13 de 13, 6 de 6, 0 de 7. `ejemplo.txt` igual.

Pasada 7. Semilla legítima «reviso el numero de atras de la tarjeta» para disputar `atras`/`tarjeta`. Todas las opiniones legítimas quedan bajo el umbral (0,456, 0,435 y una nueva en `familiar-llama-vos` t3 de 0,491, aislada, por la palabra nueva `numero` + `tenes`). Vishing sigue 6 de 6 pero con menos margen (altos iniciales en 0,505–0,545). Tradeoff documentado: si el equipo prefiere margen del lado vishing, revertir esta semilla vuelve al estado de pasada 6 sin tocar lo demás. 13 de 13, 6 de 6, 0 de 7. `ejemplo.txt` igual (goteo turno 3, incendio 5–6).

Hallazgo sin tocar (candidato a issue, roza el recorte de grilling k=3 y D08): el contador dispara con un turno alto + cualquier siguiente turno con opinión, aunque el segundo puntúe bajo, porque el máximo de la ventana sostiene el estado «alto». La histéresis real es más permisiva que «dos actualizaciones altas seguidas». No se cambió en esta serie.

Pasada 8. Fidelidad de `T_R`: `whatsapp` sale de `REQUEST_AUTH_CODE` en [rules.py](../rules.py). El saludo t1 («soy del soporte…») marcaba incendio dos turnos antes del pedido real (t3, «pasamelo»); `T_R` es inicio del pedido ([METRICAS.md](../../../docs/evaluacion/METRICAS.md)), así que t1 inflaba `L_R`. Ahora el incendio entra en t3. La expectativa se fijó primero en [chequear_casos.py](../chequear_casos.py) (falló en t1), después se tocó la regla. 13 de 13 + ejemplo en verde.

Pasada 9. `tenes` pasa a palabras vacías: solo estaba en `familiar-llama-vos` t3, `ejemplo` t3 y una semilla. Ese t3 (0,491) queda sin opinión; `ejemplo` t3 conserva 3 palabras y el goteo en t3. Resto idéntico. 13 de 13 + ejemplo en verde.

Pasada 10. `aplicacion` pasa a palabras vacías: está en semillas de ambas clases y en ningún caso vishing. `mensajeria-no-pases-nada` queda totalmente muda; última opinión legítima: `no-bajes-nada` t3 0,429. 13 de 13 + ejemplo en verde.

Pasada 11. `tiene` pasa a palabras vacías: solo estaba en `arca-deuda` t3 y una semilla legítima. Ese turno sube 0,547 → 0,582; todo lo demás idéntico. 13 de 13 + ejemplo en verde.

Pasada 12. Intento (a), revertido: semilla legítima «paso el numero de la tarjeta por la puerta» (técnica P5b) bajaba `no-bajes` a 0,389 pero empujaba 3 aperturas vishing bajo el umbral y atrasaba goteos. Intento (b), revertido: `llamo` a vacías subía `no-bajes` 0,429 → 0,444 (la palabra pesaba legítimo: 2 semillas contra 1). Intento (c), kept, de otra clase: el oracle no vigilaba turnos de goteo y (a) había pasado en verde; [pipeline.py](../pipeline.py) ahora expone `turno_goteo` y [chequear_casos.py](../chequear_casos.py) fija los seis (banco 5, whatsapp 3, acceso 3, anses 3, arca 5, familiar 6). Verificado: con las semillas de (a) el oracle falla en 3 turnos (whatsapp t4, acceso t5, anses t5). 13 de 13 + ejemplo en verde.

Lectura de la serie 8–12: el stub tocó un óptimo local para su tamaño. Los ajustes de una palabra ya arbitran margen entre clases en vez de crearlo (P12 lo muestra dos veces). Lo que sigue pide decisiones, no más tweaks: semántica de histéresis (hallazgo de arriba, D08) o taxonomía (D07).

## Sondas de otro tipo (2026-09-23, solo medición)

(A) Barrido umbral × piso de palabras: con piso 2, umbral 0,3–0,5 da idéntico 6/6 + 0/7 (el umbral casi no importa, manda la histéresis); ningún puntaje pasa 0,6 en ningún caso, así que umbral ≥ 0,6 apaga todo el goteo. Piso 1 mete 2–4 legítimas, piso 3 voltea 2 vishing. (B) Perturbaciones: mayúsculas, tildes y muletillas intactas (13/13); typo (1 swap/turno, seed 42) volteó 3 incendios (abajo, P13). (C) 4 paráfrasis inéditas: ningún vishing escapó a ambos brazos (reglas agarró 2, goteo 1, uno cada uno), pero cada brazo falló algo: reglas no ve «seis números» y el goteo queda en opinión única si la paráfrasis mata palabras backup. Las 4 se promovieron a la tabla de arriba como regresión anti-overfit.

Pasada 13. Negaciones y patrones de 6+ letras toleran un typo en [rules.py](../rules.py) (Damerau: letra cambiada, agregada, quitada o swap; un swap es distancia Levenshtein 2, por eso no bastaba distancia 1). Repara los 3 de la sonda B: `saquse`/`inngun` vuelven a negar, `autorizar` typo vuelve a prender. Limpio 17/17 + typos 17/17 (seeds 42, 1 y 7). Límite conocido: keywords cortas (`clave`, `plata`, `alias`, …) quedan exactas a propósito —con fuzzy, `llave` prendería `clave` y `plato` prendería `plata`— y un typo ahí puede silenciar (seed 123 pierde 3 coberturas vishing por esa vía). Bajar el piso pide datos fuera de muestra (D07).

Pasada 14. `numeros` entra a `REQUEST_AUTH_CODE` como patrón solo-exacto (`_SOLO_EXACTO` en [rules.py](../rules.py)): con fuzzy, `numero` (legítimo, `no-bajes` t3) lo prendería. Cierra el hueco de `banco-numeros-sin-clave`, que ahora prende t5 por ambos brazos. Ningún otro caso cambia. 17/17 + ejemplo + typos en verde.

Pasada 15. Semilla estafa «te llamo por un cobro duplicado de ayer» (palabras nuevas solo en vishing; sin `tarjeta` para no empujar `no-bajes`). `acceso-remoto-parafrasis` t1 gana opinión (0,578) y gotea t3; el lado vishing sube en bloque. `no-bajes` 0,429 → 0,461 (vía `llamo`, aislada, bajo umbral). 17/17 + ejemplo + typos en verde.

Pasada 16. Semilla estafa «vimos un gasto raro en la cuenta» (era 50/50: `hola` pesa legítimo). `banco-codigo-parafrasis` t1 da 0,577 y gotea t5; los 9 vishing ya prenden ambos brazos. `no-bajes` sube a 0,474 —tendencia vigilada (P17). 17/17 + ejemplo + typos en verde.

Pasada 17 (harness). El oracle fija el margen: toda opinión legítima bajo 0,5 (hoy máx 0,474). Nadie lo vigilaba y cada semilla E lo erosiona ~0,015.

Pasada 18 (harness + fix). Al fijar perturbaciones, tildes volteaba el goteo de `banco-codigo-parafrasis` (t5 pierde `codigo`): el detector no plegaba tildes como rules. [detector.py](../detector.py) ahora pliega en train y score (cero cambios en limpio); el oracle fija upper/tildes/muletilla 17/17 idénticos por el pipeline real.

Pasada 19. Semilla legítima «llamo por el numero de la tarjeta» (técnica P5b: solo vocabulario existente, cero opiniones nuevas). Reconstruye margen: `no-bajes` t3 0,474 → 0,403; vishing intacto. 17/17 + ejemplo + typos + margen + robusto en verde.

Pasada 20 (sonda). 3 paráfrasis inéditas (anses/arca/familiar) con predicción previa: incendio 3/3, goteo 0/3 —las 3 gotearon igual (subestimé el vocabulario E nuevo: `hoy`, `frenar`, `puedo`+`rapido`). Confirmó la verruga PV4-t4 («no pienso pagar nada» prendía `TRANSFER`) y un hueco conservador nuevo (t4 «diez mil pesos» no prende; marca tarde, no temprano —dirección segura, se deja).

Pasada 21. `no pienso` a negaciones: PV4-t4 mudo, `T_R` al t5 real. Ningún caso limpio cambia. 17/17 + ejemplo + typos + margen + robusto en verde.

Pasada 22. Las 3 paráfrasis a la suite (20 casos; typos/margen/robusto las cubren automático). Comportamiento fijado: PV3 inc t3+t5/goteo t5, PV4 t5/t5, PV5 inc t6/goteo t5 (goteo antes que incendio).

Pasada 23 (medición, sin cambio). Re-barrido tras crecer semillas (E 8→12, L 8→11): el punto (piso 2, umbral 0,3–0,5) sigue 12/12 + 0/8; el techo de confianza subió (umbral 0,6 prende 7/12, antes 0/6). No se fija en el oracle: la insensibilidad al umbral es verruga del stub, no virtud a congelar.

Sonda D (2026-09-23). 2 guiones: whatsapp-paráfrasis (inc t3/goteo t2 —goteo antes que incendio—; t3 muda porque `verificacion` no estaba en vocabulario → P24) y portero-legítima («el portero me pasó el código de la puerta»: incendio FALSO en t1 + t2 0,532 a un turno del goteo). El portero no entra a la suite verde: keyword ≠ pedido es semántica de taxonomía (D07), evidencia para esa decisión, no tweak de spike.

Pasada 24 (TDD: rojo t3-sin-opinión → verde). Semilla estafa «te mandamos el codigo de verificacion por mensaje» (palabras nuevas ausentes en legítimas). PV6-t3 None → 0,612; suite intacta, margen 0,403 → 0,411.

Pasada 25. Whatsapp-paráfrasis a la suite (21 casos; inc t3, goteo t2). Última modalidad sin paráfrasis cubierta.

## Fuentes

- Ministerio de Justicia, «¿Qué hago si me piden mis datos personales por teléfono?», información actualizada en junio de 2026. <https://www.argentina.gob.ar/justicia/convosenlaweb/situaciones/que-hago-si-me-piden-datos-personales-por-telefono>
- BCRA, «Recomendaciones del BCRA para evitar estafas virtuales», 6 de agosto de 2025. <https://www.bcra.gob.ar/noticias/recomendaciones-del-bcra-para-evitar-estafas-virtuales/>
- UFECI, informe de gestión 2024, nota del 30 de junio de 2025. <https://www.fiscales.gob.ar/ciberdelincuencia/la-unidad-fiscal-especializada-en-ciberdelincuencia-informa-que-en-2024-se-registro-un-aumento-interanual-del-211-en-la-cantidad-de-reportes-de-delitos-informaticos/>
- ARCA, «Alerta: estafas por correo electrónico», 19 de junio de 2025. <https://servicioscf.afip.gob.ar/publico/sitio/contenido/novedad/ver.aspx?id=4671>
- ANSES, «ANSES no se comunica para solicitar datos personales o información bancaria». <https://www.anses.gob.ar/noticias/anses-no-se-comunica-para-solicitar-datos-personales-o-informacion-bancaria> El extracto público dice que no pide datos, claves ni información bancaria por teléfono. La página no devolvió fecha de publicación en la consulta.
