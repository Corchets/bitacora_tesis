# #143, evaluación final

> **Estado: propuesta sin discutir.** El código está listo y probado en seco (2026-11-10), pero **no corrió**: nadie
> corrió nada sobre el test. Los criterios de abajo son un borrador y los decide Mateo. Lo que decida se fija en este
> README y en `CRITERIOS` de [`analizar.py`](analizar.py) **antes** del tag `colab/143-evaluacion-final`, nunca después
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
| `externo` (#144) | La carpeta de la custodia, si la entrega | Las estafas que la custodia deje en la vista | Las que deje aparte |

- **Las huellas del test se comprueban antes de armarlo:**
  - cada `CV2-T`, contra [`MANIFIESTO-CORPUS-V2.json`](../../casos/MANIFIESTO-CORPUS-V2.json);
  - el JSONL de las 56 y `alcance-reserva.json`, contra su SHA-256.
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

## Criterios, escritos antes de correr (borrador)

> **Estado: propuesta sin discutir.** Mateo propuso las ideas el 2026-11-07: ganarle con margen a referencias simples,
> mirar el límite inferior del intervalo, la detección útil y la tolerancia en el set externo. Las cifras son una
> propuesta de esta sesión.

Se aplican sobre el **test reservado, en la vista principal**. Si un criterio no se cumple, se informa tal cual.

1. **Le gana a cada referencia sin perder** (contra `v4-corte` y contra las reglas v1).
   - **Ganar:** en alguna de las tres cifras (estafas avisadas, a tiempo, FA), la configuración tiene 3 pares
     discordantes o más a favor, con McNemar p < 0,05.
   - **No perder:** no tiene eso en contra en ninguna.
   - En las FA, a favor quiere decir que la referencia avisa y la configuración no.
2. **El límite inferior de Wilson de «a tiempo» es ≥ 50 %.** Con 95 % de confianza, avisa a tiempo en más de la mitad
   de las estafas con pedido. Con 80 casos, eso pide un punto de alrededor del 61 %.
3. **El límite inferior de Wilson de las estafas avisadas es ≥ 50 %.**
4. **#144 no se derrumba:** las estafas avisadas en #144 caen como mucho 20 puntos respecto del test.
   - Con unas 20 estafas, cada caso vale 5 puntos y el ruido de ±2 vale 10.
   - Si #144 no corre, el criterio queda sin dato.

**No deciden, se informan:**
- antes del pedido y antes del cumplimiento;
- las FA por tipo y por volumen;
- 80/15;
- las reglas v2;
- las vistas de aparte;
- la latencia;
- todo lo de desarrollo.

### Por qué el criterio 1 no mira solo la detección

[`previa_desarrollo.py`](previa_desarrollo.py) aplica estos criterios a desarrollo, con corridas que ya existen:
- la configuración, de la sensibilidad;
- `v4-corte`, de la etapa 2;
- las reglas, que no usan modelo.

No mira el test ni decide nada. La salida está en [`previa-desarrollo-salida.md`](previa-desarrollo-salida.md).

| alcance-140 | estafas | a tiempo | FA | FA cotidianas |
|---|---|---|---|---|
| `c-premisa-corte-riesgo` | 40/46 | 29/36 | 26/94 | 2/29 |
| `v4-corte` | 28/46 | 25/36 | 42/94 | 1/29 |
| reglas v1 | 42/46 | 32/36 | 69/94 | 13/29 |

- **Con un criterio solo de detección útil, la configuración no le ganaría a ninguna de las dos.**
  - Contra `v4-corte` suma 7 pares contra 3 (p = 0,34).
  - Contra las reglas pierde 2 a 5 (p = 0,45): las reglas avisan casi todo, con 73 % de FA.
- **Con el criterio 1 cumple contra las dos, y también en la repetición.**
  - Contra `v4-corte` gana en estafas (14 a 2) y en FA (24 a 8).
  - Contra las reglas gana en FA (47 a 4) y la detección queda dentro del ruido.
- **Riesgo para el test.** Con 80 estafas con pedido, la ventaja de detección de las reglas puede volverse
  significativa (p < 0,05). Entonces el criterio diría «pierde», aunque las reglas tengan 73 % de FA en desarrollo.

### Lo que decide Mateo antes del tag

1. **El criterio 1 contra las reglas.** Hay tres opciones:
   - dejarlo así;
   - contra las reglas, exigir solo «gana en FA sin perder más de X estafas a tiempo»;
   - comparar a FA parecida, que con un punto por detector no se puede.
2. **Los pisos de los criterios 2 y 3.** La propuesta es 50 %; la alternativa más exigente, 60 %.
3. **La tolerancia de #144.** La propuesta son 20 puntos. La otra opción es que los intervalos de #144 y del test no se
   separen.
4. **La configuración,** si la revisión de producto la cambia, y sus cifras de desarrollo.
5. **Dónde quedan los resultados del test.**
   - El CSV trae el texto de cada línea, y la reserva no puede entrar en `laboratorio-main`.
   - Propuesta: los CSV del test van a `reserva/test`, y a `laboratorio-main` solo `analisis.md`, que muestra
     identificadores y cifras, sin textos.
   - Lo de #144 en coreano no se sube a ningún lado: la fuente prohíbe redistribuir derivados.
6. **#144:** anotarlo como se propone abajo, o correr la evaluación sin #144.

## Anotación alternativa de legítimas

La revisión de producto puede reanotar legítimas. El análisis acepta
`python -I analizar.py --anotacion-legitimas RUTA.json` e informa las dos versiones, cada una con sus cifras, su
McNemar y sus criterios:

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

### #144: falta casi todo

Lo que hay hoy:
- **Formato:** no está en formato de casos.
  - Las traducciones de inglés y portugués están dentro de `docs/corpus/ISSUE-144-*.md`, en secciones con encabezados.
  - El inglés conserva turnos pegados y rótulos invertidos de la fuente.
  - El coreano no está en el repositorio.
- **Roles:** no hay. Falta decir, en cada llamada, quién es PROTEGIDA.
- **`T_R` y `T_C`:** solo están las fichas de Luciano de las 16 llamadas de inglés que se conservan (y 2 de coreano).
  - Las marcas son «turno de lectura», en texto libre («10 aprox», «nunca nombra…»).
  - Son de un solo revisor y no están adjudicadas.
  - En 4 llamadas, su juicio no coincide con la etiqueta de la fuente.
- **Portugués:** no tiene fichas de Luciano. PIX se había descartado como fuente porque la conversación no define la
  clase (relevamiento, §3.3), y su clave está fuera de Git.

**Propuesta para anotar a ciegas.** Sigue el formato del
[relevamiento, §5.4](../../../../docs/corpus/RELEVAMIENTO-CORPUS-EXTERNO.md#54-formato-todas-son-conversaciones).
Nadie del lado del detector lee las llamadas.

1. **Luciano, la custodia, que ya las leyó, arma una carpeta por script:**
   - `texto/EXT-NNN.txt` con `A:`/`B:`, un turno por línea, sin rótulos de la fuente;
   - identificadores por sorteo, con semilla registrada;
   - `roles.json`, donde PROTEGIDA es quien atiende;
   - `referencia.json`.
2. **`T_R` y `T_C`:** los marca un agente nuevo, que no vio prompts, corridas ni resultados. Usa la guía de #145 y
   METRICAS.md, como la pasada 1 de `TEST-ALCANCE.md` §4. Donde no coincide con la ficha, decide Luciano.
3. **La vista:**
   - en la principal, las llamadas que Luciano juzga estafa;
   - aparte, aquellas en las que su juicio difiere de la fuente.
4. **El coreano** corre solo si la custodia tiene la traducción fuera de Git. Sus resultados no se suben.
5. **El portugués** queda afuera, salvo que Mateo decida otra cosa y la custodia aporte la clave.

**Aviso:** algunas llamadas reales son largas. Las líneas que no entran en `num_ctx` 4096 son inválidas
(`contexto_excedido`) y no avisan. Es el comportamiento de la configuración, y se informa.

## Archivos

| Archivo | Qué hace |
|---|---|
| [`conjuntos.py`](../../conjuntos.py) | Arma y valida los conjuntos; comprueba huellas; no imprime textos |
| [`correr.py --conjunto`](../../correr.py) | Corre sobre un conjunto armado, sin leer su referencia |
| [`analizar.py`](analizar.py) | Controles, cifras, Wilson, McNemar, criterios, anotación alternativa y control de reproducibilidad |
| [`previa_desarrollo.py`](previa_desarrollo.py) | Los criterios sobre desarrollo, para ver que estén bien planteados |
| [`colab/probar_evaluacion_final.py`](../../colab/probar_evaluacion_final.py) y su notebook | La corrida en Colab |
| [`tests/test_evaluacion_final.py`](../../tests/test_evaluacion_final.py) | Reserva sintética, Ollama falso y corridas sintéticas |

**Prueba en seco (2026-11-10):**
- Corrió el Colab entero en una Mac, con binarios falsos de Colab y Ollama.
- El Ollama falso repetía los riesgos de la sensibilidad en desarrollo.
- Se usaron una reserva sintética y un #144 sintético.
- La humo pasó 48/48, el control de desarrollo reprodujo 40 · 19 · 29 · FA 26 y las 9 corridas pasaron el control del
  análisis.
- Nada de eso tocó el test real.
