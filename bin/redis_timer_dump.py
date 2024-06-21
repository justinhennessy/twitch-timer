import redis

class RedisTimerUtility:
    def __init__(self, redis_host='localhost', redis_port=6379, redis_db=1):
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db)

    def list_all_timers(self):
        timers = self.redis_client.keys()
        timer_data = {}

        for timer in timers:
            if timer.startswith(b'call_counts:'):
                continue
            time_value = self.redis_client.get(timer)
            timer_data[timer.decode('utf-8')] = int(time_value)

        return timer_data

    def list_call_counts(self, timer_uuid):
        call_counts = self.redis_client.hgetall(f"call_counts:{timer_uuid}")

        if not call_counts:
            print(f"No call counts found for timer UUID: {timer_uuid}")
            return

        call_counts = {k.decode('utf-8'): int(v) for k, v in call_counts.items()}
        return call_counts

    def list_all_call_counts(self):
        keys = self.redis_client.keys('call_counts:*')
        all_call_counts = {}

        for key in keys:
            timer_uuid = key.decode('utf-8').split(':')[1]
            call_counts = self.redis_client.hgetall(key)
            call_counts = {k.decode('utf-8'): int(v) for k, v in call_counts.items()}
            all_call_counts[timer_uuid] = call_counts

        return all_call_counts

if __name__ == "__main__":
    utility = RedisTimerUtility()

    # List all timers
    timers = utility.list_all_timers()
    print("Timers and their remaining times:")
    for uuid, time in timers.items():
        print(f"UUID: {uuid}, Remaining Time: {time}")

    # List call counts for a specific timer
    timer_uuid = '317bbf49-74a9-4de5-b855-c7efe511db89'  # Replace with the actual UUID
    counts = utility.list_call_counts(timer_uuid)
    if counts:
        print(f"Call counts for timer UUID: {timer_uuid}")
        for call_type, count in counts.items():
            print(f"{call_type}: {count}")

    # List call counts for all timers
    all_counts = utility.list_all_call_counts()
    print("Call counts for all timers:")
    for uuid, counts in all_counts.items():
        print(f"UUID: {uuid}")
        for call_type, count in counts.items():
            print(f"  {call_type}: {count}")
