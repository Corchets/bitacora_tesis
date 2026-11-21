#!/usr/bin/env python3
"""Medí la llamada TTS de #77 sin panel, red de audio ni WAV de salida."""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from servidor import DIR_MODELO, EJEMPLOS, PROMPT_POR_DEFECTO, Servidor, replay, validar_configuracion
from llamada import DIR_VOIP
from motores import MotorSherpaZipformer

ESCENARIO = "SC-WA-CODE-01"
# Referencia del TTS documentada en README §4; no es T_R anotado de corpus real.
FIN_PEDIDO_S = 17.6


class Medicion(Servidor):
    """Usa la fuente y entrada de #77; al terminar espera la evaluación en curso."""

    def __init__(self, args, *resto, **kwargs):
        args.asr = "zipformer"  # el motor de crear_motor: que el manifiesto y el umbral digan el que se usa
        super().__init__(args, *resto, **kwargs)
        self.carpeta: Path | None = None

    def crear_motor(self):
        return MotorSherpaZipformer(str(self.args.modelo_asr), hilos=self.args.hilos)

    def difundir(self, mensaje):
        if mensaje["tipo"] == "error":
            raise RuntimeError(mensaje["mensaje"])

    def manifiesto_extra(self):
        extra = super().manifiesto_extra()
        # replay.info_codigo() solo mira su carpeta; acá también se ejecutan VoIP y ASR.
        try:
            estado = subprocess.run(
                ["git", "status", "--porcelain", "--", ".", "../asr-local", "../replay",
                 "../slm-directo", ":(exclude)corridas"],
                cwd=DIR_VOIP, capture_output=True, text=True, timeout=10, check=True,
            )
            extra["codigo"]["cambios_sin_commit"] = bool(estado.stdout.strip())
        except (OSError, subprocess.SubprocessError):
            extra["codigo"]["cambios_sin_commit"] = None
        return extra

    async def cerrar_llamada(self, *, esperada=None):
        llamada = self.llamada
        if llamada is None:
            return
        for act in llamada.vaciar_audio():
            if llamada.marcar_disparo(act):
                self.novedad.set()
        self.audio_terminado = True
        self.novedad.set()
        if self.tarea_detector:
            await self.tarea_detector
        self.carpeta = llamada.dir_salida
        llamada.cerrar({**self.manifiesto_extra(), "medicion": {
            "escenario": ESCENARIO, "split": "ejemplo TTS; fuera de corpus_v2",
            "fin_pedido_s": FIN_PEDIDO_S, "criterio_mediana_s": 2.0,
            "audio_sha256": hashlib.sha256(EJEMPLOS[ESCENARIO].read_bytes()).hexdigest(),
            "ollama": getattr(self, "meta_ollama", None),
        }}, guardar_audio=False)
        self.llamada = None

    async def correr(self):
        fuentes = {r: {"tipo": "ejemplo", "escenario": ESCENARIO, "canal": c}
                   for r, c in (("otra", "izq"), ("protegida", "der"))}
        try:
            await self.iniciar({"modo": "llamada", "fuentes": fuentes, "corte_silencio_s": "auto"})
            await self.tarea_ejemplo
        finally:
            await self.cerrar_llamada()
        return self.carpeta


