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
app.config['MAIL_USETLS'] = True
app.config['MAIL_USERNAME'] = '49eeff352c2a4d'
app.config['MAIL_PASSWORD'] = 'edb53d7d51b475'
app.config['MAIL_DEFAULT_SENDER'] = 'noreply@kidsfashionstore.ua'
mail = Mail(app)

# Helper functions
def sendEmail(subject, recipient, body=None, html=None, data=None):
    with app.app_context():
        if html: 
            htmlContent = render_template('mail/'+html+'.html', data=data)
            if not body:
                soup = BeautifulSoup(htmlContent, 'html.parser')
                body = soup.get_text()
        else:
            htmlContent = None
        msg = Message(subject, recipients=[recipient], body=body, html=htmlContent)
        mail.send(msg)

def getProducts():
    return database.getProducts()

def getUser(Filter):
    if not session.get('loggedIn', False) and 'userId' in Filter:
        return {'cart': [], 'favorites': []}
    return database.getUser(Filter)

# Index route
@app.route('/')
def index():
    indexImages = [im for im in os.listdir('static/img/covers') if im.endswith('.jpg')]
    random.shuffle(indexImages)
    indexImages = indexImages[:8*10]
    indexImages = [indexImages[i:i+10] for i in range(0, len(indexImages), 10)]
    
    products = getProducts()
    user = getUser({'userId': session.get('userId')})
    loggedIn = session.get('loggedIn', False)
    return render_template('index.html', indexImages=indexImages, productsFeatured=[p for p in products if p['tag'] == 'featured' and p['discount'] == 0][:4], productsSale=sorted([p for p in products if p['tag'] == 'sale' and p['discount'] != 0], key=lambda x: x['discount'], reverse=True)[:4], userData=user, loggedIn=loggedIn)

# Shop routes
@app.route('/shop')
def shop():
    brand = request.args.get('brand')
    category = request.args.get('category')
    shoeSize = request.args.get('shoeSize')
    priceRange = request.args.get('priceRange')
    priceMin = int(priceRange.split('-')[0]) if priceRange else None
    priceMax = int(priceRange.split('-')[1]) if priceRange else None
    sorting = request.args.get('sorting')

    if not request.args.get('productsPerPage'): productsPerPage = 12
    else: productsPerPage = int(request.args.get('productsPerPage'))
    if not request.args.get('page'): page = 1
    else: page = int(request.args.get('page'))

    products = getProducts()
    brands = sorted(list(set([p['brand'] for p in products])))
    categories = sorted(list(set([p['category'] for p in products])))
    sizes = sorted(list(set([size for p in products for size in p['sizes']])))

    if brand: products = [p for p in products if p['brand'] == brand]
    if category: products = [p for p in products if p['category'] == category]
    if shoeSize: products = [p for p in products if int(shoeSize) in p['sizes']]
    if priceRange: products = [p for p in products if priceMin<=int(p['price'])<=priceMax]

    if sorting == 'priceLowToHigh': products = sorted(products, key=lambda x: x['price'])
    elif sorting == 'priceHighToLow': products = sorted(products, key=lambda x: x['price'], reverse=True)
    elif sorting == 'discountLowToHigh': products = sorted(products, key=lambda x: x['discount'])
    elif sorting == 'discountHighToLow': products = sorted(products, key=lambda x: x['discount'], reverse=True)

    productsCurrent = products[(page-1)*productsPerPage:page*productsPerPage]

    maxPages = math.ceil(len(products)/productsPerPage)

    user = getUser({'userId': session.get('userId')})

    for n, p in enumerate(productsCurrent):
        productsCurrent[n]['sizes'] = sorted(p['sizes'])

    loggedIn = session.get('loggedIn', False)

    return render_template('shop.html', products=productsCurrent, userData=user, brand=brand, category=category, shoeSize=shoeSize, priceRange=priceRange, sorting=sorting, productsPerPage=productsPerPage, page=page, maxPages=maxPages, loggedIn=loggedIn, brands=brands, categories=categories, sizes=sizes)

@app.route('/product/<productId>')
def product(productId):
    products = getProducts()
    product = database.getProduct({'id': int(productId)})
    user = getUser({'userId': session.get('userId')})
    loggedIn = session.get('loggedIn', False)
    return render_template('product.html', product=product, userData=user, productsFeatured=[p for p in products if p['tag'] == 'featured' and p['discount'] == 0][:4], loggedIn=loggedIn)

