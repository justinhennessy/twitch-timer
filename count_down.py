import time
import requests
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

bucket_name = 'twitch-timer'
aws_profile = 'twitch-timer'
api_url = 'http://127.0.0.1:5001/api/timers'

session = boto3.Session(profile_name=aws_profile)
s3_client = session.client('s3')

def list_active_timers():
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json().get('active_timers', [])
    except requests.RequestException as e:
        print(f"Error fetching active timers: {e}")
        return []

def read_time(file_key):
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        return float(response['Body'].read().decode('utf-8'))
    except (NoCredentialsError, ClientError):
        return 0.0

def write_time(file_key, time_value):
    try:
        s3_client.put_object(Bucket=bucket_name, Key=file_key, Body=str(time_value))
    except NoCredentialsError as e:
        print(f"Error writing file to S3: {e}")

def countdown_timer():
    while True:
        active_timers = list_active_timers()
        for timer_uuid in active_timers:
            file_key = timer_uuid
            time_value = read_time(file_key)

            if time_value not in [-1, -999]:
                time_value = max(time_value - 1, 0)
                write_time(file_key, time_value)

        time.sleep(1)

if __name__ == "__main__":
    countdown_timer()
