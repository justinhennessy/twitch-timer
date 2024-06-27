import logging
from flask import Blueprint, jsonify, request, session
import uuid as uuid_lib
from datetime import datetime, timedelta
import redis
import json
import os
from timer_manager import TimerManager
from backend_functions import update_last_viewed, read_email_to_uuid_from_redis, write_email_to_uuid_to_redis, load_existing_timers, timers, track_redis_call, redis_operations

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)

# Initialize Redis client
redis_client = redis.Redis(host='localhost', port=6379, db=1)

base_url = os.getenv('BASE_URL')

@api_bp.route("/api/create", methods=['POST'])
def create_timer():
    new_uuid = str(uuid_lib.uuid4())
    timers[new_uuid] = TimerManager(uuid=new_uuid)
    logger.info(f"Created new timer with UUID: {new_uuid}")
    return jsonify({"uuid": new_uuid})

@api_bp.route("/api/delete/<uuid>", methods=['DELETE'])
def delete_timer(uuid):
    try:
        # Remove from Redis
        redis_client.delete(uuid)
        redis_client.delete(f"call_counts:{uuid}")

        # Remove from the email_to_uuid mapping
        email_to_uuid = read_email_to_uuid_from_redis()
        email_to_uuid = {email: data for email, data in email_to_uuid.items() if data['uuid'] != uuid}
        write_email_to_uuid_to_redis(email_to_uuid)

        # Remove from the timers dictionary
        if uuid in timers:
            del timers[uuid]

        logger.info(f"Deleted timer UUID: {uuid}")
        return jsonify({"status": "success", "message": f"Timer {uuid} deleted successfully"})
    except Exception as e:
        logger.error(f"Error deleting timer {uuid}: {e}")
        return jsonify({"status": "error", "message": f"Failed to delete timer {uuid}"}), 500

@api_bp.route("/api/timer/<uuid>", methods=['GET'])
def get_timer(uuid):
    timer_manager = timers.get(uuid)
    if timer_manager:
        remaining_time = timer_manager.get_remaining_time()
        track_redis_call("GET", uuid, "get_timer")
        update_last_viewed(uuid)
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
            track_redis_call("SET", uuid, "add_time")
            logger.info(f"Set timer with UUID {uuid} to infinite")
            return jsonify({"message": "Timer set to infinite", "timer": -999})
        else:
            seconds = int(t_param)
            timer_manager.add_time(seconds)
            track_redis_call("SET", uuid, "add_time")
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
        track_redis_call("SET", uuid, "reduce_time")
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
        track_redis_call("SET", uuid)
        logger.info(f"Reset timer with UUID {uuid}")
        return jsonify({"message": "Timer has been reset", "timer": timer_manager.get_remaining_time()})
    else:
        logger.error(f"Timer with UUID {uuid} not found.")
        return jsonify({"error": "Timer not found"}), 404

@api_bp.route("/api/start/<uuid>", methods=['GET'])
def start_time(uuid):
    timer_manager = timers.get(uuid)
    if timer_manager:
        email_to_uuid = read_email_to_uuid_from_redis()
        for email, data in email_to_uuid.items():
            if data['uuid'] == uuid:
                default_time = data.get('default_time', 300)
                timer_manager.default_time = default_time
                timer_manager.start_time()
                track_redis_call("SET", uuid, "start_time")
                logger.info(f"Started timer with UUID {uuid}")
                break
        return jsonify({"message": "Timer started", "timer": timer_manager.get_remaining_time()})
    else:
        logger.error(f"Timer with UUID {uuid} not found.")
        return jsonify({"error": "Timer not found"}), 404

@api_bp.route("/api/timers", methods=['GET'])
def list_timers():
    email_to_uuid = read_email_to_uuid_from_redis()
    active_timers = [data['uuid'] for data in email_to_uuid.values()]
    logger.info(f"List of active timers: {active_timers}")
    return jsonify({"active_timers": active_timers})

@api_bp.route("/api/update_config/<uuid>", methods=['POST'])
def update_config(uuid):
    data = request.get_json()
    default_time = data.get('default_time')

    if default_time is None:
        return jsonify({"error": "default_time is required"}), 400

    email_to_uuid = read_email_to_uuid_from_redis()
    for email, details in email_to_uuid.items():
        if details['uuid'] == uuid:
            details['default_time'] = default_time
            write_email_to_uuid_to_redis(email_to_uuid)
            timers[uuid].default_time = default_time
            track_redis_call("SET", uuid, "update_config")
            logger.info(f"Updated default time for timer with UUID {uuid} to {default_time} seconds")
            return jsonify({"message": "Configuration updated"}), 200

    return jsonify({"error": "Timer not found"}), 404

@api_bp.route("/api/register", methods=['POST'])
def register():
    data = request.get_json()
    email = data['email']
    email_to_uuid = read_email_to_uuid_from_redis()
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
        timers[user_uuid] = TimerManager(uuid=user_uuid)
        logger.info(f"Before writing to Redis: {email_to_uuid}")  # Debugging line
        write_email_to_uuid_to_redis(email_to_uuid)  # Ensure this is being called correctly
        logger.info(f"Registered new email {email} with UUID: {user_uuid}")
    return jsonify({"uuid": user_uuid})


@api_bp.route("/api/base_url", methods=['GET'])
def get_base_url():
    logger.info("Base URL requested")
    return jsonify({"base_url": base_url})

@api_bp.route("/api/timers_status", methods=['GET'])
def timers_status():
    email_to_uuid = read_email_to_uuid_from_redis()
    timer_status = []
    for email, data in email_to_uuid.items():
        uuid = data['uuid']
        last_viewed = data.get('last_viewed')
        if last_viewed:
            try:
                last_viewed_datetime = datetime.fromisoformat(last_viewed)
                is_active = (datetime.now() - last_viewed_datetime) < timedelta(minutes=1)
            except ValueError:
                print(f"Invalid ISO format for timer {uuid}: {last_viewed}")
                is_active = False
        else:
            is_active = False

        timer_status.append({
            "uuid": uuid,
            "email": email,
            "is_active": is_active,
            "last_modified": last_viewed,  # Keep original string for debugging
            "last_viewed": last_viewed
        })
    return jsonify({"timers": timer_status})

@api_bp.route("/api/track_redis_call", methods=['POST'])
def api_track_redis_call():
    data = request.get_json()
    call_type = data.get('type')
    timer_uuid = data.get('uuid')
    track_redis_call(call_type, timer_uuid, api_track_redis_call)
    logger.info(f"Tracked Redis call: {call_type} for timer UUID: {timer_uuid}")
    return jsonify({"status": "success"})

@api_bp.route("/api/redis_operations", methods=['GET'])
def get_redis_operations():
    return jsonify(redis_operations)

@api_bp.route("/api/user_info", methods=['GET'])
def get_user_info():
    email = session.get('email')
    access_token = session.get('access_token')
    logger.info(f"User info requested. Email: {email}, Access Token: {access_token}")
    return jsonify({"email": email, "access_token": access_token})

# Register the blueprint
def create_app():
    from flask import Flask
    app = Flask(__name__)
    app.register_blueprint(api_bp)
    load_existing_timers()  # Load existing timers
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
