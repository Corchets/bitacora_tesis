"""Diagnóstico del NLI: ¿el modelo está roto en esta instalación o es así para este uso?

Imprime versiones, etiquetas, tokens y las tres probabilidades para pares de control
(el ejemplo de la ficha del modelo y frases cortas en castellano) con el tokenizador rápido
y con el lento. Si los controles salen bien, el problema es el uso (ventanas de diálogo y
descripciones largas), no la instalación.

    python analisis/2026-10-30-reranker-zero-shot/diagnostico_nli.py
    python analisis/2026-10-30-reranker-zero-shot/diagnostico_nli.py --formato

`--formato` compara hipótesis cortas y largas, con y sin «A:», sobre frases INVENTADAS:
los casos de humo están relacionados con comparacion_20 y no se usan para ajustar.
"""

from __future__ import annotations

import sys

import torch
import transformers
from transformers import AutoModelForSequenceClassification, AutoTokenizer

MODELO = next((a for a in sys.argv[1:] if not a.startswith("--")), None) or "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"

PARES = [
    # (premisa, hipótesis, qué se espera)
    ("Angela Merkel ist eine Politikerin in Deutschland und Vorsitzende der CDU",
     "Emmanuel Macron is the President of France", "neutral o contradicción (ficha del modelo)"),
    ("Decime el código que te llegó por SMS.", "Alguien pide un código.", "entailment"),
    ("Hoy llueve mucho en Tucumán.", "Alguien pide un código.", "neutral"),
    ("No hace falta que me digas ningún código.", "Alguien pide un código.", "contradicción"),
    ("A: Te llamo de soporte por la activación de tu cuenta de WhatsApp.",
     "Una de las personas le pide a la otra que le diga un código que le llegó por mensaje.", "neutral"),
    ("A: Decime el código de activación que recibiste por SMS.",
     "Una de las personas le pide a la otra que le diga un código que le llegó por mensaje.", "entailment"),
]


def probar(rapido: bool) -> None:
    tok = AutoTokenizer.from_pretrained(MODELO, use_fast=rapido)
    red = AutoModelForSequenceClassification.from_pretrained(MODELO).eval()
    print(f"\n== tokenizador {'rápido' if rapido else 'lento'}: {type(tok).__name__}")
    print("id2label:", red.config.id2label)
    print("tokens de control:", tok.tokenize("Decime el código que te llegó por SMS."))
    with torch.inference_mode():
        for premisa, hipotesis, esperado in PARES:
            enc = tok(premisa, hipotesis, return_tensors="pt", truncation=True)
            p = torch.softmax(red(**enc).logits[0].float(), dim=-1).tolist()
            dist = ", ".join(f"{red.config.id2label[i]}={x:.2f}" for i, x in enumerate(p))
            print(f"- {premisa[:45]!r} / {hipotesis[:40]!r}\n    {dist}   (se espera {esperado})")


# Frases inventadas (no salen de ningún caso): (texto, ¿hay pedido?)
FRASES = [
    ("Leeme el código de seis dígitos que te llegó.", True),
    ("Pasame ya el número que te mandaron por mensaje de texto.", True),
    ("Me mandaron un código por mensaje pero no se lo voy a dar a nadie.", False),
    ("Nunca le des a nadie el código que te llega por mensaje.", False),
    ("Hola, le hablo del área de seguridad de su banco.", False),
    ("¿Ya cenaste? Mañana paso a buscarte temprano.", False),
]
HIPOTESIS = {
    "corta": "Alguien pide un código.",
    "media": "Se le pide a la otra persona que diga un código que recibió.",
    "larga (v1)": "Una de las personas le pide a la otra que le diga, le lea o le reenvíe un código que le llegó por mensaje, por WhatsApp o en un token.",
}


def formato() -> None:
    tok = AutoTokenizer.from_pretrained(MODELO)
    red = AutoModelForSequenceClassification.from_pretrained(MODELO).eval()
    entail = next(i for i, n in red.config.id2label.items() if str(n).lower().startswith("entail"))
    print("\nP(entailment) · columnas: hipótesis × con/sin «A:» · ✔ = acierta con umbral 0,5")
    cols = [(h, pref) for h in HIPOTESIS for pref in ("A: ", "")]
    print("frase".ljust(52) + " | ".join(f"{h[:6]}{'+A' if pref else '  '}" for h, pref in cols))
    aciertos = {c: 0 for c in cols}
    with torch.inference_mode():
        for texto, pide in FRASES:
            celdas = []
            for h, pref in cols:
                enc = tok(pref + texto, HIPOTESIS[h], return_tensors="pt", truncation=True)
                p = torch.softmax(red(**enc).logits[0].float(), dim=-1)[entail].item()
                ok = (p > 0.5) == pide
                aciertos[(h, pref)] += ok
                celdas.append(f"{p:.2f}{'✔' if ok else '✘'}  ")
            print(f"{('[pide] ' if pide else '[no]   ') + texto[:44]:52}" + " | ".join(celdas))
    print("aciertos".ljust(52) + " | ".join(f"{aciertos[c]}/{len(FRASES)}    " for c in cols))


if __name__ == "__main__":
    if "--formato" in sys.argv:
        print(f"torch {torch.__version__} · transformers {transformers.__version__} · modelo {MODELO}")
        formato()
        raise SystemExit(0)
    print(f"torch {torch.__version__} · transformers {transformers.__version__} · modelo {MODELO}")
    for rapido in (True, False):
        try:
            probar(rapido)
        except Exception as e:  # el lento puede no estar disponible
            print(f"\n== tokenizador {'rápido' if rapido else 'lento'}: no se pudo cargar ({type(e).__name__}: {e})")
