# Reglas v2: menos falsas alarmas

> **Estado: propuesta sin discutir.** Análisis de desarrollo del ensayo
> [#50](https://github.com/Corchets/bitacora_tesis/issues/50), etapa 3 del plan. Casos escritos,
> sin revisión humana. No usa `test_reservado`, no usa modelos y no fija umbrales ni política
> (D07, D08, D09 abiertas). Las reglas v2 son una variante para comparar, no una elección.

```bash
cd experiments/slm-directo
python3 correr.py --solo-reglas --etiqueta m1-reglas-150                      # v1 (por defecto)
python3 correr.py --solo-reglas --reglas v2 --etiqueta m1-reglas-v2-150       # v2
python3 correr.py --solo-reglas --reglas v1,v2                                # las dos en la misma corrida
python3 analisis/2026-10-21-reglas-v2/comparar.py corridas/2026-10-21_200147_m1-reglas-150 corridas/2026-10-21_201914_m1-reglas-v2-150 --detalle
```

Corridas: [`2026-10-21_200147_m1-reglas-150`](../../corridas/2026-10-21_200147_m1-reglas-150/resumen.md)
(v1) y [`2026-10-21_201914_m1-reglas-v2-150`](../../corridas/2026-10-21_201914_m1-reglas-v2-150/resumen.md)
(v2), ambas sobre los 150 casos de desarrollo.

## 1. Cómo se diseñó (y qué tan honesto es el resultado)

Se **diseñó mirando solo los 53 históricos** (textos y disparos de v1 sobre ellos) y se
**congeló antes de correr corpus_v2**. Aun así, no es una prueba ciega:

- Antes de diseñar corrí la v1 sobre los 150 y, para el paso de análisis, vi las líneas de las
  falsas alarmas de corpus_v2 (por ejemplo «pintando» disparando `pin`, «apagó» disparando `pago`).
  Eso motivó la palabra entera (cambio 1). Es información de corpus_v2 que se coló en el diseño.
- No leí las líneas de las estafas de corpus_v2 hasta tener la v2 congelada y corrida.
- Durante el diseño probé una variante que miraba también la línea anterior (para pedidos
  partidos en dos líneas): ganaba 1 estafa y agregaba 1 falsa alarma en los históricos, y la
  descarté. Esas decisiones se tomaron contra los históricos.
- Los 53 históricos están, por lo tanto, **ajustados**: sus números v2 son optimistas.
  corpus_v2 es la lectura menos contaminada, no una lectura limpia. Los dos grupos son desarrollo.
  La prueba justa sigue siendo la reserva ([#55](https://github.com/Corchets/bitacora_tesis/issues/55)), que no se tocó.

## 2. Qué hacía la v1 (análisis de errores)

Falsas alarmas de v1 sobre los 150: 51/75. Los disparos caen en cuatro familias:

| Familia | Ejemplo (caso, línea) | Patrón |
|---|---|---|
| Mención o relato, no pedido | «hice una transferencia ayer» (`CV2-D-L-BANCO-002`, L2); «me llegó por SMS un código» (`LG-WA-CONSULTA-01-e01`, L1) | `transferencia`, `codigo` |
| Pedazo de otra palabra | «están pintando el pasillo» (`CV2-D-L-DELIVERY-004`, L1); «Hola, ¿se apagó alguna luz?» (`CV2-D-L-SOPORTE-003`, L2) | `pin`, `pago` (por typo permitido) |
| Pregunta o consulta del otro lado | «¿Y el copago lo pago ahí o por transferencia?» (`CV2-D-L-MEDICO-001`, L19) | `pago`, `transferencia` |
| Advertencia de seguridad | «nunca le pases la clave del banco a nadie» (`TR-03`, L2); «no te voy a pedir ningún código» (`TR-06`, L7) | `clave`, `codigo` |

Palabras como `codigo`, `pago`, `clave`, `domicilio`, `autoriza` aparecen en conversaciones
comunes; v1 las trata como pedido sin mirar si alguien se las está pidiendo a la otra persona.
Las estafas que pierde v1 (10/75) son pedidos sin la palabra clave («leeme lo que te acaba de
llegar», «gireme ya», «dale permiso a esa ventana») o conversaciones sin pedido.

## 3. Qué cambió en la v2

Código en [`reglas_v2.py`](../../reglas_v2.py); `reglas.py` no se tocó. Se agregó el flag
`--reglas v1,v2` a `correr.py` y `DetectorReglas(version)` en `detectores.py` (config `reglas_v2`).
Mismos patrones (`PATRONES`) y mismo typo de un carácter para patrones de 6+ letras; tres filtros:

1. **Palabra entera.** El patrón tiene que empezar y terminar en límite de palabra (admite
   plural en «-s»). Excepción: las raíces `transferi`, `instala`, `autoriza`, `abri el enlace`.
2. **Pedido dirigido.** La línea necesita un imperativo con «-me» (`pasame`, `decime`,
   `deme`), un imperativo en voseo seguido de lo pedido (`abrí el enlace`), `necesito que`,
   `tenés que`, `hay que`, `te pido`, `para que me compartas`, o `¿me podés / me pasás...?`.
   Sin eso es una mención.
3. **Advertencia.** `nunca`, `ningún`, `no te vamos a pedir`, `no compartas`, `no pongas`...
   anulan el aviso salvo que haya un imperativo con «-me» («no cortes y decime el código»).

No usa quién habla (en varios casos el estafador es B). Sigue mirando una sola línea.

## 4. Resultados v1 vs v2

Estafas con aviso y falsas alarmas con la política del ensayo (primer aviso), intervalos de
Wilson 95 % entre corchetes. Salen de [`comparar.py`](comparar.py).

| Grupo | Reglas | Estafas con aviso | Falsas alarmas |
|---|---|---|---|
| 53 históricos (ajustados) | v1 | 23/29 (79 %) [62–90] | 14/24 (58 %) [39–76] |
| 53 históricos (ajustados) | v2 | 21/29 (72 %) [54–85] | 2/24 (8 %) [2–26] |
| corpus_v2 | v1 | 42/46 (91 %) [80–97] | 37/51 (73 %) [59–83] |
| corpus_v2 | v2 | 11/46 (24 %) [14–38] | 6/51 (12 %) [6–23] |
| 150 desarrollo | v1 | 65/75 (87 %) [77–93] | 51/75 (68 %) [57–77] |
| 150 desarrollo | v2 | 32/75 (43 %) [32–54] | 8/75 (11 %) [6–20] |

Lectura:

- **Las falsas alarmas bajan mucho en los dos grupos** (14→2 y 37→6), también en corpus_v2,
  que no fue la base del ajuste (aunque sí vi sus falsas alarmas, ver §1).
- **En corpus_v2 la v2 pierde la mayoría de las estafas** (42→11). No es solo el filtro:
  mirando cuándo avisaba la v1 en esas estafas, 27 de 42 avisos eran **antes del pedido** de
  referencia (y solo 5 en el pedido). Es decir, la v1 «acertaba» sobre todo por nombrar una
  palabra (`transferencia`, `pago`, `código`) en la presentación o el relato, no por detectar el
  pedido. La v2 avisa antes del pedido en 3 y en el pedido en 6. La cifra «91 %» de v1 en
  corpus_v2 mide en gran parte esa coincidencia de vocabulario, no detección incremental.
- Las 35 estafas de corpus_v2 que la v2 deja sin aviso son sobre todo **pedidos indirectos sin
  palabra clave en la línea del pedido** («Poné en un sobre todo el efectivo que retiraste»,
  «Decime la serie y dejo tu contacto aprobado», «Dale permiso a esa ventana», «si podés cubrir
  el saldo ahora»): ningún filtro de forma las rescata, falta vocabulario o interpretación.
  Son justo los casos de dificultad `indirecto` y `sin_pedido`.
- Compromiso medido: v2 baja a un octavo las falsas alarmas en históricos y a un sexto en
  corpus_v2, a costa de perder 2 estafas en históricos y 31 en corpus_v2.

## 5. Errores que quedan

Falsas alarmas de v2 (8/75):

| Caso | Línea | Por qué |
|---|---|---|
| `TR-05-asado-con-transferencia` | L13 «pasámelos por transferencia antes del viernes» | Pedido real de un familiar: indistinguible de estafa sin contexto. |
| `CV2-D-L-FAMILIAR-002` | L8 «transferime 11.700 por tu parte» | Ídem. |
| `CV2-D-L-BANCO-010` | L10 «confirmame los últimos cuatro números de esa cuenta» | Pedido legítimo del banco con `numeros`. |
| `TR-08-frase-cortada-candado` | L3 «Pasame el código» | Frase cortada; sin contexto es un pedido. |
| `CV2-D-L-BANCO-006` | L9 «me apareció un mensaje con un código cuando abrí la app» | `abri la` pasa como imperativo en voseo (el acento no se conserva). |
| `CV2-D-L-MEDICO-002` | L20 «si autorizaste el portal...» | La raíz `autoriza` acepta «autorizaste» y hay un `te` dirigido en la frase. |
| `CV2-D-L-SOPORTE-001` | L6 «¿Me confirmás la calle... donde está instalado?» | Raíz `instala` acepta «instalado» más `¿me confirmás...?`. |
| `CV2-D-L-SOPORTE-002` | L22 «La clave no necesito que me la digas.» | Falta «no necesito que» como advertencia. |

Estafas que quedan sin aviso (43/75) incluyen las 6 que ya perdía la v1 de los históricos
(`LAB-giro-sin-plata`, `LAB-digitos-sin-palabra`, `LAB-pantalla-sin-programa`,
`SC-PREMIO-01-e01`, `TR-01-pedido-indirecto-digitos`, `TR-12-corta-antes-del-pedido`) y,
nuevas por la v2, `TR-07-pedido-partido-en-dos-lineas` (el pedido sigue en la línea
siguiente, sin verbo) y `TR-10-ofrecimiento-inducido`. Lista completa:
`comparar.py ... --detalle`.

## 6. Límites

- **Todo es desarrollo y está contaminado** (§1). Ningún número de este análisis es una
  estimación del desempeño real; los intervalos de Wilson suponen casos independientes y
  son anchos. No se tocó la reserva.
- Los casos son texto escrito y ficticio, con redacción asistida y sin revisión humana. El
  corpus_v2 está hecho para que una parte de las estafas **no** traiga palabras clave en el pedido.
- La diferencia v1-v2 en corpus_v2 depende de que `T_R` (la referencia) sea la línea del pedido.
  Con un criterio que premie avisos tempranos por mención, v1 se vería mejor; con uno que
  penalice avisos sin pedido, peor. No se resolvió ese criterio (D08).
- Las reglas sólo sirven como **filtro barato** si se acepta perder casi la mitad de las
  estafas de desarrollo; como **segunda opinión** sobre un SLM serían útiles para recortar sus
  falsas alarmas solo si se combinan (no probado: sería otra corrida con Ollama).
- Que la v2 «mejore» en falsas alarmas no la convierte en candidata: la v1 sigue siendo el
  comparador de #50 y sus corridas se reproducen igual.
- `reglas_v2.py` normaliza sin acentos, así que `pasá` y `pasa` son lo mismo; el voseo se
  aproxima por contexto y deja huecos.

## 7. Tests

`tests/test_reglas_v2.py`: pedido dirigido, mención/relato, palabra entera, raíces, typo,
advertencia, v1 intacta, `DetectorReglas(version)` y flag `--reglas v1,v2`.
Suite completa: `uv run --with pytest python -m pytest -q tests` → 53 pasan.
