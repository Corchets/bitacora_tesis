"""Hotwords para sherpa-onnx (#94): vocabulario BPE sintético, lectura de listas y revisión manual.

sherpa-onnx exige `modeling_unit="bpe"` y un `bpe_vocab` para los hotwords. El modelo Kroko no trae
ese archivo ni el `bpe.model`, así que se arma uno sintético desde `tokens.txt`
(PLAN-VOZ-REAL.md §5). Con ese vocabulario sherpa parte cada palabra de la hotword con el camino
de mayor puntaje total entre las piezas (ssentencepiece, programación dinámica; no hace
fusiones BPE).

Puntaje de las piezas. El plan decía `token<TAB>-id`. Con eso gana el camino de menor suma de ids
y las palabras se parten en letras sueltas («transferencia» -> `t r a n s f e r e n ci a`), que no
es lo que el modelo emite («trans fe r encia»). Se comparó contra lo que el modelo emite al
reconocer 63 palabras sueltas (voz TTS de macOS) y 10 palabras en frase: `-id` acierta 6 de 63;
`-(ln(id+2)+3)`, que prefiere pocas piezas y desempata por id bajo, acierta 63 de 63 y 10 de 10.
Por eso el modo por defecto es `log`; `id` queda para repetir lo del plan.

`tokenizar_hotword` repite la partición de sherpa en Python para revisarla a mano. Reimplementa el
algoritmo leído en el código fuente de ssentencepiece (v0.7, el que usa sherpa-onnx 1.13.8) porque
sherpa no expone las piezas desde Python: sirve para detectar hotwords que se parten en letras
sueltas o con caracteres que el modelo no tiene, y no reemplaza mirar si la hotword realmente
sube en una corrida.

Uso:
    python hotwords.py [--modelo <carpeta con tokens.txt>] [--hotwords <archivo>] [--puntaje log|id]
"""

from __future__ import annotations

import argparse
import hashlib
import math
import re
import tempfile
from pathlib import Path

MARCA_PALABRA = "▁"  # «▁»: el espacio de SentencePiece
DIR_ASR = Path(__file__).resolve().parent
HOTWORDS_POR_DEFECTO = DIR_ASR / "voz-real" / "hotwords.txt"
DIR_TRABAJO_POR_DEFECTO = Path(tempfile.gettempdir()) / "asr-local-hotwords"
_SECCION = re.compile(r"^#\s*\[(?P<nombre>[\w\- ]+)\]\s*$")
_PUNTAJE = re.compile(r"\s+:(?P<puntaje>-?\d+(?:\.\d+)?)\s*$")
MODOS_PUNTAJE = ("log", "id")
PUNTAJE_POR_DEFECTO = "log"
PENALIDAD_POR_PIEZA = 3.0  # en modo log: cada pieza de más resta esto; alcanza para preferir las piezas largas


def leer_tokens(ruta_tokens: str | Path) -> dict[str, int]:
    """`tokens.txt` como {pieza: id}."""
    tokens: dict[str, int] = {}
    for linea in Path(ruta_tokens).read_text(encoding="utf-8").splitlines():
        if not linea.strip():
            continue
        pieza, id_texto = linea.rstrip().rsplit(" ", 1)
        tokens[pieza] = int(id_texto)
    return tokens


def puntaje_pieza(id_: int, modo: str = PUNTAJE_POR_DEFECTO) -> float:
    """Puntaje sintético de una pieza: `id` = `-id` (el plan); `log` = `-(ln(id+2) + 3)`."""
    if modo == "id":
        return float(-id_)
    if modo == "log":
        return round(-(math.log(id_ + 2) + PENALIDAD_POR_PIEZA), 4)
    raise ValueError(f"puntaje debe ser uno de {MODOS_PUNTAJE}: {modo!r}")


