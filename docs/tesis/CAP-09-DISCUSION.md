> **Estado: borrador parcial del 2026-11-03.** Sin el test reservado no hay respuesta final a las preguntas. Lo escrito aquí es lectura provisional de desarrollo, más las amenazas a la validez que ya se conocen.

# Capítulo 9: Discusión

## 9.1. Respuesta a las preguntas de investigación

**PI1, detección incremental.** Respuesta provisional: en desarrollo, usando solo lo disponible hasta cada línea, la configuración final avisó en 10/10 estafas con 0/10 falsas alarmas. La familia de modelos muestra que el contexto y el modelo importan más que la política: los mismos 10 modelos dan 48/100 falsas alarmas en directo y 27/100 con Tito viejo, a cambio de bajar de 90/100 a 82/100 estafas. **[Responder con #52.]**

**PI2, margen temporal.** Respuesta provisional y **poco favorable**: con voz real y la opción B, el aviso suele llegar después de empezado el pedido, entre 3 y 5 s. Eso no invalida el aviso, porque el daño ocurre cuando la persona cumple, pero deja poco margen. Con 3,74 s de consulta, la demora del modelo es una parte importante de esa diferencia. **[Responder con `L_C` y marcas humanas, #52.]**

**E1, efecto del ASR.** No se midió. Se sabe que se pierden términos críticos, y que en estas 9 llamadas eso no cambió ningún aviso.

**E2, explicación.** Sin revisión sistemática. El caso de D1, donde el aviso cita el débito y no el pedido, muestra por qué hay que revisar la cita y no solo el instante.

## 9.2. Interpretación y comparación con antecedentes

- **El TTS engaña.** Zipformer parecía excelente con TTS y fue malo con voz real. Coincide con la advertencia de Traister et al. (2026) sobre datos sintéticos, y por eso los resultados sobre corpus de redacción asistida se leen con cautela.
- **Reglas frente a modelos.** Las reglas no distinguen mencionar de pedir, lo que explica el 58,3 % de falsas alarmas y coincide con la caída ante negativos difíciles de Sim y Kim (2025).
- **Afinar sobre pocos casos no generaliza.** El prompt `v2` mejoró sobre los 53 antecedentes y empeoró sobre corpus v2. Es el motivo para congelar antes del test.
- **WER y términos críticos.** La opción con peor WER recuperó más términos críticos, lo que concuerda con Balagopalan et al. (2019): el WER agregado no alcanza.
- **Falsas alarmas y prevalencia.** Con Axelsson (2000) y Williams (2021), ni un 0/10 en un corpus balanceado dice cuántos avisos falsos vería una persona en su uso cotidiano.

## 9.3. Análisis de errores

Errores conocidos, a completar con el test:

| Componente | Error | Efecto observado |
|---|---|---|
| ASR | «toque» por «token»; «CBB» o «CBO» por «CVV» y «CBU» | Pierde etiquetas; no cambió avisos en estas llamadas |
| ASR | Inglés o portugués en 4 de 129 frases | Ruido en el contexto |
| Tito viejo | Deriva legítimas inocuas, como «¿Tenés la notebook gris?» | Solo más consultas: el modelo las descartó en #101 |
| Detector | Aviso por el débito, antes del pedido del código | Aviso correcto por un motivo distinto del esperado |
| Sistema | Corte de llamada que descartaba la última consulta | Corregido (`7e6b971`) |

## 9.4. Amenazas a la validez

**Interna.**
- La configuración se eligió con los mismos 20 casos que la evalúan en #101.
- La inferencia en GPU no es exactamente repetible.
- #101 corrió con cambios sin commit en la carpeta.
- Los 200 casos reservados son públicos en GitHub desde el 2026-10-23, aunque no se usaron en ninguna corrida versionada. Un modelo publicado después pudo haberse entrenado con ellos, pero Gemma 4 E2B salió el 2026-03-31 ([registro de versiones de Google](https://ai.google.dev/gemma/docs/releases?hl=en)), antes de esa fecha.

**De constructo.**
- `T_R` y `T_C` son marcas provisionales, sin revisión humana (D07 abierta).
- `T_C` es un cumplimiento actuado: permite medir márgenes de ingeniería, no que una persona habría evitado el daño.
- Los márgenes con voz real usan un pedido ubicado por palabras clave.

**Externa.**
- El corpus es simulado y de redacción asistida, y las llamadas tienen 4 guiones y 2 voces.
- Las mediciones son en computadora, no en teléfono.
- Meet entrega un audio más limpio que una llamada celular en la calle.
- No se puede prometer rendimiento para adultos mayores ni para Argentina en general.

**De conclusión.** Con 20 casos, los intervalos son muy anchos: 10/10 es compatible con 72 %, y 0/10 con 28 % de falsas alarmas, ya por encima de la meta.

## 9.5. Implicaciones de ingeniería, éticas y de uso

- **Ingeniería.** E2B no cumple el presupuesto de latencia ni el de memoria de la prefactibilidad. Si el test confirma la calidad, el camino para bajar la demora está en la caché de prefijo o en pedir menos texto, no en un modelo mayor.
- **Producto.** En Android no se puede capturar una llamada común. El prototipo muestra el análisis en una llamada por Meet, no una protección universal.
- **Ética.** Una falsa alarma en una llamada legítima también tiene costo, y un detector no verifica identidades: el aviso debe sugerir verificar, no afirmar fraude.
- **Datos.** El audio perdido muestra que el resguardo de voces requiere un procedimiento explícito.
