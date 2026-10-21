#!/usr/bin/env python3
"""Suite de texto y transcripciones en bloques, con el encoder solo y con la cascada encoder -> SLM.

Mismas columnas que resultados/2026-09-24 mas `turnos_zona_gris` y `memoria_slm_mb`.
Corre dentro del contenedor (torch + SLM en http://slm:11434/v1). No cierra D09.

    python correr_cascada.py texto        # 21 casos + ejemplo + 5 dificiles + _suite, por detector
    python correr_cascada.py transcripciones artifacts/corrida-*.json  # texto ASR guardado, en bloques
"""

import csv
import gc
import hashlib
import json
import os
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

import chequear_casos as ch
import correr_encoders as ce
import detector
import pipeline
import rules

AQUI = Path(__file__).resolve().parent
FECHA_DIR = "2026-09-28"
SALIDA = AQUI / "resultados" / FECHA_DIR
ENCODER = os.environ.get("ENCODER_MODEL", detector.ENCODER_DEFAULT)
SLM = os.environ.get("LLM_MODEL", detector.MODELO_DEFAULT)
DETECTORES = {
    "encoder": f"{ENCODER}+LR",
    "cascada": f"cascada:{ENCODER}+LR->{SLM}",
}
EXTRA = ("turnos_zona_gris", "memoria_slm_mb")
NOTA = (
    "Modo texto. Cabeza LR entrenada con semillas provisorias (turnos ASR de 8 grabaciones AR de YouTube "
    "distintas de las de evaluacion + ES-Port legitimo), ver semillas_manifiesto.json. "
    "{det}. No cierra D09. T_A = turno de goteo. T_R = primer incendio. "
    "Sin audio: T_C, L_C, Preventive@δ, WER y RTF no aplican."
)
NOTA_CASCADA = "Zona gris 0.35-0.75 (ejemplo de PR #40, sin calibrar): ahi puntua el SLM con historial"


def correr(det, path: Path) -> dict:
    """Como correr_encoders.correr, pero pasa el historial (lo usa el SLM de la cascada)."""
    textos = [
        linea.strip()
        for linea in Path(path).read_text(encoding="utf-8").splitlines()
        if linea.strip() and not linea.strip().startswith("#")
    ]
    grises0 = getattr(det, "n_zona_gris", 0)
    contador = pipeline.ContadorGoteo(ce.UMBRAL)
    turnos, eventos, historial = [], [], []
    turno_incendio = turno_goteo = None
    for n, texto in enumerate(textos, 1):
        etiquetas = rules.incendio_en(texto)
        if etiquetas:
            eventos.append({"turno": n, "etiquetas": sorted(etiquetas), "texto": texto})
            if turno_incendio is None:
                turno_incendio = n
        p = det.puntaje(texto, historial)
        if contador.agregar(p) and turno_goteo is None:
            turno_goteo = n
        turnos.append({"n": n, "texto": texto, "puntaje": pipeline._puntaje(p)})
        historial.append(texto)
    texto_final = " ".join(textos)
    ns = [n for n in (turno_incendio, turno_goteo) if n is not None]
    return {
        "turnos": turnos,
        "incendio": {"eventos": eventos},
        "goteo": {"disparo": turno_goteo is not None, "turno": turno_goteo},
        "latencia_decision_turno": min(ns) if ns else None,
        "terminos_criticos": {t: t in texto_final.lower() for t in pipeline.TERMINOS_CRITICOS},
        "memoria_pico_mb": pipeline.memoria_pico_mb(),
        "zona_gris": getattr(det, "n_zona_gris", 0) - grises0 if hasattr(det, "n_zona_gris") else None,
    }


def ok_robusto(det, rel: str, limpio: dict, modo: str) -> int:
    with tempfile.NamedTemporaryFile("w", suffix=".txt", encoding="utf-8") as f:
        f.write("\n".join(ch._perturbar(ce._leer(rel), modo)) + "\n")
        f.flush()
        return int(ce._igual(limpio, correr(det, Path(f.name))))


def _fila(rel, clase, r, etiquetas, fecha, commit, modelo, nota) -> dict:
    fila = ce.fila_de(rel, clase, r, etiquetas, fecha, commit, modelo)
    fila["nota"] = nota
    fila["turnos_zona_gris"] = "" if r["zona_gris"] is None else f"{r['zona_gris']}/{len(r['turnos'])}"
    fila["memoria_slm_mb"] = ""
    return fila


