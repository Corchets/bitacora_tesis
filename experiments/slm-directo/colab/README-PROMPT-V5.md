# Prompt v5 en Google Colab: cómo empezar a detectar las estafas sin pedido

> **Estado: propuesta sin discutir.** Prueba de desarrollo sobre los **150 casos escritos**, con referencias
> y roles sin revisión humana. Sigue la dirección de Luciano del 2026-11-05 de modificar el detector para avisar esas
> estafas. No reemplaza la configuración del
> [ADR 0001](../../../docs/ingenieria/adr/0001-parakeet-filtro-y-gemma4-e2b-con-tito-viejo.md) ni resuelve
> [D07](../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) ni
> [D08](../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).
> La rama no contiene el test reservado.

**Resultados:** [análisis del 2026-11-05](../corridas/2026-11-05_prompt-v5-tito-sin-indicio/analisis.md).

## Qué se corre

Cuatro condiciones en la misma sesión, todas con Tito viejo → SLM sin indicio, `gemma4:e2b-it-q4_K_M`, `num_ctx` 4096, seed 42,
hablantes `rol` y `--seguir-tras-aviso`. Cada una da el primer aviso y además permite simular persistencia.

| Corrida | Prompt | Qué cambia respecto de [v4](../prompts/tarea_v4.txt) | Qué responde |
|---|---|---|---|
| **a** | [`tarea_v5_maniobras.txt`](../prompts/tarea_v5_maniobras.txt) | Avisa si OTRA intenta aislar a PROTEGIDA, aunque todavía no pida nada | ¿Avisa las estafas sin pedido sin sumar falsas alarmas? |
| **b** | [`tarea_v5.txt`](../prompts/tarea_v5.txt) | Los tres cambios juntos | ¿Se acerca a la meta? |
| **c** | [`tarea_v5_indirectos.txt`](../prompts/tarea_v5_indirectos.txt) | Cuenta pedidos en condicional, parciales y «escribila vos» | ¿Recupera FAMILIAR, SOPORTE-005 y SOPORTE-006? |
| **d** | [`tarea_v5_sin_excepcion.txt`](../prompts/tarea_v5_sin_excepcion.txt) | Saca la excepción de datos comunes, que no evitaba sus 7 alarmas | ¿Recupera PREMIO-003 y ORGANISMO_PREVISIONAL-004 sin sumar alarmas? |

## Controles de maniobras

El corpus no tiene ninguna legítima con un «no cortes» genuino, así que la regla **a** daría bien en los 150 sin estar probada. Por
eso se corren aparte [18 controles](../casos/controles-maniobras.json): 12 legítimas con pedidos genuinos de no cortar o de guardar
reserva y 6 estafas sin pedido con otras palabras. Se corren con v4, `v5-maniobras` y `v5`.

**No se suman a los 150** ni cambian el denominador de nadie. Son redacción asistida, sin revisión humana, y los escribió quien escribió
la regla: sirven para encontrar problemas, no para probar que no los hay. Conviene que alguien del equipo agregue otros sin leer el prompt.

## Pasos

1. Abrir [`COLAB-PROMPT-V5.ipynb`](COLAB-PROMPT-V5.ipynb) en Colab con la URL de GitHub fijada a un commit.
2. Verificar GPU T4, ejecutar la celda y dejar la pestaña abierta.
3. Cada corrida terminada se descarga como `parcial-prompt-v5-<a|b|c|d>.zip`; el final es `resultados-prompt-v5.zip`.

**Sin Drive por defecto:** montarlo daría al notebook escritura sobre todo Google Drive. Si Colab se corta, lo no
descargado se pierde.

Cada condición tarda unos 18 minutos, más unos 10 de instalación y unos 15 de controles: **alrededor de hora y media**.
