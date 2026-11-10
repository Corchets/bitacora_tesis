#!/usr/bin/env python3
"""Catálogo de conversaciones: qué hay, dónde está, con qué lista se corre y qué usó cada corrida.

Escribe casos/CATALOGO-CONVERSACIONES.md a partir de las referencias de desarrollo, las listas de casos/listas/ y los
manifiestos de corridas/. De la reserva y de las legítimas de test no calcula nada: solo dice dónde están, porque se
miran una sola vez, en la evaluación final.

Uso (desde experiments/slm-directo), después de sumar casos, listas o corridas:
    python catalogo.py
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import casos

RAIZ = Path(__file__).resolve().parent
DIR_LISTAS = RAIZ / "casos" / "listas"
DIR_CORRIDAS = RAIZ / "corridas"
SALIDA = RAIZ / "casos" / "CATALOGO-CONVERSACIONES.md"
MANIFIESTO_DESARROLLO = RAIZ / "casos" / "MANIFIESTO-DESARROLLO.json"

# Lo que no está en casos/texto de esta rama: se describe a mano y no se cuenta por clase.
FUERA_DE_DESARROLLO = [
    ("Reserva del corpus v2 (`CV2-T-*`)", "200",
     "rama `reserva/test`: `casos/texto/` y `casos/referencia/`",
     "`--particion test_reservado` en esa rama, solo en la evaluación final"),
    ("Legítimas de test de #45", "56",
     "rama `reserva/test`: `casos/legitimas-entrantes-test.jsonl`",
     "todavía no está en el formato de casos: hay que convertirla antes de la evaluación final"),
    ("Corpus externo real de #144", "—",
     "`docs/corpus/ISSUE-144-*` y `docs/corpus/FICHAS-144-*` "
     "([relevamiento](../../../docs/corpus/RELEVAMIENTO-CORPUS-EXTERNO.md))",
     "lecturas y fichas, no casos: test externo previsto"),
    ("Ejemplos del panel VoIP", "4",
     "`experiments/asr-local/audio/*-tts-estereo.wav`, fuera de Git (`asr-local/sintetizar_par.py`)",
     "desde el panel; son audio sintético, sin valor de evaluación"),
    ("Llamadas con voz real (#94)", "—",
     "`experiments/voip/llamadas/` de la copia que corrió el servidor, fuera de Git",
     "`replay.py --actualizaciones <llamada>/actualizaciones.jsonl`"),
]


def _celda(texto: str) -> str:
    return str(texto).replace("|", "\\|").replace("\n", " ")


def leer_lista(ruta: Path) -> tuple[list[str], str]:
    """(case_id, descripción): la descripción son los comentarios de arriba de la lista, en un renglón."""
    lineas = [l.strip() for l in ruta.read_text(encoding="utf-8").splitlines()]
    cabecera = []
    for l in lineas:
        if not l.startswith("#"):
            break
        cabecera.append(l.lstrip("#").strip())
    descripcion = " ".join(c for c in cabecera if c)
    if len(descripcion) > 200:
        descripcion = descripcion[:200].rsplit(" ", 1)[0] + " …"
    return [l for l in lineas if l and not l.startswith("#")], descripcion


def clases(ids, referencias: dict[str, dict]) -> tuple[int, int]:
    """(estafas, legítimas) entre los ids que tienen referencia."""
    c = Counter("vishing" if referencias[i]["clase"] == "vishing" else "legitima" for i in ids if i in referencias)
    return c["vishing"], c["legitima"]


def conjuntos_con_nombre(listas: dict[str, list[str]], referencias: dict[str, dict],
                         estados: dict[str, str] | None = None) -> dict[frozenset, str]:
    """Conjuntos de casos que tienen nombre, para reconocer qué usó una corrida.

    `estados`: case_id → estado de MANIFIESTO-DESARROLLO.json (cuenta, historico…). Gana el nombre más específico:
    lista, después grupo, después estado.
    """
    nombres: dict[frozenset, str] = {frozenset(referencias): f"todo el desarrollo ({len(referencias)})"}
    for estado in sorted(set((estados or {}).values())):
        ids = frozenset(i for i, e in estados.items() if e == estado)
        nombres[ids] = f"estado `{estado}` del manifiesto"
    for grupo in sorted({r["grupo"] for r in referencias.values()}):
        ids = frozenset(i for i, r in referencias.items() if r["grupo"] == grupo)
        nombres[ids] = f"grupo {grupo}"
    for nombre, ids in sorted(listas.items()):
        nombres[frozenset(ids)] = f"lista {nombre}"
    return nombres


def conjunto_de(ids: list[str], nombres: dict[frozenset, str], referencias: dict[str, dict]) -> str:
    if any(i.startswith("CV2-T-") for i in ids):
        return "incluye la reserva"
    nombre = nombres.get(frozenset(ids))
    if nombre:
        return nombre
    if len(ids) == 1:
        return f"un caso: `{ids[0]}`"
    viejos = sum(i not in referencias for i in ids)
    return f"{len(ids)} casos sin lista" + (f" ({viejos} ya no están en desarrollo)" if viejos else "")


def resumen_configs(manifiesto: dict) -> str:
    """Detectores y prompts de la corrida, sin repetir."""
    vistos = []
    for c in manifiesto.get("configs") or []:
        if not isinstance(c, dict):
            continue
        etiqueta = c.get("prompt") or c.get("detector") or c.get("config", "")
        if c.get("detector") not in (None, "slm", "reglas") and c.get("prompt"):
            etiqueta = f"{c['detector']} {c['prompt']}"
        if etiqueta and etiqueta not in vistos:
            vistos.append(etiqueta)
    return ", ".join(f"`{v}`" for v in vistos[:4]) + (" …" if len(vistos) > 4 else "")


def corridas(dir_corridas: Path) -> list[tuple[str, str, list[str], dict]]:
    """(carpeta, fecha, case_id, manifiesto) de cada manifiesto de corridas/ que lista sus casos."""
    filas = []
    for ruta in sorted(dir_corridas.rglob("manifiesto.json")):
        try:
            manifiesto = json.loads(ruta.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        ids = manifiesto.get("casos")
        if not isinstance(ids, (dict, list)) or not ids:
            continue
        carpeta = ruta.parent.relative_to(dir_corridas).as_posix()
        fecha = str(manifiesto.get("inicio") or carpeta)[:10]
        filas.append((carpeta, fecha, sorted(ids), manifiesto))
    return filas


def armar(referencias: dict[str, dict], listas: dict[str, tuple[list[str], str]],
          filas_corridas: list[tuple[str, str, list[str], dict]], estados: dict[str, str] | None = None) -> str:
    md = [
        "# Catálogo de conversaciones",
        "",
        "> Generado por [`catalogo.py`](../catalogo.py); no editar a mano. Para actualizarlo, después de sumar casos,",
        "> listas o corridas: `python catalogo.py` desde `experiments/slm-directo`.",
        "",
        "Qué conversaciones hay, dónde están, con qué lista se corre cada conjunto y qué usó cada corrida. Las reglas de",
        "formato y de cada grupo están en [README.md](README.md); qué casos cuentan en desarrollo, en",
        "[MANIFIESTO-DESARROLLO.md](MANIFIESTO-DESARROLLO.md).",
        "",
        "## 1. Qué conversaciones hay",
        "",
        "Desarrollo, en esta rama (`casos/texto/` y `casos/referencia/`). `correr.py` usa todo el desarrollo por defecto;",
        "`--grupo` elige uno.",
        "",
        "| Grupo | Conversaciones | Estafas | Legítimas |",
        "|---|---:|---:|---:|",
    ]
    for grupo in sorted({r["grupo"] for r in referencias.values()}):
        ids = [i for i, r in referencias.items() if r["grupo"] == grupo]
        estafas, legitimas = clases(ids, referencias)
        md.append(f"| `{grupo}` | {len(ids)} | {estafas} | {legitimas} |")
    estafas, legitimas = clases(referencias, referencias)
    md += [f"| **Total** | **{len(referencias)}** | **{estafas}** | **{legitimas}** |", "",
           "Fuera de desarrollo. La reserva y las legítimas de test se miran una sola vez, con la configuración",
           "congelada ([ADR 0005](../../../docs/ingenieria/adr/0005-reglas-de-evaluacion-escritas-antes-de-correr.md)): no",
           "se cuentan por clase acá.", "",
           "| Conjunto | Conversaciones | Dónde | Cómo se usa |", "|---|---:|---|---|"]
    md += [f"| {a} | {b} | {c} | {d} |" for a, b, c, d in FUERA_DE_DESARROLLO]
    md += ["", "## 2. Listas para correr", "",
           "`python correr.py --lista <nombre>` corre una lista de `casos/listas/`; varias, separadas por coma. Para una",
           "lista nueva, un archivo con un `case_id` por línea y un comentario `#` arriba que diga qué es.", "",
           "| Lista | Casos | Estafas | Legítimas | Qué es |", "|---|---:|---:|---:|---|"]
    for nombre, (ids, descripcion) in sorted(listas.items()):
        estafas, legitimas = clases(ids, referencias)
        md.append(f"| `{nombre}` | {len(ids)} | {estafas} | {legitimas} | {_celda(descripcion)} |")
    nombres = conjuntos_con_nombre({n: ids for n, (ids, _) in listas.items()}, referencias, estados)
    md += ["", "## 3. Qué usó cada corrida", "",
           "Sale del `manifiesto.json` de cada carpeta de `corridas/`. «Sin lista» quiere decir que el conjunto no coincide",
           "con ninguna lista, grupo o estado del manifiesto de hoy: se eligió con `--casos` o con una lista que después",
           "cambió.", "",
           "| Corrida | Fecha | Casos | Conjunto | Prompts o detectores |", "|---|---|---:|---|---|"]
    for carpeta, fecha, ids, manifiesto in filas_corridas:
        md.append(f"| [`{carpeta}`](../corridas/{carpeta}/) | {fecha} | {len(ids)} | "
                  f"{_celda(conjunto_de(ids, nombres, referencias))} | {_celda(resumen_configs(manifiesto))} |")
    return "\n".join(md) + "\n"


def main() -> int:
    referencias = {i: casos.cargar_referencia(i) for i in casos.ids_de_casos(particion="desarrollo")}
    listas = {p.stem: leer_lista(p) for p in sorted(DIR_LISTAS.glob("*.txt"))}
    manifiesto = json.loads(MANIFIESTO_DESARROLLO.read_text(encoding="utf-8")) if MANIFIESTO_DESARROLLO.exists() else {}
    estados = {i: c["estado"] for i, c in manifiesto.get("casos", {}).items() if c.get("estado")}
    SALIDA.write_text(armar(referencias, listas, corridas(DIR_CORRIDAS), estados), encoding="utf-8")
    print(f"Escrito {SALIDA.relative_to(RAIZ)}: {len(referencias)} casos de desarrollo, {len(listas)} listas.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
