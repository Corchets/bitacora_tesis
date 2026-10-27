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
    "evaluacion_independiente",
    "regresion",
)

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
class Linea:
    hablante: str
    texto: str


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

    Devuelve tres referencias separadas: `clase_conversacion` (final, no se
    copia a los fragmentos), `marcas` (t_r/t_c/pedido, nulos si aún no
    visibles) y `supervision` (derivada solo de evidencia con linea <= n).
    Sin referencia o sin revisión humana, la supervisión es provisional.
    """
    ref = conversacion.referencia
    if ref is None:
        return {"clase_conversacion": None, "marcas": None,
                "supervision": SUPERVISION_SIN_EVIDENCIA, "provisional": True,
                "motivo": "sin referencia: no evaluable hasta resolver o excluir."}
    visibles = [e for e in ref.evidencia
                if isinstance(e, dict) and e.get("linea", 0) <= hasta_linea]
    if any(e.get("evento") == "cumplimiento" for e in visibles):
        supervision = "cumplimiento_visible"
    elif any(e.get("evento") == "pedido" for e in visibles):
        supervision = "pedido_visible"
    elif visibles:
        supervision = "indicio_parcial"
    else:
        supervision = SUPERVISION_SIN_EVIDENCIA
    marcas = {
        "t_r_linea": ref.t_r_linea if ref.t_r_linea is not None and ref.t_r_linea <= hasta_linea else None,
        "t_c_linea": ref.t_c_linea if ref.t_c_linea is not None and ref.t_c_linea <= hasta_linea else None,
        "pedido": ref.pedido if ref.t_r_linea is not None and ref.t_r_linea <= hasta_linea else None,
    }
    return {"clase_conversacion": ref.clase, "marcas": marcas,
            "supervision": supervision,
            "provisional": not ref.revision_humana,
            "motivo": ("" if ref.revision_humana
                       else "referencia sin revisión humana: provisional, no habilita uso.")}


# ---------------------------------------------------------------------------
# Validación de particiones
# ---------------------------------------------------------------------------

def _ambiguedad(ref: Referencia, n_lineas: int) -> str | None:
    if ref.clase in ("legitima", "legitima_dificil"):
        if ref.t_r_linea is not None or ref.t_c_linea is not None:
            return "legítima con marcas t_r/t_c: ambigua hasta resolución o exclusión."
        return None
    if ref.t_r_linea is not None and ref.pedido is None:
        return "pedido y t_r_linea van juntos: falta uno."
    if ref.t_c_linea is not None and ref.t_r_linea is None:
        return "t_c_linea requiere t_r_linea: no hay cumplimiento sin pedido."
    if (ref.t_r_linea is not None and
            not any(isinstance(e, dict) and e.get("linea") == ref.t_r_linea
                    and e.get("evento") == "pedido" for e in ref.evidencia)):
        return f"falta evidencia 'pedido' en t_r_linea={ref.t_r_linea}."
    return None


def validar_particiones(conversaciones: list[Conversacion],
                        asignacion: dict[str, str],
                        familias_artefacto: set[str] | None = None) -> InformeValidacion:
    """Rechaza cruces, duplicados incompatibles y referencias inválidas.

    Un informe con errores no es evaluable: el recorrido nunca presenta un
    conjunto inválido como evaluación válida (`es_evaluable=False`).
    """
    errores: list[str] = []
    advertencias: list[str] = []
    por_id = {c.case_id: c for c in conversaciones}
    desconocidas = sorted(set(asignacion) - set(por_id))
    errores += [f"{c}: asignada pero sin conversación cargada." for c in desconocidas]
    sin_asignar = sorted(set(por_id) - set(asignacion))
    errores += [f"{c}: conversación sin partición asignada." for c in sin_asignar]
    for c, p in asignacion.items():
        if p not in PARTICIONES:
            errores.append(f"{c}: partición {p!r} fuera de {list(PARTICIONES)}.")
        if es_identificador_reserva(c) or p == "test_reservado":
            errores.append(f"{c}: la reserva no entra a esta exploración (no se lee ni usa).")
    for c in por_id:
        if por_id[c].referencia is None:
            errores.append(f"{c}: falta referencia: no evaluable hasta resolver o excluir.")
        else:
            motivo = _ambiguedad(por_id[c].referencia, len(por_id[c].lineas))
            if motivo:
                errores.append(f"{c}: referencia ambigua: {motivo}")
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
    for c, conv in por_id.items():
        par = conv.referencia.par if conv.referencia else None
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
    vistos: dict[str, str] = {}
    for c in sorted(por_id):
        if c not in asignacion:
            continue
        for n, linea in enumerate(por_id[c].lineas, start=1):
            texto = _normalizar(linea.texto)
            anterior = vistos.setdefault(texto, f"{c}#{n}")
            if anterior.split("#")[0] != c and por_id[anterior.split('#')[0]].referencia is not None \
                    and por_id[c].referencia is not None:
                ref_a = por_id[anterior.split("#")[0]].referencia
                ref_b = por_id[c].referencia
                if ref_a.clase != ref_b.clase and asignacion[anterior.split("#")[0]] != asignacion[c]:
                    errores.append(
                        f"duplicado incompatible entre particiones: {anterior} y {c}#{n} "
                        "mismo texto, distinta clase.")
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
    """La evaluación independiente no comparte casos con diagnóstico ni ajuste."""
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
                       semilla: int = 42) -> dict:
    """Manifiesto determinista: otra persona comprueba procedencia y separación."""
    huellas = {c.case_id: huella("\n".join(f"{l.hablante}: {l.texto}" for l in c.lineas))
               for c in sorted(conversaciones, key=lambda c: c.case_id)}
    revision = sum(1 for c in conversaciones
                   if c.referencia is not None and c.referencia.revision_humana)
    return {
        "fecha": date.today().isoformat(),
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
        "habilitado": False,
        "bloqueo": ("Sin revisión humana efectiva ni acuerdo de composición y "
                     "proporciones (D07/D08): propuesta preparada, uso no habilitado. "
                     "No se inventan revisores, acuerdos, cuotas ni etiquetas revisadas."),
    }


def puede_habilitarse(informe: dict, revision_efectiva: dict | None = None,
                      acuerdo: dict | None = None) -> tuple[bool, list[str]]:
    """Puerta explícita: sin evidencia de revisión y acuerdo, bloquea.

    `revision_efectiva` y `acuerdo` los aporta el equipo fuera de este módulo
    (quién revisó, desacuerdos, adjudicación, composición acordada); este
    módulo nunca los inventa: por defecto informa el bloqueo exacto.
    """
    motivos = []
    if not informe.get("es_evaluable", False):
        motivos.append("Particiones inválidas: resolver errores antes de habilitar.")
    if revision_efectiva is None:
        motivos.append("Falta revisión humana efectiva del equipo "
                       "(originales, desacuerdos y adjudicaciones conservados).")
    if acuerdo is None:
        motivos.append("Falta acuerdo registrado de composición, tamaño, reglas de "
                       "referencia y proporciones (coordina con #32/#55 antes de "
                       "producir o habilitar material dependiente).")
    return (not motivos, motivos)
