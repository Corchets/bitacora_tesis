# Ayuda memoria del proyecto

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

HTML, CSS y JavaScript con generación en Node. Elección de implementación para
la primera versión; la consulta sobre framework permanece abierta en la conversación
del [issue #57](https://github.com/Corchets/bitacora_tesis/issues/57).

## Users

Los cuatro integrantes del Proyecto Final. Retoman trabajo después de una pausa y
necesitan entender dónde están, qué consultar y cómo empezar con un issue.

## Product Purpose

Mostrar el hito actual, los issues, el roadmap visual espacial interactivo y un glosario breve de forma visual.
Cada brief explica resultado, contexto necesario, primer paso y evidencia de cierre.
El roadmap mapea de forma ilustrativa no lineal la posición actual ("Estamos acá"), tres opciones de avance inmediato desacopladas (#39, #50, #25), la isla de laboratorio suspendida con sus condiciones y ramas preservadas, y el horizonte futuro. Todo el detalle permanece cerrado al inicio para encajar en un único viewport; al seleccionar un nodo se abre un drawer enfocado sin perder de vista el mapa, permitiendo explorar los briefs de issues en el mismo contexto.

## Operating Context

La entrada principal es `laboratorio-main`; un selector permite consultar `main`.
La publicación es en Vercel, visible para cualquier persona con el enlace.
GitHub conserva el backlog y los documentos de cada rama son fuentes primarias.

## Capabilities and Constraints

- Mostrar todos los issues abiertos por hito; preparar briefs iniciales del hito activo.
- Presentar el roadmap como un mapa visual espacial e ilustrativo en SVG que encaja en un viewport de escritorio sin exponer tarjetas largas ni decisiones al inicio.
- Proveer tres opciones inmediatas claras desde "Estamos acá" (Crear primer par, Alinear detector, Investigar antecedentes).
- Visibilizar el frente de laboratorio/cascada como opción suspendida para retomar con recaudos metodológicos (#51, D09) y ramas remotas preservadas.
- Abrir un único drawer enfocado al clickear un nodo; seleccionar otro reemplaza el contenido sin acumular.
- Permitir explorar el brief de cada issue dentro del mismo drawer y volver al nodo con botón Volver o cerrar al mapa con Escape o click exterior.
- Mantener la naturaleza gráfica y no lineal en dispositivos móviles (390x844) con targets táctiles >= 44px y 0px de desborde horizontal.
- Los briefs y el roadmap viven con la web; no son campos obligatorios de los issues.
- Publicar al cambiar las dos ramas o los issues. Revisar las explicaciones mediante
  la skill explícita `actualizar-ayuda-memoria`, instalada a nivel proyecto.
- Mostrar fecha y procedencia; distinguir fuentes cambiadas y decisiones abiertas.
- Mantener `AGENTS.md` sin cambios. No incluir audio ni materiales privados.

## Brand Commitments

Español de Argentina. Interfaz sencilla, visual y amigable; acceso rápido al contexto.

## Evidence on Hand

Plan de Trabajo, glosario y mapa de decisiones en ambas ramas; GitHub Issues y
milestones; guía y código del laboratorio. Las ramas tienen fuentes diferentes.

## Product Principles

- Orientar hacia un resultado concreto con pocas lecturas necesarias.
- Enlazar la fuente primaria y conservar su estado real.
- Hacer visibles bloqueos y pendientes de revisión.
