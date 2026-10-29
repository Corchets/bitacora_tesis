"""«Riesgo primero»: cuánto se gana en tiempo y qué política de aviso conviene, sin correr modelos.

Lee una o más corridas de `correr.py` y, para cada config `slm|…`, toma la serie de
`riesgo` línea por línea (una respuesta inválida cuenta como 0, como en `combinar.py`).
Prueba políticas que acumulan el puntaje entre líneas (idea de Mateo):

- `umbral`: avisa en la primera línea con riesgo > τ;
- `k seguidas`: k líneas seguidas con riesgo > τ;
- `media w`: la media de las últimas w líneas > τ;
- `ema α`: s = α·riesgo + (1 − α)·s anterior > τ (suma con olvido);
- `alerta del modelo`: solo para prompts de un paso (`tarea`, `v2`), el campo `alerta_sugerida`.

Las métricas son sobre **todas** las estafas, también las que cortan antes del pedido
(minuta del 2026-10-28), con la meta del tutor: ≥ 80 % de estafas con aviso y ≤ 15 % de
falsas alarmas. Para no elegir y medir sobre lo mismo, la mejor política de cada config se
elige en la mitad A de los casos y se informa en la B (`mitades` de `combinar.py`).

    python analisis/2026-10-29-riesgo-primero/acumular.py corridas/<una> [corridas/<otra> ...]

Escribe `acumular.md` junto a este script (o en `--salida`).

> **Estado: propuesta sin discutir.** Todo es desarrollo: no reemplaza el test reservado,
> no elige modelo (D09) ni cierra la política de alerta (D08).
"""

from __future__ import annotations

import argparse
import csv
import statistics
import sys
from collections import Counter
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SLM = AQUI.parents[1]
sys.path.insert(0, str(SLM))
sys.path.insert(0, str(AQUI.parent / "2026-10-21-pasada-0"))

import casos  # noqa: E402
import resumen  # noqa: E402
from combinar import aviso, mitades, wilson  # noqa: E402

TAUS = (0.5, 0.6, 0.7, 0.8, 0.9)
KS = (2, 3)
VENTANAS = (2, 3)
ALFAS = (0.3, 0.5, 0.7)
META_ESTAFAS, META_FA = 0.80, 0.15


def _float(x: str) -> float | None:
    return float(x) if x not in ("", None) else None


