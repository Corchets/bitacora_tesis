"""Comportamiento de la variante experimental, con modelos deterministas."""
import sys
import unittest
import json
import tempfile
import threading
from contextlib import redirect_stdout
import io
from http.server import HTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import correr
from casos import Linea
from filtro_tito import TitoGuion
from test_filtro_tito import SLMGuion
from test_ensayo import OllamaFalso
from tito_viejo_2 import TitoViejo20


class TestTitoViejo20(unittest.TestCase):
    def test_acumula_sin_repetir_y_consulta_con_contexto_sin_indicio(self):
        lineas = [Linea('A', 'TRANSFERENCIA'), Linea('B', 'transferencia'),
                  Linea('A', 'Su número del documento'), Linea('B', 'Continuemos')]
        f = TitoViejo20(TitoGuion({1: .2, 2: .2, 3: .2, 4: .39}), SLMGuion())
        filas = list(correr.procesar_caso(f, lineas))
        self.assertEqual([r.consulta for _, _, r, _ in filas], ['omitida', 'omitida', 'omitida', 'slm_valida'])
        self.assertEqual(f.vistas, {'transferencia', 'numero del documento'})
        mensaje, contexto = f.slm.recibido[0]
        self.assertEqual(contexto, tuple(lineas))
        self.assertNotIn('filtro previo', mensaje)
        self.assertNotIn('puntaje', mensaje)

    def test_coincidencia_superpuesta_y_otra_aparicion_independiente(self):
        f = TitoViejo20(TitoGuion(), SLMGuion())
        f._registrar('número del documento y otro documento')
        self.assertEqual(f.vistas, {'numero del documento', 'documento'})
        f.reiniciar()
        f._registrar('NÚMERO DEL DOCUMENTO')
        self.assertEqual(f.vistas, {'numero del documento'})

    def test_fallo_reinicia_y_no_agrega_indicio(self):
        f = TitoViejo20(TitoGuion(fallos={1}), SLMGuion())
        salida = list(correr.procesar_caso(f, [Linea('A', 'te ganaste')]))[0][2]
        self.assertEqual(salida.tito_error, 'tito_caido')
        self.assertEqual(salida.consulta, 'slm_valida')
        self.assertNotIn('filtro previo', f.slm.recibido[0][0])
        f.reiniciar()
        self.assertFalse(f.vistas)
        self.assertFalse(f.estado.activado)

    def test_corredor_compara_y_registra_configuracion(self):
        servidor = HTTPServer(('127.0.0.1', 0), OllamaFalso)
        hilo = threading.Thread(target=servidor.serve_forever, daemon=True)
        hilo.start()
        try:
            with tempfile.TemporaryDirectory() as carpeta, redirect_stdout(io.StringIO()):
                correr.main(['--modelos', 'modelo-falso:1b', '--casos', 'SC-WA-CODE-01-e01',
                             '--sin-reglas', '--filtro-tito', '--tito-viejo-2',
                             '--tito-puntajes', '1=0.5', '--url',
                             f'http://127.0.0.1:{servidor.server_port}', '--salida', carpeta])
                corrida, = Path(carpeta).iterdir()
                manifiesto = json.loads((corrida / 'manifiesto.json').read_text())
                self.assertIn('tito-viejo-2', {c['detector'] for c in manifiesto['configs']})
                self.assertFalse(manifiesto['tito_viejo_2']['indicio_a_slm'])
                self.assertIn('tito-viejo-2', (corrida / 'actualizaciones.csv').read_text(encoding='utf-8-sig'))
        finally:
            servidor.shutdown()
            servidor.server_close()
            hilo.join()

    def test_limites_de_palabra_y_continuidad(self):
        f = TitoViejo20(TitoGuion({1: .5}), SLMGuion(alertas={2}))
        lineas = [Linea('A', 'documentos y transferencias'), Linea('B', 'Listo'), Linea('A', 'futuro')]
        filas = list(correr.procesar_caso(f, lineas))
        self.assertEqual(len(filas), 2)
        self.assertFalse(f.vistas)
        self.assertEqual(len(f.slm.recibido), 2)


if __name__ == '__main__':
    unittest.main()
