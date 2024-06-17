import time
import os
import json
import boto3
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests

load_dotenv()

bucket_name = os.getenv('BUCKET_NAME')
aws_profile = 'twitch-timer'
base_url = os.getenv('BASE_URL')

session = boto3.Session(profile_name=aws_profile)
s3_client = session.client('s3')

def track_s3_call(call_type, timer_uuid):
    try:
        response = requests.post(f"{base_url}/api/track_s3_call", json={"type": call_type, "uuid": timer_uuid})
        response.raise_for_status()
        print(f"Tracked {call_type} call for timer {timer_uuid}")
    except requests.exceptions.RequestException as e:
        print(f"Error tracking S3 call: {e}")

def read_time(file_key):
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        track_s3_call("GET", file_key)
        time_value = float(response['Body'].read().decode('utf-8'))
        print(f"Read time {time_value} for timer {file_key}")
        return time_value
    except Exception as e:
        print(f"Error reading time from S3 for {file_key}: {e}")
        return 0.0

def write_time(file_key, time_value):
    try:
        s3_client.put_object(Bucket=bucket_name, Key=file_key, Body=str(time_value))
        track_s3_call("PUT", file_key)
        print(f"Wrote time {time_value} for timer {file_key}")
    except Exception as e:
        print(f"Error writing time to S3 for {file_key}: {e}")

def read_email_to_uuid_mapping():
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key='email_to_uuid.txt')
        track_s3_call("GET", 'email_to_uuid.txt')
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
                        new_time_value = max(time_value - 1, 0)  # Reduce the timer by 1 second, minimum is 0
                        write_time(uuid, new_time_value)
                        print(f"Updated timer {uuid}: {time_value} -> {new_time_value}")
                except Exception as e:
                    print(f"Error updating timer {uuid}: {e}")
            else:
                print(f"Timer {uuid} not active or not viewed recently")
        
        time.sleep(1)  # Sleep for 1 second

if __name__ == "__main__":
    countdown_timer()