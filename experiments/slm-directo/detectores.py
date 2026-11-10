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
    "v3": ("tarea_v3.txt",),
    "v3-orden-v1": ("tarea_v3_orden_v1.txt",),
    "v4": ("tarea_v4.txt",),
    "v4-cita-libre": ("tarea_v4_cita_libre.txt",),
    "v5-maniobras": ("tarea_v5_maniobras.txt",),
    "v5-indirectos": ("tarea_v5_indirectos.txt",),
    "v5-sin-excepcion": ("tarea_v5_sin_excepcion.txt",),
    "v5": ("tarea_v5.txt",),
    "riesgo": ("riesgo.txt",),  # dos etapas: ver DetectorSLMDosEtapas
    # #143: pregunta SÍ/NO en lugar del JSON. Se leen con DetectorSLMSiNo (probabilidad
    # del primer token), no con un esquema. Ver prompts/README.md.
    # Humo 1 (descartados: el modelo empieza «al…» en vez de SÍ cuando quiere avisar).
    "tarea-sino": ("tarea_sino.txt",),
    "v4-sino": ("tarea_v4_sino.txt",),
    "v4-sin-reglas-sino": ("tarea_v4_sin_reglas_sino.txt",),
    # A1 (solo formato) y A2 (intención), como los define #143.
    "tarea-a1": ("tarea_a1.txt",),
    "v4-a1": ("tarea_v4_a1.txt",),
    "v4-a2": ("tarea_v4_a2.txt",),
    # Segunda vuelta (2026-11-06): el prompt S, más simple, con tres salidas sobre el mismo
    # cuerpo, y v4 con el riesgo como un dígito. Las preguntas de token van al final del
    # mensaje del usuario (PREGUNTAS_FINALES), no en el de sistema.
    "s-json": ("tarea_s.txt", "salida_json_s.txt"),
    "s-sino": ("tarea_s.txt",),
    "s-digito": ("tarea_s.txt",),
    "v4-digito": ("tarea_v4_d.txt",),
    # v4-L: el JSON de v4 tal cual (mismo prompt, mensaje y esquema), cortado después del primer
    # decimal del riesgo; se lee la distribución de ese dígito (DetectorSLMLecturaJSON).
    "v4-lectura": ("tarea_v4.txt",),
    # Alcance del 2026-11-06: el detector corre solo en llamadas entrantes de números no agendados,
    # y el prompt lo dice. `v4-premisa` es v4 con esa sola oración más; C mira la llamada entera y
    # su intención en vez del momento del pedido, con las mismas tres salidas que S.
    "v4-premisa": ("tarea_v4_premisa.txt",),
    "c-json": ("tarea_c.txt", "salida_json_c.txt"),
    "c-sino": ("tarea_c.txt",),
    "c-digito": ("tarea_c.txt",),
    # Etapa 3 de #143 (Mateo, 2026-11-09): el mismo texto de tarea de C con un JSON más corto, en una sola consulta por
    # línea. «C sin alerta» pide solo el riesgo; «C con campo» pide `pedido_critico` y después el riesgo.
    "c-sin-alerta": ("tarea_c.txt", "salida_json_c_sin_alerta.txt"),
    "c-con-campo": ("tarea_c.txt", "salida_json_c_con_campo.txt"),
}
# Decisión del equipo (2026-11-07, ADR 0006): un prompt JSON con ESQUEMA_SALIDA tal cual (mismo prompt, mensaje
# y esquema), cortado con num_predict después del valor de `alerta_sugerida`; avisa con «riesgo ≥ 0,4 o alerta»
# y pide motivo y evidencia en una segunda consulta, solo en la línea del aviso (DetectorSLMJSONCortado). Mateo
# lo adoptó para todas las pruebas, así que la etapa 2 de #143 corta también `v4-premisa` y `c-json`.
CORTE_DE = {"v4-corte": "v4", "v4-premisa-corte": "v4-premisa", "c-json-corte": "c-json"}
PROMPTS.update({corte: PROMPTS[base] for corte, base in CORTE_DE.items()})
PROMPTS_SINO = frozenset({"tarea-sino", "v4-sino", "v4-sin-reglas-sino", "tarea-a1", "v4-a1", "v4-a2", "s-sino", "c-sino"})
# Se leen con DetectorSLMDigito: un número del 0 al 9 en el primer token.
PROMPTS_DIGITO = frozenset({"s-digito", "v4-digito", "c-digito"})
# Se leen con DetectorSLMLecturaJSON: el primer decimal del riesgo dentro del JSON.
PROMPTS_LECTURA = frozenset({"v4-lectura"})
PROMPTS_TOKEN = PROMPTS_SINO | PROMPTS_DIGITO | PROMPTS_LECTURA
# Se leen con DetectorSLMJSONCortado: riesgo y alerta del JSON cortado, sin logprobs.
PROMPTS_CORTE = frozenset(CORTE_DE)
# Se leen con DetectorSLMCCorto: el JSON entero, que el modelo cierra solo, y el motivo de C aparte.
PROMPTS_C_CORTO = frozenset({"c-sin-alerta", "c-con-campo"})
# Última oración del mensaje del usuario, después de la transcripción; `{n}` es la última línea.
# Los prompts de PREGUNTAS_FINALES la reemplazan por su pregunta, para que sea lo último que
# lee el modelo antes de responder.
CIERRE_POR_DEFECTO = "Evaluá la llamada con lo disponible hasta la línea {n}."
PREGUNTAS_FINALES = {
    "s-sino": "pregunta_s_sino.txt",
    "s-digito": "pregunta_s_digito.txt",
    "v4-digito": "pregunta_v4_digito.txt",
    "c-sino": "pregunta_c_sino.txt",
    "c-digito": "pregunta_c_digito.txt",
}
# Pedido de la segunda etapa de `riesgo`: va como mensaje del usuario, no de sistema.
PROMPT_MOTIVO = "riesgo_motivo.txt"
# Pedido de motivo y evidencia de los prompts cortados (PROMPTS_CORTE): el aviso puede salir por la alerta
# escrita con riesgo < 0,4, así que no dice que el riesgo superó el umbral. No nombra a v4.
PROMPT_MOTIVO_CORTE = "motivo_v4_corte.txt"
# Motivo propio de C (Mateo, 2026-11-09), para PROMPTS_C_CORTO: la frase de OTRA que más lo muestra y por qué puede ser
# una estafa. Nombra un pedido solo si ya ocurrió, porque C avisa antes del pedido.
PROMPT_MOTIVO_C = "motivo_c_corte.txt"
HABLANTES = ("ab", "rol", "sin")
ROLES_HABLANTE = ("PROTEGIDA", "OTRA")

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
# «C con campo» (etapa 3 de #143): primero si hay un pedido crítico y después el riesgo.
ESQUEMA_CON_CAMPO = {
    "type": "object",
    "properties": {"pedido_critico": {"type": "boolean"}, "riesgo": ESQUEMA_SALIDA["properties"]["riesgo"]},
    "required": ["pedido_critico", "riesgo"],
}
ESQUEMAS = {"tarea": ESQUEMA_SALIDA, "tarea+base": ESQUEMA_SALIDA, "v2": ESQUEMA_SALIDA_V2, "v3": ESQUEMA_SALIDA_V2, "v3-orden-v1": ESQUEMA_SALIDA, "v4": ESQUEMA_SALIDA, "v4-cita-libre": ESQUEMA_SALIDA, "v5-maniobras": ESQUEMA_SALIDA, "v5-indirectos": ESQUEMA_SALIDA, "v5-sin-excepcion": ESQUEMA_SALIDA, "v5": ESQUEMA_SALIDA, "riesgo": ESQUEMA_RIESGO, "s-json": ESQUEMA_SALIDA, "c-json": ESQUEMA_SALIDA, "v4-premisa": ESQUEMA_SALIDA}
ESQUEMAS.update(dict.fromkeys(PROMPTS_SINO | PROMPTS_DIGITO))  # sin esquema: respuesta libre de un token
ESQUEMAS["v4-lectura"] = ESQUEMA_SALIDA  # el mismo JSON que v4, cortado después del riesgo
ESQUEMAS.update({corte: ESQUEMAS[base] for corte, base in CORTE_DE.items()})  # el mismo JSON, cortado después de alerta_sugerida
ESQUEMAS.update({"c-sin-alerta": ESQUEMA_RIESGO, "c-con-campo": ESQUEMA_CON_CAMPO})

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

