"""Diagnóstico del NLI: ¿el modelo está roto en esta instalación o es así para este uso?

Imprime versiones, etiquetas, tokens y las tres probabilidades para pares de control
(el ejemplo de la ficha del modelo y frases cortas en castellano) con el tokenizador rápido
y con el lento. Si los controles salen bien, el problema es el uso (ventanas de diálogo y
descripciones largas), no la instalación.

    python analisis/2026-10-30-reranker-zero-shot/diagnostico_nli.py
"""

from __future__ import annotations

import sys

import torch
import transformers
from transformers import AutoModelForSequenceClassification, AutoTokenizer

MODELO = sys.argv[1] if len(sys.argv) > 1 else "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"

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


if __name__ == "__main__":
    print(f"torch {torch.__version__} · transformers {transformers.__version__} · modelo {MODELO}")
    for rapido in (True, False):
        try:
            probar(rapido)
        except Exception as e:  # el lento puede no estar disponible
            print(f"\n== tokenizador {'rápido' if rapido else 'lento'}: no se pudo cargar ({type(e).__name__}: {e})")
