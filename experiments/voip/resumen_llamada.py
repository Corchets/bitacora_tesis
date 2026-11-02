#!/usr/bin/env python3
"""Ficha de cada llamada de la prueba por Meet (#84, #85, #86, #94), armada desde sus registros.

Lee `manifiesto.json`, `detector.jsonl` y `actualizaciones.jsonl`, y reconoce el diálogo de
`asr-local/voz-real/dialogos.json` comparando lo transcripto con las líneas de cada rol. El parecido
ayuda a ubicar la llamada: no es una medida del ASR, de eso se ocupa `medir_voz_real.py`.

Uso:
    python resumen_llamada.py --desde 2026-11-02_180000
    python resumen_llamada.py --desde 2026-11-02_180000 --voz-protegida luciano --voz-otra otra --tele <id>
"""

from __future__ import annotations

import argparse
import statistics
import sys
from difflib import SequenceMatcher
from pathlib import Path

DIR_VOIP = Path(__file__).resolve().parent
sys.path.insert(0, str(DIR_VOIP.parent / "asr-local"))

import historial
from dialogos import Dialogo, cargar_dialogos

PARECIDO_MINIMO = 0.5  # por debajo, la llamada no sigue ningún diálogo (por ejemplo, un ejemplo TTS)


def _normalizar(texto: str) -> str:
    return " ".join("".join(c for c in texto.lower() if c.isalnum() or c.isspace()).split())


def finales_por_canal(actualizaciones: list[dict]) -> dict[str, str]:
    textos: dict[str, list[str]] = {"protegida": [], "otra": []}
    for a in actualizaciones:
        if a.get("tipo") == "final" and a.get("canal") in textos:
            textos[a["canal"]].append(a.get("texto", ""))
    return {canal: _normalizar(" ".join(t)) for canal, t in textos.items()}


def reconocer_dialogo(finales: dict[str, str], dialogos: dict[str, Dialogo]) -> tuple[str | None, float]:
    """El diálogo más parecido a lo transcripto, por rol: (id o None, parecido de 0 a 1)."""
    mejor, parecido = None, 0.0
    for d in dialogos.values():
        por_rol = [SequenceMatcher(None, finales[r], _normalizar(" ".join(l.texto for l in d.del_rol(r))), autojunk=False).ratio()
                   for r in finales]
        if sum(por_rol) / len(por_rol) > parecido:
            mejor, parecido = d.id, sum(por_rol) / len(por_rol)
    return (mejor, parecido) if parecido >= PARECIDO_MINIMO else (None, parecido)


def ficha(carpeta: Path, dialogos: dict[str, Dialogo]) -> dict:
    manifiesto, actualizaciones, detector = historial._leer_carpeta(carpeta)
    m = manifiesto or {}
    config = m.get("config", {})
    segmentacion = m.get("asr", {}).get("segmentacion", {})
    vad = segmentacion.get("vad", {})
    aviso = m.get("detector", {}).get("aviso")
    consultas = [e["ms_detector"] / 1000 for e in detector
                 if e.get("consulta", "x") != "omitida" and e.get("ms_detector") is not None]
    con_tito = any("consulta" in e for e in detector)
    activacion = next((e for e in detector if e.get("indicio_linea") is not None), None)
    d_id, parecido = reconocer_dialogo(finales_por_canal(actualizaciones), dialogos)
    return {
        "id": carpeta.name, "dialogo": d_id, "parecido": round(parecido, 2),
        "asr": config.get("asr"), "corte_s": config.get("corte_silencio_s"),
        # El umbral que usó el motor: Silero solo no usa el RMS, aunque `config` traiga el de la llamada.
        "umbral_rms": segmentacion.get("umbral_rms_silencio"), "umbral_silero": vad.get("umbral"),
        "detector": config.get("detector"), "modelo": config.get("modelo"),
        "aviso": aviso is not None, "t_a": aviso.get("t_a") if aviso else None,
        "motivo": aviso.get("motivo", "") if aviso else "", "evidencia": aviso.get("evidencia", "") if aviso else "",
        "tito_linea": activacion.get("indicio_linea") if activacion else None,
        "tito_puntaje": round(activacion["indicio_puntaje"], 2) if activacion and activacion.get("indicio_puntaje") is not None else None,
        "sin_consulta": sum(e.get("consulta") == "omitida" for e in detector) if con_tito else None,
        "consultas": len(consultas),
        "primera_s": round(consultas[0], 2) if consultas else None,
        "mediana_s": round(statistics.median(consultas), 2) if consultas else None,
        "maximo_s": round(max(consultas), 2) if consultas else None,
        "salteadas": m.get("detector", {}).get("actualizaciones_salteadas"), "fallos": m.get("detector", {}).get("fallos"),
    }


