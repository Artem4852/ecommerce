import json, os
from bson.objectid import ObjectId
from database import Database

database = Database()
products = database.get_products()

for product in products:
    print(product['img'].split('/')[-1].split('.')[0])