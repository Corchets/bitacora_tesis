#!/usr/bin/env python3
"""Lo que el WER no muestra al comparar Silero VAD contra el RMS en Parakeet (#94, PLAN-VOZ-REAL.md §12).

Corre las variantes de Parakeet de `variantes_voz_real.py` (por defecto la del laboratorio, 0,8 s / 0,008, y
las de Silero) sobre las pruebas de `voz-real/pruebas.csv` y sobre las dos grabaciones sin texto, en bloques
de 40 ms como el panel, y cuenta por grabación:

- segmentos que se abrieron (incluidos los que se descartan por tener menos de `MIN_VOZ_S` de voz), cómo se
  cerró cada uno (silencio, tope de 10 s o fin del audio) y llamadas al ASR (borradores y finales);
- palabras que salieron como final o borrador: en las grabaciones sin texto, todas son inventadas;
- desfase del detector contra el RMS 0,008 al empezar y al terminar cada tramo de voz;
- costo de decidir voz o silencio en cada bloque (RMS o Silero), aparte del costo del ASR.

Con `--corrida` (la carpeta de `medir_voz_real.py` sobre las mismas variantes) agrega las frases cuya primera
palabra no aparece al principio de la transcripción y las de «Compartí pantalla». Para el segmento de
«pantalla» vuelve a transcribir con más audio previo: si así aparece «Compartí», el corte se comió el inicio;
si no, es del modelo.

Salida: `corridas/<fecha>_voz-real_vad-extras/` con `resumen.md` y `extras.json` (textos, sin audio).

    python comparar_vad.py --pruebas ../bitacora_tesis-voip-asr/experiments/voip/llamadas \\
        --corrida corridas/2026-10-29_voz-real_parakeet-silero-vs-rms
"""

from __future__ import annotations

import argparse
import json
import re
import shlex
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np

import medir_voz_real as MV
import variantes_voz_real as V
from guion import cargar_guion
from metricas_voz_real import _clave
from motores import DetectorSilero, MotorPorFrases

DIR_ASR = Path(__file__).resolve().parent
# Comentadas en voz-real/pruebas.csv: sin referencia, no entran en el WER.
SIN_TEXTO = {"2026-10-29_201018-775836": "G10 30 s sin hablar, tele apagada",
             "2026-10-29_193603-180243": "serie de fondo sin hablar"}
VARIANTES_POR_DEFECTO = (V.PARAKEET_LABORATORIO, "parakeet-0.8-silero-0.5", "parakeet-0.5-silero-0.5",
                         "parakeet-0.3-silero-0.5", "parakeet-0.5-silero-0.9", "parakeet-0.3-silero-0.9")
UMBRAL_FIN_DE_VOZ = 0.008  # el RMS contra el que se mide el desfase (el de la referencia del laboratorio)
MAX_DESFASE_S = 0.6  # un flanco del detector se empareja con el flanco RMS más cercano a menos de esto
PREVIO_EXTRA_S = (0.3, 0.6)  # cuánto audio más se antepone al segmento de «pantalla» para volver a transcribirlo
_PALABRA = re.compile(r"\w+")


# --- Corrida instrumentada ----------------------------------------------------------------------------------


