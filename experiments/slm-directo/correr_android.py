"""Ensayo exploratorio en Android: Tito viejo 2.0 y llama-server local."""
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

import casos
import tito_real
from cliente_ollama import ErrorOllama
from detectores import DetectorSLM, cargar_prompt, esquema_de
from tito_viejo_2 import TitoViejo20

CASOS = [
    "CV2-D-V-BANCO-001", "CV2-D-V-BANCO-006", "CV2-D-V-WHATSAPP-001",
    "CV2-D-V-WHATSAPP-004", "CV2-D-V-SOPORTE-001", "CV2-D-V-SOPORTE-007",
    "CV2-D-V-ORGANISMO_PREVISIONAL-003", "CV2-D-V-ORGANISMO_PREVISIONAL-005",
    "CV2-D-V-PREMIO-003", "CV2-D-V-FAMILIAR-001", "CV2-D-L-BANCO-006",
    "CV2-D-L-DELIVERY-001", "CV2-D-L-ESCUELA-001", "CV2-D-L-FAMILIAR-001",
    "CV2-D-L-MEDICO-001", "CV2-D-L-ORGANISMO_PREVISIONAL-001",
    "CV2-D-L-PREMIO-001", "CV2-D-L-SOPORTE-004", "CV2-D-L-TRABAJO-001",
    "CV2-D-L-WHATSAPP-004",
]


class ClienteLlama:
    ultimo_cache = None

    def chat(self, modelo, mensajes, formato, opciones, pensar=None):
        cuerpo = {
            "model": modelo, "messages": mensajes, "temperature": opciones["temperature"],
            "seed": opciones["seed"], "max_tokens": opciones["num_predict"],
            "response_format": {"type": "json_schema", "json_schema": {"name": "riesgo", "schema": formato}},
            "chat_template_kwargs": {"enable_thinking": False}, "stream": False,
        }
        pedido = urllib.request.Request("http://127.0.0.1:18080/v1/chat/completions",
            data=json.dumps(cuerpo).encode(), headers={"Content-Type": "application/json"})
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--encoder", required=True)
    parser.add_argument("--salida", required=True)
    parser.add_argument("--pasadas", type=int, default=3)
    parser.add_argument("--hilos", type=int, default=4)
    args = parser.parse_args()
    import torch
    from transformers import AutoModel, AutoTokenizer
    torch.set_num_threads(args.hilos)
    inicio = time.perf_counter()
    tok = AutoTokenizer.from_pretrained(args.encoder, local_files_only=True)
    model = AutoModel.from_pretrained(args.encoder, local_files_only=True)
    model.eval()
    encoder_ms = (time.perf_counter() - inicio) * 1000
    tito_real._cargar_encoder = lambda encoder_id, revision: (tok, model, torch)
    tito = tito_real.TitoReal()
    preparacion = tito.preparar()
    if preparacion.get("error"):
        raise RuntimeError(preparacion["error"])
    cliente = ClienteLlama()
    slm = DetectorSLM(cliente, "gemma4:e2b-it-q4_K_M", cargar_prompt("v4"),
                      "rol", 4096, 42, esquema=esquema_de("v4"))
    filtro = TitoViejo20(tito, slm)
    calentamiento = slm.evaluar(casos.con_roles(CASOS[0], casos.cargar_texto(CASOS[0]))[:1])
    if not calentamiento.valida:
        raise RuntimeError(f"falló el calentamiento de Gemma: {calentamiento.error}")
    destino = Path(args.salida)
    destino.mkdir(parents=True, exist_ok=False)
    manifiesto = {"casos": CASOS, "pasadas": args.pasadas, "hilos": args.hilos,
                  "prompt": "v4", "roles": "rol", "sin_indicio": True,
                  "encoder_carga_ms": encoder_ms, "tito_preparacion": preparacion,
                  "gemma_calentamiento_ms": calentamiento.ms,
                  "prompt_sha256": hashlib.sha256(cargar_prompt("v4").encode()).hexdigest(),
                  "ejecutor_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  "textos_sha256": {c: hashlib.sha256((casos.DIR_TEXTO / f"{c}.txt").read_bytes()).hexdigest() for c in CASOS},
                  "sistema": platform.platform(), "python": platform.python_version(),
                  "torch": torch.__version__,
                  "pid": os.getpid(), "recorrido": "todos los turnos; sin detener al primer aviso"}
    (destino / "manifiesto.json").write_text(json.dumps(manifiesto, ensure_ascii=False, indent=2))
    with (destino / "turnos.jsonl").open("w", encoding="utf-8", buffering=1) as archivo:
        for pasada in range(1, args.pasadas + 1):
            for case_id in CASOS:
                ref = casos.cargar_referencia(case_id)
                if ref.get("particion") != "desarrollo" or ref.get("grupo") != "corpus_v2":
                    raise ValueError(f"caso no permitido: {case_id}")
                lineas = casos.con_roles(case_id, casos.cargar_texto(case_id))
                filtro.reiniciar()
                for n in range(1, len(lineas) + 1):
                    inicio = time.perf_counter()
                    respuesta = filtro.evaluar(lineas[:n])
                    total_ms = (time.perf_counter() - inicio) * 1000
                    fila = {"pasada": pasada, "case_id": case_id, "turno": n,
                            "total_ms": total_ms, **dataclasses.asdict(respuesta)}
                    fila["tokens_cache"] = cliente.ultimo_cache if respuesta.consulta in ("slm_valida", "slm_fallo") else None
                    archivo.write(json.dumps(fila, ensure_ascii=False) + "\n")
                    print(pasada, case_id, n, respuesta.consulta, round(total_ms), flush=True)


if __name__ == "__main__":
    main()
