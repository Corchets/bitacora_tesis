# Resumen de la corrida `2026-10-14_172248_demo-qwen3.5-2b`

> Material de **desarrollo** del ensayo [#50](https://github.com/Corchets/bitacora_tesis/issues/50):
> casos escritos, no grabaciones ni test final. Las posiciones son líneas, no segundos.
> El riesgo del SLM no está calibrado y no es una probabilidad. No elige modelo (D09) ni política (D08).

- **Comando:** `python correr.py --modelos qwen3.5:2b --sin-reglas --casos SC-WA-CODE-01-e01,LG-WA-CONSULTA-01-e01,SC-SOPORTE-CLAVE-01-e01,LG-SUPPORT-INFO-01-e01,TR-01-pedido-indirecto-digitos,TR-02-codigo-del-candado,TR-08-frase-cortada-candado,TR-12-corta-antes-del-pedido --detalle --etiqueta demo-qwen3.5-2b`
- **Inicio / fin:** 2026-10-14T17:22:48 / 2026-10-14T17:24:28
- **Código:** `ec0ba1b0e0`
- **Máquina:** Windows-11-10.0.26300-SP0, 12 núcleos lógicos, 31.9 GB de RAM
- **Ollama:** 0.40.4 · **Política:** aviso_unico_primer_true_valido
- **Casos:** 8 (4 vishing, 4 legítimas); 8 todavía sin revisión humana

## Resultados por configuración

| Configuración | Vishing con aviso | Antes del pedido | En el pedido | Después del pedido | En/después del cumplimiento | Falsas alarmas | Fallos | ms p50 | ms p95 | Evidencia textual | Sin evaluar |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `slm\|qwen3.5:2b\|tarea\|ab` | 2/4 | 0 | 2 | 0 | 0 | 0/4 | 0/73 | 527 | 1.179 | 1/2 | 0 |

«Sin evaluar» son casos cortados o sin ninguna respuesta válida: no se cuentan en las demás columnas. «Antes del pedido» cuenta avisos previos a `T_R`; en vishing sin pedido de referencia el aviso se cuenta solo en «Vishing con aviso». «Evidencia textual» cuenta avisos cuya cita aparece en el texto disponible.

## Caso por caso

Configuraciones: **C1** `slm\|qwen3.5:2b\|tarea\|ab`

`=R` aviso en la línea del pedido (`T_R`) · `<R` antes del pedido · `>R` después del pedido y antes del cumplimiento · `≥C` en o después del cumplimiento (`T_C`) · `FA` falsa alarma en una legítima · `ok` legítima sin aviso · `—` vishing sin aviso · `…` sin evaluar: la corrida se cortó antes de terminar el caso · `x` sin evaluar: ninguna respuesta válida · `(xN)` N actualizaciones fallidas en el caso.

| Caso | Clase | T_R | T_C | C1 |
|---|---|---|---|---|
| `LG-SUPPORT-INFO-01-e01` | legítima | — | — | ok |
| `LG-WA-CONSULTA-01-e01` | legítima | — | — | ok |
| `SC-SOPORTE-CLAVE-01-e01` | vishing | 6 | 11 | =R L6 |
| `SC-WA-CODE-01-e01` | vishing | 4 | 5 | =R L4 |
| `TR-01-pedido-indirecto-digitos` | vishing | 8 | 11 | — |
| `TR-02-codigo-del-candado` | legítima | — | — | ok |
| `TR-08-frase-cortada-candado` | legítima | — | — | ok |
| `TR-12-corta-antes-del-pedido` | vishing | — | — | — |

## Para revisar

### Falsas alarmas

Ninguna.

### Vishing sin aviso

- `TR-01-pedido-indirecto-digitos` · `slm|qwen3.5:2b|tarea|ab` · riesgo máximo 0.65
- `TR-12-corta-antes-del-pedido` · `slm|qwen3.5:2b|tarea|ab` · riesgo máximo 0.20

### Sin evaluar

Ninguno.

### Fallos por tipo

Ninguno.

## Carga y memoria informadas por Ollama

| Modelo | Carga (ms) | Memoria (MB) | En GPU (MB) |
|---|---|---|---|
| `qwen3.5:2b` | 53.634 | 2.255 | 2.255 |

La memoria es la que informa Ollama (pesos + caché de contexto) en esta PC; no es una medición en Android.
