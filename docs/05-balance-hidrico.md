# Balance hídrico — y el hallazgo que reorienta la capa DISPARO

**Fecha:** 2026-09-06
**Datos:** [datos/balance_hidrico_atlantico_1970_2015.csv](../datos/balance_hidrico_atlantico_1970_2015.csv) ·
[datos/masas_suelo.csv](../datos/masas_suelo.csv)
**Código:** [scripts/21](../scripts/21_pedotransferencia.py) a
[scripts/25](../scripts/25_seleccion_estaciones.py)

---

## El resultado principal

> **En la vertiente atlántica de Gipuzkoa, el agua del suelo prácticamente nunca es
> limitante durante la ventana de fructificación.**

Contenido de agua del suelo, media de 8 estaciones atlánticas, 1970–2015, sobre una
capacidad de 74 mm:

| Mes | Media | % de capacidad | Días bajo el 30 % |
|---|---|---|---|
| Julio | 39,8 mm | 54 % | 11 % |
| Agosto | 42,9 mm | 58 % | 7 % |
| Septiembre | 50,2 mm | 68 % | 1 % |
| Octubre | 61,0 mm | 82 % | 1 % |
| Noviembre | 66,9 mm | 90 % | 0 % |

En toda la ventana agosto–noviembre, **solo el 2,3 % de los días** tienen el suelo por
debajo del 30 % de su capacidad, y el 0,6 % por debajo del 20 %.

**Variación interanual de la media septiembre–octubre: CV del 12 %.** En 46 años solo un
otoño fue realmente seco — **1985, con el 40 % de capacidad**. El siguiente peor, 2014, ya
estaba al 58 %.

### ⚠️ Corrección de 2026-09-15: esa conclusión es climatológica, y 2026 la rompe

Lo de arriba vale para **1970–2015**. Comprobado el balance en vivo contra el histórico,
misma AWC (74 mm), misma ET0 de Hargreaves y mismo cubo:

| Mes | 1970–2015 | **2026** |
|---|---|---|
| Julio | 56 % de capacidad | **21 %** |
| Agosto | 57 % | **24 %** |
| Septiembre | 67 % | **21 %** |

Septiembre de 2026 va por **15,4 mm**. El mínimo de los 46 años del registro fue 1985 con
29 mm, y el percentil 5 está en 38 mm. Es decir: **2026 está por debajo de todo lo
observado en el histórico**, casi a la mitad del peor año.

Descartado el artefacto de arranque: el cubo se inicializa el 13 de abril y se probó con
40, 60, 80 y 100 % de AWC — **los cuatro convergen al mismo valor**, 13,4 mm el último día.
La condición inicial se ha olvidado por completo. Las dos series no se construyen igual (el
histórico promedia cubos por estación, el vivo corre un cubo sobre la lluvia promediada), y
esa diferencia favorece que el vivo salga *más húmedo*, no más seco: la brecha es un suelo,
no un techo.

**Consecuencia para el modelo.** El término `f_W = clip(W5 / (0,40·AWC), 0, 1)` es
prácticamente **código muerto en el histórico** — vale exactamente 1 el 97,7 % de los días
de otoño. En 2026 está activo el **100 % de los días** de julio, agosto y septiembre, y a
6 de septiembre vale **0,45**: por sí solo recorta el índice a menos de la mitad.

Un término que nunca se activó en 46 años de calibración está hoy decidiendo el resultado,
y su único parámetro —el umbral del 40 % de AWC— **se eligió, no se ajustó**. Nadie ha
comprobado nunca si la penalización tiene la forma correcta, porque hasta ahora no hacía
falta. Es la debilidad más urgente del modelo, por delante de las tres ya conocidas.

Aquí es donde entra **Ágreda et al. 2015** (Glob. Chang. Biol. 21(9), DOI 10.1111/gcb.12960):
sostiene que lo limitante es la **demanda evapotranspirativa**, no la lluvia. Comprobada la
tendencia en nuestra propia serie 1970–2015, la ET0 **no sube** de forma detectable
(otoño −0,8 % en 46 años, r = −0,04; verano +3,1 %, r = +0,15; ninguna significativa). Así
que el problema de 2026 **no es una tendencia climática en la demanda** — es un déficit de
lluvia puntual y extremo. Pero sigue haciendo falta el artículo para saber con qué forma
funcional penalizar, que es justo lo que no sabemos.

---

### Por qué esto reorienta el proyecto

Toda la literatura de referencia sitúa la **precipitación como predictor dominante**:

- Martínez-Peña 2012: `P_otoño` significativa en los tres modelos
- Karavani 2018: *"la precipitación es el predictor más significativo"*
- Olano 2020: humedad de suelo r = 0,63–0,72
- Alday 2017: *"la precipitación es el recurso limitante"*

Y todos esos trabajos son **mediterráneos o continentales**, donde el verano seco es severo
y la variación interanual enorme. Ahí la lluvia explica mucho porque hay mucho que explicar.

**En Gipuzkoa esa varianza no existe.** El suelo está entre el 68 % y el 90 % de capacidad
de septiembre a noviembre, todos los años. Una variable sin varianza no puede explicar nada.

> **Consecuencia: la capa DISPARO de Ontto debe ser principalmente térmica, no hídrica.**

Lo cual concuerda con el único trabajo en hayedo atlántico-europeo
([preprint 2025](../literatura%20científica/2025_Preprint_Disparadores-meteorologicos-diarios-Boletus-en-hayedo.pdf)),
que concluye literalmente que *"la temperatura impone una restricción más fuerte sobre la
fructificación que la precipitación a corto plazo"*, y con la banda del óptimo térmico
descendente que medimos en [02-datos.md](02-datos.md).

