# Tanda de roles con Tito sin indicio, en Google Colab

> **Estado: propuesta sin discutir.** Prueba de desarrollo sobre los **150 casos escritos**, con referencias
> y roles sin revisión humana. No reemplaza la configuración del
> [ADR 0001](../../../docs/ingenieria/adr/0001-parakeet-filtro-y-gemma4-e2b-con-tito-viejo.md) ni resuelve
> [D08](../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).
> La rama no contiene el test reservado.

## Qué se corre

Cuatro condiciones en la misma sesión, todas con Tito viejo → SLM sin indicio, `gemma4:e2b-it-q4_K_M`,
`num_ctx` 4096, seed 42 y hablantes `rol`:

| Corrida | Prompt | Corte | Qué responde |
|---|---|---|---|
| **a** | [`tarea.txt`](../prompts/tarea.txt) | Primer aviso | Si la demo actual gana o pierde al usar el canal |
| **b** | [`tarea_v4_cita_libre.txt`](../prompts/tarea_v4_cita_libre.txt) | Primer aviso | Si v4 recupera SOPORTE-003 y SOPORTE-006 sin exigir que la cita sea de OTRA |
| **c** | [`tarea_v3_orden_v1.txt`](../prompts/tarea_v3_orden_v1.txt) | Primer aviso | El efecto de los roles sin la cita primero |
| **d** | [`tarea_v4.txt`](../prompts/tarea_v4.txt) | `--seguir-tras-aviso` | Si las alarmas se sostienen después del primer aviso |

`tarea_v4_cita_libre.txt` cambia solo la instrucción de la evidencia de v4, que vuelve a la de v1.

## Pasos

1. Abrir [`COLAB-TANDA-ROLES.ipynb`](COLAB-TANDA-ROLES.ipynb) en Colab con la URL de GitHub fijada a un commit.
2. Verificar GPU T4, ejecutar la celda y dejar la pestaña abierta.
3. Cada corrida terminada se descarga como `parcial-tanda-roles-<a|b|c|d>.zip`; el final es `resultados-tanda-roles.zip`.

**Sin Drive por defecto:** montarlo daría al notebook escritura sobre todo Google Drive. Si Colab se corta, lo no
descargado se pierde.

Cada condición tarda unos 11 minutos, más unos 10 de instalación; la **d** puede tardar más.
