import tifffile, numpy as np
A=tifffile.imread('mdt_lidar_2017_25m_etrs89.tif').astype('float32'); A[A<-1e30]=np.nan
r0,r1,c0,c1=np.load('gip_win.npy'); mask=np.load('gip_mask.npy')

# margen de 1 px para que el gradiente no se corte en el borde
Zb = A[r0-1:r1+1, c0-1:c1+1]
zf = np.where(np.isfinite(Zb), Zb, np.nan)
# rellenar huecos con la mediana local para que el gradiente no propague NaN
med = np.nanmedian(zf)
zfill = np.where(np.isfinite(zf), zf, med)
gy, gx = np.gradient(zfill, 25.0, 25.0)
gy = -gy                                    # las filas crecen hacia el sur
slope_deg = np.degrees(np.arctan(np.hypot(gx, gy)))[1:-1, 1:-1]
Z = A[r0:r1, c0:c1]
valid = mask & np.isfinite(Z)
np.save('slope_deg.npy', slope_deg.astype('float32'))

v = slope_deg[valid]
pct = np.tan(np.radians(v))*100
print('=== PENDIENTE EN GIPUZKOA (MDT 25 m) ===')
print('superficie: %.0f ha' % (valid.sum()*625/1e4))
print()
print('%6s %9s %9s' % ('perc','grados','%'))
for q in [1,5,25,50,75,95,99,100]:
    print('%6s %9.1f %9.1f' % ('p%d'%q, np.percentile(v,q), np.percentile(pct,q)))
print('%6s %9.1f %9.1f' % ('media', v.mean(), pct.mean()))
print()
# clases de Mumcu Kucuker (en %)
cls=[(0,10),(10,20),(20,30),(30,45),(45,60),(60,100),(100,1e9)]
print('%-14s %10s %7s' % ('CLASE (%)','ha','%'))
tot=valid.sum()*625/1e4
for a,b in cls:
    n=((pct>=a)&(pct<b)).sum()*625/1e4
    lab = '>%d'%a if b>1e8 else '%d-%d'%(a,b)
    print('%-14s %10.0f %6.1f' % (lab, n, 100*n/tot))
