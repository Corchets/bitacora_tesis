# Formularios de revisión ciega — #145

Preparación del 2026-11-07 para [#145](https://github.com/Corchets/bitacora_tesis/issues/145).
El formulario se entrega vacío. Las [respuestas parciales de Luciano](REVISIONES-HUMANAS-LUCIANO.md)
se conservaron después, separadas de la herramienta. No completan el issue.

## Cómo completar

Abrir el [formulario HTML](../../experiments/slm-directo/analisis/tablero/revision-145.html)
en Chrome, escribir nombre y apellido y elegir **Abrir mis fichas**. El archivo funciona
sin conexión. También puede servirse con el tablero local en el puerto 8766; no usa el
servidor de llamadas del puerto 8765.

- Una conversación por ficha, con líneas numeradas y casillas. Las preguntas de respuesta
  única admiten una sola selección; «Dudoso» permite conservar la incertidumbre.
- Para cargar una marca, elegir sospecha, pedido o cumplimiento y hacer clic en el número
  de línea del diálogo. También se puede escribir el número.
- **Terminé de revisar esta ficha** comprueba respuestas, justificaciones y líneas.
  Una edición válida conserva esa confirmación; si deja campos necesarios sin completar,
  vuelve a pendiente. El contador distingue respuestas suficientes de confirmaciones.
- Las respuestas se guardan por nombre y muestra en ese navegador. **Descargar mis
  respuestas** genera un JSON con las fichas completas y pendientes. Descargar al terminar
  cada sesión: el guardado del navegador puede borrarse y no es una copia de respaldo.
- **Recuperar respuestas** permite continuar desde ese JSON. Rechaza archivos de otra
  muestra y pide confirmación si reemplaza respuestas existentes de la misma persona.
  Cambiar de equipo, navegador o dirección requiere recuperar el archivo descargado.
- Cada revisor conserva y entrega su propio JSON; no intercambiar respuestas antes de
  terminar la anotación independiente. Marcar la casilla de exposición previa cuando aplique.

La guía breve está dentro del formulario y se basa en el [manual vigente](MANUAL-ANOTACION.md)
y en [las métricas](../evaluacion/METRICAS.md). Las marcas nuevas se anotan sin ver las
anteriores; la comparación con las referencias originales se hace después con la clave.

> **Estado: propuesta sin discutir.** La guía es una ayuda de trabajo para calibrar
> [D07](../gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico), no una adjudicación
> ni un cierre de esa decisión. El tratamiento de estafas sin pedido sigue pendiente en
> [D08](../gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental) y #33.

## Muestra y separación de la clave

El [generador](../../experiments/slm-directo/preparar_revision_145.py) selecciona y mezcla con
semilla 145 las 16 estafas de desarrollo que no avisó ninguna de las cinco condiciones de
#145, 16 estafas con aviso elegidas al azar y 10 legítimas entrantes nuevas de desarrollo.
Comprueba también las nueve estafas sin pedido entre las 16 pérdidas. Las condiciones son
v1 SLM solo y su repetición, v1 con Tito e indicio, v4 SLM solo y v4 con Tito viejo 2.0.
Los CSV y detectores exactos quedan fijados en el script y sus hashes en la clave.

Las legítimas son `LEG-*` y `LEG2-*` de la revisión Git
`ac8a81f3da9e1a55f05722562053c08601829cd5`, filtradas por partición `desarrollo` y por el
alcance `dentro` de su anotación de alcance. Se reutiliza el cargador de desarrollo de
[`test_alcance.py`](../../experiments/slm-directo/test_alcance.py). No entran `CV2-T-*`,
el lote `ENT-T-*` ni las legítimas viejas de corpus_v2. No se ejecutan modelos.

El HTML lleva solo nombres neutros `Llamada 01` a `Llamada 42`, diálogos y roles
`PROTEGIDA`/`OTRA`. No incluye IDs originales, clase, familia, resultados, referencias
anteriores ni grupo de muestreo. La ceguera depende además de no consultar otros paneles,
la clave ni respuestas ajenas: el renombrado no elimina una exposición previa al diálogo.

La clave local está en `data/private/CLAVE-REVISION-145.json`, ignorada por Git, con una
copia en `~/respaldos/CLAVE-REVISION-145.json`. Vincula alias e ID original, guarda las
referencias previas y hashes de los textos, CSV y muestra. No compartirla con revisores
antes de terminar. Las respuestas exportadas incluyen el hash de muestra para unirlas
con esa clave sin confundir entregas. El generador rechaza reemplazar una clave distinta.

## Reproducción y comprobaciones

Desde la raíz del repositorio:

```bash
python3 experiments/slm-directo/preparar_revision_145.py
python3 -m unittest discover -s experiments/slm-directo/tests -p test_revision_145.py -v
node --test experiments/slm-directo/tests/test_revision_145_ui.cjs
```

La prueba de interfaz requiere Chrome y Playwright disponibles en el entorno de Node
(o en `NODE_PATH`); sin Playwright queda omitida. Verificación del 2026-11-07: cuatro
pruebas Python y una prueba en Chrome aprobadas, con diálogos ficticios; guardado y
recarga, separación por revisor, líneas por clic, validación, descarga/recuperación,
rechazo de otra muestra y ancho móvil. Inspección visual adicional de la entrega real
en notebook y móvil, sin completar fichas humanas.

## Qué sigue pendiente

Dos revisiones humanas por caso, medida del acuerdo antes de adjudicar, resolución de
desacuerdos, criterios para #32/#33/#45 y recálculo con referencias anteriores y nuevas.
La distribución de revisores del issue sigue siendo una propuesta: no se asignaron
casos a personas desde el formulario. #145 permanece abierto.
