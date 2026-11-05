# Comparación de desarrollo — Tito viejo y Tito viejo 2.0 con Gemma 4 E2B

Fecha: 2026-11-05. Seguimiento: [#140](https://github.com/Corchets/bitacora_tesis/issues/140).

> **Estado: propuesta sin discutir.** La variante y su evaluación son exploratorias;
> no sustituyen la configuración elegida ni cierran [D08](../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

## Pregunta y configuraciones

Comparar la configuración vigente Tito viejo → Gemma 4 E2B con Tito viejo 2.0
sobre conversaciones de desarrollo y, si se cuenta con material apto, conversación
cotidiana. Tito viejo 2.0 suma señales léxicas al puntaje de la frase y no envía
a Gemma el bloque de indicio; conserva los pesos del modelo original. La
comparación conjunta no permite atribuir diferencias por separado a estos dos
cambios. La definición y pesos están en [tito_viejo_2.py](../tito_viejo_2.py).

## Antecedente disponible: 150 casos de desarrollo

La [corrida del 2026-11-04](../corridas/2026-11-04_003715_e2b-tito-viejo-150/analisis.md)
contiene las salidas, configuración, versión y límites del Tito viejo. Sus
referencias no tienen revisión humana; no es test reservado ni rendimiento final.
El grupo de 53 reúne laboratorio, piloto escrito y trampa; los otros 97 son
`corpus_v2`. Los totales de 53 se obtienen sumando las tres filas del informe.

| Configuración y grupo | Estafas con aviso | Legítimas con aviso |
|---|---:|---:|
| Tito viejo, 53 antecedentes | 27/29 (93,1 %) | 8/24 (33,3 %) |
| Tito viejo, corpus v2 | 24/46 (52,2 %) | 5/51 (9,8 %) |
| Tito viejo, total | 51/75 (68,0 %) | 13/75 (17,3 %) |
| Tito viejo 2.0, 53 antecedentes | 27/29 (93,1 %) | 8/24 (33,3 %) |
| Tito viejo 2.0, corpus v2 | 28/46 (60,9 %) | 4/51 (7,8 %) |
| Tito viejo 2.0, total | 55/75 (73,3 %) | 12/75 (16,0 %) |

**Conclusión provisoria:** en los 53 antecedentes las dos variantes tienen los
mismos conteos, aunque no los mismos casos. En v2, la variante 2.0 avisa cuatro
estafas más y una legítima menos. Sobre las 150, ninguna alcanza simultáneamente
la meta del tutor de 80–85 % de avisos en estafas y 10–15 % de falsas alarmas.
**Sugerencia:** revisar especialmente la estafa que 2.0 dejó de avisar y las dos
legítimas que empezó a avisar, con revisión humana de las referencias.

## Conversaciones cotidianas

Ambas configuraciones: **pendiente**, sin resultados. La [fuente de CABNC](../../../docs/investigacion/FUENTES-CONVERSACIONES-COTIDIANAS.md)
identifica una muestra en inglés sin anonimizar ni anotación de legitimidad. El
[procedimiento Colab](../colab/README.md) indica no subir transcripciones
identificables. La selección, una eventual traducción y su revisión, la
independencia y la elegibilidad no están resueltas. No corresponde tomar cada
alerta como falsa alarma confirmada.

**Conclusión y sugerencia:** pendientes de disponer de datos aptos y ejecutar
ambas configuraciones. Para una comparación interpretable, conservar la misma
selección y documentar idioma, traducción, procedencia y referencias.

## Comparación frente a frente

En los 150 casos, 2.0 agrega aviso en cinco estafas y pierde uno que Tito viejo
había emitido. De las legítimas, agrega dos avisos y deja de emitir tres. Los
cambios exactos, incluidas líneas y referencias temporales disponibles, salen de:

```bash
python experiments/slm-directo/analisis/comparar_tito_viejo_2.py
```

La estafa `TR-04-pedido-tras-charla-larga` pasó de aviso en L27 a sin aviso;
`TR-05-asado-con-transferencia` pasó de sin aviso a aviso en L14. Las referencias
son provisorias. Hubo cero respuestas inválidas en las dos corridas; consultas a
Gemma: 1.179 para Tito viejo y 1.143 para 2.0, con terminación al primer aviso.
La diferencia de consultas no aísla costo: cambia también el punto de corte.

**Conclusión:** 2.0 mejora el conteo global en esta muestra (+4 estafas, −1 falsa
alarma), pero pierde una estafa y añade dos falsas alarmas. No demuestra mejora
general ni permite separar el aporte de las señales y la eliminación del indicio.
**Sugerencia:** revisar esos cambios y, si interesa atribuirlos, ensayar una
condición intermedia en otra muestra de desarrollo independiente.

## Procedimiento y límites

La [salida cruda de Colab](../corridas/2026-11-05_TITO-VIEJO-2-COLAB.zip)
contiene manifiesto, CSV e inventario. SHA-256:
`9e5b90b2b259bd076afc9af867ddafaa81aaecce9174c6d04217ccc3186bc1c3`.
[Notebook ejecutado](../colab/TITO-VIEJO-2-COLAB.ipynb): commit base
`2c01da2f8a6f457095f7e0b71ce2ba2b9365de0f`, con dos archivos locales
incorporados; sus SHA-256 figuran en el ZIP. El manifiesto registra parámetros,
Tito, modelo, máquina y tiempos. Se usó T4, seed 42, temperatura 0, prompt
`tarea`, `num_ctx` 4096 y digest de E2B `b37049369adf…`. Los hashes de los 150
textos y del prompt coinciden con la corrida histórica; las referencias no fueron
revisadas por humanos. La corrida histórica fue en Windows y esta en Colab; no
se comparan latencias como si fueran de la misma máquina. Las expresiones se
eligieron por fallos observados, por lo que la muestra no es una prueba
independiente de esa selección. No se usó el test reservado para medir.

La comparación solicitada de las conversaciones cotidianas sigue pendiente por
la condición de sus datos. No se calculó su tasa de falsas alarmas.
