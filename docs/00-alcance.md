# Ontto — alcance y decisiones

Registro de lo que vamos cerrando. Si una decisión cambia, se edita aquí y se anota por qué.

---

## Qué es Ontto

Una app que estima **cuándo y dónde es probable que hayan fructificado hongos** en
**Gipuzkoa**, a partir de un modelo predictivo alimentado con datos meteorológicos,
geográficos y de composición forestal.

## Decisiones cerradas

### D1 — Especies objetivo: grupo Boletus (MIC1), otoño
*Fecha: 2026-09-06*

*Boletus edulis, B. aereus, B. aestivalis, B. pinophilus.*

**Por qué:** es el grupo con más literatura predictiva, el más buscado por los recolectores,
y coincide con el grupo **MIC1** que el Gobierno de Navarra ya monitoriza oficialmente en su
red de parcelas. Máxima señal disponible y máximo interés de usuario.

**Consecuencias:**
- Hábitat: bosque, sobre todo **hayedo y robledal** (y pinar de silvestre donde lo haya).
- **Corrección 2026-09-06:** los datos medidos de Navarra
  ([03-coeficientes-navarra.md](03-coeficientes-navarra.md)) muestran que el **robledal
  atlántico produce tanto onddo como el mejor hayedo** (4,1 vs 3,9 kg/ha·año). Veníamos
  centrando el trabajo en el hayedo; hay que dar al robledal y al bosque mixto atlántico el
  mismo peso. En Gipuzkoa suman 29.178 ha frente a 19.017 de hayedo.
- Estación: otoño. Ventana de trabajo aproximada **agosto–noviembre**.
- Micorrícico obligado → la **especie arbórea hospedante** es un filtro duro, no un matiz.
- Preferencia por **suelo ácido** (correlación negativa con pH) → el hayedo acidófilo
  cantábrico es el objetivo prioritario.
- Quedan **fuera por ahora**: perretxiko (*Calocybe gambosa*, primavera, pastizal — modelo
  distinto), MIC2 (*Cantharellus*, *Craterellus*, *Hydnum*) y saprótrofos.
  No descartados, aplazados.

### D2 — La app promete: mapa de potencial + índice temporal
*Fecha: 2026-09-06*

Arquitectura **POTENCIAL(x) × DISPARO(t)**:

```
Probabilidad(hongos aquí, ahora)  ≈  POTENCIAL(x)  ×  DISPARO(t)
                                     └─ estático ─┘   └─ dinámico ─┘
```

- Un **mapa de potencial micológico** relativamente estático, derivado de masa forestal,
  sustrato, estructura y topografía. Se recalcula en años, no en días.
- Un **índice temporal** que "enciende" ese mapa según las condiciones recientes.

**Por qué no más:** [Alday et al. 2017](../literatura%20científica/2017_Alday_Escalas-espacio-temporales-de-biomasa-fungica.pdf)
demuestra que la biomasa de carpóforos es sobre todo un fenómeno **interanual**, no
espacial. Prometer "hoy hay setas en este rodal concreto" sería prometer justo la parte que
la ciencia explica peor.

**Por qué no menos:** un simple índice comarcal semanal es defendible pero no aporta el
"dónde", que es la mitad del valor para el usuario.

**Consecuencia honesta que hay que asumir:** el producto dirá *"esta semana esta zona está
bastante mejor que aquella"*, no *"aquí hay setas"*. El copy de la app tendrá que reflejarlo.

### D3 — Ámbito acotado a Gipuzkoa
*Fecha: 2026-09-06. Sustituye al ámbito inicial "Gipuzkoa y Norte de Navarra".*

**Por qué:** una sola administración, una sola infraestructura de datos, un solo criterio
cartográfico. Elimina el trabajo de reconciliar dos fuentes distintas antes siquiera de
saber si el modelo funciona.

**Lo que ganamos:**
- Todo el dato base sale de **geoEuskadi / Open Data Euskadi**, con licencia CC BY,
  actualización **anual** y metodología homogénea.
- Meteorología: **Euskalmet**, una sola red.
- No hay que armonizar leyendas, escalas ni sistemas de clasificación entre territorios.

**Dos consecuencias que hay que tener presentes, no son menores:**

