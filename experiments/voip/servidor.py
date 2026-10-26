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

Una llamada empieza con el primer bloque de audio y termina cuando se desconectan todos
los clientes de audio (o con Ctrl+C). Cada llamada queda en llamadas/<fecha>_<hora>/.

> Estado: propuesta sin discutir. No cierra D08 ni D09.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import signal
import sys
from datetime import datetime
from http import HTTPStatus
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from websockets.asyncio.server import broadcast, serve
from websockets.datastructures import Headers
from websockets.http11 import Response

from llamada import DIR_VOIP, ROLES, Llamada

import replay  # noqa: E402  (rutas de slm-directo y replay ya agregadas por llamada.py)
from motores import MotorSherpaZipformer

DIR_MODELO = DIR_VOIP.parent / "asr-local" / "modelos" / "sherpa-onnx-streaming-zipformer-es-kroko-2025-08-06"


class Servidor:
    def __init__(self, args: argparse.Namespace, detector) -> None:
        self.args = args
        self.detector = detector
        self.llamada: Llamada | None = None
        # La próxima llamada se prepara de antemano: cargar los dos ASR tarda ~1 s y, si se
        # hiciera con el primer bloque, atrasaría ese canal respecto del otro.
        self.preparada: asyncio.Task | None = None
        self.clientes_audio = 0
        self.paneles: set = set()
        self.historial: list[dict] = []  # para el panel que se conecta en medio de la llamada
        self.novedad = asyncio.Event()
        self.tarea_detector: asyncio.Task | None = None

    def crear_motor(self) -> MotorSherpaZipformer:
        modelo = str(DIR_MODELO) if DIR_MODELO.exists() else MotorSherpaZipformer.MODELO_POR_DEFECTO
        motor = MotorSherpaZipformer(modelo, hilos=self.args.hilos)
        motor.corte_silencio_s = self.args.corte_silencio
        return motor

    def difundir(self, mensaje: dict) -> None:
        self.historial.append(mensaje)
        broadcast(self.paneles, json.dumps(mensaje, ensure_ascii=False))

    def preparar(self) -> None:
        self.preparada = asyncio.create_task(
            asyncio.to_thread(Llamada, crear_motor=self.crear_motor, disparo=self.args.disparo)
        )

    async def abrir_llamada(self) -> Llamada:
        llamada = await self.preparada
        momento = datetime.now()
        llamada.abrir(f"VIVO-{momento:%Y%m%d-%H%M%S}", Path(self.args.salida) / f"{momento:%Y-%m-%d_%H%M%S}")
        self.historial = []
        self.difundir({"tipo": "inicio", "llamada_id": llamada.llamada_id})
        self.tarea_detector = asyncio.create_task(self.trabajar_detector(llamada))
        print(f"[llamada] {llamada.llamada_id} → {llamada.dir_salida}")
        return llamada

    async def cerrar_llamada(self) -> None:
        llamada, self.llamada = self.llamada, None
        if llamada is None:
            return
        if self.tarea_detector:
            self.tarea_detector.cancel()
        for act in llamada.cerrar(self.manifiesto_extra()):
            self.difundir({"tipo": "asr", **act})
        self.difundir({"tipo": "fin", "llamada_id": llamada.llamada_id, "dir": str(llamada.dir_salida)})
        print(f"[llamada] cerrada: {llamada.dir_salida}")
        self.preparar()

    def manifiesto_extra(self) -> dict:
        a = self.args
        carga = getattr(self.detector, "carga", None)
        return {
            "config": {"detector": a.detector, "modelo": a.modelo if a.detector == "slm" else None,
                       "prompt": a.prompt if a.detector == "slm" else None, "hablantes": "ab",
                       "ollama_url": a.ollama_url if a.detector == "slm" else None,
                       "seed": a.seed if a.detector == "slm" else "no-aplica",
                       "corte_silencio_s": a.corte_silencio, "hilos_asr": a.hilos, "carga_slm": carga},
            "codigo": replay.info_codigo(),
            "maquina": replay.info_maquina(),
        }

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

    async def atender_audio(self, ws, rol: str) -> None:
        if rol not in ROLES:
            await ws.close(1008, f"rol debe ser uno de {ROLES}")
            return
        self.clientes_audio += 1
        print(f"[audio] conectado: {rol} ({ws.remote_address[0]})")
        try:
            async for mensaje in ws:
                if not isinstance(mensaje, bytes):
                    continue
                if self.llamada is None:
                    self.llamada = await self.abrir_llamada()
                for act in self.llamada.recibir(rol, mensaje):
                    self.difundir({"tipo": "asr", **act})
                    if self.llamada.marcar_disparo(act):
                        self.novedad.set()
        finally:
            self.clientes_audio -= 1
            print(f"[audio] desconectado: {rol}")
            if self.clientes_audio == 0:
                await self.cerrar_llamada()

    async def atender_panel(self, ws) -> None:
        self.paneles.add(ws)
        try:
            for mensaje in self.historial:
                await ws.send(json.dumps(mensaje, ensure_ascii=False))
            await ws.wait_closed()
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


def servir_panel(connection, request):
    """GET / devuelve el panel; las rutas de WebSocket siguen de largo."""
    if urlparse(request.path).path != "/":
        return None
    cuerpo = (DIR_VOIP / "panel.html").read_bytes()
    encabezados = Headers([("Content-Type", "text/html; charset=utf-8"), ("Content-Length", str(len(cuerpo)))])
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
    p.add_argument("--corte-silencio", type=float, default=0.8,
                   help="segundos de silencio que cierran una frase (menos = aviso antes, frases más cortadas)")
    p.add_argument("--hilos", type=int, default=2, help="hilos del ASR por canal")
    p.add_argument("--salida", default=str(DIR_VOIP / "llamadas"))
    return p.parse_args()


async def principal() -> None:
    args = parse_args()
    detector = replay.construir_detector(args.detector, modelo=args.modelo, prompt_nombre=args.prompt,
                                         hablantes="ab", seed=args.seed, ollama_url=args.ollama_url)
    servidor = Servidor(args, detector)
    servidor.preparar()
    await servidor.preparada
    async with serve(servidor.atender, args.host, args.puerto, process_request=servir_panel,
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
