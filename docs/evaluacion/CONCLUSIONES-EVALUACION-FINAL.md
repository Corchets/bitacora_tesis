# Qué concluir de la evaluación final

> **Estado: propuesta sin discutir.** Pedida por Luciano el 2026-11-20 para el documento y la defensa. Sale de la
> [evaluación final](../../experiments/slm-directo/corridas/2026-11-12_evaluacion-final/analisis.md) (Mateo,
> 2026-11-19, `c-consejos-corte-riesgo`, una sola vez), de la
> [comparación con las fichas de Luciano](../../experiments/slm-directo/analisis/2026-11-20-detector-vs-luciano/README.md)
> y de la [latencia en el A56](../../experiments/slm-directo/corridas/2026-11-11_a56-latencia-172/README.md).

**En una oración:** el detector avisa a tiempo en dos de cada tres estafas que nunca vio, en un teléfono, pero se guía
más por el tema y por quién llama que por lo que efectivamente le piden a la persona.

## Con qué se evaluó

| conjunto | estafas | legítimas | qué son |
|---|---|---|---|
| Test reservado | 100 | 56 | Generadas, nunca usadas para elegir nada. Las 100 legítimas viejas del corpus v2 no cuentan: casi todas quedan fuera del alcance |
| Coreanas (#144) | 33 | — | Estafas reales, traducidas |
| Call center (CallCenterEN) | — | 33 | Llamadas reales de venta y atención, traducidas |
| Desarrollo | 46 | 94 | Con las que se eligió la configuración |

## Lo bueno

- **Generaliza:** a tiempo en el **66 %** del test, contra 72 % en desarrollo. Lo elegido no estaba sobreajustado.
- **Avisa antes del pedido en el 46 %:** la persona se entera antes de que le pidan la clave.
- **Avisa en el 27 % de las legítimas generadas**, igual que el prompt anterior, que avisaba mucho más tarde.
- **Avisa las 33 coreanas,** temprano: en la línea 6, de mediana. Son llamadas muy largas (113 líneas de mediana) y
  dos de cada tres no entrarían enteras en el contexto, pero como el detector corta en el primer aviso, ninguna llegó
  al tope (§Contexto).
- **Corre en un Samsung A56 sin internet:** primer aviso en 3,7 s.
- **Protocolo limpio:** test reservado, regla escrita antes y una sola corrida.

## Qué ve y por qué

- **Banco: 24 de 25.** Soporte técnico, en cambio: 11 de 20. Premio y WhatsApp: 9 de 15.
- **Ve la forma de la estafa:** alguien que llama sin que lo esperen, se presenta como una institución y lleva la charla
  a un tema sensible. Los motivos que escribe lo muestran: «los bancos rara vez llaman así», «te piden una
  transferencia para cobrar un premio».
- **Contra las fichas de Luciano** (21 estafas de desarrollo): coinciden en la línea en 6, el detector se adelanta en 5
  y se atrasa en 4. **Coinciden cuando hay un pedido concreto** (programa remoto, código, pago). Cuando se adelanta,
  en general es por quién llama: en dos llamadas avisa en la primera línea, apenas OTRA dice «de control de operaciones».

## Qué no ve, y lo más interesante

**1. Se le escapan pedidos de código explícitos.** Es el robo de WhatsApp, la estafa más común, y la política dice
avisar siempre. De los 25 pedidos de código del test, en **10 no avisa o avisa tarde**:
- «Te mando una confirmación por WhatsApp y me leés el código que aparece» (`WHATSAPP-006`): no avisa;
- «Leeme los números y te dejo en el grupo nuevo» (`WHATSAPP-002`): avisa 17 líneas después;
- en desarrollo pasa lo mismo: «leeme los seis dígitos» (ficha 15 de Luciano) y «la contraseña anterior» (ficha 06).

Las frases que se le escapan suelen no decir «código»: «decímelo», «pasámela», «mandámela». **Una regla de palabras
clave avisa a tiempo en 8 de esas 10.**

**2. Avisa por mencionar, no por pedir.** De los 15 avisos en legítimas del test, **8 son llamadas que solo mencionan
un código, un PIN o un pago, sin pedirlo.** Avisa en la mitad de las legítimas de ese tipo (8 de 16), y en ninguna de
las cotidianas (0 de 14). Ejemplos:
- la farmacia explica que el código de la prepaga se usa en el mostrador → «no compartas códigos»;
- la telefónica avisa que la portabilidad quedó aprobada → «te están pidiendo un PIN»;
- el consorcio avisa una cuota extraordinaria → «el número no estaba agendado».

**Juntando 1 y 2: reacciona al tema** (banco, código, deuda) **y no a si de verdad hay un pedido.**

**3. Los bancos legítimos le parecen estafas:** avisa en 5 de las 7 llamadas legítimas de banco del test.

**4. El modelo tiene tres estados, no una probabilidad:** 0,1 «limpio», 0,2 «no sé», 0,3 «sospecho». Las 27 estafas
que no avisa se quedan todas en 0,2 o menos. Con el umbral en 0,2 avisaría 99 de 100 estafas, pero también 45 de 56
legítimas: no hay umbral que lo arregle.

**5. Con llamadas reales avisa de más:** 21 de 33 legítimas de call center (64 %), contra 27 % en las generadas.
Las reales son llamadas salientes de una empresa de telecomunicaciones a negocios que ya son clientes: instalaciones,
visitas técnicas, mejoras de plan. Tienen de 13 a 38 líneas, como las del corpus. Avisa entre la línea 4 y la 26. En
la mayoría de las consultas el modelo está en «no sé», y 19 de los 21 avisos son un 0,3 justo. Los motivos que
escribió se reparten en tres grupos: unos 8 por un pedido de código o de datos de la cuenta (un call center real
verifica al cliente así), unos 7 que leen la venta como estafa (una promoción, un precio que cambia, apuro por cerrar) y
unos 6 genéricos (le piden un mail, «conviene verificar», la llamada se graba).

**6. Las legítimas generadas están sesgadas, pero no explican las reales.** Se escribieron a propósito con la
estructura de la estafa: el banco que llama por un fraude, un código que se menciona, una seña por transferencia. Tres
de cada cuatro tienen un pedido o una mención sensible. Eso infla los avisos en las generadas. Pero comparando por tipo
de llamada, las reales dan peor en todos:

| tipo de legítima | generadas (test) | reales |
|---|---|---|
| Cotidiana | **0 de 14** | **9 de 19** |
| Mención sin pedido | 8 de 16 | 8 de 10 |
| Pedido razonable | 7 de 26 | 4 de 4 |

Una llamada cotidiana generada nunca hace saltar el aviso; una real, la mitad de las veces. **Las generadas tienen la
estructura de la estafa en el contenido, pero son demasiado prolijas en la forma:** cortas, claras, sin vueltas. Las
reales tienen ruido, idas y vueltas, ventas, y eso pone al modelo en «no sé».

**7. En la zona gris avisa en 32 de 42,** y probablemente ahí acierta: son ventas de seguros y equipamiento médico de
EE. UU. que los anotadores marcaron como estafa o dudosa, y coinciden con esquemas de fraude a Medicare documentados.

## Contexto

En cada turno el detector le manda al modelo toda la conversación. La ventana es de **4096 tokens**; cuando no entra,
la consulta falla y no avisa. **Son unos 10 minutos de conversación** (unos 8.300 caracteres libres, a unos 815 por
minuto en las llamadas de la demo).

- **En la evaluación final casi no pesó:** el detector corta en el primer aviso, y las llamadas del corpus tienen de 20
  a 40 líneas. Solo una llamada llegó al tope, de la zona gris (104 líneas, 19 consultas fallidas).
- **De dónde sale el 4096:** era el contexto por defecto de Ollama cuando arrancó el proyecto. En el spike de
  septiembre (#29) ya se lo menciona por la memoria que reservaba en el teléfono. El 2026-10-23 quedó escrito en el
  protocolo como «contexto para llamadas completas sin recorte silencioso», y nunca se revisó.
- **El modelo admite 131.072 tokens** (`ollama show`): 4096 es el 3 %. Con 16.384 entrarían unos 50 minutos. Lo que
  cuesta es memoria y demora en el teléfono, y eso hay que medirlo en el A56.
- **Para la demo y una prueba de 30 minutos:** subir la ventana y declararlo. En la tesis va como límite.

## Conclusiones

1. **Un modelo chico, en un teléfono y sin internet, puede avisar a tiempo de una estafa telefónica** en dos de cada
   tres casos que nunca vio.
2. **Lo que aprendió es la forma y el tema de la estafa, no el pedido.** Por eso avisa temprano, pero también se le
   escapan pedidos explícitos con otras palabras y avisa cuando una legítima menciona un código.
3. **Contra una regla de palabras clave no detecta más:** lo que aporta es avisar mucho menos en las legítimas (27 %
   contra 86 %).
4. **Los datos generados sobreestiman cuánto acierta con las legítimas:** 27 % de avisos falsos en las generadas,
   64 % en las reales. Sin las 33 llamadas reales no se habría notado.
5. **Lo que falta:** llamadas reales argentinas, probarlo con reconocimiento de voz (#54) y una ventana de contexto
   para llamadas largas.

**No decir:** que el 33/33 de las coreanas prueba que detecta (las reglas también dan 33/33), ni una sola cifra de
avisos falsos promediando generadas y reales.

## Para leer los casos

Los textos completos de las 15 legítimas con aviso, las 27 estafas sin aviso y las 10 con aviso tarde, con la línea del
aviso y la del pedido marcadas, están en `data/private/LECTURA-FALLOS-TEST-RESERVADO.html`. No está en Git: son textos de
`reserva/test`. Se arma con los CSV del test de esa rama y la regla de aviso de `analizar.py`.
