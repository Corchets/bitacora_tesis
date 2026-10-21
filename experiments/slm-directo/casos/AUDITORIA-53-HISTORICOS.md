# Auditoría de los 53 casos históricos de desarrollo

> **Estado: propuesta sin discutir.** Auditoría asistida, sin revisión humana. Las
> recomendaciones de criterio dependen de [D07 y D08](../../../docs/gestion/MAPA-DECISIONES.md)
> (taxonomía/evento crítico y composición/política de evaluación), que siguen abiertas.
> Este documento **no modifica** ningún texto ni referencia: los 53 se conservan byte por byte
> para reproducir las corridas históricas.

Alcance: los 53 casos de desarrollo que no son `corpus_v2` (26 `laboratorio`, 14 `piloto_escrito`,
13 `trampa`; 29 vishing, 24 legítimas). Comparados además contra los 97 `corpus_v2` de desarrollo.
No se abrió ningún caso de la reserva (`CV2-T-*`) ni se corrió ningún modelo. Las cifras salen de
leer los textos y de recuentos simples (palabras normalizadas sin tildes, similitud por
`difflib` y Jaccard de n-gramas). Las referencias a líneas son 1-indexadas, como `t_r_linea`.

## 1. Resumen ejecutivo

| Tipo de hallazgo | Hallazgos | Alta | Media | Baja |
|---|---:|---:|---:|---:|
| DUP — duplicados / casi duplicados | 9 | 0 | 4 | 5 |
| COR — guiones cortos / pedido demasiado temprano | 8 | 1 | 3 | 4 |
| FUG — fuga de clase (consejos, metanarración, léxico, sesgo estructural) | 8 | 3 | 4 | 1 |
| ENT — entidades, nombres y datos con forma real | 7 | 0 | 1 | 6 |
| INC — incoherencias texto/referencia | 13 | 1 | 5 | 7 |
| **Total** | **45** | **5** | **17** | **23** |

Lectura corta:

- **Duplicados:** no hay duplicados contra los 97 `corpus_v2` (similitud de tokens máxima 0,21, ninguna línea
  idéntica de 4 o más palabras salvo `1-2-3-4-5-6`). Dentro de los 53 sí hay **conjuntos que son la misma
  situación**: 6 pares original/paráfrasis en `laboratorio` y 4 familias temáticas. Los 53 equivalen a
  unas 35 situaciones distintas, no a 53 observaciones independientes.
- **Guiones cortos:** `laboratorio` son 26 guiones de 2 a 7 líneas (14 a 57 palabras). En 10 de los 16
  vishing de `laboratorio` el pedido llega en la línea 3 de 5, con 8 a 19 palabras previas (mediana de
  los 16: 16,5 palabras). Eso casi no deja margen para una alerta *antes* del pedido.
- **Fuga de clase:** no aparecen «estafa», «fraude» ni «nunca te pedimos», pero las legítimas llevan el
  consejo de seguridad: 9 de 10 legítimas de `laboratorio` y 7 de 7 del piloto contienen
  advertencias («no hace falta», «ningún banco te pide», «cortá y llamá vos»). El vishing casi no.
  Además hay tres confusores estructurales: estilo (sin tildes ni puntuación en `laboratorio`), longitud
  y letra del hablante que pide.
- **Entidades:** no hay bancos, teléfonos, CBU, enlaces ni DNI reales. Hay marcas/organismos reales
  (ANSES, WhatsApp, «clave fiscal») y 15 nombres completos corrientes; riesgo de privacidad bajo, riesgo
  de sesgo léxico medio solo para «anses» (token que aparece únicamente en vishing).
- **Referencias:** `t_r_linea`, `t_c_linea` y `pedido` son consistentes con la evidencia en los 29
  vishing (primer evento `pedido` = `t_r_linea`; primer `cumplimiento` = `t_c_linea`; `t_c` > `t_r`).
  Las discrepancias son de criterio de anotación (ver sección 3, INC). Los 53 tienen
  `revision_humana: false`.

### Los 5 hallazgos más graves

1. **FUG-04 / FUG-01 / FUG-02 — La clase se puede adivinar por el consejo de seguridad.** «cortá/corto»
   aparece en 12 de 24 legítimas y en 5 de 29 vishing; «no hace falta», «no pido/pedimos», «nadie», «ningún»,
   «oficial» y «tampoco» son casi exclusivos de las legítimas; «no cortes / no llames / no avises» aparece en
   7 de 29 vishing y en 0 de 24 legítimas.
2. **COR-05 — Pedido en la línea 3 de 5 en 10 vishing de `laboratorio`.** Solo 2 turnos de contexto. No prueba
   comportamiento incremental ni margen de anticipación.
