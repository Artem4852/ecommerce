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
        self.other_db = self.client['other']

    def add_user(self, user):
        self.users_db['user_data'].insert_one(user)
    
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

    def remove_fields(self, productId, fields):
        self.products_db['product_data'].update_one({'id': productId}, {'$unset': {field: 1 for field in fields}})
    
    def get_products(self):
        return list(self.products_db['product_data'].find())

    def new_product(self, product):
        self.products_db['product_data'].insert_one(product)

    def add_to_newsletter(self, email):
        self.users_db['notifications'].update_one({'_id': ObjectId('6699745baeee92227cd44cfa')}, {'$push': {'newsletter': email}})

    def get_faq(self):
        return list(self.other_db['faq'].find())
    
    def get_delivery_countries(self):
        return ['Ukraine', 'Poland', 'Germany']
    
    def get_delivery_cities(self):
        return {
            'Ukraine': ['Kyiv', 'Khariv', 'Lviv'],
            'Poland': ['Warsaw', 'Krakow', 'Gdansk'],
            'Germany': ['Berlin', 'Munich', 'Hamburg']
        }
    
    def get_post_office_branches(self):
        return {
            'Kyiv': ['1', '2', '3'],
            'Khariv': ['4', '5', '6'],
            'Lviv': ['7', '8', '9'],
            'Warsaw': ['10', '11', '12'],
            'Krakow': ['13', '14', '15'],
            'Gdansk': ['16', '17', '18'],
            'Berlin': ['19', '20', '21'],
            'Munich': ['22', '23', '24'],
            'Hamburg': ['25', '26', '27']
        }

if __name__ == '__main__':
    database = Database()
    print(database.get_users())