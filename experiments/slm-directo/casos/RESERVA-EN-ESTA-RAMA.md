# La reserva está en esta rama

`reserva/test` es `laboratorio-main` más un commit con la reserva de test. Se armó el 2026-11-10, al retirar
`laboratorio-luciano`, por decisión de Mateo. Qué hay en cada rama: [catálogo de conversaciones](CATALOGO-CONVERSACIONES.md).

## Qué trae

- **Los 200 casos reservados del corpus v2:** `texto/CV2-T-*` y `referencia/CV2-T-*`, y sus filas en
  [`CATALOGO-ESCENARIOS.csv`](../../../docs/corpus/CATALOGO-ESCENARIOS.csv). Sus huellas están en
  [`MANIFIESTO-CORPUS-V2.json`](MANIFIESTO-CORPUS-V2.json), y `python casos.py` las verifica.
- **Las 56 legítimas entrantes de test de [#45](https://github.com/Corchets/bitacora_tesis/issues/45):**
  [`legitimas-entrantes-test.jsonl`](legitimas-entrantes-test.jsonl). Todavía no están en el formato de casos.
- **El alcance de la reserva anotado a ciegas:** [`alcance-reserva.json`](alcance-reserva.json). El método está en
  [TEST-ALCANCE.md](TEST-ALCANCE.md), y las instrucciones del generador del lote nuevo, en
  [INSTRUCCIONES-GENERADOR-TEST.md](INSTRUCCIONES-GENERADOR-TEST.md).

## Cómo se usa

- Se mira una sola vez, en la evaluación final, con la configuración congelada y las reglas escritas antes
  ([ADR 0005](../../../docs/ingenieria/adr/0005-reglas-de-evaluacion-escritas-antes-de-correr.md)). Sigue valiendo
  [R05](../../../docs/gestion/REGISTRO-RIESGOS.md): es pública desde el 2026-10-23.
- Los merges van de `laboratorio-main` hacia esta rama, con merge commit: `git merge origin/laboratorio-main`. Después,
  `python correr.py --particion test_reservado …`.
- En `laboratorio-main` la reserva no está: ahí `casos/RESERVA-FUERA-DEL-REPO.md` hace que `casos.py` falle si
  aparece un `CV2-T-*`.
