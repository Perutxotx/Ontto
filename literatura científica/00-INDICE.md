# Índice de literatura — Ontto

13 documentos. Nomenclatura: `AAAA_PrimerAutor_Tema.pdf`, ordenados por año.
La síntesis de factores extraída de todo esto está en
[docs/01-factores-fructificacion.md](../docs/01-factores-fructificacion.md).

Prioridad: ★★★ imprescindible · ★★ útil · ★ contexto

---

## Modelos de producción (el "cuánto")

### ★★★ `2012_MartinezPena_Modelos-de-rendimiento-Boletus-y-Lactarius.pdf`
Martínez-Peña, de-Miguel, Pukkala, Bonet, Ortega-Martínez, Aldea, Martínez de Aragón (2012).
*Yield models for ectomycorrhizal mushrooms in Pinus sylvestris forests…* For. Ecol. Manage.

**El artículo de referencia del ámbito español.** 18 parcelas valladas en Soria, 15 años
(1995–2009). Aporta las tres ecuaciones publicadas para ectomicorrícicos totales,
*Lactarius* y *B. edulis* — la primera de la historia para *B. edulis*. Marco conceptual de
tres bloques de factores (sitio / estructura de masa / meteorología) que usa todo el resto
de la literatura. R² = 0,22–0,42.

### ★★ `2019_SanchezGonzalez_Modelos-de-rendimiento-ECM-norte-de-Espana.pdf`
Sánchez-González et al. (2019). Forest Ecosystems 6:52. **Acceso abierto.**

Extiende lo anterior al **norte de España**, más cerca de tu ámbito. Dos cosas que
importan: área basimétrica óptima en **30–40 m²/ha** (no 15–20 como en el Mediterráneo), y
uso de **hurdle models** — modelos de dos partes para datos con muchos ceros, que es
exactamente la estructura estadística que Ontto va a necesitar.

### ★★ `2019_Herrero_Prediccion-de-productividad-Pinus-pinaster.pdf`
Herrero, Berraondo, Bravo, Pando, Ordóñez, Olaizola, Martín-Pinto, Oria de Rueda (2019).
Forests 10(3):206. **Acceso abierto.**

Series largas en *P. pinaster* mediterráneo con enfoque de cambio climático.

### ★ `2007_MartinezDeAragon_Productividad-y-balance-hidrico-pinares-Prepirineo.pdf`
Martínez de Aragón, Bonet, Fischer, Colinas (2007). For. Ecol. Manage. 252:239–256.

Interesa por dos ideas infrautilizadas: el **balance hídrico (P − ETP)** funciona mejor que
la lluvia bruta (R² = 0,66, el más alto de toda la revisión), y usa **temperatura del
suelo** en vez de la del aire — en concreto la mínima de agosto.

---

## Fenología y disparadores temporales (el "cuándo") — *lo que Ontto necesita*

### ★★★ `2025_Preprint_Disparadores-meteorologicos-diarios-Boletus-en-hayedo.pdf`
Preprint bioRxiv (dic. 2025). *Predicting porcini: a decade of sporocarp monitoring reveals
the meteorological triggers of Boletus edulis fruiting in central European beech forests.*
Datos y código: https://zenodo.org/records/17881359

**El trabajo más parecido a lo que quieres hacer.** 10 años (2015–2024), hayedo con roble y
abedul cerca de Bielefeld, 15–29 rodales, visitas 2–4 veces por semana, GPS de cada
carpóforo, 1.905 ejemplares. Escala **diaria**, no anual. Resultados: óptimo térmico de
**13,2 °C**, fructificación entre 7 y 19 °C, y una regla de exclusión nítida — **ningún
carpóforo con T > 17,5 °C y lluvia < 1 mm**. La señal de precipitación a 5 días es débil.
El 85,8 % de los días fueron cero. Tiene datos y código abiertos, así que se puede
reproducir.

### ★★ `2017_Alday_Escalas-espacio-temporales-de-biomasa-fungica.pdf`
Alday, Martínez de Aragón, de-Miguel, Bonet (2017). Scientific Reports 7:45824.
**Acceso abierto.**

Separa las escalas de variación y da un aviso incómodo: la **biomasa** de carpóforos
depende sobre todo de la **variación interanual**, mientras que la **riqueza** depende de
la escala espacial. La altitud no fue significativa. Motor principal: precipitación de
final de verano y principio de otoño. Leerlo antes de prometer precisión espacial fina.

### ★ `2023_Prochazka_Factores-climaticos-de-recoleccion-Europa-central.pdf`
Procházka, Soukupová, Tomšík, Mullen, Čábelková (2023). Forests 14(2):382.
**Acceso abierto.**

Perspectiva distinta: no modela producción sino **comportamiento del recolector** frente al
clima. Útil más adelante, cuando toque pensar en el usuario y no solo en el hongo.

---

## Teledetección y machine learning — *la vía que más rendimiento da*

### ★★★ `2020_Olano_NDVI-productividad-primaria-y-clima.pdf`
Olano, Martínez-Rodrigo, Altelarrea, Ágreda, Fernández-Toirán, García-Cervigón,
Rodríguez-Puerta, Águeda (2020). Agr. For. Meteorol. 288–289:108015.

