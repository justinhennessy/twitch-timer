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
email_to_uuid_file_s3_key = 'email_to_uuid.txt'
timers = {}

# Initialize S3 client
session = boto3.Session(profile_name=aws_profile)
s3_client = session.client('s3')

def read_email_to_uuid_from_s3():
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=email_to_uuid_file_s3_key)
        email_to_uuid = json.loads(response['Body'].read().decode('utf-8'))
    except s3_client.exceptions.NoSuchKey:
        email_to_uuid = {}
    return email_to_uuid

def write_email_to_uuid_to_s3(email_to_uuid):
    s3_client.put_object(Bucket=bucket_name, Key=email_to_uuid_file_s3_key, Body=json.dumps(email_to_uuid, indent=4))

# Load email to UUID mapping
email_to_uuid = read_email_to_uuid_from_s3()

# Log the structure of email_to_uuid
logging.debug(f"email_to_uuid structure: {email_to_uuid}")

# Initialize timers from email_to_uuid mapping
for email, data in email_to_uuid.items():
    logging.debug(f"Initializing timer for email: {email}, data: {data}")
    timers[data['uuid']] = TimerManager(bucket_name, data['uuid'], aws_profile)

def update_last_viewed(uuid):
    email_to_uuid = read_email_to_uuid_from_s3()
    for email, data in email_to_uuid.items():
        if data['uuid'] == uuid:
            email_to_uuid[email]['last_viewed'] = datetime.now().isoformat()
            break
    write_email_to_uuid_to_s3(email_to_uuid)

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
        update_last_viewed(uuid)
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
    return jsonify({"active_timers": [data['uuid'] for data in email_to_uuid.values()]})

@app.route("/api/register", methods=['POST'])
def register():
    data = request.get_json()
    email = data['email']
    email_to_uuid = read_email_to_uuid_from_s3()
    if email in email_to_uuid:
        user_uuid = email_to_uuid[email]['uuid']
    else:
        user_uuid = str(uuid_lib.uuid4())
        email_to_uuid[email] = {"uuid": user_uuid, "last_viewed": None}
        timers[user_uuid] = TimerManager(bucket_name, user_uuid, aws_profile)
        write_email_to_uuid_to_s3(email_to_uuid)
    return jsonify({"uuid": user_uuid})

@app.route("/api/base_url", methods=['GET'])
def get_base_url():
    return jsonify({"base_url": base_url})

@app.route("/api/timers_status", methods=['GET'])
def timers_status():
    email_to_uuid = read_email_to_uuid_from_s3()
    timer_status = []
    for email, data in email_to_uuid.items():
        uuid = data['uuid']
        response = s3_client.head_object(Bucket=bucket_name, Key=uuid)
        last_modified = response['LastModified']
        is_active = (datetime.now(last_modified.tzinfo) - last_modified) < timedelta(minutes=1)
        timer_status.append({
            "uuid": uuid,
            "email": email,
            "is_active": is_active,
            "last_modified": last_modified.isoformat(),
            "last_viewed": data.get('last_viewed')
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

@app.route('/favicon.ico')
def serve_favicon():
    return send_from_directory('static', 'favicon.ico')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)