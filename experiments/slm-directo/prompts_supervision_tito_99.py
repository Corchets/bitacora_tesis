"""Prompts de supervisión contextual por prefijo para #99 (módulo del corrector).

Corrige el sesgo de los prompts originales de ``supervision_tito_99.py``
(pasada 1 pedía ``DIRECTAMENTE`` dinero/código: el prefijo legítimo de la
pizzería recibía 1/1 aunque el contexto visible mostraba un pago legítimo
en un local ya conocido). Este módulo NO se integra solo: tras el handoff
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
firma distinta o ausente (borrador viejo descartado): no se heredan como
verdad. Ver ``es_registro_vigente()``.
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

PROMPT_VERSION = "v2-contextual-2026-10-29"

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
    "Regla para etiquetar (aplica igual a todo lo visible; seguí estos "
    "pasos en orden):\n"
    "1. Identificá si ALGUIEN LE PIDE ALGO A SU INTERLOCUTOR EN ESTA "
    "LLAMADA: un pedido, instrucción o indicación dirigido a la otra "
    "persona de la llamada para que entregue o dicte un código o clave, "
    "transfiera o pague dinero o datos de pago (alias, CBU), instale una "
    "aplicación, comparta la pantalla o entregue datos sensibles (DNI, "
    "contraseñas, tokens). El pedido puede estar repartido en varias "
    "líneas; no hace falta que esté todo en una sola.\n"
    "2. Buscá PRIMERO un indicio concreto y específico de riesgo, aunque "
    "todavía no haya ningún pedido. Es indicio concreto: que alguien que "
    "dice ser del banco, la policía o una empresa avise de un problema "
    "(movimientos raros, cargo desconocido, cuenta bloqueada) y además pida "
    "secreto ('no le cuentes a nadie'), meta urgencia ('ahora mismo', "
    "'ya', 'urgente') o pida que dicte un código; o que dé instrucciones "
    "de aislarse o no cortar la llamada. La combinación de aviso de "
    "problema con pedido de secreto o urgencia ES indicio concreto por "
    "definición: no la rebajes a aviso genérico. Si hay un indicio así, "
    "marcá 1 sin esperar el pedido: el indicio visible ya justifica "
    "consultar al SLM. Un relato o aviso SIN estos elementos (un consejo "
    "genérico como "
    "'nunca pases tu clave', una anécdota pasada, negar un pedido) no es "
    "indicio: seguí al paso 3.\n"
    "3. Si no hay indicio concreto, mirá si hay un pedido dirigido al "
    "interlocutor y su contexto visible: es 0 si nadie le pide nada a su "
    "interlocutor, o si el pedido es la parte normal del trámite que la "
    "propia persona solicitó al llamar (pagar el precio al comercio al que "
    "llamó, confirmar el alias de la factura del local ya conocido, dar "
    "el DNI para el turno que pidió) y no hay a la vista ninguna señal de "
    "riesgo. Es 1 si el pedido es riesgoso por el contexto visible "
    "(beneficiario inesperado, presión para hacerlo ya, pedido de secreto, "
    "cambio de las instrucciones respecto de lo ya acordado a la vista).\n"
    "4. Si el fragmento es tan corto o ambiguo que no podés decidir si hay "
    "un pedido ni de qué, marcá null. 1 exige evidencia concreta citada "
    "de lo visto; ante la duda entre 0 y 1 con evidencia pobre, preferí "
    "null. Hablar del tema sin pedir nada concreto a la otra persona es 0, "
    "no null.\n"
    "Que aparezcan las palabras dinero, alias, DNI, código o clave NO "
    "alcanza por sí solo para marcar 1: lo legítimo por el contexto "
    "visible es 0.\n"
    "Devolvé JSON con etiqueta, fundamento (cita textual corta de lo visto) "
    "y lineas_soporte (números de las líneas citadas)."
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
        "¿Hay en estas líneas un motivo concreto y visible para consultar "
        "al sistema de verificación?\n"
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
        "Como revisor independiente: ¿corresponde pedir una verificación "
        "adicional en este punto, a la luz de lo que se ve?\n"
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
    no se hereda como verdad y debe reanotarse.
    """
    return isinstance(registro, dict) and registro.get("firma_prompts") == firma_prompts()


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
            "IA-desarrollo contextual por prefijo (corrección v2). "
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
