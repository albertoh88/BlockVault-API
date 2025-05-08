import unittest
from unittest.mock import MagicMock, patch
from blockchain.blockchain import Blockchain

class TestBlockchain(unittest.TestCase):

    def setUp(self):
        self.blockchain = Blockchain()
        # Mockear bases de datos y autenticación
        self.blockchain.db_sql = MagicMock()
        self.blockchain.db_nosql = MagicMock()
        self.blockchain.authentication = MagicMock()
        self.blockchain.error_handle = MagicMock()
        self.blockchain.error_handle.manejar_error = MagicMock(
            side_effect=lambda e, levantar=True: {'status': 400, 'detail': str(e)}
        )

    def test_save_block_error(self):

        self.blockchain.proof_of_authority = MagicMock()
        self.blockchain.hash = MagicMock()

        self.blockchain.db_nosql.save_block.return_value = None
        self.blockchain.db_nosql.get_last_index.return_value = 1

        self.blockchain.authentication.get_public_key.return_value = 'server_pub_key'
        self.blockchain.authentication.get_server_public_key.return_value = 'server_pub_key'
        self.blockchain.authentication.sign_proof.return_value = 'sing_proof'
        self.blockchain.authentication.sign_block.return_value = 'block_signature'
        self.blockchain.hash.return_value = 'block_hash'
        self.blockchain.proof_of_authority.return_value = {'proof': 'proof_value', 'validator': 'validator'}

        self.blockchain.db_sql.ultimo_hash.return_value = True

        result = self.blockchain.create_block('test_file_hash', {'file_id': 1, 'nombre': 'test_file'}, 'private_key')

        self.blockchain.error_handle.manejar_error.assert_called_once()
        self.assertEqual(result, {'detail': "No se pudo guarda el bloque en la BD NoSQL", 'status': 400})

    def test_create_block_exception(self):
        self.blockchain.db_nosql.get_last_index.return_value = True

        self.blockchain.authentication.get_public_key.return_value = 'server_pub_key'
        self.blockchain.authentication.get_server_public_key.return_value = 'server_pub_key'
        self.blockchain.authentication.sign_proof.return_value = 'sign_proof'
        self.blockchain.proof_of_authority('previous_proof', 'private_key')

        self.blockchain.db_sql.ultimo_hash.return_value = True

        result = self.blockchain.create_block('test_file_hash', {'file_id': 1, 'nombre': 'test_file'}, 'private_key')

        self.blockchain.error_handle.manejar_error.assert_called_once()
        self.assertEqual(result, {'message': "Error al agregar el bloque: 'validator'"})

    def test_get_last_index_error(self):

        self.blockchain.db_nosql.get_last_index.return_value = None

        self.blockchain.authentication.get_public_key.return_value = 'server_pub_key'
        self.blockchain.authentication.get_server_public_key.return_value = 'server_pub_key'
        self.blockchain.authentication.sign_proof.return_value = 'sign_proof'
        self.blockchain.proof_of_authority('previous_proof', 'private_key')

        self.blockchain.db_sql.ultimo_hash.return_value = True

        result = self.blockchain.create_block('test_file_hash', {'file_id': 1, 'nombre': 'test_file'}, 'private_key')

        self.blockchain.error_handle.manejar_error.assert_called_once()
        self.assertEqual(result, {'detail': 'No se pudo obtener el índice del último bloque', 'status': 400})

    def test_get_previous_hash_success(self):
        self.blockchain.db_nosql.ultimo_registro.return_value = 'sbc123'
        result = self.blockchain.get_previous_hash()
        self.assertEqual(result, 'sbc123')

    def test_create_block_no_previous_hash(self):
        self.blockchain.get_previous_hash = MagicMock(return_value=None)
        self.blockchain.db_sql.ultimo_hash.return_value = False

        result = self.blockchain.create_block('filehash', {}, 'private_key')
        self.assertIn('No se pudo obtener el hash del último bloque', result['detail'])
        self.blockchain.error_handle.manejar_error.assert_called_once()

    def test_create_block_invalid_integrity(self):
        self.blockchain.get_previous_hash = MagicMock(return_value='sbc123')
        self.blockchain.db_sql.ultimo_hash.return_value = False
        resutl = self.blockchain.create_block('filehash', {}, 'private_key')
        self.assertIn('La integridad del último bloque está comprometida', resutl['detail'])
        self.blockchain.error_handle.manejar_error.assert_called_once()

    def test_create_block_invalid_proof_of_authority(self):
        self.blockchain.get_previous_hash = MagicMock(return_value='sbc123')
        self.blockchain.db_sql.ultimo_hash.return_value = True
        self.blockchain.proof_of_authority = MagicMock(return_value={'message': 'Error: Clave privada incorrecta'})
        resutl = self.blockchain.create_block('filehash', {}, 'private_key')
        self.assertIn('Error', resutl['detail'])
        self.blockchain.error_handle.manejar_error.assert_called_once()

    def test_hash_consistency(self):
        block = {'index': 1, 'data': 'some data'}
        import json, hashlib
        encoded_block = json.dumps(block, sort_keys=True).encode()
        expected_hash = hashlib.sha256(encoded_block).hexdigest()
        actual_hash = self.blockchain.hash(block)
        self.assertEqual(expected_hash, actual_hash)

    def test_proof_of_authority_success(self):
        self.blockchain.authentication.get_public_key.return_value = 'server_pub_key'
        self.blockchain.authentication.get_server_public_key.return_value = 'server_pub_key'
        self.blockchain.authentication.sign_proof.return_value = 'sign_proof'
        result = self.blockchain.proof_of_authority('previous_proof', 'private_key')
        self.assertEqual(result['proof'], 'sign_proof')
        self.assertEqual(result['validador'], 'server_pub_key')

    def test_proof_of_authority_invalid_key(self):
        self.blockchain.authentication.get_public_key.return_value = 'wrong_pub_key'
        self.blockchain.authentication.get_server_public_key.return_value = 'server_pub_key'
        result = self.blockchain.proof_of_authority('previous_proof', 'private_key')
        self.assertIn('Clave privada incorrecta para validación', result['detail'])
        self.blockchain.error_handle.manejar_error.assert_called_once()

    def test_create_block_success(self):
        # Mocks previos
        self.blockchain.get_previous_hash = MagicMock(return_value='sbc123')
        self.blockchain.db_sql.ultimo_hash.return_value = True

        # Mock de firmas digitales - muy importante para evitar MagicMock dentro del bloque
        self.blockchain.authentication.sign_proof = MagicMock(return_value='signed_proof_signature')
        self.blockchain.authentication.sign_block = MagicMock(return_value='block_signature')

        # Patch del proof_of_authority solo dentro de este test
        with patch.object(self.blockchain, 'proof_of_authority', return_value={'proof': 'sign_proof', 'validator': 'server_pub_key'}):

            # Mock de get_last_index
            self.blockchain.db_nosql.get_last_index.return_value = 0

            # Mock del guardado en la base de datos
            self.blockchain.db_nosql.save_block.return_value = 'bloock_id'
            self.blockchain.db_sql.save_hash_file.return_value = True

            # Datso de prueba
            file_hash = 'filehash123'
            metadatos = {'file_id': 1, 'nombre': 'testfile.txt'}
            private_key = 'private_key'

            # Ejecutar create_block
            result = self.blockchain.create_block(file_hash, metadatos, private_key)

            # Verificar resultado exitoso
            self.assertIn('Registro agregado con suceso', result['message'])
            self.assertIn('block', result)
            self.assertIsInstance(result['block'], str)

            # Verificar que save_block feu llamado una vez
            self.blockchain.db_nosql.save_block.assert_called_once()

            # Obtener el argumento del bloque pasado a save_block
            self.blockchain.db_nosql.save_block.assert_called_once()

            # Obtener el argumento del bloque pasado a save_block
            save_block = self.blockchain.db_nosql.save_block.call_args[0][0]

            # Verificar que el bloque tenga las claves correctas
            expected_keys = [
                'index', 'timestamp', 'data', 'previous_hash', 'metadatos',
                'proof', 'validator', 'proof_signature', 'hash', 'signature'
            ]

            for key in expected_keys:
                self.assertIn(key, save_block)
