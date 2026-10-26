// @ts-check

/**
 * UI de prueba; el panel conserva una única conexión y el ciclo de captura de #78.
 * @param {{iniciar: () => void, terminar: () => void, cambiar: () => void}} acciones
 */
export function montarPruebaASR(acciones) {
  const seccion = document.createElement('section');
  seccion.id = 'prueba-asr';
  seccion.innerHTML = `
    <style>
      #prueba-asr { max-width:1000px; margin:1rem auto; padding:0 1.2rem; }
      #prueba-asr h2 { font-size:1.1rem; }
      #prueba-asr .ajustes { display:flex; flex-wrap:wrap; gap:.8rem; align-items:center; }
      #prueba-asr input { font:inherit; width:7rem; }
      #prueba-asr .medicion { margin:1rem 0; }
      #prueba-asr progress { width:100%; height:1.2rem; }
      #prueba-asr .pista { position:relative; height:1rem; background:#dddbd5; margin:.5rem 0; }
      #asr-nivel { width:100%; height:100%; display:block; }
      #asr-umbral-linea { position:absolute; top:-.2rem; height:1.4rem; border-left:3px solid #1d1d1b; }
      #asr-textos p { padding:.6rem; background:white; border:1px solid #dddbd5; }
      #asr-textos .parcial { color:#6b6a66; font-style:italic; }
      #asr-textos small { display:block; color:#6b6a66; }
      body.asr #controles > :not(#error), body.asr main { display:none; }
      body.protegida #prueba-asr { display:none; }
    </style>
    <label><input id="asr-modo" type="checkbox"> Probar el ASR · solo micrófono, sin detector</label>
    <div id="asr-contenido" hidden>
      <h2>Hablá y mirá cuándo se cierra cada frase</h2>
      <div class="ajustes">
        <label>Corte de silencio <select id="asr-corte"><option value="0.5">0,5 s</option><option value="0.8" selected>0,8 s</option><option value="1.2">1,2 s</option></select></label>
        <label>Umbral de volumen (RMS) <input id="asr-umbral" type="number" min="0.0001" max="1" step="0.0001" value="0.005"></label>
        <button id="asr-iniciar" disabled>▶ Hablar</button><button id="asr-terminar" disabled>Terminar prueba</button>
      </div>
      <p>Usá auriculares. El silencio es el audio por debajo del umbral; subilo si el ruido impide cerrar frases. La demora se estima desde el último bloque con voz.</p>
      <div class="medicion">
        <label for="asr-nivel">Volumen <output id="asr-rms">RMS 0.000</output></label>
        <div class="pista"><meter id="asr-nivel" min="0" max="1" value="0"></meter><span id="asr-umbral-linea" title="Umbral de silencio"></span></div>
        <label for="asr-silencio">Silencio hasta cerrar la frase <output id="asr-espera">0,00 / 0,80 s</output></label>
        <progress id="asr-silencio" max="0.8" value="0"></progress>
      </div>
      <div id="asr-textos" aria-live="polite"></div>
    </div>`;
  document.querySelector('main')?.before(seccion);
  /** @template {HTMLElement} T @param {string} id @returns {T} */
  const el = id => /** @type {T} */ (seccion.querySelector(`#${id}`));
  const modo = /** @type {HTMLInputElement} */ (el('asr-modo'));
  const corte = /** @type {HTMLSelectElement} */ (el('asr-corte'));
  const umbral = /** @type {HTMLInputElement} */ (el('asr-umbral'));
  const iniciar = /** @type {HTMLButtonElement} */ (el('asr-iniciar'));
  const terminar = /** @type {HTMLButtonElement} */ (el('asr-terminar'));
  const volumen = /** @type {HTMLMeterElement} */ (el('asr-nivel'));
  const silencio = /** @type {HTMLProgressElement} */ (el('asr-silencio'));
  /** @type {Map<number, HTMLParagraphElement>} */
  const frases = new Map();
  let cuadro = 0;
  /** @type {{rms: number, silencio_acum_s: number, corte_silencio_s: number, umbral_rms_silencio: number}|null} */
  let ultimoNivel = null;
  /** @param {number} x */
  const escala = x => Math.min(100, Math.max(0, x * 100));
  function limpiarNiveles() {
    cancelAnimationFrame(cuadro); cuadro = 0; ultimoNivel = null;
    volumen.value = 0;
    el('asr-rms').textContent = 'RMS 0.000';
    silencio.value = 0;
    el('asr-espera').textContent = `0,00 / ${Number(corte.value).toFixed(2)} s`;
  }
  function dibujarUmbral() { el('asr-umbral-linea').style.left = `${escala(Number(umbral.value))}%`; }
  function aplicarModo() {
    document.body.classList.toggle('asr', modo.checked);
    el('asr-contenido').hidden = !modo.checked;
    acciones.cambiar();
  }
  modo.onchange = aplicarModo;
  umbral.oninput = dibujarUmbral;
  corte.onchange = limpiarNiveles;
  iniciar.onclick = () => { if (umbral.reportValidity()) acciones.iniciar(); };
  terminar.onclick = acciones.terminar;
  dibujarUmbral();
  return {
    get activa() { return modo.checked; },
    get config() { return {corte_silencio_s: Number(corte.value), umbral_rms_silencio: Number(umbral.value)}; },
    /** @param {boolean} conectada @param {boolean} ocupada @param {boolean} enLlamada */
    controles(conectada, ocupada, enLlamada) {
      modo.disabled = ocupada || enLlamada;
      corte.disabled = umbral.disabled = ocupada || enLlamada;
      iniciar.disabled = !conectada || ocupada || enLlamada;
      terminar.disabled = !conectada || ocupada || !enLlamada;
    },
    /** @param {any} m */
    evento(m) {
      if (m.tipo === 'inicio') {
        modo.checked = m.modo === 'asr'; aplicarModo();
        frases.clear(); el('asr-textos').replaceChildren(); limpiarNiveles();
        if (modo.checked) {
          corte.value = String(m.corte_silencio_s); umbral.value = String(m.umbral_rms_silencio);
          silencio.max = m.corte_silencio_s; dibujarUmbral();
        }
      }
      if (!modo.checked) return;
      if (m.tipo === 'fin' || m.tipo === 'desconexion') limpiarNiveles();
      if (m.tipo === 'niveles') {
        ultimoNivel = m.canales.protegida;
        if (!cuadro) cuadro = requestAnimationFrame(() => {
          cuadro = 0;
          if (!ultimoNivel) return;
          volumen.value = ultimoNivel.rms;
          el('asr-rms').textContent = `RMS ${ultimoNivel.rms.toFixed(3)}`;
          silencio.max = ultimoNivel.corte_silencio_s;
          silencio.value = Math.min(silencio.max, ultimoNivel.silencio_acum_s);
          el('asr-espera').textContent = `${silencio.value.toFixed(2)} / ${silencio.max.toFixed(2)} s`;
        });
      }
      if (m.tipo === 'asr' && m.rol === 'protegida') {
        let frase = frases.get(m.segmento);
        if (!frase) { frase = document.createElement('p'); frases.set(m.segmento, frase); el('asr-textos').append(frase); }
        frase.className = m.entrega;
        frase.textContent = m.texto;
        if (m.entrega === 'final') {
          const demora = document.createElement('small');
          demora.textContent = `Cerrada ${((m.disponible_s - m.fin_voz_s) * 1000).toFixed(0)} ms después de callarte`;
          frase.append(demora);
          silencio.value = silencio.max;
        }
      }
    }
  };
}