# Lectura del token «SÍ» (#143). Ollama acepta hasta 20 alternativas por posición.
TOP_LOGPROBS = 20
# Variantes de tokenización, comparadas sin espacios ni signos alrededor, sin tildes y en
# mayúsculas: «Sí», « SI», «sí.» y «SÍ» dan «SI». «S» y «N» cubren a los tokenizadores
# que parten la palabra en el primer token.
VARIANTES_SI = frozenset({"S", "SI"})
VARIANTES_NO = frozenset({"N", "NO"})
_SIGNOS_TOKEN = " \t\n\r\u2581\"'`*_.,:;!?¡¿«»()[]{}-"
# Solo para la columna `alerta_sugerida` (P(SÍ) ≥ P(NO)); la política se elige offline.
UMBRAL_SI = 0.5
# Dígitos de la escala 0–9, comparados con `forma_token`. El tokenizador de Gemma parte los
# números en dígitos sueltos: un «10» empezaría con «1» (la humo controla que no pase).
DIGITOS = frozenset("0123456789")
# Solo para la columna `alerta_sugerida` (dígito esperado en la mitad de arriba de la escala).
UMBRAL_DIGITO = 4.5
# v4-L: tokens que se dejan generar del JSON para llegar al primer decimal del riesgo
# (`{"riesgo": 0.3` son ~8 tokens), y la marca de `alerta_sugerida` (riesgo esperado ≥ 0,5).
MAXIMO_TOKENS_LECTURA = 12
UMBRAL_LECTURA = 0.5
_ANTES_DEL_ENTERO = re.compile(r'"riesgo"\s*:\s*$')
_ANTES_DEL_DECIMAL = re.compile(r'"riesgo"\s*:\s*0\.$')
_RIESGO_ESCRITO = re.compile(r'"riesgo"\s*:\s*([01](?:\.[0-9]+)?)')
# v4-corte: tokens que se dejan generar del JSON de v4 para llegar al valor de `alerta_sugerida`.
# `{\n  "riesgo": 0.1,` son 12 tokens en T4 (etapa 1) y el JSON entero con motivo y evidencia
# vacíos, 41; `\n  "alerta_sugerida": false` suma ~11 (`al|erta|_|s|uger|ida` son 6), así que
# el valor termina en el token ~23. Uno más cubre un riesgo con dos decimales. La humo de
# colab/probar_json_cortado.py cuenta los tokens reales y frena si no alcanzan. Los demás prompts
# de PROMPTS_CORTE usan el mismo esquema, y su humo (etapa 2 de #143) cuenta los suyos.
MAXIMO_TOKENS_CORTE = 24
# Regla de aviso del detector (Mateo, 2026-11-07): riesgo escrito ≥ 0,4 o alerta_sugerida escrita.
UMBRAL_CORTE = 0.4
_RIESGO_CORTADO = re.compile(r'"riesgo"\s*:\s*(-?[0-9]+(?:\.[0-9]+)?(?:[eE][-+]?[0-9]+)?)\s*,')
_ALERTA_CORTADA = re.compile(r'"alerta_sugerida"\s*:\s*(true|false)\b')
# Etapa 3 de #143: C sin alerta y C con campo escriben un JSON corto que el modelo cierra solo (`{"riesgo": 0.3}` son
# unos 13 tokens, y con `pedido_critico`, unos 25). El tope solo frena a un modelo en bucle: la humo comprueba que no se
# llegue. La regla es la de C en la etapa 2 sin la alerta escrita, «riesgo ≥ 0,3», o `pedido_critico` en true.
MAXIMO_TOKENS_C_CORTO = 48
UMBRAL_C = 0.3


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
    # Solo con DetectorSLMSiNo (#143): p_si = P(SÍ) / (P(SÍ) + P(NO)) del primer token,
    # masa_si_no = P(SÍ) + P(NO) y las alternativas leídas, como JSON [[token, logprob], ...].
    p_si: float | None = None
    masa_si_no: float | None = None
    top_logprobs: str = ""
    # Solo con DetectorSLMDigito (#143, segunda vuelta): digito_esperado = Σ d·P(d) / Σ P(d)
    # sobre los dígitos del primer token (entre 0 y 9; el puntaje es digito_esperado / 9) y
    # masa_digitos = Σ P(d). Las alternativas van en top_logprobs.
    digito_esperado: float | None = None
    masa_digitos: float | None = None
    # Solo con DetectorSLMLecturaJSON (v4-L): el riesgo esperado según la distribución del entero
    # (0 o 1) y del primer decimal dentro del JSON. `riesgo` guarda el que quedó escrito.
    riesgo_esperado: float | None = None
    # Solo con DetectorSLMJSONCortado (PROMPTS_CORTE): la `alerta_sugerida` que escribió el modelo.
    # `alerta_sugerida` es la regla del detector (riesgo ≥ UMBRAL_CORTE o alerta escrita).
    alerta_escrita: bool | None = None
    # Solo con DetectorSLMCCorto y `c-con-campo`: el `pedido_critico` que escribió el modelo (la alerta fuerte).
    pedido_critico: bool | None = None


