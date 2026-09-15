# -*- coding: utf-8 -*-
"""Primera validacion de Ontto con datos independientes.

No hay produccion medida en kg en Gipuzkoa (decision A1, abierta desde el
principio). Pero si hay registros de fructificacion con fecha exacta y
coordenadas: GBIF agrega el herbario ARAN de Aranzadi, iNaturalist y varios
herbarios mas. Son presencias, no cosechas, pero fechan el hecho.

La prueba: el dia que alguien encontro un onddo, .estaba el indice alto?

Control imprescindible: la gente sale al monte en otono. Comparar contra
"todos los dias del ano" validaria la estacionalidad por construccion. Asi
que cada hallazgo se compara solo contra los demas dias DEL MISMO MES y a
LA MISMA COTA. Lo que se mide es la parte meteorologica, no la estacional.

Segundo ajuste, fisico: un carpoforo encontrado el dia X emergio dias antes
y aguanta una o dos semanas. Lo que hay que mirar no es el indice del dia
del hallazgo, sino el maximo de los N dias previos.

Uso:  python scripts/31_validacion_gbif.py
"""
import json, glob, os, sys
import numpy as np, pandas as pd
from pyproj import Transformer
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAJA = 'decimalLatitude=42.9,43.4&decimalLongitude=-2.6,-1.7'
SP = ['Boletus edulis', 'Boletus aereus', 'Boletus pinophilus', 'Boletus reticulatus']
ZS = [0, 200, 400, 600, 800, 1000]


def descarga(dest):
    import urllib.request, urllib.parse
    os.makedirs(dest, exist_ok=True)
    for sp in SP:
        u = ('https://api.gbif.org/v1/occurrence/search?scientificName=%s&%s'
             '&hasCoordinate=true&limit=300' % (urllib.parse.quote(sp), CAJA))
        f = os.path.join(dest, 'gbif_%s.json' % sp.split()[1])
        if not os.path.exists(f):
            urllib.request.urlretrieve(u, f)
        print('  %s: %s' % (sp, f))


def main(dir_cache):
    descarga(dir_cache)
    rec = []
    for f in sorted(glob.glob(os.path.join(dir_cache, 'gbif_*.json'))):
        rec += json.load(open(f, encoding='utf-8'))['results']
    rec = [r for r in rec if r.get('decimalLatitude')
           and 1970 <= int(r['eventDate'][:4]) <= 2015]

    b = json.load(open(os.path.join(RAIZ, 'publico', 'datos', 'base.json'), encoding='utf-8'))
    minx, miny = b['bbox'][0], b['bbox'][1]
    gip = unary_union([Polygon(np.array(r).reshape(-1, 2) + [minx, miny])
                       for r in b['gip']]).buffer(0)
    amp = gip.buffer(15000)          # + Navarra atlantica: Artikutza, Leitza, Bera
    tr = Transformer.from_crs('EPSG:4326', 'EPSG:25830', always_xy=True)
    cen = np.array([(np.array(f[0][0]).reshape(-1, 2) + [minx, miny]).mean(axis=0) for f in b['f']])
    alt = np.array([f[2] for f in b['f']])

    idx = pd.read_csv(os.path.join(RAIZ, 'datos', 'disparo_diario_anual_1970_2015.csv'),
                      parse_dates=['fecha']).set_index('fecha')
    idx.columns = [int(c) for c in idx.columns]

    filas = []
    for r in rec:
        x, y = tr.transform(r['decimalLongitude'], r['decimalLatitude'])
        if not amp.contains(Point(x, y)) or y < 4740000:   # fuera, o lado del Ebro
            continue
        zb = min(ZS, key=lambda q: abs(q - alt[np.hypot(cen[:, 0] - x, cen[:, 1] - y).argmin()]))
        f = pd.Timestamp(r['eventDate'][:10])
        if f not in idx.index or pd.isna(idx.loc[f, zb]):
            continue
        filas.append({'fecha': f, 'zb': zb, 'mes': f.month,
                      'sp': r.get('species', '') or '', 'dentro': gip.contains(Point(x, y))})
    D = pd.DataFrame(filas)
    print('\n%d registros utiles (%d estrictamente en Gipuzkoa), %s a %s'
          % (len(D), int(D.dentro.sum()), D.fecha.min().date(), D.fecha.max().date()))

    def prueba(sub, etiq, vent):
        ps = []
        for _, r in sub.iterrows():
            s = idx.loc[r.fecha - pd.Timedelta(days=vent):r.fecha, r.zb].dropna()
            if not len(s):
                continue
            ref = idx[r.zb].rolling(vent + 1, min_periods=1).max()
            ref = ref[ref.index.month == r.mes].dropna()
            ps.append((ref < s.max()).mean())
        if len(ps) < 8:
            return
        m, n = np.mean(ps), len(ps)
        z = (m - 0.5) / (1 / 12 / n) ** 0.5
        print('   %-26s ventana %2d d  n=%3d  percentil %.1f %%  z=%+.1f%s'
              % (etiq, vent, n, 100 * m, z, '   <-- significativo' if abs(z) > 1.96 else ''))

    print('\nmaximo del indice en los N dias previos, contra la misma ventana del mismo mes:')
    for v in (0, 5, 10, 15, 21):
        prueba(D[D.mes.isin([9, 10, 11])], 'grupo onddo, sep-nov', v)
    print()
    for v in (0, 5, 10, 15, 21):
        prueba(D, 'grupo onddo, todo el ano', v)

    mm = idx[ZS].stack().groupby(level=0).mean()
    mi = mm.groupby(mm.index.month).mean()
    h = D.mes.value_counts(normalize=True)
    r = np.corrcoef([mi.get(m, 0) for m in range(1, 13)],
                    [h.get(m, 0) for m in range(1, 13)])[0, 1]
    print('\ncontrol estacional: correlacion mensual indice vs hallazgos  r = %+.2f' % r)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(RAIZ, 'datos', 'gbif'))
