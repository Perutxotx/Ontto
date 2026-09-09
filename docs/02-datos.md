# Inventario de fuentes de datos — Gipuzkoa

Paso 2 del proyecto. Se recorre **factor a factor**, validando cada uno antes de pasar al
siguiente. La numeración es la de la tabla de síntesis en
[01-factores-fructificacion.md](01-factores-fructificacion.md) §4.

**Estado:** 6 de 21 factores resueltos.

---

## Resumen

| # | Factor | Estado | Fuente | Fichero |
|---|---|---|---|---|
| 13 | Especie arbórea | ✅ | Mapa Forestal CAE 2024 | `gipuzkoa_forestal.csv` |
| 19 | Altitud | ✅ | MDT LiDAR 2017, 25 m | `masas_altitud.csv` |
| 18 | Pendiente | ✅ | derivado del MDT | `masas_pendiente.csv` |
| 17 | Orientación | ✅ | derivado del MDT | `masas_orientacion.csv` |
| 16 | Luminosidad | ✅ | derivado del MDT | `masas_luminosidad.csv` |
| 1 | Humedad del suelo | ✅ parcial | ESA CCI · CEDA | `humedad_suelo_esacci_otonos.json` |
| 8, 9 | NDVI / EVI / GNDVI | ⬜ | Sentinel-2 / Landsat | — |
| 12 | Edad de masa | 🟡 aprox. | campo `EMASA1` del Mapa Forestal | `gipuzkoa_forestal.csv` |
| 10 | Área basimétrica | ⬜ | LiDAR o Inventario Forestal | — |
| 11 | Altura dominante | ⬜ | LiDAR | — |
| 14 | Índice de sitio | ⬜ | derivado | — |
| 15 | Serie de vegetación / pH | ⬜ | ¿existe en Euskadi? | — |
| 20 | Retención de agua del suelo | ⬜ | mapa de suelos | — |
| 2–7 | Meteorología | ⬜ | Euskalmet | — |
| 21 | Presión recolectora | ⬜ | sin fuente identificada | — |

---

## Factor 13 · Especie arbórea hospedante

