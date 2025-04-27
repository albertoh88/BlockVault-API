import datetime
import hashlib
import json
from error_handler import Errores
from database import sql, nosql
from security import hashing
from security.authentication import Authentication

class Blockchain:
    def __init__(self):
        self.chain = [] # Cadena que contiene los bloques
        self.db_nosql = nosql.Nosql()
        self.db_sql = sql.Sql()
        self.authentication = Authentication()
        self.error_handle = Errores()

    def create_block(self, file_hash, metadatos, private_key):
        try:
            # Obteniendo el hash del último bloque registrado en la BD NoSQL
            previous_hash = self.get_previous_hash()
            if previous_hash is None:
                return {'message': 'Error: No se puedo obtener el hash del último bloque'}

            # Verificando la integridad del último bloque en la BD NoSQL
            if not self.db_sql.ultimo_hash(previous_hash):
                return {'message': 'Error: La integridad del último bloque está comprometida'}

            # Obtener la prueba de autoridad (PoA)
            proof_data = self.proof_of_authority(previous_hash, private_key)
            if 'message' in proof_data:
                return proof_data # Error si la clave privada no es del servidor

            # Obteniendo el ultimo index
            index = self.db_nosql.get_last_index()
            if index is None:
                return {'message': 'Error: No se pudo obtener el índice del último bloque'}
            index += 1

            # Construcción del bloque
            block = {'index': index,
                     'timestamp': str(datetime.datetime.now()),
                     'data': file_hash,
                     'previous_hash': previous_hash,
                     'metadatos': metadatos,
                     'proof': proof_data['proof'],
                     'validator': proof_data['validator']
            }

            # Firma digital del proof
            block['proof_signature'] = self.authentication.sign_proof(str(block['proof']), private_key)

            # Calcular el hash del bloque antes de la firma digital
            block['hash'] = self.hash(block)

            # Crear la firma digital usando la clave privada del validador
            block['signature'] = self.authentication.sign_block(block, private_key)

            # Guarda el bloque en la BD NoSQL
            id_block = self.db_nosql.save_block(block)
            if id_block is None:
                return {'message': 'Error: No se pudo guarda el bloque en la BD NoSQL'}

            # Guardar el hash en la BD SQL
            self.db_sql.save_hash_file(block['hash'], file_hash, metadatos['file_id'], id_block, metadatos['nombre'])

            return {'message': 'Registro agregado con suceso', 'block': block['hash']}

        except Exception as e:
            self.error_handle.manejar_error(e)
            return {'message': f'Error al agregar el bloque: {str(e)}'}

    def get_previous_hash(self):
        previous_hash = self.db_nosql.ultimo_registro()
        return previous_hash

    def proof_of_authority(self, previous_proof, private_key):
        try:
            # Obtner la clave pública del servidor a partir de la clave privada
            server_public_key = self.authentication.get_public_key(private_key)

            # Verificar que la clave corresponde al servidor (único validador)
            if server_public_key != self.authentication.get_server_public_key():
                return {'message': 'Error: Clave privada incorrecta para validación'}

            # Firmar el previous_proof con la clave privada del servidor
            proof = self.authentication.sign_proof(previous_proof, private_key)

            return {'proof': proof, 'validador': server_public_key}
        except Exception as e:
            self.error_handle.manejar_error(e)
            return {'message': f'Error en el PoA: {str(e)}'}

    def hash(self, block):
        encoded_block = json.dump(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
