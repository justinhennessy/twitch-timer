import redis

def fetch_redis_operations():
    client = redis.Redis(host='localhost', port=6379, db=1)
    keys = client.keys('call_counts:*')
    operations = {}

    for key in keys:
        operation_counts = client.hgetall(key)
        for operation, count in operation_counts.items():
            if operation.decode() in operations:
                operations[operation.decode()] += int(count)
            else:
                operations[operation.decode()] = int(count)

    return operations

