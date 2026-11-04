# SLM solo, Tito con indicio y Tito sin indicio (150 de desarrollo)

> **Estado: propuesta sin discutir.** Diagnóstico sobre material de desarrollo, sin revisión humana de casos ni de `T_R`. No toca el test reservado.

## Corridas

- **SLM solo**: 2026-11-04_194015_sin-indicio-a-solo-y-con-indicio · `slm|gemma4:e2b-it-q4_K_M|tarea|ab`
- **Tito → SLM con indicio**: 2026-11-04_194015_sin-indicio-a-solo-y-con-indicio · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab`
- **Tito → SLM sin indicio**: 2026-11-04_201218_sin-indicio-b-tito-sin-indicio · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|tarea|ab`
- **SLM solo (repetición)**: 2026-11-04_202259_sin-indicio-c-solo-repeticion · `slm|gemma4:e2b-it-q4_K_M|tarea|ab`

## Resultado global

| | SLM solo | Tito → SLM con indicio | Tito → SLM sin indicio | SLM solo (repetición) |
|---|---|---|---|---|
| Estafas con aviso | 55/75 (73 %) | 50/75 (67 %) | 54/75 (72 %) | 54/75 (72 %) |
| Estafas con pedido (T_R) con aviso | 54/64 | 50/64 | 53/64 | 53/64 |
| · antes del pedido | 25 | 18 | 24 | 24 |
| · en el pedido | 26 | 28 | 25 | 26 |
| · después del pedido | 3 | 4 | 4 | 3 |
| Falsas alarmas | 19/75 (25 %) | 12/75 (16 %) | 14/75 (19 %) | 20/75 (27 %) |
| · legítimas comunes | 4/51 | 5/51 | 4/51 | 4/51 |
| · legítimas difíciles | 15/24 | 7/24 | 10/24 | 16/24 |
| Consultas al SLM | 2.214 | 1.189 | 1.140 | 2.225 |
| Líneas omitidas por Tito | 0 | 1.139 | 1.139 | 0 |
| Fallos de JSON o tiempo | 0 | 0 | 0 | 0 |
| Mediana del SLM por consulta (ms) | 422 | 442 | 411 | 423 |
| Casos sin procesar | 0 | 0 | 0 | 0 |

## Activación de Tito respecto del pedido

- Tito → SLM con indicio: primera consulta antes del pedido en 57, en el pedido en 5, después en 1, nunca en 1 (de 64 estafas con `T_R`).
- Tito → SLM sin indicio: primera consulta antes del pedido en 57, en el pedido en 5, después en 1, nunca en 1 (de 64 estafas con `T_R`).

## Caso por caso

### SLM solo contra Tito → SLM con indicio

- Estafas en que avisan las dos: 49 — misma línea 35, antes «solo» 11, antes «con-indicio» 3.
  - Adelanto medio de «solo» cuando se adelanta: 3.7 líneas.
  - Adelanto medio de «con-indicio» cuando se adelanta: 2.7 líneas.
