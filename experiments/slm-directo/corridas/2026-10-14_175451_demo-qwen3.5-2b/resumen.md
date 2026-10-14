# Resumen de la corrida `2026-10-14_175451_demo-qwen3.5-2b`

> Material de **desarrollo** del ensayo [#50](https://github.com/Corchets/bitacora_tesis/issues/50):
> casos escritos, no grabaciones ni test final. Las posiciones son líneas, no segundos.
> El riesgo del SLM no está calibrado y no es una probabilidad. No elige modelo (D09) ni política (D08).

- **Comando:** `python correr.py --modelos qwen3.5:2b --sin-reglas --detalle --etiqueta demo-qwen3.5-2b`
- **Inicio / fin:** 2026-10-14T17:54:51 / 2026-10-14T17:59:50
- **Código:** `76fafa2ea6` con cambios sin commit en la carpeta
- **Máquina:** Windows-11-10.0.26300-SP0, 12 núcleos lógicos, 31.9 GB de RAM
- **Ollama:** 0.40.4 · **Política:** aviso_unico_primer_true_valido
- **Casos:** 53 (29 vishing, 24 legítimas); 53 todavía sin revisión humana

## Resultados por configuración

| Configuración | Vishing con aviso | Antes del pedido | En el pedido | Después del pedido | En/después del cumplimiento | Falsas alarmas | Fallos | ms p50 | ms p95 | Evidencia textual | Sin evaluar |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `slm\|qwen3.5:2b\|tarea\|ab` | 21/29 | 2 | 16 | 2 | 1 | 2/24 | 0/464 | 532 | 1.118 | 23/23 | 0 |

«Sin evaluar» son casos cortados o sin ninguna respuesta válida: no se cuentan en las demás columnas. «Antes del pedido» cuenta avisos previos a `T_R`; en vishing sin pedido de referencia el aviso se cuenta solo en «Vishing con aviso». «Evidencia textual» cuenta avisos cuya cita aparece en el texto disponible.

## Caso por caso

Configuraciones: **C1** `slm\|qwen3.5:2b\|tarea\|ab`

`=R` aviso en la línea del pedido (`T_R`) · `<R` antes del pedido · `>R` después del pedido y antes del cumplimiento · `≥C` en o después del cumplimiento (`T_C`) · `FA` falsa alarma en una legítima · `ok` legítima sin aviso · `—` vishing sin aviso · `…` sin evaluar: la corrida se cortó antes de terminar el caso · `x` sin evaluar: ninguna respuesta válida · `(xN)` N actualizaciones fallidas en el caso.

| Caso | Clase | T_R | T_C | C1 |
|---|---|---|---|---|
| `LAB-acceso-remoto` | vishing | 3 | — | =R L3 |
| `LAB-acceso-remoto-parafrasis` | vishing | 3 | — | =R L3 |
| `LAB-anses-beneficio` | vishing | 3 | — | =R L3 |
| `LAB-anses-beneficio-parafrasis` | vishing | 3 | — | =R L3 |
| `LAB-anses-canal-oficial` | legítima | — | — | ok |
| `LAB-arca-canal-oficial` | legítima | — | — | ok |
| `LAB-arca-deuda` | vishing | 3 | — | — |
| `LAB-arca-deuda-parafrasis` | vishing | 3 | — | — |
| `LAB-banco-app-parafrasis` | legítima | — | — | ok |
| `LAB-banco-codigo` | vishing | 5 | 6 | <R L3 |
| `LAB-banco-codigo-parafrasis` | vishing | 5 | 6 | =R L5 |
| `LAB-banco-gasto-sin-pedido` | legítima | — | — | ok |
| `LAB-banco-niega-el-codigo` | legítima | — | — | ok |
| `LAB-banco-numeros-sin-clave` | vishing | 5 | 6 | =R L5 |
| `LAB-banco-revisa-app` | legítima | — | — | ok |
| `LAB-digitos-sin-palabra` | vishing | 5 | — | — |
| `LAB-familiar-llama-vos` | legítima | — | — | ok |
| `LAB-familiar-peligro` | vishing | 4 | — | =R L4 |
| `LAB-familiar-peligro-parafrasis` | vishing | 4 | — | — |
| `LAB-giro-sin-plata` | vishing | 3 | — | — |
| `LAB-mensajeria-no-pases-nada` | legítima | — | — | ok |
| `LAB-no-bajes-nada` | legítima | — | — | ok |
| `LAB-pantalla-sin-programa` | vishing | 3 | — | =R L3 |
| `LAB-portero-codigo-puerta` | legítima | — | — | ok |
| `LAB-whatsapp-codigo` | vishing | 3 | 4 | <R L1 |
| `LAB-whatsapp-codigo-parafrasis` | vishing | 3 | 4 | =R L3 |
| `LG-BANK-VERIF-01-e01` | legítima | — | — | ok |
| `LG-FAMILIAR-LLAMADO-01-e01` | legítima | — | — | ok |
| `LG-ORG-TURNO-01-e01` | legítima | — | — | ok |
| `LG-PREMIO-CONSULTA-01-e01` | legítima | — | — | ok |
| `LG-SUPPORT-INFO-01-e01` | legítima | — | — | ok |
| `LG-SUPPORT-INFO-01-e02` | legítima | — | — | ok |
| `LG-WA-CONSULTA-01-e01` | legítima | — | — | ok |
| `SC-CLAVE-CAMBIO-01-e01` | vishing | 9 | 12 | =R L9 |
| `SC-FAMILIAR-DINERO-01-e01` | vishing | 9 | — | =R L9 |
| `SC-ORG-BENEFICIO-01-e01` | vishing | 7 | 8 | — |
| `SC-PREMIO-01-e01` | vishing | 8 | 13 | =R L8 |
| `SC-SOPORTE-CLAVE-01-e01` | vishing | 6 | 11 | =R L6 |
| `SC-SOPORTE-REMOTO-01-e01` | vishing | 6 | — | =R L6 |
| `SC-WA-CODE-01-e01` | vishing | 4 | 5 | =R L4 |
| `TR-01-pedido-indirecto-digitos` | vishing | 8 | 11 | — |
| `TR-02-codigo-del-candado` | legítima | — | — | ok |
| `TR-03-negacion-y-consejo` | legítima | — | — | FA L7 |
| `TR-04-pedido-tras-charla-larga` | vishing | 26 | 27 | =R L26 |
| `TR-05-asado-con-transferencia` | legítima | — | — | FA L17 |
| `TR-06-banco-alerta-legitima` | legítima | — | — | ok |
| `TR-07-pedido-partido-en-dos-lineas` | vishing | 7 | 9 | >R L8 |
| `TR-08-frase-cortada-candado` | legítima | — | — | ok |
| `TR-09-victima-se-niega` | vishing | 5 | — | >R L6 |
| `TR-10-ofrecimiento-inducido` | vishing | 8 | 13 | ≥C L14 |
| `TR-11-familiar-real-pide-plata` | legítima | — | — | ok |
| `TR-12-corta-antes-del-pedido` | vishing | — | — | — |
| `TR-13-turno-medico-pide-dni` | legítima | — | — | ok |

## Para revisar

### Falsas alarmas

- `TR-03-negacion-y-consejo` · `slm|qwen3.5:2b|tarea|ab` · línea 7: «Te están pidiendo compartir la pantalla para ayudarte con una aplicación» — evidencia (cita textual): «7. A: ¿Y si me piden que comparta la pantalla para ayudarme con la aplicación?»
- `TR-05-asado-con-transferencia` · `slm|qwen3.5:2b|tarea|ab` · línea 17: «Te están pidiendo un código de verificación para una transferencia antes del viernes» — evidencia (cita textual): «13. A: Si podés, pasámelos por transferencia antes del viernes, así le devuelvo a Lucho, que pagó todo él con la tarjeta.
14. B: Dale, no hay drama. Mandame el alias que ahora no lo tengo a mano.»

### Vishing sin aviso

- `LAB-arca-deuda` · `slm|qwen3.5:2b|tarea|ab` · riesgo máximo 0.30
- `LAB-arca-deuda-parafrasis` · `slm|qwen3.5:2b|tarea|ab` · riesgo máximo 0.30
- `LAB-digitos-sin-palabra` · `slm|qwen3.5:2b|tarea|ab` · riesgo máximo 0.30
- `LAB-familiar-peligro-parafrasis` · `slm|qwen3.5:2b|tarea|ab` · riesgo máximo 0.80
- `LAB-giro-sin-plata` · `slm|qwen3.5:2b|tarea|ab` · riesgo máximo 0.30
- `SC-ORG-BENEFICIO-01-e01` · `slm|qwen3.5:2b|tarea|ab` · riesgo máximo 0.85
- `TR-01-pedido-indirecto-digitos` · `slm|qwen3.5:2b|tarea|ab` · riesgo máximo 0.65
- `TR-12-corta-antes-del-pedido` · `slm|qwen3.5:2b|tarea|ab` · riesgo máximo 0.20

### Sin evaluar

Ninguno.

### Fallos por tipo

Ninguno.

## Carga y memoria informadas por Ollama

| Modelo | Carga (ms) | Memoria (MB) | En GPU (MB) |
|---|---|---|---|
| `qwen3.5:2b` | 4.642 | 2.255 | 2.255 |

La memoria es la que informa Ollama (pesos + caché de contexto) en esta PC; no es una medición en Android.
