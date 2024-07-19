from pymongo.mongo_client import MongoClient
from bson.objectid import ObjectId
import os, dotenv

dotenv.load_dotenv()

class Database:
    def __init__(self):
        uri = os.getenv('MONGO_URI')
        self.client = MongoClient(uri)
        self.users_db = self.client['users']
        self.products_db = self.client['products']
    
    def get_user(self, _filter):
        return self.users_db['user_data'].find_one(_filter)
    
    def update_user(self, _filter, update):
        self.users_db['user_data'].update_one(_filter, update)
    
    def get_users(self):
        return list(self.users_db['user_data'].find())
    
    def get_product(self, _filter):
        return self.products_db['product_data'].find_one(_filter)
    
    def update_product(self, productId, product):
        print(product)
        self.products_db['product_data'].update_one({'id': productId}, {'$set': product})
    
    def get_products(self):
        return list(self.products_db['product_data'].find())

    def new_product(self, product):
        self.products_db['product_data'].insert_one(product)

    def add_to_newsletter(self, email):
        self.users_db['notifications'].update_one({'_id': ObjectId('6699745baeee92227cd44cfa')}, {'$push': {'newsletter': email}})

if __name__ == '__main__':
    database = Database()
    print(database.get_users())