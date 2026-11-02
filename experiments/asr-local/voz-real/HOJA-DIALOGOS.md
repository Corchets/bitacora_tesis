# Hoja de diálogos: elegir el corte de Parakeet

> Generada por `python dialogos.py --hoja` desde [`dialogos.json`](dialogos.json). No la edites a mano.
> Plan: [`PLAN-VOZ-REAL.md`](../PLAN-VOZ-REAL.md#129-dos-candidatos-para-comparar-en-diálogos-reales-2026-10-30), issue #94.
> Es audio de voz real: queda fuera de Git. La otra persona da su consentimiento y queda anotado en #94.

## Qué grabar

Cinco llamadas por Meet: los cuatro diálogos y **D1 otra vez con la tele prendida** de fondo, del lado
de la notebook. Si pueden, después cambian de lugar y repiten los cuatro: así cada voz pasa por los dos
canales. Cada llamada se graba una sola vez; las dos opciones de corte se comparan después sobre el mismo audio.

## Antes de empezar

1. Los dos con **auriculares**: si el audio de Meet sale por los parlantes, el micrófono de la notebook
   lo vuelve a tomar y las voces se mezclan.
2. En el panel: modo llamada, **Persona protegida = micrófono** (con cancelación de eco) y
   **Otra persona = pestaña de Meet** con «Compartir audio».
3. Modelo de ASR **Parakeet**, con `parakeet-filtro` o `parakeet-silero`, y la misma toda la sesión: lo que
   se ve en pantalla puede cambiar cómo hablan. El audio guardado no depende de esa opción.

## Cómo hacer cada llamada

1. Iniciá la llamada en el panel y esperá a que suban los dos medidores.
2. Cada uno lee **solo sus líneas**, a ritmo de charla: contestá apenas termina el otro, sin esperar.
   Con tu acento y tu forma de hablar, sin actuar. Si se pisan un poco no pasa nada: cada voz va por su canal.
3. Si te trabás, seguí. Si cambiaste una palabra, anotala en la `nota` de la fila. Si la llamada salió
   muy mal, terminala y hacela de nuevo.
4. Terminá la llamada. Copiá el id del Historial y agregá **dos filas** a [`pruebas.csv`](pruebas.csv),
   una por canal:

```text
2026-11-02_101500-123456,5,luciano,dialogo,D1,protegida,
2026-11-02_101500-123456,5,otra,dialogo,D1,otra,
```

La llamada con la tele va con la condición `dialogo-tv`. Si cambiaron de lugar, cambia la columna `voz`
(quién estaba en ese canal); las líneas siguen el canal: quien está en la notebook lee las de la protegida.

## D1 · Falso empleado del banco: código y clave (estafa)

- **Otra**: Hola, buenas tardes, ¿hablo con el titular de la cuenta?
- **Protegida**: Sí, soy yo. ¿Quién habla?
- **Otra**: Le hablo del Banco Macro de Tucumán, del área de seguridad.
- **Otra**: Detectamos un débito de ochenta y cinco mil pesos que usted no reconoce.
- **Protegida**: ¿Ochenta y cinco mil? No, yo no hice ninguna compra.
- **Otra**: Por eso lo llamo. Le va a llegar un código por mensaje, pasámelo cuando te llegue.
- **Protegida**: Ajá. Esperá que me fijo.
- **Protegida**: Sí, me llegó uno, pero dice que no se lo muestre a nadie.
- **Otra**: Tranquilo, es automático. Leeme los seis números despacito.
- **Protegida**: Cuatro, ocho, dos, cero, siete, uno.
- **Otra**: Perfecto. Ahora confirmame la clave del cajero para terminar la anulación.
- **Protegida**: ¿Eso también? Me parece raro, che.
- **Otra**: Es el último paso, dale, que si no el débito se confirma a las cuatro.
- **Protegida**: Bueno, pará, mejor voy yo al banco.
- **Otra**: No corte, que se pierde todo el trámite.

## D2 · Falso sobrino con número nuevo: plata urgente (estafa)

- **Otra**: Hola, ¿qué hacés? Soy yo, el Nico, cambié de número.
- **Protegida**: ¿Nico? ¿Qué Nico?
- **Otra**: Tu sobrino, chango, ¿no me reconocés la voz? Se me rompió el celu.
- **Protegida**: Ah, ¿y qué pasó?
- **Otra**: Estoy en un lío, ñaño. Tengo una deuda que vence hoy y no me anda la cuenta.
- **Protegida**: ¿Y cuánto necesitás?
- **Otra**: Treinta lucas nomás. Transferime al alias que te paso y mañana te lo devuelvo.
- **Protegida**: Mirá que yo uso Ualá, no sé si me deja mandar tanto.
- **Otra**: Sí, te deja. Si no, mandalo por Mercado Pago, al toque.
- **Protegida**: No seas guaso, ¿por qué no le pedís a tu mamá?
- **Otra**: No le avisés a nadie, porfa, que se hace drama al ñudo.
- **Protegida**: Dale, pero primero te llamo al número viejo.
- **Otra**: No, ese no anda. Hacé la transferencia ya, que cierra el banco.
- **Protegida**: Bueno, ahora veo.

## D3 · Amigos arreglando un cumple: palabras parecidas (legítima)

- **Otra**: ¿Qué hacés, chango? ¿Venís el sábado al cumple de la Sofi?
- **Protegida**: Sí, obvio. ¿A qué hora es?
- **Otra**: A las nueve, en lo de la abuela. El número de la casa es el doce.
- **Protegida**: Dale. Me duele el codo todavía, así que no juego a la pelota antes.
- **Otra**: Tranqui. Mi mamá abonó la luz ayer, así que esta vez hay luz en el patio.
- **Protegida**: Jaja, re bien. ¿Llevo algo?
- **Otra**: Traé gaseosa y hielo, nada más. Yo me encargo del asado.
- **Protegida**: ¿Y cuánto ponemos cada uno para la carne?
- **Otra**: Dos mil quinientos cada uno, me los das el sábado en mano.
- **Protegida**: ¿Cuál era la dirección exacta?
- **Otra**: Calle Mendoza mil cuatrocientos. Estoy cómodo acá, igual te paso a buscar si querés.
- **Protegida**: No hace falta, voy en la moto de mi hermano.
- **Otra**: Listo, nos vemos el sábado.
- **Protegida**: Abrazo, chau.

## D4 · Falso soporte técnico: acceso remoto, token y CVV (estafa)

- **Otra**: Buen día, le hablamos del soporte de Brubank. ¿Pudo entrar hoy a la app?
- **Protegida**: No, me da error desde la mañana.
- **Otra**: Es por una actualización. Instalá AnyDesk y dame acceso remoto, así lo arreglo yo.
- **Protegida**: ¿Qué es eso? ¿Es seguro?
- **Otra**: Sí, es la herramienta que usa el banco. Avisame cuando abra.
- **Protegida**: Ya abrió.
- **Otra**: Compartí pantalla y entrá a la configuración de la cuenta, yo te guío.
- **Protegida**: Ya está, me aparece un número largo.
- **Otra**: Pasame ese número y el token que te llegó por mensaje.
- **Protegida**: El token es ocho, cuatro, dos, uno, cero, cinco.
- **Otra**: Bárbaro. Para validar la tarjeta necesito el CVV, los tres números de atrás.
- **Protegida**: Mmm, no, eso no te lo voy a dar.
- **Otra**: Si no lo valida, le bloqueamos la cuenta y el CBU en una hora.
- **Protegida**: Bloqueala nomás, mañana voy a la sucursal.

## Qué mide cada línea

| Línea | Quién | Tipo | Etiquetas de `reglas.py` sobre el texto |
|---|---|---|---|
| D1-01 | otra | charla | ninguna |
| D1-02 | protegida | corta | ninguna |
| D1-03 | otra | bancos | ninguna |
| D1-04 | otra | numeros | ninguna |
| D1-05 | protegida | numeros | ninguna |
| D1-06 | otra | critica | `REQUEST_AUTH_CODE` |
| D1-07 | protegida | corta | ninguna |
| D1-08 | protegida | charla | ninguna |
| D1-09 | otra | critica | `REQUEST_AUTH_CODE` |
| D1-10 | protegida | numeros | ninguna |
| D1-11 | otra | critica | `REQUEST_SECRET` |
| D1-12 | protegida | charla | ninguna |
| D1-13 | otra | numeros | ninguna |
| D1-14 | protegida | corta | ninguna |
| D1-15 | otra | charla | ninguna |
| D2-01 | otra | charla | ninguna |
| D2-02 | protegida | corta | ninguna |
| D2-03 | otra | jerga | ninguna |
| D2-04 | protegida | corta | ninguna |
| D2-05 | otra | jerga | ninguna |
| D2-06 | protegida | corta | ninguna |
| D2-07 | otra | numeros | `REQUEST_TRANSFER` |
| D2-08 | protegida | bancos | ninguna |
| D2-09 | otra | bancos | `REQUEST_TRANSFER` |
| D2-10 | protegida | jerga | ninguna |
| D2-11 | otra | jerga | ninguna |
| D2-12 | protegida | charla | ninguna |
| D2-13 | otra | critica | `REQUEST_TRANSFER` |
| D2-14 | protegida | corta | ninguna |
| D3-01 | otra | jerga | ninguna |
| D3-02 | protegida | corta | ninguna |
| D3-03 | otra | negativa | ninguna |
| D3-04 | protegida | negativa | ninguna |
| D3-05 | otra | negativa | ninguna |
| D3-06 | protegida | corta | ninguna |
| D3-07 | otra | charla | ninguna |
| D3-08 | protegida | charla | ninguna |
| D3-09 | otra | numeros | ninguna |
| D3-10 | protegida | charla | ninguna |
| D3-11 | otra | negativa | ninguna |
| D3-12 | protegida | negativa | ninguna |
| D3-13 | otra | corta | ninguna |
| D3-14 | protegida | corta | ninguna |
| D4-01 | otra | bancos | ninguna |
| D4-02 | protegida | charla | ninguna |
| D4-03 | otra | critica | `REQUEST_REMOTE_ACCESS` |
| D4-04 | protegida | corta | ninguna |
| D4-05 | otra | charla | ninguna |
| D4-06 | protegida | corta | ninguna |
| D4-07 | otra | critica | `REQUEST_REMOTE_ACCESS`, `REQUEST_SECURITY_ACTION` |
| D4-08 | protegida | charla | ninguna |
| D4-09 | otra | critica | `REQUEST_AUTH_CODE` |
| D4-10 | protegida | numeros | `REQUEST_AUTH_CODE` |
| D4-11 | otra | critica | `REQUEST_AUTH_CODE`, `REQUEST_SECRET` |
| D4-12 | protegida | corta | ninguna |
| D4-13 | otra | bancos | `REQUEST_TRANSFER` |
| D4-14 | protegida | charla | ninguna |

Las negativas y las respuestas cortas («Sí, obvio», «Ya abrió») no tienen que disparar nada. D3 es
una charla legítima con palabras parecidas a las de una estafa («número de la casa», «codo», «abonó la luz»).
