"""Entrena Tito una sola vez (#70, parte de #68).

Ajusta UNA regresión logística con seed 42 sobre los 5.520 textos aceptados del
banco histórico (`nacho1706/feature-training-data`, commit `bb542e1...`), usando
RoBERTuito congelado con promedio enmascarado y límite de 128 tokens. No hay
fine-tuning del encoder, ni búsqueda de configuraciones, ni calibración sobre
las ocho conversaciones: el umbral 0,5 vive en el flujo (`filtro_tito.py`), no acá.

Entradas: se leen directo de los objetos Git del commit fijado (no se duplica el
banco ni se mezclan otras historias) y se verifican contra los hashes de
`manifest.json` / `tokens.json` de ese commit. No toca el test reservado.

Uso:
    source .venv/bin/activate   # desde la raíz del repositorio
    python experiments/slm-directo/entrenar_tito.py
    python experiments/slm-directo/entrenar_tito.py --salida experiments/slm-directo/tito_logreg.json

El artefacto resultante lo carga `tito_real.py` sin reentrenar, una vez por
proceso, para todas las conversaciones y SLM.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]

# Procedencia fijada por #68/#70: no cambiar sin reabrir el issue.
BANCO_COMMIT = "bb542e130e7a67a82e376a75a0438a15de32f4a6"
BANCO_BASE = "experiments/laboratorio/entrenamiento_tito"
ENCODER_ID = "pysentimiento/robertuito-base-uncased"
ENCODER_REVISION = "20cb399e4b93f270c0cd6b6f533bcb0ada3cb658"
TOKENIZER_SHA_DECLARADO = "9465c3d57686e6b117d7c8f0e65b2b7d3a6bfb1d3c5154b52b175b3e37f2047c"
EJEMPLOS_SHA_DECLARADO = "fc1fe13cfba121c356775434bd6139c6005df847ab9e5848ffe4e6e4c82c44b1"
EXCLUSIONES_SHA_DECLARADA = "2b7f88b39f10153762a192b6d50d62026655ba288253f27317fc967656a99b24"
ESPERADO_ACEPTADAS = 5520
ESPERADO_APARTADAS = 480
ESPERADO_FAMILIAS = 276

# Único ajuste permitido: una regresión logística, seed 42, sin búsqueda.
SEMILLA = 42
LR_CONFIG = {"C": 1.0, "solver": "lbfgs", "max_iter": 1000}
LIMITE_TOKENS = 128
LOTE_EMBEDDINGS = 32
CLASES = ("estafa", "legitima")  # estafa -> 1, legitima -> 0


def _git_show(commit: str, ruta: str) -> bytes:
    r = subprocess.run(["git", "show", f"{commit}:{ruta}"],
                       cwd=RAIZ, capture_output=True, check=True, timeout=120)
    return r.stdout


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _info_codigo() -> dict:
    def git(*args: str) -> str:
        try:
            r = subprocess.run(["git", *args], cwd=RAIZ,
                               capture_output=True, text=True, timeout=10, check=True)
            return r.stdout.strip()
        except (OSError, subprocess.SubprocessError):
            return "desconocido"
    return {
        "commit": git("rev-parse", "HEAD"),
        "diff_sin_commit": git("status", "--porcelain", "--", ".", ":(exclude)corridas"),
        "script_sha256": sha(Path(__file__).read_bytes()),
    }


def _info_maquina() -> dict:
    try:
        from torch import cuda
        gpu = cuda.get_device_name(0) if cuda.is_available() else None
    except Exception:
        gpu = None
    mem_gb = None
    try:
        if sys.platform.startswith("linux"):
            for renglon in Path("/proc/meminfo").read_text().splitlines():
                if renglon.startswith("MemTotal:"):
                    mem_gb = round(int(renglon.split()[1]) / 1024**2, 1)
    except OSError:
        pass
    return {
        "sistema": platform.platform(),
        "procesador": platform.processor() or "no informado",
        "nucleos_logicos": os.cpu_count(),
        "ram_total_gb": mem_gb,
        "gpu": gpu,
        "python": platform.python_version(),
    }


def cargar_banco() -> tuple[list[dict], dict, dict]:
    """Lee ejemplos y exclusiones del commit fijado y verifica hashes y conteos."""
    ejemplos_raw = _git_show(BANCO_COMMIT, f"{BANCO_BASE}/ejemplos.jsonl")
    exclusiones_raw = _git_show(BANCO_COMMIT, f"{BANCO_BASE}/exclusiones.json")
    if sha(ejemplos_raw) != EJEMPLOS_SHA_DECLARADO:
        sys.exit("ejemplos.jsonl del banco no coincide con tokens.json del commit fijado.")
    if sha(exclusiones_raw) != EXCLUSIONES_SHA_DECLARADA:
        sys.exit("exclusiones.json del banco no coincide con manifest.json del commit fijado.")
    exclusiones = json.loads(exclusiones_raw.decode("utf-8"))
    filas = [json.loads(l) for l in ejemplos_raw.decode("utf-8").splitlines()]
    aceptadas = [f for f in filas if f["familia"] not in exclusiones]
    apartadas = [f for f in filas if f["familia"] in exclusiones]
    familias = {f["familia"] for f in aceptadas}
    if not (len(aceptadas) == ESPERADO_ACEPTADAS and len(apartadas) == ESPERADO_APARTADAS
            and len(familias) == ESPERADO_FAMILIAS):
        sys.exit(
            f"Banco inesperado: {len(aceptadas)} aceptadas, {len(apartadas)} apartadas, "
            f"{len(familias)} familias (esperado 5520/480/276).")
    return aceptadas, exclusiones, {
        "banco_commit": BANCO_COMMIT,
        "ejemplos_sha256": sha(ejemplos_raw),
        "exclusiones_sha256": sha(exclusiones_raw),
        "aceptadas": len(aceptadas),
        "apartadas": len(apartadas),
        "familias": len(familias),
        "por_clase": dict(Counter(f["etiqueta"] for f in aceptadas)),
        "por_lote": dict(Counter(f["lote"] for f in aceptadas)),
        "uso": "entrenamiento_desarrollo",
        "split": None,
    }


def incrustar(textos: list[str], tokenizer, modelo, dispositivo: str) -> tuple[list[list[float]], dict]:
    """Embeddings con encoder congelado: promedio enmascarado, límite 128 tokens."""
    import torch
    for p in modelo.parameters():
        p.requires_grad_(False)
    modelo.eval()
    if any(p.requires_grad for p in modelo.parameters()):
        sys.exit("El encoder no quedó congelado.")
    truncados = 0
    vectores: list[list[float]] = []
    t0 = time.perf_counter()
    with torch.no_grad():
        for i in range(0, len(textos), LOTE_EMBEDDINGS):
            lote = textos[i:i + LOTE_EMBEDDINGS]
            tok = tokenizer(lote, padding=True, truncation=True,
                            max_length=LIMITE_TOKENS, return_tensors="pt")
            n_reales = tok["attention_mask"].sum(dim=1)
            # Con padding a la derecha, truncar en 128 se detecta si alguna
            # secuencia sin truncar superaría el límite.
            sin_truncar = tokenizer(lote, padding=False, truncation=False)["input_ids"]
            truncados += sum(1 for ids in sin_truncar if len(ids) > LIMITE_TOKENS)
            tok = {k: v.to(dispositivo) for k, v in tok.items()}
            h = modelo(**tok).last_hidden_state
            mask = tok["attention_mask"].unsqueeze(-1).float()
            medios = (h * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1.0)
            vectores.extend(medios.cpu().tolist())
            _ = n_reales  # longitudes reales ya contadas en sin_truncar
    ms = (time.perf_counter() - t0) * 1000
    return vectores, {"truncados_en_128": truncados, "ms_incrustacion": round(ms, 1)}


def ajustar(X, y: list[int]) -> tuple[dict, dict]:
    from sklearn.linear_model import LogisticRegression
    clf = LogisticRegression(C=LR_CONFIG["C"], solver=LR_CONFIG["solver"],
                             max_iter=LR_CONFIG["max_iter"], random_state=SEMILLA)
    t0 = time.perf_counter()
    clf.fit(X, y)
    ms = (time.perf_counter() - t0) * 1000
    if clf.classes_.tolist() != [0, 1]:
        sys.exit(f"Clases inesperadas: {clf.classes_.tolist()}.")
    return {
        "coef": clf.coef_[0].tolist(),
        "intercepto": float(clf.intercept_[0]),
        "n_iter": [int(n) for n in clf.n_iter_],
    }, {"ms_ajuste": round(ms, 1)}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--salida", type=Path, default=AQUI / "tito_logreg.json")
    p.add_argument("--solo-cpu", action="store_true", default=True,
                   help="usa CPU aunque haya GPU (medición comparable con laboratorio)")
    args = p.parse_args(argv)

    aceptadas, _exclusiones, datos = cargar_banco()
    textos = [f["texto"] for f in aceptadas]
    y = [1 if f["etiqueta"] == "estafa" else 0 for f in aceptadas]

    from transformers import AutoModel, AutoTokenizer
    import torch
    from huggingface_hub import snapshot_download
    snap = Path(snapshot_download(ENCODER_ID, revision=ENCODER_REVISION))
    tok_sha = sha((snap / "tokenizer.json").read_bytes())
    if tok_sha != TOKENIZER_SHA_DECLARADO:
        sys.exit(f"tokenizer.json inesperado: {tok_sha}.")
    tokenizer = AutoTokenizer.from_pretrained(str(snap))
    dispositivo = "cpu"
    modelo = AutoModel.from_pretrained(ENCODER_ID, revision=ENCODER_REVISION).to(dispositivo)

    X, info_emb = incrustar(textos, tokenizer, modelo, dispositivo)
    pesos, info_fit = ajustar(X, y)

    import sklearn, tokenizers, transformers
    artefacto = {
        "formato": "tito-logreg-v1",
        "clases": {"1": "estafa", "0": "legitima"},
        "pesos": pesos,
        "config_regresion": {"semilla": SEMILLA, **LR_CONFIG},
        "umbral_derivacion": 0.5,  # convención exploratoria del flujo, no del ajuste
        "encoder": {
            "id": ENCODER_ID,
            "revision": ENCODER_REVISION,
            "congelado": True,
            "representacion": "promedio_enmascarado_ultima_capa",
            "hidden": int(modelo.config.hidden_size),
        },
        "tokenizador": {
            "revision_declarada": ENCODER_REVISION,
            "tokenizer_sha256": tok_sha,
            "limite_tokens": LIMITE_TOKENS,
            **{k: v for k, v in info_emb.items() if k != "ms_incrustacion"},
        },
        "datos": datos,
        "entrenamiento": {
            "librerias": {
                "torch": torch.__version__,
                "transformers": transformers.__version__,
                "scikit-learn": sklearn.__version__,
                "tokenizers": tokenizers.__version__,
                "numpy": __import__("numpy").__version__,
            },
            "maquina": _info_maquina(),
            "ms_incrustacion": info_emb["ms_incrustacion"],
            **info_fit,
        },
        "codigo": _info_codigo(),
        "nota_uso": ("entrenamiento_desarrollo; no calibra el umbral sobre las ocho "
                     "conversaciones ni toca el test reservado."),
    }
    args.salida.write_text(json.dumps(artefacto, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
    print(json.dumps({
        "salida": str(args.salida),
        "artefacto_sha256": sha(args.salida.read_bytes()),
        "aceptadas": datos["aceptadas"],
        "familias": datos["familias"],
        "truncados_en_128": info_emb["truncados_en_128"],
        **info_fit,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
