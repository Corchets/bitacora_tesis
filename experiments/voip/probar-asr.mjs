// @ts-check

import {crearSelectorCorte} from './corte-silencio.mjs';

/**
 * UI de prueba; el panel conserva una única conexión y el ciclo de captura de #78.
 * @param {{iniciar: () => void, terminar: () => void, borrar: () => void, guardar: (referencias: Record<string, string>) => void, cambiar: () => void, borrarGuardadas: () => boolean}} acciones
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
      #prueba-asr .cabeza > :first-child { flex:1 1 0; min-width:16rem; }
      #prueba-asr .botones { display:flex; align-items:center; gap:.45rem; }
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
      #asr-textos .asr-frase + .asr-frase { margin-top:1.25rem; }
      #asr-textos label { display:block; font-weight:600; margin:.5rem 0 .25rem; }
      #asr-guardado { display:grid; gap:.5rem; }
      #asr-guardado[hidden] { display:none; }
      #asr-guardado label { font-weight:700; }
      #asr-guardado .fila { display:flex; flex-wrap:wrap; gap:.6rem; align-items:center; }
      #asr-guardado-estado { font-weight:600; color:var(--tinta-secundaria, #334155); }
      #prueba-asr .opciones { position:relative; }
      #prueba-asr .opciones summary { list-style:none; cursor:pointer; display:inline-flex; align-items:center; justify-content:center; width:2.25rem; height:100%; min-height:2.25rem; border:1px solid var(--linea, #cbd5e1); border-radius:6px; background:var(--superficie, #ffffff); color:var(--tinta-secundaria, #334155); font-size:1.1rem; }
      #prueba-asr .opciones summary::-webkit-details-marker { display:none; }
      #prueba-asr .opciones summary:focus-visible { outline:2px solid var(--primary, #1d4ed8); outline-offset:1px; }
      #prueba-asr .opciones[aria-disabled="true"] summary { opacity:.5; cursor:not-allowed; }
      #prueba-asr .menu { position:absolute; right:0; top:calc(100% + .35rem); z-index:5; min-width:16rem; padding:.35rem; background:var(--superficie, #ffffff); border:1px solid var(--linea, #cbd5e1); border-radius:8px; box-shadow:0 8px 24px rgba(15,23,42,.12); }
      #prueba-asr .menu button { width:100%; text-align:left; border:0; background:none; color:var(--alerta, #b91c1c); padding:.5rem .6rem; border-radius:6px; }
      #prueba-asr .menu button:hover { background:var(--alerta-fondo, #fef2f2); }
      #asr-opciones-estado { font-size:.8125rem; font-weight:600; color:var(--tinta-secundaria, #334155); }
      #asr-opciones-estado:empty { display:none; }
      #asr-confirmar { max-width:28rem; border:1px solid var(--linea, #cbd5e1); border-radius:12px; padding:1.1rem 1.25rem; }
      #asr-confirmar::backdrop { background:rgba(15,23,42,.35); }
      #asr-confirmar h2 { font-size:1.125rem; }
      #asr-confirmar p { margin:.5rem 0 1rem; color:var(--tinta-secundaria, #334155); line-height:1.5; }
      #asr-confirmar .acciones { display:flex; justify-content:flex-end; gap:.45rem; }
      #asr-conf-borrar { background:var(--alerta-fondo, #fef2f2); color:var(--alerta, #b91c1c); border-color:var(--alerta-borde, #f87171); }
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
            <span id="asr-opciones-estado" role="status"></span>
            <button id="asr-borrar" disabled title="Borra lo hablado de la pantalla; durante la prueba, empieza de nuevo sin cortar el micrófono">Borrar</button>
            <button id="asr-terminar" disabled>Terminar prueba</button>
            <button id="asr-iniciar" disabled>▶ Hablar</button>
            <details class="opciones" id="asr-opciones">
              <summary title="Opciones de las pruebas" aria-label="Opciones de las pruebas">⚙</summary>
              <div class="menu">
                <button id="asr-borrar-guardadas" type="button">Borrar todas las pruebas guardadas…</button>
              </div>
            </details>
          </div>
        </div>
        <div class="ajustes">
          <div class="ajuste">
            <span id="asr-corte-lugar"></span>
            <p>Cuántos segundos callado tienen que pasar para dar la frase por terminada. Más corto, antes llega el texto final; demasiado corto parte las frases.</p>
          </div>
          <div class="ajuste">
            <label for="asr-umbral">Umbral de silencio (volumen)</label>
            <input id="asr-umbral" type="number" min="0.001" max="1" step="0.001" value="0.003" aria-describedby="asr-umbral-ayuda">
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
      <dialog id="asr-confirmar" aria-labelledby="asr-conf-titulo">
        <form method="dialog">
          <h2 id="asr-conf-titulo">¿Borrar todas las pruebas de ASR guardadas?</h2>
          <p>Se borran sus carpetas con el audio, la transcripción y lo que dijiste en realidad. Las llamadas no se tocan. No se puede deshacer.</p>
          <div class="acciones">
            <button value="cancelar" autofocus>Cancelar</button>
            <button value="borrar" id="asr-conf-borrar">Borrar</button>
          </div>
        </form>
      </dialog>
      <div id="asr-guardado" class="tarjeta" hidden>
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
  const guardar = /** @type {HTMLButtonElement} */ (el('asr-guardar'));
  const estadoGuardado = el('asr-guardado-estado');
  const AVISO_DESCARTE = 'Si no la guardás, se descarta al empezar otra prueba.';
  const opciones = /** @type {HTMLDetailsElement} */ (el('asr-opciones'));
  const confirmarBorrado = /** @type {HTMLDialogElement} */ (el('asr-confirmar'));
  const estadoOpciones = el('asr-opciones-estado');
  let opcionesBloqueadas = true, esperandoBorrado = false, enCurso = false, puedeBorrar = false;
  opciones.addEventListener('toggle', () => { if (opciones.open && opcionesBloqueadas) opciones.open = false; });
  document.addEventListener('click', e => { if (opciones.open && !opciones.contains(/** @type {Node} */ (e.target))) opciones.open = false; });
  el('asr-borrar-guardadas').onclick = () => {
    opciones.open = false; confirmarBorrado.returnValue = '';
    confirmarBorrado.showModal();
  };
  confirmarBorrado.onclose = () => {
    if (confirmarBorrado.returnValue !== 'borrar') return;
    esperandoBorrado = acciones.borrarGuardadas();
    estadoOpciones.textContent = esperandoBorrado ? 'Borrando…' : 'Sin conexión con el servidor.';
  };
  let esPrueba = false, guardando = false, guardada = false;
  function ocultarGuardado() {
    guardado.hidden = true; guardando = guardada = false;
    guardar.disabled = false;
    estadoGuardado.textContent = AVISO_DESCARTE;
  }
  const volumen = el('asr-nivel');
  const barraSilencio = el('asr-silencio');
  // Barra de silencio: max y value como un <progress>, pero dibujada con transform.
  const silencio = {max: 0.8, valor: 0,
    get value() { return this.valor; },
    set value(v) { this.valor = v; barraSilencio.style.transform = `scaleX(${this.max ? Math.min(1, v / this.max) : 0})`; }};
  /** @type {Map<number, {elemento: HTMLDivElement, texto: HTMLParagraphElement, referencia?: HTMLTextAreaElement}>} */
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
  // Durante la prueba reinicia en el servidor; terminada, solo limpia la pantalla (lo guardado queda en Historial).
  borrar.onclick = () => {
    if (enCurso) { acciones.borrar(); return; }
    frases.clear(); el('asr-textos').replaceChildren(); limpiarNiveles();
    guardado.hidden = true; estadoOpciones.textContent = '';
    borrar.disabled = true;
  };
  guardar.onclick = () => {
    guardando = true; guardar.disabled = true;
    estadoGuardado.textContent = 'Guardando…';
    acciones.guardar(Object.fromEntries([...frases].filter(([, f]) => f.referencia)
      .map(([segmento, f]) => [String(segmento), f.referencia?.value || ''])));
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
      enCurso = enLlamada; puedeBorrar = conectada && !ocupada;
      borrar.disabled = !puedeBorrar || (!enLlamada && !frases.size && guardado.hidden);
      // El servidor no borra con una prueba en curso.
      opcionesBloqueadas = !conectada || ocupada || enLlamada;
      opciones.setAttribute('aria-disabled', String(opcionesBloqueadas));
      if (opcionesBloqueadas) opciones.open = false;
    },
    /** @param {any} m */
    evento(m) {
      if (esperandoBorrado && (m.tipo === 'borrado' || m.tipo === 'error')) {
        esperandoBorrado = false;
        const n = m.tipo === 'borrado' ? m.ids.length : -1;
        estadoOpciones.textContent = n < 0 ? 'No se pudo borrar.' : n === 0 ? 'No había pruebas guardadas.'
          : n === 1 ? 'Se borró 1 prueba.' : `Se borraron ${n} pruebas.`;
      }
      if (m.tipo === 'inicio') {
        estadoOpciones.textContent = '';
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
      if (m.tipo === 'fin') borrar.disabled = !puedeBorrar;
      if (m.tipo === 'prueba_guardada') {
        guardando = false; guardada = true;
        for (const [segmento, frase] of frases) if (frase.referencia) {
          frase.referencia.value = m.referencias_por_segmento?.[segmento] ?? frase.referencia.value;
          frase.referencia.disabled = true;
        }
        guardar.disabled = true;
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
        if (!frase) {
          frase = {elemento: document.createElement('div'), texto: document.createElement('p')};
          frase.elemento.className = 'asr-frase'; frase.elemento.append(frase.texto);
          frases.set(m.segmento, frase); el('asr-textos').append(frase.elemento);
        }
        frase.texto.className = m.entrega;
        frase.texto.textContent = m.texto;
        if (m.entrega === 'final') {
          const demora = document.createElement('small');
          demora.textContent = `Cerrada ${((m.disponible_s - m.fin_voz_s) * 1000).toFixed(0)} ms después de callarte`;
          frase.texto.append(demora);
          if (!frase.referencia) {
            const campo = document.createElement('textarea');
            campo.id = `asr-ref-${m.segmento}`; campo.maxLength = 2000;
            campo.placeholder = 'Escribí esta frase tal como la dijiste';
            const label = document.createElement('label'); label.htmlFor = campo.id;
            label.textContent = `Lo que dije en realidad · frase ${m.segmento}`;
            frase.elemento.append(label, campo); frase.referencia = campo;
          }
          silencio.value = silencio.max;
        }
      }
    }
  };
}