3. **DUP-01 a DUP-04 — Casos no independientes.** 12 casos son 6 situaciones (original + paráfrasis) y otros
   9 repiten 3 familias. Inflan los conteos y, si el corte entrena/valida o se resume por caso, sesgan los
   promedios.
4. **FUG-07 / FUG-08 — Confusores estructurales.** `laboratorio` (26 casos) está en minúsculas, sin tildes ni
   puntuación y con 5 líneas de mediana; el resto usa puntuación y 12 líneas. Además en los 16 vishing de
   `laboratorio` el pedido lo dice la letra `A`.
5. **INC-01 — `LAB-familiar-peligro-parafrasis`: `t_r_linea = 4` con `REQUEST_TRANSFER` para un pedido de efectivo
   en mano** («trae diez mil pesos a la plaza»); la transferencia propiamente dicha recién está en la línea 6.

## 2. Método y recuentos de apoyo

- Longitud: mediana por grupo y clase.

| Grupo / clase | Casos | Líneas (mediana) | Palabras (mediana; mín–máx) |
|---|---:|---:|---|
| laboratorio / vishing | 16 | 5 | 40,5 (29–57) |
| laboratorio / legítima | 10 | 5 | 29,5 (14–40) |
| piloto_escrito / vishing | 7 | 13 | 212 (46–233) |
| piloto_escrito / legítima | 7 | 12 | 209 (40–260) |
| trampa / vishing | 6 | 12 | 143 (123–427) |
| trampa / legítima | 7 | 10 | 137 (62–303) |
| `corpus_v2` desarrollo (97) | 97 | 24 | 254 |

- Palabras antes del pedido (hasta `t_r_linea - 1`), vishing con pedido: `laboratorio` mediana 16,5 (16 casos);
  `SC-*` mediana 97 (7); `TR-*` mediana 74 (5). Con 2 turnos posteriores al pedido en todo `laboratorio`.
- Palabras más asociadas por clase (apariciones por caso, vishing/legítima, solo con ≥4 casos):
  - Legítimas: «algo» 0/8, «corta» 0/8, «falta» 0/6, «pedir» 0/6, «oficial» 0/5, «tampoco» 0/4, «revisa» 0/4,
    «nos» 0/4, «gracias» 2/9, «aplicación» 3/9, «datos» 1/5.
  - Vishing: «hablo» 12/1, «soy» 15/2, «habla» 11/2, «cuenta» 12/3, «necesito» 7/2, «soporte» 4/1, «freno» 4/1,
    «sistema» 5/1, «área» 5/1, «minutos» 5/1, «lado» 6/1, «pasame» 6/1, «cortes» 5/0, «débito» 4/0, «cae» 4/0;
    números en letra («cero» 6/1, «cuatro» 6/1, «seis» 9/1, «uno» 11/2, «nueve» 4/0) por las líneas de cumplimiento.
- Patrones de seguridad (casos con al menos una línea): «nunca» 0/29 vs 2/24; «ningún» 0/29 vs 3/24;
  «página/aplicación oficial» 0/29 vs 5/24; «corta/corto/cortá» 5/29 vs 12/24; «no cortes/llames/avises/le digas»
  7/29 vs 0/24. Heurística con regex amplia sobre `laboratorio`: 9 de 10 legítimas la activan contra 5 de 16 vishing.
  «estafa», «fraude» y «nunca te pedimos»: 0 apariciones.
- Similitud: pares con mayor `SequenceMatcher` entre los 53: `LAB-anses-beneficio` y su paráfrasis 0,50;
  `LAB-banco-codigo` y su paráfrasis 0,43; `LAB-acceso-remoto` y su paráfrasis 0,39;
  `LAB-familiar-peligro-parafrasis` y `LAB-giro-sin-plata` 0,38; `LAB-banco-codigo` y `LAB-digitos-sin-palabra` 0,37.
  Contra `corpus_v2`: máximo 0,21 (`SC-PREMIO-01-e01` con `CV2-D-V-PREMIO-001`).

## 3. Tabla de hallazgos

Severidad: **alta** = puede invalidar o sesgar conclusiones si se usa el conjunto como está; **media** = distorsiona
una métrica o dificulta la lectura; **baja** = nota de limitación.
Las recomendaciones son propuestas sin discutir salvo que se diga lo contrario.

### 3.1 DUP — duplicados y casi duplicados

