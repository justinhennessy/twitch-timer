from flask import Flask, render_template, jsonify, request
from flask_caching import Cache
import time
import math

app = Flask(__name__, static_url_path='/static')
app.config.from_pyfile('config.py')
app.config['CACHE_TYPE'] = 'simple'

initial_seconds = 5 * 60
max_seconds = 10 * 60
remaining_seconds = initial_seconds
last_updated = time.time()

cache = Cache()
cache.init_app(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/timer', methods=['GET'])
@cache.cached(timeout=10)
def timer():
    global remaining_seconds, last_updated

    current_time = time.time() * 1000  # convert to milliseconds
    elapsed_time = current_time - last_updated
    remaining_seconds -= elapsed_time / 1000  # convert to seconds
    last_updated = current_time

    if remaining_seconds < 0:
        remaining_seconds = 0

    # Round up remaining time to nearest second
    remaining_seconds = math.ceil(remaining_seconds)

    return jsonify({"value": remaining_seconds})

@app.route('/reset-time', methods=['POST'])
def reset_time():
    global remaining_seconds, last_updated

    remaining_seconds = initial_seconds
    last_updated = time.time() * 1000  # convert to milliseconds

    # Round up remaining time to nearest second
    remaining_seconds = math.ceil(remaining_seconds)

    return jsonify({"value": remaining_seconds})

if __name__ == '__main__':
    app.run(debug=False)

