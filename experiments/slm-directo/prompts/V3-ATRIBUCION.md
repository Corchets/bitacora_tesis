# Versión 3 — Atribuir el pedido dentro de la llamada

**Fecha:** 2026-11-04. **Rama:** `laboratorio-luciano`. Avance de
[#51](https://github.com/Corchets/bitacora_tesis/issues/51), que sigue abierto.

> **Estado: propuesta sin discutir.** Borrador para Gemma 4 E2B, sin inferencia
> nueva ni resultado medido. Las ambigüedades de referencia siguen en
> [D07](../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico)
> y el protocolo de comparación en
> [D08](../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

## Estado actual

**Desde esta sección hacia abajo, el documento describe el borrador anterior**, derivado de v1, y queda como
antecedente. Ese texto está en `git show 8a718fe:experiments/slm-directo/prompts/tarea_v3.txt`. Sus
afirmaciones de que v3 parte de v1, no está medida o conserva el contrato de v1 ya no valen para el texto vigente.

**Texto vigente:** [`tarea_v3.txt`](tarea_v3.txt), acordado el 2026-11-04. Parte de v2, quita el mínimo de
riesgo 0,5 y conserva el orden de campos de v2 (`evidencia`, `alerta_sugerida`, `riesgo`, `motivo`). Sus reglas:

1. Un pedido de dato personal o pago no basta: el contexto debe sustentar el peligro.
2. La negativa de la persona no borra un pedido anterior.
3. Se distingue el ofrecimiento espontáneo del que responde a una inducción previa.
4. Se evalúa la coherencia entre motivo, acción y daño, sin eximir por palabras como banco u oficial.
5. Si no se sabe qué es lo que piden, no se inventa qué permitiría hacer.
6. Sin base para alertar, evidencia y motivo van vacíos.

| Huella | Texto vigente |
|---|---|
| SHA-256 del archivo | `c11ecc1f8c6fd644c7d8b806369e73e952c3716c353fd805a0a71cbf634504e6` |
| Huella en los manifiestos (`.strip()`, 16 caracteres) | `a944aadc550480b3` |

**Resultado:** [probado en Colab sobre los 150 de desarrollo](../corridas/2026-11-04_193946_prompt-v3-a-solo-y-con-indicio/analisis.md). No se adopta como está.

## Antecedente: cambio e hipótesis del borrador anterior

El [historial de versiones](README.md#versiones-del-system-prompt) conserva la
v1 original (2026-10-13), la v2 previa (2026-10-21) y esta v3 en preparación.
La v2 ya modificaba varias instrucciones y el esquema de salida; no se usó en
las dos corridas de 150. Para aislar H1, la v3 parte de la v1 medida y conserva
su contrato. No representa una acumulación de los cambios de v2 ni una
comparación v2/v3. P0/P1 son los nombres de las condiciones experimentales.

**P0 / versión 1:** [`tarea.txt`](tarea.txt), conservado sin cambios. Coincide exactamente,
después de `.strip()`, con el prompt de los dos manifiestos de la
[comparación actual](../corridas/2026-11-04_132229_e2b-directo-150/comparacion-con-tito.md).
No hace falta duplicarlo para preservarlo.

**P1 / versión 3:** [`tarea_v3.txt`](tarea_v3.txt). Reemplaza únicamente
el párrafo «No alcanza con mencionar…» por una instrucción de atribución:
identificar quién pide qué a quién en esta llamada y distinguir ese pedido de
relato, hipótesis, ofrecimiento y consejo. Requiere revisar la inducción previa
para no descartar ofrecimientos inducidos, y mantener el pedido de la contraparte
aunque la persona lo rechace. El motivo y la cita deben respetar esos roles.

**Hipótesis H1:** hacer explícita esa operación puede reducir alertas cuyo
fundamento inventa o invierte un pedido, sin perder los pedidos peligrosos de la
llamada actual. Se debilita si persisten esas atribuciones incorrectas o si P1
descarta solicitudes reales porque aparecen como ofrecimiento, rechazo o trámite.
Una reducción neta de falsas alarmas con pérdidas de estafas no basta para
afirmar una mejora general.

Es un solo cambio conceptual en un bloque. No se está aislando el aporte de cada
frase de ese bloque; una futura diferencia solo sería atribuible a P1 en conjunto
bajo controles comparables. El texto crece de 1.516 a 2.177 caracteres después
de `.strip()`: tampoco se supone costo ni ajuste al contexto iguales sin medirlos.

Se conservan literalmente el encuadre incremental, la imposibilidad de verificar
identidades, el criterio de daño, las seis acciones y el contrato JSON con el
mismo orden de campos (`riesgo`, `alerta_sugerida`, `motivo`, `evidencia`). No se
agregan campos, ejemplos de guiones ni una escala nueva de riesgo. P1 no se
registró en `PROMPTS` ni `ESQUEMAS` de `detectores.py`; todavía no es una opción
del ejecutor. La demo continúa con P0.

| Huella | P0 | P1 |
|---|---|---|
| SHA-256 del archivo UTF-8 con LF final | `40b663ed170150c901935a575bb49648544cc4b29543f1d3cc0cfe302ee23b2d` | `8da26e12954a69340f7107aac0c73b1697ba8340f16ae5e4688f5ba26f1cdc8b` |
| SHA-256 del texto con `.strip()` como `cargar_prompt` | `bf4284996898c45dc0829d47590e65151fc1cbe0086457bee0d13834c9548928` | `5e92ab77c390392db69d9ca0b8ee4b112b5e6bfb3c7c44bb91921b3e61532c3b` |

La huella abreviada histórica de P0 es `bf4284996898c45d`; las huellas de archivo
y texto cargado difieren por el salto de línea final. P0 queda además identificado
en el commit de partida `0561dbe` por el blob Git
`5bb6ce415ca4b1db4d7d962c7f02e0cff14de30e`.

## Antecedente: contraste de desarrollo para revisar H1

Lectura de IA de 17 IDs explícitos, comprobados contra los IDs y hashes del
[manifiesto directo](../corridas/2026-11-04_132229_e2b-directo-150/manifiesto.json)
antes de abrir cada texto y su referencia. Todas esas referencias conservan
`revision_humana: false`. Las líneas citadas son observaciones de los textos;
las interpretaciones siguientes son expectativas del candidato, no salidas de P1
ni adjudicación humana. Cada enlace lleva al texto completo, pero el juicio sobre
un prefijo usa solo las líneas disponibles hasta ese momento.

| Falsa alarma o ambigüedad de P0 | Contraste peligroso y límite de P1 |
|---|---|
| [LAB-no-bajes-nada](../casos/texto/LAB-no-bajes-nada.txt), L1: A cuenta lo que le pidieron en otra llamada. En L2 B aconseja no descargar. El relato no es un pedido de B, incluso antes de L2. | [BANCO-003](../casos/texto/CV2-D-V-BANCO-003.txt), L14: B reformula lo que entiende; L19: A pide entregar efectivo. P1 debe atribuir cada intervención y reconocer el pedido de A sin confundir la reformulación de B con quien lo solicita. |
| [TR-03](../casos/texto/TR-03-negacion-y-consejo.txt), L5: «¿Y si me dicen…?» plantea una hipótesis; no prueba una amenaza de B. | [TR-09](../casos/texto/TR-09-victima-se-niega.txt), L5: A sí pide leer el SMS; L7 insiste y L10 B se niega. La negativa no borra lo que A pidió. |
| [TR-06](../casos/texto/TR-06-banco-alerta-legitima.txt), L10: B ofrece el código; en L7 A ya dijo que no lo pediría. No usar la negativa de L11 para justificar el juicio en L10. | [TR-10](../casos/texto/TR-10-ofrecimiento-inducido.txt), L8: B ya solicitó confirmar lo recibido; L10 dice que lo cargará de su lado y L11 A ofrece leerlo. No descartar esa inducción porque A formule el ofrecimiento. |
| [LG-BANK-VERIF](../casos/texto/LG-BANK-VERIF-01-e01.txt), L2: B expresa su deseo de cambiar la clave; L6: ofrece números. No atribuir esas acciones a una solicitud de A. | [SOPORTE-005](../casos/texto/CV2-D-V-SOPORTE-005.txt), L13: A lee lo que pide una ventana; L14/L16 B confirma la contraseña anterior y L18 ordena ingresarla. La instrucción de B no desaparece porque la clave se escriba o A proponga hacerlo después desde el sitio (L19). |
| [LG-SUPPORT-INFO](../casos/texto/LG-SUPPORT-INFO-01-e01.txt), L4: B relata lo que iba a ofrecer; A ya dijo en L3 que no necesita usuario ni contraseña. | El mismo SOPORTE-005 obliga a distinguir un relato de pantalla de la instrucción posterior del interlocutor. B es quien guía en ese caso: las letras A/B no fijan papeles. |
| [LAB-banco-revisa-app](../casos/texto/LAB-banco-revisa-app.txt), L3: cortar y revisar por cuenta propia; [LAB-arca-canal-oficial](../casos/texto/LAB-arca-canal-oficial.txt), L2–L3: evitar el sitio del mensaje y consultar por cuenta propia. No inventar entrega de claves, dinero o control. | [WHATSAPP-004](../casos/texto/CV2-D-V-WHATSAPP-004.txt), L10–L13: el código de registro termina pedido como «pasámelo» para una planilla del consorcio. La justificación administrativa no elimina la solicitud; tampoco «No, pasámelo» es una negación del pedido. SOPORTE-005 contrasta el consejo con una operación guiada. |
| [BANCO-002](../casos/texto/CV2-D-L-BANCO-002.txt), L7: sí hay un pedido de últimos cuatro dígitos; [TR-13](../casos/texto/TR-13-turno-medico-pide-dni.txt), L5: sí hay un pedido de DNI y fecha de nacimiento. Atribuirlos bien no basta para decidir si permitirían el daño de P0. | [ORGANISMO_PREVISIONAL-004](../casos/texto/CV2-D-V-ORGANISMO_PREVISIONAL-004.txt), L14, pide últimos cuatro y fecha; [PREMIO-003](../casos/texto/CV2-D-V-PREMIO-003.txt), L13/L19, documento y foto como requisito. P1 no añade una exención para trámites ni se anuncia como solución a estas pérdidas/FA. Clase, daño inferible y marcas requieren revisión en D07. |
| [TR-08](../casos/texto/TR-08-frase-cortada-candado.txt), L3: «Pasame el código» todavía no tiene la aclaración de L4. Es un pedido actual con objeto ambiguo. | P1 no agrega espera ni lee L4 al juzgar L3. No se promete resolver la frase incompleta; se conserva como límite de la observación incremental, pendiente de D07/D08. |

El inventario histórico es de 17 cambios de resultado, 17 de momento y 34 solo de
motivo/cita. No demuestra una causa ligada al indicio: las dos condiciones cambian
compuerta e indicio juntos y cortan al primer aviso. Los 150 ya vistos, incluidos
estos 17, sirven para diagnóstico y regresión declarada. No son comprobación
independiente ni se vuelve independiente una subdivisión hecha después de verlos.

## Antecedente: controles antes de una prueba del modelo

**Verificación determinista de este borrador:** igualdad de P0 con ambos
manifiestos y con Git; un único bloque sustituido en P1; resto del prompt y
contrato idénticos; huellas y enlaces relativos. Estas comprobaciones de texto no
miden comprensión, detección ni falsas alarmas.

**Acceso del ejecutor, revisado solo por lectura:** `correr.py:498` llama a
`casos.validar_todos()` antes de seleccionar IDs; esa función llama a
`ids_de_casos()` sin filtro, enumera textos/referencias y consulta el catálogo.
Además, `elegir_casos()` llama a `ids_de_casos(particion=...)`, que lee referencias
antes de filtrar. Pasar `--casos` o `--lista` no evita esos accesos. No se ejecutó
`correr.py`, `casos.py` ni la suite completa en esta copia. La guarda del
comparador no protege al ejecutor. Corregir y comprobar ese acceso con fixtures
sintéticos es un paso previo a usarlo aquí, fuera de este cambio de prompt.

**Propuesta para la comparación posterior, todavía sin ejecutar:**

- Contrastar P0/P1 manteniendo fijos pesos y digest de E2B, parámetros, hablantes,
  prefijos, datos y referencias congelados, política de aviso, recorrido y entorno.
  Mantener SLM solo como control. Registrar los textos y hashes efectivos.
- Coordinar la variante de la otra persona: Tito conserva la compuerta y Gemma
  recibe solo conversación. Su estado sigue en prueba. Dentro de un contraste
  P0/P1 usar el mismo modo de indicio; no comparar P0 con indicio contra P1 sin él
  como efecto del prompt. No cambiar Tito, umbrales, espera ni histéresis aquí.
- Revisar recuperaciones, pérdidas, falsas alarmas nuevas/eliminadas, momento,
  motivo/cita, omisiones y fallos técnicos por separado. Una cita distinta o una
  variación de riesgo no equivale a una recuperación. Una pérdida de alerta
  fundamentada en TR-10/TR-09 sería una regresión relevante aunque bajen las FA.
- Acordar en D07/D08 referencias y desarrollo separado antes de observar nuevas
  respuestas; declarar reutilización de los 150. Si se continúa tras el aviso,
  ejecutar controles con el mismo recorrido: las salidas actuales no permiten
  comparar persistencia. Repeticiones, selección y criterio de aceptación siguen
  pendientes; no se fijan en esta ficha.
- Probar selección/hash de prompts, esquema y ausencia de futuro/referencias en
  la entrada con dobles y fixtures sintéticos antes de una inferencia. Esos tests
  deterministas verifican el ejecutor, no el comportamiento de Gemma.

No se abrió ni enumeró la reserva, no se generó otro corpus y no se entrenó Tito.
No se cambió la demo ni se ejecutó Colab; el notebook actual todavía no ejecuta
la matriz. Adoptar un candidato requerirá evidencia y reconsiderar el
[ADR 0001](../../../docs/ingenieria/adr/0001-parakeet-filtro-y-gemma4-e2b-con-tito-viejo.md).
D09 sigue resuelta; este borrador no decide D07/D08 ni modifica referencias.

## Antecedente: comentario del borrador anterior, reemplazado y sin publicar

```markdown
Avance de #51 — versión 3, candidato P1 de prompt (2026-11-04).

Historial explícito: v1 original (`tarea.txt`), v2 previa (`tarea_v2.txt`)
y v3 actual (`tarea_v3.txt`). V1 y v2 quedan intactas. Las dos corridas de 150
usaron v1; v3 parte de esa base medida, no acumula los cambios de v2.

P0/v1 conservado, idéntico a ambos manifiestos. P1/v3 reemplaza solo
el bloque de mención/pedido por atribución de quién pide qué a quién dentro de
la llamada: relato, hipótesis, ofrecimiento y consejo, con control de inducción
previa y rechazo. Mantiene las seis acciones y el contrato JSON; no está
registrado en el ejecutor ni activado en la demo.

Evidencia: experiments/slm-directo/prompts/V3-ATRIBUCION.md y
experiments/slm-directo/prompts/tarea_v3.txt; bitácora semanal y R05/R07/R27.
Contraste de lectura de IA sobre 17 IDs explícitos de desarrollo, con hashes
verificados; referencias sin revisión humana. Sin acceso a reserva ni inferencia.
Verificaciones deterministas de conservación de P0, sustitución única, contrato,
huellas y enlaces: no son pruebas de calidad del modelo.

Riesgo: suprimir ofrecimientos inducidos o pedidos presentados como trámite;
no se da por resuelto el problema de pedidos administrativos o frases cortadas.
D07/D08 abiertas, D09 resuelta y ADR 0001 vigente.

Próximo paso: revisar P1, coordinar el estado de compuerta sin indicio y preparar
el acceso seguro del ejecutor antes de una comparación P0/P1 con factores fijos.
Los 150 ya vistos son regresión declarada, no comprobación independiente.
#51 sigue abierto; no corresponde Closes en este avance.
```
