# Revisión cruzada del consolidado Tito→SLM (#74)

Estado al 2026-10-26: **pendiente**. Nadie más revisó todavía este
consolidado; no se declara ninguna reproducción de inferencia ajena.

## Alcance de la revisión solicitada

1. Ejecutar `bash analisis/2026-10-26-tito-slm-consolidado/regenerar.sh`
   desde la raíz y confirmar «todo idéntico byte a byte».
2. Abrir `cobertura.json`: 96 evaluaciones, 0 errores, 6 digests coincidentes.
3. Recorrer un `comparacion.md` y contrastar dos filas contra su
   `actualizaciones.csv` (derivación, aviso, motivo, evidencia).
4. Revisar [CONSOLIDADO.md](CONSOLIDADO.md) §§2–4 y marcar cualquier número
   que no trace a [TABLAS.md](TABLAS.md) o a un `comparacion.md`.
5. Confirmar que no se afirma rendimiento móvil, generalización ni ahorro por
   contar consultas, y que activación e indicio no se separan causalmente.

## Registro

- Revisor/a: _(pendiente)_ — fecha: _(pendiente)_ — resultado: _(pendiente)_.
- Límite declarado: la revisión cubre procedimiento, regeneración y errores;
  no incluye repetir inferencia con Ollama (runtimes históricos del 2026-10-26).

## Intentos de asignación (2026-10-26)

- Pedido de slot de revisión al coordinador vía `ask`: rechazado — el
  Dispatch de la tarea ya estaba cerrado (`ask requires an active supervised
  Dispatch`).
- Escalación al coordinador vía `send --type escalation`: rechazada — la
  capability del Dispatch está revocada.
- Acción requerida: el coordinador debe asignar un revisor en un Dispatch
  activo (o informar revisor+fecha+resultado de una revisión ya hecha) para
  completar este registro. Hasta entonces el estado sigue pendiente y no se
  declara ninguna revisión.
