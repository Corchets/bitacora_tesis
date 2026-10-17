# Comparación de Reproducibilidad entre Máquinas: Apple M1 vs Windows 11 (#50)

> **Advertencia metodológica:** Material de desarrollo con casos escritos y semillas fijadas (seed=42). Las mediciones corresponden a hardware y motores distintos (Apple M1 8 GB Metal GGUF vs Windows 11 NVIDIA GPU GGUF). Sin interpretar más allá de lo estrictamente observado empíricamente.

- **Corrida M1:** `2026-10-17_150516_m1-gguf`
- **Fecha M1:** 2026-10-17T15:05:16 a 2026-10-17T16:21:26
- **Interrupción 4B:** SIGINT del coordinador a las 16:21 por swap de 15 GB y 3,5 GB libres en disco, con la VM de Docker del usuario activa y 8 GB de RAM.

## 1. Resumen de Acuerdo por Modelo

| Modelo | Casos | Acuerdo Aviso (Sí/No) | Acuerdo Línea Exacta | Latencia M1 (p50 / p95) | Latencia Win (p50 / p95) |
|---|---|---|---|---|---|
| **0.8B** (`qwen3.5:0.8b-q8_0`) | 53 | 51/53 (96.2%) | 48/53 (90.6%) | 1282.0 ms / 3462.5 ms | 276.5 ms / 705.5 ms |
| **2B** (`qwen3.5:2b-q8_0`) | 53 | 52/53 (98.1%) | 51/53 (96.2%) | 2645.6 ms / 6036.0 ms | 532.0 ms / 1118.3 ms |
| **4B** (`qwen3.5:4b-q4_K_M`) | 42 | 40/42 (95.2%) | 37/42 (88.1%) | 6627.9 ms / 10186.1 ms | 896.2 ms / 1630.0 ms |

## 2. Casos excluidos por evaluación incompleta

Solo se comparan casos cuyas líneas fueron evaluadas y válidas en ambas máquinas. Las latencias también se calculan sobre esas líneas incluidas.

### Modelo 0.8B: 0 excluidos

No hubo casos excluidos.

### Modelo 2B: 0 excluidos

No hubo casos excluidos.

### Modelo 4B: 11 excluidos

| Caso | Motivo |
|---|---|
| `TR-03-negacion-y-consejo` | `m1_sin_lineas:5,6,7,8,9,10` |
| `TR-04-pedido-tras-charla-larga` | `sin_evaluaciones_en_m1` |
| `TR-05-asado-con-transferencia` | `sin_evaluaciones_en_m1` |
| `TR-06-banco-alerta-legitima` | `sin_evaluaciones_en_m1` |
| `TR-07-pedido-partido-en-dos-lineas` | `sin_evaluaciones_en_m1` |
| `TR-08-frase-cortada-candado` | `sin_evaluaciones_en_m1` |
| `TR-09-victima-se-niega` | `sin_evaluaciones_en_m1` |
| `TR-10-ofrecimiento-inducido` | `sin_evaluaciones_en_m1` |
| `TR-11-familiar-real-pide-plata` | `sin_evaluaciones_en_m1` |
| `TR-12-corta-antes-del-pedido` | `sin_evaluaciones_en_m1` |
| `TR-13-turno-medico-pide-dni` | `sin_evaluaciones_en_m1` |

## 2. Diferencias Observadas Caso por Caso

### Modelo 0.8B (`qwen3.5:0.8b-q8_0`)
Se registraron 5 discrepancias entre plataformas:

| Caso | Windows (Aviso @ Línea) | M1 (Aviso @ Línea) | Motivo Windows | Motivo M1 |
|---|---|---|---|---|
| `LAB-arca-deuda` | Sí @ L5 | Sí @ L3 | Te están solicitando un código de verificación o activación para acceder a una cuenta fiscal (embargo), lo cual es una acción directa de robo de datos y dinero. | Te están solicitando una clave de acceso fiscal o un pago para realizar una transferencia hoy. |
| `LG-ORG-TURNO-01-e01` | Sí @ L9 | Sí @ L6 | Te están solicitando datos personales (DNI) y una foto de un documento para realizar una transferencia o pago, lo cual es una acción directa de robo de dinero. | Te están solicitando datos personales (DNI) y una foto de un documento para verificar si estás en el listado de jubilados. Esto es una acción directa de seguridad guiada que podría permitirles robar tu información o acceder a tus cuentas. |
| `SC-FAMILIAR-DINERO-01-e01` | Sí @ L9 | Sí @ L8 | Te están solicitando transferencias de dinero a una cuenta específica para un pago urgente (ciento ochenta mil pesos) y te están presionando para que hagas algo que permitiría robarle dinero o tomar sus cuentas. | Te están pidiendo un código de verificación o activación para acceder a tu cuenta bancaria. |
| `TR-01-pedido-indirecto-digitos` | No @ L- | Sí @ L9 | — | Te están solicitando un código de verificación para validar que la persona actual es la titular del servicio y que el consumo en curso corresponde a ella. Esto permite robar datos personales o acceder a cuentas. |
| `TR-11-familiar-real-pide-plata` | No @ L- | Sí @ L9 | — | Te están solicitando un código de verificación o activación para acceder a tu cuenta bancaria y transferir dinero. |

### Modelo 2B (`qwen3.5:2b-q8_0`)
Se registraron 2 discrepancias entre plataformas:

| Caso | Windows (Aviso @ Línea) | M1 (Aviso @ Línea) | Motivo Windows | Motivo M1 |
|---|---|---|---|---|
| `LAB-pantalla-sin-programa` | Sí @ L3 | No @ L- | Te están pidiendo instalar un programa para ver tu celular | — |
| `TR-05-asado-con-transferencia` | Sí @ L17 | Sí @ L14 | Te están pidiendo un código de verificación para una transferencia antes del viernes | Te están pidiendo un código de verificación para una transferencia antes del viernes |

### Modelo 4B (`qwen3.5:4b-q4_K_M`)
Se registraron 5 discrepancias entre plataformas:

| Caso | Windows (Aviso @ Línea) | M1 (Aviso @ Línea) | Motivo Windows | Motivo M1 |
|---|---|---|---|---|
| `LAB-banco-codigo-parafrasis` | Sí @ L2 | Sí @ L1 | Te están simulando ser del banco para pedirte información sobre un gasto que no es tuyo | Te están simulando ser del banco para pedirte un gasto que no es tuyo |
| `LAB-banco-gasto-sin-pedido` | No @ L- | Sí @ L1 | — | Te están simulando ser el banco para pedirte un código o datos por un gasto falso |
| `LG-BANK-VERIF-01-e01` | Sí @ L2 | No @ L- | Te están pidiendo que cambies tu clave por un aviso de ingreso sospechoso | — |
| `LG-ORG-TURNO-01-e01` | Sí @ L10 | Sí @ L6 | Te están pidiendo tu número de documento para que te saquen un turno por teléfono. | Te están presionando para que des tus datos personales (DNI, domicilio) y una foto del documento. |
| `SC-WA-CODE-01-e01` | Sí @ L1 | Sí @ L2 | Te están simulando ser soporte técnico para activar tu cuenta de WhatsApp | Te están simulando un soporte técnico para activar tu cuenta de WhatsApp y te piden que compartas un código que no pediste. |
