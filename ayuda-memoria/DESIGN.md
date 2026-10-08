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

## 2.4 Componentes del Mapa Espacial Ilustrativo (Roadmap)

La vista de Roadmap (`roadmapView`) implementa un mapa espacial no lineal en SVG nativo donde la carga inicial encaja confortablemente en una pantalla de escritorio sin exponer tarjetas largas ni detalles hasta que el usuario interactúa:

1. **Cabecera de orientación (`.spatial-header`):**
   - Presenta el título del mapa y una guía concisa de 3 opciones accionables: *Elegir Crear primer par (#39), Alinear detector (#50) o Investigar antecedentes (#25)*.
   - Brinda un botón accesible de ayuda rápida (`.spatial-help-toggle`) y atajo de teclado (`Esc`).
2. **Lienzo espacial nativo (`.spatial-canvas-wrap` y `.spatial-svg`):**
   - Renderizado vectorial SVG con viewBox responsivo (`1000x560` en escritorio, `420x620` en móvil) y marcadores de flecha semánticos (`#arrow-active`, `#arrow-future`, `#arrow-paused`).
   - Ilustraciones de zonas espaciales:
     - **Isla suspendida de laboratorio** (`.svg-zone-paused`): Desarrollos de pipeline/cascada pausados (#41, #42, #44, #46–#49) en ramas `nacho1706/feature-training-data` (`bb542e1`) y `origin/laboratorio-main` (`4888277`), con condición de reanudación en #51 (D09).
     - **Zona de ejecución activa** (`.svg-zone-active`): Hito 1 consolidado (PR #56) y punto neurálgico "Estamos acá".
     - **Opciones de avance inmediato**: Tres ramas vectoriales directas hacia *Crear primer par* (#39), *Alinear detector* (#50) e *Investigar antecedentes* (#25).
     - **Horizonte futuro** (`.svg-zone-future`): Hitos posteriores desacoplados (#55, #45, #33, #51, #52, #53).
3. **Botones accesibles superpuestos (`.spatial-node-btn`):**
   - Elementos `<button>` nativos HTML posicionados por porcentaje sobre el SVG con `min-height: 44px` y padding ergonómico para interacción táctil y por teclado.
   - Contienen badge de estado (`.spatial-node-badge`), etiqueta concisa (`.spatial-node-title`) y metadato descriptivo (`.spatial-node-meta`).
   - Atributos accesibles completos: `aria-expanded`, `aria-controls="roadmap-drawer"`, `:focus-visible` con halo acentuado (`var(--accent)`).
4. **Drawer enfocado único (`.roadmap-drawer`):**
   - Panel lateral derecho de ancho fijo (`380px` en escritorio, overlay completo en móvil) que se despliega al seleccionar cualquier nodo interactivo.
   - En escritorio se ubica a la derecha sin solapar ninguno de los nodos espaciales (los nodos residen en el 65% izquierdo).
   - Al seleccionar otro nodo, el drawer **reemplaza** inmediatamente el contenido sin acumulación.
   - Incorpora:
     - **Acción siguiente concreta (`.drawer-action-callout`):** Qué hacer ahora de forma unívoca.
     - **Qué leer primero (`.drawer-reading-box`):** Fuente primaria clave enlazada.
     - **Issues del frente (`.drawer-issues-box`):** Botones accesibles de issues (`.drawer-issue-btn`) con estado y título.
5. **Drill-down contextual de issues (`renderDrawerIssueBrief`):**
   - Al pulsar un botón de issue en el drawer, la vista del issue se despliega dentro del mismo panel sin abandonar la vista del mapa ni recargar la página.
   - Incluye botón *← Volver a opciones del nodo* (`.drawer-back-btn`) y botón de cerrar (`×`).
   - Cierre con tecla Escape o clic fuera del drawer restaura el foco accesible al botón del nodo previamente seleccionado.

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
  - Verificada en 16 combinaciones (escritorio y móvil, ambas ramas, 4 vistas) con cero (0) violaciones de accesibilidad.
