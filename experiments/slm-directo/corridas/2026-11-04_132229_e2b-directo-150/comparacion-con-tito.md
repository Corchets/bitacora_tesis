# Gemma 4 E2B solo contra Tito viejo → E2B en las 150 de desarrollo

> **Estado: propuesta sin discutir.** Diagnóstico sobre material de desarrollo, sin
> revisión humana de casos ni de `T_R`. No cambia la configuración del
> [ADR 0001](../../../../docs/ingenieria/adr/0001-parakeet-filtro-y-gemma4-e2b-con-tito-viejo.md)
> ni resuelve [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

## Corridas comparadas

| | SLM solo | Tito viejo → SLM |
|---|---|---|
| Carpeta | `2026-11-04_132229_e2b-directo-150` (esta) | `2026-11-04_003715_e2b-tito-viejo-150` (rama `corrida-e2b-tito-viejo-150`) |
| Modelo y prompt | `gemma4:e2b-it-q4_K_M`, `tarea`, `ab`, `num_ctx` 4096, seed 42 | igual |
| Código | `833a3fb` con cambios locales sin commit | igual |
| Máquina | PC Windows 11, 12 núcleos, 31,9 GB, Ollama 0.40.14 | igual |

Las dos corridas usan el mismo código, la misma máquina y la misma política de aviso
único. Lo único que cambia es Tito. El script de la comparación está en
[`comparar_directo_vs_tito.py`](comparar_directo_vs_tito.py).

## Resultado global

| | SLM solo | Tito → SLM |
|---|---|---|
| Estafas con aviso | **55/75 (73 %)** | 51/75 (68 %) |
| Estafas con pedido (`T_R`) con aviso | 54/64 | 51/64 |
| Avisos antes del pedido | **25** | 17 |
| Avisos en el pedido | 25 | 29 |
| Avisos después del pedido | 4 | 5 |
| Falsas alarmas | 18/75 (24 %) | **13/75 (17 %)** |
| · legítimas comunes | 3/51 | 5/51 |
| · legítimas difíciles | 15/24 | **8/24** |
| Consultas al SLM | 2.218 | **1.179** (Tito omitió 1.139 líneas) |
| Fallos de JSON o tiempo | 0 | 0 |
| Mediana por consulta | 291 ms | 296 ms |

Ninguna de las dos llega a la meta del tutor (80–85 % con 10–15 % de falsas alarmas).
El SLM solo detecta más y antes, pero tiene más falsas alarmas. Tito → SLM filtra
falsas alarmas y consume la mitad de las consultas, a cambio de 4 estafas y de avisar
más tarde.

## ¿Detecta antes?

En las 50 estafas en las que avisan los dos:

- **36** avisan en la misma línea.
- **10** avisa antes el SLM solo, por una diferencia media de 4,2 líneas (por ejemplo,
  `BANCO-007`: línea 6 contra 17, y `BANCO-002`: 11 contra 18).
- **4** avisa antes Tito → SLM (`BANCO-010`, `WHATSAPP-003`, `PREMIO-004` y `WHATSAPP-006`).

En los 10 casos en que el SLM solo se adelanta, en **3** la culpa es de la compuerta:
Tito todavía no había activado al SLM (`BANCO-004`, `BANCO-007` y `BANCO-008`). En los
**otros 7**, el SLM sí fue consultado en esa línea y respondió `alerta_sugerida: false`.

## Dónde pierde Tito → SLM

| Caso | `T_R` | Aviso del SLM solo | Qué pasó con Tito |
|---|---|---|---|
| `CV2-D-V-PREMIO-001` | 10 | 10 | **Compuerta.** Tito nunca pasó de 0,23 («el DNI completo y una foto del frente») y el SLM no se consultó nunca. |
| `CV2-D-V-PREMIO-002` | 13 | 13 | **Respuesta del SLM.** Consultado en el pedido, devolvió riesgo 0,3 sin alerta. El SLM solo devolvió riesgo 0,3 *con* alerta. |
| `CV2-D-V-SOPORTE-001` | 14 | 10 | **Respuesta del SLM.** Consultado en el pedido, devolvió riesgo 0,5 sin alerta. |
| `TR-01-pedido-indirecto-digitos` | 8 | 5 | **Respuesta del SLM.** Consultado desde antes del pedido, no alertó nunca. |
| `CV2-D-V-BANCO-011` | — | 17 | Sin pedido de referencia. El SLM solo avisa cuando la víctima ya dice «esto no me cierra»: es una detección débil. |

Tito → SLM gana solo `TR-04-pedido-tras-charla-larga` (línea 27, con `T_R` 26).

**La compuerta casi nunca es el problema.** En 57 de las 64 estafas con pedido, Tito
activa al SLM *antes* del pedido; en 5, justo en el pedido; en 1, después; y en 1,
nunca. Una vez activado, el SLM queda consultado en todas las líneas siguientes.

**El problema está en lo que responde el SLM con Tito adelante.** En las 1.083 líneas
consultadas en las dos corridas, el SLM cambia de respuesta en 21 (2 %):

| | Alerta solo sin Tito | Alerta solo con Tito |
|---|---|---|
| Estafas | **10** | 5 |
| Legítimas | 3 | 3 |

Con Tito, el SLM recibe además el bloque de «indicio»: la *primera* línea que Tito
marcó, con su puntaje y la aclaración de que puede descartarlo
([`filtro_tito.py`](../../filtro_tito.py)). Ese indicio suele apuntar a una línea
temprana y poco relevante. Por ejemplo, en `PREMIO-002` señala la línea 3, «Te ganaste un
parlante portátil…», con puntaje 1,0. Cuando el pedido real llega mucho después, el
modelo tiende a «descartar el indicio» y no alerta. Pasa mayormente en casos límite,
con riesgo 0,3–0,5.

> No está separado el efecto del indicio del no determinismo de la GPU. Con la misma
> seed y la misma entrada, Ollama en GPU puede variar la salida. Para separarlos hay
> que repetir una corrida.

## Falsas alarmas

- **Tito filtra bien en las legítimas difíciles:** 15 → 8. Saca, entre otras,
  `LAB-anses-canal-oficial`, `LAB-banco-app-parafrasis`, `LG-ORG-TURNO-01`,
  `LG-SUPPORT-INFO-01`, `LG-WA-CONSULTA-01`, `TR-03-negacion-y-consejo` y
  `TR-05-asado-con-transferencia`.
- **En las legítimas comunes saca 1 (`BANCO-001`) pero agrega 3** que el SLM solo no marca: `BANCO-005`,
  `FAMILIAR-002` y `FAMILIAR-005`. El modelo es el mismo, así que esas 3 salen de la
  diferencia en el prompt (indicio) o del no determinismo.
- Las comparten las dos condiciones: `BANCO-002` y `BANCO-010` (piden los últimos
  cuatro dígitos), `LAB-arca-canal-oficial`, `LAB-banco-revisa-app`,
  `TR-06-banco-alerta-legitima`, `TR-08-frase-cortada-candado`,
  `TR-13-turno-medico-pide-dni`, y, en distinta línea, `LAB-no-bajes-nada`,
  `LG-BANK-VERIF-01` y `TR-11-familiar-real-pide-plata`. El modelo confunde mencionar
  o desaconsejar un pedido con hacerlo.

## Las que no detecta ninguno (19)

Todas son de `corpus_v2` salvo `TR-12-corta-antes-del-pedido`. Son 11 sin pedido de
referencia (la llamada corta antes, o el pedido es indirecto) y 8 con pedido:

- **Transferencias de familiar** (`FAMILIAR-004/005/006`). El pedido es condicional
  y la referencia podría ser discutible.
- **Datos personales** (`ORGANISMO_PREVISIONAL-003/004` y `PREMIO-003`).
- **Pedidos de secreto o código** (`SOPORTE-005` y `WHATSAPP-004`).
- **Transferencia** (`BANCO-003`).

Esto no se arregla con Tito. Es el techo del SLM con este prompt.

## Por grupo

| Grupo | Estafas: solo / Tito | Falsas alarmas: solo / Tito |
|---|---|---|
| `corpus_v2` | 28/46 · 24/46 | 3/51 · 5/51 |
| `laboratorio` | 16/16 · 16/16 | 5/10 · 3/10 |
| `piloto_escrito` | 7/7 · 7/7 | 4/7 · 1/7 |
| `trampa` | 4/6 · 4/6 | 6/7 · 4/7 |

Toda la pérdida de Tito → SLM está en `corpus_v2`, el grupo más largo y con pedidos más
tardíos. Toda su ganancia en falsas alarmas está en `laboratorio`, `piloto_escrito` y
`trampa`.

## Contrafáctico: Tito como compuerta pura, sin indicio

Si Tito solo decidiera *cuándo* consultar y el SLM recibiera el mismo prompt que
cuando corre solo, sus respuestas serían las del SLM solo desde la activación de Tito.
Con eso, a partir de las dos corridas, la estimación es:

- **Estafas:** entre 50 y 54 de 75. En 4 casos el SLM solo avisó antes de que Tito
  activara y no se sabe qué habría dicho después.
- **Falsas alarmas:** entre 10 y 15 de 75. Hay 5 casos en la misma situación.

Es una estimación, no una medición. Sugiere que la compuerta pura conservaría casi
todo el filtrado de falsas alarmas sin perder las estafas por el indicio.

## Próximos pasos propuestos

1. **Correr Tito → SLM sin el bloque de indicio** (compuerta pura), con la misma
   configuración, para confirmar el contrafáctico. Es una variante del ADR 0001, así
   que la decide el equipo.
2. **Repetir una de las dos corridas** para medir cuánto de las 21 diferencias es no
   determinismo.
3. **Revisar con ojos humanos** `T_R` en `FAMILIAR-004/005/006` y en las 11 estafas
   sin pedido de referencia, antes de leer más en la sensibilidad.
4. No ajustar prompt ni umbral mirando estos 150 casos sin dejarlo declarado: el test
   reservado sigue intacto y es donde se mide.
