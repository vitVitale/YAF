import logging
from typing import List
import thriftpy2
from thriftpy2.rpc import make_server

example_thrift = thriftpy2.load(path="example.thrift",
                                 module_name="example_thrift")

Operation = example_thrift.Operation
TCheckTokenRq = example_thrift.TCheckTokenRq
CrossPlatformResource = example_thrift.CrossPlatformResource
InvalidOperationException = example_thrift.InvalidOperationException

handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(name)21s :: %(funcName)16s() :: %(message)s')
handler.setFormatter(formatter)


class Dispatcher(object):
    log = logging.getLogger('CrossPlatformService')
    log.setLevel(logging.INFO)
    log.addHandler(handler)

    def ping(self):
        Dispatcher.log.info(f'INCOMING >> Received call...')
        return True

    def get(self, id: int):
        if id == 0:
            ex = InvalidOperationException()
            ex.code = Operation.ERROR
            ex.description = f'Invalid operation with id [{id}]'
            raise ex
        reply = CrossPlatformResource()
        reply.id = id
        reply.name = 'theCall'
        reply.salutation = None
        reply.op = Operation.GOOD
        reply.token_rq = TCheckTokenRq(token='dodvk', operUid='udud-djjjd-e8w7-d87vy')
        Dispatcher.log.info(f'OUTGOING << {reply}')
        return reply

    def save(self, resource: CrossPlatformResource, list_token_rqs: List[TCheckTokenRq]):
        Dispatcher.log.info(f'INCOMING >> {resource}')
        Dispatcher.log.info(f'INCOMING >> {list_token_rqs}')


# server = make_server(example_thrift.CrossPlatformService, Dispatcher(), '127.0.0.1', 6000, client_timeout=60000)
server = make_server(example_thrift.CrossPlatformService, Dispatcher(), '0.0.0.0', 6000, client_timeout=60000)
server.serve()
