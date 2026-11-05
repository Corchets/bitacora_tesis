"""¿Ollama reutiliza la transcripción ya procesada entre una línea y la siguiente?

Para un caso largo, en varias líneas n, mide el tiempo de procesar el prompt
(`prompt_eval_duration`) en tres situaciones con el mismo modelo y opciones que correr.py:

- `secuencial`: justo después de evaluar la línea n-1, como en una corrida real.
- `frio`: con una marca distinta al comienzo del mensaje de sistema, que impide
  reutilizar cualquier prefijo: se procesa todo.
- `repetido`: el mismo pedido que `secuencial`, enviado otra vez.

Si `secuencial` tarda como `frio`, la caché no se está aprovechando.

    python analisis/2026-10-21-cache-prefijo/medir_cache.py --modelo qwen3.5:0.8b-q8_0
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
import uuid
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

import casos  # noqa: E402
from cliente_ollama import ClienteOllama  # noqa: E402
from detectores import ESQUEMA_SALIDA, DetectorSLM, armar_mensaje_usuario, cargar_prompt  # noqa: E402


def pedir(cliente, det, sistema, lineas):
    mensajes = [{"role": "system", "content": sistema},
                {"role": "user", "content": armar_mensaje_usuario(lineas, det.hablantes)}]
    r = cliente.chat(det.modelo, mensajes, ESQUEMA_SALIDA, det.opciones(), det.pensar)
    return {
        "tokens_prompt": r.get("prompt_eval_count"),
        "ms_prompt": round(r.get("prompt_eval_duration", 0) / 1e6, 1),
        "tokens_salida": r.get("eval_count"),
        "ms_salida": round(r.get("eval_duration", 0) / 1e6, 1),
        "ms_total": round(r.get("total_duration", 0) / 1e6, 1),
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--modelo", required=True)
    p.add_argument("--caso", default="TR-04-pedido-tras-charla-larga")
    p.add_argument("--lineas", default="5,10,15,20,25")
    p.add_argument("--extra", default="{}", help='opciones de Ollama en JSON, p. ej. {"num_batch": 32}')
    p.add_argument("--salida", type=Path)
    args = p.parse_args()

    cliente = ClienteOllama()
    det = DetectorSLM(cliente=cliente, modelo=args.modelo, prompt=cargar_prompt("tarea"),
                      pensar=False, extra=json.loads(args.extra) or None)
    todas = casos.cargar_texto(args.caso)
    pedir(cliente, det, det.prompt, todas[:1])  # carga el modelo

    filas = []
    for n in [int(x) for x in args.lineas.split(",")]:
        pedir(cliente, det, det.prompt, todas[: n - 1])
        sec = pedir(cliente, det, det.prompt, todas[:n])
        rep = pedir(cliente, det, det.prompt, todas[:n])
        frio = pedir(cliente, det, f"[{uuid.uuid4().hex}]\n" + det.prompt, todas[:n])
        for modo, m in (("secuencial", sec), ("repetido", rep), ("frio", frio)):
            filas.append({"linea": n, "modo": modo, **m})
            print(n, modo, m, flush=True)

    sufijo = "".join(f"_{k}{v}" for k, v in json.loads(args.extra).items())
    salida = args.salida or Path(__file__).parent / f"cache_{args.modelo.replace(':', '_')}{sufijo}.json"
    salida.write_text(json.dumps({
        "modelo": args.modelo,
        "digest": cliente.modelos_instalados().get(args.modelo, ""),
        "ollama": cliente.version(),
        "maquina": platform.platform(),
        "caso": args.caso,
        "opciones": det.opciones(),
        "filas": filas,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print("guardado en", salida)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
