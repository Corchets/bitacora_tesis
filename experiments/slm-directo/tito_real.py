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
        self.encoder = None  # se carga con preparar(), fuera de las actualizaciones
        self.preparacion: dict | None = None  # costos de preparar(), sin doble conteo

    def contar_truncamientos(self, tokenizer, textos: list[str]) -> int:
        """Cuántos textos superarían el límite sin truncar (se registran, no se recortan en silencio)."""
        reales = tokenizer(textos, padding=False, truncation=False)["input_ids"]
        return sum(1 for ids in reales if len(ids) > self.limite)

    def _asegurar_encoder(self):
        """Carga el encoder una vez por proceso (caché en `_ENCODERS`).

        Devuelve `(tokenizer, modelo, torch, desde_cache)`. Las subclases de
        prueba pueden sobreescribirlo para no descargar modelos.
        """
        enc_id = self.arte["encoder"]["id"]
        rev = self.arte["encoder"]["revision"]
        desde_cache = (enc_id, rev) in _ENCODERS
        tokenizer, modelo, torch = _cargar_encoder(enc_id, rev)
        if self.encoder is None:
            self.encoder = modelo
        return tokenizer, modelo, torch, desde_cache

    def preparar(self, texto_ejemplo: str = "hola mundo") -> dict:
        """Preparación explícita una vez por proceso, fuera de las actualizaciones.

        Carga el encoder y corre un calentamiento (una incrustación del texto
        de ejemplo). Devuelve costos separados sin doble conteo con `puntuar`:
        `encoder_ms` (carga del encoder, ~0 si ya estaba en caché) y
        `calentamiento_ms` (una sola pasada de calentamiento). Ante un fallo
        devuelve `error` sin levantar: el flujo deriva por fail-open y cada
        `puntuar` registrará su propia causa.
        """
        inicio_enc = time.perf_counter()
        try:
            _, _, _, desde_cache = self._asegurar_encoder()
        except Exception as e:  # noqa: BLE001 - se registra, no se interrumpe
            informe = {"encoder_ms": round((time.perf_counter() - inicio_enc) * 1000, 1),
                       "encoder_desde_cache": False, "calentamiento_ms": None,
                       "error": f"tito_preparar_error: {type(e).__name__}: {e}",
                       "unidad": "ms"}
            self.preparacion = informe
            return informe
        encoder_ms = round((time.perf_counter() - inicio_enc) * 1000, 1)
        inicio_cal = time.perf_counter()
        try:
            self._embed([texto_ejemplo])
        except Exception as e:  # noqa: BLE001 - se registra, no se interrumpe
            informe = {"encoder_ms": encoder_ms, "encoder_desde_cache": desde_cache,
                       "calentamiento_ms": round((time.perf_counter() - inicio_cal) * 1000, 1),
                       "error": f"tito_calentar_error: {type(e).__name__}: {e}",
                       "unidad": "ms"}
            self.preparacion = informe
            return informe
        informe = {"encoder_ms": encoder_ms, "encoder_desde_cache": desde_cache,
                   "calentamiento_ms": round((time.perf_counter() - inicio_cal) * 1000, 1),
                   "error": "", "unidad": "ms"}
        self.preparacion = informe
        return informe

    def _embed(self, textos: list[str]) -> list[list[float]]:
        tokenizer, modelo, torch, _ = self._asegurar_encoder()
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


def preparar_tito_real(artefacto: str | Path = ARTEFACTO_POR_DEFECTO) -> tuple[TitoReal, dict]:
    """Preparación reutilizable de Tito real, una vez por proceso (#97).

    Devuelve `(tito, informe)`: el informe separa `artefacto_ms` (lectura y
    validación del JSON, ~0 si ya estaba en caché) de lo que mide
    `TitoReal.preparar` (`encoder_ms`, `calentamiento_ms`, `error`). Nada de
    esto se cuenta en las actualizaciones: `puntuar` solo mide su propia
    pasada. Un `error` no vacío no levanta: la corrida sigue y cada `puntuar`
    fallará por fail-open con su causa.
    """
    clave = str(Path(artefacto).resolve())
    artefacto_desde_cache = clave in _ARTEFACTOS
    inicio = time.perf_counter()
    tito = TitoReal(artefacto)
    artefacto_ms = round((time.perf_counter() - inicio) * 1000, 1)
    informe = tito.preparar()
    informe = {"artefacto_ms": artefacto_ms,
               "artefacto_desde_cache": artefacto_desde_cache,
               **informe}
    return tito, informe
