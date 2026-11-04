"""Actualiza el panel de lectura recibido, conservando su estética e historial.

python3 -I experiments/slm-directo/analisis/tablero/actualizar_panel_lectura.py \
    --base /ruta/al/panel.html --salida /ruta/al/panel.html
No ejecuta modelos ni enumera el corpus. Reutiliza las guardas de ultimas_corridas.
"""
import argparse
import base64
import gzip
import html
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import re

AQUI = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("ultimas_lectura", AQUI / "ultimas_corridas.py")
ultimas = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ultimas)
BEGIN = "<!-- REVISION_CORRIDAS_BEGIN -->"
END = "<!-- REVISION_CORRIDAS_END -->"


class Texto(HTMLParser):
    def __init__(self):
        super().__init__()
        self.partes = []

    def handle_data(self, data):
        self.partes.append(data)


def texto_html(bloque):
    parser = Texto()
    parser.feed(bloque)
    return " ".join(" ".join(parser.partes).split())


def empaquetar(datos):
    crudo = json.dumps(datos, ensure_ascii=False, separators=(",", ":")).encode()
    return json.dumps({"gzip": base64.b64encode(gzip.compress(crudo, mtime=0)).decode()})


def desempaquetar(texto):
    datos = json.loads(texto)
    return json.loads(gzip.decompress(base64.b64decode(datos["gzip"]))) if "gzip" in datos else datos


