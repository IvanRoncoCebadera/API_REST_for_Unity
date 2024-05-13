from pymongo import MongoClient
from dotenv import dotenv_values

print("Empiezo a cargar los datos de la base de datos")

ENV = dotenv_values()

# MongoDB
user = ENV["MONGO_USER"]
print(user)
password = ENV["MONGO_PWD"]
print(password)
host = ENV["MONGO_HOST"]
print(host)
port = ENV["MONGO_PORT"]
print(port)
mongo_db = MongoClient(f"mongodb://{user}:{password}@{host}:{port}")
print("Termino de cargar los datos de la base de datos")