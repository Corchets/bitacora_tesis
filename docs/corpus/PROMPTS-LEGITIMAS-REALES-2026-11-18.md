# Prompts del set de legítimas reales (2026-11-18)

Prompts con que se armó el set de llamadas salientes reales de CallCenterEN. Ver
[FUENTES-LEGITIMAS-REALES.md §8](../investigacion/FUENTES-LEGITIMAS-REALES.md#8-set-armado-el-2026-11-18).
Modelo de los subagentes: Claude Sonnet 5.5, coordinados por una sesión de Claude Code con Opus 5.5, que no
leyó las llamadas y validó las salidas con scripts. Cada subagente leyó este archivo y recibió la lista de
alias de su lote. No vieron prompts del detector, resultados ni otros casos del repo.

## 1. Turnos, roles y traducción

Ocho subagentes en paralelo, con seis o siete llamadas cada uno, repartidas por cantidad de palabras.

```text
Vas a preparar llamadas reales de call center para un test de falsas alarmas de un detector de estafas
telefónicas. Cada llamada es una transcripción automática en inglés (ASR de AssemblyAI), sin hablantes,
partida en segmentos numerados en cada pausa de 600 ms o más. Los datos personales vienen tapados con
marcadores como [PERSON_NAME] o [DATE_OF_BIRTH]. Un segmento puede mezclar a los dos hablantes, y un turno
puede ocupar varios segmentos.

Por cada alias de tu lote, leé `fuente/<alias>.md` y escribí `traduccion/<alias>.json`. No leas otros
archivos ni otros alias.

1. Filtro. `conversacion`: true si hay una conversación de ida y vuelta entre la empresa y la persona
   llamada (al menos algunos intercambios); false si es buzón de voz, solo un menú automático, nadie
   atiende o se oye un solo lado. `direccion`: "saliente" si la empresa llamó a la persona, "entrante" si la
   persona llamó a la empresa (por ejemplo, «thank you for calling»), "no_se_sabe" si el texto no alcanza.
   No juzgues si es estafa o legítima: eso lo hace otra persona.
2. Turnos. Reconstruí el diálogo como turnos con `lado`: "EMPRESA" (el agente, otro empleado, un agente
   al que transfieren, un mensaje grabado de la empresa) o "PERSONA" (la persona llamada y quien esté de
   su lado, por ejemplo su pareja). Un turno es lo que dice un lado sin que hable el otro. Partí los
   segmentos donde cambia el hablante y juntá los segmentos seguidos del mismo lado. En `segmentos` poné
   el primero y el último que cubre el turno. Si dudás de quién dice algo, decidí por el contenido y
   marcá `duda: true`.
3. Traducción al español neutro, fiel, igual que el set coreano de #144: mismo contenido y mismo orden,
   sin agregar ni sacar información, sin volverla más ni menos sospechosa. Si piden la tarjeta, la
   traducción pide la tarjeta. Contexto de EE. UU. sin adaptar: dólares, Medicare y nombres de programas
   quedan como están. Registro oral; se pueden simplificar titubeos. Errores evidentes del ASR se
   corrigen por contexto; lo ininteligible se traduce por lo más probable. Los marcadores quedan
   exactamente como están ([PERSON_NAME], [LOCATION] …): no inventes datos. Trato de «usted».
4. Formato de salida (JSON, UTF-8):
   {"alias": "...", "conversacion": true, "direccion": "saliente", "motivo_si_no_sirve": "",
    "turnos": [{"lado": "EMPRESA", "segmentos": [1, 3], "en": "...", "es": "...", "duda": false}],
    "notas": "dificultades, en una o dos líneas"}

Tu mensaje final: una línea por alias con cantidad de turnos, `conversacion` y `direccion`, sin copiar
texto de las llamadas.
```

## 2. Anotación a ciegas

Dos anotadores independientes (subagentes que no se ven entre sí), cada uno sobre todas las llamadas de una
tanda que pasaron el filtro, con alias nuevos y en otro orden: `a1` y `a2` en la primera (`LL-01` a `LL-49`),
`b1` y `b2` en la segunda (desde `LL-51`). Leen el texto final en español, con las líneas `A:` y `B:` y quién
es la persona llamada. No ven el inglés, el estrato, el detector ni lo que marcó el otro.

`a1` escribió la misma justificación, palabra por palabra, en las 42 llamadas que marcó como estafa. Por eso, a
`b1` y `b2` se les agregó: «La justificación tiene que ser propia de cada llamada; no repitas texto entre
llamadas».

```text
Anotás llamadas telefónicas transcriptas para un test de falsas alarmas de un detector de estafas. Cada
archivo tiene líneas numeradas «A: …» / «B: …» y dice cuál de los dos es la persona llamada (PROTEGIDA);
el otro lado es OTRA. Los nombres, fechas y montos son ficticios. Anotá cada llamada sin mirar ninguna
otra fuente y escribí `anotacion-<anotador>/<alias>.json`:

- inicia: "otra" si OTRA hizo esta llamada (PROTEGIDA atiende u OTRA se presenta como quien llama, aunque
  devuelva un llamado o llame por un trámite previo); "protegida" si la hizo PROTEGIDA (OTRA atiende con
  el saludo de una empresa, o PROTEGIDA dice que llama o devuelve el llamado); "no_se_sabe".
- numero: "agendado" solo si el texto muestra que OTRA es un contacto que llama desde su teléfono de
  siempre (PROTEGIDA la reconoce y saluda por el nombre antes de que se presente); si no, "no_agendado".
- legitimidad: "legitima"; "legitima_agresiva" (venta o insistencia agresiva, pero sin engaño para sacar
  datos o plata); "dudosa" (no se puede decidir); "estafa" (engaño para obtener datos, plata o acceso).
  Justificá en una línea.
- motivo: "venta_en_frio" (ofrece algo sin contacto previo), "seguimiento" (la persona había dejado sus
  datos, pedido información o tiene un trámite), "cliente" (ya es cliente: renovación, cambio,
  verificación), "otro".
- tipo_legitima: "cotidiana" (no piden ningún dato sensible), "pedido_razonable" (piden un dato personal o
  de pago y es razonable en ese trámite), "mencion_sin_pedido" (se habla de datos, plata o claves, pero no
  se los piden).
- pedido_sensible: lista con lo que OTRA pide: "datos_personales" (fecha de nacimiento, dirección,
  número de seguro o de afiliado), "datos_de_pago" (tarjeta, cuenta bancaria), "codigo_o_clave",
  "plata" (que pague o transfiera ahora). Vacía si no pide nada. `primer_pedido_linea`: número de línea
  del primero, o null.
- completa: "si", "falta_comienzo" o "falta_final".
- notas: una línea.
```

## 3. Adjudicación

Si ninguno de los dos anotadores marca una llamada como legítima, va a la **zona gris** y no se adjudica. Si
alguno la marca legítima, lo que coincide pasa tal cual (de `pedido_sensible` se toma la unión, y de
`primer_pedido_linea`, la primera) y los desacuerdos los resuelve un tercer subagente (Claude Sonnet 5.5), que
ve las dos anotaciones y la llamada en español, con este prompt:

```text
Dos anotadores marcaron por separado las mismas llamadas con las reglas de la sección 2 de este archivo, y
no coincidieron en algunos campos. `desacuerdos.json` trae, por alias, los campos en conflicto y las dos
anotaciones completas. Para cada alias, leé `anotar/<alias>.md` (o `anotar-2/`, desde LL-51), aplicá las reglas de la sección 2 y elegí
el valor de cada campo en conflicto. Si ninguno de los dos acertó, poné el que corresponde. Escribí
`adjudicador.json`: {alias: {campo: {"valor": ..., "motivo": "una línea"}}}; para `pedido_sensible` el valor
es la lista y agregás `primer_pedido_linea`. No abras otros archivos.
```

Cada referencia guarda las dos anotaciones y lo adjudicado (`anotacion`).
