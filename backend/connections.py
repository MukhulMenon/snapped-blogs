from pymongo import MongoClient
from os import environ

MONGO_HOST = environ.get('MONGO_HOST','localhost')

client = MongoClient(MONGO_HOST)

db = client['snapped_blogs']

collection = db['blogs']
