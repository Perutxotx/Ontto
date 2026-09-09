# Factores de fructificación de hongos — síntesis de literatura

**Estado:** paso 1 del proyecto Ontto. Documento vivo.
**Ámbito objetivo:** Gipuzkoa y Norte de Navarra.
**Fecha:** 2026-09-06

---

## 0. La distinción que lo condiciona todo

La literatura responde bien a **una** pregunta y mal a **la otra**. Conviene tenerlo claro
antes de diseñar nada:

| Pregunta | Unidad | Estado en la literatura |
|---|---|---|
| **¿Cuánto produce este monte en un año?** | kg/ha/año | Bien resuelto. Modelos publicados y validados. |
| **¿Ha salido esta semana, y dónde?** | evento / presencia | Mal resuelto. Muy poca literatura, y la que hay es modesta. |

Ontto quiere lo segundo. Casi todos los modelos disponibles hacen lo primero.

**Esto no es un callejón sin salida, es una indicación de arquitectura.** El camino
practicable es factorizar el problema en dos capas que se multiplican:

```
Probabilidad(hongos aquí, ahora)  ≈  POTENCIAL(x)  ×  DISPARO(t)
                                     └─ estático ─┘   └─ dinámico ─┘
                                     dónde puede           cuándo
                                     haberlos              se activa
```

- **POTENCIAL(x)** — capa espacial casi estática (cambia en años, no en días): especie
  arbórea, edad/estructura de la masa, sustrato, orientación, altitud. Se calcula **una
  vez** con SIG y se guarda como ráster. Aquí la literatura es sólida.
- **DISPARO(t)** — serie temporal común a toda la comarca o a bandas altitudinales:
  lluvia acumulada con retardo, temperatura, balance hídrico. Se recalcula a diario.
  Aquí la literatura es floja, y es donde asumimos el riesgo real del proyecto.

> **Esta descomposición no es un apaño nuestro: la literatura ha llegado a ella por su
> cuenta.** Olano et al. (2020) proponen explícitamente modelar la producción como un
> **proceso en dos pasos** — la productividad primaria del año anterior acumula recursos
> en el árbol, y las condiciones climáticas de la temporada controlan la capacidad del
> micelio de convertir esos recursos en carpóforos. Martínez-Rodrigo et al. (2024)
> construyen un índice de "explotabilidad micológica" también **en dos etapas**. Que tres
> equipos independientes converjan en la misma estructura es la señal más fuerte que he
> encontrado de que es el planteamiento correcto.

Todo lo que sigue está clasificado según a cuál de las dos capas alimenta.

---

## 1. Factores del DISPARO temporal (el "cuándo")

### 1.1. Precipitación acumulada — **el factor dominante**

Es el predictor más potente y el más consistente en toda la literatura.

- **Martínez-Peña et al. (2012)**, `pinus_sylvestris_Martinez.pdf` — Usa
  `P_otoño` = suma de precipitación de **agosto + septiembre + octubre**. Coeficiente
  positivo en los tres modelos ajustados (total ectomicorrícicos, *Lactarius*, *Boletus*).
- **Karavani et al. (2018)** — La precipitación es el predictor más significativo de la
  productividad anual. Y un matiz crítico: **el efecto de la lluvia sobre la humedad del
  suelo se retrasa hasta un mes**. La lluvia no es el disparo; la humedad del suelo lo es.
- **Martínez de Aragón et al. (2007)** — Mejora el ajuste usando no la lluvia bruta sino
  el **balance hídrico** (ver 1.3).
- **Alday et al. (2017)** — 8 años, gradiente altitudinal en *P. sylvestris*. El motor
  principal de variación es la **precipitación de final de verano y principio de otoño**,
  consistente en todos los gremios fúngicos. Precipitación = recurso limitante.

**Y un giro importante — la humedad del suelo por satélite bate a la lluvia:**

- **Olano et al. (2020)** — 22 y 24 años de serie. La **humedad de suelo por teledetección
  iguala o supera el poder predictivo de la precipitación** (r = 0,63–0,72 frente a la
  lluvia). Es coherente con Karavani: lo que importa es el agua en el suelo, y la lluvia
  es solo un proxy ruidoso con retardo.

