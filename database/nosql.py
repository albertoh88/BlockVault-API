from pymongo import MongoClient
from error_handler import Errores
from connection import Connection
import gridfs

class Nosql:
    def __init__(self):
        self.conect = Connection()
        self.error_handle = Errores()

    def save_file(self, file, filename):
        try:
            cliente = self.conect.connection_nosql()

            fs = gridfs.GridFS(cliente['mi_base_de_datos_file'])

            if fs.exists({'filename': filename}):
                return {'message': 'El archivo ya existe', 'nombre': filename}

            file_id = fs.put(file, filename=filename)

            return {'message': 'Archivo guardado', 'file_id': file_id}

        except Exception as e:
            self.error_handle.manejar_error(e)

        finally:
            if cliente:
                cliente.close()

    def ultimo_registro(self):
        try:
            cliente = self.conect.connection_nosql()
            db = cliente['mi_base_de_datos']
            collection = db['mi_coleccion']

            # Obtener el último registro insertado
            ultimo_bloque_cursor = collection.find().sort([('$natural', -1)]).limit(1)
            ultimo_bloque = list(ultimo_bloque_cursor)

            # Obteniendo el previous_hash del último bloque
            if ultimo_bloque:
                previous_hash = ultimo_bloque[0]['previous_hash']
                return previous_hash
            else:
                return None

        except Exception as e:
            self.error_handle.manejar_error(e)

    def save_block(self, block):
        try:
            cliente = self.conect.connection_nosql()
            db = cliente['mi_base_de_datos_blockchain']
            collection = db['registros_block']

            # Guardando el registro en la bd
            collection.insert_one({'name': block['index'], 'file_hash': block['data'], 'block': block, 'enable': True})

            document = collection.find()
            return document[0]['_id']

        except Exception as e:
            self.error_handle.manejar_error(e)
        finally:
            if cliente:
                cliente.close()

    def get_last_index(self):
        try:
            cliente = self.conect.connection_nosql()
            db = cliente['mi_base-datos-blockchain']
            collection = db['registros_block']

            last_block = collection.fine_one({}, sort=[('index', -1)]) # Obtener el bloque con el mayor indice
            return last_block['index'] if last_block else 0 # Si no hay bloque, retorna 0

        except Exception as e:
            self.error_handle.manejar_error(e)
            return 0 # Retorna 0 en caso de error para evitar fallos en otras funciones
        finally:
            if cliente:
                cliente.close()

    def get_file(self, file_id):
        try:
            cliente = self.conect.connection_nosql()

            fs = gridfs.GridFS(cliente['mi_base_de_datos_file'])

            if not fs.exists({'_id': file_id }):
                return {'message': 'El archivo no existe'}

            file_obj = fs.get(file_id)
            file_data = file_obj.read() # Contenido en binario

            return file_data

        except Exception as e:
            self.error_handle.manejar_error(e)

        finally:
            if cliente:
                cliente.close()

    def delete_file(self, file_id):
        cliente = None # Previene errores en finally di falla la conexión

        try:
            cliente = self.conect.connection_nosql()
            fs = gridfs.GridFS(cliente['mi_base_de_datos_file'])

            if not fs.exists(file_id):
                return {'message': 'El archivo no existe'}

            fs.delete(file_id)
            return {'message': 'El archivo fue eliminado con exito'}

        except Exception as e:
            self.error_handle.manejar_error(e)
            return {'message': f'Error al eliminar el archivo: {str(e)}'}

        finally:
            if cliente:
                cliente.close()