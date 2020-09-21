from flask import Flask, render_template, request, jsonify
from Venom import Venom
import json
import os
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder='build')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['VENOM_DB']
db = SQLAlchemy(app)


class Users(db.Model):

    id = db.Column(db.Integer, primary_key=True)
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


db.create_all()


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
