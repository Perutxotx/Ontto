# Capa POTENCIAL — v1

**Primer entregable de Ontto.** La mitad estática de la ecuación
POTENCIAL(x) × DISPARO(t): cuánto produciría cada monte de Gipuzkoa en un año medio.

**Fecha:** 2026-09-06
**Mapa:** https://claude.ai/code/artifact/f2db98bc-fb26-48b3-8f15-36c737bd5611
**Datos:** [datos/potencial_mic1.csv](../datos/potencial_mic1.csv) ·
**Código:** [scripts/20_capa_potencial.py](../scripts/20_capa_potencial.py)

---

## Resultado

| | |
|---|---|
| **Producción potencial** | **184.345 kg/año** de grupo MIC1 (*Boletus* spp.) |
| Superficie con coeficiente | 50.219 ha de 122.219 arboladas (41 %) |
| Media ponderada | 3,67 kg/ha·año |
| Masas caracterizadas | 59.133 |

| Clase | ha | kg/ha·año | kg/año | % del total |
|---|---|---|---|---|
| Robledal · ácido · sombrío | 19.170 | 4,40 | 84.348 | 45,8 |
| Hayedo · ácido · sombrío | 13.240 | 2,62 | 34.689 | 18,8 |
| Robledal · incierto · sombrío | 7.667 | 4,40 | 33.734 | 18,3 |
| Robledal · ácido · luminoso | 2.790 | 4,40 | 12.275 | 6,7 |
| Robledal · azonal · sombrío | 1.751 | 4,40 | 7.706 | 4,2 |
| Hayedo · ácido · luminoso | 1.187 | 5,16 | 6.123 | 3,3 |
| Robledal · incierto · luminoso | 862 | 4,40 | 3.791 | 2,1 |
| Hayedo · basófilo · luminoso | 441 | 1,54 | 679 | 0,4 |
| Hayedo · basófilo · sombrío | 3.014 | 0,19 | 573 | 0,3 |

**El 74 % de la producción estimada sale de robledal y bosque mixto**, no de hayedo. Es la
consecuencia directa del hallazgo de [03-coeficientes-navarra.md](03-coeficientes-navarra.md):
el robledal atlántico produce 4,1 kg/ha frente a los 3,9 del mejor hayedo.

**Contraste con Navarra:** su comarca cantábrica rinde 2,54 kg/ha; Gipuzkoa sale a 3,67, un
44 % más. Razones identificables: más sustrato ácido (76 % frente a 64 %) y
proporcionalmente mucho más robledal.

---

## Cómo se construye

```
especie arbórea  ──┐
   (Mapa Forestal) │
                   ├──> grupo Navarra (hayedo / robledal / sin dato)
serie vegetación ──┤
   (1:50.000)      ├──> sustrato (ácido / básico / incierto / azonal)
                   │
FCCARB ────────────┴──> luminosidad (< 60 % = luminoso)
                                │
                                ▼
                     coeficiente kg/ha·año  ×  superficie
```

### Decisiones tomadas y por qué

**Umbral de luminosidad: FCCARB < 60 %.** Elegido "estricto" por decisión del usuario. Da el
10,1 % del hayedo guipuzcoano como luminoso, frente al 6,8 % que resultó en Navarra. Es lo
más cercano sin forzar.

⚠️ **Es la decisión más sensible de toda la capa.** Navarra midió la luminosidad en campo
mediante cobertura de vegetación heliófila del sotobosque; nosotros usamos cabida cubierta
arbórea. Son variables emparentadas pero no idénticas, y el umbral multiplica por 2 la
producción del hayedo acidófilo (5,16 vs 2,62). Merece un análisis de sensibilidad.

**El umbral no tiene suelo, y da igual.** Centenaro et al. 2024 (STOTEN 909:168628) mide
tres cortas a hecho en pinar de Soria ocho años después: la biomasa fúngica del suelo cae a
un tercio dentro de la corta (1,7 frente a 4,2–5,1 mg/g) y no se ha recuperado. Es decir, el
"más abierto, más produce" no es monótono — pasado cierto punto, quitar el dosel quita el
micelio. Nuestro umbral es binario y no tiene suelo: un rodal con FCCARB del 5 % cobraría el
coeficiente alto igual que uno del 55 %.

Comprobado sobre el mapa publicado (4.410 rodales, 40.773 ha):