def _celda(valor) -> str:
    if valor is None:
        return "—"
    if isinstance(valor, bool):
        return "sí" if valor else "no"
    return str(valor).replace(".", ",") if isinstance(valor, float) else str(valor)


COLUMNAS = (("id", "id"), ("dialogo", "Diálogo"), ("asr", "ASR"), ("corte_s", "Corte (s)"), ("umbral_rms", "RMS"),
            ("umbral_silero", "Silero"), ("modelo", "Modelo"), ("aviso", "¿Aviso?"), ("t_a", "T_A (s)"),
            ("tito_linea", "Tito activó en"), ("tito_puntaje", "Puntaje"), ("sin_consulta", "Sin consulta"),
            ("consultas", "Consultas"), ("primera_s", "1.ª (s)"), ("mediana_s", "Mediana (s)"), ("maximo_s", "Máx. (s)"),
            ("salteadas", "Salteadas"), ("fallos", "Fallos"))


def tabla(fichas: list[dict]) -> str:
    filas = ["| " + " | ".join(t for _, t in COLUMNAS) + " |", "|" + "---|" * len(COLUMNAS)]
    filas += ["| " + " | ".join(_celda(f[c]) for c, _ in COLUMNAS) + " |" for f in fichas]
    citas = [f"- `{f['id']}`: {f['motivo']} «{f['evidencia']}»" for f in fichas if f["aviso"]]
    return "\n".join(filas + ([""] + citas if citas else []))


def filas_de_pruebas(fichas: list[dict], voz_protegida: str, voz_otra: str, tele: set[str]) -> list[str]:
    """Las dos filas de `voz-real/pruebas.csv` de cada llamada que sigue un diálogo."""
    salida = []
    for f in fichas:
        if f["dialogo"] is None:
            continue
        condicion = "dialogo-tv" if f["id"] in tele else "dialogo"
        salida += [f"{f['id']},5,{voz_protegida},{condicion},{f['dialogo']},protegida,",
                   f"{f['id']},5,{voz_otra},{condicion},{f['dialogo']},otra,"]
    return salida


def main() -> None:
    p = argparse.ArgumentParser(description="Ficha de las llamadas de la prueba por Meet.")
    p.add_argument("--salida", default=str(DIR_VOIP / "llamadas"), help="carpeta con las llamadas")
    p.add_argument("--desde", default="", help="id desde el que se cuenta (ej. 2026-11-02_180000)")
    p.add_argument("--voz-protegida", default="luciano", help="quién estaba en el canal de la protegida")
    p.add_argument("--voz-otra", default="otra", help="quién estaba en el canal de la otra persona")
    p.add_argument("--tele", action="append", default=[], help="id de una llamada con la tele de fondo (dialogo-tv)")
    args = p.parse_args()
    dialogos = cargar_dialogos()
    carpetas = sorted(c for c in historial.carpetas_de_salida(Path(args.salida)) if c.name >= args.desde)
    fichas = [ficha(c, dialogos) for c in carpetas]
    print(tabla(fichas))
    filas = filas_de_pruebas(fichas, args.voz_protegida, args.voz_otra, set(args.tele))
    if filas:
        print("\nFilas para voz-real/pruebas.csv:\n" + "\n".join(filas))


if __name__ == "__main__":
    main()
