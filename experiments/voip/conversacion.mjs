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
  #presentacion {
    display: none;
    flex: 1;
    max-width: 1920px;
    width: 100%;
    margin: 0 auto;
    padding: 0.75rem 1.25rem 1rem;
    box-sizing: border-box;
  }
  body.presentacion {
    height: 100vh;
    overflow: hidden;
  }
  body.presentacion #presentacion {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    flex: 1;
    min-height: 0;
    height: calc(100vh - 65px);
    max-height: calc(100vh - 65px);
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
  #presentacion .pres-barra {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: center;
    gap: 0.75rem 1rem;
    padding: 0.6rem 1rem;
    background: var(--superficie, #ffffff);
    border: 1px solid var(--linea, #cbd5e1);
    border-radius: var(--radio-lg, 12px);
  }
  #presentacion .pres-barra-izq {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0.65rem 0.9rem;
    min-width: 0;
  }
  #presentacion .pres-titulo {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--tinta, #0f172a);
  }
  #presentacion .pres-estado-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    padding: 0.25rem 0.65rem;
    border-radius: var(--radio-sm, 4px);
    background: var(--otra-fondo, #f1f5f9);
    border: 1px solid var(--linea, #cbd5e1);
    font-size: 0.875rem;
    font-weight: 700;
    color: var(--tinta, #0f172a);
  }
  #presentacion .pres-estado-pill .punto {
    width: 8px;
    height: 8px;
    border-radius: var(--radio-sm, 4px);
    background: var(--tinta-secundaria, #334155);
  }
  #presentacion .pres-estado-pill[data-estado="en-llamada"] {
    background: var(--ok-fondo, #f0fdf4);
    border-color: var(--ok, #15803d);
    color: var(--ok, #15803d);
  }
  #presentacion .pres-estado-pill[data-estado="en-llamada"] .punto {
    background: var(--ok, #15803d);
  }
  #presentacion .pres-estado-pill[data-estado="finalizado"] {
    background: var(--vos-fondo, #eff6ff);
    border-color: var(--primary, #1d4ed8);
    color: var(--primary-dark, #1e40af);
  }
  #presentacion .pres-estado-pill[data-estado="finalizado"] .punto {
    background: var(--primary, #1d4ed8);
  }
  #presentacion .pres-estado-pill[data-estado="sin-conexion"] {
    background: var(--alerta-fondo, #fef2f2);
    border-color: var(--alerta-borde, #f87171);
    color: var(--alerta-tinta, #7f1d1d);
  }
  #presentacion .pres-estado-pill[data-estado="sin-conexion"] .punto {
    background: var(--alerta, #b91c1c);
  }
  #presentacion .pres-id {
    font-size: 0.8125rem;
    font-weight: 600;
    color: var(--tinta-secundaria, #334155);
    font-variant-numeric: tabular-nums;
  }
  #presentacion .pres-acciones {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0.5rem;
  }
  #presentacion .pres-btn-secundario {
    background: var(--superficie, #ffffff);
    color: var(--tinta, #0f172a);
    border: 1px solid var(--linea, #cbd5e1);
    border-radius: var(--radio-sm, 4px);
    padding: 0.45rem 0.85rem;
    font-size: 0.875rem;
    font-weight: 700;
    cursor: pointer;
  }
  #presentacion .pres-btn-secundario:hover:not(:disabled) {
    background: var(--otra-fondo, #f1f5f9);
  }
  #presentacion .pres-btn-primario {
    background: var(--primary, #1d4ed8);
    color: var(--superficie, #ffffff);
    border: 1px solid var(--primary, #1d4ed8);
    border-radius: var(--radio-sm, 4px);
    padding: 0.45rem 0.9rem;
    font-size: 0.875rem;
    font-weight: 700;
    cursor: pointer;
  }
  #presentacion .pres-btn-primario:hover:not(:disabled) {
    background: var(--primary-dark, #1e40af);
  }
  #presentacion .pres-btn-terminar {
    background: var(--alerta-fondo, #fef2f2);
    color: var(--alerta-tinta, #7f1d1d);
    border: 1px solid var(--alerta-borde, #f87171);
    border-radius: var(--radio-sm, 4px);
    padding: 0.45rem 0.9rem;
    font-size: 0.875rem;
    font-weight: 700;
    cursor: pointer;
  }
  #presentacion .pres-btn-terminar:hover:not(:disabled) {
    background: var(--alerta-claro, #fee2e2);
  }
  #presentacion button:focus-visible {
    outline: 2px solid var(--primary, #1d4ed8);
    outline-offset: 2px;
  }
  #presentacion button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  #presentacion .pres-error {
    flex-basis: 100%;
    margin: 0;
    padding: 0.45rem 0.75rem;
    border-radius: var(--radio-sm, 4px);
    background: var(--alerta-fondo, #fef2f2);
    border: 1px solid var(--alerta-borde, #f87171);
    color: var(--alerta-tinta, #7f1d1d);
    font-size: 0.875rem;
    font-weight: 700;
  }
  #presentacion .pres-escena {
    display: grid;
    grid-template-columns: 276px minmax(0, 1fr) 276px;
    gap: 1.15rem;
    align-items: stretch;
    flex: 1;
    min-height: 0;
  }
  /* Silueta de iPhone con pantalla oscura estilo llamada de WhatsApp */
  #presentacion .pres-telefono {
    display: flex;
    flex-direction: column;
    align-items: center;
    align-self: start;
  }
  #presentacion .pres-iphone-marco {
    position: relative;
    width: 100%;
    max-width: 276px;
    background: var(--tinta, #0f172a);
    border: 3px solid var(--tinta-secundaria, #334155);
    border-radius: 32px;
    padding: 10px;
    box-shadow: 0 14px 28px -12px rgb(15 23 42 / 0.35);
  }
  #presentacion .pres-telefono.protegida .pres-iphone-marco {
    border-color: var(--primary, #1d4ed8);
  }
  #presentacion .pres-telefono.hablando-activo .pres-iphone-marco {
    border-color: var(--ok, #15803d);
  }
  #presentacion .pres-iphone-pantalla {
    background: var(--tinta, #0f172a);
    color: var(--superficie, #ffffff);
    border: 1px solid var(--tinta-secundaria, #334155);
    border-radius: 24px;
    padding: 0.75rem 0.9rem 0.65rem;
    min-height: 470px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    align-items: center;
    text-align: center;
    gap: 0.65rem;
  }
  #presentacion .pres-isla {
    width: 84px;
    height: 20px;
    background: #000000;
    border: 1px solid var(--tinta-secundaria, #334155);
    border-radius: 999px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 8px;
  }
  #presentacion .pres-isla-camara {
    width: 7px;
    height: 7px;
    border-radius: var(--radio-sm, 4px);
    background: var(--tinta-secundaria, #334155);
  }
  #presentacion .pres-isla-onda {
    width: 7px;
    height: 7px;
    border-radius: var(--radio-sm, 4px);
    background: var(--tinta-secundaria, #334155);
    transition: transform 160ms var(--salida), background-color 160ms var(--salida);
  }
  #presentacion .pres-telefono.hablando-activo .pres-isla-onda {
    background: var(--ok, #15803d);
    transform: scale(1.3);
  }
  #presentacion .pres-pantalla-cabecera {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.35rem;
    width: 100%;
    background: transparent;
    border: 0;
    padding: 0;
  }
  #presentacion .pres-rol-nombre {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--superficie, #ffffff);
  }
  #presentacion .pres-estado-voz {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.2rem 0.65rem;
    border-radius: var(--radio-sm, 4px);
    background: var(--tinta-secundaria, #334155);
    border: 1px solid var(--linea, #cbd5e1);
    color: var(--superficie, #ffffff);
    font-size: 0.8125rem;
    font-weight: 700;
  }
  #presentacion .pres-estado-voz[data-voz="hablando"] {
    background: var(--ok, #15803d);
    border-color: var(--ok-fondo, #f0fdf4);
    color: var(--superficie, #ffffff);
  }
  #presentacion .pres-estado-voz[data-voz="finalizado"] {
    background: var(--primary-dark, #1e40af);
    border-color: var(--vos-borde, #93c5fd);
    color: var(--superficie, #ffffff);
  }
  #presentacion .pres-voz-punto {
    width: 8px;
    height: 8px;
    border-radius: var(--radio-sm, 4px);
    background: var(--linea, #cbd5e1);
  }
  #presentacion .pres-estado-voz[data-voz="hablando"] .pres-voz-punto {
    background: var(--superficie, #ffffff);
  }
  #presentacion .pres-perfil-area {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0.35rem 0;
  }
  #presentacion .pres-avatar-anillo {
    padding: 6px;
    border-radius: 50%;
    border: 3px solid var(--tinta-secundaria, #334155);
    transition: transform 160ms var(--salida), border-color 160ms var(--salida);
  }
  #presentacion .pres-telefono.protegida .pres-avatar-anillo {
    border-color: var(--vos-borde, #93c5fd);
  }
  #presentacion .pres-telefono.hablando-activo .pres-avatar-anillo {
    border-color: var(--ok, #15803d);
    transform: scale(1.05);
  }
  #presentacion .pres-avatar-circulo {
    width: 112px;
    height: 112px;
    border-radius: 50%;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--tinta-secundaria, #334155);
    border: 2px solid var(--superficie, #ffffff);
  }
  #presentacion .pres-actividad-caja {
    width: 100%;
    background: var(--tinta-secundaria, #334155);
    border: 1px solid var(--linea, #cbd5e1);
    border-radius: var(--radio-md, 8px);
    padding: 0.55rem 0.65rem;
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
  }
  #presentacion .pres-ondas {
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
  }
  #presentacion .pres-onda-barra {
    width: 6px;
    height: 22px;
    border-radius: var(--radio-sm, 4px);
    background: var(--linea, #cbd5e1);
    transform: scaleY(0.22);
    transform-origin: center;
    transition: transform 100ms var(--salida), background-color 120ms var(--salida);
  }
  #presentacion .pres-telefono.hablando-activo .pres-onda-barra {
    background: var(--ok-fondo, #f0fdf4);
  }
  #presentacion .pres-meter-fila {
    display: grid;
    grid-template-columns: auto 1fr auto;
    align-items: center;
    gap: 0.45rem;
  }
  #presentacion .pres-canal-tag {
    font-size: 0.75rem;
    font-weight: 700;
    color: var(--superficie, #ffffff);
    text-transform: uppercase;
  }
  #presentacion .pres-meter-fila meter {
    width: 100%;
    height: 0.85rem;
  }
  #presentacion .pres-rms {
    font-size: 0.75rem;
    font-weight: 700;
    color: var(--superficie, #ffffff);
    font-variant-numeric: tabular-nums;
    min-width: 4.8rem;
    text-align: right;
  }
  #presentacion .pres-controles-decorativos {
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.55rem;
    padding-top: 0.2rem;
  }
  #presentacion .pres-iconos-fila {
    display: flex;
    justify-content: center;
    gap: 0.85rem;
  }
  #presentacion .pres-icono-deco {
    width: 34px;
    height: 34px;
    border-radius: 50%;
    background: var(--tinta-secundaria, #334155);
    border: 1px solid var(--linea, #cbd5e1);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    color: var(--superficie, #ffffff);
  }
  #presentacion .pres-icono-deco svg {
    width: 15px;
    height: 15px;
  }
  #presentacion .pres-home-bar {
    width: 88px;
    height: 4px;
    border-radius: var(--radio-sm, 4px);
    background: var(--linea, #cbd5e1);
  }
  /* Columna central del diálogo */
  #presentacion .pres-centro {
    background: var(--superficie, #ffffff);
    border: 1px solid var(--linea, #cbd5e1);
    border-radius: var(--radio-lg, 12px);
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
    padding: 0.75rem 1rem;
    border-bottom: 1px solid var(--linea, #cbd5e1);
    flex-shrink: 0;
  }
  #presentacion .pres-centro-titulo {
    margin: 0;
    font-size: 1.125rem;
    font-weight: 700;
    color: var(--tinta, #0f172a);
  }
  #presentacion .pres-centro-sub {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--tinta-secundaria, #334155);
  }
  #presentacion .pres-charla {
    flex: 1;
    min-height: 0;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 0.65rem;
    padding: 1rem 1rem 3rem;
    scroll-behavior: smooth;
  }
  #presentacion .pres-charla::-webkit-scrollbar {
    width: 8px;
  }
  #presentacion .pres-charla::-webkit-scrollbar-track {
    background: transparent;
  }
  #presentacion .pres-charla::-webkit-scrollbar-thumb {
    background: var(--linea, #cbd5e1);
    border-radius: var(--radio-sm, 4px);
  }
  #presentacion .pres-charla::-webkit-scrollbar-thumb:hover {
    background: var(--tinta-secundaria, #334155);
  }
  #presentacion .pres-charla:empty::before {
    content: "Esperando las primeras frases confirmadas de la llamada…";
    color: var(--tinta-secundaria, #334155);
    font-size: 1.0625rem;
    font-weight: 500;
    margin: auto;
    text-align: center;
    max-width: 44ch;
  }
  #presentacion .pres-charla .linea {
    width: 76%;
    max-width: 82%;
    padding: 0.65rem 0.9rem;
    word-break: break-word;
    overflow-wrap: break-word;
  }
  #presentacion .pres-charla .linea.parcial {
    border-style: dashed;
    border-color: var(--linea, #cbd5e1);
  }
  #presentacion .pres-charla .linea.parcial .texto {
    color: var(--tinta-secundaria, #334155);
  }
  #presentacion .pres-charla .pres-provisorio-tag {
    display: inline-block;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--tinta-secundaria, #334155);
    background: var(--otra-fondo, #f1f5f9);
    border: 1px dashed var(--linea, #cbd5e1);
    border-radius: var(--radio-sm, 4px);
    padding: 0.1rem 0.45rem;
  }
  #presentacion .pres-charla .linea .quien {
    font-size: 0.875rem;
  }
  #presentacion .pres-charla .linea .texto {
    font-size: 1.125rem;
    line-height: 1.45;
  }
  #presentacion .pres-btn-volver-vivo {
    position: absolute;
    bottom: 0.85rem;
    left: 50%;
    transform: translateX(-50%);
    z-index: 10;
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.45rem 1.05rem;
    border-radius: 999px;
    background: var(--tinta, #0f172a);
    color: var(--superficie, #ffffff);
    border: 1px solid var(--tinta-secundaria, #334155);
    font-size: 0.875rem;
    font-weight: 700;
    cursor: pointer;
    box-shadow: 0 4px 14px rgb(15 23 42 / 0.28);
    transition: background-color 150ms var(--salida), transform 150ms var(--salida);
  }
  #presentacion .pres-btn-volver-vivo:hover {
    background: var(--primary, #1d4ed8);
    border-color: var(--vos-borde, #93c5fd);
  }
  #presentacion .pres-btn-volver-vivo:focus-visible {
    outline: 2px solid var(--primary, #1d4ed8);
    outline-offset: 2px;
  }
  @media (max-width: 1120px) {
    #presentacion .pres-escena {
      grid-template-columns: 232px minmax(0, 1fr) 232px;
      gap: 0.75rem;
    }
    #presentacion .pres-avatar-circulo {
      width: 96px;
      height: 96px;
    }
    #presentacion .pres-charla .linea {
      width: 88%;
      max-width: 92%;
    }
  }
  @media (max-width: 820px) {
    #presentacion .pres-escena {
      grid-template-columns: 1fr 1fr;
    }
    #presentacion .pres-centro {
      grid-column: 1 / -1;
      order: 2;
    }
    #presentacion .pres-telefono {
      position: static;
    }
  }
  @media (min-width: 1700px) {
    #presentacion .pres-escena {
      grid-template-columns: 310px minmax(0, 1fr) 310px;
      gap: 1.5rem;
    }
    #presentacion .pres-charla .linea .texto {
      font-size: 1.25rem;
    }
  }
  @media (prefers-reduced-motion: reduce) {
    #presentacion .pres-avatar-anillo,
    #presentacion .pres-onda-barra,
    #presentacion .pres-isla-onda {
      transition: none !important;
      transform: none !important;
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
  }
`;

/**
 * Arma la silueta de iPhone para un rol («otra» a la izquierda, «protegida» a la derecha).
 * @param {'otra'|'protegida'} rol
 */
function plantillaTelefono(rol) {
  const esOtra = rol === 'otra';
  const nombre = NOMBRE[rol];
  const canalTxt = esOtra ? 'Canal izq' : 'Canal der';
  const avatar = esOtra ? AVATAR_OTRA_SVG : AVATAR_PROTEGIDA_SVG;
  return `
    <article class="pres-telefono ${rol}" id="pres-telefono-${rol}" data-rol="${rol}" data-actividad="silencio" aria-label="Teléfono de ${nombre}">
      <div class="pres-iphone-marco">
        <div class="pres-iphone-pantalla">
          <div class="pres-isla" aria-hidden="true">
            <span class="pres-isla-camara"></span>
            <span class="pres-isla-onda"></span>
          </div>
          <div class="pres-pantalla-cabecera">
            <h3 class="pres-rol-nombre" id="pres-nombre-${rol}">${nombre}</h3>
            <span class="pres-estado-voz" id="pres-voz-${rol}" data-voz="silencio">
              <span class="pres-voz-punto" aria-hidden="true"></span>
              <span id="pres-voz-txt-${rol}">En silencio</span>
            </span>
          </div>
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
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M15.54 8.46a5 5 0 0 1 0 7.07"></path></svg>
              </span>
              <span class="pres-icono-deco">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="23"></line></svg>
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

  function irAlFinal(suave = true) {
    if (!abierta) return;
    desplazandoAutomatico = true;
    const reducido = movimientoReducido();
    const behavior = (!suave || reducido) ? 'instant' : 'smooth';
    charla.scrollTo({top: charla.scrollHeight, behavior});
    setTimeout(() => {
      desplazandoAutomatico = false;
      ultimoScrollTop = charla.scrollTop;
    }, 320);
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
    } else if (!desplazandoAutomatico && st < ultimoScrollTop - 5 && distAlFondo > 35) {
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
        reiniciar(m.llamada_id || '');
        enCurso = true;
        finalizada = false;
        estadoPill.dataset.estado = 'en-llamada';
        estadoTxt.textContent = 'En llamada';
        dialogoSub.textContent = 'Frases finales por canal';
        abrir();
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
          if (siguiendoVivo) irAlFinal();
          return;
        }
        return;
      }
      if (m.tipo === 'fin') {
        enCurso = false;
        finalizada = true;
        limpiarNiveles();
        estadoPill.dataset.estado = 'finalizado';
        estadoTxt.textContent = 'Análisis finalizado';
        dialogoSub.textContent = 'Análisis finalizado · escena conservada';
        return;
      }
      if (m.tipo === 'desconexion') {
        limpiarNiveles();
        if (enCurso) {
          estadoPill.dataset.estado = 'sin-conexion';
          estadoTxt.textContent = 'Sin conexión, reintentando…';
        }
      }
    }
  };
}
