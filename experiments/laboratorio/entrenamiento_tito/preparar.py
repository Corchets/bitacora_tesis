"""Valida bancos sintéticos y reproduce las exportaciones de desarrollo de Tito.

No divide datos, no simula ASR y no entrena ni evalúa el encoder.
"""

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import unicodedata

LOTES = ("banco", "identidad", "cotidiano")
CLASES = ("estafa", "legitima")
PALABRAS = {
    "autenticacion": ["código", "clave", "token", "contraseña", "pin", "dígitos", "seis cifras",
                      "números", "sms", "seguridad", "dictame", "leeme", "pasame"],
    "dinero": ["transferencia", "transferí", "alias", "cbu", "efectivo", "plata", "pesos",
               "seña", "préstamo", "cuota", "deuda", "saldo", "reintegro", "acreditado"],
    "canales": ["whatsapp", "aplicación", "pantalla", "enlace", "mensaje", "llamada",
                "dispositivo", "conectarme", "cuenta", "teléfono", "computadora", "qr"],
    "instituciones": ["banco", "billetera", "anses", "obra social", "salud", "jubilación",
                      "vacuna", "consultorio", "empresa", "soporte"],
    "presion": ["urgente", "ahora", "bloqueo", "bloqueada", "premio", "beneficio", "vence",
                "no cortes", "no llames", "secreto", "hoy", "rescate"],
    "cotidiano": ["turno", "pedido", "escuela", "comida", "laburo", "familia", "puerta",
                  "reserva", "asado", "portón", "presupuesto", "comprobante", "factura"],
}


def normalizar(texto):
    """Detecta duplicados incluso si cambia tilde, mayúscula o puntuación."""
    texto = unicodedata.normalize("NFKD", texto.casefold())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return " ".join(re.findall(r"\w+", texto))


def leer_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def validar_familias(familias, fuentes, lote, ids, textos_vistos, errores):
    if not isinstance(familias, list) or len(familias) != 100:
        errores.append(f"{lote}: se requieren 100 familias")
        return []
    clases = Counter()
    filas = []
    for familia in familias:
        if not isinstance(familia, dict):
            errores.append(f"{lote}: familia no es objeto")
            continue
        fid = familia.get("id")
        etiqueta = familia.get("etiqueta")
        tema = familia.get("tema")
        origen = familia.get("fuentes")
        textos = familia.get("textos")
        if not isinstance(fid, str) or not fid.startswith(lote + "_") or fid in ids:
            errores.append(f"{lote}: id inválido o repetido: {fid!r}")
        else:
            ids.add(fid)
        if etiqueta not in CLASES or not isinstance(tema, str) or not tema.strip():
            errores.append(f"{fid}: etiqueta/tema inválidos")
            continue
        clases[etiqueta] += 1
        if not isinstance(origen, list) or not origen or any(f not in fuentes for f in origen):
            errores.append(f"{fid}: fuentes ausentes o desconocidas")
        if not isinstance(textos, list) or len(textos) != 20:
            errores.append(f"{fid}: se requieren 20 realizaciones")
            continue
        for posicion, texto in enumerate(textos, 1):
            if not isinstance(texto, str) or not texto.strip():
                errores.append(f"{fid}/{posicion}: texto vacío o inválido")
                continue
            n = len(texto.split())
            if not 6 <= n <= 65:
                errores.append(f"{fid}/{posicion}: longitud {n}, debe ser 6–65 palabras")
            clave = normalizar(texto)
            if clave in textos_vistos:
                anterior, clase_anterior = textos_vistos[clave]
                tipo = "contradicción entre clases" if etiqueta != clase_anterior else "duplicado"
                errores.append(f"{fid}/{posicion}: {tipo} con {anterior}")
            else:
                textos_vistos[clave] = (f"{fid}/{posicion}", etiqueta)
            if re.search(r"https?://|www\.|\b\d{7,}\b|\S+@\S+", texto):
                errores.append(f"{fid}/{posicion}: URL, correo o identificador numérico largo")
            if re.search(r"\b(vosotros|vosotras|ordenador|móvil|pilláis|coged)\b", texto.casefold()):
                errores.append(f"{fid}/{posicion}: marcador peninsular a revisar")
            if re.search(r"\ben una llamada\b|\bla maniobra\b|\bbajo control del (atacante|llamante)\b", texto.casefold()):
                errores.append(f"{fid}/{posicion}: narración externa; se necesita texto dicho en la llamada")
            filas.append({
                "id": f"{fid}_{posicion:02d}", "familia": fid, "lote": lote,
                "tema": tema, "etiqueta": etiqueta, "texto": texto,
                "fuentes": origen, "idioma": "es-AR", "origen": "sintetico_original",
                "uso": "entrenamiento_desarrollo", "split": None,
            })
    if clases != Counter({"estafa": 50, "legitima": 50}):
        errores.append(f"{lote}: distribución incorrecta de familias {dict(clases)}")
    return filas


