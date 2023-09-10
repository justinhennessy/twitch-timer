from datetime import datetime, timedelta
import threading
import redis
import os

class TimerManager:
    def __init__(self, redis_url):
        self.redis = redis.from_url(redis_url)
        self.lock = threading.Lock()

    def get_remaining_time(self):
        with self.lock:
            remaining_time = self.redis.get("timer")

            if remaining_time is None:
                return "Times up!"

            return remaining_time.decode("utf-8")

    def add_time(self):
        with self.lock:
            self.redis.incrby("timer", 30)

    def reduce_time(self):
        with self.lock:
            self.redis.decrby("timer", 30)

    def reset_time(self):
        with self.lock:
            self.redis.set("timer", 5 * 60)

timer_manager = TimerManager(os.environ.get("REDIS_URL"))
