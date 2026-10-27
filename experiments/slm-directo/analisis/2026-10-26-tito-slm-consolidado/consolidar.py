"""Consolidación del experimento Tito→SLM (#74, parte de #68).

Verifica cobertura y audita las seis corridas canónicas desde las salidas
crudas, sin nueva inferencia: no llama a Ollama ni reentrena nada.

Uso, desde experiments/slm-directo/:
    python analisis/2026-10-26-tito-slm-consolidado/consolidar.py
    bash analisis/2026-10-26-tito-slm-consolidado/regenerar.sh   # re-verifica todo

Salidas (en esta misma carpeta):
    cobertura.json  manifiesto de cobertura, digests, hashes y agregados
    TABLAS.md       tablas cruzadas por modelo (generado, no editar a mano)
"""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))
import casos  # noqa: E402

CARPETA = Path(__file__).resolve().parent
CORRIDAS = RAIZ / "corridas"

# Seis artefactos de #68: tag exacto -> digest histórico esperado.
# Llama no tiene digest histórico: se registra el recuperado sin afirmar
# identidad con el artefacto de la cascada (#68, #73).
ESPERADOS = {
    "2026-10-26_133838_qwen4b-comparacion": (
        "qwen3.5:4b-q4_K_M", "d8b0f5e9760cd1682034f292d7ef72ec46f432149be0df7574bf2d6e92e38c04"),
    "2026-10-26_135518_qwen08b-q8-comparacion": (
        "qwen3.5:0.8b-q8_0", "7c00f78aed0fd757e9ba2f2720896768fd22da24b7fb6fe17096bb1e85bb2d25"),
    "2026-10-26_135640_qwen08b-comparacion": (
        "qwen3.5:0.8b", "de63045f29755d4721c09d54c9b45c2dadb644f4fd7d604d4cac90d96049971c"),
    "2026-10-26_135746_qwen2b-q8-comparacion": (
        # NOTA: la tabla de #68 trae este digest truncado a 62 hex (omite "a3"
        # tras "…ade63"); aquí va el digest completo de 64 hex informado por
        # Ollama en el manifiesto. La discrepancia queda registrada en
        # CONSOLIDADO.md; no se edita #68 desde este ticket.
        "qwen3.5:2b-q8_0", "0689d44085e06d165161a8a9a1731344278cfb5aade63a3c3dbdb48ab54b130a"),
    "2026-10-26_135930_qwen9b-comparacion": (
        "qwen3.5:9b-q4_K_M", "56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90"),
    "2026-10-26_141023_llama1b-comparacion": (
        "llama3.2:1b-instruct-q4_K_M", "22bc6b92eb0160c4629782fca05a9032c59d306ab2058b7dacc8a4644fbafa02"),
}

# Corrida superada: Tito falló con ModuleNotFoundError en las 105 líneas
# filtradas (fail-open: SLM consultado siempre, 0 evitadas). No integra
# la matriz; se conserva como evidencia del camino fail-open.
SUPERADA = "2026-10-26_132916_qwen4b-comparacion"

