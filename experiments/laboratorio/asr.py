"""Quien escribe: Zipformer streaming via sherpa-onnx.

En #29 Moonshine es solo un id en la tabla de gamas, no un motor.
"""

from pathlib import Path

ARCHIVOS = ("encoder.onnx", "decoder.onnx", "joiner.onnx", "tokens.txt")


def es_moonshine(asr_id: str) -> bool:
    return asr_id.startswith("moonshine-ai/")


def descargar_modelo(asr_id: str, cache_dir: str | Path) -> Path:
    """Baja el repo del Hub al cache del contenedor. Devuelve la carpeta."""
    if es_moonshine(asr_id):
        raise NotImplementedError(
            "Moonshine no implementado en #29: esta corrida usa config `alta` "
            "(Zipformer Kroko). El id de baja queda en gamas.json como tabla."
        )
    try:
        from huggingface_hub import snapshot_download
    except ImportError as e:
        raise RuntimeError("Falta huggingface-hub. Corre con Docker.") from e
    ruta = Path(
        snapshot_download(repo_id=asr_id, cache_dir=str(cache_dir), local_files_only=False)
    )
    faltan = [f for f in ARCHIVOS if not (ruta / f).exists()]
    if faltan:
        raise RuntimeError(f"El repo {asr_id} no trae: {faltan} (se bajo en {ruta})")
    return ruta


def crear_reconocedor(model_dir: str | Path, hilos: int):
    """Zipformer streaming en CPU. Sin endpoint detection: el turno lo cierra el silencio."""
    try:
        import sherpa_onnx
    except ImportError as e:
        raise RuntimeError("Falta sherpa-onnx. Corre con Docker.") from e
    model_dir = Path(model_dir)
    return sherpa_onnx.OnlineRecognizer.from_transducer(
        tokens=str(model_dir / "tokens.txt"),
        encoder=str(model_dir / "encoder.onnx"),
        decoder=str(model_dir / "decoder.onnx"),
        joiner=str(model_dir / "joiner.onnx"),
        num_threads=hilos,
        provider="cpu",
        sample_rate=16000,
        feature_dim=80,
        decoding_method="greedy_search",
        enable_endpoint_detection=False,
    )


def alimentar(reconocedor, stream, muestras, sample_rate: int = 16000) -> str:
    """Mete un pedazo de audio y devuelve el borrador del turno actual."""
    stream.accept_waveform(sample_rate, muestras)
    while reconocedor.is_ready(stream):
        reconocedor.decode_stream(stream)
    return reconocedor.get_result(stream)


def vaciar_final(reconocedor, stream, sample_rate: int = 16000) -> str:
    """Cola de cierre: medio segundo de silencio, fin de entrada y drenaje."""
    import numpy as np

    cola = np.zeros(int(0.5 * sample_rate), dtype=np.float32)
    stream.accept_waveform(sample_rate, cola)
    stream.input_finished()
    while reconocedor.is_ready(stream):
        reconocedor.decode_stream(stream)
    return reconocedor.get_result(stream)
