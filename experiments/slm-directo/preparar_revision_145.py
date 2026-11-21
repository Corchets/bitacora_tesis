"""Prepara las 42 fichas ciegas de #145 sin ejecutar detectores ni leer el test.

Uso desde la raíz: python3 experiments/slm-directo/preparar_revision_145.py
La clave se crea exclusivamente en data/private/CLAVE-REVISION-145.json.
No reemplaza una entrega existente diferente: cambiar la muestra requiere otra versión.
"""
from __future__ import annotations

import csv
import hashlib
import json
import random
from pathlib import Path

from test_alcance import REV_DESARROLLO, desarrollo_git, _git

BASE = Path(__file__).resolve().parent
REPO = BASE.parents[1]
TABLERO = BASE / "analisis/tablero"
SEMILLA = 145
CORRIDAS = (
    ("2026-11-04_sin-indicio-150/a/**/actualizaciones.csv", "slm"),
    ("2026-11-04_sin-indicio-150/c/**/actualizaciones.csv", "slm"),
    ("2026-11-04_sin-indicio-150/a/**/actualizaciones.csv", "tito-slm"),
    ("2026-11-05_tito-2-v4/b/**/actualizaciones.csv", "slm"),
    ("2026-11-05_tito-2-v4/a/**/actualizaciones.csv", "tito-viejo-2"),
)


def sha(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def seleccionar(refs: dict, avisos: list[set], legitimas: dict) -> list[tuple[str, str]]:
    rng = random.Random(SEMILLA)
    estafas = sorted(i for i, r in refs.items() if i.startswith("CV2-D-V-") and r["clase"] == "vishing")
    perdidas = [i for i in estafas if not any(i in a for a in avisos)]
    detectadas = [i for i in estafas if any(i in a for a in avisos)]
    if len(perdidas) != 16 or sum(refs[i]["t_r_linea"] is None for i in perdidas) != 9:
        raise ValueError("Las cinco corridas ya no reproducen las 16 pérdidas (9 sin pedido) de #145.")
    elegidas = [(i, "sin_aviso") for i in perdidas]
    elegidas += [(i, "con_aviso") for i in rng.sample(detectadas, 16)]
    elegidas += [(i, "legitima_nueva") for i in rng.sample(sorted(legitimas), 10)]
    rng.shuffle(elegidas)
    return elegidas


def renderizar(datos: dict) -> str:
    # Los textos nunca se interpretan como HTML; escapar '<' también protege el bloque JSON.
    paquete = json.dumps(datos, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    return (TABLERO / "revision_145_plantilla.html").read_text(encoding="utf-8").replace("__DATOS_REVISION__", paquete)


def conservar(ruta: Path, contenido: str) -> None:
    if ruta.exists() and ruta.read_text(encoding="utf-8") != contenido:
        raise ValueError(f"No se reemplaza una entrega diferente: {ruta}")
    ruta.write_text(contenido, encoding="utf-8")


def main() -> None:
    csv.field_size_limit(10**9)
    avisos, fuentes, ids_corrida = [], [], None
    for patron, detector in CORRIDAS:
        archivo, = (BASE / "corridas").glob(patron)
        with archivo.open(encoding="utf-8-sig", newline="") as fh:
            filas = [r for r in csv.DictReader(fh) if r["detector"] == detector]
        ids = {r["case_id"] for r in filas}
        if len(ids) != 150 or any(i.startswith("CV2-T-") for i in ids):
            raise ValueError("Se requieren las 150 conversaciones de desarrollo.")
        if ids_corrida is not None and ids != ids_corrida:
            raise ValueError("Las corridas tienen casos diferentes.")
        ids_corrida = ids
        avisos.append({r["case_id"] for r in filas if r["aviso"] == "true"})
        fuentes.append({"archivo": str(archivo.relative_to(REPO)), "detector": detector,
                        "sha256": hashlib.sha256(archivo.read_bytes()).hexdigest()})
    refs = {i: json.loads((BASE / "casos/referencia" / f"{i}.json").read_text()) for i in ids_corrida}
    nuevas = desarrollo_git(REV_DESARROLLO)
    alcance = json.loads(_git("show", f"{REV_DESARROLLO}:experiments/slm-directo/casos/alcance-legitimas-cotidianas.json"))["casos"]
    nuevas = {i: r for i, r in nuevas.items() if i.startswith(("LEG-", "LEG2-"))
              and r["referencia"].get("particion") == "desarrollo" and alcance[i]["alcance"] == "dentro"}
    roles = json.loads((BASE / "casos/roles-protegida.json").read_text())
    publico, clave = [], {}
    for n, (cid, grupo) in enumerate(seleccionar(refs, avisos, nuevas), 1):
        alias = f"Llamada {n:02d}"
        if cid in nuevas:
            lineas, protegida, ref = nuevas[cid]["texto"], nuevas[cid]["protegida"], nuevas[cid]["referencia"]
        else:
            lineas = (BASE / "casos/texto" / f"{cid}.txt").read_text().splitlines()
            protegida, ref = roles[cid]["protegida"], refs[cid]
        if ref.get("particion", "desarrollo") != "desarrollo" or protegida not in ("A", "B"):
            raise ValueError(f"Caso fuera de desarrollo o sin rol: {cid}")
        turnos = []
        for linea in lineas:
            hablante, texto = linea.split(": ", 1)
            if hablante not in ("A", "B"):
                raise ValueError(f"Turno inválido: {cid}")
            turnos.append({"hablante": "PROTEGIDA" if hablante == protegida else "OTRA", "texto": texto})
        publico.append({"id": alias, "turnos": turnos})
        clave[alias] = {"case_id": cid, "grupo_muestreo": grupo, "referencia_anterior": ref,
                       "protegida_original": protegida, "texto_sha256": sha("\n".join(lineas))}
    muestra = sha(json.dumps(publico, ensure_ascii=False, sort_keys=True))
    datos = {"version": 1, "muestra": muestra, "casos": publico}
    privada = {"issue": 145, "fecha": "2026-11-07", "semilla": SEMILLA, "muestra": muestra,
               "revision_legitimas": REV_DESARROLLO, "fuentes_corridas": fuentes, "casos": clave}
    destino_clave = REPO / "data/private/CLAVE-REVISION-145.json"
    # La clave se conserva antes de escribir la vista, para no perder la correspondencia.
    conservar(destino_clave, json.dumps(privada, ensure_ascii=False, indent=2) + "\n")
    destino_clave.chmod(0o600)
    html = renderizar(datos)
    for cid in clave.values():
        if cid["case_id"] in html:
            raise ValueError("Se filtró un identificador original al formulario.")
    (TABLERO / "revision-145.html").write_text(html, encoding="utf-8")
    print(f"42 fichas listas; muestra {muestra[:12]}. Clave privada conservada fuera de Git.")


if __name__ == "__main__":
    main()