def armar(base, datos):
    anterior = re.search(r'<script id="cmp-data" type="application/json">(.*?)</script>', base, re.S)
    if not anterior:
        raise ValueError("La base no conserva los datos de la comparación histórica")
    historico = desempaquetar(anterior[1])
    if historico.get("usar") == "historico":
        paquete = re.search(r'<script id="rev-data" type="application/json">(.*?)</script>', base, re.S)
        historico = desempaquetar(paquete[1])["historico"]
    casos_historicos = []
    for c in historico["casos"]:
        if c["id"] not in datos["casos"] or c.get("texto", datos["casos"][c["id"]]["texto"]) != datos["casos"][c["id"]]["texto"]:
            raise ValueError("El texto histórico no coincide con el desarrollo autorizado")
        casos_historicos.append({k: v for k, v in c.items() if k != "texto"})
    historico = dict(historico, casos=casos_historicos)
    base = re.sub(re.escape(BEGIN) + ".*?" + re.escape(END) + "\n?", "", base, flags=re.S)
    base = re.sub(r'<button\b[^>]*id="rev-tab"[^>]*>.*?</button>', "", base, flags=re.S)
    # Se conservan todas las lecturas históricas; nunca se atribuyen a la nueva corrida.
    lecturas = {}
    for articulo in re.findall(r"<article\b.*?</article>", base, re.S):
        cabecera = re.search(r"<header><code>(.*?)</code>", articulo)
        if not cabecera:
            continue
        cid = html.unescape(cabecera[1])
        if cid not in datos["casos"]:
            raise ValueError("La base contiene un caso ajeno a los manifiestos de desarrollo")
        why = re.search(r'<p class=(?:"why"|why)>(.*?)</p>', articulo, re.S)
        if why:
            lecturas[cid] = texto_html(why[1])
    datos = dict(datos, lecturas_previas=lecturas)
    nav = '<div class=nav role=tablist>'
    if nav not in base or 'id="comparacion150"' not in base:
        raise ValueError("La base no es el panel comparativo de lectura esperado")
    base = base.replace(nav, nav + '<button role=tab id="rev-tab">Últimas pruebas · leer casos</button>', 1)
    # Las pestañas originales siguen disponibles y conservan sus análisis íntegros.
    etiquetas = {"Comparar corridas": "Comparación v1 · Windows", "Resumen con Tito": "Resumen v1 · Windows",
                 "FA con Tito (13)": "FA v1 Windows (13)", "Perdidas con Tito (24)": "Perdidas v1 Windows (24)",
                 "Detectadas con Tito (51)": "Detectadas v1 Windows (51)", "Sin aviso con Tito (62)": "Sin aviso v1 Windows (62)",
                 "Pasos recomendados": "Revisar los casos primero"}
    for antes, despues in etiquetas.items():
        base = base.replace(f">{antes}</button>", f">{despues}</button>")
    base = re.sub(r"<title>.*?</title>", "<title>150 casos · pruebas y revisión del corpus</title>", base, count=1)
    base = re.sub(r"<h1>.*?</h1>", "<h1>150 casos · pruebas y revisión del corpus</h1>", base, count=1)
    corte = datos["hasta"].replace("T", " ")
    base = re.sub(r'<p class=m style="margin:0">.*?</p>',
                  f'<p class=m style="margin:0">{len(datos["corridas"])} condiciones completas · hasta {corte} (reloj de las corridas) · lecturas históricas conservadas</p>',
                  base, count=1, flags=re.S)
    # Un solo paquete conserva y comprime mejor textos compartidos, sin cambiar CSS.
    base = re.sub(r'<script id="cmp-data" type="application/json">(.*?)</script>',
                  '<script id="cmp-data" type="application/json">{"usar":"historico"}</script>', base, flags=re.S)
    base = base.replace("document.addEventListener('DOMContentLoaded',()=>{", "document.addEventListener('DOMContentLoaded',async()=>{")
    base = base.replace("JSON.parse(document.getElementById('cmp-data').textContent)", "await leerDatosComprimidos('cmp-data')")
    base = base.replace("'input[type=search]:not(#cmp-search)'", "'input[type=search]:not(#cmp-search):not(#rev-buscar)'")
    base = base.replace("go(0);filtrar();", "go(tabs.findIndex(t=>t.id==='cmp-tab'));filtrar();")
    nueva = (AQUI / "lectura_corridas_plantilla.html").read_text(encoding="utf-8")
    nueva = nueva.replace("__DATOS_LECTURA__", empaquetar({"actual": datos, "historico": historico}))
    # Reutilizar exactamente el CSS comparativo que ya tiene el panel suministrado.
    primer_section = base.index("<section")
    base = base[:primer_section] + BEGIN + nueva + END + "\n" + base[primer_section:]
    inicio = '''<!-- REVISION_PRIORIDAD_BEGIN --><h3>Revisar los casos antes de atribuir el problema al sistema</h3>
<p>Luciano plantea el 2026-11-04 que parte del problema puede estar en casos ambiguos o mal construidos.
Es una hipótesis para revisar, no una conclusión sobre todos los errores. No se cambia el detector ni se corrigen etiquetas desde este panel.</p>
<ol><li>Leer el diálogo completo sin mirar primero el resultado del modelo.</li>
<li>Separar lo que el texto permite saber de lo que solo afirma la ficha del caso. Revisar clase, pedido T_R y cumplimiento T_C.</li>
<li>Contrastar con la conversación de la otra clase más parecida: ¿hay una diferencia observable y suficiente?</li>
<li>Registrar dudas y adjudicarlas en D07, conservando la referencia original. Después recalcular las métricas sobre una versión trazable.</li></ol>
<p><b>Ejemplo concreto:</b> la referencia de TR-11 admite que la identidad del familiar no se verifica con el diálogo y deja pendiente si el aviso cuenta como falsa alarma.
En cambio BANCO-003 sí incluye un pedido explícito de entregar efectivo en L19. Revisar el corpus no convierte automáticamente cada pérdida en un caso inválido.</p>
<details><summary>Plan experimental anterior, conservado como antecedente</summary><!-- REVISION_PRIORIDAD_END -->'''
    if "REVISION_PRIORIDAD_BEGIN" not in base:
        base = base.replace('<section id="plan150"><h2>Pasos recomendados</h2>', '<section id="plan150"><h2>Revisar los casos primero</h2>' + inicio, 1)
        base = re.sub(r'(<section id="plan150">.*?)(</section>)', r'\1</details>\2', base, count=1, flags=re.S)
    return base


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--salida", type=Path, required=True)
    args = parser.parse_args()
    resultado = armar(args.base.read_text(encoding="utf-8"), ultimas.cargar_datos())
    if len(resultado.encode()) >= 512 * 1024:
        raise ValueError("El panel supera los 512 KB del chat")
    args.salida.write_text(resultado, encoding="utf-8")
    print(f"Panel de lectura actualizado: {args.salida} ({len(resultado.encode()):,} bytes)")


if __name__ == "__main__":
    main()
