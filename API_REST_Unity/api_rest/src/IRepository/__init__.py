from pymongo import MongoClient
from dotenv import dotenv_values

ENV = dotenv_values()

# MongoDB
user = ENV["MONGO_USER"]
password = ENV["MONGO_PWD"]
host = ENV["MONGO_HOST"]
port = ENV["MONGO_PORT"]
mongo_db = MongoClient(f"mongodb://{user}:{password}@{host}:{port}")