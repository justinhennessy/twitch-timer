import os
import json
import logging
import boto3
from datetime import datetime
from dotenv import load_dotenv
from timer_manager import TimerManager

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bucket_name = os.getenv('BUCKET_NAME')
aws_profile = 'twitch-timer'
base_url = os.getenv('BASE_URL')
email_to_uuid_file_s3_key = 'email_to_uuid.txt'
timers = {}

# Initialize S3 client
session = boto3.Session(profile_name=aws_profile)
s3_client = session.client('s3')

# Track S3 GET and PUT calls
s3_call_counts = {"GET": 0, "PUT": 0, "email_get": 0, "email_put": 0}
timer_call_counts = {}

def track_s3_call(call_type, timer_uuid=None):
    if call_type in s3_call_counts:
        s3_call_counts[call_type] += 1
    if timer_uuid:
        if timer_uuid not in timer_call_counts:
            timer_call_counts[timer_uuid] = {"GET": 0, "PUT": 0}
        if call_type in timer_call_counts[timer_uuid]:
            timer_call_counts[timer_uuid][call_type] += 1

def read_email_to_uuid_from_s3():
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=email_to_uuid_file_s3_key)
        track_s3_call("email_get")
        email_to_uuid = json.loads(response['Body'].read().decode('utf-8'))
    except s3_client.exceptions.NoSuchKey:
        email_to_uuid = {}
    return email_to_uuid

def write_email_to_uuid_to_s3(email_to_uuid):
    s3_client.put_object(Bucket=bucket_name, Key=email_to_uuid_file_s3_key, Body=json.dumps(email_to_uuid, indent=4))
    track_s3_call("email_put")

# Load email to UUID mapping
email_to_uuid = read_email_to_uuid_from_s3()

# Log the structure of email_to_uuid
logging.debug(f"email_to_uuid structure: {email_to_uuid}")

# Initialize timers from email_to_uuid mapping
for email, data in email_to_uuid.items():
    logging.debug(f"Initializing timer for email: {email}, data: {data}")
    timers[data['uuid']] = TimerManager(uuid=data['uuid'])

def update_last_viewed(uuid):
    try:
        email_to_uuid = read_email_to_uuid_from_s3()
        for email, data in email_to_uuid.items():
            if data['uuid'] == uuid:
                data['last_viewed'] = datetime.now().isoformat()
                email_to_uuid[email] = data
                write_email_to_uuid_to_s3(email_to_uuid)
                return
    except Exception as e:
        print(f"Error updating last viewed for timer {uuid}: {e}")

def load_existing_timers():
    email_to_uuid = read_email_to_uuid_mapping()
    for email, data in email_to_uuid.items():
        uuid = data['uuid']
        timers[uuid] = TimerManager(uuid=uuid)
    logger.info("Loaded existing timers into the timers dictionary.")

def read_email_to_uuid_mapping():
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key='email_to_uuid.txt')
        email_to_uuid = json.loads(response['Body'].read().decode('utf-8'))
        return email_to_uuid
    except Exception as e:
        logger.error(f"Error reading email to UUID mapping from S3: {e}")
        return {}
