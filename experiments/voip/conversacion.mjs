// @ts-check

/** Nombres de los roles, iguales en la conversación en vivo y en el Historial. */
/** @type {Record<string, string>} */
export const NOMBRE = {protegida: 'Persona protegida', otra: 'Otra persona'};

/** @param {string} texto @param {Map<string, string>} rolesPorLetra */
export function citaConRoles(texto, rolesPorLetra) {
  return texto.replace(/\\n/g, '\n').replace(/(^|\n)(\s*)([AB]):/g,
    (prefijo, salto, espacios, letra) => {
      const nombre = NOMBRE[rolesPorLetra.get(letra) || ''];
      return nombre ? `${salto}${espacios}${nombre}:` : prefijo;
    });
}

/** @param {string} rol */
export function plantillaLinea(rol) {
  return `<div class="quien"><span class="nombre-quien">${NOMBRE[rol] || rol}</span><span class="t"></span></div><div class="texto"></div>`;
}

/**
 * Burbuja de la conversación: la misma estructura y clases que usa la vista en vivo.
 * @param {string} rol @param {'parcial'|'final'} entrega @param {string} texto @param {string} tiempo
 */
export function crearLinea(rol, entrega, texto, tiempo) {
  const linea = document.createElement('div');
  linea.className = `linea ${rol} ${entrega}`;
  linea.innerHTML = plantillaLinea(rol);
  /** @type {HTMLElement} */ (linea.querySelector('.texto')).textContent = texto;
  /** @type {HTMLElement} */ (linea.querySelector('.t')).textContent = tiempo;
  return linea;
}

const AVATAR_OTRA_SVG = `
<svg viewBox="0 0 120 120" width="108" height="108" aria-hidden="true" focusable="false">
  <defs>
    <radialGradient id="avatar-otra-bg" cx="35%" cy="28%" r="72%">
      <stop offset="0%" stop-color="#334155"/>
      <stop offset="100%" stop-color="#0f172a"/>
    </radialGradient>
    <radialGradient id="avatar-otra-cara" cx="38%" cy="32%" r="65%">
      <stop offset="0%" stop-color="#fde047"/>
      <stop offset="68%" stop-color="#facc15"/>
      <stop offset="100%" stop-color="#eab308"/>
    </radialGradient>
  </defs>
  <circle cx="60" cy="60" r="56" fill="url(#avatar-otra-bg)"/>
  <path d="M24 106 C28 84 42 78 60 78 C78 78 92 84 96 106 Z" fill="#475569"/>
  <path d="M46 78 L60 95 L74 78 Z" fill="#e2e8f0"/>
  <circle cx="60" cy="52" r="27" fill="url(#avatar-otra-cara)"/>
  <path d="M35 45 C36 27 47 21 60 21 C73 21 84 27 85 45 C80 35 71 31 60 31 C49 31 40 35 35 45 Z" fill="#334155"/>
  <rect x="40" y="45" width="16" height="12" rx="5" fill="none" stroke="#0f172a" stroke-width="2.6"/>
  <rect x="64" y="45" width="16" height="12" rx="5" fill="none" stroke="#0f172a" stroke-width="2.6"/>
  <line x1="56" y1="50" x2="64" y2="50" stroke="#0f172a" stroke-width="2.6" stroke-linecap="round"/>
  <circle cx="48" cy="51" r="2.8" fill="#0f172a"/>
  <circle cx="72" cy="51" r="2.8" fill="#0f172a"/>
  <path d="M43 41 Q48 39 53 41" fill="none" stroke="#334155" stroke-width="2.4" stroke-linecap="round"/>
  <path d="M67 41 Q72 39 77 41" fill="none" stroke="#334155" stroke-width="2.4" stroke-linecap="round"/>
  <path d="M51 64 Q60 68 69 64" fill="none" stroke="#0f172a" stroke-width="2.8" stroke-linecap="round"/>
</svg>`;

const AVATAR_PROTEGIDA_SVG = `
<svg viewBox="0 0 120 120" width="108" height="108" aria-hidden="true" focusable="false">
  <defs>
    <radialGradient id="avatar-prot-bg" cx="35%" cy="28%" r="72%">
      <stop offset="0%" stop-color="#1d4ed8"/>
      <stop offset="100%" stop-color="#0f172a"/>
    </radialGradient>
    <radialGradient id="avatar-prot-cara" cx="38%" cy="32%" r="65%">
      <stop offset="0%" stop-color="#fde047"/>
      <stop offset="68%" stop-color="#facc15"/>
      <stop offset="100%" stop-color="#eab308"/>
    </radialGradient>
  </defs>
  <circle cx="60" cy="60" r="56" fill="url(#avatar-prot-bg)"/>
  <path d="M31 54 C31 30 43 20 60 20 C77 20 89 30 89 54 C89 67 84 74 79 77 L41 77 C36 74 31 67 31 54 Z" fill="#0f172a"/>
  <path d="M24 106 C28 84 42 78 60 78 C78 78 92 84 96 106 Z" fill="#1d4ed8"/>
  <path d="M47 78 C51 86 69 86 73 78" fill="none" stroke="#eff6ff" stroke-width="3" stroke-linecap="round"/>
  <circle cx="60" cy="53" r="26" fill="url(#avatar-prot-cara)"/>
  <path d="M34 48 C37 29 48 23 61 23 C73 23 83 30 86 47 C78 36 69 33 58 34 C47 35 39 40 34 48 Z" fill="#0f172a"/>
  <circle cx="49" cy="52" r="3.1" fill="#0f172a"/>
  <circle cx="71" cy="52" r="3.1" fill="#0f172a"/>
  <circle cx="43" cy="58" r="4" fill="#f87171" opacity="0.35"/>
  <circle cx="77" cy="58" r="4" fill="#f87171" opacity="0.35"/>
  <path d="M44 43 Q49 40 54 42" fill="none" stroke="#0f172a" stroke-width="2.4" stroke-linecap="round"/>
  <path d="M66 42 Q71 40 76 43" fill="none" stroke="#0f172a" stroke-width="2.4" stroke-linecap="round"/>
  <path d="M49 63 Q60 71 71 63" fill="none" stroke="#0f172a" stroke-width="2.8" stroke-linecap="round"/>
</svg>`;

