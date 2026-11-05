"""Convierte GUIA-MEET-WHATSAPP.md en la página que el panel sirve en /guia.

El Markdown sigue siendo la única fuente: acá solo se le da forma de página, sin dependencias.
Alcanza el subconjunto que usa la guía: título en la primera línea, `##`, listas numeradas y con
guion (con renglones de continuación), párrafos, **negrita**, *cursiva*, `código` y enlaces.
Los encabezados «Si falla:» y «Comprobación:» se muestran como recuadros propios.
"""

from __future__ import annotations

import html
import re

_ENLACE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")


def _en_linea(texto: str) -> str:
    """Formato dentro de un renglón; el texto se escapa antes de agregar etiquetas."""
    partes = re.split(r"(`[^`]+`)", texto)
    salida = []
    for parte in partes:
        if parte.startswith("`") and parte.endswith("`") and len(parte) > 1:
            salida.append(f"<code>{html.escape(parte[1:-1])}</code>")
            continue
        p = html.escape(parte, quote=False)
        p = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", p)
        p = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", p)
        p = _ENLACE.sub(lambda m: _enlace(m.group(1), m.group(2)), p)
        salida.append(p)
    return "".join(salida)


def _mayuscula(texto: str) -> str:
    return texto[:1].upper() + texto[1:]


def _enlace(texto: str, destino: str) -> str:
    # El README no se sirve desde el panel: el enlace relativo queda como texto.
    if not destino.startswith(("http://", "https://")):
        return f"<span class=\"ref\">{texto}</span>"
    return f'<a href="{html.escape(destino)}" target="_blank" rel="noopener">{texto}</a>'


def _bloques(lineas: list[str]) -> list[tuple[str, list[str]]]:
    """Agrupa renglones en bloques: ('h2', …), ('ol', ítems), ('ul', ítems) o ('p', renglones)."""
    bloques: list[tuple[str, list[str]]] = []
    for linea in lineas:
        crudo = linea.rstrip()
        if not crudo:
            bloques.append(("", []))
            continue
        if crudo.startswith("## "):
            bloques.append(("h2", [crudo[3:]]))
        elif m := re.match(r"^\d+\.\s+(.*)", crudo):
            if not bloques or bloques[-1][0] != "ol":
                bloques.append(("ol", []))
            bloques[-1][1].append(m.group(1))
        elif crudo.startswith("- "):
            if not bloques or bloques[-1][0] != "ul":
                bloques.append(("ul", []))
            bloques[-1][1].append(crudo[2:])
        elif crudo.startswith(" ") and bloques and bloques[-1][0] in ("ol", "ul"):
            bloques[-1][1][-1] += " " + crudo.strip()
        elif bloques and bloques[-1][0] == "p":
            bloques[-1][1].append(crudo)
        else:
            bloques.append(("p", [crudo]))
    return [b for b in bloques if b[0]]


def a_html(markdown: str) -> str:
    lineas = markdown.splitlines()
    titulo = lineas[0].strip()
    nombre, _, subtitulo = titulo.partition(" · ")  # «GUÍA · <título>»: se muestra solo el título
    cuerpo: list[str] = []
    recuadro: str | None = None  # 'falla' o 'ok' mientras se arma un recuadro
    pendiente: list[str] = []

    def cerrar_recuadro():
        nonlocal recuadro
        if recuadro:
            cuerpo.append("</div>")
            recuadro = None

    for tipo, contenido in _bloques(lineas[1:]):
        if tipo == "h2":
            cerrar_recuadro()
            if pendiente:
                cuerpo.append("</section>")
            pendiente = [contenido[0]]
            receta, _, resto = contenido[0].partition(" · ")
            cuerpo.append(f'<section class="receta"><h2><span class="num">{_en_linea(receta)}</span>'
                          f'{_en_linea(resto or receta)}</h2>')
        elif tipo == "p":
            texto = " ".join(contenido)
            if texto.strip() == "Si falla:":
                cerrar_recuadro()
                recuadro = "falla"
                cuerpo.append('<div class="recuadro falla"><h3>Si falla</h3>')
            elif texto.startswith("**Comprobación:**"):
                cerrar_recuadro()
                cuerpo.append(f'<div class="recuadro ok"><h3>Comprobación</h3><p>'
                              f'{_en_linea(_mayuscula(texto.removeprefix("**Comprobación:**").strip()))}</p></div>')
            else:
                cerrar_recuadro()
                cuerpo.append(f"<p>{_en_linea(texto)}</p>")
        else:
            items = "".join(f"<li>{_en_linea(i)}</li>" for i in contenido)
            cuerpo.append(f'<{tipo} class="{"pasos" if tipo == "ol" else "lista"}">{items}</{tipo}>')
            if tipo == "ul" and recuadro:
                cerrar_recuadro()
    cerrar_recuadro()
    if pendiente:
        cuerpo.append("</section>")
    return _PLANTILLA.format(titulo=html.escape(subtitulo or nombre), subtitulo=_en_linea(subtitulo or nombre),
                             cuerpo="\n".join(cuerpo))


