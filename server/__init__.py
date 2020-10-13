import bcrypt
from flask import Flask, render_template, request, session, redirect, url_for

import utils.mongo as mdb
from server.forms import RegistrationForm, LoginForm, CrawlerForm
from utils.jobs import Venom
from server.config import Config

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config.from_object(Config)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register')
def register_page():
    return render_template('index.html')


@app.route('/api/register', methods=['GET', 'POST'])
def register():
    req = request.form
    print(req)
    user_schema = RegistrationForm()
    req = user_schema.load(req)
    exists = mdb.users.find_one({'username': req['username']})
    req['password'] = bcrypt.hashpw(req['password'].encode('utf-8'),
                                    bcrypt.gensalt())
    if request.method == 'POST':
        if not exists:
            mdb.insert_mongo(mdb.users, req)
            session['username'] = req['username']
            return {'ok': True, 'redirect': '/'}
        return {'ok': True, 'redirect': '/login'}
    return {'ok': True, 'redirect': '/index'}


@app.route('/login')
def login_page():
    return render_template('index.html')


@app.route('/api/login', methods=['POST'])
def login():
    req = request.form
    login_schema = LoginForm()
    req = login_schema.load(req)
    print(req)
    user = mdb.users.find_one({'username': req['username']})
    if user:
        password = req['password'].encode('utf-8')
        hashed_password = user['password']
        check_password = bcrypt.checkpw(password, hashed_password)
        if check_password:
            session['username'] = req['username']
            print(f"Welcome, {req['username']}")
            return {'ok': True, 'redirect': '/'}
    return {'ok': True, 'redirect': '/login'}


@app.route('/api/profile')
def profile():
    pass


@app.route('/crawler/create')
def create_page():
    return render_template('index.html')


@app.route('/api/crawler/create', methods=['POST'])
def create():
    req = request.form
    crawler_schema = CrawlerForm()
    req = crawler_schema.load(req)
    return redirect(url_for('create_page'))


@app.route('/api/crawler/start/<crawler_name>', methods=['GET', 'POST'])
def start(crawler_name):
    username = session['username']
    crawler = mdb.crawlers.find_one(
        {'username': username, 'crawler': crawler_name}
    )
    return Venom(*crawler)


@app.route('/api/crawler/pause/<crawler_name>', methods=['GET', 'POST'])
def pause(crawler_name):
    pass


@app.route('/api/crawler/resume/<crawler_name>', methods=['GET', 'POST'])
def resume(crawler_name):
    pass
