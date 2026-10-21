---
name: actualizar-ayuda-memoria
description: Actualiza roadmap, briefs y cierre documental de un issue terminado y prepara su PR; acompaña integración y deploy cuando se solicitan. También permite revisar solo briefs.
---

# Actualizar ayuda memoria

Convertir el trabajo de un issue en avances trazables en la ayuda memoria y un
PR listo para revisión. Operación y formatos en el
[README](../../../ayuda-memoria/README.md); fuentes y cierre en
[AGENTS.md](../../../AGENTS.md) y el
[método de trabajo](../../../docs/gestion/METODO-DE-TRABAJO.md).

## Pedido y alcance

Ejemplo para ejecutar el circuito completo hasta el PR:

```text
$actualizar-ayuda-memoria terminé el issue #50; actualizá el seguimiento y prepará el PR hacia laboratorio-main.
```

- Un pedido de cierre con PR comprende los cambios afectados, verificaciones,
  commit, push de la rama de trabajo y creación o actualización del PR.
- Si el usuario pide «integrar y publicar», continuar hasta el merge y la
  comprobación del deploy, respetando revisiones y reglas del repositorio.
- Si pide «solo briefs», aplicar únicamente el apartado de briefs y su
  verificación local. Conservar este uso de la versión anterior.
- La invocación de cierre usa el alcance de `default_prompt`: seguimiento y PR.
  Inferir el issue de la sesión o rama actual; si falta o hay varios posibles,
  pedir el número y avanzar con las comprobaciones independientes. Respetar
  límites explícitos como «solo local» y las autorizaciones ya expresadas. La
  skill describe el procedimiento; los permisos proceden del pedido del usuario.

La rama destino habitual es `laboratorio-main`; usar otra si el usuario la pide.
GitHub sigue siendo el backlog. Preparar el comentario de cierre; publicarlo o
editar/cerrar el issue requiere que el pedido incluya esas acciones.

## 1. Contrastar trabajo y evidencia

Leer primero el [mapa de decisiones](../../../docs/gestion/MAPA-DECISIONES.md).
Inspeccionar estado de Git, rama, remoto e issue completo con sus dependencias
nativas; luego cargar solo sus fuentes técnicas. Contrastar los cambios y
artefactos con cada criterio de terminado. Una corrida, borrador o commit permite
registrar un avance parcial, sin acreditar validación ni cerrar decisiones.

Conservar cambios ajenos a la tarea. Para preparar un PR desde una rama
compartida, crear una rama de trabajo y seleccionar explícitamente los archivos
del issue. Si el issue es ambiguo o una decisión abierta impide continuar,
explicar el punto concreto y pedirlo sin inventar una respuesta.

**Salida:** issue, rama destino, cambios afectados y evidencia suficiente para
distinguir terminado, parcial y pendiente.

## 2. Actualizar las fuentes afectadas y el roadmap

Actualizar primero la fuente técnica primaria, si la evidencia la volvió
desactualizada. En `ayuda-memoria/roadmap.json`:

- Ubicar los componentes de `systemMap` relacionados con el issue. Corregir
  `exists`, `missing` y `artifacts` y asociar el número en `issues` cuando
  corresponda. Mantener una sola relación componente → issues.
- Revisar `parallelFronts`, `currentLocation` y sus próximos pasos solo donde el
  resultado cambie la orientación. Actualizar `updatedAt` con fecha absoluta.
- Enlazar evidencia real y conservar sus límites y procedencia por rama.
  Mantener visibles los componentes que todavía carecen de issue específico.

Los estados, responsables y bloqueos se leen de GitHub. Evitar porcentajes o
estados manuales que los dupliquen; `not_planned` no es trabajo completado.
Preservar el visor de arquitectura salvo que modificarlo sea parte del pedido.
Las decisiones abiertas conservan el rótulo y enlace exigidos por AGENTS.md.

**Salida:** los componentes afectados explican qué existe, qué falta y en qué
artefactos e issues se basa, sin cambiar el seguimiento de otros frentes.

## 3. Revisar los briefs afectados

