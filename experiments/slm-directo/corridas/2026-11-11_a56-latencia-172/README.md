# a56-latencia-172 — 2026-11-11

Propuestas de [#172](https://github.com/Corchets/bitacora_tesis/issues/172) para bajar la latencia de la configuración
congelada (`c-premisa-corte-riesgo`) en el Samsung Galaxy A56. Cada cambio se midió por separado contra la misma
línea de base. Solo seis conversaciones de desarrollo y una pasada por configuración: alcanza para ver diferencias
grandes, no para estimar variabilidad. No cambia el prompt, el modelo ni el umbral, y no cierra D08 ni D09.

## Resultado en una línea

El primer aviso pasa de 13,8 s a 3,7 s (mediana) con la propuesta 1, que solo cambia la interfaz. Lo demás que mejora
el tiempo, entre 0,5 y 0,9 s por línea, también mueve el riesgo en algunas líneas, así que necesita una decisión antes
de adoptarse.

## Configuración

- **Base:** la de la [corrida del 2026-11-10](../2026-11-10_a56-congelada-latencia/README.md), con el prompt que
  quedó por defecto desde el PR #171:
  - Gemma 4 E2B `Q4_K_M` sola, prompt `c-premisa-corte-riesgo`, `num_predict` 14, aviso con riesgo ≥ 0,3.
  - Motivo de C solo en el primer aviso, consulta solo en las líneas de OTRA, `--hablantes rol`.
  - Contexto 4096, temperatura 0, seed 42.
  - `llama-server` de llama.cpp `6c01da62` con un slot, caché activa, CPU y 4 hilos.
- **Dispositivo:** SM-A566E con Android 16, por USB, con las apps en segundo plano cerradas (`am kill-all`) antes de
  cada corrida y un `llama-server` nuevo en cada una.
- **Recorrido:** todas las líneas, aunque ya haya avisado, para tener más mediciones, y el motivo una sola vez por
  llamada. Es el mismo modo diagnóstico de la corrida anterior.
- **Ejecutor:** [`correr_android_latencia.py`](../../correr_android_latencia.py), con el detector de siempre
  (`DetectorSLMCorteRiesgo`).
  - Corre en Termux. [`medir.py`](medir.py) lo lanza desde la PC por adb, levanta el servidor con los parámetros de
    cada corrida y anota memoria y temperatura cada 15 s.
  - Los hashes del código, del prompt y de las conversaciones están en el `manifiesto.json` de cada carpeta.

## Conversaciones

Desarrollo, nada de #144. [`armar.py`](armar.py) arma `conversaciones-sub-6.json` con roles: las tres primeras estafas
y las tres primeras legítimas de la lista `rapida-20`. `conversaciones-rapida-20.json` también quedó armado, pero no
se usó.

| Caso | Líneas | Consultas (OTRA) |
|---|---:|---:|
| CV2-D-V-BANCO-001 | 38 | 19 |
| CV2-D-V-BANCO-002 | 31 | 15 |
| CV2-D-V-BANCO-007 | 30 | 15 |
| CV2-D-L-BANCO-001 | 22 | 11 |
| CV2-D-L-BANCO-007 | 23 | 11 |
| CV2-D-L-DELIVERY-001 | 24 | 12 |
| **Total** | **168** | **83** |

## Antes y después

Sale de [`resumir.py`](resumir.py), que también escribe [`resumen.json`](resumen.json).

- **Por línea:** la actualización de una línea de OTRA sin motivo, la que se repite toda la llamada (n = 78 o 79).
- **Primer aviso:** la línea del primer aviso de cada conversación (n = 4 o 5).
  - *Con motivo* es lo que pasa hoy: la primera consulta más la del motivo.
  - *Sin esperar el motivo* es la propuesta 1 aplicada a esa corrida: solo la primera consulta.
- **Memoria:** el pico de `VmHWM` de `llama-server`.
- **Riesgo distinto:** líneas en que el riesgo escrito no coincide con el de la base, y conversaciones en que el
  primer aviso cae en otra línea.

| Propuesta | Corrida | Por línea, mediana | Por línea, máx. | Procesar | Generar (tokens) | Primer aviso con motivo (med. / máx.) | Sin esperar el motivo (med. / máx.) | Memoria | Riesgo distinto | Primer aviso en otra línea |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| — | `s6-base-t4` | 3,74 s | 5,49 s | 1,94 s | 1,75 s (14) | 13,84 / 16,08 s | 3,68 / 4,01 s | 3,53 GiB | — | — |
| 2 | `s6-numero` | 2,85 s | 3,30 s | 2,01 s | 0,76 s (6) | 12,97 / 14,47 s | 2,82 / 3,23 s | 3,84 GiB | 8/83 | 0/6 |
| 3 | `s6-t6` (6 hilos) | 4,40 s | 12,88 s | 1,94 s | 2,34 s (14) | 17,62 / 19,05 s | 4,50 / 4,62 s | 3,53 GiB | 5/83 | 0/6 |
| 3 | `s6-t8` (8 hilos) | 5,61 s | 11,20 s | 2,03 s | 3,35 s (14) | 25,04 / 44,89 s | 5,89 / 6,22 s | 3,60 GiB | 6/83 | 1/6 |
| 3 | `s6-vk` (Vulkan) | 3,24 s | 4,54 s | 1,25 s | 1,91 s (14) | 13,28 / 19,60 s | 2,84 / 3,16 s | ver nota | 16/83 | 2/6 |
| 5 | `s6-i8mm` (build dotprod+i8mm) | 3,27 s | 4,10 s | 1,27 s | 1,93 s (14) | 12,67 / 14,97 s | 3,12 / 3,37 s | 4,36 GiB | 10/83 | 1/6 |
| 5 | `s6-ub128` (`-ub 128`) | 4,03 s | 6,16 s | 2,12 s | 1,82 s (14) | 14,31 / 18,13 s | 3,80 / 4,44 s | 3,34 GiB | 8/83 | 1/6 |
| 5 | `s6-rendimiento` (modo fijo de Android) | 5,73 s | 9,02 s | 2,89 s | 2,81 s (14) | 21,81 / 24,66 s | 5,63 / 6,14 s | 3,58 GiB | 0/83 | 0/6 |
| 5 | `s6-kv-q8` (caché q8, incompleta) | 3,73 s | 4,18 s | 1,99 s | 1,67 s (14) | — | — | 3,68 GiB | 2/50 | 0/4 |

`s6-kv-q8` se cortó a pedido en la consulta 50 de 83, en las cuatro primeras conversaciones. Sus tiempos se comparan
contra las mismas líneas de la base: 3,66 s de mediana y 5,49 s de máximo en esas líneas.

## Qué dice cada propuesta

### 1. Aviso sin esperar el motivo

El primer aviso pasa de 13,84 s a 3,68 s de mediana, y el máximo de 16,08 s a 4,01 s. El motivo llega unos 10 s
después, como antes.

- No hay corrida aparte: los pedidos al modelo son los mismos, en el mismo orden. Solo cambia cuándo se muestra el
  aviso.
- Implementado en el panel VoIP:
  - `DetectorSLMJSONCortado.motivo_diferido` y `completar_motivo` en [`detectores.py`](../../detectores.py).
  - En el servidor, el aviso sale con «Posible estafa detectada» y el motivo llega en un segundo evento de la misma
    evaluación (`entrega: "motivo"`), que también queda en `detector.jsonl`.
  - `replay.py` y `correr.py` no cambian.
- Es la única propuesta que baja el tiempo hasta el primer aviso sin tocar el riesgo.

### 2. Generar solo el número

Por línea baja 0,9 s (de 3,74 a 2,85 s), y el máximo de 5,49 a 3,30 s. Generar pasa de 14 tokens a 6 (de 1,75 a
0,76 s).

- **Cómo funciona:** el ejecutor arma el prompt del chat con `/apply-template`, le agrega `{\n  "riesgo":` en el turno
  del modelo y lo manda a `/completion`. La gramática solo deja el número y la coma.
  - Con `c-premisa`, las 83 consultas de la base empiezan con salto (`{\n  "riesgo": `), así que se usó ese prefijo.
  - En una prueba aparte de una sola línea salió el JSON compacto (`{"riesgo":`): el formato depende de la entrada.
- **No da lo mismo, como pedía el issue:** el riesgo cambia en 8 de 83 líneas, siempre entre ±0,1 y ±0,3.
  - En dos líneas de CV2-D-V-BANCO-001 sube de 0,3 a 0,6 y 0,5.
  - El primer aviso cae en la misma línea en las seis conversaciones.
- La causa probable es que esos tokens ahora se procesan en bloque, con el prompt, en vez de generarse de a uno: las
  cuentas en punto flotante dan apenas distinto. No se comprobó si además cambia cómo se parte el texto en tokens.
- La memoria subió 0,3 GiB, sin explicación verificada.

### 3. Hilos y GPU

- **6 y 8 hilos empeoran:** la mediana por línea sube a 4,40 y 5,61 s, y generar es más lento. El teléfono tiene
  cuatro núcleos A520 lentos (CPU 0 a 3, 1,95 GHz) y cuatro A720 (CPU 4 a 7, hasta 2,91 GHz). Más de 4 hilos
  probablemente obliga a esperar a los núcleos chicos, pero no se midió en qué núcleos corrió cada hilo.
- **Vulkan** (GPU Xclipse, `-ngl 99`): 3,24 s por línea. Procesar baja de 1,94 a 1,25 s, pero generar no mejora.
  - El build de Vulkan también trae dotprod+i8mm en la CPU, y da casi lo mismo que `s6-i8mm`, que es solo CPU. La GPU
    no agrega casi nada sobre ese build.
  - Cargar el modelo tarda 14 s, contra 1,7 s en CPU.
  - Es la que más mueve el riesgo: 16/83 líneas, y en CV2-D-V-BANCO-002 el primer aviso se adelanta de la línea 6 a
    la 4.
  - Su `VmHWM` (0,67 GiB) no es comparable: los pesos quedan en memoria del driver y no cuentan como residentes del
    proceso.
- **OpenCL** no se probó: el backend de llama.cpp apunta a GPUs Adreno, y esta es Xclipse.

### 4. Qué son los ~63 tokens nuevos de cada consulta

Se estimó con los datos de la base, sin correr nada más. Es una regresión de los tokens nuevos contra los caracteres
de las líneas nuevas, en las 71 consultas cuya anterior no pidió motivo:

- La recta corta en **unos 32 tokens fijos por consulta**, y cada carácter nuevo suma 0,2 tokens.
- La mediana es 63 tokens nuevos para 151 caracteres nuevos: casi la mitad de lo que se procesa en cada consulta es
  texto fijo.
- Según cómo arma el mensaje `armar_mensaje_usuario`, lo que va después de la transcripción es la oración de cierre
  («Evaluá la llamada con lo disponible hasta la línea N.»), cuyo número cambia en cada consulta, y el cierre de turno
  de la plantilla.
- Al ritmo de la base (unos 31 ms por token), son cerca de 1 s por consulta.
- No se tokenizó para confirmarlo.
- Moverlo antes de la transcripción cambia el prompt: queda, como dice el issue, para después de congelar.

### 5. Lo demás

- **El binario del teléfono no usaba las instrucciones del A720.** El `libggml-cpu.so` de la corrida anterior no
  tiene ni una instrucción `sdot` ni `smmla`, aunque el A720 tiene dotprod e i8mm.
  - Compilado con `GGML_CPU_ARM_ARCH=armv8.6-a+dotprod+i8mm` (1.133 `sdot` y 260 `smmla`), procesar baja de 1,94 a
    1,27 s y la línea de 3,74 a 3,27 s.
  - Generar no mejora (1,93 s), y la memoria sube a 4,36 GiB, probablemente por el reempaquetado de los pesos, aunque
    no se verificó.
  - El riesgo cambia en 10/83 líneas.
- **`-ub 128`:** no aporta (4,03 s). Las consultas nuevas tienen menos de 128 tokens; solo cambia el primer prompt de
  cada servidor, y con eso alcanza para mover el riesgo en 8 líneas.
- **Caché q8** (`-fa on -ctk q8_0 -ctv q8_0`, corrida incompleta): no mejora el tiempo (3,73 s contra 3,66 s en las
  mismas líneas). La memoria pasa de 3,53 a 3,68 GiB, y el riesgo cambia en 2/50 líneas.
- **Modo de rendimiento fijo de Android** (`cmd power set-fixed-performance-mode-enabled true`): empeora mucho, a 5,73 s
  por línea. Lo más probable es que fije las frecuencias en un valor estable, por debajo del pico, pero no se
  verificó. Da exactamente el mismo riesgo que la base en las 83 líneas.

## Lo que esto cambia: el riesgo no es estable ante cambios del runtime

Lo que significa está en [H11](../../../../docs/hallazgos/H11-el-riesgo-cambia-con-el-runtime.md).

`s6-rendimiento` usa el mismo binario, los mismos hilos y el mismo lote que la base, y repite el riesgo en las 83
líneas. Con la misma configuración, entonces, el resultado se repite.

Cualquier cambio de cómo se calcula mueve el riesgo en el 4 al 19 % de las líneas, en ±0,1 en la gran mayoría y nunca en más de ±0,3: los hilos,
el binario, el backend, el tamaño de lote, la caché o el prefijo de la propuesta 2.

- Los cambios caen sobre todo en riesgos de 0,2 a 0,5, alrededor del umbral de 0,3.
- En CV2-D-L-BANCO-007, una legítima, la base da un aviso falso en la línea 2. Ese aviso desaparece con 8 hilos, con
  i8mm, con Vulkan y con `-ub 128`.
- Con seis conversaciones no se puede decir si esto mejora o empeora la detección.

Por eso, la condición del issue («verificar que da lo mismo») no la cumple ninguna de las propuestas que aceleran el
cálculo, salvo la 1. Tampoco la cumpliría el mismo modelo corriendo en Ollama en vez de `llama-server`.

> **Estado: propuesta sin discutir.** Adoptar el cambio 2, el build con dotprod+i8mm o Vulkan implica aceptar que el
> stack del A56 no reproduce línea por línea las corridas de desarrollo. Si se acepta, convendría medir el efecto
> sobre los avisos con más conversaciones antes de la evaluación final. Toca D09 (configuración on-device) en
> [MAPA-DECISIONES.md](../../../../docs/gestion/MAPA-DECISIONES.md).

## Límites

- Una pasada por configuración y seis conversaciones: alcanza para diferencias de 0,5 s o más, no para las chicas.
- Los primeros avisos son 4 o 5 por corrida: el máximo del primer aviso es un solo valor.
- No se midió consumo, temperatura de CPU ni throttling. La temperatura de batería está en `recursos.log`.
- La memoria es `VmHWM` del proceso. No cuenta memoria del driver de GPU.
- No se combinaron cambios: por ejemplo, 1 + 2 + i8mm no se midió junto.

## Archivos

- Una carpeta por corrida, con `turnos.jsonl` (crudo y riesgo por línea), `manifiesto.json` (incluye `/props` del
  servidor), `medir.json` (línea de comando del servidor), `ejecucion.log`, `runtime.log` y `recursos.log`.
- [`serie-s6.sh`](serie-s6.sh) y [`serie-s6.log`](serie-s6.log) son la serie, en orden.
- `contaminadas/`: la primera versión de `s6-ub128` y `s6-kv-q8`.
  - Corrieron con el `llama-server` de Vulkan de `s6-vk` colgado de fondo, porque no terminó con SIGTERM.
  - `s6-ub128` se repitió limpia. `s6-kv-q8` se repitió y se cortó a la mitad.
  - Desde entonces, `medir.py` cierra el servidor con `kill -9` y frena si queda alguno vivo.

## Repetir

Los builds de llama.cpp son del commit `6c01da62`, con el NDK 28.2.13676358, `ANDROID_PLATFORM=android-28`,
`GGML_NATIVE=OFF` y `GGML_OPENMP=OFF`:

- **Base:** el binario de la corrida del 2026-11-06, en `/data/local/tmp/a56-lab/llama`.
- **i8mm:** `-DGGML_CPU_ARM_ARCH=armv8.6-a+dotprod+i8mm`, en `/data/local/tmp/a56-lab/llama-i8mm`.
- **Vulkan:** lo mismo más `-DGGML_VULKAN=ON`, con Vulkan-Headers v1.4.321 y SPIRV-Headers
  vulkan-sdk-1.4.321.0 en el host, en `/data/local/tmp/a56-lab/llama-vk`.

Con el código copiado a `~/a56-172` en Termux (los `.py` de `slm-directo`, `prompts/` y los
`conversaciones-*.json`):

```sh
python3 -I medir.py s6-base-t4 --lista sub-6 -- -t 4
python3 -I resumir.py --base s6-base-t4
```
