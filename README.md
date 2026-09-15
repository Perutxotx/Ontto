# Ontto

Estimador de probabilidad de fructificación de **onddo** (*Boletus* gr. *edulis*) en
**Gipuzkoa**, a partir de cartografía forestal, topografía y meteorología.

```
Probabilidad(aquí, ahora)  ≈  POTENCIAL(x)  ×  DISPARO(t)
                              └─ estático ─┘   └─ diario ─┘
```

- **POTENCIAL** — qué produciría cada rodal en un año medio. Especie arbórea, sustrato y
  apertura del dosel, con coeficientes medidos en 60 parcelas de Navarra.
  Se recalcula **una vez al año**, cuando sale el Mapa Forestal nuevo.
- **DISPARO** — si las condiciones de hoy favorecen la fructificación, y a qué cota.
  Temperatura, pulso de lluvia con retardo y balance hídrico. Se recalcula **a diario**.

Todo el razonamiento, con sus fuentes y sus limitaciones, está en [docs/](docs/).

---

## Qué hay aquí

```
src/                     lo que se ejecuta
  actualiza.py           descarga AEMET y regenera el disparo diario
  construye_base.py      regenera el mapa (una vez al año)
  climatologia_base.json media 1970-2015, referencia del gráfico
web/                     la app
  index.html
  manifest.json          para instalarla en el móvil
  sw.js                  caché offline
publico/                 lo que se publica
  index.html · manifest.json · sw.js · iconos/
  datos/base.json        ~900 KB · el mapa · cacheado
  datos/disparo.json      ~20 KB · el índice · cada día
docs/                    el proyecto: decisiones, datos, modelo
scripts/                 los 31 pasos del análisis, en orden
literatura científica/   18 trabajos, indexados en 00-INDICE.md
```

## Puesta en marcha

**1. Clave de AEMET.** Se pide en [opendata.aemet.es](https://opendata.aemet.es/centrodedescargas/inicio)
con un correo; llega al momento y es gratis.

**2. Guardarla como secreto** en el repositorio:
`Settings → Secrets and variables → Actions → New repository secret`,
nombre `AEMET_API_KEY`.

> ⚠️ **Las claves de AEMET caducan.** La actual expira el **13 de diciembre de 2026**.
> Cuando llegue, el flujo empezará a fallar: se pide otra en el mismo sitio y se
> reemplaza el secreto. El flujo avisa solo, porque la comprobación de sanidad rechaza
> publicar si el último dato observado tiene más de 4 días.

**3. Activar Pages:** `Settings → Pages → Source: GitHub Actions`.

**4. Listo.** El flujo corre cada mañana a las 05:40 UTC (07:40 en Gipuzkoa) y también
a mano desde la pestaña *Actions*.

### Instalarla en el móvil

Ontto es una **PWA**: se instala desde el navegador, sin tienda de aplicaciones.

- **Android / Chrome** — abrir la web y aceptar *«Instalar aplicación»*, o
  *Menú → Añadir a pantalla de inicio*.
- **iPhone / Safari** — *Compartir → Añadir a pantalla de inicio*.

Una vez instalada **funciona sin cobertura**: el mapa y el último índice descargado quedan
guardados en el teléfono. Es el requisito, no un extra — en el monte no hay red, y es
justo donde se usa.

El índice se refresca solo cuando hay conexión; sin ella se muestra el último disponible,
con su fecha en la cabecera.

### En local

```bash
pip install numpy pandas pyshp shapely pyproj tifffile Pillow netCDF4
export AEMET_API_KEY=...              # o ~/.config/ontto/aemet.key
python src/actualiza.py               # regenera publico/datos/disparo.json
python -m http.server -d publico 8000 # y abrir localhost:8000
```

`src/actualiza.py --cache` reutiliza la última descarga de climatología, útil al depurar.

---

## Lo que Ontto no es

**No dice que haya setas.** Dice que las condiciones se parecen a las que la literatura
asocia con la fructificación, en montes que deberían producir.

**Validado a medias.** El *cuándo* sí: contra 132 registros de fructificación con fecha
exacta —herbario ARAN de Aranzadi, iNaturalist y otros, vía GBIF— el índice acierta de forma
significativa en otoño (percentil 61 frente al 50 esperado por azar, z = +3,1). El *cuánto*
no: no existe producción medida en kg en Gipuzkoa, y los coeficientes vienen prestados de
Navarra, de bosque y especie equivalentes. Todo el detalle, con sus reservas, en
[docs/08-validacion.md](docs/08-validacion.md).

**Faltan 72.000 ha.** Las plantaciones de conífera —radiata sobre todo— no tienen
coeficiente medido en ninguna publicación. Aparecen fuera del mapa, no en cero: sería
afirmar algo que no sabemos.

**Dos parámetros son elecciones informadas, no ajustes.** El umbral de apertura del dosel
(60 % de cabida cubierta) y el umbral hídrico (40 % de la capacidad del suelo). Con datos de
producción locales se ajustarían en una tarde.

El **retardo de la lluvia** (10 días) ya no está en esa lista: Salerni et al. 2023 sitúa el
efecto «sobre todo a partir del décimo día» con el pico en el 12, y mover la ventana entre 5
y 24 días no cambia el resultado. La **asimetría estacional** tampoco: reproduce el
calendario real de hallazgos con r = +0,81.

## Licencia y fuentes

Código bajo MIT. Los datos son de terceros y llevan la suya:

- **Mapa Forestal de la CAE 2024**, series de vegetación y MDT LiDAR 2017 —
  Eusko Jaurlaritza / Gobierno Vasco, CC BY 4.0
- **Atlas Climático del País Vasco** — Gobierno Vasco, CC BY 4.0
- **AEMET OpenData** — Agencia Estatal de Meteorología
- **Coeficientes de producción** — Gobierno de Navarra, *Micología forestal en Navarra*
  (proyecto Micosylva, 2011) y *Diagnóstico de productos forestales no maderables* (2018)
