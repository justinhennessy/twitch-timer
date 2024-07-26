import threading
import redis
import uuid as uuid_lib
from typing import Optional

class TimerManager:
    def __init__(self, redis_host: str = 'localhost', redis_port: int = 6379, redis_db: int = 1, uuid: Optional[str] = None, default_time: int = 300):
        self.lock = threading.Lock()
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
        self.file_key = uuid if uuid else str(uuid_lib.uuid4())
        self.default_time = default_time
        self._ensure_key_exists()

    def __repr__(self) -> str:
        return f"TimerManager(uuid={self.file_key}, default_time={self.default_time})"

    def _track_redis_call(self, call_type):
        track_redis_call(call_type, self.file_key)

    def _ensure_key_exists(self):
        if not self.redis_client.exists(self.file_key):
            self._write_time(0)

    def _read_time(self) -> float:
        try:
            time_value = self.redis_client.get(self.file_key)
            self._track_redis_call("GET")
            return float(time_value) if time_value else 0.0
        except redis.RedisError as e:
            print(f"Error reading key from Redis: {e}")
            return 0.0

    def _write_time(self, time_value):
        try:
            self.redis_client.set(self.file_key, time_value)
            self._track_redis_call("SET")
        except redis.RedisError as e:
            print(f"Error writing key to Redis: {e}")

    def get_remaining_time(self) -> int:
        with self.lock:
            return int(self._read_time())

    def add_time(self, seconds: int = 30):
        with self.lock:
            time_value = self._read_time()
            if time_value > 0:
                self._write_time(min(time_value + seconds, 10 * 60))

    def reduce_time(self, seconds: int = 30):
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

def track_redis_call(call_type, timer_uuid):
    redis_client = redis.Redis(host='localhost', port=6379, db=1)
    redis_client.hincrby(f"call_counts:{timer_uuid}", call_type, 1)
