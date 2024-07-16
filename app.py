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

@app.route('/')
def index():
    return render_template('index.html', index_images=index_images)

if __name__ == "__main__":
    app.run()