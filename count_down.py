import time
import redis
from datetime import datetime, timedelta
import logging
from backend_functions import read_email_to_uuid_from_redis

# Initialize Redis client
redis_client = redis.Redis(host='localhost', port=6379, db=1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('count_down')

def track_redis_call(call_type, timer_uuid):
    # Increment call count in Redis
    redis_client.hincrby(f"call_counts:{timer_uuid}", call_type, 1)

def read_time(uuid):
    try:
        time_value = redis_client.get(uuid)
        track_redis_call("GET", uuid)
        return float(time_value) if time_value else 0.0
    except redis.RedisError as e:
        logger.error(f"Error reading key from Redis for {uuid}: {e}")
        return 0.0

def write_time(uuid, time_value):
    try:
        redis_client.set(uuid, time_value)
        track_redis_call("SET", uuid)
        logger.info(f"Updated timer {uuid}: {time_value}")  # Log for successful write
    except redis.RedisError as e:
        logger.error(f"Error writing key to Redis for {uuid}: {e}")

def countdown_timer():
    while True:
        email_to_uuid = read_email_to_uuid_from_redis()  # Use the imported function

        for email, data in email_to_uuid.items():
            uuid = data['uuid']
            last_viewed = data.get('last_viewed')
            if last_viewed:
                try:
                    last_viewed_datetime = datetime.fromisoformat(last_viewed)
                    if (datetime.now() - last_viewed_datetime) < timedelta(seconds=10):
                        time_value = read_time(uuid)
                        if time_value not in [-1, -999]:
                            new_time_value = max(time_value - 1, 0)
                            write_time(uuid, new_time_value)
                except ValueError as ve:
                    logger.error(f"Error parsing datetime for {uuid}: {ve}")
                except redis.RedisError as e:
                    logger.error(f"Error updating timer {uuid}: {e}")
            else:
                logger.debug(f"Timer {uuid} not active or not viewed recently")

        time.sleep(1)  # Sleep for 1 second

if __name__ == "__main__":
    countdown_timer()
