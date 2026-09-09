import shapefile, csv, json, time
from collections import Counter
from shapely.geometry import shape
from shapely.prepared import prep
from pyproj import Transformer

t0=time.time()
tr=shapefile.Reader('terr/TERRITORIOS_5000_ETRS89')
for sr in tr.iterShapeRecords():
    if 'GIPUZKOA' in sr.record[1]:
        gip_full=shape(sr.shape.__geo_interface__).buffer(0)
gip=gip_full.simplify(40)                      # para el test punto-en-poligono
pgip=prep(gip)
minx,miny,maxx,maxy=gip_full.bounds
print('Gipuzkoa: %.0f ha  vertices %d -> %d' % (gip_full.area/1e4,
      len(gip_full.geoms[0].exterior.coords) if hasattr(gip_full,'geoms') else 0, 0), flush=True)

r=shapefile.Reader('INV_FORESTAL_2024_10000_ETRS89')
names=[f[0] for f in r.fields[1:]]
keep=['OBJECTID','TIPES_es','SP1_es','O1','EMASA1','SP2_es','O2','SP3_es','FCCARB','Shape_Area']
out=open('gipuzkoa_forestal.csv','w',newline='',encoding='utf-8')
w=csv.writer(out); w.writerow(keep+['area_ha'])

geoms=[]   # (attrs, geom_utm)
n=cand=inside=0
for sr in r.iterShapeRecords():
    n+=1
    if n%40000==0: print('  %d/%d  (%.0fs)'%(n,220606,time.time()-t0), flush=True)
    b=sr.shape.bbox
    if b[2]<minx or b[0]>maxx or b[3]<miny or b[1]>maxy: continue
    cand+=1
    g=shape(sr.shape.__geo_interface__)
    if not g.is_valid: g=g.buffer(0)
    if g.is_empty: continue
    if not pgip.contains(g.representative_point()): continue
    inside+=1
    d=dict(zip(names,sr.record))
    ha=(d['Shape_Area'] or 0)/1e4
    w.writerow([d[k] for k in keep]+['%.4f'%ha])
    geoms.append((d,g,ha))
out.close()
print('total=%d bbox=%d gipuzkoa=%d  (%.0fs)'%(n,cand,inside,time.time()-t0), flush=True)
import pickle
pickle.dump(geoms, open('geoms.pkl','wb'))
print('guardado geoms.pkl', flush=True)
