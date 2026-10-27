"""Reporte comparativo por conversación para #71 (parte de #68).

Lee `manifiesto.json` + `actualizaciones.csv` de una corrida y escribe
`comparacion.md` en la misma carpeta: ahorro, detección, falsas alarmas,
derivación y aviso por conversación, con la doble lectura de TR-04 y TR-07
calculada sobre las mismas predicciones (sin repetir inferencia).

Uso: python comparar.py corridas/<carpeta>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import resumen
from resumen import analisis_filtro

RAIZ = Path(__file__).resolve().parent

# Doble lectura documentada en las referencias (notas de TR-04 y TR-07):
# misma predicción, otra marca candidata. No cambia la referencia original.
LECTURAS_ALT = {
    "TR-04-pedido-tras-charla-larga": {"t_r_linea": 21, "t_c_linea": 22},
    "TR-07-pedido-partido-en-dos-lineas": {"t_r_linea": 8, "t_c_linea": 9},
}


def _margen(ref: dict, aviso: int | None) -> str:
    if aviso is None:
        return "sin aviso"
    if ref["clase"] != "vishing":
        return "falsa alarma"
    tr, tc = ref.get("t_r_linea"), ref.get("t_c_linea")
    if tr is None:
        return "aviso (vishing sin pedido de referencia)"
    if aviso < tr:
        return f"{aviso - tr} líneas (antes del pedido L{tr})"
    if aviso == tr:
        return "en el pedido"
    if tc is not None and aviso >= tc:
        return f"+{aviso - tr} (en/después del cumplimiento L{tc})"
    return f"+{aviso - tr} (después del pedido)"


def armar_comparacion(carpeta: Path) -> str:
    manifiesto, filas = resumen.leer_corrida(carpeta)
    analisis = resumen.analizar(manifiesto, filas)
    configs = [c["config"] for c in manifiesto["configs"]]
    directo = next(c for c in configs if c.startswith("slm|"))
    filtrado = next(c for c in configs if c.startswith("tito-slm|"))
    detalle = analisis_filtro(manifiesto, filas, analisis)[filtrado]
    refs = {c: resumen.casos.cargar_referencia(c) for c in manifiesto["casos"]}
    f = manifiesto.get("filtro_tito", {})
    titoreal = "real" if str(f.get("tito", "")).startswith("real-") else "simulado"

    filas_cfg = {}
    for cfg in (directo, filtrado):
        por_caso: dict[str, list[dict]] = {}
        for r in filas:
            if r["config"] == cfg:
                por_caso.setdefault(r["case_id"], []).append(r)
        filas_cfg[cfg] = por_caso

    def toks(fs):
        return sum((int(r["tokens_prompt"]) if r["tokens_prompt"] else 0)
                   + (int(r["tokens_salida"]) if r["tokens_salida"] else 0) for r in fs)

    L = [f"# Comparación {directo.split('|')[1]}: directo vs Tito→SLM", ""]
    L.append(f"Corrida `{carpeta.name}` · Tito {titoreal} (`{f.get('tito', '?')}`, umbral {f.get('umbral', '?')}).")
    L.append("Mismas predicciones en ambas lecturas de marcas; la referencia original no cambia.")
    L.append("")
    L.append("## Por conversación")
    L.append("")
    L.append("| Caso | Clase | Deriv. | Aviso directo | Aviso filtrado | Cons. D/F | Evit. | Tokens D/F | Costo ms D/F |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for cid in sorted(refs):
        a_d, a_f = analisis[directo][cid], analisis[filtrado][cid]
        d = detalle[cid]
        fd, ff = filas_cfg[directo][cid], filas_cfg[filtrado][cid]
        ms_d = sum(float(r["ms"]) for r in fd if r["ms"])
        L.append(f"| `{cid}` | {refs[cid]['clase']} | {d['derivacion'] or 'nunca'} | "
                 f"{('L' + str(a_d['aviso'])) if a_d['aviso'] else '—'} | "
                 f"{('L' + str(a_f['aviso'])) if a_f['aviso'] else '—'} | "
                 f"{len(fd)}/{d['consultas']} | {d['evitadas']} | {toks(fd)}/{toks(ff)} | "
                 f"{ms_d:.0f}/{d['ms_total']:.0f} |")
    L.append("")
    tot_d = sum(toks(v) for v in filas_cfg[directo].values())
    tot_f = sum(toks(v) for v in filas_cfg[filtrado].values())
    L.append(f"Tokens totales (prompt+salida): directo {tot_d}, filtrado {tot_f}. "
             "Carga, calentamiento y ajuste van por separado abajo.")
    L.append("")
    modo = manifiesto.get("modo_termino", "no informado (corrida histórica, conversación completa)")
    ms_d = sum(analisis[directo][cid]["ms_hasta_aviso"] for cid in sorted(refs))
    ms_f = sum(detalle[cid]["ms_hasta_aviso"] for cid in sorted(refs))
    tito_f = sum(detalle[cid]["tito_ms_total"] for cid in sorted(refs))
    slm_f = sum(detalle[cid]["slm_ms_total"] for cid in sorted(refs))
    hay_split = any((f.get("tito_ms") or "") != "" or (f.get("slm_ms") or "") != "" for f in filas)
    L.append(f"Modo de término: `{modo}`: cada llamada termina en su primer aviso válido; "
             "los costos de esta tabla son hasta el aviso (o la conversación completa si nunca avisó).")
    if hay_split:
        L.append(f"Costo hasta el aviso: directo {ms_d:.0f} ms; filtrado {ms_f:.0f} ms "
                 f"(Tito {tito_f:.0f} + SLM {slm_f:.0f}, sin doble conteo).")
    else:
        L.append(f"Costo hasta el aviso: directo {ms_d:.0f} ms; filtrado {ms_f:.0f} ms "
                 "(componentes Tito/SLM no informados en esta traza histórica, sin doble conteo).")
    L.append("")
    L.append("## Cambios de aviso entre variantes")
    L.append("")
    for cid in sorted(refs):
        a_d, a_f, d = analisis[directo][cid], analisis[filtrado][cid], detalle[cid]
        if a_d["aviso"] != a_f["aviso"]:
            fila = next((r for r in filas_cfg[filtrado][cid] if r["aviso"] == "true"), None)
            ind = f" (indicio L{fila['indicio_linea']} p={fila['indicio_puntaje']})" if fila and fila["indicio_linea"] else ""
            L.append(f"- `{cid}`: directo {('L' + str(a_d['aviso'])) if a_d['aviso'] else 'sin aviso'} → "
                     f"filtrado {('L' + str(a_f['aviso'])) if a_f['aviso'] else 'sin aviso'}, "
                     f"derivación L{d['derivacion']}{ind}.")
    L.append("")
    L.append("## Doble lectura de marcas (mismas predicciones)")
    L.append("")
    for cid, alt in LECTURAS_ALT.items():
        if cid not in refs:
            continue  # la doble lectura solo aplica a las corridas que incluyen el caso
        ref = dict(refs[cid])
        L.append(f"### `{cid}`: referencia T_R={ref['t_r_linea']}/T_C={ref['t_c_linea']}, "
                 f"alternativa T_R={alt['t_r_linea']}/T_C={alt['t_c_linea']}")
        for cfg, nombre in ((directo, "directo"), (filtrado, "filtrado")):
            av = analisis[cfg][cid]["aviso"]
            L.append(f"- {nombre} (aviso {('L' + str(av)) if av else 'ninguno'}): "
                     f"referencia → {_margen(ref, av)}; alternativa → {_margen({**ref, **alt}, av)}.")
        L.append("")
    L.append("## Motivos y citas (avisos anteriores al pedido incluidos)")
    L.append("")
    L.append("Referencias provisorias: ningún caso tiene revisión humana; las lecturas de")
    L.append("pedido inventado o sospecha reforzada son del autor del reporte, no del manual.")
    L.append("")
    for cid in sorted(refs):
        ref = refs[cid]
        for cfg, nombre in ((directo, "directo"), (filtrado, "filtrado")):
            a = analisis[cfg][cid]
            if a["aviso"] is None:
                continue
            fila = a["aviso_fila"]
            prev = ""
            if ref["clase"] == "vishing" and ref.get("t_r_linea") is not None and a["aviso"] < ref["t_r_linea"]:
                prev = f" — anterior al pedido (T_R L{ref['t_r_linea']})"
            cita = "cita textual" if fila["evidencia_en_texto"] == "true" else "cita NO textual"
            L.append(f"- `{cid}` · {nombre} · L{a['aviso']}{prev}: «{fila['motivo']}» — {cita}: «{fila['evidencia']}»")
    L.append("")
    L.append("## Runtime común y hardware")
    L.append("")
    L.append(f"- Comando: `{manifiesto.get('comando', '?')}`")
    L.append(f"- Código: `{manifiesto.get('codigo', {}).get('commit', '?')}` "
             f"(cambios sin commit en la carpeta: {manifiesto.get('codigo', {}).get('cambios_sin_commit_en_la_carpeta')})")
    ol = manifiesto.get("ollama", {})
    L.append(f"- Ollama {ol.get('version', '?')} en {ol.get('url', '?')}, digests: {ol.get('digests', {})}")
    L.append(f"- Chequeo previo de contrato JSON: `chequeo-contrato.json` en esta carpeta "
             "(digest verificado, `think: false`, esquema, `num_ctx` 4096 aceptados; "
             "una incompatibilidad o exceso de contexto deja error explícito, sin sustitución).")
    p = manifiesto.get("parametros_slm", {})
    lote = (p.get("hardware") or {}).get("num_batch", "?")
    L.append(f"- Parámetros SLM: prompt `tarea`, hablantes `ab`, seed {p.get('seed')}, "
             f"temperatura {p.get('temperatura')}, contexto {p.get('num_ctx')}, lote {lote}, "
             f"timeout {p.get('timeout_s')} s, razonamiento desactivado cuando el runtime lo admite.")
    hw_path = carpeta / "hardware.json"
    if hw_path.exists():
        hw = json.loads(hw_path.read_text(encoding="utf-8"))
        L.append(f"- GPU: {hw.get('gpu')}; servidor: {hw.get('servidor_ollama')}.")
        L.append(f"- Intérprete de la corrida: `{hw.get('interprete_corrida')}`; "
                 f"librerías Tito: {hw.get('librerias_tito')}.")
        L.append(f"- Límites: {hw.get('limites')}.")
    L.append("")
    L.append("## Carga, calentamiento y ajuste (por separado, no en el costo por línea)")
    L.append("")
    for modelo, info in manifiesto.get("modelos", {}).items():
        if info.get("error"):
            L.append(f"- `{modelo}`: ERROR al calentar: {info['error']}")
        else:
            arranque = info.get("arranque_ms", "no informado")
            cal = info.get("calentamiento_ms", info.get("carga_ms"))
            L.append(f"- `{modelo}`: arranque {arranque} ms, calentamiento {cal} ms "
                     f"(carga {info.get('carga_ms')} ms), memoria {info.get('memoria')}, "
                     f"think={info.get('pensar')}.")
    ft = manifiesto.get("filtro_tito") or {}
    try:
        arte = json.loads(Path(ft["modelo"]).read_text(encoding="utf-8"))
        ent = arte.get("entrenamiento", {})
        L.append(f"- Tito (ajuste único, fuera de línea): incrustación {ent.get('ms_incrustacion')} ms, "
                 f"ajuste {ent.get('ms_ajuste')} ms, seed {arte['config_regresion']['semilla']}, "
                 f"sha {ft.get('artefacto_sha256', '')[:12]}…")
    except (KeyError, OSError, ValueError, TypeError):
        L.append("- Tito: artefacto no disponible para informar el ajuste.")
    if "arranque_ms" in ft or "nota" in ft:
        L.append(f"- Tito en esta corrida: arranque {ft.get('arranque_ms')} ms, "
                 f"calentamiento {ft.get('calentamiento_ms')} ms "
                 f"(unidad: {ft.get('unidad', 'ms')}; {ft.get('nota', '')}).")
    L.append("")
    L.append("## Límites de interpretación")
    L.append("")
    L.append("- Casos escritos de desarrollo, sin revisión humana; posiciones en líneas, sin segundos ni RTF.")
    L.append("- La comparación mide activación selectiva + indicio falible juntos: "
             "no separa el efecto del indicio del efecto de la activación.")
    L.append("- El riesgo del SLM no está calibrado; el umbral 0,5 de Tito es convención exploratoria.")
    return "\n".join(L) + "\n"


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if len(args) != 1:
        sys.exit("uso: python comparar.py corridas/<carpeta>")
    carpeta = (RAIZ / args[0]).resolve()
    (carpeta / "comparacion.md").write_text(armar_comparacion(carpeta), encoding="utf-8")
    print(f"guardado en {carpeta / 'comparacion.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
