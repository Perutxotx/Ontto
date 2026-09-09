import urllib.request, netCDF4 as nc, numpy as np, io, os, json, time
B="https://dap.ceda.ac.uk/neodc/esacci/soil_moisture/data/daily_files/COMBINED/v09.1"
import datetime as dt
res={}
t0=time.time()
for year in [2022,2023,2024]:
    d=dt.date(year,8,1); end=dt.date(year,11,30)
    ser=[]
    while d<=end:
        u=f"{B}/{year}/ESACCI-SOILMOISTURE-L3S-SSMV-COMBINED-{d:%Y%m%d}000000-fv09.1.nc"
        try:
            raw=urllib.request.urlopen(u, timeout=60).read()
            ds=nc.Dataset('m','r',memory=raw)
            lat=ds.variables['lat'][:]; lon=ds.variables['lon'][:]
            li=np.where((lat>=42.9)&(lat<=43.4))[0]; lo=np.where((lon>=-2.7)&(lon<=-1.7))[0]
            v=ds.variables['sm'][0][np.ix_(li,lo)]
            n=int(np.ma.count(v))
            ser.append([d.isoformat(), round(float(v.mean()),4) if n else None, n])
            ds.close()
        except Exception as e:
            ser.append([d.isoformat(), None, 0])
        d+=dt.timedelta(days=1)
    res[year]=ser
    ok=sum(1 for x in ser if x[1] is not None)
    print('%d: %d/%d dias con dato  (%.0fs)'%(year,ok,len(ser),time.time()-t0), flush=True)
json.dump(res, open('serie_sm.json','w'))
print('guardado')