# Static pages
@app.route('/faq')
def faq():
    loggedIn = session.get('loggedIn', False)
    faq = database.getFaq()
    return render_template('faq.html', faqPosts=faq, loggedIn=loggedIn)

@app.route('/faq/<faqName>')
def faqPost(faqName):
    loggedIn = session.get('loggedIn', False)
    if faqName == 'shoeSize':
        return render_template('faq/shoeSize.html', loggedIn=loggedIn)
    elif faqName == 'delivery':
        return render_template('faq/delivery.html', loggedIn=loggedIn)
    elif faqName == 'replacementsReturns':
        return render_template('faq/replacementsReturns.html', loggedIn=loggedIn)
    
@app.route('/contact')
def contact():
    loggedIn = session.get('loggedIn', False)
    return render_template('contact.html', loggedIn=loggedIn)

# Legal routes
@app.route('/termsofuse')
def termsofuse():
    loggedIn = session.get('loggedIn', False)
    return render_template('legal/termsOfUse.html', loggedIn=loggedIn)

@app.route('/privacypolicy')
def privacypolicy():
    loggedIn = session.get('loggedIn', False)
    return render_template('legal/privacy.html', loggedIn=loggedIn)

@app.route('/cookiespolicy')
def cookiespolicy():
    loggedIn = session.get('loggedIn', False)
    return render_template('legal/cookies.html', loggedIn=loggedIn)

@app.route('/shippingpolicy')
def shippingpolicy():
    loggedIn = session.get('loggedIn', False)
    return render_template('legal/shipping.html', loggedIn=loggedIn)

@app.route('/replacementsandreturnspolicy')
def replacementsandreturnspolicy():
    loggedIn = session.get('loggedIn', False)
    return render_template('legal/replacementsAndReturns.html', loggedIn=loggedIn)

# Cart + favorites routes
@app.route('/favorites')
def favorites():
    loggedIn = session.get('loggedIn', False)
    if not loggedIn:
        return redirect('/login?next=favorites')
    
    if not request.args.get('page'): page = 1
    else: page = int(request.args.get('page'))

    user = getUser({'userId': session.get('userId')})
    products = getProducts()
    favoriteItems = []
    for item in user['favorites']:
        product = database.getProduct({'id': item})
        favoriteItems.append(product)

    favoriteItems = favoriteItems[(page-1)*12:page*12]
    maxPages = math.ceil(len(user['favorites'])/12)

    return render_template('favorites.html', userData=user, favoriteItems=favoriteItems, productsFeatured=[p for p in products if p['tag'] == 'featured' and p['discount'] == 0][:4], page=page, maxPages=maxPages, loggedIn=loggedIn)

@app.route('/favorite/<productNumber>', methods=['POST'])
def favorite(productNumber):
    favorites = database.getUser({'userId': session.get('userId')})['favorites']

    if int(productNumber) in favorites: database.updateUser({'userId': session.get('userId')}, {'$pull': {'favorites': int(productNumber)}})
    else: database.updateUser({'userId': session.get('userId')}, {'$push': {'favorites': int(productNumber)}})

    return jsonify({'success': True, 'favorite': not int(productNumber) in favorites})

@app.route('/cart')
def cart():
    loggedIn = session.get('loggedIn', False)
    if not loggedIn:
        return redirect('/login?next=cart')
    user = getUser({'userId': session.get('userId')})
    products = getProducts()
    cartItems = []
    subtotal = 0
    for item in user['cart']:
        product = database.getProduct({'id': item['productId']})
        subtotal += int(product['price'])*int(item['quantity'])
        cartItems.append({'id': item['productId'], 'size': item['size'], 'quantity': item['quantity'], 'info': product})
    return render_template('cart.html', userData=user, cartItems=cartItems, subtotal=subtotal, productsFeatured=[p for p in products if p['tag'] == 'featured' and p['discount'] == 0][:4], loggedIn=loggedIn)

