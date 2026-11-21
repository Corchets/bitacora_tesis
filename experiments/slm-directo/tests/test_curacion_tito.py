"""Selección completa, sin lectura de reserva ni habilitación de datos IA."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import curar_datos_tito as curacion


# laboratorio-luciano lleva la reserva y generar_seleccion se niega a correr si la ve:
# la curación se regenera en laboratorio-main, que no la tiene.
con_reserva_no_regenera = unittest.skipIf(
    any((curacion.AQUI / 'casos/texto').glob('CV2-T-*')), 'la reserva está en esta rama')


def revision_con_cierre_97_actual(revision: dict) -> dict:
    """La revisión selló CIERRE-97.md tal como estaba en el commit auditado.

    El 2026-10-30 (ee78f6e) se renumeró su riesgo de R23 a R25 y nada más. Se
    comprueba que esa sea la única diferencia antes de aceptar el hash actual: si
    el documento vuelve a cambiar, las pruebas fallan acá en lugar de esconderlo.
    """
    auditado = curacion.codigo_git(curacion.REVISION_CODIGO_COMMIT, 'CIERRE-97.md')
    actual = (curacion.AQUI / 'CIERRE-97.md').read_bytes()
    arte = next(a for a in revision['artefactos'] if a['ruta'] == 'CIERRE-97.md')
    if curacion.sha(auditado) != arte['sha256']:
        raise AssertionError('CIERRE-97.md del commit auditado no coincide con la revisión')
    if auditado.replace(b'(R05, R23)', b'(R05, R25)') != actual:
        raise AssertionError('CIERRE-97.md cambió más allá de la renumeración R23 a R25')
    revision = copy.deepcopy(revision)
    arte = next(a for a in revision['artefactos'] if a['ruta'] == 'CIERRE-97.md')
    arte['sha256'] = curacion.sha(actual)
    return revision


def generar(revision: dict) -> dict:
    """Modo histórico: el código derivado se lee del commit auditado.

    Así la línea base genera sin error y cada prueba negativa falla solo por lo
    que altera, no por la deriva del código actual.
    """
    return curacion.generar_seleccion(
        revision, codigo_historico=curacion.REVISION_CODIGO_COMMIT)


class CuracionTitoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.revision = revision_con_cierre_97_actual(
            json.loads(curacion.REVISION.read_text(encoding='utf-8')))

    @con_reserva_no_regenera
    def test_cada_registro_tiene_destino_y_conserva_regresiones(self):
        paquete = generar(self.revision)
        _, originales, _, _ = curacion.leer_banco()
        por_id = {r['id']: r for r in paquete['banco']}
        self.assertEqual(set(por_id), {r['id'] for r in originales})
        for r in originales:
            self.assertEqual(por_id[r['id']]['texto_sha256'],
                             curacion.sha(r['texto'].encode()))
        self.assertEqual(len(paquete['conversaciones']), len(self.revision['conversaciones']))
        self.assertFalse(paquete['habilitado'])
        casos = {r['case_id']: r for r in paquete['conversaciones']}
        for cid in paquete['regresiones_obligatorias_preservadas']:
            self.assertEqual(casos[cid]['uso'], 'regresion_historica')
        self.assertEqual(casos['TR-12-corta-antes-del-pedido']['seleccion'], 'apartar')
        self.assertEqual(por_id['banco_044_01']['seleccion'], 'conservar')
        self.assertEqual(por_id['banco_044_09']['seleccion'], 'apartar')
        self.assertEqual(por_id['cotidiano_002_01']['seleccion'], 'apartar')

    def test_rechaza_cobertura_incompleta_o_duplicada(self):
        mensajes = {
            ('familias_banco', False): 'Faltan/sobran familias',
            ('familias_banco', True): 'Identificadores repetidos: familia',
            ('conversaciones', False): 'Faltan/sobran conversaciones',
            ('conversaciones', True): 'Identificadores repetidos: case_id',
        }
        for (campo, duplicar), mensaje in mensajes.items():
            with self.subTest(campo=campo, duplicar=duplicar):
                revision = copy.deepcopy(self.revision)
                if duplicar:
                    revision[campo].append(copy.deepcopy(revision[campo][0]))
                else:
                    revision[campo].pop()
                with self.assertRaisesRegex(ValueError, mensaje):
                    generar(revision)

    def test_no_reintroduce_exclusiones_historicas(self):
        revision = copy.deepcopy(self.revision)
        r = next(r for r in revision['familias_banco'] if r['familia']=='cotidiano_002')
        r['variantes_apartadas'] = []
        with self.assertRaisesRegex(ValueError, 'exclusión histórica'):
            curacion.generar_seleccion(revision)

    def test_rechaza_referencias_de_otro_texto_o_revision_humana_ficticia(self):
        cambios = (
            ('conversaciones', 'texto_sha256', 'alterado', 'Cambió el caso revisado'),
            ('familias_banco', 'familia_sha256', 'alterado', 'Familia distinta de la leída'),
            ('conversaciones', 'revision_humana', True, 'Revisión IA inválida'),
            ('familias_banco', 'revision_humana', True, 'presentado como humano'),
        )
        for campo, clave, valor, mensaje in cambios:
            with self.subTest(campo=campo, clave=clave):
                revision = copy.deepcopy(self.revision)
                revision[campo][0][clave] = valor
                with self.assertRaisesRegex(ValueError, mensaje):
                    generar(revision)

    def test_no_habilita_una_seleccion_ia(self):
        revision = copy.deepcopy(self.revision)
        revision['habilitado'] = True
        with self.assertRaisesRegex(ValueError, 'no habilita'):
            curacion.generar_seleccion(revision)

    @con_reserva_no_regenera
    def test_modo_estricto_rechaza_fuente_actual_cambiada(self):
        # entrenar_tito.py y filtro_tito.py cambiaron después de la revisión; cuál
        # aparece primero depende del orden de los artefactos, no del control.
        with self.assertRaisesRegex(ValueError,
                                    r'Artefacto cambiado: (entrenar_tito|filtro_tito)\.py'):
            curacion.generar_seleccion(self.revision)

    @con_reserva_no_regenera
    def test_historico_reporta_deriva_sin_reetiquetar(self):
        paquete = generar(self.revision)
        bloque = paquete['codigo_historico']
        self.assertEqual(bloque['commit'], curacion.REVISION_CODIGO_COMMIT)
        deriva = bloque['deriva_codigo_actual']['filtro_tito.py']
        auditado = next(a['sha256'] for a in self.revision['artefactos']
                        if a['ruta'] == 'filtro_tito.py')
        self.assertEqual(deriva['auditado'], auditado)
        self.assertNotEqual(deriva['actual'], auditado)
        self.assertIn('no el código actual', bloque['advertencia'])

    def test_historico_rechaza_commit_no_autorizado(self):
        with self.assertRaisesRegex(ValueError, 'no autorizado'):
            curacion.generar_seleccion(self.revision, codigo_historico='HEAD')

    def test_historico_no_oculta_pesos_modificados(self):
        revision = copy.deepcopy(self.revision)
        for arte in revision['artefactos']:
            if arte['ruta'] == 'tito_logreg.json':
                arte['sha256'] = 'alterado'
        with self.assertRaisesRegex(ValueError, 'Artefacto cambiado: tito_logreg.json'):
            generar(revision)

    def test_reserva_se_rechaza_por_id_antes_de_abrir_contenido(self):
        banco_historico = curacion.leer_banco()
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            # Solo señuelos sintéticos: no hay contenido de la reserva real.
            for carpeta, extension in (('texto', 'txt'), ('referencia', 'json')):
                destino = raiz / 'casos' / carpeta
                destino.mkdir(parents=True)
                (destino / f'CV2-T-SENUELO.{extension}').write_text('NO PARSEAR')
            with patch.object(curacion, 'AQUI', raiz), patch.object(
                    curacion, 'leer_banco', return_value=banco_historico):
                with self.assertRaisesRegex(ValueError, 'Reserva del proyecto'):
                    curacion.generar_seleccion(self.revision)


if __name__ == '__main__':
    unittest.main()
