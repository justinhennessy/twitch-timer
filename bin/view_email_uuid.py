import boto3
import json
import logging
import os
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# AWS profile name
aws_profile = 'twitch-timer'

# Set the AWS profile
session = boto3.Session(profile_name=aws_profile)
s3_client = session.client('s3')

bucket_name = 'twitch-timer'

def read_email_to_uuid_mapping():
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key='email_to_uuid.txt')
        email_to_uuid = json.loads(response['Body'].read().decode('utf-8'))
        return email_to_uuid
    except NoCredentialsError:
        logger.error("No AWS credentials found. Please configure your AWS credentials.")
        return {}
    except PartialCredentialsError:
        logger.error("Incomplete AWS credentials found. Please check your AWS configuration.")
        return {}
    except Exception as e:
        logger.error(f"Error reading email to UUID mapping from S3: {e}")
        return {}

def main():
    email_to_uuid = read_email_to_uuid_mapping()
    if email_to_uuid:
        logger.info("Email to UUID mapping:")
        for email, uuid in email_to_uuid.items():
            print(f"{email}: {uuid}")
    else:
        logger.info("No email to UUID mapping found or an error occurred.")

if __name__ == "__main__":
    main()
