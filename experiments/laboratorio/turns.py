"""Timbre de fin de frase: silencio en la onda.

No es un VAD de tesis. Umbrales de spike, no decisiones congeladas.
"""

import numpy as np


class CortadorTurnos:
    def __init__(
        self, sample_rate: int = 16000, umbral_rms: float = 0.02, silencio_ms: float = 400
    ):
        self.sample_rate = sample_rate
        self.umbral_rms = umbral_rms
        self.silencio_ms = silencio_ms
        self._silencio_acumulado_ms = 0.0
        self._hubo_voz = False

    def agregar(self, chunk: np.ndarray) -> bool:
        """Devuelve True si este pedazo cierra un turno."""
        if len(chunk) == 0:
            return False
        rms = float(np.sqrt(np.mean(chunk.astype(np.float64) ** 2)))
        chunk_ms = 1000.0 * len(chunk) / self.sample_rate
        if rms >= self.umbral_rms:
            self._hubo_voz = True
            self._silencio_acumulado_ms = 0.0
            return False
        self._silencio_acumulado_ms += chunk_ms
        if self._hubo_voz and self._silencio_acumulado_ms >= self.silencio_ms:
            self._silencio_acumulado_ms = 0.0
            self._hubo_voz = False
            return True
        return False
