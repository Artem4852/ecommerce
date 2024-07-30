from flask import Flask, request, abort, jsonify, render_template, session, redirect
from flask_mail import Mail, Message
from database import Database
import os, random, math, dotenv, re
from bs4 import BeautifulSoup
from datetime import datetime
from string import ascii_letters, digits

from novapost import NovaAPI
from telegramAPI import sendMessage
from instagram import getPost
from siteStatistics import log

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

def notifyFavorites(productId, brand, category, price):
    users = database.getUsers()
    toSend = []
    for user in users:
        if 'favorites' in user and productId in user['favorites'] and user['notifications']['discounts']:
            toSend.append(user)
    for user in toSend:
        sendEmail('New discount on your favorite product', user['email'], html='saleFavorite', data={'productId': productId, 'name': f"{category} {brand}", 'price': price})

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

    featured = [p for p in products if 'tags' in p and 'featured' in p['tags'] and p['discount'] == 0 and len(p['sizes']) > 0]
    random.shuffle(featured)

    sale = [p for p in products if 'tags' in p and 'sale' in p['tags'] and len(p['sizes']) > 0]
    random.shuffle(sale)

    logResponse = log('home', request=request)
    if logResponse: return logResponse
    return render_template('index.html', indexImages=indexImages, productsFeatured=featured[:4], productsSale=sale[:4], userData=user, loggedIn=loggedIn)

# Shop routes
@app.route('/shop')
def shop():
    brand = request.args.get('brand')
    category = request.args.get('category')
    shoeSize = request.args.get('shoeSize')
    if shoeSize: shoeSize = int(shoeSize)
    priceRange = request.args.get('priceRange')
    priceMin = int(priceRange.split('-')[0]) if priceRange else None
    priceMax = int(priceRange.split('-')[1]) if priceRange else None
    sorting = request.args.get('sorting')

    if not request.args.get('productsPerPage'): productsPerPage = 12
    else: productsPerPage = int(request.args.get('productsPerPage'))
    if not request.args.get('page'): page = 1
    else: page = int(request.args.get('page'))

    products = getProducts()
    products = [p for p in products if p['price'] != "" and len(p['images']) > 0 and 'tags' in p and (not 'archived' in p['tags'] or 'admin' in getUser({'userId': session.get('userId')})['tags'])]
    brands = sorted(list(set([p['brand'] for p in products if p['brand'] != ""])))
    categories = sorted(list(set([p['category'] for p in products if p['category'] != ""])))
    sizes = sorted(list(set([size for p in products for size in p['sizes'] if size != ""])))

    if brand: products = [p for p in products if p['brand'] == brand]
    if category: products = [p for p in products if p['category'] == category]
    if shoeSize: products = [p for p in products if int(shoeSize) in p['sizes']]
    if priceRange: products = [p for p in products if priceMin<=int(p['price'])<=priceMax]

    if sorting == 'priceLowToHigh': products = sorted(products, key=lambda x: int(x['price']))
    elif sorting == 'priceHighToLow': products = sorted(products, key=lambda x: int(x['price']), reverse=True)
    elif sorting == 'discountLowToHigh': products = sorted(products, key=lambda x: int(x['discount']))
    elif sorting == 'discountHighToLow': products = sorted(products, key=lambda x: int(x['discount']), reverse=True)

    productsCurrent = products[(page-1)*productsPerPage:page*productsPerPage]

    maxPages = math.ceil(len(products)/productsPerPage)

    user = getUser({'userId': session.get('userId')})

    for n, p in enumerate(productsCurrent):
        productsCurrent[n]['sizes'] = sorted(p['sizes'])

    loggedIn = session.get('loggedIn', False)

    logResponse = log('shop', request=request)
    if logResponse: return logResponse
    return render_template('shop.html', products=productsCurrent, userData=user, brand=brand, category=category, shoeSize=shoeSize, priceRange=priceRange, sorting=sorting, productsPerPage=productsPerPage, page=page, maxPages=maxPages, loggedIn=loggedIn, brands=brands, categories=categories, sizes=sizes)

@app.route('/product/<productId>')
def product(productId):
    products = getProducts()
    product = database.getProduct({'id': int(productId)})
    if not product or not 'tags' in product or ('archived' in product['tags'] and not 'admin' in getUser({'userId': session.get('userId')})['tags']): return abort(404)

    additionalInformation = product['additionalInformation'].copy()
    for key, value in additionalInformation.items():
        product['additionalInformation'][re.sub(r'([a-z])([A-Z])', r'\1 \2', key)] = value
        del product['additionalInformation'][key]

    user = getUser({'userId': session.get('userId')})
    loggedIn = session.get('loggedIn', False)

    productsFeatured = [p for p in products if 'tags' in p and 'featured' in p['tags'] and len(p['sizes']) > 0 and p['id'] != int(productId)]
    random.shuffle(productsFeatured)

    if loggedIn: contactData = user['contactData']
    else: contactData = {}

    logResponse = log('product', request=request)
    if logResponse: return logResponse
    return render_template('product.html', product=product, userData=user, productsFeatured=productsFeatured[:4], loggedIn=loggedIn, contactData=contactData)

