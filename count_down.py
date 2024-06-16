import time
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

bucket_name = 'twitch-timer'
aws_profile = 'twitch-timer'

session = boto3.Session(profile_name=aws_profile)
s3_client = session.client('s3')

def get_uuid():
    try:
        with open('uuid.txt', 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

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
    file_key = get_uuid()
    if not file_key:
        print("UUID file not found, ensure TimerManager initializes first.")
        return

    while True:
        time_value = read_time(file_key)

        if time_value not in [-1, -999]:
            time_value = max(time_value - 1, 0)
            write_time(file_key, time_value)

        time.sleep(1)

if __name__ == "__main__":
    countdown_timer()
