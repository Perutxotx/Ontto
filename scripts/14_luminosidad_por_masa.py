import numpy as np, shapely, pickle, csv, time, unicodedata, pandas as pd
RAD=np.load('rad_kwh.npy'); IDX=np.load('rad_idx.npy'); HS=np.load('hillshade.npy')
r0,r1,c0,c1=np.load('gip_win.npy')
OX,OY,PX=461062.5,4811737.5,25.0
X0,Y1=OX+c0*PX,OY-r0*PX; H,Wd=RAD.shape
geoms=pickle.load(open('../forestal/geoms.pkl','rb'))
def norm(s): return unicodedata.normalize('NFKD',str(s or '')).encode('ascii','ignore').decode().lower().strip()
FR=['haya','roble pedunculado','bosque mixto atlantico','roble americano','encina','quejigo',
    'quejigo faginea','rebollo','castano','roble humilis','roble','abedul','alcornoque','bosque mixto de cantil']
CO=['pino radiata','pino laricio','pino silvestre','pino pinaster','pino halepensis','abeto douglas',
    'alerce','picea europea','pino taeda','otras coniferas','abeto']
SN=['criptomeria','secuoya','chameciparis','eucalipto nitens','eucalipto globulus','eucaliptos',
    'falsa acacia','arboles ripicolas','aliso','platano','fresno','fresno excelsior','sauce','chopo',
    'cedro','aliso de corcega','tulipero','castano japones']
FRn,COn,SNn={norm(k) for k in FR},{norm(k) for k in CO},{norm(k) for k in SN}
def grupo(sp):
    s=norm(sp)
    if not s: return None
    if s in FRn: return 0
    if s in COn: return 1
    if s in SNn: return 2
    return 3

# umbral sombrio/luminoso al estilo Navarra: mediana del territorio
med_hs=float(np.median(HS[np.isfinite(HS)]))
out=open('masas_luminosidad.csv','w',newline='',encoding='utf-8')
w=csv.writer(out); w.writerow(['OBJECTID','grupo','SP1_es','area_ha','rad_kwh','rad_indice',
                               'hillshade','clase_navarra','npx'])
rows=[]; t0=time.time(); n=0
for d,g,ha in geoms:
    gr=grupo(d['SP1_es'])
    if gr is None: continue
    n+=1
    if n%20000==0: print('  %d (%.0fs)'%(n,time.time()-t0),flush=True)
    x0,y0,x1,y1=g.bounds
    cc0=max(int((x0-X0)/PX),0); cc1=min(int((x1-X0)/PX)+2,Wd)
    rr0=max(int((Y1-y1)/PX),0); rr1=min(int((Y1-y0)/PX)+2,H)
    if cc1<=cc0 or rr1<=rr0: continue
    sub=RAD[rr0:rr1,cc0:cc1]
    xs=X0+np.arange(cc0,cc1)*PX; ys=Y1-np.arange(rr0,rr1)*PX
    X,Y=np.meshgrid(xs,ys)
    m=shapely.contains_xy(g,X.ravel(),Y.ravel()).reshape(sub.shape)&np.isfinite(sub)
    if m.sum()==0: continue
    rk=float(sub[m].mean()); ri=float(IDX[rr0:rr1,cc0:cc1][m].mean())
    hv=float(HS[rr0:rr1,cc0:cc1][m].mean())
    w.writerow([d['OBJECTID'],gr,d['SP1_es'],round(ha,3),round(rk,1),round(ri,4),
                round(hv,4),'luminoso' if hv>=med_hs else 'sombrio',int(m.sum())])
    rows.append((gr,d['SP1_es'],ha,rk,ri,hv))
out.close()
print('masas: %d (%.0fs)'%(n,time.time()-t0))
df=pd.DataFrame(rows,columns=['g','sp','ha','rad','idx','hs'])
GN=['Frondosa autoctona','Conifera ECM','Sin simbiosis','Otras']
print('\n=== POR GRUPO ===')
print('%-22s %9s %11s %8s'%('','ha','kWh/m2','indice'))
for k in range(4):
    s=df[df.g==k]
    if not len(s): continue
    print('%-22s %9.0f %11.0f %8.3f'%(GN[k],s.ha.sum(),
        np.average(s.rad,weights=s.ha),np.average(s.idx,weights=s.ha)))
print('\n=== POR ESPECIE (ordenado por radiacion) ===')
r=[]
for sp,s in df.groupby('sp'):
    if s.ha.sum()<300: continue
    r.append((sp,s.ha.sum(),np.average(s.rad,weights=s.ha),np.average(s.idx,weights=s.ha)))
r.sort(key=lambda x:-x[2])
print('%-34s %8s %10s %8s'%('ESPECIE','ha','kWh/m2','indice'))
for sp,a,rk,ri in r: print('%-34s %8.0f %10.0f %8.3f'%(sp[:34],a,rk,ri))
