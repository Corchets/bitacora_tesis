"""Paso 1: ¿se puede prellenar `{\\n  "riesgo":` con este llama-server sin cambiar los tokens ni perder la caché?

Sobre una conversación de desarrollo, línea por línea de OTRA, compara tres formas de pedir lo mismo:

- `chat`: la de hoy (`/v1/chat/completions`, gramática del JSON entero, 14 tokens).
- `numero`: `/apply-template` + prefijo, a `/completion`, con la gramática `space number ","`.
- `asistente`: `/v1/chat/completions` con un mensaje `assistant` final que lleva el prefijo.

Y mira, con `/tokenize` y `return_tokens`, si el prefijo escrito por nosotros son los mismos tokens que hoy genera
el modelo. Imprime un JSON; no escribe archivos.

    python3 -I probar_prefijo.py > prefijo.json   (con llama-server en 127.0.0.1:18080)
"""
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SLM = AQUI.parents[1]
sys.path.insert(0, str(SLM))
from casos import Linea  # noqa: E402
from correr_android_congelada import gramatica  # noqa: E402
from correr_android_latencia import PREFIJOS, _post, gramatica_numero  # noqa: E402
from detectores import DetectorSLMCorteRiesgo, cargar_prompt, esquema_de  # noqa: E402

PROMPT = "c-consejos-corte-riesgo"
CASO = "CV2-D-V-BANCO-002"
PREFIJO = PREFIJOS["salto"]
SIN_PENSAR = {"chat_template_kwargs": {"enable_thinking": False}}
COMUN = {"temperature": 0, "seed": 42}
CAMPOS = ("cache_n", "prompt_n", "predicted_n", "prompt_ms", "predicted_ms")


def main():
    datos = json.loads((AQUI.parent / "2026-11-11_a56-latencia-172" / "conversaciones-sub-6.json").read_text())
    esquema = esquema_de(PROMPT)
    detector = DetectorSLMCorteRiesgo(None, "", cargar_prompt(PROMPT), "rol", 4096, 42, esquema=esquema)
    salida = {"prefijo": PREFIJO, "prefijo_tokens": _post("/tokenize", {"content": PREFIJO, "with_pieces": True})["tokens"],
              "lineas": []}
    lineas = []
    for r in datos["casos"][CASO]:
        lineas.append(Linea(r["hablante"], r["texto"]))
        if r["hablante"] != "OTRA":
            continue
        mensajes, _ = detector.mensajes(tuple(lineas))
        plantilla = _post("/apply-template", {"messages": mensajes, **SIN_PENSAR})["prompt"]
        fila = {"linea": r["n"], "fin_de_plantilla": plantilla[-40:]}
        # Cada forma corre dos veces seguidas: la primera con la caché que dejó la forma anterior, la segunda con la suya.
        for nombre in ("chat", "numero", "asistente", "chat"):
            for vez in (1, 2):
                if nombre == "chat":
                    s = _post("/v1/chat/completions", {"messages": mensajes, "max_tokens": 14, "grammar": gramatica(esquema),
                                                       **COMUN, **SIN_PENSAR})
                    texto, t = s["choices"][0]["message"]["content"], s["timings"]
                elif nombre == "numero":
                    s = _post("/completion", {"prompt": plantilla + PREFIJO, "n_predict": 14, "grammar": gramatica_numero(),
                                              "cache_prompt": True, "return_tokens": True, **COMUN})
                    texto, t = s["content"], s["timings"]
                    fila["numero_tokens"] = s.get("tokens")
                else:
                    try:
                        s = _post("/v1/chat/completions", {
                            "messages": mensajes + [{"role": "assistant", "content": PREFIJO}], "max_tokens": 14,
                            "grammar": gramatica_numero(), **COMUN, **SIN_PENSAR})
                        texto, t = s["choices"][0]["message"]["content"], s["timings"]
                    except Exception as e:  # noqa: BLE001
                        texto, t = f"ERROR {e}", {}
                fila.setdefault(nombre, []).append({"texto": texto, **{c: t.get(c) for c in CAMPOS}})
        # Lo que hoy genera el modelo, token por token: el mismo prompt por /completion con la gramática entera.
        s = _post("/completion", {"prompt": plantilla, "n_predict": 14, "grammar": gramatica(esquema),
                                  "cache_prompt": True, "return_tokens": True, **COMUN})
        fila["hoy_por_completion"] = {"texto": s["content"], "tokens": s.get("tokens")}
        salida["lineas"].append(fila)
    json.dump(salida, sys.stdout, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
