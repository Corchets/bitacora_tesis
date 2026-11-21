# #143, configuración congelada: prueba de humo en desarrollo

> **Estado: propuesta sin discutir.** Desarrollo; no toca la reserva, las legítimas de test ni #144. Preparada, corrida
> en Colab y analizada el 2026-11-10. **Según la regla, la configuración queda lista para la evaluación final:**
> 36/46 · 14/36 · 26/36 · FA 25/94, a ±1 de la lectura simulada de la etapa 3, sin líneas inválidas. De los motivos de
> las 25 FA, 3 engañan. Ver [`analisis.md`](analisis.md).
>
> La regla de abajo está escrita antes de correr, en código en [`analizar.py`](analizar.py). El Colab está en
> [`colab/README-PUNTAJE-TOKEN.md` §7](../../colab/README-PUNTAJE-TOKEN.md#7-configuración-congelada-humo-en-desarrollo-tag-colab143-config-congelada).

## Qué es

La configuración que congeló Mateo el 2026-11-09, corrida por primera vez como tal:
- **primera consulta:** el prompt de C de la etapa 2 ([`tarea_c.txt`](../../prompts/tarea_c.txt) y
  [`salida_json_c.txt`](../../prompts/salida_json_c.txt), con el mismo esquema), cortado justo después del riesgo
  (`c-json-corte-riesgo`, `num_predict` 14);
- **avisa con «riesgo ≥ 0,3»;**
- **el motivo de C** ([`motivo_c_corte.txt`](../../prompts/motivo_c_corte.txt)) en una segunda consulta, solo en el
  primer aviso ([ADR 0006](../../../../docs/ingenieria/adr/0006-salida-cortada-tras-el-campo-que-decide-y-motivo-al-avisar.md));
- **consulta solo en las líneas de OTRA** (`correr.py --solo-otra`,
  [ADR 0007](../../../../docs/ingenieria/adr/0007-consulta-al-cerrar-cada-turno-de-otra.md));
- **modo operativo:** la llamada termina en el primer aviso.

Hasta ahora nada de esto corrió junto:
- el corte tras el riesgo se leyó de `c-json-corte`, cortado tras la alerta (24 tokens);
- «solo OTRA» se simuló sobre corridas en todas las líneas;
- el motivo de C solo se pidió en la alerta fuerte de «C con campo» (22/22 válidos, unos 800 ms).

## Qué pregunta

¿La configuración real corre sin fallos y reproduce la lectura de la etapa 3? Y, solo para mirar, ¿qué motivos
muestra, sobre todo en las falsas alarmas?

No elige nada ni ajusta prompts ([ADR 0005](../../../../docs/ingenieria/adr/0005-reglas-de-evaluacion-escritas-antes-de-correr.md)).

## Por qué 14 tokens y no 12

- `{\n  "riesgo": 0.1,` son 12 tokens en T4: las 2.773 líneas de v4-L, cortadas a 12, terminan en esa coma.
- C escribe además riesgos con dos decimales (0,05, 0,85, 0,95): 198 de las 4.325 líneas de `c-json-corte`, y 51 de
  2.621 en la repetición. Con 12 tokens, `0.05` quedaría `0.0`, y `0.85`, `0.8`.
- Con 13 alcanza para dos decimales y la coma. El 14 cubre un tercer decimal, que no apareció.
- La lectura exige la coma: si el número quedó a medias, la línea es un fallo.
- Cuesta unos 10 ms por consulta en T4, estimado: en la etapa 3, cada token sumó unos 5 ms.

## Qué corre

En Colab T4, unos 20 minutos, con Ollama 0.40.14, el digest `b37049369adf…`, `num_ctx` 4096, seed 42, temperatura 0,
roles y `--sin-reglas`:

1. **Humo de formato** en los 3 casos de siempre (48 líneas), en todas las líneas (`--seguir-tras-aviso`, sin
   `--solo-otra`), con `c-json-corte` y `c-json-corte-riesgo` en una corrida.
2. **La configuración congelada sobre los 244** de desarrollo, con `--solo-otra` y en modo operativo.

## Regla de lectura, escrita antes de correr

**La humo de formato pasa** si `c-json-corte-riesgo` lee el riesgo, con su coma, en las 48 líneas.
- Datos, sin criterio: el riesgo contra el de `c-json-corte` en la misma sesión, los tokens, los riesgos con dos
  decimales y los motivos.
- Si no pasa, no corre nada más, y se le avisa a Mateo. No se ajusta nada en esa sesión.

**La corrida en desarrollo,** dentro del alcance ([`alcance-140`](../../casos/listas/alcance-140.txt): 46 estafas, 36
con pedido, y 94 legítimas). Las cifras son las estafas avisadas, los avisos antes del pedido (T_A < T_R), los avisos a
tiempo (T_A ≤ T_R) y las FA. Las líneas inválidas no avisan.

1. **Control.** La corrida tiene que ser la configuración congelada:
   - el commit del tag, sin cambios sin commitear;
   - Ollama, el digest, `num_ctx`, seed y temperatura;
   - el prompt, el esquema, el corte de 14 tokens y la segunda consulta (`motivo_c_corte.txt`);
   - los 244 de desarrollo, sin la reserva (`CV2-T`) ni las legítimas de test (`ENT-T`);
   - ninguna línea de PROTEGIDA consulta, y todas las de OTRA sí;
   - modo operativo y entera: cada llamada termina en su aviso, o en la última línea si no avisa;
   - el aviso registrado es la primera línea de OTRA con «riesgo ≥ 0,3»;
   - el motivo se pidió en cada aviso, y solo ahí.
2. **Formato.** Las líneas inválidas son como mucho el 1 % de las consultadas, como en el JSON cortado de v4.
3. **Reproduce la etapa 3.** Cada una de las cuatro cifras queda dentro de ±2 de la lectura simulada de la etapa 3:
   `c-json-corte` de la etapa 2, con «riesgo ≥ 0,3», solo en las líneas de OTRA. Da **35/46 · 15/36 · 25/36 · FA 24/94**,
   y `analizar.py` la recalcula de esa corrida.
   - La primera consulta es el pedido de `c-json-corte` cortado antes. Con temperatura 0 y seed 42, el corte no cambia
     los tokens anteriores. Queda el ruido de la GPU: dos corridas iguales coinciden en el ~96 % de los riesgos.

**Si se cumplen la humo y las tres condiciones,** la configuración queda lista para la evaluación final. **Si no,** se
le avisa a Mateo antes de fijar la evaluación final, y no se ajusta nada.

## Solo para mirar (no decide)

- las cifras en [`alcance-91`](../../casos/listas/alcance-91.txt) y los intervalos de Wilson;
- los casos con otra línea de aviso que la lectura simulada;
- cuántos avisos salen de un 0,3 exacto, en estafas y en FA;
- **la latencia en T4:** la primera consulta (p50 / p95), el motivo y el total en la línea del aviso, junto a los de la
  etapa 3;
- las consultas y los ms por llamada, hasta el aviso o el final;
- **el motivo,** con la medición de la etapa 3:
  - JSON válido con motivo;
  - la evidencia es una frase textual de OTRA hasta esa línea, o de cualquier voz;
  - el motivo nombra un pedido antes de que la referencia lo marque. Se marca por palabras, y los marcados se leen a
    mano;
- **los motivos de todas las FA,** completos, para leer a mano:
  - en la etapa 3 hubo uno engañoso: en `ENT-L-BANCO-006` el motivo decía «te están pidiendo un código», y nadie lo
    pidió;
  - 25 de las 27 FA de la base salían de un 0,3 exacto, así que casi todas van a mostrar un motivo;
  - si hay motivos que engañan, se le informa a Mateo, que decide si el aviso muestra el motivo o el texto fijo. El
    prompt del motivo no se cambia.

## Lo que no entra

- **Las 56 legítimas entrantes de test** están en `laboratorio-luciano`, no en esta rama. En la evaluación final van
  como test (partición `test_reservado`), nunca como desarrollo: los `analizar.py` de las etapas 2 y 3, y este, esperan
  exactamente los 244. Les faltan roles en `roles-protegida.json`, y `correr.py --hablantes rol` frena antes de correr
  si a algún caso le faltan.
- Los criterios de aceptación del test, los cortes simulados del ASR y #144: los decide Mateo aparte.

## Después de correr

1. Descomprimir cada ZIP en un directorio vacío nuevo, y correr todo Python con `-I`.
2. Verificar los ZIP:
   - los parciales coinciden con el final;
   - `commit.txt`, `TERMINADA.txt` y los manifiestos dan el commit del tag, sin cambios sin commitear;
   - el sha256 de `colab/probar_config_congelada.py` en el tag coincide con `script-sha256.txt`;
   - el digest coincide con `digest.txt`;
   - la segunda consulta es `motivo_c_corte.txt`, y no hay casos de la reserva.
3. Copiar `humo/` y `desarrollo/` acá y correr `python -I analizar.py`.

## Archivos

| Archivo | Qué es |
|---|---|
| [`analizar.py`](analizar.py) | La regla de arriba en código, escrita antes de correr. Usa la vista, las cifras y la medición del motivo de la etapa 3. Tests en [`tests/test_config_congelada_143.py`](../../tests/test_config_congelada_143.py). |
| [`analisis.md`](analisis.md) | Resultado: verificación de los ZIP, la regla paso a paso y la lectura a mano de los motivos de las FA. |
| [`analisis-salida.md`](analisis-salida.md) | Salida completa de `python -I analizar.py`. |
| [`diagnostico.py`](diagnostico.py), [`diagnostico-salida.md`](diagnostico-salida.md) | Diagnóstico fuera de la regla, escrito el 2026-11-10 después de ver los resultados: estafas que se escapan, umbral 0,2, FA por tipo de legítima, avisos antes del cumplimiento y una capa de reglas. |
| `humo/`, `desarrollo/` | Corridas de Colab, tal como bajaron. |
| `commit.txt`, `script-sha256.txt`, `ollama-version.txt`, `digest.txt`, `pip-freeze.txt`, `gpu.txt` | Registro de la corrida. |
