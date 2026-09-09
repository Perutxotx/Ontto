# -*- coding: utf-8 -*-
"""Actualizacion diaria de la capa DISPARO de Ontto.

Combina tres fuentes de AEMET:
  1. Climatologia diaria   -> serie validada, retardo de 2-4 dias
  2. Observacion horaria   -> ultimos dias, retardo de ~1 hora
  3. Prediccion municipal  -> 7 dias por delante

Recalcula el balance hidrico y el indice DISPARO y regenera el payload
de la app. No republica: eso lo hace quien invoque este script.
"""
import json, os, sys, time, io
import urllib.request
import datetime as dt
import numpy as np
import pandas as pd

KEY = os.environ.get('AEMET_API_KEY', '').strip()
if not KEY:
    _kf = os.path.expanduser('~/.config/ontto/aemet.key')
    if os.path.exists(_kf):
        KEY = io.open(_kf).read().strip()
if not KEY:
    raise SystemExit('falta la clave de AEMET: define AEMET_API_KEY')

# Estaciones de vertiente atlantica en el entorno de Gipuzkoa.
# Se excluyen las del lado del Ebro: Arcaute recibe 777 mm/ano frente a los
# 2.454 de Articutza, y mezclarlas produce artefactos (ver docs/05).
EST = [('1069Y', 747), ('1044X', 617), ('1033X', 520), ('1049N', 470),
       ('1037X', 460), ('1037Y', 431), ('1048X', 308), ('1021Y', 305),
       ('1026X', 290), ('1025A', 255), ('1025X', 255), ('1024X', 250),
       ('1038X', 180), ('1021X', 165), ('1052A', 150), ('1012P', 120),
       ('1050J', 119), ('1010X', 54), ('1014A', 4)]
ALT = dict(EST)
MUNI_PRED = ['20030', '20069', '20016']      # Eibar, Donostia, Beasain

AWC = 74.0
OPT, SIG = 13.2, 3.5
T_EXCL, P_EXCL = 17.5, 1.0
W_MIN = 0.40
LAG, VENT, P0 = 10, 15, 40.0
ZS = [0, 200, 400, 600, 800, 1000]
LAPSE = {1: -.00728, 2: -.00605, 3: -.00558, 4: -.00385, 5: -.00438, 6: -.00286,
         7: -.00277, 8: -.00355, 9: -.00523, 10: -.00497, 11: -.00686, 12: -.00613}


def api(url, intentos=5):
    for k in range(intentos):
        try:
            req = urllib.request.Request(url, headers={'api_key': KEY})
            meta = json.load(urllib.request.urlopen(req, timeout=60))
            if meta.get('estado') == 200 and meta.get('datos'):
                raw = urllib.request.urlopen(meta['datos'], timeout=90).read()
                return json.loads(raw.decode('latin-1'))
            if meta.get('estado') == 429:
                time.sleep(20)
                continue
            time.sleep(4)
        except Exception:
            time.sleep(5)
    return []


def num(v):
    if v is None:
        return np.nan
    s = str(v).strip()
    if s == 'Ip':
        return 0.0
    if s in ('', 'Acum', 'varias'):
        return np.nan
    try:
        return float(s.replace(',', '.'))
    except Exception:
        return np.nan


def climatologia(dias=150):
    """Serie diaria validada."""
    hoy = dt.date.today()
    ini = hoy - dt.timedelta(days=dias)
    filas = []
    for cod, alt in EST:
        d = ini
        while d < hoy:
            f = min(d + dt.timedelta(days=150), hoy)
            u = ('https://opendata.aemet.es/opendata/api/valores/climatologicos/diarios/datos/'
                 'fechaini/%sT00:00:00UTC/fechafin/%sT23:59:59UTC/estacion/%s'
                 % (d.strftime('%Y-%m-%d'), f.strftime('%Y-%m-%d'), cod))
            for r in api(u):
                filas.append({'cod': cod, 'alt': alt, 'fecha': r['fecha'],
                              'tmed': num(r.get('tmed')), 'tmin': num(r.get('tmin')),
                              'tmax': num(r.get('tmax')), 'prec': num(r.get('prec')),
                              'origen': 'clima'})
            d = f + dt.timedelta(days=1)
            time.sleep(1.1)
    return pd.DataFrame(filas)


