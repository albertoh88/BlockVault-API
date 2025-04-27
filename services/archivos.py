import mimetypes
import config
import os
from pathlib import Path
from error_handler import Errores
from database import nosql, sql
from security.hashing import Hashing
from blockchain.blockchain import Blockchain


class Archivo:
    def __init__(self):
        self.error_handle = Errores()
        self.nosql_bd = nosql.Nosql()
        self.sql_bd = sql.Sql()
        self.blockchain = Blockchain()
        self.hash = Hashing()

    async def uploadfile(self, file_encrypt, token_decode):
        try:
            # Obteniendo el nombre del archivo
            filename = file_encrypt.filename or 'archivo_desconocido'

            # Leer el contenido del archivo (esto lo consume completamente)
            contents = await file_encrypt.read()

            # Obteniendo el tamaño del archivo
            file_size = len(contents)

            # Obteniendo la extencion del archivo
            file_extension = filename.split('.')[-1] if '.' in filename else 'desconocido'

            # Hash del archivo
            hashing_file = self.hash.hashing(contents)

            # Guardar en la base de datos NoSQL
            result = self.nosql_bd.save_file(contents, filename)

            # Extraer metadatos del archivo cifrado
            metadatos = {
                'nombre': filename,
                'tamaño': file_size,
                'tipo': file_encrypt.content_type or 'desconocido',
                'extension': file_extension,
                'file_id': str(result['file_id'])
            }

            # Crear un bloque en la blockchain
            self.blockchain.create_block(hashing_file, metadatos, token_decode['clave_privada'])

            return {'message': 'Archivo subido con exito', 'nombre': filename}

        except Exception as e:
            self.error_handle.manejar_error(e)
            return {'message': f'Error: No se pudo guardar el archivo {str(e)}'}

    def deletefile(self, file_name, token_decode):
        try:
            if not self.sql_bd.file_exists(file_name):
                return {'message': 'Error: Archivo no existe'}

            # Obtener el ID del archivo desde SQL
            file_id = self.sql_bd.file_data(file_name)

            # Obtener el archivo desde la base de datos NoSQL (Gridfs)
            file_data = self.nosql_bd.get_file(file_id)

            if file_data is None:
                return {'message': 'Error: No se pudo recuperar el archivo desde la BD'}

            # Calculando el hash del archivo
            hashing_file = self.hash.hashing(file_data.read())  # Lee el contenido binario del archivo

            metadatos = {
                'nombre': file_name,
                'tamaño': os.fstat(file_data.fileno()).st_size,
                'tipo': file_data.content_type,
                'extension': filename.split('.')[-1],
                'file_id': file_id
            }

            # Registrar en el blockchain la operacion de eliminacion
            self.blockchain.create_block(hashing_file, metadatos, token_decode['clave_privada'])

            # Eliminando el archivo de la BD NoSQL
            self.nosql_bd.delete_file(file_id)

            return {'message': 'Archivo eliminado con exito', 'nombre': file_name}

        except Exception as e:
            self.error_handle.manejar_error(e)
            return{'message': f'Error: El archivo no se pudo eliminar {str(e)}'}

    def load_file(self, file_name, token_decode):
        try:
            # Verificar si el archivo existe en la base de datos SQL
            if not self.sql_bd.file_exists(file_name):
                return {'message': 'Error: Archivo no existe'}

            # Obtener el ID del archivo desde SQL
            file_id = self.sql_bd.file_data(file_name)

            # Obtener el archivo desde la base de datos NoSQL (Gridfs)
            file_data = self.nosql_bd.get_file(file_id)

            if file_data is None:
                return {'message': 'Error: No se puede recuperar el archivo desde la BD'}

            # Calculando el hash del archivo
            hashing_file = self.hash.hashing(file_data.read()) # Lee el contenido binario del archivo

            # Extraer metadatos del archvio
            metadatos = {
                'nombre': file_name,
                'tamaño': file_data.length,
                'tipo': file_data.content_type,
                'extension': file_name.split('.')[-1],
                'file_id': file_id
            }

            # Registrar en el blockchain la operacion de carga
            self.blockchain.create_block(hashing_file, metadatos, token_decode['clave_privada'])

            # Devolver el archivo y su tipo de contenido
            return file_data.read(), file_data.content_type, file_name

        except Exception as e:
            self.error_handle.manejar_error(e)
            return {'message': f'Error al cargar el archivo: {str(e)}'}
