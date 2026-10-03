"""Lectura de evidencia del spike para la UI (#44), sin importar modelos ni ASR."""

import csv
import hashlib
import io
import json
import math
import platform
import re
import subprocess
import unicodedata
import urllib.parse
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RESULTADOS = AQUI / "resultados"
FUENTE_MTIME_NS = Path(__file__).stat().st_mtime_ns


# Paleta fija y determinista para detectores conocidos
PALETA_DETECTORES = {
    "RoBERTuito": "#1f77b4",                # Azul
    "RoBERTuito → Llama 3.2 1B": "#7c3aed",  # Violeta
    "DistilBETO": "#059669",                 # Verde esmeralda
    "BETO": "#0891b2",                       # Celeste / Cyan
    "ALBETO tiny": "#d97706",                # Ámbar
    "TF-IDF histórico": "#8c564b",           # Marrón
    "Reglas solas": "#dc2626",               # Rojo
    "Sin goteo": "#64748b",                  # Gris pizarra
}

COLORES_RESERVA = (
    "#e377c2", "#bcbd22", "#393b79", "#637939", "#8c6d31", "#843c39",
    "#7b4173", "#0284c7", "#10b981", "#f59e0b", "#ec4899", "#6366f1"
)

TRAZOS_CORRIDA = ("solid", "dash", "dot", "dashdot", "longdash", "longdashdot")


def nombre_detector(fila_o_str: dict | str | None) -> str:
    if isinstance(fila_o_str, dict):
        modelo = fila_o_str.get("detector_goteo") or "Sin goteo"
    else:
        modelo = str(fila_o_str or "Sin goteo")
    if modelo.startswith("cascada:") and "robertuito" in modelo and "llama3.2:1b" in modelo:
        return "RoBERTuito → Llama 3.2 1B"
    for fragmento, nombre in (("robertuito", "RoBERTuito"), ("distilbert", "DistilBETO"),
                             ("albert-tiny", "ALBETO tiny"), ("bert-base", "BETO"),
                             ("tfidf-stub", "TF-IDF histórico"), ("reglas", "Reglas solas")):
        if fragmento in modelo.lower():
            return nombre
    return modelo.split("/")[-1]


def color_detector(detector_nombre_o_fila: dict | str | None) -> str:
    if isinstance(detector_nombre_o_fila, dict):
        nombre = nombre_detector(detector_nombre_o_fila)
    else:
        nombre = str(detector_nombre_o_fila or "")
    if nombre in PALETA_DETECTORES:
        return PALETA_DETECTORES[nombre]
    norm = nombre_detector(nombre)
    if norm in PALETA_DETECTORES:
        return PALETA_DETECTORES[norm]
    h = int(hashlib.md5(norm.encode("utf-8")).hexdigest(), 16)
    return COLORES_RESERVA[h % len(COLORES_RESERVA)]


def trazo_corrida(corrida_visual: str | None) -> str:
    if not corrida_visual:
        return "solid"
    m = re.search(r"\d+", str(corrida_visual))
    if m:
        idx = (int(m.group()) - 1) % len(TRAZOS_CORRIDA)
        return TRAZOS_CORRIDA[idx]
    return "solid"


def asignar_ocurrencias(filas: list[dict]) -> None:
    """Asigna a cada fila un índice de ocurrencia determinista para preservar duplicados exactos."""
    conteo = {}
    for f in filas:
        key = (f.get("caso", ""), f.get("archivo_resultado", ""), f.get("detector_goteo", ""))
        conteo[key] = conteo.get(key, 0) + 1
        f["_ocurrencia"] = conteo[key]


