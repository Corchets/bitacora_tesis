// @ts-check

/**
 * Selector del corte de silencio: «Automático» o un número de 0,1 a 3,0 s (de a 0,1).
 * Lo comparten la llamada y Probar el ASR; el contrato del servidor es `"auto"` o el número.
 * @param {string} id prefijo de los ids, único por instancia
 */
export function crearSelectorCorte(id) {
  const grupo = document.createElement('div');
  grupo.className = 'ajuste-grupo corte-silencio';
  grupo.innerHTML = `
    <label for="${id}-modo">Corte de silencio</label>
    <select id="${id}-modo">
      <option value="auto" selected>Automático</option>
      <option value="numero">Elegir</option>
    </select>
    <span class="corte-valor" hidden>
      <input id="${id}-valor" type="number" min="0.1" max="3" step="0.1" value="0.8" aria-label="Segundos de silencio para cerrar la frase">
      <span aria-hidden="true">s</span>
    </span>`;
  const modo = /** @type {HTMLSelectElement} */ (grupo.querySelector(`#${id}-modo`));
  const valor = /** @type {HTMLInputElement} */ (grupo.querySelector(`#${id}-valor`));
  const cajaValor = /** @type {HTMLElement} */ (grupo.querySelector('.corte-valor'));
  let bloqueado = false;
  function mostrar() { cajaValor.hidden = modo.value === 'auto'; }
  /** @type {() => void} */
  let alCambiar = () => {};
  modo.onchange = () => { mostrar(); alCambiar(); if (modo.value === 'numero') valor.focus(); };
  valor.oninput = () => alCambiar();
  return {
    elemento: grupo,
    /** @param {() => void} f */
    set alCambiar(f) { alCambiar = f; },
    /** @returns {'auto'|number} */
    get valor() { return modo.value === 'auto' ? 'auto' : Number(valor.value); },
    /** @param {'auto'|number} v */
    set valor(v) {
      modo.value = v === 'auto' ? 'auto' : 'numero';
      if (v !== 'auto') valor.value = v.toFixed(1);
      mostrar();
    },
    /** Segundos efectivos que dibuja la barra de silencio: el corte propio del modelo se muestra como 0,8 s. */
    get segundos() { return modo.value === 'auto' ? 0.8 : Number(valor.value); },
    /** @param {boolean} b */
    set deshabilitado(b) { bloqueado = b; modo.disabled = valor.disabled = b; },
    get deshabilitado() { return bloqueado; },
    /** Avisa al presentador antes de mandar `iniciar` si el número no es válido. */
    validar() { return modo.value === 'auto' || valor.reportValidity(); }
  };
}
