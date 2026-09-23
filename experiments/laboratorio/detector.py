"""Quien lee: TF-IDF stub sobre semillas inventadas.

No es corpus, no es piloto, no cierra D09. Solo da un numerito por turno
para que el camino goteo se pueda anotar en #29.

Sin opinion (propuesta 2026-09-23): palabras vacias no cuentan. Si quedan
menos de MIN_PALABRAS_CONOCIDAS en el vocabulario de las semillas, el turno
no tiene puntaje. El umbral 0.5 y este piso son parametros de spike.
"""

import json
import unicodedata
from pathlib import Path

SEED = 42
MIN_PALABRAS_CONOCIDAS = 2
# Lista de spike, no una lista cerrada de la tesis.
PALABRAS_VACIAS = (
    "que", "el", "la", "los", "las", "de", "del", "en", "un", "una", "y", "a",
    "por", "para", "con", "su", "tu", "te", "me", "se", "no", "si", "ya", "lo",
    "al", "es", "son", "le", "les", "esto", "esta", "hay", "como", "más", "mas",
    "muy", "banco", "tenes", "aplicacion", "tiene",
)
def _plegar(texto: str) -> str:
    """Saca tildes (P18). El vectorizador ya minúsculas; esto iguala a rules."""
    return "".join(
        c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn"
    )


DESCRIPCION_STUB = (
    "tfidf-stub-semillas: TF-IDF + regresion logistica sobre semillas.json inventadas; "
    f"sin opinion si quedan <{MIN_PALABRAS_CONOCIDAS} palabras conocidas "
    "(palabras vacias fuera; pliega tildes)"
)


class DetectorTfidf:
    def __init__(self, semillas_path: str | Path):
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.linear_model import LogisticRegression
        except ImportError as e:
            raise RuntimeError("Falta scikit-learn. Corre con Docker.") from e
        semillas = json.loads(Path(semillas_path).read_text(encoding="utf-8"))
        textos = [_plegar(t) for t in semillas["estafa"]] + [
            _plegar(t) for t in semillas["legitima"]
        ]
        clases = [1] * len(semillas["estafa"]) + [0] * len(semillas["legitima"])
        vacias = list(dict.fromkeys(_plegar(w) for w in PALABRAS_VACIAS))
        self._vec = TfidfVectorizer(stop_words=vacias)
        x = self._vec.fit_transform(textos)
        self._clf = LogisticRegression(random_state=SEED)
        self._clf.fit(x, clases)

    def puntaje(self, texto: str) -> float | None:
        """Probabilidad de estafa, o None si el turno es sin opinion."""
        if not texto.strip():
            return None
        x = self._vec.transform([_plegar(texto)])
        if x.nnz < MIN_PALABRAS_CONOCIDAS:
            return None
        return float(self._clf.predict_proba(x)[0][1])
