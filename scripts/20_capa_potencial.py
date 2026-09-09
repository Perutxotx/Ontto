import pandas as pd, numpy as np, unicodedata
def n(s): return unicodedata.normalize('NFKD',str(s or '')).encode('ascii','ignore').decode().lower().strip()
D='c:/Users/Peru/Desktop/Ontto App/datos/'
f=pd.read_csv(D+'gipuzkoa_forestal.csv')
s=pd.read_csv('masas_sustrato.csv')[['OBJECTID','serie_nombre','sustrato']]
d=f.merge(s,on='OBJECTID',how='left')
d=d[d.SP1_es.notna()].copy()

UMBRAL=60.0
d['luminoso']=d.FCCARB<UMBRAL

HAYA=['haya']
ROBLE=['roble pedunculado','roble americano','roble humilis','roble','rebollo','marojal',
       'bosque mixto atlantico','castano','abedul','bosque mixto de cantil']
def grupo(sp):
    x=n(sp)
    if x in [n(k) for k in HAYA]: return 'hayedo'
    if x in [n(k) for k in ROBLE]: return 'robledal'
    return 'sin_dato'
d['grupo_nav']=d.SP1_es.map(grupo)

# Coeficientes MIC1 medidos por el Gobierno de Navarra (kg/ha/ano)
HAY={('acido',True):5.16, ('acido',False):2.62, ('basico',True):1.54, ('basico',False):0.19}
ROB=4.40                     # Navarra no desglosa el robledal
def coef(r):
    if r.grupo_nav=='hayedo':
        su = r.sustrato if r.sustrato in ('acido','basico') else None
        if su is None: return np.nan
        return HAY[(su, bool(r.luminoso))]
    if r.grupo_nav=='robledal':
        if r.sustrato=='basico': return np.nan
        return ROB
    return np.nan
d['mic1_kg_ha']=d.apply(coef,axis=1)
d['mic1_kg']=d.mic1_kg_ha*d.area_ha
d.to_csv('potencial_mic1.csv',index=False)

print('CAPA POTENCIAL — produccion esperada de MIC1 (Boletus spp.)')
print('umbral de luminosidad: FCCARB < %.0f %%'%UMBRAL)
print()
con=d[d.mic1_kg_ha.notna()]
print('superficie con coeficiente: %.0f ha de %.0f (%.0f%%)'%(
    con.area_ha.sum(), d.area_ha.sum(), 100*con.area_ha.sum()/d.area_ha.sum()))
print('produccion potencial total: %.0f kg/ano'%con.mic1_kg.sum())
print('media ponderada: %.2f kg/ha/ano'%(con.mic1_kg.sum()/con.area_ha.sum()))
print()
print('%-34s %9s %8s %11s'%('CLASE','ha','kg/ha','kg/ano'))
print('-'*66)
g=con.groupby(['grupo_nav','sustrato','luminoso'])
rows=[]
for k,x in g:
    rows.append((k, x.area_ha.sum(), x.mic1_kg_ha.iloc[0], x.mic1_kg.sum()))
rows.sort(key=lambda r:-r[3])
for (gr,su,lu),ha,c,kg in rows:
    lab='%s · %s · %s'%(gr, su, 'luminoso' if lu else 'sombrio')
    print('%-34s %9.0f %8.2f %11.0f'%(lab,ha,c,kg))
print()
sd=d[d.mic1_kg_ha.isna()]
print('SIN COEFICIENTE: %.0f ha'%sd.area_ha.sum())
for k,v in sd.groupby('SP1_es').area_ha.sum().sort_values(ascending=False).head(8).items():
    print('   %-34s %8.0f ha'%(str(k)[:34],v))
