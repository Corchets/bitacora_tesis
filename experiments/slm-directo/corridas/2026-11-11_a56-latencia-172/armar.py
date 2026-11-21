"""Conversaciones de desarrollo para #172: `rapida-20` con roles (PROTEGIDA/OTRA), en el formato del ejecutor Android.

No usa nada de #144. `sub-6` son las tres primeras estafas y las tres primeras legítimas de la lista, para comparar
parámetros del servidor en menos tiempo.

    python -I armar.py   (desde esta carpeta)
"""
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SLM = AQUI.parents[1]
sys.path.insert(0, str(SLM))
from casos import cargar_texto, con_roles  # noqa: E402

LISTA = SLM / "casos" / "listas" / "rapida-20.txt"


def main():
    ids = [l.strip() for l in LISTA.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
    sub6 = [c for c in ids if "-V-" in c][:3] + [c for c in ids if "-L-" in c][:3]
    for nombre, casos in (("rapida-20", ids), ("sub-6", sub6)):
        salida = {"lista": nombre, "roles": {"OTRA": "OTRA", "PROTEGIDA": "PROTEGIDA"}, "casos": {}}
        for c in casos:
            lineas = con_roles(c, cargar_texto(c))
            salida["casos"][c] = [{"n": i, "hablante": l.hablante, "texto": l.texto} for i, l in enumerate(lineas, 1)]
        (AQUI / f"conversaciones-{nombre}.json").write_text(json.dumps(salida, ensure_ascii=False, indent=1) + "\n",
                                                            encoding="utf-8")
        otra = sum(r["hablante"] == "OTRA" for ls in salida["casos"].values() for r in ls)
        print(nombre, len(casos), "casos,", otra, "consultas")


if __name__ == "__main__":
    main()
