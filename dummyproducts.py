import json, random, os
from database import Database

database = Database()

# brands = ['Geox', 'Ecco', 'Superfit']
# sizes = list(range(20, 40))
# categories = ['Sneakers', 'Boots', 'Sandals', 'DemiSeason']
# prices = [1199, 1299, 1399, 1499, 1599, 1699, 1799, 1899, 1999, 2099, 2199]
# images = [im for im in os.listdir('static/img/covers') if im.endswith('.jpg')]
# tags = ['featured', 'sale', 'new']
# discounts = [0, 0, 0, 0, 0, 0, 0, 0, 5, 10, 15, 20, 30, 40, 50]
seasons = ['spring', 'summer', 'autumn', 'winter']
materials = ['leather', 'textile', 'synthetic', 'rubber', 'suede leather', 'nubuck leather', 'mesh', 'goreTex']

products = []
for i in range(100):
    product = database.getProduct({'id': i+1})
    images = [f'../static/img/posts/{product["img"].split("/")[-1].split(".")[0]}/{im}' for im in sorted(os.listdir(f'static/img/posts/{product["img"].split("/")[-1].split(".")[0]}')) if im.endswith('.jpg')]
    product = {
        'id': i+1,
        # 'brand': random.choice(brands),
        # 'category': random.choice(categories),
        # 'prevPrice': random.choice(prices),
        # 'sizes': random.sample(sizes, random.randint(1, 10)),
        # 'img': f'../static/img/covers/{random.choice(images)}',
        # 'tag': random.choice(tags),
        # 'discount': random.choice(discounts)
        # 'images': images,
        # 'maxQuantities': {str(size): random.randint(1, 5) for size in product['sizes']},
        # 'sizesCm': {str(size): random.randint(10, 30) for size in product['sizes']}
        'additionalInformation': {
            'season': random.choice(seasons),
            'outerMaterial': random.choice(materials),
            'innerMaterial': random.choice(materials),
            'insoleMaterial': random.choice(materials)
        }
    }
    # p=dp/(1D)
    # product['price'] = str(round(product['prevPrice']*(1Product['discount']/100)))[:-2]+"99"
    products.append(product)

for product in products:
    print(product)
    Id = product['id']
    del product['id']
    database.updateProduct(Id, product)
    database.removeFields(Id, ['season', 'innerMaterial', 'outerMaterial', 'insoleMaterial'])