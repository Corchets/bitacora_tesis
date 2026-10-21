---
name: actualizar-ayuda-memoria
description: Revisa y actualiza los briefs de arranque del ayuda memoria visual del proyecto.
---

# Actualizar ayuda memoria

Mantener explicaciones breves que permitan a una persona retomar un issue sin
reconstruir el proyecto entero. La web está en `ayuda-memoria/`; su operación y
formato de briefs están en [README.md](../../../ayuda-memoria/README.md).

## Revisión

1. Leer `docs/gestion/MAPA-DECISIONES.md` y generar datos actuales con
   `npm run build`, desde `ayuda-memoria/`. Si no puede consultar las fuentes,
   informar el bloqueo; una copia vieja no acredita una revisión actual.
2. Abrir `ayuda-memoria/dist/data.json` y `ayuda-memoria/briefs.json`. Revisar los
   briefs pendientes del hito activo y los issues que pidió el usuario. Trabajar
   por rama: un documento de `main` no acredita lo que existe en laboratorio.
3. Leer el issue completo, sus dependencias nativas y los documentos que disparan
   la tarea en la revisión indicada por `data.json`. Usar enlaces a esos archivos
   y secciones, incluyendo código o resultados si ayudan a empezar.
4. Redactar o corregir en `briefs.json`: resultado concreto, pocas lecturas
   necesarias con su propósito, primer paso ejecutable y evidencia de terminado.
   Conservar `sources` y registrar la huella de las fuentes efectivamente leídas
   con el comando `npm run revisar-brief -- <rama> <numero>`.
5. Generar y verificar otra vez. Comprobar que cada brief revisado aparece vigente,
   que los enlaces existen en esa rama y que los demás mantienen su estado real.

## Criterio editorial

- El brief es una orientación derivada; GitHub conserva estado, responsable,
  milestone y bloqueos. La web no asigna trabajo ni cambia prioridades.
- Usar el significado del glosario de cada rama. Conservar condiciones como
  «propuesta sin discutir», decisión abierta o medición solo en PC.
- Un issue bloqueado puede tener contexto para prepararse; el primer paso debe
  respetar el bloqueo. Una fuente inexistente debe quedar visible como pendiente.
- Si una elección técnica todavía está abierta, enlazarla y presentar el paso como
  propuesta; resolverla requiere el acuerdo correspondiente.
- Registrar la huella solo después de leer y revisar esas fuentes. No renovar
  todas las huellas para ocultar pendientes.
- Modificar únicamente los briefs y su documentación si cambió el contrato del
  ayuda memoria. Publicar, editar issues, integrar ramas o hacer commits requiere
  autorización propia; invocar esta skill no la agrega.

## Terminado

Reportar issues y ramas revisados, verificaciones, pendientes y bloqueos reales.
Un brief sin contexto suficiente conserva el estado pendiente, sin rellenarlo
con instrucciones inventadas.
