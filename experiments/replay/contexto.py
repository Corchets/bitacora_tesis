"""Gestión de contexto incremental para el ensayo de replay (#28).

Mantiene el estado de las llamadas a partir de un flujo de actualizaciones ASR:
- Los segmentos parciales reemplazan el borrador previo del segmento abierto.
- Los segmentos finales se acumulan como líneas cerradas de diálogo.
- Separación estricta entre llamadas (reinicio de contexto y cola secuencial).
- Garantía de no filtración de información futura (solo lo disponible hasta disponible_s).
- Modelo de cola secuencial del detector: evaluación n inicia en max(disponible_s_n, fin_eval_{n-1}).

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

    Mantiene las líneas cerradas (finales), los borradores abiertos (parciales),
    y el estado temporal de la cola secuencial de evaluación del detector.
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
    aviso_inicio_eval_s: float | None = None
    aviso_fin_eval_s: float | None = None
    aviso_espera_cola_ms: float | None = None
    ultimo_fin_eval_s: float | None = None
    max_espera_cola_ms: float = 0.0
    hubo_atraso: bool = False
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

    def registrar_evaluacion(
        self,
        act: Actualizacion,
        respuesta: Any,
        lineas_disponibles: tuple[Linea, ...],
    ) -> tuple[float | None, float | None, float | None, bool, float | None]:
        """Calcula los tiempos de evaluación secuencial con cola y evalúa el aviso único.

        En el reloj de audio:
            inicio_eval_n = max(disponible_s_n, fin_eval_{n-1})
            fin_eval_n = inicio_eval_n + ms_n/1000
            espera_cola_ms = (inicio_eval_n - disponible_s_n) * 1000
            T_A = fin_eval_n (de la evaluación que emite el aviso)

        En modo texto (sin audio):
            inicio_eval_s = None, fin_eval_s = None, espera_cola_ms = None, T_A = None

        Devuelve:
            (inicio_eval_s, fin_eval_s, espera_cola_ms, es_aviso, t_a)
        """
        if act.disponible_s is not None:
            ms = respuesta.ms if respuesta and respuesta.ms is not None else 0.0
            if self.ultimo_fin_eval_s is None:
                inicio_eval_s = act.disponible_s
            else:
                inicio_eval_s = max(act.disponible_s, self.ultimo_fin_eval_s)
            fin_eval_s = inicio_eval_s + (ms / 1000.0)
            espera_cola_ms = round((inicio_eval_s - act.disponible_s) * 1000.0, 4)
            self.ultimo_fin_eval_s = fin_eval_s
            if espera_cola_ms > 0.001:
                self.hubo_atraso = True
            self.max_espera_cola_ms = max(self.max_espera_cola_ms, espera_cola_ms)
        else:
            inicio_eval_s = None
            fin_eval_s = None
            espera_cola_ms = None

        if not respuesta.valida:
            self.fallos += 1
            if getattr(respuesta, "error", None):
                self.errores.append(str(respuesta.error))
            return inicio_eval_s, fin_eval_s, espera_cola_ms, False, None

        if respuesta.alerta_sugerida:
            if not self.aviso_emitido:
                self.aviso_emitido = True
                self.aviso_n = act.n
                self.aviso_actualizacion = act
                self.aviso_respuesta = respuesta
                self.aviso_lineas = lineas_disponibles
                self.aviso_inicio_eval_s = inicio_eval_s
                self.aviso_fin_eval_s = fin_eval_s
                self.aviso_espera_cola_ms = espera_cola_ms
                self.aviso_t_a = fin_eval_s  # T_A = fin_eval
                return inicio_eval_s, fin_eval_s, espera_cola_ms, True, fin_eval_s

        return inicio_eval_s, fin_eval_s, espera_cola_ms, False, None

    def evaluar_aviso(
        self,
        act: Actualizacion,
        respuesta: Any,
        lineas_disponibles: tuple[Linea, ...],
    ) -> tuple[bool, float | None]:
        """Compatibilidad con interfaz previa."""
        _, _, _, es_aviso, t_a = self.registrar_evaluacion(act, respuesta, lineas_disponibles)
        return es_aviso, t_a
