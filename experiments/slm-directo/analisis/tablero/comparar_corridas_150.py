"""Agrega la comparación al HTML recibido, sin leer catálogo ni reserva.

Desde la raíz: python3 -I experiments/slm-directo/analisis/tablero/comparar_corridas_150.py
    --base /ruta/al/tablero.html --salida /ruta/al/tablero-actualizado.html
La base puede ser una salida previa: la actualización es idempotente.
"""
import argparse
import html
import importlib.util
import json
from pathlib import Path
import re
import shutil
import statistics
import tempfile

AQUI = Path(__file__).resolve().parent
SLM = AQUI.parents[1]
DIRECTO = SLM / "corridas/2026-11-04_132229_e2b-directo-150"
TITO = SLM / "corridas/2026-11-04_003715_e2b-tito-viejo-150"
spec = importlib.util.spec_from_file_location("comparacion_segura_150", DIRECTO / "comparar_directo_vs_tito.py")
comparador = importlib.util.module_from_spec(spec)
spec.loader.exec_module(comparador)


def resultado(filas):
    alerta = next((r for r in filas if r["aviso"] == "true"), {})
    return {
        "aviso": int(alerta["linea"]) if alerta else None,
        "motivo": alerta.get("motivo", ""),
        "evidencia": alerta.get("evidencia", ""),
        # Estado: 0 omitida; 1 válida; 2 error. La ausencia de fila nunca es un negativo.
        "filas": [[float(r["riesgo"]) if r["riesgo"] else None,
                   0 if r["consulta"] == "omitida" else 1 if r["valida"] == "true" else 2]
                  for r in filas],
        "errores": {r["linea"]: r["error"] for r in filas if r["error"]},
    }


def diferencias(solo, tito):
    """Compara únicamente respuestas válidas observadas en la misma línea."""
    comunes = [(n, a, b) for n, (a, b) in enumerate(zip(solo["filas"], tito["filas"]), 1)
               if a[1] == b[1] == 1]
    return {
        "riesgo": [n for n, a, b in comunes if a[0] != b[0]],
        "alerta": [n for n, _, _ in comunes if (solo["aviso"] == n) != (tito["aviso"] == n)],
        "fundamento": solo["aviso"] is not None and tito["aviso"] is not None and
                      (solo["motivo"], solo["evidencia"]) != (tito["motivo"], tito["evidencia"]),
    }


def cargar_datos():
    directo, tito, refs = comparador.datos(DIRECTO, TITO)
    manifiestos = [json.loads((p / "manifiesto.json").read_text()) for p in (DIRECTO, TITO)]
    for campo in ("parametros_slm", "prompts", "maquina"):
        if manifiestos[0][campo] != manifiestos[1][campo]:
            raise ValueError(f"Las condiciones difieren en {campo}; revisar antes de comparar")
    if manifiestos[0]["ollama"]["digests"] != manifiestos[1]["ollama"]["digests"]:
        raise ValueError("Las condiciones usan modelos distintos")
    casos = []
    for cid, ref in sorted(refs.items()):
        texto = (SLM / "casos/texto" / f"{cid}.txt").read_text().splitlines()
        for filas in (directo[cid], tito[cid]):
            if [int(r["linea"]) for r in filas] != list(range(1, len(filas) + 1)):
                raise ValueError(f"Prefijo incompleto o repetido: {cid}")
            if len(filas) > len(texto):
                raise ValueError(f"Líneas fuera de texto: {cid}")
        casos.append({
            "id": cid, "clase": ref["clase"], "grupo": ref["grupo"],
            "familia": ref.get("familia"), "pedido": ref.get("pedido"),
            "tr": ref["t_r_linea"], "tc": ref["t_c_linea"], "texto": texto,
            "solo": resultado(directo[cid]), "tito": resultado(tito[cid]),
            "activacion": next((int(r["linea"]) for r in tito[cid] if r["consulta"] != "omitida"), None),
            "indicio": next((r["indicio_texto"] for r in tito[cid] if r["indicio_texto"]), ""),
        })
        casos[-1]["diferencias"] = diferencias(casos[-1]["solo"], casos[-1]["tito"])
    estadisticas = {}
    for modo, registros in (("solo", directo), ("tito", tito)):
        v = [c for c in casos if c["clase"] == "vishing"]
        l = [c for c in casos if c["clase"] != "vishing"]
        filas = [r for rs in registros.values() for r in rs]
        estadisticas[modo] = {
            "estafas": sum(c[modo]["aviso"] is not None for c in v),
            "fa": sum(c[modo]["aviso"] is not None for c in l),
            "comunes": sum(c[modo]["aviso"] is not None for c in l if c["clase"] == "legitima"),
            "dificiles": sum(c[modo]["aviso"] is not None for c in l if c["clase"] == "legitima_dificil"),
            "con_pedido": sum(c[modo]["aviso"] is not None for c in v if c["tr"] is not None),
            "sin_pedido": sum(c[modo]["aviso"] is not None for c in v if c["tr"] is None),
            "lineas": len(filas), "consultas": sum(r["consulta"] != "omitida" for r in filas),
            "mediana_ms": statistics.median(float(r["slm_ms"]) for r in filas if r["slm_ms"]),
        }
    return {"casos": casos, "estadisticas": estadisticas,
            "corridas": {"solo": DIRECTO.name, "tito": TITO.name}}


