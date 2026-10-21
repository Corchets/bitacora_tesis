# Revisión técnica del corpus v2

Fecha: 2026-10-21. Encargo de Luciano Grosso; redacción de dos subagentes
GPT-6 Luna, razonamiento high, coordinada y revisada por Codex.

> **Estado: propuesta sin discutir.** Esta es revisión técnica asistida, no revisión
> humana ni adjudicación de [D07](../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico).
> La reserva es candidata: no congela el protocolo de
> [D08](../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

## Evidencia observable

| Control | Resultado |
|---|---|
| Inventario | 350 pares texto/referencia: 53 antecedentes y 297 nuevos. |
| Desarrollo | 150: 75 vishing y 75 legítimas. |
| Reserva | 200: 100 vishing y 100 legítimas. |
| Largo nuevo | Mínimo 16, máximo 38 líneas. 18 casos de 12–19; 229 de 20–29; 50 de 30–40. |
| Cotidianas nuevas | 25 de desarrollo y 40 de reserva; familia, trabajo, delivery, médico y escuela. |
| Presentación tipo ASR | 24 de desarrollo y 60 de reserva; mitad de cada clase. |
| Tipos de pedido crítico nuevos | 35 `REQUEST_AUTH_CODE`, 25 `REQUEST_SECRET`, 21 `REQUEST_PERSONAL_DATA`, 19 `REQUEST_TRANSFER`, 9 `REQUEST_REMOTE_ACCESS`, 7 `REQUEST_SECURITY_ACTION`. |
| Fraudes sin pedido nuevo | 10 de desarrollo y 20 de reserva, con marcas nulas y límites de inferencia anotados. |
| T_C nuevo anotado | 15 en desarrollo y 35 en reserva; son marcas provisionales, con dudas particulares en notas. |
| Revisión humana | 0 casos; `revision_humana:false`. |
| Antecedentes | Los 53 textos y sus referencias coinciden byte por byte con `ece8ef4`. |
| Duplicados nuevos | 0 al normalizar mayúsculas, acentos, puntuación y números y comparar con todo el inventario. |
| Solapamiento superficial entre particiones | Máximo Jaccard de secuencias de cinco palabras: 0,02462. No es prueba de independencia semántica. |

Se controlaron las cuotas, archivos pareados, vocabulario, posiciones, coherencia de
las marcas con los fragmentos y protección de particiones. La revisión cruzada detectó
y corrigió evidencia de pedido ubicada en preguntas de quien lo recibía, marcas
desplazadas, finales con hablantes invertidos, fechas incoherentes, referencias sin
evidencia y advertencias de seguridad que facilitaban innecesariamente la clase.
También se incorporaron cumplimientos y finales distintos de la negativa.

La coordinación reescribió dos escenas extensas de desarrollo: `CV2-D-V-BANCO-001`
(38 líneas, pedido en la 32, atacante B) y `CV2-D-V-WHATSAPP-006` (36 líneas,
pedido partido en las 25–26). El primero retiene contexto administrativo distante;
el segundo mantiene abierta la duda de dónde anotar el comienzo del pedido.

## Verificación reproducible

Verificado después de integrar `886cff0`: **42 tests de `slm-directo`, 28 de métricas
y 12 de replay pasan**. El humo real de dos casos de desarrollo produjo manifiesto
y resumen con las nuevas legítimas bien contadas. Un ID reservado pasado al runner
por defecto fue rechazado antes de crear una corrida. Se comprobaron 240 enlaces
locales en los siete Markdown afectados y la sintaxis JavaScript del panel.

Desde `experiments/slm-directo/`:

```bash
python3 casos.py --listar
python3 -m unittest discover -s tests -v
```

Desde `experiments/metricas/`:

```bash
python3 -m unittest discover -s tests -v
```

Desde la raíz:

```bash
python3 experiments/slm-directo/analisis/tablero/armar_panel.py
```

La suite incluye balance y cuotas, exclusión de la reserva del runner y del panel,
rechazo de cruces de semilla/par, huellas que detectan altas/bajas/modificaciones,
rechazo de una reserva malformada y conteo correcto de las nuevas legítimas.
La reserva SHA-256 se registra en `MANIFIESTO-CORPUS-V2.json`; no se sobrescribe.
El panel solo carga los 150 casos de desarrollo y muestra el tamaño agregado de la
reserva. Las corridas históricas conservan sus denominadores originales.

## Límites que siguen abiertos

La revisión de agentes no mide acuerdo entre personas. Se requiere revisión humana
de situaciones y referencias, selección de muestra común y adjudicación en D07.
Las dudas sobre pedidos inducidos, el comienzo de una frase partida o una extracción
sin entrega final permanecen en las notas de cada caso; no se resolvieron por código.

Las semillas nuevas son borradores del [catálogo](../../../docs/corpus/CATALOGO-ESCENARIOS.csv),
con vínculo a la modalidad base. Comparten familias y modalidades con desarrollo:
el ID disjunto y la baja coincidencia literal no prueban independencia de escenarios.
D08 debe revisar su parentesco y la posibilidad de agruparlos antes del test final.
Las 200 conversaciones reservadas no se ejecutaron sobre detectores para afinar.

Los resultados sobre texto no prueban reconocimiento de voz ni rendimiento del
flujo completo. [GRABACIONES-ASR.md](GRABACIONES-ASR.md) separa 24 tomas iniciales,
126 casos que alcanzan como texto por ahora y 200 reservados. No se generó audio ni
se midió WER con las alteraciones escritas.

## Comentario de trazabilidad local

Trabajo solicitado en la conversación de 2026-10-21; relacionado con los antecedentes
[#50](https://github.com/Corchets/bitacora_tesis/issues/50) y
[#55](https://github.com/Corchets/bitacora_tesis/issues/55), sin issue nuevo asignado.
No corresponde emitir `Closes #55`: las particiones independientes y D08 siguen
pendientes. El artefacto técnico está disponible para revisión; la próxima acción es
revisar referencias y parentesco, y preparar las tomas de desarrollo según D06.
