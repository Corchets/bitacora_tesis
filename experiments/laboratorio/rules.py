"""Reglas de incendio: lista de trabajo sobre el borrador.

D07 sigue abierta: esto no congela la taxonomia, solo permite correr #29.
"""

import unicodedata

PATRONES = {
    "REQUEST_AUTH_CODE": ["codigo", "otp", "token", "verificacion", "seis digitos", "numeros"],
    "REQUEST_SECRET": ["clave", "pin", "cvv", "contrasena", "password"],
    "REQUEST_TRANSFER": [
        "transferencia",
        "transferi",
        "pago",
        "paga",
        "cripto",
        "efectivo",
        "alias",
        "cbu",
        "plata",
    ],
    "REQUEST_PERSONAL_DATA": ["dni", "domicilio", "identidad", "cuil"],
    "REQUEST_REMOTE_ACCESS": [
        "acceso remoto",
        "teamviewer",
        "anydesk",
        "comparti pantalla",
        "instala",
    ],
    "REQUEST_SECURITY_ACTION": ["abri el enlace", "link", "autoriza", "configuracion"],
}


def _normalizar(texto: str) -> str:
    texto = texto.lower()
    sin_acentos = "".join(
        c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn"
    )
    return " ".join(sin_acentos.split())


# Spike, no taxonomia (D07 abierta). Un turno que niega el pedido no es incendio,
# salvo que ademas traiga un imperativo ("no cortes y decime el codigo").
# P13: negaciones y patrones de 6+ letras toleran un typo (letra cambiada,
# agregada, quitada o swap); los cortos ("pin", "otp", "cbu") quedan exactos
# para que el fuzzy no prenda de más.
_MIN_FUZZY = 6
# P14: patrones que quedan exactos aunque sean largos. "numero" (legítimo,
# no-bajes-nada t3) está a distancia 1 de "numeros" y el fuzzy lo prendería.
_SOLO_EXACTO = frozenset({"numeros"})


def _edicion1(a: str, b: str) -> bool:
    """True si b sale de a con un solo typo (Damerau: el swap cuenta 1)."""
    if a == b:
        return True
    la, lb = len(a), len(b)
    if abs(la - lb) > 1:
        return False
    if la == lb:
        difs = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
        if len(difs) <= 1:
            return True
        return (
            len(difs) == 2
            and difs[1] == difs[0] + 1
            and a[difs[0]] == b[difs[1]]
            and a[difs[1]] == b[difs[0]]
        )
    corta, larga = (a, b) if la < lb else (b, a)
    return any(larga[:i] + larga[i + 1 :] == corta for i in range(len(larga)))


def _cerca(hay: str, patron: str) -> bool:
    """El patrón está en el texto, exacto o con un typo si es largo."""
    if patron in hay:
        return True
    if len(patron) < _MIN_FUZZY or patron in _SOLO_EXACTO:
        return False
    for n in (len(patron) - 1, len(patron), len(patron) + 1):
        for i in range(max(0, len(hay) - n + 1)):
            if _edicion1(hay[i : i + n], patron):
                return True
    return False


_NEGACIONES = (
    "ningun ",
    "ninguna ",
    "no te pide",
    "no pide ",
    "no voy a dar",
    "no voy a pasar",
    "no te pido",
    "no pido ",
    "no saques",
    "no pienso",
)
_IMPERATIVOS = (
    "pasame",
    "decime",
    "dame",
    "mandame",
    "confirmame",
    "transferi",
    "autoriz",
    "instal",
    "compart",
    "necesito que",
    "tenes que",
    "tiene que",
)


def _niega_el_pedido(norm: str) -> bool:
    if not any(_cerca(norm, n) for n in _NEGACIONES):
        return False
    return not any(imp in norm for imp in _IMPERATIVOS)


def incendio_en(texto: str) -> list[str]:
    """Etiquetas de pedido peligroso presentes en el texto. Vacio = sin incendio."""
    norm = _normalizar(texto)
    if not norm or _niega_el_pedido(norm):
        return []
    return [et for et, pals in PATRONES.items() if any(_cerca(norm, p) for p in pals)]
