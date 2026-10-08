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

La vista de Roadmap (`roadmapView`) implementa un grafo de dependencias no lineal con [Cytoscape.js](https://js.cytoscape.org/), librería vanilla de grafos (zoom, paneo, arrastre y selección por canvas) que no exige framework: su bundle ESM minificado se fija en `package.json`/`package-lock.json` y `scripts/build.mjs` lo copia a `dist/` junto con su licencia, sin CDN. Las aristas provienen exclusivamente de las dependencias nativas de GitHub (`data.roadmap.graph`, construido desde la API `blocked_by`); `roadmap.json` aporta solo la orientación editorial (frentes, próximos pasos, notas de arista, laboratorio) y los issues cerrados necesarios entran al grafo con su `state_reason` para distinguir `completed` de `not_planned`.

1. **Carriles por frente (`node:parent.front-*`):**
   - Cada frente editorial es un recuadro contenedor con fondo tenue (`FRONT_BG`) y filete del color del frente (`FRONT_COLORS`); las columnas se ordenan de izquierda a derecha según el flujo de dependencias (Concluido → Corpus → Detección → Metodología → Cierre) y cada issue ocupa una posición fija ordenada por profundidad — no hay simulación en movimiento.
   - El laboratorio es un carril separado, debajo y con filete punteado terracota: nunca cuenta como bloqueo ni como trabajo completado. Su única arista (`#51 → laboratorio`) es `conditional` (punteada, con la nota editorial de retomo).
2. **Nodos de entrega:**
   - Círculos de 34px con etiqueta `#NN` y título abreviado (el título completo va al panel): disponibles (`is-free`, filete ink sobre blanco), en espera (`is-blocked`, fondo coral y filete terracota), completados (`is-done`, verde relleno), retirados (`is-notplanned`, punteado terracota), sin verificar (`is-unknown`, punteado gris) y pausados (`is-paused`, punteado terracota). Los próximos pasos sugeridos llevan halo lima (`is-next`, `underlay`).
   - Flechas: bloqueo vigente en terracota, dependencia ya resuelta en verde y condición de retomo punteada con su nota editorial (`edgeNotes` de `roadmap.json`).
3. **Barra de herramientas (`.rm-toolbar`):**
   - Alternancia Mapa/Lista (`.rm-modes`), filtro por frente, «Solo disponibles», «Foco en próximos pasos» (atenua lo demás sin reencuadrar), zoom −/+, Encuadrar, Restablecer y una leyenda desplegable (`.rm-legend`) con frentes, estados y tipos de flecha.
   - Filtros y foco solo ocultan o atenúan elementos (`f-hidden`, `focus-dim`): nunca regeneran el lienzo ni reinician el encuadre. La selección persiste en la URL (`?vista=roadmap&nodo=i50`, `modo=lista`) para compartir una vista.
4. **Lista accesible (`.roadmap-list`):**
   - Modo Lista con la misma información en botones DOM (`.rl-node`): número, título, hito y píldora de estado (`Disponible`, `Espera #NN`, `Completado`, `Pausado`). Es la vista por defecto en pantallas ≤ 700px y la alternativa completa para teclado y lectores de pantalla.
5. **Panel de detalle (`.rm-panel`):**
   - En modo Mapa el lienzo ocupa todo el ancho disponible y el panel aparece como capa superpuesta a la derecha (`.rm-panel.has-sel`, `position: absolute`) recién al seleccionar: no roba ancho inicial ni reinicia el zoom. En modo Lista queda debajo de la lista, en flujo normal. Muestra hito, frente, responsable, enlaces a GitHub y a la vista de trabajo, estado del brief, qué se logra, siguiente acción, bloqueos vigentes como lista navegable con notas de arista (`.rm-edge-note`), dependencias sin verificar, entregas que desbloquea y evidencia del frente.
   - Al seleccionar un nodo, el grafo atenúa lo no relacionado (`.dimmed`) y colorea entrantes (terracota, `.dep-in`) y salientes (verde, `.dep-out`); Escape o tocar el fondo limpia la selección.

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
   - El roadmap abre en modo Lista (`.roadmap-list`, alternable a Mapa) y el panel de detalle se apila debajo de la lista.

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
