import os
from pymongo import MongoClient
from dotenv import dotenv_values

class MongoDBConfig:
    _mongo_db = None

    @classmethod
    def test_connection(cls, uri):
        try:
            client = MongoClient(uri, serverSelectionTimeoutMS=1000)
            client.admin.command('ismaster')
            return True
        except Exception as e:
            print(e)
            client.close()
            if 'Authentication failed' in str(e):
                print(e)
                return True
            else:
                return False

    @classmethod
    def get_mongo_db(cls):
        env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
        ENV = dotenv_values(env_path)
        print("Valores ENV: ")
        print(ENV)
        user = ENV["MONGO_USER"]
        password = ENV["MONGO_PWD"]
        host = ENV["MONGO_HOST"]
        port = ENV["MONGO_PORT"]
        uri = f"mongodb://{user}:{password}@{host}:{port}"
        if cls.test_connection(uri):
            cls._mongo_db = MongoClient(uri)
        else:
            cls._mongo_db = cls.get_mongo_db_for_tests()

        return cls._mongo_db

    @classmethod
    def get_mongo_db_for_tests(cls):
        env_path = os.path.join(os.path.dirname(__file__), '..', '.env_test')
        ENV = dotenv_values(env_path)
        print("Valores ENV de los tests: ")
        print(ENV)
        user = ENV["MONGO_USER"]
        password = ENV["MONGO_PWD"]
        host = ENV["MONGO_HOST"]
        port = ENV["MONGO_PORT"]

        uri = f"mongodb://{user}:{password}@{host}:{port}"
        if cls.test_connection(uri):
            cls._mongo_db = MongoClient(uri)
        else:
            cls._mongo_db = None

        return cls._mongo_db