# Static pages
@app.route('/faq')
def faq():
    loggedIn = session.get('loggedIn', False)
    faq = database.getFaq()
    if loggedIn:
        userData = getUser({'userId': session.get('userId')})
    else:
        userData = {}
    logResponse = log('faq', request=request)
    if logResponse: return logResponse
    return render_template('faq.html', faqPosts=faq, loggedIn=loggedIn, userData=userData)

@app.route('/faq/<faqName>')
def faqPost(faqName):
    loggedIn = session.get('loggedIn', False)
    if loggedIn: 
        userData = getUser({'userId': session.get('userId')})
    else:
        userData = {}
    logResponse = log('faq', request=request)
    if logResponse: return logResponse
    if faqName == 'shoeSize':
        return render_template('faq/shoeSize.html', loggedIn=loggedIn, userData=userData)
    elif faqName == 'delivery':
        return render_template('faq/delivery.html', loggedIn=loggedIn, userData=userData)
    elif faqName == 'replacementsReturns':
        return render_template('faq/replacementsReturns.html', loggedIn=loggedIn, userData=userData)
    
@app.route('/contact')
def contact():
    loggedIn = session.get('loggedIn', False)
    if loggedIn:
        userData = getUser({'userId': session.get('userId')})
    else:
        userData = {}
    logResponse = log('contact', request=request)
    if logResponse: return logResponse
    return render_template('contact.html', loggedIn=loggedIn, userData=userData)

# Legal routes
@app.route('/termsofuse')
def termsofuse():
    loggedIn = session.get('loggedIn', False)
    if loggedIn:
        userData = getUser({'userId': session.get('userId')})
    else:
        userData = {}
    logResponse = log('legal', request=request)
    if logResponse: return logResponse
    return render_template('legal/termsOfUse.html', loggedIn=loggedIn, userData=userData)

@app.route('/privacypolicy')
def privacypolicy():
    loggedIn = session.get('loggedIn', False)
    if loggedIn:
        userData = getUser({'userId': session.get('userId')})
    else:
        userData = {}
    logResponse = log('legal', request=request)
    if logResponse: return logResponse
    return render_template('legal/privacy.html', loggedIn=loggedIn, userData=userData)

@app.route('/cookiespolicy')
def cookiespolicy():
    loggedIn = session.get('loggedIn', False)
    if loggedIn:
        userData = getUser({'userId': session.get('userId')})
    else:
        userData = {}
    logResponse = log('legal', request=request)
    if logResponse: return logResponse
    return render_template('legal/cookies.html', loggedIn=loggedIn, userData=userData)

@app.route('/shippingpolicy')
def shippingpolicy():
    loggedIn = session.get('loggedIn', False)
    if loggedIn:
        userData = getUser({'userId': session.get('userId')})
    else:
        userData = {}
    logResponse = log('legal', request=request)
    if logResponse: return logResponse
    return render_template('legal/shipping.html', loggedIn=loggedIn, userData=userData)

@app.route('/replacementsandreturnspolicy')
def replacementsandreturnspolicy():
    loggedIn = session.get('loggedIn', False)
    if loggedIn:
        userData = getUser({'userId': session.get('userId')})
    else:
        userData = {}
    logResponse = log('legal', request=request)
    if logResponse: return logResponse
    return render_template('legal/replacementsAndReturns.html', loggedIn=loggedIn, userData=userData)

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

    productsFeatured = [p for p in products if 'tags' in p and 'featured' in p['tags'] and len(p['sizes']) > 0]
    random.shuffle(productsFeatured)

    logResponse = log('shop', request=request)
    if logResponse: return logResponse
    return render_template('favorites.html', userData=user, favoriteItems=favoriteItems, productsFeatured=productsFeatured[:4], page=page, maxPages=maxPages, loggedIn=loggedIn)

@app.route('/favorite/<productNumber>', methods=['POST'])
def favorite(productNumber):
    favorites = database.getUser({'userId': session.get('userId')})['favorites']

    if int(productNumber) in favorites: database.updateUser({'userId': session.get('userId')}, {'$pull': {'favorites': int(productNumber)}})
    else: database.updateUser({'userId': session.get('userId')}, {'$push': {'favorites': int(productNumber)}})

    return jsonify({'success': True, 'favorite': not int(productNumber) in favorites})

