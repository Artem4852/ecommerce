from pymongo.mongo_client import MongoClient
from bson.objectid import ObjectId
import os, dotenv, random, json

from string import ascii_letters, digits
characters = ascii_letters + digits

dotenv.load_dotenv()

class Database:
    def __init__(self):
        uri = os.getenv('MONGO_URI')
        self.client = MongoClient(uri)
        self.usersDb = self.client['users']
        self.productsDb = self.client['products']
        self.otherDb = self.client['other']

    def addUser(self, user):
        self.usersDb['users'].insert_one(user)
    
    def getUser(self, Filter):
        return self.usersDb['users'].find_one(Filter)
    
    def updateUser(self, Filter, update):
        self.usersDb['users'].update_one(Filter, update)
    
    def getUsers(self):
        return list(self.usersDb['users'].find())
    
    def getProduct(self, Filter):
        return self.productsDb['productData'].find_one(Filter)

    def editProduct(self, productId, fields):
        self.productsDb['productData'].update_one({'id': productId}, {'$unset': {field: 1 for field in fields}})

    def addProduct(self, data):
        self.productsDb['productData'].insert_one(data)

    def removeProduct(self, productId):
        self.productsDb['productData'].delete_one({'id': productId})

    def updateProduct(self, productId, product):
        self.productsDb['productData'].update_one({'id': productId}, {'$set': product})

    def addOrder(self, order):
        self.productsDb['orders'].insert_one(order)

    def updateOrder(self, orderId, change):
        self.productsDb['orders'].update_one({'orderId': orderId}, change)

    def editOrder(self, orderId, order):
        self.usersDb['orders'].update_one({'orderId': orderId}, {'$set': order})

    def removeOrder(self, orderId):
        self.productsDb['orders'].delete_one({'orderId': orderId})

    def getOrders(self, Filter=None):
        if not Filter:
            return list(self.productsDb['orders'].find())
        return list(self.productsDb['orders'].find(Filter))
    
    def getOrder(self, Filter):
        return self.productsDb['orders'].find_one(Filter)

    def removeFields(self, productId, fields):
        self.productsDb['productData'].update_one({'id': productId}, {'$unset': {field: 1 for field in fields}})
    
    def getProducts(self):
        return list(self.productsDb['productData'].find())

    def newProduct(self, product):
        self.productsDb['productData'].insert_one(product)

    def addToNewsletter(self, email):
        token = ''.join(random.choices(characters, k=32))
        user = self.usersDb['notifications'].find_one({'email': email})
        if user:
            return user['token']
        self.usersDb['notifications'].insert_one({'email': email, 'token': token})
        return token
        # self.usersDb['notifications'].update_one({'Id': ObjectId('6699745baeee92227cd44cfa')}, {'$push': {'newsletter': email}})

    def removeFromNewsletter(self, token):
        user = self.usersDb['notifications'].find_one({'token': token})
        if user:
            self.usersDb['notifications'].delete_one({'token': token})
            return True
        return False
    
    def updateFaq(self, faq):
        self.otherDb['faq'].update_one({'name': faq['name']}, {'$set': faq}, upsert=True)

    def getFaq(self):
        return list(self.otherDb['faq'].find())
    
    def getLegalPage(self, page):
        return self.otherDb['legal'].find_one({'name': page})
    
    def updateLegalPage(self, page):
        self.otherDb['legal'].update_one({'name': page['name']}, {'$set': page}, upsert=True)
    
    def getStats(self, statName):
        return self.otherDb['statistics'].find_one({'name': statName})

    def updateStats(self, statName, data):
        self.otherDb['statistics'].update_one({'name': statName}, {'$set': data})

    def updateTranslations(self, translations):
        self.otherDb['translations'].update_one({'name': 'translations'}, {'$set': {'name': 'translations', 'data':translations}}, upsert=True)

    def getTranslations(self, part):
        return self.otherDb['translations'].find_one({'name': 'translations'})['data'][part]

if __name__ == "__main__":
    database = Database()

    with open("json/translations.json", "r") as f:
        translations = json.load(f)
    database.updateTranslations(translations)
    print(database.getTranslations('db')['demi'])
