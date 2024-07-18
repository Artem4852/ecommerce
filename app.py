import flask
from flask import request, jsonify, render_template
import os, random, json

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
    products = get_products()
    users = get_users()
    return render_template('shop.html', products=products, user_data=users[0])

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