"""Corrida pareada de #174. Solo biblioteca estándar y código del laboratorio."""
import argparse
from collections import Counter
import csv
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import shlex
import subprocess
import sys
import urllib.error
import urllib.request

AQUI = Path(__file__).resolve().parent
SLM = AQUI.parents[1]
REPO = SLM.parents[1]
sys.path.insert(0, str(SLM))
from casos import Linea, cargar_referencia  # noqa: E402
from detectores import DetectorSLMCorteRiesgo, cargar_prompt, esquema_de  # noqa: E402

MATEO = AQUI.parent / "2026-11-21_solo-el-numero"
CONVERSACIONES = MATEO / "conversaciones-desarrollo-150.json"
SUBCONJUNTO = AQUI.parent / "2026-11-11_a56-latencia-172" / "conversaciones-sub-6.json"
BASE = MATEO / "d150-numero" / "turnos.jsonl"
PROMPT = "c-consejos-corte-riesgo"
MODELO = "google/gemini-3.8-flash"
API = "https://openrouter.ai/api/v1"
TOPE = 2
MAX_TOKENS = 336
PRECIO_ENTRADA = 0.000000375
PRECIO_SALIDA = 0.000001875
TERMINALES = {"completed", "failed", "cancelled", "expired"}


def leer(ruta):
    return json.loads(ruta.read_text(encoding="utf-8"))


def guardar(ruta, datos):
    temporal = ruta.with_suffix(".tmp")
    temporal.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporal.replace(ruta)


def pedidos():
    datos = CONVERSACIONES.read_bytes()
    prompt = cargar_prompt(PROMPT)
    manifiesto = leer(BASE.with_name("manifiesto.json"))
    if hashlib.sha256(datos).hexdigest() != manifiesto["conversaciones_sha256"]:
        raise ValueError("Las conversaciones difieren de las que usó Gemma.")
    if hashlib.sha256(prompt.encode()).hexdigest() != manifiesto["prompt_sha256"]:
        raise ValueError("El prompt difiere del que usó Gemma.")
    conversaciones = json.loads(datos)["casos"]
    piloto = leer(SUBCONJUNTO)["casos"]
    if not piloto.keys() <= conversaciones.keys() or len(piloto) != 6 or len(conversaciones) != 150:
        raise ValueError("El piloto debe ser el subconjunto de seis de desarrollo-150")
    esquema = esquema_de(PROMPT)
    detector = DetectorSLMCorteRiesgo(None, MODELO, prompt, "rol", 4096, 42, esquema=esquema)
    lotes = {"piloto": [], "resto": []}
    for caso, lineas in conversaciones.items():
        if "-T-" in caso:
            raise ValueError(f"Caso de la reserva en desarrollo: {caso}")
        prefijo = []
        destino = lotes["piloto" if caso in piloto else "resto"]
        for fila in lineas:
            prefijo.append(Linea(fila["hablante"], fila["texto"]))
            if fila["hablante"] != "OTRA":
                continue
            mensajes, error = detector.mensajes(prefijo)
            if error:
                raise ValueError(f"{caso}/{fila['n']}: {error}")
            destino.append({
                "custom_id": f"{caso}:{fila['n']}",
                "body": {
                    "messages": mensajes, "max_tokens": MAX_TOKENS, "seed": 42,
                    "reasoning": {"effort": "low", "exclude": True},
                    "response_format": {"type": "json_schema", "json_schema": {
                        "name": "evaluacion", "strict": True,
                        "schema": {**esquema, "additionalProperties": False},
                    }},
                },
            })
    base = []
    for linea in BASE.read_text(encoding="utf-8").splitlines():
        fila = json.loads(linea)
        if fila["consulta"] == "slm" and fila["valida"]:
            base.append(f"{fila['case_id']}:{fila['linea']}")
    ids = [p["custom_id"] for lote in lotes.values() for p in lote]
    if len(base) != 1392 or len(ids) != 1392 or set(ids) != set(base) or len(lotes["piloto"]) != 83:
        raise ValueError("El lote no reproduce las consultas válidas de Gemma")
    return lotes


def estimar(lote):
    # Presupuesto sin caché: 2 bytes de texto/token, más margen de plantilla y esquema.
    entrada = sum(160 + sum(math.ceil(len(m["content"].encode()) / 2) for m in p["body"]["messages"]) for p in lote)
    return {"consultas": len(lote), "tokens_entrada_estimados": entrada,
            "usd_estimados": entrada * PRECIO_ENTRADA + len(lote) * MAX_TOKENS * PRECIO_SALIDA}


def clave():
    for linea in (REPO / ".env").read_text(encoding="utf-8").splitlines():
        nombre, _, valor = linea.partition("=")
        if nombre.strip().removeprefix("export ") == "CLAVE_OPENROUTER":
            partes = shlex.split(valor, comments=True)
            if len(partes) == 1:
                return partes[0]
    raise ValueError("Falta CLAVE_OPENROUTER en .env")


