import hashlib
from error_handler import Errores

class Hashing:
    def __init__(self):
        self.error_handle = Errores()

    def hashing(self, file):
        try:
            # Verifica que el objeto tenga el método 'read'
            if not hasattr(file, 'read'):
                self.error_handle.manejar_error(ValueError('El objeto no tiene un método .read(). '
                                                           'Se esperaba un archivo en modo binario'),
                                                levantar=False)
            file.seek(0)
            hash_file = hashlib.sha256() # Crea el objeto de hash SHA-256

            # Lee el archivo en bloques para evitar problemas de memoria
            for chunk in iter(lambda: file.read(4096), b''):
                hash_file.update(chunk) # Actualiza el hash con el contenido del bloque

            return hash_file.hexdigest() # Devuelve el hash en formato hexadecimal
        except Exception as e:
            self.error_handle.manejar_error(e, levantar=False)
            return None
