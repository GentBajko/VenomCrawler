from flask import Flask, render_template, request, jsonify, sessions
import json
import utils.mongo as mdb
import bcrypt

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    pass


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        resp = request.data
        response = json.loads(resp.decode('utf8').replace("'", '"'))
        exists = [x for x in mdb.search_mongo(mdb.users, username=response['username'])]
        if not exists:
            response['password'] = bcrypt.hashpw(response['password'].encode('utf-8'), bcrypt.gensalt())
            mdb.insert_mongo(mdb.users, response)
            return {'ok': True}
    return {'ok': False}


@app.route('/profile')
def profile():
    pass


@app.route('/create', methods=['POST'])
def create():
    response = request.data
    print(response)
    response = json.loads(response.decode('utf8').replace("'", '"'))
    # TODO: Add username and subscription plan
    post = {
        'starting_url': response['starting_url'],
        'column_names': response['column_names'],
        'xpaths': response['xpaths'],
        'error_xpaths': response.get('error_xpaths'),
        'url_queries': response.get('url_queries'),
        'product_xpath': response.get('product_xpath'),
        'regex': response.get('regex'),
        'page_query': response.get('page_query'),
        'page_steps': response.get('page_steps'),
        'search_xpath': response.get('search_xpath'),
        'search_terms': response.get('search_terms')
            }
    mdb.insert_mongo(mdb.crawlers, post)
    return jsonify({'ok': True})


