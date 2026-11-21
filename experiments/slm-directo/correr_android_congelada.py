"""a56-congelada-latencia: la configuración congelada de #143 en el Samsung A56, con llama-server local.

Mismo detector que `correr.py --prompts c-json-corte-riesgo --solo-otra --hablantes rol --sin-reglas`
(DetectorSLMCorteRiesgo: num_predict 14, aviso con riesgo >= 0,3, motivo de C solo en el primer aviso), pero con el
cliente de `correr_android.py` (API compatible con OpenAI de llama-server, sin razonamiento, esquema JSON). Corre sin
Tito, sin torch y sin `correr.py` (que importa Tito y el reranker).

Mide latencia: recorre todas las líneas aunque ya haya avisado (modo diagnóstico, como `--seguir-tras-aviso`). Las
líneas de PROTEGIDA entran al contexto sin consultar (ADR 0007). Las conversaciones salen de un JSON con renglones
{n, hablante A/B, texto}; A = OTRA.

    python correr_android_congelada.py --conversaciones conversaciones.json --salida DIR_NUEVO
"""
from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import os
import platform
import time
import urllib.error
import urllib.request
from pathlib import Path

from casos import Linea
from cliente_ollama import ErrorOllama
from detectores import DetectorSLMCorteRiesgo, cargar_prompt, esquema_de

PROMPT = "c-json-corte-riesgo"
MODELO = "gemma4:e2b-it-q4_K_M"
URL = "http://127.0.0.1:18080/v1/chat/completions"


_PRIMITIVAS = {
    "space": '| " " | "\\n"{1,2} [ \\t]{0,20}',
    "boolean": '("true" | "false") space',
    "integral-part": "[0] | [1-9] [0-9]{0,15}",
    "decimal-part": "[0-9]{1,16}",
    "number": '("-"? integral-part) ("." decimal-part)? ([eE] [-+]? integral-part)? space',
    "char": '[^"\\\\\\x7F\\x00-\\x1F] | [\\\\] (["\\\\bfnrt] | "u" [0-9a-fA-F]{4})',
    "string": '"\\"" char* "\\"" space',
}


def gramatica(esquema: dict) -> str:
    """GBNF de un esquema objeto plano (propiedades number/boolean/string, todas requeridas, en orden).

    Sigue las reglas primitivas de `json-schema-to-grammar` de llama.cpp, que es lo que Ollama aplica con `format`.
    Hace falta porque este llama-server, con la plantilla de Gemma, aplica `response_format` de forma perezosa y deja
    pasar un bloque ```json antes del objeto (3 tokens que dejan la coma del riesgo fuera de los 14). `minimum` y
    `maximum` de un number no se traducen, como en llama.cpp.
    """
    props = esquema["properties"]
    if esquema.get("required") != list(props) or esquema.get("type") != "object":
        raise ValueError("solo objetos planos con todas las propiedades requeridas y en orden")
    partes = []
    for i, (nombre, sub) in enumerate(props.items()):
        if sub["type"] not in ("number", "boolean", "string"):
            raise ValueError(f"tipo no soportado: {sub['type']}")
        coma = '"," space ' if i else ""
        partes.append(f'{coma}"\\"{nombre}\\"" space ":" space {sub["type"]}')
    reglas = [f'root ::= "{{" space {" ".join(partes)} "}}" space']
    reglas += [f"{k} ::= {v}" for k, v in _PRIMITIVAS.items()]
    return "\n".join(reglas)


