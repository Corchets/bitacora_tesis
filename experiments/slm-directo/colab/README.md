# Prueba de Tito viejo y Gemma 4 E2B en Google Colab

Esta carpeta permite repetir el ensayo sobre **150 casos escritos de desarrollo**:
75 de vishing y 75 legítimos. Compara Tito → Gemma 4 E2B con reglas. Las
referencias son provisionales, sin revisión humana, y el resultado no es una
evaluación final ni una medición de rendimiento en teléfono. La configuración
se relaciona con las decisiones abiertas [D08 y D09](../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

El notebook no ejecuta el test reservado, pero clona un checkout completo que
incluye sus archivos. No subir grabaciones humanas ni transcripciones
identificables: ver [privacidad del sistema](../../../docs/corpus/PRIVACIDAD-DEL-SISTEMA.md).

## Archivos para compartir

Compartir juntos [COLAB-TITO-E2B.ipynb](COLAB-TITO-E2B.ipynb) y
[probar_tito_e2b.py](probar_tito_e2b.py). El notebook abre el entorno y carga
el script; el script es la fuente del procedimiento. El repositorio de datos y
código se descarga desde GitHub, fijado en el commit
`833a3fb5b2330ea3755b60880006a7d49b1e2e1b`.

## Pasos

1. Ingresar a [Google Colab](https://colab.research.google.com/) con una cuenta
   de Google y subir el notebook `.ipynb`.
2. En **Entorno de ejecución → Cambiar tipo de entorno de ejecución**, elegir
   **GPU T4** si está disponible. La prueba se detiene si `nvidia-smi` no
   funciona; esto comprueba que la GPU está disponible, no que el modelo la use.
3. Ejecutar la primera celda y seleccionar el archivo `probar_tito_e2b.py` sin
   cambiar su nombre. En la segunda celda, dejar `IDS = ''` para ejecutar los
   150 casos; para un subconjunto de desarrollo, escribir sus IDs separados por
   comas y registrar cuáles se usaron.
4. Ejecutar la segunda celda. Instala `zstd`, las dependencias y Ollama, inicia
   el servicio, descarga el modelo y verifica su digest antes de la corrida.
   Se procesan las reglas y Tito → SLM, sin ejecutar la condición SLM directa.
5. Al finalizar se genera y descarga `resultados-colab.zip`. Guardarlo y
   compartirlo para revisión: incluye manifiesto, actualizaciones, resumen,
   versiones de paquetes y Ollama, y hash del script. Las salidas de la máquina
   temporal pueden perderse al desconectarse.

La GPU y la duración de sesión están sujetas a disponibilidad. La corrida previa
en Colab tardó aproximadamente 15 minutos de procesamiento, sin contar la
instalación; ese tiempo no garantiza la duración de otras sesiones.

## Alcance y comparación

La configuración usa `gemma4:e2b-it-q4_K_M`, prompt `tarea`, hablantes `ab`,
contexto de 4096 y seed 42. Para comparar corridas, conservar el ZIP completo y
registrar cualquier cambio de IDs o configuración. El wrapper original de la
corrida anterior no se conservó; este implementa el mecanismo documentado de
omitir el SLM directo. La ejecución del 2026-11-04 con ese mecanismo terminó en
Colab y produjo resultados muy similares a la corrida anterior; el notebook y
script reorganizados en esta carpeta todavía requieren una ejecución completa
desde una sesión nueva para verificar el flujo de carga compartido.

Este notebook no prepara otros modelos, ASR ni audio. Las dependencias Python no
están todas fijadas: el inventario del ZIP permite auditar lo instalado, pero no
garantiza que otra sesión resuelva las mismas versiones.
