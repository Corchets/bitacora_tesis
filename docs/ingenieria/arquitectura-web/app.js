/* ============================================================================
 * app.js — Diagrama de arquitectura incremental de detección de vishing.
 * Todo el contenido sale de window.DATOS (datos.js). Vanilla JS, sin build.
 * ==========================================================================*/
(function () {
  "use strict";

  var D = window.DATOS;
  var $ = function (s, r) { return (r || document).querySelector(s); };

  function el(tag, cls, txt) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (txt != null) e.textContent = txt;
    return e;
  }

  var COMP = {}; D.componentes.forEach(function (c) { COMP[c.id] = c; });
  var DEC = {}; D.decisiones.forEach(function (d) { DEC[d.id] = d; });

  var CAPAS_ORDEN = ["fuente", "entrada", "modelo", "reglas", "memoria", "decision", "salida"];

  /* ------------------------------ cabecera ------------------------------- */

  document.title = D.meta.titulo + " — visualización";
  $("#titulo-pagina").textContent = D.meta.titulo;
  $("#subtitulo-pagina").textContent = D.meta.subtitulo;
  $("#nota-estado").textContent = D.meta.notaEstado;
  $("#pie-fecha").textContent = "Datos al " + D.meta.fecha + ".";

  /* --------------------------- piezas comunes ---------------------------- */

  function badgeEstado(estado, chico) {
    return el("span", "badge badge-" + estado + (chico ? " badge-chico" : ""), estado);
  }

  function chipDec(id) {
    var b = el("button", "chip-d", id);
    b.type = "button";
    b.dataset.dec = id;
    if (DEC[id]) b.title = DEC[id].titulo;
    return b;
  }

  function chipsDe(ids) {
    var w = el("span", "nodo-chips");
    (ids || []).forEach(function (id) { w.appendChild(chipDec(id)); });
    return w;
  }

  function rellenarTarjetaVersion(art, v) {
    art.appendChild(el("h3", null, v.nombre));
    art.appendChild(el("p", "lema", v.lema));
    if (v.descripcion) art.appendChild(el("p", "desc", v.descripcion));
    if (v.flujo) art.appendChild(el("div", "flujo", v.flujo));
    if (v.mediciones && v.mediciones.length) {
      var ul = el("ul");
      v.mediciones.forEach(function (m) { ul.appendChild(el("li", null, m)); });
      art.appendChild(ul);
    }
    if (v.lectura) art.appendChild(el("p", "lectura", v.lectura));
  }

  /* --------------------------- toggle de versión ------------------------- */

  var versionActual = "slm";
  var toggle = $("#toggle-version");
  ["slm", "cascada"].forEach(function (vid) {
    var v = D.versiones[vid];
    var b = el("button", "toggle-op", v.nombre);
    b.type = "button";
    b.dataset.ver = vid;
    b.setAttribute("aria-pressed", vid === versionActual ? "true" : "false");
    b.addEventListener("click", function () { setVersion(vid); });
    toggle.appendChild(b);
  });

  function setVersion(vid) {
    versionActual = vid;
    toggle.querySelectorAll(".toggle-op").forEach(function (b) {
      b.setAttribute("aria-pressed", b.dataset.ver === vid ? "true" : "false");
    });
    var tarjeta = $("#tarjeta-version");
    tarjeta.innerHTML = "";
    rellenarTarjetaVersion(tarjeta, D.versiones[vid]);
    renderDiagrama(vid);
  }

  /* ------------------------------- diagrama ------------------------------ */

  var X0 = 36, COL = 205, NW = 180, Y_TOP = 34, Y_MAIN = 225, Y_LOW = 462, Y_BAND = 662, BAND_H = 96;
  function cx(i) { return X0 + i * COL; }

  function layoutDe(version) {
    var xEstado = cx(3.5) - 12; /* entre ASR y detector */
    var nodos = [
      { id: "fuente-replay", x: cx(0), y: 150 },
      { id: "fuente-voip", x: cx(0), y: 332 },
      { id: "adaptador", x: cx(1), y: Y_MAIN },
      { id: "vad", x: cx(2), y: Y_MAIN },
      { id: "asr", x: cx(3), y: Y_MAIN, sub: "streaming" },
      { id: "estado", x: xEstado, y: Y_LOW }
    ];
    var aristas = [
      { f: "fuente-replay", fs: "right", t: "adaptador", ts: "left" },
      { f: "fuente-voip", fs: "right", t: "adaptador", ts: "left" },
      { f: "adaptador", fs: "right", t: "vad", ts: "left" },
      { f: "vad", fs: "right", t: "asr", ts: "left" },
      { f: "asr", fs: "top", t: "reglas", ts: "left", lbl: "borrador cada 300 ms", lblV: true },
      { f: "reglas", fs: "right", t: "alerta", ts: "top", lbl: "pedido crítico", lblV: true },
      { f: "asr", fs: "bottom", t: "estado", ts: "top" },
      { f: "contador", fs: "right", t: "alerta", ts: "left", lbl: "riesgo sostenido" },
      { f: "alerta", fs: "right", t: "presentacion", ts: "left" },
      { f: "contador", fs: "bottom", t: "salida", ts: "topX", dash: true },
      { f: "alerta", fs: "bottom", t: "salida", ts: "topX", dash: true },
      { f: "estado", fs: "bottom", t: "salida", ts: "topX", dash: true }
    ];

    if (version === "cascada") {
      var xc = cx(4) + 430 + 54; /* el grupo mide 430 de ancho; la cola corre a la derecha */
      nodos.push(
        { id: "reglas", x: xc, y: Y_TOP, sub: "incendio" },
        {
          id: "grupo-detector", x: cx(4), y: Y_MAIN, grupo: true,
          tituloId: "detector",
          subs: [
            { id: "encoder", sub: "RoBERTuito + LR" },
            { id: "cascada", sub: "zona gris → SLM" }
          ]
        },
        { id: "contador", x: xc, y: Y_MAIN, sub: "goteo" },
        { id: "alerta", x: xc + COL, y: Y_MAIN },
        { id: "presentacion", x: xc + 2 * COL, y: Y_MAIN },
        { id: "salida", x: X0, y: Y_BAND, banda: true, w: xc + 2 * COL + NW - X0 }
      );
      aristas.push(
        { f: "asr", fs: "right", t: "encoder", ts: "left", lbl: "turno cerrado" },
        { f: "encoder", fs: "right", t: "cascada", ts: "left", lbl: "0,35–0,75" },
        { f: "estado", fs: "right", t: "cascada", ts: "bottom", lbl: "historial", lblV: true },
        { f: "cascada", fs: "right", t: "contador", ts: "left", lbl: "puntaje 0–1" },
        { f: "cascada", fs: "bottom", t: "salida", ts: "topX", dash: true }
      );
      return { lienzoW: xc + 2 * COL + NW + X0, lienzoH: Y_BAND + BAND_H + 40, nodos: nodos, aristas: aristas };
    }

    nodos.push(
      { id: "reglas", x: cx(5), y: Y_TOP, sub: "incendio" },
      { id: "detector", x: cx(4), y: Y_MAIN, sub: "DetectorLlm · goteo" },
      { id: "contador", x: cx(5), y: Y_MAIN, sub: "goteo" },
      { id: "alerta", x: cx(6), y: Y_MAIN },
      { id: "presentacion", x: cx(7), y: Y_MAIN },
      { id: "salida", x: X0, y: Y_BAND, banda: true, w: cx(7) + NW - X0 }
    );
    aristas.push(
      { f: "estado", fs: "top", fdx: 62, t: "detector", ts: "bottom", tdx: -52, lbl: "historial", lblV: true },
      { f: "asr", fs: "right", t: "detector", ts: "left", lbl: "turno cerrado" },
      { f: "detector", fs: "right", t: "contador", ts: "left", lbl: "puntaje 0–1" },
      { f: "detector", fs: "bottom", fdx: 55, t: "salida", ts: "topX", dash: true }
    );
    return { lienzoW: cx(7) + NW + X0, lienzoH: Y_BAND + BAND_H + 40, nodos: nodos, aristas: aristas };
  }

  /* nodos */

  function nodoBase(c, sub) {
    var nd = el("div", "nodo capa-" + c.capa);
    nd.dataset.id = c.id;
    nd.setAttribute("role", "button");
    nd.tabIndex = 0;
    nd.setAttribute("aria-label", c.nombre + " — capa " + c.capa);

    var est = el("span", "nodo-estado" + (c.estado === "vigente" ? " es-vigente" : ""), c.estado);
    nd.appendChild(est);
    nd.appendChild(el("span", "nodo-capa", c.capa));
    nd.appendChild(el("div", "nodo-nombre", c.nombre));
    if (sub) nd.appendChild(el("div", "nodo-sub", sub));
    nd.appendChild(chipsDe(c.decisiones));
    bindNodo(nd, c.id);
    return nd;
  }

  function nodoBanda(c, w) {
    var nd = nodoBase(c);
    nd.classList.add("nodo-banda");
    var cuerpo = el("div", "nodo-cuerpo-banda");
    while (nd.childNodes.length > 1) cuerpo.appendChild(nd.childNodes[1]);
    cuerpo.insertBefore(el("span", "resumen-inline", c.resumen), cuerpo.querySelector(".nodo-chips"));
    nd.appendChild(cuerpo);
    nd.style.width = w + "px";
    return nd;
  }

  function nodoGrupo(n) {
    var det = COMP[n.tituloId];
    var g = el("div", "nodo nodo-grupo capa-" + det.capa);
    g.setAttribute("role", "group");
    g.setAttribute("aria-label", det.nombre + " — versión cascada");
    g.appendChild(el("span", "nodo-estado" + (det.estado === "vigente" ? " es-vigente" : ""), det.estado));

    var cab = el("div", "grupo-cab");
    cab.appendChild(el("span", "nodo-capa", det.capa));
    var t = el("button", "grupo-titulo", det.nombre);
    t.type = "button";
    t.dataset.id = det.id;
    cab.appendChild(t);
    cab.appendChild(chipsDe(det.decisiones));
    g.appendChild(cab);

    var subs = el("div", "subnodos");
    n.subs.forEach(function (s) {
      var sub = nodoBase(COMP[s.id], s.sub);
      sub.classList.add("nodo-subnodo");
      subs.appendChild(sub);
    });
    g.appendChild(subs);

    t.addEventListener("click", function () { abrirDrawer(det.id); });
    t.addEventListener("mouseenter", function () { mostrarTooltip(det.id, t); });
    t.addEventListener("mouseleave", programarOcultarTooltip);
    t.addEventListener("focus", function () { mostrarTooltip(det.id, t); });
    t.addEventListener("blur", programarOcultarTooltip);
    return g;
  }

  var lienzo = $("#lienzo");
  var svg = $("#aristas");
  var layoutActual = null;

  function renderDiagrama(version) {
    var L = layoutDe(version);
    layoutActual = L;
    ocultarTooltip();
    lienzo.querySelectorAll(".nodo, .nodo-grupo").forEach(function (n) { n.remove(); });
    lienzo.style.width = L.lienzoW + "px";
    lienzo.style.height = L.lienzoH + "px";
    svg.setAttribute("viewBox", "0 0 " + L.lienzoW + " " + L.lienzoH);
    svg.setAttribute("width", L.lienzoW);
    svg.setAttribute("height", L.lienzoH);

    L.nodos.forEach(function (n) {
      var nd;
      if (n.grupo) nd = nodoGrupo(n);
      else if (n.banda) nd = nodoBanda(COMP[n.id], n.w);
      else nd = nodoBase(COMP[n.id], n.sub);
      nd.style.left = n.x + "px";
      nd.style.top = n.y + "px";
      lienzo.appendChild(nd);
    });
    requestAnimationFrame(function () { dibujarAristas(L); });
  }

  /* aristas (SVG) */

  var SVGNS = "http://www.w3.org/2000/svg";

  function puntoDe(elNodo, side, xPref) {
    var r = elNodo.getBoundingClientRect();
    var lr = lienzo.getBoundingClientRect();
    var x = r.left - lr.left, y = r.top - lr.top;
    if (side === "left") return { x: x, y: y + r.height / 2 };
    if (side === "right") return { x: x + r.width, y: y + r.height / 2 };
    if (side === "top") return { x: x + r.width / 2, y: y };
    if (side === "topX") return { x: xPref, y: y };
    return { x: x + r.width / 2, y: y + r.height }; /* bottom */
  }

  var DIRS = { left: [-1, 0], right: [1, 0], top: [0, -1], bottom: [0, 1], topX: [0, -1] };

  function dibujarAristas(L) {
    svg.innerHTML =
      '<defs><marker id="flecha" viewBox="0 0 10 10" refX="9" refY="5" ' +
      'markerWidth="7" markerHeight="7" orient="auto-start-reverse">' +
      '<path d="M0,0 L10,5 L0,10 z"/></marker></defs>';

    L.aristas.forEach(function (a) {
      var nf = lienzo.querySelector('[data-id="' + a.f + '"]');
      var nt = lienzo.querySelector('[data-id="' + a.t + '"]');
      if (!nf || !nt) return;
      var pf = puntoDe(nf, a.fs);
      pf.x += a.fdx || 0;
      var pt = puntoDe(nt, a.ts, pf.x);
      if (a.ts !== "topX") pt.x += a.tdx || 0;
      var k = Math.max(36, Math.min(140, Math.hypot(pt.x - pf.x, pt.y - pf.y) / 2.2));
      var c1 = { x: pf.x + DIRS[a.fs][0] * k, y: pf.y + DIRS[a.fs][1] * k };
      var c2 = { x: pt.x + DIRS[a.ts][0] * k, y: pt.y + DIRS[a.ts][1] * k };

      var p = document.createElementNS(SVGNS, "path");
      p.setAttribute("d", "M" + pf.x + " " + pf.y + " C" + c1.x + " " + c1.y + " " + c2.x + " " + c2.y + " " + pt.x + " " + pt.y);
      p.setAttribute("marker-end", "url(#flecha)");
      if (a.dash) p.setAttribute("class", "punteada");
      if (a.lbl) {
        var tp = document.createElementNS(SVGNS, "title");
        tp.textContent = a.lbl;
        p.appendChild(tp);
      }
      svg.appendChild(p);

      if (a.lblV) {
        var mx = (pf.x + 3 * c1.x + 3 * c2.x + pt.x) / 8;
        var my = (pf.y + 3 * c1.y + 3 * c2.y + pt.y) / 8;
        var t = document.createElementNS(SVGNS, "text");
        t.setAttribute("x", mx); t.setAttribute("y", my - 4);
        t.setAttribute("text-anchor", "middle");
        t.textContent = a.lbl;
        svg.appendChild(t);
      }
    });
  }

  /* ------------------------------- tooltip ------------------------------- */

  var tooltip = $("#tooltip"), hideTimer = null;

  function campoTooltip(dt, dd) {
    var f = document.createDocumentFragment();
    f.appendChild(el("dt", null, dt));
    var d = el("dd"); d.appendChild(dd); f.appendChild(d);
    return f;
  }

  function mostrarTooltip(id, ancla) {
    var c = COMP[id];
    if (!c) return;
    clearTimeout(hideTimer);
    tooltip.innerHTML = "";

    var h = el("h3", null, c.nombre);
    h.appendChild(document.createTextNode(" "));
    h.appendChild(badgeEstado(c.estado, true));
    tooltip.appendChild(h);
    tooltip.appendChild(el("p", null, c.resumen));

    var dl = el("dl");
    dl.appendChild(campoTooltip("Entrada → salida", document.createTextNode(c.entrada + " → " + c.salida)));
    dl.appendChild(campoTooltip("Restricción", document.createTextNode(c.restriccion)));
    if (c.archivos && c.archivos.length) {
      var ul = el("ul");
      ul.style.paddingLeft = "16px"; ul.style.margin = "0";
      c.archivos.forEach(function (a) {
        var li = el("li", "archivo", a.path);
        li.appendChild(el("span", "nota-archivo", a.nota));
        ul.appendChild(li);
      });
      dl.appendChild(campoTooltip("Archivos", ul));
    }
    dl.appendChild(campoTooltip("Recomendación", document.createTextNode(c.recomendacion)));
    dl.appendChild(campoTooltip("Cómo probar", document.createTextNode(c.comoProbar)));
    tooltip.appendChild(dl);
    tooltip.appendChild(chipsDe(c.decisiones));

    tooltip.hidden = false;
    posicionarTooltip(ancla);
  }

  function posicionarTooltip(ancla) {
    var r = ancla.getBoundingClientRect();
    var tw = tooltip.offsetWidth, th = tooltip.offsetHeight;
    var vw = window.innerWidth, vh = window.innerHeight;
    var x = r.right + 12, y = r.top;
    if (x + tw > vw - 8) x = r.left - tw - 12;              /* a la izquierda */
    if (x < 8) { x = Math.max(8, Math.min(r.left, vw - tw - 8)); y = r.bottom + 10; } /* abajo */
    if (y + th > vh - 8) y = Math.max(8, vh - th - 8);
    tooltip.style.left = x + "px";
    tooltip.style.top = y + "px";
  }

  function ocultarTooltip() { tooltip.hidden = true; }
  function programarOcultarTooltip() {
    clearTimeout(hideTimer);
    hideTimer = setTimeout(function () {
      if (!tooltip.matches(":hover")) ocultarTooltip();
    }, 140);
  }
  tooltip.addEventListener("mouseleave", ocultarTooltip);

  function bindNodo(nd, id) {
    nd.addEventListener("mouseenter", function () { mostrarTooltip(id, nd); });
    nd.addEventListener("mouseleave", programarOcultarTooltip);
    nd.addEventListener("focus", function () { mostrarTooltip(id, nd); });
    nd.addEventListener("blur", function (e) {
      if (!tooltip.contains(e.relatedTarget)) programarOcultarTooltip();
    });
    nd.addEventListener("click", function (e) {
      if (e.target.closest(".chip-d")) return;
      ocultarTooltip();
      abrirDrawer(id);
    });
    nd.addEventListener("keydown", function (e) {
      if (e.target !== nd) return;
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); abrirDrawer(id); }
      else if (e.key === "Escape") { ocultarTooltip(); }
    });
  }

  /* -------------------------------- drawer ------------------------------- */

  var drawer = $("#drawer"), velo = $("#velo"), drawerCuerpo = $("#drawer-cuerpo");
  var ultimoFoco = null;

  function campoDrawer(titulo, contenido) {
    var f = document.createDocumentFragment();
    f.appendChild(el("h3", null, titulo));
    if (typeof contenido === "string") f.appendChild(el("p", null, contenido));
    else f.appendChild(contenido);
    return f;
  }

  function abrirDrawer(id) {
    var c = COMP[id];
    if (!c) return;
    ultimoFoco = document.activeElement;

    $("#drawer-titulo").textContent = c.nombre;
    drawerCuerpo.innerHTML = "";

    var badges = el("p");
    badges.appendChild(el("span", "nodo-capa", c.capa));
    badges.appendChild(document.createTextNode(" "));
    badges.appendChild(badgeEstado(c.estado, false));
    drawerCuerpo.appendChild(badges);

    if (c.versiones && c.versiones.length) {
      var nombres = c.versiones.map(function (v) { return D.versiones[v] ? D.versiones[v].nombre : v; });
      drawerCuerpo.appendChild(el("p", "nota", "Aparece en: " + nombres.join(" · ")));
    }

    drawerCuerpo.appendChild(el("p", null, c.resumen));
    drawerCuerpo.appendChild(campoDrawer("Entrada", c.entrada));
    drawerCuerpo.appendChild(campoDrawer("Salida", c.salida));
    drawerCuerpo.appendChild(campoDrawer("Restricción", c.restriccion));
    if (c.detalleExtra) {
      var dx = el("div", "detalle-extra", c.detalleExtra);
      drawerCuerpo.appendChild(campoDrawer("Detalle", dx));
    }
    if (c.archivos && c.archivos.length) {
      var ul = el("ul");
      c.archivos.forEach(function (a) {
        var li = el("li", null);
        li.appendChild(el("span", "archivo", a.path));
        li.appendChild(el("span", "nota-archivo", a.nota));
        ul.appendChild(li);
      });
      drawerCuerpo.appendChild(campoDrawer("Archivos", ul));
    }
    drawerCuerpo.appendChild(campoDrawer("Recomendación", c.recomendacion));
    drawerCuerpo.appendChild(campoDrawer("Cómo probar", c.comoProbar));

    if (c.decisiones && c.decisiones.length) {
      var lista = el("div");
      c.decisiones.forEach(function (did) {
        var d = DEC[did];
        var item = el("div", "decision-item");
        item.appendChild(chipDec(did));
        if (d) {
          item.appendChild(el("span", "t", d.titulo));
          item.appendChild(badgeEstado(d.estado, true));
        }
        lista.appendChild(item);
      });
      drawerCuerpo.appendChild(campoDrawer("Decisiones que aplican", lista));
    }

    drawer.className = "drawer capa-" + c.capa;
    velo.hidden = false;
    drawer.hidden = false;
    $("#drawer-cerrar").focus();
  }

  function cerrarDrawer() {
    drawer.hidden = true;
    velo.hidden = true;
    if (ultimoFoco && ultimoFoco.focus) ultimoFoco.focus();
  }
  $("#drawer-cerrar").addEventListener("click", cerrarDrawer);
  velo.addEventListener("click", cerrarDrawer);

  /* --------------------------- modal de decisión ------------------------- */

  var modalVelo = $("#modal-velo"), modalCuerpo = $("#modal-cuerpo");
  var focoAntesModal = null;

  function abrirDecision(id) {
    var d = DEC[id];
    if (!d) return;
    focoAntesModal = document.activeElement;

    $("#modal-titulo").textContent = d.id + " — " + d.titulo;
    modalCuerpo.innerHTML = "";
    modalCuerpo.appendChild(badgeEstado(d.estado, false));
    modalCuerpo.appendChild(campoDrawer("Pregunta", d.pregunta));
    modalCuerpo.appendChild(campoDrawer("Detalle", d.detalle));
    if (d.bloqueadaPor) modalCuerpo.appendChild(campoDrawer("Bloqueada por", d.bloqueadaPor));
    if (d.desbloquea) modalCuerpo.appendChild(campoDrawer("Desbloquea", d.desbloquea));
    if (d.evidencia && d.evidencia.length) {
      var ul = el("ul", "evidencia");
      d.evidencia.forEach(function (ev) { ul.appendChild(el("li", null, ev)); });
      modalCuerpo.appendChild(campoDrawer("Evidencia", ul));
    }
    if (d.comoSeguir) modalCuerpo.appendChild(campoDrawer("Cómo seguir", d.comoSeguir));

    modalVelo.hidden = false;
    $("#modal-cerrar").focus();
  }

  function cerrarDecision() {
    modalVelo.hidden = true;
    if (focoAntesModal && focoAntesModal.focus) focoAntesModal.focus();
  }
  $("#modal-cerrar").addEventListener("click", cerrarDecision);
  modalVelo.addEventListener("click", function (e) {
    if (e.target === modalVelo) cerrarDecision();
  });

  /* chips: apertura global por delegación */
  document.addEventListener("click", function (e) {
    var chip = e.target.closest(".chip-d");
    if (chip && chip.dataset.dec) abrirDecision(chip.dataset.dec);
  });

  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    if (!modalVelo.hidden) cerrarDecision();
    else if (!drawer.hidden) cerrarDrawer();
    else ocultarTooltip();
  });

  /* re-dibujar aristas si cambia el layout (fuentes, zoom, etc.) */
  var rT = null;
  window.addEventListener("resize", function () {
    clearTimeout(rT);
    rT = setTimeout(function () { if (layoutActual) dibujarAristas(layoutActual); }, 150);
  });
  $(".lienzo-scroll").addEventListener("scroll", ocultarTooltip);

  /* -------------------------------- leyenda ------------------------------ */

  var leyenda = $("#leyenda");
  CAPAS_ORDEN.forEach(function (capa) {
    var li = el("li");
    li.appendChild(el("span", "punto capa-" + capa));
    li.appendChild(document.createTextNode(capa));
    leyenda.appendChild(li);
  });
  var liP = el("li");
  liP.appendChild(el("span", "punto punto-punteado"));
  liP.appendChild(document.createTextNode("registro (salida)"));
  leyenda.appendChild(liP);

  /* ------------------------- secciones inferiores ------------------------ */

  /* versiones (ambas tarjetas) */
  var tv = $("#tarjetas-versiones");
  ["slm", "cascada"].forEach(function (vid) {
    var art = el("article", "tarjeta-version");
    rellenarTarjetaVersion(art, D.versiones[vid]);
    tv.appendChild(art);
  });

  /* gamas */
  $("#gamas-nota").textContent = D.gamas.nota;
  tablaSimple("#tabla-gamas",
    ["Gama", "ASR", "Detector", "Techo RAM", "Hilos", "Nota"],
    D.gamas.tabla.map(function (g) {
      return [g.gama, g.asr, g.detector, g.techo, g.hilos, g.nota || "—"];
    }));
  $("#gamas-regla").textContent = D.gamas.regla;

  /* mediciones */
  $("#mediciones-nota").textContent = D.mediciones.nota;
  tablaSimple("#tabla-mediciones",
    ["Magnitud", "Marco teórico", "Medido en el lab", "Lectura"],
    D.mediciones.tabla.map(function (m) { return [m.que, m.marco, m.medido, m.lectura]; }));

  /* métricas y marcas temporales */
  (function () {
    var bm = $("#bloque-metricas");
    var gr = el("div", "marcas");
    D.metricas.marcas.concat(D.metricas.margenes).forEach(function (m) {
      var card = el("div", "marca");
      card.appendChild(el("div", "marca-id", m.id));
      card.appendChild(el("p", null, m.def));
      gr.appendChild(card);
    });
    bm.appendChild(gr);
    bm.appendChild(el("div", "preventiva", D.metricas.preventiva));
    var h = el("h3", "nota", "Evaluación");
    bm.appendChild(h);
    var ul = el("ul", "lista-eval");
    D.metricas.evaluacion.forEach(function (e) { ul.appendChild(el("li", null, e)); });
    bm.appendChild(ul);
  })();

  /* taxonomía 6+6 */
  $("#taxonomia-nota").textContent = D.taxonomia.nota;
  (function () {
    var cont = $("#taxonomia-capas");
    [D.taxonomia.capa1, D.taxonomia.capa2].forEach(function (capa) {
      var col = el("div", "capa-tax");
      col.appendChild(el("h3", null, capa.nombre));
      capa.etiquetas.forEach(function (et) {
        var d = el("div", "etiqueta");
        var idSpan = el("span", "etiqueta-id", et.id);
        if (et.enReglas) idSpan.appendChild(el("span", "badge-rules", "en rules.py"));
        d.appendChild(idSpan);
        d.appendChild(el("p", "si", "Dispara: " + et.dispara));
        d.appendChild(el("p", "no", "No dispara: " + et.noDispara));
        col.appendChild(d);
      });
      cont.appendChild(col);
    });
  })();

  /* escalera de avisos + mockups */
  tablaSimple("#tabla-escalera",
    ["Nivel", "Cuándo", "Qué ve la persona", "Histéresis"],
    D.escalera.map(function (e) { return [e.nivel, e.cuando, e.ve, e.histeresis]; }));

  (function () {
    var gm = $("#mockups");
    D.mockups.forEach(function (m) {
      var tel = el("div", "telefono");
      var av = el("div", "aviso");
      av.appendChild(el("span", "aviso-nivel", m.nivel));
      av.appendChild(el("div", "aviso-titulo", m.titulo));
      var p1 = el("p"); p1.appendChild(el("span", "lbl", "Qué pasa")); p1.appendChild(document.createTextNode(m.que));
      var p2 = el("p"); p2.appendChild(el("span", "lbl", "Por qué")); p2.appendChild(document.createTextNode(m.porque));
      var p3 = el("p"); p3.appendChild(el("span", "lbl", "Qué hacer")); p3.appendChild(document.createTextNode(m.hacer));
      av.appendChild(p1); av.appendChild(p2); av.appendChild(p3);
      av.appendChild(el("div", "aviso-btn", m.boton));
      tel.appendChild(av);
      tel.appendChild(el("p", "mockup-leyenda", "Mockup propuesto — " + m.nivel));
      gm.appendChild(tel);
    });
  })();

  /* mapa de archivos del laboratorio */
  $("#laboratorio-nota").textContent = D.laboratorio.nota;
  tablaSimple("#tabla-laboratorio",
    ["Archivo", "Qué hace"],
    D.laboratorio.archivos.map(function (a) { return [a.path, a.que]; }),
    [true, false]);

  /* en simple */
  (function () {
    var ul = $("#lista-simple");
    D.enSimple.forEach(function (s) { ul.appendChild(el("li", null, s)); });
  })();

  /* decisiones emergentes */
  tablaSimple("#tabla-emergentes",
    ["ID", "Pregunta abierta", "Relacionada con"],
    D.decisionesEmergentes.map(function (e) { return [e.id, e.pregunta, e.relacion]; }),
    [true, false, false]);

  /* footer: fuentes */
  (function () {
    var ul = $("#lista-fuentes");
    D.fuentes.forEach(function (f) {
      var li = el("li");
      var a = el("a", null, f.path);
      a.href = f.path;
      li.appendChild(a);
      li.appendChild(el("span", "que", " — " + f.que));
      ul.appendChild(li);
    });
  })();

  function tablaSimple(sel, encabezados, filas, monoCols) {
    var t = $(sel);
    var thead = el("thead"), trh = el("tr");
    encabezados.forEach(function (h) { trh.appendChild(el("th", null, h)); });
    thead.appendChild(trh);
    var tbody = el("tbody");
    filas.forEach(function (f) {
      var tr = el("tr");
      f.forEach(function (celda, i) {
        tr.appendChild(el("td", monoCols && monoCols[i] ? "mono" : null, celda));
      });
      tbody.appendChild(tr);
    });
    t.appendChild(thead);
    t.appendChild(tbody);
  }

  /* --------------------------------- init -------------------------------- */

  var vIni = (location.search.match(/[?&]v=(slm|cascada)/) || [])[1] || "slm";
  setVersion(vIni);
})();
