# Comparación qwen3.5:9b-q4_K_M: directo vs Tito→SLM

Corrida `2026-10-26_135930_qwen9b-comparacion` · Tito real (`real-robertuito-logreg`, umbral 0.5).
Mismas predicciones en ambas lecturas de marcas; la referencia original no cambia.

## Por conversación

| Caso | Clase | Deriv. | Aviso directo | Aviso filtrado | Cons. D/F | Evit. | Tokens D/F | Costo ms D/F |
|---|---|---|---|---|---|---|---|---|
| `LG-SUPPORT-INFO-01-e02` | legitima_dificil | 8 | — | — | 13/6 | 7 | 9105/5290 | 12744/7716 |
| `SC-FAMILIAR-DINERO-01-e01` | vishing | 9 | L9 | L9 | 12/4 | 8 | 8138/3795 | 16470/9319 |
| `SC-SOPORTE-REMOTO-01-e01` | vishing | 1 | L3 | L3 | 11/11 | 0 | 8294/9258 | 26557/27408 |
| `TR-04-pedido-tras-charla-larga` | vishing | 5 | L23 | L23 | 30/26 | 4 | 28365/28930 | 39862/58786 |
| `TR-06-banco-alerta-legitima` | legitima_dificil | 3 | L10 | L9 | 12/10 | 2 | 8052/7920 | 16488/16112 |
| `TR-07-pedido-partido-en-dos-lineas` | vishing | 5 | L4 | L5 | 10/6 | 4 | 6684/4845 | 19088/13131 |
| `TR-08-frase-cortada-candado` | legitima_dificil | 3 | L3 | L3 | 7/5 | 2 | 4030/3333 | 7524/6173 |
| `TR-11-familiar-real-pide-plata` | legitima_dificil | 9 | L4 | — | 10/2 | 8 | 6364/1574 | 14489/2858 |

Tokens totales (prompt+salida): directo 79032, filtrado 64945. Carga, calentamiento y ajuste van por separado abajo.

## Cambios de aviso entre variantes

- `TR-06-banco-alerta-legitima`: directo L10 → filtrado L9, derivación L3 (indicio L3 p=0.986).
- `TR-07-pedido-partido-en-dos-lineas`: directo L4 → filtrado L5, derivación L5 (indicio L5 p=0.994).
- `TR-11-familiar-real-pide-plata`: directo L4 → filtrado sin aviso, derivación L9.

## Doble lectura de marcas (mismas predicciones)

### `TR-04-pedido-tras-charla-larga`: referencia T_R=26/T_C=27, alternativa T_R=21/T_C=22
- directo (aviso L23): referencia → -3 líneas (antes del pedido L26); alternativa → +2 (en/después del cumplimiento L22).
- filtrado (aviso L23): referencia → -3 líneas (antes del pedido L26); alternativa → +2 (en/después del cumplimiento L22).

### `TR-07-pedido-partido-en-dos-lineas`: referencia T_R=7/T_C=9, alternativa T_R=8/T_C=9
- directo (aviso L4): referencia → -3 líneas (antes del pedido L7); alternativa → -4 líneas (antes del pedido L8).
- filtrado (aviso L5): referencia → -2 líneas (antes del pedido L7); alternativa → -3 líneas (antes del pedido L8).

## Motivos y citas (avisos anteriores al pedido incluidos)

Referencias provisorias: ningún caso tiene revisión humana; las lecturas de
pedido inventado o sospecha reforzada son del autor del reporte, no del manual.

