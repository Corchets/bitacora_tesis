"""Comprueba la revisión IA de desarrollo; no habilita datos ni ejecuta modelos.

Uso desde este directorio:
    python auditar_revision_tito.py > CONTROL-REVISION-IA-TITO-2026-10-28.json
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import asdict, replace
from pathlib import Path

from casos import cargar_referencia, cargar_texto
from datos_tito import (
    Conversacion,
    Referencia,
    auditar_banco_historico,
    etiquetar_prefijo,
    generar_manifiesto,
    informe_validacion,
    puede_habilitarse,
    rechazar_reserva,
    validar_particiones,
)

AQUI = Path(__file__).resolve().parent
REVISION = AQUI / "REVISION-IA-TITO-2026-10-28.json"


def sha(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def auditar() -> dict:
    revision = json.loads(REVISION.read_text(encoding="utf-8"))
    # Rechazar identificadores antes de abrir cualquier contenido de casos.
    ids = sorted(p.stem for p in (AQUI / "casos/texto").glob("*.txt"))
    ids_ref = sorted(p.stem for p in (AQUI / "casos/referencia").glob("*.json"))
    rechazar_reserva(ids + ids_ref)
    if ids != ids_ref:
        raise ValueError("Inventario no pareado: hay texto o referencia huérfanos.")
    registros = {cid: cargar_referencia(cid) for cid in ids}
    rechazar_reserva(ids, {cid: r.get("particion", "desarrollo")
                          for cid, r in registros.items()})
    if any(r.get("particion", "desarrollo") != "desarrollo"
           for r in registros.values()):
        raise ValueError("Este control solo acepta desarrollo.")
    conversaciones = []
    huellas = {}
    for cid, ref in registros.items():
        conversaciones.append(Conversacion(
            case_id=cid, lineas=tuple(cargar_texto(cid)),
            referencia=Referencia(**{k: ref[k] for k in Referencia.__dataclass_fields__}),
            semilla=ref["semilla"], modalidad=ref.get("familia")))
        huellas[cid] = {
            "texto_sha256": sha(AQUI / "casos/texto" / f"{cid}.txt"),
            "referencia_sha256": sha(AQUI / "casos/referencia" / f"{cid}.json"),
        }
    errores_revision = []
    ids_revisados = []
    propuestas = {}
    for r in revision["casos"]:
        cid = r["case_id"]
        rechazar_reserva([cid])
        if cid not in registros:
            raise ValueError(f"Caso revisado ajeno al inventario: {cid}")
        ids_revisados.append(cid)
        if (r["texto_sha256"] != huellas[cid]["texto_sha256"]
                or r["referencia_original_sha256"] != huellas[cid]["referencia_sha256"]):
            errores_revision.append(f"{cid}: las fuentes cambiaron desde la revisión IA.")
        propuesta = Referencia(**r["referencia_propuesta_ia"])
        if propuesta.revision_humana is not False:
            errores_revision.append(f"{cid}: una propuesta IA no es revisión humana.")
        propuestas[cid] = propuesta
        for ev in r["soporte"]:
            crudo = (AQUI / "casos/texto" / f"{cid}.txt").read_text(encoding="utf-8")
            if crudo.splitlines()[ev["linea"] - 1] != ev["texto"]:
                errores_revision.append(f"{cid}: cita que no coincide con su línea.")
    if len(set(ids_revisados)) != len(ids_revisados):
        errores_revision.append("Identificadores repetidos en la revisión IA.")
    if errores_revision:
        raise ValueError("\n".join(errores_revision))

    # Única partición de humo: no es una propuesta de split experimental.
    asignacion = {cid: "regresion" for cid in ids}
    validacion = validar_particiones(conversaciones, asignacion)
    validacion_propuestas = validar_particiones(
        [replace(c, referencia=propuestas.get(c.case_id, c.referencia))
         for c in conversaciones], asignacion)
    if validacion_propuestas.errores:
        raise ValueError("\n".join(validacion_propuestas.errores))
    manifiesto = generar_manifiesto(
        {"revision_ia_sha256": sha(REVISION)},
        {"uso": "control estructural, todas en regresion; no split experimental"},
        asignacion, conversaciones, fecha=revision["fecha"])
    informe = informe_validacion(manifiesto, validacion, {})
    habilitado, motivos = puede_habilitarse(informe)
    banco = auditar_banco_historico()
    legitimas_pedido = [cid for cid, r in registros.items()
                       if r["clase"] != "vishing"
                       and any(e["evento"] == "pedido" for e in r["evidencia"])]
    legitimas_request = [cid for cid, r in registros.items()
                        if r["clase"] != "vishing"
                        and any(t.startswith("REQUEST_") for e in r["evidencia"]
                                for t in e["etiquetas"])]
    sin_pedido = [cid for cid, r in registros.items()
                 if r["clase"] == "vishing" and r["t_r_linea"] is None]
    ejemplos = []
    for cid, linea in (("CV2-D-L-SOPORTE-001", 6),
                       ("TR-13-turno-medico-pide-dni", 5),
                       ("TR-08-frase-cortada-candado", 3)):
        c = next(c for c in conversaciones if c.case_id == cid)
        ejemplos.append({"case_id": cid, "hasta_linea": linea,
                         "salida": etiquetar_prefijo(c, linea)})
    return {
        "fecha": revision["fecha"], "revision_ia_sha256": sha(REVISION),
        "script_sha256": sha(Path(__file__)),
        "fuentes_codigo_sha256": {n: sha(AQUI / n) for n in
                                  ("casos.py", "datos_tito.py", "entrenar_tito.py")},
        "inventario": {"total": len(ids),
                       "grupos": dict(Counter(r["grupo"] for r in registros.values())),
                       "clases": dict(Counter(r["clase"] for r in registros.values())),
                       "revision_humana": sum(r["revision_humana"] for r in registros.values()),
                       "huellas_archivos": huellas},
        "alcance_semantico": {"total": len(ids_revisados), "ids": ids_revisados,
                             "dictamenes": dict(Counter(r["dictamen_ia"] for r in revision["casos"]))},
        "observaciones_estructurales": {"legitimas_evento_pedido": legitimas_pedido,
                                      "legitimas_etiqueta_request": legitimas_request,
                                      "vishing_sin_pedido": sin_pedido},
        "ejemplos_supervision": ejemplos,
        "banco": {k: banco[k] for k in ("procedencia", "versiones", "exclusiones")},
        "control_estructural_regresion": asdict(validacion),
        "control_estructural_con_propuestas_ia": asdict(validacion_propuestas),
        "habilitado": habilitado, "motivos_no_habilitacion": motivos,
        "limites": ["Sin anotaciones humanas ni acuerdos; no cambia el estado de #96.",
                    "No audita independencia semántica de los 150 ni material no declarado.",
                    "No lee la reserva ni ejecuta detectores; no mide calidad aprendida."]}


if __name__ == "__main__":
    print(json.dumps(auditar(), ensure_ascii=False, indent=2, sort_keys=True))
