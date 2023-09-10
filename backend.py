from flask import Flask, jsonify, request
import os
from flask_cors import CORS
import logging
import threading
import time
from timer_manager import TimerManager

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app, origins="*")

def countdown_timer():
    while True:
        time.sleep(2)  # Sleep for 2 seconds
        timer_manager.reduce_time(2)  # Reduce the timer by 2 seconds

# Create a TimerManager instance and reset the timer to 5 minutes
timer_manager = TimerManager()
timer_manager.reset_time()

# Start the countdown timer in a separate thread
countdown_thread = threading.Thread(target=countdown_timer)
countdown_thread.daemon = True
countdown_thread.start()

@app.route("/api/timer", methods=['GET'])
def get_timer():
    remaining_time = timer_manager.get_remaining_time()
    app.logger.info(f"Request from IP: {request.remote_addr}, Process: {os.getpid()} - Remaining time: {remaining_time}")
    response = jsonify({"timer": remaining_time})
    return response

@app.route("/api/add", methods=['GET'])
def add_time():
    timer_manager.add_time()
    return jsonify({"message": "Added 30 seconds", "timer": timer_manager.get_remaining_time()})

@app.route("/api/reduce", methods=['GET'])
def reduce_time():
    timer_manager.reduce_time()
    return jsonify({"message": "Reduced 30 seconds", "timer": timer_manager.get_remaining_time()})

@app.route("/api/reset", methods=['GET'])
def reset_time():
    timer_manager.reset_time()
    return jsonify({"message": "Timer reset to 5 minutes", "timer": timer_manager.get_remaining_time()})

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