def preparar(carpeta):
    errores, filas, fuentes = [], [], {}
    entradas = []
    for lote in LOTES:
        path = carpeta / f"fuentes_{lote}.json"
        entradas.append(path)
        registros = leer_json(path)
        if not isinstance(registros, list):
            errores.append(f"{path.name}: se requiere una lista de fuentes")
            continue
        for fuente in registros:
            if not isinstance(fuente, dict):
                errores.append(f"{path.name}: fuente no es objeto")
                continue
            fid = fuente.get("id")
            if not isinstance(fid, str) or fid in fuentes:
                errores.append(f"{path.name}: id de fuente inválido/repetido {fid!r}")
                continue
            if not str(fuente.get("url", "")).startswith("https://"):
                errores.append(f"{fid}: falta URL https verificable")
            for campo in ("titulo", "consulta", "uso", "hallazgo", "licencia_textos"):
                if not fuente.get(campo):
                    errores.append(f"{fid}: falta {campo}")
            fuentes[fid] = fuente
    ids, textos_vistos = set(), {}
    for lote in LOTES:
        path = carpeta / f"familias_{lote}.json"
        entradas.append(path)
        filas.extend(validar_familias(
            leer_json(path), fuentes, lote, ids, textos_vistos, errores,
        ))
    path_exclusiones = carpeta / "exclusiones.json"
    entradas.append(path_exclusiones)
    exclusiones = leer_json(path_exclusiones)
    if not isinstance(exclusiones, dict) or any(
        fid not in ids or not isinstance(motivo, str) or not motivo.strip()
        for fid, motivo in exclusiones.items()
    ):
        errores.append("exclusiones.json: familia desconocida o motivo inválido")
    if errores:
        raise ValueError("Validación fallida:\n" + "\n".join(errores))
    pendientes = []
    aceptadas = []
    for fila in filas:
        if fila["familia"] in exclusiones:
            fila["uso"] = "revision_pendiente"
            fila["motivo_exclusion"] = exclusiones[fila["familia"]]
            pendientes.append(fila)
        else:
            aceptadas.append(fila)
    semillas = {clase: [r["texto"] for r in aceptadas if r["etiqueta"] == clase] for clase in CLASES}
    por_tema = defaultdict(Counter)
    for fila in aceptadas:
        por_tema[fila["tema"]][fila["etiqueta"]] += 1
    vocabulario = {}
    normalizados = [(r["etiqueta"], normalizar(r["texto"])) for r in aceptadas]
    for categoria, palabras in PALABRAS.items():
        vocabulario[categoria] = {}
        for palabra in palabras:
            patron = re.compile(r"\b" + re.escape(normalizar(palabra)) + r"\b")
            vocabulario[categoria][palabra] = dict(Counter(
                etiqueta for etiqueta, texto in normalizados if patron.search(texto)
            ))
    longitudes = [len(r["texto"].split()) for r in aceptadas]
    cobertura = {
        "textos_generados": len(filas), "familias_generadas": len(ids),
        "textos": len(aceptadas), "familias": len(ids - set(exclusiones)),
        "pendientes_revision": len(pendientes), "familias_excluidas": len(exclusiones),
        "por_clase": dict(Counter(r["etiqueta"] for r in aceptadas)),
        "por_lote": dict(Counter(r["lote"] for r in aceptadas)),
        "por_tema": {k: dict(v) for k, v in sorted(por_tema.items())},
        "palabras": {"min": min(longitudes), "max": max(longitudes)},
        "vocabulario": vocabulario,
        "aperturas_mas_frecuentes": {
            clase: Counter(" ".join(r["texto"].split()[:4]).casefold()
                           for r in aceptadas if r["etiqueta"] == clase).most_common(10)
            for clase in CLASES
        },
        "limite": "Conteos y chequeos estructurales; no prueban calidad semántica ni rendimiento.",
    }
    manifest = {
        "version": 1, "issue": 41, "fecha": "2026-10-02", "seed": None,
        "generacion": "Modelos y despachos en orquestacion.json; textos materializados por familia.",
        "split": None, "uso": "entrenamiento_desarrollo",
        "entrada_sha256": {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(entradas)
        },
        "codigo_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "configuracion": {"lotes": list(LOTES), "familias_por_lote": 100, "textos_por_familia": 20},
        "fuentes_registradas": len(fuentes),
        "urls_fuente_unicas": len({f["url"] for f in fuentes.values()}),
        "cobertura": "cobertura.json",
        "evaluacion": "No ejecutada; no hay test ni métricas del detector.",
    }
    salidas = {}
    for nombre, datos in (("semillas.json", semillas), ("cobertura.json", cobertura), ("manifest.json", manifest)):
        salidas[nombre] = json.dumps(datos, ensure_ascii=False, indent=2) + "\n"
    salidas["ejemplos.jsonl"] = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in filas)
    salidas["pendientes_revision.jsonl"] = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in pendientes)
    muestra = ["# Muestra por familia", "", "Salida derivada: primera y última realización de cada familia.",
               "Es material para inspección; no es un test ni evidencia de revisión humana.", ""]
    grupos = defaultdict(list)
    for fila in filas:
        grupos[fila["familia"]].append(fila)
    for fid, grupo in grupos.items():
        muestra.extend([f"## {fid} · {grupo[0]['etiqueta']} · {grupo[0]['tema']} · {grupo[0]['uso']}", ""])
        if fid in exclusiones:
            muestra.extend([f"Excluida: {exclusiones[fid]}", ""])
        muestra.extend([f"- {r['texto']}" for r in (grupo[0], grupo[-1])])
        muestra.append("")
    salidas["muestra_revision.md"] = "\n".join(muestra) + "\n"
    return salidas, cobertura


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Comprobar sin escribir; exige exportaciones idénticas")
    args = parser.parse_args()
    carpeta = Path(__file__).resolve().parent
    try:
        salidas, cobertura = preparar(carpeta)
        for nombre, contenido in salidas.items():
            path = carpeta / nombre
            if args.check:
                if not path.exists() or path.read_text(encoding="utf-8") != contenido:
                    raise ValueError(f"{nombre}: falta o difiere; ejecutá preparar.py")
            else:
                path.write_text(contenido, encoding="utf-8")
    except (ValueError, OSError, TypeError, KeyError) as exc:
        parser.exit(1, f"{exc}\n")
    print(json.dumps({k: cobertura[k] for k in ("textos_generados", "textos", "familias", "pendientes_revision", "por_clase", "por_lote")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
