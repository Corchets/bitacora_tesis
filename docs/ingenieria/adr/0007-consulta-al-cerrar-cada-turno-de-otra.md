# ADR 0007 — Consultamos al SLM solo al cerrar cada turno de OTRA

- **Fecha:** 2026-11-09
- **Estado:** Aceptada
- **Participantes de la discusión:** Mateo Antenucci, por el equipo, al cerrar la etapa 3 de
  [#143](https://github.com/Corchets/bitacora_tesis/issues/143).
- **Ámbito:** arquitectura

## Contexto

Hoy el panel VoIP consulta al SLM en cada frase final del ASR, de cualquiera de los dos lados. El ASR corta las frases
tras 0,8 s de silencio. En desarrollo, en cambio, cada consulta es un turno completo con su hablante conocido. En la
etapa 3, consultar solo en los turnos de OTRA no empeoró ninguna cifra en más de 2 y usó la mitad de las consultas: de
21 a 11 por llamada de estafa, en mediana
([análisis](../../../experiments/slm-directo/corridas/2026-11-09_pedido-critico-etapa-3/analisis.md)).

## Decisión

1. La app junta las frases del ASR de cada canal en turnos. Un turno se cierra cuando el otro lado empieza a hablar en
   serio (más de 1 s o 3 palabras; un «ajá» no cuenta) o tras un silencio largo, de unos 2 s.
2. Al cerrar cada turno de OTRA, la app consulta al SLM con toda la transcripción. Los turnos de PROTEGIDA entran en el
   contexto, pero no consultan.
3. Si un turno de OTRA se alarga, se consulta igual al llegar a un tope.

Los umbrales de cierre y el tope son provisorios: se fijan con grabaciones, no con los casos.

## Alternativas consideradas

| Alternativa | A favor | En contra | Por qué se descartó |
|---|---|---|---|
| Consultar en cada frase de los dos lados (el panel de hoy) | Avisa antes, si la frase alcanza | El doble de consultas, y no es lo que se midió | El costo por llamada pesa en el teléfono |
| Consultar en cada frase de OTRA, sin juntarlas | No hay que armar turnos | Consulta a mitad de una oración, y eso no se midió | Se mide aparte, con cortes simulados |
| Un solo ASR que alterna entre canales | Parecía ahorrar memoria | Los dos canales ya comparten el modelo, y suma el cambio de stream y la voz superpuesta | No ahorra nada |
| Subir el silencio de corte del ASR a 2 s | Turnos más largos sin capa nueva | Atrasa el texto y puede juntar las dos voces | El turno se arma después del ASR |

## Consecuencias

- Hace falta saber quién habla, así que el diseño depende de capturar cada canal por separado
  ([D05](../../gestion/MAPA-DECISIONES.md#d05--elegir-la-fuente-de-audio-demostrable)). En altavoz no hay canales, y
  queda como limitación declarada.
- Se pierden los avisos que salían de una línea de PROTEGIDA, como «¿te leo el código?».
- «Solo OTRA» se simuló sobre corridas que consultaron todas las líneas, y todas las cifras suponen turnos perfectos. La
  evaluación final mide cómo cambian con cortes simulados del ASR.
- En el panel es un cambio chico: el disparo en `llamada.py` y un acumulador de turnos.

**Para reconsiderarla:** que los cortes simulados del ASR muevan las cifras más de ±2, o que en el teléfono una
consulta tarde más que un turno típico de OTRA.

## Referencias

- [Etapa 3 de #143](../../../experiments/slm-directo/corridas/2026-11-09_pedido-critico-etapa-3/analisis.md), regla 4.
- [`asr-local/motores.py`](../../../experiments/asr-local/motores.py), `MotorSherpaParakeet`: los dos canales comparten
  el reconocedor.
