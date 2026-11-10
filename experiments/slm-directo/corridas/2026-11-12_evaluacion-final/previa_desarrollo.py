"""#143, evaluación final: los criterios del borrador aplicados a desarrollo, con corridas que ya existen.

Solo sirve para ver si los criterios están bien planteados antes de fijarlos; no decide nada ni mira el test. Usa:
- la configuración: `c-premisa-corte-riesgo` de la prueba de sensibilidad (2026-11-10) y su repetición;
- v4 sin alcance: `v4-corte` de la etapa 2 (2026-11-07), sobre los 244 con roles y en todas las líneas;
- las reglas v1 y v2, que corren acá mismo, sin modelo.
Vista: alcance-140. El primer aviso de una corrida en todas las líneas es el del modo operativo. Uso, desde esta carpeta:
    python -I previa_desarrollo.py
"""

import importlib.util, sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location('analizar_final', AQUI / 'analizar.py')
an = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(an)
import casos  # noqa: E402  (analizar.py ya puso el laboratorio en sys.path)
from detectores import DetectorReglas  # noqa: E402

e3 = an.e3
CORRIDAS = an.AQUI.parent


def avisos_reglas(version, ids):
    d = DetectorReglas(version)
    return {i: next((n for n in range(1, len(t) + 1) if d.evaluar(t[:n]).alerta_sugerida), None)
            for i in ids for t in [casos.cargar_texto(i)]}


def main():
    vista = e3.VISTA
    sens = CORRIDAS / '2026-11-10_sensibilidad-c'
    avs = {'config': an.avisos_config(e3.leer(sens, 'c-premisa')[0], vista),
           'config (repetición)': an.avisos_config(e3.leer(sens, 'c-premisa-rep')[0], vista),
           an.V4: an.avisos_v4(e3.leer(CORRIDAS / '2026-11-07_alcance-etapa-2', 'v4-corte')[0], vista),
           'reglas v1': avisos_reglas('v1', vista), 'reglas v2': avisos_reglas('v2', vista)}
    ex = {d: an.exitos(av, vista, e3.REF) for d, av in avs.items()}
    print('# #143, evaluación final: los criterios sobre desarrollo (no decide)\n')
    an.cifras_tabla(ex, an.CONFIG)
    for base in ('config', 'config (repetición)'):
        print(f'## Criterios, con `{an.CONFIG}`{" (repetición)" if "rep" in base else ""} como configuración\n')
        prueba = {'config': ex[base], **{r: ex[r] for r in (an.V4, 'reglas v1')}}
        an.tabla([[c, v, '—' if ok is None else ('cumple' if ok else 'no cumple')] for c, v, ok in an.criterios(prueba)],
                 ['criterio', 'valor', 'resultado'])
    print('Contra reglas v2 (se informa, no es criterio): ' + an.contra(ex['config'], ex['reglas v2'])[2] + '.\n')


if __name__ == '__main__':
    sys.exit(main())
