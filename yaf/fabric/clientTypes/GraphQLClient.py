from json import dumps
from python_graphql_client import GraphqlClient


class GraphQLCL:
    def __init__(self, config: dict):
        def is_ssl(): return config['ssl']['enabled'] == 'true'
        self.client = GraphqlClient(endpoint=config['path'], verify=is_ssl())

    def exchange(self, **kwargs):
        return dumps(self.client.execute(**kwargs),
                     ensure_ascii=False)
