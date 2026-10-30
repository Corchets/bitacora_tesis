---
name: Demo de detección de vishing
description: Consola de aula para demostración de detección incremental de llamadas VoIP
colors:
  fondo: "#000000"
  superficie: "#0e0e10"
  superficie-alt: "#1c1c1e"
  linea: "rgb(255 255 255 / 0.1)"
  linea-fuerte: "rgb(255 255 255 / 0.18)"
  tinta: "#f5f5f7"
  tinta-secundaria: "#c7c7cc"
  mu: "#a1a1aa"
  primary: "#4f74a8"
  primary-dark: "#3f6290"
  primary-claro: "#9db7da"
  vos-fondo: "#1c2940"
  vos-borde: "rgb(79 116 168 / 0.45)"
  otra-fondo: "#1c1c1e"
  otra-borde: "rgb(255 255 255 / 0.08)"
  alerta: "#c8584f"
  alerta-fuerte: "#a93a36"
  alerta-tinta: "#e3a8a3"
  ok: "#5a9e78"
  ok-tinta: "#9fc9b0"
  aviso-badge-tinta: "#e0d2a0"
  resaltador: "#c9a84c"
  foco: "#9db7da"
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
  sm: "8px"
  md: "12px"
  lg: "20px"
  xl: "28px"
  pildora: "999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "#ffffff"
    rounded: "{rounded.pildora}"
    padding: "8px 16px"
---

## Overview

Consola de demostración de aula (modo Operate) diseñada para proyectarse en pantalla grande ante tribunal, tutor y docentes. La interfaz permite entender de una sola mirada quién habla, qué está transcribiendo el ASR en tiempo real, qué decidió el detector en cada turno y la trayectoria de riesgo a lo largo del tiempo. Los controles de configuración quedan en una barra compacta plegable para que el contenido protagonista ocupe todo el campo visual.

## Colors

Todo el panel usa la escena oscura de la llamada: consola en vivo, Probar el ASR, Historial, vista protegida y Presentación leen los mismos tokens del `:root` de `panel.html`. Los `--p-*` de la Presentación son alias de esos tokens.

- **Fondo (`fondo`: `#000000`)**: negro completo, igual que la proyección. Las cajas son paneles translúcidos (blanco al 2-4,5 %) con borde blanco al 10 %.
- **Tinta (`tinta`: `#f5f5f7`, `tinta-secundaria`: `#c7c7cc`, `mu`: `#a1a1aa`)**: grises neutros, todos por encima de 4.5:1 sobre negro y sobre `#1c1c1e`.
- **Persona protegida (`primary`: `#4f74a8`, burbuja `#1f2c42` → `#1b273b`, rótulos `primary-claro`)**: azul acerado y apagado, el mismo del teléfono derecho.
- **Otra persona (`otra-fondo`: `#1c1c1e`)**: gris de burbuja de mensajería, sin juicio inicial.
- **Alerta (`alerta`: `#c8584f` para bordes, `alerta-fuerte`: `#a93a36` para insignias rellenas con texto blanco, `alerta-tinta`: `#e3a8a3` para texto)**: reservada al aviso y a fallos.
- **Estado seguro y voz activa (`ok`: `#5a9e78`, `ok-tinta`: `#9fc9b0`)**: verde salvia, apagado.
- **Riesgo alto sin aviso**: ámbar (`#c9a84c` al 8-14 % de relleno, tinta `#e0d2a0`); el mismo amarillo resalta la cita culpable.

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
- **Vista de presentación (escena oscura con dos iPhone y diálogo central)**: comparte la paleta del resto del panel, pero oculta su cabecera, para que en la proyección solo se vean los teléfonos y la conversación.
  - Barra superior liviana sin caja: rótulo «Vista de presentación», estado de la llamada, identificador y botones en píldora. Los errores flotan debajo de la barra sin empujar la escena.
  - Dos iPhone grandes cuyo tamaño sale del alto de la ventana (`--tel-ancho = min(alto disponible × 0.485, 27vw, 540px)`, proporción 485:1000): unos 485px de ancho en 1920 × 1080 y 330px en 1366 × 768. Todo lo de adentro escala con unidades de contenedor (`cqw`), así que no hacen falta reglas por alto de pantalla.
  - Cada pantalla imita una llamada de iOS: barra de estado con isla dinámica (que se enciende en verde al hablar), nombre del rol, estado de voz en píldora, retrato plano (hombre de pelo oscuro, mujer mayor de pelo canoso) con anillo que late al hablar, medidor RMS por canal y botonera decorativa (altavoz, silencio, colgar). El teléfono protegido tiene tinte azul; con el aviso activo pasa a rojo y el avatar se achica para dejarle lugar a la tarjeta.
  - Sin halo detrás de los marcos: el estado se ve en el velo de la pantalla (azul apagado el protegido, rojo apagado con el aviso) y en el anillo del avatar al hablar.
  - Columna central (`minmax(0, 1fr)`) en un panel translúcido: burbujas oscuras estilo mensajería (gris para «Otra persona», azul para «Persona protegida»), scroll interno, seguimiento automático, botón «Volver al vivo» y cajas de evaluación con detalles desplegables. La frase que disparó el aviso lleva borde y resplandor rojos y la cita en resaltador amarillo.
  - Accesibilidad de foco: contorno visible de 2px en azul claro (`#9db7da`) con offset de 2px sobre el fondo oscuro.

## Elevation & Depth

- **Sin resplandores**: ni las tarjetas ni los marcos de los iPhone llevan halos de color. El estado se lee en el borde (tenue azul la protegida, verde mientras habla, rojo con el aviso) y en un velo de color muy leve desde el borde superior; el aviso no brilla, solo cambia de borde.
- Menús, ayuda y diálogos usan superficie sólida `#1c1c1e`, borde blanco al 18 % y sombra negra profunda; el fondo del diálogo modal se oscurece al 65 %.

## Shapes

- Botones, conmutador de modo, píldoras de estado, insignias y evaluaciones en píldora (`999px`).
- Burbujas de conversación con esquina de cola: `20 20 20 6` para «Otra persona» y `20 20 6 20` para «Persona protegida».
- Tarjetas de persona y cajas laterales con radio de 20px; panel de conversación, tarjetas de Probar el ASR y columnas del Historial con 28px. Selects y campos numéricos con 12px.

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
