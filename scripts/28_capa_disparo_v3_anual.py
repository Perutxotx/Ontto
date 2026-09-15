"""Capa DISPARO v3 — ano completo, con asimetria estacional.

  DISPARO(t,z) = f_T x f_P x f_W x f_H x f_S x exclusion

  f_S  envolvente estacional: la fructificacion ectomicorricica sigue la
       asignacion de fotosintatos del arbol, maxima cuando cesa el crecimiento
       (final de verano y otono). Apoyo: Agreda et al. miden el micelio
       extrarradical de B. edulis con maximo en febrero y minimo en octubre
       -- fase opuesta, porque en otono el micelio se convierte en carpoforos.

       f_S = 0.35 + 0.65 * (1+cos(2pi(doy-280)/365))/2

       Pico el 7 de octubre; minimo 0,35 a principios de abril.
       NO ajustado con datos: eleccion informada.
"""
import pandas as pd, numpy as np
pr=pd.read_pickle('pr_b.pkl'); tx=pd.read_pickle('tx_b.pkl'); tn=pd.read_pickle('tn_b.pkl')
S=pd.read_pickle('agua_suelo.pkl'); z=pd.read_csv('est_buenas.csv').set_index('COD')
MED=['9275B','9269','9086']; AT=[c for c in pr.columns if c not in MED]
ZREF=float(np.average(z.loc[AT,'ALTITUD']))
tmed=((tx[AT]+tn[AT])/2).mean(axis=1); tmin=tn[AT].mean(axis=1)
p=pr[AT].mean(axis=1); agua=S[AT].mean(axis=1); AWC=74.0
L12=np.load('lapse12.npy')
cota=lambda zz,s: s + L12[s.index.month.values-1]*(zz-ZREF)
OPT,SIG=13.2,3.5; T_EXCL,P_EXCL,T_RAMPA=17.5,1.0,2.0; W_MIN=0.40; LAG,VENT,P0=10,15,40.0
f_T=lambda t:np.exp(-((t-OPT)/SIG)**2)
f_W=lambda w:np.clip(w/(W_MIN*AWC),0,1)
f_H=lambda t:np.clip((t+2.0)/4.0,0,1)
f_P=lambda a:1-np.exp(-a/P0)
f_S=lambda doy:0.35+0.65*(1+np.cos(2*np.pi*(doy-280)/365))/2
p5=p.rolling(5,min_periods=3).mean(); w5=agua.rolling(5,min_periods=3).mean()
pulso=f_P(p.rolling(VENT,min_periods=12).sum().shift(LAG))
est=pd.Series(f_S(pr.index.dayofyear.values),index=pr.index)
ZS=[0,200,400,600,800,1000]; res={}
for zz in ZS:
    t5=cota(zz,tmed).rolling(5,min_periods=3).mean()
    n5=cota(zz,tmin).rolling(5,min_periods=3).mean()
    idx=f_T(t5)*pulso*f_W(w5)*f_H(n5)*est
    supr=np.clip((t5-T_EXCL)/T_RAMPA,0,1).where(p5<P_EXCL,0.0)   # rampa, no acantilado
    res[zz]=idx*(1-supr)
D=pd.DataFrame(res); D.to_pickle('disparo_final.pkl')
D.round(4).to_csv('C:/Users/Peru/Desktop/Ontto App/datos/disparo_diario_anual_1970_2015.csv')
MES=['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic']
print('DISPARO v3 FINAL — indice por mes y altitud')
print('%-6s'%'mes'+''.join('%9d m'%zz for zz in ZS))
for m in range(1,13):
    v=D[D.index.month==m].mean(); print('%-6s'%MES[m-1]+''.join('%11.3f'%v[zz] for zz in ZS))
print()
print('REPARTO ESTACIONAL DEL INDICE ANUAL')
print('%-10s'%''+''.join('%9d m'%zz for zz in ZS))
for nom,ms in [('invierno',[12,1,2]),('primavera',[3,4,5]),('verano',[6,7,8]),('otono',[9,10,11])]:
    row=''
    for zz in ZS:
        s=D[zz]; row+='%10.0f%%'%(100*s[s.index.month.isin(ms)].sum()/s.sum())
    print('%-10s'%nom+row)
print()
print('PICOS')
for zz in ZS:
    s=D[zz]; g=s.groupby([s.index.month,s.index.day]).mean()
    pv=g[[i for i in g.index if 3<=i[0]<=7]]; ot=g[[i for i in g.index if 8<=i[0]<=12]]
    mp,dp=pv.idxmax(); mo,do=ot.idxmax()
    print('   %4d m   primavera %2d %s (%.3f)   otono %2d %s (%.3f)   ratio %.2f'%(
        zz,dp,MES[mp-1],pv.max(),do,MES[mo-1],ot.max(),pv.max()/ot.max()))
