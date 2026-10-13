"""Cliente mínimo de la API local de Ollama (https://github.com/ollama/ollama/blob/main/docs/api.md).

Solo usa la biblioteca estándar. Requiere Ollama 0.5 o posterior, que acepta un
esquema JSON en el campo `format` para forzar la forma de la respuesta.
"""

from __future__ import annotations

import json
import socket
import urllib.error
import urllib.request

URL_POR_DEFECTO = "http://localhost:11434"


class ErrorOllama(Exception):
    """Falla de comunicación con Ollama: servidor caído, timeout o error HTTP."""


class ClienteOllama:
    def __init__(self, url: str = URL_POR_DEFECTO, timeout_s: float = 120.0):
        self.url = url.rstrip("/")
        self.timeout_s = timeout_s

    def _pedir(self, ruta: str, cuerpo: dict | None = None) -> dict:
        datos = None if cuerpo is None else json.dumps(cuerpo).encode("utf-8")
        pedido = urllib.request.Request(
            self.url + ruta,
            data=datos,
            headers={"Content-Type": "application/json"},
            method="GET" if cuerpo is None else "POST",
        )
        try:
            with urllib.request.urlopen(pedido, timeout=self.timeout_s) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            detalle = e.read().decode("utf-8", errors="replace")[:300]
            raise ErrorOllama(f"http_{e.code}: {detalle}") from e
        except (socket.timeout, TimeoutError) as e:
            raise ErrorOllama("timeout") from e
        except urllib.error.URLError as e:
            if isinstance(e.reason, (socket.timeout, TimeoutError)):
                raise ErrorOllama("timeout") from e
            raise ErrorOllama(f"sin_conexion: {e.reason}") from e

    def chat(
        self, modelo: str, mensajes: list[dict], formato: dict, opciones: dict, pensar: bool | None = None
    ) -> dict:
        """Una respuesta completa, sin streaming. Devuelve el JSON de Ollama tal cual.

        `pensar=False` desactiva el razonamiento previo de los modelos que lo traen
        activado (p. ej. qwen3.5); `None` no envía el campo, para modelos sin esa opción.
        """
        cuerpo = {
            "model": modelo,
            "messages": mensajes,
            "format": formato,
            "options": opciones,
            "stream": False,
            "keep_alive": "10m",
        }
        if pensar is not None:
            cuerpo["think"] = pensar
        return self._pedir("/api/chat", cuerpo)

    def version(self) -> str:
        return self._pedir("/api/version").get("version", "desconocida")

    def modelos_instalados(self) -> dict[str, str]:
        """Nombre del modelo → digest, según `ollama list`."""
        return {m["name"]: m.get("digest", "") for m in self._pedir("/api/tags").get("models", [])}

    def memoria_cargada(self, modelo: str) -> dict | None:
        """Lo que Ollama informa del modelo en memoria (pesos + caché de contexto)."""
        for m in self._pedir("/api/ps").get("models", []):
            if m.get("name") == modelo or m.get("model") == modelo:
                return {"size_bytes": m.get("size"), "size_vram_bytes": m.get("size_vram")}
        return None