**Retardo (el punto más importante y peor documentado):**

| Fuente | Ventana usada | Escala |
|---|---|---|
| Martínez-Peña 2012 | Ago+Sep+Oct | mensual |
| Karavani 2018 | mismo mes; efecto lluvia→suelo con retardo de hasta 1 mes | mensual |
| Preprint hayedos 2025 | media móvil de **5 días** previos | diaria |
| Revisión general | correlación a 3–5 meses; lluvia de los 2 días y 7–14 días previos *reduce* la producción | diaria |

> No hay consenso sobre la ventana. Para un modelo diario habrá que **aprenderla de los
> datos** en lugar de importarla, probablemente con varias ventanas simultáneas
> (p. ej. acumulados a 7 / 15 / 30 / 60 días) y dejar que el ajuste decida.

### 1.2. Temperatura

- **Martínez-Peña et al. (2012)** — `T_otoño` = suma de temperaturas medias de
  **septiembre + octubre + noviembre**. Coeficiente positivo. Nótese el **desfase de un
  mes respecto a la ventana de lluvia**: primero llueve, después las temperaturas templadas
  activan la fructificación. Los autores lo subrayan explícitamente.
- **Preprint hayedos 2025**, `Predicting_porcini_beech_forests_2025_preprint.pdf` — Lo
  más cercano a lo que Ontto quiere hacer. 10 años (2015–2024), 15–29 rodales de hayedo
  y roble cerca de Bielefeld, visitas 2–4 veces por semana, GPS de cada carpóforo, 1.905
  ejemplares de *B. edulis*. Resultados:
  - **Óptimo térmico de ~13,2 °C** (media de 5 días, término cuadrático).
  - La mayoría de las fructificaciones entre **7 °C y 19 °C**.
  - **Ningún carpóforo con T > 17,5 °C y lluvia < 1 mm/día.** Es la regla de exclusión
    más nítida publicada.
  - Efecto de la precipitación positivo pero **lineal y débil** a 5 días.
  - Conclusión de los autores: la temperatura restringe más que la lluvia a corto plazo.
- **Martínez de Aragón et al. (2007)** — Usa **temperatura del suelo**, no del aire, y le
  funciona mejor. En concreto la **temperatura mínima media del suelo en agosto**.

### 1.3. Balance hídrico (lluvia − evapotranspiración)

El hallazgo más útil del paper de 2007 y probablemente infrautilizado:

> La mejor ecuación climática (**R² = 0,66**, la más alta de toda la literatura revisada)
> no usa la lluvia bruta, sino la **diferencia entre precipitación y evapotranspiración
> potencial acumulada de septiembre y octubre**, más la **temperatura mínima del suelo de
> agosto**.

Es decir: **P − ETP** supera a **P** sola. Tiene sentido biológico — lo que importa al
micelio es el agua que queda en el suelo, no la que cae.

Variables relacionadas que ese trabajo también encuentra significativas:
- Exceso hídrico mensual (septiembre, diciembre).
- **Amplitud térmica del suelo** (intervalo entre temperatura máxima y mínima del suelo).

### 1.4. Pulsos y discontinuidad

El preprint de hayedos observa que en varios años la producción **no fue continua, sino en
pulsos discretos dentro de la temporada**. Y que el **85,8 % de los días-observación
fueron cero**. Dos consecuencias de diseño:

- El objetivo no es una curva suave, son **eventos**.
- Los datos están **fuertemente inflados en ceros** → distribución binomial negativa o
  modelo de dos partes (¿hay pulso? / ¿cuánto?), no una regresión lineal ingenua.

Confirmación independiente: **Sánchez-González et al. (2019)** ajustan sus modelos para el
norte de España con **hurdle models** (modelos de barrera, literalmente de dos partes:
primero "¿hay o no hay?", después "¿cuánto?"). Es la elección estadística estándar en este
problema y deberíamos adoptarla desde el principio.

### 1.5. Productividad primaria del año anterior — el factor "memoria"

**Olano et al. (2020)** encuentra que el **NDVI del año anterior** correlaciona con la
producción (r = 0,41–0,60). Interpretación: un año bueno de fotosíntesis carga de
carbohidratos al árbol, que alimenta al micelio, que fructifica al año siguiente.

