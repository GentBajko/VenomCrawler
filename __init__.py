from quart import Quart, render_template, request, jsonify
from Venom import Venom
import json
import sys

app = Quart(__name__, template_folder='build')


@app.route('/')
async def index():
    return await render_template('index.html')


@app.route('/login')
async def login():
    pass


@app.route('/register')
async def register():
    pass


@app.route('/profile')
async def profile():
    pass


@app.route('/create', methods=['POST'])
async def create():
    response = await request.data
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
    app.run(host='127.0.0.1', port=8000, debug=True)
