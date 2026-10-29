"""Compara el ASR Parakeet por frases con y sin el filtro de idioma, sobre llamadas grabadas (#94).

Para cada llamada de VoIP con Parakeet, lee `estereo.wav` (izquierdo = protegida, derecho = otra) y
pasa cada canal en bloques de 40 ms, como el servidor, con la segmentación del encabezado de
`actualizaciones.jsonl`. Corre dos configuraciones: la vieja (primer parcial con 0,3 s de voz, sin
filtro) y la nueva (1,0 s de voz y filtro). Las transcripciones van a `--salida`, que tiene que quedar
fuera de Git (por defecto `experiments/voip/llamadas/_filtro_idioma/`).

    python comparar_filtro_idioma.py --prefijo 2026-10-28
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf

from motores import MotorSherpaParakeet

RAIZ = Path(__file__).resolve().parents[2]
LLAMADAS = RAIZ / "experiments" / "voip" / "llamadas"
BLOQUE_S = 0.04
CANALES = {"protegida": 0, "otra": 1}
# Criterio independiente del filtro (no usa sus listas).
INGLES = re.compile(r"\b(the|you|yeah|what|it's|oh|uh|boy|one|thank)\b|olá|obrigad", re.IGNORECASE)


def llamadas_parakeet(prefijo: str) -> list[Path]:
    salida = []
    for d in sorted(LLAMADAS.glob(f"{prefijo}_*")):
        if (d / "manifiesto.json").exists() and json.loads((d / "manifiesto.json").read_text())["config"].get("asr") == "parakeet":
            salida.append(d)
    return salida


def correr(motor: MotorSherpaParakeet, audio: np.ndarray, canal: str) -> list[dict]:
    motor.nueva_sesion()
    paso = int(BLOQUE_S * motor.sample_rate)
    eventos = []
    for i in range(0, len(audio), paso):
        bloque = audio[i:i + paso]
        t = i / motor.sample_rate
        eventos += motor.procesar_bloque(bloque, t, t + len(bloque) / motor.sample_rate)
    eventos += motor.vaciar_final(len(audio) / motor.sample_rate)
    return [{"canal": canal, "tipo": e.tipo, "segmento": e.segmento, "texto": e.texto,
             "inicio": e.inicio_audio_s, "fin": e.fin_audio_s} for e in eventos]


def configurar(motor: MotorSherpaParakeet, seg: dict, nueva: bool) -> None:
    motor.corte_silencio_s = seg["corte_silencio_s"]
    motor.umbral_rms_silencio = seg["umbral_rms_silencio"]
    motor.MIN_VOZ_PARCIAL_S = 1.0 if nueva else 0.3  # atributo de instancia: pisa la constante
    motor.filtrar_idioma = nueva


def percentil(valores: list[float], p: float) -> float:
    return float(np.percentile(valores, p)) if valores else float("nan")


def resumen(eventos: list[dict]) -> dict:
    parciales = [e for e in eventos if e["tipo"] == "parcial"]
    ingles = [e for e in parciales if INGLES.search(e["texto"])]
    primeros: dict[tuple, dict] = {}
    for e in parciales:
        primeros.setdefault((e["canal"], e["inicio"]), e)
    demoras = [e["fin"] - e["inicio"] for e in primeros.values()]
    return {"parciales": len(parciales), "ingles": ingles, "demoras": demoras}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--prefijo", default="2026-10-28", help="fecha de las carpetas de llamadas")
    ap.add_argument("--salida", type=Path, default=LLAMADAS / "_filtro_idioma")
    ap.add_argument("--hilos", type=int, default=2)
    args = ap.parse_args()
    args.salida.mkdir(parents=True, exist_ok=True)

    motor = MotorSherpaParakeet(str(RAIZ / "experiments/asr-local/modelos/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8"),
                                hilos=args.hilos)
    motor.inicializar()
    codigo = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=RAIZ, capture_output=True, text=True).stdout.strip()
    total = {"vieja": [], "nueva": []}
    cambios = []
    print(f"codigo {codigo}")
    print("llamada | corte | parciales v/n | parciales en inglés v/n | audio de los de inglés (s) vieja -> nueva")
    for d in llamadas_parakeet(args.prefijo):
        seg = json.loads(d.joinpath("actualizaciones.jsonl").open().readline())["meta"]["segmentacion"]
        audio, hz = sf.read(d / "estereo.wav", dtype="float32")
        assert hz == motor.sample_rate
        corridas = {}
        for nombre in ("vieja", "nueva"):
            configurar(motor, seg, nombre == "nueva")
            corridas[nombre] = [e for canal, col in CANALES.items() for e in correr(motor, audio[:, col], canal)]
            total[nombre] += corridas[nombre]
        (args.salida / f"{d.name}.json").write_text(json.dumps(corridas, ensure_ascii=False, indent=1), encoding="utf-8")
        v, n = resumen(corridas["vieja"]), resumen(corridas["nueva"])
        aud = lambda r: [round(e["fin"] - e["inicio"], 1) for e in r["ingles"]]
        print(f"{d.name} | {seg['corte_silencio_s']} | {v['parciales']}/{n['parciales']} | "
              f"{len(v['ingles'])}/{len(n['ingles'])} | {aud(v)} -> {aud(n)}")
        fv = {(e["canal"], e["inicio"]): e["texto"] for e in corridas["vieja"] if e["tipo"] == "final"}
        fn = {(e["canal"], e["inicio"]): e["texto"] for e in corridas["nueva"] if e["tipo"] == "final"}
        for clave in sorted(set(fv) | set(fn)):
            if fv.get(clave) != fn.get(clave):
                cambios.append((d.name, clave[0], clave[1], fv.get(clave), fn.get(clave)))
    v, n = resumen(total["vieja"]), resumen(total["nueva"])
    print("\nTOTAL")
    for nombre, r in (("vieja", v), ("nueva", n)):
        cortos = [e for e in r["ingles"] if e["fin"] - e["inicio"] < 1.5]
        print(f"{nombre}: parciales {r['parciales']}, con inglés {len(r['ingles'])} "
              f"(con <1,5 s de audio: {len(cortos)}), demora del primer parcial mediana "
              f"{statistics.median(r['demoras']):.2f} s, p90 {percentil(r['demoras'], 90):.2f} s, frases {len(r['demoras'])}")
    print(f"\nFinales que difieren: {len(cambios)}")
    for llamada, canal, inicio, vieja, nueva in cambios:
        print(f"  {llamada} {canal} @{inicio}s: vieja={vieja!r} nueva={nueva!r}")
    print("\nParciales en inglés de la nueva:")
    for e in n["ingles"]:
        print(f"  {e['canal']} {e['fin'] - e['inicio']:.1f} s: {e['texto']!r}")


if __name__ == "__main__":
    main()
