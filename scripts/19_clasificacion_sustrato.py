import pandas as pd, unicodedata
def n(s): return unicodedata.normalize('NFKD',str(s or '')).encode('ascii','ignore').decode().lower().strip()

# Clasificacion de las series de vegetacion de Euskadi por reaccion del sustrato.
# Criterio: alianza fitosociologica y sustrato caracteristico de cada serie.
ACIDO = ['hayedo acidofilo','robledal cantabrico','marojal','robledal de roble albar',
         'roquedos siliceos','robledal subcantabrico']
BASICO = ['hayedo basofilo','hayedo con boj','encinar cantabrico','encinar carrascal',
          'carrascal','quejigar','quejigar estelles','robledal pubescente','roquedos calcareos']
AZONAL = ['aliseda cantabrica','aliseda subatlantica','aliseda submediterranea','marismas',
          'dunas','medios hidroturbosos','lagunas y balsas','acantilados']
INCIERTO = ['bosque mixto atlantico']   # suelos ricos, a menudo coluviales o margosos

def clase(s):
    x=n(s)
    if x in [n(k) for k in ACIDO]: return 'acido'
    if x in [n(k) for k in BASICO]: return 'basico'
    if x in [n(k) for k in AZONAL]: return 'azonal'
    if x in [n(k) for k in INCIERTO]: return 'incierto'
    return 'sin_clasificar'

d=pd.read_csv('masas_serie_vegetacion.csv')
d['sustrato']=d.serie_nombre.map(clase)
d.to_csv('masas_sustrato.csv',index=False)
a=d[d.SP1_es.notna()]
print('SUSTRATO DE LA SUPERFICIE ARBOLADA DE GIPUZKOA')
t=a.groupby('sustrato').area_ha.sum().sort_values(ascending=False); tot=t.sum()
for k,v in t.items(): print('  %-16s %8.0f ha  %5.1f%%'%(k,v,100*v/tot))
print()
print('SUSTRATO POR ESPECIE (habitat MIC1)')
print('%-24s %9s %9s %9s %9s %9s'%('','total ha','acido','basico','azonal','incierto'))
for sp in ['Haya','Roble pedunculado','Bosque mixto atl\u00e1ntico','Roble americano','Casta\u00f1o','Encina']:
    x=a[a.SP1_es==sp]
    if not len(x): continue
    g=x.groupby('sustrato').area_ha.sum()
    print('%-24s %9.0f %9.0f %9.0f %9.0f %9.0f'%(sp[:24],x.area_ha.sum(),
        g.get('acido',0),g.get('basico',0),g.get('azonal',0),g.get('incierto',0)))
