# Resumen de la corrida `2026-10-26_125526_demo-tito-slm-simulado`

> Material de **desarrollo** del ensayo [#50](https://github.com/Corchets/bitacora_tesis/issues/50):
> casos escritos, no grabaciones ni test final. Las posiciones son líneas, no segundos.
> El riesgo del SLM no está calibrado y no es una probabilidad. No elige modelo (D09) ni política (D08).

- **Comando:** `python correr.py --modelos falso-demo:1b --url http://127.0.0.1:11439 --casos SC-WA-CODE-01-e01,LG-WA-CONSULTA-01-e01 --filtro-tito --tito-puntajes 4=0.9 --etiqueta demo-tito-slm-simulado --detalle`
- **Inicio / fin:** 2026-10-26T12:55:26 / 2026-10-26T12:55:26
- **Código:** `d53bbc1858` con cambios sin commit en la carpeta
- **Máquina:** Linux-7.2.5-3-omarchy-x86_64-with-glibc2.44, 16 núcleos lógicos, 30.5 GB de RAM
- **Ollama:** falso-demo-69 · **Política:** aviso_unico_primer_true_valido
- **Casos:** 2 (1 vishing, 1 legítimas); 2 todavía sin revisión humana

## Resultados por configuración

| Configuración | Vishing con aviso | Antes del pedido | En el pedido | Después del pedido | En/después del cumplimiento | Falsas alarmas | Fallos | ms p50 | ms p95 | Evidencia textual | Sin evaluar |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `reglas` | 1/1 | 0 | 1 | 0 | 0 | 1/1 | 0/9 | 5 | 7 | 2/2 | 0 |
| `slm\|falso-demo:1b\|tarea\|ab` | 1/1 | 0 | 1 | 0 | 0 | 0/1 | 0/9 | 0 | 1 | 1/1 | 0 |
| `tito-slm\|falso-demo:1b\|tarea\|ab` | 1/1 | 0 | 1 | 0 | 0 | 0/1 | 0/9 | 5 | 5 | 1/1 | 0 |

«Sin evaluar» son casos cortados o sin ninguna respuesta válida: no se cuentan en las demás columnas. «Antes del pedido» cuenta avisos previos a `T_R`; en vishing sin pedido de referencia el aviso se cuenta solo en «Vishing con aviso». «Evidencia textual» cuenta avisos cuya cita aparece en el texto disponible.

## Caso por caso

Configuraciones: **C1** `reglas` · **C2** `slm\|falso-demo:1b\|tarea\|ab` · **C3** `tito-slm\|falso-demo:1b\|tarea\|ab`

`=R` aviso en la línea del pedido (`T_R`) · `<R` antes del pedido · `>R` después del pedido y antes del cumplimiento · `≥C` en o después del cumplimiento (`T_C`) · `FA` falsa alarma en una legítima · `ok` legítima sin aviso · `—` vishing sin aviso · `…` sin evaluar: la corrida se cortó antes de terminar el caso · `x` sin evaluar: ninguna respuesta válida · `(xN)` N actualizaciones fallidas en el caso.

| Caso | Clase | T_R | T_C | C1 | C2 | C3 |
|---|---|---|---|---|---|---|
| `LG-WA-CONSULTA-01-e01` | legítima | — | — | FA L1 | ok | ok |
| `SC-WA-CODE-01-e01` | vishing | 4 | 5 | =R L4 | =R L4 | =R L4 |

## Para revisar

### Falsas alarmas

- `LG-WA-CONSULTA-01-e01` · `reglas` · línea 1: «REQUEST_AUTH_CODE (patrón: codigo)» — evidencia (cita textual): «Me llegó por SMS un código para activar WhatsApp y yo no lo pedí.»

### Vishing sin aviso

Ninguno.

### Sin evaluar

Ninguno.

### Fallos por tipo

Ninguno.

## Carga y memoria informadas por Ollama

| Modelo | Carga (ms) | Memoria (MB) | En GPU (MB) |
|---|---|---|---|
| `falso-demo:1b` | 1 | — | — |

La memoria es la que informa Ollama (pesos + caché de contexto) en esta PC; no es una medición en Android.

## Filtro Tito→SLM (derivación y ahorro)

Tito simulado (`guion-simulado`), umbral 0.5: el primer puntaje ≥ umbral deriva al SLM en esa misma línea y lo mantiene activo; un fallo técnico de Tito también deriva, sin fabricar sospecha.
Una conversación completa nunca derivada **conserva su denominador**: vishing sin aviso cuenta como falso negativo y legítima sin aviso como verdadero negativo.

### `tito-slm|falso-demo:1b|tarea|ab`

Consultas al SLM: 3; evitadas por el filtro: 6; costo Tito+SLM: 41 ms (omitidas: solo Tito; consultadas: Tito+SLM).

| Caso | 1.ª derivación | Aviso | Consultas SLM | Evitadas | Fallos SLM | Costo ms |
|---|---|---|---|---|---|---|
| `LG-WA-CONSULTA-01-e01` | 4 | sin aviso | 1 | 3 | 0 | 20 |
| `SC-WA-CODE-01-e01` | 4 | L4 | 2 | 3 | 0 | 21 |


## Trayectorias de riesgo

Riesgo por línea; entre corchetes, la línea del aviso; `x` = fallo.

```text
reglas
  SC-WA-CODE-01-e01                          · · · [·] ·
  LG-WA-CONSULTA-01-e01                      [·] · · ·
slm|falso-demo:1b|tarea|ab
  SC-WA-CODE-01-e01                          0.1 0.1 0.1 [0.95] 0.95
  LG-WA-CONSULTA-01-e01                      0.1 0.1 0.1 0.1
tito-slm|falso-demo:1b|tarea|ab
  SC-WA-CODE-01-e01                          · · · [0.95] 0.95
  LG-WA-CONSULTA-01-e01                      · · · 0.1
```
