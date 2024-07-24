from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_mail import Mail, Message
from database import Database
import os, random, json, math, dotenv
from bs4 import BeautifulSoup
from datetime import datetime
from string import ascii_letters, digits
from novapost import NovaAPI
from telegramAPI import sendMessage

characters = ascii_letters + digits

dotenv.load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
database = Database()

nova = NovaAPI()

# Setup mail
app.config['MAIL_SERVER'] = 'sandbox.smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = '49eeff352c2a4d'
app.config['MAIL_PASSWORD'] = 'edb53d7d51b475'
app.config['MAIL_DEFAULT_SENDER'] = 'noreply@kidsfashionstore.ua'
mail = Mail(app)

# Helper functions
def send_email(subject, recipient, body=None, html=None, data=None):
    with app.app_context():
        if html: 
            html_content = render_template('mail/'+html+'.html', data=data)
            if not body:
                soup = BeautifulSoup(html_content, 'html.parser')
                body = soup.get_text()
        else:
            html_content = None
        msg = Message(subject, recipients=[recipient], body=body, html=html_content)
        mail.send(msg)

def get_products():
    return database.get_products()

def get_user(_filter):
    if not session.get('logged_in', False) and 'user_id' in _filter:
        return {'cart': [], 'favorites': []}
    return database.get_user(_filter)

# Index route
@app.route('/')
def index():
    index_images = [im for im in os.listdir('static/img/covers') if im.endswith('.jpg')]
    random.shuffle(index_images)
    index_images = index_images[:8*10]
    index_images = [index_images[i:i+10] for i in range(0, len(index_images), 10)]
    
    products = get_products()
    user = get_user({'user_id': session.get('user_id')})
    logged_in = session.get('logged_in', False)
    return render_template('index.html', index_images=index_images, products_featured=[p for p in products if p['tag'] == 'featured' and p['discount'] == 0][:4], products_sale=sorted([p for p in products if p['tag'] == 'sale' and p['discount'] != 0], key=lambda x: x['discount'], reverse=True)[:4], user_data=user, logged_in=logged_in)

# Shop routes
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

    user = get_user({'user_id': session.get('user_id')})

    for n, p in enumerate(products_current):
        products_current[n]['sizes'] = sorted(p['sizes'])

    logged_in = session.get('logged_in', False)

    return render_template('shop.html', products=products_current, user_data=user, brand=brand, category=category, shoe_size=shoe_size, price_range=price_range, sorting=sorting, products_per_page=products_per_page, page=page, max_pages=max_pages, logged_in=logged_in)

@app.route('/product/<product_id>')
def product(product_id):
    products = get_products()
    product = database.get_product({'id': int(product_id)})
    user = get_user({'user_id': session.get('user_id')})
    logged_in = session.get('logged_in', False)
    return render_template('product.html', product=product, user_data=user, products_featured=[p for p in products if p['tag'] == 'featured' and p['discount'] == 0][:4], logged_in=logged_in)

# Static pages
@app.route('/faq')
def faq():
    logged_in = session.get('logged_in', False)
    faq = database.get_faq()
    return render_template('faq.html', faq_posts=faq, logged_in=logged_in)

@app.route('/faq/<faq_name>')
def faq_post(faq_name):
    logged_in = session.get('logged_in', False)
    if faq_name == 'shoe-size':
        return render_template('faq/shoe_size.html', logged_in=logged_in)
    elif faq_name == 'delivery':
        return render_template('faq/delivery.html', logged_in=logged_in)
    elif faq_name == 'replacements-returns':
        return render_template('faq/replacements_returns.html', logged_in=logged_in)
    
@app.route('/contact')
def contact():
    logged_in = session.get('logged_in', False)
    return render_template('contact.html', logged_in=logged_in)

# Legal routes
@app.route('/termsofuse')
def termsofuse():
    logged_in = session.get('logged_in', False)
    return render_template('legal/terms_of_use.html', logged_in=logged_in)

@app.route('/privacypolicy')
def privacypolicy():
    logged_in = session.get('logged_in', False)
    return render_template('legal/privacy.html', logged_in=logged_in)

@app.route('/cookiespolicy')
def cookiespolicy():
    logged_in = session.get('logged_in', False)
    return render_template('legal/cookies.html', logged_in=logged_in)

@app.route('/shippingpolicy')
def shippingpolicy():
    logged_in = session.get('logged_in', False)
    return render_template('legal/shipping.html', logged_in=logged_in)

@app.route('/replacementsandreturnspolicy')
def replacementsandreturnspolicy():
    logged_in = session.get('logged_in', False)
    return render_template('legal/replacements_and_returns.html', logged_in=logged_in)