def obtener_series_columnas(filas: list[dict]) -> list[dict]:
    """Obtiene las columnas de series de la matriz sin colapsar detectores ni duplicados."""
    asignar_ocurrencias(filas)
    series = []
    claves_vistas = set()
    for f in filas:
        det = nombre_detector(f)
        det_crudo = f.get("detector_goteo", "")
        corrida = f.get("corrida_visual", "C1")
        archivo = f.get("archivo_resultado", "")
        oc = f.get("_ocurrencia", 1)
        clave = (det_crudo, corrida, archivo, oc)
        if clave not in claves_vistas:
            claves_vistas.add(clave)
            series.append({
                "detector": det,
                "detector_crudo": det_crudo,
                "corrida": corrida,
                "archivo": archivo,
                "ocurrencia": oc,
                "clave": clave,
            })

    # Analizar colisiones para generar etiquetas legibles, cortas e inequívocas
    det_crudos_por_det_corrida = {}
    max_oc_por_det_crudo = {}
    for s in series:
        k = (s["detector"], s["corrida"])
        det_crudos_por_det_corrida.setdefault(k, set()).add(s["detector_crudo"])
        kc = (s["detector_crudo"], s["corrida"], s["archivo"])
        max_oc_por_det_crudo[kc] = max(max_oc_por_det_crudo.get(kc, 1), s["ocurrencia"])

    etiquetas_usadas = set()
    for idx, s in enumerate(series, start=1):
        k = (s["detector"], s["corrida"])
        kc = (s["detector_crudo"], s["corrida"], s["archivo"])
        hay_colision_raw = len(det_crudos_por_det_corrida[k]) > 1
        hay_multiples_oc = max_oc_por_det_crudo[kc] > 1

        nombre = s["detector"]
        if hay_colision_raw:
            # Distinguir por el sufijo del detector crudo si es único, o por el id completo
            sufijo = s["detector_crudo"].split("/")[-1]
            otros_sufijos = [dc.split("/")[-1] for dc in det_crudos_por_det_corrida[k] if dc != s["detector_crudo"]]
            if sufijo in otros_sufijos:
                nombre = f"{nombre} · {s['detector_crudo']}"
            else:
                nombre = f"{nombre} · {sufijo}"

        etiqueta = f"{nombre} ({s['corrida']})"
        if hay_multiples_oc:
            etiqueta = f"{etiqueta} #{s['ocurrencia']}"

        # Garantizar unicidad absoluta
        if etiqueta in etiquetas_usadas:
            if s["archivo"]:
                archivo_corto = Path(s["archivo"]).name
                etiqueta = f"{etiqueta} [{archivo_corto}]"
            n_extra = 2
            cand = etiqueta
            while cand in etiquetas_usadas:
                cand = f"{etiqueta} ({n_extra})"
                n_extra += 1
            etiqueta = cand

        etiquetas_usadas.add(etiqueta)
        s["etiqueta"] = etiqueta
        s["codigo"] = f"S{idx}"

    return series


def datos_matriz_panorama(filas: list[dict], casos: list[str] | None = None) -> dict:
    if casos is None:
        casos = list(dict.fromkeys(f["caso"] for f in filas))
    series = obtener_series_columnas(filas)
    z = []
    text = []
    customdata = []
    annotations = []
    sin_opinion_count = 0
    sin_datos_count = 0

    idx_filas = {}
    for f in filas:
        key = (f["caso"], f.get("archivo_resultado", ""), f.get("detector_goteo", ""), f.get("_ocurrencia", 1))
        idx_filas[key] = f

    for caso in casos:
        fila_z = []
        fila_text = []
        fila_custom = []
        for s in series:
            fila = idx_filas.get((caso, s["archivo"], s["detector_crudo"], s["ocurrencia"]))
            if fila is not None:
                pts = puntos(fila)
                if all(p["puntaje"] is None for p in pts):
                    sin_opinion_count += 1
                    fila_z.append(None)
                    fila_text.append("Sin opinión")
                    fila_custom.append(
                        f"<b>{caso}</b><br>Serie: {s['codigo']} · {s['etiqueta']}<br>Detector: {s['detector']}<br>"
                        f"Identidad cruda: {s['detector_crudo']}<br>"
                        f"Estado: Sin opinión registrada<br>Turnos: {fila['n_turnos']}<br>"
                        f"CSV: {s['archivo']}<br>Commit: {fila.get('commit', '')}"
                    )
                    annotations.append(dict(
                        x=s["codigo"], y=caso, text="Sin opinión",
                        showarrow=False, font=dict(color="#64748b", size=10)
                    ))
                else:
                    ps = [p["puntaje"] for p in pts if p["puntaje"] is not None]
                    val = round(max(ps), 3)
                    fila_z.append(val)
                    fila_text.append(f"{val:.2f}")
                    tr = fila.get("T_R_turno") or "Sin disparo"
                    ta = fila.get("T_A_turno") or "Sin alerta"
                    fila_custom.append(
                        f"<b>{caso}</b><br>Serie: {s['codigo']} · {s['etiqueta']}<br>Detector: {s['detector']}<br>"
                        f"Identidad cruda: {s['detector_crudo']}<br>"
                        f"Puntaje máx: {val:.3f}<br>T_R (reglas): {tr}<br>T_A (goteo): {ta}<br>"
                        f"Turnos: {fila['n_turnos']}<br>CSV: {s['archivo']}<br>Commit: {fila.get('commit', '')}"
                    )
            else:
                sin_datos_count += 1
                fila_z.append(None)
                fila_text.append("Sin datos")
                fila_custom.append(
                    f"<b>{caso}</b><br>Serie: {s['codigo']} · {s['etiqueta']}<br>Detector: {s['detector']}<br>"
                    f"Identidad cruda: {s['detector_crudo']}<br>"
                    f"Estado: Sin corrida para este ejemplo<br>CSV: {s['archivo']}"
                )
                annotations.append(dict(
                    x=s["codigo"], y=caso, text="Sin datos",
                    showarrow=False, font=dict(color="#94a3b8", size=10)
                ))
        z.append(fila_z)
        text.append(fila_text)
        customdata.append(fila_custom)

    return {
        "casos": casos,
        "series": series,
        "x": [s["codigo"] for s in series],
        "z": z,
        "text": text,
        "customdata": customdata,
        "annotations": annotations,
        "sin_opinion": sin_opinion_count,
        "sin_datos": sin_datos_count,
    }


