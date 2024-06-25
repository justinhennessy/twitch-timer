import redis
import sys

class RedisTimerUtility:
    def __init__(self, redis_host='localhost', redis_port=6379, redis_db=1):
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db)

    def list_all_timers(self):
        timers = self.redis_client.keys('*')
        timer_data = {}

        for timer in timers:
            key_type = self.redis_client.type(timer).decode('utf-8')  # Get the type of the key
            if key_type != 'string':  # Proceed only if the key type is string
                continue
            if timer.startswith(b'call_counts:'):
                continue

            time_value = self.redis_client.get(timer)
            try:
                timer_data[timer.decode('utf-8')] = float(time_value)
            except ValueError:
                timer_data[timer.decode('utf-8')] = time_value.decode('utf-8')

        return timer_data

    def list_call_counts(self, timer_uuid):
        call_counts = self.redis_client.hgetall(f"call_counts:{timer_uuid}")

        if not call_counts:
            print(f"No call counts found for timer UUID: {timer_uuid}")
            return {}

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

    def dump_all_info(self):
        all_timers = self.list_all_timers()
        all_call_counts = self.list_all_call_counts()

        print("Timers and their remaining times:")
        for uuid, time in all_timers.items():
            print(f"UUID: {uuid}, Remaining Time: {time}")

        print("\nCall counts for all timers:")
        for uuid, counts in all_call_counts.items():
            print(f"UUID: {uuid}")
            for call_type, count in counts.items():
                print(f"  {call_type}: {count}")

    def delete_timer(self, uuid):
        self.redis_client.delete(uuid)
        self.redis_client.delete(f"call_counts:{uuid}")
        print(f"Deleted timer UUID: {uuid}")

if __name__ == "__main__":
    utility = RedisTimerUtility()

    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'delete' and len(sys.argv) == 3:
            timer_uuid = sys.argv[2]
            utility.delete_timer(timer_uuid)
        else:
            print("Usage: python script.py delete <UUID>")
    else:
        # Dump all Redis info
        utility.dump_all_info()
