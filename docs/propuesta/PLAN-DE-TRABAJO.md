# Plan de Trabajo v1

## Portada provisional

**Universidad del Norte Santo Tomás de Aquino**  
**Facultad de Ingeniería**  
**Ingeniería en Informática — Plan 2008**  
**Proyecto Final Integrador**

### Detección incremental y explicable de vishing en conversaciones de voz en español

**Integrantes**

- Albarracín Ignacio.
- Antenucci Mateo.
- Grosso Luciano.
- Villalobo Evaristo.

**Tutor:** Ing. Ernesto Rico  
**Año:** 2026

> La versión final debe respetar los [requisitos académicos](REQUISITOS-ACADEMICOS.md).

## 1. Resumen de la propuesta

El vishing es una modalidad de ingeniería social realizada mediante llamadas de voz en la que un atacante intenta obtener información sensible, inducir una transferencia o provocar otra acción riesgosa. Las defensas basadas únicamente en la reputación del número no pueden reconocer necesariamente llamadas originadas desde números todavía no reportados ni explicar la maniobra que ocurre durante la
conversación.

El proyecto propone diseñar, implementar y evaluar un prototipo que procese incrementalmente un flujo de audio en español, transcriba localmente la conversación, estime el riesgo de vishing e identifique señales como suplantación, urgencia, aislamiento y pedidos de códigos, secretos o transferencias. Cuando el riesgo supere una política definida, el sistema mostrará una advertencia contextual y accionable.

La evaluación se realizará sobre un corpus controlado de conversaciones simuladas
de vishing y llamadas legítimas difíciles. Se compararán reglas solas con los
detectores candidatos y su acumulación temporal de evidencia. Además de las
métricas de clasificación, se medirá la falsa alarma, el efecto de los errores del
reconocimiento de voz, la latencia y el tiempo de anticipación respecto de una
acción crítica. El núcleo experimental utilizará reproducción en streaming; la llamada
VoIP controlada es la integración objetivo del prototipo, sujeta a una prueba de
factibilidad. La captura por altavoz quedó despriorizada por su mezcla de canales.

## 2. Problema

Un número puede parecer normal y el peligro solo hacerse visible en el contenido y la evolución de la conversación. El problema de ingeniería es detectar evidencia suficiente de manipulación y de una
solicitud riesgosa mientras la llamada todavía está en curso, con una tasa de falsa
alarma aceptable y una advertencia que permita actuar antes de compartir información
o realizar una operación.

Las modalidades y sus fuentes están en el [catálogo de escenarios](../corpus/CATALOGO-ESCENARIOS.csv).

### Formulación en cinco líneas

1. **Usuario:** una persona en Argentina que conversa por teléfono con alguien que dice llamar de su
   banco, de un organismo como ANSES, de una mesa de soporte o de parte de un familiar.
2. **Contexto:** el prototipo analiza lo dicho durante la llamada y su evolución.
   Una mención de un código, una urgencia o un pedido de dinero necesita contexto;
   también puede aparecer en una conversación legítima.
3. **Decisión bajo presión:** en pocos minutos y sin poder verificar al interlocutor, tiene que
   decidir si dicta un código o una clave, transfiere dinero o comparte la pantalla.
4. **Daño evitado:** que esa acción ocurra, y con ella la toma de la cuenta o la pérdida de dinero.
   Por eso la advertencia sirve solo si llega antes de que la persona cumpla el pedido, no después.
5. **Límite de las defensas existentes:** la reputación del número no ve la conversación; las
   recomendaciones de BCRA y ANSES dependen de que la persona las recuerde en el momento de presión.

## 3. Objetivo general

Diseñar, implementar y evaluar un prototipo capaz de analizar incrementalmente un
flujo de audio de una conversación de voz en español, mediante inferencia local,
para estimar el riesgo de vishing, identificar maniobras de ingeniería social y
emitir una advertencia contextual antes de una acción crítica, cuantificando su
desempeño, falsas alarmas, latencia y margen temporal de intervención.

## 4. Objetivos específicos

