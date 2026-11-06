> **Estado: borrador del 2026-11-03.** Reúne solo resultados de **desarrollo**, sin revisión humana. **La evaluación final sobre el test reservado (#52) no se corrió:** este capítulo se completa con ella. Todo número de aquí orienta decisiones y no estima el rendimiento del sistema.

# Capítulo 8: Resultados experimentales

## 8.1. Descripción del corpus

| Conjunto | Vishing | Legítimas | Total | Uso hasta hoy |
|---|---:|---:|---:|---|
| Antecedentes escritos | 29 | 24 | 53 | Desarrollo |
| Corpus v2, desarrollo | 46 | 51 | 97 | Desarrollo |
| Corpus v2, reserva | 100 | 100 | 200 | **Sin correr** |
| Diálogos con voz real | 3 guiones | 1 guion | 4 | 9 llamadas guionadas, 2 voces |

Corpus v2 es de redacción asistida, con [diseño y límites documentados](../../experiments/slm-directo/casos/DISENO-CORPUS-V2.md). Ninguno de los 350 casos escritos tiene `revision_humana` en verdadero, así que sus marcas son provisionales. De las 75 estafas de desarrollo, 10 terminan antes del pedido, y ningún detector las avisa.

**[Completar con la composición final, tras #54, #32, #55 y #45.]**

## 8.2. Reconocimiento de voz

### 8.2.1. Con voz real

Comparación offline de las dos opciones sobre el mismo audio, con 18 canales, 129 frases de referencia y dos voces ([resumen](../../experiments/asr-local/corridas/2026-11-02_voz-real_dialogos-a-contra-b/resumen.md)). El orden de los criterios se fijó antes de medir, en [§12.9 del plan](../../experiments/asr-local/PLAN-VOZ-REAL.md#129-dos-candidatos-para-comparar-en-diálogos-reales-2026-10-30).

| Criterio | **B · final** | A |
|---|---:|---:|
| Frases con las etiquetas correctas | 121/129 | 120/129 |
| Etiquetas nuevas en negativas | 0 | 0 |
| WER / CER | 25,6 % / 15,5 % | 32,8 % / 20,0 % |
| Recall de términos críticos | 70,9 % | 76,4 % |
| Recall de bancos y apps | 58,3 % | 50,0 % |
| Recall de jerga (informativo) | 10,0 % | 10,0 % |
| Demora de la frase final, mediana (p95) | 1,01 s (1,10) | 0,26 s (0,52) |
| Frases con palabras en otro idioma | 4 | 25 |
| Segmentos finales | 127 | 205 |
| RTF / memoria pico | 0,088 / 1.036 MB | 0,043 / 998 MB |

El WER se mide contra el guion y hubo palabras cambiadas al hablar: puede estar inflado y sirve para comparar A con B, no como valor absoluto. Con B, el canal de la otra persona, que llega por Meet y sin tele de fondo, da un WER de 32,9 % y un recall de términos críticos de 67,4 %. En el canal de Luciano sin tele, B recuperó 0 de los 2 términos críticos y A, 2 de 2: la muestra es muy chica para concluir, pero debe mirarse. El audio original se perdió el 2026-11-02, por lo que esta medición no se puede repetir con esos archivos.

### 8.2.2. Con audio sintético

Zipformer dio un WER de 4,35–5,00 % y Whisper, de 17,39 % sobre TTS ([comparación](../evaluacion/COMPARACION-CANDIDATOS-DESARROLLO.md#asr-sobre-audio-tts)). Con voz real, Zipformer resultó malo y se retiró: **el resultado con TTS no predijo el comportamiento con voz real**.

## 8.3. Comparación de detectores

### 8.3.1. Matriz #101: 10 modelos en 20 conversaciones

[Informe](../../experiments/slm-directo/corridas/2026-10-30_112956_101_informe_101.md). Son 10 estafas y 10 legítimas de desarrollo, separadas de lo usado para ajustar Tito, en un Ryzen 7 7700X con GPU, con 600 recorridos completos sobre el código `9fe43b5`, con cambios sin commit en la carpeta.

| Modelo | Directo (estafas · FA) | Con Tito viejo | Con Tito nuevo |
|---|---:|---:|---:|
| **`gemma4:e2b`** | 10/10 · 1/10 | **10/10 · 0/10** | 2/10 · 0/10 |
| `gemma4:e4b` | 10/10 · 1/10 | 10/10 · 1/10 | 3/10 · 0/10 |
| Los 10 modelos juntos | 90/100 · 48/100 | 82/100 · 27/100 | 23/100 · 0/100 |

Para E2B con Tito viejo, los intervalos de Wilson al 95 % son 72,2–100 % en estafas y 0–27,8 % en falsas alarmas. **Esos 20 casos sirvieron para elegir entre 10 modelos**, por lo que el valor es optimista.

**El filtro.** Con Tito viejo, E2B hizo 144 consultas al modelo contra 376 en directo, contando hasta el aviso. Tito derivó las 10 estafas y 5 de las 10 legítimas: las otras 5 no generaron ninguna consulta. El modelo descartó las 5 derivadas. Tito nuevo casi no deriva, y por eso pierde estafas.

### 8.3.2. Otras familias

| Candidato | Resultado | Fuente |
|---|---|---|
| Reglas | 23/29 · 14/24 sobre los 53 antecedentes | [Comparación](../evaluacion/COMPARACION-CANDIDATOS-DESARROLLO.md#tabla-maestra-de-detectores) |
| Qwen3.5 con prompt `tarea`, 97 de corpus v2 | 9B 40/46 · 10/51; 4B 39/46 · 8/51; 2B 22/46 · 6/51; 0.8B 40/46 · 46/51 | [Tablero](../../experiments/slm-directo/analisis/tablero/panel_plantilla.html) y [pasada 0](../../experiments/slm-directo/analisis/2026-10-21-pasada-0/) |
| Qwen3.5 con prompt `v2`, mismos casos | 9B 31/46 · 7/51; 4B 14/46 · 0/51 | Ídem. Se escribió mirando los 53 y no generalizó |
| bge-reranker-v2-m3 | 4/10 · 1/10 | [#123](https://github.com/Corchets/bitacora_tesis/issues/123) |
| Riesgo primero, `gemma3n:e2b` | 10/10 · 3–6/10, o 2/10 · 0/10 | [análisis del 2026-10-30](../../experiments/slm-directo/analisis/2026-10-30-reranker-zero-shot/README.md) |

La repetición de Qwen 2B en GPU, con igual configuración y seed 42, cambió la decisión en 2 de 53 casos: la inferencia no es exactamente repetible, y eso afecta a toda comparación por una sola corrida.

## 8.4. Texto manual frente a ASR (E1)

**Sin medir para la configuración final.** La única comparación disponible es la de octubre, con Qwen y Zipformer sobre un par TTS. **[Completar con #52: mismo detector sobre texto manual y ASR.]**

## 8.5. Detección temprana y latencia

### 8.5.1. Sobre texto, en líneas

Con E2B y Tito viejo, en #101, el aviso llegó en la línea del pedido en 8 de 10 estafas, una línea antes en 1 y tres líneas después en 1. En las 6 estafas con cumplimiento marcado, avisó antes de la línea de `T_C`. Las marcas son provisionales, y en texto no hay segundos.

### 8.5.2. Con voz real, en segundos

[Nueve llamadas guionadas por Meet](../../experiments/voip/corridas/2026-11-02-voz-real-meet.md), con Gemma 4 E2B y Tito viejo. La columna «Respecto del pedido» es la diferencia entre `T_A` y la primera frase con el pedido, **ubicada por palabras clave y no por anotación humana**: negativo significa que el aviso llegó antes.

| Llamada | Diálogo | ASR en vivo | `T_A` (s) | Respecto del pedido (s) | Consultas |
|---|---|---|---:|---:|---:|
| 1 | D1, estafa | B | 28,5 | −5,1 | 1 |
| 2 | D2, estafa | B | 34,5 | +3,2 | 5 |
| 3 | D3, legítima | B | sin aviso | | 11 |
| 4 | D4, estafa | B | 19,7 | +4,8 | 1 |
| 5 | D1 con tele, estafa | B | 32,6 | +4,0 | 2 |
| 6 | D1 con tele, estafa | A | 20,8 | −4,2 | 3 |
| 7 | D2, estafa | A | 34,7 | +2,1 | 4 |
| 8 | D3, legítima | A | sin aviso | | 17 |
| 9 | D4, estafa | A | 24,2 | +6,9 | 6 |

El aviso llegó en 7 de 7 estafas (Wilson: 64,6–100 %) y en 0 de 2 legítimas, que son el mismo guion. **Con B, el aviso llegó después de empezado el pedido en 3 de las 4 estafas.** En D1 puede llegar antes porque cita el débito, no el pedido del código: por eso no alcanza con leer `T_A`, hay que mirar qué frase cita.

Esto no mide rendimiento: son 4 guiones y 2 voces, y sin marcas `T_C` no hay `L_C`.

**[Completar con #52: `L_R`, `L_C` y `Preventive@δ` con marcas humanas.]**

### 8.5.3. Demora del detector

En 5 corridas de `SC-WA-CODE-01` con `medir.py` en la M1, E2B dio una mediana de **3,74 s** por consulta, mínimo de 2,04 s y p95 de 4,53 s, sin fallos ni frases salteadas. **No cumple el criterio de menos de 2 s**, aunque el aviso llegó entre −0,45 y +0,40 s respecto del fin del pedido. Es una medición con Zipformer, sin Chrome ni Meet. En las llamadas con voz real, las medianas por llamada fueron de 1,4 a 5,6 s.

## 8.6. Falsas alarmas y negativos difíciles

| Conjunto | Resultado de la configuración final |
|---|---|
| 10 legítimas de #101 | 0/10 (Wilson: 0–27,8 %) |
| D3 con voz real, mismo guion dos veces | 0/2 |
| `LG-SUPPORT-INFO-01` con TTS | Sin aviso |

La condición del tutor es que no salte por frases sueltas. D3 («amigos arreglando un cumple: palabras parecidas») se diseñó para eso, pero es un solo guion. **[Completar con #52, con el desglose entre legítimas cotidianas, con pedido razonable y con mención sin pedido.]**

## 8.7. Rendimiento y límites del hardware

Todas son mediciones en computadora; **ninguna en teléfono**.

| Dato | M1 de 8 GB |
|---|---|
| Parakeet con filtro | RTF 0,088; 1.036 MB de memoria pico |
| Tito viejo | Unos 30 ms por frase; 0,48 GB |
| Gemma 4 E2B | Archivo de 4,59 GB; 3,74 s de mediana por consulta |
| Conjunto | 28–30 % de memoria libre y 4,5–4,7 GB de swap en la medición |

La [corrida de E4B](../../experiments/voip/corridas/2026-11-02-tito-gemma4-panel.md) en la misma máquina dio 46,3 s y 15,8 s por evaluación, y avisó a +49,0 s del pedido. **[Sin ablaciones ni medición en Android.]**

## 8.8. Pendientes del capítulo

1. Correr el test reservado una sola vez con la configuración congelada (#33, #52).
2. E1, con el mismo detector sobre texto manual y ASR.
3. PI2 con marcas humanas.
4. E2, revisando motivos contra evidencia.
5. Sensibilidad de la precisión a la prevalencia.
6. Tablas y figuras regeneradas desde salidas crudas.
