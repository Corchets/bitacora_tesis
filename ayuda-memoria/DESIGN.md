# Sistema de diseño: Ayuda memoria

<!-- Documentación de tokens reales, composición y reglas visuales del sitio -->

## 1. Dirección y metáfora

- **Modo:** Operate / Read. Agenda de trabajo universitaria para retomar tareas del Proyecto Final sin perder el contexto de los hitos.
- **Forma y origen:** Programa de jornadas universitarias, derivado del seed `35b1f183` (candidato 7 del catálogo). Prioriza la claridad de etapas y la lectura de fuentes primarias sobre metáforas de tablero o vault.
- **Voz:** Precisa, sobria, amable y académica. Castellano rioplatense (Español de Argentina).
- **Estado de decisión:** Composición funcional y flujos acordados con el equipo en el marco del issue #57. La estética (paleta botánica/editorial y tipografía Manrope) constituye la realización concreta de la primera versión; no requiere entrevistas adicionales ni bloquea la entrega.

---

## 2. Tokens de diseño reales

Los tokens están implementados en `ayuda-memoria/public/styles.css` sobre `:root`:

### 2.1 Paleta cromática

| Token CSS | Valor HEX | Uso y semántica |
| --- | --- | --- |
| `--paper` | `#f6f7f0` | Fondo general de la página. Papel cálido no reflectante. |
| `--white` | `#fffef9` | Superficies de lectura, tarjetas elevadas y paneles laterales. |
| `--ink` | `#203e37` | Tinta principal (verde bosque profundo). Títulos, textos primarios, botones seleccionados y banner de hito actual. Contraste alto sobre papel y blanco. |
| `--muted` | `#5a6a62` | Tinta secundaria. Descripciones, metadatos, fechas orientativas y placeholders. |
| `--line` | `#d9dfd2` | Reglas tipográficas, bordes de separación y grilla estructural de 1px. |
| `--green` | `#e8eddb` | Superficie de acento suave. Fila de issue seleccionada, botón de navegación activo, fondo del primer paso (`.start-section`) y código en línea (`code`). |
| `--lime` | `#d7e9af` | Acento luminoso. Marca numérica del hito actual, selección de texto (`::selection`) y título del banner de etapa. |
| `--accent` | `#ad452b` | Bermellón / terracota sobrio de advertencia. Issues bloqueados, briefs pendientes/stale, enlaces faltantes y anillo de foco accesible (`:focus-visible`). |
| `--coral` | `#f9ece1` | Fondo de aviso de bloqueos abiertos (`.blocker-note`). |

#### Colores derivados y de estado
- **Estado listo / revisado:** `#365b35` (texto e indicador), `#427345` (punto de estado activo).
- **Texto en advertencia de bloqueo:** `#76331f` (sobre `--coral`).
- **Detalle en banner de etapa:** fondo `#203e37`, divisor `#4e665b`, texto secundario `#d6e0d3`.
- **Hover en fila de issue:** `#edf0e4`.
- **Barra de desplazamiento:** scrollbar `#9fae9e` sobre `var(--paper)`.

### 2.2 Tipografía

- **Familia única:** `Manrope, sans-serif`, servida localmente en formato WOFF2 (`/fonts/manrope.woff2`, licencia OFL) sin dependencias ni llamadas a redes externas.
- **Escala modular y ritmos:**
  - **Display / Título de página (H1):** `clamp(28px, 2.7vw, 40px)`, interlineado `1.2`, tracking `-0.035em`, peso `800`, `text-wrap: balance`.
  - **Títulos de sección (H2):** `20px` a `23px`, interlineado `1.45`, tracking `-0.025em`, peso `700`–`800`.
  - **Subtítulos y grupos (H3):** `12px` a `14px`, interlineado `1.5`, peso `800`.
  - **Cuerpo de texto / Prosa:** `14px`, interlineado `1.7` a `1.85`, ancho máximo recomendado `70ch` a `75ch` para legibilidad continua.
  - **Metadatos, etiquetas y controles:** `12px`, peso `600` a `800`.
  - **Números tabulares:** `font-variant-numeric: tabular-nums` aplicado en números de issue (`#57`), fechas de cronograma, referencias de hitos y contadores abiertos/cerrados.

### 2.3 Espaciado y geometría

- **Radios de curvatura (`--radius`):**
  - Contenedores grandes (tarjeta de etapa, panel de detalle, calendario): `var(--radius)` = `12px`.
  - Botones de navegación, inputs de búsqueda y selectores: `8px`.
  - Filas de issues y bloques de código: `4px`.
  - Selector de ramas (píldora): `30px` contenedor / `24px` botón interno.
  - Indicadores circulares (etapas y códigos de hito): `50%`.
- **Superficies y sombras:**
  - Sin sombras proyectadas ficticias ni elevaciones flotantes.
  - La jerarquía se establece mediante el contraste de planos (`--paper` frente a `--white` y `--ink`) delimitados por filetes de `1px solid var(--line)`.

---

## 2.4 Componentes del Mapa de Entregas (Roadmap)

La vista de Roadmap (`roadmapView`) organiza componentes según el recorrido
Audio → Transcripción → Contexto y detección → Alerta → Registro y evaluación.
Corpus, protocolo e informe forman una banda de soporte. Son botones HTML con
el mismo vocabulario y enlaces al visor de arquitectura, que conserva su diseño.

