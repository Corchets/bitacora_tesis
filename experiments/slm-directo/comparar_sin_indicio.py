"""Compara caso por caso SLM solo, Tito→SLM con indicio y Tito→SLM sin indicio.

> **Estado: propuesta sin discutir.** Diagnóstico sobre las 150 conversaciones de
> desarrollo; no toca el test reservado. Ver `colab/README-SIN-INDICIO.md`.

Uso, desde experiments/slm-directo:
    python comparar_sin_indicio.py resultados-sin-indicio.zip
    python comparar_sin_indicio.py corridas/2026-11-04_132229_e2b-directo-150 \\
        corridas/2026-11-04_003715_e2b-tito-viejo-150 [--salida comparacion.md]

Acepta ZIP o carpetas de corrida (con `actualizaciones.csv`). Las condiciones se
reconocen por la columna `detector`:
    slm                   → «solo»; si aparece en una segunda carpeta, «solo-rep»
                            (repetición para medir el no determinismo)
    tito-slm              → «con-indicio»
    tito-slm-sin-indicio  → «sin-indicio»
Las carpetas se recorren en el orden dado (dentro de un ZIP, por nombre, que
empieza con fecha y hora): la primera con `slm` es «solo».

Solo lee los CSV y las referencias; no corre modelos. Lógica tomada de
`corridas/2026-11-04_132229_e2b-directo-150/comparar_directo_vs_tito.py`.
"""

from __future__ import annotations

import argparse
import collections
import csv
import statistics
import sys
import tempfile
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import casos  # noqa: E402

NOMBRES = {"slm": "solo", "tito-slm": "con-indicio", "tito-slm-sin-indicio": "sin-indicio"}
ORDEN = ("solo", "con-indicio", "sin-indicio", "solo-rep")
TITULOS = {
    "solo": "SLM solo",
    "con-indicio": "Tito → SLM con indicio",
    "sin-indicio": "Tito → SLM sin indicio",
    "solo-rep": "SLM solo (repetición)",
}
PARES = (
    ("solo", "con-indicio"),
    ("solo", "sin-indicio"),
    ("con-indicio", "sin-indicio"),
    ("solo", "solo-rep"),
)


def carpetas_de(rutas: list[Path], tmp: Path) -> list[Path]:
    """Carpetas de corrida en orden; los ZIP se extraen en `tmp`."""
    salida: list[Path] = []
    for i, ruta in enumerate(rutas):
        if ruta.is_file() and ruta.suffix == ".zip":
            destino = tmp / f"zip{i}"
            with zipfile.ZipFile(ruta) as z:
                z.extractall(destino)
            salida += sorted(p.parent for p in destino.rglob("actualizaciones.csv"))
        elif (ruta / "actualizaciones.csv").exists():
            salida.append(ruta)
        elif ruta.is_dir():
            salida += sorted(p.parent for p in ruta.rglob("actualizaciones.csv"))
        else:
            sys.exit(f"No encuentro corridas en {ruta}")
    return salida