Implicación práctica fuerte: **parte de la predicción de este otoño ya está determinada
por el verano pasado**, y es observable gratis por satélite. Es un predictor que ningún
recolector maneja y que Ontto sí podría.

Combinando clima + teledetección, Olano alcanza **R²adj = 0,629**, muy por encima del
0,22–0,42 de los modelos solo climáticos.

---

## 2. Factores del POTENCIAL espacial (el "dónde")

### 2.1. Estructura de la masa forestal — el factor manejable más fuerte

| Variable | Efecto | Fuente |
|---|---|---|
| **Área basimétrica (G)** | El factor más determinante para *B. edulis*. Relación **unimodal**: óptimo en 40–45 m²/ha, peor por debajo y por encima. | Martínez-Peña 2012 |
| Área basimétrica | En pinares mediterráneos el óptimo baja a **15–20 m²/ha** | Bonet et al. 2008, 2010 |
| **Área basimétrica** | **Norte de España**: curva unimodal asimétrica a la derecha, máximo en **30–40 m²/ha** | Sánchez-González et al. 2019 |
| **Altura dominante (H_dom)** | Positiva (ln) para el total de ectomicorrícicos y para *Lactarius*. Óptimo de *Lactarius* en **13–14 m**. | Martínez-Peña 2012 |
| **Edad de la masa** | Unimodal. Máximo de ectomicorrícicos a los **60–70 años** en *P. sylvestris*, coincidiendo con el máximo crecimiento del arbolado. | Martínez-Peña 2012 |
| Edad de la masa | **En hayedo: producción a partir de ~40 años, máximo entre 50 y 90 años.** | Gobierno de Navarra |
| Edad de la masa | Influye en 21 de los taxones estudiados; correlación *negativa* con especies comestibles | Bonet et al. 2004, `The_relationship_between_forest_age_and.pdf` |
| Fracción de cabida cubierta / LAI | Significativas en modelos combinados | Martínez de Aragón 2007 |

> **Ojo con la transferencia.** Estos óptimos numéricos están calibrados en *Pinus
> sylvestris* de clima continental (Soria, Pirineo, Cataluña). Gipuzkoa y el norte de
> Navarra son hayedo, robledal y **plantación de *Pinus radiata***, en clima atlántico.
> Los coeficientes concretos **no son trasladables**; la *forma* de las relaciones
> (unimodal en G y en edad) probablemente sí.

### 2.2. Especie arbórea y tipo de bosque

Determina qué especies de hongo son posibles: casi todos los comestibles de interés son
**ectomicorrícicos**, es decir, viven en simbiosis obligada con un árbol concreto.

Datos oficiales de la **Comarca Cantábrica de Navarra** — es tu zona:

- Las masas con mayor potencial micológico son los **pinares de pino silvestre** y los
  **hayedos acidófilos** con buena luminosidad.
- El **hayedo acidófilo de umbría** aporta el 48,56 % de la producción total de la comarca
  (312.347 kg de 643.224 kg), sobre todo por su extensión.
- Grupos micológicos usados oficialmente:
  - **MIC1** — *Boletus aereus, B. aestivalis, B. edulis, B. pinophilus* (el grupo estrella)
  - **MIC2** — *Cantharellus cibarius, C. cinereus, Craterellus cornucopioides, Hydnum repandum, H. rufescens*
  - **MIC3** — *Amanita rubescens, Boletus erythropus, Russula* spp.
  - **SAP** — *Clitocybe geotropa, C. maxima, C. nebularis* (saprótrofos)
- Los grupos más productivos son **MIC1 y MIC3**.

### 2.3. Tipo de hayedo (serie de vegetación) — sustrato

Navarra clasifica sus hayedos por serie fitosociológica y le funciona como predictor:

1. **Hayedos basófilos cantábricos** — series *Carici sylvaticae-Fago* y *Epipactido helleborines-Fago*
2. **Hayedos acidófilos cantábricos** — serie *Saxifrago hirsutae-Fago* ← **los más productivos**
3. **Hayedos basófilos pirenaicos** — sin representación en la comarca cantábrica