@app.route('/quickOrder', methods=['POST'])
def quickOrder():
    productId = request.json.get('productId')
    size = request.json.get('size')
    quantity = request.json.get('quantity')
    contactMessenger = request.json.get('contactMessenger')
    phoneNumber = request.json.get('phoneNumber')
    username = request.json.get('username')
    username = username.replace('@', '')

    data = {
        'orderId': ''.join([random.choice(characters) for _ in range(8)]),
        'cart': [{'productId': int(productId), 'size': int(size), 'quantity': int(quantity)}],
        'userId': session.get('userId', None),
        'status': 'pending',
        'contactMessenger': contactMessenger
    }
    if contactMessenger in ['telegram', 'viber']:
        data['phoneNumber'] = phoneNumber
    elif contactMessenger == 'instagram':
        data['username'] = username

    data['timestamp'] = datetime.now().timestamp()

    database.addOrder(data)
    database.updateUser({'userId': session.get('userId')}, {'$set': {'cart': [], 'promoCodeUsed': True}})

    loggedIn = session.get('loggedIn', False)
    if loggedIn:
        userData = getUser({'userId': session.get('userId')})
        contactData = userData['contactData']
        contactData['contactMessenger'] = contactMessenger
        if contactMessenger in ['telegram', 'viber']:
            contactData['phoneNumber'] = phoneNumber
        elif contactMessenger == 'instagram':
            contactData['username'] = username
        database.updateUser({'userId': session.get('userId')}, {'$set': {'contactData': contactData}})

    if contactMessenger == 'telegram':
        messenger = f"<a href='https://t.me/{data['phoneNumber'].replace('(', '').replace(')', '').replace(' ', '')}'>Telegram</a>"
    elif contactMessenger == 'viber':
        messenger = f"<a href='viber://chat?number={phoneNumber.replace('(', '').replace(')', '').replace(' ', '')}'>Viber</a>"
    elif contactMessenger == 'instagram':
        messenger = f"<a href='https://instagram.com/{username}'>Instagram</a>"
    
    contactInfo = phoneNumber if contactMessenger in ['telegram', 'viber'] else username

    sendMessage(f"<b>New order:</b> <a href='https://kidsfashionstore.com.ua/admin/orders?orderId={data['orderId']}'>{data['orderId']}</a>. Product id: <a href='https://kidsfashionstore.com.ua/product/{productId}'>{productId}</a>. Size: {size}, quantity: {quantity}. Contact customer: on {messenger}, {contactInfo}.")

    return jsonify({'success': True})

# @app.route('/cart')
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

    productsFeatured = [p for p in products if 'tags' in p and 'featured' in p['tags'] and len(p['sizes']) > 0]

    logResponse = log('shop', request=request)
    if logResponse: return logResponse
    return render_template('cart.html', userData=user, cartItems=cartItems, subtotal=subtotal, productsFeatured=productsFeatured[:4], loggedIn=loggedIn)

# @app.route('/addToCart/<productId>', methods=['POST'])
def addToCart(productId):
    size = request.json.get('size')
    quantity = request.json.get('quantity')
    database.updateUser({'userId': session.get('userId')}, {'$push': {'cart': {'productId': int(productId), 'size': int(size), 'quantity': int(quantity)}}})
    return jsonify({'success': True})

# @app.route('/removeFromCart/<productId>', methods=['POST'])
def removeFromCart(productId):
    size = request.json.get('size')
    quantity = request.json.get('quantity')
    database.updateUser({'userId': session.get('userId')}, {'$pull': {'cart': {'productId': int(productId), 'size': int(size), 'quantity': int(quantity)}}})
    return jsonify({'success': True})

# @app.route('/editCart/<productId>', methods=['POST'])
def editCart(productId):
    size = request.json.get('size')
    quantity = request.json.get('quantity')
    database.updateUser({'userId': session.get('userId'), 'cart.productId': int(productId)},
    {'$set': {'cart.$.size': int(size), 'cart.$.quantity': int(quantity)}})
    return jsonify({'success': True})

# @app.route('/checkPromoCode', methods=['POST'])
def checkPromoCode():
    promoCode = request.json.get('promoCode')
    current_user = getUser({'userId': session.get('userId')})
    if current_user['promoCodeUsed']: return jsonify({'success': False, 'error': 'You have already used a promo code'})
    user = getUser({'promoCode': promoCode})
    if not user: return jsonify({'success': False, 'error': 'Invalid promo code'})
    else:
        # database.updateUser({'userId': session.get('userId')}, {'$set': {'promoCodeUsed': True}})
        # database.updateUser({'promoCode': promoCode}, {'$set': {'discount': int(user['discount']+1)}})
        return jsonify({'success': True, 'discount': 1})
    # cxAiihvK

