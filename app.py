from flask import Flask, render_template, jsonify, request
import time

app = Flask(__name__, static_url_path='/static')

initial_seconds = 5 * 60
max_seconds = 10 * 60
remaining_seconds = initial_seconds
last_updated = time.time()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/timer', methods=['GET'])
def timer():
    global remaining_seconds, last_updated

    current_time = time.time()
    elapsed_time = current_time - last_updated
    remaining_seconds -= elapsed_time
    last_updated = current_time

    if remaining_seconds < 0:
        remaining_seconds = 0

    return jsonify({"value": remaining_seconds})

@app.route('/add-time', methods=['POST'])
def add_time():
    global remaining_seconds, last_updated

    remaining_seconds = min(remaining_seconds + 30, max_seconds)
    last_updated = time.time()

    return jsonify({"value": remaining_seconds})

@app.route('/sub-time', methods=['POST'])
def sub_time():
    global remaining_seconds, last_updated

    remaining_seconds = max(remaining_seconds - 30, 0)
    last_updated = time.time()

    return jsonify({"value": remaining_seconds})

@app.route('/reset-time', methods=['POST'])
def reset_time():
    global remaining_seconds, last_updated

    remaining_seconds = initial_seconds
    last_updated = time.time()

    return jsonify({"value": remaining_seconds})

if __name__ == '__main__':
    app.run(debug=True)

