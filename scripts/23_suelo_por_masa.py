import numpy as np, shapely, pickle, csv, time, pandas as pd, sys
sys.path.insert(0,'.')
from pedotransfer import agua_disponible_mm, saxton_rawls
ARC=np.load('Arcilla_100_50m.npy'); ARE=np.load('Arena_100_50m.npy'); LIM=np.load('Limo_100_50m.npy')
OX,OY,PX=np.load('geo_50m.npy')
H,Wd=ARC.shape
print('raster suelo:',ARC.shape,' pixel %.2f m'%PX)
geoms=pickle.load(open('../forestal/geoms.pkl','rb'))
out=open('masas_suelo.csv','w',newline='',encoding='utf-8')
w=csv.writer(out); w.writerow(['OBJECTID','SP1_es','area_ha','arcilla_pct','arena_pct','limo_pct','awc_mm','npx'])
rows=[]; t0=time.time(); n=0; sin=0
for d,g,ha in geoms:
    if not d['SP1_es']: continue
    n+=1
    if n%20000==0: print('  %d (%.0fs)'%(n,time.time()-t0),flush=True)
    x0,y0,x1,y1=g.bounds
    c0=max(int((x0-OX)/PX),0); c1=min(int((x1-OX)/PX)+2,Wd)
    r0=max(int((OY-y1)/PX),0); r1=min(int((OY-y0)/PX)+2,H)
    if c1<=c0 or r1<=r0: sin+=1; continue
    sub=ARC[r0:r1,c0:c1]
    xs=OX+(np.arange(c0,c1)+0.5)*PX; ys=OY-(np.arange(r0,r1)+0.5)*PX
    X,Y=np.meshgrid(xs,ys)
    m=shapely.contains_xy(g,X.ravel(),Y.ravel()).reshape(sub.shape)&np.isfinite(sub)
    if m.sum()==0:
        p=g.representative_point()
        cc=int((p.x-OX)/PX); rr=int((OY-p.y)/PX)
        if not(0<=rr<H and 0<=cc<Wd) or not np.isfinite(ARC[rr,cc]): sin+=1; continue
        arc,are,lim=float(ARC[rr,cc]),float(ARE[rr,cc]),float(LIM[rr,cc]); npx=0
    else:
        arc=float(np.nanmean(sub[m])); are=float(np.nanmean(ARE[r0:r1,c0:c1][m]))
        lim=float(np.nanmean(LIM[r0:r1,c0:c1][m])); npx=int(m.sum())
    awc=float(agua_disponible_mm(are,arc))
    w.writerow([d['OBJECTID'],d['SP1_es'],round(ha,3),round(arc,1),round(are,1),round(lim,1),round(awc,1),npx])
    rows.append((d['SP1_es'],ha,arc,are,lim,awc))
out.close()
print('masas: %d  sin dato de suelo: %d  (%.0fs)'%(n,sin,time.time()-t0))
df=pd.DataFrame(rows,columns=['sp','ha','arcilla','arena','limo','awc'])
print()
print('TEXTURA Y AGUA DISPONIBLE POR ESPECIE (ponderado por superficie)')
print('%-28s %8s %8s %8s %8s %8s'%('','ha','arcilla','arena','limo','awc mm'))
r=[]
for sp,s in df.groupby('sp'):
    if s.ha.sum()<300: continue
    r.append((sp,s.ha.sum(),*[np.average(s[c],weights=s.ha) for c in ['arcilla','arena','limo','awc']]))
r.sort(key=lambda x:-x[5])
for sp,ha,a,ar,l,aw in r: print('%-28s %8.0f %8.1f %8.1f %8.1f %8.0f'%(sp[:28],ha,a,ar,l,aw))
