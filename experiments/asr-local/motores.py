"""Motores de ASR local para streaming y procesamiento por segmentos.

Contiene:
- MotorASR: interfaz común.
- MotorSherpaZipformer: Zipformer streaming español via sherpa-onnx (motor principal).
- MotorFasterWhisper: faster-whisper en modo por segmentos (segundo motor, NO streaming).
- MotorFalso: motor simulado determinístico para pruebas unitarias sin dependencias externas.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


@dataclass
class EventoASR:
    tipo: str  # "parcial" | "final"
    segmento: int
    texto: str
    inicio_audio_s: float
    fin_audio_s: float
    proceso_ms: float


class MotorASR(ABC):
    """Interfaz base para motores de ASR local."""

    nombre: str
    modelo_id: str
    es_streaming: bool
    tipo_entrega: str  # "parciales_y_finales" | "finales_por_segmento"

    @abstractmethod
    def inicializar(self) -> None:
        """Carga el modelo en memoria."""
        pass

    @abstractmethod
    def procesar_bloque(
        self,
        muestras: np.ndarray,
        inicio_bloque_s: float,
        fin_bloque_s: float,
    ) -> list[EventoASR]:
        """Procesa un bloque de audio y retorna actualizaciones si las hay."""
        pass

    @abstractmethod
    def vaciar_final(self, fin_audio_s: float) -> list[EventoASR]:
        """Cierra el stream al finalizar el audio y emite resultados pendientes."""
        pass

    @abstractmethod
    def metadatos(self) -> dict[str, Any]:
        """Retorna información del modelo y configuración."""
        pass


class MotorSherpaZipformer(MotorASR):
    """Zipformer streaming en español vía sherpa-onnx.

    Reutiliza la lógica de experiments/laboratorio/asr.py agregando
    detección de endpoint para segmentar turnos y emitir parciales/finales.
    """

    MODELO_POR_DEFECTO = "csukuangfj/sherpa-onnx-streaming-zipformer-es-kroko-2025-08-06"
    ARCHIVOS_REQUERIDOS = ("encoder.onnx", "decoder.onnx", "joiner.onnx", "tokens.txt")

    def __init__(
        self,
        modelo_dir_o_repo: str = MODELO_POR_DEFECTO,
        hilos: int = 4,
        sample_rate: int = 16000,
        enable_endpoint: bool = True,
        rule1_silence: float = 2.4,
        rule2_silence: float = 1.0,
        rule3_utterance: float = 20.0,
    ):
        self.nombre = "sherpa-zipformer"
        self.modelo_id = modelo_dir_o_repo
        self.es_streaming = True
        self.tipo_entrega = "parciales_y_finales"
        self.hilos = hilos
        self.sample_rate = sample_rate
        self.enable_endpoint = enable_endpoint
        self.rule1_silence = rule1_silence
        self.rule2_silence = rule2_silence
        self.rule3_utterance = rule3_utterance
        self.corte_silencio_s = 0.8
        self.umbral_rms_silencio = 0.005

        self.model_dir: Path | None = None
        self.recognizer: Any = None
        self.stream: Any = None

        self.segmento_actual: int = 1
        self.inicio_segmento_s: float = 0.0
        self.ultimo_texto_parcial: str = ""
        self.silencio_acum_s: float = 0.0

    def _asegurar_modelo(self) -> Path:
        """Verifica existencia local o descarga del Hugging Face Hub."""
        ruta_directa = Path(self.modelo_id)
        if ruta_directa.exists() and all((ruta_directa / f).exists() for f in self.ARCHIVOS_REQUERIDOS):
            return ruta_directa

        # Buscar en cache local experiments/asr-local/modelos
        cache_local = Path("experiments/asr-local/modelos") / Path(self.modelo_id).name
        if cache_local.exists() and all((cache_local / f).exists() for f in self.ARCHIVOS_REQUERIDOS):
            return cache_local

        # Descargar de Hugging Face
        try:
            from huggingface_hub import snapshot_download
        except ImportError as e:
            raise RuntimeError("Falta huggingface-hub para descargar el modelo.") from e

        cache_local.parent.mkdir(parents=True, exist_ok=True)
        ruta_descargada = Path(
            snapshot_download(repo_id=self.modelo_id, local_dir=str(cache_local))
        )
        faltan = [f for f in self.ARCHIVOS_REQUERIDOS if not (ruta_descargada / f).exists()]
        if faltan:
            raise RuntimeError(f"El repositorio {self.modelo_id} no contiene: {faltan}")
        return ruta_descargada

    def inicializar(self) -> None:
        import sherpa_onnx

        self.model_dir = self._asegurar_modelo()
        self.recognizer = sherpa_onnx.OnlineRecognizer.from_transducer(
            tokens=str(self.model_dir / "tokens.txt"),
            encoder=str(self.model_dir / "encoder.onnx"),
            decoder=str(self.model_dir / "decoder.onnx"),
            joiner=str(self.model_dir / "joiner.onnx"),
            num_threads=self.hilos,
            provider="cpu",
            sample_rate=self.sample_rate,
            feature_dim=80,
            decoding_method="greedy_search",
            enable_endpoint_detection=self.enable_endpoint,
            rule1_min_trailing_silence=self.rule1_silence,
            rule2_min_trailing_silence=self.rule2_silence,
            rule3_min_utterance_length=self.rule3_utterance,
        )
        self.stream = self.recognizer.create_stream()
        self.segmento_actual = 1
        self.inicio_segmento_s = 0.0
        self.ultimo_texto_parcial = ""
        self.silencio_acum_s = 0.0

    def reiniciar(self) -> None:
        """Vuelve al estado de recién inicializado sin recargar el modelo (descarta lo oído)."""
        self.recognizer.reset(self.stream)
        self.segmento_actual = 1
        self.inicio_segmento_s = 0.0
        self.ultimo_texto_parcial = ""
        self.silencio_acum_s = 0.0

    def procesar_bloque(
        self,
        muestras: np.ndarray,
        inicio_bloque_s: float,
        fin_bloque_s: float,
    ) -> list[EventoASR]:
        t0 = time.perf_counter()
        eventos: list[EventoASR] = []

        # Asegurar float32 en [-1.0, 1.0]
        if muestras.dtype != np.float32:
            muestras = muestras.astype(np.float32)

        dur_bloque_s = fin_bloque_s - inicio_bloque_s
        rms = float(np.sqrt(np.mean(muestras**2))) if len(muestras) > 0 else 0.0
        if rms < self.umbral_rms_silencio:
            self.silencio_acum_s += dur_bloque_s
        else:
            self.silencio_acum_s = 0.0

        self.stream.accept_waveform(self.sample_rate, muestras)
        while self.recognizer.is_ready(self.stream):
            self.recognizer.decode_stream(self.stream)

        t_proc_ms = (time.perf_counter() - t0) * 1000.0

        # Condición de fin de segmento: endpoint del reconocedor o corte por silencio acumulado con texto previo
        es_endpoint = False
        if self.enable_endpoint and self.recognizer.is_endpoint(self.stream):
            es_endpoint = True
        elif self.silencio_acum_s >= self.corte_silencio_s and bool(self.ultimo_texto_parcial):
            es_endpoint = True

        if es_endpoint:
            # Purgar lookahead del modelo con 0.3s de silencio antes de leer el texto definitivo
            purgar = np.zeros(int(0.3 * self.sample_rate), dtype=np.float32)
            self.stream.accept_waveform(self.sample_rate, purgar)
            while self.recognizer.is_ready(self.stream):
                self.recognizer.decode_stream(self.stream)

            texto = self.recognizer.get_result(self.stream).strip()
            if texto:
                eventos.append(
                    EventoASR(
                        tipo="final",
                        segmento=self.segmento_actual,
                        texto=texto,
                        inicio_audio_s=round(self.inicio_segmento_s, 3),
                        fin_audio_s=round(fin_bloque_s, 3),
                        proceso_ms=round(t_proc_ms, 2),
                    )
                )
                self.segmento_actual += 1
                self.inicio_segmento_s = fin_bloque_s
                self.ultimo_texto_parcial = ""
            self.recognizer.reset(self.stream)
            self.silencio_acum_s = 0.0
        else:
            texto = self.recognizer.get_result(self.stream).strip()
            if texto and texto != self.ultimo_texto_parcial:
                self.ultimo_texto_parcial = texto
                eventos.append(
                    EventoASR(
                        tipo="parcial",
                        segmento=self.segmento_actual,
                        texto=texto,
                        inicio_audio_s=round(self.inicio_segmento_s, 3),
                        fin_audio_s=round(fin_bloque_s, 3),
                        proceso_ms=round(t_proc_ms, 2),
                    )
                )

        return eventos

    def vaciar_final(self, fin_audio_s: float) -> list[EventoASR]:
        t0 = time.perf_counter()
        eventos: list[EventoASR] = []

        # Cola de lookahead extendida (2.0s de silencio) para garantizar que el encoder streaming
        # procese hasta la última palabra del audio sin truncamiento
        cola = np.zeros(int(2.0 * self.sample_rate), dtype=np.float32)
        self.stream.accept_waveform(self.sample_rate, cola)
        self.stream.input_finished()

        while self.recognizer.is_ready(self.stream):
            self.recognizer.decode_stream(self.stream)

        texto = self.recognizer.get_result(self.stream).strip()
        t_proc_ms = (time.perf_counter() - t0) * 1000.0

        if texto:
            eventos.append(
                EventoASR(
                    tipo="final",
                    segmento=self.segmento_actual,
                    texto=texto,
                    inicio_audio_s=round(self.inicio_segmento_s, 3),
                    fin_audio_s=round(fin_audio_s, 3),
                    proceso_ms=round(t_proc_ms, 2),
                )
            )
            self.segmento_actual += 1
            self.ultimo_texto_parcial = ""

        return eventos

    def metadatos(self) -> dict[str, Any]:
        import sherpa_onnx

        return {
            "motor": self.nombre,
            "modelo_id": self.modelo_id,
            "ruta_modelo": str(self.model_dir) if self.model_dir else None,
            "es_streaming": self.es_streaming,
            "tipo_entrega": self.tipo_entrega,
            "version_sherpa": getattr(sherpa_onnx, "__version__", "unknown"),
            "hilos": self.hilos,
            "sample_rate": self.sample_rate,
            "segmentacion": {
                "tipo": "endpoint_detection_nativo",
                "rule1_silence": self.rule1_silence,
                "rule2_silence": self.rule2_silence,
                "rule3_utterance": self.rule3_utterance,
            },
        }


class MotorFasterWhisper(MotorASR):
    """Segundo motor: faster-whisper en modo por segmentos (NO streaming).

    Acumula audio o transcribe por segmentos detectados con VAD interno.
    Solo emite actualizaciones de tipo 'final' al completarse cada segmento.
    """

    def __init__(
        self,
        modelo_tamanio: str = "base",
        hilos: int = 4,
        sample_rate: int = 16000,
        device: str = "cpu",
        compute_type: str = "int8",
        idioma: str = "es",
    ):
        self.nombre = "whisper"
        self.modelo_id = f"faster-whisper-{modelo_tamanio}"
        self.modelo_tamanio = modelo_tamanio
        self.es_streaming = False
        self.tipo_entrega = "finales_por_segmento"
        self.hilos = hilos
        self.sample_rate = sample_rate
        self.device = device
        self.compute_type = compute_type
        self.idioma = idioma

        self.model: Any = None
        self.buffer_muestras: list[np.ndarray] = []
        self.duracion_buffer_s: float = 0.0

    def inicializar(self) -> None:
        from faster_whisper import WhisperModel

        self.model = WhisperModel(
            self.modelo_tamanio,
            device=self.device,
            compute_type=self.compute_type,
            cpu_threads=self.hilos,
        )
        self.buffer_muestras = []
        self.duracion_buffer_s = 0.0

    def procesar_bloque(
        self,
        muestras: np.ndarray,
        inicio_bloque_s: float,
        fin_bloque_s: float,
    ) -> list[EventoASR]:
        # En modo no streaming por lotes, acumula el audio
        self.buffer_muestras.append(muestras)
        self.duracion_buffer_s = fin_bloque_s
        # No emite parciales en streaming porque este motor no es streaming
        return []

    def vaciar_final(self, fin_audio_s: float) -> list[EventoASR]:
        t0 = time.perf_counter()
        if not self.buffer_muestras:
            return []

        audio_completo = np.concatenate(self.buffer_muestras).astype(np.float32)

        # Transcribir pasando el ndarray float32 directamente (evita problemas con av.open)
        segments, info = self.model.transcribe(
            audio_completo,
            language=self.idioma,
            beam_size=5,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500),
        )

        eventos: list[EventoASR] = []
        seg_idx = 1
        t_total_proc_ms = (time.perf_counter() - t0) * 1000.0

        segments_list = list(segments)
        num_segs = len(segments_list)
        ms_por_seg = round(t_total_proc_ms / max(1, num_segs), 2)

        for s in segments_list:
            texto = s.text.strip()
            if texto:
                eventos.append(
                    EventoASR(
                        tipo="final",
                        segmento=seg_idx,
                        texto=texto,
                        inicio_audio_s=round(s.start, 3),
                        fin_audio_s=round(s.end, 3),
                        proceso_ms=ms_por_seg,
                    )
                )
                seg_idx += 1

        return eventos

    def metadatos(self) -> dict[str, Any]:
        import faster_whisper

        return {
            "motor": self.nombre,
            "modelo_id": self.modelo_id,
            "tamanio": self.modelo_tamanio,
            "es_streaming": self.es_streaming,
            "tipo_entrega": self.tipo_entrega,
            "version_faster_whisper": getattr(faster_whisper, "__version__", "unknown"),
            "device": self.device,
            "compute_type": self.compute_type,
            "hilos": self.hilos,
            "sample_rate": self.sample_rate,
            "idioma": self.idioma,
            "segmentacion": {
                "tipo": "vad_filter_whisper",
                "declaracion": "NO streaming, procesamiento segmentado offline/lote",
            },
        }


class MotorFalso(MotorASR):
    """Motor falso para tests unitarios rápidos y deterministas.

    Permite simular eventos parciales y finales programados según el tiempo de audio.
    """

    def __init__(self, eventos_programados: list[dict[str, Any]] | None = None):
        self.nombre = "falso"
        self.modelo_id = "test-mock-asr"
        self.es_streaming = True
        self.tipo_entrega = "parciales_y_finales"
        self.eventos_programados = eventos_programados or [
            {"tiempo_audio_s": 0.5, "tipo": "parcial", "segmento": 1, "texto": "hola"},
            {"tiempo_audio_s": 1.0, "tipo": "parcial", "segmento": 1, "texto": "hola mundo"},
            {"tiempo_audio_s": 1.5, "tipo": "final", "segmento": 1, "texto": "Hola mundo."},
            {"tiempo_audio_s": 2.0, "tipo": "parcial", "segmento": 2, "texto": "segundo"},
            {"tiempo_audio_s": 2.5, "tipo": "final", "segmento": 2, "texto": "Segundo segmento."},
        ]
        self._indice = 0

    def inicializar(self) -> None:
        self._indice = 0

    def procesar_bloque(
        self,
        muestras: np.ndarray,
        inicio_bloque_s: float,
        fin_bloque_s: float,
    ) -> list[EventoASR]:
        eventos = []
        while self._indice < len(self.eventos_programados):
            prog = self.eventos_programados[self._indice]
            if prog["tiempo_audio_s"] <= fin_bloque_s:
                eventos.append(
                    EventoASR(
                        tipo=prog["tipo"],
                        segmento=prog["segmento"],
                        texto=prog["texto"],
                        inicio_audio_s=round(max(0.0, prog["tiempo_audio_s"] - 0.5), 3),
                        fin_audio_s=round(prog["tiempo_audio_s"], 3),
                        proceso_ms=10.0,
                    )
                )
                self._indice += 1
            else:
                break
        return eventos

    def vaciar_final(self, fin_audio_s: float) -> list[EventoASR]:
        eventos = []
        while self._indice < len(self.eventos_programados):
            prog = self.eventos_programados[self._indice]
            eventos.append(
                EventoASR(
                    tipo=prog["tipo"],
                    segmento=prog["segmento"],
                    texto=prog["texto"],
                    inicio_audio_s=round(max(0.0, prog["tiempo_audio_s"] - 0.5), 3),
                    fin_audio_s=round(fin_audio_s, 3),
                    proceso_ms=10.0,
                )
            )
            self._indice += 1
        return eventos

    def metadatos(self) -> dict[str, Any]:
        return {
            "motor": self.nombre,
            "modelo_id": self.modelo_id,
            "es_streaming": self.es_streaming,
            "tipo_entrega": self.tipo_entrega,
            "segmentacion": {"tipo": "mock"},
        }
