# Ayuda memoria

Entrada visual para el equipo: hito actual, issues, roadmap y glosario breve.
`laboratorio-main` es la vista inicial; `main` muestra sus propias fuentes. El
backlog de GitHub es compartido. La web no asigna trabajo ni cierra decisiones.
Trabajo acordado en [#57](https://github.com/Corchets/bitacora_tesis/issues/57).

## Uso local

Requiere Node 22 o posterior y acceso al repositorio público en GitHub.

```bash
cd ayuda-memoria
npm install
npm test
npm run build
npm run preview
```

Abrir `http://127.0.0.1:4173`. La única dependencia de aplicación es
[Cytoscape.js](https://js.cytoscape.org/) (grafo del roadmap): está fijada en
`package.json`/`package-lock.json` y `npm run build` copia su bundle ESM y la
licencia dentro de `dist/`, de modo que la web no usa CDN.
El generador acepta `GH_TOKEN`/`GITHUB_TOKEN`; localmente también puede usar la
sesión existente de `gh`. El token se usa solamente para leer GitHub y no se
escribe en los datos de la web. Sin token aplican los límites de la API pública.

## Fuentes y actualización

`config.json` declara repositorio, ramas y selección del glosario.
`scripts/build.mjs` consulta commits, árboles, documentos, issues, milestones y
dependencias nativas. Usa archivos de cada commit, con enlaces a esa revisión.
`dist/` es una salida regenerable y permanece fuera de Git.

- Roadmap/calendario: `docs/propuesta/PLAN-DE-TRABAJO.md` de cada rama. Se conserva
  la condición de propuesta; las fechas no acreditan hitos terminados.
- Términos: `docs/GLOSARIO.md` de cada rama.
- Decisiones: `docs/gestion/MAPA-DECISIONES.md` de cada rama.
- Estado, responsable y bloqueos: GitHub, sin inferirlos de un brief.
- Grafo del roadmap: `data.roadmap.graph` se arma desde las dependencias nativas
  (`blocked_by`) de los issues de los frentes y de los bloqueos que esos issues
  referencian, incluidos cerrados con su `state_reason`. `roadmap.json` aporta la
  orientación editorial (frentes, próximos pasos, `edgeNotes`, laboratorio en
  suspenso); nunca define bloqueos en texto narrativo.
- Orientaciones editoriales: `briefs.json`. No son campos obligatorios del issue
  ni un segundo registro de su estado.

Si una consulta falla, el build falla: no publica un snapshot viejo como actual.
La última publicación válida sigue disponible con su fecha; después de 24 horas
muestra una advertencia para contrastar el estado en GitHub.

## Revisar briefs con la skill

Invocar [`$actualizar-ayuda-memoria`](../.agents/skills/actualizar-ayuda-memoria/SKILL.md).
Es una skill del proyecto, disponible por invocación explícita. `AGENTS.md` no
necesita nuevas reglas. La primera versión prioriza los cinco issues de H2;
el resto conserva el contrato original y muestra el brief pendiente.

Cada entrada de `briefs.json` tiene:

| Campo | Significado |
| --- | --- |
| `branch`, `issue` | Identidad de la orientación. |
| `goal` | Resultado concreto, derivado del contrato. |
| `sources` | Pocas fuentes de esa rama: `path`, `label`, `why`, y `anchor` opcional. |
| `start` | Primer paso; debe respetar bloqueos y decisiones abiertas. |
| `done` | Evidencia para reconocer el terminado. |
| `review` | Fecha y huella de las fuentes que se leyeron. La calcula el script. |

Después de agregar o cambiar fuentes, generar antes de revisarlas. Leer y
contrastar el issue y los documentos; luego registrar **solo** el brief revisado:

```bash
npm run build
npm run revisar-brief -- laboratorio-main 50
npm run build
```

Cambios del issue, sus dependencias o el contenido de las fuentes invalidan la
huella. Se muestra «Revisar brief» y se usa el contrato original del issue mientras
espera revisión. Una fuente ausente se identifica como pendiente. Revisado
significa que la orientación se contrastó; no significa que el issue terminó ni
que el código citado cumple su contrato.

Los documentos de laboratorio conservan acuerdos anteriores a Main. Sus briefs
señalan la diferencia y empiezan por verificar versiones; no trasladan el método
de Main como si ya estuviera integrado allí.

## Publicar y automatizar

El proyecto de Vercel recibe **solo `dist/`**, que incluye su `vercel.json` y
fuentes tipográficas locales. No se sube el resto del repositorio.

Con una cuenta conectada a la CLI:

```bash
npm run build
npx --yes vercel@62.7.0 deploy dist --prod --yes
```

El proyecto de producción asociado es `bitacora-tesis-ayuda-memoria` (equipo
`nacho1706s-projects`), disponible públicamente por enlace en
`https://bitacora-tesis-ayuda-memoria.vercel.app`.

El [workflow](../.github/workflows/ayuda-memoria.yml) usa el código de la web en
`main` y consulta las dos ramas. Corre `npm ci` antes de generar para tener el
bundle fijado de Cytoscape. Publica después de pushes, cambios de issues,
comentarios y milestones. La revisión horaria recupera también cambios de
dependencias nativas; no se promete actualización instantánea de esas relaciones.
La redacción de los briefs se revisa con la skill; el workflow no ejecuta IA.

Para activarlo:

1. Integrar estos archivos en `main`; el workflow también debe existir en
   `laboratorio-main` para recibir sus pushes. No requiere trasladar ni reescribir
   los documentos de laboratorio.
2. Proyecto en Vercel creado y configurado (`bitacora-tesis-ayuda-memoria`):
   protección SSO desactivada y URL pública verificada de forma anónima sin inicio de sesión.
3. Secrets en GitHub Actions: `VERCEL_ORG_ID` y `VERCEL_PROJECT_ID` ya están
   configurados en el repositorio. Falta `VERCEL_TOKEN` (requiere crear un
   personal access token clásico en `https://vercel.com/account/tokens`, ya que la
   sesión OAuth de la CLI es de corta duración y no permite emitir tokens desatendidos).
4. Ejecutar «Actualizar ayuda memoria» desde Actions → Run workflow una vez
   cargado `VERCEL_TOKEN` y realizada la integración.

Los secrets se configuran fuera de Git. Sin ellos, la generación deja un artifact
verificable y la publicación informa cuáles faltan. No es necesario conectar
también el despliegue automático de Git en Vercel: este workflow es quien publica.

Referencias de integración: [API de dependencias](https://docs.github.com/en/rest/issues/issue-dependencies),
[eventos de Actions](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows)
y [CLI de Vercel](https://vercel.com/docs/cli/deploy).

## Apartado de arquitectura

`docs/ingenieria/arquitectura-web/` es una visualización interactiva independiente
(`index.html`/`riesgo.html`, JS plano y SVG inline, sin build propio): muestra el
pipeline propuesto de detección incremental de vishing y un simulador del trade-off
entre persistencia y falsas alarmas. Adoptada del PR #58 el 2026-10-08.

- `npm run build` la copia a `dist/arquitectura/`; se abre en `/arquitectura/`.
- Sin dependencias npm extra: mismo tono visual (Manrope, verde/lima/terracota)
  y misma CSP del sitio; funciona offline una vez publicada.
- Los estados y el contenido completo de las decisiones que muestra los toma en
  vivo de `data.json` (`adoption.decisions`, parse del `MAPA-DECISIONES.md` del
  árbol de trabajo — la fuente adoptada localmente con el PR #58; como respaldo
  usa `branches[].decisions` de la rama elegida). `datos.js` no mantiene una
  copia editorial de las fichas: si `data.json` no está disponible, las
  decisiones se muestran como «contenido canónico no disponible».
- Deep links: `?c=<componente>` enfoca un componente del diagrama (por ejemplo
  `?c=detector` o `?c=contador`) y `?d=<DNN>` abre una decisión (por ejemplo
  `?d=D11`). El simulador acepta `?d=` igual.
- El simulador de riesgo es ilustrativo: sus números son sintéticos y no
  constituyen resultados medidos ni cierran D08.
