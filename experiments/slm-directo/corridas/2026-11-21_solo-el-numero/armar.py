"""Las conversaciones de `desarrollo-150` con roles, en el formato del ejecutor (como `armar.py` del 2026-11-11).

Solo desarrollo: frena si la lista trae algo de la reserva de test (`CV2-T-*`, `ENT-T-*`).

    python3 armar.py   (desde esta carpeta)
"""
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SLM = AQUI.parents[1]
sys.path.insert(0, str(SLM))
from casos import cargar_texto, con_roles  # noqa: E402

LISTA = "desarrollo-150"


def main():
    texto = (SLM / "casos" / "listas" / f"{LISTA}.txt").read_text(encoding="utf-8")
    ids = [l.strip() for l in texto.splitlines() if l.strip() and not l.startswith("#")]
    if reserva := [c for c in ids if "-T-" in c]:
        raise SystemExit(f"son de la reserva: {reserva}")
    salida = {"lista": LISTA, "roles": {"OTRA": "OTRA", "PROTEGIDA": "PROTEGIDA"}, "casos": {}}
    for c in ids:
        salida["casos"][c] = [{"n": i, "hablante": l.hablante, "texto": l.texto}
                              for i, l in enumerate(con_roles(c, cargar_texto(c)), 1)]
    (AQUI / f"conversaciones-{LISTA}.json").write_text(json.dumps(salida, ensure_ascii=False, indent=1) + "\n",
                                                       encoding="utf-8")
    otra = sum(r["hablante"] == "OTRA" for ls in salida["casos"].values() for r in ls)
    print(LISTA, len(ids), "casos,", otra, "consultas")


if __name__ == "__main__":
    main()
