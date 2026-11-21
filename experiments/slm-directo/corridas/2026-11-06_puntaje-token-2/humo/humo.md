# Humo de la segunda vuelta de #143

Commit `b9fd09ab23fc5da34035a95acf14b6ff09363f0c`. Casos: CV2-D-V-ORGANISMO_PREVISIONAL-004, CV2-D-L-BANCO-001, SC-WA-CODE-01-e01 (48 líneas).

Criterio, fijado antes de correr: masa ≥ 0,9 en al menos 44 de 48 líneas y, con 3 tokens, la respuesta empieza con SÍ/NO o con un solo dígito en al menos 44 de 48 (en v4-L: líneas en que se encontró el decimal del riesgo). Si no pasa, no corre en los 150.

| prompt | pregunta final | masa ≥ 0,9 | masa mínima / mediana | respuesta limpia | resultado |
|---|---|---|---|---|---|
| `v4-lectura` | (el JSON de v4, cortado después del riesgo) | 48/48 | 1.0000 / 1.0000 | 48/48 | PASA |
| `c-sino` | Con lo dicho hasta la línea {n}, ¿conviene avisarle ya a PROTEGIDA que esta llamada puede ser una estafa? Respondé solo SÍ o NO. | 48/48 | 1.0000 / 1.0000 | 48/48 | PASA |
| `c-digito` | Con lo dicho hasta la línea {n}, ¿qué tan probable es que esta llamada sea una estafa? Respondé solo con un número del 0 (nada probable) al 9 (casi seguro). | 48/48 | 0.9997 / 1.0000 | 48/48 | PASA |

Respuestas no limpias con 3 tokens: 0.