| ID | case_id | Línea | Cita corta | Sev. | Recomendación |
|---|---|---|---|---|---|
| DUP-01 | `LAB-acceso-remoto` / `-parafrasis`; `LAB-anses-beneficio` / `-parafrasis`; `LAB-arca-deuda` / `-parafrasis`; `LAB-banco-codigo` / `-parafrasis`; `LAB-familiar-peligro` / `-parafrasis`; `LAB-whatsapp-codigo` / `-parafrasis` | todas | misma secuencia, mismo `t_r_linea` y `pedido` en cada pareja | media | Mismo guion reescrito: son 6 situaciones en 12 casos. Reportar métricas agrupando por situación (o aclarar «12 casos, 6 situaciones») y no repartir pares entre entrenamiento y validación. |
| DUP-02 | `LAB-giro-sin-plata`, `LAB-familiar-peligro`, `LAB-familiar-peligro-parafrasis` | 1-3 | «habla un amigo de tu hermano, tuvo un accidente» / «amigo de tu hijo tuvo un accidente»; diez mil, alias/cuenta | media | Misma situación (falso accidente de familiar con pedido de diez mil): tratarlos como una familia de 3. `SC-FAMILIAR-DINERO-01-e01` y `TR-12` son variantes del mismo fraude con más texto. |
| DUP-03 | `LAB-banco-codigo`, `LAB-banco-codigo-parafrasis`, `LAB-banco-numeros-sin-clave`, `LAB-digitos-sin-palabra` | 1-5 | «consumo/gasto que no reconocemos» → «código/seis números/lo que te llegó» | media | Cuatro casos, una situación con variantes de léxico. `LAB-digitos-sin-palabra` es una variante deliberada (sin la palabra «código»): conservarla pero contarla dentro de la familia. `TR-01` y `TR-09` repiten el motivo con más texto. |
| DUP-04 | `LAB-whatsapp-codigo`, `LAB-whatsapp-codigo-parafrasis`, `SC-WA-CODE-01-e01` | 1-4 | «soporte de whatsapp… código de verificación… pasamelo» | media | Tres versiones de «soporte pide el código de WhatsApp». `TR-10` también. Contar como familia. |
| DUP-05 | `LAB-acceso-remoto`, `LAB-acceso-remoto-parafrasis`, `LAB-pantalla-sin-programa` | 1-3 | «débito duplicado» / «instalá el programa y mostrame la pantalla» | baja | Misma situación; con `SC-SOPORTE-REMOTO-01-e01` son 4 de «acceso remoto». |
| DUP-06 | `LAB-banco-revisa-app` y `LAB-banco-app-parafrasis` | 1-5 | «corta… entrá vos a la aplicación» | baja | Misma situación legítima con roles invertidos. La «paráfrasis» no tiene un original exacto en el conjunto (ver INC-10). Además `LAB-anses-canal-oficial`, `LAB-arca-canal-oficial`, `LAB-banco-niega-el-codigo`, `LAB-no-bajes-nada`, `LAB-mensajeria-no-pases-nada` repiten la plantilla «alguien relata, otro aconseja cortar y usar el canal oficial» (7 de 10 legítimas de `laboratorio`). Sin acción sobre los textos: es una limitación de variedad. |
| DUP-07 | pares `LG-*` ↔ `SC-*` (7) y `TR-07` ↔ `TR-08` | todas | mismas frases («cuarenta mil pesos», «jubilados que cobran la mínima», «Pasame el código / del candado…») | baja | Son pares contrastivos de diseño, no duplicados a eliminar. Mantenerlos juntos al partir datos. `LG-SUPPORT-INFO-01-e01` y `-e02` comparten número base y tienen pares `SC-*` distintos: cuidado al derivar la semilla desde el nombre. |
| DUP-08 | los 53 contra los 97 `corpus_v2` | — | máximo 0,21 de similitud de tokens; 2-gramas Jaccard ≤ 0,06 | baja | Sin duplicados. Solapamiento solo temático: `SC-PREMIO-01-e01` ↔ `CV2-D-V-PREMIO-001` (premio + dato personal), `SC-ORG-BENEFICIO-01-e01` ↔ familia ORGANISMO_PREVISIONAL. |
| DUP-09 | `TR-04-pedido-tras-charla-larga`, `TR-10-ofrecimiento-inducido`, `SC-WA-CODE-01-e01`, `TR-07`, `TR-02` | 27 / 13 / 5 / 9 / 4 | «Es uno, dos, tres, cuatro, cinco, seis» (idéntica en TR-04 L27 y TR-10 L13); «cero, cero, cero, cero, cero, cero» (SC-WA-CODE L5, TR-07 L9) | baja | Códigos de relleno repetidos. Inofensivo para el detector, pero la secuencia `123456` / `000000` es una pista memorizable: preferir códigos variados en corpus futuros. |

### 3.2 COR — guiones cortos y pedido temprano