def normalizar_anchor_streamlit(anchor: str) -> str:
    """Normaliza fragmentos de anclaje para compatibilidad con slugs sin tilde generados por Streamlit."""
    if not anchor.startswith("#"):
        return anchor
    frag = urllib.parse.unquote(anchor[1:])
    norm = unicodedata.normalize("NFKD", frag)
    limpio = "".join(c for c in norm if not unicodedata.combining(c))
    return "#" + limpio.lower()


def limpiar_enlaces_relativos_markdown(texto: str) -> str:
    def repl(match):
        label, url = match.group(1), match.group(2)
        if url.startswith("http://") or url.startswith("https://"):
            return match.group(0)
        if url.startswith("#"):
            return f"[{label}]({normalizar_anchor_streamlit(url)})"
        return f"**{label}** (`{url}`)"
    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", repl, texto)


def leer_seccion_manual(ruta: Path | None = None) -> str:
    if ruta is None:
        candidata = AQUI.parent.parent / "docs" / "investigacion" / "GUIA-CORRIDA-LABORATORIO.md"
        if candidata.is_file():
            ruta = candidata
        else:
            return "Manual no encontrado en la ruta esperada (`docs/investigacion/GUIA-CORRIDA-LABORATORIO.md`)."
    try:
        texto = ruta.read_text(encoding="utf-8")
        inicio = texto.find("## UI local para texto y resultados (#44)")
        if inicio == -1:
            return texto
        fin = texto.find("\n## Requisitos", inicio)
        if fin != -1:
            seccion = texto[inicio:fin].strip()
        else:
            seccion = texto[inicio:].strip()
        return limpiar_enlaces_relativos_markdown(seccion)
    except OSError as e:
        return f"Error al leer la guía de laboratorio: {e}"


def numero(valor):
    if valor is None or str(valor).strip() == "":
        return None
    n = float(valor)
    if not math.isfinite(n):
        raise ValueError(f"Valor no finito: {valor}")
    return n


