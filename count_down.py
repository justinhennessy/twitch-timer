import time
import json
import redis
import boto3
from datetime import datetime, timedelta

redis_client = redis.Redis(host='localhost', port=6379, db=1)

# Initialize S3 client
aws_profile = 'twitch-timer'
boto_session = boto3.Session(profile_name=aws_profile)
s3_client = boto_session.client('s3')
bucket_name = 'twitch-timer'  # Replace with your actual bucket name

def track_redis_call(call_type, timer_uuid):
    # Increment call count in Redis
    redis_client.hincrby(f"call_counts:{timer_uuid}", call_type, 1)

def read_time(uuid):
    try:
        time_value = redis_client.get(uuid)
        track_redis_call("GET", uuid)
        return float(time_value) if time_value else 0.0
    except redis.RedisError as e:
        print(f"Error reading key from Redis for {uuid}: {e}")
        return 0.0

def write_time(uuid, time_value):
    try:
        redis_client.set(uuid, time_value)
        track_redis_call("SET", uuid)
    except redis.RedisError as e:
        print(f"Error writing key to Redis for {uuid}: {e}")

def read_email_to_uuid_mapping():
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key='email_to_uuid.txt')
        email_to_uuid = json.loads(response['Body'].read().decode('utf-8'))
        return email_to_uuid
    except Exception as e:
        print(f"Error reading email to UUID mapping from S3: {e}")
        return {}

def countdown_timer():
    while True:
        email_to_uuid = read_email_to_uuid_mapping()

        for email, data in email_to_uuid.items():
            uuid = data['uuid']
            last_viewed = data.get('last_viewed')
            if last_viewed and (datetime.now() - datetime.fromisoformat(last_viewed)) < timedelta(seconds=10):
                try:
                    time_value = read_time(uuid)
                    if time_value not in [-1, -999]:
                        new_time_value = max(time_value - 1, 0)
                        write_time(uuid, new_time_value)
                except redis.RedisError as e:
                    print(f"Error updating timer {uuid}: {e}")
            else:
                print(f"Timer {uuid} not active or not viewed recently")

        time.sleep(1)  # Sleep for 1 second

if __name__ == "__main__":
    countdown_timer()
