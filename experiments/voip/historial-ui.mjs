// @ts-check

import {crearLinea} from './conversacion.mjs';

/**
 * @typedef {{id: string, fecha: string|null, tipo: 'llamada'|'prueba', incompleta: boolean, fuente: string,
 *   duracion_s: number|null, detector: string|null, modelo: string|null, corte_silencio_s: 'auto'|number|null,
 *   umbral_rms_silencio: number|null, riesgo_maximo: number|null, aviso: boolean, aviso_s: number|null,
 *   referencia?: string}} Elemento
 * @typedef {{item: Elemento, aviso: {t_a: number|null, motivo: string, evidencia: string, riesgo: number|null}|null,
 *   conversacion: Array<{rol: string, texto: string, fin_audio_s: number|null, provisorio: boolean, aviso: boolean}>}} Detalle
 */

const ESTILOS = `
  #historial { display:none; max-width:1500px; width:calc(100% - 2rem); margin:1rem auto; padding:0 0 1rem; max-height:calc(100vh - 5.5rem); overflow-y:auto; }
  body.historial #historial { display:block; }
  body.historial #controles, body.historial main, body.historial #prueba-asr, body.historial #sonido-aviso { display:none !important; }
  #historial h2 { font-size:1.25rem; margin:0; color:var(--tinta); }
  #historial h3 { font-size:.9375rem; margin:0 0 .5rem; color:var(--tinta-secundaria); }
  #historial .hist-barra { display:flex; flex-wrap:wrap; gap:.6rem; align-items:center; margin-bottom:.8rem; }
  #historial .hist-barra .hist-espacio { flex:1; }
  #hist-estado { color:var(--tinta-secundaria); font-size:.875rem; font-weight:600; }
  #historial .hist-columnas { display:grid; grid-template-columns:1fr 1fr; gap:1rem; align-items:start; }
  #historial ul { list-style:none; margin:0; padding:0; display:grid; gap:.45rem; }
  #historial li { display:flex; gap:.5rem; align-items:stretch; }
  #historial .hist-marca { display:flex; align-items:center; padding:0 .35rem; }
  #historial .hist-marca input { width:1.25rem; height:1.25rem; }
  #historial .hist-fila { flex:1; text-align:left; display:grid; gap:.15rem; padding:.55rem .75rem; font-weight:500; }
  #historial .hist-fila b { font-size:1.0625rem; color:var(--tinta); }
  #historial .hist-fila span { font-size:.875rem; color:var(--tinta-secundaria); font-variant-numeric:tabular-nums; }
  #historial .hist-vacio { color:var(--mu); font-size:.9375rem; padding:.5rem 0; }
  #historial .hist-insignia { display:inline-block; font-size:.75rem; font-weight:700; padding:.05rem .45rem; border-radius:var(--radio-sm); border:1px solid var(--linea); background:var(--superficie-alt); color:var(--tinta); margin-left:.4rem; }
  #historial .hist-insignia.aviso { background:var(--alerta); border-color:var(--alerta); color:var(--superficie); }
  #hist-cols { display:grid; grid-template-columns:repeat(var(--columnas, 1), minmax(0, 1fr)); gap:1rem; align-items:start; max-width:var(--ancho-detalle, 1000px); margin:0 auto; }
  #historial .hist-col { background:var(--superficie); border:1px solid var(--linea); border-radius:var(--radio-lg); padding:.75rem; min-width:0; }
  #historial .hist-datos { display:grid; grid-template-columns:auto 1fr; gap:.15rem .75rem; margin:.5rem 0 .75rem; font-size:.9375rem; }
  #historial .hist-datos dt { color:var(--tinta-secundaria); font-weight:600; }
  #historial .hist-datos dd { margin:0; font-weight:600; font-variant-numeric:tabular-nums; text-align:left; justify-self:start; }
  #historial .hist-ref { display:grid; gap:.4rem; margin-bottom:.75rem; }
  #historial .hist-ref label { font-weight:600; }
  #historial textarea { font:inherit; width:100%; min-height:3.5rem; padding:.45rem .6rem; border:1px solid var(--linea); border-radius:var(--radio-sm); resize:vertical; box-sizing:border-box; }
  #historial .hist-charla { display:flex; flex-direction:column; gap:.55rem; }
  #historial .hist-charla .linea { width:90%; max-width:90%; animation:none; }
`;

