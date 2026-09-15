# Capa DISPARO — v2

La mitad dinámica de POTENCIAL(x) × DISPARO(t): **cuándo** se dan las condiciones de
fructificación, y a qué cota.

**Fecha:** 2026-09-09
**Datos:** [datos/disparo_diario_1970_2015.csv](../datos/disparo_diario_1970_2015.csv)
**Código:** [scripts/26_capa_disparo.py](../scripts/26_capa_disparo.py)

---

## El modelo

```
DISPARO(t,z) = f_T(T5) × f_W(W5) × f_H(Tmin5) × exclusión
```

| Término | Qué hace | Origen |
|---|---|---|
| `f_T` | Respuesta térmica gaussiana, óptimo **13,2 °C**, σ = 3,5 | Preprint hayedo 2025 |
| `f_W` | Penaliza solo por debajo del **40 % de la capacidad** del suelo | Balance hídrico propio ([05](05-balance-hidrico.md)) |
| `f_H` | Corte por helada: nulo bajo −2 °C de mínima | Preprint: seguimiento *"hasta la primera helada fuerte"* |
| `exclusión` | Cero si T5 > 17,5 °C **y** lluvia5 < 1 mm/día | Preprint hayedo 2025 |

Todo sobre medias móviles de **5 días**, la escala del desarrollo del carpóforo en hayedo
templado según esa misma fuente.

**Espacialización por altitud:**
```
T(t,z) = T_referencia(t) + gradiente(mes) × (z − 164 m)
```
Gradiente medido con **169 estaciones** del Atlas Climático: agosto −0,371 · septiembre
−0,425 · octubre −0,540 · noviembre −0,584 °C/100 m. Referencia = media de 8 estaciones
atlánticas con ≥85 % de datos, altitud media 164 m.

**Solo vertiente atlántica.** Las estaciones del lado del Ebro quedan excluidas: Arcaute
recibe 777 mm/año frente a los 2.454 de Articutza ([05](05-balance-hidrico.md)).

---

## Resultado: la onda que baja del monte

Índice medio por quincena y cota, 1970–2015:

| Quincena | 0 m | 200 m | 400 m | 600 m | 800 m | 1000 m |
|---|---|---|---|---|---|---|
| 1–15 ago | 0,030 | 0,054 | 0,096 | 0,159 | 0,252 | 0,363 |
| 16–31 ago | 0,050 | 0,085 | 0,137 | 0,205 | 0,293 | 0,392 |
| 1–15 sep | 0,086 | 0,154 | 0,248 | 0,368 | 0,503 | **0,625** |
| 16–30 sep | 0,245 | 0,347 | 0,456 | 0,558 | 0,637 | **0,684** |
| 1–15 oct | 0,386 | 0,505 | 0,606 | **0,663** | **0,672** | 0,627 |
| 16–31 oct | 0,509 | 0,585 | **0,629** | **0,633** | 0,581 | 0,486 |
| 1–15 nov | **0,673** | **0,658** | 0,579 | 0,458 | 0,327 | 0,210 |
| 16–30 nov | 0,532 | 0,448 | 0,340 | 0,232 | 0,140 | 0,075 |

**Pico de temporada por cota:**

| Altitud | Pico |
|---|---|
| 1.000 m | **16 de septiembre** |
| 800 m | 13 de octubre |
| 600 m | **14 de octubre** |
| 400 m | 4 de noviembre |
| 200 m | 5 de noviembre |
| 0 m | 5 de noviembre |

**Siete semanas para bajar 1.000 metros.** El hayedo guipuzcoano tiene su mediana en 693 m:
su pico cae a mediados de octubre. El robledal, con mediana en 282 m, a principios de
noviembre.

## Variación interanual

A 600 m, sumando el índice de toda la ventana: **media 50,0 · CV del 21 %**.

Es **el doble de varianza que el agua del suelo** (CV 12 %), lo que confirma que el motor
del *cuándo* aquí es térmico.

| Mejores otoños | Peores otoños |
|---|---|
| 1984 (72) · 1977 (72) · 2015 (69) · 1972 (68) · 2002 (67) | 1991 (32) · 1997 (35) · 1974 (36) · 1999 (37) · 1990 (38) |

Entre el mejor y el peor otoño hay un factor de **2,3**.

---

## v2 — el pulso de lluvia con retardo (factor 2)

**Añadido el 2026-09-09.** La v1 no tenía memoria: reaccionaba a los 5 días previos y punto.
Faltaba el único factor con evidencia ● que estaba completamente ausente.

### El diagnóstico que lo justifica

