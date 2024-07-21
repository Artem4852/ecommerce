import flask
from flask import request, jsonify, render_template, session, redirect, url_for
from database import Database
import os, random, json, math, dotenv

dotenv.load_dotenv()

app = flask.Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

index_images = [im for im in os.listdir('static/img/covers') if im.endswith('.jpg')]
random.shuffle(index_images)
columns = 8
rows = 10
index_images = index_images[:columns*rows]
index_images = [index_images[i:i+rows] for i in range(0, len(index_images), rows)]

database = Database()

username = "test1"

def get_products():
    return database.get_products()

def get_user(_filter):
    if not session.get('logged_in', False) and 'id' in _filter:
        return {'cart': [], 'favorites': []}
    return database.get_user(_filter)

@app.route('/')
def index():
    products = get_products()
    user = get_user({'id': session.get('user_id')})
    logged_in = session.get('logged_in', False)
    return render_template('index.html', index_images=index_images, products_featured=[p for p in products if p['tag'] == 'featured' and p['discount'] == 0][:4], products_sale=sorted([p for p in products if p['tag'] == 'sale' and p['discount'] != 0], key=lambda x: x['discount'], reverse=True)[:4], user_data=user, logged_in=logged_in)

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

    user = get_user({'id': session.get('user_id')})

    for n, p in enumerate(products_current):
        products_current[n]['sizes'] = sorted(p['sizes'])

    logged_in = session.get('logged_in', False)

    return render_template('shop.html', products=products_current, user_data=user, brand=brand, category=category, shoe_size=shoe_size, price_range=price_range, sorting=sorting, products_per_page=products_per_page, page=page, max_pages=max_pages, logged_in=logged_in)

@app.route('/product/<product_id>')
def product(product_id):
    products = get_products()
    product = database.get_product({'id': int(product_id)})
    user = get_user({'id': session.get('user_id')})
    logged_in = session.get('logged_in', False)
    return render_template('product.html', product=product, user_data=user, products_featured=[p for p in products if p['tag'] == 'featured' and p['discount'] == 0][:4], logged_in=logged_in)

@app.route('/cart')
def cart():
    logged_in = session.get('logged_in', False)
    if not logged_in:
        return redirect('/login?next=cart')
    user = get_user({'id': session.get('user_id')})
    products = get_products()
    cart_items = []
    subtotal = 0
    for item in user['cart']:
        product = database.get_product({'id': item['product_id']})
        subtotal += int(product['price'])*int(item['quantity'])
        cart_items.append({'id': item['product_id'], 'size': item['size'], 'quantity': item['quantity'], 'info': product})
    return render_template('cart.html', user_data=user, cart_items=cart_items, subtotal=subtotal, products_featured=[p for p in products if p['tag'] == 'featured' and p['discount'] == 0][:4], logged_in=logged_in)

@app.route('/favorites')
def favorites():
    logged_in = session.get('logged_in', False)
    if not logged_in:
        return redirect('/login?next=favorites')
    
    if not request.args.get('page'): page = 1
    else: page = int(request.args.get('page'))

    user = get_user({'id': session.get('user_id')})
    products = get_products()
    favorite_items = []
    for item in user['favorites']:
        product = database.get_product({'id': item})
        favorite_items.append(product)

    favorite_items = favorite_items[(page-1)*12:page*12]
    max_pages = math.ceil(len(user['favorites'])/12)

    return render_template('favorites.html', user_data=user, favorite_items=favorite_items, products_featured=[p for p in products if p['tag'] == 'featured' and p['discount'] == 0][:4], page=page, max_pages=max_pages, logged_in=logged_in)

@app.route('/faq')
def faq():
    logged_in = session.get('logged_in', False)
    faq = database.get_faq()
    return render_template('faq.html', faq_posts=faq, logged_in=logged_in)

@app.route('/faq/<faq_name>')
def faq_post(faq_name):
    logged_in = session.get('logged_in', False)
    if faq_name == 'shoe-size':
        return render_template('faq_shoe_size.html', logged_in=logged_in)
    elif faq_name == 'delivery':
        return render_template('faq_delivery.html', logged_in=logged_in)
    elif faq_name == 'replacements-returns':
        return render_template('faq_replacements_returns.html', logged_in=logged_in)
    
