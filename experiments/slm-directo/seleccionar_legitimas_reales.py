"""Sortea llamadas salientes reales de CallCenterEN para el set de legítimas reales y las parte por pausas.

Uso: python3 -I seleccionar_legitimas_reales.py <carpeta con las zip> <carpeta privada de salida>

Regla escrita antes de abrir ninguna llamada (2026-11-18, docs/investigacion/FUENTES-LEGITIMAS-REALES.md §8):
- Fuente: AIxBlock/92k-real-world-call-center-scripts-english, revisión 9d40ca13f3e1 (CC BY-NC 4.0).
- Estratos, solo por nombre de archivo:
    seguros              insurance_outbound.zip, llamadas enteras (`<10 dígitos>_transcript.json`; sin partes ni P#)
    equipamiento_medico  medical_equipment_outbound.zip, `DMEMED_…-all_transcript.json`
    telecomunicaciones   el archivo mezclado, solo `US_TELECOM_…_transcript.json` (el resto es servicio entrante)
- Filtro: 60 a 900 s de audio y al menos 80 palabras. Saca buzones y cortes, y deja la traducción en un tamaño
  manejable. El tope de 15 minutos se declara: las llamadas más largas quedan afuera.
- Cupos: 24 de seguros, 18 de equipamiento médico y 8 de telecomunicaciones; `Random(20261118)` sobre la lista
  ordenada de cada estrato.
- No se lee el diálogo para elegir. Lo que se descarte después (buzón, llamada entrante, sin conversación) se
  informa con su motivo; no se reemplaza por otra.

Escribe en la salida, que queda fuera de Git porque los nombres de archivo traen el teléfono de la persona:
    candidatos.json      alias CAND-NN → estrato, archivo, SHA-256 de la fuente, duración y palabras
    fuente/CAND-NN.md    el texto partido en segmentos numerados en cada pausa de 600 ms o más, con su segundo
Imprime solo conteos y el SHA-256 de candidatos.json, sin texto de las llamadas.
"""

import hashlib
import json
import random
import re
import sys
import zipfile
from pathlib import Path

SEMILLA = 20261118
PAUSA_MS = 600
ESTRATOS = {
    "seguros": ("insurance_outbound.zip", re.compile(r"^\d{10}_transcript\.json$"), 24),
    "equipamiento_medico": ("medical_equipment_outbound.zip", re.compile(r"^DMEMED_.*-all_transcript\.json$"), 18),
    "telecomunicaciones": ("home_service_inbound_telecom_outbound.zip",
                           re.compile(r"^US_TELECOM_\d+_AH_\(\d+\)_transcript\.json$"), 8),
}
SHA_ZIP = {
    "insurance_outbound.zip": "7315446229b8706136cc1f6934192710b391b908fb7ab2a3ebb44806f22641e0",
    "medical_equipment_outbound.zip": "0d5126014fb3a03d467df86b5d3a4b835f840339e4f1800c2ed53f9025aea00a",
    "home_service_inbound_telecom_outbound.zip": "e93803a9973464f07303efb321d7c340356aea51bb64a1d3aace14f47b268d1e",
}


def segmentos(palabras: list[dict]) -> list[tuple[float, str]]:
    """Agrupa palabras consecutivas; corta donde la pausa entre dos palabras es de PAUSA_MS o más."""
    salida, actual, inicio, fin_prev = [], [], None, None
    for w in palabras:
        if actual and w["start"] - fin_prev >= PAUSA_MS:
            salida.append((inicio / 1000, " ".join(actual)))
            actual = []
        if not actual:
            inicio = w["start"]
        actual.append(w["text"])
        fin_prev = w["end"]
    if actual:
        salida.append((inicio / 1000, " ".join(actual)))
    return salida


