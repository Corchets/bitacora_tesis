"""Selección completa, sin lectura de reserva ni habilitación de datos IA."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import curar_datos_tito as curacion


class CuracionTitoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.revision = json.loads(curacion.REVISION.read_text(encoding='utf-8'))

    def test_cada_registro_tiene_destino_y_conserva_regresiones(self):
        paquete = curacion.generar_seleccion(
            self.revision, codigo_historico=curacion.REVISION_CODIGO_COMMIT)
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
        for campo in ('familias_banco', 'conversaciones'):
            for duplicar in (False, True):
                with self.subTest(campo=campo, duplicar=duplicar):
                    revision = copy.deepcopy(self.revision)
                    if duplicar:
                        revision[campo].append(copy.deepcopy(revision[campo][0]))
                    else:
                        revision[campo].pop()
                    with self.assertRaises(ValueError):
                        curacion.generar_seleccion(revision)

    def test_no_reintroduce_exclusiones_historicas(self):
        revision = copy.deepcopy(self.revision)
        r = next(r for r in revision['familias_banco'] if r['familia']=='cotidiano_002')
        r['variantes_apartadas'] = []
        with self.assertRaisesRegex(ValueError, 'exclusión histórica'):
            curacion.generar_seleccion(revision)

    def test_rechaza_referencias_de_otro_texto_o_revision_humana_ficticia(self):
        cambios = (
            ('conversaciones', 'texto_sha256', 'alterado'),
            ('familias_banco', 'familia_sha256', 'alterado'),
            ('conversaciones', 'revision_humana', True),
            ('familias_banco', 'revision_humana', True),
        )
        for campo, clave, valor in cambios:
            with self.subTest(campo=campo, clave=clave):
                revision = copy.deepcopy(self.revision)
                revision[campo][0][clave] = valor
                with self.assertRaises(ValueError):
                    curacion.generar_seleccion(revision)

    def test_no_habilita_una_seleccion_ia(self):
        revision = copy.deepcopy(self.revision)
        revision['habilitado'] = True
        with self.assertRaisesRegex(ValueError, 'no habilita'):
            curacion.generar_seleccion(revision)

    def test_modo_estricto_rechaza_fuente_actual_cambiada(self):
        with self.assertRaisesRegex(ValueError, 'Artefacto cambiado: filtro_tito.py'):
            curacion.generar_seleccion(self.revision)

    def test_historico_reporta_deriva_sin_reetiquetar(self):
        paquete = curacion.generar_seleccion(
            self.revision, codigo_historico=curacion.REVISION_CODIGO_COMMIT)
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
        with self.assertRaises(ValueError):
            curacion.generar_seleccion(
                revision, codigo_historico=curacion.REVISION_CODIGO_COMMIT)

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
