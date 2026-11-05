# Pendientes de Tito y Gemma 4 en el panel (2026-11-02)

Diagnóstico y borradores para que decida Luciano. **Nada de esto se publicó ni se envió.** La
evidencia de partida está en la [comprobación del panel](2026-11-02-tito-gemma4-panel.md).

## Diagnóstico: `test_curacion_tito` y `CIERRE-97.md`

**Causa:** [`CURACION-TITO-2026-10-28.json`](../../slm-directo/CURACION-TITO-2026-10-28.json) fija el
sha256 de `CIERRE-97.md`, y el commit `ee78f6e` (Ignacio, 2026-10-30) cambió una línea de ese
documento después de fijada la revisión (`dd65a96`, 2026-10-29): `(R05, R23)` pasó a `(R05, R25)`, al renumerar el
riesgo del filtro. `CIERRE-97.md` no es código histórico: `generar_seleccion` lo verifica siempre
contra el disco y corta con `Artefacto cambiado`.

| Comprobación, en una copia descartable de `laboratorio-main` (`4a2df79`) | Resultado |
|---|---|
| sha256 auditado de `CIERRE-97.md` | `70167e62…` |
| sha256 de la versión previa a `ee78f6e` | `70167e62…`, igual al auditado |
| sha256 actual | `c31d9e35…` |
| `tests.test_curacion_tito` sin tocar nada | 10 pruebas, los 2 errores conocidos |
| Lo mismo, restaurando solo `CIERRE-97.md` | 10 pruebas, OK: no hay otra causa detrás |

La protección funciona bien: detectó un cambio real. En `laboratorio-luciano` no se ve porque esas
pruebas se omiten donde está la reserva. El cambio es correcto: en
[`REGISTRO-RIESGOS.md`](../../../docs/gestion/REGISTRO-RIESGOS.md) el filtro Tito→SLM es R25 y R23 es
«La demo en vivo falla en la sala».

**Opciones, sin aplicar ninguna:**

1. **Recomendada: Ignacio revisa el cambio y actualiza la huella.** Es de una sola línea y sin efecto en los
   datos, pero cambia `curacion_sha256` y hay que regenerar `SELECCION-TITO-2026-10-28.json`, del que
   leen `diagnosticar_tito.py` y `preparar_particiones_tito.py`. Conviene revisar qué se invalida.
2. **Volver a `(R05, R23)` en `CIERRE-97.md`.** Las pruebas pasan sin tocar huellas, pero el documento
   queda citando un riesgo equivocado.
3. **Dejarlo documentado como deuda.** No se toca nada y los 2 errores siguen en cada corrida.

Sacar `CIERRE-97.md` de los artefactos o pasarlo a `CODIGO_HISTORICO_RUTAS` debilitaría la protección:
no lo propongo.

## Propuesta: medir la demora de E2B