**Fuente:** Mapa Forestal de la CAE 2024, Gobierno Vasco.
Ficha en [Open Data Euskadi](https://opendata.euskadi.eus/catalogo/-/mapa-forestal-del-pais-vasco/),
federada en datos.gob.es. Descarga directa:
`https://www.geo.euskadi.eus/cartografia/DatosDescarga/Agricultura/INV_FORESTAL_2024_10000_ETRS89.zip`

- Shapefile, 287 MB, ETRS89 UTM30N, escala 1:10.000, polígono mínimo 0,10 ha
- Fotointerpretación sobre ortofoto de 25 cm, metodología IFN4
- **Actualización anual**, serie desde 2004. Licencia CC BY
- 220.606 polígonos en la CAPV → **79.740 en Gipuzkoa (198.261 ha)**

**Campos útiles:** `SP1_es`/`SP2_es`/`SP3_es` (especies), `O1`/`O2`/`O3` (% ocupación),
`TIPES_es` (tipo estructural: distingue *Bosque* de *Bosque de Plantación*),
`EMASA1` (estado de masa → factor 12), `FCCARB` (cabida cubierta), `Shape_Area`.

**Ojo con el nombre:** el fichero se llama `INV_FORESTAL` pero es el **Mapa** Forestal
(cartografía continua por fotointerpretación), no el **Inventario** Forestal (~4.000
parcelas de campo). Son datasets distintos.

### Clasificación por valor como hospedante de MIC1

Criterio: capacidad de formar **ectomicorrizas**. Las cupresáceas y taxáceas
(criptomeria, secuoya, chamaeciparis) forman micorrizas arbusculares, no ecto — ahí no
puede fructificar un *Boletus* por buena que sea la meteorología. Es un filtro duro.

| Clase | ha | % Gipuzkoa | Contenido |
|---|---|---|---|
| **Frondosa autóctona ECM** | **54.733** | **27,7 %** | Haya 19.017 · Mixto atlántico 19.062 · Roble pedunculado 10.116 · Roble americano 2.421 · Encina 2.369 · Castaño 404 |
| Conífera ECM | 54.385 | 27,5 % | Radiata 32.340 · Laricio 6.957 · Alerce 6.278 · Douglas 5.490 |
| Sin simbiosis | 10.122 | 5,1 % | Criptomeria 2.736 · Secuoya 2.324 · Eucaliptos · ripícolas |
| Otras masas | 2.979 | 1,5 % | Mezclas y frondosas menores |

**Decisión metodológica pendiente de revisar:** el *Pinus radiata* (32.340 ha, un sexto de
Gipuzkoa) está en "conífera ECM". Ecológicamente es correcto —los pinos forman
ectomicorrizas— pero **no hay ni un solo trabajo en la literatura revisada sobre
producción de onddos en radiata**. Si el conocimiento local dice que no salen, bajarlo de
categoría cambia el mapa sustancialmente.

**Mapa interactivo:** https://claude.ai/code/artifact/665a5506-1624-4120-a784-765548f6c0f3

---

## Bloque topográfico · factores 19, 18, 17, 16

**Fuente única:** MDT LiDAR 2017, Gobierno Vasco.
FTP abierto: `ftp://ftp.geo.euskadi.net/lidar/MDE/MAX_ACTUALIDAD/MDT_LIDAR_2017_ETRS89/`

Tres resoluciones: 1 m (15 GB, en 15 partes), 5 m (941 MB) y **25 m (41 MB, el que usamos)**.
GeoTIFF float32 + world file, ETRS89 UTM30N. Nodata = −3,4028e38.

**Por qué 25 m basta:** las masas forestales promedian 9 ha → ~144 píxeles por rodal.
Si en el futuro hiciera falta detalle intra-rodal, el de 5 m está disponible.

**Validación de la georreferenciación:**
- Superficie calculada 197.848 ha vs 197.839 ha del límite vectorial → **error 0,005 %**
- Cota máxima 1.545,8 m en Zegama vs 1.551 m reales de Aitxuri
- Abaltzisketa 1.334,7 m vs 1.346 m de Txindoki
- Los ~10 m de defecto son el efecto esperado de promediar una cumbre afilada en 25 m

**Mapa interactivo:** https://claude.ai/code/artifact/0af67668-cc29-4260-9b69-913efa10e2c7

### Factor 19 · Altitud

Mediana 351,8 m · media 391,3 m · máximo 1.545,8 m. El 57 % del territorio entre 100 y
500 m. 216 ha con cota negativa (marismas y estuarios con marea baja) — irrelevantes.

**Discrimina con fuerza.** Mediana por especie: ripícolas 154 m · mixto atlántico 259 m ·
roble pedunculado 282 m · radiata 367 m · Douglas 511 m · alerce 616 m · laricio 639 m ·
**haya 693 m**.

**Papel en Ontto: no es un predictor, es el que espacializa la meteorología.** Con 1.500 m
de desnivel y un gradiente térmico de 0,5–0,65 °C/100 m, hay hasta 9 °C entre costa y
cumbres. Dado que el óptimo de fructificación está en 13,2 °C con exclusión por encima de
17,5 °C, ese gradiente decide qué parte del territorio fructifica cada semana.
**Va en la capa DISPARO, no en la POTENCIAL.**

### Factor 18 · Pendiente

Mediana 21,4° (39,3 %). Solo el 6,7 % del territorio baja del 10 % de pendiente; el 67 %
supera el 30 %.

**No discrimina.** Todos los grupos entre 22,8° y 24,8°; entre haya y radiata hay 1,2°.
Extremos correctos: ripícolas 14,6° (lo más llano), encina 28,9° (roquedo calizo).

**Papel en Ontto: filtro de accesibilidad, no predictor.** 29.216 ha superan el 60 % de
pendiente. Predecir setas ahí puede ser correcto e inútil a la vez.

**Aviso sobre la literatura:** Mumcu Kucuker 2019 sitúa la productividad mínima en la clase
20–30 %, pero esa clase es solo el 15 % de Gipuzkoa. Su resultado **no es transferible**.

### Factor 17 · Orientación

Dato circular: hay que promediar como vectores. Para el modelo se usa **nortidad** (cos) y
**estidad** (sin), nunca el ángulo crudo.

Reparto muy equilibrado: 10,4 %–13,9 % por octante, con leve sesgo norte (53,8 % umbría).
4.491 ha llanas (<2°) con orientación indefinida.

**Discrimina bien.** Nortidad: alerce +0,412 · **haya +0,285** · Douglas +0,283 ·
mixto atlántico +0,141 · radiata +0,028 · laricio −0,061 · **encina −0,223**.

Validación: la encina es lo más solano de Gipuzkoa (35,7 % umbría) **y** lo más empinado
(28,9°). Roquedo calizo, solano y vertical — la ecología del encinar cantábrico entera
sale de dos rásteres derivados del MDT.

Dato secundario: coherencia de ladera 0,692 en frondosa autóctona vs 0,842 en conífera.
Las plantaciones son bloques regulares; el bosque natural envuelve topografía compleja.

**No fijar el signo del efecto a priori.** Ver el aviso del factor 16.

### Factor 16 · Luminosidad

Calculado como **radiación solar potencial acumulada del 1 de agosto al 30 de noviembre**,
integrando 933 posiciones solares (41 días × cada 30 min de luz) a 43,15° N, con:
- incidencia sobre el plano inclinado (pendiente + orientación)
- transmitancia de cielo claro con masa de aire
- **sombras proyectadas por el terreno circundante**, vía ángulo de horizonte en 16 rumbos
  hasta 2 km (101 millones de valores, `horizon16.npy`, 452 MB)

Índice relativo al llano horizontal: p1 = 0,32 · mediana = 0,93 · p99 = 1,32.
**Una masa puede recibir cuatro veces más sol que otra.**

Por especie: encina 0,981 · laricio 0,953 · radiata 0,899 · roble pedunculado 0,867 ·
mixto atlántico 0,845 · **haya 0,777** · alerce 0,744 · **aliso 0,715**.

**Nota:** la cifra en kWh/m² del CSV corresponde a los 41 días muestreados, no al total
estacional (×3 aprox.). El **índice** es la magnitud a usar.

#### Hallazgo: el hillshade por defecto mide nortidad, no iluminación

Correlación de la radiación estacional real con hillshades de distinto acimut:

| Acimut | r |
|---|---|
| 180° (sur — sol real) | **+0,988** |
| 225° (SO) | +0,726 |
| 90° (E) | +0,012 |
| **315° (NO — por defecto en ArcGIS/QGIS)** | **−0,601** |
| 0° (N) | −0,912 |

El +0,988 con el hillshade al sur **valida nuestro cálculo de radiación**.

Y el 315°/45° correlaciona +0,622 con la nortidad y −0,601 con la radiación real: es una
convención **cartográfica** (luz desde arriba-izquierda), no una posición solar. El sol
nunca está en el noroeste a altura apreciable a nuestra latitud.

**Consecuencia para la réplica del método navarro.** El documento de Navarra dice solo
*"valores GIS de sombreado o hillshade"*, que es lo que se escribe cuando se acepta el
valor por defecto. Si fue así, **su clase "luminoso" es en realidad la sombría en términos
de radiación real**, y su hallazgo "más producción en hayedo acidófilo luminoso"
significaría lo contrario de lo que parece.

No está verificado — no sabemos qué acimut usaron. Es una pregunta a hacerles si algún día
se piden sus datos. Mientras tanto: **una razón más para no fijar el signo a priori.**

#### Variable inesperada: encajonamiento

El ángulo medio de horizonte en los 16 rumbos mide cuánto cielo ve cada punto.
Media 11,8° · p5 4,1° · p95 20,5°.

Por especie: **aliso 20,1°** · ripícolas 16,7° · roble pedunculado 14,6° · haya 13,4° ·
radiata 12,6° · **laricio 10,6°**.

**Correlación con la nortidad: −0,013.** Cero. Es información completamente independiente
de la orientación, que ni la pendiente ni el aspecto contienen.

Lo demuestra el aliso: nortidad +0,266 (4.º más umbrío de 24) pero radiación 0,715 (el
**último** de 24). Está en fondos de valle, encajonado entre laderas que le tapan el sol
bajo de otoño mire donde mire. Sin el cálculo de horizonte, este efecto es invisible.

### Recomendación de variables topográficas para el modelo

**Radiación + encajonamiento**, no orientación + radiación. La radiación ya contiene la
orientación (r = −0,892 con nortidad); el encajonamiento añade lo que ninguna ve.

---

## Factor 1 · Humedad del suelo

### La literatura usa dos cosas distintas bajo el mismo nombre

| Trabajo | Qué usó realmente |
|---|---|
| Olano 2020 | **ESA CCI Combined** — satélite (ASCAT + radiómetros), 0,25°, medias mensuales |
| Karavani 2018 | **medfate** — balance hídrico **simulado**, no satélite |

### Limitación de los productos satelitales bajo bosque

En banda C, con vegetación densa *"la señal retrodispersada procede enteramente del
interior del dosel, sin contribución directa del suelo"*. Saturación en torno a
**100 Mg/ha de biomasa aérea** — lo que tiene un hayedo maduro. SMAP marca como no fiables
las lecturas por encima de VOD ≈ 0,5.

Esto descarta en la práctica el **Copernicus SSM 1 km**: mejor resolución, pero ciego justo
donde nos importa.

### ESA CCI — comprobado empíricamente

**Acceso abierto y sin registro** en el archivo CEDA:
`https://dap.ceda.ac.uk/neodc/esacci/soil_moisture/data/daily_files/COMBINED/v09.1/{año}/`

- NetCDF-4, un fichero diario global (~2 MB), variable `sm` en m³/m³
- Resolución 0,25° → Gipuzkoa cubierta por **11 píxeles con dato válido** de 15
- Los 4 sin dato son la fila norte: es el Cantábrico, correctamente enmascarado
- **No hay enmascaramiento por bosque denso** — 122/122 días con dato en 2022 y 2023

**Dinámica medida (agosto–noviembre):**

| | 2022 | 2023 |
|---|---|---|
| Mínimo | 0,210 | 0,202 |
| Máximo | 0,341 | 0,324 |
| Variación intraestacional | **52 %** | **46 %** |
| Media agosto → noviembre | 0,240 → 0,281 | 0,253 → 0,283 |

Los pulsos de recarga se ven con nitidez: +0,074 m³/m³ en tres días el 15/10/2023.

**Pero la variación interanual es de solo 4,3 %.** En el Mediterráneo es enorme, y por eso
Olano explica con ella el 63–72 % de la producción. En Gipuzkoa el suelo está húmedo casi
todos los otoños: **aquí el agua rara vez es limitante**. Probablemente sirva para el
*cuándo* dentro de la temporada, no para el *cuánto* de cada año.

### Dos productos para dos trabajos

| Uso | Producto | Estado |
|---|---|---|
| Calibrar el modelo | ESA CCI v09.1/09.2 en CEDA | **1978–2024, diario, gratis, sin registro** |
| Ejecutar la app a diario | C3S NRT o Copernicus SSM 1 km | Requiere registro · **pendiente** |

El archivo climático va con año y medio de retraso. Magnífico para entrenar, inútil para
funcionar en tiempo real. Conviene resolverlo antes del despliegue, no durante.

### Recomendación

**Balance hídrico propio** como vía principal (lo que hizo Karavani con `medfate`): es
físicamente sólido, funciona bajo cualquier dosel y da valor por rodal en vez de por
comarca. **Pero depende del bloque 4 (precipitación y ETP, Euskalmet) y del factor 20
(capacidad de retención del suelo).** No se puede construir todavía.

ESA CCI queda mientras tanto como índice regional de disparo.

---

## Patrón transversal detectado

Tres factores topográficos y uno forestal después, se repite lo mismo:

| Factor | ¿Discrimina? | Correlación con especie |
|---|---|---|
| 19 · Altitud | Sí, mucho | Haya 693 m vs ripícolas 154 m |
| 18 · Pendiente | No | Todo entre 42 y 47 % |
| 17 · Orientación | Sí | Alerce +0,41 vs encina −0,22 |
| 16 · Radiación | Sí | Encina 0,98 vs aliso 0,72 |

> **En Gipuzkoa, la especie arbórea ya lleva dentro la topografía.** El haya está donde
> está *porque* es alto y umbrío; la encina, *porque* es solano y escarpado.

Meter especie, altitud, orientación y radiación como variables independientes sería contar
lo mismo cuatro veces, y el modelo podría atribuir a la topografía un efecto que es del
hayedo. Solución estándar: modelar dentro de cada tipo de bosque, o usar los residuos
topográficos respecto a lo esperado para esa especie. **A resolver en el paso del modelo.**

---

## Reproducibilidad

Todo el proceso está en [scripts/](../scripts/), numerado por orden de ejecución.
Requiere: `numpy pandas shapely pyshp pyproj tifffile Pillow netCDF4`.
