"""Diccionario de corrección de la frase final (#94, PLAN-VOZ-REAL.md §4 paso 4).

Reemplaza errores frecuentes del ASR por su corrección a partir de un archivo de pares
`error,correccion` que se arma mirando la toma 1. Solo toca lo que está en el archivo:

- exacto: la palabra (o la secuencia de palabras) coincide con el error, sin distinguir mayúsculas
  ni tildes (la ñ se distingue);
- aproximado, acotado: un error de UNA sola palabra de 6 letras o más también se corrige si el
  texto trae esa palabra con un único typo (una letra cambiada, de más, de menos o dos
  intercambiadas). Si dos errores del archivo quedan igual de cerca no se elige ninguno, y una
  palabra que ya es una corrección nunca se vuelve a tocar.

Se aplica solo a eventos `final`: un parcial se reescribe en pantalla y corregirlo sería inventar.
Va último en el orden de trabajo porque un reemplazo aproximado puede *inventar* un «código»: lo
controlan las frases negativas de la medición.

Uso en la cadena de ASR:  `MotorConDiccionario(motor, Diccionario.desde_archivo("diccionario.csv"))`.
"""

from __future__ import annotations

import csv
import re
import unicodedata
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

import numpy as np

from motores import EventoASR, MotorASR

LARGO_MINIMO_APROXIMADO = 6
_TOKEN = re.compile(r"\S+")
_BORDES = re.compile(r"^(?P<antes>[^\w]*)(?P<nucleo>.*?)(?P<despues>[^\w]*)$", re.UNICODE)


def normalizar_palabra(texto: str) -> str:
    """Minúsculas, sin tildes (la ñ se conserva) y sin signos."""
    protegido = texto.lower().replace("ñ", "\x00")
    sin_tildes = "".join(c for c in unicodedata.normalize("NFD", protegido) if unicodedata.category(c) != "Mn")
    return re.sub(r"[^\w\x00]", "", sin_tildes.replace("\x00", "ñ"), flags=re.UNICODE).strip()


def un_typo(a: str, b: str) -> bool:
    """True si `b` sale de `a` con una sola edición (Damerau: el intercambio cuenta uno)."""
    if a == b:
        return True
    la, lb = len(a), len(b)
    if abs(la - lb) > 1:
        return False
    if la == lb:
        difs = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
        if len(difs) == 1:
            return True
        return (len(difs) == 2 and difs[1] == difs[0] + 1
                and a[difs[0]] == b[difs[1]] and a[difs[1]] == b[difs[0]])
    corta, larga = (a, b) if la < lb else (b, a)
    return any(larga[:i] + larga[i + 1:] == corta for i in range(len(larga)))


@dataclass
class _Token:
    antes: str
    nucleo: str
    despues: str
    norma: str


def _separar(texto: str) -> tuple[list[_Token], list[str]]:
    """Tokens por espacios y los blancos que hay entre ellos (para rearmar el texto igual)."""
    tokens, blancos, fin = [], [], 0
    for m in _TOKEN.finditer(texto):
        blancos.append(texto[fin:m.start()])
        partes = _BORDES.match(m.group())
        tokens.append(_Token(partes["antes"], partes["nucleo"], partes["despues"], normalizar_palabra(partes["nucleo"])))
        fin = m.end()
    blancos.append(texto[fin:])
    return tokens, blancos


def _con_mayuscula_si_corresponde(original: str, correccion: str) -> str:
    if original[:1].isupper() and correccion[:1].islower():
        return correccion[:1].upper() + correccion[1:]
    return correccion