# @app.route('/checkout', methods=['GET', 'POST'])
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
            del product['_id']
            subtotal += int(product['price'])*int(item['quantity'])
            cartItems.append({'id': item['productId'], 'size': item['size'], 'quantity': item['quantity'], 'info': product})

        countryCodes = nova.loadCountryCodes()
        codesCountry = {v: k for k, v in countryCodes.items()}
        deliveryCountries = nova.loadCountries()
        deliveryCities = nova.loadCities()

        shippingData = user['shippingData']
        paymentData = user['paymentData']
        contactData = user['contactData']

        productsFeatured = [p for p in products if 'tags' in p and 'featured' in p['tags'] and len(p['sizes']) > 0]
        random.shuffle(productsFeatured)

        logResponse = log('shop', request=request)
        if logResponse: return logResponse
        return render_template('checkout.html', userData=user, cartItems=cartItems, subtotal=subtotal, productsFeatured=productsFeatured[:4], loggedIn=loggedIn, deliveryCountries=deliveryCountries, deliveryCities=deliveryCities, featuredProducts=productsFeatured, countryCodes=countryCodes, codesCountry=codesCountry, shippingData=shippingData, paymentData=paymentData, contactData=contactData)
    elif request.method == 'POST':
        data = request.json

        data["orderId"] = ''.join([random.choice(characters) for _ in range(8)])
        data["cart"] = getUser({'userId': session.get('userId')})['cart']
        data["userId"] = session.get('userId')
        data["status"] = "pending"

        data["timestamp"] = datetime.now().timestamp()

        database.addOrder(data)
        database.updateUser({'userId': session.get('userId')}, {'$set': {'cart': [], 'promoCodeUsed': True}})

        if data['promoCode']:
            user = getUser({'promoCode': data['promoCode']})
            database.updateUser({'promoCode': data['promoCode']}, {'$set': {'discount': int(user['discount']+1)}})

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

        sendMessage(f"<b>New order:</b> <a href='https://kidsfashionstore.com.ua/admin/orders?orderId={data['orderId']}'>{data['orderId']}</a>. Customer: {data['firstName']} {data['lastName']}, on " + messenger)

        return jsonify({'success': True})

# @app.route('/getBranches', methods=['POST'])
def getBranches():
    countryCode = request.json.get('countryCode')
    city = request.json.get('city')
    try:
        branches = nova.getBranches(countryCode, city)
        branches = sorted(branches, key=lambda x: int(x['number'].split("/")[-1]))
    except:
        return jsonify({'success': False, 'error': 'Error fetching branches'})
    return jsonify({'success': True, 'branches': branches})

# @app.route('/getShippingPrice', methods=['POST'])
def getShippingPrice():
    countryCode = request.json.get('countryCode')
    branch = request.json.get('branch')
    cart = request.json.get('cart')

    warehouses = {}
    for product in cart:
        warehouse = product['info']['warehouse']
        if warehouse not in warehouses:
            warehouses[warehouse] = []
        warehouses[warehouse].append(product)

    total = 0
    for warehouse, products in warehouses.items():
        price = nova.calculateShippingPrice(warehouse, {'countryCode': countryCode, 'branch': branch}, products)
        total += price

    return jsonify({'success': True, 'price': total})

# @app.route('/orderConfirmation')
def orderConfirmation():
    loggedIn = session.get('loggedIn', False)
    if not loggedIn:
        return redirect('/login?next=orderConfirmation')
    user = getUser({'userId': session.get('userId')})

    products = getProducts()
    productsFeatured = [p for p in products if 'tags' in p and 'featured' in p['tags'] and len(p['sizes']) > 0]
    random.shuffle(productsFeatured)

    logResponse = log('shop', request=request)
    if logResponse: return logResponse
    return render_template('orderConfirmation.html', userData=user, loggedIn=loggedIn, productsFeatured=productsFeatured[:4])

# @app.route('/orders')
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
    productsFeatured = [p for p in products if 'tags' in p and 'featured' in p['tags'] and len(p['sizes']) > 0]
    random.shuffle(productsFeatured)

    logResponse = log('orders', request=request)
    if logResponse: return logResponse
    return render_template('orders.html', userData=user, orders=orders, loggedIn=loggedIn, productsFeatured=productsFeatured[:4])

