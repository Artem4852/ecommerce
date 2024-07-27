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

    def updateOrder(self, orderId, change):
        self.productsDb['orders'].update_one({'orderId': orderId}, change)

    def editOrder(self, orderId, order):
        self.usersDb['orders'].update_one({'orderId': orderId}, {'$set': order})

    def removeOrder(self, orderId):
        self.productsDb['orders'].delete_one({'orderId': orderId})

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

    for n, product in enumerate(products):
        print(f"Editing {n+1}/{len(products)}")
        # images = product['images']
        # images = [i.split('/')[-1] for i in images]
        database.updateProduct(product['id'], {'img': product['img'].split('/')[-1]})

    # warehouses_names = ['Kyiv', 'Poltava', 'Ternopil', 'Odesa', 'Ivano-Frankivsk']

    # for n, product in enumerate(products):
    #     print(f"Editing {n+1}/{len(products)}")
    #     sizes = product['sizes']
    #     warehouses = {}
    #     sizes1 = sizes[:len(sizes)//2]
    #     sizes2 = sizes[len(sizes)//2:]
    #     warehouse1 = random.choice(warehouses_names)
    #     warehouse2 = random.choice(warehouses_names)
    #     for size in sizes1:
    #         warehouses[str(size)] = warehouse1
    #     for size in sizes2:
    #         warehouses[str(size)] = warehouse2
    #     database.updateProduct(product['id'], {'warehouses': warehouses})
    #     database.editProduct(product['id'], ['warehouse'])
    #     img = product['img']
    #     if not os.path.exists(f"static/{img}"):
    #         database.removeProduct(product['id'])
        # database.updateProduct(product['id'], {'img': product['img'].replace('../static/', '')})D