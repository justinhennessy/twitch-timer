import redis
import logging

class RedisTimerUtility:
    def __init__(self, redis_host='localhost', redis_port=6379, redis_db=1):
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger('RedisTimerUtility')

    def fetch_valid_uuids(self):
        # Fetch valid UUIDs from your source of truth, assuming this function is properly implemented
        return self.fetch_email_to_uuid().keys()

    def fetch_email_to_uuid(self):
        # Dummy implementation, replace with actual method to fetch from Redis
        return {'3df08934-8bc5-4317-bf19-70780581ec39': {'email': 'me@justinhennessy.com', 'default_time': 300}}

    def cleanup_orphan_timers(self):
        valid_uuids = set(self.fetch_valid_uuids())
        all_uuids = set(key.decode().split(':')[-1] for key in self.redis_client.keys('call_counts:*'))

        orphan_uuids = all_uuids.difference(valid_uuids)
        self.logger.info(f"Valid UUIDs: {valid_uuids}")
        self.logger.info(f"All UUIDs from Redis: {all_uuids}")
        self.logger.info(f"Orphan UUIDs identified: {orphan_uuids}")

        for uuid in orphan_uuids:
            # Deleting the timer and call_counts keys
            self.redis_client.delete(uuid)  # Assuming the timer key is the UUID
            self.redis_client.delete(f"call_counts:{uuid}")
            self.logger.info(f"Deleted timer and call_counts for orphan UUID: {uuid}")

if __name__ == "__main__":
    utility = RedisTimerUtility()
    utility.cleanup_orphan_timers()