def api(path, datos=None):
    solicitud = urllib.request.Request(API + path, data=None if datos is None else json.dumps(datos).encode(),
                                      headers={"Authorization": "Bearer " + clave(), "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(solicitud, timeout=100) as respuesta:
            return json.load(respuesta)
    except urllib.error.HTTPError as error:
        raise SystemExit(f"HTTP {error.code}: {error.read(600).decode(errors='replace')}") from None


def contenido(directorio, nombre):
    return directorio / f"{nombre}-resultado.json"


def cuerpo_lote(lote):
    return {"endpoint": "/v1/chat/completions", "model": MODELO,
            "provider": {"only": ["google-vertex"], "allow_fallbacks": False}, "requests": lote}


def huella_lote(lote):
    return hashlib.sha256(json.dumps(cuerpo_lote(lote)).encode()).hexdigest()


def enviar(directorio, nombre, lotes):
    directorio.mkdir(parents=True, exist_ok=True)
    recibo = directorio / f"{nombre}-envio.json"
    if recibo.exists() or contenido(directorio, nombre).exists():
        raise SystemExit("Ya hay una constancia de envío. Consultá su estado.")
    costo = 0
    if nombre == "resto":
        previo_envio = leer(directorio / "piloto-envio.json")
        if previo_envio["payload_sha256"] != huella_lote(lotes["piloto"]):
            raise SystemExit("El pedido actual del piloto difiere del pedido enviado.")
        previo = leer(contenido(directorio, "piloto"))
        resultados = puntuaciones(previo)
        if previo["status"] != "completed" or not any(resultados.get(p["custom_id"]) is not None for p in lotes["piloto"]):
            raise SystemExit("El piloto no produjo puntajes válidos.")
        costo = float(previo["usage"]["cost"])
    elif sum(estimar(lote)["usd_estimados"] for lote in lotes.values()) > TOPE:
        raise SystemExit("La estimación para las 150 conversaciones supera el presupuesto.")
    estimado = estimar(lotes[nombre])
    disponible = api("/key")["data"]["limit_remaining"]
    requerido = estimado["usd_estimados"]
    if costo + requerido > TOPE or disponible is None or requerido > disponible:
        raise SystemExit(f"Presupuesto insuficiente: consumido {costo:.4f}, estimado {requerido:.4f}, disponible {disponible}.")
    evidencia = {
        "estimacion": estimado, "estado": "envio_iniciado", "modelo": MODELO, "proveedor_solicitado": "google-vertex",
        "max_tokens": MAX_TOKENS, "razonamiento": "low", "seed_solicitada": 42, "temperatura": "predeterminada",
        "commit_base": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip(),
        "huellas": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in
                    (CONVERSACIONES, BASE, Path(__file__), SLM / "detectores.py")},
        "payload_sha256": huella_lote(lotes[nombre]),
    }
    with recibo.open("x", encoding="utf-8") as archivo:
        json.dump(evidencia, archivo, ensure_ascii=False, indent=2)
    batch = api("/batches", cuerpo_lote(lotes[nombre]))
    guardar(recibo, {**evidencia, "id": batch["id"], "estado": batch["status"]})
    print(nombre, batch["id"], batch["status"])


def consultar(directorio, nombre):
    recibo = leer(directorio / f"{nombre}-envio.json")
    batch = api("/batches/" + recibo["id"])
    if batch["status"] in TERMINALES:
        guardar(contenido(directorio, nombre), batch)
    print(nombre, batch["status"], batch.get("request_counts"), batch.get("usage"), batch.get("error"))


def puntuaciones(batch):
    resultados = {}
    for fila in batch.get("results") or []:
        riesgo = None
        respuesta = fila.get("response") or {}
        if respuesta.get("status_code") == 200:
            try:
                choice = respuesta["body"]["choices"][0]
                if choice["finish_reason"] == "stop":
                    valor = json.loads(choice["message"]["content"])["riesgo"]
                    if type(valor) in (int, float) and 0 <= valor <= 1:
                        riesgo = valor
            except (KeyError, IndexError, TypeError, ValueError):
                pass
        resultados[fila["custom_id"]] = riesgo
    return resultados


def analizar(directorio, lotes):
    ruta_analisis = AQUI.parent / "2026-11-12_evaluacion-final" / "analizar.py"
    spec = importlib.util.spec_from_file_location("evaluacion", ruta_analisis)
    evaluacion = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(evaluacion)
    gemini = {}
    causas = {}
    ejecuciones = {}
    for nombre, lote in lotes.items():
        ruta = contenido(directorio, nombre)
        if not ruta.exists():
            continue
        batch = leer(ruta)
        gemini.update(puntuaciones(batch))
        for fila in batch.get("results") or []:
            respuesta = fila.get("response") or {}
            opciones = respuesta.get("body", {}).get("choices") or [{}]
            causas[fila["custom_id"]] = opciones[0].get("finish_reason") or "sin_respuesta"
        ejecuciones[nombre] = {
            **leer(directorio / f"{nombre}-envio.json"),
            **{k: batch.get(k) for k in ("status", "provider", "usage", "request_counts", "created_at", "completed_at", "error")},
        }
    if not ejecuciones:
        raise SystemExit("Todavía no hay resultados descargados.")

    base = {}
    gemma = {}
    for linea in BASE.read_text(encoding="utf-8").splitlines():
        fila = json.loads(linea)
        if fila["consulta"] == "slm":
            caso, n = fila["case_id"], fila["linea"]
            base[f"{caso}:{n}"] = fila["riesgo"]
            if fila["primer_aviso"]:
                gemma[caso] = n
    avisos = {}
    incompletos = set()
    invalidas = Counter()
    analizadas = set()
    with (directorio / "puntajes.csv").open("w", encoding="utf-8", newline="") as archivo:
        tabla = csv.writer(archivo, lineterminator="\n")
        tabla.writerow(["caso", "linea", "riesgo_gemma", "riesgo_gemini", "estado", "fin_gemini"])
        for nombre in ejecuciones:
            for pedido in lotes[nombre]:
                uid = pedido["custom_id"]
                caso, n = uid.split(":")
                analizadas.add(caso)
                riesgo = gemini.get(uid)
                fin = causas.get(uid, "sin_respuesta")
                tabla.writerow([caso, n, base[uid], riesgo, "valido" if riesgo is not None else "sin_puntaje", fin])
                if riesgo is None:
                    incompletos.add(caso)
                    invalidas[fin] += 1
                elif riesgo >= 0.3 and caso not in avisos:
                    avisos[caso] = int(n)

    completos = sorted(analizadas - incompletos)
    ref = {caso: cargar_referencia(caso) for caso in completos}
    g = evaluacion.exitos(gemma, completos, ref)
    m = evaluacion.exitos(avisos, completos, ref)
    guardar(directorio / "manifiesto.json", ejecuciones)
    print("# Comparación exploratoria de Gemini Batch con Gemma")
    print()
    print(f"Conversaciones completas para comparar: **{len(completos)}** de **{len(analizadas)}** enviadas.")
    consultas = sum(len(lotes[nombre]) for nombre in ejecuciones)
    print(f"Puntajes válidos: **{consultas - invalidas.total()}/{consultas}**.")
    if incompletos:
        print()
        print("Consultas sin puntaje por estado de salida: " +
              ", ".join(f"`{fin}` ({cantidad})" for fin, cantidad in invalidas.items()) + ".")
        print()
        print("Conversaciones incompletas: " + ", ".join(sorted(incompletos)) + ".")
    print()
    print("| Métrica | Gemma | Gemini | Solo Gemma | Solo Gemini |")
    print("|---|---:|---:|---:|---:|")
    for nombre in evaluacion.COMPARADAS:
        x, y = g[nombre], m[nombre]
        solo_gemma = sum(x[c] and not y[c] for c in x)
        solo_gemini = sum(y[c] and not x[c] for c in x)
        print(f"| {nombre} | {sum(x.values())}/{len(x)} | {sum(y.values())}/{len(y)} | {solo_gemma} | {solo_gemini} |")
    print()
    ambos = [c for c in completos if c in gemma and c in avisos]
    antes = sum(avisos[c] < gemma[c] for c in ambos)
    despues = sum(avisos[c] > gemma[c] for c in ambos)
    print(f"Ambos avisan en {len(ambos)} llamadas. Gemini avisa antes en {antes}, después en {despues} y "
          f"en la misma línea en {len(ambos) - antes - despues}.")
    costos = [l["usage"]["cost"] for l in ejecuciones.values() if l.get("usage")]
    if len(costos) == len(ejecuciones):
        print()
        print(f"Costo informado por OpenRouter: **USD {sum(costos):.6f}**.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("accion", choices=["plan", "enviar", "consultar", "analizar"])
    parser.add_argument("--lote", choices=["piloto", "resto"])
    parser.add_argument("--salida", type=Path, required=True)
    args = parser.parse_args()
    if args.accion in {"enviar", "consultar"} and not args.lote:
        parser.error("indicá --lote")
    if args.accion == "consultar":
        consultar(args.salida, args.lote)
        return
    lotes = pedidos()
    if args.accion == "plan":
        print(json.dumps({nombre: estimar(lote) for nombre, lote in lotes.items()}, indent=2))
    elif args.accion == "enviar":
        enviar(args.salida, args.lote, lotes)
    else:
        analizar(args.salida, lotes)


if __name__ == "__main__":
    main()