def instrumentar(motor) -> dict[str, Any]:
    """Envuelve `_es_voz`, `_transcribir` y `_cerrar_frase` del motor para contar lo que hace en cada bloque."""
    registro: dict[str, Any] = {"decisiones": [], "decision_ms": [], "asr": [], "segmentos": []}
    # De la clase y no de la instancia: así, instrumentar otra vez para la grabación siguiente no anida envoltorios.
    clase = type(motor)
    es_voz, transcribir, cerrar = (getattr(clase, n).__get__(motor) for n in ("_es_voz", "_transcribir", "_cerrar_frase"))

    def _es_voz(muestras):
        t0 = time.perf_counter()
        corta, cuenta = es_voz(muestras)
        registro["decision_ms"].append((time.perf_counter() - t0) * 1000.0)
        registro["decisiones"].append(bool(corta))  # la que abre y cierra la frase
        return corta, cuenta

    def _transcribir(audio):
        t0 = time.perf_counter()
        texto = transcribir(audio)
        registro["asr"].append({"audio_s": round(len(audio) / motor.sample_rate, 3),
                                "ms": round((time.perf_counter() - t0) * 1000.0, 2), "texto": texto})
        return texto

    def _cerrar_frase(fin_s, t0):
        if motor.silencio_acum_s >= motor.corte_silencio_s:
            motivo = "silencio"
        elif fin_s - motor.inicio_segmento_s >= motor.MAX_FRASE_S:
            motivo = "tope"
        else:
            motivo = "fin_del_audio"
        inicio, voz_s, llamadas = motor.inicio_segmento_s, motor.voz_s, len(registro["asr"])
        eventos = cerrar(fin_s, t0)
        registro["segmentos"].append({"inicio_s": round(inicio, 3), "fin_s": round(fin_s, 3), "voz_s": round(voz_s, 3),
                                      "motivo": motivo, "transcripto": len(registro["asr"]) > llamadas,
                                      "texto": eventos[0].texto if eventos else ""})
        return eventos

    motor._es_voz, motor._transcribir, motor._cerrar_frase = _es_voz, _transcribir, _cerrar_frase
    return registro


def correr(motor, muestras: np.ndarray, bloque_ms: int) -> tuple[dict[str, Any], list]:
    motor.nueva_sesion()
    registro = instrumentar(motor)
    tam = int(bloque_ms / 1000 * V.SAMPLE_RATE)
    eventos = []
    for desde in range(0, len(muestras), tam):
        bloque = muestras[desde:desde + tam]
        eventos += motor.procesar_bloque(bloque, desde / V.SAMPLE_RATE, (desde + len(bloque)) / V.SAMPLE_RATE)
    eventos += motor.vaciar_final(len(muestras) / V.SAMPLE_RATE)
    return registro, eventos


def flancos(decisiones: list[bool], bloque_s: float) -> tuple[list[float], list[float]]:
    """Tiempos (fin del bloque) donde la decisión pasa a voz y donde vuelve a silencio."""
    sube, baja, antes = [], [], False
    for i, voz in enumerate(decisiones):
        if voz and not antes:
            sube.append(round((i + 1) * bloque_s, 3))
        elif antes and not voz:
            baja.append(round((i + 1) * bloque_s, 3))
        antes = voz
    return sube, baja


def desfases(detector: list[float], rms: list[float]) -> list[float]:
    """Por cada flanco del detector, cuánto después (+) o antes (−) llega que el flanco RMS más cercano."""
    salida = []
    for t in detector:
        cerca = [t - r for r in rms if abs(t - r) <= MAX_DESFASE_S]
        if cerca:
            salida.append(round(min(cerca, key=abs), 3))
    return salida


def decisiones_rms(muestras: np.ndarray, bloque_ms: int, umbral: float) -> list[bool]:
    tam = int(bloque_ms / 1000 * V.SAMPLE_RATE)
    return [bool(np.sqrt(np.mean(muestras[i:i + tam] ** 2)) >= umbral) for i in range(0, len(muestras), tam)]


def palabras(texto: str) -> int:
    return len(_PALABRA.findall(texto))


def resumen_prueba(registro: dict[str, Any], eventos: list, rms: list[bool], bloque_s: float) -> dict[str, Any]:
    finales = [e for e in eventos if e.tipo == "final" and any(c.isalnum() for c in e.texto)]
    parciales = [e for e in eventos if e.tipo == "parcial"]
    sube_d, baja_d = flancos(registro["decisiones"], bloque_s)
    sube_r, baja_r = flancos(rms, bloque_s)
    segs = registro["segmentos"]
    return {
        "segmentos_abiertos": len(segs),
        "segmentos_transcriptos": sum(s["transcripto"] for s in segs),
        "segmentos_con_texto": len(finales),
        "cierres": {m: sum(s["motivo"] == m for s in segs) for m in ("silencio", "tope", "fin_del_audio")},
        "llamadas_asr": len(registro["asr"]),
        "llamadas_asr_borrador": len(registro["asr"]) - sum(s["transcripto"] for s in segs),
        "asr_s": round(sum(a["ms"] for a in registro["asr"]) / 1000.0, 3),
        "audio_al_asr_s": round(sum(a["audio_s"] for a in registro["asr"]), 2),
        "palabras_finales": sum(palabras(e.texto) for e in finales),
        "palabras_borradores": sum(palabras(e.texto) for e in parciales),
        "finales": [{"inicio_s": e.inicio_audio_s, "fin_s": e.fin_audio_s, "texto": e.texto} for e in finales],
        "segmentos": segs,
        "voz_pct": round(100.0 * sum(registro["decisiones"]) / max(1, len(registro["decisiones"])), 1),
        "desfase_inicio_s": desfases(sube_d, sube_r),
        "desfase_fin_s": desfases(baja_d, baja_r),
        "decision_ms": registro["decision_ms"],
    }


