#!/usr/bin/env python3
"""Servidor de la llamada en vivo: ASR por canal, detector y panel (frente 1, spike).

Cada persona corre `cliente.py`, que manda su micrófono (o un canal de un WAV) por
WebSocket. El servidor transcribe cada canal con su propio Zipformer streaming, escribe
`actualizaciones.jsonl` con el contrato de experiments/asr-local (la llamada se puede
volver a correr con replay.py), llama al detector y muestra todo en un panel web.

El detector evalúa siempre la foto más reciente: si llega texto mientras evalúa, la
siguiente evaluación toma lo último disponible y las intermedias se saltean. Así la
demora no crece con la cola, a diferencia del replay, que evalúa todas en orden.

Uso:
    python servidor.py --detector reglas
    python servidor.py --detector slm --modelo qwen3.5:0.8b-q8_0
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

import historial
from llamada import DIR_VOIP, ROLES, SAMPLE_RATE, Llamada

import replay  # noqa: E402  (rutas de slm-directo y replay ya agregadas por llamada.py)
from motores import MotorSherpaZipformer

DIR_MODELO = DIR_VOIP.parent / "asr-local" / "modelos" / "sherpa-onnx-streaming-zipformer-es-kroko-2025-08-06"

EJEMPLOS = {nombre: DIR_VOIP.parent / "asr-local" / "audio" / f"{nombre}-tts-estereo.wav"
            for nombre in ("SC-WA-CODE-01", "LG-WA-CONSULTA-01")}


CORTE_AUTO = "auto"
CORTE_RESPALDO_S = 0.8  # corte del motor cuando el corte es «auto» y el modelo no cierra la frase solo
CORTE_MIN_S, CORTE_MAX_S = 0.1, 3.0
UMBRAL_LLAMADA = 0.005
LARGO_MAXIMO_REFERENCIA = 2000


def validar_corte(valor) -> str | float:
    """«auto» o un número de 0,1 a 3,0 s con un decimal; todo lo demás se rechaza."""
    if valor == CORTE_AUTO and isinstance(valor, str):
        return CORTE_AUTO
    if (isinstance(valor, bool) or not isinstance(valor, (int, float)) or not math.isfinite(valor)
            or not CORTE_MIN_S <= valor <= CORTE_MAX_S or abs(valor * 10 - round(valor * 10)) > 1e-9):
        raise ValueError("El corte de silencio debe ser «auto» o un número de 0,1 a 3,0 s con un decimal.")
    return round(float(valor), 1)


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
        self.config_asr: tuple[str | float, float] = (CORTE_AUTO, UMBRAL_LLAMADA)  # (corte elegido, umbral RMS)
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
        self.tarea_niveles: asyncio.Task | None = None
        # Última prueba cerrada y todavía sin guardar: «Guardar» actúa sobre ella.
        self.prueba_pendiente: Path | None = None

    def crear_motor(self) -> MotorSherpaZipformer:
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
            asyncio.to_thread(Llamada, crear_motor=crear_configurado, disparo=self.args.disparo, ahora=self.ahora)
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
                       "detector": {"tipo": self.args.detector,
                                    "modelo": self.args.modelo if self.args.detector == "slm" else None},
                       "corte_silencio_s": self.config_asr[0], "umbral_rms_silencio": self.config_asr[1]})

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
            if self.tarea_detector:
                self.tarea_detector.cancel()
                with suppress(asyncio.CancelledError):
                    await self.tarea_detector
                self.tarea_detector = None
            clientes = tuple(self.clientes_audio)
            self.clientes_audio.clear()
            for ws in clientes:
                await ws.close(1000, "llamada terminada")
            for act in llamada.cerrar(self.manifiesto_extra()):
                self.difundir({**act, "tipo": "asr", "entrega": act["tipo"]})
            self.prueba_pendiente = llamada.dir_salida if self.config_llamada.get("modo") == "asr" else None
            self.difundir({"tipo": "fin", "llamada_id": llamada.llamada_id, "dir": str(llamada.dir_salida)})
            print(f"[llamada] cerrada: {llamada.dir_salida}")
            self.preparar()

    def manifiesto_extra(self) -> dict:
        a = self.args
        carga = getattr(self.detector, "carga", None)
        return {
            "config": {"detector": None if self.config_llamada.get("modo") == "asr" else a.detector, "modelo": a.modelo if a.detector == "slm" else None,
                       "prompt": a.prompt if a.detector == "slm" else None, "hablantes": "ab",
                       "ollama_url": a.ollama_url if a.detector == "slm" else None,
                       "seed": a.seed if a.detector == "slm" else "no-aplica",
                       "corte_silencio_s": self.config_asr[0], "umbral_rms_silencio": self.config_asr[1],
                       "endpoint_nativo": self.config_asr[0] == CORTE_AUTO, "hilos_asr": a.hilos, "carga_slm": carga},
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
            if llamada.aviso is not None or not foto:
                continue
            inicio = llamada.reloj()
            respuesta = await asyncio.to_thread(self.detector.evaluar, foto)
            ev = llamada.registrar_evaluacion(n, disparos, respuesta, inicio, llamada.reloj())
            self.difundir({"tipo": "detector", **llamada.evento_detector(ev)})
            if ev.aviso:
                print(f"[AVISO] t={ev.fin_s:.2f}s · {respuesta.motivo}")

    def recibir_audio(self, rol: str, pcm: bytes, *, llegada: float | None = None) -> None:
        """Entrada común para cliente.py y el estéreo del ejemplo."""
        for act in self.llamada.recibir(rol, pcm, llegada=llegada):
            self.difundir({**act, "tipo": "asr", "entrega": act["tipo"]})
            if self.config_llamada.get("modo") != "asr" and self.llamada.marcar_disparo(act):
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
                if not isinstance(mensaje, bytes):
                    continue
                async with self.control:
                    if ws not in self.clientes_audio:
                        break
                    if self.llamada is None:
                        self.config_llamada = {}
                        await self.configurar_asr((validar_corte(self.args.corte_silencio), UMBRAL_LLAMADA))
                        self.llamada = await self.abrir_llamada()
                    self.recibir_audio(rol, mensaje)
        finally:
            pertenecia = ws in self.clientes_audio
            llamada = self.llamada
            self.clientes_audio.discard(ws)
            print(f"[audio] desconectado: {rol}")
            if pertenecia and not self.clientes_audio and self.tarea_ejemplo is None:
                await self.cerrar_llamada(esperada=llamada)

    async def configurar_asr(self, config: tuple[str | float, float]) -> None:
        if config == self.config_asr:
            return
        if self.preparada is not None:
            with suppress(ValueError, OSError, RuntimeError):
                await self.preparada
        self.config_asr = config
        self.preparar()

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
            audio, hz = sf.read(EJEMPLOS[escenario], dtype="float32", always_2d=True)
            if hz != SAMPLE_RATE or audio.shape[1] != 2 or not len(audio) or not np.isfinite(audio).all():
                raise ValueError("El ejemplo debe ser estéreo a 16 kHz y contener audio válido.")
        corte, umbral = validar_corte(mensaje.get("corte_silencio_s")), mensaje.get("umbral_rms_silencio")
        if prueba:
            if (isinstance(umbral, bool) or not isinstance(umbral, (int, float))
                    or not math.isfinite(umbral) or not 0 < umbral <= 1):
                raise ValueError("Elegí un umbral RMS mayor que 0 y hasta 1.")
        else:
            if umbral is not None:
                raise ValueError("El umbral de volumen de la llamada es fijo; probalo en Probar el ASR.")
            umbral = UMBRAL_LLAMADA
        async with self.control:
            if self.llamada is not None or self.clientes_audio:
                raise ValueError("Terminá la llamada actual antes de iniciar otra.")
            await self.configurar_asr((corte, umbral))
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
        referencia = mensaje.get("referencia", "")
        if not isinstance(referencia, str) or len(referencia) > LARGO_MAXIMO_REFERENCIA:
            raise ValueError(f"«Lo que dije en realidad» debe ser texto de hasta {LARGO_MAXIMO_REFERENCIA} caracteres.")
        async with self.control:
            carpeta = self.prueba_pendiente
            manifiesto = None if carpeta is None else historial.leer_manifiesto(carpeta)
            if self.llamada is not None or manifiesto is None:
                raise ValueError("No hay una prueba terminada para guardar.")
            manifiesto.update({"guardada": True, "referencia": referencia.strip()})
            temporal = carpeta / "manifiesto.json.tmp"
            temporal.write_text(json.dumps(manifiesto, ensure_ascii=False, indent=2), encoding="utf-8")
            temporal.replace(carpeta / "manifiesto.json")
            self.prueba_pendiente = None
            self.difundir({"tipo": "prueba_guardada", "dir": str(carpeta), "referencia": manifiesto["referencia"]})

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
                    else:
                        raise ValueError("Control desconocido: usá iniciar, terminar, reiniciar_prueba o guardar_prueba.")
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
        cuerpo = json.dumps({"tipo": args.detector,
                             "modelo": getattr(args, "modelo", None) if args.detector == "slm" else None},
                            ensure_ascii=False).encode("utf-8")
        encabezados = Headers([("Content-Type", "application/json; charset=utf-8"),
                               ("Content-Length", str(len(cuerpo)))])
        return Response(HTTPStatus.OK, "OK", encabezados, cuerpo)
    rutas = {"/": ("panel.html", "text/html; charset=utf-8"),
             "/guia": ("GUIA-MEET-WHATSAPP.md", "text/plain; charset=utf-8"),
             **{f"/{nombre}": (nombre, "text/javascript; charset=utf-8") for nombre in
                ("audio-navegador.mjs", "audio-worklet.mjs", "audio-pcm.mjs", "probar-asr.mjs", "fuentes.mjs", "corte-silencio.mjs")}}
    archivo = rutas.get(ruta)
    if archivo is None:
        return None
    nombre, tipo = archivo
    cuerpo = (DIR_VOIP / nombre).read_bytes()
    encabezados = Headers([("Content-Type", tipo), ("Content-Length", str(len(cuerpo)))])
    return Response(HTTPStatus.OK, "OK", encabezados, cuerpo)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Servidor de llamada en vivo con ASR por canal y detector.")
    p.add_argument("--host", default="0.0.0.0", help="0.0.0.0 para recibir de otras notebooks de la red")
    p.add_argument("--puerto", type=int, default=8765)
    p.add_argument("--detector", choices=("reglas", "slm"), required=True)
    p.add_argument("--modelo", default="qwen3.5:0.8b-q8_0")
    p.add_argument("--prompt", default="tarea")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--ollama-url", default=replay.cliente_ollama.URL_POR_DEFECTO,
                   help="Ollama de otra máquina (p. ej. la PC con GPU) para bajar la demora del SLM")
    p.add_argument("--disparo", choices=("final", "parcial"), default="final",
                   help="final: evalúa al cerrar cada frase; parcial: también con texto provisorio (menos demora, más falsas alarmas)")
    p.add_argument("--corte-silencio", type=corte_de_linea_de_comandos, default=CORTE_AUTO,
                   help="corte de silencio de las llamadas que abre cliente.py: «auto» (el del modelo, 0,8 s de respaldo) "
                        "o segundos de 0,1 a 3,0; desde el panel se elige en cada llamada")
    p.add_argument("--hilos", type=int, default=2, help="hilos del ASR por canal")
    p.add_argument("--salida", default=str(DIR_VOIP / "llamadas"))
    return p.parse_args()


async def principal() -> None:
    args = parse_args()
    detector = replay.construir_detector(args.detector, modelo=args.modelo, prompt_nombre=args.prompt,
                                         hablantes="ab", seed=args.seed, ollama_url=args.ollama_url)
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
