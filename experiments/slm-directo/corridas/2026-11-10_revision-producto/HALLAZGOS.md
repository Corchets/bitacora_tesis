# Hallazgos: los resultados de la sensibilidad con las etiquetas de producto

> **Estado: propuesta sin discutir.** Escrito el 2026-11-10 **después de ver los resultados**: no decide nada. Cruza las
> ocho corridas de [`2026-11-10_sensibilidad-c`](../2026-11-10_sensibilidad-c/analisis.md) con las
> [etiquetas de producto](REVISION-LEGITIMAS.md), que son anteriores (commit `6c1fca0`) y que Mateo aceptó el 2026-11-18.
> Las cifras de `c-premisa` salen de correr [`analizar.py`](analizar.py) con esa corrida como base.

## 1. La mitad de las falsas alarmas no lo son

| corrida | estafas | a tiempo | FA (/94) | **FA estrictas** (/75) | avisos en tolerables (/18) | «debería avisar» (/1) |
|---|---|---|---|---|---|---|
| base de la sensibilidad (`c-json`) | 37/46 | 25/36 | 26 | **11** | 14 | 1 |
| **`c-premisa`, la congelada** | 40/46 | 29/36 | 26 | **13** | 12 | 1 |
| `c-premisa`, repetición | 39/46 | 28/36 | 28 | **14** | 13 | 1 |
| `c-ancla` | 39/46 | 28/36 | 27 | **13** | 13 | 1 |
| `c-sin-freno` | 40/46 | 27/36 | 36 | **21** | 14 | 1 |

- **De las 26 FA de la configuración congelada, 13 caen en llamadas que no deberían avisar.** Otras 12 son tolerables:
  11 de las 13 llamadas de «el banco» y la seña por transferencia (`ENT-L-VENTAS-009`). La que queda es
  `ENT-L-SOPORTE-005`, el soporte que pide acceso remoto, que avisan las ocho corridas.
- **Por intención de la llamada,** en `c-premisa`: informar o coordinar 1/28, encuestas 2/13, seguir una gestión de
  PROTEGIDA 4/12, vender 7/26, advertir (el banco) 11/13. En las entregas y los turnos casi no avisa.
- **Por situación,** las 13 FA estrictas caen en 10 de 38 escenarios.
- **Todas las FA estrictas salen de un 0,3 exacto.** Con «riesgo ≥ 0,4» no queda ninguna, pero las estafas avisadas
  bajan de 40 a 15. El escalón del 0,3 sigue siendo todo el margen.

## 2. Qué dispara las 13 FA estrictas de la congelada

| causa, según el motivo | casos | cuántas |
|---|---|---|
| **Un soporte o un vendedor pide el DNI** | `ENT-L-SOPORTE-001`, `ENT-L-VENTAS-001`, `ENT-L-VENTAS-002`, `LEG2-CC-05`, `LEG2-ST-03` | 5 |
| **«Te contactan por un objeto que dejaste»,** en la primera línea | `ENT-L-SOPORTE-003`, `LEG-ST-03` (el mismo guion de `LEG2-ST-03`) | 2 |
| **OTRA la manda a llamar al 0800 de su factura,** y el motivo lo lee como «llamar a un número que le dictan» | `LEG-CC-03`, `LEG2-CC-06` | 2 |
| **OTRA nombra un código para decir que no se lo pase,** y el motivo dice «te están pidiendo un código» | `ENT-L-SELECCION-002` | 1 |
| Otras: un panel de encuestas, una tarjeta clonada que se menciona, una oferta de seguro | `ENT-L-ENCUESTA-003`, `ENT-L-ENCUESTA-006`, `ENT-L-VENTAS-003` | 3 |

- **El párrafo del DNI no frena donde debería.** Cinco avisos saltan en la línea en que un soporte o un vendedor pide
  el DNI, con motivos como «no es normal que te pidan tu DNI por teléfono». En cambio, cuando lo pide un turno médico,
  un laboratorio o la municipalidad, no avisa nunca. El modelo ya juzga el DNI por el pretexto, pero con su criterio, no
  con el del prompt.
- **Dos FA castigan el consejo oficial.** «Llamá al 0800 de tu factura» es lo que las fuentes recomiendan (S12, S14,
  S16, S18, S21, S26). El ítem de la lista que lo confunde, «cortar y llamar enseguida a otro número que le dictan», es
  el de menos base ([`FUENTES.md`](../2026-11-09_pedido-critico-etapa-3/FUENTES.md): un caso de 2015).