def observacion():
    """Ultimas horas de toda la red, agregadas a dia. Retardo de ~1 hora."""
    datos = api('https://opendata.aemet.es/opendata/api/observacion/convencional/todas')
    codes = set(ALT)
    filas = []
    for r in datos:
        if r.get('idema') not in codes:
            continue
        filas.append({'cod': r['idema'], 'fint': r.get('fint'),
                      'ta': num(r.get('ta')), 'prec': num(r.get('prec'))})
    if not filas:
        return pd.DataFrame()
    o = pd.DataFrame(filas)
    o['fecha'] = pd.to_datetime(o.fint, errors='coerce').dt.strftime('%Y-%m-%d')
    o = o.dropna(subset=['fecha'])
    g = o.groupby(['cod', 'fecha']).agg(
        tmed=('ta', 'mean'), tmin=('ta', 'min'), tmax=('ta', 'max'),
        prec=('prec', 'sum'), n=('ta', 'size')).reset_index()
    g = g[g.n >= 12]                      # solo dias con cobertura razonable
    g['alt'] = g.cod.map(ALT)
    g['origen'] = 'obs'
    return g[['cod', 'alt', 'fecha', 'tmed', 'tmin', 'tmax', 'prec', 'origen']]


def prediccion():
    """Prediccion municipal, promediada entre municipios. Devuelve dia -> (tmax,tmin,prec_mm)."""
    acc = {}
    for m in MUNI_PRED:
        d = api('https://opendata.aemet.es/opendata/api/prediccion/especifica/'
                'municipio/diaria/%s' % m)
        if not d:
            continue
        for x in d[0].get('prediccion', {}).get('dia', []):
            f = x['fecha'][:10]
            try:
                tx = float(x['temperatura']['maxima'])
                tn = float(x['temperatura']['minima'])
            except Exception:
                continue
            pp = [int(q['value']) for q in x.get('probPrecipitacion', [])
                  if str(q.get('value', '')).strip() != '']
            prob = max(pp) / 100.0 if pp else 0.0
            # traducir probabilidad a mm esperados: aproximacion grosera y declarada
            mm = prob * 12.0
            acc.setdefault(f, []).append((tx, tn, mm))
        time.sleep(1.5)
    return {f: (np.mean([v[0] for v in vs]), np.mean([v[1] for v in vs]),
                np.mean([v[2] for v in vs])) for f, vs in acc.items()}


def Ra(doy, lat=43.1):
    lat = np.deg2rad(lat)
    dr = 1 + 0.033 * np.cos(2 * np.pi * doy / 365)
    dec = 0.409 * np.sin(2 * np.pi * doy / 365 - 1.39)
    ws = np.arccos(np.clip(-np.tan(lat) * np.tan(dec), -1, 1))
    return (24 * 60 / np.pi) * 0.082 * dr * (ws * np.sin(lat) * np.sin(dec)
                                             + np.cos(lat) * np.cos(dec) * np.sin(ws))


def construye(df, pred):
    """Series diarias de la vertiente y su altitud de referencia."""
    df = df.copy()
    df['fecha'] = pd.to_datetime(df.fecha)
    # una fila por estacion y dia: la climatologia manda sobre la observacion
    df['pri'] = (df.origen == 'clima').astype(int)
    df = df.sort_values('pri').drop_duplicates(['cod', 'fecha'], keep='last')
    piv = lambda c: df.pivot_table(index='fecha', columns='cod', values=c)
    T, N, X, P = piv('tmed'), piv('tmin'), piv('tmax'), piv('prec')
    zref = float(np.mean([ALT[c] for c in T.columns if c in ALT]))
    s = pd.DataFrame({'T': T.mean(axis=1), 'N': N.mean(axis=1),
                      'X': X.mean(axis=1), 'P': P.mean(axis=1)})
    # Rejilla diaria completa. Sin esto, rolling() cuenta FILAS y un hueco de
    # dos dias convierte una ventana de 15 dias en una de 17.
    idx = pd.date_range(s.index.min(), s.index.max(), freq='D')
    s = s.reindex(idx)
    huecos = int(s['T'].isna().sum())
    if huecos:
        print('  huecos rellenados en la serie: %d dias' % huecos, flush=True)
    for c in ('T', 'N', 'X'):
        s[c] = s[c].interpolate(limit=3, limit_direction='both')
    s['P'] = s['P'].fillna(0.0)      # hueco corto: se asume sin lluvia registrada
    s['origen'] = 'observado'
    # anadir prediccion detras del ultimo dia observado
    ult = s.index.max()
    for f, (tx, tn, mm) in sorted(pred.items()):
        d = pd.Timestamp(f)
        if d <= ult:
            continue
        s.loc[d] = {'T': (tx + tn) / 2, 'N': tn, 'X': tx, 'P': mm, 'origen': 'previsto'}
    return s.sort_index(), zref