- Estafas que solo detecta «solo» (pierde «con-indicio»): `CV2-D-V-BANCO-003`, `CV2-D-V-BANCO-011`, `CV2-D-V-FAMILIAR-003`, `CV2-D-V-PREMIO-001`, `CV2-D-V-PREMIO-002`, `TR-01-pedido-indirecto-digitos`
- Estafas que solo detecta «con-indicio» (gana «con-indicio»): `TR-04-pedido-tras-charla-larga`
- Estafas que no detecta ninguna: `CV2-D-V-BANCO-012`, `CV2-D-V-FAMILIAR-004`, `CV2-D-V-FAMILIAR-005`, `CV2-D-V-FAMILIAR-006`, `CV2-D-V-ORGANISMO_PREVISIONAL-003`, `CV2-D-V-ORGANISMO_PREVISIONAL-004`, `CV2-D-V-ORGANISMO_PREVISIONAL-005`, `CV2-D-V-ORGANISMO_PREVISIONAL-006`, `CV2-D-V-PREMIO-003`, `CV2-D-V-PREMIO-005`, `CV2-D-V-PREMIO-006`, `CV2-D-V-SOPORTE-001`, `CV2-D-V-SOPORTE-005`, `CV2-D-V-SOPORTE-007`, `CV2-D-V-SOPORTE-008`, `CV2-D-V-WHATSAPP-004`, `CV2-D-V-WHATSAPP-007`, `CV2-D-V-WHATSAPP-008`, `TR-12-corta-antes-del-pedido`
- Falsas alarmas solo de «solo»: `CV2-D-L-BANCO-001`, `LAB-anses-canal-oficial`, `LAB-arca-canal-oficial`, `LAB-banco-app-parafrasis`, `LG-ORG-TURNO-01-e01`, `LG-SUPPORT-INFO-01-e01`, `LG-WA-CONSULTA-01-e01`, `TR-03-negacion-y-consejo`, `TR-05-asado-con-transferencia`
- Falsas alarmas solo de «con-indicio»: `CV2-D-L-BANCO-005`, `CV2-D-L-FAMILIAR-002`
- Líneas consultadas en común: 1083; cambia `alerta_sugerida` en 24 (2.2 %).

| | Alerta solo «solo» | Alerta solo «con-indicio» |
|---|---|---|
| estafa | 13 | 4 |
| legítima | 4 | 3 |

  - estafa, alerta solo «con-indicio»: `CV2-D-V-BANCO-010:L1`, `CV2-D-V-PREMIO-004:L14`, `LAB-whatsapp-codigo:L1`, `TR-04-pedido-tras-charla-larga:L27`
  - estafa, alerta solo «solo»: `CV2-D-V-BANCO-002:L10`, `CV2-D-V-BANCO-003:L14`, `CV2-D-V-BANCO-005:L5`, `CV2-D-V-BANCO-006:L10`, `CV2-D-V-BANCO-009:L13`, `CV2-D-V-BANCO-011:L17`, `CV2-D-V-FAMILIAR-003:L17`, `CV2-D-V-PREMIO-002:L13`, `CV2-D-V-SOPORTE-004:L14`, `LAB-banco-numeros-sin-clave:L3`, `TR-01-pedido-indirecto-digitos:L5`, `TR-07-pedido-partido-en-dos-lineas:L6`, `TR-10-ofrecimiento-inducido:L4`
  - legítima, alerta solo «con-indicio»: `CV2-D-L-BANCO-005:L8`, `CV2-D-L-FAMILIAR-002:L11`, `CV2-D-L-FAMILIAR-005:L10`
  - legítima, alerta solo «solo»: `CV2-D-L-BANCO-001:L12`, `LAB-arca-canal-oficial:L3`, `LAB-banco-app-parafrasis:L3`, `TR-05-asado-con-transferencia:L14`

### SLM solo contra Tito → SLM sin indicio

- Estafas en que avisan las dos: 54 — misma línea 48, antes «solo» 5, antes «sin-indicio» 1.
  - Adelanto medio de «solo» cuando se adelanta: 3.2 líneas.
  - Adelanto medio de «sin-indicio» cuando se adelanta: 4.0 líneas.
