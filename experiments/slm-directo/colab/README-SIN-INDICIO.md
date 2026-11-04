# Tito → Gemma 4 E2B sin indicio, en Google Colab

> **Estado: propuesta sin discutir.** Prueba de desarrollo sobre los **150 casos
> escritos** (75 de vishing y 75 legítimos), con referencias provisionales sin
> revisión humana. Cambia la configuración del
> [ADR 0001](../../../docs/ingenieria/adr/0001-parakeet-filtro-y-gemma4-e2b-con-tito-viejo.md)
> **solo como prueba** (quita el bloque de indicio del mensaje al SLM); no la
> reemplaza ni resuelve [D08](../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).
> No ejecuta el test reservado, aunque el checkout incluye sus archivos. No subir
> grabaciones humanas ni transcripciones identificables: ver
> [privacidad del sistema](../../../docs/corpus/PRIVACIDAD-DEL-SISTEMA.md).

## Hipótesis

En las 150 de desarrollo, en la misma PC Windows y con la misma configuración
(`gemma4:e2b-it-q4_K_M`, prompt `tarea`, hablantes `ab`, `num_ctx` 4096, seed 42),
[la comparación del 2026-11-04](../corridas/2026-11-04_132229_e2b-directo-150/comparacion-con-tito.md)
dio:

| | SLM solo | Tito viejo → SLM (con indicio) |
|---|---|---|
| Estafas con aviso | 55/75 | 51/75 |
| Avisos antes del pedido | 25 | 17 |
| Falsas alarmas | 18/75 | 13/75 |
| Consultas al SLM | 2.218 | 1.179 |

La compuerta de Tito activa al SLM antes del pedido en 57 de 64 estafas, así que casi
nunca es el problema. Lo que cambia es el mensaje: con Tito, el SLM recibe además el
**bloque de indicio** (`BLOQUE_INDICIO` en [`filtro_tito.py`](../filtro_tito.py), siempre
la primera línea que Tito marcó). En 10 líneas de estafa el SLM solo alertaba y con
indicio no.

**Hipótesis:** si Tito solo decide *cuándo* consultar y Gemma recibe exactamente el
mismo mensaje que el SLM solo (sin indicio), Tito → SLM detecta casi como el SLM solo
(≈ 54–55/75), mantiene ≈ 13/75 falsas alarmas o menos y usa la mitad de las consultas.

## Qué se corre

Todo en la **misma sesión de Colab**, para que la comparación no dependa de la PC:

| | Comando (`correr.py`, además de la configuración común) | Detectores |
|---|---|---|
| **a** | `--filtro-tito --tito-real` | reglas, SLM solo (`slm`) y Tito → SLM con indicio (`tito-slm`) |
| **b** | `--filtro-tito --tito-real --sin-indicio --sin-reglas`, con el wrapper que omite `DetectorSLM` (como [`probar_tito_e2b.py`](probar_tito_e2b.py)) | Tito → SLM sin indicio (`tito-slm-sin-indicio`) |
| **c** | `--sin-reglas` (solo si `REPETIR_SLM_SOLO = True`) | segunda corrida de SLM solo, para medir el no determinismo |

Con `--sin-indicio`, el SLM recibe byte a byte el mismo mensaje que `DetectorSLM` solo
(sin bloque de indicio ni de fallo técnico). La activación permanente de Tito no
cambia y las filas siguen registrando la línea y el puntaje que activaron. El
manifiesto registra `filtro_tito.indicio: false`. Ver
[`tests/test_sin_indicio.py`](../tests/test_sin_indicio.py).

Al terminar, el script corre [`comparar_sin_indicio.py`](../comparar_sin_indicio.py)
y deja `comparacion.md` en el ZIP. El repositorio se descarga desde GitHub, rama
`slm-sin-indicio`, fijado en el commit que figura en `COMMIT` de
[`probar_sin_indicio.py`](probar_sin_indicio.py).

## Criterio de lectura

Mirar la condición **b** contra la **a** (misma máquina):

- **Se confirma** si Tito sin indicio llega a ≈ 54–55/75 estafas con aviso, con
  ≤ 13/75 falsas alarmas y una cantidad de avisos antes del pedido parecida a la del
  SLM solo.
- **No se confirma** si queda en ≈ 51/75, como con indicio: entonces el indicio no
  explica la pérdida.
- Antes de leer diferencias de 1–3 casos, mirar **c**: si el SLM solo contra su
  repetición ya cambia esa cantidad de casos o de líneas, la diferencia está dentro
  del ruido de la máquina.

## Pasos en Colab

1. Ingresar a [Google Colab](https://colab.research.google.com/) con una cuenta de
   Google y subir [`COLAB-SIN-INDICIO.ipynb`](COLAB-SIN-INDICIO.ipynb) (Archivo →
   Subir notebook).
2. En **Entorno de ejecución → Cambiar tipo de entorno de ejecución**, elegir
   **GPU T4**. La prueba se detiene si `nvidia-smi` no funciona.
3. Ejecutar la primera celda y seleccionar el archivo
   [`probar_sin_indicio.py`](probar_sin_indicio.py) sin cambiarle el nombre.
4. En la segunda celda dejar `IDS = ''` (los 150), `REPETIR_SLM_SOLO = True` y
   `GUARDAR_EN_DRIVE = True`, y ejecutarla.
5. Cuando Colab lo pida, **autorizar Google Drive** con la misma cuenta.
6. Esperar. Instala `zstd`, las dependencias y Ollama, descarga el modelo y verifica
   su digest (`b37049369adfe3d2b653af0ab301a062ca5cbe96ace6aa0d3f2559ee9b563fc2`)
   antes de correr. Cada condición terminada se copia a
   `MyDrive/bitacora_tesis/sin-indicio-en-curso-<commit>-150/`.
7. Al final se descarga `resultados-sin-indicio.zip` y queda una copia en
   `MyDrive/bitacora_tesis/resultados-sin-indicio-<fecha>.zip`. Compartir ese ZIP:
   incluye manifiestos, actualizaciones, `resumen.md` de cada corrida,
   `comparacion.md`, `pip freeze`, versión de Ollama, commit y hash del script.

**Si Colab se corta:** volver a abrir el notebook, elegir otra vez GPU T4 y ejecutar
las dos celdas igual. Las condiciones ya guardadas en Drive se recuperan y no se
repiten; la que estaba a medio correr se repite entera.

## Tiempo estimado

La corrida previa de Tito → SLM en Colab tardó ≈ 15 minutos para 1.179 consultas, sin
contar la instalación. Con esa referencia: **a** ≈ 45 min (≈ 3.400 consultas), **b** ≈
15 min y **c** ≈ 30 min; en total ≈ 1 h 30 min más ≈ 10 min de instalación. La GPU y la
duración de la sesión dependen de la disponibilidad de Colab; no es una garantía.

## Comparar localmente

```bash
cd experiments/slm-directo
python comparar_sin_indicio.py resultados-sin-indicio.zip --salida comparacion.md
# o con carpetas de corrida, p. ej. las dos de Windows:
python comparar_sin_indicio.py corridas/2026-11-04_132229_e2b-directo-150 \
    corridas/2026-11-04_003715_e2b-tito-viejo-150
```

Las dependencias Python no están todas fijadas: el inventario del ZIP permite
auditar lo instalado, pero no garantiza que otra sesión resuelva las mismas
versiones. No es una medición de rendimiento en teléfono.
