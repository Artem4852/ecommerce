from database import Database
import os

database = Database()

products = database.getProducts()
ids = [int(product['id']) for product in products]
img_ids = [im for im in os.listdir('static/img/products') if im.isdigit()]
for img_id in img_ids:
    if not int(img_id) in ids:
        os.system(f'rm -r static/img/products/{img_id}')