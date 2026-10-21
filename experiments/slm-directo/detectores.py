"""Detectores del ensayo #50: SLM local directo y reglas como comparador.

Los dos reciben lo mismo, la lista de líneas disponibles hasta ese momento de UNA
llamada, y devuelven una `Respuesta`. Nunca reciben la referencia humana: ni la
clase, ni el escenario, ni las marcas. El `case_id` tampoco les llega.

> Estado: propuesta sin discutir. No cierra D08 ni D09.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import time
import unicodedata
from dataclasses import dataclass
from pathlib import Path

import reglas
from casos import Linea
from cliente_ollama import ClienteOllama, ErrorOllama

DIR_PROMPTS = Path(__file__).resolve().parent / "prompts"
PROMPTS = {
    "tarea": ("tarea.txt",),
    "tarea+base": ("tarea.txt", "base_institucional.txt"),
    "v2": ("tarea_v2.txt",),
}
HABLANTES = ("ab", "sin")

# Forma obligatoria de cada respuesta del SLM. Ollama la usa para forzar la salida;
# igual se valida acá, porque un modelo chico puede devolver algo que no cumple.
ESQUEMA_SALIDA = {
    "type": "object",
    "properties": {
        "riesgo": {"type": "number", "minimum": 0, "maximum": 1},
        "alerta_sugerida": {"type": "boolean"},
        "motivo": {"type": "string"},
        "evidencia": {"type": "string"},
    },
    "required": ["riesgo", "alerta_sugerida", "motivo", "evidencia"],
}
# El v2 pide la cita antes de decidir: Ollama genera los campos en el orden del esquema.
ESQUEMA_SALIDA_V2 = {
    "type": "object",
    "properties": {c: ESQUEMA_SALIDA["properties"][c] for c in ("evidencia", "alerta_sugerida", "riesgo", "motivo")},
    "required": ["evidencia", "alerta_sugerida", "riesgo", "motivo"],
}
ESQUEMAS = {"tarea": ESQUEMA_SALIDA, "tarea+base": ESQUEMA_SALIDA, "v2": ESQUEMA_SALIDA_V2}

# Estimación conservadora para no mandar más texto del que entra en el contexto:
# en español, los tokenizadores de estos modelos usan más de 3 caracteres por token.
# Es la única protección contra el recorte: Ollama recorta un prompt largo sin avisar
# y lo que informa después no permite detectarlo con seguridad.
CARACTERES_POR_TOKEN = 3
FRACCION_MAXIMA_DEL_CONTEXTO = 0.9
# Tope de tokens por respuesta: el JSON esperado usa menos de 200. Evita que un modelo
# que entra en bucle tarde minutos en llegar al timeout.
MAXIMO_TOKENS_RESPUESTA = 512


@dataclass
class Respuesta:
    """Lo que un detector dice sobre una actualización. Inválida = fallo, no predicción."""

    valida: bool
    error: str = ""
    riesgo: float | None = None
    alerta_sugerida: bool | None = None
    motivo: str = ""
    evidencia: str = ""
    evidencia_en_texto: bool | None = None
    crudo: str = ""
    ms: float | None = None
    tokens_prompt: int | None = None
    tokens_salida: int | None = None


def cargar_prompt(variante: str) -> str:
    if variante not in PROMPTS:
        raise ValueError(f"prompt desconocido {variante!r}; opciones: {sorted(PROMPTS)}")
    partes = [(DIR_PROMPTS / nombre).read_text(encoding="utf-8").strip() for nombre in PROMPTS[variante]]
    return "\n\n".join(partes)


def esquema_de(variante: str) -> dict:
    if variante not in ESQUEMAS:
        raise ValueError(f"prompt desconocido {variante!r}; opciones: {sorted(ESQUEMAS)}")
    return ESQUEMAS[variante]


def huella(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()[:16]


def armar_mensaje_usuario(lineas: list[Linea] | tuple[Linea, ...], hablantes: str) -> str:
    """Transcripción disponible, numerada. Con `sin`, las letras A/B no llegan al modelo."""
    if hablantes not in HABLANTES:
        raise ValueError(f"hablantes desconocido {hablantes!r}; opciones: {HABLANTES}")
    n = len(lineas)
    if hablantes == "ab":
        aclaracion = (
            "Cada línea indica quién habla con A o B. A es quien habló primero; "
            "las letras no indican quién llamó ni quién es sospechoso."
        )
        cuerpo = "\n".join(f"{i}. {l.hablante}: {l.texto}" for i, l in enumerate(lineas, start=1))
    else:
        aclaracion = "Las líneas no indican quién habla."
        cuerpo = "\n".join(f"{i}. {l.texto}" for i, l in enumerate(lineas, start=1))
    # El número de líneas va solo al final: así el comienzo del mensaje es igual entre
    # actualizaciones y Ollama puede reutilizar lo ya procesado.
    return (
        f"Transcripción disponible hasta ahora; la llamada sigue. {aclaracion}\n\n"
        f"{cuerpo}\n\n"
        f"Evaluá la llamada con lo disponible hasta la línea {n}."
    )


def _normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFD", texto.lower())
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    texto = re.sub(r"[^\w\s]", " ", texto)
    return " ".join(texto.split())


def evidencia_en_texto(evidencia: str, lineas: list[Linea] | tuple[Linea, ...]) -> bool:
    """True si la evidencia citada aparece en lo disponible (sin contar acentos, signos,
    numeración ni la letra del hablante). Detecta citas inventadas o parafraseadas.

    Si el modelo cita varias líneas (una por renglón, a veces con «2. B:» adelante),
    cada renglón tiene que aparecer en lo dicho.
    """
    disponible = " ".join(_normalizar(l.texto) for l in lineas)
    partes = []
    for renglon in evidencia.splitlines():
        cita = _normalizar(renglon)
        cita = re.sub(r"^\d+\s+", "", cita)
        cita = re.sub(r"^[ab]\s+", "", cita)
        if cita:
            partes.append(cita)
    return bool(partes) and all(cita in disponible for cita in partes)


def validar_salida(crudo: str) -> tuple[dict | None, str]:
    """(salida, "") si cumple el esquema; (None, motivo del fallo) si no."""
    try:
        salida = json.loads(crudo)
    except json.JSONDecodeError:
        return None, "json_invalido"
    if not isinstance(salida, dict):
        return None, "json_no_es_objeto"
    faltan = [c for c in ESQUEMA_SALIDA["required"] if c not in salida]
    if faltan:
        return None, f"faltan_campos: {','.join(faltan)}"
    riesgo = salida["riesgo"]
    if isinstance(riesgo, bool) or not isinstance(riesgo, (int, float)) or not math.isfinite(riesgo):
        return None, "riesgo_no_numerico"
    if not 0 <= riesgo <= 1:
        return None, "riesgo_fuera_de_rango"
    if not isinstance(salida["alerta_sugerida"], bool):
        return None, "alerta_no_booleana"
    if not isinstance(salida["motivo"], str) or not isinstance(salida["evidencia"], str):
        return None, "motivo_o_evidencia_no_texto"
    if salida["alerta_sugerida"] and not salida["motivo"].strip():
        return None, "alerta_sin_motivo"
    return salida, ""


@dataclass
class DetectorSLM:
    cliente: ClienteOllama
    modelo: str
    prompt: str
    hablantes: str = "ab"
    num_ctx: int = 4096
    seed: int = 42
    temperatura: float = 0.0
    pensar: bool | None = None  # False: sin razonamiento previo; None: no se envía (ver correr.calentar)
    extra: dict | None = None  # opciones de hardware de Ollama, p. ej. {"num_gpu": 0, "num_thread": 2}
    esquema: dict | None = None  # None: ESQUEMA_SALIDA (prompt v1)
    nombre = "slm"

    def opciones(self) -> dict:
        return {
            "temperature": self.temperatura,
            "seed": self.seed,
            "num_ctx": self.num_ctx,
            "num_predict": MAXIMO_TOKENS_RESPUESTA,
            **(self.extra or {}),
        }

    def evaluar(self, lineas: list[Linea] | tuple[Linea, ...]) -> Respuesta:
        usuario = armar_mensaje_usuario(lineas, self.hablantes)
        estimado = math.ceil((len(self.prompt) + len(usuario)) / CARACTERES_POR_TOKEN)
        if estimado > self.num_ctx * FRACCION_MAXIMA_DEL_CONTEXTO:
            # No se recorta en silencio (#50): se informa como fallo.
            return Respuesta(valida=False, error=f"contexto_excedido: ~{estimado} tokens > {self.num_ctx}")
        mensajes = [{"role": "system", "content": self.prompt}, {"role": "user", "content": usuario}]
        inicio = time.perf_counter()
        try:
            r = self.cliente.chat(self.modelo, mensajes, self.esquema or ESQUEMA_SALIDA, self.opciones(), self.pensar)
        except ErrorOllama as e:
            return Respuesta(valida=False, error=str(e), ms=(time.perf_counter() - inicio) * 1000)
        ms = (time.perf_counter() - inicio) * 1000
        crudo = r.get("message", {}).get("content", "")
        tokens_prompt, tokens_salida = r.get("prompt_eval_count"), r.get("eval_count")
        comun = dict(crudo=crudo, ms=ms, tokens_prompt=tokens_prompt, tokens_salida=tokens_salida)
        if r.get("done_reason") == "length":
            return Respuesta(valida=False, error="salida_cortada", **comun)
        salida, error = validar_salida(crudo)
        if salida is None:
            return Respuesta(valida=False, error=error, **comun)
        alerta = salida["alerta_sugerida"]
        return Respuesta(
            valida=True,
            riesgo=float(salida["riesgo"]),
            alerta_sugerida=alerta,
            motivo=salida["motivo"].strip(),
            evidencia=salida["evidencia"].strip(),
            evidencia_en_texto=evidencia_en_texto(salida["evidencia"], lineas) if alerta else None,
            **comun,
        )


class DetectorReglas:
    """Reglas del laboratorio sobre la línea nueva. No usan contexto ni hablantes."""

    nombre = "reglas"

    def evaluar(self, lineas: list[Linea] | tuple[Linea, ...]) -> Respuesta:
        inicio = time.perf_counter()
        hallazgos = reglas.coincidencias(lineas[-1].texto)
        ms = (time.perf_counter() - inicio) * 1000
        if not hallazgos:
            return Respuesta(valida=True, alerta_sugerida=False, ms=ms)
        etiquetas = sorted({et for et, _ in hallazgos})
        patrones = sorted({p for _, p in hallazgos})
        return Respuesta(
            valida=True,
            alerta_sugerida=True,
            motivo=f"{', '.join(etiquetas)} (patrón: {', '.join(patrones)})",
            evidencia=lineas[-1].texto,
            evidencia_en_texto=True,
            ms=ms,
        )
