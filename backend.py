from flask import Flask, jsonify, request, send_from_directory
import os
import logging
import threading
import time
from flask_cors import CORS  # Import the CORS library
from timer_manager import TimerManager  # Ensure timer_manager.py is in the same directory

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)

timer_manager = TimerManager('timer.txt')
timer_manager.reset_time()

@app.route("/api/timer", methods=['GET'])
def get_timer():
    remaining_time = timer_manager.get_remaining_time()
    app.logger.info(f"Request from IP: {request.remote_addr}, Process: {os.getpid()} - Remaining time: {remaining_time}")
    response = jsonify({"timer": remaining_time})
    return response

@app.route("/api/add", methods=['GET'])
def add_time():
    t_param = request.args.get('t', '30')
    if t_param.lower() == 'infinite':
        timer_manager.set_infinite_time()
        return jsonify({"message": "Timer set to infinite", "timer": -999})
    else:
        seconds = int(t_param)
        timer_manager.add_time(seconds)
        return jsonify({"message": f"Added {seconds} seconds", "timer": timer_manager.get_remaining_time()})

@app.route("/api/reduce", methods=['GET'])
def reduce_time():
    timer_manager.reduce_time()
    return jsonify({"message": "Reduced 30 seconds", "timer": timer_manager.get_remaining_time()})

@app.route("/api/reset", methods=['GET'])
def reset_time():
    timer_manager.reset_time()
    return jsonify({"message": "Timer has been reset", "timer": timer_manager.get_remaining_time()})

@app.route("/api/start", methods=['GET'])
def start_time():
    timer_manager.start_time()
    return jsonify({"message": "Timer started at 5 minutes", "timer": timer_manager.get_remaining_time()})

@app.route('/timer.html')
def serve_timer_html():
    return send_from_directory('static', 'timer.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
