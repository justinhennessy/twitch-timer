from flask import Flask, jsonify, request, send_from_directory
import os
import logging
import uuid
from flask_cors import CORS
from timer_manager import TimerManager

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)

bucket_name = 'twitch-timer'
aws_profile = 'twitch-timer'
timers = {}

@app.route("/api/create", methods=['POST'])
def create_timer():
    new_uuid = str(uuid.uuid4())
    timers[new_uuid] = TimerManager(bucket_name, new_uuid, aws_profile)
    return jsonify({"uuid": new_uuid})

@app.route("/api/timer/<uuid>", methods=['GET'])
def get_timer(uuid):
    timer_manager = timers.get(uuid)
    if timer_manager:
        remaining_time = timer_manager.get_remaining_time()
        app.logger.info(f"Request from IP: {request.remote_addr}, Process: {os.getpid()} - Remaining time: {remaining_time}")
        return jsonify({"timer": remaining_time})
    else:
        app.logger.error(f"Timer with UUID {uuid} not found.")
        return jsonify({"error": "Timer not found"}), 404

@app.route("/api/add/<uuid>", methods=['GET'])
def add_time(uuid):
    timer_manager = timers.get(uuid)
    if timer_manager:
        t_param = request.args.get('t', '30')
        if t_param.lower() == 'infinite':
            timer_manager.set_infinite_time()
            return jsonify({"message": "Timer set to infinite", "timer": -999})
        else:
            seconds = int(t_param)
            timer_manager.add_time(seconds)
            return jsonify({"message": f"Added {seconds} seconds", "timer": timer_manager.get_remaining_time()})
    else:
        return jsonify({"error": "Timer not found"}), 404

@app.route("/api/reduce/<uuid>", methods=['GET'])
def reduce_time(uuid):
    timer_manager = timers.get(uuid)
    if timer_manager:
        timer_manager.reduce_time()
        return jsonify({"message": "Reduced 30 seconds", "timer": timer_manager.get_remaining_time()})
    else:
        return jsonify({"error": "Timer not found"}), 404

@app.route("/api/reset/<uuid>", methods=['GET'])
def reset_time(uuid):
    timer_manager = timers.get(uuid)
    if timer_manager:
        timer_manager.reset_time()
        return jsonify({"message": "Timer has been reset", "timer": timer_manager.get_remaining_time()})
    else:
        return jsonify({"error": "Timer not found"}), 404

@app.route("/api/start/<uuid>", methods=['GET'])
def start_time(uuid):
    timer_manager = timers.get(uuid)
    if timer_manager:
        timer_manager.start_time()
        return jsonify({"message": "Timer started at 5 minutes", "timer": timer_manager.get_remaining_time()})
    else:
        return jsonify({"error": "Timer not found"}), 404

@app.route("/api/timers", methods=['GET'])
def list_timers():
    return jsonify({"active_timers": list(timers.keys())})

@app.route('/timer.html')
def serve_timer_html():
    return send_from_directory('static', 'timer.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