| ID | case_id | Línea | Cita corta | Sev. | Recomendación |
|---|---|---|---|---|---|
| COR-01 | `LAB-banco-niega-el-codigo` | 1-2 | «ningun banco te pide el codigo por telefono» / «corta y revisa la aplicacion oficial» | media | 2 líneas, 14 palabras, un solo hablante y sin interlocutor: no es una conversación ni prueba nada incremental (solo «mención sin pedido»). Reportarla aparte o excluirla de métricas de latencia. |
| COR-02 | `LAB-portero-codigo-puerta` | 1-2 | «el portero me paso el codigo de la puerta» | media | 2 líneas, 19 palabras; sirve como mención cotidiana, no como prueba de contexto acumulado. |
| COR-03 | `LAB-banco-gasto-sin-pedido` | 1-3 | «te llama el banco porque vimos un gasto…» | baja | 3 líneas, B nunca habla; inicio idéntico a un vishing y luego «no hagas nada por telefono». Útil como par mínimo, no como diálogo. |
| COR-04 | `LAB-no-bajes-nada`, `LG-WA-CONSULTA-01-e01` | 1-4 | 30 y 40 palabras | baja | Muy cortos para medir incrementalidad; agruparlos con los «cortos» al reportar. |
| COR-05 | `LAB-acceso-remoto`, `-parafrasis`, `LAB-anses-beneficio`, `-parafrasis`, `LAB-arca-deuda`, `-parafrasis`, `LAB-giro-sin-plata`, `LAB-pantalla-sin-programa`, `LAB-whatsapp-codigo`, `-parafrasis` | 3 de 5 | p. ej. `LAB-pantalla-sin-programa` L3 «bajate este programita…» con 8 palabras previas | **alta** | 10 vishing con `t_r_linea = 3` de 5, 2 turnos de contexto (8 a 19 palabras) y 2 de continuación. Tres más tienen `t_r_linea` 4-5 de 6-7. Con tan poco contexto, «avisar antes del pedido» depende de la primera línea. Propuesta sin discutir: informar `Preventive` por separado para `laboratorio` y para casos con ≥ 60 palabras antes del pedido ([D08](../../../docs/gestion/MAPA-DECISIONES.md)). |
| COR-06 | `LAB-digitos-sin-palabra` | 5 | «leeme lo que te acaba de llegar al telefono, de a uno» | baja | El pedido es la última línea (`t_r_linea = 5 = n`), sin `t_c_linea`: sirve para ver si hay aviso antes, no la reacción tras el pedido. |
| COR-07 | `SC-WA-CODE-01-e01` | 4 | «Decime el código de activación que recibiste por SMS.» | media | 5 líneas, 30 palabras previas: pedido directo a la 4.ª línea, en un caso del piloto. Es el contrapunto corto de su par `LG-WA-CONSULTA-01-e01`. |
| COR-08 | `TR-04-pedido-tras-charla-larga`, `TR-05-asado-con-transferencia` | 26 / 27 | 30 y 27 líneas; pedido en la línea 26 | baja | Únicos casos de más de 15 líneas entre los 53; intencionales (pedido tardío, falso positivo largo). Muy lejos del resto (mediana 5 a 12): no comparar sus latencias con las del resto sin separar. |

### 3.3 FUG — frases y estructuras que regalan la clase