# --- Inicios de palabra (sobre la corrida de medir_voz_real.py) ---------------------------------------------


def _misma_raiz(a: str, b: str) -> bool:
    """«hace» y «hacer», «transferi» y «transferir», «abri» y «abre»: el voseo que el modelo pasa a infinitivo no es un corte."""
    n = min(len(a), len(b), 4)
    return n >= 2 and a[:n] == b[:n] if min(len(a), len(b)) >= 3 else a == b


def primera_palabra_perdida(referencia: str, hipotesis: str, anterior: str = "") -> bool:
    """True si la primera palabra de la referencia no aparece (ni con la misma raíz) al principio de la transcripción.

    También se busca en la última palabra de la frase anterior (`anterior`): el reparto por frases de
    `medir_voz_real.py` deja ahí una primera palabra que no coincide exacta («Compartí» → «Compartir»).
    """
    ref = [_clave(p) for p in referencia.split() if _clave(p)]
    hip = [_clave(p) for p in hipotesis.split() if _clave(p)]
    previa = [_clave(p) for p in anterior.split() if _clave(p)][-1:]
    return bool(ref) and not any(_misma_raiz(ref[0], h) for h in previa + hip[:2])


def inicios_desde_corrida(corrida: Path, variantes: list[str]) -> dict[str, Any]:
    por_variante: dict[str, dict[str, Any]] = {}
    anterior: dict[tuple[str, str], str] = {}
    for linea in (corrida / "frases.jsonl").read_text(encoding="utf-8").splitlines():
        f = json.loads(linea)
        if f["variante"] not in variantes:
            continue
        v = por_variante.setdefault(f["variante"], {"frases": 0, "perdidas": [], "pantalla": []})
        v["frases"] += 1
        previa = anterior.get((f["variante"], f["prueba"]), "") if f["n"] > 1 else ""
        anterior[(f["variante"], f["prueba"])] = f["hipotesis"]
        if primera_palabra_perdida(f["referencia"], f["hipotesis"], previa):
            v["perdidas"].append({"prueba": f["prueba"], "toma": f["toma"], "n": f["n"],
                                  "referencia": f["referencia"], "hipotesis": f["hipotesis"]})
        if "pantalla" in f["referencia"].lower():
            v["pantalla"].append({"prueba": f["prueba"], "toma": f["toma"], "hipotesis": f["hipotesis"],
                                  "correcta": f["correcta"]})
    return por_variante


