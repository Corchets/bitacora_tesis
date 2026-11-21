# solo-el-numero — 2026-11-21

Prueba rápida del punto 2 de [#172](https://github.com/Corchets/bitacora_tesis/issues/172) con la configuración final
([ADR 0008](../../../../docs/ingenieria/adr/0008-prompt-del-detector-c-consejos.md)).

## Qué cuenta como «anda bien» (escrito antes de correr la comparación)

> **Estado: propuesta sin discutir.** La decisión de adoptar el cambio es de Mateo.

Con el mismo servidor y el mismo runtime para las dos variantes:

1. Todas las consultas válidas en las dos.
2. Cada conversación avisa o no avisa igual, y el primer aviso cae en la misma línea, en todas.
3. Las líneas en que cambia el riesgo sin mover el punto 2 se informan aparte, separando las que cruzan 0,3 de las
   que no. Como piso de comparación va la misma configuración de hoy corrida dos veces en el mismo servidor.