| ID | case_id | Línea | Cita corta | Sev. | Recomendación |
|---|---|---|---|---|---|
| FUG-01 | `LAB-banco-niega-el-codigo`, `LAB-familiar-llama-vos`, `LAB-mensajeria-no-pases-nada`, `LAB-no-bajes-nada`, `LAB-anses-canal-oficial`, `LAB-arca-canal-oficial`, `LAB-banco-revisa-app`, `LAB-banco-app-parafrasis`, `LAB-portero-codigo-puerta` | 1-4 | «ningun banco te pide el codigo por telefono» (L1); «no bajes nada» (L2); «llama vos al numero que tenes guardado» (L3); «no abras ningun sitio del mensaje» (L2); «no se lo des a nadie» (L2) | **alta** | 9 de 10 legítimas de `laboratorio` son consejos de seguridad. Un clasificador (o un modelo) puede responder «legítima» por el consejo, no por el contexto. Los 53 no se tocan; para validación futura, propuesta sin discutir: balancear legítimas con y sin consejo ([D08](../../../docs/gestion/MAPA-DECISIONES.md)) y cargar ese rasgo en las notas. |
| FUG-02 | `LG-BANK-VERIF-01-e01` L5, L7, L9; `LG-ORG-TURNO-01-e01` L5, L7, L11; `LG-PREMIO-CONSULTA-01-e01` L5, L7; `LG-SUPPORT-INFO-01-e01` L3, L5, L9, L11; `LG-SUPPORT-INFO-01-e02` L4, L12; `LG-WA-CONSULTA-01-e01` L2, L4 | varias | «tampoco te voy a pedir la clave» (BANK L7); «Por teléfono no pedimos fotos del documento, claves ni datos del banco» (ORG L5); «Nosotros no llamamos para avisar ni pedimos datos por teléfono» (PREMIO L5); «No me lo leas ni lo compartas» (WA L2) | **alta** | Las 7 legítimas del piloto repiten, en una línea, la prohibición que viola su par vishing. Es útil para probar «negación», pero entrega la clase en una sola línea. El vishing correspondiente casi no tiene esos giros. Registrar como limitación al interpretar resultados en `LG-*`. |
| FUG-03 | `TR-03-negacion-y-consejo` L2, L4, L6, L8; `TR-06-banco-alerta-legitima` L7, L11 | 2-11 | «nunca le pases la clave del banco a nadie» (TR-03 L2); «ese código no se comparte con nadie, tampoco con el banco» (TR-06 L11) | media | Trampas hechas a propósito para medir si «mención ≠ pedido». Conviene no mezclar su tasa de falsos positivos con la de legítimas sin consejo. |
| FUG-04 | los 53 | — | «corta/corto/cortá» 12/24 legítimas vs 5/29 vishing; «no cortes / no llames / no avises / no le cuentes» 7/29 vs 0/24; «oficial» 0 vs 5; «nunca/ningún» 0 vs 5; «tampoco», «revisa», «algo», «falta» solo legítimas; «soporte», «freno», «sistema», «área», «minutos» casi solo vishing | **alta** | Desbalance léxico medible. En el vishing, la presión se dice con «no cortes» y el contrario con «cortá». No es una fuga literal («estafa», «fraude» no aparecen), pero sí un atajo. Propuesta sin discutir: reportar un baseline léxico (bolsa de palabras) sobre estos 53 como cota de lo que se puede acertar sin entender el contexto. |
| FUG-05 | `LAB-banco-revisa-app` L4-5; `LAB-banco-app-parafrasis` L5; `TR-01` L9-10; `TR-11` L7; `LAB-banco-gasto-sin-pedido` L2 | varias | «no me vas a pedir nada no» / «exacto yo no te pido datos corta y revisa ahi» (L4-5); «buenisimo era mentira entonces» (L5); «Eso viene en todos los mensajes, es automático» (TR-01 L10); «con todo lo que se escucha» (TR-11 L7) | media | Metanarración: los hablantes comentan el riesgo del propio llamado. En `TR-01` L10 es una táctica creíble del estafador y está bien; en las legítimas del laboratorio es el narrador cerrando la moraleja. |
| FUG-06 | `LAB-banco-codigo`, `-parafrasis`, `LAB-banco-numeros-sin-clave`, `LAB-whatsapp-codigo`, `-parafrasis`, `SC-WA-CODE-01-e01`, `TR-*` | cumplimiento | «cero, cuatro, seis, nueve» en letra | baja | Los números dictados en letra casi solo existen en el vishing (la excepción son `TR-02` y `TR-08`). Aparecen después del pedido, por lo que no regalan `T_R`, pero sí empujan el veredicto de clase al leer el caso completo. |
| FUG-07 | los 26 `LAB-*` | todas | minúsculas, sin tildes ni puntuación («te llama la tarjeta hay un debito duplicado») | media | Estilo propio de `laboratorio` (estilo ASR del guion original) frente a texto con tildes en el resto. La clase está repartida (16 vishing, 10 legítimas), pero longitud y estilo son confusores de grupo: un resultado en `LAB-*` no se extrapola a texto puntuado. Informar por grupo. |
| FUG-08 | 16 `LAB-*` vishing | línea de `t_r_linea` | el pedido lo dice `A` en 16 de 16 | media | Con `--hablantes` activo, la letra A coincide con «quien pide» en todo `laboratorio` vishing. En las legítimas de `laboratorio`, `A` suele ser quien relata o el interlocutor. En el piloto el pedido lo dice B en 2 de 7 y en `TR` en 1 de 6. Informar resultados con y sin `--hablantes` y no sacar conclusiones de `--hablantes` en `laboratorio`. |

### 3.4 ENT — entidades, personas, teléfonos, marcas

No se encontraron nombres de bancos, números de teléfono, CBU/CVU, DNI, URL ni cuentas reales. Hallazgos:

| ID | case_id | Línea | Cita corta | Sev. | Recomendación |
|---|---|---|---|---|---|
| ENT-01 | `LAB-anses-beneficio`, `LAB-anses-beneficio-parafrasis` | 1 | «hablo de anses…» / «te hablo de anses…» | media | Organismo público real, citado solo en vishing (2/0 legítimas: la gemela legítima dice «el organismo»). El token «anses» se vuelve señal de clase. Sin riesgo de privacidad (no hay persona), pero sí de sesgo léxico. En corpus futuro usar la entidad en ambas clases o en ninguna. |
| ENT-02 | `LAB-whatsapp-codigo` L1, `SC-WA-CODE-01-e01` L1, `TR-10` L4, `SC-PREMIO-01-e01` L8; `LG-PREMIO-CONSULTA-01-e01` L7, `LG-WA-CONSULTA-01-e01` L1 | — | «soporte de whatsapp», «por WhatsApp a este mismo número» | baja | Marca real en ambas clases (4 vishing, 2 legítimas). Es un nombre de uso general; sin problema de privacidad. Las paráfrasis usan «soporte de mensajes»/«aplicación de mensajes». |
| ENT-03 | `LAB-arca-*` (ids) | id | `LAB-arca-canal-oficial`, `LAB-arca-deuda` | baja | El id nombra ARCA, el texto no («el fisco», «inspector», «clave fiscal»). Sin acción. |
| ENT-04 | `LAB-arca-deuda` L3; `LAB-anses-beneficio` L3; `LAB-arca-deuda-parafrasis` L3, L5 | 3, 5 | «clave fiscal», «clave de la seguridad social y el cbu», «homebanking», «cbu» | baja | Vocabulario institucional argentino real, sin datos. Mantener. |
| ENT-05 | 15 casos con nombre y apellido | — | Raúl Quiroga, Elena Ríos, Daniel Ferreyra, Norma Villegas, Javier Ledesma, Laura Domínguez, Hernán Ibarra, Mariela Sosa, Rubén Aguirre, Nicolás Peralta, Julieta Medina, Sergio Paz, Marta Giménez, Julián Paredes, Graciela Funes | baja | Nombres corrientes, inventados; podrían coincidir con personas reales. Sin acción sobre los 53; mantener la regla de datos ficticios. Solo el vishing del piloto y las trampas usan nombre completo de víctima y de personal: ver si el uso del nombre completo del receptor al inicio es un rasgo de clase (aparece en `SC-*`, `TR-01`, `TR-04`, `TR-07`, `TR-09`, `TR-10`; en las legítimas solo en `TR-06` y `TR-13`). |
| ENT-06 | `SC-ORG-BENEFICIO-01-e01` L8; `TR-13-turno-medico-pide-dni` L6; `SC-SOPORTE-CLAVE-01-e01` L11, L13; `TR-04` L3, L21 | varias | «Nací el doce de mayo del cincuenta y uno, y vivo en Los Aromos cuatrocientos veinte»; DNI «doce millones trescientos cuarenta y cinco mil seiscientos setenta y ocho»; «laura punto prueba» / «Prueba uno, dos, tres, cuatro»; «calle Las Acacias» | baja | Datos con forma de datos personales, evidentemente ficticios (`12.345.678`, credencial «prueba»). Aceptable. Si en el futuro se graban en audio, no usar datos de personas reales. |
| ENT-07 | `TR-10` L2 «Julián Paredes»; `LG-FAMILIAR-LLAMADO-01-e01`, `SC-FAMILIAR-DINERO-01-e01`, `TR-05` «Nico/Nicolás»; `TR-05` «Lucho»; `TR-04` «Rubén»; `LG-ORG-TURNO` «Sofía» | — | «Julián Paredes» también es nombre en `CV2-D-L-PREMIO-001` L7 (una legítima); «Lucho» está en `CV2-D-V-FAMILIAR-003`; «Rubén» en `CV2-D-V-FAMILIAR-005`; «Nicolás» (empleado del banco) en `CV2-D-V-BANCO-005` | baja | El mismo nombre completo sirve de víctima en un vishing y de nombre en una legítima de v2. No hay fuga entre conjuntos, pero conviene diversificar nombres al generar casos. |

### 3.5 INC — incoherencias entre texto y referencia

Chequeo automático sobre los 29 vishing: `t_r_linea` coincide con el primer evento `pedido`; la etiqueta `pedido`
está en esa línea; `t_c_linea` coincide con el primer `cumplimiento`; `t_c_linea` > `t_r_linea`; las 24
legítimas tienen `t_r_linea`, `t_c_linea` y `pedido` en `null`. Todas las líneas de evidencia están dentro del
rango. Lo que sigue son discrepancias de criterio.