class Diccionario:
    """Pares error -> corrección sobre el texto de una frase final."""

    def __init__(self, pares: list[tuple[str, str]], aproximado: bool = True,
                 largo_minimo_aproximado: int = LARGO_MINIMO_APROXIMADO):
        self.aproximado = aproximado
        self.largo_minimo_aproximado = largo_minimo_aproximado
        self.pares: dict[tuple[str, ...], str] = {}
        for error, correccion in pares:
            error, correccion = error.strip(), correccion.strip()
            clave = tuple(p for p in (normalizar_palabra(w) for w in error.split()) if p)
            if not clave or not correccion:
                raise ValueError(f"Par vacío en el diccionario: {error!r} -> {correccion!r}")
            if error == correccion:
                raise ValueError(f"El error y la corrección son iguales: {error!r}")
            if clave in self.pares and self.pares[clave] != correccion:
                raise ValueError(f"El error {error!r} aparece con dos correcciones distintas.")
            self.pares[clave] = correccion
        self._max_palabras = max((len(c) for c in self.pares), default=0)
        self._correcciones = {normalizar_palabra(c) for c in self.pares.values()}
        self._aproximables = [c[0] for c in self.pares
                              if len(c) == 1 and len(c[0]) >= largo_minimo_aproximado]

    def __len__(self) -> int:
        return len(self.pares)

    @classmethod
    def desde_archivo(cls, ruta: str | Path, **opciones: Any) -> "Diccionario":
        """Lee un CSV `error,correccion`. Ignora comentarios («#»), líneas vacías y el encabezado."""
        pares = []
        with open(ruta, encoding="utf-8", newline="") as archivo:
            lineas = [(n, l) for n, l in enumerate(archivo, start=1) if l.strip() and not l.lstrip().startswith("#")]
        for n, linea in lineas:
            campos = next(csv.reader([linea]))
            if [c.strip().lower() for c in campos] == ["error", "correccion"]:
                continue
            if len(campos) != 2 or not campos[0].strip() or not campos[1].strip():
                raise ValueError(f"{ruta}: línea {n}: se esperaba «error,correccion»: {linea.strip()!r}")
            pares.append((campos[0], campos[1]))
        return cls(pares, **opciones)

    def _aproximada(self, norma: str) -> str | None:
        """La clave del archivo a un typo de distancia, si es una sola y la palabra no es ya una corrección."""
        if (not self.aproximado or len(norma) < self.largo_minimo_aproximado - 1
                or norma in self._correcciones):
            return None
        cerca = [c for c in self._aproximables if un_typo(c, norma)]
        return cerca[0] if len(cerca) == 1 else None

    def corregir_con_detalle(self, texto: str) -> tuple[str, list[dict]]:
        """El texto corregido y la lista de cambios `{original, correccion, tipo}`."""
        if not texto or not self.pares:
            return texto, []
        tokens, blancos = _separar(texto)
        salida, cambios, i = [], [], 0
        while i < len(tokens):
            cambio = self._buscar(tokens, i)
            if cambio is None:
                t = tokens[i]
                salida.append(blancos[i] + t.antes + t.nucleo + t.despues)
                i += 1
                continue
            largo, correccion, tipo = cambio
            primero, ultimo = tokens[i], tokens[i + largo - 1]
            original = " ".join(t.nucleo for t in tokens[i:i + largo])
            nuevo = _con_mayuscula_si_corresponde(primero.nucleo, correccion)
            salida.append(blancos[i] + primero.antes + nuevo + ultimo.despues)
            cambios.append({"original": original, "correccion": nuevo, "tipo": tipo})
            i += largo
        return "".join(salida) + blancos[-1], cambios

    def _buscar(self, tokens: list[_Token], i: int) -> tuple[int, str, str] | None:
        """(palabras que cubre, corrección, tipo) del cambio que empieza en `i`, o None."""
        for largo in range(min(self._max_palabras, len(tokens) - i), 0, -1):
            tramo = tokens[i:i + largo]
            # Una secuencia no cruza una coma o un punto: los signos solo valen al final del tramo.
            if any(t.despues.strip() for t in tramo[:-1]) or any(not t.norma for t in tramo):
                continue
            correccion = self.pares.get(tuple(t.norma for t in tramo))
            if correccion is not None:
                return largo, correccion, "exacto"
        clave = self._aproximada(tokens[i].norma)
        if clave is not None and tokens[i].norma:
            return 1, self.pares[(clave,)], "aproximado"
        return None

    def corregir(self, texto: str) -> str:
        return self.corregir_con_detalle(texto)[0]

    def aplicar_a_evento(self, evento: EventoASR) -> EventoASR:
        """El evento con el texto corregido si es una frase final; un parcial vuelve tal cual."""
        if evento.tipo != "final":
            return evento
        return replace(evento, texto=self.corregir(evento.texto))

    def descripcion(self) -> dict[str, Any]:
        return {"pares": len(self), "aproximado": self.aproximado,
                "largo_minimo_aproximado": self.largo_minimo_aproximado, "solo_finales": True}


class MotorConDiccionario(MotorASR):
    """Envuelve un motor y corrige el texto de sus eventos finales; los parciales pasan sin tocar."""

    def __init__(self, motor: MotorASR, diccionario: Diccionario):
        self.motor = motor
        self.diccionario = diccionario

    def __getattr__(self, nombre: str) -> Any:
        # nombre, modelo_id, es_streaming, tipo_entrega, reiniciar, etc.: los del motor envuelto.
        return getattr(self.motor, nombre)

    def inicializar(self) -> None:
        self.motor.inicializar()

    def procesar_bloque(self, muestras: np.ndarray, inicio_bloque_s: float, fin_bloque_s: float) -> list[EventoASR]:
        return [self.diccionario.aplicar_a_evento(e)
                for e in self.motor.procesar_bloque(muestras, inicio_bloque_s, fin_bloque_s)]

    def vaciar_final(self, fin_audio_s: float) -> list[EventoASR]:
        return [self.diccionario.aplicar_a_evento(e) for e in self.motor.vaciar_final(fin_audio_s)]

    def metadatos(self) -> dict[str, Any]:
        return {**self.motor.metadatos(), "diccionario": self.diccionario.descripcion()}
