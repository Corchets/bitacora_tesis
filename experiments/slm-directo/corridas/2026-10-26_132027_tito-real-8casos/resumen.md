# Resumen de la corrida `2026-10-26_132027_tito-real-8casos`

> Material de **desarrollo** del ensayo [#50](https://github.com/Corchets/bitacora_tesis/issues/50):
> casos escritos, no grabaciones ni test final. Las posiciones son líneas, no segundos.
> El riesgo del SLM no está calibrado y no es una probabilidad. No elige modelo (D09) ni política (D08).

- **Comando:** `python correr.py --modelos falso-demo:1b --url http://127.0.0.1:11439 --casos TR-04-pedido-tras-charla-larga,TR-06-banco-alerta-legitima,TR-07-pedido-partido-en-dos-lineas,TR-08-frase-cortada-candado,SC-SOPORTE-REMOTO-01-e01,LG-SUPPORT-INFO-01-e02,SC-FAMILIAR-DINERO-01-e01,TR-11-familiar-real-pide-plata --filtro-tito --tito-real --etiqueta tito-real-8casos --detalle`
- **Inicio / fin:** 2026-10-26T13:20:27 / 2026-10-26T13:20:31
- **Código:** `d53bbc1858` con cambios sin commit en la carpeta
- **Máquina:** Linux-7.2.5-3-omarchy-x86_64-with-glibc2.44, 16 núcleos lógicos, 30.5 GB de RAM
- **Ollama:** falso-demo-69 · **Política:** aviso_unico_primer_true_valido
- **Casos:** 8 (4 vishing, 4 legítimas); 8 todavía sin revisión humana

## Resultados por configuración

| Configuración | Vishing con aviso | Antes del pedido | En el pedido | Después del pedido | En/después del cumplimiento | Falsas alarmas | Fallos | ms p50 | ms p95 | Evidencia textual | Sin evaluar |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `reglas` | 4/4 | 3 | 0 | 1 | 0 | 4/4 | 0/105 | 8 | 17 | 8/8 | 0 |
| `slm\|falso-demo:1b\|tarea\|ab` | 0/4 | 0 | 0 | 0 | 0 | 0/4 | 0/105 | 0 | 0 | 0/0 | 0 |
| `tito-slm\|falso-demo:1b\|tarea\|ab` | 0/4 | 0 | 0 | 0 | 0 | 0/4 | 0/105 | 0 | 25 | 0/0 | 0 |

«Sin evaluar» son casos cortados o sin ninguna respuesta válida: no se cuentan en las demás columnas. «Antes del pedido» cuenta avisos previos a `T_R`; en vishing sin pedido de referencia el aviso se cuenta solo en «Vishing con aviso». «Evidencia textual» cuenta avisos cuya cita aparece en el texto disponible.

## Caso por caso

Configuraciones: **C1** `reglas` · **C2** `slm\|falso-demo:1b\|tarea\|ab` · **C3** `tito-slm\|falso-demo:1b\|tarea\|ab`

`=R` aviso en la línea del pedido (`T_R`) · `<R` antes del pedido · `>R` después del pedido y antes del cumplimiento · `≥C` en o después del cumplimiento (`T_C`) · `FA` falsa alarma en una legítima · `ok` legítima sin aviso · `—` vishing sin aviso · `…` sin evaluar: la corrida se cortó antes de terminar el caso · `x` sin evaluar: ninguna respuesta válida · `(xN)` N actualizaciones fallidas en el caso.

| Caso | Clase | T_R | T_C | C1 | C2 | C3 |
|---|---|---|---|---|---|---|
| `LG-SUPPORT-INFO-01-e02` | legítima | — | — | FA L4 | ok | ok |
| `SC-FAMILIAR-DINERO-01-e01` | vishing | 9 | — | <R L6 | — | — |
| `SC-SOPORTE-REMOTO-01-e01` | vishing | 6 | — | <R L3 | — | — |
| `TR-04-pedido-tras-charla-larga` | vishing | 26 | 27 | <R L6 | — | — |
| `TR-06-banco-alerta-legitima` | legítima | — | — | FA L10 | ok | ok |
| `TR-07-pedido-partido-en-dos-lineas` | vishing | 7 | 9 | >R L8 | — | — |
| `TR-08-frase-cortada-candado` | legítima | — | — | FA L3 | ok | ok |
| `TR-11-familiar-real-pide-plata` | legítima | — | — | FA L4 | ok | ok |

## Para revisar

### Falsas alarmas

- `TR-06-banco-alerta-legitima` · `reglas` · línea 10: «REQUEST_AUTH_CODE (patrón: codigo)» — evidencia (cita textual): «Hace un rato me llegó un mensaje con un código. ¿Te lo paso así lo verificás?»
- `TR-08-frase-cortada-candado` · `reglas` · línea 3: «REQUEST_AUTH_CODE (patrón: codigo)» — evidencia (cita textual): «Pasame el código»
- `LG-SUPPORT-INFO-01-e02` · `reglas` · línea 4: «REQUEST_REMOTE_ACCESS (patrón: instala)» — evidencia (cita textual): «No, eso no. Nosotros no te vamos a pedir que compartas la pantalla ni que instales nada para que alguien entre a tu celular.»
- `TR-11-familiar-real-pide-plata` · `reglas` · línea 4: «REQUEST_TRANSFER (patrón: transferi)» — evidencia (cita textual): «Nada grave. Me vino más alta la boleta de la luz y no llego hasta el viernes. ¿Me podrás transferir veinte mil pesos?»

### Vishing sin aviso

- `TR-04-pedido-tras-charla-larga` · `slm|falso-demo:1b|tarea|ab` · riesgo máximo 0.10
- `TR-07-pedido-partido-en-dos-lineas` · `slm|falso-demo:1b|tarea|ab` · riesgo máximo 0.10
- `SC-SOPORTE-REMOTO-01-e01` · `slm|falso-demo:1b|tarea|ab` · riesgo máximo 0.10
- `SC-FAMILIAR-DINERO-01-e01` · `slm|falso-demo:1b|tarea|ab` · riesgo máximo 0.10
- `TR-04-pedido-tras-charla-larga` · `tito-slm|falso-demo:1b|tarea|ab` · riesgo máximo 0.10
- `TR-07-pedido-partido-en-dos-lineas` · `tito-slm|falso-demo:1b|tarea|ab` · riesgo máximo 0.10
- `SC-SOPORTE-REMOTO-01-e01` · `tito-slm|falso-demo:1b|tarea|ab` · riesgo máximo 0.10
- `SC-FAMILIAR-DINERO-01-e01` · `tito-slm|falso-demo:1b|tarea|ab` · riesgo máximo 0.10

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

Tito simulado (`real-robertuito-logreg`), umbral 0.5: el primer puntaje ≥ umbral deriva al SLM en esa misma línea y lo mantiene activo; un fallo técnico de Tito también deriva, sin fabricar sospecha.
Una conversación completa nunca derivada **conserva su denominador**: vishing sin aviso cuenta como falso negativo y legítima sin aviso como verdadero negativo.

### `tito-slm|falso-demo:1b|tarea|ab`

Consultas al SLM: 70; evitadas por el filtro: 35; costo Tito+SLM: 3.545 ms (omitidas: solo Tito; consultadas: Tito+SLM).

| Caso | 1.ª derivación | Aviso | Consultas SLM | Evitadas | Fallos SLM | Costo ms |
|---|---|---|---|---|---|---|
| `LG-SUPPORT-INFO-01-e02` | 8 | sin aviso | 6 | 7 | 0 | 182 |
| `SC-FAMILIAR-DINERO-01-e01` | 9 | sin aviso | 4 | 8 | 0 | 175 |
| `SC-SOPORTE-REMOTO-01-e01` | 1 | sin aviso | 11 | 0 | 0 | 22 |
| `TR-04-pedido-tras-charla-larga` | 5 | sin aviso | 26 | 4 | 0 | 2.791 |
| `TR-06-banco-alerta-legitima` | 3 | sin aviso | 10 | 2 | 0 | 66 |
| `TR-07-pedido-partido-en-dos-lineas` | 5 | sin aviso | 6 | 4 | 0 | 96 |
| `TR-08-frase-cortada-candado` | 3 | sin aviso | 5 | 2 | 0 | 46 |
| `TR-11-familiar-real-pide-plata` | 9 | sin aviso | 2 | 8 | 0 | 166 |


## Trayectorias de riesgo

Riesgo por línea; entre corchetes, la línea del aviso; `x` = fallo.

```text
reglas
  TR-04-pedido-tras-charla-larga             · · · · · [·] · · · · · · · · · · · · · · · · · · · · · · · ·
  TR-06-banco-alerta-legitima                · · · · · · · · · [·] · ·
  TR-07-pedido-partido-en-dos-lineas         · · · · · · · [·] · ·
  TR-08-frase-cortada-candado                · · [·] · · · ·
  SC-SOPORTE-REMOTO-01-e01                   · · [·] · · · · · · · ·
  LG-SUPPORT-INFO-01-e02                     · · · [·] · · · · · · · · ·
  SC-FAMILIAR-DINERO-01-e01                  · · · · · [·] · · · · · ·
  TR-11-familiar-real-pide-plata             · · · [·] · · · · · ·
slm|falso-demo:1b|tarea|ab
  TR-04-pedido-tras-charla-larga             0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1
  TR-06-banco-alerta-legitima                0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1
  TR-07-pedido-partido-en-dos-lineas         0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1
  TR-08-frase-cortada-candado                0.1 0.1 0.1 0.1 0.1 0.1 0.1
  SC-SOPORTE-REMOTO-01-e01                   0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1
  LG-SUPPORT-INFO-01-e02                     0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1
  SC-FAMILIAR-DINERO-01-e01                  0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1
  TR-11-familiar-real-pide-plata             0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1
tito-slm|falso-demo:1b|tarea|ab
  TR-04-pedido-tras-charla-larga             · · · · 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1
  TR-06-banco-alerta-legitima                · · 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1
  TR-07-pedido-partido-en-dos-lineas         · · · · 0.1 0.1 0.1 0.1 0.1 0.1
  TR-08-frase-cortada-candado                · · 0.1 0.1 0.1 0.1 0.1
  SC-SOPORTE-REMOTO-01-e01                   0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1
  LG-SUPPORT-INFO-01-e02                     · · · · · · · 0.1 0.1 0.1 0.1 0.1 0.1
  SC-FAMILIAR-DINERO-01-e01                  · · · · · · · · 0.1 0.1 0.1 0.1
  TR-11-familiar-real-pide-plata             · · · · · · · · 0.1 0.1
```
