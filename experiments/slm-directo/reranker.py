"""Cross-encoder / NLI zero-shot como detector del ensayo (rama `reranker-prueba`).

Por cada línea nueva arma una ventana con las últimas líneas disponibles (con A/B) y la
puntúa junto con descripciones de pedidos (`REQUEST_*` de MANUAL-ANOTACION.md), en un solo
lote. El riesgo de la línea es el máximo entre los pedidos; cada pedido es el promedio de
sus paráfrasis. Nunca recibe la referencia humana ni líneas futuras.

Tres familias, un mismo contrato (`evaluar(lineas) -> Respuesta`, como `DetectorReglas`):

- `nli`: modelo NLI (p. ej. mDeBERTa-xnli). Premisa = ventana, hipótesis = descripción;
  puntaje = P(entailment) frente a contradicción, como el zero-shot multi-label de HF.
- `cross-encoder`: reranker de búsqueda (p. ej. bge-reranker-v2-m3). Consulta =
  descripción, pasaje = ventana; puntaje = sigmoide del logit.
- `qwen3-reranker`: reranker con instrucción (Qwen3-Reranker). Puntaje = P("yes") frente a
  P("no") en el último token, con el formato de su ficha. Verificar la ficha antes de correr.
- `falso`: solapamiento de palabras, sin dependencias. Solo para pruebas y humo.

La alerta de la corrida (`riesgo > umbral`) es solo un registro: la política se elige
después, sin volver a correr, con `analisis/<fecha>-reranker-zero-shot/analizar.py`.
Los puntajes por etiqueta quedan en `crudo` (JSON) para ese análisis.

> **Estado: propuesta sin discutir.** Las descripciones dependen de la taxonomía candidata
> (D07) y la política de alerta de D08; esto no elige detector (D09).
"""

from __future__ import annotations

import gc
import json
import math
import platform
import re
import statistics
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from casos import Linea
from detectores import DIR_PROMPTS, Respuesta, huella

ARCHIVO_HIPOTESIS = DIR_PROMPTS / "hipotesis_reranker.json"
BACKENDS = ("nli", "cross-encoder", "qwen3-reranker", "falso")
MODOS_ETIQUETAS = ("pedidos", "todas")
PREFIJO_PEDIDO = "REQUEST_"

# Backend por defecto según el nombre del modelo (`--reranker-backend auto`).
BACKEND_POR_PREFIJO = (
    ("moritzlaurer/", "nli"),
    ("baai/bge-reranker", "cross-encoder"),
    ("qwen/qwen3-reranker", "qwen3-reranker"),
    ("falso", "falso"),
)


def backend_de(modelo: str, pedido: str = "auto") -> str:
    if pedido != "auto":
        if pedido not in BACKENDS:
            raise ValueError(f"backend desconocido {pedido!r}; opciones: auto, {', '.join(BACKENDS)}")
        return pedido
    nombre = modelo.lower()
    for prefijo, backend in BACKEND_POR_PREFIJO:
        if nombre.startswith(prefijo):
            return backend
    raise ValueError(f"No sé qué backend usar con {modelo!r}: indicá --reranker-backend.")


def cargar_hipotesis(modo: str = "pedidos", ruta: Path = ARCHIVO_HIPOTESIS) -> tuple[dict[str, list[str]], dict]:
    """(etiqueta → paráfrasis, datos completos del archivo). `pedidos` deja solo `REQUEST_*`."""
    if modo not in MODOS_ETIQUETAS:
        raise ValueError(f"modo de etiquetas desconocido {modo!r}; opciones: {MODOS_ETIQUETAS}")
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    etiquetas = {**datos["pedidos"], **({} if modo == "pedidos" else datos["maniobras"])}
    for etiqueta, parafrasis in etiquetas.items():
        if not parafrasis or not all(isinstance(p, str) and p.strip() for p in parafrasis):
            raise ValueError(f"{etiqueta}: hace falta al menos una paráfrasis no vacía")
    if not any(e.startswith(PREFIJO_PEDIDO) for e in etiquetas):
        raise ValueError("el archivo no tiene ningún pedido REQUEST_*")
    return etiquetas, datos


