import json, os
from bson.objectid import ObjectId
from database import Database

database = Database()
products = database.getProducts()

for product in products:
    print(product['img'].split('/')[-1].split('.')[0])