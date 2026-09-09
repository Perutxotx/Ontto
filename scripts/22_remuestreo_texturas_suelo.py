import tifffile, numpy as np, time, os
F=5
OX,OY,PX = 443421.9896483583, 4819793.1128450884, 10.0036909746
for v in ['Arcilla_100','Arena_100','Limo_100']:
    t0=time.time()
    tmp='_%s.mm'%v
    m=tifffile.imread('%s_ETRS89UTM30N/%s.tif'%(v,v), out=tmp)
    H,Wd=m.shape; h2,w2=H//F, Wd//F
    out=np.empty((h2,w2),dtype='float32')
    BL=400
    for r0 in range(0,h2,BL):
        r1=min(r0+BL,h2)
        blk=np.array(m[r0*F:r1*F, :w2*F], dtype='float32')
        blk[(blk<0)|(blk>100)|~np.isfinite(blk)]=np.nan
        blk=blk.reshape(r1-r0,F,w2,F)
        with np.errstate(all='ignore'):
            out[r0:r1]=np.nanmean(blk,axis=(1,3))
    del m
    try: os.remove(tmp)
    except: pass
    np.save('%s_50m.npy'%v,out)
    ok=np.isfinite(out)
    print('%-12s %s  validos %.1f%%  mediana %.1f%%  (%.0fs)'%(
        v,str(out.shape),100*ok.mean(),float(np.nanmedian(out)),time.time()-t0),flush=True)
np.save('geo_50m.npy',np.array([OX,OY,PX*F]))
print('listo')