| ID | case_id | Línea | Cita corta | Sev. | Recomendación |
|---|---|---|---|---|---|
| INC-01 | `LAB-familiar-peligro-parafrasis` | 4 (y 6) | L4 «trae diez mil pesos a la plaza ahora» con `REQUEST_TRANSFER`; L6 «bueno transferime a este alias entonces» | **alta** | `t_r_linea = 4` etiquetado como transferencia, pero es un pedido de efectivo en mano; la transferencia es L6. Según el criterio de `T_R` (primer pedido de dinero vs primera `REQUEST_TRANSFER` literal) el valor cambia de 4 a 6. No tocar el archivo. Propuesta sin discutir: decidir en [D07](../../../docs/gestion/MAPA-DECISIONES.md) si la entrega física de dinero entra en `REQUEST_TRANSFER`. |
| INC-02 | `LAB-familiar-peligro` vs `-parafrasis` | 6 | «entonces pasame el alias ahora» | media | En el original L6 es `contexto` (`PERSISTENCE_DISTRACTION`); en la paráfrasis es `pedido`. Misma situación, anotación distinta. Documentar. |
| INC-03 | `LAB-arca-deuda` | 3, 5 | L3 «tiene que autorizar con su clave fiscal o transferir hoy»; L5 «entonces pasame el alias para frenar el embargo» | media | L3 reúne `REQUEST_TRANSFER`, `REQUEST_SECRET`, `REQUEST_SECURITY_ACTION` y `URGENCY_PRESSURE`; el `pedido` principal es `REQUEST_TRANSFER`, aunque lo primero que se pide es la clave. L5 es un segundo pedido anotado como `contexto`. Sin impacto en `T_R`; sí en cualquier métrica por tipo de pedido. |
| INC-04 | `LAB-arca-deuda-parafrasis` | 3, 5 | L3 «regularice hoy con su homebanking o le embargo la cuenta»; L5 «deme el cbu» | baja | L3 es una orden de pago con amenaza anotada como `REQUEST_TRANSFER`; L5 pide un dato (CBU) y no tiene etiqueta de pedido. |
| INC-05 | `SC-SOPORTE-CLAVE-01-e01` | 6, 11, 13 | L6 pide usuario y contraseña; L11 «El usuario es laura punto prueba»; L13 «Prueba uno, dos, tres, cuatro» | media | `t_c_linea = 11` es la entrega del **usuario**; el secreto (`REQUEST_SECRET`) recién se cumple en L13. Si `T_C` mide la entrega de lo sensible, correspondería 13. Criterio de D07 (cumplimiento parcial). |
| INC-06 | `SC-CLAVE-CAMBIO-01-e01` | 9, 11, 12 | L9 «Abrilo y cambiá la clave ahí»; L11 «Poné tu usuario, la clave que usás ahora y después la nueva» | baja | El pedido real de credenciales (L11) se anota otra vez como `REQUEST_SECURITY_ACTION`, no como `REQUEST_SECRET`. |
| INC-07 | `TR-10-ofrecimiento-inducido` | 8, 10, 11 | L8 «necesito que me confirmes lo que te mandamos» | baja | `T_R = 8` es un pedido indirecto: la palabra «código» solo aparece en L11, dicha por la víctima. Anotación defendible; es justo el punto del caso. Documentar para quien compare con `TR-01` (L8 «leeme lo que dice»). |
| INC-08 | `TR-05` L13, `TR-11` L4, `TR-13` L5 | 13 / 4 / 5 | «pasámelos por transferencia antes del viernes»; «¿Me podrás transferir veinte mil pesos?»; «Decime tu número de documento y la fecha de nacimiento» | media | Legítimas con `pedido: null` pero con una etiqueta `REQUEST_*` en la evidencia (evento `contexto`). Si algún consumidor cuenta etiquetas `REQUEST_*` sin mirar la clase, genera positivos falsos. Otras legítimas con un pedido normal no llevan esa etiqueta (`LG-ORG-TURNO` L10). Propuesta sin discutir: en D07 fijar si las legítimas con pedido razonable llevan la etiqueta. |
| INC-09 | `LG-FAMILIAR-LLAMADO-01-e01` L2, `SC-FAMILIAR-DINERO-01-e01` L4, `TR-11` L2, `TR-12` L4, `LAB-giro-sin-plata` L1 | — | «Hola, tía, soy Nicolás»; «Hola, má. ¿Te agarro en mal momento?»; «habla un amigo de tu hermano» | baja | `AUTHORITY_CLAIM` se usa para identificarse como familiar o conocido, no como autoridad. En `TR-11` L2 ni siquiera hay un claim. Inconsistencia de la taxonomía (D07). |
| INC-10 | `LAB-banco-revisa-app` L5; `LAB-banco-app-parafrasis` | 5 | «exacto yo no te pido datos»; «buenisimo era mentira entonces» | baja | L5 de `revisa-app` está como `rechazo` aunque nadie rechaza un pedido (es una aclaración). `LAB-banco-app-parafrasis` no tiene original: los roles y el contenido difieren de `revisa-app`, y L2 no tiene evidencia anotada. |
| INC-11 | `TR-04-pedido-tras-charla-larga` | 5, 21 | L21 «Me figura el domicilio de la calle Las Acacias, ¿seguís ahí?» | baja | Confirmación de domicilio anotada como `TRUST_BUILDING`; es un pedido leve de dato personal. L5 (recambio de tarjetas) no tiene anotación. `T_R = 26` sigue siendo defendible. |
| INC-12 | `TR-12-corta-antes-del-pedido` | — | clase vishing, `t_r_linea`/`t_c_linea`/`pedido` = `null` | baja | Vishing sin pedido: `resumen.py` ya lo contempla («vishing sin aviso»). Es el único de los 53 en esa situación; no permite medir `Preventive` contra un `T_R`. |
| INC-13 | los 53 | — | `revision_humana: false` en todos; `LAB-*` convertidos «sin cambiar el texto» | media | Ninguna referencia tiene revisión humana: las notas de anotación de los 53 son del equipo asistido. Antes de citar métricas de latencia en la tesis, hacer una pasada humana sobre `t_r_linea`/`t_c_linea` (INC-01, INC-05) según D07. |

