from database import Database
import os
import shutil

database = Database()
products = database.getProducts()

os.makedirs('static/img/products', exist_ok=True)

for product in products:
    post = product['img'].split("/")[2]
    id = product['id']

    os.makedirs(f'static/img/products/{id}', exist_ok=True)
    for _file in os.listdir(f'static/img/posts/{post}/'):
        print(_file)
        shutil.copy(f'static/img/posts/{post}/{_file}', f'static/img/products/{id}/{_file}')