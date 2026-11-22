# #52, mejoras de Luciano sobre la configuración de la evaluación final

> **Estado: propuesta sin discutir.** Pedida por Luciano el 2026-11-20, solo en `laboratorio-luciano`. Es posterior a
> la [evaluación final](../2026-11-12_evaluacion-final/analisis.md) y no la reemplaza: lo que salga se informa aparte.
> La regla de abajo y [`analizar.py`](analizar.py) están escritos antes de correr.

## Qué se prueba

Las cuatro mejoras propuestas a partir de los fallos de la evaluación final
([conclusiones](../../../../docs/evaluacion/CONCLUSIONES-EVALUACION-FINAL.md)), sobre la configuración de Mateo
(`c-consejos-corte-riesgo`, primer aviso con «riesgo ≥ 0,3», solo en las líneas de OTRA):

| # | mejora | qué ataca | cómo se aplica |
|---|---|---|---|
| 1 | **Regla de pedido crítico** ([`regla_pedido_critico.py`](../../regla_pedido_critico.py)) | Los pedidos de código y de clave que el modelo deja pasar | El aviso es el primero entre el modelo y la regla |
| 2 | **Prompt que pregunta por el pedido:** `p-niveles` y `p-lista`, de la [exploración de Mateo](../2026-11-20_exploracion-reales/README.md) | Los avisos por quién llama y por mencionar | Se corre cada prompt |
| 3 | **Aviso en dos niveles:** «atención» con la política de siempre; «cortá» con la regla o un «riesgo ≥ 0,5» | Que una venta real reciba una alarma fuerte | Sobre los mismos riesgos |
| 4 | **Confirmación:** dos «riesgo ≥ 0,3», o uno ≥ 0,5 | Los avisos por casualidad en llamadas largas | Sobre los mismos riesgos, como en la exploración |

Además, **16.384 tokens de contexto** (la demo, PR #192), así las coreanas largas se leen enteras.

**Los prompts.** `p-niveles` fue el que más bajó los avisos falsos en la exploración (12 de 33 reales), a costa de
perder estafas: la pregunta es si la regla se las devuelve. `p-lista` es el que pregunta solo qué pide OTRA. Los
otros prompts de la exploración quedan afuera para que la corrida entre en una sesión.

**Cada prompt corre una vez,** en todas las líneas de OTRA, sobre los cinco conjuntos: las 33 coreanas, las 33
legítimas reales, la zona gris de Medicare (42), desarrollo (`alcance-140`) y la vista principal del test (100
estafas y 56 legítimas). La regla, la confirmación y los dos niveles se aplican después, sobre esos riesgos. Son 15
combinaciones más la regla sola.

**Lo que ya se sabe y esta corrida no cambia:** el test y los conjuntos reales ya se miraron para diseñar la regla y
los prompts. Lo que salga es exploración, no una evaluación nueva.

## Regla, escrita antes de correr

**Referencia:** la base con el primer aviso, corrida en esta misma sesión.

**Una combinación sirve** si, contra la referencia:
1. en las coreanas pierde a lo sumo una estafa avisada y una a tiempo;
2. en el test, los avisos a tiempo no bajan más de 3 (lo que cambia entre corridas);
3. y mejora en algo de forma clara:
   - **avisa menos:** baja 7 o más los avisos falsos en las 33 legítimas reales (un tercio de los 21), o
   - **detecta más:** sube 5 o más los avisos a tiempo del test, sin sumar más de 1 aviso falso en el test ni en las
     legítimas reales.

**El nivel «cortá» sirve** si avisa en 7 o menos de las 33 legítimas reales y en 7 o menos de las 56 del test, y llega
a tiempo en al menos 20 de las 27 coreanas con pedido.

**Lo que se espera,** por lo que ya se midió sin correr el modelo ([regla sumada a la evaluación final](../../analisis/2026-11-20-regla-pedido-critico/README.md)
y a la corrida de la exploración): la base con la regla sube los avisos a tiempo del test de unos 53–56 a unos 63–65,
sin avisos falsos nuevos. Si en esta corrida sube menos de 5, la mejora no era real.

## Cómo corre

[`colab/probar_mejoras_luciano.py`](../../colab/probar_mejoras_luciano.py), desde
[`COLAB-MEJORAS-LUCIANO.ipynb`](../../colab/COLAB-MEJORAS-LUCIANO.ipynb), fijado a un tag. Es el script de la
exploración de Mateo con tres cambios: otros prompts, 16.384 tokens y todos los conjuntos para todos los prompts. Las
legítimas reales salen del repo (publicadas el 2026-11-20), así que no hay que subir nada. T4, Ollama 0.40.14, el
digest `b37049369adf…`, seed 42, temperatura 0, roles, `--sin-reglas`, `--solo-otra` y `--seguir-tras-aviso`.

**Análisis:** `python3 -I analizar.py CARPETA`, con el ZIP descomprimido en una carpeta vacía.
