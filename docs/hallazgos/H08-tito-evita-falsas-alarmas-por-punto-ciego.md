# H08 — Las falsas alarmas que Tito «evita» son casi todas punto ciego

- **Fecha:** 2026-11-06
- **Tipo:** resultado
- **Estado:** vigente
- **Evidencia:** [análisis del 2026-11-06](../../experiments/slm-directo/analisis/2026-11-06-tito-compuerta-sensible/README.md), reproducible con `revisar.py`.
- **Afecta a:**
  - la decisión del filtro en [#51](https://github.com/Corchets/bitacora_tesis/issues/51);
  - el riesgo [R25](../gestion/REGISTRO-RIESGOS.md);
  - la [propuesta de configuración](../evaluacion/PROPUESTA-CONFIGURACION-DETECTOR.md#decisión-1-el-filtro-tito);
  - los capítulos [5](../tesis/CAP-05-DISENO-Y-ARQUITECTURA.md#551-detector), [8](../tesis/CAP-08-RESULTADOS-EXPERIMENTALES.md#831-matriz-101-10-modelos-en-20-conversaciones), [9](../tesis/CAP-09-DISCUSION.md) y [11](../tesis/CAP-11-CONCLUSIONES.md#112-hipótesis-respaldadas-o-no).

## Qué encontramos

**Criterio:** Tito no decide, solo despierta al SLM. Una falsa alarma que desaparece porque Tito no vio la línea sensible no es un mérito.

- **Lectura JSON en los 150 casos.** Con Tito, las falsas alarmas bajan de 19 a 14 con v1 y de 17 a 13 con v4. Las 7 legítimas distintas que desaparecen son punto ciego. En todas, el SLM avisaba en una línea con algo sensible que Tito puntuó casi en cero, por ejemplo «Me llegó por SMS un código para activar WhatsApp» (0,234). En corpus_v2, Tito no cambia las falsas alarmas.
- **Lectura por token (#143).** De 5 legítimas más, 2 son punto ciego, 1 es dudosa y 2 están bien filtradas. Con un Tito sin punto ciego, la ventaja que queda sale de dos llamadas médicas, en una lectura que no se adoptó.
- **Cobertura.** Cuando aparece la primera línea sensible, el SLM ya está despierto en 62 de 64 estafas, pero solo en 14 de 43 legítimas.
- **Lo que cuesta.** `CV2-D-V-PREMIO-001` se pierde («El DNI completo y una foto del frente», 0,024), y el aviso de `CV2-D-V-BANCO-007` se atrasa diez líneas con v1.
- **Matriz #101.** Con E2B, la falsa alarma del SLM solo (`CV2-D-L-BANCO-001`) no la filtró Tito, que había activado en la línea 1. En los 10 modelos, de 24 falsas alarmas que desaparecen, 13 son filtrado honesto, casi todas de modelos chicos que avisan en las primeras líneas; 6 son punto ciego, y en 5 Tito ya había activado.

## Qué tan seguro es

- La línea sensible sale de marcas sin revisión humana. Algunas faltan: `MEDICO-004` pide la fecha de nacimiento sin marca.
- Tito no registra puntajes después de activar.
- Todo es material de desarrollo ya visto.

Aun así, el resultado no depende de casos dudosos: en la lectura JSON, los 7 casos tienen la línea sensible marcada antes del aviso.

## Qué cambia

- La baja de falsas alarmas no es un argumento a favor de Tito. Su aporte medido es la mitad de las consultas, a cambio de una estafa perdida y avisos atrasados.
- Una compuerta se evalúa por su **cobertura**: si el SLM está despierto en la primera línea sensible. No por las falsas alarmas que desaparecen. Ver [H09](H09-tito-clasificador-en-vez-de-compuerta.md).
- Se agregaron notas con fecha donde se afirmaba lo contrario. La tesis queda marcada con `Corregir (#51)`.

> **Estado: propuesta sin discutir.** Para [#51](https://github.com/Corchets/bitacora_tesis/issues/51):
> - SLM solo como configuración principal.
> - Tito como ablación en la corrida de la reserva. Una falsa alarma que desaparece cuenta solo si el SLM estaba despierto en la primera línea sensible, y la cobertura se informa como métrica propia de la compuerta.