VISHING = [
    "TR-04-pedido-tras-charla-larga",
    "TR-07-pedido-partido-en-dos-lineas",
    "SC-SOPORTE-REMOTO-01-e01",
    "SC-FAMILIAR-DINERO-01-e01",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def leer_csv(corrida: Path) -> list[dict]:
    with open(corrida / "actualizaciones.csv", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def main() -> None:
    errores: list[str] = []
    modelos = {}
    for nombre, (modelo, digest) in ESPERADOS.items():
        corrida = CORRIDAS / nombre
        manifiesto = json.loads((corrida / "manifiesto.json").read_text())
        filas = leer_csv(corrida)

        cfgs = sorted({r["config"] for r in filas})
        directo = f"slm|{modelo}|tarea|ab"
        filtrado = f"tito-slm|{modelo}|tarea|ab"
        if cfgs != [directo, filtrado]:
            errores.append(f"{nombre}: configs {cfgs}")

        got = (manifiesto.get("ollama", {}).get("digests", {}).get(modelo))
        if got != digest:
            errores.append(f"{nombre}: digest {got} != esperado")

        # Sin alias duplicados: solo el tag exacto de la tabla de #68.
        otros = {c.split("|")[1] for c in cfgs} - {modelo}
        if otros:
            errores.append(f"{nombre}: tags inesperados {otros}")

        p = manifiesto.get("parametros_slm", {})
        cond = (
            manifiesto.get("prompts", {}).keys() == {"tarea"}
            and p.get("seed") == 42 and p.get("temperatura") == 0.0
            and p.get("num_ctx") == 4096
            and manifiesto.get("filtro_tito", {}).get("umbral") == 0.5
            and str(manifiesto.get("filtro_tito", {}).get("tito", "")).startswith("real-")
        )
        if not cond:
            errores.append(f"{nombre}: condiciones comunes distintas de #68")

        casos_man = manifiesto.get("casos", {})
        if len(casos_man) != 8:
            errores.append(f"{nombre}: {len(casos_man)} casos != 8")

        por_cfg: dict[str, dict] = {}
        for cfg in (directo, filtrado):
            fs = [r for r in filas if r["config"] == cfg]
            por_caso: dict[str, list[dict]] = {}
            for r in fs:
                por_caso.setdefault(r["case_id"], []).append(r)
            if len(por_caso) != 8 or len(fs) != 105:
                errores.append(f"{nombre} {cfg}: {len(por_caso)} casos, {len(fs)} filas")
            avisos = {}
            for cid, rs in por_caso.items():
                for r in sorted(rs, key=lambda x: int(x["linea"])):
                    if r["aviso"] == "true":
                        avisos[cid] = int(r["linea"])
                        break
            if cfg == directo:
                # Variante directa: cada fila es una consulta al SLM
                # (columna `consulta` vacía por diseño del ensayo #50).
                cons = list(fs)
                evit = []
            else:
                cons = [r for r in fs if (r.get("consulta") or "") in ("slm_valida", "slm_fallo")]
                evit = [r for r in fs if (r.get("consulta") or "") == "omitida"]
            por_cfg[cfg] = {
                "filas": len(fs),
                "consultas_slm": len(cons),
                "evitadas": len(evit),
                "fallos_slm": sum(1 for r in cons
                                if r.get("valida") == "false" or (r.get("error") or "").strip()),
                "fallos_tito": sum(1 for r in fs if (r.get("tito_error") or "").strip()),
                "tokens": sum((int(r["tokens_prompt"]) if r.get("tokens_prompt") else 0)
                              + (int(r["tokens_salida"]) if r.get("tokens_salida") else 0)
                              for r in (fs if cfg == directo else cons)),
                "ms_total": round(sum(float(r["ms"]) for r in fs if r.get("ms")), 1),
                "derivacion": {cid: min((int(r["linea"]) for r in por_caso[cid]
                                         if (r.get("consulta") or "") in ("slm_valida", "slm_fallo")),
                                        default=None) for cid in por_caso} if cfg == filtrado else {},
                "avisos": avisos,
                "vishing_detectado": sum(1 for c in VISHING if c in avisos),
                "falsas_alarmas": sum(1 for c in por_caso if c not in VISHING and c in avisos),
            }
        nunca = sorted(c for c, l in por_cfg[filtrado]["derivacion"].items() if l is None)
        if nunca:
            errores.append(f"{nombre}: nunca derivadas {nunca} (igual conservan denominador)")

        modelos[modelo] = {
            "corrida": nombre,
            "digest_ok": got == digest,
            "sha_actualizaciones_csv": sha256(corrida / "actualizaciones.csv"),
            "sha_manifiesto_json": sha256(corrida / "manifiesto.json"),
            "sha_comparacion_md": sha256(corrida / "comparacion.md"),
            "directo": por_cfg[directo],
            "filtrado": por_cfg[filtrado],
        }
        # Avisos se serializan con claves str; derivación también.
        modelos[modelo]["filtrado"]["derivacion"] = {
            k: v for k, v in por_cfg[filtrado]["derivacion"].items()}
        modelos[modelo]["directo"]["avisos"] = por_cfg[directo]["avisos"]
        modelos[modelo]["filtrado"]["avisos"] = por_cfg[filtrado]["avisos"]

    total_evaluaciones = len(modelos) * 8 * 2
    cobertura = {
        "generado_por": "consolidar.py (solo lee salidas crudas, sin inferencia)",
        "corridas_canonicas": sorted(ESPERADOS),
        "corrida_superada_excluida": SUPERADA,
        "artefactos": len(modelos),
        "evaluaciones_conversacion": total_evaluaciones,
        "matriz_esperada": "6 x 8 x 2 = 96",
        "matriz_ok": total_evaluaciones == 96 and not errores,
        "errores": errores,
        "modelos": modelos,
    }
    (CARPETA / "cobertura.json").write_text(
        json.dumps(cobertura, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    L = ["# Tablas cruzadas Tito→SLM (generado por `consolidar.py`)", "",
         "No editar a mano: se regenera con `bash regenerar.sh` desde las salidas crudas.",
         "", "## Detección y falsas alarmas por modelo y variante",
         "", "| Modelo | Vishing directo | Vishing filtrado | FA directo | FA filtrado |",
         "|---|---|---|---|---|"]
    for modelo, m in modelos.items():
        d, f = m["directo"], m["filtrado"]
        L.append(f"| `{modelo}` | {d['vishing_detectado']}/4 | {f['vishing_detectado']}/4 "
                 f"| {d['falsas_alarmas']}/4 | {f['falsas_alarmas']}/4 |")
    L += ["", "Denominadores: 4 vishing y 4 legítimas difíciles por variante y modelo.",
          "", "## Ahorro y costo por modelo", "",
          "| Modelo | Consultas D | Consultas F | Evitadas | Tokens D | Tokens F | Costo ms D | Costo ms F | Fallos SLM D/F | Fallos Tito |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for modelo, m in modelos.items():
        d, f = m["directo"], m["filtrado"]
        L.append(f"| `{modelo}` | {d['consultas_slm']} | {f['consultas_slm']} | {f['evitadas']} "
                 f"| {d['tokens']} | {f['tokens']} | {d['ms_total']:.0f} | {f['ms_total']:.0f} "
                 f"| {d['fallos_slm']}/{f['fallos_slm']} | {f['fallos_tito']} |")
    L += ["", "Costo ms F = Tito en todas las líneas + SLM válido y fallido; "
              "carga, calentamiento y ajuste van por separado en cada `comparacion.md`.",
          "", "## Cambios de aviso (directo → filtrado)", ""]
    for modelo, m in modelos.items():
        cambios = []
        for cid in sorted(set(m["directo"]["avisos"]) | set(m["filtrado"]["avisos"])):
            a, b = m["directo"]["avisos"].get(cid), m["filtrado"]["avisos"].get(cid)
            if a != b:
                sa, sb = (f"L{a}" if a else "sin aviso"), (f"L{b}" if b else "sin aviso")
                cambios.append(f"{cid}: {sa} → {sb}")
        linea = "; ".join(cambios) if cambios else "sin cambios"
        L.append(f"- `{modelo}`: {linea}.")
    L += ["", "La comparación mide activación selectiva + indicio falible juntos; "
              "no se atribuye el efecto a uno de ellos por separado.",
          ""]
    (CARPETA / "TABLAS.md").write_text("\n".join(L), encoding="utf-8")

    print(f"evaluaciones={total_evaluaciones} errores={len(errores)}")
    for e in errores:
        print("ERROR:", e)
    if errores:
        sys.exit(1)
    print("OK: cobertura 96, digests coincidentes, sin alias duplicados.")


if __name__ == "__main__":
    # Referencias humanas provisorias: existen para las ocho conversaciones.
    for cid in VISHING:
        casos.cargar_referencia(cid)
    main()
