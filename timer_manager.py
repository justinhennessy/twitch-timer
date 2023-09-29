import threading
import time

class TimerManager:
    def __init__(self, file_path):
        self.lock = threading.Lock()
        self.file_path = file_path

    def _read_time(self):
        with open(self.file_path, 'r') as file:
            return float(file.read())

    def _write_time(self, time_value):
        with open(self.file_path, 'w') as file:
            file.write(str(time_value))

    def get_remaining_time(self):
        with self.lock:
            return int(self._read_time())

    def add_time(self, seconds=30):
        with self.lock:
            time_value = self._read_time()
            self._write_time(min(time_value + seconds, 10 * 60))  # Ensure the timer does not exceed 10 minutes

    def reduce_time(self, seconds=30):
        with self.lock:
            time_value = self._read_time()
            self._write_time(max(time_value - seconds, 0))

    def reset_time(self):
        with self.lock:
            self._write_time(-1)  # Setting the counter to -1 as per the new requirement

    def start_time(self):
        with self.lock:
            self._write_time(300)  # Setting the counter to 300 seconds (5 minutes)
