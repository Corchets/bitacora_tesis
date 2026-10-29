# Hoja de grabación: ASR con voz real

> Generada por `python guion.py --hoja` desde [`guion.json`](guion.json). No la edites a mano:
> cambiá el guion y volvé a generarla. Plan: [`PLAN-VOZ-REAL.md`](../PLAN-VOZ-REAL.md), issue #94.
> Es audio de voz real: queda fuera de Git (también el de otra persona, con su consentimiento anotado en el issue).

## Qué grabar

Son **2 tomas × 3 condiciones × 6 bloques = 36 grabaciones**, cada una de un bloque de 5 frases:

| Condición | Voz | Cómo entra el audio |
|---|---|---|
| `luciano-microfono` | Luciano | micrófono del panel |
| `luciano-meet` | Luciano | Luciano habla por Meet y el panel toma el audio de Meet (ver abajo) |
| `otra-meet` | otra voz del equipo | igual que la anterior, con otra persona. Si no hay otra voz, alcanza con las dos de Luciano |

La **toma 1** sirve para ajustar los hotwords y el diccionario; la **toma 2** es la que mide y decide
(PLAN-VOZ-REAL.md §2). No ajustes nada mirando la toma 2. En las dos tomas usá el mismo cuarto, la misma
máquina y el mismo micrófono, y no toques la ganancia entre una y otra.

## Cómo grabar un bloque

1. Abrí el panel y activá **Probar el ASR** (README de `experiments/voip`, §10). Dejá el corte en
   **Automático** y el umbral en `0,005`: los otros valores se prueban después, offline, sobre lo guardado.
2. Tocá **▶ Hablar** y leé las 5 frases del bloque con tu voz de siempre (con tu acento, sin actuar).
   Una pausa corta, de un segundo y medio más o menos, entre frase y frase. Si te trabás, seguí; si el bloque
   salió mal, **Borrar** y empezá el bloque de nuevo.
3. **Terminar prueba**. En **Lo que dije en realidad** pegá el bloque de abajo, una frase por línea.
   Si dijiste algo distinto, corregí esa línea para que diga lo que dijiste: la medida compara contra
   eso, no contra el guion. Escribí los números con palabras, como están acá.
4. **Guardar prueba**. Anotá el id de la prueba (lo ves en el Historial) en
   [`pruebas.csv`](pruebas.csv) con la toma, la voz y la condición.

### Condición Meet

> **Estado: propuesta sin discutir.** «Probar el ASR» solo lee un micrófono del navegador, así que para que
> entre el audio que pasó por Meet hay que elegir como micrófono del panel un dispositivo que lo reciba.
> Una forma con lo que ya hay: la receta 2 de [`GUIA-MEET-WHATSAPP.md`](../../voip/GUIA-MEET-WHATSAPP.md)
> (salida múltiple con BlackHole 2ch), eligiendo **BlackHole 2ch** como micrófono del panel mientras vos (o la otra
> persona) hablan por Meet desde el celular. Ajustalo si preferís otro camino, pero que las tomas 1 y 2 usen el mismo.

## Bloques para copiar y pegar

Cada bloque va tal cual en **Lo que dije en realidad**.

### Bloque 1

```text
Pasame el código que te llegó por mensaje, dale, que no tengo todo el día.
Transferí cuarenta y cinco mil pesos al CBU que te paso, es urgente.
Estoy cómodo acá, no hace falta que me ayudes con nada más.
Hablás con el Banco Macro de Tucumán: confirmame tu clave para anular el débito.
Necesito que me confirmes la clave del cajero ahora, ñaño.
```

### Bloque 2

```text
Hacé la transferencia ya, al alias que te mandé, y no le avises a nadie.
Mirá, chango, no seas sonso, pasame la clave y zafás de la multa al toque.
Me duele el codo desde que jugué al fútbol con los changos.
Pasame la plata, son treinta lucas, y que sea en efectivo.
Instalá AnyDesk y dame acceso remoto a tu compu, así lo arreglo yo.
```

### Bloque 3

```text
Entrá a Mercado Pago, abrí el link que te mandé y autorizá la operación.
Decime tu DNI completo y el domicilio donde vivís, es para verificar.
Ñaño, al ñudo te hacés drama, mandame la plata y listo, no seas guaso.
El código tiene seis números: tres, cuatro, uno, nueve, dos, siete.
Abrí el enlace que te mandé y autorizá el ingreso desde tu celular.
```

### Bloque 4

