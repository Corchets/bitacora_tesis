# Detección incremental y explicable de vishing en español

**Universidad del Norte Santo Tomás de Aquino (UNSTA)**  
**Facultad de Ingeniería — Ingeniería en Informática (Plan 2008)**  
**Proyecto Final Integrador | Año 2026**  

- **Integrantes:** Albarracín Ignacio, Antenucci Mateo, Grosso Luciano, Villalobo Evaristo.  
- **Tutor:** Ing. Ernesto Rico.  
- **Defensa objetivo:** Última / penúltima semana de diciembre de 2026.

---

## 1. Sobre el proyecto

El proyecto diseña, implementa y evalúa un prototipo para la **detección temprana y explicable de vishing** (estafas por llamadas de voz) en español con foco en Argentina.

La clave del problema no es clasificar la llamada cuando ya terminó, sino **intervenir con suficiente anticipación**: advertir al usuario en tiempo real antes de que realice una acción de riesgo (entregar un código OTP, transferir dinero o instalar una aplicación de acceso remoto).

- **Inferencia local (*on-device*):** El audio y la transcripción se procesan en el dispositivo; ningún dato sale a la nube.
- **Métricas temporales:** Evaluación basada en el margen de intervención ($L_R = T_R - T_A$, $L_C = T_C - T_A$) y la tasa de prevención ($Preventive@\delta$), no solo en exactitud tradicional.

---

## 2. Estado actual del proyecto

- **Fase en curso:** **Ciclo 1 — Factibilidad técnica** (septiembre 2026).
- **Hito alcanzado (2026-09-09):** Dirección general, alcance núcleo y preguntas centrales PI1 y PI2 aprobadas por el tutor Ing. Ernesto Rico. Estrategia de audio confirmada con reproducción en streaming (*replay*) para la base experimental y llamada VoIP controlada para la demo del prototipo.
- **Gestión activa:** El backlog vivo se administra a través de **GitHub Issues** bajo los hitos del cronograma.

---

## 3. Mapa del repositorio (Estructura documental)

Toda la documentación vive dentro de [`docs/`](docs/) organizada por áreas sin copias paralelas:

```text
bitacora_tesis/
├── README.md                      # Esta guía de entrada y mapa para humanos
├── AGENTS.md                      # Router operativo e instrucciones para asistentes de IA
├── deep-research-report.md        # Investigación técnica inicial exhaustiva
├── docs/
│   ├── GLOSARIO.md                # Términos técnicos con sentido preciso (T_A, T_R, T_C, WER, etc.)
│   ├── propuesta/
│   │   ├── PLAN-DE-TRABAJO.md     # Fuente única de verdad: problema, objetivos, método y cronograma
│   │   └── REQUISITOS-ACADEMICOS.md # Pautas formales de UNSTA (portada, ~100 págs, defensa)
│   ├── gestion/
│   │   ├── METODO-DE-TRABAJO.md   # Flujo de sesiones, tipos de issue y definiciones de terminado
│   │   ├── MAPA-DECISIONES.md     # Registro vivo de decisiones abiertas y resueltas
│   │   ├── REGISTRO-RIESGOS.md    # Matriz de riesgos técnicos, de datos y mitigaciones
│   │   ├── RUNBOOK-RESOLUCION-ISSUES.md # Guía práctica y plantillas de prompts para issues
│   │   ├── bitacora/              # Historial semanal del equipo (AAAA-MM-semana-NN.md)
│   │   └── seguimientos/          # Consultas y minutas con el profesor (AAAA-MM-DD.md)
│   ├── investigacion/
│   │   ├── PREGUNTAS-DE-INVESTIGACION.md # Preguntas centrales PI1/PI2 y objetivos
│   │   ├── PROTOCOLO-REVISION.md  # Método de búsqueda bibliográfica reproducible
│   │   └── SINTESIS-ESTADO-DEL-ARTE.md  # Literatura analizada, matriz comparativa y vacíos
│   ├── datos-etica/
│   │   ├── PRIVACIDAD-DEL-SISTEMA.md    # Privacy by Design on-device, Ley 25.326 y permisos Android
│   │   ├── METODO-CREACION-CORPUS.md    # Fichas de rol, diseño de semillas, negativos difíciles y parada
│   │   ├── CATALOGO-ESCENARIOS.csv      # Inventario estructurado de semillas de fraude y control
│   │   └── MANUAL-ANOTACION.md          # Taxonomía de etiquetas y protocolo por turnos
│   ├── ingenieria/
│   │   ├── ALTERNATIVAS-CAPTURA-AUDIO.md # Comparación replay vs VoIP vs altavoz vs telefonía
│   │   ├── ARQUITECTURA.md              # Componentes conceptuales y pipeline de audio a alerta
│   │   └── adr/                         # Architecture Decision Records duraderos
│   ├── evaluacion/
│   │   └── METRICAS.md            # Fórmulas de tiempos, márgenes de anticipación y falsas alarmas
│   └── tesis/
│       └── ESQUELETO-INFORME.md   # Estructura capitular e índice orientativo de páginas
```

---

## 4. Dinámica de trabajo

1. **Backlog en GitHub Issues:** Las tareas se toman por autoasignación desde los issues del milestone activo.
2. **Desarrollo enfocado:** Cada integrante/asistente trabaja sobre la fuente de verdad primaria del issue (código en `src/`, experimentos en `experiments/` o textos en `docs/`).
3. **Barrido Documental al cerrar:** Al terminar una tarea, se verifica la fuente de verdad, se registra el artefacto en la bitácora semanal (`docs/gestion/bitacora/`) y se actualiza el mapa de decisiones o riesgos si correspondió.
4. **Trabajo asistido por IA:** El repositorio cuenta con skills en `.agents/skills/` y un flujo guiado en [RUNBOOK-RESOLUCION-ISSUES.md](docs/gestion/RUNBOOK-RESOLUCION-ISSUES.md). Los asistentes leen [AGENTS.md](AGENTS.md).

---

## 5. Reglas y Guardrails

- **Audio fuera de Git:** Ningún archivo de audio (`.wav`, `.mp3`) se sube al repositorio (reglado por `.gitignore`).
- **Datos ficticios:** Las grabaciones y guiones emplean identidades, cuentas y números ficticios; no se usan datos reales de víctimas.
- **Privacidad desde el diseño:** Todo procesamiento conversacional es estrictamente local en el dispositivo.
- **Alcance acotado:** La captura universal de llamadas PSTN estándar, la biometría vocal y la detección de deepfakes quedan formalmente fuera de alcance.
