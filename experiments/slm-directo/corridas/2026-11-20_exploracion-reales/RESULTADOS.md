# #52, exploración con los conjuntos reales: corridas con texto de la reserva

Corrida del 2026-11-20 en Colab T4, con el tag `colab/52-exploracion-reales-2` (`7c52850`). Es posterior a la
evaluación final y no la reemplaza. Estos CSV traen el texto del test reservado, por eso viven en `reserva/test` y no
en `laboratorio-main`.

- `test_reservado/base/`: la única corrida sobre el test, con `c-consejos-corte-riesgo` en todas las líneas de OTRA.
  Ningún candidato pasó la regla, así que el test no corrió con ningún otro prompt.
- `desarrollo/`: los siete prompts sobre `alcance-140`.
- `humo/`: el humo de formato de los siete.
- `fase-2.json`: lo que dijo la regla en Colab. `commit.txt`, `digest.txt`, `script-sha256.txt` y los demás: los
  metadatos de la sesión.
- **No están acá** las corridas del set externo de #144, las de las legítimas reales de CallCenterEN ni la de la zona
  gris: sus fuentes prohíben redistribuir derivados. Quedan en custodia, en el ZIP `resultados-exploracion-reales.zip`.

El análisis, con cifras e identificadores, está en la rama `exp/52-exploracion-reales`:
`experiments/slm-directo/corridas/2026-11-20_exploracion-reales/analisis.md`.