```text
El número de la casa es el doce, queda enfrente de la panadería.
Tu tarjeta quedó bloqueada, pasame el PIN y el CVV para destrabarla.
Naranja X y Ualá te bloquearon la cuenta, tenés que mandarme el DNI.
Tenés que pagar mil doscientos pesos de multa antes de las cuatro.
Te llegó un token por mensaje, leémelo despacito, que ya se vence.
```

### Bloque 5

```text
Dejá al mishi en paz y decime el código, vo', que estoy al vicio con este trámite.
Te escribo del Galicia: pasame el alias y el CBU que usás en Brubank.
Mi mamá abonó la luz y el gas ayer, así que está todo al día.
Mandame el código de verificación de seis dígitos que te llegó por WhatsApp.
Con cinco lucas no zafo, che, mandame el link y lo pago al toque.
```

### Bloque 6

```text
Dame el OTP: ocho, cuatro, dos, uno, cero, cinco, que se vence en un minuto.
Instalá la app del Banco Provincia con este enlace y pasame el PIN.
Esta changa me salió re cara, ñaño: pagame veinte mangos en efectivo y quedamos a mano.
Te mando la foto del cumple de mi sobrino cuando llegue a casa.
Compartí pantalla y entrá a la configuración de la cuenta, yo te guío.
```

## Qué mide cada frase

| Bloque | Frase | Tipo | Etiquetas de `reglas.py` sobre el guion |
|---|---|---|---|
| 1 | F01 | término crítico | `REQUEST_AUTH_CODE` |
| 1 | F02 | números y montos | `REQUEST_TRANSFER` |
| 1 | F03 | negativa parecida | ninguna (debe quedar sin etiquetas) |
| 1 | F04 | banco o app | `REQUEST_SECRET` |
| 1 | F05 | término crítico | `REQUEST_SECRET` |
| 2 | F06 | término crítico | `REQUEST_TRANSFER` |
| 2 | F07 | jerga espontánea | `REQUEST_SECRET` |
| 2 | F08 | negativa parecida | ninguna (debe quedar sin etiquetas) |
| 2 | F09 | números y montos | `REQUEST_TRANSFER` |
| 2 | F10 | término crítico | `REQUEST_REMOTE_ACCESS` |
| 3 | F11 | banco o app | `REQUEST_SECURITY_ACTION`, `REQUEST_TRANSFER` |
| 3 | F12 | término crítico | `REQUEST_PERSONAL_DATA` |
| 3 | F13 | jerga espontánea | `REQUEST_TRANSFER` |
| 3 | F14 | números y montos | `REQUEST_AUTH_CODE` |
| 3 | F15 | término crítico | `REQUEST_SECURITY_ACTION` |
| 4 | F16 | negativa parecida | ninguna (debe quedar sin etiquetas) |
| 4 | F17 | término crítico | `REQUEST_SECRET` |
| 4 | F18 | banco o app | `REQUEST_PERSONAL_DATA` |
| 4 | F19 | números y montos | `REQUEST_TRANSFER` |
| 4 | F20 | término crítico | `REQUEST_AUTH_CODE` |
| 5 | F21 | jerga espontánea | `REQUEST_AUTH_CODE` |
| 5 | F22 | banco o app | `REQUEST_TRANSFER` |
| 5 | F23 | negativa parecida | ninguna (debe quedar sin etiquetas) |
| 5 | F24 | término crítico | `REQUEST_AUTH_CODE` |
| 5 | F25 | jerga espontánea | `REQUEST_SECURITY_ACTION`, `REQUEST_TRANSFER` |
| 6 | F26 | números y montos | `REQUEST_AUTH_CODE` |
| 6 | F27 | banco o app | `REQUEST_REMOTE_ACCESS`, `REQUEST_SECRET` |
| 6 | F28 | jerga espontánea | `REQUEST_TRANSFER` |
| 6 | F29 | negativa parecida | ninguna (debe quedar sin etiquetas) |
| 6 | F30 | término crítico | `REQUEST_REMOTE_ACCESS`, `REQUEST_SECURITY_ACTION` |

Las 5 negativas se parecen a términos críticos («cómodo», «codo», «número») y **no** deben disparar nada.
Dos ejemplos del plan salieron del guion porque `reglas.py` sí los dispara: «pagó la luz» (la regla busca el
texto `pago`) y «el link del cumple» (`link`). «Mercado Pago» también dispara `REQUEST_TRANSFER` por la
misma razón; está en la frase `F11` a propósito.

Cuando termines, completá [`pruebas.csv`](pruebas.csv) y corré la medición:
ver «Cómo correrlo» en [`PLAN-VOZ-REAL.md`](../PLAN-VOZ-REAL.md#8-cómo-correrlo).
