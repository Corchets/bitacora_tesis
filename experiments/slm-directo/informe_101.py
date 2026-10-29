"""Informe regenerable de la matriz #101 (sin inferencia).

Lee `manifiesto.json` + `actualizaciones.csv` de una corrida `matriz_101.py`
(carpeta legada o prefijo de archivos) y escribe `informe_101.md` junto al
manifiesto: por modelo y caso, aviso de cada condición (directo, Tito
viejo→SLM, Tito nuevo→SLM), oportunidad respecto de T_R/T_C disponibles en
las líneas, derivación, consultas, tokens y costo por componente y hasta el
aviso. Conserva fallos, inválidos, no avisos y denominadores.

Antes de informar verifica el snapshot de la corrida (hashes de texto y
referencia por caso): si los archivos actuales derivaron, rechaza en lugar
de releer mutable en silencio. Agrega gráficos SVG estáticos regenerables
(solo stdlib) desde las salidas guardadas.

Uso: python informe_101.py corridas/<carpeta_101>|<prefijo>

No declara éxito ni compara costos con corridas históricas completas:
los costos son prefijos hasta el aviso. No adopta metas (95/5 sigue
abierta en D08) ni cierra #101 por sí solo: la cobertura pendiente queda
explícita contra el denominador global 600.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import casos
import matriz_101
import resumen
from resumen import analisis_filtro  # noqa: F401  (reexportado para tests)

AQUI = Path(__file__).resolve().parent


def _num(fila: dict, clave: str) -> float:
    valor = fila.get(clave)
    if valor is None or valor == "":
        return 0.0
    try:
        return float(valor)
    except (TypeError, ValueError):
        return 0.0


def _tiene_tito_ms(fila: dict) -> bool:
    return (fila.get("tito_ms") or "") not in ("", None)


def detalle_condicion(filas: list[dict], analisis_cfg: dict, config: str) -> dict[str, dict]:
    """Derivación, consultas y costos por caso para una condición filtrada.

    Misma definición que `resumen.analisis_filtro` (prefijo hasta el aviso
    incluido; omitidas = SLM no consultado; sin doble conteo Tito+SLM),
    parametrizada por configuración para viejo y nuevo por separado.
    Un `tito_error` arrastrado en filas donde Tito ya no corre (sin
    `tito_ms`) NO cuenta como fallo nuevo: es el mismo error de activación.
    """
    por_caso: dict[str, list[dict]] = {}
    for f in filas:
        if f["config"] == config:
            por_caso.setdefault(f["case_id"], []).append(f)
    casos_cfg = {}
    for case_id, fs in por_caso.items():
        fs = sorted(fs, key=lambda f: int(f["linea"]))
        c = analisis_cfg[case_id]
        prefijo = fs if c["aviso"] is None else [f for f in fs if int(f["linea"]) <= c["aviso"]]
        consultadas = [f for f in prefijo if (f.get("consulta") or "") in ("slm_valida", "slm_fallo")]
        evitadas = [f for f in prefijo if (f.get("consulta") or "") == "omitida"]
        consultadas_full = [f for f in fs if (f.get("consulta") or "") in ("slm_valida", "slm_fallo")]
        casos_cfg[case_id] = {
            "derivacion": min((int(f["linea"]) for f in consultadas_full), default=None),
            "consultas": len(consultadas),
            "evitadas": len(evitadas),
            "fallos_slm": sum(1 for f in consultadas if f.get("consulta") == "slm_fallo"),
            "fallos_tito": sum(1 for f in prefijo
                               if (f.get("tito_error") or "").strip() and _tiene_tito_ms(f)),
            "tito_ms_total": sum(_num(f, "tito_ms") for f in prefijo),
            "slm_ms_total": sum(_num(f, "slm_ms") for f in prefijo),
            "ms_total": sum(_num(f, "ms") for f in prefijo),
            "tokens_slm": sum(_num(f, "tokens_prompt") + _num(f, "tokens_salida") for f in consultadas),
            "aviso": c["aviso"],
            "categoria": c["categoria"],
            "fin": c["fin"],
        }
    return casos_cfg


def _aviso_txt(aviso: int | None) -> str:
    return f"L{aviso}" if aviso else "—"


def _oportunidad(ref: dict, aviso: int | None) -> str:
    if aviso is None:
        return "sin aviso" if ref["clase"] == "vishing" else "ok sin aviso"
    if ref["clase"] in casos.LEGITIMAS:
        return "falsa alarma"
    tr, tc = ref.get("t_r_linea"), ref.get("t_c_linea")
    if tr is None:
        return "aviso (vishing sin pedido de referencia)"
    if aviso < tr:
        return f"{aviso - tr} (antes del pedido L{tr})"
    if aviso == tr:
        return "en el pedido"
    if tc is not None and aviso >= tc:
        return f"+{aviso - tr} (en/después del cumplimiento L{tc})"
    return f"+{aviso - tr} (después del pedido)"


def verificar_snapshot(manifiesto: dict) -> None:
    """Rechaza el informe si texto o referencia derivaron del snapshot."""
    for cid, snap in (manifiesto.get("casos") or {}).items():
        if isinstance(snap, str):
            actual = hashlib.sha256((casos.DIR_TEXTO / f"{cid}.txt").read_bytes()).hexdigest()
            if actual != snap:
                raise ValueError(f"{cid}: el texto derivó del snapshot de la corrida.")
            continue
        for clave, ruta in (("texto_sha256", casos.DIR_TEXTO / f"{cid}.txt"),
                            ("referencia_sha256", casos.DIR_REFERENCIA / f"{cid}.json")):
            if not ruta.exists():
                raise ValueError(f"{cid}: falta {ruta.name} para verificar el snapshot.")
            actual = hashlib.sha256(ruta.read_bytes()).hexdigest()
            if actual != snap.get(clave):
                raise ValueError(f"{cid}: deriva de {clave} respecto del snapshot "
                                 "de la corrida (no se relee mutable).")


def leer_corrida(base: Path) -> tuple[dict, list[dict], dict]:
    """Manifiesto + filas de una corrida legada o por prefijo, con snapshot verificado."""
    import csv
    import json

    corrida = matriz_101.resolver_corrida(base)
    if corrida["modo"] == "legado":
        manifiesto, filas = resumen.leer_corrida(corrida["base"])
    else:
        manifiesto = json.loads(corrida["manifiesto"].read_text(encoding="utf-8"))
        with corrida["csv"].open(encoding="utf-8-sig", newline="") as f:
            filas = list(csv.DictReader(f))
    if manifiesto.get("matriz") != "matriz-101":
        raise ValueError(f"{base} no es una corrida matriz-101.")
    verificar_snapshot(manifiesto)
    return manifiesto, filas, corrida


def _svg_barras(titulo: str, grupos: list[str], series: dict[str, list[float]],
                unidad: str) -> str:
    """Gráfico de barras agrupadas en SVG puro (stdlib, regenerable)."""
    colores = {"directo": "#4a7c59", "tito-viejo": "#b07d2b", "tito-nuevo": "#5b6abf"}
    ancho, alto = 640, 300
    margen_izq, margen_sup, margen_inf = 56, 44, 60
    area_w = ancho - margen_izq - 20
    area_h = alto - margen_sup - margen_inf
    maximo = max((v for vals in series.values() for v in vals), default=1) or 1
    n, k = len(grupos), len(series)
    paso = area_w / max(n, 1)
    barra_w = min(36, paso / max(k, 1) * 0.7)
    partes = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{ancho}" height="{alto}" role="img">',
              f"<title>{titulo}</title>",
              f'<text x="{ancho // 2}" y="22" text-anchor="middle" font-size="15">{titulo}</text>']
    for g in range(n + 1):
        y = margen_sup + area_h * g / 4
        val = maximo * (4 - g) / 4
        partes.append(f'<line x1="{margen_izq}" y1="{y}" x2="{ancho - 20}" y2="{y}" stroke="#ddd"/>')
        partes.append(f'<text x="{margen_izq - 6}" y="{y + 4}" text-anchor="end" font-size="10">'
                      f"{val:,.0f}</text>".replace(",", "."))
    for gi, grupo in enumerate(grupos):
        for si, (nombre, vals) in enumerate(series.items()):
            v = vals[gi] if gi < len(vals) else 0
            h = area_h * v / maximo
            x = margen_izq + paso * gi + (paso - barra_w * k) / 2 + barra_w * si
            y = margen_sup + area_h - h
            partes.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{barra_w:.1f}" height="{h:.1f}" '
                          f'fill="{colores.get(nombre, "#888")}">'
                          f"<title>{nombre} {grupo}: {v:,.0f} {unidad}</title></rect>".replace(",", "."))
        partes.append(f'<text x="{margen_izq + paso * gi + paso / 2:.1f}" y="{alto - 38}" '
                      f'text-anchor="middle" font-size="10">{grupo}</text>')
    leyenda_x = margen_izq
    for nombre in series:
        partes.append(f'<rect x="{leyenda_x}" y="{alto - 22}" width="12" height="12" '
                      f'fill="{colores.get(nombre, "#888")}"/>')
        partes.append(f'<text x="{leyenda_x + 16}" y="{alto - 12}" font-size="11">{nombre}</text>')
        leyenda_x += len(nombre) * 8 + 34
    partes.append("</svg>")
    return "\n".join(partes)


def generar_graficos(informe_md: Path, manifiesto: dict, analisis: dict, filas: list[dict]) -> list[str]:
    """Dos SVG estáticos desde salidas guardadas: avisos y costos por condición."""
    modelos = manifiesto.get("funcionales", {}).get("modelos", [])
    avisos: dict[str, list[float]] = {"directo": [], "tito-viejo": [], "tito-nuevo": []}
    costo_tito: dict[str, list[float]] = {"directo": [], "tito-viejo": [], "tito-nuevo": []}
    costo_slm: dict[str, list[float]] = {"directo": [], "tito-viejo": [], "tito-nuevo": []}
    for modelo in modelos:
        cfgs = {c.split("|")[0]: c for c in analisis if c.split("|")[1:2] == [modelo]}
        for cond in avisos:
            cfg = cfgs.get(cond)
            if cfg is None:
                avisos[cond].append(0)
                costo_tito[cond].append(0)
                costo_slm[cond].append(0)
                continue
            cs = analisis[cfg]
            avisos[cond].append(sum(1 for c in cs.values() if c["aviso"] is not None))
            if cond == "directo":
                costo_tito[cond].append(0)
                costo_slm[cond].append(sum(c["ms_hasta_aviso"] for c in cs.values()))
            else:
                det = detalle_condicion(filas, cs, cfg)
                costo_tito[cond].append(sum(d["tito_ms_total"] for d in det.values()))
                costo_slm[cond].append(sum(d["slm_ms_total"] for d in det.values()))
    prefijo = informe_md.stem
    if prefijo != "informe_101" and prefijo.endswith("_informe_101"):
        prefijo = prefijo[: -len("_informe_101")]
    avisos_svg = informe_md.parent / (prefijo + "_grafico_avisos.svg")
    costos_svg = informe_md.parent / (prefijo + "_grafico_costos.svg")
    avisos_svg.write_text(_svg_barras("Avisos por modelo y condición (de 20 casos)",
                                      modelos, avisos, "avisos"), encoding="utf-8")
    costos_svg.write_text(_svg_barras("Costo hasta aviso por condición: Tito (claro) + SLM",
                                      modelos, {**{c + "·tito": v for c, v in costo_tito.items()},
                                                **{c + "·slm": v for c, v in costo_slm.items()}},
                                      "ms"), encoding="utf-8")
    return [avisos_svg.name, costos_svg.name]


def nombres_salida(corrida: dict) -> tuple[Path, list[str]]:
    """Rutas del informe y sus gráficos (legado o prefijo)."""
    if corrida["modo"] == "legado":
        return (corrida["base"] / "informe_101.md",
                ["informe_101_grafico_avisos.svg", "informe_101_grafico_costos.svg"])
    pref = corrida["prefijo"]
    return (corrida["base"] / (pref + "_informe_101.md"),
            [pref + "_grafico_avisos.svg", pref + "_grafico_costos.svg"])


def armar_informe(base: Path) -> str:
    manifiesto, filas, corrida = leer_corrida(Path(base))
    analisis = resumen.analizar(manifiesto, filas)
    funcionales = manifiesto.get("funcionales", {})
    modelos = funcionales.get("modelos", [])
    refs = {c: casos.cargar_referencia(c) for c in manifiesto["casos"]}
    cob = manifiesto.get("cobertura", {})
    _, svg_nombres = nombres_salida(corrida)
    L = [f"# Informe matriz #101 — `{Path(base).name}`", ""]
    esperados = cob.get("esperados_globales", 600)
    L.append(f"Recorridos completados: {cob.get('completados', '?')}/{esperados} globales "
             f"(planificados: {cob.get('planificados', '?')}; "
             f"pendientes: {cob.get('pendientes', '?')}).")
    if not cob.get("matriz_completa"):
        L.append("NO es la matriz completa: faltan triples (ver faltantes por causa).")
    if manifiesto.get("interrumpida"):
        L.append("Corrida interrumpida: la cobertura es parcial, no es la matriz completa.")
    for modelo, motivo in (manifiesto.get("bloqueos_modelo") or {}).items():
        L.append(f"- Modelo bloqueado `{modelo}`: {motivo}")
    if manifiesto.get("bloqueo_nuevo"):
        L.append(f"- Condición tito-nuevo pendiente: {manifiesto['bloqueo_nuevo']}")
    L.append("Costos hasta el aviso incluido (o caso completo si nunca avisó); "
             "sin doble conteo Tito+SLM. Referencias de trabajo sin revisión humana "
             "(D07/D08 abiertas); posiciones en líneas, sin segundos ni RTF.")
    L.append("")
    faltantes = cob.get("faltantes", [])
    if faltantes:
        from collections import Counter
        por_causa = Counter(f["causa"] for f in faltantes)
        L.append("## Faltantes por causa (denominador global 600)")
        L.append("")
        L.append("| Causa | Triples |")
        L.append("|---|---|")
        for causa, n in sorted(por_causa.items()):
            L.append(f"| {causa} | {n} |")
        L.append("")
        detalle = [f for f in faltantes if f["causa"] in ("pendiente-medicion", "modelo_bloqueado")]
        for f in detalle[:40]:
            L.append(f"- `{f['modelo']}` {f['condicion']} `{f['caso']}`: {f['causa']}.")
        if len(detalle) > 40:
            L.append(f"- … y {len(detalle) - 40} más (lista completa en el manifiesto).")
        L.append("")

    for modelo in modelos:
        cfgs = {c.split("|")[0]: c for c in analisis
                if c.split("|")[1:2] == [modelo]}
        if not cfgs:
            L.append(f"## `{modelo}`: sin traza (bloqueado o pendiente)")
            L.append("")
            continue
        L.append(f"## `{modelo}`")
        L.append("")
        inv = (manifiesto.get("ollama", {}).get("modelos", {}).get(modelo, {}))
        L.append(f"- Artefacto medido: tag `{inv.get('tag', modelo)}`, digest `{inv.get('digest', '?')}`, "
                 f"cuantización `{inv.get('cuantizacion', '?')}`, familia `{inv.get('familia', '?')}`, "
                 f"parámetros `{inv.get('tamano_parametros', '?')}`; "
                 f"Ollama {manifiesto.get('ollama', {}).get('version', '?')} "
                 f"en {manifiesto.get('ollama', {}).get('url', '?')}.")
        digest_previo = (funcionales.get("inventario", {}).get(modelo, {}).get("digest"))
        if digest_previo and inv.get("digest") and digest_previo != inv.get("digest"):
            L.append(f"- ADVERTENCIA: el digest medido difiere del inventario previo "
                     f"(`{digest_previo}` vs `{inv.get('digest')}`).")
        else:
            L.append("- Identidad entre condiciones: mismo artefacto (una carga por proceso), "
                     "sin `latest`, alias ni sustituciones.")
        L.append(f"- Carga (fuera del costo por línea): {inv.get('carga_ms', '?')} ms "
                 f"(memoria {inv.get('memoria', '?')}).")
        L.append("")
        L.append("| Caso | Clase | T_R/T_C | Aviso directo | Aviso viejo | Aviso nuevo | "
                 "Deriv. V/N | Cons. D/V/N | Evit. V/N | Tokens D/V/N | ms hasta aviso D/V/N | "
                 "Tito ms V/N | SLM ms D/V/N |")
        L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
        for cid in sorted(refs):
            avisos, deriv, cons, evit, toks, mss, titos, slms = {}, {}, {}, {}, {}, {}, {}, {}
            for cond, cfg in cfgs.items():
                a = analisis[cfg][cid] if cid in analisis[cfg] else None
                avisos[cond] = _aviso_txt(a["aviso"]) if a else "s/t"
                if a and cond != "directo":
                    d = detalle_condicion(filas, analisis[cfg], cfg)[cid]
                    deriv[cond] = d["derivacion"] or "nunca"
                    cons[cond] = d["consultas"]
                    evit[cond] = d["evitadas"]
                    toks[cond] = f"{d['tokens_slm']:.0f}"
                    mss[cond] = f"{d['ms_total']:.0f}"
                    titos[cond] = f"{d['tito_ms_total']:.0f}"
                    slms[cond] = f"{d['slm_ms_total']:.0f}"
                elif a:
                    cons[cond] = len([f for f in filas if f["config"] == cfg and f["case_id"] == cid
                                      and (int(f["linea"]) <= a["aviso"] if a["aviso"] else True)])
                    toks[cond] = f"{a['tokens_hasta_aviso']:.0f}"
                    mss[cond] = f"{a['ms_hasta_aviso']:.0f}"
                    slms[cond] = f"{a['ms_hasta_aviso']:.0f}"
            ref = refs[cid]
            trtc = f"{ref.get('t_r_linea') or '—'}/{ref.get('t_c_linea') or '—'}"
            L.append(f"| `{cid}` | {ref['clase']} | {trtc} | "
                     f"{avisos.get('directo', 's/t')} | {avisos.get('tito-viejo', 's/t')} | "
                     f"{avisos.get('tito-nuevo', 's/t')} | "
                     f"{deriv.get('tito-viejo', 's/t')}/{deriv.get('tito-nuevo', 's/t')} | "
                     f"{cons.get('directo', 's/t')}/{cons.get('tito-viejo', 's/t')}/{cons.get('tito-nuevo', 's/t')} | "
                     f"{evit.get('tito-viejo', 's/t')}/{evit.get('tito-nuevo', 's/t')} | "
                     f"{toks.get('directo', 's/t')}/{toks.get('tito-viejo', 's/t')}/{toks.get('tito-nuevo', 's/t')} | "
                     f"{mss.get('directo', 's/t')}/{mss.get('tito-viejo', 's/t')}/{mss.get('tito-nuevo', 's/t')} | "
                     f"{titos.get('tito-viejo', 's/t')}/{titos.get('tito-nuevo', 's/t')} | "
                     f"{slms.get('directo', 's/t')}/{slms.get('tito-viejo', 's/t')}/{slms.get('tito-nuevo', 's/t')} |")
        L.append("")
        L.append("### Oportunidad y fallos")
        L.append("")
        for cid in sorted(refs):
            ref = refs[cid]
            partes = []
            for cond, cfg in sorted(cfgs.items()):
                a = analisis[cfg].get(cid)
                if not a:
                    partes.append(f"{cond}: sin traza")
                    continue
                extra = ""
                if a["aviso_fila"] is not None and a["aviso_fila"].get("evidencia_en_texto") == "false":
                    extra = " (cita no textual)"
                if a["n_fallos_hasta_aviso"]:
                    extra += f" [{a['n_fallos_hasta_aviso']} fallos]"
                partes.append(f"{cond}: {_oportunidad(ref, a['aviso'])}{extra}")
            L.append(f"- `{cid}` ({ref['clase']}): " + "; ".join(partes) + ".")
        L.append("")
        tot = {cond: resumen.metricas(analisis[cfg]) for cond, cfg in sorted(cfgs.items())}
        L.append("### Totales (denominadores incluidos)")
        L.append("")
        L.append("| Condición | Vishing con aviso | Falsas alarmas | Fallos | Sin evaluar |")
        L.append("|---|---|---|---|---|")
        for cond, m in tot.items():
            L.append(f"| {cond} | {m['vishing_con_aviso']}/{m['vishing']} | "
                     f"{m['falsas_alarmas']}/{m['legitimas']} | {m['fallos']}/{m['actualizaciones']} | "
                     f"{m['sin_evaluar']} |")
        L.append("")

    L.append("### Totales globales por condición (todos los modelos)")
    L.append("")
    L.append("| Condición | Vishing con aviso | Falsas alarmas | Fallos Tito/SLM | Sin evaluar |")
    L.append("|---|---|---|---|---|")
    for cond in ("directo", "tito-viejo", "tito-nuevo"):
        cfgs = [c for c in analisis if c.split("|")[0] == cond]
        v_av = sum(1 for c in cfgs for v in analisis[c].values()
                   if v["ref"]["clase"] == "vishing" and v["aviso"] is not None
                   and v["categoria"] not in resumen.SIN_EVALUAR)
        vish = sum(1 for c in cfgs for v in analisis[c].values()
                   if v["ref"]["clase"] == "vishing" and v["categoria"] not in resumen.SIN_EVALUAR)
        fa = sum(1 for c in cfgs for v in analisis[c].values() if v["categoria"] == "falsa_alarma")
        leg = sum(1 for c in cfgs for v in analisis[c].values()
                  if v["ref"]["clase"] in casos.LEGITIMAS and v["categoria"] not in resumen.SIN_EVALUAR)
        L.append(f"| {cond} | {v_av}/{vish} | {fa}/{leg} | "
                 f"ver desglose por modelo | "
                 f"{sum(1 for c in cfgs for v in analisis[c].values() if v['categoria'] in resumen.SIN_EVALUAR)} |")
    L.append("")
    L.append("## Gráficos (SVG regenerables desde salidas guardadas)")
    L.append("")
    for nombre in svg_nombres:
        L.append(f"- `{nombre}`")
    L.append("")
    L.append("## Preparación y hardware (fuera del costo por línea)")
    L.append("")
    L.append(f"- Comando: `{manifiesto.get('comando', '?')}`")
    L.append(f"- Código: `{manifiesto.get('codigo', {}).get('commit', '?')}` "
             f"(cambios sin commit en la carpeta: "
             f"{manifiesto.get('codigo', {}).get('cambios_sin_commit_en_la_carpeta')})")
    for nombre, clave in (("Tito viejo", "tito_viejo_preparacion"), ("Tito nuevo", "tito_nuevo_preparacion")):
        prep = manifiesto.get(clave)
        if prep is None:
            L.append(f"- {nombre}: condición pendiente (sin preparación).")
        else:
            L.append(f"- {nombre}: artefacto {prep.get('artefacto_ms', '?')} ms, "
                     f"encoder {prep.get('encoder_ms', '?')} ms "
                     f"(listo: {prep.get('encoder_listo', 'sin dato')}), "
                     f"calentamiento {prep.get('calentamiento_ms', '?')} ms "
                     f"(unidad: {prep.get('unidad', 'ms')}; error: {prep.get('error') or 'ninguno'}).")
    fv, fn = (funcionales.get("tito_viejo", {}), funcionales.get("tito_nuevo", {}))
    L.append(f"- Entrada/umbral viejo: {fv.get('entrada', '?')} / {fv.get('umbral', '?')} "
             f"(sha {str(fv.get('sha256', '?'))[:12]}…); "
             f"nuevo: {fn.get('entrada', fn.get('bloqueo', '?'))} / {fn.get('umbral', '?')} "
             f"(sha {str(fn.get('sha256', ''))[:12]}…).")
    L.append("")
    L.append("## Límites de interpretación")
    L.append("")
    L.append("- Casos sintéticos de desarrollo, sin revisión humana; sin audio, RTF ni prevención.")
    L.append("- La comparación mide activación selectiva + indicio falible juntos: "
             "no separa el efecto del indicio del efecto de la activación.")
    L.append("- Sin criterio de aceptación: no se adopta ninguna meta ni se declara mejora "
             "sin el acuerdo previsto en #102.")
    return "\n".join(L) + "\n"


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if len(args) != 1:
        sys.exit("uso: python informe_101.py corridas/<carpeta_101>|<prefijo_101>")
    manifiesto, filas, corrida = leer_corrida(Path(args[0]))
    analisis = resumen.analizar(manifiesto, filas)
    md_path, _ = nombres_salida(corrida)
    md_path.write_text(armar_informe(Path(args[0])), encoding="utf-8")
    generados = generar_graficos(md_path, manifiesto, analisis, filas)
    print(f"guardado en {md_path} + {', '.join(generados)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
