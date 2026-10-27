# Comparación qwen3.5:0.8b: directo vs Tito→SLM

Corrida `2026-10-26_135640_qwen08b-comparacion` · Tito real (`real-robertuito-logreg`, umbral 0.5).
Mismas predicciones en ambas lecturas de marcas; la referencia original no cambia.

## Por conversación

| Caso | Clase | Deriv. | Aviso directo | Aviso filtrado | Cons. D/F | Evit. | Tokens D/F | Costo ms D/F |
|---|---|---|---|---|---|---|---|---|
| `LG-SUPPORT-INFO-01-e02` | legitima_dificil | 8 | — | — | 13/6 | 7 | 9077/5302 | 2338/1726 |
| `SC-FAMILIAR-DINERO-01-e01` | vishing | 9 | L8 | L9 | 12/4 | 8 | 8133/3942 | 3221/2962 |
| `SC-SOPORTE-REMOTO-01-e01` | vishing | 1 | L6 | L4 | 11/11 | 0 | 7804/9271 | 3378/5698 |
| `TR-04-pedido-tras-charla-larga` | vishing | 5 | L20 | L6 | 30/26 | 4 | 28154/29734 | 7211/17012 |
| `TR-06-banco-alerta-legitima` | legitima_dificil | 3 | — | L3 | 12/10 | 2 | 7784/8406 | 2105/5301 |
| `TR-07-pedido-partido-en-dos-lineas` | vishing | 5 | L9 | L5 | 10/6 | 4 | 6248/4922 | 2006/3341 |
| `TR-08-frase-cortada-candado` | legitima_dificil | 3 | L4 | — | 7/5 | 2 | 4116/3294 | 1837/1092 |
| `TR-11-familiar-real-pide-plata` | legitima_dificil | 9 | L9 | L9 | 10/2 | 8 | 6196/1728 | 2104/1288 |

Tokens totales (prompt+salida): directo 77512, filtrado 66599. Carga, calentamiento y ajuste van por separado abajo.

## Cambios de aviso entre variantes

- `SC-FAMILIAR-DINERO-01-e01`: directo L8 → filtrado L9, derivación L9 (indicio L9 p=0.576).
- `SC-SOPORTE-REMOTO-01-e01`: directo L6 → filtrado L4, derivación L1 (indicio L1 p=0.558).
- `TR-04-pedido-tras-charla-larga`: directo L20 → filtrado L6, derivación L5 (indicio L5 p=0.633).
- `TR-06-banco-alerta-legitima`: directo sin aviso → filtrado L3, derivación L3 (indicio L3 p=0.986).
- `TR-07-pedido-partido-en-dos-lineas`: directo L9 → filtrado L5, derivación L5 (indicio L5 p=0.994).
- `TR-08-frase-cortada-candado`: directo L4 → filtrado sin aviso, derivación L3.

## Doble lectura de marcas (mismas predicciones)

### `TR-04-pedido-tras-charla-larga`: referencia T_R=26/T_C=27, alternativa T_R=21/T_C=22
- directo (aviso L20): referencia → -6 líneas (antes del pedido L26); alternativa → -1 líneas (antes del pedido L21).
- filtrado (aviso L6): referencia → -20 líneas (antes del pedido L26); alternativa → -15 líneas (antes del pedido L21).

### `TR-07-pedido-partido-en-dos-lineas`: referencia T_R=7/T_C=9, alternativa T_R=8/T_C=9
- directo (aviso L9): referencia → +2 (en/después del cumplimiento L9); alternativa → +1 (en/después del cumplimiento L9).
- filtrado (aviso L5): referencia → -2 líneas (antes del pedido L7); alternativa → -3 líneas (antes del pedido L8).

## Motivos y citas (avisos anteriores al pedido incluidos)

Referencias provisorias: ningún caso tiene revisión humana; las lecturas de
pedido inventado o sospecha reforzada son del autor del reporte, no del manual.

