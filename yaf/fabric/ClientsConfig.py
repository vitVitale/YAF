import os
import yaml
from time import sleep
from typing import final
from cryptography.fernet import Fernet
from yaf.utils.regex_operations import single_regex_find
from yaf.fabric.clientTypes.RestClient import RestCl
from yaf.fabric.clientTypes.KafkaClient import KafkaCl
from yaf.fabric.clientTypes.SqlDbClient import SqlDbCl
from yaf.fabric.clientTypes.MongoClient import MongoCl
from yaf.fabric.clientTypes.CacheClient import CacheCl
from yaf.fabric.clientTypes.RedisClient import RedisCl
from yaf.fabric.clientTypes.ElasticsearchClient import ElasticCl
from yaf.fabric.clientTypes.WebSocketClient import WSocketCl
from yaf.fabric.clientTypes.GraphQLClient import GraphQLCL
from yaf.fabric.clientTypes.ThriftClient import ThriftCl
from yaf.fabric.clientTypes.GrpcClient import GrpcCl
from yaf.fabric.clientTypes.SshClient import SSHCl
from yaf.utils.common_constants import API_CONTEXT, DECRYPT_KEY, ENCRYPTED_MARK


class ClientStore:

    @classmethod
    def __create_clients__(cls, clients_bus, clients_context, config_set):
        rule: final(dict) = {'kafka':         'KafkaCl',
                             'rest':          'RestCl',
                             'cache':         'CacheCl',
                             'sqldb':         'SqlDbCl',
                             'mongodb':       'MongoCl',
                             'elasticsearch': 'ElasticCl',
                             'redis':         'RedisCl',
                             'websocket':     'WSocketCl',
                             'graphql':       'GraphQLCL',
                             'thrift':        'ThriftCl',
                             'grpc':          'GrpcCl',
                             'ssh_sftp':      'SSHCl'}

        for k in rule:
            if k in clients_context:
                for client in clients_context[k]:
                    if client['name'] in config_set:
                        clients_bus[client['name']] = eval(rule[k])(cls.decrypt_secrets(client))

    @classmethod
    def decrypt_secrets(cls, conf: dict):
        for key, value in conf.items():
            if isinstance(value, str):
                result = single_regex_find(value, ENCRYPTED_MARK)
                if result and DECRYPT_KEY is not None:
                    conf[key] = Fernet(DECRYPT_KEY).decrypt(result[1].encode()).decode(encoding='utf-8')

        return conf.copy()

    def __init__(self, config_set):
        if not os.path.isfile(API_CONTEXT):
            raise Exception("API_CONTEXT file is missing!!\n"
                            "Use README.md to launch correctly.")

        with open(API_CONTEXT, "r", encoding='utf-8') as stream:
            try:
                clients_context = yaml.safe_load(stream)
                self.connect_yml_text = yaml.safe_dump(clients_context)
            except yaml.YAMLError as exc:
                raise Exception(f'Failed to parse file {API_CONTEXT}\n{exc.__cause__}')

        self.clients_bus = {}
        self.__create_clients__(self.clients_bus, clients_context, config_set)
        self.log_listener = clients_context.get('docker', {}) \
            .get('container_log_listener', [])
        sleep(5)  # wait to start and warming connection containers

    def get_client(self, name: str):
        if name in self.clients_bus.keys():
            return self.clients_bus.get(name)
        else:
            raise Exception(f"Client: [ {name} ] not configured!!")

    def finalize(self):
        for client in self.clients_bus.values():
            if isinstance(client, tuple([KafkaCl, WSocketCl])):
                client.shutdown()