def contar_palabras(texto: str) -> int:
    return len(texto.split())


def armar_ventana(lineas: list[Linea] | tuple[Linea, ...], n_lineas: int, max_tokens: int,
                  contar=contar_palabras) -> tuple[str, dict]:
    """Últimas `n_lineas` con `A:`/`B:`, recortadas por la izquierda hasta `max_tokens`.

    Se descartan primero las líneas más viejas; si la más reciente sola no entra, se le
    quitan palabras del comienzo. El recorte nunca toca el final: ahí está lo nuevo.
    Devuelve (texto, {"lineas": incluidas, "lineas_recortadas": n, "palabras_recortadas": n}).
    """
    if n_lineas < 1 or max_tokens < 1:
        raise ValueError("la ventana necesita al menos una línea y un token")
    partes = [f"{l.hablante}: {l.texto}" for l in lineas[-n_lineas:]]
    recortadas = 0
    while len(partes) > 1 and contar("\n".join(partes)) > max_tokens:
        partes.pop(0)
        recortadas += 1
    palabras = partes[0].split(" ")
    quitadas = 0
    while len(palabras) > 1 and contar(" ".join(palabras)) > max_tokens:
        palabras.pop(0)
        quitadas += 1
    if quitadas:
        partes[0] = "… " + " ".join(palabras)
    return "\n".join(partes), {"lineas": len(partes), "lineas_recortadas": recortadas, "palabras_recortadas": quitadas}


class Puntuador(Protocol):
    def preparar(self) -> dict: ...
    def contar_tokens(self, texto: str) -> int: ...
    def puntuar(self, pares: list[tuple[str, str]]) -> list[float]: ...
    def liberar(self) -> None: ...


def _sin_tildes(texto: str) -> str:
    return texto.lower().translate(str.maketrans("áéíóúüñ", "aeiouun"))


@dataclass
class PuntuadorFalso:
    """Solapamiento de palabras largas entre hipótesis y ventana. Determinista y sin modelos."""

    modelo: str = "falso"

    def preparar(self) -> dict:
        return {"backend": "falso", "modelo": self.modelo, "revision": "", "carga_ms": 0.0}

    def contar_tokens(self, texto: str) -> int:
        return contar_palabras(texto)

    def puntuar(self, pares: list[tuple[str, str]]) -> list[float]:
        salida = []
        for hipotesis, ventana in pares:
            clave = {p for p in re.findall(r"\w+", _sin_tildes(hipotesis)) if len(p) > 4}
            texto = set(re.findall(r"\w+", _sin_tildes(ventana)))
            salida.append(len(clave & texto) / len(clave) if clave else 0.0)
        return salida

    def liberar(self) -> None:
        pass