- `SC-FAMILIAR-DINERO-01-e01` · directo · L8 — anterior al pedido (T_R L9): «Te están pidiendo un código de verificación o activación para acceder a tu cuenta bancaria.» — cita NO textual: «A: ¿Qué querés que haga yo? B: Choqué con el auto de papá y el señor del otro auto dice que si no le pago el arreglo ahora, hace la denuncia y me quedo sin registro. Estoy acá al lado de él.»
- `SC-FAMILIAR-DINERO-01-e01` · filtrado · L9: «Te están solicitando transferencias de dinero a una cuenta específica para un monto considerable (100 mil pesos), lo cual constituye un indicador claro de estafas telefónicas diseñadas para robar recursos.» — cita NO textual: «B: 'Son ciento ochenta mil pesos. ¿Me los podés transferir ahora a la cuenta del señor? Te paso los datos por mensaje y el lunes te los devuelvo.' A: 'Pero ¿qué querés que haga yo?' B: 'Son ciento ochenta mil pesos...' A: '¿Qué querés que haga yo?' B: 'Te paso los datos por mensaje y el lunes te los devuelvo.' A: 'Pero ¿qué querés que haga yo?'»
- `SC-SOPORTE-REMOTO-01-e01` · directo · L6: «Te están pidiendo un código de verificación o activación para anular un préstamo y obtener dinero.» — cita NO textual: «A: Todavía no salió, pero si no la frenamos ahora, la plata se va y el préstamo te queda a vos para pagarlo en cuotas. B: ¿Qué? Yo no pedí ningún préstamo. ¿Cómo lo freno? A: Yo desde acá no veo la aplicación como la ves vos. Te hago una videollamada, tocás «compartir pantalla» y te voy guiando para anular el préstamo.»
- `SC-SOPORTE-REMOTO-01-e01` · filtrado · L4 — anterior al pedido (T_R L6): «Te están solicitando un préstamo de dinero para pagar una transferencia que ya se ha realizado a otra cuenta bancaria.» — cita NO textual: «A: Buenas noches, te hablo del sector de préstamos del banco, mi nombre es Hernán Ibarra. ¿Sos el titular de la cuenta?\n2. B: Sí, soy yo. ¿Qué pasó?\n3. A: Hace un rato se pidió a tu nombre un préstamo de cuatrocientos cincuenta mil pesos, y ya quedó cargada una transferencia de esa plata a una cuenta de otro banco.\n4. A: Todavía no salió, pero si no la frenamos ahora, la plata se va y el préstamo te queda a vos para pagarlo en cuotas.»
- `TR-04-pedido-tras-charla-larga` · directo · L20 — anterior al pedido (T_R L26): «Te están solicitando un código de verificación para acceder a tu tarjeta de débito y cobrar su jubilación.» — cita textual: «A: Por eso te llamo. Estamos llamando uno por uno a los clientes de la sucursal por el recambio de las tarjetas de débito, que vencen a fin de año.»
- `TR-04-pedido-tras-charla-larga` · filtrado · L6 — anterior al pedido (T_R L26): «Te están solicitando un código de verificación o activación para acceder a tu cuenta bancaria. Esto es una estafa común que se utiliza para robar datos personales y fondos.» — cita textual: «A: Por eso te llamo. Estamos llamando uno por uno a los clientes de la sucursal por el recambio de las tarjetas de débito, que vencen a fin de año.»
- `TR-06-banco-alerta-legitima` · filtrado · L3: «El mensaje indica que Gastón es del área de seguridad de tarjetas y te llama por un consumo en tu tarjeta de crédito. Esto sugiere una posible estafa para robar datos personales o dinero.» — cita textual: «A: Te habla Gastón, del área de seguridad de tarjetas del banco. Te llamo por un consumo que nos llamó la atención en tu tarjeta de crédito.»
- `TR-07-pedido-partido-en-dos-lineas` · directo · L9: «Te están solicitando un código de verificación o desvinculación que podría permitirles robar tu cuenta bancaria.» — cita textual: «A: los seis números del mensaje del banco, así lo desvinculo antes de que te hagan una transferencia.»
- `TR-07-pedido-partido-en-dos-lineas` · filtrado · L5 — anterior al pedido (T_R L7): «El mensaje indica que el sistema te ha enviado un mensaje para desvincularlo, lo cual es una acción directa de seguridad guiada (abrir un enlace o cambiar una clave) que podría permitir robar datos personales o acceso a cuentas.» — cita NO textual: «E: El sistema te acaba de mandar un mensaje para desvincularlo.»
- `TR-08-frase-cortada-candado` · directo · L4: «Te están solicitando un código de acceso a una valija que me prestaste en el hotel para cerrarla sin pensar; esto es una acción directa de robo.» — cita textual: «A: Pasame el código del candado de la valija que me prestaste. La cerré sin pensar y ahora, en el hotel, no la puedo abrir.»
- `TR-11-familiar-real-pide-plata` · directo · L9: «Te están solicitando un código de verificación o activación para acceder a tu cuenta bancaria (cuenta de siempre) y pedirte transferir dinero.» — cita NO textual: «B: ¿Me podrás transferir veinte mil pesos? A: Sí, mi amor. ¿A qué cuenta? B: A la mía de siempre, la que tenés agendada. No hay apuro, eh: hoy o mañana, cuando puedas. El viernes cobro y te los devuelvo.»
- `TR-11-familiar-real-pide-plata` · filtrado · L9: «Te están solicitando un código de verificación o activación que permitiría acceder a tu cuenta bancaria sin verificar la identidad del interlocutor.» — cita NO textual: «B: ¿A qué cuenta? A: A la mía de siempre, la que tenés agendada. No hay apuro, eh: hoy o mañana, cuando puedas. El viernes cobro y te los devuelvo.»