@app.route('/addToCart/<productId>', methods=['POST'])
def addToCart(productId):
    size = request.json.get('size')
    quantity = request.json.get('quantity')
    database.updateUser({'userId': session.get('userId')}, {'$push': {'cart': {'productId': int(productId), 'size': int(size), 'quantity': int(quantity)}}})
    return jsonify({'success': True})

@app.route('/removeFromCart/<productId>', methods=['POST'])
def removeFromCart(productId):
    size = request.json.get('size')
    quantity = request.json.get('quantity')
    database.updateUser({'userId': session.get('userId')}, {'$pull': {'cart': {'productId': int(productId), 'size': int(size), 'quantity': int(quantity)}}})
    return jsonify({'success': True})

@app.route('/editCart/<productId>', methods=['POST'])
def editCart(productId):
    size = request.json.get('size')
    quantity = request.json.get('quantity')
    database.updateUser({'userId': session.get('userId'), 'cart.productId': int(productId)},
    {'$set': {'cart.$.size': int(size), 'cart.$.quantity': int(quantity)}})
    return jsonify({'success': True})

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'GET':
        loggedIn = session.get('loggedIn', False)
        if not loggedIn:
            return redirect('/login?next=checkout')
        user = getUser({'userId': session.get('userId')})
        if not user['cart']:
            return redirect('/cart')
        products = getProducts()
        cartItems = []
        subtotal = 0
        for item in user['cart']:
            product = database.getProduct({'id': item['productId']})
            subtotal += int(product['price'])*int(item['quantity'])
            cartItems.append({'id': item['productId'], 'size': item['size'], 'quantity': item['quantity'], 'info': product})

        countryCodes = nova.loadCountryCodes()
        codesCountry = {v: k for k, v in countryCodes.items()}
        deliveryCountries = nova.loadCountries()
        deliveryCities = nova.loadCities()

        shippingData = user['shippingData']
        paymentData = user['paymentData']
        contactData = user['contactData']

        featuredProducts = [p for p in products if p['tag'] == 'featured' and p['discount'] == 0]

        return render_template('checkout.html', userData=user, cartItems=cartItems, subtotal=subtotal, productsFeatured=[p for p in products if p['tag'] == 'featured' and p['discount'] == 0][:4], loggedIn=loggedIn, deliveryCountries=deliveryCountries, deliveryCities=deliveryCities, featuredProducts=featuredProducts, countryCodes=countryCodes, codesCountry=codesCountry, shippingData=shippingData, paymentData=paymentData, contactData=contactData)
    elif request.method == 'POST':
        data = request.json

        data["orderId"] = ''.join([random.choice(characters) for _ in range(8)])
        data["cart"] = getUser({'userId': session.get('userId')})['cart']
        data["userId"] = session.get('userId')
        data["status"] = "pending"

        database.addOrder(data)
        database.updateUser({'userId': session.get('userId')}, {'$set': {'cart': []}})

        if data['saveShippingData']: 
            shippingData = {
                'firstName': data['firstName'],
                'lastName': data['lastName'],
                'middleName': data['middleName'],
                'country': data['country'],
                'city': data['city'],
                'deliveryMethod': data['deliveryMethod'],
            }
            if data['deliveryMethod'] == 'pickUpFromPostOffice':
                shippingData['postOfficeBranch'] = data['postOfficeBranch']
            else:
                shippingData['address'] = data['address']
                shippingData['address2'] = data['address2']
                shippingData['postalCode'] = data['postalCode']
            database.updateUser({'userId': session.get('userId')}, {'$set': {'shippingData': shippingData}})
        if data['savePaymentData']: 
            paymentData = {
                'paymentMethod': data['paymentMethod']
            }
            database.updateUser({'userId': session.get('userId')}, {'$set': {'paymentData': paymentData}})
        if data['saveContactData']: 
            contactData = {
                'contactMessenger': data['contactMessenger']
            }
            if data['contactMessenger'] == 'instagram':
                contactData['username'] = data['username']
            else:
                contactData['phoneNumber'] = data['phoneNumber']
            database.updateUser({'userId': session.get('userId')}, {'$set': {'contactData': contactData}})

        if data['contactMessenger'] == 'telegram':
            messenger = f"<a href='https://t.me/{data['phoneNumber'].replace('(', '').replace(')', '').replace(' ', '')}'>Telegram</a>"
        elif data['contactMessenger'] == 'viber':
            messenger = f"<a href='viber://chat?number={data['phoneNumber'].replace('(', '').replace(')', '').replace(' ', '')}'>Viber</a>"
        elif data['contactMessenger'] == 'instagram':
            messenger = f"<a href='https://instagram.com/{data['username']}'>Instagram</a>"

        sendMessage(f"<b>New order: {data['orderId']}</b>. Check it <a href='https://kidsfashionstore.com.ua/orders/{data['orderId']}'>here</a>. Customer: {data['firstName']} {data['lastName']}, contact in " + messenger)

        return jsonify({'success': True})

