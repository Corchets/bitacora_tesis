/* ============================================================================
 * canon.js — Decisiones canónicas para la visualización.
 *
 * El build de ayuda-memoria genera dist/data.json con:
 *   - `adoption.decisions`: parse del MAPA-DECISIONES.md del árbol de trabajo
 *     (fuente adoptada localmente, PR #58, 2026-10-08). ES LA FUENTE CANÓNICA:
 *     el panel de decisión muestra su contenido completo (pregunta, detalle,
 *     bloqueadaPor, desbloquea, evidencia, comoSeguir), no una copia de datos.js.
 *   - `branches[].decisions`: parse del MAPA de cada rama remota (snapshot).
 *
 * Prioridad: adopción local > decisiones de la rama elegida > editorial datos.js.
 * Así los estados de main remoto nunca pisan lo adoptado en esta rama.
 *
 * Expone:
 *   window.DECISIONES_CANONICAS: Promise<Canon|null>
 *   window.aplicarDecisionesCanonicas(canon, DEC): reescribe los campos de DEC
 *     con el contenido canónico; conserva como `editorial*` los campos del PR
 *     que el MAPA no cubre.
 * ==========================================================================*/
(function () {
  "use strict";

  /* Clasifica el campo **Estado:** del MAPA en el vocabulario de badges:
   * resuelto | parcial | abierto | propuesta. */
  function clasificar(texto, open) {
    var s = (texto || "").toLowerCase();
    /* El primer término manda: "abierta … registró cerrada" es abierta. */
    if (/abiert/.test(s)) return "abierto";
    if (/propuesta/.test(s)) return "propuesta";
    if (/parcial|en curso|inicial|ratificad|pendiente/.test(s)) return "parcial";
    if (/resuelt|cerrad/.test(s)) return "resuelto";
    return open ? "abierto" : "resuelto";
  }

  function mapDecisions(list) {
    var out = {};
    (list || []).forEach(function (d) {
      out[d.id] = {
        titulo: d.title,
        estado: clasificar(d.state, d.open),
        texto: d.state,
        pregunta: d.pregunta || "",
        detalle: d.detalle || "",
        bloqueadaPor: d.bloqueadaPor || "",
        desbloquea: d.desbloquea || "",
        evidencia: d.evidencia || "",
        comoSeguir: d.comoSeguir || "",
        paraCerrar: d.paraCerrar || ""
      };
    });
    return out;
  }

  window.DECISIONES_CANONICAS = (async function () {
    try {
      var res = await fetch("../data.json", { cache: "no-store" });
      if (!res.ok) return null;
      var data = await res.json();
      var issues = {};
      (data.issues || []).forEach(function (i) {
        issues[i.number] = { title: i.title, state: i.state };
      });
      /* 1) Adopción local: el MAPA del árbol de trabajo integrado por PR #58. */
      if (data.adoption && data.adoption.decisions && data.adoption.decisions.length) {
        return { fuente: data.adoption.source, local: true, decisiones: mapDecisions(data.adoption.decisions), issues: issues };
      }
      /* 2) Decisiones de la rama elegida (snapshot remoto). */
      var params = new URLSearchParams(location.search);
      var rama = params.get("rama") || data.defaultBranch;
      var b = (data.branches || []).find(function (x) { return x.name === rama; }) || data.branches[0];
      if (!b || !b.decisions) return null;
      return { fuente: "docs/gestion/MAPA-DECISIONES.md @" + b.name + " · " + (b.sha || "").slice(0, 7),
        local: false, decisiones: mapDecisions(b.decisions), issues: issues };
    } catch (e) {
      return null;
    }
  })();

  /* Rellena DEC (índice id → {id, issues}) con el contenido canónico del MAPA
   * adoptado. datos.js ya no lleva una tabla editorial: las decisiones sin
   * fuente canónica quedan como stubs y la UI las muestra "no disponible". */
  window.aplicarDecisionesCanonicas = function (canon, DEC) {
    if (!canon || !canon.decisiones) return;
    Object.keys(canon.decisiones).forEach(function (id) {
      var cd = canon.decisiones[id];
      var d = DEC[id] || (DEC[id] = { id: id, issues: [] });
      d.titulo = cd.titulo || id;
      d.estado = cd.estado;
      d.estadoTexto = cd.texto;
      d.pregunta = cd.pregunta;
      d.detalle = cd.detalle;
      d.bloqueadaPor = cd.bloqueadaPor;
      d.desbloquea = cd.desbloquea;
      d.evidencia = cd.evidencia;
      d.comoSeguir = cd.comoSeguir;
      d.paraCerrar = cd.paraCerrar;
      d.canonico = true;
    });
  };
})();
