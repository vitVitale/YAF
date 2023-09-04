import re
from json import dumps
from time import sleep
from redis import Redis
from redis.cluster import ClusterNode, RedisCluster, RedisClusterException


class RedisCl:
    def __init__(self, config: dict):
        try:
            nodes = [ClusterNode(node['host'], node['port']) for node in config['node']]

            self.client = RedisCluster(startup_nodes=nodes,
                                       password=config['pass'],
                                       decode_responses=True)
            self.client.get_nodes()
        except RedisClusterException as ex:
            print(f'Redis {config["name"]} not a cluster !!')
            self.client = Redis(host=config['node'][0]['host'],
                                port=config['node'][0]['port'],
                                password=config['pass'],
                                decode_responses=True)
        self.client.time()

    def get_keys(self, key_pattern):
        return self.client.keys(pattern=key_pattern)

    def put_to_cache(self, key, value, expired=None):
        expired = int(expired) if expired is not None else None
        assert self.client.set(name=key,
                               value=value,
                               ex=expired), f'Failed to put by key {key} !'

    def get_from_cache(self, key, timeout=5):
        types = self.client.type(key)
        for _ in range(timeout * 2):
            value = self.client.hgetall(key) if 'hash' == types else self.client.get(key)
            if value is not None:
                if type(value) is dict:
                    # поля с вложенными объектами redis возвращаются, как строки,
                    # поэтому нужно их "зачистить" от лишних кавычек и обратных слешей для преобразования в json
                    temp1 = re.sub(r'"{\\', '{', dumps(value, ensure_ascii=False))
                    return re.sub(r'\\"}"', '"}', temp1).replace('\\', '')
                return value
            sleep(0.5)
        raise Exception(f'Failed to get object from Redis by key [{key}] !!')
