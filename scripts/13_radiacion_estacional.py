import tifffile, numpy as np, time
t0=time.time()
A=tifffile.imread('mdt_lidar_2017_25m_etrs89.tif').astype('float32'); A[A<-1e30]=np.nan
r0,r1,c0,c1=np.load('gip_win.npy'); mask=np.load('gip_mask.npy')
PAD=100
R0,R1=max(r0-PAD,0),min(r1+PAD,A.shape[0]); C0,C1=max(c0-PAD,0),min(c1+PAD,A.shape[1])
Z=np.where(np.isfinite(A[R0:R1,C0:C1]),A[R0:R1,C0:C1],0.0).astype('float32')
PX=25.0; Hh,Ww=Z.shape
gy,gx=np.gradient(Z,PX,PX); gy=-gy
slope=np.arctan(np.hypot(gx,gy)).astype('float32')
aspect=(np.arctan2(-gx,-gy)%(2*np.pi)).astype('float32')
hor=np.load('horizon16.npy')                     # (16,H,W) radianes
NAZ=16; AZS=np.arange(NAZ)*(2*np.pi/NAZ)

LAT=np.deg2rad(43.15)
I0=1367.0
acc=np.zeros((Hh,Ww),dtype='float32')            # Wh/m2 acumulados
acc_flat=0.0                                     # referencia: llano horizontal
DT=0.5                                           # paso de 30 min
dias=list(range(213,335,3))                      # 1 ago - 30 nov, cada 3 dias
nsun=0
for n in dias:
    dec=np.deg2rad(23.45*np.sin(np.deg2rad(360*(284+n)/365.0)))
    for t in np.arange(4.0,20.0,DT):
        h=np.deg2rad(15.0*(t-12.0))
        sinel=np.sin(LAT)*np.sin(dec)+np.cos(LAT)*np.cos(dec)*np.cos(h)
        if sinel<=0.02: continue
        el=np.arcsin(sinel)
        caz=(np.sin(dec)*np.cos(LAT)-np.cos(dec)*np.sin(LAT)*np.cos(h))/max(np.cos(el),1e-6)
        az=np.arccos(np.clip(caz,-1,1))
        if h>0: az=2*np.pi-az                     # tarde -> oeste
        # masa de aire y transmitancia de cielo claro (Kasten-Young simplificada)
        m=1.0/(sinel+0.50572*(np.degrees(el)+6.07995)**-1.6364)
        I=I0*0.7**(m**0.678)
        # incidencia sobre el plano inclinado
        cosi=(np.cos(slope)*sinel + np.sin(slope)*np.cos(el)*np.cos(az-aspect))
        np.clip(cosi,0,None,out=cosi)
        # sombra proyectada: interpolacion entre los dos acimutes vecinos
        k=az/(2*np.pi/NAZ); k0=int(np.floor(k))%NAZ; k1=(k0+1)%NAZ; f=k-np.floor(k)
        hz=hor[k0]*(1-f)+hor[k1]*f
        vis=(el>hz).astype('float32')
        acc += (I*DT)*cosi*vis
        acc_flat += I*DT*sinel
        nsun+=1
print('posiciones solares: %d  (%.0fs)'%(nsun,time.time()-t0), flush=True)

rad = acc[PAD if r0>=PAD else r0-R0 : (PAD if r0>=PAD else r0-R0)+(r1-r0),
          PAD if c0>=PAD else c0-C0 : (PAD if c0>=PAD else c0-C0)+(c1-c0)] / 1000.0   # kWh/m2
idx = rad/(acc_flat/1000.0)                       # indice relativo al llano
np.save('rad_kwh.npy', rad.astype('float32')); np.save('rad_idx.npy', idx.astype('float32'))

# hillshade clasico de Navarra, para comparar
sl=np.load('slope_deg.npy'); asp=np.load('aspect_deg.npy')
slr=np.deg2rad(sl); aspr=np.deg2rad(asp)
hs=np.clip(np.sin(np.deg2rad(45))*np.cos(slr)+np.cos(np.deg2rad(45))*np.sin(slr)*np.cos(np.deg2rad(315)-aspr),0,1)
np.save('hillshade.npy', hs.astype('float32'))

Zc=A[r0:r1,c0:c1]; ok=mask&np.isfinite(Zc)
v=rad[ok]; vi=idx[ok]
print()
print('=== RADIACION SOLAR POTENCIAL, 1 AGO - 30 NOV (cielo claro) ===')
print('referencia llano horizontal: %.0f kWh/m2' % (acc_flat/1000.0))
for q in [1,5,25,50,75,95,99]:
    print('  p%-3d %8.0f kWh/m2   indice %.3f' % (q,np.percentile(v,q),np.percentile(vi,q)))
print('  media %7.0f kWh/m2   indice %.3f' % (v.mean(), vi.mean()))
print()
sh=hs[ok]
print('correlacion radiacion estacional vs hillshade clasico: r = %.3f' % np.corrcoef(v,sh)[0,1])
nn=np.load('northness.npy')[ok]
print('correlacion radiacion vs nortidad:                     r = %.3f' % np.corrcoef(v,nn)[0,1])