def leer_csv(path: Path) -> tuple[list[dict], list[dict]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        lector = csv.DictReader(f)
        requeridas = {"caso", "clase", "n_turnos", "puntajes"}
        if not requeridas <= set(lector.fieldnames or []):
            raise ValueError(f"{path.name}: faltan columnas {sorted(requeridas - set(lector.fieldnames or []))}")
        filas = list(lector)
    return ([f for f in filas if f["caso"] != "_suite"],
            [f for f in filas if f["caso"] == "_suite"])


def combinar_corridas(archivos: list[Path]) -> tuple[list[dict], list[dict]]:
    """Conserva una fila por caso/detector/corrida, con la fuente identificada."""
    casos, resumenes = [], []
    for n, path in enumerate(archivos, 1):
        filas, resumen = leer_csv(path)
        fuente = str(path.relative_to(RESULTADOS))
        casos.extend({**fila, "archivo_resultado": fuente, "corrida_visual": f"C{n}"} for fila in filas)
        resumenes.extend({**fila, "archivo_resultado": fuente, "corrida_visual": f"C{n}"} for fila in resumen)
    return casos, resumenes


def tipo_entrada(fila: dict) -> str:
    if fila.get("video_url"):
        return "Grabaciones transcritas"
    if fila.get("caso") == "texto-ui":
        return "Pruebas de UI"
    return "Guiones del laboratorio"


def csv_comparacion(filas: list[dict]) -> str:
    if not filas:
        return ""
    columnas = list(dict.fromkeys(k for fila in filas for k in fila))
    f = io.StringIO(newline="")
    w = csv.DictWriter(f, fieldnames=columnas)
    w.writeheader()
    w.writerows(filas)
    return f.getvalue()


def puntos(fila: dict) -> list[dict]:
    """Restituye turnos sin opinión como None; nunca los transforma en riesgo cero."""
    n = int(fila["n_turnos"])
    if n < 1:
        raise ValueError("Cantidad de turnos inválida")
    valores = {}
    for token in (fila.get("puntajes") or "").split(","):
        if not token.strip():
            continue
        m = re.fullmatch(r"t(\d+)=(.+)", token.strip())
        if m is None:
            raise ValueError(f"Puntaje inválido: {token}")
        turno, p = int(m[1]), numero(m[2])
        if not 1 <= turno <= n or turno in valores or p is None or not 0 <= p <= 1:
            raise ValueError(f"Turno/puntaje inválido: {token}")
        valores[turno] = p
    return [{"turno": t, "puntaje": valores.get(t)} for t in range(1, n + 1)]


def texto_caso(caso: str) -> str | None:
    """Solo guiones existentes dentro del laboratorio, sin seguir rutas arbitrarias del CSV."""
    candidatas = [AQUI / "casos" / caso, AQUI / caso]
    for candidata in candidatas:
        ruta = candidata.resolve()
        if ruta.is_relative_to(AQUI) and ruta.is_file() and ruta.suffix == ".txt":
            return ruta.read_text(encoding="utf-8")
    return None


def validar_semillas(raw: bytes) -> dict:
    datos = json.loads(raw.decode("utf-8-sig"))
    if not isinstance(datos, dict):
        raise ValueError("Se espera un objeto con listas estafa y legitima")
    for clase in ("estafa", "legitima"):
        textos = datos.get(clase)
        if not isinstance(textos, list) or not textos:
            raise ValueError(f"{clase}: se requiere una lista no vacía")
        if any(not isinstance(t, str) or not t.strip() for t in textos):
            raise ValueError(f"{clase}: todos los ejemplos deben ser textos no vacíos")
    if set(t.strip() for t in datos["estafa"]) & set(t.strip() for t in datos["legitima"]):
        raise ValueError("Un mismo texto aparece en las dos clases; revisar las etiquetas")
    return datos


def procedencia() -> dict:
    git = subprocess.run(["git", "rev-parse", "HEAD"], cwd=AQUI,
                         capture_output=True, text=True, timeout=5)
    estado = subprocess.run(["git", "status", "--porcelain"], cwd=AQUI,
                            capture_output=True, text=True, timeout=5)
    versiones = {}
    for paquete in ("streamlit", "plotly", "numpy", "torch", "transformers", "scikit-learn"):
        try:
            versiones[paquete] = metadata.version(paquete)
        except metadata.PackageNotFoundError:
            versiones[paquete] = "no instalado"
    return {"fecha_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "commit": git.stdout.strip() or "desconocido",
            "cambios_sin_commit": bool(estado.stdout.strip()),
            "hardware": platform.platform(), "versiones": versiones,
            "codigo_sha256": {nombre: sha256((AQUI / nombre).read_bytes()) for nombre in
                              ("pipeline.py", "rules.py", "detector_encoder.py", "detector.py",
                               "detector_cascada.py", "ui_resultados.py", "ui_laboratorio.py")}}


def fila_texto(resultado: dict, modelo: str, origen: dict, clase: str) -> dict:
    evs = resultado["incendio"]["eventos"]
    tr = evs[0]["turno"] if evs else None
    ta = resultado["goteo"]["turno"]
    ps = [t["puntaje"] for t in resultado["turnos"] if t["puntaje"] is not None]
    return {"fecha": origen["fecha_utc"], "commit": origen["commit"],
            "caso": "texto-ui", "clase": clase, "detector_incendio": "reglas",
            "detector_goteo": modelo, "n_turnos": len(resultado["turnos"]),
            "incendio": int(bool(evs)), "goteo": int(resultado["goteo"]["disparo"]),
            "T_R_turno": tr, "T_A_turno": ta, "T_C_turno": None,
            "L_R_turnos": tr - ta if tr is not None and ta is not None else None,
            "L_C_turnos": None, "umbral_goteo": resultado["goteo"]["umbral"],
            "latencia_decision_turno": resultado["latencia_decision_turno"],
            "puntaje_max": max(ps) if ps else None,
            "puntajes": ",".join(f"t{t['n']}={t['puntaje']}" for t in resultado["turnos"]
                                 if t["puntaje"] is not None),
            "etiquetas_incendio": "|".join(sorted({e for ev in evs for e in ev["etiquetas"]})),
            "falsa_alarma": int(bool(evs) or resultado["goteo"]["disparo"]) if clase == "L" else None,
            "nota": "Prueba manual de laboratorio; clase declarada, no test independiente. "
                    "T_R_turno = reglas, no anotación humana. Sin segundos ni T_C. "
                    "Histéresis vigente del spike; D07/D08/D09 abiertas.",
            "procedencia_json": json.dumps(origen, ensure_ascii=False)}


def csv_texto(fila: dict) -> str:
    f = io.StringIO(newline="")
    w = csv.DictWriter(f, fieldnames=list(fila))
    w.writeheader()
    w.writerow(fila)
    return f.getvalue()


def guardar_csv(fila: dict) -> Path:
    """Nueva evidencia agregada, sin texto ni sobrescritura de corridas anteriores."""
    path = RESULTADOS / ("resultados-ui-" + datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%S-%fZ") + ".csv")
    with path.open("x", encoding="utf-8", newline="") as f:
        f.write(csv_texto(fila))
    return path


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()
