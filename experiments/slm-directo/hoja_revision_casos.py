"""Arma el documento para leer y revisar los casos de desarrollo.

Es una vista de casos/texto y casos/referencia, que siguen siendo la fuente de verdad. Solo
incluye la partición de desarrollo: la reserva nunca entra.

Uso:
    python hoja_revision_casos.py
"""

from __future__ import annotations

import re
from pathlib import Path

import casos

SALIDA = casos.RAIZ.parents[1] / "docs" / "corpus" / "REVISION-HUMANA-CASOS-DESARROLLO.md"
INFORME_101 = casos.RAIZ / "corridas" / "2026-10-30_112956_101_informe_101.md"
GRABACIONES = casos.RAIZ / "casos" / "GRABACIONES-ASR.md"
PROPUESTA = "> **Estado: propuesta sin discutir.**"
SECCIONES = (
    ("Estafas del corpus v2", lambda i, r: i.startswith("CV2-") and r["clase"] == "vishing"),
    ("Legítimas del corpus v2", lambda i, r: i.startswith("CV2-")),
    ("Casos trampa", lambda i, r: i.startswith("TR-")),
    ("Piloto escrito: estafas", lambda i, r: i.startswith("SC-")),
    ("Piloto escrito: legítimas", lambda i, r: i.startswith("LG-")),
    ("Laboratorio", lambda i, r: i.startswith("LAB-")),
)


def ids_de_la_matriz() -> set[str]:
    return set(re.findall(r"^\| `(CV2-[^`]+)`", INFORME_101.read_text(encoding="utf-8"), re.M))


def ids_para_grabar() -> set[str]:
    primera = GRABACIONES.read_text(encoding="utf-8").split("## 2.")[0]
    return set(re.findall(r"^\| \[([^\]]+)\]\(texto/", primera, re.M))


def marcas_de_linea(n: int, ref: dict) -> str:
    marcas = [f"**{m}**" for m, c in (("T_R", "t_r_linea"), ("T_C", "t_c_linea")) if ref[c] == n]
    for e in ref["evidencia"]:
        if e["linea"] == n:
            marcas.append(", ".join(f"`{x}`" for x in e["etiquetas"]) or f"_{e['evento']}_")
    return f" ← {' · '.join(marcas)}" if marcas else ""


def bloque_de_caso(case_id: str, ref: dict, matriz: set[str], grabar: set[str]) -> str:
    datos = [ref["clase"], ref.get("familia"), ref.get("dificultad")]
    if ref.get("variante_asr"):
        datos.append("con errores escritos de ASR")
    if case_id in matriz:
        datos.append("**en la matriz #101**")
    if case_id in grabar:
        datos.append("**propuesto para grabar**")
    texto = casos.cargar_texto(case_id)
    salida = [f"### {case_id}", "", " · ".join(d for d in datos if d) + f" · {len(texto)} líneas", ""]
    if ref.get("situacion"):
        salida += [f"**Situación:** {ref['situacion']}", ""]
    for n, linea in enumerate(texto, start=1):
        salida.append(f"`{n:>2}` **{linea.hablante}:** {linea.texto}{marcas_de_linea(n, ref)}  ")
    es_estafa = ref["clase"] == "vishing"
    marcas = f"`T_R` {ref['t_r_linea'] or '—'}, `T_C` {ref['t_c_linea'] or '—'}, pedido {ref['pedido'] or '—'}"
    notas = ref["notas"].replace(PROPUESTA, "").strip()
    salida += ["", f"**Referencia de trabajo:** {marcas}.", "", f"**Qué prueba:** {ref['que_prueba']}", ""]
    if notas:
        salida += [f"**Notas de la referencia:** {notas}", ""]
    salida += ["- [ ] La clase está bien"]
    salida += ["- [ ] `T_R` y `T_C` están bien"] if es_estafa else ["- [ ] De acuerdo: no hay pedido crítico"]
    salida += ["- [ ] Suena a una conversación real", "- [ ] Grabarlo", "", "**Comentarios:**", "", "---", ""]
    return "\n".join(salida)


def main() -> None:
    ids = casos.ids_de_casos("desarrollo")
    if any(i.startswith("CV2-T-") for i in ids):
        raise SystemExit("La reserva no puede entrar en este documento.")
    refs = {i: casos.cargar_referencia(i) for i in ids}
    matriz, grabar = ids_de_la_matriz(), ids_para_grabar()
    grupos: list[tuple[str, list[str]]] = []
    resto = sorted(ids)
    for titulo, pertenece in SECCIONES:
        grupo = [i for i in resto if pertenece(i, refs[i])]
        resto = [i for i in resto if i not in grupo]
        grupos.append((titulo, grupo))
    if resto:
        raise SystemExit(f"Casos sin sección: {resto}")

    primero = sorted(matriz | grabar)
    partes = [
        "# Revisión humana de los casos de desarrollo", "",
        f"Los {len(ids)} casos de desarrollo, para leerlos y corregirlos. Todos son ficticios y ninguno tiene "
        "todavía revisión humana. La reserva (`CV2-T-*`) no está acá.", "",
        "Generado con `experiments/slm-directo/hoja_revision_casos.py`: los diálogos y las marcas viven en "
        "[`casos/texto`](../../experiments/slm-directo/casos/texto) y "
        "[`casos/referencia`](../../experiments/slm-directo/casos/referencia). Volver a generarlo pisa lo que "
        "se haya marcado acá.", "",
        "## Antes de leer", "",
        "- **Esto no cierra [D07](../gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico).** Sirve "
        "para corregir casos. D07 pide además que los cuatro integrantes anoten por separado una muestra común, "
        "sin ver respuestas ajenas, y acá las marcas ya están a la vista.",
        "- **`revision_humana` sigue en `false`** hasta pasar lo revisado a cada referencia.",
        "- **Quien vaya a atender una llamada grabada no debería leer ese caso antes:** el "
        "[método](METODO-CREACION-CORPUS.md) pide que no conozca la clase.", "",
        "## Qué significan las marcas", "",
        "- `T_R`: línea donde empieza el pedido crítico. `T_C`: línea donde la persona cumple. Ver el "
        "[manual](MANUAL-ANOTACION.md).",
        "- Las etiquetas al final de una línea son la evidencia que la referencia eligió.", "",
        "## Por dónde empezar", "",
        f"Estos {len(primero)} son los de la matriz #101 o los [propuestos para grabar](../../experiments/slm-directo/casos/GRABACIONES-ASR.md):", "",
        ", ".join(f"[{i}](#{i.lower()})" for i in primero), "",
        "## Contenido", "",
        "| Sección | Casos |", "|---|---:|",
        *[f"| {t} | {len(g)} |" for t, g in grupos], "",
    ]
    for titulo, grupo in grupos:
        partes += [f"## {titulo}", ""]
        partes += [bloque_de_caso(i, refs[i], matriz, grabar) for i in grupo]
    Path(SALIDA).write_text("\n".join(partes), encoding="utf-8")
    print(f"{SALIDA}: {len(ids)} casos")


if __name__ == "__main__":
    main()