_PLANTILLA = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titulo}</title>
<style>
  :root {{
    --fondo: #f8fafc; --superficie: #ffffff; --linea: #cbd5e1; --tinta: #0f172a;
    --tinta-secundaria: #334155; --mu: #64748b; --primary: #1d4ed8; --primary-bg: #eff6ff;
    --alerta: #b91c1c; --alerta-fondo: #fef2f2; --alerta-borde: #fca5a5;
    --ok: #15803d; --ok-fondo: #f0fdf4; --ok-borde: #86efac;
    accent-color: var(--primary);
  }}
  * {{ box-sizing: border-box; }}
  ::selection {{ background: #93c5fd; color: var(--tinta); }}
  body {{ margin: 0; background: var(--fondo); color: var(--tinta);
    font: 16px/1.6 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
  .hoja {{ max-width: 46rem; margin: 0 auto; padding: 2.5rem 1.5rem 4rem; }}
  .volver {{ display: inline-flex; align-items: center; gap: .35rem; font-size: .875rem; font-weight: 600;
    color: var(--primary); text-decoration: none; }}
  .volver:hover {{ text-decoration: underline; text-underline-offset: 3px; }}
  header {{ margin: 1.25rem 0 2rem; }}
  h1 {{ font-size: 2rem; line-height: 1.15; letter-spacing: -0.02em; margin: 0; text-wrap: balance; }}
  .intro > p {{ color: var(--tinta-secundaria); margin: 0 0 .9rem; max-width: 65ch; }}
  .intro > p:nth-of-type(2) {{ background: var(--primary-bg); border: 1px solid #bfdbfe; border-radius: 10px;
    padding: .85rem 1rem; color: var(--tinta); }}
  .receta {{ background: var(--superficie); border: 1px solid var(--linea); border-radius: 14px;
    padding: 1.5rem 1.6rem 1.25rem; margin-top: 2rem; box-shadow: 0 1px 2px rgb(15 23 42 / .04), 0 6px 18px -8px rgb(15 23 42 / .12); }}
  .receta h2 {{ font-size: 1.375rem; line-height: 1.25; margin: 0 0 1rem; display: flex; flex-direction: column; gap: .2rem; text-wrap: balance; }}
  .receta h2 .num {{ font-size: .8125rem; font-weight: 700; color: var(--primary); }}
  .receta > p {{ color: var(--tinta-secundaria); max-width: 65ch; }}
  ol.pasos {{ list-style: none; counter-reset: paso; padding: 0; margin: 1rem 0; display: grid; gap: .85rem; }}
  ol.pasos li {{ counter-increment: paso; position: relative; padding-left: 2.6rem; min-height: 1.9rem; }}
  ol.pasos li::before {{ content: counter(paso); position: absolute; left: 0; top: .05rem; width: 1.75rem; height: 1.75rem;
    border-radius: 50%; background: var(--primary); color: #fff; font-weight: 700; font-size: .875rem;
    display: grid; place-items: center; font-variant-numeric: tabular-nums; }}
  ul.lista {{ margin: .4rem 0 0; padding-left: 1.15rem; display: grid; gap: .55rem; }}
  .recuadro {{ border-radius: 10px; padding: .85rem 1.1rem; margin: 1.1rem 0 .4rem; border: 1px solid; }}
  .recuadro h3 {{ margin: 0 0 .35rem; font-size: .9375rem; }}
  .recuadro p {{ margin: 0; }}
  .recuadro.ok {{ background: var(--ok-fondo); border-color: var(--ok-borde); }}
  .recuadro.ok h3 {{ color: var(--ok); }}
  .recuadro.falla {{ background: var(--alerta-fondo); border-color: var(--alerta-borde); }}
  .recuadro.falla h3 {{ color: var(--alerta); }}
  code {{ font: .875em ui-monospace, SFMono-Regular, Menlo, monospace; background: #e2e8f0; border-radius: 4px;
    padding: .1rem .35rem; overflow-wrap: anywhere; }}
  strong {{ font-weight: 700; }}
  a {{ color: var(--primary); text-underline-offset: 3px; }}
  a:focus-visible {{ outline: 2px solid var(--primary); outline-offset: 2px; border-radius: 2px; }}
  .ref {{ font-weight: 600; }}
  @media (max-width: 600px) {{ .hoja {{ padding: 1.5rem 1rem 3rem; }} .receta {{ padding: 1.15rem 1rem; }} h1 {{ font-size: 1.6rem; }} }}
</style>
</head>
<body>
<main class="hoja">
  <a class="volver" href="/">← Volver al panel</a>
  <header>
    <h1>{subtitulo}</h1>
  </header>
  <div class="intro">
  {cuerpo}
  </div>
</main>
</body>
</html>
"""