def suite(tipo: str, fecha: str, commit: str) -> Path:
    os.environ["DETECTOR"] = tipo
    t0 = time.perf_counter()
    det = detector.crear(hilos=2)
    modelo = DETECTORES[tipo]
    nota = NOTA.format(det=NOTA_CASCADA if tipo == "cascada" else "Encoder solo, sin SLM")
    casos = [(rel, clase, et, turno) for rel, clase, et, turno, _ in ch.ESPERADO]
    casos += [(rel, clase, et, 1 if clase == "V" else None) for rel, clase, et in ce.DIFICILES]
    filas = []
    for rel, clase, etiquetas, turno in casos:
        r = correr(det, ce.CASOS / rel)
        fila = _fila(rel, clase, r, etiquetas, fecha, commit, modelo,
                     ("Caso dificil (no entra al oracle). " if rel.startswith("dificiles/") else "") + nota)
        fila["typo_ok"] = ce.ok_typo(rel, clase, etiquetas, turno)
        for modo in ("upper", "tildes", "muletilla"):
            fila[f"robusto_{modo}"] = ok_robusto(det, rel, r, modo)
        filas.append(fila)
        print(f"  {tipo} {rel} goteo={fila['goteo']} tA={fila['T_A_turno']} gris={fila['turnos_zona_gris']}", flush=True)
    r_ej = correr(det, AQUI / "ejemplo.txt")
    filas.append(_fila("ejemplo.txt", "ejemplo", r_ej, {"REQUEST_AUTH_CODE"}, fecha, commit, modelo, nota))

    duracion_s = round(time.perf_counter() - t0, 3)
    stats = det.stats() if hasattr(det, "stats") else {}
    nota_suite = (
        "Resumen de los 21 casos mas los 5 dificiles (ejemplo aparte). "
        "Semillas provisorias de laboratorio, no corpus ni piloto (#41). "
        "precision/recall/F1 del goteo como alerta, V=positivo. mediana de L_R en L_R_turnos. "
        "AUROC/AUPRC usan el puntaje maximo del caso."
    )
    if stats:
        nota_suite += (
            f" Cascada: {stats['n_zona_gris']}/{stats['n_turnos']} turnos al SLM "
            f"(respondio {stats['n_slm_ok']}); ms p50 encoder={stats['ms_encoder_p50']} "
            f"SLM={stats['ms_slm_p50']}. Incluye las pasadas de robustez."
        )
    resumen = ce._resumen(filas, fecha, commit, modelo, nota_suite)
    resumen["duracion_s"] = duracion_s
    resumen["turnos_zona_gris"] = f"{stats['n_zona_gris']}/{stats['n_turnos']}" if stats else ""
    resumen["memoria_slm_mb"] = stats.get("slm_mem_mb") or "" if stats else ""
    for f in filas:
        f["duracion_s"] = duracion_s
    slug = "cascada-robertuito-" + SLM.replace(":", "-").split("/")[-1] if tipo == "cascada" else ENCODER.split("/")[-1]
    out = SALIDA / f"resultados-{FECHA_DIR}-{slug}.csv"
    _escribir(out, filas + [resumen])
    print(f"{tipo}: {duracion_s}s goteo {resumen['goteo']} falsas {resumen['falsa_alarma']} -> {out.name}", flush=True)
    del det
    gc.collect()
    return out


def _escribir(out: Path, filas: list[dict]) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0].keys()))
        w.writeheader()
        w.writerows(filas)


PALABRAS_POR_BLOQUE = 25
RECORTE = f"bloques fijos de {PALABRAS_POR_BLOQUE} palabras, sin solapamiento (el cortador de turnos no esta definido)"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


def partir(texto: str, n: int = PALABRAS_POR_BLOQUE) -> list[str]:
    palabras = texto.split()
    return [" ".join(palabras[i : i + n]) for i in range(0, len(palabras), n)]


def transcripciones(corridas: list[Path], fecha: str, commit: str) -> Path:
    """Texto plano del ASR de cada grabacion -> bloques -> reglas + goteo, sin audio."""
    bloques_dir = AQUI / "artifacts" / "transcripciones"
    bloques_dir.mkdir(parents=True, exist_ok=True)
    entradas = []
    for c in corridas:
        d = json.loads(c.read_text(encoding="utf-8"))
        vid = c.stem[-11:]
        archivo = bloques_dir / f"{c.stem.removeprefix('corrida-')}-bloques{PALABRAS_POR_BLOQUE}.txt"
        archivo.write_text("\n".join(partir(d["texto_final"])) + "\n", encoding="utf-8")
        entradas.append((c, d, vid, archivo))
    filas = []
    for tipo in ("encoder", "cascada"):
        os.environ["DETECTOR"] = tipo
        det = detector.crear(hilos=2)
        for c, d, vid, archivo in entradas:
            t0 = time.perf_counter()
            r = correr(det, archivo)
            fila = _fila(c.stem.removeprefix("corrida-"), "V", r, set(), fecha, commit, DETECTORES[tipo],
                         "Texto plano (salida ASR guardada), sin audio. Grabacion AR editada por medios: incluye narracion. "
                         "Todas las grabaciones son estafas: falsa_alarma no aplica. Semillas provisorias (#41).")
            fila["duracion_s"] = round(time.perf_counter() - t0, 3)
            fila["cobertura_etiquetas"] = ""
            fila["falsa_alarma"] = ""
            st = det.stats() if hasattr(det, "stats") else {}
            fila["memoria_slm_mb"] = st.get("slm_mem_mb") or ""
            fila.update({
                "video_url": f"https://www.youtube.com/watch?v={vid}",
                "duracion_audio_s": d["duracion_s"],
                "texto_fuente": f"experiments/laboratorio/artifacts/{c.name} (texto_final, sha256:{_sha(c)})",
                "asr_texto_fuente": f"{d['asr']} @ {d['fecha_utc']}",
                "recorte": RECORTE,
                "archivo_bloques": f"experiments/laboratorio/artifacts/transcripciones/{archivo.name} (sha256:{_sha(archivo)})",
                "palabras": len(d["texto_final"].split()),
            })
            filas.append(fila)
            print(f"  {tipo} {c.stem} bloques={fila['n_turnos']} goteo={fila['goteo']} tA={fila['T_A_turno']} "
                  f"tR={fila['T_R_turno']} gris={fila['turnos_zona_gris']}", flush=True)
        del det
        gc.collect()
    out = SALIDA / f"resultados-{FECHA_DIR}-transcripciones.csv"
    _escribir(out, filas)
    return out


def main() -> None:
    commit = os.environ.get("COMMIT", "")
    fecha = datetime.now().astimezone().isoformat(timespec="seconds")
    if sys.argv[1:2] == ["texto"]:
        for tipo in sys.argv[2:] or ("encoder", "cascada"):
            suite(tipo, fecha, commit)
    elif sys.argv[1:2] == ["transcripciones"]:
        print(transcripciones([Path(p) for p in sys.argv[2:]], fecha, commit).name, flush=True)
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