Es un proxy de **pH y sustrato**. Concuerda con Martínez-Peña 2012, que encuentra
correlación **negativa entre pH del suelo y producción de *B. edulis***: al boleto le
gusta el suelo ácido.

### 2.4. Luminosidad / orientación / topografía

- **Navarra** usa el **hillshade SIG** como segundo parámetro para estimar productividad
  potencial, separando terrenos umbríos y luminosos. Es un método barato, replicable y ya
  validado administrativamente en tu zona exacta.
- **Mumcu Kucuker (2019)**, `10.17474-artvinofd.449736-717479.pdf` — 75 parcelas, Turquía.
  Diferencias significativas por **orientación** y por **pendiente**; **no** por altitud.
  Menor productividad en **orientación norte** (6,5 kg/ha) y en pendientes del **20–30 %**
  (33 kg/ha).
- **Bonet et al. (2010)** — Orientación, pendiente y altitud influyen significativamente.
- **Martínez-Peña et al. (2012)** — **No** encuentra efecto de altitud, pendiente ni
  orientación, pero lo atribuye explícitamente a que sus parcelas eran demasiado homogéneas.

> Aviso: el efecto de la orientación es **dependiente del clima**. En el Mediterráneo seco
> la umbría retiene agua y produce más. En el Cantábrico húmedo el agua no es limitante y
> el signo puede invertirse. Navarra, de hecho, encuentra más producción en hayedo
> acidófilo **luminoso**. No copies el signo de estudios mediterráneos.

### 2.5. Suelo

En Martínez-Peña 2012 las propiedades del suelo **no entraron como predictores
significativos** en los modelos, pero sí correlacionan:

| Propiedad | *Boletus edulis* | *Lactarius* | Total ECM |
|---|---|---|---|
| Capacidad de retención de agua | — | **+** | **+** |
| pH | **−** | — | — |
| Contenido en arena | **+** | **−** | — |
| Contenido en limo | **−** | **+** | — |
| Contenido en arcilla | — | **+** | — |

### 2.6. Índices de vegetación por satélite

Además del NDVI del año anterior (§1.5), **Martínez-Rodrigo et al. (2024)** usan **EVI**
(Enhanced Vegetation Index) y **GNDVI** (Green NDVI) de Landsat como predictores
seleccionados por el modelo. Son datos **gratuitos, espacialmente continuos y
actualizados**, justo lo que a Ontto le hace falta: dan resolución espacial *real* en vez
de asumir homogeneidad dentro de cada rodal.

### 2.7. El aviso de Alday: el espacio importa menos de lo que uno querría

**Alday et al. (2017)** separa las escalas de variación y encuentra algo incómodo para un
proyecto como Ontto:

- La **biomasa de carpóforos** depende sobre todo de la **variación interanual** (tiempo).
- La **riqueza de especies** depende sobre todo de la **escala espacial**.
- La **altitud no fue significativa**.

Es decir: **cuánto sale lo decide el año; dónde sale es más difícil de explicar**. Una app
que prometa precisión espacial fina está prometiendo justo la parte que la literatura
explica peor. Conviene calibrar expectativas: probablemente Ontto acierte mucho mejor con
"esta semana es buena" que con "ve a este rodal concreto".

---

## 3. Ecuaciones publicadas concretas

De Martínez-Peña et al. (2012), *P. sylvestris*, Soria, 18 parcelas, 15 años:

```
Ectomicorrícicos = exp(-2.389 + 0.008·P_otoño + 0.164·T_otoño + 0.664·ln(H_dom) - 0.005·Edad)
                   R² = 0.417   RMSE = 106.0 kg/ha/año

Lactarius        = exp(-3.309 + 0.008·P_otoño + 0.106·T_otoño + 0.653·ln(H_dom) - 0.018·G)
                   R² = 0.261   RMSE = 25.75 kg/ha/año

Boletus edulis   = exp(-14.706 + 0.007·P_otoño + 0.129·T_otoño + 5.049·ln(G) - 0.121·G)
                   R² = 0.222   RMSE = 43.2 kg/ha/año
```