# @app.route('/orders/<orderId>/<productId>')
def order(orderId, productId):
    loggedIn = session.get('loggedIn', False)
    if not loggedIn:
        return redirect('/login?next=orders')
    user = getUser({'userId': session.get('userId')})
    order = database.getOrder({'orderId': orderId})
    if order['userId'] != user['userId']: return redirect('/orders')
    order['product'] = [o for o in order['cart'] if int(o['productId']) == int(productId)][0]
    order['product']['info'] = database.getProduct({'id': int(productId)})
    products = getProducts()

    countryCodes = nova.loadCountryCodes()
    codesCountry = {v: k for k, v in countryCodes.items()}

    productsFeatured = [p for p in products if 'tags' in p and 'featured' in p['tags'] and len(p['sizes']) > 0]
    random.shuffle(productsFeatured)

    logResponse = log('orders', request=request)
    if logResponse: return logResponse
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

    logResponse = log('home', request=request)
    if logResponse: return logResponse
    return render_template('settings.html', userData=user, loggedIn=loggedIn, codesCountry=codesCountry, deliveryCountries=deliveryCountries, deliveryCities=deliveryCities)

@app.route('/updateSettings', methods=['POST'])
def updateSettings():
    data = request.json
    for key, value in data.items():
        key = key[0].lower()+key[1:]
        if key == "messengerUsername": key="username"
        elif key == "messenger": key="contactMessenger"

        if key in ['firstName', 'lastName', 'middleName', 'country', 'city', 'address', 'address2', 'postalCode', 'deliveryMethod', 'postOfficeBranch']: key = 'shippingData.'+key
        elif key in ['paymentMethod']: key = 'paymentData.'+key
        elif key in ['contactMessenger', 'username', 'phoneNumber']: key = 'contactData.'+key
        elif key in ['newDeals', 'seasonalSales', 'discounts', 'promoCode']: key = 'notifications.'+key
        # print(key, value)
        database.updateUser({'userId': session.get('userId')}, {'$set': {key: value}})  
    return jsonify({'success': True})

# Newsletter route
@app.route('/newsletterSignup', methods=['POST'])
def newsletterSignup():
    email = request.json.get('email')
    token = database.addToNewsletter(email)
    sendEmail('Kids Fashion Store Newsletter', email, html='newsletterSignup', data={'unsubscribeToken': token})
    return jsonify({'success': True})

@app.route('/newsletterUnsubscribe/<unsubscribeToken>', methods=['GET'])
def newsletterUnsubscribe(unsubscribeToken):
    if database.removeFromNewsletter(unsubscribeToken):
        loggedIn = session.get('loggedIn', False)
        if loggedIn:
            user = getUser({'userId': session.get('userId')})
        else:
            user = {}
        return render_template('newsletterUnsubscribe.html', loggedIn=loggedIn, userData=user)
    return abort(404)

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
        # print(user)
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
        'discount': 0,
        'promoCodeUsed': False,
        "tags": []
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
    # print(email, code, password)
    user = getUser({'email': email})
    if not user or not user.get('reset'):
        return jsonify({'success': False, 'error': 'User not found'})
    if user['reset']['code'] != int(code) or user['reset']['expires'] < datetime.now().timestamp():
        # print(user['reset'])
        return jsonify({'success': False, 'error': 'Invalid code'})
    database.updateUser({'email': email}, {'$set': {'password': password}})
    return jsonify({'success': True})

@app.route('/previewEmail/<file>')
def previewEmail(file):
    data = {
        'code': 123456
    }
    return render_template('mail/'+file+'.html', data=data)