1. **Bloques (`.system-node`):** nombre, función, pendiente visible y cantidad de
   issues abiertos. El avance combina artefactos presentes en el árbol de la
   rama seleccionada con el estado real de los issues. Los textos editoriales y
   la correspondencia componente→issues viven en `roadmap.json > systemMap`.
2. **Estados:** «Avance parcial» en ocre identifica documentos o código
   experimental; «Pendiente» tiene borde terracota discontinuo; «Entregas
   cerradas» en verde exige todos los issues asociados cerrados como
   `completed`. No equivale a certificación del componente. `not_planned` nunca
   cuenta como terminado. «Sin issue específico» hace visibles huecos de
   seguimiento, como VoIP, sin crear tareas locales.
3. **Controles:** Mapa del sistema/Lista, filtros de issues abiertos, sin
   bloqueos, trabajo pendiente y componentes sin issue. Las flechas entre
   columnas indican recorrido conceptual; las dependencias reales se consultan
   en el detalle del issue. «Sin bloqueos» excluye condiciones documentales
   registradas, además de dependencias abiertas.
4. **Detalle (`.system-detail`):** debajo del recorrido; muestra qué existe y
   qué falta, artefactos enlazados al commit de la rama, issues abiertos,
   cerrados, decisiones y avances editoriales con su fuente. Al abrir un issue
   aparecen su contrato y bloqueos nativos; se puede volver al componente.
   La selección recibe foco y Escape retorna al bloque de origen.
5. **Adaptación y enlaces:** cinco columnas en escritorio, con desplazamiento
   horizontal en anchos intermedios y una columna en celular. Lista usa dos
   columnas y una en celular. `componente`, `nodo`, `modo` y `filtro` en la URL
   permiten compartir una selección. Los filtros conservan el detalle abierto.
6. **Contexto adicional:** próximos pasos, avances recientes y laboratorio
   encoder/cascada en pausa, más calendario y decisiones, quedan en secciones
   desplegables. El backlog continúa en GitHub.

---

## 3. Disposición y adaptabilidad (Responsive)

El layout se organiza en una grilla de dos columnas principales: barra lateral de orientación fija (`.sidebar`) y espacio de trabajo (`.workspace`).

### 3.1 Puntos de quiebre (Breakpoints)

1. **Pantalla ancha (>= 1700px):**
   - Barra lateral: `260px`.
   - Área de trabajo: grilla `minmax(0, 1.3fr) minmax(0, 1fr)` con separación de `46px`.
   - Padding generoso en filas y contenedores.
2. **Escritorio estándar (1201px – 1699px):**
   - Barra lateral: `226px`.
   - Área de trabajo: grilla `minmax(0, 1.1fr) minmax(0, 1fr)` con separación de `32px`.
3. **Escritorio compacto (1001px – 1200px):**
   - Barra lateral: `195px`.
   - Área de trabajo: grilla de dos columnas con separación reducida a `20px`.
4. **Tableta / Portátil angosto (701px – 1000px):**
   - Layout de issues y roadmap colapsa a **una sola columna vertical** (`1fr`).
   - El panel de detalle (`#brief-panel`) se sitúa inmediatamente a continuación de la lista y recibe scroll / foco automático al seleccionar una fila.
5. **Móvil (<= 700px):**
   - La estructura (`.shell`) pasa a `display: block`.
   - La barra lateral se convierte en cabecera estática superior con navegación en grilla de 2 columnas de botones táctiles (mínimo `44px` de altura).
   - Ocultamiento de metadatos no críticos en el riel de fases (conserva códigos táctiles `H0`–`H5`).
   - Filas de issues optimizadas en espaciado horizontal.
   - El roadmap muestra los componentes apilados, con el detalle debajo del recorrido. El modo Lista sigue disponible.

---

## 4. Accesibilidad y estados

- **Navegación por teclado:**
  - Enlace de salto inicial accesible (`.skip`) para omitir la barra lateral e ir directamente a `#contenido`.
  - Anillo de foco unificado y nítido para todos los controles interactivos: `:focus-visible { outline: 3px solid var(--accent); outline-offset: 4px; }`.
  - Inputs con indicador de inserción visible (`caret-color: var(--accent)`).
- **Semántica y lectores de pantalla:**
  - Uso riguroso de etiquetas semánticas: `<aside>`, `<nav>`, `<header>`, `<main>`, `<footer>`, `<section>`, `<article>`, `<dl>`, `<dt>`, `<dd>`, `<ol>`.
  - Estados accesibles dinámicos: `aria-current="page"`, `aria-pressed`, `aria-busy`, `aria-live="polite"`, `aria-labelledby`, `role="status"`.
  - Íconos puramente decorativos marcados con `aria-hidden="true"`.
  - Enlaces externos con texto claro e ícono SVG complementario.
- **Movimiento reducido:**
  - Regla `@media(prefers-reduced-motion: reduce)` que neutraliza todas las transiciones y animaciones (`animation: none !important; transition: none !important; scroll-behavior: auto !important`).
  - Scroll automático instantáneo (`instant`) en lugar de animado (`smooth`) cuando dicha preferencia está activa.
- **Auditoría axe:**
  - La versión previa registró cero violaciones en 16 combinaciones. Ese resultado no verifica el roadmap modificado el 2026-10-21; en esta sesión no hubo navegador disponible para repetir la revisión visual o axe.
