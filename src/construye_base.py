# -*- coding: utf-8 -*-
"""Genera publico/datos/base.json: la capa POTENCIAL y la geometria del mapa.

Esto cambia una vez al ano, cuando sale el Mapa Forestal nuevo. No forma parte
de la actualizacion diaria: el navegador lo cachea y no vuelve a pedirlo.

Entrada:  datos/potencial_mic1.csv  +  geometrias recortadas de Gipuzkoa
Salida:   publico/datos/base.json   (~900 KB)
"""
import json, os, pickle, sys
import pandas as pd
import shapefile
from shapely.geometry import shape

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAL = os.path.join(RAIZ, 'publico', 'datos', 'base.json')
MIN_HA = 2.0          # por debajo de esto el poligono no se ve en el mapa
TOL = 45              # simplificacion en metros


def anillos(g, minx, miny, tol=TOL):
    gs = g.simplify(tol, preserve_topology=True)
    if gs.is_empty:
        return []
    gj = gs.__geo_interface__
    polis = [gj['coordinates'][0]] if gj['type'] == 'Polygon' \
        else [p[0] for p in gj['coordinates']]
    out = []
    for r in polis:
        pts = []
        for x, y in r:
            pts += [int(round(x - minx)), int(round(y - miny))]
        if len(pts) >= 8:
            out.append(pts)
    return out


def main(dir_trabajo):
    geoms = pickle.load(open(os.path.join(dir_trabajo, 'geoms.pkl'), 'rb'))
    pot = pd.read_csv(os.path.join(RAIZ, 'datos', 'potencial_mic1.csv'))
    alt = pd.read_csv(os.path.join(RAIZ, 'datos', 'masas_altitud.csv'))[['OBJECTID', 'alt_media']]
    pen = pd.read_csv(os.path.join(RAIZ, 'datos', 'masas_pendiente.csv'))[['OBJECTID', 'pend_pct']]
    t = pot.merge(alt, on='OBJECTID', how='left').merge(pen, on='OBJECTID', how='left')
    t = t.set_index('OBJECTID')

    tr = shapefile.Reader(os.path.join(dir_trabajo, 'terr', 'TERRITORIOS_5000_ETRS89'))
    gip = None
    for sr in tr.iterShapeRecords():
        if 'GIPUZKOA' in sr.record[1]:
            gip = shape(sr.shape.__geo_interface__).buffer(0)
    minx, miny, maxx, maxy = [int(v) for v in gip.bounds]

    feats = []
    for d, g, ha in geoms:
        oid = d['OBJECTID']
        if oid not in t.index or ha < MIN_HA:
            continue
        r = t.loc[oid]
        if isinstance(r, pd.DataFrame):
            r = r.iloc[0]
        c = r.mic1_kg_ha
        if c != c:
            continue                       # sin coeficiente medido: fuera del mapa
        rr = anillos(g, minx, miny)
        if not rr:
            continue
        num = lambda v, d0: int(v) if v == v else d0
        feats.append([rr, round(float(c), 2), num(r.alt_media, 200), str(r.SP1_es),
                      round(float(ha), 1),
                      str(r.sustrato) if r.sustrato == r.sustrato else '',
                      num(r.FCCARB, 0),
                      str(r.EMASA1).split('/')[-1].strip() if r.EMASA1 == r.EMASA1 else '',
                      num(r.pend_pct, 0)])

    mr = shapefile.Reader(os.path.join(dir_trabajo, 'muni', 'MUNICIPIOS_5000_ETRS89'))
    mn = [f[0] for f in mr.fields[1:]]
    munis = []
    for sr in mr.iterShapeRecords():
        dd = dict(zip(mn, sr.record))
        if 'GIPUZKOA' not in (dd.get('TERRITORIO') or ''):
            continue
        g = shape(sr.shape.__geo_interface__).buffer(0)
        munis.append({'n': dd.get('NOMBRE_TOP', ''), 'r': anillos(g, minx, miny, 120),
                      'c': [int(g.centroid.x - minx), int(g.centroid.y - miny)],
                      'a': round(g.area / 1e4)})

    out = {'bbox': [minx, miny, maxx, maxy],
           'gip': anillos(gip, minx, miny, 60),
           'muni': munis, 'f': feats,
           'version': 'mapa-forestal-cae-2024'}
    txt = json.dumps(out, separators=(',', ':'), allow_nan=False)
    json.loads(txt)
    os.makedirs(os.path.dirname(SAL), exist_ok=True)
    open(SAL, 'w', encoding='utf-8').write(txt)
    print('base.json: %d rodales, %d municipios, %.2f MB'
          % (len(feats), len(munis), len(txt) / 1e6))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('uso: python construye_base.py <directorio con geoms.pkl, terr/ y muni/>')
        sys.exit(1)
    main(sys.argv[1])
