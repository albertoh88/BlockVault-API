import unittest
import connection
from decouple import config
from database.sql import Sql
from database.nosql import Nosql


class TestDatabase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass
