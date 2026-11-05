# Datos revisados y particiones verificables para evaluar a Tito (#96)

> **Curación e informes aprobados por el usuario el 2026-10-28 (#96).**
> #96 queda aprobado y cerrado. El seguimiento #103 fue creado por error y
> retirado; no agrega una condición para continuar la secuencia acordada.
> Decisiones abiertas: [D07](../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico)
> y [D08](../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

**Selección completa vigente:** [curación de 150 conversaciones y 6.000 realizaciones](CURACION-TITO-2026-10-28.md), con conservadas y apartadas por ID.

**Para organizar la revisión humana:** [entrada del equipo](#entrada-para-la-revisión-del-equipo--2026-10-28).

**Revisión técnica realizada el 2026-10-28:** [dictamen IA, hallazgos y propuestas](REVISION-IA-TITO-2026-10-28.md). No reemplaza la revisión humana pendiente.

**Aprobación y alcance del cierre:** [registro del 2026-10-28](CURACION-TITO-2026-10-28.md#aprobación-del-usuario--2026-10-28). No acredita anotaciones independientes ni cambia las puertas de validación.

## Qué hay

- [datos_tito.py](datos_tito.py): recorrido público conversaciones → prefijos →
  particiones → manifiesto → informe. Solo stdlib, sin descargas ni modelos.
  Nunca lee la reserva: la rechaza por identificador/partición.
- [tests/test_datos_tito.py](tests/test_datos_tito.py): pruebas de
  comportamiento con dobles (incluyen regresiones de cada fallo
  corregido). Se corren sin red ni GPU:
  `python -m unittest tests.test_datos_tito` desde este directorio.

## Contratos reutilizados (no modificados)

`casos.py` (`Linea` —reutilizada directamente, sin dataclass duplicada—,
`CLASES`, `PEDIDOS`, `ETIQUETAS`, `EVENTOS`), `correr.procesar_caso` (recorrido
incremental), `filtro_tito`/`tito_real` (interfaz `puntuar`, umbral 0,5 en el
flujo) y las constantes de procedencia de `entrenar_tito.py`
(`BANCO_COMMIT`, hashes declarados). La familia de variantes del banco
(`banco_001`, 276 familias) se distingue de la modalidad amplia del corpus
(`banco`, `whatsapp`, `soporte`, ...): solo la primera agrupa variantes
relacionadas que no pueden cruzar particiones.

## Antecedente auditado (solo lectura, sin sobrescribir)

Banco histórico del commit `bb542e1` (`entrenar_tito.py`): 6.000 registros,
5.520 aceptados en 276 familias, 480 apartados en 24 exclusiones con motivo.
Verificado por `auditar_banco_historico()` contra los hashes declarados.
Ese banco ya ajustó el artefacto actual (`tito_logreg.json`): separarlo
retrospectivamente no lo vuelve evaluación independiente; el módulo lo
rechaza (`familias_artefacto`). Las ocho conversaciones de la demo
(`demo.sh`, `CASOS_DEMO`) se conservan como regresión, no como evaluación.

## Preparación técnica delegada — 2026-10-29

El usuario delegó expresamente resolver la preparación técnica: «no quiero pensar esto
quiero que funcione». Esto autoriza definir configuraciones de **desarrollo** y realizar
la preparación por IA; no acredita revisores humanos, no cierra las decisiones globales
D07/D08/D09 y no promete una mejora sin medir. Los pedidos previos de otra aprobación
genérica para elegir particiones, supervisión y búsqueda quedan reemplazados por esta
configuración operativa. Los requisitos de calidad se comprueban técnicamente.

Fuentes ejecutables: [configuración](CONFIGURACION-TITO-2026-10-29.json),
[particiones por ID y hash](PARTICIONES-TITO-2026-10-29.json) y
[generador](preparar_particiones_tito.py). El compromiso de ejecución y sus criterios
viven en #98–#102. La selección de veinte aprobada en #101 se conserva sin cambios.

| Material | Entrenamiento | Validación | Diagnóstico | Comparación | Apartado del ajuste por relación con comparación | Regresión |
|---|---:|---:|---:|---:|---:|---:|
| Conversaciones conservadas | 34 | 10 | 10 | 20 | 45 | 3 |
| Frases del banco conservadas | 3.843 | 968 | — | — | — | — |

En conversaciones, entrenamiento tiene 12 fraudulentas y 22 legítimas (incluye difíciles);
validación 4 y 6; diagnóstico 2 y 8; comparación 10 y 10. No se fuerza balance artificial
del diagnóstico dividiendo grupos. Las 45 relacionadas se excluyen del ajuste, pero no se
agregan a las veinte. Las regresiones históricas conectadas a un escenario de comparación
quedan dentro de las relacionadas excluidas, no se duplican entre particiones.

El generador comprueba hashes, escenarios base/semillas, pares declarados, alias de
paráfrasis LAB, duplicados completos y familias del banco. El reparto aproximado 80/20 es
por grupos con semilla 42; los conteos exactos son los del manifiesto. **Todavía se debe
auditar la relación semántica entre fuentes banco/conversaciones**: ese trabajo es parte
de #98–#99, no un acuerdo para pedir otra vez al usuario. Si implica exclusiones, registrar
la versión nueva y sus conteos sin cambiar las veinte. No afirmar independencia solo por
IDs distintos. El banco completo fue usado por Tito viejo; su nueva validación no es
independiente de ese artefacto.

El Tito nuevo principal ve el historial acumulado línea por línea con hablantes A/B.
El control ve la frase actual; Tito viejo conserva sus pesos e interfaz originales.
Para historiales que excedan 128 tokens, procesar todos los tokens en bloques y combinar
sus representaciones ponderando tokens de contenido; no descartar líneas. Esto requiere
implementación en #99 y no equivale a atención entre todos los bloques. La misma
construcción debe usarse al entrenar y al inferir.

Se acota #99 a dos entradas × tres valores de C × tres umbrales: seis clasificadores y
18 configuraciones de validación como máximo; seed 42 y RoBERTuito congelado. No se abre
una búsqueda libre de ventanas. Los valores, desempates y presupuesto condicional de
fine-tuning están en la configuración. El candidato principal conserva historial acumulado;
el control aislado sirve para interpretar el efecto de la entrada.

**Supervisión:** preparar 0 (no derivar), 1 (consultar al SLM) o nulo (incierto) por prefijo,
con revisión IA trazable que solo vea el texto hasta ese instante y cite su evidencia.
Un saludo no hereda la clase final; tampoco la ausencia de una anotación se transforma en
negativo. Los inciertos quedan fuera de la pérdida, con cobertura explícita. Esta revisión
es trabajo técnico de #99 y no se presenta como anotación humana. Conservar referencias
originales y no alterar `revision_humana` ni la puerta formal de `datos_tito.py`. Para una
corrida exploratoria implementar una autorización de desarrollo separada y explícita,
sin falsificar el cumplimiento de los requisitos humanos del protocolo final.

**Estado observable:** particiones/configuración materializadas y controles estructurales
verificados; no hay etiquetas binarias nuevas de prefijos, nuevos pesos, entrenamiento,
fine-tuning ni corridas de los diez SLM ejecutados por esta preparación. La autorización
para resolver valores técnicos queda definida; la auditoría, etiquetas, adaptación de
entrada y entrenamiento siguen siendo entregables que los workers deben producir.

Reproducir y comprobar:

```bash
python experiments/slm-directo/preparar_particiones_tito.py --salida /tmp/particiones-tito.json
cmp experiments/slm-directo/PARTICIONES-TITO-2026-10-29.json /tmp/particiones-tito.json
```

## Estado histórico al 2026-10-27

- 150 casos de desarrollo válidos (`python casos.py`), **0 con
  `revision_humana: true`**. La revisión del equipo y el acuerdo de
  composición/tamaño/reglas/proporciones no existen todavía.
- La reserva (200 `CV2-T-*`) sigue fuera de esta rama y no se leyó.

## Criterios originales de #96 y estado del módulo de datos

El detalle siguiente describe la preparación y el contrato técnico del módulo.
La aceptación del usuario de #96 está registrada arriba; no se traslada su aprobación
a otro ticket ni se inventan anotaciones, particiones o resultados de fases posteriores.

- Cumple: inventario con procedencia y exclusiones; rechazo de cruces
  (semilla, familia, par, grupos semánticos), conversaciones completas
  duplicadas entre particiones aun con la misma clase, conflictos de
  referencia para diálogos duplicados, identificadores duplicados y
  referencias inválidas (vocabulario de clase/pedido/evento/etiqueta,
  rangos y tipos de líneas, coherencia pedido–`T_R`–`T_C`–evidencia);
  las ocho históricas solo entran como regresión; el diagnóstico es una
  partición disjunta verificada dentro del recorrido (no en un helper
  desconectado); prefijos con supervisión solo del texto visible y
  `clase_conversacion` como metadato final nunca usado como etiqueta del
  prefijo; manifiesto reproducible con fecha inyectable; reserva rechazada
  sin leerla. Una línea suelta repetida (un saludo común en llamadas
  distintas) no cuenta como duplicado. Una legítima sin pedido crítico no
  inventa evidencia (admite lista vacía; lo presente se valida igual).
  Coherencia pedido–`T_R`–`T_C`: se reutiliza el contrato vigente de
  `casos.py` sin modificarlo (`T_C` posterior estricto a `T_R`, rechaza
  `T_C <= T_R`).
  Las entradas inválidas (etiquetas o eventos mal formados, evidencia no
  lista, referencia con otra estructura) vuelven informe no evaluable en
  vez de romper el recorrido. La referencia acepta `Referencia` o dict
  con los mismos campos.
- Pendiente (bloquea habilitar el uso): revisión humana efectiva con
  originales, desacuerdos y adjudicaciones; acuerdo de composición, tamaño,
  reglas de referencia y proporciones (coordinar con #32/#55); cobertura
  real de la muestra; diagnóstico con material revisado. El módulo informa
  cada bloqueo exacto (`puede_habilitarse`, `informe_validacion`) en vez de
  completar artificialmente. No se inventan revisores, acuerdos, cuotas ni
  etiquetas revisadas. La puerta es fail-closed: exige revisión trazable
  (lista no vacía de revisores identificables, originales conservados con
  su ruta o identificador, desacuerdos y adjudicaciones relacionados por
  caso o id, conteo de revisadas cruzado con el manifiesto) y acuerdo con
  contenido (composición, tamaño, reglas de referencia, proporciones
  presentes y no vacíos); ningún dict o lista vacío, ningún faltante y
  ninguna discrepancia con el manifiesto habilita. El software no
  autentica personas ni fija cuotas o metodología nueva: solo verifica la
  estructura que el equipo aporta fuera del módulo.
  El `informe_validacion` conserva el conteo y las huellas del manifiesto;
  la puerta rechaza lo declarado cuando discrepa del manifiesto o la
  revisión está incompleta.

> **Estado: propuesta sin discutir.** Los criterios estructurales de la
> puerta (sin cuotas de revisores ni longitudes mínimas) se proponen
> enlazados a
> [D07](../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico)
> y [D08](../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

## Propuestas históricas anteriores a la delegación del 2026-10-29

Los parámetros operativos de #98–#100 se resuelven en la sección de preparación técnica delegada. Este registro conserva antecedentes; no exige otra aprobación genérica para esa preparación. Los acuerdos finales de D07/D08 siguen abiertos.

- Tamaño y proporciones entrenamiento/validación/evaluación, ventanas
  candidatas y criterio de insuficiencia para fine-tuning: se proponen y
  acuerdan antes de producir material dependiente, con
  [D07](../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico)
  y [D08](../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).
  Esta entrega no cierra ninguna de las dos ni fija cuotas.

## Entrada para la revisión del equipo — 2026-10-28

**Primero:** acordar la lista de la sección siguiente. Después, cada integrante
abre solamente sus enlaces de diálogo y completa una ficha propia por caso, con
el [manual §§1–4](../../docs/corpus/MANUAL-ANOTACION.md#1-qué-registramos-por-conversación)
a mano. Los JSON de `casos/referencia/` son respuestas propuestas: se consultan
recién al comparar los originales. No constituyen la ficha que hay que copiar.

Esta preparación corresponde al [#96](https://github.com/Corchets/bitacora_tesis/issues/96),
asignado a Ignacio; no satisface todavía su revisión humana. El backlog y sus
criterios siguen en GitHub. No habilita #98, #99 ni #100.

### Inventario comprobado y límites de procedencia

Control del 2026-10-28 sobre HEAD `0a95968b7de9ed1a689cecb4a88a3e8e9f373f8e`:
`python casos.py` desde `experiments/slm-directo/` informa 150 casos válidos:
97 `corpus_v2`, 26 `laboratorio`, 14 `piloto_escrito` y 13 `trampa`.
Hay 75 referencias vishing y 75 legítimas (51 `legitima` y 24
`legitima_dificil`); las 150 tienen `revision_humana:false`. Es validez de
formato, no aprobación semántica. No se abrió la reserva.

| Material | Uso que puede prepararse | Evidencia que falta |
|---|---|---|
| Banco histórico usado por Tito | Antecedente de ajuste, sin modificarlo; nunca evaluación independiente retrospectiva. | No se recupera independencia cambiando la partición. Procedencia en `entrenar_tito.py` y auditoría por API arriba. |
| Ocho casos de `REGRESION_OCHO` en `datos_tito.py` | Calibración humana y regresiones. El validador solo admite `regresion` para ellos. | Revisión y adjudicación humanas; no son evaluación nueva. |
| Otros 45 antecedentes escritos | Calibración y desarrollo expuesto; conservar los originales. | Auditoría de uso en ajustes y corridas, parentesco y revisión; no presumir diagnóstico independiente. |
| 97 `corpus_v2` de desarrollo | Candidatos para revisión; sin asignación experimental nueva. | Uso previo real respecto de cada artefacto, semillas/pares/relaciones semánticas, revisión y acuerdo de destino. ID nuevo no prueba independencia. |

Los antecedentes y la revisión asistida se explican en
[AUDITORIA-53-HISTORICOS.md](casos/AUDITORIA-53-HISTORICOS.md) y
[REVISION-CORPUS-V2.md](casos/REVISION-CORPUS-V2.md). Para cada candidato falta
registrar quién lo produjo, versión/hashes de texto y referencia, relación con el
banco y otros escenarios, y si fue usado para ajustar, diagnosticar o seleccionar
cada modelo. No hay aquí una partición independiente habilitada.

### Lista común candidata para acordar

> **Estado: propuesta sin discutir.** Revisar estas 12 conversaciones como primera
> muestra común de trabajo, por los cuatro integrantes de forma independiente,
> para probar el procedimiento de [D07](../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico).
> Su número no fija tamaño del corpus ni proporciones experimentales de
> [D08](../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).
> Se puede quitar o reemplazar material antes de anotar; registrar la lista acordada.

La tabla permite abrir solo los diálogos. No contiene respuestas ni marcas
sugeridas. Los IDs originales pueden anticipar clase o tema; esta propuesta no
es una anotación ciega a ese indicio. Quien ya haya visto JSON, auditorías o
resultados lo declara en su ficha. No atribuir independencia de respuestas a
una persona que ya las leyó.

| ID del diálogo | Líneas |
|---|---:|
| [SC-WA-CODE-01-e01](casos/texto/SC-WA-CODE-01-e01.txt) | 5 |
| [LG-WA-CONSULTA-01-e01](casos/texto/LG-WA-CONSULTA-01-e01.txt) | 4 |
| [TR-02-codigo-del-candado](casos/texto/TR-02-codigo-del-candado.txt) | 8 |
| [TR-03-negacion-y-consejo](casos/texto/TR-03-negacion-y-consejo.txt) | 10 |
| [TR-05-asado-con-transferencia](casos/texto/TR-05-asado-con-transferencia.txt) | 27 |
| [TR-07-pedido-partido-en-dos-lineas](casos/texto/TR-07-pedido-partido-en-dos-lineas.txt) | 10 |
| [TR-09-victima-se-niega](casos/texto/TR-09-victima-se-niega.txt) | 12 |
| [TR-10-ofrecimiento-inducido](casos/texto/TR-10-ofrecimiento-inducido.txt) | 14 |
| [TR-13-turno-medico-pide-dni](casos/texto/TR-13-turno-medico-pide-dni.txt) | 12 |
| [CV2-D-V-BANCO-001](casos/texto/CV2-D-V-BANCO-001.txt) | 38 |
| [CV2-D-V-WHATSAPP-006](casos/texto/CV2-D-V-WHATSAPP-006.txt) | 36 |
| [CV2-D-L-SOPORTE-001](casos/texto/CV2-D-L-SOPORTE-001.txt) | 25 |

**Para quien coordina, después de recibir los originales:** cobertura candidata,
verificada por lectura de estos diálogos, no adjudicada por personas:

| Dificultad del #96 | Casos que permiten discutirla |
|---|---|
| Legítima difícil / solicitud sensible legítima | TR-02, TR-05, TR-13, CV2-D-L-SOPORTE-001. |
| Negación, cita, relato y advertencia | TR-03 contiene consejos y pedidos de terceros reportados como hipotéticos; LG-WA contiene prohibición de compartir. Falta un relato retrospectivo desarrollado de un fraude ocurrido. |
| Pedido indirecto y evidencia repartida | TR-07, TR-10 y CV2-D-V-WHATSAPP-006; discutir inicio del pedido, sin dar por aprobadas las posiciones del JSON. |
| Contexto prolongado | CV2-D-V-BANCO-001 y CV2-D-V-WHATSAPP-006; contraste largo legítimo TR-05. |
| Cumplimiento y negativa sin cumplimiento | SC-WA y TR-09 permiten contrastar desenlaces; verificar observabilidad sin inferir entrega por una intención. |

La lista no cubre todas las modalidades, pedidos remotos, fraudes sin pedido ni
cumplimientos parciales, y no mide representatividad. Tampoco contiene audio ni
prueba acuerdo temporal. Es calibración de desarrollo: los dos ejemplos iniciales
y TR-02 pertenecen a las ocho regresiones; los otros seis TR son antecedentes;
los tres CV2 son candidatos sin independencia acreditada. Haberlos revisado no
resuelve qué material nuevo destinar a diagnóstico o evaluación independiente.

### Ficha para cada anotación original

> **Estado: propuesta sin discutir.** Usar esta ficha en Markdown, con un archivo
> local separado por integrante y sin compartir respuestas hasta que los cuatro
> entreguen; herramienta y custodia se acuerdan en
> [D07](../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico).
> No se crearon carpetas ni originales ficticios. Al recibir aportes, se propone
> conservar archivos `ANOTACION-<id_revisor>-AAAA-MM-DD.md` en `casos/`, carpeta ya
> existente, con una ficha por caso y sin sobrescribir entregas anteriores.

Copiar el bloque vacío. Cada persona identifica su entrega, fecha, versión de
muestra y archivo de texto/commit revisado. Dejar un campo vacío significa
pendiente; `null` significa evento ausente o no observable, con motivo en notas.
La duda se escribe: no es obligatorio forzar clase ni inventar una marca para
poder entregar. Una duda sin resolver impide exportar ese caso como revisado.

```text
Revisor (identificador):
Fecha absoluta:
Versión/lista de muestra acordada:
Commit y versión de los textos:
Exposición previa a JSON, respuestas, auditorías o resultados (cuáles):

Caso:
Clase propuesta (vishing / legitima / duda sin resolver):
Sustento en el diálogo y límite para inferir identidad:
Primer pedido riesgoso: línea o null; fragmento y motivo:
Primer cumplimiento observable: línea o null; fragmento y motivo:
Pedido REQUEST_* si corresponde (ver manual):
Evidencia seleccionada (repetir): línea / fragmento / evento / etiquetas opcionales:
Ambigüedades y alternativas de marca/clase:
Tiempo empleado y problemas para usar la ficha:
```

Numerar desde 1 las líneas del `.txt`; A/B solo identifican hablantes. Aplicar
el manual y el [formato vigente](casos/README.md#formato-de-referenciaidjson),
sin convertir líneas a segundos. No registrar `T_A`: lo produce el detector.
Si el catálogo aporta contexto que el diálogo no permite inferir, distinguir
ambas fuentes. Las etiquetas parciales no prueban ausencia en el resto del texto.

Para Tito, agregar a las dudas los fragmentos cuyo sentido cambia al ver el turno
siguiente: registrar qué líneas de soporte ya eran visibles en el prefijo y qué
información apareció después. No hace falta anotar exhaustivamente cada turno.
La clase final no se copia como etiqueta de todos los prefijos. La función
`etiquetar_prefijo()` deriva estados de evidencia (`pedido_visible`, etc.);
no establece por sí sola la etiqueta objetivo de derivación. Su interpretación
para entrenar, y cómo tratar pedidos legítimos, negaciones y evidencia parcial,
requiere acuerdo local D07/D08 antes de #99.

### Comparación, adjudicación y conexión técnica

> **Estado: propuesta sin discutir.** Registrar la comparación local con el esquema
> siguiente, pendiente de herramienta y medidas de acuerdo de
> [D07](../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico).

1. Recibir los cuatro originales antes de mostrar respuestas ajenas o JSON.
   Conservar cada entrega y su huella; cualquier corrección posterior es otra
   versión. Registrar exposición previa y faltantes. No completar por una persona
   las respuestas de otra ni considerar un faltante como acuerdo.
2. Antes de adjudicar, comparar por caso clase, presencia de pedido/cumplimiento
   y línea elegida cuando ambos observan el evento. Proponer informar conteos y
   denominadores de acuerdo/desacuerdo y diferencias de líneas, sin un umbral
   inventado ni exigir Kappa sobre etiquetas parciales. Medida definitiva pendiente.
3. Para cada discrepancia conservar: `id`, `case_id`, campo, valores de cada
   original, fragmentos que los sustentan, resolución o pendiente, motivo,
   participantes reales y fecha. Incluso sin discrepancias, registrar que hubo
   comparación. No resolver automáticamente por mayoría ni por coincidencia con
   el JSON. Si no se resuelve, dejar el caso bloqueado o excluirlo con motivo
   acordado; un fallo del modelo no es motivo de exclusión.
4. Proponer guardar la comparación y referencia adjudicada como
   `ADJUDICACION-TITO-AAAA-MM-DD.md` en `casos/`, con rutas/huellas de originales,
   valores finales y exclusiones, después de que exista. Conservar texto y JSON
   históricos; no reemplazarlos ni cambiar solo `revision_humana` a `true`.
   Preparar desde el registro adjudicado los objetos `Referencia` que consume la
   API, con trazabilidad de cuál versión se exportó.
5. Con revisión y acuerdos reales, cargar `Conversacion`/`Referencia` y declarar
   particiones por API. `datos_tito.py` no tiene CLI ni carga automática de estas
   fichas ni integración automática con el runner. Sus funciones disponibles son
   `validar_particiones`, `generar_manifiesto`, `cobertura_muestra`,
   `informe_validacion` y `puede_habilitarse`; los ejemplos ejecutables están en
   [tests/test_datos_tito.py](tests/test_datos_tito.py). Las categorías de cobertura
   son metadatos aportados, no inferidas por el programa. El validador usa la
   familia de variantes, semillas, pares y grupos semánticos declarados; no
   descubre parentescos que nadie registró.
6. Registrar acuerdo efectivo de `composicion`, `tamano`, `reglas_referencia` y
   `proporciones`, con fecha/participantes y enlace al acuerdo de #96/#32/#55.
   Aportar `revisores`, `originales_conservados`, `originales_referencia`,
   `desacuerdos`, `adjudicaciones`, `referencias_revisadas` a la puerta de
   habilitación, cruzados con el manifiesto. La puerta verifica estructura y
   conteos; no prueba que cuatro personas anotaron independientemente. Otra
   persona debe comprobar originales y separación, además del resultado técnico.

### Acuerdo que falta para comenzar

Antes de anotar: confirmar o reemplazar los 12 IDs, identificar a los cuatro
integrantes que entregarán originales, acordar herramienta/custodia y tratamiento
de exposición previa. Esto habilita la calibración humana de esa lista, sin fijar
particiones ni habilitar experimentos. Para completar #96 faltará además acordar
revisión del resto, supervisión de prefijos, procedencia y grupos, composición,
tamaño y proporciones de los conjuntos experimentales. No hay valores adoptados.

La secuencia vigente es [#96](https://github.com/Corchets/bitacora_tesis/issues/96)
→ [#98](https://github.com/Corchets/bitacora_tesis/issues/98)
→ [#99](https://github.com/Corchets/bitacora_tesis/issues/99)
→ [#100](https://github.com/Corchets/bitacora_tesis/issues/100).
El diagnóstico no abre la evaluación independiente posterior; la selección y
la decisión de fine-tuning usan entrenamiento/validación. La reserva final del
proyecto permanece fuera de este procedimiento.
