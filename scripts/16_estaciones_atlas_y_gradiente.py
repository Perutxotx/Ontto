import pandas as pd, numpy as np, os
BASE='atlas_est/01_Estaciones meteorologicas'
inv=pd.read_excel(BASE+'/01_Descripcion/01_Estaciones meteorologicas.xlsx',header=1)
inv.columns=[str(c).strip() for c in inv.columns]
inv['ALTITUD']=pd.to_numeric(inv['ALTITUD'],errors='coerce')
inv['COD']=inv['COD'].astype(str).str.strip()
inv=inv.dropna(subset=['ALTITUD']).drop_duplicates('COD')
# entorno de Gipuzkoa
zona=inv[(inv.LON_WGS84>-2.90)&(inv.LON_WGS84<-1.55)&(inv.LAT_WGS84>42.80)&(inv.LAT_WGS84<43.50)]
print('estaciones del Atlas en el entorno de Gipuzkoa: %d'%len(zona))

def carga(var):
    fr=[]
    for f in os.listdir(f'{BASE}/{var}'):
        d=pd.read_csv(f'{BASE}/{var}/{f}', encoding='latin-1', low_memory=False)
        d.columns=[str(c).strip() for c in d.columns]
        d=d.rename(columns={d.columns[0]:'fecha'})
        d['fecha']=d['fecha'].astype(str).str.strip()
        d=d[d['fecha'].str.fullmatch(r'\d{8}')]
        d['fecha']=pd.to_datetime(d['fecha'],format='%Y%m%d')
        d=d.set_index('fecha').replace(-9999.0,np.nan)
        fr.append(d)
    out=pd.concat(fr,axis=1)
    return out.loc[:,~out.columns.duplicated()]

pr=carga('pr'); tas=carga('tas')
print('pr: %s   tas: %s'%(str(pr.shape),str(tas.shape)))
cods=[c for c in zona.COD if c in pr.columns]
print('con serie de precipitacion: %d'%len(cods))

# completitud en la ventana de fructificacion
oto = pr.index.month.isin([8,9,10,11])
sub = pr.loc[oto, cods]
comp = 100*sub.notna().mean()
z = zona.set_index('COD').loc[cods]
print()
print('COMPLETITUD (agosto-noviembre, 1970-2015)')
for lo,hi in [(90,101),(70,90),(50,70),(0,50)]:
    n=((comp>=lo)&(comp<hi)).sum()
    print('  %3d-%3d%% de datos: %3d estaciones'%(lo,hi,n))

# gradiente termico de otoño
cods_t=[c for c in zona.COD if c in tas.columns]
zt=zona.set_index('COD').loc[cods_t]
t_oto=tas.loc[tas.index.month.isin([9,10,11]), cods_t]
print()
print('GRADIENTE TERMICO VERTICAL (sep-nov)')
res=[]
for mes,nom in [(9,'septiembre'),(10,'octubre'),(11,'noviembre')]:
    m=tas.loc[tas.index.month==mes, cods_t].mean()*0.1
    ok=m.notna() & (zt.ALTITUD.notna())
    if ok.sum()<10: continue
    b,a=np.polyfit(zt.ALTITUD[ok], m[ok], 1)
    r=np.corrcoef(zt.ALTITUD[ok], m[ok])[0,1]
    print('  %-11s  %.3f C/100 m   r=%.3f   n=%d'%(nom, b*100, r, ok.sum()))
    res.append(b*100)
m=t_oto.mean()*0.1
ok=m.notna()&zt.ALTITUD.notna()
b,a=np.polyfit(zt.ALTITUD[ok],m[ok],1)
print('  %-11s  %.3f C/100 m   r=%.3f   n=%d'%('conjunto', b*100, np.corrcoef(zt.ALTITUD[ok],m[ok])[0,1], ok.sum()))
print()
print('  Temperatura media sep-nov estimada:')
for alt in [0,200,400,600,800,1000]:
    print('     %4d m -> %.1f C'%(alt, a+b*alt))
pr[cods].to_parquet('pr_zona.parquet') if False else None
z.to_csv('estaciones_atlas_zona.csv')
