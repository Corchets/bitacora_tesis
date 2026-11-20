"""colab/preparar_colab.py: ubicar las legítimas reales que se subieron a Colab (carpeta o ZIP), dejar zstd disponible,
instalar Ollama con reintentos y descargar sin cortar la corrida. Sin Colab, sin red y sin apt-get: todo con dobles.

Uso (desde experiments/slm-directo):
    python3 -B -m unittest tests.test_preparar_colab -v
"""

from __future__ import annotations

import importlib.util
import io
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace

RAIZ = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("preparar_colab", RAIZ / "colab" / "preparar_colab.py")
prep = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(prep)

ARCHIVOS = {  # un set mínimo en el formato de la custodia
    "set-legitimas/texto/EXT-1.txt": "A: hola\n", "set-legitimas/referencia/EXT-1.json": "{}",
    "set-legitimas/roles-protegida.json": "{}", "set-legitimas/correspondencia.json": "{}",
    "set-zona-gris/texto/EXT-2.txt": "A: hola\n", "set-zona-gris/referencia/EXT-2.json": "{}",
    "set-zona-gris/roles-protegida.json": "{}",
}
BASURA = {"set-legitimas/texto/.DS_Store": "x", "set-legitimas/texto/._EXT-1.txt": "x", "set-zona-gris/referencia/.DS_Store": "x"}


def escribir(base: Path, archivos: dict[str, str]) -> None:
    for nombre, texto in archivos.items():
        (base / nombre).parent.mkdir(parents=True, exist_ok=True)
        (base / nombre).write_text(texto, encoding="utf-8")


def armar_zip(ruta: Path, archivos: dict[str, str]) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ruta, "w") as z:
        for nombre, texto in archivos.items():
            z.writestr(nombre, texto)


def contenido(carpeta: Path) -> list[str]:
    return sorted(str(p.relative_to(carpeta)) for p in carpeta.rglob("*") if p.is_file())


