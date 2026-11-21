"""Extrae los segmentos de llamadas de KorCCVi v2 a un texto compacto para traducir (#144).

Uso: python3 -I extraer_korccvi.py <carpeta con vishing_N.json> <salida> 300,304,...
KorCCVi: github.com/selfcontrol7/Korean_Voice_Phishing_Detection, commit 93b5b07a9a73b20d2e686f82e5115ba850e21b9c.
Numera los casos desde KO-13. La salida contiene el texto original y no se versiona
(la fuente prohíbe redistribuir derivados); casos.json guarda el SHA-256 de cada fuente.
"""
import hashlib, json, sys
from pathlib import Path
src, out = Path(sys.argv[1]), Path(sys.argv[2])
casos = sys.argv[3].split(",")
out.mkdir(parents=True, exist_ok=True)
filas = []
for i, n in enumerate(casos, start=13):
    ko = f"KO-{i:02d}"
    f = src / f"vishing_{n}.json"
    crudo = f.read_bytes()
    segs = json.loads(crudo)["segments"]
    lineas, fin_prev = [], None
    for k, s in enumerate(segs, 1):
        ini = s["start"] / 1000
        if fin_prev is not None and ini - fin_prev >= 5:
            lineas.append(f"[sin texto entre {fin_prev:.1f} s y {ini:.1f} s]".replace(".", ","))
        hab = s.get("speaker", {}).get("name") or s["diarization"]["label"]
        lineas.append(f"{k}. [{ini:.1f} s] {hab}: {s['textEdited'] or s['text']}".replace(f"[{ini:.1f} s]", f"[{ini:.1f} s]".replace(".", ",")))
        fin_prev = s["end"] / 1000
    dur = segs[-1]["end"] / 1000
    sha = hashlib.sha256(crudo).hexdigest()
    (out / f"{ko}_vishing_{n}.ko.txt").write_text(
        f"{ko} · vishing_{n}.json · SHA-256 {sha} · {len(segs)} segmentos · {dur:.0f} s\n\n" + "\n".join(lineas) + "\n")
    filas.append({"caso": ko, "fuente": f"vishing_{n}", "sha256": sha, "segmentos": len(segs), "duracion_s": round(dur)})
(out / "casos.json").write_text(json.dumps(filas, indent=1, ensure_ascii=False))
for f in filas: print(f)
