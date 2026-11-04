# v1, v3 y v4 en Colab, sobre los 150 de desarrollo. Uso: python -I comparar_con_v1_colab.py
# Lee los CSV y las referencias de los IDs de esas corridas; rechaza la reserva. No corre modelos.
# Las corridas cortan en el primer aviso: un filtro que veta un aviso no sabe qué pasaría después.
import collections,csv,difflib,json,re,unicodedata
from pathlib import Path
csv.field_size_limit(10**9)
W=Path(__file__).resolve().parents[2]; C=W/'corridas'; E=C/'2026-11-04_sin-indicio-150'
EA=E/'a/2026-11-04_194015_sin-indicio-a-solo-y-con-indicio'; EB=E/'b/2026-11-04_201218_sin-indicio-b-tito-sin-indicio'; EC=E/'c/2026-11-04_202259_sin-indicio-c-solo-repeticion'
LA=C/'2026-11-04_193946_prompt-v3-a-solo-y-con-indicio'; LB=C/'2026-11-04_201116_prompt-v3-b-tito-sin-indicio'
V=C/'2026-11-04_prompt-v4-tito-sin-indicio'; VA=V/'a/2026-11-04_215231_prompt-v4-a-v4-rol'; VB=V/'b/2026-11-04_220639_prompt-v4-b-v3-rol'; VC=V/'c/2026-11-04_221708_prompt-v4-c-v3-orden-v1-ab'; VD=V/'d/2026-11-04_222802_prompt-v4-d-tarea-ab'
CORRIDAS={'v1 solo':(EA,'slm'),'v1 solo rep':(EC,'slm'),'v1 Tito ind':(EA,'tito-slm'),'v1 Tito sin':(EB,'tito-slm-sin-indicio'),'v3 solo':(LA,'slm'),'v3 Tito ind':(LA,'tito-slm'),'v3 Tito sin':(LB,'tito-slm-sin-indicio'),'v1 control':(VD,'tito-slm-sin-indicio'),'v3 orden v1':(VC,'tito-slm-sin-indicio'),'v3 roles':(VB,'tito-slm-sin-indicio'),'v4 roles':(VA,'tito-slm-sin-indicio'),
 'v1 solo Win':(C/'2026-11-04_132229_e2b-directo-150','slm'),'v1 Tito ind Win':(C/'2026-11-04_003715_e2b-tito-viejo-150','tito-slm')}
def carga(carpeta,det):
    d=collections.defaultdict(list)
    for r in csv.DictReader(open(carpeta/'actualizaciones.csv',encoding='utf-8-sig')):
        if r['detector']==det: d[r['case_id']].append(r)
    for v in d.values(): v.sort(key=lambda r:int(r['linea']))
    return d
R={n:carga(*v) for n,v in CORRIDAS.items()}
ids=sorted(R['v3 Tito sin']); assert len(ids)==150 and not [i for i in ids if 'CV2-T' in i]
assert all(sorted(c)==ids for c in R.values())
for carpeta,huella in ((EA,'bf4284996898c45d'),(EB,'bf4284996898c45d'),(EC,'bf4284996898c45d'),(LA,'a944aadc550480b3'),(LB,'a944aadc550480b3'),(VD,'bf4284996898c45d'),(VC,'e1030f8859125834'),(VB,'a944aadc550480b3'),(VA,'92df75a22c2746fb')):
    m=json.load(open(carpeta/'manifiesto.json',encoding='utf-8'))
    assert huella in json.dumps(m['prompts']) and m['ollama']['version']=='0.40.14' and m['particion']=='desarrollo'
    assert m['ollama']['digests']['gemma4:e2b-it-q4_K_M'].startswith('b37049369adf')
    if m['filtro_tito']: assert m['filtro_tito']['artefacto_sha256'].startswith('fb601eaa') and m['filtro_tito']['umbral']==0.5
