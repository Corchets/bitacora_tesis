"""Puntaje de goteo con un encoder de español congelado.

No es corpus, no es piloto, no cierra D09. El encoder no clasifica vishing:
se embebe semillas.json y una regresion logistica (semilla 42) pone el
numero. Misma interfaz que DetectorTfidf.puntaje.
"""

import json
from pathlib import Path

import numpy as np

SEED = 42


class DetectorEncoder:
    def __init__(self, model_id: str, semillas_path: str | Path):
        try:
            import torch
            from sklearn.linear_model import LogisticRegression
            from transformers import AutoModel, AutoTokenizer
        except ImportError as e:
            raise RuntimeError("Faltan torch, transformers o scikit-learn.") from e

        self.model_id = model_id
        self._torch = torch
        semillas = json.loads(Path(semillas_path).read_text(encoding="utf-8"))
        textos = list(semillas["estafa"]) + list(semillas["legitima"])
        clases = [1] * len(semillas["estafa"]) + [0] * len(semillas["legitima"])
        try:
            self._tok = AutoTokenizer.from_pretrained(model_id, use_fast=True)
        except TypeError:
            # ALBETO tiny trae tokenizer.json; el tokenizador lento de transformers 5 no lo abre.
            from transformers import PreTrainedTokenizerFast

            local = Path(model_id)
            if local.is_dir():
                archivo = local / "tokenizer.json"
            else:
                from huggingface_hub import hf_hub_download

                archivo = hf_hub_download(model_id, "tokenizer.json")
            self._tok = PreTrainedTokenizerFast(tokenizer_file=str(archivo))
        self._modelo = AutoModel.from_pretrained(model_id)
        self._modelo.eval()
        x = self._embeber(textos)
        self._clf = LogisticRegression(random_state=SEED, max_iter=1000)
        self._clf.fit(x, clases)

    def _embeber(self, textos: list[str]) -> np.ndarray:
        torch = self._torch
        lotes = []
        with torch.no_grad():
            for texto in textos:
                tokens = self._tok(
                    texto,
                    return_tensors="pt",
                    truncation=True,
                    max_length=128,
                )
                salida = self._modelo(**tokens).last_hidden_state
                mascara = tokens["attention_mask"].unsqueeze(-1)
                suma = (salida * mascara).sum(dim=1)
                cuenta = mascara.sum(dim=1).clamp(min=1)
                lotes.append((suma / cuenta).squeeze(0).numpy())
        return np.vstack(lotes)

    def puntaje(self, texto: str) -> float | None:
        """Probabilidad de estafa. None solo si el turno está vacío."""
        if not texto.strip():
            return None
        x = self._embeber([texto])
        return float(self._clf.predict_proba(x)[0][1])
