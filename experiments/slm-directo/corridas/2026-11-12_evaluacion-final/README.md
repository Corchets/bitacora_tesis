# #143, evaluación final

> **Estado: propuesta sin discutir.** El código está listo y probado en seco, pero **no corrió**: nadie corrió nada
> sobre el test. Decisiones de Mateo del 2026-11-18: sin criterios de aprobación (se informan cifras con intervalo y la
> comparación pareada), el set externo es solo de estafas, y los resultados del test van a `reserva/test`. Falta fijar la
> configuración, que sale de la revisión de producto, antes del tag `colab/143-evaluacion-final`
> ([ADR 0005](../../../../docs/ingenieria/adr/0005-reglas-de-evaluacion-escritas-antes-de-correr.md)).

## Qué corre

Corre una sola vez, fijada por tag, en modo operativo: cada llamada termina en su primer aviso.

**La configuración:** `c-premisa-corte-riesgo`, la congelada del [PR #171](https://github.com/Corchets/bitacora_tesis/pull/171).
- Es C con el párrafo del número no agendado, con la salida cortada tras el riesgo (`num_predict` 14).
- Avisa con «riesgo ≥ 0,3».
- Muestra el motivo en el primer aviso y consulta solo en las líneas de OTRA.

Es un parámetro (`CONFIG` en el notebook, `--config` en el análisis). Si la revisión de producto la cambia, la nueva
entra en `CIFRAS_DESARROLLO` de `analizar.py`, con sus cifras de desarrollo, antes del tag.

**Las referencias simples:**
- **v4 sin alcance:** `v4-corte`, el JSON de v4 cortado tras la alerta
  ([ADR 0006](../../../../docs/ingenieria/adr/0006-salida-cortada-tras-el-campo-que-decide-y-motivo-al-avisar.md)).
  Avisa con «riesgo ≥ 0,4 o alerta», con roles y en todas las líneas.
- **La regla de palabras clave del laboratorio:** reglas v1, sobre la línea nueva.
- Las reglas v2 corren también, pero solo se informan.
- Tito queda afuera.

**Los conjuntos.** [`conjuntos.py`](../../conjuntos.py) los arma fuera del repositorio, con texto, roles y referencia.
`correr.py --conjunto` corre sobre el texto y los roles, sin abrir la referencia. El test nunca entra en `casos/` ni corre
como `desarrollo`.

| Conjunto | De dónde sale | Vista principal | Aparte |
|---|---|---|---|
| `desarrollo` | Los 244 de `laboratorio-main` | [`alcance-140`](../../casos/listas/alcance-140.txt): 46 estafas (36 con pedido y 15 con cumplimiento) y 94 legítimas (29 cotidianas, 38 con pedido razonable y 27 con mención sin pedido) | Los otros 104, por grupo |
| `test_reservado` | La rama `reserva/test` (9089b19), traída por ruta en Colab | 100 estafas `CV2-T-V` (80 con pedido, 32 con cumplimiento y 20 sin pedido) y las 56 legítimas `ENT-T` (14 cotidianas, 26 con pedido razonable y 16 con mención sin pedido) | Las 100 legítimas viejas `CV2-T-L`: 26 dentro del alcance y 74 fuera |
| `externo` (#144) | El set coreano congelado ([PR #181](https://github.com/Corchets/bitacora_tesis/pull/181)). Por defecto, las 9 con ficha que están en [`casos/externo/coreano`](../../casos/externo/coreano) ([PR #184](https://github.com/Corchets/bitacora_tesis/pull/184)); si Luciano pasa la carpeta con las 33, esas | Las estafas coreanas de KorCCVi: 9 (7 con pedido, 5 con cumplimiento) o 33 (27 con pedido y 6 sin pedido) | — |

- **Las huellas del test se comprueban antes de armarlo:**
  - cada `CV2-T`, contra [`MANIFIESTO-CORPUS-V2.json`](../../casos/MANIFIESTO-CORPUS-V2.json);
  - el JSONL de las 56 y `alcance-reserva.json`, contra su SHA-256;
  - cada archivo del externo, contra [`MANIFIESTO-144-SET-COREANO-2026-11-11.json`](../../../../docs/corpus/MANIFIESTO-144-SET-COREANO-2026-11-11.json).
- **Los roles del test:**
  - los `CV2-T`, de `alcance-reserva.json`, anotado a ciegas;
  - las `ENT-T`, del campo `protegida` del JSONL.

## Cómo corre

[`colab/probar_evaluacion_final.py`](../../colab/probar_evaluacion_final.py), desde
[`COLAB-EVALUACION-FINAL.ipynb`](../../colab/COLAB-EVALUACION-FINAL.ipynb). Usa T4, Ollama 0.40.14, el digest
`b37049369adf…`, `num_ctx` 4096, seed 42 y temperatura 0, igual que la humo y la sensibilidad.

1. **Arma los conjuntos.** La rama `reserva/test` se trae con `git worktree` a `/content/reserva-test`, fuera del
   checkout del tag.
2. **Humo de formato** en los 3 casos de siempre (48 líneas), con la configuración y con `v4-corte`.
   - Si la configuración no lee el riesgo en las 48 líneas, no corre nada.
   - Si no pasa `v4-corte`, esa referencia no corre.
3. **Desarrollo:** la configuración, `v4-corte` y las reglas.
4. **Control de reproducibilidad, antes de tocar el test.** La configuración tiene que pasar cuatro controles:
   - repetir en desarrollo sus cifras ya medidas, con ±2 en cada una: **40/46 · 19/36 · 29/36 · FA 26/94**, de la
     sensibilidad;
   - tener como mucho un 1 % de líneas inválidas;
   - pasar el control de la corrida;
   - tener sus cifras en `CIFRAS_DESARROLLO`.

   Si falla, para sin correr el test y se le avisa a Mateo. No se ajusta nada.
5. **El test reservado y después #144**, con lo mismo.

Cada corrida baja como ZIP. Si Colab se corta, la corrida cortada se repite entera y lo terminado no se repite: es la
misma corrida, no una segunda mirada. Dura alrededor de 1 h en T4, estimado y sin medir. Como referencia, la humo de la
configuración tardó 7 min sobre los 244, y `v4-corte` tardó 14 min sobre 150 en todas las líneas.

**Análisis:** `python -I analizar.py` desde esta carpeta, con el ZIP descomprimido acá.

## Cifras, escritas antes de correr

Estas cifras salen en cada conjunto, sobre la vista principal y con Wilson al 95 %:
- **estafas avisadas;**
- **antes del pedido** (T_A < T_R);
- **a tiempo**, la detección útil (T_A ≤ T_R);
- **antes del cumplimiento** (T_A < T_C);
- **FA,** en total y por `tipo_legitima`.

La configuración se compara con cada referencia con McNemar exacto, con los pares discordantes en los mismos casos. Las
definiciones están en [METRICAS.md](../../../../docs/evaluacion/METRICAS.md). Las líneas inválidas no avisan. Además
salen las vistas de aparte, la latencia, las líneas inválidas (incluido `contexto_excedido`) y, con `--motivos`, los
motivos de las FA.

**FA por mes:** no apareció una fuente del volumen de llamadas de desconocidos de un adulto mayor en Argentina. Por eso
va una tabla por volumen, sin umbral: FA por mes con 1, 3, 5, 10 y 20 llamadas legítimas de desconocidos por semana. Sale
de la FA de las 56 `ENT-T`, con su intervalo.

**80/15** se informa solo como referencia ([PR #159](https://github.com/Corchets/bitacora_tesis/pull/159)).

## Sin criterios de aprobación

Mateo lo decidió el 2026-11-18: no hay aprobado ni desaprobado. Se informan las cifras de arriba con su intervalo, y la
comparación pareada (McNemar exacto) de la configuración contra `v4-corte` y las reglas. El set externo es solo de
estafas: las FA del test salen de las 56 `ENT-T`.

**Cómo leer la comparación con las reglas.** [`previa_desarrollo.py`](previa_desarrollo.py) arma las mismas tablas sobre
desarrollo, con corridas que ya existen ([salida](previa-desarrollo-salida.md)). Las reglas v1 avisan casi todo: a
tiempo 32/36, pero con 69/94 FA. La configuración avisa a tiempo 29/36 con 26/94 FA. No hay que leer una sola cifra: la
diferencia de detección con las reglas queda dentro del ruido (2 a 5 pares, p = 0,45) y la de FA es enorme (4 a 47).

**Dónde quedan los resultados.** Los CSV del test traen el texto de la reserva: van a la rama `reserva/test`. A
`laboratorio-main` va solo `analisis.md`, con identificadores y cifras. Lo del set externo no se sube a ningún lado: la
fuente prohíbe redistribuir derivados.

**Lo que falta antes del tag:** la configuración, que sale de la revisión de producto. Si no es `c-premisa-corte-riesgo`,
va en `CONFIG` del notebook y en `CIFRAS_DESARROLLO` de `analizar.py`, con sus cifras de desarrollo.

## Anotación alternativa de legítimas

La revisión de producto puede reanotar legítimas. El análisis acepta
`python -I analizar.py --anotacion-legitimas RUTA.json` e informa las dos versiones, cada una con sus cifras y su McNemar:

```json
{"_meta": {"fecha": "2026-11-11", "autor": "…", "motivo": "…"},
 "casos": {"ENT-L-BANCO-006": {"tipo_legitima": "mencion_sin_pedido"},
           "LEG2-CC-06": {"vista": "excluida"}}}
```

- **Campos que se pueden cambiar:** `clase`, `tipo_legitima`, `vista`, `t_r_linea`, `t_c_linea` y `pedido`.
- **`vista`:** cualquier valor distinto de `principal` saca el caso de la vista principal.
- La anotación se valida igual que una referencia: una legítima no lleva `T_R`.
- **También acepta tal cual `etiquetas-producto.json`,** el de la revisión de producto
  (`corridas/2026-11-10_revision-producto/`, rama `exp/143-revision-producto`, sin integrar).
  - Cuentan como FA solo las legítimas `no_avisar`.
  - Las `tolerable` y la `avisar` pasan a vistas aparte, como en su versión «producto».
  - Solo etiqueta las 94 legítimas de desarrollo, así que el test no cambia.

## Qué falta anotar

### El test reservado: nada

Se miraron solo el formato, las claves, los manifiestos y las huellas, sin leer ningún texto.

- **Las 56 `ENT-T`:**
  - tienen roles por línea (`protegida`, A o B) y `tipo_legitima`;
  - no están en el formato de casos, pero `conjuntos.py` las convierte sin tocarlas;
  - no tienen corrección a ciegas: Mateo lo decidió el 2026-11-10.
- **Los 200 `CV2-T`:**
  - las huellas coinciden con el manifiesto de `laboratorio-main`;
  - los roles salen de `alcance-reserva.json`: 9 con `rol_dudoso`;
  - `T_R` y `T_C` salen de la referencia.

### El set externo: nada

#144 lo dejó congelado el 2026-11-11: formato de casos, roles y `T_R`/`T_C`, con las huellas en el manifiesto. Las 9
con ficha están en el repo desde el 2026-11-18 y corren solas; las otras 24 están en la carpeta de Luciano. El inglés
(`casos/externo/ingles`) queda afuera: solo 2 de las 16 son entrantes (#151). Algunas llamadas reales son largas: las líneas que no entran en `num_ctx` 4096
son inválidas (`contexto_excedido`) y no avisan. Se informa.

## Archivos

| Archivo | Qué hace |
|---|---|
| [`conjuntos.py`](../../conjuntos.py) | Arma y valida los conjuntos; comprueba huellas; no imprime textos |
| [`correr.py --conjunto`](../../correr.py) | Corre sobre un conjunto armado, sin leer su referencia |
| [`analizar.py`](analizar.py) | Controles, cifras, Wilson, McNemar, anotación alternativa y control de reproducibilidad |
| [`previa_desarrollo.py`](previa_desarrollo.py) | Las mismas tablas sobre desarrollo, para ver cómo se leen |
| [`colab/probar_evaluacion_final.py`](../../colab/probar_evaluacion_final.py) y su notebook | La corrida en Colab |
| [`tests/test_evaluacion_final.py`](../../tests/test_evaluacion_final.py) | Reserva sintética, Ollama falso y corridas sintéticas |

**Prueba en seco (2026-11-10, repetida el 2026-11-18 con un externo sintético en el formato del set coreano):**
- Corrió el Colab entero en una Mac, con binarios falsos de Colab y Ollama.
- El Ollama falso repetía los riesgos de la sensibilidad en desarrollo.
- Se usaron una reserva sintética y un #144 sintético.
- La humo pasó 48/48, el control de desarrollo reprodujo 40 · 19 · 29 · FA 26 y las 9 corridas pasaron el control del
  análisis.
- Nada de eso tocó el test real.
