"""SLM falso para la demo Tito→SLM simulada (#69).

Imita la API mínima de Ollama que usa el ensayo (`/api/version`, `/api/tags`,
`/api/ps`, `/api/chat`) con respuestas deterministas: avisa solo si la
transcripción disponible contiene un pedido explícito de código. No es un
modelo: sirve para demostrar el recorrido Tito→SLM de punta a punta y
regenerar su traza y reporte sin descargar nada.

Uso (desde experiments/slm-directo):
    python slm_falso.py --puerto 11439 &
    python correr.py --modelos falso-demo:1b --url http://127.0.0.1:11439 \\
        --casos SC-WA-CODE-01-e01,LG-WA-CONSULTA-01-e01 \\
        --filtro-tito --tito-puntajes "4=0.9" --etiqueta demo-tito-slm-simulado
    python resumen.py corridas/*_demo-tito-slm-simulado
"""

from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

MODELO = "falso-demo:1b"
DIGEST = "falso69-demo-sin-modelo-real"
VERSION = "falso-demo-69"


class Manejador(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _responder(self, cuerpo: dict, codigo: int = 200):
        datos = json.dumps(cuerpo).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(datos)))
        self.end_headers()
        self.wfile.write(datos)

    def do_GET(self):
        if self.path == "/api/version":
            self._responder({"version": VERSION})
        elif self.path == "/api/tags":
            self._responder({"models": [{"name": MODELO, "digest": DIGEST}]})
        elif self.path == "/api/ps":
            self._responder({"models": []})
        else:
            self._responder({}, 404)

    def do_POST(self):
        if self.path != "/api/chat":
            self._responder({}, 404)
            return
        pedido = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        usuario = pedido["messages"][-1]["content"]
        formato = pedido.get("format", {})
        if "ok" in formato.get("properties", {}):  # calentamiento de correr.py
            contenido = json.dumps({"ok": True})
        elif "Decime el código" in usuario:
            contenido = json.dumps({
                "riesgo": 0.95,
                "alerta_sugerida": True,
                "motivo": "Te piden un código que da acceso a tu cuenta",
                "evidencia": "Decime el código de activación que recibiste por SMS.",
            })
        else:
            contenido = json.dumps({"riesgo": 0.1, "alerta_sugerida": False, "motivo": "", "evidencia": ""})
        self._responder({
            "message": {"role": "assistant", "content": contenido},
            "prompt_eval_count": 100,
            "eval_count": 10,
        })


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--puerto", type=int, default=11439)
    args = p.parse_args(argv)
    servidor = HTTPServer(("127.0.0.1", args.puerto), Manejador)
    print(f"SLM falso en http://127.0.0.1:{args.puerto} (modelo {MODELO}). Ctrl+C para cortar.")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
