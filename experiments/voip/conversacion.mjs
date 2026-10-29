// @ts-check

/** Nombres de los roles, iguales en la conversación en vivo y en el Historial. */
/** @type {Record<string, string>} */
export const NOMBRE = {protegida: 'Persona protegida', otra: 'Otra persona'};

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
