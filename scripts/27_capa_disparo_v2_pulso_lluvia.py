"""Capa DISPARO v2 — anade el pulso de lluvia con retardo (factor 2).

    DISPARO(t,z) = f_T(T5) x f_P(Pacc) x f_W(W5) x f_H(Tmin5) x exclusion

  f_P  pulso de lluvia: 1-exp(-Pacc/40), sobre la lluvia acumulada en una
       ventana de 15 dias que termina 10 dias antes del dia evaluado.

  Justificacion del retardo: la iniciacion de primordios requiere el episodio
  humedo, y el desarrollo del carpoforo hasta tamano recolectable lleva de 5 a
  15 dias. La literatura describe desfases de 1 a 4 semanas.
  NO esta ajustado con datos: es una eleccion informada, no un parametro estimado.

  Por que no duplica el termino f_W: el cubo de suelo satura a 74 mm y pierde
  la informacion del episodio; el pulso conserva la magnitud del evento.
"""
import pandas as pd, numpy as np
pr=pd.read_pickle('pr_b.pkl'); tx=pd.read_pickle('tx_b.pkl'); tn=pd.read_pickle('tn_b.pkl')
S=pd.read_pickle('agua_suelo.pkl'); z=pd.read_csv('est_buenas.csv').set_index('COD')
MED=['9275B','9269','9086']; AT=[c for c in pr.columns if c not in MED]
ZREF=float(np.average(z.loc[AT,'ALTITUD']))
tmed=((tx[AT]+tn[AT])/2).mean(axis=1); tmin=tn[AT].mean(axis=1)
p=pr[AT].mean(axis=1); agua=S[AT].mean(axis=1); AWC=74.0
LAPSE={7:-.0036,8:-.00371,9:-.00425,10:-.0054,11:-.00584,12:-.0056}
def cota(zz,s):
    b=np.array([LAPSE.get(m,-.00512) for m in s.index.month]); return s+b*(zz-ZREF)
OPT,SIG=13.2,3.5; T_EXCL,P_EXCL=17.5,1.0; W_MIN=0.40
LAG,VENT,P0 = 10, 15, 40.0
f_T=lambda t:np.exp(-((t-OPT)/SIG)**2)
f_W=lambda w:np.clip(w/(W_MIN*AWC),0,1)
f_H=lambda t:np.clip((t+2.0)/4.0,0,1)
f_P=lambda a:1-np.exp(-a/P0)

p5=p.rolling(5,min_periods=3).mean(); w5=agua.rolling(5,min_periods=3).mean()
pulso=f_P(p.rolling(VENT,min_periods=int(VENT*0.8)).sum().shift(LAG))
ZS=[0,200,400,600,800,1000]; res={}
for zz in ZS:
    t5=cota(zz,tmed).rolling(5,min_periods=3).mean()
    n5=cota(zz,tmin).rolling(5,min_periods=3).mean()
    idx=f_T(t5)*pulso*f_W(w5)*f_H(n5)
    res[zz]=idx.where(~((t5>T_EXCL)&(p5<P_EXCL)),0.0)
D=pd.DataFrame(res); D.to_pickle('disparo2.pkl')
D[D.index.month.isin([8,9,10,11])].round(4).to_csv(
 'C:/Users/Peru/Desktop/Ontto App/datos/disparo_diario_v2_1970_2015.csv')

print('DISPARO v2 — indice medio por quincena y altitud')
print('%-12s'%'quincena'+''.join('%9d m'%zz for zz in ZS))
for m,d0,nom in [(8,16,'16-31 ago'),(9,1,'1-15 sep'),(9,16,'16-30 sep'),(10,1,'1-15 oct'),
                 (10,16,'16-31 oct'),(11,1,'1-15 nov'),(11,16,'16-30 nov')]:
    sel=(D.index.month==m)&(D.index.day>=d0)&(D.index.day<d0+15)
    v=D[sel].mean(); print('%-12s'%nom+''.join('%11.3f'%v[zz] for zz in ZS))
print()
print('PICO POR ALTITUD          v1 (sin lluvia) -> v2')
D1=pd.read_pickle('disparo.pkl')
for zz in ZS:
    out=[]
    for DD in (D1,D):
        s=DD[zz]; s=s[s.index.month.isin([8,9,10,11])]
        g=s.groupby([s.index.month,s.index.day]).mean(); m,d=g.idxmax()
        out.append('%2d %s'%(d,['','','','','','','','','ago','sep','oct','nov'][m]))
    print('   %4d m ->  %s   ->   %s'%(zz,out[0],out[1]))
print()
o=D.loc[D.index.month.isin([8,9,10,11]),600]
an=o.groupby(o.index.year).sum(); an=an[an>3]
print('VARIACION INTERANUAL a 600 m: media %.1f  CV %.0f%%  (v1: 21%%)'%(an.mean(),100*an.std()/an.mean()))
print('   mejores: '+', '.join('%d'%y for y in an.nlargest(5).index))
print('   peores:  '+', '.join('%d'%y for y in an.nsmallest(5).index))
o1=D1.loc[D1.index.month.isin([8,9,10,11]),600]
a1=o1.groupby(o1.index.year).sum(); a1=a1[a1>5]
comun=an.index.intersection(a1.index)
print('   correlacion del ranking anual v1 vs v2: %.2f'%np.corrcoef(an[comun],a1[comun])[0,1])