| FCCARB | rodales | ha | % del total kg |
|---|---|---|---|
| 0–10 % | 14 | 52 | 0,2 % |
| 10–20 % | 0 | 0 | 0 % |
| 20–40 % | 300 | 1.851 | 5,8 % |
| 40–60 % | 219 | 1.730 | 4,8 % |
| 60–100 % | 3.877 | 37.140 | 89,3 % |

No hay ningún rodal con cabida 0 y solo 52 ha por debajo del 10 %. **El mapa no contiene
cortas a hecho**, así que el sesgo existe pero es inmaterial. Si algún año el Mapa Forestal
trae masas recién cortadas, habría que poner un suelo al umbral (p. ej. FCCARB ≥ 20 %).

**El suelo no discrimina a escala fina.** El mismo trabajo mide materia orgánica, N, P y pH
en el gradiente: no difieren entre zonas y **no explican nada** de la composición fúngica —
la variabilidad dentro de cada zona supera a la de entre zonas. Coincide con lo que nos
pasó con TWI, textura y pendiente, y respalda no bajar el modelo de suelo por debajo del
rodal. No afecta al corte ácido/básico, que es un contraste de otra escala: allí el pH va de
4 a 8, aquí todo el gradiente estaba entre 3,4 y 5,95.

**Y una fuente que va al revés.** El TFG de Escribano (2018), que hace esta misma capa para
la Comarca de Pinares, valora la cubierta arbórea en sentido opuesto: 70–100 % de cubierta
= potencialidad muy alta, 0–50 % = media. Es pinar mediterráneo —donde el dosel protege de
la evaporación— y su valoración es criterio experto, no medida, mientras la nuestra sale de
60 parcelas navarras de hayedo. No lo da por malo, pero refuerza que el umbral de
luminosidad necesita el análisis de sensibilidad que sigue pendiente.

**Robledal sin desglosar.** Navarra da un único valor (4,40) para el robledal atlántico, sin
separar por sustrato ni luminosidad. Se aplica plano. Modular con los ratios del hayedo
habría extrapolado hasta ~8-12 kg/ha, muy por encima de lo observado.

**Bosque mixto atlántico → coeficiente de robledal.** 19.062 ha aportando el 20 % del total
estimado. Justificación: masas dominadas por robles, avellanos y abedules, todos
hospedantes ectomicorrícicos. **Es la asunción más gruesa de la capa** y no está medida.

**Sin coeficiente, deliberadamente:** 72.000 ha. Se marcan como tales en vez de asignarles
un número inventado.

| Especie | ha sin coeficiente |
|---|---|
| Pino radiata | 32.340 |
| Pino laricio | 6.957 |
| Alerce | 6.278 |
| Abeto Douglas | 5.490 |
| Criptomeria | 2.736 |
| Pino pinaster | 2.573 |
| Encina | 2.369 |
| Secuoya | 2.324 |

Las cupresáceas (criptomeria, secuoya, chamaeciparis) no forman ectomicorrizas: ahí el cero
es real, no una laguna. Para los pinos y el alerce sí es laguna de conocimiento. La encina
está sobre sustrato básico y Navarra no la midió.

---

## Limitaciones que hay que repetir cada vez que se enseñe este mapa

1. **No dice dónde hay setas hoy.** Dice qué produciría cada monte en un año medio. Falta
   multiplicar por el DISPARO.
2. **Los coeficientes son prestados**, de 60 parcelas navarras 2005–2010. De nuestro bosque,
   nuestra especie y nuestro clima, pero no medidos en Gipuzkoa.
3. **No está validada.** Sigue sin haber verdad-terreno guipuzcoana (decisión abierta A1).
4. **Las series de vegetación son 1:50.000**, más gruesas que el Mapa Forestal (1:10.000).
   La asignación de sustrato hereda esa imprecisión.
5. **17.830 ha de sustrato "incierto"** — toda la serie de bosque mixto atlántico, cuya
   reacción varía. Resoluble cruzando con el mapa litológico, ya descargado.

---

## Siguiente

- **Balance hídrico** → puerta de entrada a la capa DISPARO. Ya tenemos ET0 y precipitación
  del Atlas Climático, y los mapas de textura del suelo (arcilla, arena, limo) localizados
  en geoEuskadi, que resuelven el factor 20.
- **Análisis de sensibilidad al umbral de luminosidad.** Sigue pendiente; lo que sí está
  comprobado es que el umbral no se rompe por abajo (ver arriba).
- **Resolver el sustrato "incierto"** con el mapa litológico.
- **Factores 10, 11, 14** (área basimétrica, altura dominante, índice de sitio) vía LiDAR:
  mejorarían la capa, no la bloquean.
