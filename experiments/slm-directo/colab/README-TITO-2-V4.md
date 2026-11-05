# v4 con roles, Tito viejo 2.0 y SLM solo, en Google Colab

> **Estado: propuesta sin discutir.** Prueba de desarrollo sobre los **150 casos escritos**, con referencias
> y roles sin revisión humana. No reemplaza la configuración del
> [ADR 0001](../../../docs/ingenieria/adr/0001-parakeet-filtro-y-gemma4-e2b-con-tito-viejo.md) ni resuelve
> [D08](../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).
> La rama no contiene el test reservado. Seguimiento: [#140](https://github.com/Corchets/bitacora_tesis/issues/140).

**Resultados:** [análisis del 2026-11-05](../corridas/2026-11-05_tito-2-v4/analisis.md).

## Qué se corre

Dos condiciones en la misma sesión, con [`tarea_v4.txt`](../prompts/tarea_v4.txt), hablantes `rol`, `gemma4:e2b-it-q4_K_M`,
`num_ctx` 4096, seed 42 y corte en el primer aviso:

| Corrida | Detector | Qué responde |
|---|---|---|
| **a** | Tito viejo 2.0 → SLM ([`tito_viejo_2.py`](../tito_viejo_2.py)) | ¿Las frases agregadas cambian algo con v4? |
| **b** | SLM solo, sin Tito | ¿Qué pasa si Tito salta siempre? v4 todavía no se corrió sin Tito |

## Qué esperamos, escrito antes de correr

Con Tito viejo y v4 da 55/75 estafas y 13/75 falsas alarmas, repetido dos veces.

- **a: 55/13.** Las frases adelantan la activación en un solo caso, `CV2-D-L-BANCO-002` (de la línea 7 a la 6), que ya
  es falsa alarma con v4. Sale de los puntajes de Tito ya registrados. Cualquier otro cambio se lee como ruido de la corrida.
- **b: alrededor de 56 estafas y entre 18 y 25 falsas alarmas.** Sacar a Tito solo sumó `CV2-D-V-PREMIO-001` con v1
  (de 54/14 a 55/19) y con v3 (de 64/35 a 65/47). Es una extrapolación de otros prompts, no una medición.

## Pasos

1. Abrir [`COLAB-TITO-2-V4.ipynb`](COLAB-TITO-2-V4.ipynb) en Colab con la URL de GitHub fijada a un commit.
2. Verificar GPU T4, ejecutar la celda y dejar la pestaña abierta.
3. Cada corrida terminada se descarga como `parcial-tito-2-v4-<a|b>.zip`; el final es `resultados-tito-2-v4.zip`.

**Sin Drive por defecto:** montarlo daría al notebook escritura sobre todo Google Drive. Si Colab se corta, lo no
descargado se pierde.

La **a** tarda unos 11 minutos y la **b**, unos 25, más unos 10 de instalación: **alrededor de 45 minutos**. Si solo
interesa la **a**, se puede cortar la sesión después de que baje su ZIP.
