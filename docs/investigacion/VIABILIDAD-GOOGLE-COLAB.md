# Viabilidad de Google Colab para pruebas compartidas

**Consulta:** 2026-11-04. Investigación documental; no se ejecutó una corrida en
Colab ni se comprobó allí la instalación del proyecto.

## Conclusión

Colab permite ejecutar código Python en una máquina remota desde el navegador y
compartir un notebook. Es una opción viable **a verificar mediante una prueba de
humo** para repartir pruebas de desarrollo con textos ficticios y audio sintético,
sin instalar el entorno en la computadora de cada integrante. No demuestra el
rendimiento del sistema en Android. El objetivo inmediato es comparar aciertos,
falsas alarmas y calidad de las respuestas, no medir tiempos en un teléfono;
la selección de ASR y detector sigue abierta en
[D09](../gestion/MAPA-DECISIONES.md#d09--elegir-asr-y-detector) y el protocolo en
[D08](../gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

Las grabaciones de personas y las transcripciones vinculables **no deben subirse**
con el acuerdo vigente: [D06](../gestion/MAPA-DECISIONES.md#d06--definir-corpus-y-piloto)
establece resguardo local a cargo de Mateo, y la
[política de privacidad](../corpus/PRIVACIDAD-DEL-SISTEMA.md) excluye transferir audio
o transcripciones a terceros. Que un archivo no se publique ni entre a Git no
equivale a autorizar su procesamiento en la nube. Las pruebas humanas requieren
resolver previamente esa incompatibilidad y las condiciones de autorización; esta
investigación no modifica el acuerdo.

## 1. Qué ofrece y qué limita

| Aspecto | Evidencia y consecuencia para el equipo |
|---|---|
| Acceso | [Colab](https://research.google.com/colaboratory/faq.html) es un servicio de notebooks alojados, con acceso gratuito a cómputo y GPU/TPU sujetos a disponibilidad. Cada integrante puede ejecutar desde su navegador sin usar un runtime local. |
| Colaboración | Los notebooks se guardan en Drive o pueden cargarse desde GitHub. Se comparte el notebook con código, texto, salidas y comentarios, **no** la máquina virtual ni sus archivos y librerías; cada ejecución debe reconstruir su entorno. [FAQ de Colab](https://research.google.com/colaboratory/faq.html). |
| Recursos | En el plan gratuito los límites y tipos de GPU varían; no hay disponibilidad garantizada. Una sesión puede durar como máximo 12 horas, pero terminar antes por inactividad o disponibilidad. Planes pagos también dependen de disponibilidad y unidades; no garantizan el mismo hardware. [FAQ de Colab](https://research.google.com/colaboratory/faq.html). |
| Ejecución | Seleccionar GPU no significa que el código la use: hay que comprobarlo. El servicio gratuito prioriza trabajo interactivo y prohíbe workers de cómputo distribuido; distribuir corridas manuales independientes entre integrantes no debe convertirse en un sistema de workers ni utilizar varias cuentas para eludir límites. [FAQ de Colab](https://research.google.com/colaboratory/faq.html). |
| Persistencia | La máquina se elimina tras inactividad o al alcanzar su duración máxima: dependencias, descargas y salidas guardadas solo allí se pierden. El montaje de Drive da acceso al código del notebook a los archivos de la cuenta; conviene revisar el código y guardar los resultados autorizados fuera de la VM. [FAQ de Colab](https://research.google.com/colaboratory/faq.html). |
| Versiones | El entorno preinstalado cambia. Google recomienda instalar las versiones de librerías necesarias; admite fijar una versión anterior del runtime, actualmente disponible durante un año desde su publicación. Eso mejora la repetibilidad, pero no fija GPU, resultados ni disponibilidad. [Versiones de runtime](https://research.google.com/colaboratory/runtime-version-faq.html). |
| IA de Colab | Las funciones generativas son opcionales y tienen tratamiento propio: Google indica que recoge prompts, código relacionado y salidas, que pueden ser revisados por personas. No incluir información personal o confidencial en esos intercambios. Esto no describe por sí solo todas las condiciones de tratamiento del runtime. [FAQ de Colab](https://research.google.com/colaboratory/faq.html). |

## 2. Aplicación a los experimentos existentes

| Trabajo | Posibilidad en Colab | Comprobación pendiente |
|---|---|---|
| Reglas, tests y métricas | Candidatos iniciales de bajo costo en CPU: reutilizar código existente con datos ficticios de desarrollo. | Que dependencias, rutas y exportación funcionen en una sesión nueva. |
| Detector SLM | El ensayo [slm-directo](../../experiments/slm-directo/README.md) usa Ollama y modelos descargados. La GPU podría acelerar las pruebas, pero no basta seleccionarla. | Instalar y arrancar Ollama en el runtime administrado, descargar un modelo, verificar uso real de GPU, salida estructurada y registro del manifiesto. No está validado aquí. |
| ASR y replay | [ASR local](../../experiments/asr-local/README.md) y [replay](../../experiments/replay/README.md) tienen scripts reutilizables; comenzar con audio TTS sintético permitido. | Compatibilidad de paquetes y modelos, descarga, rutas y exportación; no asumir que el ASR usa GPU ni cambiar sus parámetros sin registrarlo. |
| Medición para teléfono | Fuera del objetivo inmediato: se prioriza la calidad de las respuestas. | Una latencia o consumo medido en Colab solo describe esa VM. |

Los resultados históricos muestran variación entre corridas y entre equipos:
consultar [slm-directo](../../experiments/slm-directo/README.md). En consecuencia,
una comparación debe conservar tanto las predicciones como el entorno; no atribuir
una diferencia al modelo si también cambiaron hardware, versión o configuración.

## 3. Reparto y prueba de humo propuestos

> **Estado: propuesta sin discutir.** Relacionada con
> [D08](../gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental) y
> [D09](../gestion/MAPA-DECISIONES.md#d09--elegir-asr-y-detector). No modifica
> particiones, métricas ni modelos acordados, y no habilita el test reservado.

1. Preparar un notebook liviano que obtenga un commit identificado del repositorio,
   instale dependencias con versiones explícitas y ejecute los tests y reglas sobre
   un subconjunto ficticio de desarrollo identificado. No duplicar en el notebook
   la implementación que ya vive en `experiments/`.
2. Una persona prueba CPU/reglas y métricas; otra, ASR con TTS; otra, Ollama/SLM;
   otra revisa que pueda repetir una corrida y auditar una predicción. Son roles
   posibles, no asignaciones adoptadas. Cada una usa una sesión independiente y
   exporta su resultado sin sobrescribir el de otra persona.
3. Cada corrida guarda identificador, responsable, fecha, commit, dataset y split
   identificados con hash, configuración, modelo y versión, semilla o no aplica,
   versiones de dependencias y runtime, CPU/GPU y memoria observadas, comando,
   salida cruda y métricas. Registrar cortes y fallos; no contarlos como negativos.
4. Guardar resultados parciales autorizados periódicamente fuera de la VM; verificar
   integridad y revisar las salidas de celdas antes de compartir el notebook. No
   incluir audios humanos, datos identificables ni secretos en notebook, resultados
   o Git. No repartir ni explorar el test reservado para ajustar candidatos.
5. Considerar viable el circuito cuando otra persona reconstruya el entorno en una
   sesión nueva, ejecute la misma prueba y contraste un resultado con las salidas
   crudas; reportar diferencias, costo, interrupciones y pasos manuales. Si la GPU no
   está disponible, registrar el bloqueo de esa prueba en vez de presentar CPU como
   medición equivalente.

No hay garantía de que una sola sesión alcance para una corrida completa. Se pueden
dividir lotes independientes de desarrollo por IDs y guardar cada lote terminado;
antes de unirlos hay que comprobar cobertura, duplicados, misma configuración y
versiones. Consolidar las predicciones por ID y calcular los porcentajes sobre los
conteos totales y sus denominadores, no promediar porcentajes de lotes de distinto
tamaño. Informar por separado aciertos en estafas, falsas alarmas en legítimas,
fallos de ejecución y casos no procesados; revisar ejemplos de errores y de motivos
o evidencia incorrectos. Estas son pruebas de desarrollo, no estimaciones de
rendimiento final. La división no debe mezclar semillas entre particiones ni convertir
variantes de una misma conversación en observaciones independientes; eso sigue
dependiendo del acuerdo de D08 y [#55](https://github.com/Corchets/bitacora_tesis/issues/55).