# admin
@app.route('/admin')
def admin():
    loggedIn = session.get('loggedIn', False)
    if not loggedIn:
        abort(404)
    user = getUser({'userId': session.get('userId')})
    if not "admin" in user['tags']:
        abort(404)

    dailyRequests = database.getStats('dailyRequests')['data']
    averageDailyRequests = int(sum(dailyRequests.values())/len(dailyRequests))

    sortedDailyRequests = sorted(dailyRequests, key=lambda x: x)
    dailyRequests = {n: dailyRequests[n] for n in sortedDailyRequests[-7:]}

    requestsToday = dailyRequests[sortedDailyRequests[-1]]

    dailyUniqueVisits = database.getStats('dailyUniqueVisits')['data']
    uniqueVisitsToday = len(dailyUniqueVisits[datetime.now().strftime('%d.%m.%Y')])
    averageDailyUniqueVisits = int(sum([len(v) for v in dailyUniqueVisits.values()])/len(dailyUniqueVisits))

    products = getProducts()
    totalProducts = len(products)
    inStock = len([p for p in products if len(p['sizes']) > 0])

    orders = database.getOrders()
    ordersTotal = sum([len(o['cart']) for o in database.getOrders()])
    ordersPending = sum([len(o['cart']) for o in database.getOrders({'status': 'pending'})])
    ordersToday = len([o for o in orders if datetime.fromtimestamp(o['timestamp']).strftime('%d.%m.%Y') == datetime.now().strftime('%d.%m.%Y')])
    days = []
    for o in orders:
        day = datetime.fromtimestamp(o['timestamp']).strftime('%d.%m.%Y')
        if day not in days:
            days.append(day)
    ordersDailyAverage = len(orders)//len(days)

    return render_template('admin.html', userData=user, loggedIn=loggedIn, averageDailyRequests=averageDailyRequests, dailyRequests=dailyRequests, requestsToday=requestsToday, averageDailyUniqueVisits=averageDailyUniqueVisits, uniqueVisitsToday=uniqueVisitsToday, totalProducts=totalProducts, inStock=inStock, orders=orders, ordersTotal=ordersTotal, ordersPending=ordersPending, ordersToday=ordersToday, ordersDailyAverage=ordersDailyAverage)

@app.route('/admin/products')
def adminProducts():
    loggedIn = session.get('loggedIn', False)
    if not loggedIn:
        abort(404)
    user = getUser({'userId': session.get('userId')})
    if not "admin" in user['tags']:
        abort(404)
    
    brand = request.args.get('brand')
    category = request.args.get('category')
    shoeSize = request.args.get('shoeSize')
    tag = request.args.get('tag')
    sorting = request.args.get('sorting')

    if not request.args.get('productsPerPage'): productsPerPage = 12
    else: productsPerPage = int(request.args.get('productsPerPage'))
    if not request.args.get('page'): page = 1
    else: page = int(request.args.get('page'))

    products = getProducts()
    products = [p for p in products if p['price'] != "" and len(p['images']) > 0]
    brands = sorted(list(set([p['brand'] for p in products if p['brand'] != ""])))
    categories = sorted(list(set([p['category'] for p in products if p['category'] != ""])))
    sizes = sorted(list(set([size for p in products for size in p['sizes'] if size != ""])))
    tags = sorted(list(set([tag for p in products for tag in p['tags'] if tag != ""])))

    if brand: products = [p for p in products if p['brand'] == brand]
    if category: products = [p for p in products if p['category'] == category]
    if shoeSize: products = [p for p in products if int(shoeSize) in p['sizes']]
    if tag: products = [p for p in products if tag in p['tags']]

    if sorting == 'priceLowToHigh': products = sorted(products, key=lambda x: int(x['price']))
    elif sorting == 'priceHighToLow': products = sorted(products, key=lambda x: int(x['price']), reverse=True)
    elif sorting == 'discountLowToHigh': products = sorted(products, key=lambda x: int(x['discount']))
    elif sorting == 'discountHighToLow': products = sorted(products, key=lambda x: int(x['discount']), reverse=True)

    productsCurrent = products[(page-1)*productsPerPage:page*productsPerPage]

    maxPages = math.ceil(len(products)/productsPerPage)

    user = getUser({'userId': session.get('userId')})

    for n, p in enumerate(productsCurrent):
        productsCurrent[n]['sizes'] = sorted(p['sizes'])

    return render_template('adminProducts.html', userData=user, loggedIn=loggedIn, products=productsCurrent, brand=brand, category=category, shoeSize=shoeSize, sorting=sorting, productsPerPage=productsPerPage, page=page, maxPages=maxPages, brands=brands, categories=categories, sizes=sizes, tags=tags, tag=tag)

@app.route('/admin/products/edit/<productId>')
def adminProductEdit(productId):
    loggedIn = session.get('loggedIn', False)
    if not loggedIn:
        abort(404)
    user = getUser({'userId': session.get('userId')})
    if not "admin" in user['tags']:
        abort(404)
    product = database.getProduct({'id': int(productId)})
    if not product:
        return redirect('/admin/products')
    return render_template('adminProductEdit.html', userData=user, loggedIn=loggedIn, product=product, pageType='edit')

@app.route('/admin/product/image', methods=['POST'])
def adminProductImage():
    file = request.files['file']
    productId = request.args.get('productId')
    if not file or not productId:
        return jsonify({'success': False, 'error': 'No file or product id'})
    
    os.makedirs(f'static/img/products/{productId}', exist_ok=True)

    existing = sorted([im.split('.')[0] for im in os.listdir(f'static/img/products/{productId}') if im.endswith('.jpg')])
    if existing:
        new = str(int(existing[-1])+1)
    else:
        new = '1'
    file.save(f'static/img/products/{productId}/{new}.jpg')
    product = database.getProduct({'id': int(productId)})
    images = product['images'] + [f'{new}.jpg']
    index = len(images)-1
    database.updateProduct(int(productId), {'images': images})
    return jsonify({'success': True, 'image': f'{new}.jpg', 'index': index})
    