def texto_bpe_vocab(tokens: dict[str, int], modo: str = PUNTAJE_POR_DEFECTO) -> str:
    """Contenido del `bpe.vocab` sintético: `pieza<TAB>puntaje`, una por línea."""
    return "".join(f"{pieza}\t{puntaje_pieza(id_, modo):g}\n" for pieza, id_ in tokens.items())


def leer_hotwords(ruta: str | Path) -> list[str]:
    """Una hotword por línea. Se ignoran las vacías y las que empiezan con «#» (comentarios y secciones)."""
    return [linea.strip() for linea in Path(ruta).read_text(encoding="utf-8").splitlines()
            if linea.strip() and not linea.lstrip().startswith("#")]


def leer_secciones(ruta: str | Path) -> dict[str, list[str]]:
    """Las hotwords agrupadas por sección. Una sección empieza con una línea `# [nombre]`."""
    secciones: dict[str, list[str]] = {}
    actual = "sin_seccion"
    for linea in Path(ruta).read_text(encoding="utf-8").splitlines():
        marca = _SECCION.match(linea.strip())
        if marca:
            actual = marca["nombre"].strip()
            secciones.setdefault(actual, [])
        elif linea.strip() and not linea.lstrip().startswith("#"):
            secciones.setdefault(actual, []).append(linea.strip())
    return secciones


def sin_puntaje(hotword: str) -> str:
    """La hotword sin el sufijo opcional ` :puntaje` de sherpa."""
    return _PUNTAJE.sub("", hotword).strip()


def tokenizar_hotword(hotword: str, tokens: dict[str, int], modo: str = PUNTAJE_POR_DEFECTO) -> list[str]:
    """Piezas de la hotword según el codificador de sherpa-onnx (ssentencepiece), palabra por palabra.

    Cada palabra lleva «▁» adelante y se parte con el camino de mayor puntaje total entre las piezas
    del vocabulario (programación dinámica, como `Ssentencepiece::CalcDp`); a igual puntaje gana la
    pieza más larga. Un carácter que ninguna pieza cubre queda como «<fuera:x>»: sherpa descarta la
    hotword entera.
    """
    piezas: list[str] = []
    for palabra in sin_puntaje(hotword).split():
        texto = MARCA_PALABRA + palabra
        n = len(texto)
        mejor = [0.0] * (n + 1)  # mejor puntaje desde la posición i hasta el final
        siguiente = [-1] * (n + 1)
        for i in range(n - 1, -1, -1):
            puntaje_i, fin_i = float("-inf"), -1
            for fin in range(i + 1, n + 1):
                id_ = tokens.get(texto[i:fin])
                if id_ is None:
                    continue
                puntaje = float(f"{puntaje_pieza(id_, modo):g}") + mejor[fin]
                if puntaje >= puntaje_i:  # a igual puntaje gana la pieza más larga
                    puntaje_i, fin_i = puntaje, fin
            mejor[i], siguiente[i] = (0.0, -1) if fin_i == -1 else (puntaje_i, fin_i)
        i = 0
        while i < n:
            if siguiente[i] == -1:
                piezas.append(f"<fuera:{texto[i]}>")
                i += 1
            else:
                piezas.append(texto[i:siguiente[i]])
                i = siguiente[i]
    return piezas


def revisar_hotwords(hotwords: list[str], tokens: dict[str, int], modo: str = PUNTAJE_POR_DEFECTO) -> list[dict]:
    """Cómo se parte cada hotword y qué avisos merece para la revisión manual."""
    revision = []
    for hotword in hotwords:
        piezas = tokenizar_hotword(hotword, tokens, modo)
        fuera = [p for p in piezas if p.startswith("<fuera:")]
        # «▁» solo no cuenta: es el comienzo de palabra. Letra suelta = pieza de un carácter sin «▁».
        sueltas = [p for p in piezas if len(p.replace(MARCA_PALABRA, "")) == 1 and p != MARCA_PALABRA]
        letras = [p for p in piezas if p != MARCA_PALABRA]
        avisos = []
        if fuera:
            avisos.append("caracteres fuera del vocabulario: sherpa descarta la hotword")
        # Las siglas (DNI, CBU, PIN) el modelo también las emite letra por letra: no es un defecto.
        es_sigla = all(palabra.isupper() for palabra in sin_puntaje(hotword).split())
        if letras and not es_sigla and len(sueltas) / len(letras) > 0.5:
            avisos.append("más de la mitad son letras sueltas: el boost se reparte entre letras")
        revision.append({"hotword": hotword, "piezas": piezas, "n_piezas": len(piezas),
                         "avisos": avisos, "ok": not avisos})
    return revision


