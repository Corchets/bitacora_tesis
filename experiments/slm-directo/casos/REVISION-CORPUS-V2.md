# Revisión técnica del corpus v2

Fecha: 2026-10-21. Revisión vigente: **r02**. Encargo de Luciano Grosso; redacción de dos subagentes
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
| Largo nuevo | Mínimo 17, máximo 38 líneas. 17 casos de 12–19; 230 de 20–29; 50 de 30–40. |
| Cotidianas nuevas | 25 de desarrollo y 40 de reserva; familia, trabajo, delivery, médico y escuela. |
| Presentación tipo ASR | 24 de desarrollo y 60 de reserva; mitad de cada clase. |
| Tipos de pedido crítico nuevos | 35 `REQUEST_AUTH_CODE`, 25 `REQUEST_SECRET`, 21 `REQUEST_PERSONAL_DATA`, 19 `REQUEST_TRANSFER`, 9 `REQUEST_REMOTE_ACCESS`, 7 `REQUEST_SECURITY_ACTION`. |
| Fraudes sin pedido nuevo | 10 de desarrollo y 20 de reserva, con marcas nulas y límites de inferencia anotados. |
| T_C nuevo anotado | 15 en desarrollo y 32 en reserva; son marcas candidatas e incluyen cumplimientos parciales discutibles, señalados en notas. |
| Revisión humana | 0 casos; `revision_humana:false`. |
| Antecedentes | Los 53 textos y sus referencias coinciden byte por byte con `ece8ef4`. |
| Duplicados nuevos | 0 al normalizar mayúsculas, acentos, puntuación y números y comparar con todo el inventario. |
| Turnos consecutivos duplicados en los nuevos | 0. La ausencia de repetición literal no demuestra independencia semántica. |

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

## Corrección r02 solicitada por Luciano

La revisión crítica posterior encontró fallas que la validación de formato no podía
detectar. Se modificaron **95 textos y 254 referencias**; estos números incluyen
cambios de orden de hablantes y mejoras de descripción, no 95 reescrituras completas.
El catálogo se sincronizó con las situaciones y dificultades revisadas.

- Se corrigieron repartos y saldos en las transferencias familiares legítimas:
  46.800 entre cuatro, y 38.000 cubiertos con 15.000 + 19.000 + 4.000. Se eliminó
  la promesa de pagar otra vez después de confirmar que el aporte ya estaba saldado.
- Los fraudes de alta bancaria distinguen un equipo o receptor de verificaciones
  ajeno de una operación sobre el propio dispositivo. Otros episodios ahora muestran
  el desvío hacia un representante desconocido o permisos ajenos al soporte ofrecido.
  La mera solicitud de DNI, transferencia o asistencia remota no se usa como prueba
  suficiente de fraude.
- Se alinearon `situacion`, `que_prueba`, evidencia y desenlaces: una negativa posterior
  no borra los datos o permisos ya entregados. Los cumplimientos parciales conservan
  su duda explícita en D07/D08. Tres entregas antes afirmadas en la reserva dejaron de
  figurar al reescribir esos episodios con negativa sin entrega.
- Se quitaron frases metanarrativas como «marca inventada» de la conversación y tres
  turnos idénticos consecutivos. `que_prueba` de las legítimas ahora distingue la
  dificultad de la sinopsis y remite a un intercambio concreto.
- En 74 fraudes, quien recibe atiende primero y se reasigna todo A/B; también se
  desplazan marcas, evidencia y menciones de líneas. Entre los pedidos nuevos de
  desarrollo hay 18 emitidos por A y 18 por B; en la reserva hay 40 y 40. Son
  propiedades de los guiones revisados, no una cuota de protocolo aprobada.
- Se ampliaron escenas con contradicciones, preguntas y consecuencias específicas,
  y se variaron cierres sin pedido para incluir interrupciones domésticas y pérdida
  de conexión, además del corte para verificar identidad.

La comprobación estructural recorre los 350 pares. La revisión semántica fue dirigida
a los problemas identificados, con contraste entre coordinación y agentes; **no es
una validación humana exhaustiva ni prueba de realismo de todas las llamadas**.
Las clases autorales de escenas sin pedido pueden no ser inferibles del texto, y no
se convierten por esta revisión en aciertos obligatorios o falsas alarmas adjudicadas.

## Verificación reproducible

En r02: **42 tests de `slm-directo`, 28 de métricas y 12 de replay pasan**;
`casos.py --listar` informa 350 válidos y se regenera el panel. Se comprueban los
enlaces locales de los Markdown afectados y la sintaxis JavaScript del panel.
No se ejecuta un detector para medir ni ajustar estas correcciones.

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
Las huellas actuales se registran en `MANIFIESTO-CORPUS-V2.json`, junto con la
trazabilidad explícita de r02. El manifiesto anterior se recupera sin alteraciones:

```bash
git show acdf4642073bbee0fea4d2d8a2fe5ea819c51527:experiments/slm-directo/casos/MANIFIESTO-CORPUS-V2.json
```

Su SHA-256 es `fab60ea3ee3bb498926406f8597a8f34efcd3415414269b0f2104bbb3cd27bfa`.
El comando `--congelar` sigue rechazando sobrescribir una reserva existente.
El panel solo carga los 150 casos de desarrollo y muestra el tamaño agregado de la
reserva. Las corridas históricas conservan sus denominadores originales.

## Límites que siguen abiertos

La revisión de agentes no mide acuerdo entre personas. Se requiere revisión humana
de situaciones y referencias, selección de muestra común y adjudicación en D07.
Las dudas sobre pedidos inducidos, el comienzo de una frase partida o una entrega parcial permanecen en las notas de cada caso; no se resolvieron por código.

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