const ESTILOS_PRESENTACION = `
  /* Escena oscura de presentación: fondo negro, dos iPhone grandes y el diálogo al centro.
     El tamaño del teléfono sale del alto de la ventana; lo de adentro escala con cqw. */
  #presentacion {
    display: none;
    flex: 1;
    max-width: 1920px;
    width: 100%;
    margin: 0 auto;
    padding: 0.75rem 1.5rem 1rem;
    box-sizing: border-box;
    color: #f5f5f7;
    --tel-alto: calc(100vh - 5.75rem);
    --tel-ancho: min(calc(var(--tel-alto) * 0.485), 27vw, 540px);
    /* Alias de la paleta única del panel (:root de panel.html). */
    --p-fondo: var(--fondo);
    --p-superficie: rgb(255 255 255 / 0.04);
    --p-borde: var(--linea);
    --p-tinta: var(--tinta);
    --p-tinta-2: var(--tinta-secundaria);
    --p-tinta-3: var(--mu);
    --p-azul: var(--primary);
    --p-azul-claro: var(--primary-claro);
    --p-verde: var(--ok);
    --p-rojo: var(--alerta);
    --p-rojo-fuerte: var(--alerta-fuerte);
    --p-foco: var(--foco);
  }
  body.presentacion {
    height: 100vh;
    overflow: hidden;
    background: #000000;
  }
  body.presentacion > header {
    display: none !important;
  }
  /* El tinte de alerta del panel pasa a ser un halo rojo detrás del teléfono protegido. */
  body.presentacion::before {
    background: radial-gradient(ellipse 45% 70% at 88% 50%, rgb(220 38 38 / 0.28), transparent 70%);
  }
  body.presentacion.alerta-emitida::before {
    opacity: 1;
  }
  /* Las reglas con display propio no deben pisar el atributo hidden. */
  #presentacion [hidden] {
    display: none !important;
  }
  body.presentacion #presentacion {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    flex: 1;
    min-height: 0;
    height: 100vh;
    max-height: 100vh;
    overflow: hidden;
  }
  body.presentacion #controles,
  body.presentacion main,
  body.presentacion #prueba-asr,
  body.presentacion #historial {
    display: none !important;
  }
  body.protegida #presentacion,
  body.asr #presentacion,
  body.historial #presentacion {
    display: none !important;
  }
  #presentacion button:focus-visible,
  #presentacion summary:focus-visible {
    outline: 2px solid var(--p-foco);
    outline-offset: 2px;
  }

  /* Barra superior: liviana, sin caja, para que los teléfonos sean protagonistas */
  #presentacion .pres-barra {
    position: relative;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 0.75rem 1rem;
    min-height: 2.5rem;
    padding: 0 0.25rem;
  }
  #presentacion .pres-barra-izq {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    min-width: 0;
  }
  #presentacion .pres-titulo {
    margin: 0;
    font-size: 0.8125rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--p-tinta-3);
    white-space: nowrap;
  }
  #presentacion .pres-estado-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    background: rgb(255 255 255 / 0.06);
    border: 1px solid var(--p-borde);
    font-size: 0.8125rem;
    font-weight: 600;
    color: var(--p-tinta);
    white-space: nowrap;
  }
  #presentacion .pres-estado-pill .punto {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--p-tinta-3);
  }
  #presentacion .pres-estado-pill[data-estado="en-llamada"] {
    border-color: rgb(48 209 88 / 0.45);
    color: #86efac;
  }
  #presentacion .pres-estado-pill[data-estado="en-llamada"] .punto {
    background: var(--p-verde);
    box-shadow: 0 0 0 0 rgb(48 209 88 / 0.6);
    animation: pres-latido 1.8s ease-out infinite;
  }
  @keyframes pres-latido {
    0% { box-shadow: 0 0 0 0 rgb(48 209 88 / 0.55); }
    70% { box-shadow: 0 0 0 7px rgb(48 209 88 / 0); }
    100% { box-shadow: 0 0 0 0 rgb(48 209 88 / 0); }
  }
  #presentacion .pres-estado-pill[data-estado="finalizado"] {
    border-color: rgb(10 132 255 / 0.5);
    color: var(--p-azul-claro);
  }
  #presentacion .pres-estado-pill[data-estado="finalizado"] .punto {
    background: var(--p-azul);
  }
  #presentacion .pres-estado-pill[data-estado="sin-conexion"] {
    border-color: rgb(255 69 58 / 0.5);
    color: #fca5a5;
  }
  #presentacion .pres-estado-pill[data-estado="sin-conexion"] .punto {
    background: var(--p-rojo);
  }
  #presentacion .pres-id {
    font: 500 0.8125rem/1.2 ui-monospace, SFMono-Regular, Menlo, monospace;
    color: var(--p-tinta-3);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  #presentacion .pres-acciones {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex-shrink: 0;
  }
  #presentacion .pres-btn-secundario,
  #presentacion .pres-btn-primario,
  #presentacion .pres-btn-terminar {
    padding: 0.45rem 1rem;
    border-radius: 999px;
    font-size: 0.875rem;
    font-weight: 600;
    cursor: pointer;
    transition: background-color 150ms var(--salida), border-color 150ms var(--salida);
  }
  #presentacion .pres-btn-secundario {
    background: rgb(255 255 255 / 0.06);
    color: var(--p-tinta);
    border: 1px solid rgb(255 255 255 / 0.16);
  }
  #presentacion .pres-btn-secundario:hover:not(:disabled) {
    background: rgb(255 255 255 / 0.12);
  }
  #presentacion .pres-btn-primario {
    background: var(--p-azul);
    color: #ffffff;
    border: 1px solid var(--p-azul);
  }
  #presentacion .pres-btn-primario:hover:not(:disabled) {
    background: #0070e0;
  }
  #presentacion .pres-btn-terminar {
    background: rgb(255 69 58 / 0.12);
    color: #fca5a5;
    border: 1px solid rgb(255 69 58 / 0.45);
  }
  #presentacion .pres-btn-terminar:hover:not(:disabled) {
    background: rgb(255 69 58 / 0.22);
  }
  #presentacion .pres-btn-secundario:disabled,
  #presentacion .pres-btn-primario:disabled,
  #presentacion .pres-btn-terminar:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }
  /* El error flota bajo la barra: no empuja la escena ni saca a los teléfonos de la ventana. */
  #presentacion .pres-error {
    position: absolute;
    top: calc(100% + 0.4rem);
    left: 50%;
    transform: translateX(-50%);
    z-index: 20;
    margin: 0;
    max-width: min(90%, 52rem);
    padding: 0.5rem 1rem;
    border-radius: 12px;
    background: rgb(69 10 10 / 0.92);
    border: 1px solid rgb(255 69 58 / 0.6);
    color: #fecaca;
    font-size: 0.875rem;
    font-weight: 600;
    box-shadow: 0 10px 30px rgb(0 0 0 / 0.6);
  }

  #presentacion .pres-escena {
    display: grid;
    grid-template-columns: var(--tel-ancho) minmax(0, 1fr) var(--tel-ancho);
    gap: clamp(1rem, 2.2vw, 2.75rem);
    align-items: center;
    flex: 1;
    min-height: 0;
  }

  /* iPhone: marco de titanio, bisel negro y pantalla de llamada */
  #presentacion .pres-telefono {
    display: flex;
    justify-content: center;
    align-self: center;
  }
  #presentacion .pres-iphone-marco {
    position: relative;
    container-type: inline-size;
    width: var(--tel-ancho);
    aspect-ratio: 485 / 1000;
    box-sizing: border-box;
    padding: calc(var(--tel-ancho) * 0.032);
    border-radius: calc(var(--tel-ancho) * 0.17);
    background: linear-gradient(145deg, #4a4a4f 0%, #1c1c1f 22%, #0b0b0d 50%, #1c1c1f 78%, #3d3d42 100%);
    box-shadow:
      inset 0 0 0 1.5px rgb(255 255 255 / 0.14),
      inset 0 0 0 calc(var(--tel-ancho) * 0.018) #050506,
      0 0 0 1px #000000,
      0 40px 80px -30px rgb(0 0 0 / 0.9),
      0 0 120px -30px var(--tel-halo, rgb(255 255 255 / 0.08));
    transition: box-shadow 400ms var(--salida);
  }
  #presentacion .pres-telefono.protegida {
    --tel-halo: rgb(10 132 255 / 0.35);
  }
  #presentacion .pres-telefono.hablando-activo {
    --tel-halo: rgb(48 209 88 / 0.45);
  }
  #presentacion .pres-telefono.protegida:has(.pres-aviso-tarjeta:not([hidden])) {
    --tel-halo: rgb(255 69 58 / 0.6);
  }
  /* Botones laterales del marco */
  #presentacion .pres-iphone-marco::before,
  #presentacion .pres-iphone-marco::after {
    content: "";
    position: absolute;
    width: 3px;
    border-radius: 2px;
    background: linear-gradient(90deg, #2a2a2e, #5a5a60);
  }
  #presentacion .pres-iphone-marco::before {
    left: -3px;
    top: 22%;
    height: 14%;
    box-shadow: 0 -9cqw 0 0 #3a3a3f;
  }
  #presentacion .pres-iphone-marco::after {
    right: -3px;
    top: 28%;
    height: 18%;
  }
  #presentacion .pres-iphone-pantalla {
    position: relative;
    height: 100%;
    box-sizing: border-box;
    overflow: hidden;
    border-radius: calc(var(--tel-ancho) * 0.14);
    background-color: #0b0b0f;
    background-image:
      radial-gradient(120% 60% at 50% 0%, rgb(255 255 255 / 0.10), transparent 60%),
      linear-gradient(180deg, #24252c 0%, #121318 45%, #07070a 100%);
    color: #ffffff;
    padding: 2.5cqw 6cqw 4cqw;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    align-items: center;
    text-align: center;
    gap: 2.5cqw;
  }
  #presentacion .pres-telefono.protegida .pres-iphone-pantalla {
    background-image:
      radial-gradient(120% 60% at 50% 0%, rgb(10 132 255 / 0.32), transparent 62%),
      linear-gradient(180deg, #0f1f3d 0%, #0a1222 45%, #05070d 100%);
  }
  #presentacion .pres-telefono.protegida:has(.pres-aviso-tarjeta:not([hidden])) .pres-iphone-pantalla {
    background-image:
      radial-gradient(120% 60% at 50% 0%, rgb(255 69 58 / 0.30), transparent 62%),
      linear-gradient(180deg, #2a0f12 0%, #150a0c 45%, #07050a 100%);
  }

  /* Barra de estado del teléfono con la isla dinámica */
  #presentacion .pres-estado-ios {
    width: 100%;
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    align-items: center;
    font-size: max(11px, 3.6cqw);
    font-weight: 600;
    color: #ffffff;
    font-variant-numeric: tabular-nums;
  }
  #presentacion .pres-estado-ios-hora {
    justify-self: start;
    padding-left: 3cqw;
  }
  #presentacion .pres-estado-ios-iconos {
    justify-self: end;
    display: inline-flex;
    align-items: center;
    gap: 1.4cqw;
    padding-right: 2cqw;
  }
  #presentacion .pres-estado-ios-iconos svg {
    height: 3.2cqw;
    width: auto;
  }
  #presentacion .pres-isla {
    width: 30cqw;
    height: 8.5cqw;
    background: #000000;
    border-radius: 999px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 2.6cqw;
    box-sizing: border-box;
  }
  #presentacion .pres-isla-camara {
    width: 2.6cqw;
    height: 2.6cqw;
    border-radius: 50%;
    background: radial-gradient(circle at 35% 35%, #2b3a55, #0a0d14 70%);
  }
  #presentacion .pres-isla-onda {
    width: 2.2cqw;
    height: 2.2cqw;
    border-radius: 50%;
    background: #1f1f23;
    transition: transform 160ms var(--salida), background-color 160ms var(--salida);
  }
  #presentacion .pres-telefono.hablando-activo .pres-isla-onda {
    background: var(--p-verde);
    box-shadow: 0 0 2cqw var(--p-verde);
    transform: scale(1.2);
  }

  #presentacion .pres-pantalla-cabecera {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2cqw;
    width: 100%;
    margin-top: 2cqw;
  }
  #presentacion .pres-llamada-etiqueta {
    font-size: max(11px, 3.6cqw);
    font-weight: 500;
    letter-spacing: 0.02em;
    color: var(--p-tinta-2);
  }
  #presentacion .pres-rol-nombre {
    margin: 0;
    font-size: max(20px, 8.2cqw);
    font-weight: 600;
    letter-spacing: -0.02em;
    line-height: 1.1;
    color: #ffffff;
  }
  #presentacion .pres-estado-voz {
    display: inline-flex;
    align-items: center;
    gap: 1.6cqw;
    padding: 1cqw 3.2cqw;
    border-radius: 999px;
    background: rgb(255 255 255 / 0.10);
    border: 1px solid rgb(255 255 255 / 0.12);
    color: #ffffff;
    font-size: max(12px, 3.7cqw);
    font-weight: 600;
    transition: background-color 200ms var(--salida), border-color 200ms var(--salida);
  }
  #presentacion .pres-estado-voz[data-voz="hablando"] {
    background: rgb(48 209 88 / 0.22);
    border-color: rgb(48 209 88 / 0.6);
  }
  #presentacion .pres-estado-voz[data-voz="finalizado"] {
    background: rgb(10 132 255 / 0.22);
    border-color: rgb(10 132 255 / 0.6);
  }
  #presentacion .pres-voz-punto {
    width: 2cqw;
    height: 2cqw;
    min-width: 6px;
    min-height: 6px;
    border-radius: 50%;
    background: var(--p-tinta-3);
  }
  #presentacion .pres-estado-voz[data-voz="hablando"] .pres-voz-punto {
    background: var(--p-verde);
  }
  #presentacion .pres-estado-voz[data-voz="finalizado"] .pres-voz-punto {
    background: var(--p-azul);
  }

  /* Avatar grande con anillos que laten mientras la persona habla */
  #presentacion .pres-perfil-area {
    flex: 1;
    min-height: 0;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  #presentacion .pres-avatar-anillo {
    position: relative;
    padding: 2cqw;
    border-radius: 50%;
    background: rgb(255 255 255 / 0.05);
    box-shadow: 0 0 0 1px rgb(255 255 255 / 0.10);
    transition: transform 200ms var(--salida), box-shadow 200ms var(--salida);
  }
  #presentacion .pres-telefono.protegida .pres-avatar-anillo {
    background: rgb(10 132 255 / 0.10);
    box-shadow: 0 0 0 1px rgb(10 132 255 / 0.35);
  }
  #presentacion .pres-telefono.hablando-activo .pres-avatar-anillo {
    transform: scale(1.04);
    box-shadow: 0 0 0 1.2cqw rgb(48 209 88 / 0.18), 0 0 0 2.6cqw rgb(48 209 88 / 0.08), 0 0 8cqw rgb(48 209 88 / 0.35);
  }
  #presentacion .pres-avatar-circulo {
    width: 44cqw;
    height: 44cqw;
    border-radius: 50%;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #1c1c1f;
    transition: width 300ms var(--salida), height 300ms var(--salida);
  }
  #presentacion .pres-avatar-circulo svg {
    width: 100%;
    height: 100%;
  }
  /* Con el aviso en pantalla el avatar se achica para dejarle lugar. */
  #presentacion .pres-iphone-pantalla:has(.pres-aviso-tarjeta:not([hidden])) .pres-avatar-circulo {
    width: 34cqw;
    height: 34cqw;
  }

  #presentacion .pres-actividad-caja {
    width: 100%;
    box-sizing: border-box;
    background: rgb(255 255 255 / 0.06);
    border: 1px solid rgb(255 255 255 / 0.08);
    border-radius: 5cqw;
    padding: 2.6cqw 4cqw;
    display: flex;
    flex-direction: column;
    gap: 1.6cqw;
  }
  #presentacion .pres-ondas {
    height: 8cqw;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 2cqw;
  }
  #presentacion .pres-onda-barra {
    width: 2cqw;
    height: 7.5cqw;
    border-radius: 999px;
    background: rgb(255 255 255 / 0.35);
    transform: scaleY(0.22);
    transform-origin: center;
    transition: transform 100ms var(--salida), background-color 120ms var(--salida);
  }
  #presentacion .pres-telefono.hablando-activo .pres-onda-barra {
    background: var(--p-verde);
  }
  #presentacion .pres-meter-fila {
    display: grid;
    grid-template-columns: auto 1fr auto;
    align-items: center;
    gap: 2cqw;
  }
  #presentacion .pres-canal-tag,
  #presentacion .pres-rms {
    font-size: max(10px, 3cqw);
    font-weight: 600;
    letter-spacing: 0.04em;
    color: var(--p-tinta-2);
    text-transform: uppercase;
    font-variant-numeric: tabular-nums;
  }
  #presentacion .pres-rms {
    text-align: right;
  }
  #presentacion .pres-meter-fila meter {
    width: 100%;
    height: 1.6cqw;
    min-height: 5px;
    appearance: none;
    border: 0;
    border-radius: 999px;
    background: rgb(255 255 255 / 0.12);
  }
  #presentacion .pres-meter-fila meter::-webkit-meter-bar {
    background: rgb(255 255 255 / 0.12);
    border: 0;
    border-radius: 999px;
    height: 100%;
  }
  #presentacion .pres-meter-fila meter::-webkit-meter-optimum-value,
  #presentacion .pres-meter-fila meter::-webkit-meter-suboptimum-value,
  #presentacion .pres-meter-fila meter::-webkit-meter-even-less-good-value {
    background: var(--p-verde);
    border-radius: 999px;
  }

  /* Botonera de llamada decorativa: altavoz, silencio y colgar */
  #presentacion .pres-controles-decorativos {
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 3.5cqw;
  }
  #presentacion .pres-iconos-fila {
    display: flex;
    justify-content: center;
    gap: 6cqw;
  }
  #presentacion .pres-icono-deco {
    width: 14cqw;
    height: 14cqw;
    border-radius: 50%;
    background: rgb(255 255 255 / 0.14);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    color: #ffffff;
  }
  #presentacion .pres-icono-deco.colgar {
    background: var(--p-rojo);
  }
  #presentacion .pres-icono-deco svg {
    width: 45%;
    height: 45%;
  }
  #presentacion .pres-home-bar {
    width: 32cqw;
    height: 1.2cqw;
    min-height: 4px;
    border-radius: 999px;
    background: rgb(255 255 255 / 0.85);
  }

  /* Columna central del diálogo */
  #presentacion .pres-centro {
    align-self: stretch;
    background: linear-gradient(180deg, rgb(255 255 255 / 0.045), rgb(255 255 255 / 0.02));
    border: 1px solid var(--p-borde);
    border-radius: 28px;
    display: flex;
    flex-direction: column;
    min-height: 0;
    height: 100%;
    max-height: 100%;
    position: relative;
    overflow: hidden;
  }
  #presentacion .pres-centro-cabecera {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: baseline;
    gap: 0.5rem;
    padding: 1rem 1.5rem 0.85rem;
    border-bottom: 1px solid rgb(255 255 255 / 0.07);
    flex-shrink: 0;
  }
  #presentacion .pres-centro-titulo {
    margin: 0;
    font-size: 1.125rem;
    font-weight: 600;
    letter-spacing: -0.01em;
    color: var(--p-tinta);
  }
  #presentacion .pres-centro-sub {
    font-size: 0.8125rem;
    font-weight: 500;
    color: var(--p-tinta-3);
  }
  #presentacion .pres-charla {
    flex: 1;
    min-height: 0;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 0.85rem;
    padding: 1.25rem 1.5rem 3.5rem;
    scroll-behavior: smooth;
    scrollbar-color: rgb(255 255 255 / 0.18) transparent;
  }
  #presentacion .pres-charla::-webkit-scrollbar {
    width: 8px;
  }
  #presentacion .pres-charla::-webkit-scrollbar-track {
    background: transparent;
  }
  #presentacion .pres-charla::-webkit-scrollbar-thumb {
    background: rgb(255 255 255 / 0.16);
    border-radius: 999px;
  }
  #presentacion .pres-charla::-webkit-scrollbar-thumb:hover {
    background: rgb(255 255 255 / 0.3);
  }
  #presentacion .pres-charla:empty::before {
    content: "Esperando las primeras frases confirmadas de la llamada…";
    color: var(--p-tinta-3);
    font-size: 1.0625rem;
    font-weight: 500;
    margin: auto;
    text-align: center;
    max-width: 44ch;
  }
  #presentacion .pres-charla .linea {
    width: auto;
    min-width: 42%;
    max-width: 80%;
    padding: 0.75rem 1rem 0.8rem;
    border-radius: 20px 20px 20px 6px;
    background: #1c1c1e;
    border: 1px solid rgb(255 255 255 / 0.08);
    word-break: break-word;
    overflow-wrap: break-word;
  }
  #presentacion .pres-charla .linea.protegida {
    border-radius: 20px 20px 6px 20px;
    background: linear-gradient(180deg, #0f2a55, #0b2046);
    border-color: rgb(10 132 255 / 0.45);
  }
  #presentacion .pres-charla .linea.parcial {
    border-style: dashed;
    border-color: rgb(255 255 255 / 0.25);
  }
  #presentacion .pres-charla .linea.parcial .texto {
    color: var(--p-tinta-2);
  }
  #presentacion .pres-charla .pres-provisorio-tag {
    display: inline-block;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--p-tinta-2);
    background: rgb(255 255 255 / 0.06);
    border: 1px dashed rgb(255 255 255 / 0.25);
    border-radius: 999px;
    padding: 0.1rem 0.5rem;
  }
  #presentacion .pres-charla .linea .quien {
    font-size: 0.8125rem;
    font-weight: 600;
    color: var(--p-tinta-3);
  }
  #presentacion .pres-charla .linea.protegida .quien {
    color: var(--p-azul-claro);
  }
  #presentacion .pres-charla .linea .t {
    color: var(--p-tinta-3);
  }
  #presentacion .pres-charla .linea .texto {
    font-size: 1.125rem;
    line-height: 1.45;
    color: var(--p-tinta);
  }
  #presentacion .pres-btn-volver-vivo {
    position: absolute;
    bottom: 1rem;
    left: 50%;
    transform: translateX(-50%);
    z-index: 10;
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.5rem 1.15rem;
    border-radius: 999px;
    background: #f5f5f7;
    color: #0b0b0f;
    border: 0;
    font-size: 0.875rem;
    font-weight: 700;
    cursor: pointer;
    box-shadow: 0 10px 30px rgb(0 0 0 / 0.6);
    transition: background-color 150ms var(--salida);
  }
  #presentacion .pres-btn-volver-vivo:hover {
    background: #ffffff;
  }
  @media (max-width: 1120px) {
    #presentacion .pres-charla .linea {
      max-width: 92%;
    }
  }
  @media (max-width: 820px) {
    body.presentacion {
      height: auto;
      overflow: auto;
    }
    body.presentacion #presentacion {
      height: auto;
      max-height: none;
    }
    #presentacion {
      --tel-ancho: 44vw;
    }
    #presentacion .pres-escena {
      grid-template-columns: 1fr 1fr;
    }
    #presentacion .pres-centro {
      grid-column: 1 / -1;
      order: 2;
      height: 70vh;
    }
  }
  @media (min-width: 1700px) {
    #presentacion .pres-charla .linea .texto {
      font-size: 1.25rem;
    }
  }

  /* Aviso en el teléfono protegido: notificación del sistema */
  #presentacion .pres-aviso-tarjeta {
    width: 100%;
    box-sizing: border-box;
    background: rgb(40 8 10 / 0.88);
    border: 1px solid rgb(255 69 58 / 0.65);
    border-radius: 5.5cqw;
    padding: 3.2cqw 3.8cqw;
    display: flex;
    flex-direction: column;
    gap: 1.6cqw;
    text-align: left;
    box-shadow: 0 0 0 1px rgb(0 0 0 / 0.4), 0 2cqw 8cqw rgb(255 69 58 / 0.25);
    animation: pres-aviso-entra 260ms var(--salida);
  }
  @keyframes pres-aviso-entra {
    from { opacity: 0; transform: translateY(-6px) scale(0.97); }
    to { opacity: 1; transform: none; }
  }
  #presentacion .pres-aviso-cabecera {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 2cqw;
  }
  #presentacion .pres-aviso-badge {
    display: inline-flex;
    align-items: center;
    gap: 1.4cqw;
    padding: 0.8cqw 2.4cqw;
    border-radius: 999px;
    background: var(--p-rojo-fuerte);
    color: #ffffff;
    font-size: max(10px, 3.1cqw);
    font-weight: 800;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    white-space: nowrap;
  }
  #presentacion .pres-aviso-tiempo {
    font-size: max(10px, 3.1cqw);
    font-weight: 600;
    color: #fca5a5;
    font-variant-numeric: tabular-nums;
    white-space: nowrap;
  }
  #presentacion .pres-aviso-motivo {
    margin: 0;
    font-size: max(13px, 4.3cqw);
    font-weight: 700;
    color: #ffffff;
    line-height: 1.3;
  }
  #presentacion .pres-aviso-cita {
    margin: 0;
    padding: 0.6cqw 0 0.6cqw 2.6cqw;
    border-left: 2px solid var(--p-rojo);
    color: #fecaca;
    font-size: max(12px, 3.7cqw);
    font-style: italic;
    line-height: 1.35;
    word-break: break-word;
  }
  #presentacion .pres-aviso-botones {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2cqw;
    margin-top: 0.6cqw;
  }
  #presentacion .pres-aviso-btn-sonido,
  #presentacion .pres-aviso-btn-cerrar {
    border-radius: 999px;
    padding: 1.6cqw 2cqw;
    font-size: max(11px, 3.4cqw);
    font-weight: 700;
    cursor: pointer;
  }
  #presentacion .pres-aviso-btn-sonido {
    background: rgb(255 255 255 / 0.10);
    color: #ffffff;
    border: 1px solid rgb(255 255 255 / 0.2);
  }
  #presentacion .pres-aviso-btn-sonido:hover {
    background: rgb(255 255 255 / 0.18);
  }
  #presentacion .pres-aviso-btn-cerrar {
    background: var(--p-rojo-fuerte);
    color: #ffffff;
    border: 1px solid var(--p-rojo-fuerte);
  }
  #presentacion .pres-aviso-btn-cerrar:hover {
    background: #b91c1c;
  }

  /* Cajas de evaluación adjuntas a cada frase */
  #presentacion .pres-eval-caja {
    margin-top: 0.55rem;
    padding: 0.45rem 0.65rem;
    border-radius: 12px;
    border: 1px solid rgb(255 255 255 / 0.1);
    background: rgb(0 0 0 / 0.25);
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    box-sizing: border-box;
    font-size: 0.875rem;
  }
  #presentacion .pres-eval-caja.estado-analizando {
    border-style: dashed;
    border-color: rgb(255 255 255 / 0.2);
  }
  #presentacion .pres-eval-caja.estado-sin-aviso {
    border-color: rgb(48 209 88 / 0.3);
    background: rgb(48 209 88 / 0.07);
  }
  #presentacion .pres-eval-caja.estado-posible-estafa,
  #presentacion .pres-eval-caja.estado-error {
    border-color: rgb(255 69 58 / 0.5);
    background: rgb(255 69 58 / 0.1);
  }
  #presentacion .pres-eval-fila {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0.45rem 0.65rem;
  }
  #presentacion .pres-eval-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.15rem 0.55rem;
    border-radius: 999px;
    font-size: 0.6875rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
  }
  #presentacion .pres-eval-badge.analizando {
    background: rgb(255 255 255 / 0.06);
    border: 1px solid rgb(255 255 255 / 0.2);
    color: var(--p-tinta-2);
  }
  #presentacion .pres-eval-punto {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--p-tinta-2);
  }
  #presentacion .pres-eval-badge.sin-aviso {
    background: rgb(48 209 88 / 0.14);
    border: 1px solid rgb(48 209 88 / 0.55);
    color: #86efac;
  }
  #presentacion .pres-eval-badge.posible-estafa,
  #presentacion .pres-eval-badge.error {
    background: var(--p-rojo-fuerte);
    border: 1px solid var(--p-rojo-fuerte);
    color: #ffffff;
  }
  #presentacion .pres-eval-badge.no-evaluado {
    background: rgb(255 255 255 / 0.1);
    border: 1px solid rgb(255 255 255 / 0.18);
    color: var(--p-tinta-2);
  }
  #presentacion .pres-eval-motivo {
    font-size: 0.8125rem;
    font-weight: 500;
    color: var(--p-tinta-2);
    word-break: break-word;
  }
  #presentacion .pres-eval-caja.estado-posible-estafa .pres-eval-motivo,
  #presentacion .pres-eval-caja.estado-error .pres-eval-motivo {
    color: #fecaca;
    font-weight: 700;
  }

  /* Panel desplegable de detalles técnicos */
  #presentacion .pres-detalles {
    margin-top: 0.15rem;
  }
  #presentacion .pres-detalles-summary {
    cursor: pointer;
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--p-tinta-3);
    user-select: none;
    outline: none;
  }
  #presentacion .pres-detalles-summary:hover {
    color: var(--p-tinta);
  }
  #presentacion .pres-detalles-summary:focus-visible {
    outline: 2px solid var(--p-foco);
    outline-offset: 2px;
  }
  #presentacion .pres-detalles-contenido {
    margin-top: 0.35rem;
    padding-top: 0.35rem;
    border-top: 1px dashed rgb(255 255 255 / 0.14);
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    font-size: 0.8125rem;
  }
  #presentacion .pres-det-fila {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    gap: 0.5rem;
  }
  #presentacion .pres-det-etiqueta {
    font-weight: 500;
    color: var(--p-tinta-3);
  }
  #presentacion .pres-det-valor {
    font-weight: 600;
    color: var(--p-tinta);
    font-variant-numeric: tabular-nums;
    text-align: right;
  }

  /* Cita culpable y disparo de aviso */
  #presentacion .pres-cita-culpable {
    background: #facc15;
    color: #1a1204;
    padding: 0 4px;
    border-radius: 4px;
    font-weight: 700;
  }
  #presentacion .linea.pres-disparo-aviso {
    border-color: rgb(255 69 58 / 0.75) !important;
    box-shadow: 0 0 0 1px rgb(255 69 58 / 0.35), 0 0 32px -6px rgb(255 69 58 / 0.45);
  }
  @media (prefers-reduced-motion: reduce) {
    #presentacion .pres-avatar-anillo,
    #presentacion .pres-avatar-circulo,
    #presentacion .pres-onda-barra,
    #presentacion .pres-isla-onda {
      transition: none !important;
      transform: none !important;
    }
    #presentacion .pres-estado-pill .punto {
      animation: none !important;
    }
    #presentacion .pres-charla {
      scroll-behavior: auto !important;
    }
    #presentacion .pres-charla .linea {
      animation: none !important;
    }
    #presentacion .pres-btn-volver-vivo {
      transition: none !important;
    }
    #presentacion .pres-aviso-tarjeta {
      animation: none !important;
    }
  }
`;