1. Relevar el estado del arte, las modalidades relevantes de vishing y las
   restricciones técnicas, éticas y legales del problema.
2. Definir una taxonomía operacional de maniobras y solicitudes riesgosas.
3. Construir un corpus controlado y documentado de conversaciones simuladas de
   vishing y llamadas legítimas en español.
4. Comparar alternativas de reconocimiento de voz local sobre audio representativo.
5. Evaluar reglas solas como línea base para comparar los detectores candidatos.
6. Desarrollar un detector incremental que acumule evidencia a lo largo del tiempo.
7. Diseñar advertencias explicables derivadas de las señales detectadas.
8. Integrar la cadena audio→ASR→detección→advertencia en un entorno controlado.
9. Evaluar clasificación, falsas alarmas, robustez al ASR, anticipación, latencia y
   consumo de recursos.
10. Documentar arquitectura, decisiones, implementación, pruebas, resultados,
    limitaciones y oportunidades de trabajo futuro.

## 5. Preguntas de investigación

- **PI1:** ¿con qué desempeño puede detectarse vishing usando solo la parte de la
  conversación disponible hasta un instante dado?
- **PI2:** ¿con cuánto margen respecto del primer pedido riesgoso y de la primera
  acción de cumplimiento puede emitirse una alerta estable?

Como evaluación diagnóstica se comparará el detector con transcripción manual y
ASR local. La explicación de maniobras será un objetivo secundario. No se presentan
como preguntas centrales independientes.

Las definiciones operativas y métricas están en
[PREGUNTAS-DE-INVESTIGACION.md](../investigacion/PREGUNTAS-DE-INVESTIGACION.md).

## 6. Alcance

### Núcleo obligatorio

- Español, priorizando variedad argentina sin afirmar representatividad nacional.
- Público sin foco etario específico. La composición del corpus limita las
  conclusiones; no se promete rendimiento para todos los públicos.
- Corpus de llamadas simuladas/representadas y llamadas legítimas difíciles.
- Transcripción local del audio.
- Detector sobre texto, conservando contexto de la llamada actual. La representación
  y la ventana de contexto se elegirán mediante pruebas.
- Maniobras de ingeniería social y solicitudes de alto riesgo.
- Evento crítico y medición de anticipación.
- Advertencia explicable.
- Reproducción de audio como streaming reproducible.
- Prototipo o demo en entorno controlado.

### Extensiones condicionadas al avance

- Llamada VoIP integrada en la aplicación.
- Cuantización avanzada y comparación de dispositivos.
- Prueba de comprensión de warnings con voluntarios.
- Evaluación adversarial o fuera de distribución.

### Fuera de alcance

- Captura universal de llamadas PSTN desde una app Android ordinaria.
- Identificación biométrica o detección de voces clonadas/deepfake.
- Agenda, historial de llamadas, memoria entre sesiones, reputación de números y
  detección de spoofing. La dirección entrante/saliente tampoco será una entrada del detector.
- Rasgos acústicos para detectar fraude, como tono o estrés vocal. El audio se usa
  para transcribir y medir tiempos y calidad del ASR.
- App iOS, múltiples idiomas, análisis de mensajes de SMS/WhatsApp y detección de malware.
- Backend de producción o publicación comercial en Play Store.
- Estudio poblacional representativo con víctimas reales.

El contenido de la llamada permite evaluar señales de riesgo, pero no verificar la
identidad del interlocutor. Si dos llamadas tienen el mismo contenido observable,
el detector dispone de la misma evidencia aunque una sea legítima y la otra no.
Este límite debe aparecer en los casos de evaluación y en las conclusiones.

## 7. Alternativas para obtener el audio

1. reproducción de grabaciones como stream;
2. llamada en altavoz capturada por un micrófono externo;
3. llamada VoIP controlada cuyo audio pertenece a la aplicación;
4. integración privilegiada con telefonía mediante OEM/AOSP/root.

