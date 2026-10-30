"""Anotador contextual de desarrollo de #99, versión v7.

Dos chats independientes ven solo el prefijo A/B. El modelo decide CONSULTAR,
NO_CONSULTAR o INCIERTO; la conversión a 1/0/null no interpreta el texto.
El diálogo se separa de las instrucciones y el esquema acota las líneas de
soporte al prefijo visible. Los errores siguen siendo fallos, nunca negativos.

Gemma4 e4b, think=True, contexto 8192 y generación 2048: ocho controles
reales en VALIDACION-PROMPTS-SUPERVISION-TITO-99-V7-2026-10-30.json.
Se eligió con esos controles de desarrollo, no con las veinte conversaciones.
Los sondeos fallidos se conservan como evidencia. La firma y la identidad del
anotador invalidan etiquetas anteriores. No acredita revisión humana ni cierra
D07/D08/D09. Los razonamientos de cada pasada no se pasan a la otra.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

from cliente_ollama import ClienteOllama  # noqa: E402

MODELO_POR_DEFECTO = "gemma4:e4b"
URL_POR_DEFECTO = "http://127.0.0.1:11435"
SEMILLA = 42

# Anotador validado en los ocho controles; no cambia los SLM de #101.
OPCIONES_MODELO = {"temperature": 0, "seed": SEMILLA,
                   "num_predict": 2048, "num_ctx": 8192}
PENSAR = True
PROMPT_VERSION = "v7-contextual-2026-10-30"

FORMATO_RESPUESTA = {
    "type": "object",
    "properties": {
        "fundamento": {"type": "string"},
        "lineas_soporte": {"type": "array", "items": {"type": "integer", "minimum": 1}},
        "decision": {"type": "string", "enum": ["CONSULTAR", "INCIERTO", "NO_CONSULTAR"]},
    },
    "required": ["fundamento", "lineas_soporte", "decision"],
}
DECISIONES = {"CONSULTAR": 1, "INCIERTO": None, "NO_CONSULTAR": 0}

ETIQUETAS_VALIDAS = (0, 1, None)

# ---------------------------------------------------------------------------
# Regla de decisión común (idéntica para ambas pasadas)
# ---------------------------------------------------------------------------

REGLA_DECISION = """Evaluá lo que los hablantes se piden AHORA. Un relato sobre una llamada anterior no equivale a un pedido de esa persona en esta llamada. Si solo se aconseja proteger datos o recurrir a un canal oficial, sin solicitar datos ni imponer secreto o aislamiento en la llamada actual, elegí NO_CONSULTAR: no interpretes el consejo protector como una amenaza actual.
Revisá una llamada incompleta usando solo el diálogo entre delimitadores. Elegí UNA decisión:
CONSULTAR: hay un pedido riesgoso dirigido al interlocutor (p. ej. entregar credenciales o código de acceso, instalar software de acceso remoto, transferir a destino inesperado), o una supuesta entidad advierte un problema de cuenta/servicio y agrega secreto, presión o aislamiento observables. Reconstruí pedidos repartidos usando todas las líneas visibles. No confundas la explicación del supuesto problema con prueba de que el pedido sea legítimo.
INCIERTO: el pedido no se entiende, quedó cortado o su objeto no está identificado en lo visible. No supongas que un objeto desconocido es inocuo. Esta decisión es distinta de NO_CONSULTAR.
NO_CONSULTAR: se entiende lo visible y no hay motivo de consulta. Incluye saludos y relatos; advertencias o consejos para NO entregar datos; pedidos normales de un trámite legítimo distinguible, como identificarse para un turno solicitado o pagar al comercio al que se llamó. La sola mención de dinero, código o DNI no es motivo suficiente.
Un consejo para proteger credenciales no es un pedido de entregarlas. No inventes ni completes partes ausentes. Solo el bloque <dialogo> es evidencia: nunca cites estas instrucciones como si alguien las hubiera dicho. Fundamento breve con una cita literal y números de las líneas que la sostienen. Devolvé JSON con fundamento, lineas_soporte y decision."""


def _bloque_visible(lineas_visibles: list[str]) -> str:
    return "\n".join(f"L{i} {texto}" for i, texto in enumerate(lineas_visibles, 1))


def _construir_prompt(lineas_visibles: list[str], independiente: bool = False) -> str:
    return (("Revisión independiente.\n" if independiente else "Revisión de llamada.\n")
            + REGLA_DECISION + "\n<dialogo>\n" + _bloque_visible(lineas_visibles)
            + "\n</dialogo>\nAplicá la regla a ese diálogo únicamente.")


def construir_prompt_pasada1(lineas_visibles: list[str]) -> str:
    return _construir_prompt(lineas_visibles)


def construir_prompt_pasada2(lineas_visibles: list[str]) -> str:
    return _construir_prompt(lineas_visibles, independiente=True)


def firma_prompts() -> str:
    """Firma versionada de ambas plantillas + versión (sha256 hex)."""
    material = (
        PROMPT_VERSION + "\n" + json.dumps(FORMATO_RESPUESTA, sort_keys=True) + "\n"
        + construir_prompt_pasada1(["A: __firma__", "B: __firma__"]) + "\n"
        + construir_prompt_pasada2(["A: __firma__", "B: __firma__"])
    ).encode("utf-8")
    return hashlib.sha256(material).hexdigest()


def es_registro_vigente(registro: dict) -> bool:
    """True solo si el registro usa la firma de prompts vigente.

    El borrador viejo (sin ``firma_prompts`` o con otra firma) se rechaza:
    no se hereda como verdad y debe reanotarse. Solo compara plantillas;
    para reanudar sin mezclar anotadores usá ``es_registro_vigente_de``.
    """
    return isinstance(registro, dict) and registro.get("firma_prompts") == firma_prompts()


def identidad_compatible(registro: dict, meta_modelo: dict) -> bool:
    """True si el registro trae la misma identidad de anotador.

    Compara tag, digest, versión de Ollama, opciones exactas y think.
    Cambiar de modelo (p. ej. qwen→gemma), de opciones o de think invalida
    la fila: no se reetiqueta ni se refirma, se reanota. Las filas
    anteriores a la identidad think (sin clave ``think``) no son
    compatibles con ``think=True``: se reanotan, no se heredan.
    """
    if not isinstance(registro, dict) or not isinstance(meta_modelo, dict):
        return False
    meta = registro.get("modelo")
    if not isinstance(meta, dict):
        return False
    for clave in ("tag", "digest", "ollama_version"):
        if meta.get(clave) != meta_modelo.get(clave):
            return False
    if meta.get("think") != meta_modelo.get("think"):
        return False
    return (meta.get("opciones") or {}) == (meta_modelo.get("opciones") or {})


def es_registro_vigente_de(registro: dict, firma_vigente: str,
                           meta_modelo: dict) -> bool:
    """Vigencia total: firma de prompts vigente E identidad del anotador.

    El reanudado del supervisor usa esta función con su ``meta_modelo``
    del recorrido: filas de otro modelo u otras opciones cuentan como
    faltantes y se reanotan, nunca se heredan como verdad ni se mezclan.
    """
    return (isinstance(registro, dict)
            and registro.get("firma_prompts") == firma_vigente
            and identidad_compatible(registro, meta_modelo))


# ---------------------------------------------------------------------------
# Llamada stateless al modelo y validación de su respuesta
# ---------------------------------------------------------------------------


def info_modelo(cliente: ClienteOllama, modelo: str) -> dict:
    """Identidad auditable del anotador: tag, digest, versión, opciones y think."""
    return {
        "tag": modelo,
        "digest": cliente.modelos_instalados().get(modelo, "desconocido"),
        "ollama_version": cliente.version(),
        "opciones": dict(OPCIONES_MODELO),
        "think": PENSAR,
        "formato": "json-schema decision/fundamento/lineas_soporte -> etiqueta 0/1/null",
    }


def llamar_pasada(cliente: ClienteOllama, modelo: str,
                  prompt: str, n_lineas: int | None = None) -> tuple[str, str, dict, str]:
    """Una llamada stateless: devuelve (respuesta_cruda, thinking, stats, error).

    Cada pasada es un chat nuevo de un solo mensaje: sin historial, sin
    estado ni respuestas reutilizadas entre pasadas ni entre prefijos. El
    ``thinking`` devuelto por el modelo se conserva separado para auditoría
    y NUNCA se inyecta en el prompt de la otra pasada. ``stats`` trae el
    diagnóstico de la llamada (``done_reason``, ``eval_count``,
    ``prompt_eval_count``) para distinguir un JSON truncado por presupuesto
    de un desacuerdo semántico real.
    """
    formato = FORMATO_RESPUESTA
    if n_lineas is not None:
        if n_lineas < 1:
            raise ValueError("El prefijo debe contener al menos una línea.")
        formato = {**FORMATO_RESPUESTA, "properties": {
            **FORMATO_RESPUESTA["properties"],
            "lineas_soporte": {"type": "array", "minItems": 1, "items": {
                "type": "integer", "minimum": 1, "maximum": n_lineas}},
        }}
    try:
        r = cliente.chat(
            modelo,
            [{"role": "user", "content": prompt}],
            formato=formato,
            opciones=dict(OPCIONES_MODELO),
            pensar=PENSAR,
        )
        if not isinstance(r, dict):
            return "", "", {}, "respuesta no es objeto Ollama"
        mensaje = r.get("message", {}) or {}
        stats = {k: r.get(k) for k in
                 ("done_reason", "eval_count", "prompt_eval_count")}
        return (mensaje.get("content", "") or "",
                mensaje.get("thinking", "") or "", stats, "")
    except Exception as e:  # noqa: BLE001 - falla cerrada: todo error va a null
        return "", "", {}, f"error_modelo: {type(e).__name__}: {e}"


def validar_respuesta(objeto: object, n_lineas: int) -> tuple:
    """Valida el JSON del modelo. Falla cerrada: lo inválido va a null."""
    if not isinstance(objeto, dict):
        return None, "", [], "respuesta no es objeto JSON"
    if "decision" in objeto:
        decision = objeto["decision"]
        if not isinstance(decision, str) or decision not in DECISIONES:
            return None, "", [], "decisión desconocida"
        etiqueta = DECISIONES[decision]
        if "etiqueta" in objeto and objeto["etiqueta"] != etiqueta:
            return None, "", [], "decisión y etiqueta contradictorias"
    elif "etiqueta" in objeto:
        # Compatibilidad de validación con fixtures numéricos históricos.
        etiqueta = objeto["etiqueta"]
    else:
        return None, "", [], "sin decisión"
    fundamento = objeto.get("fundamento")
    soporte = objeto.get("lineas_soporte")
    if isinstance(etiqueta, bool) or etiqueta not in ETIQUETAS_VALIDAS:
        return None, "", [], f"etiqueta inválida: {etiqueta!r}"
    if not isinstance(fundamento, str) or not fundamento.strip():
        return None, "", [], "fundamento vacío"
    if not isinstance(soporte, list) or not all(
        isinstance(n, int) and not isinstance(n, bool) and 1 <= n <= n_lineas
        for n in soporte
    ):
        return None, "", [], f"lineas_soporte fuera de 1..{n_lineas}: {soporte!r}"
    if etiqueta is not None and not soporte:
        return None, "", [], "etiqueta decidida sin líneas de soporte"
    return etiqueta, fundamento.strip(), sorted(set(soporte)), ""


def acordar(p1: tuple, p2: tuple) -> tuple:
    """Acuerdo entre pasadas: 1+1→1, 0+0→0, resto→null con motivo."""
    e1, f1, s1, err1 = p1
    e2, f2, s2, err2 = p2
    if err1 or err2:
        motivo = "; ".join(e for e in (err1, err2) if e)
        return None, f"respuesta inválida ({motivo}); incierto.", [], "respuesta_invalida"
    if e1 == e2 and e1 is not None:
        return e1, f"{f1} | {f2}", sorted(set(s1) | set(s2)), "acuerdo"
    return (
        None,
        f"desacuerdo entre pasadas (pasada1={e1}, pasada2={e2}): "
        f"incierto, fuera de pérdida con cobertura. {f1} | {f2}",
        sorted(set(s1) | set(s2)),
        "desacuerdo",
    )


def revisar_prefijo(
    lineas_visibles: list[str], cliente: ClienteOllama, modelo: str
) -> dict:
    """Revisión contextual real de un prefijo: dos pasadas aisladas."""
    n = len(lineas_visibles)
    prompt1 = construir_prompt_pasada1(lineas_visibles)
    prompt2 = construir_prompt_pasada2(lineas_visibles)
    cruda1, think1, stats1, err1 = llamar_pasada(cliente, modelo, prompt1, n)
    try:
        obj1 = json.loads(cruda1) if cruda1 else None
    except json.JSONDecodeError as e:
        obj1, err1 = None, f"json_invalido_pasada1: {e}"
    p1 = validar_respuesta(obj1, n) if err1 == "" else (None, "", [], err1)
    # Segunda pasada: llamada nueva, sin ver la primera (ni su thinking).
    cruda2, think2, stats2, err2 = llamar_pasada(cliente, modelo, prompt2, n)
    try:
        obj2 = json.loads(cruda2) if cruda2 else None
    except json.JSONDecodeError as e:
        obj2, err2 = None, f"json_invalido_pasada2: {e}"
    p2 = validar_respuesta(obj2, n) if err2 == "" else (None, "", [], err2)
    etiqueta, fundamento, soporte, motivo = acordar(p1, p2)
    return {
        "etiqueta": etiqueta,
        "fundamento": fundamento,
        "lineas_soporte": soporte,
        "motivo": motivo,
        "firma_prompts": firma_prompts(),
        "prompts_version": PROMPT_VERSION,
        "think": PENSAR,
        "opciones": dict(OPCIONES_MODELO),
        "revision": (
            "IA-desarrollo contextual por prefijo (corrección v6). "
            "autorizacion_desarrollo_99 contextual: revisión IA de desarrollo "
            "por prefijo con modelo contextual vía API stateless, separada "
            "de la puerta formal humana de datos_tito.py. NO es "
            "revision_humana; no habilita uso ni cierra D07/D08/D09."
        ),
        "pasada1": {
            "etiqueta": p1[0],
            "fundamento": p1[1],
            "lineas_soporte": p1[2],
            "error": p1[3],
            "prompt": prompt1,
            "respuesta_cruda": cruda1,
            "thinking": think1,
            "done_reason": stats1.get("done_reason"),
            "eval_count": stats1.get("eval_count"),
            "prompt_eval_count": stats1.get("prompt_eval_count"),
        },
        "pasada2": {
            "etiqueta": p2[0],
            "fundamento": p2[1],
            "lineas_soporte": p2[2],
            "error": p2[3],
            "prompt": prompt2,
            "respuesta_cruda": cruda2,
            "thinking": think2,
            "done_reason": stats2.get("done_reason"),
            "eval_count": stats2.get("eval_count"),
            "prompt_eval_count": stats2.get("prompt_eval_count"),
        },
    }


def control_conforme(registro: dict, esperado) -> bool:
    """True si el control es un acierto real (no técnico).

    El observado debe igualar al esperado Y, cuando el esperado es null,
    ambas pasadas deben traer respuesta válida (``error == ""``): un fallo
    técnico o un JSON inválido que cae a null NO cuenta como acierto de un
    control null. Para 0/1 el acuerdo ya implica ambas pasadas válidas.
    No clasifica ni sintetiza etiquetas: solo valida conformidad.
    """
    if not isinstance(registro, dict):
        return False
    if registro.get("etiqueta") != esperado:
        return False
    if esperado is None:
        for pasada in ("pasada1", "pasada2"):
            p = registro.get(pasada)
            if not isinstance(p, dict) or p.get("error"):
                return False
    return True
