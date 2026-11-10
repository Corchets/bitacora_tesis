# La reserva no está en esta rama

> **Nota del 2026-11-10 (Mateo):** `laboratorio-luciano` se retira. La reserva, sus filas del catálogo, las 56
> legítimas de test y el alcance anotado a ciegas de [#45](https://github.com/Corchets/bitacora_tesis/issues/45)
> pasan a la rama `reserva/test`: `laboratorio-main` más un commit con la reserva y sin esta marca. Esa rama nunca
> se mergea a `laboratorio-main` ni a `main`; para la evaluación final se mergea `laboratorio-main` en ella. Qué hay
> en cada lado: [catálogo de conversaciones](CATALOGO-CONVERSACIONES.md).

Los 200 casos reservados del corpus v2 (`CV2-T-*`) y sus filas del catálogo (`*-CV2-T-*`)
quedaron fuera de esta rama a propósito. Desde el 2026-10-23 están públicos en
`laboratorio-luciano`, por decisión de Luciano: no correrlos ni mirarlos hasta la evaluación
final, y usarlos como test solo con modelos publicados antes de esa fecha
([R05](../../../docs/gestion/REGISTRO-RIESGOS.md)). Sus huellas SHA-256 siguen en
[`MANIFIESTO-CORPUS-V2.json`](MANIFIESTO-CORPUS-V2.json).

Con este archivo presente, `casos.py` valida solo el desarrollo y falla si aparece algo de
la reserva. Ver [README §Copia pública](README.md#copia-pública-laboratorio-main). No
borrar este archivo ni agregar casos `CV2-T-*` a esta rama.
