"""Reglas v2: los mismos patrones de reglas.py, pero solo si el pedido va dirigido a la otra persona.

La v1 prende con nombrar la palabra («clave», «pago», «código») en cualquier lugar: relatos,
preguntas, advertencias y hasta pedazos de otras palabras («pintando» por «pin»). La v2 agrega
tres filtros sobre la misma lógica de patrones y deja reglas.py intacta (las corridas viejas
se reproducen igual):

1. Palabra entera: el patrón empieza donde empieza una palabra y termina donde termina,
   salvo las raíces de _RAICES («transferi» vale para «transferime»). El typo de un solo
   carácter de la v1 se mantiene para patrones de 6+ letras.
2. Pedido dirigido: la línea tiene que traer un imperativo, un «necesito que / tenés que» o un «¿me podés...?». Sin eso es una mención.
3. Advertencia: «nunca», «no te vamos a pedir», «no compartas» anulan el aviso, salvo que
   haya un imperativo con «-me» («no cortes y decime el código»).

Nada de esto usa quién habla: A y B pueden ser el estafador o la víctima.

> **Estado: propuesta sin discutir.** Afinada mirando casos de desarrollo; no fija umbrales
> ni política (D07, D08 abiertas).
"""

import re

from reglas import _MIN_FUZZY, _SOLO_EXACTO, PATRONES, _edicion1, _normalizar

_RAICES = frozenset({"transferi", "instala", "autoriza", "abri el enlace"})

# Imperativos con «-me / -melo» (el pedido a «mí»: pasame, decime, deme) y en voseo seguidos
# de lo pedido («abrí el enlace»). Sin acentos, porque _normalizar los saca.
_VERBOS = (
    "pasa|deci|di|da|de|manda|confirma|lee|envia|mostra|comparti|transferi|abri|dicta|repeti|"
    "indica|escribi|ingresa|descarga|instala|autoriza|saca|deposita|gira|cambia"
)
_VOSEO = "pasa|deci|manda|confirma|lee|envia|comparti|transferi|abri|dicta|ingresa|descarga|instala|autoriza|deposita|cambia"
_CLITICO = rf"(?<!\w)(?:{_VERBOS})(?:me|melo|mela|melos|nos)(?!\w)"
_DIRIGIDO = re.compile(
    rf"{_CLITICO}"
    rf"|(?<!\w)(?:abri|pasa|manda|deci)(?:lo|la)(?!\w)"
    rf"|(?<!\w)(?:{_VOSEO}) (?:el|la|los|las|tu|ese|esa|a este)\b"
    r"|(?<!\w)para que (?:me|nos) (?:compartas|pases|des|digas|mandes|confirmes|envies|leas|transfieras)\b"
    r"|(?<!\w)(?:necesito|necesitamos|queremos|quiero) que\b"
    r"|(?<!\w)(?:tenes|tiene|tienen|debe|debes|hay) que\b"
    r"|(?<!\w)te (?:voy a |vamos a )?(?:pido|pedimos|pedir)\b"
    r"|(?<!\w)me (?:lo |la |los |las )?(?:podes|podrias|pasas|das|confirmas|decis|mandas|envias|lees|transferis|giras)\b"
)
_IMPERATIVO_ME = re.compile(_CLITICO)
_ADVERTENCIA = (
    "nunca ", "jamas ", "ningun ", "ninguna ", "no te vamos a pedir", "no te voy a pedir", "tampoco te voy a pedir",
    "no te pedimos", "no te pide", "no te pido", "no compartas", "no le pases", "no pases",
    "no des ", "no le des ", "no se la pase", "no voy a dar", "no voy a pasar", "no pienso",
    "no pongas", "no digas", "no mandes", "no ingreses", "no instales", "no abras",
)


def _palabra(hay: str, patron: str) -> bool:
    """El patrón está como palabra entera (o raíz), exacto o con un typo si es largo."""
    raiz = patron in _RAICES
    fuzzy = len(patron) >= _MIN_FUZZY and patron not in _SOLO_EXACTO
    largos = (len(patron) - 1, len(patron), len(patron) + 1) if fuzzy else (len(patron),)
    for i in range(len(hay)):
        if i and hay[i - 1] != " ":
            continue
        for n in largos:
            trozo = hay[i : i + n]
            if i + n > len(hay) or not (_edicion1(trozo, patron) if fuzzy else trozo == patron):
                continue
            resto = hay[i + n :]
            if raiz or not resto or resto[0] == " " or (resto[0] == "s" and resto[1:2] in ("", " ")):
                return True
    return False


def _limpiar(texto: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", _normalizar(texto)).split())


def _anulado_por_advertencia(norm: str) -> bool:
    return any(a in norm + " " for a in _ADVERTENCIA) and not _IMPERATIVO_ME.search(norm)


def coincidencias_v2(texto: str) -> list[tuple[str, str]]:
    """(etiqueta, patrón) que disparan: patrón de palabra entera en una línea con pedido dirigido."""
    norm = _limpiar(texto)
    if not norm or _anulado_por_advertencia(norm):
        return []
    if not _DIRIGIDO.search(norm):
        return []
    return [(et, p) for et, pals in PATRONES.items() for p in pals if _palabra(norm, p)]
