import datetime
import jwt
from decouple import config
from error_handler import Errores

class Services:
    def __init__(self):
        self.error_handle = Errores()

    def verify_and_validate_token(self, token):
        try:
            # Decodificar el token
            decode = jwt.decode(token, config('SECRET_KEY'), algorithms=['HS256'])

            return decode

        except (jwt.ExpiredSignatureError, jwt.InvalidSignatureError, jwt.DecodeError) as e:
            self.error_handle.manejar_error(e)
        except Exception as e:
            self.error_handle.manejar_error(e)
