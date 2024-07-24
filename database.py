from pymongo.mongo_client import MongoClient
from bson.objectid import ObjectId
import os, dotenv, random

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

    def editOrder(self, orderId, order):
        self.usersDb['orders'].update_one({'Id': ObjectId(orderId)}, {'$set': order})

    def getOrders(self, Filter):
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
        self.usersDb['notifications'].update_one({'Id': ObjectId('6699745baeee92227cd44cfa')}, {'$push': {'newsletter': email}})

    def getFaq(self):
        return list(self.otherDb['faq'].find())

if __name__ == "__main__":
    database = Database()
    products = database.getProducts()
    for product in products:
        database.updateProduct(product['id'], {'prevPrice': product['prev-price'], 'maxQuantities': product['max_quantities'], 'sizesCm': product['sizes_cm']})
        database.editProduct(product['id'], ['prev-price', 'max_quantities', 'sizes_cm'])
    #     img = product['img']
    #     if not os.path.exists(f"static/{img}"):
    #         database.removeProduct(product['id'])
        # database.updateProduct(product['id'], {'img': product['img'].replace('../static/', '')})