@app.route('/contact')
def contact():
    logged_in = session.get('logged_in', False)
    return render_template('contact.html', logged_in=logged_in)

@app.route('/newsletter-signup', methods=['POST'])
def newsletter_signup():
    email = request.json.get('email')
    database.add_to_newsletter(email)
    return jsonify({'success': True})

@app.route('/termsofuse')
def termsofuse():
    logged_in = session.get('logged_in', False)
    return render_template('legal_tos.html', logged_in=logged_in)

@app.route('/privacypolicy')
def privacypolicy():
    logged_in = session.get('logged_in', False)
    return render_template('legal_privacypolicy.html', logged_in=logged_in)

@app.route('/cookiespolicy')
def cookiespolicy():
    logged_in = session.get('logged_in', False)
    return render_template('legal_cookiespolicy.html', logged_in=logged_in)

@app.route('/shippingpolicy')
def shippingpolicy():
    logged_in = session.get('logged_in', False)
    return render_template('legal_shippingpolicy.html', logged_in=logged_in)

@app.route('/replacementsandreturnspolicy')
def replacementsandreturnspolicy():
    logged_in = session.get('logged_in', False)
    return render_template('legal_replacementsandreturnspolicy.html', logged_in=logged_in)

@app.route('/favorite/<product_number>', methods=['POST'])
def favorite(product_number):
    favorites = database.get_user({'id': session.get('user_id')})['favorites']

    if int(product_number) in favorites: database.update_user({'id': session.get('user_id')}, {'$pull': {'favorites': int(product_number)}})
    else: database.update_user({'id': session.get('user_id')}, {'$push': {'favorites': int(product_number)}})

    return jsonify({'success': True, 'favorite': not int(product_number) in favorites})

@app.route('/add-to-cart/<product_id>', methods=['POST'])
def add_to_cart(product_id):
    size = request.json.get('size')
    quantity = request.json.get('quantity')
    database.update_user({'id': session.get('user_id')}, {'$push': {'cart': {'product_id': int(product_id), 'size': int(size), 'quantity': int(quantity)}}})
    return jsonify({'success': True})

@app.route('/remove-from-cart/<product_id>', methods=['POST'])
def remove_from_cart(product_id):
    size = request.json.get('size')
    quantity = request.json.get('quantity')
    database.update_user({'id': session.get('user_id')}, {'$pull': {'cart': {'product_id': int(product_id), 'size': int(size), 'quantity': int(quantity)}}})
    return jsonify({'success': True})

@app.route('/edit-cart/<product_id>', methods=['POST'])
def edit_cart(product_id):
    size = request.json.get('size')
    quantity = request.json.get('quantity')
    database.update_user({'id': session.get('user_id'), 'cart.product_id': int(product_id)},
    {'$set': {'cart.$.size': int(size), 'cart.$.quantity': int(quantity)}})
    return jsonify({'success': True})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        logged_in = session.get('logged_in', False)
        if logged_in:
            return redirect('/')
        return render_template('login.html', logged_in=logged_in)
    
    email = request.json.get('email')
    password = request.json.get('password')
    user = get_user({'email': email})

    if user and user['password'] == password:
        session['user_id'] = user['id']
        session['logged_in'] = True
        return jsonify({'success': True})

    return jsonify({'success': False, 'error': 'Incorrect email or password'})

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('logged_in', None)
    return redirect('/')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        logged_in = session.get('logged_in', False)
        if logged_in:
            return redirect('/')
        return render_template('signup.html', logged_in=logged_in)
    
    email = request.json.get('email')
    phone_number = request.json.get('phone')
    password = request.json.get('password')

    user = get_user({'email': email})
    if user:
        return jsonify({'success': False, 'error': 'User already exists'})
    
    database.add_user({'email': email, 'phone-number': phone_number, 'password': password, 'cart': [], 'favorites': [], 'shipping-information': {}, 'billing-information': {}, 'user_id': random.randint(100000, 999999)})
    return jsonify({'success': True})
    

if __name__ == "__main__":
    app.run(debug=True, port=8080)