def cargar_prompt(variante: str) -> str:
    if variante not in PROMPTS:
        raise ValueError(f"prompt desconocido {variante!r}; opciones: {sorted(PROMPTS)}")
    partes = [(DIR_PROMPTS / nombre).read_text(encoding="utf-8").strip() for nombre in PROMPTS[variante]]
    return "\n\n".join(partes)


def cargar_pregunta(variante: str) -> str | None:
    """Pregunta que cierra el mensaje del usuario (con `{n}`), o None si el prompt usa el cierre por defecto."""
    if variante not in PROMPTS:
        raise ValueError(f"prompt desconocido {variante!r}; opciones: {sorted(PROMPTS)}")
    nombre = PREGUNTAS_FINALES.get(variante)
    return None if nombre is None else (DIR_PROMPTS / nombre).read_text(encoding="utf-8").strip()


def usa_roles(variante: str) -> bool:
    """True si el prompt nombra a PROTEGIDA y OTRA: necesita `--hablantes rol`, no A/B."""
    return "PROTEGIDA" in cargar_prompt(variante)


def esquema_de(variante: str) -> dict:
    if variante not in ESQUEMAS:
        raise ValueError(f"prompt desconocido {variante!r}; opciones: {sorted(ESQUEMAS)}")
    return ESQUEMAS[variante]


def cargar_prompt_motivo(nombre: str = PROMPT_MOTIVO) -> str:
    return (DIR_PROMPTS / nombre).read_text(encoding="utf-8").strip()


