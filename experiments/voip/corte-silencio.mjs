// @ts-check

const CORTE_INICIAL_S = 0.9;

/**
 * Selector del corte de silencio: un número de 0,1 a 3,0 s (de a 0,1), sin opción automática.
 * Lo comparten la llamada (inicial 0,9 s) y Probar el ASR (0,8 s, medido con voz real en #94).
 * El servidor sigue aceptando `"auto"` (lo usan cliente.py y las llamadas viejas); si llega,
 * el selector muestra su valor inicial.
 * @param {string} id prefijo de los ids, único por instancia
 * @param {number} [inicial] segundos con que arranca
 */
export function crearSelectorCorte(id, inicial = CORTE_INICIAL_S) {
  const grupo = document.createElement('div');
  grupo.className = 'ajuste-grupo corte-silencio';
  grupo.innerHTML = `
    <label for="${id}-valor">Corte de silencio</label>
    <span class="corte-valor">
      <input id="${id}-valor" type="number" min="0.1" max="3" step="0.1" value="${inicial}"
        aria-describedby="${id}-ayuda">
      <span aria-hidden="true">s</span>
    </span>
    <span id="${id}-ayuda" class="ayuda-oculta">Segundos callado que tienen que pasar para que el ASR dé la frase por terminada y se la pase al detector.</span>`;
  const valor = /** @type {HTMLInputElement} */ (grupo.querySelector(`#${id}-valor`));
  let bloqueado = false;
  /** @type {() => void} */
  let alCambiar = () => {};
  valor.oninput = () => alCambiar();
  return {
    elemento: grupo,
    /** @param {() => void} f */
    set alCambiar(f) { alCambiar = f; },
    /** @returns {number} */
    get valor() { return Number(valor.value); },
    /** @param {'auto'|number} v */
    set valor(v) { valor.value = (v === 'auto' ? inicial : v).toFixed(1); },
    /** Segundos que dibuja la barra de silencio. */
    get segundos() { return Number(valor.value); },
    /** @param {boolean} b */
    set deshabilitado(b) { bloqueado = b; valor.disabled = b; },
    get deshabilitado() { return bloqueado; },
    /** Avisa al presentador antes de mandar `iniciar` si el número no es válido. */
    validar() { return valor.reportValidity(); }
  };
}
