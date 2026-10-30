---
name: Demo de detección de vishing
description: Consola de aula para demostración de detección incremental de llamadas VoIP
colors:
  primary: "#1d4ed8"
  primary-dark: "#1e40af"
  primary-bg: "#eff6ff"
  neutral-bg: "#f8fafc"
  neutral-surface: "#ffffff"
  neutral-surface-alt: "#e2e8f0"
  neutral-border: "#cbd5e1"
  text-primary: "#0f172a"
  text-secondary: "#334155"
  text-muted: "#64748b"
  otra-bg: "#f1f5f9"
  otra-border: "#cbd5e1"
  protegida-bg: "#eff6ff"
  protegida-border: "#93c5fd"
  alert-primary: "#b91c1c"
  alert-text: "#7f1d1d"
  alert-bg: "#fef2f2"
  alert-light: "#fee2e2"
  alert-border: "#f87171"
  ok-primary: "#15803d"
  ok-bg: "#f0fdf4"
  warning-badge-bg: "#fef9c3"
  warning-badge-text: "#854d0e"
typography:
  display:
    fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
    fontSize: "28px"
    fontWeight: 700
    lineHeight: 1.2
  h1:
    fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
    fontSize: "24px"
    fontWeight: 700
    lineHeight: 1.2
  h2:
    fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
    fontSize: "20px"
    fontWeight: 700
    lineHeight: 1.3
  subheading:
    fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
    fontSize: "18px"
    fontWeight: 700
    lineHeight: 1.3
  h3:
    fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
    fontSize: "15px"
    fontWeight: 700
    lineHeight: 1.3
  body:
    fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.45
  body-sm:
    fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
    fontSize: "14px"
    fontWeight: 500
    lineHeight: 1.4
  body-large:
    fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
    fontSize: "17px"
    fontWeight: 400
    lineHeight: 1.45
  small:
    fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
    fontSize: "13px"
    fontWeight: 400
    lineHeight: 1.4
  caption:
    fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
    fontSize: "12px"
    fontWeight: 600
    lineHeight: 1.2
rounded:
  sm: "4px"
  md: "8px"
  lg: "12px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.neutral-surface}"
    rounded: "{rounded.sm}"
    padding: "8px 16px"
---

## Overview

Consola de demostración de aula (modo Operate) diseñada para proyectarse en pantalla grande ante tribunal, tutor y docentes. La interfaz permite entender de una sola mirada quién habla, qué está transcribiendo el ASR en tiempo real, qué decidió el detector en cada turno y la trayectoria de riesgo a lo largo del tiempo. Los controles de configuración quedan en una barra compacta plegable para que el contenido protagonista ocupe todo el campo visual.

## Colors

- **Fondo general (`neutral-bg`: `#f8fafc`)**: Blanco frío suave (slate-50) que reduce el encandilamiento del proyector en sala oscura sin perder contraste.
- **Superficies (`neutral-surface`: `#ffffff`)**: Blanco puro con borde sutil para tarjetas y paneles.
- **Tinta principal (`text-primary`: `#0f172a`)**: Azul noche casi negro (slate-900) con ratio de contraste superior a 12:1 sobre fondo claro.
- **Tinta secundaria y apagada (`text-secondary`: `#334155`, `text-muted`: `#64748b`)**: Gris azulado con contraste verificado mayor a 4.5:1.
- **Persona protegida (`protegida-bg`: `#eff6ff`, `protegida-border`: `#93c5fd`, `primary`: `#1d4ed8`)**: Tono azul cielo y azul cobalto, que identifica a la persona que recibe la llamada.
- **Otra persona (`otra-bg`: `#f1f5f9`, `otra-border`: `#cbd5e1`)**: Gris neutro slate, sobrio y sin emitir juicio inicial de culpabilidad.
- **Alerta de estafa (`alert-primary`: `#b91c1c`, `alert-bg`: `#fef2f2`, `alert-border`: `#f87171`)**: Rojo carmesí de alto contraste reservado exclusivamente al momento en que el detector dispara un aviso.
- **Estado seguro (`ok-primary`: `#15803d`, `ok-bg`: `#f0fdf4`)**: Verde esmeralda para llamadas legítimas o turnos sin riesgo.

