from pymongo.mongo_client import MongoClient
from bson.objectid import ObjectId
import os, dotenv, random

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
    
    def getStats(self, statName):
        return self.otherDb['statistics'].find_one({'name': statName})

    def updateStats(self, statName, data):
        self.otherDb['statistics'].update_one({'name': statName}, {'$set': data})

if __name__ == "__main__":
    database = Database()
    # for i in range(22, 29):
    #     data = database.getStats('dailyRequests')['data']
    #     data[f'{i}.07.2024'] = random.randint(300, 900)
    #     database.updateStats('dailyRequests', {'data': data})

    # ips = [
    #     "192.168.1.1",
    #     "10.0.0.1",
    #     "172.16.0.1",
    #     "192.168.0.100",
    #     "10.0.1.1",
    #     "172.16.1.1",
    #     "192.168.1.100",
    #     "10.0.0.100",
    #     "172.16.0.100",
    #     "192.168.0.1",
    #     "192.168.1.10",
    #     "10.0.0.10",
    #     "172.16.0.10",
    #     "192.168.0.101",
    #     "10.0.1.10",
    #     "172.16.1.10",
    #     "192.168.1.101",
    #     "10.0.0.101",
    #     "172.16.0.101",
    #     "192.168.0.11",
    #     "192.168.1.11",
    #     "10.0.0.11",
    #     "172.16.0.11",
    #     "192.168.0.102",
    #     "10.0.1.11",
    #     "172.16.1.11",
    #     "192.168.1.102",
    #     "10.0.0.102",
    #     "172.16.0.102",
    #     "192.168.0.12",
    #     "192.168.1.12",
    #     "10.0.0.12",
    #     "172.16.0.12",
    #     "192.168.0.103",
    #     "10.0.1.12",
    #     "172.16.1.12",
    #     "192.168.1.103",
    #     "10.0.0.103",
    #     "172.16.0.103",
    #     "192.168.0.13",
    #     "192.168.1.13",
    #     "10.0.0.13",
    #     "172.16.0.13",
    #     "192.168.0.104",
    #     "10.0.1.13",
    #     "172.16.1.13",
    #     "192.168.1.104",
    #     "10.0.0.104",
    #     "172.16.0.104",
    #     "192.168.0.14",
    #     "192.168.1.14",
    #     "10.0.0.14",
    #     "172.16.0.14",
    #     "192.168.0.105",
    #     "10.0.1.14",
    #     "172.16.1.14",
    #     "192.168.1.105",
    #     "10.0.0.105",
    #     "172.16.0.105",
    #     "192.168.0.15",
    #     "192.168.1.15",
    #     "10.0.0.15",
    #     "172.16.0.15",
    #     "192.168.0.106",
    #     "10.0.1.15",
    #     "172.16.1.15",
    #     "192.168.1.106",
    #     "10.0.0.106",
    #     "172.16.0.106",
    #     "192.168.0.16",
    #     "192.168.1.16",
    #     "10.0.0.16",
    #     "172.16.0.16",
    #     "192.168.0.107",
    #     "10.0.1.16",
    #     "172.16.1.16",
    #     "192.168.1.107",
    #     "10.0.0.107",
    #     "172.16.0.107",
    #     "192.168.0.17",
    #     "192.168.1.17",
    #     "10.0.0.17",
    #     "172.16.0.17",
    #     "192.168.0.108",
    #     "10.0.1.17",
    #     "172.16.1.17",
    #     "192.168.1.108",
    #     "10.0.0.108",
    #     "172.16.0.108",
    #     "192.168.0.18",
    #     "192.168.1.18",
    #     "10.0.0.18",
    #     "172.16.0.18",
    #     "192.168.0.109",
    #     "10.0.1.18",
    #     "172.16.1.18",
    #     "192.168.1.109",
    #     "10.0.0.109",
    #     "172.16.0.109",
    #     "192.168.0.19",
    #     "192.168.1.19",
    #     "10.0.0.19",
    #     "172.16.0.19",
    #     "192.168.0.110",
    #     "10.0.1.19",
    #     "172.16.1.19",
    #     "192.168.1.110",
    #     "10.0.0.110",
    #     "172.16.0.110",
    #     "192.168.0.20",
    #     "192.168.1.20",
    #     "10.0.0.20",
    #     "172.16.0.20",
    #     "192.168.0.111",
    #     "10.0.1.20",
    #     "172.16.1.20",
    #     "192.168.1.111",
    #     "10.0.0.111",
    #     "172.16.0.111",
    # ]
    # for i in range(22, 29):
    #     data = database.getStats('dailyUniqueVisits')['data']
    #     data[f'{i}.07.2024'] = random.sample(ips, random.randint(5, len(ips)))
    #     database.updateStats('dailyUniqueVisits', {'data': data})

    products = database.getProducts()
    for n, product in enumerate(products):
        print(f'{n+1}/{len(products)}')
        database.editProduct(product['id'], ['tag'])
        tag = 'sale' if product['discount'] > 20 else ''
        if tag == '' and random.random() > 0.9: tag = 'featured'
        database.productsDb['productData'].update_one({'id': product['id']}, {'$set': {'tags': [tag]}})