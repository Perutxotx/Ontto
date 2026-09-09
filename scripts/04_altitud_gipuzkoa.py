import tifffile, numpy as np, shapefile, shapely, pickle, csv, time
from shapely.geometry import shape

t0=time.time()
A = tifffile.imread('mdt_lidar_2017_25m_etrs89.tif').astype('float32')
A[A < -1e30] = np.nan
OX, OY, PX = 461062.5, 4811737.5, 25.0
nrow, ncol = A.shape
def col_of(x): return (x-OX)/PX
def row_of(y): return (OY-y)/PX

tr=shapefile.Reader('../forestal/terr/TERRITORIOS_5000_ETRS89')
for sr in tr.iterShapeRecords():
    if 'GIPUZKOA' in sr.record[1]: gip=shape(sr.shape.__geo_interface__).buffer(0)
gs = gip.simplify(15); shapely.prepare(gs)

c0,c1 = int(np.floor(col_of(gip.bounds[0]))), int(np.ceil(col_of(gip.bounds[2])))+1
r0,r1 = int(np.floor(row_of(gip.bounds[3]))), int(np.ceil(row_of(gip.bounds[1])))+1
c0,r0 = max(c0,0), max(r0,0); c1,r1 = min(c1,ncol), min(r1,nrow)
sub = A[r0:r1, c0:c1]
xs = OX + np.arange(c0,c1)*PX
ys = OY - np.arange(r0,r1)*PX
X,Y = np.meshgrid(xs, ys)
print('ventana:', sub.shape, ' (%.0fs)'%(time.time()-t0), flush=True)
inside = shapely.contains_xy(gs, X.ravel(), Y.ravel()).reshape(sub.shape)
print('mascara lista (%.0fs)'%(time.time()-t0), flush=True)

v = sub[inside & np.isfinite(sub)]
print()
print('=== ALTITUD EN GIPUZKOA (MDT LiDAR 2017, 25 m) ===')
print('pixeles validos: %d  = %.0f ha' % (v.size, v.size*625/1e4))
for q in [0,1,5,25,50,75,95,99,100]:
    print('   p%-3d %7.1f m' % (q, np.percentile(v,q)))
print('   media %.1f m   desv %.1f' % (v.mean(), v.std()))
print()
bandas=[(0,100),(100,200),(200,300),(300,400),(400,500),(500,600),(600,700),(700,800),
        (800,1000),(1000,1200),(1200,1600)]
print('%-14s %10s %7s' % ('BANDA','ha','%'))
tot=v.size*625/1e4
for a,b in bandas:
    n=((v>=a)&(v<b)).sum()*625/1e4
    print('%-14s %10.0f %6.1f' % ('%d-%d m'%(a,b), n, 100*n/tot))
np.save('gip_mask.npy', inside); np.save('gip_win.npy', np.array([r0,r1,c0,c1]))
print('\nnegativos (<0 m): %d px = %.0f ha' % ((v<0).sum(), (v<0).sum()*625/1e4))
