# Comparación qwen3.5:2b-q8_0: directo vs Tito→SLM

Corrida `2026-10-26_135746_qwen2b-q8-comparacion` · Tito real (`real-robertuito-logreg`, umbral 0.5).
Mismas predicciones en ambas lecturas de marcas; la referencia original no cambia.

## Por conversación

| Caso | Clase | Deriv. | Aviso directo | Aviso filtrado | Cons. D/F | Evit. | Tokens D/F | Costo ms D/F |
|---|---|---|---|---|---|---|---|---|
| `LG-SUPPORT-INFO-01-e02` | legitima_dificil | 8 | — | L12 | 13/6 | 7 | 9241/5427 | 6626/4374 |
| `SC-FAMILIAR-DINERO-01-e01` | vishing | 9 | L9 | L9 | 12/4 | 8 | 8069/3743 | 6528/3948 |
| `SC-SOPORTE-REMOTO-01-e01` | vishing | 1 | L6 | L6 | 11/11 | 0 | 7867/8734 | 7819/6922 |
| `TR-04-pedido-tras-charla-larga` | vishing | 5 | L26 | L26 | 30/26 | 4 | 28114/28296 | 15290/19159 |
| `TR-06-banco-alerta-legitima` | legitima_dificil | 3 | — | — | 12/10 | 2 | 7893/7738 | 5638/5088 |
| `TR-07-pedido-partido-en-dos-lineas` | vishing | 5 | L8 | L8 | 10/6 | 4 | 6387/4661 | 5639/3928 |
| `TR-08-frase-cortada-candado` | legitima_dificil | 3 | — | — | 7/5 | 2 | 4011/3308 | 3094/2354 |
| `TR-11-familiar-real-pide-plata` | legitima_dificil | 9 | — | — | 10/2 | 8 | 6167/1576 | 4404/1180 |

Tokens totales (prompt+salida): directo 77749, filtrado 63483. Carga, calentamiento y ajuste van por separado abajo.

## Cambios de aviso entre variantes

- `LG-SUPPORT-INFO-01-e02`: directo sin aviso → filtrado L12, derivación L8 (indicio L8 p=0.909).

## Doble lectura de marcas (mismas predicciones)

### `TR-04-pedido-tras-charla-larga`: referencia T_R=26/T_C=27, alternativa T_R=21/T_C=22
- directo (aviso L26): referencia → en el pedido; alternativa → +5 (en/después del cumplimiento L22).
- filtrado (aviso L26): referencia → en el pedido; alternativa → +5 (en/después del cumplimiento L22).

### `TR-07-pedido-partido-en-dos-lineas`: referencia T_R=7/T_C=9, alternativa T_R=8/T_C=9
- directo (aviso L8): referencia → +1 (después del pedido); alternativa → en el pedido.
- filtrado (aviso L8): referencia → +1 (después del pedido); alternativa → en el pedido.

## Motivos y citas (avisos anteriores al pedido incluidos)

Referencias provisorias: ningún caso tiene revisión humana; las lecturas de
pedido inventado o sospecha reforzada son del autor del reporte, no del manual.

