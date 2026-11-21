"""El detector de `correr_android_latencia.py` (mismo cliente, mismo detector, misma configuración), a ritmo real.

En vez de consultar una línea detrás de otra, cada línea de OTRA se consulta a la hora en que termina en el audio más
el corte de 0,8 s: `inicio + fin_s + CORTE_S`, con `fin_s` de `agenda.json` e `inicio` la hora de reloj (segundos
Unix) en que empieza el audio, la misma que recibe el ASR. La consulta va sobre el texto original de la línea, no
sobre la transcripción. Si la consulta anterior todavía no terminó, la siguiente sale apenas termine y el retraso
queda anotado. Cada conversación empieza con el detector reiniciado.

    python3 -I ejecutar_agenda.py --inicio HORA --salida DIR_NUEVO --base http://IP:18080 --servidor "..."

Deja `turnos.jsonl` con los campos de `correr_android_latencia.py` (lo lee `resumir.py`) más `programada_s`,
`inicio_s` (segundos desde el inicio del audio) y `retraso_s` (inicio real menos programado), y `manifiesto.json`.
"""
import argparse
import dataclasses
import json
import os
import platform
import sys
import time
import urllib.request
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SLM = AQUI.parent.parent
sys.path.insert(0, str(SLM))

import correr_android_latencia as cal  # noqa: E402
from casos import Linea  # noqa: E402
from correr_android_congelada import sha  # noqa: E402
from detectores import DetectorSLMCorteRiesgo, cargar_prompt, esquema_de  # noqa: E402

CONVERSACIONES = AQUI.parent / "2026-11-11_a56-latencia-172" / "conversaciones-sub-6.json"
AGENDA = AQUI / "agenda.json"
CORTE_S = 0.8  # el corte por silencio del ASR: la línea se da por cerrada 0,8 s después de que termina


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--inicio", type=float, required=True, help="hora de reloj (s Unix) en que empieza el audio")
    p.add_argument("--salida", required=True)
    p.add_argument("--base", default=cal.BASE)
    p.add_argument("--prompt", default="c-consejos-corte-riesgo")
    p.add_argument("--servidor", default="", help="los parámetros de llama-server, para el manifiesto")
    a = p.parse_args()
    cal.BASE = a.base  # _post lee la base del módulo en cada consulta
    datos = json.loads(CONVERSACIONES.read_text(encoding="utf-8"))
    agenda = json.loads(AGENDA.read_text(encoding="utf-8"))
    assert agenda["conversaciones_sha256"] == sha(CONVERSACIONES.read_bytes())
    esquema = esquema_de(a.prompt)
    cliente = cal.Cliente("chat", esquema)
    detector = DetectorSLMCorteRiesgo(cliente, cal.MODELO, cargar_prompt(a.prompt), "rol", 4096, 42, esquema=esquema)
    calentamiento = detector.evaluar((Linea("OTRA", "Hola, ¿qué tal?"),))
    detector.reiniciar()

    destino = Path(a.salida)
    destino.mkdir(parents=True, exist_ok=False)
    with urllib.request.urlopen(a.base + "/props", timeout=30) as r:
        props = json.load(r)
    manifiesto = {
        "experimento": "iphone-15-pro-max-asr-y-detector",
        "configuracion": {"prompt": a.prompt, "modelo": cal.MODELO, "detector": type(detector).__name__,
                          "consulta": "chat", "hablantes": "rol", "solo_otra": True, "num_ctx": 4096, "seed": 42,
                          "temperatura": detector.opciones()["temperature"],
                          "num_predict": detector.opciones()["num_predict"], "umbral": detector.umbral,
                          "recorrido": "todas las líneas, sin detener al primer aviso; PROTEGIDA no consulta",
                          "ritmo": f"cada línea de OTRA a su fin en el audio + {CORTE_S} s"},
        "servidor": a.servidor, "base": a.base, "inicio_audio": a.inicio,
        "props": {k: v for k, v in props.items() if k not in ("chat_template", "default_generation_settings")},
        "casos": list(datos["casos"]),
        "conversaciones_sha256": sha(CONVERSACIONES.read_bytes()), "agenda_sha256": sha(AGENDA.read_bytes()),
        "prompt_sha256": sha(cargar_prompt(a.prompt).encode()), "motivo_sha256": sha(detector.pedido_motivo.encode()),
        "codigo_sha256": {q.name: sha(q.read_bytes()) for q in
                          [Path(__file__).resolve(), SLM / "correr_android_latencia.py",
                           SLM / "correr_android_congelada.py", SLM / "detectores.py", SLM / "casos.py"]},
        "calentamiento": {"valida": calentamiento.valida, "error": calentamiento.error, "ms": calentamiento.ms},
        "ejecutor_en": platform.platform(), "python": platform.python_version(), "pid": os.getpid(),
        "inicio": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    if time.time() > a.inicio:
        manifiesto["advertencia"] = f"el calentamiento terminó {time.time() - a.inicio:.1f} s después del inicio"
    (destino / "manifiesto.json").write_text(json.dumps(manifiesto, ensure_ascii=False, indent=2))

    tiempos = {c["caso"]: {l["n"]: l for l in c["lineas"]} for c in agenda["casos"]}
    with (destino / "turnos.jsonl").open("w", encoding="utf-8", buffering=1) as archivo:
        for caso, renglones in datos["casos"].items():
            detector.reiniciar()
            disponibles: list[Linea] = []
            aviso_en = None
            for r in renglones:
                linea = Linea(r["hablante"], r["texto"])
                disponibles.append(linea)
                fila = {"case_id": caso, "linea": r["n"], "hablante": linea.hablante}
                if linea.hablante != "OTRA":
                    fila["consulta"] = "omitida"
                else:
                    programada = tiempos[caso][r["n"]]["fin_s"] + CORTE_S
                    time.sleep(max(0.0, a.inicio + programada - time.time()))
                    inicio_s = time.time() - a.inicio
                    t0 = time.perf_counter()
                    respuesta = detector.evaluar(tuple(disponibles))
                    total_ms = (time.perf_counter() - t0) * 1000
                    fila.update(dataclasses.asdict(respuesta))
                    fila.update(total_ms=total_ms, consulta="slm", tokens_cache=cliente.ultimo_cache,
                                programada_s=round(programada, 3), inicio_s=round(inicio_s, 3),
                                retraso_s=round(inicio_s - programada, 3))
                    if aviso_en is None and respuesta.valida and respuesta.alerta_sugerida:
                        aviso_en = r["n"]
                    fila["primer_aviso"] = aviso_en == r["n"]
                archivo.write(json.dumps(fila, ensure_ascii=False) + "\n")
                print(caso, r["n"], fila["hablante"], fila.get("inicio_s"), round(fila.get("total_ms") or 0),
                      fila.get("riesgo"), flush=True)
    manifiesto["fin"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    (destino / "manifiesto.json").write_text(json.dumps(manifiesto, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