Generar datos desde `ayuda-memoria/` con `npm run build` y consultar
`dist/data.json`, `briefs.json` y las fuentes del issue. Si la consulta falla,
informar el fallo; una copia vieja no acredita una revisión actual.

Revisar únicamente los briefs afectados, por rama: resultado, pocas fuentes con
su propósito, primer paso ejecutable y evidencia de terminado. El primer paso
respeta dependencias y condiciones documentales. Un documento de main no prueba
lo que existe en laboratorio. Los issues cerrados pueden salir de la vista de
abiertos; no reabrirlos para generar un brief.

El build lee fuentes **remotas**, no los cambios locales sin integrar. Comparar
las fuentes locales modificadas con el commit indicado por el snapshot. Cuando
las fuentes revisadas ya estén en esa revisión remota, registrar solo su huella:

```bash
npm run revisar-brief -- laboratorio-main 50
npm run build
```

Adaptar rama y número al issue real. Si las fuentes todavía están en la rama de
trabajo, redactar el brief y dejar su revisión pendiente; no acreditar la
versión local con una huella de la rama destino. En el modo de publicación,
retomar esta revisión después de integrar las fuentes. Si requiere persistir
una huella nueva, incluir únicamente ese ajuste en un PR de seguimiento y
respetar el alcance de integración autorizado.

**Salida:** briefs revisados contra la revisión correcta o pendientes con un
motivo concreto; conservar los demás sin renovar huellas en lote.

## 4. Verificar y completar el cierre documental

Ejecutar las comprobaciones relevantes para el cambio y las de la web declaradas
en `package.json`. Revisar el build, enlaces relativos y fuentes de la rama
destino; comprobar la vista modificada en navegador si está disponible e informar
el límite si no lo está. Mantener `dist/`, audio, datos identificables, secretos
y cachés generados fuera del commit.

Aplicar el cierre de AGENTS.md: bitácora semanal con artefacto observable;
decisiones y riesgos solo si hubo una novedad respaldada. Preparar el comentario
de GitHub con evidencia, límites y próxima acción. Usar `Closes #N` únicamente
si se cumple el objetivo completo; para entregas parciales usar `Refs #N`.

**Salida:** verificaciones registradas y diferencias listas para revisión. No
presentar una preparación local como integración o publicación realizada.

## 5. Preparar el PR cuando esté solicitado

Actualizar las referencias remotas y simular la integración con la rama destino
sin alterar su árbol de trabajo. Resolver conflictos técnicos trazables; pedir
la decisión si el conflicto afecta acuerdos de tesis o evidencia contradictoria.

Con el alcance autorizado, crear el commit del trabajo revisado, hacer push
normal de su rama y crear o actualizar su PR hacia el destino. Reutilizar un PR
abierto existente para la misma entrega. Cuerpo: resultado, evidencia,
verificaciones, límites e issue relacionado; conservar trabajo ajeno fuera.

**Salida por defecto del pedido con PR:** URL del PR, resultado de la simulación
y estado real de las verificaciones. Un PR abierto todavía no publica la web.

## 6. Integrar y comprobar Vercel cuando esté solicitado

Integrar solo el contenido revisado, respetando checks y revisiones exigidos,
sin forzar pushes ni saltear protecciones. Revisar el workflow de la rama
destino y seguir la ejecución correspondiente al SHA integrado hasta su
conclusión. Publicar correctamente requiere el paso de deploy exitoso, no solo
el build o la apertura del PR.

Consultar el sitio público y comprobar que los datos incluyen el commit de la
rama integrada y que la interfaz esperada está servida. Las dos ramas comparten
producción: otro deploy puede reemplazarla. Reportar esa diferencia si ocurre;
no disparar publicaciones en bucle para ganar la carrera.

Si falla, leer la causa y corregir solo lo que pertenece a esta entrega. Si exige
credenciales, permisos o una decisión externa, entregar el enlace de la ejecución
y el paso concreto pendiente. Los secrets se cargan en GitHub; conservar sus
valores fuera de mensajes, archivos y comandos visibles.

**Salida:** PR, commit, resultado de Actions, URL publicada y verificación real;
o bloqueo preciso. Los pendientes de revisión editorial siguen declarados.
