"""Arma una página para ver una o varias corridas como si la llamada estuviera ocurriendo.

Uso:
    python visor.py corridas/<carpeta> [corridas/<otra> ...] [--abrir]

Escribe visor.html en la carpeta de la primera corrida (o en --salida) y, con --abrir,
lo abre en el navegador. Es un archivo autocontenido: se puede mandar por mensaje o
abrir sin conexión (sin conexión usa las fuentes del sistema).

Muestra, línea por línea, el texto disponible, la respuesta del detector (riesgo,
alerta, motivo, evidencia y la respuesta cruda del modelo) y dónde salió el aviso.
La referencia humana (T_R, T_C) se puede ocultar: es para evaluar, el detector no la ve.
"""

from __future__ import annotations

import argparse
import json
import sys
import webbrowser
from pathlib import Path

import casos
import resumen

PLANTILLA = Path(__file__).resolve().parent / "visor_plantilla.html"


def _num(valor: str):
    return None if valor in ("", None) else float(valor)


def _bool(valor: str):
    return None if valor in ("", None) else valor == "true"


def datos_de_corridas(carpetas: list[Path]) -> dict:
    """Todo lo que la página necesita, ya calculado con la misma lógica que resumen.py."""
    corridas, configs, resultados, metricas = [], [], {}, {}
    ids: set[str] = set()
    for carpeta in carpetas:
        manifiesto, filas = resumen.leer_corrida(carpeta)
        analisis = resumen.analizar(manifiesto, filas)
        corridas.append(
            {
                "nombre": carpeta.name,
                "comando": manifiesto["comando"],
                "inicio": manifiesto["inicio"],
                "interrumpida": manifiesto["interrumpida"],
                "commit": resumen.commit_corto(manifiesto["codigo"]["commit"]),
                "maquina": manifiesto["maquina"],
                "ollama": (manifiesto.get("ollama") or {}).get("version"),
                "modelos": manifiesto.get("modelos", {}),
            }
        )
        por_config: dict[str, dict[str, list]] = {}
        for fila in filas:
            por_config.setdefault(fila["config"], {}).setdefault(fila["case_id"], []).append(fila)
        for config, cs in analisis.items():
            nombre = config if config not in resultados else f"{config} ({carpeta.name})"
            configs.append({"id": nombre, "corrida": carpeta.name, "detector": "reglas" if config == "reglas" else "slm"})
            metricas[nombre] = resumen.metricas(cs)
            # Mismo texto que resumen.md, para que los dos muestren el mismo número.
            metricas[nombre]["ms_p50_texto"] = resumen._ms(metricas[nombre]["ms_p50"])
            resultados[nombre] = {}
            for case_id, c in cs.items():
                ids.add(case_id)
                por_linea: dict[int, dict] = {}
                for f in por_config[config][case_id]:
                    por_linea.setdefault(int(f["linea"]), f)  # igual que resumen.analizar
                actualizaciones = [por_linea[n] for n in sorted(por_linea)]
                resultados[nombre][case_id] = {
                    "aviso": c["aviso"],
                    "categoria": c["categoria"],
                    "codigo": resumen.CODIGOS[c["categoria"]],
                    "completo": c["completo"],
                    "lineas": [
                        {
                            "valida": f["valida"] == "true",
                            "error": f["error"],
                            "riesgo": _num(f["riesgo"]),
                            "alerta": _bool(f["alerta_sugerida"]),
                            "motivo": f["motivo"],
                            "evidencia": f["evidencia"],
                            "textual": _bool(f["evidencia_en_texto"]),
                            "ms": _num(f["ms"]),
                            "crudo": f["crudo"],
                        }
                        for f in actualizaciones
                    ],
                }
    datos_casos = {}
    for case_id in sorted(ids):
        ref = casos.cargar_referencia(case_id)
        datos_casos[case_id] = {
            "grupo": ref["grupo"],
            "clase": ref["clase"],
            "t_r": ref["t_r_linea"],
            "t_c": ref["t_c_linea"],
            "pedido": ref["pedido"],
            "que_prueba": ref["que_prueba"],
            "notas": ref["notas"],
            "revision_humana": ref["revision_humana"],
            "lineas": [{"h": l.hablante, "t": l.texto} for l in casos.cargar_texto(case_id)],
        }
    return {"corridas": corridas, "configs": configs, "metricas": metricas, "resultados": resultados, "casos": datos_casos}


def armar_html(datos: dict, documento_completo: bool = True) -> str:
    """Inserta los datos en la plantilla. Sin documento completo, deja solo el contenido
    (para publicarlo en un sitio que agrega su propio <html>, <head> y <body>)."""
    plantilla = PLANTILLA.read_text(encoding="utf-8")
    # Sin ningún "<" literal, el texto de los datos no puede cerrar ni alterar el <script>.
    # Es JSON válido: "<" solo aparece dentro de cadenas y JSON.parse lo decodifica.
    carga = json.dumps(datos, ensure_ascii=False).replace("<", "\\u003c")
    contenido = plantilla.replace("/*__DATOS__*/null", carga)
    if not documento_completo:
        return contenido
    return (
        '<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        "</head>\n<body>\n" + contenido + "\n</body>\n</html>\n"
    )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("carpetas", type=Path, nargs="+", help="una o más carpetas de corridas/")
    p.add_argument("--salida", type=Path, help="archivo HTML a escribir (por defecto, <primera carpeta>/visor.html)")
    p.add_argument("--abrir", action="store_true", help="abrir el visor en el navegador")
    p.add_argument("--solo-contenido", action="store_true", help=argparse.SUPPRESS)
    args = p.parse_args(argv)
    for carpeta in args.carpetas:
        if not (carpeta / "actualizaciones.csv").exists():
            sys.exit(f"{carpeta} no parece una corrida: falta actualizaciones.csv")
    datos = datos_de_corridas(args.carpetas)
    if not datos["casos"]:
        sys.exit("Las corridas no tienen ninguna conversación procesada: no hay nada que mostrar.")
    salida = args.salida or args.carpetas[0] / "visor.html"
    salida.write_text(armar_html(datos, not args.solo_contenido), encoding="utf-8")
    print(f"Visor: {salida}")
    if args.abrir:
        webbrowser.open(salida.resolve().as_uri())
    return 0


if __name__ == "__main__":
    sys.exit(main())
