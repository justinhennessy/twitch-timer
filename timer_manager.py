import time

class TimerManager:
    def __init__(self):
        self.start_time = time.time()
        self.default_time = 5 * 60  # 5 minutes in seconds
        self.total_set_time = self.default_time
        self.maximum_time = 10 * 60  # 10 minutes in seconds

    def get_remaining_time(self):
        elapsed_time = time.time() - self.start_time
        remaining_time = self.total_set_time - elapsed_time

        if remaining_time <= 0:
            return "Times up!"
        
        minutes = int(remaining_time // 60)
        seconds = int(remaining_time % 60)
        return f"{minutes}:{seconds:02}"

    def add_time(self):
        self.total_set_time += 30
        if self.total_set_time >= self.maximum_time:
            self.total_set_time = self.maximum_time

    def reduce_time(self):
        elapsed_time = time.time() - self.start_time
        if self.total_set_time - elapsed_time > 0:
            self.total_set_time -= 30

    def reset_time(self):
        self.start_time = time.time()
        self.total_set_time = self.default_time

timer_manager = TimerManager()