Donde `P_otoño` = precipitación total ago+sep+oct (mm); `T_otoño` = suma de temperaturas
medias sep+oct+nov (°C); `H_dom` = altura dominante (m); `G` = área basimétrica (m²/ha).

### Comparativa de rendimiento de los modelos publicados

| Trabajo | Enfoque | Rendimiento |
|---|---|---|
| Martínez-Peña 2012 | Regresión no lineal, clima + masa | R² = 0,22–0,42 |
| Martínez de Aragón 2007 | Balance hídrico + Tª suelo | R² = 0,66 |
| **Olano 2020** | **Clima + humedad suelo satélite + NDVI año anterior** | **R²adj = 0,629** |
| **Martínez-Rodrigo 2024** | **Redes neuronales; clima + índices satélite + estructura** | **Acierto validación = 0,72** |
| Preprint hayedos 2025 | GLMM diario, 5 días previos | Señal débil; sin R² reportado |

**Nota sobre estos números.** El salto está claro: los modelos que **solo usan lluvia y
temperatura de estación se quedan en R² de 0,2–0,4**; los que **añaden teledetección
(humedad de suelo, NDVI/EVI) suben a 0,6–0,7**. Si Ontto se construye solo con datos de
estaciones meteorológicas, arranca en la banda mala. Esto es probablemente la decisión
técnica más importante del proyecto.

Aun así, conviene interiorizarlo desde ya: Ontto no va a decir "aquí hay hongos". Como
mucho dirá "esta semana la zona A está bastante mejor que la zona B", y eso ya sería
valioso. Y todos esos números son de **producción anual**, el problema fácil; el problema
temporal fino está peor resuelto.

---

## 4. Síntesis: tabla de factores

Leyenda de evidencia: ● fuerte · ◐ moderada · ○ débil o contradictoria

| # | Factor | Capa | Efecto | Evidencia |
|---|---|---|---|---|
| 1 | **Humedad del suelo (satélite)** | Disparo | Positivo. **Iguala o supera a la lluvia** (r=0,63–0,72) | ● |
| 2 | Precipitación acumulada con retardo | Disparo | Positivo, dominante entre los clásicos | ● |
| 3 | Balance hídrico P − ETP | Disparo | Positivo, mejor que P sola (R²=0,66) | ◐ |
| 4 | Temperatura media del aire | Disparo | Unimodal, óptimo ~13 °C | ◐ |
| 5 | Temperatura del suelo (mín. agosto) | Disparo | Positivo | ◐ |
| 6 | Amplitud térmica del suelo | Disparo | Significativo | ○ |
| 7 | Umbral de exclusión T>17,5 °C y lluvia<1 mm | Disparo | Bloqueante | ◐ |
| 8 | **NDVI del año anterior** | Memoria | Positivo (r=0,41–0,60). Ya determinado hoy | ◐ |
| 9 | EVI / GNDVI de la temporada | Mixta | Seleccionados por modelos ML | ◐ |
| 10 | Área basimétrica G | Potencial | Unimodal. Norte de España: 30–40 m²/ha | ● |
| 11 | Altura dominante H_dom | Potencial | Positivo (log) | ● |
| 12 | Edad de la masa | Potencial | Unimodal; hayedo 50–90 años | ● |
| 13 | Especie arbórea hospedante | Potencial | Determinante (simbiosis obligada) | ● |
| 14 | Índice de sitio (calidad de estación) | Potencial | Seleccionado por modelos ML | ◐ |
| 15 | Serie de vegetación / sustrato / pH | Potencial | Acidófilo > basófilo para *Boletus* | ◐ |
| 16 | Luminosidad (hillshade) | Potencial | Significativo; signo según clima | ◐ |
| 17 | Orientación | Potencial | Significativo; signo según clima | ◐ |
| 18 | Pendiente | Potencial | Significativo | ◐ |
| 19 | Altitud | Potencial | **Contradictorio**: no significativo en 3 de 4 estudios | ○ |
| 20 | Textura y retención de agua del suelo | Potencial | Correlaciones claras, no predictor | ○ |
| 21 | Presión recolectora | Corrección | Reduce lo *encontrable*, no lo producido | ○ |

