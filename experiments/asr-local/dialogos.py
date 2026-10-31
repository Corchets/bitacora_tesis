"""Diálogos de voz real para elegir el corte de Parakeet (#94, PLAN-VOZ-REAL.md §12.9).

`voz-real/dialogos.json` es la fuente: cuatro llamadas con líneas para «otra» (habla por Meet) y
«protegida» (habla por el micrófono de la notebook). De él sale `voz-real/HOJA-DIALOGOS.md`
(`python dialogos.py --hoja`); no se edita a mano. `medir_voz_real.py` toma de acá la referencia de
cada canal de una llamada: las líneas de ese rol, en orden.

Uso:
    python dialogos.py --verificar   # etiquetas y tipos contra reglas.py
    python dialogos.py --hoja        # reescribe voz-real/HOJA-DIALOGOS.md
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DIR_ASR = Path(__file__).resolve().parent
DIR_VOZ_REAL = DIR_ASR / "voz-real"
DIALOGOS_POR_DEFECTO = DIR_VOZ_REAL / "dialogos.json"
HOJA_POR_DEFECTO = DIR_VOZ_REAL / "HOJA-DIALOGOS.md"
DIR_REGLAS = DIR_ASR.parent / "slm-directo"

ROLES = ("otra", "protegida")
TIPOS = ("critica", "numeros", "bancos", "jerga", "negativa", "charla", "corta")
SIN_ETIQUETAS = ("negativa", "corta")  # tienen que quedar sin etiquetas en reglas.py
NOMBRE_DE_ROL = {"otra": "Otra persona (por Meet)", "protegida": "Persona protegida (en la notebook)"}


@dataclass(frozen=True)
class Linea:
    id: str
    rol: str
    tipo: str
    texto: str
    etiquetas: tuple[str, ...]


@dataclass(frozen=True)
class Dialogo:
    id: str
    clase: str
    titulo: str
    lineas: tuple[Linea, ...]

    def del_rol(self, rol: str) -> list[Linea]:
        return [l for l in self.lineas if l.rol == rol]


def cargar_dialogos(ruta: str | Path = DIALOGOS_POR_DEFECTO) -> dict[str, Dialogo]:
    datos = json.loads(Path(ruta).read_text(encoding="utf-8"))
    return {d["id"]: Dialogo(d["id"], d["clase"], d["titulo"], tuple(
        Linea(l["id"], l["rol"], l["tipo"], l["texto"], tuple(l["etiquetas"])) for l in d["lineas"]))
        for d in datos["dialogos"]}


def _modulo_reglas() -> Any:
    if str(DIR_REGLAS) not in sys.path:
        sys.path.insert(0, str(DIR_REGLAS))
    import reglas

    return reglas


def verificar_dialogos(dialogos: dict[str, Dialogo]) -> list[str]:
    """Problemas de los diálogos; lista vacía si están bien.

    Pide ids de línea distintos, roles y tipos conocidos, las dos voces en cada diálogo, que las
    negativas y las respuestas cortas no den etiquetas y que las anotadas sean las de reglas.py.
    """
    reglas = _modulo_reglas()
    problemas: list[str] = []
    ids = [l.id for d in dialogos.values() for l in d.lineas]
    if len(set(ids)) != len(ids):
        problemas.append("hay ids de línea repetidos")
    for d in dialogos.values():
        if d.clase not in ("estafa", "legitima"):
            problemas.append(f"{d.id}: clase desconocida {d.clase!r}")
        if any(not d.del_rol(r) for r in ROLES):
            problemas.append(f"{d.id}: tiene que haber líneas de las dos personas")
        for l in d.lineas:
            if l.rol not in ROLES:
                problemas.append(f"{l.id}: rol desconocido {l.rol!r}")
            if l.tipo not in TIPOS:
                problemas.append(f"{l.id}: tipo desconocido {l.tipo!r}")
            reales = tuple(sorted(reglas.incendio_en(l.texto)))
            if l.tipo in SIN_ETIQUETAS and reales:
                problemas.append(f"{l.id}: la línea {l.tipo} dispara {list(reales)} en reglas.py")
            if reales != tuple(sorted(l.etiquetas)):
                problemas.append(f"{l.id}: anotadas {list(l.etiquetas)}, reglas.py da {list(reales)}")
    return problemas


def referencia_del_canal(dialogo: Dialogo, canal: str) -> tuple[list[str], list[str]]:
    """(textos, tipos) de las líneas que dijo quien está en ese canal, en orden."""
    lineas = dialogo.del_rol(canal)
    return [l.texto for l in lineas], [l.tipo for l in lineas]


def generar_hoja(dialogos: dict[str, Dialogo]) -> str:
    """La hoja para hacer las llamadas, en Markdown."""
    salida = [
        "# Hoja de diálogos: elegir el corte de Parakeet",
        "",
        "> Generada por `python dialogos.py --hoja` desde [`dialogos.json`](dialogos.json). No la edites a mano.",
        "> Plan: [`PLAN-VOZ-REAL.md`](../PLAN-VOZ-REAL.md#129-dos-candidatos-para-comparar-en-diálogos-reales-2026-10-30), issue #94.",
        "> Es audio de voz real: queda fuera de Git. La otra persona da su consentimiento y queda anotado en #94.",
        "",
        "## Qué grabar",
        "",
        "Cinco llamadas por Meet: los cuatro diálogos y **D1 otra vez con la tele prendida** de fondo, del lado",
        "de la notebook. Si pueden, después cambian de lugar y repiten los cuatro: así cada voz pasa por los dos",
        "canales. Cada llamada se graba una sola vez; las dos opciones de corte se comparan después sobre el mismo audio.",
        "",
        "## Antes de empezar",
        "",
        "1. Los dos con **auriculares**: si el audio de Meet sale por los parlantes, el micrófono de la notebook",
        "   lo vuelve a tomar y las voces se mezclan.",
        "2. En el panel: modo llamada, **Persona protegida = micrófono** (con cancelación de eco) y",
        "   **Otra persona = pestaña de Meet** con «Compartir audio».",
        "3. Modelo de ASR **Parakeet**, con `parakeet-filtro` o `parakeet-silero`, y la misma toda la sesión: lo que",
        "   se ve en pantalla puede cambiar cómo hablan. El audio guardado no depende de esa opción.",
        "",
        "## Cómo hacer cada llamada",
        "",
        "1. Iniciá la llamada en el panel y esperá a que suban los dos medidores.",
        "2. Cada uno lee **solo sus líneas**, a ritmo de charla: contestá apenas termina el otro, sin esperar.",
        "   Con tu acento y tu forma de hablar, sin actuar. Si se pisan un poco no pasa nada: cada voz va por su canal.",
        "3. Si te trabás, seguí. Si cambiaste una palabra, anotala en la `nota` de la fila. Si la llamada salió",
        "   muy mal, terminala y hacela de nuevo.",
        "4. Terminá la llamada. Copiá el id del Historial y agregá **dos filas** a [`pruebas.csv`](pruebas.csv),",
        "   una por canal:",
        "",
        "```text",
        "2026-11-02_101500-123456,5,luciano,dialogo,D1,protegida,",
        "2026-11-02_101500-123456,5,otra,dialogo,D1,otra,",
        "```",
        "",
        "La llamada con la tele va con la condición `dialogo-tv`. Si cambiaron de lugar, cambia la columna `voz`",
        "(quién estaba en ese canal); las líneas siguen el canal: quien está en la notebook lee las de la protegida.",
        "",
    ]
    for d in dialogos.values():
        clase = "estafa" if d.clase == "estafa" else "legítima"
        salida += [f"## {d.id} · {d.titulo} ({clase})", ""]
        for l in d.lineas:
            quien = "**Otra**" if l.rol == "otra" else "**Protegida**"
            salida.append(f"- {quien}: {l.texto}")
        salida.append("")
    salida += [
        "## Qué mide cada línea",
        "",
        "| Línea | Quién | Tipo | Etiquetas de `reglas.py` sobre el texto |",
        "|---|---|---|---|",
    ]
    for d in dialogos.values():
        for l in d.lineas:
            etiquetas = ", ".join(f"`{e}`" for e in l.etiquetas) or "ninguna"
            salida.append(f"| {l.id} | {l.rol} | {l.tipo} | {etiquetas} |")
    salida += [
        "",
        "Las negativas y las respuestas cortas («Sí, obvio», «Ya abrió») no tienen que disparar nada. D3 es",
        "una charla legítima con palabras parecidas a las de una estafa («número de la casa», «codo», «abonó la luz»).",
        "",
    ]
    return "\n".join(salida)


def main() -> None:
    p = argparse.ArgumentParser(description="Diálogos de voz real: verificación y hoja para las llamadas.")
    p.add_argument("--dialogos", default=str(DIALOGOS_POR_DEFECTO))
    p.add_argument("--verificar", action="store_true", help="comprueba los diálogos contra reglas.py")
    p.add_argument("--hoja", action="store_true", help="reescribe HOJA-DIALOGOS.md")
    args = p.parse_args()
    dialogos = cargar_dialogos(args.dialogos)
    if args.verificar or not args.hoja:
        problemas = verificar_dialogos(dialogos)
        total = sum(len(d.lineas) for d in dialogos.values())
        print("\n".join(problemas) if problemas else f"Diálogos en orden: {len(dialogos)} diálogos, {total} líneas.")
        if problemas:
            raise SystemExit(1)
    if args.hoja:
        HOJA_POR_DEFECTO.write_text(generar_hoja(dialogos), encoding="utf-8")
        print(f"Escribí {HOJA_POR_DEFECTO}")


if __name__ == "__main__":
    main()
