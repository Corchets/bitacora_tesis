# Comparación qwen3.5:4b-q4_K_M: directo vs Tito→SLM

Corrida `2026-10-26_133838_qwen4b-comparacion` · Tito real (`real-robertuito-logreg`, umbral 0.5).
Mismas predicciones en ambas lecturas de marcas; la referencia original no cambia.

## Por conversación

| Caso | Clase | Deriv. | Aviso directo | Aviso filtrado | Cons. D/F | Evit. | Tokens D/F | Costo ms D/F |
|---|---|---|---|---|---|---|---|---|
| `LG-SUPPORT-INFO-01-e02` | legitima_dificil | 8 | — | L10 | 13/6 | 7 | 9112/5355 | 8020/5800 |
| `SC-FAMILIAR-DINERO-01-e01` | vishing | 9 | L9 | L9 | 12/4 | 8 | 8117/3784 | 10221/6557 |
| `SC-SOPORTE-REMOTO-01-e01` | vishing | 1 | L1 | L1 | 11/11 | 0 | 8088/9220 | 14704/20192 |
| `TR-04-pedido-tras-charla-larga` | vishing | 5 | L3 | L5 | 30/26 | 4 | 28404/29600 | 26461/46805 |
| `TR-06-banco-alerta-legitima` | legitima_dificil | 3 | L3 | L3 | 12/10 | 2 | 8115/8145 | 12063/13200 |
| `TR-07-pedido-partido-en-dos-lineas` | vishing | 5 | L3 | L5 | 10/6 | 4 | 6591/4839 | 11158/10082 |
| `TR-08-frase-cortada-candado` | legitima_dificil | 3 | L3 | L3 | 7/5 | 2 | 4113/3505 | 6033/7541 |
| `TR-11-familiar-real-pide-plata` | legitima_dificil | 9 | L4 | L9 | 10/2 | 8 | 6360/1679 | 9310/3137 |

Tokens totales (prompt+salida): directo 78900, filtrado 66127. Carga, calentamiento y ajuste van por separado abajo.

## Cambios de aviso entre variantes

- `LG-SUPPORT-INFO-01-e02`: directo sin aviso → filtrado L10, derivación L8 (indicio L8 p=0.909).
- `TR-04-pedido-tras-charla-larga`: directo L3 → filtrado L5, derivación L5 (indicio L5 p=0.633).
- `TR-07-pedido-partido-en-dos-lineas`: directo L3 → filtrado L5, derivación L5 (indicio L5 p=0.994).
- `TR-11-familiar-real-pide-plata`: directo L4 → filtrado L9, derivación L9 (indicio L9 p=0.987).

## Doble lectura de marcas (mismas predicciones)

### `TR-04-pedido-tras-charla-larga`: referencia T_R=26/T_C=27, alternativa T_R=21/T_C=22
- directo (aviso L3): referencia → -23 líneas (antes del pedido L26); alternativa → -18 líneas (antes del pedido L21).
- filtrado (aviso L5): referencia → -21 líneas (antes del pedido L26); alternativa → -16 líneas (antes del pedido L21).

### `TR-07-pedido-partido-en-dos-lineas`: referencia T_R=7/T_C=9, alternativa T_R=8/T_C=9
- directo (aviso L3): referencia → -4 líneas (antes del pedido L7); alternativa → -5 líneas (antes del pedido L8).
- filtrado (aviso L5): referencia → -2 líneas (antes del pedido L7); alternativa → -3 líneas (antes del pedido L8).

## Motivos y citas (avisos anteriores al pedido incluidos)

Referencias provisorias: ningún caso tiene revisión humana; las lecturas de
pedido inventado o sospecha reforzada son del autor del reporte, no del manual.

