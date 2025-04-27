import unittest
import json
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from unittest.mock import MagicMock

# Importando la funcion sing_block desde security\authentication.py
from security.authentication import Authentication

class TestAuthentication(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Generamos una clave privada y pública para las pruebas.

        cls.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        cls.public_key = cls.private_key.public_key()

        # Generamos una clave privada en formato pem para las pruebas
        private_pem = cls.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode()

        cls.private_key_pem_valid = private_pem

        cls.private_key_pem_invalid = 'private-key-pem-invalid'

        cls.previous_proof = 'dato para firmar'

    def test_get_public_key_valid(self):
        auth = Authentication()
        resultado = auth.get_public_key(self.private_key_pem_valid)
        print(resultado)
        self.assertTrue(resultado.startswith("-----BEGIN PUBLIC KEY-----"))

    def test_get_public_key_invalid(self):
        mock_error_handler = MagicMock()
        auth = Authentication(error_handle=mock_error_handler)
        resultado = auth.get_public_key(self.private_key_pem_invalid)
        self.assertIsNone(resultado)

        mock_error_handler.manejar_error.assert_called_once()

    def test_sign_block_valid_signature(self):
        # Verifica que la firma generada sea válida con la clave correcta
        block = {'index': 1, 'data': 'Test block'}
        signature = Authentication.sign_block(self, block, self.private_key)

        # Convertimos el bloque a JSON para verificar la firma
        block_string = json.dumps(block, sort_keys=True).encode()

        try:
            self.public_key.verify(
                signature,
                block_string,
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            valid = True
        except Exception:
            valid = False

        self.assertTrue(valid, 'La firma generada no es valida')

    def test_sign_block_invalid_signature(self):
        # Verifica que la firma falle con una clave incorrecta.

        block = {'index': 1, 'data': 'Test block'}
        signature = Authentication.sign_block(self, block, self.private_key)

        # genaramos otra clave privada diferente.
        other_private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        other_private_key = other_private_key.public_key()

        block_string = json.dumps(block, sort_keys=True).encode()

        with self.assertRaises(Exception):
            other_private_key(
                signature,
                block_string,
                padding.PKCS1v15(),
                hashes.SHA256()
            )

    def test_get_server_public_key_success(self):
        # Crear archivo de prueba
        key_content = "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvTmeEEIUzCQ0OlCoR78KNeTq+i/RtrMkia8L736ybmJfylFtYJk+UZ3Z/Weaq69PLL2OwxxxwMh+kc4lyq9XmRdDnU4QR8g8zmnnSS95qFYuWgg+m3zpL4irfUDULFiJ7D/rTAckuCe1o/SlSkHTRQC63yrgh+UU96E1GniltyEMVD6Ui0pVW6r6TVWOdA2W+HX4W5IcyZ21RCObooo6DUZctms9OWUGV4RYvWE82d1J/38SZBpQ2eqBKwx9Ag/ABL6DgEVTRuYFZbdm2hlsUwdqROkeQXgptwhaOg9bd+C9lwk19TxuIDR6qDof5yr7lwEQpKPMBHnEU7N05yqfawIDAQAB\n-----END PUBLIC KEY-----"

        with open('../server_public_key.pem', 'w') as f:
            f.write(key_content)

        auth = Authentication()
        resultado = auth.get_server_public_key()
        self.assertEqual(resultado, key_content)

    def test_get_server_public_key_not_fount(self):
        # Asegurar de no exista
        import os
        if os.path.exists('../server_public_key.pem'):
            print('existe')
            os.remove('../server_public_key.pem')

        mock_error_handle = MagicMock()
        auth = Authentication()
        auth.error_handle = mock_error_handle

        resultado = auth.get_server_public_key()
        self.assertIsNone(resultado)

        mock_error_handle.manejar_error.assert_called_once()

    def test_sign_proof_valid_key(self):
        auth = Authentication()
        auth.error_handle = MagicMock() # Mockeamos el handler de errores

        signature = auth.sign_proof(self.previous_proof, self.private_key_pem_valid)

        # Aseguramos que la firma es un string en hexadecimal
        self.assertIsInstance(signature, str)
        self.assertTrue(all(c in '0123456789abcdef' for c in signature.lower()))

        auth.error_handle.manejar_error.assert_not_called()

    def test_sign_proof_invalid_key(self):
        auth = Authentication()
        mock_error_handle = MagicMock()
        auth.error_handle = mock_error_handle

        invalid_key = 'clave inválida'

        result = auth.sign_proof(self.previous_proof, invalid_key)

        # Deberia retornar None
        self.assertIsNone(result)

        # El manejador de errores debió ser llamado
        mock_error_handle.manejar_error.assert_called_once()