@app.route('/admin/product/deleteImage', methods=['POST'])
def adminProductDeleteImage():
    productId = request.json.get('productId')
    image = request.json.get('image')
    if not productId or not image:
        return jsonify({'success': False, 'error': 'No product id or image'})
    os.remove(f'static/img/products/{productId}/{image}')
    product = database.getProduct({'id': int(productId)})
    images = product['images']
    try: images.remove(image)
    except: pass
    database.updateProduct(int(productId), {'images': images})
    return jsonify({'success': True})

@app.route('/admin/product/load', methods=['POST'])
def adminProductLoad():
    productId = request.json.get('productId')
    instagramUrl = request.json.get('url')
    if not productId or not instagramUrl:
        return jsonify({'success': False, 'error': 'No product id or instagram url'})
    sizes, category, brand, sizesCm, price, imagesSrcs = getPost(instagramUrl, productId)
    return jsonify({'success': True, 'sizes': sizes, 'category': category, 'brand': brand, 'sizesCm': sizesCm, 'price': price, 'images': imagesSrcs})

@app.route('/admin/product/update', methods=['POST'])
def adminProductUpdate():
    productData = request.json.get('data')
    productData['tags'] = [tag.strip() for tag in productData['tags'].split(',')]
    productData['sizes'] = [int(size) for size in productData['sizes'].split(',')]
    productData['maxQuantities'] = {quantity.strip().split(" ")[0].strip(): int(quantity.strip().split(" ")[1].replace("(", "").replace(")", "").strip()) for quantity in productData['maxQuantities'].split(',')}
    productData['sizesCm'] = {size.strip().split(" ")[0].strip(): float(size.strip().split(" ")[1].replace("cm", "").replace("(", "").replace(")", "").strip()) for size in productData['sizesCm'].split(',')}
    productData['warehouses'] = {warehouse.strip().split(" ")[0].strip(): warehouse.strip().split(" ")[1].replace("(", "").replace(")", "").strip() for warehouse in productData['warehouses'].split(',')}

    productData['discount'] = int(productData['discount'].replace("%", ""))
    productData['price'] = str(int(productData['prevPrice']) * (1 - productData['discount'] / 100))[:2]+'99'

    productData['additionalInformation'] = {
        "innerMaterial": productData['innerMaterial'],
        "insoleMaterial": productData['insoleMaterial'],
        "outerMaterial": productData['outerMaterial'],
        "season": productData['season'],
    }
    del productData['innerMaterial']
    del productData['insoleMaterial']
    del productData['outerMaterial']
    del productData['season']

    if productData['discount'] != 0:
        notifyFavorites(productData['id'], productData['brand'], productData['category'], productData['price'])

    database.updateProduct(int(productData['id']), productData)
    return jsonify({'success': True})

@app.route('/admin/products/add', methods=['GET', 'POST'])
def adminProductAdd():
    loggedIn = session.get('loggedIn', False)
    if not loggedIn:
        abort(404)
    user = getUser({'userId': session.get('userId')})
    if not "admin" in user['tags']:
        abort(404)
    if request.method == 'GET':
        products = getProducts()
        ids = [p['id'] for p in products]
        newId = random.randint(100000, 999999)
        while newId in ids:
            newId = random.randint(100000, 999999)
        product = {
            "id": newId,
            "brand": "",
            "category": "",
            "price": "",
            "prevPrice": "",
            "discount": 0,
            "sizes": [],
            "tags": [],
            "images": [],
            "additionalInformation": {
                "innerMaterial": "",
                "insoleMaterial": "",
                "outerMaterial": "",
                "season": "",
            },
            "maxQuantities": {},
            "sizesCm": {},
            "warehouses": {},
            "addedBy": user['userId']
        }
        database.addProduct(product)
        return render_template('adminProductEdit.html', userData=user, loggedIn=loggedIn, product=product, pageType='add')
    elif request.method == 'POST':
        productData = request.json.get('data')
        productData['sizes'] = [int(size) for size in productData['sizes'].split(',')]
        productData['maxQuantities'] = {quantity.strip().split(" ")[0].strip(): int(quantity.strip().split(" ")[1].replace("(", "").replace(")", "").strip()) for quantity in productData['maxQuantities'].split(',')}
        productData['sizesCm'] = {size.strip().split(" ")[0].strip(): float(size.strip().split(" ")[1].replace("cm", "").replace("(", "").replace(")", "").strip()) for size in productData['sizesCm'].split(',')}
        productData['warehouses'] = {warehouse.strip().split(" ")[0].strip(): warehouse.strip().split(" ")[1].replace("(", "").replace(")", "").strip() for warehouse in productData['warehouses'].split(',')}
        productData['addedBy'] = user['userId']

        productData['additionalInformation'] = {
            "innerMaterial": productData['innerMaterial'],
            "insoleMaterial": productData['insoleMaterial'],
            "outerMaterial": productData['outerMaterial'],
            "season": productData['season'],
        }
        del productData['innerMaterial']
        del productData['insoleMaterial']
        del productData['outerMaterial']
        del productData['season']

        database.addProduct(productData)
        return jsonify({'success': True})
    
