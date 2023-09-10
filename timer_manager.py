from datetime import datetime, timedelta
import threading

class TimerManager:
    def __init__(self):
        self.start_time = datetime.now()
        self.default_time = timedelta(minutes=5)
        self.total_set_time = self.default_time
        self.maximum_time = timedelta(minutes=10)
        self.lock = threading.Lock()

    def get_remaining_time(self):
        with self.lock:
            elapsed_time = datetime.now() - self.start_time
            remaining_time = self.total_set_time - elapsed_time

            if remaining_time <= timedelta(seconds=0):
                return "Times up!"

            minutes, seconds = divmod(remaining_time.seconds, 60)
            return f"{minutes}:{seconds:02}"

    def add_time(self):
        with self.lock:
            self.total_set_time += timedelta(seconds=30)
            if self.total_set_time >= self.maximum_time:
                self.total_set_time = self.maximum_time

    def reduce_time(self):
        with self.lock:
            elapsed_time = datetime.now() - self.start_time
            if self.total_set_time - elapsed_time > timedelta(seconds=0):
                self.total_set_time -= timedelta(seconds=30)

    def reset_time(self):
        with self.lock:
            self.start_time = datetime.now()
            self.total_set_time = self.default_time

