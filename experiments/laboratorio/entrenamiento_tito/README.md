# Datos argentinos para Tito — #41

Banco de frases y fragmentos **sintéticos originales**, escritos como intervenciones de
llamadas en español argentino. Las fuentes argentinas respaldan las modalidades que se
representan; los textos no son transcripciones extraídas de esas fuentes. No se incorporan
conversaciones inglesas, españolas ni los casos y resultados anteriores del laboratorio.

El usuario autorizó la generación amplia y esta carpeta el 2026-10-02. La búsqueda y la
generación se ejecutan mediante la skill `orchestration`
con workers de Orca, `gpt-6-luna`, esfuerzo `medium`. La evidencia de los despachos y los
resultados efectivos queda en [orquestacion.json](orquestacion.json).

> **Estado: propuesta sin discutir.** La composición balanceada y el uso experimental del
> banco se vinculan a [D07](../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico),
> [D08](../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental) y
> [D09](../../../docs/gestion/MAPA-DECISIONES.md#d09--elegir-asr-y-detector). Producir los datos fue
> autorizado; este artefacto no congela taxonomía, particiones, umbrales ni elección de modelo.

## Contenido y cobertura

Se generaron **6.000 realizaciones de 300 familias**, 3.000 por clase. El filtro inicial deja
**5.520 textos para entrenamiento** (2.620 `estafa`, 2.900 `legitima`): excluye 480 textos de
veinticuatro familias por ambigüedad o combinaciones poco naturales. Los motivos están en
[exclusiones.json](exclusiones.json); los textos descartados se conservan en
[pendientes_revision.jsonl](pendientes_revision.jsonl) y no entran a `semillas.json`.
Una familia representa un marco de situación/pedido; sus veinte realizaciones
son variantes relacionadas, compuestas a partir de bloques compatibles. **No son 6.000
escenarios independientes**, ni un corpus de llamadas reales.

| Lote | Cobertura | Familias | Textos |
|---|---|---:|---:|
| Banco | Banco, billetera, autenticación, pagos, créditos, devoluciones y soporte | 100 | 2.000 |
| Identidad | WhatsApp, organismos, salud, beneficios, servicios y telefonía | 100 | 2.000 |
| Cotidiano | Familia, compras, reservas, trabajo, reparaciones y charlas comunes | 100 | 2.000 |

La tabla cuenta lo generado, antes del filtro. Quedan 276 familias exportadas para entrenar,
1.640 textos cotidianos, 1.880 de identidad y 2.000 de banco. En cada lote generado hay cincuenta familias
por clase; después del filtro la exportación no está perfectamente balanceada.
Los negativos incluyen usos inocentes de
códigos, urgencia y dinero; las palabras clave guían cobertura, no asignan la clase. La
distribución observada por tema y término está en [cobertura.json](cobertura.json). Se cuentan
coincidencias literales normalizadas: una ausencia en ese mapa no prueba ausencia del concepto.

## Fuentes de verdad y archivos derivados

- `familias_banco.json`, `familias_identidad.json`, `familias_cotidiano.json`: textos originales,
  tema, clase, identificador de familia y referencias. Editar aquí para corregir un ejemplo.
- `fuentes_banco.json`, `fuentes_identidad.json`, `fuentes_cotidiano.json`: URL, fecha de consulta,
  hallazgo y función de cada fuente. No se importaron textos de terceros.
- `informe_*.md`: evidencia y límites de cada entrega de los workers.
- [exclusiones.json](exclusiones.json): filtro conservador de familias por falta de contexto
  o incoherencia. No redefine la taxonomía; una familia excluida debe reescribirse y revisarse
  antes de quitarla de este archivo.
- [ejemplos.jsonl](ejemplos.jsonl): exportación con metadatos por realización, idioma `es-AR`,
  origen `sintetico_original`, `split: null` y uso de entrenamiento o revisión pendiente.
- [semillas.json](semillas.json): exportación compatible con el clasificador actual,
  `{"estafa": ["…"], "legitima": ["…"]}`.
- [manifest.json](manifest.json): configuración, hashes SHA-256 de entradas y preparador.
- [muestra_revision.md](muestra_revision.md): primera y última realización de cada familia
  para inspección. No es un test ni certifica revisión humana.

Las exportaciones se regeneran; no se corrigen a mano. Los textos no excluidos están destinados al
**entrenamiento de desarrollo**; la clase de un texto pendiente es la propuesta del generador,
no una etiqueta validada para aprender. No se reservó un test dentro de este banco. Las familias y los
temas deben conservarse al diseñar futuros splits; familias con la misma maniobra pueden
seguir siendo similares aunque tengan identificadores diferentes.

## Reproducir y verificar

Desde la raíz del repositorio, con Python 3 y sin descargar modelos:

```bash
python experiments/laboratorio/entrenamiento_tito/preparar.py
python experiments/laboratorio/entrenamiento_tito/preparar.py --check
python -m unittest discover -s experiments/laboratorio/entrenamiento_tito -p 'test_*.py'
```

El preparador verifica cantidades, clases, referencias, IDs, longitudes de 6–65 palabras,
duplicados incluso con cambios de caja/tildes/puntuación, contradicciones entre clases y
algunos marcadores de narración externa o español peninsular. Rechaza URLs, correos y números
largos en los textos. Son controles estructurales y heurísticos; no prueban por sí solos la
etiqueta, la naturalidad, la diversidad semántica ni la ausencia de todo dato identificable.
`--check` también exige que todas las exportaciones coincidan exactamente con sus entradas.

La revisión del coordinador inspeccionó la primera y la última realización de cada familia
y pidió correcciones de voz, contexto, ambigüedad y estilo a los workers. No fue una
adjudicación humana exhaustiva de las seis mil cadenas. Las exclusiones son conservadoras:
se aparta la familia completa cuando algunas de sus realizaciones no sostienen la etiqueta.

La reproducción vuelve a materializar los mismos textos desde los JSON. No vuelve a consultar
al modelo generador; no hay seed de muestreo que garantice repetir una generación de LLM.

## Alimentar el clasificador de esta rama

[DetectorEncoder](../detector_encoder.py) consume directamente la exportación. Su implementación
actual mantiene el encoder congelado y ajusta una regresión logística con seed `42` y
`max_iter=1000`; no hace fine-tuning del encoder. En un entorno con las dependencias y el modelo:

```python
import sys
from pathlib import Path

sys.path.insert(0, "experiments/laboratorio")
from detector_encoder import DetectorEncoder

detector = DetectorEncoder(
    "pysentimiento/robertuito-base-uncased",
    Path("experiments/laboratorio/entrenamiento_tito/semillas.json"),
)
```

La factoría existente también acepta `SEMILLAS_PATH` junto con `DETECTOR=encoder`. En
Docker Compose, `ENTRENAMIENTO` puede apuntar a la ruta absoluta de esta carpeta, montada
como `/data/entrenamiento`; `SEMILLAS_PATH=/data/entrenamiento/semillas.json`. No hace falta
copiar ni sobreescribir las semillas en la raíz del laboratorio.

La implementación embebe texto por texto y recorta a 128 tokens: el tiempo de ajuste crece
con este banco. El límite en palabras no garantiza por sí mismo entrar en 128 tokens para
todos los tokenizadores. [tokens.json](tokens.json) conserva la comprobación con el archivo
de RoBERTuito, su revisión y SHA-256, sin truncamiento y contando tokens especiales. Para
repetirla con ese archivo local y la dependencia opcional `tokenizers`:

```bash
python experiments/laboratorio/entrenamiento_tito/verificar_tokens.py \
  --tokenizer-json /ruta/al/tokenizer.json \
  --modelo pysentimiento/robertuito-base-uncased \
  --revision 20cb399e4b93f270c0cd6b6f533bcb0ada3cb658
```

No se entrenó el detector ni se midió mejora en esta entrega.

## Cómo continuar

1. Revisar semánticamente familias completas, especialmente negativos con autenticación,
   pagos o ayuda remota, y corregir su fuente primaria. Ampliar formulaciones y contextos donde
   se repitan aperturas o haya cobertura débil; no sumar variantes por sumar.
2. Diseñar ejemplos independientes de evaluación en [#45](https://github.com/Corchets/bitacora_tesis/issues/45),
   escritos a partir de situaciones que no se usaron aquí. Acordar agrupamiento y protocolo
   con D08 antes de calibrar umbrales o reportar calidad.
3. Ajustar la cabeza del encoder con este banco y medir errores en esa evaluación independiente,
   registrando versión, hashes, modelo, configuración y recursos. Las proporciones de clases
   sintéticas no estiman prevalencia ni calibran una probabilidad de fraude real.
4. Cuando haya audio autorizado y su ASR, contrastar texto de referencia frente a transcripción.
   Estos textos no simulan errores medidos de Zipformer ni reemplazan el piloto.

La investigación de fuentes y sus límites vive en
[SINTESIS-ESTADO-DEL-ARTE §2.3](../../../docs/investigacion/SINTESIS-ESTADO-DEL-ARTE.md#23-fuentes-y-producción-de-ejemplos-argentinos-para-tito-41).
El [comentario de avance para #41](COMENTARIO-ISSUE-41.md) queda listo para copiar;
no declara cerrado el alcance original del issue.