## 4. Recomendaciones

> **Estado: propuesta sin discutir.** Ninguna cambia los 53; todas dependen de decisiones abiertas
> ([D07](../../../docs/gestion/MAPA-DECISIONES.md), [D08](../../../docs/gestion/MAPA-DECISIONES.md)).

1. **Conservar los 53 tal cual** (reproducibilidad de corridas) y tratarlos como *conjunto de desarrollo
   exploratorio*, no como evidencia de generalización.
2. **Agrupar por situación al reportar** (DUP-01 a DUP-05): los 53 son unas 35 situaciones. Si hay
   validación cruzada o particiones, partir por `semilla`/familia, no por caso.
3. **Separar los informes por grupo** (`laboratorio` / `piloto_escrito` / `trampa`) por estilo, longitud y
   latencia de pedido (COR-05, FUG-07, FUG-08), y reportar el efecto de `--hablantes` por separado.
4. **Medir el atajo léxico**: correr una bolsa de palabras trivial sobre los 53 (sin modelo de lenguaje)
   como línea base, para saber cuánto se acierta sin entender el pedido (FUG-04).
5. **Balance de consejos en corpus nuevo**: incluir legítimas sin ningún consejo y vishing con
   advertencias dichas por la víctima (como `SC-SOPORTE-CLAVE`, `TR-09`); verificar que «cortá»/«no cortes» no
   separe las clases (FUG-01, FUG-02, FUG-04). `corpus_v2` ya agrega 97 casos más largos; falta medir si
   mantiene el desbalance.
6. **Criterios de anotación para D07**: pedido de efectivo en mano (INC-01), cumplimiento parcial (INC-05),
   etiqueta `REQUEST_*` en legítimas (INC-08), uso de `AUTHORITY_CLAIM` para identidad familiar (INC-09).
   Pasada humana sobre `t_r_linea`/`t_c_linea` de los casos señalados antes de usarlos en la tesis.
7. **Entidades**: en material nuevo, usar las entidades reales (ANSES, WhatsApp) en ambas clases o en
   ninguna (ENT-01), diversificar nombres y códigos (ENT-07, DUP-09); no usar datos de personas reales.
8. **Excluir o reportar aparte** los guiones de 2 a 4 líneas (COR-01 a COR-04) en métricas de latencia,
   y los dos casos largos `TR-04`/`TR-05` (COR-08).
9. **Cierre**: nada de lo anterior requiere editar los 53. Si D08 decide excluir algunos, hacerlo con una
   lista en el análisis, no borrando archivos.

## 5. Reproducibilidad

Los recuentos se obtuvieron con scripts descartables sobre `casos.ids_de_casos('desarrollo')` filtrando
`casos.cargar_referencia(id)['grupo'] != 'corpus_v2'`; no se guardaron scripts. Para repetirlos: normalizar
(minúsculas, sin tildes), contar palabras por caso (presencia, no frecuencia) y calcular el log-odds por clase;
similitud con `difflib.SequenceMatcher` sobre tokens y Jaccard de 2/3-gramas. No se leyó ningún caso de la
reserva ni se ejecutó ningún modelo.