def resumir(manifiesto: dict) -> str:
    d = manifiesto["detector"]
    tiempos = d["segundos_detector"]
    mediana = None if tiempos is None else tiempos["mediana"]
    cumple = mediana is not None and mediana < 2 and not d["fallos"]
    criterio = "CUMPLE" if cumple else "NO CUMPLE"
    duracion = "sin mediciones" if mediana is None else f"{mediana:.3f} s".replace(".", ",")
    aviso = d["aviso"]
    if aviso is None:
        momento = "sin aviso"
    else:
        diferencia = aviso["t_a"] - manifiesto["medicion"]["fin_pedido_s"]
        momento = f"aviso a {aviso['t_a']:.3f} s ({diferencia:+.3f} s respecto del fin del pedido)"
    return (f"{criterio} (< 2 s/evaluación): mediana {duracion} · evaluaciones: {d['evaluaciones']} · "
            f"salteadas: {d['actualizaciones_salteadas']} · fallos: {d['fallos']} · {momento}")


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Medí SC-WA-CODE-01 en tiempo real, sin panel ni WAV de salida.")
    p.add_argument("--detector", choices=("reglas", "slm", "tito-slm"), default="slm",
                   help="por defecto, la configuración congelada de #143, como servidor.py")
    p.add_argument("--modelo", default="gemma4:e2b-it-q4_K_M")
    p.add_argument("--prompt", default=PROMPT_POR_DEFECTO, help="como en servidor.py; tito-slm necesita --prompt v4")
    p.add_argument("--solo-otra", action=argparse.BooleanOptionalAction, default=None,
                   help="como en servidor.py: por defecto, sí con --detector slm y --hablantes rol")
    p.add_argument("--audio", type=Path, default=EJEMPLOS[ESCENARIO], help="WAV TTS original estéreo a 16 kHz")
    p.add_argument("--modelo-asr", type=Path, default=DIR_MODELO, help="directorio local de Zipformer")
    p.add_argument("--salida", type=Path, default=DIR_VOIP / "corridas")
    p.add_argument("--hablantes", choices=("ab", "rol"), default="rol",
                   help="modo de hablantes que ve el SLM: rol (PROTEGIDA/OTRA) o ab (A/B)")
    p.add_argument("--sin-indicio", action="store_true", default=True,
                   help="omitir el bloque de indicio de Tito en el mensaje al SLM (por defecto)")
    p.add_argument("--con-indicio", dest="sin_indicio", action="store_false",
                   help="agregar el bloque de indicio de Tito, como en la configuración del ADR 0001")
    args = p.parse_args(argv)
    # Protocolo de #77 (disparo en cada frase final, Zipformer); el detector es el de servidor.py.
    args.seed, args.ollama_url = 42, replay.cliente_ollama.URL_POR_DEFECTO
    validar_configuracion(p, args)
    args.disparo, args.corte_silencio, args.hilos = "final", "auto", 2
    return args


async def principal(args):
    if not args.audio.is_file():
        raise ValueError(f"Falta el ejemplo local: {args.audio}. Copiá el TTS de SC-WA-CODE-01 o indicá --audio.")
    archivos = MotorSherpaZipformer.ARCHIVOS_REQUERIDOS
    if not all((args.modelo_asr / nombre).is_file() for nombre in archivos):
        raise ValueError(f"Falta Zipformer local en {args.modelo_asr}. Indicá --modelo-asr con sus ONNX y tokens.txt.")
    EJEMPLOS[ESCENARIO] = args.audio
    meta_ollama = None
    if args.detector in ("slm", "tito-slm"):
        print(f"Preparando Ollama local y {args.modelo}…", flush=True)
        meta_ollama = replay.correr.preparar_ollama(replay.cliente_ollama.ClienteOllama(), [args.modelo])
    detector = replay.construir_detector(args.detector, modelo=args.modelo, prompt_nombre=args.prompt,
                                         hablantes=args.hablantes, seed=args.seed, ollama_url=args.ollama_url,
                                         indicio=not args.sin_indicio)
    medicion = Medicion(args, detector)
    medicion.meta_ollama = meta_ollama
    print("Reproduciendo SC-WA-CODE-01 al ritmo real (~22 s); al final espero el detector…", flush=True)
    carpeta = await medicion.correr()
    manifiesto = json.loads((carpeta / "manifiesto.json").read_text())
    print(resumir(manifiesto))
    print(f"Corrida sin WAV: {carpeta}")
    return 1 if manifiesto["detector"]["fallos"] or not manifiesto["detector"]["evaluaciones"] else 0


if __name__ == "__main__":
    try:
        sys.exit(asyncio.run(principal(parse_args())))
    except (OSError, ValueError, RuntimeError, replay.correr.FalloAlCalentar) as exc:
        sys.exit(f"No pude medir: {exc}")
    except KeyboardInterrupt:
        sys.exit("Medición interrumpida; volvé a correr el comando para una medición completa.")