/** @param {number|null|undefined} n @param {string} [unidad] */
const num = (n, unidad = '') => n == null ? '—' : `${n.toFixed(1)}${unidad}`;
/** @param {Elemento['corte_silencio_s']} c */
const corte = c => c === 'auto' ? 'Automático' : c == null ? '—' : `${c.toFixed(1)} s`;
/** @param {number|null} r */
const riesgo = r => r == null ? '—' : `${Math.round(r * 100)}%`;
/** @param {Elemento} e */
const detector = e => e.detector ? (e.modelo ? `${e.detector} · ${e.modelo}` : e.detector) : '—';
/** @param {Elemento} e */
const avisoTexto = e => e.aviso ? `Avisó a los ${num(e.aviso_s, ' s')}` : 'No avisó';
/** @param {string|null} iso */
function fecha(iso) {
  const d = iso ? new Date(iso) : null;
  return d && !isNaN(d.getTime())
    ? d.toLocaleString('es-AR', {day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit', hour12: false})
    : 'Fecha desconocida';
}
/** @param {string} texto */
const sinPuntuacionInicial = texto => texto.replace(/^[.\s,;:]+/, '').trim();

/**
 * Pestaña Historial: lista llamadas y pruebas guardadas, muestra una conversación o compara dos.
 * Todo viaja por los mensajes de control del panel (`historial`, `ver`, `referencia`).
 * @param {{enviar: (mensaje: object) => boolean, alCambiar: () => void}} acciones
 */
export function montarHistorial(acciones) {
  const seccion = document.createElement('section');
  seccion.id = 'historial';
  seccion.setAttribute('aria-label', 'Historial de llamadas y pruebas');
  seccion.innerHTML = `
    <style>${ESTILOS}</style>
    <div id="hist-lista-vista">
      <div class="hist-barra">
        <h2>Historial</h2><span id="hist-estado" role="status"></span><span class="hist-espacio"></span>
        <button id="hist-comparar" type="button" disabled>Comparar (marcá dos)</button>
        <button id="hist-actualizar" type="button">Actualizar</button>
      </div>
      <div class="hist-columnas">
        <section aria-labelledby="hist-t-llamadas"><h3 id="hist-t-llamadas">Llamadas</h3><ul id="hist-llamadas"></ul></section>
        <section aria-labelledby="hist-t-pruebas"><h3 id="hist-t-pruebas">Pruebas de ASR guardadas</h3><ul id="hist-pruebas"></ul></section>
      </div>
    </div>
    <div id="hist-detalle-vista" hidden>
      <div class="hist-barra">
        <button id="hist-volver" type="button">← Volver a la lista</button>
        <h2 id="hist-titulo" tabindex="-1"></h2><span id="hist-estado-detalle" role="status"></span>
      </div>
      <div id="hist-cols"></div>
    </div>`;
  document.querySelector('main')?.before(seccion);
  /** @template {HTMLElement} T @param {string} id @returns {T} */
  const el = id => /** @type {T} */ (seccion.querySelector(`#${id}`));
  const comparar = /** @type {HTMLButtonElement} */ (el('hist-comparar'));
  const listaVista = el('hist-lista-vista'), detalleVista = el('hist-detalle-vista');

  let abierto = false;
  /** @type {Elemento[]} */ let elementos = [];
  /** @type {string[]} */ let marcados = [];
  /** @type {string[]} */ let pedidos = [];
  /** @type {Map<string, Detalle>} */ const detalles = new Map();
  /** @type {string|null} */ let ultimoAbierto = null;

  /** @param {string} texto */
  function estado(texto) { el('hist-estado').textContent = texto; el('hist-estado-detalle').textContent = texto; }

  function dibujarLista() {
    for (const [id, tipo, vacio] of /** @type {const} */ ([
      ['hist-llamadas', 'llamada', 'Todavía no hay llamadas guardadas.'],
      ['hist-pruebas', 'prueba', 'Todavía no hay pruebas guardadas. Se guardan con «Guardar prueba» en Probar el ASR.']])) {
      const ul = el(id);
      const items = elementos.filter(e => e.tipo === tipo);
      ul.replaceChildren(...(items.length ? items.map(fila) : [Object.assign(document.createElement('li'), {className: 'hist-vacio', textContent: vacio})]));
    }
    actualizarMarcas();
  }

  /** Solo cambia el estado de las casillas y del botón: no redibuja filas, así el foco no se pierde. */
  function actualizarMarcas() {
    const dos = marcados.length === 2;
    comparar.disabled = !dos;
    comparar.textContent = dos ? 'Comparar los 2 marcados' : `Comparar (marcá dos${marcados.length ? `; hay ${marcados.length}` : ''})`;
    for (const caja of seccion.querySelectorAll('.hist-marca input')) {
      const c = /** @type {HTMLInputElement} */ (caja);
      c.disabled = dos && !c.checked;
    }
  }

  /** @param {Elemento} e */
  function fila(e) {
    const li = document.createElement('li');
    const etiqueta = `${fecha(e.fecha)} · ${e.fuente}`;
    const marca = document.createElement('label');
    marca.className = 'hist-marca';
    const caja = document.createElement('input');
    caja.type = 'checkbox';
    caja.checked = marcados.includes(e.id);
    caja.setAttribute('aria-label', `Marcar para comparar: ${etiqueta}`);
    caja.onchange = () => {
      marcados = caja.checked ? [...marcados, e.id] : marcados.filter(id => id !== e.id);
      actualizarMarcas();
    };
    marca.append(caja);
    const boton = document.createElement('button');
    boton.type = 'button';
    boton.className = 'hist-fila';
    boton.dataset.id = e.id;
    const extra = e.tipo === 'prueba'
      ? `Corte ${corte(e.corte_silencio_s)} · Umbral ${e.umbral_rms_silencio ?? '—'} · ${e.referencia ? `«${e.referencia.slice(0, 60)}»` : 'Sin referencia'}`
      : `${detector(e)} · Corte ${corte(e.corte_silencio_s)} · Riesgo máx. ${riesgo(e.riesgo_maximo)} · ${avisoTexto(e)}`;
    boton.innerHTML = `<b></b><span class="datos"></span>`;
    /** @type {HTMLElement} */ (boton.querySelector('b')).textContent = etiqueta;
    if (e.incompleta) /** @type {HTMLElement} */ (boton.querySelector('b')).append(Object.assign(document.createElement('span'), {className: 'hist-insignia', textContent: 'Incompleta'}));
    if (e.aviso) /** @type {HTMLElement} */ (boton.querySelector('b')).append(Object.assign(document.createElement('span'), {className: 'hist-insignia aviso', textContent: 'Avisó'}));
    /** @type {HTMLElement} */ (boton.querySelector('.datos')).textContent = `${num(e.duracion_s, ' s')} · ${extra}`;
    boton.onclick = () => ver([e.id]);
    li.append(marca, boton);
    return li;
  }

  /** @param {string[]} ids */
  function ver(ids) {
    pedidos = ids;
    ultimoAbierto = ids[0];
    listaVista.hidden = true; detalleVista.hidden = false;
    el('hist-titulo').textContent = ids.length === 2 ? 'Comparación' : 'Conversación';
    el('hist-cols').replaceChildren();
    estado('Cargando…');
    for (const id of ids) if (!detalles.has(id) && !acciones.enviar({tipo: 'ver', id})) estado('Sin conexión con el servidor.');
    dibujarDetalle();
  }

  function dibujarDetalle() {
    if (!pedidos.length || !pedidos.every(id => detalles.has(id))) return;
    const cols = el('hist-cols');
    cols.style.setProperty('--columnas', String(pedidos.length));
    cols.style.setProperty('--ancho-detalle', pedidos.length === 2 ? 'none' : '1000px');
    cols.replaceChildren(...pedidos.map(id => columna(/** @type {Detalle} */ (detalles.get(id)))));
    estado('');
    el('hist-titulo').focus();
  }

  /** @param {Detalle} d */
  function columna(d) {
    const e = d.item;
    const col = document.createElement('article');
    col.className = 'hist-col';
    col.innerHTML = `<h3></h3><dl class="hist-datos"></dl>`;
    /** @type {HTMLElement} */ (col.querySelector('h3')).textContent = `${e.tipo === 'prueba' ? 'Prueba' : 'Llamada'} · ${fecha(e.fecha)} · ${e.fuente}`;
    const datos = /** @type {HTMLElement} */ (col.querySelector('dl'));
    const pares = e.tipo === 'prueba'
      ? [['Duración', num(e.duracion_s, ' s')], ['Corte', corte(e.corte_silencio_s)], ['Umbral RMS', String(e.umbral_rms_silencio ?? '—')]]
      : [['Duración', num(e.duracion_s, ' s')], ['Detector', detector(e)], ['Corte', corte(e.corte_silencio_s)],
         ['Riesgo máximo', riesgo(e.riesgo_maximo)], ['Aviso', avisoTexto(e)]];
    for (const [k, v] of pares) {
      datos.append(Object.assign(document.createElement('dt'), {textContent: k}), Object.assign(document.createElement('dd'), {textContent: v}));
    }
    if (e.tipo === 'prueba') col.append(editorReferencia(e));
    const charla = document.createElement('div');
    charla.className = 'hist-charla';
    charla.setAttribute('role', 'list');
    charla.setAttribute('aria-label', 'Conversación');
    for (const l of d.conversacion) {
      const linea = crearLinea(l.rol || 'otra', l.provisorio ? 'parcial' : 'final', l.texto, l.fin_audio_s == null ? '' : `${l.fin_audio_s.toFixed(1)} s`);
      linea.setAttribute('role', 'listitem');
      if (l.aviso && d.aviso) marcarAviso(linea, d.aviso);
      charla.append(linea);
    }
    if (!d.conversacion.length) charla.append(Object.assign(document.createElement('p'), {className: 'hist-vacio', textContent: 'No quedó texto transcripto.'}));
    col.append(charla);
    return col;
  }

  /** @param {HTMLElement} linea @param {NonNullable<Detalle['aviso']>} aviso */
  function marcarAviso(linea, aviso) {
    linea.classList.add('disparo-aviso');
    const texto = /** @type {HTMLElement} */ (linea.querySelector('.texto'));
    const cita = sinPuntuacionInicial(aviso.evidencia || '');
    const original = texto.textContent || '';
    const idx = cita ? original.toLowerCase().indexOf(cita.toLowerCase()) : -1;
    const marca = document.createElement('mark');
    marca.className = 'cita-culpable';
    if (idx >= 0) {
      marca.textContent = original.slice(idx, idx + cita.length);
      texto.replaceChildren(original.slice(0, idx), marca, original.slice(idx + cita.length));
    } else {
      marca.textContent = original;
      texto.replaceChildren(marca);
    }
    const ev = document.createElement('div');
    ev.className = 'eval-adjunta aviso-alerta';
    ev.innerHTML = `<div class="eval-pills"><span class="eval-pill eval-riesgo"></span><span class="eval-pill eval-alerta si">Alerta: Sí</span></div><span class="eval-motivo-txt"></span><span class="eval-aviso-banner"></span>`;
    /** @type {HTMLElement} */ (ev.querySelector('.eval-riesgo')).textContent = `Riesgo ${riesgo(aviso.riesgo)}`;
    /** @type {HTMLElement} */ (ev.querySelector('.eval-motivo-txt')).textContent = aviso.motivo;
    /** @type {HTMLElement} */ (ev.querySelector('.eval-aviso-banner')).textContent = `Aviso emitido a los ${num(aviso.t_a, ' s')}`;
    linea.append(ev);
  }

  /** @param {Elemento} e */
  function editorReferencia(e) {
    const caja = document.createElement('div');
    caja.className = 'hist-ref';
    const idCampo = `hist-ref-${e.id}`;
    caja.innerHTML = `<label for="${idCampo}">Lo que dije en realidad</label><textarea id="${idCampo}" maxlength="2000" placeholder="Escribí la frase tal como la dijiste"></textarea><div><button type="button">Guardar referencia</button> <span role="status"></span></div>`;
    const campo = /** @type {HTMLTextAreaElement} */ (caja.querySelector('textarea'));
    const boton = /** @type {HTMLButtonElement} */ (caja.querySelector('button'));
    const aviso = /** @type {HTMLElement} */ (caja.querySelector('[role=status]'));
    campo.value = e.referencia || '';
    campo.oninput = () => { aviso.textContent = ''; };
    boton.onclick = () => {
      boton.disabled = true; aviso.textContent = 'Guardando…';
      if (!acciones.enviar({tipo: 'referencia', id: e.id, referencia: campo.value})) { boton.disabled = false; aviso.textContent = 'Sin conexión con el servidor.'; }
      else esperandoReferencia = {id: e.id, boton, aviso};
    };
    return caja;
  }
  /** @type {{id: string, boton: HTMLButtonElement, aviso: HTMLElement}|null} */
  let esperandoReferencia = null;

  function volver() {
    pedidos = [];
    detalleVista.hidden = true; listaVista.hidden = false;
    estado('');
    const fila = ultimoAbierto && seccion.querySelector(`.hist-fila[data-id="${ultimoAbierto}"]`);
    /** @type {HTMLElement} */ (fila || comparar).focus();
  }

  function actualizar() {
    estado('Cargando…');
    if (!acciones.enviar({tipo: 'historial'})) estado('Sin conexión con el servidor.');
  }

  el('hist-actualizar').onclick = actualizar;
  el('hist-volver').onclick = volver;
  comparar.onclick = () => ver([...marcados]);
  seccion.addEventListener('keydown', ev => { if (ev.key === 'Escape' && !detalleVista.hidden) volver(); });

  return {
    get abierto() { return abierto; },
    abrir() {
      abierto = true;
      detalles.clear(); marcados = [];
      listaVista.hidden = false; detalleVista.hidden = true;
      document.body.classList.add('historial');
      actualizar();
      acciones.alCambiar();
    },
    cerrar() {
      if (!abierto) return;
      abierto = false;
      document.body.classList.remove('historial');
      acciones.alCambiar();
    },
    /** @param {any} m */
    evento(m) {
      if (!abierto) return;
      if (m.tipo === 'historial') {
        elementos = [...m.llamadas, ...m.pruebas];
        marcados = marcados.filter(id => elementos.some(e => e.id === id));
        estado('');
        dibujarLista();
      } else if (m.tipo === 'detalle') {
        detalles.set(m.item.id, m);
        dibujarDetalle();
      } else if (m.tipo === 'referencia_guardada' && esperandoReferencia && esperandoReferencia.id === m.item.id) {
        const espera = esperandoReferencia;
        espera.boton.disabled = false;
        espera.aviso.textContent = 'Guardada ✓';
        const e = elementos.find(x => x.id === m.item.id);
        if (e) e.referencia = m.item.referencia;
        const d = detalles.get(m.item.id);
        if (d) d.item.referencia = m.item.referencia;
        esperandoReferencia = null;
      } else if (m.tipo === 'error') {
        estado(m.mensaje);
        if (esperandoReferencia) { esperandoReferencia.boton.disabled = false; esperandoReferencia.aviso.textContent = m.mensaje; esperandoReferencia = null; }
      }
    }
  };
}
