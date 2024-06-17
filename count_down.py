import time
import os
import json
import boto3
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

bucket_name = os.getenv('BUCKET_NAME')
aws_profile = 'twitch-timer'
session = boto3.Session(profile_name=aws_profile)
s3_client = session.client('s3')

def read_time(file_key):
    response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
    time_value = float(response['Body'].read().decode('utf-8'))
    return time_value

def write_time(file_key, time_value):
    s3_client.put_object(Bucket=bucket_name, Key=file_key, Body=str(time_value))

def read_email_to_uuid_from_s3():
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key='email_to_uuid.txt')
        email_to_uuid = json.loads(response['Body'].read().decode('utf-8'))
    except s3_client.exceptions.NoSuchKey:
        email_to_uuid = {}
    return email_to_uuid

def countdown_timer():
    while True:
        email_to_uuid = read_email_to_uuid_from_s3()

        for email, data in email_to_uuid.items():
            uuid = data['uuid']
            last_viewed = data.get('last_viewed')
            if last_viewed and (datetime.now() - datetime.fromisoformat(last_viewed)) < timedelta(seconds=10):
                try:
                    time_value = read_time(uuid)
                    if time_value not in [-1, -999]:
                        time_value = max(time_value - 1, 0)  # Reduce the timer by 1 second, minimum is 0
                        write_time(uuid, time_value)
                except Exception as e:
                    print(f"Error updating timer {uuid}: {e}")

        time.sleep(1)  # Sleep for 1 second

if __name__ == "__main__":
    countdown_timer()