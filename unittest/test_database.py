import unittest
from unittest.mock import MagicMock, patch
from database.sql import Sql
from database.nosql import Nosql
from connection import Connection
from error_handler import Errores


class TestDatabase(unittest.TestCase):


    def setUp(self):
        # Inicializar las instancias de las clases a testear
        self.sql = Sql()
        self.sql.error_handle = MagicMock()
        self.nosql = Nosql()
        self.nosql.error_handle = MagicMock()
        self.conecction_mock = MagicMock()

        # Mockear el comportamiento del método de conexión
        self.sql.conect.connection_sql = MagicMock(return_value=self.conecction_mock)

    def test_save_hash_file(self):
        # Mockear el cursor y sus comportamiento
        cursor_mock = MagicMock()
        self.conecction_mock.cursor.return_value = cursor_mock

        # Simular el comportamiento del cursor cuando se ejecuta una llamada al procedimiento
        cursor_mock.callproc.return_value = None
        cursor_mock.commit.return_value = None

        # Llamar al método que estamos probando
        self.sql.save_hash_file('hash_block', 'hash_file', 1, 2, 'file_name')

        # Verificar que se llamaron los métodos correctamente
        self.conecction_mock.cursor.assert_called_once()
        cursor_mock.callproc.assert_called_once_with('registro', ['hash_block', 'hash_file', 1, 2, 'file_name'])
        self.conecction_mock.commit.assert_called_once()

    def test_ultimo_hash_exists(self):
        # Mockear el cursor y simular el comportamiento de 'fetchone'
        cursor_mock = MagicMock()
        self.conecction_mock.cursor.return_value = cursor_mock
        cursor_mock.callproc.return_value = (1, ) # Simular que la función 'hash_exists' devuelve 1 (True)

        # Llamamos al método
        result = self.sql.ultimo_hash('previous_hash')

        # Verificamos que el resultado sea True
        self.assertTrue(result)
        cursor_mock.execute.assert_called_once_with('SELECT hash_exists(%s);', ('previous_hash',))
