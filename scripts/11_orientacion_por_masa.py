import numpy as np, shapely, pickle, csv, time, unicodedata, pandas as pd
NN=np.load('northness.npy'); EE=np.load('eastness.npy'); SL=np.load('slope_deg.npy')
r0,r1,c0,c1=np.load('gip_win.npy')
OX,OY,PX=461062.5,4811737.5,25.0
X0,Y1=OX+c0*PX, OY-r0*PX
H,Wd=NN.shape
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

out=open('masas_orientacion.csv','w',newline='',encoding='utf-8')
w=csv.writer(out); w.writerow(['OBJECTID','grupo','SP1_es','area_ha','nortidad','estidad',
                               'azimut_medio','coherencia','pct_umbria','npx'])
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
    sn=SL[rr0:rr1,cc0:cc1]
    xs=X0+np.arange(cc0,cc1)*PX; ys=Y1-np.arange(rr0,rr1)*PX
    X,Y=np.meshgrid(xs,ys)
    m=shapely.contains_xy(g,X.ravel(),Y.ravel()).reshape(sn.shape) & np.isfinite(sn) & (sn>=2.0)
    if m.sum()==0: continue
    nn=NN[rr0:rr1,cc0:cc1][m]; ee=EE[rr0:rr1,cc0:cc1][m]
    mn, me = float(nn.mean()), float(ee.mean())
    az = float(np.degrees(np.arctan2(me,mn)) % 360)
    coh = float(np.hypot(mn,me))                 # 0 = orientaciones dispersas, 1 = ladera uniforme
    umb = float((nn>0).mean()*100)
    w.writerow([d['OBJECTID'],gr,d['SP1_es'],round(ha,3),round(mn,4),round(me,4),
                round(az,1),round(coh,3),round(umb,1),int(m.sum())])
    rows.append((gr,d['SP1_es'],ha,mn,me,coh,umb))
out.close()
print('masas: %d (%.0fs)'%(n,time.time()-t0))

df=pd.DataFrame(rows,columns=['g','sp','ha','nn','ee','coh','umb'])
GN=['Frondosa autoctona','Conifera ECM','Sin simbiosis','Otras']
print('\n=== POR GRUPO (ponderado por superficie) ===')
print('%-22s %9s %9s %9s %9s'%('','ha','nortidad','coherenc','% umbria'))
for k in range(4):
    s=df[df.g==k]
    if not len(s): continue
    print('%-22s %9.0f %9.3f %9.3f %9.1f'%(GN[k],s.ha.sum(),
      np.average(s.nn,weights=s.ha),np.average(s.coh,weights=s.ha),np.average(s.umb,weights=s.ha)))
print('\n=== POR ESPECIE (ordenado por nortidad) ===')
r=[]
for sp,s in df.groupby('sp'):
    if s.ha.sum()<300: continue
    r.append((sp,s.ha.sum(),np.average(s.nn,weights=s.ha),np.average(s.ee,weights=s.ha),
              np.average(s.umb,weights=s.ha)))
r.sort(key=lambda x:-x[2])
print('%-34s %8s %9s %9s %8s'%('ESPECIE','ha','nortidad','estidad','% umbria'))
for sp,a,nn,ee,um in r: print('%-34s %8.0f %9.3f %9.3f %8.1f'%(sp[:34],a,nn,ee,um))