@app.route('/admin/product/archive', methods=['POST'])
def adminProductArchive():
    productId = request.json.get('productId')
    product = database.getProduct({'id': int(productId)})
    tags = [t for t in product['tags'] if t != ""]
    if 'archived' in tags:
        tags.remove('archived')
    else:
        tags.append('archived')
    database.updateProduct(int(productId), {'tags': tags})
    return jsonify({'success': True})

@app.route('/admin/orders')
def adminOrders():
    loggedIn = session.get('loggedIn', False)
    if not loggedIn:
        abort(404)
    user = getUser({'userId': session.get('userId')})
    if not "admin" in user['tags']:
        abort(404)
    orders = database.getOrders({})
    statuses = sorted(list(set([o['status'] for o in orders])))
    orders = sorted(orders, key=lambda x: x['timestamp'], reverse=True)

    page_size = 20
    page = request.args.get('page')
    if not page: page = 1
    status = request.args.get('orderStatus')
    if status: orders = [o for o in orders if o['status'] == status]
    orderId = request.args.get('orderId')
    if orderId: orders = [o for o in orders if o['orderId'] == orderId]
    orders = orders[(int(page)-1)*page_size:int(page)*page_size]

    for order in orders:
        cartItems = []
        for item in order['cart']:
            # print(item)
            product = database.getProduct({'id': item['productId']})
            cartItems.append({'id': item['productId'], 'size': item['size'], 'quantity': item['quantity'], 'info': product})
        order['cart'] = cartItems
    return render_template('adminOrders.html', userData=user, loggedIn=loggedIn, orders=orders, statuses=statuses, status=status, orderId=orderId, page=int(page))

@app.route('/admin/orders/<orderId>/<productId>')
def adminOrder(orderId, productId):
    loggedIn = session.get('loggedIn', False)
    if not loggedIn:
        abort(404)
    user = getUser({'userId': session.get('userId')})
    if not "admin" in user['tags']:
        abort(404)
    order = database.getOrder({'orderId': orderId})
    try: order['product'] = [o for o in order['cart'] if int(o['productId']) == int(productId)][0]
    except: return redirect('/admin/orders')
    order['product']['info'] = database.getProduct({'id': int(productId)})
    codesCountry = {v: k for k, v in nova.loadCountryCodes().items()}
    return render_template('adminOrder.html', userData=user, loggedIn=loggedIn, order=order, codesCountry=codesCountry)

@app.route('/admin/order/status', methods=['POST'])
def updateOrderStatus():
    orderId = request.json.get('orderId')
    status = request.json.get('status')
    database.updateOrder(orderId, {'$set': {'status': status.lower()}})
    return jsonify({'success': True})

@app.route('/admin/order/trackingNumber', methods=['POST'])
def updateOrderTrackingNumber():
    orderId = request.json.get('orderId')
    trackingNumber = request.json.get('trackingNumber')
    database.updateOrder(orderId, {'$set': {'trackingNumber': trackingNumber}})
    return jsonify({'success': True})

@app.route('/admin/order/delete', methods=['POST'])
def deleteOrder():
    orderId = request.json.get('orderId')
    productId = request.json.get('productId')

    orderCart = database.getOrder({'orderId': orderId})['cart']
    if len(orderCart) == 1:
        database.removeOrder(orderId)
    else:
        database.updateOrder(orderId, {'$pull': {'cart': {'productId': int(productId)}}})
    return jsonify({'success': True})

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == "__main__":
    # sendEmail('Welcome to Kids Fashion Store', "test@kids.com", body="Welcome to our store!\nThank you for signing up. You can now log in to your new account.\nHappy shopping!", html='welcome')
    app.run(debug=True, port=8080)
    # logResponse = log('home', None)