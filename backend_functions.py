import os
import json
import logging
import redis
from datetime import datetime
from dotenv import load_dotenv
from timer_manager import TimerManager
import time

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Redis client with retry mechanism
def get_redis_client(max_retries=5, retry_delay=2):
    for attempt in range(max_retries):
        try:
            client = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                db=1
            )
            client.ping()  # Test the connection
            logger.info("Successfully connected to Redis")
            return client
        except redis.ConnectionError as e:
            if attempt < max_retries - 1:
                logger.warning(f"Failed to connect to Redis (attempt {attempt + 1}/{max_retries}). Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error(f"Failed to connect to Redis after {max_retries} attempts: {e}")
                raise

redis_client = get_redis_client()

bucket_name = os.getenv('BUCKET_NAME')
base_url = os.getenv('BASE_URL')
timers = {}

# Track Redis GET and PUT calls
redis_call_counts = {"GET": 0, "PUT": 0, "email_get": 0, "email_put": 0}
timer_call_counts = {}

def track_redis_call(call_type, timer_uuid=None):
    if call_type in redis_call_counts:
        redis_call_counts[call_type] += 1
    if timer_uuid:
        if timer_uuid not in timer_call_counts:
            timer_call_counts[timer_uuid] = {"GET": 0, "PUT": 0}
        if call_type in timer_call_counts[timer_uuid]:
            timer_call_counts[timer_uuid][call_type] += 1

def read_email_to_uuid_from_redis():
    try:
        email_to_uuid = {}
        keys = redis_client.keys('email:*')
        logger.info(f"Keys: {keys}")
        for key in keys:
            email = key.decode().split(':', 1)[1]
            data = redis_client.hgetall(key)
            email_to_uuid[email] = {k.decode(): v.decode() for k, v in data.items()}

            # Convert 'default_time' to int and handle 'last_viewed' conversion
            email_to_uuid[email]['default_time'] = int(email_to_uuid[email]['default_time'])
            last_viewed = email_to_uuid[email].get('last_viewed')
            if last_viewed != 'None':
                email_to_uuid[email]['last_viewed'] = last_viewed
        track_redis_call("email_get")
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
        track_redis_call("email_put")
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

