"""Ensayo nuevo de catálogo contrastivo; no modifica el ensayo previo.

Registra puntajes por prefijo sin consultar referencias durante inferencia.
Salida JSONL nueva; las métricas se calculan aparte, con referencias existentes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

from casos import DIR_TEXTO, cargar_referencia, cargar_texto
from filtro_tito import UMBRAL_TITO
from tito_real import TitoReal

ROOT = Path(__file__).resolve().parent
CATALOGO = ROOT / "prompts" / "catalogo-qwen-decisiones-v1.json"
MODELO = "Qwen/Qwen3-Reranker-0.6B"
PREFIX = ("<|im_start|>system\nJudge whether the Document meets the requirements based on the Query "
          "and the Instruct provided. Note that the answer can only be \"yes\" or \"no\".<|im_end|>\n"
          "<|im_start|>user\n")
SUFFIX = "<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lista(nombre: str) -> list[str]:
    ruta = ROOT / "casos" / "listas" / f"{nombre}.txt"
    return [s.strip() for s in ruta.read_text(encoding="utf-8").splitlines()
            if s.strip() and not s.lstrip().startswith("#")]


def guardar(f, registro: dict) -> None:
    f.write(json.dumps(registro, ensure_ascii=False, allow_nan=False) + "\n")
    f.flush()


def preparar_pares(tok, instruccion: str, categorias: list[dict], texto: str, limite: int):
    """Recorta solo el comienzo del documento; conserva la consulta y el sufijo completos."""
    documento = tok.encode(texto, add_special_tokens=False)
    pares, recortes = [], []
    sufijo = tok.encode(SUFFIX, add_special_tokens=False)
    for categoria in categorias:
        cabecera = (PREFIX + f"<Instruct>: {instruccion}\n<Query>: {categoria['texto']}\n<Document>: ")
        prefijo = tok.encode(cabecera, add_special_tokens=False)
        cupo = limite - len(prefijo) - len(sufijo)
        if cupo <= 0:
            raise ValueError("El límite no permite conservar la instrucción, consulta y sufijo")
        tokens = documento[-cupo:]
        pares.append(prefijo + tokens + sufijo)
        recortes.append(len(documento) - len(tokens))
    return pares, recortes


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--lista", choices=("seleccion-57", "rapida-20"), default="seleccion-57")
    p.add_argument("--casos", help="IDs existentes de la lista separados por coma; para pruebas pequeñas")
    p.add_argument("--salida", type=Path, required=True, help="archivo JSONL nuevo; no se sobreescribe")
    p.add_argument("--revision", default="main", help="revisión Hugging Face; se registra el commit resuelto")
    p.add_argument("--max-tokens", type=int, default=2048, help="tope de cada par completo")
    p.add_argument("--hilos", type=int, default=4)
    p.add_argument("--lote", type=int, default=4, help="pares procesados juntos en la GPU")
    args = p.parse_args()
    ids_lista = lista(args.lista)
    ids = args.casos.split(",") if args.casos else ids_lista
    if not ids or len(set(ids)) != len(ids) or not set(ids) <= set(ids_lista):
        p.error("Los IDs deben ser distintos y pertenecer a la lista elegida")
    # Exclusión del test reservado antes de iniciar la inferencia.
    if any(cargar_referencia(c).get("particion", "desarrollo") != "desarrollo" for c in ids):
        p.error("No se permite utilizar test reservado")
    catalogo = json.loads(CATALOGO.read_text(encoding="utf-8"))
    categorias = catalogo["categorias"]
    if len(categorias) != 11 or len({c["id"] for c in categorias}) != 11:
        raise ValueError("El catálogo debe contener once IDs diferentes")
    import torch
    import transformers
    from transformers import AutoModelForCausalLM, AutoTokenizer

    torch.set_num_threads(args.hilos)
    if not torch.cuda.is_available():
        raise RuntimeError("Se requiere GPU CUDA; el ensayo no usa CPU como alternativa")
    if args.lote < 1:
        p.error("El lote debe ser positivo")
    dispositivo = torch.device("cuda:0")
    torch.manual_seed(42)
    torch.cuda.manual_seed_all(42)

    class TitoCuda(TitoReal):
        def _embed(self, textos):
            tokenizador, encoder, torch_mod, _ = self._asegurar_encoder()
            encoder.to(dispositivo)
            vectores = []
            with torch_mod.inference_mode():
                for i in range(0, len(textos), 32):
                    lote = textos[i:i + 32]
                    self.truncamientos += self.contar_truncamientos(tokenizador, lote)
                    entradas = tokenizador(lote, padding=True, truncation=True,
                                           max_length=self.limite, return_tensors="pt").to(dispositivo)
                    h = encoder(**entradas).last_hidden_state
                    mascara = entradas["attention_mask"].unsqueeze(-1).float()
                    vectores.extend(((h * mascara).sum(dim=1) / mascara.sum(dim=1).clamp(min=1)).cpu().tolist())
            return vectores

    tok = AutoTokenizer.from_pretrained(MODELO, revision=args.revision, padding_side="left")
    modelo = AutoModelForCausalLM.from_pretrained(MODELO, revision=args.revision,
                                                  torch_dtype=torch.float16).to(dispositivo).eval()
    tito = TitoCuda()
    tito_info = tito.preparar()
    if tito_info.get("error"):
        raise RuntimeError(f"No se pudo preparar Tito: {tito_info['error']}")
    yes, no = tok.convert_tokens_to_ids("yes"), tok.convert_tokens_to_ids("no")
    revision_real = getattr(modelo.config, "_commit_hash", None)
    git = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    estado = subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip()
    info = {"tipo": "manifiesto", "experimento": "catalogo-qwen-decisiones-v1",
            "estado": "desarrollo, no test final; D07/D08/D09 abiertas", "modelo": MODELO,
            "revision_solicitada": args.revision, "revision_resuelta": revision_real,
            "catalogo_sha256": sha(CATALOGO), "ejecutor_sha256": sha(Path(__file__)),
            "tito_sha256": sha(ROOT / "tito_logreg.json"), "lista": args.lista,
            "lista_sha256": sha(ROOT / "casos" / "listas" / f"{args.lista}.txt"),
            "casos": ids, "textos_sha256": {c: sha(DIR_TEXTO / f"{c}.txt") for c in ids},
            "git_head": git, "git_estado": estado, "python": sys.version,
            "plataforma": platform.platform(), "procesador": platform.processor(),
            "torch": torch.__version__, "transformers": transformers.__version__,
            "dispositivo": str(dispositivo), "gpu": torch.cuda.get_device_name(dispositivo),
            "gpu_memoria_total_bytes": torch.cuda.get_device_properties(dispositivo).total_memory,
            "precision_qwen": "float16", "precision_tito": "float32",
            "lote": args.lote, "hilos": args.hilos, "max_tokens_par": args.max_tokens,
            "umbral_tito": UMBRAL_TITO, "seed": 42,
            "tito_preparacion": tito_info, "ventanas": ["cuatro", "acumulada"]}
    with args.salida.open("x", encoding="utf-8") as salida:
        guardar(salida, info)
        for case_id in ids:
            lineas = cargar_texto(case_id)
            for n, actual in enumerate(lineas, 1):
                inicio = time.perf_counter()
                puntaje, error, tito_ms = tito.puntuar(n, actual.texto)
                if error or puntaje is None:
                    guardar(salida, {"tipo": "error_tito", "case_id": case_id, "linea": n,
                                     "error": error, "ms": tito_ms})
                    continue
                for ventana, comienzo in (("cuatro", max(0, n - 4)), ("acumulada", 0)):
                    texto = "\n".join(f"{l.hablante}: {l.texto}" for l in lineas[comienzo:n])
                    pares, recortes = preparar_pares(tok, catalogo["instruccion"], categorias, texto, args.max_tokens)
                    torch.cuda.synchronize()
                    torch.cuda.reset_peak_memory_stats(dispositivo)
                    inicio_qwen = time.perf_counter()
                    scores = []
                    try:
                        with torch.inference_mode():
                            for j in range(0, len(pares), args.lote):
                                lote = pares[j:j + args.lote]
                                entradas = tok.pad({"input_ids": lote}, padding=True, return_tensors="pt").to(dispositivo)
                                logits = modelo(**entradas, logits_to_keep=1).logits[:, -1, :]
                                scores.extend(torch.softmax(logits[:, [no, yes]].float(), dim=1)[:, 1].cpu().tolist())
                        torch.cuda.synchronize()
                    except Exception as exc:
                        guardar(salida, {"tipo": "error_qwen", "case_id": case_id, "linea": n,
                                         "ventana": ventana, "error": f"{type(exc).__name__}: {exc}"})
                        continue
                    guardar(salida, {"tipo": "actualizacion", "case_id": case_id, "linea": n,
                                     "ventana": ventana, "puntajes": dict(zip((c["id"] for c in categorias), scores)),
                                     "tito_puntaje": puntaje, "tito_ms": tito_ms,
                                     "tito_activa": puntaje >= UMBRAL_TITO,
                                     "tokens_documento_recortados": dict(zip((c["id"] for c in categorias), recortes)),
                                     "gpu_pico_asignado_bytes": torch.cuda.max_memory_allocated(dispositivo),
                                     "qwen_ms": round((time.perf_counter() - inicio_qwen) * 1000, 1)})
                print(f"{case_id} {n}/{len(lineas)} ({time.perf_counter() - inicio:.1f} s)", flush=True)
        guardar(salida, {"tipo": "fin"})


if __name__ == "__main__":
    main()
