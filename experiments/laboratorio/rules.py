"""Reglas de incendio: lista de trabajo sobre el borrador.

D07 sigue abierta: esto no congela la taxonomia, solo permite correr #29.
"""

import unicodedata

PATRONES = {
    "REQUEST_AUTH_CODE": ["codigo", "otp", "token", "whatsapp", "verificacion", "seis digitos"],
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


def incendio_en(texto: str) -> list[str]:
    """Etiquetas de pedido peligroso presentes en el texto. Vacio = sin incendio."""
    norm = _normalizar(texto)
    if not norm:
        return []
    return [et for et, pals in PATRONES.items() if any(p in norm for p in pals)]
