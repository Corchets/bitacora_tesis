# Informe visual Tito → SLM

[Abrir el informe](index.html). Reúne las pruebas experimentales de #69–#74 y
permite comparar las variantes directa y filtrada por modelo y conversación.

## Regeneración

Desde esta carpeta, con Python estándar:

```bash
python generar.py
```

- `generar.py`: carga las corridas explícitas, compara sus agregados con
  `../cobertura.json` y prepara los datos de presentación.
- `plantilla.html`: estructura, estilos e interacción, con un único marcador
  `<!-- REPORT_DATA -->` para los datos.
- `index.html`: informe generado y autónomo. Se abre en el navegador sin servidor,
  acceso a Internet ni dependencias de JavaScript externas. No editar a mano.

La regeneración lee CSV, el consolidado, referencias de los casos ya incluidos y el
artefacto de Tito. No ejecuta modelos ni accede al test reservado. Las cifras
mantienen como fuente las salidas del experimento; el informe es una vista derivada.

## Contenido

- **Vista general:** detecciones y falsas alarmas sobre cuatro casos por clase;
  consultas evitadas y comparación de tokens y costo acumulado.
- **Por modelo:** métricas del artefacto elegido y detalle de las ocho llamadas.
- **Por conversación:** líneas de derivación y aviso, costo por modelo, motivos,
  citas y transcripción; referencias alternativas en TR-04/TR-07.
- **Tickets 69–74:** demostraciones simuladas y entregas reales con sus reportes.

Los límites y el estado de revisión del experimento se consultan en
[CONSOLIDADO.md](../CONSOLIDADO.md). La presentación se reconstruyó el 2026-10-26;
reemplaza el índice anterior de ocho imágenes SVG.

Verificación de presentación del 2026-10-26: recorrido de los seis modelos,
las ocho conversaciones, los seis tickets y las referencias alternativas en
Chromium. Sin errores de JavaScript ni desbordes horizontales de página en
320, 390, 768 y 1440 px; revisión visual de escritorio y celular.
