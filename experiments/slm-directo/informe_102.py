"""Informe regenerable de la matriz #102 (sin inferencia).

Lee `manifiesto.json` + `actualizaciones.csv` de una corrida `matriz_102.py`
(prefijo de archivos) y escribe `<pref>_informe_102.md` junto al manifiesto:
por modelo y caso, aviso de cada política (permanente vs reconsultas),
oportunidad respecto de `T_R`/`T_C`, márgenes `L_C`, derivación, consultas,
tokens y costo por componente y hasta el aviso. Conserva fallos,
inválidos, no avisos y denominadores íntegros (global 400).

Con `--comparar-101 <manifiesto|carpeta>` agrega la sección consolidada
que separa el efecto de cambiar el Tito (directo→tito-viejo→tito-nuevo,
medido en #101) del efecto de cambiar la política (permanente→
reconsultas, medido en #102 con el Tito nuevo fijo). Sin ese flag, la
sección consolidada queda pendiente explícita.

Antes de informar verifica el snapshot de la corrida (hashes de texto y
referencia por caso): si los archivos actuales derivaron, rechaza en lugar
de releer mutable en silencio. Agrega dos figuras Matplotlib (SVG + PNG,
backend Agg) regenerables desde las salidas guardadas. Si el manifiesto
trae `"sintetico": true` (fixtures de prueba), el informe se marca como
DATOS SINTÉTICOS y nunca como medición real.

Uso: python informe_102.py regenerar <prefijo|carpeta> [--comparar-101 ...]

No declara éxito ni adopta metas (95/5 sigue abierta en D08): informa
conteos, denominadores, costos y pendientes. No cierra D07/D08/D09.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import textwrap
from pathlib import Path

import casos
import informe_101
import matriz_101
import matriz_102
import resumen

AQUI = Path(__file__).resolve().parent

_CONDICIONES_102 = ("permanente", "reconsultas")
_COLORES_102 = {"permanente": "#5b6bab", "reconsultas": "#4a9c6d"}


def leer_corrida_102(base: Path) -> tuple[dict, list[dict], dict]:
    """Manifiesto + filas de una corrida por prefijo, con snapshot verificado."""
    corrida = matriz_102.resolver_corrida_102(base)
    manifiesto = json.loads(corrida["manifiesto"].read_text(encoding="utf-8"))
    with corrida["csv"].open(encoding="utf-8-sig", newline="") as f:
        filas = list(csv.DictReader(f))
    informe_101.verificar_snapshot(manifiesto)
    return manifiesto, filas, corrida


def _cfg_de(modelo: str, cond: str, analisis: dict) -> str | None:
    for cfg in analisis:
        partes = cfg.split("|")
        if partes[0] == cond and len(partes) > 1 and partes[1] == modelo:
            return cfg
    return None


def _oportunidad_lc(ref: dict, aviso: int | None) -> str:
    """Oportunidad con margen L_C explícito y referencias ausentes."""
    base = informe_101._oportunidad(ref, aviso)
    if aviso is None:
        return base
    tc = ref.get("t_c_linea")
    if tc is None:
        return base + " (T_C ausente: sin margen L_C)"
    return base + f" (L_C={tc - aviso})"


def nombres_salida_102(corrida: dict) -> tuple[Path, list[str]]:
    pref = corrida["prefijo"]
    return (corrida["base"] / (pref + "_informe_102.md"),
            [pref + "_grafico102_avisos.svg", pref + "_grafico102_avisos.png",
             pref + "_grafico102_costos.svg", pref + "_grafico102_costos.png"])


def _figura_calidad(ruta_base: Path, modelos: list[str], analisis: dict,
                    sintetico: bool) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch

    n = max(len(modelos), 1)
    fig, ejes = plt.subplots(1, 2, figsize=(min(7 + 1.2 * n, 15), 6.2))
    paneles = ((ejes[0], "vishing con aviso", "n avisados /\nn vishing evaluados"),
               (ejes[1], "falsas alarmas", "n falsas alarmas /\nn legítimas evaluadas"))
    for ax, _, subtitulo in paneles:
        ax.set_title(subtitulo, fontsize=10, wrap=True)
        ax.set_xticks(list(range(n)))
        ax.set_xticklabels(modelos, rotation=30, ha="right", fontsize=9)
        ax.set_ylim(0, 1.12)
        ax.set_ylabel("proporción", fontsize=9)
        ax.grid(axis="y", linestyle=":", alpha=0.6)
    for gi, cond in enumerate(_CONDICIONES_102):
        for mi, modelo in enumerate(modelos):
            cfg = _cfg_de(modelo, cond, analisis)
            x = mi + (gi - 0.5) * 0.24
            for ax, cual, _ in paneles:
                if cfg is None:
                    ax.bar(x, 0, width=0.22, color="#cccccc",
                           edgecolor="#666666", hatch="///")
                    ax.text(x, 0.03, "sin datos", ha="center", va="bottom",
                            fontsize=7, rotation=90, color="#333333")
                    continue
                mm = resumen.metricas(analisis[cfg])
                num, den = ((mm["vishing_con_aviso"], mm["vishing"]) if cual == "vishing con aviso"
                            else (mm["falsas_alarmas"], mm["legitimas"]))
                if den == 0:
                    ax.bar(x, 0, width=0.22, color="#cccccc",
                           edgecolor="#666666", hatch="///")
                    ax.text(x, 0.03, "sin cobertura", ha="center", va="bottom",
                            fontsize=7, rotation=90, color="#333333")
                    continue
                ax.bar(x, num / den, width=0.22, color=_COLORES_102[cond],
                       edgecolor="black", linewidth=0.5)
                ax.text(x, num / den + 0.02, f"{num}/{den}", ha="center",
                        va="bottom", fontsize=8)
    handles = [Patch(facecolor=_COLORES_102[c], edgecolor="black", label=c)
               for c in _CONDICIONES_102]
    ejes[1].legend(handles=handles, title="política", fontsize=8, loc="upper right")
    titulo = "Calidad por modelo y política (avisos sobre salidas guardadas)"
    if sintetico:
        titulo += " — DATOS SINTÉTICOS"
    fig.suptitle(textwrap.fill(titulo, width=60), fontsize=11, wrap=True)
    nota = ("Barras por política: permanente · reconsultas. "
            "Sin datos = política sin traza (no es cero). Denominadores excluyen sin evaluar.")
    fig.text(0.5, 0.02, textwrap.fill(nota, width=100),
             ha="center", va="bottom", fontsize=8, style="italic", wrap=True)
    fig.tight_layout(rect=(0, 0.16, 1, 0.88))
    fig.savefig(str(ruta_base) + ".svg", format="svg", bbox_inches="tight", pad_inches=0.3)
    fig.savefig(str(ruta_base) + ".png", format="png", dpi=110,
                bbox_inches="tight", pad_inches=0.3)
    plt.close(fig)


def _figura_costos(ruta_base: Path, modelos: list[str], manifiesto: dict,
                   analisis: dict, sintetico: bool) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch

    n = max(len(modelos), 1)
    fig, ax = plt.subplots(figsize=(min(7 + 1.2 * n, 15), 6.4))
    for gi, cond in enumerate(_CONDICIONES_102):
        for mi, modelo in enumerate(modelos):
            x = mi + (gi - 0.5) * 0.24
            cfg = _cfg_de(modelo, cond, analisis)
            if cfg is None or not analisis[cfg]:
                ax.bar(x, 0, width=0.22, color="#cccccc",
                       edgecolor="#666666", hatch="///")
                ax.text(x, 0, "sin datos", ha="center", va="bottom",
                        fontsize=7, rotation=90, color="#333333")
                continue
            tito = sum(c["tito_ms_total"] for c in analisis[cfg].values())
            slm = sum(c["slm_ms_total"] for c in analisis[cfg].values())
            total = tito + slm
            ax.bar(x, tito, width=0.22, color=_COLORES_102[cond],
                   edgecolor="black", linewidth=0.5)
            ax.bar(x, slm, width=0.22, bottom=tito, color=_COLORES_102[cond],
                   edgecolor="black", linewidth=0.5, alpha=0.45,
                   hatch="//" if slm > 0 else None)
            ax.text(x, total, f"{total:,.0f} ms".replace(",", "."),
                    ha="center", va="bottom", fontsize=8)
    ax.set_xticks(list(range(n)))
    ax.set_xticklabels(modelos, rotation=30, ha="right", fontsize=9)
    ax.set_ylabel("ms hasta el aviso (o caso completo si nunca avisó)", fontsize=9)
    ax.set_xlabel("modelo", fontsize=9)
    titulo = "Costo por componente hasta el aviso: Tito (sólido) + SLM (claro)"
    if sintetico:
        titulo += " — DATOS SINTÉTICOS"
    ax.set_title(textwrap.fill(titulo, width=55), fontsize=11, wrap=True)
    ax.grid(axis="y", linestyle=":", alpha=0.6)
    prep = manifiesto.get("tito_nuevo_preparacion") or {}
    nota_prep = ("Preparación fuera del costo por línea — Tito nuevo: artefacto "
                 f"{prep.get('artefacto_ms', '?')} ms, encoder {prep.get('encoder_ms', '?')} ms, "
                 f"calentamiento {prep.get('calentamiento_ms', '?')} ms "
                 f"(error: {prep.get('error') or 'ninguno'}).")
    fig.text(0.5, 0.02, textwrap.fill(nota_prep, width=95),
             ha="center", va="bottom", fontsize=8, style="italic", wrap=True)
    handles = [Patch(facecolor=_COLORES_102[c], edgecolor="black", label=c)
               for c in _CONDICIONES_102]
    handles.append(Patch(facecolor="white", edgecolor="black", hatch="//",
                         label="tramo SLM (claro con trama)"))
    ax.legend(handles=handles, title="política", fontsize=8, loc="upper right")
    fig.tight_layout(rect=(0, 0.20, 1, 0.88))
    fig.savefig(str(ruta_base) + ".svg", format="svg", bbox_inches="tight", pad_inches=0.3)
    fig.savefig(str(ruta_base) + ".png", format="png", dpi=110,
                bbox_inches="tight", pad_inches=0.3)
    plt.close(fig)


def generar_graficos(informe_md: Path, manifiesto: dict, analisis: dict) -> list[str]:
    modelos = manifiesto.get("funcionales", {}).get("modelos", [])
    sintetico = bool(manifiesto.get("sintetico"))
    prefijo = informe_md.stem
    if prefijo.endswith("_informe_102"):
        prefijo = prefijo[: -len("_informe_102")]
    base_avisos = informe_md.parent / (prefijo + "_grafico102_avisos")
    base_costos = informe_md.parent / (prefijo + "_grafico102_costos")
    _figura_calidad(base_avisos, modelos, analisis, sintetico)
    _figura_costos(base_costos, modelos, manifiesto, analisis, sintetico)
    return [base_avisos.name + ".svg", base_avisos.name + ".png",
            base_costos.name + ".svg", base_costos.name + ".png"]


def consolidado_101_vs_102(manifiesto_102: dict, analisis_102: dict,
                           manifiesto_101: dict | None,
                           analisis_101: dict | None) -> list[str]:
    """Separa el efecto de cambiar el Tito (#101) del de cambiar la política (#102)."""
    L = ["## Consolidado: efecto Tito (#101) vs efecto política (#102)", ""]
    if manifiesto_101 is None or analisis_101 is None:
        L.append("Comparación con #101 pendiente: este informe solo muestra el efecto "
                 "de la política (permanente→reconsultas) con el Tito nuevo fijo. "
                 "Pasar `--comparar-101 <corrida>` para agregar el efecto del Tito.")
        L.append("")
        return L
    L.append("Efecto Tito (medido en #101, mismo procedimiento, tres condiciones): "
             "directo → tito-viejo → tito-nuevo. Efecto política (medido en #102, "
             "Tito nuevo fijo): permanente → reconsultas. No se atribuye al "
             "entrenamiento una diferencia que también cambia la política.")
    L.append("")
    L.append("| Efecto | Condiciones | Vishing con aviso | Falsas alarmas |")
    L.append("|---|---|---|---|")
    for etiqueta, analisis, conds in (
            ("Tito (#101)", analisis_101, ("directo", "tito-viejo", "tito-nuevo")),
            ("Política (#102)", analisis_102, ("permanente", "reconsultas"))):
        for cond in conds:
            cfgs = [c for c in analisis if c.split("|")[0] == cond]
            v_av = sum(1 for c in cfgs for v in analisis[c].values()
                       if v["ref"]["clase"] == "vishing" and v["aviso"] is not None
                       and v["categoria"] not in resumen.SIN_EVALUAR)
            vish = sum(1 for c in cfgs for v in analisis[c].values()
                       if v["ref"]["clase"] == "vishing" and v["categoria"] not in resumen.SIN_EVALUAR)
            fa = sum(1 for c in cfgs for v in analisis[c].values() if v["categoria"] == "falsa_alarma")
            leg = sum(1 for c in cfgs for v in analisis[c].values()
                      if v["ref"]["clase"] in casos.LEGITIMAS and v["categoria"] not in resumen.SIN_EVALUAR)
            L.append(f"| {etiqueta} | {cond} | {v_av}/{vish} | {fa}/{leg} |")
    L.append("")
    L.append(f"(Procedencia #101: `{manifiesto_101.get('comando', '?')}`; "
             f"cobertura #101: {manifiesto_101.get('cobertura', {}).get('completados', '?')}/600.)")
    L.append("")
    return L


def armar_informe(base: Path, comparar_101: Path | None = None) -> str:
    manifiesto, filas, corrida = leer_corrida_102(Path(base))
    analisis = resumen.analizar(manifiesto, filas)
    funcionales = manifiesto.get("funcionales", {})
    modelos = funcionales.get("modelos", [])
    refs = {c: casos.cargar_referencia(c) for c in manifiesto["casos"]}
    cob = manifiesto.get("cobertura", {})
    informe_md, _svg = nombres_salida_102(corrida)
    sintetico = bool(manifiesto.get("sintetico"))
    L = [f"# Informe matriz #102 — `{Path(base).name}`", ""]
    if sintetico:
        L.append("> DATOS SINTÉTICOS: fixture de prueba, nunca una medición real. "
                 "No informa calidad ni costos observados.")
        L.append("")
    esperados = cob.get("esperados_globales", 400)
    L.append(f"Recorridos completados: {cob.get('completados', '?')}/{esperados} globales "
             f"(planificados: {cob.get('planificados', '?')}; "
             f"pendientes: {cob.get('pendientes', '?')}).")
    if not cob.get("matriz_completa"):
        L.append("NO es la matriz completa: faltan triples (ver faltantes por causa).")
    if manifiesto.get("interrumpida"):
        L.append("Corrida interrumpida: la cobertura es parcial, no es la matriz completa.")
    for modelo, motivo in (manifiesto.get("bloqueos_modelo") or {}).items():
        L.append(f"- Modelo bloqueado `{modelo}`: {motivo}")
    if manifiesto.get("bloqueo_politica"):
        L.append(f"- Condición reconsultas pendiente: {manifiesto['bloqueo_politica']}")
    reuso = manifiesto.get("reutilizacion_101") or {}
    if reuso.get("triples_importados"):
        L.append(f"- Celdas permanente reusadas de #101: {reuso['triples_importados']} "
                 f"(desde `{reuso.get('desde', '?')}`, huellas coincidentes verificadas).")
    pol = (manifiesto.get("politica_congelada") or {})
    L.append(f"- Política congelada: `{pol.get('ganadora', '?')}` "
             f"(periodo {pol.get('periodo_revision', '?')}, "
             f"regla {pol.get('regla_nueva_evidencia', '?')}, delta {pol.get('delta_minimo', '?')}).")
    L.append("Costos hasta el aviso incluido (o caso completo si nunca avisó); "
             "Tito corre en cada actualización y su costo queda visible sin doble conteo. "
             "Referencias de trabajo sin revisión humana (D07/D08 abiertas); "
             "posiciones en líneas, sin segundos ni RTF.")
    L.append("")
    faltantes = cob.get("faltantes", [])
    if faltantes:
        from collections import Counter
        por_causa = Counter(f["causa"] for f in faltantes)
        L.append("## Faltantes por causa (denominador global 400)")
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
        L.append(f"## `{modelo}`")
        L.append("")
        inv = (manifiesto.get("ollama", {}).get("modelos", {}).get(modelo, {}))
        L.append(f"- Artefacto medido: tag `{inv.get('tag', modelo)}`, digest `{inv.get('digest', '?')}`, "
                 f"cuantización `{inv.get('cuantizacion', '?')}`; "
                 f"Ollama {manifiesto.get('ollama', {}).get('version', '?')}.")
        L.append("- Identidad entre políticas: mismo Tito, entrada, umbral, prompt y runtime; "
                 "solo varía la política. Sin `latest`, alias ni sustituciones.")
        L.append("")
        cfgs = {c.split("|")[0]: c for c in analisis if c.split("|")[1:2] == [modelo]}
        L.append("| Caso | Clase | T_R/T_C | Aviso P/R | Oportunidad P/R (L_C) | "
                 "Deriv. P/R | Cons. P/R | Evit. P/R | Tokens P/R | ms P/R | Tito ms P/R | SLM ms P/R |")
        L.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
        for cid in sorted(refs):
            avisos, oport, deriv, cons, evit, toks, mss, titos, slms = (
                {}, {}, {}, {}, {}, {}, {}, {}, {})
            for cond, cfg in cfgs.items():
                a = analisis[cfg][cid] if cid in analisis[cfg] else None
                avisos[cond] = informe_101._aviso_txt(a["aviso"]) if a else "s/t"
                if a and cond in ("permanente", "reconsultas"):
                    d = informe_101.detalle_condicion(filas, analisis[cfg], cfg)[cid]
                    oport[cond] = _oportunidad_lc(refs[cid], a["aviso"])
                    deriv[cond] = d["derivacion"] or "nunca"
                    cons[cond] = d["consultas"]
                    evit[cond] = d["evitadas"]
                    toks[cond] = f"{d['tokens_slm']:.0f}"
                    mss[cond] = f"{d['ms_total']:.0f}"
                    titos[cond] = f"{d['tito_ms_total']:.0f}"
                    slms[cond] = f"{d['slm_ms_total']:.0f}"
            ref = refs[cid]
            trtc = f"{ref.get('t_r_linea') or '—'}/{ref.get('t_c_linea') or '—'}"
            L.append(f"| `{cid}` | {ref['clase']} | {trtc} | "
                     f"{avisos.get('permanente', 's/t')}/{avisos.get('reconsultas', 's/t')} | "
                     f"{oport.get('permanente', 's/t')} ; {oport.get('reconsultas', 's/t')} | "
                     f"{deriv.get('permanente', 's/t')}/{deriv.get('reconsultas', 's/t')} | "
                     f"{cons.get('permanente', 's/t')}/{cons.get('reconsultas', 's/t')} | "
                     f"{evit.get('permanente', 's/t')}/{evit.get('reconsultas', 's/t')} | "
                     f"{toks.get('permanente', 's/t')}/{toks.get('reconsultas', 's/t')} | "
                     f"{mss.get('permanente', 's/t')}/{mss.get('reconsultas', 's/t')} | "
                     f"{titos.get('permanente', 's/t')}/{titos.get('reconsultas', 's/t')} | "
                     f"{slms.get('permanente', 's/t')}/{slms.get('reconsultas', 's/t')} |")
        L.append("")
        tot = {cond: resumen.metricas(analisis[cfg]) for cond, cfg in sorted(cfgs.items())}
        L.append("### Totales (denominadores incluidos)")
        L.append("")
        L.append("| Política | Vishing con aviso | Falsas alarmas | Fallos | Sin evaluar |")
        L.append("|---|---|---|---|---|")
        for cond, mm in tot.items():
            L.append(f"| {cond} | {mm['vishing_con_aviso']}/{mm['vishing']} | "
                     f"{mm['falsas_alarmas']}/{mm['legitimas']} | {mm['fallos']}/{mm['actualizaciones']} | "
                     f"{mm['sin_evaluar']} |")
        L.append("")

    man101, ana101 = None, None
    if comparar_101 is not None:
        man101, filas101, _c101 = informe_101.leer_corrida(comparar_101)
        ana101 = resumen.analizar(man101, filas101)
    L.extend(consolidado_101_vs_102(manifiesto, analisis, man101, ana101))

    L.append("## Gráficos (Matplotlib SVG+PNG regenerables desde salidas guardadas)")
    L.append("")
    _informe_md, svg_nombres = nombres_salida_102(corrida)
    for nombre in svg_nombres:
        L.append(f"- `{nombre}`")
    L.append("")
    L.append("## Preparación y hardware (fuera del costo por línea)")
    L.append("")
    L.append(f"- Comando: `{manifiesto.get('comando', '?')}`")
    L.append(f"- Código: `{manifiesto.get('codigo', {}).get('commit', '?')}` "
             f"(cambios sin commit en la carpeta: "
             f"{manifiesto.get('codigo', {}).get('cambios_sin_commit_en_la_carpeta')})")
    prep = manifiesto.get("tito_nuevo_preparacion") or {}
    L.append(f"- Tito nuevo: artefacto {prep.get('artefacto_ms', '?')} ms, "
             f"encoder {prep.get('encoder_ms', '?')} ms "
             f"(listo: {prep.get('encoder_listo', 'sin dato')}), "
             f"calentamiento {prep.get('calentamiento_ms', '?')} ms "
             f"(error: {prep.get('error') or 'ninguno'}).")
    L.append("")
    return "\n".join(L) + "\n"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="comando", required=True)
    r = sub.add_parser("regenerar", help="regenera el informe desde salidas guardadas (sin inferencia)")
    r.add_argument("corrida", type=Path)
    r.add_argument("--comparar-101", type=Path, default=None,
                   help="corrida matriz-101 para la sección consolidada")
    args = p.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    try:
        texto = armar_informe(args.corrida, args.comparar_101)
    except (ValueError, FileNotFoundError) as e:
        sys.exit(f"No se pudo regenerar: {e}")
    manifiesto, _filas, corrida = leer_corrida_102(Path(args.corrida))
    analisis = resumen.analizar(manifiesto, _filas)
    informe_md, _nombres = nombres_salida_102(corrida)
    informe_md.write_text(texto, encoding="utf-8")
    try:
        generar_graficos(informe_md, manifiesto, analisis)
    except ImportError as e:
        sys.exit(f"Informe escrito sin gráficos (falta Matplotlib en este intérprete: {e}).")
    print(f"Informe regenerado (sin inferencia): {informe_md.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
