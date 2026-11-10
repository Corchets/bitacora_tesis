# Legítimas dudosas del corpus de desarrollo

Fecha: 2026-11-09. Aplicación a ciegas del [criterio](CRITERIO-LEGITIMAS-DUDOSAS.md) a las 94 legítimas de desarrollo.

> **Estado: propuesta sin discutir.** Dos agentes aplicaron el criterio sin ver `case_id`, referencia ni resultados.
> **No se borra nada:** las dudosas se informan aparte. El juicio de credibilidad es humano
> ([#145](https://github.com/Corchets/bitacora_tesis/issues/145)); esto solo dice qué llamadas chocan con lo que las
> fuentes dicen que una entidad real no hace por teléfono.

## Resultado

**7 dudosas de 94; con la variante estricta de S4, 13.** No queda ninguna «a revisar».

| Caso | Escenario | Señales | Qué pasa |
|---|---|---|---|
| `ENT-L-BANCO-001` | E01 | S4 | Prevención de fraudes, por una compra que la persona no hizo. Pide DNI y fecha de nacimiento antes de decir el motivo. |
| `LEG2-BA-01` | E01 | S4 | El mismo guion, más corto. |
| `ENT-L-BANCO-002` | E02 | S4, S2 | Accesos desde un celular nuevo que la persona no hizo. Pide el DNI después del motivo y, más adelante, la guía en la app durante la llamada. |
| `LEG2-BA-02` | E02 | S4 | El mismo guion, más corto: pide el DNI y la persona se niega. |
| `ENT-L-BANCO-005` | E16 | S4 | Extracciones en un cajero que la persona no hizo. Pide el documento antes del motivo. |
| `LEG2-BA-05` | E16 | S4 | El mismo guion, más corto. |
| `ENT-L-SOPORTE-005` | E42 | S1 | Soporte técnico por un ticket de la persona: le hace instalar la asistencia remota, le pide leer el número de conexión y la guía a tipear la clave fiscal mientras mira. |

- **Seis de las siete son el mismo patrón:** un aviso de fraude del banco, que la persona no pidió, que valida identidad
  con el DNI. En cuatro, el pedido llega antes de decir para qué llama, que es el ejemplo de la propuesta. F3 y F9
  dicen que una entidad real no pide datos personales en una llamada así.
- **Los originales no lo hacen.** `LEG-BA-01` y `LEG-BA-02`, en los mismos escenarios, no piden el DNI: la validación
  aparece en la reescritura `LEG2` y en la versión larga `ENT-L`. Es el sesgo del DNI de las `LEG2` que ya marcaba #45
  (15 de 28 lo nombran).
- **Por escenario:** tocan 4 de los 47. E16 y E42 quedan sin ninguna llamada; en E01 y E02 queda la `LEG`.
- **`ENT-L-SOPORTE-005` es la menos firme.** Es un contacto pedido, así que la asistencia remota sola no cuenta (S3).
  Cuenta S1 por el número de conexión y la clave fiscal. Que el número de conexión sea un código de vinculación es
  discutible; la clave fiscal tipeada mientras el técnico mira, no tanto.

**La variante estricta suma 6:** cuatro llamadas del banco por una operación que la persona hizo y reconoce (una compra
de pasajes, una transferencia retenida y una app vinculada a un celular nuevo), que piden el DNI o sus últimos tres
números antes del motivo (`ENT-L-BANCO-003`, `LEG2-BA-03`, `ENT-L-BANCO-004` y `ENT-L-BANCO-006`), y las dos llamadas
del centro de licencias de conducir (E25), que piden DNI y fecha de nacimiento para un turno que la persona sacó. F3 no
tiene la excepción del contacto pedido; F9 sí.

**Qué no marca el criterio** y queda para la credibilidad de #145: 28 de las 40 llamadas que piden DNI u otro dato son
de empresas que no son bancos ni organismos (correo, consultorio, encuestas, ventas, soporte), y no hay fuente sobre lo
que hacen esas empresas por teléfono. Tampoco marca lo raro o lo poco natural de una llamada.

**Acuerdo.** Los dos anotadores coinciden en la marca de las 94 llamadas, en el contacto pedido y en qué señales hay.
Difieren en la entidad de 2 llamadas (`ENT-L-TRAMITE-001` y `LEG2-ST-05`, sin efecto en la marca) y en una línea de
S3. **Ese acuerdo no mide la confiabilidad de un juicio humano:** son dos corridas del mismo modelo con el mismo
paquete, y sus errores están correlacionados. Mide que el criterio se aplica sin ambigüedad.

**Huellas:** paquete `856a8f48c5b1…`, anotaciones `b1b769aefc19…` y `734633e1f82c…`; completas en el JSON. La clave
(`llamada-NNN` → `case_id`), el paquete y las anotaciones crudas quedaron fuera del repositorio, con Mateo; el JSON ya
trae cada anotación unida a su `case_id`.

## Tabla

«Propuesta» usa el criterio; «Estricta», la variante de S4 sin la excepción del contacto pedido. Cada anotador da la
entidad, si la persona pidió el contacto y las señales con su línea; «(no cuenta)» es una señal anotada que el criterio
no cuenta para esa entidad o ese contacto. Las anotaciones completas, con los motivos, están en
[`legitimas-dudosas.json`](legitimas-dudosas.json). Se regenera con `python -I corpus_desarrollo.py unir-dudosas`.

<!-- tabla:inicio -->
| Caso | Escenario | Familia | Propuesta | Estricta | Anotador 1 | Anotador 2 |
|---|---|---|---|---|---|---|
| `ENT-L-BANCO-001` | E01 | banco | **si** | si | banco, pedido: no; S4 l.3 | banco, pedido: no; S4 l.3 |
| `ENT-L-BANCO-002` | E02 | banco | **si** | si | banco, pedido: no; S2 l.18, S4 l.6 | banco, pedido: no; S2 l.18, S4 l.6 |
| `ENT-L-BANCO-005` | E16 | banco | **si** | si | banco, pedido: no; S4 l.3 | banco, pedido: no; S4 l.3 |
| `ENT-L-SOPORTE-005` | E42 | soporte | **si** | si | soporte_tecnico, pedido: si; S1 l.13, S3 l.11 (no cuenta) | soporte_tecnico, pedido: si; S1 l.13, S3 l.9 (no cuenta) |
| `LEG2-BA-01` | E01 | banco | **si** | si | banco, pedido: no; S4 l.4 | banco, pedido: no; S4 l.4 |
| `LEG2-BA-02` | E02 | banco | **si** | si | banco, pedido: no; S4 l.4 | banco, pedido: no; S4 l.4 |
| `LEG2-BA-05` | E16 | banco | **si** | si | banco, pedido: no; S4 l.4 | banco, pedido: no; S4 l.4 |
| `ENT-L-BANCO-003` | E03 | banco | **no** | si | banco, pedido: si; S4 l.5 (no cuenta) | banco, pedido: si; S4 l.5 (no cuenta) |
| `ENT-L-BANCO-004` | E33 | banco | **no** | si | banco, pedido: si; S4 l.4 (no cuenta) | banco, pedido: si; S4 l.4 (no cuenta) |
| `ENT-L-BANCO-006` | E34 | banco | **no** | si | banco, pedido: si; S4 l.4 (no cuenta) | banco, pedido: si; S4 l.4 (no cuenta) |
| `ENT-L-TRAMITE-002` | E25 | tramite | **no** | si | organismo_publico, pedido: si; S4 l.4 (no cuenta) | organismo_publico, pedido: si; S4 l.4 (no cuenta) |
| `LEG2-BA-03` | E03 | banco | **no** | si | banco, pedido: si; S4 l.4 (no cuenta) | banco, pedido: si; S4 l.4 (no cuenta) |
| `LEG2-TU-06` | E25 | medico | **no** | si | organismo_publico, pedido: si; S4 l.4 (no cuenta) | organismo_publico, pedido: si; S4 l.4 (no cuenta) |
| `ENT-L-DELIVERY-001` | E35 | delivery | **no** | no | otra_empresa, pedido: si; S4 l.15 (no cuenta) | otra_empresa, pedido: si; S4 l.15 (no cuenta) |
| `ENT-L-DELIVERY-002` | E04 | delivery | **no** | no | otra_empresa, pedido: si; S4 l.8 (no cuenta) | otra_empresa, pedido: si; S4 l.8 (no cuenta) |
| `ENT-L-DELIVERY-003` | E05 | delivery | **no** | no | otra_empresa, pedido: si; — | otra_empresa, pedido: si; — |
| `ENT-L-DELIVERY-004` | E36 | delivery | **no** | no | otra_empresa, pedido: si; S4 l.8 (no cuenta) | otra_empresa, pedido: si; S4 l.8 (no cuenta) |
| `ENT-L-DELIVERY-005` | E37 | delivery | **no** | no | otra_empresa, pedido: si; — | otra_empresa, pedido: si; — |
| `ENT-L-DELIVERY-006` | E17 | delivery | **no** | no | otra_empresa, pedido: si; S4 l.18 (no cuenta) | otra_empresa, pedido: si; S4 l.18 (no cuenta) |
| `ENT-L-ENCUESTA-001` | E06 | encuesta | **no** | no | otra_empresa, pedido: si; — | otra_empresa, pedido: si; — |
| `ENT-L-ENCUESTA-002` | E18 | encuesta | **no** | no | otra_empresa, pedido: no; — | otra_empresa, pedido: no; — |
| `ENT-L-ENCUESTA-003` | E07 | encuesta | **no** | no | otra_empresa, pedido: no; — | otra_empresa, pedido: no; — |
| `ENT-L-ENCUESTA-004` | E19 | encuesta | **no** | no | otra_empresa, pedido: si; S4 l.6 (no cuenta) | otra_empresa, pedido: si; S4 l.6 (no cuenta) |
| `ENT-L-ENCUESTA-005` | E20 | encuesta | **no** | no | organismo_publico, pedido: no; — | organismo_publico, pedido: no; — |
| `ENT-L-ENCUESTA-006` | E38 | encuesta | **no** | no | banco, pedido: si; — | banco, pedido: si; — |
| `ENT-L-MEDICO-001` | E08 | medico | **no** | no | otra_empresa, pedido: si; S4 l.5 (no cuenta) | otra_empresa, pedido: si; S4 l.5 (no cuenta) |
| `ENT-L-MEDICO-002` | E09 | medico | **no** | no | otra_empresa, pedido: si; — | otra_empresa, pedido: si; — |
| `ENT-L-MEDICO-003` | E21 | medico | **no** | no | otra_empresa, pedido: si; S4 l.3 (no cuenta) | otra_empresa, pedido: si; S4 l.3 (no cuenta) |
| `ENT-L-MEDICO-004` | E22 | medico | **no** | no | otra_empresa, pedido: si; — | otra_empresa, pedido: si; — |
| `ENT-L-SELECCION-001` | E39 | trabajo | **no** | no | otra_empresa, pedido: si; — | otra_empresa, pedido: si; — |
| `ENT-L-SELECCION-002` | E40 | trabajo | **no** | no | otra_empresa, pedido: si; — | otra_empresa, pedido: si; — |
| `ENT-L-SELECCION-003` | E41 | trabajo | **no** | no | otra_empresa, pedido: si; S4 l.10 (no cuenta) | otra_empresa, pedido: si; S4 l.10 (no cuenta) |
| `ENT-L-SOPORTE-001` | E23 | soporte | **no** | no | otra_empresa, pedido: si; S4 l.3 (no cuenta) | otra_empresa, pedido: si; S4 l.3 (no cuenta) |
| `ENT-L-SOPORTE-002` | E10 | soporte | **no** | no | otra_empresa, pedido: si; S4 l.6 (no cuenta) | otra_empresa, pedido: si; S4 l.6 (no cuenta) |
| `ENT-L-SOPORTE-003` | E11 | soporte | **no** | no | otra_empresa, pedido: si; S4 l.15 (no cuenta) | otra_empresa, pedido: si; S4 l.15 (no cuenta) |
| `ENT-L-SOPORTE-004` | E24 | soporte | **no** | no | otra_empresa, pedido: si; — | otra_empresa, pedido: si; — |
| `ENT-L-SOPORTE-006` | E43 | soporte | **no** | no | otra_empresa, pedido: si; S4 l.8 (no cuenta) | otra_empresa, pedido: si; S4 l.8 (no cuenta) |
| `ENT-L-TRAMITE-001` | E44 | tramite | **no** | no | organismo_publico, pedido: si; — | otra_empresa, pedido: si; — |
| `ENT-L-VENTAS-001` | E12 | comercial | **no** | no | otra_empresa, pedido: no; S4 l.13 (no cuenta) | otra_empresa, pedido: no; S4 l.13 (no cuenta) |
| `ENT-L-VENTAS-002` | E45 | comercial | **no** | no | otra_empresa, pedido: no; S4 l.14 (no cuenta) | otra_empresa, pedido: no; S4 l.14 (no cuenta) |
| `ENT-L-VENTAS-003` | E46 | comercial | **no** | no | banco, pedido: no; — | banco, pedido: no; — |
| `ENT-L-VENTAS-004` | E13 | comercial | **no** | no | otra_empresa, pedido: no; — | otra_empresa, pedido: no; — |
| `ENT-L-VENTAS-005` | E26 | comercial | **no** | no | otra_empresa, pedido: si; S4 l.5 (no cuenta) | otra_empresa, pedido: si; S4 l.5 (no cuenta) |
| `ENT-L-VENTAS-006` | E14 | comercial | **no** | no | otra_empresa, pedido: no; — | otra_empresa, pedido: no; — |
| `ENT-L-VENTAS-007` | E15 | comercial | **no** | no | otra_empresa, pedido: si; S4 l.11 (no cuenta) | otra_empresa, pedido: si; S4 l.11 (no cuenta) |
| `ENT-L-VENTAS-008` | E27 | comercial | **no** | no | otra_empresa, pedido: no; S4 l.12 (no cuenta) | otra_empresa, pedido: no; S4 l.12 (no cuenta) |
| `ENT-L-VENTAS-009` | E28 | comercial | **no** | no | otra_empresa, pedido: si; S2 l.17 (no cuenta) | otra_empresa, pedido: si; S2 l.17 (no cuenta) |
| `ENT-L-VENTAS-010` | E29 | comercial | **no** | no | otra_empresa, pedido: si; S4 l.8 (no cuenta) | otra_empresa, pedido: si; S4 l.8 (no cuenta) |
| `ENT-L-VENTAS-011` | E30 | comercial | **no** | no | otra_empresa, pedido: si; — | otra_empresa, pedido: si; — |
| `ENT-L-VENTAS-012` | E31 | comercial | **no** | no | otra_empresa, pedido: si; — | otra_empresa, pedido: si; — |
| `LEG-BA-01` | E01 | banco | **no** | no | banco, pedido: no; — | banco, pedido: no; — |
| `LEG-BA-02` | E02 | banco | **no** | no | banco, pedido: no; — | banco, pedido: no; — |
| `LEG-BA-03` | E03 | banco | **no** | no | banco, pedido: si; — | banco, pedido: si; — |
| `LEG-CC-01` | E12 | comercial | **no** | no | otra_empresa, pedido: no; — | otra_empresa, pedido: no; — |
| `LEG-CC-02` | E13 | comercial | **no** | no | otra_empresa, pedido: no; — | otra_empresa, pedido: no; — |
| `LEG-CC-03` | E14 | comercial | **no** | no | otra_empresa, pedido: no; — | otra_empresa, pedido: no; — |
| `LEG-CO-01` | E32 | delivery | **no** | no | otra_empresa, pedido: no_se_sabe; — | otra_empresa, pedido: no_se_sabe; — |
| `LEG-CO-02` | E04 | delivery | **no** | no | otra_empresa, pedido: si; — | otra_empresa, pedido: si; — |
| `LEG-CO-03` | E05 | delivery | **no** | no | otra_empresa, pedido: no_se_sabe; — | otra_empresa, pedido: no_se_sabe; — |
| `LEG-EN-01` | E06 | encuesta | **no** | no | otra_empresa, pedido: si; — | otra_empresa, pedido: si; — |
| `LEG-EN-02` | E18 | encuesta | **no** | no | otra_empresa, pedido: no; — | otra_empresa, pedido: no; — |
| `LEG-EN-03` | E07 | encuesta | **no** | no | otra_empresa, pedido: no; — | otra_empresa, pedido: no; — |
| `LEG-ST-01` | E23 | soporte | **no** | no | otra_empresa, pedido: si; — | otra_empresa, pedido: si; — |
| `LEG-ST-02` | E10 | soporte | **no** | no | otra_empresa, pedido: si; — | otra_empresa, pedido: si; — |
| `LEG-ST-03` | E11 | soporte | **no** | no | otra_empresa, pedido: si; — | otra_empresa, pedido: si; — |
| `LEG-TU-01` | E08 | medico | **no** | no | otra_empresa, pedido: si; — | otra_empresa, pedido: si; — |
| `LEG-TU-02` | E09 | medico | **no** | no | otra_empresa, pedido: si; — | otra_empresa, pedido: si; — |
| `LEG-TU-03` | E21 | medico | **no** | no | otra_empresa, pedido: si; — | otra_empresa, pedido: si; — |
| `LEG-VE-01` | E15 | comercial | **no** | no | otra_empresa, pedido: si; — | otra_empresa, pedido: si; — |
| `LEG-VE-02` | E27 | comercial | **no** | no | otra_empresa, pedido: no; — | otra_empresa, pedido: no; — |
| `LEG-VE-03` | E28 | comercial | **no** | no | otra_empresa, pedido: si; — | otra_empresa, pedido: si; — |
| `LEG2-CC-01` | E12 | comercial | **no** | no | otra_empresa, pedido: no; S4 l.8 (no cuenta) | otra_empresa, pedido: no; S4 l.8 (no cuenta) |
| `LEG2-CC-04` | E13 | comercial | **no** | no | otra_empresa, pedido: no; — | otra_empresa, pedido: no; — |
| `LEG2-CC-05` | E26 | comercial | **no** | no | otra_empresa, pedido: si; S4 l.6 (no cuenta) | otra_empresa, pedido: si; S4 l.6 (no cuenta) |
| `LEG2-CC-06` | E14 | comercial | **no** | no | otra_empresa, pedido: no; — | otra_empresa, pedido: no; — |
| `LEG2-CO-01` | E32 | delivery | **no** | no | otra_empresa, pedido: no_se_sabe; — | otra_empresa, pedido: no_se_sabe; — |
| `LEG2-CO-02` | E04 | delivery | **no** | no | otra_empresa, pedido: si; S4 l.6 (no cuenta) | otra_empresa, pedido: si; S4 l.6 (no cuenta) |
| `LEG2-CO-03` | E05 | delivery | **no** | no | otra_empresa, pedido: no_se_sabe; — | otra_empresa, pedido: no_se_sabe; — |
| `LEG2-CO-06` | E17 | delivery | **no** | no | otra_empresa, pedido: si; S4 l.10 (no cuenta) | otra_empresa, pedido: si; S4 l.10 (no cuenta) |
| `LEG2-EN-01` | E06 | encuesta | **no** | no | otra_empresa, pedido: si; — | otra_empresa, pedido: si; — |
| `LEG2-EN-03` | E07 | encuesta | **no** | no | otra_empresa, pedido: no; — | otra_empresa, pedido: no; — |
| `LEG2-EN-04` | E19 | encuesta | **no** | no | otra_empresa, pedido: si; S4 l.4 (no cuenta) | otra_empresa, pedido: si; S4 l.4 (no cuenta) |
| `LEG2-EN-05` | E20 | encuesta | **no** | no | organismo_publico, pedido: no; — | organismo_publico, pedido: no; — |
| `LEG2-ST-02` | E10 | soporte | **no** | no | otra_empresa, pedido: si; S4 l.6 (no cuenta) | otra_empresa, pedido: si; S4 l.6 (no cuenta) |
| `LEG2-ST-03` | E11 | soporte | **no** | no | otra_empresa, pedido: si; S4 l.4 (no cuenta) | otra_empresa, pedido: si; S4 l.4 (no cuenta) |
| `LEG2-ST-04` | E24 | soporte | **no** | no | otra_empresa, pedido: si; — | otra_empresa, pedido: si; — |
| `LEG2-ST-05` | E47 | soporte | **no** | no | soporte_tecnico, pedido: si; — | otra_empresa, pedido: si; — |
| `LEG2-TU-01` | E08 | medico | **no** | no | otra_empresa, pedido: si; S4 l.6 (no cuenta) | otra_empresa, pedido: si; S4 l.6 (no cuenta) |
| `LEG2-TU-02` | E09 | medico | **no** | no | otra_empresa, pedido: si; — | otra_empresa, pedido: si; — |
| `LEG2-TU-05` | E22 | medico | **no** | no | otra_empresa, pedido: si; — | otra_empresa, pedido: si; — |
| `LEG2-VE-01` | E15 | comercial | **no** | no | otra_empresa, pedido: si; S4 l.6 (no cuenta) | otra_empresa, pedido: si; S4 l.6 (no cuenta) |
| `LEG2-VE-04` | E29 | comercial | **no** | no | otra_empresa, pedido: si; S4 l.6 (no cuenta) | otra_empresa, pedido: si; S4 l.6 (no cuenta) |
| `LEG2-VE-05` | E30 | comercial | **no** | no | otra_empresa, pedido: si; — | otra_empresa, pedido: si; — |
| `LEG2-VE-06` | E31 | comercial | **no** | no | otra_empresa, pedido: si; — | otra_empresa, pedido: si; — |
<!-- tabla:fin -->
