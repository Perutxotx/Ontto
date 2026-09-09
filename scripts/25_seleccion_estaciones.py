import pandas as pd, numpy as np, os, sys, time
sys.path.insert(0,'../suelo')
BASE='atlas_est/01_Estaciones meteorologicas'
inv=pd.read_excel(BASE+'/01_Descripcion/01_Estaciones meteorologicas.xlsx',header=1)
inv.columns=[str(c).strip() for c in inv.columns]
inv['ALTITUD']=pd.to_numeric(inv['ALTITUD'],errors='coerce'); inv['COD']=inv['COD'].astype(str).str.strip()
inv=inv.dropna(subset=['ALTITUD']).drop_duplicates('COD')
zona=inv[(inv.LON_WGS84>-2.90)&(inv.LON_WGS84<-1.55)&(inv.LAT_WGS84>42.80)&(inv.LAT_WGS84<43.50)]

def carga(var):
    fr=[]
    for f in os.listdir(f'{BASE}/{var}'):
        d=pd.read_csv(f'{BASE}/{var}/{f}',encoding='latin-1',low_memory=False)
        d.columns=[str(c).strip() for c in d.columns]
        d=d.rename(columns={d.columns[0]:'fecha'})
        d['fecha']=d['fecha'].astype(str).str.strip()
        d=d[d['fecha'].str.fullmatch(r'\d{8}')]
        d['fecha']=pd.to_datetime(d['fecha'],format='%Y%m%d')
        fr.append(d.set_index('fecha').replace(-9999.0,np.nan))
    o=pd.concat(fr,axis=1); return o.loc[:,~o.columns.duplicated()]

pr=carga('pr')*0.1; tx=carga('tasmax')*0.1; tn=carga('tasmin')*0.1
comunes=[c for c in zona.COD if c in pr.columns and c in tx.columns and c in tn.columns]
z=zona.set_index('COD').loc[comunes]
print('estaciones con las tres variables: %d'%len(comunes))

# completitud en la ventana ago-nov
oto=pr.index.month.isin([8,9,10,11])
comp=pd.DataFrame({'pr':pr.loc[oto,comunes].notna().mean(),
                   'tx':tx.loc[oto,comunes].notna().mean(),
                   'tn':tn.loc[oto,comunes].notna().mean()}).min(axis=1)
buenas=comp[comp>=0.85].index.tolist()
print('con >=85%% de datos en agosto-noviembre: %d'%len(buenas))
zb=z.loc[buenas]
print('  altitudes: %.0f - %.0f m (mediana %.0f)'%(zb.ALTITUD.min(),zb.ALTITUD.max(),zb.ALTITUD.median()))
print()
print('%-8s %-30s %6s %6s'%('COD','NOMBRE','m','% dat'))
for c in sorted(buenas,key=lambda c:-z.loc[c,'ALTITUD']):
    print('%-8s %-30s %6.0f %6.0f'%(c,str(z.loc[c,'NOMBRE'])[:30],z.loc[c,'ALTITUD'],100*comp[c]))
np.save('buenas.npy',np.array(buenas))
pr[buenas].to_pickle('pr_b.pkl'); tx[buenas].to_pickle('tx_b.pkl'); tn[buenas].to_pickle('tn_b.pkl')
zb.to_csv('est_buenas.csv')
