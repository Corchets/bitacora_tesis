"""Variante de desarrollo: cada línea y cada par no solapado de líneas."""
from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

from casos import DIR_TEXTO, cargar_referencia, cargar_texto
from ensayo_catalogo_qwen import CATALOGO, MODELO, guardar, lista, preparar_pares, sha
from filtro_tito import UMBRAL_TITO
from tito_real import TitoReal

ROOT = Path(__file__).resolve().parent
REVISION = "e61197ed45024b0ed8a2d74b80b4d909f1255473"


def ventanas_en(n: int):
    """(nombre, índice inicial inclusivo) sin usar futuras líneas."""
    yield "linea", n - 1
    if n % 2 == 0:
        yield "par", n - 2


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--lista", choices=("seleccion-57", "rapida-20"), default="seleccion-57")
    p.add_argument("--casos", help="IDs de la lista separados por coma")
    p.add_argument("--salida", type=Path, required=True)
    p.add_argument("--hilos", type=int, default=4)
    p.add_argument("--lote", type=int, default=4)
    p.add_argument("--max-tokens", type=int, default=2048)
    args = p.parse_args()
    permitidos = lista(args.lista)
    ids = args.casos.split(",") if args.casos else permitidos
    if not ids or len(ids) != len(set(ids)) or not set(ids) <= set(permitidos):
        p.error("IDs repetidos o fuera de la lista")
    if any(cargar_referencia(c).get("particion", "desarrollo") != "desarrollo" for c in ids):
        p.error("No se usa el test reservado")
    catalogo = json.loads(CATALOGO.read_text(encoding="utf-8"))
    categorias = catalogo["categorias"]
    if len(categorias) != 11 or len({c["id"] for c in categorias}) != 11:
        raise ValueError("Se esperan once categorías distintas")
    import torch
    import transformers
    from transformers import AutoModelForCausalLM, AutoTokenizer
    if not torch.cuda.is_available():
        raise RuntimeError("Se requiere GPU CUDA")
    if args.lote < 1:
        p.error("El lote debe ser positivo")
    torch.set_num_threads(args.hilos)
    torch.manual_seed(42)
    torch.cuda.manual_seed_all(42)
    dispositivo = torch.device("cuda:0")

    class TitoCuda(TitoReal):
        def _embed(self, textos):
            tokenizador, encoder, t, _ = self._asegurar_encoder()
            encoder.to(dispositivo)
            salida = []
            with t.inference_mode():
                for inicio in range(0, len(textos), 32):
                    lote = textos[inicio:inicio + 32]
                    self.truncamientos += self.contar_truncamientos(tokenizador, lote)
                    entradas = tokenizador(lote, padding=True, truncation=True,
                                           max_length=self.limite, return_tensors="pt").to(dispositivo)
                    oculto = encoder(**entradas).last_hidden_state
                    mascara = entradas["attention_mask"].unsqueeze(-1).float()
                    salida.extend(((oculto * mascara).sum(1) / mascara.sum(1).clamp(min=1)).cpu().tolist())
            return salida

    tok = AutoTokenizer.from_pretrained(MODELO, revision=REVISION, padding_side="left")
    modelo = AutoModelForCausalLM.from_pretrained(MODELO, revision=REVISION,
                                                  torch_dtype=torch.float16).to(dispositivo).eval()
    tito = TitoCuda()
    info_tito = tito.preparar()
    if info_tito.get("error"):
        raise RuntimeError(info_tito["error"])
    si, no = tok.convert_tokens_to_ids("yes"), tok.convert_tokens_to_ids("no")
    manifiesto = {"tipo": "manifiesto", "experimento": "catalogo-qwen-linea-y-par-v1",
                  "estado": "desarrollo; no test final; D07/D08/D09 abiertas",
                  "modelo": MODELO, "revision_resuelta": getattr(modelo.config, "_commit_hash", REVISION),
                  "catalogo_sha256": sha(CATALOGO), "ejecutor_sha256": sha(Path(__file__)),
                  "soporte_sha256": sha(ROOT / "ensayo_catalogo_qwen.py"),
                  "tito_sha256": sha(ROOT / "tito_logreg.json"), "lista": args.lista,
                  "lista_sha256": sha(ROOT / "casos" / "listas" / f"{args.lista}.txt"),
                  "casos": ids, "textos_sha256": {c: sha(DIR_TEXTO / f"{c}.txt") for c in ids},
                  "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                  "git_estado": subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip(),
                  "python": sys.version, "plataforma": platform.platform(), "torch": torch.__version__,
                  "transformers": transformers.__version__, "dispositivo": str(dispositivo),
                  "gpu": torch.cuda.get_device_name(dispositivo), "precision_qwen": "float16",
                  "precision_tito": "float32", "lote": args.lote, "hilos": args.hilos,
                  "max_tokens_par": args.max_tokens, "seed": 42, "umbral_tito": UMBRAL_TITO,
                  "tito_preparacion": info_tito, "ventanas": ["linea", "par"],
                  "regla_par": "líneas 1-2, 3-4, etc.; última impar no evaluada",
                  "regla_tito": "puntuar frase actual; en pares usar la segunda línea"}
    with args.salida.open("x", encoding="utf-8") as salida:
        guardar(salida, manifiesto)
        for case_id in ids:
            lineas = cargar_texto(case_id)
            for n, actual in enumerate(lineas, 1):
                puntaje, error, tito_ms = tito.puntuar(n, actual.texto)
                if error or puntaje is None:
                    guardar(salida, {"tipo": "error_tito", "case_id": case_id, "linea": n,
                                     "error": error, "ms": tito_ms})
                    continue
                for ventana, inicio in ventanas_en(n):
                    texto = "\n".join(f"{l.hablante}: {l.texto}" for l in lineas[inicio:n])
                    pares, recortes = preparar_pares(tok, catalogo["instruccion"], categorias, texto, args.max_tokens)
                    torch.cuda.synchronize()
                    torch.cuda.reset_peak_memory_stats(dispositivo)
                    instante = time.perf_counter()
                    scores = []
                    try:
                        with torch.inference_mode():
                            for j in range(0, len(pares), args.lote):
                                entradas = tok.pad({"input_ids": pares[j:j + args.lote]},
                                                   padding=True, return_tensors="pt").to(dispositivo)
                                logits = modelo(**entradas, logits_to_keep=1).logits[:, -1, :]
                                scores.extend(torch.softmax(logits[:, [no, si]].float(), dim=1)[:, 1].cpu().tolist())
                        torch.cuda.synchronize()
                    except Exception as exc:
                        guardar(salida, {"tipo": "error_qwen", "case_id": case_id, "linea": n,
                                         "ventana": ventana, "error": f"{type(exc).__name__}: {exc}"})
                        continue
                    guardar(salida, {"tipo": "actualizacion", "case_id": case_id, "linea": n,
                                     "ventana": ventana, "puntajes": dict(zip((c["id"] for c in categorias), scores)),
                                     "tito_puntaje": puntaje, "tito_ms": tito_ms,
                                     "tito_activa": puntaje >= UMBRAL_TITO,
                                     "linea_inicio": inicio + 1,
                                     "tokens_documento_recortados": dict(zip((c["id"] for c in categorias), recortes)),
                                     "gpu_pico_asignado_bytes": torch.cuda.max_memory_allocated(dispositivo),
                                     "qwen_ms": round((time.perf_counter() - instante) * 1000, 1)})
            if len(lineas) % 2:
                guardar(salida, {"tipo": "par_final_incompleto", "case_id": case_id, "linea": len(lineas)})
            print(f"{case_id}: {len(lineas)} líneas", flush=True)
        guardar(salida, {"tipo": "fin"})


if __name__ == "__main__":
    main()