def main() -> None:
    origen, salida = Path(sys.argv[1]), Path(sys.argv[2])
    for zf, sha in SHA_ZIP.items():
        if hashlib.sha256((origen / zf).read_bytes()).hexdigest() != sha:
            sys.exit(f"{zf} no coincide con su SHA-256")
    if (salida / "candidatos.json").exists():
        sys.exit("candidatos.json ya existe: el sorteo se hace una sola vez")
    (salida / "fuente").mkdir(parents=True, exist_ok=True)
    rng = random.Random(SEMILLA)
    candidatos, n = {}, 0
    for estrato, (zf, patron, cupo) in ESTRATOS.items():
        z = zipfile.ZipFile(origen / zf)
        elegibles = []
        for nombre in sorted(z.namelist()):
            if "__MACOSX" in nombre or not patron.match(nombre.split("/")[-1]):
                continue
            j = json.loads(z.read(nombre))
            if 60 <= j["audio_duration"] <= 900 and len(j["words"]) >= 80:
                elegibles.append(nombre)
        elegidos = rng.sample(elegibles, cupo)
        print(f"{estrato}: {len(elegibles)} elegibles, {cupo} sorteados")
        for nombre in elegidos:
            n += 1
            alias = f"CAND-{n:02d}"
            crudo = z.read(nombre)
            j = json.loads(crudo)
            segs = segmentos(j["words"])
            candidatos[alias] = {"estrato": estrato, "zip": zf, "archivo": nombre,
                                 "sha256_fuente": hashlib.sha256(crudo).hexdigest(),
                                 "duracion_s": j["audio_duration"], "palabras": len(j["words"]),
                                 "segmentos": len(segs)}
            lineas = [f"# {alias} · {j['audio_duration']} s · {len(segs)} segmentos", ""]
            lineas += [f"[{i} | {t:.1f} s] {texto}" for i, (t, texto) in enumerate(segs, 1)]
            (salida / "fuente" / f"{alias}.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    datos = {"semilla": SEMILLA, "pausa_ms": PAUSA_MS, "revision_dataset": "9d40ca13f3e173ad815c89bb8fff144be3ae3146",
             "sha256_zip": SHA_ZIP, "candidatos": candidatos}
    texto = json.dumps(datos, ensure_ascii=False, indent=1) + "\n"
    (salida / "candidatos.json").write_text(texto, encoding="utf-8")
    print(f"{n} candidatos; SHA-256 de candidatos.json: {hashlib.sha256(texto.encode()).hexdigest()}")


def segunda_tanda(origen: Path, salida: Path) -> None:
    """Segunda tanda, decidida el 2026-11-18 después de anotar la primera y antes de correr ningún detector.

    En la primera, las 42 de seguros y equipamiento médico resultaron captación de Medicare o esquemas que el
    OIG describe como fraude; solo las de telecomunicaciones son legítimas. Se sortean 28 más de ese estrato,
    con el mismo filtro, entre las elegibles que no salieron en la primera (`Random(20261119)`), como CAND-51
    a CAND-78. No se reemplaza ni se vuelve a sortear nada de la primera tanda.
    """
    datos = json.loads((salida / "candidatos.json").read_text(encoding="utf-8"))
    if "segunda_tanda" in datos:
        sys.exit("la segunda tanda ya se sorteó")
    zf, patron, _ = ESTRATOS["telecomunicaciones"]
    z = zipfile.ZipFile(origen / zf)
    ya = {c["archivo"] for c in datos["candidatos"].values()}
    elegibles = []
    for nombre in sorted(z.namelist()):
        if "__MACOSX" in nombre or not patron.match(nombre.split("/")[-1]) or nombre in ya:
            continue
        j = json.loads(z.read(nombre))
        if 60 <= j["audio_duration"] <= 900 and len(j["words"]) >= 80:
            elegibles.append(nombre)
    elegidos = random.Random(20261119).sample(elegibles, 28)
    print(f"telecomunicaciones, segunda tanda: {len(elegibles)} elegibles, 28 sorteados")
    nuevos = {}
    for i, nombre in enumerate(elegidos, 51):
        alias = f"CAND-{i:02d}"
        crudo = z.read(nombre)
        j = json.loads(crudo)
        segs = segmentos(j["words"])
        nuevos[alias] = {"estrato": "telecomunicaciones", "zip": zf, "archivo": nombre,
                         "sha256_fuente": hashlib.sha256(crudo).hexdigest(),
                         "duracion_s": j["audio_duration"], "palabras": len(j["words"]), "segmentos": len(segs)}
        lineas = [f"# {alias} · {j['audio_duration']} s · {len(segs)} segmentos", ""]
        lineas += [f"[{k} | {t:.1f} s] {texto}" for k, (t, texto) in enumerate(segs, 1)]
        (salida / "fuente" / f"{alias}.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    datos["candidatos"].update(nuevos)
    datos["segunda_tanda"] = {"semilla": 20261119, "alias": sorted(nuevos)}
    texto = json.dumps(datos, ensure_ascii=False, indent=1) + "\n"
    (salida / "candidatos.json").write_text(texto, encoding="utf-8")
    print(f"SHA-256 de candidatos.json: {hashlib.sha256(texto.encode()).hexdigest()}")


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "segunda":
        segunda_tanda(Path(sys.argv[2]), Path(sys.argv[3]))
    else:
        main()
