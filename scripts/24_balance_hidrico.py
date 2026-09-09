import pandas as pd, numpy as np
pr=pd.read_pickle('pr_b.pkl'); tx=pd.read_pickle('tx_b.pkl'); tn=pd.read_pickle('tn_b.pkl')
z=pd.read_csv('est_buenas.csv').set_index('COD')
LAT=np.deg2rad(43.1)

def Ra(doy):
    """Radiacion extraterrestre diaria, MJ/m2/dia."""
    dr=1+0.033*np.cos(2*np.pi*doy/365)
    dec=0.409*np.sin(2*np.pi*doy/365-1.39)
    ws=np.arccos(np.clip(-np.tan(LAT)*np.tan(dec),-1,1))
    return (24*60/np.pi)*0.0820*dr*(ws*np.sin(LAT)*np.sin(dec)+np.cos(LAT)*np.cos(dec)*np.sin(ws))

doy=pr.index.dayofyear.values
ra=Ra(doy)
tmed=(tx+tn)/2
# Hargreaves-Samani (FAO-56)
et0=0.0023*(ra[:,None]/2.45)*(tmed.values+17.8)*np.sqrt(np.clip(tx.values-tn.values,0,None))
et0=pd.DataFrame(et0,index=pr.index,columns=pr.columns).clip(lower=0)

AWC=74.0                      # mm, mediana de Gipuzkoa
def balance(p,e,awc=AWC):
    """Modelo de cubo. Devuelve contenido de agua (mm) y ET real."""
    n=len(p); s=np.empty(n); eta=np.empty(n)
    w=awc*0.5
    for i in range(n):
        pi = p[i] if np.isfinite(p[i]) else 0.0
        ei = e[i] if np.isfinite(e[i]) else 0.0
        w = min(awc, w+pi)                                # entra lluvia, escorrenta lo que sobra
        k = w/awc                                          # reduccion por sequedad del suelo
        a = min(w, ei*k)
        w = max(0.0, w-a)
        s[i]=w; eta[i]=a
    return s,eta

res={}
for c in pr.columns:
    s,a=balance(pr[c].values, et0[c].values)
    res[c]=s
S=pd.DataFrame(res,index=pr.index)
S.to_pickle('agua_suelo.pkl'); et0.to_pickle('et0.pkl')

print('BALANCE HIDRICO — contenido de agua del suelo (mm de 74 posibles)')
print()
oto=S.index.month.isin([8,9,10,11])
print('%-8s %-28s %5s %8s %8s %8s'%('COD','NOMBRE','m','ago','sep-oct','nov'))
r=[]
for c in S.columns:
    a=S.loc[S.index.month==8,c].mean()
    so=S.loc[S.index.month.isin([9,10]),c].mean()
    nv=S.loc[S.index.month==11,c].mean()
    r.append((c,str(z.loc[c,'NOMBRE'])[:28],z.loc[c,'ALTITUD'],a,so,nv))
r.sort(key=lambda x:-x[2])
for c,n,al,a,so,nv in r: print('%-8s %-28s %5.0f %8.1f %8.1f %8.1f'%(c,n,al,a,so,nv))

print()
alt=np.array([x[2] for x in r]); ago=np.array([x[3] for x in r]); sepoct=np.array([x[4] for x in r])
b,a0=np.polyfit(alt,ago,1); print('agua en agosto  vs altitud: %+.2f mm/100m  r=%.2f'%(b*100,np.corrcoef(alt,ago)[0,1]))
b,a0=np.polyfit(alt,sepoct,1); print('agua en sep-oct vs altitud: %+.2f mm/100m  r=%.2f'%(b*100,np.corrcoef(alt,sepoct)[0,1]))
print()
print('ET0 media diaria (mm) por mes, media de todas las estaciones:')
for m in [7,8,9,10,11]:
    print('   mes %2d  %.2f mm/dia'%(m, et0.loc[et0.index.month==m].mean().mean()))