La pregunta era si el pulso de lluvia tiene varianza, aunque el **nivel** de agua del suelo
no la tenga. Resultado, en la ventana agosto–noviembre:

| Variable | CV |
|---|---|
| Lluvia acumulada en 5 días | **130 %** |
| Lluvia acumulada en 15 días | **88 %** |
| Lluvia acumulada en 30 días | 66 % |
| *Agua del suelo* | *27 %* |

**El nivel está saturado pero el pulso varía enormemente.** Son variables distintas, y en
la v1 las traté como una sola. Gipuzkoa además no llueve constantemente: el 55 % de los días
de la ventana son secos, con **5 rachas de ≥5 días al año** y 1,4 de ≥10 días.

### Y una lectura del preprint que conviene anotar

El preprint de hayedos encontró una señal de precipitación **débil**. Usaba ventanas de 5
días **alineadas a la derecha**, terminando el día de la observación.

Si el disparador es la lluvia de hace dos semanas, una ventana concurrente **no la ve**:
mide la lluvia del día en que el carpóforo ya estaba fuera, no la que lo provocó. Su
resultado puede ser un artefacto de la ventana, no una ausencia de efecto.

### Implementación

```
f_P = 1 − exp( −P_acc / 40 mm )
```

sobre la lluvia acumulada en una **ventana de 15 días que termina 10 días antes** del día
evaluado.

**Justificación del retardo:** la iniciación de primordios requiere el episodio húmedo, y el
desarrollo del carpóforo hasta tamaño recolectable lleva de 5 a 15 días. La literatura
describe desfases de 1 a 4 semanas.

⚠️ **El retardo NO está ajustado con datos.** Es una elección informada, no un parámetro
estimado. El análisis de sensibilidad (retardos de 0 a 28 días) mueve el pico entre el 14 y
el 20 de octubre y el CV interanual entre el 23 % y el 27 %: la forma general es robusta,
el detalle no.

**Por qué no duplica al término hídrico:** el cubo de suelo satura a 74 mm y pierde la
información del episodio; el pulso conserva la magnitud del evento. Uno mide el nivel, el
otro el suceso.

### Qué cambia

| Altitud | Pico v1 | **Pico v2** |
|---|---|---|
| 1.000 m | 16 sep | **2 oct** |
| 800 m | 13 oct | **5 oct** |
| 600 m | 14 oct | **19 oct** |
| 400 m | 4 nov | **19 oct** |
| 200 m | 5 nov | 5 nov |
| 0 m | 5 nov | 6 nov |

**La temporada se concentra.** En la v1 se estiraba de mediados de septiembre a primeros de
noviembre; ahora se comprime en **octubre para toda la franja de 400 a 1.000 m**, que es
donde está el hábitat. Más plausible.

La causa: agosto y septiembre son más secos, y el término de pulso apaga el pico temprano de
las cumbres que la temperatura por sí sola producía.

### Validación interna

**Variación interanual a 600 m: CV del 24 %** (v1: 21 %). El ranking de años cambia
bastante — correlación v1 vs v2 de **0,77**.

Y una comprobación que sale bien: **1985 pasa a ser el peor año de la serie**. Era el único
otoño realmente seco del balance hídrico (40 % de capacidad). En la v1 ni siquiera aparecía
entre los cinco peores. El término de lluvia lo detecta, como debe.

| Mejores otoños (v2) | Peores otoños (v2) |
|---|---|
| 1984 · 1994 · 1996 · 2002 · 1992 | **1985** · 1978 · 1999 · 2013 · 1997 |

1984 sigue siendo el mejor en ambas versiones.

---

## ⚠️ El problema serio de este modelo

**El óptimo de 13,2 °C se estimó donde la temperatura y la fecha están confundidas.**

En Bielefeld, donde se midió, los 13,2 °C ocurren en septiembre–octubre y el otoño se corta
pronto por el frío. Con esos datos **es imposible distinguir** entre:

- *"13,2 °C es la temperatura óptima"*, y
- *"principios de octubre es el momento óptimo"*

Son la misma observación. Y nuestro modelo transporta esa relación a un clima marítimo donde
los 13,2 °C se alcanzan **en noviembre a nivel del mar**. Es justo donde la transferencia es
menos segura.

**Consecuencia práctica:** el pico de principios de noviembre a cotas bajas puede ser un
artefacto. A 600–800 m el modelo da mediados de octubre, que coincide con lo esperable, y ahí
merece más confianza — que es, afortunadamente, donde está el hayedo.

