# Preguntas de investigación y evaluaciones

## Decisión metodológica

El proyecto tendrá **dos preguntas centrales**. El impacto del ASR será una
comparación diagnóstica obligatoria y la explicación será un objetivo secundario.
Así, el trabajo no se fragmenta en cuatro tesis distintas.

Las preguntas no se hacen a participantes: son lo que los experimentos deben
responder. No presuponen un resultado favorable.

## PI1 — Detección incremental

### Pregunta

¿Con qué desempeño y tasa de falsas alarmas puede detectarse vishing utilizando solo la parte de la conversación disponible hasta cada instante?

### Qué busca responder

Si las señales acumuladas permiten distinguir una llamada fraudulenta de una legítima antes de escucharla completa, y desde qué punto la predicción se vuelve estable.

### Experimento

Ejecutar el detector con prefijos sucesivos de cada conversación: primeros turnos, 25%, 50%, 75% y 100%, o ventanas temporales equivalentes.

### Resultados que se reportan

- Precision, recall, F1 y AUPRC por prefijo.
- Porcentaje de llamadas legítimas con al menos una alerta.
- Falsas alertas por hora.
- Curva de riesgo a lo largo del tiempo.

No se busca un número elegido de antemano. Se busca caracterizar el compromiso: detectar antes normalmente implica más falsas alarmas.

## PI2 — Utilidad temporal

### Pregunta

¿Con cuánto margen respecto del primer pedido riesgoso y de la primera acción de cumplimiento puede emitirse una alerta estable?

### Marcas necesarias

- `T_A`: momento de primera alerta estable.
- `T_R`: comienzo del primer pedido de alto riesgo.
- `T_C`: comienzo de la primera acción de cumplimiento ficticio.

Ejemplo:

```text
00:30 “Tenemos que resolverlo ahora”                  urgencia
00:45 “No cortes la llamada”                          aislamiento
00:58 “Decime el código de seis dígitos”              T_R
01:04 “El código es...”                               T_C
```

Si la alerta aparece a los 00:48, no anticipa el pedido, pero aparece 16 segundos antes de que el rol de víctima comience a compartir el código.

### Resultados que se reportan

- `L_R = T_R - T_A`.
- `L_C = T_C - T_A`.
- `Preventive@5s`, `Preventive@10s` y `Preventive@20s`.
- Casos detectados después del evento o nunca detectados.

El resultado buscado es una distribución honesta de márgenes, no demostrar por fuerza que todos son positivos.

## E1 — Impacto del ASR, evaluación diagnóstica obligatoria

### No es una pregunta central

El producto recibe audio; por eso hay que separar errores del detector de errores de transcripción. Esta comparación es una evaluación del pipeline y puede aparecer como subpregunta de PI1/PI2 o como experimento de ablación.

### ¿Requiere llamadas reales?

No. Requiere que las conversaciones simuladas tengan:

1. audio grabado;
2. transcripción manual revisada;
3. transcripción producida por el ASR local.

Se ejecuta el mismo detector dos veces:

```text
Transcripción manual ─┐
                     ├→ mismo detector → comparar
Audio → ASR local ───┘
```

### Qué resultado se busca

- WER global y recall de términos críticos.
- Diferencia de F1/AUPRC entre transcripción manual y ASR.
- Diferencia de falsas alarmas.
- Segundos de anticipación ganados o perdidos.
- Latencia y real-time factor.

Interpretaciones posibles:

- buen resultado manual y malo con ASR: el cuello de botella es la transcripción;
- ambos malos: falta señal temprana, datos o capacidad del detector;
- ambos similares: el ASR elegido es suficiente para este corpus;
- ASR mejora algún caso: revisar si normalización o ruido del texto manual explica el efecto, sin asumir que la mejora es general.

Si el alcance cambiara a un detector que recibe texto y no audio, E1 dejaría de ser
necesaria. Mientras el producto prometa escuchar voz, esta comparación es parte de
una evaluación responsable.

## E2 — Explicación, objetivo secundario

El sistema puede identificar señales como suplantación, urgencia, aislamiento,
pedido de código, pedido de secreto o transferencia. Esas etiquetas alimentan
mensajes deterministas.

Se reportará macro-F1 por etiqueta y correspondencia entre motivo mostrado y
etiqueta real. Una prueba con usuarios solo se hará si se aprueba y no compromete
PI1/PI2.

## Matriz pregunta–evidencia

| Elemento | Datos necesarios             | Comparación                       | Salida                                   |
| -------- | ---------------------------- | --------------------------------- | ---------------------------------------- |
| PI1      | prefijos, clase y timestamps | reglas vs modelo; prefijos        | curvas desempeño-tiempo y falsas alarmas |
| PI2      | `T_A`, `T_R`, `T_C`          | políticas de alerta               | márgenes y Preventive@δ                  |
| E1       | audio, texto manual y ASR    | misma detección, entrada distinta | degradación, errores críticos y latencia |
| E2       | etiquetas por turno          | predicción vs anotación           | fidelidad de explicación                 |

## Propuesta al profesor

Pedir aprobación para PI1 y PI2 como preguntas centrales, E1 como evaluación
diagnóstica obligatoria y E2 como objetivo secundario. Preguntar si prefiere que el
informe use la expresión “preguntas de investigación” o que estas aparezcan como
criterios de evaluación dentro de los objetivos específicos.
