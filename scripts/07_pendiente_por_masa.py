import numpy as np, shapely, pickle, csv, time, unicodedata
SL = np.load('slope_deg.npy')
r0,r1,c0,c1 = np.load('gip_win.npy')
OX,OY,PX = 461062.5, 4811737.5, 25.0
X0, Y1 = OX + c0*PX, OY - r0*PX
H,Wd = SL.shape

geoms = pickle.load(open('../forestal/geoms.pkl','rb'))
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

out=open('masas_pendiente.csv','w',newline='',encoding='utf-8')
w=csv.writer(out); w.writerow(['OBJECTID','grupo','SP1_es','area_ha','pend_grados','pend_pct','pend_max_g','npx'])
rows=[]; t0=time.time(); n=0
for d,g,ha in geoms:
    gr=grupo(d['SP1_es'])
    if gr is None: continue
    n+=1
    if n%20000==0: print('  %d (%.0fs)'%(n,time.time()-t0), flush=True)
    x0,y0,x1,y1=g.bounds
    cc0=max(int((x0-X0)/PX),0); cc1=min(int((x1-X0)/PX)+2,Wd)
    rr0=max(int((Y1-y1)/PX),0); rr1=min(int((Y1-y0)/PX)+2,H)
    if cc1<=cc0 or rr1<=rr0: continue
    sub=SL[rr0:rr1,cc0:cc1]
    xs=X0+np.arange(cc0,cc1)*PX; ys=Y1-np.arange(rr0,rr1)*PX
    X,Y=np.meshgrid(xs,ys)
    m=shapely.contains_xy(g,X.ravel(),Y.ravel()).reshape(sub.shape) & np.isfinite(sub)
    if m.sum()==0:
        p=g.representative_point()
        cc=int(round((p.x-X0)/PX)); rr=int(round((Y1-p.y)/PX))
        if not (0<=rr<H and 0<=cc<Wd): continue
        deg=float(SL[rr,cc]); mx=deg; npx=0
    else:
        v=sub[m]; deg=float(v.mean()); mx=float(v.max()); npx=int(m.sum())
    w.writerow([d['OBJECTID'],gr,d['SP1_es'],round(ha,3),round(deg,2),
                round(np.tan(np.radians(deg))*100,1),round(mx,2),npx])
    rows.append((gr,d['SP1_es'],ha,deg))
out.close()
print('masas: %d (%.0fs)'%(n,time.time()-t0))

import pandas as pd
df=pd.DataFrame(rows,columns=['g','sp','ha','deg'])
df['pct']=np.tan(np.radians(df.deg))*100
GN=['Frondosa autoctona','Conifera ECM','Sin simbiosis','Otras']
print('\n=== PENDIENTE MEDIA POR GRUPO (ponderada por superficie) ===')
for k in range(4):
    s=df[df.g==k]
    if not len(s): continue
    print('%-22s %8.0f ha  %5.1f grados  %5.1f %%' %
          (GN[k], s.ha.sum(), np.average(s.deg,weights=s.ha), np.average(s.pct,weights=s.ha)))
print('\n=== POR ESPECIE ===')
r=[]
for sp,s in df.groupby('sp'):
    if s.ha.sum()<300: continue
    r.append((sp,s.ha.sum(),np.average(s.deg,weights=s.ha),np.average(s.pct,weights=s.ha)))
r.sort(key=lambda x:-x[2])
print('%-34s %8s %8s %7s'%('ESPECIE','ha','grados','%'))
for sp,a,dg,pc in r: print('%-34s %8.0f %8.1f %7.1f'%(sp[:34],a,dg,pc))
