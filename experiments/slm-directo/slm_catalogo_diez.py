"""Consulta Gemma en cada actualización puntuada del catálogo de diez opciones.

Las variantes con Tito se calculan después a partir de los mismos resultados:
solo conservan las consultas donde Tito se activó en esa actualización.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from casos import cargar_texto
from cliente_ollama import ClienteOllama
from detectores import DetectorSLM, armar_mensaje_usuario, cargar_prompt, esquema_de, huella
from ensayo_catalogo_qwen import guardar, lista, sha

ROOT = Path(__file__).resolve().parent
CATALOGO = ROOT / "prompts" / "catalogo-qwen-diez-v2.json"


def leer(ruta: Path, ids: list[str]):
    registros = [json.loads(s) for s in ruta.read_text(encoding="utf-8").splitlines()]
    if not registros or registros[0].get("tipo") != "manifiesto" or registros[-1].get("tipo") != "fin":
        raise ValueError("La corrida del reranker no terminó")
    m = registros[0]
    if m.get("experimento") != "catalogo-diez-gemma-siempre-v1" or m.get("lista") != "rapida-20":
        raise ValueError("La entrada no pertenece a esta prueba")
    if m.get("catalogo_sha256") != sha(CATALOGO):
        raise ValueError("El catálogo no coincide con el usado por el reranker")
    if len(set(m["casos"])) != len(m["casos"]) or set(m["casos"]) != set(ids):
        raise ValueError("La corrida no cubre los casos requeridos")
    if any(r["tipo"].startswith("error_") for r in registros):
        raise ValueError("Hay errores del reranker")
    filas = [r for r in registros if r["tipo"] == "actualizacion"]
    esperado = {(c, n, v) for c in ids for n in range(1, len(cargar_texto(c)) + 1)
                for v in ("linea", "par") if v == "linea" or n % 2 == 0}
    claves = [(r["case_id"], r["linea"], r["ventana"]) for r in filas]
    if len(claves) != len(set(claves)) or set(claves) != esperado:
        raise ValueError("Faltan actualizaciones o están duplicadas")
    if any(r["linea_inicio"] != r["linea"] - (r["ventana"] == "par") for r in filas):
        raise ValueError("Hay ventanas inconsistentes")
    return m, filas


def elegir_opcion(puntajes: dict, textos: dict) -> str:
    """Una opción siempre gana, incluso si todos los puntajes son bajos."""
    if not puntajes or set(puntajes) != set(textos):
        raise ValueError("Categorías inconsistentes")
    return max(puntajes, key=puntajes.get)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("reranker", type=Path)
    p.add_argument("--salida", type=Path, required=True)
    p.add_argument("--casos", help="IDs del informe separados por coma, para prueba corta")
    args = p.parse_args()
    ids_permitidos = set(lista("rapida-20"))
    with args.reranker.open(encoding="utf-8") as f:
        ids = json.loads(f.readline()).get("casos", [])
    if not ids or not set(ids) <= ids_permitidos:
        p.error("El archivo debe contener casos del informe")
    manifiesto_rr, filas = leer(args.reranker, ids)
    elegidos = args.casos.split(",") if args.casos else ids
    if not elegidos or len(elegidos) != len(set(elegidos)) or not set(elegidos) <= set(ids):
        p.error("Los IDs deben pertenecer a la corrida y no repetirse")
    categorias = json.loads(CATALOGO.read_text(encoding="utf-8"))["categorias"]
    textos = {c["id"]: c["texto"] for c in categorias}
    if len(textos) != 10 or "POSSIBLE_DECEPTION" in textos:
        raise ValueError("El catálogo debe contener diez opciones sin posible engaño")
    cliente = ClienteOllama(timeout_s=120)
    modelo = "gemma4:e2b"
    digest = cliente.modelos_instalados().get(modelo)
    if not digest:
        raise RuntimeError("gemma4:e2b no está instalado")
    cliente._pedir("/api/generate", {"model": modelo, "keep_alive": "10m",
                                     "options": {"num_gpu": 99, "num_ctx": 4096}})
    memoria = cliente.memoria_cargada(modelo)
    if not memoria or not memoria.get("size_bytes") or memoria.get("size_vram_bytes", 0) < memoria["size_bytes"]:
        raise RuntimeError(f"Ollama no informa el modelo completamente en GPU: {memoria}")
    prompt = cargar_prompt("v2")
    slm = DetectorSLM(cliente, modelo, prompt, num_ctx=4096, seed=42, pensar=False,
                      extra={"num_gpu": 99}, esquema=esquema_de("v2"))
    with args.salida.open("x", encoding="utf-8") as salida:
        guardar(salida, {"tipo": "manifiesto", "experimento": "catalogo-diez-gemma-siempre-v1",
                         "estado": "desarrollo, no evaluación final", "reranker_sha256": sha(args.reranker),
                         "catalogo_sha256": sha(CATALOGO), "ejecutor_sha256": sha(Path(__file__)),
                         "modelo": modelo, "digest": digest, "prompt_variante": "v2",
                         "prompt_huella": huella(prompt), "seed": 42, "num_ctx": 4096,
                         "think": False, "opciones": slm.opciones(), "ollama_version": cliente.version(),
                         "memoria_modelo": memoria, "casos": elegidos, "python": sys.version,
                         "politica": "consultar cada actualización válida; sin umbral ni veto",
                         "con_tito": "reconstrucción offline filtrando por tito_activa",
                         "reranker_revision": manifiesto_rr["revision_resuelta"]})
        for case_id in elegidos:
            lineas = cargar_texto(case_id)
            propias = sorted((r for r in filas if r["case_id"] == case_id),
                             key=lambda r: (r["linea"], r["ventana"]))
            for r in propias:
                n, puntajes = r["linea"], r["puntajes"]
                ganador = elegir_opcion(puntajes, textos)
                orden = sorted(puntajes, key=puntajes.get, reverse=True)
                detalle = "\n".join(f"- {textos[k]}: {puntajes[k]:.5f}" for k in orden)
                contexto = lineas[:n]
                mensaje = (armar_mensaje_usuario(contexto, "ab") +
                           "\n\nUn reranker comparó lo disponible con un catálogo. "
                           f"La opción mejor puntuada fue: {textos[ganador]}\n"
                           "Sus puntajes son indicios falibles, no probabilidades ni prueba de fraude. "
                           "Evaluá independientemente el contexto y podés rechazarlos:\n" + detalle)
                respuesta = slm.evaluar_mensaje(mensaje, contexto)
                guardar(salida, {"tipo": "consulta", "case_id": case_id, "linea": n,
                                 "ventana": r["ventana"], "linea_inicio": r["linea_inicio"],
                                 "opcion_principal": ganador, "tito_activa": r["tito_activa"],
                                 "tito_puntaje": r["tito_puntaje"], "respuesta": asdict(respuesta)})
            print(f"{case_id}: {len(propias)} consultas a Gemma", flush=True)
        guardar(salida, {"tipo": "fin"})


if __name__ == "__main__":
    main()