**La regla de doble codificación.** Como los proyectores de aula suelen desteñir o lavar colores, ningún estado ni decisión crítica depende exclusivamente del color: siempre se acompaña de texto unívoco («Alerta: Sí», «Alerta: No», «Posible estafa»), etiquetas y formas.

## Typography

Tipografía nativa del sistema (`system-ui, -apple-system, sans-serif`) para garantizar ejecución autónoma e instantánea sin descargas de internet ni fuentes de terceros.

- **Jerarquía tipográfica pronunciada**:
  - Título proyector (`display`): 28px (1.75rem), peso 700.
  - Título de aplicación (`h1`): 24px (1.5rem), peso 700.
  - Título de tarjetas de rol (`h2`): 20px (1.25rem), peso 700.
  - Subtítulos técnicos y cabeceras de bloque (`h3`): 15px (0.9375rem), peso 700, mayúsculas sobrias con espaciado de 0.05em.
  - Texto de conversación / frases transcritas (`body-large`): 17px (1.0625rem), altura de línea 1.45, legible a distancia.
  - Hablando ahora (transcripción viva en tarjeta): 15px (0.9375rem), peso 500.
  - Metadatos secundarios (`small`): 13px (0.8125rem).
  - Píldoras e insignias (`caption`): 12px (0.75rem), peso 700.
  - Valores métricos y temporales: con `font-variant-numeric: tabular-nums` para evitar saltos de ancho al actualizar mediciones continuas.

## Layout

- **Estructura vertical con desplazamiento de página**: La conversación crece hacia abajo y la página entera se desplaza. Por debajo de 900px la columna técnica pasa abajo. Al borrador se lo lee en la tarjeta de cada persona; a la conversación entra solo la frase cerrada, con su renglón de evaluación ya reservado.
- **Barra superior compacta**: Encabezado con título, estado de conexión, conmutador de modos («Llamada en vivo» / «Probar el ASR»), botones de ciclo de vida (Iniciar, Terminar, Nueva) y panel plegable de configuración de fuentes de audio.
- **Área principal de presentación (Grid de 2 tercios y 1 tercio lateral en consola)**:
  - **Fila superior de tarjetas de voz**: Dos tarjetas simétricas («Otra persona» a la izquierda, «Persona protegida» a la derecha) con medidor RMS visible y caja de transcripción viva.
  - **Columna de conversación (izquierda / centro, 65-70% ancho)**: Diálogo en dos bandas alineadas con las tarjetas superiores, con las evaluaciones del detector incrustadas bajo la frase que las disparó.
  - **Columna técnica (derecha, 30-35% ancho)**: Panel lateral que contiene el detector fijo en uso, la línea gráfica de riesgo en el tiempo (SVG) y la tabla de métricas y latencias.
- **Vista de presentación (Grid de dos teléfonos iPhone y diálogo central)**:
  - Siluetas laterales de iPhone (276px de ancho, 310px en proyección ≥ 1700px, 232px en pantallas estrechas) con avatares ilustrados estilo emoji, medidores RMS por canal y ondas reactivas.
  - Columna central (`minmax(0, 1fr)`) con scroll interno, seguimiento automático en vivo, botón «Volver al vivo» al pausar la revisión y cajas de evaluación con detalles desplegables.
  - Tarjeta de aviso de posible estafa en el iPhone protegido con motivo, evidencia resaltada en el diálogo y control de sonido.
  - Ajuste responsivo vertical (`@media (max-height: 820px)`): marco, avatar y separaciones compactadas para garantizar que los teléfonos permanezcan visibles dentro del viewport en notebooks (1366 × 768) sin scroll de ventana.
  - Accesibilidad de foco: contorno visible de 2px en azul primario (`--primary`, `#1d4ed8`) con offset de 2px para todos los controles interactivos.

