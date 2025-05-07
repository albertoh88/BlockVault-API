import unittest
from unittest.mock import MagicMock, patch
from database.sql import Sql
from database.nosql import Nosql
from connection import Connection
from error_handler import Errores


class TestDatabase(unittest.TestCase):


    def setUp(self):
        # Inicializar las instancias de las clases a testear
        self.cursor_mock = MagicMock()

        self.sql = Sql()
        self.sql.error_handle = MagicMock()
        self.conecction_mock = MagicMock()
        self.conecction_mock.cursor.return_value = self.cursor_mock
        # Mockear el comportamiento del método de conexión
        self.sql.conect.connection_sql = MagicMock(return_value=self.conecction_mock)

        self.nosql = Nosql()
        self.nosql.error_handle = MagicMock()
        self.nosql.conect.connection_nosql = MagicMock()
        self.fs_mock = MagicMock()
        self.gridfs_patch = patch('database.nosql.gridfs.GridFS', return_value=self.fs_mock)
        self.gridfs_patch.start()

    def test_save_hash_file(self):

        # Simular el comportamiento del cursor cuando se ejecuta una llamada al procedimiento
        self.cursor_mock.callproc.return_value = None
        self.cursor_mock.commit.return_value = None

        # Llamar al método que estamos probando
        self.sql.save_hash_file('hash_block', 'hash_file', 1, 2, 'file_name')

        # Verificar que se llamaron los métodos correctamente
        self.conecction_mock.cursor.assert_called_once()
        self.cursor_mock.callproc.assert_called_once_with('registro', ['hash_block', 'hash_file', 1, 2, 'file_name'])
        self.conecction_mock.commit.assert_called_once()

    def test_ultimo_hash_exists(self):
        # Mockear el cursor y simular el comportamiento de 'fetchone'
        self.cursor_mock.callproc.return_value = (1, ) # Simular que la función 'hash_exists' devuelve 1 (True)

        # Llamamos al método
        result = self.sql.ultimo_hash('previous_hash')

        # Verificamos que el resultado sea True
        self.assertTrue(result)
        self.cursor_mock.execute.assert_called_once_with('SELECT hash_exists(%s);', ('previous_hash',))

    def test_file_exists(self):
        # Mokear el cursor y simular que 'fetchone' devuelve (1, )
        self.cursor_mock.fetchone.return_value = (1, ) # Simular que el archivo existe

        # Llamar al método
        result = self.sql.file_exists('file_name')

        # Verificar que el resultado sea True
        self.assertTrue(result)
        self.cursor_mock.execute.assert_called_once_with('SELECT file_exists(%s);', ('file_name',))

    def test_file_data(self):
        # Mokear el cursor y simular que 'fetchone' devuelve los valores esperados
        self.cursor_mock.fetchone.return_value = (1, 'Some message') # Simulamos la salida del procedimiento

        # Llamar al método
        file_id = self.sql.file_data('file_name')

        # Vereficar que el id del archivo es correcto
        self.assertEqual(file_id, 1)
        self.cursor_mock.execute.assert_any_call('CALL file_id(%s, @idfile, @message);', 'file_name')
        self.cursor_mock.execute.assert_any_call('SELECT @idfile, @message;')

    def test_file_data_exception(self):
        # Mokear para que lance una excepción al ejecutar la consulta
        self.cursor_mock.execute.side_effect = Exception('Database error')

        # Llamar al método y verificar que se maneje la excepción
        file_id = self.sql.file_data('file_name')

        # Verificar que no se haya retornado un id
        self.assertIsNone(file_id)
        self.sql.error_handle.manejar_error.assert_called_once()

    def tearDown(self):
        self.gridfs_patch.stop()

    def test_save_file(self):
        cliente_mock = MagicMock()
        self.nosql.conect.connection_nosql.return_value = cliente_mock

        self.fs_mock.exists.return_value = False
        self.fs_mock.put.return_value = 'mock_file_id'

        result = self.nosql.save_file(b'file_content', 'filename.txt')

        self.fs_mock.exists.assert_called_once_with({'filename': 'filename.txt'})
        self.fs_mock.put.assert_called_once_with(b'file_content',filename='filename.txt')

        self.assertEqual(result['message'], 'Archivo guardado')
        self.assertEqual(result['file_id'], 'mock_file_id')

    def test_ultimo_registro(self):
        cliente_mock = MagicMock()
        db_mock = MagicMock()
        collection_mock = MagicMock()

        self.nosql.conect.connection_nosql.return_value = cliente_mock
        cliente_mock.__getitem__.return_value = db_mock # cliente['mi_base_de_datos]
        db_mock.__getitem__.return_value = collection_mock # db['mi_coleccion']

        # Simular find().sort().limit() = lista con un bloque
        collection_mock.find.return_value.sort.return_value.limit.return_value = [{'previous_hash': 'mock_previous_hash'}]

        result = self.nosql.ultimo_registro()

        # Verificar que devolvemos el previous_hash correcto
        self.assertEqual(result, 'mock_previous_hash')

        # Verificar que se llamaron los métodos correctos
        collection_mock.find.assert_called_once()
        collection_mock.find.return_value.sort.assert_called_once_with([('$natural', -1)])
        collection_mock.find.return_value.sort.return_value.limit.assert_called_once_with(1)

    def test_save_block(self):
        cliente_mock = MagicMock()
        db_mock = MagicMock()
        collection_mock = MagicMock()
        mock_block = {'index': 1, 'data': 'some_hash_data'}

        self.nosql.conect.connection_nosql.return_value = cliente_mock
        cliente_mock.__getitem__.return_value = db_mock
        db_mock.__getitem__.return_value = collection_mock

        collection_mock.insert_one.return_value.inserted_id = 'mock_id'

        resutl = self.nosql.save_block(mock_block)

        collection_mock.insert_one.assert_called_once()
        collection_mock.insert_one.assert_called_once_with({ 'name': mock_block['index'], 'file_hash': mock_block['data'],
                                                             'block': mock_block, 'enable': True })



    def test_get_last_index(self):
        pass

    def test_get_file(self):
        pass

    def test_delete_file(self):
        pass