> **Estado: propuesta sin discutir.** No cambia el criterio de < 2 s de
> [#84](https://github.com/Corchets/bitacora_tesis/issues/84) ni cierra
> [D09](../../../docs/gestion/MAPA-DECISIONES.md#d09--elegir-asr-y-detector).

**Resultado (2026-11-02):** NO CUMPLE, mediana de 3,74 s en 15 consultas. Ver la [corrida](2026-11-02-voz-real-meet.md#demora-de-e2b-84).

### Por qué 4,02 s y 1,45 a 1,80 s no se pueden comparar

**Las medianas mezclan dos cosas.** `segundos_detector` junta en la misma lista las frases
«Sin consulta», donde solo corre Tito (unos 30 ms), y las consultas reales al modelo. #84 se escribió
cuando toda evaluación consultaba al SLM.

- **`LG-SUPPORT-INFO-01`, 1,45 s:** son 14 evaluaciones y 7 frases sin consulta. Si esas 7 son 7
  evaluaciones, la mediana es el promedio de la más lenta de Tito y la más rápida del modelo, así que
  **la consulta más rápida tardó unos 2,9 s**: ninguna bajó de 2 s.
- **`SC-SOPORTE-CLAVE-01`, 1,80 s:** son 8 evaluaciones y máximo 3,25 s, lo que obliga a que haya hasta 3
  sin consulta y al menos una consulta de 1,80 s o menos. Acá sí hubo consultas por debajo de 2 s.
- **`SC-WA-CODE-01`, 4,02 s:** son 3 evaluaciones; no sabemos si alguna fue sin consulta.

Es una deducción aritmética: los `detector.jsonl` de esas llamadas no están en ninguna copia de la
Mac. Lo que sí se puede afirmar es que **el 1,45 a 1,80 s no muestra que E2B cumpla**, y que sigue sin
saberse la mediana real de las consultas.

**La primera consulta no se debe excluir sin más.** Hay dos «primeras» distintas:

- **Primera corrida tras cargar el modelo:** es calentamiento y se puede descartar, si se declara antes de medir.
- **Primera consulta de cada llamada:** con Tito ocurre justo cuando activa, cerca del pedido, y es la
  que define cuánto tarda el aviso. Sacarla escondería la demora que le importa a la persona. Se conserva.

Además, `keep_alive` es de 10 min y el panel solo calienta el modelo al construir el detector: con
más de 10 min sin consultas, la primera consulta de una llamada real puede salir en frío de verdad.

### Protocolo

Corrida preregistrada, unos 3 minutos, con Luciano sin usar el panel:

1. **Condiciones:** preferible con el servidor de 8765 cerrado por Luciano, porque `medir.py` carga otro
   Tito y otro Zipformer que en la demo no existen. Con el servidor abierto, anotarlo. Antes de cada
   repetición, guardar `memory_pressure | tail -1` y `ollama ps`.
2. **Una corrida de calentamiento, que se descarta, y 5 válidas**, siempre con `SC-WA-CODE-01`. Si
   quedan menos de 10 consultas, sumar corridas hasta llegar a 10:

   ```sh
   python medir.py --detector tito-slm --modelo gemma4:e2b-it-q4_K_M \
     --salida corridas/AAAA-MM-DD-medicion-84-e2b
   ```

3. **Resultado, con el mismo umbral:** mediana de todas las consultas juntas (`consulta` ≠ `omitida`) < 2 s.
   Al lado, sin decidir el resultado: primera consulta de cada llamada, p95, máximo, salteadas y aviso
   respecto del fin del pedido.
4. **Una llamada de `SC-WA-CODE-01` por el panel, con Chrome**, para separar el efecto del camino del
   efecto del ejemplo.
5. Si no cumple, se registra «NO CUMPLE». No se ajusta el protocolo después de ver el número.

El desglose sale de lo que ya guarda `medir.py`, sin cambiar código:

```sh
python3 - corridas/AAAA-MM-DD-medicion-84-e2b/*/detector.jsonl <<'PY'
import json, statistics, sys
todas = []
for ruta in sys.argv[1:]:
    filas = [json.loads(l) for l in open(ruta, encoding="utf-8") if l.strip()]
    ms = [f["ms_detector"] / 1000 for f in filas if f.get("consulta", "x") != "omitida" and f["ms_detector"] is not None]
    todas += ms
    print(ruta, "consultas", [round(x, 2) for x in ms])
if todas:
    print("n", len(todas), "mediana", round(statistics.median(todas), 3), "max", round(max(todas), 3))
PY
```

## Borrador: comentario de cierre de #85

Actualizado después de la prueba: está en la [corrida con voz real](2026-11-02-voz-real-meet.md#borradores-de-cierre).

## Borrador: mensaje a Ignacio sobre #102

Para que lo mande Luciano. No propone criterio a propósito.

```markdown
Ignacio, necesito que definamos qué pasa con #102, porque los registros no coinciden:

- GitHub lo da por borrado: la API responde HTTP 410, «This issue was deleted» (2026-11-02).
- La bitácora de la semana 04 dice, el 2026-10-30, que «el borrado de #102 fue rechazado por GitHub».
- El informe de #101 dice que no se adopta ninguna meta ni se declara mejora «sin el acuerdo previsto en #102».
- También lo citan `comprobar_tito_100.py` (política de #102) y `PROPUESTA-20-CONVERSACIONES-TITO-2026-10-29.md`.

Hoy el criterio de aceptación de la matriz remite a un issue que no se puede leer. Te pregunto:

1. ¿Sabés quién lo borró y si fue a propósito? ¿Guardaste el texto o un borrador?
2. Lo que tenía adentro, ¿sigue haciendo falta o quedó superado por el cierre de #101?
3. Si sigue haciendo falta, ¿dónde lo dejamos: un issue nuevo o el acuerdo escrito en otro lado?

Hasta definirlo no recreo el issue, no fijo ningún criterio y los resultados de #101 siguen sin meta adoptada.
```
