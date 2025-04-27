import unittest
import io
import hashlib
from security.hashing import Hashing


class TestHashing(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.hashing_tool = Hashing() # Crea la instancia de la clase Hashing

    def test_hashing_archivo_binario_valido(self):
        contenido = b'Este es un contenido de prueba para hashing'
        archivo_similar = io.BytesIO(contenido)

        resultado = self.hashing_tool.hashing(archivo_similar)

        esperando = hashlib.sha256(contenido).hexdigest()
        self.assertEqual(resultado, esperando)

    def test_hashing_archivo_invalido_sin_read(self):
        class ObjetoSinRead:
            pass

        archivo_invalido = ObjetoSinRead()
        resultado = self.hashing_tool.hashing(archivo_invalido)

        self.assertIsNone(resultado)
