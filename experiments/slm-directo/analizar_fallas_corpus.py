"""Cruza las corridas del 2026-11-04 con el corpus para ver qué casos fallan y dónde.

Lee solo CSV ya generados y los casos de desarrollo; no corre modelos ni lee la reserva.
Sostiene las cifras de casos/FALLAS-Y-CORPUS-2026-11-05.md.

Uso, desde experiments/slm-directo:
    python -I analizar_fallas_corpus.py            # resumen por grupo y casos que fallan
    python -I analizar_fallas_corpus.py --casos ID  # primer aviso de cada condición en esos casos
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
CASOS = RAIZ / "casos"
CORRIDAS = RAIZ / "corridas"

# Condiciones de Tito sin indicio de la prueba v4 (misma sesión de Colab).
V4 = "prompt-v4-a-v4-rol"
V1_CONTROL = "prompt-v4-d-tarea-ab"

# Maniobras de aislamiento o de retención: "no cortes", "no lo abras", "no le cuentes"...
MANIOBRA = re.compile(
    r"no cort|no cierres|no le cuentes|no lo comentes|no lo abras|no respondas|no lo reenv"
    r"|no te conviene entrar|no salgas|no conviene decirlo|pisar la revisi",
    re.IGNORECASE,
)

csv.field_size_limit(10**9)


def leer_corridas() -> tuple[list[str], dict[str, dict[str, dict | None]], dict[str, int]]:
    """Devuelve las etiquetas de condición, el primer aviso por caso y la activación de Tito en v4."""
    etiquetas: list[str] = []
    avisos: dict[str, dict[str, dict | None]] = defaultdict(dict)
    tito_v4: dict[str, int] = {}
    for patron in ("2026-11-04*/**/actualizaciones.csv", "2026-11-05*/**/actualizaciones.csv"):
        for archivo in sorted(CORRIDAS.glob(patron)):
            if "controles" in archivo.parts:
                continue
            corrida = archivo.parent.name
            corrida = corrida[18:] if corrida[:4].isdigit() and len(corrida) > 18 else corrida
            with archivo.open(encoding="utf-8-sig", newline="") as fh:
                for fila in csv.DictReader(fh):
                    if fila["config"] == "reglas":
                        continue
                    etiqueta = f"{corrida} :: {fila['config']}"
                    if etiqueta not in etiquetas:
                        etiquetas.append(etiqueta)
                    caso = fila["case_id"]
                    avisos[caso].setdefault(etiqueta, None)
                    if fila["aviso"] == "true" and avisos[caso][etiqueta] is None:
                        avisos[caso][etiqueta] = {
                            "linea": int(fila["linea"]),
                            "evidencia": fila["evidencia"],
                            "motivo": fila["motivo"],
                        }
                    if corrida == V4 and fila["consulta"] == "slm_valida":
                        tito_v4.setdefault(caso, int(fila["linea"]))
    return etiquetas, avisos, tito_v4


def referencia(caso: str) -> dict:
    return json.loads((CASOS / "referencia" / f"{caso}.json").read_text(encoding="utf-8"))


def texto(caso: str) -> list[str]:
    return (CASOS / "texto" / f"{caso}.txt").read_text(encoding="utf-8").strip().splitlines()


def grupo(caso: str) -> str:
    return "CV2" if caso.startswith("CV2") else caso.split("-")[0]


def etiqueta_de(etiquetas: list[str], corrida: str) -> str:
    return next(e for e in etiquetas if e.startswith(corrida + " "))


def resumen(etiquetas, avisos, tito_v4) -> None:
    v4 = etiqueta_de(etiquetas, V4)
    v1 = etiqueta_de(etiquetas, V1_CONTROL)

    print("## v4 por grupo de origen y dificultad\n")
    conteo: Counter = Counter()
    for caso, por_cond in avisos.items():
        ref = referencia(caso)
        clase = "vishing" if ref["clase"] == "vishing" else "legitima"
        clave = (grupo(caso), clase, ref.get("dificultad") or "-")
        conteo[clave + ("aviso" if por_cond.get(v4) else "sin aviso",)] += 1
    claves = sorted({k[:3] for k in conteo})
    for g, clase, dif in claves:
        con = conteo[(g, clase, dif, "aviso")]
        total = con + conteo[(g, clase, dif, "sin aviso")]
        print(f"{g:4} {clase:9} {dif:20} con aviso {con:2}/{total}")

    print("\n## Casos que fallan en v4 o en v1 control\n")
    print("caso | clase | T_R | Tito activa (v4) | v4 | v1 control | condiciones con aviso")
    for caso in sorted(avisos):
        ref = referencia(caso)
        es_vishing = ref["clase"] == "vishing"
        falla4 = (avisos[caso].get(v4) is None) == es_vishing
        falla1 = (avisos[caso].get(v1) is None) == es_vishing
        if not (falla4 or falla1):
            continue
        n = sum(1 for e in etiquetas if avisos[caso].get(e))
        print(
            f"{caso} | {ref['clase']} | {ref.get('t_r_linea')} | {tito_v4.get(caso)} | "
            f"{'falla' if falla4 else 'ok'} | {'falla' if falla1 else 'ok'} | {n}/{len(etiquetas)}"
        )

    print("\n## Maniobras de aislamiento (sin contar estafas con pedido)\n")
    con_maniobra: Counter = Counter()
    for caso in sorted(avisos):
        ref = referencia(caso)
        if ref["clase"] == "vishing" and ref.get("t_r_linea") is not None:
            continue
        clase = "vishing sin pedido" if ref["clase"] == "vishing" else "legitima"
        con_maniobra[(clase, "total")] += 1
        lineas = [i + 1 for i, linea in enumerate(texto(caso)) if MANIOBRA.search(linea)]
        if lineas:
            con_maniobra[(clase, "con maniobra")] += 1
            print(f"{caso}: líneas {lineas}")
    for clase in ("vishing sin pedido", "legitima"):
        print(f"{clase}: {con_maniobra[(clase, 'con maniobra')]}/{con_maniobra[(clase, 'total')]} con maniobra")


def detalle(etiquetas, avisos, tito_v4, casos: list[str]) -> None:
    for caso in casos:
        ref = referencia(caso)
        print(f"\n=== {caso} | {ref['clase']} | T_R {ref.get('t_r_linea')} | Tito activa en v4: {tito_v4.get(caso)}")
        for e in etiquetas:
            aviso = avisos[caso].get(e)
            if aviso:
                print(f"  L{aviso['linea']:<3} {e}\n       cita: {aviso['evidencia'][:120]!r}")
        for i, linea in enumerate(texto(caso), start=1):
            print(f"  {i:2}. {linea}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--casos", nargs="*", default=None, help="mostrar el detalle de estos casos")
    args = parser.parse_args(argv)
    etiquetas, avisos, tito_v4 = leer_corridas()
    if args.casos:
        detalle(etiquetas, avisos, tito_v4, args.casos)
    else:
        print(f"{len(etiquetas)} condiciones, {len(avisos)} casos\n")
        resumen(etiquetas, avisos, tito_v4)
    return 0


if __name__ == "__main__":
    sys.exit(main())
