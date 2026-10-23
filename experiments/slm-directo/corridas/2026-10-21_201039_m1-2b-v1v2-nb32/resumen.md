# Resumen de la corrida `2026-10-21_201039_m1-2b-v1v2-nb32`

> Material de **desarrollo** del ensayo [#50](https://github.com/Corchets/bitacora_tesis/issues/50):
> casos escritos, no grabaciones ni test final. Las posiciones son líneas, no segundos.
> El riesgo del SLM no está calibrado y no es una probabilidad. No elige modelo (D09) ni política (D08).

- **Comando:** `python correr.py --modelos qwen3.5:2b-q8_0 --prompts tarea,v2 --num-batch 32 --sin-reglas --etiqueta m1-2b-v1v2-nb32`
- **Inicio / fin:** 2026-10-21T20:10:39 / 2026-10-21T23:38:10
- **Código:** `6bfac9ae23` con cambios sin commit en la carpeta
- **Máquina:** macOS-27.0.1-arm64-arm-64bit, 8 núcleos lógicos, 8.0 GB de RAM
- **Ollama:** 0.40.5 · **Política:** aviso_unico_primer_true_valido
- **Casos:** 150 (75 vishing, 75 legítimas); 150 todavía sin revisión humana

## Resultados por configuración

| Configuración | Vishing con aviso | Antes del pedido | En el pedido | Después del pedido | En/después del cumplimiento | Falsas alarmas | Fallos | ms p50 | ms p95 | Evidencia textual | Sin evaluar |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `slm\|qwen3.5:2b-q8_0\|tarea\|ab` | 42/75 | 12 | 22 | 6 | 2 | 8/75 | 0/2773 | 1.875 | 4.481 | 45/50 | 0 |
| `slm\|qwen3.5:2b-q8_0\|v2\|ab` | 47/75 | 15 | 27 | 5 | 0 | 15/75 | 0/2773 | 1.786 | 4.293 | 61/62 | 0 |

«Sin evaluar» son casos cortados o sin ninguna respuesta válida: no se cuentan en las demás columnas. «Antes del pedido» cuenta avisos previos a `T_R`; en vishing sin pedido de referencia el aviso se cuenta solo en «Vishing con aviso». «Evidencia textual» cuenta avisos cuya cita aparece en el texto disponible.

## Caso por caso

Configuraciones: **C1** `slm\|qwen3.5:2b-q8_0\|tarea\|ab` · **C2** `slm\|qwen3.5:2b-q8_0\|v2\|ab`

`=R` aviso en la línea del pedido (`T_R`) · `<R` antes del pedido · `>R` después del pedido y antes del cumplimiento · `≥C` en o después del cumplimiento (`T_C`) · `FA` falsa alarma en una legítima · `ok` legítima sin aviso · `—` vishing sin aviso · `…` sin evaluar: la corrida se cortó antes de terminar el caso · `x` sin evaluar: ninguna respuesta válida · `(xN)` N actualizaciones fallidas en el caso.

| Caso | Clase | T_R | T_C | C1 | C2 |
|---|---|---|---|---|---|
| `CV2-D-L-BANCO-001` | legítima | — | — | FA L12 | FA L12 |
| `CV2-D-L-BANCO-002` | legítima | — | — | FA L11 | FA L11 |
| `CV2-D-L-BANCO-003` | legítima | — | — | ok | ok |
| `CV2-D-L-BANCO-004` | legítima | — | — | ok | ok |
| `CV2-D-L-BANCO-005` | legítima | — | — | FA L9 | FA L8 |
| `CV2-D-L-BANCO-006` | legítima | — | — | ok | ok |
| `CV2-D-L-BANCO-007` | legítima | — | — | ok | ok |
| `CV2-D-L-BANCO-008` | legítima | — | — | ok | ok |
| `CV2-D-L-BANCO-009` | legítima | — | — | ok | ok |
| `CV2-D-L-BANCO-010` | legítima | — | — | FA L12 | FA L12 |
| `CV2-D-L-DELIVERY-001` | legítima | — | — | ok | ok |
| `CV2-D-L-DELIVERY-002` | legítima | — | — | ok | ok |
| `CV2-D-L-DELIVERY-003` | legítima | — | — | ok | ok |
| `CV2-D-L-DELIVERY-004` | legítima | — | — | ok | ok |
| `CV2-D-L-DELIVERY-005` | legítima | — | — | ok | ok |
| `CV2-D-L-ESCUELA-001` | legítima | — | — | ok | ok |
| `CV2-D-L-ESCUELA-002` | legítima | — | — | ok | ok |
| `CV2-D-L-ESCUELA-003` | legítima | — | — | ok | ok |
| `CV2-D-L-ESCUELA-004` | legítima | — | — | ok | ok |
| `CV2-D-L-ESCUELA-005` | legítima | — | — | ok | ok |
| `CV2-D-L-FAMILIAR-001` | legítima | — | — | ok | ok |
| `CV2-D-L-FAMILIAR-002` | legítima | — | — | FA L13 | FA L8 |
| `CV2-D-L-FAMILIAR-003` | legítima | — | — | ok | ok |
| `CV2-D-L-FAMILIAR-004` | legítima | — | — | ok | ok |
| `CV2-D-L-FAMILIAR-005` | legítima | — | — | ok | FA L8 |
| `CV2-D-L-MEDICO-001` | legítima | — | — | ok | ok |
| `CV2-D-L-MEDICO-002` | legítima | — | — | ok | FA L16 |
| `CV2-D-L-MEDICO-003` | legítima | — | — | ok | ok |
| `CV2-D-L-MEDICO-004` | legítima | — | — | ok | ok |
| `CV2-D-L-MEDICO-005` | legítima | — | — | ok | ok |
| `CV2-D-L-ORGANISMO_PREVISIONAL-001` | legítima | — | — | ok | ok |
| `CV2-D-L-ORGANISMO_PREVISIONAL-002` | legítima | — | — | ok | ok |
| `CV2-D-L-ORGANISMO_PREVISIONAL-003` | legítima | — | — | ok | ok |
| `CV2-D-L-PREMIO-001` | legítima | — | — | ok | ok |
| `CV2-D-L-PREMIO-002` | legítima | — | — | ok | ok |
| `CV2-D-L-PREMIO-003` | legítima | — | — | ok | ok |
| `CV2-D-L-SOPORTE-001` | legítima | — | — | ok | ok |
| `CV2-D-L-SOPORTE-002` | legítima | — | — | ok | FA L8 |
| `CV2-D-L-SOPORTE-003` | legítima | — | — | ok | ok |
| `CV2-D-L-SOPORTE-004` | legítima | — | — | ok | FA L11 |
| `CV2-D-L-SOPORTE-005` | legítima | — | — | ok | FA L10 |
| `CV2-D-L-TRABAJO-001` | legítima | — | — | FA L21 | FA L21 |
| `CV2-D-L-TRABAJO-002` | legítima | — | — | ok | ok |
| `CV2-D-L-TRABAJO-003` | legítima | — | — | ok | ok |
| `CV2-D-L-TRABAJO-004` | legítima | — | — | ok | ok |
| `CV2-D-L-TRABAJO-005` | legítima | — | — | ok | ok |
| `CV2-D-L-WHATSAPP-001` | legítima | — | — | ok | ok |
| `CV2-D-L-WHATSAPP-002` | legítima | — | — | ok | ok |
| `CV2-D-L-WHATSAPP-003` | legítima | — | — | ok | ok |
| `CV2-D-L-WHATSAPP-004` | legítima | — | — | ok | ok |
| `CV2-D-L-WHATSAPP-005` | legítima | — | — | ok | ok |
| `CV2-D-V-BANCO-001` | vishing | 32 | — | <R L29 | <R L26 |
| `CV2-D-V-BANCO-002` | vishing | 18 | 27 | >R L20 | <R L11 |
| `CV2-D-V-BANCO-003` | vishing | 19 | 26 | <R L14 | <R L14 |
| `CV2-D-V-BANCO-004` | vishing | 16 | 21 | <R L10 | <R L8 |
| `CV2-D-V-BANCO-005` | vishing | 19 | — | <R L11 | <R L11 |
| `CV2-D-V-BANCO-006` | vishing | 14 | — | <R L10 | <R L10 |
| `CV2-D-V-BANCO-007` | vishing | 17 | 26 | =R L17 | =R L17 |
| `CV2-D-V-BANCO-008` | vishing | 16 | — | — | — |
| `CV2-D-V-BANCO-009` | vishing | 13 | — | <R L12 | =R L13 |
| `CV2-D-V-BANCO-010` | vishing | 13 | — | — | — |
| `CV2-D-V-BANCO-011` | vishing | — | — | — | — |
| `CV2-D-V-BANCO-012` | vishing | — | — | — | — |
| `CV2-D-V-FAMILIAR-001` | vishing | 15 | 20 | =R L15 | =R L15 |
| `CV2-D-V-FAMILIAR-002` | vishing | 16 | 27 | =R L16 | =R L16 |
| `CV2-D-V-FAMILIAR-003` | vishing | 15 | — | — | <R L14 |
| `CV2-D-V-FAMILIAR-004` | vishing | 22 | — | — | — |
| `CV2-D-V-FAMILIAR-005` | vishing | 20 | — | — | — |
| `CV2-D-V-FAMILIAR-006` | vishing | 22 | — | =R L22 | — |
| `CV2-D-V-ORGANISMO_PREVISIONAL-001` | vishing | 12 | 19 | — | =R L12 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-002` | vishing | 9 | 10 | — | — |
| `CV2-D-V-ORGANISMO_PREVISIONAL-003` | vishing | 11 | — | — | — |
| `CV2-D-V-ORGANISMO_PREVISIONAL-004` | vishing | 14 | — | — | — |
| `CV2-D-V-ORGANISMO_PREVISIONAL-005` | vishing | — | — | — | — |
| `CV2-D-V-ORGANISMO_PREVISIONAL-006` | vishing | — | — | — | — |
| `CV2-D-V-PREMIO-001` | vishing | 10 | 13 | — | =R L10 |
| `CV2-D-V-PREMIO-002` | vishing | 13 | 16 | =R L13 | >R L14 |
| `CV2-D-V-PREMIO-003` | vishing | 13 | — | — | — |
| `CV2-D-V-PREMIO-004` | vishing | 14 | — | >R L15 | =R L14 |
| `CV2-D-V-PREMIO-005` | vishing | — | — | — | — |
| `CV2-D-V-PREMIO-006` | vishing | — | — | — | — |
| `CV2-D-V-SOPORTE-001` | vishing | 14 | — | >R L15 | >R L15 |
| `CV2-D-V-SOPORTE-002` | vishing | 13 | 20 | =R L13 | =R L13 |
| `CV2-D-V-SOPORTE-003` | vishing | 11 | 18 | <R L10 | <R L10 |
| `CV2-D-V-SOPORTE-004` | vishing | 14 | — | — | — |
| `CV2-D-V-SOPORTE-005` | vishing | 16 | — | — | — |
| `CV2-D-V-SOPORTE-006` | vishing | 15 | — | <R L10 | <R L10 |
| `CV2-D-V-SOPORTE-007` | vishing | — | — | — | — |
| `CV2-D-V-SOPORTE-008` | vishing | — | — | — | — |
| `CV2-D-V-WHATSAPP-001` | vishing | 9 | 20 | =R L9 | =R L9 |
| `CV2-D-V-WHATSAPP-002` | vishing | 10 | — | >R L13 | =R L10 |
| `CV2-D-V-WHATSAPP-003` | vishing | 12 | 19 | ≥C L21 | — |
| `CV2-D-V-WHATSAPP-004` | vishing | 13 | — | — | — |
| `CV2-D-V-WHATSAPP-005` | vishing | 14 | — | <R L13 | <R L13 |
| `CV2-D-V-WHATSAPP-006` | vishing | 25 | 31 | <R L24 | =R L25 |
| `CV2-D-V-WHATSAPP-007` | vishing | — | — | — | — |
| `CV2-D-V-WHATSAPP-008` | vishing | — | — | — | — |
| `LAB-acceso-remoto` | vishing | 3 | — | =R L3 | =R L3 |
| `LAB-acceso-remoto-parafrasis` | vishing | 3 | — | =R L3 | =R L3 |
| `LAB-anses-beneficio` | vishing | 3 | — | =R L3 | =R L3 |
| `LAB-anses-beneficio-parafrasis` | vishing | 3 | — | =R L3 | >R L5 |
| `LAB-anses-canal-oficial` | legítima | — | — | ok | ok |
| `LAB-arca-canal-oficial` | legítima | — | — | ok | ok |
| `LAB-arca-deuda` | vishing | 3 | — | — | =R L3 |
| `LAB-arca-deuda-parafrasis` | vishing | 3 | — | — | — |
| `LAB-banco-app-parafrasis` | legítima | — | — | ok | ok |
| `LAB-banco-codigo` | vishing | 5 | 6 | <R L3 | <R L3 |
| `LAB-banco-codigo-parafrasis` | vishing | 5 | 6 | =R L5 | =R L5 |
| `LAB-banco-gasto-sin-pedido` | legítima | — | — | ok | ok |
| `LAB-banco-niega-el-codigo` | legítima | — | — | ok | ok |
| `LAB-banco-numeros-sin-clave` | vishing | 5 | 6 | =R L5 | =R L5 |
| `LAB-banco-revisa-app` | legítima | — | — | ok | ok |
| `LAB-digitos-sin-palabra` | vishing | 5 | — | — | — |
| `LAB-familiar-llama-vos` | legítima | — | — | ok | ok |
| `LAB-familiar-peligro` | vishing | 4 | — | =R L4 | =R L4 |
| `LAB-familiar-peligro-parafrasis` | vishing | 4 | — | — | >R L6 |
| `LAB-giro-sin-plata` | vishing | 3 | — | — | =R L3 |
| `LAB-mensajeria-no-pases-nada` | legítima | — | — | ok | ok |
| `LAB-no-bajes-nada` | legítima | — | — | ok | ok |
| `LAB-pantalla-sin-programa` | vishing | 3 | — | — | — |
| `LAB-portero-codigo-puerta` | legítima | — | — | ok | ok |
| `LAB-whatsapp-codigo` | vishing | 3 | 4 | <R L1 | =R L3 |
| `LAB-whatsapp-codigo-parafrasis` | vishing | 3 | 4 | =R L3 | =R L3 |
| `LG-BANK-VERIF-01-e01` | legítima | — | — | ok | FA L4 |
| `LG-FAMILIAR-LLAMADO-01-e01` | legítima | — | — | ok | ok |
| `LG-ORG-TURNO-01-e01` | legítima | — | — | ok | ok |
| `LG-PREMIO-CONSULTA-01-e01` | legítima | — | — | ok | ok |
| `LG-SUPPORT-INFO-01-e01` | legítima | — | — | ok | ok |
| `LG-SUPPORT-INFO-01-e02` | legítima | — | — | ok | ok |
| `LG-WA-CONSULTA-01-e01` | legítima | — | — | ok | ok |
| `SC-CLAVE-CAMBIO-01-e01` | vishing | 9 | 12 | =R L9 | =R L9 |
| `SC-FAMILIAR-DINERO-01-e01` | vishing | 9 | — | =R L9 | =R L9 |
| `SC-ORG-BENEFICIO-01-e01` | vishing | 7 | 8 | — | =R L7 |
| `SC-PREMIO-01-e01` | vishing | 8 | 13 | =R L8 | =R L8 |
| `SC-SOPORTE-CLAVE-01-e01` | vishing | 6 | 11 | =R L6 | <R L5 |
| `SC-SOPORTE-REMOTO-01-e01` | vishing | 6 | — | =R L6 | <R L3 |
| `SC-WA-CODE-01-e01` | vishing | 4 | 5 | =R L4 | =R L4 |
| `TR-01-pedido-indirecto-digitos` | vishing | 8 | 11 | — | — |
| `TR-02-codigo-del-candado` | legítima | — | — | ok | ok |
| `TR-03-negacion-y-consejo` | legítima | — | — | FA L7 | FA L5 |
| `TR-04-pedido-tras-charla-larga` | vishing | 26 | 27 | =R L26 | <R L25 |
| `TR-05-asado-con-transferencia` | legítima | — | — | FA L14 | FA L13 |
| `TR-06-banco-alerta-legitima` | legítima | — | — | ok | ok |
| `TR-07-pedido-partido-en-dos-lineas` | vishing | 7 | 9 | >R L8 | >R L8 |
| `TR-08-frase-cortada-candado` | legítima | — | — | ok | ok |
| `TR-09-victima-se-niega` | vishing | 5 | — | >R L6 | =R L5 |
| `TR-10-ofrecimiento-inducido` | vishing | 8 | 13 | ≥C L14 | <R L4 |
| `TR-11-familiar-real-pide-plata` | legítima | — | — | ok | ok |
| `TR-12-corta-antes-del-pedido` | vishing | — | — | — | — |
| `TR-13-turno-medico-pide-dni` | legítima | — | — | ok | FA L5 |

## Para revisar

### Falsas alarmas

- `CV2-D-L-BANCO-001` · `slm|qwen3.5:2b-q8_0|tarea|ab` · línea 12: «Te están pidiendo un código de verificación o confirmación para una posible transferencia o pago que no estás autorizando.» — evidencia (cita textual): «12. B: entonces cargo el desconocimiento por el importe completo te voy a pedir que confirmes el nombre que figura como titular»
- `CV2-D-L-BANCO-002` · `slm|qwen3.5:2b-q8_0|tarea|ab` · línea 11: «Te están pidiendo un código de verificación o una clave para confirmar tu identidad y autorizar la transferencia» — evidencia (cita NO textual): «A: ¿La transferencia la hiciste a un alias o a un contacto guardado? B: A un alias que me pasó la ceramista, algo como taller.luna. No sé si quedó bien escrito.
A: Veo una operación por 32.500 con un alias terminado en luna. ¿Te suena el nombre de destino, Eva Montal?»
- `CV2-D-L-BANCO-005` · `slm|qwen3.5:2b-q8_0|tarea|ab` · línea 9: «Te están pidiendo un código de verificación para confirmar movimientos recientes» — evidencia (cita NO textual): «B: ¿Los dos movimientos tienen el mismo importe? A: Sí, 145.000 cada uno... B: Para encontrar la cuenta, me confirmás los últimos cuatro dígitos, por favor. A: 7210.»
- `CV2-D-L-BANCO-010` · `slm|qwen3.5:2b-q8_0|tarea|ab` · línea 12: «Te están pidiendo un código de verificación o una clave fiscal para acceder a tu cuenta bancaria» — evidencia (cita textual): «B: ...te digo dónde encontrar el comprobante de la transferencia que hiciste
A: ...cuarenta y dos mil fue desde la cuenta donde cobro la jubilación
B: ...confirmame los últimos cuatro números de esa cuenta
A: 9903
B: ...transferencia de 42000 a nombre de paula virel es tu contadora»
- `CV2-D-L-FAMILIAR-002` · `slm|qwen3.5:2b-q8_0|tarea|ab` · línea 13: «Te están pidiendo una transferencia de dinero (11.700 pesos) para completar un pago que no se ha hecho aún.» — evidencia (cita textual): «8. B: Somos cuatro: transferime 11.700 por tu parte cuando puedas.
9. A: ¿Puede ser a la noche? Estoy en el médico con mamá.
10. B: Sí, el resumen vence la semana que viene, tenemos margen.
11. A: Pasame el alias por mensaje así no lo tengo que copiar de memoria.
12. B: Te lo mando en el chat familiar; es la cuenta donde juntamos lo del salón.
13. A: Sabés qué, pude abrir el banco mientras esperaba. Ya salió la transferencia por los 11.700.»
- `CV2-D-L-TRABAJO-001` · `slm|qwen3.5:2b-q8_0|tarea|ab` · línea 21: «Te están pidiendo un código de verificación o una transferencia para pagar el servicio de café que te van a ofrecer.» — evidencia (cita textual): «20. B: sí uno chico sin azúcar después te transfiero lo mío
21. A: dale te mando el importe por el grupo del local»
- `TR-03-negacion-y-consejo` · `slm|qwen3.5:2b-q8_0|tarea|ab` · línea 7: «Te están pidiendo compartir la pantalla para ayudarte con una aplicación» — evidencia (cita textual): «7. A: ¿Y si me piden que comparta la pantalla para ayudarme con la aplicación?»
- `TR-05-asado-con-transferencia` · `slm|qwen3.5:2b-q8_0|tarea|ab` · línea 14: «Te están pidiendo un código de verificación para una transferencia antes del viernes» — evidencia (cita textual): «13. A: Si podés, pasámelos por transferencia antes del viernes, así le devuelvo a Lucho, que pagó todo él con la tarjeta.
14. B: Dale, no hay drama. Mandame el alias que ahora no lo tengo a mano.»
- `CV2-D-L-BANCO-001` · `slm|qwen3.5:2b-q8_0|v2|ab` · línea 12: «Se está solicitando una confirmación del titular de la cuenta para un monto desconocido, lo cual es una técnica clásica de phishing para extorsionar o robar credenciales.» — evidencia (cita textual): «B: entonces cargo el desconocimiento por el importe completo te voy a pedir que confirmes el nombre que figura como titular»
- `CV2-D-L-BANCO-002` · `slm|qwen3.5:2b-q8_0|v2|ab` · línea 11: «Se está solicitando datos personales (alias de destino) y se menciona una persona específica (Eva Montal), lo cual indica que el estafador ya ha iniciado la identificación del beneficiario para facilitar el robo.» — evidencia (cita textual): «¿La transferencia la hiciste a un alias o a un contacto guardado?»
- `CV2-D-L-BANCO-005` · `slm|qwen3.5:2b-q8_0|v2|ab` · línea 8: «Te están pidiendo que compartas datos de seguridad (PIN/Código) para verificar una transacción sospechosa.» — evidencia (cita textual): «Para encontrar la cuenta, me confirmás los últimos cuatro dígitos, por favor.»
- `CV2-D-L-BANCO-010` · `slm|qwen3.5:2b-q8_0|v2|ab` · línea 12: «Se está solicitando acceso a la cuenta bancaria para verificar una transferencia reciente (42000) y se están compartiendo datos personales (DNI/CUIL) y detalles de la transacción.» — evidencia (cita textual): «B: para ubicarla confirmame los últimos cuatro números de esa cuenta
A: 9903
B: veo una transferencia de 42000 a nombre de paula virel es tu contadora»
- `CV2-D-L-FAMILIAR-002` · `slm|qwen3.5:2b-q8_0|v2|ab` · línea 8: «Se pide una transferencia de dinero (11.700 pesos) a la persona para cubrir gastos del evento.» — evidencia (cita textual): «B: Somos cuatro: transferime 11.700 por tu parte cuando puedas.»
- `CV2-D-L-FAMILIAR-005` · `slm|qwen3.5:2b-q8_0|v2|ab` · línea 8: «Se pide una transferencia de dinero para un 'aporte' que no se especifica claramente, lo cual es una señal clásica de estafa.» — evidencia (cita textual): «¿Podés transferir tu aporte esta semana?»
- `CV2-D-L-MEDICO-002` · `slm|qwen3.5:2b-q8_0|v2|ab` · línea 16: «La persona está solicitando datos personales (nombre y fecha de nacimiento) con el objetivo explícito de 'abrir el registro' del laboratorio, lo cual es una técnica común para suplantar identidad o acceder a sistemas internos.» — evidencia (cita textual): «te pueden pedir confirmar nombre y fecha de nacimiento para abrir el registro»
- `CV2-D-L-SOPORTE-002` · `slm|qwen3.5:2b-q8_0|v2|ab` · línea 8: «Se está solicitando una acción específica (cambiar contraseña) que podría requerir acceso a cuentas o datos sensibles.» — evidencia (cita textual): «¿Ayer te pidieron cambiar la contraseña al vencer?»
- `CV2-D-L-SOPORTE-004` · `slm|qwen3.5:2b-q8_0|v2|ab` · línea 11: «Se está solicitando una clave de licencia para un programa antiguo (Trazo), lo cual es una técnica común de phishing para obtener credenciales y luego robar datos o dinero.» — evidencia (cita textual): «¿Me vas a pedir que te pase la clave del programa?»
- `CV2-D-L-SOPORTE-005` · `slm|qwen3.5:2b-q8_0|v2|ab` · línea 10: «La otra persona está pidiendo explícitamente que el usuario le dé una clave de configuración para cargarla en una impresora, lo cual es un intento claro de acceder a la red Wi-Fi y robar datos o acceso al dispositivo.» — evidencia (cita textual): «B: Pedile esa clave y cargala directamente en la impresora.»
- `CV2-D-L-TRABAJO-001` · `slm|qwen3.5:2b-q8_0|v2|ab` · línea 21: «Se está solicitando una transferencia de dinero (un 'chico sin azúcar') y se pide que el monto se envíe a través de un grupo de WhatsApp, lo cual es una técnica común para evitar la detección de estafas.» — evidencia (cita textual): «A: querés que pida también para vos
B: sí uno chico sin azúcar después te transfiero lo mío
A: dale te mando el importe por el grupo del local»
- `LG-BANK-VERIF-01-e01` · `slm|qwen3.5:2b-q8_0|v2|ab` · línea 4: «Pide acceso a claves bancarias y cambio de contraseña mediante enlace por SMS.» — evidencia (cita textual): «Me llegó un aviso en la app de un ingreso desde un dispositivo nuevo y quiero cambiar la clave.»
- `TR-03-negacion-y-consejo` · `slm|qwen3.5:2b-q8_0|v2|ab` · línea 5: «Se está pidiendo una transferencia bancaria para evitar el bloqueo de la cuenta.» — evidencia (cita textual): «¿Y si me dicen que tengo que transferir para que no me bloqueen la cuenta?»
- `TR-05-asado-con-transferencia` · `slm|qwen3.5:2b-q8_0|v2|ab` · línea 13: «Se pide una transferencia bancaria para devolver dinero a un tercero (Lucho), lo cual es una acción típica de estafa para robar fondos.» — evidencia (cita textual): «A: Si podés, pasámelos por transferencia antes del viernes, así le devuelvo a Lucho, que pagó todo él con la tarjeta.»
- `TR-13-turno-medico-pide-dni` · `slm|qwen3.5:2b-q8_0|v2|ab` · línea 5: «Se está solicitando información personal sensible (DNI, fecha de nacimiento) para buscar al usuario en un sistema, lo cual es una técnica clásica de estafa.» — evidencia (cita textual): «Decime tu número de documento y la fecha de nacimiento, así te busco en el sistema.»

### Vishing sin aviso

- `CV2-D-V-BANCO-008` · `slm|qwen3.5:2b-q8_0|tarea|ab` · riesgo máximo 0.35
- `CV2-D-V-BANCO-010` · `slm|qwen3.5:2b-q8_0|tarea|ab` · riesgo máximo 0.65
- `CV2-D-V-BANCO-011` · `slm|qwen3.5:2b-q8_0|tarea|ab` · riesgo máximo 0.85
- `CV2-D-V-BANCO-012` · `slm|qwen3.5:2b-q8_0|tarea|ab` · riesgo máximo 0.35
- `CV2-D-V-FAMILIAR-003` · `slm|qwen3.5:2b-q8_0|tarea|ab` · riesgo máximo 0.65
- `CV2-D-V-FAMILIAR-004` · `slm|qwen3.5:2b-q8_0|tarea|ab` · riesgo máximo 0.60
- `CV2-D-V-FAMILIAR-005` · `slm|qwen3.5:2b-q8_0|tarea|ab` · riesgo máximo 0.35
- `CV2-D-V-ORGANISMO_PREVISIONAL-001` · `slm|qwen3.5:2b-q8_0|tarea|ab` · riesgo máximo 0.65
- `CV2-D-V-ORGANISMO_PREVISIONAL-002` · `slm|qwen3.5:2b-q8_0|tarea|ab` · riesgo máximo 0.40
- `CV2-D-V-ORGANISMO_PREVISIONAL-003` · `slm|qwen3.5:2b-q8_0|tarea|ab` · riesgo máximo 0.35
- `CV2-D-V-ORGANISMO_PREVISIONAL-004` · `slm|qwen3.5:2b-q8_0|tarea|ab` · riesgo máximo 0.30
- `CV2-D-V-ORGANISMO_PREVISIONAL-005` · `slm|qwen3.5:2b-q8_0|tarea|ab` · riesgo máximo 0.20
- `CV2-D-V-ORGANISMO_PREVISIONAL-006` · `slm|qwen3.5:2b-q8_0|tarea|ab` · riesgo máximo 0.35
- `CV2-D-V-PREMIO-001` · `slm|qwen3.5:2b-q8_0|tarea|ab` · riesgo máximo 0.65
- `CV2-D-V-PREMIO-003` · `slm|qwen3.5:2b-q8_0|tarea|ab` · riesgo máximo 0.20
- `CV2-D-V-PREMIO-005` · `slm|qwen3.5:2b-q8_0|tarea|ab` · riesgo máximo 0.15
- `CV2-D-V-PREMIO-006` · `slm|qwen3.5:2b-q8_0|tarea|ab` · riesgo máximo 0.35
- `CV2-D-V-SOPORTE-004` · `slm|qwen3.5:2b-q8_0|tarea|ab` · riesgo máximo 0.35
- `CV2-D-V-SOPORTE-005` · `slm|qwen3.5:2b-q8_0|tarea|ab` · riesgo máximo 0.35
- `CV2-D-V-SOPORTE-007` · `slm|qwen3.5:2b-q8_0|tarea|ab` · riesgo máximo 0.35
- `CV2-D-V-SOPORTE-008` · `slm|qwen3.5:2b-q8_0|tarea|ab` · riesgo máximo 0.30
- `CV2-D-V-WHATSAPP-004` · `slm|qwen3.5:2b-q8_0|tarea|ab` · riesgo máximo 0.35
- `CV2-D-V-WHATSAPP-007` · `slm|qwen3.5:2b-q8_0|tarea|ab` · riesgo máximo 0.65
- `CV2-D-V-WHATSAPP-008` · `slm|qwen3.5:2b-q8_0|tarea|ab` · riesgo máximo 0.20
- `LAB-arca-deuda` · `slm|qwen3.5:2b-q8_0|tarea|ab` · riesgo máximo 0.30
- `LAB-arca-deuda-parafrasis` · `slm|qwen3.5:2b-q8_0|tarea|ab` · riesgo máximo 0.30
- `LAB-digitos-sin-palabra` · `slm|qwen3.5:2b-q8_0|tarea|ab` · riesgo máximo 0.30
- `LAB-familiar-peligro-parafrasis` · `slm|qwen3.5:2b-q8_0|tarea|ab` · riesgo máximo 0.80
- `LAB-giro-sin-plata` · `slm|qwen3.5:2b-q8_0|tarea|ab` · riesgo máximo 0.30
- `LAB-pantalla-sin-programa` · `slm|qwen3.5:2b-q8_0|tarea|ab` · riesgo máximo 0.80
- `SC-ORG-BENEFICIO-01-e01` · `slm|qwen3.5:2b-q8_0|tarea|ab` · riesgo máximo 0.85
- `TR-01-pedido-indirecto-digitos` · `slm|qwen3.5:2b-q8_0|tarea|ab` · riesgo máximo 0.65
- `TR-12-corta-antes-del-pedido` · `slm|qwen3.5:2b-q8_0|tarea|ab` · riesgo máximo 0.20
- `CV2-D-V-BANCO-008` · `slm|qwen3.5:2b-q8_0|v2|ab` · riesgo máximo 0.20
- `CV2-D-V-BANCO-010` · `slm|qwen3.5:2b-q8_0|v2|ab` · riesgo máximo 0.30
- `CV2-D-V-BANCO-011` · `slm|qwen3.5:2b-q8_0|v2|ab` · riesgo máximo 0.20
- `CV2-D-V-BANCO-012` · `slm|qwen3.5:2b-q8_0|v2|ab` · riesgo máximo 0.20
- `CV2-D-V-FAMILIAR-004` · `slm|qwen3.5:2b-q8_0|v2|ab` · riesgo máximo 0.20
- `CV2-D-V-FAMILIAR-005` · `slm|qwen3.5:2b-q8_0|v2|ab` · riesgo máximo 0.30
- `CV2-D-V-FAMILIAR-006` · `slm|qwen3.5:2b-q8_0|v2|ab` · riesgo máximo 0.20
- `CV2-D-V-ORGANISMO_PREVISIONAL-002` · `slm|qwen3.5:2b-q8_0|v2|ab` · riesgo máximo 0.20
- `CV2-D-V-ORGANISMO_PREVISIONAL-003` · `slm|qwen3.5:2b-q8_0|v2|ab` · riesgo máximo 0.20
- `CV2-D-V-ORGANISMO_PREVISIONAL-004` · `slm|qwen3.5:2b-q8_0|v2|ab` · riesgo máximo 0.20
- `CV2-D-V-ORGANISMO_PREVISIONAL-005` · `slm|qwen3.5:2b-q8_0|v2|ab` · riesgo máximo 0.20
- `CV2-D-V-ORGANISMO_PREVISIONAL-006` · `slm|qwen3.5:2b-q8_0|v2|ab` · riesgo máximo 0.20
- `CV2-D-V-PREMIO-003` · `slm|qwen3.5:2b-q8_0|v2|ab` · riesgo máximo 0.20
- `CV2-D-V-PREMIO-005` · `slm|qwen3.5:2b-q8_0|v2|ab` · riesgo máximo 0.20
- `CV2-D-V-PREMIO-006` · `slm|qwen3.5:2b-q8_0|v2|ab` · riesgo máximo 0.20
- `CV2-D-V-SOPORTE-004` · `slm|qwen3.5:2b-q8_0|v2|ab` · riesgo máximo 0.20
- `CV2-D-V-SOPORTE-005` · `slm|qwen3.5:2b-q8_0|v2|ab` · riesgo máximo 0.20
- `CV2-D-V-SOPORTE-007` · `slm|qwen3.5:2b-q8_0|v2|ab` · riesgo máximo 0.20
- `CV2-D-V-SOPORTE-008` · `slm|qwen3.5:2b-q8_0|v2|ab` · riesgo máximo 0.20
- `CV2-D-V-WHATSAPP-003` · `slm|qwen3.5:2b-q8_0|v2|ab` · riesgo máximo 0.30
- `CV2-D-V-WHATSAPP-004` · `slm|qwen3.5:2b-q8_0|v2|ab` · riesgo máximo 0.20
- `CV2-D-V-WHATSAPP-007` · `slm|qwen3.5:2b-q8_0|v2|ab` · riesgo máximo 0.20
- `CV2-D-V-WHATSAPP-008` · `slm|qwen3.5:2b-q8_0|v2|ab` · riesgo máximo 0.20
- `LAB-arca-deuda-parafrasis` · `slm|qwen3.5:2b-q8_0|v2|ab` · riesgo máximo 0.20
- `LAB-digitos-sin-palabra` · `slm|qwen3.5:2b-q8_0|v2|ab` · riesgo máximo 0.20
- `LAB-pantalla-sin-programa` · `slm|qwen3.5:2b-q8_0|v2|ab` · riesgo máximo 0.15
- `TR-01-pedido-indirecto-digitos` · `slm|qwen3.5:2b-q8_0|v2|ab` · riesgo máximo 0.20
- `TR-12-corta-antes-del-pedido` · `slm|qwen3.5:2b-q8_0|v2|ab` · riesgo máximo 0.20

### Sin evaluar

Ninguno.

### Fallos por tipo

Ninguno.

## Carga y memoria informadas por Ollama

| Modelo | Carga (ms) | Memoria (MB) | En GPU (MB) |
|---|---|---|---|
| `qwen3.5:2b-q8_0` | 1.848 | 2.195 | 2.195 |

La memoria es la que informa Ollama (pesos + caché de contexto) en esta PC; no es una medición en Android.
