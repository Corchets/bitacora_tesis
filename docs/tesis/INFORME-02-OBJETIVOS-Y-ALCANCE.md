# Capítulo 2. Objetivos y alcance

## 2.1. Objetivo general

Diseñar, implementar y evaluar un prototipo que analice de manera incremental una conversación de voz en español,
mediante inferencia local, para estimar el riesgo de vishing, identificar maniobras de ingeniería social y emitir una
advertencia contextual antes de una acción crítica, cuantificando su desempeño, sus falsas alarmas, su latencia y su
margen temporal de intervención.

## 2.2. Objetivos específicos

1. Relevar el estado del arte, las modalidades de vishing relevantes en la Argentina y las restricciones técnicas,
   éticas y legales del problema.
2. Definir una taxonomía operativa de maniobras y de pedidos riesgosos.
3. Construir un corpus controlado y documentado de conversaciones de vishing y de llamadas legítimas difíciles en
   español.
4. Comparar alternativas de reconocimiento de voz que corran en el dispositivo.
5. Evaluar reglas de palabras clave como línea base para comparar los detectores candidatos.
6. Desarrollar un detector incremental que considere toda la conversación disponible hasta cada momento.
7. Diseñar advertencias explicables, derivadas de la evidencia de la conversación.
8. Integrar el recorrido audio → transcripción → detección → advertencia en un entorno controlado.
9. Evaluar la detección, las falsas alarmas, la anticipación respecto del pedido, la latencia y el consumo de recursos.
10. Documentar la arquitectura, las decisiones, los resultados, las limitaciones y el trabajo futuro.

## 2.3. Preguntas de investigación

El trabajo se organiza alrededor de dos preguntas:

- **Detección incremental.** ¿Con qué desempeño y con qué tasa de falsas alarmas puede detectarse vishing usando solo
  la parte de la conversación disponible hasta cada momento?
- **Utilidad temporal.** ¿Con cuánto margen respecto del primer pedido riesgoso y del primer cumplimiento puede
  emitirse el aviso?

Como objetivo secundario se plantea revisar si el motivo que muestra el aviso corresponde a lo que efectivamente se
dijo en la llamada.

> **Corregir:** no hay una evaluación registrada del motivo. Antes de cerrar el capítulo 9, decidir si se informa
> como no realizada o si se hace una revisión acotada.

Las preguntas no presuponen un resultado favorable. Un experimento que muestre poca anticipación, o que un método
simple rinde igual que uno complejo, es un resultado válido si está bien diseñado.

## 2.4. Alcance

**Idioma y escenarios.** Español, con prioridad de la variedad rioplatense y de las modalidades documentadas en la
Argentina. No se afirma representatividad nacional ni regional.

**Llamadas.** El detector se activa en llamadas entrantes de números que no están en la agenda del teléfono. Es la
situación típica del vishing y la misma que usan los productos comerciales comparables. Las consultas que inicia la
propia persona, en las que es normal que le pidan datos, quedan fuera. La aplicación decide si activa el detector; el
modelo recibe solo la transcripción.

> **Estado: propuesta sin discutir.** El alcance de entrantes de números no agendados
> ([ADR 0003](../ingenieria/adr/0003-detector-solo-en-entrantes-de-no-agendados.md)) se usó en la evaluación final,
> pero no está aceptado formalmente.

**Procesamiento.** Todo ocurre en el dispositivo: la transcripción, la detección y el aviso. La conversación no sale
del teléfono y el audio no se guarda. El sistema no consulta modelos remotos.

> **Estado: propuesta sin discutir.** Un modelo remoto se usó como referencia de comparación sobre conversaciones
> ficticias (capítulo 8). [D03](../gestion/MAPA-DECISIONES.md#d03--congelar-alcance-y-contribución) dice que no
> entra ni como referencia: el equipo tiene que actualizarla antes de cerrar este párrafo.

**Detección.** Sobre la transcripción de la llamada en curso, sin memoria de llamadas anteriores. El sistema emite un
solo aviso por llamada, con un motivo breve.

**Prototipo.** Un recorrido completo, desde el audio hasta el aviso, que funciona en vivo sobre una llamada por
internet en la que el sistema recibe la voz de cada persona por separado.

**Evaluación.** La detección se mide sobre conversaciones escritas: un corpus propio y conjuntos externos de llamadas
reales. El reconocimiento de voz se mide aparte, con voz real. La latencia y la memoria se miden en teléfonos.

## 2.5. Exclusiones

| Fuera del alcance | Motivo |
|---|---|
| Analizar llamadas telefónicas comunes desde una aplicación instalada por el usuario | En Android, el audio de una llamada telefónica está reservado a aplicaciones del sistema (Android Developers, s. f.-a, s. f.-b). Un producto real tendría que integrarse con el fabricante (capítulo 4) |
| Biometría de voz y detección de voces clonadas | Es otro problema, con otras técnicas y otros datos |
| Rasgos acústicos (tono, estrés en la voz) para detectar fraude | El audio se usa para transcribir. El análisis del tono queda como mejora futura |
| Reputación del número y detección de números falsificados | Ya existen soluciones para eso, y no ven el contenido de la llamada |
| Medir cuánto cambia la detección entre una transcripción manual y la automática sobre las mismas llamadas | Requería grabar y transcribir a mano todo el corpus. El reconocimiento de voz se midió por separado |
| Prueba con usuarios | No se midió si el aviso cambia la conducta de la persona |
| Aplicación para el público, otros idiomas, análisis de mensajes y servicios en la nube | Fuera del tiempo y del objetivo del trabajo |

## 2.6. Criterio de éxito

El trabajo es exitoso si responde las preguntas con un procedimiento honesto y reproducible, entrega un recorrido
demostrable de punta a punta y documenta sus límites.

El equipo fijó una meta de referencia: avisar en el 80 % a 85 % de las estafas, con 10 % a 15 % de falsas alarmas,
contando todas las estafas, incluso las que terminan antes de que aparezca un pedido. No es un umbral de aprobación.
Se busca el mejor resultado posible sin ajustar el sistema para alcanzar esa cifra, y el resultado se informa aunque
no la alcance. Además, se pide que el detector no avise por una frase suelta (por ejemplo, «pasame el código») en una
conversación que no tiene nada que ver con una estafa.