const ICONOS_ESTADO_IOS = `
              <svg viewBox="0 0 18 12" fill="currentColor"><rect x="0" y="8" width="3" height="4" rx="1"/><rect x="5" y="5.5" width="3" height="6.5" rx="1"/><rect x="10" y="3" width="3" height="9" rx="1"/><rect x="15" y="0" width="3" height="12" rx="1"/></svg>
              <svg viewBox="0 0 16 12" fill="currentColor"><path d="M8 2.5c2.3 0 4.4.9 6 2.4l1.3-1.4A10.6 10.6 0 0 0 8 .5C5.2.5 2.6 1.6.7 3.5L2 4.9a8.6 8.6 0 0 1 6-2.4Zm0 3.5c1.4 0 2.6.5 3.6 1.4l1.3-1.4A7.1 7.1 0 0 0 8 4c-1.9 0-3.6.7-4.9 2l1.3 1.4C5.4 6.5 6.6 6 8 6Zm0 3.5c-.6 0-1.1.2-1.5.6L8 11.6l1.5-1.5c-.4-.4-.9-.6-1.5-.6Z"/></svg>
              <svg viewBox="0 0 27 12" fill="none"><rect x="0.5" y="0.5" width="23" height="11" rx="3" stroke="currentColor" opacity="0.45"/><rect x="2" y="2" width="18" height="8" rx="1.8" fill="currentColor"/><rect x="24.8" y="4" width="1.7" height="4" rx="0.8" fill="currentColor" opacity="0.45"/></svg>`;