# Cart + favorites routes
@app.route('/favorites')
def favorites():
    logged_in = session.get('logged_in', False)
    if not logged_in:
        return redirect('/login?next=favorites')
    
    if not request.args.get('page'): page = 1
    else: page = int(request.args.get('page'))

    user = get_user({'user_id': session.get('user_id')})
    products = get_products()
    favorite_items = []
    for item in user['favorites']:
        product = database.get_product({'id': item})
        favorite_items.append(product)

    favorite_items = favorite_items[(page-1)*12:page*12]
    max_pages = math.ceil(len(user['favorites'])/12)

    return render_template('favorites.html', user_data=user, favorite_items=favorite_items, products_featured=[p for p in products if p['tag'] == 'featured' and p['discount'] == 0][:4], page=page, max_pages=max_pages, logged_in=logged_in)

@app.route('/favorite/<product_number>', methods=['POST'])
def favorite(product_number):
    favorites = database.get_user({'user_id': session.get('user_id')})['favorites']

    if int(product_number) in favorites: database.update_user({'user_id': session.get('user_id')}, {'$pull': {'favorites': int(product_number)}})
    else: database.update_user({'user_id': session.get('user_id')}, {'$push': {'favorites': int(product_number)}})

    return jsonify({'success': True, 'favorite': not int(product_number) in favorites})

@app.route('/cart')
def cart():
    logged_in = session.get('logged_in', False)
    if not logged_in:
        return redirect('/login?next=cart')
    user = get_user({'user_id': session.get('user_id')})
    products = get_products()
    cart_items = []
    subtotal = 0
    for item in user['cart']:
        product = database.get_product({'id': item['product_id']})
        subtotal += int(product['price'])*int(item['quantity'])
        cart_items.append({'id': item['product_id'], 'size': item['size'], 'quantity': item['quantity'], 'info': product})
    return render_template('cart.html', user_data=user, cart_items=cart_items, subtotal=subtotal, products_featured=[p for p in products if p['tag'] == 'featured' and p['discount'] == 0][:4], logged_in=logged_in)

@app.route('/add-to-cart/<product_id>', methods=['POST'])
def add_to_cart(product_id):
    size = request.json.get('size')
    quantity = request.json.get('quantity')
    database.update_user({'user_id': session.get('user_id')}, {'$push': {'cart': {'product_id': int(product_id), 'size': int(size), 'quantity': int(quantity)}}})
    return jsonify({'success': True})

@app.route('/remove-from-cart/<product_id>', methods=['POST'])
def remove_from_cart(product_id):
    size = request.json.get('size')
    quantity = request.json.get('quantity')
    database.update_user({'user_id': session.get('user_id')}, {'$pull': {'cart': {'product_id': int(product_id), 'size': int(size), 'quantity': int(quantity)}}})
    return jsonify({'success': True})