## Elevation & Depth

- **Planitud instrumental con bordes nítidos**: Sin sombras pesadas ni halos difusos. Bordes limpios de 1px en `#cbd5e1` o variantes de color por rol.
- Elevación leve en tarjetas mediante borde contrastado y fondo blanco, maximizando la legibilidad en entornos proyectados con luz ambiente.

## Shapes

- Esquinas suavemente redondeadas con radio de 8px (`md`) para contenedores principales, 12px (`lg`) para tarjetas grandes y 4px (`sm`) para botones y controles.
- Insignias de métricas y píldoras de estado con radio completo (pills) para distinguirlas claramente de los bloques de contenido.

## Motion

- Solo se animan `opacity` y `transform`, con curva de salida (`cubic-bezier(0.22, 1, 0.36, 1)`), sin rebote ni parpadeo.
- **Mensaje nuevo**: fundido y desplazamiento de 8px en 200ms; la animación vive en la clase base de la burbuja, así pasar de provisorio a final (mismo nodo) no la reinicia. El provisorio se distingue por borde punteado y tinta secundaria, sin cursiva, para que el renglón no salte al cerrarse. La conversación baja con scroll suave.
- **Alerta**: la franja ocupa su lugar desde el principio (invisible) y entra con fundido y escala de 0,98 a 1 en 220ms; el tinte de fondo es una capa propia que sube de opacidad en 300ms. El tono se dispara en la misma tarea que muestra la franja.
- Con `prefers-reduced-motion` todo es instantáneo y el scroll no es suave.

## Components

- **Franja de aviso de posible estafa**: Franja horizontal compacta no modal sobre las tarjetas de voz con insignia de alto contraste («Posible estafa»), motivo, cita resaltada en la conversación, control de sonido WebAudio persistente y botón de cierre. En reposo, su casillero muestra un borde punteado con «Sin aviso. Si el detector encuentra una posible estafa, aparece en esta franja.», que enseña dónde mirar sin anticipar que la llamada sea fraudulenta.
- **Tarjetas de rol («Otra persona» y «Persona protegida»)**: Identifican al hablante, presentan el medidor de nivel RMS en vivo y muestran la transcripción parcial en curso.
- **Burbuja de conversación**: Alineada a izquierda para «Otra persona» y derecha para «Persona protegida». Incorpora autor, tiempo relativo, texto final y la evaluación del detector asociada cuando corresponde.
- **Píldora de evaluación del detector**: Caja adosada a la frase con riesgo porcentual, decisión sí/no, latencia de inferencia y advertencia de frases salteadas si el detector estuvo ocupado. Sin riesgo, va en voz baja: renglón bajo un filete, sin caja, con «Alerta: No» en verde contorneado. Riesgo alto (amarillo), fallo y aviso (rojo) conservan caja y relleno para sobresalir.
- **Gráfico de riesgo temporal (SVG)**: Visualización continua del riesgo a lo largo de los segundos de la llamada, con umbral de decisión y marca vertical explícita en el instante exacto del aviso de estafa.
- **Panel de control plegable**: Acordeón que oculta la selección de micrófonos y dispositivos cuando no se está configurando la llamada.

## Do's and Don'ts

- **DO**: Mantener siempre visibles a ambas personas y sus medidores de audio en la parte superior.
- **DO**: Adjuntar la evaluación exactamente a la frase que cerró el detector.
- **DO**: Indicar explícitamente cuando una frase fue salteada por demora de procesamiento.
- **DO**: Utilizar `tabular-nums` en todos los contadores de tiempo y decibeles/RMS.
- **DON'T**: Usar transiciones CSS sobre propiedades que fuerzan relayout como `width` o `height`.
- **DON'T**: Iniciar llamadas presumiendo que «Otra persona» es un atacante; la llamada puede ser legítima.
- **DON'T**: Depender de conexiones externas o librerías CDN; todo debe operar en local.
- **DON'T**: Usar ventanas modales invasivas para los avisos.