def armar(base, datos):
    base = re.sub(r"<!-- COMPARACION_150_BEGIN -->.*?<!-- COMPARACION_150_END -->\n?", "", base, flags=re.S)
    base = re.sub(r"<script\b[^>]*>.*?</script>", "", base, flags=re.S)
    base = re.sub(r'<button\b[^>]*id="cmp-tab"[^>]*>.*?</button>', "", base, flags=re.S)
    base = re.sub(r"<title>.*?</title>", "<title>150 casos: SLM solo y Tito → E2B</title>", base)
    base = re.sub(r"<h1>.*?</h1>", "<h1>150 casos: SLM solo y Tito → Gemma 4 E2B</h1>", base, count=1)
    base = re.sub(r'<p class=m style="margin:0">.*?</p>',
                  '<p class=m style="margin:0">Corridas del 2026-11-04 · SLM solo (13:22) y con Tito (00:37) · mismo modelo, prompt, seed y PC Windows</p>',
                  base, count=1, flags=re.S)
    if "name=viewport" not in base and 'name="viewport"' not in base:
        base = base.replace("<meta charset=utf-8>", '<meta charset=utf-8><meta name="viewport" content="width=device-width,initial-scale=1">')
    base = base.replace("No cierran D07, D08, D09 ni #51.", "D07 y D08 siguen abiertas; no cambia el ADR 0001 ni cierra #51.")
    base = base.replace("El mapa dice 10; falta <code>TR-12</code>.", "Son once, contando <code>TR-12</code>; el mapa fue corregido el 2026-11-04.")
    # Mantener las lecturas previas, con una única conversación comparativa por caso.
    permitidos = {c["id"] for c in datos["casos"]}

    def articulo(match):
        bloque = match.group(0)
        cid = html.unescape(re.search(r"<header><code>(.*?)</code>", bloque).group(1))
        if cid not in permitidos:
            raise ValueError("La base contiene un caso ajeno a los manifiestos")
        bloque = re.sub(r'<p class="cmp-enlace">.*?</p>', "", bloque, flags=re.S)
        bloque = re.sub(r"<div class=dw><table class=dl>.*?</table></div>", "", bloque, flags=re.S)
        bloque = bloque.replace("<summary>Ver conversación</summary>", "<summary>Contexto de referencia</summary>")
        enlace = f'<p class="cmp-enlace"><button type="button" data-comparar="{html.escape(cid, quote=True)}">Comparar conversación: SLM solo / con Tito</button></p>'
        return bloque.replace("</article>", enlace + "</article>")

    base = re.sub(r"<article\b.*?</article>", articulo, base, flags=re.S)
    etiquetas = {"Resumen": "Resumen con Tito", "Falsas alarmas (13)": "FA con Tito (13)",
                 "Estafas perdidas (24)": "Perdidas con Tito (24)", "Estafas detectadas (51)": "Detectadas con Tito (51)",
                 "Legítimas sin aviso (62)": "Sin aviso con Tito (62)", "Corrida y cómo seguir": "Pasos recomendados"}
    for antes, despues in etiquetas.items():
        base = base.replace(f">{antes}</button>", f">{despues}</button>")
    plan = (AQUI / "comparacion_150_plantilla.html").read_text()
    comparacion, pasos = plan.split("<!-- PASOS_150 -->")
    serializado = json.dumps(datos, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    comparacion = comparacion.replace("__DATOS_150__", serializado)
    base, n = re.subn(r'<section(?: id="plan150")?><h2>(?:Corrida de diagnóstico|Pasos recomendados)</h2>.*?</section>', lambda _: pasos.strip(), base, flags=re.S)
    if n != 1:
        raise ValueError("No se encontró una única sección de pasos en el tablero")
    nav = '<div class=nav role=tablist>'
    if nav not in base or "<section" not in base:
        raise ValueError("La base no tiene la estructura esperada")
    base = base.replace(nav, nav + '<button role=tab id="cmp-tab">Comparar corridas</button>', 1)
    primer_section = base.index("<section")
    return base[:primer_section] + comparacion + base[primer_section:]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--base", type=Path, required=True)
    p.add_argument("--salida", type=Path, required=True)
    args = p.parse_args()
    # La copia aislada evita importar módulos vecinos a un HTML descargado.
    with tempfile.TemporaryDirectory(prefix="tablero-150-") as tmp:
        copia = Path(tmp) / "base.html"
        shutil.copy2(args.base, copia)
        salida = armar(copia.read_text(), cargar_datos())
    if len(salida.encode("utf-8")) >= 512 * 1024:
        raise ValueError("El HTML supera el límite de 512 KB del chat")
    args.salida.write_text(salida, encoding="utf-8")
    print(f"Panel escrito: {args.salida} ({len(salida.encode('utf-8')):,} bytes)")


if __name__ == "__main__":
    main()