def tabla_revision_markdown(revision: list[dict]) -> str:
    """La revisión como tabla Markdown (para pegar en una corrida o en un issue)."""
    filas = ["| Hotword | Piezas | Aviso |", "|---|---|---|"]
    for r in revision:
        filas.append(f"| `{r['hotword']}` | `{' '.join(r['piezas'])}` | {'; '.join(r['avisos']) or 'ok'} |")
    return "\n".join(filas)


def preparar_hotwords(modelo_dir: str | Path, hotwords_file: str | Path,
                      dir_trabajo: str | Path | None = None, puntaje: str = PUNTAJE_POR_DEFECTO) -> dict:
    """Escribe el `bpe.vocab` sintético y la lista de hotwords limpia, fuera de Git, y devuelve sus rutas.

    Los archivos llevan el hash del contenido en el nombre: dos motores con listas distintas
    no se pisan y repetir la corrida reutiliza lo ya escrito.
    """
    tokens = leer_tokens(Path(modelo_dir) / "tokens.txt")
    hotwords = leer_hotwords(hotwords_file)
    if not hotwords:
        raise ValueError(f"La lista de hotwords está vacía: {hotwords_file}")
    destino = Path(dir_trabajo) if dir_trabajo is not None else DIR_TRABAJO_POR_DEFECTO
    destino.mkdir(parents=True, exist_ok=True)
    vocab = texto_bpe_vocab(tokens, puntaje)
    lista = "".join(h + "\n" for h in hotwords)
    huella = hashlib.sha256((vocab + "\0" + lista).encode("utf-8")).hexdigest()[:12]
    ruta_vocab, ruta_lista = destino / f"bpe-{huella}.vocab", destino / f"hotwords-{huella}.txt"
    ruta_vocab.write_text(vocab, encoding="utf-8")
    ruta_lista.write_text(lista, encoding="utf-8")
    return {"bpe_vocab": ruta_vocab, "hotwords_file": ruta_lista, "hotwords": hotwords, "huella": huella,
            "puntaje": puntaje}


def main() -> None:
    modelo_defecto = DIR_ASR / "modelos" / "sherpa-onnx-streaming-zipformer-es-kroko-2025-08-06"
    p = argparse.ArgumentParser(description="Muestra cómo se parte cada hotword con el tokens.txt del modelo.")
    p.add_argument("--modelo", default=str(modelo_defecto), help="carpeta del modelo (con tokens.txt)")
    p.add_argument("--hotwords", default=str(HOTWORDS_POR_DEFECTO), help="archivo de hotwords")
    p.add_argument("--puntaje", choices=MODOS_PUNTAJE, default=PUNTAJE_POR_DEFECTO,
                   help="puntaje sintético de las piezas del bpe.vocab (defecto: log; id = lo del plan)")
    args = p.parse_args()
    tokens = leer_tokens(Path(args.modelo) / "tokens.txt")
    revision = revisar_hotwords(leer_hotwords(args.hotwords), tokens, args.puntaje)
    print(tabla_revision_markdown(revision))
    malas = [r["hotword"] for r in revision if not r["ok"]]
    print(f"\n{len(revision)} hotwords, {len(malas)} con aviso" + (f": {', '.join(malas)}" if malas else "."))


if __name__ == "__main__":
    main()
