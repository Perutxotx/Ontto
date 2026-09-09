import tifffile, numpy as np, shapefile, shapely, json, base64, io
from shapely.geometry import shape
from PIL import Image

A = tifffile.imread('mdt_lidar_2017_25m_etrs89.tif').astype('float32')
A[A < -1e30] = np.nan
OX, OY, PX = 461062.5, 4811737.5, 25.0
r0,r1,c0,c1 = np.load('gip_win.npy')
mask = np.load('gip_mask.npy')
Z = A[r0:r1, c0:c1].copy()
Z[~mask] = np.nan
H, Wd = Z.shape
X0, Y1 = OX + c0*PX, OY - r0*PX          # centro del pixel superior-izquierdo
print('raster', Z.shape, 'origen', X0, Y1)

# ---------- rampa hipsometrica ----------
stops = [(0,(31,79,60)), (150,(74,116,72)), (300,(128,146,80)), (450,(178,166,92)),
         (600,(196,148,84)), (800,(178,116,70)), (1000,(156,96,72)), (1250,(186,158,148)),
         (1550,(238,236,232))]
xs = np.array([s[0] for s in stops], float)
cs = np.array([s[1] for s in stops], float)
zz = np.nan_to_num(Z, nan=0.0)
rgb = np.stack([np.interp(zz, xs, cs[:,i]) for i in range(3)], axis=-1)

# ---------- sombreado de relieve ----------
zf = np.where(np.isfinite(Z), Z, np.nanmedian(Z))
gy, gx = np.gradient(zf, PX, PX)
gy = -gy                                  # filas crecen hacia el sur
slope = np.arctan(np.hypot(gx, gy))
aspect = np.arctan2(gy, -gx)
az, alt = np.deg2rad(315.0), np.deg2rad(45.0)
hs = (np.sin(alt)*np.cos(slope) + np.cos(alt)*np.sin(slope)*np.cos(az - aspect))
hs = np.clip(hs, 0, 1)

def png_uri(arr_rgb, alpha):
    im = Image.fromarray(np.dstack([arr_rgb.astype('uint8'), alpha.astype('uint8')]), 'RGBA')
    b = io.BytesIO(); im.save(b, 'PNG', optimize=True)
    return 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode(), len(b.getvalue())

alpha = np.where(np.isfinite(Z), 255, 0)
shaded = np.clip(rgb * (0.55 + 0.75*hs)[...,None], 0, 255)
uri_hyp, n1 = png_uri(shaded, alpha)
uri_flat, n2 = png_uri(rgb, alpha)
g = np.clip(hs*255, 0, 255)
uri_hs, n3 = png_uri(np.dstack([g,g,g]), alpha)
print('png hipso+sombra %.2f MB | plano %.2f MB | sombreado %.2f MB' % (n1/1e6, n2/1e6, n3/1e6))

# ---------- rejilla de consulta a 100 m ----------
step = 4
Zq = Z[::step, ::step]
Zi = np.where(np.isfinite(Zq), np.round(Zq), -32768).astype('<i2')
q_b64 = base64.b64encode(Zi.tobytes()).decode()
print('rejilla consulta', Zi.shape, '%.2f MB b64' % (len(q_b64)/1e6))

# ---------- cota maxima por municipio ----------
mr = shapefile.Reader('../forestal/muni/MUNICIPIOS_5000_ETRS89')
mn = [f[0] for f in mr.fields[1:]]
tr = shapefile.Reader('../forestal/terr/TERRITORIOS_5000_ETRS89')
for sr in tr.iterShapeRecords():
    if 'GIPUZKOA' in sr.record[1]: gip = shape(sr.shape.__geo_interface__).buffer(0)
picos = []
xs_g = X0 + np.arange(Wd)*PX
ys_g = Y1 - np.arange(H)*PX
XX, YY = np.meshgrid(xs_g, ys_g)
for sr in mr.iterShapeRecords():
    d = dict(zip(mn, sr.record))
    if 'GIPUZKOA' not in (d.get('TERRITORIO') or ''): continue
    g = shape(sr.shape.__geo_interface__).buffer(0)
    b = g.bounds
    cc0 = max(int((b[0]-X0)/PX), 0); cc1 = min(int((b[2]-X0)/PX)+2, Wd)
    rr0 = max(int((Y1-b[3])/PX), 0); rr1 = min(int((Y1-b[1])/PX)+2, H)
    if cc1<=cc0 or rr1<=rr0: continue
    sub = Z[rr0:rr1, cc0:cc1]
    m = shapely.contains_xy(g, XX[rr0:rr1, cc0:cc1].ravel(), YY[rr0:rr1, cc0:cc1].ravel()).reshape(sub.shape)
    m &= np.isfinite(sub)
    if not m.any(): continue
    v = np.where(m, sub, -1e9)
    i = np.unravel_index(np.argmax(v), v.shape)
    picos.append({'n': d.get('NOMBRE_TOP',''), 'z': round(float(sub[i]),1),
                  'x': int(XX[rr0+i[0], cc0+i[1]]), 'y': int(YY[rr0+i[0], cc0+i[1]]),
                  'zmin': round(float(np.nanmin(np.where(m, sub, np.nan))),1)})
picos.sort(key=lambda p:-p['z'])
print('municipios:', len(picos), ' top:', [(p['n'],p['z']) for p in picos[:6]])

# ---------- histograma ----------
v = Z[np.isfinite(Z)]
edges = list(range(0,1600,50))
hist = [int(((v>=a)&(v<a+50)).sum()) for a in edges]

payload = {'w':int(Wd),'h':int(H),'x0':float(X0),'y1':float(Y1),'px':PX,'step':step,
           'qw':int(Zi.shape[1]),'qh':int(Zi.shape[0]),'q':q_b64,
           'picos':picos,'hist':hist,'edges':edges,
           'stops':[[s[0],'#%02x%02x%02x'%s[1]] for s in stops],
           'stats':{'min':float(np.nanmin(Z)),'max':float(np.nanmax(Z)),
                    'mean':float(np.nanmean(Z)),'med':float(np.nanmedian(Z)),
                    'ha':float(np.isfinite(Z).sum()*625/1e4)}}
json.dump(payload, open('alt_payload.json','w'), separators=(',',':'))
open('img_hyp.txt','w').write(uri_hyp); open('img_flat.txt','w').write(uri_flat); open('img_hs.txt','w').write(uri_hs)
print('payload %.2f MB' % (len(json.dumps(payload))/1e6))
