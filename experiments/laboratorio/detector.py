"""Quien lee: LLM/SLM local (clasificador o agente).

No es corpus, no es piloto, no cierra D09. Sustituye al stub TF-IDF
(eliminado 2026-09-25). El puntaje alimenta el camino goteo.

Sin servidor local (`LLM_BASE_URL` vacio): el turno queda sin opinion
(None). El incendio sigue en rules.py.

> Estado: propuesta sin discutir.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Literal

# Candidato de arranque para gama alta (PC de lab). Cuantizar al medir R08.
MODELO_DEFAULT = "meta-llama/Llama-3.2-1B-Instruct"
MODO = Literal["clasificador", "agente", "base"]

# Texto de ESTRATEGIA-MODELOS-NLP-Y-COMPRESION.md / benchmark_nlp.py (PR #40, Luciano), sin cambios.
BASE_CONOCIMIENTO = """[REGLAS OFICIALES DE SEGURIDAD - ARGENTINA]
1. ANSES: Jamás se comunica telefónicamente para ofrecer cobros, bonos ni reparaciones históricas. Todo trámite es presencial o por Mi ANSES.
2. BANCOS / BILLETERAS: Nunca solicitan códigos SMS, token, claves ni CBU por teléfono para frenar compras dudosas.
3. ARCA (AFIP): No notifica deudas, embargos ni intimaciones por llamada telefónica.
4. ACCESO REMOTO: Cualquier pedido de instalar AnyDesk, TeamViewer o QuickSupport es fraude informático."""

DESCRIPCION = (
    "llm-local: SLM via API OpenAI-compatible (LLM_BASE_URL); "
    f"candidato {MODELO_DEFAULT}; modos clasificador|agente|base; "
    "sin server = sin opinion"
)


def _modo() -> MODO:
    m = (os.environ.get("DETECTOR_MODO") or "clasificador").strip().lower()
    if m not in ("clasificador", "agente", "base"):
        raise ValueError(f"DETECTOR_MODO invalido: {m}. Usar clasificador|agente|base")
    return m  # type: ignore[return-value]


class DetectorLlm:
    """Puntaje de riesgo 0..1 a partir del turno (+ historial opcional)."""

    def __init__(
        self,
        modelo: str | None = None,
        modo: MODO | None = None,
        base_url: str | None = None,
        timeout_s: float = 30.0,
    ):
        self.modelo = modelo or os.environ.get("LLM_MODEL", MODELO_DEFAULT)
        self.modo = modo or _modo()
        raw = base_url if base_url is not None else os.environ.get("LLM_BASE_URL", "")
        self.base_url = raw.rstrip("/")
        self.timeout_s = timeout_s

    def puntaje(self, texto: str, historial: list[str] | None = None) -> float | None:
        """Probabilidad de estafa, o None si no hay opinion (sin server / vacio)."""
        if not texto.strip():
            return None
        if not self.base_url:
            return None
        hist = historial or []
        if self.modo == "agente":
            return self._agente(texto, hist)
        if self.modo == "base":
            return self._base(texto, hist)
        return self._clasificador(texto, hist)

    def _clasificador(self, texto: str, historial: list[str]) -> float | None:
        contexto = "\n".join(f"- {t}" for t in historial[-5:])
        prompt = (
            "Sos un detector de vishing en espanol argentino. "
            "Dado el historial reciente y el ultimo turno, devolve SOLO un JSON "
            'con la forma {"riesgo": <float 0..1>} sin texto extra.\n'
            f"Historial:\n{contexto or '(vacio)'}\n"
            f"Ultimo turno: {texto}\n"
        )
        return self._pedir_riesgo(prompt)

    def _agente(self, texto: str, historial: list[str]) -> float | None:
        """Misma salida; checklist de maniobras/pedidos antes del puntaje.

        Variante a medir en #29 / #27. Si no aporta, se documenta el descarte.
        """
        contexto = "\n".join(f"- {t}" for t in historial[-8:])
        prompt = (
            "Sos un agente de deteccion de vishing. Primero revisa mentalmente si "
            "aparecen senales de: AUTHORITY_CLAIM, URGENCY_PRESSURE, THREAT_FEAR, "
            "ISOLATION_SECRECY, REQUEST_AUTH_CODE, REQUEST_SECRET, REQUEST_TRANSFER, "
            "REQUEST_REMOTE_ACCESS u otros pedidos de capa 2. "
            "Despues devolve SOLO JSON "
            '{"riesgo": <float 0..1>, "etiquetas": [<strings>]} '
            "sin texto extra.\n"
            f"Historial:\n{contexto or '(vacio)'}\n"
            f"Ultimo turno: {texto}\n"
        )
        return self._pedir_riesgo(prompt)

    def memoria_mb(self) -> float | None:
        """RAM del modelo cargado segun Ollama (/api/ps). None si el server no es Ollama."""
        raiz = self.base_url.removesuffix("/v1")
        try:
            with urllib.request.urlopen(f"{raiz}/api/ps", timeout=5) as resp:
                modelos = json.loads(resp.read().decode("utf-8")).get("models", [])
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError):
            return None
        tam = [m.get("size", 0) for m in modelos if m.get("name", "").startswith(self.modelo)]
        return round(tam[0] / 2**20, 1) if tam else None

    def _base(self, texto: str, historial: list[str]) -> float | None:
        """Base institucional offline en el sistema, como en PR #40 (benchmark_nlp.py).

        Turnos recortados: con contexto de 1024 tokens, un prompt largo le come el sistema.
        """
        contexto = "\n".join(f"- {t[:300]}" for t in historial[-5:])
        prompt = (
            f"Historial:\n{contexto or '(vacio)'}\n"
            f"Ultimo turno: {texto[:400]}\n"
            "Que tan probable es que esta llamada sea una estafa? "
            "0 = charla normal, 1 = estafa segura. "
            'Devolve SOLO {"riesgo": <float 0..1>}.'
        )
        sistema = (
            "Sos un detector de vishing (estafa telefonica) en espanol argentino. "
            f"{BASE_CONOCIMIENTO} Respondé solo JSON valido."
        )
        return self._pedir_riesgo(prompt, sistema)

    def _pedir_riesgo(self, prompt: str, sistema: str = "Respondé solo JSON valido.") -> float | None:
        url = f"{self.base_url}/chat/completions"
        cuerpo = {
            "model": self.modelo,
            "temperature": 0,
            # Sin esto llama3.2:1b Q4 contesta prosa y el turno queda sin opinion.
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": sistema},
                {"role": "user", "content": prompt},
            ],
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(cuerpo).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError):
            return None
        try:
            content = data["choices"][0]["message"]["content"]
            start, end = content.find("{"), content.rfind("}")
            if start < 0 or end < 0:
                return None
            obj = json.loads(content[start : end + 1])
            r = float(obj["riesgo"])
            return max(0.0, min(1.0, r))
        except (KeyError, TypeError, ValueError, json.JSONDecodeError, IndexError):
            return None


ENCODER_DEFAULT = "pysentimiento/robertuito-base-uncased"


def crear(hilos: int | None = None):
    """DETECTOR=llm (defecto) | encoder | cascada. El encoder entrena su cabeza con SEMILLAS_PATH."""
    tipo = (os.environ.get("DETECTOR") or "llm").strip().lower()
    if tipo == "llm":
        return DetectorLlm()
    if tipo not in ("encoder", "cascada"):
        raise ValueError(f"DETECTOR invalido: {tipo}. Usar llm|encoder|cascada")
    from pathlib import Path

    import detector_encoder

    semillas = os.environ.get("SEMILLAS_PATH") or str(Path(__file__).resolve().parent / "semillas.json")
    enc = detector_encoder.DetectorEncoder(
        os.environ.get("ENCODER_MODEL", ENCODER_DEFAULT), semillas, hilos=hilos
    )
    if tipo == "encoder":
        return enc
    import detector_cascada

    return detector_cascada.DetectorCascada(enc, DetectorLlm())
