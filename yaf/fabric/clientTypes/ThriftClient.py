import thriftpy2
from json import loads
from importlib import import_module
from yaf.utils.common_constants import THRIFT_DIR


class ThriftCl:
    def __init__(self, config: dict):
        app_name = config['class'].rsplit('.')[0]
        class_name = config['class'].rsplit('.')[-1]
        module_name = '.'.join(config['class'].rsplit('.')[:-1])
        self.create_DTO_at_runtime = config.get('createDTOatRuntime', True)
        if self.create_DTO_at_runtime:
            thrift = thriftpy2.load(path=f"{THRIFT_DIR}/{config['file']}", module_name=f"{app_name}_thrift").__dict__.items()
            self.cls_dict = {key: value for key, value in thrift if not (key.startswith('__') or key.startswith('_'))}
        self.client = getattr(import_module(f'test_model.thrift.{module_name}'), class_name)(host=config['host'],
                                                                                             port=config['port'])

    def performer(self, service, method, args: str = None):
        args_obj = None
        if self.create_DTO_at_runtime:
            for attr in self.cls_dict:
                vars()[attr] = self.cls_dict[attr]
            if args is not None:
                args_obj = loads(args)
                for key in args_obj:
                    if isinstance(args_obj[key], list):
                        for i in range(len(args_obj[key])):
                            args_obj[key][i] = eval(args_obj[key][i])
                    else:
                        args_obj[key] = eval(args_obj[key])
        else:
            args_obj = args
        return self.client.send_request(service=service,
                                        method=method,
                                        args=args_obj)
