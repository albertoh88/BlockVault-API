import datetime
import mysql.connector
from connection import Connection
from error_handler import Errores

class Sql:
    def __init__(self):
        self.conect = Connection()
        self.error_handle = Errores()

    def save_hash_file(self, hash_block, hash_file, id_file, id_block, file_name):
        try:
            # Establecer conexión con la BD
            conn = self.conect.connection_sql()
            cursor = conn.cursor()

            # Llamamos al procedimiento que se encarga de guardar los datos
            cursor.callproc('registro', [hash_block, hash_file, id_file, id_block, file_name])

            # Confirmamos cambios
            conn.commit()

        except Exception as e:
            self.error_handle.manejar_error(e)
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if 'conn' in locals() and conn:
                conn.close()

    def ultimo_hash(self, previous_hash):
        # Establecer conexión con la BD
        conn = self.conect.connection_sql()
        cursor = conn.cursor()

        # Logica para verificar si el previous_hash existe
        query = 'SELECT hash_exists(%s);' # Aquí invocamos la función
        cursor.execute(query, (previous_hash,))
        result = cursor.fetchone()
        if result[0]:
            return True
        else:
            return False

    def file_exists(self, file_name):
        # Establecer conexión con la BD
        conn = self.conect.connection_sql()
        cursor = conn.cursor()

        # Logica para verificar si el archivo existe
        query = 'SELECT file_exists(%s);'  # Aquí invocamos la función
        cursor.execute(query, (file_name,))
        result = cursor.fetchone()
        if result[0]:
            return True
        else:
            return False

    def file_data(self, file_name):
        try:
            # Establecer conexión con la BD
            conn = self.conect.connection_sql()
            cursor = conn.cursor()

            # Llamamos al procedimiento para extraer el id
            query = 'CALL file_id(%s, @idfile, @message);'
            cursor.execute(query, (file_name))

            # Recuperando las variables de salida
            cursor.execute('SELECT @idfile, @message;')
            result = cursor.fetchone()

            file_id = result[0]
            message = result[1]

            return file_id

        except Exception as e:
            self.error_handle.manejar_error(e)

        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if 'conn' in locals() and conn:
                conn.close()