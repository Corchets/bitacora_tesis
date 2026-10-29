"""Prompts de supervisión contextual por prefijo para #99 (módulo del corrector).

Corrige el sesgo de los prompts originales de ``supervision_tito_99.py``
(pasada 1 pedía ``DIRECTAMENTE`` dinero/código: el prefijo legítimo de la
pizzería recibía 1/1 aunque el contexto visible mostraba un pago legítimo
en un local ya conocido). La v2 contextual corrigió ese caso pero dejó
tres limitaciones reales medidas con el modelo en
``VALIDACION-PROMPTS-SUPERVISION-TITO-99-2026-10-29.json`` (7/8):
el indicio sin pedido dividió a las pasadas (0/1 → null), los
fundamentos afirmaron secreto/urgencia no presentes en el texto y los
controles ambiguos se declararon 0 en vez del null que pide el contrato.
La v3 ordenó el indicio como chequeo previo pero el enunciado seguía
planteando una pregunta binaria de motivo y gemma4:e4b devolvió 0/0 en
ambos ambiguos (6/8) aunque el transporte emite null (diagnóstico
verificado por root). Esta v4 aplica la regla triestado breve de root:
pregunta explícita de asignar UNA etiqueta (1, 0 o null), orden
1-evidencia / null-incomprensible / 0-legítimo, con cita literal y
segunda pasada aislada. Este módulo NO se integra solo: tras el handoff
con el dueño del supervisor (ctx_98285f28e9d3) sus constructores reemplazan
a ``construir_prompt_pasada1/_pasada2`` del supervisor, que conserva la
orquestación, la auditoría y la puerta de entrenamiento.

Contrato contextual (CONFIGURACION-TITO-2026-10-29.json § supervision_prefijos):

- ``1``: hay en lo visible un pedido riesgoso o un indicio concreto y
  específico suficiente para consultar al SLM. Se citan líneas visibles.
- ``0``: tras revisar TODO lo visible no hay motivo observable de consulta,
  incluyendo solicitudes legítimas distinguibles por el contexto visible.
- ``null``: con lo visible solo no se puede decidir (incompleto o ambiguo
  genuino). Fuera de pérdida/métricas, dentro de cobertura.

Ambas pasadas son stateless y aisladas, ven SOLO el prefijo visible con
hablantes A/B íntegros, sin case_id, sin clase final, sin T_R, sin sufijo
futuro y sin la respuesta de la otra pasada. Comparten el MISMO objetivo
(enunciado con distinta redacción para mantener independencia) y la MISMA
regla de decisión: no se exige petición directa en una sola línea (un
pedido repartido en varias líneas también es 1) y ninguna palabra
(dinero, alias, DNI, código) convierte sola un prefijo en 1.

Sin reglas léxicas ni excepciones ad hoc: la decisión la toma el modelo
contextual aplicando la regla; este módulo solo arma prompts, valida el
formato de la respuesta y acuerda las pasadas (1+1→1, 0+0→0, resto→null).

Versionado: cada registro lleva ``firma_prompts`` (sha256 de la versión y
de ambas plantillas). El reanudado y el entrenamiento RECHAZAN filas con
firma distinta o ausente (borrador viejo y v1/v2/v3 descartados): no se
heredan como verdad. Ver ``es_registro_vigente()``.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

from cliente_ollama import ClienteOllama  # noqa: E402

MODELO_POR_DEFECTO = "qwen3.5:4b"
URL_POR_DEFECTO = "http://127.0.0.1:11435"
SEMILLA = 42

OPCIONES_MODELO = {"temperature": 0, "seed": SEMILLA, "num_predict": 300}

PROMPT_VERSION = "v4-contextual-2026-10-29"

FORMATO_RESPUESTA = {
    "type": "object",
    "properties": {
        "etiqueta": {"type": ["integer", "null"], "enum": [0, 1, None]},
        "fundamento": {"type": "string"},
        "lineas_soporte": {"type": "array", "items": {"type": "integer"}},
    },
    "required": ["etiqueta", "fundamento", "lineas_soporte"],
}

ETIQUETAS_VALIDAS = (0, 1, None)

# ---------------------------------------------------------------------------
# Regla de decisión común (idéntica para ambas pasadas)
# ---------------------------------------------------------------------------

REGLA_DECISION = (
    "Regla para etiquetar: leé TODO lo visible y asigná UNA etiqueta "
    "(1, 0 o null). No es una pregunta de sí/no: las tres salidas son "
    "posibles y debés elegir una.\n"
    "1. Marcá 1 si hay evidencia contextual concreta de riesgo. Hay "
    "evidencia si alguien que dice ser del banco, la policía, una "
    "empresa o un organismo avisa de un problema de la cuenta o del "
    "servicio (movimientos raros, cargo desconocido, cuenta bloqueada o "
    "equivalente que cites del texto) Y ADEMÁS pide secreto ('no le "
    "cuentes a nadie'), mete urgencia ('ahora mismo', 'ya', 'urgente' o "
    "equivalente literal), pide que le dicten un código o clave, o da "
    "instrucciones de aislarse o de no cortar; la evidencia vale aunque "
    "nadie haya pedido nada todavía. También es 1 si hay un pedido "
    "dirigido a la otra persona de ESTA llamada que es riesgoso por el "
    "contexto visible (beneficiario inesperado, presión para hacerlo ya, "
    "pedido de secreto, cambio de lo ya acordado a la vista). El pedido "
    "puede estar repartido en varias líneas; no hace falta que esté todo "
    "en una sola. Citá las líneas.\n"
    "2. Sin esa evidencia, marcá null si el objeto o el trámite no se "
    "entiende o está cortado: fragmento cortado a mitad de palabra o "
    "frase sin saberse qué se pidió, o pedido de algo sin identificar "
    "qué es ('eso', 'esto', 'lo que...', pronombres sin antecedente "
    "visible) sin poderse saber si es sensible. Lo incompleto o no "
    "identificado no es 0.\n"
    "3. Marcá 0 si el contenido se entiende y no hay motivo: nadie le "
    "pide nada sensible a su interlocutor (incluye consejos preventivos "
    "y relatos sin pedido), o el pedido es la parte normal del trámite "
    "que la propia persona solicitó al llamar (pagar el precio al "
    "comercio al que llamó, confirmar el alias de la factura del local "
    "ya conocido, dar el DNI para el turno que pidió) sin señal de "
    "riesgo a la vista.\n"
    "PROHIBIDO inventar: cada afirmación del fundamento sobre secreto, "
    "urgencia, presión, amenaza o quién llamó a quién debe apoyarse en "
    "palabras LITERALES del fragmento, entrecomilladas. Lo 'implícito' o "
    "'sugerido' NO cuenta: si el texto no lo dice, no lo afirmes. Que "
    "aparezcan las palabras dinero, alias, DNI, código o clave NO "
    "alcanza por sí solo para marcar 1: lo legítimo por el contexto "
    "visible es 0.\n"
    "Devolvé JSON con etiqueta, fundamento (con citas textuales cortas "
    "entrecomilladas de lo visto) y lineas_soporte (números de las líneas "
    "citadas)."
)


def _bloque_visible(lineas_visibles: list[str]) -> str:
    """Numera las líneas visibles conservando el hablante A/B original."""
    return "\n".join(f"L{i} {texto}" for i, texto in enumerate(lineas_visibles, 1))


def construir_prompt_pasada1(lineas_visibles: list[str]) -> str:
    """Primera pasada: revisa el prefijo con la regla de decisión común."""
    return (
        "Estás revisando una llamada en curso. Solo existe lo que sigue; "
        "no hay más contexto, ni antes ni después.\n"
        f"{_bloque_visible(lineas_visibles)}\n\n"
        "Asigná UNA etiqueta (1, 0 o null) a estas líneas según la regla.\n"
        f"{REGLA_DECISION}"
    )


def construir_prompt_pasada2(lineas_visibles: list[str]) -> str:
    """Segunda pasada aislada: mismo objetivo, redacción independiente.

    No recibe case_id, referencia, clase, T_R ni sufijo futuro; tampoco
    recibe la respuesta de la primera pasada.
    """
    return (
        "Sos un segundo revisor independiente de una llamada en curso. "
        "Estas líneas son todo lo que se sabe hasta ahora; no hay nada "
        "más, ni antes ni después.\n"
        f"{_bloque_visible(lineas_visibles)}\n\n"
        "Como revisor independiente, asigná UNA etiqueta (1, 0 o null) a "
        "estas líneas según la regla.\n"
        f"{REGLA_DECISION}"
    )


def firma_prompts() -> str:
    """Firma versionada de ambas plantillas + versión (sha256 hex)."""
    material = (
        PROMPT_VERSION + "\n"
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

    Compara tag, digest, versión de Ollama y opciones exactas. Cambiar de
    modelo (p. ej. qwen→gemma) o de opciones invalida la fila: no se
    reetiqueta ni se refirma, se reanota.
    """
    if not isinstance(registro, dict) or not isinstance(meta_modelo, dict):
        return False
    meta = registro.get("modelo")
    if not isinstance(meta, dict):
        return False
    for clave in ("tag", "digest", "ollama_version"):
        if meta.get(clave) != meta_modelo.get(clave):
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
    """Identidad auditable del anotador: tag, digest, versión y parámetros."""
    return {
        "tag": modelo,
        "digest": cliente.modelos_instalados().get(modelo, "desconocido"),
        "ollama_version": cliente.version(),
        "opciones": dict(OPCIONES_MODELO),
        "formato": "json-schema etiqueta/fundamento/lineas_soporte",
    }


