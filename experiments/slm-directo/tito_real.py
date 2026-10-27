"""Tito real para el recorrido incremental (#70, parte de #68).

RoBERTuito congelado con promedio enmascarado (límite 128 tokens) más la única
regresión logística ajustada por `entrenar_tito.py` (seed 42, 5.520 textos).
Cargar el artefacto no reentrena: los pesos se leen una vez por proceso y se
reutilizan para todas las conversaciones y SLM. `puntuar` es sin estado: una
llamada no influye en la siguiente (la anti-contaminación entre llamadas la
garantiza `FlujoTitoSLM.reiniciar`, que `correr.procesar_caso` llama por caso).

Interfaz compatible con `TitoGuion`: `puntuar(n, texto)` devuelve
`(puntaje o None, error o "", ms)`. Un fallo técnico devuelve `(None, error, ms)`
sin fabricar puntaje, igual que el simulado.
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path

from filtro_tito import UMBRAL_TITO  # noqa: F401  (el umbral vive en el flujo, no acá)

AQUI = Path(__file__).resolve().parent
ARTEFACTO_POR_DEFECTO = AQUI / "tito_logreg.json"

_ARTEFACTOS: dict[str, dict] = {}  # ruta resuelta -> artefacto (carga única)
_ENCODERS: dict[tuple[str, str], tuple] = {}  # (id, revision) -> (tokenizer, modelo)


def cargar_artefacto(ruta: str | Path = ARTEFACTO_POR_DEFECTO) -> dict:
    """Lee y valida el artefacto una vez por proceso; no ajusta nada."""
    clave = str(Path(ruta).resolve())
    if clave not in _ARTEFACTOS:
        arte = json.loads(Path(clave).read_text(encoding="utf-8"))
        if arte.get("formato") != "tito-logreg-v1":
            raise ValueError(f"artefacto desconocido en {clave}: {arte.get('formato')!r}.")
        if arte["config_regresion"].get("semilla") != 42:
            raise ValueError("el artefacto no es el ajuste único con seed 42.")
        coef = arte["pesos"]["coef"]
        if len(coef) != arte["encoder"]["hidden"]:
            raise ValueError("pesos y dimensión del encoder no coinciden.")
        _ARTEFACTOS[clave] = arte
    return _ARTEFACTOS[clave]


def _cargar_encoder(encoder_id: str, revision: str):
    clave = (encoder_id, revision)
    if clave not in _ENCODERS:
        import torch
        from transformers import AutoModel, AutoTokenizer
        from huggingface_hub import snapshot_download
        snap = Path(snapshot_download(encoder_id, revision=revision))
        tokenizer = AutoTokenizer.from_pretrained(str(snap))
        modelo = AutoModel.from_pretrained(str(snap))
        for p in modelo.parameters():
            p.requires_grad_(False)
        modelo.eval()
        _ENCODERS[clave] = (tokenizer, modelo, torch)
    return _ENCODERS[clave]


class TitoReal:
    """Filtro Tito con encoder real. Sin estado entre llamadas."""

    nombre = "tito-real"

    def __init__(self, artefacto: str | Path = ARTEFACTO_POR_DEFECTO) -> None:
        self.arte = cargar_artefacto(artefacto)
        self.limite = int(self.arte["tokenizador"]["limite_tokens"])
        self.coef = self.arte["pesos"]["coef"]
        self.intercepto = float(self.arte["pesos"]["intercepto"])
        self.consultas: list[tuple[int, str]] = []
        self.truncamientos = 0
        self.encoder = None  # se carga vago en el primer puntaje (mide aparte)

    def contar_truncamientos(self, tokenizer, textos: list[str]) -> int:
        """Cuántos textos superarían el límite sin truncar (se registran, no se recortan en silencio)."""
        reales = tokenizer(textos, padding=False, truncation=False)["input_ids"]
        return sum(1 for ids in reales if len(ids) > self.limite)

    def _embed(self, textos: list[str]) -> list[list[float]]:
        enc_id = self.arte["encoder"]["id"]
        rev = self.arte["encoder"]["revision"]
        tokenizer, modelo, torch = _cargar_encoder(enc_id, rev)
        if self.encoder is None:
            self.encoder = modelo
        vectors: list[list[float]] = []
        with torch.no_grad():
            for i in range(0, len(textos), 32):
                lote = textos[i:i + 32]
                self.truncamientos += self.contar_truncamientos(tokenizer, lote)
                tok = tokenizer(lote, padding=True, truncation=True,
                                max_length=self.limite, return_tensors="pt")
                h = modelo(**tok).last_hidden_state
                mask = tok["attention_mask"].unsqueeze(-1).float()
                medios = (h * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1.0)
                vectors.extend(medios.tolist())
        return vectors

    def puntuar(self, n: int, texto: str) -> tuple[float | None, str, float]:
        """(puntaje, "", ms). Fallo técnico -> (None, error, ms) sin puntaje."""
        self.consultas.append((n, texto))
        inicio = time.perf_counter()
        try:
            (vec,) = self._embed([texto])
        except Exception as e:  # noqa: BLE001 - el flujo lo registra como fallo técnico
            return None, f"tito_error: {type(e).__name__}", (time.perf_counter() - inicio) * 1000
        z = sum(c * x for c, x in zip(self.coef, vec)) + self.intercepto
        puntaje = 1.0 / (1.0 + math.exp(-z))
        return puntaje, "", (time.perf_counter() - inicio) * 1000
