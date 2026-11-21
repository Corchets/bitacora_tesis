"""Turnos de la llamada: cuándo consultar al detector (ADR 0007).

Junta las frases del ASR de cada canal en turnos. El turno de un lado se cierra cuando el otro lado
empieza a hablar en serio o tras un silencio largo. Al cerrar un turno de OTRA se consulta; los de
PROTEGIDA entran en el contexto pero no consultan. Un turno de OTRA largo consulta igual al pasar
el tope, siempre al cerrar una frase: nunca a mitad de una oración.

No sabe de audio ni de relojes: `llamada.py` le pasa cada actualización del ASR y el silencio de
cada canal, en segundos del reloj de la llamada.

> Estado: los umbrales son provisorios; se fijan con grabaciones, no con los casos.
"""

from __future__ import annotations

from dataclasses import dataclass

CONSULTA = "otra"  # el único rol cuyos turnos consultan


@dataclass(frozen=True)
class ReglasTurno:
    palabras: int = 3  # el otro lado habla en serio con al menos estas palabras...
    voz_s: float = 1.0  # ...o con un segmento de más de estos segundos; un «ajá» no llega a ninguno
    silencio_s: float = 2.0  # silencio de un canal que cierra su turno
    tope_s: float = 15.0  # un turno de OTRA más largo consulta igual, al cerrar la frase siguiente

    def __post_init__(self) -> None:
        if self.palabras < 1 or self.voz_s < 0 or self.silencio_s <= 0 or self.tope_s <= 0:
            raise ValueError("Reglas de turno: palabras >= 1, voz >= 0 s, silencio y tope > 0 s.")


@dataclass
class _Turno:
    desde_s: float  # inicio de lo que todavía no se consultó
    finales: int = 0  # frases cerradas sin consultar
    abierto: bool = False  # el ASR tiene una frase de este lado sin cerrar
    ceder: bool = False  # el otro lado ya habló en serio: se cierra al terminar la frase abierta


class Turnos:
    def __init__(self, reglas: ReglasTurno) -> None:
        self.reglas = reglas
        self.abiertos: dict[str, _Turno] = {}
        self.cierres: list[dict] = []  # para el manifiesto: con esto se calibran los umbrales

    def frase(self, rol: str, tipo: str, texto: str, inicio_s: float, fin_s: float) -> int:
        """Una actualización del ASR. `fin_s`: fin de la voz si es final. Devuelve cuántas consultas pide."""
        turno = self.abiertos.setdefault(rol, _Turno(desde_s=inicio_s))
        turno.abierto = tipo == "parcial"
        consultas = 0
        if tipo == "final":
            turno.finales += 1
            if rol == CONSULTA and fin_s - turno.desde_s >= self.reglas.tope_s and not turno.ceder:
                consultas += self._anotar(rol, "tope", turno, fin_s)
                turno.desde_s, turno.finales = fin_s, 0
        if self.en_serio(texto, fin_s - inicio_s):
            for otro, t in self.abiertos.items():
                t.ceder = t.ceder or otro != rol
        for otro in [r for r, t in self.abiertos.items() if t.ceder and not t.abierto]:
            consultas += self._cerrar(otro, "cambio", fin_s)
        return consultas

    def silencio(self, rol: str, silencio_s: float, t_s: float) -> int:
        """Silencio acumulado de un canal tras cada bloque de audio."""
        if rol in self.abiertos and silencio_s >= self.reglas.silencio_s:
            return self._cerrar(rol, "silencio", t_s)
        return 0

    def cerrar_todo(self, t_s: float) -> int:
        """Fin de la llamada: lo que quedó abierto también se consulta."""
        return sum(self._cerrar(rol, "fin", t_s) for rol in list(self.abiertos))

    def en_serio(self, texto: str, dur_s: float) -> bool:
        palabras = sum(any(c.isalnum() for c in p) for p in texto.split())
        return palabras >= self.reglas.palabras or dur_s > self.reglas.voz_s

    def _cerrar(self, rol: str, motivo: str, t_s: float) -> int:
        return self._anotar(rol, motivo, self.abiertos.pop(rol), t_s)

    def _anotar(self, rol: str, motivo: str, turno: _Turno, t_s: float) -> int:
        consulta = rol == CONSULTA and turno.finales > 0
        self.cierres.append({"rol": rol, "motivo": motivo, "desde_s": round(turno.desde_s, 3),
                             "hasta_s": round(t_s, 3), "finales": turno.finales, "consulta": consulta})
        return int(consulta)
