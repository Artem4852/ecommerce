import flask
from flask import request, jsonify, render_template
import os, random

app = flask.Flask(__name__)

index_images = [im for im in os.listdir('static/img/covers') if im.endswith('.jpg')]
random.shuffle(index_images)
columns = 8
rows = 10
index_images = index_images[:columns*rows]
index_images = [index_images[i:i+rows] for i in range(0, len(index_images), rows)]

products = [{
    'title': 'Sneakers',
    'brand': 'Geox',
    'size': '24',
    'price': '1999',
    'img': '../static/img/covers/post_2024-03-06 15h01m26s.jpg',
    'product-number': '123456',
}, {
    'title': 'Sneakers',
    'brand': 'Geox',
    'size': '24',
    'price': '1999',
    'img': '../static/img/covers/post_2024-03-06 15h01m26s.jpg',
    'product-number': '123456',
}, {
    'title': 'Sneakers',
    'brand': 'Geox',
    'size': '24',
    'price': '1999',
    'img': '../static/img/covers/post_2024-03-06 15h01m26s.jpg',
    'product-number': '123456',
}, {
    'title': 'Sneakers',
    'brand': 'Geox',
    'size': '24',
    'price': '1999',
    'img': '../static/img/covers/post_2024-03-06 15h01m26s.jpg',
    'product-number': '123456',
}]

@app.route('/')
def index():
    return render_template('index.html', index_images=index_images, products_featured=products)

if __name__ == "__main__":
    app.run(debug=True)