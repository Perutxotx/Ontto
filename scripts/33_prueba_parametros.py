# -*- coding: utf-8 -*-
"""Prueba parametros del DISPARO contra los registros de fructificacion.

scripts/31 demostro que el modelo acierta. Esto lo usa al reves: como banco
de pruebas para decidir si un parametro concreto mejora o empeora.

La metrica es la de scripts/31: para cada hallazgo, en que percentil cae el
maximo del indice de los N dias previos, comparado con la misma ventana movil
de los demas dias del mismo mes y a la misma cota. 50 % = el modelo no sabe
nada. Cuanto mas alto, mejor.

AVISO SOBRE SOBREAJUSTE. La muestra es de unos cientos de registros. Barrer
un parametro y quedarse con el maximo es sobreajustar. Por eso:
  - los candidatos se fijan ANTES, desde la bibliografia
  - se imprime la superficie entera, para ver si hay un pico real o es plano
  - solo se cambia el modelo si el candidato bibliografico gana de forma clara

Uso:  python scripts/33_prueba_parametros.py
"""
import json, glob, os, sys
import numpy as np, pandas as pd
from pyproj import Transformer
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'src'))
os.environ.setdefault('AEMET_API_KEY', 'x')
import actualiza as A

SERIE = os.path.join(RAIZ, 'datos', 'serie_diaria_atlantica.csv')
ZS = A.ZS
OTONO = [9, 10, 11]


def serie_referencia():
    """Media de las estaciones atlanticas -> serie diaria y altitud de referencia."""
    d = pd.read_csv(SERIE)
    for c in ('tmed', 'tmin', 'tmax', 'prec'):
        d[c] = pd.to_numeric(d[c], errors='coerce')
    d['fecha'] = pd.to_datetime(d.fecha)
    zref = d.groupby('cod').alt.first().mean()
    g = d.groupby('fecha')
    s = pd.DataFrame({'T': g.tmed.mean(), 'N': g.tmin.mean(),
                      'X': g.tmax.mean(), 'P': g.prec.mean()})
    # rejilla diaria completa: sin esto rolling() cuenta filas, no dias
    s = s.reindex(pd.date_range(s.index.min(), s.index.max(), freq='D'))
    for c in ('T', 'N', 'X'):
        s[c] = s[c].interpolate(limit=5, limit_direction='both')
    s['P'] = s['P'].fillna(0.0)
    return s, zref