def disparo(s, zref):
    et0 = 0.0023 * (Ra(s.index.dayofyear.values) / 2.45) * (s['T'].values + 17.8) \
        * np.sqrt(np.clip(s['X'].values - s['N'].values, 0, None))
    et0 = pd.Series(np.clip(np.nan_to_num(et0), 0, None), index=s.index)
    w = AWC * 0.6
    agua = []
    for i in range(len(s)):
        p = s['P'].iloc[i]
        p = 0.0 if not np.isfinite(p) else p
        w = min(AWC, w + p)
        w = max(0.0, w - min(w, et0.iloc[i] * (w / AWC)))
        agua.append(w)
    agua = pd.Series(agua, index=s.index)
    p5 = s['P'].rolling(5, min_periods=2).mean()
    w5 = agua.rolling(5, min_periods=2).mean()
    pulso = 1 - np.exp(-s['P'].rolling(VENT, min_periods=8).sum().shift(LAG) / P0)
    est = pd.Series(0.35 + 0.65 * (1 + np.cos(2 * np.pi * (s.index.dayofyear.values - 280) / 365)) / 2,
                    index=s.index)
    b = np.array([LAPSE[m] for m in s.index.month])
    out = {}
    for z in ZS:
        t5 = (s['T'] + b * (z - zref)).rolling(5, min_periods=2).mean()
        n5 = (s['N'] + b * (z - zref)).rolling(5, min_periods=2).mean()
        idx = np.exp(-((t5 - OPT) / SIG) ** 2) * pulso \
            * np.clip(w5 / (W_MIN * AWC), 0, 1) * np.clip((n5 + 2) / 4, 0, 1) * est
        out[z] = idx.where(~((t5 > T_EXCL) & (p5 < P_EXCL)), 0.0)
    D = pd.DataFrame(out)
    D['origen'] = s['origen']
    return D, agua


def main():
    _cache = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'crudo.pkl')
    usa_cache = '--cache' in sys.argv and os.path.exists(_cache)
    if usa_cache:
        cl = pd.read_pickle(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'crudo.pkl'))
        print('climatologia desde cache: %d registros' % len(cl), flush=True)
    else:
        print('descargando climatologia...', flush=True)
        cl = climatologia()
        try: cl.to_pickle(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'crudo.pkl'))
        except Exception: pass
    print('descargando observacion...', flush=True)
    ob = observacion()
    print('  %d dias-estacion' % len(ob), flush=True)
    print('descargando prediccion...', flush=True)
    pr = prediccion()
    print('  %d dias previstos' % len(pr), flush=True)
    df = pd.concat([cl, ob], ignore_index=True) if len(ob) else cl
    s, zref = construye(df, pr)
    D, agua = disparo(s, zref)
    ok = D[ZS].notna().all(axis=1)
    D = D[ok]
    print()
    print('serie: %s a %s  (referencia %.0f m)' % (D.index[0].date(), D.index[-1].date(), zref))
    obs = D[D.origen == 'observado']
    prv = D[D.origen == 'previsto']
    print('  observado hasta %s, previsto %d dias' % (obs.index[-1].date(), len(prv)))
    out = {'zs': ZS,
           'live': {'d': [d.strftime('%Y-%m-%d') for d in D.index],
                    'v': [[round(float(D.loc[d, z]), 3) for z in ZS] for d in D.index],
                    'o': [1 if D.loc[d, 'origen'] == 'previsto' else 0 for d in D.index]},
           'hoy': obs.index[-1].strftime('%Y-%m-%d'),
           'actualizado': dt.datetime.now().strftime('%Y-%m-%d %H:%M')}
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    clim = json.load(io.open(os.path.join(raiz, 'src', 'climatologia_base.json'),
                             encoding='utf-8'))
    out['clim'] = clim['clim']
    txt = json.dumps(out, separators=(',', ':'), allow_nan=False)
    json.loads(txt)
    sal = os.path.join(raiz, 'publico', 'datos', 'disparo.json')
    os.makedirs(os.path.dirname(sal), exist_ok=True)
    io.open(sal, 'w', encoding='utf-8').write(txt)
    print('escrito %s (%.0f KB)' % (sal, len(txt) / 1024))
    print()
    print('ULTIMOS DIAS')
    print('%-12s %-10s' % ('fecha', 'origen') + ''.join('%8d m' % z for z in ZS))
    for f in D.index[-10:]:
        print('%-12s %-10s' % (f.date(), D.loc[f, 'origen'])
              + ''.join('%10.3f' % D.loc[f, z] for z in ZS))


if __name__ == '__main__':
    main()
