# -*- coding: utf-8 -*-
"""Reconstruye la serie diaria historica de las 19 estaciones atlanticas.

Los intermedios del analisis original (pr_b.pkl, tx_b.pkl, tn_b.pkl) se
perdieron, y sin ellos no se puede recalcular el indice historico con otros
parametros -- es decir, no se puede probar nada contra la validacion de
scripts/31. Esto los reconstruye.

Se baja 1998-hoy y no 1970: los registros de fructificacion de GBIF estan
concentrados ahi (2000s: 161, 2010s: 55, 2020s: 105; antes de 1998 hay 10 en
total), y bajar 46 anos cuesta el triple para no anadir muestra.

Guarda datos/serie_diaria_atlantica.csv. Reanudable: si el fichero existe,
solo pide lo que falta.

Uso:  AEMET_API_KEY=... python scripts/32_serie_historica_aemet.py [ano_inicio]
"""
import os, sys, time, datetime as dt
import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'src'))
import actualiza as A                                   # api(), EST, num()

SAL = os.path.join(RAIZ, 'datos', 'serie_diaria_atlantica.csv')
INI = int(sys.argv[1]) if len(sys.argv) > 1 else 1998


def main():
    hoy = dt.date.today()
    hecho = set()
    previo = None
    if os.path.exists(SAL):
        previo = pd.read_csv(SAL)
        hecho = set(zip(previo.cod, previo.fecha.str[:7]))
        print('reanudando: %d filas ya descargadas' % len(previo), flush=True)

    filas = []
    for i, (cod, alt) in enumerate(A.EST, 1):
        d = dt.date(INI, 1, 1)
        n0 = len(filas)
        while d < hoy:
            f = min(d + dt.timedelta(days=150), hoy)
            if (cod, d.strftime('%Y-%m')) in hecho:      # ya lo tenemos
                d = f + dt.timedelta(days=1)
                continue
            u = ('https://opendata.aemet.es/opendata/api/valores/climatologicos/diarios/datos/'
                 'fechaini/%sT00:00:00UTC/fechafin/%sT23:59:59UTC/estacion/%s'
                 % (d.strftime('%Y-%m-%d'), f.strftime('%Y-%m-%d'), cod))
            for r in A.api(u):
                filas.append({'cod': cod, 'alt': alt, 'fecha': r['fecha'],
                              'tmed': A.num(r.get('tmed')), 'tmin': A.num(r.get('tmin')),
                              'tmax': A.num(r.get('tmax')), 'prec': A.num(r.get('prec'))})
            d = f + dt.timedelta(days=1)
            time.sleep(1.1)
        print('  [%2d/%d] %s (%d m): %d filas' % (i, len(A.EST), cod, alt, len(filas) - n0),
              flush=True)

    D = pd.DataFrame(filas)
    if previo is not None and len(previo):
        D = pd.concat([previo, D], ignore_index=True)
    D = D.drop_duplicates(subset=['cod', 'fecha']).sort_values(['cod', 'fecha'])
    D.to_csv(SAL, index=False)
    print('\nescrito %s: %d filas, %s a %s, %d estaciones'
          % (SAL, len(D), D.fecha.min(), D.fecha.max(), D.cod.nunique()))


if __name__ == '__main__':
    main()