class ClienteLlama:
    """Como en correr_android.py, pero el esquema va como gramática GBNF (`grammar`), que llama-server sí aplica."""

    ultimo_cache = None

    def chat(self, modelo, mensajes, formato, opciones, pensar=None):
        cuerpo = {
            "model": modelo, "messages": mensajes, "temperature": opciones["temperature"],
            "seed": opciones["seed"], "max_tokens": opciones["num_predict"],
            "grammar": gramatica(formato),
            "chat_template_kwargs": {"enable_thinking": False}, "stream": False,
        }
        pedido = urllib.request.Request(URL, data=json.dumps(cuerpo).encode(),
                                        headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(pedido, timeout=600) as r:
                salida = json.load(r)
        except (OSError, ValueError, urllib.error.URLError) as exc:
            raise ErrorOllama(str(exc)) from exc
        choice = salida["choices"][0]
        tiempos = salida.get("timings", {})
        self.ultimo_cache = tiempos.get("cache_n")
        return {"message": choice["message"], "done_reason": choice["finish_reason"],
                "prompt_eval_count": tiempos.get("prompt_n"), "eval_count": tiempos.get("predicted_n"),
                "prompt_eval_duration": int(tiempos.get("prompt_ms", 0) * 1_000_000),
                "eval_duration": int(tiempos.get("predicted_ms", 0) * 1_000_000)}


def sha(datos: bytes) -> str:
    return hashlib.sha256(datos).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--conversaciones", required=True)
    parser.add_argument("--salida", required=True)
    args = parser.parse_args()
    ruta = Path(args.conversaciones)
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    roles = datos["roles"]

    cliente = ClienteLlama()
    detector = DetectorSLMCorteRiesgo(cliente, MODELO, cargar_prompt(PROMPT), "rol", 4096, 42,
                                      esquema=esquema_de(PROMPT))
    # Calentamiento con una línea neutra, ajena a las conversaciones: no entra a los turnos.
    calentamiento = detector.evaluar((Linea("OTRA", "Hola, ¿qué tal?"),))
    detector.reiniciar()

    destino = Path(args.salida)
    destino.mkdir(parents=True, exist_ok=False)
    aqui = Path(__file__).resolve().parent
    manifiesto = {
        "experimento": "a56-congelada-latencia",
        "configuracion": {"prompt": PROMPT, "modelo": MODELO, "detector": type(detector).__name__,
                          "hablantes": "rol", "solo_otra": True, "num_ctx": 4096, "seed": 42,
                          "temperatura": detector.opciones()["temperature"],
                          "num_predict": detector.opciones()["num_predict"], "umbral": detector.umbral,
                          "recorrido": "todas las líneas, sin detener al primer aviso; PROTEGIDA no consulta"},
        "casos": list(datos["casos"]),
        "conversaciones_sha256": sha(ruta.read_bytes()),
        "prompt_sha256": sha(cargar_prompt(PROMPT).encode()),
        "motivo_sha256": sha(detector.pedido_motivo.encode()),
        "codigo_sha256": {p.name: sha(p.read_bytes()) for p in
                          [Path(__file__).resolve(), aqui / "detectores.py", aqui / "casos.py"]},
        "calentamiento": {"valida": calentamiento.valida, "error": calentamiento.error, "ms": calentamiento.ms},
        "sistema": platform.platform(), "python": platform.python_version(), "pid": os.getpid(),
        "inicio": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    (destino / "manifiesto.json").write_text(json.dumps(manifiesto, ensure_ascii=False, indent=2))

    with (destino / "turnos.jsonl").open("w", encoding="utf-8", buffering=1) as archivo:
        for caso, renglones in datos["casos"].items():
            detector.reiniciar()
            disponibles: list[Linea] = []
            aviso_en = None
            for r in renglones:
                linea = Linea(roles[r["hablante"]], r["texto"])
                disponibles.append(linea)
                fila = {"case_id": caso, "linea": r["n"], "hablante": linea.hablante}
                if linea.hablante != "OTRA":
                    fila["consulta"] = "omitida"
                else:
                    inicio = time.perf_counter()
                    respuesta = detector.evaluar(tuple(disponibles))
                    total_ms = (time.perf_counter() - inicio) * 1000
                    fila.update(dataclasses.asdict(respuesta))
                    fila.update(total_ms=total_ms, consulta="slm", tokens_cache=cliente.ultimo_cache)
                    if aviso_en is None and respuesta.valida and respuesta.alerta_sugerida:
                        aviso_en = r["n"]
                    fila["primer_aviso"] = aviso_en == r["n"]
                archivo.write(json.dumps(fila, ensure_ascii=False) + "\n")
                # Por consola solo tiempos: las salidas del detector no se miran (conversaciones de test de #144).
                print(caso, r["n"], fila["hablante"], round(fila.get("total_ms") or 0), flush=True)
    manifiesto["fin"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    (destino / "manifiesto.json").write_text(json.dumps(manifiesto, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
