"""Integración secundaria Gemma: activa solo ante sospecha del reranker."""
import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from analizar_catalogo_lineas import VENTANAS, leer
from analizar_catalogo_qwen import DETECCION, SITUACIONES
from casos import cargar_texto
from cliente_ollama import ClienteOllama
from detectores import DetectorSLM, armar_mensaje_usuario, cargar_prompt, esquema_de, huella
from ensayo_catalogo_qwen import CATALOGO, guardar, sha


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("informe", type=Path)
    p.add_argument("umbrales", type=Path)
    p.add_argument("--salida", type=Path, required=True)
    p.add_argument("--casos", help="subset de casos para prueba de humo")
    args = p.parse_args()
    manifiesto, filas, _ = leer(args.informe, "rapida-20")
    u = json.loads(args.umbrales.read_text(encoding="utf-8"))
    umbrales = {(r["ventana"], r["con_tito"]): r["umbral"] for r in u["umbrales"]}
    ids = args.casos.split(",") if args.casos else manifiesto["casos"]
    if not ids or len(ids) != len(set(ids)) or not set(ids) <= set(manifiesto["casos"]):
        p.error("IDs repetidos o fuera de la lista de informe")
    cliente = ClienteOllama(timeout_s=120)
    modelo = "gemma4:e2b"
    digest = cliente.modelos_instalados().get(modelo)
    if not digest:
        raise RuntimeError("gemma4:e2b no está instalado")
    cliente._pedir("/api/generate", {"model": modelo, "keep_alive": "10m",
                                     "options": {"num_gpu": 99, "num_ctx": 4096}})
    memoria = cliente.memoria_cargada(modelo)
    if not memoria or not memoria.get("size_bytes") or memoria.get("size_vram_bytes", 0) < memoria["size_bytes"]:
        raise RuntimeError(f"El SLM no está completamente en GPU: {memoria}")
    prompt = cargar_prompt("v2")
    slm = DetectorSLM(cliente, modelo, prompt, num_ctx=4096, seed=42, pensar=False,
                      extra={"num_gpu": 99}, esquema=esquema_de("v2"))
    categorias = {c["id"]: c["texto"] for c in json.loads(CATALOGO.read_text(encoding="utf-8"))["categorias"]}
    condiciones = [(v, t, politica) for v in VENTANAS for t in (False, True)
                   for politica in ("mayor_puntaje", "mayor_y_umbral")]
    estados = {(c, *cond): False for c in ids for cond in condiciones}
    with args.salida.open("x", encoding="utf-8") as salida:
        guardar(salida, {"tipo": "manifiesto", "estado": "integración secundaria de desarrollo",
                         "experimento": "catalogo-qwen-linea-y-par-v1", "informe_sha256": sha(args.informe),
                         "umbrales_sha256": sha(args.umbrales), "ejecutor_sha256": sha(Path(__file__)),
                         "modelo": modelo, "digest": digest, "prompt_variante": "v2",
                         "prompt_huella": huella(prompt), "seed": 42, "num_ctx": 4096,
                         "think": False, "opciones": slm.opciones(), "ollama_version": cliente.version(),
                         "memoria_modelo": memoria, "casos": ids, "python": sys.version})
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
            print(f"{case_id}: SLM terminado", flush=True)
        guardar(salida, {"tipo": "fin", "consultas_con_alerta_por_condicion": [
            {"case_id": c, "ventana": v, "con_tito": t, "politica": politica, "alerto": estado}
            for (c, v, t, politica), estado in estados.items()]})


if __name__ == "__main__":
    main()
