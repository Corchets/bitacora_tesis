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

- **Estado al 2026-11-21:** la evaluación final corrió el 2026-11-19, una sola vez, sobre el test reservado y los conjuntos externos ([análisis](experiments/slm-directo/corridas/2026-11-12_evaluacion-final/analisis.md), [qué concluir](docs/evaluacion/CONCLUSIONES-EVALUACION-FINAL.md)). El proyecto está en el cierre y la redacción del informe ([capítulos](docs/tesis/README.md)). Para redactar, empezar por el [mapa del proceso](docs/tesis/MAPA-DEL-PROCESO.md).
- **Configuración final:** ASR en el [ADR 0001](docs/ingenieria/adr/0001-parakeet-filtro-y-gemma4-e2b-con-tito-viejo.md); detector en los [ADR 0002](docs/ingenieria/adr/0002-detector-gemma4-e2b-solo-con-prompt-c-premisa.md), [0006](docs/ingenieria/adr/0006-salida-cortada-tras-el-campo-que-decide-y-motivo-al-avisar.md), [0007](docs/ingenieria/adr/0007-consulta-al-cerrar-cada-turno-de-otra.md), [0008](docs/ingenieria/adr/0008-prompt-del-detector-c-consejos.md) y [0009](docs/ingenieria/adr/0009-en-el-telefono-el-modelo-genera-solo-el-numero.md). Lo que se aprendió en el camino está en los [hallazgos](docs/hallazgos/README.md).
- **Gestión activa:** el backlog vivo se administra en **GitHub Issues** bajo el [método de trabajo](docs/gestion/METODO-DE-TRABAJO.md). Para el historial semanal, ver la [bitácora](docs/gestion/bitacora/README.md); para decisiones abiertas, el [mapa](docs/gestion/MAPA-DECISIONES.md).
- **Lo que salió del repo:** la poda del 2026-11-21 (sitio ayuda-memoria, `arquitectura-web/`, corridas intermedias y documentos de trabajo) queda en el tag [`archivo/pre-informe`](https://github.com/Corchets/bitacora_tesis/tree/archivo/pre-informe).

---

## 3. Mapa del repositorio (Estructura documental)

Toda la documentación vive dentro de [`docs/`](docs/), organizada por áreas sin copias paralelas; el código y las corridas, en [`experiments/`](experiments/):

```text
bitacora_tesis/
├── README.md                      # Esta guía de entrada y mapa para humanos
├── AGENTS.md                      # Router operativo e instrucciones para asistentes de IA
├── .github/                       # Plantillas de issues y de PR
├── docs/
│   ├── GLOSARIO.md                # Términos técnicos con sentido preciso (T_A, T_R, T_C, WER, etc.)
│   ├── hallazgos/                 # Lo que aprendimos: un archivo por hallazgo (H01…H13), con evidencia, estado y qué cambia
│   ├── propuesta/
│   │   ├── PLAN-DE-TRABAJO.md     # Plan v1: problema, objetivos, alcance y cronograma
│   │   └── REQUISITOS-ACADEMICOS.md # Pautas formales de UNSTA (portada, ~100 págs, defensa)
│   ├── gestion/
│   │   ├── METODO-DE-TRABAJO.md   # Flujo de sesiones, tipos de issue y definiciones de terminado
│   │   ├── MAPA-DECISIONES.md     # Registro vivo de decisiones abiertas y resueltas
│   │   ├── REGISTRO-RIESGOS.md    # Matriz de riesgos técnicos, de datos y mitigaciones
│   │   ├── bitacora/              # Historial semanal del equipo (AAAA-MM-semana-NN.md)
│   │   └── seguimientos/          # Consultas y minutas con el profesor (AAAA-MM-DD.md)
│   ├── investigacion/
│   │   ├── PREGUNTAS-DE-INVESTIGACION.md # Preguntas PI1/PI2, E1 (fuera) y E2
│   │   ├── PROTOCOLO-REVISION.md  # Método de búsqueda bibliográfica reproducible
│   │   ├── SINTESIS-ESTADO-DEL-ARTE.md  # Literatura analizada, matriz comparativa y vacíos
│   │   ├── lecturas/              # Fichas de lectura de fuentes primarias
│   │   ├── FUENTES-LEGITIMAS-REALES.md # Relevamiento y armado de las legítimas reales (CallCenterEN)
│   │   ├── PREFACTIBILIDAD-TECNICA.md # Umbrales de latencia y memoria (criterio interno)
│   │   ├── PRIMERA-INVESTIGACION-MODELOS.md # Antecedente: recorte inicial de D09
│   │   ├── VENTANA-DE-CONTEXTO-Y-ALERTA.md # Antecedente: propuesta de ventana y alerta para D08
│   │   ├── ESTRATEGIA-MODELOS-NLP-Y-COMPRESION.md # Antecedente: marco teórico de #27
│   │   ├── CONTRASTE-NLP-TEORIA-Y-LABORATORIO.md  # Antecedente: marco de #27 frente al spike #29
│   │   └── GUIA-CORRIDA-LABORATORIO.md # Antecedente: corrida del spike #29
│   ├── corpus/
│   │   ├── PRIVACIDAD-DEL-SISTEMA.md    # Privacidad por diseño on-device, Ley 25.326 y permisos Android
│   │   ├── METODO-CREACION-CORPUS.md    # Método previsto en octubre (fichas de rol, semillas, piloto)
│   │   ├── CATALOGO-ESCENARIOS.csv      # Inventario estructurado de semillas de fraude y control
│   │   ├── MANUAL-ANOTACION.md          # Referencia humana y reglas de anotación
│   │   ├── RELEVAMIENTO-CORPUS-EXTERNO.md # Fuentes externas y armado del set coreano (#144)
│   │   ├── FILTRO-KORCCVI.csv           # Decisión por llamada del filtro de KorCCVi (#144)
│   │   ├── MANIFIESTO-*.json            # Huellas de los conjuntos externos congelados
│   │   ├── PROMPTS-*.md                 # Prompts de traducción y armado de los externos
│   │   ├── FICHAS-144-*.md, ISSUE-144-INGLES-*  # Fichas y lecturas de Luciano de los externos
│   │   ├── REVISION-CIEGA-145.md, REVISIONES-HUMANAS-LUCIANO.md # Revisión humana de #145 y sus capturas
│   │   └── KIT-PRIMER-PAR.md            # Kit de grabación del primer par (#39)
│   ├── ingenieria/
│   │   ├── ALTERNATIVAS-CAPTURA-AUDIO.md # Comparación replay vs VoIP vs altavoz vs telefonía
│   │   ├── ARQUITECTURA.md              # Arquitectura conceptual de septiembre a noviembre (con notas)
│   │   └── adr/                         # Decisiones de arquitectura duraderas (0001…0009)
│   ├── evaluacion/
│   │   ├── METRICAS.md            # Fórmulas de tiempos, márgenes de anticipación y falsas alarmas
│   │   ├── PROTOCOLO-EXPERIMENTAL.md # Propuesta de protocolo del 2026-10-17 (#33), con nota de D08
│   │   ├── COMPARACION-CANDIDATOS-DESARROLLO.md # Comparación de candidatos que sostuvo el ADR 0001
│   │   ├── PROPUESTA-CONFIGURACION-DETECTOR.md  # Propuesta del 2026-11-05, superada por el ADR 0002
│   │   └── CONCLUSIONES-EVALUACION-FINAL.md     # Qué concluir de la evaluación final
│   └── tesis/
│       ├── README.md              # Índice y estado de los capítulos
│       ├── MAPA-DEL-PROCESO.md    # Guía de las etapas del proceso para quien redacta
│       ├── ESQUELETO-INFORME.md   # Estructura capitular e índice orientativo de páginas
│       └── CAP-00…CAP-11          # Capítulos del informe
├── experiments/
│   ├── asr-local/                 # Procedimiento repetible de ASR local streaming/segmentado (#19)
│   ├── laboratorio/               # Antecedente: laboratorio de septiembre (spike #29)
│   ├── metricas/                  # Módulo de cálculo y reporte de métricas según METRICAS.md (#52)
│   ├── replay/                    # Simulación de streaming, cola secuencial y política de aviso único (#28)
│   ├── voip/                      # Llamada en vivo: ASR por canal, detector y panel de la demo
│   └── slm-directo/               # Detector: SLM local sobre texto incremental (#50)
│       ├── casos/                 # Corpus de desarrollo, test reservado, externos y catálogo de conversaciones
│       ├── prompts/               # Textos de los prompts y sus diferencias
│       ├── corridas/              # Una carpeta por corrida, con manifiesto y resultados
│       ├── analisis/              # Análisis que cruzan corridas
│       ├── colab/                 # Notebooks para correr en Colab T4
│       └── tests/                 # Pruebas del código de slm-directo
```

## 4. Demo local de llamadas (Luciano)

Desde el 2026-11-10 la demo se levanta desde una copia de la rama principal (`main` desde el 2026-11-21; antes, `laboratorio-main`), con la configuración congelada de
[#143](https://github.com/Corchets/bitacora_tesis/issues/143) por defecto. Comando, de dónde sale Ollama y opciones:
[`experiments/voip/README.md` §3](experiments/voip/README.md#demo-con-la-configuración-congelada-de-143). Hasta esa
fecha corría desde la copia de `laboratorio-luciano` de Luciano, con Tito y el prompt `v4`; esa rama se retira. Las
variables y el orden de la prueba con voz real están en [`PRUEBA-VOZ-REAL-MEET.md`](experiments/voip/PRUEBA-VOZ-REAL-MEET.md).

**Qué se guarda.** Cada llamada deja en `experiments/voip/llamadas/` de la copia donde corre el servidor
las voces (`estereo.wav`) y sus registros (`actualizaciones.jsonl`, `detector.jsonl`, `manifiesto.json`).
Esa carpeta está fuera de Git: **borrar la copia borra las voces**, y así se perdió el
[audio de la corrida por Meet](experiments/voip/corridas/2026-11-02-voz-real-meet.md#audio-original-perdido).
`git status` no la muestra. Antes de borrar una copia, mirá lo ignorado con `git status --short --ignored`
y resguardá las llamadas. Además, al arrancar, el servidor borra las pruebas que no se guardaron.

Antes de abrir localhost, comprobá qué proceso ocupa el puerto y desde qué carpeta corre:

```bash
lsof -nP -iTCP:8765 -sTCP:LISTEN
lsof -a -p <PID> -d cwd
git -C <copia> status -sb   # tiene que estar en main
```

Si el servidor corresponde a otra copia, terminalo con `kill -TERM <PID>` y esperá
que libere el puerto: el cierre normal conserva la llamada en curso. Levantá la copia de `main`:

```bash
ollama serve   # en otra terminal, o --ollama-url a otra máquina; solo reglas y Probar el ASR andan sin Ollama
cd <copia>/experiments/voip
<copia>/.venv/bin/python servidor.py --host 127.0.0.1
```

Sin Tito no hacen falta `torch` ni `transformers`: solo los pide `--detector tito-slm --prompt v4`. Los modelos y
audios de `experiments/asr-local/` están fuera de Git: en una copia nueva hay que enlazarlos o bajarlos. En otra
terminal, comprobá el panel antes de abrirlo:

```bash
curl --fail --silent http://localhost:8765/ | cmp - <copia>/experiments/voip/panel.html
open http://localhost:8765/
```

`cmp` termina sin salida y con código 0 si coincide. El puerto **8765** queda para
esta demo; el tablero de resultados se sirve aparte en **8766**. El arranque no
inicia una grabación. Servir la versión correcta no valida la captura ni cierra D05, D06, D08 o D09.
