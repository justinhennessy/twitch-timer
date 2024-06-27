import os
import json
import logging
import redis
from datetime import datetime
from dotenv import load_dotenv
from timer_manager import TimerManager

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bucket_name = os.getenv('BUCKET_NAME')
base_url = os.getenv('BASE_URL')
redis_client = redis.Redis(host='localhost', port=6379, db=1)
timers = {}

# Track Redis GET and PUT calls
redis_operations = {}
# timer_call_counts = {}

def track_redis_call(call_type, timer_uuid=None, reason=""):
    key = f"{call_type}:{timer_uuid}:{reason}"
    if key in redis_operations:
        redis_operations[key] += 1
    else:
        redis_operations[key] = 1

    # Also update aggregate counts
    aggregate_key = f"{call_type}:{reason}"
    if aggregate_key in redis_operations:
        redis_operations[aggregate_key] += 1
    else:
        redis_operations[aggregate_key] = 1

def read_email_to_uuid_from_redis():
    try:
        email_to_uuid = {}
        keys = redis_client.keys('email:*')
        for key in keys:
            email = key.decode().split(':', 1)[1]
            data = redis_client.hgetall(key)
            email_to_uuid[email] = {k.decode(): v.decode() for k, v in data.items()}
            # Convert 'default_time' to int and handle 'last_viewed' conversion
            email_to_uuid[email]['default_time'] = int(email_to_uuid[email]['default_time'])
            last_viewed = email_to_uuid[email].get('last_viewed')
            if last_viewed != 'None':
                email_to_uuid[email]['last_viewed'] = last_viewed
        track_redis_call("GET", None,"email_get")
        return email_to_uuid
    except redis.RedisError as e:
        logger.error(f"Error reading email to UUID mapping from Redis: {e}")
        return {}

def write_email_to_uuid_to_redis(email_to_uuid):
    try:
        for email, data in email_to_uuid.items():
            redis_key = f"email:{email}"
            # Convert all values to strings for storage in Redis
            data = {k: str(v) for k, v in data.items()}
            redis_client.hmset(redis_key, data)
        track_redis_call("SET", None,"email_set")
        logger.info(f"Written to Redis: {email_to_uuid}")  # Debugging line
    except redis.RedisError as e:
        logger.error(f"Error writing email to UUID mapping to Redis: {e}")

# Load email to UUID mapping
email_to_uuid = read_email_to_uuid_from_redis()

# Log the structure of email_to_uuid
logging.debug(f"email_to_uuid structure: {email_to_uuid}")

# Initialize timers from email_to_uuid mapping
for email, data in email_to_uuid.items():
    logging.debug(f"Initializing timer for email: {email}, data: {data}")
    timers[data['uuid']] = TimerManager(uuid=data['uuid'])

def update_last_viewed(uuid):
    try:
        email_to_uuid = read_email_to_uuid_from_redis()
        for email, data in email_to_uuid.items():
            if data['uuid'] == uuid:
                data['last_viewed'] = datetime.now().isoformat()
                email_to_uuid[email] = data
                write_email_to_uuid_to_redis(email_to_uuid)
                return
    except Exception as e:
        logger.error(f"Error updating last viewed for timer {uuid}: {e}")

def load_existing_timers():
    email_to_uuid = read_email_to_uuid_from_redis()
    for email, data in email_to_uuid.items():
        uuid = data['uuid']
        timers[uuid] = TimerManager(uuid=uuid)
    logger.info("Loaded existing timers into the timers dictionary.")

