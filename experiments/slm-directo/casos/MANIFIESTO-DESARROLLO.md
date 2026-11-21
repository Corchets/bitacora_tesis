# Manifiesto del corpus de desarrollo

Fecha: 2026-11-09. Lo preparó un agente con las decisiones de Mateo Antenucci del mismo día, para la etapa 3 de
[#143](https://github.com/Corchets/bitacora_tesis/issues/143), que corre el 2026-11-12.

> **Estado: propuesta sin discutir.** Ordena el corpus: dice qué casos cuentan y cuáles quedan aparte o como
> históricos. **No borra ni cambia ningún caso** (`texto/`, `referencia/`) ni las listas que ya existían. No toca la
> reserva ni el test de #45.

## Qué decidió Mateo (2026-11-09)

1. **Una legítima por escenario, sin las 7 dudosas.** Los 47 escenarios son los del método de #45
   ([`ESCENARIOS-LEGITIMAS-DESARROLLO.md`](ESCENARIOS-LEGITIMAS-DESARROLLO.md)). El representante se fija antes de
   correr, y por defecto es la `ENT-L`.
2. **Un solo manifiesto de desarrollo** que diga qué cuenta y qué queda como histórico: este archivo y
   [`MANIFIESTO-DESARROLLO.json`](MANIFIESTO-DESARROLLO.json).
3. **Las estafas sin pedido no llevan una hoja aparte.** La pregunta a/b/c se suma al formulario de #145
   ([`PREGUNTA-145-ESTAFAS-SIN-PEDIDO.md`](../../../docs/corpus/PREGUNTA-145-ESTAFAS-SIN-PEDIDO.md)).

## Qué cuenta

<!-- estados:inicio -->
| Estado | Casos | Qué son |
|---|---:|---|
| `cuenta` | 91 | la vista principal: 46 estafas y 45 legítimas representativas |
| `misma_situacion` | 42 | legítimas cotidianas que repiten un escenario ya representado |
| `dudosa` | 7 | legítimas cotidianas que chocan con las fuentes (criterio de dudosas) |
| `aparte` | 7 | legítimas de corpus_v2 dentro del alcance, de familia o trabajo |
| `fuera_del_alcance` | 44 | legítimas de corpus_v2 que inicia la persona o de un número agendado |
| `historico` | 53 | piloto escrito, trampas y laboratorio |
| **total** | **244** | |
<!-- estados:fin -->

- **Vista principal:** [`listas/alcance-91.txt`](listas/alcance-91.txt), con las 46 estafas de corpus_v2 y las 45
  legítimas de [`listas/legitimas-escenarios-45.txt`](listas/legitimas-escenarios-45.txt).
- **Estafas:** las 46 cuentan. Las 10 sin pedido llevan la marca hasta que se conteste la pregunta 5 de #145; las que
  salgan `c` (incoherentes) pasarían a informarse aparte, según la regla ya escrita.
- **Aparte:** las 7 dudosas y las 7 legítimas de corpus_v2 de familia o trabajo se informan aparte, como en la etapa 2.
- **Fuera del alcance:** las 44 legítimas de corpus_v2 que inicia la persona (#151).
- **Históricos:** los 53 casos anteriores a corpus_v2
  ([`AUDITORIA-53-HISTORICOS.md`](AUDITORIA-53-HISTORICOS.md)). Quedan para repetir corridas viejas
  (`listas/desarrollo-150.txt`).
- **Las otras 42 legítimas cotidianas** repiten un escenario ya representado. Siguen en `legitimas-91` y sirven para ver
  si el resultado depende de qué llamada se eligió.

El JSON da, por caso, el grupo, la clase, el alcance, el estado, el escenario, el motivo y las huellas SHA-256 del texto
y de la referencia. [`MANIFIESTO-CORPUS-V2.json`](MANIFIESTO-CORPUS-V2.json) sigue siendo el de las huellas de la
reserva: este no lo reemplaza.

## Cómo se elige el representante

Regla fijada el 2026-11-09, antes de la etapa 3. Solo usa el texto, los escenarios y las dudosas; no mira resultados.

1. Se sacan las dudosas.
2. Si queda la `ENT-L` del escenario, es el representante. Ningún escenario tiene más de una.
3. Si no, la llamada más larga que queda; si empatan, la de `case_id` menor.
4. Si no queda ninguna, el escenario sale.

**Resultado: 45 representantes.** Son 41 `ENT-L`, 2 `LEG` y 2 `LEG2`. Tienen de 9 a 36 líneas (mediana 21), contra
5 a 36 (mediana 13,5) de las 94; las estafas tienen de 20 a 38. 22 de los 45 piden un dato personal, según las dos
anotaciones de las dudosas.

La tabla muestra los escenarios con más de una llamada o con algo que decidir. Las 13 `ENT-L` sueltas que no son
dudosas se representan a sí mismas y no figuran.

<!-- representantes:inicio -->
| Escenario | Llamadas | Representante | Por qué |
|---|---|---|---|
| E01 | `ENT-L-BANCO-001` (dudosa), `LEG-BA-01`, `LEG2-BA-01` (dudosa) | `LEG-BA-01` | no hay ENT-L no dudosa: la más larga |
| E02 | `ENT-L-BANCO-002` (dudosa), `LEG-BA-02`, `LEG2-BA-02` (dudosa) | `LEG-BA-02` | no hay ENT-L no dudosa: la más larga |
| E03 | `ENT-L-BANCO-003`, `LEG-BA-03`, `LEG2-BA-03` | `ENT-L-BANCO-003` | la ENT-L |
| E04 | `ENT-L-DELIVERY-002`, `LEG-CO-02`, `LEG2-CO-02` | `ENT-L-DELIVERY-002` | la ENT-L |
| E05 | `ENT-L-DELIVERY-003`, `LEG-CO-03`, `LEG2-CO-03` | `ENT-L-DELIVERY-003` | la ENT-L |
| E06 | `ENT-L-ENCUESTA-001`, `LEG-EN-01`, `LEG2-EN-01` | `ENT-L-ENCUESTA-001` | la ENT-L |
| E07 | `ENT-L-ENCUESTA-003`, `LEG-EN-03`, `LEG2-EN-03` | `ENT-L-ENCUESTA-003` | la ENT-L |
| E08 | `ENT-L-MEDICO-001`, `LEG-TU-01`, `LEG2-TU-01` | `ENT-L-MEDICO-001` | la ENT-L |
| E09 | `ENT-L-MEDICO-002`, `LEG-TU-02`, `LEG2-TU-02` | `ENT-L-MEDICO-002` | la ENT-L |
| E10 | `ENT-L-SOPORTE-002`, `LEG-ST-02`, `LEG2-ST-02` | `ENT-L-SOPORTE-002` | la ENT-L |
| E11 | `ENT-L-SOPORTE-003`, `LEG-ST-03`, `LEG2-ST-03` | `ENT-L-SOPORTE-003` | la ENT-L |
| E12 | `ENT-L-VENTAS-001`, `LEG-CC-01`, `LEG2-CC-01` | `ENT-L-VENTAS-001` | la ENT-L |
| E13 | `ENT-L-VENTAS-004`, `LEG-CC-02`, `LEG2-CC-04` | `ENT-L-VENTAS-004` | la ENT-L |
| E14 | `ENT-L-VENTAS-006`, `LEG-CC-03`, `LEG2-CC-06` | `ENT-L-VENTAS-006` | la ENT-L |
| E15 | `ENT-L-VENTAS-007`, `LEG-VE-01`, `LEG2-VE-01` | `ENT-L-VENTAS-007` | la ENT-L |
| E16 | `ENT-L-BANCO-005` (dudosa), `LEG2-BA-05` (dudosa) | — | sale: todas sus llamadas son dudosas |
| E17 | `ENT-L-DELIVERY-006`, `LEG2-CO-06` | `ENT-L-DELIVERY-006` | la ENT-L |
| E18 | `ENT-L-ENCUESTA-002`, `LEG-EN-02` | `ENT-L-ENCUESTA-002` | la ENT-L |
| E19 | `ENT-L-ENCUESTA-004`, `LEG2-EN-04` | `ENT-L-ENCUESTA-004` | la ENT-L |
| E20 | `ENT-L-ENCUESTA-005`, `LEG2-EN-05` | `ENT-L-ENCUESTA-005` | la ENT-L |
| E21 | `ENT-L-MEDICO-003`, `LEG-TU-03` | `ENT-L-MEDICO-003` | la ENT-L |
| E22 | `ENT-L-MEDICO-004`, `LEG2-TU-05` | `ENT-L-MEDICO-004` | la ENT-L |
| E23 | `ENT-L-SOPORTE-001`, `LEG-ST-01` | `ENT-L-SOPORTE-001` | la ENT-L |
| E24 | `ENT-L-SOPORTE-004`, `LEG2-ST-04` | `ENT-L-SOPORTE-004` | la ENT-L |
| E25 | `ENT-L-TRAMITE-002`, `LEG2-TU-06` | `ENT-L-TRAMITE-002` | la ENT-L |
| E26 | `ENT-L-VENTAS-005`, `LEG2-CC-05` | `ENT-L-VENTAS-005` | la ENT-L |
| E27 | `ENT-L-VENTAS-008`, `LEG-VE-02` | `ENT-L-VENTAS-008` | la ENT-L |
| E28 | `ENT-L-VENTAS-009`, `LEG-VE-03` | `ENT-L-VENTAS-009` | la ENT-L |
| E29 | `ENT-L-VENTAS-010`, `LEG2-VE-04` | `ENT-L-VENTAS-010` | la ENT-L |
| E30 | `ENT-L-VENTAS-011`, `LEG2-VE-05` | `ENT-L-VENTAS-011` | la ENT-L |
| E31 | `ENT-L-VENTAS-012`, `LEG2-VE-06` | `ENT-L-VENTAS-012` | la ENT-L |
| E32 | `LEG-CO-01`, `LEG2-CO-01` | `LEG2-CO-01` | no hay ENT-L no dudosa: la más larga |
| E42 | `ENT-L-SOPORTE-005` (dudosa) | — | sale: todas sus llamadas son dudosas |
| E47 | `LEG2-ST-05` | `LEG2-ST-05` | no hay ENT-L no dudosa: la más larga |
<!-- representantes:fin -->

**Variantes, por si el equipo prefiere otra lectura:**
- **Si un escenario sale cuando su `ENT-L` es dudosa,** también salen E01 y E02, que hoy representa su `LEG`, y
  quedan 43.
- **Con la variante estricta de las dudosas,** quedan 42. Salen además E25, E33 y E34, y E03 pasa a `LEG-BA-03`.

## ¿Regenerar el corpus o alcanza con ordenarlo?

> **Estado: propuesta sin discutir.** Lo decide Mateo. La recomendación es **ordenar y no regenerar** el desarrollo
> antes del cierre.

**Qué arreglaría regenerar:**
- el sesgo del DNI: el control de escenarios muestra que las reescrituras agregan pedidos de datos;
- los guiones repetidos;
- las `LEG` y `LEG2` cortas.

**Por qué no conviene ahora:**
- **El calendario:** el 90 % es para el 2026-11-15, la etapa 3 corre el 2026-11-12 y el cierre es el 2026-11-30.
  Regenerar exige escribir llamadas nuevas, controlar su parecido, anotar referencias, roles y alcance, revisarlas con
  #145 y volver a correr cada configuración en Colab. Son varios días, y los mismos días que necesita el test.
- **Rompe la comparación.** Las etapas 1 y 2 de #143 y las decisiones de los ADR 0002 y 0006 se tomaron sobre este
  corpus. Con uno nuevo habría que volver a correr v4 y C para tener la referencia.
- **Lo que más importa ya está hecho donde importa.** La cifra final sale del test, y el test de #45 ya tiene 56
  legítimas nuevas: entrantes, escritas a ciegas, de largo parecido al de las estafas, con DNI en el 5 % y sin parecido
  a las 94 de desarrollo.
- **Ordenar resuelve lo urgente.** Con un representante por escenario, ningún guion pesa doble. Las dudosas se informan
  aparte, y el sesgo del DNI queda declarado como límite del desarrollo.

**Lo que queda como límite:** 22 de los 45 representantes piden un dato personal. Si el detector aprende a no avisar
por eso, en desarrollo puede parecer mejor de lo que es; el test, con DNI en el 5 %, lo va a mostrar. Conviene
informarlo como hallazgo.

## Cómo se regenera

```bash
python -I corpus_desarrollo.py manifiesto
```

Reescribe `MANIFIESTO-DESARROLLO.json`, las dos listas y las tablas de este archivo a partir de
`escenarios-legitimas.json` y `legitimas-dudosas.json`. El alcance de corpus_v2 sale de `alcance-desarrollo.json` en el
commit `29a4790` de `exp/143-puntaje-token` (#151), que todavía no está en `laboratorio-main`. Lo lee con `git show`,
como hace #45.
