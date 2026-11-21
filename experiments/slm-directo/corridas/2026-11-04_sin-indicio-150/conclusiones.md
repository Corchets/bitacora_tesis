# SLM solo, Tito con indicio y Tito sin indicio: conclusiones (2026-11-04)

> **Estado: propuesta sin discutir.** Diagnóstico sobre las 150 conversaciones de desarrollo,
> sin revisión humana de casos ni de `T_R`. No toca el test reservado. El detalle caso por caso
> está en [comparacion.md](comparacion.md).

## Qué se corrió

- **Dónde:** Colab, GPU T4, con [COLAB-SIN-INDICIO.ipynb](../../colab/COLAB-SIN-INDICIO.ipynb).
- **Versión:** commit `4916eada648c2f7c394ae82ed43c90df47ab6573` (rama `slm-sin-indicio`, archivada en el tag `archivo/slm-sin-indicio`) y Ollama 0.40.14.
- **Modelo:** `gemma4:e2b-it-q4_K_M` con prompt `tarea` y hablantes `ab`, sobre las 150 conversaciones de desarrollo (75 estafas y 75 legítimas).
- **Corridas:**
  - [a](a/2026-11-04_194015_sin-indicio-a-solo-y-con-indicio/): SLM solo y Tito → SLM con indicio, 32,2 min.
  - [b](b/2026-11-04_201218_sin-indicio-b-tito-sin-indicio/): Tito → SLM sin indicio, 11,0 min.
  - [c](c/2026-11-04_202259_sin-indicio-c-solo-repeticion/): repetición de SLM solo, 16,2 min, para medir el no determinismo.
- **Reproducibilidad:** [pip-freeze.txt](pip-freeze.txt), [commit.txt](commit.txt), [script-sha256.txt](script-sha256.txt) y [ollama-version.txt](ollama-version.txt).
- **Calidad de la corrida:** sin casos sin procesar y sin fallos de JSON ni de tiempo.

## Cuadro comparativo

| | SLM solo | Tito con indicio | Tito sin indicio | SLM solo (repetición) |
|---|---|---|---|---|
| Estafas con aviso (de 75) | 55 (73 %) | 50 (67 %) | 54 (72 %) | 54 (72 %) |
| Aviso antes del pedido (de 64 con `T_R`) | 25 | 18 | 24 | 24 |
| Falsas alarmas (de 75 legítimas) | 19 (25 %) | 12 (16 %) | 14 (19 %) | 20 (27 %) |
| · en legítimas difíciles (de 24) | 15 | 7 | 10 | 16 |
| Consultas al SLM | 2.214 | 1.189 | 1.140 | 2.225 |

## Conclusiones

1. **El no determinismo es chico pero alcanza para mover 1 o 2 casos.** Repetida tal cual, la
   corrida de SLM solo cambia la respuesta en 2 de 2.213 líneas, pero eso le cuesta una estafa y le
   suma una falsa alarma. Diferencias de 1 o 2 casos entre configuraciones son ruido.
2. **Tito reduce el costo a la mitad.** Con Tito se hacen alrededor de 1.150 consultas en vez de
   2.200, porque omite unas 1.140 líneas.
3. **El indicio perjudica la detección.** Con indicio se pierden 5 estafas que sin indicio se
   detectan (`CV2-D-V-BANCO-003`, `CV2-D-V-BANCO-011`, `CV2-D-V-FAMILIAR-003`,
   `CV2-D-V-PREMIO-002` y `TR-01-pedido-indirecto-digitos`) y los avisos antes del pedido bajan
   de 24 a 18. La activación de Tito es la misma en ambas condiciones: la diferencia la produce
   el bloque de indicio en el prompt del SLM.
4. **Tito sin indicio es la configuración más equilibrada de las tres.** Detecta lo mismo que el
   SLM solo dentro del ruido (54 contra 55), da 5 falsas alarmas menos (14 contra 19) y hace la
   mitad de consultas. Sobre las líneas que consultan los dos, la respuesta cambia en el 0,3 %.

   > **Nota del 2026-11-06:** las 5 falsas alarmas menos no son mérito de Tito. En esas legítimas, el SLM avisaba en una línea
   > sensible que Tito no vio; en corpus_v2 son 4 = 4. Ver [H08](../../../../docs/hallazgos/H08-tito-evita-falsas-alarmas-por-punto-ciego.md).
5. **Hay 19 estafas que ninguna configuración detecta**, siempre las mismas: varias de
   organismo previsional, familiar, soporte técnico, WhatsApp y premio, más `CV2-D-V-BANCO-012`
   y `TR-12-corta-antes-del-pedido`. `TR-04-pedido-tras-charla-larga` solo lo detecta Tito con
   indicio. Ese techo no depende de Tito sino del SLM o del prompt.

**Próximo paso sugerido:** adoptar Tito sin indicio como candidato y concentrar el trabajo en
las estafas que ninguna configuración detecta. Antes de convertirlo en decisión hay que
discutirlo en el equipo y validarlo fuera del material de desarrollo.

## Verificación agregada el 2026-11-05

Evaristo volvió a analizar estas mismas corridas en la rama `slm-sin-indicio` (los CSV son idénticos). Esa rama está archivada en el tag `archivo/slm-sin-indicio`. Su análisis agrega cuatro cosas:

- **Hipótesis escrita antes de correr:**
  - Se esperaban 54–55 estafas y salieron 54/75, con los mismos 24 avisos antes del pedido que el SLM solo.
  - En falsas alarmas se pedían 13/75 o menos y salieron 14/75.
- **Cambios por línea, en las líneas que consultan las dos condiciones:**
  - Con indicio, la respuesta del SLM cambia en el 2,2 % de las líneas respecto del SLM solo.
  - Sin indicio, en el 0,3 %. Entre el SLM solo y su repetición, en el 0,1 % (2 de 2.213).
  - Con indicio se perdían 13 alertas en estafas; sin indicio, 2.
  - A nivel de caso, la repetición igual movió una estafa y una falsa alarma, así que sigue valiendo la conclusión 1: diferencias de 1 o 2 casos son ruido.
- **Misma línea:** en 48 de las 54 estafas en que avisan los dos, Tito sin indicio avisa en la misma línea que el SLM solo.
- **Falsas alarmas por tipo:**
  - En las legítimas comunes hay 4/51 en todas las condiciones, salvo con indicio (5/51).
  - La diferencia entre el SLM solo y Tito está toda en las 24 legítimas difíciles, que no forman parte de la reserva.
