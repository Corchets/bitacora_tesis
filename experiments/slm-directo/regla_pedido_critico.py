"""Regla de pedido crítico: avisa cuando OTRA le pide a PROTEGIDA algo que la política dice no darle nunca a quien
llamó (corridas/2026-11-10_revision-producto/POLITICA.md §2 y §4).

> **Estado: propuesta sin discutir.** Exploración posterior a la evaluación final (Luciano, 2026-11-20), solo en
> `laboratorio-luciano`. Se escribió y se ajustó después de leer los fallos del test reservado y de desarrollo: sus
> cifras no valen como test.

Se suma al modelo, no lo reemplaza: el híbrido avisa en la primera línea en que avisa cualquiera de los dos.

Una línea de OTRA dispara con uno de estos pedidos, si no es una advertencia («no compartas el código», «no tenés que
mandarnos nada»):
- **dictar** un código, una clave o un PIN a OTRA: «decime el código», «leeme los seis dígitos», «¿me lo pasás?». Un
  código que se carga en la propia app no cuenta (POLITICA.md §4); una clave o contraseña que se escribe donde dice
  OTRA, sí;
- **los datos de la tarjeta;**
- **transferir, depositar o pagar** (pedir un alias para mandarle plata a PROTEGIDA no cuenta);
- **acceso remoto:** instalar un programa, AnyDesk, compartir la pantalla;
- **foto del documento, selfie o número de trámite.**

El objeto puede estar en las dos líneas anteriores solo si la frase lo retoma con un pronombre: «decímelo»,
«pasámela», «me lo leés». El número de DNI, el nombre o la dirección no son objetos críticos (POLITICA.md §3).
"""

from __future__ import annotations

import re

from reglas_v2 import _anulado_por_advertencia, _limpiar

VENTANA = 2  # líneas anteriores en las que se busca el objeto retomado por un pronombre

# Se busca sobre el texto en minúsculas y sin puntuación, con acentos: «pagá» es un pedido; «está paga», no. Las formas
# con pronombre («pasame», «decímelo») no dependen del acento y se buscan también sin él.
_SECRETO = (r"c[oó]digos?|d[ií]gitos|n[uú]meros(?! (?:de|del) (?:tu |su |el |la )?(?:dni|documento|tel[eé]fono|celular))"
            r"|token|otp|claves?|contrase[nñ]as?|password|pin|cvv")
_TARJETA = r"(?:n[uú]meros?|datos|vencimiento|c[oó]digo de seguridad) de (?:la |tu )?tarjeta|vencimiento|cvv"
_ME = r"(?:me|nos|melo|mela|melos|melas)"
_DICTAR = (rf"(?:dec[ií]|le[eé]|pas[aá]|dict[aá]|mand[aá]|confirm[aá]|compart[ií]|repet[ií]|envi[aá]|escrib[ií]|copi[aá]){_ME}"
           r"|me (?:lo |la |los |las )?(?:dec[ií]s|le[eé]s|pas[aá]s|dict[aá]s|mand[aá]s|confirm[aá]s|compart[ií]s|repet[ií]s)"
           r"|(?:necesito|necesitamos|ten[eé]s que) (?:que )?(?:me |nos )?(?:digas|leas|pases|dictes|confirmes|des)")
_RETOMA = (r"(?:dec[ií]|le[eé]|pas[aá]|dict[aá]|mand[aá]|confirm[aá]|repet[ií]|envi[aá])(?:melo|mela|melos|melas)"
           r"|me (?:lo|la|los|las) (?:dec[ií]s|le[eé]s|pas[aá]s|dict[aá]s|mand[aá]s|confirm[aá]s)")
_ESCRIBIR_CLAVE = (r"(?:ingres[aá]|escrib[ií]|pon[eé]|carg[aá]|tipe[aá])(?:la|lo)\b"
                   r"|(?:ingresá|escribí|poné|cargá|tipeá) (?:\w+ ){0,3}?(?:clave|contrase[nñ]a|password|pin)")
_TRANSFERIR = (r"transfer[ií](?:me|nos|le)|transferí|deposit[aá](?:me|nos|le)|depositá|pag[aá](?:me|nos|le)|pagá|aboná"
               r"|me (?:transfer[ií]s|deposit[aá]s|pag[aá]s|gir[aá]s)|hac[eé] (?:la|una) transferencia"
               r"|mand[aá]me (?:la )?plata|(?:necesito|ten[eé]s) que (?:me )?(?:transfieras|deposites|pagues|abones|transferir|depositar|pagar)")
_REMOTO = (r"compart[ií](?:me|nos)? (?:la )?pantalla|(?:dame|darme|habilitame|habilitá|necesito) (?:el )?acceso remoto"
           r"|(?:instalá|descargá|bajá|abrí|instal[aá]te|descarg[aá]te|baj[aá]te) (?:la |una |el |este |esta )?"
           r"(?:app|aplicaci[oó]n|programa|anydesk|teamviewer)")
_DOCUMENTO = (r"(?:mand[aá]|envi[aá]|sac[aá])(?:me|nos)? (?:una )?(?:foto (?:del|de tu) (?:dni|documento)|selfie)"
              r"|(?:dec[ií]|pas[aá]|dict[aá])(?:me|nos) el n[uú]mero de tr[aá]mite")

_P = lambda r: re.compile(rf"(?<!\w)(?:{r})(?!\w)")  # noqa: E731
_OBJETOS = {"secreto": _P(_SECRETO), "tarjeta": _P(_TARJETA)}
_DICTAR_RE, _RETOMA_RE, _ESCRIBIR = _P(_DICTAR), _P(_RETOMA), _P(_ESCRIBIR_CLAVE)
_SOLOS = {"transferencia": _P(_TRANSFERIR), "acceso_remoto": _P(_REMOTO), "documento": _P(_DOCUMENTO)}
_NO_HACE_FALTA = ("no tenes que", "no tiene que", "no hace falta", "no necesitas", "no necesitamos", "no sirve")


def _con_acentos(texto: str) -> str:
    return " ".join(re.sub(r"[^\w ]", " ", texto.lower()).split())


def dispara(lineas: list[tuple[str, str]], i: int) -> list[str]:
    """Pedidos críticos de la línea i, o [] si no dispara. `lineas` son (rol, texto), con rol OTRA o PROTEGIDA."""
    rol, texto = lineas[i]
    norm = _limpiar(texto)
    if rol != "OTRA" or not norm or _anulado_por_advertencia(norm) or any(n in norm for n in _NO_HACE_FALTA):
        return []
    linea = _con_acentos(texto)
    previas = " ".join(_con_acentos(t) for _, t in lineas[max(0, i - VENTANA): i])
    salida = set()
    if _DICTAR_RE.search(linea):
        for nombre, objeto in _OBJETOS.items():
            if objeto.search(linea) or (_RETOMA_RE.search(linea) and objeto.search(previas)):
                salida.add(nombre)
    if _ESCRIBIR.search(linea) and (_OBJETOS["secreto"].search(linea) or _OBJETOS["secreto"].search(previas)):
        salida.add("secreto")
    salida |= {nombre for nombre, r in _SOLOS.items() if r.search(linea)}
    return sorted(salida)


def primer_pedido(lineas: list[tuple[str, str]]) -> tuple[int, list[str]] | None:
    """(línea, 1-based, y pedidos) del primer disparo, o None."""
    for i in range(len(lineas)):
        if p := dispara(lineas, i):
            return i + 1, p
    return None
