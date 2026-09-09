import tifffile, numpy as np, time
t0=time.time()
A=tifffile.imread('mdt_lidar_2017_25m_etrs89.tif').astype('float32'); A[A<-1e30]=np.nan
r0,r1,c0,c1=np.load('gip_win.npy'); mask=np.load('gip_mask.npy')

# ventana ampliada: las sombras vienen de montes de fuera del limite administrativo
PAD=100                                   # 2,5 km de margen
R0,R1 = max(r0-PAD,0), min(r1+PAD, A.shape[0])
C0,C1 = max(c0-PAD,0), min(c1+PAD, A.shape[1])
Zb = A[R0:R1, C0:C1]
Z = np.where(np.isfinite(Zb), Zb, 0.0).astype('float32')
Hh, Ww = Z.shape
PX = 25.0
print('ventana con margen:', Z.shape, flush=True)

gy,gx = np.gradient(Z, PX, PX); gy = -gy
slope = np.arctan(np.hypot(gx,gy))
aspect = np.arctan2(-gx, -gy) % (2*np.pi)          # 0=N, horario

# ---------- angulo de horizonte en 16 acimutes ----------
NAZ = 16
AZS = np.arange(NAZ)*(360.0/NAZ)
MAXD = 80                                          # 2 km de alcance
hor = np.zeros((NAZ, Hh, Ww), dtype='float32')
for k,azd in enumerate(AZS):
    az = np.deg2rad(azd)
    dx, dy = np.sin(az), np.cos(az)                # dy>0 = norte
    best = np.zeros((Hh,Ww), dtype='float32')
    for s in range(1, MAXD+1):
        ox_, oy_ = int(round(dx*s)), int(round(dy*s))
        if ox_==0 and oy_==0: continue
        sh = np.full((Hh,Ww), -9e9, dtype='float32')
        ys0, ys1 = max(0,-(-oy_)), Hh-max(0,(-oy_))   # fila destino = fila - oy_
        src = np.roll(np.roll(Z, -oy_*-1, axis=0), ox_*-1, axis=1)
        # desplazamiento correcto: vecino en direccion (dx,dy) a distancia s
        src = Z
        rr = np.clip(np.arange(Hh)[:,None] - oy_, 0, Hh-1)
        cc = np.clip(np.arange(Ww)[None,:] + ox_, 0, Ww-1)
        sh = Z[rr, cc]
        d = np.hypot(ox_, oy_)*PX
        ang = (sh - Z)/d
        np.maximum(best, ang, out=best)
    hor[k] = np.arctan(best)
    print('  horizonte %3.0f  (%.0fs)'%(azd, time.time()-t0), flush=True)
np.save('horizon16.npy', hor.astype('float32'))
print('horizontes listos (%.0fs)'%(time.time()-t0), flush=True)
