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

@app.route('/')
def index():
    products = get_products()
    return render_template('index.html', index_images=index_images, products_featured=[p for p in products if p['tag'] == 'featured'], products_sale=[p for p in products if p['tag'] == 'sale'])

@app.route('/newsletter-signup', methods=['POST'])
def newsletter_signup():
    email = request.json.get('email')
    print(email)
    return jsonify({'success': True})

@app.route('/favorite/<product_number>', methods=['POST'])
def favorite(product_number):
    global products
    products = get_products()
    product_i = [i for i, p in enumerate(products) if p['product-number'] == product_number][0]
    products[product_i]['favorite'] = not products[product_i]['favorite']
    print(product_number)
    save_products(products)
    return jsonify({'success': True, 'favorite': products[product_i]['favorite']})

if __name__ == "__main__":
    app.run(debug=True, port=8080)