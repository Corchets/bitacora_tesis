# #143, configuración congelada: análisis de la humo

> **Estado: propuesta sin discutir.** Desarrollo; no se tocó la reserva, las legítimas de test ni #144. Mateo la corrió
> en Colab T4 el 2026-11-10, y se analizó el mismo día.

**Resultado de la regla escrita antes de correr:** la configuración queda **lista para la evaluación final**. La humo de
formato pasa, el control no encuentra problemas, no hay líneas inválidas y las cuatro cifras quedan a ±1 de la lectura
simulada de la etapa 3.

La salida completa está en [`analisis-salida.md`](analisis-salida.md).

## Verificación de los ZIP

- Cada ZIP se descomprimió en un directorio vacío nuevo, y los dos parciales coinciden archivo por archivo con su carpeta
  en el final.
- `commit.txt`, `TERMINADA.txt` y los dos manifiestos dan `58b0997`, el commit del tag `colab/143-config-congelada`,
  sin cambios sin commitear.
- El sha256 de `colab/probar_config_congelada.py` en el tag coincide con `script-sha256.txt` (`10a15a84…`).
- El digest coincide en los manifiestos y en `digest.txt` (`b37049369adf…`), con Ollama 0.40.14 en una Tesla T4.
- La segunda consulta es la de `motivo_c_corte.txt`, y no hay casos de la reserva ni de test.
- La corrida en desarrollo tardó 7,2 minutos.

## La regla, paso a paso

**0. Humo de formato:** pasa. Lee el riesgo, con su coma, en 48/48 líneas, sin errores.
- Como dato, el riesgo coincide con el de `c-json-corte` en 43 de las 48 líneas, en la misma sesión.
- Las 5 que difieren son 0,5 contra 0,6 o 0,4 (4 líneas, todas arriba del umbral) y un 0,3 contra 0,2 en una línea de
  PROTEGIDA, que con «solo OTRA» no consulta.
- Una sola línea tuvo dos decimales.

**1. Control:** sin problemas. Son los 244 de desarrollo, con `--solo-otra` y en modo operativo. Las 1.478 líneas de
PROTEGIDA no consultaron, y las 1.548 de OTRA sí. El aviso registrado es el de la regla, y el motivo se pidió en cada
aviso y solo ahí.

**2. Líneas inválidas:** 0 de 1.548 consultadas.

**3. Contra la lectura simulada de la etapa 3:**

| configuración | estafas | antes del pedido | a tiempo | FA |
|---|---|---|---|---|
| lectura simulada de la etapa 3 | 35/46 | 15/36 | 25/36 | 24/94 |
| la configuración congelada | 36/46 | 14/36 | 26/36 | 25/94 |

Diferencias: +1, −1, +1 y +1 FA. Todo dentro de ±2.

## Lo que se ve (solo para mirar)

**Las cifras.** Con Wilson al 95 %: estafas 36/46, 78 % [64–88]; a tiempo 26/36, 72 % [56–84]; FA 25/94, 27 % [19–36].
En `alcance-91` las FA son 12/45.

**El ruido.** 10 de los 140 casos avisan en otra línea que en la lectura simulada. Las cifras se compensan, pero muestra
que la línea del aviso se mueve entre sesiones.

**El escalón del 0,3 sigue.** 31 de los 36 avisos en estafas y 23 de las 25 FA salen de un 0,3 exacto.

**Latencia en T4** (p50 / p95, dentro del alcance):
- primera consulta: 206 / 267 ms, con 14 tokens. En la etapa 3, C sin alerta tardaba 239 ms;
- motivo: 678 / 835 ms;
- total en la línea del aviso: 900 / 1.081 ms;
- por llamada, hasta el aviso o el final: 5 consultas en las estafas y 6 en las legítimas (medianas), unos 1,7 s y
  1,4 s.

**El motivo, con la medición de la etapa 3:**
- JSON válido con motivo en 61 de 61 avisos;
- evidencia textual de OTRA en 60. La otra cita una frase de PROTEGIDA;
- la búsqueda por palabras marcó 6 motivos de estafas como «pedido antes de tiempo», y se leyeron los 6:
  - 5 nombran un pedido que ya está en curso. La referencia lo marca más tarde o como dato personal (el DNI con la
    foto);
  - el otro (CV2-D-V-ORGANISMO_PREVISIONAL-006) habla de pagos en general, sin decir que hubo un pedido.

## Los motivos de las 25 FA, leídos a mano

| tipo | casos | cuántos |
|---|---|---|
| Describe un pedido que sí ocurrió | ENT-L-BANCO-003, ENT-L-BANCO-004, ENT-L-DELIVERY-004, ENT-L-SOPORTE-001, ENT-L-SOPORTE-005, ENT-L-VENTAS-001, ENT-L-VENTAS-002, ENT-L-VENTAS-009, LEG-BA-02, LEG-BA-03, LEG2-BA-01, LEG2-BA-02, LEG2-BA-03, LEG2-BA-05, LEG2-CC-05 | 15 |
| Advierte en general, sin decir que hubo un pedido | ENT-L-BANCO-001, ENT-L-BANCO-002, ENT-L-BANCO-005, ENT-L-SOPORTE-003, LEG-BA-01, LEG-ST-03, LEG2-ST-03 | 7 |
| Engaña o no tiene sentido | ENT-L-BANCO-006, LEG2-CC-06, LEG2-ST-05 | 3 |

