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
import reglas_v2
from casos import Linea
from cliente_ollama import ClienteOllama, ErrorOllama

DIR_PROMPTS = Path(__file__).resolve().parent / "prompts"
PROMPTS = {
    "tarea": ("tarea.txt",),
    "tarea+base": ("tarea.txt", "base_institucional.txt"),
    "v2": ("tarea_v2.txt",),
    "riesgo": ("riesgo.txt",),  # dos etapas: ver DetectorSLMDosEtapas
}
# Pedido de la segunda etapa de `riesgo`: va como mensaje del usuario, no de sistema.
PROMPT_MOTIVO = "riesgo_motivo.txt"
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
# «Riesgo primero»: la etapa 1 escribe solo el número (~8 tokens en vez de ~40); la etapa 2
# pide la evidencia y el motivo únicamente cuando el riesgo supera el umbral.
ESQUEMA_RIESGO = {
    "type": "object",
    "properties": {"riesgo": ESQUEMA_SALIDA["properties"]["riesgo"]},
    "required": ["riesgo"],
}
ESQUEMA_MOTIVO = {
    "type": "object",
    "properties": {c: ESQUEMA_SALIDA["properties"][c] for c in ("evidencia", "motivo")},
    "required": ["evidencia", "motivo"],
}
ESQUEMAS = {"tarea": ESQUEMA_SALIDA, "tarea+base": ESQUEMA_SALIDA, "v2": ESQUEMA_SALIDA_V2, "riesgo": ESQUEMA_RIESGO}

# Estimación conservadora para no mandar más texto del que entra en el contexto:
# en español, los tokenizadores de estos modelos usan más de 3 caracteres por token.
# Es la única protección contra el recorte: Ollama recorta un prompt largo sin avisar
# y lo que informa después no permite detectarlo con seguridad.
CARACTERES_POR_TOKEN = 3
FRACCION_MAXIMA_DEL_CONTEXTO = 0.9
# Tope de tokens por respuesta: el JSON esperado usa menos de 200. Evita que un modelo
# que entra en bucle tarde minutos en llegar al timeout.
MAXIMO_TOKENS_RESPUESTA = 512
# `{"riesgo": 0.35}` son ~8 tokens; el margen cubre espacios o más decimales.
MAXIMO_TOKENS_RIESGO = 24
UMBRAL_POR_DEFECTO = 0.6


@dataclass
class Respuesta:
    """Lo que un detector dice sobre una actualización. Inválida = fallo, no predicción.

    Los campos de filtro (`consulta`, `tito_*`, `indicio_*`) solo los usa el
    flujo Tito→SLM (#69): en el comparador directo quedan vacíos.
    `tito_ms`/`slm_ms` separan el costo por componente (#97): `ms` es el
    total de la actualización (suma de los componentes que corrieron, sin
    doble conteo). `runtime_ns` es la duración total que informa el runtime
    (Ollama `total_duration`, en nanosegundos); `runtime_unidad` es `"ns"`
    cuando hay dato y `""` cuando no (ausencia explícita).
    `runtime_load_ns`, `runtime_prompt_eval_ns` y `runtime_eval_ns` son las
    demás duraciones que expone el runtime (`load_duration`,
    `prompt_eval_duration`, `eval_duration`, en nanosegundos); cada una es
    `None` cuando el runtime no la informa (ausencia explícita, no cero).
    """

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
    consulta: str = ""
    tito_puntaje: float | None = None
    tito_error: str = ""
    indicio_linea: int | None = None
    indicio_texto: str = ""
    indicio_puntaje: float | None = None
    tito_ms: float | None = None
    slm_ms: float | None = None
    runtime_ns: int | None = None
    runtime_unidad: str = ""
    runtime_load_ns: int | None = None
    runtime_prompt_eval_ns: int | None = None
    runtime_eval_ns: int | None = None
    # Solo con DetectorSLMDosEtapas; `ms` es la suma de las dos etapas.
    ms_etapa1: float | None = None
    ms_etapa2: float | None = None
    tokens_prompt_etapa2: int | None = None
    tokens_salida_etapa2: int | None = None
    crudo_etapa2: str = ""


def cargar_prompt(variante: str) -> str:
    if variante not in PROMPTS:
        raise ValueError(f"prompt desconocido {variante!r}; opciones: {sorted(PROMPTS)}")
    partes = [(DIR_PROMPTS / nombre).read_text(encoding="utf-8").strip() for nombre in PROMPTS[variante]]
    return "\n\n".join(partes)


def esquema_de(variante: str) -> dict:
    if variante not in ESQUEMAS:
        raise ValueError(f"prompt desconocido {variante!r}; opciones: {sorted(ESQUEMAS)}")
    return ESQUEMAS[variante]