class TestUbicar(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.raiz, self.trabajo = self.tmp / "content", self.tmp / "content" / "legitimas-reales"
        self.raiz.mkdir()
        (self.raiz / "sample_data").mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def ubicar(self, indicada: str = "") -> Path:
        with redirect_stdout(io.StringIO()) as salida:
            limpia = prep.ubicar_legitimas_reales(self.raiz, self.trabajo, indicada)
        self.salida = salida.getvalue()
        return limpia

    def test_la_carpeta_sets_suelta_en_content(self):
        escribir(self.raiz / "sets", ARCHIVOS)
        limpia = self.ubicar()
        self.assertEqual(limpia, self.trabajo / "limpias")
        self.assertEqual(contenido(limpia), sorted(ARCHIVOS))

    def test_la_carpeta_mas_adentro_y_con_otro_nombre(self):
        escribir(self.raiz / "subida" / "legitimas-reales-sets" / "sets", ARCHIVOS)
        self.assertEqual(contenido(self.ubicar()), sorted(ARCHIVOS))

    def test_un_zip_subido_se_descomprime_solo(self):
        armar_zip(self.raiz / "legitimas-reales-sets.zip", {f"sets/{k}": v for k, v in ARCHIVOS.items()})
        self.assertEqual(contenido(self.ubicar()), sorted(ARCHIVOS))
        self.assertIn("Se descomprimió", self.salida)

    def test_un_zip_armado_en_una_mac_queda_limpio(self):
        mac = {f"sets/{k}": v for k, v in {**ARCHIVOS, **BASURA}.items()}
        mac |= {f"__MACOSX/sets/{k}": "x" for k in ARCHIVOS}
        armar_zip(self.raiz / "sets.zip", mac)
        self.assertEqual(contenido(self.ubicar()), sorted(ARCHIVOS), "sin .DS_Store, sin ._* y sin __MACOSX")

    def test_la_basura_de_una_carpeta_tampoco_pasa(self):
        escribir(self.raiz / "sets", {**ARCHIVOS, **BASURA})
        self.assertEqual(contenido(self.ubicar()), sorted(ARCHIVOS))

    def test_la_ruta_indicada_puede_ser_la_carpeta_o_el_zip(self):
        escribir(self.tmp / "otro" / "sets", ARCHIVOS)
        self.assertEqual(contenido(self.ubicar(str(self.tmp / "otro" / "sets"))), sorted(ARCHIVOS))
        self.assertEqual(contenido(self.ubicar(str(self.tmp / "otro"))), sorted(ARCHIVOS), "o la carpeta que la contiene")
        armar_zip(self.tmp / "zips" / "x.zip", {f"sets/{k}": v for k, v in ARCHIVOS.items()})
        self.assertEqual(contenido(self.ubicar(str(self.tmp / "zips" / "x.zip"))), sorted(ARCHIVOS))

    def test_si_la_ruta_indicada_no_existe_busca_igual(self):
        escribir(self.raiz / "sets", ARCHIVOS)
        self.assertEqual(contenido(self.ubicar("/content/no-existe")), sorted(ARCHIVOS))
        self.assertIn("no existe", self.salida)

    def test_al_reejecutar_no_toma_su_propia_copia(self):
        escribir(self.raiz / "sets", ARCHIVOS)
        self.ubicar()
        (self.raiz / "sets" / "set-legitimas" / "texto" / "EXT-9.txt").write_text("A: otra\n", encoding="utf-8")
        self.assertIn("set-legitimas/texto/EXT-9.txt", contenido(self.ubicar()), "vuelve a partir de la subida")

    def test_no_mira_el_repo_ni_los_resultados_ni_los_zip_propios(self):
        escribir(self.raiz / "bitacora_tesis" / "sets", ARCHIVOS)
        escribir(self.raiz / "resultados-exploracion-reales" / "sets", ARCHIVOS)
        armar_zip(self.raiz / "parcial-exploracion-conjuntos.zip", {f"sets/{k}": v for k, v in ARCHIVOS.items()})
        with self.assertRaises(RuntimeError) as error:
            self.ubicar()
        self.assertIn("legitimas-reales-sets.zip", str(error.exception), "dice qué hay que subir")
        self.assertIn("sample_data", str(error.exception), "y qué encontró")

    def test_un_zip_sin_los_dos_sets_no_sirve(self):
        armar_zip(self.raiz / "otra-cosa.zip", {k: v for k, v in ARCHIVOS.items() if k.startswith("set-legitimas")})
        with self.assertRaises(RuntimeError):
            self.ubicar()

    def test_un_zip_no_puede_escribir_fuera_de_su_carpeta(self):
        armar_zip(self.raiz / "malo.zip", {**{f"sets/{k}": v for k, v in ARCHIVOS.items()}, "../../afuera.txt": "x"})
        self.assertEqual(contenido(self.ubicar()), sorted(ARCHIVOS))
        self.assertFalse((self.tmp / "afuera.txt").exists())
        self.assertFalse((self.raiz / "afuera.txt").exists())


def doble(codigos: dict[str, list[int]]):
    """Un `correr` falso: registra las órdenes y devuelve, por programa, los códigos de salida pedidos (0 si no hay más)."""
    llamadas = []

    def correr(orden, **_):
        llamadas.append(list(orden))
        clave = next((k for k in codigos if k in " ".join(orden)), None)
        codigo = codigos[clave].pop(0) if clave and codigos[clave] else 0
        return SimpleNamespace(returncode=codigo)

    return correr, llamadas


class TestZstd(unittest.TestCase):
    def test_si_ya_esta_no_toca_nada(self):
        correr, llamadas = doble({})
        self.assertEqual(prep.asegurar_zstd(correr, which=lambda _: "/usr/bin/zstd"), "ya estaba")
        self.assertEqual(llamadas, [])

    def test_apt_get_actualiza_antes_de_instalar_y_reintenta(self):
        correr, llamadas = doble({})
        vistas = iter([None, None, "/usr/bin/zstd"])  # no está; el primer intento no lo deja; el segundo sí
        self.assertEqual(prep.asegurar_zstd(correr, which=lambda _: next(vistas), dormir=lambda _: None), "apt-get")
        programas = [(o[0], o[-2] if "install" in o else o[-1]) for o in llamadas]
        self.assertEqual([" ".join(o[-2:]) for o in llamadas if "update" in o], ["update -qq"] * 2)
        self.assertEqual(sum("install" in o and o[-1] == "zstd" for o in llamadas), 2)
        self.assertTrue(all(o[0] == "apt-get" for o in llamadas), programas)
        self.assertLess(llamadas.index(next(o for o in llamadas if "update" in o)),
                        llamadas.index(next(o for o in llamadas if "install" in o)))

    def test_sin_apt_get_deja_un_reemplazo_en_python(self):
        with tempfile.TemporaryDirectory() as tmp:
            carpeta = Path(tmp) / "bin"
            correr, llamadas = doble({})
            hay = lambda _: str(carpeta / "zstd") if (carpeta / "zstd").exists() else None  # noqa: E731
            como = prep.asegurar_zstd(correr, which=hay, dormir=lambda _: None, carpeta_bin=carpeta)
            self.assertEqual(como, "reemplazo en Python")
            self.assertTrue((carpeta / "zstd").stat().st_mode & 0o111, "queda ejecutable")
            self.assertIn("zstandard", (carpeta / "zstd").read_text(encoding="utf-8"))
            self.assertEqual(sum("install" in o and "apt-get" in o for o in llamadas), 3, "antes probó apt-get tres veces")
            self.assertTrue(any(o[1:4] == ["-m", "pip", "install"] and o[-1] == "zstandard" for o in llamadas))
            compile((carpeta / "zstd").read_text(encoding="utf-8"), "zstd", "exec")  # el reemplazo es Python válido

    def test_si_nada_funciona_avisa_que_hacer(self):
        with tempfile.TemporaryDirectory() as tmp:
            correr, _ = doble({"import zstandard": [1]})
            with self.assertRaises(RuntimeError) as error:
                prep.asegurar_zstd(correr, which=lambda _: None, dormir=lambda _: None, carpeta_bin=Path(tmp))
            self.assertIn("Reiniciá el entorno", str(error.exception))

    @unittest.skipUnless(importlib.util.find_spec("zstandard"), "sin el módulo zstandard en esta máquina")
    def test_el_reemplazo_descomprime_de_la_entrada_a_la_salida(self):
        import zstandard
        with tempfile.TemporaryDirectory() as tmp:
            guion = Path(tmp) / "zstd"
            guion.write_text(prep.REEMPLAZO_ZSTD, encoding="utf-8")
            comprimido = zstandard.ZstdCompressor().compress(b"hola " * 1000)
            salida = subprocess.run([sys.executable, str(guion), "-d"], input=comprimido, capture_output=True, check=True)
            self.assertEqual(salida.stdout, b"hola " * 1000)


class TestOllama(unittest.TestCase):
    def test_el_instalador_corre_con_pipefail_y_la_version_fija(self):
        correr, llamadas = doble({})
        prep.instalar_ollama("0.40.14", correr, which=lambda _: "/usr/local/bin/ollama", dormir=lambda _: None)
        self.assertEqual(len(llamadas), 1)
        self.assertEqual(llamadas[0][:2], ["bash", "-c"])
        self.assertIn("set -o pipefail", llamadas[0][2], "si curl falla, no pasa por bueno")
        self.assertIn("OLLAMA_VERSION=0.40.14 sh", llamadas[0][2])

    def test_reintenta_si_la_descarga_se_corta_o_no_queda_el_binario(self):
        correr, llamadas = doble({"install.sh": [1, 0, 0]})
        vistas = iter([None, "/usr/local/bin/ollama"])  # el segundo intento sale bien pero sin binario; el tercero, con
        prep.instalar_ollama("0.40.14", correr, which=lambda _: next(vistas), dormir=lambda _: None)
        self.assertEqual(len(llamadas), 3)

    def test_si_no_instala_avisa(self):
        correr, _ = doble({"install.sh": [1, 1, 1]})
        with self.assertRaises(RuntimeError):
            prep.instalar_ollama("0.40.14", correr, which=lambda _: None, dormir=lambda _: None)

    def test_reintentar_la_descarga_del_modelo(self):
        correr, llamadas = doble({"pull": [1, 0]})
        prep.reintentar(["ollama", "pull", "modelo"], "La descarga del modelo", correr, dormir=lambda _: None)
        self.assertEqual(len(llamadas), 2)
        correr, _ = doble({"pull": [1, 1, 1]})
        with self.assertRaises(RuntimeError) as error:
            prep.reintentar(["ollama", "pull", "modelo"], "La descarga del modelo", correr, dormir=lambda _: None)
        self.assertIn("no se repite", str(error.exception))


class TestDescargar(unittest.TestCase):
    def test_sin_colab_arma_el_zip_y_no_corta(self):
        with tempfile.TemporaryDirectory() as tmp:
            carpeta = Path(tmp) / "corrida"
            escribir(carpeta, {"a.txt": "hola"})
            with redirect_stdout(io.StringIO()) as salida:
                archivo = prep.descargar(carpeta, "parcial-prueba", Path(tmp))
            self.assertEqual(archivo, Path(tmp) / "parcial-prueba.zip")
            self.assertEqual(zipfile.ZipFile(archivo).namelist(), ["a.txt"])
            self.assertIn("queda en", salida.getvalue())


class TestScript(unittest.TestCase):
    def test_el_script_busca_las_legitimas_antes_de_instalar_nada(self):
        script = (RAIZ / "colab" / "probar_exploracion_reales.py").read_text(encoding="utf-8")
        orden = [script.index(x) for x in ("prep.ubicar_legitimas_reales(", "conjuntos.preparar_legitimas_reales(",
                                           "prep.asegurar_zstd()", "prep.instalar_ollama(", "'ollama', 'pull'",
                                           "humo_dir = SALIDA / 'humo'")]
        self.assertEqual(orden, sorted(orden))
        self.assertNotIn("apt-get", script, "la instalación pasa toda por preparar_colab.py")
        self.assertNotIn("files.download", script, "y las descargas también")


if __name__ == "__main__":
    unittest.main()
