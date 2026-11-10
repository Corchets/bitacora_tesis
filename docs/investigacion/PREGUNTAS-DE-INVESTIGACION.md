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

### Marcas y métricas de evaluación

Para responder PI2 se analizan los márgenes de anticipación temporal respecto del pedido de alto riesgo (`L_R = T_R - T_A`) y respecto de la acción de cumplimiento ficticia (`L_C = T_C - T_A`), además de la tasa de llamadas advertidas con margen suficiente (`Preventive@δ`).

La definición matemática rigurosa, el tratamiento estadístico y el ejemplo temporal viven en [METRICAS.md](../evaluacion/METRICAS.md).

El objetivo es obtener una distribución honesta de márgenes y no forzar números arbitrarios.

## E1 — Efecto del ASR: fuera de la evaluación

> **Decisión (2026-11-10, [#54](https://github.com/Corchets/bitacora_tesis/issues/54)):** E1 no se mide. Hacían falta llamadas grabadas con
> transcripción manual revisada y no hay tiempo de grabarlas antes de la entrega. Con las
> pocas llamadas que se podrían grabar, un cambio en la detección difícilmente se notaría.

E1 comparaba el mismo detector sobre la transcripción manual y sobre la del ASR, para separar
los errores del detector de los de transcripción. En su lugar queda un límite: las métricas
de detección salen de conversaciones escritas, no de audio transcripto. El ASR se midió
aparte, con voz real del equipo, contra el guion y con ruido de fondo
([PLAN-VOZ-REAL.md](../../experiments/asr-local/PLAN-VOZ-REAL.md)), y el recorrido completo se probó en 9 llamadas guionadas
([corrida del 2026-11-02](../../experiments/voip/corridas/2026-11-02-voz-real-meet.md)). El límite está en el
[protocolo §7.2](../evaluacion/PROTOCOLO-EXPERIMENTAL.md#72-amenazas-a-la-validez).

## E2 — Explicación, objetivo secundario

Se revisa si el motivo mostrado corresponde a evidencia disponible en la llamada,
sin inventar una maniobra ni repetir el mismo mensaje para todos los casos. La
referencia mínima del piloto permite una revisión de casos y fragmentos seleccionados.

No se promete macro-F1 de doce etiquetas con una anotación parcial. Una medición
exhaustiva por etiqueta requiere datos y protocolo adicionales acordados en D07/D08.
Una prueba con usuarios es una extensión condicionada al avance de PI1/PI2.

## Matriz pregunta–evidencia

| Elemento | Datos necesarios             | Comparación                       | Salida                                   |
| -------- | ---------------------------- | --------------------------------- | ---------------------------------------- |
| PI1      | prefijos, clase y timestamps | reglas vs modelo; prefijos        | curvas desempeño-tiempo y falsas alarmas |
| PI2      | `T_A`, `T_R`, `T_C`          | políticas de alerta               | márgenes y Preventive@δ                  |
| E2       | evidencia seleccionada       | motivo mostrado vs evidencia     | correspondencia y errores de explicación |
