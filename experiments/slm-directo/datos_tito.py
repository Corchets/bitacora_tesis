"""Preparación y validación reproducible de datos para evaluar a Tito (#96, parte de #95).

Recorrido público: conversaciones -> prefijos -> particiones -> manifiesto ->
informe de validación. Todo entra por parámetros (dobles en pruebas); este
módulo nunca descarga modelos ni lee la reserva del proyecto.

Contratos reutilizados (sin modificarlos): `casos.Linea`, `casos.CLASES`,
`casos.LEGITIMAS`, `casos.EVENTOS` y las constantes de procedencia de
`entrenar_tito.py` (`BANCO_COMMIT`, `ESPERADO_*`). La reserva se rechaza por
identificador/partición sin leer su contenido.

> **Estado: propuesta sin discutir.** La composición, los tamaños, las reglas de
> referencia y las proporciones que este módulo registra requieren el acuerdo
> del equipo antes de habilitar su uso
> ([D07](../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico),
> [D08](../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental)).
> Ninguna conversación tiene revisión humana confirmada (`revision_humana`
> siempre `False` en esta rama); el módulo lo informa y bloquea la
> habilitación en vez de completarla artificialmente.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from casos import CLASES, ETIQUETAS, EVENTOS, PEDIDOS, Linea

AQUI = Path(__file__).resolve().parent

# Las ocho conversaciones ya analizadas (demo.sh, corrida 2026-10-14): se
# conservan como regresiones, no como evaluación independiente nueva.
REGRESION_OCHO = (
    "SC-WA-CODE-01-e01",
    "LG-WA-CONSULTA-01-e01",
    "SC-SOPORTE-CLAVE-01-e01",
    "LG-SUPPORT-INFO-01-e01",
    "TR-01-pedido-indirecto-digitos",
    "TR-02-codigo-del-candado",
    "TR-08-frase-cortada-candado",
    "TR-12-corta-antes-del-pedido",
)

PARTICIONES = (
    "entrenamiento",
    "validacion",
    "diagnostico",
    "evaluacion_independiente",
    "regresion",
)

HABLANTES = ("A", "B")

CAMPOS_ACUERDO = ("composicion", "tamano", "reglas_referencia", "proporciones")

# La revisión conserva los originales: el indicador dice si se conservaron y
# la referencia dice dónde (ruta o identificador trazable).
CAMPOS_REVISION = ("revisores", "originales_conservados", "originales_referencia",
                   "desacuerdos", "adjudicaciones", "referencias_revisadas")

# Categorías que la muestra debe cubrir (#96). No se detectan por texto: cada
# conversación trae sus marcas `dificultades`; lo no marcado se informa como
# ausente o no registrado, nunca se inventa.
CATEGORIAS_COBERTURA = (
    "legitima_dificil",
    "solicitud_sensible_legitima",
    "negacion",
    "cita",
    "relato",
    "advertencia",
    "pedido_indirecto",
    "evidencia_repartida",
    "contexto_prolongado",
)

SUPERVISION_SIN_EVIDENCIA = "sin_evidencia_suficiente"

DECISIONES_PENDIENTES = ("D07", "D08")


@dataclass(frozen=True)
class Referencia:
    """Referencia humana de una conversación. Provisional hasta revisión."""

    clase: str  # "vishing" | "legitima" | "legitima_dificil"
    t_r_linea: int | None = None
    t_c_linea: int | None = None
    pedido: str | None = None
    evidencia: tuple = ()
    revision_humana: bool = False
    par: str | None = None


@dataclass(frozen=True)
class Conversacion:
    """Unidad de agrupación: nunca se parte entre particiones."""

    case_id: str
    lineas: tuple
    referencia: Referencia | None = None
    semilla: str | None = None
    # Familia de variantes del banco histórico (p. ej. "banco_001"): agrupa
    # textos generados de la misma variante. Distinta de `modalidad`.
    familia_variante: str | None = None
    # Modalidad amplia del corpus (p. ej. "banco", "whatsapp", "soporte"):
    # describe el escenario, no agrupa variantes relacionadas.
    modalidad: str | None = None
    dificultades: tuple = ()


@dataclass(frozen=True)
class Prefijo:
    """Una actualización incremental: lo visible hasta la línea n, sin futuro."""

    case_id: str
    hasta_linea: int
    visible: tuple
    truncado: bool = False


@dataclass(frozen=True)
class InformeValidacion:
    es_evaluable: bool
    errores: tuple = ()
    advertencias: tuple = ()

    def a_dict(self) -> dict:
        return {
            "es_evaluable": self.es_evaluable,
            "errores": list(self.errores),
            "advertencias": list(self.advertencias),
        }


def huella(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def _normalizar(texto: str) -> str:
    return " ".join(texto.split())


def _campo_ref(ref, nombre: str, faltante=None):
    """Lee un campo de una referencia `Referencia` o de un dict equivalente.

    Las entradas con otra estructura se informan como errores de validación
    en vez de romper el recorrido (`TypeError`/`AttributeError`).
    """
    if isinstance(ref, Referencia):
        return getattr(ref, nombre)
    if isinstance(ref, dict):
        return ref.get(nombre, faltante)
    return faltante


# ---------------------------------------------------------------------------
# Inventario del banco histórico (antecedente, sin sobrescribirlo)
# ---------------------------------------------------------------------------

def inventariar_banco(registros: list[dict], exclusiones: dict,
                      procedencia: dict) -> dict:
    """Inventario auditable sobre registros inyectados (en pruebas, dobles).

    Distingue `familias_variante` (banco: agrupan variantes relacionadas, no
    pueden cruzar particiones) de `modalidades` (lotes amplios del banco:
    describen origen, no agrupan variantes). Registra exclusiones con motivo.
    """
    aceptados = [r for r in registros if r.get("familia") not in exclusiones]
    apartados = [r for r in registros if r.get("familia") in exclusiones]
    familias = sorted({r["familia"] for r in aceptados})
    fuentes: dict[str, list[str]] = {}
    for r in aceptados:
        for f in r.get("fuentes", []):
            fuentes.setdefault(f, [])
            if r["familia"] not in fuentes[f]:
                fuentes[f].append(r["familia"])
    for f in fuentes:
        fuentes[f] = sorted(fuentes[f])
    return {
        "procedencia": procedencia,
        "versiones": {
            "registros_total": len(registros),
            "aceptados": len(aceptados),
            "apartados": len(apartados),
            "familias_variante": len(familias),
        },
        "familias_variante": familias,
        "modalidades": sorted({r.get("lote") for r in aceptados if r.get("lote")}),
        "exclusiones": dict(exclusiones),
        "relaciones_sematicas": {"fuente_a_familias": fuentes},
        "nota_unidad": ("La familia de variantes agrupa textos relacionados; "
                        "la modalidad describe el lote amplio y no agrupa variantes."),
    }


def auditar_banco_historico() -> dict:
    """Lee el banco del commit fijado por #68/#70 y lo inventaría.

    Auditoría de solo lectura sobre objetos git locales (historia de
    desarrollo, no la reserva). No duplica el banco ni lo modifica.
    """
    from entrenar_tito import (  # contrato existente, no modificado
        BANCO_BASE,
        BANCO_COMMIT,
        EJEMPLOS_SHA_DECLARADO,
        EXCLUSIONES_SHA_DECLARADA,
    )
    raiz = AQUI.parent.parent
    raiz_repo = raiz if (raiz / ".git").exists() else AQUI.parents[1]
    base = raiz_repo if (raiz_repo / ".git").exists() else Path(
        subprocess.run(["git", "rev-parse", "--show-toplevel"],
                       capture_output=True, text=True,
                       check=True).stdout.strip())
    ejemplos_raw = subprocess.run(
        ["git", "show", f"{BANCO_COMMIT}:{BANCO_BASE}/ejemplos.jsonl"],
        cwd=base, capture_output=True, check=True).stdout
    exclusiones_raw = subprocess.run(
        ["git", "show", f"{BANCO_COMMIT}:{BANCO_BASE}/exclusiones.json"],
        cwd=base, capture_output=True, check=True).stdout
    if hashlib.sha256(ejemplos_raw).hexdigest() != EJEMPLOS_SHA_DECLARADO:
        raise ValueError("ejemplos.jsonl no coincide con el hash declarado en entrenar_tito.py.")
    if hashlib.sha256(exclusiones_raw).hexdigest() != EXCLUSIONES_SHA_DECLARADA:
        raise ValueError("exclusiones.json no coincide con el hash declarado en entrenar_tito.py.")
    registros = [json.loads(l) for l in exclusiones_raw and ejemplos_raw.decode("utf-8").splitlines()]
    exclusiones = json.loads(exclusiones_raw.decode("utf-8"))
    return inventariar_banco(registros, exclusiones, {
        "banco_commit": BANCO_COMMIT,
        "base": BANCO_BASE,
        "artefacto_actual": "tito_logreg.json (5.520 aceptadas, 276 familias; ver entrenar_tito.py)",
    })


# ---------------------------------------------------------------------------
# Reserva: se rechaza, no se lee
# ---------------------------------------------------------------------------

def es_identificador_reserva(case_id: str) -> bool:
    return "CV2-T-" in case_id


def rechazar_reserva(case_ids: list[str], particiones: dict | None = None) -> None:
    """Rechaza identificadores o particiones de reserva sin leer su contenido."""
    reservados = [c for c in case_ids if es_identificador_reserva(c)]
    if particiones:
        reservados += [c for c, p in particiones.items() if p == "test_reservado"]
    if reservados:
        raise ValueError(
            "Reserva del proyecto fuera de esta exploración "
            f"({sorted(set(reservados))}): no se lee, ejecuta, copia ni usa.")


# ---------------------------------------------------------------------------
# Prefijos y etiquetas por actualización (solo texto visible)
# ---------------------------------------------------------------------------

def construir_prefijos(conversacion: Conversacion,
                       ventana: int | None = None,
                       limite_tokens: int | None = None) -> list[Prefijo]:
    """Prefijos 1..n con la misma construcción en preparación e inferencia.

    `ventana=None` usa el historial completo; con entero, las últimas
    `ventana` líneas incluida la actual. Nunca arrastra otra conversación
    (cada llamada empieza vacía) ni incluye contenido futuro. Los recortes
    por `limite_tokens` (aproximado por caracteres, 4 por token) se marcan
    en `truncado`, no se recortan en silencio.
    """
    if ventana is not None and ventana < 1:
        raise ValueError("la ventana debe ser None o un entero >= 1.")
    prefijos = []
    for n in range(1, len(conversacion.lineas) + 1):
        inicio = 0 if ventana is None else max(0, n - ventana)
        visible = conversacion.lineas[inicio:n]
        truncado = False
        if limite_tokens is not None:
            caracteres = sum(len(l.texto) for l in visible)
            truncado = caracteres > limite_tokens * 4
        prefijos.append(Prefijo(conversacion.case_id, n, tuple(visible), truncado))
    return prefijos


def etiquetar_prefijo(conversacion: Conversacion, hasta_linea: int) -> dict:
    """Etiqueta de una actualización según solo lo visible hasta esa línea.

    Devuelve tres referencias separadas: `clase_conversacion` (metadato
    final de la conversación: se informa para distinguirla, nunca se usa
    como etiqueta de supervisión del prefijo ni se copia a los fragmentos),
    `marcas` (t_r/t_c/pedido, nulos si aún no visibles) y `supervision`
    (derivada solo de evidencia con linea <= n).
    Sin referencia o sin revisión humana, la supervisión es provisional.
    """
    ref = conversacion.referencia
    if ref is None or not isinstance(ref, (Referencia, dict)):
        return {"clase_conversacion": None, "marcas": None,
                "supervision": SUPERVISION_SIN_EVIDENCIA, "provisional": True,
                "motivo": "sin referencia: no evaluable hasta resolver o excluir."}
    evidencia = _campo_ref(ref, "evidencia", ())
    if not isinstance(evidencia, (list, tuple)):
        evidencia = ()
    visibles = [e for e in evidencia
                if isinstance(e, dict) and e.get("linea", 0) <= hasta_linea]
    if any(e.get("evento") == "cumplimiento" for e in visibles):
        supervision = "cumplimiento_visible"
    elif any(e.get("evento") == "pedido" for e in visibles):
        supervision = "pedido_visible"
    elif visibles:
        supervision = "indicio_parcial"
    else:
        supervision = SUPERVISION_SIN_EVIDENCIA
    t_r = _campo_ref(ref, "t_r_linea")
    t_c = _campo_ref(ref, "t_c_linea")
    marcas = {
        "t_r_linea": t_r if t_r is not None and t_r <= hasta_linea else None,
        "t_c_linea": t_c if t_c is not None and t_c <= hasta_linea else None,
        "pedido": _campo_ref(ref, "pedido") if t_r is not None and t_r <= hasta_linea else None,
    }
    revision_humana = _campo_ref(ref, "revision_humana", False)
    return {"clase_conversacion": _campo_ref(ref, "clase"), "marcas": marcas,
            "supervision": supervision,
            "provisional": not revision_humana,
            "motivo": ("" if revision_humana
                       else "referencia sin revisión humana: provisional, no habilita uso.")}


# ---------------------------------------------------------------------------
# Validación de particiones
# ---------------------------------------------------------------------------

def _es_entero_linea(valor) -> bool:
    return isinstance(valor, int) and not isinstance(valor, bool)


def _errores_referencia(case_id: str, ref, n_lineas: int) -> list[str]:
    """Vocabulario, rangos, tipos y coherencia TR/TC/evidencia (#96).

    Acepta `Referencia` o un dict con los mismos campos; otra estructura
    se informa como error en vez de romper el recorrido. Las ambigüedades
    detienen el uso del dato: cualquier motivo devuelve un error que
    vuelve el informe no evaluable.
    """
    prefijo = f"{case_id}: referencia"
    errores: list[str] = []
    if not isinstance(ref, (Referencia, dict)):
        return [f"{prefijo} con estructura no soportada "
                f"({type(ref).__name__}): no es Referencia ni dict."]
    clase = _campo_ref(ref, "clase")
    t_r = _campo_ref(ref, "t_r_linea")
    t_c = _campo_ref(ref, "t_c_linea")
    pedido = _campo_ref(ref, "pedido")
    if not isinstance(clase, str) or clase not in CLASES:
        errores.append(
            f"{prefijo}: clase {clase!r} fuera del vocabulario {sorted(CLASES)}.")
    for campo, valor in (("t_r_linea", t_r), ("t_c_linea", t_c)):
        if valor is not None and not _es_entero_linea(valor):
            errores.append(f"{prefijo}: {campo} {valor!r} no es un entero de línea.")
        elif _es_entero_linea(valor) and not 1 <= valor <= n_lineas:
            errores.append(
                f"{prefijo}: {campo} {valor!r} fuera del diálogo (1..{n_lineas}).")
    if pedido is not None:
        if not isinstance(pedido, str):
            errores.append(f"{prefijo}: pedido {pedido!r} no es texto.")
        elif pedido not in PEDIDOS:
            errores.append(
                f"{prefijo}: pedido {pedido!r} no es una etiqueta REQUEST_*.")
    if not isinstance(_campo_ref(ref, "revision_humana"), bool):
        errores.append(f"{prefijo}: revision_humana debe ser true o false.")
    par = _campo_ref(ref, "par")
    if par is not None and (not isinstance(par, str) or not par.strip()):
        errores.append(f"{prefijo}: par {par!r} no es un identificador válido.")
    if clase in ("legitima", "legitima_dificil"):
        if t_r is not None or t_c is not None:
            errores.append(
                f"{prefijo} ambigua: legítima con marcas t_r/t_c: "
                "ambigua hasta resolución o exclusión.")
        if pedido is not None:
            errores.append(
                f"{prefijo} ambigua: legítima con pedido: "
                "ambigua hasta resolución o exclusión.")
    else:
        if (t_r is None) != (pedido is None):
            errores.append(
                f"{prefijo} ambigua: pedido y t_r_linea van juntos: falta uno.")
        if t_c is not None and t_r is None:
            errores.append(
                f"{prefijo} ambigua: t_c_linea requiere t_r_linea: "
                "no hay cumplimiento sin pedido.")
        # Contrato vigente de casos.py: t_c_linea debe ser posterior a
        # t_r_linea en sentido estricto (rechaza t_c <= t_r). Este módulo
        # lo reutiliza sin modificarlo.
        if (_es_entero_linea(t_r) and _es_entero_linea(t_c)
                and t_c <= t_r):
            errores.append(
                f"{prefijo} ambigua: t_c_linea debe ser posterior a t_r_linea.")
    evidencia = _campo_ref(ref, "evidencia", ())
    if clase in ("legitima", "legitima_dificil"):
        # Una legítima sin pedido crítico no inventa evidencia: la lista
        # puede estar vacía; lo presente se valida igual que en vishing.
        if evidencia is None:
            evidencia = ()
        if not isinstance(evidencia, (list, tuple)):
            errores.append(f"{prefijo}: evidencia debe ser una lista.")
            return errores
    else:
        if not isinstance(evidencia, (list, tuple)) or not evidencia:
            errores.append(f"{prefijo}: evidencia debe ser una lista con al menos un elemento.")
            return errores
    for i, ev in enumerate(evidencia):
        donde = f"{prefijo} evidencia[{i}]"
        if not isinstance(ev, dict) or set(ev) != {"linea", "evento", "etiquetas"}:
            errores.append(f"{donde} debe tener exactamente linea, evento y etiquetas.")
            continue
        if not _es_entero_linea(ev["linea"]):
            errores.append(f"{donde}.linea {ev['linea']!r} no es un entero de línea.")
        elif not 1 <= ev["linea"] <= n_lineas:
            errores.append(
                f"{donde}.linea {ev['linea']!r} fuera del diálogo (1..{n_lineas}).")
        if not isinstance(ev["evento"], str) or ev["evento"] not in EVENTOS:
            errores.append(
                f"{donde}.evento {ev['evento']!r} no está en {sorted(EVENTOS)}.")
        etiquetas = ev["etiquetas"]
        if (not isinstance(etiquetas, list)
                or any(not isinstance(t, str) or t not in ETIQUETAS for t in etiquetas)):
            errores.append(
                f"{donde}.etiquetas tiene valores fuera del vocabulario del manual.")
    if t_r is not None and not any(
            isinstance(e, dict) and e.get("linea") == t_r
            and e.get("evento") == "pedido" for e in evidencia):
        errores.append(
            f"{prefijo} ambigua: falta evidencia 'pedido' en t_r_linea={t_r}.")
    if t_c is not None and not any(
            isinstance(e, dict) and e.get("linea") == t_c
            and e.get("evento") == "cumplimiento" for e in evidencia):
        errores.append(
            f"{prefijo} ambigua: falta evidencia 'cumplimiento' en "
            f"t_c_linea={t_c}.")
    return errores


def _errores_conversacion(conv: Conversacion) -> list[str]:
    """Estructura mínima de la conversación antes de validar su referencia."""
    errores: list[str] = []
    if not isinstance(conv.case_id, str) or not conv.case_id.strip():
        errores.append(f"conversación sin case_id válido: {conv.case_id!r}.")
    if not isinstance(conv.lineas, (list, tuple)) or not conv.lineas:
        errores.append(f"{conv.case_id}: el diálogo necesita al menos 1 línea.")
        return errores
    for n, linea in enumerate(conv.lineas, start=1):
        if not isinstance(linea, Linea):
            errores.append(
                f"{conv.case_id} línea {n}: no es casos.Linea "
                f"({type(linea).__name__}).")
            continue
        if linea.hablante not in HABLANTES:
            errores.append(
                f"{conv.case_id} línea {n}: hablante {linea.hablante!r} "
                f"fuera de {list(HABLANTES)}.")
        if not isinstance(linea.texto, str) or not linea.texto.strip():
            errores.append(f"{conv.case_id} línea {n}: texto vacío o no textual.")
    return errores


def _huella_conversacion(conv: Conversacion) -> str:
    return huella("\n".join(f"{l.hablante}: {_normalizar(l.texto)}" for l in conv.lineas))


def _huella_referencia(ref) -> str:
    evidencia = _campo_ref(ref, "evidencia", ())
    if not isinstance(evidencia, (list, tuple)):
        evidencia = ()
    partes = sorted(
        (str(e.get("linea")), str(e.get("evento")),
         ",".join(str(t) for t in e.get("etiquetas", [])
                  if isinstance(e.get("etiquetas"), list)))
        for e in evidencia if isinstance(e, dict))
    return huella("|".join([str(_campo_ref(ref, "clase")),
                            str(_campo_ref(ref, "t_r_linea")),
                            str(_campo_ref(ref, "t_c_linea")),
                            str(_campo_ref(ref, "pedido"))]
                           + ["/".join(p) for p in partes]))


def validar_particiones(conversaciones: list[Conversacion],
                        asignacion: dict[str, str],
                        familias_artefacto: set[str] | None = None,
                        ids_ajuste: set[str] | None = None,
                        grupos_semanticos: dict[str, str] | None = None,
                        ) -> InformeValidacion:
    """Rechaza cruces, duplicados, referencias inválidas y usos indebidos.

    Un informe con errores no es evaluable: el recorrido nunca presenta un
    conjunto inválido como evaluación válida (`es_evaluable=False`).
    El diagnóstico es una partición disjunta de la evaluación: la
    separación se verifica dentro de este recorrido (no solo en el helper
    `verificar_separacion_diagnostico`). Los grupos semánticos declarados
    (`grupos_semanticos`: case_id -> grupo, p. ej. fuente o escenario
    compartido del inventario) tampoco pueden cruzar particiones.
    Las conversaciones completas duplicadas entre particiones se rechazan
    incluso con la misma clase; una línea suelta repetida (un saludo común
    en llamadas distintas) no es un duplicado.
    """
    errores: list[str] = []
    advertencias: list[str] = []
    vistos_ids: set[str] = set()
    duplicados: list[str] = []
    for c in conversaciones:
        if c.case_id in vistos_ids:
            duplicados.append(c.case_id)
        vistos_ids.add(c.case_id)
    for c in sorted(set(duplicados)):
        errores.append(f"{c}: identificador duplicado: cada conversación entra una sola vez.")
    por_id: dict[str, Conversacion] = {}
    for c in conversaciones:
        por_id.setdefault(c.case_id, c)
    desconocidas = sorted(set(asignacion) - set(por_id))
    errores += [f"{c}: asignada pero sin conversación cargada." for c in desconocidas]
    sin_asignar = sorted(set(por_id) - set(asignacion))
    errores += [f"{c}: conversación sin partición asignada." for c in sin_asignar]
    for c, p in asignacion.items():
        if p not in PARTICIONES:
            errores.append(f"{c}: partición {p!r} fuera de {list(PARTICIONES)}.")
        if es_identificador_reserva(c) or p == "test_reservado":
            errores.append(f"{c}: la reserva no entra a esta exploración (no se lee ni usa).")
        if c in REGRESION_OCHO and p != "regresion":
            errores.append(
                f"{c}: caso histórico de las ocho: solo entra como regresión, "
                f"no como {p!r}.")
    for c in sorted(por_id):
        errores += _errores_conversacion(por_id[c])
        if por_id[c].referencia is None:
            errores.append(f"{c}: falta referencia: no evaluable hasta resolver o excluir.")
        else:
            errores += _errores_referencia(
                c, por_id[c].referencia, len(por_id[c].lineas))
    for clave in ("semilla", "familia_variante"):
        grupos: dict[str, set[str]] = {}
        for c, conv in por_id.items():
            if c not in asignacion:
                continue
            valor = conv.semilla if clave == "semilla" else conv.familia_variante
            if valor is None:
                continue
            grupos.setdefault(str(valor), set()).add(asignacion[c])
        for valor, partes in sorted(grupos.items()):
            if len(partes) > 1:
                errores.append(
                    f"{clave} {valor!r} cruza particiones {sorted(partes)}: "
                    "prefijos, ventanas y variantes relacionadas van juntos.")
    if grupos_semanticos:
        sem: dict[str, set[str]] = {}
        for c, grupo in grupos_semanticos.items():
            if c in asignacion and grupo is not None:
                sem.setdefault(str(grupo), set()).add(asignacion[c])
        for grupo, partes in sorted(sem.items()):
            if len(partes) > 1:
                errores.append(
                    f"grupo semántico {grupo!r} cruza particiones {sorted(partes)}: "
                    "los escenarios relacionados van juntos.")
    for c, conv in por_id.items():
        par = _campo_ref(conv.referencia, "par") if conv.referencia else None
        if par is None:
            continue
        if par not in por_id:
            errores.append(f"{c}: par {par!r} sin conversación cargada.")
            continue
        if c not in asignacion or par not in asignacion:
            continue
        if asignacion[par] != asignacion[c]:
            errores.append(
                f"par {par!r} cruza particiones "
                f"({c}: {asignacion[c]}, {par}: {asignacion[par]}): "
                "los casos contrastantes van juntos.")
    con_ref_invalida = {c for c in por_id
                        if por_id[c].referencia is not None
                        and _errores_referencia(c, por_id[c].referencia,
                                               len(por_id[c].lineas)
                                               if isinstance(por_id[c].lineas, (list, tuple)) else 0)}
    por_huella: dict[str, list[str]] = {}
    for c in sorted(por_id):
        if c not in asignacion or _errores_conversacion(por_id[c]):
            continue
        por_huella.setdefault(_huella_conversacion(por_id[c]), []).append(c)
    for h, ids in sorted(por_huella.items()):
        if len(ids) < 2:
            continue
        partes = sorted({asignacion[i] for i in ids if i in asignacion})
        if len(partes) > 1:
            errores.append(
                f"conversación completa duplicada entre particiones {partes}: "
                f"{', '.join(ids)} con el mismo diálogo.")
        huellas_ref = {_huella_referencia(por_id[i].referencia)
                       for i in ids if por_id[i].referencia is not None
                       and i not in con_ref_invalida}
        if len(huellas_ref) > 1:
            errores.append(
                f"conflicto de referencia para conversación duplicada: "
                f"{', '.join(ids)} comparten el diálogo con referencias distintas.")
    ids_evaluacion = {c for c, p in asignacion.items() if p == "evaluacion_independiente"}
    ids_diagnostico = {c for c, p in asignacion.items() if p == "diagnostico"}
    errores += verificar_separacion_diagnostico(
        ids_diagnostico, ids_evaluacion, set(ids_ajuste or ()))
    if familias_artefacto:
        eval_familias = {por_id[c].familia_variante for c, p in asignacion.items()
                         if p == "evaluacion_independiente" and c in por_id
                         and por_id[c].familia_variante}
        cruce = sorted(eval_familias & set(familias_artefacto))
        if cruce:
            errores.append(
                "El banco ya usado por el artefacto actual no se presenta como "
                f"evaluación independiente por separarlo retrospectivamente: {cruce}.")
    if not any(p == "evaluacion_independiente" for p in asignacion.values()):
        advertencias.append("Sin partición de evaluación independiente: solo diagnóstico y regresión.")
    if not any(p == "validacion" for p in asignacion.values()):
        advertencias.append("Sin partición de validación: la selección de configuración queda bloqueada.")
    return InformeValidacion(es_evaluable=not errores,
                             errores=tuple(errores),
                             advertencias=tuple(advertencias))


def verificar_separacion_diagnostico(ids_diagnostico: set[str],
                                     ids_evaluacion: set[str],
                                     ids_ajuste: set[str]) -> list[str]:
    """La evaluación independiente no comparte casos con diagnóstico ni ajuste.

    Helper público reutilizable; `validar_particiones` ya lo invoca en su
    recorrido con la partición `diagnostico` y `ids_ajuste`, así que la
    separación diagnóstico/evaluación se ejecuta siempre, no queda
    desconectada."""
    errores = []
    if ids_diagnostico & ids_evaluacion:
        errores.append(f"La evaluación pisa el diagnóstico: {sorted(ids_diagnostico & ids_evaluacion)}.")
    if ids_ajuste & ids_evaluacion:
        errores.append(f"La evaluación pisa el ajuste: {sorted(ids_ajuste & ids_evaluacion)}.")
    return errores


def marcar_regresiones(case_ids: list[str]) -> dict[str, str]:
    """Marca cuáles de las ocho históricas están presentes (regresión, no eval)."""
    return {c: ("regresion" if c in REGRESION_OCHO else "no_regresion") for c in case_ids}


# ---------------------------------------------------------------------------
# Cobertura de la muestra (presente/ausente, sin inventar)
# ---------------------------------------------------------------------------

def cobertura_muestra(conversaciones: list[Conversacion]) -> dict:
    presentes = {cat: sorted(c.case_id for c in conversaciones if cat in c.dificultades)
                 for cat in CATEGORIAS_COBERTURA}
    ausentes = sorted(cat for cat, ids in presentes.items() if not ids)
    return {
        "presentes": presentes,
        "ausentes": ausentes,
        "limites": [
            "Categorías marcadas por quien prepara la muestra; lo no marcado "
            "figura ausente, no se infiere del texto.",
            "Ninguna referencia está revisada por el equipo "
            "(revision_humana=False): la cobertura describe la propuesta, "
            "no una muestra habilitada.",
        ] + ([f"Sin cobertura: {', '.join(ausentes)}."] if ausentes else []),
    }


# ---------------------------------------------------------------------------
# Manifiesto e informe reproducibles
# ---------------------------------------------------------------------------

def generar_manifiesto(procedencia: dict, configuracion: dict,
                       asignacion: dict[str, str],
                       conversaciones: list[Conversacion],
                       semilla: int = 42,
                       fecha: str | None = None) -> dict:
    """Manifiesto reproducible: otra persona comprueba procedencia y separación.

    `fecha` es inyectable (`"2026-10-27"`): con fecha explícita, dos
    corridas producen el mismo manifiesto; sin ella se usa el día actual
    y el manifiesto solo es determinista dentro del mismo día."""
    huellas = {c.case_id: huella("\n".join(f"{l.hablante}: {l.texto}" for l in c.lineas))
               for c in sorted(conversaciones, key=lambda c: c.case_id)}
    revision = sum(1 for c in conversaciones
                   if c.referencia is not None and c.referencia.revision_humana)
    return {
        "fecha": fecha if fecha is not None else date.today().isoformat(),
        "estado": "propuesta sin discutir",
        "decisiones_pendientes": list(DECISIONES_PENDIENTES),
        "semilla": semilla,
        "codigo_version": huella(AQUI.joinpath("datos_tito.py").read_text(encoding="utf-8"))
        if AQUI.joinpath("datos_tito.py").exists() else "no_registrada",
        "procedencia": procedencia,
        "configuracion": configuracion,
        "particiones": {c.case_id: asignacion.get(c.case_id, "sin_asignar")
                        for c in conversaciones},
        "huellas_conversaciones": huellas,
        "revision_humana": {"revisadas": revision, "total": len(conversaciones)},
    }


def informe_validacion(manifiesto: dict, informe: InformeValidacion,
                       cobertura: dict) -> dict:
    return {
        "manifiesto_sha256": hashlib.sha256(
            json.dumps(manifiesto, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest(),
        "es_evaluable": informe.es_evaluable,
        "errores": list(informe.errores),
        "advertencias": list(informe.advertencias),
        "cobertura": cobertura,
        # Conteo y huellas del manifiesto: la puerta cruza lo declarado en
        # la revisión con lo que el manifiesto informa de verdad.
        "revision_manifiesto": (manifiesto.get("revision_humana")
                                if isinstance(manifiesto, dict)
                                and isinstance(manifiesto.get("revision_humana"), dict)
                                else None),
        "huellas_conversaciones": (dict(manifiesto["huellas_conversaciones"])
                                    if isinstance(manifiesto, dict)
                                    and isinstance(manifiesto.get("huellas_conversaciones"), dict)
                                    else {}),
        "habilitado": False,
        "bloqueo": ("Sin revisión humana efectiva ni acuerdo de composición y "
                     "proporciones (D07/D08): propuesta preparada, uso no habilitado. "
                     "No se inventan revisores, acuerdos, cuotas ni etiquetas revisadas."),
    }


def _tiene_contenido(valor) -> bool:
    """Un campo de acuerdo trae contenido si está presente y no vacío.

    Solo estructura (nada, texto en blanco o colección vacía no cuentan).
    Sin longitudes mínimas ni listas de marcadores: no hay decisión
    aprobada que fije esa metodología.
    """
    if valor is None:
        return False
    if isinstance(valor, str):
        return bool(valor.strip())
    if isinstance(valor, (list, tuple, dict, set)):
        return len(valor) > 0
    return True


def _es_entero_conteo(valor) -> bool:
    return isinstance(valor, int) and not isinstance(valor, bool)


def _relacionado_por_caso(item) -> bool:
    """Un desacuerdo/adjudicación debe relacionarse por caso o id."""
    if not isinstance(item, dict) or not item:
        return False
    for clave in ("caso", "id"):
        valor = item.get(clave)
        if isinstance(valor, str) and valor.strip():
            return True
        if _es_entero_conteo(valor):
            return True
    return False


def _motivos_revision(revision_efectiva, informe) -> list[str]:
    if not isinstance(revision_efectiva, dict):
        return ["Falta revisión humana efectiva del equipo "
                "(originales, desacuerdos y adjudicaciones conservados)."]
    motivos = []
    faltan = [k for k in CAMPOS_REVISION if k not in revision_efectiva]
    if faltan:
        motivos.append(
            "Revisión incompleta: faltan campos trazables "
            f"{faltan} (se exigen {list(CAMPOS_REVISION)}).")
        return motivos
    # Sin cuotas ni autenticación de personas: lista identificable no vacía.
    revisores = revision_efectiva["revisores"]
    if (not isinstance(revisores, list) or not revisores
            or not all(isinstance(r, str) and r.strip() for r in revisores)):
        motivos.append(
            "Revisores no trazables: se exige una lista no vacía de "
            "identificadores (el software no autentica personas).")
    if revision_efectiva["originales_conservados"] is not True:
        motivos.append(
            "Sin originales conservados: la revisión debe conservar "
            "las anotaciones originales.")
    referencia_originales = revision_efectiva["originales_referencia"]
    if not isinstance(referencia_originales, str) or not referencia_originales.strip():
        motivos.append(
            "Originales sin referencia trazable: indicar ruta o identificador "
            "donde se conservan, además del indicador.")
    desacuerdos = revision_efectiva["desacuerdos"]
    adjudicaciones = revision_efectiva["adjudicaciones"]
    if not isinstance(desacuerdos, list):
        motivos.append("Desacuerdos no registrados: deben listarse (vacía si no hubo).")
        desacuerdos = []
    elif any(not _relacionado_por_caso(d) for d in desacuerdos):
        motivos.append("Desacuerdos no trazables: cada uno indica su caso o id.")
    if not isinstance(adjudicaciones, list):
        motivos.append("Adjudicaciones no registradas: deben listarse.")
    elif desacuerdos and not adjudicaciones:
        motivos.append(
            "Hay desacuerdos sin adjudicación: cada desacuerdo requiere "
            "su adjudicación registrada.")
    elif any(not _relacionado_por_caso(a) for a in adjudicaciones):
        motivos.append("Adjudicaciones no trazables: cada una indica su caso o id.")
    conteo = revision_efectiva["referencias_revisadas"]
    if (not isinstance(conteo, dict)
            or not _es_entero_conteo(conteo.get("revisadas"))
            or not _es_entero_conteo(conteo.get("total"))
            or conteo["total"] <= 0 or conteo["revisadas"] != conteo["total"]):
        motivos.append(
            "Referencias sin revisar en su totalidad: se exige "
            "`referencias_revisadas: {revisadas, total}` con revisadas == total > 0.")
    else:
        revision_manifiesto = (informe.get("revision_manifiesto")
                               if isinstance(informe, dict) else None)
        if not isinstance(revision_manifiesto, dict):
            motivos.append(
                "Sin conteo de revisión del manifiesto: regenerar el informe "
                "con el manifiesto para cruzar lo declarado con lo revisado.")
        elif (not _es_entero_conteo(revision_manifiesto.get("revisadas"))
                or not _es_entero_conteo(revision_manifiesto.get("total"))):
            motivos.append(
                "Manifiesto sin conteo de revisión utilizable: regenerar el "
                "manifiesto con su conteo de revisión humana.")
        elif conteo["total"] != revision_manifiesto["total"]:
            motivos.append(
                "Discrepancia con el manifiesto: lo declarado "
                f"(total={conteo['total']}) no coincide con las "
                f"conversaciones del manifiesto (total={revision_manifiesto['total']}).")
        elif revision_manifiesto["revisadas"] != revision_manifiesto["total"]:
            motivos.append(
                "Revisión incompleta en el manifiesto: informa "
                f"{revision_manifiesto['revisadas']}/{revision_manifiesto['total']} "
                "referencias revisadas.")
    return motivos


def _motivos_acuerdo(acuerdo) -> list[str]:
    if not isinstance(acuerdo, dict):
        return ["Falta acuerdo registrado de composición, tamaño, reglas de "
                "referencia y proporciones (coordina con #32/#55 antes de "
                "producir o habilitar material dependiente)."]
    motivos = []
    faltan = [k for k in CAMPOS_ACUERDO if k not in acuerdo]
    if faltan:
        motivos.append(
            f"Acuerdo incompleto: faltan campos efectivos {faltan} "
            f"(se exigen {list(CAMPOS_ACUERDO)}).")
    for campo in CAMPOS_ACUERDO:
        if campo in acuerdo and not _tiene_contenido(acuerdo[campo]):
            motivos.append(
                f"Acuerdo sin contenido en {campo!r}: informar el valor "
                "acordado en vez de dejarlo vacío.")
    return motivos


def puede_habilitarse(informe: dict, revision_efectiva: dict | None = None,
                      acuerdo: dict | None = None) -> tuple[bool, list[str]]:
    """Puerta explícita fail-closed: sin revisión y acuerdo trazables, bloquea.

    `revision_efectiva` y `acuerdo` los aporta el equipo fuera de este módulo
    (revisores identificados, originales con su referencia, desacuerdos y
    adjudicaciones; composición, tamaño, reglas de referencia y proporciones).
    Este módulo nunca los inventa y no autentica personas por software: solo
    verifica estructura y contenido no vacío, y cruza lo declarado en la
    revisión con el conteo real del manifiesto que conserva el informe. Un
    dict vacío, una lista vacía o una discrepancia con el manifiesto no
    habilitan. Por defecto (sin revisión ni acuerdo reales, estado al
    2026-10-27) informa el bloqueo.
    """
    motivos = []
    if not isinstance(informe, dict) or not informe.get("es_evaluable", False):
        motivos.append("Particiones inválidas: resolver errores antes de habilitar.")
    motivos += _motivos_revision(revision_efectiva, informe)
    motivos += _motivos_acuerdo(acuerdo)
    return (not motivos, motivos)
