"""Gestión de contexto incremental para el ensayo de replay (#28).

Mantiene el estado de las llamadas a partir de un flujo de actualizaciones ASR:
- Los segmentos parciales reemplazan el borrador previo del segmento abierto.
- Los segmentos finales se acumulan como líneas cerradas de diálogo.
- Separación estricta entre llamadas (reinicio de contexto).
- Garantía de no filtración de información futura (solo lo disponible hasta disponible_s).

Reutiliza tipos de `experiments/slm-directo/casos.py`.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Importar tipos de slm-directo
DIR_REPLAY = Path(__file__).resolve().parent
DIR_SLM_DIRECTO = DIR_REPLAY.parent / "slm-directo"
if str(DIR_SLM_DIRECTO) not in sys.path:
    sys.path.insert(0, str(DIR_SLM_DIRECTO))

from casos import Linea


@dataclass(frozen=True)
class Actualizacion:
    """Una actualización incremental de transcripción (contrato JSONL de ASR o línea de texto)."""

    llamada_id: str
    n: int
    tipo: str  # "parcial" o "final"
    segmento: int
    texto: str
    inicio_audio_s: float | None = None
    fin_audio_s: float | None = None
    disponible_s: float | None = None
    proceso_ms: float | None = None
    canal: str | None = None  # "A", "B" o None


@dataclass
class ContextoLlamada:
    """Estado acumulado de UNA llamada en curso.

    Mantiene las líneas cerradas (finales) y los borradores abiertos (parciales).
    Aplica la política de aviso único: solo el primer `alerta_sugerida=True` válido
    dispara la emisión de alerta.
    """

    llamada_id: str
    cerrados: list[Linea] = field(default_factory=list)
    parciales: dict[int, Linea] = field(default_factory=dict)
    aviso_emitido: bool = False
    aviso_n: int | None = None
    aviso_t_a: float | None = None
    aviso_actualizacion: Actualizacion | None = None
    aviso_respuesta: Any | None = None
    aviso_lineas: tuple[Linea, ...] | None = None
    fallos: int = 0
    errores: list[str] = field(default_factory=list)

    def aplicar(self, act: Actualizacion, hablantes_modo: str) -> tuple[Linea, ...]:
        """Aplica la actualización al contexto incremental y devuelve la foto actual de líneas.

        - Un parcial reemplaza el borrador del segmento abierto sin duplicar.
        - Un final cierra el segmento y lo acumula como línea fija.
        """
        if act.canal in ("A", "B"):
            hablante = act.canal
        else:
            hablante = ""

        linea = Linea(hablante=hablante, texto=act.texto)

        if act.tipo == "parcial":
            self.parciales[act.segmento] = linea
        elif act.tipo == "final":
            self.parciales.pop(act.segmento, None)
            self.cerrados.append(linea)

        # Foto actual de líneas disponibles: cerradas + parciales abiertas ordenadas por segmento
        lineas_parciales = [self.parciales[s] for s in sorted(self.parciales)]
        return tuple(self.cerrados + lineas_parciales)

    def evaluar_aviso(
        self,
        act: Actualizacion,
        respuesta: Any,
        lineas_disponibles: tuple[Linea, ...],
    ) -> tuple[bool, float | None]:
        """Aplica la política de aviso único.

        Devuelve (es_aviso, t_a).
        - Solo la primera respuesta válida con alerta_sugerida=True produce el aviso.
        - Respuestas inválidas o fallos se contabilizan como fallos y no producen aviso.
        - En modo audio, T_A = disponible_s + (detector_ms / 1000.0).
        - En modo texto (sin audio), t_a es None.
        """
        if not respuesta.valida:
            self.fallos += 1
            if getattr(respuesta, "error", None):
                self.errores.append(str(respuesta.error))
            return False, None

        if respuesta.alerta_sugerida:
            if not self.aviso_emitido:
                self.aviso_emitido = True
                self.aviso_n = act.n
                self.aviso_actualizacion = act
                self.aviso_respuesta = respuesta
                self.aviso_lineas = lineas_disponibles

                if act.disponible_s is not None:
                    ms = respuesta.ms if respuesta.ms is not None else 0.0
                    t_a = act.disponible_s + (ms / 1000.0)
                    self.aviso_t_a = t_a
                else:
                    t_a = None
                    self.aviso_t_a = None

                return True, t_a

        return False, None
