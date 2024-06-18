import logging
from flask import Blueprint, jsonify, request, session
import uuid as uuid_lib
from backend_functions import (bucket_name, base_url, timers, s3_call_counts, timer_call_counts,
                               read_email_to_uuid_from_s3, write_email_to_uuid_to_s3, track_s3_call,
                               update_last_viewed)
from timer_manager import TimerManager
from datetime import datetime, timedelta
from dotenv import load_dotenv
import boto3
import os

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)

# Load environment variables from .env file
load_dotenv()

# Initialize S3 client
aws_profile = 'twitch-timer'
boto_session = boto3.Session(profile_name=aws_profile)
s3_client = boto_session.client('s3')

@api_bp.route("/api/create", methods=['POST'])
def create_timer():
    new_uuid = str(uuid_lib.uuid4())
    timers[new_uuid] = TimerManager(bucket_name, new_uuid, 'twitch-timer')
    logger.info(f"Created new timer with UUID: {new_uuid}")
    return jsonify({"uuid": new_uuid})

@api_bp.route("/api/timer/<uuid>", methods=['GET'])
def get_timer(uuid):
    timer_manager = timers.get(uuid)
    if timer_manager:
        remaining_time = timer_manager.get_remaining_time()
        update_last_viewed(uuid)
        track_s3_call("GET", uuid)
        logger.info(f"Retrieved timer with UUID: {uuid}, Remaining time: {remaining_time}")
        return jsonify({"timer": remaining_time})
    else:
        logger.error(f"Timer with UUID {uuid} not found.")
        return jsonify({"error": "Timer not found"}), 404

@api_bp.route("/api/add/<uuid>", methods=['GET'])
def add_time(uuid):
    timer_manager = timers.get(uuid)
    if timer_manager:
        t_param = request.args.get('t', '30')
        if t_param.lower() == 'infinite':
            timer_manager.set_infinite_time()
            track_s3_call("PUT", uuid)
            logger.info(f"Set timer with UUID {uuid} to infinite")
            return jsonify({"message": "Timer set to infinite", "timer": -999})
        else:
            seconds = int(t_param)
            timer_manager.add_time(seconds)
            track_s3_call("PUT", uuid)
            logger.info(f"Added {seconds} seconds to timer with UUID {uuid}")
            return jsonify({"message": f"Added {seconds} seconds", "timer": timer_manager.get_remaining_time()})
    else:
        logger.error(f"Timer with UUID {uuid} not found.")
        return jsonify({"error": "Timer not found"}), 404

@api_bp.route("/api/reduce/<uuid>", methods=['GET'])
def reduce_time(uuid):
    timer_manager = timers.get(uuid)
    if timer_manager:
        timer_manager.reduce_time()
        track_s3_call("PUT", uuid)
        logger.info(f"Reduced 30 seconds from timer with UUID {uuid}")
        return jsonify({"message": "Reduced 30 seconds", "timer": timer_manager.get_remaining_time()})
    else:
        logger.error(f"Timer with UUID {uuid} not found.")
        return jsonify({"error": "Timer not found"}), 404

@api_bp.route("/api/reset/<uuid>", methods=['GET'])
def reset_time(uuid):
    timer_manager = timers.get(uuid)
    if timer_manager:
        timer_manager.reset_time()
        track_s3_call("PUT", uuid)
        logger.info(f"Reset timer with UUID {uuid}")
        return jsonify({"message": "Timer has been reset", "timer": timer_manager.get_remaining_time()})
    else:
        logger.error(f"Timer with UUID {uuid} not found.")
        return jsonify({"error": "Timer not found"}), 404

@api_bp.route("/api/start/<uuid>", methods=['GET'])
def start_time(uuid):
    timer_manager = timers.get(uuid)
    if timer_manager:
        email_to_uuid = read_email_to_uuid_from_s3()
        for email, data in email_to_uuid.items():
            if data['uuid'] == uuid:
                default_time = data.get('default_time', 300)  # Default to 300 seconds if not found
                timer_manager.default_time = default_time
                timer_manager.start_time()
                track_s3_call("PUT", uuid)
                logger.info(f"Started timer with UUID {uuid}")
                break
        return jsonify({"message": "Timer started", "timer": timer_manager.get_remaining_time()})
    else:
        logger.error(f"Timer with UUID {uuid} not found.")
        return jsonify({"error": "Timer not found"}), 404