/**
 * Arma la silueta de iPhone para un rol («otra» a la izquierda, «protegida» a la derecha).
 * @param {'otra'|'protegida'} rol
 */
function plantillaTelefono(rol) {
  const esOtra = rol === 'otra';
  const nombre = NOMBRE[rol];
  const canalTxt = esOtra ? 'Canal izq' : 'Canal der';
  const avatar = esOtra ? AVATAR_OTRA_SVG : AVATAR_PROTEGIDA_SVG;
  const avisoHtml = esOtra ? '' : `
          <div id="pres-aviso-protegida" class="pres-aviso-tarjeta" role="alert" hidden>
            <div class="pres-aviso-cabecera">
              <span class="pres-aviso-badge">Posible estafa</span>
              <span class="pres-aviso-tiempo" id="pres-aviso-tiempo"></span>
            </div>
            <p class="pres-aviso-motivo" id="pres-aviso-motivo"></p>
            <blockquote class="pres-aviso-cita" id="pres-aviso-cita" hidden></blockquote>
            <div class="pres-aviso-botones">
              <button type="button" class="pres-aviso-btn-sonido" id="pres-aviso-btn-sonido" aria-pressed="true">Sonido: sí</button>
              <button type="button" class="pres-aviso-btn-cerrar" id="pres-aviso-btn-cerrar">Cerrar aviso</button>
            </div>
          </div>`;
  return `
    <article class="pres-telefono ${rol}" id="pres-telefono-${rol}" data-rol="${rol}" data-actividad="silencio" aria-label="Teléfono de ${nombre}">
      <div class="pres-iphone-marco">
        <div class="pres-iphone-pantalla">
          <div class="pres-estado-ios" aria-hidden="true">
            <span class="pres-estado-ios-hora">9:41</span>
            <div class="pres-isla">
              <span class="pres-isla-camara"></span>
              <span class="pres-isla-onda"></span>
            </div>
            <span class="pres-estado-ios-iconos">${ICONOS_ESTADO_IOS}
            </span>
          </div>
          <div class="pres-pantalla-cabecera">
            <span class="pres-llamada-etiqueta" aria-hidden="true">Llamada de voz</span>
            <h3 class="pres-rol-nombre" id="pres-nombre-${rol}">${nombre}</h3>
            <span class="pres-estado-voz" id="pres-voz-${rol}" data-voz="silencio">
              <span class="pres-voz-punto" aria-hidden="true"></span>
              <span id="pres-voz-txt-${rol}">En silencio</span>
            </span>
          </div>
${avisoHtml}
          <div class="pres-perfil-area">
            <div class="pres-avatar-anillo" id="pres-anillo-${rol}">
              <div class="pres-avatar-circulo" role="img" aria-label="Avatar ilustrado estilo emoji de ${nombre}">
                ${avatar}
              </div>
            </div>
          </div>
          <div class="pres-actividad-caja" aria-label="Actividad de voz de ${nombre}">
            <div class="pres-ondas" id="pres-ondas-${rol}" aria-hidden="true">
              <span class="pres-onda-barra"></span>
              <span class="pres-onda-barra"></span>
              <span class="pres-onda-barra"></span>
              <span class="pres-onda-barra"></span>
              <span class="pres-onda-barra"></span>
            </div>
            <div class="pres-meter-fila">
              <span class="pres-canal-tag">${canalTxt}</span>
              <meter id="pres-nivel-${rol}" min="0" max="1" value="0" aria-label="Nivel de voz de ${nombre}"></meter>
              <output class="pres-rms" id="pres-rms-${rol}" for="pres-nivel-${rol}">RMS 0.000</output>
            </div>
          </div>
          <div class="pres-controles-decorativos" aria-hidden="true">
            <div class="pres-iconos-fila">
              <span class="pres-icono-deco">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M15.54 8.46a5 5 0 0 1 0 7.07"></path><path d="M19.07 4.93a10 10 0 0 1 0 14.14"></path></svg>
              </span>
              <span class="pres-icono-deco">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="23"></line></svg>
              </span>
              <span class="pres-icono-deco colgar">
                <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 9c-2.6 0-5.1.5-7.4 1.5-.9.4-1.4 1.3-1.3 2.3l.2 1.8c.1.9.9 1.5 1.8 1.4l2.7-.4c.8-.1 1.4-.8 1.4-1.6v-1.4c1.7-.4 3.5-.4 5.2 0V14c0 .8.6 1.5 1.4 1.6l2.7.4c.9.1 1.7-.5 1.8-1.4l.2-1.8c.1-1-.4-1.9-1.3-2.3C17.1 9.5 14.6 9 12 9Z"/></svg>
              </span>
            </div>
            <span class="pres-home-bar"></span>
          </div>
        </div>
      </div>
    </article>`;
}

