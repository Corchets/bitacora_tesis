"""Informe regenerable de la matriz #101 (sin inferencia).

Lee `manifiesto.json` + `actualizaciones.csv` de una corrida `matriz_101.py`
y escribe `informe_101.md` en la misma carpeta: por modelo y caso, aviso de
cada condición (directo, Tito viejo→SLM, Tito nuevo→SLM), oportunidad
respecto de T_R/T_C disponibles en las líneas, derivación, consultas,
tokens y costo por componente y hasta el aviso. Conserva fallos,
inválidos, no avisos y denominadores.

Uso: python informe_101.py corridas/<carpeta_101>

No declara éxito ni compara costos con corridas históricas completas:
los costos son prefijos hasta el aviso. No adopta metas (95/5 sigue
abierta en D08) ni cierra #101 por sí solo: la cobertura pendiente queda
explícita.
"""

from __future__ import annotations

import sys
from pathlib import Path

import casos
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


def detalle_condicion(filas: list[dict], analisis_cfg: dict, config: str) -> dict[str, dict]:
    """Derivación, consultas y costos por caso para una condición filtrada.

    Misma definición que `resumen.analisis_filtro` (prefijo hasta el aviso
    incluido; omitidas = SLM no consultado; sin doble conteo Tito+SLM),
    parametrizada por configuración para viejo y nuevo por separado.
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
            "fallos_tito": sum(1 for f in prefijo if (f.get("tito_error") or "").strip()),
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


def armar_informe(carpeta: Path) -> str:
    manifiesto, filas = resumen.leer_corrida(carpeta)
    if manifiesto.get("matriz") != "matriz-101":
        raise ValueError(f"{carpeta} no es una corrida matriz-101.")
    analisis = resumen.analizar(manifiesto, filas)
    funcionales = manifiesto.get("funcionales", {})
    modelos = funcionales.get("modelos", [])
    refs = {c: casos.cargar_referencia(c) for c in manifiesto["casos"]}
    cob = manifiesto.get("cobertura", {})
    L = [f"# Informe matriz #101 — `{carpeta.name}`", ""]
    L.append(f"Recorridos completados: {cob.get('completados', '?')}/{cob.get('esperados', '?')} "
             f"(pendientes: {cob.get('pendientes', '?')}).")
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
        cal = inv.get("calentamiento_ms", inv.get("carga_ms"))
        L.append(f"- Calentamiento (fuera del costo por línea): {cal} ms "
                 f"(memoria {inv.get('memoria', '?')}).")
        L.append("")
        L.append("| Caso | Clase | T_R/T_C | Aviso directo | Aviso viejo | Aviso nuevo | "
                 "Deriv. V/N | Cons. D/V/N | Evit. V/N | Tokens D/V/N | ms hasta aviso D/V/N |")
        L.append("|---|---|---|---|---|---|---|---|---|---|---|")
        for cid in sorted(refs):
            avisos, deriv, cons, evit, toks, mss = {}, {}, {}, {}, {}, {}
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
                elif a:
                    cons[cond] = len([f for f in filas if f["config"] == cfg and f["case_id"] == cid
                                      and (int(f["linea"]) <= a["aviso"] if a["aviso"] else True)])
                    toks[cond] = f"{a['tokens_hasta_aviso']:.0f}"
                    mss[cond] = f"{a['ms_hasta_aviso']:.0f}"
            ref = refs[cid]
            trtc = f"{ref.get('t_r_linea') or '—'}/{ref.get('t_c_linea') or '—'}"
            L.append(f"| `{cid}` | {ref['clase']} | {trtc} | "
                     f"{avisos.get('directo', 's/t')} | {avisos.get('tito-viejo', 's/t')} | "
                     f"{avisos.get('tito-nuevo', 's/t')} | "
                     f"{deriv.get('tito-viejo', 's/t')}/{deriv.get('tito-nuevo', 's/t')} | "
                     f"{cons.get('directo', 's/t')}/{cons.get('tito-viejo', 's/t')}/{cons.get('tito-nuevo', 's/t')} | "
                     f"{evit.get('tito-viejo', 's/t')}/{evit.get('tito-nuevo', 's/t')} | "
                     f"{toks.get('directo', 's/t')}/{toks.get('tito-viejo', 's/t')}/{toks.get('tito-nuevo', 's/t')} | "
                     f"{mss.get('directo', 's/t')}/{mss.get('tito-viejo', 's/t')}/{mss.get('tito-nuevo', 's/t')} |")
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
                     f"encoder {prep.get('encoder_ms', '?')} ms, "
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
        sys.exit("uso: python informe_101.py corridas/<carpeta_101>")
    carpeta = (AQUI / args[0]).resolve()
    (carpeta / "informe_101.md").write_text(armar_informe(carpeta), encoding="utf-8")
    print(f"guardado en {carpeta / 'informe_101.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())