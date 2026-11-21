"""Extrae EN-07, EN-09 y EN-13 de la traducción de Luciano (#144), renglón por renglón como están escritos.

Solo toma los renglones numerados del diálogo: deja afuera el encabezado, el canal, el contexto y la ficha. De cada
renglón saca el formato Markdown (negritas, cursivas) y las marcas entre acentos graves del traductor
(`[en la fuente: ...]`, `[turno pegado en la fuente]`), que son anotaciones y no parte de lo dicho. El hablante es la
letra que el renglón tiene escrita (A = estafador = OTRA; B = quien atiende = PROTEGIDA), aunque la marca diga que la
fuente lo etiquetó mal. Los reemplazos `[NOMBRE_B]` quedan, porque son el texto.

    python -I extraer.py
"""
import hashlib
import json
import re
from pathlib import Path

AQUI = Path(__file__).resolve().parent
FUENTE = AQUI.parents[3] / "docs" / "corpus" / "ISSUE-144-INGLES-18-2026-11-07.md"
CASOS = ["EN-07", "EN-09", "EN-13"]
RENGLON = re.compile(r"^(\d+)\.\s+(.*)$")


def limpiar(cuerpo: str) -> tuple[str, str]:
    cuerpo = re.sub(r"`[^`]*`", "", cuerpo)            # marcas del traductor
    cuerpo = cuerpo.replace("**", "")                   # negritas
    cuerpo = re.sub(r"\*([^*]+)\*", r"\1", cuerpo)      # cursivas
    cuerpo = re.sub(r"\s+", " ", cuerpo).strip()
    m = re.match(r"^([AB])\s*:\s*(.*)$", cuerpo)
    if not m:
        raise ValueError(f"renglón sin hablante: {cuerpo!r}")
    return m.group(1), m.group(2)


def main():
    texto = FUENTE.read_text(encoding="utf-8")
    salida = {"fuente": FUENTE.relative_to(AQUI.parents[3]).as_posix(),
              "fuente_sha256": hashlib.sha256(texto.encode()).hexdigest(),
              "roles": {"A": "OTRA", "B": "PROTEGIDA"}, "casos": {}}
    for caso in CASOS:
        seccion = re.search(rf"^## {caso} .*?(?=^### Ficha {caso})", texto, re.S | re.M).group(0)
        lineas = []
        for renglon in seccion.splitlines():
            m = RENGLON.match(renglon)
            if m:
                assert int(m.group(1)) == len(lineas) + 1, (caso, renglon)
                hablante, dicho = limpiar(m.group(2))
                lineas.append({"n": int(m.group(1)), "hablante": hablante, "texto": dicho})
        salida["casos"][caso] = lineas
    (AQUI / "conversaciones.json").write_text(json.dumps(salida, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for caso, lineas in salida["casos"].items():
        print(caso, len(lineas), "renglones,", sum(l["hablante"] == "A" for l in lineas), "de OTRA")


if __name__ == "__main__":
    main()
