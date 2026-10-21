"""Cascada encoder -> SLM (#27 / PR #40): el SLM solo mira la zona gris.

El encoder puntua cada turno. Si cae en [theta_low, theta_high] se le pregunta
al SLM con el historial y su riesgo reemplaza al del encoder; si el SLM no
contesta, queda el del encoder. 0.35 / 0.75 son el ejemplo de
ESTRATEGIA-MODELOS-NLP-Y-COMPRESION.md (PR #40), no umbrales calibrados.

> Estado: propuesta sin discutir. No cierra D09.
"""

from __future__ import annotations

import time

THETA_LOW = 0.35
THETA_HIGH = 0.75


class DetectorCascada:
    def __init__(self, encoder, slm, theta_low: float = THETA_LOW, theta_high: float = THETA_HIGH):
        self.encoder = encoder
        self.slm = slm
        self.theta_low = theta_low
        self.theta_high = theta_high
        self.n_turnos = 0
        self.n_zona_gris = 0
        self.n_slm_ok = 0
        self.ms_encoder: list[float] = []
        self.ms_slm: list[float] = []

    def puntaje(self, texto: str, historial: list[str] | None = None) -> float | None:
        t0 = time.perf_counter()
        p = self.encoder.puntaje(texto)
        if p is None:
            return None
        self.ms_encoder.append((time.perf_counter() - t0) * 1000)
        self.n_turnos += 1
        if not (self.theta_low <= p <= self.theta_high):
            return p
        self.n_zona_gris += 1
        t0 = time.perf_counter()
        r = self.slm.puntaje(texto, historial)
        self.ms_slm.append((time.perf_counter() - t0) * 1000)
        if r is None:
            return p
        self.n_slm_ok += 1
        return r

    def stats(self) -> dict:
        def p50(xs: list[float]) -> float | None:
            return round(sorted(xs)[len(xs) // 2], 1) if xs else None

        return {
            "theta_low": self.theta_low,
            "theta_high": self.theta_high,
            "n_turnos": self.n_turnos,
            "n_zona_gris": self.n_zona_gris,
            "n_slm_ok": self.n_slm_ok,
            "ms_encoder_p50": p50(self.ms_encoder),
            "ms_slm_p50": p50(self.ms_slm),
            "slm_mem_mb": self.slm.memoria_mb() if hasattr(self.slm, "memoria_mb") else None,
        }
