"""Política de reconsultas Tito→SLM con cierre y reapertura (#102, parte de #95).

Prepara la comparación «activación permanente vs reconsultas» sin medirla:
demonstra con dobles el comportamiento de consulta en el recorrido existente
(`correr.procesar_caso`) con la misma interfaz que `FlujoTitoSLM`
(`evaluar(lineas)` / `reiniciar()`).

Diferencia con `FlujoTitoSLM` (activación permanente): acá una respuesta
negativa VÁLIDA del SLM cierra las consultas; solo se vuelve a consultar ante
evidencia nueva configurable o revisión periódica configurable, y solo
después de la derivación inicial. Todo lo demás se mantiene fijo para que la
política sea la única variable al comparar: mismo Tito, misma entrada, mismo
umbral, mismo prompt, mismo indicio falible, mismo `Respuesta` y mismo
`correr.procesar_caso` (aviso único y fin operativo al primer aviso válido).

Reglas invariantes (no configurables):

- Tito se evalúa y se cuenta en CADA actualización, incluso sin consultar al
  SLM (`tito_ms` nunca es `None`): el costo adicional de Tito queda visible
  sin doble conteo (`ms` = `tito_ms` + `slm_ms`).
- El SLM recibe siempre el contexto completo disponible hasta la actualización
  (sin futuro) más el bloque de indicio o de fallo técnico, igual que el
  flujo permanente.
- Error o salida inválida del SLM NO es rechazo válido y NO cierra: la
  consulta sigue abierta y se reintenta en la actualización siguiente.
- Fallo técnico de Tito deriva por fail-open sin fabricar sospecha ni puntaje;
  solo el SLM puede avisar.
- `reiniciar()` limpia todo entre llamadas: nada pasa de una a otra.

> **Estado: propuesta sin discutir.** `periodo_revision`,
> `regla_nueva_evidencia` y `delta_minimo` son candidatos sin acordar ni
> seleccionar; ver
> [D08](../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).
> Se elegirán con validación ANTES de abrir veinte y medir; el margen
> preventivo final sigue abierto y no se adopta 95/5. Los valores de los
> ejemplos y tests son solo para demostrar el mecanismo, no una selección.
> Nada de lo que sigue cierra D08 ni la arquitectura final.
"""

from __future__ import annotations

from dataclasses import dataclass

import math

from detectores import Respuesta
from filtro_tito import (
    UMBRAL_TITO,
    EstadoFiltro,
    FlujoTitoSLM,
    armar_bloque_fallo_tecnico,
    armar_bloque_indicio,
    armar_mensaje_filtrado,
    armar_mensaje_usuario,
)

# Única regla de nueva evidencia implementada (candidata, ver D08 en el
# docstring del módulo): el puntaje vuelve a cruzar el umbral después de
# haber estado bajo desde la última consulta al SLM. Cualquier otra regla
# futura se agrega acá con nombre explícito; nada se hardcodea en silencio
# dentro de `evaluar`.
REGLA_NUEVO_CRUCE_TRAS_BAJAR = "nuevo_cruce_tras_bajar"
REGLAS_NUEVA_EVIDENCIA = (REGLA_NUEVO_CRUCE_TRAS_BAJAR,)

BLOQUE_SIN_INDICIO = (
    "Revisión sin indicio vigente: Tito no señala sospecha en el contexto "
    "visible. No hay puntaje ni fragmento sospechoso: evaluá solo el "
    "contexto de consulta."
)


def armar_bloque_sin_indicio() -> str:
    """Revisión tras fail-open recuperado sin indicio: no fabrica sospecha."""
    return BLOQUE_SIN_INDICIO


def visibles_para_tito(lineas) -> list[str]:
    """Historial visible hasta la actualización, con hablantes, sin futuro.

    Misma forma que `entrenar_tito_99.construir_entrada` espera para
    `historial_acumulado` (`"A: ..."` por línea). Sin estado entre llamadas
    y sin truncamiento: siempre el prefijo completo disponible.
    """
    return [f"{linea.hablante}: {linea.texto}" for linea in lineas]


@dataclass
class EstadoReconsulta(EstadoFiltro):
    """Estado público y trazable de la política por conversación.

    `fallo_tito` conserva la causa histórica del último fail-open para
    trazabilidad; nunca se usa como error actual (`Respuesta.tito_error`
    lleva solo el error de la actualización que se consulta).
    """

    cerrada: bool = False
    ultima_consulta_linea: int | None = None
    bajo_desde_ultima: bool = False


