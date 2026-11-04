# Prompt v3 con Gemma 4 E2B, en Google Colab

> **Estado: propuesta sin discutir.** Prueba de desarrollo sobre los **150 casos
> escritos** (75 de vishing y 75 legítimos), con referencias provisionales sin
> revisión humana. Cambia el prompt de la configuración del
> [ADR 0001](../../../docs/ingenieria/adr/0001-parakeet-filtro-y-gemma4-e2b-con-tito-viejo.md)
> **solo como prueba**; no la reemplaza ni resuelve
> [D08](../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).
> La rama parte de `slm-sin-indicio` y no contiene el test reservado.

## Qué se corre

Tres condiciones en la misma sesión, todas con [`tarea_v3.txt`](../prompts/tarea_v3.txt)
(`--prompts v3`), `gemma4:e2b-it-q4_K_M`, hablantes `ab`, `num_ctx` 4096, seed 42 y
corte al primer aviso, como las dos corridas de 150 con v1:

| Corrida | Detector | Qué recibe el SLM |
|---|---|---|
| **a** | `slm` | La conversación, en cada línea |
| **a** | `tito-slm` | La conversación y el bloque de indicio, desde que Tito activa |
| **b** | `tito-slm-sin-indicio` | La misma conversación que `slm`, desde que Tito activa |

No hay control v1 en esta sesión ni repetición del SLM solo. Comparar contra las corridas
de Windows con v1 mezcla el efecto del prompt con el de la máquina, y una diferencia de
1–3 casos no se puede leer como efecto. El artefacto de Tito es el mismo: en Windows
registra otro SHA-256 solo por los saltos de línea CRLF del archivo.

## Pasos

1. Abrir [`COLAB-PROMPT-V3.ipynb`](COLAB-PROMPT-V3.ipynb) en Colab desde GitHub:
   `https://colab.research.google.com/github/Corchets/bitacora_tesis/blob/prompt-v3-colab/experiments/slm-directo/colab/COLAB-PROMPT-V3.ipynb`.
2. Verificar GPU T4, ejecutar la celda y dejar la pestaña abierta.
3. Cada corrida terminada se descarga como `parcial-prompt-v3-<a|b>.zip`; el ZIP final,
   `resultados-prompt-v3.zip`, incluye todo y `comparacion.md`.

**Sin Drive por defecto:** montarlo daría al notebook escritura sobre todo Google Drive. Si
Colab se corta, lo no descargado se pierde y hay que volver a correrlo. Para reanudar desde
Drive, usar `COLAB_GUARDAR_EN_DRIVE = '1'` y autorizarlo desde la cuenta.

Con la referencia de ≈ 15 minutos para 1.179 consultas, **a** tarda ≈ 45 min y **b** ≈ 15 min,
más ≈ 10 min de instalación. El prompt es más largo y puede tardar más. No es una medición
de rendimiento en teléfono.