- Estafas que solo detecta «solo» (pierde «sin-indicio»): `CV2-D-V-PREMIO-001`
- Estafas que solo detecta «sin-indicio» (gana «sin-indicio»): ninguna
- Estafas que no detecta ninguna: `CV2-D-V-BANCO-012`, `CV2-D-V-FAMILIAR-004`, `CV2-D-V-FAMILIAR-005`, `CV2-D-V-FAMILIAR-006`, `CV2-D-V-ORGANISMO_PREVISIONAL-003`, `CV2-D-V-ORGANISMO_PREVISIONAL-004`, `CV2-D-V-ORGANISMO_PREVISIONAL-005`, `CV2-D-V-ORGANISMO_PREVISIONAL-006`, `CV2-D-V-PREMIO-003`, `CV2-D-V-PREMIO-005`, `CV2-D-V-PREMIO-006`, `CV2-D-V-SOPORTE-001`, `CV2-D-V-SOPORTE-005`, `CV2-D-V-SOPORTE-007`, `CV2-D-V-SOPORTE-008`, `CV2-D-V-WHATSAPP-004`, `CV2-D-V-WHATSAPP-007`, `CV2-D-V-WHATSAPP-008`, `TR-04-pedido-tras-charla-larga`, `TR-12-corta-antes-del-pedido`
- Falsas alarmas solo de «solo»: `LAB-anses-canal-oficial`, `LG-ORG-TURNO-01-e01`, `LG-SUPPORT-INFO-01-e01`, `LG-WA-CONSULTA-01-e01`, `TR-03-negacion-y-consejo`
- Falsas alarmas solo de «sin-indicio»: ninguna
- Líneas consultadas en común: 1119; cambia `alerta_sugerida` en 3 (0.3 %).

| | Alerta solo «solo» | Alerta solo «sin-indicio» |
|---|---|---|
| estafa | 2 | 1 |
| legítima | 0 | 0 |

  - estafa, alerta solo «sin-indicio»: `CV2-D-V-BANCO-010:L3`
  - estafa, alerta solo «solo»: `CV2-D-V-WHATSAPP-006:L25`, `TR-01-pedido-indirecto-digitos:L5`

### Tito → SLM con indicio contra Tito → SLM sin indicio

- Estafas en que avisan las dos: 49 — misma línea 36, antes «con-indicio» 4, antes «sin-indicio» 9.
  - Adelanto medio de «con-indicio» cuando se adelanta: 1.2 líneas.
  - Adelanto medio de «sin-indicio» cuando se adelanta: 3.0 líneas.
- Estafas que solo detecta «con-indicio» (pierde «sin-indicio»): `TR-04-pedido-tras-charla-larga`
- Estafas que solo detecta «sin-indicio» (gana «sin-indicio»): `CV2-D-V-BANCO-003`, `CV2-D-V-BANCO-011`, `CV2-D-V-FAMILIAR-003`, `CV2-D-V-PREMIO-002`, `TR-01-pedido-indirecto-digitos`
- Estafas que no detecta ninguna: `CV2-D-V-BANCO-012`, `CV2-D-V-FAMILIAR-004`, `CV2-D-V-FAMILIAR-005`, `CV2-D-V-FAMILIAR-006`, `CV2-D-V-ORGANISMO_PREVISIONAL-003`, `CV2-D-V-ORGANISMO_PREVISIONAL-004`, `CV2-D-V-ORGANISMO_PREVISIONAL-005`, `CV2-D-V-ORGANISMO_PREVISIONAL-006`, `CV2-D-V-PREMIO-001`, `CV2-D-V-PREMIO-003`, `CV2-D-V-PREMIO-005`, `CV2-D-V-PREMIO-006`, `CV2-D-V-SOPORTE-001`, `CV2-D-V-SOPORTE-005`, `CV2-D-V-SOPORTE-007`, `CV2-D-V-SOPORTE-008`, `CV2-D-V-WHATSAPP-004`, `CV2-D-V-WHATSAPP-007`, `CV2-D-V-WHATSAPP-008`, `TR-12-corta-antes-del-pedido`
- Falsas alarmas solo de «con-indicio»: `CV2-D-L-BANCO-005`, `CV2-D-L-FAMILIAR-002`
- Falsas alarmas solo de «sin-indicio»: `CV2-D-L-BANCO-001`, `LAB-arca-canal-oficial`, `LAB-banco-app-parafrasis`, `TR-05-asado-con-transferencia`
- Líneas consultadas en común: 1103; cambia `alerta_sugerida` en 26 (2.4 %).

