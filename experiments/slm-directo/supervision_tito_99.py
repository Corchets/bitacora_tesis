"""Supervisión contextual de prefijos para #99 (módulo del corrector).

Revisión contextual REAL: cada prefijo de entrenamiento/validación se
somete a DOS pasadas independientes de un modelo contextual vía API
stateless (Ollama http://127.0.0.1:11435) con el MISMO objetivo
contextual (1 = pedido riesgoso o indicio concreto visible para consultar
al SLM; 0 = sin motivo observable revisado, incluyendo solicitudes
legítimas distinguibles por contexto; null = ambiguo/incompleto). Cada
pasada ve SOLO las líneas visibles hasta ese punto, con hablantes A/B
íntegros, sin case_id, sin clase final, sin T_R, sin sufijo futuro y sin
reutilizar respuestas ni estado entre pasadas.

Procedencia de los prompts: corrección v2 en
`prompts_supervision_tito_99.py` (2026-10-29; reemplaza los prompts v1 que
pedían "DIRECTAMENTE" y marcaban 1/1 el prefijo legítimo de la pizzería).
Validación real previa con qwen3.5:4b en
`VALIDACION-PROMPTS-SUPERVISION-TITO-99-2026-10-29.json` (7/7 controles).
Registros versionados con `firma_prompts`; el borrador v1 sin firma queda
descartado y se reanota.

Acuerdo: 1+1 → 1, 0+0 → 0, cualquier otro caso (incluida respuesta
inválida) → null, que queda fuera de pérdida/métricas pero presente en
cobertura. Nunca se toca `revision_humana` ni la puerta formal de
`datos_tito.py`; la autorización es de desarrollo y está declarada.

Tampoco lee la reserva (rechazo por identificador/partición).

Uso (desde experiments/slm-directo/, con .venv de la raíz):
    python supervision_tito_99.py --paso supervision
    python supervision_tito_99.py --paso auditoria
    python supervision_tito_99.py --paso cruce
    python supervision_tito_99.py --paso todo
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from collections import Counter
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

from cliente_ollama import ClienteOllama, ErrorOllama
from datos_tito import rechazar_reserva
from prompts_supervision_tito_99 import (
    PROMPT_VERSION,
    construir_prompt_pasada1,
    construir_prompt_pasada2,
    es_registro_vigente,
    es_registro_vigente_de,
    firma_prompts,
)

CONFIG_RUTA = AQUI / "CONFIGURACION-TITO-2026-10-29.json"
PARTICIONES_RUTA = AQUI / "PARTICIONES-TITO-2026-10-29.json"
SUPERVISION_RUTA = AQUI / "SUPERVISION-CONTEXTUAL-TITO-99-2026-10-29.jsonl"
AUDITORIA_RUTA = AQUI / "AUDITORIA-SEMANTICA-CONTEXTUAL-TITO-99-2026-10-29.json"

MODELO_POR_DEFECTO = "qwen3.5:4b"
URL_POR_DEFECTO = "http://127.0.0.1:11435"
SEMILLA = 42

OPCIONES_MODELO = {"temperature": 0, "seed": SEMILLA, "num_predict": 200}

FORMATO_RESPUESTA = {
    "type": "object",
    "properties": {
        "etiqueta": {"type": ["integer", "null"], "enum": [0, 1, None]},
        "fundamento": {"type": "string"},
        "lineas_soporte": {"type": "array", "items": {"type": "integer"}},
    },
    "required": ["etiqueta", "fundamento", "lineas_soporte"],
}

AUTORIZACION_DESARROLLO = (
    "autorizacion_desarrollo_99 contextual: revisión IA de desarrollo por "
    "prefijo con modelo contextual vía API stateless, separada de la puerta "
    "formal humana de datos_tito.py. NO es revision_humana; no habilita uso "
    "ni cierra D07/D08/D09."
)

ETIQUETAS_VALIDAS = (0, 1, None)


# ---------------------------------------------------------------------------
# Prompts: reexportados del módulo del corrector (v2 contextual)
# ---------------------------------------------------------------------------
# Procedencia: `prompts_supervision_tito_99.py` (corrección v2, 2026-10-29,
# prompts_version v2-contextual-2026-10-29) tras el handoff del supervisor.
# Ambas pasadas comparten el MISMO objetivo contextual (1 = pedido riesgoso
# o indicio concreto visible para consultar al SLM; 0 = sin motivo revisado
# incluyendo legítimo distinguible; null = ambiguo/incompleto), solo llevan
# el prefijo visible con A/B y no ven IDs, clase, T_R, futuro ni la otra
# pasada. Los constructores se reexportan para compatibilidad con las
# pruebas y la orquestación de este módulo; la firma versionada permite
# rechazar filas del borrador viejo (sin firma) sin heredarlas como verdad.
# (Los constructores importados arriba conservan estos mismos nombres.)


# ---------------------------------------------------------------------------
# Llamada stateless al modelo y validación de su respuesta
# ---------------------------------------------------------------------------

def info_modelo(cliente: ClienteOllama, modelo: str) -> dict:
    """Identidad auditable del anotador: tag, digest, versión y parámetros."""
    return {
        "tag": modelo,
        "digest": cliente.modelos_instalados().get(modelo, "desconocido"),
        "ollama_version": cliente.version(),
        "opciones": dict(OPCIONES_MODELO),
        "formato": "json-schema etiqueta/fundamento/lineas_soporte",
    }


def llamar_pasada(cliente: ClienteOllama, modelo: str, prompt: str) -> tuple[str, str]:
    """Una llamada stateless: devuelve (respuesta_cruda, error).

    Sin historial entre llamadas: cada pasada es un chat nuevo de un solo
    mensaje, así no se reutiliza estado ni respuestas entre pasadas ni
    entre prefijos.
    """
    try:
        r = cliente.chat(
            modelo,
            [{"role": "user", "content": prompt}],
            formato=FORMATO_RESPUESTA,
            opciones=dict(OPCIONES_MODELO),
            pensar=False,
        )
        return r["message"]["content"], ""
    except Exception as e:  # noqa: BLE001 - falla cerrada: todo error va a null
        return "", f"error_modelo: {type(e).__name__}: {e}"


def validar_respuesta(objeto: object, n_lineas: int) -> tuple:
    """Valida el JSON del modelo. Falla cerrada: lo inválido va a null."""
    if not isinstance(objeto, dict):
        return None, "", [], "respuesta no es objeto JSON"
    etiqueta = objeto.get("etiqueta")
    fundamento = objeto.get("fundamento")
    soporte = objeto.get("lineas_soporte")
    if etiqueta not in ETIQUETAS_VALIDAS:
        return None, "", [], f"etiqueta inválida: {etiqueta!r}"
    if not isinstance(fundamento, str) or not fundamento.strip():
        return None, "", [], "fundamento vacío"
    if not isinstance(soporte, list) or not all(
            isinstance(n, int) and 1 <= n <= n_lineas for n in soporte):
        return None, "", [], f"lineas_soporte fuera de 1..{n_lineas}: {soporte!r}"
    if etiqueta is not None and not soporte:
        return None, "", [], "etiqueta decidida sin líneas de soporte"
    return etiqueta, fundamento.strip(), sorted(set(soporte)), ""


def acordar(p1: tuple, p2: tuple) -> tuple:
    """Acuerdo entre pasadas: 1+1→1, 0+0→0, resto→null con motivo."""
    e1, f1, s1, err1 = p1
    e2, f2, s2, err2 = p2
    if err1 or err2:
        motivo = "; ".join(e for e in (err1, err2) if e)
        return None, f"respuesta inválida ({motivo}); incierto.", [], "respuesta_invalida"
    if e1 == e2 and e1 is not None:
        return e1, f"{f1} | {f2}", sorted(set(s1) | set(s2)), "acuerdo"
    return (
        None,
        f"desacuerdo entre pasadas (propuesta={e1}, confirmacion={e2}): "
        f"incierto, fuera de pérdida con cobertura. {f1}",
        sorted(set(s1) | set(s2)),
        "desacuerdo",
    )


def revisar_prefijo(lineas_visibles: list[str], cliente: ClienteOllama,
                    modelo: str) -> dict:
    """Revisión contextual real de un prefijo: dos pasadas aisladas."""
    n = len(lineas_visibles)
    prompt1, prompt2 = (construir_prompt_pasada1(lineas_visibles),
                        construir_prompt_pasada2(lineas_visibles))
    cruda1, err1 = llamar_pasada(cliente, modelo, prompt1)
    try:
        obj1 = json.loads(cruda1) if cruda1 else None
    except json.JSONDecodeError as e:
        obj1, err1 = None, f"json_invalido_pasada1: {e}"
    p1 = validar_respuesta(obj1, n) if err1 == "" else (None, "", [], err1)
    # Segunda pasada: llamada nueva, sin ver la primera.
    cruda2, err2 = llamar_pasada(cliente, modelo, prompt2)
    try:
        obj2 = json.loads(cruda2) if cruda2 else None
    except json.JSONDecodeError as e:
        obj2, err2 = None, f"json_invalido_pasada2: {e}"
    p2 = validar_respuesta(obj2, n) if err2 == "" else (None, "", [], err2)
    etiqueta, fundamento, soporte, motivo = acordar(p1, p2)
    return {
        "etiqueta": etiqueta,
        "fundamento": fundamento,
        "lineas_soporte": soporte,
        "motivo": motivo,
        "revision": "IA-desarrollo contextual por prefijo. " + AUTORIZACION_DESARROLLO,
        "pasada1": {"etiqueta": p1[0], "fundamento": p1[1],
                    "lineas_soporte": p1[2], "error": p1[3],
                    "prompt": prompt1, "respuesta_cruda": cruda1},
        "pasada2": {"etiqueta": p2[0], "fundamento": p2[1],
                    "lineas_soporte": p2[2], "error": p2[3],
                    "prompt": prompt2, "respuesta_cruda": cruda2},
    }


# ---------------------------------------------------------------------------
# Carga de conversaciones de ajuste (entrenamiento/validación)
# ---------------------------------------------------------------------------

def sha_hex(crudo: bytes) -> str:
    return hashlib.sha256(crudo).hexdigest()


def cargar_particiones() -> dict:
    particiones = json.loads(PARTICIONES_RUTA.read_text(encoding="utf-8"))
    if particiones.get("semilla") != SEMILLA:
        raise ValueError("particiones con semilla inesperada.")
    return particiones


def cargar_textos_ajuste(particiones: dict) -> tuple[dict, dict]:
    """Textos y partición por case_id para train/val. Sin reserva."""
    from casos import cargar_texto
    convs = [c for c in particiones["conversaciones"]
             if c["particion_preparacion"] in ("entrenamiento", "validacion")]
    textos, particion_de = {}, {}
    for c in convs:
        cid = c["case_id"]
        rechazar_reserva([cid])
        crudo = (AQUI / "casos" / "texto" / f"{cid}.txt").read_bytes()
        if sha_hex(crudo) != c["texto_sha256"]:
            raise ValueError(f"{cid}: el texto cambió desde la partición.")
        textos[cid] = [f"{l.hablante}: {l.texto}" for l in cargar_texto(cid)]
        particion_de[cid] = c["particion_preparacion"]
    return textos, particion_de


def total_prefijos_esperados(textos: dict) -> set[tuple[str, int]]:
    return {(cid, k) for cid, lineas in textos.items()
            for k in range(1, len(lineas) + 1)}


def leer_registros_existentes(ruta: Path) -> dict[tuple[str, int], dict]:
    if not ruta.exists():
        return {}
    regs = {}
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        if linea.strip():
            r = json.loads(linea)
            regs[(r["case_id"], r["hasta_linea"])] = r
    return regs


def recorrer_y_guardar(textos: dict, particion_de: dict, cliente: ClienteOllama,
                       modelo: str, meta_modelo: dict,
                       ruta: Path = SUPERVISION_RUTA,
                       limite: int | None = None) -> dict:
    """Revisa los prefijos faltantes y los agrega al JSONL (reanudable).

    Solo las filas con firma de prompts vigente E identidad del anotador
    del recorrido (tag/digest/versión/opciones) cuentan como hechas: el
    borrador viejo, otra firma, otro modelo u otras opciones se reanotan,
    no se heredan ni se mezclan (corrección v4, orden del coordinador).
    """
    existentes = {k: v for k, v in leer_registros_existentes(ruta).items()
                  if es_registro_vigente_de(v, firma_prompts(), meta_modelo)}
    faltantes = sorted(set(total_prefijos_esperados(textos)) - set(existentes))
    if limite is not None:
        faltantes = faltantes[:limite]
    nuevos = 0
    with ruta.open("a", encoding="utf-8") as f:
        for cid, k in faltantes:
            visibles = textos[cid][:k]
            sup = revisar_prefijo(visibles, cliente, modelo)
            registro = {
                "case_id": cid, "hasta_linea": k,
                "particion": particion_de[cid],
                "texto_hash": sha_hex("\n".join(visibles).encode("utf-8")),
                "modelo": meta_modelo,
                "firma_prompts": firma_prompts(),
                "prompts_version": PROMPT_VERSION,
                **sup,
            }
            f.write(json.dumps(registro, ensure_ascii=False) + "\n")
            f.flush()
            nuevos += 1
    return {"nuevos": nuevos, "faltantes_antes": len(faltantes)}


# ---------------------------------------------------------------------------
# API consumible por el corrector (entrenar_tito_99.py)
# ---------------------------------------------------------------------------

def cargar_supervision(ruta: Path = SUPERVISION_RUTA) -> tuple[dict, dict, dict]:
    """Devuelve (etiqueta_de, cobertura, meta): etiquetas y cobertura real."""
    etiqueta_de, cobertura, modelos = {}, Counter(), Counter()
    for r in leer_registros_existentes(ruta).values():
        etiqueta_de[(r["case_id"], r["hasta_linea"])] = r["etiqueta"]
        etiqueta = "nulo" if r["etiqueta"] is None else r["etiqueta"]
        cobertura[(r["particion"], etiqueta)] += 1
        modelos[r["modelo"]["tag"]] += 1
    return (etiqueta_de,
            {f"{k[0]}/{k[1]}": v for k, v in cobertura.items()},
            dict(modelos))


def etiquetas_entrenamiento_para_ajuste(etiqueta_de: dict,
                                       particion_de: dict) -> tuple[list, list]:
    """Pares ((case_id, hasta_linea)) con etiqueta 0/1 de entrenamiento.

    Los null quedan EXCLUIDOS de la pérdida pero se informan aparte para
    cobertura; nunca se convierten en negativos.
    """
    incluidos, nulos = [], []
    for (cid, k), et in sorted(etiqueta_de.items()):
        if particion_de.get(cid) != "entrenamiento":
            continue
        (incluidos if et is not None else nulos).append(((cid, k), et))
    return incluidos, nulos


def puede_entrenar(textos: dict, particion_de: dict,
                   ruta_sup: Path = SUPERVISION_RUTA,
                   ruta_aud: Path = AUDITORIA_RUTA) -> tuple[bool, list[str]]:
    """Puerta de desarrollo: bloquea entrenar sin etiquetas contextuales."""
    motivos = []
    etiqueta_de, _, _ = (cargar_supervision(ruta_sup)
                         if ruta_sup.exists() else ({}, {}, {}))
    faltantes = sorted(total_prefijos_esperados(textos) - set(etiqueta_de))
    if faltantes:
        motivos.append(f"{len(faltantes)} prefijos sin revisión contextual "
                       f"(p. ej. {faltantes[:3]}).")
    etiquetas_train = {et for (cid, _), et in etiqueta_de.items()
                       if particion_de.get(cid) == "entrenamiento"}
    if 0 not in etiquetas_train or 1 not in etiquetas_train:
        motivos.append("falta una clase (0/1) en entrenamiento: no hay "
                       "supervisión binaria real.")
    if not ruta_aud.exists():
        motivos.append("sin auditoría semántica con exclusiones.")
    else:
        aud = json.loads(ruta_aud.read_text(encoding="utf-8"))
        if ("familias_excluidas_ajuste" not in aud
                or "resolucion_exclusiones" not in aud):
            motivos.append("auditoría sin lista de exclusiones registrada.")
    if motivos:
        return False, motivos
    return True, ["supervisión contextual completa y auditoría con "
                  "exclusiones registradas."]


# ---------------------------------------------------------------------------
# Auditoría semántica banco <-> conversaciones (con las veinte)
# ---------------------------------------------------------------------------

def cargar_banco_textos(particiones: dict) -> list[dict]:
    """Frases del banco conservadas con familia y texto original."""
    import subprocess
    from entrenar_tito import BANCO_BASE, BANCO_COMMIT
    raiz = AQUI.parents[1]
    crudo = subprocess.run(
        ["git", "show", f"{BANCO_COMMIT}:{BANCO_BASE}/ejemplos.jsonl"],
        cwd=raiz, capture_output=True, check=True, timeout=120).stdout
    por_id = {json.loads(l)["id"]: json.loads(l)
              for l in crudo.decode("utf-8").splitlines()}
    ids = {b["id"] for b in particiones["banco"]}
    return [{"id": i, "familia": por_id[i]["familia"], "texto": por_id[i]["texto"]}
            for i in sorted(ids) if i in por_id]


def cargar_lineas_grupo(particiones: dict, grupo: str) -> dict[str, list[str]]:
    """Líneas 'A: ...' por case_id de un grupo de partición. Sin reserva."""
    from casos import cargar_texto
    textos = {}
    for c in particiones["conversaciones"]:
        if c["particion_preparacion"] != grupo:
            continue
        cid = c["case_id"]
        rechazar_reserva([cid])
        textos[cid] = [f"{l.hablante}: {l.texto}" for l in cargar_texto(cid)]
    return textos


def _cargar_robertuito():
    import torch
    from transformers import AutoModel, AutoTokenizer
    from huggingface_hub import snapshot_download
    config = json.loads(CONFIG_RUTA.read_text(encoding="utf-8"))
    encoder_id = config.get("encoder", "pysentimiento/robertuito-base-uncased")
    encoder_rev = config.get("revision", "20cb399e4b93f270c0cd6b6f533bcb0ada3cb658")
    snap = Path(snapshot_download(encoder_id, revision=encoder_rev))
    tokenizer = AutoTokenizer.from_pretrained(str(snap))
    modelo = AutoModel.from_pretrained(str(snap))
    for p in modelo.parameters():
        p.requires_grad_(False)
    modelo.eval()
    return tokenizer, modelo, torch


def incrustar_lineas(lineas: list[str], tokenizer, modelo, torch,
                     lote: int = 16) -> list[list[float]]:
    """Un vector por línea: media de estados de tokens de contenido."""
    import torch as _t  # noqa: F401 (verificación de presencia)
    vectores: list[list[float]] = []
    with torch.no_grad():
        for i in range(0, len(lineas), lote):
            for texto in lineas[i:i + lote]:
                ids = tokenizer(texto, add_special_tokens=True,
                                truncation=True, max_length=128)["input_ids"]
                ids_t = _t.tensor([ids])
                mask = _t.ones_like(ids_t)
                h = modelo(input_ids=ids_t,
                           attention_mask=mask).last_hidden_state[0]
                especiales = {tokenizer.cls_token_id, tokenizer.sep_token_id,
                              tokenizer.pad_token_id}
                estados = [h[j] for j, t in enumerate(ids) if t not in especiales]
                v = (sum(estados) / len(estados)) if estados else h[0] * 0
                vectores.append([float(x) for x in v.tolist()])
    return vectores


def coseno(a: list[float], b: list[float]) -> float:
    import math
    num = sum(x * y for x, y in zip(a, b))
    den = math.sqrt(sum(x * x for x in a) * sum(y * y for y in b))
    return num / den if den else 0.0


def vector_conversacion(vecs_lineas: list[list[float]]) -> list[float]:
    n = len(vecs_lineas)
    m = len(vecs_lineas[0])
    return [sum(v[j] for v in vecs_lineas) / n for j in range(m)]


def calibrar_umbral(vec_por_caso: dict[str, list[float]]) -> dict:
    """Umbral desde pares de paráfrasis declarados (sufijo -parafrasis).

    No usa etiquetas del test ni resultados comparativos: solo pares
    declarados como variantes y pares aleatorios (seed 42) de contraste.
    """
    import random
    pares = [(cid[:-len("-parafrasis")], cid) for cid in vec_por_caso
             if cid.endswith("-parafrasis") and cid[:-len("-parafrasis")] in vec_por_caso]
    sims_par = sorted(coseno(vec_por_caso[a], vec_por_caso[b]) for a, b in pares)
    cids = sorted(vec_por_caso)
    rnd = random.Random(SEMILLA)
    aleatorios = set()
    while len(aleatorios) < max(50, len(pares) * 5) and len(aleatorios) < len(cids) * (len(cids) - 1) // 2:
        a, b = rnd.sample(cids, 2)
        if not a.endswith("-parafrasis") and not b.endswith("-parafrasis"):
            aleatorios.add(tuple(sorted((a, b))))
    sims_azar = sorted(coseno(vec_por_caso[a], vec_por_caso[b]) for a, b in aleatorios)
    if sims_par and sims_azar and min(sims_par) > max(sims_azar):
        umbral = (min(sims_par) + max(sims_azar)) / 2
        metodo = "punto_medio:min_par_max_azar"
    elif sims_par:
        umbral = min(sims_par)
        metodo = "conservador:min_par (solapa con azar; se excluye de más)"
    else:
        umbral = 0.90
        metodo = "reserva:sin_pares_declarados"
    return {"pares_declarados": len(pares), "contrastes_azar": len(aleatorios),
            "sims_par": [round(s, 4) for s in sims_par],
            "sims_azar": [round(s, 4) for s in sims_azar],
            "umbral": round(umbral, 4), "metodo": metodo}


def auditar_semantica(banco: list[dict], grupos: dict[str, dict[str, list[str]]],
                      vec_banco: list[list[float]],
                      vec_lineas: dict[str, list[list[float]]],
                      umbral: float) -> dict:
    """Máximo coseno por frase contra líneas de cada grupo; excluye por familia."""
    por_grupo: dict[str, dict] = {}
    for nombre, textos in grupos.items():
        ids_linea = [(cid, j) for cid, ls in textos.items() for j in range(len(ls))]
        planos = [vec_lineas[f"{cid}#{j}"] for cid, j in ids_linea]
        max_por_frase = []
        for v in vec_banco:
            max_por_frase.append(max((coseno(v, w) for w in planos),
                                     default=0.0))
        por_grupo[nombre] = {"max_por_frase": max_por_frase}
    fam_de = [f["familia"] for f in banco]
    familias_orden = sorted(set(fam_de))
    max_veinte_por_fam = {}
    for fam in familias_orden:
        idx = [i for i, f in enumerate(fam_de) if f == fam]
        max_veinte_por_fam[fam] = (
            max(por_grupo["comparacion_20"]["max_por_frase"][i] for i in idx),
            len(idx))
    excluidas, detalle = [], {}
    for fam, (m, n) in max_veinte_por_fam.items():
        if m >= umbral:
            excluidas.append(fam)
            detalle[fam] = {"max_vs_veinte": round(m, 4), "frases": n}
    top_veinte = sorted(max_veinte_por_fam.items(), key=lambda kv: -kv[1][0])[:20]
    top_diagnostico = []
    for fam in familias_orden:
        idx = [i for i, f in enumerate(fam_de) if f == fam]
        m = max(por_grupo["diagnostico"]["max_por_frase"][i] for i in idx)
        top_diagnostico.append((fam, round(m, 4), len(idx)))
    top_diagnostico.sort(key=lambda t: -t[1])
    hist = Counter()
    for _, (m, _) in max_veinte_por_fam.items():
        hist[f"{int(m * 20) / 20:.2f}-{int(m * 20) / 20 + 0.05:.2f}"] += 1
    return {"grupos": list(grupos),
            "familias_excluidas_ajuste": sorted(excluidas),
            "detalle_excluidas": detalle,
            "umbral_usado": umbral,
            "top_familias_vs_veinte": [
                {"familia": f, "max": round(m, 4), "frases": n}
                for f, (m, n) in top_veinte],
            "top_familias_vs_diagnostico": [
                {"familia": f, "max": m, "frases": n}
                for f, m, n in top_diagnostico[:10]],
            "histograma_max_vs_veinte": dict(sorted(hist.items()))}


def cruces_banco_grupos(banco: list[dict], grupos: dict[str, dict[str, list[str]]],
                        vec_banco: list[list[float]],
                        vec_lineas: dict[str, list[float]],
                        umbral_referencia: float) -> dict:
    """Maximo coseno por familia del banco vs lineas de cada grupo.

    Informativo: no excluye ni habilita entrenamiento. Reusa el umbral de
    referencia calibrado vs las veinte (etapa `auditoria`); no recalibra.
    No acredita independencia causal.
    """
    fam_de = [f["familia"] for f in banco]
    cruces = {}
    for nombre, textos in grupos.items():
        planos = [vec_lineas[f"{cid}#{j}"] for cid, ls in textos.items()
                  for j in range(len(ls))]
        max_pf = [max((coseno(v, w) for w in planos), default=0.0)
                  for v in vec_banco]
        por_fam = {}
        for fam in sorted(set(fam_de)):
            idx = [i for i, f in enumerate(fam_de) if f == fam]
            por_fam[fam] = {"max": round(max(max_pf[i] for i in idx), 4),
                            "frases": len(idx)}
        top = sorted(por_fam.items(), key=lambda kv: -kv[1]["max"])[:15]
        hist = Counter()
        for d in por_fam.values():
            hist[f"{int(d['max'] * 20) / 20:.2f}-{int(d['max'] * 20) / 20 + 0.05:.2f}"] += 1
        cruces[nombre] = {
            "top15": [{"familia": f, **d} for f, d in top],
            "histograma": dict(sorted(hist.items())),
            "n_familias_ge_umbral_referencia": sum(
                1 for d in por_fam.values() if d["max"] >= umbral_referencia),
            "n_lineas_grupo": len(planos),
        }
    return cruces


# ---------------------------------------------------------------------------
# Orquestación CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--paso", choices=["supervision", "auditoria", "cruce",
                                      "todo"],
                   default="todo")
    p.add_argument("--modelo", default=MODELO_POR_DEFECTO)
    p.add_argument("--url", default=URL_POR_DEFECTO)
    p.add_argument("--limite", type=int, default=None,
                   help="Solo para pruebas: revisa como máximo N prefijos.")
    args = p.parse_args(argv)

    particiones = cargar_particiones()
    rechazar_reserva([c["case_id"] for c in particiones["conversaciones"]])

    if args.paso in ("supervision", "todo"):
        textos, particion_de = cargar_textos_ajuste(particiones)
        cliente = ClienteOllama(url=args.url)
        meta = info_modelo(cliente, args.modelo)
        print(f"anotador: {meta['tag']} digest={meta['digest'][:12] if len(meta['digest']) > 12 else meta['digest']} "
              f"ollama={meta['ollama_version']} url={args.url}")
        res = recorrer_y_guardar(textos, particion_de, cliente, args.modelo,
                                 meta, limite=args.limite)
        etiqueta_de, cobertura, modelos = cargar_supervision()
        print(f"supervision: nuevos={res['nuevos']} cobertura={cobertura}")
        ok, motivos = puede_entrenar(textos, particion_de)
        print(f"puerta: {'OK' if ok else 'BLOQUEADA'}: {motivos}")
        if args.paso == "supervision":
            return 0 if ok else 2

    if args.paso in ("auditoria", "todo"):
        import torch  # noqa: F401 (verifica entorno antes de incrustar)
        banco = cargar_banco_textos(particiones)
        grupos = {g: cargar_lineas_grupo(particiones, g) for g in
                  ("entrenamiento", "validacion", "comparacion_20", "diagnostico")}
        tokenizer, modelo_rt, torch_mod = _cargar_robertuito()
        lineas_banco = [f["texto"] for f in banco]
        vec_banco = incrustar_lineas(lineas_banco, tokenizer, modelo_rt, torch_mod)
        vec_lineas, vec_por_caso = {}, {}
        for textos in grupos.values():
            for cid, ls in textos.items():
                vs = incrustar_lineas(ls, tokenizer, modelo_rt, torch_mod)
                for j, v in enumerate(vs):
                    vec_lineas[f"{cid}#{j}"] = v
                vec_por_caso[cid] = vector_conversacion(vs)
        calib = calibrar_umbral(vec_por_caso)
        aud = auditar_semantica(banco, grupos, vec_banco, vec_lineas,
                                calib["umbral"])
        familias_excl = set(aud["familias_excluidas_ajuste"])
        banco_rest = [f for f in banco if f["familia"] not in familias_excl]
        clase_de = {(b["id"]): (b["particion_preparacion"], b["clase_autoral"])
                    for b in particiones["banco"]}
        conteo_antes = Counter(clase_de[f["id"]] for f in banco)
        conteo_despues = Counter(clase_de[f["id"]] for f in banco_rest)
        if aud["familias_excluidas_ajuste"]:
            resolucion = (f"exclusión de {len(familias_excl)} familias por "
                          "similitud >= umbral calibrado vs las veinte.")
        else:
            resolucion = ("cero exclusiones: ninguna familia alcanza el "
                          "umbral calibrado vs las veinte; ver top e "
                          "histograma como evidencia. No acredita "
                          "independencia causal.")
        informe = {
            "fecha": "2026-10-29", "semilla": SEMILLA,
            "anotador": "auditoria por incrustaciones RoBERTuito congelado "
                        "(solo textos; sin etiquetas del test ni reserva)",
            "calibracion": calib, **aud,
            "frases_auditadas": len(banco),
            "conteo_antes": {f"{k[0]}/{k[1]}": v for k, v in conteo_antes.items()},
            "conteo_despues": {f"{k[0]}/{k[1]}": v for k, v in conteo_despues.items()},
            "banco_restante": len(banco_rest),
            "resolucion_exclusiones": resolucion,
            "nota": ("Exclusión por familia completa vs las veinte. "
                     "Diagnóstico se informa sin excluir (lo usa #98). Si "
                     "falta una clase tras excluir, material sintético "
                     "trazable sin reserva; no se sustituyen las veinte."),
            "limites": ["Cota por similitud de textos, no prueba de "
                        "independencia causal.",
                        "Umbral calibrado en pares declarados, no en "
                        "resultados comparativos.",
                        "La validación del banco no es independiente del "
                        "Tito viejo (lo vio en ajuste)."],
        }
        AUDITORIA_RUTA.write_text(json.dumps(informe, ensure_ascii=False,
                                             indent=1), encoding="utf-8")
        print(f"auditoria: umbral={calib['umbral']} excluidas="
              f"{len(aud['familias_excluidas_ajuste'])} "
              f"restantes={len(banco_rest)}")

    if args.paso in ("cruce", "todo"):
        # Cruce banco <-> train/val (+ comparacion_20, diagnostico) sobre el
        # artefacto primario unico: no recalibra, no excluye, no habilita.
        import torch  # noqa: F401 (verifica entorno antes de incrustar)
        if not AUDITORIA_RUTA.exists():
            print("cruce fail-closed: falta el artefacto primario de "
                  "auditoria; correr --paso auditoria primero.")
            return 2
        base = json.loads(AUDITORIA_RUTA.read_text(encoding="utf-8"))
        banco = cargar_banco_textos(particiones)
        grupos = {g: cargar_lineas_grupo(particiones, g) for g in
                  ("entrenamiento", "validacion", "comparacion_20",
                   "diagnostico")}
        tokenizer, modelo_rt, torch_mod = _cargar_robertuito()
        vec_banco = incrustar_lineas([f["texto"] for f in banco],
                                     tokenizer, modelo_rt, torch_mod)
        vec_lineas = {}
        for textos in grupos.values():
            for cid, ls in textos.items():
                vs = incrustar_lineas(ls, tokenizer, modelo_rt, torch_mod)
                for j, v in enumerate(vs):
                    vec_lineas[f"{cid}#{j}"] = v
        cruces = cruces_banco_grupos(banco, grupos, vec_banco, vec_lineas,
                                     float(base["umbral_usado"]))
        base["cruces_por_grupo"] = cruces
        etapas = list(base.get("etapas_ejecutadas", ["auditoria_20"]))
        if "cruce_train_val" not in etapas:
            etapas.append("cruce_train_val")
        base["etapas_ejecutadas"] = etapas
        lim_cruce = ("Cruces banco<->train/val/comparacion/diagnostico "
                     "informativos con el umbral de referencia; sin "
                     "exclusiones ni prueba de independencia causal.")
        if lim_cruce not in base.get("limites", []):
            base["limites"] = list(base.get("limites", [])) + [lim_cruce]
        AUDITORIA_RUTA.write_text(json.dumps(base, ensure_ascii=False,
                                             indent=1), encoding="utf-8")
        print(f"cruce: grupos={sorted(cruces)} "
              f"sobre_umbral={[g for g, c in cruces.items() if c['n_familias_ge_umbral_referencia']]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
