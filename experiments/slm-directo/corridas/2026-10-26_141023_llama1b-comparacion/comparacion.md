# Comparación llama3.2:1b-instruct-q4_K_M: directo vs Tito→SLM

Corrida `2026-10-26_141023_llama1b-comparacion` · Tito real (`real-robertuito-logreg`, umbral 0.5).
Mismas predicciones en ambas lecturas de marcas; la referencia original no cambia.

## Por conversación

| Caso | Clase | Deriv. | Aviso directo | Aviso filtrado | Cons. D/F | Evit. | Tokens D/F | Costo ms D/F |
|---|---|---|---|---|---|---|---|---|
| `LG-SUPPORT-INFO-01-e02` | legitima_dificil | 8 | — | L9 | 13/6 | 7 | 10271/6335 | 3977/3690 |
| `SC-FAMILIAR-DINERO-01-e01` | vishing | 9 | — | — | 12/4 | 8 | 9085/4119 | 4223/2128 |
| `SC-SOPORTE-REMOTO-01-e01` | vishing | 1 | — | — | 11/11 | 0 | 8560/9893 | 3215/4141 |
| `TR-04-pedido-tras-charla-larga` | vishing | 5 | — | L10 | 30/26 | 4 | 32480/31945 | 15810/14643 |
| `TR-06-banco-alerta-legitima` | legitima_dificil | 3 | — | L5 | 12/10 | 2 | 8763/8927 | 3212/4065 |
| `TR-07-pedido-partido-en-dos-lineas` | vishing | 5 | — | L5 | 10/6 | 4 | 6946/5245 | 2648/2500 |
| `TR-08-frase-cortada-candado` | legitima_dificil | 3 | — | — | 7/5 | 2 | 4457/3697 | 1742/1512 |
| `TR-11-familiar-real-pide-plata` | legitima_dificil | 9 | — | L9 | 10/2 | 8 | 7348/1748 | 4470/785 |

Tokens totales (prompt+salida): directo 87910, filtrado 71909. Carga, calentamiento y ajuste van por separado abajo.

## Cambios de aviso entre variantes

- `LG-SUPPORT-INFO-01-e02`: directo sin aviso → filtrado L9, derivación L8 (indicio L8 p=0.909).
- `TR-04-pedido-tras-charla-larga`: directo sin aviso → filtrado L10, derivación L5 (indicio L5 p=0.633).
- `TR-06-banco-alerta-legitima`: directo sin aviso → filtrado L5, derivación L3 (indicio L3 p=0.986).
- `TR-07-pedido-partido-en-dos-lineas`: directo sin aviso → filtrado L5, derivación L5 (indicio L5 p=0.994).
- `TR-11-familiar-real-pide-plata`: directo sin aviso → filtrado L9, derivación L9 (indicio L9 p=0.987).

## Doble lectura de marcas (mismas predicciones)

### `TR-04-pedido-tras-charla-larga`: referencia T_R=26/T_C=27, alternativa T_R=21/T_C=22
- directo (aviso ninguno): referencia → sin aviso; alternativa → sin aviso.
- filtrado (aviso L10): referencia → -16 líneas (antes del pedido L26); alternativa → -11 líneas (antes del pedido L21).

### `TR-07-pedido-partido-en-dos-lineas`: referencia T_R=7/T_C=9, alternativa T_R=8/T_C=9
- directo (aviso ninguno): referencia → sin aviso; alternativa → sin aviso.
- filtrado (aviso L5): referencia → -2 líneas (antes del pedido L7); alternativa → -3 líneas (antes del pedido L8).

## Motivos y citas (avisos anteriores al pedido incluidos)

Referencias provisorias: ningún caso tiene revisión humana; las lecturas de
pedido inventado o sospecha reforzada son del autor del reporte, no del manual.

