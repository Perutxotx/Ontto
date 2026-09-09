import tifffile, numpy as np, shapely, pickle, csv, time, unicodedata
from collections import Counter

A = tifffile.imread('mdt_lidar_2017_25m_etrs89.tif').astype('float32')
A[A < -1e30] = np.nan
OX, OY, PX = 461062.5, 4811737.5, 25.0
nrow, ncol = A.shape

geoms = pickle.load(open('../forestal/geoms.pkl','rb'))
def norm(s): return unicodedata.normalize('NFKD',str(s or '')).encode('ascii','ignore').decode().lower().strip()
FR=['haya','roble pedunculado','bosque mixto atlantico','roble americano','encina','quejigo',
    'quejigo faginea','rebollo','castano','roble humilis','roble','abedul','alcornoque','bosque mixto de cantil']
CO=['pino radiata','pino laricio','pino silvestre','pino pinaster','pino halepensis','abeto douglas',
    'alerce','picea europea','pino taeda','otras coniferas','abeto']
SN=['criptomeria','secuoya','chameciparis','eucalipto nitens','eucalipto globulus','eucaliptos',
    'falsa acacia','arboles ripicolas','aliso','platano','fresno','fresno excelsior','sauce','chopo',
    'cedro','aliso de corcega','tulipero','castano japones']
FRn,COn,SNn = {norm(k) for k in FR},{norm(k) for k in CO},{norm(k) for k in SN}
def grupo(sp):
    s=norm(sp)
    if not s: return None
    if s in FRn: return 0
    if s in COn: return 1
    if s in SNn: return 2
    return 3

out=open('masas_altitud.csv','w',newline='',encoding='utf-8')
w=csv.writer(out); w.writerow(['OBJECTID','grupo','SP1_es','area_ha','alt_media','alt_min','alt_max','npx'])
res=[]; t0=time.time(); n=0; sinpx=0
for d,g,ha in geoms:
    gr=grupo(d['SP1_es'])
    if gr is None: continue
    n+=1
    if n%15000==0: print('  %d  (%.0fs)'%(n,time.time()-t0), flush=True)
    x0,y0,x1,y1=g.bounds
    c0=max(int(np.floor((x0-OX)/PX)),0); c1=min(int(np.ceil((x1-OX)/PX))+1,ncol)
    r0=max(int(np.floor((OY-y1)/PX)),0); r1=min(int(np.ceil((OY-y0)/PX))+1,nrow)
    if c1<=c0 or r1<=r0: continue
    sub=A[r0:r1,c0:c1]
    xs=OX+np.arange(c0,c1)*PX; ys=OY-np.arange(r0,r1)*PX
    X,Y=np.meshgrid(xs,ys)
    m=shapely.contains_xy(g,X.ravel(),Y.ravel()).reshape(sub.shape) & np.isfinite(sub)
    if m.sum()==0:
        p=g.representative_point()
        c=int(round((p.x-OX)/PX)); r=int(round((OY-p.y)/PX))
        val=A[r,c] if 0<=r<nrow and 0<=c<ncol else np.nan
        if not np.isfinite(val): sinpx+=1; continue
        am=amin=amax=float(val); npx=0
    else:
        v=sub[m]; am,amin,amax,npx=float(v.mean()),float(v.min()),float(v.max()),int(m.sum())
    w.writerow([d['OBJECTID'],gr,d['SP1_es'],round(ha,3),round(am,1),round(amin,1),round(amax,1),npx])
    res.append((gr,ha,am))
out.close()
print('masas procesadas: %d  sin pixel: %d  (%.0fs)'%(n,sinpx,time.time()-t0))

import numpy as np
res=np.array([(r[0],r[1],r[2]) for r in res])
GN=['Frondosa autoctona','Conifera ECM','Sin simbiosis','Otras']
print()
print('=== ALTITUD MEDIA PONDERADA POR SUPERFICIE ===')
for k in range(4):
    s=res[res[:,0]==k]
    if not len(s): continue
    wm=np.average(s[:,2],weights=s[:,1])
    print('%-22s %8.0f ha   media %5.0f m   p10 %4.0f   p90 %4.0f' %
          (GN[k], s[:,1].sum(), wm,
           np.percentile(np.repeat(s[:,2],np.maximum(s[:,1].astype(int),1)),10),
           np.percentile(np.repeat(s[:,2],np.maximum(s[:,1].astype(int),1)),90)))
