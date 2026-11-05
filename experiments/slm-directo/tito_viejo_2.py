"""Variante exploratoria de Tito viejo con señales léxicas acumuladas (#140)."""
from __future__ import annotations

import re
import unicodedata

from detectores import armar_mensaje_usuario
from filtro_tito import FlujoTitoSLM

# Pesos provisorios acordados; no son probabilidades ni están validados.
PESOS = {
    "te ganaste": 0.10,
    "fuiste seleccionado": 0.10,
    "transferencia": 0.04,
    "documento": 0.03,
    "codigo de acceso": 0.10,
    "numero del documento": 0.07,
    "numero del dni": 0.07,
    "pasamelo por aca": 0.06,
}


def normalizar(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texto.casefold())
                   if unicodedata.category(c) != "Mn")


class TitoViejo20(FlujoTitoSLM):
    """Compuerta experimental; no modifica ni reentrena el modelo de Tito."""

    def __init__(self, tito, slm, umbral=0.5, pesos=None):
        super().__init__(tito, slm, umbral)
        self.pesos = dict(PESOS if pesos is None else pesos)
        self.vistas = set()

    def reiniciar(self):
        super().reiniciar()
        self.vistas.clear()

    def _registrar(self, texto):
        texto = normalizar(texto)
        coincidencias = []
        for expresion in self.pesos:
            patron = r"(?<!\w)" + r"\s+".join(map(re.escape, expresion.split())) + r"(?!\w)"
            for m in re.finditer(patron, texto):
                coincidencias.append((m.start(), m.end(), expresion))
        ocupadas = []
        for inicio, fin, expresion in sorted(coincidencias, key=lambda c: (-(c[1] - c[0]), c[0])):
            if any(inicio < otro_fin and fin > otro_inicio for otro_inicio, otro_fin in ocupadas):
                continue
            ocupadas.append((inicio, fin))
            self.vistas.add(expresion)

    def evaluar(self, lineas):
        e = self.estado
        puntaje = None
        tito_ms = None
        error = ""
        if not e.activado:
            self._registrar(lineas[-1].texto)
            puntaje, error, tito_ms = self._puntuar(lineas)
            if error:
                e.activado, e.fallo_tito = True, error
            elif puntaje is not None and puntaje + sum(self.pesos[x] for x in self.vistas) >= self.umbral:
                e.activado = True
                e.indicio_linea = len(lineas)
                e.indicio_texto = lineas[-1].texto
                e.indicio_puntaje = puntaje
        if not e.activado:
            assert puntaje is not None and tito_ms is not None
            return self._respuesta_omitida(tito_ms, puntaje)
        # En esta variante no se añade ningún bloque de indicio o fallo al mensaje.
        usuario = armar_mensaje_usuario(lineas, self.slm.hablantes)
        r = self.slm.evaluar_mensaje(usuario, lineas)
        r.consulta = "slm_valida" if r.valida else "slm_fallo"
        r.tito_puntaje, r.tito_ms = puntaje, tito_ms
        r.tito_error = error or e.fallo_tito
        r.indicio_linea, r.indicio_texto, r.indicio_puntaje = e.indicio_linea, e.indicio_texto, e.indicio_puntaje
        if r.slm_ms is None:
            r.slm_ms = r.ms
        r.ms = (r.slm_ms or 0.0) + (tito_ms or 0.0)
        return r
