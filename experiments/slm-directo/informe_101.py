"""Informe regenerable de la matriz #101 (sin inferencia).

Lee `manifiesto.json` + `actualizaciones.csv` de una corrida `matriz_101.py`
(carpeta legada o prefijo de archivos) y escribe `informe_101.md` junto al
manifiesto: por modelo y caso, aviso de cada condición (directo, Tito
viejo→SLM, Tito nuevo→SLM), oportunidad respecto de T_R/T_C disponibles en
las líneas, derivación, consultas, tokens y costo por componente y hasta el
aviso. Conserva fallos, inválidos, no avisos y denominadores.

Antes de informar verifica el snapshot de la corrida (hashes de texto y
referencia por caso): si los archivos actuales derivaron, rechaza en lugar
de releer mutable en silencio. Agrega dos figuras Matplotlib (SVG + PNG,
backend Agg) regenerables desde las salidas guardadas.

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


_CONDICIONES = ("directo", "tito-viejo", "tito-nuevo")
_COLORES = {"directo": "#4a7c59", "tito-viejo": "#b07d2b", "tito-nuevo": "#5b6abf"}


def _cfg_de(modelo: str, cond: str, analisis: dict) -> str | None:
    for cfg in analisis:
        partes = cfg.split("|")
        if partes[0] == cond and len(partes) > 1 and partes[1] == modelo:
            return cfg
    return None


def _figura_calidad(ruta_base: Path, modelos: list[str], analisis: dict) -> None:
    """Calidad por modelo y condición: vishing con aviso y falsas alarmas.

    Denominadores = casos evaluados (excluyen `sin evaluar`). Una condición
    sin traza se marca `sin datos`: nunca se dibuja como cero observado.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    import textwrap
    from matplotlib.patches import Patch

    n = max(len(modelos), 1)
    fig, ejes = plt.subplots(1, 2, figsize=(min(7 + 1.2 * n, 15), 6.2))
    paneles = (
        (ejes[0], "vishing con aviso", "n avisados /\nn vishing evaluados"),
        (ejes[1], "falsas alarmas", "n falsas alarmas /\nn legítimas evaluadas"),
    )
    for ax, _, subtitulo in paneles:
        ax.set_title(subtitulo, fontsize=10, wrap=True)
        ax.set_xticks(list(range(n)))
        ax.set_xticklabels(modelos, rotation=30, ha="right", fontsize=9)
        ax.set_ylim(0, 1.12)
        ax.set_ylabel("proporción", fontsize=9)
        ax.grid(axis="y", linestyle=":", alpha=0.6)
    for gi, cond in enumerate(_CONDICIONES):
        for mi, modelo in enumerate(modelos):
            cfg = _cfg_de(modelo, cond, analisis)
            x = mi + (gi - 1) * 0.24
            for ax, cual, _ in paneles:
                if cfg is None:
                    ax.bar(x, 0, width=0.22, color="#cccccc",
                           edgecolor="#666666", hatch="///")
                    ax.text(x, 0.03, "sin datos", ha="center", va="bottom",
                            fontsize=7, rotation=90, color="#333333")
                    continue
                m = resumen.metricas(analisis[cfg])
                if cual == "vishing con aviso":
                    num, den = m["vishing_con_aviso"], m["vishing"]
                else:
                    num, den = m["falsas_alarmas"], m["legitimas"]
                if den == 0:
                    ax.bar(x, 0, width=0.22, color="#cccccc",
                           edgecolor="#666666", hatch="///")
                    ax.text(x, 0.03, "sin cobertura", ha="center", va="bottom",
                            fontsize=7, rotation=90, color="#333333")
                    continue
                ax.bar(x, num / den, width=0.22, color=_COLORES[cond],
                       edgecolor="black", linewidth=0.5)
                ax.text(x, num / den + 0.02, f"{num}/{den}", ha="center",
                        va="bottom", fontsize=8)
    handles = [Patch(facecolor=_COLORES[cond], edgecolor="black", label=cond)
                 for cond in _CONDICIONES]
    ejes[1].legend(handles=handles, title="condición", fontsize=8, loc="upper right")
    titulo = textwrap.fill("Calidad por modelo y condición (avisos sobre salidas guardadas)",
                           width=60)
    fig.suptitle(titulo, fontsize=11, wrap=True)
    nota = ("Barras por condición: directo · tito-viejo · tito-nuevo. "
            "Sin datos = condición sin traza (no es cero). Denominadores excluyen sin evaluar.")
    fig.text(0.5, 0.02, textwrap.fill(nota, width=100),
             ha="center", va="bottom", fontsize=8, style="italic", wrap=True)
    fig.tight_layout(rect=(0, 0.16, 1, 0.88))
    fig.savefig(str(ruta_base) + ".svg", format="svg", bbox_inches="tight", pad_inches=0.3)
    fig.savefig(str(ruta_base) + ".png", format="png", dpi=110,
                bbox_inches="tight", pad_inches=0.3)
    plt.close(fig)


