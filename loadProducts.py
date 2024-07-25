import json, random, os
from database import Database

database = Database()

brands = ['Geox', 'Superfit', 'Ecco', 'Pablosky']
categories = ['Sandals', 'Sneakers', 'Boots', 'Demi', 'Slippers', 'Shoes']
sizes = list(range(25, 40))
tags = ['New', 'Sale', 'Bestseller', 'Featured']
discounts = [0, 0, 0, 0, 0, 5, 10, 15, 20, 25, 30]
prices = [int(str(i) + '99') for i in range(10, 30)]
sizes_cm = {
    '25': 16.5,
    '26': 17.2,
    '27': 18,
    '28': 18.7,
    '29': 19.5,
    '30': 20.2,
    '31': 21,
    '32': 21.7,
    '33': 22.5,
    '34': 23.2,
    '35': 24,
    '36': 24.7,
    '37': 25.5,
    '38': 26.2,
    '39': 27,
    '40': 27.7
}
seasons = ['Winter', 'Spring', 'Summer', 'Autumn']
materials = ['Leather', 'Textile', 'Synthetic', 'Rubber', 'Fur', 'Faux fur', 'Faux leather', 'Eco leather', 'Eco textile', 'Eco rubber']
warehouses = ['Kyiv', 'Poltava', 'Ternopil', 'Odesa', 'Ivano-Frankivsk']

posts = [f for f in os.listdir('static/img/posts') if os.path.isdir('static/img/posts/' + f)]
products = database.getProducts()

ids = [product['id'] for product in products]
for n, post in enumerate(posts):
    if database.getProduct({'img': f"img/posts/{post}/0.jpg"}):
        continue
    print(f"Adding {n+1}/{len(posts)}")
    id = random.randint(100000, 999999)
    while id in ids:
        id = random.randint(100000, 999999)
    ids.append(id)
    product = {
        "id": id,
        "brand": random.choice(brands),
        "category": random.choice(categories),
        "price": random.choice(prices),
        "discount": random.choice(discounts),
        "sizes": random.sample(sizes, random.randint(0, 5)),
        "img": f"img/posts/{post}/0.jpg",
        "tag": random.choice(tags) if random.random() < 0.2 else '',
        "images": [f"img/posts/{post}/{img}" for img in os.listdir(f"static/img/posts/{post}") if img.endswith('.jpg')],
        "warehouse": random.choice(warehouses),
        "additionalInformation": {
            "season": random.choice(seasons),
            "outerMaterial": random.choice(materials),
            "innerMaterial": random.choice(materials),
            "insoleMaterial": random.choice(materials),
        }
    }
    product['prev-price'] = str(product['price'] / (1 - product['discount'] / 100))[:2]+'99'
    product['max_quantities'] = {str(size): random.randint(1, 3) for size in product['sizes']}
    product['sizes_cm'] = {str(size): sizes_cm[str(size)] for size in product['sizes']}

    database.addProduct(product)