# Revisiones humanas de Luciano

Captura del 2026-11-07. Publicación solicitada por Luciano en `laboratorio-main`, junto
con los antecedentes de [#144](https://github.com/Corchets/bitacora_tesis/issues/144), para
comparar las anotaciones con los resultados del sistema. Cada respuesta conserva su fuente;
ninguna se promueve automáticamente a referencia adjudicada.

## Fuentes y vista para comparar

| Archivo | Contenido y estado |
|---|---|
| [Original de #145](REVISION-145-LUCIANO-2026-11-07.json) | Descarga exacta del navegador: 20 fichas con respuestas, 17 confirmadas y 3 sin confirmar. Incluye las respuestas y observaciones literales. |
| [Correspondencia de #145](CORRESPONDENCIA-145-LUCIANO-2026-11-07.json) | Alias de esas 20 fichas → `case_id` de desarrollo y hash del diálogo. No publica la clave de las otras 22 fichas, las referencias anteriores ni resultados del detector. |
| [Fichas originales de inglés de #144](FICHAS-144-LUCIANO-INGLES-2026-11-07.md) | Copia exacta de las 20 fichas que estaban en custodia local: 16 casos conservados y 4 descartados. Las columnas atribuidas a Claude siguen separadas del juicio humano. |
| [Vista común JSONL](REVISIONES-LUCIANO-2026-11-07.jsonl) | 40 registros derivados con issue, revisor, identificador, respuesta de clase literal, marcas y enlace al original. Se regenera; no se edita a mano. |

SHA-256 del original de #145:
`e490dd5649b42c5ce2509fc8da6b26ac2c9f73d05f771a9ebf4b9a5b9cf05238`.
SHA-256 de las fichas de #144:
`0ce3610e78ad656d9ea43f485d7a18f6be6967d3c684b7b55d4914173ea111d6`.
La captura de #145 también tiene copias exactas en `data/private/` y `~/respaldos/`.

El encabezado «Fuera de Git» del original de #144 describe su custodia anterior. Se
conserva como antecedente histórico, sin alterar el archivo. Esta publicación autorizada
incluye las anotaciones; las conversaciones externas, sus traducciones y el resto del set
privado permanecen fuera de Git. El [relevamiento](RELEVAMIENTO-CORPUS-EXTERNO.md#74-revisión-de-las-20-llamadas-de-inglés-youtube-y-armado-del-set-local-2026-11-07)
documenta la procedencia y la conversión previa de turnos a líneas.

## Estado recuperado de #145

El navegador exportó respuestas de las llamadas **01–15 y 17–21**. Las **09, 10 y 14**
tienen `completa: false`, aunque pasan la validación de los campos del formulario. La
**17 sí tiene respuestas**; las **16 y 22 están vacías** en esta captura. Esto difiere del
recuerdo inicial de Luciano (01–22 salvo 17); se conserva lo observado, sin rellenar huecos.

El formulario anterior desmarcaba una ficha completa al editar cualquier campo, incluso
una observación opcional. Una prueba en Chrome reprodujo ese comportamiento. No existe
historial por campo para afirmar que esa fue la secuencia de cada ficha concreta.
La corrección conserva la confirmación cuando la edición sigue siendo válida y muestra
por separado fichas respondidas, confirmadas y sin empezar. No modifica esta captura ni
convierte sus tres casillas `false` en `true`.

## Cómo usar los datos

Regenerar la vista común sin datos privados ni modelos:

```bash
python3 experiments/slm-directo/consolidar_revisiones_luciano.py
python3 -m unittest discover -s experiments/slm-directo/tests -p test_consolidar_revisiones_luciano.py -v
```

Para #145, unir `case_id` con el resultado del detector y comprobar el hash del texto.
Para #144, usar `case_id = EXT-NNN` y el mapa local de turnos a líneas; las cuatro
descartadas conservan fila de origen pero no tienen `case_id` del set.
`archivo_original` y `selector_original` permiten volver a las explicaciones literales.

**Las unidades no se mezclan:** #145 usa líneas del diálogo; #144 conserva los turnos de
las lecturas y respuestas textuales como «13 17» o «nunca nombra que abre el anydesk».
No se convierten esas frases en números ni se imputan datos faltantes. La vista común
no contiene transcripciones ni predicciones del detector.

Estas son anotaciones de **un revisor**, con desacuerdos y dudas todavía sin adjudicar.
La comparación puede señalar casos para discutir, pero no reemplaza la segunda revisión
ni habilita cambiar las métricas finales. Quien haga una revisión independiente debe
evitar consultar estas respuestas antes de anotar. D07, D08, #144 y #145 siguen abiertos.