def cargar(carpetas: list[Path]) -> dict[str, dict[str, list[dict]]]:
    """config → case_id → filas ordenadas por línea (solo detectores SLM)."""
    datos: dict[str, dict[str, dict[int, dict]]] = {}
    for carpeta in carpetas:
        with (carpeta / "actualizaciones.csv").open(encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                if r["detector"] != "slm":
                    continue
                datos.setdefault(r["config"], {}).setdefault(r["case_id"], {})[int(r["linea"])] = r
    return {cfg: {c: [ls[i] for i in sorted(ls)] for c, ls in cs.items()} for cfg, cs in datos.items()}


def completos(por_caso: dict[str, list[dict]]) -> list[str]:
    """Casos con todas sus líneas evaluadas (una corrida cortada deja el último a medias)."""
    return sorted(c for c, filas in por_caso.items() if len(filas) == len(casos.cargar_texto(c)))


def serie(filas: list[dict]) -> tuple[list[float], list[bool]]:
    riesgos, alertas = [], []
    for f in filas:
        valida = f["valida"] == "true"
        riesgos.append(float(f["riesgo"]) if valida and f["riesgo"] else 0.0)
        alertas.append(valida and f["alerta_sugerida"] == "true")
    return riesgos, alertas


def _media_movil(xs: list[float], w: int) -> list[float]:
    return [statistics.fmean(xs[max(0, i - w + 1): i + 1]) for i in range(len(xs))]


def _ema(xs: list[float], alfa: float) -> list[float]:
    salida, s = [], 0.0
    for x in xs:
        s = alfa * x + (1 - alfa) * s
        salida.append(s)
    return salida


def politicas(un_paso: bool) -> list[tuple[str, callable]]:
    """(nombre, función (riesgos, alertas) → línea del aviso o None)."""
    pols = []
    if un_paso:
        pols.append(("alerta del modelo", lambda r, a: aviso(a, 1)))
    for t in TAUS:
        pols.append((f"umbral > {t}", lambda r, a, t=t: aviso([x > t for x in r], 1)))
        for k in KS:
            pols.append((f"{k} seguidas > {t}", lambda r, a, t=t, k=k: aviso([x > t for x in r], k)))
        for w in VENTANAS:
            pols.append((f"media {w} > {t}", lambda r, a, t=t, w=w: aviso([x > t for x in _media_movil(r, w)], 1)))
        for al in ALFAS:
            pols.append((f"ema {al} > {t}", lambda r, a, t=t, al=al: aviso([x > t for x in _ema(r, al)], 1)))
    return pols


def medir(avisos: dict[str, int | None], ids: list[str], refs: dict) -> dict:
    tp = nv = fp = nl = 0
    lugares = Counter()
    for c in ids:
        a = avisos[c]
        if refs[c]["clase"] in casos.LEGITIMAS:
            nl += 1
            fp += a is not None
        else:
            nv += 1
            tp += a is not None
            if a is not None:
                lugares[resumen.categoria(refs[c], a)] += 1
    rec, fa = (tp / nv if nv else 0.0), (fp / nl if nl else 0.0)
    return {"tp": tp, "nv": nv, "fp": fp, "nl": nl, "rec": rec, "fa": fa, "lugares": lugares,
            "meta": rec >= META_ESTAFAS and fa <= META_FA}


def latencias(por_caso: dict[str, list[dict]], ids: list[str]) -> dict:
    filas = [f for c in ids for f in por_caso[c]]

    def nums(campo: str) -> list[float]:
        return [v for v in (_float(f.get(campo, "")) for f in filas) if v is not None]

    ms, ms1, ms2, tok = nums("ms"), nums("ms_etapa1"), nums("ms_etapa2"), nums("tokens_salida")
    por_llamada = [sum(_float(f["ms"]) or 0 for f in por_caso[c]) for c in ids]

    def p(xs: list[float], q: float) -> float | None:
        return statistics.quantiles(xs, n=100)[q - 1] if len(xs) >= 2 else (xs[0] if xs else None)

    return {
        "lineas": len(filas),
        "invalidas": sum(f["valida"] != "true" for f in filas),
        "ms_p50": p(ms, 50), "ms_p95": p(ms, 95),
        "ms1_p50": p(ms1, 50), "ms2_p50": p(ms2, 50), "con_etapa2": len(ms2),
        "tokens_p50": p(tok, 50),
        "llamada_p50": p(por_llamada, 50),
    }


def _ms(x: float | None) -> str:
    return "—" if x is None else f"{x:.0f}"


def _md(cfg: str) -> str:
    return "`" + cfg.replace("|", "\\|") + "`"


def _pct(k: int, n: int) -> str:
    return f"{k}/{n} ({100 * k / n:.0f} %)" if n else "—"


def analizar(carpetas: list[Path]) -> str:
    datos = cargar(carpetas)
    if not datos:
        return "No hay detectores SLM en las corridas indicadas.\n"
    salida = [
        "# «Riesgo primero»: latencia y políticas que acumulan el puntaje",
        "",
        "Corridas: " + ", ".join(f"`{c.name}`" for c in carpetas),
        "",
        f"Meta del tutor: ≥ {META_ESTAFAS:.0%} de estafas con aviso (sobre todas) y ≤ {META_FA:.0%} de falsas alarmas.",
        "",
        "## Latencia por config",
        "",
        "| Config | Casos | Líneas | Inválidas | ms/línea p50 | p95 | Etapa 1 p50 | Etapa 2 p50 (líneas) | Tokens salida p50 | ms/llamada p50 |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    detalle = []
    for cfg, por_caso in sorted(datos.items()):
        ids = completos(por_caso)
        if not ids:
            continue
        refs = {c: casos.cargar_referencia(c) for c in ids}
        lat = latencias(por_caso, ids)
        salida.append(
            f"| {_md(cfg)} | {len(ids)} | {lat['lineas']} | {lat['invalidas']} | {_ms(lat['ms_p50'])} | {_ms(lat['ms_p95'])} | "
            f"{_ms(lat['ms1_p50'])} | {_ms(lat['ms2_p50'])} ({lat['con_etapa2']}) | {_ms(lat['tokens_p50'])} | {_ms(lat['llamada_p50'])} |"
        )
        un_paso = cfg.split("|")[2] != "riesgo" if cfg.count("|") >= 2 else True
        a, b = mitades(ids, refs)
        series = {c: serie(por_caso[c]) for c in ids}
        resultados = []
        for nombre, f in politicas(un_paso):
            avisos = {c: f(*series[c]) for c in ids}
            resultados.append((nombre, medir(avisos, ids, refs), medir(avisos, a, refs), medir(avisos, b, refs)))
        detalle += [
            "", f"### {_md(cfg)}", "",
            "| Política | Estafas con aviso | Falsas alarmas | Antes / en el pedido | Meta |",
            "|---|---|---|---|---|",
        ]
        for nombre, m, _, _ in resultados:
            temprano = m["lugares"]["antes_del_pedido"] + m["lugares"]["en_el_pedido"]
            detalle.append(f"| {nombre} | {_pct(m['tp'], m['nv'])} | {_pct(m['fp'], m['nl'])} | {temprano} | {'✔' if m['meta'] else ''} |")
        # Elegida en A: la que cumple la meta con más estafas; si ninguna, la de más estafas con FA ≤ meta.
        candidatas = [x for x in resultados if x[2]["fa"] <= META_FA] or resultados
        nombre, _, sel, ver = max(candidatas, key=lambda x: (x[2]["rec"], -x[2]["fa"]))
        detalle += [
            "",
            f"Elegida en la mitad A ({len(a)} casos): **{nombre}** · estafas {_pct(sel['tp'], sel['nv'])}, FA {_pct(sel['fp'], sel['nl'])}.",
            f"En la mitad B ({len(b)} casos): estafas {_pct(ver['tp'], ver['nv'])} (IC 95 % {wilson(ver['tp'], ver['nv'])}), "
            f"FA {_pct(ver['fp'], ver['nl'])} (IC 95 % {wilson(ver['fp'], ver['nl'])}).",
        ]
    salida += ["", "## Políticas por config (todos los casos completos)"] + detalle
    salida += [
        "",
        "`ms/línea` es la suma de las dos etapas donde corrió la 2. Con `riesgo`, la etapa 2 solo",
        "corre en las líneas con riesgo > umbral de la corrida; en un sistema real alcanza con correrla",
        "una vez, en la línea del aviso.",
        "",
    ]
    return "\n".join(salida)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("corridas", nargs="+", type=Path, help="carpetas de corridas/ (una o más)")
    ap.add_argument("--salida", type=Path, default=AQUI / "acumular.md")
    args = ap.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    texto = analizar([c.resolve() for c in args.corridas])
    args.salida.write_text(texto, encoding="utf-8")
    print(texto)
    print(f"Escrito en {args.salida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
