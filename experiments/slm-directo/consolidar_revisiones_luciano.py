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
ORIGINAL_145 = "REVISION-145-LUCIANO-2026-11-07.json"
MAPA_145 = "CORRESPONDENCIA-145-LUCIANO-2026-11-07.json"
ORIGINAL_144 = "FICHAS-144-LUCIANO-INGLES-2026-11-07.md"
SALIDA = "REVISIONES-LUCIANO-2026-11-07.jsonl"


def filas_145(original: bytes, mapa: dict) -> list[dict]:
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
            "issue": 145, "fecha": "2026-11-07", "revisor": fuente["revisor"],
            "case_id": caso["case_id"], "alias_revision": alias,
            "archivo_original": ORIGINAL_145, "selector_original": f"/respuestas/{alias}",
            "texto_sha256": caso["texto_sha256"], "juicio_estafa": respuesta["estafa"],
            "credibilidad": respuesta["credibilidad"], "unidad_marcas": "linea_dialogo",
            "sospecha": respuesta["sospecha"], "sospecha_marca": respuesta["sospecha_linea"] or None,
            "pedido": respuesta["pedido"], "pedido_marca": respuesta["pedido_linea"] or None,
            "cumplimiento": respuesta["cumplimiento"], "cumplimiento_marca": respuesta["cumplimiento_linea"] or None,
            "confirmada_en_formulario": respuesta["completa"],
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


def main() -> None:
    registros = filas_144((CORPUS / ORIGINAL_144).read_text(encoding="utf-8"))
    registros += filas_145((CORPUS / ORIGINAL_145).read_bytes(), json.loads((CORPUS / MAPA_145).read_text()))
    (CORPUS / SALIDA).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in registros), encoding="utf-8")
    print(f"{len(registros)} anotaciones individuales; sin adjudicar ni modificar los originales.")


if __name__ == "__main__":
    main()
