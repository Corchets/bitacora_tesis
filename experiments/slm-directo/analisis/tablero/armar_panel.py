"""Arma panel.html: una sola página con el estado del ensayo, los casos, las corridas
guardadas y un probador en vivo contra Ollama.

Uso (desde la raíz del repositorio):
    python3 experiments/slm-directo/analisis/tablero/armar_panel.py            # solo escribe
    python3 experiments/slm-directo/analisis/tablero/armar_panel.py --servir   # escribe, sirve y abre

El probador habla con Ollama desde el navegador. Ollama rechaza páginas abiertas como
archivo (origen `null`), por eso `--servir` levanta un servidor en 127.0.0.1 con la raíz
del repositorio, para que también funcionen los enlaces a corridas y documentos.

> Estado: propuesta sin discutir. Es una vista sobre las fuentes del repositorio; no
> reemplaza los manifiestos ni las métricas registradas, y no cierra D07, D08 ni D09.
"""

from __future__ import annotations

import argparse
import csv
import functools
import http.server
import json
import sys
import webbrowser
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SLM = AQUI.parents[1]
REPO = AQUI.parents[3]
sys.path.insert(0, str(SLM))

import casos as mod_casos  # noqa: E402
import detectores  # noqa: E402

# Corridas completas sobre los 53 casos, más el 4B de M1 interrumpido (se marca parcial).
# Cuarto campo opcional: el prompt, cuando una carpeta tiene más de uno.
CORRIDAS = [
    ("2026-10-13_224418_linea-base-reglas", "reglas", "Reglas · Windows"),
    ("2026-10-14_173532_demo-qwen3.5-0.8b", "qwen3.5:0.8b", "Qwen3.5 0.8B · Windows GPU"),
    ("2026-10-14_172930_demo-qwen3.5-2b", "qwen3.5:2b", "Qwen3.5 2B · Windows GPU (1)"),
    ("2026-10-14_175451_demo-qwen3.5-2b", "qwen3.5:2b", "Qwen3.5 2B · Windows GPU (2)"),
    ("2026-10-14_174602_demo-qwen3.5-4b", "qwen3.5:4b", "Qwen3.5 4B · Windows GPU"),
    ("2026-10-17_150455_m1-reglas", "reglas", "Reglas · M1"),
    ("2026-10-17_150516_m1-gguf", "qwen3.5:0.8b-q8_0", "Qwen3.5 0.8B · M1"),
    ("2026-10-17_150516_m1-gguf", "qwen3.5:2b-q8_0", "Qwen3.5 2B · M1"),
    ("2026-10-17_150516_m1-gguf", "qwen3.5:4b-q4_K_M", "Qwen3.5 4B · M1 (parcial, 42/53)"),
    ("2026-10-21_182201_m1-0.8b-v1v2-nb32", "qwen3.5:0.8b-q8_0", "Qwen3.5 0.8B · M1 · num_batch 32", "tarea"),
    ("2026-10-21_182201_m1-0.8b-v1v2-nb32", "qwen3.5:0.8b-q8_0", "Qwen3.5 0.8B · M1 · prompt v2 (parcial, 24/53)", "v2"),
]


def _casos(resultados_tablero: dict) -> list[dict]:
    salida = []
    for cid in mod_casos.ids_de_casos(particion="desarrollo"):
        ref = mod_casos.cargar_referencia(cid)
        x = resultados_tablero.get(cid, {})
        salida.append(
            {
                "id": cid,
                "grupo": ref["grupo"],
                "clase": ref["clase"],
                "tipo_legitima": ref.get("tipo_legitima"),
                "revision_humana": ref["revision_humana"],
                "familia": ref.get("familia"),
                "variante_asr": ref.get("variante_asr", False),
                "tr": ref.get("t_r_linea"),
                "tc": ref.get("t_c_linea"),
                "pedido": ref.get("pedido"),
                "prueba": ref.get("que_prueba", ""),
                "notas": ref.get("notas", ""),
                "lineas": [[l.hablante, l.texto] for l in mod_casos.cargar_texto(cid)],
                "win": {k: x.get(k) for k in ("reglas", "q08", "q2", "q4")},
            }
        )
    return salida