@dataclass
class PuntuadorHF:
    """Modelos de Hugging Face en CPU con `transformers` (se importan al preparar)."""

    modelo: str
    backend: str
    revision: str | None = None
    hilos: int | None = None
    lote: int = 16
    max_longitud: int = 512
    instruccion: str = ""  # solo qwen3-reranker
    _tok: object = field(default=None, repr=False)
    _red: object = field(default=None, repr=False)
    _torch: object = field(default=None, repr=False)
    _info: dict = field(default_factory=dict, repr=False)

    def preparar(self) -> dict:
        import torch
        import transformers
        from transformers import AutoModelForCausalLM, AutoModelForSequenceClassification, AutoTokenizer

        if self.hilos:
            torch.set_num_threads(self.hilos)
        inicio = time.perf_counter()
        kw = {"revision": self.revision} if self.revision else {}
        if self.backend == "qwen3-reranker":
            self._tok = AutoTokenizer.from_pretrained(self.modelo, padding_side="left", **kw)
            self._red = AutoModelForCausalLM.from_pretrained(self.modelo, **kw).eval()
            self._si = self._tok.convert_tokens_to_ids("yes")
            self._no = self._tok.convert_tokens_to_ids("no")
        else:
            self._tok = AutoTokenizer.from_pretrained(self.modelo, **kw)
            self._red = AutoModelForSequenceClassification.from_pretrained(self.modelo, **kw).eval()
            if self.backend == "nli":
                etiquetas = {i: str(n).lower() for i, n in self._red.config.id2label.items()}
                self._entail = next((i for i, n in etiquetas.items() if n.startswith("entail")), None)
                self._contra = next((i for i, n in etiquetas.items() if n.startswith("contradict")), None)
                if self._entail is None:
                    raise ValueError(f"{self.modelo} no tiene clase entailment: {etiquetas}")
        self._torch = torch
        carga_ms = (time.perf_counter() - inicio) * 1000
        inicio = time.perf_counter()
        self.puntuar([("Una persona le pide un código a otra.", "A: hola\nB: hola, ¿quién habla?")])
        self._info = {
            "backend": self.backend,
            "modelo": self.modelo,
            "revision": getattr(self._red.config, "_commit_hash", None) or self.revision or "",
            "parametros": sum(p.numel() for p in self._red.parameters()),
            "carga_ms": round(carga_ms, 1),
            "calentamiento_ms": round((time.perf_counter() - inicio) * 1000, 1),
            "hilos": torch.get_num_threads(),
            "torch": torch.__version__,
            "transformers": transformers.__version__,
            "lote": self.lote,
            "max_longitud": self.max_longitud,
            **({"instruccion": self.instruccion} if self.backend == "qwen3-reranker" else {}),
        }
        return dict(self._info)

    def contar_tokens(self, texto: str) -> int:
        return len(self._tok(texto, add_special_tokens=False)["input_ids"])

    def puntuar(self, pares: list[tuple[str, str]]) -> list[float]:
        salida: list[float] = []
        with self._torch.inference_mode():
            for i in range(0, len(pares), self.lote):
                salida += self._lote(pares[i:i + self.lote])
        return salida

    def _lote(self, pares: list[tuple[str, str]]) -> list[float]:
        torch = self._torch
        if self.backend == "nli":
            # Premisa = ventana, hipótesis = descripción del pedido.
            enc = self._tok([v for _, v in pares], [h for h, _ in pares], padding=True,
                            truncation="only_first", max_length=self.max_longitud, return_tensors="pt")
            logits = self._red(**enc).logits
            if self._contra is not None:
                logits = logits[:, [self._entail, self._contra]]
                return torch.softmax(logits, dim=-1)[:, 0].tolist()
            return torch.softmax(logits, dim=-1)[:, self._entail].tolist()
        if self.backend == "cross-encoder":
            # Consulta = descripción, pasaje = ventana.
            enc = self._tok([h for h, _ in pares], [v for _, v in pares], padding=True,
                            truncation="only_second", max_length=self.max_longitud, return_tensors="pt")
            return torch.sigmoid(self._red(**enc).logits.view(-1).float()).tolist()
        # qwen3-reranker: formato de la ficha del modelo (Qwen/Qwen3-Reranker-0.6B).
        prefijo = ("<|im_start|>system\nJudge whether the Document meets the requirements based on the Query "
                   "and the Instruct provided. Note that the answer can only be \"yes\" or \"no\".<|im_end|>\n"
                   "<|im_start|>user\n")
        sufijo = "<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"
        textos = [f"{prefijo}<Instruct>: {self.instruccion}\n<Query>: {h}\n<Document>: {v}{sufijo}" for h, v in pares]
        enc = self._tok(textos, padding=True, truncation=True, max_length=self.max_longitud, return_tensors="pt")
        ultimo = self._red(**enc).logits[:, -1, :]
        dos = torch.stack([ultimo[:, self._no], ultimo[:, self._si]], dim=1)
        return torch.softmax(dos.float(), dim=-1)[:, 1].tolist()

    def liberar(self) -> None:
        self._red = self._tok = None
        gc.collect()