def huella(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()[:16]


def armar_mensaje_usuario(lineas: list[Linea] | tuple[Linea, ...], hablantes: str, cierre: str | None = None) -> str:
    """Transcripción disponible, numerada. Con `sin`, las letras A/B no llegan al modelo.

    Con `rol`, cada línea trae PROTEGIDA u OTRA en vez de la letra (ver `casos.con_roles`).
    `cierre` reemplaza la última oración (CIERRE_POR_DEFECTO); `{n}` se cambia por la última
    línea disponible.
    """
    if hablantes not in HABLANTES:
        raise ValueError(f"hablantes desconocido {hablantes!r}; opciones: {HABLANTES}")
    n = len(lineas)
    if hablantes == "ab":
        aclaracion = (
            "Cada línea indica quién habla con A o B. A es quien habló primero; "
            "las letras no indican quién llamó ni quién es sospechoso."
        )
        cuerpo = "\n".join(f"{i}. {l.hablante}: {l.texto}" for i, l in enumerate(lineas, start=1))
    elif hablantes == "rol":
        if any(l.hablante not in ROLES_HABLANTE for l in lineas):
            raise ValueError("hablantes 'rol' requiere líneas con PROTEGIDA u OTRA (ver casos.con_roles)")
        aclaracion = "Cada línea indica quién habla: PROTEGIDA es la persona que protegés y OTRA es con quien habla."
        cuerpo = "\n".join(f"{i}. {l.hablante}: {l.texto}" for i, l in enumerate(lineas, start=1))
    else:
        aclaracion = "Las líneas no indican quién habla."
        cuerpo = "\n".join(f"{i}. {l.texto}" for i, l in enumerate(lineas, start=1))
    # El número de líneas va solo al final: así el comienzo del mensaje es igual entre
    # actualizaciones y Ollama puede reutilizar lo ya procesado.
    return (
        f"Transcripción disponible hasta ahora; la llamada sigue. {aclaracion}\n\n"
        f"{cuerpo}\n\n"
        f"{(cierre or CIERRE_POR_DEFECTO).replace('{n}', str(n))}"
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
        cita = re.sub(r"^(?:[ab]|protegida|otra)\s+", "", cita)
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
    cierre: str | None = None  # None: CIERRE_POR_DEFECTO; si no, la pregunta final (cargar_pregunta)
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
        return self._mensajes_de(armar_mensaje_usuario(lineas, self.hablantes, self.cierre))

    def _mensajes_de(self, usuario: str) -> tuple[list[dict] | None, str]:
        estimado = math.ceil((len(self.prompt) + len(usuario)) / CARACTERES_POR_TOKEN)
        if estimado > self.num_ctx * FRACCION_MAXIMA_DEL_CONTEXTO:
            # No se recorta en silencio (#50): se informa como fallo.
            return None, f"contexto_excedido: ~{estimado} tokens > {self.num_ctx}"
        return [{"role": "system", "content": self.prompt}, {"role": "user", "content": usuario}], ""

    def evaluar(self, lineas: list[Linea] | tuple[Linea, ...]) -> Respuesta:
        return self.evaluar_mensaje(armar_mensaje_usuario(lineas, self.hablantes, self.cierre), lineas)

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
        comun = _medidas(r, ms)
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


def _duracion_ns(r: dict, clave: str) -> int | None:
    """Duración del runtime en ns; None si el runtime no la informa."""
    valor = r.get(clave)
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        return None
    return int(valor)


def _medidas(r: dict, ms: float) -> dict:
    """Texto crudo, tiempo de pared, tokens y duraciones del runtime de una respuesta de Ollama."""
    total_ns = _duracion_ns(r, "total_duration")
    return dict(crudo=r.get("message", {}).get("content", ""), ms=ms, slm_ms=ms,
                tokens_prompt=r.get("prompt_eval_count"), tokens_salida=r.get("eval_count"),
                runtime_ns=total_ns, runtime_unidad="ns" if total_ns is not None else "",
                runtime_load_ns=_duracion_ns(r, "load_duration"),
                runtime_prompt_eval_ns=_duracion_ns(r, "prompt_eval_duration"),
                runtime_eval_ns=_duracion_ns(r, "eval_duration"))


def forma_token(token: str) -> str:
    """Token sin tildes, sin espacios ni signos alrededor y en mayúsculas: « Sí.» → «SI»."""
    sin_tildes = "".join(c for c in unicodedata.normalize("NFD", token) if unicodedata.category(c) != "Mn")
    return sin_tildes.strip(_SIGNOS_TOKEN).upper()


def leer_si_no(logprobs) -> tuple[float | None, float | None, list, str]:
    """(p_si, masa_si_no, alternativas, error) del primer token generado.

    `logprobs` es el campo de la respuesta de Ollama: una lista con un elemento por token
    generado, cada uno con sus `top_logprobs` [{token, logprob, bytes}]. Se suman las
    probabilidades de todas las variantes de SÍ y de NO entre las alternativas (no se
    suma aparte el token elegido: ya está entre ellas). Sin variantes de SÍ ni de NO,
    p_si no está definido y la línea queda como fallo (`sin_si_no`), con masa 0.
    """
    pares, error = _alternativas_primer_token(logprobs)
    if pares is None:
        return None, None, [], error
    p_si = sum(math.exp(lp) for token, lp in pares if forma_token(token) in VARIANTES_SI)
    p_no = sum(math.exp(lp) for token, lp in pares if forma_token(token) in VARIANTES_NO)
    alternativas = [[token, round(lp, 4)] for token, lp in pares]
    masa = p_si + p_no
    if masa <= 0:
        return None, 0.0, alternativas, "sin_si_no"
    return p_si / masa, masa, alternativas, ""


def leer_digito(logprobs) -> tuple[float | None, float | None, list, str]:
    """(digito_esperado, masa_digitos, alternativas, error) del primer token generado.

    Como `leer_si_no`, pero suma la probabilidad de cada dígito del 0 al 9 entre las
    alternativas. `digito_esperado` es el promedio de los dígitos ponderado por esas
    probabilidades, entre 0 y 9. Sin dígitos, la línea queda como fallo (`sin_digitos`),
    con masa 0.
    """
    pares, error = _alternativas_primer_token(logprobs)
    if pares is None:
        return None, None, [], error
    masa, suma = 0.0, 0.0
    for token, lp in pares:
        forma = forma_token(token)
        if forma in DIGITOS:
            masa += math.exp(lp)
            suma += int(forma) * math.exp(lp)
    alternativas = [[token, round(lp, 4)] for token, lp in pares]
    if masa <= 0:
        return None, 0.0, alternativas, "sin_digitos"
    return suma / masa, masa, alternativas, ""


def leer_riesgo_json(logprobs) -> tuple[float | None, float | None, float | None, dict, float | None, str]:
    """(riesgo_esperado, digito_esperado, masa_digitos, alternativas, riesgo_escrito, error) de v4-L.

    `logprobs` trae un elemento por token generado del JSON. Se busca la posición del entero
    del riesgo (después de `"riesgo":`) y la del primer decimal (después de `"riesgo": 0.`).
    En el decimal, `digito_esperado` y `masa_digitos` se calculan como en `leer_digito`.
    riesgo_esperado = P(1) + P(0)·digito_esperado/10, con P(0) y P(1) normalizadas en el
    entero; si el entero no queda en un token propio, es digito_esperado/10. Si el modelo
    escribió 1, no hay decimal que leer y el riesgo esperado es 1.
    """
    if not isinstance(logprobs, list) or not logprobs:
        return None, None, None, {}, None, "sin_logprobs"
    texto, entero, decimal = "", None, None
    for paso in logprobs:
        token = paso.get("token") if isinstance(paso, dict) else None
        if not isinstance(token, str):
            return None, None, None, {}, None, "logprobs_malformados"
        if entero is None and _ANTES_DEL_ENTERO.search(texto) and token.strip()[:1].isdigit():
            entero = paso  # el primer token con número después de `"riesgo":` (puede venir un espacio antes)
        if decimal is None and _ANTES_DEL_DECIMAL.search(texto):
            decimal = paso
        texto += token
    escrito = _RIESGO_ESCRITO.search(texto)
    riesgo_escrito = float(escrito.group(1)) if escrito else None
    alternativas = {}
    p0 = p1 = 0.0
    if entero is not None:
        pares, error = _alternativas_primer_token([entero])
        if pares is None:
            return None, None, None, {}, riesgo_escrito, error
        alternativas["entero"] = [[t, round(lp, 4)] for t, lp in pares]
        p0 = sum(math.exp(lp) for t, lp in pares if forma_token(t) == "0")
        p1 = sum(math.exp(lp) for t, lp in pares if forma_token(t) == "1")
    if decimal is None:
        if riesgo_escrito is not None and riesgo_escrito >= 1:
            return 1.0, None, None, alternativas, riesgo_escrito, ""
        return None, None, None, alternativas, riesgo_escrito, "sin_decimal_de_riesgo"
    digito, masa, pares, error = leer_digito([decimal])
    alternativas["decimal"] = pares
    if digito is None:
        return None, None, masa, alternativas, riesgo_escrito, error
    if p0 + p1 > 0:
        riesgo = (p1 + p0 * digito / 10) / (p0 + p1)
    else:
        riesgo = digito / 10
    return riesgo, digito, masa, alternativas, riesgo_escrito, ""


def leer_json_cortado(crudo: str) -> tuple[float | None, bool | None, int | None, str]:
    """(riesgo, alerta_escrita, fin, error) del JSON de v4 cortado después de `alerta_sugerida`.

    `crudo` es el texto que generó el modelo con MAXIMO_TOKENS_CORTE tokens: no es JSON válido.
    `fin` es la posición en `crudo` donde termina el valor de la alerta. Acepta `"riesgo": 0`
    sin decimal. Sin el valor de la alerta (el corte llegó antes), la línea es un fallo
    (`sin_alerta`) aunque el riesgo se haya leído: se devuelve igual, para el registro.
    """
    escrito = _RIESGO_CORTADO.search(crudo)
    riesgo = float(escrito.group(1)) if escrito else None
    alerta = _ALERTA_CORTADA.search(crudo, escrito.end() if escrito else 0)
    if riesgo is None:
        return None, None, None, "sin_riesgo"
    if not math.isfinite(riesgo) or not 0 <= riesgo <= 1:
        return riesgo, None, None, "riesgo_fuera_de_rango"
    if alerta is None:
        return riesgo, None, None, "sin_alerta"
    return riesgo, alerta.group(1) == "true", alerta.end(), ""


def leer_c_corto(crudo: str, esquema: dict) -> tuple[float | None, bool | None, str]:
    """(riesgo, pedido_critico, error) del JSON de C sin alerta o de C con campo (PROMPTS_C_CORTO).

    `pedido_critico` es None si el esquema no lo pide. Con el riesgo fuera de rango o el campo mal, la línea es un fallo.
    """
    try:
        salida = json.loads(crudo)
    except json.JSONDecodeError:
        return None, None, "json_invalido"
    if not isinstance(salida, dict):
        return None, None, "json_no_es_objeto"
    faltan = [c for c in esquema["required"] if c not in salida]
    if faltan:
        return None, None, f"faltan_campos: {','.join(faltan)}"
    riesgo = salida["riesgo"]
    if isinstance(riesgo, bool) or not isinstance(riesgo, (int, float)) or not math.isfinite(riesgo):
        return None, None, "riesgo_no_numerico"
    campo = salida.get("pedido_critico") if "pedido_critico" in esquema["required"] else None
    if "pedido_critico" in esquema["required"] and not isinstance(campo, bool):
        return float(riesgo), None, "pedido_critico_no_booleano"
    if not 0 <= riesgo <= 1:
        return float(riesgo), campo, "riesgo_fuera_de_rango"
    return float(riesgo), campo, ""


def _alternativas_primer_token(logprobs) -> tuple[list[tuple[str, float]] | None, str]:
    """([(token, logprob), ...], "") del primer token generado, o (None, error)."""
    if not isinstance(logprobs, list) or not logprobs:
        return None, "sin_logprobs"
    top = logprobs[0].get("top_logprobs") if isinstance(logprobs[0], dict) else None
    if not isinstance(top, list) or not top:
        return None, "sin_top_logprobs"
    pares = []
    for alt in top:
        token, logprob = (alt.get("token"), alt.get("logprob")) if isinstance(alt, dict) else (None, None)
        if not isinstance(token, str) or isinstance(logprob, bool) or not isinstance(logprob, (int, float)) or logprob > 1e-6:
            return None, "logprobs_malformados"
        pares.append((token, float(logprob)))
    return pares, ""


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


@dataclass
class DetectorSLMSiNo(DetectorSLM):
    """Puntaje por probabilidad del token «SÍ» (#143).

    Mismos mensajes que DetectorSLM (la pregunta SÍ/NO cierra el prompt de sistema o, con
    `cierre`, el mensaje del usuario), sin esquema JSON, con `num_predict` 1, temperatura 0, sin razonamiento previo y con los
    `top_logprobs` (20) del primer token. `p_si` es el puntaje continuo para las políticas
    offline; `alerta_sugerida` (P(SÍ) ≥ P(NO)) solo deja una marca en el CSV.
    """

    pensar: bool | None = False

    def opciones(self) -> dict:
        return {**super().opciones(), "num_predict": 1}

    def evaluar_mensaje(self, usuario: str, lineas: list[Linea] | tuple[Linea, ...]) -> Respuesta:
        mensajes, error = self._mensajes_de(usuario)
        if mensajes is None:
            return Respuesta(valida=False, error=error)
        inicio = time.perf_counter()
        try:
            r = self.cliente.chat(self.modelo, mensajes, None, self.opciones(), self.pensar, top_logprobs=TOP_LOGPROBS)
        except ErrorOllama as e:
            ms_fallo = (time.perf_counter() - inicio) * 1000
            return Respuesta(valida=False, error=str(e), ms=ms_fallo, slm_ms=ms_fallo)
        # done_reason "length" es lo esperado: se pide un solo token.
        return self._leer(r, (time.perf_counter() - inicio) * 1000)

    def _leer(self, r: dict, ms: float) -> Respuesta:
        p_si, masa, alternativas, error = leer_si_no(r.get("logprobs"))
        comun = dict(**_medidas(r, ms), masa_si_no=masa,
                     top_logprobs=json.dumps(alternativas, ensure_ascii=False) if alternativas else "")
        if p_si is None:
            return Respuesta(valida=False, error=error, **comun)
        return Respuesta(valida=True, p_si=p_si, alerta_sugerida=p_si >= UMBRAL_SI, **comun)


@dataclass
class DetectorSLMDigito(DetectorSLMSiNo):
    """Puntaje por el dígito del primer token (#143, segunda vuelta).

    El mismo pedido que DetectorSLMSiNo, pero la pregunta final pide un número del 0 al 9
    y se lee la distribución de los dígitos. `digito_esperado` (0 a 9) es el puntaje
    continuo para las políticas offline; `alerta_sugerida` (≥ UMBRAL_DIGITO) solo deja una
    marca en el CSV.
    """

    def _leer(self, r: dict, ms: float) -> Respuesta:
        esperado, masa, alternativas, error = leer_digito(r.get("logprobs"))
        comun = dict(**_medidas(r, ms), masa_digitos=masa,
                     top_logprobs=json.dumps(alternativas, ensure_ascii=False) if alternativas else "")
        if esperado is None:
            return Respuesta(valida=False, error=error, **comun)
        return Respuesta(valida=True, digito_esperado=esperado, alerta_sugerida=esperado >= UMBRAL_DIGITO, **comun)


@dataclass
class DetectorSLMLecturaJSON(DetectorSLM):
    """v4-L (#143, segunda vuelta): el riesgo leído dentro del JSON de siempre.

    Mismo prompt, mismo mensaje y mismo esquema que DetectorSLM, y tampoco se envía `think`. Se
    generan solo MAXIMO_TOKENS_LECTURA tokens, con logprobs, para llegar al primer decimal del
    riesgo (ver `leer_riesgo_json`). `riesgo_esperado` es el puntaje continuo para las políticas
    offline; `riesgo`, el que quedó escrito; `alerta_sugerida` (≥ UMBRAL_LECTURA) solo deja una marca.
    """

    def opciones(self) -> dict:
        return {**super().opciones(), "num_predict": MAXIMO_TOKENS_LECTURA}

    def evaluar_mensaje(self, usuario: str, lineas: list[Linea] | tuple[Linea, ...]) -> Respuesta:
        mensajes, error = self._mensajes_de(usuario)
        if mensajes is None:
            return Respuesta(valida=False, error=error)
        inicio = time.perf_counter()
        try:
            r = self.cliente.chat(self.modelo, mensajes, self.esquema or ESQUEMA_SALIDA, self.opciones(), self.pensar,
                                  top_logprobs=TOP_LOGPROBS)
        except ErrorOllama as e:
            ms_fallo = (time.perf_counter() - inicio) * 1000
            return Respuesta(valida=False, error=str(e), ms=ms_fallo, slm_ms=ms_fallo)
        ms = (time.perf_counter() - inicio) * 1000
        riesgo, digito, masa, alternativas, escrito, error = leer_riesgo_json(r.get("logprobs"))
        # done_reason "length" es lo esperado: el JSON se corta después del riesgo.
        comun = dict(**_medidas(r, ms), masa_digitos=masa,
                     top_logprobs=json.dumps(alternativas, ensure_ascii=False) if alternativas else "")
        if riesgo is None:
            return Respuesta(valida=False, error=error, riesgo=escrito, **comun)
        return Respuesta(valida=True, riesgo=escrito, riesgo_esperado=riesgo, digito_esperado=digito,
                         alerta_sugerida=riesgo >= UMBRAL_LECTURA, **comun)


@dataclass
class DetectorSLMJSONCortado(DetectorSLM):
    """PROMPTS_CORTE (#143, ADR 0006): el JSON hasta `alerta_sugerida`, y el motivo aparte.

    Vale para v4 (`v4-corte`) y para los otros prompts JSON con ESQUEMA_SALIDA (`v4-premisa-corte`,
    `c-json-corte`; ver CORTE_DE). Primera consulta: el mismo pedido que DetectorSLM con el prompt
    base (prompt, mensaje y esquema; tampoco se envía `think` ni se piden logprobs), cortado con
    `num_predict` = MAXIMO_TOKENS_CORTE, justo después del valor de `alerta_sugerida`. Riesgo y alerta se leen del texto cortado
    (`leer_json_cortado`). La regla del detector es riesgo ≥ UMBRAL_CORTE o alerta escrita.

    Segunda consulta, solo la primera vez que la regla dispara en la llamada (el aviso es único):
    repite los mensajes, agrega como `assistant` lo que escribió el modelo, cerrado como JSON
    (`{… "alerta_sugerida": false\\n}`), y el pedido de `motivo_v4_corte.txt` con ESQUEMA_MOTIVO.
    No repite el JSON del prompt: si avisa por el riesgo con la alerta en false, el prompt deja
    motivo y evidencia vacíos. El comienzo es idéntico a la primera consulta, así que Ollama reutiliza
    la transcripción ya procesada. Si la segunda consulta falla, el aviso se mantiene y el error
    queda en `error` con el prefijo `etapa2_`. `reiniciar()` (lo llama `correr.procesar_caso`
    al empezar cada caso) la vuelve a habilitar.
    """

    umbral: float = UMBRAL_CORTE
    pedido_motivo: str = ""

    def __post_init__(self) -> None:
        self.pedido_motivo = self.pedido_motivo or cargar_prompt_motivo(PROMPT_MOTIVO_CORTE)
        self.reiniciar()

    def reiniciar(self) -> None:
        self._aviso_hecho = False

    def opciones(self) -> dict:
        return {**super().opciones(), "num_predict": MAXIMO_TOKENS_CORTE}

    def _leer(self, r1: dict, crudo: str) -> tuple[float | None, dict, int | None, str, bool]:
        """(riesgo, campos para Respuesta, fin, error, avisa) de la primera consulta."""
        # done_reason "length" es lo esperado: el JSON se corta después de la alerta.
        riesgo, alerta, fin, error = leer_json_cortado(crudo)
        return riesgo, {"alerta_escrita": alerta}, fin, error, not error and (riesgo >= self.umbral - 1e-9 or alerta)

    def _asistente(self, crudo: str, fin: int | None) -> str:
        """Lo que escribió el modelo, cerrado como JSON, para el turno `assistant` de la segunda consulta."""
        return crudo[:fin] + "\n}"

    def _pide_motivo(self, avisa: bool, campos: dict) -> bool:
        """True si esta línea dispara la segunda consulta (solo la primera vez en la llamada): el aviso."""
        return avisa

    def evaluar_mensaje(self, usuario: str, lineas: list[Linea] | tuple[Linea, ...]) -> Respuesta:
        mensajes, error = self._mensajes_de(usuario)
        if mensajes is None:
            return Respuesta(valida=False, error=error)
        inicio = time.perf_counter()
        try:
            r1 = self.cliente.chat(self.modelo, mensajes, self.esquema or ESQUEMA_SALIDA, self.opciones(), self.pensar)
        except ErrorOllama as e:
            ms_fallo = (time.perf_counter() - inicio) * 1000
            return Respuesta(valida=False, error=str(e), ms=ms_fallo, slm_ms=ms_fallo, ms_etapa1=ms_fallo)
        ms1 = (time.perf_counter() - inicio) * 1000
        comun = dict(**_medidas(r1, ms1), ms_etapa1=ms1)
        riesgo, campos, fin, error, avisa = self._leer(r1, comun["crudo"])
        if error:
            return Respuesta(valida=False, error=error, riesgo=riesgo, **comun)
        if not self._pide_motivo(avisa, campos) or self._aviso_hecho:
            return Respuesta(valida=True, riesgo=riesgo, alerta_sugerida=avisa, **campos, **comun)
        self._aviso_hecho = True

        asistente = self._asistente(comun["crudo"], fin)
        mensajes2 = mensajes + [{"role": "assistant", "content": asistente}, {"role": "user", "content": self.pedido_motivo}]
        opciones2 = {**super().opciones(), "num_predict": MAXIMO_TOKENS_RESPUESTA}
        base = dict(valida=True, riesgo=riesgo, alerta_sugerida=True, **campos)
        inicio2 = time.perf_counter()
        try:
            r2 = self.cliente.chat(self.modelo, mensajes2, ESQUEMA_MOTIVO, opciones2, self.pensar)
        except ErrorOllama as e:
            ms2 = (time.perf_counter() - inicio2) * 1000
            comun.update(ms=ms1 + ms2, slm_ms=ms1 + ms2, ms_etapa2=ms2)
            return Respuesta(**base, error=f"etapa2_{e}", **comun)
        ms2 = (time.perf_counter() - inicio2) * 1000
        crudo2 = r2.get("message", {}).get("content", "")
        comun.update(ms=ms1 + ms2, slm_ms=ms1 + ms2, ms_etapa2=ms2, crudo_etapa2=crudo2,
                     tokens_prompt_etapa2=r2.get("prompt_eval_count"), tokens_salida_etapa2=r2.get("eval_count"))
        salida, error = validar_motivo(crudo2) if r2.get("done_reason") != "length" else (None, "salida_cortada")
        if salida is None:
            return Respuesta(**base, error=f"etapa2_{error}", **comun)
        return Respuesta(**base, motivo=salida["motivo"].strip(), evidencia=salida["evidencia"].strip(),
                         evidencia_en_texto=evidencia_en_texto(salida["evidencia"], lineas), **comun)


@dataclass
class DetectorSLMCCorto(DetectorSLMJSONCortado):
    """PROMPTS_C_CORTO (etapa 3 de #143): C sin alerta o C con campo, en una consulta por línea, y el motivo de C aparte.

    Primera consulta: el pedido de DetectorSLM con el prompt y el esquema propios (`c-sin-alerta`: solo el riesgo;
    `c-con-campo`: `pedido_critico` y después el riesgo), sin `think` ni logprobs, con `num_predict` =
    MAXIMO_TOKENS_C_CORTO de tope. El modelo cierra el JSON solo: si llega al tope, la línea es un fallo. La regla es
    «riesgo ≥ UMBRAL_C o pedido_critico» en cualquier línea; la lectura solo en las de OTRA se simula después.

    Segunda consulta (Mateo, 2026-11-09): solo en la primera alerta fuerte de la llamada (`pedido_critico` en true), con
    el JSON tal como lo escribió el modelo en el turno `assistant` y el pedido de motivo_c_corte.txt. El primer aviso por
    riesgo no consulta nada: la app muestra un texto fijo. `c-sin-alerta` no tiene alerta fuerte y nunca la pide.
    """

    umbral: float = UMBRAL_C

    def __post_init__(self) -> None:
        self.pedido_motivo = self.pedido_motivo or cargar_prompt_motivo(PROMPT_MOTIVO_C)
        super().__post_init__()

    def opciones(self) -> dict:
        return {**DetectorSLM.opciones(self), "num_predict": MAXIMO_TOKENS_C_CORTO}

    def _leer(self, r1: dict, crudo: str) -> tuple[float | None, dict, int | None, str, bool]:
        if r1.get("done_reason") == "length":
            return None, {}, None, "salida_cortada", False
        riesgo, campo, error = leer_c_corto(crudo, self.esquema or ESQUEMA_RIESGO)
        return riesgo, {"pedido_critico": campo}, None, error, not error and (riesgo >= self.umbral - 1e-9 or campo is True)

    def _asistente(self, crudo: str, fin: int | None) -> str:
        return crudo.strip()

    def _pide_motivo(self, avisa: bool, campos: dict) -> bool:
        return campos.get("pedido_critico") is True


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
