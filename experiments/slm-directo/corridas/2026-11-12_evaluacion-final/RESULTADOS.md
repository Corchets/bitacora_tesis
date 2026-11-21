# #52, evaluación final: corridas con texto de la reserva

Corrida única del 2026-11-19 en Colab T4, con el tag `colab/143-evaluacion-final-2` (`87bb745`) y la configuración
`c-consejos-corte-riesgo`. Estos CSV traen el texto del test reservado, por eso viven en `reserva/test` y no en
`laboratorio-main`.

- `test_reservado/`, `desarrollo/` y `humo/`: las corridas de la configuración, `v4-corte` y las reglas.
- `commit.txt`, `control-desarrollo.txt`, `digest.txt`, `script-sha256.txt` y los demás: los metadatos de la sesión.
- **No están acá** las corridas del set externo de #144 ni las de las legítimas reales de CallCenterEN: sus fuentes
  prohíben redistribuir derivados. Quedan en custodia, en el ZIP `resultados-evaluacion-final.zip`.

El análisis, con cifras e identificadores, está en `laboratorio-main`:
`experiments/slm-directo/corridas/2026-11-12_evaluacion-final/analisis.md`.
