from flask import Flask, jsonify, request, send_from_directory
import os
import logging
import uuid as uuid_lib
import json
from flask_cors import CORS
from timer_manager import TimerManager
from datetime import datetime, timedelta
from dotenv import load_dotenv
import boto3

logging.basicConfig(level=logging.DEBUG)

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

bucket_name = os.getenv('BUCKET_NAME')
aws_profile = 'twitch-timer'
base_url = os.getenv('BASE_URL')
timers = {}

# Initialize S3 client
session = boto3.Session(profile_name=aws_profile)
s3_client = session.client('s3')

# Load email to UUID mapping
email_to_uuid_file = 'email_to_uuid.txt'
if os.path.exists(email_to_uuid_file):
    with open(email_to_uuid_file, 'r') as f:
        email_to_uuid = json.load(f)
else:
    email_to_uuid = {}

# Initialize timers from email_to_uuid mapping
for user_uuid in email_to_uuid.values():
    timers[user_uuid] = TimerManager(bucket_name, user_uuid, aws_profile)

@app.route("/api/create", methods=['POST'])
def create_timer():
    new_uuid = str(uuid_lib.uuid4())
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

@app.route("/api/register", methods=['POST'])
def register():
    data = request.get_json()
    email = data['email']
    if email in email_to_uuid:
        user_uuid = email_to_uuid[email]
    else:
        user_uuid = str(uuid_lib.uuid4())
        email_to_uuid[email] = user_uuid
        timers[user_uuid] = TimerManager(bucket_name, user_uuid, aws_profile)
        # Save the updated email to UUID mapping
        with open(email_to_uuid_file, 'w') as f:
            json.dump(email_to_uuid, f)
    return jsonify({"uuid": user_uuid})

@app.route("/api/base_url", methods=['GET'])
def get_base_url():
    return jsonify({"base_url": base_url})

@app.route("/api/timers_status", methods=['GET'])
def timers_status():
    timer_status = []
    for email, uuid in email_to_uuid.items():
        response = s3_client.head_object(Bucket=bucket_name, Key=uuid)
        last_modified = response['LastModified']
        is_active = (datetime.now(last_modified.tzinfo) - last_modified) < timedelta(minutes=1)
        timer_status.append({
            "uuid": uuid,
            "email": email,
            "is_active": is_active,
            "last_modified": last_modified.isoformat()
        })
    return jsonify({"timers": timer_status})

@app.route('/timer.html')
def serve_timer_html():
    return send_from_directory('static', 'timer.html')

@app.route('/register.html')
def serve_register_html():
    return send_from_directory('static', 'register.html')

@app.route('/admin.html')
def serve_admin_html():
    return send_from_directory('static', 'admin.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)