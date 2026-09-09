import tifffile, numpy as np
A=tifffile.imread('mdt_lidar_2017_25m_etrs89.tif').astype('float32'); A[A<-1e30]=np.nan
r0,r1,c0,c1=np.load('gip_win.npy'); mask=np.load('gip_mask.npy')
Zb=A[r0-1:r1+1, c0-1:c1+1]
zfill=np.where(np.isfinite(Zb), Zb, np.nanmedian(Zb))
gy,gx=np.gradient(zfill,25.0,25.0); gy=-gy          # filas crecen hacia el sur
gx,gy = gx[1:-1,1:-1], gy[1:-1,1:-1]

# azimut de la linea de maxima pendiente, 0=N, 90=E, sentido horario
asp = np.degrees(np.arctan2(-gx, -gy)) % 360.0
slope = np.load('slope_deg.npy')
Z=A[r0:r1,c0:c1]
valid = mask & np.isfinite(Z)
FLAT = 2.0                                           # umbral de llano en grados
flat = valid & (slope < FLAT)
ok   = valid & (slope >= FLAT)
np.save('aspect_deg.npy', asp.astype('float32'))
np.save('northness.npy', np.cos(np.radians(asp)).astype('float32'))
np.save('eastness.npy',  np.sin(np.radians(asp)).astype('float32'))

print('=== ORIENTACION EN GIPUZKOA (MDT 25 m) ===')
print('superficie total   %.0f ha' % (valid.sum()*625/1e4))
print('llano (<%.0f grados) %.0f ha  (%.1f%%)  -> orientacion indefinida'
      % (FLAT, flat.sum()*625/1e4, 100*flat.sum()/valid.sum()))
print()
oct_ = [('N',337.5,22.5),('NE',22.5,67.5),('E',67.5,112.5),('SE',112.5,157.5),
        ('S',157.5,202.5),('SO',202.5,247.5),('O',247.5,292.5),('NO',292.5,337.5)]
a=asp[ok]; tot=ok.sum()*625/1e4
print('%-5s %10s %7s' % ('OCT','ha','%'))
for nm,lo,hi in oct_:
    m = ((a>=lo)&(a<hi)) if lo<hi else ((a>=lo)|(a<hi))
    n=m.sum()*625/1e4
    print('%-5s %10.0f %6.1f' % (nm, n, 100*n/tot))
umb = ((a>=270)|(a<90)).sum()*625/1e4        # componente norte
sol = ((a>=90)&(a<270)).sum()*625/1e4        # componente sur
print()
print('umbria (NO-N-NE-E) %.0f ha  %.1f%%' % (umb, 100*umb/tot))
print('solana (SE-S-SO-O) %.0f ha  %.1f%%' % (sol, 100*sol/tot))
nn=np.cos(np.radians(a))
print('nortidad media %.3f   (0 = sin sesgo; +1 todo al norte)' % nn.mean())
