import pickle, json, unicodedata, shapefile
from collections import Counter
from shapely.geometry import shape

geoms = pickle.load(open('geoms.pkl','rb'))
def norm(s):
    return unicodedata.normalize('NFKD',str(s or '')).encode('ascii','ignore').decode().lower().strip()

FR=['haya','roble pedunculado','bosque mixto atlantico','roble americano','encina','quejigo',
    'quejigo faginea','rebollo','castano','roble humilis','roble','abedul','alcornoque','bosque mixto de cantil']
CO=['pino radiata','pino laricio','pino silvestre','pino pinaster','pino halepensis','abeto douglas',
    'alerce','picea europea','pino taeda','otras coniferas','abeto']
SN=['criptomeria','secuoya','chameciparis','eucalipto nitens','eucalipto globulus','eucaliptos',
    'falsa acacia','arboles ripicolas','aliso','platano','fresno','fresno excelsior','sauce','chopo',
    'cedro','aliso de corcega','tulipero','castano japones']
def grupo(sp):
    s=norm(sp)
    if not s: return None
    if s in [norm(k) for k in FR]: return 0   # frondosa ECM
    if s in [norm(k) for k in CO]: return 1   # conifera ECM
    if s in [norm(k) for k in SN]: return 2   # sin ECM
    return 3                                   # otras

# bbox de Gipuzkoa
tr=shapefile.Reader('terr/TERRITORIOS_5000_ETRS89')
for sr in tr.iterShapeRecords():
    if 'GIPUZKOA' in sr.record[1]: gipg=shape(sr.shape.__geo_interface__).buffer(0)
MINX,MINY,MAXX,MAXY=[int(v) for v in gipg.bounds]

def rings(g, tol):
    gs=g.simplify(tol, preserve_topology=True)
    if gs.is_empty: return []
    gj=gs.__geo_interface__
    polys = gj['coordinates'] if gj['type']=='Polygon' else [r for p in gj['coordinates'] for r in [p[0]]]
    if gj['type']=='Polygon': polys=[gj['coordinates'][0]]
    out=[]
    for ring in polys:
        pts=[]
        for x,y in ring:
            pts.append(int(round(x-MINX))); pts.append(int(round(y-MINY)))
        if len(pts)>=8: out.append(pts)
    return out

feats=[]; stats=Counter(); npol=Counter(); spa={}
for d,g,ha in geoms:
    gr=grupo(d['SP1_es'])
    if gr is None: stats['no_arbolado']+=ha; continue
    stats[gr]+=ha; npol[gr]+=1
    spa.setdefault(gr,Counter())[d['SP1_es']]+=ha
    if ha<2.0: continue
    rr=rings(g,45)
    if not rr: continue
    feats.append([gr, rr, d['SP1_es'], round(d['O1'] or 0), (d['EMASA1'] or '').split('/')[-1].strip(),
                  d['SP2_es'] or '', round(d['O2'] or 0), round(d['FCCARB'] or 0), round(ha,1), d['TIPES_es']])

# limites municipales para orientacion
mr=shapefile.Reader('muni/MUNICIPIOS_5000_ETRS89')
mn=[f[0] for f in mr.fields[1:]]
munis=[]
for sr in mr.iterShapeRecords():
    dd=dict(zip(mn,sr.record))
    g=shape(sr.shape.__geo_interface__).buffer(0)
    if not g.intersects(gipg): continue
    if g.intersection(gipg).area < 0.5*g.area: continue
    if 'GIPUZKOA' not in (dd.get('TERRITORIO') or ''): continue
    munis.append({'n': dd.get('NOMBRE_TOP',''), 'k': dd.get('COMARC_EUS',''), 'r': rings(g,120),
                  'c':[int(g.centroid.x-MINX), int(g.centroid.y-MINY)], 'a': round(g.area/1e4)})

payload={'bbox':[MINX,MINY,MAXX,MAXY],'gip':rings(gipg,60),'muni':munis,'f':feats,
         'stats':{str(k):round(v) for k,v in stats.items()},
         'npol':{str(k):v for k,v in npol.items()},
         'sp':{str(k):[[s,round(a)] for s,a in v.most_common(20)] for k,v in spa.items()}}
json.dump(payload, open('datos.json','w'), separators=(',',':'))
print('features:',len(feats),' municipios:',len(munis))
print('campos municipio ejemplo:', munis[0]['n'] if munis else '-')
for k in [0,1,2,3]: print('grupo',k, npol[k],'pol', round(stats[k]),'ha')