@app.route('/getBranches', methods=['POST'])
def getBranches():
    countryCode = request.json.get('countryCode')
    city = request.json.get('city')
    try:
        branches = nova.getBranches(countryCode, city)
        branches = sorted(branches, key=lambda x: int(x['number'].split("/")[-1]))
    except:
        return jsonify({'success': False, 'error': 'Error fetching branches'})
    return jsonify({'success': True, 'branches': branches})

@app.route('/orderConfirmation')
def orderConfirmation():
    loggedIn = session.get('loggedIn', False)
    if not loggedIn:
        return redirect('/login?next=orderConfirmation')
    user = getUser({'userId': session.get('userId')})
    products = getProducts()
    productsFeatured = [p for p in products if p['tag'] == 'featured' and p['discount'] == 0]
    return render_template('orderConfirmation.html', userData=user, loggedIn=loggedIn, productsFeatured=productsFeatured[:4])

@app.route('/orders')
def orders():
    loggedIn = session.get('loggedIn', False)
    if not loggedIn:
        return redirect('/login?next=orders')
    user = getUser({'userId': session.get('userId')})
    orders = database.getOrders({'userId': session.get('userId')})
    for order in orders:
        cartItems = []
        for item in order['cart']:
            product = database.getProduct({'id': item['productId']})
            cartItems.append({'id': item['productId'], 'size': item['size'], 'quantity': item['quantity'], 'info': product})
        order['cart'] = cartItems
    products = getProducts()
    productsFeatured = [p for p in products if p['tag'] == 'featured' and p['discount'] == 0]
    return render_template('orders.html', userData=user, orders=orders, loggedIn=loggedIn, productsFeatured=productsFeatured[:4])

@app.route('/orders/<orderId>/<productId>')
def order(orderId, productId):
    loggedIn = session.get('loggedIn', False)
    if not loggedIn:
        return redirect('/login?next=orders')
    user = getUser({'userId': session.get('userId')})
    order = database.getOrder({'orderId': orderId})
    order['product'] = [o for o in order['cart'] if int(o['productId']) == int(productId)][0]
    order['product']['info'] = database.getProduct({'id': int(productId)})
    products = getProducts()
    productsFeatured = [p for p in products if p['tag'] == 'featured' and p['discount'] == 0]

    countryCodes = nova.loadCountryCodes()
    codesCountry = {v: k for k, v in countryCodes.items()}

    return render_template('order.html', userData=user, order=order, loggedIn=loggedIn, productsFeatured=productsFeatured[:4], codesCountry=codesCountry)

# Settings
@app.route('/settings')
def settings():
    loggedIn = session.get('loggedIn', False)
    if not loggedIn:
        return redirect('/login?next=settings')
    user = getUser({'userId': session.get('userId')})

    deliveryCountries = nova.loadCountries()
    deliveryCities = nova.loadCities()
    codesCountry = {v: k for k, v in nova.loadCountryCodes().items()}

    return render_template('settings.html', userData=user, loggedIn=loggedIn, codesCountry=codesCountry, deliveryCountries=deliveryCountries, deliveryCities=deliveryCities)

@app.route('/updateSettings', methods=['POST'])
def updateSettings():
    data = request.json
    for key, value in data.items():
        if key == "messengerUsername": key="username"
        elif key == "messenger": key="contactMessenger"

        if key in ['firstName', 'lastName', 'middleName', 'country', 'city', 'address', 'address2', 'postalCode', 'deliveryMethod', 'postOfficeBranch']: key = 'shippingData.'+key
        elif key in ['paymentMethod']: key = 'paymentData.'+key
        elif key in ['contactMessenger', 'username', 'phoneNumber']: key = 'contactData.'+key
        elif key in ['newDeals', 'seasonalSales', 'discounts', 'promoCode']: key = 'notifications.'+key
        database.updateUser({'userId': session.get('userId')}, {'$set': {key: value}})  
    return jsonify({'success': True})

