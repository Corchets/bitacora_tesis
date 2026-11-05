# SLM solo, Tito con indicio y Tito sin indicio (150 de desarrollo)

> **Estado: propuesta sin discutir.** Diagnóstico sobre material de desarrollo, sin revisión humana de casos ni de `T_R`. No toca el test reservado.

## Corridas

- **SLM solo**: 2026-11-04_193946_prompt-v3-a-solo-y-con-indicio · `slm|gemma4:e2b-it-q4_K_M|v3|ab`
- **Tito → SLM con indicio**: 2026-11-04_193946_prompt-v3-a-solo-y-con-indicio · `tito-slm|gemma4:e2b-it-q4_K_M|v3|ab`
- **Tito → SLM sin indicio**: 2026-11-04_201116_prompt-v3-b-tito-sin-indicio · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|ab`

## Resultado global

| | SLM solo | Tito → SLM con indicio | Tito → SLM sin indicio |
|---|---|---|---|
| Estafas con aviso | 65/75 (87 %) | 63/75 (84 %) | 64/75 (85 %) |
| Estafas con pedido (T_R) con aviso | 64/64 | 62/64 | 63/64 |
| · antes del pedido | 43 | 36 | 42 |
| · en el pedido | 20 | 23 | 18 |
| · después del pedido | 1 | 3 | 3 |
| Falsas alarmas | 47/75 (63 %) | 30/75 (40 %) | 35/75 (47 %) |
| · legítimas comunes | 28/51 | 17/51 | 20/51 |
| · legítimas difíciles | 19/24 | 13/24 | 15/24 |
| Consultas al SLM | 1.680 | 867 | 791 |
| Líneas omitidas por Tito | 0 | 1.139 | 1.139 |
| Fallos de JSON o tiempo | 0 | 0 | 0 |
| Mediana del SLM por consulta (ms) | 556 | 616 | 584 |
| Casos sin procesar | 0 | 0 | 0 |

## Activación de Tito respecto del pedido

- Tito → SLM con indicio: primera consulta antes del pedido en 57, en el pedido en 5, después en 1, nunca en 1 (de 64 estafas con `T_R`).
- Tito → SLM sin indicio: primera consulta antes del pedido en 57, en el pedido en 5, después en 1, nunca en 1 (de 64 estafas con `T_R`).

## Caso por caso

### SLM solo contra Tito → SLM con indicio

- Estafas en que avisan las dos: 63 — misma línea 38, antes «solo» 20, antes «con-indicio» 5.
  - Adelanto medio de «solo» cuando se adelanta: 3.7 líneas.
  - Adelanto medio de «con-indicio» cuando se adelanta: 1.2 líneas.
- Estafas que solo detecta «solo» (pierde «con-indicio»): `CV2-D-V-FAMILIAR-006`, `CV2-D-V-PREMIO-001`
- Estafas que solo detecta «con-indicio» (gana «con-indicio»): ninguna
- Estafas que no detecta ninguna: `CV2-D-V-BANCO-012`, `CV2-D-V-ORGANISMO_PREVISIONAL-005`, `CV2-D-V-ORGANISMO_PREVISIONAL-006`, `CV2-D-V-PREMIO-005`, `CV2-D-V-PREMIO-006`, `CV2-D-V-SOPORTE-007`, `CV2-D-V-SOPORTE-008`, `CV2-D-V-WHATSAPP-007`, `CV2-D-V-WHATSAPP-008`, `TR-12-corta-antes-del-pedido`
- Falsas alarmas solo de «solo»: `CV2-D-L-BANCO-003`, `CV2-D-L-BANCO-009`, `CV2-D-L-DELIVERY-001`, `CV2-D-L-MEDICO-001`, `CV2-D-L-MEDICO-004`, `CV2-D-L-MEDICO-005`, `CV2-D-L-ORGANISMO_PREVISIONAL-002`, `CV2-D-L-PREMIO-003`, `CV2-D-L-SOPORTE-001`, `CV2-D-L-SOPORTE-002`, `CV2-D-L-WHATSAPP-002`, `LAB-banco-gasto-sin-pedido`, `LG-FAMILIAR-LLAMADO-01-e01`, `LG-ORG-TURNO-01-e01`, `LG-SUPPORT-INFO-01-e02`, `LG-WA-CONSULTA-01-e01`, `TR-03-negacion-y-consejo`
- Falsas alarmas solo de «con-indicio»: ninguna
- Líneas consultadas en común: 725; cambia `alerta_sugerida` en 24 (3.3 %).

| | Alerta solo «solo» | Alerta solo «con-indicio» |
|---|---|---|
| estafa | 12 | 5 |
| legítima | 7 | 0 |

  - estafa, alerta solo «con-indicio»: `CV2-D-V-SOPORTE-005:L10`, `CV2-D-V-WHATSAPP-005:L10`, `LAB-whatsapp-codigo:L1`, `TR-04-pedido-tras-charla-larga:L21`, `TR-10-ofrecimiento-inducido:L4`
  - estafa, alerta solo «solo»: `CV2-D-V-BANCO-003:L14`, `CV2-D-V-BANCO-005:L2`, `CV2-D-V-BANCO-006:L8`, `CV2-D-V-BANCO-009:L9`, `CV2-D-V-BANCO-010:L1`, `CV2-D-V-FAMILIAR-001:L15`, `CV2-D-V-FAMILIAR-006:L19`, `CV2-D-V-ORGANISMO_PREVISIONAL-001:L2`, `CV2-D-V-PREMIO-002:L12`, `CV2-D-V-PREMIO-003:L15`, `SC-CLAVE-CAMBIO-01-e01:L2`, `SC-WA-CODE-01-e01:L3`
  - legítima, alerta solo «solo»: `CV2-D-L-BANCO-006:L6`, `CV2-D-L-DELIVERY-001:L17`, `CV2-D-L-PREMIO-002:L11`, `CV2-D-L-TRABAJO-001:L15`, `LAB-arca-canal-oficial:L2`, `LAB-banco-gasto-sin-pedido:L3`, `LG-SUPPORT-INFO-01-e02:L11`

### SLM solo contra Tito → SLM sin indicio

- Estafas en que avisan las dos: 64 — misma línea 51, antes «solo» 10, antes «sin-indicio» 3.
  - Adelanto medio de «solo» cuando se adelanta: 4.5 líneas.
  - Adelanto medio de «sin-indicio» cuando se adelanta: 3.3 líneas.
- Estafas que solo detecta «solo» (pierde «sin-indicio»): `CV2-D-V-PREMIO-001`
- Estafas que solo detecta «sin-indicio» (gana «sin-indicio»): ninguna
- Estafas que no detecta ninguna: `CV2-D-V-BANCO-012`, `CV2-D-V-ORGANISMO_PREVISIONAL-005`, `CV2-D-V-ORGANISMO_PREVISIONAL-006`, `CV2-D-V-PREMIO-005`, `CV2-D-V-PREMIO-006`, `CV2-D-V-SOPORTE-007`, `CV2-D-V-SOPORTE-008`, `CV2-D-V-WHATSAPP-007`, `CV2-D-V-WHATSAPP-008`, `TR-12-corta-antes-del-pedido`
- Falsas alarmas solo de «solo»: `CV2-D-L-BANCO-003`, `CV2-D-L-BANCO-009`, `CV2-D-L-MEDICO-001`, `CV2-D-L-MEDICO-004`, `CV2-D-L-MEDICO-005`, `CV2-D-L-ORGANISMO_PREVISIONAL-002`, `CV2-D-L-PREMIO-003`, `CV2-D-L-SOPORTE-001`, `CV2-D-L-SOPORTE-002`, `LG-FAMILIAR-LLAMADO-01-e01`, `LG-ORG-TURNO-01-e01`, `LG-WA-CONSULTA-01-e01`, `TR-03-negacion-y-consejo`
- Falsas alarmas solo de «sin-indicio»: `CV2-D-L-WHATSAPP-004`
- Líneas consultadas en común: 708; cambia `alerta_sugerida` en 6 (0.8 %).

| | Alerta solo «solo» | Alerta solo «sin-indicio» |
|---|---|---|
| estafa | 1 | 3 |
| legítima | 1 | 1 |

  - estafa, alerta solo «sin-indicio»: `CV2-D-V-FAMILIAR-004:L15`, `CV2-D-V-ORGANISMO_PREVISIONAL-002:L8`, `SC-ORG-BENEFICIO-01-e01:L5`
  - estafa, alerta solo «solo»: `CV2-D-V-FAMILIAR-006:L19`
  - legítima, alerta solo «sin-indicio»: `CV2-D-L-WHATSAPP-004:L12`
  - legítima, alerta solo «solo»: `LAB-arca-canal-oficial:L2`

### Tito → SLM con indicio contra Tito → SLM sin indicio

- Estafas en que avisan las dos: 63 — misma línea 44, antes «con-indicio» 5, antes «sin-indicio» 14.
  - Adelanto medio de «con-indicio» cuando se adelanta: 1.2 líneas.
  - Adelanto medio de «sin-indicio» cuando se adelanta: 3.1 líneas.
- Estafas que solo detecta «con-indicio» (pierde «sin-indicio»): ninguna
- Estafas que solo detecta «sin-indicio» (gana «sin-indicio»): `CV2-D-V-FAMILIAR-006`
- Estafas que no detecta ninguna: `CV2-D-V-BANCO-012`, `CV2-D-V-ORGANISMO_PREVISIONAL-005`, `CV2-D-V-ORGANISMO_PREVISIONAL-006`, `CV2-D-V-PREMIO-001`, `CV2-D-V-PREMIO-005`, `CV2-D-V-PREMIO-006`, `CV2-D-V-SOPORTE-007`, `CV2-D-V-SOPORTE-008`, `CV2-D-V-WHATSAPP-007`, `CV2-D-V-WHATSAPP-008`, `TR-12-corta-antes-del-pedido`
- Falsas alarmas solo de «con-indicio»: ninguna
- Falsas alarmas solo de «sin-indicio»: `CV2-D-L-DELIVERY-001`, `CV2-D-L-WHATSAPP-002`, `CV2-D-L-WHATSAPP-004`, `LAB-banco-gasto-sin-pedido`, `LG-SUPPORT-INFO-01-e02`
- Líneas consultadas en común: 785; cambia `alerta_sugerida` en 30 (3.8 %).

| | Alerta solo «con-indicio» | Alerta solo «sin-indicio» |
|---|---|---|
| estafa | 5 | 15 |
| legítima | 0 | 10 |

  - estafa, alerta solo «con-indicio»: `CV2-D-V-SOPORTE-005:L10`, `CV2-D-V-WHATSAPP-005:L10`, `LAB-whatsapp-codigo:L1`, `TR-04-pedido-tras-charla-larga:L21`, `TR-10-ofrecimiento-inducido:L4`
  - estafa, alerta solo «sin-indicio»: `CV2-D-V-BANCO-003:L14`, `CV2-D-V-BANCO-005:L2`, `CV2-D-V-BANCO-006:L8`, `CV2-D-V-BANCO-009:L9`, `CV2-D-V-BANCO-010:L1`, `CV2-D-V-FAMILIAR-001:L15`, `CV2-D-V-FAMILIAR-004:L15`, `CV2-D-V-FAMILIAR-006:L23`, `CV2-D-V-ORGANISMO_PREVISIONAL-001:L2`, `CV2-D-V-ORGANISMO_PREVISIONAL-002:L8`, `CV2-D-V-PREMIO-002:L12`, `CV2-D-V-PREMIO-003:L15`, `SC-CLAVE-CAMBIO-01-e01:L2`, `SC-ORG-BENEFICIO-01-e01:L5`, `SC-WA-CODE-01-e01:L3`
  - legítima, alerta solo «sin-indicio»: `CV2-D-L-BANCO-006:L6`, `CV2-D-L-DELIVERY-001:L17`, `CV2-D-L-ESCUELA-004:L7`, `CV2-D-L-PREMIO-002:L11`, `CV2-D-L-TRABAJO-001:L15`, `CV2-D-L-WHATSAPP-002:L20`, `CV2-D-L-WHATSAPP-004:L12`, `LAB-banco-gasto-sin-pedido:L3`, `LG-SUPPORT-INFO-01-e01:L7`, `LG-SUPPORT-INFO-01-e02:L11`