Se aprobó **replay como base experimental reproducible** y **VoIP controlada como integración objetivo**, condicionada a la factibilidad del prototipo. El altavoz externo
quedó despriorizado; la captura universal PSTN permanece fuera de alcance. La comparación
y su decisión posterior están en
[ALTERNATIVAS-CAPTURA-AUDIO.md](../ingenieria/ALTERNATIVAS-CAPTURA-AUDIO.md)
y en la [minuta del 2026-09-09](../gestion/seguimientos/2026-09-09.md).

## 8. Recorrido del desarrollo

> **Estado: propuesta sin discutir.** Orden de hitos para revisar con el equipo.
> Las reglas de anotación, el protocolo y los modelos siguen abiertos en
> [D07, D08 y D09](../gestion/MAPA-DECISIONES.md#decisiones-precisas-de-alcance-y-experimentación).

| Hito | Resultado que habilita el siguiente paso | Dependencia |
|---|---|---|
| **[H1](https://github.com/Corchets/bitacora_tesis/milestone/2) — Acuerdo mínimo** | Alcance y preguntas claros; un ejemplo contrastante trabajado; reglas iniciales de anotación y entradas/salidas conceptuales acordadas; primeras tareas listas para ejecutar. | Revisión del Plan, corpus, anotación, métricas y arquitectura. |
| **[H2](https://github.com/Corchets/bitacora_tesis/milestone/3) — Piloto del corpus y primeras pruebas** | Piloto con audio, texto revisado y referencia humana; desacuerdos y costo conocidos. Primer detector con reglas sobre texto incremental y prueba de ASR local con errores, tiempos y recursos registrados. | H1. Los primeros textos habilitan el detector; las primeras grabaciones habilitan ASR. No hace falta esperar a completar el piloto para empezar esas pruebas. |
| **[H3](https://github.com/Corchets/bitacora_tesis/milestone/4) — Primera integración medible** | Un replay recorre audio→ASR→reglas→aviso. Otra persona puede repetirlo y comparar alertas con la referencia humana, sin confundir sus marcas. | Primeros casos revisados, detector sobre texto y ASR ejecutable de H2; puede comenzar antes de completar el piloto. |
| **[H4](https://github.com/Corchets/bitacora_tesis/milestone/5) — Desarrollo, comparación y selección del detector** | Candidatos implementados o adaptados y, si corresponde, entrenados. Comparación sobre desarrollo, revisión del contexto y política de alerta, análisis del efecto del ASR y selección por calidad, falsas alarmas y costo. | Primeras exploraciones pueden comenzar en H2. La selección requiere el piloto revisado y una integración medible; alimenta D08 y D09. |
| **[H5](https://github.com/Corchets/bitacora_tesis/milestone/6) — Evaluación final** | Corpus y particiones versionados; protocolo, configuración y test reservados antes de medir. Resultados reproducibles responden PI1, PI2 y E1 e incluyen errores y límites. | H4 y cierre de las decisiones necesarias para interpretar la evaluación. |
| **[H6](https://github.com/Corchets/bitacora_tesis/milestone/7) — Entrega y defensa** | Informe coherente con los resultados, paquete reproducible, presentación, demo y video de respaldo revisados. | H5; redacción y bibliografía acompañan los hitos anteriores. |

Los hitos definen resultados, no una arquitectura obligatoria. El laboratorio
existente se evalúa cuando una tarea necesita esa función: se puede reutilizar,
adaptar o reemplazar. Entrenar un modelo, usar una cascada o desarrollar una UI
completa requieren justificar su aporte a la comparación. No son condiciones para
obtener la primera ejecución medible.

**H1 termina cuando** se puede recorrer un ejemplo escrito fraudulento y uno legítimo
desde su preparación hasta la referencia que se anotaría, distinguir esa referencia
de la salida esperada del detector y explicar el flujo conceptual. Es un recorrido
ilustrativo; las grabaciones y las mediciones reales pertenecen a los hitos posteriores.
Además, los issues del arranque deben
tener resultado observable, dependencias y criterio de revisión. La elección de
modelos y la política final de alerta se resuelven con las pruebas posteriores.

“Piloto” se refiere al corpus y a su procedimiento de producción y anotación.
El detector tiene primeras versiones que se prueban con esos datos. Su desarrollo
atraviesa H2, H3 y H4; no se reduce a ejecutar modelos ya hechos.

Corpus, detector y ASR avanzan con intercambios pequeños: primero textos para probar
la detección con contexto; después las grabaciones permiten medir el ASR e integrar
audio y tiempos. El ASR se incorpora mediante motores existentes, cuya calidad y
costo se prueban. La arquitectura se detalla al implementar y se revisa cuando las
pruebas muestran qué interfaces o componentes conviene cambiar.

Antes de ampliar el corpus se acuerda cómo separar semillas y variantes entre
desarrollo y test. El piloto sirve para ajustar el método; no se presenta como test
final. La evaluación con transcripción manual y ASR, las marcas y las métricas se
rigen por sus documentos, sin repetir aquí sus fórmulas.

## 9. Arquitectura conceptual

```text
Fuente de audio permitida
          ↓
VAD / segmentación / ventanas
          ↓
ASR local con texto parcial y timestamps
          ↓
Estado de conversación
          ↓
Detector de riesgo + evidencia explicativa
          ↓
Política de alerta (pendiente de evaluación)
          ↓
Advertencia: qué ocurre + por qué importa + qué hacer
```

El motor y la interfaz se mantienen separados para poder desarrollar y evaluar en
computadora. La integración móvil se considera según la evidencia de factibilidad.

## 10. Entregables

| Entregable                     | Qué permite comprobar                                                                                                                                                                                                                                                                                 |
| ------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Prototipo local ejecutable** | Una grabación reproducida como stream recorre audio→ASR→detector→alerta; se observan transcripción, motivo y momento de cada aviso. Incluye instrucciones de ejecución y pruebas de los comportamientos críticos.                                                                                     |
| **Corpus controlado**          | Conversaciones simuladas fraudulentas y legítimas difíciles, con transcripciones, anotaciones y separación de datos para desarrollo y evaluación. Audio y datos identificables permanecen fuera de Git; el repositorio conserva método y metadatos disociados.                                        |
| **Experimentos reproducibles** | Comparación de reglas solas y detectores candidatos, texto manual frente a ASR y detección por turno frente a acumulación temporal. Cada corrida registra datos/split, configuración, seed, versión de código, hardware, salidas y análisis de errores; permite regenerar métricas, tablas y figuras. |
| **Informe Final digital**      | Problema, antecedentes con fuentes verificadas, requisitos, arquitectura, método, resultados y límites; resúmenes español/inglés y anexos según los [requisitos académicos](REQUISITOS-ACADEMICOS.md).                                                                                                |
| **Defensa y demostración**     | Presentación que explica el aporte y los resultados, demo repetible y video de respaldo.                                                                                                                                                                                                              |

El Plan de Trabajo y la documentación técnica guían estos entregables. Cada contenido
se mantiene en su fuente de verdad y se incorpora al informe cuando corresponde.

## 11. Cronograma

> **Estado: propuesta sin discutir.** Calendario de referencia desde el lunes
> 2026-10-05. Se revisa con el equipo según disponibilidad y evidencia; no supone
> que el laboratorio existente ya cumple los hitos.

El acuerdo mínimo de H1 debe permitir el arranque. No hace falta cerrar de antemano
todas las decisiones de modelos y evaluación final.

| Fechas                  | Resultado verificable esperado                                                                                                                                                 |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 2026-10-05 a 2026-10-11 | H2: probar el procedimiento con un par de casos contrastantes; producir texto, audio y referencia humana. En paralelo, probar un primer detector con reglas sobre texto incremental y ASR local sobre las grabaciones. |
| 2026-10-12 a 2026-10-18 | Completar y revisar el piloto de H2. H3: obtener el primer replay completo con reglas, aviso y tiempos verificables por otra persona. Acordar separación de datos antes de ampliar. |
| 2026-10-19 a 2026-10-25 | H4: comparar reglas y pocos candidatos sobre desarrollo; probar contexto y revisar errores con texto manual y ASR. Decidir qué alternativas merecen continuar. |
| 2026-10-26 a 2026-11-08 | Continuar H4: corregir y comparar candidatos; completar los datos necesarios según cobertura y costo del piloto. Elegir configuración y cerrar el protocolo para H5; reservar test y verificar reproducción antes de medirlo. |
| 2026-11-09 a 2026-11-22 | Ejecutar la evaluación final sobre el test reservado; generar tablas y figuras, analizar errores y responder PI1 y PI2 sin ajustar el detector mirando ese test.               |
| 2026-11-23 a 2026-11-30 | Completar y revisar el informe, verificar reproducción de resultados, preparar presentación, demo y video de respaldo.                                                         |
| **2026-12-01**          | **Objetivo de cierre interno: informe, código, resultados y presentación disponibles para revisión.**                                                                          |
| Desde 2026-12-02        | Correcciones del tutor y ensayo de defensa; fecha exacta de entrega y defensa pendiente de confirmación.                                                                       |

El informe se escribe junto a cada resultado desde 2026-10-05. Cada semana se revisa
el avance mostrando una corrida, datos anotados o resultados verificables; se puede
adelantar trabajo si sus dependencias están resueltas. Si hay atraso, se replanifica
y se postergan primero las [extensiones](#extensiones-condicionadas-al-avance).
Se reservan dos semanas para evaluación final. El **2026-12-01** es una referencia
interna, y la defensa prevista para fines de diciembre surge de la
[minuta del 2026-09-09](../gestion/seguimientos/2026-09-09.md).

## 12. Organización del equipo

> **Estado: propuesta sin discutir.** Distribución operativa para revisar con los
> cuatro integrantes; acompaña el cronograma y las decisiones pendientes de
> [corpus, evaluación y modelos](../gestion/MAPA-DECISIONES.md).

El equipo elige pocas tareas según el resultado del hito actual y las publica como
GitHub Issues. Cada tarea tiene una persona responsable y una revisora distinta
cuando afecta datos, métricas, arquitectura o conclusiones del informe.

| Momento                               | Organización sugerida                                                                                                                      |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| Arranque: corpus y primeras pruebas | Una pareja prepara, graba y revisa los primeros casos. La otra reparte detector sobre texto y prueba de ASR; ambos trabajos usan esos casos y acuerdan el formato compartido. Todo el equipo revisa un ejemplo de principio a fin. |
| Detector e integración de audio       | Una pareja trabaja en datos, reglas y detector; otra en ASR, integración y mediciones. Ambas usan los mismos formatos de entrada y salida. |
| Evaluación final y entrega            | Se reparte ejecución, análisis y redacción; otra persona verifica cada resultado relevante y reproduce la demo.                            |

Las parejas pueden rotar según disponibilidad y conocimiento. La bibliografía y la
redacción se distribuyen junto al trabajo técnico que las necesita. Todo el equipo
participa de una muestra común de anotación, comprende el flujo completo y ensaya
la defensa. Los nombres y compromisos concretos se acuerdan en los issues.

El reparto sigue las tareas del hito, sin fijar líneas permanentes por persona.
Cada semana termina mostrando el resultado y su revisión; una lista de issues
cerrados por sí sola no demuestra avance.

## 13. Riesgos principales

Los riesgos activos se mantienen en el
[REGISTRO-RIESGOS.md](../gestion/REGISTRO-RIESGOS.md): corpus insuficiente, fuga entre
desarrollo y test, errores del ASR, falsas alarmas, costo de ejecución, integración
tardía y medición incorrecta de la anticipación. Probabilidad, impacto, responsables
y mitigaciones se actualizan en esa matriz.

## 14. Criterio de éxito

El proyecto será exitoso si responde las preguntas con un procedimiento honesto y reproducible, entrega un pipeline demostrable y documenta sus límites. No se fija una accuracy arbitraria como condición. Un resultado que muestre baja anticipación, degradación por ASR o superioridad de un baseline simple sigue siendo un resultado válido si el experimento está bien diseñado.