El agua no desaparece del modelo —hará falta detectar los años y episodios excepcionales,
como 1985— pero pasa de protagonista a variable de excepción.

---

## Cómo se ha calculado

### Factor 20 · Capacidad de agua del suelo

**Fuente:** geoEuskadi, `Medio_Ambiente/CarbonoOrganico_Texturas_Suelos/` — rásteres de
arcilla, arena y limo a **10 m**, ETRS89 UTM30N. Remuestreados a 50 m por media de bloques.

**Pedotransferencia:** Saxton & Rawls (2006). Capacidad de campo (33 kPa) menos punto de
marchitez (1500 kPa), por 50 cm de espesor.

Comprobación con texturas de referencia:

| Textura | Agua disponible en 50 cm |
|---|---|
| Arenosa | 29 mm |
| Franco-arenosa | 49 mm |
| Arcillosa | 62 mm |
| Franca | 71 mm |
| Franco-limosa | 98 mm |

**Resultado en Gipuzkoa:** mediana 74 mm, p5 68, p95 80. **Coeficiente de variación 5,8 %.**

El suelo guipuzcoano es homogéneo: franco-arcillo-limoso, coherente con el flysch. Como la
pendiente, **no discrimina en el espacio**. Única excepción: el *pino pinaster*, con 44 % de
arena y 63 mm — se planta en los suelos arenosos y pobres.

⚠️ **Nota ecológica que hay que tener presente.** El suelo que más agua retiene es el
franco-limoso (98 mm), pero Martínez-Peña 2012 encuentra que el **limo correlaciona
negativamente** con *B. edulis* y la **arena positivamente**. Al boleto no le gusta el suelo
que más almacena: prefiere suelo grueso y drenante, que se moja y se seca rápido. La textura
debe entrar en el modelo **por su cuenta**, no solo a través de la capacidad de retención.

### Modelo de balance

Cubo simple, paso diario:

```
w(t) = min( AWC , w(t-1) + P(t) )
k    = w(t) / AWC                    reducción por sequedad
ETa  = min( w(t) , ET0(t) · k )
w(t) = max( 0 , w(t) - ETa )
```

**ET0 por Hargreaves-Samani (FAO-56)**, a partir de temperatura máxima, mínima y radiación
extraterrestre a 43,1° N. Es la misma familia de método que usa Ur Agentzia en el Atlas.

ET0 media diaria obtenida: julio 4,33 · agosto 3,88 · septiembre 2,96 · octubre 1,80 ·
noviembre 0,99 mm/día. Descenso otoñal correcto.

### Estaciones

De las 197 del Atlas en el entorno de Gipuzkoa, **11 tienen ≥85 % de datos** de
precipitación y temperaturas en agosto–noviembre.

---

## El artefacto que estuvo a punto de colarse

El primer cálculo dio un gradiente de **−3,20 mm de agua por cada 100 m de altitud**
(r = −0,73): a más altura, menos agua. Contraintuitivo.

La causa: **las tres estaciones altas están al otro lado de la divisoria de aguas.**

| Estación | m | mm/año | Vertiente |
|---|---|---|---|
| Articutza | 305 | **2.454** | Atlántica |
| Añarbe | 120 | 2.066 | Atlántica |
| Legazpia | 402 | 1.466 | Atlántica |
| Goñi | 865 | 1.388 | Mediterránea |
| Alsasua | 525 | 1.228 | Mediterránea |
| **Arcaute (Vitoria)** | 515 | **777** | Mediterránea |

Articutza recibe **tres veces más lluvia que Vitoria**. El supuesto gradiente altitudinal era
el salto climático de Aizkorri y Aralar.

Separando vertientes: atlántica 42,9 mm en agosto frente a 22,6 de la mediterránea. Y dentro
de la atlántica sola, el gradiente con la altitud es **−1,75 mm/100 m con r = −0,31: no
significativo**.

**Lección:** en Gipuzkoa nunca se puede mezclar estaciones de las dos vertientes. Es un
territorio pequeño con dos climas, y la divisoria pasa justo por donde está nuestro hábitat.

---

## Limitaciones

1. **Sigue el problema de la cota.** Las estaciones atlánticas con datos completos llegan a
   402 m. El hayedo tiene su mediana en 693 m. No podemos medir el balance hídrico donde
   más nos importa; lo estamos extrapolando.
2. **El modelo de cubo es simple.** Sin intercepción por el dosel, sin percolación profunda,
   sin variación de la profundidad radicular por especie. Para una primera aproximación es
   razonable, pero medfate haría esto mucho mejor.
3. **AWC fijo en 74 mm.** Es la mediana de Gipuzkoa y el CV es del 5,8 %, así que el error
   por usar un valor único es pequeño.
4. **La serie acaba en 2015**, como el Atlas. Para operar en tiempo real hará falta el
   puente con AEMET y Euskalmet.

---

## Qué se lleva la capa DISPARO de aquí

| Variable | Papel |
|---|---|
| **Temperatura** | **Protagonista.** Óptimo 13,2 °C, exclusión >17,5 °C, banda descendente |
| Agua del suelo | Variable de excepción — detectar los años tipo 1985 |
| ET0 | Insumo del balance, no predictor directo |
| Textura (arena / limo) | Covariable espacial propia, no vía capacidad de retención |
