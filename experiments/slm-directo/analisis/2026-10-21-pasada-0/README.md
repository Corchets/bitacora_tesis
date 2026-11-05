# Pasada 0 hacia 95/5: combinar detectores guardados

> **Estado: propuesta sin discutir.** La meta 95/5 (avisar en el 95 % de las estafas con a
> lo sumo 5 % de falsas alarmas) es la que propuso Luciano el 2026-10-23 y falta que la
> apruebe el tutor ([D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental)).
> Todo es material de desarrollo: nada de esto reemplaza al test reservado.

[`combinar.py`](combinar.py) no corre modelos. Toma las corridas guardadas y prueba:

- cada detector solo, con umbral τ sobre el riesgo (con o sin `alerta_sugerida`) y
  persistencia k (líneas seguidas);
- pares de detectores con tres operadores: **Y** (los dos en la misma línea), **O**
  (cualquiera) y **luego**, una cascada que avisa cuando los dos ya dispararon alguna vez.

Para no elegir y medir sobre los mismos casos, se elige con una parte y se informa otra
(mitades fijas por SHA-256 del `case_id`, balanceadas por clase). La regla de elección
es el mayor recall con FA ≤ 5, 10 o 20 % en la selección.

```
python analisis/2026-10-21-pasada-0/combinar.py              # 150: elige con 53 + mitad A de corpus_v2, informa B
python analisis/2026-10-21-pasada-0/combinar.py --casos 53   # solo los 53: elige con su mitad A, informa B
```

Salidas: [`combinar.json`](combinar.json) y [`combinar-53.json`](combinar-53.json).

## 1. Sobre los 150 (reglas y 2B)

Solo las reglas y el 2B tienen los 150 completos. La mitad B tiene 23 estafas, de las
cuales 17 tienen pedido, y 25 legítimas.

| Presupuesto | Mejor configuración | Mitad B: estafas | Con pedido | Mitad B: FA |
|---|---|---|---|---|
| FA ≤ 5 % | (reglas v2) Y (2B v1, riesgo ≥ 0,35) | 3/23 (5–32 %) | 3/17 | 0/25 (0–13 %) |
| FA ≤ 10 % | (2B v1, riesgo ≥ 0,45) Y (2B v2, riesgo ≥ 0,25) | 11/23 (29–67 %) | 11/17 | 5/25 (9–39 %) |
| FA ≤ 20 % | 2B v1, riesgo ≥ 0,40 | 15/23 (45–81 %) | 13/17 | 5/25 (9–39 %) |

Ninguna de las 517 configuraciones llega a 95/5 en la selección. Con el 2B y las reglas,
la pasada 0 no se acerca a la meta.

## 2. Sobre los 53 históricos (suma 0.8B, 4B y 9B de Linux)

Es optimista por dos motivos: el v2 se escribió mirando estos casos y cada mitad tiene unos
26 casos (14 estafas y 12 legítimas en la B), así que los intervalos son muy anchos.

| Presupuesto | Mejor configuración | Mitad B: estafas | Mitad B: FA |
|---|---|---|---|
| FA ≤ 5 % | (2B v2, riesgo ≥ 0,15) Y (9B v1, alerta ≥ 0,95) | 13/14 (69–99 %) | 2/12 (5–45 %) |
| FA ≤ 5 %, un solo modelo | 4B v2, riesgo ≥ 0,35, k = 2 | 11/14 (52–92 %) | 0/12 (0–24 %) |
| FA ≤ 10 %, un solo modelo | 9B v2, riesgo ≥ 0,25, k = 3 | 13/14 (69–99 %) | 1/12 (1–35 %) |
| FA ≤ 20 %, un solo modelo | 9B v1, alerta ≥ 0,85, k = 3 | 14/14 (78–100 %) | 2/12 (5–45 %) |

Una sola configuración de 3093 cumple 95/5 en la selección (el par de la primera fila), y
en la mitad B da 2/12 FA.

### «El 4B o el 9B avisan y el 2B confirma»

| 53 históricos | Estafas | FA |
|---|---|---|
| 2B v1 solo | 20/29 | 2/24 |
| 9B v1 luego 2B v1 | 20/29 | 1/24 |
| (4B v1 O 9B v1) luego 2B v1 | 20/29 | 2/24 |
| 2B v2 solo | 24/29 | 4/24 |
| 9B v1 luego 2B v2 | 24/29 | 3/24 |

La cascada no agrega nada. El 4B y el 9B con v1 avisan en casi todas las llamadas, así que
«luego 2B» se reduce al 2B solo, menos una FA. Lo que falta es recall en el que confirma,
no un filtro. Lo que sí funciona en estos 53 son los modelos grandes **con el v2 y un umbral
de riesgo**, solos o con el 2B en la misma línea.

## 3. Qué dice para la gama objetivo

La gama objetivo propuesta el 2026-10-23 son los teléfonos de gama alta: iPhone 16 o
posterior, Samsung de gama alta y equivalentes de otras marcas
([D09](../../../../docs/gestion/MAPA-DECISIONES.md#d09--elegir-asr-y-detector)). Los pesos
en Ollama ocupan 1,0 GB el 0.8B `q8_0`, 2,7 GB el 2B `q8_0`, 3,3 GB el 4B `q4_K_M` y 6,6 GB
el 9B `q4_K_M`, sin contar la caché ni el ASR.

- Si el 9B es el único que se acerca a 95/5 en corpus_v2, se documenta como **techo de
  referencia** («da lo que buscamos, pero no entra en un teléfono de la gama») y se elige
  el mejor de lo que sí entra.
- Si alcanza con el 4B v2 con umbral, la propuesta es el 4B. Todavía falta medirlo en
  corpus_v2.

## 4. Próximo paso

Cuando lleguen las corridas de Ignacio sobre corpus_v2 (`linux-4b-v1v2-cv2-nb32`,
`linux-9b-v1v2-cv2-nb32` y `linux-0.8b-v1v2-nb32`), `combinar.py` junta sola las dos carpetas
de cada modelo y vuelve a la partición de los 150. Regla de las pasadas: tope de 3, y frenar
si no se acerca a 95/5.
