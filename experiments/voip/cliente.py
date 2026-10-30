#!/usr/bin/env python3
"""Manda el audio de UNA persona al servidor de la llamada en vivo (frente 1, spike).

Dos fuentes:
- micrófono (o cualquier entrada, p. ej. BlackHole para tomar lo que sale de la app de
  llamada en la misma notebook);
- un canal de un WAV, al ritmo real: sirve para probar sin personas y como plan B
  (replay estéreo en tiempo real con el mismo panel).

Manda PCM 16 bits mono a 16 kHz en bloques chicos: el bloque es la demora mínima que
agrega la captura.

Uso:
    python cliente.py --listar
    python cliente.py --servidor ws://192.168.0.10:8765 --rol protegida
    python cliente.py --servidor ws://192.168.0.10:8765 --rol otra --dispositivo BlackHole
    python cliente.py --rol otra --wav llamada-estereo.wav --canal der

> Estado: propuesta sin discutir.
"""

from __future__ import annotations

import argparse
import asyncio
import signal
import sys
import time

import numpy as np
from websockets.asyncio.client import connect

SAMPLE_RATE = 16000


def a_pcm16(muestras: np.ndarray) -> bytes:
    return (np.clip(muestras, -1.0, 1.0) * 32767).astype("<i2").tobytes()


def remuestrear(muestras: np.ndarray, desde_hz: int) -> np.ndarray:
    """Interpolación lineal a 16 kHz: alcanza para voz y no agrega dependencias."""
    if desde_hz == SAMPLE_RATE:
        return muestras
    n = int(round(len(muestras) * SAMPLE_RATE / desde_hz))
    return np.interp(np.linspace(0, len(muestras) - 1, n), np.arange(len(muestras)), muestras).astype(np.float32)


async def mandar_microfono(ws, dispositivo: str | int | None, bloque_ms: int) -> None:
    import sounddevice as sd

    loop = asyncio.get_running_loop()
    cola: asyncio.Queue[bytes] = asyncio.Queue()
    info = sd.query_devices(dispositivo, "input")
    # Se captura a la frecuencia nativa del dispositivo y se baja a 16 kHz acá: no todos aceptan 16 kHz.
    nativo = int(info["default_samplerate"])
    print(f"Capturando de «{info['name']}» a {nativo} Hz, bloques de {bloque_ms} ms")

    def al_capturar(indata, frames, tiempo, estado):
        if estado:
            print(f"[captura] {estado}")
        pcm = a_pcm16(remuestrear(indata[:, 0].copy(), nativo))
        loop.call_soon_threadsafe(cola.put_nowait, pcm)

    entrada = sd.InputStream(device=dispositivo, channels=1, samplerate=nativo, dtype="float32",
                             blocksize=int(nativo * bloque_ms / 1000), latency="low", callback=al_capturar)
    entrada.start()
    try:
        while True:
            await ws.send(await cola.get())
    finally:
        # abort y no stop: en macOS, stop puede trabarse esperando al callback de PortAudio.
        entrada.abort(ignore_errors=True)
        entrada.close(ignore_errors=True)


async def mandar_wav(ws, ruta: str, canal: str, bloque_ms: int) -> None:
    import soundfile as sf

    audio, hz = sf.read(ruta, dtype="float32", always_2d=True)
    columna = {"izq": 0, "der": 1, "mono": None}[canal]
    muestras = audio.mean(axis=1) if columna is None else audio[:, columna]
    muestras = remuestrear(muestras, hz)
    paso = int(SAMPLE_RATE * bloque_ms / 1000)
    inicio = time.monotonic()
    print(f"Mandando {ruta} (canal {canal}, {len(muestras) / SAMPLE_RATE:.1f} s) al ritmo real")
    for i, desde in enumerate(range(0, len(muestras), paso)):
        # Cada bloque sale cuando terminaría de grabarse en una llamada de verdad.
        espera = inicio + (i + 1) * bloque_ms / 1000 - time.monotonic()
        if espera > 0:
            await asyncio.sleep(espera)
        await ws.send(a_pcm16(muestras[desde : desde + paso]))


async def principal(args: argparse.Namespace) -> None:
    url = f"{args.servidor.rstrip('/')}/audio?rol={args.rol}"
    async with connect(url, max_size=2**20, ping_interval=None) as ws:
        print(f"Conectado a {url}")
        if args.wav:
            envio = mandar_wav(ws, args.wav, args.canal, args.bloque_ms)
        else:
            dispositivo = int(args.dispositivo) if args.dispositivo and args.dispositivo.isdigit() else args.dispositivo
            envio = mandar_microfono(ws, dispositivo, args.bloque_ms)
        # Ctrl+C o kill cortan el envío y cierran la conexión: para el servidor, esta persona colgó.
        tarea = asyncio.create_task(envio)
        for senal in (signal.SIGINT, signal.SIGTERM):
            asyncio.get_running_loop().add_signal_handler(senal, tarea.cancel)
        try:
            await tarea
        except asyncio.CancelledError:
            pass


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Manda el micrófono o un canal de WAV al servidor de la llamada.")
    p.add_argument("--servidor", default="ws://localhost:8765")
    p.add_argument("--rol", choices=("protegida", "otra"))
    p.add_argument("--dispositivo", help="nombre (o parte) o número de la entrada; ver --listar")
    p.add_argument("--wav", help="en vez del micrófono, manda este archivo al ritmo real")
    p.add_argument("--canal", choices=("izq", "der", "mono"), default="mono", help="canal del WAV a mandar")
    p.add_argument("--bloque-ms", type=int, default=40)
    p.add_argument("--listar", action="store_true", help="lista las entradas de audio y sale")
    args = p.parse_args()
    if not args.listar and not args.rol:
        p.error("falta --rol (protegida u otra)")
    return args


if __name__ == "__main__":
    args = parse_args()
    if args.listar:
        import sounddevice as sd

        print(sd.query_devices())
    else:
        sys.stdout.reconfigure(line_buffering=True)
        asyncio.run(principal(args))
