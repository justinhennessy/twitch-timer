import threading
import boto3
import uuid
from botocore.exceptions import NoCredentialsError, ClientError

class TimerManager:
    def __init__(self, bucket_name, uuid=None, aws_profile='twitch-timer', default_time=300):
        self.lock = threading.Lock()
        self.bucket_name = bucket_name
        self.session = boto3.Session(profile_name=aws_profile)
        self.s3_client = self.session.client('s3')
        self.file_key = uuid if uuid else str(uuid.uuid4())
        self.default_time = default_time
        self._ensure_file_exists()

    def _track_s3_call(self, call_type):
        from backend_functions import track_s3_call
        track_s3_call(call_type)

    def _ensure_file_exists(self):
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=self.file_key)
        except ClientError:
            self._write_time(0.0)

    def _read_time(self):
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=self.file_key)
            self._track_s3_call("GET")
            return float(response['Body'].read().decode('utf-8'))
        except (NoCredentialsError, ClientError) as e:
            print(f"Error reading file from S3: {e}")
            return 0.0

    def _write_time(self, time_value):
        try:
            self.s3_client.put_object(Bucket=self.bucket_name, Key=self.file_key, Body=str(time_value))
            self._track_s3_call("PUT")
        except NoCredentialsError as e:
            print(f"Error writing file to S3: {e}")

    def get_remaining_time(self):
        with self.lock:
            return int(self._read_time())

    def add_time(self, seconds=30):
        with self.lock:
            time_value = self._read_time()
            if time_value > 0:
                self._write_time(min(time_value + seconds, 10 * 60))

    def reduce_time(self, seconds=30):
        with self.lock:
            time_value = self._read_time()
            self._write_time(max(time_value - seconds, 0))

    def reset_time(self):
        with self.lock:
            self._write_time(-1)

    def set_infinite_time(self):
        with self.lock:
            self._write_time(-999)

    def start_time(self):
        with self.lock:
            self._write_time(self.default_time)