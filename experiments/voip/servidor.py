#!/usr/bin/env python3
"""Servidor de la llamada en vivo: ASR por canal, detector y panel (frente 1, spike).

Cada persona corre `cliente.py`, que manda su micrófono (o un canal de un WAV) por
WebSocket. El servidor transcribe cada canal con su propio ASR (Zipformer streaming por defecto; Parakeet por
frases si se elige en el panel), escribe
`actualizaciones.jsonl` con el contrato de experiments/asr-local (la llamada se puede
volver a correr con replay.py), llama al detector y muestra todo en un panel web.

Por defecto se consulta al detector al cerrar cada turno de OTRA (ADR 0007, `turnos.py`): el
turno se cierra cuando PROTEGIDA empieza a hablar en serio o tras un silencio largo, y un turno
largo consulta igual al pasar el tope. Los umbrales son provisorios y van por línea de comandos
(`--turno-*`). `--disparo final` vuelve a consultar en cada frase de los dos lados, para comparar.

El detector evalúa siempre la foto más reciente: si llega texto mientras evalúa, la
siguiente evaluación toma lo último disponible y las intermedias se saltean. Así la
demora no crece con la cola, a diferencia del replay, que evalúa todas en orden.

Por defecto el detector es la configuración congelada de #143: Gemma 4 E2B directo con `c-json-corte-riesgo`
(cortado tras el riesgo, aviso con riesgo ≥ 0,3 y el motivo solo en el primer aviso), roles y solo OTRA.

Uso:
    python servidor.py --ollama-url http://<ip-de-ollama>:11434
    python servidor.py --detector reglas
    python servidor.py --detector tito-slm --prompt v4 --modelo gemma4:e2b-it-q4_K_M
    Panel: http://<ip>:8765/   ·   vista de la persona protegida: http://<ip>:8765/?vista=protegida

Una llamada empieza desde el panel o con el primer bloque de cliente.py. Termina con
«Terminar», al finalizar el ejemplo, al desconectar todos los clientes o con Ctrl+C.
Cada llamada queda en llamadas/<fecha>_<hora>_<microsegundos>/.

> Estado: propuesta sin discutir. No cierra D08 ni D09.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import math
import signal
import sys
import time
from contextlib import suppress
from datetime import datetime
from http import HTTPStatus
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from websockets.asyncio.server import broadcast, serve
from websockets.datastructures import Headers
from websockets.http11 import Response

import guia
import historial
from llamada import DIR_VOIP, DISPAROS, ROLES, SAMPLE_RATE, Llamada
from turnos import ReglasTurno

import replay  # noqa: E402  (rutas de slm-directo y replay ya agregadas por llamada.py)
from motores import DetectorSilero, MotorASR, MotorSherpaParakeet, MotorSherpaZipformer

DIR_MODELOS = DIR_VOIP.parent / "asr-local" / "modelos"
DIR_MODELO = DIR_MODELOS / "sherpa-onnx-streaming-zipformer-es-kroko-2025-08-06"
DIR_PARAKEET = DIR_MODELOS / "sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8"
MODELO_SILERO = DIR_MODELOS / "silero-vad" / "silero_vad.onnx"
URL_SILERO = "https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/silero_vad.onnx"

# Modelos de ASR que se pueden elegir desde el panel. Por defecto, la opción B, final desde ADR 0001 (asr-local/PLAN-VOZ-REAL.md §12.9). Whisper no está:
# solo transcribe al cerrar la frase y la demo tiene que ir escribiendo mientras se habla.
ASR_POR_DEFECTO = "parakeet-filtro"
MODELOS_ASR = {
    "zipformer": "Zipformer Kroko · antecedente",
    "parakeet": "Parakeet TDT 0.6B v3 · por frases",
    "parakeet-filtro": "Parakeet · RMS con filtro Silero · final",
    "parakeet-y": "Parakeet · RMS y Silero",
    "parakeet-silero": "Parakeet · solo Silero",
}
# Parakeet con Silero VAD, a prueba en el laboratorio (asr-local/PLAN-VOZ-REAL.md §12): modo de
# MotorPorFrases.MODOS_VAD y umbral de Silero. El umbral RMS y el corte siguen siendo los elegidos en el panel.
SILERO_ASR = {"parakeet-filtro": ("filtro", 0.5), "parakeet-y": ("y", 0.5), "parakeet-silero": ("silero", 0.9)}

EJEMPLOS = {nombre: DIR_VOIP.parent / "asr-local" / "audio" / f"{nombre}-tts-estereo.wav"
            for nombre in ("SC-WA-CODE-01", "LG-WA-CONSULTA-01", "SC-SOPORTE-CLAVE-01", "LG-SUPPORT-INFO-01")}


CORTE_AUTO = "auto"
# Al cortar, cuánto se espera al detector: una consulta en frío tardó 16 s y puede quedar otra pendiente.
ESPERA_DETECTOR_AL_CERRAR_S = 30.0
CORTE_RESPALDO_S = 0.8  # corte del motor cuando el corte es «auto» y el modelo no cierra la frase solo
CORTE_MIN_S, CORTE_MAX_S = 0.1, 3.0
UMBRAL_LLAMADA = 0.003
# Opción B de asr-local/PLAN-VOZ-REAL.md §12.9: con filtro Silero, el RMS corta a 0,008 también en la llamada.
UMBRAL_RMS_POR_ASR = {"parakeet-filtro": 0.008}


def umbral_de_llamada(asr: str) -> float:
    return UMBRAL_RMS_POR_ASR.get(asr, UMBRAL_LLAMADA)


def validar_corte(valor) -> str | float:
    """«auto» o un número de 0,1 a 3,0 s con un decimal; todo lo demás se rechaza."""
    if valor == CORTE_AUTO and isinstance(valor, str):
        return CORTE_AUTO
    if (isinstance(valor, bool) or not isinstance(valor, (int, float)) or not math.isfinite(valor)
            or not CORTE_MIN_S <= valor <= CORTE_MAX_S or abs(valor * 10 - round(valor * 10)) > 1e-9):
        raise ValueError("El corte de silencio debe ser «auto» o un número de 0,1 a 3,0 s con un decimal.")
    return round(float(valor), 1)


# Detectores que se pueden elegir desde el panel: Gemma 4 E2B directo, sin Tito (la configuración congelada de #143
# con el prompt por defecto), más las reglas como respaldo sin modelo. Tito viejo queda solo por línea de comandos.
# Tags completos: «gemma4:e2b» a secas baja otro artefacto según la plataforma (MLX en Mac), no el medido.
DETECTOR_POR_DEFECTO = "gemma4:e2b-it-q4_K_M"
DETECTORES_PANEL = ("gemma4:e2b-it-q4_K_M", "reglas")
DETECTORES_CON_MODELO = replay.DETECTORES_CON_MODELO
# Configuración congelada de #143 (ADR 0006 y 0007): C cortado tras el riesgo, «riesgo ≥ 0,3», el motivo solo en el
# primer aviso y solo OTRA. Si la prueba de sensibilidad adopta una variante de C, el cambio es --prompt.
PROMPT_POR_DEFECTO = "c-json-corte-riesgo"


def validar_detector(valor) -> str:
    if valor not in DETECTORES_PANEL:
        raise ValueError(f"Detector desconocido; opciones: {', '.join(DETECTORES_PANEL)}.")
    return valor


def info_detector(args: argparse.Namespace) -> dict:
    """Lo que el panel muestra del detector activo."""
    con_modelo = args.detector in DETECTORES_CON_MODELO
    return {"tipo": args.detector, "modelo": args.modelo if con_modelo else None,
            "prompt": getattr(args, "prompt", None) if con_modelo else None,
            "solo_otra": getattr(args, "solo_otra", False)}


def validar_configuracion(p: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    """Prompt, hablantes, Tito y solo OTRA: lo comparten servidor.py y medir.py.

    Sin --solo-otra ni --no-solo-otra, «solo OTRA» va con el SLM directo y los roles (la configuración congelada), y
    no con reglas ni Tito, como en correr.py.
    """
    detectores = replay.detectores
    if args.prompt not in detectores.PROMPTS:
        p.error(f"prompt desconocido {args.prompt!r}; opciones: {', '.join(detectores.PROMPTS)}")
    if args.hablantes == "ab" and detectores.usa_roles(args.prompt):
        p.error(f"el prompt {args.prompt} nombra a PROTEGIDA y OTRA: necesita --hablantes rol")
    if args.detector == "tito-slm" and args.prompt in detectores.PROMPTS_CORTE_RIESGO:
        p.error(f"tito-slm usa un prompt de un paso, no {args.prompt}: pasá --prompt v4 "
                "(la configuración congelada de #143 va sin Tito: --detector slm)")
    if args.solo_otra is None:
        args.solo_otra = args.detector == "slm" and args.hablantes == "rol"
    elif args.solo_otra and (args.detector != "slm" or args.hablantes != "rol"):
        p.error("--solo-otra corre solo el SLM y tiene que saber quién habla: usá --detector slm --hablantes rol")


def validar_asr(valor) -> str:
    if not isinstance(valor, str) or valor not in MODELOS_ASR:
        raise ValueError(f"Modelo de ASR desconocido; opciones: {', '.join(MODELOS_ASR)}.")
    if valor in SILERO_ASR and not MODELO_SILERO.is_file():
        raise ValueError(f"Falta el modelo de Silero: bajá {URL_SILERO} a {MODELO_SILERO}.")
    return valor


def reglas_turno(args: argparse.Namespace) -> ReglasTurno:
    """Las de la línea de comandos; sin ellas (tests, medir.py), las provisorias por defecto."""
    base = ReglasTurno()
    return ReglasTurno(palabras=getattr(args, "turno_palabras", base.palabras),
                       voz_s=getattr(args, "turno_voz_s", base.voz_s),
                       silencio_s=getattr(args, "turno_silencio_s", base.silencio_s),
                       tope_s=getattr(args, "turno_tope_s", base.tope_s))


def corte_de_linea_de_comandos(texto: str) -> str | float:
    try:
        return validar_corte(CORTE_AUTO if texto == CORTE_AUTO else float(texto))
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from None


class Servidor:
    def __init__(self, args: argparse.Namespace, detector, *, ahora=time.monotonic, dormir=asyncio.sleep) -> None:
        self.ahora = ahora
        self.dormir = dormir
        self.control = asyncio.Lock()
        self.config_llamada: dict = {}
        self.asr = validar_asr(getattr(args, "asr", ASR_POR_DEFECTO))
        self.config_asr: tuple[str | float, float] = (CORTE_AUTO, umbral_de_llamada(self.asr))  # (corte elegido, umbral RMS)
        self.args = args
        self.detector = detector
        self.llamada: Llamada | None = None
        # La próxima llamada se prepara de antemano: cargar los dos ASR tarda ~1 s y, si se
        # hiciera con el primer bloque, atrasaría ese canal respecto del otro.
        self.preparada: asyncio.Task | None = None
        self.clientes_audio: set = set()
        self.tarea_ejemplo: asyncio.Task | None = None
        self.paneles: set = set()
        self.historial: list[dict] = []  # para el panel que se conecta en medio de la llamada
        self.novedad = asyncio.Event()
        self.tarea_detector: asyncio.Task | None = None
        self.audio_terminado = False
        self.tarea_niveles: asyncio.Task | None = None
        # Última prueba cerrada y todavía sin guardar: «Guardar» actúa sobre ella.
        self.prueba_pendiente: Path | None = None

    def crear_motor(self) -> MotorASR:
        if self.asr == "parakeet" or self.asr in SILERO_ASR:
            modelo = str(DIR_PARAKEET) if DIR_PARAKEET.exists() else MotorSherpaParakeet.MODELO_POR_DEFECTO
            motor = MotorSherpaParakeet(modelo, hilos=self.args.hilos)
            if self.asr in SILERO_ASR:
                # Uno por canal: Silero guarda el estado de la voz que viene escuchando.
                motor.modo_vad, umbral = SILERO_ASR[self.asr]
                motor.detector_voz = DetectorSilero(MODELO_SILERO, umbral)
            return motor
        modelo = str(DIR_MODELO) if DIR_MODELO.exists() else MotorSherpaZipformer.MODELO_POR_DEFECTO
        return MotorSherpaZipformer(modelo, hilos=self.args.hilos)

    def difundir(self, mensaje: dict) -> None:
        self.historial.append(mensaje)
        broadcast(self.paneles, json.dumps(mensaje, ensure_ascii=False))

    def preparar(self) -> None:
        corte, umbral = self.config_asr

        def crear_configurado():
            motor = self.crear_motor()
            automatico = corte == CORTE_AUTO
            motor.corte_silencio_s = CORTE_RESPALDO_S if automatico else corte
            motor.umbral_rms_silencio = umbral
            # Con un número manda ese corte, incluso si supera el endpoint nativo del modelo.
            motor.enable_endpoint = automatico
            return motor

        self.preparada = asyncio.create_task(
            asyncio.to_thread(
                Llamada,
                crear_motor=crear_configurado,
                disparo=self.args.disparo,
                hablantes=getattr(self.args, "hablantes", "ab"),
                ahora=self.ahora,
                reglas_turno=reglas_turno(self.args),
                solo_otra=getattr(self.args, "solo_otra", False),
            )
        )

    async def abrir_llamada(self) -> Llamada:
        if self.preparada is None:
            self.preparar()
        try:
            llamada = await self.preparada
        finally:
            # Una carga fallida no debe envenenar todos los intentos siguientes.
            self.preparada = None
        self.novedad.clear()
        self.audio_terminado = False
        # El filtro guarda si ya derivó: cada llamada empieza de cero, también tras cambiar de vista.
        getattr(self.detector, "reiniciar", lambda: None)()
        momento = datetime.now()
        llamada.abrir(*self.nombres_de_llamada(momento))
        self.difundir_inicio(llamada)
        if self.config_llamada.get("modo") != "asr":
            self.tarea_detector = asyncio.create_task(self.trabajar_detector(llamada))
        self.tarea_niveles = asyncio.create_task(self.emitir_niveles(llamada))
        print(f"[llamada] {llamada.llamada_id} → {llamada.dir_salida}")
        return llamada

    def nombres_de_llamada(self, momento: datetime) -> tuple[str, Path]:
        return f"VIVO-{momento:%Y%m%d-%H%M%S-%f}", Path(self.args.salida) / f"{momento:%Y-%m-%d_%H%M%S-%f}"

    def difundir_inicio(self, llamada: Llamada) -> None:
        self.historial = []
        self.difundir({"tipo": "inicio", "llamada_id": llamada.llamada_id,
                       "modo": self.config_llamada.get("modo", "llamada"),
                       "detector": info_detector(self.args),
                       "corte_silencio_s": self.config_asr[0], "umbral_rms_silencio": self.config_asr[1],
                       "asr": self.asr})

    async def cerrar_llamada(self, *, esperada: Llamada | None = None) -> None:
        async with self.control:
            if esperada is not None and self.llamada is not esperada:
                return
            llamada, self.llamada = self.llamada, None
            if llamada is None:
                return
            ejemplo, self.tarea_ejemplo = self.tarea_ejemplo, None
            if ejemplo and ejemplo is not asyncio.current_task():
                ejemplo.cancel()
                with suppress(asyncio.CancelledError):
                    await ejemplo
            if self.tarea_niveles:
                self.tarea_niveles.cancel()
                with suppress(asyncio.CancelledError):
                    await self.tarea_niveles
                self.tarea_niveles = None
            clientes = tuple(self.clientes_audio)
            self.clientes_audio.clear()
            for ws in clientes:
                await ws.close(1000, "llamada terminada")
            if self.tarea_detector:
                await self.esperar_detector(llamada)
                self.tarea_detector = None
            for act in llamada.cerrar(self.manifiesto_extra()):
                self.difundir({**act, "tipo": "asr", "entrega": act["tipo"]})
            self.prueba_pendiente = llamada.dir_salida if self.config_llamada.get("modo") == "asr" else None
            self.difundir({"tipo": "fin", "llamada_id": llamada.llamada_id, "dir": str(llamada.dir_salida)})
            print(f"[llamada] cerrada: {llamada.dir_salida}")
            self.preparar()

    async def esperar_detector(self, llamada: Llamada) -> None:
        """Evalúa lo que ya se dijo antes de cerrar: si no, se pierde el pedido que llega justo antes del corte."""
        for act in llamada.vaciar_audio():
            self.difundir({**act, "tipo": "asr", "entrega": act["tipo"]})
            llamada.marcar_disparo(act)
        self.audio_terminado = True
        self.novedad.set()
        try:
            await asyncio.wait_for(self.tarea_detector, ESPERA_DETECTOR_AL_CERRAR_S)
        except TimeoutError:
            print(f"[llamada] el detector no terminó en {ESPERA_DETECTOR_AL_CERRAR_S} s: se descarta lo pendiente")

    def manifiesto_extra(self) -> dict:
        a = self.args
        carga = getattr(self.detector, "carga", None)
        return {
            "config": {"detector": None if self.config_llamada.get("modo") == "asr" else a.detector, "modelo": a.modelo if a.detector in DETECTORES_CON_MODELO else None,
                       "prompt": a.prompt if a.detector in DETECTORES_CON_MODELO else None, "hablantes": getattr(a, "hablantes", "ab"),
                       "solo_otra": getattr(a, "solo_otra", False),
                       "ollama_url": a.ollama_url if a.detector in DETECTORES_CON_MODELO else None,
                       "seed": a.seed if a.detector in DETECTORES_CON_MODELO else "no-aplica",
                       "corte_silencio_s": self.config_asr[0], "umbral_rms_silencio": self.config_asr[1],
                       "endpoint_nativo": self.config_asr[0] == CORTE_AUTO, "asr": self.asr, "hilos_asr": a.hilos, "carga_slm": carga},
            "inicio_panel": self.config_llamada,
            # La prueba se guarda solo si el presentador toca «Guardar»; hasta entonces se descarta.
            **({"guardada": False} if self.config_llamada.get("modo") == "asr" else {}),
            "codigo": replay.info_codigo(),
            "maquina": replay.info_maquina(),
        }

    async def emitir_niveles(self, llamada: Llamada) -> None:
        while True:
            await asyncio.sleep(0.1)
            # Telemetría efímera: no pasa por el historial, JSONL ni manifiesto.
            broadcast(self.paneles, json.dumps({"tipo": "niveles", **llamada.niveles()}))

    async def trabajar_detector(self, llamada: Llamada) -> None:
        while True:
            await self.novedad.wait()
            self.novedad.clear()
            n, foto, disparos = llamada.tomar_foto()
            if getattr(self.detector, "solo_cerradas", False):
                foto = tuple(llamada.contexto.cerrados)
            if llamada.aviso is None and foto and disparos:
                inicio = llamada.reloj()
                respuesta = await asyncio.to_thread(self.detector.evaluar, foto)
                ev = llamada.registrar_evaluacion(n, disparos, respuesta, inicio, llamada.reloj())
                self.difundir({"tipo": "detector", **llamada.evento_detector(ev)})
                if ev.aviso:
                    print(f"[AVISO] t={ev.fin_s:.2f}s · {respuesta.motivo}")
            if self.audio_terminado and not self.novedad.is_set():
                return

    def recibir_audio(self, rol: str, pcm: bytes, *, llegada: float | None = None) -> None:
        """Entrada común para cliente.py y el estéreo del ejemplo."""
        llamada, consulta = self.llamada, self.config_llamada.get("modo") != "asr"
        for act in llamada.recibir(rol, pcm, llegada=llegada):
            self.difundir({**act, "tipo": "asr", "entrega": act["tipo"]})
            if consulta:
                llamada.marcar_disparo(act)
        # Con turnos el disparo puede llegar sin texto nuevo: lo cierra el silencio del bloque.
        if consulta and llamada.disparos:
            self.novedad.set()

    async def atender_audio(self, ws, rol: str) -> None:
        if rol not in ROLES:
            await ws.close(1008, f"rol debe ser uno de {ROLES}")
            return
        # La admisión también espera la precarga: no mezclar un cliente que llegó
        # mientras iniciar todavía esperaba los motores del ejemplo.
        async with self.control:
            if self.llamada is not None and self.config_llamada.get("modo") == "asr" and rol != "protegida":
                await ws.close(1008, "Probar el ASR admite solamente el micrófono de protegida")
                return
            if self.llamada is not None and self.config_llamada.get("fuentes", {}).get(rol, {}).get("tipo") == "ejemplo":
                await ws.close(1008, "el rol ya recibe audio de la llamada de ejemplo")
                return
            self.clientes_audio.add(ws)
        print(f"[audio] conectado: {rol} ({ws.remote_address[0]})")
        try:
            async for mensaje in ws:
                if mensaje == "fin_audio":
                    # Viaja por el mismo socket que el PCM: todo lo anterior ya fue procesado.
                    await ws.send("audio_recibido")
                    continue
                if not isinstance(mensaje, bytes):
                    continue
                async with self.control:
                    if ws not in self.clientes_audio:
                        break
                    if self.llamada is None:
                        self.config_llamada = {}
                        await self.configurar_asr((validar_corte(self.args.corte_silencio), umbral_de_llamada(self.asr)))
                        self.llamada = await self.abrir_llamada()
                    self.recibir_audio(rol, mensaje)
        finally:
            pertenecia = ws in self.clientes_audio
            llamada = self.llamada
            self.clientes_audio.discard(ws)
            print(f"[audio] desconectado: {rol}")
            if pertenecia and not self.clientes_audio and self.tarea_ejemplo is None:
                await self.cerrar_llamada(esperada=llamada)

    async def configurar_asr(self, config: tuple[str | float, float], asr: str | None = None) -> None:
        asr = self.asr if asr is None else asr
        if config == self.config_asr and asr == self.asr:
            return
        if self.preparada is not None:
            with suppress(ValueError, OSError, RuntimeError):
                await self.preparada
        self.config_asr = config
        self.asr = asr
        self.preparar()

    async def configurar_detector(self, elegido: str) -> None:
        """Carga el detector que eligió el panel; si falla, sigue el que estaba.

        El modelo va directo, sin Tito, con el prompt de la línea de comandos. «Solo OTRA» lo fija la línea de comandos.
        """
        tipo, modelo = ("reglas", None) if elegido == "reglas" else ("slm", elegido)
        a = self.args
        if tipo == a.detector and (modelo is None or modelo == a.modelo):
            return
        try:
            self.detector = await asyncio.to_thread(
                replay.construir_detector,
                tipo,
                modelo=modelo,
                prompt_nombre=a.prompt,
                hablantes=getattr(a, "hablantes", "ab"),
                seed=a.seed,
                ollama_url=a.ollama_url,
                indicio=not getattr(a, "sin_indicio", False),
            )
        except (replay.correr.FalloAlCalentar, replay.cliente_ollama.ErrorOllama) as exc:
            raise RuntimeError(f"No se pudo cargar {modelo}: {exc} ¿Está Ollama abierto? Si falta el modelo: ollama pull {modelo}") from exc
        a.detector = tipo
        if modelo is not None:
            a.modelo = modelo

    async def iniciar(self, mensaje: dict) -> None:
        """Valida el contrato de control antes de abrir archivos o arrancar audio."""
        fuentes = mensaje.get("fuentes")
        prueba = mensaje.get("modo") == "asr"
        if mensaje.get("modo") not in ("llamada", "asr") or not isinstance(fuentes, dict):
            raise ValueError("Elegí modo llamada y las fuentes de ambos canales.")
        roles = {"protegida"} if prueba else set(ROLES)
        if set(fuentes) != roles or any(not isinstance(f, dict) for f in fuentes.values()):
            raise ValueError("Faltan las fuentes de protegida y otra.")
        if any(not isinstance(f.get("tipo"), str) for f in fuentes.values()):
            raise ValueError("El tipo de fuente debe ser ejemplo o cliente.")
        tipos = {r: f["tipo"] for r, f in fuentes.items()}
        if prueba and tipos != {"protegida": "navegador"}:
            raise ValueError("Probar el ASR usa solamente el micrófono del navegador.")
        if not prueba and (tipos not in ({"otra": "cliente", "protegida": "cliente"},
                          {"otra": "cliente", "protegida": "navegador"},
                          {"otra": "navegador", "protegida": "navegador"},
                          {"otra": "ejemplo", "protegida": "navegador"},
                          {"otra": "ejemplo", "protegida": "ejemplo"})):
            raise ValueError("Elegí ejemplo, cliente.py o dos fuentes del navegador.")
        audio = None
        if tipos.get("otra") == "ejemplo":
            escenario = fuentes["otra"].get("escenario")
            if (not isinstance(escenario, str) or escenario not in EJEMPLOS
                    or fuentes["otra"].get("canal") != "izq"
                    or (tipos["protegida"] == "ejemplo" and
                        (fuentes["protegida"].get("escenario") != escenario or fuentes["protegida"].get("canal") != "der"))):
                raise ValueError("Elegí un ejemplo: izquierdo otra persona, derecho protegida.")
            import soundfile as sf
            import numpy as np
            ruta = EJEMPLOS[escenario]
            if not ruta.is_file():
                raise ValueError(
                    f"Falta el audio de ejemplo {ruta.name} en {ruta.parent}. "
                    "Prepará los ejemplos desde la raíz del repositorio con "
                    "python experiments/asr-local/sintetizar_par.py, o enlazá la carpeta audio "
                    "de la copia donde ya los generaste. Para hablar, elegí micrófono, Meet o cliente.py."
                )
            try:
                audio, hz = sf.read(ruta, dtype="float32", always_2d=True)
            except (OSError, sf.LibsndfileError) as exc:
                raise ValueError(f"No se pudo leer el audio de ejemplo {ruta.name}. "
                                 "Volvé a generarlo con python experiments/asr-local/sintetizar_par.py.") from exc
            if hz != SAMPLE_RATE or audio.shape[1] != 2 or not len(audio) or not np.isfinite(audio).all():
                raise ValueError("El ejemplo debe ser estéreo a 16 kHz y contener audio válido.")
        corte, umbral = validar_corte(mensaje.get("corte_silencio_s")), mensaje.get("umbral_rms_silencio")
        asr = validar_asr(mensaje.get("asr", self.asr))
        detector_elegido = None if prueba or "detector" not in mensaje else validar_detector(mensaje["detector"])
        if prueba:
            if (isinstance(umbral, bool) or not isinstance(umbral, (int, float))
                    or not math.isfinite(umbral) or not 0 < umbral <= 1):
                raise ValueError("Elegí un umbral RMS mayor que 0 y hasta 1.")
        else:
            if umbral is not None:
                raise ValueError("El umbral de volumen de la llamada es fijo; probalo en Probar el ASR.")
            umbral = umbral_de_llamada(asr)
        async with self.control:
            if self.llamada is not None or self.clientes_audio:
                raise ValueError("Terminá la llamada actual antes de iniciar otra.")
            await self.configurar_asr((corte, umbral), asr)
            if detector_elegido is not None:
                await self.configurar_detector(detector_elegido)
            if prueba:
                historial.descartar_pruebas_no_guardadas(self.args.salida)
            self.prueba_pendiente = None
            self.config_llamada = mensaje
            self.llamada = await self.abrir_llamada()
            if audio is not None:
                self.tarea_ejemplo = asyncio.create_task(self.reproducir_ejemplo(audio, protegida=tipos["protegida"] == "ejemplo"))

    async def reiniciar_prueba(self) -> None:
        """«Borrar»: descarta lo hablado y empieza otra prueba igual sin soltar el audio del navegador.

        Todo ocurre con el candado de control tomado, así que el audio que llega mientras tanto
        espera y cae en la prueba nueva; nunca abre una llamada con la configuración por defecto.
        """
        async with self.control:
            llamada = self.llamada
            if llamada is None or self.config_llamada.get("modo") != "asr":
                raise ValueError("Borrar solo sirve durante una prueba del ASR.")
            if self.tarea_niveles:
                self.tarea_niveles.cancel()
                with suppress(asyncio.CancelledError):
                    await self.tarea_niveles
            llamada.descartar()
            llamada.reiniciar(*self.nombres_de_llamada(datetime.now()))
            self.difundir_inicio(llamada)
            self.tarea_niveles = asyncio.create_task(self.emitir_niveles(llamada))
            print(f"[prueba] borrada; sigue {llamada.llamada_id} → {llamada.dir_salida}")

    async def guardar_prueba(self, mensaje: dict) -> None:
        """«Guardar»: marca la última prueba cerrada como guardada y anota lo que se dijo en realidad."""
        async with self.control:
            carpeta = self.prueba_pendiente
            manifiesto = None if carpeta is None else historial.leer_manifiesto(carpeta)
            if self.llamada is not None or manifiesto is None:
                raise ValueError("No hay una prueba terminada para guardar.")
            referencias = historial.datos_referencia(carpeta, mensaje.get("referencia", ""),
                                                     mensaje.get("referencias_por_segmento"))
            manifiesto.update({"guardada": True, **referencias})
            historial.escribir_manifiesto(carpeta, manifiesto)
            self.prueba_pendiente = None
            self.difundir({"tipo": "prueba_guardada", "dir": str(carpeta), **referencias})

    def carpeta_en_curso(self) -> Path | None:
        return None if self.llamada is None else self.llamada.dir_salida

    async def borrar(self, mensaje: dict) -> None:
        """Borrado desde el Historial: nunca durante una llamada o prueba, y se avisa a todos los paneles."""
        async with self.control:
            if self.llamada is not None or self.clientes_audio:
                raise ValueError("No se puede borrar con una llamada o prueba en curso; terminala primero.")
            salida = Path(self.args.salida)
            if mensaje["tipo"] == "borrar_pruebas":
                ids = await asyncio.to_thread(historial.borrar_pruebas_guardadas, salida)
            else:
                ids = await asyncio.to_thread(historial.borrar, salida, mensaje.get("ids"))
            if self.prueba_pendiente is not None and self.prueba_pendiente.name in ids:
                self.prueba_pendiente = None
            # No pasa por el historial de eventos: un panel que se conecta después no necesita saberlo.
            broadcast(self.paneles, json.dumps({"tipo": "borrado", "ids": ids}))

    async def responder_historial(self, ws, mensaje: dict) -> None:
        """Lectura del Historial: la respuesta va solo al panel que preguntó; el disco se lee fuera del bucle."""
        salida, tipo = Path(self.args.salida), mensaje["tipo"]
        if tipo == "historial":
            respuesta = await asyncio.to_thread(historial.listar, salida, self.carpeta_en_curso())
            respuesta = {"tipo": "historial", **respuesta}
        elif tipo == "ver":
            respuesta = {"tipo": "detalle", **await asyncio.to_thread(historial.detalle, salida, mensaje.get("id"))}
        else:
            async with self.control:
                item = await asyncio.to_thread(historial.editar_referencia, salida, mensaje.get("id"),
                                               mensaje.get("referencia", ""), mensaje.get("referencias_por_segmento"))
            respuesta = {"tipo": "referencia_guardada", "item": item}
        await ws.send(json.dumps(respuesta, ensure_ascii=False))

    async def reproducir_ejemplo(self, audio, *, protegida: bool = True) -> None:
        """Entrega pares de bloques de 40 ms con una única marca de llegada."""
        from cliente import a_pcm16
        paso = SAMPLE_RATE * 40 // 1000
        inicio = self.ahora()
        try:
            for desde in range(0, len(audio), paso):
                hasta = min(desde + paso, len(audio))
                await self.dormir(max(0.0, inicio + hasta / SAMPLE_RATE - self.ahora()))
                llegada = self.ahora()
                self.recibir_audio("otra", a_pcm16(audio[desde:hasta, 0]), llegada=llegada)
                if protegida:
                    self.recibir_audio("protegida", a_pcm16(audio[desde:hasta, 1]), llegada=llegada)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            self.difundir({"tipo": "error", "mensaje": f"No se pudo reproducir el ejemplo: {exc}"})
        else:
            await self.cerrar_llamada()
            return
        # Un fallo de lectura/procesamiento también debe conservar lo recibido.
        await self.cerrar_llamada()

    async def atender_panel(self, ws) -> None:
        self.paneles.add(ws)
        try:
            for mensaje in self.historial:
                await ws.send(json.dumps(mensaje, ensure_ascii=False))
            async for texto in ws:
                try:
                    mensaje = json.loads(texto)
                    if not isinstance(mensaje, dict):
                        raise ValueError("El mensaje debe ser un objeto JSON.")
                    if mensaje.get("tipo") == "iniciar":
                        await self.iniciar(mensaje)
                    elif mensaje.get("tipo") == "terminar":
                        await self.cerrar_llamada()
                    elif mensaje.get("tipo") == "reiniciar_prueba":
                        await self.reiniciar_prueba()
                    elif mensaje.get("tipo") == "guardar_prueba":
                        await self.guardar_prueba(mensaje)
                    elif mensaje.get("tipo") in ("borrar", "borrar_pruebas"):
                        await self.borrar(mensaje)
                    elif mensaje.get("tipo") in ("historial", "ver", "referencia"):
                        await self.responder_historial(ws, mensaje)
                    else:
                        raise ValueError("Control desconocido: usá iniciar, terminar, reiniciar_prueba, "
                                         "guardar_prueba, historial, ver, referencia, borrar o borrar_pruebas.")
                except (ValueError, OSError, RuntimeError) as exc:
                    await ws.send(json.dumps({"tipo": "error", "mensaje": str(exc)}, ensure_ascii=False))
        finally:
            self.paneles.discard(ws)

    async def atender(self, ws) -> None:
        url = urlparse(ws.request.path)
        if url.path == "/audio":
            await self.atender_audio(ws, parse_qs(url.query).get("rol", [""])[0])
        elif url.path == "/panel":
            await self.atender_panel(ws)
        else:
            await ws.close(1008, "ruta desconocida")


def servir_panel(connection, request, args: argparse.Namespace | None = None):
    """GET / devuelve el panel; /guia la guía de Meet y WhatsApp; /detector informa el detector activo; las rutas de WebSocket siguen de largo."""
    ruta = urlparse(request.path).path
    if ruta == "/detector" and args is not None:
        cuerpo = json.dumps(info_detector(args), ensure_ascii=False).encode("utf-8")
        encabezados = Headers([("Content-Type", "application/json; charset=utf-8"),
                               ("Content-Length", str(len(cuerpo)))])
        return Response(HTTPStatus.OK, "OK", encabezados, cuerpo)
    rutas = {"/": ("panel.html", "text/html; charset=utf-8"),
             **{f"/{nombre}": (nombre, "text/javascript; charset=utf-8") for nombre in
                ("audio-navegador.mjs", "audio-worklet.mjs", "audio-pcm.mjs", "probar-asr.mjs", "fuentes.mjs", "corte-silencio.mjs", "conversacion.mjs", "historial-ui.mjs")}}
    if ruta == "/guia":
        # La guía se escribe en Markdown y se sirve como página, para leerla cómoda desde el panel.
        cuerpo = guia.a_html((DIR_VOIP / "GUIA-MEET-WHATSAPP.md").read_text(encoding="utf-8")).encode("utf-8")
        tipo = "text/html; charset=utf-8"
    elif (archivo := rutas.get(ruta)) is None:
        return None
    else:
        nombre, tipo = archivo
        cuerpo = (DIR_VOIP / nombre).read_bytes()
    encabezados = Headers([("Content-Type", tipo), ("Content-Length", str(len(cuerpo)))])
    return Response(HTTPStatus.OK, "OK", encabezados, cuerpo)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Servidor de llamada en vivo con ASR por canal y detector.")
    p.add_argument("--host", default="0.0.0.0", help="0.0.0.0 para recibir de otras notebooks de la red")
    p.add_argument("--puerto", type=int, default=8765)
    p.add_argument("--detector", choices=("reglas", "slm", "tito-slm"), default="slm",
                   help="por defecto, la configuración congelada de #143: Gemma 4 E2B directo, sin Tito; "
                        "tito-slm (ADR 0001, en retiro) necesita --prompt v4")
    p.add_argument("--modelo", default=DETECTOR_POR_DEFECTO)
    p.add_argument("--prompt", default=PROMPT_POR_DEFECTO,
                   help="por defecto c-json-corte-riesgo, la configuración congelada de #143: C cortado tras el riesgo, "
                        "aviso con riesgo >= 0,3 y el motivo solo en el primer aviso (ADR 0006)")
    p.add_argument("--solo-otra", action=argparse.BooleanOptionalAction, default=None,
                   help="las frases de PROTEGIDA entran al contexto pero no consultan, como correr.py --solo-otra "
                        "(ADR 0007), y la consulta termina en la última línea de OTRA; por defecto, sí con --detector slm "
                        "y --hablantes rol")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--ollama-url", default=replay.cliente_ollama.URL_POR_DEFECTO,
                   help="Ollama de otra máquina (p. ej. la PC con GPU) para bajar la demora del SLM")
    p.add_argument("--disparo", choices=DISPAROS, default="turno",
                   help="turno: consulta al cerrar cada turno de OTRA (ADR 0007); final: en cada frase de los dos "
                        "lados, como antes; parcial: también con texto provisorio (menos demora, más falsas alarmas)")
    base = ReglasTurno()
    p.add_argument("--turno-palabras", type=int, default=base.palabras,
                   help="con --disparo turno: el otro lado habla en serio con al menos estas palabras…")
    p.add_argument("--turno-voz-s", type=float, default=base.voz_s,
                   help="…o con un segmento del ASR de más de estos segundos (un «ajá» no cierra el turno)")
    p.add_argument("--turno-silencio-s", type=float, default=base.silencio_s,
                   help="silencio de un canal que cierra su turno, medido con el umbral RMS del ASR")
    p.add_argument("--turno-tope-s", type=float, default=base.tope_s,
                   help="un turno de OTRA más largo consulta igual, al cerrar la frase siguiente")
    p.add_argument("--corte-silencio", type=corte_de_linea_de_comandos, default=CORTE_AUTO,
                   help="corte de silencio de las llamadas que abre cliente.py: «auto» (el del modelo, 0,8 s de respaldo) "
                        "o segundos de 0,1 a 3,0; desde el panel se elige en cada llamada")
    p.add_argument("--asr", choices=tuple(MODELOS_ASR), default=ASR_POR_DEFECTO,
                   help="modelo de ASR con el que arranca; desde el panel se elige en cada llamada")
    p.add_argument("--hilos", type=int, default=2, help="hilos del ASR por canal")
    p.add_argument("--hablantes", choices=("ab", "rol"), default="rol",
                   help="modo de hablantes que ve el SLM: rol (PROTEGIDA/OTRA) o ab (A/B según orden de habla)")
    p.add_argument("--sin-indicio", action="store_true", default=True,
                   help="omitir el bloque de indicio de Tito en el mensaje al SLM (por defecto)")
    p.add_argument("--con-indicio", dest="sin_indicio", action="store_false",
                   help="agregar el bloque de indicio de Tito, como en la configuración del ADR 0001")
    p.add_argument("--salida", default=str(DIR_VOIP / "llamadas"))
    args = p.parse_args()
    validar_configuracion(p, args)
    try:
        reglas_turno(args)
    except ValueError as exc:
        p.error(str(exc))
    return args


async def principal() -> None:
    args = parse_args()
    detector = replay.construir_detector(args.detector, modelo=args.modelo, prompt_nombre=args.prompt,
                                         hablantes=args.hablantes, seed=args.seed, ollama_url=args.ollama_url,
                                         indicio=not args.sin_indicio)
    servidor = Servidor(args, detector)
    for id_carpeta in historial.descartar_pruebas_no_guardadas(args.salida):
        print(f"[prueba] descartada por no guardada: {id_carpeta}")
    servidor.preparar()
    await servidor.preparada
    async with serve(servidor.atender, args.host, args.puerto,
                     process_request=lambda conn, req: servir_panel(conn, req, args),
                     max_size=2**20, ping_interval=None):
        print(f"Panel: http://localhost:{args.puerto}/  ·  audio: ws://<esta-ip>:{args.puerto}/audio?rol=protegida|otra")
        # Ctrl+C o kill: se cierra la llamada en curso y se guarda lo grabado.
        parar = asyncio.Event()
        for senal in (signal.SIGINT, signal.SIGTERM):
            asyncio.get_running_loop().add_signal_handler(senal, parar.set)
        await parar.wait()
        await servidor.cerrar_llamada()


if __name__ == "__main__":
    sys.stdout.reconfigure(line_buffering=True)
    asyncio.run(principal())
