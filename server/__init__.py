from flask import Flask, render_template, request, jsonify
from Venom import Venom
import json
import os
from flask_sqlalchemy import SQLAlchemy
from multiprocessing import Pool

app = Flask(__name__, template_folder='build')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['VENOM_DB']
db = SQLAlchemy(app)


class Users(db.Model):

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(20))

    def __init__(self, user_id, username, email, password):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password = password

    def __repr__(self):
        return f'<ID={self.user_id}, <User={self.username}, <Email={self.email}, <Password={self.password}>'


class Crawlers(db.Model):

    user_id = db.Column(db.ARRAY)
    username = db.Column(db.Integer)
    starting_url = db.Column(db.Integer)
    column_names = db.Column(db.Integer)
    xpaths = db.Column(db.Integer)
    error_xpaths = db.Column(db.String)
    url_queries = db.Column(db.Integer)
    product_xpath = db.Column(db.Integer)
    regex = db.Column(db.Integer)
    splits = db.Column(db.Integer)
    chunks = db.Column(db.Integer)
    page_query = db.Column(db.Integer)
    page_steps = db.Column(db.Integer)
    search_xpath = db.Column(db.Integer)
    search_terms = db.Column(db.Integer)

    def __init__(self, user_id, username, starting_url, column_names, xpaths, error_xpaths, url_queries,
                 product_xpath, regex, splits, chunks, page_query, page_steps, search_xpath, search_terms):
        self.user_id = user_id
        self.username = username
        self.starting_url = starting_url
        self.column_names = column_names
        self.xpaths = xpaths
        self.error_xpaths = error_xpaths
        self.url_queries = url_queries
        self.product_xpath = product_xpath
        self.regex = regex
        self.splits = splits
        self.chunks = chunks
        self.page_query = page_query
        self.page_steps = page_steps
        self.search_xpath = search_xpath
        self.search_terms = search_terms

    def __repr__(self):
        return f'<ID={self.user_id}, <User={self.username}, <Email={self.email}, <Password={self.password}>'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    pass


@app.route('/register')
def register():
    pass


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