- `LG-SUPPORT-INFO-01-e02` · filtrado · L12: «Te están pidiendo que compartas la pantalla para ver una actualización del banco» — cita textual: «"Bien. Cuando termine, abrila y contame qué te aparece en la pantalla. Todavía no pongas la clave."»
- `SC-FAMILIAR-DINERO-01-e01` · directo · L9: «Te están pidiendo transferir dinero de un monto alto (180k pesos) para pagar una reparación y te están ofreciendo datos personales para hacerlo.» — cita textual: «B: Son ciento ochenta mil pesos. ¿Me los podés transferir ahora a la cuenta del señor? Te paso los datos por mensaje y el lunes te los devuelvo.»
- `SC-FAMILIAR-DINERO-01-e01` · filtrado · L9: «Te están pidiendo transferir dinero ahora para arreglar un problema con el auto y te dan datos de pago» — cita textual: «Son ciento ochenta mil pesos. ¿Me los podés transferir ahora a la cuenta del señor? Te paso los datos por mensaje y el lunes te los devuelvo.»
- `SC-SOPORTE-REMOTO-01-e01` · directo · L6: «Te están pidiendo un código que da acceso a tu cuenta» — cita textual: «A: Todavía no salió, pero si no la frenamos ahora, la plata se va y el préstamo te queda a vos para pagarlo en cuotas.
B: ¿Qué? Yo no pedí ningún préstamo. ¿Cómo lo freno?
A: Yo desde acá no veo la aplicación como la ves vos. Te hago una videollamada, tocás «compartir pantalla» y te voy guiando para anular el préstamo.»
- `SC-SOPORTE-REMOTO-01-e01` · filtrado · L6: «Te están pidiendo un código que da acceso a tu cuenta» — cita textual: «A: Buenas noches, te hablo del sector de préstamos del banco, mi nombre es Hernán Ibarra. ¿Sos el titular de la cuenta?»
- `TR-04-pedido-tras-charla-larga` · directo · L26: «Te están pidiendo un código de verificación para activar una transferencia o pago inmediato» — cita textual: «"Bárbaro. Leeme el código que te llegó, así lo cargo y la tarjeta sale mañana mismo."»
- `TR-04-pedido-tras-charla-larga` · filtrado · L26: «Te están pidiendo un código de verificación para activar una transferencia o pago inmediato» — cita textual: «"Bárbaro. Leeme el código que te llegó, así lo cargo y la tarjeta sale mañana mismo."»
- `TR-07-pedido-partido-en-dos-lineas` · directo · L8: «Te están pidiendo un código de verificación que da acceso a tu cuenta» — cita textual: «A: Solamente pasame lo que te llegó
8. A: los seis números del mensaje del banco, así lo desvinculo antes de que te hagan una transferencia.»
- `TR-07-pedido-partido-en-dos-lineas` · filtrado · L8: «Te están pidiendo un código de verificación que da acceso a tu cuenta» — cita textual: «A: Solamente pasame lo que te llegó los seis números del mensaje del banco, así lo desvinculo antes de que te hagan una transferencia.»

## Runtime común y hardware

- Comando: `python correr.py --modelos qwen3.5:2b-q8_0 --url http://127.0.0.1:11435 --casos TR-04-pedido-tras-charla-larga,TR-06-banco-alerta-legitima,TR-07-pedido-partido-en-dos-lineas,TR-08-frase-cortada-candado,SC-SOPORTE-REMOTO-01-e01,LG-SUPPORT-INFO-01-e02,SC-FAMILIAR-DINERO-01-e01,TR-11-familiar-real-pide-plata --filtro-tito --tito-real --sin-reglas --num-batch 32 --etiqueta qwen2b-q8-comparacion`
- Código: `d53bbc1858b3fa8fafc7cc2006a0f7d1f3bfce9d` (cambios sin commit en la carpeta: True)
- Ollama 0.40.8 en http://127.0.0.1:11435, digests: {'qwen3.5:2b-q8_0': '0689d44085e06d165161a8a9a1731344278cfb5aade63a3c3dbdb48ab54b130a'}
- Chequeo previo de contrato JSON: `chequeo-contrato.json` en esta carpeta (digest verificado, `think: false`, esquema, `num_ctx` 4096 aceptados; una incompatibilidad o exceso de contexto deja error explícito, sin sustitución).
- Parámetros SLM: prompt `tarea`, hablantes `ab`, seed 42, temperatura 0.0, contexto 4096, lote 32, timeout 120.0 s, razonamiento desactivado cuando el runtime lo admite.
- GPU: NVIDIA GeForce RTX 3060 12288 MiB; servidor: 0.40.8 (/home/chato/.local/bin/ollama serve, OLLAMA_HOST=127.0.0.1:11435, OLLAMA_MODELS=/home/chato/.ollama/models).
- Intérprete de la corrida: `/home/chato/orca/workspaces/bitacora_tesis/searobin/.venv/bin/python`; librerías Tito: {'torch': '2.14.1+cpu', 'transformers': '5.20.2', 'scikit-learn': '1.9.1'}.
- Límites: sin segundos ni RTF: posiciones en líneas; ms por actualización medidos, no presupuesto móvil; 8 conversaciones de desarrollo, sin test reservado.

## Carga, calentamiento y ajuste (por separado, no en el costo por línea)

- `qwen3.5:2b-q8_0`: carga 1820 ms, memoria {'size_bytes': 2311051016, 'size_vram_bytes': 2311051016}, think=False.
- Tito (ajuste único, fuera de línea): incrustación 50666.3 ms, ajuste 321.4 ms, seed 42, sha fb601eaa8ecb…

## Límites de interpretación

- Casos escritos de desarrollo, sin revisión humana; posiciones en líneas, sin segundos ni RTF.
- La comparación mide activación selectiva + indicio falible juntos: no separa el efecto del indicio del efecto de la activación.
- El riesgo del SLM no está calibrado; el umbral 0,5 de Tito es convención exploratoria.
