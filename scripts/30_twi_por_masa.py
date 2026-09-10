import numpy as np, shapely, pickle, csv, time, pandas as pd
TWI=np.load('twi_50m.npy')
r0,r1,c0,c1=np.load('gip_win.npy'); PAD=60; F=2
R0,C0=max(r0-PAD,0),max(c0-PAD,0)
OX,OY,P0=461062.5,4811737.5,25.0
X0=OX+(C0+1)*P0            # centro de la primera celda de 50 m
Y1=OY-(R0+1)*P0
PX=P0*F
H,Wd=TWI.shape
print('TWI %s  origen %.0f, %.0f  pixel %.0f m'%(str(TWI.shape),X0,Y1,PX))
geoms=pickle.load(open('../forestal/geoms.pkl','rb'))
out=open('masas_twi.csv','w',newline='',encoding='utf-8')
w=csv.writer(out); w.writerow(['OBJECTID','SP1_es','area_ha','twi_medio','twi_p90','npx'])
rows=[]; n=0; t0=time.time()
for d,g,ha in geoms:
    if not d['SP1_es']: continue
    n+=1
    x0,y0,x1,y1=g.bounds
    cc0=max(int((x0-X0)/PX),0); cc1=min(int((x1-X0)/PX)+2,Wd)
    rr0=max(int((Y1-y1)/PX),0); rr1=min(int((Y1-y0)/PX)+2,H)
    if cc1<=cc0 or rr1<=rr0: continue
    sub=TWI[rr0:rr1,cc0:cc1]
    xs=X0+np.arange(cc0,cc1)*PX; ys=Y1-np.arange(rr0,rr1)*PX
    X,Y=np.meshgrid(xs,ys)
    m=shapely.contains_xy(g,X.ravel(),Y.ravel()).reshape(sub.shape)&np.isfinite(sub)
    if m.sum()==0:
        p=g.representative_point()
        cc=int((p.x-X0)/PX); rr=int((Y1-p.y)/PX)
        if not(0<=rr<H and 0<=cc<Wd) or not np.isfinite(TWI[rr,cc]): continue
        tm=float(TWI[rr,cc]); t9=tm; npx=0
    else:
        v=sub[m]; tm=float(v.mean()); t9=float(np.percentile(v,90)); npx=int(m.sum())
    w.writerow([d['OBJECTID'],d['SP1_es'],round(ha,3),round(tm,2),round(t9,2),npx])
    rows.append((d['SP1_es'],ha,tm,t9))
out.close()
print('masas: %d  (%.0fs)'%(n,time.time()-t0))
df=pd.DataFrame(rows,columns=['sp','ha','twi','twi90'])
print()
print('TWI MEDIO POR ESPECIE (ponderado por superficie)')
print('%-30s %9s %8s %8s'%('','ha','TWI','TWI p90'))
r=[(sp,s.ha.sum(),np.average(s.twi,weights=s.ha),np.average(s.twi90,weights=s.ha))
   for sp,s in df.groupby('sp') if s.ha.sum()>=300]
r.sort(key=lambda x:-x[2])
for sp,ha,t,t9 in r:
    print('%-30s %9.0f %8.2f %8.2f'%(sp[:30],ha,t,t9))
