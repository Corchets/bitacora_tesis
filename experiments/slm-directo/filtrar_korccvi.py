"""Triage de llamadas largas de KorCCVi v2 para #144.

Uso: python3 -I filtrar_korccvi.py <KorCCVi>/Multimodal/data/transcripts/vishing <salida.json>
KorCCVi: github.com/selfcontrol7/Korean_Voice_Phishing_Detection, commit 93b5b07a9a73b20d2e686f82e5115ba850e21b9c.
La salida es intermedia y no se versiona: contiene fragmentos del texto original.
La decisión por llamada está en docs/corpus/FILTRO-KORCCVI.csv.
Solo marca candidatos por palabra clave; la decisión es de lectura humana.
"""
import json, os, re, sys

SRC, OUT = sys.argv[1], sys.argv[2]

# Pedidos candidatos, agrupados por etiqueta del MANUAL-ANOTACION.
PAT = {
    "REQUEST_TRANSFER": r"이체(하|해|를|시|좀|부탁)|송금|입금(하|해|시)|보내(주|셔|드)|옮기(셔|시|세)|현금.{0,12}(인출|찾|뽑|준비|전달|가지고|들고)|인출(하|해|을|시)|출금(하|해|시)|(돈|금액|자금).{0,10}(보내|넘기|맡기|전달)|상품권|선납|수수료.{0,10}(입금|보내|내)|보증금.{0,10}(입금|보내)|상환.{0,10}(입금|이체|하셔|해 주)",
    "REQUEST_SECRET": r"비밀번호.{0,15}(불러|말씀|알려|입력|누르)|보안카드|공인인증서|카드 ?번호.{0,10}(불러|말씀|알려)|계좌 ?번호.{0,10}(불러|말씀|알려|확인해 주)",
    "REQUEST_AUTH_CODE": r"인증 ?번호.{0,15}(불러|말씀|알려|입력|누르)|OTP|일회용",
    "REQUEST_PERSONAL_DATA": r"주민(등록)? ?번호.{0,15}(불러|말씀|알려|확인)|신분증.{0,10}(사진|찍|보내)|생년월일.{0,10}(불러|말씀|알려)",
    "REQUEST_REMOTE_ACCESS": r"원격|팀뷰어|화면.{0,6}공유",
    "REQUEST_SECURITY_ACTION": r"(앱|어플|애플리케이션).{0,12}(설치|다운|깔)|링크|URL|사이트.{0,12}(접속|들어가|입력)|(은행|ATM|현금인출기|자동인출기|인출기).{0,12}(가셔|가 주|이동|도착|가세요|가시)",
}
# Advertencias del propio estafador que mencionan el dato sin pedirlo.
NEG = r"(묻지|요구하지|요청하지) ?(않|안)|절대.{0,10}(알려 주지|말씀하지)"
OPEN = r"여보세요|안녕하(십니까|세요)|통화 ?가능|(입니다|이고요)[.?]?$|에서 (연락|전화)"


def turns_of(segs):
    out = []
    for s in segs:
        sp = s["speaker"]["label"]
        if out and out[-1]["sp"] == sp:
            out[-1]["text"] += " " + s["text"]; out[-1]["end"] = s["end"]
        else:
            out.append({"sp": sp, "text": s["text"], "start": s["start"], "end": s["end"]})
    return out


rows = []
for f in sorted(os.listdir(SRC), key=lambda x: int(re.sub(r"\D", "", x))):
    segs = json.load(open(os.path.join(SRC, f), encoding="utf-8"))["segments"]
    if not segs:
        continue
    T = turns_of(segs)
    dur = segs[-1]["end"] / 1000
    nspk = len({t["sp"] for t in T})
    if not (dur >= 240 and nspk >= 2 and len(T) >= 20):
        continue
    words = {}
    for t in T:
        words[t["sp"]] = words.get(t["sp"], 0) + len(t["text"])
    caller = max(words, key=words.get)
    share = words[caller] / sum(words.values())
    txt = " ".join(t["text"] for t in T)
    tipo = ("fiscalia_policia" if re.search(r"검찰|수사관|검사|경찰|지검|사건번호", txt)
            else "prestamo" if re.search(r"대출|대환|저축은행|캐피탈|금리", txt) else "otro")
    hits = []
    for i, t in enumerate(T):
        for lab, p in PAT.items():
            for m in re.finditer(p, t["text"]):
                ctx = t["text"][max(0, m.start() - 60): m.end() + 60]
                if re.search(NEG, ctx):
                    continue
                hits.append({"turn": i, "t_s": round(t["start"] / 1000), "label": lab,
                             "by_caller": t["sp"] == caller, "match": m.group(0)})
    opening = " ".join(t["text"] for t in T[:2])[:200]
    rows.append({
        "id": f, "dur_s": round(dur), "turns": len(T), "nspk": nspk,
        "caller_share": round(share, 2), "tipo": tipo,
        "opening_like": bool(re.search(OPEN, opening)),
        "hits": hits,
    })

json.dump(rows, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(rows), "llamadas largas;", sum(bool([h for h in r["hits"] if h["by_caller"]]) for r in rows),
      "con algún pedido candidato del llamante")
