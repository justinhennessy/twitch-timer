import redis

def dump_redis_data(redis_host='localhost', redis_port=6379, redis_db=1):
    client = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
    keys = client.keys('*')
    data_dump = {}

    for key in keys:
        key_type = client.type(key).decode('utf-8')
        if key_type == 'string':
            value = client.get(key).decode('utf-8')
        elif key_type == 'hash':
            value = {k.decode('utf-8'): v.decode('utf-8') for k, v in client.hgetall(key).items()}
        elif key_type == 'list':
            value = [v.decode('utf-8') for v in client.lrange(key, 0, -1)]
        elif key_type == 'set':
            value = {v.decode('utf-8') for v in client.smembers(key)}
        elif key_type == 'zset':
            value = {v.decode('utf-8'): s for v, s in client.zrange(key, 0, -1, withscores=True)}
        else:
            value = None  # Unknown type or you can add more handlers here

        data_dump[key.decode('utf-8')] = {'type': key_type, 'value': value}

    return data_dump

if __name__ == "__main__":
    redis_data = dump_redis_data()
    for key, info in redis_data.items():
        print(f"Key: {key}, Type: {info['type']}, Value: {info['value']}")