def crear_puntuador(modelo: str, backend: str, *, revision: str | None = None, hilos: int | None = None,
                    lote: int = 16, max_longitud: int = 512, instruccion: str = "") -> Puntuador:
    if backend == "falso":
        return PuntuadorFalso(modelo)
    return PuntuadorHF(modelo, backend, revision, hilos, lote, max_longitud, instruccion)


@dataclass
class DetectorReranker:
    """Detector zero-shot sobre una ventana de las últimas líneas. Sin estado entre líneas."""

    puntuador: Puntuador
    hipotesis: dict[str, list[str]]
    ventana: int = 4
    max_tokens: int = 384
    umbral: float = 0.5
    nombre = "reranker"

    def preparar(self) -> dict:
        return self.puntuador.preparar()

    def liberar(self) -> None:
        self.puntuador.liberar()

    def evaluar(self, lineas: list[Linea] | tuple[Linea, ...]) -> Respuesta:
        inicio = time.perf_counter()
        try:
            texto, recorte = armar_ventana(lineas, self.ventana, self.max_tokens, self.puntuador.contar_tokens)
            pares = [(h, texto) for parafrasis in self.hipotesis.values() for h in parafrasis]
            puntajes = self.puntuador.puntuar(pares)
        except Exception as e:  # un fallo del modelo no es una predicción de legitimidad
            return Respuesta(valida=False, error=f"reranker: {type(e).__name__}: {e}",
                             ms=(time.perf_counter() - inicio) * 1000)
        ms = (time.perf_counter() - inicio) * 1000
        if len(puntajes) != len(pares) or not all(math.isfinite(p) for p in puntajes):
            return Respuesta(valida=False, error="reranker: puntajes inválidos", ms=ms)
        por_etiqueta, i = {}, 0
        for etiqueta, parafrasis in self.hipotesis.items():
            por_etiqueta[etiqueta] = statistics.fmean(puntajes[i:i + len(parafrasis)])
            i += len(parafrasis)
        pedidos = {e: p for e, p in por_etiqueta.items() if e.startswith(PREFIJO_PEDIDO)}
        top = max(pedidos, key=pedidos.get)
        riesgo = pedidos[top]
        return Respuesta(
            valida=True,
            riesgo=riesgo,
            alerta_sugerida=riesgo > self.umbral,
            motivo=f"{top} ({riesgo:.2f})",
            evidencia=lineas[-1].texto,
            evidencia_en_texto=True,
            crudo=json.dumps({"puntajes": {e: round(p, 4) for e, p in por_etiqueta.items()}, "ventana": recorte},
                             ensure_ascii=False),
            ms=ms,
        )


def huella_hipotesis(etiquetas: dict[str, list[str]]) -> str:
    return huella(json.dumps(etiquetas, ensure_ascii=False, sort_keys=True))


def memoria_mb() -> dict:
    """RSS y pico del proceso en MB, si el sistema los informa (psutil o resource)."""
    try:
        import psutil

        info = psutil.Process().memory_info()
        pico = getattr(info, "peak_wset", None) or getattr(info, "peak_rss", None)
        return {"rss_mb": round(info.rss / 2**20, 1), "pico_mb": None if pico is None else round(pico / 2**20, 1)}
    except ImportError:
        pass
    try:
        import resource

        pico = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        # Linux informa KB; macOS, bytes.
        return {"rss_mb": None, "pico_mb": round(pico / (2**20 if platform.system() == "Darwin" else 2**10), 1)}
    except ImportError:
        return {"rss_mb": None, "pico_mb": None}
