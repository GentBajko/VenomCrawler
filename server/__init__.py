from flask import Flask, render_template, request, jsonify
from Venom import Venom
import json
import os
import utils.mongo as mongo
from multiprocessing import Pool

app = Flask(__name__, template_folder='build')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    pass


@app.route('/register')
def register():
    resp = request.data
    response = json.loads(resp.decode('utf8').replace("'", '"'))
    mongo.insert_mongo(mongo.users, response)


@app.route('/profile')
def profile():
    pass


@app.route('/create', methods=['POST'])
def create():
    response = request.data
    print(response)
    response = json.loads(response.decode('utf8').replace("'", '"'))
    # Class Attributes
    starting_url = response['starting_url']
    column_names = response['column_names']
    xpaths = response['xpaths']
    error_xpaths = response.get('error_xpaths')
    url_queries = response.get('url_queries')
    product_xpath = response.get('product_xpath')
    regex = response.get('regex')
    # Calculate URLs
    page_query = response.get('page_query')
    page_steps = response.get('page_steps')
    search_xpath = response.get('search_xpath')
    search_terms = response.get('search_terms')
    # Create File
    website = starting_url[0]
    with open(f"{website}.py", "w") as f:
        f.write(f"from Venom import Venom\n"
                f"{website} = Venom({starting_url[0], error_xpaths, url_queries, product_xpath})")
    print(starting_url, column_names, xpaths)
    return jsonify({'ok': True})


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5050, debug=True)