def llamar_pasada(cliente: ClienteOllama, modelo: str, prompt: str) -> tuple[str, str]:
    """Una llamada stateless: devuelve (respuesta_cruda, error).

    Cada pasada es un chat nuevo de un solo mensaje: sin historial, sin
    estado ni respuestas reutilizadas entre pasadas ni entre prefijos.
    """
    try:
        r = cliente.chat(
            modelo,
            [{"role": "user", "content": prompt}],
            formato=FORMATO_RESPUESTA,
            opciones=dict(OPCIONES_MODELO),
            pensar=False,
        )
        return r["message"]["content"], ""
    except Exception as e:  # noqa: BLE001 - falla cerrada: todo error va a null
        return "", f"error_modelo: {type(e).__name__}: {e}"


def validar_respuesta(objeto: object, n_lineas: int) -> tuple:
    """Valida el JSON del modelo. Falla cerrada: lo inválido va a null."""
    if not isinstance(objeto, dict):
        return None, "", [], "respuesta no es objeto JSON"
    etiqueta = objeto.get("etiqueta")
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
    cruda1, err1 = llamar_pasada(cliente, modelo, prompt1)
    try:
        obj1 = json.loads(cruda1) if cruda1 else None
    except json.JSONDecodeError as e:
        obj1, err1 = None, f"json_invalido_pasada1: {e}"
    p1 = validar_respuesta(obj1, n) if err1 == "" else (None, "", [], err1)
    # Segunda pasada: llamada nueva, sin ver la primera.
    cruda2, err2 = llamar_pasada(cliente, modelo, prompt2)
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
        "revision": (
            "IA-desarrollo contextual por prefijo (corrección v4). "
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
        },
        "pasada2": {
            "etiqueta": p2[0],
            "fundamento": p2[1],
            "lineas_soporte": p2[2],
            "error": p2[3],
            "prompt": prompt2,
            "respuesta_cruda": cruda2,
        },
    }