def indice(s, zref, opt=A.OPT, sig=A.SIG, wmin=A.W_MIN, lag=A.LAG, vent=A.VENT,
           p0=A.P0, t_excl=A.T_EXCL, t_rampa=2.0, awc=A.AWC):
    et0 = 0.0023 * (A.Ra(s.index.dayofyear.values) / 2.45) * (s['T'].values + 17.8) \
        * np.sqrt(np.clip(s['X'].values - s['N'].values, 0, None))
    et0 = pd.Series(np.clip(np.nan_to_num(et0), 0, None), index=s.index)
    w = awc * 0.6
    ag = []
    for i in range(len(s)):
        p = s['P'].iloc[i]
        p = 0.0 if not np.isfinite(p) else p
        w = min(awc, w + p)
        w = max(0.0, w - min(w, et0.iloc[i] * (w / awc)))
        ag.append(w)
    agua = pd.Series(ag, index=s.index)
    p5 = s['P'].rolling(5, min_periods=3).mean()
    w5 = agua.rolling(5, min_periods=3).mean()
    pulso = 1 - np.exp(-s['P'].rolling(vent, min_periods=max(2, vent // 2)).sum().shift(lag) / p0)
    est = pd.Series(0.35 + 0.65 * (1 + np.cos(2 * np.pi * (s.index.dayofyear.values - 280) / 365)) / 2,
                    index=s.index)
    b = np.array([A.LAPSE[m] for m in s.index.month])
    out = {}
    for z in ZS:
        t5 = (s['T'] + b * (z - zref)).rolling(5, min_periods=3).mean()
        n5 = (s['N'] + b * (z - zref)).rolling(5, min_periods=3).mean()
        idx = np.exp(-((t5 - opt) / sig) ** 2) * pulso \
            * np.clip(w5 / (wmin * awc), 0, 1) * np.clip((n5 + 2) / 4, 0, 1) * est
        supr = np.clip((t5 - t_excl) / t_rampa, 0, 1).where(p5 < A.P_EXCL, 0.0)
        out[z] = idx * (1 - supr)
    return pd.DataFrame(out)


def hallazgos(dir_cache, ini, fin):
    rec = []
    for f in sorted(glob.glob(os.path.join(dir_cache, 'gbif_*.json'))):
        rec += json.load(open(f, encoding='utf-8'))['results']
    rec = [r for r in rec if r.get('decimalLatitude') and ini <= int(r['eventDate'][:4]) <= fin]
    b = json.load(open(os.path.join(RAIZ, 'publico', 'datos', 'base.json'), encoding='utf-8'))
    minx, miny = b['bbox'][0], b['bbox'][1]
    gip = unary_union([Polygon(np.array(r).reshape(-1, 2) + [minx, miny])
                       for r in b['gip']]).buffer(0)
    amp = gip.buffer(15000)
    tr = Transformer.from_crs('EPSG:4326', 'EPSG:25830', always_xy=True)
    cen = np.array([(np.array(f[0][0]).reshape(-1, 2) + [minx, miny]).mean(axis=0) for f in b['f']])
    alt = np.array([f[2] for f in b['f']])
    filas = []
    for r in rec:
        x, y = tr.transform(r['decimalLongitude'], r['decimalLatitude'])
        if not amp.contains(Point(x, y)) or y < 4740000:
            continue
        zb = min(ZS, key=lambda q: abs(q - alt[np.hypot(cen[:, 0] - x, cen[:, 1] - y).argmin()]))
        f = pd.Timestamp(r['eventDate'][:10])
        filas.append({'fecha': f, 'zb': zb, 'mes': f.month, 'sp': r.get('species', '') or ''})
    return pd.DataFrame(filas)


def puntua(D, H, vent=10, meses=None):
    """Percentil medio del indice en los hallazgos. Devuelve (percentil, z, n)."""
    meses = OTONO if meses is None else meses
    H = H[H.mes.isin(meses)]
    ref = {z: D[z].rolling(vent + 1, min_periods=1).max() for z in ZS}
    ps = []
    for _, r in H.iterrows():
        if r.fecha not in D.index:
            continue
        s = D.loc[r.fecha - pd.Timedelta(days=vent):r.fecha, r.zb].dropna()
        if not len(s):
            continue
        rr = ref[r.zb]
        rr = rr[rr.index.month == r.mes].dropna()
        if not len(rr):
            continue
        ps.append((rr < s.max()).mean())
    if len(ps) < 8:
        return np.nan, np.nan, len(ps)
    m, n = float(np.mean(ps)), len(ps)
    return m, (m - 0.5) / (1 / 12 / n) ** 0.5, n


def main():
    s, zref = serie_referencia()
    print('serie: %s a %s (%d dias), referencia %.0f m'
          % (s.index[0].date(), s.index[-1].date(), len(s), zref))
    H = hallazgos(os.path.join(RAIZ, 'datos', 'gbif'), s.index[0].year, s.index[-1].year)
    print('hallazgos utiles: %d (%d en otono)\n' % (len(H), int(H.mes.isin(OTONO).sum())))

    p, z, n = puntua(indice(s, zref), H)
    print('MODELO ACTUAL (OPT=%.1f SIG=%.1f):  percentil %.1f %%  z=%+.2f  n=%d\n'
          % (A.OPT, A.SIG, 100 * p, z, n))

    print('=== optimo termico (SIG=%.1f fijo) ===' % A.SIG)
    print('  Andrew 2025: 12,2 +- 2,0 C.  Preprint de hayedo: 13,2')
    for opt in (10.0, 11.0, 12.0, 12.2, 13.0, 13.2, 14.0, 15.0, 16.0):
        p, z, _ = puntua(indice(s, zref, opt=opt), H)
        m = '  <- Andrew' if abs(opt - 12.2) < .01 else ('  <- actual' if abs(opt - 13.2) < .01 else '')
        print('   OPT=%5.1f   percentil %.1f %%   z=%+.2f%s' % (opt, 100 * p, z, m))

    print('\n=== anchura del optimo (OPT=%.1f fijo) ===' % A.OPT)
    print('  Andrew: nicho diario de ectomicorricicos terrestres, 3,4 C')
    for sig in (2.0, 2.5, 3.0, 3.4, 3.5, 4.0, 5.0, 6.0):
        p, z, _ = puntua(indice(s, zref, sig=sig), H)
        m = '  <- Andrew' if abs(sig - 3.4) < .01 else ('  <- actual' if abs(sig - 3.5) < .01 else '')
        print('   SIG=%5.1f   percentil %.1f %%   z=%+.2f%s' % (sig, 100 * p, z, m))

    print('\n=== umbral hidrico (el parametro sin calibrar) ===')
    for wmin in (0.0, 0.20, 0.30, 0.40, 0.50, 0.60):
        p, z, _ = puntua(indice(s, zref, wmin=wmin), H)
        m = '  <- actual' if abs(wmin - 0.40) < .001 else ''
        print('   W_MIN=%.2f  percentil %.1f %%   z=%+.2f%s' % (wmin, 100 * p, z, m))

    print('\n=== retardo de la lluvia (control: Salerni ya lo valido) ===')
    for lag, vent in ((5, 15), (7, 10), (10, 15), (12, 10), (15, 15)):
        p, z, _ = puntua(indice(s, zref, lag=lag, vent=vent), H)
        m = '  <- actual' if (lag, vent) == (10, 15) else ''
        print('   LAG=%2d VENT=%2d  percentil %.1f %%   z=%+.2f%s' % (lag, vent, 100 * p, z, m))


if __name__ == '__main__':
    main()