@app.route('/edit-cart/<product_id>', methods=['POST'])
def edit_cart(product_id):
    size = request.json.get('size')
    quantity = request.json.get('quantity')
    database.update_user({'user_id': session.get('user_id'), 'cart.product_id': int(product_id)},
    {'$set': {'cart.$.size': int(size), 'cart.$.quantity': int(quantity)}})
    return jsonify({'success': True})

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'GET':
        logged_in = session.get('logged_in', False)
        if not logged_in:
            return redirect('/login?next=checkout')
        user = get_user({'user_id': session.get('user_id')})
        if not user['cart']:
            return redirect('/cart')
        products = get_products()
        cart_items = []
        subtotal = 0
        for item in user['cart']:
            product = database.get_product({'id': item['product_id']})
            subtotal += int(product['price'])*int(item['quantity'])
            cart_items.append({'id': item['product_id'], 'size': item['size'], 'quantity': item['quantity'], 'info': product})

        country_codes = nova.loadCountryCodes()
        codes_country = {v: k for k, v in country_codes.items()}
        delivery_countries = nova.loadCountries()
        delivery_cities = nova.loadCities()

        shippingData = user['shipping-data']
        paymentData = user['payment-data']
        contactData = user['contact-data']

        featured_products = [p for p in products if p['tag'] == 'featured' and p['discount'] == 0]

        return render_template('checkout.html', user_data=user, cart_items=cart_items, subtotal=subtotal, products_featured=[p for p in products if p['tag'] == 'featured' and p['discount'] == 0][:4], logged_in=logged_in, delivery_countries=delivery_countries, delivery_cities=delivery_cities, featured_products=featured_products, country_codes=country_codes, codes_country=codes_country, shipping_data=shippingData, payment_data=paymentData, contact_data=contactData)
    elif request.method == 'POST':
        data = request.json

        data["order_id"] = ''.join([random.choice(characters) for _ in range(8)])
        data["cart"] = get_user({'user_id': session.get('user_id')})['cart']
        data["user_id"] = session.get('user_id')
        data["status"] = "pending"

        database.add_order(data)
        database.update_user({'user_id': session.get('user_id')}, {'$set': {'cart': []}})

        if data['saveShippingData']: 
            shippingData = {
                'firstName': data['firstName'],
                'lastName': data['lastName'],
                'middleName': data['middleName'],
                'country': data['country'],
                'city': data['city'],
                'deliveryMethod': data['deliveryMethod'],
            }
            if data['deliveryMethod'] == 'pick-up-from-post-office':
                shippingData['postOfficeBranch'] = data['postOfficeBranch']
            else:
                shippingData['address'] = data['address']
                shippingData['address2'] = data['address2']
                shippingData['postalCode'] = data['postalCode']
            database.update_user({'user_id': session.get('user_id')}, {'$set': {'shipping-data': shippingData}})
        if data['savePaymentData']: 
            paymentData = {
                'paymentMethod': data['paymentMethod']
            }
            database.update_user({'user_id': session.get('user_id')}, {'$set': {'payment-data': paymentData}})
        if data['saveContactData']: 
            contactData = {
                'contactMessenger': data['contactMessenger']
            }
            if data['contactMessenger'] == 'instagram':
                contactData['username'] = data['username']
            else:
                contactData['phoneNumber'] = data['phoneNumber']
            database.update_user({'user_id': session.get('user_id')}, {'$set': {'contact-data': contactData}})

        if data['contactMessenger'] == 'telegram':
            messenger = f"<a href='https://t.me/{data['phoneNumber'].replace('(', '').replace(')', '').replace(' ', '')}'>Telegram</a>"
        elif data['contactMessenger'] == 'viber':
            messenger = f"<a href='viber://chat?number={data['phoneNumber'].replace('(', '').replace(')', '').replace(' ', '')}'>Viber</a>"
        elif data['contactMessenger'] == 'instagram':
            messenger = f"<a href='https://instagram.com/{data['username']}'>Instagram</a>"

        sendMessage(f"<b>New order: {data['order_id']}</b>. Check it <a href='https://kidsfashionstore.com.ua/orders/{data['order_id']}'>here</a>. Customer: {data['firstName']} {data['lastName']}, contact in " + messenger)

        return jsonify({'success': True})

@app.route('/get-branches', methods=['POST'])
def get_branches():
    country_code = request.json.get('country_code')
    city = request.json.get('city')
    try:
        branches = nova.getBranches(country_code, city)
        branches = sorted(branches, key=lambda x: int(x['number'].split("/")[-1]))
    except:
        return jsonify({'success': False, 'error': 'Error fetching branches'})
    return jsonify({'success': True, 'branches': branches})

@app.route('/order-confirmation')
def order_confirmation():
    logged_in = session.get('logged_in', False)
    if not logged_in:
        return redirect('/login?next=order-confirmation')
    user = get_user({'user_id': session.get('user_id')})
    products = get_products()
    products_featured = [p for p in products if p['tag'] == 'featured' and p['discount'] == 0]
    return render_template('order_confirmation.html', user_data=user, logged_in=logged_in, products_featured=products_featured[:4])

@app.route('/orders')
def orders():
    logged_in = session.get('logged_in', False)
    if not logged_in:
        return redirect('/login?next=orders')
    user = get_user({'user_id': session.get('user_id')})
    orders = database.get_orders({'user_id': session.get('user_id')})
    for order in orders:
        cart_items = []
        for item in order['cart']:
            product = database.get_product({'id': item['product_id']})
            cart_items.append({'id': item['product_id'], 'size': item['size'], 'quantity': item['quantity'], 'info': product})
        order['cart'] = cart_items
    products = get_products()
    products_featured = [p for p in products if p['tag'] == 'featured' and p['discount'] == 0]
    return render_template('orders.html', user_data=user, orders=orders, logged_in=logged_in, products_featured=products_featured[:4])

@app.route('/orders/<order_id>/<product_id>')
def order(order_id, product_id):
    logged_in = session.get('logged_in', False)
    if not logged_in:
        return redirect('/login?next=orders')
    user = get_user({'user_id': session.get('user_id')})
    order = database.get_order({'order_id': order_id})
    order['product'] = [o for o in order['cart'] if int(o['product_id']) == int(product_id)][0]
    order['product']['info'] = database.get_product({'id': int(product_id)})
    products = get_products()
    products_featured = [p for p in products if p['tag'] == 'featured' and p['discount'] == 0]

    country_codes = nova.loadCountryCodes()
    codes_country = {v: k for k, v in country_codes.items()}

    return render_template('order.html', user_data=user, order=order, logged_in=logged_in, products_featured=products_featured[:4], codes_country=codes_country)

