import flask
from flask import request, jsonify, render_template
import os, random, json, math

app = flask.Flask(__name__)

index_images = [im for im in os.listdir('static/img/covers') if im.endswith('.jpg')]
random.shuffle(index_images)
columns = 8
rows = 10
index_images = index_images[:columns*rows]
index_images = [index_images[i:i+rows] for i in range(0, len(index_images), rows)]

def get_products():
    with open('products.json') as f:
        products = json.load(f)['products']
        return products
    
def save_products(products):
    with open('products.json', 'w') as f:
        json.dump({'products': products}, f)

def get_users():
    with open('users.json') as f:
        users = json.load(f)['users']
        return users
    
def save_users(users):
    with open('users.json', 'w') as f:
        json.dump({'users': users}, f)

@app.route('/')
def index():
    products = get_products()
    users = get_users()
    return render_template('index.html', index_images=index_images, products_featured=[p for p in products if p['tag'] == 'featured'], products_sale=[p for p in products if p['tag'] == 'sale'], user_data=users[0])

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

    users = get_users()
    return render_template('shop.html', products=products_current, user_data=users[0], brand=brand, category=category, shoe_size=shoe_size, price_range=price_range, sorting=sorting, products_per_page=products_per_page, page=page, max_pages=math.ceil(len(products)/products_per_page))

@app.route('/newsletter-signup', methods=['POST'])
def newsletter_signup():
    email = request.json.get('email')
    print(email)
    return jsonify({'success': True})

@app.route('/favorite/<product_number>', methods=['POST'])
def favorite(product_number):
    global users
    users = get_users()
    if product_number in users[0]["favorites"]: users[0]["favorites"].remove(product_number)
    else: users[0]["favorites"].append(product_number)
    save_users(users)
    return jsonify({'success': True, 'favorite': product_number in users[0]["favorites"]})

@app.route('/add-to-cart/<product_number>', methods=['POST'])
def add_to_cart(product_number):
    global users
    users = get_users()
    users[0]['cart'].append(product_number)
    save_users(users)
    return jsonify({'success': True})

if __name__ == "__main__":
    app.run(debug=True, port=8080)