- `SC-FAMILIAR-DINERO-01-e01` · directo · L9: «Te están pidiendo que hagas una transferencia de dinero a una cuenta extraña para pagar un arreglo de auto.» — cita textual: «Son ciento ochenta mil pesos. ¿Me los podés transferir ahora a la cuenta del señor? Te paso los datos por mensaje y el lunes te los devuelvo.»
- `SC-FAMILIAR-DINERO-01-e01` · filtrado · L9: «Te están pidiendo que transfieras dinero inmediatamente a una cuenta de terceros bajo amenaza y promesas falsas.» — cita textual: «Son ciento ochenta mil pesos. ¿Me los podés transferir ahora a la cuenta del señor? Te paso los datos por mensaje y el lunes te los devuelvo.»
- `SC-SOPORTE-REMOTO-01-e01` · directo · L3 — anterior al pedido (T_R L6): «Te están diciendo que ya te cargaron una transferencia sin pedirte códigos ni contraseñas, pero es una estafa clásica: no firmes nada ni des datos personales hasta verificar con tu banco real.» — cita textual: «A: Hace un rato se pidió a tu nombre un préstamo de cuatrocientos cincuenta mil pesos, y ya quedó cargada una transferencia de esa plata a una cuenta de otro banco.»
- `SC-SOPORTE-REMOTO-01-e01` · filtrado · L3 — anterior al pedido (T_R L6): «Te están diciendo que ya te cargaron una transferencia y piden confirmación o datos para 'regularizar' la situación.» — cita textual: «Hace un rato se pidió a tu nombre un préstamo de cuatrocientos cincuenta mil pesos, y ya quedó cargada una transferencia de esa plata a una cuenta de otro banco.»
- `TR-04-pedido-tras-charla-larga` · directo · L23 — anterior al pedido (T_R L26): «Te están pidiendo que leas o confirmes un código de verificación (mensajito) que te llega al celular para validar la operación.» — cita textual: «23. A: Perfecto. Ahora te va a llegar un mensajito del banco al celular para confirmar el envío. ¿Lo tenés a mano?»
- `TR-04-pedido-tras-charla-larga` · filtrado · L23 — anterior al pedido (T_R L26): «Te están pidiendo que le confirmes tu domicilio y te van a enviar un mensaje al celular para 'confirmar' el envío de la tarjeta; es una táctica clásica para validar tus datos personales y prepararte para pedirte códigos o instalar programas.» — cita textual: «21. A: Perfecto. Ahora te va a llegar un mensajito del banco al celular para confirmar el envío. ¿Lo tenés a mano?»
- `TR-06-banco-alerta-legitima` · directo · L10: «El estafador intenta recuperar tu confianza tras advertirte para luego pedirte un código de verificación que él mismo dice haber recibido, lo cual es una táctica clásica para obtener tus datos.» — cita textual: «10. B: Hace un rato me llegó un mensaje con un código. ¿Te lo paso así lo verificás?»
- `TR-06-banco-alerta-legitima` · filtrado · L9: «Te están indicando una acción específica (entrar a la app y tocar Pausar) para frenar el consumo sin verificar tu identidad primero, lo cual es una táctica común para presionarte a actuar bajo estrés antes de que te den más datos o intenten robarlos después.» — cita textual: «A: Antes que nada: no te voy a pedir ningún código, ni la clave, ni los números de la tarjeta. Si en algún momento alguien te los pide, cortá.
B: Bueno. ¿Y entonces cómo la freno?
A: Entrá a la aplicación del banco, en Tarjetas, y tocá Pausar. Eso la frena al instante.»
- `TR-07-pedido-partido-en-dos-lineas` · directo · L4 — anterior al pedido (T_R L7): «Te están indicando que hay un dispositivo vinculado desde otra provincia para generar urgencia y posiblemente pedirte datos o códigos.» — cita textual: «A: Esta mañana se vinculó un dispositivo nuevo a tu cuenta, desde otra provincia. ¿Fuiste vos?»
- `TR-07-pedido-partido-en-dos-lineas` · filtrado · L5 — anterior al pedido (T_R L7): «Te están creando urgencia falsa para que actúes rápido y te van a pedir un código o enlace para 'desvincular' el dispositivo.» — cita textual: «Todavía no pudieron operar, por eso te llamo ya. El sistema te acaba de mandar un mensaje para desvincularlo.»
- `TR-08-frase-cortada-candado` · directo · L3: «Te están pidiendo un código de verificación o acceso a tu cuenta sin haber establecido una identidad confiable.» — cita textual: «3. A: Pasame el código»
- `TR-08-frase-cortada-candado` · filtrado · L3: «Te están pidiendo directamente un código de verificación o acceso a tu cuenta bancaria.» — cita textual: «3. A: Pasame el código»
- `TR-11-familiar-real-pide-plata` · directo · L4: «Te están pidiendo que hagas una transferencia de dinero directamente por teléfono.» — cita textual: «B: Nada grave. Me vino más alta la boleta de la luz y no llego hasta el viernes. ¿Me podrás transferir veinte mil pesos?»

## Runtime común y hardware

- Comando: `python correr.py --modelos qwen3.5:9b-q4_K_M --url http://127.0.0.1:11435 --casos TR-04-pedido-tras-charla-larga,TR-06-banco-alerta-legitima,TR-07-pedido-partido-en-dos-lineas,TR-08-frase-cortada-candado,SC-SOPORTE-REMOTO-01-e01,LG-SUPPORT-INFO-01-e02,SC-FAMILIAR-DINERO-01-e01,TR-11-familiar-real-pide-plata --filtro-tito --tito-real --sin-reglas --num-batch 32 --etiqueta qwen9b-comparacion`
- Código: `d53bbc1858b3fa8fafc7cc2006a0f7d1f3bfce9d` (cambios sin commit en la carpeta: True)
- Ollama 0.40.8 en http://127.0.0.1:11435, digests: {'qwen3.5:9b-q4_K_M': '56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90'}
- Chequeo previo de contrato JSON: `chequeo-contrato.json` en esta carpeta (digest verificado, `think: false`, esquema, `num_ctx` 4096 aceptados; una incompatibilidad o exceso de contexto deja error explícito, sin sustitución).
- Parámetros SLM: prompt `tarea`, hablantes `ab`, seed 42, temperatura 0.0, contexto 4096, lote 32, timeout 120.0 s, razonamiento desactivado cuando el runtime lo admite.
- GPU: NVIDIA GeForce RTX 3060 12288 MiB; servidor: 0.40.8 (/home/chato/.local/bin/ollama serve, OLLAMA_HOST=127.0.0.1:11435, OLLAMA_MODELS=/home/chato/.ollama/models).
- Intérprete de la corrida: `/home/chato/orca/workspaces/bitacora_tesis/searobin/.venv/bin/python`; librerías Tito: {'torch': '2.14.1+cpu', 'transformers': '5.20.2', 'scikit-learn': '1.9.1'}.
- Límites: sin segundos ni RTF: posiciones en líneas; ms por actualización medidos, no presupuesto móvil; 8 conversaciones de desarrollo, sin test reservado.

## Carga, calentamiento y ajuste (por separado, no en el costo por línea)

- `qwen3.5:9b-q4_K_M`: carga 15151 ms, memoria {'size_bytes': 5502350130, 'size_vram_bytes': 5502350130}, think=False.
- Tito (ajuste único, fuera de línea): incrustación 50666.3 ms, ajuste 321.4 ms, seed 42, sha fb601eaa8ecb…

## Límites de interpretación

- Casos escritos de desarrollo, sin revisión humana; posiciones en líneas, sin segundos ni RTF.
- La comparación mide activación selectiva + indicio falible juntos: no separa el efecto del indicio del efecto de la activación.
- El riesgo del SLM no está calibrado; el umbral 0,5 de Tito es convención exploratoria.
