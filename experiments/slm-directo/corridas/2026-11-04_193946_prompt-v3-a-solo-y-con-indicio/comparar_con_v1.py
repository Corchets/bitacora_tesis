# Prompt v3 (Colab) contra v1 (Windows), sobre los 150 de desarrollo. Uso: python -I comparar_con_v1.py
# Lee los CSV y las referencias de los IDs de esas corridas; rechaza la reserva.
import csv,json,glob,collections,statistics as st
from pathlib import Path
W=str(Path(__file__).resolve().parents[2])
def carga(ruta,det):
    d=collections.defaultdict(list)
    for r in csv.DictReader(open(ruta,encoding='utf-8-sig')):
        if r['detector']==det: d[r['case_id']].append(r)
    for v in d.values(): v.sort(key=lambda r:int(r['linea']))
    return d
a=W+'/corridas/2026-11-04_193946_prompt-v3-a-solo-y-con-indicio/actualizaciones.csv'; b=W+'/corridas/2026-11-04_201116_prompt-v3-b-tito-sin-indicio/actualizaciones.csv'
v1s=W+'/corridas/2026-11-04_132229_e2b-directo-150/actualizaciones.csv'; v1t=W+'/corridas/2026-11-04_003715_e2b-tito-viejo-150/actualizaciones.csv'
C={'v1 solo (Win)':carga(v1s,'slm'),'v1 Tito ind (Win)':carga(v1t,'tito-slm'),'v3 solo':carga(a,'slm'),'v3 Tito ind':carga(a,'tito-slm'),'v3 Tito sin':carga(b,'tito-slm-sin-indicio')}
ids=sorted(C['v3 solo']); assert not [i for i in ids if 'CV2-T' in i] and len(ids)==150
ref={i:json.load(open(f'{W}/casos/referencia/{i}.json',encoding='utf-8')) for i in ids}
def av(fs): return next((int(r['linea']) for r in fs if r['aviso']=='true'),None)
def tr(i): return ref[i].get('t_r_linea')
vis=[i for i in ids if ref[i]['clase']=='vishing']; leg=[i for i in ids if ref[i]['clase']!='vishing']; com=[i for i in leg if ref[i]['clase']=='legitima']; dif=[i for i in leg if ref[i]['clase']=='legitima_dificil']
print(len(vis),len(leg),len(com),len(dif),'con TR',sum(1 for i in vis if tr(i)))
for n,c in C.items():
    A={i:av(c[i]) for i in ids}
    filas=sum(len(c[i]) for i in ids); cons=sum(1 for i in ids for r in c[i] if r.get('consulta')!='omitida')
    v=[i for i in vis if A[i]]; ant=sum(1 for i in v if tr(i) and A[i]<tr(i)); en=sum(1 for i in v if tr(i) and A[i]==tr(i)); pos=sum(1 for i in v if tr(i) and A[i]>tr(i))
    conpedido=[i for i in vis if tr(i)]
    al=[r for i in ids for r in c[i] if r['alerta_sugerida']=='true']
    bajo=sum(1 for r in al if float(r['riesgo'])<0.5); noev=sum(1 for r in al if r['evidencia_en_texto']!='true')
    incoh=sum(1 for i in ids for r in c[i] if r['alerta_sugerida']=='false' and (r['evidencia'] or '').strip())
    err=sum(1 for i in ids for r in c[i] if r['error'])
    sm=[float(r['slm_ms']) for i in ids for r in c[i] if r.get('slm_ms') and r.get('consulta')!='omitida']
    print(f"{n:18} estafas {len(v)}/75 conTR {sum(1 for i in conpedido if A[i])}/{len(conpedido)} FA {sum(1 for i in leg if A[i])}/75 com {sum(1 for i in com if A[i])}/{len(com)} dif {sum(1 for i in dif if A[i])}/{len(dif)} ant/en/pos {ant}/{en}/{pos} filas {filas} cons {cons} err {err} alertas {len(al)} riesgo<.5 {bajo} cita-no-en-texto {noev} ev-sin-alerta {incoh} slm_ms med {st.median(sm):.0f}")
S={n:{i:bool(av(c[i])) for i in ids} for n,c in C.items()}
def dif_(x,y,g):
    return sorted(i for i in g if S[x][i] and not S[y][i]),sorted(i for i in g if S[y][i] and not S[x][i])
for x,y in [('v1 solo (Win)','v3 solo'),('v1 Tito ind (Win)','v3 Tito ind'),('v3 solo','v3 Tito ind'),('v3 solo','v3 Tito sin'),('v3 Tito ind','v3 Tito sin')]:
    pv,gv=dif_(x,y,vis); pl,gl=dif_(x,y,leg)
    print(f'\n{x} -> {y}: estafas pierde {len(pv)} {pv[:14]}\n  gana {len(gv)} {gv[:14]}\n  FA elimina {len(pl)} {pl[:14]}\n  FA nuevas {len(gl)} {gl[:20]}')
print()
for i in ['CV2-D-V-BANCO-003','CV2-D-V-PREMIO-003','CV2-D-V-SOPORTE-005','TR-13-turno-medico-pide-dni','TR-08-frase-cortada-candado','TR-09-victima-se-niega','TR-10-ofrecimiento-inducido','TR-06-banco-alerta-legitima']:
    print(i,ref[i]['clase'],'TR',tr(i),{n:av(c[i]) for n,c in C.items()})