**Probablemente el segundo artículo más importante para Ontto.** Series de 22 y 24 años.
Tres hallazgos que cambian el diseño:
- La **humedad de suelo por satélite iguala o supera a la precipitación** (r = 0,63–0,72).
- El **NDVI del año anterior** correlaciona con la producción (r = 0,41–0,60): parte de la
  cosecha de este otoño ya quedó determinada el verano pasado.
- Combinando clima + teledetección, **R²adj = 0,629** — muy por encima del 0,2–0,4 clásico.

Y propone explícitamente modelar la producción como **proceso en dos pasos** (acumulación
de recursos → conversión en carpóforos), que es la arquitectura que hemos adoptado.

### ★★★ `2024_MartinezRodrigo_Machine-learning-para-potencialidad-micologica.pdf`
Martínez-Rodrigo, Águeda, Ágreda, Altelarrea, Fernández-Toirán, Rodríguez-Puerta (2024).
Sustainability 16:5656. **Acceso abierto.**

El estado del arte metodológico. 17 parcelas de *P. pinaster* en Soria, serie larga,
combinando estructura forestal + índices de vegetación Landsat + clima. Compara árboles de
clasificación, random forest, SVM y redes neuronales; ganan las **redes neuronales**
(acierto en validación = 0,72). Variables seleccionadas: precipitación de enero, humedad de
noviembre, EVI, GNDVI, altura media, índice de sitio y área basimétrica. Construye un
índice de "explotabilidad micológica" **en dos etapas**.

---

## Factores de sitio y estructura (el "dónde")

### ★★ `2004_Bonet_Edad-de-masa-y-orientacion-Pinus-sylvestris.pdf`
Bonet, Fischer, Colinas (2004). For. Ecol. Manage. 203:157–175.

36 parcelas, 7 clases de edad, 4 orientaciones, 3 años, 9.073 carpóforos de 164 taxones. La
edad influye en 21 taxones y la orientación en 7. Correlación **negativa** entre edad de la
masa y producción de comestibles.

### ★ `2019_MumcuKucuker_Pendiente-orientacion-altitud-Boletus-edulis.pdf`
Mumcu Kucuker (2019). Artvin Coruh Univ. J. For. Fac. 20(1):10–17. **Acceso abierto.**

75 parcelas en Turquía. Diferencias significativas por **orientación** y **pendiente**, no
por altitud. Menor productividad en orientación norte y en pendientes del 20–30 %. Estudio
modesto, pero es de los pocos que aísla la topografía.

---

## Tu zona exacta — Gipuzkoa y Norte de Navarra

### ★★★ `2018_GobNavarra_Diagnostico-hongos-ANEXOS-parcelas-y-productividad.pdf`
Gobierno de Navarra, Dirección General de Medio Ambiente y Agua (2018).
*Diagnóstico de productos forestales no maderables I: Hongos — Anexos.*

**El documento más directamente aplicable de todos.** Describe cómo la administración
navarra ya hace, oficialmente, una versión estática de lo que Ontto quiere hacer:

- Red de parcelas micológicas **desde 1997**. Hoy **92 parcelas en Navarra, 32 en la
  comarca cantábrica**. Muestreo en agosto–noviembre.
- Red específica de hayedo creada en 2003: **60 parcelas**, estratificadas por ecología del
  hayedo, calidad de estación y luminosidad → 12 tipos de hayedo.
- **Método de cartografía de potencial**: cruzar *serie de vegetación* × *luminosidad
  (hillshade SIG)* y aplicar las medias de producción de las parcelas. Barato y replicable.
- Grupos micológicos oficiales **MIC1** (*Boletus* spp.), **MIC2** (*Cantharellus*,
  *Craterellus*, *Hydnum*), **MIC3** (*Amanita*, *Russula*), **SAP** (*Clitocybe*).
- Producción potencial de la comarca cantábrica: **643.224 kg**, de los que el hayedo
  acidófilo de umbría aporta el 48,56 %.
- Presión recolectora ~0,3 recolectores/ha.

### ★★ `2018_GobNavarra_Diagnostico-hongos-INFORME-principal.pdf`
El informe principal del que cuelgan los anexos anteriores. Contexto normativo, económico y
de aprovechamiento.

---

## Huecos conocidos

- **Karavani et al. (2018)**, Agr. For. Meteorol. 248:432–440,
  DOI 10.1016/j.agrformet.2017.10.024 — de pago, sin copia en abierto localizada. Es la
  fuente del **retardo de hasta un mes entre lluvia y humedad del suelo**. Merece pedirlo a
  los autores o vía biblioteca.
- **Ágreda et al. (2013)**, Mycorrhiza — dinámica estacional del micelio extrarradical.
- **Nada sobre *Pinus radiata***, que es la masa dominante de Gipuzkoa.
- **Nada sobre *Calocybe gambosa*** (perretxiko), especie de primavera, de pastizal, y
  probablemente la más buscada de Gipuzkoa.
- **No hay red de parcelas micológicas conocida en Euskadi**, a diferencia de Navarra. Sí
  existe Inventario Forestal de la CAE (~4.000 parcelas, HAZI) y Mapa Forestal anual.
