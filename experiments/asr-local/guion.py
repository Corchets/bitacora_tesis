"""Guion de 30 frases del plan de voz real (#94): carga, verificación contra reglas.py, hoja de grabación.

`voz-real/guion.json` es la fuente: 6 bloques de 5 frases. De él sale `voz-real/HOJA-DE-GRABACION.md`
(`python guion.py --hoja`); no se edita a mano. `medir_voz_real.py` usa el guion para saber de qué
bloque es cada prueba y de qué tipo es cada frase; la medida en sí corre sobre «Lo que dije en
realidad», no sobre el guion.

Uso:
    python guion.py --verificar   # etiquetas y tipos del guion contra reglas.py
    python guion.py --hoja        # reescribe voz-real/HOJA-DE-GRABACION.md
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from wer import calcular_wer

DIR_ASR = Path(__file__).resolve().parent
DIR_VOZ_REAL = DIR_ASR / "voz-real"
GUION_POR_DEFECTO = DIR_VOZ_REAL / "guion.json"
HOJA_POR_DEFECTO = DIR_VOZ_REAL / "HOJA-DE-GRABACION.md"
DIR_REGLAS = DIR_ASR.parent / "slm-directo"

TIPOS = ("critica", "numeros", "bancos", "jerga", "negativa")
CANTIDAD_POR_TIPO = {"critica": 10, "numeros": 5, "bancos": 5, "jerga": 5, "negativa": 5}
NOMBRE_DE_TIPO = {
    "critica": "término crítico",
    "numeros": "números y montos",
    "bancos": "banco o app",
    "jerga": "jerga espontánea",
    "negativa": "negativa parecida",
}
SIMILITUD_MINIMA = 0.5  # una línea de la referencia se toma por una frase del guion desde acá


@dataclass(frozen=True)
class Frase:
    id: str
    bloque: int
    tipo: str
    texto: str
    etiquetas: tuple[str, ...]


@dataclass(frozen=True)
class Guion:
    frases: tuple[Frase, ...]

    def bloques(self) -> dict[int, list[Frase]]:
        porbloque: dict[int, list[Frase]] = {}
        for f in self.frases:
            porbloque.setdefault(f.bloque, []).append(f)
        return porbloque

    def por_id(self, id_frase: str) -> Frase:
        return next(f for f in self.frases if f.id == id_frase)


def cargar_guion(ruta: str | Path = GUION_POR_DEFECTO) -> Guion:
    datos = json.loads(Path(ruta).read_text(encoding="utf-8"))
    frases = [Frase(id=f["id"], bloque=b["id"], tipo=f["tipo"], texto=f["texto"], etiquetas=tuple(f["etiquetas"]))
              for b in datos["bloques"] for f in b["frases"]]
    return Guion(tuple(frases))


def _modulo_reglas() -> Any:
    if str(DIR_REGLAS) not in sys.path:
        sys.path.insert(0, str(DIR_REGLAS))
    import reglas

    return reglas


def verificar_guion(guion: Guion) -> list[str]:
    """Problemas del guion; lista vacía si está bien.

    Pide: 6 bloques de 5 frases con 30 ids distintos; 10/5/5/5/5 por tipo; que las negativas no den
    ninguna etiqueta en reglas.py; y que las otras 25 den exactamente las etiquetas anotadas, y al
    menos una.
    """
    reglas = _modulo_reglas()
    problemas: list[str] = []
    bloques = guion.bloques()
    if sorted(bloques) != [1, 2, 3, 4, 5, 6] or any(len(fs) != 5 for fs in bloques.values()):
        problemas.append("tiene que haber 6 bloques de 5 frases")
    if len({f.id for f in guion.frases}) != len(guion.frases):
        problemas.append("hay ids de frase repetidos")
    for tipo, cantidad in CANTIDAD_POR_TIPO.items():
        real = sum(f.tipo == tipo for f in guion.frases)
        if real != cantidad:
            problemas.append(f"tipo {tipo}: {real} frases, debería haber {cantidad}")
    for f in guion.frases:
        if f.tipo not in TIPOS:
            problemas.append(f"{f.id}: tipo desconocido {f.tipo!r}")
            continue
        reales = tuple(sorted(reglas.incendio_en(f.texto)))
        if f.tipo == "negativa" and reales:
            problemas.append(f"{f.id}: la negativa dispara {list(reales)} en reglas.py")
        elif f.tipo != "negativa" and not reales:
            problemas.append(f"{f.id}: no dispara ninguna etiqueta en reglas.py")
        if reales != tuple(sorted(f.etiquetas)):
            problemas.append(f"{f.id}: anotadas {list(f.etiquetas)}, reglas.py da {list(reales)}")
    return problemas


def _similitud(a: str, b: str) -> float:
    return max(0.0, 1.0 - calcular_wer(a, b, sin_tildes=True)["wer"])


def lineas_de_referencia(referencia: str) -> list[str]:
    """Una frase por línea; las líneas vacías no cuentan."""
    return [l.strip() for l in referencia.splitlines() if l.strip()]


def identificar_bloque(referencia: str, guion: Guion) -> dict[str, Any]:
    """De qué bloque del guion es una referencia, comparando cada línea con las 30 frases.

    Devuelve `bloque` (el que reúne más líneas; `None` si ninguna se parece), `exacto` (todas las
    líneas son las 5 frases del bloque), `lineas` (por cada línea: la frase más parecida, su
    similitud y su tipo, o `None` si no pasa de la similitud mínima) y `mezcla` si las líneas
    reconocidas vienen de más de un bloque.
    """
    lineas = lineas_de_referencia(referencia)
    detalle, votos = [], {}
    for texto in lineas:
        mejor = max(guion.frases, key=lambda f: _similitud(f.texto, texto))
        sim = round(_similitud(mejor.texto, texto), 3)
        if sim >= SIMILITUD_MINIMA:
            detalle.append({"texto": texto, "frase": mejor.id, "bloque": mejor.bloque, "tipo": mejor.tipo, "similitud": sim})
            votos.setdefault(mejor.bloque, []).append(sim)
        else:
            detalle.append({"texto": texto, "frase": None, "bloque": None, "tipo": None, "similitud": sim})
    bloque = max(votos, key=lambda b: (len(votos[b]), sum(votos[b]))) if votos else None
    exacto = (bloque is not None and len(lineas) == 5
              and [d["frase"] for d in detalle] == [f.id for f in guion.bloques()[bloque]]
              and all(d["similitud"] == 1.0 for d in detalle))
    return {"bloque": bloque, "exacto": exacto, "mezcla": len(votos) > 1,
            "reconocidas": sum(len(v) for v in votos.values()), "lineas": detalle}


def generar_hoja(guion: Guion) -> str:
    """La hoja de grabación en Markdown, lista para usar con el panel."""
    salida = [
        "# Hoja de grabación: ASR con voz real",
        "",
        "> Generada por `python guion.py --hoja` desde [`guion.json`](guion.json). No la edites a mano:",
        "> cambiá el guion y volvé a generarla. Plan: [`PLAN-VOZ-REAL.md`](../PLAN-VOZ-REAL.md), issue #94.",
        "> Es audio de voz real: queda fuera de Git (también el de otra persona, con su consentimiento anotado en el issue).",
        "",
        "## Qué grabar",
        "",
        "Son **2 tomas × 3 condiciones × 6 bloques = 36 grabaciones**, cada una de un bloque de 5 frases:",
        "",
        "| Condición | Voz | Cómo entra el audio |",
        "|---|---|---|",
        "| `luciano-microfono` | Luciano | micrófono del panel |",
        "| `luciano-meet` | Luciano | Luciano habla por Meet y el panel toma el audio de Meet (ver abajo) |",
        "| `otra-meet` | otra voz del equipo | igual que la anterior, con otra persona. Si no hay otra voz, alcanza con las dos de Luciano |",
        "",
        "La **toma 1** sirve para ajustar los hotwords y el diccionario; la **toma 2** es la que mide y decide",
        "(PLAN-VOZ-REAL.md §2). No ajustes nada mirando la toma 2. En las dos tomas usá el mismo cuarto, la misma",
        "máquina y el mismo micrófono, y no toques la ganancia entre una y otra.",
        "",
        "## Cómo grabar un bloque",
        "",
        "1. Abrí el panel y activá **Probar el ASR** (README de `experiments/voip`, §10). Dejá el corte en",
        "   **Automático** y el umbral en `0,005`: los otros valores se prueban después, offline, sobre lo guardado.",
        "2. Tocá **▶ Hablar** y leé las 5 frases del bloque con tu voz de siempre (con tu acento, sin actuar).",
        "   Una pausa corta, de un segundo y medio más o menos, entre frase y frase. Si te trabás, seguí; si el bloque",
        "   salió mal, **Borrar** y empezá el bloque de nuevo.",
        "3. **Terminar prueba**. En **Lo que dije en realidad** pegá el bloque de abajo, una frase por línea.",
        "   Si dijiste algo distinto, corregí esa línea para que diga lo que dijiste: la medida compara contra",
        "   eso, no contra el guion. Escribí los números con palabras, como están acá.",
        "4. **Guardar prueba**. Anotá el id de la prueba (lo ves en el Historial) en",
        "   [`pruebas.csv`](pruebas.csv) con la toma, la voz y la condición.",
        "",
        "### Condición Meet",
        "",
        "> **Estado: propuesta sin discutir.** «Probar el ASR» solo lee un micrófono del navegador, así que para que",
        "> entre el audio que pasó por Meet hay que elegir como micrófono del panel un dispositivo que lo reciba.",
        "> Una forma con lo que ya hay: la receta 2 de [`GUIA-MEET-WHATSAPP.md`](../../voip/GUIA-MEET-WHATSAPP.md)",
        "> (salida múltiple con BlackHole 2ch), eligiendo **BlackHole 2ch** como micrófono del panel mientras vos (o la otra",
        "> persona) hablan por Meet desde el celular. Ajustalo si preferís otro camino, pero que las tomas 1 y 2 usen el mismo.",
        "",
        "## Bloques para copiar y pegar",
        "",
        "Cada bloque va tal cual en **Lo que dije en realidad**.",
        "",
    ]
    for numero, frases in guion.bloques().items():
        salida += [f"### Bloque {numero}", "", "```text", *[f.texto for f in frases], "```", ""]
    salida += [
        "## Qué mide cada frase",
        "",
        "| Bloque | Frase | Tipo | Etiquetas de `reglas.py` sobre el guion |",
        "|---|---|---|---|",
    ]
    for f in guion.frases:
        etiquetas = ", ".join(f"`{e}`" for e in f.etiquetas) or "ninguna (debe quedar sin etiquetas)"
        salida.append(f"| {f.bloque} | {f.id} | {NOMBRE_DE_TIPO[f.tipo]} | {etiquetas} |")
    salida += [
        "",
        "Las 5 negativas se parecen a términos críticos («cómodo», «codo», «número») y **no** deben disparar nada.",
        "Dos ejemplos del plan salieron del guion porque `reglas.py` sí los dispara: «pagó la luz» (la regla busca el",
        "texto `pago`) y «el link del cumple» (`link`). «Mercado Pago» también dispara `REQUEST_TRANSFER` por la",
        f"misma razón; está en la frase `{', '.join(f.id for f in guion.frases if 'Mercado Pago' in f.texto)}` a propósito.",
        "",
        "Cuando termines, completá [`pruebas.csv`](pruebas.csv) y corré la medición:",
        "ver «Cómo correrlo» en [`PLAN-VOZ-REAL.md`](../PLAN-VOZ-REAL.md#cómo-correrlo).",
        "",
    ]
    return "\n".join(salida)


def main() -> None:
    p = argparse.ArgumentParser(description="Guion de voz real: verificación y hoja de grabación.")
    p.add_argument("--guion", default=str(GUION_POR_DEFECTO))
    p.add_argument("--verificar", action="store_true", help="comprueba el guion contra reglas.py")
    p.add_argument("--hoja", action="store_true", help="reescribe HOJA-DE-GRABACION.md")
    args = p.parse_args()
    guion = cargar_guion(args.guion)
    if args.verificar or not args.hoja:
        problemas = verificar_guion(guion)
        print("\n".join(problemas) if problemas else f"Guion en orden: {len(guion.frases)} frases.")
        if problemas:
            raise SystemExit(1)
    if args.hoja:
        HOJA_POR_DEFECTO.write_text(generar_hoja(guion), encoding="utf-8")
        print(f"Escribí {HOJA_POR_DEFECTO}")


if __name__ == "__main__":
    main()
