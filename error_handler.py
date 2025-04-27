import json
import logging
import mysql.connector
from fastapi import HTTPException
from pymongo.errors import PyMongoError
from cryptography.exceptions import InvalidKey
import jwt
from jwt.exceptions import DecodeError, ExpiredSignatureError, InvalidTokenError

class Errores:
    def __init__(self):
        logging.basicConfig(level=logging.ERROR, filename='../errores.log')

    def manejar_error(self, error, levantar=True):
        # Se registra el error con detalles completos
        logging.error(f'Error: {str(error)}')

        # Manejo de los errores comunes
        msg = str(error)
        if 'Could not deserializa key data' in msg:
            detalle = 'La clave proporcionada no es válida o no se pudo deserializar'
            if levantar:
                raise HTTPException(status_code=400, detail=detalle)
            return {'status': 400, 'detail': detalle}
        if isinstance(error, ValueError):
            detalle = f'Error de valor: {str(error)}'
            if levantar:
                raise HTTPException(status_code=400, detail=detalle)
            return {'status': 400, 'detail': detalle}
        elif isinstance(error, InvalidKey):
            detalle = 'La clave proporcionada no es válida para firmar los datos'
            if levantar:
                raise HTTPException(status_code=400, detail=detalle)
            return {'status': 400, 'detail': detalle}


        # Errores de archivo
        elif isinstance(error, FileNotFoundError):
            detalle = f'Archivo no encontrado: {str(error)}'
            if levantar:
                raise HTTPException(status_code=404, detail=detalle)
            return {'status': 404, 'detail': detalle}
        elif isinstance(error, PermissionError):
            detalle = f'Acceso denegado: {str(error)}'
            if levantar:
                raise HTTPException(status_code=403, detail=detalle)
            return {'status': 403, 'detail': detalle}


        # Errores relacionados con JWT
        elif isinstance(error, jwt.ExpiredSignatureError):
            detalle = 'El token ha expirado'
            if levantar:
                raise HTTPException(status_code=401, detail=detalle)
            return {'status': 401, 'detail': detalle}
        elif isinstance(error, jwt.InvalidSignatureError):
            detalle = 'El token no es válido'
            if levantar:
                raise HTTPException(status_code=401, detail=detalle)
            return {'status': 401, 'detail': detalle}
        elif isinstance(error, jwt.DecodeError):
            detalle = 'El token está mal formado'
            if levantar:
                raise HTTPException(status_code=401, detail=detalle)
            return {'status': 401, 'detail': detalle}


        # Errores relacionados con la base de datos
        elif isinstance(error, mysql.connector.Error):
            # Aquí manejamos errores especificos de MySQL
            detalle = f'Error en la base de datos SQL: {str(error)}'
            if levantar:
                raise HTTPException(status_code=500, detail=detalle)
            return {'status': 500, 'detail': detalle}
        elif isinstance(error, PyMongoError):
            # Aqui manejamos errores de bases de datos NoSQL como MongoDB
            detalle = f'Error en la base de datos NoSQL: {str(error)}'
            if levantar:
                raise HTTPException(status_code=500, detail=detalle)
            return {'status': 500, 'detail': detalle}

        # Errores generales
        else:
            # Para otros tipos de errores generales
            detalle = f'Error interno del servidor: {str(error)}'
            if levantar:
                raise HTTPException(status_code=500, detail=detalle)
            return {'status': 500, 'detail': detalle}