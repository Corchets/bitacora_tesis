# Checklist de ética y datos personales

> Hoy no bloquea nada. Importa **el día que grabemos a la primera persona** — y es la única
> dependencia del proyecto que no podemos acelerar, porque depende de un tercero.

El [anteproyecto](../propuesta/ANTEPROYECTO.md) (sección 11) ya se comprometió a esto:

> "El protocolo se someterá a consideración del comité de ética de la facultad **antes** de iniciar
> la recolección."

Si la recolección del corpus arranca en el ciclo 2 y el comité tarda semanas en expedirse, hay que
averiguar los plazos **antes** de necesitarlos, no cuando ya haya gente esperando para grabar. Por
eso figura como riesgo en el [registro de riesgos](../gestion/REGISTRO-RIESGOS.md) y como parte de
[D06](../gestion/MAPA-DECISIONES.md#d06--definir-la-gobernanza-de-datos).

## Checklist

- [ ] Averiguar si la facultad tiene comité de ética, cómo se presenta y **cuánto tarda**.
- [ ] Confirmar con el profesor si hace falta aprobación previa del protocolo de participantes
      (es una de las cinco confirmaciones del 9 de septiembre).
- [ ] Redactar el protocolo a presentar.
- [ ] Validar el [consentimiento borrador](CONSENTIMIENTO-BORRADOR.md) para grabación de voz.
- [ ] Definir dónde vive el audio, cifrado con qué y quién tiene acceso.
- [ ] Definir el procedimiento de anonimización de las conversaciones legítimas.
- [ ] Encuadrar el tratamiento de datos en la Ley 25.326 de Protección de Datos Personales.

## Reglas que ya rigen

1. **El audio no entra al repositorio.** Nunca. Ver [.gitignore](../../.gitignore).
2. **Los consentimientos firmados tampoco.** Son datos personales.
3. **No se graban llamadas fraudulentas reales.** El corpus es simulado/representado — declarado en
   el anteproyecto como limitación de validez externa y desarrollado en el
   [método de creación del corpus](METODO-CREACION-CORPUS.md).

## Nota sobre el producto, no sobre el corpus

Hay una distinción que la tesis se comprometió a abordar explícitamente y conviene no perder: la
supervisión por parte de un familiar es **asistencia consentida, no vigilancia encubierta**. Requiere
emparejamiento explícito y visible para la persona protegida. Es un argumento de diseño que va al
informe, no un detalle de implementación.