def _figura_costos(ruta_base: Path, modelos: list[str], manifiesto: dict, analisis: dict) -> None:
    """Costo hasta el aviso apilado Tito + SLM, por modelo y condición.

    Suma `tito_ms_total`/`slm_ms_total` del análisis guardado (prefijo hasta
    el aviso incluido, sin doble conteo). La preparación queda en nota aparte,
    fuera del costo por línea. Sin traza: `sin datos`, no cero.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    import textwrap
    from matplotlib.patches import Patch

    n = max(len(modelos), 1)
    fig, ax = plt.subplots(figsize=(min(7 + 1.2 * n, 15), 6.4))
    for gi, cond in enumerate(_CONDICIONES):
        for mi, modelo in enumerate(modelos):
            x = mi + (gi - 1) * 0.24
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
            ax.bar(x, tito, width=0.22, color=_COLORES[cond],
                   edgecolor="black", linewidth=0.5)
            ax.bar(x, slm, width=0.22, bottom=tito, color=_COLORES[cond],
                   edgecolor="black", linewidth=0.5, alpha=0.45,
                   hatch="//" if slm > 0 else None)
            ax.text(x, total, f"{total:,.0f} ms".replace(",", "."),
                    ha="center", va="bottom", fontsize=8)
    ax.set_xticks(list(range(n)))
    ax.set_xticklabels(modelos, rotation=30, ha="right", fontsize=9)
    ax.set_ylabel("ms hasta el aviso (o caso completo si nunca avisó)", fontsize=9)
    ax.set_xlabel("modelo", fontsize=9)
    ax.set_title(textwrap.fill("Costo por componente hasta el aviso: Tito (sólido) + SLM (claro)",
                               width=55),
                 fontsize=11, wrap=True)
    ax.grid(axis="y", linestyle=":", alpha=0.6)
    notas = []
    for nombre, clave in (("Tito viejo", "tito_viejo_preparacion"),
                          ("Tito nuevo", "tito_nuevo_preparacion")):
        prep = manifiesto.get(clave)
        if prep is None:
            notas.append(f"{nombre}: condición pendiente (sin preparación).")
        else:
            notas.append(f"{nombre}: artefacto {prep.get('artefacto_ms', '?')} ms, "
                         f"encoder {prep.get('encoder_ms', '?')} ms, "
                         f"calentamiento {prep.get('calentamiento_ms', '?')} ms "
                         f"(error: {prep.get('error') or 'ninguno'}).")
    nota_prep = "Preparación fuera del costo por línea — " + " ".join(notas)
    fig.text(0.5, 0.02, textwrap.fill(nota_prep, width=95),
             ha="center", va="bottom", fontsize=8, style="italic", wrap=True)
    handles = [Patch(facecolor=_COLORES[cond], edgecolor="black", label=cond)
               for cond in _CONDICIONES]
    handles.append(Patch(facecolor="white", edgecolor="black", hatch="//",
                         label="tramo SLM (claro con trama)"))
    ax.legend(handles=handles, title="condición", fontsize=8, loc="upper right")
    fig.tight_layout(rect=(0, 0.20, 1, 0.88))
    fig.savefig(str(ruta_base) + ".svg", format="svg", bbox_inches="tight", pad_inches=0.3)
    fig.savefig(str(ruta_base) + ".png", format="png", dpi=110,
                bbox_inches="tight", pad_inches=0.3)
    plt.close(fig)


def generar_graficos(informe_md: Path, manifiesto: dict, analisis: dict, filas: list[dict]) -> list[str]:
    """Dos figuras Matplotlib (SVG + PNG) desde salidas guardadas.

    Calidad por modelo/condición (vishing con aviso vs falsas alarmas, con
    denominadores) y costo Tito+SLM hasta el aviso. Regenerable sin
    inferencia: solo lee `manifiesto` + `analisis` ya calculados.
    """
    modelos = manifiesto.get("funcionales", {}).get("modelos", [])
    prefijo = informe_md.stem
    if prefijo != "informe_101" and prefijo.endswith("_informe_101"):
        prefijo = prefijo[: -len("_informe_101")]
    base_avisos = informe_md.parent / (prefijo + "_grafico_avisos")
    base_costos = informe_md.parent / (prefijo + "_grafico_costos")
    _figura_calidad(base_avisos, modelos, analisis)
    _figura_costos(base_costos, modelos, manifiesto, analisis)
    return [base_avisos.name + ".svg", base_avisos.name + ".png",
            base_costos.name + ".svg", base_costos.name + ".png"]


def nombres_salida(corrida: dict) -> tuple[Path, list[str]]:
    """Rutas del informe y sus gráficos (legado o prefijo)."""
    if corrida["modo"] == "legado":
        return (corrida["base"] / "informe_101.md",
                ["informe_101_grafico_avisos.svg", "informe_101_grafico_avisos.png",
                 "informe_101_grafico_costos.svg", "informe_101_grafico_costos.png"])
    pref = corrida["prefijo"]
    return (corrida["base"] / (pref + "_informe_101.md"),
            [pref + "_grafico_avisos.svg", pref + "_grafico_avisos.png",
             pref + "_grafico_costos.svg", pref + "_grafico_costos.png"])


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
    L.append("## Gráficos (Matplotlib SVG+PNG regenerables desde salidas guardadas)")
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