def cargar(carpetas: list[Path]) -> tuple[dict[str, dict], dict[str, str]]:
    """{condición: {case_id: [filas ordenadas]}} y {condición: carpeta/config}."""
    condiciones: dict[str, dict] = {}
    origen: dict[str, str] = {}
    for carpeta in carpetas:
        por_det: dict[str, dict] = collections.defaultdict(lambda: collections.defaultdict(list))
        configs: dict[str, set] = collections.defaultdict(set)
        with open(carpeta / "actualizaciones.csv", encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                if r["detector"] in NOMBRES:
                    por_det[r["detector"]][r["case_id"]].append(r)
                    configs[r["detector"]].add(r["config"])
        for det, filas in por_det.items():
            nombre = NOMBRES[det]
            if nombre in condiciones:
                if nombre != "solo" or "solo-rep" in condiciones:
                    sys.exit(f"Condición {nombre!r} repetida en {carpeta.name}; pasá menos carpetas.")
                nombre = "solo-rep"
            if len(configs[det]) != 1:
                sys.exit(f"{carpeta.name}: más de una configuración {det}: {sorted(configs[det])}")
            for v in filas.values():
                v.sort(key=lambda r: int(r["linea"]))
            condiciones[nombre] = filas
            origen[nombre] = f"{carpeta.name} · `{next(iter(configs[det]))}`"
    return condiciones, origen


def aviso(filas) -> int | None:
    return next((int(r["linea"]) for r in filas if r["aviso"] == "true"), None)


def consultada(r) -> bool:
    return (r.get("consulta") or "") != "omitida"


def momento(av: int | None, tr: int | None) -> str:
    if av is None:
        return "sin aviso"
    if not tr:
        return "sin T_R"
    return "antes" if av < tr else "en" if av == tr else "después"


def analizar(condiciones: dict[str, dict]) -> tuple[list[dict], list[str]]:
    presentes = [c for c in ORDEN if c in condiciones]
    filas_casos = []
    # Solo los casos que tiene alguna corrida: los agregados después no cuentan como no procesados.
    corridos = {cid for cond in presentes for cid in condiciones[cond]}
    for cid in (c for c in casos.ids_de_casos("desarrollo") if c in corridos):
        ref = casos.cargar_referencia(cid)
        c = dict(cid=cid, clase=ref["clase"], tr=ref["t_r_linea"])
        for cond in presentes:
            filas = condiciones[cond].get(cid, [])
            c[cond] = aviso(filas)
            c[f"{cond}_procesado"] = bool(filas)
            c[f"{cond}_act"] = next((int(r["linea"]) for r in filas if consultada(r)), None)
        filas_casos.append(c)
    return filas_casos, presentes


def _pct(n: int, d: int) -> str:
    return f"{n}/{d} ({100 * n / d:.0f} %)" if d else f"{n}/0"


def tabla_global(cs: list[dict], presentes: list[str], condiciones: dict) -> list[str]:
    V = [c for c in cs if c["clase"] == "vishing"]
    VT = [c for c in V if c["tr"]]
    L = [c for c in cs if c["clase"] != "vishing"]
    filas = {}
    for cond in presentes:
        todas = [r for v in condiciones[cond].values() for r in v]
        cons = [r for r in todas if consultada(r)]
        mom = collections.Counter(momento(c[cond], c["tr"]) for c in VT)
        ms = [float(r["slm_ms"] or r["ms"]) for r in cons if (r.get("slm_ms") or r.get("ms"))]
        filas[cond] = {
            "Estafas con aviso": _pct(sum(c[cond] is not None for c in V), len(V)),
            "Estafas con pedido (T_R) con aviso": f"{sum(c[cond] is not None for c in VT)}/{len(VT)}",
            "· antes del pedido": str(mom["antes"]),
            "· en el pedido": str(mom["en"]),
            "· después del pedido": str(mom["después"]),
            "Falsas alarmas": _pct(sum(c[cond] is not None for c in L), len(L)),
            "· legítimas comunes": "{}/{}".format(
                sum(c[cond] is not None for c in L if c["clase"] == "legitima"),
                sum(1 for c in L if c["clase"] == "legitima")),
            "· legítimas difíciles": "{}/{}".format(
                sum(c[cond] is not None for c in L if c["clase"] == "legitima_dificil"),
                sum(1 for c in L if c["clase"] == "legitima_dificil")),
            "Consultas al SLM": f"{len(cons):,}".replace(",", "."),
            "Líneas omitidas por Tito": f"{len(todas) - len(cons):,}".replace(",", "."),
            "Fallos de JSON o tiempo": str(sum(1 for r in cons if r["valida"] != "true")),
            "Mediana del SLM por consulta (ms)": f"{statistics.median(ms):.0f}" if ms else "—",
            "Casos sin procesar": str(sum(not c[f"{cond}_procesado"] for c in cs)),
        }
    claves = list(next(iter(filas.values())).keys())
    salida = ["| | " + " | ".join(TITULOS[c] for c in presentes) + " |",
              "|---|" + "---|" * len(presentes)]
    salida += [f"| {k} | " + " | ".join(filas[c][k] for c in presentes) + " |" for k in claves]
    return salida


def seccion_activacion(cs: list[dict], presentes: list[str]) -> list[str]:
    salida = []
    VT = [c for c in cs if c["clase"] == "vishing" and c["tr"]]
    for cond in ("con-indicio", "sin-indicio"):
        if cond not in presentes:
            continue
        act = collections.Counter(
            "nunca" if c[f"{cond}_act"] is None else momento(c[f"{cond}_act"], c["tr"]) for c in VT)
        salida.append(f"- {TITULOS[cond]}: primera consulta antes del pedido en {act['antes']}, "
                      f"en el pedido en {act['en']}, después en {act['después']}, nunca en {act['nunca']} "
                      f"(de {len(VT)} estafas con `T_R`).")
    return salida


def seccion_par(cs: list[dict], condiciones: dict, a: str, b: str) -> list[str]:
    ta, tb = TITULOS[a], TITULOS[b]
    V = [c for c in cs if c["clase"] == "vishing"]
    L = [c for c in cs if c["clase"] != "vishing"]
    salida = [f"### {ta} contra {tb}", ""]
    ambos = [c for c in V if c[a] is not None and c[b] is not None]
    orden = collections.Counter(
        "igual" if c[a] == c[b] else f"{a} antes" if c[a] < c[b] else f"{b} antes" for c in ambos)
    salida.append(f"- Estafas en que avisan las dos: {len(ambos)} — misma línea {orden['igual']}, "
                  f"antes «{a}» {orden[f'{a} antes']}, antes «{b}» {orden[f'{b} antes']}.")
    adel = [c[b] - c[a] for c in ambos if c[a] < c[b]]
    if adel:
        salida.append(f"  - Adelanto medio de «{a}» cuando se adelanta: {statistics.mean(adel):.1f} líneas.")
    adel = [c[a] - c[b] for c in ambos if c[b] < c[a]]
    if adel:
        salida.append(f"  - Adelanto medio de «{b}» cuando se adelanta: {statistics.mean(adel):.1f} líneas.")

    def lista(xs):
        return ", ".join(f"`{c}`" for c in xs) if xs else "ninguna"

    salida.append(f"- Estafas que solo detecta «{a}» (pierde «{b}»): "
                  + lista([c["cid"] for c in V if c[a] is not None and c[b] is None]))
    salida.append(f"- Estafas que solo detecta «{b}» (gana «{b}»): "
                  + lista([c["cid"] for c in V if c[b] is not None and c[a] is None]))
    salida.append("- Estafas que no detecta ninguna: "
                  + lista([c["cid"] for c in V if c[a] is None and c[b] is None]))
    salida.append(f"- Falsas alarmas solo de «{a}»: "
                  + lista([c["cid"] for c in L if c[a] is not None and c[b] is None]))
    salida.append(f"- Falsas alarmas solo de «{b}»: "
                  + lista([c["cid"] for c in L if c[b] is not None and c[a] is None]))

    # Misma línea consultada (y válida) en las dos: ¿cambia la respuesta del SLM?
    clase = {c["cid"]: ("estafa" if c["clase"] == "vishing" else "legítima") for c in cs}
    ra = {(cid, r["linea"]): r for cid, v in condiciones[a].items() for r in v
          if consultada(r) and r["valida"] == "true"}
    cambio: collections.Counter = collections.Counter()
    ejemplos: dict = collections.defaultdict(list)
    comunes = 0
    for cid, v in condiciones[b].items():
        for r in v:
            k = (cid, r["linea"])
            if consultada(r) and r["valida"] == "true" and k in ra:
                comunes += 1
                if ra[k]["alerta_sugerida"] != r["alerta_sugerida"]:
                    sentido = f"alerta solo «{a}»" if ra[k]["alerta_sugerida"] == "true" else f"alerta solo «{b}»"
                    cambio[(clase[cid], sentido)] += 1
                    ejemplos[(clase[cid], sentido)].append(f"{cid}:L{r['linea']}")
    total = sum(cambio.values())
    salida.append(f"- Líneas consultadas en común: {comunes}; cambia `alerta_sugerida` en {total}"
                  + (f" ({100 * total / comunes:.1f} %)." if comunes else "."))
    if total:
        salida += ["", f"| | Alerta solo «{a}» | Alerta solo «{b}» |", "|---|---|---|"]
        for cl in ("estafa", "legítima"):
            salida.append(f"| {cl} | {cambio[(cl, f'alerta solo «{a}»')]} | {cambio[(cl, f'alerta solo «{b}»')]} |")
        salida.append("")
        for k in sorted(ejemplos):
            salida.append(f"  - {k[0]}, {k[1]}: " + ", ".join(f"`{e}`" for e in ejemplos[k]))
    salida.append("")
    return salida


def armar(rutas: list[Path]) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        carpetas = carpetas_de(rutas, Path(tmp))
        condiciones, origen = cargar(carpetas)
    if not condiciones:
        sys.exit("No hay filas de slm, tito-slm ni tito-slm-sin-indicio.")
    cs, presentes = analizar(condiciones)
    L = ["# SLM solo, Tito con indicio y Tito sin indicio (150 de desarrollo)", "",
         "> **Estado: propuesta sin discutir.** Diagnóstico sobre material de desarrollo, sin "
         "revisión humana de casos ni de `T_R`. No toca el test reservado.", "",
         "## Corridas", ""]
    L += [f"- **{TITULOS[c]}**: {origen[c]}" for c in presentes]
    L += ["", "## Resultado global", "", *tabla_global(cs, presentes, condiciones), ""]
    act = seccion_activacion(cs, presentes)
    if act:
        L += ["## Activación de Tito respecto del pedido", "", *act, ""]
    L += ["## Caso por caso", ""]
    for a, b in PARES:
        if a in presentes and b in presentes:
            L += seccion_par(cs, condiciones, a, b)
    return "\n".join(L).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("rutas", nargs="+", type=Path, help="ZIP de Colab o carpetas de corrida")
    p.add_argument("--salida", type=Path, help="escribir el informe en Markdown en este archivo")
    args = p.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    texto = armar(args.rutas)
    if args.salida:
        args.salida.write_text(texto, encoding="utf-8")
    print(texto)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