- **Las legítimas «ejemplares» atraen avisos:** 6 de las 14 «no debería avisar» en que OTRA hace seguridad por su cuenta
  tienen FA, contra 7 de las otras 61. Nombrar un código o una clave, aunque sea para cuidarla, sube el riesgo.

## 3. La duda del DNI, con los números de desarrollo

**En desarrollo, la exclusión del DNI no está tapando estafas.**

- De las 6 estafas cuyo pedido es de datos personales, la congelada avisa **5**, y las 5 a tiempo. La única que pide
  solo datos de identidad (`ORGANISMO_PREVISIONAL-002`: CUIL y fecha de nacimiento) avisa en la línea del pedido.
- La que no avisa, `PREMIO-003` (DNI y foto para un premio), **tampoco avisa sin el párrafo del DNI**: `c-sin-freno` no
  la recupera, ni en la corrida ni en la repetición.
- Sacar el párrafo cuesta: de 11 a 21 FA estrictas contra su base, por +3 estafas netas. Recupera dos de familiar, un
  código de WhatsApp y una sin pedido, y pierde un premio. Ninguna es de datos.

**Lo que estos números no pueden decir:** son 6 estafas, generadas, y en las 6 el pretexto es plata o un trámite que la
persona no pidió. Si las estafas reales piden el DNI con un pretexto cotidiano, acá no hay cómo verlo. Lo dirán #144 y
[#154](https://github.com/Corchets/bitacora_tesis/issues/154).

## 4. Lo que sigue sin aviso

- **Código o clave: 14 de 17, 13 a tiempo.** La congelada no avisa `WHATSAPP-003`, `WHATSAPP-006` ni `SOPORTE-003`, ni
  en la corrida ni en la repetición. `SOPORTE-003` no la avisa ninguna de las ocho corridas; `c-ancla` avisa
  `WHATSAPP-006` a tiempo las dos veces. No se leyeron para escribir las variantes.
- **Las otras tres:** `FAMILIAR-005` (plata para un familiar), `PREMIO-003` (DNI y foto) y `PREMIO-006` (sin pedido).

## El prompt

El mensaje de sistema de la congelada son 2.411 caracteres: seis párrafos de tarea y la salida.

| # | observación | qué se haría | ¿se prueba ahora? |
|---|---|---|---|
| 1 | **La regla del código depende de quién llama** («un banco, una empresa o un organismo no le pide…»). El estafador elige el disfraz. | Decirla por la intención | **Sí:** `c-codigo` |
| 2 | **El párrafo del DNI es parejo para todos los pretextos,** y no dice cuándo sí pesa. Va último, justo antes de la salida. | Reescribirlo por intención, con el número de trámite | **Sí:** `c-freno` |
| 3 | **El párrafo del número no agendado es un consejo oficial suelto.** | Poner los consejos completos | **Sí:** `c-consejos` |
| 4 | **«Que el número no esté agendado pesa»** no separa nada: por el alcance (ADR 0003), todas las llamadas vienen de un número no agendado. Aparece en motivos de FA («te llaman con un número desconocido», «no tiene agendado un ticket»). | Sacar la frase y dejar las dos reglas | No. Es un recorte, no busca avisar más |
| 5 | **La salida describe tres campos que no se generan** (`alerta_sugerida`, `motivo`, `evidencia`): 417 de sus 544 caracteres. No es texto muerto: en la etapa 3, sacarlo (`c-sin-alerta`) movió +3 estafas y +5 FA. | Dejar solo el riesgo | No. Ya se sabe que mueve todo |
| 6 | **El riesgo se define por «qué tan probable es que sea una estafa»,** o sea por quién es OTRA. La política mira lo que pide. Un pedido de código con un pretexto inocente puede ser «poco probable que sea estafa» y quedar en 0,2. | Definirlo por el pedido | No. Cambia la escala, y `c-ancla` mostró que tocar esa línea mueve el medio |
| 7 | **«Cortar y llamar enseguida a otro número que le dictan»** tiene poca base y da 2 FA estrictas. | Aclarar que llamar uno mismo al número oficial es lo aconsejado | En parte: `c-consejos` lo dice |
| 8 | **El párrafo de cómo se arma una estafa es una sola oración de 800 caracteres,** con el disfraz, el gancho y los nueve pedidos. | Partirlo, con la lista aparte | No. Reordenar todo es otra prueba |

**Sobre acortar:** no hay un recorte neutro a la vista. Lo único que sobra sin discusión es la frase del punto 4 (unos
40 caracteres). El punto 5 acorta de verdad, pero ya mostró que cambia las cifras. Conviene dejarlos para después de
congelar, con su propia regla.
