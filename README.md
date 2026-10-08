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

La clave del problema es advertir al usuario en tiempo real antes de que realice una acción de riesgo (entregar un código OTP, transferir dinero o instalar una aplicación de acceso remoto).

- **Procesamiento local (privacidad por diseño):** El procesamiento se realiza de forma local sin enviar audio ni transcripciones a la nube. La base experimental se evalúa sobre streaming de audio (_replay_) y la integración _on-device_ en Android permanece como objetivo sujeto a factibilidad técnica.
- **Métricas temporales:** Se mide cuándo llega la alerta respecto del pedido y del cumplimiento simulado. Las definiciones están en [METRICAS.md](docs/evaluacion/METRICAS.md); estos márgenes no demuestran prevención de daño real.
- **Exclusiones de alcance:** La captura universal de llamadas PSTN estándar, la biometría vocal y la detección de deepfakes quedan formalmente fuera de alcance.

---

## 2. Estado actual del proyecto

- **Gestión activa:** El backlog vivo se administra en **GitHub Issues** bajo el [método de trabajo](docs/gestion/METODO-DE-TRABAJO.md). Para el historial semanal, ver la [bitácora](docs/gestion/bitacora/README.md); para decisiones abiertas, el [mapa](docs/gestion/MAPA-DECISIONES.md).
- **Ayuda memoria:** Entrada visual para el equipo en [`ayuda-memoria/`](ayuda-memoria/README.md), con vistas por rama (`laboratorio-main` y `main`), hitos, briefs de arranque para H2 y glosario.
- **Issues por hito:** [H1 — acuerdo mínimo](https://github.com/Corchets/bitacora_tesis/milestone/2) y [H2 — piloto y primeras pruebas](https://github.com/Corchets/bitacora_tesis/milestone/3). Elegir trabajo por el hito y sus dependencias.
- **Próximo recorrido:** [alcance, hitos y calendario de referencia](docs/propuesta/PLAN-DE-TRABAJO.md#8-recorrido-del-desarrollo). El laboratorio existente es material para evaluar y reutilizar según las tareas; no determina la arquitectura final.

---

## 3. Mapa del repositorio (Estructura documental)

Toda la documentación vive dentro de [`docs/`](docs/) organizada por áreas sin copias paralelas; la web de orientación interna vive en [`ayuda-memoria/`](ayuda-memoria/):

```text
bitacora_tesis/
├── README.md                      # Esta guía de entrada y mapa para humanos
├── AGENTS.md                      # Router operativo e instrucciones para asistentes de IA
├── ayuda-memoria/                 # Web visual de orientación, roadmap, glosario y briefs del equipo
│   ├── README.md                  # Uso local, fuentes y publicación en Vercel
│   ├── PRODUCT.md                 # Propósito, usuarios, principios y alcance del producto
│   ├── INTERFAZ.md                # Contrato de dirección y superficies (seed 35b1f183)
│   ├── DESIGN.md                  # Tokens reales, escalas, composición y accesibilidad
│   ├── briefs.json                # Orientaciones editoriales de arranque por rama e issue
│   ├── config.json                # Configuración de repositorio, ramas y glosario
│   ├── public/                    # Fuentes estáticas (HTML, CSS, JS, fuentes Manrope WOFF2)
│   └── scripts/                   # Generador Node (build, serve, review-brief)
├── docs/
│   ├── GLOSARIO.md                # Términos técnicos con sentido preciso (T_A, T_R, T_C, WER, etc.)
│   ├── propuesta/
│   │   ├── PLAN-DE-TRABAJO.md     # Fuente única de verdad: problema, objetivos, método y cronograma
│   │   └── REQUISITOS-ACADEMICOS.md # Pautas formales de UNSTA (portada, ~100 págs, defensa)
│   ├── gestion/
│   │   ├── METODO-DE-TRABAJO.md   # Flujo de sesiones, tipos de issue y definiciones de terminado
│   │   ├── MAPA-DECISIONES.md     # Registro vivo de decisiones abiertas y resueltas
│   │   ├── REGISTRO-RIESGOS.md    # Matriz de riesgos técnicos, de datos y mitigaciones
│   │   ├── bitacora/              # Historial semanal del equipo (AAAA-MM-semana-NN.md)
│   │   └── seguimientos/          # Consultas y minutas con el profesor (AAAA-MM-DD.md)
│   ├── investigacion/
│   │   ├── deep-research-report-00.md # Investigación técnica inicial exhaustiva
│   │   ├── PREGUNTAS-DE-INVESTIGACION.md # Preguntas centrales PI1/PI2 y objetivos
│   │   ├── PROTOCOLO-REVISION.md  # Método de búsqueda bibliográfica reproducible
│   │   ├── SINTESIS-ESTADO-DEL-ARTE.md  # Literatura analizada, matriz comparativa y vacíos
│   │   ├── PRIMERA-INVESTIGACION-MODELOS.md # Recorte inicial D09: candidatos, no elección final
│   │   ├── PREFACTIBILIDAD-TECNICA.md # Criterios de laboratorio y límite Android
│   │   └── VENTANA-DE-CONTEXTO-Y-ALERTA.md # Recorte D08: contexto y alerta
│   ├── corpus/
│   │   ├── PRIVACIDAD-DEL-SISTEMA.md    # Privacy by Design on-device, Ley 25.326 y permisos Android
│   │   ├── METODO-CREACION-CORPUS.md    # Fichas de rol, diseño de semillas, negativos difíciles y parada
│   │   ├── CATALOGO-ESCENARIOS.csv      # Inventario estructurado de semillas de fraude y control
│   │   └── MANUAL-ANOTACION.md          # Referencia humana y reglas de anotación
│   ├── ingenieria/
│   │   ├── ALTERNATIVAS-CAPTURA-AUDIO.md # Comparación replay vs VoIP vs altavoz vs telefonía
│   │   ├── ARQUITECTURA.md              # Componentes conceptuales y pipeline de audio a alerta
│   │   └── adr/                         # Architecture Decision Records duraderos
│   ├── evaluacion/
│   │   └── METRICAS.md            # Fórmulas de tiempos, márgenes de anticipación y falsas alarmas
│   └── tesis/
│       └── ESQUELETO-INFORME.md   # Estructura capitular e índice orientativo de páginas
```
