"""Estado de UNA llamada en vivo: audio por canal, ASR, contexto y aviso único (frente 1).

No sabe nada de la red: `servidor.py` le entrega bloques de audio con su rol y le pide
fotos para el detector. Así se puede probar sin micrófonos ni modelos (tests/).

Reloj de la llamada: segundos desde que llegó el primer bloque de audio de cualquier
canal. Cada canal ubica su audio en ese reloj según cuándo llegó su primer bloque; desde
ahí cuenta muestras. Así los dos canales quedan alineados aunque vengan de notebooks
distintas, y el estéreo guardado tiene el mismo reloj que `actualizaciones.jsonl`.

> Estado: propuesta sin discutir. Spike del frente 1; no cierra D08 ni D09.
"""

from __future__ import annotations

import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import numpy as np

DIR_VOIP = Path(__file__).resolve().parent
for _dir in (DIR_VOIP.parent / "asr-local", DIR_VOIP.parent / "replay", DIR_VOIP.parent / "slm-directo"):
    if str(_dir) not in sys.path:
        sys.path.insert(0, str(_dir))

from contexto import Actualizacion, ContextoLlamada
from motores import MotorASR

SAMPLE_RATE = 16000
ROLES = ("protegida", "otra")
# Lo que se manda al ASR y se guarda: PCM 16 bits mono a 16 kHz.
ESCALA_INT16 = 32768.0


@dataclass
class Canal:
    rol: str
    motor: MotorASR
    letra: str | None = None  # A = quien habló primero, como en los casos de texto
    inicio_s: float | None = None
    muestras: int = 0
    ultima_voz_s: float | None = None  # fin del último bloque con voz (RMS sobre el umbral)
    bloques: list[np.ndarray] = field(default_factory=list)
    # llegada - fin del bloque en el reloj de la llamada: si crece, el canal se atrasa.
    desfases_s: list[float] = field(default_factory=list)
    # disponible - fin del audio: lo que tarda un parcial en aparecer.
    retrasos_parcial_s: list[float] = field(default_factory=list)
    # disponible - fin de la voz: lo que tarda una frase cerrada desde que la persona se calla.
    retrasos_final_s: list[float] = field(default_factory=list)

    def fin_s(self) -> float:
        return (self.inicio_s or 0.0) + self.muestras / SAMPLE_RATE


@dataclass
class Evaluacion:
    n: int  # última actualización incluida en la foto
    saltadas: int  # disparos que llegaron mientras el detector estaba ocupado y no se evaluaron solos
    inicio_s: float
    fin_s: float
    respuesta: Any
    aviso: bool
    fin_voz_s: float | None  # fin de la voz de la última línea cerrada de la foto


