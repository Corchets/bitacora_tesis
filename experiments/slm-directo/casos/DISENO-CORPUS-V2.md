# Corpus v2 — diseño y límites

Fecha: 2026-10-21. Redacción ficticia asistida, encargada por Luciano Grosso.
Cuotas y ajuste de longitud autorizados en la conversación de trabajo. Se conservan
los 53 antecedentes para reproducir corridas; se agregan 297 conversaciones.

> **Estado: propuesta sin discutir.** La composición, la definición de semilla y la
> reserva no constituyen el protocolo final de
> [D08](../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).
> Las referencias y marcas siguen pendientes de
> [D07](../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico).

## Cantidades

| Clase | Desarrollo anterior | Desarrollo nuevo | Reserva nueva | Total |
|---|---:|---:|---:|---:|
| Vishing | 29 | 46 | 100 | 175 |
| Legítima | 24 | 51 | 100 | 175 |
| Total | 53 | 97 | 200 | 350 |

Las cuotas siguientes se refieren exclusivamente a los 297 casos nuevos.

| Familia | Dev. vishing | Dev. legítima | Reserva vishing | Reserva legítima |
|---|---:|---:|---:|---:|
| banco | 12 | 10 | 25 | 20 |
| whatsapp | 8 | 5 | 15 | 8 |
| soporte | 8 | 5 | 20 | 10 |
| organismo_previsional | 6 | 3 | 10 | 6 |
| premio | 6 | 3 | 15 | 6 |
| familiar | 6 | 5 | 15 | 18 |
| trabajo | 0 | 5 | 0 | 8 |
| delivery | 0 | 5 | 0 | 8 |
| medico | 0 | 5 | 0 | 8 |
| escuela | 0 | 5 | 0 | 8 |

| Dificultad principal | Desarrollo nuevo | Reserva nueva |
|---|---:|---:|
| Vishing: directo | 18 | 40 |
| Vishing: indirecto, inducido o partido | 18 | 40 |
| Vishing: termina antes del pedido | 10 | 20 |
| Legítima: cotidiana | 25 | 40 |
| Legítima: pedido razonable | 16 | 35 |
| Legítima: mención sin pedido | 10 | 25 |

Cada conversación nueva tiene entre 12 y 40 líneas; la mayoría tiene 20–40.
La extensión se logra mediante aclaraciones, objeciones, negociación y consecuencias
de lo dicho. Los textos previos no se alargan ni se reetiquetan retroactivamente.
Hay 24 variantes escritas de transcripción en desarrollo y 60 en reserva, la mitad
de cada clase. Son casos de robustez del detector, no transcripciones medidas de ASR.

## Semillas, parentesco y reserva

`particion` es `desarrollo` o `test_reservado`. Su ausencia en los 53 antecedentes
significa desarrollo. `grupo` conserva la procedencia; los nuevos son `corpus_v2`.
Cada nuevo caso describe una `situacion` concreta y una semilla propuesta registrada
como `borrador` en el [catálogo](../../../docs/corpus/CATALOGO-ESCENARIOS.csv).
`escenario_base` enlaza el antecedente que respalda la modalidad, cuando corresponde;
los contextos cotidianos originales pueden tenerlo en `null`.

La fuente de una modalidad no documenta el diálogo ni los procedimientos de atención
inventados. Las nuevas filas del catálogo distinguen esa adaptación del respaldo
externo del escenario base. No se recuperan las dos filas policiales descartadas.

Las semillas propuestas y los pares no pueden cruzar particiones. **La validación
por ID no demuestra independencia semántica.** Se comparten familias y modalidades
base entre desarrollo y reserva: crear un ID nuevo no vuelve independiente una
paráfrasis. D08 debe revisar la granularidad y el parentesco con los 53 antecedentes;
si considera dos situaciones una misma semilla, se deben reagrupar y versionar la
reserva antes de usarla. Estos 200 casos son candidatos reservados, no un test final
homologado ni 200 observaciones independientes demostradas.

El runner usa desarrollo por defecto; incluso `--casos` rechaza un ID reservado
salvo que se indique `--particion test_reservado`. Esa opción queda para la evaluación
final tras acordar D08. El panel solo incorpora desarrollo: no contiene diálogos,
marcas ni pruebas individuales de la reserva, ni los ofrece al probador en vivo.
Los archivos locales siguen siendo accesibles para preparar y revisar el corpus;
esta separación evita mezclas accidentales, no es un control de acceso.

`MANIFIESTO-CORPUS-V2.json` registra SHA-256 de los textos, referencias, asignaciones y
catálogo. Se crea una sola vez con `python3 casos.py --congelar`, luego de la revisión
técnica. `python3 casos.py --listar` detecta altas, bajas y modificaciones posteriores.
El comando no sobrescribe una reserva existente. Una revisión humana que cambie
referencias requiere una nueva versión acordada en D08 y sus nuevas huellas.

## Referencia y calidad

La clase responde a la situación ficticia. En un fraude abortado puede no alcanzarse
evidencia suficiente para inferir la identidad o intención desde el texto: ese límite
se explicita en `notas`; `T_R`, `T_C` y `pedido` quedan nulos cuando no hubo pedido.
No se inventa una acción crítica para completar marcas.

En solicitudes indirectas o partidas se registra una ubicación tentativa y la
alternativa razonable en `notas`, sin adjudicar D07. Una negativa no es cumplimiento.
Las legítimas pueden pedir y recibir datos o transferencias: esos eventos pueden
figurar en evidencia, manteniendo nulas las marcas críticas de fraude. A y B indican
orden de primera intervención, no dirección de llamada ni rol sospechoso.

Todos los nombres, números, montos y episodios nuevos son inventados. Ninguna
revisión automática o de otro agente cambia `revision_humana` a `true`.
La selección humana, las anotaciones independientes y su adjudicación siguen
pendientes. No se ejecutaron detectores sobre la reserva para elegir reglas,
prompts, modelos, umbrales ni política de alerta.

## Qué se puede medir

Estos textos permiten probar el detector, no el reconocimiento de voz. La selección
de audio está en [GRABACIONES-ASR.md](GRABACIONES-ASR.md). No se trasladan las líneas
a segundos ni se atribuye a las corrupciones escritas una WER medida.

La meta 95/5 sigue siendo propuesta. Por la fórmula de Wilson usada en el panel,
0/100 falsas alarmas tiene límite superior de 3,70 % y 1/100 de 5,45 %;
95/100 estafas detectadas tiene límite inferior de 88,83 % y 100/100 de 96,30 %.
Son cálculos binomiales de referencia; no corrigen dependencia entre situaciones
relacionadas ni autorizan generalizar a llamadas reales.
