from fastapi import APIRouter, Depends, HTTPException, Header, Request, File, UploadFile
from pydantic import BaseModel
from services import archivos
from error_handler import Errores
from services.services import Services

router = APIRouter()
archivo = archivos.Archivo()
error_handle = Errores()
service = Services()

# Ruta para guardar el archivo
@router.post('/uploadfile/')
async def upload_file(file: UploadFile = File(...), authorization: str = Header(...)):
    try:
        if not isinstance(authorization, str) or not authorization.startswith('Bearer '):
            error_handle.manejar_error(ValueError('El token no fue proporcionado o es inválido'))

        token_parts = authorization.split(' ')
        if len(token_parts) != 2:
            error_handle.manejar_error(ValueError('El formato del token es incorrecto'))

        token = token_parts[1] # Extrae el token después de 'Bearer'

        result = service.verify_and_validate_token(token)

        # Valida si el archivo tiene contenido
        if not file.filename:
            error_handle.manejar_error(ValueError('El archivo no fue proporcionado o esta vacío'))

        filename = file.filename
        await archivo.uploadfile(file, result)

        return {'name': filename, 'token': token}

    except Exception as e:
        error_handle.manejar_error(e)
        return {'message': f'Error al guardar el archivo: {str(e)}'}

class RegisterRequest(BaseModel):
    filename: str # Se valida automáticamente que filename exista y sea una cadena

# Ruta para eliminar el archivo
@router.post('/deletefile/')
def delete_file(request: RegisterRequest, authorization: str = Header(...)):
    try:
        if not isinstance(authorization, str) or not authorization.startswith('Bearer '):
            raise  ValueError('El token no fue proporcionado o es inválido')

        token_parts = authorization.split(' ')
        if len(token_parts) != 2:
            raise ValueError('El formato del token es incorrecto')

        token = token_parts[1] # Extrae el token después de 'Bearer'

        result = service.verify_and_validate_token(token)

        archivo.deletefile(request.filename, result)
        return {'message': 'Archivo eliminado correctamente'}
    except Exception as e:
        error_handle.manejar_error(e)
        return {'message': f'Error al eliminar el archivo: {str(e)}'}

# Ruta para cargar el archivo
@router.post('/loadfile/')
def load_file(request: RegisterRequest, authorization: str = Header(...)):
    try:
        if not isinstance(authorization, str) or not authorization.startswith('Bearer '):
            raise ValueError('El token no fue proporcionado o es inválido')

        token_parts = authorization.split(' ')
        if len(token_parts) != 2:
            raise ValueError('El formato del token es incorrecto')

        token = token_parts[1] # Extrae el token después de 'Bearer'
        result = service.verify_and_validate_token(token)

        file_data, file_name, content_type = archivo.load_file(request.file_name, result)

        if isinstance(file_data, dict): # Si es un error
            return file_data

        if file_data is None:
            return {'message': 'Error: El archivo no existe o no se puedo recuperar'}

        # Devuelve el archivo con el tipo de contenido correcto
        return  Response(file_data, media_type=content_type, headers={'Content-Disposition': f'attachment; filename={file_name}'})

    except Exception as e:
        error_handle.manejar_error(e)
        return {'message': f'Error al cargar el archivo: {str(e)}'}

