# Plan provisional de participantes y corpus

**Estado:** borrador para aprobación del profesor/tutor antes de grabar  
**Principio:** conversaciones simuladas con datos ficticios; no llamadas reales de
víctimas ni contacto encubierto con instituciones o presuntos estafadores

## Quiénes serían los participantes

Personas adultas voluntarias que actuarán roles de interlocutor fraudulento,
interlocutor legítimo y usuario. Pueden incluir:

- los cuatro integrantes del equipo para pruebas técnicas iniciales;
- compañeros, familiares o conocidos mayores de 18 años para el corpus piloto y
  principal;
- voces de diferentes géneros, edades adultas, ritmos y acentos, sin afirmar que la
  muestra representa a toda Argentina.

No hace falta reclutar víctimas reales ni adultos mayores para entrenar el detector.
Una eventual prueba de comprensión de warnings con adultos mayores sería un estudio
separado, pequeño y opcional, con protocolo específico.

## Escala propuesta

### Piloto — septiembre

- 6–10 hablantes adultos, incluyendo al equipo.
- 12–20 conversaciones de 2–4 minutos.
- Balance aproximado entre vishing y llamadas legítimas difíciles.
- Todos los integrantes anotan un subconjunto común de 10 conversaciones.

El piloto sirve para corregir los guiones, la grabación y el manual. No se usa para
prometer métricas finales.

### Corpus posterior al piloto — octubre

- Mínimo defendible provisional: 60–80 conversaciones.
- Objetivo provisional: 100–120 conversaciones.
- Extensión: 160–200 solo si grabación y anotación ya son sostenibles.
- Balance experimental inicial aproximado entre fraudulentas y legítimas difíciles.
- Cantidad de hablantes y horas definida después de medir el piloto.

Es preferible un corpus menor, variado y bien separado que cientos de lecturas del
mismo libreto. Si la recolección es lenta, se reduce la cantidad de familias sin
debilitar el test ni la documentación.

La cantidad final no se decide por intuición. El método, las bandas y el criterio de
parada están en [METODO-CREACION-CORPUS.md](METODO-CREACION-CORPUS.md).

## Cómo se producirán las conversaciones

- Fichas de rol semi-estructuradas, no guiones leídos palabra por palabra.
- Cada rol conoce sus objetivos, pero no la redacción exacta del otro.
- Identidades, DNI, tarjetas, cuentas, direcciones, códigos y montos son ficticios.
- El atacante puede insistir o adaptar su discurso dentro de límites definidos.
- Las llamadas legítimas deben incluir vocabulario difícil: banco, compra
  sospechosa, urgencia o soporte, pero sin pedir secretos ni acciones peligrosas.
- Grabar condiciones limpias y algunas variantes con ruido/compresión controlados.

## Familias iniciales

### Vishing

1. Banco: compra sospechosa y pedido de código.
2. Banco: cuenta comprometida y transferencia a “cuenta segura”.
3. WhatsApp: código de activación.
4. Billetera digital: token o credenciales.
5. ANSES/PAMI/obra social: datos personales o bancarios.
6. Soporte técnico: instalar acceso remoto o compartir pantalla.
7. Familiar en emergencia: transferencia urgente.
8. Premio, reintegro o beneficio: pago/datos para recibirlo.

### Legítimas difíciles

1. Banco informa anomalía y pide usar la app oficial, sin solicitar secretos.
2. Familiar relata una urgencia, pero no pide dinero.
3. Soporte real guía una configuración inocua.
4. Turno médico u obra social solicita datos mínimos permitidos.
5. Comercio gestiona una devolución sin pedir credenciales.
6. Entrega de paquete verifica dirección parcial.
7. Cobranza legítima informa una deuda y ofrece canales oficiales.

## Consentimiento

Se utilizará consentimiento escrito aunque el profesor no exija un comité formal.
La voz y la transcripción pueden identificar a una persona. El consentimiento debe
separar como mínimo:

1. participación y grabación;
2. transcripción y uso para entrenamiento/evaluación;
3. acceso interno del equipo/tutor;
4. publicación de transcripciones pseudonimizadas;
5. publicación del audio original.

Aceptar participar no implica automáticamente aceptar publicar la voz. El borrador
está en [CONSENTIMIENTO-BORRADOR.md](CONSENTIMIENTO-BORRADOR.md).

La [Ley 25.326](https://www.argentina.gob.ar/normativa/nacional/64790/actualizacion)
y la [guía de la AAIP](https://www.argentina.gob.ar/aaip/datospersonales/derechos)
fundamentan informar finalidad, destinatarios, responsable y tratamiento. El tutor
debe revisar el protocolo institucionalmente.

## Datos y acceso

- Audio e información de contacto fuera de Git.
- ID pseudónimo por participante; tabla identidad↔ID en ubicación separada.
- Acceso solo para integrantes y tutor autorizado.
- Backup cifrado y registro de quién posee copias.
- Transcripciones revisadas para eliminar nombres o datos dichos por error.
- Fecha de eliminación propuesta: seis meses después de la aprobación, salvo que el
  participante autorice conservación/publicación y la universidad lo apruebe.
- El repositorio público solo incluye esquemas, código, estadísticas agregadas y
  artefactos expresamente autorizados.

## División train/validation/test

- Todas las variantes de una misma semilla de escenario permanecen en un único
  split.
- Evitar que parejas o hablantes del test aparezcan en entrenamiento cuando la
  cantidad lo permita.
- Congelar test antes de seleccionar modelos y umbrales.
- Registrar exclusiones, fallas de audio y transformaciones.

## Gate antes de grabar

No comenzar el corpus principal hasta responder:

- [ ] ¿El profesor aprueba conversaciones simuladas como fuente de datos?
- [ ] ¿Aprueba el borrador de consentimiento?
- [ ] ¿Existe un procedimiento institucional adicional?
- [ ] ¿Se permitirá publicar transcripciones, audio, ambos o ninguno?
- [ ] ¿Está definido el almacenamiento y la fecha de eliminación?
- [ ] ¿Está aprobado el manual de anotación v0?

Las pruebas técnicas de esta semana pueden usar voces de los propios integrantes o
audio creado específicamente para el spike, sin incorporarlo aún al corpus final.