def retranscribir_pantalla(motor, muestras: np.ndarray, finales: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """El segmento que tiene «pantalla», otra vez, con más audio previo. Usa el reconocedor sin el corte."""
    salida = []
    for f in finales:
        if "pantalla" not in f["texto"].lower():
            continue
        for extra in (0.0, *PREVIO_EXTRA_S):
            desde = max(0, int((f["inicio_s"] - extra) * V.SAMPLE_RATE))
            hasta = int(f["fin_s"] * V.SAMPLE_RATE)
            salida.append({"inicio_s": round(desde / V.SAMPLE_RATE, 3), "previo_extra_s": extra,
                           "texto": type(motor)._transcribir(motor, muestras[desde:hasta]).strip()})
    return salida


# --- Simulación del corte sin ASR (umbral de Silero) --------------------------------------------------------


class _SinASR(MotorPorFrases):
    """El corte de MotorPorFrases sin reconocedor: solo interesa cómo se cierran los segmentos."""

    def _transcribir(self, audio):
        return "x"

    def inicializar(self):
        pass

    def metadatos(self):
        return {}


def simular_cortes(grabaciones: list[tuple[str, str, int, str]], umbrales: list[float], cortes: list[float],
                   bloque_ms: int) -> list[dict[str, Any]]:
    """Segmentos y cierres por tope con cada umbral de Silero y cada corte, más el RMS 0,008 como referencia."""
    detectores = [("rms", UMBRAL_FIN_DE_VOZ)] + [("silero", u) for u in umbrales]
    filas = []
    audios = [(id_, V.leer_canal(wav, col)) for id_, wav, col, _ in grabaciones]
    for vad, umbral in detectores:
        for corte in cortes:
            motor = _SinASR(sample_rate=V.SAMPLE_RATE)
            motor.corte_silencio_s = corte
            motor.umbral_rms_silencio = umbral if vad == "rms" else UMBRAL_FIN_DE_VOZ
            if vad == "silero":
                motor.detector_voz = DetectorSilero(V.MODELO_SILERO, umbral)
            fila = {"vad": vad, "umbral": umbral, "corte": corte, "segmentos": 0, "tope": 0, "silencio": 0, "voz_pct": 0.0}
            voz = bloques = 0
            for _, muestras in audios:
                registro, _ = correr(motor, muestras, bloque_ms)
                fila["segmentos"] += len(registro["segmentos"])
                fila["tope"] += sum(s["motivo"] == "tope" for s in registro["segmentos"])
                fila["silencio"] += sum(s["motivo"] == "silencio" for s in registro["segmentos"])
                voz, bloques = voz + sum(registro["decisiones"]), bloques + len(registro["decisiones"])
            fila["voz_pct"] = round(100.0 * voz / max(1, bloques), 1)
            filas.append(fila)
    return filas


# --- Salida -------------------------------------------------------------------------------------------------


def estadistica(valores: list[float]) -> dict[str, Any]:
    if not valores:
        return {"n": 0}
    return {"n": len(valores), "mediana": round(float(np.median(valores)), 3),
            "p10": round(float(np.percentile(valores, 10)), 3), "p90": round(float(np.percentile(valores, 90)), 3)}


def escribir_resumen(ruta: Path, datos: dict[str, Any]) -> None:
    vs = datos["variantes"]
    nombres = list(vs)
    etiqueta = {i: p["etiqueta"] for v in vs.values() for i, p in v["pruebas"].items()}
    plan = "../../PLAN-VOZ-REAL.md"
    l = ["# Silero contra RMS: lo que el WER no muestra", "",
         f"> Una voz (Luciano), micrófono de la Mac, demora y costo medidos offline en la M1 (2 hilos para el ASR, 1 para Silero). "
         f"No cierra D09. Plan: [PLAN-VOZ-REAL.md §12]({plan}). Issue #94.", ""]
    if datos["corrida"]:
        l += [f"WER, CER y etiquetas de las mismas variantes: [{Path(datos['corrida']).name}](../{Path(datos['corrida']).name}/resumen.md).", ""]

    l += ["## 1. Grabaciones sin texto (todo lo que sale es inventado)", "",
          "| Grabación | Variante | Voz según el detector | Segmentos abiertos | Al ASR | Llamadas al ASR | Audio al ASR (s) | Finales con texto | Palabras inventadas (finales / borradores) | Lo que salió |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for id_ in SIN_TEXTO:
        for n in nombres:
            p = vs[n]["pruebas"].get(id_)
            if p:
                textos = " · ".join(f"«{f['texto']}»" for f in p["finales"]) or "—"
                l.append(f"| {etiqueta[id_]} | `{n}` | {p['voz_pct']} % | {p['segmentos_abiertos']} | {p['segmentos_transcriptos']} | "
                         f"{p['llamadas_asr']} | {p['audio_al_asr_s']} | {p['segmentos_con_texto']} | "
                         f"{p['palabras_finales']} / {p['palabras_borradores']} | {textos} |")

    l += ["", "## 2. G08, serie de fondo mientras habla: ¿se sigue cerrando por el tope?", "",
          "| Variante | Voz según el detector | Segmentos | Cierres por silencio / tope / fin | Duración de los segmentos (s) |", "|---|---|---|---|---|"]
    for n in nombres:
        p = vs[n]["pruebas"].get(datos["g08"])
        if p:
            c = p["cierres"]
            durs = ", ".join(f"{s['fin_s'] - s['inicio_s']:.1f}" for s in p["segmentos"])
            l.append(f"| `{n}` | {p['voz_pct']} % | {p['segmentos_abiertos']} | {c['silencio']} / {c['tope']} / {c['fin_del_audio']} | {durs} |")

    l += ["", "## 3. Todas las grabaciones con texto (20)", "",
          "| Variante | Segmentos abiertos | Descartados sin ASR (< 0,3 s de voz) | Cierres por tope | Llamadas al ASR (borradores + finales) | Audio al ASR (s) | Tiempo de ASR (s) |",
          "|---|---|---|---|---|---|---|"]
    for n in nombres:
        a = vs[n]["agregado_con_texto"]
        l.append(f"| `{n}` | {a['segmentos_abiertos']} | {a['segmentos_abiertos'] - a['segmentos_transcriptos']} | {a['tope']} | "
                 f"{a['llamadas_asr']} | {a['audio_al_asr_s']:.0f} | {a['asr_s']:.1f} |")

    l += ["", "## 4. Demora del detector contra el RMS 0,008 y costo por bloque", "",
          "Desfase = flanco del detector − flanco RMS más cercano (± 0,6 s), en las 20 grabaciones con texto; "
          "positivo es que el detector llega después. El costo es solo la decisión voz/silencio de cada bloque de 40 ms, sin el ASR.", "",
          "| Variante | Desfase al empezar la voz: mediana (p10–p90) s | Desfase al terminar: mediana (p10–p90) s | Decisión por bloque: mediana / p95 / máx. (ms) | % de los 40 ms (mediana) |",
          "|---|---|---|---|---|"]
    for n in nombres:
        d = vs[n]["demora_detector"]
        ini, fin, c = d["inicio"], d["fin"], d["costo_ms"]
        rango = lambda e: f"{e['mediana']:+.2f} ({e['p10']:+.2f} a {e['p90']:+.2f}), n={e['n']}" if e["n"] else "—"
        l.append(f"| `{n}` | {rango(ini)} | {rango(fin)} | {c['mediana']:.3f} / {c['p95']:.3f} / {c['max']:.2f} | {100 * c['mediana'] / 40:.2f} % |")

    if datos["inicios"]:
        l += ["", "## 5. Inicios de palabra", "",
              "Frases (de las 100 con texto) cuya primera palabra no aparece entre las dos primeras de la transcripción, "
              "según el reparto por frases de `medir_voz_real.py`. Incluye errores del modelo, no solo cortes.", "",
              "| Variante | Frases con la primera palabra perdida | «Compartí pantalla» (toma: lo que salió) |", "|---|---|---|"]
        for n in nombres:
            v = datos["inicios"].get(n)
            if v:
                pant = " · ".join(f"t{p['toma']}: «{p['hipotesis']}»" for p in v["pantalla"])
                l.append(f"| `{n}` | {len(v['perdidas'])}/{v['frases']} | {pant} |")
        if datos["pantalla"]:
            l += ["", "El segmento de «pantalla» transcripto otra vez con más audio previo (mismo reconocedor, sin el corte):", "",
                  "| Variante | Grabación | Audio previo extra (s) | Lo que salió |", "|---|---|---|---|"]
            for n, por_id in datos["pantalla"].items():
                for id_, filas in por_id.items():
                    for f in filas:
                        l.append(f"| `{n}` | {etiqueta[id_]} | {f['previo_extra_s']} | «{f['texto']}» |")
        l += ["", "Primeras palabras perdidas, por variante:", ""]
        for n in nombres:
            v = datos["inicios"].get(n)
            if v and v["perdidas"]:
                l.append(f"- `{n}`: " + "; ".join(f"t{p['toma']} «{p['referencia'].split()[0]}» → «{' '.join(p['hipotesis'].split()[:3])}…»"
                                                    for p in v["perdidas"]))

    if datos.get("simulacion"):
        l += ["", "## 6. Simulación del corte sin ASR: ¿es el umbral de Silero?", "",
              "Solo el corte de `MotorPorFrases` (sin Parakeet) sobre las 20 grabaciones con texto, que tienen 100 frases. "
              "Con Silero, ya en voz sigue en voz mientras la probabilidad no baje de umbral − 0,15. No mide WER ni etiquetas.", "",
              "| Detector | Umbral | Corte (s) | Voz según el detector | Segmentos | Cierres por silencio | Cierres por tope |", "|---|---|---|---|---|---|---|"]
        for f in datos["simulacion"]:
            l.append(f"| {f['vad']} | {f['umbral']} | {f['corte']} | {f['voz_pct']} % | {f['segmentos']} | {f['silencio']} | {f['tope']} |")
    l += ["", "## 7. Reproducir", "", "```bash", datos["comando"], *(datos.get("comandos_extra") or []), "```", "",
          f"Código: `{datos['codigo']['hash']}` ({datos['codigo']['rama']}, {'con cambios sin commit' if datos['codigo']['dirty'] else 'limpio'}). "
          "Detalle por segmento en `extras.json`."]
    ruta.write_text("\n".join(l) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pruebas", type=Path, default=None, help="carpeta con las pruebas del panel (defecto: experiments/voip/llamadas)")
    ap.add_argument("--csv", default=str(MV.CSV_POR_DEFECTO))
    ap.add_argument("--variantes", default=",".join(VARIANTES_POR_DEFECTO))
    ap.add_argument("--corrida", type=Path, default=None, help="carpeta de medir_voz_real.py con las mismas variantes")
    ap.add_argument("--bloque-ms", type=int, default=V.BLOQUE_MS_POR_DEFECTO)
    ap.add_argument("--hilos", type=int, default=V.HILOS_POR_DEFECTO)
    ap.add_argument("--salida", type=Path, default=None)
    ap.add_argument("--simular-umbrales", default=None,
                    help="umbrales de Silero (p. ej. 0.5,0.7,0.85) para simular solo el corte, sin ASR, y agregarlo a extras.json")
    ap.add_argument("--simular-cortes", default="0.3,0.5,0.8")
    ap.add_argument("--rehacer-resumen", action="store_true",
                    help="no corre Parakeet: lee extras.json de --salida, recalcula los inicios con --corrida y reescribe resumen.md")
    args = ap.parse_args(argv)
    comando = "python experiments/asr-local/comparar_vad.py " + shlex.join(sys.argv[1:] if argv is None else argv)
    carpeta = args.pruebas or MV.carpeta_de_pruebas_por_defecto()
    destino = args.salida or (DIR_ASR / "corridas" / f"{datetime.now():%Y-%m-%d}_voz-real_vad-extras")
    if args.rehacer_resumen:
        rehacer(destino, args, carpeta, comando)
        return
    configs = dict(V.VARIANTES_PARAKEET)
    nombres = [n.strip() for n in args.variantes.split(",") if n.strip()]
    pruebas, omitidas = MV.cargar_pruebas(MV.leer_csv(args.csv), carpeta, cargar_guion(MV.GUION_POR_DEFECTO))
    if omitidas:
        print(f"Omitidas: {omitidas}", file=sys.stderr)
    grabaciones = [(p["id"], p["wav"], p["columna"], f"{p['nota'] or p['id']} (toma {p['toma']})") for p in pruebas]
    for id_, nota in SIN_TEXTO.items():
        manifiesto = json.loads((carpeta / id_ / "manifiesto.json").read_text(encoding="utf-8"))
        grabaciones.append((id_, str(carpeta / id_ / "estereo.wav"), MV.elegir_canal(manifiesto)[1], nota))
    g08 = next(p["id"] for p in pruebas if p["condicion"] == "ruido-tv")
    con_texto = {p["id"] for p in pruebas}
    bloque_s = args.bloque_ms / 1000.0

    salida: dict[str, Any] = {}
    pantalla: dict[str, dict[str, Any]] = {}
    for n in nombres:
        print(f"{n} ...", flush=True)
        motor = V.crear_motor({"motor": "parakeet", "config": configs[n].como_dict(), "hilos": args.hilos})
        motor.inicializar()
        por_id = {}
        for id_, wav, columna, nota in grabaciones:
            muestras = V.leer_canal(wav, columna)
            registro, eventos = correr(motor, muestras, args.bloque_ms)
            r = resumen_prueba(registro, eventos, decisiones_rms(muestras, args.bloque_ms, UMBRAL_FIN_DE_VOZ), bloque_s)
            r["etiqueta"] = nota
            if any("pantalla" in f["texto"].lower() for f in r["finales"]):
                pantalla.setdefault(n, {})[id_] = retranscribir_pantalla(motor, muestras, r["finales"])
            por_id[id_] = r
        costo = [ms for i, r in por_id.items() if i in con_texto for ms in r["decision_ms"]]
        ct = [r for i, r in por_id.items() if i in con_texto]
        salida[n] = {
            "config": configs[n].como_dict(), "metadatos_motor": motor.metadatos(),
            "agregado_con_texto": {
                "segmentos_abiertos": sum(r["segmentos_abiertos"] for r in ct),
                "segmentos_transcriptos": sum(r["segmentos_transcriptos"] for r in ct),
                "tope": sum(r["cierres"]["tope"] for r in ct),
                "llamadas_asr": sum(r["llamadas_asr"] for r in ct),
                "audio_al_asr_s": round(sum(r["audio_al_asr_s"] for r in ct), 2),
                "asr_s": round(sum(r["asr_s"] for r in ct), 3)},
            "demora_detector": {
                "inicio": estadistica([d for r in ct for d in r["desfase_inicio_s"]]),
                "fin": estadistica([d for r in ct for d in r["desfase_fin_s"]]),
                "costo_ms": {"mediana": float(np.median(costo)), "p95": float(np.percentile(costo, 95)), "max": float(max(costo)),
                             "bloques": len(costo)}},
            "pruebas": {i: {k: v for k, v in r.items() if k != "decision_ms"} for i, r in por_id.items()},
        }

    inicios = inicios_desde_corrida(args.corrida, nombres) if args.corrida else {}
    destino.mkdir(parents=True, exist_ok=True)
    from asr_local import obtener_info_hardware, obtener_versiones_paquetes

    datos = {"fecha": datetime.now().isoformat(timespec="seconds"),
             "comando": comando,
             "codigo": MV.info_git(), "versiones": obtener_versiones_paquetes(), "hardware": obtener_info_hardware(),
             "carpeta_pruebas": str(carpeta), "bloque_ms": args.bloque_ms, "hilos": args.hilos,
             "umbral_fin_de_voz": UMBRAL_FIN_DE_VOZ, "corrida": str(args.corrida) if args.corrida else None,
             "g08": g08, "sin_texto": SIN_TEXTO, "variantes": salida, "inicios": inicios, "pantalla": pantalla}
    (destino / "extras.json").write_text(json.dumps(datos, indent=1, ensure_ascii=False), encoding="utf-8")
    escribir_resumen(destino / "resumen.md", datos)
    print(f"Listo: {destino}/resumen.md")


def rehacer(destino: Path, args: argparse.Namespace, carpeta: Path, comando: str) -> None:
    """Sobre una salida ya hecha: inicios recalculados y, si se pide, la simulación del umbral. Parakeet no corre."""
    datos = json.loads((destino / "extras.json").read_text(encoding="utf-8"))
    if args.corrida:
        datos["inicios"] = inicios_desde_corrida(args.corrida, list(datos["variantes"]))
        datos["corrida"] = str(args.corrida)
    if args.simular_umbrales:
        pruebas, _ = MV.cargar_pruebas(MV.leer_csv(args.csv), carpeta, cargar_guion(MV.GUION_POR_DEFECTO))
        grabaciones = [(p["id"], p["wav"], p["columna"], "") for p in pruebas]
        datos["simulacion"] = simular_cortes(grabaciones, [float(u) for u in args.simular_umbrales.split(",")],
                                             [float(c) for c in args.simular_cortes.split(",")], datos["bloque_ms"])
    datos["comandos_extra"] = [c for c in datos.get("comandos_extra", []) if c != comando] + [comando]
    datos["codigo_resumen"] = MV.info_git()
    (destino / "extras.json").write_text(json.dumps(datos, indent=1, ensure_ascii=False), encoding="utf-8")
    escribir_resumen(destino / "resumen.md", datos)
    print(f"Listo: {destino}/resumen.md")


if __name__ == "__main__":
    main()
