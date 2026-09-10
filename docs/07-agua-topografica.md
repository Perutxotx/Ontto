# Ríos, vaguadas y aire frío

**Origen:** pregunta directa — *¿los cauces y riachuelos afectan a la humedad del suelo y,
por ahí, a la fructificación? ¿Podemos incluirlo?*

**Fecha:** 2026-09-10
**Datos:** [datos/masas_twi.csv](../datos/masas_twi.csv) ·
**Código:** [scripts/29](../scripts/29_indice_topografico_humedad.py), [30](../scripts/30_twi_por_masa.py)

---

## El hueco era real

El balance hídrico de [05](05-balance-hidrico.md) es **unidimensional**: entra lluvia, sale
evapotranspiración. Ignora que el agua corre cuesta abajo y se acumula. En un territorio tan
quebrado como Gipuzkoa eso no es un detalle.

Y los cauces provocan **dos** efectos, no uno:

1. **Agua acumulada** — las vaguadas reciben el drenaje de toda la ladera de encima
2. **Aire frío embalsado** — el aire denso baja de noche y se estanca en el fondo

El segundo no lo había considerado, y afecta a un modelo que es principalmente térmico.

---

## Efecto 1 · Agua: el índice topográfico de humedad

```
TWI = ln( a / tan β )
```
`a` = área de drenaje acumulada por unidad de anchura · `β` = pendiente local.

Calculado del MDT LiDAR a **50 m**: relleno de depresiones por *priority-flood*, direcciones
de flujo D8 y acumulación procesando de mayor a menor cota.

**Distribución en Gipuzkoa:** mín 2,6 · p5 4,5 · mediana 6,0 · p95 10,8 · máx 19,1.
El **12,4 %** del territorio supera 10 — las vaguadas.

### Valida perfectamente en los extremos

| Especie | TWI |
|---|---|
| **Árboles ripícolas** | **10,13** |
| **Aliso** | **8,37** |
| Bosque mixto atlántico | 6,71 |
| Roble pedunculado | 6,41 |
| Haya | 6,26 |
| Pino radiata | 5,97 |
| **Encina** | **5,75** |

Ripícolas y aliso arriba; encina —roquedo calizo— abajo. El cálculo es correcto.

### Pero no discrimina donde importa

Entre haya (6,26), radiata (5,97) y roble pedunculado (6,41) hay **medio punto**.

Es la **tercera vez** que ocurre lo mismo, y ya es un patrón del territorio:

| Variable | Extremos | Matriz forestal |
|---|---|---|
| Pendiente ([02](02-datos.md)) | Ripícolas 14,6° vs encina 28,9° | Todo entre 42 y 47 % |
| Textura del suelo ([05](05-balance-hidrico.md)) | Pinaster 63 mm | CV del 5,8 % |
| **TWI** | Ripícolas 10,1 vs encina 5,8 | Todo entre 5,9 y 6,7 |

Gipuzkoa es homogénea en casi todo salvo en la especie arbórea y la altitud.

### El hallazgo que sí importa

Restringiendo a los 1.619 rodales de haya, robledal y mixto de más de 5 ha:

```
Variación ENTRE rodales   σ = 0,94
Variación DENTRO del rodal σ = 1,74
                            ─────
                     razón   1,9×
```

> **La variación dentro de un rodal es el doble que la variación entre rodales.**

Un rodal típico tiene TWI medio 6,5 y contiene celdas de **3,0 a 10,0**: de loma seca a
vaguada encharcada, dentro de la misma mancha.

**Esto dice algo sobre el proyecto entero, no sobre esta variable.** Todo el modelo trabaja
a escala de rodal —9 ha de media— pero **el recolector trabaja a escala de diez metros**.
Va a la regata concreta, a la vaguada umbría, no a la media del rodal.

El TWI es la primera variable donde la información interesante vive **por debajo** de nuestra
resolución. Y es computable: la tenemos a 50 m, y el MDT permite bajar a 5 m.

### Y sobre el signo, una advertencia

La intuición dice "más agua, más setas". Aquí probablemente sea al revés:

