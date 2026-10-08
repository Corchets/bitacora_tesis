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

Mostrar el hito actual, los issues, el roadmap como grafo de dependencias interactivo y un glosario breve de forma visual.
Cada brief explica resultado, contexto necesario, primer paso y evidencia de cierre.
El roadmap dibuja los issues como nodos agrupados por frente y las dependencias reales de GitHub como flechas: qué está hecho (contexto concluido como #20), qué espera a qué (#19 espera a #39; #28 converge de #19 y #50), y qué puede empezar ya (#39, #50, #25). El laboratorio aparece como frente pausado separado, con sus condiciones de retomo y ramas preservadas, sin bloquear ni contarse como trabajo hecho. Al seleccionar un nodo, un panel lateral muestra qué existe, la siguiente acción, los bloqueos vigentes y la evidencia, sin perder el encuadre del mapa; una vista de lista accesible ofrece la misma información para teclado y móvil.

## Operating Context

La entrada principal es `laboratorio-main`; un selector permite consultar `main`.
La publicación es en Vercel, visible para cualquier persona con el enlace.
GitHub conserva el backlog y los documentos de cada rama son fuentes primarias.

## Capabilities and Constraints

- Mostrar todos los issues abiertos por hito; preparar briefs iniciales del hito activo.
- Presentar el roadmap como un grafo interactivo de entregas (Cytoscape.js, bundle local en `dist/`): carriles por frente, aristas desde las dependencias nativas de GitHub, zoom, encuadre, paneo y nodos arrastrables.
- Proveer tres opciones inmediatas claras desde el estado actual (primer par grabado #39, SLM directo con contexto #50, antecedentes #25).
- Visibilizar el frente de laboratorio/cascada como opción suspendida para retomar con recaudos metodológicos (#51, D09) y ramas remotas preservadas.
- Resaltar al seleccionar un nodo sus bloqueos entrantes y las entregas que desbloquea; un panel muestra qué existe, siguiente acción, bloqueos y evidencia enlazada.
- Ofrecer la misma información en una lista DOM accesible por teclado (modo Lista), con filtros por frente y por disponibilidad, y cierre del panel con Escape.
- Mantener la legibilidad en dispositivos móviles (390x844) con modo Lista por defecto, targets táctiles >= 44px y 0px de desborde horizontal.
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