- `LG-SUPPORT-INFO-01-e02` · filtrado · L9: «La llamada sigue después de la línea 8, donde se solicita la clave y se menciona la pantalla de la aplicación del banco. Podría ser una estafa para obtener la clave y acceder a la cuenta del destinatario.» — cita NO textual: «La línea 8 de la transcripción es la que menciona la clave y la pantalla de la aplicación del banco, lo que sugiere una estafa.»
- `TR-04-pedido-tras-charla-larga` · filtrado · L10 — anterior al pedido (T_R L26): «La llamada parece ser una estafa, ya que no se menciona el nombre de la sucursal ni la fecha, y no hay ninguna razón para que Silvina se llame de la sucursal del banco donde cobrás la jubilación, la de la avenida, al lado de la farmacia.» — cita NO textual: «La línea 5 de la transcripción es una sospecha preliminar, ya que no se menciona el nombre de la sucursal ni la fecha, y no hay ninguna razón para que Silvina se llame de la sucursal del banco donde cobrás la jubilación, la de la avenida, al lado de la farmacia.»
- `TR-06-banco-alerta-legitima` · filtrado · L5: «Te están pidiendo un código que da acceso a tu cuenta» — cita textual: «¿Qué consumo? Una compra de sesenta y dos mil pesos en una tienda en línea, hoy a las once y cuarto.»
- `TR-07-pedido-partido-en-dos-lineas` · filtrado · L5 — anterior al pedido (T_R L7): «Sospecha preliminar, puede ser incorrecta y no confirma una estafa.» — cita NO textual: «La línea 5: "Todavía no pudieron operar, por eso te llamo ya. El sistema te acaba de mandar un mensaje para desvincularlo."»
- `TR-11-familiar-real-pide-plata` · filtrado · L9: «La sospecha preliminar no confirma una estafa.» — cita NO textual: «La línea 9: "Dale, te corto y te llamo"»

## Runtime común y hardware

- Comando: `python correr.py --modelos llama3.2:1b-instruct-q4_K_M --url http://127.0.0.1:11435 --casos TR-04-pedido-tras-charla-larga,TR-06-banco-alerta-legitima,TR-07-pedido-partido-en-dos-lineas,TR-08-frase-cortada-candado,SC-SOPORTE-REMOTO-01-e01,LG-SUPPORT-INFO-01-e02,SC-FAMILIAR-DINERO-01-e01,TR-11-familiar-real-pide-plata --filtro-tito --tito-real --sin-reglas --num-batch 32 --etiqueta llama1b-comparacion`
- Código: `d53bbc1858b3fa8fafc7cc2006a0f7d1f3bfce9d` (cambios sin commit en la carpeta: True)
- Ollama 0.40.8 en http://127.0.0.1:11435, digests: {'llama3.2:1b-instruct-q4_K_M': '22bc6b92eb0160c4629782fca05a9032c59d306ab2058b7dacc8a4644fbafa02'}
- Chequeo previo de contrato JSON: `chequeo-contrato.json` en esta carpeta (digest verificado, `think: false`, esquema, `num_ctx` 4096 aceptados; una incompatibilidad o exceso de contexto deja error explícito, sin sustitución).
- Parámetros SLM: prompt `tarea`, hablantes `ab`, seed 42, temperatura 0.0, contexto 4096, lote 32, timeout 120.0 s, razonamiento desactivado cuando el runtime lo admite.
- GPU: NVIDIA GeForce RTX 3060 12288 MiB; servidor: 0.40.8 (/home/chato/.local/bin/ollama serve, OLLAMA_HOST=127.0.0.1:11435, OLLAMA_MODELS=/home/chato/.ollama/models).
- Intérprete de la corrida: `/home/chato/orca/workspaces/bitacora_tesis/searobin/.venv/bin/python`; librerías Tito: {'scikit-learn': '1.9.1', 'torch': '2.14.1+cpu', 'transformers': '5.20.2'}.
- Límites: sin segundos ni RTF: posiciones en lineas; ms por actualizacion medidos, no presupuesto movil; 8 conversaciones de desarrollo, sin test reservado.

## Carga, calentamiento y ajuste (por separado, no en el costo por línea)

- `llama3.2:1b-instruct-q4_K_M`: carga 1235 ms, memoria {'size_bytes': 938538434, 'size_vram_bytes': 938538434}, think=False.
- Tito (ajuste único, fuera de línea): incrustación 50666.3 ms, ajuste 321.4 ms, seed 42, sha fb601eaa8ecb…

## Límites de interpretación

- Casos escritos de desarrollo, sin revisión humana; posiciones en líneas, sin segundos ni RTF.
- La comparación mide activación selectiva + indicio falible juntos: no separa el efecto del indicio del efecto de la activación.
- El riesgo del SLM no está calibrado; el umbral 0,5 de Tito es convención exploratoria.
