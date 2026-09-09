import shapefile, pickle, numpy as np, csv, time, unicodedata
from shapely.geometry import shape
from shapely.strtree import STRtree
import shapely

t0=time.time()
r=shapefile.Reader('CT_SERIES_VEGETACION_50000_ETRS89/CT_SERIES_VEGETACION_50000_ETRS89',encoding='latin-1')
fn=[f[0] for f in r.fields[1:]]
partes=[]; info=[]
for sr in r.iterShapeRecords():
    d=dict(zip(fn,sr.record))
    g=shape(sr.shape.__geo_interface__).buffer(0)
    geoms=list(g.geoms) if g.geom_type=='MultiPolygon' else [g]
    for p in geoms:
        if p.is_empty: continue
        partes.append(p); info.append((str(d['CODIGO']).strip(), str(d['NOMBRE_ES']).strip()))
print('poligonos de series: %d  (%.0fs)'%(len(partes),time.time()-t0),flush=True)
tree=STRtree(partes)

geoms=pickle.load(open('../forestal/geoms.pkl','rb'))
out=open('masas_serie_vegetacion.csv','w',newline='',encoding='utf-8')
w=csv.writer(out); w.writerow(['OBJECTID','SP1_es','area_ha','serie_cod','serie_nombre'])
from collections import Counter
cnt=Counter(); n=0; sin=0
for d,g,ha in geoms:
    n+=1
    if n%20000==0: print('  %d (%.0fs)'%(n,time.time()-t0),flush=True)
    p=g.representative_point()
    idx=tree.query(p)
    cod=nom=''
    for i in idx:
        if partes[i].contains(p): cod,nom=info[i]; break
    if not cod:
        # sin coincidencia: buscar el poligono mas cercano
        j=tree.nearest(p)
        if j is not None: cod,nom=info[int(j)]; sin+=1
    w.writerow([d['OBJECTID'],d['SP1_es'] or '',round(ha,3),cod,nom])
    if d['SP1_es']: cnt[(d['SP1_es'],nom)]+=ha
out.close()
print('masas: %d  asignadas por proximidad: %d  (%.0fs)'%(n,sin,time.time()-t0))
pickle.dump(cnt,open('cruce_cnt.pkl','wb'))