El factor 21 no sale en los modelos porque las parcelas científicas están **valladas**.
Para una app de usuario final es real: en Navarra se estiman ~0,3 recolectores/ha, con
picos en fines de semana y festivos. Un buen recolector local puede llevarse 25 kg de
*Boletus* en un día. **Ontto, si tiene éxito, empeora este factor**: concentra gente donde
predice. Merece pensarse pronto, no al final.

Curiosidad que no encaja en ningún sitio pero apunto por si reaparece: el modelo de redes
neuronales de Martínez-Rodrigo 2024 selecciona la **precipitación de enero** como variable
crítica para *Lactarius*. Recarga hídrica invernal, presumiblemente. Nadie más lo reporta.

---

## 5. Huecos que la literatura no cubre para tu caso

1. **No hay modelo temporal fino calibrado en clima atlántico.** El único trabajo a escala
   diaria en hayedo es el preprint alemán de 2025, en clima centroeuropeo, y su señal es
   débil.
2. **Los modelos españoles están calibrados en pinares mediterráneos/continentales.** Tu
   ámbito es atlántico. Los coeficientes no se trasladan.
3. **Falta *Pinus radiata*.** Es la masa forestal dominante en Gipuzkoa y no aparece en
   ninguno de estos trabajos. Producción micológica probablemente baja y de otras
   especies, pero es un hueco de conocimiento real.
4. **No hay red de parcelas micológicas conocida en Euskadi**, a diferencia de Navarra
   (92 parcelas, 32 en la comarca cantábrica, desde 1997). Sí hay Inventario Forestal de
   la CAE (~4.000 parcelas, HAZI) y Mapa Forestal anual.
5. **Especies de primavera sin cubrir.** *Calocybe gambosa* (perretxiko) es
   probablemente la seta más buscada de Gipuzkoa, fructifica de finales de abril a junio,
   crece en **pastos y prados**, no en bosque, y **no aparece en ninguno de estos
   modelos**. Requiere un modelo aparte.
6. **Toda la literatura mide kg/ha en parcela.** Nadie valida "¿acerté al decir que había
   setas en este monte esta semana?", que es la métrica de Ontto.
7. **Nadie ha modelado la variabilidad espacial fina.** Alday 2017 muestra que la biomasa
   es sobre todo un fenómeno interanual. El "dónde" a escala de rodal sigue siendo el
   agujero grande de este campo — y es justo la mitad de lo que quieres.

---

## 6. Referencias

El detalle completo, con resumen y utilidad de cada trabajo, está en
[literatura científica/00-INDICE.md](../literatura%20científica/00-INDICE.md).
Los 13 PDF están descargados en esa carpeta.

**Los cinco que hay que leer si solo se leen cinco:**

1. `2012_MartinezPena_...` — las ecuaciones de referencia del ámbito español
2. `2020_Olano_...` — la hipótesis de dos pasos y la humedad de suelo por satélite
3. `2025_Preprint_...` — lo más cercano a la escala temporal que Ontto necesita
4. `2018_GobNavarra_..._ANEXOS` — tu zona exacta, con método ya aplicado
5. `2024_MartinezRodrigo_...` — el enfoque ML y las variables que selecciona

### Pendiente de conseguir (de pago)
- **Karavani, A., De Cáceres, M., Martínez de Aragón, J., Bonet, J.A., de-Miguel, S.
  (2018)**. *Effect of climatic and soil moisture conditions on mushroom productivity and
  related ecosystem services in Mediterranean pine stands facing climate change*.
  Agricultural and Forest Meteorology 248:432–440. DOI: 10.1016/j.agrformet.2017.10.024
  → Es el único que no he podido descargar (Elsevier, sin copia en abierto). Importa
  porque es la fuente del **retardo de hasta un mes entre lluvia y humedad de suelo**.
  Se puede pedir a los autores por correo o vía biblioteca universitaria.
- Ágreda et al. (2013). Dinámica estacional del micelio extrarradical de *B. edulis*.
  Mycorrhiza. → interesante para entender la fase subterránea previa a la fructificación.

### Referencia competitiva
- [sporas.io](https://sporas.io/) — "el mapa que predice dónde salen las setas". Conviene
  mirar qué hacen y hasta dónde llegan antes de decidir el alcance de Ontto.
