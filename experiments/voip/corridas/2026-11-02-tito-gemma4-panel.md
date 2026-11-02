# Tito viejo con Gemma 4 en el panel (2026-11-02)

Comprobación de punta a punta en la notebook de demo. Sirve para ubicar demoras y ver que el
recorrido funciona; **no es rendimiento del detector** ni resuelve
[D09](../../../docs/gestion/MAPA-DECISIONES.md#d09--elegir-asr-y-detector). La elección de estos dos
modelos sale de la [matriz #101](../../slm-directo/corridas/2026-10-30_112956_101_informe_101.md),
sobre 20 conversaciones sintéticas sin revisión humana.

- **Máquina:** Apple M1 con 8 GB, Ollama 0.40.5. La matriz corrió en un Ryzen 7 7700X con 30,5 GB y GPU.
- **Datos:** ejemplos TTS fuera de `corpus_v2` (`SC-WA-CODE-01`, `SC-SOPORTE-CLAVE-01`, `LG-SUPPORT-INFO-01`).
- **Configuración:** ASR Zipformer, prompt `tarea`, `num_ctx` 4096, seed 42, disparo al cerrar la frase.
- **Tito viejo:** `tito_logreg.json`, sha256 `fb601eaa…5098eccd`, frase aislada, umbral 0,5.
- **SLM:** `gemma4:e2b-it-q4_K_M`, digest `b37049369adf…`, el mismo artefacto de la matriz.
- **Código:** `26d1d31` con los cambios del panel sin commit.

| Ejemplo | Comando | Resultado | Evaluaciones | Mediana por evaluación | Máximo |
|---|---|---|---|---|---|
| `SC-WA-CODE-01` (estafa) | `medir.py` | aviso a +1,39 s del fin del pedido | 3 | 4,02 s | 7,70 s |
| `SC-SOPORTE-CLAVE-01` (estafa) | panel en Chrome | aviso a los 42,5 s, con cita del pedido de contraseña | 8 | 1,80 s | 3,25 s |
| `LG-SUPPORT-INFO-01` (legítima) | panel en Chrome | sin aviso; 7 frases sin consulta y Tito activó en la octava | 14 (1 salteada) | 1,45 s | 5,22 s |

Sin fallos del detector. Tito tarda unos 30 ms por frase, con 0,48 GB de memoria, y reproduce el
puntaje de 0,5712 del [diagnóstico #98](../../slm-directo/DIAGNOSTICO-TITO-2026-10-29.md) en otra máquina.

![Aviso en Presentación](2026-11-02-tito-gemma4-aviso-1366x900.png)

## Lo que hay que saber

- **Tag completo:** en esta Mac, `gemma4:e2b` baja otro artefacto (MLX `nvfp4`, 7,5 GB, digest
  `45d11505…`) que pide 6,9 GiB y no carga: había 4,8 GiB libres. Por eso el panel usa `-it-q4_K_M`.
- **Memoria en el informe #101:** Ollama informa 0,31 GB para este modelo cargado también acá, así que
  los 0,5 GB de `gemma4` en ese informe no miden lo que ocupa. El archivo pesa 4,59 GB.
- **`gemma4:e4b-it-q4_K_M` (6,58 GB, digest `dc35e8d9c606…`):** carga en esta Mac, pero entra en swap.
  Con `SC-WA-CODE-01` dio 46,3 s y 15,8 s por evaluación, 3 frases salteadas y el aviso a +49,0 s del
  pedido. No sirve en vivo con 8 GB; para usarlo hay que pasar `--ollama-url` con la PC con GPU.
- **Una sola llamada por ejemplo:** no alcanza para comparar con otros detectores.
