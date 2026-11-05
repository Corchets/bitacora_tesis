# Prompt v4 con Tito sin indicio, en Google Colab

> **Estado: propuesta sin discutir.** Prueba de desarrollo sobre los **150 casos escritos**, con referencias
> y roles sin revisión humana. No reemplaza la configuración del
> [ADR 0001](../../../docs/ingenieria/adr/0001-parakeet-filtro-y-gemma4-e2b-con-tito-viejo.md) ni resuelve
> [D08](../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).
> La rama no contiene el test reservado.

## Qué se corre

Cuatro condiciones en la misma sesión, todas con Tito viejo → SLM sin indicio, `gemma4:e2b-it-q4_K_M`,
`num_ctx` 4096, seed 42 y corte al primer aviso:

| Corrida | Prompt | Hablantes | Qué responde |
|---|---|---|---|
| **a** | [`tarea_v4.txt`](../prompts/tarea_v4.txt) | `rol` | Si todo junto se acerca a la meta |
| **b** | [`tarea_v3.txt`](../prompts/tarea_v3.txt) | `rol` | Cuánto pesa que el SLM sepa a quién protege |
| **c** | [`tarea_v3_orden_v1.txt`](../prompts/tarea_v3_orden_v1.txt) | `ab` | Cuánto pesa el orden de los campos |
| **d** | [`tarea.txt`](../prompts/tarea.txt) | `ab` | Control v1 en la misma sesión |

Con `rol`, cada línea llega al SLM como `PROTEGIDA:` u `OTRA:`, según
[`casos/roles-protegida.json`](../casos/roles-protegida.json). Es lo que en una llamada daría el canal de cada persona.
Tito recibe solo el texto de la línea, igual que antes.

## Pasos

1. Abrir [`COLAB-PROMPT-V4.ipynb`](COLAB-PROMPT-V4.ipynb) en Colab con la URL de GitHub fijada a un commit.
2. Verificar GPU T4, ejecutar la celda y dejar la pestaña abierta.
3. Cada corrida terminada se descarga como `parcial-prompt-v4-<a|b|c|d>.zip`; el final es `resultados-prompt-v4.zip`.

**Sin Drive por defecto:** montarlo daría al notebook escritura sobre todo Google Drive. Si Colab se corta, lo no
descargado se pierde.

Cada condición tarda unos 11 minutos, más unos 10 de instalación.