class PoliticaReconsultas(FlujoTitoSLM):
    """Adaptador con cierre y reapertura sobre `FlujoTitoSLM`.

    Reutiliza su interfaz (`evaluar`/`reiniciar`), sus ayudantes de mensaje y
    su tratamiento del SLM (`slm.evaluar_mensaje`); no duplica el evaluador
    ni el llamador de API. Solo cambia CUÁNDO se consulta una vez derivado.
    La traza pública (`traza`, `ultimo_motivo`) registra la decisión de cada
    actualización para el reporte #102.
    """

    def __init__(
        self,
        tito,
        slm,
        umbral: float = UMBRAL_TITO,
        *,
        periodo_revision: int | None,
        regla_nueva_evidencia: str,
        delta_minimo: float = 0.0,
    ) -> None:
        """Parámetros explícitos de la política (candidatos, ver D08).

        `periodo_revision`: cada cuántas líneas desde la última consulta se
        vuelve a consultar tras el cierre (p. ej. 3); `None` desactiva la
        revisión periódica. Solo aplica después de la derivación inicial.
        `regla_nueva_evidencia`: nombre en `REGLAS_NUEVA_EVIDENCIA`.
        `delta_minimo`: margen extra sobre el umbral para la reapertura
        (0.0 = el umbral sin margen); cualquier delta futuro pasa por acá.
        """
        super().__init__(tito, slm, umbral)
        if periodo_revision is not None and (
            isinstance(periodo_revision, bool)
            or not isinstance(periodo_revision, int)
            or periodo_revision < 1
        ):
            raise ValueError(
                f"periodo_revision debe ser entero >= 1 o None, no {periodo_revision!r}."
            )
        if regla_nueva_evidencia not in REGLAS_NUEVA_EVIDENCIA:
            raise ValueError(
                f"regla_nueva_evidencia desconocida {regla_nueva_evidencia!r}; "
                f"opciones: {list(REGLAS_NUEVA_EVIDENCIA)}."
            )
        if (
            isinstance(delta_minimo, bool)
            or not isinstance(delta_minimo, (int, float))
            or not math.isfinite(delta_minimo)
            or delta_minimo < 0
        ):
            raise ValueError(
                f"delta_minimo debe ser número finito >= 0, no {delta_minimo!r}."
            )
        self.periodo_revision = periodo_revision
        self.regla_nueva_evidencia = regla_nueva_evidencia
        self.delta_minimo = float(delta_minimo)
        self.estado = EstadoReconsulta()
        self.traza: list[dict] = []
        self.ultimo_motivo: str = ""

    def reiniciar(self) -> None:
        self.estado = EstadoReconsulta()
        self.traza = []
        self.ultimo_motivo = ""

    def _puntuar(self, lineas) -> tuple[float | None, str, float]:
        """Puntúa la actualización actual con la entrada que el Tito trae.

        Tito de frase (`puntuar(n, frase)`, `TitoGuion`/`TitoReal`): solo
        el fragmento nuevo, igual que `FlujoTitoSLM`. Tito nuevo con API
        real (`puntuar_prefijo(visibles)`, `Tito99`): el historial
        acumulado con hablantes A/B vía `visibles_para_tito`, misma
        construcción que `entrenar_tito_99.construir_entrada` espera.
        Sin estado entre llamadas, sin futuro y sin truncamiento: siempre
        el prefijo completo disponible. Solo cambia la entrada de Tito;
        umbral, prompt, indicio y SLM quedan fijos.
        """
        puntuar_prefijo = getattr(self.tito, "puntuar_prefijo", None)
        if callable(puntuar_prefijo):
            return puntuar_prefijo(visibles_para_tito(lineas))
        n = len(lineas)
        return self.tito.puntuar(n, lineas[-1].texto)

    def _registrar(self, n: int, motivo: str, consulta: str, puntaje=None) -> None:
        e = self.estado
        self.ultimo_motivo = motivo
        self.traza.append(
            {
                "linea": n,
                "motivo": motivo,
                "consulta": consulta,
                "cerrada": e.cerrada,
                "activado": e.activado,
                "tito_puntaje": puntaje,
                "ultima_consulta_linea": e.ultima_consulta_linea,
            }
        )

    def _hay_evidencia_nueva(self, puntaje: float | None) -> bool:
        """Candidata `nuevo_cruce_tras_bajar` (ver D08): cruza umbral+delta
        después de haber estado bajo desde la última consulta al SLM."""
        e = self.estado
        if self.regla_nueva_evidencia == REGLA_NUEVO_CRUCE_TRAS_BAJAR:
            return (
                puntaje is not None
                and puntaje >= self.umbral + self.delta_minimo
                and e.bajo_desde_ultima
            )
        return False  # reglas futuras con nombre explícito

    def _toca_revision(self, n: int) -> bool:
        e = self.estado
        return (
            self.periodo_revision is not None
            and e.ultima_consulta_linea is not None
            and n - e.ultima_consulta_linea >= self.periodo_revision
        )

    def _consultar_slm(self, lineas, tito_puntaje, tito_ms, tito_error) -> Respuesta:
        e = self.estado
        if tito_error:
            bloque = armar_bloque_fallo_tecnico(tito_error)
        elif e.indicio_linea is not None and e.indicio_puntaje is not None:
            bloque = armar_bloque_indicio(e.indicio_linea, e.indicio_texto, e.indicio_puntaje)
        else:
            # Revisión sin indicio vigente (p. ej. periódica tras un
            # fail-open ya recuperado): ni se reutiliza la causa histórica
            # ni se fabrica sospecha; se evalúa solo el contexto visible.
            bloque = armar_bloque_sin_indicio()
        base = armar_mensaje_usuario(lineas, self.slm.hablantes)
        r = self.slm.evaluar_mensaje(armar_mensaje_filtrado(base, bloque), lineas)
        r.consulta = "slm_valida" if r.valida else "slm_fallo"
        r.tito_puntaje = tito_puntaje
        r.tito_ms = tito_ms  # Tito corre siempre: se cuenta cada evaluación
        r.tito_error = tito_error  # solo el error actual; el histórico queda en e.fallo_tito
        r.indicio_linea = e.indicio_linea
        r.indicio_texto = e.indicio_texto
        r.indicio_puntaje = e.indicio_puntaje
        if r.slm_ms is None:
            r.slm_ms = r.ms
        r.ms = (r.slm_ms or 0.0) + (tito_ms or 0.0)
        return r

    def _tras_consulta_valida(self, n: int, r: Respuesta) -> None:
        """Actualiza el cierre solo ante respuesta VÁLIDA del SLM."""
        e = self.estado
        e.ultima_consulta_linea = n
        e.bajo_desde_ultima = False
        if not r.alerta_sugerida:
            e.cerrada = True

    def evaluar(self, lineas) -> Respuesta:
        n = len(lineas)
        e = self.estado
        # Tito corre en cada actualización, consulte o no el SLM.
        tito_puntaje, tito_error, costo_tito = self._puntuar(lineas)

        if not e.activado:
            if tito_error:
                e.activado = True
                e.fallo_tito = tito_error
            elif tito_puntaje is not None and tito_puntaje >= self.umbral:
                e.activado = True
                e.indicio_linea = n
                e.indicio_texto = lineas[-1].texto
                e.indicio_puntaje = tito_puntaje
            else:
                assert tito_puntaje is not None
                r = self._respuesta_omitida(costo_tito, tito_puntaje)
                r.tito_ms = costo_tito
                self._registrar(n, "sin_derivar", r.consulta, tito_puntaje)
                return r

        if tito_error:
            # Fail-open: el fallo técnico actual siempre deriva, sin puntaje
            # ni sospecha. No envenena el flujo: si Tito se recupera, la
            # política vuelve a decidir por puntaje. La causa queda en
            # e.fallo_tito solo como trazabilidad histórica.
            e.fallo_tito = tito_error
            e.cerrada = False
            r = self._consultar_slm(lineas, None, costo_tito, tito_error)
            if r.valida:
                self._tras_consulta_valida(n, r)
            # Inválida: queda abierta y reintenta en la actualización
            # siguiente, sin mover ultima_consulta_linea.
            self._registrar(n, "fallo_tito_deriva", r.consulta, None)
            return r

        assert tito_puntaje is not None
        if not e.cerrada and e.ultima_consulta_linea is None and n == e.indicio_linea:
            motivo = "activacion_inicial"
            r = self._consultar_slm(lineas, tito_puntaje, costo_tito, "")
            if r.valida:
                self._tras_consulta_valida(n, r)
            self._registrar(n, motivo, r.consulta, tito_puntaje)
            return r

        if not e.cerrada:
            # Abierta sin veredicto válido todavía: se consulta cada línea
            # hasta la primera respuesta válida (igual que la permanente).
            motivo = "abierta_sin_veredicto"
            r = self._consultar_slm(lineas, tito_puntaje, costo_tito, "")
            if r.valida:
                self._tras_consulta_valida(n, r)
            self._registrar(n, motivo, r.consulta, tito_puntaje)
            return r

        # Cerrada: solo se reabre por evidencia nueva, revisión periódica o
        # fallo técnico (ya tratado arriba). Error o salida inválida del
        # SLM NO es rechazo válido y NO cierra: queda abierta y reintenta
        # en la actualización siguiente, sin mover ultima_consulta_linea.
        if self._hay_evidencia_nueva(tito_puntaje):
            motivo = "reapertura_nueva_evidencia"
            e.cerrada = False
            r = self._consultar_slm(lineas, tito_puntaje, costo_tito, "")
            if r.valida:
                self._tras_consulta_valida(n, r)
            self._registrar(n, motivo, r.consulta, tito_puntaje)
            return r
        if self._toca_revision(n):
            motivo = "revision_periodica"
            e.cerrada = False
            r = self._consultar_slm(lineas, tito_puntaje, costo_tito, "")
            if r.valida:
                self._tras_consulta_valida(n, r)
            self._registrar(n, motivo, r.consulta, tito_puntaje)
            return r
        if tito_puntaje < self.umbral:
            e.bajo_desde_ultima = True
        r = self._respuesta_omitida(costo_tito, tito_puntaje)
        r.tito_ms = costo_tito
        self._registrar(n, "cerrada_sin_novedad", r.consulta, tito_puntaje)
        return r
