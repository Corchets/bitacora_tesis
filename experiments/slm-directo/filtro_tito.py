"""Filtro Tito como consulta al SLM (#69, parte de #68).

Tito puntúa cada fragmento nuevo. Ante el primer puntaje mayor o igual al umbral
(0,5, igualdad incluida) activa al SLM en esa misma actualización y lo mantiene
activo en cada línea posterior. Si Tito falla técnicamente, también se activa el
SLM y se conserva la causa técnica: no se fabrica puntaje ni sospecha.

El SLM recibe el contexto de consulta completo (todas las líneas disponibles
desde el comienzo, incluida la disparadora, sin futuro ni referencia humana) y,
por separado, el indicio de la primera activación declarado explícitamente como
sospecha falible que puede descartarse. Solo el SLM puede sugerir el aviso; el
puntaje de Tito nunca avisa.

Estado por conversación: contexto, activación e indicio se reinician con
`reiniciar()` (lo llama `correr.procesar_caso` al empezar cada caso).

El Tito real (RoBERTuito congelado + regresión logística) llega con #68
completo; acá va `TitoGuion`, un simulado determinista para demostrar el
recorrido de punta a punta sin descargar ni entrenar modelos.
"""

from __future__ import annotations

from dataclasses import dataclass

from detectores import Respuesta, armar_mensaje_usuario

# Convención exploratoria de #68: no es probabilidad de fraude ni umbral validado.
UMBRAL_TITO = 0.5

BLOQUE_INDICIO = (
    "El filtro previo señaló para revisión la línea {n}: «{fragmento}».\n"
    "Su puntaje fue {puntaje:.2f}. Es una sospecha preliminar, puede ser incorrecta y no "
    "confirma una estafa. Evaluá el contexto de consulta completo y decidí si el indicio "
    "está justificado; podés descartarlo."
)

BLOQUE_FALLO_TITO = (
    "El filtro previo falló técnicamente ({error}) y por eso se consulta al SLM. "
    "No hay puntaje ni fragmento sospechoso: evaluá solo el contexto de consulta."
)


def armar_bloque_indicio(n: int, fragmento: str, puntaje: float) -> str:
    """Indicio de la primera activación, separado del diálogo y falible."""
    return BLOQUE_INDICIO.format(n=n, fragmento=fragmento, puntaje=puntaje)


def armar_bloque_fallo_tecnico(error: str) -> str:
    """Activación por fallo de Tito: registra la causa sin inventar sospecha."""
    return BLOQUE_FALLO_TITO.format(error=error)


def armar_mensaje_filtrado(base: str, bloque: str) -> str:
    """Contexto completo más el bloque de indicio, en partes separadas."""
    return base + "\n\n" + bloque


class TitoGuion:
    """Tito simulado determinista: puntaje fijo por línea y fallos programados.

    Lo no listado puntúa 0,0. `ms_fijo` deja el costo de Tito verificable
    en pruebas sin depender del reloj.
    """

    nombre = "tito-guion"

    def __init__(
        self,
        puntajes: dict[int, float] | None = None,
        fallos: set[int] | None = None,
        ms_fijo: float = 5.0,
    ) -> None:
        self.puntajes = dict(puntajes or {})
        self.fallos = set(fallos or ())
        self.ms_fijo = ms_fijo
        self.consultas: list[tuple[int, str]] = []

    def puntuar(self, n: int, texto: str) -> tuple[float | None, str, float]:
        """(puntaje o None, error o "", ms). Un fallo no fabrica puntaje."""
        self.consultas.append((n, texto))
        if n in self.fallos:
            return None, "tito_caido", self.ms_fijo
        return self.puntajes.get(n, 0.0), "", self.ms_fijo


@dataclass
class EstadoFiltro:
    activado: bool = False
    indicio_linea: int | None = None
    indicio_texto: str = ""
    indicio_puntaje: float | None = None
    fallo_tito: str = ""


class FlujoTitoSLM:
    """Orquestación Tito→SLM compatible con `correr.procesar_caso`.

    `slm` debe exponer `.hablantes` y `.evaluar_mensaje(usuario, lineas)`
    (ver `DetectorSLM`); así se reutiliza su validación de salida, su control
    de contexto excedido y su política de aviso único queda en `Llamada`.
    """

    def __init__(self, tito: TitoGuion, slm, umbral: float = UMBRAL_TITO) -> None:
        self.tito = tito
        self.slm = slm
        self.umbral = umbral
        self.estado = EstadoFiltro()

    def reiniciar(self) -> None:
        self.estado = EstadoFiltro()

    def _respuesta_omitida(self, tito_ms: float, puntaje: float) -> Respuesta:
        e = self.estado
        return Respuesta(
            valida=True,
            alerta_sugerida=False,
            ms=tito_ms,
            consulta="omitida",
            tito_puntaje=puntaje,
            indicio_linea=e.indicio_linea,
            indicio_puntaje=e.indicio_puntaje,
        )

    def evaluar(self, lineas) -> Respuesta:
        n = len(lineas)
        fragmento = lineas[-1].texto
        e = self.estado
        tito_ms = 0.0
        tito_puntaje: float | None = None
        tito_error = ""

        if not e.activado:
            tito_puntaje, tito_error, tito_ms = self.tito.puntuar(n, fragmento)
            if tito_error:
                e.activado = True
                e.fallo_tito = tito_error
            elif tito_puntaje is not None and tito_puntaje >= self.umbral:
                e.activado = True
                e.indicio_linea = n
                e.indicio_texto = fragmento
                e.indicio_puntaje = tito_puntaje

        if not e.activado:
            assert tito_puntaje is not None  # sin fallo, puntuar siempre devuelve puntaje
            return self._respuesta_omitida(tito_ms, tito_puntaje)

        if e.fallo_tito:
            bloque = armar_bloque_fallo_tecnico(e.fallo_tito)
        else:
            assert e.indicio_linea is not None and e.indicio_puntaje is not None
            bloque = armar_bloque_indicio(e.indicio_linea, e.indicio_texto, e.indicio_puntaje)
        base = armar_mensaje_usuario(lineas, self.slm.hablantes)
        r = self.slm.evaluar_mensaje(armar_mensaje_filtrado(base, bloque), lineas)
        r.consulta = "slm_valida" if r.valida else "slm_fallo"
        r.tito_puntaje = tito_puntaje
        r.tito_error = tito_error or e.fallo_tito
        r.indicio_linea = e.indicio_linea
        r.indicio_texto = e.indicio_texto
        r.indicio_puntaje = e.indicio_puntaje
        r.ms = (r.ms or 0.0) + tito_ms
        return r
