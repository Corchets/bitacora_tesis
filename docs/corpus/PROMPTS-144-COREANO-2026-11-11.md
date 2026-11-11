# Prompts de la traducción y el pre-marcado del coreano (#144, 2026-11-11)

Registro de [#144](https://github.com/Corchets/bitacora_tesis/issues/144): el modelo, el prompt y el
reparto de las dos tareas delegadas a agentes para el [set coreano](RELEVAMIENTO-CORPUS-EXTERNO.md#8-set-coreano-congelado-2026-11-11).
No contiene texto de las llamadas ni marcas.

| | Traducción | Pre-marcado |
|---|---|---|
| Casos | KO-13 a KO-33 (21 llamadas, 5204 segmentos) | KO-10 a KO-33 (24 llamadas) |
| Agente | Codex, `gpt-6.1-sol`, esfuerzo `medium`, 6 workers coordinados con Orca | ídem |
| Verificación | Claude (Opus 5.5): un ítem por segmento, en orden, y el SHA-256 de la fuente en cada archivo | Claude (Opus 5.5): segmentos existentes, `T_R` en el estafador, `T_C` en la víctima |
| Salida | `data/private/issue-144/tanda3/KO-NN.es.md`, unida en `ISSUE-144-COREANO-TRADUCCION-3-2026-11-11.md` (fuera de Git) | `data/private/issue-144/tanda3/premarcado/KO-NN.json` (fuera de Git) |

Reparto. Traducción: KO-13, 25, 26, 33 y 22 · KO-20, 15 y 18 · KO-31, 14 y 28 · KO-16, 32 y 29 ·
KO-17, 23 y 24 · KO-21, 27, 19 y 30. Pre-marcado: KO-13, 10, 11 y 12 · KO-20, 15 y 18 ·
KO-31, 14, 28 y 33 · KO-16, 32, 29 y 25 · KO-17, 23, 24 y 26 · KO-21, 27, 19, 30 y 22.
Los seis prompts de cada tarea son iguales salvo la lista de casos.

KO-01 a KO-12 se tradujeron antes con Claude (Opus 5.5), con los mismos criterios
(encabezados de `ISSUE-144-COREANO-TRADUCCION-2026-11-07.md` y `-2-2026-11-10.md`, fuera de Git).

**Después del pre-marcado.** Luciano fijó dos criterios el 2026-11-11 y se aplicaron a las propuestas:
pedir el nombre, la ciudad o la fecha de nacimiento no es `T_R`; y en los pedidos de entrar a un
sitio, `T_R` es el sitio falso (cuando se dicta la dirección), no abrir un portal como Naver.
Cambiaron 11 casos: KO-13, 14, 15, 16, 20, 21, 23, 25, 29, 31 y 32 (en KO-21, solo `T_C`,
que caía antes del pedido). En KO-30 se confirmó la propuesta sin pedido. Luciano aprobó la
lista resultante. El `T_R` de KO-02, que la ficha de Luciano no traía como número, lo marcó
Claude (Opus 5.5) con los mismos criterios.

---

## Prompt de traducción

### Traducción coreano → español de llamadas de estafa (issue #144)

Sos un traductor. Tu tarea: traducir al español estas llamadas, una por una: <lista de casos del reparto>.

#### Archivos

- Carpeta de trabajo: `data/private/issue-144/tanda3`
- Entrada: para cada caso hay un archivo `<CASO>_vishing_<N>.ko.txt` (por ejemplo `KO-13_vishing_300.ko.txt`). Primera línea: encabezado con caso, fuente, SHA-256, segmentos y duración. Después, un segmento por línea: `N. [segundo s] HABLANTE: texto coreano`, y a veces una línea `[sin texto entre X s y Y s]`.
- Salida: para cada caso escribí `data/private/issue-144/tanda3/<CASO>.es.md`. **Solo podés crear esos archivos.** No edites nada más, no hagas commits, no subas ni compartas el texto en ningún lado (la fuente prohíbe redistribuir derivados; todo queda local). No uses la red.
- Modelo de referencia (formato ya aprobado por el usuario): `data/private/issue-144/tanda3/../ISSUE-144-COREANO-TRADUCCION-2-2026-11-10.md`, sección KO-03. Imitá ese formato exactamente.

#### Formato de cada `<CASO>.es.md`

```
#### <CASO> · `vishing_<N>` · <tipo breve de maniobra en 3 a 10 palabras>

SHA-256 `<sha del encabezado>` · <S> segmentos · <D> s.

1. [0,3 s] **A:** ...
2. [2,8 s] **B:** ...
[sin texto entre X s y Y s]
...

##### Ficha <CASO>

- Conservar / descartar / revisar:
- ¿Es creíble como llamada? (sí / dudosa / no) y por qué:
- Leyendo la conversación entera, ¿es estafa? (sí / no / dudoso):
- ¿En qué segmento (y segundo) una persona atenta ya sospecharía?:
- Primer pedido de alto riesgo (segmento y segundo, `T_R`):
- Primer cumplimiento (segmento y segundo, `T_C`):
- ¿Comienzo y final completos o es un recorte?:
- ¿Se distinguen bien los hablantes?:
- Dirección: ¿llama el estafador (entrante) o la víctima?:
- Equivalente local (familia del catálogo):
- Dudas o ambigüedades:
- Decisión y motivo:

---
```

La ficha va **vacía**: la llena una persona. No agregues observaciones tuyas sobre pedidos, cumplimientos ni si es estafa, en ningún lado.

#### Criterios de traducción (los mismos de las tandas anteriores)

1. **Un número por segmento de la fuente, todos, en el mismo orden**, con el mismo número y el mismo segundo de inicio (coma decimal). No juntes, no saltees, no resumas: si la fuente tiene 605 segmentos, la salida tiene 605 ítems numerados. Conservá las líneas `[sin texto entre …]` donde están.
2. Traducción fiel al español, oral y natural, **sin argentinizar** y sin volver más explícito ningún pedido. No agregues ni saques información.
3. `A` y `B` son las etiquetas de hablante de la fuente: conservalas. Si la transcripción asignó mal el hablante, dejá la letra de la fuente y agregá `[en la fuente: B — probable A]` (o al revés).
4. Errores evidentes del reconocimiento de voz: traducí lo más probable por contexto y, si cambia el sentido, marcá `[así en la fuente; …]` o `[probable error de reconocimiento por «…»]`. Lo que no se entiende: `[confuso en la fuente]`.
5. Nombres de personas, instituciones y empresas, tal como aparecen (romanizados). Teléfonos, números de documento, nombre de la víctima e ID de KakaoTalk → `[TELÉFONO]`, `[NÚMERO]`, `[NOMBRE]`, `[ID]`. Montos en wones, como en la fuente.
6. Si la llamada es muy larga, trabajá por bloques y escribí el archivo de a partes, pero entregalo completo.

#### Cómo comprobar que terminaste

Para cada caso, contá los ítems numerados de tu salida y compará con el número de segmentos del encabezado. Por ejemplo:
`grep -cE '^[0-9]+\. \[' data/private/issue-144/tanda3/<CASO>.es.md` tiene que dar exactamente S.
Si algún caso no cierra, corregilo antes de reportar.

#### Reporte

Al terminar, reportá con `worker_done`: por cada caso, archivo escrito, segmentos esperados y segmentos contados, y cualquier problema (pasajes muy confusos, diarización muy mezclada). Si no pudiste terminar un caso, el Task falló: decilo y explicá dónde quedaste.

---

## Prompt de pre-marcado

### Pre-marcado de llamadas de estafa coreanas traducidas (issue #144)

Sos un anotador. Para cada caso de esta lista proponés quién es la víctima, el primer pedido de alto riesgo (`T_R`) y el primer cumplimiento (`T_C`): <lista de casos del reparto>.

Tu propuesta **no** es la referencia final: una persona la va a confirmar o corregir leyendo una línea por caso. Por eso cada marca va con la frase citada.

#### Dónde están las conversaciones

- KO-10, KO-11 y KO-12: secciones `## KO-10 …`, `## KO-11 …` y `## KO-12 …` de `data/private/issue-144/ISSUE-144-COREANO-TRADUCCION-2-2026-11-10.md`.
- KO-13 a KO-33: `data/private/issue-144/tanda3/<CASO>.es.md`.

Cada segmento: `N. [segundo s] **HABLANTE:** texto`. Los hablantes (A, B, C, D, E) salen de una diarización automática con errores; algunos errores ya están marcados (`[en la fuente: E — probable B]`). Son todas llamadas reales de estafa publicadas por el regulador coreano, traducidas al español.

#### Qué escribís

**Solo** podés crear `data/private/issue-144/tanda3/premarcado/<CASO>.json`, uno por caso. No edites nada más, no hagas commits, no uses la red y no copies el texto a ningún otro lado (la fuente prohíbe redistribuir derivados).

```json
{
  "caso": "KO-14",
  "hablantes": {"A": "estafador", "B": "victima", "C": "estafador", "E": "victima"},
  "correcciones_hablante": [{"segmento": 120, "es": "victima", "motivo": "responde a la pregunta de A"}],
  "es_estafa": "sí",
  "t_r": {"segmento": 88, "etiqueta": "REQUEST_SECRET", "cita": "frase corta del segmento que contiene el pedido"},
  "otros_pedidos": [{"segmento": 140, "etiqueta": "REQUEST_TRANSFER", "cita": "…"}],
  "t_c": {"segmento": 89, "cita": "…"},
  "comienzo_final": "completa | arranca empezada | final cortado | recorte por los dos lados",
  "confianza": "alta | media | baja",
  "dudas": "texto breve, o vacío"
}
```

- `hablantes`: cada etiqueta que aparece en el caso → `victima`, `estafador` u `otro` (por ejemplo, un empleado real del banco o un familiar). Hay **una sola víctima**: la persona a la que llamaron y a la que le piden cosas. Si una etiqueta mezcla a las dos personas, poné la mayoritaria y listá en `correcciones_hablante` al menos los segmentos de `T_R`, `T_C` y los que estén a ±3 de ellos que estén mal atribuidos.
- `t_r`: el **primer** pedido de alto riesgo que el estafador le hace a la víctima. Si no hay ninguno en la conversación, `"t_r": null` y explicalo en `dudas`. `otros_pedidos`: los siguientes pedidos distintos importantes (hasta 5).
- `t_c`: el **primer** cumplimiento observable de la víctima (dicta la clave, dice que transfirió, instala la app, carga los datos en el sitio). Si no se observa, `null`. Decir «sí, ya lo hago» sin hacerlo no es cumplimiento.
- `etiqueta`, una de estas:
  - `REQUEST_AUTH_CODE`: pide un código de un solo uso (OTP, token). No cuenta mencionar que el código existe sin pedir que lo dicte.
  - `REQUEST_SECRET`: pide una credencial permanente (clave, PIN, contraseña, tarjeta de coordenadas). No cuenta confirmar datos que la entidad ya tiene.
  - `REQUEST_PERSONAL_DATA`: pide datos identificatorios (número de documento, domicilio, foto del documento). No cuenta si la persona los dice sin que se los pidan.
  - `REQUEST_TRANSFER`: pide mover dinero (transferir, pagar, depositar, sacar efectivo, operar un cajero, entregar efectivo o tarjetas). No cuenta hablar de un movimiento ya ocurrido.
  - `REQUEST_REMOTE_ACCESS`: pide instalar acceso remoto o compartir pantalla.
  - `REQUEST_SECURITY_ACTION`: pide abrir un enlace o sitio, instalar una app «de seguridad», cargar datos en un sitio, autorizar un dispositivo.

#### Criterios (guía de anotación del proyecto)

- Revisar el pedido en su contexto: mencionar un código no es pedirlo. Anunciar que «después vamos a verificar su cuenta» no es pedido; «entre a este sitio y escriba su número de cuenta» sí.
- La marca va al segmento donde el pedido queda formulado. Si el estafador lo construye en varios segmentos, el primero en que ya es un pedido concreto.
- Ante la duda entre dos segmentos, elegí uno, bajá la `confianza` y explicá la alternativa en `dudas`.
- No inventes: si la conversación está cortada antes del pedido, `t_r` es `null`.

#### Cómo comprobar que terminaste

Para cada caso: el JSON es válido (`python3 -m json.tool archivo`), los números de segmento existen en esa conversación, la etiqueta de `t_r.segmento` corresponde a un `estafador` (con las correcciones aplicadas) y la de `t_c.segmento` a la `victima`.

#### Reporte

Reportá con `worker_done`: por caso, archivo escrito, `t_r` y `t_c` (segmento o null) y confianza. Si no pudiste terminar un caso, el Task falló: decilo.