assert all(json.load(open(x/'manifiesto.json',encoding='utf-8'))['filtro_tito']['indicio'] is False for x in (EB,LB,VA,VB,VC,VD))
ref={i:json.load(open(W/f'casos/referencia/{i}.json',encoding='utf-8')) for i in ids}
vis=[i for i in ids if ref[i]['clase']=='vishing']; leg=[i for i in ids if ref[i]['clase']!='vishing']
com=[i for i in leg if ref[i]['clase']=='legitima']; dif=[i for i in leg if ref[i]['clase']=='legitima_dificil']
tr=lambda i:ref[i].get('t_r_linea')
def fila(c,i): return next((r for r in c[i] if r['aviso']=='true'),None)
def av(c,i):
    f=fila(c,i); return int(f['linea']) if f else None
def norm(s):
    s=unicodedata.normalize('NFKD',s.lower()); return ' '.join(''.join(x for x in s if x.isalnum() or x==' ').split())
def turnos(i):
    return [m.groups() for l in (W/f'casos/texto/{i}.txt').read_text(encoding='utf-8').splitlines() if (m:=re.match(r'^([AB]):\s*(.*)$',l))]
def citadas(f,i):
    T=turnos(i)[:int(f['linea'])]; res=set()
    for frag in f['evidencia'].split('\n'):
        x=norm(re.sub(r'^(?:[AB]|PROTEGIDA|OTRA):\s*','',re.sub(r'^\s*\d+[.)]\s*','',frag)))
        if len(x)<4: continue
        hit=[n+1 for n,(_,t) in enumerate(T) if x in norm(t) or norm(t) in x]
        if not hit:
            s,n=max((difflib.SequenceMatcher(None,x,norm(t)).ratio(),n+1) for n,(_,t) in enumerate(T))
            if s>.6: hit=[n]
        if hit: res.add(hit[-1])
    return res

print('## Resultado'); print('corrida | estafas | con pedido | FA | comunes | dificiles | antes/en/despues | consultas | cita el pedido | cita solo a la victima')
for n,c in R.items():
    A={i:av(c,i) for i in ids}; conp=[i for i in vis if tr(i) and A[i]]
    t=lambda f:sum(1 for i in conp if f(A[i],tr(i)))
    ped=vict=0
    for i in conp:
        cit=citadas(fila(c,i),i); T=turnos(i)
        ped+=bool(cit&({e['linea'] for e in ref[i]['evidencia'] if e['evento']=='pedido'}|{tr(i)}))
        vict+=bool(cit) and all(T[x-1][0]!=T[tr(i)-1][0] for x in cit)
    cons=sum(1 for i in ids for r in c[i] if r.get('consulta')!='omitida')
    print(f"{n} | {sum(1 for i in vis if A[i])} | {len(conp)} | {sum(1 for i in leg if A[i])} | {sum(1 for i in com if A[i])} | {sum(1 for i in dif if A[i])} | {t(lambda a,b:a<b)}/{t(lambda a,b:a==b)}/{t(lambda a,b:a>b)} | {cons} | {ped} | {vict}")

S={n:{i for i in ids if av(c,i)} for n,c in R.items()}
print('\n## Cruce de casos')
for x,y in (('v1 Tito sin','v3 Tito sin'),('v1 Tito ind','v3 Tito ind'),('v1 solo','v3 solo'),('v1 solo','v1 solo Win'),('v1 Tito ind','v1 Tito ind Win'),('v1 solo','v1 solo rep'),('v1 Tito sin','v1 control'),('v3 Tito sin','v3 orden v1'),('v3 Tito sin','v3 roles'),('v3 Tito sin','v4 roles'),('v1 control','v4 roles')):
    print(f"{x} -> {y}: estafas pierde {sorted(S[x]-S[y]&set(vis))} gana {len(S[y]-S[x]&set(vis))}; FA quita {sorted(S[x]-S[y]&set(leg))} agrega {len(S[y]-S[x]&set(leg))}")
print('v1 Tito sin + v3 Tito sin: union',len((S['v1 Tito sin']|S['v3 Tito sin'])&set(vis)),len((S['v1 Tito sin']|S['v3 Tito sin'])&set(leg)),'interseccion',len(S['v1 Tito sin']&S['v3 Tito sin']&set(vis)),len(S['v1 Tito sin']&S['v3 Tito sin']&set(leg)))

