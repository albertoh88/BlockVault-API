from decouple import config
from error_handler import Errores
from pymongo import MongoClient
from pymongo.errors import PyMongoError
import mysql.connector


class Connection:
    def __init__(self):
        self.error_handle = Errores()

    def connection_sql(self):
        try:
            return mysql.connector.connect(host=config('MYSQL_HOST'),
                                           database=config('MYSQL_BD'),
                                           port=config('MYSQL_PORT'),
                                           user=config('MYSQL_USER'),
                                           password=config('MYSQL_PASSWORD'))
        except mysql.connector.Error as err:
            self.error_handle.manejar_error(err)

    def connection_nosql(self):
        try:
            cliente = MongoClient(host=config('NOSQL_HOST'),
                                  port=int(config('NOSQL_PORT')))
            return cliente

        except PyMongoError as err:
            self.error_handle.manejar_error(err)

