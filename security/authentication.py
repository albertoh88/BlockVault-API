import json
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from error_handler import Errores

class Authentication:
    def __init__(self, error_handle = None):
        self.error_handle = error_handle or Errores()

    def get_public_key(self, private_key):
        try:
            # Carga la clave privada desde una cadena PEM
            private_key_obj = serialization.load_pem_private_key(private_key.encode(), password=None)

            # Obtener la clave pública
            public_key = private_key_obj.public_key()
            # Convertir la clave pública a formato PEM
            public_pem = public_key.public_bytes(encoding=serialization.Encoding.PEM,
                                                 format=serialization.PublicFormat.SubjectPublicKeyInfo)
            return public_pem.decode()
        except Exception as e:
            self.error_handle.manejar_error(e)
            return None

    # Nota: esta función se usa como demostración para cargar la clave pública desde un archivo.
    # En entornos productivos, se recomienda obtenerla desde un vault seguro o base de datos cifrada.
    def get_server_public_key(self):
        try:
            with open('../server_public_key.pem', 'r') as file:
                return file.read()
        except Exception as e:
            self.error_handle.manejar_error(e)
            return None

    def sign_block(self, block, private_key):
        block_string = json.dumps(block, sort_keys=True).encode()
        signature = private_key.sign(
            block_string,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return signature

    def sign_proof(self, previous_poof, private_key):
        try:
            # Carga la clave privada
            privet_key_obj = serialization.load_pem_private_key(private_key.encode(), password=None)

            # Firma los datos usando SHA256
            signature = privet_key_obj.sign(
                previous_poof.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return signature.hex()
        except Exception as e:
            self.error_handle.manejar_error(e)
            return None