**Qué faltaría para resolverlo:** un término de fenología propia del hongo (fotoperiodo,
acumulación térmica desde el verano, o simplemente una envolvente estacional ajustada con
datos locales). Sin verdad-terreno guipuzcoana no se puede ajustar. Es, otra vez, la
decisión abierta A1.

## Otras limitaciones

1. **Extrapolación en altura.** Las estaciones atlánticas llegan a 402 m; las cotas de 600,
   800 y 1.000 m son extrapolación pura del gradiente. Cuarta vez que este problema
   condiciona un resultado.
2. ~~Sin retardo lluvia→fructificación.~~ **Resuelto en la v2.** ~~El retardo concreto sigue
   sin ajustar con datos.~~ **Respaldado desde fuera (2026-09-15):** Salerni et al. 2023
   encuentra el efecto de la lluvia intensa «sobre todo a partir del décimo día», con el pico
   en el **día 12**, y cita a Salerni et al. 2002, donde el máximo de fructificación cae
   **justo 10 días** después de la lluvia. Nuestro `LAG = 10` coincide.

   Además **da igual el detalle**. Probadas cinco configuraciones de la ventana sobre la
   serie en vivo (600 m, media agosto–septiembre 2026):

   | ventana | días cubiertos | centro | índice medio |
   |---|---|---|---|
   | `VENT=15 LAG=10` (actual) | 10–24 | 17,0 | 0,0008 |
   | `VENT=10 LAG=7` | 7–16 | 11,5 | 0,0007 |
   | `VENT=10 LAG=10` | 10–19 | 14,5 | 0,0007 |
   | `VENT=7 LAG=9` | 9–15 | 12,0 | 0,0007 |
   | `VENT=20 LAG=5` | 5–24 | 14,5 | 0,0008 |

   El resultado es insensible a dónde se ponga la ventana. **Esta deja de ser una debilidad.**
3. **Serie hasta 2015.** Para operar en tiempo real hace falta el puente con AEMET y
   Euskalmet.
4. **Sin validar.** Es coherente con la literatura; no sabemos si acierta.
6. **Sin memoria estacional.** García-Bustamante et al. 2021 encuentra que la lluvia del
   **verano previo** condiciona la producción de todo el otoño, con retardos de *meses*.
   Ontto solo mira 15 días. El balance hídrico arrastra algo de esa memoria por el nivel del
   cubo, pero no hay ningún término explícito de humedad antecedente estacional.

7. **Sin factor de edad del rodal.** El mismo trabajo lo llama pivotal: máximo en la clase
   de 51–70 años, y los pies viejos exigen más humedad que los jóvenes. Es el factor 14, sin
   obtener. Sería abordable con LiDAR.

8. **`f_W` es una rampa y probablemente debería ser una joroba.** García-Bustamante mide
   producción entre el 10 y el 70 % de humedad volumétrica con el **máximo entre el 20 y el
   45 %** — demasiada humedad tampoco favorece. Nuestra `f_W` nunca penaliza por arriba.
   Ojo: humedad volumétrica y «% de la capacidad de agua disponible» no son la misma escala,
   así que el número no se traslada directamente; la **forma** sí es una señal.

5. **La demanda evapotranspirativa entra sólo por la puerta de atrás.** El balance hídrico
   usa ET0 de Hargreaves, pero el modelo concluye que el agua no limita en Gipuzkoa y la
   única penalización por aire seco es la regla de exclusión (T5 > 17,5 °C y lluvia < 1 mm),
   que es un sustituto tosco del déficit de presión de vapor. Ágreda et al. 2015
   (Glob. Chang. Biol. 21(9), DOI 10.1111/gcb.12960), sobre la serie de nueve años de Pinar
   Grande, sostiene justo lo contrario: que **la demanda evapotranspirativa creciente** —no
   la lluvia— es lo que hace caer los rendimientos. Es el trabajo que más puede mover este
   modelo y no lo tenemos. Anotado en
   [literatura científica/00-INDICE.md](../literatura%20cient%C3%ADfica/00-INDICE.md).

---

## Qué predice, para poder contrastarlo

Son afirmaciones falsables con conocimiento local:

- En **Aralar y Aizkorri por encima de 900 m**, la temporada arranca a **mediados de
  septiembre** y está acabada a primeros de noviembre.
- En el **hayedo de 600–800 m**, el pico es la **segunda semana de octubre**.
- En **robledal de fondo de valle**, la temporada es más tardía y se alarga hasta noviembre.
- **1984 y 1977** debieron de ser otoños excepcionales; **1991 y 1997**, malos.