## Runtime común y hardware

- Comando: `python correr.py --modelos qwen3.5:0.8b --url http://127.0.0.1:11435 --casos TR-04-pedido-tras-charla-larga,TR-06-banco-alerta-legitima,TR-07-pedido-partido-en-dos-lineas,TR-08-frase-cortada-candado,SC-SOPORTE-REMOTO-01-e01,LG-SUPPORT-INFO-01-e02,SC-FAMILIAR-DINERO-01-e01,TR-11-familiar-real-pide-plata --filtro-tito --tito-real --sin-reglas --num-batch 32 --etiqueta qwen08b-comparacion`
- Código: `d53bbc1858b3fa8fafc7cc2006a0f7d1f3bfce9d` (cambios sin commit en la carpeta: True)
- Ollama 0.40.8 en http://127.0.0.1:11435, digests: {'qwen3.5:0.8b': 'de63045f29755d4721c09d54c9b45c2dadb644f4fd7d604d4cac90d96049971c'}
- Chequeo previo de contrato JSON: `chequeo-contrato.json` en esta carpeta (digest verificado, `think: false`, esquema, `num_ctx` 4096 aceptados; una incompatibilidad o exceso de contexto deja error explícito, sin sustitución).
- Parámetros SLM: prompt `tarea`, hablantes `ab`, seed 42, temperatura 0.0, contexto 4096, lote 32, timeout 120.0 s, razonamiento desactivado cuando el runtime lo admite.
- GPU: NVIDIA GeForce RTX 3060 12288 MiB; servidor: 0.40.8 (/home/chato/.local/bin/ollama serve, OLLAMA_HOST=127.0.0.1:11435, OLLAMA_MODELS=/home/chato/.ollama/models).
- Intérprete de la corrida: `/home/chato/orca/workspaces/bitacora_tesis/searobin/.venv/bin/python`; librerías Tito: {'torch': '2.14.1+cpu', 'transformers': '5.20.2', 'scikit-learn': '1.9.1'}.
- Límites: sin segundos ni RTF: posiciones en líneas; ms por actualización medidos, no presupuesto móvil; 8 conversaciones de desarrollo, sin test reservado.

## Carga, calentamiento y ajuste (por separado, no en el costo por línea)

- `qwen3.5:0.8b`: carga 2471 ms, memoria {'size_bytes': 536954796, 'size_vram_bytes': 536954796}, think=False.
- Tito (ajuste único, fuera de línea): incrustación 50666.3 ms, ajuste 321.4 ms, seed 42, sha fb601eaa8ecb…

## Límites de interpretación

- Casos escritos de desarrollo, sin revisión humana; posiciones en líneas, sin segundos ni RTF.
- La comparación mide activación selectiva + indicio falible juntos: no separa el efecto del indicio del efecto de la activación.
- El riesgo del SLM no está calibrado; el umbral 0,5 de Tito es convención exploratoria.