def _corridas() -> list[dict]:
    salida = []
    for carpeta, modelo, nombre, *prompt in CORRIDAS:
        prompt = prompt[0] if prompt else None
        ruta = SLM / "corridas" / carpeta / "actualizaciones.csv"
        filas = []
        with ruta.open(encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                if (r["modelo"] or "reglas") != modelo or (prompt and r["prompt"] != prompt):
                    continue
                filas.append(
                    [
                        r["case_id"],
                        int(r["linea"]),
                        r["valida"] == "true",
                        float(r["riesgo"]) if r["riesgo"] else None,
                        r["alerta_sugerida"] == "true",
                        round(float(r["ms"]), 1) if r["ms"] else None,
                        r["motivo"][:160],
                        r["evidencia"][:200],
                    ]
                )
        salida.append({"id": f"{carpeta}|{modelo}" + (f"|{prompt}" if prompt else ""), "carpeta": carpeta, "modelo": modelo, "nombre": nombre, "filas": filas})
    return salida


def _e2e() -> list[dict]:
    """Tabla «Detector por variante y llamada» del resumen E2E."""
    texto = (REPO / "experiments/replay/corridas/2026-10-17_RESUMEN-E2E.md").read_text(encoding="utf-8")
    bloque = texto.split("## Detector por variante y llamada", 1)[1].split("\n## ", 1)[0]
    filas = []
    for renglon in bloque.splitlines():
        celdas = [c.strip() for c in renglon.strip().strip("|").split("|")]
        if len(celdas) != 11 or celdas[0] in ("Detector",) or set(celdas[0]) <= {"-", ":"}:
            continue
        num = lambda s: None if s in ("—", "") else float(s)  # noqa: E731
        filas.append(
            {"detector": celdas[0], "variante": celdas[1], "llamada": celdas[2], "aviso": celdas[3],
             "ta": num(celdas[4]), "lr": num(celdas[5]), "lc": num(celdas[6]), "fa": celdas[7],
             "p50": num(celdas[8]), "cola": num(celdas[9])}
        )
    return filas


def _audio_ref() -> list[dict]:
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted((REPO / "experiments/asr-local/audio-referencia").glob("*.json"))]


def armar() -> Path:
    errores = mod_casos.validar_todos()
    if errores:
        raise ValueError("No se puede generar el panel con casos inválidos: " + "; ".join(errores))
    datos_tablero = AQUI / "datos"
    res_tablero = {c["caso"]: c for c in json.loads((datos_tablero / "casos.json").read_text(encoding="utf-8"))}
    datos = {
        "casos": _casos(res_tablero),
        "reserva": {p: len(mod_casos.ids_de_casos(particion=p)) for p in sorted(mod_casos.PARTICIONES)},
        "corridas": _corridas(),
        "e2e": _e2e(),
        "audio_ref": _audio_ref(),
        "velocidad": json.loads((datos_tablero / "velocidad.json").read_text(encoding="utf-8")),
        "prompts": {v: detectores.cargar_prompt(v) for v in detectores.PROMPTS},
        "esquemas": {v: detectores.esquema_de(v) for v in detectores.PROMPTS},
        "opciones": {"temperature": 0.0, "seed": 42, "num_ctx": 4096, "num_predict": detectores.MAXIMO_TOKENS_RESPUESTA},
    }
    plantilla = (AQUI / "panel_plantilla.html").read_text(encoding="utf-8")
    js = json.dumps(datos, ensure_ascii=False).replace("</", "<\\/")
    salida = AQUI / "panel.html"
    salida.write_text(plantilla.replace("/*__DATOS__*/null", js), encoding="utf-8")
    return salida


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--servir", action="store_true", help="servir el repositorio en 127.0.0.1 y abrir el panel")
    p.add_argument("--puerto", type=int, default=8765)
    a = p.parse_args()
    salida = armar()
    print(f"Panel: {salida}")
    if not a.servir:
        return 0
    url = f"http://127.0.0.1:{a.puerto}/{salida.relative_to(REPO).as_posix()}"
    manejador = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(REPO))
    with http.server.ThreadingHTTPServer(("127.0.0.1", a.puerto), manejador) as srv:
        print(f"Abrí {url}  (Ctrl+C para cortar)")
        webbrowser.open(url)
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
