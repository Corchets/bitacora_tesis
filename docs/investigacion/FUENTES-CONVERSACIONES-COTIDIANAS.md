# Fuentes de conversaciones cotidianas

Consulta: 2026-11-04. Objetivo: identificar conversaciones humanas no guionadas
para explorar falsas alarmas en habla cotidiana. La inclusión en una evaluación y
sus particiones siguen pendientes en [D08](../gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

## CABNC

[CABNC](https://talkbank.org/ca/access/CABNC.html) describe 1.436 conversaciones
naturalistas en inglés británico, con unos 400 participantes, tomadas del British
National Corpus. El [proyecto](https://github.com/saulalbert/CABNC) describe
conversaciones informales en hogares, pasillos y otros entornos cotidianos, recogidas
mediante grabadoras portátiles. No afirma que todas sean llamadas telefónicas ni
que cada archivo corresponda a una llamada completa. Por eso sirven para explorar
conversación cotidiana, con una diferencia de dominio frente a llamadas de vishing.

El proyecto declara las transcripciones bajo [CC BY 3.0](https://creativecommons.org/licenses/by/3.0/):
requiere atribución y señalar adaptaciones, como traducciones. El audio tiene
restricciones de uso adicionales, explicitadas por la ficha de CABNC. Los derechos
de autor no sustituyen la revisión de privacidad: las conversaciones podrían
contener datos identificables y las reglas del repositorio impiden subirlos a Git.

La ficha ofrece descarga en TalkBank; el enlace de descarga devolvió una pantalla de
autenticación en la consulta automatizada. El repositorio público del proyecto sí se
clonó el 2026-11-04: revisión `0a28a11e168e312d1b9ad406a3352f31c13b86a2`,
con archivos CHAT en `data/cabnc_talkbank_chat/`. La selección de unidades,
completitud, elegibilidad y revisión de datos personales requieren inspección; no
se verificó que existan 200 llamadas independientes elegibles. Una traducción
requiere conservar la referencia al original y comprobar su fidelidad.

### Muestra exploratoria extraída el 2026-11-04

Se seleccionaron 200 archivos CHAT en inglés, conservados fuera del repositorio en
`/home/chato/conversaciones-cabnc-exploracion-2026-11-04.zip`. El archivo incluye
un manifiesto con las rutas originales, cantidad de turnos y SHA-256 de cada
transcripción. La revisión de origen es la indicada arriba; el SHA-256 del ZIP es
`481f30ec2ebad52afa0fc8561a8212f865964955e9dbb8fcddd052a1bc22e6cd`.

Se filtraron archivos con exactamente dos hablantes que intervienen, ambos con edad
de al menos 18 años declarada en los metadatos, y al menos 25 turnos. Entre los 201
archivos que cumplieron el filtro se eligieron 200 alternando carpetas de origen,
con orden seudoaleatorio y semilla `20261104`. La edad proviene de los metadatos y
no se verificó por separado. Hay 54 pares de identificadores de hablantes y 34
carpetas de origen; los archivos van de 25 a 825 turnos. No se revisó cada diálogo
ni se demostró que cada archivo sea una conversación completa e independiente.

Las transcripciones incluyen metadatos personales y no fueron anonimizadas: se
guardaron con permisos restringidos fuera de Git. Están en el idioma original,
sin traducción ni anotación humana de legitimidad. Son material de exploración,
no se incorporaron al test ni permiten estimar por sí solas falsas alarmas en
llamadas reales. La selección no decide la composición o particiones de D08.

## Alternativas telefónicas

[CALLHOME Spanish, segunda edición](https://catalog.ldc.upenn.edu/LDC2026S04)
contiene 120 llamadas no guionadas en español; la mayoría entre familiares o
amistades. Está sujeto a un acuerdo de LDC y no alcanza por sí solo las 200.
[Fisher English](https://catalog.ldc.upenn.edu/LDC2005T19) reúne, sumando sus dos
partes, 11.699 conversaciones telefónicas y también se distribuye bajo acuerdo
LDC. Antes de adquirir o redistribuir cualquiera debe verificarse el acceso y los
términos concretos; no se ha comprobado acceso institucional.
