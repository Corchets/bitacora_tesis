# Curación completa de los datos y antecedentes de Tito

Fecha: 2026-10-28. Trabajo técnico del [#96](https://github.com/Corchets/bitacora_tesis/issues/96),
por pedido explícito del usuario de revisar todo el material y apartar lo que no
sirve. **Revisión y selección realizadas por IA**, sin simular personas del equipo.
Esta entrega amplía la [revisión focalizada anterior](REVISION-IA-TITO-2026-10-28.md).

**Resultado:** se conservan 4.811 realizaciones del banco y 122 conversaciones de
desarrollo; se apartan 1.189 realizaciones y 28 conversaciones del paquete
supervisado nuevo. La selección está materializada por identificador y huella;
no es una lista de cosas a revisar después. Las observaciones y los ajustes
propuestos siguen distinguidos de referencias humanas aprobadas.

> **Estado: propuesta sin discutir.** Supervisión y protocolo. La selección y los informes
> fueron aprobados por el usuario el 2026-10-28 (ver registro siguiente). Esa
> aprobación no acuerda
> nuevas reglas de supervisión, particiones ni evaluación. Esas decisiones siguen
> en [D07](../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico)
> y [D08](../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).
> El paquete conserva `habilitado:false` y no cambia `revision_humana`.

## Aprobación del usuario — 2026-10-28

El usuario de esta sesión indicó: «ahi revise los informes y apruebo 96».
Se registra la aceptación de la curación y los informes entregados: 4.811
realizaciones del banco y 122 conversaciones conservadas, con los descartes,
observaciones y límites documentados. Manifiesto aprobado:
[SELECCION-TITO-2026-10-28.json](SELECCION-TITO-2026-10-28.json), SHA-256
`012080dfdd8d6bdcba4f99cf664d86d77112421b5b0bd8b0e804d6e2aafe7443`.

[#96](https://github.com/Corchets/bitacora_tesis/issues/96) queda aprobado y
cerrado por indicación expresa del usuario, para continuar la secuencia de #95.
Codex había limitado esa aprobación a los informes y creado #103 por una
interpretación errónea. El usuario lo corrigió: #103 se retiró como no planificado
y se eliminaron su bloqueo de #98 y su relación de subissue. No constituye una
condición adicional ni exige repetir la aprobación de #96. Las fases posteriores
aplican sus criterios propios; no se inventan datos o resultados para cumplirlos.

La lectura y aprobación de informes es un aporte humano real; no se registra como
anotación independiente de cada caso por cuatro personas ni como adjudicación de
sus diferencias. No se altera `revision_humana`, `habilitado:false`, Tito ni sus
pesos. D07/D08/D09 permanecen abiertas; se continúa la secuencia prevista sin
el seguimiento adicional creado por error.

## Qué se revisó y qué queda seleccionado

| Material revisado completo | Se conserva | Se aparta | Interpretación |
|---|---:|---:|---|
| 6.000 realizaciones, 300 familias del banco histórico | 4.811 | 1.189 | 1.937 `estafa` y 2.874 `legitima` conservadas. Las 1.189 incluyen las 480 exclusiones anteriores: hay 709 exclusiones adicionales. |
| 150 conversaciones completas con sus referencias y notas | 122 | 28 | 74 sin observaciones sustantivas de selección y 48 con observaciones. No implica que tengan revisión humana. |
| 53 antecedentes escritos dentro de esas 150 | 51 en selección, originales de los 53 preservados | 2 del uso supervisado nuevo | Uso de regresión/desarrollo expuesto; no evaluación independiente. |
| 97 conversaciones `corpus_v2` de desarrollo | 71 | 26 | Candidatas de desarrollo, todavía sin independencia acreditada. |

Las 300 familias tienen decisión registrada; 267 conservan al menos una
realización y 33 quedan completamente apartadas. No se descartó una familia
entera cuando el problema podía localizarse en variantes concretas, salvo las
exclusiones históricas ya documentadas y familias con problemas estructurales.
Las 24 exclusiones históricas no se rehabilitaron por encontrarles variantes
rescatables sin reescribir y revisar su fuente.

La lectura del banco se hizo **por composición exacta, con todas sus excepciones**:
se revisaron las cinco aperturas y cuatro cierres cuando se podían combinar;
cuando no, se mostraron todas las piezas y las veinte combinaciones. La reconstrucción
se comprueba contra cada una de las 6.000 cadenas exportadas. Esto evita leer
solo la primera y última realización como en la entrega histórica; no convierte
las realizaciones relacionadas en escenarios independientes.

Además se contrastaron el ajuste (`entrenar_tito.py`), artefacto persistido
(`tito_logreg.json`), carga/inferencia (`tito_real.py`), flujo (`filtro_tito.py`),
validación de datos (`datos_tito.py`) y antecedentes de costos/resultados/estado
software. Sus dictámenes y huellas están en `artefactos` del registro de curación.
Las veinte fuentes registradas del banco se conservan como procedencia: el
verificador controla sus huellas y que las familias las referencien. **No se
realizó una nueva revisión bibliográfica de sus páginas web**; las fuentes de
modalidades no certifican la clase de cada frase sintética ni un trámite vigente.

La reserva final queda excluida del alcance: no se leyó, copió ni ejecutó.

## Criterio aplicado

Se conservó lo que aporta una situación interpretable para detección incremental:
pedidos de acceso o dinero con contexto, usos propios de códigos, solicitudes
sensibles legítimas, negaciones, relatos, citas, pedidos indirectos y contexto
prolongado. Un caso difícil o una predicción incorrecta del detector **no** fueron
motivo de descarte. No se ejecutaron modelos ni se eligió por métricas.

Se apartó del uso supervisado nuevo lo que presenta incoherencia central de
actores, hechos o fechas; combinaciones de bloques incompatibles; o una etiqueta
binaria que requiere conocer una intención de autor que el texto no permite
contrastar. «Apartar» no significa reetiquetar como legítima ni afirmar que nunca
podría ser fraude. Los casos ambiguos pueden seguir sirviendo como preguntas de
calibración o pruebas cualitativas; no se fuerzan como respuestas binarias ciertas.

La evaluación debe seguir mostrando cuántos casos se apartaron y por qué.
Reducir ambigüedades cambia la población del conjunto: una mejora sobre esta
selección no sería comparable directamente con el banco/corpus anterior ni prueba
mejora en llamadas reales. No se quitaron casos retrospectivamente de las corridas
archivadas ni de sus denominadores.

## Descartes concretos de conversaciones

El registro contiene el motivo individual y citas de las 28, sin omisiones.
Agrupación para orientar su lectura:

| Motivo | IDs apartados |
|---|---|
| Incoherencia central del guion | `CV2-D-L-BANCO-004`: ingreso supuestamente pendiente que después era de otro alias; `CV2-D-L-ORGANISMO_PREVISIONAL-002`: domingo 12 seguido de lunes 14; `CV2-D-L-TRABAJO-003`: horas trabajadas/cubiertas incompatibles. |
| Episodio truncado sin pedido crítico ni clase fraudulenta distinguible del escenario autoral | `CV2-D-V-BANCO-011/012`, `CV2-D-V-ORGANISMO_PREVISIONAL-005/006`, `CV2-D-V-PREMIO-005/006`, `CV2-D-V-SOPORTE-007/008`, `CV2-D-V-WHATSAPP-007/008`, `TR-12-corta-antes-del-pedido`. Los sufijos con barra abrevian dos IDs completos. |
| Acción sensible compatible con gestión genuina, sin evidencia suficiente para exigir la clase fraude | `CV2-D-V-BANCO-005/009`, `CV2-D-V-FAMILIAR-001/003/005/006`, `CV2-D-V-ORGANISMO_PREVISIONAL-002/003/004`, `CV2-D-V-PREMIO-001`, `CV2-D-V-SOPORTE-001/002/005`, `LAB-giro-sin-plata`. |

Hay once episodios sin pedido marcado: permanecen disponibles para análisis
cualitativo de sospecha. Su exclusión del paquete binario nuevo no resuelve la
política global de evaluación de esas llamadas ni autoriza contarlas como
legítimas o detecciones correctas por defecto. Tampoco se calculan márgenes
respecto de un `T_R` ausente.

Las ocho regresiones de `REGRESION_OCHO` se preservan explícitamente, incluido
TR-12 aunque se aparte del uso supervisado nuevo. No se borra evidencia histórica
para que el filtro parezca mejor.

## Problemas encontrados en el banco completo

- **Cruces de voz dentro de una realización:** por ejemplo, `banco_044` abre como
  proveedor o colegio y cierra como quien paga; `banco_049` mezcla estudio contable
  y contribuyente. Se excluyen esas combinaciones, no las aperturas del cliente
  que sí encajan. También se identifican cambios de familiar/vendedor a banco o
  servicio en familias cotidianas. Los índices exactos están en `variantes_apartadas`.
- **Discordancia entre actores:** `identidad_027` combina compañero/amigo con
  «ella/juntas». Se apartan seis realizaciones, manteniendo las compatibles.
- **Positivos demasiado genéricos:** asistencia remota, un gasto de envío o datos
  de tarjeta no especificados pueden describir atención genuina. Se conservan
  los pedidos claros de OTP/contraseña/CVV, accesos a otro equipo, transferencias
  de validación o desvíos explícitos; los demás requieren contexto o reescritura.
  No se sostiene que toda asistencia remota o todo adelanto sean estafas.
- **Tema declarado ajeno al contenido:** `cotidiano_039` dice `falso_plan_salud`
  pero sus textos tratan pedidos de comida. `cotidiano_075`–`cotidiano_084`
  contienen negativos diversos reescritos, no veinte ejemplos del tema del nombre.
  Se conserva contenido útil, pero esos temas se retiran como prueba de cobertura.
- **Paráfrasis y pistas artificiales:** se mantienen como desarrollo relacionado;
  «oficial», «cuenta habitual» o «confirmé» son afirmaciones del guion, no pruebas
  externas de autenticidad. Familias cercanas y textos emparentados no quedan
  independientes porque tengan otros IDs. Esta entrega no inventa un split.

## Qué corregir en las referencias conservadas

Dos ajustes concretos quedan preparados, separados de los JSON originales:

| Caso | Referencia autoral | Recomendación IA y evidencia |
|---|---|---|
| `CV2-D-V-BANCO-010` | `T_R=13` | Proponer `T_R=15`: L13 vincula la serie con la gestión, pero L15 pide decir los números. L14 es una pregunta del receptor. Mantener la lectura inducida como alternativa pendiente. |
| `CV2-D-V-ORGANISMO_PREVISIONAL-001` | `T_C=19` | Proponer primer cumplimiento en L13: ya dicta DNI y fecha. L19 completa las fotos. El pedido es compuesto; conservar ambos hitos sin ignorar la entrega parcial anterior. |

Los ajustes están en `ajustes_referencia_ia`; no se aplicaron a los originales ni
se presentaron como adjudicación. Las dudas de inicio/completitud en TR-07,
TR-10 y CV2-D-V-WHATSAPP-006 siguen registradas. Tampoco se resolvió por cuenta
propia el alcance de secretos físicos ni el cumplimiento parcial del usuario de
SC-SOPORTE-CLAVE.

Se mantiene el hallazgo de supervisión: 13 legítimas codifican evidencia como
`pedido`, mientras otras solicitudes legítimas similares usan `contexto`.
`pedido_visible` e `indicio_parcial` son estados de evidencia, **no etiquetas ya
acordadas de derivación de Tito**. El futuro puede aclarar que un «código» era un
candado; no se usa ese final para exigir certeza en el prefijo anterior.

## Qué mantener y qué conclusiones retirar

Se conserva el Tito histórico y su código para reproducción y comparación. Su
SHA-256 sigue siendo
`fb601eaa8ecb8d51e0d37f1d5af00ec4ca41706ef638fe2780ae276e5098eccd`.
Sigue representando un ajuste sobre **5.520 textos**, no sobre los 4.811 de esta
selección. Filtrar ahora no desaprende datos ni vuelve independiente al banco.

Se conservan las 96 evaluaciones históricas como evidencia exploratoria de ocho
conversaciones expuestas. Se descarta utilizarlas para sostener generalización,
ahorro móvil, beneficio causal separado del indicio o necesidad de fine-tuning.
Las pruebas con dobles prueban el recorrido del software; no validan calidad
aprendida ni sustituyen anotaciones humanas. No se realizaron nuevas corridas.

## Usar y comprobar la selección

- [CURACION-TITO-2026-10-28.json](CURACION-TITO-2026-10-28.json): fuente de verdad
  de los 150 juicios por conversación, 300 por familia y dictámenes de artefactos.
- [SELECCION-TITO-2026-10-28.json](SELECCION-TITO-2026-10-28.json): manifiesto
  derivado con los 6.000 IDs y 150 conversaciones, cada uno con selección y huella.
  Los motivos del banco se consultan por familia; no se duplican los textos del banco.
- [curar_datos_tito.py](curar_datos_tito.py): comprueba cobertura total, exportación
  contra fuentes primarias, fuentes registradas, huellas, citas y exclusiones
  históricas antes de producir el manifiesto. No genera nuevos juicios semánticos.

Desde `experiments/slm-directo/`:

```bash
python curar_datos_tito.py --listar-casos apartar
python curar_datos_tito.py --listar-casos conservar
python curar_datos_tito.py --mostrar-banco 0 15
python curar_datos_tito.py > /tmp/SELECCION-TITO.json
cmp SELECCION-TITO-2026-10-28.json /tmp/SELECCION-TITO.json
python -m unittest tests.test_curacion_tito tests.test_datos_tito
```

Los rangos de familias son desde cero y excluyen el límite superior. La lista de
casos conservados indica cuáles quedan como regresiones y cuáles como desarrollo
sin independencia acreditada; no habilita entrenamiento ni abre evaluación.

Verificación del 2026-10-28: 56 pruebas verdes (seis de curación y 50 de datos),
control de los 6.000 registros contra su fuente, de los 150 pares contra sus
huellas/citas, y reconstrucción sin pérdida de las 300 familias. Los controles
rechazan revisión incompleta/duplicada, cambio de fuente, revisión humana ficticia,
rehabilitación de exclusiones históricas y un ID reservado antes de parsearlo.

La curación completa solicitada está entregada y aprobada por el usuario.
El usuario aprobó #96 y su cierre; se continúa con los tickets posteriores de
#95, sin el seguimiento adicional #103, retirado por error de interpretación.

## Registro de cierre en GitHub

El [comentario de cierre de #96](https://github.com/Corchets/bitacora_tesis/issues/96#issuecomment-6473338190) registra la aprobación y sus límites, corrige el seguimiento #103 retirado y conserva
la distinción entre aceptación de informes y habilitación experimental. No se
marcan como cumplidos los criterios originales que se trasladaron al seguimiento.