class Llamada:
    """Se crea antes de la llamada (carga un ASR por rol) y empieza con `abrir`."""

    def __init__(
        self,
        crear_motor: Callable[[], MotorASR],
        disparo: str = "final",
        ahora: Callable[[], float] = time.monotonic,
    ) -> None:
        if disparo not in ("final", "parcial"):
            raise ValueError(f"disparo desconocido {disparo!r}; opciones: final, parcial")
        self.disparo = disparo
        self._ahora = ahora
        self.canales: dict[str, Canal] = {}
        for rol in ROLES:
            motor = crear_motor()
            motor.inicializar()
            self.canales[rol] = Canal(rol=rol, motor=motor)
        self.meta_asr = self.canales[ROLES[0]].motor.metadatos()
        self.umbral_voz = getattr(self.canales[ROLES[0]].motor, "umbral_rms_silencio", 0.005)
        self.llamada_id = ""
        self.dir_salida: Path | None = None
        self.t0: float | None = None
        self.foto: tuple = ()
        self.n = 0
        self.disparos = 0
        self.ultimo_fin_voz_s: float | None = None
        self.segmentos: dict[tuple[str, int], int] = {}  # (rol, segmento del motor) -> segmento de la llamada
        self.evaluaciones: list[Evaluacion] = []
        self.aviso: Evaluacion | None = None

    def abrir(self, llamada_id: str, dir_salida: Path) -> None:
        self.llamada_id = llamada_id
        self.dir_salida = dir_salida
        self.contexto = ContextoLlamada(llamada_id=llamada_id)
        dir_salida.mkdir(parents=True, exist_ok=True)
        self._jsonl = open(dir_salida / "actualizaciones.jsonl", "w", encoding="utf-8")
        self._detector = open(dir_salida / "detector.jsonl", "w", encoding="utf-8")
        self._escribir(self._jsonl, {"meta": {
            **self.meta_asr, "modo": "en_vivo", "sample_rate": SAMPLE_RATE,
            "roles": "cada línea trae `rol`: protegida (micrófono de la persona a proteger) u otra",
        }})

    def reloj(self) -> float:
        return 0.0 if self.t0 is None else self._ahora() - self.t0

    def recibir(self, rol: str, pcm: bytes, *, llegada: float | None = None) -> list[dict]:
        """Procesa un bloque PCM16 de un canal. Devuelve las actualizaciones nuevas (contrato ASR)."""
        if rol not in ROLES:
            raise ValueError(f"rol desconocido {rol!r}; opciones: {ROLES}")
        llegada = self._ahora() if llegada is None else llegada
        muestras = np.frombuffer(pcm, dtype=np.int16)
        dur_s = len(muestras) / SAMPLE_RATE
        if self.t0 is None:
            # El primer bloque se capturó durante los dur_s previos a su llegada.
            self.t0 = llegada - dur_s
        canal = self.canales[rol]
        if canal.inicio_s is None:
            canal.inicio_s = max(0.0, llegada - self.t0 - dur_s)
        inicio_bloque = canal.fin_s()
        canal.muestras += len(muestras)
        canal.bloques.append(muestras.copy())
        fin_bloque = canal.fin_s()
        canal.desfases_s.append(llegada - self.t0 - fin_bloque)
        flotante = muestras.astype(np.float32) / ESCALA_INT16
        if len(flotante) and float(np.sqrt(np.mean(flotante**2))) >= self.umbral_voz:
            canal.ultima_voz_s = fin_bloque
        eventos = canal.motor.procesar_bloque(flotante, inicio_bloque, fin_bloque)
        # Zipformer a veces cierra un segmento con solo un punto: no es una línea.
        return [self._registrar(canal, e) for e in eventos if any(c.isalnum() for c in e.texto)]

    def _registrar(self, canal: Canal, evento) -> dict:
        if canal.letra is None:
            canal.letra = "AB"[sum(c.letra is not None for c in self.canales.values())]
        clave = (canal.rol, evento.segmento)
        if clave not in self.segmentos:
            self.segmentos[clave] = len(self.segmentos) + 1
        self.n += 1
        disponible = max(self.reloj(), evento.fin_audio_s)
        act = {
            "llamada_id": self.llamada_id,
            "n": self.n,
            "tipo": evento.tipo,
            "segmento": self.segmentos[clave],
            "texto": evento.texto,
            "inicio_audio_s": round(evento.inicio_audio_s, 3),
            "fin_audio_s": round(evento.fin_audio_s, 3),
            "disponible_s": round(disponible, 3),
            "proceso_ms": evento.proceso_ms,
            "canal": canal.letra,
            "rol": canal.rol,
        }
        if evento.tipo == "final":
            fin_voz = min(canal.ultima_voz_s or evento.fin_audio_s, evento.fin_audio_s)
            act["fin_voz_s"] = round(fin_voz, 3)
            canal.retrasos_final_s.append(disponible - fin_voz)
            self.ultimo_fin_voz_s = fin_voz
        else:
            canal.retrasos_parcial_s.append(disponible - evento.fin_audio_s)
        self._escribir(self._jsonl, act)
        campos = {k: v for k, v in act.items() if k not in ("rol", "fin_voz_s")}
        self.foto = self.contexto.aplicar(Actualizacion(**campos), "ab")
        return act

    def marcar_disparo(self, act: dict) -> bool:
        """True si esta actualización pide evaluar (según --disparo y si ya hubo aviso)."""
        if self.aviso is None and (self.disparo == "parcial" or act["tipo"] == "final"):
            self.disparos += 1
            return True
        return False

    def tomar_foto(self) -> tuple[int, tuple, int]:
        """Lo último disponible para el detector y cuántos disparos junta esta evaluación."""
        disparos, self.disparos = self.disparos, 0
        return self.n, self.foto, disparos

    def registrar_evaluacion(self, n: int, disparos: int, respuesta: Any, inicio_s: float, fin_s: float) -> Evaluacion:
        """Aviso único: la primera respuesta válida con alerta. T_A = fin de esa evaluación."""
        aviso = self.aviso is None and respuesta.valida and bool(respuesta.alerta_sugerida)
        ev = Evaluacion(
            n=n,
            saltadas=max(0, disparos - 1),
            inicio_s=inicio_s,
            fin_s=fin_s,
            respuesta=respuesta,
            aviso=aviso,
            fin_voz_s=self.ultimo_fin_voz_s,
        )
        self.evaluaciones.append(ev)
        if aviso:
            self.aviso = ev
        self._escribir(self._detector, self.evento_detector(ev))
        return ev

    def evento_detector(self, ev: Evaluacion) -> dict:
        r = ev.respuesta
        return {
            "n": ev.n,
            "saltadas": ev.saltadas,
            "inicio_eval_s": round(ev.inicio_s, 3),
            "fin_eval_s": round(ev.fin_s, 3),
            "ms_detector": None if r.ms is None else round(r.ms, 1),
            "valida": r.valida,
            "error": r.error,
            "riesgo": r.riesgo,
            "alerta_sugerida": r.alerta_sugerida,
            "motivo": r.motivo,
            "evidencia": r.evidencia,
            "aviso": ev.aviso,
            "t_a": round(ev.fin_s, 3) if ev.aviso else None,
            "fin_voz_s": None if ev.fin_voz_s is None else round(ev.fin_voz_s, 3),
        }

    def cerrar(self, manifiesto_extra: dict | None = None) -> list[dict]:
        """Vacía el ASR de cada canal, guarda el estéreo y el manifiesto. Devuelve las últimas actualizaciones."""
        ultimas = []
        for canal in self.canales.values():
            if canal.inicio_s is None:
                continue
            for e in canal.motor.vaciar_final(canal.fin_s()):
                if any(c.isalnum() for c in e.texto):
                    ultimas.append(self._registrar(canal, e))
        self._jsonl.close()
        self._detector.close()
        self._guardar_estereo()
        manifiesto = {
            "llamada_id": self.llamada_id,
            "asr": self.meta_asr,
            "disparo": self.disparo,
            "politica": "aviso_unico_primer_true_valido; el detector evalúa siempre la foto más reciente",
            "canales": {c.rol: self._resumen_canal(c) for c in self.canales.values() if c.inicio_s is not None},
            "estereo": "estereo.wav (izquierdo = protegida, derecho = otra; fuera de Git)",
            "detector": self._resumen_detector(),
            **(manifiesto_extra or {}),
        }
        (self.dir_salida / "manifiesto.json").write_text(
            json.dumps(manifiesto, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return ultimas

    def _guardar_estereo(self) -> None:
        if self.t0 is None:
            return
        import soundfile as sf

        total = max(int(round(c.fin_s() * SAMPLE_RATE)) for c in self.canales.values() if c.inicio_s is not None)
        estereo = np.zeros((total, 2), dtype=np.int16)
        for columna, rol in enumerate(ROLES):
            canal = self.canales.get(rol)
            if canal is None or not canal.bloques:
                continue
            audio = np.concatenate(canal.bloques)
            desde = int(round((canal.inicio_s or 0.0) * SAMPLE_RATE))
            audio = audio[: total - desde]
            estereo[desde : desde + len(audio), columna] = audio
        sf.write(self.dir_salida / "estereo.wav", estereo, SAMPLE_RATE, subtype="PCM_16")

    @staticmethod
    def _resumen_canal(c: Canal) -> dict:
        return {
            "letra": c.letra,
            "inicio_s": round(c.inicio_s or 0.0, 3),
            "duracion_s": round(c.muestras / SAMPLE_RATE, 3),
            "desfase_llegada_s": _cuantiles(c.desfases_s),
            "retraso_parcial_s": _cuantiles(c.retrasos_parcial_s),
            "retraso_final_desde_voz_s": _cuantiles(c.retrasos_final_s),
        }

    def _resumen_detector(self) -> dict:
        validas = [e for e in self.evaluaciones if e.respuesta.valida]
        aviso = None
        if self.aviso is not None:
            a = self.aviso
            aviso = {
                **self.evento_detector(a),
                # Desde que se calló quien dijo la última frase cerrada hasta que se ve el aviso.
                "demora_desde_fin_de_voz_s": None if a.fin_voz_s is None else round(a.fin_s - a.fin_voz_s, 3),
            }
        return {
            "evaluaciones": len(self.evaluaciones),
            "fallos": len(self.evaluaciones) - len(validas),
            "actualizaciones_salteadas": sum(e.saltadas for e in self.evaluaciones),
            "segundos_detector": _cuantiles([e.respuesta.ms / 1000 for e in self.evaluaciones if e.respuesta.ms is not None]),
            "aviso": aviso,
        }

    @staticmethod
    def _escribir(archivo, dato: dict) -> None:
        archivo.write(json.dumps(dato, ensure_ascii=False) + "\n")
        archivo.flush()


def _cuantiles(valores: list[float]) -> dict | None:
    """Mediana, p95 y máximo en segundos (redondeados a ms)."""
    if not valores:
        return None
    v = np.asarray(valores, dtype=float)
    return {
        "n": len(v),
        "min": round(float(v.min()), 3),
        "mediana": round(float(np.median(v)), 3),
        "p95": round(float(np.percentile(v, 95)), 3),
        "max": round(float(v.max()), 3),
    }