@api_bp.route("/api/timers", methods=['GET'])
def list_timers():
    active_timers = [data['uuid'] for data in read_email_to_uuid_from_s3().values()]
    logger.info(f"List of active timers: {active_timers}")
    return jsonify({"active_timers": active_timers})

@api_bp.route("/api/update_config/<uuid>", methods=['POST'])
def update_config(uuid):
    data = request.get_json()
    default_time = data.get('default_time')

    if default_time is None:
        return jsonify({"error": "default_time is required"}), 400

    email_to_uuid = read_email_to_uuid_from_s3()
    for email, details in email_to_uuid.items():
        if details['uuid'] == uuid:
            details['default_time'] = default_time
            write_email_to_uuid_to_s3(email_to_uuid)
            timers[uuid].default_time = default_time
            track_s3_call("PUT", uuid)
            logger.info(f"Updated default time for timer with UUID {uuid} to {default_time} seconds")
            return jsonify({"message": "Configuration updated"}), 200

    return jsonify({"error": "Timer not found"}), 404

@api_bp.route("/api/register", methods=['POST'])
def register():
    data = request.get_json()
    email = data['email']
    email_to_uuid = read_email_to_uuid_from_s3()
    if email in email_to_uuid:
        user_uuid = email_to_uuid[email]['uuid']
        logger.info(f"Email {email} already registered with UUID: {user_uuid}")
    else:
        user_uuid = str(uuid_lib.uuid4())
        email_to_uuid[email] = {
            "uuid": user_uuid,
            "last_viewed": None,
            "default_time": 300  # Default to 300 seconds
        }
        timers[user_uuid] = TimerManager(bucket_name, user_uuid, 'twitch-timer')
        write_email_to_uuid_to_s3(email_to_uuid)
        logger.info(f"Registered new email {email} with UUID: {user_uuid}")
    return jsonify({"uuid": user_uuid})

@api_bp.route("/api/base_url", methods=['GET'])
def get_base_url():
    logger.info("Base URL requested")
    return jsonify({"base_url": base_url})

@api_bp.route("/api/timers_status", methods=['GET'])
def timers_status():
    email_to_uuid = read_email_to_uuid_from_s3()
    timer_status = []
    for email, data in email_to_uuid.items():
        uuid = data['uuid']
        response = s3_client.head_object(Bucket=bucket_name, Key=uuid)
        track_s3_call("GET", uuid)
        last_modified = response['LastModified']
        is_active = (datetime.now(last_modified.tzinfo) - last_modified) < timedelta(minutes=1)
        timer_status.append({
            "uuid": uuid,
            "email": email,
            "is_active": is_active,
            "last_modified": last_modified.isoformat(),
            "last_viewed": data.get('last_viewed'),
            "get_count": timer_call_counts.get(uuid, {}).get("GET", 0),
            "put_count": timer_call_counts.get(uuid, {}).get("PUT", 0)
        })
    logger.info(f"Timer status: {timer_status}")
    return jsonify({"timers": timer_status})

@api_bp.route("/api/s3_call_counts", methods=['GET'])
def get_s3_call_counts():
    logger.info("S3 call counts requested")
    return jsonify({
        "GET": s3_call_counts["GET"],
        "PUT": s3_call_counts["PUT"],
        "email_get": s3_call_counts["email_get"],
        "email_put": s3_call_counts["email_put"]
    })

@api_bp.route("/api/track_s3_call", methods=['POST'])
def api_track_s3_call():
    data = request.get_json()
    call_type = data.get('type')
    timer_uuid = data.get('uuid')
    track_s3_call(call_type, timer_uuid)
    logger.info(f"Tracked S3 call: {call_type} for timer UUID: {timer_uuid}")
    return jsonify({"status": "success"})

@api_bp.route("/api/user_info", methods=['GET'])
def get_user_info():
    email = session.get('email')
    access_token = session.get('access_token')
    logger.info(f"User info requested. Email: {email}, Access Token: {access_token}")
    return jsonify({"email": email, "access_token": access_token})
