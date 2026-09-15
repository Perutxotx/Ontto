# Validación — la primera evidencia de que Ontto acierta

**Fecha:** 2026-09-16
**Código:** [scripts/31_validacion_gbif.py](../scripts/31_validacion_gbif.py)
**Datos:** GBIF — herbario ARAN (Aranzadi), iNaturalist, MA, VIT

---

## El problema que esto resuelve a medias

La decisión **A1** lleva abierta desde el primer día: no existe producción de onddo medida
en kg en Gipuzkoa con la que comprobar si el modelo acierta. Sin eso, Ontto era coherente
con la literatura y nada más.

Pero hay un dato que sí existe y que no habíamos mirado: **registros de fructificación con
fecha exacta y coordenadas.** GBIF agrega el herbario **ARAN de Aranzadi** (117 registros),
iNaturalist (39) y varios herbarios más. No dicen cuántos kilos hubo. Dicen **qué día
alguien encontró un onddo, y dónde**. Para validar la capa DISPARO —que es la mitad que
cambia a diario y la que enseña la app— eso basta.

## La prueba

331 registros del grupo *Boletus* (*edulis*, *aereus*, *pinophilus*, *reticulatus*) en la
caja de Gipuzkoa, 1977–2026, **todos con día exacto**. De ellos, **132 caen dentro de
Gipuzkoa o de los 15 km atlánticos de alrededor** (Artikutza, Leitza, Bera) y dentro del
periodo que cubre nuestro índice histórico, 1970–2015.

Dos controles, ambos imprescindibles:

**1. Comparar solo contra el mismo mes y la misma cota.** La gente sale al monte en otoño.
Comparar los días con hallazgo contra *todos* los días del año validaría la envolvente
estacional por pura construcción. Cada hallazgo se compara únicamente con los demás días
**de su mismo mes y a su misma cota**. Lo que se mide así es la parte meteorológica.

**2. Mirar los días previos, no el día del hallazgo.** Un carpóforo encontrado el día X
emergió varios días antes y aguanta una o dos semanas. El disparo que lo produjo está en el
pasado. Se toma el **máximo del índice en los N días previos**.

## El resultado

| Ventana | n | Percentil medio | z |
|---|---|---|---|
| 0 días (el día del hallazgo) | 65 | 52,9 % | +0,8 |
| **5 días** | 65 | **61,1 %** | **+3,1** |
| **10 días** | 65 | **60,9 %** | **+3,0** |
| **15 días** | 65 | **59,8 %** | **+2,7** |
| 21 días | 65 | 57,1 % | +2,0 |

*Grupo onddo, septiembre–noviembre. 50 % sería «el modelo no sabe nada».*

**Con ventana de 5 a 15 días, el modelo acierta de forma estadísticamente significativa.**
Un hallazgo cae, de media, en el percentil 61 de los días de su mes — no en el 50 que
cabría esperar por azar.

Y el patrón tiene la forma correcta: **sin ventana no hay señal** (52,9 %, z = +0,8), la
señal aparece al mirar hacia atrás y se desvanece al alargar demasiado. Eso es exactamente
lo que predice la biología —el disparo precede al carpóforo— y es lo que hace difícil
atribuirlo al azar: no es una ventana afortunada entre muchas, es una curva coherente.

**Control estacional aparte:** la correlación entre el índice medio mensual y el reparto
mensual de hallazgos es **r = +0,81**. La envolvente estacional, que estaba inventada,
reproduce el calendario real.

## Lo que esto NO demuestra

1. **Son presencias, no cosechas.** Nada dice de cuántos kilos. La capa POTENCIAL sigue sin
   validar; esto solo toca el DISPARO.
2. **Sesgo de recolector, y uno incómodo:** el buscador experimentado **sale al monte cuando
   las condiciones pintan bien**. Parte de la señal puede ser que el modelo coincide con el
   criterio del buscador, no con la seta. No es despreciable como resultado —significa que
   Ontto reproduce lo que ya sabe la gente— pero no es lo mismo que predecir fructificación.
3. **Muestra pequeña.** n = 65 en otoño. Descarta un efecto grande en contra; no descarta
   que la habilidad real sea menor que la medida.
4. **Fuera de otoño no hay señal** (todo el año: z = +1,9 como mucho). El modelo está
   calibrado para el otoño y ahí se queda.
5. El índice histórico usado se generó con la **regla de exclusión antigua** (acantilado).
   La diferencia con la rampa actual es r = 0,997, así que no cambia la conclusión.

## Qué queda por hacer

- **Ampliar la muestra.** Aranzadi tiene más de lo que publica en GBIF: catálogo digital de
  diversidad fúngica de Gipuzkoa y seguimientos en Oieleku, Añarbe, Artikutza y Monte San
  Antón. Contacto: `mikologia@aranzadi.eus`. Con unos cientos de registros más, la misma
  prueba pasaría de indicio a medida.
- **Repetir con el índice regenerado** cuando se reconstruya la serie histórica.
- **Validar la capa POTENCIAL** sigue necesitando producción medida. Ahí A1 continúa
  abierta.
