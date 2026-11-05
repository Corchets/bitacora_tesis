> **Estado: borrador del 2026-11-03.** La sección de contribuciones debe completarse entre los cuatro integrantes.

# Capítulo 10: Gestión del proyecto

## 10.1. Modelo de proceso y planificación

El trabajo se organizó por hitos de resultado, sin fijar de antemano una arquitectura. GitHub Issues es el único backlog, cada tarea parte de un issue con definición de terminado, y cada semana queda registrada en una [bitácora](../gestion/bitacora/README.md) con el artefacto generado. Las decisiones viven en un [mapa](../gestion/MAPA-DECISIONES.md), y las duraderas, en un ADR.

| Hito | Resultado | Situación al 2026-11-03 |
|---|---|---|
| H1 · Acuerdo mínimo | Alcance, preguntas y ejemplo trabajado | Cerrado |
| H2 · Piloto y primeras pruebas | Piloto con audio y referencia humana | **Atrasado:** faltan #54, #32 y #39 |
| H3 · Primera integración | Replay de punta a punta | Hecho (#28, cerrado el 2026-11-03); sin reproducción registrada por otra persona |
| H4 · Desarrollo y selección | Comparación y elección | Elección tomada; faltan #33, #55 y #45 |
| H5 · Evaluación final | Test reservado | Sin correr (#52) |
| H6 · Entrega y defensa | Informe, demo y video | En curso (#53) |

Fechas del tutor: **todo al 90 % el 2026-11-15**, todo terminado el 2026-11-30, y entrega con presentación de 20 a 30 minutos entre el 2026-12-07 y el 2026-12-11. Falta el día exacto.

## 10.2. Evolución del alcance y decisiones

| Fecha | Decisión | Consecuencia |
|---|---|---|
| 2026-09-09 | Replay como base y VoIP como objetivo; PI1 y PI2 aprobadas; PSTN, deepfakes y biometría afuera | Alcance acotado |
| 2026-10-04 | Referencia mínima por conversación, sin etiquetar cada turno | Anotación viable |
| 2026-10-21 | Corpus v2: 297 conversaciones nuevas, 200 reservadas | Desarrollo más grande; sin revisión humana |
| 2026-10-28 | Tutor: API descartada, demo por Meet aprobada, meta 80–85 / 10–15, gama más alta | Baja la meta original de 95/5 y se define la demo |
| 2026-10-29 | Zipformer retirado por sus errores con voz real | Se prueba Parakeet |
| 2026-10-31 | WhatsApp Desktop fuera, porque BlackHole no funcionó con él | Demo por pestaña de Chrome |
| 2026-11-02 | Opción B por defecto; corrida por Meet | Primer recorrido con voz real |
| 2026-11-03 | [ADR 0001](../ingenieria/adr/0001-parakeet-filtro-y-gemma4-e2b-con-tito-viejo.md): Parakeet con filtro y Tito viejo con E2B | D09 resuelta |

**Cambios respecto del plan.**
- La arquitectura pasó de VoIP propia a captura por canal.
- La referencia de hardware pasó de la gama media a la más alta.
- La selección se resolvió antes del piloto revisado, que era su condición original. El plan lo pedía al revés: es una desviación que se declara.
- El piloto de 14 conversaciones sigue pendiente; el equipo tiene previsto hacer esas llamadas.

## 10.3. Riesgos y mitigaciones

La matriz completa está en el [registro de riesgos](../gestion/REGISTRO-RIESGOS.md). Los más relevantes hoy:

| ID | Riesgo | Estado |
|---|---|---|
| R28 | Test sin referencia humana | Abierto; lo mitigan las llamadas y la muestra común |
| R27 | La configuración rinde peor en el test | Abierto; se informa aunque sea desfavorable |
| R08 | Modelo pesado para el móvil | Materializado en computadora; sin medir en teléfono |
| R23 | La demo falla en la sala | Mitigado con plan B y video; falta confirmar el ensayo en sala |
| R24 | Pérdida de grabaciones | **Materializado** el 2026-11-02; sigue abierto |
| R17 | Desincronización entre ramas y copias | Recurrente; se corrigen citas al cerrar issues |

**Lección de R24.** Una copia de trabajo se borró tras comprobar `git status` y los commits sin subir, que no muestran lo que Git ignora. Mateo tampoco tenía copia. Se agregó al procedimiento la revisión de archivos ignorados antes de borrar, y un paso de resguardo al terminar cada corrida.

## 10.4. Herramientas

Se usaron Git y GitHub para código e issues, y copias de trabajo separadas por tarea. La [ayuda memoria visual](../../ayuda-memoria/README.md) y un tablero personal resumen el estado.

**Uso de asistentes de IA.** Según registra la bitácora, participaron Claude, Codex y Gemini en implementación, revisión técnica y redacción. Corpus v2 es de redacción asistida. Una revisión por IA no sustituye a la revisión humana. **[Acordar cómo se declara en el informe final.]**

## 10.5. Contribuciones y carga de trabajo

> **[Completar entre los cuatro.]** Lo siguiente es solo lo que surge de bitácoras y documentos, y no representa el reparto completo.

| Integrante | Registrado en el repositorio |
|---|---|
| Ignacio Albarracín | Laboratorio inicial y reglas; Tito y sus particiones (#68, #95); corridas en Linux con GPU |
| Mateo Antenucci | Referencia mínima de anotación; propuesta de acumulación del puntaje; resguardo acordado de los materiales |
| Luciano Grosso | Panel de llamada y Presentación; ASR con voz real (#94); corpus v2; integración de Tito con Gemma 4 |
| Evaristo Villalobo | Corridas en Windows |
