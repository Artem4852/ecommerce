import flask
from flask import request, jsonify, render_template
from database import Database
import os, random, json, math

app = flask.Flask(__name__)

index_images = [im for im in os.listdir('static/img/covers') if im.endswith('.jpg')]
random.shuffle(index_images)
columns = 8
rows = 10
index_images = index_images[:columns*rows]
index_images = [index_images[i:i+rows] for i in range(0, len(index_images), rows)]

database = Database()

username = "test"

def get_products():
    return database.get_products()

def get_user(_filter):
    return database.get_user(_filter)

@app.route('/')
def index():
    products = get_products()
    user = get_user({'username': username})
    return render_template('index.html', index_images=index_images, products_featured=[p for p in products if p['tag'] == 'featured' and p['discount'] == 0][:4], products_sale=sorted([p for p in products if p['tag'] == 'sale' and p['discount'] != 0], key=lambda x: x['discount'], reverse=True)[:4], user_data=user)

@app.route('/shop')
def shop():
    brand = request.args.get('brand')
    category = request.args.get('category')
    shoe_size = request.args.get('shoe-size')
    price_range = request.args.get('price-range')
    price_min = int(price_range.split('-')[0]) if price_range else None
    price_max = int(price_range.split('-')[1]) if price_range else None
    sorting = request.args.get('sorting')

    if not request.args.get('products-per-page'): products_per_page = 12
    else: products_per_page = int(request.args.get('products-per-page'))
    if not request.args.get('page'): page = 1
    else: page = int(request.args.get('page'))

    products = get_products()
    if brand: products = [p for p in products if p['brand'] == brand]
    if category: products = [p for p in products if p['category'] == category]
    if shoe_size: products = [p for p in products if int(shoe_size) in p['sizes']]
    if price_range: products = [p for p in products if price_min<=int(p['price'])<=price_max]

    if sorting == 'price-low-to-high': products = sorted(products, key=lambda x: x['price'])
    elif sorting == 'price-high-to-low': products = sorted(products, key=lambda x: x['price'], reverse=True)

    products_current = products[(page-1)*products_per_page:page*products_per_page]

    max_pages = math.ceil(len(products)/products_per_page)

    user = get_user({'username': username})

    for n, p in enumerate(products_current):
        products_current[n]['sizes'] = sorted(p['sizes'])

    return render_template('shop.html', products=products_current, user_data=user, brand=brand, category=category, shoe_size=shoe_size, price_range=price_range, sorting=sorting, products_per_page=products_per_page, page=page, max_pages=max_pages)

@app.route('/product/<product_id>')
def product(product_id):
    product = database.get_product({'id': int(product_id)})
    user = get_user({'username': username})
    return render_template('product.html', product=product, user_data=user)

@app.route('/newsletter-signup', methods=['POST'])
def newsletter_signup():
    email = request.json.get('email')
    database.add_to_newsletter(email)
    return jsonify({'success': True})

@app.route('/favorite/<product_number>', methods=['POST'])
def favorite(product_number):
    favorites = database.get_user({'username': username})['favorites']
    if int(product_number) in favorites: database.update_user({'username': username}, {'$pull': {'favorites': int(product_number)}})
    else: database.update_user({'username': username}, {'$push': {'favorites': int(product_number)}})

    return jsonify({'success': True, 'favorite': not int(product_number) in favorites})

@app.route('/add-to-cart/<product_id>', methods=['POST'])
def add_to_cart(product_id):
    database.update_user({'username': username}, {'$push': {'cart': product_id}})
    return jsonify({'success': True})

if __name__ == "__main__":
    app.run(debug=True, port=8080)