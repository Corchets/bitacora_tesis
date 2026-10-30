# Supervisión contextual #99 — estado BORRADOR (2026-10-29)

> **Borrador NO apto para entrenar.** El coordinador reprodujo etiquetas
> incorrectas en un caso legítimo explícito, por definición de los prompts
> actuales (`construir_prompt_pasada1/_pasada2` en
> [supervision_tito_99.py](supervision_tito_99.py)).
> La corrección de prompts la hace otro corrector (ctx_21184cb827b1);
> este worker no los modifica.

- **Alcance anotado:** 33 de 543 prefijos (solo entrenamiento/validación
  según particiones). Faltan 510, visibles por re-ejecución del módulo.
- **Distribución del borrador:** 25 `entrenamiento/0` + 8 `validacion/0`;
  ningún `1` ni `null`. Indicio adicional de sesgo del prompt actual.
- **Anotador del borrador:** `qwen3.5:4b` vía `http://127.0.0.1:11435`
  (digest y versión Ollama guardados por registro en el JSONL).
- **Puerta:** `puede_entrenar()` sigue BLOQUEADA (faltantes + sin clase 1
  + auditoría en curso). No se entrenó nada ni se tocó `entrenar_tito_99.py`.
