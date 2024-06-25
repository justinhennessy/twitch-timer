import redis
import json

# Initialize Redis client
redis_client = redis.Redis(host='localhost', port=6379, db=1)

def dump_email_to_uuid():
    try:
        email_to_uuid = {}
        keys = redis_client.keys('email:*')
        for key in keys:
            email = key.decode().split(':', 1)[1]
            data = redis_client.hgetall(key)
            email_to_uuid[email] = {k.decode(): v.decode() for k, v in data.items()}
            # Convert 'default_time' to int and handle 'last_viewed' conversion
            email_to_uuid[email]['default_time'] = int(email_to_uuid[email]['default_time'])
            last_viewed = email_to_uuid[email].get('last_viewed')
            if last_viewed != 'None':
                email_to_uuid[email]['last_viewed'] = last_viewed

        # Print the JSON pretty-printed output
        print(json.dumps(email_to_uuid, indent=4))
        
    except redis.RedisError as e:
        print(f"Error reading email to UUID mapping from Redis: {e}")

if __name__ == "__main__":
    dump_email_to_uuid()