1. **La mejor serie de datos de la región se queda fuera del ámbito.** Las 92 parcelas
   micológicas de Navarra (32 en la comarca cantábrica, 60 específicas de hayedo, serie
   desde 1997) quedan ahora en territorio externo. **Esto no significa que haya que
   tirarlas.** Los hayedos del Norte de Navarra y los de Gipuzkoa son ecológicamente los
   mismos bosques; esa serie sigue siendo, con diferencia, el mejor material de
   calibración disponible. Acotar el **producto** a Gipuzkoa no obliga a acotar la
   **calibración** a Gipuzkoa.

2. **Cambia la composición forestal del ámbito.** Gipuzkoa tiene mucha más plantación de
   ***Pinus radiata*** y proporcionalmente menos hayedo y robledal que la comarca
   cantábrica navarra. Y *P. radiata* es precisamente el hueco de literatura señalado en
   [01-factores-fructificacion.md](01-factores-fructificacion.md) §5: **no hay ni un solo
   trabajo de los revisados que lo estudie**.

   → Pregunta abierta y urgente: **¿qué porcentaje de la superficie forestal de Gipuzkoa
   es siquiera hábitat candidato para el grupo MIC1?** Si resulta que la mayor parte es
   radiata, el mapa de potencial puede quedarse en unas pocas manchas de hayedo y
   robledal. Es una pregunta que hay que responder pronto, y se responde con el Mapa
   Forestal — que es justo el factor que estamos inventariando ahora.

---

## Decisiones abiertas

### A1 — De dónde salen los datos de validación *(bloqueante, pero reducido)*
No tenemos verdad-terreno para Gipuzkoa. Sin ella no se puede validar nada.

**Reducido el 2026-09-06.** Los coeficientes de producción medidos en Navarra
([03-coeficientes-navarra.md](03-coeficientes-navarra.md)) permiten construir la capa
POTENCIAL sin pedir nada a nadie. Lo que sigue faltando es:
- Calibrar la capa **DISPARO** (el *cuándo*)
- **Validar** que Ontto acierta

Es decir, A1 ya no bloquea el mapa, solo el modelo temporal y la verificación.

### A2 — ¿Solo estaciones meteorológicas o también teledetección?
La literatura es contundente: solo estaciones → R² 0,2–0,4; añadiendo humedad de suelo y
NDVI por satélite → 0,6–0,7. Afecta a toda la arquitectura técnica.

**Parcialmente resuelta (factor 1).** La humedad del suelo por satélite existe, es gratis
y cubre Gipuzkoa, pero con 0,25° de resolución solo sirve como índice regional, y en clima
atlántico su variación interanual es pequeña (4,3 %). La vía correcta es un **balance
hídrico propio**, que depende de los bloques 3 y 4. Queda por evaluar NDVI (factores 8-9).

### A5 — Datos en tiempo real para el despliegue
ESA CCI va con año y medio de retraso: sirve para entrenar, no para funcionar. Habrá que
resolver el producto NRT equivalente **antes** de desplegar, no durante.

### A3 — Plataforma
Móvil, web, o web-primero. Sin decidir. No urge.

### A4 — Qué hacer con la presión recolectora
Si Ontto funciona, concentra gente donde predice. Es un problema de diseño, no solo ético.
Navarra estima ~0,3 recolectores/ha.

---

## Estado del proyecto

| Paso | Estado |
|---|---|
| 1. Identificar factores en la literatura | ✅ Hecho — [01-factores-fructificacion.md](01-factores-fructificacion.md) |
| 2. Inventario de fuentes de datos disponibles | 🟡 En curso — 10 de 21 factores · [02-datos.md](02-datos.md) |
| 2-bis. Coeficientes transferibles de Navarra | ✅ Hecho — [03-coeficientes-navarra.md](03-coeficientes-navarra.md) |
| 3. Datos de validación | ⬜ Ya no bloquea el mapa; sí el modelo temporal |
| **4. Capa POTENCIAL (SIG)** | ✅ **v1 construida** — [04-capa-potencial.md](04-capa-potencial.md) · 184.345 kg/año |
| 5. Capa DISPARO (serie temporal) | ✅ **v1 construida** — [06-capa-disparo.md](06-capa-disparo.md) |
| 6. Modelo y validación | ⬜ |
| 7. App | ⬜ |
