# Criterios de prefactibilidad técnica

**Fecha de definición:** 2026-09-17

**Alcance:** prototipo de laboratorio y eventual demo Android

**Issue:** [#24](https://github.com/Corchets/bitacora_tesis/issues/24)

> **Estado: propuesta para revisión del equipo.** Los criterios están definidos y fundamentados,
> pero no cierran el issue #24 hasta que al menos otra persona los revise y el equipo ratifique los
> umbrales operativos.

Este documento define cómo decidir si el pipeline incremental `audio → ASR → detector → alerta`
es técnicamente prefactible. Fija umbrales de aceptación; no afirma que los modelos ya los cumplan.
La evidencia de cumplimiento debe provenir de un benchmark reproducible.

## 1. Hardware objetivo y entorno de referencia

El objetivo de referencia es un **Android de gama media con 6–8 GB de RAM**, sin `root`, sin
permisos privilegiados de telefonía y sin depender de GPU de escritorio ni servicios en la nube.
El presupuesto del proceso es deliberadamente menor que la RAM física para no desplazar al sistema
operativo ni a las demás aplicaciones.

| Perfil | RAM física orientativa | Techo del pipeline | Hilos CPU | Uso en la evaluación |
|---|---:|---:|---:|---|
| Baja | 3–4 GB | 256 MB | 2 (1 ASR + 1 detector) | sensibilidad / límite inferior |
| **Media (objetivo)** | **6–8 GB** | **512 MB** | **4 (3 ASR + 1 detector)** | **gate principal** |
| Alta | clase 8 GB | 1024 MB | 6 (4 ASR + 2 detector) | sensibilidad / límite superior |

**Origen de los presupuestos.** Los techos de 256/512/1024 MB y 2/4/6 hilos provienen del
[recorte de modelos](PRIMERA-INVESTIGACION-MODELOS.md) como configuraciones iniciales para comparar
tres perfiles. Duplicar el techo de memoria entre perfiles permite observar dónde deja de caber el
pipeline; cuatro hilos en el perfil medio reservan un presupuesto conjunto para ASR y detector. Son
límites de la prueba, no un relevamiento de la RAM o los núcleos promedio del mercado, ni una
garantía de que los modelos entren en ellos. Los 6–8 GB físicos identifican una clase de dispositivo
objetivo propuesta por el equipo; al medir en Android se registra el modelo y su hardware real.

El prototipo obligatorio corre en una PC limitada a esos presupuestos, sobre CPU y sin GPU. Esa
medición demuestra comportamiento bajo recursos acotados, pero **no equivale** a una medición en
ARM ni habilita afirmar que el sistema ya funciona en un teléfono. La demo Android es la única que
puede aportar evidencia sobre batería, temperatura y rendimiento móvil real. El recorte de modelos y
las limitaciones de la simulación están en
[PRIMERA-INVESTIGACION-MODELOS.md](PRIMERA-INVESTIGACION-MODELOS.md).

## 2. Gates de aceptación

| Dimensión | Criterio de aceptación | Evidencia mínima |
|---|---|---|
| Flujo incremental | ASR produce parciales y el detector actualiza el riesgo por turno, sin esperar el fin de la conversación. | log monotónico con timestamps de audio, cierre de turno, inferencia y alerta |
| Ritmo sostenido | `RTF` conjunto del pipeline **< 1,00** en cada conversación y en el agregado. No puede crecer una cola de audio pendiente. | `RTF` por conversación, media, p95 y máximo |
| Latencia por turno | Desde el cierre de turno hasta el riesgo actualizado: **p95 ≤ 1,5 s** (objetivo) y ningún perfil se declara aceptable si **p95 > 2,0 s**. El intervalo `(1,5; 2,0] s` se reporta como degradado, no como cumplimiento pleno. | distribución de latencia y definición exacta de inicio/fin |
| Memoria | En el perfil medio, pico de memoria residente del pipeline **≤ 512 MB**. Los perfiles bajo/alto respetan 256/1024 MB. El techo general de 1,5 GB del issue queda reemplazado por estos límites más estrictos. | pico RSS y herramienta/versión usada para medirlo |
| CPU | Perfil medio limitado a **4 hilos**; baja a 2 y alta a 6. No se acepta una corrida que use hilos adicionales de forma silenciosa. | configuración y uso observado de CPU |
| Dependencias | Inferencia local, CPU-only, sin envío de audio o transcripciones y sin descarga de modelos durante la corrida. | configuración, log de red o inspección equivalente |
| Calidad mínima | Reportar WER y recall de términos críticos; una reducción de latencia o memoria no es aceptable si elimina pedidos críticos del texto. El umbral de calidad final se congela en D09 con el piloto. | salida por conversación y errores sobre términos críticos |
| Estabilidad | Tres corridas de 30 minutos por perfil, sin caída, fuga creciente de memoria ni backlog acumulado. | series temporales de memoria, latencia y `RTF` |

Los umbrales de latencia, memoria e hilos son criterios internos del proyecto. No se presentan como
límites universales ni como resultados publicados por terceros.

**Por qué estos umbrales.** `RTF < 1` es la condición mínima para que el procesamiento sostenido
avance más rápido que el audio entrante; por sí sola no garantiza un aviso oportuno. El p95 de
1,5 s por turno es un objetivo inicial de respuesta: exige que casi todos los turnos produzcan una
actualización poco después de terminar. El corte de 2 s distingue una configuración degradada.
Ninguno de esos dos tiempos proviene de un promedio de dispositivos o de una norma clínica: deberán
contrastarse con el margen real entre la alerta y la solicitud o entrega riesgosa (`T_A`, `T_R`,
`T_C`) y con pruebas de uso. Si los resultados muestran que el aviso llega tarde, se revisa el
criterio y se registra la revisión; no se cambia retroactivamente para declarar éxito una corrida.

## 3. Batería y temperatura en la demo Android

La PC limitada no permite concluir nada sobre consumo energético móvil. Si se ejecuta la demo
Android, se comparan dos sesiones de 30 minutos en el mismo dispositivo, nivel de brillo, red,
temperatura inicial y audio: control sin modelos y pipeline completo.

La demo se considera aceptable cuando:

- el pipeline completo consume **como máximo 10 puntos porcentuales de batería en 30 minutos**;
- el costo incremental frente al control es **como máximo 5 puntos porcentuales en 30 minutos**;
- el dispositivo no alcanza `THERMAL_STATUS_SEVERE` o superior; y
- no hay degradación que lleve el `RTF` a 1 o más durante la segunda mitad de la corrida.

Estos números son un **gate operativo propuesto**, no una afirmación de autonomía comercial. Se
eligieron como presupuesto exploratorio para comparar pipeline y control durante una sesión corta;
no representan una media de consumo de teléfonos ni una recomendación del fabricante. Se
registran modelo de teléfono, versión de Android, capacidad/estado de batería, temperatura ambiente,
brillo y conectividad. Android recomienda medir el consumo con Power Profiler, métricas de potencia
o `Batterystats`, y expone el estado térmico mediante `PowerManager` ([documentación de consumo](https://developer.android.com/topic/performance/power/battery-historian),
[API térmica](https://developer.android.com/reference/android/os/PowerManager), consulta
2026-09-17).

Si no se realiza esta prueba, el resultado debe decir **“prefactible en laboratorio; batería y
térmica móvil no evaluadas”**.

## 4. Protocolo mínimo del benchmark

1. Congelar commit, modelos, runtime, configuración, semilla y hardware.
2. Calentar el proceso con una corrida que no se usa para el resultado.
3. Ejecutar tres repeticiones por perfil sobre el mismo conjunto de conversaciones.
4. Capturar timestamps, `RTF`, latencia por turno, pico de memoria, CPU y fallas.
5. En Android, ejecutar control y tratamiento alternados y registrar batería/térmica.
6. Publicar tabla por corrida y conclusión `cumple`, `degradado`, `no cumple` o `no evaluado`.

## 5. Regla de conclusión

- **Prefactible para el objetivo Android:** el perfil medio cumple todos los gates de laboratorio,
  existe una medición en un Android objetivo y esta cumple rendimiento, batería y térmica. El gate
  de calidad crítica debe estar definido antes de clasificar el resultado.
- **Prefactible solo en laboratorio:** cumple el perfil medio en PC limitada, pero no existe medición
  móvil.
- **No prefactible con la configuración evaluada:** falla `RTF`, latencia, memoria, estabilidad o
  calidad crítica. Esto descarta esa configuración, no necesariamente la arquitectura.

La elección de ASR y detector permanece abierta en
[D09](../gestion/MAPA-DECISIONES.md#d09--elegir-asr-y-detector) hasta ejecutar el benchmark.