- `LG-SUPPORT-INFO-01-e02` · filtrado · L10: «Te están pidiendo que abras la aplicación bancaria para ver qué te aparece en pantalla.» — cita textual: «Bien. Cuando termine, abrila y contame qué te aparece en la pantalla.»
- `SC-FAMILIAR-DINERO-01-e01` · directo · L9: «Te están pidiendo transferir dinero urgente bajo amenaza de denuncia» — cita textual: «Son ciento ochenta mil pesos. ¿Me los podés transferir ahora a la cuenta del señor? Te paso los datos por mensaje y el lunes te los devuelvo.»
- `SC-FAMILIAR-DINERO-01-e01` · filtrado · L9: «Te están pidiendo transferir dinero inmediatamente por un problema inventado.» — cita textual: «Son ciento ochenta mil pesos. ¿Me los podés transferir ahora a la cuenta del señor? Te paso los datos por mensaje y el lunes te los devuelvo.»
- `SC-SOPORTE-REMOTO-01-e01` · directo · L1 — anterior al pedido (T_R L6): «Te están simulando ser del banco para pedir si sos titular de la cuenta» — cita textual: «Buenas noches, te hablo del sector de préstamos del banco, mi nombre es Hernán Ibarra. ¿Sos el titular de la cuenta?»
- `SC-SOPORTE-REMOTO-01-e01` · filtrado · L1 — anterior al pedido (T_R L6): «Te están simulando ser del banco para verificar tu identidad y pedir datos sensibles.» — cita textual: «Buenas noches, te hablo del sector de préstamos del banco, mi nombre es Hernán Ibarra. ¿Sos el titular de la cuenta?»
- `TR-04-pedido-tras-charla-larga` · directo · L3 — anterior al pedido (T_R L26): «Te están simulando ser del banco para pedir datos de tu cuenta» — cita textual: «Te llamo de la sucursal del banco donde cobrás la jubilación, la de la avenida, al lado de la farmacia. Me llamo Silvina.»
- `TR-04-pedido-tras-charla-larga` · filtrado · L5 — anterior al pedido (T_R L26): «Te están simulando ser del banco para ofrecerte recambiar tu tarjeta de débito.» — cita textual: «Por eso te llamo. Estamos llamando uno por uno a los clientes de la sucursal por el recambio de las tarjetas de débito, que vencen a fin de año.»
- `TR-06-banco-alerta-legitima` · directo · L3: «Te están simulando ser del banco para pedirte datos de tu tarjeta por un consumo sospechoso» — cita textual: «Te habla Gastón, del área de seguridad de tarjetas del banco. Te llamo por un consumo que nos llamó la atención en tu tarjeta de crédito.»
- `TR-06-banco-alerta-legitima` · filtrado · L3: «Te están fingiendo ser del banco para pedirle información sensible sobre su tarjeta de crédito» — cita textual: «Te habla Gastón, del área de seguridad de tarjetas del banco. Te llamo por un consumo que nos llamó la atención en tu tarjeta de crédito.»
- `TR-07-pedido-partido-en-dos-lineas` · directo · L3 — anterior al pedido (T_R L7): «Te están pidiendo información sobre un nuevo dispositivo vinculado a tu cuenta para verificar tu identidad.» — cita textual: «Esta mañana se vinculó un dispositivo nuevo a tu cuenta, desde otra provincia. ¿Fuiste vos?»
- `TR-07-pedido-partido-en-dos-lineas` · filtrado · L5 — anterior al pedido (T_R L7): «Te están pidiendo desvincular un dispositivo y mencionan que te enviaron un mensaje para ello.» — cita NO textual: «Esta mañana se vinculó un dispositivo nuevo a tu cuenta, desde otra provincia. ¿Fuiste vos? ... Todavía no pudieron operar, por eso te llamo ya. El sistema te acaba de mandar un mensaje para desvincularlo.»
- `TR-08-frase-cortada-candado` · directo · L3: «Te están pidiendo un código de acceso a tu cuenta o servicio» — cita textual: «Pasame el código»
- `TR-08-frase-cortada-candado` · filtrado · L3: «Te están pidiendo un código de acceso a tu cuenta o servicio» — cita textual: «Pasame el código»
- `TR-11-familiar-real-pide-plata` · directo · L4: «Te están pidiendo dinero bajo una excusa falsa sobre un recibo de luz.» — cita textual: «Me vino más alta la boleta de la luz y no llego hasta el viernes. ¿Me podrás transferir veinte mil pesos?»
- `TR-11-familiar-real-pide-plata` · filtrado · L9: «Te están pidiendo dinero bajo la excusa de una factura de luz y te instan a transferir ahora.» — cita textual: «"Me vino más alta la boleta de la luz y no llego hasta el viernes. ¿Me podrás transferir veinte mil pesos?"»

## Runtime común y hardware

- Comando: `python correr.py --modelos qwen3.5:4b-q4_K_M --url http://127.0.0.1:11435 --casos TR-04-pedido-tras-charla-larga,TR-06-banco-alerta-legitima,TR-07-pedido-partido-en-dos-lineas,TR-08-frase-cortada-candado,SC-SOPORTE-REMOTO-01-e01,LG-SUPPORT-INFO-01-e02,SC-FAMILIAR-DINERO-01-e01,TR-11-familiar-real-pide-plata --filtro-tito --tito-real --sin-reglas --num-batch 32 --etiqueta qwen4b-comparacion --detalle`
- Código: `d53bbc1858b3fa8fafc7cc2006a0f7d1f3bfce9d` (cambios sin commit en la carpeta: True)
- Ollama 0.40.8 en http://127.0.0.1:11435, digests: {'qwen3.5:4b-q4_K_M': 'd8b0f5e9760cd1682034f292d7ef72ec46f432149be0df7574bf2d6e92e38c04'}
- Chequeo previo de contrato JSON: `chequeo-contrato.json` en esta carpeta (digest verificado, `think: false`, esquema, `num_ctx` 4096 aceptados; una incompatibilidad o exceso de contexto deja error explícito, sin sustitución).
- Parámetros SLM: prompt `tarea`, hablantes `ab`, seed 42, temperatura 0.0, contexto 4096, lote 32, timeout 120.0 s, razonamiento desactivado cuando el runtime lo admite.
- GPU: NVIDIA GeForce RTX 3060 12288 MiB; servidor: 0.40.8 (/home/chato/.local/bin/ollama serve, OLLAMA_HOST=127.0.0.1:11435, OLLAMA_MODELS=/home/chato/.ollama/models).
- Intérprete de la corrida: `/home/chato/orca/workspaces/bitacora_tesis/searobin/.venv/bin/python`; librerías Tito: {'torch': '2.14.1+cpu', 'transformers': '5.20.2', 'scikit-learn': '1.9.1'}.
- Límites: sin segundos ni RTF: posiciones en líneas; ms por actualización medidos, no presupuesto móvil; 8 conversaciones de desarrollo, sin test reservado.

## Carga, calentamiento y ajuste (por separado, no en el costo por línea)

- `qwen3.5:4b-q4_K_M`: carga 221 ms, memoria {'size_bytes': 3067179170, 'size_vram_bytes': 3067179170}, think=False.
- Tito (ajuste único, fuera de línea): incrustación 50666.3 ms, ajuste 321.4 ms, seed 42, sha fb601eaa8ecb…

## Límites de interpretación

- Casos escritos de desarrollo, sin revisión humana; posiciones en líneas, sin segundos ni RTF.
- La comparación mide activación selectiva + indicio falible juntos: no separa el efecto del indicio del efecto de la activación.
- El riesgo del SLM no está calibrado; el umbral 0,5 de Tito es convención exploratoria.
