import datetime
import hashlib
import json
from uuid import uuid4
from urllib.parse import urlparse
import requests
from fastapi import FastAPI
from route import routes
import uvicorn

app = FastAPI()

# Definimos las rutas
app.include_router(routes.router)

@app.get('/')
def read_root():
    return {'message': 'Hola, este es el primer endpoint!!'}

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