/**
 * Vista de presentación de la llamada con dos teléfonos y diálogo central confirmado.
 * @param {{terminar: () => void, nueva: () => void, cambiar: () => void, alVolverAlPanel?: () => void}} acciones
 */
export function montarPresentacion(acciones) {
  const seccion = document.createElement('section');
  seccion.id = 'presentacion';
  seccion.hidden = true;
  seccion.setAttribute('aria-label', 'Vista de presentación de la llamada');
  seccion.innerHTML = `
    <style>${ESTILOS_PRESENTACION}</style>
    <div class="pres-barra">
      <div class="pres-barra-izq">
        <h2 class="pres-titulo">Vista de presentación</h2>
        <span class="pres-estado-pill" id="pres-estado-pill" data-estado="esperando">
          <span class="punto" aria-hidden="true"></span>
          <span id="pres-estado" role="status">Esperando inicio</span>
        </span>
        <span class="pres-id" id="pres-llamada-id" aria-label="Identificador de la llamada"></span>
      </div>
      <div class="pres-acciones">
        <button type="button" id="volver-panel" class="pres-btn-secundario">← Volver al panel</button>
        <button type="button" id="pres-nueva" class="pres-btn-primario" hidden disabled>Nueva llamada</button>
        <button type="button" id="pres-terminar" class="pres-btn-terminar" disabled>Terminar análisis</button>
      </div>
      <p id="pres-error" class="pres-error" role="alert" hidden></p>
    </div>
    <div class="pres-escena">
      ${plantillaTelefono('otra')}
      <section class="pres-centro" aria-label="Diálogo confirmado en el centro">
        <div class="pres-centro-cabecera">
          <h3 class="pres-centro-titulo">Diálogo de la conversación</h3>
          <span class="pres-centro-sub" id="pres-dialogo-sub">Frases finales por canal</span>
        </div>
        <div id="pres-charla" class="pres-charla" role="log" aria-live="polite" aria-label="Frases finales de ambos roles"></div>
        <button type="button" id="pres-volver-vivo" class="pres-btn-volver-vivo" hidden aria-label="Volver al vivo">↓ Volver al vivo</button>
      </section>
      ${plantillaTelefono('protegida')}
    </div>`;
  document.querySelector('main')?.before(seccion);

  /** @template {HTMLElement} T @param {string} id @returns {T} */
  const el = id => /** @type {T} */ (seccion.querySelector(`#${id}`));
  const estadoPill = el('pres-estado-pill');
  const estadoTxt = el('pres-estado');
  const llamadaIdEl = el('pres-llamada-id');
  const dialogoSub = el('pres-dialogo-sub');
  const charla = el('pres-charla');
  const errorEl = el('pres-error');
  const btnVolver = /** @type {HTMLButtonElement} */ (el('volver-panel'));
  const btnTerminar = /** @type {HTMLButtonElement} */ (el('pres-terminar'));
  const btnNueva = /** @type {HTMLButtonElement} */ (el('pres-nueva'));
  const btnVolverVivo = /** @type {HTMLButtonElement} */ (el('pres-volver-vivo'));

  const ROLES = /** @type {const} */ (['otra', 'protegida']);
  const UMBRAL_VOZ = 0.003;
  const FACTORES_ONDA = [0.55, 0.85, 1.0, 0.8, 0.6];

  const avisoProtegida = /** @type {HTMLElement|null} */ (seccion.querySelector('#pres-aviso-protegida'));
  const avisoTiempo = /** @type {HTMLElement|null} */ (seccion.querySelector('#pres-aviso-tiempo'));
  const avisoMotivo = /** @type {HTMLElement|null} */ (seccion.querySelector('#pres-aviso-motivo'));
  const avisoCita = /** @type {HTMLElement|null} */ (seccion.querySelector('#pres-aviso-cita'));
  const avisoBtnSonido = /** @type {HTMLButtonElement|null} */ (seccion.querySelector('#pres-aviso-btn-sonido'));
  const avisoBtnCerrar = /** @type {HTMLButtonElement|null} */ (seccion.querySelector('#pres-aviso-btn-cerrar'));

  let detectorActual = null;
  let tiempoAviso = null;
  let avisoCerrado = false;
  let sonidoActivo = acciones.obtenerSonido?.() ?? true;

  /** @type {Map<number, {linea: HTMLElement, n: number, rol: 'otra'|'protegida', evaluado: boolean, texto: string}>} */
  const segmentosInfo = new Map();
  /** @type {number[]} */
  const ordenSegmentos = [];

  function actualizarBotonSonido() {
    if (!avisoBtnSonido) return;
    const txt = sonidoActivo ? 'Sonido: sí' : 'Sonido: no';
    avisoBtnSonido.textContent = txt;
    avisoBtnSonido.setAttribute('aria-pressed', String(sonidoActivo));
    avisoBtnSonido.classList.toggle('silenciado', !sonidoActivo);
  }
  actualizarBotonSonido();

  if (avisoBtnSonido) {
    avisoBtnSonido.onclick = () => {
      sonidoActivo = !sonidoActivo;
      actualizarBotonSonido();
      acciones.fijarSonido?.(sonidoActivo);
    };
  }

  if (avisoBtnCerrar) {
    avisoBtnCerrar.onclick = () => {
      avisoCerrado = true;
      if (avisoProtegida) avisoProtegida.hidden = true;
      acciones.detenerTono?.();
      acciones.cerrarAviso?.();
    };
  }

  /** @param {string} texto @returns {string} */
  function escapar(texto) {
    return String(texto ?? '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  /** @param {number|null|undefined} riesgo @returns {string} */
  function obtenerTextoPuntuacion(riesgo) {
    if (riesgo == null || !Number.isFinite(riesgo)) {
      return 'No entregada por el detector';
    }
    const pct = Math.round(riesgo * 100);
    return `${pct}% (salida directa del detector · puntuación no calibrada)`;
  }

  /** @param {any} det @returns {string} */
  function obtenerNombreDetector(det) {
    if (!det) return 'Detector local';
    if (det.tipo === 'slm') {
      return `SLM (${det.modelo || 'local'})`;
    }
    if (det.tipo === 'reglas') {
      return 'Reglas';
    }
    return det.tipo || 'Detector local';
  }

  /**
   * Resalta la evidencia culpable en la frase evaluada si existe y se localiza en su texto.
   * Si falta la evidencia o no se encuentra en el texto de la frase, no inventa ni atribuye nada.
   * @param {HTMLElement} linea
   * @param {string} evidencia
   * @param {string} textoOriginal
   * @returns {boolean} True si la cita se localizó y resaltó en la frase.
   */
  function resaltarEvidenciaEnFrase(linea, evidencia, textoOriginal) {
    const citaLimpia = (evidencia || '').replace(/^[.\s,;:]+/, '').trim();
    if (!citaLimpia) return false;
    const textoEl = /** @type {HTMLElement|null} */ (linea.querySelector('.texto'));
    if (!textoEl) return false;
    const texto = textoOriginal || textoEl.textContent || '';
    const idx = texto.toLowerCase().indexOf(citaLimpia.toLowerCase());
    if (idx < 0) return false;
    const antes = texto.slice(0, idx);
    const medio = texto.slice(idx, idx + citaLimpia.length);
    const despues = texto.slice(idx + citaLimpia.length);
    textoEl.innerHTML = `${escapar(antes)}<mark class="pres-cita-culpable">${escapar(medio)}</mark>${escapar(despues)}`;
    linea.classList.add('pres-disparo-aviso');
    return true;
  }

  /**
   * @param {HTMLElement} linea
   * @param {{estado: 'analizando'|'sin-aviso'|'posible-estafa'|'no-evaluado'|'error', badge: string, motivo?: string, m?: any, detector?: any}} config
   */
  function actualizarEvalCaja(linea, { estado, badge, motivo = '', m = null, detector = null }) {
    let caja = /** @type {HTMLElement|null} */ (linea.querySelector('.pres-eval-caja'));
    if (!caja) {
      caja = document.createElement('div');
      linea.appendChild(caja);
    }
    caja.className = `pres-eval-caja estado-${estado}`;
    caja.dataset.estado = estado;

    const detInfo = detector || detectorActual;
    const detectorNombre = obtenerNombreDetector(detInfo);
    const demoraTxt = (m && m.ms_detector != null) ? `${m.ms_detector.toFixed(0)} ms` : '—';
    const puntuacionTxt = obtenerTextoPuntuacion(m?.riesgo);

    const motivoHtml = motivo ? `<span class="pres-eval-motivo">${escapar(motivo)}</span>` : '';
    let badgeHtml = '';
    if (estado === 'analizando') {
      badgeHtml = `<span class="pres-eval-badge analizando"><span class="pres-eval-punto" aria-hidden="true"></span>${escapar(badge)}</span>`;
    } else if (estado === 'sin-aviso') {
      badgeHtml = `<span class="pres-eval-badge sin-aviso">${escapar(badge)}</span>`;
    } else if (estado === 'posible-estafa') {
      badgeHtml = `<span class="pres-eval-badge posible-estafa">${escapar(badge)}</span>`;
    } else if (estado === 'no-evaluado') {
      badgeHtml = `<span class="pres-eval-badge no-evaluado">${escapar(badge)}</span>`;
    } else if (estado === 'error') {
      badgeHtml = `<span class="pres-eval-badge error">${escapar(badge)}</span>`;
    }

    let detallesHtml = '';
    if (estado === 'sin-aviso' || estado === 'posible-estafa' || estado === 'error') {
      detallesHtml = `
        <details class="pres-detalles">
          <summary class="pres-detalles-summary">Detalles técnicos</summary>
          <div class="pres-detalles-contenido">
            <div class="pres-det-fila">
              <span class="pres-det-etiqueta">Detector:</span>
              <span class="pres-det-valor">${escapar(detectorNombre)}</span>
            </div>
            <div class="pres-det-fila">
              <span class="pres-det-etiqueta">Demora de cómputo:</span>
              <span class="pres-det-valor">${escapar(demoraTxt)}</span>
            </div>
            <div class="pres-det-fila">
              <span class="pres-det-etiqueta">Puntuación del detector:</span>
              <span class="pres-det-valor">${escapar(puntuacionTxt)}</span>
            </div>
            ${m?.error ? `
            <div class="pres-det-fila">
              <span class="pres-det-etiqueta">Diagnóstico:</span>
              <span class="pres-det-valor">${escapar(m.error)}</span>
            </div>` : ''}
            ${m?.saltadas ? `
            <div class="pres-det-fila">
              <span class="pres-det-etiqueta">Frases salteadas:</span>
              <span class="pres-det-valor">${m.saltadas}</span>
            </div>` : ''}
          </div>
        </details>
      `;
    }

    caja.innerHTML = `
      <div class="pres-eval-fila">
        ${badgeHtml}
        ${motivoHtml}
      </div>
      ${detallesHtml}
    `;
  }

  const telefonos = Object.fromEntries(ROLES.map(rol => {
    const ondas = /** @type {HTMLElement[]} */ ([...el(`pres-ondas-${rol}`).querySelectorAll('.pres-onda-barra')]);
    return [rol, {
      articulo: el(`pres-telefono-${rol}`),
      nombre: el(`pres-nombre-${rol}`),
      vozBadge: el(`pres-voz-${rol}`),
      vozTxt: el(`pres-voz-txt-${rol}`),
      meter: /** @type {HTMLMeterElement} */ (el(`pres-nivel-${rol}`)),
      rms: el(`pres-rms-${rol}`),
      ondas
    }];
  }));

  /** @type {Map<number, HTMLElement>} */
  const frases = new Map();
  /** @type {Record<'otra'|'protegida', boolean>} */
  const enParcial = {otra: false, protegida: false};
  let abierta = false;
  let enCurso = false;
  let finalizada = false;
  let llamadaActual = '';
  let siguiendoVivo = true;
  let desplazandoAutomatico = false;

  let ultimoScrollTop = 0;

  /** @returns {boolean} */
  function movimientoReducido() {
    return Boolean(window.matchMedia?.('(prefers-reduced-motion: reduce)')?.matches);
  }

  let timerDesplazamiento = null;

  function irAlFinal(suave = true) {
    if (!abierta) return;
    desplazandoAutomatico = true;
    if (timerDesplazamiento) clearTimeout(timerDesplazamiento);
    const reducido = movimientoReducido();
    const behavior = (!suave || reducido) ? 'instant' : 'smooth';
    charla.scrollTo({top: charla.scrollHeight, behavior});
    timerDesplazamiento = setTimeout(() => {
      desplazandoAutomatico = false;
      ultimoScrollTop = charla.scrollTop;
    }, 150);
  }

  function pausarSeguimiento() {
    if (!siguiendoVivo) return;
    siguiendoVivo = false;
    btnVolverVivo.hidden = false;
  }

  function reanudarSeguimiento() {
    siguiendoVivo = true;
    btnVolverVivo.hidden = true;
    irAlFinal(true);
  }

  btnVolverVivo.onclick = () => {
    reanudarSeguimiento();
  };

  charla.addEventListener('scroll', () => {
    const st = charla.scrollTop;
    const distAlFondo = charla.scrollHeight - st - charla.clientHeight;
    if (distAlFondo <= 15) {
      if (!siguiendoVivo) {
        siguiendoVivo = true;
        btnVolverVivo.hidden = true;
      }
    } else if (distAlFondo > 35 && st < ultimoScrollTop - 2) {
      desplazandoAutomatico = false;
      if (timerDesplazamiento) clearTimeout(timerDesplazamiento);
      if (siguiendoVivo) {
        pausarSeguimiento();
      }
    }
    ultimoScrollTop = st;
  }, {passive: true});

  /**
   * Inserta la línea en el diálogo conservando el orden cronológico por número de segmento.
   * @param {HTMLElement} linea
   * @param {number} segmento
   */
  function insertarEnOrden(linea, segmento) {
    const hijos = /** @type {HTMLElement[]} */ ([...charla.children]);
    for (const hijo of hijos) {
      const seg = Number(hijo.dataset.segmento);
      if (Number.isFinite(seg) && seg > segmento) {
        hijo.before(linea);
        return;
      }
    }
    charla.appendChild(linea);
  }

  /**
   * @param {'otra'|'protegida'} rol
   * @param {number} rms
   * @param {'hablando'|'silencio'|'finalizado'} estado
   */
  function fijarTelefono(rol, rms, estado) {
    const t = telefonos[rol];
    const valor = Math.max(0, Math.min(1, Number.isFinite(rms) ? rms : 0));
    t.meter.value = valor;
    t.rms.textContent = `RMS ${valor.toFixed(3)}`;
    t.nombre.textContent = NOMBRE[rol];
    const activo = estado === 'hablando';
    t.articulo.classList.toggle('hablando-activo', activo);
    t.articulo.dataset.actividad = estado;
    t.vozBadge.dataset.voz = estado;
    t.vozTxt.textContent = estado === 'hablando'
      ? 'Hablando ahora'
      : estado === 'finalizado'
        ? 'Análisis finalizado'
        : 'En silencio';
    const norm = valor <= 0 ? 0 : Math.min(1, Math.max(0, (20 * Math.log10(valor) + 55) / 50));
    const reducido = movimientoReducido();
    for (let i = 0; i < t.ondas.length; i++) {
      const escala = (!activo || reducido) ? 0.22 : Math.max(0.28, Math.min(1, norm * FACTORES_ONDA[i]));
      t.ondas[i].style.transform = reducido ? 'none' : `scaleY(${escala.toFixed(2)})`;
    }
  }

  function limpiarNiveles() {
    enParcial.otra = false;
    enParcial.protegida = false;
    const estado = finalizada ? 'finalizado' : 'silencio';
    fijarTelefono('otra', 0, estado);
    fijarTelefono('protegida', 0, estado);
  }

  function abrir() {
    if (document.body.classList.contains('protegida')) return;
    const focoEnControles = Boolean(document.activeElement && document.getElementById('controles')?.contains(document.activeElement));
    abierta = true;
    seccion.hidden = false;
    document.body.classList.add('presentacion');
    acciones.cambiar();
    if (siguiendoVivo) irAlFinal(false);
    if (focoEnControles) btnVolver.focus();
  }

  function cerrar() {
    if (!abierta && seccion.hidden) return;
    abierta = false;
    seccion.hidden = true;
    document.body.classList.remove('presentacion');
    acciones.cambiar();
  }

  /** @param {string} [id] */
  function reiniciar(id = '') {
    frases.clear();
    segmentosInfo.clear();
    ordenSegmentos.length = 0;
    tiempoAviso = null;
    avisoCerrado = Boolean(acciones.obtenerAvisoCerrado?.());
    charla.replaceChildren();
    siguiendoVivo = true;
    desplazandoAutomatico = false;
    ultimoScrollTop = 0;
    btnVolverVivo.hidden = true;
    charla.scrollTop = 0;
    llamadaActual = id;
    llamadaIdEl.textContent = id;
    errorEl.textContent = '';
    errorEl.hidden = true;
    if (avisoProtegida) {
      avisoProtegida.hidden = true;
      if (avisoMotivo) avisoMotivo.textContent = '';
      if (avisoCita) {
        avisoCita.textContent = '';
        avisoCita.hidden = true;
      }
      if (avisoTiempo) avisoTiempo.textContent = '';
    }
    actualizarBotonSonido();
    if (!id) {
      enCurso = false;
      finalizada = false;
      estadoPill.dataset.estado = 'esperando';
      estadoTxt.textContent = 'Esperando inicio';
      dialogoSub.textContent = 'Frases finales por canal';
      limpiarNiveles();
      cerrar();
      return;
    }
    finalizada = false;
    limpiarNiveles();
  }

  btnVolver.onclick = () => {
    cerrar();
    acciones.alVolverAlPanel?.();
  };
  btnTerminar.onclick = () => acciones.terminar();
  btnNueva.onclick = () => acciones.nueva();

  return {
    get abierta() { return abierta; },
    get tieneLlamada() { return enCurso || finalizada; },
    get llamadaId() { return llamadaActual; },
    abrir,
    cerrar,
    reiniciar,
    /** @param {string} mensaje */
    error(mensaje) {
      errorEl.textContent = mensaje;
      errorEl.hidden = !mensaje;
    },
    /** @param {boolean} conectada @param {boolean} ocupada @param {boolean} enLlamada @param {boolean} terminada */
    controles(conectada, ocupada, enLlamada, terminada) {
      const activa = enCurso && enLlamada;
      const cerrada = finalizada && terminada && !enLlamada;
      btnTerminar.disabled = !conectada || !activa || ocupada;
      btnNueva.hidden = !cerrada;
      btnNueva.disabled = !conectada || ocupada || !cerrada;
      if (ocupada && activa) {
        estadoTxt.textContent = 'Terminando análisis…';
      } else if (cerrada) {
        estadoPill.dataset.estado = 'finalizado';
        estadoTxt.textContent = 'Análisis finalizado';
      } else if (activa && conectada) {
        estadoPill.dataset.estado = 'en-llamada';
        estadoTxt.textContent = 'En llamada';
      }
    },
    /** @param {any} m */
    evento(m) {
      if (m.tipo === 'inicio') {
        if (m.modo === 'asr') {
          reiniciar('');
          return;
        }
        const esMismaLlamada = Boolean(m.llamada_id && m.llamada_id === llamadaActual);
        const estabaAbierta = abierta;
        reiniciar(m.llamada_id || '');
        if (m.detector) detectorActual = m.detector;
        enCurso = true;
        finalizada = false;
        estadoPill.dataset.estado = 'en-llamada';
        estadoTxt.textContent = 'En llamada';
        dialogoSub.textContent = 'Frases finales por canal';
        if (!esMismaLlamada) {
          abrir();
        } else if (estabaAbierta) {
          abrir();
        }
        return;
      }
      if (m.tipo === 'error') {
        errorEl.textContent = m.mensaje || '';
        errorEl.hidden = !m.mensaje;
        return;
      }
      if (!enCurso && !finalizada) return;
      if (m.tipo === 'niveles' && enCurso) {
        for (const rol of ROLES) {
          const canal = m.canales?.[rol];
          const rms = canal?.rms ?? 0;
          const umbral = canal?.umbral_rms_silencio ?? UMBRAL_VOZ;
          fijarTelefono(rol, rms, rms >= umbral ? 'hablando' : 'silencio');
        }
        return;
      }
      if (m.tipo === 'asr') {
        const rol = m.rol === 'otra' ? 'otra' : 'protegida';
        const tiempo = typeof m.fin_audio_s === 'number' ? `${m.fin_audio_s.toFixed(1)} s` : '';

        if (m.entrega === 'parcial') {
          enParcial[rol] = true;
          fijarTelefono(rol, telefonos[rol].meter.value, 'hablando');

          let linea = frases.get(m.segmento);
          if (!linea) {
            linea = crearLinea(rol, 'parcial', m.texto, 'Texto provisorio');
            linea.id = `pres-seg-${m.segmento}`;
            linea.dataset.rol = rol;
            linea.dataset.segmento = String(m.segmento);
            linea.dataset.entrega = 'parcial';
            const t = linea.querySelector('.t');
            if (t) t.innerHTML = '<span class="pres-provisorio-tag">Texto provisorio</span>';
            insertarEnOrden(linea, m.segmento);
            frases.set(m.segmento, linea);
          } else {
            linea.className = `linea ${rol} parcial`;
            linea.dataset.rol = rol;
            linea.dataset.entrega = 'parcial';
            const quien = /** @type {HTMLElement|null} */ (linea.querySelector('.nombre-quien'));
            if (quien) quien.textContent = NOMBRE[rol];
            const txt = /** @type {HTMLElement|null} */ (linea.querySelector('.texto'));
            if (txt) txt.textContent = m.texto;
            const t = /** @type {HTMLElement|null} */ (linea.querySelector('.t'));
            if (t) t.innerHTML = '<span class="pres-provisorio-tag">Texto provisorio</span>';
            if (!linea.isConnected) insertarEnOrden(linea, m.segmento);
          }
          if (siguiendoVivo) irAlFinal();
          return;
        }

        if (m.entrega === 'final') {
          enParcial[rol] = false;
          if (telefonos[rol].meter.value < UMBRAL_VOZ) {
            fijarTelefono(rol, telefonos[rol].meter.value, finalizada ? 'finalizado' : 'silencio');
          }
          let linea = frases.get(m.segmento);
          if (!linea) {
            linea = crearLinea(rol, 'final', m.texto, tiempo);
            linea.id = `pres-seg-${m.segmento}`;
            linea.dataset.rol = rol;
            linea.dataset.segmento = String(m.segmento);
            linea.dataset.entrega = 'final';
            insertarEnOrden(linea, m.segmento);
            frases.set(m.segmento, linea);
          } else {
            linea.className = `linea ${rol} final`;
            linea.dataset.rol = rol;
            linea.dataset.entrega = 'final';
            const quien = /** @type {HTMLElement|null} */ (linea.querySelector('.nombre-quien'));
            if (quien) quien.textContent = NOMBRE[rol];
            const txt = /** @type {HTMLElement|null} */ (linea.querySelector('.texto'));
            if (txt) txt.textContent = m.texto;
            const t = /** @type {HTMLElement|null} */ (linea.querySelector('.t'));
            if (t) t.textContent = tiempo;
            if (!linea.isConnected) insertarEnOrden(linea, m.segmento);
          }

          const info = segmentosInfo.get(m.segmento) || {
            linea,
            n: m.n,
            rol,
            evaluado: false,
            texto: m.texto
          };
          info.linea = linea;
          info.n = m.n;
          info.rol = rol;
          info.texto = m.texto;
          segmentosInfo.set(m.segmento, info);
          if (!ordenSegmentos.includes(m.segmento)) {
            ordenSegmentos.push(m.segmento);
          }

          if (tiempoAviso !== null) {
            info.evaluado = true;
            actualizarEvalCaja(linea, {
              estado: 'no-evaluado',
              badge: 'No evaluado',
              motivo: 'Detector detenido tras el primer aviso',
              m: null
            });
          } else if (!info.evaluado) {
            actualizarEvalCaja(linea, {
              estado: 'analizando',
              badge: 'Analizando',
              motivo: '',
              m: null
            });
          }

          if (siguiendoVivo) irAlFinal();
          return;
        }
        return;
      }
      if (m.tipo === 'detector') {
        let segId = null;
        for (const s of ordenSegmentos) {
          const inf = segmentosInfo.get(s);
          if (inf && inf.n <= m.n && !inf.evaluado) {
            segId = s;
          }
        }
        if (segId === null) {
          for (const s of ordenSegmentos) {
            const inf = segmentosInfo.get(s);
            if (inf && !inf.evaluado) {
              segId = s;
              break;
            }
          }
        }

        if (segId !== null && m.saltadas > 0) {
          const idx = ordenSegmentos.indexOf(segId);
          let restan = m.saltadas;
          for (let i = idx - 1; i >= 0 && restan > 0; i--) {
            const prevId = ordenSegmentos[i];
            const prevInf = segmentosInfo.get(prevId);
            if (prevInf && !prevInf.evaluado) {
              prevInf.evaluado = true;
              actualizarEvalCaja(prevInf.linea, {
                estado: 'no-evaluado',
                badge: 'No evaluado',
                motivo: 'Salteada por demora del detector',
                m: null
              });
              restan--;
            }
          }
        }

        const inf = segId !== null ? segmentosInfo.get(segId) : null;
        if (inf) {
          inf.evaluado = true;
          if (!m.valida) {
            actualizarEvalCaja(inf.linea, {
              estado: 'error',
              badge: 'Error',
              motivo: m.error || 'Fallo del detector',
              m
            });
          } else if (m.aviso || m.alerta_sugerida) {
            actualizarEvalCaja(inf.linea, {
              estado: 'posible-estafa',
              badge: 'Posible estafa',
              motivo: m.motivo || 'Alerta de estafa',
              m
            });
          } else {
            actualizarEvalCaja(inf.linea, {
              estado: 'sin-aviso',
              badge: 'Sin aviso',
              motivo: m.motivo || 'Sin señales de riesgo',
              m
            });
          }
        }

        if (m.aviso) {
          tiempoAviso = m.t_a;
          if (avisoProtegida) {
            if (!avisoCerrado) {
              avisoProtegida.hidden = false;
            }
            if (avisoMotivo) {
              avisoMotivo.textContent = m.motivo || 'Posible estafa detectada';
            }
            if (avisoTiempo) {
              avisoTiempo.textContent = typeof m.t_a === 'number' ? `a los ${m.t_a.toFixed(1)} s` : '';
            }
            const citaLimpia = (m.evidencia || '').replace(/^[.\s,;:]+/, '').trim();
            let resaltada = false;
            if (citaLimpia && inf) {
              resaltada = resaltarEvidenciaEnFrase(inf.linea, citaLimpia, inf.texto);
            }
            if (avisoCita) {
              if (resaltada && citaLimpia) {
                avisoCita.hidden = false;
                avisoCita.textContent = `«${citaLimpia}»`;
              } else {
                avisoCita.hidden = true;
                avisoCita.textContent = '';
              }
            }
          }

          for (const s of ordenSegmentos) {
            const otroInf = segmentosInfo.get(s);
            if (otroInf && !otroInf.evaluado) {
              otroInf.evaluado = true;
              actualizarEvalCaja(otroInf.linea, {
                estado: 'no-evaluado',
                badge: 'No evaluado',
                motivo: 'Detector detenido tras el primer aviso',
                m: null
              });
            }
          }
        }

        if (siguiendoVivo) irAlFinal();
        return;
      }
      if (m.tipo === 'fin') {
        enCurso = false;
        finalizada = true;
        limpiarNiveles();
        estadoPill.dataset.estado = 'finalizado';
        estadoTxt.textContent = 'Análisis finalizado';
        dialogoSub.textContent = 'Análisis finalizado · escena conservada';
        // Si quedó algún borrador o parcial sin confirmación final al cerrar la llamada, se limpia de la charla
        for (const [segId, linea] of frases.entries()) {
          if (linea.dataset.entrega === 'parcial') {
            linea.remove();
            frases.delete(segId);
          }
        }
        for (const s of ordenSegmentos) {
          const inf = segmentosInfo.get(s);
          if (inf && !inf.evaluado) {
            inf.evaluado = true;
            actualizarEvalCaja(inf.linea, {
              estado: 'no-evaluado',
              badge: 'No evaluado',
              motivo: 'Llamada finalizada antes de la evaluación',
              m: null
            });
          }
        }
        return;
      }
      if (m.tipo === 'desconexion') {
        limpiarNiveles();
        if (enCurso || (!enCurso && !finalizada)) {
          estadoPill.dataset.estado = 'sin-conexion';
          estadoTxt.textContent = 'Sin conexión, reintentando…';
        }
      }
    },
    cerrarAviso() {
      avisoCerrado = true;
      if (avisoProtegida) avisoProtegida.hidden = true;
    },
    actualizarSonido(activo) {
      sonidoActivo = activo;
      actualizarBotonSonido();
    },
    fijarDetector(info) {
      detectorActual = info;
    }
  };
}
