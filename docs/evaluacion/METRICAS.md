# Métricas

> **Estado: propuesta sin discutir.** Deriva del [deep research](../../deep-research-report.md), no
> de un relevamiento propio. Se congela al cerrar
> [D07](../gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y
> [D08](../gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

Definición única de cada métrica y sus unidades. Si dos documentos reportan un número con el mismo
nombre, la definición que vale es la de acá.

## Por qué la métrica temporal es la que diferencia la tesis

El objetivo de la defensa es poder decir:

> "El 72% de las estafas fue advertido al menos diez segundos antes de la primera acción crítica."

y no simplemente *"obtuvimos accuracy de 91,4%"*. Un detector que acierta la clasificación después
de que la víctima entregó el código no protege a nadie. Esa distinción es la que
[PI2](../investigacion/PREGUNTAS-DE-INVESTIGACION.md) tiene que poder responder con números.

## Tres marcas temporales, no una

El [anteproyecto](../propuesta/ANTEPROYECTO.md) habla de un solo "momento crítico". Hacen falta
**tres**, y la distinción importa:

| Marca | Definición |
|---|---|
| `T_A` | Momento de la alerta del sistema |
| `T_R` | Inicio del primer **pedido** de alto riesgo (el atacante lo pide) |
| `T_C` | Inicio de la primera **acción de cumplimiento** de la víctima (empieza a obedecer) |

Ejemplo:

```text
00:31 atacante: "tenemos que resolver esto ahora"     URGENCY
00:43 atacante: "no cortes la llamada"                ISOLATION
00:58 atacante: "decime el código que recibiste"      ← T_R
01:04 víctima:  "el código dice..."                   ← T_C
```

Si el sistema avisa en `00:47`, **no** anticipó el pedido (`L_R` < 0), pero **sí** protegió a la
víctima antes de que revelara el código (`L_C` > 0). Con una sola marca esa distinción se pierde, y
es justamente la que hace útil al sistema.

El [método de creación del corpus](../datos-etica/METODO-CREACION-CORPUS.md) ya especifica `T_R` y
`T_C` como parte de cada semilla, y el [manual de anotación](../datos-etica/MANUAL-ANOTACION.md)
define cómo se marcan.

## Márgenes

Valores positivos = el sistema llegó a tiempo.

- `L_R = T_R − T_A` — anticipación respecto del primer pedido riesgoso.
- `L_C = T_C − T_A` — margen de intervención antes de que la víctima empiece a cumplir.

Se reporta la mediana y el rango intercuartil, no el promedio: la distribución tiene cola y el
promedio la esconde.

## Tasa preventiva

La métrica de titular:

```
Preventive@δ = #{ i : T_A,i ≤ T_C,i − δ } / #{ llamadas de vishing }
```

Se reporta para δ = 5 s, 10 s y 20 s.

**Pendiente de decidir:** si `Preventive@δ` se mide contra `T_C` o contra `T_R`. Son dos
afirmaciones distintas en la defensa y hay que elegir una antes de congelar el test.

## Definición de `T_A` con histéresis

`T_A` **no** es la primera predicción que cruza el umbral. Es la primera que **se mantiene durante
dos actualizaciones consecutivas** (o una histéresis equivalente).

Motivo: un pico aislado de 200 ms contaría fraudulentamente como "detección temprana" e infla los
resultados. Sin esta regla, `Preventive@δ` es trivialmente manipulable bajando el umbral.

## Evaluación completa

La métrica temporal no reemplaza al resto. Se reporta:

| Dimensión | Métricas |
|---|---|
| ASR | WER, recall de términos críticos |
| Clasificación global | precision, recall, F1, AUPRC, AUROC |
| Llamadas legítimas | % con al menos una falsa alarma |
| Carga de falsas alarmas | falsas alertas por hora |
| Detección temporal | `Preventive@5/10/20s`, mediana de `L_R` y `L_C` |
| Evolución | métricas usando solo 25%, 50%, 75% y 100% de la llamada |
| Maniobras | macro-F1 de etiquetas multi-label |
| Latencia | p50/p95 desde audio hasta decisión |
| Rendimiento móvil | memoria, CPU, real-time factor |
| Explicación | correspondencia entre motivo mostrado y etiqueta real |

La curva de evolución (25/50/75/100%) es la evidencia directa de que la detección es incremental y
no una clasificación offline disfrazada.

## El primer gráfico que hay que producir

**Riesgo vs. tiempo**, con las tres marcas superpuestas:

```text
riesgo
1.0 |                             █████████
0.8 |              █████████ █████
0.6 |         █████
0.4 |    ████
0.2 |████
0.0 +-------------------------------------- tiempo
        autoridad   urgencia     código
                      ↑            ↑
                   ALERTA       CRÍTICO
```

Todo el resto del proyecto es, en esencia, lograr que esa figura sea científicamente válida.

## Preguntas abiertas

- ¿Anotamos las tres marcas o solo `T_R`? Anotar `T_C` obliga a guionar también la reacción de la
  víctima, lo que encarece cada semilla del corpus.
- ¿Cuál es la restricción de falsos positivos fijada de antemano? El anteproyecto la menciona pero
  no la define. Sin ese número la hipótesis no es falsable.
- ¿`Preventive@δ` contra `T_C` o contra `T_R`?
