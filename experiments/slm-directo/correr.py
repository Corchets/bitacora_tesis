"""Corre el ensayo #50: recorre cada caso línea por línea, como si la llamada estuviera
ocurriendo, y registra qué dice cada detector en cada actualización.

Ejemplos:
    python correr.py --solo-reglas
    python correr.py --modelos qwen3.5:2b
    python correr.py --modelos qwen3.5:0.8b,qwen3.5:2b,qwen3.5:4b --prompts tarea,tarea+base --hablantes ab,sin
    python correr.py --modelos qwen3.5:2b --casos SC-WA-CODE-01-e01 --detalle

Cada corrida crea corridas/<fecha>_<hora>[_<etiqueta>]/ con:
    manifiesto.json      qué se corrió: modelos, prompts, casos, código, máquina
    actualizaciones.csv  una fila por detector, caso y línea
Después: python resumen.py corridas/<carpeta>

Política del ensayo (#50): un único aviso por llamada, en la primera respuesta válida
con alerta_sugerida=true. Las respuestas posteriores se registran sin volver a avisar.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import casos
from cliente_ollama import URL_POR_DEFECTO, ClienteOllama, ErrorOllama
from detectores import HABLANTES, PROMPTS, DetectorReglas, DetectorSLM, Respuesta, cargar_prompt, huella

RAIZ = Path(__file__).resolve().parent
POLITICA = "aviso_unico_primer_true_valido"
COLUMNAS = [
    "config",
    "detector",
    "modelo",
    "prompt",
    "hablantes",
    "case_id",
    "linea",
    "hablante",
    "texto",
    "valida",
    "error",
    "riesgo",
    "alerta_sugerida",
    "aviso",
    "motivo",
    "evidencia",
    "evidencia_en_texto",
    "ms",
    "tokens_prompt",
    "tokens_salida",
    "crudo",
]


@dataclass
class Llamada:
    """Estado de UNA llamada: lo disponible hasta ahora y en qué línea se avisó.

    Se crea una nueva por caso, así que nada pasa de una llamada a la siguiente.
    """

    lineas: list[casos.Linea] = field(default_factory=list)
    aviso_en: int | None = None

    def agregar(self, linea: casos.Linea) -> tuple[casos.Linea, ...]:
        self.lineas.append(linea)
        return tuple(self.lineas)  # copia: el detector no puede ver líneas futuras

    def registrar(self, n: int, respuesta: Respuesta) -> bool:
        """True si esta respuesta produce el aviso de la llamada."""
        if self.aviso_en is None and respuesta.valida and respuesta.alerta_sugerida:
            self.aviso_en = n
            return True
        return False


def procesar_caso(detector, lineas: list[casos.Linea]):
    """Entrega las líneas de a una y devuelve (n, línea, respuesta, aviso) por actualización."""
    llamada = Llamada()
    for n, linea in enumerate(lineas, start=1):
        disponibles = llamada.agregar(linea)
        respuesta = detector.evaluar(disponibles)
        yield n, linea, respuesta, llamada.registrar(n, respuesta)


def _git(*args: str) -> str:
    try:
        return subprocess.run(
            ["git", *args], cwd=RAIZ, capture_output=True, text=True, timeout=10, check=True
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def info_codigo() -> dict:
    commit = _git("rev-parse", "HEAD") or "desconocido"
    cambios = _git("status", "--porcelain", "--", ".")
    return {"commit": commit, "cambios_sin_commit_en_la_carpeta": bool(cambios)}


def _ram_total_gb() -> float | None:
    try:
        if sys.platform.startswith("linux"):
            for renglon in Path("/proc/meminfo").read_text().splitlines():
                if renglon.startswith("MemTotal:"):
                    return round(int(renglon.split()[1]) / 1024**2, 1)
        if sys.platform == "darwin":
            salida = subprocess.run(["sysctl", "-n", "hw.memsize"], capture_output=True, text=True)
            return round(int(salida.stdout) / 1024**3, 1)
        if sys.platform == "win32":
            import ctypes

            class Estado(ctypes.Structure):
                _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong)] + [
                    (n, ctypes.c_ulonglong)
                    for n in ("total", "libre", "pag_total", "pag_libre", "virt_total", "virt_libre", "ext")
                ]

            estado = Estado()
            estado.dwLength = ctypes.sizeof(Estado)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(estado))
            return round(estado.total / 1024**3, 1)
    except Exception:
        return None
    return None


def info_maquina() -> dict:
    return {
        "sistema": platform.platform(),
        "arquitectura": platform.machine(),
        "procesador": platform.processor() or "no informado",
        "nucleos_logicos": os.cpu_count(),
        "ram_total_gb": _ram_total_gb(),
        "python": platform.python_version(),
    }


def _lista(valor: str) -> list[str]:
    """Valores separados por coma, sin vacíos ni repetidos (un repetido duplicaría filas)."""
    return list(dict.fromkeys(v.strip() for v in valor.split(",") if v.strip()))


def elegir_casos(args) -> list[str]:
    ids = casos.ids_de_casos()
    if args.casos:
        pedidos = _lista(args.casos)
        faltan = [c for c in pedidos if c not in ids]
        if faltan:
            sys.exit(f"Casos inexistentes: {faltan}")
        ids = pedidos
    if args.grupo:
        ids = [c for c in ids if casos.cargar_referencia(c)["grupo"] == args.grupo]
    if not ids:
        sys.exit("No hay casos para correr con esos filtros.")
    return ids


def preparar_ollama(cliente: ClienteOllama, modelos: list[str]) -> dict:
    try:
        version = cliente.version()
        instalados = cliente.modelos_instalados()
    except ErrorOllama as e:
        sys.exit(
            f"No pude hablar con Ollama en {cliente.url} ({e}).\n"
            "¿Está abierto? Instalalo desde https://ollama.com y ejecutá `ollama serve`."
        )
    faltan = [m for m in modelos if m not in instalados and f"{m}:latest" not in instalados]
    if faltan:
        sys.exit("Faltan modelos en Ollama. Descargalos con:\n" + "\n".join(f"  ollama pull {m}" for m in faltan))
    return {"version": version, "digests": {m: instalados.get(m) or instalados.get(f"{m}:latest") for m in modelos}}


class FalloAlCalentar(Exception):
    """El modelo no quedó listo para medir: la corrida no debe seguir con él."""


def calentar(cliente: ClienteOllama, modelo: str, num_ctx: int) -> dict:
    """Carga el modelo antes de medir y comprueba que respete el formato JSON.

    - La carga no se cuenta en la primera actualización.
    - Se envía `think: false`, que los modelos que razonan por defecto (p. ej. qwen3.5)
      necesitan para responder rápido. Si el modelo rechaza el campo, se reintenta sin él.
    - El pedido de prueba no menciona JSON: si la respuesta no es el objeto del esquema,
      esta versión de Ollama está ignorando `format` y las respuestas serían inválidas.
    """
    mensajes = [{"role": "user", "content": "Saludá con una sola palabra."}]
    formato = {"type": "object", "properties": {"ok": {"type": "boolean"}}, "required": ["ok"]}
    opciones = {"temperature": 0, "num_ctx": num_ctx, "num_predict": 64}
    inicio = time.perf_counter()
    pensar: bool | None = False
    try:
        r = cliente.chat(modelo, mensajes, formato, opciones, pensar=False)
    except ErrorOllama as e:
        if "think" not in str(e).lower():
            raise FalloAlCalentar(f"{modelo} no respondió al cargarlo ({e}).") from e
        pensar = None
        try:
            r = cliente.chat(modelo, mensajes, formato, opciones)
        except ErrorOllama as e2:
            raise FalloAlCalentar(f"{modelo} no respondió al cargarlo ({e2}).") from e2
    carga_ms = round((time.perf_counter() - inicio) * 1000)
    contenido = (r.get("message") or {}).get("content", "")
    try:
        respeta_esquema = isinstance(json.loads(contenido).get("ok"), bool)
    except (json.JSONDecodeError, AttributeError):
        respeta_esquema = False
    if not respeta_esquema:
        raise FalloAlCalentar(
            f"Ollama ignoró el formato JSON pedido con {modelo} (respondió {contenido[:80]!r}). "
            "Pasa con algunas versiones de Ollama: actualizalo desde https://ollama.com/download "
            "y volvé a correr."
        )
    try:
        memoria = cliente.memoria_cargada(modelo)
    except ErrorOllama:
        memoria = None
    return {"carga_ms": carga_ms, "error": "", "memoria": memoria, "pensar": pensar}


def _fila(config: dict, case_id: str, n: int, linea: casos.Linea, r: Respuesta, aviso: bool) -> dict:
    def num(x, d=3):
        return "" if x is None else round(x, d)

    def bool_(x):
        return "" if x is None else str(x).lower()

    return {
        **config,
        "case_id": case_id,
        "linea": n,
        "hablante": linea.hablante,
        "texto": linea.texto,
        "valida": bool_(r.valida),
        "error": r.error,
        "riesgo": num(r.riesgo),
        "alerta_sugerida": bool_(r.alerta_sugerida),
        "aviso": bool_(aviso),
        "motivo": r.motivo,
        "evidencia": r.evidencia,
        "evidencia_en_texto": bool_(r.evidencia_en_texto),
        "ms": num(r.ms, 1),
        "tokens_prompt": "" if r.tokens_prompt is None else r.tokens_prompt,
        "tokens_salida": "" if r.tokens_salida is None else r.tokens_salida,
        "crudo": r.crudo,
    }


def _mostrar(carpeta: Path) -> str:
    try:
        return carpeta.relative_to(RAIZ).as_posix()
    except ValueError:
        return str(carpeta)


def _marca(r: Respuesta, aviso: bool) -> str:
    if not r.valida:
        return "x"
    if aviso:
        return "A"
    return "a" if r.alerta_sugerida else "."


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--modelos", default="", help="modelos de Ollama separados por coma, p. ej. qwen3.5:2b")
    p.add_argument("--prompts", default="tarea", help=f"variantes separadas por coma: {', '.join(PROMPTS)}")
    p.add_argument("--hablantes", default="ab", help="ab (con A/B), sin (sin hablantes) o ab,sin")
    p.add_argument("--casos", default="", help="case_id separados por coma (por defecto, todos)")
    p.add_argument("--grupo", choices=sorted(casos.GRUPOS), help="solo un grupo de casos")
    p.add_argument("--solo-reglas", action="store_true", help="correr solo el comparador de reglas (sin Ollama)")
    p.add_argument("--sin-reglas", action="store_true", help="no correr el comparador de reglas")
    p.add_argument("--url", default=URL_POR_DEFECTO, help="dirección de Ollama")
    p.add_argument("--num-ctx", type=int, default=4096, help="contexto del modelo en tokens")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--timeout", type=float, default=120.0, help="segundos máximos por actualización")
    p.add_argument("--etiqueta", default="", help="texto corto para el nombre de la carpeta")
    p.add_argument("--salida", type=Path, default=RAIZ / "corridas", help="dónde crear la carpeta de la corrida")
    p.add_argument("--detalle", action="store_true", help="mostrar cada línea y la respuesta (modo demo)")
    args = p.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    errores = casos.validar_todos()
    if errores:
        print("\n".join(errores))
        sys.exit("Hay casos con errores de formato: corregilos con `python casos.py` antes de correr.")

    modelos = [] if args.solo_reglas else _lista(args.modelos)
    if not modelos and not args.solo_reglas:
        sys.exit("Indicá --modelos (p. ej. --modelos qwen3.5:2b) o usá --solo-reglas.")
    prompts = _lista(args.prompts)
    hablantes = _lista(args.hablantes)
    for v in prompts:
        if v not in PROMPTS:
            sys.exit(f"Prompt desconocido {v!r}. Opciones: {', '.join(PROMPTS)}")
    for h in hablantes:
        if h not in HABLANTES:
            sys.exit(f"Hablantes desconocido {h!r}. Opciones: {', '.join(HABLANTES)}")
    ids = elegir_casos(args)

    cliente = ClienteOllama(args.url, args.timeout)
    # La primera carga de un modelo grande desde el disco puede tardar varios minutos.
    cliente_carga = ClienteOllama(args.url, max(args.timeout, 600.0))
    ollama = preparar_ollama(cliente, modelos) if modelos else None

    detectores = []
    if not args.sin_reglas:
        detectores.append(({"config": "reglas", "detector": "reglas", "modelo": "", "prompt": "", "hablantes": ""}, DetectorReglas()))
    for modelo in modelos:
        for variante in prompts:
            for h in hablantes:
                d = DetectorSLM(cliente, modelo, cargar_prompt(variante), h, args.num_ctx, args.seed)
                etiqueta = {"config": f"slm|{modelo}|{variante}|{h}", "detector": "slm", "modelo": modelo, "prompt": variante, "hablantes": h}
                detectores.append((etiqueta, d))
    if not detectores:
        sys.exit("No quedó ningún detector para correr.")

    nombre = datetime.now().strftime("%Y-%m-%d_%H%M%S") + (f"_{args.etiqueta}" if args.etiqueta else "")
    carpeta = args.salida.resolve() / nombre
    carpeta.mkdir(parents=True)
    manifiesto = {
        "inicio": datetime.now().isoformat(timespec="seconds"),
        "comando": "python correr.py " + " ".join(argv if argv is not None else sys.argv[1:]),
        "codigo": info_codigo(),
        "maquina": info_maquina(),
        "politica": POLITICA,
        "ollama": None if ollama is None else {"url": args.url, **ollama},
        "parametros_slm": {"num_ctx": args.num_ctx, "seed": args.seed, "temperatura": 0.0, "timeout_s": args.timeout},
        "prompts": {v: {"huella": huella(cargar_prompt(v)), "texto": cargar_prompt(v)} for v in prompts} if modelos else {},
        "configs": [c for c, _ in detectores],
        "casos": {c: huella((casos.DIR_TEXTO / f"{c}.txt").read_text(encoding="utf-8")) for c in ids},
        "modelos": {},
        "interrumpida": False,
        "fin": None,
    }

    def guardar_manifiesto() -> None:
        (carpeta / "manifiesto.json").write_text(json.dumps(manifiesto, ensure_ascii=False, indent=2), encoding="utf-8")

    guardar_manifiesto()
    print(f"Corrida: {_mostrar(carpeta)}  ({len(ids)} casos, {len(detectores)} configuraciones)")
    print("Marcas por línea: . sin alerta · A aviso emitido · a alerta posterior al aviso · x fallo\n")

    try:
        with (carpeta / "actualizaciones.csv").open("w", encoding="utf-8-sig", newline="") as f:
            escritor = csv.DictWriter(f, fieldnames=COLUMNAS)
            escritor.writeheader()
            modelo_actual = None
            for config, detector in detectores:
                if config["modelo"] and config["modelo"] != modelo_actual:
                    modelo_actual = config["modelo"]
                    print(f"Cargando {modelo_actual}...", end=" ", flush=True)
                    try:
                        carga = calentar(cliente_carga, modelo_actual, args.num_ctx)
                    except FalloAlCalentar as e:
                        manifiesto["modelos"][modelo_actual] = {"error": str(e)}
                        raise
                    manifiesto["modelos"][modelo_actual] = carga
                    guardar_manifiesto()
                    for c, d in detectores:
                        if c["modelo"] == modelo_actual:
                            d.pensar = carga["pensar"]
                    print(f"listo ({carga['carga_ms'] / 1000:.1f} s).")
                print(f"== {config['config']}")
                for case_id in ids:
                    lineas = casos.cargar_texto(case_id)
                    marcas = []
                    for n, linea, r, aviso in procesar_caso(detector, lineas):
                        escritor.writerow(_fila(config, case_id, n, linea, r, aviso))
                        f.flush()
                        marcas.append(_marca(r, aviso))
                        if args.detalle:
                            estado = f"FALLO: {r.error}" if not r.valida else (
                                f"riesgo={r.riesgo if r.riesgo is not None else '-'} alerta={'sí' if r.alerta_sugerida else 'no'}"
                            )
                            print(f"   [{n:>2}] {linea.hablante}: {linea.texto}")
                            print(f"        {estado}" + (f"  >>> AVISO: {r.motivo}" if aviso else ""))
                    print(f"   {case_id:42} {' '.join(marcas)}")
    except KeyboardInterrupt:
        manifiesto["interrumpida"] = True
        print("\nCorrida interrumpida: lo procesado hasta acá quedó guardado.")
    except FalloAlCalentar as e:
        manifiesto["interrumpida"] = True
        manifiesto["fin"] = datetime.now().isoformat(timespec="seconds")
        guardar_manifiesto()
        print("no quedó listo.")
        sys.exit(f"\n{e}\nLo procesado hasta acá quedó en {_mostrar(carpeta)}.")
    manifiesto["fin"] = datetime.now().isoformat(timespec="seconds")
    guardar_manifiesto()
    print(f"\nListo. Resumen: python resumen.py {_mostrar(carpeta)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
