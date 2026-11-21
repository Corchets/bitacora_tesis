> Reanálisis en la Mac el 2026-11-21 con los 10 ZIP parciales que llegaron: falta todo `p-lista` y `p-niveles` en desarrollo y
> el test. La base da las mismas cifras que [`salida-final.md`](salida-final.md), transcrita de Colab.

# Mejoras de Luciano: salida de analizar.py

## Control

| tanda | prompt | num_ctx | consultas inválidas | control |
|---|---|---|---|---|
| externo | base | 16384 | 0/4193 | bien |
| externo | p-niveles | 16384 | 0/4193 | bien |
| externo | p-lista | — | — | falta |
| legitimas_reales | base | 16384 | 0/387 | bien |
| legitimas_reales | p-niveles | 16384 | 0/387 | bien |
| legitimas_reales | p-lista | — | — | falta |
| desarrollo | base | 16384 | 0/1313 | bien |
| desarrollo | p-niveles | — | — | falta |
| desarrollo | p-lista | — | — | falta |
| zona_gris | base | 16384 | 0/1139 | bien |
| zona_gris | p-niveles | 16384 | 0/1139 | bien |
| zona_gris | p-lista | — | — | falta |
| test_reservado | base | 16384 | 0/1786 | bien |
| test_reservado | p-niveles | — | — | falta |
| test_reservado | p-lista | — | — | falta |

## Todas las combinaciones

| prompt · política | coreanas (/33) | coreanas a tiempo (/27) | FA reales (/33) | zona gris (/42) | desarrollo estafas (/46) | desarrollo a tiempo (/36) | desarrollo FA (/94) | test estafas (/100) | test a tiempo (/80) | test FA (/56) | veredicto |
|---|---|---|---|---|---|---|---|---|---|---|---|
| base · primer aviso | 33 | 27 | 21 | 29 | 42 | 28 | 21 | 75 | 53 | 16 | referencia |
| base · confirmación | 33 | 26 | 17 | 28 | 39 | 18 | 14 | 68 | 42 | 16 | no sirve: pierde 11 a tiempo en el test, no mejora lo suficiente |
| base · primer aviso + regla | 33 | 27 | 21 | 29 | 43 | 28 | 21 | 82 | 64 | 16 | **sirve** |
| base · confirmación + regla | 33 | 26 | 17 | 28 | 42 | 22 | 14 | 78 | 56 | 16 | no sirve: no mejora lo suficiente |
| base · cortá (regla o 0,5) | 29 | 20 | 5 | 12 | 24 | 18 | 8 | 50 | 39 | 4 | sirve como «cortá» |
| p-niveles · primer aviso | 32 | 24 | 13 | 7 | — | — | — | — | — | — | no sirve: faltan corridas |
| p-niveles · confirmación | 32 | 24 | 13 | 7 | — | — | — | — | — | — | no sirve: faltan corridas |
| p-niveles · primer aviso + regla | 33 | 24 | 13 | 7 | — | — | — | — | — | — | no sirve: faltan corridas |
| p-niveles · confirmación + regla | 33 | 24 | 13 | 7 | — | — | — | — | — | — | no sirve: faltan corridas |
| p-niveles · cortá (regla o 0,5) | 33 | 24 | 13 | 7 | — | — | — | — | — | — | no sirve como «cortá»: faltan corridas |
| p-lista · primer aviso | — | — | — | — | — | — | — | — | — | — | no sirve: faltan corridas |
| p-lista · confirmación | — | — | — | — | — | — | — | — | — | — | no sirve: faltan corridas |
| p-lista · primer aviso + regla | — | — | — | — | — | — | — | — | — | — | no sirve: faltan corridas |
| p-lista · confirmación + regla | — | — | — | — | — | — | — | — | — | — | no sirve: faltan corridas |
| p-lista · cortá (regla o 0,5) | — | — | — | — | — | — | — | — | — | — | no sirve como «cortá»: faltan corridas |
| solo la regla · — | 3 | 1 | 0 | 0 | 14 | 10 | 0 | 30 | 27 | 0 | — |
