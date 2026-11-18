> **Estado: borrador del 2026-11-03.** [D07](../gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental) siguen abiertas: lo marcado como propuesta se ajusta cuando se congelen. El detalle está en el [protocolo experimental](../evaluacion/PROTOCOLO-EXPERIMENTAL.md).

# Capítulo 4: Metodología

## 4.1. Diseño del estudio y variables

Es un estudio experimental sobre un corpus controlado. La llamada se procesa como un flujo: en cada actualización, el detector solo recibe lo disponible hasta ese momento.

| Elemento | Datos | Comparación | Salida |
|---|---|---|---|
| PI1 | Prefijos, clase y tiempos | Configuración final y reglas | Detección y falsas alarmas |
| PI2 | `T_A`, `T_R`, `T_C` | Márgenes del aviso | `L_R`, `L_C` y `Preventive@δ` |
| E2 | Evidencia seleccionada | Motivo mostrado contra evidencia | Correspondencia y errores de explicación |

No se compara el mismo detector sobre texto manual y sobre ASR (E1, [#54](https://github.com/Corchets/bitacora_tesis/issues/54)): las métricas de detección salen de conversaciones escritas, y el ASR se mide aparte con voz real.

## 4.2. Construcción del corpus y muestreo

El [método del corpus](../corpus/METODO-CREACION-CORPUS.md) parte de una modalidad identificada en fuentes oficiales o académicas, diseña una situación ficticia y le da una contraparte legítima comparable. Los participantes reciben fichas de rol que orientan sin imponer frases.

El material disponible es el siguiente:

| Conjunto | Contenido | Estado |
|---|---|---|
| 53 antecedentes | 29 vishing y 24 negativos difíciles, escritos | Desarrollo; se conservan para reproducir corridas |
| [Corpus v2](../../experiments/slm-directo/casos/DISENO-CORPUS-V2.md), desarrollo | 46 vishing y 51 legítimas, de redacción asistida | Desarrollo |
| Corpus v2, reserva | 100 vishing y 100 legítimas, de redacción asistida | Test reservado candidato, sin correr |
| Diálogos con voz real | 4 guiones (3 estafas y 1 legítima), 9 llamadas y 2 voces | Prueba del recorrido, fuera de `corpus_v2` |

Ninguno de los 350 casos escritos tiene `revision_humana` en verdadero. Corpus v2 incluye 30 estafas que terminan antes del pedido y legítimas con pedidos razonables o menciones sin pedido, para no reducir el problema a palabras clave.

> **Estado: propuesta sin discutir.** El piloto original era de 14 conversaciones con voz ([D06](../gestion/MAPA-DECISIONES.md#d06--definir-corpus-y-piloto)) y sigue pendiente (#54). El equipo va a hacer llamadas con ese fin. Su alcance definitivo y la composición final del corpus se cierran en D08.

## 4.3. Taxonomía, anotación y acuerdo

El [manual de anotación](../corpus/MANUAL-ANOTACION.md) define una referencia mínima por conversación: clase, `T_R` y `T_C` cuando corresponden, evidencia seleccionada y notas. No se etiqueta cada turno. La ausencia de una etiqueta no significa que la maniobra esté ausente, por lo que no se promete un macro-F1 de las doce etiquetas candidatas.

`T_R` es el inicio del primer pedido de alto riesgo y `T_C`, el inicio del primer cumplimiento observable. Un disparo de reglas nunca determina la referencia.

> **Estado: propuesta sin discutir.** Falta que los cuatro anoten de forma independiente una muestra común y que se adjudiquen los desacuerdos (#32). Es el principal pendiente metodológico: hasta entonces, las marcas son provisionales.

## 4.4. Particiones y prevención de fuga

Una conversación conserva juntos sus turnos y fragmentos. Traister et al. (2026) muestran que las particiones que repiten llamantes o guiones inflan el rendimiento, y por eso se propone separar por semilla y por voz.

Las [particiones de Tito](../../experiments/slm-directo/PARTICIONES-TITO-2026-10-29.json) son disjuntas por grupo, con 34 conversaciones de entrenamiento, 10 de validación, 10 de diagnóstico, 3 de regresión, 20 de comparación y 45 excluidas por su relación con la comparación. La reserva final queda fuera de ellas: el código la rechaza por identificador.

**Fuga conocida.** Los 200 casos reservados son públicos en GitHub desde el 2026-10-23, en la rama `laboratorio-luciano`, por decisión de Luciano ([copia pública](../../experiments/slm-directo/casos/README.md#copia-pública-laboratorio-main)). Se mantienen fuera de `laboratorio-main` y no aparecen en ninguna corrida versionada. Por eso solo valen como test limpio para modelos publicados antes de esa fecha: Gemma 4 E2B lo cumple: se publicó el 2026-03-31, según el [registro de versiones de Google](https://ai.google.dev/gemma/docs/releases?hl=en) (R05). Tito viejo se ajustó con un banco anterior, del commit `bb542e1`.

## 4.5. Línea base, modelos y protocolo

La línea base son las **reglas léxicas**. La configuración evaluada es la del [ADR 0002](../ingenieria/adr/0002-detector-gemma4-e2b-solo-con-prompt-c-premisa.md), sobre el ASR del [ADR 0001](../ingenieria/adr/0001-parakeet-filtro-y-gemma4-e2b-con-tito-viejo.md): Gemma 4 E2B solo, con el prompt `c-premisa-corte-riesgo`, aviso con riesgo ≥ 0,3 y consulta solo en las líneas de OTRA. Se congela antes del test y se corre una sola vez ([#52](https://github.com/Corchets/bitacora_tesis/issues/52)). Tito no se evalúa, ni como configuración ni como ablación: se cita solo como evidencia de lo que se probó ([H08](../hallazgos/H08-tito-evita-falsas-alarmas-por-punto-ciego.md), [H09](../hallazgos/H09-tito-clasificador-en-vez-de-compuerta.md)).

> **Estado: propuesta sin discutir.** El [protocolo](../evaluacion/PROTOCOLO-EXPERIMENTAL.md#5-política-de-alerta-a-congelar-opciones-y-evidencia-observada) propone como política de referencia el aviso único en el primer `true` válido, que es la que usó #101. Se congela en D08.

> **Nota del 2026-11-11:** el [ADR 0002](../ingenieria/adr/0002-detector-gemma4-e2b-solo-con-prompt-c-premisa.md) fija el aviso: uno solo por llamada, en la primera consulta con riesgo ≥ 0,3. Lo que sigue abierto en D08 es cómo se mide.

## 4.6. Métricas y análisis estadístico

Las definiciones viven en [METRICAS.md](../evaluacion/METRICAS.md):

- **Márgenes:** `L_R = T_R − T_A` y `L_C = T_C − T_A`. Positivo significa que el aviso llegó antes. Se informan su mediana y su rango intercuartil, y cuántas conversaciones permiten calcularlos.
- **`Preventive@δ(X)`:** proporción de llamadas de vishing con `T_A ≤ X − δ`. Las llamadas sin alerta quedan en el denominador.
- **Falsas alarmas:** llamadas legítimas con al menos una alerta, sobre las legítimas evaluadas, desglosadas por tipo.
- **ASR:** WER, CER y recall de términos críticos.
- **Costo:** `RTF`, demora y memoria, con el hardware declarado.

Las proporciones se informan con conteos, denominadores e intervalo de Wilson al 95 %. La precisión se analiza con frecuencias hipotéticas de fraude, como análisis de sensibilidad, no como estimación de uso real:

```text
precision(p) = (p × r) / (p × r + (1 − p) × f)
```

En texto sin tiempos, el aviso se informa por línea: no se inventan segundos.

> **Estado: propuesta sin discutir.** Los valores `δ` de 5, 10 y 20 s son hipótesis de trabajo sin fuente, y `T_C` es la referencia principal propuesta. Se acuerdan en D08.

## 4.7. Consideraciones éticas y plan de datos

Se usan datos ficticios y participantes adultos que consienten. Audio, consentimientos firmados y datos identificables quedan fuera de Git; el repositorio conserva el método, los metadatos y las salidas sin WAV. Una evaluación sin revisión humana se declara como tal.

La pérdida del audio original de la corrida por Meet, el 2026-11-02, mostró que ese resguardo debe incluir una copia ([registro](../../experiments/voip/corridas/2026-11-02-voz-real-meet.md#audio-original-perdido)).
