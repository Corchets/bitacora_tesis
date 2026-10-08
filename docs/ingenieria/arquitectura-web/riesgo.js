/* ============================================================================
 * riesgo.js — Simulador de riesgo y falsas alarmas
 * Todo el contenido sale de window.DATOS (datos.js). Sin dependencias.
 * ==========================================================================*/
(function () {
  "use strict";

  var D = window.DATOS;
  if (!D || !D.simulador) {
    document.body.insertAdjacentHTML(
      "afterbegin",
      '<p class="sinjs">No se encontró window.DATOS: falta cargar datos.js.</p>'
    );
    return;
  }

  var SIM = D.simulador;
  var SVGNS = "http://www.w3.org/2000/svg";

  /* ---------- helpers ---------- */
  function h(tag, attrs, kids) {
    var e = document.createElement(tag);
    if (attrs) {
      for (var k in attrs) {
        if (attrs[k] == null || attrs[k] === false) continue;
        if (k === "text") e.textContent = attrs[k];
        else if (k === "html") e.innerHTML = attrs[k];
        else e.setAttribute(k, attrs[k]);
      }
    }
    (kids || []).forEach(function (c) {
      if (c == null) return;
      e.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
    });
    return e;
  }
  function s(tag, attrs, kids) {
    var e = document.createElementNS(SVGNS, tag);
    if (attrs) for (var k in attrs) e.setAttribute(k, attrs[k]);
    (kids || []).forEach(function (c) { if (c) e.appendChild(c); });
    return e;
  }
  function num(v, d) {
    if (v == null) return "—";
    return (+v).toFixed(d == null ? 2 : d).replace(".", ",");
  }
  function pct(v, d) { return num(v * 100, d == null ? 1 : d) + "%"; }
  function $(id) { return document.getElementById(id); }
  function tabla(headers, rows, opts) {
    opts = opts || {};
    var t = h("table");
    if (opts.caption) t.appendChild(h("caption", { text: opts.caption }));
    var tr = h("tr");
    headers.forEach(function (hd, i) {
      tr.appendChild(h("th", { text: hd, class: opts.numCols && opts.numCols.indexOf(i) >= 0 ? "num" : null }));
    });
    t.appendChild(h("thead", null, [tr]));
    var tb = h("tbody");
    rows.forEach(function (r) { tb.appendChild(r); });
    t.appendChild(tb);
    return t;
  }
  function fila(cells, cls, numCols) {
    var tr = h("tr", cls ? { class: cls } : null);
    cells.forEach(function (c, i) {
      var td = h("td", numCols && numCols.indexOf(i) >= 0 ? { class: "num" } : null);
      if (c == null) td.textContent = "—";
      else if (typeof c === "string" || typeof c === "number") td.textContent = c;
      else td.appendChild(c);
      tr.appendChild(td);
    });
    return tr;
  }

  /* ==========================================================================
   * HEADER
   * ========================================================================*/
  $("badge-estado").appendChild(h("span", {
    html: "Valores de llamadas sintéticas y coeficientes elegidos a mano — <strong>prueban el mecanismo, no miden rendimiento</strong>."
  }));

  /* ==========================================================================
   * 1. TRAZA DE LLAMADA — gráfico SVG riesgo vs tiempo
   * ========================================================================*/
  var W = 900, H = 360, ML = 48, MR = 16, MT = 22, MB = 66;
  var XMAX = 220, YMAX = 1;
  var PW = W - ML - MR, PH = H - MT - MB;
  var EV_Y = MT + PH + 24;            // carril de eventos
  var XLAB_Y = MT + PH + 52;          // etiquetas del eje X
  function x(t) { return ML + (t / XMAX) * PW; }
  function y(v) { return MT + (1 - v / YMAX) * PH; }

  var svg = $("chart");
  svg.setAttribute("viewBox", "0 0 " + W + " " + H);
  var wrap = $("chart-wrap");
  var tip = $("tooltip");

  function showTip(html, sx, sy) {
    tip.innerHTML = html;
    tip.hidden = false;
    var r = svg.getBoundingClientRect();
    var wr = wrap.getBoundingClientRect();
    var px = r.left - wr.left + (sx / W) * r.width + wrap.scrollLeft;
    var py = r.top - wr.top + (sy / H) * r.height;
    tip.style.left = px + "px";
    if (sy < 110) {  // cerca del borde superior: el tooltip cae hacia abajo
      tip.style.top = py + 14 + "px";
      tip.style.transform = "translate(-50%, 0)";
    } else {
      tip.style.top = py - 10 + "px";
      tip.style.transform = "translate(-50%, -100%)";
    }
  }
  function hideTip() { tip.hidden = true; }

  /* ----- rejilla y ejes ----- */
  [0, 0.25, 0.5, 0.75, 1].forEach(function (v) {
    svg.appendChild(s("line", {
      x1: ML, x2: W - MR, y1: y(v), y2: y(v),
      class: v === 0 ? "eje" : "grid"
    }));
    svg.appendChild(s("text", {
      x: ML - 7, y: y(v) + 4, "text-anchor": "end", class: "eje-txt"
    }, [document.createTextNode(v === 0 ? "0" : v === 1 ? "1" : num(v))]));
  });
  for (var t = 0; t <= 210; t += 30) {
    svg.appendChild(s("line", { x1: x(t), x2: x(t), y1: MT + PH, y2: MT + PH + 5, class: "eje" }));
    svg.appendChild(s("text", {
      x: x(t), y: XLAB_Y, "text-anchor": "middle", class: "eje-txt"
    }, [document.createTextNode(t)]));
  }
  svg.appendChild(s("line", { x1: ML, x2: ML, y1: MT, y2: MT + PH, class: "eje" }));
  svg.appendChild(s("text", {
    x: W - MR, y: XLAB_Y, "text-anchor": "end", class: "eje-txt"
  }, [document.createTextNode("segundos →")]));
  svg.appendChild(s("text", {
    x: 8, y: MT - 8, class: "eje-txt"
  }, [document.createTextNode("riesgo S_t")]));

  /* ----- umbrales (etiquetas a la izquierda: la derecha está ocupada por las trazas) ----- */
  [{ v: 0.75, lab: "θ_high ≈ 0,75 — enciende" }, { v: 0.40, lab: "θ_low ≈ 0,40 — apaga" }].forEach(function (u) {
    svg.appendChild(s("line", { x1: ML, x2: W - MR, y1: y(u.v), y2: y(u.v), class: "umbral" }));
    svg.appendChild(s("text", {
      x: ML + 6, y: y(u.v) - 5, "text-anchor": "start", class: "umbral-txt"
    }, [document.createTextNode(u.lab)]));
  });

  /* ----- marcas T_R (etiqueta arriba) y T_C (abajo: arriba choca con la traza) ----- */
  [{ t: 185, id: "T_R", cls: "tr", ly: MT + 11, anchor: "end", dx: -6 },
   { t: 200, id: "T_C", cls: "tc", ly: MT + PH - 6, anchor: "start", dx: 6 }].forEach(function (m) {
    svg.appendChild(s("line", {
      x1: x(m.t), x2: x(m.t), y1: MT, y2: MT + PH,
      class: "marca-linea marca-" + m.cls
    }));
    svg.appendChild(s("text", {
      x: x(m.t) + m.dx, y: m.ly,
      "text-anchor": m.anchor,
      class: "marca-txt " + m.cls
    }, [document.createTextNode(m.id + " · " + m.t + " s")]));
  });

  /* ----- series S_t (escalón: el valor se sostiene hasta la próxima revisión) ----- */
  var grupos = {};
  ["informe", "corregido"].forEach(function (key) {
    var tr = SIM.trazas[key];
    var pts = tr.puntos;
    var g = s("g", { class: "serie-g " + key });
    var d = "M " + x(pts[0].t) + " " + y(pts[0].s);
    for (var i = 1; i < pts.length; i++) {
      d += " H " + x(pts[i].t) + " V " + y(pts[i].s);
    }
    d += " H " + x(XMAX);  // se sostiene hasta el fin del eje
    g.appendChild(s("path", { d: d, class: "serie " + key }));

    pts.forEach(function (p) {
      if (p.alerta) {
        g.appendChild(s("circle", {
          cx: x(p.t), cy: y(p.s), r: 9, class: "punto-alerta",
          stroke: key === "informe" ? "var(--violeta)" : "var(--teal)"
        }));
        var lbl = s("text", {
          x: x(p.t) - 8, y: y(p.s) + (key === "informe" ? 20 : -10),
          "text-anchor": "end", class: "ta-txt " + key
        }, [document.createTextNode("T_A = " + p.t + " s")]);
        g.appendChild(lbl);
      }
      var gc = s("g", { tabindex: "0", role: "button", class: "ev", "aria-label": "Punto de la traza " + tr.nombre + ": t " + p.t + " segundos, S " + num(p.s) });
      gc.appendChild(s("circle", { cx: x(p.t), cy: y(p.s), r: 4.5, class: "punto " + key }));
      var html = '<div class="tt-t">' + tr.nombre + '</div>' +
        '<div class="tt-meta">t = ' + p.t + ' s</div>' +
        'M = ' + num(p.m) + ' · C = ' + num(p.c) + ' → <strong>S = ' + num(p.s) + '</strong>' +
        (p.alerta ? '<br><span class="tt-marca">T_A — alerta sostenida</span>' : '');
      gc.addEventListener("mouseenter", function () { showTip(html, x(p.t), y(p.s)); });
      gc.addEventListener("mouseleave", hideTip);
      gc.addEventListener("focus", function () { showTip(html, x(p.t), y(p.s)); });
      gc.addEventListener("blur", hideTip);
      g.appendChild(gc);
    });
    svg.appendChild(g);
    grupos[key] = g;
  });

  /* ----- eventos de la llamada sobre el eje ----- */
  var ROL = { A: "Atacante", V: "Víctima" };
  SIM.llamadaEstafa.forEach(function (ev) {
    var g = s("g", {
      tabindex: "0", role: "button",
      class: "ev rol-" + ev.rol,
      "aria-label": "Segundo " + ev.t + ", " + ROL[ev.rol] + ", " + ev.evento + (ev.marca ? ", marca " + ev.marca : "")
    });
    if (ev.marca) {
      g.appendChild(s("circle", { cx: x(ev.t), cy: EV_Y, r: 8.5, class: "ev-ring", stroke: ev.rol === "A" ? "var(--ladrillo)" : "var(--teal)" }));
    }
    g.appendChild(s("circle", { cx: x(ev.t), cy: EV_Y, r: 5.5 }));
    var html = '<div class="tt-t">' + ev.evento.replace(/_/g, " ") + '</div>' +
      '<div class="tt-meta">t = ' + ev.t + ' s · ' + ROL[ev.rol] + '</div>' +
      ev.texto +
      (ev.marca ? '<br><span class="tt-marca">' + ev.marca + '</span>' : '');
    g.addEventListener("mouseenter", function () { showTip(html, x(ev.t), EV_Y); });
    g.addEventListener("mouseleave", hideTip);
    g.addEventListener("focus", function () { showTip(html, x(ev.t), EV_Y); });
    g.addEventListener("blur", hideTip);
    g.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); showTip(html, x(ev.t), EV_Y); }
      if (e.key === "Escape") hideTip();
    });
    svg.appendChild(g);
  });
  svg.appendChild(s("text", {
    x: W - MR, y: EV_Y + 4, "text-anchor": "end", class: "eje-txt"
  }, [document.createTextNode("← hechos")]));

  /* ----- leyenda con toggles ----- */
  var ley = $("leyenda");
  ["informe", "corregido"].forEach(function (key) {
    var b = h("button", {
      type: "button", class: "ley-toggle", "aria-pressed": "true",
      "aria-label": "Mostrar u ocultar la traza " + SIM.trazas[key].nombre
    });
    b.appendChild(h("span", { class: "ley-muestra " + key }));
    b.appendChild(h("span", { text: SIM.trazas[key].nombre }));
    b.addEventListener("click", function () {
      var on = b.getAttribute("aria-pressed") === "true";
      b.setAttribute("aria-pressed", String(!on));
      grupos[key].setAttribute("visibility", on ? "hidden" : "visible");
    });
    ley.appendChild(b);
  });
  [["umbral", "θ_high / θ_low"], ["rolA", "hecho del atacante"], ["rolV", "hecho de la víctima"]].forEach(function (it) {
    var sp = h("span", { class: "ley-item" });
    sp.appendChild(h("span", { class: "ley-muestra " + it[0] }));
    sp.appendChild(h("span", { text: it[1] }));
    ley.appendChild(sp);
  });

  /* ----- cards de resultado de cada traza ----- */
  var cards = $("traza-cards");
  [{ key: "informe", cls: "borde-violeta" }, { key: "corregido", cls: "borde-teal" }].forEach(function (it) {
    var tr = SIM.trazas[it.key];
    cards.appendChild(h("div", { class: "card " + it.cls }, [
      h("h4", { text: tr.nombre }),
      h("p", { text: tr.resultado })
    ]));
  });

  /* ----- tabla de controles ----- */
  $("controles-tabla").appendChild(tabla(
    ["Caso de control", "Riesgo máximo", "Resultado"],
    SIM.controles.map(function (c) {
      return fila([c.caso, num(c.riesgoMax), c.resultado], null, [1]);
    })
  ));
  $("nota-traza").textContent = "Los segundos salen de una llamada inventada; lo que se sostiene es el mecanismo.";

  /* ==========================================================================
   * 2. REGISTRO DE EVENTOS — peso con decaimiento por vida media
   * ========================================================================*/
  var hmap = {};
  SIM.vidasMedias.forEach(function (v) { hmap[v.tipo] = v.h; });

  var regTbody = h("tbody");
  var regFilas = SIM.llamadaEstafa.map(function (ev, i) {
    var pesoTd = h("td", { class: "num" }, [h("span", { class: "peso-val", text: "—" })]);
    var tr = h("tr");
    [i + 1, ev.t + " s"].forEach(function (c) { tr.appendChild(h("td", { text: String(c) })); });
    var rolTd = h("td");
    rolTd.appendChild(h("span", { class: "rol-chip rol-" + ev.rol, text: ev.rol, title: ROL[ev.rol] }));
    rolTd.appendChild(document.createTextNode(" " + ROL[ev.rol]));
    tr.appendChild(rolTd);
    tr.appendChild(h("td", { text: ev.evento }));
    var txtTd = h("td"); txtTd.appendChild(h("span", { class: "ev-texto", text: ev.texto }));
    tr.appendChild(txtTd);
    var marcaTd = h("td");
    if (ev.marca) marcaTd.appendChild(h("span", { class: "marca-chip", text: ev.marca }));
    tr.appendChild(marcaTd);
    tr.appendChild(pesoTd);
    regTbody.appendChild(tr);
    return { tr: tr, td: pesoTd, ev: ev };
  });
  var regTabla = h("table");
  regTabla.appendChild(h("thead", null, [filaTh(["k", "t", "Rol", "Evento", "Qué dijo", "Marca", "Peso"])]));
  regTabla.appendChild(regTbody);
  $("registro-tabla").appendChild(regTabla);
  function filaTh(cells) {
    var tr = h("tr");
    cells.forEach(function (c, i) { tr.appendChild(h("th", { text: c, class: i === 6 ? "num" : null })); });
    return tr;
  }

  function actualizarRegistro(now) {
    $("out-tiempo").textContent = "t = " + now + " s";
    var activos = 0;
    regFilas.forEach(function (f) {
      var ev = f.ev, hh = hmap[ev.evento], span = f.td.firstChild;
      f.tr.classList.remove("fila-activa", "fila-futura");
      if (ev.t > now) {
        f.tr.classList.add("fila-futura");
        span.textContent = "—";
        f.td.title = "Todavía no ocurrió a t = " + now + " s";
      } else if (hh == null) {
        span.textContent = "—";
        f.td.title = "Sin vida media definida para " + ev.evento;
      } else {
        var w = Math.pow(0.5, (now - ev.t) / hh);
        span.textContent = num(w);
        f.td.title = "0,5^((" + now + " − " + ev.t + ") / " + hh + ")";
        if (w > 0.2) { f.tr.classList.add("fila-activa"); activos++; }
      }
    });
    $("pesos-resumen").innerHTML = "";
    $("pesos-resumen").appendChild(h("span", {
      html: "A t = " + now + " s hay <strong>" + activos + " hechos con peso &gt; 0,2</strong> — esos son los que todavía cuentan en el score."
    }));
  }
  var sliderT = $("slider-tiempo");
  sliderT.addEventListener("input", function () { actualizarRegistro(+sliderT.value); });
  actualizarRegistro(+sliderT.value);

  /* ----- vidas medias ----- */
  var colsVida = Object.keys(SIM.vidasMedias[0].pesos);
  $("vidas-tabla").appendChild(tabla(
    ["Tipo de evento", "h (s)"].concat(colsVida),
    SIM.vidasMedias.map(function (v) {
      return fila([v.tipo, v.h].concat(colsVida.map(function (k) { return num(v.pesos[k]); })), null,
        [1, 2, 3, 4, 5, 6, 7]);
    }),
    { numCols: [1, 2, 3, 4, 5, 6, 7] }
  ));

  /* ----- indicadores κ Ω δ ----- */
  var ind = $("indicadores-cards");
  SIM.indicadores.forEach(function (ind_) {
    var kids = [
      h("span", { class: "ind-simbolo", text: ind_.id }),
      h("h4", { text: ind_.nombre }),
      h("code", { class: "ind-formula", text: ind_.formula }),
      h("p", { class: "ind-pregunta", text: ind_.pregunta })
    ];
    if (ind_.guion) kids.push(h("p", { class: "ind-guion", text: "Guion: " + ind_.guion }));
    if (ind_.nota) kids.push(h("p", { class: "ind-nota", text: ind_.nota }));
    ind.appendChild(h("div", { class: "card borde-teal" }, kids));
  });

  /* ==========================================================================
   * 3. FÓRMULA DE RIESGO
   * ========================================================================*/
  var FR = SIM.formulaRiesgo;
  var eqg = $("formula-bloques");
  [
    { t: "Manipulación acumulada", txt: FR.M },
    { t: "Pedido — escalada", txt: FR.C },
    { t: "Score combinado", txt: FR.S },
    { t: "Umbrales", txt: FR.umbrales, cls: "umbrales" }
  ].forEach(function (b) {
    eqg.appendChild(h("div", { class: "eq-card" + (b.cls ? " " + b.cls : "") }, [
      h("h4", { text: b.t }),
      h("p", { class: "eq-txt", text: b.txt })
    ]));
  });

  $("tabla-casos").appendChild(tabla(
    ["Caso", "M", "C", "crudo (antes de σ)", "S_t"],
    FR.tablaCasos.map(function (c) {
      var tr = fila([c.caso, num(c.m), num(c.c), num(c.crudo)], null, [1, 2, 3]);
      var sTd = h("td", { class: "s-cell", text: num(c.s) });
      sTd.style.background = "rgba(160, 58, 46, " + (0.05 + c.s * 0.8).toFixed(2) + ")";
      if (c.s > 0.55) sTd.style.color = "#fff";
      tr.appendChild(sTd);
      return tr;
    }),
    { numCols: [1, 2, 3, 4] }
  ));

  /* ==========================================================================
   * 4. CALCULADORA DE FALSAS ALARMAS
   * ========================================================================*/
  var FA = SIM.falsasAlarmas;
  $("calc-formula").textContent = FA.formula;
  var inP = $("in-p"), inCad = $("in-cad"), inDur = $("in-dur");

  function calcular() {
    var p = +inP.value, cad = +inCad.value, dur = +inDur.value;
    var N = dur * 60 / cad;
    var P = 1 - Math.pow(1 - p / 100, N);
    $("out-p").textContent = "p = " + num(p, 1) + "% de error";
    $("out-cad").textContent = "cada " + cad + " s";
    $("out-dur").textContent = dur + " min";
    $("calc-n").textContent = "N = " + dur + " min / " + cad + " s = " + num(N, 0) + " revisiones";
    $("calc-p").textContent = "≈ " + pct(P, 1);
    marcarCeldaViva(cad, p);
  }
  [inP, inCad, inDur].forEach(function (i) { i.addEventListener("input", calcular); });

  /* ----- tabla de cadencia (fija) + celda viva ----- */
  var CAD_SEGS = [5, 10, 15, 30, 60];       // filas de tablaCadencia, en orden
  var P_COLS = [0.1, 0.5, 1, 2];            // columnas 99,9 / 99,5 / 99 / 98 % acierto
  var TC = FA.tablaCadencia;
  var cadTbody = h("tbody");
  var cadCeldas = TC.filas.map(function (f) {
    var tr = h("tr");
    f.forEach(function (c, i) {
      var td = h("td", { text: String(c), class: i >= 1 ? "num" : null });
      tr.appendChild(td);
    });
    cadTbody.appendChild(tr);
    return tr;
  });
  var tablaCad = h("table");
  tablaCad.appendChild(h("thead", null, [filaTh(TC.encabezados)]));
  tablaCad.appendChild(cadTbody);
  $("tabla-cadencia").appendChild(tablaCad);

  function marcarCeldaViva(cad, p) {
    cadCeldas.forEach(function (tr) {
      for (var i = 1; i < tr.children.length; i++) tr.children[i].classList.remove("celda-viva");
    });
    var fi = CAD_SEGS.indexOf(cad);
    var ci = P_COLS.findIndex(function (pc) { return Math.abs(pc - p) < 0.05; });
    if (fi >= 0 && ci >= 0) {
      // col 0 = cadencia, col 1 = N; las columnas de acierto arrancan en 2
      cadCeldas[fi].children[2 + ci].classList.add("celda-viva");
    }
  }
  calcular();

  /* ----- margen de aceptación ----- */
  $("tabla-margen").appendChild(tabla(
    ["Llamadas legítimas con alerta toleradas", "Revisando cada 15 s", "Revisando cada 60 s"],
    FA.margenAceptacion.map(function (m) { return fila([m.tolera, m.cada15, m.cada60]); })
  ));

  /* ----- regla de persistencia ----- */
  var RD = FA.reglaDosSeguidas;
  $("tabla-regla").appendChild(tabla(
    RD.encabezados,
    RD.filas.map(function (f) { return fila(f, null, [1, 2, 3, 4]); })
  ));
  $("nota-regla").textContent = RD.nota + ".";

  /* ==========================================================================
   * 5. ESCALERA DE AVISOS + MOCKUPS
   * ========================================================================*/
  var esc = $("escalera-cards");
  D.escalera.forEach(function (n, i) {
    var hist = n.histeresis.indexOf("Sí") === 0 ? "si" : "no";
    esc.appendChild(h("div", { class: "esc-nivel n" + (i + 1) }, [
      h("h4", { text: "Nivel " + (i + 1) + " — " + n.nivel }),
      h("p", null, [h("span", { class: "esc-label", text: "Cuándo dispara · " }), document.createTextNode(n.cuando)]),
      h("p", null, [h("span", { class: "esc-label", text: "Qué ve la persona · " }), document.createTextNode(n.ve)]),
      h("p", null, [
        h("span", { class: "esc-label", text: "Histéresis · " }),
        h("span", { class: "hist-pill " + hist, text: n.histeresis })
      ])
    ]));
  });

  var mk = $("mockups");
  D.mockups.forEach(function (m) {
    var moderado = /moderado/i.test(m.nivel);
    mk.appendChild(h("div", { class: "telefono" }, [
      h("div", { class: "aviso" + (moderado ? " moderado" : "") }, [
        h("p", { class: "nivel", text: m.nivel }),
        h("h4", { text: m.titulo }),
        h("p", { text: m.que }),
        h("p", { class: "porque", text: m.porque }),
        h("p", { class: "hacer", text: m.hacer }),
        h("span", { class: "mock-btn", text: m.boton })
      ])
    ]));
  });

  /* ==========================================================================
   * 6. VENTANA VS DECAIMIENTO
   * ========================================================================*/
  var V = SIM.ventana;
  var vg = $("ventana-tablas");
  [
    { datos: V.sinVentana, cap: "Sin ventana — todo el historial pesa igual" },
    { datos: V.conVentana, cap: "Con ventana deslizante de 300 s" }
  ].forEach(function (cfg) {
    var rows = cfg.datos.map(function (r) {
      var alerta = /ALERTA/.test(r.que);
      var que = r.que
        ? h("span", { text: r.que })
        : h("span", { class: "que-vacia", text: "—" });
      return fila([r.min, num(r.k), num(r.o), num(r.m), num(r.s), que],
        alerta ? "fila-alerta" : null, [1, 2, 3, 4]);
    });
    var div = h("div", { class: "tabla-scroll" });
    div.appendChild(tabla(["min", "κ", "Ω", "M_t", "S_t", "Qué pasa"], rows,
      { caption: cfg.cap, numCols: [1, 2, 3, 4] }));
    vg.appendChild(div);
  });
  $("nota-ventana").textContent = V.nota;

  /* ==========================================================================
   * 7. DECISIONES RELACIONADAS
   * ========================================================================*/
  var IDS = ["D04", "D07", "D08", "D09"];
  var ESTADO_TXT = { resuelto: "Resuelta", parcial: "Parcial", abierto: "Abierta", propuesta: "Propuesta sin discutir" };
  var chips = $("chips-decisiones");
  IDS.forEach(function (id) {
    var d = D.decisiones.find(function (dd) { return dd.id === id; });
    if (!d) return;
    var b = h("button", { type: "button", class: "chip-d", "aria-haspopup": "dialog" });
    b.appendChild(h("span", { class: "estado-dot " + d.estado, title: ESTADO_TXT[d.estado] || d.estado }));
    var txt = h("span");
    txt.appendChild(h("span", { class: "chip-id", text: d.id }));
    txt.appendChild(h("span", { class: "chip-txt", text: " " + d.titulo }));
    b.appendChild(txt);
    b.addEventListener("click", function () { abrirPanel(d, b); });
    chips.appendChild(b);
  });

  var overlay = $("panel-overlay");
  var ultimoFoco = null;
  function bloque(titulo, contenido) {
    if (!contenido) return null;
    var div = h("div", { class: "p-bloque" }, [h("h5", { text: titulo })]);
    if (Array.isArray(contenido)) {
      var ul = h("ul");
      contenido.forEach(function (c) { ul.appendChild(h("li", { class: "p-ev", text: c })); });
      div.appendChild(ul);
    } else {
      div.appendChild(h("p", { text: contenido }));
    }
    return div;
  }
  function abrirPanel(d, origen) {
    ultimoFoco = origen;
    var c = $("panel-contenido");
    c.innerHTML = "";
    c.appendChild(h("h3", { text: "Decisión del mapa (MAPA-DECISIONES.md)", id: "panel-titulo" }));
    c.appendChild(h("p", { class: "p-id", text: d.id }));
    c.appendChild(h("p", { class: "p-titulo", text: d.titulo }));
    c.appendChild(h("span", { class: "estado-pill " + d.estado, text: ESTADO_TXT[d.estado] || d.estado }));
    [
      bloque("Pregunta que decide", d.pregunta),
      bloque("Detalle y estado actual", d.detalle),
      bloque("Bloqueada por", d.bloqueadaPor),
      bloque("Desbloquea", d.desbloquea),
      bloque("Evidencia", d.evidencia),
      bloque("Cómo seguir", d.comoSeguir)
    ].forEach(function (b) { if (b) c.appendChild(b); });
    overlay.hidden = false;
    $("panel-cerrar").focus();
  }
  function cerrarPanel() {
    overlay.hidden = true;
    if (ultimoFoco) ultimoFoco.focus();
  }
  $("panel-cerrar").addEventListener("click", cerrarPanel);
  overlay.addEventListener("click", function (e) { if (e.target === overlay) cerrarPanel(); });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") { if (!overlay.hidden) cerrarPanel(); hideTip(); }
  });

  /* ==========================================================================
   * FOOTER
   * ========================================================================*/
  var RELEVANTES = /VENTANA-DE-CONTEXTO|METRICAS\.md|DISENO-INTEGRADO/;
  var fl = $("fuentes-list");
  D.fuentes.filter(function (f) { return RELEVANTES.test(f.path); }).forEach(function (f) {
    fl.appendChild(h("li", null, [
      h("span", { class: "f-path", text: f.path }),
      document.createTextNode(" — " + f.que)
    ]));
  });
  $("pie-meta").textContent = "Visualización generada el " + D.meta.fecha + ". " + D.meta.notaEstado;
})();
