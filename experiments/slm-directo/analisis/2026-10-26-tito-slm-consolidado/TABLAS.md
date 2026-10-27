# Tablas cruzadas Tito→SLM (generado por `consolidar.py`)

No editar a mano: se regenera con `bash regenerar.sh` desde las salidas crudas.

## Detección y falsas alarmas por modelo y variante

| Modelo | Vishing directo | Vishing filtrado | FA directo | FA filtrado |
|---|---|---|---|---|
| `qwen3.5:4b-q4_K_M` | 4/4 | 4/4 | 3/4 | 4/4 |
| `qwen3.5:0.8b-q8_0` | 4/4 | 4/4 | 2/4 | 2/4 |
| `qwen3.5:0.8b` | 4/4 | 4/4 | 2/4 | 2/4 |
| `qwen3.5:2b-q8_0` | 4/4 | 4/4 | 0/4 | 1/4 |
| `qwen3.5:9b-q4_K_M` | 4/4 | 4/4 | 3/4 | 2/4 |
| `llama3.2:1b-instruct-q4_K_M` | 0/4 | 2/4 | 0/4 | 3/4 |

Denominadores: 4 vishing y 4 legítimas difíciles por variante y modelo.

## Ahorro y costo por modelo

| Modelo | Consultas D | Consultas F | Evitadas | Tokens D | Tokens F | Costo ms D | Costo ms F | Fallos SLM D/F | Fallos Tito |
|---|---|---|---|---|---|---|---|---|---|
| `qwen3.5:4b-q4_K_M` | 105 | 70 | 35 | 78900 | 66127 | 97969 | 113314 | 0/0 | 0 |
| `qwen3.5:0.8b-q8_0` | 105 | 70 | 35 | 77512 | 66566 | 31416 | 46364 | 0/0 | 0 |
| `qwen3.5:0.8b` | 105 | 70 | 35 | 77512 | 66599 | 24200 | 38419 | 0/0 | 0 |
| `qwen3.5:2b-q8_0` | 105 | 70 | 35 | 77749 | 63483 | 55037 | 46954 | 0/0 | 0 |
| `qwen3.5:9b-q4_K_M` | 105 | 70 | 35 | 79032 | 64945 | 153222 | 141504 | 0/0 | 0 |
| `llama3.2:1b-instruct-q4_K_M` | 105 | 70 | 35 | 87910 | 71909 | 39297 | 33464 | 5/0 | 0 |

Costo ms F = Tito en todas las líneas + SLM válido y fallido; carga, calentamiento y ajuste van por separado en cada `comparacion.md`.

## Cambios de aviso (directo → filtrado)

- `qwen3.5:4b-q4_K_M`: LG-SUPPORT-INFO-01-e02: sin aviso → L10; TR-04-pedido-tras-charla-larga: L3 → L5; TR-07-pedido-partido-en-dos-lineas: L3 → L5; TR-11-familiar-real-pide-plata: L4 → L9.
- `qwen3.5:0.8b-q8_0`: SC-FAMILIAR-DINERO-01-e01: L8 → L9; SC-SOPORTE-REMOTO-01-e01: L6 → L4; TR-04-pedido-tras-charla-larga: L20 → L6; TR-06-banco-alerta-legitima: sin aviso → L3; TR-07-pedido-partido-en-dos-lineas: L9 → L5; TR-08-frase-cortada-candado: L4 → sin aviso.
- `qwen3.5:0.8b`: SC-FAMILIAR-DINERO-01-e01: L8 → L9; SC-SOPORTE-REMOTO-01-e01: L6 → L4; TR-04-pedido-tras-charla-larga: L20 → L6; TR-06-banco-alerta-legitima: sin aviso → L3; TR-07-pedido-partido-en-dos-lineas: L9 → L5; TR-08-frase-cortada-candado: L4 → sin aviso.
- `qwen3.5:2b-q8_0`: LG-SUPPORT-INFO-01-e02: sin aviso → L12.
- `qwen3.5:9b-q4_K_M`: TR-06-banco-alerta-legitima: L10 → L9; TR-07-pedido-partido-en-dos-lineas: L4 → L5; TR-11-familiar-real-pide-plata: L4 → sin aviso.
- `llama3.2:1b-instruct-q4_K_M`: LG-SUPPORT-INFO-01-e02: sin aviso → L9; TR-04-pedido-tras-charla-larga: sin aviso → L10; TR-06-banco-alerta-legitima: sin aviso → L5; TR-07-pedido-partido-en-dos-lineas: sin aviso → L5; TR-11-familiar-real-pide-plata: sin aviso → L9.

La comparación mide activación selectiva + indicio falible juntos; no se atribuye el efecto a uno de ellos por separado.