1. **El agua no limita** ([05](05-balance-hidrico.md)): suelo al 68–90 % de capacidad de
   septiembre a noviembre. Más agua no aporta.
2. **Martínez-Peña 2012**: la arena correlaciona **positivamente** con *B. edulis* y el limo
   **negativamente**. Al boleto le gusta suelo grueso y drenante, no encharcado.
3. **El fondo encharcado es otro bosque**: aliseda y fresneda, con sus propios hongos
   ectomicorrícicos (*Alnicola*, *Lactarius obscuratus*), no boletos.

Hipótesis razonable: **el TWI actúa como modulador de sequía, no como bonificación.** En una
racha seca las vaguadas serían lo único activo; en un otoño normal, penalizan.

---

## Efecto 2 · Aire frío embalsado

En noches despejadas y en calma el aire frío baja por las laderas y se estanca en el fondo,
**invirtiendo el gradiente térmico**. La literatura confirma que ocurre también en otoño.

Nuestro modelo asume que la temperatura baja monótonamente con la altura. Si los fondos están
más fríos de lo que el gradiente predice, el modelo se equivoca **justo donde vive el
robledal** (mediana 282 m).

### La firma está en los datos

Gradiente vertical de la máxima frente al de la mínima, vertiente atlántica:

| Mes | Tmáx | Tmín | Diferencia |
|---|---|---|---|
| Agosto | −0,252 | −0,585 | −0,33 |
| Septiembre | −0,360 | −0,536 | −0,18 |
| **Octubre** | −0,668 | **−0,553** | **+0,11** |
| **Noviembre** | −0,720 | **−0,541** | **+0,18** |

En octubre y noviembre la mínima tiene el gradiente **más plano** que la máxima: firma de
embalsamiento.

Y la prueba directa, separando por amplitud térmica diaria (proxy de cielo despejado):

```
Noches despejadas   Tmín: −0,437 °C/100 m
Noches cubiertas    Tmín: −0,634 °C/100 m
```

**0,20 °C/100 m de aplanamiento en noches despejadas**, que es cuando se forma la inversión.
La física se comporta como debe.

### Pero no podemos calibrar la magnitud

El efecto medido es modesto —0,11 a 0,20 °C/100 m— y sé por qué: **ninguna estación está en
un fondo de valle encajonado**. Están en aeropuertos, pueblos y embalses. La que mediría un
embalsamiento fuerte, el fondo de una regata angosta, no existe.

Estamos detectando el fenómeno con la señal diluida. Una corrección basada en esto sería
correcta en el signo y arbitraria en la magnitud.

**Conexión con un problema conocido:** el modelo da un pico raro a nivel del mar en noviembre
([06](06-capa-disparo.md)). Si los fondos están más fríos de lo que el gradiente predice, ese
pico sería menor y más temprano. El embalsamiento podría explicar parte del artefacto.

---

## Qué se hace con esto

**No añadir el TWI como variable de rodal.** Aportaría casi nada (σ 0,94 entre rodales) y
está correlacionado con la especie, que ya está en el modelo. Sería el cuarto factor
calculado y sin usar.

**Sí guardar el TWI**, ya calculado para las 59.133 masas, porque es la llave de otra cosa:

> **Resolución sub-rodal.** No *"¿a qué monte voy?"* sino *"dentro de este monte, ¿a qué
> parte?"*. Es lo que un recolector realmente necesita, y es la primera vez que tenemos una
> variable capaz de responderlo.

**El aire frío queda anotado**, con signo confirmado y magnitud sin calibrar. No lo meto en
el modelo: prefiero un artefacto conocido a una corrección inventada.

### Lo que desbloquearía ambas cosas

Las dos vías —sub-rodal y aire frío— piden lo mismo que todo lo demás: **datos de dónde
salen realmente los onddos**. Con unos cientos de puntos GPS se podría comprobar si caen en
las vaguadas o en las lomas, y si los fondos van con retraso respecto a las laderas.

Es la decisión abierta A1, otra vez.
