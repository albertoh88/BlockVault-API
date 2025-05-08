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

        self.cliente_mock = MagicMock()
        self.db_mock = MagicMock()
        self.collection_mock = MagicMock()

        self.nosql.conect.connection_nosql.return_value = self.cliente_mock
        self.cliente_mock.__getitem__.return_value = self.db_mock  # cliente['mi_base_de_datos]
        self.db_mock.__getitem__.return_value = self.collection_mock  # db['mi_coleccion']

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

        self.fs_mock.exists.return_value = False
        self.fs_mock.put.return_value = 'mock_file_id'

        result = self.nosql.save_file(b'file_content', 'filename.txt')

        self.fs_mock.exists.assert_called_once_with({'filename': 'filename.txt'})
        self.fs_mock.put.assert_called_once_with(b'file_content',filename='filename.txt')

        self.assertEqual(result['message'], 'Archivo guardado')
        self.assertEqual(result['file_id'], 'mock_file_id')

    def test_ultimo_registro(self):

        # Simular find().sort().limit() = lista con un bloque
        self.collection_mock.find.return_value.sort.return_value.limit.return_value = [{'previous_hash': 'mock_previous_hash'}]

        result = self.nosql.ultimo_registro()

        # Verificar que devolvemos el previous_hash correcto
        self.assertEqual(result, 'mock_previous_hash')

        # Verificar que se llamaron los métodos correctos
        self.collection_mock.find.assert_called_once()
        self.collection_mock.find.return_value.sort.assert_called_once_with([('$natural', -1)])
        self.collection_mock.find.return_value.sort.return_value.limit.assert_called_once_with(1)

    def test_save_block(self):
        self.mock_block = {'index': 1, 'data': 'some_hash_data'}

        self.collection_mock.insert_one.return_value.inserted_id = 'mock_id'

        resutl = self.nosql.save_block(self.mock_block)

        self.collection_mock.insert_one.assert_called_once()
        self.collection_mock.insert_one.assert_called_once_with({ 'name': self.mock_block['index'], 'file_hash': self.mock_block['data'],
                                                             'block': self.mock_block, 'enable': True })

    def test_get_last_index_success(self):

        # Verificamos que find_one devuelve un bloque válido, retorna el índice correcto
        self.collection_mock.find_one.return_value = {'index': 1}

        resutl = self.nosql.get_last_index()

        self.collection_mock.find_one.assert_called_once()
        self.collection_mock.find_one.assert_called_once_with({}, sort=[('index', -1)])
        self.assertEqual(resutl, (1))

    def test_get_last_index_none(self):

        self.collection_mock.find_one.return_value = {}

        resutl = self.nosql.get_last_index()

        self.collection_mock.find_one.assert_called_once()
        self.assertEqual(resutl, (0))

    def test_get_last_index_error(self):
        # Simular un error en la base de datos, como una excepción al acceder a la base de datos
        self.collection_mock.find_one.side_effect = Exception('Database error')
        resutl = self.nosql.get_last_index()
        # Asegurar que el retorno sea 0
        self.assertEqual(resutl, 0)
        # Verificamos que el método manejar_error fue llamado
        self.nosql.error_handle.manejar_error.assert_called_once()

    def test_get_file_exists_false(self):
        self.fs_mock.exists.return_value = False

        result = self.nosql.get_file('file_id')

        self.fs_mock.exists.assert_called_once_with({'_id': 'file_id'})

        self.assertEqual(result['message'], 'El archivo no existe')

    def test_get_file_exists_true(self):
        self.fs_mock.exists.return_value = True
        # Simulanfo el metodo get() que devuelva un objeto con .read() que regrese los datos binarios esperados.
        self.fs_mock.get.return_value = MagicMock(read=MagicMock(return_value= b'mock_file.txt'))

        result = self.nosql.get_file('file_id')
        self.fs_mock.exists.assert_called_once_with({'_id': 'file_id'})
        self.fs_mock.get.return_value.read.assert_called_once()
        self.assertEqual(result, b'mock_file.txt')

    def test_get_file_exception(self):
        self.fs_mock.exists.side_effect = Exception('Database error')
        resutl = self.nosql.get_file('file_id')
        self.assertEqual(resutl, None)
        self.nosql.error_handle.manejar_error.assert_called_once()
        self.fs_mock.get.assert_not_called()
        self.fs_mock.get.return_value.read.assert_not_called()

    def test_delete_file_exists_false(self):
        self.fs_mock.exists.return_value = False
        result = self.nosql.delete_file('file_id')
        self.fs_mock.exists.assert_called_once_with({'_id': 'file_id'})
        self.assertEqual(result['message'], 'El archivo no existe')

    def test_delete_file_exists_true(self):
        self.fs_mock.exists.return_value = True
        result = self.nosql.delete_file('file_id')
        self.fs_mock.exists.assert_called_once_with({'_id': 'file_id'})
        self.fs_mock.delete.assert_called_once_with('file_id')
        self.assertEqual(result['message'], 'El archivo fue eliminado con exito')

    def test_delete_file_exception(self):
        self.fs_mock.exists.side_effect = Exception('Database error')
        resutl = self.nosql.delete_file('file_id')
        self.nosql.error_handle.manejar_error.assert_called_once()
        self.fs_mock.delete.assert_not_called()
        self.assertEqual(resutl['message'], 'Error al eliminar el archivo: Database error')