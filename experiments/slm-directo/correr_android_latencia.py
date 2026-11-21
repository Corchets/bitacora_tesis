"""#172: latencia de la configuración congelada en el A56, con variantes de la primera consulta.

Mismo recorrido que `correr_android_congelada.py` (todas las líneas, PROTEGIDA no consulta, motivo solo en el primer
aviso) y el mismo detector (`DetectorSLMCorteRiesgo`), pero sobre conversaciones de desarrollo: guarda el texto
crudo y el riesgo para comparar línea por línea. La primera consulta tiene tres modos (`--consulta`):

- `chat`: la de hoy. `/v1/chat/completions` con la gramática del JSON entero y `max_tokens` 14.
- `coma`: igual, pero la gramática termina en la coma que cierra el riesgo. Con temperatura 0 y las mismas reglas
  hasta ahí, los tokens son los mismos; solo deja de generar los que siguen a la coma.
- `numero`: el prompt del chat (`/apply-template`) más `{"riesgo":` (o `{\n  "riesgo":`, `--prefijo salto`) escrito por nosotros en el turno del modelo, a
  `/completion`, con una gramática que solo deja el número y la coma. El modelo genera 4 o 5 tokens.

La segunda consulta (motivo) es la misma en los tres modos. Los parámetros del servidor (hilos, lote, caché, backend)
no los fija este script: van en `--servidor` para el manifiesto, y `/props` se guarda tal cual.

    python correr_android_latencia.py --conversaciones conv.json --salida DIR_NUEVO --consulta coma --servidor "-t 4"
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import os
import platform
import time
import urllib.error
import urllib.request
from pathlib import Path

from casos import Linea
from cliente_ollama import ErrorOllama
from correr_android_congelada import _PRIMITIVAS, gramatica, sha
from detectores import DetectorSLMCorteRiesgo, cargar_prompt, esquema_de

MODELO = "gemma4:e2b-it-q4_K_M"
BASE = "http://127.0.0.1:18080"
# Lo que Gemma escribe antes del número con la gramática del JSON entero. Con c-premisa no es siempre igual: a veces
# compacto (`{"riesgo": 0.1, "alerta_s`) y a veces con salto (`{\n  "riesgo": 0.5,\n  `), según la transcripción.
# Sin el espacio final: el espacio y el número los genera el modelo.
PREFIJOS = {"compacto": '{"riesgo":', "salto": '{\n  "riesgo":'}


def gramatica_hasta_coma(esquema: dict) -> str:
    """La gramática de `gramatica(esquema)` cortada en la coma que sigue a la primera propiedad."""
    nombre, sub = next(iter(esquema["properties"].items()))
    reglas = [f'root ::= "{{" space "\\"{nombre}\\"" space ":" space {sub["type"]} ","']
    return "\n".join(reglas + [f"{k} ::= {v}" for k, v in _PRIMITIVAS.items()])


def gramatica_numero() -> str:
    """Después del prefijo: lo mismo que permite la gramática entera hasta la coma (`space number ","`)."""
    return "\n".join(['root ::= space number ","'] + [f"{k} ::= {v}" for k, v in _PRIMITIVAS.items()])


def _post(ruta: str, cuerpo: dict) -> dict:
    pedido = urllib.request.Request(BASE + ruta, data=json.dumps(cuerpo).encode(),
                                    headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(pedido, timeout=600) as r:
            return json.load(r)
    except (OSError, ValueError, urllib.error.URLError) as exc:
        raise ErrorOllama(str(exc)) from exc


def _medidas(tiempos: dict, contenido: str, fin: str) -> dict:
    return {"message": {"content": contenido}, "done_reason": fin,
            "prompt_eval_count": tiempos.get("prompt_n"), "eval_count": tiempos.get("predicted_n"),
            "prompt_eval_duration": int(tiempos.get("prompt_ms", 0) * 1_000_000),
            "eval_duration": int(tiempos.get("predicted_ms", 0) * 1_000_000)}


class Cliente:
    """Cliente de llama-server. La primera consulta (esquema con «riesgo» primero) va según `consulta`."""

    def __init__(self, consulta: str, esquema_riesgo: dict, prefijo: str = PREFIJOS["compacto"]) -> None:
        self.consulta = consulta
        self.prefijo = prefijo
        self.esquema_riesgo = esquema_riesgo
        self.ultimo_cache = None

    def chat(self, modelo, mensajes, formato, opciones, pensar=None):
        primera = formato == self.esquema_riesgo
        if primera and self.consulta == "numero":
            prompt = _post("/apply-template", {"messages": mensajes,
                                               "chat_template_kwargs": {"enable_thinking": False}})["prompt"]
            salida = _post("/completion", {"prompt": prompt + self.prefijo, "temperature": opciones["temperature"],
                                           "seed": opciones["seed"], "n_predict": opciones["num_predict"],
                                           "grammar": gramatica_numero(), "cache_prompt": True})
            tiempos = salida.get("timings", {})
            self.ultimo_cache = tiempos.get("cache_n")
            return _medidas(tiempos, self.prefijo + salida["content"], "length" if salida.get("stop_type") == "limit" else "stop")
        g = gramatica_hasta_coma(formato) if primera and self.consulta == "coma" else gramatica(formato)
        salida = _post("/v1/chat/completions", {
            "model": modelo, "messages": mensajes, "temperature": opciones["temperature"], "seed": opciones["seed"],
            "max_tokens": opciones["num_predict"], "grammar": g,
            "chat_template_kwargs": {"enable_thinking": False}, "stream": False})
        choice = salida["choices"][0]
        tiempos = salida.get("timings", {})
        self.ultimo_cache = tiempos.get("cache_n")
        return _medidas(tiempos, choice["message"]["content"], choice["finish_reason"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--conversaciones", required=True)
    parser.add_argument("--salida", required=True)
    parser.add_argument("--prompt", default="c-premisa-corte-riesgo")
    parser.add_argument("--consulta", choices=("chat", "coma", "numero"), default="chat")
    parser.add_argument("--prefijo", choices=sorted(PREFIJOS), default="compacto")
    parser.add_argument("--servidor", default="", help="los parámetros de llama-server, para el manifiesto")
    args = parser.parse_args()
    ruta = Path(args.conversaciones)
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    esquema = esquema_de(args.prompt)

    cliente = Cliente(args.consulta, esquema, PREFIJOS[args.prefijo])
    detector = DetectorSLMCorteRiesgo(cliente, MODELO, cargar_prompt(args.prompt), "rol", 4096, 42, esquema=esquema)
    calentamiento = detector.evaluar((Linea("OTRA", "Hola, ¿qué tal?"),))
    detector.reiniciar()

    destino = Path(args.salida)
    destino.mkdir(parents=True, exist_ok=False)
    aqui = Path(__file__).resolve().parent
    with urllib.request.urlopen(BASE + "/props", timeout=30) as r:
        props = json.load(r)
    manifiesto = {
        "experimento": "a56-latencia-172",
        "configuracion": {"prompt": args.prompt, "modelo": MODELO, "detector": type(detector).__name__,
                          "consulta": args.consulta,
                          "prefijo": PREFIJOS[args.prefijo] if args.consulta == "numero" else None, "hablantes": "rol", "solo_otra": True, "num_ctx": 4096,
                          "seed": 42, "temperatura": detector.opciones()["temperature"],
                          "num_predict": detector.opciones()["num_predict"], "umbral": detector.umbral,
                          "recorrido": "todas las líneas, sin detener al primer aviso; PROTEGIDA no consulta"},
        "servidor": args.servidor,
        "props": {k: v for k, v in props.items() if k not in ("chat_template", "default_generation_settings")},
        "casos": list(datos["casos"]),
        "conversaciones_sha256": sha(ruta.read_bytes()),
        "prompt_sha256": sha(cargar_prompt(args.prompt).encode()),
        "motivo_sha256": sha(detector.pedido_motivo.encode()),
        "codigo_sha256": {p.name: sha(p.read_bytes()) for p in
                          [Path(__file__).resolve(), aqui / "correr_android_congelada.py", aqui / "detectores.py",
                           aqui / "casos.py"]},
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
                linea = Linea(r["hablante"], r["texto"])
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
                print(caso, r["n"], fila["hablante"], round(fila.get("total_ms") or 0), fila.get("riesgo"), flush=True)
    manifiesto["fin"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    (destino / "manifiesto.json").write_text(json.dumps(manifiesto, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
