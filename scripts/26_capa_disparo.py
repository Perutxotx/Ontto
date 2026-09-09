"""Capa DISPARO de Ontto — indice diario de probabilidad de fructificacion (0-1).

    DISPARO(t,z) = f_T(T5) x f_W(W5) x f_H(Tmin5) x exclusion

  f_T  respuesta termica gaussiana, optimo 13,2 C          [preprint hayedo 2025]
  f_W  penalizacion por sequedad, solo bajo el 40% de AWC  [balance hidrico propio]
  f_H  corte por helada, nulo bajo -2 C de minima          [preprint: hasta la 1a helada fuerte]
  excl cero si T5>17,5 C y lluvia5<1 mm/dia                [preprint hayedo 2025]

  T(t,z) = T_referencia(t) + gradiente(mes) x (z - 164 m)
  gradiente medido con 169 estaciones del Atlas Climatico.
"""
import pandas as pd, numpy as np

pr=pd.read_pickle('pr_b.pkl'); tx=pd.read_pickle('tx_b.pkl'); tn=pd.read_pickle('tn_b.pkl')
S=pd.read_pickle('agua_suelo.pkl'); z=pd.read_csv('est_buenas.csv').set_index('COD')
MED=['9275B','9269','9086']; AT=[c for c in pr.columns if c not in MED]
ZREF=float(np.average(z.loc[AT,'ALTITUD']))

tmed=((tx[AT]+tn[AT])/2).mean(axis=1); tmin=tn[AT].mean(axis=1)
lluvia=pr[AT].mean(axis=1); agua=S[AT].mean(axis=1); AWC=74.0
LAPSE={7:-0.00360,8:-0.00371,9:-0.00425,10:-0.00540,11:-0.00584,12:-0.00560}
def a_cota(zz,s):
    b=np.array([LAPSE.get(m,-0.00512) for m in s.index.month])
    return s + b*(zz-ZREF)

OPT,SIG=13.2,3.5; T_EXCL,P_EXCL=17.5,1.0; W_MIN=0.40
f_T=lambda t: np.exp(-((t-OPT)/SIG)**2)
f_W=lambda w: np.clip(w/(W_MIN*AWC),0,1)
f_H=lambda tm: np.clip((tm+2.0)/4.0,0,1)

ZS=[0,200,400,600,800,1000]
p5=lluvia.rolling(5,min_periods=3).mean(); w5=agua.rolling(5,min_periods=3).mean()
res={}
for zz in ZS:
    t5=a_cota(zz,tmed).rolling(5,min_periods=3).mean()
    n5=a_cota(zz,tmin).rolling(5,min_periods=3).mean()
    idx=f_T(t5)*f_W(w5)*f_H(n5)
    res[zz]=idx.where(~((t5>T_EXCL)&(p5<P_EXCL)),0.0)
D=pd.DataFrame(res); D.to_pickle('disparo.pkl')
D[D.index.month.isin([8,9,10,11])].round(4).to_csv(
    'c:/Users/Peru/Desktop/Ontto App/datos/disparo_diario_1970_2015.csv')

print('INDICE DISPARO MEDIO POR QUINCENA Y ALTITUD (1970-2015)')
print('%-12s'%'quincena'+''.join('%9d m'%zz for zz in ZS))
for m,d0,nom in [(8,1,'1-15 ago'),(8,16,'16-31 ago'),(9,1,'1-15 sep'),(9,16,'16-30 sep'),
                 (10,1,'1-15 oct'),(10,16,'16-31 oct'),(11,1,'1-15 nov'),(11,16,'16-30 nov')]:
    sel=(D.index.month==m)&(D.index.day>=d0)&(D.index.day<d0+15)
    v=D[sel].mean(); print('%-12s'%nom+''.join('%11.3f'%v[zz] for zz in ZS))
print()
print('PICO DE TEMPORADA')
for zz in ZS:
    s=D[zz]; s=s[s.index.month.isin([8,9,10,11])]
    g=s.groupby([s.index.month,s.index.day]).mean()
    m,d=g.idxmax()
    print('   %4d m -> %2d de %s  (%.3f)'%(zz,d,['','','','','','','','','ago','sep','oct','nov'][m],g.max()))
print()
print('VARIACION INTERANUAL — suma del indice en la ventana ago-nov, a 600 m')
o=D.loc[D.index.month.isin([8,9,10,11]),600]
an=o.groupby(o.index.year).sum(); an=an[an>10]
print('   media %.1f   desviacion %.1f   cv %.0f%%'%(an.mean(),an.std(),100*an.std()/an.mean()))
print('   mejores anos: '+', '.join('%d (%.0f)'%(y,v) for y,v in an.nlargest(5).items()))
print('   peores anos:  '+', '.join('%d (%.0f)'%(y,v) for y,v in an.nsmallest(5).items()))
