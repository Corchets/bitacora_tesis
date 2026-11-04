"""Seguimiento secundario con SLM para los avisos sospechosos del catálogo.

Trabaja sobre las salidas ya calculadas, sin referencia humana ni texto futuro en
los prompts. No modifica el resultado principal del reranker. Requiere Ollama y
verifica que el modelo esté completamente cargado en GPU antes de inferir.
"""
import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from analizar_catalogo_qwen import DETECCION, SITUACIONES, leer
from casos import cargar_texto
from cliente_ollama import ClienteOllama
from detectores import DetectorSLM, armar_mensaje_usuario, cargar_prompt, esquema_de, huella
from ensayo_catalogo_qwen import CATALOGO, guardar, sha


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("informe", type=Path)
    p.add_argument("umbrales", type=Path)
    p.add_argument("--salida", type=Path, required=True)
    p.add_argument("--modelo", default="gemma4:e2b")
    p.add_argument("--casos", help="subset de IDs de informe para comprobación")
    args = p.parse_args()
    manifiesto, filas = leer(args.informe, "rapida-20")
    u = json.loads(args.umbrales.read_text(encoding="utf-8"))
    umbrales = {(r["ventana"], r["con_tito"]): r["umbral"] for r in u["umbrales"]}
    ids = args.casos.split(",") if args.casos else manifiesto["casos"]
    if not ids or len(ids) != len(set(ids)) or not set(ids) <= set(manifiesto["casos"]):
        p.error("IDs repetidos o fuera de la lista de informe")
    cliente = ClienteOllama(timeout_s=120)
    digest = cliente.modelos_instalados().get(args.modelo)
    if not digest:
        p.error("El modelo SLM no está instalado en Ollama")
    # Se carga sin inferir y se rechaza cualquier offload parcial a CPU.
    cliente._pedir("/api/generate", {"model": args.modelo, "keep_alive": "10m",
                                     "options": {"num_gpu": 99, "num_ctx": 4096}})
    memoria = cliente.memoria_cargada(args.modelo)
    if not memoria or not memoria.get("size_bytes") or memoria.get("size_vram_bytes", 0) < memoria["size_bytes"]:
        raise RuntimeError(f"El SLM no está totalmente cargado en GPU: {memoria}")
    prompt = cargar_prompt("v2")
    slm = DetectorSLM(cliente, args.modelo, prompt, num_ctx=4096, seed=42, pensar=False,
                      extra={"num_gpu": 99}, esquema=esquema_de("v2"))
    categorias = {c["id"]: c["texto"] for c in json.loads(CATALOGO.read_text(encoding="utf-8"))["categorias"]}
    condiciones = [(v, t, politica) for v in ("cuatro", "acumulada") for t in (False, True)
                   for politica in ("mayor_puntaje", "mayor_y_umbral")]
    estados = {(c, *cond): False for c in ids for cond in condiciones}
    with args.salida.open("x", encoding="utf-8") as salida:
        guardar(salida, {"tipo": "manifiesto", "estado": "integración secundaria de desarrollo",
                         "informe_sha256": sha(args.informe), "umbrales_sha256": sha(args.umbrales),
                         "ejecutor_sha256": sha(Path(__file__)), "modelo": args.modelo, "digest": digest,
                         "prompt_variante": "v2", "prompt_huella": huella(prompt), "seed": 42,
                         "num_ctx": 4096, "think": False, "opciones": slm.opciones(),
                         "ollama_version": cliente.version(), "memoria_modelo": memoria, "casos": ids,
                         "python": sys.version})
        for case_id in ids:
            lineas = cargar_texto(case_id)
            propias = sorted((r for r in filas if r["case_id"] == case_id),
                             key=lambda r: (r["linea"], r["ventana"]))
            for r in propias:
                ventana, n, puntajes = r["ventana"], r["linea"], r["puntajes"]
                ganador = max((k for k in puntajes if k in SITUACIONES), key=puntajes.get)
                if ganador != DETECCION:
                    continue
                activas = []
                for v, tito, politica in condiciones:
                    if v != ventana or (tito and not r["tito_activa"]) or estados[(case_id, v, tito, politica)]:
                        continue
                    if politica == "mayor_y_umbral" and puntajes[ganador] <= umbrales[(v, tito)]:
                        continue
                    activas.append((v, tito, politica))
                if not activas:
                    continue
                contexto = lineas[:n]
                orden = sorted(puntajes, key=puntajes.get, reverse=True)
                indicios = "\n".join(f"- {categorias[k]}: {puntajes[k]:.5f}" for k in orden)
                mensaje = (armar_mensaje_usuario(contexto, "ab") +
                           "\n\nUn filtro previo produjo los siguientes puntajes de relevancia. "
                           "Son indicios falibles, no probabilidades ni prueba de fraude. "
                           "Evaluá independientemente el contexto y podés rechazarlos:\n" + indicios)
                respuesta = slm.evaluar_mensaje(mensaje, contexto)
                if respuesta.valida and respuesta.alerta_sugerida:
                    for v, tito, politica in activas:
                        estados[(case_id, v, tito, politica)] = True
                guardar(salida, {"tipo": "consulta", "case_id": case_id, "linea": n,
                                 "ventana": ventana, "condiciones": activas, "respuesta": asdict(respuesta)})
                print(f"{case_id} línea {n} {ventana}: válida={respuesta.valida} alerta={respuesta.alerta_sugerida}", flush=True)
        guardar(salida, {"tipo": "fin", "consultas_con_alerta_por_condicion": [
            {"case_id": c, "ventana": v, "con_tito": t, "politica": p, "alerto": estado}
            for (c, v, t, p), estado in estados.items()]})


if __name__ == "__main__":
    main()