- **Los 15 que describen un pedido real** son casi todos el DNI o el nombre. Los demás son la descarga del programa de
  asistencia remota, la seña por transferencia, y confirmar un inicio de sesión o una compra.
- **Los 7 genéricos** dicen cosas como «siempre es mejor verificar la identidad antes de compartir cualquier dato».
  - Tres son el mismo escenario: el local de reparación que avisa que la notebook está lista, y el motivo dice que
    eso «es una táctica común para intentar obtener información o pedir dinero».
  - LEG-BA-01 recomienda no «hacer clic en enlaces», y en la llamada no hay ningún enlace.
- **Los 3 que engañan:**
  - **ENT-L-BANCO-006 (L2):** «Desconfía de que te contacten por un número no agendado y que te pidan información
    sensible a través de una app». Hasta ahí OTRA solo dijo «Te hablo del banco, por tu app», y nadie pidió nada. Es el
    mismo caso engañoso de la etapa 3. Ahora lo dice como advertencia y no como hecho, pero sigue nombrando un pedido
    que no ocurrió.
  - **LEG2-CC-06 (L6):** presenta como señal de estafa que «se pide hacer una llamada a un número específico». OTRA le
    dijo que llame al 0800 de su factura, que es el consejo seguro. Es el mismo choque que tuvo la definición de pedido
    crítico en la etapa 3.
  - **LEG2-ST-05 (L2):** «no tiene agendado un ticket y no puede verificar la identidad de quien llama». Mezcla la
    premisa del alcance (el número no agendado) con el ticket, y no tiene sentido.
- **Además, 5 motivos generalizan algo falso:** «los bancos legítimos rara vez solicitan…» el DNI o confirmar una
  compra (ENT-L-BANCO-003, LEG-BA-03, LEG2-BA-01, LEG2-BA-02 y LEG2-BA-05). Los bancos sí validan el DNI y sí llaman
  para confirmar compras.
- **El trato no es el de la app:** mezcla «Desconfía», «Desconfíe» y «mantente» con «Tené cuidado». El prompt no fija el
  voseo.

## Lo que queda para decidir

- **Qué muestra el aviso** lo decide Mateo. El motivo nunca falló, y en 22 de las 25 FA no inventa nada. En 3 engaña, y
  en 5 da un consejo general falso. El prompt del motivo no se cambia (ADR 0005), y las métricas no dependen de él.
- **Propuesta:** mantener el motivo y declarar como hallazgo y limitación los 3 engañosos y las generalizaciones falsas.
- Esto es desarrollo: en la evaluación final, el motivo de las FA del test se lee igual, sin tocar nada.

## Diagnóstico: dónde flaquea el detector (después de ver los resultados; no decide)

A pedido de Mateo, el 2026-11-10. Salida completa en [`diagnostico-salida.md`](diagnostico-salida.md), de
[`diagnostico.py`](diagnostico.py).

**1. El riesgo escrito no separa: casi todo lo dudoso queda en 0,2.**
- Las 10 estafas que no avisan escriben como máximo 0,2, en todas sus líneas de OTRA.
- 7 de esas 10 tienen un pedido explícito y el riesgo no sube ni en la línea del pedido. Por ejemplo:
  - en CV2-D-V-WHATSAPP-003, «Leeme los seis dígitos y te incorporo al grupo» da 0,2;
  - en CV2-D-V-SOPORTE-003, OTRA pide usuario y contraseña;
  - en CV2-D-V-FAMILIAR-004, -005 y -006, un supuesto familiar pide plata desde un número que PROTEGIDA no tiene
    agendado.
- Las otras 3 son premios: dos sin pedido y una que pide el DNI.
- Por familia avisa 12/12 de banco y 6/6 de organismo, pero solo 3/6 de familiar y 3/6 de premio.
- No es que el modelo no vea nada: escribe 0,2 en vez de 0,1. Pero con 0,2 de umbral avisa en 46/46 estafas y en 69/94
  legítimas, 14 de ellas cotidianas. El número escrito no tiene un punto intermedio (H04).

**2. Las FA no caen en llamadas inofensivas.** Según `tipo_legitima`, la anotación previa de cada legítima:
- 0 de las 29 cotidianas;
- 12 de las 38 que hacen un pedido razonable, como el DNI;
- 13 de las 27 que mencionan algo sensible sin pedirlo.

  Casi todas son llamadas en las que un aviso de precaución desde un número no agendado se puede defender. La excepción
  son las tres del local que avisa que la notebook está lista.

**3. Avisos antes del cumplimiento (T_A < T_C):** 12 de las 15 estafas con T_C. Las 3 que llegan a cumplirse sin aviso
son el código de WhatsApp (dos) y la contraseña del portal docente.

**4. Una capa de reglas no lo arregla.** Sobre las líneas de OTRA, unida al SLM:
- las reglas v1 suman 5 estafas y 32 FA;
- las reglas v2 suman 1 estafa y 9 FA.
