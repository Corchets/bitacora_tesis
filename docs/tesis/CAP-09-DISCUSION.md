> **Estado: borrador del 2026-11-20, propuesta de redacción sin discutir.** Responde las preguntas con la evaluación final del 2026-11-19 ([§8.3.4](CAP-08-RESULTADOS-EXPERIMENTALES.md#834-evaluación-final)). La lectura es de quien redactó: falta revisarla entre los cuatro.

# Capítulo 9: Discusión

## 9.1. Respuesta a las preguntas de investigación

**PI1, detección incremental.** Respuesta provisional: en desarrollo, usando solo lo disponible hasta cada línea, la configuración del ADR 0001 avisó en 10/10 estafas con 0/10 falsas alarmas en #101. La del [ADR 0002](../ingenieria/adr/0002-detector-gemma4-e2b-solo-con-prompt-c-premisa.md), en los 140 casos de desarrollo dentro del alcance, avisó 40 de 46 estafas con 26 falsas alarmas en 94 legítimas ([H10](../hallazgos/H10-c-avisa-antes-del-pedido.md)). La familia de modelos muestra que el contexto y el modelo importan más que la política: los mismos 10 modelos dan 48/100 falsas alarmas en directo y 27/100 con Tito viejo, a cambio de bajar de 90/100 a 82/100 estafas. Esa baja no es toda mérito del filtro: de las 24 falsas alarmas que desaparecen, 13 estaban en llamadas sin nada sensible antes del aviso, 6 en líneas sensibles que Tito no vio, y en 5 Tito ya había activado ([H08](../hallazgos/H08-tito-evita-falsas-alarmas-por-punto-ciego.md)).

**Con la evaluación final,** la respuesta es afirmativa, con una reserva. Usando solo lo dicho hasta cada turno, la configuración final ([ADR 0008](../ingenieria/adr/0008-prompt-del-detector-c-consejos.md)) avisó 73 de 100 estafas generadas que no habían intervenido en ninguna elección [64–81 %] y las 33 estafas reales coreanas, con 15 falsas alarmas en 56 legítimas generadas [17–40 %]. La reserva es la especificidad en llamadas reales: avisó en 21 de 33 llamadas legítimas de call center [47–78 %], y cambiar el prompt no lo corrige ([H12](../hallazgos/H12-cambiar-el-prompt-mueve-el-corte-no-la-separacion.md)). Tampoco detecta más que la línea base: las reglas léxicas avisan 87 de 100 estafas, pero también 48 de 56 legítimas. Lo que aporta el modelo es no avisar en todo.

**PI2, margen temporal.** Respuesta provisional y **poco favorable**: con voz real y la opción B, el aviso suele llegar después de empezado el pedido, entre 3 y 5 s. Eso no invalida el aviso, porque el daño ocurre cuando la persona cumple, pero deja poco margen. Con 3,74 s de consulta, la demora del modelo es una parte importante de esa diferencia.

**Con la evaluación final,** sobre texto y en líneas: el aviso llegó antes de la línea del pedido en 37 de las 80 estafas con pedido, a más tardar en esa línea en 53, y antes del cumplimiento en 24 de 32. Lo que lo adelanta es preguntar por la intención: el prompt de pedidos avisó antes en 15 de 80 ([H10](../hallazgos/H10-c-avisa-antes-del-pedido.md)). En segundos no hay respuesta con la configuración final. No se midieron `L_R` ni `L_C`, las marcas no tienen revisión humana, y en el teléfono cada consulta tarda unos 3,6 s ([§8.6](CAP-08-RESULTADOS-EXPERIMENTALES.md#86-rendimiento-y-límites-del-hardware)): una línea de ventaja no garantiza segundos de ventaja.

**E1, efecto del ASR.** Quedó fuera ([#54](https://github.com/Corchets/bitacora_tesis/issues/54)). Se sabe que el ASR pierde términos críticos y que en las 9 llamadas con voz real el detector igual avisó en todas las estafas y en ninguna legítima, pero no se pasó el mismo detector por el texto del guion.

**E2, explicación.** Sin revisión sistemática. El caso de D1, donde el aviso cita el débito y no el pedido, muestra por qué hay que revisar la cita y no solo el instante. En la evaluación final se leyeron, sin protocolo, los motivos de los 21 avisos en legítimas reales: se reparten entre pedidos de código o datos, ventas leídas como estafa y motivos genéricos ([§8.5](CAP-08-RESULTADOS-EXPERIMENTALES.md#85-falsas-alarmas-y-negativos-difíciles)).

## 9.2. Interpretación y comparación con antecedentes

- **El TTS engaña.** Zipformer parecía excelente con TTS y fue malo con voz real. Coincide con la advertencia de Traister et al. (2026) sobre datos sintéticos, y por eso los resultados sobre corpus de redacción asistida se leen con cautela.
- **Reglas frente a modelos.** Las reglas no distinguen mencionar de pedir, lo que explica el 58,3 % de falsas alarmas y coincide con la caída ante negativos difíciles de Sim y Kim (2025). En la evaluación final avisaron más estafas que el modelo (87 contra 73 de 100) y avisaron en 48 de las 56 legítimas.
- **Afinar sobre pocos casos no generaliza.** El prompt `v2` mejoró sobre los 53 antecedentes y empeoró sobre corpus v2. Es el motivo para congelar antes del test.
- **WER y términos críticos.** La opción con peor WER recuperó más términos críticos, lo que concuerda con Balagopalan et al. (2019): el WER agregado no alcanza.
- **Falsas alarmas y prevalencia.** Con Axelsson (2000) y Williams (2021), ni un 0/10 en un corpus balanceado dice cuántos avisos falsos vería una persona en su uso cotidiano.
- **Una compuerta no es un clasificador.** Tito se entrenó para distinguir estafas de legítimas. Por eso no despierta al modelo con lo sensible de las legítimas: cuando aparece la primera línea sensible, el SLM ya está despierto en 62 de 64 estafas, pero solo en 14 de 43 legítimas. La baja de falsas alarmas que se le atribuía era un punto ciego ([H08](../hallazgos/H08-tito-evita-falsas-alarmas-por-punto-ciego.md), [H09](../hallazgos/H09-tito-clasificador-en-vez-de-compuerta.md)). Una compuerta se mide por cuánto de lo sensible deja pasar, no por las alarmas que evita.
- **Lo elegido en desarrollo se sostuvo en lo que desarrollo medía.** El aviso a tiempo fue del 66 % en el test contra el 72 % en desarrollo, y las falsas alarmas, del 27 % contra el 21 %. No se sostuvo lo que desarrollo no tenía: llamadas reales.
- **Las estafas generadas son más directas que las reales.** Tienen unos 10 turnos de quien llama y el pedido llega enseguida. Las coreanas tienen 113 líneas de mediana y el pedido llega en la 57. En las generadas el modelo rara vez pasa de 0,3; en las coreanas escribe 0,7 o más en un tercio de las consultas. Cuando el aviso caía en la línea del pedido ([H03](../hallazgos/H03-el-slm-avisa-en-el-pedido.md)) había dos explicaciones: que el modelo solo reaccionara al pedido, o que el corpus no tuviera nada que detectar antes. Pesaban las dos. El prompt de intención adelantó el aviso ([H10](../hallazgos/H10-c-avisa-antes-del-pedido.md)), y las llamadas reales dan mucho más recorrido previo. Las coreanas están traducidas y son de otro país: no dicen cómo es una estafa real de acá.
- **Las legítimas generadas también son más fáciles que las reales.** El detector avisa en el 27 % de las generadas y en el 64 % de las reales de call center. Una venta telefónica real tiene la forma del disfraz: una empresa que llama, ofrece algo y confirma datos. Es la misma advertencia de Traister et al. (2026), ahora del lado de las legítimas.
- **Cambiar el prompt mueve cuánto avisa el detector, no a quién.** Siete prompts, cinco escritos desde cero, no bajaron las falsas alarmas en llamadas reales sin perder estafas, y uno más corto no avisó mejor ([H12](../hallazgos/H12-cambiar-el-prompt-mueve-el-corte-no-la-separacion.md)). Lo que queda es ajustar el modelo o cambiar cómo se presenta el aviso.
- **Repetir mueve casos.** La misma configuración dio 73 y 76 estafas avisadas de 100 en dos pasadas ([H13](../hallazgos/H13-la-misma-configuracion-corrida-de-otro-modo.md)). Dos configuraciones se comparan en la misma sesión y del mismo modo, y una diferencia de 3 casos no se le atribuye a la configuración.

## 9.3. Análisis de errores

Errores conocidos. Los de la evaluación final van por categoría, porque no se leyeron los textos del test:

| Componente | Error | Efecto observado |
|---|---|---|
| ASR | «toque» por «token»; «CBB» o «CBO» por «CVV» y «CBU» | Pierde etiquetas; no cambió avisos en estas llamadas |
| ASR | Inglés o portugués en 4 de 129 frases | Ruido en el contexto |
| Tito viejo | Deriva legítimas inocuas, como «¿Tenés la notebook gris?» | Solo más consultas: el modelo las descartó en #101 |
| Tito viejo | No despierta al modelo con lo sensible: «Me llegó por SMS un código para activar WhatsApp» saca 0,234 y «El DNI completo y una foto del frente», 0,024 | Pierde `CV2-D-V-PREMIO-001`, atrasa el aviso de `CV2-D-V-BANCO-007` y produce una baja engañosa de falsas alarmas ([H08](../hallazgos/H08-tito-evita-falsas-alarmas-por-punto-ciego.md)) |
| Detector | Aviso por el débito, antes del pedido del código | Aviso correcto por un motivo distinto del esperado |
| Detector | Estafas sin pedido: avisa 10 de 20 en el test | Quedan a un escalón: 26 de las 27 estafas sin aviso tienen 0,2 de riesgo máximo |
| Detector | Por familia, en el test: banco 24/25; soporte 11/20, WhatsApp 9/15 y premio 9/15 | Fuera de banco y previsional pierde cerca de la mitad |
| Detector | Llamadas legítimas «del banco»: avisan 5 de 7 en el test | Un tercio de las falsas alarmas en legítimas generadas |
| Detector | Llamadas reales de call center: verificación con un código o con datos, venta con apuro | Avisa en 21 de 33, y no se corrige con el prompt ([H12](../hallazgos/H12-cambiar-el-prompt-mueve-el-corte-no-la-separacion.md)) |
| Detector | El contexto de 4.096 tokens se llena entre las líneas 70 y 130 de una llamada larga | Deja de mirar más de la mitad de los turnos de las coreanas (2.359 de 4.193) y de ahí en más no avisa. No cambió el resultado porque avisa antes, pero una estafa que pida algo después de ese punto quedaría sin aviso |
| Sistema | Corte de llamada que descartaba la última consulta | Corregido (`7e6b971`) |

## 9.4. Amenazas a la validez

**Interna.**
- La configuración se eligió con los mismos 20 casos que la evalúan en #101.
- La inferencia en GPU no es exactamente repetible: la misma configuración dio 73 y 76 estafas avisadas de 100 en dos pasadas ([H13](../hallazgos/H13-la-misma-configuracion-corrida-de-otro-modo.md)).
- El prompt final lo eligió Mateo Antenucci por fuera de la regla escrita, mirando desarrollo ([ADR 0008](../ingenieria/adr/0008-prompt-del-detector-c-consejos.md)). El test no intervino en ninguna elección y corrió una sola vez.
- La exploración posterior comparó prompts sobre los conjuntos reales. Las cifras de esos conjuntos en la evaluación final son anteriores.
- #101 corrió con cambios sin commit en la carpeta.
- Los 200 casos reservados son públicos en GitHub desde el 2026-10-23, aunque no se usaron en ninguna corrida versionada. Un modelo publicado después pudo haberse entrenado con ellos, pero Gemma 4 E2B salió el 2026-03-31 ([registro de versiones de Google](https://ai.google.dev/gemma/docs/releases?hl=en)), antes de esa fecha.

**De constructo.**
- `T_R` y `T_C` son marcas provisionales, sin revisión humana (D07 abierta).
- `T_C` es un cumplimiento actuado: permite medir márgenes de ingeniería, no que una persona habría evitado el daño.
- Los márgenes con voz real usan un pedido ubicado por palabras clave.
- En las legítimas reales, los roles y el tipo de llamada los infirió un modelo.
- Las cifras de detección suponen turnos perfectos. En vivo los turnos se arman con umbrales provisorios, que no se calibraron con grabaciones ([ADR 0007](../ingenieria/adr/0007-consulta-al-cerrar-cada-turno-de-otra.md)).

**Externa.**
- El corpus es simulado y de redacción asistida, y las llamadas tienen 4 guiones y 2 voces.
- Los dos conjuntos reales tienen 33 llamadas cada uno, son de Corea y de Estados Unidos y están traducidos. No hay estafas reales argentinas.
- Las cifras de detección salen de Colab. En los teléfonos se midieron la latencia y la memoria, no la detección, y ahí el cálculo no es idéntico ([H11](../hallazgos/H11-el-riesgo-cambia-con-el-runtime.md)). Entre el iPhone y el A56, con el mismo prompt, el riesgo cambió en 12 de 83 líneas, sin mover el primer aviso de ninguna conversación ([medición](../../experiments/slm-directo/corridas/2026-11-20_iphone-15-pro-max-latencia/README.md)). Desde el 2026-11-21, además, en el teléfono el modelo genera solo el número del riesgo ([ADR 0009](../ingenieria/adr/0009-en-el-telefono-el-modelo-genera-solo-el-numero.md)), y la evaluación final corrió con la salida de 14 tokens. En 150 conversaciones de desarrollo, en la Mac, ese cambio no movió ningún aviso; en el test no se probó.
- Las métricas de detección salen de conversaciones escritas, no de audio transcripto. El ASR se midió aparte, con voz real y ruido de fondo. En el iPhone corrieron a la vez, pero el detector leyó el texto original y no la transcripción.
- Meet entrega un audio más limpio que una llamada celular en la calle.
- Las llamadas generadas son cortas, de unos 10 turnos de quien llama, y no ejercitan el límite del contexto. En una llamada real larga el detector deja de mirar después de unos 55 turnos (§9.3).
- No se puede prometer rendimiento para adultos mayores ni para Argentina en general.

**De conclusión.** Con 20 casos, los intervalos son muy anchos: 10/10 es compatible con 72 %, y 0/10 con 28 % de falsas alarmas, ya por encima de la meta. En la evaluación final los intervalos siguen siendo anchos: el 73 % de estafas avisadas es compatible con 64 a 81 %, y el 64 % de falsas alarmas en llamadas reales, con 47 a 78 %.

## 9.5. Implicaciones de ingeniería, éticas y de uso

- **Ingeniería.** En la notebook y en el A56, E2B no cumple el presupuesto de latencia ni el de memoria de la prefactibilidad. El camino para bajar la demora fue la caché de prefijo y pedir menos texto, no un modelo mayor: con la salida cortada después del riesgo, en un A56 tarda 3,6 s por turno, y mostrar el aviso sin esperar el motivo baja el primero de 13,8 s a 3,7 s ([#172](https://github.com/Corchets/bitacora_tesis/issues/172)). En un iPhone 15 Pro Max con GPU, la configuración final tarda 0,8 s por turno, dentro del presupuesto de latencia, y 0,5 s si el modelo genera solo el número ([medición](../../experiments/slm-directo/corridas/2026-11-21_solo-el-numero/README.md)); el ASR corre a la vez sin demorarla ([§8.6](CAP-08-RESULTADOS-EXPERIMENTALES.md#86-rendimiento-y-límites-del-hardware)). Es una pasada, con audio sintético.
- **Producto.** En Android no se puede capturar una llamada común, y en iOS una app tampoco tiene una interfaz para el audio de una llamada. El prototipo muestra el análisis en una llamada por Meet, no una protección universal.
- **Ética.** Una falsa alarma en una llamada legítima también tiene costo, y un detector no verifica identidades: el aviso debe sugerir verificar, no afirmar fraude. Con dos de cada tres llamadas comerciales reales avisadas, no puede presentarse como una alarma. La [política de producto](../../experiments/slm-directo/corridas/2026-11-10_revision-producto/POLITICA.md) ya trata como tolerable el aviso que coincide con un consejo oficial, aunque la llamada sea legítima.
- **Datos.** El audio perdido muestra que el resguardo de voces requiere un procedimiento explícito.