# Settings
@app.route('/settings')
def settings():
    logged_in = session.get('logged_in', False)
    if not logged_in:
        return redirect('/login?next=settings')
    user = get_user({'user_id': session.get('user_id')})

    delivery_countries = nova.loadCountries()
    delivery_cities = nova.loadCities()
    codes_country = {v: k for k, v in nova.loadCountryCodes().items()}

    return render_template('settings.html', userData=user, logged_in=logged_in, codes_country=codes_country, delivery_countries=delivery_countries, delivery_cities=delivery_cities)

@app.route('/update-settings', methods=['POST'])
def update_settings():
    data = request.json
    for key, value in data.items():
        if key == "messengerUsername": key="username"
        elif key == "messenger": key="contactMessenger"

        if key in ['firstName', 'lastName', 'middleName', 'country', 'city', 'address', 'address2', 'postalCode', 'deliveryMethod', 'postOfficeBranch']: key = 'shipping-data.'+key
        elif key in ['paymentMethod']: key = 'payment-data.'+key
        elif key in ['contactMessenger', 'username', 'phoneNumber']: key = 'contact-data.'+key
        elif key in ['newDeals', 'seasonalSales', 'discounts', 'promoCode']: key = 'notifications.'+key
        database.update_user({'user_id': session.get('user_id')}, {'$set': {key: value}})  
    return jsonify({'success': True})

# Newsletter route
@app.route('/newsletter-signup', methods=['POST'])
def newsletter_signup():
    email = request.json.get('email')
    database.add_to_newsletter(email)
    return jsonify({'success': True})

# Auth routes
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
        print(user)
        session['user_id'] = user['user_id']
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
    
    database.add_user({
        'email': email, 
        'phone-number': phone_number, 
        'password': password, 
        'cart': [], 
        'favorites': [], 
        'shipping-data': {}, 
        'payment-data': {}, 
        'contact-data': {}, 
        'user_id': random.randint(100000, 999999),
        'promoCode': ''.join([random.choice(characters) for _ in range(8)]),
        'notifications': {
            'newDeals': True,
            'seasonalSales': True,
            'discounts': True,
            'promoCode': True
        },
        'discount': 0
    })
    send_email('Welcome to Kids Fashion Store', email, body="Welcome to our store!\nThank you for signing up. You can now log in to your new account.\nHappy shopping!", html='welcome')
    return jsonify({'success': True})

@app.route('/forgot-password', methods=['GET'])
def forgot_password():
    logged_in = session.get('logged_in', False)
    if logged_in:
        return redirect('/')
    return render_template('forgot_password.html', logged_in=logged_in)

@app.route('/update-password', methods=['GET'])
def update_password():
    logged_in = session.get('logged_in', False)
    if logged_in:
        return redirect('/')
    return render_template('update_password.html', logged_in=logged_in)

@app.route('/reset-password', methods=['POST'])
def reset_password():
    email = request.json.get('email')
    user = get_user({'email': email})
    if not user:
        return jsonify({'success': False, 'error': 'User not found'})
    reset = {
        'code': random.randint(100000, 999999),
        'expires': datetime.now().timestamp()+3600
    }
    database.update_user({'email': email}, {'$set': {'reset': reset}})
    send_email('Password reset', email, html='password_reset', data={'code': reset['code']})
    return jsonify({'success': True})

@app.route('/update-password', methods=['POST'])
def update_password_post():
    email = request.json.get('email')
    code = request.json.get('code').replace("-", "")
    password = request.json.get('password')
    print(email, code, password)
    user = get_user({'email': email})
    if not user or not user.get('reset'):
        return jsonify({'success': False, 'error': 'User not found'})
    if user['reset']['code'] != int(code) or user['reset']['expires'] < datetime.now().timestamp():
        print(user['reset'])
        return jsonify({'success': False, 'error': 'Invalid code'})
    database.update_user({'email': email}, {'$set': {'password': password}})
    return jsonify({'success': True})

@app.route('/preview-email/<file>')
def preview_email(file):
    data = {
        'code': 123456
    }
    return render_template('mail/'+file+'.html', data=data)

if __name__ == "__main__":
    # send_email('Welcome to Kids Fashion Store', "test@kids.com", body="Welcome to our store!\nThank you for signing up. You can now log in to your new account.\nHappy shopping!", html='welcome')
    app.run(debug=True, port=8080)