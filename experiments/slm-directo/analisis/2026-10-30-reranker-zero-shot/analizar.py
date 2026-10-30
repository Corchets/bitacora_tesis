"""Reranker zero-shot: roles × políticas acumuladas, sin volver a correr modelos.

Lee corridas guardadas de `correr.py` (reranker, SLM, riesgo primero y reglas) y compara:

- **solo**: cada detector con políticas que acumulan el puntaje (idea de Mateo, como en
  `../2026-10-29-riesgo-primero/acumular.py`): umbral, 2 seguidas, media 3, EMA 0,3 y 0,5;
- **verificador** (rol C y H5): el SLM decide con su política y el reranker veta línea por
  línea; avisa en la primera línea donde los dos están de acuerdo;
- **filtro** (rol B): el reranker deriva al SLM en la primera línea con puntaje > τ (con
  `--reranker-etiquetas todas`, el máximo entre pedidos y maniobras) y desde ahí decide el
  SLM. Es una aproximación por compuerta: el SLM no recibe el bloque de indicio de #68.

Elige con la **selección** (particiones entrenamiento + validacion + diagnostico +
regresion de `PARTICIONES-TITO-2026-10-29.json`, 57 casos) y lo informa en
**`comparacion_20`** (las mismas 20 de #101 y de `rapida-20`). Nunca elige sobre
`comparacion_20` ni sobre `excluido_relacion_comparacion`: si se cruzan, se detiene.

    python analisis/2026-10-30-reranker-zero-shot/analizar.py corridas/<reranker> corridas/<slm> ...

Escribe `analisis.md` junto a este script (o en `--salida`).

> **Estado: propuesta sin discutir.** Desarrollo, sin revisión humana: no reemplaza el
> test reservado, no elige detector (D09) ni cierra la política de alerta (D08).
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import Counter
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SLM = AQUI.parents[1]
sys.path.insert(0, str(SLM))
sys.path.insert(0, str(AQUI.parent / "2026-10-21-pasada-0"))
sys.path.insert(0, str(AQUI.parent / "2026-10-29-riesgo-primero"))

import casos  # noqa: E402
import resumen  # noqa: E402
from acumular import _ema, _media_movil, cargar, completos  # noqa: E402
from combinar import wilson  # noqa: E402

PARTICIONES = SLM / "PARTICIONES-TITO-2026-10-29.json"
GRUPOS_SELECCION = ("entrenamiento", "validacion", "diagnostico", "regresion")
TAUS = (0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95)
TAUS_SLM = (0.5, 0.6, 0.7, 0.8, 0.9)
META_ESTAFAS, META_FA = 0.80, 0.15
TIPOS_R07 = {"mencion_sin_pedido", "pedido_razonable"}


def splits(ruta: Path = PARTICIONES) -> tuple[list[str], list[str]]:
    """(selección, informe). Falla si la selección toca el informe o sus casos relacionados."""
    d = json.loads(ruta.read_text(encoding="utf-8"))
    seleccion = sorted(c["case_id"] for c in d["conversaciones"] if c["particion_preparacion"] in GRUPOS_SELECCION)
    informe = sorted(d["evaluacion_ids"])
    vedados = set(informe) | {c["case_id"] for c in d["conversaciones"]
                              if c["particion_preparacion"] == "excluido_relacion_comparacion"}
    cruce = sorted(set(seleccion) & vedados)
    if cruce:
        raise ValueError(f"la selección incluye casos de informe o relacionados: {cruce}")
    return seleccion, informe


# ---------------------------------------------------------------- series y políticas

def _tipo(cfg: str) -> str:
    return cfg.split("|")[0]


def un_paso(cfg: str) -> bool:
    """El SLM de un paso trae su propia `alerta_sugerida`; reglas solo tienen esa."""
    partes = cfg.split("|")
    return partes[0] in ("reglas", "reglas_v2") or (partes[0] == "slm" and len(partes) > 2 and partes[2] != "riesgo")


def riesgos(filas: list[dict], todas: bool = False) -> list[float]:
    """Riesgo por línea (inválida = 0, como en combinar.py). `todas`: máximo de todas las
    etiquetas del reranker (pedidos y maniobras), para derivar en el rol filtro."""
    salida = []
    for f in filas:
        if f["valida"] != "true":
            salida.append(0.0)
        elif todas and f["detector"] == "reranker":
            salida.append(max(json.loads(f["crudo"])["puntajes"].values()))
        else:
            salida.append(float(f["riesgo"]) if f["riesgo"] else 0.0)
    return salida


def alertas(filas: list[dict]) -> list[bool]:
    return [f["valida"] == "true" and f["alerta_sugerida"] == "true" for f in filas]


def estados(nombre: str, r: list[float], a: list[bool]) -> list[bool]:
    """Si la política está «arriba» en cada línea. El aviso es la primera línea arriba."""
    if nombre == "alerta del modelo":
        return list(a)
    tipo, t = nombre.rsplit(" > ", 1)
    t = float(t)
    if tipo == "umbral":
        return [x > t for x in r]
    if tipo == "2 seguidas":
        return [i > 0 and r[i] > t and r[i - 1] > t for i in range(len(r))]
    if tipo == "media 3":
        return [x > t for x in _media_movil(r, 3)]
    if tipo.startswith("ema "):
        return [x > t for x in _ema(r, float(tipo.split()[1]))]
    raise ValueError(f"política desconocida {nombre!r}")


def politicas(cfg: str, taus: tuple[float, ...] = TAUS) -> list[str]:
    if _tipo(cfg) in ("reglas", "reglas_v2"):
        return ["alerta del modelo"]
    nombres = ["alerta del modelo"] if un_paso(cfg) else []
    for t in taus:
        nombres += [f"umbral > {t}", f"2 seguidas > {t}", f"media 3 > {t}", f"ema 0.3 > {t}", f"ema 0.5 > {t}"]
    return nombres


def politicas_slm_verificador(cfg: str) -> list[str]:
    """Lado SLM del verificador: su propia decisión, sin barrer todo (pocos casos para elegir)."""
    if un_paso(cfg):
        return ["alerta del modelo"]
    return [f"umbral > {t}" for t in TAUS_SLM] + [f"ema 0.3 > {t}" for t in TAUS_SLM]


def primero(arriba: list[bool]) -> int | None:
    return next((i for i, x in enumerate(arriba, 1) if x), None)


# ---------------------------------------------------------------- métricas

def medir(avisos: dict[str, int | None], ids: list[str], refs: dict) -> dict:
    tp = nv = fp = nl = fp_r07 = n_r07 = 0
    lugares = Counter()
    for c in ids:
        ref, a = refs[c], avisos[c]
        if ref["clase"] in casos.LEGITIMAS:
            nl += 1
            fp += a is not None
            if ref["clase"] == "legitima_dificil" or ref.get("tipo_legitima") in TIPOS_R07:
                n_r07 += 1
                fp_r07 += a is not None
        else:
            nv += 1
            tp += a is not None
        lugares[resumen.categoria(ref, a)] += 1
    rec, fa = (tp / nv if nv else 0.0), (fp / nl if nl else 0.0)
    temprano = lugares["antes_del_pedido"] + lugares["en_el_pedido"]
    return {"tp": tp, "nv": nv, "fp": fp, "nl": nl, "fp_r07": fp_r07, "n_r07": n_r07, "rec": rec, "fa": fa,
            "lugares": lugares, "temprano": temprano, "meta": rec >= META_ESTAFAS and fa <= META_FA}


def auroc(puntaje: dict[str, float], ids: list[str], refs: dict) -> float | None:
    """AUROC por conversación con el máximo puntaje de la llamada (Mann-Whitney)."""
    pos = [puntaje[c] for c in ids if refs[c]["clase"] not in casos.LEGITIMAS]
    neg = [puntaje[c] for c in ids if refs[c]["clase"] in casos.LEGITIMAS]
    if not pos or not neg:
        return None
    gana = sum((p > n) + 0.5 * (p == n) for p in pos for n in neg)
    return gana / (len(pos) * len(neg))


def elegir(candidatos: list[tuple[str, dict, dict]]) -> tuple[tuple[str, dict, dict] | None, bool]:
    """Mayor recall con FA ≤ meta en selección; empate: menos FA, después aviso más temprano.
    Si ninguno entra en la meta de FA, el de menos FA (y más recall). Devuelve (elegido, entra)."""
    if not candidatos:
        return None, False
    validos = [x for x in candidatos if x[1]["fa"] <= META_FA]
    if validos:
        return max(validos, key=lambda x: (x[1]["rec"], -x[1]["fa"], x[1]["temprano"])), True
    return min(candidatos, key=lambda x: (x[1]["fa"], -x[1]["rec"])), False


# ---------------------------------------------------------------- roles

def rol_solo(datos, seleccion, informe, refs):
    grupos = {}
    for cfg, por_caso in datos.items():
        cand = []
        ids_s = [c for c in seleccion if c in por_caso]
        ids_i = [c for c in informe if c in por_caso]
        series = {c: (riesgos(por_caso[c]), alertas(por_caso[c])) for c in ids_s + ids_i}
        for nombre in politicas(cfg):
            avisos = {c: primero(estados(nombre, *series[c])) for c in series}
            cand.append((nombre, medir(avisos, ids_s, refs), medir(avisos, ids_i, refs) if ids_i else None, avisos))
        grupos[cfg] = (ids_s, ids_i, cand)
    return grupos


def rol_verificador(datos, seleccion, informe, refs):
    """SLM con su política Y reranker > τ en la misma línea. Agrupado por SLM."""
    rrs = [c for c in datos if _tipo(c) == "reranker"]
    grupos = {}
    for s in (c for c in datos if _tipo(c) == "slm"):
        cand = []
        for r in rrs:
            comunes = set(datos[s]) & set(datos[r])
            ids_s = [c for c in seleccion if c in comunes]
            ids_i = [c for c in informe if c in comunes]
            if not ids_s:
                continue
            ser_s = {c: (riesgos(datos[s][c]), alertas(datos[s][c])) for c in ids_s + ids_i}
            ser_r = {c: riesgos(datos[r][c]) for c in ids_s + ids_i}
            for ps in politicas_slm_verificador(s):
                arriba_s = {c: estados(ps, *ser_s[c]) for c in ser_s}
                for t in TAUS:
                    avisos = {c: primero([x and y > t for x, y in zip(arriba_s[c], ser_r[c])]) for c in ser_s}
                    nombre = f"{ps} ∧ {r.split('|')[1]} > {t}"
                    cand.append((nombre, medir(avisos, ids_s, refs), medir(avisos, ids_i, refs) if ids_i else None, avisos))
        grupos[s] = (None, None, cand)
    return grupos


def rol_filtro(datos, seleccion, informe, refs):
    """Reranker deriva (> τ, primera vez) y desde ahí decide el SLM. Agrupado por SLM."""
    rrs = [c for c in datos if _tipo(c) == "reranker"]
    grupos = {}
    for s in (c for c in datos if _tipo(c) == "slm"):
        cand = []
        for r in rrs:
            comunes = set(datos[s]) & set(datos[r])
            ids_s = [c for c in seleccion if c in comunes]
            ids_i = [c for c in informe if c in comunes]
            if not ids_s:
                continue
            todas = r.split("|")[2] == "todas" if r.count("|") >= 2 else False
            ser_s = {c: (riesgos(datos[s][c]), alertas(datos[s][c])) for c in ids_s + ids_i}
            ser_r = {c: riesgos(datos[r][c], todas=todas) for c in ids_s + ids_i}
            for ps in politicas_slm_verificador(s):
                arriba_s = {c: estados(ps, *ser_s[c]) for c in ser_s}
                for t in TAUS:
                    deriva = {c: primero([y > t for y in ser_r[c]]) for c in ser_s}
                    avisos = {c: (None if deriva[c] is None else
                                  primero([x and i >= deriva[c] for i, x in enumerate(arriba_s[c], 1)])) for c in ser_s}
                    lineas = sum(len(ser_r[c]) for c in ids_s)
                    evitadas = sum(len(ser_r[c]) if deriva[c] is None else deriva[c] - 1 for c in ids_s)
                    m_s = medir(avisos, ids_s, refs)
                    m_s["evitadas"] = (evitadas, lineas)
                    nombre = f"{r.split('|')[1]} ({'todas' if todas else 'pedidos'}) > {t} → {ps}"
                    cand.append((nombre, m_s, medir(avisos, ids_i, refs) if ids_i else None, avisos))
        grupos[s] = (None, None, cand)
    return grupos


# ---------------------------------------------------------------- informe

def _md(cfg: str) -> str:
    return "`" + cfg.replace("|", "\\|") + "`"


def _pct(k: int, n: int) -> str:
    return f"{k}/{n} ({100 * k / n:.0f} %)" if n else "—"


def _fila(nombre: str, sel: dict, inf: dict | None) -> str:
    def lado(m):
        if m is None:
            return "— | — | — | —"
        return (f"{_pct(m['tp'], m['nv'])} | {_pct(m['fp'], m['nl'])} | {_pct(m['fp_r07'], m['n_r07'])} | "
                f"{m['temprano']} antes/en · {m['lugares']['en_o_despues_del_cumplimiento']} ≥C")
    extra = ""
    if "evitadas" in sel:
        e, n = sel["evitadas"]
        extra = f" (evita {100 * e / n:.0f} % de consultas)" if n else ""
    return f"| {nombre}{extra} | {lado(sel)} | {lado(inf)} |"


ENCABEZADO = ("| Configuración | Sel.: estafas | Sel.: FA | Sel.: FA R07 | Sel.: momento | "
              "Inf.: estafas | Inf.: FA | Inf.: FA R07 | Inf.: momento |\n|---|---|---|---|---|---|---|---|---|")


def seccion_rol(titulo: str, explicacion: str, grupos: dict, top: int = 5) -> list[str]:
    salida = ["", f"## {titulo}", "", explicacion]
    for clave, (_, _, cand) in sorted(grupos.items()):
        elegido, entra = elegir([(n, s, i) for n, s, i, _ in cand])
        if elegido is None:
            continue
        nombre, sel, inf = elegido
        salida += ["", f"### {_md(clave)}", ""]
        if sel["nv"] + sel["nl"] == 0:
            salida.append("Sin casos de selección en estas corridas: no se elige nada. Para elegir, correr "
                          "`--lista seleccion-57 --seguir-tras-aviso` con esta configuración.")
            continue
        aviso = "" if entra else " **Ninguna entra en FA ≤ 15 % en selección: se muestra la de menos FA.**"
        salida.append(f"Elegida en selección: **{nombre}**.{aviso}")
        if inf is not None:
            salida.append(f"En el informe: estafas {_pct(inf['tp'], inf['nv'])} (IC 95 % {wilson(inf['tp'], inf['nv'])}), "
                          f"FA {_pct(inf['fp'], inf['nl'])} (IC 95 % {wilson(inf['fp'], inf['nl'])})"
                          f"{' · cumple la meta' if inf['meta'] else ''}.")
        mejores = sorted(cand, key=lambda x: (x[1]["fa"] > META_FA, -x[1]["rec"], x[1]["fa"], -x[1]["temprano"]))[:top]
        salida += ["", ENCABEZADO] + [_fila(n, s, i) for n, s, i, _ in mejores]
    return salida


def tabla_latencia(datos: dict) -> list[str]:
    salida = ["", "## Costo por línea", "", "| Config | Líneas | ms p50 | ms p95 | Etapa 1 p50 | Etapa 2 p50 |", "|---|---|---|---|---|---|"]

    def p(xs, q):
        return f"{statistics.quantiles(xs, n=100)[q - 1]:.0f}" if len(xs) >= 2 else "—"

    for cfg, por_caso in sorted(datos.items()):
        filas = [f for fs in por_caso.values() for f in fs]
        nums = lambda campo: [float(f[campo]) for f in filas if f.get(campo)]  # noqa: E731
        salida.append(f"| {_md(cfg)} | {len(filas)} | {p(nums('ms'), 50)} | {p(nums('ms'), 95)} | "
                      f"{p(nums('ms_etapa1'), 50)} | {p(nums('ms_etapa2'), 50)} |")
    return salida


def tabla_reranker(datos: dict, seleccion: list[str], informe: list[str], refs: dict) -> list[str]:
    """AUROC (para la compuerta de entrenamiento) y acierto del tipo de pedido en T_R."""
    salida = ["", "## Reranker: orden y tipo de pedido", "",
              "| Config | AUROC sel. | AUROC inf. | Pedido correcto en `T_R` (sel.) | (inf.) |", "|---|---|---|---|---|"]
    for cfg, por_caso in sorted(datos.items()):
        if _tipo(cfg) != "reranker":
            continue
        maximo = {c: max(riesgos(fs)) for c, fs in por_caso.items()}

        def acierto(ids):
            k = n = 0
            for c in ids:
                ref = refs[c]
                if c not in por_caso or ref["clase"] in casos.LEGITIMAS or not ref.get("t_r_linea") or not ref.get("pedido"):
                    continue
                fila = por_caso[c][ref["t_r_linea"] - 1]
                if fila["valida"] != "true":
                    continue
                puntajes = {e: v for e, v in json.loads(fila["crudo"])["puntajes"].items() if e.startswith("REQUEST_")}
                n += 1
                k += max(puntajes, key=puntajes.get) == ref["pedido"]
            return _pct(k, n)

        def au(ids):
            ids = [c for c in ids if c in maximo]
            v = auroc(maximo, ids, refs)
            return "—" if v is None else f"{v:.3f}"

        salida.append(f"| {_md(cfg)} | {au(seleccion)} | {au(informe)} | {acierto(seleccion)} | {acierto(informe)} |")
    return salida


def analizar(carpetas: list[Path], particiones: Path = PARTICIONES) -> str:
    seleccion, informe = splits(particiones)
    crudos = cargar(carpetas, ("slm", "reranker", "reglas"))
    datos = {}
    for cfg, por_caso in crudos.items():
        ids = set(completos(por_caso)) & (set(seleccion) | set(informe))
        if ids:
            datos[cfg] = {c: por_caso[c] for c in ids}
    if not datos:
        return "No hay casos de selección ni de informe en las corridas indicadas.\n"
    refs = {c: casos.cargar_referencia(c) for c in seleccion + informe}
    n = lambda ids, clase: sum((refs[c]["clase"] in casos.LEGITIMAS) == (clase == "l") for c in ids)  # noqa: E731
    salida = [
        "# Reranker zero-shot: roles × políticas acumuladas",
        "",
        "> **Estado: propuesta sin discutir.** Desarrollo sin revisión humana. No elige detector (D09)",
        "> ni política (D08). Las posiciones son líneas, no segundos.",
        "",
        "Corridas: " + ", ".join(f"`{c.name}`" for c in carpetas),
        "",
        f"- **Selección** (se elige acá): {len(seleccion)} casos, {n(seleccion, 'v')} estafas y {n(seleccion, 'l')} legítimas.",
        f"- **Informe** (`comparacion_20`, no se elige acá): {len(informe)} casos, {n(informe, 'v')} estafas y {n(informe, 'l')} legítimas.",
        f"- **Meta del tutor:** ≥ {META_ESTAFAS:.0%} de estafas con aviso (sobre todas) y ≤ {META_FA:.0%} de FA.",
        "- **FA R07:** legítimas difíciles o con `tipo_legitima` mención sin pedido / pedido razonable.",
        "- **Momento:** avisos antes o en el pedido (`T_R`) · avisos en o después del cumplimiento (`≥C`, ya no protegen).",
        "- Cada configuración usa solo los casos que cubren todas sus corridas; la cobertura figura en la sección de costo.",
    ]
    salida += tabla_latencia(datos)
    salida += tabla_reranker(datos, seleccion, informe, refs)
    salida += seccion_rol("Rol A — cada detector solo, con políticas acumuladas",
                          "Una fila por detector. Incluye SLM y reglas como comparadores sobre los mismos casos.",
                          rol_solo(datos, seleccion, informe, refs))
    salida += seccion_rol("Rol C y H5 — verificador: SLM ∧ reranker en la misma línea",
                          "El SLM decide con su política y el reranker tiene que superar τ en esa línea. Con "
                          "`riesgo` (riesgo primero) es la H5: el reranker reemplaza la etapa 2.",
                          rol_verificador(datos, seleccion, informe, refs))
    salida += seccion_rol("Rol B — filtro: reranker deriva, después decide el SLM",
                          "Aproximación por compuerta sobre corridas completas del SLM: no incluye el bloque de "
                          "indicio de #68, que cambiaría las respuestas del SLM.",
                          rol_filtro(datos, seleccion, informe, refs))
    return "\n".join(salida) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("corridas", nargs="+", type=Path, help="carpetas de corridas/ (reranker, SLM, reglas)")
    ap.add_argument("--particiones", type=Path, default=PARTICIONES)
    ap.add_argument("--salida", type=Path, default=AQUI / "analisis.md")
    args = ap.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    texto = analizar([c.resolve() for c in args.corridas], args.particiones)
    args.salida.write_text(texto, encoding="utf-8")
    print(texto)
    print(f"Escrito en {args.salida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