print('\n## Veto por riesgo del primer aviso (estafas/FA; censurado)')
for n in ('v1 Tito sin','v3 Tito sin'):
    print(n,' '.join(f">={x}: {sum(1 for i in vis if av(R[n],i) and float(fila(R[n],i)['riesgo'])>=x)}/{sum(1 for i in leg if av(R[n],i) and float(fila(R[n],i)['riesgo'])>=x)}" for x in (.5,.6,.7,.8,.9)))
print('\n## Puntaje de Tito al activarse (mediana), v1 Tito sin')
def act(i): return next((r for r in R['v1 Tito sin'][i] if r['consulta']!='omitida'),None)
for nom,g in (('estafa con aviso',S['v1 Tito sin']&set(vis)),('falsa alarma',S['v1 Tito sin']&set(leg))):
    v=sorted(float(act(i)['tito_puntaje']) for i in g); print(nom,len(v),round(v[len(v)//2],2))
print('\n## Formato, Tito sin indicio')
for n in ('v1 control','v3 Tito sin','v3 orden v1','v3 roles','v4 roles'):
    F=[r for i in ids for r in R[n][i] if r['consulta']!='omitida' and r['alerta_sugerida']=='false']
    print(n,'cita sin alerta',sum(1 for r in F if r['evidencia'].strip()),'de',len(F),'; avisos con podria',sum(1 for i in S[n] if re.search(r'podr[ií]a|puede ser|puede permit',fila(R[n],i)['motivo'].lower())),'de',len(S[n]),'; motivo con OTRA o PROTEGIDA',sum(1 for i in S[n] if re.search(r'\b(OTRA|PROTEGIDA)\b',fila(R[n],i)['motivo'])))

# Lectura propia de las falsas alarmas de Tito sin indicio, sin revisión humana.
CLASES={'Dato de identificación en una gestión legítima':'CV2-D-L-BANCO-001 CV2-D-L-BANCO-002 CV2-D-L-BANCO-004 CV2-D-L-BANCO-005 CV2-D-L-BANCO-006 CV2-D-L-BANCO-010 TR-13-turno-medico-pide-dni',
'Consejo seguro, explicación o negación':'LAB-arca-canal-oficial LAB-banco-app-parafrasis LAB-banco-revisa-app LAB-banco-gasto-sin-pedido LAB-familiar-llama-vos CV2-D-L-WHATSAPP-001 CV2-D-L-WHATSAPP-002 CV2-D-L-WHATSAPP-004 CV2-D-L-TRABAJO-001 CV2-D-L-MEDICO-002',
'Quien ofrece, pregunta o relata es la propia persona':'LG-BANK-VERIF-01-e01 TR-06-banco-alerta-legitima LAB-no-bajes-nada LAB-anses-canal-oficial LG-SUPPORT-INFO-01-e01 LG-SUPPORT-INFO-01-e02 CV2-D-L-ORGANISMO_PREVISIONAL-001 CV2-D-L-SOPORTE-004 CV2-D-L-ESCUELA-004',
'Dinero o encargo cotidiano entre conocidos':'CV2-D-L-FAMILIAR-005 CV2-D-L-FAMILIAR-002 TR-05-asado-con-transferencia TR-11-familiar-real-pide-plata CV2-D-L-TRABAJO-003 CV2-D-L-SOPORTE-005 CV2-D-L-DELIVERY-001',
'Frase ambigua o pedido inexistente':'TR-08-frase-cortada-candado CV2-D-L-PREMIO-002'}
CLASES={k:set(v.split()) for k,v in CLASES.items()}
assert set().union(*CLASES.values())==S['v3 Tito sin']&set(leg) and sum(map(len,CLASES.values()))==35
COL=('v1 control','v3 Tito sin','v3 orden v1','v3 roles','v4 roles')
print('\n## Clases de falsa alarma',COL)
for k,v in CLASES.items(): print(k,[len(v&S[n]) for n in COL])
print('fuera de las clases',{n:sorted((S[n]&set(leg))-set().union(*CLASES.values())) for n in COL})
print('\n## Estafas con pedido sin aviso en v4',[i for i in vis if tr(i) and i not in S['v4 roles']])
