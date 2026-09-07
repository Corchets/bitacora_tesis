# Método de creación del corpus

Este documento define quién diseña las llamadas, de dónde salen los diálogos y cómo
se determina la cantidad. El equipo diseña el corpus; los voluntarios interpretan
roles sin memorizar un diálogo completo; el profesor/tutor valida el método antes
de escalar la grabación.

## 1. Unidad del corpus

- **Familia:** modalidad amplia, por ejemplo “banco” o “soporte técnico”.
- **Semilla:** situación concreta, por ejemplo “compra sospechosa y pedido de OTP”.
- **Ficha de rol:** objetivos y límites separados para cada interlocutor.
- **Conversación:** una interpretación particular de una semilla.
- **Turno:** intervención de un hablante con timestamps y etiquetas.

La conversación es la unidad de clasificación. Turnos derivados de la misma
conversación permanecen en el mismo split.

## 2. De dónde salen las llamadas

El equipo construye un catálogo a partir de:

1. modalidades documentadas por organismos oficiales argentinos;
2. tipologías y progresiones descriptas en literatura académica;
3. negativos legítimos diseñados para compartir vocabulario con cada fraude;
4. revisión del profesor/tutor para pertinencia y seguridad.

El catálogo vive en `CATALOGO-ESCENARIOS.csv`. Una modalidad entra al corpus cuando
tiene fuente, acción crítica, evidencia observable y un negativo comparable.

## 3. Cómo se diseña una semilla fraudulenta

Cada semilla especifica:

- identidad que se suplanta;
- pretexto y problema inventado;
- objetivo del atacante;
- maniobras permitidas: autoridad, urgencia, miedo, aislamiento o persistencia;
- solicitud riesgosa objetivo;
- punto `T_R`: comienzo de la solicitud;
- posible punto `T_C`: comienzo de cumplimiento;
- ramas si la otra persona duda, acepta o rechaza;
- datos ficticios que pueden mencionarse;
- condiciones de cierre y debriefing.

La ficha contiene intenciones y restricciones, no frases obligatorias. Así se evita
que todas las conversaciones sean copias léxicas.

## 4. Cómo se diseña el negativo difícil

Por cada grupo de semillas fraudulentas se crea al menos un escenario legítimo con
vocabulario y contexto similares, pero conducta segura.

Ejemplo:

| Fraudulenta | Legítima difícil |
|---|---|
| “Soy del banco; decime el código para bloquear la compra” | “Detectamos una compra; no compartas claves y revisá la app oficial” |

El negativo se acepta cuando contiene señales superficiales —banco, urgencia,
seguridad, dinero— sin solicitud secreta, aislamiento ni canal irregular. Esto evita
un detector que solo aprenda palabras obvias.

## 5. Fichas de rol

### Rol A

- Contexto que debe representar.
- Objetivo conversacional.
- Información ficticia disponible.
- Maniobras o conductas permitidas.
- Respuesta ante aceptación, duda y rechazo.
- Conductas excluidas por seguridad.

### Rol B

- Contexto conocido, sin ver el texto del Rol A.
- Actitud asignada: confiado, dudoso o resistente.
- Preguntas que puede hacer.
- Si corresponde, acción ficticia de cumplimiento.
- Condición de cierre.

Los participantes reciben su propia ficha. Una persona del equipo controla que la
grabación respete el escenario y detiene cualquier uso accidental de datos reales.

## 6. Piloto

1. Crear 4 semillas fraudulentas y 4 legítimas difíciles.
2. Grabar 12–20 conversaciones con integrantes y voluntarios autorizados.
3. Transcribirlas y anotar un subconjunto común entre los cuatro integrantes.
4. Registrar ambigüedades, duraciones, fallas técnicas y tiempo de anotación.
5. Revisar taxonomía, fichas y procedimiento.
6. Presentar resultados al profesor antes de escalar.

**Piloto terminado cuando:** al menos 12 audios son utilizables, cada etiqueta tiene
definición y ejemplo, los desacuerdos principales fueron adjudicados y puede
estimarse el costo de producir/anotar una conversación adicional.

## 7. Cómo se determina el tamaño final

No existe una cifra universal de 120–200 llamadas. Se decide después del piloto
usando diversidad, incertidumbre estadística, curva de aprendizaje y capacidad.

Bandas de planificación:

| Nivel | Conversaciones | Uso |
|---|---:|---|
| Piloto | 12–20 | corregir método; no reportar como evaluación final |
| Mínimo defendible | 60–80 | baselines y evaluación exploratoria con límites explícitos |
| Objetivo | 100–120 | más diversidad y un test menos inestable |
| Extensión | 160–200 | solo si producción y anotación ya son sostenibles |

Después del piloto se estima:

- minutos para grabar, transcribir y anotar una conversación;
- cobertura por familia, semilla, hablante, actitud y condición acústica;
- intervalo de confianza de métricas clave;
- curva de aprendizaje al agregar datos;
- semanas disponibles antes de congelar el test.

**Criterio de parada:** se alcanza al menos el mínimo acordado, cada familia central
tiene cobertura suficiente, existe test independiente, la curva de aprendizaje se
aplana o producir más datos desplaza la integración/evaluación crítica. El número
final y sus límites se documentan; no se inventa una justificación retrospectiva.

## 8. Balance

El 50/50 es una decisión experimental inicial, no una estimación de prevalencia
real. Facilita comparar clases en un corpus pequeño. El test puede incluir 50/50
para medir capacidad discriminativa y una evaluación adicional con menor
prevalencia para observar falsas alarmas.

Las conversaciones fraudulentas y legítimas no se “consiguen”: el equipo las
produce mediante el catálogo y las fichas. Fuentes externas justifican modalidades;
no aportan llamadas listas para usar.

## 9. División de datos

1. Agrupar todas las variantes derivadas de una misma semilla.
2. Distribuir semillas completas entre train, validation y test.
3. Mantener las familias centrales representadas en los tres splits cuando sea
   posible.
4. Reservar hablantes del test si el tamaño lo permite; si no, reportar una segunda
   evaluación speaker-disjoint o la limitación.
5. Congelar el test antes de seleccionar modelo y umbral.

**Split terminado cuando:** ningún audio, turno ni paráfrasis de una semilla cruza
particiones, y un script valida esa condición.

## 10. Control de calidad

Una grabación se acepta cuando:

- existe consentimiento válido;
- usa datos ficticios;
- respeta la ficha sin ser una lectura mecánica;
- ambos lados son inteligibles;
- tiene ID, semilla, hablantes pseudónimos y condición acústica;
- puede anotarse `T_R` y, cuando corresponda, `T_C`;
- no contiene información identificable accidental.

Las exclusiones se registran con motivo; nunca se eliminan silenciosamente para
mejorar métricas.
