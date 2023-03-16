import sys
import types
import grpc.experimental
from grpc import RpcError
from google.protobuf.json_format import MessageToJson, Parse
from yaf.utils.common_constants import GRPC_DIR, EMPTY


def __filter_protected__(module):
    return {key: value for key, value in module.__dict__.items()
            if not (key.startswith('__')
                    or key.startswith('_')
                    or key.startswith('add_')
                    or key == 'grpc')}


def __register_grpc_dto__(modules):
    initial: dict = __filter_protected__(modules)
    '''  check if it has modules  '''
    while [i for i in list(initial.values()) if isinstance(i, types.ModuleType)]:
        work: dict = initial.copy()
        for k, v in work.items():
            if isinstance(v, types.ModuleType):
                initial.update(__filter_protected__(initial.pop(k)))
    return initial


class GrpcCl:
    def __init__(self, config: dict):
        self.address = f"{config['host']}:{config['port']}"
        self.cls_dict = {}
        for proto_file in config['proto']:
            proto_path_list = proto_file.split('/')
            file_name = proto_path_list.pop()
            dir_name = EMPTY if len(proto_path_list) == 0 else f"/{'/'.join(proto_path_list)}"
            sys.path.append(f"{GRPC_DIR}{dir_name}")
            proto, services = grpc.protos_and_services(protobuf_path=file_name)
            self.cls_dict.update(__filter_protected__(services))
            self.cls_dict.update(__register_grpc_dto__(proto))

    def performer(self, service, rpc, message, args: dict = None):
        for attr in self.cls_dict:
            vars()[attr] = self.cls_dict[attr]
        if args is not None:
            for key in args:
                if isinstance(args[key], list):
                    for i in range(len(args[key])):
                        args[key][i] = eval(args[key][i])
                else:
                    args[key] = eval(args[key])
        msg_obj = eval(message)() if args is None else eval(message)(**args)
        try:
            answer = eval(f"{service}.{rpc}")(msg_obj, self.address, insecure=True)
        except RpcError as ex:
            answer = ex
        return answer

    def json_performer(self, service, rpc, message, json_representation: str = None):
        for attr in self.cls_dict:
            vars()[attr] = self.cls_dict[attr]
        msg_obj = Parse(text=json_representation, message=eval(message)())
        try:
            answer = MessageToJson(
                message=eval(f"{service}.{rpc}")(msg_obj, self.address, insecure=True),
                ensure_ascii=False,
                including_default_value_fields=True)
        except RpcError as ex:
            answer = ex
        return answer
