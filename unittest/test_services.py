import unittest
import jwt
import datetime
from services.services import Services
from decouple import config
from fastapi import HTTPException
from unittest.mock import MagicMock, patch

class TestServices(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.services = Services() # Crea la instancia de la clase Services

        # Gerar tokens de prueba
        cls.token_valido = jwt.encode(
            {
                'email': 'algunacosa@otracosa.com',
                'username': 'elloco',
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            },
            config('SECRET_KEY'),
            algorithm='HS256'
        )

        cls.token_expirado = jwt.encode(
            {
                'email': 'algunacosa@otracosa.com',
                'username': 'elloco',
                'exp': datetime.datetime.utcnow() - datetime.timedelta(hours=1)
            },
            config('SECRET_KEY'),
            algorithm='HS256'
        )

        cls.token_invalido = jwt.encode(
            {
                'email': 'algunacosa@otracosa.com',
                'username': 'elloco',
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            },
            'clave_incorrecta', # Se firma con otra clave incorrecta
            algorithm='HS256'
        )

        cls.token_mal_formado = 'esto-no-es-un-token-jwt'

        cls.token_exception = MagicMock()

    def test_token_valido(self):
        result = self.services.verify_and_validate_token(self.token_valido)
        self.assertIsInstance(result, dict)
        self.assertIn('email', result) # Verificar que el token decodificado contiene el email
        self.assertIn('username', result) # Debe contener el campo 'username'

    def test_token_expirado(self):
        with self.assertRaises(HTTPException) as cm:
            self.services.verify_and_validate_token(self.token_expirado)

        # Verificar que el código de error es 401
        self.assertEqual(cm.exception.status_code, 401)
        self.assertEqual(cm.exception.detail, 'El token ha expirado')

    def test_token_invalido(self):
        with self.assertRaises(HTTPException) as cm:
            self.services.verify_and_validate_token(self.token_invalido)

        # Verificar que el código de error es 401
        self.assertEqual(cm.exception.status_code, 401)
        self.assertEqual(cm.exception.detail, 'El token no es válido')

    def test_token_mal_formado(self):
        with self.assertRaises(HTTPException) as cm:
            self.services.verify_and_validate_token(self.token_mal_formado)

        # Verificar que el código de error es 401
        self.assertEqual(cm.exception.status_code, 401)
        self.assertEqual(cm.exception.detail, 'El token está mal formado')

    def test_token_exception(self):
        with patch('services.services.config', side_effect=Exception('fallo en config')):
            result = self.services.verify_and_validate_token('token')

        self.assertEqual(result['status'], 500)
        self.assertEqual('Error interno del servidor: Error genérico: fallo en config', result['detail'])
