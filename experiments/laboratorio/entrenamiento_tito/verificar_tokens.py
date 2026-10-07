"""Comprueba el límite del detector con un tokenizer.json local, sin bajar pesos."""

import argparse
from collections import Counter
import hashlib
from importlib.metadata import version
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tokenizer-json", type=Path, required=True)
    parser.add_argument("--modelo", required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--limite", type=int, default=128)
    args = parser.parse_args()
    if args.limite < 1:
        parser.error("el límite debe ser positivo")
    from tokenizers import Tokenizer

    tokenizer = Tokenizer.from_file(str(args.tokenizer_json))
    tokenizer.no_truncation()
    tokenizer.no_padding()
    carpeta = Path(__file__).resolve().parent
    entrada = carpeta / "ejemplos.jsonl"
    filas = [json.loads(linea) for linea in entrada.read_text(encoding="utf-8").splitlines()]
    conteos = [(fila["id"], len(tokenizer.encode(fila["texto"]).ids)) for fila in filas]
    excedidos = [{"id": fid, "tokens": n} for fid, n in conteos if n > args.limite]
    reporte = {
        "modelo": args.modelo, "revision_declarada": args.revision,
        "tokenizers_version": version("tokenizers"),
        "tokenizer_sha256": hashlib.sha256(args.tokenizer_json.read_bytes()).hexdigest(),
        "ejemplos_sha256": hashlib.sha256(entrada.read_bytes()).hexdigest(),
        "tokens_incluyen_especiales": True, "truncamiento": False,
        "limite": args.limite, "textos": len(conteos),
        "min": min(n for _, n in conteos), "max": max(n for _, n in conteos),
        "histograma": dict(sorted(Counter(n for _, n in conteos).items())),
        "excedidos": excedidos,
        "limite_evidencia": "Solo este tokenizer.json; otros encoders necesitan su propia comprobación.",
    }
    (carpeta / "tokens.json").write_text(json.dumps(reporte, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: reporte[k] for k in ("modelo", "textos", "min", "max")}, ensure_ascii=False))
    if excedidos:
        parser.exit(1, f"{len(excedidos)} textos exceden {args.limite} tokens; ver tokens.json\n")


if __name__ == "__main__":
    main()
