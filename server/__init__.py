import bcrypt
from flask import Flask, render_template, request, session, redirect, url_for

import utils.mongo as mdb
from server.forms import RegistrationForm, LoginForm

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/login', methods=['POST'])
def login():
    req = {k: v[0] for k, v in request.form.lists()}
    user = mdb.users.find_one({'username': req['username']})
    if user:
        password = req['password'].encode('utf-8')
        hashed_password = user['password']
        check_password = bcrypt.checkpw(password, hashed_password)
        if check_password:
            session['username'] = req['username']
            return redirect(url_for('index'))
    return 'Invalid username/password. Please try again.'


@app.route('/api/register', methods=['GET', 'POST'])
def register():
    req = request.form
    print(req)
    user_schema = RegistrationForm()
    user_schema.load(req)
    req = {k: v[0] for k, v in request.form.lists()}
    print(req)
    exists = mdb.users.find_one({'username': req['username']})
    req['password'] = bcrypt.hashpw(req['password'].encode('utf-8'),
                                    bcrypt.gensalt())
    if request.method == 'POST':
        if not exists:
            mdb.insert_mongo(mdb.users, req)
            session['username'] = req['username']
            return redirect(url_for('index'))
        return 'That username already exists'
    return render_template('register.html')


@app.route('/api/profile')
def profile():
    pass


@app.route('/api/create', methods=['POST'])
def create():
    req = request.form
    username = session['username']
    user = mdb.crawlers.find_one({'username': username})
    print(req)
    post = {
        'username': user['username'],
        'crawler': req['crawler'],
        'starting_url': req['starting_url'],
        'column_names': req['column_names'],
        'xpaths': req['xpaths'],
        'error_xpaths': req.get('error_xpaths'),
        'url_queries': req.get('url_queries'),
        'product_xpath': req.get('product_xpath'),
        'regex': req.get('regex'),
        'page_query': req.get('page_query'),
        'page_steps': req.get('page_steps'),
        'search_xpath': req.get('search_xpath'),
        'search_terms': req.get('search_terms'),
        'concurrent_jobs': req.get('concurrent_jobs')
            }
    mdb.insert_mongo(mdb.crawlers, post)
    return redirect(url_for('index'))


@app.route('/start/<crawler_name>', methods=['GET', 'POST'])
def start(crawler_name):
    username = session['username']
    crawler = mdb.crawlers.find_one(
        {'username': username, 'crawler': crawler_name}
    )

    def venom_container(chunk):
        pass