def cargar_prompt_motivo() -> str:
    return (DIR_PROMPTS / PROMPT_MOTIVO).read_text(encoding="utf-8").strip()


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

    def mensajes(self, lineas: list[Linea] | tuple[Linea, ...]) -> tuple[list[dict] | None, str]:
        """(mensajes, "") o (None, error) si la transcripción no entra en el contexto."""
        return self._mensajes_de(armar_mensaje_usuario(lineas, self.hablantes))

    def _mensajes_de(self, usuario: str) -> tuple[list[dict] | None, str]:
        estimado = math.ceil((len(self.prompt) + len(usuario)) / CARACTERES_POR_TOKEN)
        if estimado > self.num_ctx * FRACCION_MAXIMA_DEL_CONTEXTO:
            # No se recorta en silencio (#50): se informa como fallo.
            return None, f"contexto_excedido: ~{estimado} tokens > {self.num_ctx}"
        return [{"role": "system", "content": self.prompt}, {"role": "user", "content": usuario}], ""

    def evaluar(self, lineas: list[Linea] | tuple[Linea, ...]) -> Respuesta:
        return self.evaluar_mensaje(armar_mensaje_usuario(lineas, self.hablantes), lineas)

    def evaluar_mensaje(self, usuario: str, lineas: list[Linea] | tuple[Linea, ...]) -> Respuesta:
        """Evalúa un mensaje ya armado (el filtro agrega el bloque de indicio).

        `lineas` es el historial íntegro disponible, para validar la evidencia
        citada sin texto futuro.
        """
        mensajes, error = self._mensajes_de(usuario)
        if mensajes is None:
            return Respuesta(valida=False, error=error)
        inicio = time.perf_counter()
        try:
            r = self.cliente.chat(self.modelo, mensajes, self.esquema or ESQUEMA_SALIDA, self.opciones(), self.pensar)
        except ErrorOllama as e:
            ms_fallo = (time.perf_counter() - inicio) * 1000
            return Respuesta(valida=False, error=str(e), ms=ms_fallo, slm_ms=ms_fallo)
        ms = (time.perf_counter() - inicio) * 1000
        crudo = r.get("message", {}).get("content", "")
        tokens_prompt, tokens_salida = r.get("prompt_eval_count"), r.get("eval_count")

        def _duracion_ns(clave: str) -> int | None:
            """Duración del runtime en ns; None si el runtime no la informa."""
            valor = r.get(clave)
            if isinstance(valor, bool) or not isinstance(valor, (int, float)):
                return None
            return int(valor)

        total_ns = _duracion_ns("total_duration")
        unidad = "ns" if total_ns is not None else ""
        comun = dict(crudo=crudo, ms=ms, slm_ms=ms, tokens_prompt=tokens_prompt,
                     tokens_salida=tokens_salida, runtime_ns=total_ns, runtime_unidad=unidad,
                     runtime_load_ns=_duracion_ns("load_duration"),
                     runtime_prompt_eval_ns=_duracion_ns("prompt_eval_duration"),
                     runtime_eval_ns=_duracion_ns("eval_duration"))
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


def validar_riesgo(crudo: str) -> tuple[float | None, str]:
    """Etapa 1 de `riesgo`: (riesgo, "") o (None, motivo del fallo)."""
    try:
        salida = json.loads(crudo)
    except json.JSONDecodeError:
        return None, "json_invalido"
    if not isinstance(salida, dict):
        return None, "json_no_es_objeto"
    if "riesgo" not in salida:
        return None, "faltan_campos: riesgo"
    riesgo = salida["riesgo"]
    if isinstance(riesgo, bool) or not isinstance(riesgo, (int, float)) or not math.isfinite(riesgo):
        return None, "riesgo_no_numerico"
    if not 0 <= riesgo <= 1:
        return None, "riesgo_fuera_de_rango"
    return float(riesgo), ""


def validar_motivo(crudo: str) -> tuple[dict | None, str]:
    """Etapa 2 de `riesgo`: ({evidencia, motivo}, "") o (None, motivo del fallo)."""
    try:
        salida = json.loads(crudo)
    except json.JSONDecodeError:
        return None, "json_invalido"
    if not isinstance(salida, dict):
        return None, "json_no_es_objeto"
    faltan = [c for c in ESQUEMA_MOTIVO["required"] if c not in salida]
    if faltan:
        return None, f"faltan_campos: {','.join(faltan)}"
    if not isinstance(salida["motivo"], str) or not isinstance(salida["evidencia"], str):
        return None, "motivo_o_evidencia_no_texto"
    if not salida["motivo"].strip():
        return None, "alerta_sin_motivo"
    return salida, ""


