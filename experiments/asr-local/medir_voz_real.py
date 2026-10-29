#!/usr/bin/env python3
"""Medición del ASR con voz real (#94): re-corre offline las pruebas guardadas del panel con cada variante.

Entrada: las pruebas guardadas por «Probar el ASR» (`guardada: true`) y un CSV que dice de cada una a
qué toma, voz y condición pertenece (`voz-real/pruebas.csv`). La referencia es «Lo que dije en realidad»;
si está vacío y el CSV dice qué `bloque` del guion se leyó, es el texto de ese bloque.
Por cada variante (PLAN-VOZ-REAL.md §4) se pasa el audio guardado por el motor y se compara lo que
sale contra la referencia, frase por frase, con las etiquetas de `slm-directo/reglas.py` como medida
principal. La regla del plan §2 se aplica en la toma 2, cada paso contra el anterior.

Salida: `corridas/<fecha>_voz-real_<etiqueta>/` con `manifiesto.json`, `resumen.md` y `frases.jsonl`
(textos por frase, sin audio).

Uso típico (ver «Cómo correrlo» en PLAN-VOZ-REAL.md):
    python medir_voz_real.py
    python medir_voz_real.py --sin-whisper
    python medir_voz_real.py --variantes beam,beam+hotwords,whisper-small
    python medir_voz_real.py --solo-parakeet
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import shlex
import subprocess
import sys
import tempfile
from dataclasses import replace
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

import metricas_voz_real as M
import variantes_voz_real as V
from guion import GUION_POR_DEFECTO, Guion, cargar_guion, identificar_bloque, lineas_de_referencia
from hotwords import HOTWORDS_POR_DEFECTO

DIR_ASR = Path(__file__).resolve().parent
RAIZ_REPO = DIR_ASR.parents[1]
DIR_VOZ_REAL = DIR_ASR / "voz-real"
CSV_POR_DEFECTO = DIR_VOZ_REAL / "pruebas.csv"
DICCIONARIO_POR_DEFECTO = DIR_VOZ_REAL / "diccionario.csv"
JERGA_POR_DEFECTO = M.JERGA_POR_DEFECTO
CORRIDAS = DIR_ASR / "corridas"
VOCES = ("luciano", "otra")
CONDICIONES = ("microfono", "meet", "voz-baja", "ruido-tv", "pausas")  # las tres últimas: extras por micrófono
CANALES = {"protegida": 0, "otra": 1}  # columna del estereo.wav del panel
TOMA_DE_DECISION = 2


# --- Entrada: CSV y pruebas guardadas ------------------------------------------------------------------


def carpeta_de_pruebas_por_defecto() -> Path:
    """Donde guarda el servidor del panel (`experiments/voip/llamadas`); si en esta copia no hay, la de `../bitacora_tesis-voip`."""
    aca = RAIZ_REPO / "experiments" / "voip" / "llamadas"
    if aca.is_dir():
        return aca
    vecina = RAIZ_REPO.parent / "bitacora_tesis-voip" / "experiments" / "voip" / "llamadas"
    return vecina if vecina.is_dir() else aca


def leer_csv(ruta: str | Path) -> list[dict[str, str]]:
    """Filas de `pruebas.csv` validadas. Ignora comentarios («#») y líneas vacías."""
    texto = Path(ruta).read_text(encoding="utf-8")
    lineas = [l for l in texto.splitlines() if l.strip() and not l.lstrip().startswith("#")]
    lector = csv.DictReader(lineas)
    if not {"id", "toma", "voz", "condicion"} <= set(lector.fieldnames or []):
        raise ValueError(f"{ruta}: faltan columnas; se esperan id,toma,voz,condicion (y opcional canal,nota)")
    filas = list(lector)
    vistos = set()
    for n, fila in enumerate(filas, start=1):
        for clave in list(fila):
            fila[clave] = (fila[clave] or "").strip()
        problemas = []
        if not fila["id"]:
            problemas.append("falta el id")
        if fila["toma"] not in ("1", "2"):
            problemas.append(f"toma debe ser 1 o 2: {fila['toma']!r}")
        if fila["voz"] not in VOCES:
            problemas.append(f"voz debe ser una de {VOCES}: {fila['voz']!r}")
        if fila["condicion"] not in CONDICIONES:
            problemas.append(f"condicion debe ser una de {CONDICIONES}: {fila['condicion']!r}")
        if fila.get("bloque") and fila["bloque"] not in {"1", "2", "3", "4", "5", "6"}:
            problemas.append(f"bloque debe ser vacío o de 1 a 6: {fila['bloque']!r}")
        if fila.get("canal") and fila["canal"] not in CANALES:
            problemas.append(f"canal debe ser vacío o uno de {tuple(CANALES)}: {fila['canal']!r}")
        if fila["id"] in vistos:
            problemas.append(f"el id {fila['id']!r} está repetido")
        vistos.add(fila["id"])
        if problemas:
            raise ValueError(f"{ruta}: fila {n}: " + "; ".join(problemas))
    return filas


def elegir_canal(manifiesto: dict[str, Any], canal_csv: str = "") -> tuple[str, int]:
    """(nombre, columna) del canal a medir: el del CSV, o el que tiene audio según el manifiesto de la prueba."""
    if canal_csv:
        return canal_csv, CANALES[canal_csv]
    canales = manifiesto.get("canales")
    if isinstance(canales, dict):
        for nombre in ("protegida", "otra"):
            if nombre in canales:
                return nombre, CANALES[nombre]
    return "protegida", 0


def cargar_pruebas(filas: list[dict[str, str]], carpeta: str | Path, guion: Guion
                   ) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    """(pruebas medibles, omitidas con el motivo). Se miden solo las guardadas con referencia.

    Si «Lo que dije en realidad» está vacío y la fila trae `bloque`, la referencia es ese bloque del guion.
    """
    pruebas, omitidas = [], []
    for fila in filas:
        carpeta_prueba = Path(carpeta) / fila["id"]
        try:
            manifiesto = json.loads((carpeta_prueba / "manifiesto.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            omitidas.append({"id": fila["id"], "motivo": "no existe la carpeta o no tiene manifiesto legible"})
            continue
        referencia = str(manifiesto.get("referencia") or "").strip()
        origen = "manifiesto"
        if not referencia and fila.get("bloque"):
            referencia = "\n".join(f.texto for f in guion.bloques()[int(fila["bloque"])])
            origen = "guion"
        if manifiesto.get("guardada") is not True:
            omitidas.append({"id": fila["id"], "motivo": "no está guardada (guardada distinta de true)"})
        elif not referencia:
            omitidas.append({"id": fila["id"], "motivo": "«Lo que dije en realidad» está vacío"})
        elif origen == "manifiesto" and "referencias_por_segmento" in manifiesto and any(
                not texto.strip() for texto in manifiesto["referencias_por_segmento"].values()):
            omitidas.append({"id": fila["id"], "motivo": "Falta completar «Lo que dije en realidad» en alguna frase"})
        elif not (carpeta_prueba / "estereo.wav").is_file():
            omitidas.append({"id": fila["id"], "motivo": "no tiene estereo.wav"})
        else:
            nombre_canal, columna = elegir_canal(manifiesto, fila.get("canal", ""))
            ident = identificar_bloque(referencia, guion)
            pruebas.append({
                "id": fila["id"], "toma": int(fila["toma"]), "voz": fila["voz"], "condicion": fila["condicion"],
                "grupo": f"{fila['voz']}-{fila['condicion']}", "canal": nombre_canal, "columna": columna,
                "wav": str(carpeta_prueba / "estereo.wav"), "referencia": referencia,
                "lineas": lineas_de_referencia(referencia), "tipos": [l["tipo"] for l in ident["lineas"]],
                "bloque": {k: ident[k] for k in ("bloque", "exacto", "mezcla", "reconocidas")},
                "referencia_de": origen, "nota": fila.get("nota", ""),
            })
    return pruebas, omitidas


# --- Correr una variante ----------------------------------------------------------------------------------


def memoria_pico_de(ru_maxrss: int) -> float:
    """MB a partir de ru_maxrss (bytes en macOS, kilobytes en Linux)."""
    return round(ru_maxrss / (1024.0 * 1024.0 if sys.platform == "darwin" else 1024.0), 2)


def ejecutar_en_subproceso(spec: dict[str, Any]) -> tuple[dict[str, Any], float, str]:
    """Corre la variante en un proceso aparte: así la memoria pico es la de esa variante y no la acumulada."""
    with tempfile.TemporaryDirectory() as tmp:
        ruta_spec, ruta_salida = Path(tmp) / "spec.json", Path(tmp) / "salida.json"
        ruta_spec.write_text(json.dumps(spec), encoding="utf-8")
        proc = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "--trabajador", str(ruta_spec), str(ruta_salida)])
        _, estado, uso = os.wait4(proc.pid, 0)
        proc.returncode = os.waitstatus_to_exitcode(estado)
        if proc.returncode != 0:
            raise RuntimeError(f"La variante {spec['nombre']} terminó con error (código {proc.returncode}).")
        return json.loads(ruta_salida.read_text(encoding="utf-8")), memoria_pico_de(uso.ru_maxrss), "subproceso_por_variante"


def ejecutor_en_proceso(crear: Callable[[dict[str, Any]], Any] | None = None):
    """Corre la variante en este proceso (para pruebas o depuración). La memoria que informa es la acumulada."""
    from asr_local import obtener_memoria_pico_mb

    def ejecutar(spec: dict[str, Any]) -> tuple[dict[str, Any], float, str]:
        resultado = V.ejecutar_variante(spec, crear or V.crear_motor)
        return resultado, obtener_memoria_pico_mb(), "proceso_acumulado"

    return ejecutar


def trabajar(ruta_spec: str, ruta_salida: str) -> None:
    """Punto de entrada del subproceso: lee la especificación, corre la variante y escribe el resultado."""
    spec = json.loads(Path(ruta_spec).read_text(encoding="utf-8"))
    Path(ruta_salida).write_text(json.dumps(V.ejecutar_variante(spec), ensure_ascii=False), encoding="utf-8")


# --- Evaluación -------------------------------------------------------------------------------------------


def evaluar_prueba(prueba: dict[str, Any], corrida: dict[str, Any], terminos: M.Terminos) -> dict[str, Any]:
    """Métricas de una prueba para una variante, a partir de los finales que devolvió el motor."""
    finales = sorted(corrida["finales"], key=lambda f: f["segmento"])
    hipotesis = " ".join(f["texto"] for f in finales)
    por_frase = M.partir_por_frases(prueba["lineas"], hipotesis)
    bloques = corrida.get("bloques")
    return {
        "etiquetas": M.evaluar_frases(prueba["lineas"], por_frase, terminos, prueba["tipos"]),
        "error": M.error_de_texto(" ".join(prueba["lineas"]), hipotesis),
        "demoras_s": [f["demora_s"] for f in finales if f["demora_s"] is not None],
        "segmentos": len(finales),
        "proceso_s": corrida["proceso_s"],
        "audio_s": corrida["audio_s"],
        "p95_bloque_ms": bloques["p95_ms"] if bloques else None,
        "max_bloque_ms": bloques["max_ms"] if bloques else None,
        "hipotesis": hipotesis,
    }


def evaluar_variante(nombre: str, motor: str, config: dict[str, Any], bruto: dict[str, Any], memoria_mb: float,
                     alcance_memoria: str, pruebas: list[dict[str, Any]], terminos: M.Terminos) -> dict[str, Any]:
    por_id = {p["id"]: p for p in pruebas}
    por_prueba = {c["id"]: evaluar_prueba(por_id[c["id"]], c, terminos) for c in bruto["pruebas"]}
    grupos: dict[str, list] = {}
    tomas: dict[str, list] = {}
    for id_, r in por_prueba.items():
        p = por_id[id_]
        grupos.setdefault(f"toma{p['toma']}/{p['grupo']}", []).append(r)
        tomas.setdefault(str(p["toma"]), []).append(r)
    return {
        "nombre": nombre, "motor": motor, "config": config, "carga_s": bruto["carga_s"],
        "metadatos_motor": bruto["metadatos_motor"], "memoria_pico_mb": memoria_mb, "alcance_memoria": alcance_memoria,
        "por_prueba": por_prueba,
        "por_grupo": {k: M.agregar(v) for k, v in sorted(grupos.items())},
        "por_toma": {k: M.agregar(v) for k, v in sorted(tomas.items())},
    }


# --- Cadena de decisión (plan §4 y regla §2) ---------------------------------------------------------------


class Medicion:
    """Corre las variantes en el orden del plan y decide, paso por paso, cuáles se quedan."""

    def __init__(self, pruebas: list[dict[str, Any]], args: argparse.Namespace, terminos: M.Terminos,
                 ejecutor: Callable[[dict[str, Any]], tuple[dict[str, Any], float, str]], diccionario_vacio: bool):
        self.pruebas, self.args, self.terminos, self.ejecutor = pruebas, args, terminos, ejecutor
        self.diccionario_vacio = diccionario_vacio
        self.variantes: dict[str, dict[str, Any]] = {}
        self.pasos: list[dict[str, Any]] = []
        self.techo: list[dict[str, Any]] = []
        self.parakeet: list[dict[str, Any]] = []
        self.base = self.final = "greedy"  # con --solo-parakeet, la de Parakeet del panel

    def spec(self, nombre: str, motor: str, config: dict[str, Any]) -> dict[str, Any]:
        return {"nombre": nombre, "motor": motor, "config": config,
                "pruebas": [{"id": p["id"], "wav": p["wav"], "canal": p["columna"]} for p in self.pruebas],
                "bloque_ms": self.args.bloque_ms, "hilos": self.args.hilos_whisper if motor == "whisper" else self.args.hilos,
                "hotwords_file": str(self.args.hotwords), "jerga_file": str(self.args.jerga),
                "diccionario_file": str(self.args.diccionario),
                "modelo_dir": str(V.DIR_MODELO_PARAKEET if motor == "parakeet" else V.DIR_MODELO)}

    def correr(self, nombre: str, motor: str, config: dict[str, Any]) -> dict[str, Any]:
        print(f"[{len(self.variantes) + 1}] {nombre} ...", flush=True)
        bruto, memoria, alcance = self.ejecutor(self.spec(nombre, motor, config))
        variante = evaluar_variante(nombre, motor, config, bruto, memoria, alcance, self.pruebas, self.terminos)
        self.variantes[nombre] = variante
        return variante

    def agregado_de_decision(self, variante: dict[str, Any]) -> dict[str, Any] | None:
        return variante["por_toma"].get(str(self.args.toma_decision))

    def elegida(self, seleccion: set[str] | None, nombre: str) -> bool:
        return seleccion is None or nombre in seleccion

    def correr_cadena(self, seleccion: set[str] | None) -> None:
        config = V.ConfigKroko()
        base = self.correr("greedy", "kroko", config.como_dict())  # la línea base se corre siempre
        quedada, quedada_nombre = base, "greedy"
        self.pasos.append({"paso": "linea_base", "descripcion": V.PASOS[0].descripcion, "candidatos": [
            {"nombre": "greedy", "config": config.como_dict(), "aplica": True, "regla": None, "pasa": None,
             "elegido": True}], "se_queda": "greedy", "contra": None})
        for paso in V.PASOS[1:]:
            candidatos, evaluados = [], []
            for cand in paso.candidatos:
                if not self.elegida(seleccion, cand.nombre):
                    continue
                nueva = V.aplicar(V.ConfigKroko(**quedada["config"]), cand)
                if nueva is None:
                    candidatos.append({"nombre": cand.nombre, "aplica": False, "motivo": "no aplica sobre la configuración que se quedó"})
                    continue
                if cand.nombre == "+diccionario" and self.diccionario_vacio:
                    candidatos.append({"nombre": cand.nombre, "aplica": False,
                                       "motivo": "el diccionario está vacío: se arma con la toma 1"})
                    continue
                if nueva.hotwords:
                    nueva = replace(nueva, hotwords_score=self.args.hotwords_score)
                if nueva.beam and nueva.max_paths != self.args.max_caminos:
                    nueva = replace(nueva, max_paths=self.args.max_caminos)
                variante = self.correr(cand.nombre, "kroko", nueva.como_dict())
                agregado, anterior = self.agregado_de_decision(variante), self.agregado_de_decision(quedada)
                regla = M.regla_de_paso(agregado, anterior) if agregado and anterior else None
                item = {"nombre": cand.nombre, "config": nueva.como_dict(), "aplica": True, "regla": regla,
                        "pasa": bool(regla and regla["pasa"]), "elegido": False}
                candidatos.append(item)
                evaluados.append((item, variante))
            pasan = [(i, v) for i, v in evaluados if i["pasa"]]
            if pasan:
                item, ganadora = max(pasan, key=lambda iv: (self.agregado_de_decision(iv[1])["frases_correctas"],
                                                            -(self.agregado_de_decision(iv[1])["demora_final"]["mediana_s"] or 0)))
                item["elegido"] = True
            self.pasos.append({"paso": paso.nombre, "descripcion": paso.descripcion, "candidatos": candidatos,
                               "contra": quedada_nombre, "se_queda": item["nombre"] if pasan else None})
            if pasan:
                quedada, quedada_nombre = ganadora, item["nombre"]
        self.final = quedada_nombre

    def correr_techo(self, seleccion: set[str] | None) -> None:
        """Whisper offline: se compara con la línea base y con la configuración final, sin decidir nada."""
        for nombre, config in V.VARIANTES_WHISPER:
            if not self.elegida(seleccion, nombre):
                continue
            variante = self.correr(nombre, "whisper", config.como_dict())
            agregado = self.agregado_de_decision(variante)
            comparaciones = {}
            for contra in ("greedy", getattr(self, "final", "greedy")):
                anterior = self.agregado_de_decision(self.variantes[contra])
                comparaciones[contra] = M.regla_de_paso(agregado, anterior) if agregado and anterior else None
            self.techo.append({"nombre": nombre, "config": config.como_dict(), "comparaciones": comparaciones})

    def correr_parakeet(self, seleccion: set[str] | None) -> None:
        """Parakeet con cada corte y umbral; cada una contra la del panel con la regla §2, sin elegir ninguna."""
        for nombre, config in V.VARIANTES_PARAKEET:
            if nombre == V.PARAKEET_PANEL or self.elegida(seleccion, nombre):
                self.correr(nombre, "parakeet", config.como_dict())
        base = self.agregado_de_decision(self.variantes[V.PARAKEET_PANEL])
        for nombre, config in V.VARIANTES_PARAKEET[1:]:
            if nombre in self.variantes:
                agregado = self.agregado_de_decision(self.variantes[nombre])
                self.parakeet.append({"nombre": nombre, "config": config.como_dict(), "contra": V.PARAKEET_PANEL,
                                      "regla": M.regla_de_paso(agregado, base) if agregado and base else None})


def seleccion_de_variantes(texto: str | None, sin_whisper: bool) -> set[str] | None:
    """Los nombres pedidos con --variantes (validados), o None para todas; --sin-whisper saca las de Whisper."""
    validos = V.nombres_de_variantes()
    if texto:
        pedidos = {n.strip() for n in texto.split(",") if n.strip()}
        desconocidos = sorted(pedidos - set(validos))
        if desconocidos:
            raise ValueError(f"Variantes desconocidas: {', '.join(desconocidos)}. Las válidas: {', '.join(validos)}")
        return pedidos
    if sin_whisper:
        return {n for n in validos if not n.startswith("whisper")}
    return None


# --- Salida ----------------------------------------------------------------------------------------------


def _huella(ruta: Path) -> str | None:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()[:16] if ruta.is_file() else None


def info_git() -> dict[str, Any]:
    def git(*partes: str) -> str:
        return subprocess.check_output(["git", "-C", str(RAIZ_REPO), *partes], text=True, stderr=subprocess.DEVNULL).strip()

    try:
        return {"hash": git("rev-parse", "HEAD"), "rama": git("rev-parse", "--abbrev-ref", "HEAD"),
                "dirty": bool(git("status", "--porcelain", "-uno"))}
    except Exception:
        return {"hash": "desconocido", "rama": None, "dirty": False}


def porcentaje(x: float | None) -> str:
    return "—" if x is None else f"{x * 100:.1f}%"


def numero(x: Any, decimales: int = 2) -> str:
    return "—" if x is None else f"{x:.{decimales}f}"


def tabla_principal(med: Medicion, toma: int) -> list[str]:
    filas = ["| Variante | Frases OK | Etiquetas nuevas en negativas | Recall críticos | Recall bancos y apps | Recall jerga* | WER | CER | Segmentos finales | Demora final mediana (s) | p95 (s) | Proceso (s) | RTF | p95 / máx. por bloque (ms) | Memoria pico (MB) |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for nombre, v in med.variantes.items():
        a = v["por_toma"].get(str(toma))
        if not a:
            continue
        p95 = a["p95_bloque_ms"]
        filas.append(
            f"| `{nombre}` | {a['frases_correctas']}/{a['frases']} | {a['etiquetas_nuevas_en_negativas']} | "
            f"{porcentaje(a['recall_criticos']['recall'])} | {porcentaje(a['recall_entidades']['recall'])} | "
            f"{porcentaje(a['recall_jerga']['recall'])} | {porcentaje(a['wer'])} | {porcentaje(a['cer'])} | "
            f"{a['segmentos_finales']} | {numero(a['demora_final']['mediana_s'], 2)} | {numero(a['demora_final']['p95_s'], 2)} | "
            f"{a['proceso_s']:.2f} | {numero(a['rtf'], 3)} | {(numero(p95['max'], 1) + ' / ' + numero(a['max_bloque_ms'], 1)) if p95 else '—'} | {v['memoria_pico_mb']:.0f} |")
    return filas


def lineas_de_parakeet(med: Medicion) -> list[str]:
    toma = med.args.toma_decision
    salida = [f"Cada corte y umbral contra `{V.PARAKEET_PANEL}` (el del panel), en la toma {toma}, con las cuatro condiciones de la regla. "
              "No se elige sola: «pasa» quiere decir que cumple las cuatro.", "",
              "| Variante | Frases más | Etiquetas nuevas en negativas | Demora extra (s) | WER extra (puntos) | ¿Pasa? |",
              "|---|---|---|---|---|---|"]
    for c in med.parakeet:
        r = c["regla"]
        if r is None:
            salida.append(f"| `{c['nombre']}` | — | — | — | — | sin datos de la toma {toma} |")
            continue
        k = r["criterios"]
        marca = lambda ok: "" if ok else " ✗"
        salida.append(
            f"| `{c['nombre']}` | {k['etiquetas']['frases_mas']:+d}{marca(k['etiquetas']['cumple'])} | "
            f"{k['negativas']['etiquetas_nuevas']:+d}{marca(k['negativas']['cumple'])} | "
            f"{numero(k['demora']['extra_s'], 2) if k['demora']['extra_s'] is not None else '—'}{marca(k['demora']['cumple'])} | "
            f"{(k['wer']['extra'] * 100):+.1f}{marca(k['wer']['cumple'])} | {'**sí**' if r['pasa'] else 'no'} |")
    return salida


def lineas_de_decision(med: Medicion) -> list[str]:
    toma = med.args.toma_decision
    if not any(p["toma"] == toma for p in med.pruebas):
        return [f"No hay pruebas de la toma {toma}: **no se aplicó la regla** y no se decidió ningún paso. "
                f"La tabla de la sección 2 sirve para mirar; la decisión espera la toma {toma}."]
    if not med.pasos:  # --solo-parakeet: no corrió la cadena de Zipformer
        return lineas_de_parakeet(med)
    salida = [f"Cada candidato se compara con el paso que se quedó antes, en la toma {toma} (todas las condiciones juntas). "
              "Se queda solo si cumple las cuatro: **≥ 2 frases más con etiquetas correctas**, **sin etiquetas nuevas en negativas** "
              "(no más que el paso anterior), **demora final mediana ≤ +0,3 s** y **WER ≤ +2 puntos**.", "",
              "| Paso | Candidato | Contra | Frases más | Etiquetas nuevas en negativas (vs. anterior) | Demora extra (s) | WER extra (puntos) | ¿Se queda? |",
              "|---|---|---|---|---|---|---|---|"]
    for paso in med.pasos[1:]:
        for c in paso["candidatos"]:
            if not c["aplica"]:
                salida.append(f"| {paso['paso']} | `{c['nombre']}` | — | — | — | — | — | no corrió: {c['motivo']} |")
                continue
            r = c["regla"]
            if r is None:
                salida.append(f"| {paso['paso']} | `{c['nombre']}` | {paso['contra']} | — | — | — | — | sin datos |")
                continue
            k = r["criterios"]
            marca = lambda ok: "" if ok else " ✗"
            salida.append(
                f"| {paso['paso']} | `{c['nombre']}` | {paso['contra']} | {k['etiquetas']['frases_mas']:+d}{marca(k['etiquetas']['cumple'])} | "
                f"{k['negativas']['etiquetas_nuevas']:+d}{marca(k['negativas']['cumple'])} | "
                f"{numero(k['demora']['extra_s'], 2) if k['demora']['extra_s'] is not None else '—'}{marca(k['demora']['cumple'])} | "
                f"{(k['wer']['extra'] * 100):+.1f}{marca(k['wer']['cumple'])} | "
                f"{'**sí**' if c['elegido'] else 'no' + (' (pasa, pero hay otro mejor)' if c['pasa'] else '')} |")
    if len(salida) == 6:  # solo el encabezado: no se corrió ningún candidato de la cadena
        salida += ["| — | — | — | — | — | — | — | no se corrió ningún candidato de la cadena |"]
    quedan = [p["se_queda"] for p in med.pasos[1:] if p["se_queda"]]
    salida += ["", f"**Se quedan:** {', '.join(f'`{q}`' for q in quedan) if quedan else 'ningún paso'}. "
               f"**Configuración final:** `{med.final}`"
               + ("." if quedan else " (la línea base, sin cambios).")]
    if med.techo:
        salida += ["", "Techo offline (Whisper, no pasa al panel), mismas cuentas contra la línea base y contra la configuración final:", "",
                   "| Whisper | Contra | Frases más | Etiquetas nuevas en negativas | WER extra (puntos) |", "|---|---|---|---|---|"]
        for t in med.techo:
            for contra, r in t["comparaciones"].items():
                if r is None:
                    continue
                k = r["criterios"]
                salida.append(f"| `{t['nombre']}` | {contra} | {k['etiquetas']['frases_mas']:+d} | "
                              f"{k['negativas']['etiquetas_nuevas']:+d} | {(k['wer']['extra'] * 100):+.1f} |")
    if med.parakeet:
        salida += ["", "Parakeet (aparte de la cadena):", ""] + lineas_de_parakeet(med)
    return salida


def tablas_por_grupo(med: Medicion) -> list[str]:
    salida = []
    claves = sorted({k for v in med.variantes.values() for k in v["por_grupo"]})
    for clave in claves:
        salida += [f"### {clave}", "", "| Variante | Frases OK | Etiquetas nuevas en negativas | Recall críticos | WER | Segmentos | Demora mediana (s) |",
                   "|---|---|---|---|---|---|---|"]
        for nombre, v in med.variantes.items():
            a = v["por_grupo"].get(clave)
            if a:
                salida.append(f"| `{nombre}` | {a['frases_correctas']}/{a['frases']} | {a['etiquetas_nuevas_en_negativas']} | "
                              f"{porcentaje(a['recall_criticos']['recall'])} | {porcentaje(a['wer'])} | "
                              f"{a['segmentos_finales']} | {numero(a['demora_final']['mediana_s'], 2)} |")
        salida.append("")
    return salida


def tabla_recall_por_termino(med: Medicion, toma: int) -> list[str]:
    columnas = [med.base] + ([med.final] if med.final != med.base else [])
    a0 = med.variantes[med.base]["por_toma"].get(str(toma))
    if not a0 or not a0["recall_criticos"]["por_termino"]:
        return ["_Sin términos críticos en la referencia._"]
    salida = ["| Término | En la referencia | " + " | ".join(f"`{c}`" for c in columnas) + " |",
              "|---|---|" + "---|" * len(columnas)]
    for termino, celda in a0["recall_criticos"]["por_termino"].items():
        valores = []
        for c in columnas:
            t = med.variantes[c]["por_toma"][str(toma)]["recall_criticos"]["por_termino"].get(termino)
            valores.append(f"{t['ok']}/{t['ref']}" if t else "—")
        salida.append(f"| `{termino}` | {celda['ref']} | " + " | ".join(valores) + " |")
    return salida


def sustituciones_toma1(med: Medicion, tope: int = 30) -> list[tuple[str, str, int]]:
    from collections import Counter

    cuenta: Counter = Counter()
    base = med.variantes[med.base]["por_prueba"]
    for p in med.pruebas:
        if p["toma"] == 1:
            cuenta.update(M.sustituciones(p["lineas"], base[p["id"]]["hipotesis"]))
    return [(error, dicho, n) for (error, dicho), n in cuenta.most_common(tope)]


def escribir_resumen(ruta: Path, med: Medicion, manifiesto: dict[str, Any]) -> None:
    mapa = os.path.relpath(RAIZ_REPO / "docs/gestion/MAPA-DECISIONES.md", ruta.resolve().parent)
    plan = os.path.relpath(DIR_ASR / "PLAN-VOZ-REAL.md", ruta.resolve().parent)
    toma = med.args.toma_decision
    datos = manifiesto["datos"]
    por_toma = {}
    for p in med.pruebas:
        por_toma.setdefault(p["toma"], {}).setdefault(p["grupo"], []).append(p)
    l = ["# Resumen de la medición del ASR con voz real", "",
         "> **ADVERTENCIA: son una o dos voces del equipo, sin piloto: no es evidencia de rendimiento general ni cierra D09** "
         f"(ver [MAPA-DECISIONES.md]({mapa}#d09--elegir-asr-y-detector)). Plan: [PLAN-VOZ-REAL.md]({plan}). Issue #94.", ""]
    if med.args.nota:
        l += [f"> **Nota de esta corrida:** {med.args.nota}", ""]
    l += ["> **Estado: propuesta sin discutir.** Las listas de términos y jerga se usan como instrumento; D07 sigue abierta.", "",
          "## 1. Datos", ""]
    for t in sorted(por_toma):
        for g, ps in sorted(por_toma[t].items()):
            exactos = sum(1 for p in ps if p["bloque"]["exacto"])
            l.append(f"- Toma {t}, `{g}`: {len(ps)} pruebas ({exactos} con el bloque tal cual el guion). "
                     f"Bloques: {', '.join(str(p['bloque']['bloque'] or '?') for p in ps)}.")
    if not med.pruebas:
        l.append("- Ninguna prueba medible.")
    l.append(f"- Omitidas: {len(datos['omitidas'])}" + ("." if not datos["omitidas"] else ": " +
             "; ".join(f"`{o['id']}` ({o['motivo']})" for o in datos["omitidas"])))
    audio = round(sum(p["duracion_s"] for p in datos["pruebas"] if p.get("duracion_s")), 1)
    l += [f"- Carpeta de pruebas: `{datos['carpeta_pruebas']}` | CSV: `{datos['csv']}` | audio medido: {audio} s.", "",
          f"## 2. Resultado por variante (toma {toma}, todas las condiciones juntas)", ""]
    if not any(p["toma"] == toma for p in med.pruebas):
        l += [f"_No hay pruebas de la toma {toma}; se muestran todas las pruebas juntas._", ""]
        toma_tabla = None
    else:
        toma_tabla = toma
    l += tabla_principal(med, toma_tabla) if toma_tabla else tabla_todas(med)
    l += ["", "\\* La jerga es informativa, sin umbral. «Frases OK» = frases cuyas etiquetas de `reglas.py` sobre la transcripción son "
          "iguales a las de la referencia. La demora es offline (ver sección 6).", "",
          f"## 3. Regla del plan §2 (toma {toma})", ""] + lineas_de_decision(med)
    l += ["", "## 4. Por toma y condición", ""] + tablas_por_grupo(med)
    if toma_tabla:
        l += [f"## 5. Recall por término crítico (toma {toma})", ""] + tabla_recall_por_termino(med, toma_tabla) + [""]
    sust = sustituciones_toma1(med)
    l += ["## 5b. Sustituciones frecuentes de la toma 1 (candidatas al diccionario)", ""]
    if sust:
        l += [f"Lo que salió con `{med.base}` → lo que se dijo. Revisá cada una antes de pasarla a `voz-real/diccionario.csv`.", "",
              "| Salió | Se dijo | Veces |", "|---|---|---|"] + [f"| `{e}` | `{d}` | {n} |" for e, d, n in sust]
    else:
        l.append("_Sin pruebas de la toma 1 o sin sustituciones._")
    l += ["", "## 6. Cómo se midió", "",
          f"- El audio guardado (canal {', '.join(sorted({p['canal'] for p in med.pruebas})) or '—'} del estéreo) se pasa por cada variante en bloques de "
          f"{med.args.bloque_ms} ms con {med.args.hilos} hilos, igual que el servidor del panel.",
          "- **Demora de la frase final** = `disponible_s − fin de la voz`, con el reloj simulado de `asr_local.py` (`disponible_s` suma el tiempo de proceso "
          "de cada bloque) y el fin de la voz en el último bloque con RMS sobre el umbral. No incluye red ni pantalla. "
          "La final que sale al cerrar la prueba cuenta como segmento pero no entra en la demora. Whisper va por lotes y no tiene demora comparable.",
          "- **Proceso, p95 por bloque y memoria pico**: el proceso suma el tiempo de todos los bloques; el p95 es el máximo entre pruebas de los p95 por bloque; "
          "la memoria pico es la del subproceso de esa variante (incluye la carga del modelo) y no se puede separar por condición.",
          "- La ganancia y el umbral RMS **de captura** ya quedaron en el audio: offline solo se rehacen el umbral del motor (`rms-*`) y una normalización de nivel (`norm`).",
          "- Los hotwords usan un `bpe.vocab` sintético con puntaje `-(ln(id+2)+3)`; `beam+hotwords-id` repite el `-id` del plan. Ver `hotwords.py`.",
          "- Whisper con ayudas: `hotwords` = términos críticos, bancos y apps; `initial_prompt` = la jerga.",
          "", "## 7. Reproducir", "", "```bash", manifiesto["comando"], "```", "",
          f"Código: `{manifiesto['codigo']['hash']}` ({manifiesto['codigo']['rama']}, {'con cambios sin commit' if manifiesto['codigo']['dirty'] else 'limpio'}). "
          "Detalle completo en `manifiesto.json`; textos por frase en `frases.jsonl`."]
    ruta.write_text("\n".join(l) + "\n", encoding="utf-8")


def tabla_todas(med: Medicion) -> list[str]:
    """Si no hay pruebas de la toma de decisión, la misma tabla con todas las pruebas juntas."""
    for v in med.variantes.values():
        v["por_toma"]["todas"] = M.agregar(list(v["por_prueba"].values()))
    return tabla_principal(med, "todas")


def escribir_salida(carpeta: Path, med: Medicion, args: argparse.Namespace, omitidas: list[dict[str, str]], comando: str) -> None:
    from asr_local import obtener_info_hardware, obtener_versiones_paquetes

    carpeta.mkdir(parents=True, exist_ok=True)
    datos = {
        "carpeta_pruebas": str(args.pruebas), "csv": str(args.csv),
        "pruebas": [{"id": p["id"], "toma": p["toma"], "voz": p["voz"], "condicion": p["condicion"], "canal": p["canal"],
                     "bloque": p["bloque"], "lineas_referencia": len(p["lineas"]),
                     "referencia_de": p["referencia_de"],
                     "duracion_s": med.variantes[med.base]["por_prueba"][p["id"]]["audio_s"]} for p in med.pruebas],
        "omitidas": omitidas,
    }
    manifiesto = {
        "fecha": datetime.now().isoformat(timespec="seconds"), "comando": comando, "datos": datos,
        "configuracion": {
            "bloque_ms": args.bloque_ms, "hilos_kroko": args.hilos, "hilos_whisper": args.hilos_whisper,
            "toma_de_decision": args.toma_decision, "hotwords_score": args.hotwords_score, "max_caminos": args.max_caminos,
            "modelo": str(V.DIR_MODELO.name), "motores_por_subproceso": not args.en_proceso,
            "archivos": {n: {"ruta": str(r), "sha256_16": _huella(Path(r))} for n, r in
                         (("guion", args.guion), ("hotwords", args.hotwords), ("jerga", args.jerga),
                          ("diccionario", args.diccionario), ("pruebas_csv", args.csv))},
            "regla": {"min_frases_mas": M.MIN_FRASES_MAS, "max_demora_extra_s": M.MAX_DEMORA_EXTRA_S, "max_wer_extra": M.MAX_WER_EXTRA},
        },
        "codigo": info_git(), "versiones": obtener_versiones_paquetes(),
        "hardware": {**obtener_info_hardware(), "python": platform.python_version()},
        "nota": args.nota or None,
        "decision": {"toma": args.toma_decision, "pasos": med.pasos, "configuracion_final": med.final, "techo": med.techo,
                     "parakeet": med.parakeet},
        "variantes": {n: {k: v[k] for k in ("motor", "config", "carga_s", "metadatos_motor", "memoria_pico_mb", "alcance_memoria",
                                            "por_grupo", "por_toma")}
                      | {"por_prueba": {i: {k: r[k] for k in ("error", "demoras_s", "segmentos", "proceso_s", "audio_s", "p95_bloque_ms", "max_bloque_ms")}
                                        | {"etiquetas": {k: x for k, x in r["etiquetas"].items() if k not in ("frases", "recall")}}
                                        for i, r in v["por_prueba"].items()}}
                      for n, v in med.variantes.items()},
        "sustituciones_toma1": [{"salio": e, "se_dijo": d, "veces": n} for e, d, n in sustituciones_toma1(med)],
    }
    (carpeta / "manifiesto.json").write_text(json.dumps(manifiesto, indent=2, ensure_ascii=False), encoding="utf-8")
    with open(carpeta / "frases.jsonl", "w", encoding="utf-8") as f:
        for nombre, v in med.variantes.items():
            for p in med.pruebas:
                for fr in v["por_prueba"][p["id"]]["etiquetas"]["frases"]:
                    f.write(json.dumps({"variante": nombre, "prueba": p["id"], "toma": p["toma"], "grupo": p["grupo"], **fr},
                                       ensure_ascii=False) + "\n")
    escribir_resumen(carpeta / "resumen.md", med, manifiesto)


# --- Línea de comandos -----------------------------------------------------------------------------------


def parsear(argv: list[str] | None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Mide el ASR con las pruebas guardadas del panel: cada variante, re-corrida offline sobre el audio guardado.")
    p.add_argument("--pruebas", default=None, help="carpeta con las pruebas del panel (defecto: experiments/voip/llamadas)")
    p.add_argument("--csv", default=str(CSV_POR_DEFECTO), help="qué es cada prueba: id,toma,voz,condicion[,bloque,canal,nota]")
    p.add_argument("--variantes", default=None, help="solo estas variantes, separadas por coma (greedy se corre siempre). "
                   f"Válidas: {', '.join(V.nombres_de_variantes())}")
    p.add_argument("--sin-whisper", action="store_true", help="no corre las variantes de Whisper (son lentas)")
    p.add_argument("--solo-parakeet", action="store_true",
                   help=f"solo Parakeet con cada corte y umbral, sin la cadena de Zipformer ni Whisper ({V.PARAKEET_PANEL} se corre siempre)")
    p.add_argument("--toma-decision", type=int, default=TOMA_DE_DECISION, choices=(1, 2), help="toma donde se aplica la regla (defecto: 2)")
    p.add_argument("--bloque-ms", type=int, default=V.BLOQUE_MS_POR_DEFECTO, help="tamaño de bloque (defecto: 40, como el panel)")
    p.add_argument("--hilos", type=int, default=V.HILOS_POR_DEFECTO, help="hilos del ASR sherpa (defecto: 2, como el servidor)")
    p.add_argument("--hilos-whisper", type=int, default=4)
    p.add_argument("--hotwords", default=str(HOTWORDS_POR_DEFECTO))
    p.add_argument("--hotwords-score", type=float, default=1.5, help="puntaje de los hotwords de sherpa (se ajusta con la toma 1)")
    p.add_argument("--max-caminos", type=int, default=4, help="max_active_paths del beam (defecto: 4)")
    p.add_argument("--jerga", default=str(JERGA_POR_DEFECTO))
    p.add_argument("--diccionario", default=str(DICCIONARIO_POR_DEFECTO))
    p.add_argument("--guion", default=str(GUION_POR_DEFECTO))
    p.add_argument("--salida", default=None, help="carpeta de salida (defecto: corridas/<fecha>_voz-real_<etiqueta>)")
    p.add_argument("--etiqueta", default=None, help="sufijo del nombre de la carpeta de salida")
    p.add_argument("--nota", default=None, help="texto libre para la cabecera del resumen (por ejemplo, si es una corrida de humo)")
    p.add_argument("--en-proceso", action="store_true", help="no usa subprocesos (la memoria pico sale acumulada); para depurar")
    return p.parse_args(argv)


def carpeta_de_salida(args: argparse.Namespace, n_pruebas: int) -> Path:
    if args.salida:
        return Path(args.salida)
    base = CORRIDAS / f"{datetime.now():%Y-%m-%d}_voz-real_{args.etiqueta or f'{n_pruebas}pruebas'}"
    destino, k = base, 2
    while destino.exists():
        destino, k = Path(f"{base}-{k}"), k + 1
    return destino


def medir(args: argparse.Namespace, ejecutor: Callable | None = None) -> Path:
    from diccionario import Diccionario

    args.pruebas = Path(args.pruebas) if args.pruebas else carpeta_de_pruebas_por_defecto()
    seleccion = seleccion_de_variantes(args.variantes, args.sin_whisper)
    guion = cargar_guion(args.guion)
    pruebas, omitidas = cargar_pruebas(leer_csv(args.csv), args.pruebas, guion)
    for o in omitidas:
        print(f"Se omite {o['id']}: {o['motivo']}", file=sys.stderr)
    if not pruebas:
        raise SystemExit("No hay pruebas medibles: completá voz-real/pruebas.csv con pruebas guardadas que tengan «Lo que dije en realidad».")
    print(f"{len(pruebas)} pruebas medibles ({len(omitidas)} omitidas) de {args.pruebas}", flush=True)
    med = Medicion(pruebas, args, M.cargar_terminos(args.hotwords, args.jerga),
                   ejecutor or (ejecutor_en_proceso() if args.en_proceso else ejecutar_en_subproceso),
                   diccionario_vacio=len(Diccionario.desde_archivo(args.diccionario)) == 0)
    if args.solo_parakeet:
        med.base = med.final = V.PARAKEET_PANEL
        med.correr_parakeet(seleccion)
    else:
        med.correr_cadena(seleccion)
        if seleccion is None or any(n.startswith("whisper") for n in seleccion):
            med.correr_techo(seleccion)
        if seleccion is None or any(n.startswith("parakeet") for n in seleccion):
            med.correr_parakeet(seleccion)
    carpeta = carpeta_de_salida(args, len(pruebas))
    comando = "python experiments/asr-local/medir_voz_real.py " + shlex.join(sys.argv[1:])
    escribir_salida(carpeta, med, args, omitidas, comando.strip())
    print(f"Listo: {carpeta}/resumen.md")
    return carpeta


def main(argv: list[str] | None = None) -> None:
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] == "--trabajador":  # subproceso de una variante, ver ejecutar_en_subproceso
        trabajar(argv[1], argv[2])
        return
    medir(parsear(argv))


if __name__ == "__main__":
    main()
