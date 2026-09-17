"""Quien lee: TF-IDF stub sobre semillas inventadas.

No es corpus, no es piloto, no cierra D09. Solo da un numerito por turno
para que el camino goteo se pueda anotar en #29.
"""

import json
from pathlib import Path

SEED = 42
DESCRIPCION_STUB = "tfidf-stub-semillas: TF-IDF + regresion logistica sobre semillas.json inventadas"


class DetectorTfidf:
    def __init__(self, semillas_path: str | Path):
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.linear_model import LogisticRegression
        except ImportError as e:
            raise RuntimeError("Falta scikit-learn. Corre con Docker.") from e
        semillas = json.loads(Path(semillas_path).read_text(encoding="utf-8"))
        textos = list(semillas["estafa"]) + list(semillas["legitima"])
        clases = [1] * len(semillas["estafa"]) + [0] * len(semillas["legitima"])
        self._vec = TfidfVectorizer()
        x = self._vec.fit_transform(textos)
        self._clf = LogisticRegression(random_state=SEED)
        self._clf.fit(x, clases)

    def puntaje(self, texto: str) -> float:
        """Probabilidad de estafa para un turno. Vacio = 0."""
        if not texto.strip():
            return 0.0
        x = self._vec.transform([texto])
        return float(self._clf.predict_proba(x)[0][1])
