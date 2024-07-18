import json, random, os

brands = ['Geox', 'Ecco', 'Superfit']
sizes = list(range(20, 40))
categories = ['Sneakers', 'Boots', 'Sandals', 'Demi-season']
prices = [1199, 1299, 1399, 1499, 1599, 1699, 1799, 1899, 1999, 2099, 2199]
images = [im for im in os.listdir('static/img/covers') if im.endswith('.jpg')]
tags = ['featured', 'sale', 'new']
discounts = [0, 0, 0, 0, 0, 0, 0, 0, 5, 10, 15, 20, 30, 40, 50]

products = []
for i in range(100):
    product = {
        'id': i+1,
        'brand': random.choice(brands),
        'category': random.choice(categories),
        'prev-price': random.choice(prices),
        'sizes': random.sample(sizes, random.randint(1, 10)),
        'img': f'../static/img/covers/{random.choice(images)}',
        'tag': random.choice(tags),
        'discount': random.choice(discounts)
    }
    # p=dp/(1-d)
    product['price'] = str(round(product['prev-price']*(1-product['discount']/100)))[:-2]+"99"
    products.append(product)

with open('products.json', 'w') as f:
    json.dump({'products': products}, f)