| | Alerta solo «con-indicio» | Alerta solo «sin-indicio» |
|---|---|---|
| estafa | 5 | 14 |
| legítima | 3 | 4 |

  - estafa, alerta solo «con-indicio»: `CV2-D-V-BANCO-010:L1`, `CV2-D-V-PREMIO-004:L14`, `CV2-D-V-WHATSAPP-006:L25`, `LAB-whatsapp-codigo:L1`, `TR-04-pedido-tras-charla-larga:L27`
  - estafa, alerta solo «sin-indicio»: `CV2-D-V-BANCO-002:L10`, `CV2-D-V-BANCO-003:L14`, `CV2-D-V-BANCO-005:L5`, `CV2-D-V-BANCO-006:L10`, `CV2-D-V-BANCO-007:L16`, `CV2-D-V-BANCO-009:L13`, `CV2-D-V-BANCO-011:L17`, `CV2-D-V-FAMILIAR-003:L17`, `CV2-D-V-PREMIO-002:L13`, `CV2-D-V-SOPORTE-004:L14`, `LAB-banco-numeros-sin-clave:L3`, `TR-01-pedido-indirecto-digitos:L6`, `TR-07-pedido-partido-en-dos-lineas:L6`, `TR-10-ofrecimiento-inducido:L4`
  - legítima, alerta solo «con-indicio»: `CV2-D-L-BANCO-005:L8`, `CV2-D-L-FAMILIAR-002:L11`, `CV2-D-L-FAMILIAR-005:L10`
  - legítima, alerta solo «sin-indicio»: `CV2-D-L-BANCO-001:L12`, `LAB-arca-canal-oficial:L3`, `LAB-banco-app-parafrasis:L3`, `TR-05-asado-con-transferencia:L14`

### SLM solo contra SLM solo (repetición)

- Estafas en que avisan las dos: 54 — misma línea 54, antes «solo» 0, antes «solo-rep» 0.
- Estafas que solo detecta «solo» (pierde «solo-rep»): `CV2-D-V-BANCO-003`
- Estafas que solo detecta «solo-rep» (gana «solo-rep»): ninguna
- Estafas que no detecta ninguna: `CV2-D-V-BANCO-012`, `CV2-D-V-FAMILIAR-004`, `CV2-D-V-FAMILIAR-005`, `CV2-D-V-FAMILIAR-006`, `CV2-D-V-ORGANISMO_PREVISIONAL-003`, `CV2-D-V-ORGANISMO_PREVISIONAL-004`, `CV2-D-V-ORGANISMO_PREVISIONAL-005`, `CV2-D-V-ORGANISMO_PREVISIONAL-006`, `CV2-D-V-PREMIO-003`, `CV2-D-V-PREMIO-005`, `CV2-D-V-PREMIO-006`, `CV2-D-V-SOPORTE-001`, `CV2-D-V-SOPORTE-005`, `CV2-D-V-SOPORTE-007`, `CV2-D-V-SOPORTE-008`, `CV2-D-V-WHATSAPP-004`, `CV2-D-V-WHATSAPP-007`, `CV2-D-V-WHATSAPP-008`, `TR-04-pedido-tras-charla-larga`, `TR-12-corta-antes-del-pedido`
- Falsas alarmas solo de «solo»: ninguna
- Falsas alarmas solo de «solo-rep»: `LAB-familiar-llama-vos`
- Líneas consultadas en común: 2213; cambia `alerta_sugerida` en 2 (0.1 %).

| | Alerta solo «solo» | Alerta solo «solo-rep» |
|---|---|---|
| estafa | 1 | 0 |
| legítima | 0 | 1 |

  - estafa, alerta solo «solo»: `CV2-D-V-BANCO-003:L14`
  - legítima, alerta solo «solo-rep»: `LAB-familiar-llama-vos:L4`
