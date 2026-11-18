"""Genera la vista comparable de las anotaciones de Luciano de #144 y #145.

Desde la raíz: python3 experiments/slm-directo/consolidar_revisiones_luciano.py
Solo lee las fuentes publicadas en docs/corpus; no necesita datos privados ni modelos.
Los originales no se reescriben. No convierte dudas en clases ni turnos en líneas.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

CORPUS = Path(__file__).resolve().parents[2] / "docs/corpus"
# Captura vigente de #145; la del 2026-11-07 queda versionada como antecedente.
FECHA_145 = "2026-11-10"
ORIGINAL_145 = f"REVISION-145-LUCIANO-{FECHA_145}.json"
MAPA_145 = f"CORRESPONDENCIA-145-LUCIANO-{FECHA_145}.json"
ORIGINAL_144 = "FICHAS-144-LUCIANO-INGLES-2026-11-07.md"
COREANO_144 = "FICHAS-144-LUCIANO-COREANO-2026-11-10.md"
FUENTES_COREANO = {"KO-01": "vishing_540", "KO-02": "vishing_281"}
# Segunda tanda: solo las fichas llenadas; KO-10 a KO-12 siguen vacías y no se publican.
COREANO_144_B = "FICHAS-144-LUCIANO-COREANO-2026-11-11.md"
FUENTES_COREANO_B = {
    "KO-03": "vishing_577", "KO-04": "vishing_657", "KO-05": "vishing_443", "KO-06": "vishing_635",
    "KO-07": "vishing_298", "KO-08": "vishing_545", "KO-09": "vishing_349",
}
SALIDA = f"REVISIONES-LUCIANO-{FECHA_145}.jsonl"


def filas_145(original: bytes, mapa: dict, archivo: str = ORIGINAL_145, fecha: str = FECHA_145) -> list[dict]:
    fuente = json.loads(original)
    if fuente.get("issue") != 145 or fuente["muestra"] != mapa["muestra"]:
        raise ValueError("Muestra de #145 diferente de su correspondencia.")
    if hashlib.sha256(original).hexdigest() != mapa["archivo_original_sha256"]:
        raise ValueError("Cambió el original de #145; conservar esta captura y registrar otra versión.")
    if set(fuente["respuestas"]) != set(mapa["casos"]):
        raise ValueError("Las respuestas y la correspondencia no tienen los mismos alias.")
    salida = []
    for alias, respuesta in sorted(fuente["respuestas"].items()):
        caso = mapa["casos"][alias]
        if not caso["case_id"].startswith(("CV2-D-", "LEG-", "LEG2-")):
            raise ValueError("Solo se publican anotaciones de desarrollo en #145.")
        salida.append({
            "issue": 145, "fecha": fecha, "revisor": fuente["revisor"],
            "case_id": caso["case_id"], "alias_revision": alias,
            "archivo_original": archivo, "selector_original": f"/respuestas/{alias}",
            "texto_sha256": caso["texto_sha256"], "juicio_estafa": respuesta["estafa"],
            "credibilidad": respuesta["credibilidad"], "unidad_marcas": "linea_dialogo",
            "sospecha": respuesta["sospecha"], "sospecha_marca": respuesta["sospecha_linea"] or None,
            "pedido": respuesta["pedido"], "pedido_marca": respuesta["pedido_linea"] or None,
            "cumplimiento": respuesta["cumplimiento"], "cumplimiento_marca": respuesta["cumplimiento_linea"] or None,
            "confirmada_en_formulario": respuesta["completa"],
            "conocido_en_formulario": respuesta["conocido"], "aviso_previo": caso.get("aviso_previo"),
            "estado_revision": "anotacion_individual_sin_adjudicar",
        })
    return salida


def filas_144(texto: str) -> list[dict]:
    bloques = list(re.finditer(r"^## Fila (\d+) · (.+?) · (EXT-\d+|descartada)\s*$", texto, re.M))
    if len(bloques) != 20 or {int(b[1]) for b in bloques} != set(range(20)):
        raise ValueError("No se localizaron las veinte fichas originales de inglés.")
    salida = []
    for i, match in enumerate(bloques):
        cuerpo = texto[match.end():bloques[i + 1].start() if i + 1 < len(bloques) else len(texto)]
        campos = dict(re.findall(r"^- (.+?): (.*)$", cuerpo, re.M))
        def campo(nombre):
            if nombre not in campos:
                raise ValueError(f"Falta {nombre} en la fila {match[1]}.")
            return None if campos[nombre] == "—" else campos[nombre]
        salida.append({
            "issue": 144, "fecha": "2026-11-07", "revisor": "Luciano Grosso",
            "case_id": match[3] if match[3] != "descartada" else None,
            "alias_revision": match[2], "fila_csv_fuente": int(match[1]),
            "archivo_original": ORIGINAL_144, "selector_original": match[0],
            "juicio_estafa": campo("¿Es estafa?"), "credibilidad": campo("¿Creíble?"),
            "unidad_marcas": "turno_lectura", "sospecha_marca": campo("Turno de sospecha"),
            "pedido_marca": campo("Primer pedido de alto riesgo (turno)"),
            "cumplimiento_marca": campo("Primer cumplimiento (turno)"),
            "conservar_respuesta": campo("Conservar / descartar"),
            "descartada_del_set": match[3] == "descartada",
            "estado_revision": "anotacion_individual_sin_adjudicar",
        })
    return salida


def filas_144_coreano(texto: str, fuentes: dict = FUENTES_COREANO, archivo: str = COREANO_144,
                      fecha: str = "2026-11-10") -> list[dict]:
    bloques = list(re.finditer(r"^### Ficha (KO-\d+)\s*$", texto, re.M))
    if [b[1] for b in bloques] != list(fuentes):
        raise ValueError("Las fichas de coreano no coinciden con las esperadas.")
    salida = []
    for i, match in enumerate(bloques):
        cuerpo = texto[match.end():bloques[i + 1].start() if i + 1 < len(bloques) else len(texto)]
        campos = {k.split(" (")[0].strip(): v.strip() or None for k, v in re.findall(r"^- (.+?):(.*)$", cuerpo, re.M)}
        salida.append({
            "issue": 144, "fecha": fecha, "revisor": "Luciano Grosso",
            "case_id": None, "alias_revision": match[1], "fuente_id": fuentes[match[1]],
            "archivo_original": archivo, "selector_original": match[0],
            "juicio_estafa": campos["Leyendo la conversación entera, ¿es estafa?"],
            "credibilidad": campos["¿Es creíble como llamada?"], "unidad_marcas": "segmento_fuente",
            "sospecha_marca": campos["¿En qué segmento"], "pedido_marca": campos["Primer pedido de alto riesgo"],
            "cumplimiento_marca": campos["Primer cumplimiento"],
            "conservar_respuesta": campos["Conservar / descartar / revisar"],
            "estado_revision": "anotacion_individual_sin_adjudicar",
        })
    return salida


def main() -> None:
    registros = filas_144((CORPUS / ORIGINAL_144).read_text(encoding="utf-8"))
    registros += filas_144_coreano((CORPUS / COREANO_144).read_text(encoding="utf-8"))
    registros += filas_144_coreano((CORPUS / COREANO_144_B).read_text(encoding="utf-8"),
                                   FUENTES_COREANO_B, COREANO_144_B, "2026-11-11")
    registros += filas_145((CORPUS / ORIGINAL_145).read_bytes(), json.loads((CORPUS / MAPA_145).read_text()))
    (CORPUS / SALIDA).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in registros), encoding="utf-8")
    print(f"{len(registros)} anotaciones individuales; sin adjudicar ni modificar los originales.")


if __name__ == "__main__":
    main()