# Newsletter route
@app.route('/newsletterSignup', methods=['POST'])
def newsletterSignup():
    email = request.json.get('email')
    database.addToNewsletter(email)
    return jsonify({'success': True})

# Auth routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        loggedIn = session.get('loggedIn', False)
        if loggedIn:
            return redirect('/')
        return render_template('login.html', loggedIn=loggedIn)
        
    email = request.json.get('email')
    password = request.json.get('password')
    user = getUser({'email': email})

    if user and user['password'] == password:
        print(user)
        session['userId'] = user['userId']
        session['loggedIn'] = True
        return jsonify({'success': True})

    return jsonify({'success': False, 'error': 'Incorrect email or password'})

@app.route('/logout')
def logout():
    session.pop('userId', None)
    session.pop('loggedIn', None)
    return redirect('/')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        loggedIn = session.get('loggedIn', False)
        if loggedIn:
            return redirect('/')
        return render_template('signup.html', loggedIn=loggedIn)
    
    email = request.json.get('email')
    phoneNumber = request.json.get('phone')
    password = request.json.get('password')

    user = getUser({'email': email})
    if user:
        return jsonify({'success': False, 'error': 'User already exists'})
    
    database.addUser({
        'email': email, 
        'phoneNumber': phoneNumber, 
        'password': password, 
        'cart': [], 
        'favorites': [], 
        'shippingData': {}, 
        'paymentData': {}, 
        'contactData': {}, 
        'userId': random.randint(100000, 999999),
        'promoCode': ''.join([random.choice(characters) for _ in range(8)]),
        'notifications': {
            'newDeals': True,
            'seasonalSales': True,
            'discounts': True,
            'promoCode': True
        },
        'discount': 0
    })
    sendEmail('Welcome to Kids Fashion Store', email, body="Welcome to our store!\nThank you for signing up. You can now log in to your new account.\nHappy shopping!", html='welcome')
    return jsonify({'success': True})

@app.route('/forgotPassword', methods=['GET'])
def forgotPassword():
    loggedIn = session.get('loggedIn', False)
    if loggedIn:
        return redirect('/')
    return render_template('forgotPassword.html', loggedIn=loggedIn)

@app.route('/updatePassword', methods=['GET'])
def updatePassword():
    loggedIn = session.get('loggedIn', False)
    if loggedIn:
        return redirect('/')
    return render_template('updatePassword.html', loggedIn=loggedIn)

@app.route('/resetPassword', methods=['POST'])
def resetPassword():
    email = request.json.get('email')
    user = getUser({'email': email})
    if not user:
        return jsonify({'success': False, 'error': 'User not found'})
    reset = {
        'code': random.randint(100000, 999999),
        'expires': datetime.now().timestamp()+3600
    }
    database.updateUser({'email': email}, {'$set': {'reset': reset}})
    sendEmail('Password reset', email, html='passwordReset', data={'code': reset['code']})
    return jsonify({'success': True})

@app.route('/updatePassword', methods=['POST'])
def updatePasswordPost():
    email = request.json.get('email')
    code = request.json.get('code').replace("-", "")
    password = request.json.get('password')
    print(email, code, password)
    user = getUser({'email': email})
    if not user or not user.get('reset'):
        return jsonify({'success': False, 'error': 'User not found'})
    if user['reset']['code'] != int(code) or user['reset']['expires'] < datetime.now().timestamp():
        print(user['reset'])
        return jsonify({'success': False, 'error': 'Invalid code'})
    database.updateUser({'email': email}, {'$set': {'password': password}})
    return jsonify({'success': True})

@app.route('/previewEmail/<file>')
def previewEmail(file):
    data = {
        'code': 123456
    }
    return render_template('mail/'+file+'.html', data=data)

if __name__ == "__main__":
    # sendEmail('Welcome to Kids Fashion Store', "test@kids.com", body="Welcome to our store!\nThank you for signing up. You can now log in to your new account.\nHappy shopping!", html='welcome')
    app.run(debug=True, port=8080)