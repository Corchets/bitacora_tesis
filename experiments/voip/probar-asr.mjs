// @ts-check

import {crearSelectorCorte} from './corte-silencio.mjs';

/**
 * UI de prueba; el panel conserva una única conexión y el ciclo de captura de #78.
 * @param {{iniciar: () => void, terminar: () => void, borrar: () => void, guardar: (referencia: string) => void, cambiar: () => void}} acciones
 */
export function montarPruebaASR(acciones) {
  const seccion = document.createElement('section');
  seccion.id = 'prueba-asr';
  seccion.innerHTML = `
    <style>
      #prueba-asr { display:none; max-width:1000px; width:calc(100% - 2rem); margin:1rem auto; }
      body.asr #prueba-asr { display:block; }
      #prueba-asr .asr-modo-toggle { position:absolute; width:1px; height:1px; padding:0; margin:-1px; overflow:hidden; clip:rect(0, 0, 0, 0); white-space:nowrap; border:0; }
      #prueba-asr .tarjeta { background:var(--superficie, #ffffff); border:1px solid var(--linea, #cbd5e1); border-radius:12px; padding:1.1rem 1.25rem; margin-bottom:.85rem; }
      #prueba-asr h2 { font-size:1.375rem; letter-spacing:-.01em; margin:0; color:var(--tinta, #0f172a); }
      #prueba-asr .bajada { margin:.25rem 0 0; color:var(--tinta-secundaria, #334155); }
      #prueba-asr .cabeza { display:flex; flex-wrap:wrap; justify-content:space-between; align-items:flex-end; gap:1rem; }
      #prueba-asr .botones { display:flex; gap:.45rem; }
      #asr-iniciar { background:var(--primary, #1d4ed8); color:#fff; border-color:var(--primary, #1d4ed8); padding-inline:1.1rem; }
      #asr-iniciar:hover:not(:disabled) { background:var(--primary-dark, #1e40af); }
      #asr-terminar { color:var(--alerta, #b91c1c); border-color:var(--alerta-borde, #f87171); }
      #prueba-asr .ajustes { display:grid; grid-template-columns:repeat(2, minmax(0, 1fr)); gap:1rem 1.5rem; margin-top:1rem; padding-top:1rem; border-top:1px solid var(--linea, #cbd5e1); }
      #prueba-asr .ajuste p { margin:.35rem 0 0; font-size:.8125rem; line-height:1.5; color:var(--tinta-secundaria, #334155); max-width:52ch; }
      #prueba-asr .ajuste label { font-size:.75rem; font-weight:700; color:var(--tinta-secundaria, #334155); display:block; margin-bottom:.2rem; }
      #prueba-asr #asr-umbral { font:inherit; font-size:.875rem; width:6.5rem; padding:.4rem .5rem; border:1px solid var(--linea, #cbd5e1); border-radius:6px; font-variant-numeric:tabular-nums; }
      #prueba-asr textarea { font:inherit; width:100%; min-height:4.5rem; padding:.5rem .6rem; border:1px solid var(--linea, #cbd5e1); border-radius:6px; resize:vertical; box-sizing:border-box; }
      #prueba-asr .medidor { display:grid; gap:.3rem; }
      #prueba-asr .medidor + .medidor { margin-top:.9rem; }
      #prueba-asr .medidor-cabeza { display:flex; justify-content:space-between; align-items:baseline; font-size:.8125rem; font-weight:700; color:var(--tinta-secundaria, #334155); }
      #prueba-asr output { font-variant-numeric:tabular-nums; font-weight:600; }
      #prueba-asr .pista { position:relative; height:14px; background:var(--superficie-alt, #e2e8f0); border-radius:7px; }
      #prueba-asr .relleno { position:absolute; inset:0; border-radius:7px; transform-origin:left; transform:scaleX(0); transition:transform 90ms linear; }
      #asr-nivel { background:var(--ok, #15803d); }
      #asr-nivel.bajo { background:#94a3b8; }
      #asr-silencio { background:var(--primary, #1d4ed8); }
      #asr-umbral-linea { position:absolute; top:-5px; bottom:-5px; width:3px; margin-left:-1.5px; background:var(--tinta, #0f172a); border-radius:2px; }
      #asr-umbral-linea::after { content:"umbral"; position:absolute; top:100%; left:50%; transform:translateX(-50%); margin-top:2px; font-size:.6875rem; font-weight:700; color:var(--tinta, #0f172a); }
      #prueba-asr .escala { display:flex; justify-content:space-between; font-size:.6875rem; color:var(--mu, #64748b); margin-top:1rem; }
      #asr-textos:empty::before { content:"Lo que digas aparece acá: gris mientras hablás, fijo cuando se cierra la frase."; color:var(--mu, #64748b); }
      #asr-textos p { padding:.6rem .8rem; background:var(--superficie, #ffffff); border:1px solid var(--linea, #cbd5e1); border-radius:8px; margin:.4rem 0; font-size:1.0625rem; }
      #asr-textos .parcial { color:var(--tinta-secundaria, #334155); border-style:dashed; }
      #asr-textos small { display:block; color:var(--mu, #64748b); margin-top:.2rem; font-size:.75rem; font-variant-numeric:tabular-nums; }
      #asr-guardado { display:grid; gap:.5rem; }
      #asr-guardado[hidden] { display:none; }
      #asr-guardado label { font-weight:700; }
      #asr-guardado .fila { display:flex; flex-wrap:wrap; gap:.6rem; align-items:center; }
      #asr-guardado-estado { font-weight:600; color:var(--tinta-secundaria, #334155); }
      body.asr #controles > :not(#error):not(.campos), body.asr #controles .campos > :not(#campo-microfono), body.asr main { display:none; }
      body.protegida #prueba-asr { display:none; }
      @media (max-width: 760px) { #prueba-asr .ajustes { grid-template-columns:1fr; } }
      @media (prefers-reduced-motion: reduce) { #prueba-asr .relleno { transition:none; } }
    </style>
    <label class="asr-modo-toggle"><input id="asr-modo" type="checkbox"> Probar el ASR · solo micrófono, sin detector</label>
    <div id="asr-contenido" hidden>
      <div class="tarjeta">
        <div class="cabeza">
          <div>
            <h2>Probar el ASR</h2>
            <p class="bajada">Hablá con pausas y mirá cuándo se cierra cada frase. Solo tu micrófono, sin detector. Usá auriculares.</p>
          </div>
          <div class="botones">
            <button id="asr-borrar" disabled title="Borra lo hablado y empieza de nuevo sin cortar el micrófono">Borrar</button>
            <button id="asr-terminar" disabled>Terminar prueba</button>
            <button id="asr-iniciar" disabled>▶ Hablar</button>
          </div>
        </div>
        <div class="ajustes">
          <div class="ajuste">
            <span id="asr-corte-lugar"></span>
            <p>Cuántos segundos callado tienen que pasar para dar la frase por terminada. Más corto, antes llega el texto final; demasiado corto parte las frases.</p>
          </div>
          <div class="ajuste">
            <label for="asr-umbral">Umbral de silencio (volumen)</label>
            <input id="asr-umbral" type="number" min="0.001" max="1" step="0.001" value="0.005" aria-describedby="asr-umbral-ayuda">
            <p id="asr-umbral-ayuda">Por debajo de este volumen el sonido cuenta como silencio. Es la rayita negra del medidor de abajo: si con ruido de fondo la barra de silencio no se llena nunca, subilo (por ejemplo a 0,02); si corta mientras hablás bajito, bajalo.</p>
          </div>
        </div>
      </div>
      <div class="tarjeta">
        <div class="medidor">
          <div class="medidor-cabeza"><span>Volumen de tu voz</span><output id="asr-rms">RMS 0.000</output></div>
          <div class="pista"><div id="asr-nivel" class="relleno bajo"></div><span id="asr-umbral-linea" title="Umbral de silencio"></span></div>
          <div class="escala" aria-hidden="true"><span>silencio</span><span>voz normal</span><span>muy fuerte</span></div>
        </div>
        <div class="medidor">
          <div class="medidor-cabeza"><span>Silencio hasta cerrar la frase</span><output id="asr-espera">0,00 / 0,80 s</output></div>
          <div class="pista"><div id="asr-silencio" class="relleno"></div></div>
        </div>
      </div>
      <div class="tarjeta"><div id="asr-textos" aria-live="polite"></div></div>
      <div id="asr-guardado" class="tarjeta" hidden>
        <label for="asr-referencia">Lo que dije en realidad</label>
        <textarea id="asr-referencia" maxlength="2000" placeholder="Escribí la frase tal como la dijiste; sirve para medir cuánto se equivocó el ASR"></textarea>
        <div class="fila">
          <button id="asr-guardar" type="button">Guardar prueba</button>
          <span id="asr-guardado-estado" role="status">Si no la guardás, se descarta al empezar otra prueba.</span>
        </div>
      </div>
    </div>`;
  document.querySelector('main')?.before(seccion);
  /** @template {HTMLElement} T @param {string} id @returns {T} */
  const el = id => /** @type {T} */ (seccion.querySelector(`#${id}`));
  const modo = /** @type {HTMLInputElement} */ (el('asr-modo'));
  const corte = crearSelectorCorte('asr-corte');
  el('asr-corte-lugar').replaceWith(corte.elemento);
  const umbral = /** @type {HTMLInputElement} */ (el('asr-umbral'));
  const iniciar = /** @type {HTMLButtonElement} */ (el('asr-iniciar'));
  const terminar = /** @type {HTMLButtonElement} */ (el('asr-terminar'));
  const borrar = /** @type {HTMLButtonElement} */ (el('asr-borrar'));
  const guardado = el('asr-guardado');
  const referencia = /** @type {HTMLTextAreaElement} */ (el('asr-referencia'));
  const guardar = /** @type {HTMLButtonElement} */ (el('asr-guardar'));
  const estadoGuardado = el('asr-guardado-estado');
  const AVISO_DESCARTE = 'Si no la guardás, se descarta al empezar otra prueba.';
  let esPrueba = false, guardando = false, guardada = false;
  function ocultarGuardado() {
    guardado.hidden = true; guardando = guardada = false;
    referencia.value = ''; referencia.disabled = guardar.disabled = false;
    estadoGuardado.textContent = AVISO_DESCARTE;
  }
  const volumen = el('asr-nivel');
  const barraSilencio = el('asr-silencio');
  // Barra de silencio: max y value como un <progress>, pero dibujada con transform.
  const silencio = {max: 0.8, valor: 0,
    get value() { return this.valor; },
    set value(v) { this.valor = v; barraSilencio.style.transform = `scaleX(${this.max ? Math.min(1, v / this.max) : 0})`; }};
  /** @type {Map<number, HTMLParagraphElement>} */
  const frases = new Map();
  let cuadro = 0;
  /** @type {{rms: number, silencio_acum_s: number, corte_silencio_s: number, umbral_rms_silencio: number}|null} */
  let ultimoNivel = null;
  /** Escala en decibeles (-60 a 0 dB): en lineal, el umbral de 0,005 quedaba pegado al cero.
   * @param {number} rms @returns {number} fracción 0–1 */
  const escala = rms => rms <= 0 ? 0 : Math.min(1, Math.max(0, (20 * Math.log10(rms) + 60) / 60));
  function limpiarNiveles() {
    cancelAnimationFrame(cuadro); cuadro = 0; ultimoNivel = null;
    volumen.style.transform = 'scaleX(0)';
    el('asr-rms').textContent = 'RMS 0.000';
    silencio.value = 0;
    el('asr-espera').textContent = `0,00 / ${corte.segundos.toFixed(2)} s`;
  }
  function dibujarUmbral() { el('asr-umbral-linea').style.left = `${escala(Number(umbral.value)) * 100}%`; }
  function aplicarModo() {
    document.body.classList.toggle('asr', modo.checked);
    el('asr-contenido').hidden = !modo.checked;
    acciones.cambiar();
  }
  modo.onchange = aplicarModo;
  umbral.oninput = dibujarUmbral;
  corte.alCambiar = limpiarNiveles;
  iniciar.onclick = () => { if (corte.validar() && umbral.reportValidity()) acciones.iniciar(); };
  terminar.onclick = acciones.terminar;
  borrar.onclick = acciones.borrar;
  guardar.onclick = () => {
    guardando = true; guardar.disabled = true;
    estadoGuardado.textContent = 'Guardando…';
    acciones.guardar(referencia.value);
  };
  dibujarUmbral();
  return {
    get activa() { return modo.checked; },
    get config() { return {corte_silencio_s: corte.valor, umbral_rms_silencio: Number(umbral.value)}; },
    /** @param {boolean} conectada @param {boolean} ocupada @param {boolean} enLlamada */
    controles(conectada, ocupada, enLlamada) {
      modo.disabled = ocupada || enLlamada;
      corte.deshabilitado = umbral.disabled = ocupada || enLlamada;
      iniciar.disabled = !conectada || ocupada || enLlamada;
      terminar.disabled = !conectada || ocupada || !enLlamada;
      borrar.disabled = !conectada || ocupada || !enLlamada;
    },
    /** @param {any} m */
    evento(m) {
      if (m.tipo === 'inicio') {
        esPrueba = m.modo === 'asr';
        ocultarGuardado();
        modo.checked = esPrueba; aplicarModo();
        frases.clear(); el('asr-textos').replaceChildren(); limpiarNiveles();
        if (modo.checked) {
          corte.valor = m.corte_silencio_s; umbral.value = String(m.umbral_rms_silencio);
          silencio.max = corte.segundos; dibujarUmbral();
        }
      }
      if (!modo.checked) return;
      if (m.tipo === 'fin' && esPrueba) guardado.hidden = false;
      if (m.tipo === 'prueba_guardada') {
        guardando = false; guardada = true;
        referencia.value = m.referencia; referencia.disabled = guardar.disabled = true;
        estadoGuardado.textContent = 'Guardada ✓ Quedó con el audio, la transcripción y lo que dijiste en realidad.';
      }
      if (m.tipo === 'error' && guardando) {
        guardando = false; guardar.disabled = false;
        estadoGuardado.textContent = AVISO_DESCARTE;
      }
      if (m.tipo === 'fin' || m.tipo === 'desconexion') limpiarNiveles();
      if (m.tipo === 'niveles') {
        ultimoNivel = m.canales.protegida;
        if (!cuadro) cuadro = requestAnimationFrame(() => {
          cuadro = 0;
          if (!ultimoNivel) return;
          volumen.style.transform = `scaleX(${escala(ultimoNivel.rms)})`;
          volumen.classList.toggle('bajo', ultimoNivel.rms < ultimoNivel.umbral_rms_silencio);
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
