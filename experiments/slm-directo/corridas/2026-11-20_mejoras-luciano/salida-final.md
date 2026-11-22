# Mejoras de Luciano: salida de analizar.py

> Transcrita de la terminal de Colab el 2026-11-21 (`python3 -I analizar.py /content/resultados-mejoras-luciano`):
> las descargas del navegador no llegaron a la Mac. Columnas de veredicto abreviadas.

## Control

Las 15 corridas (3 prompts × 5 conjuntos) dan «bien», con `num_ctx` 16384 y **ninguna consulta inválida**:

| tanda | consultas de OTRA, por prompt |
|---|---|
| externo (coreanas) | 0/4193 inválidas |
| legitimas_reales | 0/387 |
| zona_gris | 0/1139 |
| desarrollo | 0/1313 |
| test_reservado | 0/1786 |

## Todas las combinaciones

| prompt · política | coreanas (/33) | coreanas a tiempo (/27) | FA reales (/33) | zona gris (/42) | desarrollo estafas (/46) | desarrollo a tiempo (/36) | desarrollo FA (/94) | test estafas (/100) | test a tiempo (/80) | test FA (/56) | veredicto |
|---|---|---|---|---|---|---|---|---|---|---|---|
| base · primer aviso | 33 | 27 | 21 | 29 | 42 | 28 | 21 | 75 | 53 | 16 | referencia |
| base · confirmación | 33 | 26 | 17 | 28 | 39 | 18 | 14 | 68 | 42 | 16 | no sirve: pierde 11 a tiempo en el test, no mejora lo suficiente |
| base · primer aviso + regla | 33 | 27 | 21 | 29 | 43 | 28 | 21 | 82 | 64 | 16 | **sirve** |
| base · confirmación + regla | 33 | 26 | 17 | 28 | 42 | 22 | 14 | 78 | 56 | 16 | no sirve: no mejora lo suficiente |
| base · cortá (regla o 0,5) | 29 | 20 | 5 | 12 | 24 | 18 | 8 | 50 | 39 | 4 | **sirve como «cortá»** |
| p-niveles · primer aviso | 32 | 24 | 13 | 7 | 24 | 20 | 16 | 44 | 29 | 19 | no sirve: pierde coreanas, pierde 24 a tiempo en el test |
| p-niveles · confirmación | 32 | 24 | 13 | 7 | 24 | 20 | 16 | 44 | 29 | 19 | no sirve: pierde coreanas, pierde 24 a tiempo en el test |
| p-niveles · primer aviso + regla | 33 | 24 | 13 | 7 | 30 | 23 | 16 | 57 | 42 | 19 | no sirve: pierde coreanas, pierde 11 a tiempo en el test |
| p-niveles · confirmación + regla | 33 | 24 | 13 | 7 | 30 | 23 | 16 | 57 | 42 | 19 | no sirve: pierde coreanas, pierde 11 a tiempo en el test |
| p-niveles · cortá (regla o 0,5) | 33 | 24 | 13 | 7 | 30 | 23 | 16 | 57 | 42 | 19 | no sirve como «cortá»: 13 FA reales, 19 FA en el test |
| p-lista · primer aviso | 31 | 22 | 17 | 15 | 37 | 31 | 36 | 80 | 70 | 15 | no sirve: pierde coreanas |
| p-lista · confirmación | 31 | 22 | 17 | 15 | 37 | 31 | 36 | 80 | 70 | 15 | no sirve: pierde coreanas |
| p-lista · primer aviso + regla | 31 | 22 | 17 | 15 | 38 | 31 | 36 | 81 | 71 | 15 | no sirve: pierde coreanas |
| p-lista · confirmación + regla | 31 | 22 | 17 | 15 | 38 | 31 | 36 | 81 | 71 | 15 | no sirve: pierde coreanas |
| p-lista · cortá (regla o 0,5) | 31 | 22 | 17 | 15 | 38 | 31 | 36 | 81 | 71 | 15 | no sirve como «cortá»: 17 FA reales, 15 FA en el test |
| solo la regla · — | 3 | 1 | 0 | 0 | 14 | 10 | 0 | 30 | 27 | 0 | — |
