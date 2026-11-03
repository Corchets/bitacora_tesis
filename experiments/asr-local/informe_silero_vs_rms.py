#!/usr/bin/env python3
"""Informe en PDF de la comparación Silero VAD contra el corte RMS en Parakeet (#94, PLAN-VOZ-REAL.md §12).

Lee las dos corridas del 2026-10-29 (`parakeet-silero-vs-rms` y `vad-extras`), el guion y `voz-real/pruebas.csv`, y
arma gráficos y tablas. Para los gráficos de G12 y G08 lee el audio guardado (fuera de Git) con `--pruebas`; si no
está, esos gráficos se omiten. El PDF no contiene audio.

No usa el entorno del laboratorio: matplotlib y reportlab van en un entorno aparte, por ejemplo

    uv run --no-project --python 3.13 --with matplotlib --with reportlab --with numpy --with soundfile \\
        --with onnxruntime python experiments/asr-local/informe_silero_vs_rms.py \\
        --pruebas ../bitacora_tesis-voip-asr/experiments/voip/llamadas
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import tempfile
from datetime import date
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402
from reportlab.lib import colors  # noqa: E402
from reportlab.lib.enums import TA_CENTER  # noqa: E402
from reportlab.lib.pagesizes import A4  # noqa: E402
from reportlab.lib.styles import ParagraphStyle  # noqa: E402
from reportlab.lib.units import cm  # noqa: E402
from reportlab.pdfbase import pdfmetrics  # noqa: E402
from reportlab.pdfbase.ttfonts import TTFont  # noqa: E402
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,  # noqa: E402
                                TableStyle)

DIR_ASR = Path(__file__).resolve().parent
RAIZ = DIR_ASR.parents[1]
CORRIDA = DIR_ASR / "corridas" / "2026-10-29_voz-real_parakeet-silero-vs-rms"
EXTRAS = DIR_ASR / "corridas" / "2026-10-29_voz-real_vad-extras"
SALIDA = EXTRAS / "INFORME-SILERO-VS-RMS.pdf"
MODELO_SILERO = DIR_ASR / "modelos" / "silero-vad" / "silero_vad.onnx"
G12, G08 = "2026-10-29_201733-924805", "2026-10-29_200832-553834"
G10, SERIE = "2026-10-29_201018-775836", "2026-10-29_193603-180243"

REF = "parakeet-0.8-rms-0.008"
ORDEN = [REF, "parakeet-0.9-rms-0.003", "parakeet-0.8-silero-0.5", "parakeet-0.5-silero-0.5", "parakeet-0.3-silero-0.5",
         "parakeet-0.5-silero-0.9", "parakeet-0.3-silero-0.9"]
NOMBRE = {REF: "RMS 0,008 · corte 0,8 s (referencia)", "parakeet-0.9-rms-0.003": "RMS 0,003 · corte 0,9 s (panel anterior)",
          "parakeet-0.8-silero-0.5": "Silero 0,5 · corte 0,8 s", "parakeet-0.5-silero-0.5": "Silero 0,5 · corte 0,5 s",
          "parakeet-0.3-silero-0.5": "Silero 0,5 · corte 0,3 s", "parakeet-0.5-silero-0.9": "Silero 0,9 · corte 0,5 s",
          "parakeet-0.3-silero-0.9": "Silero 0,9 · corte 0,3 s"}
CORTO = {REF: "RMS\n0,8 s (ref.)", "parakeet-0.9-rms-0.003": "RMS 0,003\n0,9 s (ant.)",
         "parakeet-0.8-silero-0.5": "Silero 0,5\n0,8 s", "parakeet-0.5-silero-0.5": "Silero 0,5\n0,5 s",
         "parakeet-0.3-silero-0.5": "Silero 0,5\n0,3 s", "parakeet-0.5-silero-0.9": "Silero 0,9\n0,5 s",
         "parakeet-0.3-silero-0.9": "Silero 0,9\n0,3 s"}
COLOR = {REF: "#1f4e79", "parakeet-0.9-rms-0.003": "#9aa5b1", "parakeet-0.8-silero-0.5": "#f4a259",
         "parakeet-0.5-silero-0.5": "#e07a1f", "parakeet-0.3-silero-0.5": "#b85c00", "parakeet-0.5-silero-0.9": "#5fae6e",
         "parakeet-0.3-silero-0.9": "#2e7d32"}
MOTIVO_COLOR = {"silencio": "#4c9be8", "tope": "#d64545", "fin_del_audio": "#b0b0b0"}
AZUL, GRIS_CLARO, GRIS = colors.HexColor("#1f4e79"), colors.HexColor("#eef2f7"), colors.HexColor("#5a6470")


def coma(x: float, d: int = 1) -> str:
    return f"{x:.{d}f}".replace(".", ",")


# --- Datos --------------------------------------------------------------------------------------------------


def cargar() -> dict:
    m = json.loads((CORRIDA / "manifiesto.json").read_text(encoding="utf-8"))
    e = json.loads((EXTRAS / "extras.json").read_text(encoding="utf-8"))
    frases = [json.loads(l) for l in (CORRIDA / "frases.jsonl").read_text(encoding="utf-8").splitlines()]
    filas = [l for l in (DIR_ASR / "voz-real/pruebas.csv").read_text(encoding="utf-8").splitlines()]
    csv_activas = list(csv.DictReader([l for l in filas if not l.startswith("#")]))
    guion = json.loads((DIR_ASR / "voz-real/guion.json").read_text(encoding="utf-8"))
    return {"m": m, "e": e, "frases": frases, "csv": {f["id"]: f for f in csv_activas}, "guion": guion}


def toma(d: dict, n: str, t: str) -> dict:
    return d["m"]["variantes"][n]["por_toma"][t]


def ok_por_prueba(d: dict, n: str) -> dict[str, tuple[int, int]]:
    salida: dict[str, list[int]] = {}
    for f in d["frases"]:
        if f["variante"] == n:
            c = salida.setdefault(f["prueba"], [0, 0])
            c[0] += f["correcta"]
            c[1] += 1
    return {k: (v[0], v[1]) for k, v in salida.items()}


def git_corto() -> str:
    try:
        return subprocess.check_output(["git", "-C", str(RAIZ), "rev-parse", "--short", "HEAD"], text=True).strip()
    except Exception:
        return "desconocido"


# --- Gráficos -----------------------------------------------------------------------------------------------


def preparar_matplotlib() -> None:
    for ruta in ("/System/Library/Fonts/Supplemental/Arial Unicode.ttf",):
        if Path(ruta).exists():
            font_manager.fontManager.addfont(ruta)
            plt.rcParams["font.family"] = font_manager.FontProperties(fname=ruta).get_name()
    plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False, "axes.titlesize": 10,
                         "axes.titleweight": "bold", "figure.dpi": 200, "savefig.bbox": "tight"})


def fig_wer_y_frases(d: dict, ruta: Path) -> None:
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.2, 3.4), gridspec_kw={"width_ratios": [1.35, 1]})
    x = np.arange(len(ORDEN))
    for k, (t, desp, alfa) in enumerate((("2", -0.2, 1.0), ("3", 0.2, 0.55))):
        wer = [toma(d, n, t)["wer"] * 100 for n in ORDEN]
        barras = a1.bar(x + desp, wer, 0.38, color=[COLOR[n] for n in ORDEN], alpha=alfa,
                        edgecolor="white", label=f"toma {t}")
        for b, w in zip(barras, wer):
            a1.text(b.get_x() + b.get_width() / 2, w + 0.3, coma(w), ha="center", va="bottom", fontsize=6.5)
    ref2 = toma(d, REF, "2")["wer"] * 100
    from matplotlib.lines import Line2D

    a1.axhline(ref2 + 2, color="#d64545", ls="--", lw=1)
    a1.set_ylim(0, 27)
    a1.set_xticks(x, [CORTO[n] for n in ORDEN], fontsize=7)
    a1.set_ylabel("WER (%)")
    a1.set_title("WER por variante (menos es mejor)")
    a1.legend(handles=[Patch(color="#777", alpha=1.0, label="toma 2 (decide)"), Patch(color="#777", alpha=0.55, label="toma 3 (confirma)"),
                       Line2D([], [], color="#d64545", ls="--", label="tope de la regla §2 (ref. + 2 puntos)")],
              fontsize=6.5, frameon=False, loc="upper center", ncol=3, bbox_to_anchor=(0.5, 1.0))
    for k, (t, desp, alfa) in enumerate((("2", -0.2, 1.0), ("3", 0.2, 0.55))):
        ok = [toma(d, n, t)["frases_correctas"] for n in ORDEN]
        a2.bar(x + desp, ok, 0.38, color=[COLOR[n] for n in ORDEN], alpha=alfa, edgecolor="white")
        for xi, o in zip(x + desp, ok):
            a2.text(xi, o + 0.1, str(o), ha="center", va="bottom", fontsize=6.5)
    a2.axhline(30, color="#d64545", ls="--", lw=1)
    a2.set_ylim(24, 31.6)
    a2.legend(handles=[Line2D([], [], color="#d64545", ls="--", label="lo que pedía la regla §2 (30/30)")],
              fontsize=6.5, frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.0))
    a2.set_xticks(x, [CORTO[n] for n in ORDEN], fontsize=6.5, rotation=0)
    a2.set_ylabel("frases con etiquetas correctas (de 30)")
    a2.set_title("Frases OK (más es mejor)")
    fig.tight_layout()
    fig.savefig(ruta)
    plt.close(fig)


def fig_demora_vs_wer(d: dict, ruta: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.6, 3.8))
    r = toma(d, REF, "2")
    ax.add_patch(plt.Rectangle((0, 0), r["demora_final"]["mediana_s"] + 0.3, r["wer"] * 100 + 2, color="#e3f1e5", zorder=0))
    ax.text(0.63, 10.4, "zona permitida por la regla §2 (además tenía que sumar 2 frases)", fontsize=7, color="#2e7d32")
    desplazamiento = {REF: (10, -12), "parakeet-0.9-rms-0.003": (-20, 12), "parakeet-0.8-silero-0.5": (-40, -22),
                      "parakeet-0.5-silero-0.5": (-25, 12), "parakeet-0.3-silero-0.5": (12, -14),
                      "parakeet-0.5-silero-0.9": (-10, 14), "parakeet-0.3-silero-0.9": (-20, -26)}
    for n in ORDEN:
        a = toma(d, n, "2")
        ax.scatter(a["demora_final"]["mediana_s"], a["wer"] * 100, s=30 + 10 * a["segmentos_finales"], color=COLOR[n],
                   edgecolor="black", lw=0.5, zorder=3)
        ax.annotate(f"{CORTO[n].replace(chr(10), ' ')}: {a['segmentos_finales']} segm., {a['frases_correctas']}/30",
                    (a["demora_final"]["mediana_s"], a["wer"] * 100), xytext=desplazamiento[n], textcoords="offset points",
                    fontsize=6.5, arrowprops={"arrowstyle": "-", "color": "#999", "lw": 0.5})
    ax.set_xlim(0.6, 1.95)
    ax.set_ylim(10, 23.5)
    ax.set_xlabel("demora de la frase final, mediana (s, offline en la M1)")
    ax.set_ylabel("WER toma 2 (%)")
    ax.set_title("Demora contra WER (toma 2). El tamaño del punto es la cantidad de segmentos")
    fig.tight_layout()
    fig.savefig(ruta)
    plt.close(fig)


def leer_audio(carpeta: Path, id_: str) -> np.ndarray | None:
    try:
        import soundfile as sf
    except ImportError:
        return None
    wav = carpeta / id_ / "estereo.wav"
    if not wav.is_file():
        return None
    datos, hz = sf.read(str(wav), dtype="float32", always_2d=True)
    return datos[:, 0] if hz == 16000 else None


def probabilidad_silero(x: np.ndarray) -> np.ndarray | None:
    try:
        import onnxruntime as ort
    except ImportError:
        return None
    if not MODELO_SILERO.is_file():
        return None
    ses = ort.InferenceSession(str(MODELO_SILERO))
    h = np.zeros((2, 1, 64), np.float32)
    c = np.zeros((2, 1, 64), np.float32)
    p = []
    for i in range(0, len(x) - 511, 512):
        o, h, c = ses.run(None, {"x": x[None, i:i + 512], "h": h, "c": c})
        p.append(float(o.ravel()[0]))
    return np.array(p)


def barras_de_segmentos(ax, d: dict, id_: str, variantes: list[str]) -> None:
    for k, n in enumerate(variantes):
        for s in d["e"]["variantes"][n]["pruebas"][id_]["segmentos"]:
            ax.barh(k, s["fin_s"] - s["inicio_s"], left=s["inicio_s"], height=0.6, color=MOTIVO_COLOR[s["motivo"]],
                    edgecolor="white", lw=1)
    ax.set_yticks(range(len(variantes)), [NOMBRE[n].replace(" (referencia)", " (ref.)") for n in variantes], fontsize=7)
    ax.invert_yaxis()
    ax.legend(handles=[Patch(color=MOTIVO_COLOR["silencio"], label="se cerró por silencio"),
                       Patch(color=MOTIVO_COLOR["tope"], label="se cerró por el tope de 10 s"),
                       Patch(color=MOTIVO_COLOR["fin_del_audio"], label="fin de la grabación")],
              fontsize=6.5, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.32), ncol=3)


def fig_g12(d: dict, carpeta: Path | None, ruta: Path) -> bool:
    x = leer_audio(carpeta, G12) if carpeta else None
    p = probabilidad_silero(x) if x is not None else None
    if p is None:
        return False
    fig, (a1, a2, a3) = plt.subplots(3, 1, figsize=(9.2, 5.6), sharex=True, gridspec_kw={"height_ratios": [1, 1.2, 1]})
    tam = 640
    rms = np.array([np.sqrt(np.mean(x[i:i + tam] ** 2)) for i in range(0, len(x), tam)])
    t_rms = (np.arange(len(rms)) + 1) * 0.04
    a1.semilogy(t_rms, np.maximum(rms, 1e-4), color="#1f4e79", lw=0.8)
    a1.axhline(0.008, color="#1f4e79", ls="--", lw=1)
    a1.fill_between(t_rms, 1e-4, 1, where=rms >= 0.008, color="#1f4e79", alpha=0.12, step="pre")
    a1.text(0.2, 0.0095, "umbral RMS 0,008", fontsize=7, color="#1f4e79")
    a1.set_ylim(5e-4, 0.3)
    a1.set_ylabel("RMS del bloque")
    a1.set_title("G12 (toma 2): energía del bloque y probabilidad de voz de Silero; abajo, cómo quedó cortado")
    t_p = (np.arange(len(p)) + 1) * 512 / 16000
    a2.plot(t_p, p, color="#444", lw=0.8)
    for umbral, col in ((0.5, "#e07a1f"), (0.9, "#2e7d32")):
        a2.axhline(umbral, color=col, ls="--", lw=1)
        a2.axhline(umbral - 0.15, color=col, ls=":", lw=1)
    a2.text(26.6, 0.52, "0,5 entra en voz", fontsize=6.5, color="#e07a1f", ha="right")
    a2.text(26.6, 0.37, "0,35 sale de voz", fontsize=6.5, color="#e07a1f", ha="right", va="bottom")
    a2.text(26.6, 0.92, "0,9 entra", fontsize=6.5, color="#2e7d32", ha="right")
    a2.text(26.6, 0.77, "0,75 sale", fontsize=6.5, color="#2e7d32", ha="right", va="bottom")
    a2.set_ylim(0, 1.05)
    a2.set_ylabel("prob. de voz (Silero)")
    barras_de_segmentos(a3, d, G12, [REF, "parakeet-0.8-silero-0.5", "parakeet-0.3-silero-0.9"])
    a3.set_xlabel("segundos de la grabación")
    a3.set_xlim(0, len(x) / 16000)
    fig.tight_layout()
    fig.savefig(ruta)
    plt.close(fig)
    return True


def fig_g08(d: dict, ruta: Path) -> None:
    fig, ax = plt.subplots(figsize=(9.2, 2.6))
    barras_de_segmentos(ax, d, G08, [REF, "parakeet-0.8-silero-0.5", "parakeet-0.5-silero-0.9", "parakeet-0.3-silero-0.9"])
    ax.set_xlabel("segundos de la grabación")
    ax.set_title("G08: Luciano lee el bloque 2 con una serie de fondo. Cada barra es un segmento que va al ASR")
    fig.tight_layout()
    fig.savefig(ruta)
    plt.close(fig)


VARS_EXTRAS = [REF, "parakeet-0.8-silero-0.5", "parakeet-0.5-silero-0.5", "parakeet-0.3-silero-0.5",
               "parakeet-0.5-silero-0.9", "parakeet-0.3-silero-0.9"]


def fig_sin_texto(d: dict, ruta: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.1))
    x = np.arange(len(VARS_EXTRAS))
    titulos = ((G10, f"G10: sin hablar, tele apagada ({d['duraciones'].get(G10, '44,2')} s)"),
               (SERIE, f"Serie de fondo, sin hablar ({d['duraciones'].get(SERIE, '175,3')} s)"))
    for ax, (id_, titulo) in zip(axes, titulos):
        ps = [d["e"]["variantes"][n]["pruebas"][id_] for n in VARS_EXTRAS]
        llam = [p["llamadas_asr"] for p in ps]
        pal = [p["palabras_finales"] for p in ps]
        ax.bar(x - 0.2, llam, 0.38, color=[COLOR[n] for n in VARS_EXTRAS], label="llamadas al ASR")
        ax.bar(x + 0.2, pal, 0.38, color="white", edgecolor=[COLOR[n] for n in VARS_EXTRAS], hatch="///", label="palabras inventadas (finales)")
        for xi, v in zip(x - 0.2, llam):
            ax.text(xi, v + 0.4, str(v), ha="center", fontsize=6.5)
        for xi, v in zip(x + 0.2, pal):
            ax.text(xi, v + 0.4, str(v), ha="center", fontsize=6.5)
        ax.set_xticks(x, [CORTO[n] for n in VARS_EXTRAS], fontsize=6.5)
        ax.set_title(titulo)
        ax.set_ylim(0, 45)
    axes[0].legend(fontsize=7, frameon=False)
    fig.tight_layout()
    fig.savefig(ruta)
    plt.close(fig)


def fig_computo(d: dict, ruta: Path) -> None:
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.2, 3.0))
    x = np.arange(len(VARS_EXTRAS))
    ag = [d["e"]["variantes"][n]["agregado_con_texto"] for n in VARS_EXTRAS]
    audio = [a["audio_al_asr_s"] / 60 for a in ag]
    a1.bar(x, audio, color=[COLOR[n] for n in VARS_EXTRAS])
    for xi, v in zip(x, audio):
        a1.text(xi, v + 0.8, coma(v, 0), ha="center", fontsize=7)
    a1.axhline(587.4 / 60, color="#555", ls=":", lw=1)
    a1.text(5.4, 587.4 / 60 + 1, "duración del audio (9,8 min)", fontsize=6.5, ha="right", color="#555")
    a1.set_ylabel("minutos de audio pasados al ASR")
    a1.set_title("Trabajo del ASR en las 20 grabaciones")
    a1.set_xticks(x, [CORTO[n] for n in VARS_EXTRAS], fontsize=6.5)
    sil = [a["segmentos_abiertos"] - a["tope"] for a in ag]
    top = [a["tope"] for a in ag]
    a2.bar(x, sil, color=MOTIVO_COLOR["silencio"], label="cerrados por silencio o fin")
    a2.bar(x, top, bottom=sil, color=MOTIVO_COLOR["tope"], label="cerrados por el tope de 10 s")
    for xi, s, t in zip(x, sil, top):
        a2.text(xi, s + t + 1.5, f"{t} tope{'s' if t != 1 else ''}", ha="center", fontsize=6.5)
    a2.axhline(100, color="#555", ls=":", lw=1)
    a2.text(5.4, 101, "100 frases leídas", fontsize=6.5, ha="right", color="#555")
    a2.set_ylabel("segmentos")
    a2.set_title("Segmentos abiertos y cómo se cerraron")
    a2.set_xticks(x, [CORTO[n] for n in VARS_EXTRAS], fontsize=6.5)
    a2.legend(fontsize=6.5, frameon=False, loc="upper left")
    a2.set_ylim(0, 150)
    fig.tight_layout()
    fig.savefig(ruta)
    plt.close(fig)


def fig_simulacion(d: dict, ruta: Path) -> None:
    sim = d["e"].get("simulacion") or []
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.2, 2.9))
    for corte, estilo in ((0.3, "-o"), (0.5, "-s"), (0.8, "-^")):
        fs = sorted([f for f in sim if f["vad"] == "silero" and f["corte"] == corte], key=lambda f: f["umbral"])
        rms = next(f for f in sim if f["vad"] == "rms" and f["corte"] == corte)
        lin, = a1.plot([f["umbral"] for f in fs], [f["tope"] for f in fs], estilo, ms=4, label=f"corte {coma(corte)} s")
        a1.axhline(rms["tope"], color=lin.get_color(), ls=":", lw=1)
        a2.plot([f["umbral"] for f in fs], [f["segmentos"] for f in fs], estilo, ms=4, color=lin.get_color())
        a2.axhline(rms["segmentos"], color=lin.get_color(), ls=":", lw=1)
    a1.set_xlabel("umbral de Silero")
    a1.set_ylabel("cierres por el tope de 10 s")
    a1.set_title("Frases juntadas hasta el tope")
    a1.legend(fontsize=7, frameon=False)
    a2.set_xlabel("umbral de Silero")
    a2.set_ylabel("segmentos (100 frases leídas)")
    a2.set_title("Cantidad de segmentos")
    a2.axhline(100, color="#999", lw=0.8)
    for ax in (a1, a2):
        ax.text(0.99, 0.02, "punteado: RMS 0,008 con el mismo corte", transform=ax.transAxes, fontsize=6.5, ha="right", color="#555")
    fig.tight_layout()
    fig.savefig(ruta)
    plt.close(fig)


# --- PDF ----------------------------------------------------------------------------------------------------


def estilos() -> dict[str, ParagraphStyle]:
    base = "/System/Library/Fonts/Supplemental/"
    pdfmetrics.registerFont(TTFont("Texto", base + "Arial Unicode.ttf"))
    pdfmetrics.registerFont(TTFont("Negrita", base + "Arial Bold.ttf"))
    pdfmetrics.registerFont(TTFont("Cursiva", base + "Arial Italic.ttf"))
    pdfmetrics.registerFontFamily("Texto", normal="Texto", bold="Negrita", italic="Cursiva", boldItalic="Negrita")
    s = {
        "titulo": ParagraphStyle("titulo", fontName="Negrita", fontSize=21, leading=26, textColor=AZUL, spaceAfter=6),
        "subtitulo": ParagraphStyle("subtitulo", fontName="Texto", fontSize=11.5, leading=15, textColor=GRIS, spaceAfter=14),
        "h1": ParagraphStyle("h1", fontName="Negrita", fontSize=14, leading=18, textColor=AZUL, spaceBefore=12, spaceAfter=6),
        "h2": ParagraphStyle("h2", fontName="Negrita", fontSize=11, leading=14, textColor=AZUL, spaceBefore=8, spaceAfter=4),
        "p": ParagraphStyle("p", fontName="Texto", fontSize=9.6, leading=13.4, spaceAfter=5),
        "vi": ParagraphStyle("vi", fontName="Texto", fontSize=9.6, leading=13.4, leftIndent=12, bulletIndent=2, spaceAfter=3),
        "pie": ParagraphStyle("pie", fontName="Cursiva", fontSize=8, leading=10.5, textColor=GRIS, alignment=TA_CENTER, spaceAfter=10),
        "celda": ParagraphStyle("celda", fontName="Texto", fontSize=8, leading=10),
        "celda_n": ParagraphStyle("celda_n", fontName="Negrita", fontSize=8, leading=10, textColor=colors.white),
        "caja": ParagraphStyle("caja", fontName="Texto", fontSize=9.6, leading=13.6, spaceAfter=4),
        "nota": ParagraphStyle("nota", fontName="Texto", fontSize=8.4, leading=11, textColor=GRIS),
    }
    return s


def tabla(datos: list[list], s: dict, anchos: list[float], resaltar: list[int] | None = None) -> Table:
    filas = [[Paragraph(str(c), s["celda_n"]) for c in datos[0]]] + [
        [c if not isinstance(c, str) else Paragraph(c, s["celda"]) for c in fila] for fila in datos[1:]]
    t = Table(filas, colWidths=[a * cm for a in anchos], repeatRows=1)
    estilo = [("BACKGROUND", (0, 0), (-1, 0), AZUL), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
              ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, GRIS_CLARO]),
              ("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.HexColor("#c9d2dc")),
              ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
    for r in resaltar or []:
        estilo.append(("BACKGROUND", (0, r), (-1, r), colors.HexColor("#dbe8f5")))
    t.setStyle(TableStyle(estilo))
    return t


def caja(contenido: list, s: dict, fondo: str = "#eef4fb", borde: str = "#1f4e79") -> Table:
    t = Table([[contenido]], colWidths=[17 * cm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(fondo)),
                           ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor(borde)),
                           ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                           ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    return t


def figura(ruta: Path, ancho_cm: float, pie: str, s: dict) -> KeepTogether:
    from reportlab.lib.utils import ImageReader

    w, h = ImageReader(str(ruta)).getSize()
    return KeepTogether([Image(str(ruta), width=ancho_cm * cm, height=ancho_cm * cm * h / w), Paragraph(pie, s["pie"])])


def vi(texto: str, s: dict) -> Paragraph:
    return Paragraph(texto, s["vi"], bulletText="•")


def armar(d: dict, figs: dict[str, Path | None], salida: Path) -> None:
    s = estilos()
    m, e = d["m"], d["e"]
    r2, r3 = toma(d, REF, "2"), toma(d, REF, "3")
    b2 = toma(d, "parakeet-0.3-silero-0.9", "2")
    b3 = toma(d, "parakeet-0.3-silero-0.9", "3")
    f2 = toma(d, "parakeet-0.8-silero-0.5", "2")
    ag = {n: e["variantes"][n]["agregado_con_texto"] for n in VARS_EXTRAS}
    sx = lambda n, i: e["variantes"][n]["pruebas"][i]
    st = []

    # Portada y resumen
    st += [Spacer(1, 1.2 * cm), Paragraph("Silero VAD contra el corte por energía (RMS) en Parakeet", s["titulo"]),
           Paragraph("Medición con voz real para la detección incremental de vishing · issue #94 (sub-issue de #87) · "
                     "PLAN-VOZ-REAL.md §12 · 2026-10-29", s["subtitulo"]),
           Paragraph("<b>Autor:</b> Luciano Grosso. Medición, gráficos y redacción asistidos por Claude Opus 5.5. "
                     f"Código en la rama <font name='Courier'>LucianoGrosso13/silero-vs-rms-94</font> (<font name='Courier'>{git_corto()}</font>). "
                     "Material de desarrollo: <b>no cierra D09</b> ni elige un ASR.", s["nota"]), Spacer(1, 0.4 * cm)]
    st.append(caja([
        Paragraph("<b>En una página</b>", s["h2"]),
        Paragraph(f"<b>Pregunta.</b> ¿Mejora el texto que le llega al detector si un VAD de voz (Silero) decide qué es voz en lugar de "
                  f"la energía del bloque (RMS)? Todo lo demás quedó igual: el mismo audio, el mismo Parakeet, el mismo preaudio y el mismo corte.", s["caja"]),
        Paragraph(f"<b>Respuesta corta: no le gana al RMS en texto, pero sí ahorra trabajo en el silencio con ruidos.</b>", s["caja"]),
        vi(f"Referencia (RMS 0,008, corte 0,8 s, lo de «Probar el ASR»): <b>{r2['frases_correctas']}/30</b> frases con etiquetas correctas y "
           f"<b>WER {coma(r2['wer'] * 100)} %</b> en la toma 2; {r3['frases_correctas']}/30 y {coma(r3['wer'] * 100)} % en la toma 3.", s),
        vi(f"Silero con su umbral de fábrica (0,5) <b>junta frases</b>: {ag['parakeet-0.8-silero-0.5']['tope']} cierres por el tope de 10 s "
           f"contra {ag[REF]['tope']} del RMS, WER {coma(f2['wer'] * 100)} % y casi el doble de audio al ASR.", s),
        vi(f"Silero con umbral 0,9 y corte 0,3 s <b>queda cerca pero no gana</b>: {b2['frases_correctas']}/30 y WER {coma(b2['wer'] * 100)} % "
           f"(toma 2), {b3['frases_correctas']}/30 y {coma(b3['wer'] * 100)} % (toma 3), 0,36 s menos de demora, pero parte más "
           f"({b2['segmentos_finales']} segmentos para 30 frases).", s),
        vi(f"<b>Donde Silero sí sirve:</b> {d['duraciones'].get(G10, '44,2')} s de silencio con ruidos (G10) pasan de {sx(REF, G10)['llamadas_asr']} llamadas al ASR a "
           f"{sx('parakeet-0.3-silero-0.9', G10)['llamadas_asr']}; con la tele de fondo (G08) deja de cortar cada 10 s. "
           "No frena la voz de una serie sin nadie hablando.", s),
        vi("Ninguna variante pasa la regla del plan (§2) y ninguna frase negativa disparó etiquetas. «Compartí pantalla» no lo pierde el corte: "
           "Parakeet escribe «Compartir la pantalla» y las reglas no reconocen esa forma.", s),
        vi("<b>Decisión:</b> ninguna todavía. El panel y la llamada siguen como estaban. Lo que sugiere esta medición está marcado como "
           "<i>propuesta sin discutir</i> (sección 9) y lo decide Luciano en D09.", s),
    ], s))
    st.append(PageBreak())

    # 1. Por qué
    st += [Paragraph("1. Por qué probamos esto", s["h1"]),
           Paragraph("El sistema escucha la llamada, la pasa a texto con un ASR local y un detector busca pedidos de estafa en ese texto. "
                     "Parakeet, el ASR que se está probando, no es streaming: hay que cortarle el audio en frases. Quién decide dónde empieza y "
                     "termina cada frase es justamente lo que se compara acá.", s["p"]),
           vi("<b>Lo que había (auditoría del 2026-10-29, §10).</b> <font name='Courier'>MotorPorFrases</font> decide voz o silencio por "
              "bloque de 40 ms comparando la energía (RMS) con un umbral. Es un detector de energía: no distingue la voz de un golpe, una "
              "respiración o una tele. Una recomendación recibida proponía Silero VAD como imprescindible; la auditoría dejó la comparación "
              "como pendiente, sin adoptarlo.", s),
           vi("<b>Lo que mostró la primera medición con voz real (§11).</b> Con el RMS: 30 s de silencio con ruidos (G10) mandaron 8 ruidos al "
              "ASR, que inventó «Shh. Uh-uh.»; con una serie de fondo (G08) el ruido nunca baja del umbral y las frases se cierran cada 10 s "
              "justos, cortando palabras; «Compartí pantalla» parecía perder la primera palabra en todas las tomas.", s),
           vi("<b>La hipótesis.</b> Un VAD entrenado para reconocer voz humana debería dejar de mandar ruidos al ASR y no comerse los "
              "inicios de palabra. Era el paso 1 del plan (§11.6) antes de tocar la llamada en vivo.", s),
           Paragraph("2. Contra qué lo comparamos", s["h1"]),
           Paragraph("Se cambió <b>una sola cosa</b>: quién decide si cada bloque de 40 ms es voz. Todo lo demás es idéntico en todas las variantes.", s["p"])]
    st.append(tabla([["Queda igual en todas", "Valor"],
                     ["Audio", "las 20 grabaciones con texto de <font name='Courier'>pruebas.csv</font> más G10 y la serie sin hablar"],
                     ["Modelo de ASR", "Parakeet TDT 0.6B v3 int8 (sherpa-onnx 1.13.8), 2 hilos, greedy"],
                     ["Bloques", "40 ms (640 muestras a 16 kHz), como los manda el panel"],
                     ["Preaudio", "0,3 s de audio anterior al inicio detectado"],
                     ["Voz mínima", "0,3 s para transcribir una frase; 1 s para el primer borrador"],
                     ["Borradores", "cada 0,5 s, con el filtro de idioma"],
                     ["Tope de frase", "10 s"]], s, [4, 13]))
    st += [Spacer(1, 6), Paragraph("Las variantes medidas:", s["p"])]
    st.append(tabla([["Variante", "Quién decide la voz", "Por qué está"],
                     [NOMBRE[REF], "RMS ≥ 0,008", "<b>Referencia</b>: el valor inicial de «Probar el ASR» elegido por Luciano el 2026-10-29"],
                     [NOMBRE["parakeet-0.9-rms-0.003"], "RMS ≥ 0,003", "Contexto: lo que tenía el panel antes (y la llamada en vivo hoy)"],
                     ["Silero 0,5 · corte 0,8 / 0,5 / 0,3 s", "Silero, umbral de fábrica", "Mismo corte que la referencia y dos más cortos, porque Silero tarda en soltar la voz"],
                     ["Silero 0,9 · corte 0,5 / 0,3 s", "Silero, umbral alto", "Agregadas después de ver que con 0,5 las frases se juntaban (sección 6)"]],
                    s, [5.2, 3.6, 8.2], resaltar=[1]))
    st += [Spacer(1, 4), Paragraph("<b>Cómo usa Silero el motor.</b> <font name='Courier'>VadModel.is_speech()</font> de sherpa-onnx con el "
                                   "<font name='Courier'>silero_vad.onnx</font> oficial del release (644 KB). Silero mira ventanas de 32 ms; un bloque de 40 ms es "
                                   "voz si alguna ventana que terminó en él es voz. Una vez en voz, sigue en voz mientras la probabilidad no baje de "
                                   "<i>umbral − 0,15</i> (histéresis de sherpa). El RMS 0,008 se sigue calculando solo para marcar el fin de la voz y medir la "
                                   "demora igual que en la referencia.", s["p"])]
    st.append(PageBreak())

    # 3. Datos
    tipos: dict[str, int] = {}
    for b in d["guion"]["bloques"]:
        for f in b["frases"]:
            tipos[f["tipo"]] = tipos.get(f["tipo"], 0) + 1
    st += [Paragraph("3. Con qué datos: tu voz y el guion", s["h1"]),
           Paragraph("Todo el audio lo grabó Luciano el 2026-10-29 entre las 19:36 y las 20:52, con «Probar el ASR» del panel, el micrófono de la "
                     "Mac, en su pieza, leyendo los bloques del guion desde el celular. El panel guardó el audio entero a 16 kHz; las variantes se "
                     "rehicieron offline sobre ese mismo audio, así que todas escuchan exactamente lo mismo. <b>El audio no está en Git</b> (copia "
                     "<font name='Courier'>bitacora_tesis-voip-asr/experiments/voip/llamadas/</font>) y tampoco en este informe.", s["p"]),
           Paragraph(f"<b>El guion.</b> 30 frases en 6 bloques de 5: {tipos.get('critica', 0)} con términos críticos (código, clave, CVV, token…), "
                     f"{tipos.get('numeros', 0)} con números y montos, {tipos.get('bancos', 0)} con bancos y apps, {tipos.get('jerga', 0)} espontáneas con "
                     f"jerga tucumana y {tipos.get('negativa', 0)} negativas parecidas a una estafa pero inocentes («estoy cómodo», «me duele el codo»). "
                     "La referencia de cada grabación es el texto del bloque leído; Luciano no informó desvíos.", s["p"]),
           Paragraph("<b>Cómo se mide.</b> La medida principal es la que importa para la tesis: se corren las reglas del detector "
                     "(<font name='Courier'>reglas.py</font>) sobre el texto real y sobre la transcripción, frase por frase, y una frase está OK si dan "
                     "las mismas etiquetas (<font name='Courier'>REQUEST_AUTH_CODE</font>, <font name='Courier'>REQUEST_TRANSFER</font>…). Además WER y "
                     "CER, demora de la frase final y, para lo que el WER no ve, segmentos, llamadas al ASR y palabras inventadas.", s["p"])]
    info = {p["id"]: p for p in m["datos"]["pruebas"]}
    ok_ref, ok_b = ok_por_prueba(d, REF), ok_por_prueba(d, "parakeet-0.3-silero-0.9")
    filas = [["Grab.", "T.", "Condición", "Bl.", "Dur. (s)", "Segmentos RMS / S0,5 / S0,9", "Frases OK RMS · S0,9"]]
    def g(i):
        return d["csv"][i]["nota"].split()[0] if i in d["csv"] else "—"
    for i in sorted(info, key=lambda i: (info[i]["toma"], g(i))):
        p = info[i]
        segs = " / ".join(str(len(sx(n, i)["segmentos"])) for n in (REF, "parakeet-0.8-silero-0.5", "parakeet-0.3-silero-0.9"))
        filas.append([g(i), str(p["toma"]), p["condicion"].replace("microfono", "micrófono"), str(p["bloque"]["bloque"]),
                      coma(p["duracion_s"]), segs, f"{ok_ref[i][0]}/{ok_ref[i][1]} · {ok_b[i][0]}/{ok_b[i][1]}"])
    for i, nombre in ((G10, "G10"), (SERIE, "Serie")):
        segs = " / ".join(str(len(sx(n, i)["segmentos"])) for n in (REF, "parakeet-0.8-silero-0.5", "parakeet-0.3-silero-0.9"))
        filas.append([nombre, "—", "sin hablar" + (" (tele apagada)" if i == G10 else " (serie de fondo)"), "—",
                      d["duraciones"].get(i, "—"), segs, "sin texto"])
    st.append(tabla(filas, s, [1.4, 0.8, 3.9, 0.9, 1.5, 4.6, 3.9]))
    st += [Spacer(1, 4), Paragraph(
        "Toma 1: para ajustar (G06, bloque 6, se borró del Historial antes de medir). Toma 2: para decidir. Toma 3: grabada en vivo con 0,8 s / 0,008 "
        "para confirmar con audio nuevo. G07: voz baja (salió casi al volumen normal). G08: con una serie de fondo. G09: con una pausa de ~1 s dentro "
        "de cada frase. G10 y la serie: sin nadie hablando, para ver qué se inventa. T. = toma; Bl. = bloque del guion. «S0,5» = Silero 0,5 con corte 0,8 s; «S0,9» = Silero 0,9 con corte 0,3 s.",
        s["nota"])]
    st.append(PageBreak())

    # 4. Qué esperábamos
    lim_dem = r2["demora_final"]["mediana_s"] + 0.3
    st += [Paragraph("4. Qué valores esperábamos", s["h1"]),
           Paragraph("<b>La regla para quedarse con un cambio</b> (PLAN-VOZ-REAL.md §2, fijada antes de medir) se aplica en la toma 2 contra la "
                     "referencia. Hay que cumplir las cuatro:", s["p"])]
    st.append(tabla([["Condición", "Qué pide", "Con esta referencia significa"],
                     ["Más frases OK", "al menos 2 frases más con etiquetas correctas", f"30/30 (la referencia tiene {r2['frases_correctas']}/30)"],
                     ["Negativas", "ninguna etiqueta nueva en las frases negativas", "0 etiquetas nuevas"],
                     ["Demora", "la frase final no tarda más de +0,3 s", f"mediana ≤ {coma(lim_dem, 2)} s"],
                     ["WER", "no empeora más de 2 puntos", f"WER ≤ {coma(r2['wer'] * 100 + 2)} %"]], s, [3, 7, 7]))
    st += [Spacer(1, 6), Paragraph("<b>Lo que esperábamos de cada caso</b> (escrito en §10 y §11 antes de esta medición) y lo que pasó:", s["p"])]
    st.append(tabla([["Caso", "Esperábamos", "Pasó"],
                     ["G10, silencio con ruidos", "Silero ahorra el ASR sobre ruidos", "<b>Sí.</b> De 28 llamadas al ASR a 0–1; de 4 palabras inventadas a 0–2"],
                     ["Serie sin hablar", "No lo resuelve: la tele también es voz", "<b>Confirmado.</b> Menos llamadas (40 → 17), mismas palabras inventadas (17 → 16–19)"],
                     ["G08, serie mientras habla", "No lo resuelve: haría falta otro umbral", "<b>Mejor de lo esperado.</b> Corta en las pausas de Luciano: 0 topes con 0,9 / 0,3"],
                     ["«Compartí» al inicio", "Un VAD no se comería inicios", "<b>No era el corte.</b> Parakeet escribe «Compartir la pantalla» (sección 7)"],
                     ["Calidad del texto", "Igual o mejor que el RMS", "<b>No.</b> Peor con 0,5; cerca pero sin ganar con 0,9"],
                     ["Costo del VAD", "Bajo", "<b>Sí.</b> 0,11 ms por bloque de 40 ms (0,3 %)"]], s, [3.8, 5.2, 8]))
    st += [Spacer(1, 8), Paragraph("Glosario rápido", s["h2"])]
    st.append(tabla([["Término", "Qué quiere decir acá"],
                     ["ASR", "Reconocimiento automático del habla: pasa la voz a texto. Acá, Parakeet corriendo en la Mac, sin internet."],
                     ["VAD", "Detector de actividad de voz: decide si un pedazo de audio tiene voz. Silero es un VAD hecho con una red neuronal."],
                     ["RMS", "Energía promedio de un bloque de audio. «Voz» si supera el umbral (0,008). No distingue voz de ruido."],
                     ["Corte", "Cuánto silencio seguido hace falta para dar la frase por terminada y mandarla al ASR."],
                     ["Segmento", "Pedazo de audio que el motor manda al ASR como una frase. Lo ideal: un segmento por frase leída."],
                     ["Tope", "Si una frase llega a 10 s sin pausa, se corta igual. Suele cortar en medio de una palabra."],
                     ["Preaudio", "Los 0,3 s anteriores al inicio detectado que se agregan a la frase para no perder la primera sílaba."],
                     ["WER / CER", "Porcentaje de palabras / letras mal transcriptas contra el texto real. Menos es mejor."],
                     ["Frases OK", "Frases donde las reglas del detector dan las mismas etiquetas en la transcripción que en el texto real."],
                     ["Demora", "Tiempo entre que termina la voz y que la frase final está lista (offline, en la M1)."]], s, [2.8, 14.2]))
    st.append(PageBreak())

    # 5. Resultados
    st += [Paragraph("5. Resultados con referencia escrita", s["h1"])]
    filas = [["Variante", "T2 OK", "T2 WER", "T2 CER", "T2 segm.", "T2 demora", "T3 OK", "T3 WER", "§2"]]
    regla = {c["nombre"]: c["regla"]["pasa"] for c in m["decision"]["parakeet"]}
    for n in ORDEN:
        a2, a3 = toma(d, n, "2"), toma(d, n, "3")
        filas.append([NOMBRE[n], f"{a2['frases_correctas']}/30", f"{coma(a2['wer'] * 100)} %", f"{coma(a2['cer'] * 100)} %",
                      str(a2["segmentos_finales"]), f"{coma(a2['demora_final']['mediana_s'], 2)} s", f"{a3['frases_correctas']}/30",
                      f"{coma(a3['wer'] * 100)} %", "ref." if n == REF else ("sí" if regla.get(n) else "no")])
    st.append(tabla(filas, s, [5.4, 1.3, 1.5, 1.5, 1.4, 1.6, 1.3, 1.5, 1.3], resaltar=[1]))
    st.append(Paragraph("T2 / T3 = toma 2 / toma 3. OK = frases con las mismas etiquetas que el texto real (de 30). §2 = ¿pasa la regla del plan?", s["nota"]))
    st += [Spacer(1, 8), figura(figs["wer"], 17, "Figura 1. WER y frases con etiquetas correctas. La línea roja es lo que pedía la regla para "
                                                 "quedarse con el cambio. Toma 2 decide; toma 3 (más clara) confirma.", s),
           figura(figs["demora"], 13, "Figura 2. Cada variante en demora y WER. Ninguna cae en la zona verde con 2 frases más.", s)]
    st += [vi("<b>Ninguna variante pasa la regla.</b> Ninguna suma frases (+0 o −1) y todas suben el WER más de 2 puntos en la toma 2 "
              "(de +2,8 a +7,0). Ninguna negativa dispara etiquetas.", s),
           vi("<b>La toma 3 no cambia la lectura.</b> Silero acierta «Dame el OTP» y, con 0,9, pierde «token» (sale «toque»): son cambios del "
              "texto de Parakeet cuando recibe otro recorte de audio, no un efecto del detector.", s),
           vi("<b>Con Silero 0,9 / 0,3 en la toma 1 con micrófono</b> salen 20/25 frases, contra 23/25 del RMS.", s)]
    st.append(PageBreak())

    # 6. Por qué Silero 0,5 junta frases
    st += [Paragraph("6. Por qué Silero con su umbral de fábrica junta frases", s["h1"]),
           Paragraph("Después de hablar, la probabilidad de voz de Silero no cae de golpe: baja de a poco durante 0,3 a 1 s. Con la histéresis de "
                     "sherpa, una vez en voz sigue en voz hasta que baja de 0,35. Las pausas reales de Luciano entre frases son de 0,5 a 1,4 s "
                     "(§11.2): muchas no llegan a verse como silencio, la frase sigue abierta y termina cerrada por el tope de 10 s, en medio de "
                     "una palabra. Con umbral 0,9 hay que bajar de 0,75 para salir, y las pausas sí se ven.", s["p"])]
    if figs.get("g12"):
        st.append(figura(figs["g12"], 17, "Figura 3. G12 (toma 2, bloque 2). Arriba: energía de cada bloque y el umbral RMS. Medio: probabilidad de "
                                          "Silero con sus umbrales de entrada (rayas) y de salida (puntos). Abajo: los segmentos que quedan con cada "
                                          "variante. Con Silero 0,5 las cinco frases quedan en dos tramos de 10 s cerrados por el tope.", s))
    st += [Paragraph("Para elegir el 0,9 se simuló solo el corte, sin ASR, sobre las 20 grabaciones con texto (100 frases):", s["p"]),
           figura(figs["sim"], 17, "Figura 4. Simulación del corte sin ASR. Con 0,9 y corte 0,3 s queda 1 tope en 125 segmentos, casi como el RMS. "
                                   "El 0,9 se eligió mirando estas mismas grabaciones: falta confirmarlo con una toma nueva.", s)]
    st.append(PageBreak())

    # 7. Lo que el WER no muestra
    st += [Paragraph("7. Lo que el WER no muestra", s["h1"]),
           Paragraph("<b>Grabaciones sin nadie hablando.</b> Todo lo que sale ahí es inventado y cada llamada al ASR es trabajo de más.", s["p"]),
           figura(figs["sin_texto"], 17, "Figura 5. Llamadas al ASR y palabras inventadas en las frases finales. En G10 Silero no manda nada "
                                         "al ASR; con la serie llama menos pero inventa lo mismo, porque la tele es voz humana.", s)]
    filas = [["Grab.", "Variante", "Segm.", "Llam. ASR", "Audio ASR", "Lo que salió"]]
    for i, nom in ((G10, "G10"), (SERIE, "Serie")):
        for n in (REF, "parakeet-0.8-silero-0.5", "parakeet-0.3-silero-0.9"):
            p = sx(n, i)
            filas.append([nom, NOMBRE[n].replace(" (referencia)", " (ref.)"), str(p["segmentos_abiertos"]), str(p["llamadas_asr"]),
                          f"{coma(p['audio_al_asr_s'], 0)} s", " · ".join(f"«{f['texto']}»" for f in p["finales"][:4]) or "nada"])
    st.append(tabla(filas, s, [1.3, 4.3, 1.3, 1.6, 1.7, 6.8]))
    st += [Spacer(1, 8), Paragraph("<b>G08: hablar con la tele prendida.</b>", s["p"]),
           figura(figs["g08"], 17, "Figura 6. Con el RMS el ruido de la tele nunca baja del umbral y las frases se cortan cada 10 s. Silero "
                                   "reconoce las pausas de Luciano aunque la tele siga: con 0,9 / 0,3 ningún segmento llega al tope. "
                                   "Las etiquetas de G08 salieron 5/5 con todas las variantes.", s),
           figura(figs["computo"], 17, "Figura 7. En las 20 grabaciones con texto (9,8 min). Cada borrador vuelve a transcribir la frase "
                                       "entera: con frases de 10 s, Silero 0,5 casi duplica el audio que procesa el ASR. Silero 0,9 / 0,3 queda "
                                       "un 12 % por debajo del RMS.", s)]
    det = {n: e["variantes"][n]["demora_detector"] for n in VARS_EXTRAS}
    filas = [["Variante", "Llega al empezar la voz", "Llega al terminar la voz", "Costo por bloque (mediana / p95)"]]
    for n in (REF, "parakeet-0.8-silero-0.5", "parakeet-0.3-silero-0.9"):
        x = det[n]
        fmt = lambda q: "igual (es la referencia)" if n == REF else f"{coma(q['mediana'], 2)} s después (p90 {coma(q['p90'], 2)} s)"
        filas.append([NOMBRE[n], fmt(x["inicio"]), fmt(x["fin"]), f"{coma(x['costo_ms']['mediana'], 3)} / {coma(x['costo_ms']['p95'], 3)} ms"])
    st += [Paragraph("<b>Demora y costo del detector</b>, contra el RMS, en las 20 grabaciones:", s["p"]),
           tabla(filas, s, [5, 4, 4, 4]),
           Paragraph("Al empezar, Silero llega una ventana (40 ms) después del RMS: el preaudio de 0,3 s lo cubre. El costo es de CPU en la M1, "
                     "no de batería: 0,11 ms por cada bloque de 40 ms, un 0,3 % del tiempo real.", s["nota"]),
           Spacer(1, 8), Paragraph("<b>Inicios de palabra y «Compartí pantalla».</b>", s["p"]),
           vi("Ningún detector se come inicios de forma sistemática: sin contar el voseo que el modelo pasa a infinitivo («Hacé» → «Hacer»), "
              "falta la primera palabra en 10 de 100 frases con el RMS y en 9 a 15 con Silero, casi siempre por errores del modelo "
              "(«Ñaño, al ñudo» → «Al pedo»).", s),
           vi("<b>«Compartí» no se pierde.</b> Parakeet escribe «Compartir la pantalla…» al principio de su propio segmento, con los dos "
              "detectores, y volver a transcribir ese segmento con 0,3 o 0,6 s más de audio previo da lo mismo.", s),
           vi("La etiqueta <font name='Courier'>REQUEST_REMOTE_ACCESS</font> se pierde por otras dos cosas: el reparto por frases de la medición "
              "deja «Compartir» en la frase anterior, y las reglas buscan «comparti pantalla», que no coincide con «compartir la pantalla». "
              "Es un riesgo de las reglas (D07, abierta), no del VAD. Corrige lo que decía el §11.5.", s)]
    st.append(PageBreak())

    # 8 y 9. Decisiones
    st += [Paragraph("8. Qué está decidido y qué no", s["h1"])]
    st.append(tabla([["Tema", "Estado"],
                     ["Valor inicial de «Probar el ASR»", "<b>Decidido por Luciano</b> (2026-10-29, §11): 0,8 s / 0,008 con RMS. Esta medición no lo cambia."],
                     ["Llamada en vivo", "Sigue en 0,9 s / 0,003 con RMS. No se tocó."],
                     ["Silero en el motor", "Implementado como opción (<font name='Courier'>detector_voz</font>). <b>Por defecto sigue el RMS.</b>"],
                     ["Reemplazar el RMS por Silero", "<b>No decidido.</b> Propuesta sin discutir (sección 9)."],
                     ["Elegir ASR y detector (D09)", "<b>Abierta.</b> Esto es material de desarrollo con una sola voz."],
                     ["Reglas y «compartir la pantalla» (D07)", "<b>Abierta.</b> Las reglas no se tocaron."]], s, [5, 12]))
    st += [Spacer(1, 10), Paragraph("9. Qué sugiere la medición", s["h1"])]
    st.append(caja([
        Paragraph("<b>Estado: propuesta sin discutir.</b> Decide Luciano en D09.", s["caja"]),
        vi("<b>Con esta voz no hay motivo para cambiar el RMS por Silero.</b> Con el umbral de fábrica empeora el texto y duplica el trabajo "
           "del ASR; con 0,9 / 0,3 queda cerca pero no suma frases, sube el WER y parte más (cada segmento extra es una evaluación más del detector).", s),
        vi("<b>Silero sí sirve para no transcribir el silencio con ruidos y para cortar con una tele de fondo.</b> No sirve para frenar la "
           "voz ajena de una serie.", s),
        vi("<b>Ideas para el próximo paso, sin probar:</b> usar Silero 0,9 solo para <i>abrir</i> la frase y dejar que el RMS la cierre; o un "
           "umbral RMS que siga el ruido de fondo (§11.6, paso 2). Cualquiera se confirma con una toma nueva y otra voz antes de tocar la llamada.", s),
    ], s, fondo="#fff7e8", borde="#e0a030"))
    st += [Paragraph("10. Límites", s["h1"]),
           vi("<b>Una sola voz y un solo lugar:</b> Luciano, micrófono de la Mac, su pieza y una serie de fondo. 30 frases por toma: una frase "
              "equivale a 3,3 puntos. Faltan la condición Meet y otra voz del equipo.", s),
           vi("<b>El umbral 0,9 se eligió mirando este mismo audio</b> (simulación de la sección 6). No hay una toma nueva que lo confirme.", s),
           vi("<b>Demora y costo son offline en la Mac M1</b> (reloj simulado, ASR con 2 hilos y Silero con 1). No hay mediciones en el "
              "teléfono, de batería ni de temperatura. La memoria pico varió entre 870 y 1140 MB sin relación con el detector (Silero pesa 0,6 MB).", s),
           vi("<b>Una versión de Silero y una forma de usarlo:</b> el <font name='Courier'>silero_vad.onnx</font> del release de sherpa con su "
              "histéresis. No se probaron otros modelos, otra histéresis ni combinar los dos detectores.", s),
           vi("La toma 1 de G06 (bloque 6) se borró antes de medir, así que «Compartí pantalla» se midió en dos tomas.", s),
           Paragraph("11. Cómo reproducirlo", s["h1"]),
           Paragraph("Desde la raíz del repositorio, con el entorno que tiene sherpa-onnx. Las corridas quedan en "
                     "<font name='Courier'>experiments/asr-local/corridas/</font> y el detalle está en PLAN-VOZ-REAL.md §12:", s["p"]),
           Paragraph("<font name='Courier' size='6.8'>python experiments/asr-local/medir_voz_real.py --solo-parakeet --contra-parakeet "
                     "parakeet-0.8-rms-0.008 --variantes parakeet-0.9-rms-0.003,parakeet-0.8-silero-0.5,parakeet-0.5-silero-0.5,"
                     "parakeet-0.3-silero-0.5,parakeet-0.5-silero-0.9,parakeet-0.3-silero-0.9 --pruebas …/llamadas --etiqueta parakeet-silero-vs-rms<br/>"
                     "python experiments/asr-local/comparar_vad.py --pruebas …/llamadas --corrida "
                     "experiments/asr-local/corridas/2026-10-29_voz-real_parakeet-silero-vs-rms<br/>"
                     "python experiments/asr-local/comparar_vad.py --rehacer-resumen --salida experiments/asr-local/corridas/2026-10-29_voz-real_vad-extras "
                     "--pruebas …/llamadas --corrida … --simular-umbrales 0.5,0.7,0.85,0.9</font>", s["p"]),
           Paragraph(f"Informe generado con <font name='Courier'>informe_silero_vs_rms.py</font> el {date.today().isoformat()}.", s["nota"])]

    def pie(canvas, doc):
        canvas.saveState()
        canvas.setFont("Texto", 7.5)
        canvas.setFillColor(GRIS)
        canvas.drawString(2 * cm, 1.2 * cm, "Silero VAD contra RMS en Parakeet · #94 · una voz, sin piloto: no cierra D09")
        canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"página {doc.page}")
        canvas.restoreState()

    doc = SimpleDocTemplate(str(salida), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm, bottomMargin=1.8 * cm,
                            title="Silero VAD contra el corte RMS en Parakeet", author="Luciano Grosso", subject="Issue #94, PLAN-VOZ-REAL.md §12")
    doc.build(st, onFirstPage=pie, onLaterPages=pie)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pruebas", type=Path, default=None, help="carpeta con el audio de las pruebas (para los gráficos de G12)")
    ap.add_argument("--salida", type=Path, default=SALIDA)
    args = ap.parse_args()
    preparar_matplotlib()
    d = cargar()
    d["duraciones"] = {}
    for i in (G10, SERIE):
        x = leer_audio(args.pruebas, i) if args.pruebas else None
        if x is not None:
            d["duraciones"][i] = coma(len(x) / 16000)
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        figs: dict[str, Path | None] = {k: t / f"{k}.png" for k in ("wer", "demora", "g12", "sim", "sin_texto", "g08", "computo")}
        fig_wer_y_frases(d, figs["wer"])
        fig_demora_vs_wer(d, figs["demora"])
        if not fig_g12(d, args.pruebas, figs["g12"]):
            figs["g12"] = None
        fig_simulacion(d, figs["sim"])
        fig_sin_texto(d, figs["sin_texto"])
        fig_g08(d, figs["g08"])
        fig_computo(d, figs["computo"])
        armar(d, figs, args.salida)
    print(f"Listo: {args.salida}")


if __name__ == "__main__":
    main()