@dataclass
class DetectorSLMDosEtapas(DetectorSLM):
    """«Riesgo primero»: la etapa 1 escribe solo `{"riesgo": x}` y, si x ≤ umbral, la línea
    termina ahí. Si x > umbral, la alerta queda decidida y la etapa 2 pide evidencia y
    motivo para armar el aviso.

    La etapa 2 repite los mensajes de la 1, agrega su respuesta como `assistant` y el pedido
    corto: el comienzo es idéntico y Ollama puede reutilizar la transcripción ya procesada.
    Como el aviso es único por llamada, la etapa 2 corre solo la primera vez que se supera el
    umbral; después se registran el riesgo y la alerta sin motivo. `reiniciar()` (lo llama
    `correr.procesar_caso` al empezar cada caso) vuelve a habilitarla.
    Si la etapa 2 falla, la alerta se mantiene (el riesgo ya la decidió) y el error queda
    en `error` con el prefijo `etapa2_`, sin motivo ni evidencia.
    """

    umbral: float = UMBRAL_POR_DEFECTO
    pedido_motivo: str = ""
    nombre = "slm"

    def __post_init__(self) -> None:
        self.pedido_motivo = self.pedido_motivo or cargar_prompt_motivo()
        self.reiniciar()

    def reiniciar(self) -> None:
        """Nueva llamada: la próxima línea sobre el umbral vuelve a pedir evidencia y motivo."""
        self._alerto = False

    def _opciones(self, num_predict: int) -> dict:
        return {**self.opciones(), "num_predict": num_predict}

    def evaluar(self, lineas: list[Linea] | tuple[Linea, ...]) -> Respuesta:
        mensajes, error = self.mensajes(lineas)
        if mensajes is None:
            return Respuesta(valida=False, error=error)
        inicio = time.perf_counter()
        try:
            r1 = self.cliente.chat(self.modelo, mensajes, ESQUEMA_RIESGO, self._opciones(MAXIMO_TOKENS_RIESGO), self.pensar)
        except ErrorOllama as e:
            return Respuesta(valida=False, error=str(e), ms=(time.perf_counter() - inicio) * 1000)
        ms1 = (time.perf_counter() - inicio) * 1000
        crudo1 = r1.get("message", {}).get("content", "")
        comun = dict(crudo=crudo1, ms=ms1, ms_etapa1=ms1, tokens_prompt=r1.get("prompt_eval_count"), tokens_salida=r1.get("eval_count"))
        if r1.get("done_reason") == "length":
            return Respuesta(valida=False, error="salida_cortada", **comun)
        riesgo, error = validar_riesgo(crudo1)
        if riesgo is None:
            return Respuesta(valida=False, error=error, **comun)
        if riesgo <= self.umbral:
            return Respuesta(valida=True, riesgo=riesgo, alerta_sugerida=False, **comun)
        if self._alerto:
            return Respuesta(valida=True, riesgo=riesgo, alerta_sugerida=True, **comun)
        self._alerto = True

        mensajes2 = mensajes + [{"role": "assistant", "content": crudo1}, {"role": "user", "content": self.pedido_motivo}]
        inicio2 = time.perf_counter()
        try:
            r2 = self.cliente.chat(self.modelo, mensajes2, ESQUEMA_MOTIVO, self._opciones(MAXIMO_TOKENS_RESPUESTA), self.pensar)
        except ErrorOllama as e:
            ms2 = (time.perf_counter() - inicio2) * 1000
            comun.update(ms=ms1 + ms2, ms_etapa2=ms2)
            return Respuesta(valida=True, riesgo=riesgo, alerta_sugerida=True, error=f"etapa2_{e}", **comun)
        ms2 = (time.perf_counter() - inicio2) * 1000
        crudo2 = r2.get("message", {}).get("content", "")
        comun.update(
            ms=ms1 + ms2, ms_etapa2=ms2, crudo_etapa2=crudo2,
            tokens_prompt_etapa2=r2.get("prompt_eval_count"), tokens_salida_etapa2=r2.get("eval_count"),
        )
        salida, error = validar_motivo(crudo2) if r2.get("done_reason") != "length" else (None, "salida_cortada")
        if salida is None:
            return Respuesta(valida=True, riesgo=riesgo, alerta_sugerida=True, error=f"etapa2_{error}", **comun)
        return Respuesta(
            valida=True,
            riesgo=riesgo,
            alerta_sugerida=True,
            motivo=salida["motivo"].strip(),
            evidencia=salida["evidencia"].strip(),
            evidencia_en_texto=evidencia_en_texto(salida["evidencia"], lineas),
            **comun,
        )


class DetectorReglas:
    """Reglas del laboratorio sobre la línea nueva. No usan hablantes.

    v1 (por defecto) es el comparador del laboratorio. v2 (reglas_v2.py) exige además que el
    pedido vaya dirigido a la otra persona. Las dos miran solo la línea nueva.
    """

    def __init__(self, version: str = "v1") -> None:
        if version not in ("v1", "v2"):
            raise ValueError(f"Versión de reglas desconocida: {version!r}")
        self.version = version
        self.nombre = "reglas" if version == "v1" else "reglas_v2"

    def evaluar(self, lineas: list[Linea] | tuple[Linea, ...]) -> Respuesta:
        inicio = time.perf_counter()
        if self.version == "v1":
            hallazgos = reglas.coincidencias(lineas[-1].texto)
        else:
            hallazgos = reglas_v2.coincidencias_v2(lineas[-1].texto)
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
